# SLMocapArchive
Collected Sign Language Motion Capture

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24378054.svg)](https://doi.org/10.5281/zenodo.24378054)

Hello, this is Studio Galt. Since 2020 we have been recording motion capture, primarily of American Sign Language (ASL). Everything here is free under CC0.

**[Browse the signs](https://studiogalt.github.io/Sign-Language-Mocap-Archive/)** Search the archive, watch each sign, and download its files without cloning anything.

**At a glance:** about 2,700 motions covering 2,100+ signs, plus the ASL fingerspelling alphabet and numbers. Each motion comes as FBX for Blender, Unreal and Mixamo-style rigs (and loads in Unity and Maya), with a rendered video and a ReadMe. See [catalog/SUMMARY.md](catalog/SUMMARY.md) for current counts and coverage.

**Please don't clone the whole repository.** It's about 45 GB. Instead:

- **One sign:** use **Download all files (zip)** on its page in the [gallery](https://studiogalt.github.io/Sign-Language-Mocap-Archive/).
- **Every sign for one program** (Unreal, MetaHuman, Mixamo, Rigify, glTF or Blender): get the [download packs](#packs) from the [latest release](../../releases/latest) or from [Hugging Face](https://huggingface.co/datasets/StudioGaltMocap/sign-language-mocap-archive).
- **A few folders with git:** use a [sparse checkout](#folders).

1. [Quick start](#quick_start)
2. [Finding a sign](#finding)
3. [Downloading](#downloading): [packs](#packs), or [only the folders you need](#folders)
4. [What's in a motion folder](#motion_folder)
5. [Reporting an error or requesting a sign](#errors)
6. [FAQ](Documentation/FAQ.md)

<a name="quick_start"></a>
## Quick start

1. Find your sign in the [gallery](https://studiogalt.github.io/Sign-Language-Mocap-Archive/), or in the [catalog](#finding) (use the row whose `status` is `current`).
2. Download just that folder ([how](#folders)), or get every sign for your program as a [pack](#packs).
3. Pick the FBX for your target:

| I'm using… | Use this file |
|---|---|
| Blender, with the Galtis avatar | `… Mesh.fbx` (or the `.blend` in *Blend File*) |
| Blender Rigify | `… Rigify APose.fbx` / `… Rigify TPose.fbx` |
| Unreal Engine 5 | `… Manny` / `… Quinn` / `… MetaHuman` FBX (newer motions) or `… No Mesh UE Mannequin.fbx` (older) |
| Mixamo-compatible rigs, Unity | `… No Mesh Mixamo.fbx` or `… Mixamo TPose.fbx` |
| Research / your own retargeting | `… No Mesh Full.fbx` (every bone), or the raw take in *FBX Files/Original* or *Raw Mocap* |

Not every motion has every file. The file set changed over the years (see [Folder layouts](#layouts)), and the catalog lists exactly what each motion has.

<a name="finding"></a>
## Finding a sign

[`catalog/catalog.csv`](catalog/catalog.csv) lists every motion, one row each. It opens in any spreadsheet, and GitHub lets you search it in the browser. [`catalog/catalog.json`](catalog/catalog.json) has the same data for scripts.

Useful columns:

| Column | Meaning |
|---|---|
| `name`, `group` | The sign as named in the folder; `group` gathers alternates (Alt 1, Var, 2, …) of the same sign |
| `date` | Upload date (ISO format, so it sorts correctly) |
| `status` | `current`, or `superseded` when the same motion was re-made under a newer date (`superseded_by` says which) |
| `folder` | Where it lives in the repo |
| `layout` | Which [folder layout](#layouts) it uses |
| `rig`, `blender_version` | Galtis rig version and Blender version it was made with |
| `raw_mocap_file` | The raw take it was cleaned from, when known |
| `raw_mocap_source` | How that link was found: `readme` (the ReadMe's Original Motion), `bundled` (the copy in *FBX Files/Original*), or `name match` (a Raw Mocap file with the sign's name, used only when the ReadMe doesn't name a take; where both a plain and a `_frames_` cut exist it is a best guess) |
| `keypose_frames` | Key pose frame numbers from the ReadMe |
| `facial_animation` | `yes` if face shape keys move beyond blinking, `no` if only blinks, `unknown` for motions whose ShapeKeys file has no key names (mostly 2023) |
| `audited_by`, `audited` | Who checked the motion against the sign, and when (from the ReadMe's *Audited by* line). `audited` is `yes` once someone has; a blank line or "Unaudited as of …" is `no` |
| `has_…` columns | Which file types exist for that motion |

The catalog is rebuilt automatically on every push by [`tools/build_catalog.py`](tools/build_catalog.py). Anything that looks misnamed or incomplete goes to [`catalog/issues.csv`](catalog/issues.csv). A raw take that really was used for more than one sign is listed in [`tools/shared_takes.txt`](tools/shared_takes.txt), so it isn't reported as a copied ReadMe value.

<a name="downloading"></a>
## Downloading

The repository holds every version of every motion, plus videos and raw takes, which comes to about 45 GB. Most people want either everything for one program (a pack) or a few signs (single folders).

<a name="packs"></a>
### Download packs

For every sign in one program, use the packs. Each [release](../../releases/latest) has zip packs of all current signs, one file set per software. The same packs and the catalog are also on [Hugging Face](https://huggingface.co/datasets/StudioGaltMocap/sign-language-mocap-archive), for download with Hugging Face's tools (`hf_hub_download`, `load_dataset`):

| Pack | Contents |
|---|---|
| `unreal` | UE5 Manny and Quinn, A-pose and T-pose (older signs: UE Mannequin) |
| `metahuman` | MetaHuman, A-pose and T-pose (signs from 2026) |
| `mixamo` | Mixamo skeleton, also for Unity Humanoid |
| `rigify` | Blender Rigify, A-pose and T-pose (signs from 2025) |
| `gltf` | glTF binary (`.glb`) on the Mixamo skeleton, for three.js, Babylon.js, Godot and other web or glTF tools: skeleton and animation only, hands included, no face |
| `blender` | The full Galtis skeleton (newest signs: the Mesh FBX), plus the Galtis rig as a separate file |

Big packs are split into parts by letter (e.g. `SLMA-2026-11-11-blender-part1-A-C.zip`; fingerspelling comes last, in a part ending `-Fingerspelling`). Each zip has a README and an `index.csv` of the signs inside, and `SLMA-<release>-pack-index.csv` on the release page says which zip holds each sign. Packs hold only the current version of each sign, with no videos or raw takes; for those, download the [motion folders](#folders).

<a name="folders"></a>
### Only the folders you need

Git can download just the folders you want, without the rest of the archive:

```bash
git clone --filter=blob:none --sparse https://github.com/StudioGalt/Sign-Language-Mocap-Archive.git
cd Sign-Language-Mocap-Archive
git sparse-checkout set "SG ASL Dictionary/ASL C/SG ASL Cabinet 2025-2-12 Upload"
```

Copy the folder path from the `folder` column of the catalog. To add more folders later, run `git sparse-checkout add "<folder>"`.

Without git: [DownGit](https://downgit.github.io/#/home) downloads a single folder as a zip. Paste in the folder's GitHub URL. There is a [DownGit walkthrough](Documentation/Workflows/DownGit%20Workflow%20%28How%20to%20download%20specific%20files%29.md) in Documentation, and more guides (Maya, Unreal, Rokoko) in the [Documentation index](Documentation/README.md).

<a name="motion_folder"></a>
## What's in a motion folder

Each motion is a folder named `SG ASL <Sign> <Date> Upload`. The newest layout (2026) looks like this:

```
SG ASL <Sign> <Date> Upload/
├── Blend File/       Working.zip: the Blender file used to make the motion
├── Documentation/    ReadMe.txt, ShapeKeys.txt, Framelog.txt, captioned video (.webm)
├── FBX Files/
│   ├── Full/         Mesh.fbx: Galtis with mesh and every bone
│   ├── Mixamo/       Mixamo-compatible skeleton (most motions)
│   ├── Original/     the raw take before cleanup
│   ├── Rigify/       Rigify A-pose and T-pose
│   └── Unreal_Engine/ Manny, Quinn and MetaHuman, A-pose and T-pose
└── Poses/
    ├── CSV/          bone transforms for each key pose
    └── JSON/         the same poses for JSON Pose Manager (jpm)
```

<a name="layouts"></a>
### Folder layouts

The layout has improved over time. Older folders are left as they were so existing links keep working.

| Layout | Used | What's different |
|---|---|---|
| v1 | 2023 (and the 2023 fingerspelling) | All files loose in one folder: Mesh, No Mesh Full/Mini/Mixamo FBX, MKV and captioned MP4, ReadMe, ShapeKeys |
| v2 | Nov 2023 – Apr 2024 | *Documentation* and *FBX Files* subfolders; *Poses* added in 2024 |
| v3 | Apr 2024 – Mar 2025 | FBX split into *Game Ready* (Mesh, Mixamo, UE Mannequin, Rigify) and *Research* (Full, Mini, UEPlus); pose JSON; GIF; *Blend File* from Jan 2025 |
| v4 | Mar 2025 – Jan 2026 | FBX grouped by target: *Full*, *Mixamo*, *Rigify*, *Unreal_Engine* (Manny, Quinn), *Other* (Mini, UEPlus, until Dec 2025); the GIF is no longer included from mid-2025 |
| v5 | Jan 2026 – now | Adds *FBX Files/Original* (raw take), MetaHuman FBX and *Poses/CSV*; Mini, UEPlus and the pose .blend libraries are no longer included |

<a name="errors"></a>
## Reporting an error or requesting a sign

If a sign is wrong or a file doesn't load, please [open an issue](../../issues/new/choose) using the **Sign correction** or **File problem** template. Corrections are re-recorded under a new date ([FAQ](Documentation/FAQ.md#general_faq), question 12), and the catalog marks the old one as superseded.

Missing a sign? Use the **Request a sign** template, or add a 👍 to an [existing request](../../issues?q=is%3Aissue%20is%3Aopen%20label%3A%22sign%20request%22%20sort%3Areactions-%2B1-desc). The most-wanted signs are recorded first.

Questions, ideas, or something you've made with the archive? Post it in [Discussions](../../discussions). To help with the scripts, documentation or motions, see [CONTRIBUTING](.github/CONTRIBUTING.md).

Every sign has its own page you can link to, for example [Cabinet](https://studiogalt.github.io/Sign-Language-Mocap-Archive/sign/cabinet-2025-2-12/). Use **Copy link** in the gallery to get it.

If you use the archive in research, please cite it:

> Studio Galt (2026). *Sign Language Mocap Archive* (Version 2026-11-19) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24378054

GitHub's **Cite this repository** button gives the same citation in other formats, from [CITATION.cff](CITATION.cff). The [Zenodo record](https://zenodo.org/records/24378054) holds a permanent copy of the catalog, documentation, pipeline scripts and rig; the motions themselves are here on GitHub. Citing is appreciated, not required: everything is CC0.

<a name="faq"></a>
## FAQ

Answers about the licence, why ASL, how errors are corrected, AI use, the recording setup, the Galtis avatar and what each file is are in [Documentation/FAQ.md](Documentation/FAQ.md):
[General](Documentation/FAQ.md#general_faq) · [Tech](Documentation/FAQ.md#tech_faq) · [Avatar](Documentation/FAQ.md#avatar_faq) · [Files](Documentation/FAQ.md#file_faq)
