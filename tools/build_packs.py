#!/usr/bin/env python3
"""Build download packs: every current sign for one piece of software, zipped.

    python tools/build_packs.py --tag 2026-11-11                  # all packs into packs/
    python tools/build_packs.py --tag 2026-11-11 --only rigify    # one pack
    python tools/build_packs.py --tag 2026-11-11 --plan           # list what would go in, no downloads
    python tools/build_packs.py --tag 2026-11-11 --upload         # also attach each zip to that GitHub release

Each pack holds one folder per section (ASL A, ASL B, ..., Fingerspelling) of
FBX files, a README.txt and an index.csv listing every sign in it. A pack
larger than --max-gb is split into parts named by the letters they cover.

The FBX files are fetched from GitHub in batches, each into a temporary
partial clone that is deleted after use, so only a batch or two ever sits on
disk. Uploading needs the GitHub CLI (gh) and a token allowed to edit releases.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalog as bc  # noqa: E402

DEFAULT_REPO = "StudioGalt/Sign-Language-Mocap-Archive"

# For each pack: the files wanted per sign, as groups tried in order. The first
# group with at least one file present is used, so older signs fall back to the
# formats they were made in.
PACKS = {
    "unreal": {
        "title": "Unreal Engine",
        "about": "UE5 Manny and Quinn skeletons, A-pose and T-pose. Older signs, made before these "
                 "exports existed, use the UE Mannequin skeleton instead.",
        "groups": [["Manny APose.fbx", "Manny TPose.fbx", "Quinn APose.fbx", "Quinn TPose.fbx"],
                   ["No Mesh UE Mannequin.fbx"]],
    },
    "metahuman": {
        "title": "MetaHuman",
        "about": "Unreal Engine MetaHuman skeleton, A-pose and T-pose. Only signs made since 2026 have these.",
        "groups": [["MetaHuman APose.fbx", "MetaHuman TPose.fbx"]],
    },
    "mixamo": {
        "title": "Mixamo and Unity",
        "about": "Mixamo-compatible skeleton (mixamorig bone names), which also retargets to Unity Humanoid.",
        "groups": [["Mixamo TPose.fbx"], ["No Mesh Mixamo.fbx"]],
    },
    "rigify": {
        "title": "Blender Rigify",
        "about": "Blender Rigify skeleton, A-pose and T-pose. Signs made before 2025 don't have these; "
                 "use the Blender (Galtis) pack for those.",
        "groups": [["Rigify APose.fbx", "Rigify TPose.fbx"]],
    },
    "blender": {
        "title": "Blender (Galtis)",
        "about": "The full Galtis skeleton with every bone, no mesh. Import onto the Galtis rig "
                 "(Rigs folder on GitHub, also attached to this release) to see the avatar. "
                 "Also suits research and custom retargeting. The newest signs (2026) come as the "
                 "Mesh FBX instead, which includes the avatar.",
        "groups": [["No Mesh Full.fbx"], ["Mesh.fbx"]],
    },
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)


def plan(root: Path, only: list[str] | None):
    """{pack: [(row, [repo paths])]} for current motions, in catalog order."""
    files = bc.list_files(root)
    entries, _ = bc.find_entries(files)
    rows = list(csv.DictReader(open(root / "catalog" / "catalog.csv", encoding="utf-8")))
    rows = [r for r in rows if r["status"] == "current"]
    rows.sort(key=lambda r: (r["collection"] != "Dictionary", r["section"], r["name"].lower(), r["date"]))
    out = {}
    for key, spec in PACKS.items():
        if only and key not in only:
            continue
        chosen = []
        for r in rows:
            rel = entries.get(r["folder"], [])
            for group in spec["groups"]:
                hits = [f"{r['folder']}/{f}" for f in rel
                        if any(f.split("/")[-1] == f"{r['id']} {suffix}" for suffix in group)]
                if hits:
                    # A few folders hold the same file twice (in two subfolders); keep one of each name,
                    # preferring the copy inside "FBX Files".
                    by_name = {}
                    for h in sorted(hits, key=lambda h: ("/FBX Files/" not in h, h)):
                        by_name.setdefault(h.split("/")[-1], h)
                    chosen.append((r, sorted(by_name.values())))
                    break
        out[key] = chosen
    return out


def sparse_pattern(path: str) -> str:
    for ch in "\\*?[]!#":
        path = path.replace(ch, "\\" + ch)
    return "/" + path


class Fetcher:
    """Fetch a batch of repo files into a throwaway partial clone."""

    def __init__(self, repo_url: str, ref: str, workdir: Path):
        self.repo_url, self.ref, self.workdir = repo_url, ref, workdir

    def fetch(self, paths: list[str]) -> Path:
        dest = Path(tempfile.mkdtemp(prefix="batch-", dir=self.workdir))
        run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1",
             "--branch", self.ref, self.repo_url, str(dest)])
        run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"])
        (dest / ".git" / "info" / "sparse-checkout").write_text(
            "\n".join(sparse_pattern(p) for p in paths) + "\n", encoding="utf-8")
        run(["git", "-C", str(dest), "checkout", "-q", self.ref])
        return dest


def letter(name: str) -> str:
    c = name.strip()[:1].upper()
    return c if c.isalpha() else "#"


def readme_text(key, tag, count, first, last, part_no, repo, gallery):
    spec = PACKS[key]
    part = f", part {part_no}" if part_no else ""
    return f"""Sign Language Mocap Archive - {spec['title']} pack
Release {tag}{part}: {count} signs, {first} to {last}

{spec['about']}

Files are named "SG ASL <sign> <date> <format>.fbx" and sorted into one folder
per section (ASL A, ASL B, ..., Fingerspelling). index.csv lists every sign in
this zip, with the folder it comes from on GitHub. Large packs are split into
parts by letter; the release page lists them all.

Only the current version of each sign is included. Every motion, every format,
the videos and the raw takes are on GitHub:
  {gallery}
  https://github.com/{repo}

All files are CC0: use them however you like, no credit required.
Signs are made by a hearing signer and are not a substitute for a Deaf-led
translation. If a sign looks wrong, please report it with the
"Sign correction" form on GitHub.
"""


def build_pack(key, items, tag, outdir: Path, fetcher: Fetcher, max_bytes: int, batch_files: int,
               repo: str, gallery: str) -> list[Path]:
    """Write the pack's zip part(s) into outdir. Returns their paths."""
    spec = PACKS[key]
    prefix = f"SLMA {tag} {spec['title']}"
    done = []                                  # (path, first, last)
    state = {"z": None, "path": None, "rows": []}

    def open_part():
        state["path"] = outdir / f"_building_{key}_{len(done) + 1}.zip"
        state["z"] = zipfile.ZipFile(state["path"], "w", zipfile.ZIP_DEFLATED, compresslevel=6)
        state["rows"] = []

    def close_part():
        z, rows = state["z"], state["rows"]
        first, last = letter(rows[0][1]), letter(rows[-1][1])
        idx = io.StringIO()
        w = csv.writer(idx, lineterminator="\n")
        w.writerow(["id", "name", "group", "date", "section", "file", "github_folder"])
        w.writerows(rows)
        z.writestr(f"{prefix}/index.csv", idx.getvalue())
        z.writestr(f"{prefix}/README.txt",
                   readme_text(key, tag, len({r[0] for r in rows}), first, last, len(done) + 1, repo, gallery))
        z.close()
        done.append((state["path"], first, last, len({r[0] for r in rows}), len(rows)))
        state["z"] = None

    for start in range(0, len(items), batch_files):
        batch = items[start:start + batch_files]
        clone = fetcher.fetch([p for _, paths in batch for p in paths])
        try:
            for row, paths in batch:
                if state["z"] is None:
                    open_part()
                section = "Fingerspelling" if row["collection"] == "Fingerspelling" else row["section"]
                for p in paths:
                    name = p.split("/")[-1]
                    state["z"].write(clone / p, f"{prefix}/{section}/{name}")
                    state["rows"].append([row["id"], row["name"], row["group"], row["date"], section,
                                          f"{section}/{name}", row["folder"]])
                if state["path"].stat().st_size >= max_bytes:
                    close_part()
        finally:
            shutil.rmtree(clone, ignore_errors=True)
    if state["z"] is not None:
        close_part()

    final = []
    for i, (path, first, last, signs, nfiles) in enumerate(done, 1):
        name = f"SLMA-{tag}-{key}.zip" if len(done) == 1 else f"SLMA-{tag}-{key}-part{i}-{first}-{last}.zip"
        target = outdir / name
        path.replace(target)
        final.append(target)
        print(f"  {name}: {signs} signs, {nfiles} files, {target.stat().st_size / 1e9:.2f} GB")
    return final


def upload(tag: str, repo: str, path: Path):
    run(["gh", "release", "upload", tag, str(path), "--clobber", "--repo", repo])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="release tag the packs are for")
    ap.add_argument("--ref", default="main", help="branch to take the files from")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--only", nargs="*", choices=list(PACKS), help="build only these packs")
    ap.add_argument("--out", default="packs")
    ap.add_argument("--max-gb", type=float, default=1.9, help="start a new part above this size (GitHub allows 2 GB)")
    ap.add_argument("--batch", type=int, default=600, help="files fetched per temporary clone")
    ap.add_argument("--plan", action="store_true", help="only list what each pack would hold")
    ap.add_argument("--upload", action="store_true", help="attach each zip to the release, then delete it locally")
    ap.add_argument("--rig", default="", help="also attach this rig file from the repo, e.g. \"Rigs/Galtis 8 20260401.blend\"")
    args = ap.parse_args(argv)

    root = bc.repo_root()
    packs = plan(root, args.only)
    for key, items in packs.items():
        print(f"{PACKS[key]['title']}: {len(items)} signs, {sum(len(p) for _, p in items)} files")
    if args.plan:
        return 0

    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    gallery = f"https://{args.repo.split('/')[0].lower()}.github.io/{args.repo.split('/')[1]}/"
    fetcher = Fetcher(f"https://github.com/{args.repo}.git", args.ref, out)
    index_rows = []
    for key, items in packs.items():
        print(f"Building {PACKS[key]['title']} ...")
        for path in build_pack(key, items, args.tag, out, fetcher, int(args.max_gb * 1e9), args.batch,
                               args.repo, gallery):
            with zipfile.ZipFile(path) as z:
                rows = list(csv.reader(io.StringIO(z.read(next(n for n in z.namelist()
                                                                if n.endswith("/index.csv"))).decode())))[1:]
            index_rows += [[key, path.name, r[0], r[5]] for r in rows]
            if args.upload:
                upload(args.tag, args.repo, path)
                path.unlink()

    suffix = "" if not args.only else "-" + "-".join(args.only)
    idx = out / f"SLMA-{args.tag}-pack-index{suffix}.csv"
    with open(idx, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["pack", "zip", "id", "file_in_zip"])
        w.writerows(index_rows)
    if args.upload:
        upload(args.tag, args.repo, idx)
    if args.upload and args.rig:
        clone = fetcher.fetch([args.rig])
        try:
            upload(args.tag, args.repo, clone / args.rig)
        finally:
            shutil.rmtree(clone, ignore_errors=True)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
