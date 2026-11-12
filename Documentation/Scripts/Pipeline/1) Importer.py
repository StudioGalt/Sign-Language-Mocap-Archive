import bpy
import os
import glob
import shutil 
import datetime

# Using Blender 5.2.1
# Last tested May 18, 2026 

# Set your Workspace with "U) 0 Set Working Directory"
blend_file_dir = os.path.dirname(bpy.data.filepath)


if "Reincarnation" in blend_file_dir:
    parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
else:
    # One parent directory
    parent_dir = os.path.dirname(blend_file_dir)
    

animation_dir = os.path.join(parent_dir, "Unprocessed Animations")
os.chdir(animation_dir)

# This pulls all FBX files in the working directory and 
directory = glob.glob('*.fbx')
RAWFBX = directory[0]
RAWFBXless = RAWFBX[:-4]
Split = RAWFBX.split('_')
Motion = Split[0]

# Get current date info
current_time = datetime.datetime.now()
Today = f"{current_time.year}-{current_time.month}-{current_time.day}"
Stamp = f"{Motion} {Today}"

# Create archive directory for file being worked
ArchivePath = os.path.join(parent_dir, Stamp)
os.makedirs(ArchivePath, exist_ok=True)


parent_dir_FBX = os.path.join(animation_dir, RAWFBX)
ArchivePathFBX = os.path.join(ArchivePath, RAWFBX)
shutil.move(parent_dir_FBX, ArchivePathFBX)

# Set file paths
ArchivePathblend = os.path.join(ArchivePath, f"{Stamp} Unedited.blend")

# Switch to object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Update rig properties, this adds notes to the Locator so if file animation is reused it can be tracked.
armature = bpy.data.objects['root']
bone = armature.pose.bones['Locator_Root']
file_path = bpy.path.basename(bpy.context.blend_data.filepath)
file_name = file_path[:-6]



#Delete the existing custom properties
bone_name = "Locator_Root"

# Get the active armature object
armature_obj = bpy.context.object

if armature_obj and armature_obj.type == 'ARMATURE':
    # Switch to Object mode if not already
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Remove custom properties from the pose bone
    if bone_name in armature_obj.pose.bones:
        pose_bone = armature_obj.pose.bones[bone_name]
        for prop in list(pose_bone.keys()):
            if prop not in "_RNA_UI":  # skip Blender internal keys
                del pose_bone[prop]
        if "_RNA_UI" in pose_bone.keys():
            del pose_bone["_RNA_UI"]

    # Remove custom properties from the edit bone
    bpy.ops.object.mode_set(mode='EDIT')
    if bone_name in armature_obj.data.edit_bones:
        edit_bone = armature_obj.data.edit_bones[bone_name]
        for prop in list(edit_bone.keys()):
            del edit_bone[prop]

    bpy.ops.object.mode_set(mode='POSE')  # or return to your preferred mode
else:
    print("Active object is not an armature.")


if armature_obj and armature_obj.type == 'ARMATURE':
    # Make sure we're in Pose Mode
    bpy.ops.object.mode_set(mode='POSE')

    pose_bone = armature_obj.pose.bones.get(bone_name)
    if pose_bone:
        pose_bone[file_name] = 0  # Set the custom property
        pose_bone[Today] = 0
        pose_bone[RAWFBXless] = 0
        print("Custom property added to pose bone.")
    else:
        print(f"Pose bone '{bone_name}' not found.")



# Switch to pose mode
bpy.ops.object.mode_set(mode='POSE')

# Purge existing actions, in case there are in the file
actions = bpy.data.actions
for action in actions:
    bpy.data.actions.remove(action)


bpy.ops.import_scene.fbx(filepath=ArchivePathFBX, automatic_bone_orientation=True)

bpy.data.objects["Reference"].select_set(True)

# Set frame rate to 60
bpy.context.scene.render.fps = 60

# Get frame range from imported motion
armature = bpy.data.objects['Reference']
action = armature.animation_data.action
frame_range = action.frame_range
last_frame = action.frame_range[1]



# Calculate bake time (converting to 60fps)
BT = int(last_frame // 4)

# Set up baking
bpy.ops.object.mode_set(mode='POSE')
bpy.context.scene.frame_end = BT
scene_end = bpy.context.scene.frame_end

# Bake animation at 60fps
bpy.ops.nla.bake(frame_start=1, frame_end=int(last_frame), step=4, clean_curves=True, bake_types={'POSE'})

# Add locator root to imported motion
armature = bpy.data.objects["Reference"]
bpy.ops.object.mode_set(mode='EDIT')

# Create new locator bone
new_bone = armature.data.edit_bones.new("Locator")
new_bone.head = (0, 0, 0)
new_bone.tail = (0, 25, 0)

# Parent hips to locator
arm = bpy.data.objects['Reference']
arm.data.edit_bones['Hips'].parent = arm.data.edit_bones['Locator']

# Set frame to beginning
bpy.context.scene.frame_set(0)
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')


obj = bpy.context.active_object
anim_data = obj.animation_data
action = anim_data.action

new_start_frame = bpy.context.scene.frame_start
new_end_frame = bpy.context.scene.frame_end

#The following grabs every fcurve and resizes them to Length.
#action.layers[0].strips[0].channelbag(action.slots[0]).fcurves

for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
    for kf in fcurve.keyframe_points:
        kf.co[0] = ((kf.co[0] - action.frame_range[0]) / (action.frame_range[1] - action.frame_range[0])) * (new_end_frame - new_start_frame) + new_start_frame

action.frame_range = (1, BT)

bpy.context.scene.frame_preview_end =BT

# Fix thumb rotations
bpy.data.objects["Reference"].select_set(True)
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='DESELECT')

# Helper function to select and rotate thumbs
def process_thumb_bones(bone_names, rotation_value):
    # Select the bones
    for bone_name in bone_names:
        try:
            bpy.data.objects['Reference'].data.bones[bone_name].select = True
        except KeyError:
            print(f"Bone '{bone_name}' not found. Skipping...")
        except Exception as e:
            print(f"An error occurred while selecting bone '{bone_name}': {e}. Skipping...")
    
    # Set pivot point to active element
    bpy.context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
    
    # Rotate in edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.rotate(value=rotation_value, orient_axis='Y', orient_type='LOCAL', 
                           orient_matrix=((1, 0, 0), (0, 0, 1), (0, -1, 0)), 
                           orient_matrix_type='LOCAL', constraint_axis=(False, True, False))
    
    bpy.ops.transform.transform(mode='BONE_ROLL', value=(1.15472, 0, 0, 0), 
                              orient_axis='Z', orient_type='LOCAL', 
                              orient_matrix=((1, 0, 0), (0, 0, 1), (0, -1, 0)), 
                              orient_matrix_type='LOCAL')
    
    # Return to pose mode and deselect
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')

# Process right and left thumbs
right_bone_names = ['RightHandThumb3', 'RightHandThumb2', 'RightHandThumb1']
process_thumb_bones(right_bone_names, 0.523599)  # ~30 degrees

left_bone_names = ['LeftHandThumb3', 'LeftHandThumb2', 'LeftHandThumb1']
process_thumb_bones(left_bone_names, -0.523599)  # ~-30 degrees

# Reset transform pivot point
bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

#Set the animation to be in front
bpy.context.object.show_in_front = True

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=ArchivePathblend)
