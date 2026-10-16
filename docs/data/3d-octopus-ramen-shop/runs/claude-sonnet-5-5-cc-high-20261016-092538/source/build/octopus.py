octo = empty("OctopusChef", parent=root)
skin = mat("OctoSkin", (0.86, 0.2, 0.1), 0.42)
skin_dark = mat("OctoSpots", (0.66, 0.16, 0.09), 0.5)
sucker_m = mat("OctoSucker", (0.98, 0.72, 0.66), 0.35)
eye_w = mat("EyeWhite", (0.97, 0.97, 0.95), 0.15)
pupil_m = mat("Pupil", (0.01, 0.01, 0.015), 0.1)
cheek_m = mat("Cheek", (1.0, 0.45, 0.45), 0.6)
toque_m = mat("Toque", (0.97, 0.97, 0.95), 0.8)
scarf_m = mat("Scarf", (0.75, 0.05, 0.05), 0.7)

C = Vector((0, 0.1, 1.78))
RAD = Vector((0.62, 0.58, 0.72))


def surf(x, z, off=0.0):
    t = 1 - (x / RAD.x) ** 2 - ((z - C.z) / RAD.z) ** 2
    y = C.y - RAD.y * math.sqrt(max(t, 0.0))
    n = Vector(((x) / RAD.x ** 2, (y - C.y) / RAD.y ** 2, (z - C.z) / RAD.z ** 2)).normalized()
    return Vector((x, y, z)) + n * off, n


# --- mantle (head) ---
bm = bm_sphere(1.0, 48, 28)
for v in bm.verts:
    co = v.co.copy()
    # slightly pear shaped: a bit narrower at the top, soft bulge near the bottom
    k = 1.0 - 0.10 * max(co.z, 0.0) ** 2
    v.co = Vector((co.x * RAD.x * k, co.y * RAD.y * k, co.z * RAD.z))
add("OctoMantle", bm, skin, tuple(C), parent=octo, smooth=True)

# skin spots
random.seed(21)
sp = bmesh.new()
for i in range(60):
    for _ in range(20):
        th = random.uniform(0, 2 * math.pi)
        ph = random.uniform(0.05, 1.35)
        x = RAD.x * math.sin(ph) * math.cos(th) * 0.97
        z = C.z + RAD.z * math.cos(ph)
        yy = C.y + RAD.y * math.sin(ph) * math.sin(th) * 0.97
        if yy > C.y - 0.1 or ph < 0.9:  # back & top & sides only
            break
    n = Vector((x / RAD.x ** 2, (yy - C.y) / RAD.y ** 2, (z - C.z) / RAD.z ** 2)).normalized()
    rr = random.uniform(0.02, 0.055)
    s = bm_sphere(rr, 10, 6, (1, 1, 0.35))
    q = n.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bm_xform(s, Matrix.Translation(Vector((x, yy, z)) + n * 0.005) @ q)
    merge(sp, s)
add("OctoSpotsMesh", sp, skin_dark, tuple(Vector((0, 0, 0))), parent=octo, smooth=True)

# --- eyes ---
for sgn in (-1, 1):
    ex = 0.255 * sgn
    ez = 1.92
    pos, n = surf(ex, ez, 0.02)
    eye = empty("Eye%s" % ("L" if sgn < 0 else "R"), tuple(pos), parent=octo)
    add("Sclera", bm_sphere(0.15, 24, 16), eye_w, (0, 0, 0), parent=eye, smooth=True)
    look = Vector((-0.10 * sgn, -1.0, 0.0)).normalized()
    pp = look * 0.105
    add("Pupil", bm_sphere(0.085, 18, 12, (1, 0.6, 1)), pupil_m, tuple(pp), parent=eye, smooth=True)
    add("Glint", bm_sphere(0.025, 10, 8), eye_w, tuple(pp + Vector((0.03 * -sgn * -1, -0.065, 0.045))), parent=eye)
    add("Glint2", bm_sphere(0.012, 8, 6), eye_w, tuple(pp + Vector((-0.03, -0.075, -0.035))), parent=eye)
    lid = bm_cap(0.158, True, 24, 12)
    kill = [v for v in lid.verts if v.co.z < 0.095]
    bmesh.ops.delete(lid, geom=kill, context='VERTS')
    add("Eyelid", lid, skin, (0, 0, 0), rot=(0.0, 0.0, 0.0), parent=eye, smooth=True)
    # tilt lids a little: friendly slant
    eye.children[-1].rotation_euler = (math.radians(-12), math.radians(10 * sgn), 0)

# --- cheeks ---
for sgn in (-1, 1):
    p, n = surf(0.40 * sgn, 1.6, 0.0)
    q = n.to_track_quat('Y', 'Z').to_euler()
    add("Cheek", bm_sphere(0.085, 14, 10, (1, 0.3, 0.65)), cheek_m, tuple(p), rot=tuple(q), parent=octo, smooth=True)

# --- smile ---
pts = []
for i in range(9):
    f = i / 8
    x = (f - 0.5) * 0.30
    z = 1.58 + 0.07 * (1 - (2 * f - 1) ** 2) * -1 + 0.0
    z = 1.54 + 0.06 * ((2 * f - 1) ** 2)
    p, n = surf(x, z, 0.003)
    pts.append(tuple(p))
add("Smile", simple_tube(pts, 0.011, 6, 4), mat("MouthDark", (0.25, 0.04, 0.04), 0.4), parent=octo, smooth=True)

# --- neckerchief ---
sc = bm_torus(1.0, 0.07, 40, 10)
for v in sc.verts:
    v.co.x *= 0.5
    v.co.y *= 0.46
add("Neckerchief", sc, scarf_m, (0, C.y, 1.27), parent=octo, smooth=True)
knot, kn = surf(0.0, 1.27, 0.04)
add("ScarfKnot", bm_sphere(0.075, 12, 8, (1, 0.8, 1)), scarf_m, tuple(knot), parent=octo, smooth=True)
for sgn in (-1, 1):
    add("ScarfTail", bm_box(0.09, 0.02, 0.22), scarf_m, (knot.x + 0.06 * sgn, knot.y - 0.02, knot.z - 0.13),
        rot=(0.1, 0, 0.25 * sgn), parent=octo)

# --- chef hat (toque) ---
hat = empty("ChefHat", (0, C.y + 0.02, 2.33), (math.radians(-4), math.radians(5), 0), parent=octo)
add("HatBand", bm_cyl(0.43, 0.46, 0.26, 36), toque_m, (0, 0, 0.0), parent=hat, smooth=True)
add("HatBandRim", bm_torus(0.445, 0.02, 36, 8), toque_m, (0, 0, -0.12), parent=hat, smooth=True)
add("HatPuffCenter", bm_sphere(0.40, 28, 18, (1, 1, 0.8)), toque_m, (0, 0, 0.42), parent=hat, smooth=True)
for i in range(7):
    a = i * 2 * math.pi / 7 + 0.2
    add("HatPuff%d" % i, bm_sphere(0.24, 18, 12, (1, 1, 1.05)), toque_m,
        (0.3 * math.cos(a), 0.3 * math.sin(a), 0.38 + 0.04 * (i % 2)), parent=hat, smooth=True)
add("HatPuffTop", bm_sphere(0.28, 20, 14), toque_m, (0.02, 0, 0.7), parent=hat, smooth=True)
for i in range(14):
    a = i * 2 * math.pi / 14
    add("HatPleat%d" % i, bm_cyl(0.012, 0.012, 0.22, 6), mat("ToquePleat", (0.86, 0.86, 0.84), 0.8),
        (0.444 * math.cos(a), 0.444 * math.sin(a), 0.0), parent=hat)

# ================= TENTACLES =================
ARM_R = 0.19


def arm(name, ctrl, r0=ARM_R, n0=(0, 0, -1), sucker_dir=1, per=10, suck_from=0.18, rtip=0.014, power=1.0):
    path = catmull(ctrl, per)
    # arc length parameter
    L = [0.0]
    for i in range(1, len(path)):
        L.append(L[-1] + (path[i] - path[i - 1]).length)
    tot = L[-1]
    radii = [rtip + (r0 - rtip) * (1 - (l / tot)) ** (1.15 * power) for l in L]
    fr = frames_for(path, radii, n0)
    ob = add(name, tube_bm(fr, 14), skin, parent=octo, smooth=True)
    # suckers
    sbm = bmesh.new()
    acc = 0.0
    side = 1
    for i in range(1, len(fr)):
        p, t, n, b, r = fr[i]
        acc += L[i] - L[i - 1]
        u = L[i] / tot
        if u < suck_from or u > 0.97:
            continue
        if acc < r * 2.1:
            continue
        acc = 0.0
        side = -side
        d = (n * sucker_dir * 0.9 + b * side * 0.45).normalized()
        sr = max(r * 0.42, 0.01)
        s = bm_sphere(sr, 10, 6, (1, 1, 0.5))
        m = Matrix.Translation(p + d * (r * 0.93)) @ Matrix(((t.x, d.cross(t).x, d.x), (t.y, d.cross(t).y, d.y),
                                                            (t.z, d.cross(t).z, d.z))).to_4x4()
        bm_xform(s, m)
        merge(sbm, s)
    add(name + "Suckers", sbm, sucker_m, parent=octo, smooth=True)
    return fr


# ---- A: ladle (right) ----
lad0 = Vector((1.05, 0.38, 2.12))
lad1 = Vector((1.42, 0.78, 1.46))
ld = (lad1 - lad0).normalized()
lg = lad0 + ld * 0.28
ctrlA = [(0.3, 0.2, 1.2), (0.7, 0.1, 1.4), (0.95, 0.05, 1.7), (0.98, 0.18, 1.95)]
ctrlA += helix(ctrlA[-1], lg, ld, 0.058, 1.4, 0.16)
arm("ArmLadle", ctrlA, per=8)
lh = simple_tube([tuple(lad0), tuple(lad1)], 0.017, 8, 2)
add("LadleHandle", lh, steel_m, parent=props, smooth=True)
add("LadleCup", bm_cap(0.1, False, 20, 10, (1, 1, 0.8)), steel_m, tuple(lad1 + Vector((0, 0, -0.02))), parent=props, smooth=True)
add("LadleTop", bm_sphere(0.028, 10, 8), steel_m, tuple(lad0), parent=props)

# ---- B: chopsticks lifting noodles (center right) ----
chL = Vector((0.0, -0.96, 1.58))
chU = Vector((0.95, -0.9, 1.82))
cd = (chU - chL).normalized()
cg = chL + (chU - chL) * 0.52
ctrlB = [(0.2, -0.1, 1.2), (0.6, -0.3, 1.3), (0.95, -0.55, 1.5), (0.75, -0.88, 1.62)]
ctrlB += helix(ctrlB[-1], cg, cd, 0.05, 1.3, 0.1)
arm("ArmChopsticks", ctrlB, per=8)
side = cd.cross(Vector((0, 0, 1))).normalized() * 0.014
for s in (-1, 1):
    a, b = chL + side * s, chU + side * s * 1.6
    add("Chopstick", simple_tube([tuple(a), tuple(b)], 0.0085, 6, 2, rfun=lambda f: 0.0065 + 0.0035 * f), mat("ChopWood", (0.55, 0.32, 0.12), 0.5),
        parent=props, smooth=True)
# lifted noodles dangling from the chopsticks into the bowl
random.seed(12)
nb = bmesh.new()
for i in range(9):
    sx = (i - 4) * 0.006
    top = chL + Vector((sx, 0.02, 0.0)) + side * random.uniform(-1, 1)
    bot = Vector((0.1 + random.uniform(-0.1, 0.1), -0.95 + random.uniform(-0.1, 0.1), TOP + 0.32 + random.uniform(-0.02, 0.02)))
    pts = []
    for k in range(9):
        f = k / 8
        base = top.lerp(bot, f)
        wob = 0.015 * math.sin(f * 10 + i) * (1 - f)
        pts.append((base.x + wob, base.y + wob * 0.5, base.z - 0.1 * f * (1 - f) * 0))
    merge(nb, simple_tube(pts, 0.0085, 5, 3))
add("LiftedNoodles", nb, mat("Noodle", (0.96, 0.80, 0.33), 0.45), parent=props, smooth=True)

# ---- C: strainer (left) ----
st0 = Vector((-1.45, 0.68, 1.68))
sdir = Vector((0.55, -0.40, 0.55)).normalized()
st1 = st0 + sdir * 0.82
sg = st0 + sdir * 0.5
ctrlC = [(-0.3, 0.2, 1.2), (-0.62, 0.1, 1.4), (-0.78, 0.12, 1.7), (-0.8, 0.28, 1.9)]
ctrlC += helix(ctrlC[-1], sg, sdir, 0.056, 1.4, 0.15)
arm("ArmStrainer", ctrlC, per=8)
add("StrainerHandle", simple_tube([tuple(st0), tuple(st1)], 0.017, 8, 2), wood_light, parent=props, smooth=True)
tk = bm_cap(0.17, False, 24, 12, (1, 1, 0.75))
add("StrainerBasket", tk, mat("StrainerMesh", (0.5, 0.5, 0.52), 0.35, metal=1.0), tuple(st0), parent=props, smooth=True)
add("StrainerRim", bm_torus(0.17, 0.008, 28, 6), steel_m, tuple(st0), parent=props)
add("StrainerNoodles", bm_cap(0.155, True, 20, 8, (1, 1, 0.55)), mat("Noodle", (0.96, 0.80, 0.33), 0.45),
    tuple(st0 + Vector((0, 0, -0.04))), parent=props, smooth=True)

# ---- D: bowl server (left front) ----
bc = Vector((-0.85, -0.92, TOP))
pre = (-0.5, -0.6, TOP + 0.2)
ctrlD = [(-0.3, 0.0, 1.2), (-0.35, -0.3, 1.38), (-0.42, -0.5, 1.34), pre]
ctrlD += helix(pre, (bc.x, bc.y, TOP + 0.1), (0, 0, 1), 0.27, 0.8, 0.07)
arm("ArmBowl", ctrlD, per=8, sucker_dir=1)

# ---- E: left curl on counter (suckers up) ----
ctrlE = [(-0.45, 0.0, 1.2), (-0.85, -0.2, 1.46), (-1.35, -0.62, 1.34), (-1.82, -1.0, TOP + 0.1)]
ctrlE += spiral((-1.8, -0.85), 0.16, 0.05, 1.2, TOP + 0.045, start_angle=-1.2, ccw=False)
arm("ArmCurlLeft", ctrlE, per=8, n0=(0, 0, 1), sucker_dir=1, rtip=0.02, suck_from=0.3, r0=0.17)

# ---- F: right curl on counter ----
ctrlF = [(0.5, 0.0, 1.2), (1.0, -0.15, 1.46), (1.6, -0.5, 1.34), (2.0, -0.95, TOP + 0.1)]
ctrlF += spiral((1.97, -0.82), 0.15, 0.05, 1.2, TOP + 0.045, start_angle=-1.3, ccw=True)
arm("ArmCurlRight", ctrlF, per=8, n0=(0, 0, 1), sucker_dir=1, rtip=0.02, suck_from=0.3, r0=0.17)

# ---- G/H: draped on floor behind ----
ctrlG = [(-0.3, 0.35, 1.15), (-0.7, 0.8, 0.9), (-0.8, 1.15, 0.5), (-0.5, 1.2, FLOOR + 0.06)]
ctrlG += spiral((-0.3, 1.05), 0.28, 0.06, 1.1, FLOOR + 0.04, start_angle=3.0, ccw=True)
arm("ArmFloorLeft", ctrlG, per=8, n0=(0, 0, 1), rtip=0.02, suck_from=0.3, r0=0.17)
ctrlH = [(0.3, 0.35, 1.15), (0.7, 0.8, 0.9), (0.8, 1.15, 0.5), (0.5, 1.2, FLOOR + 0.06)]
ctrlH += spiral((0.3, 1.05), 0.28, 0.06, 1.1, FLOOR + 0.04, start_angle=0.2, ccw=False)
arm("ArmFloorRight", ctrlH, per=8, n0=(0, 0, 1), rtip=0.02, suck_from=0.3, r0=0.17)
