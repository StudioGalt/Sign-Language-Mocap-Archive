# Pipeline changelog

Notes kept in the Galtis working file, newest first, copied as written. Dates without a year are in the year above them.

```text
May 18, 2026
Removed numpy in 1) Importer

Added arm reverse bones to deal with certain retargeting issue for MMD/PMX.

April 23, 2026

Add bones to fake soma bones help soam retargeting


February 1,

Refactor 5 exporter into 2 scripts for easy maintenance.

Janaury 17th, 2026
Added Reincarnator 1,7 to create a workflow for updating old animations.


January 9, 2026
Added limit location to hip bone,
Add metahuman to exporter

December 28

Added thigh bones openpose mapping
Added mixamo to exporter.
Retired Triple 6 script

December 5, 2025,

Updated scripts to 5.0.0
Updated shoulderinte driver



August 23, Off hand updated

August 23, updated quickener

August 1, Moved to 4.5.1
2a, added interpreter Neutral as frame 1 and frame last.

July 19th, updated to 4.5
Move Camera back to

July 9th, Importer, add in front.
7 Bundler, repalced MP4 with Webm

July 5th, added U) Check for Invalid Drivers, and deleted 88 invalid drivers. Embarassing but better late than never.

July 4th, Moved to 4.5 Beta, fixes crashes for some reason??

June 17, Added export option 3) Pose Magic

June 15,
Fixed Working file should be zipped properly now.


June 14,  2a removed excess actions
Locked FK-IK switch, loc, rot, and scale.

June 8,

Replaced caption workflow in 5, with VSE in native blender, few python package necessary.

June 5,
Removed gif from exporter, and removed dependency to transition to 4.4.

May 21
Added frame budget to 3) Pose Magic

May 20th
Update 3 Pose Magic to include Motion Name, Pose Name, Frame Count


May 19th

Updated Left Ik Drivers

Added finger snap for left IK fingers 2b.

May 14th
Added Save to working copy in 2a) and 2b)

Rough Workflow is now

Unedited (animation in file, and file named)
Working Copy (One with edits prebake, no pose library)
Cleaned (Post bake, A backup copy, to help finished is ever deleted or corrupted)
Finished (Completed baked animation, with excess data removed, has pose library)

April 28th
Updated Pose Magic to output text file with fk transforms.

April 23rd

Updated unreal bone rolls


April 11th,

Add copy rotation to FK4 bones,
Added Pole anchors to Finger IK


April 6th,

Realigned finger rolls,

Order of operation was intermediate -> FK -> IK
unreal/deform should remain uneffect as they are copied from unreal mannequin.


April 5th,

Updated Snapper script.

March 30th,
Updated following scripts to no longer use hardcoding
1) Importer
2a) Superset New
2b) Baker Combined
3) Pose Magic
4) Archive II New
5) Exporter
6) Triple 6 New
7) Bundler

March 10th,
Add quicker, to remove dead frames at start of animation

 added output for mannequin/metahumans Manny and Quinn with T Pose and A Pose

March 1st, 2025

Added Fractional Paste Script

Consolidate FK to IK, IK to FK scripts into Snapper WIP, removed other snapper scripts.

Feb 21, 2025

Updated shortener


February 17, 2025

Added turn off solo layers to Shortener.

February 16, 2025

Merge 2b and 2c



February 13, 2025

Update Importer to accept animdata that is missing hands.

February 9, 2025

Added Shortener script, which allows quick way of eliminating extras frames if intial cut has too much dead time.


Janaury 18, 2025

Added U) Offhand script.
Script designed to clean offhand data (left in this case) for single hand motions.

Added U) Get Selected Bone Names, grabs all bone names selected and prints them.



Janaury 1, 2025

Added Zip export to 7) bundler,


December 26th,

Add Fake hands bones to allow rigify export mapping.

Update Rigify Export






December 14th,
updated Exporter script to use moviepy 2.0.2 from 1.0.3
All scripts work 4.3.1






November1 update:
Uncapped pose magic, can now 50 poses.

Updated exporter to handle double digit mkv files.








September 1 update:
Improved Eyelid weight painting.
Moved Eyes back in Y direction, to reduces overlap with Eye Lids.
Imrpoved hadn topology

Updated Script 6, to align with default mixamo output.

Locked all Shapekeys and vertex groups

Moved shoulder track mechanism from hand Ik to Handintermediate


Changed IK shoulder control to intermediate hand bone

2) added a turn off for solo layers
6) Updated Mixamo mapping
```
