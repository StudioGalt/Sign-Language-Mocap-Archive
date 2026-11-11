#!/usr/bin/env python3
"""Build the browsable gallery (GitHub Pages) from the catalog.

    python tools/build_site.py            # writes _site/
    python -m http.server -d _site 8000   # preview at http://localhost:8000

Copies site/index.html and writes _site/data.json: one compact record per
motion, with its preview video and every downloadable file grouped by the
software it is meant for. Files are served straight from the repository via
raw.githubusercontent.com, so nothing large is copied into the site.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

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


def group_for(rel: str) -> str:
    for name, rx in GROUPS:
        if rx.search(rel):
            return name
    return "Other files"


def short(rel: str, stamp: str) -> str:
    """Store paths relative to the motion folder, with the stamp shortened to '~'."""
    return rel.replace(stamp, "~")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="_site")
    ap.add_argument("--repo", default="StudioGalt/Sign-Language-Mocap-Archive")
    ap.add_argument("--branch", default="main")
    args = ap.parse_args(argv)

    root = bc.repo_root()
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

    motions.sort(key=lambda m: (m["c"] != "D", m["n"].lower(), m["d"]))
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    data = {"repo": args.repo, "branch": args.branch, "motions": motions}
    (out / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copy(root / "site" / "index.html", out / "index.html")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(motions)} motions -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
