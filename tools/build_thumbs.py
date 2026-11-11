#!/usr/bin/env python3
"""Make a still image of each sign for the gallery grid and for link previews.

    python tools/build_thumbs.py            # writes .thumbs/<slug>.jpg

For each motion it takes the preview video (or GIF), grabs a frame from the
middle of the sign, crops it to a 4:5 portrait around the signer and saves a
400x500 JPEG of roughly 20 KB. Existing images are kept, so after the first
run only new motions are processed.

In a sparse or partial clone (like the GitHub Action), the preview videos
are fetched from GitHub in one batch first. Needs ffmpeg.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalog as bc  # noqa: E402
import build_site as bs  # noqa: E402

CROP = "crop='min(iw,ih*4/5)':'min(ih,iw*5/4)',scale=400:500:flags=lanczos"


def sparse_pattern(path: str) -> str:
    """Exact-path pattern for a non-cone sparse checkout."""
    for ch in "\\*?[]!#":
        path = path.replace(ch, "\\" + ch)
    return "/" + path


def fetch_missing(root: Path, paths: list[str]) -> None:
    missing = [p for p in paths if not (root / p).is_file()]
    if not missing:
        return
    sparse = subprocess.run(["git", "-C", str(root), "config", "--get", "core.sparseCheckout"],
                            capture_output=True, text=True).stdout.strip() == "true"
    if not sparse:
        print(f"{len(missing)} preview files are not checked out; skipping them.")
        return
    print(f"Fetching {len(missing)} preview files from GitHub...")
    subprocess.run(["git", "-C", str(root), "sparse-checkout", "add", "--stdin"],
                   input="\n".join(sparse_pattern(p) for p in missing) + "\n", text=True, check=True)


def duration(src: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(src)], capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def make_thumb(src: Path, dst: Path) -> bool:
    tmp = dst.with_suffix(".tmp.jpg")
    for t in (duration(src) * 0.45, 0.0):
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(src),
                            "-frames:v", "1", "-vf", CROP, "-q:v", "5", str(tmp)], capture_output=True)
        if r.returncode == 0 and tmp.is_file() and tmp.stat().st_size > 0:
            tmp.replace(dst)
            return True
    tmp.unlink(missing_ok=True)
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=".thumbs")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--limit", type=int, default=0, help="only make this many (for testing)")
    args = ap.parse_args(argv)

    root = bc.repo_root()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    motions = bs.collect_motions(root)

    wanted = {f"{m['u']}.jpg": bs.preview_source(m) for m in motions if bs.preview_source(m)}
    for stale in out.glob("*.jpg"):
        if stale.name not in wanted:
            stale.unlink()
    todo = [(name, src) for name, src in sorted(wanted.items()) if not (out / name).is_file()]
    print(f"{len(wanted)} motions with a preview, {len(wanted) - len(todo)} thumbnails already made, {len(todo)} to make")
    if args.limit:
        todo = todo[: args.limit]
    if not todo:
        return 0

    fetch_missing(root, [src for _, src in todo])
    made = failed = 0
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        jobs = {pool.submit(make_thumb, root / src, out / name): src
                for name, src in todo if (root / src).is_file()}
        for job in cf.as_completed(jobs):
            if job.result():
                made += 1
            else:
                failed += 1
                print(f"  could not read {jobs[job]}")
    print(f"made {made} thumbnails, {failed} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
