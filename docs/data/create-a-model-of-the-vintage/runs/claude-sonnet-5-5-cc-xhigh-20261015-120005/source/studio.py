"""Studio set (floor, world, lights, camera) - render-only, not exported to the GLB."""
import bpy, math
from math import radians
from mathutils import Vector

scene = bpy.context.scene

# remove the default cube / camera / light and any previous studio
for n in ('Cube', 'Camera', 'Light'):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
if 'Studio' in bpy.data.collections:
    for o in list(bpy.data.collections['Studio'].objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(bpy.data.collections['Studio'])
studio = bpy.data.collections.new('Studio')
scene.collection.children.link(studio)


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# backdrop: seamless sweep (floor curving up into a back wall)
import bmesh
from math import pi, sin, cos
prof = [(-4.0, 0.0), (0.9, 0.0)]
R_SWEEP = 0.9
for i in range(1, 13):
    t = (pi / 2) * i / 12
    prof.append((0.9 + R_SWEEP * sin(t), R_SWEEP * (1 - cos(t))))
prof.append((0.9 + R_SWEEP, 3.5))
bm = bmesh.new()
rows = [[bm.verts.new((-4, y, z)), bm.verts.new((4, y, z))] for (y, z) in prof]
for i in range(len(rows) - 1):
    bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
me = bpy.data.meshes.new('Backdrop')
bm.to_mesh(me)
bm.free()
me.shade_smooth()
floor = bpy.data.objects.new('Backdrop', me)
studio.objects.link(floor)
fm = bpy.data.materials.get('Studio_Floor') or bpy.data.materials.new('Studio_Floor')
fm.use_nodes = True
b = fm.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.44, 0.35, 0.27, 1)
b.inputs['Roughness'].default_value = 0.9
me.materials.append(fm)

# world
w = scene.world or bpy.data.worlds.new('World')
scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.35, 0.33, 0.30, 1)
bg.inputs['Strength'].default_value = 0.5


def light(name, kind, loc, energy, size, target=(0, 0, 0.18), color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'AREA':
        ld.size = size
    ob = bpy.data.objects.new(name, ld)
    studio.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    return ob


light('Key', 'AREA', (0.55, -0.9, 1.0), 26, 0.8, color=(1.0, 0.96, 0.9))
light('Fill', 'AREA', (-0.9, -0.5, 0.35), 12, 0.8, color=(0.85, 0.92, 1.0))
light('Rim', 'AREA', (0.2, 0.9, 0.7), 28, 0.6)
light('Top', 'AREA', (0.0, -0.1, 1.2), 8, 0.6)

cam_data = bpy.data.cameras.new('Camera')
cam_data.lens = 70
cam_data.sensor_width = 36
cam = bpy.data.objects.new('Camera', cam_data)
studio.objects.link(cam)
scene.camera = cam


def set_cam(loc, target=(0, 0, 0.19), lens=70):
    cam.location = loc
    cam_data.lens = lens
    aim(cam, target)


set_cam((0.45, -0.85, 0.40), target=(0, 0, 0.20), lens=55)

r = scene.render
r.resolution_x = 1280
r.resolution_y = 1024
r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'


def render(path, loc, target=(0, 0, 0.20), lens=55, samples=64, res=(1280, 1024), yaw=0.0):
    root = bpy.data.objects.get('Robie')
    if root:
        root.rotation_euler.z = radians(yaw)
    set_cam(loc, target, lens)
    scene.eevee.taa_render_samples = samples
    scene.eevee.shadow_ray_count = 4
    scene.eevee.shadow_step_count = 16
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
