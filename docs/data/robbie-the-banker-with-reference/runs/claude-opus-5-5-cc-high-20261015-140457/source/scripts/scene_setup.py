import bpy, math
from mathutils import Vector

sc = bpy.context.scene
for nm in ("Backdrop", "Key", "Fill", "Rim", "Cam"):
    if nm in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[nm], do_unlink=True)

# seamless white sweep backdrop
bm_pts = []
me = bpy.data.meshes.new("Backdrop")
verts, faces = [], []
prof = []
for i in range(25):
    a = i / 24 * math.pi / 2
    prof.append((4 - 2.0 * math.sin(a) + 0.0, 2.0 - 2.0 * math.cos(a)))  # (y, z)
prof = [(-8, 0)] + [(y, z) for y, z in prof] + [(4.0, 8)]
prof = [(-30, 0)] + [(2 + 2.0 * math.sin(i / 24 * math.pi / 2), 2.0 - 2.0 * math.cos(i / 24 * math.pi / 2)) for i in range(25)] + [(4.0, 20)]
for y, z in prof:
    verts += [(-30, y, z), (30, y, z)]
for i in range(len(prof) - 1):
    faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
me.from_pydata(verts, [], faces)
for p in me.polygons:
    p.use_smooth = True
bd = bpy.data.objects.new("Backdrop", me)
sc.collection.objects.link(bd)
m = bpy.data.materials.get("Backdrop") or bpy.data.materials.new("Backdrop")
m.use_nodes = True
b = m.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.78, 0.78, 0.78, 1)
b.inputs["Roughness"].default_value = 0.7
bd.data.materials.append(m)


def area(name, loc, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(ob)
    ob.location = loc
    d = Vector((0, 0, 1.0)) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


area("Key", (-3.5, -4.5, 5.0), 500, 4.0, (1, 0.97, 0.92))
area("Fill", (4.5, -3.5, 2.5), 180, 5.0, (0.92, 0.95, 1))
area("Rim", (1.5, 4.0, 4.5), 250, 3.0)

w = sc.world or bpy.data.worlds.new("World")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.82, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.45

cd = bpy.data.cameras.new("Cam")
cd.lens = 70
cam = bpy.data.objects.new("Cam", cd)
sc.collection.objects.link(cam)
sc.camera = cam


def aim(loc, target=(0, 0, 1.0), lens=70):
    cam.location = loc
    cam.data.lens = lens
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


aim((-3.0, -8.0, 3.2))
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 1200
sc.render.resolution_y = 1200
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
