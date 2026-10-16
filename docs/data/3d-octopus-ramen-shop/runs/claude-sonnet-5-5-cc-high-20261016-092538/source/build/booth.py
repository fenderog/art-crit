TOP = 1.1          # counter top height
FLOOR = 0.12       # booth platform height

root = empty("RamenBooth")
booth = empty("Booth", parent=root)
props = empty("Props", parent=root)

# ---------- materials ----------
wood_dark = mat("WoodDark", (0.17, 0.085, 0.045), 0.65)
wood_mid = mat("WoodMid", (0.36, 0.19, 0.09), 0.55)
wood_light = mat("WoodLight", (0.62, 0.40, 0.20), 0.4)
wood_tint = [mat("WoodPlank%d" % i, c, 0.6) for i, c in enumerate(
    [(0.24, 0.12, 0.06), (0.20, 0.10, 0.05), (0.27, 0.14, 0.07), (0.22, 0.115, 0.06)])]
roof_m = mat("RoofTile", (0.10, 0.12, 0.18), 0.45)
red_m = mat("LacquerRed", (0.62, 0.05, 0.04), 0.35)
red_paper = mat("LanternRed", (0.8, 0.07, 0.04), 0.5, emit=(1.0, 0.18, 0.05), es=3.0)
black_m = mat("Black", (0.02, 0.02, 0.02), 0.5)
cream_m = mat("Cream", (0.93, 0.87, 0.72), 0.7)
white_m = mat("White", (0.95, 0.95, 0.93), 0.5)
indigo_m = mat("Indigo", (0.04, 0.07, 0.22), 0.9)
steel_m = mat("Steel", (0.8, 0.8, 0.83), 0.35, metal=0.55)
iron_m = mat("DarkIron", (0.07, 0.07, 0.08), 0.5, metal=0.6)
ground_m = mat("Cobble", (0.10, 0.11, 0.15), 0.9)
glow_m = mat("FireGlow", (1, 0.4, 0.05), 0.5, emit=(1.0, 0.35, 0.03), es=6.0)
steam_m = mat("Steam", (1, 1, 1), 1.0, alpha=0.13)

# ---------- ground & platform ----------
add("Street", bm_box(40, 40, 0.1), mat("Cobble", (0.06, 0.065, 0.09), 0.9), (0, 0, -0.04), parent=booth)
# cobble stones merged into 4 meshes
random.seed(4)
cob_bm = [bmesh.new() for _ in range(4)]
for ix in range(-12, 13):
    for iy in range(-9, 8):
        x = ix * 0.62 + (0.31 if iy % 2 else 0) + random.uniform(-0.02, 0.02)
        y = iy * 0.62 + random.uniform(-0.02, 0.02)
        if abs(x) < 3.1 and -1.9 < y < 2.4:
            continue
        s = bm_box(0.57, 0.57, 0.05)
        bm_xform(s, Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(random.uniform(-0.06, 0.06), 4, 'Z'))
        merge(cob_bm[random.randrange(4)], s)
cob_cols = [(0.11, 0.12, 0.17), (0.09, 0.10, 0.15), (0.13, 0.13, 0.18), (0.10, 0.11, 0.14)]
for i in range(4):
    add("Cobbles%d" % i, cob_bm[i], mat("Cob%d" % i, cob_cols[i], 0.85), parent=booth)

for i in range(11):
    add("FloorPlank%d" % i, bm_box(0.435, 3.6, FLOOR), wood_tint[i % 4], (-2.4 + i * 0.48, 0.1, FLOOR / 2),
        parent=booth)

# ---------- counter ----------
cw = 2.4
front = bm_box(2 * cw, 0.12, TOP - 0.06)
add("CounterFront", front, wood_dark, (0, -1.25, (TOP - 0.06) / 2), parent=booth)
for i in range(13):
    add("CounterSlat%d" % i, bm_box(0.05, 0.03, TOP - 0.2), wood_mid, (-2.2 + i * 0.3667, -1.325, (TOP - 0.06) / 2),
        parent=booth)
add("CounterBack", bm_box(2 * cw, 0.1, TOP - 0.06), wood_dark, (0, -0.65, (TOP - 0.06) / 2), parent=booth)
add("CounterTop", bm_box(2 * cw + 0.2, 0.95, 0.07), wood_light, (0, -0.93, TOP - 0.035), parent=booth)
add("CounterLip", bm_box(2 * cw + 0.2, 0.05, 0.1), wood_mid, (0, -1.42, TOP - 0.06), parent=booth)
add("CounterRail", bm_box(2 * cw, 0.08, 0.06), black_m, (0, -1.31, 0.35), parent=booth)

# ---------- posts, roof ----------
PH = 4.4
for sx in (-1, 1):
    for sy in (-1, 1):
        add("Post_%d_%d" % (sx, sy), bm_box(0.16, 0.16, PH), wood_dark, (sx * 2.4, sy * 1.5 + (0.1 if sy > 0 else 0), PH / 2),
            parent=booth)
add("BeamFront", bm_box(5.1, 0.18, 0.2), wood_mid, (0, -1.5, PH - 0.12), parent=booth)
add("BeamBack", bm_box(5.1, 0.18, 0.2), wood_mid, (0, 1.6, PH - 0.12), parent=booth)
for i in range(7):
    add("RafterB%d" % i, bm_box(0.1, 3.3, 0.12), wood_mid, (-2.4 + i * 0.8, 0.05, PH - 0.02), parent=booth)
add("Ceiling", bm_box(5.4, 3.5, 0.05), wood_dark, (0, 0.05, PH + 0.04), parent=booth)
roof = empty("Roof", (0, 0.05, PH + 0.1), (math.radians(-6), 0, 0), parent=booth)
add("RoofSlab", bm_box(5.7, 3.8, 0.1), roof_m, (0, 0, 0.05), parent=roof)
for i in range(30):
    bm = bm_cyl(0.08, 0.08, 3.8, 10)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
    add("RoofRidge%d" % i, bm, roof_m, (-2.75 + i * 0.19, 0, 0.12), parent=roof, smooth=True)
add("RoofEdge", bm_box(5.8, 0.1, 0.22), mat("RoofEdge", (0.07, 0.08, 0.12), 0.5), (0, -1.9, 0.03), parent=roof)

# fascia sign
add("SignBoard", bm_box(3.3, 0.1, 0.5), red_m, (0, -1.85, 4.3), parent=booth)
add("SignFrame", bm_box(3.45, 0.08, 0.6), black_m, (0, -1.83, 4.3), parent=booth)
cu = bpy.data.curves.new("RamenText", 'FONT')
cu.body = "RAMEN"
cu.size = 0.34
cu.extrude = 0.025
cu.align_x = 'CENTER'
cu.align_y = 'CENTER'
cu.space_character = 1.3
tobj = bpy.data.objects.new("tmp", cu)
bpy.context.scene.collection.objects.link(tobj)
tme = bpy.data.meshes.new_from_object(tobj)
bpy.data.objects.remove(tobj)
bpy.data.curves.remove(cu)
tme.materials.append(white_m)
txt = bpy.data.objects.new("SignText", tme)
txt.location = (0, -1.9, 4.3)
txt.rotation_euler = (math.pi / 2, 0, 0)
bpy.context.scene.collection.objects.link(txt)
txt.parent = booth

# noren curtains
add("NorenRod", bm_cyl(0.025, 0.025, 4.9, 10), wood_light, (0, -1.6, 4.1), rot=(0, math.pi / 2, 0), parent=booth)
for i in range(6):
    x = -1.75 + i * 0.7
    g = empty("Noren%d" % i, (x, -1.6, 4.08), (math.radians(random.uniform(-3, 3)), 0, math.radians(random.uniform(-2, 2))),
              parent=booth)
    add("NorenCloth%d" % i, bm_box(0.62, 0.015, 0.55), indigo_m, (0, 0, -0.275), parent=g)
    disc = bm_cyl(0.13, 0.13, 0.012, 24)
    bmesh.ops.rotate(disc, verts=disc.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
    add("NorenMark%d" % i, disc, white_m, (0, -0.012, -0.26), parent=g)
    dot = bm_cyl(0.07, 0.07, 0.014, 24)
    bmesh.ops.rotate(dot, verts=dot.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
    add("NorenDot%d" % i, dot, red_m, (0, -0.014, -0.26), parent=g)

# ---------- back wall ----------
for i in range(12):
    add("WallPlank%d" % i, bm_box(0.42, 0.08, PH), wood_tint[i % 4], (-2.3 + i * 0.418, 1.7, PH / 2), parent=booth)
add("WallBatten", bm_box(5.0, 0.04, 0.1), wood_mid, (0, 1.64, 1.9), parent=booth)
add("WallBatten2", bm_box(5.0, 0.04, 0.1), wood_mid, (0, 1.64, 3.1), parent=booth)
# shelf with jars & bowls
add("Shelf", bm_box(3.4, 0.4, 0.06), wood_light, (-0.2, 1.45, 2.05), parent=booth)
jar_cols = [(0.5, 0.2, 0.1), (0.15, 0.3, 0.2), (0.8, 0.7, 0.5), (0.35, 0.1, 0.1), (0.1, 0.2, 0.35)]
for i in range(9):
    x = -1.7 + i * 0.4
    h = 0.22 + (i % 3) * 0.06
    add("Jar%d" % i, bm_cyl(0.095, 0.085, h, 16), mat("Jar%d" % (i % 5), jar_cols[i % 5], 0.3), (x, 1.45, 2.08 + h / 2),
        parent=props, smooth=True)
    add("JarLid%d" % i, bm_cyl(0.075, 0.075, 0.04, 16), black_m, (x, 1.45, 2.08 + h + 0.02), parent=props)
# stack of bowls on the shelf
for i in range(4):
    add("ShelfBowl%d" % i, bm_cyl(0.16, 0.1, 0.1, 20), white_m, (1.6, 1.45, 2.14 + i * 0.07), parent=props, smooth=True)

# hanging menu tags
for i in range(7):
    x = -1.5 + i * 0.5
    add("MenuTag%d" % i, bm_box(0.2, 0.025, 0.7), cream_m, (x, 1.6, 3.2), parent=props)
    add("MenuFrame%d" % i, bm_box(0.23, 0.02, 0.73), wood_dark, (x, 1.615, 3.2), parent=props)
    for k in range(3):
        add("MenuMark%d_%d" % (i, k), bm_box(0.11 - 0.015 * k, 0.01, 0.07), mat("Ink", (0.04, 0.03, 0.03), 0.8),
            (x, 1.585, 3.4 - k * 0.17), parent=props)

# ---------- lanterns ----------
for sx in (-1, 1):
    g = empty("Lantern_%d" % sx, (sx * 2.15, -1.75, 3.25), parent=booth)
    add("LanternBody", bm_sphere(0.3, 24, 16, (1, 1, 1.25)), red_paper, (0, 0, 0), parent=g, smooth=True)
    add("LanternTop", bm_cyl(0.13, 0.13, 0.06, 16), black_m, (0, 0, 0.37), parent=g)
    add("LanternBot", bm_cyl(0.13, 0.13, 0.06, 16), black_m, (0, 0, -0.37), parent=g)
    add("LanternCord", bm_cyl(0.008, 0.008, 0.5, 6), black_m, (0, 0, 0.65), parent=g)
    for k in (-1, 0, 1):
        ring = bm_torus(0.3 * math.sqrt(1 - (k * 0.19 / 0.375) ** 2), 0.007, 32, 6)
        add("LanternRib%d" % k, ring, black_m, (0, 0, k * 0.19), parent=g)

# ---------- stoves with pots ----------
def make_pot(name, loc, broth_col):
    g = empty(name, loc, parent=props)
    prof = [(0, 0), (0.34, 0), (0.38, 0.04), (0.385, 0.5), (0.41, 0.52), (0.41, 0.55), (0.375, 0.55), (0.365, 0.5),
            (0.355, 0.05), (0, 0.05)]
    add(name + "Body", bm_lathe(prof, 36), steel_m, (0, 0, 0), parent=g, smooth=True)
    disc = bm_lathe([(0, 0.44), (0.36, 0.44)], 36)
    disc2 = bm_lathe([(0.36, 0.44), (0, 0.44)], 36)
    merge(disc, disc2)
    add(name + "Broth", disc, mat("BrothPot", broth_col, 0.1), (0, 0, 0), parent=g)
    for s in (-1, 1):
        add(name + "Handle", bm_torus(0.06, 0.016, 16, 8), iron_m, (s * 0.43, 0, 0.42), rot=(math.pi / 2, 0, 0), parent=g)
    return g


def stove(name, loc):
    g = empty(name, loc, parent=booth)
    add(name + "Box", bm_box(0.9, 0.9, 1.0 - FLOOR), iron_m, (0, 0, FLOOR + (1.0 - FLOOR) / 2), parent=g)
    add(name + "Top", bm_box(0.95, 0.95, 0.04), mat("StoveTop", (0.15, 0.15, 0.17), 0.4, metal=0.8), (0, 0, 1.0), parent=g)
    for k in range(3):
        add(name + "Vent", bm_box(0.5, 0.01, 0.05), glow_m, (0, -0.455, 0.35 + k * 0.12), parent=g)
    return g


stove("StoveR", (1.5, 0.75, 0))
stove("StoveL", (-1.5, 0.75, 0))
make_pot("PotR", (1.5, 0.75, 1.02), (0.88, 0.80, 0.58))
make_pot("PotL", (-1.5, 0.75, 1.02), (0.88, 0.80, 0.58))
# steam puffs
random.seed(9)
for nm, cx in (("SteamR", 1.5), ("SteamL", -1.5)):
    for k in range(10):
        r = 0.07 + 0.025 * k
        add("%s%d" % (nm, k), bm_sphere(r, 14, 10), steam_m,
            (cx + random.uniform(-0.1, 0.1) + 0.04 * k, 0.75 + random.uniform(-0.1, 0.1), 1.62 + k * 0.14), parent=props,
            smooth=True)


# ---------- ramen bowl ----------
def ramen_bowl(name, loc, rot=0.0, scale=1.0, noodles=True, seed=1):
    random.seed(seed)
    g = empty(name, loc, (0, 0, rot), parent=props)
    g.scale = (scale, scale, scale)
    outer = mat("BowlRed", (0.55, 0.04, 0.03), 0.25)
    inner = mat("BowlWhite", (0.93, 0.92, 0.88), 0.2)
    prof = [(0, 0), (0.09, 0), (0.1, 0.015), (0.115, 0.035), (0.2, 0.075), (0.27, 0.145), (0.305, 0.215), (0.31, 0.24),
            (0.298, 0.245), (0.29, 0.23), (0.255, 0.155), (0.18, 0.085), (0.0, 0.055)]
    add(name + "Bowl", bm_lathe(prof, 40, split=8), [outer, inner], parent=g, smooth=True)
    # decorative band
    add(name + "Band", bm_torus(0.272, 0.011, 48, 6), mat("BowlGold", (0.9, 0.7, 0.2), 0.3, metal=0.6), (0, 0, 0.165),
        parent=g, smooth=True)
    add(name + "Band2", bm_torus(0.228, 0.008, 48, 6), mat("BowlGold", (0.9, 0.7, 0.2), 0.3, metal=0.6), (0, 0, 0.115),
        parent=g, smooth=True)
    # broth
    b1 = bm_lathe([(0, 0.2), (0.275, 0.2)], 40)
    b2 = bm_lathe([(0.275, 0.2), (0, 0.2)], 40)
    merge(b1, b2)
    add(name + "Broth", b1, mat("BrothBowl", (0.78, 0.45, 0.16), 0.12), parent=g)
    noodle_m = mat("Noodle", (0.96, 0.80, 0.33), 0.45)
    if noodles:
        add(name + "NoodleMound", bm_sphere(0.19, 24, 12, (1, 1, 0.5)), noodle_m, (0, 0.02, 0.2), parent=g, smooth=True)
        nb = bmesh.new()
        for s in range(16):
            ph = random.uniform(0, 6.28)
            pts = []
            for k in range(14):
                f = k / 13
                a = ph + f * random.uniform(3.5, 6.0)
                rr = 0.17 * math.sin(math.pi * f * 0.9 + 0.2) + 0.02
                x = rr * math.cos(a)
                y = 0.02 + rr * math.sin(a)
                z = 0.2 + 0.095 * math.sqrt(max(0.0, 1 - (x / 0.19) ** 2 - ((y - 0.02) / 0.19) ** 2)) + 0.006
                pts.append((x, y, z))
            merge(nb, simple_tube(pts, 0.0085, 5, 4))
        add(name + "NoodleStrands", nb, noodle_m, parent=g, smooth=True)
    # chashu
    for i, (x, y, ang) in enumerate([(0.12, 0.11, 0.5), (0.0, 0.17, 0.35)]):
        cs = bm_cyl(0.095, 0.095, 0.014, 20)
        add(name + "ChashuFat%d" % i, cs, mat("ChashuFat", (0.92, 0.78, 0.68), 0.5), (x, y, 0.255 + i * 0.012),
            rot=(-ang, 0.3 * (1 - i * 2), 0), parent=g)
        add(name + "Chashu%d" % i, bm_cyl(0.08, 0.08, 0.017, 20), mat("Chashu", (0.55, 0.32, 0.2), 0.5),
            (x, y, 0.257 + i * 0.012), rot=(-ang, 0.3 * (1 - i * 2), 0), parent=g)
    # egg
    add(name + "EggWhite", bm_sphere(0.07, 18, 12, (1, 1.25, 0.55)), mat("EggWhite", (0.97, 0.95, 0.88), 0.3),
        (-0.11, -0.02, 0.255), rot=(0, 0, 0.5), parent=g, smooth=True)
    add(name + "EggYolk", bm_sphere(0.043, 14, 10, (1, 1.2, 0.6)), mat("EggYolk", (0.95, 0.55, 0.06), 0.25),
        (-0.11, -0.02, 0.272), rot=(0, 0, 0.5), parent=g, smooth=True)
    # naruto
    add(name + "NarutoPink", bm_cyl(0.05, 0.05, 0.012, 20), mat("NarutoPink", (0.95, 0.4, 0.55), 0.4),
        (0.1, -0.12, 0.262), rot=(0.25, 0.15, 0), parent=g)
    add(name + "NarutoWhite", bm_cyl(0.034, 0.034, 0.014, 20), white_m, (0.1, -0.12, 0.264), rot=(0.25, 0.15, 0), parent=g)
    add(name + "NarutoSwirl", bm_cyl(0.015, 0.015, 0.016, 12), mat("NarutoPink", (0.95, 0.4, 0.55), 0.4),
        (0.1, -0.12, 0.266), rot=(0.25, 0.15, 0), parent=g)
    # nori
    add(name + "Nori", bm_box(0.13, 0.008, 0.12), mat("Nori", (0.02, 0.06, 0.035), 0.7), (0.0, 0.2, 0.3),
        rot=(-0.25, 0, 0.1), parent=g)
    # scallion
    sb = bmesh.new()
    for k in range(34):
        a = random.uniform(0, 6.28)
        rr = random.uniform(0.02, 0.2)
        x, y = rr * math.cos(a), 0.02 + rr * math.sin(a)
        z = 0.2 + 0.1 * math.sqrt(max(0.0, 1 - (x / 0.2) ** 2 - ((y - 0.02) / 0.2) ** 2)) + 0.008
        c = bm_cyl(0.012, 0.012, 0.008, 8)
        bm_xform(c, Matrix.Translation((x, y, z)) @ Matrix.Rotation(random.uniform(0, 3), 4, 'X'))
        merge(sb, c)
    add(name + "Scallion", sb, mat("Scallion", (0.35, 0.75, 0.2), 0.5), parent=g)
    return g


bowlB = ramen_bowl("RamenBowlCenter", (0.1, -0.95, TOP), 0.3, 1.0, noodles=True, seed=3)
bowlD = ramen_bowl("RamenBowlLeft", (-0.85, -0.92, TOP), 2.2, 1.0, seed=5)
bowlR = ramen_bowl("RamenBowlRight", (0.95, -0.92, TOP), 4.0, 1.0, seed=8)

# ---------- counter accessories ----------
cad = empty("ChopstickCaddy", (1.5, -0.75, TOP), parent=props)
add("CaddyBody", bm_cyl(0.11, 0.11, 0.2, 16), wood_dark, (0, 0, 0.1), parent=cad, smooth=True)
for k in range(8):
    a = k * 0.8
    add("CaddyStick%d" % k, bm_cyl(0.008, 0.006, 0.34, 6), wood_light,
        (0.04 * math.cos(a), 0.04 * math.sin(a), 0.25), rot=(0.06 * math.sin(a), -0.06 * math.cos(a), 0), parent=cad)
sb = empty("Condiments", (1.4, -1.1, TOP), parent=props)
for i, (x, col, h) in enumerate([(-0.1, (0.15, 0.06, 0.03), 0.28), (0.07, (0.7, 0.1, 0.05), 0.22)]):
    add("Bottle%d" % i, bm_cyl(0.045, 0.045, h, 14), mat("Bottle%d" % i, col, 0.2), (x, 0, h / 2), parent=sb, smooth=True)
    add("BottleCap%d" % i, bm_cyl(0.02, 0.02, 0.05, 10), black_m, (x, 0, h + 0.025), parent=sb)
# napkin / menu stand
add("MenuStand", bm_box(0.2, 0.02, 0.28), cream_m, (-1.25, -1.2, TOP + 0.14), rot=(-0.2, 0, 0.1), parent=props)
add("MenuStandInk", bm_box(0.12, 0.01, 0.03), mat("Ink", (0.04, 0.03, 0.03), 0.8), (-1.25, -1.213, TOP + 0.2),
    rot=(-0.2, 0, 0.1), parent=props)

# ---------- stools ----------
for i, x in enumerate((-1.1, 0.4, 1.6)):
    s = empty("Stool%d" % i, (x, -2.3, 0), parent=props)
    add("StoolSeat", bm_cyl(0.24, 0.22, 0.07, 24), wood_light, (0, 0, 0.66), parent=s, smooth=True)
    for k in range(3):
        a = k * 2.094 + 0.5
        add("StoolLeg", bm_cyl(0.02, 0.03, 0.66, 8), wood_dark, (0.15 * math.cos(a), 0.15 * math.sin(a), 0.33),
            rot=(0.12 * math.sin(a), -0.12 * math.cos(a), 0), parent=s)
