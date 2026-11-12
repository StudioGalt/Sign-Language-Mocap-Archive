import sys
import bpy


import os
# The folder holding anchor.py: edit this, or set the GALT_WORKSPACE environment variable.
script_path = os.path.join(os.environ.get("GALT_WORKSPACE", "H:/Galt Workspace"), "Scripts")
if script_path not in sys.path:
    sys.path.append(script_path)

import anchor


anchor.keyframe_rig_with_als("root", first_anchor=110, last_anchor=223)


