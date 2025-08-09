# blender/game/bootstrap.py  (you can also paste this as an internal text)
import sys, os
try:
    import bge
    root = bge.logic.expandPath("//")        # folder containing the .blend
except Exception:
    import bpy
    root = os.path.dirname(bpy.data.filepath)

# Ensure the 'blender' folder is on sys.path so 'game.*' imports work
if root and root not in sys.path:
    sys.path.insert(0, root)                 # now 'import game.actor_controller' works
