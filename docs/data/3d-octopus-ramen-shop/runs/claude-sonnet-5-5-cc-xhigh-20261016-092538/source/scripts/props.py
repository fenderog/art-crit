"""Props: stove, pots, utensils, ramen bowls, condiments, shelves, steam."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import layout as L

PI = pi
V = Vector


def pm():
    return {
        'steel': mat('Steel', '#c4c9d1', rough=0.3, metal=0.7),
        'steel_dark': mat('Steel_Dark', '#4a4e57', rough=0.4, metal=0.9),
        'iron': mat('Iron', '#26282e', rough=0.5, metal=0.7),
        'pot': mat('Pot_Steel', '#cfd4db', rough=0.34, metal=0.55),
        'wood_light': mat('Wood_Light', '#dcae72', rough=0.55),
        'wood_handle': mat('Wood_Handle', '#b27a44', rough=0.5),
        'wood_dark': mat('Wood_DarkHandle', '#2c1a10', rough=0.45),
        'water': mat('Pot_Water', '#e9eef0', rough=0.15, coat=0.4),
        'milk': mat('Pot_Broth', '#ecd7a6', rough=0.2, coat=0.4),
        'bubble': mat('Bubble', '#ffffff', rough=0.1),
        'noodle': mat('Noodle', '#f3d982', rough=0.35, coat=0.15),
        'bowl_red': mat('Bowl_Red', '#b3202b', rough=0.22, coat=0.4),
        'bowl_cream': mat('Bowl_Cream', '#f6ecdb', rough=0.2, coat=0.4),
        'bowl_gold': mat('Bowl_Gold', '#e2b34a', rough=0.3, metal=0.6),
        'broth': mat('Broth', '#c97a2b', rough=0.12, coat=0.5),
        'oil': mat('Oil', '#f6cf62', rough=0.08, coat=0.5),
        'chashu_edge': mat('Chashu_Edge', '#7e4226', rough=0.45),
        'chashu_face': mat('Chashu_Face', '#e09a77', rough=0.4),
        'egg_white': mat('Egg_White', '#fbf4e4', rough=0.3),
        'yolk': mat('Egg_Yolk', '#f4a315', rough=0.2, coat=0.3),
        'nori': mat('Nori', '#14301f', rough=0.35, coat=0.2),
        'naruto_w': mat('Naruto_White', '#fbf1ee', rough=0.4),
        'naruto_p': mat('Naruto_Pink', '#f0668a', rough=0.4),
        'scallion': mat('Scallion', '#6dc03a', rough=0.45),
        'scallion_w': mat('Scallion_White', '#e8f2c8', rough=0.45),
        'menma': mat('Menma', '#c8964f', rough=0.5),
        'knife': mat('Knife_Steel', '#dfe3ea', rough=0.2, metal=0.55),
        'glass_dark': mat('Glass_Soy', '#2a1309', rough=0.08, coat=0.6),
        'glass_red': mat('Glass_Chili', '#b41e14', rough=0.1, coat=0.5),
        'white': mat('White_Ceramic', '#f3efe6', rough=0.3, coat=0.3),
        'black': mat('Black_Plastic', '#16161a', rough=0.4),
        'steam': mat('Steam', '#ffffff', rough=1.0, alpha=0.11, spec=0.0),
        'steam_hi': mat('Steam_Fade', '#ffffff', rough=1.0, alpha=0.055, spec=0.0),
        'flame': mat('Flame', '#ff7a1a', rough=0.5, emit='#ff6a10', emit_strength=4.0),
        'bamboo': mat('Bamboo_Prop', '#b6a35a', rough=0.6),
        'paper': mat('Paper', '#f4e8cc', rough=0.9),
        'bulb': mat('Bulb', '#fff2c8', rough=0.3, emit='#ffd27a', emit_strength=6.0),
        'lantern_cap': mat('Lantern_Cap', '#16100c', rough=0.5),
        'cloth_blue': mat('Cloth_Blue', '#27468a', rough=0.9),
        'jar': mat('Jar_Ceramic', '#6f7f8c', rough=0.3, coat=0.4),
        'jar_brown': mat('Jar_Brown', '#7a4b2a', rough=0.3, coat=0.4),
    }


P = None


# ----------------------------------------------------------------------------- generic bits
def rotm(rot):
    return Euler(rot, 'XYZ').to_matrix().to_4x4()


def ring_pts(c, r, n=24, z=0.0):
    return [V((c.x + r * cos(2 * PI * i / n), c.y + r * sin(2 * PI * i / n), c.z + z)) for i in range(n + 1)]


def prof_smooth(ctrl, n=40, per=8):
    pts, _ = spline([(r, 0, z) for r, z in ctrl], n, per=per)
    out = [(max(p.x, 0.0), p.z) for p in pts]
    return out


# ----------------------------------------------------------------------------- cooking gear
def build_stove(root):
    g = group("Stove", root)
    # body
    make("Stove_Body", box(1.1, 0.95, 0.89, 0.012), P['steel_dark'], loc=(-1.0, 0.475, 0.06 + 0.445), parent=g, sharp=30)
    make("Stove_Top", box(1.12, 0.97, 0.03, 0.01), P['steel'], loc=(-1.0, 0.475, L.STOVE_TOP - 0.015), parent=g, sharp=30)
    for k, x in enumerate((-1.30, -0.80)):
        make(f"Stove_Knob_{k}", cyl(0.032, 0.026, 0.035, segs=16), P['black'], loc=(x, -0.01, 0.78), rot=(PI / 2, 0, 0),
             parent=g)
        make(f"Stove_KnobRing_{k}", torus(0.036, 0.005, segs=20, sides=6), P['steel'], loc=(x, -0.0, 0.78), rot=(PI / 2, 0, 0),
             parent=g)
    # burner rings under pots
    for c in (L.NOODLE_POT, L.STOCK_POT):
        make("Burner", torus(0.14, 0.012, segs=28, sides=8), P['iron'], loc=(c.x, c.y, L.STOVE_TOP + 0.01), parent=g)
        make("Burner_Grate", box(0.34, 0.03, 0.012, 0.003, 1), P['iron'], loc=(c.x, c.y, L.STOVE_TOP + 0.02), parent=g)
        make("Burner_Grate2", box(0.03, 0.34, 0.012, 0.003, 1), P['iron'], loc=(c.x, c.y, L.STOVE_TOP + 0.02), parent=g)


def build_pot(name, parent, base, r, h, liquid, liquid_drop, mats_liq, with_bubbles=True, seed=1):
    g = group(name, parent, loc=tuple(base))
    prof = [(0.0, 0.0), (r - 0.012, 0.0), (r, 0.012), (r, h - 0.012), (r + 0.016, h), (r + 0.016, h + 0.008),
            (r + 0.004, h + 0.01), (r - 0.012, h + 0.002), (r - 0.012, 0.03), (0.0, 0.03)]
    bm = lathe(prof, segs=48)
    make(f"{name}_Body", bm, P['pot'], parent=g, sharp=50)
    # liquid
    zl = h - liquid_drop
    pl = [(r - 0.011, zl - 0.006), (r * 0.7, zl), (0.0, zl + 0.002)]
    make(f"{name}_Liquid", lathe(pl, segs=48), mats_liq, parent=g)
    # handles
    for s in (-1, 1):
        pts = [V((s * (r + 0.005), 0, h - 0.05)), V((s * (r + 0.05), 0, h - 0.05)), V((s * (r + 0.065), 0, h - 0.09)),
               V((s * (r + 0.05), 0, h - 0.125)), V((s * (r + 0.005), 0, h - 0.125))]
        bm = wire(pts, 0.011, sides=8, n=24)
        make(f"{name}_Handle_{'L' if s < 0 else 'R'}", bm, P['steel_dark'], parent=g)
    if with_bubbles:
        rng = random.Random(seed)
        bm = bmesh.new()
        for i in range(26):
            a = rng.random() * 2 * PI
            rr = (r - 0.03) * sqrt(rng.random())
            br = rng.uniform(0.008, 0.02)
            s = sphere(br, br, br * 0.7, u=10, v=6)
            add_bm(bm, s, Matrix.Translation((rr * cos(a), rr * sin(a), zl + 0.002)))
        make(f"{name}_Bubbles", bm, P['bubble'], parent=g)
    return g


def noodle_mound(center_z, R, height, count, seed, rot_deg=20, spread=25, amp=0.012, rad=0.0036, keep=0.0):
    rng = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        ang = radians(rot_deg + rng.uniform(-spread, spread))
        d = V((cos(ang), sin(ang), 0))
        p = V((-d.y, d.x, 0))
        off = rng.uniform(-0.92, 0.92) * R
        half = sqrt(max(R * R - off * off, 1e-4)) * 0.97
        ph = rng.uniform(0, 2 * PI)
        fr = rng.uniform(5, 9)
        ctrl = []
        for k in range(14):
            u = -1 + 2 * k / 13
            lat = sin(u * fr + ph) * amp * (0.5 + rng.random() * 0.5)
            pt = d * (u * half) + p * (off + lat)
            rr = sqrt(pt.x ** 2 + pt.y ** 2)
            dome = max(0.0, 1 - (rr / R) ** 2)
            pt.z = center_z + 0.002 + height * dome + rad + rng.uniform(0, 0.006) * dome
            ctrl.append(pt)
        s = wire(ctrl, rad, sides=6, n=34, per=6)
        add_bm(bm, s)
    return bm


def build_tebo(root):
    g = group("Tebo", root)
    C = L.TEBO_C
    R = L.TEBO_R
    bm = bmesh.new()
    add_bm(bm, torus(R, 0.0048, segs=36, sides=6), Matrix.Translation(C))
    for k in range(10):
        a = 2 * PI * k / 10
        pts = [V((C.x + R * cos(a) * sin(t), C.y + R * sin(a) * sin(t), C.z - R * (1 - cos(t)))) for t in
               [i / 8 * PI / 2 for i in range(9)]]
        pts = [V((C.x + R * cos(a) * cos(t), C.y + R * sin(a) * cos(t), C.z - R * sin(t))) for t in
               [i / 8 * PI / 2 for i in range(9)]]
        add_bm(bm, wire(pts, 0.0028, sides=5, n=14, per=6))
    for j in range(1, 4):
        t = j / 4 * PI / 2
        rr = R * cos(t)
        add_bm(bm, torus(rr, 0.0028, segs=30, sides=5), Matrix.Translation((C.x, C.y, C.z - R * sin(t))))
    make("Tebo_Basket", bm, P['steel'], parent=g)
    # noodles in the basket
    nb = noodle_mound(C.z - 0.03, 0.095, 0.055, 24, 11, rot_deg=60, spread=40, amp=0.01)
    xform(nb, Matrix.Translation((C.x, C.y, 0)))
    rng = random.Random(21)
    for k in range(9):
        a = rng.random() * 2 * PI
        rr = 0.075 * sqrt(rng.random())
        x0, y0 = C.x + rr * cos(a), C.y + rr * sin(a)
        zb = L.NOODLE_POT.z + 0.22
        ctrl = [V((x0, y0, C.z - 0.07)), V((x0 + rng.uniform(-0.01, 0.01), y0 + rng.uniform(-0.01, 0.01), C.z - 0.11)),
                V((x0 + rng.uniform(-0.02, 0.02), y0 + rng.uniform(-0.02, 0.02), (C.z + zb) / 2 - 0.02)),
                V((x0 + rng.uniform(-0.03, 0.03), y0 + rng.uniform(-0.03, 0.03), zb))]
        add_bm(nb, wire(ctrl, 0.0036, sides=6, n=22, per=6))
    make("Tebo_Noodles", nb, P['noodle'], parent=g)
    # handle: steel neck + wood grip
    S, D = L.TEBO_S, L.TEBO_DIR
    neck = wire([C + (S - C) * 0.9, S + D * 0.14], 0.009, sides=8, n=10)
    make("Tebo_Neck", neck, P['steel'], parent=g)
    grip = cyl(0.0195, 0.0195, L.TEBO_LEN - 0.14, segs=14)
    make("Tebo_Grip", grip, P['bamboo'], loc=S + D * 0.14, rot=rot_to(D), parent=g)
    make("Tebo_Cap", sphere(0.0195, 0.0195, 0.0195, u=14, v=8), P['bamboo'], loc=S + D * L.TEBO_LEN, parent=g)


def build_ladle(root):
    g = group("Ladle", root)
    C = L.LADLE_C
    D = L.LADLE_DIR
    n = (V((0, 0, 1)) - D * D.z).normalized()
    rr = L.LADLE_R
    prof = []
    steps = 10
    for i in range(steps + 1):
        a = PI / 2 * i / steps
        prof.append((rr * sin(a), -rr * cos(a)))                       # outside, bottom pole to rim
    for i in range(steps + 1):
        a = PI / 2 * (steps - i) / steps
        prof.append(((rr - 0.004) * sin(a), -(rr - 0.004) * cos(a)))   # inside, rim to pole
    bm = lathe(prof, segs=32)
    make("Ladle_Cup", bm, P['steel'], loc=C, rot=rot_to(n), parent=g, sharp=50)
    # soup held in the cup
    sd = lathe([(rr * 0.93, -0.012), (rr * 0.5, -0.0075), (0.0, -0.006)], segs=28)
    make("Ladle_Soup", sd, P['milk'], loc=C + n * 0.0, rot=rot_to(n), parent=g)
    S = L.LADLE_S
    shaft = cyl(0.0115, 0.0115, 0.22, segs=10)
    make("Ladle_Shaft", shaft, P['steel'], loc=S - D * 0.02, rot=rot_to(D), parent=g)
    grip = cyl(0.0195, 0.0195, L.LADLE_LEN - 0.17, segs=14)
    make("Ladle_Grip", grip, P['wood_dark'], loc=S + D * 0.17, rot=rot_to(D), parent=g)
    make("Ladle_Cap", sphere(0.0195, 0.0195, 0.0195, u=14, v=8), P['wood_dark'], loc=S + D * L.LADLE_LEN, parent=g)


def build_knife_and_board(root):
    g = group("Chopping", root)
    B = L.BOARD
    make("Board", box(0.58, 0.34, 0.04, 0.008), P['wood_light'], loc=(B.x, B.y, B.z + 0.02), parent=g, sharp=30)
    make("Board_Groove", box(0.5, 0.26, 0.002, 0.0005, 1), P['wood_handle'], loc=(B.x, B.y, B.z + 0.041), parent=g)
    # knife (local frame = KNIFE_M)
    kn = group("Knife", g)
    kn.matrix_world = L.KNIFE_M
    blade = box(0.20, 0.004, 0.092, 0.002, 1)
    for v in blade.verts:
        v.co.z += 0.046
        if v.co.x > 0.08 and v.co.z > 0.06:
            v.co.z -= 0.012
    make("Knife_Blade", blade, P['knife'], parent=kn, sharp=30)
    make("Knife_Spine", box(0.2, 0.0085, 0.01, 0.0025, 1), P['knife'], loc=(0, 0, 0.088), parent=kn, sharp=30)
    make("Knife_Hole", cyl(0.007, 0.007, 0.0046, segs=12), P['white'], loc=(-0.07, 0.0, 0.06), rot=(PI / 2, 0, 0), parent=kn) if False else None
    make("Knife_Ferrule", cyl(0.0155, 0.0155, 0.02, segs=14), P['steel'], loc=(0.10, 0, 0.06), rot=(0, PI / 2, 0), parent=kn)
    make("Knife_Handle", cyl(0.0145, 0.0145, 0.15, segs=14), P['wood_dark'], loc=(0.12, 0, 0.06), rot=(0, PI / 2, 0), parent=kn)
    make("Knife_HandleCap", sphere(0.0145, 0.0145, 0.0145, u=14, v=8), P['wood_dark'], loc=(0.27, 0, 0.06), parent=kn)
    # scallions: sliced rounds left of the blade and whole stalks behind
    rng = random.Random(5)
    bm = bmesh.new()
    for i in range(46):
        x = B.x - 0.255 + rng.random() * 0.12 + (0.03 if i % 5 == 0 else 0)
        y = B.y + rng.uniform(-0.1, 0.1)
        z = B.z + 0.044 + rng.random() * 0.006
        t = torus(0.0062, 0.0026, segs=12, sides=5)
        add_bm(bm, t, Matrix.Translation((x, y, z)) @ Euler((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5),
                                                              rng.uniform(0, 3)), 'XYZ').to_matrix().to_4x4(),
               matidx=0)
    make("Scallion_Rounds", bm, P['scallion'], parent=g)
    for k in range(3):
        y = B.y + 0.10 + 0.0 + k * 0.0
        x0 = B.x + 0.04 + k * 0.035
        p0 = V((x0, B.y + 0.13 - k * 0.012, B.z + 0.052))
        p1 = V((x0 + 0.17, B.y + 0.095 - k * 0.006, B.z + 0.05))
        bm = wire([p0, p0.lerp(p1, 0.5), p1], 0.0085 - k * 0.0006, sides=8, n=16)
        make(f"Scallion_Stalk_{k}", bm, P['scallion'], parent=g)
        w = wire([p0 - V((0.07, 0, 0)), p0 + V((0.01, 0, 0))], 0.0085 - k * 0.0006, sides=8, n=8)
        make(f"Scallion_Stalk_Base_{k}", w, P['scallion_w'], parent=g)


# ----------------------------------------------------------------------------- ramen bowl
def ztop(x, y, zb, R=0.105, H=0.032):
    rr = sqrt(x * x + y * y)
    return zb + 0.003 + H * max(0.0, 1 - (rr / R) ** 2)


def build_bowl(name, parent, loc, rot=(0, 0, 0), seed=0, scale=1.0, noodle_rot=20):
    g = group(name, parent, loc=tuple(loc))
    g.rotation_euler = rot
    g.scale = (scale, scale, scale)
    rng = random.Random(seed)
    prof = [(0.0, 0.012), (0.046, 0.012), (0.048, 0.0), (0.060, 0.0), (0.063, 0.012), (0.09, 0.040), (0.112, 0.075),
            (0.125, 0.105), (0.1272, 0.1135), (0.1255, 0.1175), (0.122, 0.1185), (0.119, 0.1165), (0.118, 0.112),
            (0.108, 0.075), (0.082, 0.040), (0.05, 0.022), (0.0, 0.017)]
    midx = [0] * 7 + [1] * 10
    bm = lathe(prof, segs=48, matidx=midx)
    make(f"{name}_Bowl", bm, [P['bowl_red'], P['bowl_cream']], parent=g, sharp=35)
    # decorative cream bands on the outside
    for zz, rr in ((0.080, 0.1145), (0.093, 0.1195)):
        make(f"{name}_Band", torus(rr + 0.0004, 0.0028, segs=48, sides=6), P['bowl_cream'], loc=(0, 0, zz), parent=g)
    zb = 0.090
    pb = [(0.1115, zb - 0.0025), (0.10, zb - 0.0005), (0.05, zb + 0.0015), (0.0, zb + 0.002)]
    make(f"{name}_Broth", lathe(pb, segs=48), P['broth'], parent=g)
    # oil droplets
    obm = bmesh.new()
    for i in range(16):
        a = rng.random() * 2 * PI
        rr = 0.098 * sqrt(rng.random())
        if rr < 0.045:
            continue
        r_ = rng.uniform(0.004, 0.011)
        add_bm(obm, cyl(r_, r_, 0.0008, segs=10), Matrix.Translation((rr * cos(a), rr * sin(a), zb + 0.0014)))
    make(f"{name}_Oil", obm, P['oil'], parent=g)
    # noodles
    nb = noodle_mound(zb, 0.098, 0.030, 26, seed + 3, rot_deg=noodle_rot)
    make(f"{name}_Noodles", nb, P['noodle'], parent=g)

    # toppings, one mesh with several materials
    T = bmesh.new()
    MI = {'chashu_edge': 0, 'chashu_face': 1, 'egg_white': 2, 'yolk': 3, 'nori': 4, 'naruto_w': 5, 'naruto_p': 6,
          'scallion': 7, 'menma': 8}

    def place(bm_src, pos, rot_e, matidx):
        M = Matrix.Translation(pos) @ Euler(rot_e, 'XYZ').to_matrix().to_4x4()
        add_bm(T, bm_src, M, matidx=matidx)

    # chashu slices leaning on the left/back
    for (cx, cy, tilt, yaw) in ((-0.052, 0.030, 24, 0.5), (-0.022, 0.058, 20, 0.2)):
        pos = V((cx, cy, ztop(cx, cy, zb) + 0.012))
        e = (radians(-tilt), radians(tilt * 0.5), yaw)
        d = cyl(0.044, 0.044, 0.0075, segs=26)
        for v in d.verts:
            v.co.y *= 0.82
        place(d, pos, e, MI['chashu_edge'])
        d2 = cyl(0.036, 0.036, 0.0008, segs=26)
        for v in d2.verts:
            v.co.y *= 0.8
        place(d2, pos + V((0, 0, 0)), e, MI['chashu_face']) if False else None
        d2 = cyl(0.035, 0.035, 0.0012, segs=26)
        for v in d2.verts:
            v.co.y *= 0.8
        # offset along local +Z of the slice
        zax = (Euler(e, 'XYZ').to_matrix() @ V((0, 0, 1)))
        place(d2, pos + zax * 0.0070, e, MI['chashu_face'])
        # fat swirl ring
        sw = torus(0.016, 0.0016, segs=20, sides=5)
        for v in sw.verts:
            v.co.y *= 0.8
        place(sw, pos + zax * 0.0085, e, MI['egg_white'])
    # soft-boiled egg halves
    for k, (ex, ey, yaw) in enumerate(((0.056, 0.012, 0.3), (0.066, -0.040, -0.4))):
        pos = V((ex, ey, ztop(ex, ey, zb) + 0.008))
        e = (radians(-28), radians(8), yaw)
        half = sphere(0.032, 0.023, 0.020, u=18, v=12)
        for v in half.verts:
            v.co.z = min(v.co.z, 0.0)
        place(half, pos, e, MI['egg_white'])
        yk = sphere(0.0135, 0.0105, 0.0085, u=14, v=8)
        for v in yk.verts:
            v.co.z = max(v.co.z, 0.0)
        place(yk, pos + Euler(e, 'XYZ').to_matrix() @ V((0, 0, 0.0004)), e, MI['yolk'])
    # nori standing at the back
    nr = box(0.082, 0.0015, 0.095, 0.0004, 1)
    for v in nr.verts:
        v.co.z += 0.0475
        v.co.x += 0.0004 * sin(v.co.x * 90) * 3
    place(nr, V((0.012, 0.088, zb - 0.002)), (radians(-14), 0, radians(4)), MI['nori'])
    nr2 = box(0.07, 0.0015, 0.085, 0.0004, 1)
    for v in nr2.verts:
        v.co.z += 0.0425
    place(nr2, V((-0.058, 0.082, zb - 0.002)), (radians(-10), 0, radians(-28)), MI['nori'])
    # narutomaki
    nd = cyl(0.029, 0.029, 0.0048, segs=30)
    for v in nd.verts:
        th = math.atan2(v.co.y, v.co.x)
        f = 1 + 0.07 * cos(9 * th)
        v.co.x *= f
        v.co.y *= f
    pos = V((-0.060, -0.052, ztop(-0.06, -0.052, zb) + 0.010))
    e = (radians(38), radians(-12), 0.4)
    place(nd, pos, e, MI['naruto_w'])
    zax = Euler(e, 'XYZ').to_matrix() @ V((0, 0, 1))
    sp = [V((0.0035 * (1 + 3.2 * f) * cos(f * 5.2 * PI), 0.0035 * (1 + 3.2 * f) * sin(f * 5.2 * PI), 0.0)) for f in
          [i / 30 for i in range(31)]]
    sp = [V((p.x, p.y, 0.0)) for p in sp]
    swirl = wire(sp, 0.0017, sides=5, n=60, per=4)
    place(swirl, pos + zax * 0.0052, e, MI['naruto_p'])
    # scallion rounds scattered in the centre
    for i in range(30):
        a = rng.random() * 2 * PI
        rr = 0.034 * sqrt(rng.random())
        x, y = rr * cos(a) + 0.006, rr * sin(a) - 0.004
        t = torus(0.0055, 0.0022, segs=10, sides=5)
        place(t, V((x, y, ztop(x, y, zb) + 0.004)), (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 3)),
              MI['scallion'])
    # menma strips
    for i in range(6):
        x = -0.015 + i * 0.011 + rng.uniform(-0.003, 0.003)
        y = -0.075 + rng.uniform(-0.006, 0.006)
        b = box(0.026, 0.0058, 0.0042, 0.001, 1)
        place(b, V((x, y, ztop(x, y, zb) + 0.003)), (0, rng.uniform(-0.2, 0.2), rng.uniform(-0.5, 0.5)), MI['menma'])
    make(f"{name}_Toppings", T, [P['chashu_edge'], P['chashu_face'], P['egg_white'], P['yolk'], P['nori'], P['naruto_w'],
                                 P['naruto_p'], P['scallion'], P['menma']], parent=g, sharp=40)
    return g


def build_chopsticks(name, parent, a, b, spacing=0.016, tilt=0.0, z=0.0):
    g = group(name, parent)
    a = V(a)
    b = V(b)
    d = (b - a).normalized()
    side = d.cross(V((0, 0, 1))).normalized()
    for k, s in enumerate((-1, 1)):
        off = side * (spacing * 0.5 * s)
        bm = wire([a + off, a.lerp(b, 0.5) + off, b + off], 0.0042, sides=6, n=22)
        make(f"{name}_{k}", bm, P['wood_dark'] if False else P['wood_handle'], parent=g)
    return g


# ----------------------------------------------------------------------------- counter dressing
def build_condiments(root):
    g = group("Condiments", root)
    base = V((0.34, -0.80, L.COUNTER_TOP))
    # tray
    make("Tray", box(0.36, 0.16, 0.012, 0.004), P['wood_dark'], loc=base + V((0, 0, 0.006)), parent=g, sharp=30)
    # soy sauce bottle
    prof = [(0.0, 0.0), (0.028, 0.0), (0.034, 0.01), (0.034, 0.085), (0.026, 0.115), (0.011, 0.14), (0.011, 0.16),
            (0.0, 0.16)]
    pr = prof_smooth(prof, 30, 6)
    pr[0] = (0, pr[0][1])
    pr[-1] = (0, pr[-1][1])
    make("Soy_Bottle", lathe(pr, segs=24), P['glass_dark'], loc=base + V((-0.12, 0, 0.012)), parent=g)
    make("Soy_Cap", cyl(0.014, 0.012, 0.025, segs=14), P['glass_red'], loc=base + V((-0.12, 0, 0.012 + 0.16)), parent=g)
    make("Soy_Label", cyl(0.0345, 0.0345, 0.04, segs=24), P['paper'], loc=base + V((-0.12, 0, 0.012 + 0.04)), parent=g)
    # chili oil jar
    make("Chili_Jar", cyl(0.036, 0.036, 0.075, segs=22), P['glass_red'], loc=base + V((-0.04, 0, 0.012)), parent=g)
    make("Chili_Lid", cyl(0.038, 0.038, 0.016, segs=22), P['black'], loc=base + V((-0.04, 0, 0.012 + 0.075)), parent=g)
    # pepper shaker + salt
    for k, x in enumerate((0.03, 0.075)):
        make(f"Shaker_{k}", cyl(0.02, 0.018, 0.07, segs=16), P['white'], loc=base + V((x, 0, 0.012)), parent=g)
        make(f"Shaker_Cap_{k}", cyl(0.0185, 0.012, 0.018, segs=16), P['steel'], loc=base + V((x, 0, 0.012 + 0.07)), parent=g)
    # toothpick holder / chopstick cup
    make("Chopstick_Cup", cyl(0.032, 0.036, 0.085, segs=20), P['jar_brown'], loc=base + V((0.14, 0, 0.012)), parent=g)
    rng = random.Random(3)
    for k in range(9):
        a = rng.uniform(0, 2 * PI)
        r = 0.016 * sqrt(rng.random())
        tilt = V((rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), 1)).normalized()
        p0 = base + V((0.14 + r * cos(a), r * sin(a), 0.012 + 0.05))
        bm = wire([p0, p0 + tilt * 0.17], 0.0038, sides=6, n=10)
        make(f"Cup_Chopstick_{k}", bm, P['wood_handle'], parent=g)


def build_pitcher(root):
    g = group("Pitcher", root)
    base = V((-1.40, -0.40, L.COUNTER_TOP))
    prof = [(0.0, 0.0), (0.07, 0.0), (0.078, 0.02), (0.078, 0.16), (0.07, 0.2), (0.0, 0.2)]
    pr = prof_smooth(prof, 20, 6)
    pr[0] = (0, pr[0][1])
    pr[-1] = (0, pr[-1][1])
    make("Pitcher_Body", lathe(pr, segs=28), P['steel'], loc=base, parent=g)
    pts = [V((0.074, 0, 0.17)), V((0.12, 0, 0.17)), V((0.13, 0, 0.09)), V((0.078, 0, 0.04))]
    make("Pitcher_Handle", wire(pts, 0.01, sides=8, n=24), P['steel'], loc=base, parent=g)
    for k, (dx, dy) in enumerate(((0.16, -0.12), (0.26, -0.06), (0.2, -0.20))):
        c = base + V((dx, dy, 0))
        make(f"Cup_{k}", cyl(0.032, 0.04, 0.062, segs=20), P['white'], loc=c, parent=g)
        make(f"Cup_Water_{k}", cyl(0.036, 0.036, 0.002, segs=20), P['water'], loc=c + V((0, 0, 0.052)), parent=g)


# ----------------------------------------------------------------------------- back shelves
def bowl_stack(name, parent, loc, n=5, scale=0.7):
    g = group(name, parent, loc=tuple(loc))
    prof = [(0.0, 0.0), (0.05, 0.0), (0.06, 0.012), (0.09, 0.04), (0.11, 0.075), (0.1255, 0.105), (0.1272, 0.1135),
            (0.1255, 0.1175), (0.119, 0.1165), (0.117, 0.108), (0.1, 0.06), (0.06, 0.02), (0.0, 0.015)]
    for i in range(n):
        bm = lathe(prof, segs=32, matidx=[0] * 7 + [1] * 6)
        make(f"{name}_{i}", bm, [P['bowl_red'], P['bowl_cream']], loc=(0, 0, 0.034 * i * scale + 0.0), parent=g,
             scale=(scale, scale, scale), sharp=35)
    return g


def jar(name, parent, loc, r, h, mat_body, mat_lid):
    g = group(name, parent, loc=tuple(loc))
    prof = [(0.0, 0.0), (r * 0.9, 0.0), (r, 0.01), (r, h * 0.8), (r * 0.7, h * 0.95), (r * 0.65, h), (0.0, h)]
    pr = prof_smooth(prof, 24, 6)
    pr[0] = (0, pr[0][1])
    pr[-1] = (0, pr[-1][1])
    make(f"{name}_Body", lathe(pr, segs=24), mat_body, parent=g)
    make(f"{name}_Lid", cyl(r * 0.72, r * 0.72, 0.03, segs=20), mat_lid, loc=(0, 0, h), parent=g)
    return g


def build_shelves(root):
    g = group("Shelves", root)
    # left shelf above the stove
    make("Shelf_L", box(1.15, 0.26, 0.035, 0.006), P['wood_dark'], loc=(-1.0, 1.0, 2.25), parent=g, sharp=30)
    for x in (-1.5, -0.5):
        make("Shelf_Bracket", box(0.03, 0.2, 0.2, 0.004), P['wood_dark'], loc=(x, 1.0, 2.15), parent=g, sharp=30)
    bowl_stack("Bowl_Stack_L", g, (-1.3, 1.0, 2.2675), n=5, scale=0.62)
    jar("Jar_1", g, (-0.95, 1.0, 2.2675), 0.075, 0.2, P['jar'], P['wood_handle'])
    jar("Jar_2", g, (-0.72, 1.0, 2.2675), 0.06, 0.15, P['jar_brown'], P['wood_dark'])
    # right shelf
    make("Shelf_R", box(0.9, 0.26, 0.035, 0.006), P['wood_dark'], loc=(1.0, 1.0, 1.7), parent=g, sharp=30)
    for x in (0.6, 1.4):
        make("Shelf_Bracket", box(0.03, 0.2, 0.2, 0.004), P['wood_dark'], loc=(x, 1.0, 1.6), parent=g, sharp=30)
    bowl_stack("Bowl_Stack_R", g, (1.25, 1.0, 1.7175), n=6, scale=0.62)
    jar("Jar_3", g, (0.8, 1.0, 1.7175), 0.07, 0.17, P['jar_brown'], P['wood_dark'])
    jar("Jar_4", g, (1.0, 1.0, 1.7175), 0.05, 0.13, P['jar'], P['wood_handle'])
    # hanging utensil rail
    make("Rail", cyl(0.012, 0.012, 1.0, segs=10), P['steel_dark'], loc=(-1.5, 1.07, 2.0), rot=(0, PI / 2, 0), parent=g)
    for k, x in enumerate((-1.3, -1.12, -0.95, -0.78)):
        make(f"Hang_Ladle_{k}", wire([V((x, 1.06, 2.0)), V((x, 1.06, 1.78)), V((x + 0.005, 1.06, 1.62))], 0.007, sides=6, n=16),
             P['steel'], parent=g)
        make(f"Hang_Cup_{k}", sphere(0.04, 0.012, 0.045, u=12, v=8) if k % 2 == 0 else cyl(0.035, 0.035, 0.012, segs=16),
             P['steel'], loc=(x + 0.005, 1.06, 1.60), parent=g)


def build_bulb(root):
    g = group("Lamp", root)
    make("Lamp_Cord", cyl(0.004, 0.004, 0.25, segs=6), P['black'], loc=(0, 0.05, 2.72), parent=g)
    prof = [(0.0, 0.0), (0.05, 0.0), (0.12, 0.05), (0.13, 0.065), (0.04, 0.09), (0.0, 0.1)]
    prof = [(0.025, 0.1), (0.05, 0.085), (0.115, 0.03), (0.13, 0.0), (0.12, 0.0), (0.105, 0.02), (0.045, 0.07), (0.02, 0.09)]
    make("Lamp_Shade", lathe(prof, segs=28), P['lantern_cap'], loc=(0, 0.05, 2.66), parent=g)
    make("Lamp_Bulb", sphere(0.05, 0.05, 0.055, u=18, v=12), P['bulb'], loc=(0, 0.05, 2.65), parent=g)


# ----------------------------------------------------------------------------- steam
def steam(name, parent, base, height=0.5, seed=0, count=3, spread=0.06, w=0.04):
    """Soft cartoon steam: columns of translucent puffs drifting up in a lazy S-curve."""
    g = group(name, parent)
    rng = random.Random(seed)
    for k in range(count):
        ox, oy = rng.uniform(-spread, spread), rng.uniform(-spread, spread)
        ph = rng.uniform(0, 2 * PI)
        amp = rng.uniform(0.03, 0.07)
        hh = height * rng.uniform(0.8, 1.1)
        bm_a, bm_b = bmesh.new(), bmesh.new()
        N = 7
        for i in range(N):
            t = i / (N - 1)
            c = V((base.x + ox + amp * sin(ph + t * 4.5) * t, base.y + oy + amp * 0.6 * cos(ph + t * 3.5) * t,
                   base.z + hh * t))
            r = (0.8 * w + w * 1.3 * t) * rng.uniform(0.8, 1.2)
            sp = sphere(r, r, r * 0.85, u=14, v=9)
            add_bm(bm_a if t < 0.5 else bm_b, sp, Matrix.Translation(c))
        make(f"{name}_{k}_a", bm_a, P['steam'], parent=g)
        make(f"{name}_{k}_b", bm_b, P['steam_hi'], parent=g)
    return g


def build_all(root, BM, OM):
    global P
    P = pm()
    build_stove(root)
    build_pot("Noodle_Pot", root, L.NOODLE_POT, L.NOODLE_POT_R, L.NOODLE_POT_H, 0.06, 0.06, P['water'], True, 2)
    build_pot("Stock_Pot", root, L.STOCK_POT, L.STOCK_POT_R, L.STOCK_POT_H, 0.07, 0.07, P['milk'], True, 4)
    build_tebo(root)
    build_ladle(root)
    build_knife_and_board(root)
    # the bowl presented by the octopus (tilted towards the guests)
    hb = build_bowl("Bowl_Held", root, L.HELD_BOWL, rot=(radians(18), 0, 0), seed=1, scale=1.2, noodle_rot=15)
    build_chopsticks("Held_Chopsticks", root, L.HELD_BOWL + V((-0.17, -0.03, 0.19)),
                     L.HELD_BOWL + V((0.17, 0.11, 0.18)))
    # customers' bowls on the counter
    build_bowl("Bowl_Customer_L", root, (-1.02, -0.62, L.COUNTER_TOP), rot=(0, 0, radians(20)), seed=7, scale=1.2, noodle_rot=70)
    build_chopsticks("Chopsticks_L", root, (-1.30, -0.80, L.COUNTER_TOP + 0.006), (-1.14, -0.52, L.COUNTER_TOP + 0.006))
    build_bowl("Bowl_Customer_R", root, (1.30, -0.76, L.COUNTER_TOP), rot=(0, 0, radians(-30)), seed=11, scale=1.2, noodle_rot=30)
    build_chopsticks("Chopsticks_R", root, (1.12, -0.90, L.COUNTER_TOP + 0.006), (1.14, -0.62, L.COUNTER_TOP + 0.006))
    build_condiments(root)
    build_pitcher(root)
    build_shelves(root)
    # steam
    steam("Steam_Noodle", root, L.NOODLE_POT + V((-0.08, 0.0, 0.31)), 0.45, 1, 2, 0.06, 0.035)
    steam("Steam_Stock", root, L.STOCK_POT + V((-0.04, 0.1, 0.47)), 0.5, 2, 2, 0.06, 0.04)
    steam("Steam_Held", root, L.HELD_BOWL + V((0, 0.0, 0.14)), 0.4, 3, 3, 0.05, 0.03)
    steam("Steam_CL", root, V((-1.02, -0.62, L.COUNTER_TOP + 0.13)), 0.35, 4, 3, 0.05, 0.028)
    steam("Steam_CR", root, V((1.31, -0.78, L.COUNTER_TOP + 0.13)), 0.35, 5, 2, 0.04, 0.026)
