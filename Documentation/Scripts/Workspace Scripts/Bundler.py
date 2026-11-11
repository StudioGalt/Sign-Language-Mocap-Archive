import bpy
import shutil
import os
import zipfile
import glob
from pathlib import Path


#This bundles everything into an upload folder to put on Github.
# Using Blender 5.1.0
# Last tested March 18,  2025 

file_name=bpy.path.basename(bpy.context.blend_data.filepath)
fnsplit = file_name.split()
Stamp = " ".join(fnsplit[:-1])
print(Stamp)

blend_file_dir = os.path.dirname(bpy.data.filepath)
parent_dir = os.path.dirname(blend_file_dir)

BaseUpload= blend_file_dir+'\\'+ Stamp + ' Upload'

if not os.path.exists(BaseUpload):
    os.makedirs(BaseUpload)

NoMeshMini=Stamp+ " No Mesh Mini.fbx" 

NoMeshMini1=blend_file_dir+'\\'+ NoMeshMini
NoMeshMini2=BaseUpload+'\\'+NoMeshMini


if os.path.exists(NoMeshMini1):
    shutil.move(NoMeshMini1, NoMeshMini2)
    print(f"File moved from {NoMeshMini1} to {NoMeshMini2}")
else:
    print(f"File does not exist: {NoMeshMini1}")



NoMeshFull=Stamp+ " No Mesh Full.fbx" 

NoMeshFull1=blend_file_dir+'\\'+ NoMeshFull
NoMeshFull2=BaseUpload+'\\'+NoMeshFull

if os.path.exists(NoMeshFull1):
    shutil.move(NoMeshFull1, NoMeshFull2)
    print(f"File moved from {NoMeshFull1} to {NoMeshFull2}")
else:
    print(f"File does not exist: {NoMeshFull1}")



MKV=Stamp+ ".mkv" 

MKV1=blend_file_dir+'\\'+ MKV
MKV2=BaseUpload+'\\'+MKV

if os.path.exists(MKV1):
    shutil.move(MKV1, MKV2)
    print(f"File moved from {MKV1} to {MKV2}")
else:
    print(f"File does not exist: {MKV1}")


Mesh=Stamp+ " Mesh.fbx" 

Mesh1=blend_file_dir+'\\'+ Mesh
Mesh2=BaseUpload+'\\'+Mesh

if os.path.exists(Mesh1):
    shutil.move(Mesh1, Mesh2)
    print(f"File moved from {Mesh1} to {Mesh2}")
else:
    print(f"File does not exist: {Mesh1}")


Readme=Stamp+ " ReadMe.txt" 

Readme1=blend_file_dir+'\\'+ Readme
Readme2=BaseUpload+'\\'+Readme

if os.path.exists(Readme1):
    shutil.move(Readme1, Readme2)
    print(f"File moved from {Readme1} to {Readme2}")
else:
    print(f"File does not exist: {Readme1}")



Framelog=Stamp+ " Framelog.txt" 

Framelog1=blend_file_dir+'\\'+ Framelog
Framelog2=BaseUpload+'\\'+Framelog

if os.path.exists(Framelog1):
    shutil.move(Framelog1, Framelog2)
    print(f"File moved from {Framelog1} to {Framelog2}")
else:
    print(f"File does not exist: {Framelog1}")


Mix=Stamp+ " Mixamo TPose.fbx" 

Mix1=blend_file_dir+'\\'+ Mix
Mix2=BaseUpload+'\\'+Mix

if os.path.exists(Mix1):
    shutil.move(Mix1, Mix2)
    print(f"File moved from {Mix1} to {Mix2}")
else:
    print(f"File does not exist: {Mix2}")
    



ShapeKeys=Stamp+ " ShapeKeys.txt" 

ShapeKeys1=blend_file_dir+'\\'+ ShapeKeys
ShapeKeys2=BaseUpload+'\\'+ShapeKeys

if os.path.exists(ShapeKeys1):
    shutil.move(ShapeKeys1, ShapeKeys2)
    print(f"File moved from {ShapeKeys1} to {ShapeKeys2}")
else:
    print(f"File does not exist: {ShapeKeys2}")

webm=Stamp+ " Captions.webm" 

webm1=blend_file_dir+'\\'+ webm
webm2=BaseUpload+'\\'+webm

if os.path.exists(webm1):
    shutil.move(webm1, webm2)
    print(f"File moved from {webm1} to {webm2}")
else:
    print(f"File does not exist: {webm2}")
    




RigAPose=Stamp+ " Rigify APose.fbx"

RigAPose1=blend_file_dir+'\\'+ RigAPose
RigAPose2=BaseUpload+'\\'+RigAPose

if os.path.exists(RigAPose1):
    shutil.move(RigAPose1, RigAPose2)
    print(f"File moved from {RigAPose1} to {RigAPose2}")
else:
    print(f"File does not exist: {RigAPose2}")
    
    
RigTPose=Stamp+ " Rigify TPose.fbx"

RigTPose1=blend_file_dir+'\\'+ RigTPose
RigTPose2=BaseUpload+'\\'+RigTPose

if os.path.exists(RigTPose1):
    shutil.move(RigTPose1, RigTPose2)
    print(f"File moved from {RigTPose1} to {RigTPose2}")
else:
    print(f"File does not exist: {RigTPose2}")


MannyTPose=Stamp+ " Manny TPose.fbx"

MannyTPose1=blend_file_dir+'\\'+ MannyTPose
MannyTPose2=BaseUpload+'\\'+MannyTPose

if os.path.exists(MannyTPose1):
    shutil.move(MannyTPose1, MannyTPose2)
    print(f"File moved from {MannyTPose1} to {MannyTPose2}")
else:
    print(f"File does not exist: {MannyTPose2}")



MannyAPose=Stamp+ " Manny APose.fbx"

MannyAPose1=blend_file_dir+'\\'+ MannyAPose
MannyAPose2=BaseUpload+'\\'+MannyAPose

if os.path.exists(MannyAPose1):
    shutil.move(MannyAPose1, MannyAPose2)
    print(f"File moved from {MannyAPose1} to {MannyAPose2}")
else:
    print(f"File does not exist: {MannyTPose2}")

MannyTPose=Stamp+ " Manny TPose.fbx"

MannyTPose1=blend_file_dir+'\\'+ MannyTPose
MannyTPose2=BaseUpload+'\\'+MannyTPose

if os.path.exists(MannyTPose1):
    shutil.move(MannyTPose1, MannyTPose2)
    print(f"File moved from {MannyTPose1} to {MannyTPose2}")
else:
    print(f"File does not exist: {MannyTPose2}")
    


QuinnTPose=Stamp+ " Quinn TPose.fbx"

QuinnTPose1=blend_file_dir+'\\'+ QuinnTPose
QuinnTPose2=BaseUpload+'\\'+QuinnTPose

if os.path.exists(QuinnTPose1):
    shutil.move(QuinnTPose1, QuinnTPose2)
    print(f"File moved from {QuinnTPose1} to {QuinnTPose2}")
else:
    print(f"File does not exist: {QuinnTPose2}")



QuinnAPose=Stamp+ " Quinn APose.fbx"

QuinnAPose1=blend_file_dir+'\\'+ QuinnAPose
QuinnAPose2=BaseUpload+'\\'+QuinnAPose

if os.path.exists(QuinnAPose1):
    shutil.move(QuinnAPose1, QuinnAPose2)
    print(f"File moved from {QuinnAPose1} to {QuinnAPose2}")
else:
    print(f"File does not exist: {QuinnTPose2}")




    
    
MetaHumanTPose=Stamp+ " MetaHuman TPose.fbx"

MetaHumanTPose1=blend_file_dir+'\\'+ MetaHumanTPose
MetaHumanTPose2=BaseUpload+'\\'+MetaHumanTPose

if os.path.exists(MetaHumanTPose1):
    shutil.move(MetaHumanTPose1, MetaHumanTPose2)
    print(f"File moved from {MetaHumanTPose1} to {MetaHumanTPose2}")
else:
    print(f"File does not exist: {MetaHumanTPose2}")



MetaHumanAPose=Stamp+ " MetaHuman APose.fbx"

MetaHumanAPose1=blend_file_dir+'\\'+ MetaHumanAPose
MetaHumanAPose2=BaseUpload+'\\'+MetaHumanAPose

if os.path.exists(MetaHumanAPose1):
    shutil.move(MetaHumanAPose1, MetaHumanAPose2)
    print(f"File moved from {MetaHumanAPose1} to {MetaHumanAPose2}")
else:
    print(f"File does not exist: {MetaHumanAPose2}")


BlendFile=blend_file_dir+'\\' + Stamp + ' Finished.blend'

# Define paths
source_file_path = BlendFile  # Current Blender file
destination_dir = os.path.join(BaseUpload, "Blend File")
destination_file_path = os.path.join(destination_dir, os.path.basename(source_file_path))

# Ensure the destination directory exists
BlendFileWorking=blend_file_dir+'\\' + Stamp + ' Working.blend'
source_file_path_working = BlendFileWorking
destination_dir_working = os.path.join(BaseUpload, "Blend File")
destination_file_path_working = os.path.join(destination_dir_working, os.path.basename(source_file_path_working))

# 1. FIX: Ensure the directory exists (not the file path)
if not os.path.exists(destination_dir_working):
    os.makedirs(destination_dir_working, exist_ok=True)

# Copy the Blender file
shutil.copy2(source_file_path_working, destination_file_path_working)
print(f"Blender file copied to: {destination_file_path_working}")

# 2. FIX: Use the correct destination directory variable
zip_file_path_working = os.path.join(
    destination_dir_working, 
    os.path.splitext(os.path.basename(source_file_path_working))[0] + '.zip'
)

try:
    # Create the zip archive
    with zipfile.ZipFile(zip_file_path_working, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(destination_file_path_working, os.path.basename(destination_file_path_working))
    print(f"Blender file zipped to: {zip_file_path_working}")

finally:
    # 3. FIX: Actually call the delete command
    if os.path.exists(destination_file_path_working):
        os.remove(destination_file_path_working)
        print(f"Unzipped file deleted: {destination_file_path_working}")

target_folder=BaseUpload+'\\'+'FBX Files'
os.makedirs(target_folder, exist_ok=True)

target_folder_full=os.path.join(target_folder, "Full")
target_folder_rigify=os.path.join(target_folder, "Rigify")
target_folder_unreal_engine=os.path.join(target_folder, "Unreal_Engine")
target_folder_mixamo=os.path.join(target_folder, "Mixamo")
target_folder_original=os.path.join(target_folder, "Original")

os.makedirs(target_folder_full, exist_ok=True)
os.makedirs(target_folder_rigify, exist_ok=True)
os.makedirs(target_folder_unreal_engine, exist_ok=True)
os.makedirs(target_folder_mixamo, exist_ok=True)
os.makedirs(target_folder_original, exist_ok=True)

# The take's Reference FBX (the MetaHuman's motion on the Xsens skeleton, made by export_reference_fbx.py): copied
# in with the originals; the take's folder keeps it, for running the Galtis import again
ReferenceFBX = os.path.join(blend_file_dir, Stamp + " Reference.fbx")
if os.path.exists(ReferenceFBX):
    shutil.copy2(ReferenceFBX, os.path.join(target_folder_original, os.path.basename(ReferenceFBX)))
    print(f"File copied from {ReferenceFBX} to {target_folder_original}")
else:
    print(f"File does not exist: {ReferenceFBX}")

all_files = os.listdir(BaseUpload)

# Filter out only the .fbx files
fbx_files = [file for file in all_files if file.endswith(".fbx")]

# Move each .fbx file to the "FBX files" folder
for fbx_file in fbx_files:
    source_path = os.path.join(BaseUpload, fbx_file)
    if any(substring in fbx_file for substring in ["No Mesh Full"]):
        target_path = os.path.join(target_folder_full, fbx_file)
        shutil.move(source_path, target_path)
    elif any(substring in fbx_file for substring in ["Rigify"]):
        target_path = os.path.join(target_folder_rigify, fbx_file)
        shutil.move(source_path, target_path)
    elif any(substring in fbx_file for substring in ["Mixamo"]):
        target_path = os.path.join(target_folder_mixamo, fbx_file)
        shutil.move(source_path, target_path)
    elif any(substring in fbx_file for substring in ["Mannequin", "Quinn", "Manny", "MetaHuman"]):
        target_path = os.path.join(target_folder_unreal_engine, fbx_file)
        shutil.move(source_path, target_path)
    elif any(substring in fbx_file for substring in ["Mesh"]):
        target_path = os.path.join(target_folder_full, fbx_file)
        shutil.move(source_path, target_path)
    else:
        # Default case for files that don't match any condition
        pass
    
source_dir = Path(blend_file_dir)
target_dir = Path(target_folder_original)
for fbx in source_dir.rglob("*.fbx"):
    if "_" in fbx.stem and "-" in fbx.stem:
        dest = target_dir / fbx.name
        if not dest.exists():
            shutil.move(str(fbx), dest)
            
text_folder = os.path.join(BaseUpload, "Documentation")
os.makedirs(text_folder, exist_ok=True)

# Filter out only the .fbx files
txt_files = [file for file in all_files if file.endswith(".txt")]

# Move each .fbx file to the "FBX files" folder
for txt_file in txt_files:
    source_path = os.path.join(BaseUpload, txt_file)
    target_path = os.path.join(text_folder, txt_file)
    shutil.move(source_path, target_path)

gif_files = [file for file in all_files if file.endswith(".gif")]

for gif_file in gif_files:
    source_path = os.path.join(BaseUpload, gif_file)
    target_path = os.path.join(text_folder, gif_file)
    shutil.move(source_path, target_path)


webm_files = [file for file in all_files if file.endswith(".webm")]

for webm_file in webm_files:
    source_path = os.path.join(BaseUpload, webm_file)
    target_path = os.path.join(text_folder, webm_file)
    shutil.move(source_path, target_path)


MKV_files = [file for file in all_files if file.endswith(".mkv")]

for MKV_file in MKV_files:
    source_path = os.path.join(BaseUpload, MKV_file)
    target_path = os.path.join(text_folder, MKV_file)
    shutil.move(source_path, target_path)

pose_folder = os.path.join(BaseUpload, "Poses")
os.makedirs(pose_folder, exist_ok=True)

# Filter out only the .fbx files
pose_files = [file for file in all_files if file.endswith(".blend")]

# Move each .fbx file to the "FBX files" folder
for pose_file in pose_files:
    source_path = os.path.join(BaseUpload, pose_file)
    target_path = os.path.join(pose_folder, pose_file)
    shutil.move(source_path, target_path)
    
source_dir = blend_file_dir
target_dir = BaseUpload+'\\'+"Poses"+'\\'+"JSON"
os.makedirs(target_dir, exist_ok=True)

files = os.listdir(source_dir)

# Filter JSON files
json_files = [f for f in files if f.endswith('.json')]

for file_name in json_files:
    source_file = os.path.join(source_dir, file_name)
    target_file = os.path.join(target_dir, file_name)
    shutil.move(source_file, target_file)

print(f"Moved {len(json_files)} JSON files to '{target_dir}'.")

source_dir = blend_file_dir
target_dir = BaseUpload+'\\'+"Poses"+'\\'+"CSV"
os.makedirs(target_dir, exist_ok=True)

csv_files = [f for f in files if f.endswith('.csv')]

for file_name in csv_files:
    source_file = os.path.join(source_dir, file_name)
    target_file = os.path.join(target_dir, file_name)
    shutil.move(source_file, target_file)

print(f"Moved {len(csv_files)} CSV files to '{target_dir}'.")


source_dir = blend_file_dir
target_dir = blend_file_dir+'\\'+"Scriptable Poses"
os.makedirs(target_dir, exist_ok=True)

files = os.listdir(source_dir)

# Filter JSON files
txt_files = [f for f in files if f.endswith('.txt')]

for file_name in txt_files:
    source_file = os.path.join(source_dir, file_name)
    target_file = os.path.join(target_dir, file_name)
    shutil.move(source_file, target_file)

print(f"Moved {len(txt_files)} txt files to '{target_dir}'.")

import os

# Set the directory you want to clean (use '.' for the current folder)

def delete_blend1_files(directory):
    count = 0
    # os.walk goes through all subfolders as well
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".blend1"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"\nCleanup complete. Total files deleted: {count}")

# Run the function
delete_blend1_files(blend_file_dir)



CopyFolder2= parent_dir + '\\' +'Ready for Upload'+'\\'+Stamp+' Upload'
 
shutil.copytree(BaseUpload, CopyFolder2, dirs_exist_ok=True)
##

#done