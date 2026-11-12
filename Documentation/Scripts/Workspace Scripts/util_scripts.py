import bpy

def toggle_collections_visibility(set_visible=True):
    """
    Toggle visibility for all bone collections in the active armature.
    
    Args:
        set_visible (bool): If True, makes all collections visible. 
                           If False, hides all collections.
    """
    obj = bpy.context.object
    
    # Safety check: Ensure object is an Armature
    if not obj or obj.type != 'ARMATURE':
        print("Error: Active object is not an Armature.")
        return
    
    # Loop through all bone collections
    for collection in obj.data.collections_all:
        collection.is_visible = set_visible
    
    action = "visible" if set_visible else "hidden"
    print(f"All bone collections have been set to {action}.")

# --- Execute ---
# Set to True to make all collections visible
#toggle_collections_visibility(set_visible=False)





def toggle_solo_collections(set_solo=False):
    """
    Toggle solo state for all bone collections in the active armature.
    
    Args:
        set_solo (bool): If True, sets all collections to solo. 
                        If False, removes solo from all collections.
    """
    obj = bpy.context.object
    
    # Safety check: Ensure object is an Armature
    if not obj or obj.type != 'ARMATURE':
        print("Error: Active object is not an Armature.")
        return
    
    # Loop through all bone collections
    for collection in obj.data.collections_all:
        collection.is_solo = set_solo
    
    action = "soloed" if set_solo else "un-soloed"
    print(f"All bone collections have been {action}.")


#toggle_solo_collections(set_solo=False)

def setup_als_layer(target_name="root", layer_name="Base_Layer", layer_index=0):
    """
    Enables ALS on the target object and initializes the Animation Layer.
    
    Args:
        target_name (str): The name of the object to target (default: "root").
        layer_name (str): The name to give the animation layer.
        layer_index (int): The index of the layer to rename (default: 0).
    """
    # Check if object exists
    if target_name not in bpy.data.objects:
        print(f"Error: Object '{target_name}' not found.")
        return

    obj = bpy.data.objects[target_name]
    bpy.context.view_layer.objects.active = obj
    
    #I refuse to count 0.

    
    if hasattr(obj, "als"):
        obj.als.turn_on = True
    else:
        print(f"Warning: '{target_name}' does not have an 'als' property.")
    count = len(obj.Anim_Layers)
    if count < layer_index:
        layer_index = count
    else:
        layer_index = layer_index
    if count > 0:
        pass
    else:
        bpy.ops.anim.add_anim_layer()
        
    if layer_index > 0:
        layer_index=layer_index-1
    else:
        layer_index=0
    # 2. Reset Selection in Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    # 3. Add Animation Layer in Pose Mode
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.object.als.layer_index = (layer_index)
    try:
        # Add a new layer
        bpy.ops.anim.add_anim_layer()
        # 4. Rename the specific layer index
        if hasattr(obj, "Anim_Layers"):
            # Ensure the index exists before trying to access it
            if len(obj.Anim_Layers) > layer_index:
                obj.Anim_Layers[layer_index+1].name = layer_name
                bpy.context.object.als.layer_index = (layer_index+1)
            else:
                print(f"Error: Layer index {layer_index} is out of range. Total layers: {len(obj.Anim_Layers)}")
                
    except AttributeError:
        print("Error: 'Animation Layers' addon does not seem to be installed or enabled.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def keyframe_rig_with_als(rig_name="Galtis_Rig", first_anchor=None, last_anchor=None):
    """
    Keyframes a rig with ALS enabled at frame 0, start, and end frames.
    
    Args:
        rig_name: Name of the rig object to keyframe
        first_anchor: Frame number to set as the starting keyframe (default: scene.frame_start)
        last_anchor: Frame number to set as the ending keyframe (default: scene.frame_end)
    """
    scene = bpy.context.scene
    
    # Use scene defaults if not specified
    if first_anchor is None:
        first_anchor = scene.frame_start
    if last_anchor is None:
        last_anchor = scene.frame_end
    
    # Switch to object mode and select the rig
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects[rig_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[rig_name]
    
    # Enable ALS
    bpy.context.object.als.turn_on = True
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    
    # Keyframe at frame 0
    scene.frame_set(0)
    bpy.ops.anim.keyframe_insert_by_name(type="LocRotScale")
    
    # Keyframe at start frame
    scene.frame_set(first_anchor)
    bpy.ops.anim.keyframe_insert_by_name(type="LocRotScale")
    
    # Keyframe at end frame
    scene.frame_set(last_anchor)
    bpy.ops.anim.keyframe_insert_by_name(type="LocRotScale")

# Usage examples:
# Use scene's frame range:
#keyframe_rig_with_als("root", first_anchor=110, last_anchor=223)



def _get_today_string(self) -> str:
    """Get today's date as a formatted string"""
    current_time = datetime.datetime.now()
    return f"{current_time.year}-{current_time.month}-{current_time.day}"
    
def get_sorted_markers(self) -> list:
    """Get timeline markers sorted by frame"""
    return sorted(bpy.context.scene.timeline_markers, key=lambda marker: marker.frame)

def jump_to_next_marker(self, sorted_markers: list) -> bool:
    """Jump to the next marker in the timeline"""
    current_frame = bpy.context.scene.frame_current
    for marker in sorted_markers:
        if marker.frame > current_frame:
            bpy.context.scene.frame_set(marker.frame)
            print(f"Jumped to marker '{marker.name}' at frame {marker.frame}")
            return True
        
    print("No next marker found")
    return False
    
def get_armature(self):
    """Get the target armature object"""
    armature = bpy.data.objects.get(self.armature_name)
    if not armature or armature.type != 'ARMATURE':
        print(f"Armature '{self.armature_name}' not found or is not an armature")
        return None
    return armature

def export_json_data(self, pose_name: str) -> bool:
    """Export armature data as JSON compatible with Jason Pose Manager"""
    armature = self.get_armature()
    if not armature:
       return False
        
    pose_name_cleaned = pose_name.replace("(", "").replace(")", "")
        
    armature_data = {
        "addon": "jpm",
        "name": pose_name_cleaned,
        "def_limbs": [None] * 8,
        "bones": []
        }
                # Export bone data
    for bone in armature.pose.bones:
        bone_data = {
            "name": bone.name,
            "location": {"vector": list(bone.location)},
            "rotation": {"vector": list(bone.rotation_quaternion), "mode": "QUATERNION"},
            "scale": {"vector": list(bone.scale)}
            }
        armature_data["bones"].append(bone_data)
        
        if not self.output_dir:
            print("Cannot determine export directory")
            return False
        
        pose_name_underline = pose_name_cleaned.replace(" ", "_")
        filename = f"jpm_{pose_name_underline}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, "w") as outfile:
                json.dump([armature_data], outfile, indent=2)
            print(f"Successfully exported JSON to: {filepath}")
            return True
        except Exception as e:
            print(f"Error exporting JSON to {filepath}: {e}")
            return False
    
def export_csv_data(self, pose_name: str) -> bool:
    """Export bone rotation data as CSV file"""
    armature = self.get_armature()
    if not armature:
        return False

    if bpy.context.mode != 'POSE':
        print("Not in pose mode, cannot export bone rotations")
        return False

    pose_name_cleaned = pose_name.replace("(", "").replace(")", "")

    # Collect bones
    selected_bones = [
        armature.pose.bones[bn]
        for bn in self.bone_names
        if bn in armature.pose.bones
        ]

    if not selected_bones:
        print("No target bones found for export")
        return False

        # Frame budget
    current_frame = bpy.context.scene.frame_current
    markers = bpy.context.scene.timeline_markers
    previous_markers = [m for m in markers if m.frame < current_frame]

    if previous_markers:
        previous_marker = max(previous_markers, key=lambda m: m.frame)
        frame_budget = current_frame - previous_marker.frame
    else:
        frame_budget = current_frame
    
    if not self.output_dir:
        print("Cannot determine export directory")
        return False

    filename = f"{pose_name_cleaned}.csv"
    filepath = os.path.join(self.output_dir, filename)

    try:
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Metadata block
            writer.writerow(["motion_name", self.file_info['stamp']])
            writer.writerow(["pose_name", pose_name_cleaned])
            writer.writerow(["export_date", self.today])
            writer.writerow(["current_frame", current_frame])
            writer.writerow(["frame_budget", frame_budget])
            writer.writerow([])

                # CSV header
            writer.writerow(["bone_name", "w", "x", "y", "z"])

                # Bone rotations
            for bone in selected_bones:
                if bone.rotation_mode == 'QUATERNION':
                    rot = bone.rotation_quaternion
                elif bone.rotation_mode == 'AXIS_ANGLE':
                    rot = bone.rotation_axis_angle
                else:
                    rot = bone.rotation_euler.to_quaternion()

                writer.writerow([
                    bone.name,
                    round(rot.w, 4),
                    round(rot.x, 4),
                    round(rot.y, 4),
                    round(rot.z, 4),
                    ])

            print(f"Successfully exported CSV to: {filepath}")
            return True

    except Exception as e:
        print(f"Error writing CSV data to {filepath}: {e}")
        return False

def create_pose_asset(self, pose_name: str) -> bool:
    """Create a pose asset from the current pose"""
    armature = self.get_armature()
    if not armature:
        return False
        
    # Ensure we're in the right context
    bpy.context.view_layer.objects.active = armature
    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
            
    bpy.ops.pose.select_all(action='SELECT')
        
    try:
        bpy.ops.poselib.create_pose_asset(
                pose_name=pose_name,
                asset_library_reference='LOCAL',
                catalog_path=""
            )
            
            # Set asset metadata
        if pose_name in bpy.data.actions:
            action = bpy.data.actions[pose_name]
            action.name = pose_name
                
            current_frame = bpy.context.scene.frame_current
            action.asset_data.author = "Studio Galt Mocap"
            action.asset_data.description = str(current_frame)
            action.asset_data.copyright = "CC0"
                
            print(f"Successfully created pose asset: {pose_name}")
            return True
        else:
            print(f"Warning: Exact name '{pose_name}' not found immediately after creation.")
            return True
                
    except Exception as e:
        print(f"Error creating pose asset '{pose_name}': {e}")
        return False
    
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

'''
fkleg_bonesR = ['thighfk_R', 'shinfk_R', 'footfk_R']
ikleg_bonesR = ['thighik_R', 'shinik_R', 'footik_R']
fkleg_bonesL = ['thighfk_L', 'shinfk_L', 'footfk_L']
ikleg_bonesL = ['thighik_L', 'shinik_L', 'footik_L']

snap_fk_to_ik(armature_name, fkleg_bonesR, ikleg_bonesR, frame_range)
snap_fk_to_ik(armature_name, fkleg_bonesL, ikleg_bonesL, frame_range)
'''
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




def add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'POSE'
    constraint.owner_space = 'POSE'




def keyframe_constraint_influence(bone, influence=1.0):
    for constraint in bone.constraints:
        constraint.influence = influence
        constraint.keyframe_insert(data_path="influence")
        print(
            f"Keyframed influence {influence} for constraint "
            f"'{constraint.name}' on bone '{bone.name}'"
            )
        




def delete_keyframes_at_frame(target_obj, frame_number):
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

# --- HOW TO USE ---
# Example: Delete keyframes on frame 80 for the active object
#active_obj = bpy.context.active_object
#delete_keyframes_at_frame(active_obj, 70)
#delete_keyframes_at_frame(active_obj, 72)




def setup_and_rename_armature(target_name, new_name):
    """
    Sets an object as active and renames both the object 
    and its underlying data block.
    """
    obj = bpy.data.objects.get(target_name)
    if not obj:
        print(f"Error: Object '{target_name}' not found.")
        return False

    # 2. Set as Active
    bpy.context.view_layer.objects.active = obj

    if obj.type == 'ARMATURE':
        old_name = obj.name
        obj.name = new_name

        if obj.data:
            obj.data.name = new_name
            
        print(f"Success: '{old_name}' renamed to '{new_name}'.")
        return True
    else:
        print(f"Object '{target_name}' found, but it is a {obj.type}, not an ARMATURE.")
        return False


##setup_and_rename_armature("MyNewAnimationName", 'root')




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




def add_copy_transform_constraint_pose(source_bone, target_armature, target_bone_name):
    constraint = source_bone.constraints.new(type='COPY_ROTATION')
    constraint.target = target_armature
    constraint.subtarget = target_bone_name
    constraint.target_space = 'POSE'
    constraint.owner_space = 'POSE'




def keyframe_constraint_influence(bone, influence=1.0):
    for constraint in bone.constraints:
        constraint.influence = influence
        constraint.keyframe_insert(data_path="influence")
        print(
            f"Keyframed influence {influence} for constraint "
            f"'{constraint.name}' on bone '{bone.name}'"
            )
        




def delete_keyframes_at_frame(target_obj, frame_number):
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



import bpy
import os

def get_stamp():
    """
    Extracts the current .blend filename and removes the last segment
    to create a clean string 'stamp'.
    """
    # Get the filename (e.g., "Character_Model_v01.blend")
    file_path = bpy.data.filepath
    
    if not file_path:
        return "Unsaved_File"

    file_name = bpy.path.basename(file_path)
    
    # Remove the .blend extension first to avoid it being part of the last segment
    name_no_ext = os.path.splitext(file_name)[0]
    
    # Split by whitespace
    fnsplit = name_no_ext.split()
    
    if len(fnsplit) > 1:
        # Join everything except the last element
        stamp = " ".join(fnsplit[:-1])
    else:
        # Fallback if the filename is only one word
        stamp = fnsplit[0]
        
    return stamp

# Example usage:
#my_stamp = get_stamp()
#print(my_stamp)


import bpy
import os

def export_bone_lengths_to_file(filename="bone_lengths_report.txt"):
    # Determine the directory of the current blend file
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    
    # Fallback to user's home directory if the blend file hasn't been saved yet
    if not directory:
        directory = os.path.expanduser("~")
        
    full_path = os.path.join(directory, filename)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("BONE LENGTHS REPORT\n")
            f.write("=" * 40 + "\n")
            
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE':
                    f.write(f"\nArmature: {obj.name}\n")
                    f.write("-" * 20 + "\n")
                    
                    # Accessing the edit/rest bone data
                    for bone in obj.data.bones:
                        f.write(f"{bone.name}: {bone.length:.6f}\n")
            
            f.write("\nEnd of Report")
            
        print(f"Report successfully saved to: {full_path}")
        # Optional: Show a message in the Blender UI
        # self.report({'INFO'}, f"Saved to {full_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    export_bone_lengths_to_file()



import bpy
import os

def export_filtered_bone_lengths_filtered(filename="bone_lengths_manny.txt"):
    # The list of bones you want to include
    target_bones = {
        "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", 
        "neck_01", "neck_02", "head", "clavicle_l", "upperarm_l", "lowerarm_l", 
        "lowerarm_twist_02_l", "lowerarm_twist_01_l", "hand_l", "middle_metacarpal_l", 
        "middle_01_l", "middle_02_l", "middle_03_l", "pinky_metacarpal_l", 
        "pinky_01_l", "pinky_02_l", "pinky_03_l", "ring_metacarpal_l", "ring_01_l", 
        "ring_02_l", "ring_03_l", "thumb_01_l", "thumb_02_l", "thumb_03_l", 
        "index_metacarpal_l", "index_01_l", "index_02_l", "index_03_l", 
        "upperarm_twist_01_l", "upperarm_twist_02_l", "clavicle_r", "upperarm_r", 
        "lowerarm_r", "lowerarm_twist_02_r", "lowerarm_twist_01_r", "hand_r", 
        "middle_metacarpal_r", "middle_01_r", "middle_02_r", "middle_03_r", 
        "pinky_metacarpal_r", "pinky_01_r", "pinky_02_r", "pinky_03_r", 
        "ring_metacarpal_r", "ring_01_r", "ring_02_r", "ring_03_r", "thumb_01_r", 
        "thumb_02_r", "thumb_03_r", "index_metacarpal_r", "index_01_r", "index_02_r", 
        "index_03_r", "upperarm_twist_01_r", "upperarm_twist_02_r", "thigh_r", 
        "calf_r", "foot_r", "ball_r", "calf_twist_02_r", "calf_twist_01_r", 
        "thigh_twist_01_r", "thigh_twist_02_r", "thigh_l", "calf_l", "foot_l", 
        "ball_l", "calf_twist_02_l", "calf_twist_01_l", "thigh_twist_01_l", 
        "thigh_twist_02_l", "ik_foot_root", "ik_foot_l", "ik_foot_r", "ik_hand_root", 
        "ik_hand_gun", "ik_hand_l", "ik_hand_r", "interaction", "center_of_mass"
    }

    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    
    if not directory:
        directory = os.path.expanduser("~")
        
    full_path = os.path.join(directory, filename)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("bone_lengths_manny = {\n")
            
            # Find the active armature or the first one available
            armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
            
            for obj in armatures:
                f.write(f"    # From Armature: {obj.name}\n")
                
                # Filter bones
                found_bones = []
                for bone in obj.data.bones:
                    if bone.name in target_bones:
                        found_bones.append(f'    "{bone.name}": {bone.length:.6f}')
                
                # Join with commas and newlines
                f.write(",\n".join(found_bones))
                f.write("\n")
            
            f.write("}")
            
        print(f"Filtered report saved to: {full_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    export_filtered_bone_lengths_filtered()


import bpy

def list_all_data(print_output=True):
    """
    List all data-blocks in the current .blend file, grouped by type.
    
    Args:
        print_output (bool): If True, prints the results. Default is True.
    
    Returns:
        dict: A dictionary mapping collection names to lists of item names.
              e.g. {'objects': ['Cube', 'Camera'], 'meshes': ['Cube'], ...}
    """
    result = {}
    
    for collection_name in dir(bpy.data):
        collection = getattr(bpy.data, collection_name)
        # Filter to only bpy_prop_collection types that contain data
        if hasattr(collection, '__len__') and hasattr(collection, '__iter__'):
            try:
                count = len(collection)
                if count > 0:
                    names = [item.name for item in collection]
                    result[collection_name] = names
                    
                    if print_output:
                        print(f"\n=== {collection_name} ({count}) ===")
                        for name in names:
                            print(f"  {name}")
            except (TypeError, AttributeError):
                pass
    
    return result


# Usage examples:
if __name__ == "__main__":   # (was run on every import, printing every datablock)
    list_all_data()                      # print + return dict
# data = list_all_data(print_output=False)  # silent, just get the dict
# print(data['objects'])                    # access a specific type