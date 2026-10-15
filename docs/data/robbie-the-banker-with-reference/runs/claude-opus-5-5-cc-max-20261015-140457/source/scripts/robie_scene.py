# Studio, camera and render helpers for the Robie model.
import bpy, bmesh, math
from mathutils import Vector

TARGET = Vector((0.0, -0.25, 1.05))


def _coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def setup_studio():
    sc = bpy.context.scene
    coll = _coll("Studio")
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    # 360-degree cove backdrop: floor disc curving up into a cylindrical wall
    bm = bmesh.new()
    prof = [(0.5, 0.0), (6.0, 0.0), (12.0, 0.0), (18.0, 0.0)]
    rb = 7.0
    for k in range(1, 13):
        a = (math.pi / 2) * k / 12
        prof.append((18.0 + rb * math.sin(a), rb - rb * math.cos(a)))
    prof.append((25.0, 40.0))
    seg = 96
    rings = []
    for (r, z) in prof:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg),
                                    r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for j in range(len(rings) - 1):
        for i in range(seg):
            bm.faces.new((rings[j][i], rings[j + 1][i], rings[j + 1][(i + 1) % seg], rings[j][(i + 1) % seg]))
    bm.faces.new(rings[0])
    me = bpy.data.meshes.new("Backdrop")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    mat = bpy.data.materials.get("Backdrop_White") or bpy.data.materials.new("Backdrop_White")
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1)
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    b.inputs["Emission Strength"].default_value = 0.0
    # brighten the backdrop only as seen by the camera (keeps the subject's light unchanged)
    nt = mat.node_tree
    if "BgCamBoost" not in nt.nodes:
        lp = nt.nodes.new("ShaderNodeLightPath")
        mul = nt.nodes.new("ShaderNodeMath")
        mul.name = "BgCamBoost"
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 0.55
        nt.links.new(lp.outputs["Is Camera Ray"], mul.inputs[0])
        nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    me.materials.append(mat)
    ob = bpy.data.objects.new("Backdrop", me)
    coll.objects.link(ob)

    def area(name, loc, size, energy, color=(1, 1, 1), size_y=None):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.energy = energy
        ld.color = color
        if size_y:
            ld.shape = 'RECTANGLE'
            ld.size = size
            ld.size_y = size_y
        else:
            ld.size = size
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        d = (TARGET - Vector(loc)).normalized()
        lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        coll.objects.link(lo)
        return lo

    area("Key", (-6.0, -7.5, 8.0), 7.0, 900)
    area("Fill", (8.0, -6.0, 3.5), 8.0, 300)
    area("Rim", (3.0, 7.0, 7.0), 5.0, 600)
    area("Top", (0.0, -1.0, 11.0), 6.0, 150)

    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1)
    bg.inputs["Strength"].default_value = 0.7
    return coll


def set_camera(name, loc, target=None, lens=60):
    sc = bpy.context.scene
    coll = _coll("Studio")
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        coll.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_start = 0.05
    cam.data.clip_end = 200
    cam.location = loc
    t = TARGET if target is None else Vector(target)
    d = (t - Vector(loc)).normalized()
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    return cam


def orbit(az_deg, el_deg, dist, target=None, lens=60, name="Cam"):
    t = TARGET if target is None else Vector(target)
    az, el = math.radians(az_deg), math.radians(el_deg)
    # az = 0 -> camera in front of robot (-Y); positive az -> toward robot's left (+X)
    loc = t + dist * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return set_camera(name, loc, t, lens)


def render(path, res=800, samples=64, engine='CYCLES', view='Standard', look='None', exposure=-0.3,
           res_y=None):
    sc = bpy.context.scene
    sc.render.engine = engine
    sc.render.resolution_x = res
    sc.render.resolution_y = res_y or res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.film_transparent = False
    if engine == 'CYCLES':
        sc.cycles.device = 'GPU'
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.max_bounces = 8
    sc.view_settings.view_transform = view
    sc.view_settings.look = look
    sc.view_settings.exposure = exposure
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def render_views(prefix, views, res=560, samples=32, **kw):
    """views: list of (tag, az, el, dist, lens)"""
    out = []
    for tag, az, el, dist, lens in views:
        orbit(az, el, dist, lens=lens)
        out.append(render(prefix + tag + ".png", res=res, samples=samples, **kw))
    return out
