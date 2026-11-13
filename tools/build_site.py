#!/usr/bin/env python3
"""Build the browsable gallery (GitHub Pages) from the catalog.

    python tools/build_thumbs.py          # optional: still images for the grid
    python tools/build_site.py            # writes _site/
    python -m http.server -d _site 8000   # preview at http://localhost:8000

Writes to _site/:
    index.html          the gallery (from site/index.html)
    data.json           one compact record per motion
    sign/<slug>/        a small page per motion, so a link to one sign shows
                        its picture and name when shared, and search engines
                        can index it
    thumbs/             still images made by build_thumbs.py, if present
    sitemap.xml, robots.txt, social.png

With --release (latest, or a tag), each sign also lists the release's download
pack zips that hold it, read from the release's pack index. This needs the
GitHub CLI (gh); without it, or before the packs are built, the packs are left out.

Videos and FBX files are linked straight from the repository via
raw.githubusercontent.com, so nothing large is copied into the site.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalog as bc  # noqa: E402

# Order matters: the first matching rule decides a file's group.
GROUPS = [
    ("Unreal Engine", re.compile(r"(UE Mannequin|UEPlus|Manny|Quinn|MetaHuman)", re.I)),
    ("Mixamo and Unity", re.compile(r"Mixamo", re.I)),
    ("Blender Rigify", re.compile(r"Rigify|metarig", re.I)),
    ("Raw take", re.compile(r"^FBX Files/Original/|Original \(raw take\)", re.I)),
    ("Blender and Galtis", re.compile(r"(^|[ /])Mesh\.fbx$|\.blend$|Working\.zip$|Finished\.zip$|Animation\.zip$", re.I)),
    ("Research", re.compile(r"No Mesh (Full|Mini)\.fbx$", re.I)),
    ("Key poses", re.compile(r"\.json$|\.csv$|Poses", re.I)),
    ("Video and notes", re.compile(r"\.(mp4|mkv|webm|gif|txt)$", re.I)),
]

PREVIEW_ORDER = [r" CC\.mp4$", r"Captions\.webm$", r"\.mp4$", r"\.webm$"]
SOFTWARE = {"blender": "Blender", "unreal": "Unreal Engine", "mixamo": "Mixamo and Unity", "rigify": "Rigify"}
DEFAULT_REPO = "StudioGalt/Sign-Language-Mocap-Archive"
PACK_NAMES = {"blender": "Blender (Galtis)", "unreal": "Unreal Engine", "metahuman": "MetaHuman",
              "mixamo": "Mixamo and Unity", "rigify": "Blender Rigify"}


def release_packs(repo: str, release: str) -> dict | None:
    """The release's pack zips and which signs each holds, from its pack index.

    Returns {"tag", "url", "zips": {zip name: [pack, size]}, "by_id": {sign id: [zip, ...]}},
    or None when the release, its pack index or the GitHub CLI isn't available.
    """
    def gh(*args, binary=False):
        r = subprocess.run(["gh", "api", *args], capture_output=True, check=True)
        return r.stdout if binary else json.loads(r.stdout)

    path = "releases/latest" if release == "latest" else f"releases/tags/{release}"
    try:
        rel = gh(f"repos/{repo}/{path}")
        idx = next((a for a in rel["assets"] if a["name"].endswith("-pack-index.csv")), None)
        if idx is None:
            print(f"Release {rel['tag_name']} has no pack index yet; packs left out of the gallery.")
            return None
        text = gh("-H", "Accept: application/octet-stream", f"repos/{repo}/releases/assets/{idx['id']}",
                  binary=True).decode("utf-8")
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Could not read release {release} ({e}); packs left out of the gallery.")
        return None
    sizes = {a["name"]: a["size"] for a in rel["assets"]}
    zips, by_id = {}, {}
    for row in csv.DictReader(io.StringIO(text)):
        zips.setdefault(row["zip"], [row["pack"], sizes.get(row["zip"], 0)])
        ids = by_id.setdefault(row["id"], [])
        if row["zip"] not in ids:
            ids.append(row["zip"])
    tag = rel["tag_name"]
    print(f"Release {tag}: {len(zips)} pack zips holding {len(by_id)} signs")
    return {"tag": tag, "url": f"https://github.com/{repo}/releases/download/{quote(tag)}/",
            "zips": zips, "by_id": by_id}


def pack_order(packs: dict, names: list[str]) -> list[str]:
    order = list(PACK_NAMES)
    return sorted(names, key=lambda z: (order.index(packs["zips"][z][0]) if packs["zips"][z][0] in order else 99, z))


def size_text(n: int) -> str:
    return f"{n / 1e9:.1f} GB" if n >= 1e9 else f"{max(1, round(n / 1e6))} MB"


def group_for(rel: str) -> str:
    for name, rx in GROUPS:
        if rx.search(rel):
            return name
    return "Other files"


def short(rel: str, stamp: str) -> str:
    """Store paths relative to the motion folder, with the stamp shortened to '~'."""
    return rel.replace(stamp, "~")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"^SG ASL ", "", text).lower()).strip("-") or "sign"


def default_base_url(repo: str) -> str:
    owner, name = repo.split("/", 1)
    return f"https://{owner.lower()}.github.io/{name}/"


def preview_source(m: dict) -> str:
    """Repo path of the file a thumbnail is made from (video, else GIF)."""
    rel = m["p"] or m["gif"]
    return f"{m['f']}/{rel.replace('~', m['i'])}" if rel else ""


def collect_motions(root: Path) -> list[dict]:
    files = bc.list_files(root)
    entries, _ = bc.find_entries(files)

    # Fresh catalog in a temp folder, so the site never lags behind a push.
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        rel_tmp = Path(tmp).relative_to(root).as_posix()
        bc.main(["--out", rel_tmp])
        rows = json.loads((Path(tmp) / "catalog.json").read_text(encoding="utf-8"))

    motions = []
    for r in rows:
        stamp = r["id"]
        rel_files = sorted(entries.get(r["folder"], []))
        groups: dict[str, list[str]] = {}
        for rel in rel_files:
            if rel.lower().endswith((".blend1", ".blend2")):
                continue
            groups.setdefault(group_for(rel), []).append(short(rel, stamp))
        preview = ""
        for pattern in PREVIEW_ORDER:
            hit = next((f for f in rel_files if re.search(pattern, f, re.I)), None)
            if hit:
                preview = short(hit, stamp)
                break
        gif = next((short(f, stamp) for f in rel_files if f.lower().endswith(".gif")), "")
        if not preview and not gif:
            # Last resort: Chrome and Edge play these; other browsers show "no preview".
            preview = next((short(f, stamp) for f in rel_files if f.lower().endswith(".mkv")), "")
        tags = []
        if r["has_mesh_fbx"] == "yes" or r["has_animation_blend"] == "yes":
            tags.append("blender")
        if r["has_ue_mannequin_fbx"] == "yes" or r["has_metahuman_fbx"] == "yes":
            tags.append("unreal")
        if r["has_mixamo_fbx"] == "yes":
            tags.append("mixamo")
        if r["has_rigify_fbx"] == "yes":
            tags.append("rigify")
        rec = {
            "i": stamp,
            "n": r["name"],
            "g": r["group"],
            "d": r["date"],
            "c": "F" if r["collection"] == "Fingerspelling" else "D",
            "s": r["section"],
            "f": r["folder"],
            "t": tags,
            "p": preview,
            "gif": gif,
            "files": groups,
        }
        if r["status"] != "current":
            rec["old"] = r["superseded_by"] or 1
        for key, col in (("rig", "rig"), ("bv", "blender_version"), ("raw", "raw_mocap_file"),
                         ("kp", "keypose_count"), ("sk", "animated_shape_keys")):
            if r.get(col) not in ("", None, 0, "0"):
                rec[key] = r[col]
        motions.append(rec)

    # Stable, unique link names: assigned in id order so they never shuffle.
    used: set[str] = set()
    for m in sorted(motions, key=lambda m: m["i"]):
        base = slugify(m["i"])
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        m["u"] = slug

    motions.sort(key=lambda m: (m["c"] != "D", m["n"].lower(), m["d"]))
    return motions


SIGN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sign Language Mocap Archive">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
{og_image}<meta name="twitter:card" content="summary">
<style>
  body {{ margin: 0; background: #EEF1F4; color: #14213D; font: 400 1rem/1.5 "Schibsted Grotesk", system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 880px; margin: 0 auto; padding: 24px clamp(16px, 4vw, 40px) 56px; }}
  a {{ color: #14213D; text-underline-offset: 0.18em; }}
  :focus-visible {{ outline: 3px solid #F2B807; outline-offset: 2px; }}
  .back {{ font-size: 0.95rem; }}
  h1 {{ margin: 22px 0 4px; font-size: clamp(2.4rem, 7vw, 4rem); font-weight: 900; line-height: 1; letter-spacing: -0.035em; }}
  .facts {{ color: #5B6B82; margin: 8px 0 20px; }}
  video, img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: contain; background: #4A4A4C; border-radius: 6px; }}
  .notice {{ margin: 16px 0 0; padding: 10px 12px; border-left: 4px solid #F2B807; background: #FFF8E1; }}
  .actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 22px 0; }}
  .actions a {{ padding: 10px 16px; border-radius: 4px; border: 1px solid #14213D; background: #fff; font-weight: 700; text-decoration: none; }}
  .actions .primary {{ background: #14213D; color: #fff; }}
  p {{ max-width: 64ch; }}
  h2 {{ margin: 32px 0 6px; font-size: 1.15rem; }}
  .packs {{ margin: 0; padding: 0; list-style: none; border-top: 1px solid #C9D2DC; max-width: 64ch; }}
  .packs li {{ padding: 8px 0; border-bottom: 1px solid #C9D2DC; }}
  .packs span {{ color: #5B6B82; }}
</style>
</head>
<body>
<main>
  <a class="back" href="../../">All signs</a>
  <h1>{name}</h1>
  <p class="facts">{facts}</p>
  {media}
  {notice}
  <div class="actions">
    <a class="primary" href="../../#sign={hash}">Open in the gallery</a>
    <a href="{zip}">Download all files (zip)</a>
    <a href="{folder}">Open on GitHub</a>
  </div>
  <p>{desc}</p>
  {packs}
</main>
</body>
</html>
"""


def packs_block(m: dict, packs: dict | None) -> str:
    if not packs or not m.get("pk"):
        return ""
    items = "".join(
        f'<li><a href="{html.escape(packs["url"] + quote(z))}">{html.escape(PACK_NAMES.get(packs["zips"][z][0], packs["zips"][z][0]))}</a>'
        f' <span>{html.escape(z)}, {size_text(packs["zips"][z][1])}</span></li>'
        for z in m["pk"])
    return ("<h2>In the download packs</h2>\n  <p>Each pack holds every current sign for one program, "
            f"from release {html.escape(packs['tag'])}. This sign is in:</p>\n  <ul class=\"packs\">{items}</ul>")


def write_sign_pages(out: Path, motions: list[dict], repo: str, branch: str, base_url: str,
                     packs: dict | None = None) -> list[str]:
    by_folder = {m["f"]: m for m in motions}
    raw_base = f"https://raw.githubusercontent.com/{repo}/{branch}/"
    urls = []
    for m in motions:
        url = f"{base_url}sign/{m['u']}/"
        urls.append(url)
        software = [SOFTWARE[t] for t in m["t"] if t in SOFTWARE]
        kind = "fingerspelling" if m["c"] == "F" else "sign"
        desc = (f"The ASL {kind} “{m['n']}” as motion capture"
                + (f": FBX for {', '.join(software[:-1]) + ' and ' + software[-1] if len(software) > 1 else software[0]}" if software else "")
                + ", with video and key poses. Free to use for anything under CC0.")
        facts = ", ".join(x for x in [f"Recorded {m['d']}" if m["d"] else "", m.get("rig", "")] if x)
        thumb = f"{base_url}thumbs/{m['u']}.jpg" if m.get("th") else ""
        src = preview_source(m)
        if src and not src.lower().endswith(".gif"):
            poster = f' poster="../../thumbs/{m["u"]}.jpg"' if thumb else ""
            media = (f'<video src="{html.escape(raw_base + quote(src))}" controls muted loop playsinline autoplay '
                     f'crossorigin="anonymous"{poster} aria-label="{html.escape(m["n"])}, signed"></video>')
        elif src:
            media = f'<img src="{html.escape(raw_base + quote(src))}" alt="{html.escape(m["n"])}, signed">'
        else:
            media = ""
        notice = ""
        if m.get("old"):
            newer = by_folder.get(m["old"]) if isinstance(m["old"], str) else None
            notice = ('<p class="notice">This is an older version. '
                      + (f'<a href="../{newer["u"]}/">Use the {newer["d"]} version instead.</a>' if newer else "A newer recording replaces it.")
                      + "</p>")
        folder_url = f"https://github.com/{repo}/tree/{branch}/{quote(m['f'])}"
        page = SIGN_PAGE.format(
            title=html.escape(f"{m['n']} in ASL | Sign Language Mocap Archive"),
            og_title=html.escape(f"{m['n']} in ASL"),
            desc=html.escape(desc),
            url=html.escape(url),
            og_image=(f'<meta property="og:image" content="{html.escape(thumb)}">\n'
                      '<meta property="og:image:width" content="400">\n<meta property="og:image:height" content="500">\n'
                      if thumb else ""),
            name=html.escape(m["n"]),
            facts=html.escape(facts),
            media=media,
            notice=notice,
            hash=quote(m["i"]),
            zip=html.escape(f"https://downgit.github.io/#/home?url={quote(folder_url, safe='')}"),
            folder=html.escape(folder_url),
            packs=packs_block(m, packs),
        )
        d = out / "sign" / m["u"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
    return urls


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="_site")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--branch", default="main")
    ap.add_argument("--base-url", default="", help="public address of the site (default: GitHub Pages address)")
    ap.add_argument("--thumbs", default=".thumbs", help="folder of thumbnails made by build_thumbs.py")
    ap.add_argument("--release", default="", help="list download packs from this release: latest, or a tag")
    args = ap.parse_args(argv)
    base_url = (args.base_url or default_base_url(args.repo)).rstrip("/") + "/"

    root = bc.repo_root()
    motions = collect_motions(root)
    out = root / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    thumbs = root / args.thumbs
    if thumbs.is_dir():
        (out / "thumbs").mkdir()
        for m in motions:
            src = thumbs / f"{m['u']}.jpg"
            if src.is_file():
                shutil.copy(src, out / "thumbs" / src.name)
                m["th"] = 1

    packs = release_packs(args.repo, args.release) if args.release else None
    if packs:
        for m in motions:
            if m["i"] in packs["by_id"]:
                m["pk"] = pack_order(packs, packs["by_id"][m["i"]])

    data = {"repo": args.repo, "branch": args.branch, "base": base_url, "motions": motions}
    if packs:
        used = {z for m in motions for z in m.get("pk", [])}
        data["packs"] = {"tag": packs["tag"], "url": packs["url"],
                         "zips": {z: v for z, v in packs["zips"].items() if z in used}}
    (out / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    page = (root / "site" / "index.html").read_text(encoding="utf-8").replace("{{BASE_URL}}", base_url)
    (out / "index.html").write_text(page, encoding="utf-8")
    if (root / "site" / "social.png").is_file():
        shutil.copy(root / "site" / "social.png", out / "social.png")
    (out / ".nojekyll").write_text("", encoding="utf-8")

    urls = write_sign_pages(out, motions, args.repo, args.branch, base_url, packs)
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
               f"  <url><loc>{html.escape(base_url)}</loc></url>"]
    sitemap += [f"  <url><loc>{html.escape(u)}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (out / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url}sitemap.xml\n", encoding="utf-8")

    print(f"{len(motions)} motions, {sum(1 for m in motions if m.get('th'))} thumbnails -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
