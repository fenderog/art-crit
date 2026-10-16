# Entry point: exec this file inside Blender. Rebuilds the whole scene from scratch.
import bpy, os, time
ROOT = os.path.abspath(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd())
SCRIPTS = os.path.join(ROOT, "scripts")
G = globals()
for mod in ("lib.py", "textures.py", "booth.py", "kitchen.py", "octopus.py", "environment.py"):
    path = os.path.join(SCRIPTS, mod)
    if os.path.exists(path):
        exec(compile(open(path).read(), path, "exec"), G)

STAGES = G.get("STAGES", ("booth", "kitchen", "octopus", "env"))
t0 = time.time()
clear_scene()
info = {}
if "booth" in STAGES:
    info["booth"] = build_booth()
if "kitchen" in STAGES and "build_kitchen" in G:
    info["kitchen"] = build_kitchen(info["booth"]["mats"])
if "octopus" in STAGES and "build_octopus" in G:
    info["octopus"] = build_octopus(info)
if "env" in STAGES and "build_environment" in G:
    info["env"] = build_environment(info)
BUILD_TIME = time.time() - t0
