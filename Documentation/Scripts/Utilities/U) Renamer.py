import bpy
import os
import bpy.utils.previews
from bpy.types import Operator
import datetime
import shutil

# Using Blender 4.5.1
# Last tested August 12, 2025 

blend_file_dir = os.path.dirname(bpy.data.filepath)
parent_dir = os.path.dirname(blend_file_dir)
file_name = bpy.path.basename(bpy.context.blend_data.filepath)
fnsplit = file_name.split()
OldStamp = " ".join(fnsplit[:-1])
Name=Stamp = " ".join(fnsplit[2:-2])

current_time = datetime.datetime.now()
Year=current_time.year
Month=current_time.month
Day=current_time.day
Today=str(Year) + '-' + str(Month) + '-' + str(Day)
print(Today)


# Define the operator class for the popup window
class SimpleOperator(Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Rename File"

    filename1: bpy.props.StringProperty(name="Product Line", default="SG", maxlen=255)
    filename2: bpy.props.StringProperty(name="Language", default="ASL", maxlen=255)
    filename3: bpy.props.StringProperty(name="Name", default=Name, maxlen=255)
 
    def execute(self, context):
    # Get the active object
        obj = context.object
        if obj:
            filepath = bpy.data.filepath
            directory = os.path.dirname(filepath)
            file_name = bpy.path.basename(bpy.context.blend_data.filepath)
            fnsplit = file_name.split()
            OldStamp = " ".join(fnsplit[:-1])
            # New file path with the inputted name  
            current_time = datetime.datetime.now()
            Year=current_time.year
            Month=current_time.month
            Day=current_time.day
            Today=str(Year) + '-' + str(Month) + '-' + str(Day)
            print(Today)
            NewStamp = self.filename1 + " " + self.filename2 + " " + self.filename3 + " " + Today
            print(NewStamp)
            blend_file_dir = os.path.dirname(bpy.data.filepath)
            parent_dir = os.path.dirname(blend_file_dir)
            new_filepath = parent_dir+'\\'+NewStamp
            os.makedirs(new_filepath,exist_ok=True)
            new_filepath2=new_filepath+'\\' + NewStamp+ " Unedited.blend"
            bpy.ops.wm.save_as_mainfile(filepath=new_filepath2)
            actions = bpy.data.actions
            for action in actions:
                if OldStamp in action.name:
                    new_name = action.name.replace(OldStamp, NewStamp)
                    action.name = new_name
            bpy.ops.wm.save_as_mainfile(filepath=new_filepath2)      
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Register the operator
def register():
    bpy.utils.register_class(SimpleOperator)

# Unregister the operator
def unregister():
    bpy.utils.unregister_class(SimpleOperator)

# Test the operator
if __name__ == "__main__":
    register()
    bpy.ops.object.simple_operator('INVOKE_DEFAULT')

