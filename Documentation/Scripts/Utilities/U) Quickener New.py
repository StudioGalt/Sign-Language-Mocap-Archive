import bpy
from bpy.types import Operator
import os


# Using Blender 5.1.0
# Last tested March 18,  2025 
#Note use bake to scene rather key frame range after running script





def get_layer_actions():
    """Get all actions containing '_Layer' in their name"""
    layer_actions = [action for action in bpy.data.actions if "_Layer" in action.name]
    print(f"Found {len(layer_actions)} layer actions: {[a.name for a in layer_actions]}")
    return layer_actions


def shift_action_keyframes(action, offset):
    """Shift all keyframes in an action by the given offset"""
    if not action or not action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
        return 0
    
    keyframe_count = 0
    for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co[0] -= offset  
            keyframe_count += 1 
                
    print(f"Shifted {keyframe_count} keyframes in action '{action.name}' by {offset} frames")
    return keyframe_count

def delete_keyframes_in_range(start_frame, end_frame, obj=None):
    """Delete keyframes within a frame range for the specified object (or active object)"""
    if obj is None:
        obj = bpy.context.active_object
    
    if obj and obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
            # Find and remove keyframes within the frame range
            keyframes_to_remove = []
            for i, keyframe in enumerate(fcurve.keyframe_points):
                if start_frame <= keyframe.co.x <= end_frame:
                    keyframes_to_remove.append(i)       
            # Remove keyframes (reverse order to maintain indices)
            for i in reversed(keyframes_to_remove):               
                fcurve.keyframe_points.remove(fcurve.keyframe_points[i])



       


class SimpleOperator(Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Shiftpoint"

    filename1: bpy.props.IntProperty(name="Shiftpoint", default=1, min=0)

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
            bpy.ops.object.mode_set(mode='POSE')

            # Enable collections
            armature = bpy.data.objects['root']
            if armature and armature.data and hasattr(armature.data, 'collections_all'):
                for collection in armature.data.collections_all.values():
                    collection.is_solo = False
                    collection.is_visible = True
        
            # Store original frame range
            original_start_frame = bpy.context.scene.frame_start
            original_end_frame = bpy.context.scene.frame_end
            original_length = original_end_frame - original_start_frame + 1
                
            new_start_frame=self.filename1   
            keyframes_shifted=0    
            offset=new_start_frame
            scene = bpy.context.scene
            obj = bpy.context.active_object

            obj = bpy.context.object
    
            #esnsure solo levels are turned off


            # Set new frame and keyframe bones
            scene = context.scene
            layer_actions = get_layer_actions()
            if not layer_actions:
                self.report({'WARNING'}, "No layer actions found (actions with '_Layer' in name)")
   
            processed_actions = 0
            total_keyframes_shifted = 0
            offset = new_start_frame

            for i, action in enumerate(layer_actions):
                print(f"Processing action {i+1}/{len(layer_actions)}: {action.name}")
                if offset != 0:
                    keyframes_shifted = shift_action_keyframes(action, offset)
                    total_keyframes_shifted += keyframes_shifted
                else:
                    print(f"No offset needed for action '{action.name}'")
                    if hasattr(obj, 'als') and hasattr(obj.als, 'layer_index'):
                        obj.als.layer_index = i
                        # Assign action to object if requested
                    if not self.process_all_layers:
                        assign_action_to_object(obj, action)
                        break
            processed_actions += 1         



            action = armature.animation_data.action
            frame_range = action.frame_range
            last_frame = action.frame_range[1]
            print(frame_range)
    
            bpy.context.scene.frame_end = int(last_frame)
            scene_end = bpy.context.scene.frame_end
            
            for i, action in enumerate(layer_actions):
                bpy.context.object.als.layer_index = i
                negative_offset=int(-offset*10)
                delete_keyframes_in_range(negative_offset, -1)   
    
            scene = bpy.context.scene
            bpy.context.object.als.layer_index = 0

            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.context.scene.frame_set(1)
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            bpy.context.scene.frame_set(0)
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            print("Completed layer")
    

            bpy.context.object.als.layer_index = 1

            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.context.scene.frame_set(1)
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            bpy.context.scene.frame_set(0)
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            print("Completed layer")
    
            bpy.context.object.als.layer_index = 2

            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.context.scene.frame_set(1)
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            bpy.context.scene.frame_set(0)
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            print("Completed layer")
    

            bpy.context.object.als.layer_index = 3

            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            scene.frame_set(20)
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            scene.frame_set(scene.frame_end)
            bpy.ops.pose.copy()
            bpy.context.scene.frame_set(1)
            bpy.ops.pose.paste(flipped=False)

            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            bpy.context.scene.frame_set(0)
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
            print("Completed layer")
    

            if armature and armature.data and hasattr(armature.data, 'collections_all'):
                for collection in armature.data.collections_all.values():
                    collection.is_visible = False
        
            bpy.context.object.data.collections_all["Limbs IK"].is_visible = True
            action = armature.animation_data.action
            frame_range = action.frame_range
            last_frame = action.frame_range[1]
            print(frame_range)
            new_end_frame=int(last_frame)
            bpy.context.scene.frame_end = new_end_frame

            def set_layer_frame_ranges(start_frame=1, end_frame=new_end_frame):
                """Set frame range for all layer actions"""
                layer_actions = get_layer_actions()
    
                for action in layer_actions:
                    action.use_frame_range = True
                    action.frame_start = start_frame
                    action.frame_end = end_frame
                    print(f"Set {action.name}: frames {start_frame}-{end_frame}")
            
            set_layer_frame_ranges(1, new_end_frame)
            
            # Calculate new length
            new_start = bpy.context.scene.frame_start
            new_end = bpy.context.scene.frame_end
            new_length = new_end - new_start + 1
        
            report_text = f"""Animation Shift Report
====================

Original Frame Range: {original_start_frame} - {original_end_frame}
Original Length: {original_length} frames

Shift Point: {self.filename1} frames

New Frame Range: {new_start} - {new_end}
New Length: {new_length} frames

Total Keyframes Shifted: {total_keyframes_shifted}
Actions Processed: {len(layer_actions)}
"""
            
            # Print to console
            print("\n" + "="*50)
            print(report_text)
            print("="*50 + "\n")
            
            # Save to text file
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
                output_path = os.path.join(tempfile.gettempdir(), "animation_shift_report.txt")
            
            try:
                with open(output_path, 'a') as f:
                    f.write(report_text)
                print(f"Report saved to: {output_path}")
                self.report({'INFO'}, f"Report saved to: {output_path}")
            except Exception as e:
                print(f"Could not save report file: {e}")
                self.report({'WARNING'}, f"Could not save report file: {e}")
            
            for marker in scene.timeline_markers:
                marker.select = True
                marker.frame -= self.filename1   
            for marker in scene.timeline_markers:
                marker.name = f"F_{marker.frame}"
            
            last_frame=original_end_frame-self.filename1  

            scene.frame_end = last_frame
            bpy.context.scene.frame_preview_end = last_frame

            print(f"Frame range end set to: {last_frame}")
            
            
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
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
