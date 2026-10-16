# The ramen yatai (street cart booth): cart body, counter, posts, tiled roof, noren,
# lanterns, menu tags, stools, wheels.
# Expects lib.py and textures.py to be exec'd into the same namespace.

def build_booth():
    C = get_coll("Booth")
    rnd = random.Random(11)

    # ---- materials -------------------------------------------------------
    img_wood_l = wood_image("tex_wood_light", (0.62, 0.42, 0.24), (0.42, 0.25, 0.12), 512, rings=44, seed=1)
    img_wood_m = wood_image("tex_wood_mid", (0.42, 0.24, 0.11), (0.24, 0.12, 0.05), 256, rings=40, seed=2)
    img_wood_d = wood_image("tex_wood_dark", (0.17, 0.09, 0.045), (0.08, 0.04, 0.02), 256, rings=36, seed=3)
    img_cnt = wood_image("tex_wood_counter", (0.66, 0.40, 0.19), (0.45, 0.24, 0.10), 512, rings=50, seed=4, knots=3)
    M = {}
    M['wood_l'] = image_mat("Wood_Light", img_wood_l, rough=0.6, bump=0.05)
    M['wood_m'] = image_mat("Wood_Mid", img_wood_m, rough=0.55, bump=0.05)
    M['wood_d'] = image_mat("Wood_Dark", img_wood_d, rough=0.5, bump=0.04)
    M['counter'] = image_mat("Wood_Counter", img_cnt, rough=0.28, coat=0.6, bump=0.03)
    M['steel'] = make_mat("Steel", (0.75, 0.75, 0.76), rough=0.28, metal=1.0)
    M['steel_dark'] = make_mat("Steel_Dark", (0.35, 0.35, 0.37), rough=0.4, metal=1.0)
    M['tile'] = make_mat("Roof_Tile", (0.11, 0.12, 0.14), rough=0.35, coat=0.3)
    M['tile_edge'] = make_mat("Roof_Tile_Edge", (0.08, 0.085, 0.10), rough=0.4)
    M['noren'] = image_mat("Noren_Indigo", fabric_image("tex_noren", (0.045, 0.09, 0.26)), rough=0.9, spec=0.2)
    M['noren_txt'] = make_mat("Noren_Text", (0.92, 0.9, 0.85), rough=0.9, spec=0.2)
    M['lantern'] = image_mat("Lantern_Paper", paper_image("tex_lantern", (0.95, 0.16, 0.06)), rough=0.7,
                             emit_image=True, emit_strength=2.5)
    M['black'] = make_mat("Black_Lacquer", (0.02, 0.02, 0.02), rough=0.3)
    M['ink'] = make_mat("Ink", (0.02, 0.015, 0.01), rough=0.8)
    M['red'] = make_mat("Red_Lacquer", (0.55, 0.04, 0.03), rough=0.3, coat=0.4)
    M['rope'] = make_mat("Rope", (0.55, 0.45, 0.3), rough=0.9)
    M['bulb'] = make_mat("Bulb", (1.0, 0.8, 0.5), rough=0.2, emit=(1.0, 0.72, 0.38), emit_strength=25.0)
    M['tag'] = image_mat("Menu_Tag", img_wood_l, rough=0.6)
    M['sign'] = image_mat("Sign_Board", img_cnt, rough=0.45, coat=0.3)
    M['rubber'] = make_mat("Rubber", (0.03, 0.03, 0.03), rough=0.8)
    M['cushion'] = make_mat("Stool_Cushion", (0.55, 0.06, 0.04), rough=0.55, coat=0.2)

    def wbox(name, mn, mx, mat, bev=0.006, scale=0.7):
        ob = box_minmax(name, mn, mx, mat, C, bev=bev)
        box_uv(ob, scale)
        return ob

    # ---- cart body ---------------------------------------------------------
    # chassis deck (chef stands on it)
    wbox("Cart_Deck", (-1.32, -0.34, 0.22), (1.32, 1.36, 0.30), M['wood_m'])
    for y in (-0.25, 0.55, 1.28):
        wbox(f"Cart_Beam_{y}", (-1.36, y - 0.05, 0.14), (1.36, y + 0.05, 0.22), M['wood_d'])
    # kitchen cabinet
    wbox("Cabinet", (-1.3, -0.32, 0.30), (1.3, 0.36, 0.92), M['wood_d'])
    # front slats facing customers
    n = 17
    w = 2.6 / n
    for i in range(n):
        x0 = -1.3 + i * w
        ob = wbox(f"Front_Slat_{i:02d}", (x0 + 0.004, -0.345, 0.32), (x0 + w - 0.004, -0.32, 1.0),
                  M['wood_l'] if i % 2 == 0 else M['wood_m'], bev=0.004)
    # horizontal rails across slats
    wbox("Front_Rail_Low", (-1.32, -0.37, 0.36), (1.32, -0.34, 0.42), M['wood_d'])
    wbox("Front_Rail_Mid", (-1.32, -0.37, 0.70), (1.32, -0.34, 0.75), M['wood_d'])
    # side panels
    for s in (-1, 1):
        wbox(f"Side_Panel_{s}", (s * 1.3 - 0.02 if s > 0 else -1.32, -0.34, 0.30),
             (1.32 if s > 0 else -1.3 + 0.02, 0.36, 0.98), M['wood_m'])
    # stainless work surface
    box_minmax("Work_Surface", (-1.29, -0.31, 0.92), (1.29, 0.36, 0.935), M['steel'], C, bev=0.003)
    # back lip of kitchen (chef side)
    wbox("Back_Lip", (-1.3, 0.34, 0.92), (1.3, 0.38, 0.97), M['wood_d'])
    # customer counter plank + brackets
    wbox("Counter_Top", (-1.5, -0.76, 1.0), (1.5, -0.26, 1.055), M['counter'], bev=0.01, scale=0.6)
    wbox("Counter_Lip", (-1.3, -0.34, 0.92), (1.3, -0.26, 1.0), M['wood_d'])
    for x in (-1.15, -0.4, 0.4, 1.15):
        bm = bmesh.new()
        vs = [bm.verts.new(p) for p in ((0, -0.345, 0.70), (0, -0.345, 0.995), (0, -0.66, 0.995))]
        f = bm.faces.new(vs)
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        ext = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=ext, vec=(0.05, 0, 0))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = obj_from_bm(f"Counter_Bracket_{x}", bm, M['wood_d'], C, smooth=False, loc=(x - 0.025, 0, 0))
        box_uv(ob, 0.7)

    # ---- wheels ------------------------------------------------------------
    for s in (-1, 1):
        cx, cy, cz, R = s * 1.42, 0.55, 0.34, 0.34
        rim = lathe(f"Wheel_Rim_{s}", [(R - 0.045, -0.035), (R, -0.035), (R + 0.004, 0.0), (R, 0.035),
                                        (R - 0.045, 0.035), (R - 0.045, -0.035)],
                    loc=(cx, cy, cz), mat=M['wood_d'], coll=C, segs=48, rot=(0, PI / 2, 0))
        tire = lathe(f"Wheel_Tire_{s}", [(R, -0.03), (R + 0.018, -0.025), (R + 0.022, 0.0), (R + 0.018, 0.025),
                                          (R, 0.03)], loc=(cx, cy, cz), mat=M['steel_dark'], coll=C, segs=48,
                     rot=(0, PI / 2, 0))
        hub = cylinder(f"Wheel_Hub_{s}", 0.06, 0.12, (cx, cy, cz), M['wood_m'], C, segs=20, rot=(0, PI / 2, 0),
                       bev=0.01)
        cap = cylinder(f"Wheel_Cap_{s}", 0.035, 0.13, (cx, cy, cz), M['steel_dark'], C, segs=16,
                       rot=(0, PI / 2, 0))
        for k in range(10):
            a = 2 * PI * k / 10
            d = Vector((0, math.cos(a), math.sin(a)))
            p0 = Vector((cx, cy, cz)) + d * 0.05
            p1 = Vector((cx, cy, cz)) + d * (R - 0.04)
            sp = tube(f"Wheel_Spoke_{s}_{k}", [p0, p1], 0.017, M['wood_m'], C, ring=8, samples=1)

    # ---- posts & beams --------------------------------------------------------
    post_xy = [(-1.27, -0.22), (1.27, -0.22), (-1.27, 1.27), (1.27, 1.27)]
    for i, (x, y) in enumerate(post_xy):
        z0 = 0.935 if y < 0 else 0.30
        wbox(f"Post_{i}", (x - 0.04, y - 0.04, z0), (x + 0.04, y + 0.04, 2.52), M['wood_m'], bev=0.008)
    # side beams (front-back) and front/back beams
    for s in (-1, 1):
        wbox(f"Side_Beam_{s}", (s * 1.27 - 0.045, -0.95, 2.40), (s * 1.27 + 0.045, 1.55, 2.50), M['wood_d'])
    wbox("Front_Beam", (-1.6, -0.97, 2.36), (1.6, -0.89, 2.48), M['wood_d'])
    wbox("Back_Beam", (-1.6, 1.47, 2.40), (1.6, 1.55, 2.50), M['wood_d'])
    wbox("Mid_Beam", (-1.6, 0.25, 2.42), (1.6, 0.33, 2.52), M['wood_d'])
    wbox("Menu_Bar", (-1.3, 1.24, 2.33), (1.3, 1.28, 2.37), M['wood_d'])

    # ---- tiled roof (kawara) ------------------------------------------------------
    ridge_y, ridge_z = 0.30, 2.86
    eaves = {-1: (-1.12, 2.46), 1: (1.70, 2.50)}
    tiles = []
    for side, (ey, ez) in eaves.items():
        # sloped board
        p_r = Vector((0, ridge_y, ridge_z))
        p_e = Vector((0, ey, ez))
        L = (p_e - p_r).length
        ang = math.atan2(ez - ridge_z, abs(ey - ridge_y))
        board = box(f"Roof_Board_{side}", (3.5, L, 0.04), ((p_r + p_e) / 2) - Vector((0, 0, 0.03)),
                    M['wood_d'], C, rot=(ang if side > 0 else -ang, 0, 0), bev=0.005)
        box_uv(board, 0.7)
        # rows of half-round tiles running down the slope
        nx = 26
        dirv = (p_e - p_r).normalized()
        for i in range(nx + 1):
            x = -1.72 + i * (3.44 / nx)
            a = p_r + Vector((x, 0, 0)) + Vector((0, 0, 0.0))
            b = p_e + Vector((x, 0, 0)) + dirv * 0.03
            # half cylinder along slope (convex up)
            prof = []
            segs = 8
            r = 0.062
            nrm = Vector((0, 0, 1)) - Vector((0, 0, 1)).dot(dirv) * dirv
            nrm.normalize()
            side_v = dirv.cross(nrm).normalized()
            verts, faces = [], []
            nl = 10
            for j in range(nl + 1):
                t = j / nl
                c = a.lerp(b, t)
                # slight wave between overlapping tiles
                bump = 0.008 * math.sin(t * nl * PI) ** 2
                for k in range(segs + 1):
                    th = PI * k / segs
                    p = c + side_v * math.cos(th) * r + nrm * (math.sin(th) * r * 0.75 + bump)
                    verts.append(tuple(p))
            for j in range(nl):
                for k in range(segs):
                    i0 = j * (segs + 1) + k
                    i1 = i0 + segs + 1
                    faces.append([i0, i1, i1 + 1, i0 + 1])
            ob = obj_from_data(f"Tile_{side}_{i}", verts, faces, M['tile'], C)
            tiles.append(ob)
            # round end cap at the eave
            capo = cylinder(f"TileCap_{side}_{i}", r * 0.8, 0.02, b + nrm * 0.004, M['tile_edge'], C, segs=16, bev=0.004)
            capo.rotation_euler = dirv.to_track_quat('Z', 'Y').to_euler()
            tiles.append(capo)
    roof = join(tiles, "Roof_Tiles")
    # ridge
    ridge = cylinder("Roof_Ridge", 0.09, 3.6, (0, ridge_y, ridge_z + 0.04), M['tile_edge'], C, segs=20,
                     rot=(0, PI / 2, 0))
    ridge.scale = (1.0, 1.0, 1.0)
    box_minmax("Roof_Ridge_Base", (-1.8, ridge_y - 0.1, ridge_z - 0.02), (1.8, ridge_y + 0.1, ridge_z + 0.05),
               M['tile_edge'], C, bev=0.01)
    for s in (-1, 1):
        oni = sphere(f"Ridge_End_{s}", 0.13, (s * 1.8, ridge_y, ridge_z + 0.08), M['tile_edge'], C,
                     scale=(0.5, 1.0, 0.9))
    # fascia boards along eaves
    for side, (ey, ez) in eaves.items():
        wbox(f"Fascia_{side}", (-1.78, ey - 0.03, ez - 0.10), (1.78, ey + 0.03, ez + 0.0), M['wood_d'])

    # ---- shop sign on the roof -----------------------------------------------
    sign = wbox("Shop_Sign", (-0.62, -0.24, 2.80), (0.62, -0.19, 3.18), M['sign'], bev=0.012, scale=0.6)
    box_minmax("Shop_Sign_Frame", (-0.66, -0.20, 2.77), (0.66, -0.17, 3.21), M['red'], C, bev=0.01)
    for s in (-1, 1):
        wbox(f"Sign_Leg_{s}", (s * 0.5 - 0.03, -0.18, 2.6), (s * 0.5 + 0.03, -0.14, 2.82), M['wood_d'])
    t = text_obj("Sign_Text", "たこ亭", 0.29, (0, -0.245, 2.975), mat=M['ink'], coll=C, extrude=0.004, bold=0.006)

    # ---- noren curtains ---------------------------------------------------------
    chars = ["ラ", "ー", "メ", "ン"]
    pw, gap, top, bot = 0.62, 0.035, 2.38, 1.98
    total = 4 * pw + 3 * gap
    for i, ch in enumerate(chars):
        x0 = -total / 2 + i * (pw + gap)
        xc = x0 + pw / 2

        def cloth_y(x, z, i=i, x0=x0):
            u = (x - x0) / pw
            v = (top - z) / (top - bot)
            return -0.93 + 0.012 * math.sin(u * PI * 3 + i) * v - 0.025 * v * v * (0.6 + 0.4 * math.sin(i * 1.7))

        nxs, nzs = 10, 8
        verts, faces = [], []
        for zi in range(nzs + 1):
            for xi in range(nxs + 1):
                x = x0 + xi / nxs * pw
                z = top - zi / nzs * (top - bot)
                verts.append((x, cloth_y(x, z), z))
        for zi in range(nzs):
            for xi in range(nxs):
                a0 = zi * (nxs + 1) + xi
                faces.append([a0, a0 + 1, a0 + nxs + 2, a0 + nxs + 1])
        ob = obj_from_data(f"Noren_{i}", verts, faces, M['noren'], C)
        sol = ob.modifiers.new("Thick", 'SOLIDIFY')
        sol.thickness = 0.008
        sol.offset = 1.0
        me = ob.data
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                uvl.data[li].uv = (co.x * 2.0, co.z * 2.0)
        # white character printed on the cloth, conformed to its sway
        tme = text_mesh(f"Noren_Char_{i}", ch, 0.36, subdivide=1, bold=0.007)
        for v in tme.vertices:
            x = xc + v.co.x
            z = 2.17 + v.co.y
            v.co = Vector((x, cloth_y(x, z) - 0.006, z))
        tob = bpy.data.objects.new(f"Noren_Char_{i}", tme)
        C.objects.link(tob)
        tme.materials.append(M['noren_txt'])

    # ---- lanterns -----------------------------------------------------------------
    lanterns = []
    for s, text in ((-1, "らーめん"), (1, "たこ亭")):
        cx, cy, cz = s * 1.52, -0.98, 1.98
        Rm, H = 0.17, 0.46
        prof = []
        N = 14
        for k in range(N + 1):
            t = k / N
            z = -H / 2 + t * H
            r = 0.105 + (Rm - 0.105) * math.sin(t * PI) ** 0.7
            prof.append((r, z))
        body = lathe(f"Lantern_{s}", prof, loc=(cx, cy, cz), mat=M['lantern'], coll=C, segs=32)
        # cylindrical uv for paper ribs
        me = body.data
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                uvl.data[li].uv = (math.atan2(co.y, co.x) / (2 * PI) * 3, (co.z + H / 2) / H)
        for zz in (-H / 2, H / 2):
            cap = cylinder(f"Lantern_Cap_{s}_{zz:.2f}", 0.112, 0.05, (cx, cy, cz + zz), M['black'], C, segs=32,
                           bev=0.006)
        tube(f"Lantern_Cord_{s}", [(cx, cy, cz + H / 2 + 0.02), (cx, cy, 2.36)], 0.006, M['rope'], C, ring=6,
             samples=1)
        tube(f"Lantern_Tassel_{s}", [(cx, cy, cz - H / 2 - 0.02), (cx, cy, cz - H / 2 - 0.14)], 0.012,
             M['red'], C, ring=8, samples=1)
        # vertical lettering wrapped on the paper surface, facing the street (-Y)
        vt = vertical_text(f"Lantern_Text_{s}", text, 0.088 if len(text) > 3 else 0.108, spacing=0.98,
                           mat=M['ink'], coll=C, bold=0.004)
        # subdivide then wrap onto the lantern surface
        bm = bmesh.new()
        bm.from_mesh(vt.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
        for v in bm.verts:
            x, zt = v.co.x, v.co.y
            t = (zt + H / 2) / H
            t = min(max(t, 0), 1)
            r = 0.105 + (Rm - 0.105) * math.sin(t * PI) ** 0.7 + 0.003
            a = x / r
            v.co = Vector((r * math.sin(a), -r * math.cos(a), zt))
        bm.to_mesh(vt.data)
        bm.free()
        vt.location = (cx, cy, cz)
        lanterns.append((cx, cy, cz))

    # ---- hanging bulbs under the roof ---------------------------------------------------
    bulbs = []
    for x in (-0.62, 0.62):
        p = Vector((x, -0.38, 2.12))
        sphere(f"Bulb_{x}", 0.045, p, M['bulb'], C, scale=(1, 1, 1.25))
        cylinder(f"Bulb_Socket_{x}", 0.022, 0.05, p + Vector((0, 0, 0.07)), M['black'], C, segs=12)
        tube(f"Bulb_Cord_{x}", [p + Vector((0, 0, 0.09)), Vector((x, -0.38, 2.62))], 0.005, M['black'], C,
             ring=6, samples=1)
        shade = lathe(f"Bulb_Shade_{x}", [(0.02, 0.10), (0.05, 0.085), (0.11, 0.035), (0.125, 0.02),
                                         (0.12, 0.018), (0.045, 0.078), (0.018, 0.092)],
                      loc=p, mat=M['steel_dark'], coll=C, segs=28)
        bulbs.append(p)

    # ---- menu tags hanging behind the chef ---------------------------------------------
    menu = ["醤油", "味噌", "塩", "豚骨", "餃子", "替玉", "煮卵", "ビール"]
    xs = [-1.18, -1.0, -0.82, -0.64, 0.64, 0.82, 1.0, 1.18]
    for i, (word, x) in enumerate(zip(menu, xs)):
        h = 0.36
        tagb = wbox(f"Menu_Tag_{i}", (x - 0.07, 1.215, 2.30 - h), (x + 0.07, 1.235, 2.30), M['tag'],
                    bev=0.004, scale=1.2)
        size = 0.085 if len(word) <= 2 else 0.068
        vt = vertical_text(f"Menu_Text_{i}", word, size, spacing=1.08, mat=M['ink'], coll=C, bold=0.003)
        vt.rotation_euler = (PI / 2, 0, 0)
        vt.location = (x, 1.21, 2.30 - h / 2 + 0.01)
        # red seal stamp at the bottom
    # bar hooks: little strings
    # ---- stools --------------------------------------------------------------------------
    for i, x in enumerate((-0.85, 0.0, 0.85)):
        y = -1.12
        seat = lathe(f"Stool_Seat_{i}", [(0, 0.60), (0.16, 0.60), (0.175, 0.615), (0.18, 0.64), (0.172, 0.66),
                                         (0.15, 0.668), (0, 0.672)], loc=(x, y, 0), mat=M['cushion'], coll=C,
                     segs=32)
        ring = lathe(f"Stool_Frame_{i}", [(0, 0.585), (0.17, 0.585), (0.17, 0.60), (0, 0.60)], loc=(x, y, 0),
                     mat=M['wood_d'], coll=C, segs=32, smooth=False)
        for k in range(4):
            a = PI / 4 + k * PI / 2
            top = Vector((x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, 0.59))
            bot = Vector((x + math.cos(a) * 0.17, y + math.sin(a) * 0.17, 0.0))
            tube(f"Stool_Leg_{i}_{k}", [bot, top], 0.018, M['wood_d'], C, ring=8, samples=1)
        # foot ring
        pts = [Vector((x + math.cos(a) * 0.152, y + math.sin(a) * 0.152, 0.2)) for a in
               [2 * PI * k / 24 for k in range(24)]]
        v, f, _, _ = tube_data(catmull(pts + pts[:1], 2), [0.008] * (len(pts) * 2 + 1), 6,
                               cap_start=False, cap_end=False)
        obj_from_data(f"Stool_Ring_{i}", v, f, M['steel_dark'], C)

    return {"lanterns": lanterns, "bulbs": bulbs, "mats": M}
