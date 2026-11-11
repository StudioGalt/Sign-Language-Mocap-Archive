# Blender scripts (July 2024)

These are kept for reference. The current scripts are one folder up, in [Documentation/Scripts](../README.md).

These are the scripts used to turn a raw take into an upload folder, run in Blender's Text Editor in numbered order. They are a snapshot of the pipeline as of **July 2024** (Blender 4.2), which produced the v3 [folder layout](../../../README.md#layouts). Newer uploads use a later version of the pipeline.

## Before you run them

1. **Set your folders.** Each script starts with a `WORKSPACE` setting (the Exporter also has `STORAGE`). Edit it, or set the `GALT_WORKSPACE` / `GALT_STORAGE` environment variables before starting Blender. The Rokoko importer uses `GALT_ROKOKO_WORKSPACE`.
2. **Install the add-ons they expect:**
   - Animation Layers by Tal Hershkovich (SuperSet, Layer Update)
   - Auto-Rig Pro, for retargeting before SuperSet
   - Pose Exporter by Bookyakuno (Baker, Exporter, Triple 6)
   - JSON Pose Manager, if you want to load the exported pose JSON files
3. **Install the extra Python modules** into Blender's own Python for the Exporter: `numpy`, `Pillow` and `moviepy`.
4. **Windows only, in places:** paths are joined with `\\`, and the Exporter calls `taskkill` to stop ffmpeg.

## Order

| Script | What it does |
|---|---|
| `1) Importer Xsens 240 fps.py` | Imports the first FBX in the workspace, cleans up the take name, makes a dated working folder and keys the locator. |
| `1) Importer Rokoko 30fps.py` | Same, for 30 fps Rokoko recordings (baked to 60 fps). |
| `2) SuperSet.py` | Run after retargeting with Auto-Rig Pro. Adds animation layers, keeps the frame-0 T-pose, sets anchor points 30 frames from each end, and stabilises hips, legs and chest on separate layers. |
| `2b) Baker.py` | Run after animating. Snaps FK to IK, bakes the layers and exports each layer as CSV. |
| `2c) Layer Update.py` | Small helper for Animation Layers. |
| `3) Pose Magic.py` | Turns timeline markers into pose assets and exports each one as a jpm-compatible JSON file. Needs the current file open in the Asset Browser. |
| `4) Archive II New.py` | Removes non-"SG ASL" actions and tidies the file for archiving. Bake the animation layers first. |
| `5) Exporter.py` | Converts the hair to mesh, exports `Mesh.fbx`, renders the video and adds captions. The longest step. |
| `6) Triple 6 New.py` | Exports the no-mesh FBX variants (Full, UEPlus, UE Mannequin, Mini, Mixamo) and the Mixamo pose library. |
| `7) Bundler.py` | Moves everything into the `… Upload` folder that goes on GitHub. |
