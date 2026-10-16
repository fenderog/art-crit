import os, bpy
s = bpy.context.scene
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'JPEG'
s.render.image_settings.quality = 90
for cam, fn in (("CamMain", "octopus_ramen_booth.jpg"), ("CamClose", "octopus_chef_closeup.jpg")):
    s.camera = bpy.data.objects[cam]
    s.render.filepath = os.path.abspath("output/" + fn)
    bpy.ops.render.render(write_still=True)
s.camera = bpy.data.objects["CamMain"]
bpy.ops.export_scene.gltf(filepath=os.path.abspath("output/octopus_ramen_booth.glb"), export_format='GLB',
                          export_apply=True, export_cameras=False, export_lights=False)
