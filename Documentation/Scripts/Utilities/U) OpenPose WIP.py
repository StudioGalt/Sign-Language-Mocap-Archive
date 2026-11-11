import bpy
import os
import importlib



import pose_magic_lib
importlib.reload(pose_magic_lib)





blend_file_dir = os.path.dirname(bpy.data.filepath)
parent_dir = os.path.dirname(blend_file_dir)

OpenPoseFolder=parent_dir+'\\'+'Reference Rigs'
OpenPoseRig=OpenPoseFolder+"\\"+"OpenPose.FBX"


bpy.ops.import_scene.fbx(filepath=OpenPoseRig, automatic_bone_orientation=False)

file_name = bpy.path.basename(bpy.context.blend_data.filepath)
fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
print(Stamp)




bpy.context.scene.unit_settings.scale_length = 0.01

# Bone mapping dictionary with swapped order
bone_mapping_openpose_pose = {
    "pelvis":"pelvisinte",
    "stomach":"spineinte_01",
    "chest":"spineinte_03",
    "neck":"neckinte_01",
    "head":"headinte",
    "clavicle_r":"clavicleinte_R",
    "arm_r": "upperarminte_R",
    "forearm_r":"lowerarminte_R",
    "hand_r":"handinte_R",
    "f_thumb2_r":"thumbinte_01_R",
    "f_thumb3_r":"thumbinte_02_R",
    "f_thumb4_r":"thumbinte_03_R",
    "f_index1_r":"indexinte_metacarpal_R",
    "f_index2_r":"indexinte_01_R",
    "f_index3_r":"indexinte_02_R",
    "f_index4_r":"indexinte_03_R",
    "f_middle1_r":"middleinte_metacarpal_R",
    "f_middle2_r":"middleinte_01_R",
    "f_middle3_r":"middleinte_02_R",
    "f_middle4_r":"middleinte_03_R",
    "f_ring1_r":"ringinte_metacarpal_R",
    "f_ring2_r":"ringinte_01_R",
    "f_ring3_r":"ringinte_02_R", 
    "f_ring4_r":"ringinte_03_R",  
    "f_pinky1_r":"pinkyinte_metacarpal_R",
    "f_pinky2_r":"pinkyinte_01_R",
    "f_pinky3_r":"pinkyinte_01_R",
    "f_pinky4_r":"pinkyinte_01_R",
    "arm_twist_r": "upperarm_twist_02_r",
    "thigh_r":"thighinte_R",
    "calf_r":"calfinte_R",
    "foot_r":"footinte_R",
    "toe_r":"ballinte_R",
    "thigh_r_helper":"thighproxy_R",
    "stomach":"spineinte_01",
    "chest":"spineinte_03",
    "neck":"neckinte_01",
    "head":"headinte",
    "clavicle_l":"clavicleinte_L",
    "arm_l": "upperarminte_L",
    "forearm_l":"lowerarminte_L",
    "hand_l":"handinte_L",
    "f_thumb2_l":"thumbinte_01_L",
    "f_thumb3_l":"thumbinte_02_L",
    "f_thumb4_l":"thumbinte_03_L",
    "f_index1_l":"indexinte_metacarpal_L",
    "f_index2_l":"indexinte_01_L",
    "f_index3_l":"indexinte_02_L",
    "f_index4_l":"indexinte_03_L",
    "f_middle1_l":"middleinte_metacarpal_L",
    "f_middle2_l":"middleinte_01_L",
    "f_middle3_l":"middleinte_02_L",
    "f_middle4_l":"middleinte_03_L",
    "f_ling1_l":"ringinte_metacarpal_L",
    "f_ling2_l":"ringinte_01_L",
    "f_ling3_l":"ringinte_02_L", 
    "f_ling4_l":"ringinte_03_L",  
    "f_pinky1_l":"pinkyinte_metacarpal_L",
    "f_pinky2_l":"pinkyinte_01_L",
    "f_pinky3_l":"pinkyinte_01_L",
    "f_pinky4_l":"pinkyinte_01_L",
    "arm_twist_l": "upperarm_twist_02_l",
    "thigh_l":"thighinte_L",
    "calf_l":"calfinte_L",
    "foot_l":"footinte_L",
    "toe_l":"ballinte_L",
    "thigh_l_helper":"thighproxy_L",
}





# Get the active object
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

bpy.data.objects["root"].select_set(True)

obj = bpy.context.active_object


def add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'LOCAL_WITH_PARENT'
    constraint.owner_space = 'LOCAL_WITH_PARENT'

source_armature_name = "Armature"
target_armature_name = "root"

source_armature = bpy.data.objects[source_armature_name]
target_armature = bpy.data.objects[target_armature_name]

# Check if armatures exist
if source_armature_name not in bpy.data.objects:
    raise ValueError(f"Source armature '{source_armature_name}' not found in the scene.")

if target_armature_name not in bpy.data.objects:
    raise ValueError(f"Target armature '{target_armature_name}' not found in the scene.")

# Check if objects are armatures
if source_armature.type != 'ARMATURE':
    raise TypeError(f"Source object '{source_armature_name}' is not an armature.")
    
if target_armature.type != 'ARMATURE':
    raise TypeError(f"Target object '{target_armature_name}' is not an armature.")



# Ensure we're in pose mode for the source armature
bpy.context.view_layer.objects.active = source_armature
bpy.ops.object.mode_set(mode='POSE')

# Add constraints
constraints_added = 0
for source_bone_name, target_bone_name in bone_mapping_openpose_pose.items():
    if source_bone_name not in source_armature.pose.bones:
        print(f"Warning: Source bone '{source_bone_name}' not found in '{source_armature_name}'")
        continue
    if target_bone_name not in target_armature.pose.bones:
        print(f"Warning: Target bone '{target_bone_name}' not found in '{target_armature_name}'")
        continue
    source_bone = source_armature.pose.bones[source_bone_name]
    add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name)
    constraints_added += 1

print(f"Constraints added successfully! Total constraints added: {constraints_added}")

armature_name = "root"
bpy.context.scene.frame_set(1)

def keyframe_constraint_influence_1(bone):
    for constraint in bone.constraints:
        constraint.influence = 1.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")

# Check if the armature exists
if armature_name not in bpy.data.objects:
    raise ValueError(f"Armature '{armature_name}' not found in the scene.")

armature = bpy.data.objects[armature_name]

# Check if the object is an armature
if armature.type != 'ARMATURE':
    raise TypeError(f"Object '{armature_name}' is not an armature.")

# Ensure we're in pose mode for the armature
bpy.context.view_layer.objects.active = armature


#Keyframe all constraints at influence 1, on frame 1
constraints_keyframed = 0
for bone in armature.pose.bones:
    if bone.constraints:
        keyframe_constraint_influence_1(bone)
        constraints_keyframed += len(bone.constraints)


 
OpenPoseT=Stamp+ " OpenPose T.fbx" 
OpenPoseTPath=blend_file_dir+'\\'+ OpenPoseT


OpenPoseTAnim = Stamp + " OpenPose TP"

actions = bpy.data.actions
for action in actions:
    if action.name.endswith("ArmatureAction"):
        action.name = OpenPoseTAnim


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')

bpy.data.objects["root"].select_set(True)


pose_magic_lib.run_pose_magic(
    armature_name="Armature",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=False,
    output_dir=None,
    rig_type="Open Pose T",
    asset_library_reference='OpenPose_T'
)

bpy.context.scene.frame_set(0)

bpy.ops.export_scene.fbx(filepath=OpenPoseTPath,check_existing=True, 
    use_selection=True, object_types={'ARMATURE'}, 
    add_leaf_bones=False, bake_anim=True, bake_anim_use_all_bones=True, 
    bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, bake_anim_force_startend_keying=False)

#TPOSE Openpose should now be exported
#Onto APose Openpose


OpenPoseAAnim = Stamp + " OpenPose AP"

actions = bpy.data.actions
for action in actions:
    if action.name.endswith("OpenPose TP"):
        action.name = OpenPoseAAnim




#
def keyframe_constraint_influence_0(bone):
    for constraint in bone.constraints:
        constraint.influence = 0.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



if armature_name not in bpy.data.objects:
    raise ValueError(f"Armature '{armature_name}' not found in the scene.")

armature = bpy.data.objects[armature_name]

# Check if the object is an armature
if armature.type != 'ARMATURE':
    raise TypeError(f"Object '{armature_name}' is not an armature.")

# Ensure we're in pose mode for the armature
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# Get the current frame
current_frame = bpy.context.scene.frame_current

# Keyframe constraints on influence 0 on frame 0
constraints_keyframed = 0
for bone in armature.pose.bones:
    if bone.constraints:
        keyframe_constraint_influence_0(bone)
        constraints_keyframed += len(bone.constraints)

print(f"Constraint influences keyframed successfully! Total constraints keyframed: {constraints_keyframed}")
print(f"Keyframes set at frame {current_frame}")

    
OpenPoseA=Stamp+ " OpenPose APose.fbx" 
OpenPoseAPath=blend_file_dir+'\\'+ OpenPoseA



if armature_name not in bpy.data.objects:
    raise ValueError(f"Armature '{armature_name}' not found in the scene.")

armature = bpy.data.objects[armature_name]

# Check if the object is an armature
if armature.type != 'ARMATURE':
    raise TypeError(f"Object '{armature_name}' is not an armature.")

# Ensure we're in pose mode for the armature
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# Get the current frame
current_frame = bpy.context.scene.frame_current

print(f"Constraint influences keyframed successfully! Total constraints keyframed: {constraints_keyframed}")
print(f"Keyframes set at frame {current_frame}")


pose_magic_lib.run_pose_magic(
    armature_name="Armature",
    max_poses=50,
    export_json=False,
    export_csv=False,
    export_txt=False,
    output_dir=None,
    rig_type="Open Pose A",
    asset_library_reference='OpenPose_A'
)




bpy.ops.export_scene.fbx(filepath=OpenPoseAPath,check_existing=True, 
    use_selection=True, object_types={'ARMATURE'}, 
    add_leaf_bones=False, bake_anim=True, bake_anim_use_all_bones=True, 
    bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, bake_anim_force_startend_keying=False)






#bpy.data.objects["Armature"].select_set(True)
#bpy.data.objects["OpenPose_mesh"].select_set(True)
#bpy.ops.object.delete(use_global=False)

#Local with parent default,
#lowerarm world space
#metacarpal and finger ???

