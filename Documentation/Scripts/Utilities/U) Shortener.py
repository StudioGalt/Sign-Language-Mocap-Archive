import bpy
from bpy.types import Operator
import os


# Using Blender 5.1.0
# Last tested March 18,  2025 
#Note use bake to scene rather key frame range after running script

def delete_keyframes_after_scene_end():
    scene = bpy.context.scene
    end_frame = scene.frame_end
    deleted_count = 0
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                # Delete keyframes beyond scene end
                for kp in reversed(fcurve.keyframe_points):
                    if kp.co.x > end_frame:
                        fcurve.keyframe_points.remove(kp)
                        deleted_count += 1
    return deleted_count


class SimpleOperator(Operator):
    bl_idname = "object.simple_operator"
    bl_label = "New End Frame"

    filename1: bpy.props.IntProperty(name="New End Point", default=0, min=0)

    def execute(self, context):
        obj = context.object
        if obj is None:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        GaltisRig = bpy.data.objects.get('root')
        if GaltisRig is None:
            self.report({'ERROR'}, "Object 'root' not found.")
            return {'CANCELLED'}

        try:
            # Store original values before any changes
            original_start_frame = bpy.context.scene.frame_start
            original_end_frame = bpy.context.scene.frame_end
            original_length = original_end_frame - original_start_frame + 1
            layer_keyframe_counts = {}
            for layer_idx in range(4):
                bpy.context.object.als.layer_index = layer_idx
                if obj.animation_data and obj.animation_data.action:
                    action = obj.animation_data.action
                    count = 0
                    for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                        count += len(fcurve.keyframe_points)
                    layer_keyframe_counts[f'Layer {layer_idx}'] = {'original': count}
            
            bpy.ops.object.mode_set(mode='POSE')

            # Enable collections
            collections = [
                "Limbs Corrections", "Limbs FK", "Limbs IK", "Limbs IK Correction",
                "Spine Input", "Fingers FK", "Fingers IK", "Fingers Intermediate",
                "Unreal (Deform Rig)", "Intermediate Rig"
            ]

            for col in collections:
                if col in obj.data.collections:
                    obj.data.collections[col].is_visible = True
            obj = bpy.context.object
    
            #esnsure solo levels are turned off
            for collection in obj.data.collections_all.values():
                collection.is_solo = False

            # Set new frame and keyframe bones
            scene = context.scene
            NewFrame = self.filename1
            
            scene = bpy.context.scene
            scene.frame_set(scene.frame_end+1)
            
            bpy.ops.pose.select_all(action='DESELECT')


            bpy.ops.object.mode_set(mode='EDIT') 
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.object.mode_set(mode='POSE') 
            bpy.ops.pose.copy()
            bpy.context.scene.frame_end = NewFrame

            # Track deleted keyframes per layer
            total_deleted = 0
            
            bpy.context.object.als.layer_index = 0
            deleted = delete_keyframes_after_scene_end()
            layer_keyframe_counts['Layer 0']['deleted'] = deleted
            total_deleted += deleted

            bpy.context.object.als.layer_index = 1
            deleted = delete_keyframes_after_scene_end()
            layer_keyframe_counts['Layer 1']['deleted'] = deleted
            total_deleted += deleted

            bpy.context.object.als.layer_index = 2
            deleted = delete_keyframes_after_scene_end()
            layer_keyframe_counts['Layer 2']['deleted'] = deleted
            total_deleted += deleted

            bpy.context.object.als.layer_index = 3
            deleted = delete_keyframes_after_scene_end()
            layer_keyframe_counts['Layer 3']['deleted'] = deleted
            total_deleted += deleted
        
            scene.frame_set(NewFrame)
            bpy.context.scene.frame_end = NewFrame
            bpy.ops.pose.paste(flipped=False)
            bpy.ops.anim.keyframe_insert()
            
            
            for col in collections:
                if col in obj.data.collections:
                    obj.data.collections[col].is_visible = False
                    
            bpy.context.object.data.collections_all["Limbs IK"].is_visible = True
            bpy.ops.pose.select_all(action='DESELECT')



            bpy.ops.object.mode_set(mode='EDIT') 
            bpy.data.objects["root"].data.edit_bones['elbow_target_R'].select = True
            bpy.data.objects["root"].data.edit_bones['elbow_target_L'].select = True
            bpy.ops.object.mode_set(mode='POSE') 
            bpy.context.scene.frame_set(20)
            bpy.ops.pose.copy()

            bpy.context.scene.frame_set(NewFrame-20)
            bpy.ops.pose.paste(flipped=False)
            bpy.ops.anim.keyframe_insert()
            
            
            obj = bpy.context.active_object
            anim_data = obj.animation_data
            action = anim_data.action

            new_start_frame = bpy.context.scene.frame_start
            new_end_frame = bpy.context.scene.frame_end

            action.frame_range = (1, NewFrame)
            
            # Count final keyframes in each layer
            for layer_idx in range(4):
                bpy.context.object.als.layer_index = layer_idx
                if obj.animation_data and obj.animation_data.action:
                    action = obj.animation_data.action
                    count = 0
                    for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
                        count += len(fcurve.keyframe_points)
                    layer_keyframe_counts[f'Layer {layer_idx}']['final'] = count
            
            # Calculate final values
            final_start_frame = bpy.context.scene.frame_start
            final_end_frame = bpy.context.scene.frame_end
            final_length = final_end_frame - final_start_frame + 1
            frame_change = final_end_frame - original_end_frame
            
            # Generate detailed report
            report_text =f"""Original Range: {original_start_frame} - {original_end_frame} ({original_length} frames)
New Range:      {final_start_frame} - {final_end_frame} ({final_length} frames)
New End Point:  {NewFrame}
Frame Change:   {frame_change:+d} frames

"""
            blend_filepath = bpy.data.filepath
            if blend_filepath:
                # Save next to the .blend file
                output_dir = os.path.dirname(blend_filepath)
                file_name = bpy.path.basename(bpy.context.blend_data.filepath)
                fnsplit = file_name.split()
                Stamp = " ".join(fnsplit[:-1])
                output_filename = Stamp + " Framelog.txt"
                output_path = os.path.join(output_dir, output_filename)
            else:
                # Save to temp directory if blend file not saved
                import tempfile
                output_path = os.path.join(tempfile.gettempdir(), "endframe_adjustment_report.txt")
            
            try:
                with open(output_path, 'a') as f:
                    f.write(report_text)
                print(f"Report saved to: {output_path}")
                self.report({'INFO'}, f"Report saved to: {output_path}")
            except Exception as e:
                print(f"Could not save report file: {e}")
                self.report({'WARNING'}, f"Could not save report file: {e}")
            
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Set default to current frame
        self.filename1 = context.scene.frame_current
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(SimpleOperator)

def unregister():
    bpy.utils.unregister_class(SimpleOperator)

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
    bpy.ops.object.simple_operator('INVOKE_DEFAULT')
