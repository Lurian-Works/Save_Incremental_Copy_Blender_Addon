import bpy
# Import OS functions for file handling
import os
# Import regex module for detecting trailing numbers
import re

from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty


# Addon Preferences for naming format
class IncrementalSavePreferences(AddonPreferences):

    bl_idname = __name__

    separator: StringProperty(
        name="Separator",
        description="Character placed between the filename and the number",
        default=""
    )

    padding: IntProperty(
        name="Number Padding",
        description="Number of digits for the incremental number (0 = no padding)",
        default=1,
        min=1,
        max=6
    )

    def draw(self, context):

        layout = self.layout
        layout.label(text="Incremental Naming Settings")
        layout.prop(self, "separator")
        layout.prop(self, "padding")


# Define the operator that saves an incremental copy
class WM_OT_save_incremental_copy(bpy.types.Operator):

    bl_idname = "wm.save_incremental_copy_simple"
    bl_label = "Save Incremental Copy"
    bl_description = "Save an incremental copy without switching files"
    bl_options = {'REGISTER'}


    # Main execution function
    def execute(self, context):

        # Get addon preferences
        prefs = bpy.context.preferences.addons[__name__].preferences
        separator = prefs.separator
        padding = prefs.padding

        # Get the current blend file path
        filepath = bpy.data.filepath

        # If the file was never saved, show an error
        if not filepath:
            self.report({'ERROR'}, "File must be saved first")
            return {'CANCELLED'}

        # Extract directory path
        directory = os.path.dirname(filepath)

        # Extract filename from full path
        filename = os.path.basename(filepath)

        # Split filename into base name and extension
        base_name, ext = os.path.splitext(filename)

        # Separate trailing numbers from the base name
        match = re.match(r"(.*?)(\d+)?$", base_name)

        # Base name without the incremental number
        name_only = match.group(1)

        # Find all files starting with the base name and ending with .blend
        existing_files = [
            f for f in os.listdir(directory)
            if f.startswith(name_only) and f.endswith(ext)
        ]

        # Regex pattern to detect incremental numbers at the end
        pattern = re.compile(rf"{re.escape(name_only)}{re.escape(separator)}(\d+){re.escape(ext)}$")

        # List to store found incremental numbers
        numbers = []

        # Loop through existing files
        for f in existing_files:

            # Check if file matches the incremental pattern
            m = pattern.match(f)

            # If it matches, extract the number
            if m:

                # Convert the captured number to integer
                numbers.append(int(m.group(1)))


        next_number = max(numbers) + 1 if numbers else 1

        # Apply number padding if enabled
        if padding > 1:
            number_str = str(next_number).zfill(padding)
        else:
            number_str = str(next_number)

        # Construct the new incremental filename and path
        new_filename = f"{name_only}{separator}{number_str}{ext}"
        new_filepath = os.path.join(directory, new_filename)


        bpy.ops.wm.save_as_mainfile(filepath=new_filepath, copy=True)

        self.report({'INFO'}, f"Saved incremental copy: {new_filename}")
        
        return {'FINISHED'}


def menu_func(self, context):
    
    self.layout.operator(WM_OT_save_incremental_copy.bl_idname)


def register():

    bpy.utils.register_class(IncrementalSavePreferences)
    bpy.utils.register_class(WM_OT_save_incremental_copy)

    # Append the operator to the File menu
    bpy.types.TOPBAR_MT_file.append(menu_func)


def unregister():

    bpy.types.TOPBAR_MT_file.remove(menu_func)

    bpy.utils.unregister_class(WM_OT_save_incremental_copy)
    bpy.utils.unregister_class(IncrementalSavePreferences)
    

if __name__ == "__main__":
    register()
