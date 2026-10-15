# Studio: floor, soft lights, cameras and render helpers for the Robie scene.
import bpy, math
from mathutils import Vector

def _coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def setup_studio(scale=1.0):
    c = _coll("Studio")
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    sc = bpy.context.scene

    # seamless cyclorama: floor curving up into a surrounding wall
    prof = [(0.0, 0.0), (7.0, 0.0)]
    for i in range(1, 13):
        a = math.radians(-90 + 90 * i / 12)
        prof.append((7.0 + 4.0 * math.cos(a), 4.0 + 4.0 * math.sin(a)))
    prof.append((11.0, 14.0))
    segs = 96
    verts, faces = [(0.0, 0.0, 0.0)], []
    for r, z in prof[1:]:
        for j in range(segs):
            a = 2 * math.pi * j / segs
            verts.append((r * scale * math.cos(a), r * scale * math.sin(a), z * scale))
    for j in range(segs):
        faces.append((0, 1 + j, 1 + (j + 1) % segs))
    for i in range(len(prof) - 2):
        a0, a1 = 1 + i * segs, 1 + (i + 1) * segs
        for j in range(segs):
            k = (j + 1) % segs
            faces.append((a0 + j, a1 + j, a1 + k, a0 + k))
    me = bpy.data.meshes.new("Cyclorama")
    me.from_pydata(verts, [], faces)
    me.shade_smooth()
    fl = bpy.data.objects.new("Cyclorama", me)
    c.objects.link(fl)
    m = bpy.data.materials.get("Studio Floor") or bpy.data.materials.new("Studio Floor")
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.80, 0.80, 0.81, 1)
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Emission Color"].default_value = (0.92, 0.92, 0.94, 1)
    b.inputs["Emission Strength"].default_value = 0.22
    me.materials.append(m)

    # world: soft neutral studio ambience
    w = bpy.data.worlds.get("Studio World") or bpy.data.worlds.new("Studio World")
    sc.world = w
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.86, 0.87, 0.89, 1)
    bg.inputs["Strength"].default_value = 0.4

    def area(name, loc, size, power, color=(1, 1, 1)):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.size = size * scale
        ld.energy = power * scale * scale
        ld.color = color
        ob = bpy.data.objects.new(name, ld)
        c.objects.link(ob)
        ob.location = Vector(loc) * scale
        d = Vector((0, 0, 0.55 * scale)) - ob.location
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return ob

    area("Key Light", (-3.2, -4.2, 4.6), 3.2, 900, (1.0, 0.97, 0.93))
    area("Fill Light", (4.6, -2.6, 2.2), 4.0, 380, (0.93, 0.96, 1.0))
    area("Rim Light", (1.2, 4.8, 4.2), 2.6, 600)
    area("Top Light", (0.0, 0.0, 6.0), 4.0, 250)

def set_camera(az_deg, el_deg, dist, target=(0, 0, 0.55), lens=70, name="Camera",
               scale=1.0):
    c = _coll("Studio")
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        c.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_start = 0.01 * scale
    cam.data.clip_end = 200 * scale
    az, el = math.radians(az_deg), math.radians(el_deg)
    t = Vector(target) * scale
    # az = 0 looks at the front of the robot (camera on -Y)
    p = t + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist * scale
    cam.location = p
    cam.rotation_euler = (t - p).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam

def render(path, res=(900, 900), samples=64, engine='CYCLES', fmt='PNG', quality=92):
    sc = bpy.context.scene
    sc.render.engine = engine
    if engine == 'CYCLES':
        sc.cycles.device = 'GPU'
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 8
        sc.cycles.transmission_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = -0.25
    sc.render.image_settings.file_format = fmt
    if fmt == 'JPEG':
        sc.render.image_settings.quality = quality
    else:
        sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path
