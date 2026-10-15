"""Small modelling helpers for the Robbie the Banker build (all arguments in centimetres)."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

CM = 0.01
STATE = {"coll": None, "parent": None}


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras,
                  bpy.data.lights, bpy.data.images):
        for d in list(block):
            block.remove(d)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    STATE["coll"] = c
    return c


def make_mat(name, color, metallic=0.0, rough=0.5, extra=None, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    for k, v in (extra or {}).items():
        b.inputs[k].default_value = v
    m.diffuse_color = (*color, 1.0)
    m.metallic = metallic
    m.roughness = rough
    return m


def group(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.02
    e.location = Vector(loc) * CM
    STATE["coll"].objects.link(e)
    if parent is not None:
        attach(e, parent)
    return e


def attach(ob, parent):
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Translation(-Vector(parent.location))
    # parent.location is relative to its own parent; groups here are only nested at the origin
    # except for the hat pivot, which is a direct child of the root at the origin.


def use(parent):
    STATE["parent"] = parent


def _finish(name, bm, mat, loc, rot, scale, smooth=True, mods=None):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    STATE["coll"].objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    ob.location = Vector(loc) * CM
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    ob.scale = scale
    if STATE["parent"] is not None:
        attach(ob, STATE["parent"])
    for kind, kw in (mods or []):
        md = ob.modifiers.new(kind.title(), kind)
        for k, v in kw.items():
            setattr(md, k, v)
    return ob


def _wn():
    return ("WEIGHTED_NORMAL", dict(mode='FACE_AREA', keep_sharp=True, weight=50))


def _bevel(width, seg):
    return ("BEVEL", dict(width=width * CM, segments=seg, limit_method='ANGLE',
                          angle_limit=math.radians(32)))


def box(name, size, loc, mat, bevel=0.15, seg=3, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0] * CM
        v.co.y *= size[1] * CM
        v.co.z *= size[2] * CM
    mods = []
    if bevel > 0:
        mods.append(_bevel(bevel, seg))
    mods.append(_wn())
    return _finish(name, bm, mat, loc, rot, (1, 1, 1), mods=mods)


def cyl(name, r, h, loc, mat, r2=None, rot=(0, 0, 0), seg=48, bevel=0.0, bseg=2, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r * CM, radius2=(r if r2 is None else r2) * CM, depth=h * CM)
    mods = []
    if bevel > 0:
        mods.append(_bevel(bevel, bseg))
    mods.append(_wn())
    return _finish(name, bm, mat, loc, rot, scale, mods=mods)


def sph(name, r, loc, mat, scale=(1, 1, 1), rot=(0, 0, 0), seg=32, rings=16):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r * CM)
    return _finish(name, bm, mat, loc, rot, scale)


def torus(name, R, r, loc, mat, rot=(0, 0, 0), seg=48, rseg=12):
    bm = bmesh.new()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * math.cos(a) * CM, rr * math.sin(a) * CM, r * math.sin(b) * CM)))
        verts.append(ring)
    for i in range(seg):
        for j in range(rseg):
            bm.faces.new((verts[i][j], verts[i][(j + 1) % rseg],
                          verts[(i + 1) % seg][(j + 1) % rseg], verts[(i + 1) % seg][j]))
    return _finish(name, bm, mat, loc, rot, (1, 1, 1))


def limb(name, p0, p1, r, mat, r2=None, seg=32, bevel=0.0):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    ob = cyl(name, r, d.length, tuple((p0 + p1) / 2), mat, r2=r2, seg=seg, bevel=bevel)
    ob.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    return ob


def catmull(pts, n=8):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Vector(pts[-1]))
    return out


def tube(name, pts, radii, mat, sides=12, n=8):
    pts = [Vector(p) for p in pts]
    path = catmull(pts, n)
    rad = [v.x for v in catmull([Vector((r, 0, 0)) for r in radii], n)]
    bm = bmesh.new()
    rings = []
    N = None
    for i, p in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, len(path) - 1)]
        T = (b - a).normalized()
        if N is None:
            ref = Vector((0, 0, 1)) if abs(T.z) < 0.9 else Vector((1, 0, 0))
            N = (ref - T * ref.dot(T)).normalized()
        else:
            N = (N - T * N.dot(T)).normalized()
        B = T.cross(N)
        ring = []
        for s in range(sides):
            ang = 2 * math.pi * s / sides
            q = p + (N * math.cos(ang) + B * math.sin(ang)) * rad[i]
            ring.append(bm.verts.new(q * CM))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for s in range(sides):
            bm.faces.new((rings[i][s], rings[i][(s + 1) % sides],
                          rings[i + 1][(s + 1) % sides], rings[i + 1][s]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return _finish(name, bm, mat, (0, 0, 0), (0, 0, 0), (1, 1, 1))


def text_mesh(name, body, size, loc, mat, rot=(90, 0, 0), extrude=0.05, scale_x=1.0):
    cu = bpy.data.curves.new(name + "_cu", 'FONT')
    cu.body = body
    cu.size = size * CM
    cu.extrude = extrude * CM
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.resolution_u = 6
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    STATE["coll"].objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    me.name = name
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    STATE["coll"].objects.link(ob)
    ob.location = Vector(loc) * CM
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    ob.scale = (scale_x, 1, 1)
    if STATE["parent"] is not None:
        attach(ob, STATE["parent"])
    return ob


def coin(name, loc, r, mat, rot=(0, 0, 0), h=0.34):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=56,
                          radius1=r * CM, radius2=r * CM, depth=h * CM)
    caps = [f for f in bm.faces if abs(f.normal.z) > 0.99]
    res = bmesh.ops.inset_region(bm, faces=caps, thickness=0.2 * CM, depth=-0.06 * CM)
    # keep rim edges crisp-ish, everything else smooth
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35):
            e.smooth = False
    ob = _finish(name, bm, mat, loc, rot, (1, 1, 1), mods=[_wn()])
    return ob


def bake_modifiers(ob):
    if not ob.modifiers:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    mats = list(old.materials)
    ob.modifiers.clear()
    ob.data = me
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    bpy.data.meshes.remove(old)


def boolean_cut(target, cutter):
    """Difference-cut `cutter` out of `target`, evaluated before the weighted-normal modifier."""
    md = target.modifiers.new("Cut", 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.object = cutter
    md.solver = 'EXACT'
    last = len(target.modifiers) - 1
    wn = [m.type for m in target.modifiers].index('WEIGHTED_NORMAL')
    target.modifiers.move(last, wn)
