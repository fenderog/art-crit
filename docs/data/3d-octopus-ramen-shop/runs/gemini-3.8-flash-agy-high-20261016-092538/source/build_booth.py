import bpy
import bmesh
import math
from mathutils import Vector, Euler
from mesh_utils import create_cube, create_cylinder, create_sphere, create_torus, create_plane, smooth_shade

def build_booth(mats):
    booth_objects = []
    
    # 1. Stone ground platform
    floor = create_cube("Floor_Base", location=(0, 0.4, -0.05), scale=(3.6, 3.2, 0.1), material=mats["StoneFloor"])
    booth_objects.append(floor)
    
    # Curb/border stones around platform
    curb_f = create_cube("Floor_Curb_F", location=(0, -1.2, 0.02), scale=(3.64, 0.08, 0.06), material=mats["WoodTimber"])
    curb_b = create_cube("Floor_Curb_B", location=(0, 2.0, 0.02), scale=(3.64, 0.08, 0.06), material=mats["WoodTimber"])
    curb_l = create_cube("Floor_Curb_L", location=(-1.8, 0.4, 0.02), scale=(0.08, 3.24, 0.06), material=mats["WoodTimber"])
    curb_r = create_cube("Floor_Curb_R", location=(1.8, 0.4, 0.02), scale=(0.08, 3.24, 0.06), material=mats["WoodTimber"])
    booth_objects.extend([curb_f, curb_b, curb_l, curb_r])

    # 2. Main wooden counter
    counter_top = create_cube("Counter_Top", location=(0, -0.15, 0.95), scale=(2.6, 0.62, 0.07), material=mats["WoodCounter"])
    smooth_shade(counter_top)
    booth_objects.append(counter_top)
    
    # Counter front vertical facade
    counter_front = create_cube("Counter_Front", location=(0, -0.43, 0.46), scale=(2.54, 0.05, 0.92), material=mats["WoodPlank"])
    booth_objects.append(counter_front)
    
    # Counter vertical decorative slats
    num_slats = 16
    for i in range(num_slats):
        x = -1.2 + (2.4 / (num_slats - 1)) * i
        slat = create_cube(f"Counter_Slat_{i}", location=(x, -0.45, 0.46), scale=(0.04, 0.025, 0.88), material=mats["WoodTimber"])
        booth_objects.append(slat)
        
    # Counter baseboard
    baseboard = create_cube("Counter_Baseboard", location=(0, -0.45, 0.04), scale=(2.56, 0.06, 0.08), material=mats["WoodTimber"])
    booth_objects.append(baseboard)
    
    # Brass footrest rail
    foot_rail = create_cylinder("Foot_Rail", location=(0, -0.65, 0.20), radius=0.022, depth=2.5, rotation=(0, math.pi/2, 0), material=mats["Brass"])
    smooth_shade(foot_rail)
    booth_objects.append(foot_rail)
    
    # Footrest supports
    for x in [-1.0, -0.35, 0.35, 1.0]:
        post = create_cylinder(f"Rail_Support_{x}", location=(x, -0.55, 0.20), radius=0.015, depth=0.22, rotation=(math.pi/2, 0, 0), material=mats["Brass"])
        smooth_shade(post)
        booth_objects.append(post)

    # 3. Back prep station & counter
    back_top = create_cube("Back_Counter_Top", location=(0, 0.95, 0.86), scale=(2.5, 0.52, 0.06), material=mats["WoodTimber"])
    back_cabinet = create_cube("Back_Cabinet", location=(0, 0.95, 0.42), scale=(2.46, 0.48, 0.82), material=mats["WoodPlank"])
    booth_objects.extend([back_top, back_cabinet])
    
    # Noodle boiling station (left side of back counter)
    noodle_vat = create_cube("Noodle_Cooker", location=(-0.8, 0.95, 0.89), scale=(0.7, 0.42, 0.08), material=mats["StainlessSteel"])
    noodle_water = create_cube("Noodle_Water", location=(-0.8, 0.95, 0.925), scale=(0.64, 0.36, 0.02), material=mats["Broth"])
    booth_objects.extend([noodle_vat, noodle_water])
    
    # 2 spare noodle strainers (tebo) resting in the vat
    for idx, sx in enumerate([-0.95, -0.65]):
        basket = create_cylinder(f"Tebo_Basket_{idx}", location=(sx, 0.95, 0.98), radius=0.07, depth=0.14, material=mats["WireMesh"])
        smooth_shade(basket)
        handle = create_cylinder(f"Tebo_Handle_{idx}", location=(sx, 1.04, 1.15), radius=0.014, depth=0.24, rotation=(-math.pi/6, 0, 0), material=mats["Bamboo"])
        smooth_shade(handle)
        booth_objects.extend([basket, handle])

    # Stockpot for broth (center-left)
    pot = create_cylinder("Broth_Stockpot", location=(-0.25, 0.95, 1.04), radius=0.18, depth=0.32, material=mats["StainlessSteel"])
    smooth_shade(pot)
    pot_soup = create_cylinder("Broth_Soup", location=(-0.25, 0.95, 1.16), radius=0.17, depth=0.04, material=mats["Broth"])
    smooth_shade(pot_soup)
    handle_l = create_torus("Pot_Handle_L", location=(-0.44, 0.95, 1.12), major_radius=0.035, minor_radius=0.008, rotation=(0, math.pi/2, 0), material=mats["StainlessSteel"])
    handle_r = create_torus("Pot_Handle_R", location=(-0.06, 0.95, 1.12), major_radius=0.035, minor_radius=0.008, rotation=(0, math.pi/2, 0), material=mats["StainlessSteel"])
    pot_lid = create_cylinder("Pot_Lid", location=(-0.20, 0.98, 1.22), radius=0.19, depth=0.025, rotation=(0.2, 0.1, 0), material=mats["WoodPlank"])
    smooth_shade(pot_lid)
    booth_objects.extend([pot, pot_soup, handle_l, handle_r, pot_lid])

    # Prep chopping board & knife (center-right)
    board = create_cube("Cutting_Board", location=(0.4, 0.95, 0.91), scale=(0.45, 0.32, 0.04), material=mats["WoodCounter"])
    booth_objects.append(board)
    
    chashu_log = create_cylinder("Chashu_Roll", location=(0.38, 0.92, 0.98), radius=0.06, depth=0.22, rotation=(0, math.pi/2, 0), material=mats["Chashu"], unwrap_caps=True)
    smooth_shade(chashu_log)
    chashu_slice = create_cylinder("Chashu_Cut_Slice", location=(0.54, 0.92, 0.94), radius=0.06, depth=0.015, rotation=(math.pi/2, 0, 0), material=mats["Chashu"], unwrap_caps=True)
    smooth_shade(chashu_slice)
    knife_blade = create_cube("Knife_Blade", location=(0.42, 1.04, 0.94), scale=(0.22, 0.045, 0.005), material=mats["StainlessSteel"])
    knife_handle = create_cylinder("Knife_Handle", location=(0.26, 1.04, 0.94), radius=0.014, depth=0.12, rotation=(0, math.pi/2, 0), material=mats["WoodTimber"])
    smooth_shade(knife_handle)
    booth_objects.extend([chashu_log, chashu_slice, knife_blade, knife_handle])

    # Condiment bowls & bottles on back counter
    negi_bowl = create_cylinder("Negi_Prep_Bowl", location=(0.75, 0.90, 0.93), radius=0.08, depth=0.06, material=mats["BowlWhite"])
    smooth_shade(negi_bowl)
    negi_pile = create_sphere("Negi_Pile", location=(0.75, 0.90, 0.96), radius=0.075, scale=(1.0, 1.0, 0.4), material=mats["Negi"])
    smooth_shade(negi_pile)
    menma_bowl = create_cylinder("Menma_Prep_Bowl", location=(0.95, 0.90, 0.93), radius=0.08, depth=0.06, material=mats["BowlWhite"])
    smooth_shade(menma_bowl)
    menma_pile = create_sphere("Menma_Pile", location=(0.95, 0.90, 0.96), radius=0.075, scale=(1.0, 1.0, 0.4), material=mats["Menma"])
    smooth_shade(menma_pile)
    booth_objects.extend([negi_bowl, negi_pile, menma_bowl, menma_pile])

    # Back wall shelves (two tiers)
    shelf_l1 = create_cube("Shelf_Tier1", location=(0, 1.25, 1.35), scale=(2.5, 0.28, 0.04), material=mats["WoodTimber"])
    shelf_l2 = create_cube("Shelf_Tier2", location=(0, 1.25, 1.70), scale=(2.5, 0.28, 0.04), material=mats["WoodTimber"])
    booth_objects.extend([shelf_l1, shelf_l2])

    # Stacks of clean ramen bowls on Shelf 1
    for stack_idx, sx in enumerate([-0.9, -0.65]):
        for b_idx in range(4):
            sb = create_cylinder(f"Bowl_Stack_{stack_idx}_{b_idx}", location=(sx, 1.25, 1.41 + b_idx * 0.045), radius=0.10, depth=0.05, material=mats["BowlRed"] if (stack_idx + b_idx)%2==0 else mats["BowlBlack"])
            smooth_shade(sb)
            booth_objects.append(sb)

    # Condiment dispensers
    bottles_info = [
        ("Shoyu_Bottle", -0.35, mats["BowlBlack"], mats["BowlRed"]),
        ("Rayu_Bottle", -0.20, mats["BowlWhite"], mats["BowlRed"]),
        ("Su_Bottle", -0.05, mats["BowlWhite"], mats["WoodCounter"]),
    ]
    for b_name, bx, body_m, cap_m in bottles_info:
        b_body = create_cylinder(f"{b_name}_Body", location=(bx, 1.25, 1.45), radius=0.035, depth=0.14, material=body_m)
        smooth_shade(b_body)
        b_spout = create_cylinder(f"{b_name}_Spout", location=(bx, 1.25, 1.54), radius=0.012, depth=0.05, material=cap_m)
        smooth_shade(b_spout)
        booth_objects.extend([b_body, b_spout])

    # Bamboo chopstick holder with sticks
    holder = create_cylinder("Chopstick_Holder", location=(0.6, 1.25, 1.47), radius=0.05, depth=0.16, material=mats["Bamboo"])
    smooth_shade(holder)
    booth_objects.append(holder)
    for c_i in range(8):
        ca = c_i * math.pi / 4.0
        cx = 0.6 + 0.025 * math.cos(ca)
        cy = 1.25 + 0.025 * math.sin(ca)
        stick = create_cylinder(f"Chopstick_Bundle_{c_i}", location=(cx, cy, 1.58), radius=0.004, depth=0.22, rotation=(0.08 * math.sin(ca), 0.08 * math.cos(ca), 0), material=mats["Bamboo"])
        smooth_shade(stick)
        booth_objects.append(stick)

    # Shelf 2 items (casks)
    for j_i, jx in enumerate([-0.8, -0.4, 0.4, 0.8]):
        jar = create_cylinder(f"Sake_Cask_{j_i}", location=(jx, 1.25, 1.83), radius=0.09, depth=0.22, material=mats["WoodPlank"])
        smooth_shade(jar)
        jar_lid = create_cylinder(f"Sake_Cask_Lid_{j_i}", location=(jx, 1.25, 1.95), radius=0.095, depth=0.03, material=mats["WoodTimber"])
        smooth_shade(jar_lid)
        booth_objects.extend([jar, jar_lid])

    # 4. Timber booth structure
    post_coords = [
        ("Post_FL", -1.25, -0.45),
        ("Post_FR", 1.25, -0.45),
        ("Post_BL", -1.25, 1.35),
        ("Post_BR", 1.25, 1.35),
    ]
    for p_name, px, py in post_coords:
        post = create_cube(p_name, location=(px, py, 1.25), scale=(0.11, 0.11, 2.5), material=mats["WoodTimber"])
        smooth_shade(post)
        plinth = create_cube(f"{p_name}_Base", location=(px, py, 0.06), scale=(0.16, 0.16, 0.12), material=mats["StoneFloor"])
        booth_objects.extend([post, plinth])

    # Horizontal lintels & beams
    beam_f = create_cube("Beam_Front", location=(0, -0.45, 2.40), scale=(2.75, 0.12, 0.12), material=mats["WoodTimber"])
    beam_b = create_cube("Beam_Back", location=(0, 1.35, 2.54), scale=(2.75, 0.12, 0.12), material=mats["WoodTimber"])
    beam_l = create_cube("Beam_Left", location=(-1.25, 0.45, 2.47), scale=(0.12, 1.95, 0.12), material=mats["WoodTimber"])
    beam_r = create_cube("Beam_Right", location=(1.25, 0.45, 2.47), scale=(0.12, 1.95, 0.12), material=mats["WoodTimber"])
    smooth_shade(beam_f)
    smooth_shade(beam_b)
    smooth_shade(beam_l)
    smooth_shade(beam_r)
    booth_objects.extend([beam_f, beam_b, beam_l, beam_r])

    # Corner braces
    brace_fl = create_cube("Brace_FL", location=(-1.12, -0.45, 2.28), scale=(0.22, 0.08, 0.08), rotation=(0, math.pi/4, 0), material=mats["WoodTimber"])
    brace_fr = create_cube("Brace_FR", location=(1.12, -0.45, 2.28), scale=(0.22, 0.08, 0.08), rotation=(0, -math.pi/4, 0), material=mats["WoodTimber"])
    booth_objects.extend([brace_fl, brace_fr])

    # Sloped Awning Roof
    roof_angle = math.atan2(2.70 - 2.48, 1.55 - (-0.75))
    roof_main = create_cube("Roof_Subdeck", location=(0, 0.40, 2.60), scale=(2.85, 2.42, 0.05), rotation=(-roof_angle, 0, 0), material=mats["WoodTimber"])
    smooth_shade(roof_main)
    booth_objects.append(roof_main)
    
    num_tiles = 19
    for ti in range(num_tiles):
        tx = -1.35 + (2.70 / (num_tiles - 1)) * ti
        tile_ridge = create_cylinder(f"Roof_Tile_{ti}", location=(tx, 0.40, 2.64), radius=0.038, depth=2.45, rotation=(math.pi/2 - roof_angle, 0, 0), material=mats["RoofTile"])
        smooth_shade(tile_ridge)
        booth_objects.append(tile_ridge)

    roof_fascia = create_cube("Roof_Fascia", location=(0, -0.78, 2.47), scale=(2.9, 0.06, 0.08), material=mats["WoodTimber"])
    smooth_shade(roof_fascia)
    booth_objects.append(roof_fascia)

    sign = create_cube("Shop_Signboard", location=(0, -0.48, 2.56), scale=(1.15, 0.04, 0.20), material=mats["WoodTimber"])
    sign_border = create_cube("Shop_Signboard_Border", location=(0, -0.49, 2.56), scale=(1.19, 0.025, 0.23), material=mats["Brass"])
    booth_objects.extend([sign, sign_border])

    # 5. Raised Noren Fabric Banner (Framing the chef perfectly!)
    noren_pole = create_cylinder("Noren_Pole", location=(0, -0.42, 2.38), radius=0.016, depth=2.5, rotation=(0, math.pi/2, 0), material=mats["Bamboo"])
    smooth_shade(noren_pole)
    booth_objects.append(noren_pole)
    
    # Noren plane hanging from Z=2.38 down to Z=2.10
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -0.43, 2.24), rotation=(math.pi/2, 0, 0))
    noren_obj = bpy.context.active_object
    noren_obj.name = "Noren_Curtain"
    noren_obj.scale = (2.2, 1.0, 0.28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    noren_obj.data.materials.append(mats["Noren"])
    smooth_shade(noren_obj)
    booth_objects.append(noren_obj)

    # 6. Two Hanging Red Chochin Lanterns
    lantern_positions = [("Lantern_L", -1.02, -0.52), ("Lantern_R", 1.02, -0.52)]
    for l_name, lx, ly in lantern_positions:
        string = create_cylinder(f"{l_name}_Cord", location=(lx, ly, 2.28), radius=0.005, depth=0.18, material=mats["LanternBlack"])
        smooth_shade(string)
        cap_top = create_cylinder(f"{l_name}_CapTop", location=(lx, ly, 2.19), radius=0.09, depth=0.04, material=mats["LanternBlack"])
        smooth_shade(cap_top)
        body = create_sphere(f"{l_name}_Body", location=(lx, ly, 2.02), radius=0.16, segments=24, ring_count=18, scale=(1.0, 1.0, 1.40), material=mats["Lantern"])
        smooth_shade(body)
        cap_bot = create_cylinder(f"{l_name}_CapBot", location=(lx, ly, 1.85), radius=0.08, depth=0.035, material=mats["LanternBlack"])
        smooth_shade(cap_bot)
        tassel = create_cylinder(f"{l_name}_Tassel", location=(lx, ly, 1.78), radius=0.016, depth=0.11, material=mats["LanternBlack"])
        smooth_shade(tassel)
        booth_objects.extend([string, cap_top, body, cap_bot, tassel])

        light_data = bpy.data.lights.new(name=f"{l_name}_Light", type='POINT')
        light_data.color = (1.0, 0.42, 0.12)
        light_data.energy = 18.0 # soft warm internal lantern glow
        light_data.shadow_soft_size = 0.15
        light_obj = bpy.data.objects.new(name=f"{l_name}_LightObj", object_data=light_data)
        light_obj.location = (lx, ly, 2.02)
        bpy.context.collection.objects.link(light_obj)
        booth_objects.append(light_obj)

    # 7. Customer Stools
    stool_positions = [("Stool_L", -0.65, -0.85), ("Stool_R", 0.65, -0.85)]
    for s_name, sx, sy in stool_positions:
        seat = create_cylinder(f"{s_name}_Seat", location=(sx, sy, 0.55), radius=0.17, depth=0.045, material=mats["WoodCounter"])
        smooth_shade(seat)
        ring = create_torus(f"{s_name}_Ring", location=(sx, sy, 0.22), major_radius=0.12, minor_radius=0.012, material=mats["WoodTimber"])
        smooth_shade(ring)
        booth_objects.extend([seat, ring])
        for leg_i in range(4):
            la = leg_i * math.pi / 2.0 + math.pi/4.0
            lx = sx + 0.11 * math.cos(la)
            ly = sy + 0.11 * math.sin(la)
            leg = create_cylinder(f"{s_name}_Leg_{leg_i}", location=(lx, ly, 0.27), radius=0.016, depth=0.54, 
                                  rotation=(0.07 * math.sin(la), -0.07 * math.cos(la), 0), material=mats["WoodTimber"])
            smooth_shade(leg)
            booth_objects.append(leg)

    return booth_objects
