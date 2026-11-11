import bpy

# Using Blender 5.1.0
# Last tested March 21, 2026 
# Necessary Addon: Animation Layer by Tal

class BONE_OT_CorrectionRange(bpy.types.Operator):
    """Run Rig Corrections over a Frame Range"""
    bl_idname = "object.bone_correction_range"
    bl_label = "Rig Correction Range"
    bl_options = {'REGISTER', 'UNDO'}

    # User Inputs for the Dialog Box
    start_frame: bpy.props.IntProperty(name="Start Frame", default=bpy.context.scene.frame_start)
    end_frame: bpy.props.IntProperty(name="End Frame", default=bpy.context.scene.frame_end)
    step_interval: bpy.props.IntProperty(name="Step Interval", default=10, min=1)

    def execute(self, context):
        # Grab the rig
        GaltisRig = bpy.data.objects.get('root')

        if not GaltisRig:
            self.report({'ERROR'}, "Object 'root' not found.")
            return {'CANCELLED'}

        # Ensure we are working with the correct object
        bpy.context.view_layer.objects.active = GaltisRig
        obj = GaltisRig
        
        # Ensure solo levels are turned off
        for collection in obj.data.collections_all.values():
            collection.is_solo = False

        bpy.ops.object.mode_set(mode='OBJECT')

        # Animation Layers logic
        try:
            bpy.context.object.als.turn_on = True
        except AttributeError:
            self.report({'WARNING'}, "Animation Layers addon not found or active.")

        bpy.ops.object.mode_set(mode='POSE')
        
        # 1. Turn visibility ON
        show_cols = ["Limbs Corrections", "Limbs FK", "Limbs IK", "Limbs IK Correction", 
                     "Spine Input", "Fingers FK", "Fingers IK", "Fingers Intermediate", 
                     "Unreal (Deform Rig)", "Intermediate Rig"]
        for col in show_cols:
            if col in obj.data.collections:
                obj.data.collections[col].is_visible = True

        # 2. Setup Hand IK Selection
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT') 
        if 'handik_L' in obj.data.edit_bones:
            obj.data.edit_bones['handik_L'].select = True
        bpy.ops.object.mode_set(mode='POSE') 

        # 3. Pose Paste Loop
        bpy.context.scene.frame_set(1)
        bpy.ops.pose.copy()

        # Initial keyframe at Start Frame
        bpy.context.scene.frame_set(self.start_frame)

        # Loop through range
        for frame in range(self.start_frame + 15, self.end_frame, self.step_interval):
            bpy.context.scene.frame_set(frame)
            bpy.ops.pose.paste(flipped=False)
            bpy.ops.anim.keyframe_insert()

        # 4. Finger Selection and Rotation Clearing
        bones = [
            'thumbfk_01_L', 'thumbfk_02_L', 'thumbfk_03_L', 'thumbfk_04_L',
            'pinkyinte_metacarpal_L', 'pinkyfk_01_L', 'pinkyfk_02_L', 'pinkyfk_03_L', 'pinkyfk_04_L',
            'indexinte_metacarpal_L', 'indexfk_01_L', 'indexfk_02_L', 'indexfk_03_L', 'indexfk_04_L',
            'middleinte_metacarpal_L', 'middlefk_01_L', 'middlefk_02_L', 'middlefk_03_L', 'middlefk_04_L',
            'ringinte_metacarpal_L', 'ringfk_01_L', 'ringfk_02_L', 'ringfk_03_L', 'ringfk_04_L'
        ]

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        for bone_name in bones:
            bone = obj.data.edit_bones.get(bone_name)
            if bone: bone.select = True

        bpy.ops.object.mode_set(mode='POSE')

        for frame in range(self.start_frame + 15, self.end_frame + 1, self.step_interval):
            bpy.context.scene.frame_set(frame)
            bpy.ops.pose.rot_clear()
            bpy.ops.anim.keyframe_insert()

        # 5. Cleanup UI and Visibility
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        
        hide_cols = ["Limbs Corrections", "Limbs FK", "Limbs IK Correction", "Spine Input", 
                     "Fingers FK", "Fingers IK", "Fingers Intermediate", "Unreal (Deform Rig)", 
                     "Intermediate Rig", "HeadCTRL"]
        for col in hide_cols:
            if col in obj.data.collections:
                obj.data.collections[col].is_visible = False
        
        if "Limbs IK" in obj.data.collections:
            obj.data.collections["Limbs IK"].is_visible = True

        self.report({'INFO'}, f"Completed: {self.start_frame} to {self.end_frame}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # This opens the dialog box
        return context.window_manager.invoke_props_dialog(self)

# Register the operator
def register():
    bpy.utils.register_class(BONE_OT_CorrectionRange)

def unregister():
    bpy.utils.unregister_class(BONE_OT_CorrectionRange)

if __name__ == "__main__":
    register()
    # Call the operator
    bpy.ops.object.bone_correction_range('INVOKE_DEFAULT')
