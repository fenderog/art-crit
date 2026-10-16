sc = bpy.context.scene
# world
w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.05, 0.07, 0.16, 1)
bg.inputs['Strength'].default_value = 1.0


def light(name, kind, loc, energy, color=(1, 1, 1), size=1.0, rot=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
    elif kind == 'POINT':
        l.shadow_soft_size = size
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    sc.collection.objects.link(ob)
    ob.parent = root
    return ob


light("LanternGlowL", 'POINT', (-2.15, -1.75, 3.2), 250, (1.0, 0.45, 0.2), 0.3)
light("LanternGlowR", 'POINT', (2.15, -1.75, 3.2), 250, (1.0, 0.45, 0.2), 0.3)
light("CookingLamp", 'POINT', (0, -0.3, 3.7), 600, (1.0, 0.72, 0.45), 0.4)
light("FillFront", 'AREA', (-2.5, -6.0, 3.0), 350, (0.75, 0.85, 1.0), 4.0,
      rot=(math.radians(80), 0, math.radians(-22)))
light("RimBack", 'POINT', (0, 3.5, 3.0), 400, (0.4, 0.5, 1.0), 0.6)

cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = 42
cam = bpy.data.objects.new("Camera", cam_d)
sc.collection.objects.link(cam)
cam.location = (3.3, -9.2, 3.0)
tgt = Vector((0.0, 0.0, 2.3))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 1600
sc.render.resolution_y = 1000
try:
    sc.eevee.taa_render_samples = 48
except Exception:
    pass
sc.view_settings.view_transform = 'Standard'
