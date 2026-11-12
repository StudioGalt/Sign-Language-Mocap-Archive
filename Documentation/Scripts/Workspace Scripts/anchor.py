import bpy

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


