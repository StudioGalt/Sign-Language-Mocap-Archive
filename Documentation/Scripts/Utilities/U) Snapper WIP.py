import bpy
from bpy.types import Operator, Panel, PropertyGroup

#Using Blender 4.3.2
#Last tested April 5th, 2025 


# Configure default transform orientation
bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'


# -------------------------------------------------------------------------------
# Core snapping functions with improved error handling and performance
# -------------------------------------------------------------------------------

def snap_bones(armature_name, source_bones, target_bones, frame_range, direction='IK_TO_FK'):
    """
    Universal snapping function for both FK to IK and IK to FK directions
    with better error handling and progress reporting
    
    Parameters:
    - armature_name: Name of the armature object
    - source_bones: List of source bone names
    - target_bones: List of target bone names (must match length of source_bones)
    - frame_range: List or range of frames to process
    - direction: 'IK_TO_FK' or 'FK_TO_IK'
    
    Returns:
    - tuple: (success, message)
    """
    # Validate armature
    armature = bpy.data.objects.get(armature_name)
    if armature is None:
        return False, f"Object '{armature_name}' not found"
    if armature.type != 'ARMATURE':
        return False, f"Object '{armature_name}' is not an armature"
    
    # Validate bone counts
    if len(source_bones) != len(target_bones):
        return False, "Source and target bone lists must have the same length"
    
    # Check if bones exist
    missing_bones = []
    for bone in source_bones + target_bones:
        if bone not in armature.pose.bones:
            missing_bones.append(bone)
    
    if missing_bones:
        return False, f"The following bones were not found: {', '.join(missing_bones)}"
    
    # Store initial frame to restore it later
    initial_frame = bpy.context.scene.frame_current
    
    # Process each frame
    total_frames = len(frame_range)
    success_count = 0
    
    for i, frame in enumerate(frame_range):
        # Update progress every 10 frames
        if i % 10 == 0:
            bpy.context.window_manager.progress_update(i / total_frames)
        
        bpy.context.scene.frame_set(frame)
        
        # Process each bone pair
        for source, target in zip(source_bones, target_bones):
            source_bone = armature.pose.bones.get(source)
            target_bone = armature.pose.bones.get(target)
            
            # Transfer matrix transformation
            target_bone.matrix = source_bone.matrix
            
            # Insert keyframes
            for channel in ['location', 'rotation_quaternion', 'scale']:
                if hasattr(target_bone, channel):  # Only insert keyframes for properties that exist
                    armature.keyframe_insert(data_path=f'pose.bones["{target}"].{channel}', frame=frame)
        
        # Update view after each frame to ensure proper visualization
        bpy.context.view_layer.update()
        success_count += 1
    
    # Restore original frame
    bpy.context.scene.frame_set(initial_frame)
    
    # Return results
    if success_count == total_frames:
        return True, f"Successfully processed {success_count} frames"
    else:
        return False, f"Processed {success_count}/{total_frames} frames"


# -------------------------------------------------------------------------------
# Bone mapping configuration - with better organization
# -------------------------------------------------------------------------------

class BoneMapping:
    """
    Class to organize and store bone mappings
    """
    def __init__(self):
        self.armature_name = 'root'
        
        # Limbs
        self.arm_chains = {
            'R': {
                'fk': ['bicepfk_R', 'forearmfk_R', 'handfk_R'],
                'ik': ['bicepik_R', 'forearmik_R', 'handik_R']
            },
            'L': {
                'fk': ['bicepfk_L', 'forearmfk_L', 'handfk_L'],
                'ik': ['bicepik_L', 'forearmik_L', 'handik_L']
            }
        }
        
        self.leg_chains = {
            'R': {
                'fk': ['thighfk_R', 'shinfk_R', 'footfk_R'],
                'ik': ['thighik_R', 'shinik_R', 'footik_R']
            },
            'L': {
                'fk': ['thighfk_L', 'shinfk_L', 'footfk_L'],
                'ik': ['thighik_L', 'shinik_L', 'footik_L']
            }
        }
        
        # Fingers
        self.finger_chains = {
            'index': {
                'R': {
                    'fk': ['indexfk_01_R', 'indexfk_02_R', 'indexfk_03_R'],
                    'ik': ['indexik_01_R', 'indexik_02_R', 'indexik_03_R']
                },
                'L': {
                    'fk': ['indexfk_01_L', 'indexfk_02_L', 'indexfk_03_L'],
                    'ik': ['indexik_01_L', 'indexik_02_L', 'indexik_03_L']
                }
            },
            'middle': {
                'R': {
                    'fk': ['middlefk_01_R', 'middlefk_02_R', 'middlefk_03_R'],
                    'ik': ['middleik_01_R', 'middleik_02_R', 'middleik_03_R']
                },
                'L': {
                    'fk': ['middlefk_01_L', 'middlefk_02_L', 'middlefk_03_L'],
                    'ik': ['middleik_01_L', 'middleik_02_L', 'middleik_03_L']
                }
            },
            'ring': {
                'R': {
                    'fk': ['ringfk_01_R', 'ringfk_02_R', 'ringfk_03_R'],
                    'ik': ['ringik_01_R', 'ringik_02_R', 'ringik_03_R']
                },
                'L': {
                    'fk': ['ringfk_01_L', 'ringfk_02_L', 'ringfk_03_L'],
                    'ik': ['ringik_01_L', 'ringik_02_L', 'ringik_03_L']
                }
            },
            'pinky': {
                'R': {
                    'fk': ['pinkyfk_01_R', 'pinkyfk_02_R', 'pinkyfk_03_R'],
                    'ik': ['pinkyik_01_R', 'pinkyik_02_R', 'pinkyik_03_R']
                },
                'L': {
                    'fk': ['pinkyfk_01_L', 'pinkyfk_02_L', 'pinkyfk_03_L'],
                    'ik': ['pinkyik_01_L', 'pinkyik_02_L', 'pinkyik_03_L']
                }
            },
            'thumb': {
                'R': {
                    'fk': ['thumbfk_01_R', 'thumbfk_02_R', 'thumbfk_03_R'],
                    'ik': ['thumbik_01_R', 'thumbik_02_R', 'thumbik_03_R']
                },
                'L': {
                    'fk': ['thumbfk_01_L', 'thumbfk_02_L', 'thumbfk_03_L'],
                    'ik': ['thumbik_01_L', 'thumbik_02_L', 'thumbik_03_L']
                }
            }
        }
    
    def get_bone_pairs(self, limb_type, side, direction):
        """
        Get source and target bone lists based on type, side, and direction
        
        Parameters:
        - limb_type: 'arm', 'leg', or a finger name
        - side: 'L' or 'R'
        - direction: 'IK_TO_FK' or 'FK_TO_IK'
        
        Returns:
        - tuple: (source_bones, target_bones)
        """
        if limb_type == 'arm':
            chains = self.arm_chains
        elif limb_type == 'leg':
            chains = self.leg_chains
        else:
            # Finger
            chains = self.finger_chains.get(limb_type, {})
        
        side_chains = chains.get(side, {})
        
        # Determine source and target based on direction
        if direction == 'IK_TO_FK':
            source_bones = side_chains.get('fk', [])
            target_bones = side_chains.get('ik', [])
        else:  # FK_TO_IK
            source_bones = side_chains.get('ik', [])
            target_bones = side_chains.get('fk', [])
        
        return source_bones, target_bones


# Global instance of bone mapping
BONE_MAPPING = BoneMapping()


# -------------------------------------------------------------------------------
# Settings property group with improved organization and additional features
# -------------------------------------------------------------------------------

class FK_IK_SnapSettings(PropertyGroup):
    # Direction settings
    snap_direction: bpy.props.EnumProperty(
        name="Snap Direction",
        description="Direction to snap bones",
        items=[
            ('IK_TO_FK', "IK to FK", "Snap IK bones to match FK bones"),
            ('FK_TO_IK', "FK to IK", "Snap FK bones to match IK bones")
        ],
        default='IK_TO_FK'
    )
    
    # Frame range settings
    use_current_frame_only: bpy.props.BoolProperty(
        name="Current Frame Only",
        description="Snap only on the current frame",
        default=True
    )
    
    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        description="Start frame for snapping",
        default=0,
        min=0
    )
    
    frame_end: bpy.props.IntProperty(
        name="End Frame",
        description="End frame for snapping",
        default=100,
        min=0
    )
    
    # Custom armature name setting
    custom_armature: bpy.props.BoolProperty(
        name="Custom Armature",
        description="Use a custom armature instead of 'root'",
        default=False
    )
    
    armature_name: bpy.props.StringProperty(
        name="Armature Name",
        description="Name of the armature to use",
        default="root"
    )
    
    # Preset system
    presets: bpy.props.EnumProperty(
        name="Quick Selection",
        description="Select a preset configuration",
        items=[
            ('NONE', "Custom Selection", "Use custom selection"),
            ('ALL', "All Limbs", "Select all limbs"),
            ('ARMS', "Arms Only", "Select both arms"),
            ('LEGS', "Legs Only", "Select both legs"),
            ('FINGERS', "All Fingers", "Select all fingers"),
            ('RIGHT', "Right Side", "Select all right limbs"),
            ('LEFT', "Left Side", "Select all left limbs")
        ],
        default='NONE'
    )
    
    # Limb settings
    use_right_arm: bpy.props.BoolProperty(
        name="Right Arm",
        description="Snap Right Arm bones",
        default=False
    )
    
    use_left_arm: bpy.props.BoolProperty(
        name="Left Arm",
        description="Snap Left Arm bones",
        default=False
    )
    
    use_right_leg: bpy.props.BoolProperty(       
        name="Right Leg",
        description="Snap Right Leg bones",
        default=False
    )
    
    use_left_leg: bpy.props.BoolProperty(
        name="Left Leg",
        description="Snap Left Leg bones",
        default=False
    )
    
    # Finger settings
    use_right_index: bpy.props.BoolProperty(
        name="Right Index",
        description="Snap Right Index Finger bones",
        default=False
    )
    
    use_left_index: bpy.props.BoolProperty(
        name="Left Index",
        description="Snap Left Index Finger bones",
        default=False
    )
    
    use_right_middle: bpy.props.BoolProperty(
        name="Right Middle",
        description="Snap Right Middle Finger bones",
        default=False
    )
    
    use_left_middle: bpy.props.BoolProperty(
        name="Left Middle",
        description="Snap Left Middle Finger bones",
        default=False
    )
    
    use_right_ring: bpy.props.BoolProperty(
        name="Right Ring",
        description="Snap Right Ring Finger bones",
        default=False
    )
    
    use_left_ring: bpy.props.BoolProperty(
        name="Left Ring",
        description="Snap Left Ring Finger bones",
        default=False
    )
    
    use_right_pinky: bpy.props.BoolProperty(
        name="Right Pinky",
        description="Snap Right Pinky Finger bones",
        default=False
    )
    
    use_left_pinky: bpy.props.BoolProperty(
        name="Left Pinky",
        description="Snap Left Pinky Finger bones",
        default=False
    )
    
    use_right_thumb: bpy.props.BoolProperty(
        name="Right Thumb",
        description="Snap Right Thumb bones",
        default=False
    )
    
    use_left_thumb: bpy.props.BoolProperty(
        name="Left Thumb",
        description="Snap Left Thumb bones",
        default=False
    )


# -------------------------------------------------------------------------------
# Preset Handler
# -------------------------------------------------------------------------------

def apply_preset(self, context):
    """Update checkboxes based on selected preset"""
    settings = context.scene.fk_ik_snap_settings
    preset = settings.presets
    
    # Skip if NONE is selected
    if preset == 'NONE':
        return
    
    # Clear all selections first
    settings.use_right_arm = False
    settings.use_left_arm = False
    settings.use_right_leg = False
    settings.use_left_leg = False
    settings.use_right_index = False
    settings.use_left_index = False
    settings.use_right_middle = False
    settings.use_left_middle = False
    settings.use_right_ring = False
    settings.use_left_ring = False
    settings.use_right_pinky = False
    settings.use_left_pinky = False
    settings.use_right_thumb = False
    settings.use_left_thumb = False
    
    # Apply preset selections
    if preset == 'ALL':
        settings.use_right_arm = True
        settings.use_left_arm = True
        settings.use_right_leg = True
        settings.use_left_leg = True
        settings.use_right_index = True
        settings.use_left_index = True
        settings.use_right_middle = True
        settings.use_left_middle = True
        settings.use_right_ring = True
        settings.use_left_ring = True
        settings.use_right_pinky = True
        settings.use_left_pinky = True
        settings.use_right_thumb = True
        settings.use_left_thumb = True
    
    elif preset == 'ARMS':
        settings.use_right_arm = True
        settings.use_left_arm = True
    
    elif preset == 'LEGS':
        settings.use_right_leg = True
        settings.use_left_leg = True
    
    elif preset == 'FINGERS':
        settings.use_right_index = True
        settings.use_left_index = True
        settings.use_right_middle = True
        settings.use_left_middle = True
        settings.use_right_ring = True
        settings.use_left_ring = True
        settings.use_right_pinky = True
        settings.use_left_pinky = True
        settings.use_right_thumb = True
        settings.use_left_thumb = True
    
    elif preset == 'RIGHT':
        settings.use_right_arm = True
        settings.use_right_leg = True
        settings.use_right_index = True
        settings.use_right_middle = True
        settings.use_right_ring = True
        settings.use_right_pinky = True
        settings.use_right_thumb = True
    
    elif preset == 'LEFT':
        settings.use_left_arm = True
        settings.use_left_leg = True
        settings.use_left_index = True
        settings.use_left_middle = True
        settings.use_left_ring = True
        settings.use_left_pinky = True
        settings.use_left_thumb = True
    
    # Reset preset to NONE
    settings.presets = 'NONE'


# -------------------------------------------------------------------------------
# Improved Operator with progress indicator and error reporting
# -------------------------------------------------------------------------------

class FK_IK_Snapper(Operator):
    bl_idname = "object.fk_ik_snapper"
    bl_label = "Snap FK/IK Bones"
    bl_description = "Snap FK and IK bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.fk_ik_snap_settings
        
        # Get armature name
        armature_name = settings.armature_name if settings.custom_armature else BONE_MAPPING.armature_name
        
        # Check if any bones are selected for snapping
        any_selected = (
            settings.use_right_arm or settings.use_left_arm or 
            settings.use_right_leg or settings.use_left_leg or
            settings.use_right_index or settings.use_left_index or
            settings.use_right_middle or settings.use_left_middle or
            settings.use_right_ring or settings.use_left_ring or
            settings.use_right_pinky or settings.use_left_pinky or
            settings.use_right_thumb or settings.use_left_thumb
        )
        
        if not any_selected:
            self.report({'WARNING'}, "Please select at least one limb or finger to snap")
            return {'CANCELLED'}
        
        # Define frame range
        if settings.use_current_frame_only:
            frame_range = [context.scene.frame_current]
        else:
            frame_range = range(settings.frame_start, settings.frame_end + 1)
        
        # Start progress indicator
        wm = context.window_manager
        wm.progress_begin(0, 100)
        
        # Process limbs and fingers
        results = []
        success_count = 0
        error_count = 0
        
        # Process limbs
        limb_data = [
            ("arm", "R", settings.use_right_arm),
            ("arm", "L", settings.use_left_arm),
            ("leg", "R", settings.use_right_leg),
            ("leg", "L", settings.use_left_leg),
            ("index", "R", settings.use_right_index),
            ("index", "L", settings.use_left_index),
            ("middle", "R", settings.use_right_middle),
            ("middle", "L", settings.use_left_middle),
            ("ring", "R", settings.use_right_ring),
            ("ring", "L", settings.use_left_ring),
            ("pinky", "R", settings.use_right_pinky),
            ("pinky", "L", settings.use_left_pinky),
            ("thumb", "R", settings.use_right_thumb),
            ("thumb", "L", settings.use_left_thumb)
        ]
        
        for limb_type, side, is_selected in limb_data:
            if is_selected:
                source_bones, target_bones = BONE_MAPPING.get_bone_pairs(
                    limb_type, side, settings.snap_direction
                )
                
                # Check if bone lists are valid
                if not source_bones or not target_bones:
                    results.append(f"No bone mapping found for {side} {limb_type}")
                    error_count += 1
                    continue
                
                success, message = snap_bones(
                    armature_name, source_bones, target_bones, 
                    frame_range, settings.snap_direction
                )
                
                limb_name = f"{side} {limb_type}"
                results.append(f"{limb_name}: {'Success' if success else 'Failed'} - {message}")
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
        
        # End progress indicator
        wm.progress_end()
        
        # Report results
        if error_count == 0:
            direction_text = "IK to FK" if settings.snap_direction == 'IK_TO_FK' else "FK to IK"
            self.report({'INFO'}, f"{direction_text} snapping completed successfully for {success_count} elements")
        else:
            self.report({'WARNING'}, f"Completed with {error_count} errors. Check console for details.")
            for result in results:
                print(result)
        
        return {'FINISHED'}


# -------------------------------------------------------------------------------
# Panel UI with more organization and features
# -------------------------------------------------------------------------------

class VIEW3D_PT_fk_ik_tools(Panel):
    bl_label = "FK/IK Snap Tools"
    bl_idname = "VIEW3D_PT_fk_ik_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Snap2'
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.fk_ik_snap_settings
        
        # Direction selector
        row = layout.row()
        row.label(text="Snap Direction:")
        row = layout.row()
        row.prop(settings, "snap_direction", expand=True)
        
        # Presets system
        box = layout.box()
        box.label(text="Quick Selection:")
        row = box.row()
        row.prop(settings, "presets", text="")
        
        # Armature settings
        box = layout.box()
        box.label(text="Armature:")
        row = box.row()
        row.prop(settings, "custom_armature")
        if settings.custom_armature:
            row = box.row()
            row.prop(settings, "armature_name")
        
        # Frame range settings
        box = layout.box()
        box.label(text="Frame Range:")
        row = box.row()
        row.prop(settings, "use_current_frame_only")
        
        if not settings.use_current_frame_only:
            row = box.row(align=True)
            row.prop(settings, "frame_start")
            row.prop(settings, "frame_end")
        
        # Limb checkboxes
        box = layout.box()
        box.label(text="Limbs:")
        
        grid = box.grid_flow(row_major=True, columns=2, even_columns=True)
        grid.prop(settings, "use_right_arm")
        grid.prop(settings, "use_left_arm")
        grid.prop(settings, "use_right_leg")
        grid.prop(settings, "use_left_leg")
        
        # Finger checkboxes
        box = layout.box()
        box.label(text="Fingers:")
        
        grid = box.grid_flow(row_major=True, columns=2, even_columns=True)
        grid.prop(settings, "use_right_index")
        grid.prop(settings, "use_left_index")
        grid.prop(settings, "use_right_middle")
        grid.prop(settings, "use_left_middle")
        grid.prop(settings, "use_right_ring")
        grid.prop(settings, "use_left_ring")
        grid.prop(settings, "use_right_pinky")
        grid.prop(settings, "use_left_pinky")
        grid.prop(settings, "use_right_thumb")
        grid.prop(settings, "use_left_thumb")
        
        # Execute button
        row = layout.row()
        row.scale_y = 1.5
        row.operator(FK_IK_Snapper.bl_idname, text="Execute Snap")


# -------------------------------------------------------------------------------
# Register and unregister functions
# -------------------------------------------------------------------------------

# Callback for preset system
def update_presets(self, context):
    apply_preset(self, context)

def register():
    # Add callback for presets
    FK_IK_SnapSettings.presets = bpy.props.EnumProperty(
        name="Quick Selection",
        description="Select a preset configuration",
        items=[
            ('NONE', "Custom Selection", "Use custom selection"),
            ('ALL', "All Limbs", "Select all limbs"),
            ('ARMS', "Arms Only", "Select both arms"),
            ('LEGS', "Legs Only", "Select both legs"),
            ('FINGERS', "All Fingers", "Select all fingers"),
            ('RIGHT', "Right Side", "Select all right limbs"),
            ('LEFT', "Left Side", "Select all left limbs")
        ],
        default='NONE',
        update=update_presets
    )
    
    bpy.utils.register_class(FK_IK_SnapSettings)
    bpy.utils.register_class(FK_IK_Snapper)
    bpy.utils.register_class(VIEW3D_PT_fk_ik_tools)
    bpy.types.Scene.fk_ik_snap_settings = bpy.props.PointerProperty(type=FK_IK_SnapSettings)

def unregister():
    del bpy.types.Scene.fk_ik_snap_settings
    bpy.utils.unregister_class(VIEW3D_PT_fk_ik_tools)
    bpy.utils.unregister_class(FK_IK_Snapper)
    bpy.utils.unregister_class(FK_IK_SnapSettings)

if __name__ == "__main__":
    register()
