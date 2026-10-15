# Final renders + GLB export for the Robie model.
import bpy, os, math
from mathutils import Vector

REAL_HEIGHT = 0.15  # metres; the toy stands roughly 15 cm tall


def robot_objects():
    return [o for o in bpy.data.collections["Robie"].all_objects]


def robot_bbox():
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    dg = bpy.context.evaluated_depsgraph_get()
    for o in robot_objects():
        if o.type != 'MESH':
            continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            w = oe.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def final_renders(S, out_dir, res=1400, samples=256):
    shots = [
        ("robie_hero_3q", dict(az=-32, el=17, dist=8.6, lens=60, t=(-0.12, -0.35, 1.0))),
        ("robie_front", dict(az=0, el=17, dist=7.7, lens=60, t=(0.0, -0.3, 1.0))),
        ("robie_side", dict(az=-82, el=18, dist=7.8, lens=60, t=(0.0, -0.3, 1.05))),
        ("robie_back_3q", dict(az=152, el=27, dist=8.0, lens=60, t=(-0.22, 0.17, 1.0))),
    ]
    paths = []
    for name, v in shots:
        S["orbit"](v["az"], v["el"], v["dist"], target=v["t"], lens=v["lens"])
        p = os.path.join(out_dir, name + ".png")
        S["render"](p, res=res, samples=samples)
        paths.append(p)
    # face close-up
    S["set_camera"]("Cam", (-1.1, -5.2, 2.75), (0.0, -0.9, 1.92), lens=90)
    p = os.path.join(out_dir, "robie_face_closeup.png")
    S["render"](p, res=res, samples=samples)
    paths.append(p)
    return paths


def export_glb(path):
    coll = bpy.data.collections["Robie"]
    lo, hi = robot_bbox()
    scale = REAL_HEIGHT / hi.z
    root = bpy.data.objects.get("Robie_Banker")
    if root is None:
        root = bpy.data.objects.new("Robie_Banker", None)
        coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.location = (0, 0, 0)
    root.scale = (1, 1, 1)
    for o in coll.objects:
        if o is not root and o.parent is None:
            o.parent = root
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in coll.all_objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_cameras=False,
                              export_lights=False, export_draco_mesh_compression_enable=False,
                              export_animations=False, export_materials='EXPORT')
    info = {"scale": scale, "bbox_units": (tuple(lo), tuple(hi)), "size": os.path.getsize(path)}
    # restore unscaled working scene
    root.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    return info
