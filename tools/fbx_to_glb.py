"""Convert Mixamo-skeleton FBX files to glTF binary (.glb) with Blender.

    python fbx_to_glb.py pairs.tsv                      # with Blender's Python module: pip install bpy
    blender -b --python fbx_to_glb.py -- pairs.tsv      # or with a Blender install

pairs.tsv has one "<source.fbx>\t<target.glb>\t<clip name>" per line. Each
file is converted on its own, in one Blender session:

  - only the armature and its bone animation are kept (no meshes, and no
    tracks on the armature object, which would move the root of the model
    the clip is played on);
  - bone names are made standard Mixamo ("mixamorig:Hips"), since older exports
    used "mixamorig1:" (and a few a bare "Hips");
  - helper bones some exports put inside the Mixamo chain ("Chestdissolve",
    "Neckdissolve", a "pelvisinte" root) are removed, the thighs are put back
    under the hips, "footinte_L/R" become the feet when there are no foot
    bones, and the animation is re-baked, so every Mixamo bone keeps its
    exact pose on every frame (checked after baking);
  - the animation is named after the clip name given (the sign);
  - Y-up glTF, with the armature's 0.01 scale kept, as in Mixamo's own files.

Files that fail are listed on stderr and in "<pairs.tsv>.failed", and the
rest carry on. Exit status is 0 unless nothing at all could be converted.
"""

import json
import re
import struct
import sys
import traceback
from pathlib import Path

import bpy

PREFIX = re.compile(r"^mixamorig\d*:")


def fcurve_lists(action):
    """The action's F-Curve collections (Blender 4.4+ keeps them in layers)."""
    if hasattr(action, "layers") and action.layers:
        return [bag.fcurves for layer in action.layers for strip in layer.strips for bag in strip.channelbags]
    return [action.fcurves]


def remove_helper_bones(arm, action) -> None:
    """Take non-Mixamo bones out of the middle of the Mixamo chain, keeping the motion.

    Records every Mixamo bone's pose (armature space) on every frame, removes the
    helper bones (their children move up to the helper's parent), then keys each
    bone's local transform so it lands on the recorded pose again.
    """
    from mathutils import Matrix

    bones = arm.data.bones
    helpers = [b.name for b in bones if not b.name.startswith("mixamorig:") and b.name != "Locator_Root"
               and any(c.name.startswith("mixamorig:") for c in b.children)]
    thighs = [n for n in ("mixamorig:LeftUpLeg", "mixamorig:RightUpLeg")
              if n in bones and "mixamorig:Hips" in bones and bones[n].parent != bones["mixamorig:Hips"]]
    if not helpers and not thighs:
        return
    scene = bpy.context.scene
    start, end = (int(round(f)) for f in action.frame_range)
    frames = range(start, end + 1)
    keep = [pb.name for pb in arm.pose.bones if pb.name not in helpers]
    recorded = {}
    for f in frames:
        scene.frame_set(f)
        recorded[f] = {n: arm.pose.bones[n].matrix.copy() for n in keep}

    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    edit = arm.data.edit_bones
    for name in helpers:
        helper = edit[name]
        for child in list(helper.children):
            child.use_connect = False
            child.parent = helper.parent
        edit.remove(helper)
    for name in ("mixamorig:LeftUpLeg", "mixamorig:RightUpLeg"):
        if name in edit and "mixamorig:Hips" in edit and edit[name].parent != edit["mixamorig:Hips"]:
            edit[name].use_connect = False
            edit[name].parent = edit["mixamorig:Hips"]
    bpy.ops.object.mode_set(mode="OBJECT")

    for fcurves in fcurve_lists(action):
        for fc in list(fcurves):
            fcurves.remove(fc)
    rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
    parent = {b.name: (b.parent.name if b.parent else None) for b in arm.data.bones}
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    for f in frames:
        for name in keep:
            p = parent[name]
            if p is None:
                basis = rest[name].inverted() @ recorded[f][name]
            else:
                basis = (rest[p].inverted() @ rest[name]).inverted() @ recorded[f][p].inverted() @ recorded[f][name]
            pb = arm.pose.bones[name]
            pb.matrix_basis = basis
            for path in ("location", "rotation_quaternion", "scale"):
                pb.keyframe_insert(path, frame=f)

    worst = 0.0
    for f in frames:
        scene.frame_set(f)
        for name in keep:
            diff = arm.pose.bones[name].matrix - recorded[f][name]
            worst = max(worst, max(abs(v) for row in diff for v in row))
    if worst > 1e-3:
        raise RuntimeError(f"re-baked motion differs from the original by {worst:.4f}")


def convert(src: str, dst: str, clip: str) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=src)

    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"expected one armature, found {len(arms)}")
    arm = arms[0]
    for o in list(bpy.data.objects):
        if o is not arm:
            bpy.data.objects.remove(o, do_unlink=True)

    action = arm.animation_data.action if arm.animation_data else None
    if action is None:
        if len(bpy.data.actions) != 1:
            raise RuntimeError(f"no animation on the armature ({len(bpy.data.actions)} actions)")
        action = bpy.data.actions[0]
        arm.animation_data_create().action = action
    for a in list(bpy.data.actions):
        if a is not action:
            bpy.data.actions.remove(a)

    # Keep only Mixamo bone tracks. The armature object and the old Locator_Root
    # bone have constant tracks that would scale or turn the root of whatever
    # model the clip is played on.
    for fcurves in fcurve_lists(action):
        for fc in list(fcurves):
            m = re.match(r'pose\.bones\["([^"]+)"\]', fc.data_path)
            if not (m and PREFIX.match(m.group(1))):
                fcurves.remove(fc)

    # Renaming a bone also renames its F-Curve paths in the armature's action.
    names = {b.name for b in arm.data.bones}
    feet = {} if any(PREFIX.sub("", n) in ("LeftFoot", "RightFoot") for n in names if PREFIX.match(n)) \
        else {"footinte_L": "mixamorig:LeftFoot", "footinte_R": "mixamorig:RightFoot"}
    for bone in arm.data.bones:
        new = "mixamorig:Hips" if bone.name == "Hips" else feet.get(bone.name) or PREFIX.sub("mixamorig:", bone.name)
        if new != bone.name:
            bone.name = new
    remove_helper_bones(arm, action)
    action.name = clip
    arm.name = "Armature"
    arm.data.name = "Armature"
    start, end = (int(round(f)) for f in action.frame_range)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=dst, export_format="GLB", export_yup=True,
        export_animations=True, export_animation_mode="ACTIONS",
        export_skins=True, export_morph=False, export_apply=False,
        export_cameras=False, export_lights=False)
    check(dst, clip)


def check(path: str, clip: str) -> None:
    """The .glb has one animation, named clip, that moves Mixamo bones only."""
    data = Path(path).read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + length])
    anims = gltf.get("animations", [])
    if len(anims) != 1 or anims[0].get("name") != clip:
        raise RuntimeError(f"expected one animation named {clip!r}, found {[a.get('name') for a in anims]}")
    # Older exports keep a still "Locator_Root" bone above the hips; the exporter
    # samples it with the rest of the skeleton.
    targets = {gltf["nodes"][c["target"]["node"]]["name"] for c in anims[0]["channels"]} - {"Locator_Root"}
    if "mixamorig:Hips" not in targets or any(not t.startswith("mixamorig:") for t in targets):
        bad = sorted(t for t in targets if not t.startswith("mixamorig:"))[:3]
        raise RuntimeError(f"not a Mixamo skeleton (animated bones such as {bad})")


def main() -> int:
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    pairs = Path(args[0])
    jobs = [line.split("\t") for line in pairs.read_text(encoding="utf-8").splitlines() if line.strip()]
    failed = []
    for src, dst, clip in jobs:
        try:
            convert(src, dst, clip)
        except Exception as e:  # keep going; report at the end
            failed.append(f"{src}\t{e}")
            print(f"FAILED {Path(src).name}: {e}", file=sys.stderr)
            traceback.print_exc(limit=1)
    Path(str(pairs) + ".failed").write_text("\n".join(failed) + ("\n" if failed else ""), encoding="utf-8")
    print(f"Converted {len(jobs) - len(failed)} of {len(jobs)} files")
    return 1 if jobs and len(failed) == len(jobs) else 0


if __name__ == "__main__":
    sys.exit(main())
