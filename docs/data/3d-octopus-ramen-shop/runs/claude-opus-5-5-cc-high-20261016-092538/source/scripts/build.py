import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion

random.seed(7)

# ---------------------------------------------------------------- reset
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
    for d in list(coll):
        coll.remove(d)

scene = bpy.context.scene
COL = scene.collection

# ---------------------------------------------------------------- materials
MATS = {}
def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, ss=0.0, alpha=1.0, spec=0.5):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    if ss > 0:
        b.inputs["Subsurface Weight"].default_value = ss
        b.inputs["Subsurface Radius"].default_value = (0.3, 0.08, 0.05)
        b.inputs["Subsurface Scale"].default_value = 0.05
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = 'BLENDED'
    m.diffuse_color = (*color, alpha)
    MATS[name] = m
    return m

M = dict(
    octo=mat("Octopus Skin", (0.85, 0.12, 0.06), rough=0.38, ss=0.25),
    octo_dark=mat("Octopus Spots", (0.5, 0.04, 0.03), rough=0.4),
    sucker=mat("Octopus Suckers", (1.0, 0.6, 0.45), rough=0.45, ss=0.2),
    blush=mat("Blush", (1.0, 0.42, 0.45), rough=0.6),
    eye_white=mat("Eye White", (0.95, 0.95, 0.92), rough=0.15),
    pupil=mat("Pupil", (0.02, 0.02, 0.03), rough=0.1),
    mouth=mat("Mouth", (0.25, 0.03, 0.04), rough=0.5),
    hat=mat("Chef Hat", (0.82, 0.82, 0.8), rough=0.75),
    scarf=mat("Neckerchief", (0.9, 0.55, 0.08), rough=0.7),
    wood=mat("Wood Light", (0.36, 0.17, 0.07), rough=0.6),
    wood_dark=mat("Wood Dark", (0.12, 0.05, 0.02), rough=0.65),
    wood_top=mat("Wood Counter", (0.55, 0.32, 0.15), rough=0.45),
    roof=mat("Roof", (0.16, 0.12, 0.10), rough=0.7),
    noren=mat("Noren Cloth", (0.02, 0.05, 0.16), rough=0.9),
    white=mat("White Print", (0.95, 0.93, 0.88), rough=0.8),
    lantern=mat("Lantern Paper", (0.5, 0.04, 0.02), rough=0.7, emit=(1.0, 0.16, 0.03), estr=2.2),
    black=mat("Black Lacquer", (0.03, 0.03, 0.03), rough=0.35),
    bowl=mat("Bowl Ceramic", (0.6, 0.06, 0.05), rough=0.25),
    bowl_in=mat("Bowl Inside", (0.92, 0.9, 0.84), rough=0.2),
    broth=mat("Broth", (0.62, 0.32, 0.1), rough=0.08),
    noodle=mat("Noodles", (0.98, 0.84, 0.48), rough=0.4),
    egg_white=mat("Egg White", (0.97, 0.95, 0.9), rough=0.3),
    yolk=mat("Egg Yolk", (1.0, 0.55, 0.05), rough=0.3),
    chashu=mat("Chashu", (0.62, 0.36, 0.25), rough=0.5),
    chashu_fat=mat("Chashu Fat", (0.95, 0.85, 0.75), rough=0.5),
    naruto=mat("Naruto", (0.98, 0.96, 0.95), rough=0.4),
    naruto_pink=mat("Naruto Pink", (0.95, 0.3, 0.5), rough=0.4),
    nori=mat("Nori", (0.04, 0.08, 0.05), rough=0.5),
    scallion=mat("Scallion", (0.3, 0.7, 0.15), rough=0.5),
    steel=mat("Steel", (0.7, 0.7, 0.72), rough=0.3, metal=0.7),
    chop=mat("Chopsticks", (0.85, 0.7, 0.45), rough=0.5),
    steam=mat("Steam", (1, 1, 1), rough=0.9, alpha=0.12),
    ground=mat("Ground", (0.05, 0.05, 0.06), rough=0.85),
    soy=mat("Soy Bottle", (0.12, 0.05, 0.02), rough=0.1),
    chili=mat("Chili", (0.75, 0.1, 0.02), rough=0.4),
    cushion=mat("Stool Cushion", (0.45, 0.04, 0.03), rough=0.7),
    rope=mat("Rope", (0.8, 0.7, 0.5), rough=0.9),
    sign=mat("Sign Board", (0.8, 0.62, 0.38), rough=0.6),
    sign_text=mat("Sign Text", (0.6, 0.05, 0.04), rough=0.5),
    bulb=mat("Bulb", (1.0, 0.85, 0.6), rough=0.3, emit=(1.0, 0.8, 0.5), estr=8.0),
)

def link(obj, parent=None):
    COL.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj

def mesh_obj(name, bm, mats, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link(ob)
    return ob

# ---------------------------------------------------------------- primitives
def box(name, x0, x1, y0, y1, z0, z1, m, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    ob = mesh_obj(name, bm, [m], smooth=False)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.harden_normals = False
    return ob

def lathe(name, prof, m, loc=(0, 0, 0), segs=48, rfunc=None, mats=None, mat_idx=None, scale=(1, 1, 1)):
    """prof: list of (r, z). r == 0 makes a pole."""
    bm = bmesh.new()
    rings = []
    for i, (r, z) in enumerate(prof):
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            ring = []
            for s in range(segs):
                a = 2 * math.pi * s / segs
                rr = r * (rfunc(a, z, i) if rfunc else 1.0)
                ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
            rings.append(ring)
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            for s in range(segs):
                bm.faces.new((A[0], B[s], B[(s + 1) % segs]))
        elif len(B) == 1:
            for s in range(segs):
                bm.faces.new((A[s], B[0], A[(s + 1) % segs]))
        else:
            for s in range(segs):
                f = bm.faces.new((A[s], A[(s + 1) % segs], B[(s + 1) % segs], B[s]))
                if mat_idx:
                    f.material_index = mat_idx(i)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    ob = mesh_obj(name, bm, mats or [m])
    ob.location = loc
    return ob

def cyl(name, r, z0, z1, m, loc=(0, 0, 0), segs=32):
    return lathe(name, [(0, z0), (r, z0), (r, z1), (0, z1)], m, loc=loc, segs=segs)

def sphere(name, r, m, loc=(0, 0, 0), scale=(1, 1, 1), segs=24, rings=16):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    ob = mesh_obj(name, bm, [m])
    ob.location = loc
    ob.scale = scale
    return ob

def catmull(pts, n=10):
    P = [Vector(p) for p in pts]
    out, ts = [], []
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i > 0 else P[i] * 2 - P[i + 1]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else P[i + 1] * 2 - P[i]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append(v)
            ts.append(i + t)
    out.append(P[-1])
    ts.append(len(P) - 1)
    return out, ts

def interp(vals, t):
    i = min(int(t), len(vals) - 2)
    f = t - i
    return vals[i] * (1 - f) + vals[i + 1] * f

def tube(name, pts, radii, m, sides=16, n=10, suckers=None, sucker_mat=None, cap_start=True, flat=1.0):
    """Tube along a Catmull-Rom spline. suckers: world-space direction hint for sucker side."""
    samples, ts = catmull(pts, n)
    N = len(samples)
    tangents = []
    for i in range(N):
        a = samples[max(i - 1, 0)]
        b = samples[min(i + 1, N - 1)]
        tangents.append((b - a).normalized())
    # parallel transport frames
    t0 = tangents[0]
    ref = Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    nrm = t0.cross(ref).normalized()
    frames = []
    for i in range(N):
        if i > 0:
            q = tangents[i - 1].rotation_difference(tangents[i])
            nrm = (q @ nrm)
            nrm = (nrm - tangents[i] * nrm.dot(tangents[i])).normalized()
        frames.append((nrm.copy(), tangents[i].cross(nrm).normalized()))
    bm = bmesh.new()
    rings = []
    for i in range(N):
        r = interp(radii, ts[i])
        nv, bv = frames[i]
        ring = []
        for s in range(sides):
            a = 2 * math.pi * s / sides
            ring.append(bm.verts.new(samples[i] + (nv * math.cos(a) + bv * math.sin(a) * flat) * r))
        rings.append(ring)
    for i in range(N - 1):
        for s in range(sides):
            bm.faces.new((rings[i][s], rings[i][(s + 1) % sides], rings[i + 1][(s + 1) % sides], rings[i + 1][s]))
    # tip cap
    tip = bm.verts.new(samples[-1] + tangents[-1] * interp(radii, ts[-1]) * 0.9)
    for s in range(sides):
        bm.faces.new((rings[-1][s], rings[-1][(s + 1) % sides], tip))
    if cap_start:
        st = bm.verts.new(samples[0] - tangents[0] * radii[0] * 0.5)
        for s in range(sides):
            bm.faces.new((rings[0][(s + 1) % sides], rings[0][s], st))
    mats = [m]
    if suckers is not None:
        mats.append(sucker_mat)
        hint = Vector(suckers)
        total = len(samples)
        i = int(total * 0.18)
        while i < total - 3:
            p, t = samples[i], tangents[i]
            r = interp(radii, ts[i])
            d = (hint - t * hint.dot(t))
            if d.length < 1e-4:
                i += 3
                continue
            d.normalize()
            sr = r * 0.42
            if sr < 0.006:
                break
            u = t
            w = d.cross(u).normalized()
            base = p + d * r * 0.72
            rim = p + d * (r * 0.72 + sr * 0.7)
            cup = p + d * (r * 0.72 + sr * 0.4)
            k = 10
            ring_b, ring_t, ring_i = [], [], []
            for s in range(k):
                a = 2 * math.pi * s / k
                off = (u * math.cos(a) + w * math.sin(a))
                ring_b.append(bm.verts.new(base + off * sr))
                ring_t.append(bm.verts.new(rim + off * sr * 0.95))
                ring_i.append(bm.verts.new(rim + off * sr * 0.55))
            c = bm.verts.new(cup)
            for s in range(k):
                s1 = (s + 1) % k
                for f in (bm.faces.new((ring_b[s], ring_b[s1], ring_t[s1], ring_t[s])),
                          bm.faces.new((ring_t[s], ring_t[s1], ring_i[s1], ring_i[s])),
                          bm.faces.new((ring_i[s], ring_i[s1], c))):
                    f.material_index = 1
            step = max(2, int(sr * 2.6 / max((samples[min(i + 1, total - 1)] - p).length, 1e-4)))
            i += step
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mats)

def coil(center, axis, radius, z0, z1, a0, turns, n=10):
    """Points spiralling around an axis (for tentacle tips gripping things)."""
    axis = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u)
    pts = []
    for k in range(n + 1):
        f = k / n
        a = a0 + 2 * math.pi * turns * f
        h = z0 + (z1 - z0) * f
        pts.append(Vector(center) + axis * h + (u * math.cos(a) + v * math.sin(a)) * radius)
    return pts

# ================================================================= BOOTH
ZC = 1.11  # counter surface height

ground = lathe("Ground", [(0, 0), (40, 0)], M["ground"], segs=64)

# cabinet body
box("Cart Cabinet", -1.5, 1.5, -0.45, 0.3, 0.18, 1.05, M["wood"], bevel=0.01)
for i, x in enumerate([-1.5 + k * 0.25 for k in range(13)]):
    box(f"Cabinet Slat {i}", x - 0.012, x + 0.012, -0.465, -0.44, 0.2, 1.03, M["wood_dark"])
box("Cabinet Trim Top", -1.52, 1.52, -0.48, 0.32, 0.95, 1.05, M["wood_dark"], bevel=0.005)
box("Cabinet Trim Bottom", -1.52, 1.52, -0.48, 0.32, 0.18, 0.26, M["wood_dark"], bevel=0.005)
box("Counter Top", -1.62, 1.62, -0.68, 0.36, 1.05, ZC, M["wood_top"], bevel=0.012)
box("Counter Front Lip", -1.62, 1.62, -0.7, -0.66, 1.0, ZC + 0.015, M["wood_dark"], bevel=0.005)

# cart wheels
for side in (-1, 1):
    x = side * 1.6
    wheel = lathe(f"Wheel Rim {side}", [(0.36, -0.04), (0.44, -0.04), (0.44, 0.04), (0.36, 0.04), (0.36, -0.04)],
                  M["wood_dark"], segs=40)
    wheel.rotation_euler = (0, math.pi / 2, 0)
    wheel.location = (x, -0.05, 0.44)
    hub = cyl(f"Wheel Hub {side}", 0.07, -0.07, 0.07, M["black"], segs=20)
    hub.rotation_euler = (0, math.pi / 2, 0)
    hub.location = (x, -0.05, 0.44)
    for k in range(8):
        a = k * math.pi / 4
        p1 = Vector((x, -0.05, 0.44))
        p2 = p1 + Vector((0, math.cos(a), math.sin(a))) * 0.38
        tube(f"Wheel Spoke {side}{k}", [p1, p2], [0.02, 0.018], M["wood"], sides=8, n=1)
    box(f"Axle Block {side}", side * 1.5 - 0.06, side * 1.5 + 0.06, -0.12, 0.02, 0.36, 0.52, M["wood_dark"])

# posts
for i, (x, y, z0) in enumerate([(-1.52, -0.6, ZC), (1.52, -0.6, ZC), (-1.52, 1.5, 0), (1.52, 1.5, 0)]):
    box(f"Post {i}", x - 0.05, x + 0.05, y - 0.05, y + 0.05, z0, 3.32, M["wood"], bevel=0.008)
box("Front Beam", -1.62, 1.62, -0.66, -0.54, 3.2, 3.32, M["wood_dark"], bevel=0.006)
box("Back Beam", -1.62, 1.62, 1.44, 1.56, 3.2, 3.32, M["wood_dark"], bevel=0.006)
for s in (-1, 1):
    box(f"Side Beam {s}", s * 1.52 - 0.05, s * 1.52 + 0.05, -0.66, 1.56, 3.22, 3.32, M["wood_dark"])

# gable roof: ridge along X
def roof_slab(name, y_eave, z_eave, y_ridge, z_ridge):
    bm = bmesh.new()
    th = 0.06
    xs = (-1.9, 1.9)
    vs = []
    for (y, z) in ((y_eave, z_eave), (y_ridge, z_ridge)):
        for x in xs:
            vs.append(Vector((x, y, z)))
    d = Vector((0, y_ridge - y_eave, z_ridge - z_eave)).normalized()
    up = Vector((1, 0, 0)).cross(d)
    if up.z < 0:
        up = -up
    bot = [bm.verts.new(v) for v in vs]
    top = [bm.verts.new(v + up * th) for v in vs]
    order = [0, 1, 3, 2]
    bm.faces.new([bot[i] for i in order])
    bm.faces.new([top[i] for i in reversed(order)])
    for a in range(4):
        i, j = order[a], order[(a + 1) % 4]
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, [M["roof"]], smooth=False)

roof_slab("Roof Front", -0.95, 3.28, 0.45, 3.75)
roof_slab("Roof Back", 1.85, 3.28, 0.45, 3.75)
tube("Roof Ridge", [(-1.95, 0.45, 3.8), (1.95, 0.45, 3.8)], [0.05, 0.05], M["wood_dark"], sides=12, n=1)
# roof battens for texture
for k in range(10):
    f = (k + 0.5) / 10
    for (ye, yr) in ((-0.95, 0.45), (1.85, 0.45)):
        y = ye + (yr - ye) * f
        z = 3.28 + (3.75 - 3.28) * f + 0.075
        tube(f"Roof Batten {ye}_{k}", [(-1.9, y, z), (1.9, y, z)], [0.015, 0.015], M["wood_dark"], sides=6, n=1, cap_start=True)
# gable triangles
for s in (-1, 1):
    bm = bmesh.new()
    vs = [bm.verts.new((s * 1.52, y, z)) for (y, z) in ((-0.6, 3.3), (1.5, 3.3), (0.45, 3.72))]
    bm.faces.new(vs)
    mesh_obj(f"Gable {s}", bm, [M["wood"]], smooth=False)

# sign on ridge
sign_y = 0.45
box("Sign Board", -1.0, 1.0, sign_y - 0.04, sign_y + 0.04, 3.85, 4.25, M["sign"], bevel=0.015)
box("Sign Frame", -1.05, 1.05, sign_y - 0.03, sign_y + 0.03, 3.82, 4.28, M["wood_dark"], bevel=0.01)
for x in (-0.7, 0.7):
    box(f"Sign Leg {x}", x - 0.03, x + 0.03, sign_y - 0.03, sign_y + 0.03, 3.7, 3.86, M["wood_dark"])

def text_mesh(name, body, size, loc, rot, m, extrude=0.01, align='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = 'CENTER'
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active

text_mesh("Sign Text Front", "TAKO RAMEN", 0.26, (0, sign_y - 0.05, 4.05), (math.pi / 2, 0, 0), M["sign_text"], extrude=0.01)
text_mesh("Sign Text Back", "TAKO RAMEN", 0.26, (0, sign_y + 0.05, 4.05), (math.pi / 2, 0, math.pi), M["sign_text"], extrude=0.01)

# noren curtains with letters
letters = "RAMEN"
pw, gap = 0.56, 0.04
x_start = -(5 * pw + 4 * gap) / 2
for i, ch in enumerate(letters):
    x0 = x_start + i * (pw + gap)
    bm = bmesh.new()
    nx, nz = 8, 6
    grid = []
    for iz in range(nz + 1):
        row = []
        for ix in range(nx + 1):
            fx, fz = ix / nx, iz / nz
            x = x0 + fx * pw
            z = 3.22 - fz * 0.42
            y = -0.66 - 0.012 * math.sin(fx * math.pi * 2 + i) * fz - 0.02 * fz
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for iz in range(nz):
        for ix in range(nx):
            bm.faces.new((grid[iz][ix], grid[iz][ix + 1], grid[iz + 1][ix + 1], grid[iz + 1][ix]))
    ob = mesh_obj(f"Noren {ch}", bm, [M["noren"]])
    sol = ob.modifiers.new("Thickness", 'SOLIDIFY')
    sol.thickness = 0.008
    cx = x0 + pw / 2
    text_mesh(f"Noren Letter {ch}", ch, 0.28, (cx, -0.7, 3.0), (math.pi / 2, 0, 0), M["white"], extrude=0.004)
    circ = lathe(f"Noren Circle {ch}", [(0.15, 0), (0.17, 0), (0.17, 0.004), (0.15, 0.004), (0.15, 0)], M["white"], segs=40)
    circ.rotation_euler = (math.pi / 2, 0, 0)
    circ.location = (cx, -0.695, 3.0)
tube("Noren Rod", [(-1.62, -0.66, 3.23), (1.62, -0.66, 3.23)], [0.018, 0.018], M["wood_dark"], sides=10, n=1)

# lanterns
LANTERN_POS = [(-1.78, -0.85), (1.78, -0.85)]
for i, (x, y) in enumerate(LANTERN_POS):
    zc = 2.68
    prof = []
    for k in range(17):
        t = k / 16
        z = -0.22 + 0.44 * t
        r = 0.17 * math.sin(math.pi * (0.12 + 0.76 * t)) + 0.02
        prof.append((r, z))
    lan = lathe(f"Lantern {i}", prof, M["lantern"], segs=32,
                rfunc=lambda a, z, idx: 1.0 + (0.025 if idx % 2 else -0.01))
    lan.location = (x, y, zc)
    cyl(f"Lantern Cap Top {i}", 0.08, 0.19, 0.25, M["black"], loc=(x, y, zc), segs=20)
    cyl(f"Lantern Cap Bottom {i}", 0.08, -0.25, -0.19, M["black"], loc=(x, y, zc), segs=20)
    tube(f"Lantern Cord {i}", [(x, y, zc + 0.25), (x, y, 3.28)], [0.006, 0.006], M["black"], sides=6, n=1)
    tube(f"Lantern Tassel {i}", [(x, y, zc - 0.25), (x, y, zc - 0.4)], [0.012, 0.004], M["chili"], sides=8, n=1)
    L = bpy.data.lights.new(f"Lantern Light {i}", 'POINT')
    L.energy = 60
    L.color = (1.0, 0.45, 0.2)
    L.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(f"Lantern Light {i}", L)
    lo.location = (x, y, zc)
    link(lo)

# hanging bulb under roof
tube("Bulb Cord", [(0, -0.2, 3.6), (0, -0.2, 3.05)], [0.006, 0.006], M["black"], sides=6, n=1)
sphere("Bulb", 0.05, M["bulb"], loc=(0, -0.2, 3.0))

# stools
for i, x in enumerate((-0.95, 0.0, 0.95)):
    y = -1.15
    lathe(f"Stool Seat {i}", [(0, 0.66), (0.2, 0.66), (0.22, 0.68), (0.22, 0.72), (0.2, 0.75), (0, 0.76)],
          M["cushion"], loc=(x, y, 0), segs=32)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3
        p0 = Vector((x + math.cos(a) * 0.13, y + math.sin(a) * 0.13, 0.66))
        p1 = Vector((x + math.cos(a) * 0.2, y + math.sin(a) * 0.2, 0.0))
        tube(f"Stool Leg {i}{k}", [p0, p1], [0.018, 0.02], M["wood_dark"], sides=8, n=1)
    lathe(f"Stool Ring {i}", [(0.155, 0.26), (0.175, 0.26), (0.175, 0.28), (0.155, 0.28), (0.155, 0.26)],
          M["wood_dark"], loc=(x, y, 0), segs=24)

# back shelf
box("Back Shelf", -1.45, 1.45, 1.22, 1.45, 0.0, 0.95, M["wood"], bevel=0.01)
box("Back Shelf Top", -1.5, 1.5, 1.18, 1.48, 0.95, 1.0, M["wood_top"], bevel=0.008)
box("Upper Shelf", -1.45, 1.45, 1.25, 1.45, 1.85, 1.89, M["wood_top"], bevel=0.005)

# ================================================================= RAMEN
def ramen_bowl(name, x, y, z, toppings=True, broth=True, noodles=True):
    prof = [(0, 0), (0.07, 0), (0.07, 0.015), (0.085, 0.02), (0.14, 0.06), (0.17, 0.12), (0.18, 0.13),
            (0.165, 0.13), (0.155, 0.115), (0.125, 0.06), (0.06, 0.03), (0, 0.028)]
    b = lathe(f"{name} Bowl", prof, M["bowl"], mats=[M["bowl"], M["bowl_in"]], segs=40,
              mat_idx=lambda i: 1 if i >= 7 else 0)
    b.location = (x, y, z)
    if broth:
        lathe(f"{name} Broth", [(0, 0.1), (0.15, 0.1)], M["broth"], loc=(x, y, z), segs=40)
    if noodles:
        for k in range(7):
            pts = []
            a0 = random.uniform(0, 2 * math.pi)
            for j in range(6):
                a = a0 + j * 0.7
                rr = random.uniform(0.02, 0.11)
                pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, z + 0.102 + 0.004 * (j % 2)))
            tube(f"{name} Noodle {k}", pts, [0.008, 0.008], M["noodle"], sides=6, n=5)
    if toppings:
        # egg half
        egg = sphere(f"{name} Egg", 0.04, M["egg_white"], loc=(x + 0.06, y - 0.05, z + 0.11), scale=(1, 1.3, 0.5))
        sphere(f"{name} Yolk", 0.022, M["yolk"], loc=(x + 0.06, y - 0.05, z + 0.122), scale=(1, 1.2, 0.35))
        # chashu
        ch = lathe(f"{name} Chashu", [(0, 0), (0.055, 0), (0.06, 0.006), (0.06, 0.012), (0.055, 0.016), (0, 0.016)],
                   M["chashu"], mats=[M["chashu"], M["chashu_fat"]], segs=24, mat_idx=lambda i: 1 if i == 2 else 0)
        ch.location = (x - 0.06, y + 0.04, z + 0.104)
        ch.rotation_euler = (0.25, -0.15, 0)
        # naruto
        nar = lathe(f"{name} Naruto", [(0, 0), (0.035, 0), (0.035, 0.008), (0, 0.008)], M["naruto"], segs=24,
                    rfunc=lambda a, z, i: 1 + 0.08 * math.sin(a * 10))
        nar.location = (x - 0.02, y - 0.07, z + 0.106)
        nar.rotation_euler = (0.2, 0.1, 0)
        sw = []
        for j in range(12):
            a = j * 0.9
            rr = 0.003 + j * 0.0023
            sw.append((math.cos(a) * rr, math.sin(a) * rr, 0.0095))
        sp = tube(f"{name} Naruto Swirl", sw, [0.003, 0.003], M["naruto_pink"], sides=5, n=3)
        sp.parent = nar
        # nori
        nori = box(f"{name} Nori", -0.05, 0.05, -0.003, 0.003, -0.02, 0.09, M["nori"])
        nori.location = (x + 0.0, y + 0.115, z + 0.11)
        nori.rotation_euler = (-0.35, 0, 0)
        # scallions
        for k in range(10):
            a = random.uniform(0, 2 * math.pi)
            rr = random.uniform(0.0, 0.09)
            s = cyl(f"{name} Scallion {k}", 0.007, -0.002, 0.002, M["scallion"], segs=8,
                    loc=(x + math.cos(a) * rr, y + math.sin(a) * rr, z + 0.118))
            s.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0)
    return b

bowl_a = ramen_bowl("Ramen A", -0.42, -0.32, ZC)   # presented by tentacle
bowl_b = ramen_bowl("Ramen B", 0.72, -0.2, ZC)     # noodles being lifted
bowl_c = ramen_bowl("Ramen C", 1.22, -0.35, ZC)

# chopsticks resting on bowl C
for k, dx in enumerate((-0.012, 0.012)):
    tube(f"Rest Chopstick {k}", [(1.05 + dx, -0.48, ZC + 0.135), (1.4 + dx, -0.28, ZC + 0.135)], [0.006, 0.004], M["chop"], sides=6, n=1)

# stock pot
PX, PY = -1.05, 0.0
lathe("Stock Pot", [(0, 0.0), (0.24, 0.0), (0.26, 0.02), (0.26, 0.42), (0.275, 0.43), (0.275, 0.445), (0.25, 0.445),
                    (0.245, 0.43), (0.245, 0.03), (0, 0.03)], M["steel"], loc=(PX, PY, ZC), segs=48)
lathe("Pot Broth", [(0, 0.37), (0.247, 0.37)], M["broth"], loc=(PX, PY, ZC), segs=48)
for s in (-1, 1):
    h = lathe(f"Pot Handle {s}", [(0.012, -0.04), (0.02, -0.04), (0.02, 0.04), (0.012, 0.04), (0.012, -0.04)],
              M["steel"], segs=16, scale=(3, 1.6, 1))
    h.location = (PX + s * 0.28, PY, ZC + 0.36)
    h.rotation_euler = (math.pi / 2, 0, 0)
# a few bubbles/noodle bits in the pot
for k in range(6):
    a = random.uniform(0, 6.28)
    rr = random.uniform(0.03, 0.18)
    sphere(f"Pot Bubble {k}", 0.015, M["broth"], loc=(PX + math.cos(a) * rr, PY + math.sin(a) * rr, ZC + 0.37), scale=(1, 1, 0.5), segs=10, rings=6)

# ladle
ladle_bowl_c = Vector((PX + 0.06, PY - 0.02, ZC + 0.39))
ladle_top = Vector((PX + 0.32, PY + 0.24, ZC + 0.78))
lb = lathe("Ladle Bowl", [(0, -0.045), (0.03, -0.04), (0.055, -0.02), (0.065, 0.01), (0.06, 0.012), (0.05, -0.012), (0.025, -0.03), (0, -0.034)],
           M["steel"], loc=ladle_bowl_c, segs=24)
tube("Ladle Handle", [ladle_bowl_c + Vector((0.05, 0.0, 0.01)), ladle_bowl_c + Vector((0.08, 0.04, 0.12)), ladle_top], [0.009, 0.009, 0.009], M["steel"], sides=8, n=6)

# steam wisps
def steam(name, base, height, count, spread):
    for k in range(count):
        pts = []
        a0 = random.uniform(0, 6.28)
        ox, oy = random.uniform(-spread, spread), random.uniform(-spread, spread)
        for j in range(7):
            f = j / 6
            pts.append((base[0] + ox + 0.05 * math.sin(a0 + f * 7) * (0.4 + f),
                        base[1] + oy + 0.05 * math.cos(a0 + f * 5) * (0.4 + f),
                        base[2] + f * height))
        tube(f"{name} {k}", pts, [0.012, 0.03, 0.045, 0.05, 0.045, 0.03, 0.006], M["steam"], sides=10, n=6)

steam("Pot Steam", (PX, PY, ZC + 0.42), 0.75, 4, 0.1)
steam("Bowl A Steam", (-0.48, -0.36, ZC + 0.14), 0.22, 2, 0.03)
steam("Bowl C Steam", (1.22, -0.35, ZC + 0.14), 0.4, 2, 0.04)

# condiments
lathe("Soy Bottle", [(0, 0), (0.04, 0), (0.042, 0.01), (0.042, 0.1), (0.03, 0.13), (0.015, 0.15), (0.015, 0.18), (0.02, 0.185), (0, 0.19)],
      M["soy"], loc=(1.45, -0.05, ZC), segs=24)
lathe("Soy Cap", [(0, 0.185), (0.021, 0.185), (0.021, 0.21), (0, 0.215)], M["chili"], loc=(1.45, -0.05, ZC), segs=16)
lathe("Chili Jar", [(0, 0), (0.045, 0), (0.048, 0.08), (0.04, 0.09), (0, 0.09)], M["chili"], loc=(1.47, 0.12, ZC), segs=24)
lathe("Chili Lid", [(0, 0.088), (0.042, 0.088), (0.042, 0.11), (0, 0.11)], M["black"], loc=(1.47, 0.12, ZC), segs=24)
lathe("Chopstick Cup", [(0, 0), (0.05, 0), (0.055, 0.14), (0.048, 0.14), (0.045, 0.01), (0, 0.01)], M["wood_dark"], loc=(1.3, 0.12, ZC), segs=24)
for k in range(9):
    a = k * 0.7
    tube(f"Cup Chopstick {k}", [(1.3 + math.cos(a) * 0.02, 0.12 + math.sin(a) * 0.02, ZC + 0.02),
                                (1.3 + math.cos(a) * 0.04, 0.12 + math.sin(a) * 0.04, ZC + 0.26)], [0.005, 0.004], M["chop"], sides=6, n=1)

# stacked bowls & jars on the back shelf
for j, x in enumerate((-1.1, -0.75, 0.75, 1.1)):
    for k in range(3):
        b = lathe(f"Stack Bowl {j}{k}", [(0, 0), (0.06, 0), (0.12, 0.05), (0.14, 0.09), (0.13, 0.09), (0.11, 0.055), (0.06, 0.012), (0, 0.012)],
                  M["bowl"], mats=[M["bowl"], M["bowl_in"]], segs=32, mat_idx=lambda i: 1 if i >= 4 else 0)
        b.location = (x, 1.33, 1.89 + k * 0.035)
for j, x in enumerate((-0.3, 0.0, 0.3)):
    lathe(f"Shelf Jar {j}", [(0, 0), (0.08, 0), (0.09, 0.05), (0.09, 0.2), (0.06, 0.24), (0.06, 0.26), (0, 0.26)],
          [M["wood_top"], M["bowl_in"], M["chili"]][j], loc=(x, 1.33, 1.89), segs=24)

# ================================================================= OCTOPUS CHEF
OX, OY, OZ = 0.0, 0.74, 1.13
BODY_SY = 0.92
body_prof = [(0, -0.04), (0.2, -0.02), (0.31, 0.06), (0.37, 0.18), (0.4, 0.32), (0.42, 0.48), (0.43, 0.64),
             (0.41, 0.78), (0.35, 0.9), (0.22, 0.99), (0, 1.02)]
def body_radius(zr):
    for i in range(len(body_prof) - 1):
        (r0, z0), (r1, z1) = body_prof[i], body_prof[i + 1]
        if z0 <= zr <= z1:
            f = (zr - z0) / (z1 - z0)
            return r0 + (r1 - r0) * f
    return 0.0
body = lathe("Octopus Body", body_prof, M["octo"], loc=(OX, OY, OZ), segs=48, scale=(1, BODY_SY, 1))
body.modifiers.new("Subsurf", 'SUBSURF').levels = 1

def on_body(theta, zr, push=0.0):
    """Point on the body surface; theta measured from -Y (front) toward +X."""
    r = body_radius(zr) + push
    return Vector((OX + math.sin(theta) * r, OY - math.cos(theta) * r * BODY_SY, OZ + zr))

# eyes
for s in (-1, 1):
    th = s * 0.42
    p = on_body(th, 0.4, -0.04)
    eye = sphere(f"Eye White {s}", 0.105, M["eye_white"], loc=p, scale=(1, 0.8, 1.1))
    look = Vector((-0.12, -1, -0.05)).normalized()
    pp = p + Vector((math.sin(th) * 0.03, -0.075, 0.0)) + Vector((-0.012, 0, -0.01))
    sphere(f"Pupil {s}", 0.058, M["pupil"], loc=pp, scale=(1, 0.6, 1.15))
    sphere(f"Eye Shine {s}", 0.018, M["eye_white"], loc=pp + Vector((0.02, -0.035, 0.03)))
    sphere(f"Eye Shine Small {s}", 0.008, M["eye_white"], loc=pp + Vector((-0.018, -0.035, -0.025)))
    # brows
    bp = [on_body(th - 0.12 * s, 0.56, 0.0), on_body(th, 0.585, 0.005), on_body(th + 0.14 * s, 0.57, 0.0)]
    tube(f"Brow {s}", bp, [0.014, 0.016, 0.012], M["octo_dark"], sides=8, n=4)
    # blush
    bl = sphere(f"Blush {s}", 0.06, M["blush"], loc=on_body(s * 0.78, 0.27, -0.015), scale=(1, 0.4, 0.6))
    bl.rotation_euler = (0, 0, -s * 0.78)

# smile
sm = [on_body(a, 0.24 - 0.04 * math.cos(a * 4.5), -0.005) for a in (-0.32, -0.16, 0.0, 0.16, 0.32)]
tube("Smile", sm, [0.012, 0.016, 0.018, 0.016, 0.012], M["mouth"], sides=8, n=4)

# spots on mantle
for k in range(14):
    th = random.uniform(-2.6, 2.6)
    zr = random.uniform(0.6, 0.86)
    if abs(th) < 0.6 and zr < 0.75:
        continue
    p = on_body(th, zr, -0.012)
    sr = random.uniform(0.025, 0.05)
    sp = sphere(f"Mantle Spot {k}", sr, M["octo_dark"], loc=p, scale=(1, 1, 1), segs=12, rings=8)
    n = (p - Vector((OX, OY, OZ + zr))).normalized()
    sp.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
    sp.scale = (1, 1, 0.3)

# chef hat (toque) on top, slightly tilted
HAT_Z = OZ + 0.86
hat_prof = [(0, 0.0), (0.26, 0.0), (0.27, 0.05), (0.27, 0.16), (0.3, 0.19), (0.36, 0.25), (0.39, 0.33), (0.38, 0.42),
            (0.33, 0.5), (0.2, 0.55), (0, 0.565)]
hat = lathe("Chef Hat", hat_prof, M["hat"], segs=48,
            rfunc=lambda a, z, i: 1.0 + (0.05 * math.sin(a * 9) if i >= 4 else 0.0))
hat.location = (OX + 0.02, OY + 0.02, HAT_Z)
hat.rotation_euler = (0.08, -0.12, 0)
hat.modifiers.new("Subsurf", 'SUBSURF').levels = 1
band = lathe("Chef Hat Band", [(0.274, 0.0), (0.274, 0.16)], M["hat"], segs=48)
band.location = hat.location
band.rotation_euler = hat.rotation_euler

# neckerchief
nk = lathe("Neckerchief", [(0.0, 0.0)] and [(0.3, -0.03), (0.345, 0.0), (0.37, 0.05), (0.36, 0.09), (0.32, 0.1)], M["scarf"], segs=48)
nk.location = (OX, OY, OZ + 0.05)
nk.scale = (1, BODY_SY, 1)
knot = sphere("Neckerchief Knot", 0.05, M["scarf"], loc=on_body(0, 0.1, 0.06))
for s in (-1, 1):
    bm = bmesh.new()
    k0 = on_body(0, 0.1, 0.07)
    vs = [bm.verts.new(k0), bm.verts.new(k0 + Vector((s * 0.13, -0.06, -0.14))), bm.verts.new(k0 + Vector((s * 0.02, -0.07, -0.17)))]
    bm.faces.new(vs)
    flap = mesh_obj(f"Neckerchief Flap {s}", bm, [M["scarf"]])
    flap.modifiers.new("Thick", 'SOLIDIFY').thickness = 0.015

# ---------------------------------------------------------------- tentacles
TR = [0.11, 0.085, 0.065, 0.05, 0.038, 0.028, 0.02, 0.014]
def radii_for(n_pts, r0=0.11, r1=0.012):
    return [r0 * (r1 / r0) ** (i / (n_pts - 1)) for i in range(n_pts)]

def root(theta, zr=0.1, push=-0.08):
    return on_body(theta, zr, push)

tentacles = []

# 1: ladle tentacle (left, reaching over the pot)
gr = coil(ladle_top - Vector((0.03, 0.03, 0.04)) * 0, Vector(ladle_top - ladle_bowl_c).normalized(), 0.028, -0.18, -0.06, 0.3, 1.3, n=8)
p = [root(-1.0, 0.12), on_body(-1.25, 0.05, 0.12), Vector((-0.55, 0.35, 1.42)), Vector((-0.65, 0.3, 1.72)),
     ladle_top + Vector((0.03, 0.06, 0.1))] + gr
tentacles.append(("Tentacle Ladle", p, radii_for(len(p), 0.12, 0.016), (0, -1, 0.3)))

# 2: chopstick tentacle (right, lifting noodles from bowl B)
cs_top = Vector((0.9, -0.02, 1.86))
cs_tip = Vector((0.73, -0.2, 1.5))
cs_axis = (cs_top - cs_tip).normalized()
gr = coil(cs_tip, cs_axis, 0.03, 0.22, 0.32, 3.5, 1.4, n=8)
p = [root(1.0, 0.12), on_body(1.25, 0.08, 0.12), Vector((0.55, 0.38, 1.5)), Vector((0.75, 0.28, 1.95)),
     Vector((0.9, 0.12, 2.0))] + gr
tentacles.append(("Tentacle Chopsticks", p, radii_for(len(p), 0.12, 0.016), (0, -1, 0)))
for k, d in enumerate((-0.016, 0.016)):
    off = Vector((d, 0.0, 0)) + Vector((0, d * 0.4, 0))
    tube(f"Chef Chopstick {k}", [cs_top + off, cs_tip + off * (0.25)], [0.007, 0.004], M["chop"], sides=8, n=1)
# noodles hanging from the chopsticks into bowl B
for k in range(7):
    top = cs_tip + Vector((random.uniform(-0.012, 0.012), random.uniform(-0.01, 0.01), 0.005))
    bot = Vector((0.72 + random.uniform(-0.06, 0.06), -0.2 + random.uniform(-0.06, 0.06), ZC + 0.105))
    pts = []
    for j in range(7):
        f = j / 6
        q = top.lerp(bot, f)
        q += Vector((0.018 * math.sin(f * 9 + k), 0.018 * math.cos(f * 7 + k * 2), 0)) * math.sin(f * math.pi)
        pts.append(q)
    tube(f"Lifted Noodle {k}", pts, [0.0075] * 7, M["noodle"], sides=6, n=5)

# 3: tentacle hugging bowl A and pushing it forward
bc = Vector((-0.42, -0.32, ZC + 0.075))
wrap = [bc + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.0)) for a in
        [math.radians(d) for d in (60, 100, 140, 180, 215, 250)]]
p = [root(-0.45, 0.1), on_body(-0.55, 0.0, 0.12), Vector((-0.28, 0.12, ZC + 0.1)), Vector((-0.3, -0.05, ZC + 0.08))] + wrap
tentacles.append(("Tentacle Bowl", p, radii_for(len(p), 0.11, 0.018), (0, 0, -1)))

# 4: waving tentacle (right back, up high)
p = [root(1.9, 0.15), on_body(2.0, 0.15, 0.15), Vector((0.75, 0.95, 1.6)), Vector((1.0, 0.85, 2.05)),
     Vector((1.05, 0.65, 2.4)), Vector((0.95, 0.55, 2.55)), Vector((0.88, 0.62, 2.48)), Vector((0.93, 0.68, 2.42))]
tentacles.append(("Tentacle Wave", p, radii_for(len(p), 0.11, 0.015), (0, -1, 0)))

# 5: tentacle lying across the counter, curled tip
p = [root(0.35, 0.08), on_body(0.4, -0.02, 0.12), Vector((0.2, 0.15, ZC + 0.07)), Vector((0.25, -0.15, ZC + 0.05)),
     Vector((0.3, -0.42, ZC + 0.045)), Vector((0.2, -0.52, ZC + 0.04)), Vector((0.1, -0.46, ZC + 0.035)),
     Vector((0.13, -0.38, ZC + 0.03)), Vector((0.19, -0.42, ZC + 0.028))]
tentacles.append(("Tentacle Counter", p, radii_for(len(p), 0.11, 0.016), (0.0, -0.3, 1.0)))

# 6: tentacle holding a small bowl of scallions over the counter on the left
p = [root(-1.9, 0.15), on_body(-2.0, 0.12, 0.15), Vector((-0.8, 0.9, 1.5)), Vector((-1.05, 0.75, 1.95)),
     Vector((-1.2, 0.5, 2.15)), Vector((-1.3, 0.35, 2.05)), Vector((-1.25, 0.3, 1.97)), Vector((-1.18, 0.36, 1.95))]
tentacles.append(("Tentacle Reach", p, radii_for(len(p), 0.11, 0.015), (0, -1, -0.5)))

# 7-8: tentacles supporting the chef, reaching the floor behind the counter
for k, (th, end) in enumerate(((2.6, Vector((0.55, 1.05, 0.04))), (-2.6, Vector((-0.55, 1.05, 0.04))))):
    s = 1 if th > 0 else -1
    p = [root(th, 0.1), on_body(th, -0.05, 0.1), Vector((s * 0.4, 0.95, 0.75)), Vector((s * 0.45, 0.95, 0.3)),
         end, end + Vector((s * 0.25, -0.15, 0.0)), end + Vector((s * 0.35, -0.35, 0.02)), end + Vector((s * 0.25, -0.42, 0.03))]
    tentacles.append((f"Tentacle Floor {k}", p, radii_for(len(p), 0.12, 0.02), (0, 0, -1)))
for k, th in enumerate((0.0,)):
    pass

for name, pts, rad, sdir in tentacles:
    ob = tube(name, pts, rad, M["octo"], sides=18, n=8, suckers=sdir, sucker_mat=M["sucker"])

# ================================================================= LIGHTS / CAMERA / WORLD
def area(name, loc, rot, energy, size, color):
    L = bpy.data.lights.new(name, 'AREA')
    L.energy = energy
    L.size = size
    L.color = color
    o = bpy.data.objects.new(name, L)
    o.location = loc
    o.rotation_euler = rot
    link(o)
    return o

def aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

key = area("Key Light", (-3.0, -3.5, 4.5), (0, 0, 0), 450, 3.0, (1.0, 0.85, 0.7)); aim(key, (0, 0.2, 1.4))
fill = area("Fill Light", (4.0, -2.5, 2.5), (0, 0, 0), 120, 3.0, (0.5, 0.6, 1.0)); aim(fill, (0, 0.3, 1.5))
rim = area("Rim Light", (1.5, 4.0, 4.0), (0, 0, 0), 500, 2.5, (0.5, 0.65, 1.0)); aim(rim, (0, 0.7, 1.8))
inner = area("Booth Light", (0, 0.2, 3.15), (0, 0, 0), 70, 1.5, (1.0, 0.8, 0.55))

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.03, 0.04, 0.09, 1)
bg.inputs["Strength"].default_value = 1.0

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 36
cam = bpy.data.objects.new("Camera", cam_data)
link(cam)
cam.location = (-3.2, -6.3, 2.45)
aim(cam, (0.05, 0.2, 2.0))
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Punchy'

# ================================================================= BACKDROP: night street
M["bldg"] = mat("Building", (0.07, 0.07, 0.09), rough=0.9)
M["bldg2"] = mat("Building Warm", (0.11, 0.08, 0.07), rough=0.9)
M["win"] = mat("Window Lit", (0.3, 0.15, 0.05), rough=0.4, emit=(1.0, 0.5, 0.18), estr=1.5)
M["win_dark"] = mat("Window Dark", (0.02, 0.03, 0.05), rough=0.2)
M["pole"] = mat("Pole", (0.1, 0.1, 0.1), rough=0.6)
M["fairy"] = mat("Fairy Bulb", (1.0, 0.8, 0.45), rough=0.3, emit=(1.0, 0.75, 0.4), estr=10.0)

x = -20.0
bi = 0
while x < 20.0:
    w = random.uniform(2.5, 4.0)
    h = random.uniform(6.0, 12.0)
    y0 = random.uniform(9.0, 11.0)
    box(f"Building {bi}", x, x + w - 0.15, y0, y0 + 4.0, 0, h, M["bldg"] if bi % 2 else M["bldg2"])
    bm = bmesh.new()
    bm_d = bmesh.new()
    fl = 1.3
    z = 1.2
    while z + 0.8 < h - 0.3:
        cx = x + 0.45
        while cx + 0.55 < x + w - 0.3:
            target = bm if random.random() < 0.3 else bm_d
            vs = [target.verts.new((cx, y0 - 0.02, z)), target.verts.new((cx + 0.45, y0 - 0.02, z)),
                  target.verts.new((cx + 0.45, y0 - 0.02, z + 0.6)), target.verts.new((cx, y0 - 0.02, z + 0.6))]
            target.faces.new(vs)
            cx += 0.9
        z += fl
    mesh_obj(f"Building {bi} Lit Windows", bm, [M["win"]], smooth=False)
    mesh_obj(f"Building {bi} Dark Windows", bm_d, [M["win_dark"]], smooth=False)
    x += w
    bi += 1

# poles & string lights
def catenary(a, b, sag, n):
    a, b = Vector(a), Vector(b)
    return [a.lerp(b, k / n) - Vector((0, 0, sag * 4 * (k / n) * (1 - k / n))) for k in range(n + 1)]

for s, (px, py) in ((-1, (-4.2, 2.8)), (1, (4.4, 3.2))):
    cyl(f"Street Pole {s}", 0.07, 0, 4.4, M["pole"], loc=(px, py, 0), segs=12)
    a = (s * 1.88, -0.95, 3.3)
    b = (px, py, 4.2)
    pts = catenary(a, b, 0.45, 16)
    tube(f"Light String {s}", pts, [0.006] * len(pts), M["black"], sides=6, n=2)
    for k in range(1, 16):
        sphere(f"Fairy Bulb {s}{k}", 0.035, M["fairy"], loc=pts[k] - Vector((0, 0, 0.05)), segs=10, rings=6)

# ================================================================= compositor glow (renders only)
ng = bpy.data.node_groups.get("Glow Comp")
if ng:
    bpy.data.node_groups.remove(ng)
ng = bpy.data.node_groups.new("Glow Comp", "CompositorNodeTree")
ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
rl = ng.nodes.new("CompositorNodeRLayers")
gl = ng.nodes.new("CompositorNodeGlare")
gl.inputs["Type"].default_value = 'Bloom'
gl.inputs["Threshold"].default_value = 0.9
gl.inputs["Strength"].default_value = 0.6
gl.inputs["Size"].default_value = 0.6
out = ng.nodes.new("NodeGroupOutput")
ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
ng.links.new(gl.outputs["Image"], out.inputs[0])
scene.compositing_node_group = ng
scene.eevee.taa_render_samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
