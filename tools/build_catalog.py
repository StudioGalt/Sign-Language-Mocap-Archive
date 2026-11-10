#!/usr/bin/env python3
"""Build a searchable catalog of every motion in the Sign Language Mocap Archive.

Run from anywhere inside the repository:

    python tools/build_catalog.py

Writes:
    catalog/catalog.csv   one row per motion (open in any spreadsheet)
    catalog/catalog.json  the same data, for scripts and websites
    catalog/issues.csv    entries that look incomplete or misnamed
    catalog/SUMMARY.md    counts and coverage, linked from the main README

Only the Python standard library is needed. The file list comes from git, so
this works in a sparse or partial clone where the large FBX/blend/video files
were never downloaded. Only the small ReadMe.txt and ShapeKeys.txt files are read.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

COLLECTIONS = ("SG ASL Dictionary", "SG ASL Fingerspelling")
RAW_MOCAP = "Raw Mocap"

# "SG ASL Alert (Inform) Alt 1 2023-5-17 Upload" -> name="Alert (Inform) Alt 1", date=2023-5-17
STAMP_RE = re.compile(
    r"^SG ASL (?P<name>.+?)\s+(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})(?P<upload> Upload)?$"
)
# Trailing take/alternate markers, used only to group related motions together.
VARIANT_RE = re.compile(
    r"(?:\s+(?:\((?:alt|alternate)\)|alt|alternate|var|variant|redo|v\d+|\d+))+$", re.I
)
FRAME_RE = re.compile(r"^\s*Frame:\s*(\d+)\s*$")
SHAPEKEY_RE = re.compile(r"^\s*\d+\.\s*(\S+)\s*$")
SHAPEKEY_FRAME_RE = re.compile(r"^\s*Frame:\s*\d+,\s*Value:\s*([-\d.eE]+)\s*$")
BLINK_KEYS = {"EyesCloseL_AU43_L", "EyesCloseR_AU43_R"}

# Friendly column names for the file types people ask for most. Any other file
# type still shows up in the "files" column, so nothing is hidden.
def _is(*names):
    return lambda k: k in names


def _ends(*exts):
    return lambda k: k.lower().endswith(exts)


FORMAT_COLUMNS = [
    ("has_mesh_fbx", _is("Mesh.fbx")),
    ("has_mixamo_fbx", _is("No Mesh Mixamo.fbx", "Mixamo.fbx", "Mixamo TPose.fbx")),
    ("has_ue_mannequin_fbx", _is("No Mesh UE Mannequin.fbx", "Manny TPose.fbx", "Manny APose.fbx",
                                 "Quinn TPose.fbx", "Quinn APose.fbx")),
    ("has_metahuman_fbx", _is("MetaHuman TPose.fbx", "MetaHuman APose.fbx")),
    ("has_rigify_fbx", _is("Rigify TPose.fbx", "Rigify APose.fbx")),
    ("has_research_full_fbx", _is("No Mesh Full.fbx")),
    ("has_research_mini_fbx", _is("No Mesh Mini.fbx")),
    ("has_research_ueplus_fbx", _is("No Mesh UEPlus.fbx")),
    ("has_original_fbx", _is("Original (raw take).fbx")),
    ("has_animation_blend", _is("Finished.zip", "Working.zip", "Working.blend", "Animation.blend",
                                "Finished.blend")),
    ("has_pose_library", _is("Poses.blend", "Mixamo Poses.blend")),
    ("has_pose_data", lambda k: k == "Pose JSON (jpm)" or k.endswith((".json", ".csv"))),
    ("has_video", _ends(".mkv", ".mp4", ".webm")),
    ("has_gif", _ends(".gif")),
]


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except (OSError, subprocess.CalledProcessError):
        return Path(__file__).resolve().parent.parent


def list_files(root: Path) -> list[str]:
    """All tracked paths (forward slashes), falling back to a disk walk."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, check=True,
        ).stdout
        files = [p for p in out.decode("utf-8").split("\0") if p]
        if files:
            return files
    except (OSError, subprocess.CalledProcessError):
        pass
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in filenames:
            files.append(Path(dirpath, f).relative_to(root).as_posix())
    return files


class TextReader:
    """Reads small text files from disk, or from git when not checked out."""

    def __init__(self, root: Path):
        self.root = root
        self._proc = None

    def read(self, path: str) -> str:
        p = self.root / path
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
        return self._from_git(path)

    def _from_git(self, path: str) -> str:
        if self._proc is None:
            try:
                self._proc = subprocess.Popen(
                    ["git", "-C", str(self.root), "cat-file", "--batch"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                )
            except OSError:
                return ""
        self._proc.stdin.write(f"HEAD:{path}\n".encode("utf-8"))
        self._proc.stdin.flush()
        header = self._proc.stdout.readline().decode("utf-8").split()
        if len(header) < 3 or header[1] == "missing":
            return ""
        size = int(header[2])
        data = self._proc.stdout.read(size)
        self._proc.stdout.read(1)  # trailing newline
        return data.decode("utf-8", errors="replace")

    def close(self):
        if self._proc is not None:
            self._proc.stdin.close()
            self._proc.wait()


def parse_readme(text: str) -> dict:
    lines = [l.rstrip() for l in text.splitlines()]
    info = {
        "submitted_by": "", "audited_by": "", "parent_motion": "",
        "blender_version": "", "rig": "", "recorded": "", "original_motion": "",
        "keypose_frames": [], "keypose_notes": [],
    }
    for l in lines:
        for key, label in (("submitted_by", "Submitted by:"), ("audited_by", "Audited by:"),
                           ("parent_motion", "Parent Motion:"), ("blender_version", "Blender Version:")):
            if l.startswith(label) and not info[key]:
                info[key] = l[len(label):].strip()
    # Newer ReadMes list the labels "Model:, Date:, Original Motion:" and then
    # the three values on the following lines.
    for i, l in enumerate(lines):
        if l.strip().startswith("Original Motion:"):
            values = []
            for nxt in lines[i + 1:]:
                if nxt.strip() == "---":
                    break
                if nxt.strip():
                    values.append(nxt.strip())
            if len(values) >= 3:
                info["rig"], info["recorded"], info["original_motion"] = values[:3]
            elif values:
                info["original_motion"] = values[-1]
            break
    for i, l in enumerate(lines):
        m = FRAME_RE.match(l)
        if m and i > 0 and lines[i - 1].strip().lower().startswith("keypose"):
            info["keypose_frames"].append(int(m.group(1)))
            note = lines[i + 1].strip() if i + 1 < len(lines) else ""
            note = note[len("Notes:"):].strip() if note.startswith("Notes:") else ""
            if note and note != "{}":
                info["keypose_notes"].append(note)
    return info


def parse_shapekeys(text: str) -> list[str]:
    """Names of shape keys that actually move (any keyframe value above zero)."""
    animated, current = [], None
    for l in text.splitlines():
        m = SHAPEKEY_RE.match(l)
        if m:
            current = m.group(1)
            continue
        m = SHAPEKEY_FRAME_RE.match(l)
        if m and current and current not in animated:
            try:
                if abs(float(m.group(1))) > 1e-6:
                    animated.append(current)
            except ValueError:
                pass
    return animated


def iso_date(y: str, m: str, d: str) -> str:
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"


def find_entries(files: list[str]):
    """Map each motion folder to the files inside it.

    A motion folder is any folder under a collection whose name is a stamp
    ("SG ASL <name> <date>"), with or without the " Upload" suffix. Files go to
    the deepest such folder, so a motion accidentally nested inside another is
    still found (and reported in issues.csv).
    """
    entries: dict[str, list[str]] = collections.defaultdict(list)
    stray: list[str] = []
    for path in files:
        parts = path.split("/")
        if parts[0] not in COLLECTIONS:
            continue
        owner = None
        for i in range(2, len(parts) - 1):
            if STAMP_RE.match(parts[i]) or parts[i].endswith(" Upload"):
                owner = i
        if owner is None:
            stray.append(path)
            continue
        folder = "/".join(parts[: owner + 1])
        entries[folder].append("/".join(parts[owner + 1:]))
    return entries, stray


def layout_version(rel_files: list[str]) -> str:
    """Which generation of the folder layout an entry uses (see README "Folder layouts")."""
    dirs = {"/".join(f.split("/")[:2]) for f in rel_files if "/" in f}
    if any(d.startswith("FBX Files/Original") for d in dirs) or any(d.startswith("Poses/CSV") for d in dirs):
        return "v5"
    if any(d.startswith(("FBX Files/Full", "FBX Files/Unreal_Engine", "FBX Files/Rigify")) for d in dirs):
        return "v4"
    if any(d.startswith(("FBX Files/Game Ready", "FBX Files/Research")) for d in dirs):
        return "v3"
    if any(d.startswith(("FBX Files", "Documentation")) for d in dirs):
        return "v2"
    return "v1"


def file_kinds(folder_name: str, rel_files: list[str]) -> list[str]:
    stamp = re.sub(r" Upload$", "", folder_name)
    kinds = set()
    for f in rel_files:
        base = f.split("/")[-1]
        if f.startswith("FBX Files/Original/"):
            kinds.add("Original (raw take).fbx")
            continue
        if base.startswith(stamp):
            kind = base[len(stamp):]
        elif base.startswith("jpm_") and base.endswith(".json"):
            kind = " Pose JSON (jpm)"
        else:
            kind = " " + base
        kind = re.sub(r"\bP\d+\b", "P#", kind)
        kinds.add(kind.strip() or base)
    return sorted(kinds)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="catalog", help="output folder, relative to the repo root")
    args = ap.parse_args(argv)

    root = repo_root()
    files = list_files(root)
    entries, stray = find_entries(files)

    raw_index = {}
    for p in files:
        if p.startswith(RAW_MOCAP + "/") and p.lower().endswith(".fbx"):
            raw_index.setdefault(Path(p).stem.strip().lower(), p)

    reader = TextReader(root)
    rows, issues = [], []

    def issue(folder, kind, detail):
        issues.append({"folder": folder, "issue": kind, "detail": detail})

    for folder in sorted(entries):
        rel = entries[folder]
        parts = folder.split("/")
        collection = parts[0].replace("SG ASL ", "")
        section = parts[1]
        folder_name = parts[-1]
        m = STAMP_RE.match(folder_name)
        if m:
            name, date = m.group("name").strip(), iso_date(m["y"], m["m"], m["d"])
            if not m.group("upload"):
                issue(folder, "folder name missing ' Upload'", folder_name)
        else:
            name = re.sub(r"^SG ASL |\s*Upload$", "", folder_name).strip()
            date = ""
            issue(folder, "no date in folder name", folder_name)
        if len(parts) > 3:
            issue(folder, "motion folder nested inside another folder", "/".join(parts[2:-1]))
        if "  " in folder_name:
            issue(folder, "double space in name", folder_name)

        readme_path = next((f for f in rel if f.endswith("ReadMe.txt")), None)
        shapekey_path = next((f for f in rel if f.endswith("ShapeKeys.txt")), None)
        info = parse_readme(reader.read(f"{folder}/{readme_path}")) if readme_path else parse_readme("")
        animated = parse_shapekeys(reader.read(f"{folder}/{shapekey_path}")) if shapekey_path else []
        if not readme_path:
            issue(folder, "no ReadMe.txt", "")

        raw = ""
        if info["original_motion"]:
            raw = raw_index.get(info["original_motion"].strip().lower(), "")
        bundled = next((f for f in rel if f.startswith("FBX Files/Original/")), None)
        if not raw and bundled:
            raw = f"{folder}/{bundled}"

        kinds = file_kinds(folder_name, rel)
        if any(k.endswith(".blend1") for k in kinds):
            issue(folder, "Blender backup (.blend1) committed", "; ".join(k for k in kinds if k.endswith(".blend1")))

        row = {
            "id": re.sub(r" Upload$", "", folder_name),
            "collection": collection,
            "section": section,
            "name": name,
            "group": VARIANT_RE.sub("", name).strip() or name,
            "date": date,
            "status": "",  # filled in below
            "superseded_by": "",
            "folder": folder,
            "layout": layout_version(rel),
            "rig": info["rig"],
            "blender_version": info["blender_version"],
            "original_motion": info["original_motion"],
            "raw_mocap_file": raw,
            "keypose_count": len(info["keypose_frames"]),
            "keypose_frames": " ".join(map(str, info["keypose_frames"])),
            "facial_animation": "yes" if any(k not in BLINK_KEYS for k in animated) else "no",
            "animated_shape_keys": " ".join(animated),
            "submitted_by": info["submitted_by"],
            "audited_by": info["audited_by"],
            "parent_motion": info["parent_motion"],
            "notes": " | ".join(info["keypose_notes"]),
        }
        for col, test in FORMAT_COLUMNS:
            row[col] = "yes" if any(test(k) for k in kinds) else "no"
        row["files"] = "; ".join(kinds)
        rows.append(row)

    reader.close()

    # Some ReadMe templates kept an old "Original Motion" value, so dozens of
    # unrelated signs point at the same raw take. Re-cleaning the same take
    # (same sign, new date) is fine; a value shared across different signs is not.
    groups_per_source = collections.defaultdict(set)
    for r in rows:
        if r["original_motion"]:
            groups_per_source[r["original_motion"]].add(r["group"].lower())
    for r in rows:
        src = r["original_motion"]
        if src and len(groups_per_source[src]) > 1:
            r["raw_mocap_file"] = ""
            issue(r["folder"], "ReadMe 'Original Motion' looks copied from another sign",
                  f"{src} (shared by {len(groups_per_source[src])} different signs)")
        elif src and not r["raw_mocap_file"]:
            issue(r["folder"], "Original Motion not found in Raw Mocap", src)

    # A motion re-recorded under a newer date replaces the older one (README FAQ 12).
    # Fingerspelling "Letters-Old" / "Numbers-Old" pair with "Letters" / "Numbers".
    by_key = collections.defaultdict(list)
    for r in rows:
        family = r["section"].removesuffix("-Old")
        by_key[(r["collection"], family, r["name"].lower())].append(r)
    for same in by_key.values():
        # Newest date wins; on a tie prefer the proper " Upload" folder with more files.
        same.sort(key=lambda r: (r["date"], not r["section"].endswith("-Old"),
                                 r["folder"].endswith(" Upload"), len(r["files"])))
        newest = same[-1]
        for r in same:
            if r is newest and not r["section"].endswith("-Old"):
                r["status"] = "current"
            else:
                r["status"] = "superseded"
                if r is not newest:
                    r["superseded_by"] = newest["folder"]

    for p in stray:
        issues.append({"folder": str(Path(p).parent.as_posix()), "issue": "file outside any motion folder", "detail": p})

    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with open(out / "catalog.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(out / "catalog.json", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(out / "issues.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["folder", "issue", "detail"])
        w.writeheader()
        w.writerows(sorted(issues, key=lambda i: (i["issue"], i["folder"])))
    write_summary(out / "SUMMARY.md", rows, issues)

    print(f"{len(rows)} motions, {sum(r['status'] == 'current' for r in rows)} current, "
          f"{len(issues)} issues -> {out}")
    return 0


def write_summary(path: Path, rows: list[dict], issues: list[dict]):
    current = [r for r in rows if r["status"] == "current"]
    lines = [
        "# Archive summary",
        "",
        "Generated by `tools/build_catalog.py`. Do not edit by hand; re-run the script.",
        "",
        f"- **Motions:** {len(rows)} ({len(current)} current, {len(rows) - len(current)} superseded)",
        f"- **Distinct signs (alternates grouped):** {len({(r['collection'], r['group'].lower()) for r in current})}",
        f"- **With facial animation beyond blinks:** {sum(r['facial_animation'] == 'yes' for r in current)}",
        f"- **Linked to a raw mocap file:** {sum(bool(r['raw_mocap_file']) for r in rows)}",
        f"- **Marked as audited:** {sum(bool(r['audited_by']) for r in rows)}",
        "",
        "## Coverage",
        "",
        "| Collection | Section | Current motions | Newest upload |",
        "|---|---|---:|---|",
    ]
    by_sec = collections.defaultdict(list)
    for r in current:
        by_sec[(r["collection"], r["section"])].append(r)
    for (col, sec), rs in sorted(by_sec.items()):
        newest = max((r["date"] for r in rs if r["date"]), default="")
        lines.append(f"| {col} | {sec} | {len(rs)} | {newest} |")
    present = {r["section"] for r in rows if r["collection"] == "Dictionary"}
    missing = [f"ASL {c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if f"ASL {c}" not in present]
    if missing:
        lines += ["", "Dictionary letters with no motions yet: " + ", ".join(m.split()[-1] for m in missing)]
    lines += ["", "## Folder layouts", "",
              "Described in the main README under *Folder layouts*.", "",
              "| Layout | Motions | First | Last |", "|---|---:|---|---|"]
    by_layout = collections.defaultdict(list)
    for r in rows:
        by_layout[r["layout"]].append(r["date"])
    for lay, all_ds in sorted(by_layout.items()):
        ds = [d for d in all_ds if d]
        lines.append(f"| {lay} | {len(all_ds)} | {min(ds, default='')} | {max(ds, default='')} |")
    lines += ["", "## Uploads per year", "", "| Year | Motions |", "|---|---:|"]
    for y, c in sorted(collections.Counter(r["date"][:4] for r in rows if r["date"]).items()):
        lines.append(f"| {y} | {c} |")
    lines += ["", "## Open issues", "", "See [issues.csv](issues.csv) for the full list.", "",
              "| Issue | Count |", "|---|---:|"]
    for k, c in collections.Counter(i["issue"] for i in issues).most_common():
        lines.append(f"| {k} | {c} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
