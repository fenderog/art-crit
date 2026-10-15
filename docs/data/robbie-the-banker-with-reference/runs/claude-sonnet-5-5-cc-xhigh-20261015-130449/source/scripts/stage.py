import math, bpy, bmesh
from mathutils import Vector

CM = 0.01
scn = bpy.context.scene

# remove any previous stage
for ob in list(bpy.data.objects):
    if ob.name.startswith("Stage_") or ob.name in ("Camera", "Light", "Cube"):
        bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    if c.name == "Studio":
        bpy.data.collections.remove(c)
for cam in list(bpy.data.cameras):
    if cam.users == 0:
        bpy.data.cameras.remove(cam)
for l in list(bpy.data.lights):
    if l.users == 0:
        bpy.data.lights.remove(l)

studio = bpy.data.collections.new("Studio")
scn.collection.children.link(studio)

# ---- round cyclorama backdrop (lathe of a floor + cove + wall profile)
bm = bmesh.new()
prof = [(0.0005, 0.0), (1.5, 0.0)]
R = 0.9
for i in range(1, 17):
    a = math.pi / 2 * i / 16
    prof.append((1.5 + R * math.sin(a), R * (1 - math.cos(a))))
prof.append((1.5 + R, R + 3.0))
SEG = 96
rings = []
for (rr, z) in prof:
    ring = []
    for k in range(SEG):
        ang = 2 * math.pi * k / SEG
        ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), z)))
    rings.append(ring)
for i in range(len(rings) - 1):
    for k in range(SEG):
        bm.faces.new((rings[i][k], rings[i][(k + 1) % SEG], rings[i + 1][(k + 1) % SEG], rings[i + 1][k]))
me = bpy.data.meshes.new("Stage_Backdrop")
for f in bm.faces:
    f.smooth = True
bm.to_mesh(me); bm.free()
back = bpy.data.objects.new("Stage_Backdrop", me)
studio.objects.link(back)
mat = bpy.data.materials.new("Backdrop")
mat.use_nodes = True
b = mat.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.30, 0.285, 0.27, 1)
b.inputs["Roughness"].default_value = 0.55
me.materials.append(mat)

# ---- world
w = scn.world or bpy.data.worlds.new("World")
scn.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.55, 0.52, 0.48, 1)
bg.inputs["Strength"].default_value = 0.25

# ---- lights
def area(name, loc, target, size, energy, color=(1, 1, 1), shape='RECTANGLE', sy=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.color = color
    ld.shape = shape
    ld.size = size
    if shape == 'RECTANGLE':
        ld.size_y = sy or size
    ob = bpy.data.objects.new(name, ld)
    studio.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob

T = (0, 0, 0.2)
area("Stage_Key", (-0.75, -0.95, 0.85), T, 0.9, 130, (1.0, 0.95, 0.88), sy=0.6)
area("Stage_Fill", (1.1, -0.8, 0.35), T, 1.0, 45, (0.85, 0.92, 1.0))
area("Stage_Rim", (0.6, 0.9, 0.75), T, 0.7, 130, (1.0, 0.97, 0.9))
area("Stage_Top", (0.0, -0.1, 1.3), T, 0.8, 40, (1, 1, 1))

# ---- camera
def make_cam(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.dof.use_dof = False
    ob = bpy.data.objects.new(name, cd)
    studio.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob

cam = make_cam("Stage_Camera", (0.36, -1.0, 0.33), (0.0, -0.01, 0.2), 75)
scn.camera = cam

# ---- render settings
r = scn.render
r.engine = 'CYCLES'
r.resolution_x = 1400
r.resolution_y = 1500
r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'
r.film_transparent = False
scn.cycles.samples = 96
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 8
scn.cycles.device = 'CPU'
try:
    scn.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception as e:
    pass
scn.view_settings.exposure = -0.3
