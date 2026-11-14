#!/usr/bin/env python3
"""Publish a release to the archive's Hugging Face dataset.

    python tools/build_hf.py --tag 2026-11-12 --hf-repo NAME/sign-language-mocap-archive --card-only
    python tools/build_hf.py --tag 2026-11-12 --hf-repo NAME/sign-language-mocap-archive

The dataset gets:
  README.md               the dataset card (written here from the catalog)
  catalog/catalog.csv     one row per motion; shown in Hugging Face's dataset viewer
  catalog/pack-index.csv  which pack zip holds each motion's file
  packs/                  every file attached to the GitHub release: the pack zips, the
                          pack index and the Galtis rig

Each release file is downloaded from GitHub, uploaded, then deleted, so only one
sits on disk at a time. Files in packs/ from an older release are removed in the
same run, and the dataset is tagged with the release's tag, so every earlier
release stays downloadable at its tag.

Needs: the GitHub CLI (gh), `pip install huggingface_hub`, and a Hugging Face
token with write access in HF_TOKEN. --card-only writes the card and catalog
files into --out without uploading anything.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "StudioGalt/Sign-Language-Mocap-Archive"
ROOT = Path(__file__).resolve().parent.parent

PACK_TEXT = {
    "unreal": "UE5 Manny and Quinn, A-pose and T-pose (older signs: UE Mannequin)",
    "metahuman": "MetaHuman, A-pose and T-pose (signs from 2026)",
    "mixamo": "Mixamo skeleton, also for Unity Humanoid",
    "rigify": "Blender Rigify, A-pose and T-pose (signs from 2025)",
    "gltf": "glTF binary (.glb) on the Mixamo skeleton, for three.js, Babylon.js and other web tools",
    "blender": "The full Galtis skeleton (newest signs: the Mesh FBX)",
}


def gh_json(*args):
    return json.loads(subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout)


def release_assets(repo: str, tag: str) -> list[dict]:
    rel = gh_json("api", f"repos/{repo}/releases/tags/{tag}")
    return [{"name": a["name"], "size": a["size"], "id": a["id"]} for a in rel["assets"]]


def download(repo: str, asset: dict, dest: Path) -> Path:
    """Download one release file through the REST API."""
    path = dest / asset["name"]
    with open(path, "wb") as fh:
        subprocess.run(["gh", "api", "-H", "Accept: application/octet-stream",
                        f"repos/{repo}/releases/assets/{asset['id']}"], check=True, stdout=fh)
    if path.stat().st_size != asset["size"]:
        sys.exit(f"{asset['name']}: downloaded {path.stat().st_size} bytes, expected {asset['size']}")
    return path


def citation() -> tuple[str, str]:
    """(version DOI, version) from CITATION.cff, without needing a YAML library."""
    doi = version = ""
    for line in (ROOT / "CITATION.cff").read_text(encoding="utf-8").splitlines():
        if line.startswith("doi:"):
            doi = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("version:"):
            version = line.split(":", 1)[1].strip().strip('"')
    return doi, version


def gb(n: int) -> str:
    return f"{n / 1e9:.2f} GB" if n >= 1e8 else f"{n / 1e6:.1f} MB"


def card(tag: str, hf_repo: str, repo: str, assets: list[dict]) -> str:
    rows = list(csv.DictReader(open(ROOT / "catalog/catalog.csv", encoding="utf-8")))
    current = [r for r in rows if r["status"] == "current"]
    signs = len({r["group"] for r in current if r["collection"] == "Dictionary"})
    spelled = sum(1 for r in current if r["collection"] == "Fingerspelling")
    doi, version = citation()
    owner, name = repo.split("/")
    gallery = f"https://{owner.lower()}.github.io/{name}/"
    total = sum(a["size"] for a in assets)

    pack_rows = []
    for a in sorted(assets, key=lambda a: a["name"]):
        n = a["name"]
        key = next((k for k in PACK_TEXT if f"-{k}." in n or f"-{k}-part" in n), None)
        what = PACK_TEXT[key] if key else ("Which zip holds each motion's file" if "pack-index" in n
                                           else "The Galtis rig" if n.endswith(".blend") else "")
        pack_rows.append(f"| `packs/{n}` | {gb(a['size'])} | {what} |")

    return f"""---
license: cc0-1.0
pretty_name: Sign Language Mocap Archive
language:
- ase
tags:
- sign-language
- american-sign-language
- asl
- motion-capture
- mocap
- gltf
- animation
- fbx
- blender
- unreal-engine
size_categories:
- 1K<n<10K
configs:
- config_name: catalog
  default: true
  data_files:
  - split: train
    path: catalog/catalog.csv
- config_name: pack_index
  data_files:
  - split: train
    path: catalog/pack-index.csv
---

# Sign Language Mocap Archive

Motion capture of American Sign Language (ASL) by Studio Galt: {len(current):,} current motions, covering {signs:,} signs (with their alternates) and {spelled} fingerspelling letters and numbers. Recorded with an Xsens Link suit and StretchSense gloves, cleaned in Blender, and released as FBX for Blender, Unreal Engine (including MetaHuman) and Mixamo-compatible rigs, which also load in Unity and Maya, and as glTF for the web. Everything is CC0: no permission or credit needed.

This dataset holds the catalog and the download packs of release **{tag}**. The full archive, with every motion's videos, poses, older versions and the raw takes, is on [GitHub](https://github.com/{repo}), and each sign can be watched and downloaded on its own in the [gallery]({gallery}).

## What's here

| Path | Size | Contents |
|---|---|---|
| `catalog/catalog.csv` | | One row per motion ({len(rows):,}, including superseded versions) |
| `catalog/pack-index.csv` | | Which pack zip holds each motion's file |
{chr(10).join(pack_rows)}

The packs hold the current version of each sign only, as FBX, without videos or raw takes ({gb(total)} in all). Big packs are split into parts by letter; each zip has a README and an `index.csv` of the signs inside.

## Using it

The catalog loads as a table:

```python
from datasets import load_dataset

catalog = load_dataset("{hf_repo}", "catalog", split="train")
current = catalog.filter(lambda r: r["status"] == "current")
```

Download a pack, or everything:

```python
from huggingface_hub import hf_hub_download, snapshot_download

path = hf_hub_download("{hf_repo}", "packs/SLMA-{tag}-mixamo.zip", repo_type="dataset")
snapshot_download("{hf_repo}", repo_type="dataset", allow_patterns="packs/*rigify*")
```

Earlier releases stay available: pass `revision="<release tag>"`.

To get a single sign, copy its `folder` from the catalog and download that folder from GitHub (see [Downloading only what you need](https://github.com/{repo}#downloading)).

## Catalog columns

| Column | Meaning |
|---|---|
| `name`, `group` | The sign as named in its folder; `group` gathers alternates (Alt 1, Var, 2, …) of the same sign |
| `collection`, `section` | Dictionary or Fingerspelling, and the letter section |
| `date` | Recording upload date |
| `status` | `current`, or `superseded` when the motion was re-made under a newer date (`superseded_by` says which) |
| `folder` | Where the motion lives in the GitHub repository |
| `rig`, `blender_version` | Galtis rig and Blender version it was made with |
| `raw_mocap_file`, `raw_mocap_source` | The raw take it was cleaned from, and how that link was found |
| `keypose_count`, `keypose_frames` | Key poses marked in the motion |
| `facial_animation` | Whether face shape keys move beyond blinking |
| `has_…` | Which file types the motion has |

## Recording

Signs are performed and recorded by Studio Galt, cleaned in Blender on the Galtis avatar rig, and exported for each target skeleton. Each motion's ReadMe names the raw take it came from; the raw takes are in the repository's *Raw Mocap* folder. The rig and the Blender pipeline scripts are in the GitHub repository. Report a wrong sign or a broken file through the repository's issue templates.

## Citation

If you use the archive in research, please cite it:

> Studio Galt (2026). *Sign Language Mocap Archive* (Version {version}) [Data set]. Zenodo. https://doi.org/{doi}

## License

[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/): dedicated to the public domain.
"""


def write_local(out: Path, tag: str, hf_repo: str, repo: str, assets: list[dict]) -> None:
    (out / "catalog").mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text(card(tag, hf_repo, repo, assets), encoding="utf-8")
    shutil.copy(ROOT / "catalog/catalog.csv", out / "catalog/catalog.csv")
    idx = next((a for a in assets if a["name"].endswith("pack-index.csv")), None)
    if idx:
        download(repo, idx, out).replace(out / "catalog/pack-index.csv")
    else:
        print("No pack index on the release yet; catalog/pack-index.csv left out.")


def publish(out: Path, tag: str, hf_repo: str, repo: str, assets: list[dict]) -> None:
    from huggingface_hub import CommitOperationDelete, HfApi

    api = HfApi(token=os.environ.get("HF_TOKEN"))
    api.create_repo(hf_repo, repo_type="dataset", exist_ok=True)
    have = {f for f in api.list_repo_files(hf_repo, repo_type="dataset")}

    work = out / "_download"
    work.mkdir(exist_ok=True)
    for a in assets:
        name = a["name"]
        print(f"{name} ({gb(a['size'])})", flush=True)
        api.upload_file(path_or_fileobj=str(download(repo, a, work)), path_in_repo=f"packs/{name}",
                        repo_id=hf_repo, repo_type="dataset",
                        commit_message=f"Add {name} from release {tag}")
        (work / name).unlink()

    keep = {f"packs/{a['name']}" for a in assets}
    stale = sorted(f for f in have if f.startswith("packs/") and f not in keep)
    if stale:
        print("Removing files of the previous release:", *stale, sep="\n  ")
        api.create_commit(hf_repo, repo_type="dataset",
                          operations=[CommitOperationDelete(path_in_repo=f) for f in stale],
                          commit_message=f"Remove packs replaced by release {tag}")

    api.upload_folder(folder_path=str(out), repo_id=hf_repo, repo_type="dataset",
                      allow_patterns=["README.md", "catalog/*"],
                      commit_message=f"Card and catalog for release {tag}")
    api.create_tag(hf_repo, tag=tag, repo_type="dataset", exist_ok=True,
                   tag_message=f"Release {tag}: https://github.com/{repo}/releases/tag/{tag}")
    print(f"Done: https://huggingface.co/datasets/{hf_repo}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="GitHub release to publish, e.g. 2026-11-12")
    ap.add_argument("--hf-repo", required=True, help="Hugging Face dataset, e.g. NAME/sign-language-mocap-archive")
    ap.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository of the release")
    ap.add_argument("--out", default="hf_dataset", help="folder for the card and catalog files")
    ap.add_argument("--card-only", action="store_true", help="write the card and catalog locally; upload nothing")
    args = ap.parse_args(argv)

    assets = release_assets(args.repo, args.tag)
    if not assets:
        sys.exit(f"Release {args.tag} has no files yet; run the packs workflow first.")
    out = Path(args.out)
    write_local(out, args.tag, args.hf_repo, args.repo, assets)
    print(f"Card and catalog written to {out}/")
    if not args.card_only:
        publish(out, args.tag, args.hf_repo, args.repo, assets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
