import bpy

bpy.ops.mesh.primitive_cube_add(size=4, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

cube_obj = bpy.context.active_object
cube_obj.location.z = 5

