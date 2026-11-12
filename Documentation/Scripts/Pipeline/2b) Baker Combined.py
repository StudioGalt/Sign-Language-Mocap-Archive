import bpy
import csv
import os


# Using Blender 5.1.0
# Last tested March 18,  2025 

#Use after you completed animating the motion
blend_file_dir = os.path.dirname(bpy.data.filepath)


#Set your working directory
file_name = bpy.path.basename(bpy.context.blend_data.filepath)


fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
print(Stamp)



ArchivePathblend1=blend_file_dir + '\\'  + Stamp + ' Working.blend'
bpy.ops.wm.save_as_mainfile(filepath=ArchivePathblend1)






obj = bpy.context.object

# Iterate over all collections in the object's data
for collection in obj.data.collections_all.values():
    collection.is_solo = False

blend_file_dir = os.path.dirname(bpy.data.filepath)


#Set your working directory
file_name = bpy.path.basename(bpy.context.blend_data.filepath)


fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])

ArchivePathblend=blend_file_dir+'\\' + file_name
bpy.ops.wm.save_as_mainfile(filepath=ArchivePathblend)



#Snap all fk limbs to ik
def snap_fk_to_ik(armature_name, fk_bones, ik_bones, frame_range):
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
            fk_bone_obj.matrix = ik_bone_obj.matrix
            for channel in ['location', 'rotation_quaternion', 'scale']:
                armature.keyframe_insert(data_path=f'pose.bones["{fk_bone}"].{channel}', frame=frame)
        bpy.context.view_layer.update()


armature_name = 'root'

fkarm_bonesR = ['bicepfk_R', 'forearmfk_R', 'handfk_R']
ikarm_bonesR = ['bicepik_R', 'forearmik_R', 'handik_R']
fkarm_bonesL = ['bicepfk_L', 'forearmfk_L', 'handfk_L']
ikarm_bonesL = ['bicepik_L', 'forearmik_L', 'handik_L']


scene_end = bpy.context.scene.frame_end

frame_range = range(0, scene_end) 

snap_fk_to_ik(armature_name, fkarm_bonesR, ikarm_bonesR, frame_range)
snap_fk_to_ik(armature_name, fkarm_bonesL, ikarm_bonesL, frame_range)

fkleg_bonesR = ['thighfk_R', 'shinfk_R', 'footfk_R']
ikleg_bonesR = ['thighik_R', 'shinik_R', 'footik_R']
fkleg_bonesL = ['thighfk_L', 'shinfk_L', 'footfk_L']
ikleg_bonesL = ['thighik_L', 'shinik_L', 'footik_L']

snap_fk_to_ik(armature_name, fkleg_bonesR, ikleg_bonesR, frame_range)
snap_fk_to_ik(armature_name, fkleg_bonesL, ikleg_bonesL, frame_range)


def snapfinger_fk_to_ik(armature_name, fk_bones, ik_bones, frame_range):
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
            fk_bone_obj.matrix = ik_bone_obj.matrix
            for channel in ['location', 'rotation_euler', 'scale']:
                armature.keyframe_insert(data_path=f'pose.bones["{fk_bone}"].{channel}', frame=frame)
        bpy.context.view_layer.update()

# Replace 'Armature' with the name of your armature object
armature_name = 'root'

fkthumb_bonesR = ['thumbfk_01_R', 'thumbfk_02_R', 'thumbfk_03_R', 'thumbfk_04_R']
ikthumb_bonesR= ['thumbik_01_R', 'thumbik_02_R', 'thumbik_03_R', 'thumbCTRL_R']
fkthumb_bonesL = ['thumbfk_01_L', 'thumbfk_02_L', 'thumbfk_03_L', 'thumbfk_04_L']
ikthumb_bonesL= ['thumbik_01_L', 'thumbik_02_L', 'thumbik_03_L', 'thumbCTRL_L']


fkindex_bonesR = ['indexfk_01_R', 'indexfk_02_R', 'indexfk_03_R', 'indexfk_04_R']
ikindex_bonesR= ['indexik_01_R', 'indexik_02_R', 'indexik_03_R', 'indexCTRL_R']
fkindex_bonesL = ['indexfk_01_L', 'indexfk_02_L', 'indexfk_03_L', 'indexfk_04_L']
ikindex_bonesL= ['indexik_01_L', 'indexik_02_L', 'indexik_03_L', 'indexCTRL_L']



fkmiddle_bonesR = ['middlefk_01_R', 'middlefk_02_R', 'middlefk_03_R', 'middlefk_04_R']
ikmiddle_bonesR= ['middleik_01_R', 'middleik_02_R', 'middleik_03_R', 'middleCTRL_R']
fkmiddle_bonesL = ['middlefk_01_L', 'middlefk_02_L', 'middlefk_03_L', 'middlefk_04_L']
ikmiddle_bonesL= ['middleik_01_L', 'middleik_02_L', 'middleik_03_L', 'middleCTRL_L']


fkring_bonesR = ['ringfk_01_R', 'ringfk_02_R', 'ringfk_03_R', 'ringfk_04_R']
ikring_bonesR= ['ringik_01_R', 'ringik_02_R', 'ringik_03_R', 'ringCTRL_R']
fkring_bonesL = ['ringfk_01_L', 'ringfk_02_L', 'ringfk_03_L', 'ringfk_04_L']
ikring_bonesL= ['ringik_01_L', 'ringik_02_L', 'ringik_03_L', 'ringCTRL_L']



fkpinky_bonesR = ['pinkyfk_01_R', 'pinkyfk_02_R', 'pinkyfk_03_R', 'pinkyfk_04_R']
ikpinky_bonesR= ['pinkyik_01_R', 'pinkyik_02_R', 'pinkyik_03_R', 'pinkyCTRL_R']
fkpinky_bonesL = ['pinkyfk_01_L', 'pinkyfk_02_L', 'pinkyfk_03_L', 'pinkyfk_04_L']
ikpinky_bonesL= ['pinkyik_01_L', 'pinkyik_02_L', 'pinkyik_03_L', 'pinkyCTRL_L']


scene_end = bpy.context.scene.frame_end

# Set the frame range for keyframing
frame_range = range(0, scene_end)  # Replace with your desired frame range

# Call the function to snap FK bones to their IK counterparts and keyframe them

# Call the function to snap FK bones to their IK counterparts and keyframe them
snapfinger_fk_to_ik(armature_name, fkthumb_bonesR, ikthumb_bonesR, frame_range)
snapfinger_fk_to_ik(armature_name, fkthumb_bonesL, ikthumb_bonesL, frame_range)

snapfinger_fk_to_ik(armature_name, fkindex_bonesR, ikindex_bonesR, frame_range)
snapfinger_fk_to_ik(armature_name, fkindex_bonesL, ikindex_bonesL, frame_range)

snapfinger_fk_to_ik(armature_name, fkmiddle_bonesR, ikmiddle_bonesR, frame_range)
snapfinger_fk_to_ik(armature_name, fkmiddle_bonesL, ikmiddle_bonesL, frame_range)


snapfinger_fk_to_ik(armature_name, fkring_bonesR, ikring_bonesR, frame_range)
snapfinger_fk_to_ik(armature_name, fkring_bonesL, ikring_bonesL, frame_range)

snapfinger_fk_to_ik(armature_name, fkpinky_bonesR, ikpinky_bonesR, frame_range)
snapfinger_fk_to_ik(armature_name, fkpinky_bonesL, ikpinky_bonesL, frame_range)


bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'

    
bpy.data.objects["root"].pose.bones["FKIK Switch"]["ArmIKFK_L"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["ArmIKFK_R"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["LegIKFK_L"] = 1
bpy.data.objects["root"].pose.bones["FKIK Switch"]["LegIKFK_R"] = 1





#Turn all layers visible
bpy.context.object.data.collections["Limbs Corrections"].is_visible = True
bpy.context.object.data.collections["Limbs FK"].is_visible = True
bpy.context.object.data.collections["Limbs IK"].is_visible = True
bpy.context.object.data.collections["Limbs IK Correction"].is_visible = True
bpy.context.object.data.collections["Spine Input"].is_visible = True
bpy.context.object.data.collections["Fingers FK"].is_visible = True
bpy.context.object.data.collections["Fingers IK"].is_visible = True
bpy.context.object.data.collections["Fingers Intermediate"].is_visible = True
bpy.context.object.data.collections["Unreal (Deform Rig)"].is_visible = True
bpy.context.object.data.collections["Intermediate Rig"].is_visible = True
bpy.context.object.data.collections["HeadCTRL"].is_visible = True
bpy.context.object.data.collections["Retarget Bones"].is_visible = True





# Create an empty list to store the filtered action names
filtered_action_names_list = []

print("Populating filtered list of Actions...")

# Iterate through all actions to build the filtered list first
for action in bpy.data.actions:
    action_name = action.name    
    # Check if the action name starts with 'SG ASL' or 'Reference'
    if not (action_name.startswith('SG ASL') or action_name.startswith('Reference')):
        # If it doesn't start with either, add it to our filtered list
        filtered_action_names_list.append(action_name)

print("\n--- Filtered Action List Created ---")
print(f"Total filtered actions found: {len(filtered_action_names_list)}")
print("Actions to be renamed:")
for name in filtered_action_names_list:
    print(name)

# --- RENAMING PART ---
print("\n--- Renaming Actions ---")
renamed_count = 0
for original_name in filtered_action_names_list:
    # Find the actual Action data block using its original name
    action_data_block = bpy.data.actions.get(original_name) 
    if action_data_block:
        base_new_name = Stamp + " " +original_name
        final_new_name = base_new_name.replace('_', ' ')
        # Rename the action data block
        action_data_block.name = final_new_name
        print(f"Renamed '{original_name}' to '{final_new_name}'")
        renamed_count += 1
    else:
        print(f"Warning: Action '{original_name}' not found. It might have been renamed or deleted externally.")

print(f"\n--- Renaming Complete. {renamed_count} actions renamed. ---")

# Optional: Verify the new names by printing all actions again
print("\n--- Current List of ALL Actions (after renaming) ---")
for action in bpy.data.actions:
    print(action.name)


for action in bpy.data.actions:
    action_name = action.name    
    # Check if the action name starts with 'SG ASL' or 'Reference'
    if not (action_name.endswith('ShapeKeys')):
        # If it doesn't start with either, add it to our filtered list
        filtered_action_names_list.append(action_name)


filtered_action_names_list = []
print(filtered_action_names_list)


#Use Pose Exporter by Bookyakuno, the layers from Animations as seperate CSV
#This is to potentially allow better research, and AI automation
#The AI automation is purely speculation at this point, but worth building in
for name in filtered_action_names_list:
    if name in bpy.data.actions:
        bpy.data.actions[name].pose_folder.select = True
    else:
        print(f"Warning: Action '{name}' not found in bpy.data.actions")
        
        
#
Decompose= Stamp+" Decompose.blend"
DecomposeExport=blend_file_dir+'\\'+Decompose
bpy.ops.pose_folder.pose_export(filepath=DecomposeExport, action='')

bpy.ops.pose_folder.batch_select_all(type='SELECT', obj_name="root")
for action in bpy.data.actions:
    action.pose_folder.select = False



BaseUpload= blend_file_dir+'\\'+ Stamp + ' CSV'

if not os.path.exists(BaseUpload):
    os.makedirs(BaseUpload)

#This adds labels to CSV for easier reading
axis_labels = {0: "X", 1: "Y", 2: "Z", 3: "W"}

scene = bpy.context.scene

filtered_actions = []


for action in bpy.data.actions:
    if action.name in filtered_actions:
        filtered_actions.append(action)

for action in filtered_actions:
    action_name = action.name
    csv_path = os.path.join(BaseUpload, f"{action_name}.csv")
    
    with open(csv_path, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header_row = ["Frame"]
        for fcurve in action.fcurves:
            bone_name = fcurve.data_path.split('"')[1]
            fcurve_name = fcurve.data_path.split('"')[2]
            if fcurve.array_index in axis_labels:
                label = axis_labels[fcurve.array_index]
            else:
                label = f"{fcurve.array_index}"
            header_row.append(f"{bone_name}-{fcurve_name}-{label}")
        csv_writer.writerow(header_row)
        
        for frame in range(int(action.frame_range[0]), int(action.frame_range[1]) + 1):
            row_data = [frame]
            
            for fcurve in action.fcurves:
                value = fcurve.evaluate(frame)
                row_data.append(value)
            
            csv_writer.writerow(row_data)

print("CSV export complete.")

#Now go use "Merge / Bake" in animation layers
#I recommend Anim layers, Merge, Down, and Merge/cyclic being checked.

##bpy.ops.anim.layers_merge_down()


#Done
scene_start=bpy.context.scene.frame_start
scene_end = bpy.context.scene.frame_end

bpy.ops.pose.select_all(action='SELECT')

bpy.ops.nla.bake(frame_start=scene_start, frame_end=scene_end, step=1, only_selected=True, visual_keying=False, clean_curves=False, bake_types={'POSE'})


def remove_all_anim_layers_descending():
    obj = bpy.context.object   
    if not obj or not hasattr(obj, 'als') or not hasattr(obj.als, 'layer_index'):
        print("Object doesn't have animation layer system")
        return   
    # Get the total number of layers (assuming layer_index.real gives us the count)
    total_layers = int(obj.als.layer_index.real) if hasattr(obj.als.layer_index, 'real') else 3  
    # Remove layers from highest index down to 0
    for layer_idx in range(total_layers-1, -1, -1):
        try:
            obj.als.layer_index = layer_idx
            bpy.ops.anim.remove_anim_layer()
            print(f"Removed animation layer {layer_idx}")
        except Exception as e:
            print(f"Failed to remove layer {layer_idx}: {e}")


remove_all_anim_layers_descending()



file_name = bpy.path.basename(bpy.context.blend_data.filepath)

ArchivePathblend=blend_file_dir+'\\' + file_name
Baked_Layer="Action"
StampAni=Stamp+" Animation"



new_name = {
    Baked_Layer:StampAni
}


for action in bpy.data.actions:
    if action.name in new_name:
        action.name = new_name [action.name]


armature_name = 'root'
armature = bpy.data.objects.get(armature_name)
if armature is None or armature.type != 'ARMATURE':
    print(f"Object '{armature_name}' not found or not an armature")
else:
    animation_data = armature.animation_data
    if animation_data is not None and animation_data.action is not None:
        action = animation_data.action
        action.name = StampAni
        print(f"Action renamed to: {action.name}")
    else:
        print("No action is currently assigned to the armature")
        
StampFinished=StampAni+" Finished"

# Dictionary mapping old names to new names
rename_map = {
    StampAni:StampFinished
}


for action in bpy.data.actions:
    if action.name in rename_map:
        action.name = rename_map[action.name]


#Use Pose Exporter by Bookyakuno, the layers from Animations as seperate CSV
#This is to potentially allow better research, and AI automation
#The AI automation is purely speculation at this point, but worth building in

bpy.data.actions[StampFinished].pose_folder.select = True


#

bpy.ops.pose_folder.batch_select_all(type='SELECT', obj_name="root")
for action in bpy.data.actions:
    action.pose_folder.select = False


BaseUpload= blend_file_dir+'\\'+ Stamp + ' CSV'

if not os.path.exists(BaseUpload):
    os.makedirs(BaseUpload)

#This adds labels to CSV for easier reading
axis_labels = {0: "X", 1: "Y", 2: "Z", 3: "W"}

scene = bpy.context.scene

filtered_actions = []

actions_to_filter = [StampAni]

for action in bpy.data.actions:
    if action.name in actions_to_filter:
        filtered_actions.append(action)

for action in filtered_actions:
    action_name = action.name
    csv_path = os.path.join(BaseUpload, f"{action_name}.csv")
    
    with open(csv_path, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header_row = ["Frame"]
        for fcurve in action.fcurves:
            bone_name = fcurve.data_path.split('"')[1]
            fcurve_name = fcurve.data_path.split('"')[2]
            if fcurve.array_index in axis_labels:
                label = axis_labels[fcurve.array_index]
            else:
                label = f"{fcurve.array_index}"
            header_row.append(f"{bone_name}-{fcurve_name}-{label}")
        csv_writer.writerow(header_row)
        
        for frame in range(int(action.frame_range[0]), int(action.frame_range[1]) + 1):
            row_data = [frame]
            
            for fcurve in action.fcurves:
                value = fcurve.evaluate(frame)
                row_data.append(value)
            
            csv_writer.writerow(row_data)

print("CSV export complete.")

rename_map = {
    StampFinished:StampAni
}


for action in bpy.data.actions:
    if action.name in rename_map:
        action.name = rename_map[action.name]

#Now go use "Merge / Bake" in animation layers
#I recommend Anim layers, Merge, Down, and Merge/cyclic being checked.


bpy.context.object.Anim_Layers[0].name = StampAni
#Done


