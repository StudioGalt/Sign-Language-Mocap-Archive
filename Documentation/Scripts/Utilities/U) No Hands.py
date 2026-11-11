import bpy


#This is a script for fixing mocap, where no hand data was recorded.


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
bpy.context.object.data.collections["Limbs IK Correction"].is_visible = True
bpy.context.object.data.collections["HeadCTRL"].is_visible = True




bpy.ops.pose.select_all(action='DESELECT')

bpy.context.object.data.collections_all["Fingers FK"].is_solo = True
bpy.ops.pose.select_all(action='SELECT')
bpy.context.object.als.layer_index = 1

bpy.ops.pose.select_all(action='SELECT')
bpy.ops.anim.keyframe_clear_v3d()

scene = bpy.context.scene

bpy.context.scene.frame_set(0)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()
bpy.context.scene.frame_set(1)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(2)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(bpy.context.scene.frame_start)
bpy.context.scene.frame_set(30)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

scene.frame_set(scene.frame_end - 30)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()




bpy.context.scene.frame_set(scene.frame_end-1)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(scene.frame_end)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.object.als.layer_index = 3

bpy.context.scene.frame_set(0)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()
bpy.context.scene.frame_set(1)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(scene.frame_end-1)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.scene.frame_set(scene.frame_end)
bpy.ops.pose.rot_clear()
bpy.ops.anim.keyframe_insert()

bpy.context.object.als.layer_index = 3

bpy.context.object.data.collections["Limbs Corrections"].is_visible = False
bpy.context.object.data.collections["Limbs FK"].is_visible = False
bpy.context.object.data.collections["Limbs IK"].is_visible = False
bpy.context.object.data.collections["Limbs IK Correction"].is_visible = False
bpy.context.object.data.collections["Spine Input"].is_visible = False
bpy.context.object.data.collections["Fingers FK"].is_visible = False
bpy.context.object.data.collections["Fingers IK"].is_visible = False
bpy.context.object.data.collections["Fingers Intermediate"].is_visible = False
bpy.context.object.data.collections["Unreal (Deform Rig)"].is_visible = False
bpy.context.object.data.collections["Intermediate Rig"].is_visible = False
bpy.context.object.data.collections["Limbs IK Correction"].is_visible = False
bpy.context.object.data.collections["HeadCTRL"].is_visible = False

