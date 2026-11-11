import bpy
import subprocess
import shutil
import os
import sys
import importlib
import glob


# Using Blender 5.1.1
# Last tested May 24,  2025 



def set_bone_length(armature, bone_name, length):
    if bone_name in armature.edit_bones:
        bone = armature.edit_bones[bone_name]
        current_vector = bone.vector
        if current_vector.length != 0:
            new_vector = current_vector.normalized() * length
            bone.tail = bone.head + new_vector
        else:
            print(f"Warning: Bone '{bone_name}' has zero length. Cannot set new length.")
    else:
        print(f"Warning: Bone '{bone_name}' not found in the armature.")


def add_copy_transform_constraint_world(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'WORLD'
    constraint.owner_space = 'WORLD'



def keyframe_constraint_influence_1(bone):
    for constraint in bone.constraints:
        constraint.influence = 1.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")




def keyframe_constraint_influence(bone):
    for constraint in bone.constraints:
        constraint.influence = 0.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")


def add_copy_transform_constraint_world(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'WORLD'
    constraint.owner_space = 'WORLD'


def keyframe_constraint_influence_1(bone):
    for constraint in bone.constraints:
        constraint.influence = 1.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



#
def keyframe_constraint_influence_0(bone):
    for constraint in bone.constraints:
        constraint.influence = 0.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")


def add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'POSE'
    constraint.owner_space = 'POSE'



def keyframe_constraint_influence_1(bone):
    for constraint in bone.constraints:
        constraint.influence = 1.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



#
def keyframe_constraint_influence_0(bone):
    for constraint in bone.constraints:
        constraint.influence = 0.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



def set_bone_length(armature, bone_name, length):
    if bone_name in armature.edit_bones:
        bone = armature.edit_bones[bone_name]
        current_vector = bone.vector
        if current_vector.length != 0:
            new_vector = current_vector.normalized() * length
            bone.tail = bone.head + new_vector
        else:
            print(f"Warning: Bone '{bone_name}' has zero length. Cannot set new length.")
    else:
        print(f"Warning: Bone '{bone_name}' not found in the armature.")



def add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'WORLD'
    constraint.owner_space = 'WORLD'



def keyframe_constraint_influence_1(bone):
    for constraint in bone.constraints:
        constraint.influence = 1.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



#
def keyframe_constraint_influence_0(bone):
    for constraint in bone.constraints:
        constraint.influence = 0.0
        constraint.keyframe_insert("influence")
        print(f"Keyframed influence for constraint '{constraint.name}' on bone '{bone.name}'")



def delete_keyframes_at_frame(target_obj, frame_number):
    """
    Deletes all keyframes on a specific frame for the given object
    using the Blender 4.4+ Layered Action API.
    """
    # 1. Safety check for animation data
    if not (target_obj and target_obj.animation_data and target_obj.animation_data.action):
        print(f"Object '{target_obj.name}' has no active action.")
        return

    action = target_obj.animation_data.action
    slot = target_obj.animation_data.action_slot
    
    # 2. Navigate the Layered Action hierarchy
    # We use a loop for layers/strips to ensure we catch all layered data
    if slot and action.layers:
        for layer in action.layers:
            for strip in layer.strips:
                channelbag = strip.channelbag(slot)
                
                if not channelbag:
                    continue
                    
                for fcurve in channelbag.fcurves:
                    points = fcurve.keyframe_points
                    # Iterate backwards to safely remove items from the collection
                    for i in range(len(points) - 1, -1, -1):
                        kp = points[i]
                        
                        if abs(kp.co.x - frame_number) < 0.1:
                            points.remove(kp)
    
    # 3. Trigger UI Redraw
    for area in bpy.context.screen.areas:
        if area.type in {'DOPESHEET_EDITOR', 'GRAPH_EDITOR'}:
            area.tag_redraw()




blend_file_dir = os.path.dirname(bpy.data.filepath)

if "Reincarnation" in blend_file_dir:
    # Parent's parent directory
    parent_dir = os.path.dirname(os.path.dirname(blend_file_dir))
else:
    # One parent directory
    parent_dir = os.path.dirname(blend_file_dir)


script_path = os.path.join(parent_dir, "Scripts")

if script_path not in sys.path:
    sys.path.append(script_path)

import pose_magic_lib
importlib.reload(pose_magic_lib)






#Grab all hair strands
#These hair strands were created with Pro Stylized Hair v3 by Dean Zarkov.
#You can buy it on Gumroad.
bpy.context.object.Anim_Layers[0].lock = False

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')


bpy.data.objects["Strand.001"].select_set(True)
bpy.data.objects["Strand.002"].select_set(True)
bpy.data.objects["Strand.003"].select_set(True)
bpy.data.objects["Strand.006"].select_set(True)
bpy.data.objects["Strand.007"].select_set(True)
bpy.data.objects["Strand.008"].select_set(True)


#Convert them to a Mesh
bpy.ops.object.convert(target='MESH')

# List of object names you want to apply the material to
object_names = ["Strand.001", "Strand.002", "Strand.003","Strand.006", "Strand.007","Strand.008"]
     

material_name = "Blender_Orange"
if material_name in bpy.data.materials:
    material = bpy.data.materials[material_name]
else:
    material = bpy.data.materials.new(name=material_name)
    material.diffuse_color = (0.8, 0.1, 0.1, 1)  # RGBA: Red color for demonstration

# Ensure we're in Object mode
bpy.ops.object.mode_set(mode='OBJECT')

for object_name in object_names:
    # Ensure the object exists
    if object_name in bpy.data.objects:
        bpy.data.objects[object_name].select_set(True)
        # Make it the active object
        bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
        obj = bpy.context.active_object
        # Assign the material to the first material slot or create a new slot
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material) 
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.material_slot_assign()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects[object_name].select_set(False)

# Return to the default active object or deselect all, if desired

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')


bpy.data.objects["Strand.001"].select_set(True)
bpy.data.objects["Strand.002"].select_set(True)
bpy.data.objects["Strand.003"].select_set(True)
bpy.data.objects["Strand.006"].select_set(True)
bpy.data.objects["Strand.007"].select_set(True)
bpy.data.objects["Strand.008"].select_set(True)
#the last selected as active object

bpy.ops.object.join()

bpy.ops.object.select_all(action='DESELECT')


object_name = "Strand.008"

#Reduce the mesh size. 0.05 is chosen to ensure outputted files are under 25mbs for reposting on github.
decimation_ratio = 0.05

# Get a reference to the mesh object by name
obj = bpy.data.objects.get(object_name)

if obj is not None and obj.type == 'MESH':
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.decimate(ratio=decimation_ratio)
    bpy.ops.object.mode_set(mode='OBJECT')
else:
    print(f"Mesh object '{object_name}' not found in the scene.")

#Create name cliche
file_name = bpy.path.basename(bpy.context.blend_data.filepath)
fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
print(Stamp)


Mesh=Stamp + " Mesh.fbx"

Meshfbx=blend_file_dir+'\\'+ Mesh


bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
#Deselect everything, then select body, Head, Hair, and Armature for export. 

bpy.data.objects["Strand.008"].select_set(True)
bpy.data.objects["GaltisBody"].select_set(True)
bpy.data.objects["GaltisHead"].select_set(True)
bpy.data.objects["root"].select_set(True)

#Now we create and export a video.
bpy.context.scene.frame_set(0)

armature = bpy.data.objects['root']
action = armature.animation_data.action

frame_range = action.frame_range
print(frame_range)

lf = int(action.frame_range[1])
last_frame=lf+15


scene = bpy.context.scene
scene.frame_end = last_frame
scene_end=int(scene.frame_end)


scene.use_preview_range = True
scene.frame_preview_start = 0
scene.frame_preview_end = lf



bpy.ops.export_scene.fbx(filepath=Meshfbx, check_existing=True, use_selection=True, use_visible=False, object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False, use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_force_startend_keying=False, path_mode='COPY')


frame_start= int(action.frame_range[0])
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = last_frame



bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

#We add 15 frames to make looping appear smoother


bpy.context.scene.render.image_settings.media_type = 'VIDEO'
bpy.context.scene.render.ffmpeg.format = 'WEBM'


bpy.context.scene.render.filepath = blend_file_dir


bpy.context.scene.camera = bpy.data.objects['Camera']
VideoWEBM=blend_file_dir+'\\'+ Stamp + ".webm"



webm_files = glob.glob(os.path.join(blend_file_dir, "*.webm"))
for webm_file in webm_files:
    try:
        os.remove(webm_file)
        print(f"Deleted: {webm_file}")
    except Exception as e:
        print(f"Error deleting {webm_file}: {e}")






bpy.context.scene.render.ffmpeg.format = 'WEBM'
bpy.context.scene.render.ffmpeg.codec = 'WEBM'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

bpy.context.scene.render.fps = 60
bpy.ops.render.render(animation=True)


if len(str(last_frame)) == 4:
    webm = "0001-" + str(last_frame) + ".webm"
elif len(str(last_frame)) == 3:
    webm = "0001-0" + str(last_frame) + ".webm"
elif len(str(last_frame))  == 2:
    webm = "0001-00" + str(last_frame) + ".webm"
elif len(str(last_frame))  == 1:
    webm = "0001-000" + str(last_frame) + ".webm"
        

WEBM1=blend_file_dir+webm


StampWEBM=blend_file_dir+'\\'+Stamp+".webm"
os.rename(WEBM1, StampWEBM)


stampwebm=Stamp+".webm"

file_name = stampwebm
directory = "//" 
filepath = directory + file_name

# 2. Find the Video Sequencer Area in your current screen
area = None
for window in bpy.context.window_manager.windows:
    for a in window.screen.areas:
        if a.type == 'SEQUENCE_EDITOR':
            area = a
            break

# 3. Run the operator with the overridden context
if area:
    with bpy.context.temp_override(area=area):
        bpy.ops.sequencer.movie_strip_add(
            filepath=filepath,
            directory=directory,
            files=[{"name": file_name}], # Fixed the dictionary syntax here
            show_multiview=False,
            frame_start=frame_start,
            channel=1,
            fit_method='FIT',
            set_view_transform=False,
            adjust_playback_rate=True,
            use_framerate=False
        )
    print("Strip added successfully.")
else:
    print("Error: Could not find a Video Sequencer area. Please open one.")
    
 
area = None
for window in bpy.context.window_manager.windows:
    for a in window.screen.areas:
        if a.type == 'SEQUENCE_EDITOR':
            area = a
            break

if area:
    # 2. Context Override
    with bpy.context.temp_override(area=area):
        # OPTIONAL: Deselect everything first to avoid "context" confusion
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.effect_strip_add(type='TEXT', 
            move_strips=True, 
            frame_start=frame_start, 
            length=last_frame, 
            channel=3, 
            replace_sel=True, 
            overlap=False, 
            overlap_shuffle_override=False, 
            skip_locked_or_muted_channels=True, 
            color=(0, 0, 0)
        )
        
    print("Effect strip added.")
else:
    print("Video Sequencer area not found.") 
 
    
bpy.context.active_strip.location[1] = 0.8
bpy.context.active_strip.font_size = 80


bpy.context.active_strip.text = Stamp

bpy.context.active_strip.blend_alpha = 1
bpy.ops.font.open(filepath="//..\\..\\..\\..\\..\\..\\WINDOWS\\Fonts\\arial.ttf", relative_path=True)




    
bpy.context.scene.render.image_settings.color_mode = 'RGBA'
bpy.context.scene.render.film_transparent = True

bpy.ops.render.render(animation=True)



bpy.context.scene.render.filepath = blend_file_dir


VideoWEBM=blend_file_dir+'\\'+ Stamp + ".webm"



if len(str(last_frame)) == 4:
    webm = "0001-" + str(last_frame) + ".webm"
elif len(str(last_frame)) == 3:
    webm = "0001-0" + str(last_frame) + ".webm"
elif len(str(last_frame))  == 2:
    webm = "0001-00" + str(last_frame) + ".webm"
elif len(str(last_frame))  == 1:
    webm = "0001-000" + str(last_frame) + ".webm"
        

WEBM1=blend_file_dir+webm


StampWEBM=blend_file_dir+'\\'+Stamp+" Captions.webm"
os.rename(WEBM1, StampWEBM)
scene.frame_end -= 15


    
    


#Does not hurt to save the file, we grab the finished blend file and store in a pose storage, folder so we can grab poses more easily
ArchivePathblend=blend_file_dir+'\\' + Stamp + ' Finished.blend'




PoseStorage=parent_dir+'\\Storage\\Galtis'


AnimationStorage=PoseStorage+'\\'+ Stamp + ' Finished.blend'

shutil.copyfile(ArchivePathblend, AnimationStorage)




AnimStamp=Stamp +" Animation"


#The following use Pose Exporter by Bookyakuno
bpy.ops.pose_folder.batch_select_all(type='SELECT', obj_name="root")
for action in bpy.data.actions:
    action.pose_folder.select = True

ShapekeyStamp=Stamp +" ShapeKeys"
bpy.data.actions[AnimStamp].pose_folder.select = False
if ShapekeyStamp in bpy.data.actions and hasattr(bpy.data.actions[ShapekeyStamp], "pose_folder"):
    bpy.data.actions[ShapekeyStamp].pose_folder.select = False
# If no shape keys or the specific action doesn't exist, skip this step
else:
    pass


#
Poses= Stamp+" Poses.blend"
PoseExport=blend_file_dir+'\\'+Poses
bpy.ops.pose_folder.pose_export(filepath=PoseExport, action='')

bpy.ops.pose_folder.batch_select_all(type='SELECT', obj_name="root")
for action in bpy.data.actions:
    action.pose_folder.select = False

bpy.data.actions[AnimStamp].pose_folder.select = True

#This exports the animation to a individual blend file for appending purposes.
AnimOnly= Stamp+" Anim Only.blend"


AnimOnlyExport=blend_file_dir+'\\'+AnimOnly
bpy.ops.pose_folder.pose_export(filepath=AnimOnlyExport, action='')

actions = bpy.data.actions

# Create a list of actions to be removed
actions_to_remove = [action for action in actions if not action.name.endswith("Animation")]

for action in actions_to_remove:
    bpy.data.actions.remove(action)
    
    
#We are done with meshes at this point so, delete them
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects["GaltisBody"].select_set(True)
bpy.data.objects["GaltisHead"].select_set(True)
bpy.data.objects["Strand.008"].select_set(True)
bpy.ops.object.delete(use_global=False)


armature = bpy.data.objects['root']


bpy.data.objects["root"].select_set(True)
object_name = 'root'
object_to_set_active = bpy.data.objects.get(object_name)
if object_to_set_active:
    bpy.context.view_layer.objects.active = object_to_set_active
else:
    print(f"Object '{object_name}' not found in the scene.")


object_name = 'root'
object_to_set_active = bpy.data.objects.get(object_name)
if object_to_set_active:
    bpy.context.view_layer.objects.active = object_to_set_active
else:
    print(f"Object '{object_name}' not found in the scene.")


#We update root to animation name then mark as asset and save in animation folder

old_armature_name = 'root'
new_armature_name = AnimStamp
armature_object = bpy.data.objects.get(old_armature_name)
if armature_object and armature_object.type == 'ARMATURE':
    armature_object.name = new_armature_name
    armature_object.data.name = new_armature_name
    print(f"Armature '{old_armature_name}' renamed to '{new_armature_name}'.")
else:
    print(f"Armature '{old_armature_name}' not found or is not of type 'ARMATURE'.")


bpy.data.objects[AnimStamp].asset_mark()



AnimStorage=parent_dir+'\\'+'Storage\\Animation'+'\\'+ Stamp + ' Animation.blend'

bpy.ops.wm.save_as_mainfile(filepath=AnimStorage)

AnimStorageII=blend_file_dir+'\\'+Stamp + ' Animation.blend'
bpy.ops.wm.save_as_mainfile(filepath=AnimStorageII)
object_name = AnimStamp
object_to_set_active = bpy.data.objects.get(object_name)
if object_to_set_active:
    bpy.context.view_layer.objects.active = object_to_set_active
else:
    print(f"Object '{object_name}' not found in the scene.")

#Don't fdrget to convert it back
old_armature_name = AnimStamp
new_armature_name = 'root'
armature_object = bpy.data.objects.get(old_armature_name)
if armature_object and armature_object.type == 'ARMATURE':
    # Change the armature object's name
    armature_object.name = new_armature_name
    # Change the armature data's name (if it's different from the object's name)
    armature_object.data.name = new_armature_name
    print(f"Armature '{old_armature_name}' renamed to '{new_armature_name}'.")
else:
    print(f"Armature '{old_armature_name}' not found or is not of type 'ARMATURE'.")


