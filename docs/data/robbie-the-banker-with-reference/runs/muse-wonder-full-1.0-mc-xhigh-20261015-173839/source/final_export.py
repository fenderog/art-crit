import bpy, os
from mathutils import Vector

scene = bpy.context.scene
os.makedirs('output', exist_ok=True)

# Seamless studio: ground as shadow catcher only
ground = bpy.data.objects.get('Ground')
if ground:
    try:
        ground.is_shadow_catcher = True
    except Exception as e:
        print('shadow catcher', e)
world = bpy.data.worlds['World']
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.93, 0.93, 0.93, 1)
bg.inputs[1].default_value = 0.5

cam = bpy.data.objects['Camera']
def set_cam(loc, target=(0, -0.08, 0.82)):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

scene.cycles.samples = 96
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200

views = {
    'robie_hero.png': ((2.35, -3.05, 1.85), (0, -0.08, 0.82)),
    'robie_front.png': ((0.0, -3.9, 1.30), (0, -0.08, 0.82)),
    'robie_back_top.png': ((-1.7, 2.4, 3.1), (0, 0.0, 0.95)),
}
for fname, (loc, tgt) in views.items():
    set_cam(loc, tgt)
    scene.render.filepath = 'output/' + fname
    bpy.ops.render.render(write_still=True)

# Convert text / curve objects to meshes for a clean GLB
exclude = {'Ground', 'Camera', 'Key', 'Fill', 'Top'}
robie_objs = [o for o in bpy.data.objects if o.name not in exclude and o.type in ('MESH', 'CURVE', 'FONT')]
bpy.ops.object.select_all(action='DESELECT')
for o in robie_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = robie_objs[0]
bpy.ops.object.convert(target='MESH')
# Re-select after conversion
robie_objs = [o for o in bpy.data.objects if o.name not in exclude and o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in robie_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = robie_objs[0]

bpy.ops.export_scene.gltf(
    filepath=os.path.abspath('output/robie_the_banker.glb'),
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_draco_mesh_compression_enable=False,
)
bpy.ops.wm.save_as_mainfile(filepath='robie.blend')
result = {'exported': [o.name for o in robie_objs], 'glb_size': os.path.getsize('output/robie_the_banker.glb')}
