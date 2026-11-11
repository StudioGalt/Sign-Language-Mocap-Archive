# Blender scripts

These are the scripts that turn a raw take into an upload folder in this archive. They are the versions used for the newest uploads (Blender 5.2.1 LTS, rig Galtis 8, September 2026), and they produce the v5 [folder layout](../../README.md#layouts). What changed and when is in the [changelog](CHANGELOG.md). The July 2024 scripts are kept in [Legacy (2024)](Legacy%20%282024%29).

The scripts are written for one person's setup, so expect to adjust them. They run from Blender's Text Editor, inside the Galtis rig file from the [Rigs](../../Rigs) folder.

## Folders

| Folder | What's in it | Where it goes |
|---|---|---|
| [Pipeline](Pipeline) | The numbered steps, run in order for every take | Open in Blender's Text Editor |
| [Workspace Scripts](Workspace%20Scripts) | Helper modules and the export steps that MegaExporter runs | Copy into `<your workspace>\Scripts` |
| [Utilities](Utilities) | `U)` clean-up tools used as needed, and the Reincarnator scripts for updating old motions | Open in Blender's Text Editor |
| [Rokoko](Rokoko) | Importer for Rokoko suit recordings, used instead of `1) Importer` | Open in Blender's Text Editor |

## Before you start

1. **Blender 5.2.1 LTS**, and the newest Galtis rig from [Rigs](../../Rigs). The rig's armature is called `root`, and the scripts expect that name.
2. **Add-ons:**
   - **Animation Layers** by Tal Hershkovich. Steps 2a and 2b and most utilities depend on it.
   - **Auto-Rig Pro**, to retarget the raw take onto Galtis before step 2a.
   - **MMD Tools**, only for the MMD / PMX export in Process Rigs.
   - **JSON Pose Manager** (optional), to load the pose `.json` files.
3. **Set up a workspace folder.** Run `Pipeline/U) 0 Set Working Directory.py` once and pick a folder. It creates *AvatarFolder*, *Unprocessed Animations*, *Storage*, *Mannequin*, *Ready for Upload* and other folders, and saves the rig file into *AvatarFolder*.
4. **Copy the [Workspace Scripts](Workspace%20Scripts) files into `<workspace>\Scripts`.** Steps 2a, 3 and 5 load their helper modules from the `Scripts` folder beside the take's folder.
5. **Put the Unreal mannequins in `<workspace>\Mannequin`.** Export `SKM_Manny_Simple.FBX` and `SKM_Quinn_Simple.FBX` from your own Unreal Engine install. They are Epic's files, so they aren't included here.
6. **Folder paths.** MegaExporter and `U) Anchor` look in `H:\Galt Workspace` by default. Set the `GALT_WORKSPACE` environment variable, or edit the line marked in each script. The Rokoko importer uses `GALT_ROKOKO_WORKSPACE`. Paths are joined Windows-style (`\`) in places, so the scripts are only tested on Windows.

## The pipeline

Put the raw FBX in *Unprocessed Animations*, then:

| Step | Script | What it does |
|---|---|---|
| 1 | `1) Importer` | Imports the take, names it from the file name and date, makes the take's working folder and saves `<Stamp> Unedited.blend`. Records the Blender version, date and source take on the rig. |
| – | *(by hand)* | Retarget the take onto Galtis with Auto-Rig Pro. |
| 2a | `2a) Superset New` | Sets up Animation Layers: keeps the frame-0 T-pose, adds a neutral pose at the first and last frames, and adds anchor and correction layers. |
| – | *(by hand)* | Clean up the sign: hands, fingers, contacts, timing. Mark each key pose with a timeline marker. |
| 2b | `2b) Baker Combined` | Snaps FK to IK, bakes the layers, writes the per-layer CSV records and saves the working copy. |
| 3 | `3) Pose Magic` | Makes a pose asset for every timeline marker and writes its JSON, CSV and TXT files (via `pose_magic_lib`). |
| 4 | `4) Archive II New` | Removes leftover actions (anything not named `SG ASL …`), tidies the file and writes the ReadMe. Bake the animation layers first. |
| 5 | `5) MegaExporter` | Runs, in order: `Normal Exporter.py` (Mesh FBX, captioned WebM, ShapeKeys), `Process Rigs.py` (Full, Rigify, Manny, Quinn, MetaHuman, Mixamo, MMD/PMX and Soma versions) and `Bundler.py` (sorts everything into `<Stamp> Upload` and copies it to *Ready for Upload*). It checks that all three exist before starting, and stops at the first error. |

The file names follow the stages in your changelog: *Unedited* (as imported), *Working* (edits before baking), *Cleaned* (a backup after baking) and *Finished* (baked, with the pose library).

### Unreal export settings

If you export by hand for Unreal Engine: Z up, Y forward, Selected Objects on, Smoothing set to Face, Leaf Bones off, and under Bake Animation, export the animation but not the rig.

## Workspace Scripts

| File | Used by |
|---|---|
| `util_scripts.py` | 2a, Process Rigs: bone-collection visibility, Animation Layers set-up, keyframe helpers |
| `pose_magic_lib.py` | 3, Normal Exporter, Process Rigs, `U) OpenPose WIP`: pose assets with thumbnails, and JSON / CSV / TXT pose files |
| `bone_maps.py` | Process Rigs: bone-name maps from Galtis to Rigify, UE Mannequin, MetaHuman, Mixamo, Ready Player Me, Soma and MMD |
| `anchor.py` | `U) Anchor` |
| `Normal Exporter.py`, `Process Rigs.py`, `Bundler.py` | Run by `5) MegaExporter` |

MegaExporter also lists `AI Export.py`, which renders OpenPose, depth and line-art passes for AI video. It isn't published, so it's commented out in the list here.

## Utilities

| Script | Use it when |
|---|---|
| `U) Anchor` | Keying the whole rig at frame 0 and at two anchor frames |
| `U) Fractional Paste` | Pasting a copied pose at partial strength (blend between poses) |
| `U) No Hands` | The take has no hand data |
| `U) Offhand` | Cleaning the unused hand in one-handed signs |
| `U) Quickener New` | Removing dead frames at the start of a take |
| `U) Shortener` | Removing extra frames when the first cut left too much dead time |
| `U) Renamer` | Renaming the take and its file in one step |
| `U) Snapper WIP` | Snapping FK to IK, or IK to FK, over a frame range |
| `U) OpenPose WIP` | Mapping the rig to an OpenPose skeleton (work in progress) |
| `Reincarnator 1)`, `Reincarnator 7)` | Updating an old motion: 1) brings its Finished action into the current rig file; 7) bundles the result. The rest of the pipeline runs in between. |
