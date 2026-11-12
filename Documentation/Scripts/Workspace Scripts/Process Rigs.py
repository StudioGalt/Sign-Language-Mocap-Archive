import bpy
import os
import sys
import importlib


# Using Blender 5.1.1
# Last tested May 26,  2026


def process_rigify_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_rigify = {
        "upper_arm.L": 25.5032, "forearm.L": 20.6275, "hand.L": 10.0394,
        "upper_arm.R": 25.5032, "forearm.R": 20.6275, "hand.R": 10.0394
    }

    bone_lengths_galtis_normal = {
        "clavicle_r": 14.2605, "upperarminte_R": 25.4394, "lowerarminte_R": 20.6275,
        "handinte_R": 10.0016, "clavicle_l": 14.2605, "upperarminte_L": 25.4394,
        "lowerarminte_L": 20.6275, "handinte_L": 10.0016,
    }

    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    # --- 4. Rigify Generation and Scaling ---
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.scale = (100, 100, 100)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    scene.unit_settings.scale_length = 0.01

    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    metarig.select_set(True)
    bpy.context.view_layer.objects.active = metarig
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_rigify.items():
        util_scripts.set_bone_length(metarig.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_rigify_world.items():
        if src_bone in metarig.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(metarig.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in metarig.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    rigify_fbx_name = f"{stamp} Rigify TPose.fbx"
    rigify_path = os.path.join(blend_file_dir, rigify_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Rigify TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
        armature_name="metarig", max_poses=50, export_txt=True, rig_type="metarig T", asset_library_reference='metarig_T'
    )

    scene.frame_set(0)
    bpy.ops.export_scene.fbx(filepath=rigify_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Remove Rigify Actions
    for act in [a for a in bpy.data.actions if "Rigify" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "metarig" in bpy.data.objects:
        obj_meta = bpy.data.objects["metarig"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "metarig" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["metarig"])

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis_normal.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_rigify_T()


def process_rigify_A():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_rigify = {
        "upper_arm.L": 25.5032, "forearm.L": 20.6275, "hand.L": 10.0394,
        "upper_arm.R": 25.5032, "forearm.R": 20.6275, "hand.R": 10.0394
    }

    bone_lengths_galtis_normal = {
        "clavicle_r": 14.2605, "upperarminte_R": 25.4394, "lowerarminte_R": 20.6275,
        "handinte_R": 10.0016, "clavicle_l": 14.2605, "upperarminte_L": 25.4394,
        "lowerarminte_L": 20.6275, "handinte_L": 10.0016,
    }

    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    # --- 4. Rigify Generation and Scaling ---
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.scale = (100, 100, 100)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    scene.unit_settings.scale_length = 0.01

    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    metarig.select_set(True)
    bpy.context.view_layer.objects.active = metarig
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_rigify.items():
        util_scripts.set_bone_length(metarig.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_rigify_world.items():
        if src_bone in metarig.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(metarig.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in metarig.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    rigify_fbx_name = f"{stamp} Rigify APose.fbx"
    rigify_path = os.path.join(blend_file_dir, rigify_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Rigify AP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
        armature_name="metarig", max_poses=50, export_txt=True, rig_type="metarig A", asset_library_reference='metarig_A'
    )

    scene.frame_set(0)
    bpy.ops.export_scene.fbx(filepath=rigify_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Remove Rigify Actions
    for act in [a for a in bpy.data.actions if "Rigify" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "metarig" in bpy.data.objects:
        obj_meta = bpy.data.objects["metarig"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "metarig" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["metarig"])

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis_normal.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_rigify_A()


def process_manny_A():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_manny = {
    # Torso and Head
    "pelvis": 8.056781, "spine_01": 6.795059, "spine_02": 7.238230, 
    "spine_03": 8.523896, "spine_04": 19.439806, "spine_05": 7.861110, 
    "neck_01": 5.110263, "neck_02": 4.912973, "head": 4.912974,

    # Left Arm and Hand
    "clavicle_l": 17.809526, "upperarm_l": 18.514095, "lowerarm_l": 18.167385, 
    "lowerarm_twist_02_l": 18.167385, "lowerarm_twist_01_l": 18.167385, "hand_l": 3.777156, 
    "index_metacarpal_l": 5.882194, "index_01_l": 4.080000, "index_02_l": 2.595001, "index_03_l": 2.594999, 
    "middle_metacarpal_l": 6.098213, "middle_01_l": 5.169003, "middle_02_l": 2.473998, "middle_03_l": 2.474003, 
    "thumb_01_l": 4.378003, "thumb_02_l": 3.086003, "thumb_03_l": 3.086001, 
    "pinky_metacarpal_l": 4.963617, "pinky_01_l": 3.815999, "pinky_02_l": 2.039999, "pinky_03_l": 2.040001, 
    "ring_metacarpal_l": 5.645708, "ring_01_l": 4.976998, "ring_02_l": 2.265001, "ring_03_l": 2.265001, 
    "upperarm_twist_01_l": 18.514093, "upperarm_twist_02_l": 18.514093,

    # Right Arm and Hand
    "clavicle_r": 17.809631, "upperarm_r": 18.513802, "lowerarm_r": 18.167311, 
    "lowerarm_twist_02_r": 18.167311, "lowerarm_twist_01_r": 18.167311, "hand_r": 3.777258, 
    "pinky_metacarpal_r": 4.963354, "pinky_01_r": 3.816031, "pinky_02_r": 2.039994, "pinky_03_r": 2.039996, 
    "ring_metacarpal_r": 5.645902, "ring_01_r": 4.977061, "ring_02_r": 2.264971, "ring_03_r": 2.264969, 
    "middle_metacarpal_r": 6.098363, "middle_01_r": 5.168988, "middle_02_r": 2.474043, "middle_03_r": 2.474042, 
    "index_metacarpal_r": 5.882305, "index_01_r": 4.079931, "index_02_r": 2.595074, "index_03_r": 2.595076, 
    "thumb_01_r": 4.377820, "thumb_02_r": 3.085947, "thumb_03_r": 3.085947, 
    "upperarm_twist_01_r": 18.513792, "upperarm_twist_02_r": 18.513796,

    # Legs
    "thigh_r": 28.894186, "calf_r": 28.145353, "foot_r": 16.781149, "ball_r": 16.781139, 
    "calf_twist_02_r": 28.145351, "calf_twist_01_r": 28.145348, "thigh_twist_01_r": 28.894178, "thigh_twist_02_r": 28.894182, 
    "thigh_l": 28.894217, "calf_l": 28.145319, "foot_l": 16.781149, "ball_l": 16.781145, 
    "calf_twist_02_l": 28.145323, "calf_twist_01_l": 28.145323, "thigh_twist_01_l": 28.894211, "thigh_twist_02_l": 28.894215,

    # IK and Special
    "ik_foot_root": 16.349424, "ik_foot_l": 16.349424, "ik_foot_r": 16.349424, 
    "ik_hand_root": 115.937485, "ik_hand_gun": 47.768467, "ik_hand_l": 47.768463, "ik_hand_r": 47.768471, 
    "interaction": 1.000000, "center_of_mass": 1.000000
    }

    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Manny=MannequinFolder+"\\"+"SKM_Manny_Simple.FBX"

    bpy.ops.import_scene.fbx(filepath=Manny,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_manny.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_mannequin_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    manny_fbx_name = f"{stamp} Manny APose.fbx"
    manny_path = os.path.join(blend_file_dir, manny_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Manny AP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="Manny A",
    asset_library_reference='Manny_A'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=manny_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Manny Actions
    for act in [a for a in bpy.data.actions if "Manny" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_Manny_Simple"].select_set(True)
    bpy.data.objects["SKM_Manny_Simple.001"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_manny_A()




def process_manny_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_manny = {
    # Torso and Head
    "pelvis": 8.056781, "spine_01": 6.795059, "spine_02": 7.238230, 
    "spine_03": 8.523896, "spine_04": 19.439806, "spine_05": 7.861110, 
    "neck_01": 5.110263, "neck_02": 4.912973, "head": 4.912974,

    # Left Arm and Hand
    "clavicle_l": 17.809526, "upperarm_l": 18.514095, "lowerarm_l": 18.167385, 
    "lowerarm_twist_02_l": 18.167385, "lowerarm_twist_01_l": 18.167385, "hand_l": 3.777156, 
    "index_metacarpal_l": 5.882194, "index_01_l": 4.080000, "index_02_l": 2.595001, "index_03_l": 2.594999, 
    "middle_metacarpal_l": 6.098213, "middle_01_l": 5.169003, "middle_02_l": 2.473998, "middle_03_l": 2.474003, 
    "thumb_01_l": 4.378003, "thumb_02_l": 3.086003, "thumb_03_l": 3.086001, 
    "pinky_metacarpal_l": 4.963617, "pinky_01_l": 3.815999, "pinky_02_l": 2.039999, "pinky_03_l": 2.040001, 
    "ring_metacarpal_l": 5.645708, "ring_01_l": 4.976998, "ring_02_l": 2.265001, "ring_03_l": 2.265001, 
    "upperarm_twist_01_l": 18.514093, "upperarm_twist_02_l": 18.514093,

    # Right Arm and Hand
    "clavicle_r": 17.809631, "upperarm_r": 18.513802, "lowerarm_r": 18.167311, 
    "lowerarm_twist_02_r": 18.167311, "lowerarm_twist_01_r": 18.167311, "hand_r": 3.777258, 
    "pinky_metacarpal_r": 4.963354, "pinky_01_r": 3.816031, "pinky_02_r": 2.039994, "pinky_03_r": 2.039996, 
    "ring_metacarpal_r": 5.645902, "ring_01_r": 4.977061, "ring_02_r": 2.264971, "ring_03_r": 2.264969, 
    "middle_metacarpal_r": 6.098363, "middle_01_r": 5.168988, "middle_02_r": 2.474043, "middle_03_r": 2.474042, 
    "index_metacarpal_r": 5.882305, "index_01_r": 4.079931, "index_02_r": 2.595074, "index_03_r": 2.595076, 
    "thumb_01_r": 4.377820, "thumb_02_r": 3.085947, "thumb_03_r": 3.085947, 
    "upperarm_twist_01_r": 18.513792, "upperarm_twist_02_r": 18.513796,

    # Legs
    "thigh_r": 28.894186, "calf_r": 28.145353, "foot_r": 16.781149, "ball_r": 16.781139, 
    "calf_twist_02_r": 28.145351, "calf_twist_01_r": 28.145348, "thigh_twist_01_r": 28.894178, "thigh_twist_02_r": 28.894182, 
    "thigh_l": 28.894217, "calf_l": 28.145319, "foot_l": 16.781149, "ball_l": 16.781145, 
    "calf_twist_02_l": 28.145323, "calf_twist_01_l": 28.145323, "thigh_twist_01_l": 28.894211, "thigh_twist_02_l": 28.894215,

    # IK and Special
    "ik_foot_root": 16.349424, "ik_foot_l": 16.349424, "ik_foot_r": 16.349424, 
    "ik_hand_root": 115.937485, "ik_hand_gun": 47.768467, "ik_hand_l": 47.768463, "ik_hand_r": 47.768471, 
    "interaction": 1.000000, "center_of_mass": 1.000000
    }

    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Manny=MannequinFolder+"\\"+"SKM_Manny_Simple.FBX"

    bpy.ops.import_scene.fbx(filepath=Manny,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_manny.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_mannequin_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    manny_fbx_name = f"{stamp} Manny TPose.fbx"
    manny_path = os.path.join(blend_file_dir, manny_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Manny TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="Manny T",
    asset_library_reference='Manny_T'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=manny_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Manny Actions
    for act in [a for a in bpy.data.actions if "Manny" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_Manny_Simple"].select_set(True)
    bpy.data.objects["SKM_Manny_Simple.001"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_manny_T()


def process_quinn_A():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_quinn = {
    # Torso and Head
    "pelvis": 8.566345, "spine_01": 4.987514, "spine_02": 7.625883, 
    "spine_03": 8.851114, "spine_04": 17.498758, "spine_05": 7.964658, 
    "neck_01": 5.848839, "neck_02": 5.758487, "head": 5.758487,

    # Left Arm and Hand
    "clavicle_l": 15.286097, "upperarm_l": 18.060240, "lowerarm_l": 17.396780, 
    "lowerarm_twist_02_l": 17.396778, "lowerarm_twist_01_l": 17.396780, "hand_l": 3.531960, 
    "upperarm_twist_01_l": 18.060246, "upperarm_twist_02_l": 18.060247,
    "middle_metacarpal_l": 5.560550, "middle_01_l": 4.919671, "middle_02_l": 2.902053, "middle_03_l": 2.902052,
    "pinky_metacarpal_l": 4.717950, "pinky_01_l": 2.893297, "pinky_02_l": 1.791519, "pinky_03_l": 1.791521,
    "ring_metacarpal_l": 4.992765, "ring_01_l": 4.251389, "ring_02_l": 3.234829, "ring_03_l": 3.234826,
    "thumb_01_l": 4.631789, "thumb_02_l": 2.710590, "thumb_03_l": 2.710591,
    "index_metacarpal_l": 5.376909, "index_01_l": 4.564551, "index_02_l": 2.486471, "index_03_l": 2.486473,

    # Right Arm and Hand
    "clavicle_r": 15.285992, "upperarm_r": 18.059954, "lowerarm_r": 17.397003, 
    "lowerarm_twist_02_r": 17.396999, "lowerarm_twist_01_r": 17.396999, "hand_r": 3.531931, 
    "upperarm_twist_01_r": 18.059954, "upperarm_twist_02_r": 18.059958,
    "middle_metacarpal_r": 5.560617, "middle_01_r": 4.919606, "middle_02_r": 2.902068, "middle_03_r": 2.902071,
    "pinky_metacarpal_r": 4.717987, "pinky_01_r": 2.893318, "pinky_02_r": 1.791474, "pinky_03_r": 1.791472,
    "ring_metacarpal_r": 4.992805, "ring_01_r": 4.251379, "ring_02_r": 3.234728, "ring_03_r": 3.234728,
    "thumb_01_r": 4.631796, "thumb_02_r": 2.710572, "thumb_03_r": 2.710572,
    "index_metacarpal_r": 5.376899, "index_01_r": 4.564569, "index_02_r": 2.486447, "index_03_r": 2.486449,

    # Legs
    "thigh_r": 30.501287, "calf_r": 27.803738, "foot_r": 15.115789, "ball_r": 15.115799,
    "calf_twist_02_r": 27.803732, "calf_twist_01_r": 27.803734, "thigh_twist_01_r": 30.501295, "thigh_twist_02_r": 30.501295,
    "thigh_l": 30.501354, "calf_l": 27.803701, "foot_l": 15.115789, "ball_l": 15.115788,
    "calf_twist_02_l": 27.803703, "calf_twist_01_l": 27.803703, "thigh_twist_01_l": 30.501358, "thigh_twist_02_l": 30.501352,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815487, "ik_foot_r": 16.815489,
    "ik_hand_root": 115.942146, "ik_hand_gun": 45.554955, "ik_hand_l": 45.554958, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Quinn=MannequinFolder+"\\"+"SKM_Quinn_Simple.FBX"

    bpy.ops.import_scene.fbx(filepath=Quinn,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_quinn.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_mannequin_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    quinn_fbx_name = f"{stamp} Quinn APose.fbx"
    quinn_path = os.path.join(blend_file_dir, quinn_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Quinn AP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="Quinn A",
    asset_library_reference='Quinn_A'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=quinn_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Quinn Actions
    for act in [a for a in bpy.data.actions if "Quinn" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_Quinn_Simple"].select_set(True)
    bpy.data.objects["SKM_Quinn_Simple.001"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_quinn_A()
    

def process_quinn_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_quinn = {
    # Torso and Head
    "pelvis": 8.566345, "spine_01": 4.987514, "spine_02": 7.625883, 
    "spine_03": 8.851114, "spine_04": 17.498758, "spine_05": 7.964658, 
    "neck_01": 5.848839, "neck_02": 5.758487, "head": 5.758487,

    # Left Arm and Hand
    "clavicle_l": 15.286097, "upperarm_l": 18.060240, "lowerarm_l": 17.396780, 
    "lowerarm_twist_02_l": 17.396778, "lowerarm_twist_01_l": 17.396780, "hand_l": 3.531960, 
    "upperarm_twist_01_l": 18.060246, "upperarm_twist_02_l": 18.060247,
    "middle_metacarpal_l": 5.560550, "middle_01_l": 4.919671, "middle_02_l": 2.902053, "middle_03_l": 2.902052,
    "pinky_metacarpal_l": 4.717950, "pinky_01_l": 2.893297, "pinky_02_l": 1.791519, "pinky_03_l": 1.791521,
    "ring_metacarpal_l": 4.992765, "ring_01_l": 4.251389, "ring_02_l": 3.234829, "ring_03_l": 3.234826,
    "thumb_01_l": 4.631789, "thumb_02_l": 2.710590, "thumb_03_l": 2.710591,
    "index_metacarpal_l": 5.376909, "index_01_l": 4.564551, "index_02_l": 2.486471, "index_03_l": 2.486473,

    # Right Arm and Hand
    "clavicle_r": 15.285992, "upperarm_r": 18.059954, "lowerarm_r": 17.397003, 
    "lowerarm_twist_02_r": 17.396999, "lowerarm_twist_01_r": 17.396999, "hand_r": 3.531931, 
    "upperarm_twist_01_r": 18.059954, "upperarm_twist_02_r": 18.059958,
    "middle_metacarpal_r": 5.560617, "middle_01_r": 4.919606, "middle_02_r": 2.902068, "middle_03_r": 2.902071,
    "pinky_metacarpal_r": 4.717987, "pinky_01_r": 2.893318, "pinky_02_r": 1.791474, "pinky_03_r": 1.791472,
    "ring_metacarpal_r": 4.992805, "ring_01_r": 4.251379, "ring_02_r": 3.234728, "ring_03_r": 3.234728,
    "thumb_01_r": 4.631796, "thumb_02_r": 2.710572, "thumb_03_r": 2.710572,
    "index_metacarpal_r": 5.376899, "index_01_r": 4.564569, "index_02_r": 2.486447, "index_03_r": 2.486449,

    # Legs
    "thigh_r": 30.501287, "calf_r": 27.803738, "foot_r": 15.115789, "ball_r": 15.115799,
    "calf_twist_02_r": 27.803732, "calf_twist_01_r": 27.803734, "thigh_twist_01_r": 30.501295, "thigh_twist_02_r": 30.501295,
    "thigh_l": 30.501354, "calf_l": 27.803701, "foot_l": 15.115789, "ball_l": 15.115788,
    "calf_twist_02_l": 27.803703, "calf_twist_01_l": 27.803703, "thigh_twist_01_l": 30.501358, "thigh_twist_02_l": 30.501352,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815487, "ik_foot_r": 16.815489,
    "ik_hand_root": 115.942146, "ik_hand_gun": 45.554955, "ik_hand_l": 45.554958, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Quinn=MannequinFolder+"\\"+"SKM_Quinn_Simple.FBX"

    bpy.ops.import_scene.fbx(filepath=Quinn,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_quinn.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_mannequin_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    quinn_fbx_name = f"{stamp} Quinn TPose.fbx"
    quinn_path = os.path.join(blend_file_dir, quinn_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Quinn TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="Quinn T",
    asset_library_reference='Quinn_T'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=quinn_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Quinn Actions
    for act in [a for a in bpy.data.actions if "Quinn" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_Quinn_Simple"].select_set(True)
    bpy.data.objects["SKM_Quinn_Simple.001"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_quinn_T()


def process_metahuman_A():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_metahuman = {
    # Torso and Head
    "pelvis": 7.714468, "spine_01": 6.470849, "spine_02": 7.155190, 
    "spine_03": 8.265511, "spine_04": 13.724074, "spine_05": 12.988820, 
    "neck_01": 5.653063, "neck_02": 5.830815, "head": 5.830813,

    # Left Arm and Twist Bones
    "clavicle_l": 12.416552, "upperarm_l": 13.972830, "lowerarm_l": 13.094187, "hand_l": 2.904648,
    "lowerarm_twist_02_l": 13.094188, "lowerarm_twist_01_l": 13.094189,
    "upperarm_twist_01_l": 0.010001, "upperarm_twist_02_l": 2.660811,

    # Left Hand Fingers
    "thumb_01_l": 3.738714, "thumb_02_l": 1.505848, "thumb_03_l": 0.876300,
    "index_metacarpal_l": 3.765739, "index_01_l": 2.434239, "index_02_l": 1.362287, "index_03_l": 0.554643,
    "middle_metacarpal_l": 4.041406, "middle_01_l": 2.898576, "middle_02_l": 1.559715, "middle_03_l": 0.499454,
    "ring_metacarpal_l": 3.646179, "ring_01_l": 2.592799, "ring_02_l": 1.673844, "ring_03_l": 0.345956,
    "pinky_metacarpal_l": 3.241924, "pinky_01_l": 1.896758, "pinky_02_l": 1.137306, "pinky_03_l": 0.477853,

    # Right Arm and Twist Bones
    "clavicle_r": 12.415775, "upperarm_r": 13.972008, "lowerarm_r": 13.092746, "hand_r": 2.904947,
    "lowerarm_twist_02_r": 13.092745, "lowerarm_twist_01_r": 13.092747,
    "upperarm_twist_01_r": 0.010000, "upperarm_twist_02_r": 2.661113,

    # Right Hand Fingers
    "thumb_01_r": 3.740194, "thumb_02_r": 1.506917, "thumb_03_r": 0.876913,
    "index_metacarpal_r": 3.767571, "index_01_r": 2.435822, "index_02_r": 1.363116, "index_03_r": 0.555099,
    "middle_metacarpal_r": 4.042378, "middle_01_r": 2.900054, "middle_02_r": 1.560977, "middle_03_r": 0.500357,
    "ring_metacarpal_r": 3.647082, "ring_01_r": 2.594290, "ring_02_r": 1.675866, "ring_03_r": 0.346736,
    "pinky_metacarpal_r": 3.242840, "pinky_01_r": 1.897847, "pinky_02_r": 1.137720, "pinky_03_r": 0.477757,

    # Legs and Feet
    "thigh_l": 22.531576, "calf_l": 20.747414, "foot_l": 8.197683, "ball_l": 2.874686,
    "thigh_r": 22.530914, "calf_r": 20.749228, "foot_r": 8.195644, "ball_r": 2.873585,

    # Leg Twist Bones
    "thigh_twist_01_l": 0.010000, "thigh_twist_02_l": 0.010002, "calf_twist_01_l": 20.747416, "calf_twist_02_l": 0.010002,
    "thigh_twist_01_r": 0.009996, "thigh_twist_02_r": 0.009998, "calf_twist_01_r": 20.749229, "calf_twist_02_r": 0.009998
}
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Metahuman=MannequinFolder+"\\"+"SKM_GaltisMH_BodyMesh.FBX"

    bpy.ops.import_scene.fbx(filepath=Metahuman,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_metahuman.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_metahuman_pose.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    metahuman_fbx_name = f"{stamp} Metahuman APose.fbx"
    metahuman_path = os.path.join(blend_file_dir, metahuman_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Metahuman AP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="MetaHuman A",
    asset_library_reference='MetaHuman_A'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=metahuman_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Metahuman Actions
    for act in [a for a in bpy.data.actions if "Metahuman" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_GaltisMH_BodyMesh"].select_set(True)
    bpy.data.objects["SKM_GaltisMH_BodyMesh_LOD0"].select_set(True)
    bpy.data.objects["SKM_GaltisMH_BodyMesh_LOD1"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_metahuman_A()


def process_metahuman_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_metahuman = {
    # Torso and Head
    "pelvis": 7.714468, "spine_01": 6.470849, "spine_02": 7.155190, 
    "spine_03": 8.265511, "spine_04": 13.724074, "spine_05": 12.988820, 
    "neck_01": 5.653063, "neck_02": 5.830815, "head": 5.830813,

    # Left Arm and Twist Bones
    "clavicle_l": 12.416552, "upperarm_l": 13.972830, "lowerarm_l": 13.094187, "hand_l": 2.904648,
    "lowerarm_twist_02_l": 13.094188, "lowerarm_twist_01_l": 13.094189,
    "upperarm_twist_01_l": 0.010001, "upperarm_twist_02_l": 2.660811,

    # Left Hand Fingers
    "thumb_01_l": 3.738714, "thumb_02_l": 1.505848, "thumb_03_l": 0.876300,
    "index_metacarpal_l": 3.765739, "index_01_l": 2.434239, "index_02_l": 1.362287, "index_03_l": 0.554643,
    "middle_metacarpal_l": 4.041406, "middle_01_l": 2.898576, "middle_02_l": 1.559715, "middle_03_l": 0.499454,
    "ring_metacarpal_l": 3.646179, "ring_01_l": 2.592799, "ring_02_l": 1.673844, "ring_03_l": 0.345956,
    "pinky_metacarpal_l": 3.241924, "pinky_01_l": 1.896758, "pinky_02_l": 1.137306, "pinky_03_l": 0.477853,

    # Right Arm and Twist Bones
    "clavicle_r": 12.415775, "upperarm_r": 13.972008, "lowerarm_r": 13.092746, "hand_r": 2.904947,
    "lowerarm_twist_02_r": 13.092745, "lowerarm_twist_01_r": 13.092747,
    "upperarm_twist_01_r": 0.010000, "upperarm_twist_02_r": 2.661113,

    # Right Hand Fingers
    "thumb_01_r": 3.740194, "thumb_02_r": 1.506917, "thumb_03_r": 0.876913,
    "index_metacarpal_r": 3.767571, "index_01_r": 2.435822, "index_02_r": 1.363116, "index_03_r": 0.555099,
    "middle_metacarpal_r": 4.042378, "middle_01_r": 2.900054, "middle_02_r": 1.560977, "middle_03_r": 0.500357,
    "ring_metacarpal_r": 3.647082, "ring_01_r": 2.594290, "ring_02_r": 1.675866, "ring_03_r": 0.346736,
    "pinky_metacarpal_r": 3.242840, "pinky_01_r": 1.897847, "pinky_02_r": 1.137720, "pinky_03_r": 0.477757,

    # Legs and Feet
    "thigh_l": 22.531576, "calf_l": 20.747414, "foot_l": 8.197683, "ball_l": 2.874686,
    "thigh_r": 22.530914, "calf_r": 20.749228, "foot_r": 8.195644, "ball_r": 2.873585,

    # Leg Twist Bones
    "thigh_twist_01_l": 0.010000, "thigh_twist_02_l": 0.010002, "calf_twist_01_l": 20.747416, "calf_twist_02_l": 0.010002,
    "thigh_twist_01_r": 0.009996, "thigh_twist_02_r": 0.009998, "calf_twist_01_r": 20.749229, "calf_twist_02_r": 0.009998
}
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }


    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    Metahuman=MannequinFolder+"\\"+"SKM_GaltisMH_BodyMesh.FBX"

    bpy.ops.import_scene.fbx(filepath=Metahuman,    automatic_bone_orientation=False)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_metahuman.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_metahuman_pose.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    metahuman_fbx_name = f"{stamp} Metahuman TPose.fbx"
    metahuman_path = os.path.join(blend_file_dir, metahuman_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Metahuman TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})

    pose_magic_lib.run_pose_magic(
    armature_name="root",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="MetaHuman T",
    asset_library_reference='MetaHuman_T'
)

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=metahuman_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove Metahuman Actions
    for act in [a for a in bpy.data.actions if "Metahuman" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["SKM_GaltisMH_BodyMesh"].select_set(True)
    bpy.data.objects["SKM_GaltisMH_BodyMesh_LOD0"].select_set(True)
    bpy.data.objects["SKM_GaltisMH_BodyMesh_LOD1"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_metahuman_T()
    



def process_RPM_A():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_RPM = {
    "Hips": 9.6363, "Spine": 9.1474, "Spine1": 12.1621, "Spine2": 12.2613,
    "Neck": 9.0795, "Head": 11.4630, "HeadTop_End": 11.4630,
    "LeftEye": 11.4630, "RightEye": 11.4630,

    # Left Arm and Hand
    "LeftShoulder": 6.5343, "LeftArm": 26.8844, "LeftForeArm": 25.7376, "LeftHand": 2.7093,
    "LeftHandThumb1": 3.4079, "LeftHandThumb2": 3.1169, "LeftHandThumb3": 3.3780, "LeftHandThumb4": 3.3780,
    "LeftHandIndex1": 3.2220, "LeftHandIndex2": 2.8317, "LeftHandIndex3": 2.5589, "LeftHandIndex4": 2.5589,
    "LeftHandMiddle1": 3.8194, "LeftHandMiddle2": 3.2195, "LeftHandMiddle3": 2.4585, "LeftHandMiddle4": 2.4585,
    "LeftHandRing1": 3.0380, "LeftHandRing2": 2.8316, "LeftHandRing3": 2.1251, "LeftHandRing4": 2.1251,
    "LeftHandPinky1": 2.7638, "LeftHandPinky2": 1.7656, "LeftHandPinky3": 1.3381, "LeftHandPinky4": 1.3381,

    # Right Arm and Hand
    "RightShoulder": 6.5343, "RightArm": 26.8844, "RightForeArm": 25.7375, "RightHand": 2.7093,
    "RightHandThumb1": 3.4079, "RightHandThumb2": 3.1169, "RightHandThumb3": 3.3779, "RightHandThumb4": 3.3779,
    "RightHandIndex1": 3.2221, "RightHandIndex2": 2.8316, "RightHandIndex3": 2.5588, "RightHandIndex4": 2.5588,
    "RightHandMiddle1": 3.8194, "RightHandMiddle2": 3.2194, "RightHandMiddle3": 2.4585, "RightHandMiddle4": 2.4585,
    "RightHandRing1": 3.0379, "RightHandRing2": 2.8317, "RightHandRing3": 2.1251, "RightHandRing4": 2.1251,
    "RightHandPinky1": 2.7638, "RightHandPinky2": 1.7656, "RightHandPinky3": 1.3381, "RightHandPinky4": 1.3381,

    # Legs and Feet
    "LeftUpLeg": 44.7509, "LeftLeg": 44.9561, "LeftFoot": 15.6575, "LeftToeBase": 8.3197, "LeftToe_End": 8.3197,
    "RightUpLeg": 44.7509, "RightLeg": 44.9559, "RightFoot": 15.6571, "RightToeBase": 8.3195, "RightToe_End": 8.3196
}
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    RPM=MannequinFolder+"\\"+"GaltisRPM.glb"

    bpy.ops.import_scene.gltf(filepath=RPM, directory=MannequinFolder, files=[{"name":"GaltisRPM.glb", "name":"GaltisRPM.glb"}], loglevel=20)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_RPM.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_RPM_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    RPM_glb_name = f"{stamp} RPM A Pose.glb"
    RPMAPosePath = os.path.join(blend_file_dir, RPM_glb_name)
    RPMAPose=stamp+ " RPM A Pose.glb" 
    RPMAPosePath=blend_file_dir+'\\'+ RPMAPose


    RPMAAnim = stamp + " RPM AP"

    actions = bpy.data.actions
    for action in actions:
        if action.name.endswith("rootAction"):
            action.name = RPMAAnim


    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    bpy.data.objects["Armature"].select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')




    bpy.ops.nla.bake(frame_start=0, frame_end=scene_end, only_selected=False, visual_keying=True, clear_constraints=False, clear_parents=True, use_current_action=True, clean_curves=True, bake_types={'POSE'})



    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')



    bpy.data.objects["EyeLeft"].select_set(True)
    bpy.data.objects["EyeRight"].select_set(True)
    bpy.data.objects["Wolf3D_Body"].select_set(True)
    bpy.data.objects["Wolf3D_Hair"].select_set(True)
    bpy.data.objects["Wolf3D_Head"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Bottom"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Footwear"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Top"].select_set(True)
    bpy.data.objects["Wolf3D_Teeth"].select_set(True)
    bpy.data.objects["Armature"].select_set(True)



    bpy.context.scene.frame_start = 0

    bpy.context.scene.frame_set(0)


    bpy.ops.export_scene.gltf(filepath=RPMAPosePath, check_existing=True, use_selection=True, use_visible=True, export_copyright='CC0', use_mesh_vertices=False, export_cameras=False, export_extras=False, export_yup=True, export_apply=False, export_bake_animation=True, export_merge_animation='ACTION', export_nla_strips_merged_animation_name=stamp, export_reset_pose_bones=False, export_current_frame=True, export_rest_position_armature=True)

    
    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove RPM Actions
    for act in [a for a in bpy.data.actions if "RPM" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["EyeLeft"].select_set(True)
    bpy.data.objects["EyeRight"].select_set(True)
    bpy.data.objects["Wolf3D_Body"].select_set(True)
    bpy.data.objects["Wolf3D_Hair"].select_set(True)
    bpy.data.objects["Wolf3D_Head"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Bottom"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Footwear"].select_set(True)
    bpy.data.objects["Wolf3D_Outfit_Top"].select_set(True)
    bpy.data.objects["Wolf3D_Teeth"].select_set(True)
    bpy.data.objects["Armature"].select_set(True)
    bpy.ops.object.delete(use_global=False)
    

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")
# To run the script:
if __name__ == "__main__":
    process_RPM_A()
    

def process_mixamo_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_mixamo = {
    # Torso and Head
    "pelvis": 8.566345, "spine_01": 4.987514, "spine_02": 7.625883, 
    "spine_03": 8.851114, "spine_04": 17.498758, "spine_05": 7.964658, 
    "neck_01": 5.848839, "neck_02": 5.758487, "head": 5.758487,

    # Left Arm and Hand
    "clavicle_l": 15.286097, "upperarm_l": 18.060240, "lowerarm_l": 17.396780, 
    "lowerarm_twist_02_l": 17.396778, "lowerarm_twist_01_l": 17.396780, "hand_l": 3.531960, 
    "upperarm_twist_01_l": 18.060246, "upperarm_twist_02_l": 18.060247,
    "middle_metacarpal_l": 5.560550, "middle_01_l": 4.919671, "middle_02_l": 2.902053, "middle_03_l": 2.902052,
    "pinky_metacarpal_l": 4.717950, "pinky_01_l": 2.893297, "pinky_02_l": 1.791519, "pinky_03_l": 1.791521,
    "ring_metacarpal_l": 4.992765, "ring_01_l": 4.251389, "ring_02_l": 3.234829, "ring_03_l": 3.234826,
    "thumb_01_l": 4.631789, "thumb_02_l": 2.710590, "thumb_03_l": 2.710591,
    "index_metacarpal_l": 5.376909, "index_01_l": 4.564551, "index_02_l": 2.486471, "index_03_l": 2.486473,

    # Right Arm and Hand
    "clavicle_r": 15.285992, "upperarm_r": 18.059954, "lowerarm_r": 17.397003, 
    "lowerarm_twist_02_r": 17.396999, "lowerarm_twist_01_r": 17.396999, "hand_r": 3.531931, 
    "upperarm_twist_01_r": 18.059954, "upperarm_twist_02_r": 18.059958,
    "middle_metacarpal_r": 5.560617, "middle_01_r": 4.919606, "middle_02_r": 2.902068, "middle_03_r": 2.902071,
    "pinky_metacarpal_r": 4.717987, "pinky_01_r": 2.893318, "pinky_02_r": 1.791474, "pinky_03_r": 1.791472,
    "ring_metacarpal_r": 4.992805, "ring_01_r": 4.251379, "ring_02_r": 3.234728, "ring_03_r": 3.234728,
    "thumb_01_r": 4.631796, "thumb_02_r": 2.710572, "thumb_03_r": 2.710572,
    "index_metacarpal_r": 5.376899, "index_01_r": 4.564569, "index_02_r": 2.486447, "index_03_r": 2.486449,

    # Legs
    "thigh_r": 30.501287, "calf_r": 27.803738, "foot_r": 15.115789, "ball_r": 15.115799,
    "calf_twist_02_r": 27.803732, "calf_twist_01_r": 27.803734, "thigh_twist_01_r": 30.501295, "thigh_twist_02_r": 30.501295,
    "thigh_l": 30.501354, "calf_l": 27.803701, "foot_l": 15.115789, "ball_l": 15.115788,
    "calf_twist_02_l": 27.803703, "calf_twist_01_l": 27.803703, "thigh_twist_01_l": 30.501358, "thigh_twist_02_l": 30.501352,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815487, "ik_foot_r": 16.815489,
    "ik_hand_root": 115.942146, "ik_hand_gun": 45.554955, "ik_hand_l": 45.554958, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    bone_lengths_galtis = {
    # Torso and Head
    "pelvis": 10.288247, "spine_01": 5.482167, "spine_02": 11.154024, 
    "spine_03": 13.500072, "spine_04": 17.498764, "spine_05": 7.964671, 
    "neck_01": 4.737705, "neck_02": 8.020221, "head": 8.020223,

    # Left Arm and Hand
    "clavicle_l": 13.332889, "upperarm_l": 16.167719, "lowerarm_l": 14.613164, 
    "lowerarm_twist_02_l": 14.613163, "lowerarm_twist_01_l": 14.613165, "hand_l": 3.975786, 
    "upperarm_twist_01_l": 16.167721, "upperarm_twist_02_l": 16.167719,
    "middle_metacarpal_l": 6.697494, "middle_01_l": 3.015491, "middle_02_l": 2.201410, "middle_03_l": 2.169034,
    "ring_metacarpal_l": 6.249307, "ring_01_l": 2.352131, "ring_02_l": 2.286490, "ring_03_l": 2.187817,
    "index_metacarpal_l": 6.765007, "index_01_l": 2.821282, "index_02_l": 2.618548, "index_03_l": 2.157521,
    "pinky_metacarpal_l": 6.186306, "pinky_01_l": 1.764283, "pinky_02_l": 1.978351, "pinky_03_l": 2.001472,
    "thumb_01_l": 3.811302, "thumb_02_l": 2.607104, "thumb_03_l": 2.559699,

    # Right Arm and Hand
    "clavicle_r": 13.332792, "upperarm_r": 16.167717, "lowerarm_r": 14.616251, "hand_r": 3.864913,
    "upperarm_twist_01_r": 16.162525, "upperarm_twist_02_r": 16.162525,
    "lowerarm_twist_02_r": 14.616252, "lowerarm_twist_01_r": 14.616250,
    "middle_metacarpal_r": 6.697493, "middle_01_r": 3.015491, "middle_02_r": 2.201409, "middle_03_r": 2.169034,
    "ring_metacarpal_r": 6.249304, "ring_01_r": 2.352130, "ring_02_r": 2.286490, "ring_03_r": 2.187816,
    "index_metacarpal_r": 6.765004, "index_01_r": 2.821281, "index_02_r": 2.618546, "index_03_r": 2.157521,
    "pinky_metacarpal_r": 6.186306, "pinky_01_r": 1.764283, "pinky_02_r": 1.978351, "pinky_03_r": 2.001472,
    "thumb_01_r": 3.811301, "thumb_02_r": 2.607103, "thumb_03_r": 2.559803,

    # Legs
    "thigh_r": 23.767262, "calf_r": 34.117607, "foot_r": 15.504932, "ball_r": 15.504798,
    "thigh_twist_01_r": 23.767262, "thigh_twist_02_r": 23.767262, "calf_twist_01_r": 34.117607, "calf_twist_02_r": 34.117603,
    "thigh_l": 23.767309, "calf_l": 34.117493, "foot_l": 15.504923, "ball_l": 15.504920,
    "thigh_twist_01_l": 23.767309, "thigh_twist_02_l": 23.767309, "calf_twist_01_l": 33.566139, "calf_twist_02_l": 34.117489,

    # IK and Special
    "ik_foot_root": 16.815489, "ik_foot_l": 16.815489, "ik_foot_r": 16.815489,
    "ik_hand_root": 122.781090, "ik_hand_gun": 45.956863, "ik_hand_l": 45.554943, "ik_hand_r": 45.554962,
    "interaction": 1.000000, "center_of_mass": 1.000000
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    mixamo=MannequinFolder+"\\"+"X Bot.fbx"

    bpy.ops.import_scene.fbx(filepath=mixamo, automatic_bone_orientation=False, ignore_leaf_bones=True)
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_mixamo.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_mixamo_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    mixamo_fbx_name = f"{stamp} Mixamo TPose.fbx"
    mixamo_path = os.path.join(blend_file_dir, mixamo_fbx_name)

    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} Mixamo TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})


    pose_magic_lib.run_pose_magic(
    armature_name="Armature",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="Mixamo",
    asset_library_reference='Mixamo'
    )

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=mixamo_path, use_selection=True, object_types={'ARMATURE'}, add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove mixamo Actions
    for act in [a for a in bpy.data.actions if "Mixamo" in a.name]:
        bpy.data.actions.remove(act)
    for act in [a for a in bpy.data.actions if "mixamo" in a.name]:
        bpy.data.actions.remove(act)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["Beta_Joints"].select_set(True)
    bpy.data.objects["Beta_Surface"].select_set(True)
    bpy.data.objects["Armature"].select_set(True)

    bpy.ops.object.delete(use_global=False)
    
    if "Armature.001" in bpy.data.objects:
        obj_meta = bpy.data.objects["Armature.001"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "Armature.001" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["Armature.001"])

    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")

# To run the script:
if __name__ == "__main__":
    process_mixamo_T()
    
    




def process_soma_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return

    # --- 2. Data Definitions ---
    bone_lengths_soma = {
    # Torso and Head
    "Spine1": 0.072061, "Spine2": 0.072626, "Neck1": 0.078721, "Neck2": 0.066593,
    "Head": 0.161695, "HeadEnd": 0.050000,
    # Legs
    "LeftFoot": 0.141328, "RightFoot": 0.141328,
    # Other
    "Root": 0.050000, "Hips": 0.051315, "Chest": 0.263508, "Jaw": 0.050000,
    "LeftEye": 0.050000, "RightEye": 0.050000, "LeftShoulder": 0.157430, "LeftArm": 0.289160,
    "LeftForeArm": 0.270262, "LeftHand": 0.040068, "LeftHandThumb1": 0.047045, "LeftHandThumb2": 0.028564,
    "LeftHandThumb3": 0.031806, "LeftHandThumbEnd": 0.050000, "LeftHandIndex1": 0.063209, "LeftHandIndex2": 0.036355,
    "LeftHandIndex3": 0.023208, "LeftHandIndex4": 0.027612, "LeftHandIndexEnd": 0.050000, "LeftHandMiddle1": 0.060545,
    "LeftHandMiddle2": 0.045741, "LeftHandMiddle3": 0.029249, "LeftHandMiddle4": 0.023414, "LeftHandMiddleEnd": 0.050000,
    "LeftHandRing1": 0.058845, "LeftHandRing2": 0.043685, "LeftHandRing3": 0.026751, "LeftHandRing4": 0.019416,
    "LeftHandRingEnd": 0.050000, "LeftHandPinky1": 0.054877, "LeftHandPinky2": 0.030999, "LeftHandPinky3": 0.015850,
    "LeftHandPinky4": 0.018838, "LeftHandPinkyEnd": 0.050000, "RightShoulder": 0.157431, "RightArm": 0.289151,
    "RightForeArm": 0.270262, "RightHand": 0.040067, "RightHandThumb1": 0.047047, "RightHandThumb2": 0.028564,
    "RightHandThumb3": 0.031806, "RightHandThumbEnd": 0.050000, "RightHandIndex1": 0.063207, "RightHandIndex2": 0.036355,
    "RightHandIndex3": 0.023208, "RightHandIndex4": 0.027612, "RightHandIndexEnd": 0.050000, "RightHandMiddle1": 0.060546,
    "RightHandMiddle2": 0.045741, "RightHandMiddle3": 0.029248, "RightHandMiddle4": 0.023415, "RightHandMiddleEnd": 0.050000,
    "RightHandRing1": 0.058847, "RightHandRing2": 0.043685, "RightHandRing3": 0.026752, "RightHandRing4": 0.019416,
    "RightHandRingEnd": 0.050000, "RightHandPinky1": 0.054877, "RightHandPinky2": 0.030998, "RightHandPinky3": 0.015850,
    "RightHandPinky4": 0.018839, "RightHandPinkyEnd": 0.050000, "LeftLeg": 0.433003, "LeftShin": 0.424241,
    "LeftToeBase": 0.067754, "LeftToeEnd": 0.050000, "RightLeg": 0.433004, "RightShin": 0.424240,
    "RightToeBase": 0.067754, "RightToeEnd": 0.050000
}
    bone_lengths_galtis = {
    "spineinte_02": 11.154021,
    "spineinte_03": 13.500081,
    "neckinte_01": 9.007055,
    "neckinte_02": 7.800326,
    "headinte": 8.150731,
    "footinte_L": 17.526606,
    "footinte_R": 17.526604,
    "hip": 7.207733,
    "spineinte_04": 12.334437,
    "clavicleinte_L": 14.260497,
    "upperarminte_L": 25.439404,
    "lowerarminte_L": 20.627499,
    "handinte_L": 10.001600,
    "indexinte_metacarpal_L": 6.765002,
    "indexinte_01_L": 3.148665,
    "indexinte_02_L": 2.223212,
    "indexinte_03_L": 1.926071,
    "middleinte_metacarpal_L": 6.697499,
    "middleinte_01_L": 4.052257,
    "middleinte_02_L": 2.024192,
    "middleinte_03_L": 2.169761,
    "ringinte_metacarpal_L": 6.249301,
    "ringinte_02_L": 1.924728,
    "ringinte_03_L": 1.881157,
    "pinkyinte_metacarpal_L": 6.186300,
    "pinkyinte_01_L": 2.363476,
    "pinkyinte_02_L": 1.727912,
    "pinkyinte_03_L": 1.355308,
    "clavicleinte_R": 14.260498,
    "upperarminte_R": 25.439400,
    "lowerarminte_R": 20.627501,
    "handinte_R": 10.001600,
    "indexinte_metacarpal_R": 6.765002,
    "indexinte_01_R": 3.148664,
    "indexinte_02_R": 2.223213,
    "indexinte_03_R": 1.926071,
    "middleinte_metacarpal_R": 6.697500,
    "middleinte_01_R": 4.052257,
    "middleinte_02_R": 2.024192,
    "middleinte_03_R": 2.169761,
    "ringinte_metacarpal_R": 6.249301,
    "ringinte_02_R": 1.924728,
    "ringinte_03_R": 1.881157,
    "pinkyinte_metacarpal_R": 6.186300,
    "pinkyinte_01_R": 2.363476,
    "pinkyinte_02_R": 1.727912,
    "pinkyinte_03_R": 1.355308,
    "thighinte_L": 45.989285,
    "calfinte_L": 50.051117,
    "ballinte_L": 9.074887,
    "thighinte_R": 45.989285,
    "calfinte_R": 50.051121,
    "ballinte_R": 9.074888
    }
    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')



    MannequinFolder=parent_dir+'\\'+'Reference Rigs'
    soma=MannequinFolder+"\\"+"SOMA_rig2.fbx"

    bpy.ops.import_scene.fbx(filepath=soma, global_scale=1.0)
    
    root = bpy.context.active_object
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_soma.items():
        util_scripts.set_bone_length(root.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- 5. Constraints and Keyframing ---
    bpy.ops.object.mode_set(mode='POSE')
    constraints_added = 0
    for src_bone, tgt_bone in bone_maps.bone_mapping_soma_world.items():
        if src_bone in root.pose.bones and tgt_bone in armature_galtis.pose.bones:
            util_scripts.add_copy_transform_constraint_world(root.pose.bones[src_bone], armature_galtis, tgt_bone)
            constraints_added += 1

    # Influence Keyframing
    for frame, influence in [(1, 1.0), (0, 0.0)]:
        scene.frame_set(frame)
        for bone in root.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    soma_fbx_name = f"{stamp} SOMA TPose.fbx"
    soma_path = os.path.join(blend_file_dir, soma_fbx_name)



    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} soma TP"

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True, 
                     clear_constraints=False, use_current_action=True, bake_types={'POSE'})


    pose_magic_lib.run_pose_magic(
    armature_name="SOMA_Skeleton_T",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=True,
    output_dir=None,
    rig_type="SOMA",
    asset_library_reference='SOMA'
    )

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    root.select_set(True)
    bpy.ops.export_scene.fbx(filepath=soma_path, use_selection=True, object_types={'ARMATURE'}, 
                             add_leaf_bones=False, bake_anim=True)

    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove soma Actions
    for act in [a for a in bpy.data.actions if "soma" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    if "root" in bpy.data.objects:
        obj_meta = bpy.data.objects["root"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "root" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["root"])

    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.data.objects["SOMA_Body_T"].select_set(True)
    bpy.data.objects["SOMA_Skeleton_T"].select_set(True)
    
    bpy.ops.object.delete(use_global=False)

    if "SOMA_Skeleton_T" in bpy.data.objects:
        obj_meta = bpy.data.objects["SOMA_Skeleton_T"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "SOMA_Skeleton_T" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["SOMA_Skeleton_T"])
    
    if "Armature" in bpy.data.objects:
        obj_meta = bpy.data.objects["Armature"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "Armature" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["Armature"])
    
    # --- 8. Final Galtis Adjustments ---
    if armature_galtis:
        bpy.context.view_layer.objects.active = armature_galtis
        armature_galtis.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name, length in bone_lengths_galtis.items():
            util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")
    
# To run the script:
if __name__ == "__main__":
    process_soma_T()
    
    



# Using Blender 5.1.0
# Last tested May 6,  2026

import logging

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
PMX_FILEPATH = r"H:/Galt Workspace/Reference Rigs/reze.pmx"

# Default import options. Names and defaults match PMXImporter.execute()
# as used by the mmd_tools test suite.
#note scale 10 is roughly galtis size
IMPORT_OPTIONS = {
    "types": {"MESH", "ARMATURE", "PHYSICS", "MORPHS", "DISPLAY"},
    "scale": 10.00,
    "clean_model": False,
    "remove_doubles": False,
    "fix_ik_links": False,
    "apply_bone_fixed_axis": False,
    "rename_LR_bones":True,
    "use_underscore": False,
    "translator": None,
    "use_mipmap": True,
    "sph_blend_factor": 1.0,
    "spa_blend_factor": 1.0,
}


# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
def enable_mmd_tools():
    """Enable mmd_tools. Tries the Extensions module first (Blender 4.2+)."""
    pref = getattr(bpy.context, "preferences", None) or bpy.context.user_preferences
    addon_enable = (
        bpy.ops.preferences.addon_enable
        if "addon_enable" in dir(bpy.ops.preferences)
        else bpy.ops.wm.addon_enable
    )

    for module in ("bl_ext.blender_org.mmd_tools", "mmd_tools"):
        if pref.addons.get(module):
            return module
        try:
            addon_enable(module=module)
            if pref.addons.get(module):
                return module
        except Exception:
            continue

    raise RuntimeError(
        "mmd_tools is not installed/enabled. Install it via "
        "Edit > Preferences > Get Extensions, or from "
        "https://github.com/MMD-Blender/blender_mmd_tools"
    )


def _import_classes():
    """Import PMXImporter and Model from whichever mmd_tools path is available."""
    try:
        from bl_ext.blender_org.mmd_tools.core.model import Model
        from bl_ext.blender_org.mmd_tools.core.pmx.importer import PMXImporter
    except ImportError:
        from mmd_tools.core.model import Model
        from mmd_tools.core.pmx.importer import PMXImporter
    return PMXImporter, Model


# ----------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------
def import_pmx(filepath, **overrides):
    """
    Import a PMX/PMD file using PMXImporter directly.

    Returns the MMD root Empty object created by the importer.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)

    PMXImporter, _ = _import_classes()

    args = dict(IMPORT_OPTIONS)
    args.update(overrides)
    args["filepath"] = filepath

    # Make sure we're in OBJECT mode before importing, but don't touch
    # any existing objects/selection.
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # Snapshot existing objects so we can identify the newly created root.
    existing_objects = set(bpy.context.scene.objects)

    importer = PMXImporter()
    importer.execute(**args)

    bpy.context.view_layer.update()

    # Find the MMD root among the objects that were created by this import.
    new_objects = set(bpy.context.scene.objects) - existing_objects
    for obj in new_objects:
        if getattr(obj, "mmd_type", None) == "ROOT":
            return obj

    raise RuntimeError("PMX import finished but no MMD root object was found.")


# ----------------------------------------------------------------------
# Inspection (mirrors _get_model_components / _check_* helpers)
# ----------------------------------------------------------------------
def get_model_components(root_obj):
    """Return a dict of the imported model's parts, like the test helper."""
    _, Model = _import_classes()
    if not root_obj or root_obj.mmd_type != "ROOT":
        return None

    model = Model(root_obj)
    return {
        "root": root_obj,
        "armature": model.armature(),
        "meshes": list(model.meshes()),
        "rigid_bodies": list(model.rigidBodies()),
        "joints": list(model.joints()),
        "materials": list(model.materials()),
    }


def report(components):
    """Print a summary similar to test_pmx_importer_complete_workflow."""
    root = components["root"]
    armature = components["armature"]
    meshes = components["meshes"]

    mmd_root = root.mmd_root
    print("\n=== PMX Import Report ===")
    print(f"  Model name (JP): {mmd_root.name}")
    print(f"  Model name (EN): {mmd_root.name_e}")
    print(f"  Root object    : {root.name}")
    print(f"  Armature       : {armature.name if armature else '(none)'}")
    if armature:
        print(f"    Bones        : {len(armature.data.bones)}")
    print(f"  Meshes         : {len(meshes)}")
    for i, m in enumerate(meshes, 1):
        verts = len(m.data.vertices)
        polys = len(m.data.polygons)
        shape_keys = (
            len(m.data.shape_keys.key_blocks) if m.data.shape_keys else 0
        )
        print(f"    {i}. {m.name}  verts={verts}  polys={polys}  shape_keys={shape_keys}")
    print(f"  Materials      : {len(components['materials'])}")
    print(f"  Rigid bodies   : {len(components['rigid_bodies'])}")
    print(f"  Joints         : {len(components['joints'])}")

    # Morph counts
    print(
        f"  Morphs         : "
        f"vertex={len(mmd_root.vertex_morphs)} "
        f"bone={len(mmd_root.bone_morphs)} "
        f"material={len(mmd_root.material_morphs)} "
        f"uv={len(mmd_root.uv_morphs)} "
        f"group={len(mmd_root.group_morphs)}"
    )
    print(f"  Display frames : {len(mmd_root.display_item_frames)}")
    print("=========================\n")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    logging.getLogger().setLevel("ERROR")

    filepath = PMX_FILEPATH
    if "--" in sys.argv:
        extra = sys.argv[sys.argv.index("--") + 1 :]
        if extra:
            filepath = extra[0]

    enable_mmd_tools()

    root_obj = import_pmx(filepath)
    components = get_model_components(root_obj)
    report(components)


if __name__ == "__main__":
    main()
    
    
def process_pmx_T():
    
    blend_file_dir = os.path.dirname(bpy.data.filepath)
    
    if "Reincarnation" in blend_file_dir:
        parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
    else:
        parent_dir = os.path.dirname(blend_file_dir)

    script_path = os.path.join(parent_dir, "Scripts")
    if script_path not in sys.path:
        sys.path.append(script_path)

    try:
        import pose_magic_lib
        import bone_maps
        import util_scripts
        importlib.reload(pose_magic_lib)
        importlib.reload(bone_maps)
        importlib.reload(util_scripts)
    except ImportError as e:
        print(f"Error: Could not find required scripts in {script_path}. {e}")
        return


    bone_lengths_pmx = {
    # Torso and Head
    "Locator_Root": 0.7056, "hip": 0.1095, "spineinte_02": 0.0764,
    "spineinte_03": 0.1005, "spineinte_04": 0.2221, "neckinte_01": 0.0818,
    "headinte": 0.1173,
    # Left Arm and Hand
    "clavicleinte_L": 0.0847, "upperarminte_L": 0.2622, "lowerarminte_L": 0.2277,
    "handinte_L": 0.0558, "thumbinte_01_L": 0.0313, "thumbinte_02_L": 0.0250,
    "thumbinte_03_L": 0.0206, "pinkyinte_01_L": 0.0266, "pinkyinte_02_L": 0.0155,
    "pinkyinte_03_L": 0.0177, "ringinte_01_L": 0.0344, "ringinte_02_L": 0.0207,
    "ringinte_03_L": 0.0187, "middleinte_01_L": 0.0339, "middleinte_02_L": 0.0195,
    "middleinte_03_L": 0.0220, "indexinte_01_L": 0.0287, "indexinte_02_L": 0.0176,
    "indexinte_03_L": 0.0211,
    # Right Arm and Hand
    "clavicleinte_R": 0.0843, "upperarminte_R": 0.2610, "lowerarminte_R": 0.2266,
    "handinte_R": 0.0555, "thumbinte_01_R": 0.0319, "thumbinte_02_R": 0.0231,
    "thumbinte_03_R": 0.0187, "pinkyinte_01_R": 0.0272, "pinkyinte_02_R": 0.0158,
    "pinkyinte_03_R": 0.0181, "ringinte_01_R": 0.0339, "ringinte_02_R": 0.0204,
    "ringinte_03_R": 0.0184, "middleinte_01_R": 0.0374, "middleinte_02_R": 0.0215,
    "middleinte_03_R": 0.0243, "indexinte_01_R": 0.0294, "indexinte_02_R": 0.0180,
    "indexinte_03_R": 0.0216,
    # Right Leg
    "thighinte_R": 0.4429, "calfinte_R": 0.4276, "footinte_R": 0.1248,
    "ballinte_R": 0.0782,
    # Left Leg
    "thighinte_L": 0.4429, "calfinte_L": 0.4276, "footinte_L": 0.1248,
    "ballinte_L": 0.0782,
    # Eyes
    "eye_R": 0.0414, "eye_L": 0.0414,
    }

# Galtis-side bone lengths. Merged from both prior definitions: the
# higher-precision values (with metacarpals + neck_02) take priority,
# but eyes / Locator_Root / extra finger joints from the first table
# are preserved.
    bone_lengths_galtis = {
    # --- From the simpler table (preserved) ---
    "Locator_Root": 12.9931,
    "eye_R": 2.2460, "eye_L": 2.2460,
    # Finger joints not present in the metacarpal-aware table
    "thumbinte_01_L": 3.8113, "thumbinte_02_L": 2.6071, "thumbinte_03_L": 2.5597,
    "thumbinte_01_R": 3.8113, "thumbinte_02_R": 2.6071, "thumbinte_03_R": 2.5597,
    "ringinte_01_L": 3.3797,
    "ringinte_01_R": 3.3797,
    "footinte_L": 17.526606, "footinte_R": 17.526604,

    # --- From the more precise / metacarpal-aware table ---
    "spineinte_02": 11.154021,
    "spineinte_03": 13.500081,
    "neckinte_01": 9.007055,
    "neckinte_02": 7.800326,
    "headinte": 8.150731,
    "hip": 7.207733,
    "spineinte_04": 12.334437,

    "clavicleinte_L": 14.260497,
    "upperarminte_L": 25.439404,
    "lowerarminte_L": 20.627499,
    "handinte_L": 10.001600,
    "indexinte_metacarpal_L": 6.765002,
    "indexinte_01_L": 3.148665,
    "indexinte_02_L": 2.223212,
    "indexinte_03_L": 1.926071,
    "middleinte_metacarpal_L": 6.697499,
    "middleinte_01_L": 4.052257,
    "middleinte_02_L": 2.024192,
    "middleinte_03_L": 2.169761,
    "ringinte_metacarpal_L": 6.249301,
    "ringinte_02_L": 1.924728,
    "ringinte_03_L": 1.881157,
    "pinkyinte_metacarpal_L": 6.186300,
    "pinkyinte_01_L": 2.363476,
    "pinkyinte_02_L": 1.727912,
    "pinkyinte_03_L": 1.355308,

    "clavicleinte_R": 14.260498,
    "upperarminte_R": 25.439400,
    "lowerarminte_R": 20.627501,
    "handinte_R": 10.001600,
    "indexinte_metacarpal_R": 6.765002,
    "indexinte_01_R": 3.148664,
    "indexinte_02_R": 2.223213,
    "indexinte_03_R": 1.926071,
    "middleinte_metacarpal_R": 6.697500,
    "middleinte_01_R": 4.052257,
    "middleinte_02_R": 2.024192,
    "middleinte_03_R": 2.169761,
    "ringinte_metacarpal_R": 6.249301,
    "ringinte_02_R": 1.924728,
    "ringinte_03_R": 1.881157,
    "pinkyinte_metacarpal_R": 6.186300,
    "pinkyinte_01_R": 2.363476,
    "pinkyinte_02_R": 1.727912,
    "pinkyinte_03_R": 1.355308,

    "thighinte_L": 45.989285,
    "calfinte_L": 50.051117,
    "ballinte_L": 9.074887,
    "thighinte_R": 45.989285,
    "calfinte_R": 50.051121,
    "ballinte_R": 9.074888,
    }

    # --- 3. Initial Armature Setup ---
    util_scripts.setup_and_rename_armature("root", "Galtis")
    
    # Get frame range from Galtis
    armature_galtis = bpy.data.objects.get("Galtis")
    if not armature_galtis or not armature_galtis.animation_data:
        print("Error: 'root' (Galtis) armature or animation data not found.")
        return

    action = armature_galtis.animation_data.action
    scene = bpy.context.scene
    scene_end = int(action.frame_range[1])
    scene.frame_end = scene_end

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')


    pmx_arm = bpy.data.objects.get("reze_arm")
    if pmx_arm is None:
        # Fallback: find any armature whose parent is an mmd_type ROOT
        for obj in bpy.data.objects:
            if (obj.type == 'ARMATURE' 
                and obj.parent 
                and getattr(obj.parent, 'mmd_type', None) == 'ROOT'):
                pmx_arm = obj
                break

    if pmx_arm is None:
        print("ERROR: PMX armature not found. Aborting.")
        return

    print(f"Galtis armature: {armature_galtis.name}")
    print(f"PMX armature:    {pmx_arm.name}")
    
    bpy.context.scene.unit_settings.scale_length = 0.01
    # Reset Galtis Pose
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis
    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    bpy.ops.anim.keyframe_insert()

    # Apply bone lengths to Metarig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    pmx_arm = bpy.data.objects.get("reze_arm")
    if pmx_arm is None:
        for obj in bpy.data.objects:
            if (obj.type == 'ARMATURE'
                and obj.parent
                and getattr(obj.parent, 'mmd_type', None) == 'ROOT'):
                pmx_arm = obj
                break

    if pmx_arm is None:
        print("ERROR: PMX armature (reze_arm) not found in scene.")
        return

    print(f"Galtis armature: {armature_galtis.name}  ({len(armature_galtis.data.bones)} bones)")
    print(f"PMX armature:    {pmx_arm.name}  ({len(pmx_arm.data.bones)} bones)")

    # Activate PMX rig for constraint work
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    pmx_arm.select_set(True)
    bpy.context.view_layer.objects.active = pmx_arm
    bpy.ops.object.mode_set(mode='POSE')

    constraints_added = 0
    missing_on_pmx = []
    missing_on_galtis = []

    # Dict is {galtis_name: pmx_name}; constraint lives on PMX bone,
    # pointing at the Galtis bone as target.
    for galtis_name, pmx_name in bone_maps.bone_mapping_pmx_world.items():
        if pmx_name not in pmx_arm.pose.bones:
            missing_on_pmx.append(pmx_name)
            continue
        if galtis_name not in armature_galtis.pose.bones:
            missing_on_galtis.append(galtis_name)
            continue
        util_scripts.add_copy_transform_constraint_world(
            pmx_arm.pose.bones[pmx_name], armature_galtis, galtis_name
        )
        constraints_added += 1

    print(f"Constraints added: {constraints_added}/{len(bone_maps.bone_mapping_pmx_world)}")
    if missing_on_pmx:
        print(f"  Missing on PMX ({len(missing_on_pmx)}): {missing_on_pmx}")
    if missing_on_galtis:
        print(f"  Missing on Galtis ({len(missing_on_galtis)}): {missing_on_galtis}")

    # Influence keyframing on PMX bones
    for frame, influence in [(1, 1.0)]:
        scene.frame_set(frame)
        for bone in pmx_arm.pose.bones:
            if bone.constraints:
                util_scripts.keyframe_constraint_influence(bone, influence)

    # --- 6. Baking and Export ---
    stamp = util_scripts.get_stamp()
    pmx_vmd_name = f"{stamp} PMX TPose.fbx"
    soma_path = os.path.join(blend_file_dir, pmx_vmd_name)



    # Rename Action
    for act in bpy.data.actions:
        if act.name.endswith("Action"):
            act.name = f"{stamp} PMX TP"

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    pmx_arm.select_set(True)
    bpy.context.view_layer.objects.active = pmx_arm
    bpy.ops.object.mode_set(mode='POSE')

    bpy.ops.nla.bake(frame_start=1, frame_end=scene_end, visual_keying=True,
                 clear_constraints=False, use_current_action=True, bake_types={'POSE'})
                 
                 
    pose_magic_lib.run_pose_magic(
        armature_name="reze_arm",
        max_poses=50,
        export_json=False,
        export_csv=False,
        export_txt=True,
        output_dir=None,
        rig_type="Reze T",
        asset_library_reference='Reze_T',
    )

    bpy.ops.object.mode_set(mode='POSE')
    scene.frame_set(0)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.anim.keyframe_insert()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    pmx_arm.select_set(True)
    bpy.context.view_layer.objects.active = pmx_arm
    bpy.ops.export_scene.fbx(filepath=soma_path, use_selection=True,
                         object_types={'ARMATURE'},
                         add_leaf_bones=False, bake_anim=True)
    # --- 7. Cleanup Metarig ---
    bpy.ops.object.mode_set(mode='OBJECT')

    # Remove soma Actions
    for act in [a for a in bpy.data.actions if "PMX" in a.name]:
        bpy.data.actions.remove(act)

    # Delete Metarig Object and Data
    mmd_root = pmx_arm.parent
    for child in list(mmd_root.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(mmd_root, do_unlink=True)
    
        # Delete Metarig Object and Data
    if "reze" in bpy.data.objects:
        obj_meta = bpy.data.objects["reze"]
        bpy.data.objects.remove(obj_meta, do_unlink=True)
    if "reze" in bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures["reze"])

    bpy.ops.object.select_all(action='DESELECT')

    # Re-fetch by name in case the Python reference is stale
    armature_galtis = bpy.data.objects.get("Galtis")
    if armature_galtis is None:
        print("Galtis armature not found, skipping final adjustments.")
        return

    armature_galtis.hide_set(False)          # must be visible for mode_set
    armature_galtis.hide_viewport = False
    armature_galtis.select_set(True)
    bpy.context.view_layer.objects.active = armature_galtis

    # Verify
    assert bpy.context.view_layer.objects.active is armature_galtis, \
        "Failed to make Galtis active"

    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name, length in bone_lengths_galtis.items():
        util_scripts.set_bone_length(armature_galtis.data, bone_name, length)
    bpy.ops.object.mode_set(mode='OBJECT')

    util_scripts.setup_and_rename_armature("Galtis", "root")

    print("Workflow completed successfully.")
    
# To run the script:
if __name__ == "__main__":
    process_pmx_T()
    
    
