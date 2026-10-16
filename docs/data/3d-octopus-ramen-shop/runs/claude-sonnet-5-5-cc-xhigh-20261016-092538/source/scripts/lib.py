"""Geometry / material helpers for the octopus ramen booth (bmesh based)."""
import bpy, bmesh, math, random, bisect
from math import pi, sin, cos, radians, sqrt
from mathutils import Vector, Matrix, Euler, Quaternion, noise

MATS = {}


# --------------------------------------------------------------------------- scene
def reset():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras,
                 bpy.data.lights, bpy.data.images, bpy.data.node_groups):
        for d in list(coll):
            coll.remove(d)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    MATS.clear()


def group(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    if parent:
        e.parent = parent
    return e


# --------------------------------------------------------------------------- materials
def srgb2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (srgb2lin(r), srgb2lin(g), srgb2lin(b), a)


def mat(name, color='#ffffff', rough=0.5, metal=0.0, emit=None, emit_strength=1.0,
        alpha=1.0, vcol=None, coat=0.0, spec=0.5, sss=0.0, sss_color=None):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    c = hexc(color) if isinstance(color, str) else color
    b.inputs['Base Color'].default_value = c
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    if coat > 0:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.1
    if sss > 0:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.2)
    if emit:
        b.inputs['Emission Color'].default_value = hexc(emit) if isinstance(emit, str) else emit
        b.inputs['Emission Strength'].default_value = emit_strength
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
    if vcol:
        n = nt.nodes.new('ShaderNodeVertexColor')
        n.layer_name = vcol
        nt.links.new(n.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Base Color'].default_value = (1, 1, 1, 1)
    m.diffuse_color = c
    MATS[name] = m
    return m


# --------------------------------------------------------------------------- bmesh helpers
def _scale_verts(bm, sx, sy, sz):
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz


def sphere(rx, ry=None, rz=None, u=24, v=16):
    ry = rx if ry is None else ry
    rz = rx if rz is None else rz
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    _scale_verts(bm, rx, ry, rz)
    return bm


def box(sx, sy, sz, bevel=0.0, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    _scale_verts(bm, sx, sy, sz)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, offset_type='OFFSET',
                        segments=segs, profile=0.5, affect='EDGES')
    return bm


def cyl(r1, r2=None, h=1.0, segs=24, caps=True, base_at_zero=True):
    """Cone/cylinder along +Z; r1 at z=0 (bottom), r2 at z=h."""
    r2 = r1 if r2 is None else r2
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs,
                          radius1=r1, radius2=r2, depth=h)
    if base_at_zero:
        for v in bm.verts:
            v.co.z += h / 2
    return bm


def lathe(profile, segs=32, closed=False, sx=1.0, sy=1.0, matidx=None):
    """profile: list of (r, z). Travelling along the profile, the surface normal is on its right-hand side
    in the (r, z) plane (up the outside => outward)."""
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        if abs(r) < 1e-9:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * cos(2 * pi * k / segs) * sx, r * sin(2 * pi * k / segs) * sy, z))
                          for k in range(segs)])
    n = len(rings)
    pairs = [(i, i + 1) for i in range(n - 1)]
    if closed:
        pairs.append((n - 1, 0))
    for (i, j) in pairs:
        a, b = rings[i], rings[j]
        mi = 0 if matidx is None else matidx[i]
        for k in range(segs):
            k2 = (k + 1) % segs
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                f = bm.faces.new((a[0], b[k2], b[k]))
            elif len(b) == 1:
                f = bm.faces.new((a[k], a[k2], b[0]))
            else:
                f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
            f.material_index = mi
    return bm


def torus(R, r, segs=32, sides=12, sx=1.0, sy=1.0):
    prof = [(R + r * cos(2 * pi * i / sides), r * sin(2 * pi * i / sides)) for i in range(sides)]
    return lathe(prof, segs=segs, closed=True, sx=sx, sy=sy)


def add_bm(dst, src, M=None, matidx=None):
    vm = {}
    for v in src.verts:
        vm[v] = dst.verts.new(M @ v.co if M is not None else v.co.copy())
    for f in src.faces:
        try:
            nf = dst.faces.new([vm[v] for v in f.verts])
        except ValueError:
            continue
        nf.material_index = f.material_index if matidx is None else matidx
        nf.smooth = f.smooth
    for e in src.edges:
        if not e.smooth:
            de = dst.edges.get((vm[e.verts[0]], vm[e.verts[1]]))
            if de:
                de.smooth = False
    src.free()
    return dst


def xform(bm, M):
    bmesh.ops.transform(bm, matrix=M, verts=list(bm.verts))
    return bm


def trs(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return (Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4() @
            Matrix.Diagonal(Vector((*scale, 1))))


def rot_to(vec, up_hint=(0, 0, 1)):
    """Euler that rotates +Z onto vec."""
    v = Vector(vec).normalized()
    q = Vector((0, 0, 1)).rotation_difference(v)
    return q.to_euler('XYZ')


def basis_matrix(origin, zaxis, xhint=(1, 0, 0)):
    """4x4 with Z along zaxis, X as close to xhint as possible."""
    z = Vector(zaxis).normalized()
    x = Vector(xhint) - z * Vector(xhint).dot(z)
    if x.length < 1e-6:
        x = Vector((0, 1, 0)) - z * z.y
    x.normalize()
    y = z.cross(x)
    M = Matrix((x, y, z)).transposed().to_4x4()
    M.translation = Vector(origin)
    return M


def make(name, bm, mats, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None,
         smooth=True, sharp=None):
    if not isinstance(mats, (list, tuple)):
        mats = [mats]
    for f in bm.faces:
        f.smooth = smooth
    if smooth and sharp is not None:
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > radians(sharp):
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    if parent:
        ob.parent = parent
    return ob


# --------------------------------------------------------------------------- curves / tubes
def cr_dense(ctrl, per=16):
    P = [Vector(p) for p in ctrl]
    ext = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for j in range(per):
            t = j / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1].copy())
    return out


def resample(pts, n):
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + (pts[i] - pts[i - 1]).length)
    total = L[-1]
    res = []
    j = 0
    for k in range(n):
        s = total * k / (n - 1)
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        seg = L[j + 1] - L[j]
        f = 0 if seg < 1e-12 else (s - L[j]) / seg
        res.append(pts[j].lerp(pts[j + 1], f))
    return res, total


def spline(ctrl, n, per=16):
    """Catmull-Rom through ctrl, resampled to n points evenly spaced by arc length."""
    return resample(cr_dense(ctrl, per), n)


def frames(pts, under=(0, 0, -1), twist=0.0, under_fn=None):
    n = len(pts)
    T = []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        T.append((b - a).normalized())
    u = Vector(under)
    N0 = u - T[0] * u.dot(T[0])
    if N0.length < 1e-5:
        N0 = Vector((1, 0, 0)) - T[0] * T[0].x
    N0.normalize()
    Ns = [N0]
    for i in range(1, n):
        Nn = Ns[-1] - T[i] * Ns[-1].dot(T[i])
        if Nn.length < 1e-6:
            Nn = Ns[-1]
        Ns.append(Nn.normalized())
    out = []
    for i in range(n):
        N = Ns[i]
        B = T[i].cross(N)
        if twist:
            a = twist(i / (n - 1)) if callable(twist) else twist * i / (n - 1)
            N, B = N * cos(a) + B * sin(a), B * cos(a) - N * sin(a)
        if under_fn is not None:
            w, vec = under_fn(i, pts[i])
            if w > 0:
                pr = Vector(vec) - T[i] * Vector(vec).dot(T[i])
                if pr.length > 1e-5:
                    N2 = N * (1 - w) + pr.normalized() * w
                    N2 = N2 - T[i] * N2.dot(T[i])
                    if N2.length > 1e-5:
                        N = N2.normalized()
                        B = T[i].cross(N)
        out.append((pts[i], T[i], N, B))
    return out


def tube(pts, radii, sides=12, under=(0, 0, -1), twist=0.0, cap_end=True, cap_start=True,
         color_fn=None, flat=1.0, under_fn=None, bump=None):
    """Sweep a circle along pts. Returns (bm, frames). color_fn(i, cosang, sinang) -> rgba (linear)."""
    fr = frames(pts, under, twist, under_fn)
    bm = bmesh.new()
    rings = []
    vcol = {}
    n = len(pts)
    for i, (p, T, N, B) in enumerate(fr):
        r = radii[i]
        ring = []
        for k in range(sides):
            a = 2 * pi * k / sides
            pos = p + N * (cos(a) * r) + B * (sin(a) * r * flat)
            if bump is not None:
                pos = pos + (N * cos(a) + B * sin(a)) * bump(pos, r)
            v = bm.verts.new(pos)
            ring.append(v)
            if color_fn:
                vcol[v] = color_fn(i, cos(a), sin(a), v.co)
        rings.append(ring)
    for i in range(n - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(sides):
            k2 = (k + 1) % sides
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if cap_end:
        p, T, N, B = fr[-1]
        r = radii[-1]
        prev = rings[-1]
        steps = 4
        for j in range(1, steps + 1):
            ang = j / steps * pi / 2
            off = r * sin(ang)
            rr = r * cos(ang)
            if j == steps:
                pole = bm.verts.new(p + T * off)
                if color_fn:
                    vcol[pole] = color_fn(n - 1, 0.0, 0.0, pole.co)
                for k in range(sides):
                    bm.faces.new((prev[k], prev[(k + 1) % sides], pole))
            else:
                ring = []
                for k in range(sides):
                    a = 2 * pi * k / sides
                    v = bm.verts.new(p + T * off + N * (cos(a) * rr) + B * (sin(a) * rr * flat))
                    ring.append(v)
                    if color_fn:
                        vcol[v] = color_fn(n - 1, cos(a), sin(a), v.co)
                for k in range(sides):
                    k2 = (k + 1) % sides
                    bm.faces.new((prev[k], prev[k2], ring[k2], ring[k]))
                prev = ring
    if cap_start:
        p, T, N, B = fr[0]
        pole = bm.verts.new(p - T * radii[0] * 0.6)
        if color_fn:
            vcol[pole] = color_fn(0, 0.0, 0.0, pole.co)
        for k in range(sides):
            bm.faces.new((pole, rings[0][(k + 1) % sides], rings[0][k]))
    if color_fn:
        layer = bm.loops.layers.float_color.new("Color")
        for f in bm.faces:
            for lp in f.loops:
                lp[layer] = vcol[lp.vert]
    return bm, fr


def wire(ctrl, radius, sides=6, n=None, per=12, **kw):
    """Constant radius tube through control points (chopsticks, noodles, handles...)."""
    dense = cr_dense(ctrl, per)
    if n is None:
        n = max(4, int(sum((dense[i + 1] - dense[i]).length for i in range(len(dense) - 1)) / (radius * 2.2)))
    pts, total = resample(dense, n)
    rad = [radius] * n if not callable(radius) else [radius(i / (n - 1)) for i in range(n)]
    return tube(pts, rad, sides=sides, **kw)[0]


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def mixc(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(4))


def paint(bm, fn, layer_name="Color"):
    """Per-vertex colour from fn(co, normal) -> linear rgba, into a float colour layer."""
    layer = bm.loops.layers.float_color.get(layer_name) or bm.loops.layers.float_color.new(layer_name)
    bm.normal_update()
    cache = {}
    for f in bm.faces:
        for lp in f.loops:
            v = lp.vert
            if v not in cache:
                cache[v] = fn(v.co, v.normal)
            lp[layer] = cache[v]
    return bm


def wrap_pts(origin, axis, radius, turns, length, phase=0.0, n_per_turn=8, ref=(0, 0, 1), r_end=None):
    """Helix points winding around an axis starting at origin, advancing `length` along axis."""
    a = Vector(axis).normalized()
    u = Vector(ref) - a * Vector(ref).dot(a)
    if u.length < 1e-4:
        u = Vector((1, 0, 0)) - a * a.x
    u.normalize()
    v = a.cross(u)
    n = max(3, int(turns * n_per_turn))
    out = []
    for i in range(n + 1):
        f = i / n
        th = phase + turns * 2 * pi * f
        r = radius if r_end is None else radius + (r_end - radius) * f
        out.append(Vector(origin) + a * (length * f) + (u * cos(th) + v * sin(th)) * r)
    return out


def text_bm(body, size=0.1, extrude=0.005, align_x='CENTER', align_y='CENTER', bevel=0.0, spacing=1.0):
    """Text outline as bmesh in the XY plane (extruded along Z)."""
    cu = bpy.data.curves.new("txt", 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align_x
    cu.align_y = align_y
    cu.bevel_depth = bevel
    cu.space_character = spacing
    ob = bpy.data.objects.new("txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    ev.to_mesh_clear()
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return bm


def hash01(*a):
    h = 0
    for x in a:
        h = (h * 1000003 + int(x) * 7919 + 12345) & 0xffffffff
        h ^= (h >> 13)
        h = (h * 0x5bd1e995) & 0xffffffff
    return (h & 0xffff) / 0xffff
