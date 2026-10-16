# Kitchen equipment, ramen bowls and food, counter props.
WS_Z = 0.935   # work surface top
CT_Z = 1.055   # customer counter top

FOOD = {}


def food_mats():
    if FOOD:
        return FOOD
    FOOD['bowl_out'] = make_mat("Bowl_Outer", (0.50, 0.035, 0.03), rough=0.25, coat=0.6)
    FOOD['bowl_in'] = make_mat("Bowl_Inner", (0.93, 0.90, 0.83), rough=0.2, coat=0.5)
    FOOD['bowl_band'] = make_mat("Bowl_Band", (0.04, 0.03, 0.03), rough=0.25, coat=0.5)
    FOOD['broth'] = make_mat("Broth", (0.55, 0.30, 0.11), rough=0.08, coat=0.3, sss=0.2)
    FOOD['broth_pot'] = make_mat("Broth_Pot", (0.72, 0.52, 0.30), rough=0.1, sss=0.2)
    FOOD['water'] = make_mat("Boiling_Water", (0.55, 0.55, 0.50), rough=0.05, coat=0.5)
    FOOD['noodle'] = make_mat("Noodle", (0.95, 0.70, 0.25), rough=0.35, sss=0.3)
    FOOD['chashu'] = make_mat("Chashu", (0.80, 0.52, 0.40), rough=0.45, sss=0.2)
    FOOD['chashu_rim'] = make_mat("Chashu_Rim", (0.32, 0.13, 0.05), rough=0.35)
    FOOD['egg_out'] = make_mat("Egg_Marinated", (0.72, 0.48, 0.22), rough=0.25, sss=0.3)
    FOOD['egg_white'] = make_mat("Egg_White", (0.93, 0.90, 0.82), rough=0.3, sss=0.3)
    FOOD['yolk'] = make_mat("Egg_Yolk", (0.98, 0.45, 0.03), rough=0.2, sss=0.3)
    FOOD['naruto'] = make_mat("Naruto", (0.96, 0.94, 0.9), rough=0.4)
    FOOD['naruto_pink'] = make_mat("Naruto_Pink", (0.9, 0.22, 0.42), rough=0.4)
    FOOD['nori'] = make_mat("Nori", (0.025, 0.05, 0.035), rough=0.55)
    FOOD['menma'] = make_mat("Menma", (0.62, 0.42, 0.16), rough=0.4)
    FOOD['negi'] = make_mat("Negi_Green", (0.18, 0.55, 0.08), rough=0.4, sss=0.2)
    FOOD['negi_w'] = make_mat("Negi_White", (0.82, 0.9, 0.62), rough=0.4)
    FOOD['fat'] = make_mat("Broth_Fat", (0.95, 0.7, 0.25), rough=0.02, coat=0.8)
    FOOD['steel'] = bpy.data.materials["Steel"]
    FOOD['steel_dark'] = bpy.data.materials["Steel_Dark"]
    FOOD['mesh'] = make_mat("Strainer_Mesh", (0.42, 0.42, 0.44), rough=0.45, metal=1.0)
    FOOD['knife'] = make_mat("Knife_Blade", (0.8, 0.8, 0.82), rough=0.15, metal=1.0)
    FOOD['glass'] = make_mat("Glass", (0.85, 0.9, 0.9), rough=0.03, alpha=0.25, spec=0.8)
    FOOD['soy'] = make_mat("Soy_Sauce", (0.08, 0.02, 0.005), rough=0.05)
    FOOD['chili'] = make_mat("Chili_Oil", (0.55, 0.06, 0.01), rough=0.05)
    FOOD['beer'] = make_mat("Beer", (0.85, 0.5, 0.06), rough=0.05, alpha=0.85)
    FOOD['foam'] = make_mat("Beer_Foam", (0.97, 0.95, 0.9), rough=0.6)
    FOOD['bottle'] = make_mat("Beer_Bottle", (0.12, 0.05, 0.01), rough=0.08, coat=0.6)
    FOOD['label'] = make_mat("Label", (0.92, 0.88, 0.75), rough=0.5)
    FOOD['white'] = make_mat("White_Ceramic", (0.92, 0.92, 0.9), rough=0.25)
    FOOD['chopstick'] = make_mat("Chopstick", (0.85, 0.66, 0.42), rough=0.5)
    FOOD['drop'] = make_mat("Water_Drop", (0.9, 0.95, 1.0), rough=0.02, alpha=0.45)
    return FOOD


def ramen_bowl(name, loc, C, rot_z=0.0, contents="full", seed=0):
    """A ramen bowl; contents: 'full', 'broth', 'empty'. Returns list of objects."""
    F = food_mats()
    rnd = random.Random(seed)
    base = Vector(loc)
    objs = []
    outer = [(0.0, 0.003), (0.05, 0.0), (0.057, 0.0), (0.059, 0.012), (0.068, 0.015), (0.098, 0.035),
             (0.122, 0.064), (0.136, 0.088), (0.141, 0.097)]
    inner = [(0.141, 0.097), (0.1395, 0.1005), (0.136, 0.101), (0.131, 0.093), (0.118, 0.07),
             (0.092, 0.042), (0.06, 0.026), (0.0, 0.021)]
    o1 = lathe(name + "_out", outer, base, F['bowl_out'], C, segs=48)
    o2 = lathe(name + "_in", inner, base, F['bowl_in'], C, segs=48)
    band = lathe(name + "_band", [(0.1235, 0.066), (0.1295, 0.0745), (0.1315, 0.078), (0.1255, 0.0695)],
                 base, F['bowl_band'], C, segs=48)
    # decorative "raimon" band: small square spiral tiles around the outside
    deco = []
    for k in range(18):
        a = 2 * PI * k / 18
        r = 0.133
        p = base + Vector((math.cos(a) * r, math.sin(a) * r, 0.082))
        b = box(f"{name}_raimon_{k}", (0.004, 0.018, 0.006), p, F['bowl_band'], C, bev=0)
        b.rotation_euler = (0, -0.5, a)
        deco.append(b)
    join(deco, name + "_raimon")
    objs += [o1, o2, band]
    if contents == "empty":
        return objs
    bz = 0.074  # broth level
    broth = cylinder(name + "_broth", 0.1215, 0.004, base + Vector((0, 0, bz - 0.002)), F['broth'], C, segs=48)
    objs.append(broth)
    # floating fat droplets
    fats = []
    for k in range(26):
        r = 0.105 * math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * PI)
        s = rnd.uniform(0.003, 0.009)
        fats.append(sphere(f"{name}_fat{k}", s, base + Vector((math.cos(a) * r, math.sin(a) * r, bz + 0.0004)),
                           F['fat'], C, scale=(1, 1, 0.12), segs=10, rings=5))
    join(fats, name + "_fat")
    if contents == "broth":
        return objs

    R = Matrix.Rotation(rot_z, 4, 'Z')

    def L(x, y, z):
        return base + (R @ Vector((x, y, z)))

    # noodles: crinkly strands piled at front-centre, partially submerged
    strands = []
    for k in range(26):
        a0 = rnd.uniform(0, 2 * PI)
        c = Vector((rnd.uniform(0.0, 0.06), rnd.uniform(-0.07, 0.01), 0))
        length = rnd.uniform(0.10, 0.17)
        n = 22
        pts = []
        heading = a0
        p = c - Vector((math.cos(heading), math.sin(heading), 0)) * length / 2
        for i in range(n):
            t = i / (n - 1)
            heading += rnd.uniform(-0.35, 0.35)
            step = length / n
            p = p + Vector((math.cos(heading), math.sin(heading), 0)) * step
            q = p.copy()
            rr = q.xy.length
            if rr > 0.105:
                q.xy = q.xy * (0.105 / rr)
            wav = math.sin(t * 34 + k) * 0.0035
            perp = Vector((-math.sin(heading), math.cos(heading), 0))
            z = bz + 0.006 + 0.012 * math.sin(t * PI) * rnd.uniform(0.3, 1.0) - (0.004 if i in (0, n - 1) else 0)
            pts.append(L(q.x + perp.x * wav, q.y + perp.y * wav, z) - base)
        v, f, _, _ = tube_data([base + pp for pp in pts], [0.0036] * len(pts), 6)
        strands.append(obj_from_data(f"{name}_noodle{k}", v, f, F['noodle'], C))
    join(strands, name + "_noodles")

    # chashu slices leaning at back-left
    for k, (x, y, tilt, rz) in enumerate(((-0.045, 0.05, 0.55, 0.5), (0.0, 0.065, 0.6, 0.0))):
        p = L(x, y, bz + 0.018)
        rim = cylinder(f"{name}_chashu{k}", 0.052, 0.009, p, F['chashu_rim'], C, segs=28)
        meat = cylinder(f"{name}_chashu{k}_m", 0.045, 0.0098, p, F['chashu'], C, segs=28)
        for o in (rim, meat):
            o.rotation_euler = (tilt, 0, rz + rot_z)
            o.scale = (1.0, 0.85, 1.0)
        # fat marbling streak
        fat = cylinder(f"{name}_chashu{k}_f", 0.018, 0.0101, p, F['egg_white'], C, segs=16)
        fat.rotation_euler = (tilt, 0, rz + rot_z)
        fat.scale = (1.4, 0.35, 1.0)

    # ajitama egg halves at front-left
    for k, (x, y, rz) in enumerate(((-0.07, -0.025, 0.4), (-0.045, -0.072, -0.5))):
        p = L(x, y, bz + 0.004)
        prof = [(0.0, -0.018)]
        for i in range(1, 9):
            th = (PI / 2) * i / 8
            prof.append((0.027 * math.sin(th), -0.021 * math.cos(th)))
        egg = lathe(f"{name}_egg{k}", prof, p, F['egg_out'], C, segs=24)
        egg.scale = (1.35, 1.0, 1.0)
        egg.rotation_euler = (0.15, 0, rz + rot_z)
        top = cylinder(f"{name}_egg{k}_w", 0.0265, 0.002, p, F['egg_white'], C, segs=24)
        top.scale = (1.35, 1.0, 1.0)
        top.rotation_euler = (0.15, 0, rz + rot_z)
        yolk = sphere(f"{name}_egg{k}_y", 0.0155, p + Vector((0, 0, 0.0005)), F['yolk'], C,
                      scale=(1.3, 1.0, 0.35), segs=16, rings=8)
        yolk.rotation_euler = (0.15, 0, rz + rot_z)

    # naruto at the right
    p = L(0.075, 0.0, bz + 0.006)
    prof = []
    nz = []
    disc_v, disc_f = [], []
    nr = 40
    # wavy-edged disc
    top_c, bot_c = [], []
    for i in range(nr):
        a = 2 * PI * i / nr
        r = 0.03 + 0.002 * math.cos(a * 12)
        disc_v.append((math.cos(a) * r, math.sin(a) * r, 0.004))
        disc_v.append((math.cos(a) * r, math.sin(a) * r, -0.004))
    disc_v.append((0, 0, 0.004))
    disc_v.append((0, 0, -0.004))
    ct, cb = 2 * nr, 2 * nr + 1
    for i in range(nr):
        j = (i + 1) % nr
        disc_f.append([2 * i, 2 * j, ct])
        disc_f.append([2 * j + 1, 2 * i + 1, cb])
        disc_f.append([2 * i + 1, 2 * j + 1, 2 * j, 2 * i])
    nob = obj_from_data(f"{name}_naruto", disc_v, disc_f, F['naruto'], C, smooth=False)
    nob.location = p
    nob.rotation_euler = (0.25, -0.1, rot_z)
    sp = []
    for i in range(60):
        t = i / 59
        a = t * 2.2 * 2 * PI
        r = 0.002 + 0.023 * t
        sp.append(Vector((math.cos(a) * r, math.sin(a) * r, 0.0038)))
    spiral = tube(f"{name}_naruto_sp", sp, 0.0019, F['naruto_pink'], C, ring=6, samples=2)
    spiral.location = p
    spiral.rotation_euler = (0.25, -0.1, rot_z)

    # nori sheets standing at the back
    for k, (x, rz) in enumerate(((-0.02, 0.15), (0.045, -0.2))):
        verts, faces = [], []
        w, h = 0.075, 0.095
        for j in range(5):
            for i in range(5):
                u, v = i / 4, j / 4
                bend = 0.006 * math.sin(u * PI)
                verts.append(((u - 0.5) * w, bend, v * h))
        for j in range(4):
            for i in range(4):
                a0 = j * 5 + i
                faces.append([a0, a0 + 1, a0 + 6, a0 + 5])
        nori = obj_from_data(f"{name}_nori{k}", verts, faces, F['nori'], C)
        md = nori.modifiers.new("Thick", 'SOLIDIFY')
        md.thickness = 0.0015
        nori.location = L(x, 0.09, bz - 0.012)
        nori.rotation_euler = (-0.38, 0, rz + rot_z)

    # menma
    for k in range(5):
        p = L(0.035 + rnd.uniform(-0.012, 0.012), -0.065 + rnd.uniform(-0.01, 0.01), bz + 0.008 + k * 0.002)
        m = box(f"{name}_menma{k}", (0.038, 0.009, 0.005), p, F['menma'], C, bev=0.0015, segs=1)
        m.rotation_euler = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, PI) + rot_z)

    # chopped green onions sprinkled on top
    negi = []
    for k in range(60):
        r = 0.03 * math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * PI)
        x, y = 0.012 + math.cos(a) * r, -0.025 + math.sin(a) * r
        z = bz + 0.016 + rnd.uniform(0, 0.008)
        if k > 40:  # stragglers
            r = 0.09 * math.sqrt(rnd.random())
            x, y = math.cos(a) * r, math.sin(a) * r
            z = bz + 0.006
        ring = lathe(f"{name}_negi{k}", [(0.0035, -0.0012), (0.0042, 0.0), (0.0035, 0.0012), (0.0028, 0.0),
                                         (0.0035, -0.0012)], L(x, y, z),
                     F['negi'] if rnd.random() < 0.7 else F['negi_w'], C, segs=8, smooth=True)
        ring.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0)
        negi.append(ring)
    join(negi, name + "_negi")
    return objs


def steam_wisp(name, base, height, C, mat, seed=0, r0=0.02, r1=0.06, sway=0.05):
    rnd = random.Random(seed)
    pts = []
    n = 9
    ph = rnd.uniform(0, 2 * PI)
    for i in range(n):
        t = i / (n - 1)
        pts.append(Vector(base) + Vector((math.sin(t * 5 + ph) * sway * t + rnd.uniform(-0.01, 0.01),
                                          math.cos(t * 4 + ph) * sway * 0.6 * t, t * height)))
    pts = catmull(pts, 5)
    radii = [r0 + (r1 - r0) * (i / (len(pts) - 1)) for i in range(len(pts))]
    radii = [r * (0.4 + 0.6 * math.sin(min(1.0, i / (len(pts) - 1) * 1.15) * PI) ** 0.5)
             for i, r in enumerate(radii)]
    v, f, _, _ = tube_data(pts, radii, 10)
    return obj_from_data(name, v, f, mat, C)


def steam_material():
    m = make_mat("Steam", (1.0, 1.0, 1.0), rough=1.0, alpha=0.10, spec=0.0)
    nt = m.node_tree
    out = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'][0]
    vol = nt.nodes.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = (1.0, 0.97, 0.94, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 9.0
    nz.inputs['Detail'].default_value = 3.0
    nz.inputs['Roughness'].default_value = 0.6
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.42
    mr.inputs['From Max'].default_value = 0.72
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    fade = nt.nodes.new('ShaderNodeFloatCurve')
    c = fade.mapping.curves[0]
    c.points[0].location = (0.0, 0.0)
    c.points[1].location = (1.0, 0.0)
    c.points.new(0.15, 1.0)
    c.points.new(0.5, 0.6)
    fade.mapping.update()
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul2 = nt.nodes.new('ShaderNodeMath')
    mul2.operation = 'MULTIPLY'
    mul2.inputs[1].default_value = 7.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], fade.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mul.inputs[0])
    nt.links.new(fade.outputs['Value'], mul.inputs[1])
    nt.links.new(mul.outputs[0], mul2.inputs[0])
    nt.links.new(mul2.outputs[0], vol.inputs['Density'])
    nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    # surface fully transparent in renders; export restores a translucent surface
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    nt.links.new(tr.outputs['BSDF'], out.inputs['Surface'])
    m["steam"] = True
    return m


def build_kitchen(M):
    C = get_coll("Kitchen")
    F = food_mats()
    rnd = random.Random(5)
    out = {}

    # ---- burners --------------------------------------------------------------
    for x in (-0.76,):
        lathe(f"Burner_{x}", [(0.0, WS_Z), (0.16, WS_Z), (0.17, WS_Z + 0.03), (0.15, WS_Z + 0.035),
                              (0.0, WS_Z + 0.035)], (x, 0.03, 0), F['steel_dark'], C, segs=32, smooth=False)
        for k in range(6):
            a = k * PI / 3
            box(f"Burner_Grate_{k}", (0.17, 0.012, 0.012), (x + math.cos(a) * 0.08, 0.03 + math.sin(a) * 0.08,
                                                            WS_Z + 0.041), M['black'], C, rot=(0, 0, a), bev=0)

    # ---- stock pot with broth ---------------------------------------------------
    px, py, pz = -0.76, 0.03, WS_Z + 0.047
    H, R = 0.34, 0.2
    pot = lathe("Stock_Pot", [(0.0, 0.0), (R - 0.01, 0.0), (R, 0.012), (R, H - 0.01), (R + 0.012, H - 0.004),
                              (R + 0.012, H + 0.004), (R - 0.004, H + 0.004), (R - 0.008, H - 0.01),
                              (R - 0.008, 0.02), (0.0, 0.02)], (px, py, pz), F['steel'], C, segs=48)
    for s in (-1, 1):
        h = tube(f"Stock_Pot_Handle_{s}", [(px + s * (R - 0.01), py - 0.06, pz + H - 0.06),
                                           (px + s * (R + 0.05), py - 0.05, pz + H - 0.05),
                                           (px + s * (R + 0.05), py + 0.05, pz + H - 0.05),
                                           (px + s * (R - 0.01), py + 0.06, pz + H - 0.06)], 0.009,
                 F['steel'], C, ring=8, samples=4)
    cylinder("Stock_Broth", R - 0.009, 0.004, (px, py, pz + H - 0.06), F['broth_pot'], C, segs=48)
    # bones / aromatics peeking out
    for k in range(5):
        a = rnd.uniform(0, 2 * PI)
        r = rnd.uniform(0.03, 0.13)
        sphere(f"Pot_Bit_{k}", rnd.uniform(0.018, 0.03),
               (px + math.cos(a) * r, py + math.sin(a) * r, pz + H - 0.062),
               F['egg_white'] if k % 2 else F['negi_w'], C, scale=(1.6, 1, 0.5), segs=12, rings=6)
    # ladle (scoop in pot, handle toward the chef)
    lad_bowl = Vector((-0.70, 0.0, pz + H - 0.075))
    lad_top = Vector((-0.40, 0.33, 1.68))
    scoop = lathe("Ladle_Scoop", [(0.0, -0.045), (0.03, -0.042), (0.05, -0.03), (0.058, -0.01),
                                  (0.06, 0.0), (0.056, 0.0), (0.054, -0.008), (0.047, -0.026),
                                  (0.028, -0.037), (0.0, -0.04)], lad_bowl, F['steel'], C, segs=32)
    rim_pt = lad_bowl + (lad_top - lad_bowl).normalized() * 0.06
    rim_pt.z = lad_bowl.z
    handle_pts = [lad_bowl + Vector((0.04, 0.035, 0.0)), lad_bowl + Vector((0.07, 0.07, 0.06)),
                  lad_bowl.lerp(lad_top, 0.5), lad_top]
    tube("Ladle_Handle", handle_pts, 0.0085, F['steel'], C, ring=10, samples=6)
    out['ladle'] = (lad_bowl.lerp(lad_top, 0.5), lad_top)

    # ---- noodle boiler with strainers (tebo) -------------------------------------------
    bx, by = 0.78, 0.04
    bw, bh = 0.40, 0.25
    lathe("Noodle_Boiler", [(0.0, 0.0), (bw / 2 * 1.41 - 0.01, 0.0), (bw / 2 * 1.41, 0.01),
                            (bw / 2 * 1.41, bh), (bw / 2 * 1.41 - 0.012, bh), (bw / 2 * 1.41 - 0.012, 0.02),
                            (0.0, 0.02)], (bx, by, WS_Z), F['steel'], C, segs=4, smooth=False).rotation_euler = (
        0, 0, PI / 4)
    box("Boiler_Water", (bw - 0.03, bw - 0.03, 0.006), (bx, by, WS_Z + bh - 0.035), F['water'], C, bev=0)
    for k in range(40):
        sphere(f"Bubble_{k}", rnd.uniform(0.004, 0.012),
               (bx + rnd.uniform(-0.17, 0.17), by + rnd.uniform(-0.17, 0.17), WS_Z + bh - 0.032),
               F['water'], C, scale=(1, 1, 0.6), segs=10, rings=6)

    def tebo(name, rim_c, handle_dir, handle_len=0.32, filled=True):
        rim_c = Vector(rim_c)
        objs = []
        b = lathe(name + "_basket", [(0.0, -0.165), (0.025, -0.165), (0.045, -0.12), (0.06, -0.05),
                                      (0.066, -0.005), (0.068, 0.0), (0.064, 0.0), (0.062, -0.006),
                                      (0.056, -0.05), (0.041, -0.12), (0.022, -0.158), (0.0, -0.158)],
                  rim_c, F['mesh'], C, segs=24)
        ring = lathe(name + "_rim", [(0.066, -0.006), (0.072, -0.003), (0.072, 0.004), (0.066, 0.006)],
                     rim_c, F['steel'], C, segs=24)
        hd = Vector(handle_dir).normalized()
        start = rim_c + Vector((hd.x, hd.y, 0)).normalized() * 0.066
        tube(name + "_handle", [start, start + hd * handle_len], 0.008, M['wood_m'], C, ring=8, samples=1)
        if filled:
            strands = []
            for k in range(14):
                a = rnd.uniform(0, 2 * PI)
                pts = []
                for i in range(10):
                    t = i / 9
                    r = 0.04 * rnd.uniform(0.2, 1.0)
                    aa = a + t * rnd.uniform(1.5, 3.5)
                    pts.append(rim_c + Vector((math.cos(aa) * r, math.sin(aa) * r, -0.01 + 0.02 * math.sin(t * PI)
                                               + rnd.uniform(-0.005, 0.005))))
                v, f, _, _ = tube_data(catmull(pts, 3), [0.0036] * (9 * 3 + 1), 6)
                strands.append(obj_from_data(f"{name}_n{k}", v, f, F['noodle'], C))
            join(strands, name + "_noodles")
        return start + hd * handle_len

    for k, (dx, dy) in enumerate(((-0.08, 0.08), (0.09, 0.07), (0.08, -0.09))):
        rc = Vector((bx + dx, by + dy, WS_Z + bh + 0.04))
        hdir = Vector((dx, dy, 0)).normalized() * 0.55 + Vector((0, 0, 0.85))
        tebo(f"Tebo_{k}", rc, hdir, filled=False)
    # the strainer being lifted by the octopus, held above the prep bowl
    lifted_rim = Vector((0.33, -0.05, 1.33))
    hdir = Vector((0.55, 0.5, 0.55))
    tip = tebo("Tebo_Lifted", lifted_rim, hdir, handle_len=0.34)
    out['tebo'] = (lifted_rim, tip, hdir.normalized())
    # drips falling from the lifted strainer
    for k in range(7):
        sphere(f"Drip_{k}", 0.006, lifted_rim + Vector((rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03),
                                                         -0.18 - k * 0.035)),
               F['drop'], C, scale=(1, 1, 1.8), segs=10, rings=6)

    # ---- prep bowl (broth only, waiting for noodles) -----------------------------------
    ramen_bowl("Prep_Bowl", (0.33, -0.06, WS_Z), C, contents="broth", seed=3)

    # ---- cutting board, green onion, knife ---------------------------------------------
    cb = box("Cutting_Board", (0.36, 0.25, 0.028), (-0.27, -0.02, WS_Z + 0.014), M['wood_l'], C, bev=0.006)
    box_uv(cb, 1.0)
    # whole negi stalk being chopped
    tube("Negi_Stalk", [(-0.42, 0.04, WS_Z + 0.04), (-0.30, 0.03, WS_Z + 0.04), (-0.22, 0.02, WS_Z + 0.04)],
         0.012, F['negi_w'], C, ring=12, samples=2)
    tube("Negi_Stalk_G", [(-0.50, 0.05, WS_Z + 0.042), (-0.43, 0.045, WS_Z + 0.04)], 0.011, F['negi'], C,
         ring=12, samples=2)
    pile = []
    for k in range(45):
        r = 0.05 * math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * PI)
        p = Vector((-0.16 + math.cos(a) * r * 1.2, -0.06 + math.sin(a) * r * 0.8, WS_Z + 0.032 +
                    0.012 * (1 - r / 0.05) + rnd.uniform(0, 0.004)))
        ring = lathe(f"Negi_Chop_{k}", [(0.006, -0.002), (0.0075, 0.0), (0.006, 0.002), (0.0048, 0.0),
                                        (0.006, -0.002)], p, F['negi'] if rnd.random() < 0.6 else F['negi_w'], C,
                     segs=8)
        ring.rotation_euler = (rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2), 0)
        pile.append(ring)
    join(pile, "Negi_Pile")
    # knife: blade resting on the stalk, handle lifted toward the chef
    kn_tip = Vector((-0.38, -0.05, WS_Z + 0.035))
    kn_heel = Vector((-0.17, 0.05, WS_Z + 0.075))
    blade_v, blade_f = [], []
    along = (kn_heel - kn_tip).normalized()
    upv = Vector((0, 0, 1))
    side = along.cross(upv).normalized()
    upv = side.cross(along).normalized()
    nb = 8
    for i in range(nb + 1):
        t = i / nb
        p = kn_tip.lerp(kn_heel, t)
        h = 0.012 + 0.038 * min(1, t * 1.6)
        for (dz, ds) in ((0, 0.0), (h, 0.002), (h, -0.002)):
            blade_v.append(tuple(p + upv * (dz - 0.0) + side * ds))
    for i in range(nb):
        a, b = i * 3, (i + 1) * 3
        blade_f += [[a, b, b + 1, a + 1], [a, a + 2, b + 2, b], [a + 1, b + 1, b + 2, a + 2]]
    blade_f.append([0, 1, 2])
    blade_f.append([nb * 3, nb * 3 + 2, nb * 3 + 1])
    obj_from_data("Knife_Blade", blade_v, blade_f, F['knife'], C, smooth=False)
    kh0 = kn_heel + upv * 0.02
    kh1 = kh0 + along * 0.13 + upv * 0.02
    tube("Knife_Handle", [kh0, kh1], 0.012, M['wood_d'], C, ring=10, samples=1)
    out['knife'] = (kh0, kh1)

    # ---- stack of clean bowls ----------------------------------------------------------
    for k in range(4):
        ramen_bowl(f"Stack_Bowl_{k}", (1.12, 0.17, WS_Z + k * 0.032), C, contents="empty")

    # ---- the hero bowl being served on the counter --------------------------------------
    hero = Vector((0.08, -0.5, CT_Z))
    ramen_bowl("Hero_Bowl", hero, C, contents="full", seed=7, rot_z=0.0)
    out['hero'] = hero
    # chopsticks on a rest
    rest = box("Hashioki", (0.03, 0.012, 0.01), (-0.12, -0.66, CT_Z + 0.005), F['white'], C, bev=0.004)
    for k, dy in enumerate((-0.006, 0.006)):
        tube(f"Chopstick_{k}", [(-0.19, -0.64 + dy, CT_Z + 0.004), (-0.12, -0.66 + dy, CT_Z + 0.014),
                                 (0.05, -0.70 + dy * 1.5, CT_Z + 0.006)], lambda t: 0.0045 - 0.0025 * t,
             F['chopstick'], C, ring=8, samples=3)
    # spoon (renge)
    sp = lathe("Renge", [(0.0, -0.012), (0.018, -0.011), (0.026, -0.004), (0.028, 0.0), (0.025, 0.0),
                         (0.022, -0.006), (0.0, -0.009)], (0.27, -0.6, CT_Z + 0.012), F['white'], C, segs=20)
    sp.scale = (1.5, 1.0, 1.0)
    sp.rotation_euler = (0, 0, 0.6)
    tube("Renge_Handle", [(0.27 + 0.03, -0.6 + 0.022, CT_Z + 0.006), (0.27 + 0.075, -0.6 + 0.055, CT_Z + 0.02)],
         0.006, F['white'], C, ring=8, samples=1)

    # ---- condiments at the left end of the counter -------------------------------------
    tray = box("Condiment_Tray", (0.3, 0.16, 0.015), (-1.2, -0.52, CT_Z + 0.0075), M['wood_d'], C, bev=0.003)
    box_uv(tray, 1.0)
    # soy sauce dispenser
    lathe("Soy_Bottle", [(0.0, 0.0), (0.03, 0.0), (0.032, 0.01), (0.032, 0.08), (0.02, 0.1), (0.012, 0.11),
                         (0.0, 0.11)], (-1.29, -0.52, CT_Z + 0.015), F['glass'], C, segs=20)
    lathe("Soy_Liquid", [(0.0, 0.003), (0.028, 0.003), (0.029, 0.06), (0.0, 0.06)],
          (-1.29, -0.52, CT_Z + 0.015), F['soy'], C, segs=20)
    lathe("Soy_Cap", [(0.0, 0.105), (0.016, 0.105), (0.016, 0.13), (0.008, 0.14), (0.004, 0.155), (0.0, 0.156)],
          (-1.29, -0.52, CT_Z + 0.015), M['red'], C, segs=16)
    # chili oil jar
    lathe("Chili_Jar", [(0.0, 0.0), (0.03, 0.0), (0.032, 0.05), (0.028, 0.06), (0.0, 0.06)],
          (-1.2, -0.52, CT_Z + 0.015), F['glass'], C, segs=20)
    lathe("Chili_Oil", [(0.0, 0.003), (0.028, 0.003), (0.029, 0.04), (0.0, 0.04)],
          (-1.2, -0.52, CT_Z + 0.015), F['chili'], C, segs=20)
    lathe("Chili_Lid", [(0.0, 0.06), (0.03, 0.06), (0.03, 0.075), (0.0, 0.075)],
          (-1.2, -0.52, CT_Z + 0.015), M['black'], C, segs=20)
    # pepper shaker
    lathe("Pepper", [(0.0, 0.0), (0.02, 0.0), (0.021, 0.07), (0.016, 0.085), (0.0, 0.09)],
          (-1.12, -0.5, CT_Z + 0.015), F['white'], C, segs=16)
    # chopstick box
    cbx = box("Chopstick_Box", (0.08, 0.14, 0.09), (-1.38, -0.42, CT_Z + 0.045), M['wood_m'], C, bev=0.004)
    box_uv(cbx, 1.0)
    for k in range(18):
        x = -1.38 + rnd.uniform(-0.03, 0.03)
        y = -0.42 + rnd.uniform(-0.06, 0.06)
        tube(f"Box_Chopstick_{k}", [(x, y, CT_Z + 0.03), (x + rnd.uniform(-0.01, 0.01), y +
                                                          rnd.uniform(-0.01, 0.01), CT_Z + 0.17)],
             0.004, F['chopstick'], C, ring=6, samples=1)

    # ---- beer and glass at the right end -----------------------------------------------
    bxp = Vector((1.18, -0.55, CT_Z))
    lathe("Beer_Bottle", [(0.0, 0.0), (0.036, 0.0), (0.038, 0.01), (0.038, 0.17), (0.034, 0.2),
                          (0.016, 0.24), (0.014, 0.29), (0.016, 0.295), (0.0, 0.3)], bxp, F['bottle'], C, segs=24)
    lathe("Beer_Label", [(0.0385, 0.06), (0.0385, 0.13)], bxp, F['label'], C, segs=24)
    gp = bxp + Vector((-0.12, 0.03, 0))
    lathe("Beer_Glass", [(0.0, 0.0), (0.03, 0.0), (0.034, 0.12), (0.032, 0.12), (0.028, 0.004), (0.0, 0.004)],
          gp, F['glass'], C, segs=24)
    lathe("Beer_In_Glass", [(0.0, 0.006), (0.027, 0.006), (0.0305, 0.09), (0.0, 0.09)], gp, F['beer'], C,
          segs=24)
    lathe("Beer_Foam", [(0.0, 0.09), (0.0305, 0.09), (0.0318, 0.11), (0.026, 0.118), (0.0, 0.12)], gp, F['foam'],
          C, segs=24)

    # ---- maneki-neko (lucky cat) at the right end of the counter ---------------------------
    cat_w = make_mat("Cat_White", (0.93, 0.92, 0.88), rough=0.25, coat=0.5)
    cat_r = make_mat("Cat_Red", (0.75, 0.05, 0.04), rough=0.3, coat=0.4)
    gold = make_mat("Gold", (1.0, 0.72, 0.25), rough=0.25, metal=1.0)
    cat_dark = make_mat("Cat_Dark", (0.03, 0.03, 0.03), rough=0.4)
    cp = Vector((1.36, -0.40, CT_Z))
    rz = -0.45
    Rz = Matrix.Rotation(rz, 4, 'Z')

    def cl(x, y, z):
        return cp + (Rz @ Vector((x, y, z)))

    sphere("Cat_Body", 0.055, cl(0, 0, 0.055), cat_w, C, scale=(1.0, 0.85, 1.05))
    sphere("Cat_Head", 0.05, cl(0, -0.005, 0.145), cat_w, C, scale=(1.12, 0.92, 0.95))
    for s3 in (-1, 1):
        ear = cylinder(f"Cat_Ear_{s3}", 0.022, 0.035, cl(s3 * 0.032, 0.0, 0.19), cat_w, C, segs=12, r2=0.002)
        ear.rotation_euler = (0, s3 * 0.35, rz)
        inner = cylinder(f"Cat_Ear_In_{s3}", 0.013, 0.025, cl(s3 * 0.032, -0.008, 0.188), cat_r, C, segs=10, r2=0.001)
        inner.rotation_euler = (0, s3 * 0.35, rz)
        eye = sphere(f"Cat_Eye_{s3}", 0.0065, cl(s3 * 0.02, -0.047, 0.15), cat_dark, C, scale=(1.4, 0.5, 0.45))
        eye.rotation_euler = (0, 0, rz)
    sphere("Cat_Nose", 0.005, cl(0, -0.05, 0.138), cat_r, C)
    collar = lathe("Cat_Collar", [(0.046, 0.0), (0.05, 0.006), (0.046, 0.012), (0.042, 0.006), (0.046, 0.0)],
                   cl(0, 0, 0.098), cat_r, C, segs=24)
    collar.rotation_euler = (0.12, 0, rz)
    sphere("Cat_Bell", 0.012, cl(0, -0.05, 0.095), gold, C)
    # raised beckoning paw
    tube("Cat_Arm", [cl(0.045, -0.01, 0.08), cl(0.06, -0.02, 0.13), cl(0.058, -0.03, 0.17)], 0.016, cat_w, C,
         ring=10, samples=4)
    sphere("Cat_Paw", 0.019, cl(0.058, -0.032, 0.18), cat_w, C)
    sphere("Cat_Paw_Low", 0.017, cl(-0.03, -0.045, 0.04), cat_w, C)
    coin = cylinder("Cat_Coin", 0.03, 0.006, cl(-0.025, -0.05, 0.065), gold, C, segs=20)
    coin.rotation_euler = (1.35, 0, rz)
    coin.scale = (0.7, 1.0, 1.0)

    # ---- steam --------------------------------------------------------------------------
    steam = steam_material()
    SC = get_coll("Steam")
    k = 0
    for (x, y, z, h, n) in ((px, py, pz + H, 0.75, 6), (bx, by, WS_Z + bh, 0.6, 5),
                            (hero.x, hero.y, CT_Z + 0.08, 0.45, 3), (0.33, -0.06, WS_Z + 0.08, 0.35, 2)):
        for i in range(n):
            ang = 2 * PI * i / n
            rr = 0.06 if n > 3 else 0.03
            steam_wisp(f"Steam_{k}", (x + math.cos(ang) * rr, y + math.sin(ang) * rr, z), h * rnd.uniform(0.7, 1.1),
                       SC, steam, seed=k, r0=0.03, r1=0.10 if n > 3 else 0.06, sway=0.08)
            k += 1
    return out
