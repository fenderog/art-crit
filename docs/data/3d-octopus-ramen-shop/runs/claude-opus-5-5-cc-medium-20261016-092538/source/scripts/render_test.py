import os, bpy
s = bpy.context.scene
s.render.resolution_percentage = 50
for cam in ("CamMain", "CamClose"):
    s.camera = bpy.data.objects[cam]
    s.render.filepath = os.path.abspath(f"scripts/test_{cam}.png")
    bpy.ops.render.render(write_still=True)
s.camera = bpy.data.objects["CamMain"]
