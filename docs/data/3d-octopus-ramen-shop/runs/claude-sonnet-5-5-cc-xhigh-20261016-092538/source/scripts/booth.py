"""The ramen booth structure: floor, frame, roof, counter, walls, noren, lanterns, stools."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import layout as L

PI = pi
def V3(x, y, z):
    return Vector((x, y, z))


def mats():
    return {
        'wood_vc': mat('Wood_VC', '#ffffff', rough=0.7, vcol='Color'),
        'post': mat('Wood_Post', '#4a2a18', rough=0.65),
        'beam': mat('Wood_Beam', '#33190e', rough=0.6),
        'counter_top': mat('Counter_Top', '#b97d3d', rough=0.45, spec=0.5, coat=0.2),
        'counter_front': mat('Counter_Front', '#6e3a22', rough=0.6),
        'counter_trim': mat('Counter_Trim', '#3a1c10', rough=0.55),
        'roof': mat('Roof_Tile', '#2d3a52', rough=0.45, spec=0.6),
        'roof_rib': mat('Roof_Rib', '#3d4e6e', rough=0.4),
        'roof_cap': mat('Roof_Cap', '#1c2435', rough=0.4),
        'indigo': mat('Noren_Indigo', '#0e2257', rough=0.9),
        'cream': mat('Cream', '#f6ecd6', rough=0.7),
        'sign_dark': mat('Sign_Dark', '#24120b', rough=0.5, spec=0.5),
        'sign_text': mat('Sign_Text', '#fbeccd', rough=0.5),
        'lantern': mat('Lantern_Paper', '#e0331f', rough=0.6, emit='#ff3d12', emit_strength=3.0),
        'lantern_cap': mat('Lantern_Cap', '#16100c', rough=0.5),
        'lantern_rib': mat('Lantern_Rib', '#9e1c12', rough=0.6),
        'steel': mat('Steel', '#c4c9d1', rough=0.3, metal=0.7),
        'steel_dark': mat('Steel_Dark', '#4a4e57', rough=0.4, metal=0.9),
        'iron': mat('Iron', '#26282e', rough=0.5, metal=0.7),
        'stool': mat('Stool_Wood', '#a8703c', rough=0.6),
        'stool_pad': mat('Stool_Pad', '#b02a2e', rough=0.8),
        'stone_vc': mat('Stone_VC', '#ffffff', rough=0.85, vcol='Color'),
        'paper': mat('Paper', '#f4e8cc', rough=0.9),
        'ink': mat('Ink', '#7d1c14', rough=0.6),
        'bulb': mat('Bulb', '#fff2c8', rough=0.3, emit='#ffd27a', emit_strength=6.0),
        'bamboo': mat('Bamboo', '#b6a35a', rough=0.6),
        'rope': mat('Rope', '#c9b387', rough=0.9),
    }


def vc_wood(base_hex, var=0.12):
    base = hexc(base_hex)
    def fn(co, n):
        k = hash01(int(co.x * 7.3 + 100), int(co.y * 3.1 + 100), int(co.z * 5.9 + 100))
        f = 1 + (k - 0.5) * var * 2
        return (base[0] * f, base[1] * f, base[2] * f, 1)
    return fn


def build_floor(root, M):
    # cobbled street
    bm = bmesh.new()
    S = 0.6
    for ix in range(-5, 5):
        for iy in range(-4, 4):
            k = hash01(ix + 20, iy + 20)
            b = box(S - 0.035, S - 0.035, 0.14, 0.012, 2)
            add_bm(bm, b, Matrix.Translation((ix * S + S / 2, iy * S + S / 2 + 0.1, -0.07 - k * 0.006)))
    def fn(co, n):
        ix = math.floor(co.x / S)
        iy = math.floor((co.y - 0.1) / S)
        k = hash01(ix + 3, iy + 7)
        c = mixc(hexc('#232836'), hexc('#3a4254'), k)
        return c
    paint(bm, fn)
    make("Street_Tiles", bm, M['stone_vc'], parent=root, sharp=35)
    # wooden floor in the booth
    bm = bmesh.new()
    n = 15
    for i in range(n):
        w = 3.3 / n
        b = box(w - 0.006, 2.2, 0.06, 0.004, 1)
        add_bm(bm, b, Matrix.Translation((-1.65 + w * (i + 0.5), 0.1, 0.03)))
    paint(bm, vc_wood('#9a6a3e', 0.14))
    make("Booth_Floor", bm, M['wood_vc'], parent=root, sharp=35)


def build_frame(root, M):
    g = group("Booth_Frame", root)
    for sx in (-1, 1):
        for (y, name) in ((-0.98, 'F'), (1.08, 'B')):
            make(f"Post_{name}{'L' if sx < 0 else 'R'}", box(0.13, 0.13, 2.95, 0.012), M['post'],
                 loc=(sx * 1.6, y, 2.95 / 2 + 0.03), parent=g, sharp=30)
    # front fascia (sign board) + back/side beams
    make("Fascia", box(3.9, 0.10, 0.28, 0.012), M['sign_dark'], loc=(0, -1.04, 3.09), parent=g, sharp=30)
    make("Fascia_Trim_Top", box(3.94, 0.13, 0.03, 0.008), M['beam'], loc=(0, -1.04, 3.235), parent=g, sharp=30)
    make("Fascia_Trim_Bot", box(3.94, 0.13, 0.03, 0.008), M['beam'], loc=(0, -1.04, 2.945), parent=g, sharp=30)
    for sx in (-1, 1):
        make(f"Beam_Side_{'L' if sx < 0 else 'R'}", box(0.12, 2.2, 0.14, 0.01), M['beam'], loc=(sx * 1.6, 0.05, 2.88),
             parent=g, sharp=30)
    make("Beam_Back", box(3.3, 0.12, 0.14, 0.01), M['beam'], loc=(0, 1.08, 2.88), parent=g, sharp=30)
    # ceiling boards
    bm = bmesh.new()
    for i in range(11):
        w = 3.5 / 11
        add_bm(bm, box(w - 0.01, 2.5, 0.04, 0.004, 1), Matrix.Translation((-1.75 + w * (i + 0.5), 0.1, 2.97)))
    paint(bm, vc_wood('#6b4226', 0.12))
    make("Ceiling", bm, M['wood_vc'], parent=g, sharp=30)
    # rafters
    for i in range(7):
        x = -1.7 + i * 0.5667
        make(f"Rafter_{i}", box(0.07, 2.4, 0.07, 0.006), M['beam'], loc=(x, 0.1, 2.925), parent=g, sharp=30)
    # roof: two slabs with ribs
    th = math.atan2(0.42, 1.3)
    ln = sqrt(0.42 ** 2 + 1.3 ** 2)
    for side, (y0, y1, rot) in {'F': (-1.2, 0.1, th), 'B': (1.4, 0.1, -th)}.items():
        ym, zm = (y0 + y1) / 2, (3.2 + 3.62) / 2 + 0.035
        make(f"Roof_{side}", box(4.0, ln + 0.08, 0.07, 0.01), M['roof'], loc=(0, ym, zm), rot=(rot, 0, 0), parent=g, sharp=30)
        bm = bmesh.new()
        for i in range(19):
            x = -1.8 + i * 0.2
            add_bm(bm, box(0.07, ln + 0.1, 0.035, 0.008, 1), Matrix.Translation((x, 0, 0.045)))
        make(f"Roof_Ribs_{side}", bm, M['roof_rib'], loc=(0, ym, zm), rot=(rot, 0, 0), parent=g, sharp=30)
        # eave edge board
        make(f"Roof_Edge_{side}", box(4.04, 0.04, 0.12, 0.008), M['roof_cap'],
             loc=(0, y0 - (0.02 if side == 'F' else -0.02) * 0, 3.2 + 0.02), rot=(rot, 0, 0), parent=g, sharp=30)
    cap = cyl(0.075, 0.075, 4.06, segs=14)
    make("Roof_Ridge", cap, M['roof_cap'], loc=(-2.03, 0.1, 3.65), rot=(0, PI / 2, 0), parent=g)
    # gable infill (triangles) left/right
    for sx in (-1, 1):
        bm = bmesh.new()
        pts = [(-1.3, 3.0), (1.5, 3.0), (0.1, 3.60)]
        vs = [bm.verts.new((0, y, z)) for (y, z) in pts]
        bm.faces.new(vs)
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.06)
        make(f"Gable_{'L' if sx < 0 else 'R'}", bm, M['beam'], loc=(sx * 1.75, 0, 0), parent=g, sharp=30)


def build_walls(root, M):
    g = group("Booth_Walls", root)
    # back wall of planks
    bm = bmesh.new()
    n = 17
    for i in range(n):
        w = 3.3 / n
        add_bm(bm, box(w - 0.008, 0.05, 2.9, 0.004, 1), Matrix.Translation((-1.65 + w * (i + 0.5), 1.14, 1.5)))
    paint(bm, vc_wood('#2b5566', 0.14))
    make("Back_Wall", bm, M['wood_vc'], parent=g, sharp=30)
    bm = bmesh.new()
    n = 17
    for i in range(n):
        w = 3.3 / n
        add_bm(bm, box(w - 0.008, 0.04, 2.9, 0.004, 1), Matrix.Translation((-1.65 + w * (i + 0.5), 1.185, 1.5)))
    paint(bm, vc_wood('#4d2f1c', 0.12))
    make("Back_Wall_Outer", bm, M['wood_vc'], parent=g, sharp=30)
    make("Back_Wall_Core", box(3.3, 0.04, 2.9), M['counter_trim'], loc=(0, 1.14, 1.5), parent=g, sharp=30)
    # side walls (horizontal boards)
    for sx in (-1, 1):
        make(f"Side_Wall_Core_{'L' if sx < 0 else 'R'}", box(0.04, 2.2, 2.9), M['counter_trim'], loc=(sx * 1.66, 0.05, 1.5),
             parent=g, sharp=30)
        bm = bmesh.new()
        n = 20
        for i in range(n):
            h = 2.9 / n
            add_bm(bm, box(0.05, 2.2, h - 0.008, 0.004, 1), Matrix.Translation((0, 0.05, 0.06 + h * (i + 0.5))))
        paint(bm, vc_wood('#4d2f1c', 0.12))
        make(f"Side_Wall_{'L' if sx < 0 else 'R'}", bm, M['wood_vc'], loc=(sx * 1.66, 0.0, 0), parent=g, sharp=30)


def build_counter(root, M):
    g = group("Counter", root)
    top_y0, top_y1 = -1.0, -0.18
    make("Counter_Top", box(3.3, top_y1 - top_y0, 0.065, 0.014, 3), M['counter_top'],
         loc=(0, (top_y0 + top_y1) / 2, L.COUNTER_TOP - 0.0325), parent=g, sharp=30)
    # front panel: vertical planks
    bm = bmesh.new()
    n = 20
    for i in range(n):
        w = 3.2 / n
        add_bm(bm, box(w - 0.01, 0.05, 0.86, 0.006, 1), Matrix.Translation((-1.6 + w * (i + 0.5), -0.93, 0.5)))
    paint(bm, vc_wood('#7a432a', 0.10))
    make("Counter_Front", bm, M['wood_vc'], parent=g, sharp=30)
    make("Counter_Rail_Top", box(3.3, 0.09, 0.07, 0.01), M['counter_trim'], loc=(0, -0.95, 0.93), parent=g, sharp=30)
    make("Counter_Rail_Bot", box(3.3, 0.09, 0.07, 0.01), M['counter_trim'], loc=(0, -0.95, 0.10), parent=g, sharp=30)
    make("Counter_Back", box(3.2, 0.04, 0.88, 0.006), M['counter_trim'], loc=(0, -0.2, 0.5), parent=g, sharp=30)
    make("Counter_Foot_Rail", cyl(0.025, 0.025, 3.1, segs=12), M['steel'], loc=(-1.55, -1.12, 0.22), rot=(0, PI / 2, 0), parent=g)
    for k, x in enumerate((-1.45, 0.0, 1.45)):
        make(f"Foot_Rail_Bracket_{k}", box(0.05, 0.17, 0.035, 0.006), M['steel'], loc=(x, -1.045, 0.22), parent=g, sharp=30)


def build_noren(root, M):
    g = group("Noren", root)
    rod = cyl(0.014, 0.014, 3.2, segs=10)
    make("Noren_Rod", rod, M['post'], loc=(-1.6, -1.12, 2.93), rot=(0, PI / 2, 0), parent=g)
    panels = [(-1.34, ), (-1.0, ), (-0.66, ), (0.66, ), (1.0, ), (1.34, )]
    W, H = 0.32, 0.36
    for k, (cx,) in enumerate(panels):
        nu, nv = 6, 12
        bm = bmesh.new()
        rows = []
        for j in range(nv + 1):
            z = -H * j / nv
            row = []
            for i in range(nu + 1):
                x = -W / 2 + W * i / nu
                y = 0.014 * sin((x / W * 2.0 + k * 0.7) * PI) * (0.4 + 0.6 * (j / nv)) - 0.012 * (j / nv) ** 2
                row.append(bm.verts.new((x, y, z)))
            rows.append(row)
        for j in range(nv):
            for i in range(nu):
                bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
        # flip so the front faces -Y
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
        ob = make(f"Noren_Panel_{k}", bm, M['indigo'], loc=(cx, -1.125, 2.925), parent=g)
        # white emblem: ring
        bm2 = torus(0.055, 0.007, segs=28, sides=6)
        make(f"Noren_Mark_{k}", bm2, M['cream'], loc=(cx, -1.147, 2.925 - 0.15), rot=(PI / 2, 0, 0), parent=g)
        bm3 = box(W * 0.98, 0.006, 0.022, 0.002, 1)
        make(f"Noren_Hem_{k}", bm3, M['cream'], loc=(cx, -1.125 - 0.012 - 0.003, 2.925 - H + 0.025), parent=g)


def build_signs(root, M):
    g = group("Signs", root)
    bm = text_bm("TAKO-YA  RAMEN", size=0.17, extrude=0.012, bevel=0.0)
    make("Sign_Text", bm, M['sign_text'], loc=(0, -1.098, 3.09), rot=(PI / 2, 0, 0), parent=g, smooth=False)
    # hanging bamboo menu paper tags on the back wall (right)
    tags = [("SHOYU  800", 2.52), ("MISO  900", 2.33), ("TONKOTSU  1000", 2.14)]
    for k, (txt, z) in enumerate(tags):
        rot = radians((-1) ** k * 1.5)
        make(f"Tag_{k}", box(0.62, 0.012, 0.15, 0.003, 1), M['paper'], loc=(1.17, 1.085, z), rot=(0, rot, 0), parent=g, sharp=30)
        bmt = text_bm(txt, size=0.065, extrude=0.003)
        make(f"Tag_Text_{k}", bmt, M['ink'], loc=(1.17, 1.077, z - 0.02), rot=(PI / 2, rot, 0), parent=g, smooth=False)


def build_lanterns(root, M):
    g = group("Lanterns", root)
    for sx in (-1, 1):
        x, y = sx * 1.80, -1.34
        # bracket arm
        make(f"Lantern_Arm_{'L' if sx < 0 else 'R'}", box(0.07, 0.34, 0.07, 0.008), M['beam'], loc=(x, -1.19, 3.1), parent=g, sharp=30)
        z0 = 2.62
        # paper body: bulged lathe
        prof = [(0.0, 0.0), (0.09, 0.0), (0.15, 0.04), (0.19, 0.12), (0.2, 0.2), (0.19, 0.28), (0.15, 0.36), (0.09, 0.4), (0.0, 0.4)]
        pts, _ = spline([(r, 0, z) for r, z in prof], 28, per=8)
        pr = [(max(p.x, 0.0), p.z) for p in pts]
        pr[0] = (0.0, pr[0][1])
        pr[-1] = (0.0, pr[-1][1])
        bm = lathe(pr, segs=32)
        make(f"Lantern_{'L' if sx < 0 else 'R'}", bm, M['lantern'], loc=(x, y, z0), parent=g)
        for k in range(7):
            zz = 0.06 + k * 0.047
            rr = (0.0 if False else 1)
            t = (zz / 0.4)
            rad = 0.2 * (1 - (2 * t - 1) ** 2 * 0.22) + 0.002
            make(f"Lantern_Rib_{k}", torus(rad, 0.0045, segs=32, sides=6), M['lantern_rib'],
                 loc=(x, y, z0 + zz + 0.0), parent=g)
        make("Lantern_Cap_T", cyl(0.1, 0.1, 0.05, segs=24), M['lantern_cap'], loc=(x, y, z0 + 0.4), parent=g)
        make("Lantern_Cap_B", cyl(0.1, 0.1, 0.05, segs=24), M['lantern_cap'], loc=(x, y, z0 - 0.05), parent=g)
        make("Lantern_Cord", cyl(0.006, 0.006, 0.08, segs=6), M['lantern_cap'], loc=(x, y, z0 + 0.45), parent=g)
        # stripe/label: cream band with text
        bt = text_bm("RAMEN", size=0.06, extrude=0.004)
        Rb = 0.2
        for v in bt.verts:
            th = v.co.x / Rb
            rr = Rb + v.co.z
            v.co.x = rr * sin(th)
            v.co.z = rr * cos(th) - Rb
        make("Lantern_Label", bt, M['lantern_cap'], loc=(x, y - 0.2, z0 + 0.2), rot=(PI / 2, 0, 0), parent=g, smooth=False)


def build_stools(root, M):
    g = group("Stools", root)
    for k, (x, y) in enumerate([(-1.05, -1.62), (0.95, -1.7)]):
        seat = cyl(0.23, 0.23, 0.06, segs=28)
        make(f"Stool_Seat_{k}", seat, M['stool'], loc=(x, y, 0.58), parent=g)
        make(f"Stool_Pad_{k}", cyl(0.2, 0.17, 0.06, segs=28), M['stool_pad'], loc=(x, y, 0.64), parent=g)
        for j in range(3):
            a = 2 * PI * j / 3 + 0.5
            top = Vector((x + 0.14 * cos(a), y + 0.14 * sin(a), 0.58))
            bot = Vector((x + 0.24 * cos(a), y + 0.24 * sin(a), 0.0))
            d = top - bot
            leg = cyl(0.026, 0.021, d.length, segs=10)
            make(f"Stool_Leg_{k}_{j}", leg, M['stool'], loc=bot, rot=rot_to(d), parent=g)
        make(f"Stool_Ring_{k}", torus(0.19, 0.012, segs=28, sides=6), M['stool'], loc=(x, y, 0.26), parent=g)


def build_aframe(root, M):
    g = group("AFrame_Sign", root, loc=(-2.15, -1.25, 0.0))
    g.rotation_euler = (0, 0, radians(-14))
    chalk = mat('Chalkboard', '#1b2b27', rough=0.85)
    chalk_txt = mat('Chalk', '#f4f1e4', rough=0.9)
    front = group("AFrame_Front", g)
    front.rotation_euler = (-radians(8), 0, 0)
    make("AFrame_Board", box(0.56, 0.03, 0.86, 0.008), M['stool'], loc=(0, 0, 0.43), parent=front, sharp=30)
    make("AFrame_Panel", box(0.46, 0.012, 0.68, 0.004), chalk, loc=(0, -0.018, 0.45), parent=front, sharp=30)
    for k, (txt, z, sz) in enumerate((("TODAY'S", 0.64, 0.055), ("SPECIAL", 0.57, 0.065), ("TAKO RAMEN", 0.45, 0.058),
                                      ("800 YEN", 0.115, 0.052))):
        bt = text_bm(txt, size=sz, extrude=0.002)
        make(f"AFrame_Text_{k}", bt, chalk_txt, loc=(0, -0.0245, z), rot=(PI / 2, 0, 0), parent=front, smooth=False)
    # little chalk octopus doodle: head + legs
    doodle = bmesh.new()
    add_bm(doodle, torus(0.045, 0.0035, segs=24, sides=5), Matrix.Translation((0, 0, 0.0)))
    for k in range(5):
        a = -0.8 + 0.4 * k
        pts = [V3(0.03 * (k - 2) * 0.7, -0.04, 0), V3(0.04 * (k - 2) + 0.01, -0.08, 0), V3(0.05 * (k - 2) - 0.012, -0.115, 0)]
        add_bm(doodle, wire(pts, 0.0035, sides=5, n=10, per=6))
    make("AFrame_Doodle", doodle, chalk_txt, loc=(0, -0.0245, 0.325), rot=(PI / 2, 0, 0), parent=front, smooth=False)
    back = group("AFrame_Back", g, loc=(0, 0.24, 0))
    back.rotation_euler = (radians(8), 0, 0)
    make("AFrame_BackBoard", box(0.56, 0.03, 0.86, 0.008), M['stool'], loc=(0, 0, 0.43), parent=back, sharp=30)
    make("AFrame_Chain", wire([V3(0.0, 0.02, 0.5), V3(0.0, 0.12, 0.42), V3(0.0, 0.2, 0.5)], 0.004, sides=5, n=10),
         M['steel'], parent=g)


def build_all(root, M):
    build_floor(root, M)
    build_frame(root, M)
    build_walls(root, M)
    build_counter(root, M)
    build_noren(root, M)
    build_signs(root, M)
    build_lanterns(root, M)
    build_stools(root, M)
    build_aframe(root, M)
