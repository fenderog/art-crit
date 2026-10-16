import bpy, bmesh, math, random
from mathutils import Vector, Matrix

MATS = {}


def clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for d in list(coll):
            coll.remove(d)
    MATS.clear()


def mat(name, color, rough=0.6, metal=0.0, emit=None, es=0.0, alpha=1.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = es
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
    MATS[name] = m
    return m


def add(name, bm, materials, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if not isinstance(materials, (list, tuple)):
        materials = [materials]
    for m in materials:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    bpy.context.scene.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.rotation_euler = rot
    bpy.context.scene.collection.objects.link(e)
    if parent:
        e.parent = parent
    return e


def bm_box(sx, sy, sz):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    return bm


def bm_sphere(r, us=24, vs=16, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=us, v_segments=vs, radius=r)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return bm


def bm_cyl(r1, r2, h, seg=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=h)
    return bm


def bm_cap(r, keep_above, us=20, vs=12, scale=(1, 1, 1), flip=False):
    """Part of a sphere. keep_above=True keeps z>=0 (dome); False keeps z<=0 (cup)."""
    bm = bm_sphere(r, us, vs, scale)
    kill = [v for v in bm.verts if (v.co.z < -1e-5 if keep_above else v.co.z > 1e-5)]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    return bm


def bm_torus(R, r, us=32, vs=10):
    bm = bmesh.new()
    verts = []
    for i in range(us):
        a = 2 * math.pi * i / us
        ring = []
        for j in range(vs):
            b = 2 * math.pi * j / vs
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            ring.append(bm.verts.new((x, y, r * math.sin(b))))
        verts.append(ring)
    for i in range(us):
        for j in range(vs):
            a, b = verts[i][j], verts[i][(j + 1) % vs]
            c, d = verts[(i + 1) % us][(j + 1) % vs], verts[(i + 1) % us][j]
            bm.faces.new((a, d, c, b))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_lathe(profile, seg=40, split=None):
    """profile: list of (r, z), outer surface bottom -> up, then inner. split = profile index
    where material index switches from 0 to 1."""
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        ring = []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for i in range(len(profile) - 1):
        for j in range(seg):
            a, b = rings[i][j], rings[i][(j + 1) % seg]
            c, d = rings[i + 1][(j + 1) % seg], rings[i + 1][j]
            try:
                f = bm.faces.new((a, b, c, d))
            except ValueError:
                continue
            if split is not None and i >= split:
                f.material_index = 1
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    return bm


def bm_xform(bm, m):
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return bm


def merge(dst, src):
    """append src bmesh geometry into dst"""
    mp = {}
    for v in src.verts:
        mp[v] = dst.verts.new(v.co)
    for f in src.faces:
        nf = dst.faces.new([mp[v] for v in f.verts])
        nf.material_index = f.material_index
    src.free()


def catmull(pts, per=10):
    P = [Vector(p) for p in pts]
    P2 = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P2) - 2):
        p0, p1, p2, p3 = P2[i - 1], P2[i], P2[i + 1], P2[i + 2]
        for k in range(per):
            t = k / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return out


def frames_for(path, radii, n0):
    n = Vector(n0)
    fr = []
    prev_t = None
    N = len(path)
    for i, p in enumerate(path):
        t = (path[min(i + 1, N - 1)] - path[max(i - 1, 0)]).normalized()
        if prev_t is not None:
            ax = prev_t.cross(t)
            if ax.length > 1e-7:
                n = Matrix.Rotation(prev_t.angle(t), 3, ax.normalized()) @ n
        n = (n - t * n.dot(t)).normalized()
        b = t.cross(n)
        fr.append((p, t, n, b, radii[i]))
        prev_t = t
    return fr


def tube_bm(fr, sides=12, cap_start=True, cap_end=True):
    bm = bmesh.new()
    rings = []
    for (p, t, n, b, r) in fr:
        ring = []
        for j in range(sides):
            a = 2 * math.pi * j / sides
            ring.append(bm.verts.new(p + (math.cos(a) * n + math.sin(a) * b) * r))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for j in range(sides):
            a, b = rings[i][j], rings[i][(j + 1) % sides]
            c, d = rings[i + 1][(j + 1) % sides], rings[i + 1][j]
            bm.faces.new((a, b, c, d))
    if cap_start:
        bm.faces.new(list(reversed(rings[0])))
    if cap_end:
        bm.faces.new(rings[-1])
    return bm


def simple_tube(pts, r, sides=8, per=8, n0=(0, 0, 1), rfun=None):
    path = catmull(pts, per)
    radii = [r if rfun is None else rfun(i / (len(path) - 1)) for i in range(len(path))]
    return tube_bm(frames_for(path, radii, n0), sides)


def helix(prev, A, D, R, turns, length, per_turn=8):
    A = Vector(A)
    D = Vector(D).normalized()
    prev = Vector(prev)
    w = prev - A
    w = w - D * w.dot(D)
    u = w.normalized()
    v = D.cross(u)
    pts = []
    n = int(turns * per_turn)
    for k in range(n + 1):
        th = 2 * math.pi * turns * k / n
        s = length * k / n
        pts.append(A + D * s + R * (math.cos(th) * u + math.sin(th) * v))
    return pts


def spiral(center, r0, r1, turns, z, start_angle=0.0, per_turn=10, ccw=True):
    c = Vector(center)
    pts = []
    n = int(turns * per_turn)
    for k in range(n + 1):
        f = k / n
        a = start_angle + (1 if ccw else -1) * 2 * math.pi * turns * f
        r = r0 + (r1 - r0) * f
        pts.append(Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), z)))
    return pts
