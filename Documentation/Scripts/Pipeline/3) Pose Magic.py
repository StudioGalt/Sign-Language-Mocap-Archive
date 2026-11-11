import sys
import bpy
import importlib
import os

# Using Blender 5.1.0
# Last tested March 18,  2025 
blend_file_dir = os.path.dirname(bpy.data.filepath)

if "Reincarnation" in blend_file_dir:
    # Parent's parent directory
    parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
else:
    # One parent directory
    parent_dir = os.path.dirname(blend_file_dir)


script_path = parent_dir + "//Scripts//" 
if script_path not in sys.path:
    sys.path.append(script_path)


import pose_magic_lib

importlib.reload(pose_magic_lib)

  
pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=True,
    export_csv=True,
    export_txt=True,
    output_dir=None,
    rig_type=None,
    asset_library_reference='Galtis'
)

