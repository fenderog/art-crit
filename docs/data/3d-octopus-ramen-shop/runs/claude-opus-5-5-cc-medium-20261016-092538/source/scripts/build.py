import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

random.seed(7)

# ---------- reset ----------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights,
             bpy.data.cameras, bpy.data.metaballs):
    for d in list(coll):
        coll.remove(d)
scene = bpy.context.scene
COL = scene.collection

# ---------- helpers ----------
MATS = {}


def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, alpha=1.0, sss=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.3, 0.1, 0.08)
        b.inputs["Subsurface Scale"].default_value = 0.05
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    MATS[name] = m
    return m


def finish(name, bm, m, loc=(0, 0, 0), rot=(0, 0, 0), smooth=True, smooth_cyl=False, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        if smooth_cyl:
            p.use_smooth = abs(p.normal.z) < 0.9
        else:
            p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    if isinstance(m, (list, tuple)):
        for mm in m:
            me.materials.append(mm)
    else:
        me.materials.append(m)
    if bevel:
        md = o.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = 2
        md.limit_method = 'ANGLE'
    return o


def box(name, loc, dims, m, rot=(0, 0, 0), bevel=0.008):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0]; v.co.y *= dims[1]; v.co.z *= dims[2]
    return finish(name, bm, m, loc, rot, smooth=False, bevel=bevel)


def sphere(name, loc, r, m, scale=(1, 1, 1), rot=(0, 0, 0), seg=32, rings=16):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for v in bm.verts:
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    return finish(name, bm, m, loc, rot)


def cyl(name, loc, r, depth, m, rot=(0, 0, 0), seg=32, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    return finish(name, bm, m, loc, rot, smooth_cyl=True)


def cyl_between(name, a, b, r, m, seg=12, r2=None):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(name, (a + b) / 2, r, d.length, m, seg=seg, r2=r2)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.normalized().to_track_quat('Z', 'Y')
    return o


def lathe(name, prof, m, loc=(0, 0, 0), seg=48, rot=(0, 0, 0)):
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            try:
                bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, m, loc, rot)


def crom(pts, n):
    pts = [Vector(p) for p in pts]
    P = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    segs = len(pts) - 1
    out = []
    for i in range(n):
        t = i / (n - 1) * segs
        k = min(int(t), segs - 1)
        u = t - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    return out


def tube(name, pts, rfun, m, seg=14, samples=80, under=(0, 0, -1), suckers=None, sucker_mat=None):
    path = crom(pts, samples)
    n = len(path)
    tans = []
    for i in range(n):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        tans.append((b - a).normalized())
    u = Vector(under)
    nrm = (u - u.dot(tans[0]) * tans[0])
    if nrm.length < 1e-4:
        nrm = tans[0].orthogonal()
    nrm.normalize()
    frames = []
    bm = bmesh.new()
    rings = []
    for i in range(n):
        t = tans[i]
        nrm = (nrm - nrm.dot(t) * t).normalized()
        bi = t.cross(nrm)
        s = i / (n - 1)
        r = rfun(s)
        frames.append((path[i], t, nrm.copy(), r))
        ring = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ring.append(bm.verts.new(path[i] + r * (math.cos(a) * nrm + math.sin(a) * bi)))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
    tip = bm.verts.new(path[-1] + tans[-1] * rfun(1.0))
    for k in range(seg):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], tip))
    start = bm.verts.new(path[0] - tans[0] * rfun(0.0) * 0.5)
    for k in range(seg):
        bm.faces.new((rings[0][(k + 1) % seg], rings[0][k], start))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish(name, bm, m)
    if suckers:
        sbm = bmesh.new()
        i0, step = suckers
        flip = 1
        for i in range(i0, n - 3, step):
            p, t, nr, r = frames[i]
            bi = t.cross(nr)
            ang = 0.45 * flip
            flip = -flip
            d = (math.cos(ang) * nr + math.sin(ang) * bi).normalized()
            rs = max(r * 0.42, 0.004)
            q = d.to_track_quat('Z', 'Y')
            M = Matrix.Translation(p + d * r * 0.92) @ q.to_matrix().to_4x4()
            bmesh.ops.create_cone(sbm, cap_ends=True, segments=12, radius1=rs, radius2=rs * 0.8,
                                  depth=rs * 0.55, matrix=M)
        finish(name + "_suckers", sbm, sucker_mat)
    return o, frames


# ---------- materials ----------
M_wood = mat("Wood", (0.28, 0.13, 0.06), 0.6)
M_wood_dark = mat("WoodDark", (0.16, 0.08, 0.04), 0.65)
M_wood_light = mat("WoodLight", (0.55, 0.36, 0.2), 0.55)
M_roof = mat("RoofRed", (0.45, 0.06, 0.04), 0.55)
M_noren = mat("NorenNavy", (0.03, 0.05, 0.16), 0.9)
M_white = mat("ClothWhite", (0.92, 0.9, 0.85), 0.8)
M_floor = mat("Ground", (0.05, 0.05, 0.06), 0.85)
M_metal = mat("Steel", (0.85, 0.83, 0.8), 0.38, 0.6)
M_black = mat("BlackIron", (0.03, 0.03, 0.03), 0.5, 0.6)
M_broth = mat("Broth", (0.62, 0.36, 0.13), 0.08, coat=0.5)
M_noodle = mat("Noodle", (0.95, 0.78, 0.35), 0.4, sss=0.2)
M_bowl = mat("BowlRed", (0.55, 0.05, 0.04), 0.25, coat=0.6)
M_bowl_in = mat("BowlCream", (0.92, 0.88, 0.78), 0.3)
M_egg = mat("EggWhite", (0.95, 0.92, 0.85), 0.3)
M_yolk = mat("Yolk", (1.0, 0.5, 0.05), 0.25)
M_chashu = mat("Chashu", (0.55, 0.3, 0.17), 0.5)
M_nori = mat("Nori", (0.03, 0.06, 0.03), 0.6)
M_naruto_pink = mat("NarutoPink", (0.95, 0.35, 0.5), 0.5)
M_scallion = mat("Scallion", (0.25, 0.65, 0.15), 0.5)
M_octo = mat("OctopusSkin", (0.85, 0.16, 0.08), 0.35, sss=0.25, coat=0.3)
M_sucker = mat("Sucker", (1.0, 0.75, 0.62), 0.4, sss=0.2)
M_eye = mat("EyeWhite", (0.98, 0.98, 0.98), 0.15)
M_pupil = mat("Pupil", (0.01, 0.01, 0.02), 0.05, coat=1.0)
M_blush = mat("Blush", (1.0, 0.45, 0.45), 0.6)
M_hat = mat("ChefHat", (0.97, 0.97, 0.95), 0.75)
M_lantern = mat("Lantern", (0.85, 0.08, 0.05), 0.6, emit=(1.0, 0.07, 0.02), estr=2.5)
M_glow = mat("WarmGlow", (1, 0.85, 0.6), 0.5, emit=(1.0, 0.8, 0.5), estr=8.0)
M_steam = mat("Steam", (1, 1, 1), 0.9, alpha=0.22)
M_soy = mat("SoyGlass", (0.08, 0.02, 0.01), 0.1)
M_chili = mat("Chili", (0.75, 0.1, 0.02), 0.4)
M_flame = mat("Flame", (0.2, 0.4, 1.0), 0.5, emit=(0.2, 0.45, 1.0), estr=10.0)
M_text = mat("SignText", (0.95, 0.9, 0.8), 0.5, emit=(1.0, 0.9, 0.7), estr=1.5)
M_seat = mat("SeatRed", (0.6, 0.05, 0.05), 0.4)

# ---------- ground ----------
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=12)
finish("Ground", bm, M_floor, smooth=False)

# ---------- booth ----------
box("CounterTop", (0, -0.75, 1.0), (3.3, 0.56, 0.08), M_wood_light)
box("CounterFront", (0, -0.97, 0.48), (3.1, 0.06, 0.96), M_wood)
for i in range(11):
    x = -1.5 + i * 0.3
    box(f"CounterSlat{i}", (x, -1.005, 0.48), (0.035, 0.02, 0.92), M_wood_dark, bevel=0.003)
box("CounterSideL", (-1.55, -0.62, 0.48), (0.06, 0.7, 0.96), M_wood)
box("CounterSideR", (1.55, -0.62, 0.48), (0.06, 0.7, 0.96), M_wood)
box("BackCounter", (0, 0.95, 0.45), (3.1, 0.6, 0.9), M_wood)
box("BackCounterTop", (0, 0.95, 0.915), (3.2, 0.66, 0.03), M_metal, bevel=0.004)
box("BackWall", (0, 1.27, 1.9), (3.1, 0.05, 2.0), M_wood_dark)
box("Shelf", (0, 1.15, 1.85), (2.6, 0.2, 0.03), M_wood_light)

ROOF_ANG = math.radians(8)


def roof_z(y):
    return 3.1 + (y - 0.12) * math.tan(ROOF_ANG)


for sx in (-1, 1):
    for y in (-1.0, 1.25):
        h = roof_z(y)
        box(f"Post{sx}{y}", (sx * 1.6, y, h / 2), (0.1, 0.1, h), M_wood_dark)
box("Roof", (0, 0.12, 3.1 + 0.04), (3.9, 3.0, 0.06), M_roof, rot=(ROOF_ANG, 0, 0))
box("RoofTrimF", (0, -1.38, roof_z(-1.38) - 0.02), (3.95, 0.06, 0.14), M_wood_dark)
box("BeamFront", (0, -1.0, roof_z(-1.0) - 0.12), (3.3, 0.1, 0.12), M_wood_dark)
box("BeamBack", (0, 1.25, roof_z(1.25) - 0.12), (3.3, 0.1, 0.12), M_wood_dark)
for sx in (-1, 1):
    box(f"BeamSide{sx}", (sx * 1.6, 0.12, 3.0), (0.1, 2.3, 0.1), M_wood_dark, rot=(ROOF_ANG, 0, 0))

# noren curtains
ntop = roof_z(-1.0) - 0.18
for i in range(5):
    x = -1.28 + i * 0.64
    p = box(f"Noren{i}", (x, -1.06, ntop - 0.2), (0.6, 0.012, 0.4), M_noren, bevel=0.0)
    cyl(f"NorenMark{i}", (x, -1.07, ntop - 0.24), 0.11, 0.004, M_white, rot=(math.pi / 2, 0, 0))
    cyl(f"NorenMarkIn{i}", (x, -1.073, ntop - 0.24), 0.07, 0.004, M_noren, rot=(math.pi / 2, 0, 0))
cyl_between("NorenRod", (-1.65, -1.06, ntop + 0.01), (1.65, -1.06, ntop + 0.01), 0.015, M_wood_light)

# sign
sz = roof_z(-1.3) + 0.25
box("SignBoard", (0, -1.3, sz), (1.7, 0.07, 0.38), M_wood_dark)
box("SignInner", (0, -1.34, sz), (1.58, 0.01, 0.3), M_roof, bevel=0.0)
fc = bpy.data.curves.new("SignText", 'FONT')
fc.body = "RAMEN"
fc.align_x = 'CENTER'
fc.align_y = 'CENTER'
fc.size = 0.24
fc.extrude = 0.01
fc.space_character = 1.15
to = bpy.data.objects.new("SignTextTmp", fc)
COL.objects.link(to)
to.location = (0, -1.36, sz)
to.rotation_euler = (math.pi / 2, 0, 0)
bpy.context.view_layer.update()
me = bpy.data.meshes.new_from_object(to.evaluated_get(bpy.context.evaluated_depsgraph_get()))
txt = bpy.data.objects.new("SignText", me)
COL.objects.link(txt)
txt.matrix_world = to.matrix_world.copy()
me.materials.clear(); me.materials.append(M_text)
bpy.data.objects.remove(to, do_unlink=True)

# lanterns (chochin)
lprof = [(0.0, -0.22)] + [(0.17 * math.sin(math.pi * k / 16) + 0.05, -0.2 + 0.4 * k / 16) for k in range(17)] + [(0.0, 0.22)]
for sx in (-1, 1):
    lx, ly, lz = sx * 1.85, -1.15, 2.35
    lathe(f"Lantern{sx}", lprof, M_lantern, loc=(lx, ly, lz), seg=32)
    for k in range(1, 8):
        z = -0.2 + 0.4 * k / 8
        rr = 0.17 * math.sin(math.pi * k / 8) + 0.052
        lathe(f"LanternRib{sx}{k}", [(rr, z - 0.004), (rr + 0.004, z), (rr, z + 0.004)], M_wood_dark,
              loc=(lx, ly, lz), seg=32)
    cyl(f"LanternCapT{sx}", (lx, ly, lz + 0.22), 0.07, 0.04, M_black)
    cyl(f"LanternCapB{sx}", (lx, ly, lz - 0.22), 0.07, 0.04, M_black)
    cyl_between(f"LanternCord{sx}", (lx, ly, lz + 0.24), (lx, ly, roof_z(ly) - 0.05), 0.006, M_black)
    L = bpy.data.lights.new(f"LanternLight{sx}", 'POINT')
    L.energy = 120; L.color = (1.0, 0.45, 0.2); L.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(f"LanternLight{sx}", L); COL.objects.link(lo); lo.location = (lx, ly, lz)

# hanging bulb inside booth
cyl_between("BulbCord", (0, 0.2, roof_z(0.2) - 0.02), (0, 0.2, 2.75), 0.005, M_black)
lathe("BulbShade", [(0.02, 0.0), (0.06, -0.03), (0.13, -0.1), (0.135, -0.11)], M_roof, loc=(0, 0.2, 2.76))
sphere("Bulb", (0, 0.2, 2.68), 0.04, M_glow)

# stools
for i, x in enumerate((-1.0, 0.0, 1.0)):
    cyl(f"StoolSeat{i}", (x, -1.45, 0.66), 0.19, 0.06, M_seat)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cyl_between(f"StoolLeg{i}{k}", (x + 0.1 * math.cos(a), -1.45 + 0.1 * math.sin(a), 0.63),
                    (x + 0.15 * math.cos(a), -1.45 + 0.15 * math.sin(a), 0.0), 0.018, M_wood_dark, seg=8)

# ---------- ramen bowl ----------
BOWL_OUT = [(0.0, 0.0), (0.065, 0.0), (0.07, 0.02), (0.11, 0.035), (0.15, 0.07), (0.172, 0.11), (0.178, 0.125)]
BOWL_IN = [(0.178, 0.125), (0.168, 0.126), (0.16, 0.1), (0.135, 0.065), (0.09, 0.04), (0.0, 0.035)]


def ramen(tag, cx, cy, cz, full=True):
    lathe(f"Bowl{tag}", BOWL_OUT, M_bowl, loc=(cx, cy, cz))
    lathe(f"BowlIn{tag}", BOWL_IN, M_bowl_in, loc=(cx, cy, cz))
    if not full:
        return
    bz = cz + 0.105
    cyl(f"Broth{tag}", (cx, cy, bz), 0.158, 0.004, M_broth, seg=40)
    # noodles: wavy strands
    for k in range(14):
        a0 = random.uniform(0, 2 * math.pi)
        rr = random.uniform(0.0, 0.07)
        pts = []
        for j in range(6):
            a = a0 + j * 0.5
            r = rr + 0.02 * math.sin(j * 1.7 + k)
            pts.append((cx + (0.03 + r) * math.cos(a), cy + (0.03 + r) * math.sin(a),
                        bz + 0.004 + 0.006 * math.sin(j * 2.1 + k)))
        tube(f"Noodle{tag}_{k}", pts, lambda s: 0.0045, M_noodle, seg=6, samples=24)
    # chashu
    for k, (dx, dy, ry) in enumerate(((-0.07, 0.06, 0.4), (-0.09, -0.01, 0.3))):
        c = cyl(f"Chashu{tag}{k}", (cx + dx, cy + dy, bz + 0.012), 0.05, 0.012, M_chashu, rot=(0.3, ry, 0))
    # egg
    sphere(f"Egg{tag}", (cx + 0.07, cy - 0.05, bz + 0.004), 0.034, M_egg, scale=(1, 1.35, 0.6))
    sphere(f"Yolk{tag}", (cx + 0.07, cy - 0.05, bz + 0.016), 0.018, M_yolk, scale=(1, 1.1, 0.35))
    # nori
    box(f"Nori{tag}", (cx + 0.02, cy + 0.12, bz + 0.05), (0.11, 0.005, 0.12), M_nori, rot=(-0.35, 0, 0), bevel=0)
    # naruto
    cyl(f"Naruto{tag}", (cx + 0.08, cy + 0.05, bz + 0.008), 0.03, 0.008, M_egg, rot=(0.15, 0, 0))
    lathe(f"NarutoSwirl{tag}", [(0.012, 0.0), (0.016, 0.003), (0.02, 0.0)], M_naruto_pink,
          loc=(cx + 0.08, cy + 0.05, bz + 0.012), seg=16, rot=(0.15, 0, 0))
    # scallions
    for k in range(18):
        a = random.uniform(0, 2 * math.pi); r = random.uniform(0.0, 0.08)
        cyl(f"Scallion{tag}{k}", (cx + r * math.cos(a) - 0.01, cy + r * math.sin(a), bz + 0.016),
            0.007, 0.004, M_scallion, seg=8, rot=(random.uniform(-.3, .3), random.uniform(-.3, .3), 0))


def steam(tag, cx, cy, cz, n=3, h=0.45, spread=0.06):
    for k in range(n):
        ox = (k - (n - 1) / 2) * spread * 0.9
        ph = random.uniform(0, 6.28)
        pts = [(cx + ox + 0.035 * math.sin(ph + j * 1.6), cy + 0.01 * math.cos(ph + j), cz + 0.03 + h * j / 5)
               for j in range(6)]
        tube(f"Steam{tag}{k}", pts, lambda s: 0.004 + 0.014 * math.sin(math.pi * s), M_steam,
             seg=10, samples=40)


ramen("A", 0.55, -0.72, 1.04)
ramen("B", -0.48, -0.74, 1.04)
steam("A", 0.55, -0.72, 1.18, n=2, h=0.35, spread=0.04)
# stacked clean bowls on shelf
for i in range(3):
    for j in range(3):
        lathe(f"StackBowl{i}{j}", BOWL_OUT, M_bowl, loc=(-1.0 + i * 0.4, 1.15, 1.867 + j * 0.045), seg=32)

# customer chopsticks + condiments
for k, x in enumerate((0.95, -1.0)):
    for d in (-0.008, 0.008):
        cyl_between(f"Chop{k}{d}", (x + d, -0.62, 1.05), (x + d * 2.5, -0.88, 1.05), 0.005, M_wood_light, seg=6)
cyl("SoyBottle", (1.25, -0.6, 1.14), 0.035, 0.18, M_soy)
cyl("SoyCap", (1.25, -0.6, 1.25), 0.02, 0.04, M_roof)
cyl("ChiliJar", (1.35, -0.68, 1.1), 0.04, 0.1, M_chili)
cyl("ChiliLid", (1.35, -0.68, 1.155), 0.042, 0.015, M_black)
cyl("ChopCup", (-1.3, -0.62, 1.12), 0.045, 0.16, M_wood_dark)
for k in range(9):
    a = k * 0.7
    cyl_between(f"CupChop{k}", (-1.3 + 0.02 * math.cos(a), -0.62 + 0.02 * math.sin(a), 1.06),
                (-1.3 + 0.04 * math.cos(a), -0.62 + 0.04 * math.sin(a), 1.32), 0.004, M_wood_light, seg=6)
box("NapkinBox", (1.1, -0.58, 1.09), (0.12, 0.08, 0.09), M_white)

# ---------- kitchen: pots ----------
for tag, px, r, h in (("Stock", -0.9, 0.3, 0.45), ("Boil", 0.9, 0.27, 0.36)):
    cyl(f"Burner{tag}", (px, 0.95, 0.94), r * 0.8, 0.04, M_black)
    for k in range(10):
        a = k * math.pi / 5
        sphere(f"Flame{tag}{k}", (px + r * 0.6 * math.cos(a), 0.95 + r * 0.6 * math.sin(a), 0.97), 0.02, M_flame,
               scale=(1, 1, 1.8), seg=8, rings=6)
    top = 0.96 + h
    lathe(f"Pot{tag}", [(0, 0.96), (r, 0.96), (r, top), (r + 0.012, top + 0.005), (r - 0.012, top), (r - 0.012, 0.98),
                        (0, 0.98)], M_metal, seg=48)
    cyl(f"PotLiquid{tag}", (px, 0.95, top - 0.07), r - 0.015, 0.01, M_broth if tag == "Stock" else M_steam, seg=40)
    bpy.data.objects[f"Pot{tag}"].location = (px, 0.95, 0)
    for sx in (-1, 1):
        cyl_between(f"PotHandle{tag}{sx}", (px + sx * r, 0.95, top - 0.06), (px + sx * (r + 0.06), 0.95, top - 0.06),
                    0.015, M_black, seg=8)
    steam(tag, px, 0.95, top, n=4, h=0.7, spread=0.1)
bpy.data.objects["PotLiquidBoil"].data.materials[0] = mat("BoilWater", (0.8, 0.75, 0.6), 0.05, alpha=0.7)

# ladle in stock pot
lathe("LadleBowl", [(0, -0.05), (0.04, -0.045), (0.06, -0.02), (0.065, 0.0), (0.06, 0.0), (0.05, -0.02), (0, -0.04)],
      M_metal, loc=(-0.88, 0.93, 1.38), seg=24)
cyl_between("LadleHandle", (-0.88 + 0.06, 0.93, 1.38), (-0.78, 0.72, 1.82), 0.01, M_metal, seg=8)

# noodle strainer (tebo) lifted from the boiler
SB = Vector((0.82, 0.88, 1.47))
lathe("Strainer", [(0, -0.14), (0.04, -0.13), (0.07, -0.06), (0.08, 0.0), (0.085, 0.005)], M_metal, loc=SB, seg=24)
for k in range(6):
    a = k * 1.05
    tube(f"StrainNoodle{k}", [(SB.x + 0.04 * math.cos(a), SB.y + 0.04 * math.sin(a), SB.z - 0.02),
                              (SB.x + 0.05 * math.cos(a + 1), SB.y + 0.05 * math.sin(a + 1), SB.z - 0.05),
                              (SB.x + 0.02 * math.cos(a + 2), SB.y + 0.02 * math.sin(a + 2), SB.z - 0.09)],
         lambda s: 0.005, M_noodle, seg=6, samples=16)
cyl_between("StrainerHandle", (SB.x - 0.08, SB.y, SB.z), (0.55, 0.62, 1.72), 0.011, M_wood_light, seg=8)

# chopsticks lifting noodles above bowl B
CT = Vector((-0.42, -0.56, 1.55))
CB = Vector((-0.48, -0.72, 1.33))
for d in (-0.012, 0.012):
    cyl_between(f"CookChop{d}", CT + Vector((d, 0, 0)), CB + Vector((d * 0.3, 0, 0)), 0.006, M_wood_light, seg=6,
                r2=0.0035)
for k in range(9):
    ox = random.uniform(-0.02, 0.02); oy = random.uniform(-0.02, 0.02)
    pts = [(CB.x + ox * 0.3, CB.y, CB.z + 0.005)]
    for j in range(1, 6):
        pts.append((CB.x + ox * (1 + j * 0.6) + 0.01 * math.sin(j * 2 + k), CB.y + oy * (1 + j * 0.4),
                    CB.z - j * 0.035))
    tube(f"LiftNoodle{k}", pts, lambda s: 0.0045, M_noodle, seg=6, samples=24)
steam("B", -0.48, -0.74, 1.2, n=2, h=0.3, spread=0.04)

# ---------- octopus ----------
bm = bmesh.new()
for (c, rad, rx) in (((0, 0.3, 1.38), (0.36, 0.33, 0.29), 0), ((0, 0.44, 1.82), (0.38, 0.41, 0.5), -14),
                     ((0, 0.3, 1.14), (0.27, 0.25, 0.15), 0)):
    M = Matrix.Translation(c) @ Matrix.Rotation(math.radians(rx), 4, 'X') @ Matrix.Diagonal((*rad, 1))
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0, matrix=M)
body = finish("OctopusBodyTmp", bm, M_octo)
rm = body.modifiers.new("Remesh", 'REMESH')
rm.mode = 'VOXEL'; rm.voxel_size = 0.012
sm = body.modifiers.new("Smooth", 'CORRECTIVE_SMOOTH')
sm.iterations = 12; sm.smooth_type = 'SIMPLE'; sm.use_only_smooth = True
sm2 = body.modifiers.new("Smooth2", 'SMOOTH')
sm2.factor = 0.8; sm2.iterations = 8
bpy.context.view_layer.update()
me = bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
bpy.data.objects.remove(body, do_unlink=True)
body = bpy.data.objects.new("OctopusBody", me)
COL.objects.link(body)
me.materials.clear(); me.materials.append(M_octo)
for p in me.polygons:
    p.use_smooth = True

# face details
FY = -0.03
for sx in (-1, 1):
    ex = sx * 0.15
    sphere(f"Eye{sx}", (ex, FY + 0.02, 1.47), 0.1, M_eye, scale=(1, 0.7, 1.1))
    sphere(f"Pupil{sx}", (ex - sx * 0.01, FY - 0.045, 1.46), 0.058, M_pupil, scale=(1, 0.5, 1.15))
    sphere(f"Glint{sx}", (ex - sx * 0.03, FY - 0.072, 1.5), 0.016, M_eye, scale=(1, 0.5, 1))
    sphere(f"Blush{sx}", (sx * 0.24, FY + 0.06, 1.33), 0.05, M_blush, scale=(1, 0.3, 0.6),
           rot=(0, 0, sx * -0.5))
    # brows
    tube(f"Brow{sx}", [(ex - 0.06, FY + 0.0, 1.6 + (0.0 if sx > 0 else 0.015)), (ex, FY - 0.015, 1.625),
                       (ex + 0.06, FY + 0.0, 1.6 + (0.015 if sx > 0 else 0.0))],
         lambda s: 0.012, M_wood_dark, seg=8, samples=12)
# smile
tube("Smile", [(-0.08, FY + 0.02, 1.32), (-0.04, FY - 0.02, 1.285), (0.0, FY - 0.03, 1.275),
               (0.04, FY - 0.02, 1.285), (0.08, FY + 0.02, 1.32)], lambda s: 0.011, M_pupil, seg=8, samples=24)

# chef hat sitting on the mantle (tilted with it)
hat_tilt = Matrix.Rotation(math.radians(-14), 4, 'X')
hat_base = Vector((0, 0.5, 2.08))


def hat_part(o, local):
    o.matrix_world = Matrix.Translation(hat_base) @ hat_tilt @ Matrix.Translation(local)


hb = lathe("HatBand", [(0.27, 0.0), (0.285, 0.0), (0.295, 0.17), (0.28, 0.17)], M_hat, seg=48)
hat_part(hb, Vector((0, 0, 0)))
puff_specs = [((0, 0, 0.27), 0.2), ((0.15, 0, 0.24), 0.16), ((-0.15, 0, 0.24), 0.16),
              ((0, 0.15, 0.24), 0.16), ((0, -0.15, 0.24), 0.16), ((0.11, 0.11, 0.25), 0.15),
              ((-0.11, 0.11, 0.25), 0.15), ((0.11, -0.11, 0.25), 0.15), ((-0.11, -0.11, 0.25), 0.15)]
for k, (p, r) in enumerate(puff_specs):
    s = sphere(f"HatPuff{k}", (0, 0, 0), r, M_hat, scale=(1, 1, 0.85))
    hat_part(s, Vector(p))


def taper(r0, r1=0.012, p=1.0):
    return lambda s: r1 + (r0 - r1) * (1 - s) ** p


arms = {
    # ladle in stock pot
    "ArmLadle": ([(-0.12, 0.38, 1.13), (-0.35, 0.5, 1.12), (-0.58, 0.62, 1.38), (-0.74, 0.7, 1.66),
                  (-0.8, 0.76, 1.74), (-0.76, 0.7, 1.78), (-0.74, 0.68, 1.72)], (0, 1, -0.3)),
    # noodle strainer
    "ArmStrainer": ([(0.12, 0.38, 1.13), (0.35, 0.5, 1.12), (0.48, 0.55, 1.4), (0.56, 0.6, 1.66),
                     (0.6, 0.66, 1.74), (0.56, 0.68, 1.7)], (0, 1, -0.3)),
    # holding bowl A
    "ArmBowl": ([(0.1, 0.18, 1.13), (0.25, -0.1, 1.2), (0.38, -0.45, 1.2)]
                + [(0.55 + 0.205 * math.cos(math.radians(a)), -0.72 + 0.205 * math.sin(math.radians(a)),
                    1.11 + 0.01 * i) for i, a in enumerate((140, 180, 220, 260, 300))], (0, 0, -1)),
    # chopsticks
    "ArmChop": ([(-0.1, 0.18, 1.13), (-0.22, -0.05, 1.3), (-0.33, -0.35, 1.48), (-0.4, -0.52, 1.56),
                 (-0.45, -0.58, 1.52), (-0.42, -0.6, 1.48), (-0.39, -0.56, 1.5)], (0, 0.3, -1)),
    # waving
    "ArmWave": ([(0.18, 0.4, 1.12), (0.45, 0.35, 1.25), (0.62, 0.22, 1.55), (0.64, 0.12, 1.85),
                 (0.56, 0.06, 2.02), (0.46, 0.08, 2.0), (0.46, 0.12, 1.92)], (-1, 0, 0)),
    # resting on counter
    "ArmRest": ([(-0.18, 0.3, 1.1), (-0.5, 0.05, 1.06), (-0.85, -0.42, 1.1), (-1.08, -0.72, 1.095),
                 (-1.3, -0.82, 1.095), (-1.42, -0.72, 1.1), (-1.36, -0.62, 1.12), (-1.27, -0.68, 1.13)], (0, 0, -1)),
    "ArmFloorL": ([(-0.08, 0.32, 1.05), (-0.22, 0.25, 0.6), (-0.35, 0.05, 0.2), (-0.6, -0.15, 0.06),
                   (-0.85, -0.1, 0.06), (-0.9, 0.08, 0.08), (-0.78, 0.12, 0.12)], (0, 0, -1)),
    "ArmFloorR": ([(0.08, 0.32, 1.05), (0.25, 0.3, 0.6), (0.4, 0.12, 0.2), (0.65, 0.0, 0.06),
                   (0.88, 0.1, 0.06), (0.88, 0.28, 0.08), (0.75, 0.28, 0.12)], (0, 0, -1)),
}
for name, (pts, under) in arms.items():
    tube(name, pts, taper(0.085, 0.014, 0.9), M_octo, seg=16, samples=90, under=under, suckers=(10, 4),
         sucker_mat=M_sucker)

# ---------- world & lights ----------
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.012, 0.018, 0.045, 1)
bg.inputs["Strength"].default_value = 1.0


def light(name, t, loc, energy, color, rot=(0, 0, 0), size=1.0):
    L = bpy.data.lights.new(name, t)
    L.energy = energy; L.color = color
    if t == 'AREA':
        L.size = size
    else:
        L.shadow_soft_size = size
    o = bpy.data.objects.new(name, L); COL.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o


light("BoothBulb", 'POINT', (0, 0.2, 2.6), 250, (1.0, 0.78, 0.5), size=0.1)
light("RoofGlow", 'AREA', (0, 0.1, 2.8), 150, (1.0, 0.7, 0.4), size=2.0)
light("KeyArea", 'AREA', (-1.8, -3.2, 3.6), 220, (1.0, 0.85, 0.7), rot=(math.radians(50), 0, math.radians(-30)),
      size=2.5)
light("MoonRim", 'AREA', (2.5, 3.5, 4.0), 500, (0.45, 0.6, 1.0), rot=(math.radians(-45), 0, math.radians(150)),
      size=3.0)
light("FillFront", 'AREA', (2.5, -3.0, 1.5), 60, (0.6, 0.7, 1.0), rot=(math.radians(75), 0, math.radians(40)),
      size=2.0)

# ---------- cameras ----------
def camera(name, loc, target, lens):
    c = bpy.data.cameras.new(name); c.lens = lens
    o = bpy.data.objects.new(name, c); COL.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o


cam_main = camera("CamMain", (2.9, -5.3, 2.1), (0.0, -0.1, 1.5), 30)
camera("CamClose", (1.0, -2.5, 1.85), (0.0, -0.2, 1.6), 36)
scene.camera = cam_main

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
