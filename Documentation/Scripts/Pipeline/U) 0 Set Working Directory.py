import bpy
import os
import addon_utils



'''This script sets the working directory, this should be where animation files are located.
This can be thought of as step 0, but only needs to run once.

Tested with Version 5.0.0
Last tested December 10, 2025
'''



class OpenFolderOperator(bpy.types.Operator):
    """Open File Explorer to Select a Folder"""
    bl_idname = "wm.open_folder"
    bl_label = "Select Folder"  
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if self.directory:
            os.chdir(self.directory)
            self.report({'INFO'}, f"Working Directory Set: {self.directory}")
            blend_file_dir = os.getcwd()
            RigFolder="AvatarFolder"
            RigDirectory = os.path.join(blend_file_dir, RigFolder)
            os.makedirs(RigDirectory, exist_ok=True)
            ModuleFolder="ModuleFolder"
            ModuleDirectory = os.path.join(blend_file_dir, ModuleFolder)
            os.makedirs(ModuleDirectory, exist_ok=True)
            AnimationFolder="Unprocessed Animations"
            AnimationDirectory = os.path.join(blend_file_dir, AnimationFolder)
            os.makedirs(AnimationDirectory, exist_ok=True)
            StorageFolder="Storage"
            StorageDirectory = os.path.join(blend_file_dir, StorageFolder)
            os.makedirs(StorageDirectory, exist_ok=True)
            AnimationStorageFolder="Storage//Animation"
            AnimationStorageDirectory = os.path.join(blend_file_dir, AnimationStorageFolder)
            os.makedirs(AnimationStorageDirectory, exist_ok=True)
            MannequinFolder="Mannequin"
            MannequinDirectory = os.path.join(blend_file_dir, MannequinFolder)
            os.makedirs(MannequinDirectory, exist_ok=True)
            UploadFolder="Ready for Upload"
            UploadDirectory = os.path.join(blend_file_dir, UploadFolder)
            os.makedirs(UploadDirectory, exist_ok=True)
            ScriptsFolder="Scripts Folder"
            ScriptDirectory = os.path.join(blend_file_dir, ScriptsFolder)
            os.makedirs(ScriptDirectory, exist_ok=True)
            file_name = bpy.path.basename(bpy.context.blend_data.filepath)
            ArchivePathblend=RigDirectory+'\\' + file_name
            bpy.ops.wm.save_as_mainfile(filepath=ArchivePathblend)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Register the operator
def register():
    bpy.utils.register_class(OpenFolderOperator)

def unregister():
    bpy.utils.unregister_class(OpenFolderOperator)

if __name__ == "__main__":
    register()
    bpy.ops.wm.open_folder('INVOKE_DEFAULT')


def check_manny_fbx():
    """
    Check if SKM_Manny_Simple.FBX exists in the mannequin folder.
    Checks relative to the current Blender file location.
    """
    # Get the directory where the current Blender file is located
    blend_file_path = bpy.data.filepath
    
    if not blend_file_path:
        print("Blender file not saved yet. Cannot determine relative path.")
        return False
    
    # Get the directory of the current Blender file
    blend_dir = os.path.dirname(blend_file_path)

    # Construct path to mannequin folder and FBX file
    mannequin_folder = os.path.join(blend_dir, "Mannequin")
    fbx_file_path = os.path.join(mannequin_folder, "SKM_Manny_Simple.FBX")
    # Check if the file exists
    if os.path.exists(fbx_file_path):
        print("SKM_Manny_Simple.FBX is ready")
        return True
    else:
        print("SKM_Manny_Simple.FBX is missing")
        return False

def check_quinn_fbx():
    """
    Check if SKM_quinn_Simple.FBX exists in the mannequin folder.
    Checks relative to the current Blender file location.
    """
    # Get the directory where the current Blender file is located
    blend_file_path = bpy.data.filepath
    
    if not blend_file_path:
        print("Blender file not saved yet. Cannot determine relative path.")
        return False
    
    # Get the directory of the current Blender file
    blend_dir = os.path.dirname(blend_file_path)

    # Construct path to mannequin folder and FBX file
    mannequin_folder = os.path.join(blend_dir, "Mannequin")
    fbx_file_path = os.path.join(mannequin_folder, "SKM_Quinn_Simple.FBX")
    # Check if the file exists
    if os.path.exists(fbx_file_path):
        print("SKM_quinn_Simple.FBX is ready")
        return True
    else:
        print("SKM_quinn_Simple.FBX is missing")
        return False



# Main execution - choose the method that works best for your setup
if __name__ == "__main__":
    # Method 1: Check relative to current Blender file location
    print("Checking relative to Blender file location:")
    check_manny_fbx()
    check_quinn_fbx()
    
#this part of script enables Rigify
def check_and_enable_rigify():
    """
    Check if Rigify is enabled and enable it if it's not.
    Returns True if Rigify is available and enabled, False otherwise.
    """
    rigify_module_name = "rigify"
    
    # Check if Rigify is already enabled
    if rigify_module_name in bpy.context.preferences.addons.keys():
        print("Rigify is already enabled")
        return True
    
    # Try to enable Rigify
    try:
        # Enable the addon
        bpy.ops.preferences.addon_enable(module=rigify_module_name)
        print("Rigify has been enabled")
        return True
    except Exception as e:
        print(f"Failed to enable Rigify: {e}")
        return False

def is_rigify_available():
    """
    Check if Rigify addon is available (installed) in Blender.
    """
    # Get all available addons
    addons = addon_utils.modules()
    
    for addon in addons:
        if addon.__name__ == "rigify":
            return True
    return False

# Main execution
if __name__ == "__main__":
    # First check if Rigify is available
    if not is_rigify_available():
        print("Rigify addon is not available in this Blender installation")
    else:
        # Check and enable Rigify
        success = check_and_enable_rigify()
        
        if success:
            print("Rigify is now ready to use!")
            # You can now access Rigify features
            # For example, check if rigify operators are available
            if hasattr(bpy.ops, 'pose') and hasattr(bpy.ops.pose, 'rigify_generate'):
                print("Rigify operators are available")
        else:
            print("Could not enable Rigify")



