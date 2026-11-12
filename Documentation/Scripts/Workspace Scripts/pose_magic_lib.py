import bpy
import os
import json
import datetime
import csv
from typing import List, Dict, Optional, Tuple

# Pose Magic: a pose asset (and JSON / CSV / TXT files) for every timeline marker of a take.
# Blender 5.x. Works on the MetaHuman rig (MH_rig, made by build_metahuman_rig.py) and on the Galtis rig ('root').
#
# On the MetaHuman rig:
#   - the rig is found by itself (armature_name=None)
#   - arms and legs that are on IK have their FK bones turned to the IK pose first (on that frame only, nothing
#     is keyed), so the FK rotations written to the CSV / TXT are the pose you see
#   - the pose asset holds the rig's controls only (not the MetaHuman's own bones or helper bones)
#   - the CSV / TXT list the FK controls, named as on Galtis where there is one
# The Metahuman Rig tab's "Pose Magic" button runs this file; it can also be run from a script:
#     import pose_magic_lib
#     pose_magic_lib.run_pose_magic(max_poses=50, asset_library_reference='LOCAL')
#
# Thumbnails: Blender draws a pose asset's thumbnail through the scene's active camera. Pose Magic puts a camera
# of its own ("SGM Pose Camera") in front of the character, framed so the whole body - in every marked pose -
# fits (thumbnail="WHOLE_BODY"), or from the hips up ("UPPER_BODY"). "SCENE" leaves the scene's camera as it is.
# While the thumbnails are drawn, everything but the character is hidden (thumbnail_isolate=True); the scene's
# camera and those objects are put back once Blender has finished the thumbnails.
#
# Face poses (face_poses=True): the face board's controls on each marker are made into a pose asset of their own,
# "<pose name> Face P1", P2 ..., in the same library. Its thumbnail is a picture of the face on that frame, taken
# by "SGM Face Camera" from in front of the face (face_view="FRONT") or from its left or right side ("LEFT",
# "RIGHT"). The face poses are made first, then the body poses.

LIB_VERSION = 4          # 2: pose_prefix (the name the poses are given); 3: thumbnail camera; 4: face board poses

GALTIS_BONES = [
    "bicepfk_L", "forearmfk_L", "handfk_L", "bicepfk_R", "forearmfk_R", "handfk_R",
    "thighfk_L", "shinfk_L", "footfk_L", "toefk_L", "thighfk_R", "shinfk_R",
    "footfk_R", "toefk_R", "thumbfk_01_L", "thumbfk_02_L", "thumbfk_03_L", "thumbfk_04_L",
    "pinkyinte_metacarpal_L", "pinkyfk_01_L", "pinkyfk_02_L", "pinkyfk_03_L", "pinkyfk_04_L",
    "indexinte_metacarpal_L", "indexfk_01_L", "indexfk_02_L", "indexfk_03_L", "indexfk_04_L",
    "middleinte_metacarpal_L", "middlefk_01_L", "middlefk_02_L", "middlefk_03_L", "middlefk_04_L",
    "ringinte_metacarpal_L", "ringfk_01_L", "ringfk_02_L", "ringfk_03_L", "ringfk_04_L",
    "thumbfk_01_R", "thumbfk_02_R", "thumbfk_03_R", "thumbfk_04_R", "pinkyinte_metacarpal_R",
    "pinkyfk_01_R", "pinkyfk_02_R", "pinkyfk_03_R", "pinkyfk_04_R", "indexinte_metacarpal_R",
    "indexfk_01_R", "indexfk_02_R", "indexfk_03_R", "indexfk_04_R", "middleinte_metacarpal_R",
    "middlefk_01_R", "middlefk_02_R", "middlefk_03_R", "middlefk_04_R", "ringinte_metacarpal_R",
    "ringfk_01_R", "ringfk_02_R", "ringfk_03_R", "ringfk_04_R",
    "collar_R", "collar_L", "neckfk", "headfk", "chest_5",
    "chest_4", "chest_3", "chest_2", "chest_1", "hip"
]
AUTHOR = "Studio Galt Mocap"
SWITCH_BONE = "FKIK Switch"
CAMERA_NAME = "SGM Pose Camera"
CAMERA_LENS = 50.0        # mm
CAMERA_MARGIN = 1.08      # room round the character (1.0 = touching the edges)
HIP_BONES = ("pelvis", "hip", "hips", "Hips", "root")       # the upper-body thumbnail starts here
FACE_CAMERA_NAME = "SGM Face Camera"
FACE_MARGIN = 1.15
NECK_BONES = ("neck_02", "neck_01", "neckfk", "neck")         # the face thumbnail starts at the first of these
THUMB_SIZE = 256
SIDE_PAIRS = (("upperarm_l", "upperarm_r"), ("thigh_l", "thigh_r"), ("bicepfk_L", "bicepfk_R"),
              ("thighfk_L", "thighfk_R"), ("collar_L", "collar_R"))


def is_metahuman_rig(obj) -> bool:
    return obj is not None and obj.type == "ARMATURE" and obj.get("sgm_rig") == "metahuman"


def metahuman_limbs(rig) -> list:
    try:
        return json.loads(rig.get("sgm_limbs", "[]"))
    except ValueError:
        return []


def metahuman_fk_bones(rig) -> List[str]:
    """The MetaHuman rig's FK controls, in the Galtis list's order (metacarpals are <finger>fk_metacarpal_* here),
    then any it has that Galtis doesn't (neckfk_01)."""
    try:
        controls = list(json.loads(rig.get("sgm_control_map", "{}")).values())
    except ValueError:
        controls = []
    ordered = []
    for name in GALTIS_BONES:
        name = name.replace("inte_metacarpal", "fk_metacarpal")
        if name in controls and name not in ordered:
            ordered.append(name)
    return ordered + [c for c in controls if c not in ordered]


def metahuman_controls(rig) -> List[str]:
    """Everything a person poses: FK and IK controls, elbow / knee targets, master."""
    chain = {n for limb in metahuman_limbs(rig) for n in limb["ik"]}
    return [b.name for b in rig.data.bones if b.get("sgm_control") and b.name not in chain and b.name != SWITCH_BONE
            and not b.name.endswith(("_ikmch", "_aim")) and "_follow" not in b.name]


def fk_from_ik(rig) -> List[str]:
    """Turn the FK bones of every limb that is on IK to the IK pose (current frame, no keys). Returns the limbs."""
    switch = rig.pose.bones.get(SWITCH_BONE)
    done = []
    for limb in metahuman_limbs(rig):
        try:
            on_ik = switch is not None and float(switch[limb["switch"]]) > 0.5
        except (KeyError, TypeError, ValueError):
            on_ik = False
        if not on_ik:
            continue
        for fk_name, part in zip(limb["fk"], ("upper", "lower", "end")):
            fk, ik = rig.pose.bones.get(fk_name), rig.pose.bones.get(f"{limb[part]}_ikmch")
            if fk is None or ik is None:
                continue
            location = fk.location.copy()
            fk.matrix = ik.matrix
            fk.location = location
            bpy.context.view_layer.update()
        done.append(limb["switch"])
    return done


def as_quaternion(bone):
    """The bone's rotation as a quaternion, whatever its rotation mode."""
    from mathutils import Quaternion
    if bone.rotation_mode == 'QUATERNION':
        return bone.rotation_quaternion.copy()
    if bone.rotation_mode == 'AXIS_ANGLE':
        angle, x, y, z = bone.rotation_axis_angle
        return Quaternion((x, y, z), angle)
    return bone.rotation_euler.to_quaternion()


def view3d_override():
    wm = bpy.context.window_manager
    for window in (wm.windows if wm else []):
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                region = next((r for r in area.regions if r.type == "WINDOW"), None)
                if region:
                    return {"window": window, "area": area, "region": region}
    return {}


# --- thumbnail camera ---

def follows(obj, armature) -> bool:
    """An armature that moves with the character's rig (face, outfit, DNA head) or is parented to it."""
    if obj is armature:
        return True
    if obj.type != "ARMATURE":
        return False
    if obj.parent is armature or obj.get("sgm_follows_body"):
        return True
    constraints = list(obj.constraints) + [c for pb in obj.pose.bones for c in pb.constraints]
    return any(getattr(c, "target", None) is armature for c in constraints)


def _meshes_of(rigs) -> list:
    found = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue
        owners = {m.object for m in obj.modifiers if m.type == "ARMATURE"} | {obj.parent}
        if owners & rigs:
            found.append(obj)
    return found


def character_objects(armature) -> list:
    """The character's visible meshes: those deformed by the rig or by a skeleton that follows it. A rig with no
    mesh of its own (a metarig or a generated Rigify rig constrained to Galtis) gets the meshes of the rig it follows."""
    rigs = {o for o in bpy.context.scene.objects if follows(o, armature)}
    found = _meshes_of(rigs)
    if not found:
        constraints = list(armature.constraints) + [c for pb in armature.pose.bones for c in pb.constraints]
        leaders = {t for c in constraints for t in [getattr(c, "target", None)] + [getattr(x, "target", None) for x in getattr(c, "targets", [])]
                   if t is not None and t is not armature and t.type == "ARMATURE"}
        rigs = {o for o in bpy.context.scene.objects for lead in leaders if follows(o, lead)}
        found = _meshes_of(rigs)
    return found


def character_axes(armature):
    """(front, left, up) in world space, from the rig's shoulders or hips; facing -Y when it can't tell."""
    from mathutils import Vector
    up = Vector((0, 0, 1))
    bones = armature.data.bones
    for left, right in SIDE_PAIRS:
        if left in bones and right in bones:
            to_left = (armature.matrix_world @ bones[left].head_local) - (armature.matrix_world @ bones[right].head_local)
            to_left.z = 0.0
            if to_left.length > 1e-9:
                to_left.normalize()
                return up.cross(-to_left).normalized(), to_left, up
    return Vector((0, -1, 0)), Vector((1, 0, 0)), up


def hip_height(armature):
    """The world height of the hips' bone on the current frame, or None."""
    pb = next((armature.pose.bones[n] for n in HIP_BONES if n in armature.pose.bones), None)
    return None if pb is None else (armature.matrix_world @ pb.head).z


def body_points(armature, frames, upper_body=False):
    """The character's mesh vertices (as deformed, in world space) on each of the frames, as an (n, 3) array;
    for the upper body, nothing below the hips."""
    import numpy as np
    scene = bpy.context.scene
    meshes = character_objects(armature)
    chunks = []
    for frame in frames:
        scene.frame_set(frame)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        here = []
        for obj in meshes:
            ev = obj.evaluated_get(depsgraph)
            mesh = ev.to_mesh()
            try:
                co = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
                mesh.vertices.foreach_get("co", co)
            finally:
                ev.to_mesh_clear()
            co = co.reshape(-1, 3)
            if len(co):
                mw = np.array(ev.matrix_world, dtype=np.float64)
                here.append(co @ mw[:3, :3].T + mw[:3, 3])
        if not here:                               # no meshes: the bones
            here = [np.array([tuple(armature.matrix_world @ p) for pb in armature.pose.bones for p in (pb.head, pb.tail)])]
        pts = np.concatenate(here)
        if upper_body:
            hips = hip_height(armature)
            if hips is not None and (pts[:, 2] >= hips).any():
                pts = pts[pts[:, 2] >= hips]
        chunks.append(pts)
    return np.concatenate(chunks) if chunks else np.zeros((0, 3))


def place_camera(name, points, x_axis, up, toward, margin=CAMERA_MARGIN):
    """A perspective camera called name, looking along -toward (its X = x_axis, Y = up), at the distance where
    every point is in view with the margin. Returns it."""
    import math
    import numpy as np
    from mathutils import Matrix
    axes = np.array([tuple(x_axis), tuple(up), tuple(toward)])
    local = points @ axes.T
    lo, hi = local.min(axis=0), local.max(axis=0)

    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    data.type = "PERSP"
    data.lens = CAMERA_LENS
    data.sensor_fit = "VERTICAL"
    cam = bpy.data.objects.get(name)
    if cam is None or cam.type != "CAMERA":
        cam = bpy.data.objects.new(name, data)
    cam.data = data
    if cam.name not in bpy.context.scene.collection.all_objects:
        bpy.context.scene.collection.objects.link(cam)

    tan = math.tan(data.angle / 2) / margin
    size = float((hi - lo).max())
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2

    def distance():
        return max(float((local[:, 2] + np.abs(local[:, 0] - cx) / tan).max()),
                   float((local[:, 2] + np.abs(local[:, 1] - cy) / tan).max()), hi[2] + size * 0.5)
    for _ in range(4):        # centre what the camera sees (perspective pulls near things outwards), then fit again
        depth = distance() - local[:, 2]
        sx, sy = (local[:, 0] - cx) / depth, (local[:, 1] - cy) / depth
        cx += (sx.min() + sx.max()) / 2 * float(np.median(depth))
        cy += (sy.min() + sy.max()) / 2 * float(np.median(depth))
    d = distance()
    rotation = Matrix((x_axis, up, toward)).transposed().to_4x4()
    cam.matrix_world = Matrix.Translation(x_axis * cx + up * cy + toward * d) @ rotation
    data.clip_start = max((d - hi[2]) * 0.5, 1e-4)
    data.clip_end = (d - lo[2]) * 2
    return cam


def frame_camera(armature, frames, upper_body=False):
    """Put the pose camera in front of the character with every vertex of the frames in view. Returns it."""
    front, left, up = character_axes(armature)
    points = body_points(armature, frames, upper_body)
    if not len(points):
        return None
    return place_camera(CAMERA_NAME, points, left, up, front)


# --- face board poses ---

def face_board_of(armature):
    """The face board: an armature called *_face_gui / *_face_board, or one with 10+ CTRL_ bones."""
    for o in bpy.context.scene.objects:
        if o.type == "ARMATURE" and o is not armature and (o.name.endswith(("_face_gui", "_face_board"))
                                                          or sum(1 for b in o.data.bones if b.name.startswith("CTRL_")) >= 10):
            return o
    return None


def board_controls(board) -> list:
    """The face board's controls (CTRL_ bones, not the board's frame), plus any other bone its animation moves."""
    import re
    names = {b.name for b in board.pose.bones if b.name.startswith("CTRL_") and "GUI" not in b.name}
    ad = board.animation_data
    actions = ([ad.action] if ad and ad.action else []) + \
        ([s.action for t in ad.nla_tracks for s in t.strips if s.action] if ad else [])
    for act in actions:
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        m = re.match(r'pose\.bones\["([^"]+)"\]', fc.data_path)
                        if m and m.group(1) in board.pose.bones:
                            names.add(m.group(1))
    return [pb for pb in board.pose.bones if pb.name in names]


def face_meshes(armature) -> list:
    """The visible meshes of the face (deformed by a skeleton with FACIAL_ bones), else the character's meshes."""
    faces = {o for o in bpy.context.scene.objects
             if o.type == "ARMATURE" and any(b.name.startswith("FACIAL_") for b in o.data.bones)}
    found = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()
             and ({m.object for m in o.modifiers if m.type == "ARMATURE"} | {o.parent}) & faces]
    return found or character_objects(armature)


def face_points(armature):
    """The face meshes' vertices on the current frame, from the neck up."""
    import numpy as np
    depsgraph = bpy.context.evaluated_depsgraph_get()
    chunks = []
    for obj in face_meshes(armature):
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        try:
            co = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
            mesh.vertices.foreach_get("co", co)
        finally:
            ev.to_mesh_clear()
        mw = np.array(ev.matrix_world, dtype=np.float64)
        chunks.append(co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])
    if not chunks:
        return np.zeros((0, 3))
    pts = np.concatenate(chunks)
    neck = next((armature.pose.bones[n] for n in NECK_BONES if n in armature.pose.bones), None)
    if neck is not None:
        cut = (armature.matrix_world @ neck.head).z
        if (pts[:, 2] >= cut).sum() > 10:
            pts = pts[pts[:, 2] >= cut]
    return pts


def frame_face(armature, view="FRONT"):
    """Put the face camera in front of the face (FRONT) or at its LEFT / RIGHT side, on the current frame."""
    pts = face_points(armature)
    if not len(pts):
        return None
    front, left, up = character_axes(armature)
    if view == "LEFT":
        return place_camera(FACE_CAMERA_NAME, pts, -front, up, left, FACE_MARGIN)
    if view == "RIGHT":
        return place_camera(FACE_CAMERA_NAME, pts, front, up, -left, FACE_MARGIN)
    return place_camera(FACE_CAMERA_NAME, pts, left, up, front, FACE_MARGIN)


def render_thumbnail(camera, show, size=THUMB_SIZE):
    """A small Workbench render through camera with only the objects in show; ((w, h), RGBA floats) or None."""
    import tempfile
    import numpy as np
    scene = bpy.context.scene
    r, shading, img = scene.render, scene.display.shading, scene.render.image_settings
    saved = {"camera": scene.camera, "engine": r.engine, "x": r.resolution_x, "y": r.resolution_y,
             "pct": r.resolution_percentage, "film": r.film_transparent, "fmt": img.file_format,
             "mode": img.color_mode, "color": shading.color_type, "light": shading.light}
    hidden = []
    for obj in scene.objects:
        if obj not in show and obj.type not in ("CAMERA", "LIGHT") and not obj.hide_render:
            obj.hide_render = True
            hidden.append(obj)
    path = os.path.join(tempfile.gettempdir(), f"sgm_thumb_{os.getpid()}.png")
    try:
        scene.camera = camera
        r.engine = "BLENDER_WORKBENCH"
        r.resolution_x = r.resolution_y = size
        r.resolution_percentage = 100
        r.film_transparent = True
        img.file_format, img.color_mode = "PNG", "RGBA"
        shading.color_type, shading.light = "MATERIAL", "STUDIO"
        bpy.ops.render.render(write_still=False)
        bpy.data.images["Render Result"].save_render(path)
        image = bpy.data.images.load(path, check_existing=False)
        try:
            w, h = image.size
            px = np.empty(w * h * 4, dtype=np.float32)
            image.pixels.foreach_get(px)
        finally:
            bpy.data.images.remove(image)
        return (w, h), px
    except Exception as e:
        print(f"Warning: no thumbnail ({e})")
        return None
    finally:
        scene.camera = saved["camera"]
        r.engine, r.resolution_x, r.resolution_y = saved["engine"], saved["x"], saved["y"]
        r.resolution_percentage, r.film_transparent = saved["pct"], saved["film"]
        img.file_format, img.color_mode = saved["fmt"], saved["mode"]
        shading.color_type, shading.light = saved["color"], saved["light"]
        for obj in hidden:
            obj.hide_render = False
        if os.path.isfile(path):
            os.remove(path)


def pose_action(board, bones, name):
    """An action with the bones' pose on frame 1, for the board (what a pose asset holds)."""
    action = bpy.data.actions.new(name)
    slot = action.slots.new(id_type="OBJECT", name=board.name)
    strip = action.layers.new("Layer").strips.new(type="KEYFRAME")
    bag = strip.channelbag(slot, ensure=True)
    for pb in bones:
        channels = [("location", pb.location)]
        if not all(pb.lock_rotation) or (pb.lock_rotations_4d and not pb.lock_rotation_w):
            channels.append({"QUATERNION": ("rotation_quaternion", pb.rotation_quaternion),
                             "AXIS_ANGLE": ("rotation_axis_angle", pb.rotation_axis_angle)}
                            .get(pb.rotation_mode, ("rotation_euler", pb.rotation_euler)))
        if not all(pb.lock_scale):
            channels.append(("scale", pb.scale))
        for prop, values in channels:
            for i, v in enumerate(values):
                fc = bag.fcurves.new(f'pose.bones["{pb.name}"].{prop}', index=i, group_name=pb.name)
                fc.keyframe_points.insert(1, float(v), options={"FAST"})
    return action


def library_folder(reference):
    """The folder of the asset library called reference, or None for the current file (LOCAL)."""
    if reference in (None, "", "LOCAL"):
        return None
    lib = bpy.context.preferences.filepaths.asset_libraries.get(reference)
    return bpy.path.abspath(lib.path) if lib is not None else None


def store_asset(action, reference):
    """Keep the pose asset in this file (LOCAL) or write it to the library's Saved\\Actions folder as Blender
    does. Returns where it went."""
    folder = library_folder(reference)
    if folder is None:
        action.use_fake_user = True
        return "this file"
    target = os.path.join(folder, "Saved", "Actions")
    os.makedirs(target, exist_ok=True)
    safe = "".join("_" if c in '<>:"/\\|?*' else c for c in action.name)
    path = os.path.join(target, f"{safe}.asset.blend")
    bpy.data.libraries.write(path, {action}, path_remap="NONE", fake_user=True)
    bpy.data.actions.remove(action)
    return path


class ThumbnailSetup:
    """The pose camera made the scene's camera, everything but the character hidden; all put back by restore()
    (straight away when there is no window, else once Blender's thumbnail jobs have finished)."""

    def __init__(self, armature, frames, framing="WHOLE_BODY", isolate=True):
        self.scene = bpy.context.scene
        self.old_camera = self.scene.camera
        self.hidden = []
        self.camera = None
        if framing in ("WHOLE_BODY", "UPPER_BODY"):
            self.camera = frame_camera(armature, frames, framing == "UPPER_BODY")
            if self.camera is not None:
                self.scene.camera = self.camera
                print(f"Thumbnail camera '{self.camera.name}': {framing.replace('_', ' ').lower()} "
                      f"of {len(frames)} pose(s)")
        elif self.scene.camera is None:
            print("Warning: the scene has no camera, so Blender makes no thumbnails (use the whole-body camera)")
        if isolate:
            keep = set(character_objects(armature)) | {armature}
            keep |= {o for o in self.scene.objects if follows(o, armature)}
            for obj in self.scene.objects:
                if obj in keep or obj.type in ("CAMERA", "LIGHT") or not obj.visible_get():
                    continue
                try:
                    obj.hide_set(True)
                    self.hidden.append(obj.name)
                except RuntimeError:
                    pass
            if self.hidden:
                print(f"Hidden while the thumbnails are drawn: {', '.join(self.hidden[:8])}"
                      + (" ..." if len(self.hidden) > 8 else ""))

    def put_back(self):
        try:                                       # (the camera or the old one may have been deleted since)
            if self.camera is not None and self.scene.camera == self.camera:
                old = self.old_camera
                self.scene.camera = old if old is not None and old.name in bpy.data.objects else None
        except ReferenceError:
            pass
        for name in self.hidden:
            obj = bpy.data.objects.get(name)
            if obj is not None and name in bpy.context.view_layer.objects:
                obj.hide_set(False)
        self.hidden = []

    def restore(self):
        if bpy.app.background or not hasattr(bpy.app, "timers"):
            self.put_back()
            return
        state = {"waited": 0.0, "quiet": 0}

        def check():
            state["waited"] += 0.5
            try:
                busy = bpy.app.is_job_running("RENDER_PREVIEW")
            except (AttributeError, TypeError, ValueError):
                busy = False
            state["quiet"] = 0 if busy else state["quiet"] + 1
            if (state["quiet"] >= 3 and state["waited"] >= 1.5) or state["waited"] > 120:
                try:
                    self.put_back()
                except ReferenceError:
                    pass
                return None
            return 0.5
        bpy.app.timers.register(check, first_interval=0.5)


class PoseMagicProcessor:
    """Main processor class for pose magic operations"""

    def __init__(self,
                 armature_name: Optional[str] = None,
                 max_poses: int = 50,
                 export_json: bool = True,
                 export_csv: bool = True,
                 export_txt: bool = True,
                 output_dir: str = None,
                 rig_type: str = None,
                 asset_library_reference: str = 'LOCAL',
                 match_fk_to_ik: bool = True,
                 pose_prefix: Optional[str] = None,
                 thumbnail: str = "WHOLE_BODY",
                 thumbnail_isolate: bool = True,
                 face_poses: bool = False,
                 face_view: str = "FRONT"):

        self.face_poses = face_poses
        self.face_view = face_view
        self.thumbnail = thumbnail
        self.thumbnail_isolate = thumbnail_isolate
        self.pose_prefix = (pose_prefix or "").strip() or None
        self.armature_name = armature_name
        self.max_poses = max_poses
        self.export_json = export_json
        self.export_csv = export_csv
        self.export_txt = export_txt
        self.rig_type = rig_type or None
        self.asset_library_reference = asset_library_reference
        self.match_fk_to_ik = match_fk_to_ik
        self.output_dir = output_dir or bpy.path.abspath("//")
        self.file_info = self._parse_file_info()
        self.today = self._get_today_string()

        armature = self.get_armature()
        if is_metahuman_rig(armature):
            self.bone_names = metahuman_fk_bones(armature)
        elif self.asset_library_reference == 'Galtis':
            self.bone_names = list(GALTIS_BONES)
        elif armature:
            self.bone_names = [bone.name for bone in armature.pose.bones]
        else:
            self.bone_names = []
            print(f"Warning: Armature '{self.armature_name}' not found. Bone list is empty.")

    def _parse_file_info(self) -> Dict[str, str]:
        """The motion's name from the .blend: 'SG ASL Hello 2026-10-12 Working.blend' -> 'SG ASL Hello 2026-10-12'
        (the last word dropped); a name without spaces ('Hello_tk1_5.blend') is used whole."""
        if not bpy.data.is_saved:
            return {'name': 'Unsaved', 'stamp': 'Unsaved', 'old_stamp': 'Unsaved'}
        stem = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
        words = stem.split()
        stamp = " ".join(words[:-1]) if len(words) > 1 else stem
        name = " ".join(words[2:-2]) if len(words) > 4 else (" ".join(words[2:-1]) if len(words) == 4 else stamp)
        old_stamp = stamp
        if self.rig_type:
            stamp = stamp + " " + self.rig_type
        return {'name': name, 'stamp': stamp, 'old_stamp': old_stamp}

    def _get_today_string(self) -> str:
        current_time = datetime.datetime.now()
        return f"{current_time.year}-{current_time.month}-{current_time.day}"

    def get_sorted_markers(self) -> List:
        return sorted(bpy.context.scene.timeline_markers, key=lambda marker: marker.frame)

    def get_armature(self) -> Optional[bpy.types.Object]:
        """The armature named armature_name; without a name, the MetaHuman rig, else 'root' (Galtis)."""
        if self.armature_name:
            armature = bpy.data.objects.get(self.armature_name)
        else:
            armature = next((o for o in bpy.context.scene.objects if is_metahuman_rig(o)), None) \
                or bpy.data.objects.get("root")
        if not armature or armature.type != 'ARMATURE':
            print(f"Armature '{self.armature_name or 'MetaHuman rig / root'}' not found or is not an armature")
            return None
        return armature

    def frame_budget(self) -> int:
        current_frame = bpy.context.scene.frame_current
        previous = [m for m in bpy.context.scene.timeline_markers if m.frame < current_frame]
        return current_frame - max(previous, key=lambda m: m.frame).frame if previous else current_frame

    def export_json_data(self, pose_name: str) -> bool:
        """Export armature data as JSON compatible with Jason Pose Manager"""
        armature = self.get_armature()
        if not armature:
            return False
        pose_name_cleaned = pose_name.replace("(", "").replace(")", "")
        armature_data = {"addon": "jpm", "name": pose_name_cleaned, "def_limbs": [None] * 8, "bones": []}
        bones = armature.pose.bones
        if is_metahuman_rig(armature):
            bones = [armature.pose.bones[n] for n in metahuman_controls(armature)]
        for bone in bones:
            armature_data["bones"].append({
                "name": bone.name,
                "location": {"vector": list(bone.location)},
                "rotation": {"vector": list(as_quaternion(bone)), "mode": "QUATERNION"},
                "scale": {"vector": list(bone.scale)},
            })
        filepath = os.path.join(self.output_dir, f"jpm_{pose_name_cleaned.replace(' ', '_')}.json")
        try:
            with open(filepath, "w") as outfile:
                json.dump([armature_data], outfile, indent=2)
            print(f"Successfully exported JSON to: {filepath}")
            return True
        except Exception as e:
            print(f"Error exporting JSON to {filepath}: {e}")
            return False

    def selected_bones(self, armature):
        return [armature.pose.bones[bn] for bn in self.bone_names if bn in armature.pose.bones]

    def export_csv_data(self, pose_name: str) -> bool:
        """Export bone rotation data as CSV file"""
        armature = self.get_armature()
        if not armature:
            return False
        pose_name_cleaned = pose_name.replace("(", "").replace(")", "")
        bones = self.selected_bones(armature)
        if not bones:
            print("No target bones found for export")
            return False
        filepath = os.path.join(self.output_dir, f"{pose_name_cleaned}.csv")
        try:
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["motion_name", self.file_info['stamp']])
                writer.writerow(["pose_name", pose_name_cleaned])
                writer.writerow(["export_date", self.today])
                writer.writerow(["current_frame", bpy.context.scene.frame_current])
                writer.writerow(["frame_budget", self.frame_budget()])
                writer.writerow([])
                writer.writerow(["bone_name", "w", "x", "y", "z"])
                for bone in bones:
                    rot = as_quaternion(bone)
                    writer.writerow([bone.name, round(rot.w, 4), round(rot.x, 4), round(rot.y, 4), round(rot.z, 4)])
            print(f"Successfully exported CSV to: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing CSV data to {filepath}: {e}")
            return False

    def export_txt_data(self, pose_name: str) -> bool:
        """Export bone rotation data as a Python-style dictionary in a TXT file"""
        armature = self.get_armature()
        if not armature:
            return False
        pose_name_cleaned = pose_name.replace("(", "").replace(")", "")
        filepath = os.path.join(self.output_dir, f"{pose_name_cleaned}.txt")
        try:
            with open(filepath, 'w') as f:
                f.write(f"Motion Name: {self.file_info['stamp']}\n")
                f.write(f"Pose Name: {pose_name_cleaned}\n")
                f.write(f"Export Date: {self.today}\n")
                f.write(f"Current Frame: {bpy.context.scene.frame_current}\n")
                f.write(f"Frame Budget: {self.frame_budget()}\n")
                f.write("bone_rotations = {\n")
                for bone in self.selected_bones(armature):
                    rot = as_quaternion(bone)
                    note = "" if bone.rotation_mode == 'QUATERNION' else f"  # converted from {bone.rotation_mode}"
                    f.write(f'    "{bone.name}": ({rot.w:.4f}, {rot.x:.4f}, {rot.y:.4f}, {rot.z:.4f}),{note}\n')
                f.write("}\n")
            print(f"Successfully exported TXT data to: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing TXT data to {filepath}: {e}")
            return False

    def create_pose_asset(self, pose_name: str) -> bool:
        armature = self.get_armature()
        if not armature:
            return False
        bpy.context.view_layer.objects.active = armature
        if bpy.context.object.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        if is_metahuman_rig(armature):                 # the controls only
            wanted = set(metahuman_controls(armature))
            for pb in armature.pose.bones:
                sel = pb.name in wanted
                if hasattr(pb, "select"):
                    pb.select = sel
                else:
                    pb.bone.select = sel
        else:
            bpy.ops.pose.select_all(action='SELECT')
        try:
            with bpy.context.temp_override(**view3d_override()):
                bpy.ops.poselib.create_pose_asset(pose_name=pose_name,
                                                  asset_library_reference=self.asset_library_reference,
                                                  catalog_path="")
            action = bpy.data.actions.get(pose_name)
            if action is not None and action.asset_data is not None:
                action.asset_data.author = AUTHOR
                action.asset_data.description = str(bpy.context.scene.frame_current)
                action.asset_data.copyright = "CC0"
            print(f"Successfully created pose asset: {pose_name}")
            return True
        except Exception as e:
            print(f"Error creating pose asset '{pose_name}': {e}")
            return False

    def process(self) -> Tuple[int, int]:
        """A pose for each timeline marker (up to max_poses)."""
        sorted_markers = self.get_sorted_markers()
        if not sorted_markers:
            print("No timeline markers found")
            return 0, 0
        armature = self.get_armature()
        if armature and armature.data and hasattr(armature.data, 'collections_all'):
            for collection in armature.data.collections_all.values():
                collection.is_solo = False
        successful_exports = total_attempts = 0
        if armature is not None and self.face_poses:
            self.make_face_poses(armature, sorted_markers[:self.max_poses])
        thumbs = None
        if armature is not None:
            thumbs = ThumbnailSetup(armature, [m.frame for m in sorted_markers[:self.max_poses]],
                                    self.thumbnail, self.thumbnail_isolate)
        try:
            successful_exports, total_attempts = self._each_marker(sorted_markers, armature)
        finally:
            if thumbs is not None:
                thumbs.restore()
        bpy.context.scene.frame_set(sorted_markers[0].frame)   # put the animation back on a keyed frame
        return successful_exports, total_attempts

    def make_face_poses(self, armature, markers) -> int:
        """A face board pose asset for each marker, with a picture of the face as its thumbnail."""
        board = face_board_of(armature)
        if board is None:
            print("Face poses: no face board (*_face_gui) in this scene; none made")
            return 0
        bones = board_controls(board)
        if not bones:
            print(f"Face poses: '{board.name}' has no CTRL_ controls; none made")
            return 0
        show = set(face_meshes(armature)) | set(character_objects(armature))
        self.face_done = 0
        for i, marker in enumerate(markers):
            bpy.context.scene.frame_set(marker.frame)
            name = f"{self.pose_prefix or self.file_info['stamp']} Face P{i + 1}"
            old = bpy.data.actions.get(name)
            if old is not None and old.users == (1 if old.use_fake_user else 0):
                bpy.data.actions.remove(old)               # made by an earlier run
            try:
                action = pose_action(board, bones, name)
                action.asset_mark()
                action.asset_data.author = AUTHOR
                action.asset_data.description = f"Face board, frame {marker.frame}"
                action.asset_data.copyright = "CC0"
                camera = frame_face(armature, self.face_view)
                picture = render_thumbnail(camera, show) if camera is not None else None
                if picture is not None:
                    preview = action.preview_ensure()
                    preview.image_size = picture[0]
                    preview.image_pixels_float.foreach_set(picture[1])
                where = store_asset(action, self.asset_library_reference)
                self.face_done += 1
                print(f"Face pose {i + 1}/{len(markers)}: {marker.name} (frame {marker.frame}) -> {name} "
                      f"({len(bones)} controls{'' if picture else ', no thumbnail'}; {where})")
            except Exception as e:
                print(f"Error creating face pose '{name}': {e}")
        return self.face_done

    def _each_marker(self, sorted_markers, armature) -> Tuple[int, int]:
        successful_exports = total_attempts = 0
        for i, marker in enumerate(sorted_markers[:self.max_poses]):
            total_attempts += 1
            bpy.context.scene.frame_set(marker.frame)
            if armature and is_metahuman_rig(armature) and self.match_fk_to_ik:
                fk_from_ik(armature)                    # FK shows the IK pose on this frame (nothing keyed)
            pose_name = f"{self.pose_prefix or self.file_info['stamp']} P{i + 1}"
            print(f"Processing marker {i + 1}/{min(len(sorted_markers), self.max_poses)}: {marker.name} "
                  f"(frame {marker.frame}) -> {pose_name}")
            if self.create_pose_asset(pose_name):
                ok = True
                if self.export_json and not self.export_json_data(pose_name):
                    ok = False
                if self.export_csv and not self.export_csv_data(pose_name):
                    ok = False
                if self.export_txt and not self.export_txt_data(pose_name):
                    ok = False
                if ok:
                    successful_exports += 1
        return successful_exports, total_attempts


def default_pose_prefix(rig_type: Optional[str] = None) -> str:
    """What the poses are called without a pose_prefix: the .blend's name without its last word."""
    if not bpy.data.is_saved:
        return "Unsaved"
    stem = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
    words = stem.split()
    stamp = " ".join(words[:-1]) if len(words) > 1 else stem
    return f"{stamp} {rig_type}" if rig_type else stamp


def run_pose_magic(armature_name: Optional[str] = None,
                   max_poses: int = 50,
                   export_json: bool = True,
                   export_csv: bool = True,
                   export_txt: bool = True,
                   output_dir: str = None,
                   rig_type: str = None,
                   asset_library_reference: str = 'LOCAL',
                   match_fk_to_ik: bool = True,
                   pose_prefix: Optional[str] = None,
                   thumbnail: str = "WHOLE_BODY",
                   thumbnail_isolate: bool = True,
                   face_poses: bool = False,
                   face_view: str = "FRONT") -> Tuple[int, int]:
    """Run Pose Magic. Returns (poses done, markers tried). The poses are called '<pose_prefix> P1', P2 ...;
    without a pose_prefix, '<the .blend's name without its last word>[ <rig_type>] P1' as before.
    thumbnail: "WHOLE_BODY" / "UPPER_BODY" (Pose Magic's camera frames the character) or "SCENE" (the scene's camera).
    face_poses: also a face board pose for each marker ('<pose_prefix> Face P1' ...), its thumbnail taken from
    face_view: "FRONT", "LEFT" or "RIGHT" of the face. (The returned counts are the body poses.)"""
    if not bpy.data.is_saved and output_dir is None:
        print("ERROR: Blend file is not saved and no output_dir provided.")
        return 0, 0
    processor = PoseMagicProcessor(armature_name=armature_name, max_poses=max_poses, export_json=export_json,
                                   export_csv=export_csv, export_txt=export_txt, output_dir=output_dir,
                                   rig_type=rig_type, asset_library_reference=asset_library_reference,
                                   match_fk_to_ik=match_fk_to_ik, pose_prefix=pose_prefix,
                                   thumbnail=thumbnail, thumbnail_isolate=thumbnail_isolate,
                                   face_poses=face_poses, face_view=face_view)
    try:
        successful, total = processor.process()
        print("-" * 30)
        print(f"Pose Magic Finished: {successful}/{total} poses processed successfully."
              + (f" Face poses: {getattr(processor, 'face_done', 0)}/{total}." if face_poses else ""))
        print("-" * 30)
        return successful, total
    except Exception as e:
        print(f"Pose Magic Critical Error: {e}")
        return 0, 0


if __name__ == "__main__":
    run_pose_magic()
