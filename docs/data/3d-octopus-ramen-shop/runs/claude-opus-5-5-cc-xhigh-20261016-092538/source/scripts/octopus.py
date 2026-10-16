# The octopus chef: mantle/head, face, hachimaki headband, eight tentacles with suckers.

HEAD_C = Vector((0.0, 0.80, 1.56))
HEAD_R = Vector((0.40, 0.38, 0.46))

SKIN_TOP = Vector((0.52, 0.045, 0.035))
SKIN_MID = Vector((0.78, 0.13, 0.06))
SKIN_BELLY = Vector((0.98, 0.55, 0.40))


def _smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def head_deform(u):
    """Map a unit-sphere point to the mantle surface (object space around HEAD_C)."""
    x, y, z = u
    p = Vector((x * HEAD_R.x, y * HEAD_R.y, z * HEAD_R.z))
    if z > 0:
        p.y += 0.13 * z * z          # mantle leans back
        p.z += 0.04 * z * z
        p.x *= 1.0 + 0.05 * z
    if y < 0:
        p.y *= 0.93                  # slightly flatter face
    if z < -0.25:
        k = ((-z - 0.25) / 0.75)
        s = 1.0 - 0.32 * k * k
        p.x *= s
        p.y = (p.y - 0.0) * s
    return p


def skin_color(world_co, normal, seed_off=Vector((0, 0, 0))):
    h = world_co.z
    up = normal.z
    top = _smooth(1.45, 2.0, h) * 0.8 + max(up, 0) * 0.2
    c = SKIN_MID.lerp(SKIN_TOP, min(top, 1.0))
    belly = _smooth(-0.1, -0.85, up) * 0.85
    c = c.lerp(SKIN_BELLY, belly)
    n = noise.noise(world_co * 9.0 + seed_off) * 0.5 + noise.noise(world_co * 23.0) * 0.25
    c = c * (1.0 + 0.10 * n)
    return (min(c.x, 1), min(c.y, 1), min(c.z, 1))


def build_octopus(info):
    C = get_coll("Octopus")
    K = info.get("kitchen", {})
    rnd = random.Random(42)

    skin = make_mat("Octo_Skin", (0.78, 0.13, 0.06), rough=0.32, vcol=True, coat=0.35, sss=0.06)
    sucker_m = make_mat("Octo_Sucker", (0.99, 0.72, 0.6), rough=0.4, vcol=True, sss=0.15)
    eye_w = make_mat("Eye_White", (0.95, 0.94, 0.92), rough=0.15, coat=0.8)
    pupil = make_mat("Eye_Pupil", (0.015, 0.012, 0.02), rough=0.1, coat=1.0)
    iris = make_mat("Eye_Iris", (0.25, 0.12, 0.05), rough=0.1, coat=1.0)
    hilite = make_mat("Eye_Highlight", (1, 1, 1), rough=0.2, emit=(1, 1, 1), emit_strength=3.0)
    mouth_m = make_mat("Mouth", (0.25, 0.03, 0.03), rough=0.5)
    tongue_m = make_mat("Tongue", (0.95, 0.35, 0.35), rough=0.4)
    blush_m = make_mat("Blush", (1.0, 0.42, 0.45), rough=0.6, alpha=0.75)
    spot_m = make_mat("Octo_Spot", (0.36, 0.03, 0.025), rough=0.35, coat=0.3)
    band_m = make_mat("Hachimaki", (0.93, 0.93, 0.9), rough=0.85, spec=0.3)
    band_r = make_mat("Hachimaki_Red", (0.75, 0.05, 0.05), rough=0.85, spec=0.3)

    # ---- head -------------------------------------------------------------------
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=48, radius=1.0)
    for v in bm.verts:
        v.co = head_deform(v.co.normalized())
    bmesh.ops.translate(bm, verts=bm.verts, vec=HEAD_C)
    bm.normal_update()
    bvh = BVHTree.FromBMesh(bm)
    head = obj_from_bm("Octo_Head", bm, skin, C)
    set_vcol(head, lambda co, n, i: skin_color(co, n))

    def surf(p_from, p_to):
        d = (Vector(p_to) - Vector(p_from)).normalized()
        hit = bvh.ray_cast(Vector(p_from), d, 5.0)
        return hit[0], hit[1]

    def surf_front(x, z):
        return surf((x, -1.0, z), (x, HEAD_C.y, z))

    # ---- eyes ---------------------------------------------------------------------
    look = Vector((-0.35, -2.6, 1.30))   # toward the customer seats / viewer
    ER = 0.098
    eyes = []
    for s in (-1, 1):
        p, n = surf_front(s * 0.158, 1.50)
        ec = p - n * 0.032
        sphere(f"Eye_{s}", ER, ec, eye_w, C, segs=32, rings=20)
        d = (look - ec).normalized()
        # iris + pupil as flattened spheres sitting on the eyeball
        q = d.to_track_quat('Z', 'Y')
        ir = sphere(f"Eye_Iris_{s}", ER * 0.62, ec + d * (ER - ER * 0.62 * 0.18), iris, C, scale=(1, 1.08, 0.22),
                    segs=28, rings=14)
        ir.rotation_euler = q.to_euler()
        pu = sphere(f"Eye_Pupil_{s}", ER * 0.47, ec + d * (ER - ER * 0.47 * 0.1), pupil, C, scale=(1, 1.08, 0.22),
                    segs=28, rings=14)
        pu.rotation_euler = q.to_euler()
        # highlights (upper-left, consistent "key light" reflection)
        side = d.cross(Vector((0, 0, 1))).normalized()
        upv = side.cross(d).normalized()
        for k, (a, b, r) in enumerate(((0.33, 0.38, 0.20), (-0.25, -0.30, 0.09))):
            hd = (d + side * a + upv * b).normalized()
            sphere(f"Eye_Hi_{s}_{k}", ER * r, ec + hd * ER * 1.0, hilite, C, segs=12, rings=8,
                   scale=(1, 1, 1))
        # upper eyelid: spherical cap following the head colour
        prof = []
        th_max = 1.25
        for i in range(13):
            th = th_max * i / 12
            prof.append((ER * 1.075 * math.sin(th), ER * 1.075 * math.cos(th)))
        for i in range(12, -1, -1):
            th = th_max * i / 12
            prof.append((ER * 1.02 * math.sin(th), ER * 1.02 * math.cos(th)))
        lid = lathe(f"Eyelid_{s}", prof, ec, skin, C, segs=32)
        # cap axis points up and slightly forward so the lid covers the top of the eye;
        # a small roll lowers the outer corners for a kind expression
        axis = (Vector((0, 0, 1)) + n * 0.3).normalized()
        lid.rotation_mode = 'QUATERNION'
        lid.rotation_quaternion = Quaternion(n, -s * 0.12) @ axis.to_track_quat('Z', 'Y')
        bpy.context.view_layer.update()
        set_vcol(lid, lambda co, nn, i: skin_color(co, nn))
        eyes.append(ec)

    # ---- mouth (open smile) & blush --------------------------------------------------------
    pts = []
    for i in range(15):
        t = i / 14
        x = -0.075 + 0.15 * t
        z = 1.345 - 0.032 * math.sin(t * PI)
        p, n = surf_front(x, z)
        pts.append(p - n * 0.0)
    # smile line
    tube("Mouth_Line", pts, lambda t: 0.0085 * (0.55 + 0.45 * math.sin(t * PI)), mouth_m, C, ring=10,
         samples=2, cap=True)
    # open part of the mouth: dark half-disc pressed onto the face
    mv, mf = [], []
    for i in range(15):
        t = i / 14
        x = -0.06 + 0.12 * t
        z_top = 1.343 - 0.03 * math.sin(t * PI)
        z_bot = 1.343 - 0.062 * math.sin(t * PI) ** 0.75
        for z in (z_top, z_bot):
            p, n = surf_front(x, z)
            mv.append(tuple(p + n * 0.0015))
    for i in range(14):
        a = i * 2
        mf.append([a, a + 2, a + 3, a + 1])
    mo = obj_from_data("Mouth_Open", mv, mf, mouth_m, C)
    md = mo.modifiers.new("Thick", 'SOLIDIFY')
    md.thickness = 0.003
    md.offset = 0.0
    tv, tf = [], []
    for i in range(11):
        t = i / 10
        x = -0.028 + 0.056 * t
        z_top = 1.297 - 0.006 * math.sin(t * PI)
        z_bot = 1.297 - 0.017 * math.sin(t * PI) ** 0.7
        for z in (z_top, z_bot):
            p, n = surf_front(x, z)
            tv.append(tuple(p + n * 0.0035))
    tf = [[i * 2, i * 2 + 2, i * 2 + 3, i * 2 + 1] for i in range(10)]
    obj_from_data("Tongue", tv, tf, tongue_m, C)
    for s in (-1, 1):
        p, n = surf_front(s * 0.27, 1.385)
        b = sphere(f"Blush_{s}", 0.05, p - n * 0.004, blush_m, C, scale=(1.0, 0.65, 0.12), segs=20, rings=10)
        b.rotation_mode = 'QUATERNION'
        b.rotation_quaternion = n.to_track_quat('Z', 'Y')

    # ---- spots on the mantle ----------------------------------------------------------------
    spots = []
    for k in range(48):
        for _ in range(30):
            a = rnd.uniform(0, 2 * PI)
            z = rnd.uniform(1.55, 2.05)
            o = Vector((0, HEAD_C.y + 0.08, z))
            dirv = Vector((math.cos(a), math.sin(a), rnd.uniform(-0.1, 0.9))).normalized()
            hit = bvh.ray_cast(o + dirv * 1.0, -dirv, 2.0)
            if hit[0] is None:
                continue
            p, n = hit[0], hit[1]
            # keep the face and headband zone clear
            if n.y < -0.35 and p.z < 1.85:
                continue
            if 1.66 < p.z < 1.84:
                continue
            break
        r = rnd.uniform(0.012, 0.03)
        sp = sphere(f"Spot_{k}", r, p - n * r * 0.25, spot_m, C, scale=(1, rnd.uniform(0.7, 1.0), 0.3), segs=12,
                    rings=6)
        sp.rotation_mode = 'QUATERNION'
        sp.rotation_quaternion = n.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), rnd.uniform(0, PI))
        spots.append(sp)
    bpy.context.view_layer.update()
    join(spots, "Octo_Spots")

    # ---- hachimaki (twisted headband) --------------------------------------------------------
    band_pts = []
    nb = 72
    tilt = 0.10
    for i in range(nb):
        a = 2 * PI * i / nb
        dirv = Vector((math.cos(a), math.sin(a), 0))
        zc = 1.745 + tilt * (math.sin(a) * 0.5 + 0.0)  # higher at the back
        o = Vector((0, HEAD_C.y + 0.07, zc))
        hit = bvh.ray_cast(o + dirv * 1.0, -dirv, 2.0)
        p, n = hit[0], hit[1]
        band_pts.append(p + n * 0.012)
    pts = catmull(band_pts + band_pts[:1], 3)
    radii = [0.03] * len(pts)

    def twist_fn(i, k, a):
        return 0.78 + 0.22 * abs(math.sin(a + i * 0.55))

    v, f, T, N = tube_data(pts, radii, 14, normals=[(p - Vector((0, HEAD_C.y + 0.07, p.z))) for p in pts],
                           cap_start=False, cap_end=False, radial_fn=twist_fn)
    hb = obj_from_data("Hachimaki", v, f, band_m, C)
    hb.scale = (1.0, 1.0, 1.0)
    # knot at the front-left with two upturned ends
    ka = math.radians(208)
    dirv = Vector((math.cos(ka), math.sin(ka), 0))
    o = Vector((0, HEAD_C.y + 0.07, 1.745 + tilt * math.sin(ka) * 0.5))
    hit = bvh.ray_cast(o + dirv, -dirv, 2.0)
    kp, kn = hit[0], hit[1]
    knot = sphere("Hachimaki_Knot", 0.05, kp + kn * 0.03, band_m, C, scale=(1.0, 0.75, 0.8), segs=20, rings=12)
    knot.rotation_euler = kn.to_track_quat('Y', 'Z').to_euler()
    side = kn.cross(Vector((0, 0, 1))).normalized()
    upk = side.cross(kn).normalized()
    for s, ang in enumerate((0.75, -0.55)):
        dirr = (side * math.cos(ang) * (1 if s == 0 else -1) + upk * math.sin(abs(ang)) *
                (1 if s == 0 else -0.6)).normalized()
        e0 = kp + kn * 0.035
        e1 = e0 + dirr * 0.045 + kn * 0.025
        e2 = e0 + dirr * 0.095 + kn * 0.03 - upk * 0.012
        pts = catmull([e0, e1, e2], 6)
        radii = [0.026 * (1.0 - 0.25 * (i / (len(pts) - 1))) for i in range(len(pts))]

        def flat(i, k, a):
            return 1.0 / math.sqrt((math.cos(a) / 0.38) ** 2 + math.sin(a) ** 2)

        v, f, _, _ = tube_data(pts, radii, 12, normals=[kn] * len(pts), radial_fn=flat)
        obj_from_data(f"Hachimaki_End_{s}", v, f, band_m, C)

    # ---- tentacles ------------------------------------------------------------------------------
    sucker_v, sucker_f = lathe_data([(0.0, -0.25), (1.0, -0.25), (1.08, 0.1), (1.0, 0.32), (0.72, 0.4),
                                     (0.5, 0.28), (0.42, 0.05), (0.0, 0.0)], segs=12)
    root_c = Vector((0.0, HEAD_C.y, 1.21))

    def root(angle_deg, r=0.12):
        a = math.radians(angle_deg)
        return root_c + Vector((math.cos(a) * r, math.sin(a) * r, 0))

    def wrap(axis_p0, axis_p1, t0, rad, turns, a0, n=12, ref=None):
        a = Vector(axis_p0).lerp(Vector(axis_p1), t0)
        ax = (Vector(axis_p1) - Vector(axis_p0)).normalized()
        span = (Vector(axis_p1) - Vector(axis_p0)).length
        pitch = rad * 1.9
        pts = helix(a, ax, rad, turns, a0, pitch, n, ref=ref)
        hints = [(p - (a + ax * (p - a).dot(ax))).normalized() for p in pts]
        return pts, hints

    tentacles = []
    up = Vector((0, 0, 1))

    def T(name, ctrl, hints, r0=0.085, r1=0.010, power=1.05):
        tentacles.append((name, ctrl, hints, r0, r1, power))

    # r2: ladle in the stock pot
    lad_mid, lad_top = K.get('ladle', (Vector((-0.55, 0.16, 1.46)), Vector((-0.40, 0.33, 1.68))))
    lad_bot = lad_mid * 2 - lad_top
    rt = root(-157.5)
    wp, wh = wrap(lad_bot, lad_top, 0.66, 0.036, 1.7, 2.2, n=14, ref=(0, 0, 1))
    ctrl = [rt, rt + Vector((-0.12, -0.02, -0.02)), Vector((-0.34, 0.58, 1.22)), Vector((-0.44, 0.48, 1.42)),
            wp[0].lerp(Vector((-0.44, 0.48, 1.42)), 0.4)] + wp
    hints = [up, up, up, up, wh[0]] + wh
    T("Tentacle_Ladle", ctrl, hints)

    # r0: knife on the cutting board
    kh0, kh1 = K.get('knife', (Vector((-0.17, 0.05, 1.03)), Vector((-0.05, 0.1, 1.07))))
    rt = root(-112.5)
    wp, wh = wrap(kh1, kh0, 0.25, 0.034, 1.5, 0.5, n=12, ref=(0, 0, 1))
    ctrl = [rt, rt + Vector((-0.02, -0.12, -0.03)), Vector((-0.07, 0.40, 1.10)), Vector((-0.06, 0.27, 1.12)),
            wp[0] + Vector((0.02, 0.06, 0.03))] + wp
    hints = [up, up, up, up, wh[0]] + wh
    T("Tentacle_Knife", ctrl, hints)

    # r1: serving the finished bowl - drapes over the counter lip and hugs the bowl's base
    hero = K.get('hero', Vector((0.08, -0.5, 1.055)))
    rt = root(-67.5)
    ring = []
    rh = []
    for i in range(13):
        a = math.radians(-20 + i * 15)
        rr = 0.142 - 0.004 * i
        p = hero + Vector((math.cos(a) * rr, math.sin(a) * rr, 0.034 + 0.0015 * i))
        ring.append(p)
        rh.append(Vector((math.cos(a), math.sin(a), 0.8)).normalized())
    ctrl = [rt, rt + Vector((0.05, -0.12, -0.02)), Vector((0.17, 0.40, 1.13)), Vector((0.22, 0.17, 1.08)),
            Vector((0.25, -0.10, 1.10)), Vector((0.27, -0.30, 1.11)), Vector((0.25, -0.50, 1.10))] + ring
    hints = [up, up, up, up, up, up, up] + rh
    T("Tentacle_Serve", ctrl, hints, r0=0.088, r1=0.011, power=1.15)

    # r3: lifting the noodle strainer
    rim, tip, hdir = K.get('tebo', (Vector((0.33, -0.05, 1.33)), Vector((0.58, 0.18, 1.53)),
                                    Vector((0.6, 0.54, 0.6))))
    start = tip - hdir * 0.34
    rt = root(-22.5)
    wp, wh = wrap(start, tip, 0.5, 0.036, 1.6, 3.5, n=14, ref=(0, 0, 1))
    ctrl = [rt, rt + Vector((0.12, -0.04, 0.0)), Vector((0.36, 0.62, 1.26)), Vector((0.50, 0.46, 1.40)),
            wp[0].lerp(Vector((0.50, 0.46, 1.40)), 0.35)] + wp
    hints = [up, up, up, up, wh[0]] + wh
    T("Tentacle_Tebo", ctrl, hints)

    # r5: waving hello, curled tip raised beside the head
    rt = root(22.5)
    curl_c = Vector((0.74, 0.80, 2.0))
    curl = []
    ch = []
    for i in range(14):
        t = i / 13
        a = PI * 0.9 - t * 2.4 * PI
        r = 0.13 * (1 - t * 0.82)
        curl.append(curl_c + Vector((math.cos(a) * r * 0.9, -0.03 * t, math.sin(a) * r)))
        ch.append(Vector((math.cos(a), 0.0, math.sin(a))))
    ctrl = [rt, rt + Vector((0.12, 0.0, -0.04)), Vector((0.48, 0.85, 1.14)), Vector((0.68, 0.86, 1.36)),
            Vector((0.78, 0.84, 1.58)), Vector((0.68, 0.82, 1.80))] + curl
    hints = [up, up, Vector((-1, 0, 0.6)), Vector((-1, 0, 0.2)), Vector((-1, 0, 0)), Vector((-1, 0, 0))] + ch
    T("Tentacle_Wave", ctrl, hints, r0=0.085, r1=0.009)

    # r4: resting over the back lip on the left, tip curled
    rt = root(157.5)
    curl_c = Vector((-0.86, 0.47, 0.99))
    curl, ch = [], []
    for i in range(12):
        t = i / 11
        a = -PI * 0.5 + t * 2.1 * PI
        r = 0.085 * (1 - t * 0.8)
        curl.append(curl_c + Vector((math.sin(a) * r * 0.3 - 0.02 * t, math.cos(a) * r, math.sin(a) * r)))
        ch.append(Vector((0, math.cos(a), math.sin(a))))
    ctrl = [rt, rt + Vector((-0.12, 0.02, -0.06)), Vector((-0.42, 0.78, 1.0)), Vector((-0.62, 0.55, 1.04)),
            Vector((-0.76, 0.44, 1.02))] + curl
    hints = [up, up, up, up, up] + ch
    T("Tentacle_Rest", ctrl, hints)

    # the chef stands on two stacked beer crates to reach the counter
    crate_m = make_mat("Beer_Crate_Yellow", (0.85, 0.55, 0.03), rough=0.45)
    cz = 0.30
    for ci, (h, rz) in enumerate(((0.31, 0.04), (0.30, -0.07))):
        lattice_crate(f"Chef_Crate_{ci}", (0.0, 0.86, cz), 0.56, 0.40, h, rz, crate_m, C, upside_down=True)
        cz += h
    crate_top = cz  # ~1.0

    # r6, r7: draped over the crate edges, tips coiled flat on the deck
    for nm, ang, outd, sgn in (("Tentacle_Back_L", 112.5, Vector((-0.80, 0.60, 0)), -1),
                               ("Tentacle_Back_R", 67.5, Vector((0.84, 0.54, 0)), 1)):
        rt = root(ang)
        outd = outd.normalized()
        edge = Vector((0.0, 0.86, crate_top)) + Vector((outd.x * 0.30, outd.y * 0.21, 0))
        floor_z = 0.30 + 0.02
        contact = Vector((edge.x, edge.y, floor_z)) + outd * 0.16
        side_t = Vector((-outd.y, outd.x, 0)) * sgn
        ctrl = [rt, rt + outd * 0.10 + Vector((0, 0, -0.06)), edge + Vector((0, 0, 0.07)) - outd * 0.06,
                edge + outd * 0.06 + Vector((0, 0, 0.0)), edge + outd * 0.07 + side_t * 0.08 + Vector((0, 0, -0.2)),
                edge + outd * 0.06 - side_t * 0.04 + Vector((0, 0, -0.45)),
                contact + Vector((0, 0, 0.05))]
        hints = [up, up, up, outd + up, outd, outd, up]
        perp = Vector((-outd.y, outd.x, 0)) * sgn
        cc = contact + outd * 0.11
        a0 = math.atan2(-outd.y, -outd.x)
        for i in range(1, 13):
            t = i / 12
            aa = a0 - sgn * t * 1.7 * PI
            r = 0.11 * (1 - 0.72 * t)
            ctrl.append(cc + Vector((math.cos(aa) * r, math.sin(aa) * r, 0.0)) + Vector((0, 0, 0.01 * t)))
            hints.append(up)
        T(nm, ctrl, hints, power=1.1)

    sucker_count = 0
    tent_objs = []
    for (name, ctrl, hints, r0, r1, power) in tentacles:
        spp = 8
        pts = catmull(ctrl, spp)
        hs = []
        nseg = len(ctrl) - 1
        for i in range(len(pts)):
            s = min(i // spp, nseg - 1)
            f = (i - s * spp) / spp if i < nseg * spp else 1.0
            if i == len(pts) - 1:
                s, f = nseg - 1, 1.0
            hs.append(Vector(hints[s]).lerp(Vector(hints[s + 1]), f))
        # resample by arc length (both points and hints)
        d = [0.0]
        for i in range(1, len(pts)):
            d.append(d[-1] + (pts[i] - pts[i - 1]).length)
        L = d[-1]
        n = max(60, int(L / 0.012))
        rp, rh = [], []
        j = 0
        for k in range(n):
            sd = L * k / (n - 1)
            while j < len(d) - 2 and d[j + 1] < sd:
                j += 1
            seg = max(d[j + 1] - d[j], 1e-9)
            t = min(max((sd - d[j]) / seg, 0), 1)
            rp.append(pts[j].lerp(pts[j + 1], t))
            rh.append(hs[j].lerp(hs[j + 1], t))
        # smooth hints to avoid sudden twists
        for _ in range(6):
            rh = [rh[0]] + [(rh[i - 1] + rh[i] * 2 + rh[i + 1]) / 4 for i in range(1, len(rh) - 1)] + [rh[-1]]
        radii = [r1 + (r0 - r1) * (1 - k / (n - 1)) ** power for k in range(n)]
        # gentle swelling near the root
        radii = [r * (1.0 + 0.12 * math.exp(-((k / (n - 1)) / 0.08) ** 2)) for k, r in enumerate(radii)]
        ring = 16
        v, f, Tn, Nn = tube_data(rp, radii, ring, normals=rh, cap_start=True, cap_end=True)
        ob = obj_from_data(name, v, f, skin, C)
        # vertex colours: dorsal red -> ventral pale
        me = ob.data
        ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
        for i in range(n):
            for k in range(ring):
                a = 2 * PI * k / ring
                vent = _smooth(0.1, -0.85, math.cos(a))
                tfrac = i / (n - 1)
                base = SKIN_MID.lerp(SKIN_TOP, 0.35 * (1 - tfrac))
                c = base.lerp(SKIN_BELLY, vent * 0.9)
                nz = noise.noise(Vector(v[i * ring + k]) * 11.0) * 0.08
                c = c * (1 + nz)
                ca.data[i * ring + k].color = (min(c.x, 1), min(c.y, 1), min(c.z, 1), 1)
        for extra in range(n * ring, len(v)):
            ca.data[extra].color = (*SKIN_MID, 1)
        me.color_attributes.active_color = ca
        tent_objs.append(ob)

        # suckers along the underside, two alternating rows
        sv, sf, scol = [], [], []
        acc = 0.0
        row = 0
        k = int(n * 0.10)
        while k < n - 3:
            tfrac = k / (n - 1)
            r = radii[k]
            Tk = Tn[k]
            Nk = Nn[k]
            Bk = Tk.cross(Nk).normalized()
            ang = PI + (0.42 if row % 2 == 0 else -0.42)
            dirv = (Nk * math.cos(ang) + Bk * math.sin(ang)).normalized()
            cen = rp[k] + dirv * r * 0.86
            sr = r * 0.40
            q = dirv.to_track_quat('Z', 'Y')
            mtx = Matrix.Translation(cen) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((sr, sr, sr * 0.9, 1))
            base_i = len(sv)
            for vv in sucker_v:
                sv.append(tuple(mtx @ Vector(vv)))
            for ff in sucker_f:
                sf.append([base_i + x for x in ff])
            row += 1
            step = max(2, int((r * 0.95) / (L / (n - 1))))
            k += step
            sucker_count += 1
        so = obj_from_data(name + "_Suckers", sv, sf, sucker_m, C)
        me = so.data
        ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
        nvs = len(sucker_v)
        prof_n = 8
        for i in range(len(sv)):
            li = i % nvs
            # inner rim vertices darker
            ri = 0 if li == 0 else (7 if li == nvs - 1 else (li - 1) // 12 + 1)
            dark = ri >= 5
            c = Vector((0.88, 0.47, 0.42)) if dark else Vector((0.99, 0.76, 0.64))
            ca.data[i].color = (*c, 1)
        me.color_attributes.active_color = ca

    return {"head": head, "eyes": eyes, "suckers": sucker_count}
