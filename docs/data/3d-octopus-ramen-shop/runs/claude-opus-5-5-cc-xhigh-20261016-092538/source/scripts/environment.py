# Night street surroundings, lights, world, cameras and render settings.

def emissive_mat(name, color, strength):
    return make_mat(name, tuple(c * 0.15 for c in color), rough=0.5, emit=color, emit_strength=strength)


def add_light(name, kind, loc, energy, color, size=0.1, rot=None, target=None, coll=None, spot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'
        if isinstance(size, (tuple, list)):
            ld.size, ld.size_y = size
        else:
            ld.size = ld.size_y = size
    elif kind in ('POINT', 'SPOT'):
        ld.shadow_soft_size = size
    if kind == 'SPOT' and spot:
        ld.spot_size, ld.spot_blend = spot
    ob = bpy.data.objects.new(name, ld)
    ob.visible_camera = False
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    if target is not None:
        look_at(ob, target)
    return ob


def build_environment(info):
    C = get_coll("Street")
    LC = get_coll("Lights")
    rnd = random.Random(21)

    # ---- ground -----------------------------------------------------------------------------
    asph = asphalt_image("tex_asphalt", (0.075, 0.075, 0.08), 256)
    gm = image_mat("Asphalt_Wet", asph, rough=0.32, spec=0.5)
    # render-only: puddle variation in roughness
    nt = gm.node_tree
    p = principled(gm)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 0.6
    nz.inputs['Detail'].default_value = 4.0
    ramp = nt.nodes.new('ShaderNodeMapRange')
    ramp.inputs['From Min'].default_value = 0.45
    ramp.inputs['From Max'].default_value = 0.6
    ramp.inputs['To Min'].default_value = 0.06
    ramp.inputs['To Max'].default_value = 0.5
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
    nt.links.new(ramp.outputs['Result'], p.inputs['Roughness'])
    ramp["render_only"] = True
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    bmesh.ops.scale(bm, vec=(7.0, 5.0, 1), verts=bm.verts)
    ground = obj_from_bm("Ground", bm, gm, C, smooth=False, loc=(0, 1.2, 0))
    me = ground.data
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (co.x / 2.0, co.y / 2.0)
    # curb + sidewalk behind the cart
    stone = make_mat("Curb_Stone", (0.22, 0.21, 0.2), rough=0.6)
    box_minmax("Curb", (-7.0, 3.0, 0.0), (7.0, 3.18, 0.14), stone, C, bev=0.01)
    box_minmax("Sidewalk", (-7.0, 3.18, 0.0), (7.0, 6.2, 0.13), make_mat("Sidewalk", (0.16, 0.155, 0.15),
                                                                           rough=0.45), C, bev=0.0)
    # painted road line
    paint = make_mat("Road_Paint", (0.75, 0.72, 0.6), rough=0.5)
    for i in range(5):
        x = -6.0 + i * 3.0
        box_minmax(f"Road_Line_{i}", (x, -2.4, 0.0), (x + 1.6, -2.28, 0.004), paint, C, bev=0.0)

    # ---- buildings behind ------------------------------------------------------------------------
    wall_mats = [make_mat("Bldg_A", (0.12, 0.11, 0.105), rough=0.8), make_mat("Bldg_B", (0.17, 0.15, 0.13),
                                                                                     rough=0.85),
                 make_mat("Bldg_C", (0.09, 0.095, 0.11), rough=0.75)]
    win_warm = emissive_mat("Window_Warm", (1.0, 0.62, 0.3), 0.7)
    shop_glow = emissive_mat("Shop_Glow", (1.0, 0.55, 0.25), 0.12)
    win_cool = emissive_mat("Window_Cool", (0.55, 0.75, 1.0), 0.8)
    win_dark = make_mat("Window_Dark", (0.02, 0.025, 0.035), rough=0.1)
    shutter = make_mat("Shutter", (0.17, 0.175, 0.18), rough=0.5, metal=0.6)
    blds = [(-6.5, -3.4, 6.5), (-3.4, -0.6, 5.2), (-0.6, 2.4, 7.5), (2.4, 4.8, 5.8), (4.8, 7.0, 8.0)]
    for bi, (x0, x1, h) in enumerate(blds):
        y0 = 6.2
        box_minmax(f"Building_{bi}", (x0, y0, 0.0), (x1, y0 + 3.0, h), wall_mats[bi % 3], C, bev=0.0)
        # ground floor: shutters / shop front
        if True:
            box_minmax(f"Shutter_{bi}", (x0 + 0.3, y0 - 0.05, 0.13), (x1 - 0.3, y0, 2.4), shutter, C, bev=0.0)
        else:
            box_minmax(f"Shopfront_{bi}", (x0 + 0.3, y0 - 0.05, 0.13), (x1 - 0.3, y0, 2.4),
                       shop_glow if bi == 1 else win_dark, C, bev=0.0)
        # awning / ledge
        box_minmax(f"Ledge_{bi}", (x0, y0 - 0.4, 2.5), (x1, y0, 2.6), wall_mats[(bi + 1) % 3], C, bev=0.0)
        # upper windows
        floors = int((h - 3.0) / 1.6)
        cols = max(1, int((x1 - x0) / 1.1))
        for fl in range(floors):
            for cc in range(cols):
                wx = x0 + (cc + 0.5) * (x1 - x0) / cols
                wz = 3.2 + fl * 1.6
                r = rnd.random()
                m = win_warm if r < 0.35 else (win_cool if r < 0.45 else win_dark)
                box_minmax(f"Win_{bi}_{fl}_{cc}", (wx - 0.35, y0 - 0.03, wz), (wx + 0.35, y0, wz + 0.9), m, C,
                           bev=0.0)
                box_minmax(f"WinSill_{bi}_{fl}_{cc}", (wx - 0.4, y0 - 0.08, wz - 0.06), (wx + 0.4, y0, wz), stone,
                           C, bev=0.0)
    # vertical neon-ish shop signs
    sign_specs = [(-2.2, "居酒屋", (1.0, 0.25, 0.2)), (3.4, "喫茶", (0.3, 0.8, 1.0)), (-5.2, "銭湯", (1.0, 0.75, 0.3))]
    for i, (x, word, col) in enumerate(sign_specs):
        board = box_minmax(f"Street_Sign_{i}", (x - 0.22, 6.0, 2.9), (x + 0.22, 6.12, 4.5),
                           make_mat(f"Street_Sign_Bg_{i}", (0.03, 0.03, 0.035), rough=0.4), C, bev=0.01)
        vt = vertical_text(f"Street_Sign_Text_{i}", word, 0.3, spacing=1.15,
                           mat=make_mat(f"Street_Sign_Ink_{i}", col, rough=0.5, emit=col, emit_strength=6.0),
                           coll=C, bold=0.01)
        vt.rotation_euler = (PI / 2, 0, 0)
        vt.location = (x, 5.995, 3.7)

    # ---- vending machine ----------------------------------------------------------------------------
    vm_body = make_mat("Vending_Body", (0.85, 0.1, 0.08), rough=0.35, coat=0.4)
    vm_panel = emissive_mat("Vending_Panel", (0.85, 0.92, 1.0), 4.0)
    vx, vy = -3.3, 5.6
    box_minmax("Vending_Machine", (vx - 0.5, vy - 0.4, 0.13), (vx + 0.5, vy + 0.4, 1.95), vm_body, C, bev=0.02)
    box_minmax("Vending_Panel", (vx - 0.42, vy - 0.42, 0.95), (vx + 0.42, vy - 0.39, 1.82), vm_panel, C, bev=0.0)
    drink_cols = [(0.9, 0.1, 0.1), (0.1, 0.4, 0.9), (0.95, 0.8, 0.1), (0.2, 0.7, 0.3), (0.95, 0.95, 0.95),
                  (0.4, 0.2, 0.1)]
    for row in range(3):
        for col in range(6):
            dx = vx - 0.34 + col * 0.136
            dz = 1.05 + row * 0.26
            cm = make_mat(f"Drink_{(row * 6 + col) % 6}", drink_cols[(row * 6 + col + row) % 6], rough=0.3)
            cylinder(f"Drink_{row}_{col}", 0.03, 0.12, (dx, vy - 0.44, dz + 0.06), cm, C, segs=12)
    box_minmax("Vending_Slot", (vx - 0.3, vy - 0.43, 0.3), (vx + 0.3, vy - 0.39, 0.5),
               make_mat("Vending_Slot", (0.02, 0.02, 0.02), rough=0.4), C, bev=0.0)
    add_light("Vending_Glow", 'AREA', (vx, vy - 0.6, 1.4), 60.0, (0.8, 0.9, 1.0), size=(0.8, 0.9),
              target=(vx, vy - 3.0, 0.6), coll=LC)

    # ---- utility pole + wires ---------------------------------------------------------------------
    pole_m = make_mat("Concrete_Pole", (0.42, 0.41, 0.39), rough=0.8)
    cylinder("Utility_Pole", 0.13, 9.0, (3.6, 4.2, 4.5), pole_m, C, segs=20, r2=0.10)
    box_minmax("Pole_Arm", (2.9, 4.15, 7.6), (4.3, 4.25, 7.7), pole_m, C, bev=0.0)
    wire_m = make_mat("Wire", (0.02, 0.02, 0.02), rough=0.6)
    for k, (dz, sag) in enumerate(((7.65, 0.5), (7.3, 0.6), (7.0, 0.7))):
        pts = []
        for i in range(21):
            t = i / 20
            x = -8.0 + 16.0 * t
            # anchored at the pole
            dist = abs(x - 3.6) / 11.6
            pts.append(Vector((x, 4.2 + 0.6 * (t - 0.5), dz - sag * (1 - (1 - dist) ** 2) * 0.8)))
        tube(f"Wire_{k}", pts, 0.012, wire_m, C, ring=6, samples=2)
    # street lamp on the pole
    lamp_m = emissive_mat("Street_Lamp", (0.75, 0.85, 1.0), 6.0)
    sphere("Street_Lamp_Bulb", 0.12, (3.0, 3.95, 5.1), lamp_m, C, scale=(1.6, 1.0, 0.5))
    box_minmax("Street_Lamp_Arm", (3.0, 3.9, 5.15), (3.6, 4.0, 5.22), pole_m, C, bev=0.0)

    # ---- small street props --------------------------------------------------------------------------
    crate_m = bpy.data.materials.get("Beer_Crate_Yellow") or make_mat("Beer_Crate_Yellow", (0.85, 0.55, 0.03),
                                                                             rough=0.45)
    for k, (x, y, z, rz) in enumerate(((1.95, 1.0, 0.0, 0.2), (1.95, 1.0, 0.3, 0.25), (2.0, 0.35, 0.0, -0.1))):
        lattice_crate(f"Crate_{k}", (x, y, z), 0.45, 0.32, 0.3, rz, crate_m, C)
    # bottles in top crate
    for i in range(4):
        for j in range(3):
            cylinder(f"Crate_Bottle_{i}_{j}", 0.03, 0.2, (1.95 - 0.16 + i * 0.105, 1.0 - 0.09 + j * 0.09, 0.62),
                     bpy.data.materials["Beer_Bottle"], C, segs=10)
    # bucket and stacked bowls rack at the back-left
    bucket_m = make_mat("Bucket_Blue", (0.1, 0.25, 0.6), rough=0.4)
    lathe("Bucket", [(0.0, 0.0), (0.16, 0.0), (0.2, 0.32), (0.21, 0.33), (0.19, 0.33), (0.155, 0.02), (0.0, 0.02)],
          (-1.6, 1.75, 0.0), bucket_m, C, segs=28)
    cylinder("Bucket_Water", 0.185, 0.005, (-1.6, 1.75, 0.27), bpy.data.materials["Boiling_Water"], C, segs=28)
    # a propane tank behind the cart (fuel for the burners)
    tank_m = make_mat("Gas_Tank", (0.85, 0.85, 0.82), rough=0.35, coat=0.3)
    lathe("Gas_Tank", [(0.0, 0.0), (0.15, 0.0), (0.16, 0.05), (0.16, 0.5), (0.13, 0.58), (0.05, 0.62),
                       (0.05, 0.68), (0.0, 0.68)], (1.75, 1.75, 0.0), tank_m, C, segs=28)
    tube("Gas_Hose", [(1.75, 1.75, 0.66), (1.6, 1.6, 0.5), (1.45, 1.4, 0.3), (1.32, 1.2, 0.35)], 0.012,
         bpy.data.materials["Rubber"], C, ring=8, samples=6)

    # ---- world ------------------------------------------------------------------------------------------
    w = bpy.context.scene.world
    if w is None:
        w = bpy.data.worlds.new("World")
        bpy.context.scene.world = w
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.035, 0.03, 0.05, 1)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (0.006, 0.009, 0.025, 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # ---- lights -------------------------------------------------------------------------------------------
    B = info["booth"]
    for i, (x, y, z) in enumerate(B["lanterns"]):
        add_light(f"Lantern_Light_{i}", 'POINT', (x, y, z), 30.0, (1.0, 0.38, 0.16), size=0.1, coll=LC)
    for i, p in enumerate(B["bulbs"]):
        add_light(f"Bulb_Light_{i}", 'POINT', tuple(p), 40.0, (1.0, 0.72, 0.42), size=0.03, coll=LC)
    # soft warm key under the roof onto the chef and counter
    add_light("Key_Under_Roof", 'AREA', (-0.2, -0.5, 2.25), 60.0, (1.0, 0.78, 0.55), size=(2.0, 0.3),
              target=(0.0, 0.3, 1.25), coll=LC)
    # frontal soft fill (street glow)
    fill = add_light("Fill_Street", 'AREA', (-2.0, -4.0, 2.0), 32.0, (0.55, 0.65, 1.0), size=(3.0, 2.0),
                     target=(0.0, 0.4, 1.3), coll=LC)
    fill.data.use_shadow = False
    # cool moonlight rim from behind
    add_light("Rim_Moon", 'AREA', (2.8, 3.8, 4.2), 500.0, (0.45, 0.6, 1.0), size=(1.5, 1.5),
              target=(0.0, 0.8, 1.6), coll=LC)
    add_light("Rim_Moon_L", 'AREA', (-3.2, 3.0, 3.2), 180.0, (0.5, 0.62, 1.0), size=(1.2, 1.2),
              target=(-0.4, 0.8, 1.5), coll=LC)
    # street lamp spill
    add_light("Street_Lamp_Light", 'SPOT', (3.0, 3.95, 5.0), 900.0, (0.75, 0.85, 1.0), size=0.2,
              rot=(0, 0, 0), target=(2.5, 2.5, 0.0), coll=LC, spot=(1.4, 0.6))
    # sign light: small warm spot from the eave up onto the roof sign
    add_light("Sign_Spot", 'SPOT', (0.0, -1.25, 2.55), 60.0, (1.0, 0.78, 0.5), size=0.05,
              target=(0.0, -0.22, 3.0), coll=LC, spot=(0.9, 0.5))
    # warm low spill on the cart front / stools (lantern bounce)
    add_light("Front_Spill", 'SPOT', (0.0, -2.6, 1.4), 110.0, (1.0, 0.55, 0.3), size=0.6,
              target=(0.0, -0.4, 0.55), coll=LC, spot=(1.25, 0.7))
    # soft face key for the chef (motivated by the left bulb)
    add_light("Face_Key", 'SPOT', (-0.9, -0.9, 2.05), 45.0, (1.0, 0.76, 0.5), size=0.25,
              target=(0.0, 0.5, 1.5), coll=LC, spot=(0.55, 0.8))
    # inside-kitchen glow (from burners / boiler)
    add_light("Kitchen_Glow", 'POINT', (0.0, 0.1, 1.25), 25.0, (1.0, 0.6, 0.3), size=0.3, coll=LC)
    return {}


def setup_render(engine='CYCLES', samples=128, res=(1600, 1000)):
    s = bpy.context.scene
    s.render.engine = engine
    if engine == 'CYCLES':
        s.cycles.device = 'GPU'
        s.cycles.samples = samples
        s.cycles.use_denoising = True
        s.cycles.use_adaptive_sampling = True
        s.cycles.max_bounces = 8
        s.cycles.transparent_max_bounces = 16
        s.cycles.volume_bounces = 0
    s.render.resolution_x, s.render.resolution_y = res
    s.render.resolution_percentage = 100
    s.view_settings.view_transform = 'AgX'
    try:
        s.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    s.view_settings.exposure = 0.0


def make_camera(name, loc, target, lens=40, fstop=None, focus=None):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, cd)
        get_coll("Cameras").objects.link(ob)
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 100
    ob.location = loc
    look_at(ob, target)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = (Vector(focus or target) - Vector(loc)).length
    else:
        cd.dof.use_dof = False
    return ob
