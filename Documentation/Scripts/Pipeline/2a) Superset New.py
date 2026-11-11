import bpy
import os
import sys



#Necessary Addon Animation Layer by Tal
blend_file_dir = os.path.dirname(bpy.data.filepath)


if "Reincarnation" in blend_file_dir:
    # Parent's parent directory
    parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
else:
    # One parent directory
    parent_dir = os.path.dirname(blend_file_dir)
    
    

script_path = parent_dir + "\\Scripts\\" 

print(script_path)


if script_path not in sys.path:
    sys.path.append(script_path)

import util_scripts

util_scripts.toggle_collections_visibility(set_visible=True)
util_scripts.toggle_solo_collections(set_solo=False)



#After you have used autorig pro for retargeting, use this script.

#Grab the rig
GaltisRig = bpy.data.objects['root']

obj = bpy.context.object

#esnsure solo levels are turned off
for collection in obj.data.collections_all.values():
    collection.is_solo = False


bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = GaltisRig

#This turn Animation Layers on.
bpy.context.object.als.turn_on = True
bpy.ops.object.mode_set(mode='POSE')
util_scripts.toggle_collections_visibility(set_visible=True)
util_scripts.toggle_solo_collections(set_solo=False)

#This adds an animation layer, from Animation Layers.
    
bpy.data.objects["root"].pose.bones["FKIK Switch"]["ArmIKFK_L"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["ArmIKFK_R"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["LegIKFK_L"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["LegIKFK_R"] = 1


##
bpy.ops.anim.add_anim_layer()
bpy.ops.anim.remove_anim_layer()
bpy.context.object.als.layer_index = 0
bpy.context.object.Anim_Layers[0].name = "Base_Layer"
bpy.ops.anim.duplicate_anim_layer()
bpy.context.object.animation_data.nla_tracks["Base_Layer.001"].strips["Base_Layer.001"].blend_type = 'REPLACE'
bpy.context.object.als.layer_index = 0

bpy.context.object.Anim_Layers[0].influence_mute = True
bpy.context.object.Anim_Layers[0].influence = 0

bpy.context.object.als.layer_index = 1
bpy.context.object.Anim_Layers[1].name = "Subtractive_Layer"


bpy.ops.anim.add_anim_layer()
bpy.context.object.Anim_Layers[2].name = "Correction_Layer"
bpy.context.scene.frame_set(0)
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.anim.keyframe_insert()
bpy.ops.pose.copy()
#This is done to ensure the T-pose is perserved, Xsens files have a T-pose on frame 0

#The following are anchor points to perserve the motion, 30 from beginning and end.
#For whatever corrections are at the ends, do not effect the middle
bpy.context.scene.frame_set(bpy.context.scene.frame_start)
bpy.context.scene.frame_set(30)
bpy.ops.anim.keyframe_insert()


scene = bpy.context.scene
scene.frame_set(scene.frame_end - 30)
bpy.ops.anim.keyframe_insert()


#To create a standardize rest position, we got to frame 1, and copy and modify the T-Pose, by moving BicepFk.
bpy.context.scene.frame_set(1)
bpy.ops.pose.paste(flipped=False)
bpy.ops.pose.select_all(action='DESELECT')


asl_poses = {
"NEUTRAL": {
    "bicepfk_L": (0.8104, 0.5843, -0.0432, 0.0055),
    "forearmfk_L": (0.7627, 0.3034, 0.4544, 0.3461),
    "handfk_L": (0.9886, 0.0577, 0.1288, -0.0527),
    "bicepfk_R": (0.8104, 0.5843, 0.0432, -0.0055),
    "forearmfk_R": (0.7627, 0.3034, -0.4544, -0.3461),
    "handfk_R": (0.9795, 0.1123, -0.1467, 0.0799),
    "thighfk_L": (1.0000, 0.0000, 0.0000, -0.0000),
    "shinfk_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "footfk_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "toefk_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "thighfk_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "shinfk_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "footfk_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "toefk_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_01_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_02_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_03_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_04_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyinte_metacarpal_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_01_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_02_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_03_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_04_L": (1.0000, 0.0000, 0.0000, -0.0000),
    "indexinte_metacarpal_L": (1.0000, 0.0000, 0.0000, -0.0000),
    "indexfk_01_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_02_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_03_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_04_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "middleinte_metacarpal_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_01_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_02_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_03_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_04_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringinte_metacarpal_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_01_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_02_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_03_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_04_L": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_01_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_02_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_03_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "thumbfk_04_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyinte_metacarpal_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_01_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_02_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_03_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "pinkyfk_04_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexinte_metacarpal_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_01_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_02_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_03_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "indexfk_04_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "middleinte_metacarpal_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_01_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_02_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_03_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "middlefk_04_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringinte_metacarpal_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_01_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_02_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_03_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "ringfk_04_R": (1.0000, 0.0000, 0.0000, 0.0000),
    "collar_R": (0.9965, 0.0033, 0.0489, -0.0674),
    "collar_L": (0.9977, -0.0003, 0.0048, 0.0675),
    "neckfk": (1.0000, 0.0000, 0.0000, 0.0000),
    "headfk": (1.0000, 0.0000, 0.0000, 0.0000),
    "chest_5": (1.0000, 0.0000, 0.0000, 0.0000),
    "chest_4": (1.0000, 0.0000, 0.0000, 0.0000),
    "chest_3": (0.9998, -0.0193, -0.0032, -0.0074),
    "chest_2": (1.0000, 0.0000, 0.0000, 0.0000),
    "chest_1": (1.0000, 0.0000, 0.0000, 0.0000),
    "hip": (1.0000, 0.0000, 0.0000, 0.0000),
}
}


POSE_NAME = "NEUTRAL"  
frame = bpy.context.scene.frame_current  

# --- Helper function to insert keyframes into an action directly ---
def insert_quaternion_key(action, bone_name, frame, quat):
    """
    Insert quaternion keyframes directly into the action FCurves.
    Avoids the NLA stack restrictions.
    """
    paths = [
        (bone_name, "rotation_quaternion", 0, quat[0]),
        (bone_name, "rotation_quaternion", 1, quat[1]),
        (bone_name, "rotation_quaternion", 2, quat[2]),
        (bone_name, "rotation_quaternion", 3, quat[3]),
    ]

    for bone, path, index, value in paths:
        fcurve = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves.find(f'pose.bones["{bone}"].{path}', index=index)
        if not fcurve:
            fcurve = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves.new(data_path=f'pose.bones["{bone}"].{path}', index=index)
        fcurve.keyframe_points.insert(frame, value, options={'FAST'})


# --- Script Execution ---
armature = bpy.context.object
if armature is None or armature.type != 'ARMATURE':
    raise Exception("Select an armature object before running the script")

if armature.animation_data is None:
    armature.animation_data_create()

if armature.animation_data.action is None:
    armature.animation_data.action = bpy.data.actions.new(name="ASL_Pose_Action")

action = armature.animation_data.action
pose_data = asl_poses[POSE_NAME]

if armature.mode != 'POSE':
    bpy.ops.object.mode_set(mode='POSE')

# Apply the pose & keyframe safely
for bone_name, quat in pose_data.items():
    if bone_name in armature.pose.bones:
        pb = armature.pose.bones[bone_name]
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = quat
        insert_quaternion_key(action, bone_name, frame, quat)
        print(f"✅ Set and keyed {bone_name}")
    else:
        print(f"⚠️ Bone not found: {bone_name}")

print(f"\n✅ Pose '{POSE_NAME}' applied and keyed on frame {frame} (NLA-safe).")

bpy.ops.pose.select_all(action='SELECT')
bpy.ops.anim.keyframe_insert()
bpy.ops.pose.copy()

bpy.context.scene.frame_set(bpy.context.scene.frame_end)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()
bpy.ops.pose.select_all(action='DESELECT')


#This is a stabilizer, to keep the legs and hips mostly in the same place, 
#It allow a little movement for realism

bpy.context.scene.frame_set(1)
bpy.ops.pose.select_all(action='DESELECT')


bpy.ops.object.mode_set(mode='EDIT') 
bpy.data.objects["root"].data.edit_bones['hip'].select = True
bpy.data.objects["root"].data.edit_bones['thighfk_L'].select = True
bpy.data.objects["root"].data.edit_bones['shinfk_L'].select = True
bpy.data.objects["root"].data.edit_bones['footfk_L'].select = True
bpy.data.objects["root"].data.edit_bones['toefk_L'].select = True

bpy.data.objects["root"].data.edit_bones['thighfk_R'].select = True
bpy.data.objects["root"].data.edit_bones['shinfk_R'].select = True
bpy.data.objects["root"].data.edit_bones['footfk_R'].select = True
bpy.data.objects["root"].data.edit_bones['toefk_R'].select = True

bpy.ops.object.mode_set(mode='POSE') 


bpy.context.scene.frame_set(1)
bpy.ops.pose.copy()
bpy.context.scene.frame_set(2)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()
bpy.context.scene.frame_set(30)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()
scene.frame_set(scene.frame_end - 30)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()



start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end



for frame in range(start_frame, end_frame + 1, 30):
    bpy.context.scene.frame_set(frame)
    bpy.ops.pose.paste(flipped=False)
    bpy.ops.anim.keyframe_insert()


#This is repeated with the Chest. These edits are all kept on seperate layer. 
#If necessary to remove they can be removed. 

bpy.context.scene.frame_set(1)
bpy.ops.pose.select_all(action='DESELECT')



bpy.ops.object.mode_set(mode='EDIT') 
bpy.data.objects["root"].data.edit_bones['chest_1' ].select = True
bpy.data.objects["root"].data.edit_bones['chest_2' ].select = True
bpy.data.objects["root"].data.edit_bones['chest_3' ].select = True
bpy.data.objects["root"].data.edit_bones['chest_4' ].select = True
bpy.data.objects["root"].data.edit_bones['neckfk' ].select = True
bpy.data.objects["root"].data.edit_bones['headfk' ].select = True


bpy.ops.object.mode_set(mode='POSE') 


bpy.ops.pose.copy()


bpy.context.scene.frame_set(30)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()
scene.frame_set(scene.frame_end - 30)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()
scene.frame_set(scene.frame_end)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(1)
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.copy()


bpy.context.scene.frame_set(2)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()

#Now we bake our FK limbs to IK
GaltisRig = bpy.data.objects['root']
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = GaltisRig

def snaparm_ik_to_fk(armature_name, fk_bones, ik_bones, frame_range):
    armature = bpy.data.objects.get(armature_name)
    if armature is None or armature.type != 'ARMATURE':
        print(f"Object '{armature_name}' not found or not an armature")
        return
    for frame in frame_range:
        bpy.context.scene.frame_set(frame)
        for fk_bone, ik_bone in zip(fk_bones, ik_bones):
            fk_bone_obj = armature.pose.bones.get(fk_bone)
            ik_bone_obj = armature.pose.bones.get(ik_bone)
            if fk_bone_obj is None or ik_bone_obj is None:
                print(f"Bones '{fk_bone}' or '{ik_bone}' not found in armature '{armature_name}'")
                continue
            ik_bone_obj.matrix = fk_bone_obj.matrix
            for channel in ['location', 'rotation_quaternion', 'scale']:
                armature.keyframe_insert(data_path=f'pose.bones["{ik_bone}"].{channel}', frame=frame)
        bpy.context.view_layer.update()

def snapleg_ik_to_fk(armature_name, fk_bones, ik_bones, frame_range):
    armature = bpy.data.objects.get(armature_name)
    if armature is None or armature.type != 'ARMATURE':
        print(f"Object '{armature_name}' not found or not an armature")
        return
    for frame in frame_range:
        bpy.context.scene.frame_set(frame)
        for fk_bone, ik_bone in zip(fk_bones, ik_bones):
            fk_bone_obj = armature.pose.bones.get(fk_bone)
            ik_bone_obj = armature.pose.bones.get(ik_bone)
            if fk_bone_obj is None or ik_bone_obj is None:
                print(f"Bones '{fk_bone}' or '{ik_bone}' not found in armature '{armature_name}'")
                continue
            ik_bone_obj.matrix = fk_bone_obj.matrix
            for channel in ['location', 'rotation_quaternion', 'scale']:
                armature.keyframe_insert(data_path=f'pose.bones["{ik_bone}"].{channel}', frame=frame)
        bpy.context.view_layer.update()




# Replace 'Armature' with the name of your armature object
armature_name = 'root'

# Define the FK and IK bone names
fkarm_bonesR = ['bicepfk_R', 'forearmfk_R', 'handfk_R']
ikarm_bonesR = ['bicepik_R', 'forearmik_R', 'handik_R']
fkarm_bonesL = ['bicepfk_L', 'forearmfk_L', 'handfk_L']
ikarm_bonesL = ['bicepik_L', 'forearmik_L', 'handik_L']

fkleg_bonesR = ['thighfk_R', 'shinfk_R', 'footfk_R']
ikleg_bonesR = ['thighik_R', 'shinik_R', 'footik_R']
fkleg_bonesL = ['thighfk_L', 'shinfk_L', 'footfk_L']
ikleg_bonesL = ['thighik_L', 'shinik_L', 'footik_L']



scene_end = bpy.context.scene.frame_end

# Set the frame range for keyframing
frame_range = range(0, scene_end)  # Replace with your desired frame range

# Call the function to snap FK bones to their IK counterparts and keyframe them
snaparm_ik_to_fk(armature_name, fkarm_bonesR, ikarm_bonesR, frame_range)
snaparm_ik_to_fk(armature_name, fkarm_bonesL, ikarm_bonesL, frame_range)


snapleg_ik_to_fk(armature_name, fkarm_bonesR, ikarm_bonesR, frame_range)
snapleg_ik_to_fk(armature_name, fkarm_bonesL, ikarm_bonesL, frame_range)


#We removed keyframes from IK bones, that are not controller.
#This will not effect position, but also makes editting easier.
def remove_keyframes_for_bone(armature, bone_name):
    if bone_name in armature.pose.bones:
        pose_bone = armature.pose.bones[bone_name]
        if armature.animation_data:
            fcurves_to_remove = []
            for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                if fcurve.data_path.startswith(f'pose.bones["{pose_bone.name}"]'):
                    fcurves_to_remove.append(fcurve)
            for fcurve in fcurves_to_remove:
                action.layers[0].strips[0].channelbag(action.slots[0]).fcurves.remove(fcurve)        


root = bpy.data.objects.get("root")
if root and root.type == "ARMATURE":
    bpy.ops.object.mode_set(mode="POSE")  
    bpy.context.view_layer.objects.active = root 
    specific_IKbones = [
        'bicepik_L', 'forearmik_L', 'bicepik_R', 'forearmik_R', 
        'thighik_L',  'shinik_L', 'thighik_R', 'shinik_R',
    ]
    for bone_name in specific_IKbones:
        remove_keyframes_for_bone(root, bone_name)



bpy.ops.anim.add_anim_layer()
bpy.context.object.Anim_Layers[3].name = "Working_Layer"
bpy.context.scene.frame_set(0)
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(1)
bpy.ops.anim.keyframe_insert()


bpy.ops.pose.copy()


scene = bpy.context.scene



bpy.context.scene.frame_set(scene.frame_end-1)
bpy.ops.anim.keyframe_insert()


bpy.context.scene.frame_set(scene.frame_end)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()

bpy.ops.pose.select_all(action='DESELECT')


#Move the elbow target from rest pose to a more natural default.
#They are originally set for T-Pose, and this moves them to N-Pose.




bpy.ops.object.mode_set(mode='EDIT') 


bpy.data.objects["root"].data.edit_bones['elbow_target_R'].select = True
bpy.data.objects["root"].data.edit_bones['elbow_target_L'].select = True

bpy.ops.object.mode_set(mode='POSE') 

bpy.context.scene.frame_set(20)



bpy.ops.transform.translate(value=(0, 0, 60), orient_type='LOCAL', orient_matrix=((-1, 0, 0), (0, 1, 2.8213e-07), (0, 2.8213e-07, -1)), orient_matrix_type='LOCAL', constraint_axis=(False, False, True), mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

bpy.ops.anim.keyframe_insert()

bpy.ops.pose.copy()

bpy.context.scene.frame_set(scene.frame_end-20)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()

bpy.context.object.pose.use_mirror_x = False
bpy.ops.object.mode_set(mode='EDIT') 

bpy.data.objects["root"].data.edit_bones['elbow_target_R'].select = False


#We now activate the FK/IK switch so that IK will be used.
bpy.data.objects["root"].data.edit_bones['FKIK Switch'].select = True

bpy.ops.object.mode_set(mode='POSE') 

if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
    # Set the mode to 'POSE'
    bpy.ops.object.mode_set(mode='POSE')
else:
    print("No armature selected.")



bpy.context.scene.frame_set(1)
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.copy()
bpy.context.scene.frame_set(scene.frame_end-1)
bpy.ops.pose.paste(flipped=False)
bpy.ops.anim.keyframe_insert()


root = bpy.data.objects.get("root")
if root and root.type == "ARMATURE":
    bpy.ops.object.mode_set(mode="POSE")  
    bpy.context.view_layer.objects.active = root  # Corrected line
    specificIK_bones = [
        'bicepik_L', 'forearmik_L', 'bicepik_R', 'forearmik_R', 
        'thighik_L',  'shinik_L', 'thighik_R', 'shinik_R',
    ]
    for bone_name in specificIK_bones:
        remove_keyframes_for_bone(root, bone_name)

#For some reason the rig creates reversed elbow, we can fix this by clearing the rotation.

bpy.ops.pose.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='EDIT') 


bpy.data.objects["root"].data.edit_bones['forearmik_R'].select = True
bpy.data.objects["root"].data.edit_bones['bicepik_R'].select = True
bpy.data.objects["root"].data.edit_bones['forearmik_L'].select = True
bpy.data.objects["root"].data.edit_bones['bicepik_L'].select = True


bpy.ops.object.mode_set(mode='POSE') 

bpy.ops.pose.rot_clear()
#Done
bpy.ops.pose.select_all(action='DESELECT')

file_name = bpy.path.basename(bpy.context.blend_data.filepath)
fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
print(Stamp)

#we add blinking to the rig, my having the rig oscilate between Eye Close 0, 1. 
#The Rig starts and ends on eyes open, to allow looping, and make sure mixing motions is good.
object_name = "GaltisHead"  # replace with the name of your object

shape_key_nameL = "EyesCloseL_AU43_L"
shape_key_nameR = "EyesCloseR_AU43_R"

scene = bpy.context.scene
start_frame = scene.frame_start
end_frame = scene.frame_end

obj = bpy.data.objects.get(object_name)

if not obj:
    print(f"No object found with the name {object_name}.")
else:
    for frame in range(start_frame, end_frame, 60):  # Adjusted the range to include start_frame and end_frame
        scene.frame_set(frame)
        # Shape Key L
        shape_keyL = obj.data.shape_keys.key_blocks.get(shape_key_nameL)
        if shape_keyL:
            shape_keyL.value = 0.0  # Corrected the value to 1.0 as per the comment
            shape_keyL.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameL} value to 0 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameL}.")
        # Shape Key R (if needed)
        shape_keyR = obj.data.shape_keys.key_blocks.get(shape_key_nameR)
        if shape_keyR:
            shape_keyR.value = 0.0
            shape_keyR.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameR} value to 0 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameR}.")


if not obj:
    print(f"No object found with the name {object_name}.")
else:
    for frame in range(start_frame+20, end_frame-20, 60):  # Adjusted the range to include start_frame and end_frame
        scene.frame_set(frame)
        # Shape Key L
        shape_keyL = obj.data.shape_keys.key_blocks.get(shape_key_nameL)
        if shape_keyL:
            shape_keyL.value = 0.0  # Corrected the value to 1.0 as per the comment
            shape_keyL.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameL} value to 0 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameL}.")
        # Shape Key R (if needed)
        shape_keyR = obj.data.shape_keys.key_blocks.get(shape_key_nameR)
        if shape_keyR:
            shape_keyR.value = 0.0
            shape_keyR.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameR} value to 0 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameR}.")

if not obj:
    print(f"No object found with the name {object_name}.")
else:
    for frame in range(start_frame+30, end_frame-30, 60):  # Adjusted the range to include start_frame and end_frame
        scene.frame_set(frame)
        # Shape Key L
        shape_keyL = obj.data.shape_keys.key_blocks.get(shape_key_nameL)
        if shape_keyL:
            shape_keyL.value = 1.0  # Corrected the value to 1.0 as per the comment
            shape_keyL.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameL} value to 1 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameL}.")
        # Shape Key R (if needed)
        shape_keyR = obj.data.shape_keys.key_blocks.get(shape_key_nameR)
        if shape_keyR:
            shape_keyR.value = 1.0
            shape_keyR.keyframe_insert(data_path="value", frame=frame)
            print(f"Set {shape_key_nameR} value to 1 and inserted keyframe at frame {frame}.")
        else:
            print(f"No shape key found with the name {shape_key_nameR}.")
        

#Renaming the Shapekeys after the motion in question for easy of use.
#This is important because later scripts will want a predictable name for shapekeys
old_datablock_name = "Key"  # Replace with the name of your shape key datablock
new_datablock_name = Stamp + " ShapeKeys" # Replace with the new name you desire

shape_key_datablock = bpy.data.shape_keys.get(old_datablock_name)
if shape_key_datablock:
    shape_key_datablock.name = new_datablock_name
    print(f"Shape Key Datablock '{old_datablock_name}' renamed to '{new_datablock_name}'.")
else:
    print(f"No Shape Key Datablock found with the name {old_datablock_name}.")




bpy.data.actions["GaltisHeadVerticesAction"].name = new_datablock_name


#Last step is hiding bone setting rig ready for animating.
bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'

util_scripts.toggle_collections_visibility(set_visible=False)
bpy.context.object.data.collections["Limbs IK"].is_visible = True


#Save as copy of the file. 
blend_file_dir = os.path.dirname(bpy.data.filepath)

#Set your working directory
file_name = bpy.path.basename(bpy.context.blend_data.filepath)

fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
actions = bpy.data.actions

#Sometimes the reference action name is too long, so a second filter hits Reference       
for action in actions:
    # Check if the action name does not start with "SG ASL"
    if action.name.startswith(("Action", "Anim")):
        # Remove the action
        bpy.data.actions.remove(action)                
        
 
filepath = bpy.data.filepath
filename = bpy.path.basename(filepath) if filepath else "Untitled"

# Get the scene frame range
scene = bpy.context.scene
frame_start = scene.frame_start
frame_end = scene.frame_end

# Determine save location (same directory as blend file, or user's home)
if filepath:
    save_dir = os.path.dirname(filepath)
else:
    save_dir = os.path.expanduser("~")

Frametxt = Stamp + ' Framelog.txt'
output_file = os.path.join(save_dir, Frametxt)

# Write to file
with open(output_file, 'w') as f:
    f.write(f"End Frame Adjustment Report\n")
    f.write(f"Generated from: {Stamp}\n")
    f.write(f"Blender Version: {bpy.app.version_string}\n")
    f.write(f"File: {filename}\n")
    f.write(f"Frame Range: {frame_start} - {frame_end}\n")
    print(f"Scene info saved to: {output_file}")
   
    
ArchivePathblend1=blend_file_dir + '\\'  + Stamp + ' Working.blend'
bpy.ops.wm.save_as_mainfile(filepath=ArchivePathblend1)


