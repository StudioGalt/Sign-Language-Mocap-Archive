import bpy

def paste_pose_with_strength(strength=0.5):
    """
    Paste the copied pose data to the selected bones at the specified strength (0.0 - 1.0)
    
    Args:
        strength: Float between 0.0 and 1.0 representing the influence of the copied pose
    """
    # Ensure we have the animation data
    obj = bpy.context.object
    if not obj or obj.type != 'ARMATURE':
        print("No armature selected")
        return
    
    armature = obj
    pose = obj.pose
    
    # Get selected pose bones
    selected_bones = [b for b in pose.bones if b.bone.select]
    if not selected_bones:
        print("No bones selected")
        return
    
    # Access the copy buffer through bpy.context
    copy_buffer = bpy.context.copy()
    
    # Store the current pose for interpolation
    original_transforms = {}
    for bone in selected_bones:
        if bone.rotation_mode == 'QUATERNION':
            original_transforms[bone.name] = {
                'location': bone.location.copy(),
                'rotation_quaternion': bone.rotation_quaternion.copy(),
                'scale': bone.scale.copy()
            }
        else:
            original_transforms[bone.name] = {
                'location': bone.location.copy(),
                'rotation_euler': bone.rotation_euler.copy(),
                'scale': bone.scale.copy()
            }
    
    # Paste the pose normally (100%)
    bpy.ops.pose.paste(flipped=False)
    
    # Now interpolate back to the original pose based on strength
    for bone in selected_bones:
        if bone.name in original_transforms:
            orig = original_transforms[bone.name]
            
            # Interpolate location
            bone.location = bone.location * strength + orig['location'] * (1 - strength)
            
            # Interpolate rotation
            if bone.rotation_mode == 'QUATERNION':
                bone.rotation_quaternion = bone.rotation_quaternion.slerp(orig['rotation_quaternion'], 1 - strength)
            else:
                for i in range(len(bone.rotation_euler)):
                    bone.rotation_euler[i] = bone.rotation_euler[i] * strength + orig['rotation_euler'][i] * (1 - strength)
            
            # Interpolate scale
            bone.scale = bone.scale * strength + orig['scale'] * (1 - strength)
    
    print(f"Pose pasted at {strength*100}% strength")


paste_pose_with_strength(0.5)


