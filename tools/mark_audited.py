#!/usr/bin/env python3
"""Record that motions have been checked, in each motion's ReadMe.

Writes "Audited by: <who> <date>" into the ReadMe's "Audited by:" line (or adds
the line if the ReadMe has none). The catalog's `audited` column, the summary
and the gallery read that line, so after you commit and push, the motions show
as audited everywhere.

Name the motions any way that's handy, mixed freely:
    folder path   SG ASL Dictionary/ASL R/SG ASL Robot 2026-11-19 Upload
    catalog id    SG ASL Robot 2026-11-19
    gallery link  https://studiogalt.github.io/Sign-Language-Mocap-Archive/sign/robot-2026-11-19/
    gallery slug  robot-2026-11-19

Examples (run from the repository root):
    python tools/mark_audited.py --by "Studio Galt" "SG ASL Robot 2026-11-19"
    python tools/mark_audited.py --by "Jane Doe" --list checked.txt --dry-run
    python tools/mark_audited.py --unaudit "SG ASL Robot 2026-11-19"

--list reads one motion per line; blank lines and lines starting with # are skipped.
In a sparse checkout, the motion folders must be checked out
(git sparse-checkout add "<folder>"). Nothing is committed for you.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

LABEL = "Audited by:"


def slugify(text: str) -> str:
    # Same rule as tools/build_site.py, so gallery links resolve.
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"^SG ASL ", "", text).lower()).strip("-") or "sign"


def load_catalog(root: Path) -> list[dict]:
    path = root / "catalog" / "catalog.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def resolve(name: str, root: Path, catalog: list[dict]) -> Path | None:
    name = name.strip().strip('"').rstrip("/")
    m = re.search(r"/sign/([^/?#]+)", name)
    if m:
        name = m.group(1)
    direct = root / name
    if direct.is_dir():
        return direct
    folder_name = name.split("/")[-1]
    hits = [r["folder"] for r in catalog
            if r["id"] == name or r["folder"].split("/")[-1] == folder_name or slugify(r["id"]) == name]
    hits = sorted(set(hits))
    if len(hits) > 1:
        sys.exit(f"'{name}' matches more than one motion: {', '.join(hits)}. Use the folder path.")
    return root / hits[0] if hits else None


def find_readme(folder: Path) -> Path | None:
    found = sorted(folder.glob("*ReadMe.txt")) + sorted(folder.glob("Documentation/*ReadMe.txt"))
    return found[0] if found else None


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            text = raw.decode(enc)
            if enc == "utf-16" and not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                continue
            return text, enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def set_audited(path: Path, value: str, dry_run: bool) -> str:
    text, enc = read_text(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    new_line = f"{LABEL} {value}".rstrip()
    idx = next((i for i, l in enumerate(lines) if l.strip().startswith(LABEL)), None)
    if idx is not None:
        old = lines[idx].strip()
        if old == new_line:
            return "unchanged"
        lines[idx] = new_line
        change = f"{old!r} -> {new_line!r}"
    else:
        after = next((i for i, l in enumerate(lines) if l.strip().startswith("Submitted by:")), 0)
        lines.insert(after + 1, new_line)
        change = f"added {new_line!r}"
    if not dry_run:
        out = newline.join(lines) + (newline if text.endswith(("\n", "\r")) else "")
        path.write_bytes(out.encode("utf-8" if enc == "utf-8-sig" else enc))
    return change


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("motions", nargs="*", help="folder paths, catalog ids, gallery links or slugs")
    ap.add_argument("--list", type=Path, help="text file with one motion per line")
    ap.add_argument("--by", help="who checked them (a name or handle)")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="audit date, default today")
    ap.add_argument("--unaudit", action="store_true", help='set "Unaudited as of <date>" instead')
    ap.add_argument("--dry-run", action="store_true", help="show what would change without writing")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="repository root (default: here)")
    args = ap.parse_args()

    names = list(args.motions)
    if args.list:
        names += [l.strip() for l in args.list.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.lstrip().startswith("#")]
    if not names:
        ap.error("name at least one motion, or use --list")
    if not args.unaudit and not args.by:
        ap.error("--by is required (who checked the motions)")
    value = f"Unaudited as of {args.date}" if args.unaudit else f"{args.by.strip()} {args.date}"

    root = args.root.resolve()
    catalog = load_catalog(root)
    problems = 0
    for name in names:
        folder = resolve(name, root, catalog)
        if folder is None:
            print(f"  ?  {name}: not found in the catalog or on disk")
            problems += 1
            continue
        if not folder.is_dir():
            print(f"  ?  {name}: not checked out here; run  git sparse-checkout add \"{folder.relative_to(root).as_posix()}\"")
            problems += 1
            continue
        readme = find_readme(folder)
        if readme is None:
            print(f"  ?  {folder.name}: no ReadMe.txt")
            problems += 1
            continue
        print(f"  {'~' if args.dry_run else 'ok'} {folder.name}: {set_audited(readme, value, args.dry_run)}")
    print(("Dry run: nothing written. " if args.dry_run else "")
          + (f"{problems} could not be marked." if problems else "Done. Commit and push to update the catalog."))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
