#!/usr/bin/env python3
"""Check motion upload folders before (or after) they go into the archive.

Errors (the check fails):
  - folder name isn't "SG ASL <Sign> <Year>-<Month>-<Day> Upload"
  - folder is in the wrong place (Dictionary signs go in "ASL <first letter>")
  - no ReadMe, or a ReadMe that doesn't follow the standard: first line is the
    folder's stamp, and Submitted by, Audited by and Model are filled in
  - no raw take in "FBX Files/Original/"
  - a Blender backup (.blend1), or (for --dir) a file over 100 MB, which GitHub refuses
  - an existing version of the sign has the same or a later date, so this
    one would not replace it

Warnings (reported, but the check still passes):
  - a standard export is missing (Mesh, Mixamo, Unreal, MetaHuman, Rigify,
    animation .blend, pose data, captions video, ShapeKeys.txt)
  - (for --dir) a file over 50 MB, or the ReadMe's Date doesn't match the folder
  - "Redo of:" names a motion that isn't in the archive

Which folders to check:
  --base REV          folders changed between REV and HEAD (what the workflow uses)
  --folder PATH ...   repository folders, e.g. "SG ASL Dictionary/ASL R/SG ASL Robot 2026-11-19 Upload"
  --since DATE        every motion in the repository dated DATE or later
  --dir PATH          upload folders on disk that aren't in the repository yet, e.g.
                      "H:/Galt Workspace/Ready for Upload" (or one upload folder);
                      compared against this repository's existing versions

Examples:
  python tools/check_uploads.py --dir "H:/Galt Workspace/Ready for Upload"
  python tools/check_uploads.py --since 2026-11-01
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import (  # noqa: E402
    COLLECTIONS, FORMAT_COLUMNS, STAMP_RE, TextReader, file_kinds, find_entries,
    iso_date, parse_readme, repo_root,
)

MB = 1024 * 1024
HARD_LIMIT = 100 * MB
SOFT_LIMIT = 50 * MB
EXPECTED = {
    "has_mesh_fbx": "Mesh FBX", "has_mixamo_fbx": "Mixamo FBX", "has_ue_mannequin_fbx": "Unreal Mannequin FBX",
    "has_metahuman_fbx": "MetaHuman FBX", "has_rigify_fbx": "Rigify FBX",
    "has_animation_blend": "Working or Finished .blend/.zip", "has_pose_data": "pose CSV/JSON",
    "has_video": "captions video",
}


class Motion:
    def __init__(self, label: str, folder_name: str, files: dict[str, int | None], read, place: str | None):
        self.label = label              # how the folder is shown in messages
        self.name = folder_name         # "SG ASL Robot 2026-11-19 Upload"
        self.files = files              # path inside the folder -> size in bytes (None in the repo)
        self.read = read                # function(path inside folder) -> text
        self.place = place              # "SG ASL Dictionary/ASL R", or None when on disk
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []


def stamp_parts(folder_name: str):
    m = STAMP_RE.match(folder_name)
    if not m:
        return None
    return m["name"].strip(), iso_date(m["y"], m["m"], m["d"]), bool(m["upload"])


def expected_place(name: str, collection_hint: str | None) -> str:
    if collection_hint == "SG ASL Fingerspelling":
        return "SG ASL Fingerspelling/Letters or Numbers"
    first = name[:1].upper()
    return f"SG ASL Dictionary/ASL {first}"


def existing_versions(all_files: list[str]):
    """(collection, section family, lower name) -> [(date, folder)] for every motion in the repo."""
    entries, _ = find_entries(all_files)
    index = collections.defaultdict(list)
    by_id = {}
    for folder in entries:
        parts = folder.split("/")
        sp = stamp_parts(parts[-1])
        if not sp or len(parts) < 3:
            continue
        name, date, _ = sp
        family = parts[1].removesuffix("-Old")
        index[(parts[0], family, name.lower())].append((date, folder))
        by_id[re.sub(r" Upload$", "", parts[-1]).lower()] = folder
    return index, by_id


def check(m: Motion, versions, by_id) -> None:
    sp = stamp_parts(m.name)
    if not sp:
        m.errors.append(f'folder name should be "SG ASL <Sign> <Year>-<Month>-<Day> Upload", not "{m.name}"')
        return
    name, date, has_upload = sp
    stamp = re.sub(r" Upload$", "", m.name)
    if not has_upload:
        m.errors.append('folder name should end in " Upload"')
    if "  " in m.name:
        m.errors.append("double space in the folder name")

    # Where it lives
    collection = m.place.split("/")[0] if m.place else None
    if m.place:
        parts = m.place.split("/")
        if len(parts) != 2:
            m.errors.append(f"should sit directly in a section folder, not in {m.place}")
        elif collection == "SG ASL Dictionary" and parts[1] != f"ASL {name[:1].upper()}":
            m.errors.append(f'is in "{parts[1]}" but should be in "ASL {name[:1].upper()}"')
        elif collection == "SG ASL Fingerspelling" and parts[1].endswith("-Old"):
            m.warnings.append(f'new uploads go in "{parts[1].removesuffix("-Old")}", not "{parts[1]}"')
    else:
        m.notes.append(f"goes in {expected_place(name, collection)}")

    # ReadMe
    readmes = sorted(p for p in m.files if p.endswith("ReadMe.txt"))
    if not readmes:
        m.errors.append("no ReadMe.txt")
    else:
        if len(readmes) > 1:
            m.warnings.append(f"{len(readmes)} ReadMe files: {', '.join(readmes)}")
        rp = readmes[0]
        if not rp.startswith("Documentation/"):
            m.warnings.append(f"ReadMe should be in Documentation/, found {rp}")
        text = m.read(rp)
        lines = text.splitlines()
        first = lines[0].strip() if lines else ""
        info = parse_readme(text)
        if first != stamp:
            hint = " (written by an older 4) Archive II New)" if first == "Stamp" else ""
            m.errors.append(f'ReadMe first line is "{first}", should be "{stamp}"{hint}')
        if not info["submitted_by"]:
            m.errors.append('ReadMe "Submitted by:" is blank (use "Studio Galt Mocap" for our own recordings)')
        if not info["audited_by"]:
            m.errors.append(f'ReadMe "Audited by:" is blank (use "Unaudited as of <date>" until a third party audits it)')
        labelled_model = any(l.strip().startswith("Model:") and l.strip()[6:].strip() not in ("", ",")
                             for l in lines)
        if not labelled_model:
            if info["rig"]:
                m.errors.append(f'ReadMe Model value isn\'t on its label (should read "Model: {info["rig"]}")')
            else:
                m.errors.append('ReadMe "Model:" is blank')
        if info["recorded"]:
            try:
                y, mo, d = re.split(r"[-/]", info["recorded"].strip())[:3]
                if iso_date(y, mo, d) != date:
                    m.warnings.append(f'ReadMe Date is {info["recorded"]}, folder says {date}')
            except ValueError:
                m.warnings.append(f'ReadMe Date "{info["recorded"]}" isn\'t a date')
        redo = next((l.split(":", 1)[1].strip() for l in lines if l.strip().startswith("Redo of:")), "")
        if redo and redo.lower() not in by_id:
            m.warnings.append(f'"Redo of: {redo}" isn\'t in the archive')

    # Raw take
    if not any(p.startswith("FBX Files/Original/") and p.lower().endswith(".fbx") for p in m.files):
        m.errors.append("no raw take in FBX Files/Original/")

    # Files
    for p, size in sorted(m.files.items()):
        if p.lower().endswith(".blend1"):
            m.errors.append(f"Blender backup file: {p}")
        if size is None:
            continue
        if size > HARD_LIMIT:
            m.errors.append(f"{p} is {size / MB:.0f} MB; GitHub refuses files over 100 MB")
        elif size > SOFT_LIMIT:
            m.warnings.append(f"{p} is {size / MB:.0f} MB (GitHub warns over 50 MB)")
    kinds = file_kinds(m.name, list(m.files))
    missing = [EXPECTED[col] for col, test in FORMAT_COLUMNS
               if col in EXPECTED and not any(test(k) for k in kinds)]
    if not any(p.endswith("ShapeKeys.txt") for p in m.files):
        missing.append("ShapeKeys.txt")
    if missing:
        m.warnings.append("missing: " + ", ".join(missing))

    # Is it the newest version?
    if collection or m.place is None:
        coll_candidates = [collection] if collection else list(COLLECTIONS)
        family = m.place.split("/")[1].removesuffix("-Old") if m.place and "/" in m.place else None
        others = []
        for (c, fam, n), vs in versions.items():
            if c in coll_candidates and n == name.lower() and (family is None or fam == family):
                others += [(d, f) for d, f in vs if f.split("/")[-1] != m.name]
        newer = [f for d, f in others if d >= date]
        older = sorted((d, f) for d, f in others if d < date)
        if newer:
            m.errors.append("won't replace the existing version, which is dated the same or later: "
                            + ", ".join(f.split("/")[-1] for f in sorted(newer)))
        elif older:
            m.notes.append(f"replaces {older[-1][1].split('/')[-1]}")
        else:
            m.notes.append("new sign")


# --- gathering folders -------------------------------------------------------

def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def repo_sizes(root: Path) -> dict[str, None]:
    """Every tracked path at HEAD. Sizes aren't read: in a partial clone that would download
    every file, and GitHub already refuses files over 100 MB."""
    names = git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD").decode("utf-8").split("\0")
    return {p: None for p in names if p}


def owner_folder(path: str) -> str | None:
    parts = path.split("/")
    if parts[0] not in COLLECTIONS:
        return None
    owner = None
    for i in range(2, len(parts) - 1):
        if STAMP_RE.match(parts[i]) or parts[i].endswith(" Upload"):
            owner = i
    return "/".join(parts[: owner + 1]) if owner is not None else None


def repo_motions(root: Path, folders: set[str], sizes: dict[str, int]) -> list[Motion]:
    reader = TextReader(root)
    by_folder = collections.defaultdict(dict)
    for p, s in sizes.items():
        f = owner_folder(p)
        if f in folders:
            by_folder[f][p[len(f) + 1:]] = s
    motions = []
    for f in sorted(folders):
        if f not in by_folder:
            continue  # deleted
        parts = f.split("/")
        motions.append(Motion(f, parts[-1], by_folder[f], lambda rel, f=f: reader.read(f"{f}/{rel}"),
                              "/".join(parts[:-1])))
    return motions


def disk_motions(path: Path) -> list[Motion]:
    if path.name.endswith(" Upload") and path.is_dir():
        dirs = [path]
    else:
        dirs = sorted(d for d in path.rglob("*") if d.is_dir() and d.name.endswith(" Upload"))
    motions = []
    for d in dirs:
        files = {}
        for dirpath, _, names in os.walk(d):
            for n in names:
                p = Path(dirpath, n)
                files[p.relative_to(d).as_posix()] = p.stat().st_size

        def read(rel, d=d):
            raw = (d / rel).read_bytes()
            return raw.decode("utf-16") if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else raw.decode("utf-8", "replace")
        motions.append(Motion(str(d), d.name, files, read, None))
    return motions


# --- reporting ----------------------------------------------------------------

def report(motions: list[Motion]) -> int:
    gh = os.environ.get("GITHUB_ACTIONS") == "true"
    n_err = sum(bool(m.errors) for m in motions)
    for m in motions:
        mark = "FAIL" if m.errors else ("warn" if m.warnings else " ok ")
        extra = f"  ({'; '.join(m.notes)})" if m.notes else ""
        print(f"[{mark}] {m.name}{extra}")
        for e in m.errors:
            print(f"        error: {e}")
            if gh:
                print(f"::error title={m.name}::{e}")
        for w in m.warnings:
            print(f"        warning: {w}")
            if gh:
                print(f"::warning title={m.name}::{w}")
    print(f"\n{len(motions)} folder(s) checked: {n_err} with errors, "
          f"{sum(bool(m.warnings) and not m.errors for m in motions)} with warnings only.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"## Upload check: {len(motions)} folder(s), {n_err} with errors\n\n")
            fh.write("| | Motion | Problems |\n|---|---|---|\n")
            for m in motions:
                icon = "❌" if m.errors else ("⚠️" if m.warnings else "✅")
                probs = "<br>".join([f"**{e}**" for e in m.errors] + m.warnings + [f"_{n}_" for n in m.notes])
                fh.write(f"| {icon} | {m.name} | {probs.replace('|', '/')} |\n")
    return 1 if n_err else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--base", help="check folders changed between this commit and HEAD")
    g.add_argument("--folder", nargs="+", help="repository folders to check")
    g.add_argument("--since", help="check every motion dated on or after this date (YYYY-MM-DD)")
    g.add_argument("--dir", type=Path, help="upload folders on disk, not yet in the repository")
    args = ap.parse_args(argv)

    root = repo_root()
    sizes = repo_sizes(root)
    versions, by_id = existing_versions(list(sizes))

    if args.dir:
        motions = disk_motions(args.dir)
        if not motions:
            print(f'No folders ending in " Upload" found in {args.dir}')
            return 0
    else:
        if args.base:
            changed = git(root, "diff", "--name-only", "--no-renames", "-z", args.base, "HEAD").decode("utf-8")
            folders = {f for p in changed.split("\0") if p and (f := owner_folder(p))}
        elif args.folder:
            folders = {f.strip().rstrip("/").replace("\\", "/") for f in args.folder}
        else:
            entries, _ = find_entries(list(sizes))
            folders = set()
            for f in entries:
                sp = stamp_parts(f.split("/")[-1])
                if sp and sp[1] >= args.since:
                    folders.add(f)
        motions = repo_motions(root, folders, sizes)
        if not motions:
            print("No motion folders to check.")
            return 0
    for m in motions:
        check(m, versions, by_id)
    return report(motions)


if __name__ == "__main__":
    sys.exit(main())
