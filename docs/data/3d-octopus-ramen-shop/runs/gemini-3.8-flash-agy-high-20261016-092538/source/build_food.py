import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
from mesh_utils import create_cube, create_cylinder, create_sphere, create_torus, create_plane, smooth_shade, unwrap_cylinder_caps

def create_open_ramen_bowl(name, location, scale=1.0, mats=None, outer_mat_name="BowlRed"):
    bm = bmesh.new()
    profile = [
        (0.00, 0.00),
        (0.065, 0.00),
        (0.070, 0.022), # foot outer
        (0.060, 0.022), # foot inner
        (0.075, 0.035), # lower bowl
        (0.115, 0.065), # mid bowl
        (0.148, 0.095), # upper flare
        (0.165, 0.125), # rim top
        (0.155, 0.125), # rim inner
        (0.140, 0.095), # inner mid
        (0.100, 0.060), # inner low
        (0.060, 0.030), # inner bottom
        (0.000, 0.030), # center bottom
    ]
    
    verts = [bm.verts.new(Vector((r * scale, 0, z * scale))) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i+1])) for i in range(len(verts)-1)]
    
    bmesh.ops.spin(
        bm,
        geom=verts + edges,
        angle=2.0 * math.pi,
        steps=32,
        axis=Vector((0, 0, 1)),
        cent=Vector((0, 0, 0))
    )
    
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002 * scale)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    
    obj.data.materials.append(mats[outer_mat_name])
    obj.data.materials.append(mats["BowlWhite"])
    
    for poly in obj.data.polygons:
        poly.use_smooth = True
        if poly.center.z > (0.035 * scale) and poly.normal.z > -0.2 and poly.normal.dot(poly.center) < 0.05:
            poly.material_index = 1
        else:
            poly.material_index = 0
            
    return obj

def create_ramen_egg_half(name, location, rotation=(0, 0, 0), scale=1.0, mats=None):
    bm = bmesh.new()
    profile = [
        (0.000, -0.030),
        (0.015, -0.028),
        (0.028, -0.022),
        (0.036, -0.012),
        (0.038, 0.000), # outer edge of cut face
        (0.035, 0.000), # inner rim
        (0.022, 0.000), # outer yolk boundary
        (0.012, 0.006), # yolk curve
        (0.000, 0.008), # yolk peak
    ]
    
    verts = [bm.verts.new(Vector((r * scale, 0, z * scale))) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i+1])) for i in range(len(verts)-1)]
    
    bmesh.ops.spin(
        bm,
        geom=verts + edges,
        angle=2.0 * math.pi,
        steps=24,
        axis=Vector((0, 0, 1)),
        cent=Vector((0, 0, 0))
    )
    
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001 * scale)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    
    if mats:
        obj.data.materials.append(mats["EggWhite"])
        obj.data.materials.append(mats["EggRim"])
        obj.data.materials.append(mats["EggYolk"])
        
        for poly in obj.data.polygons:
            poly.use_smooth = True
            c = poly.center
            r = math.sqrt(c.x*c.x + c.y*c.y) / scale
            if c.z >= -0.001 * scale:
                if r < 0.023:
                    poly.material_index = 2 # Yolk
                elif r > 0.034:
                    poly.material_index = 1 # Rim
                else:
                    poly.material_index = 0 # White
            else:
                if c.z > -0.005 * scale:
                    poly.material_index = 1 # Outer marinated brown
                else:
                    poly.material_index = 0 # White
                    
    return obj

def build_food(mats):
    food_objects = []
    
    # ==========================================================
    # 1. HERO RAMEN BOWL (Center of front counter: 0.0, -0.05, 0.985)
    # ==========================================================
    bx, by, bz = 0.0, -0.05, 0.985
    hero_bowl = create_open_ramen_bowl("Hero_Bowl", location=(bx, by, bz), scale=1.05, mats=mats, outer_mat_name="BowlRed")
    food_objects.append(hero_bowl)
    
    # Rich golden-amber tonkotsu broth liquid surface
    broth = create_cylinder("Hero_Broth", location=(bx, by, bz + 0.088), radius=0.144, depth=0.008, vertices=28, material=mats["Broth"])
    smooth_shade(broth)
    food_objects.append(broth)
    
    # Floating glossy fat droplets
    oil_spots = [
        (-0.05, 0.035, 0.012), (0.055, -0.05, 0.014), (0.075, 0.03, 0.010),
        (-0.02, -0.07, 0.012), (0.02, 0.065, 0.011), (-0.07, -0.03, 0.010)
    ]
    for oi, (ox, oy, orad) in enumerate(oil_spots):
        oil = create_cylinder(f"Hero_Oil_{oi}", location=(bx + ox, by + oy, bz + 0.093), radius=orad, depth=0.002, vertices=12, material=mats["Brass"])
        smooth_shade(oil)
        food_objects.append(oil)
        
    # Slender wavy ramen noodles (multiple fine curved strands)
    num_strands = 14
    for ni in range(num_strands):
        ang = (ni / num_strands) * 2.0 * math.pi
        rad = 0.03 + 0.065 * ((ni % 4) / 3.0)
        nx = bx + rad * math.cos(ang)
        ny = by + rad * math.sin(ang)
        strand = create_torus(
            f"Hero_Noodle_Strand_{ni}",
            location=(nx, ny, bz + 0.089),
            major_radius=0.025 + 0.008 * (ni % 3),
            minor_radius=0.0042,
            rotation=(0.2 * math.sin(ni), 0.2 * math.cos(ni), ang),
            material=mats["Noodles"]
        )
        smooth_shade(strand)
        food_objects.append(strand)

    # Chashu Pork Slices (2 tender rolled pork belly rounds with remapped UVs)
    chashu1 = create_cylinder(
        "Hero_Chashu_1", 
        location=(bx - 0.058, by + 0.02, bz + 0.100), 
        radius=0.050, 
        depth=0.008, 
        rotation=(0.12, -0.18, 0.35), 
        material=mats["Chashu"],
        unwrap_caps=True
    )
    chashu2 = create_cylinder(
        "Hero_Chashu_2", 
        location=(bx - 0.076, by - 0.035, bz + 0.098), 
        radius=0.048, 
        depth=0.008, 
        rotation=(0.08, -0.22, 0.10), 
        material=mats["Chashu"],
        unwrap_caps=True
    )
    smooth_shade(chashu1)
    smooth_shade(chashu2)
    food_objects.extend([chashu1, chashu2])

    # Ajitsuke Tamago (Halved Marinated Ramen Egg with exposed golden yolk!)
    # Tilted up towards front-left so the camera sees the yolk face directly!
    egg = create_ramen_egg_half(
        "Hero_Egg",
        location=(bx + 0.065, by + 0.025, bz + 0.102),
        rotation=(-0.25, 0.15, -0.4), # tilted towards viewer
        scale=1.0,
        mats=mats
    )
    food_objects.append(egg)

    # Narutomaki (2 slices with distinct pink spiral)
    naruto1 = create_cylinder(
        "Hero_Naruto_1", 
        location=(bx + 0.012, by - 0.052, bz + 0.100), 
        radius=0.034, 
        depth=0.006, 
        rotation=(0.10, 0.15, -0.5), 
        material=mats["Naruto"],
        unwrap_caps=True
    )
    naruto2 = create_cylinder(
        "Hero_Naruto_2", 
        location=(bx - 0.024, by - 0.068, bz + 0.098), 
        radius=0.032, 
        depth=0.006, 
        rotation=(0.08, 0.12, 0.2), 
        material=mats["Naruto"],
        unwrap_caps=True
    )
    smooth_shade(naruto1)
    smooth_shade(naruto2)
    food_objects.extend([naruto1, naruto2])

    # Menma (Seasoned Bamboo Shoot Strips)
    for mi in range(4):
        my_offset = -0.015 + mi * 0.010
        menma_stick = create_cube(f"Hero_Menma_{mi}", location=(bx + 0.076, by - 0.04 + my_offset, bz + 0.098), scale=(0.046, 0.009, 0.005), rotation=(0.05, -0.1, 0.3), material=mats["Menma"])
        smooth_shade(menma_stick)
        food_objects.append(menma_stick)

    # Negi (Fresh Chopped Green Scallion Mound)
    negi_mound = create_sphere("Hero_Negi_Mound", location=(bx + 0.005, by + 0.005, bz + 0.104), radius=0.026, scale=(1.2, 1.1, 0.5), material=mats["Negi"])
    smooth_shade(negi_mound)
    food_objects.append(negi_mound)
    for sfi in range(8):
        sa = sfi * math.pi / 4.0
        scallion_ring = create_cylinder(f"Hero_Negi_Fleck_{sfi}", location=(bx + 0.005 + 0.032*math.cos(sa), by + 0.005 + 0.032*math.sin(sa), bz + 0.099), radius=0.005, depth=0.003, material=mats["Negi"])
        smooth_shade(scallion_ring)
        food_objects.append(scallion_ring)

    # Nori Seaweed Sheets (2 crisp dark green sheets standing at back rim)
    nori1 = create_cube("Hero_Nori_1", location=(bx - 0.05, by + 0.11, bz + 0.145), scale=(0.065, 0.003, 0.095), rotation=(-0.35, -0.15, 0.2), material=mats["Nori"])
    nori2 = create_cube("Hero_Nori_2", location=(bx + 0.03, by + 0.12, bz + 0.150), scale=(0.060, 0.003, 0.095), rotation=(-0.38, 0.12, -0.15), material=mats["Nori"])
    smooth_shade(nori1)
    smooth_shade(nori2)
    food_objects.extend([nori1, nori2])

    # Utensils beside Hero Bowl
    rest = create_cube("Hero_Hashioki", location=(bx + 0.22, by - 0.06, bz + 0.01), scale=(0.025, 0.045, 0.015), material=mats["BowlWhite"])
    smooth_shade(rest)
    chop1 = create_cylinder("Hero_Chopstick_1", location=(bx + 0.21, by + 0.02, bz + 0.022), radius=0.004, depth=0.24, rotation=(math.pi/2, 0, -0.05), material=mats["Bamboo"])
    chop2 = create_cylinder("Hero_Chopstick_2", location=(bx + 0.225, by + 0.02, bz + 0.022), radius=0.004, depth=0.24, rotation=(math.pi/2, 0, -0.04), material=mats["Bamboo"])
    smooth_shade(chop1)
    smooth_shade(chop2)
    spoon_handle = create_cylinder("Hero_Renge_Handle", location=(bx - 0.14, by - 0.04, bz + 0.11), radius=0.008, depth=0.14, rotation=(0.6, -0.6, 0.4), material=mats["BowlWhite"])
    spoon_bowl = create_sphere("Hero_Renge_Bowl", location=(bx - 0.09, by, bz + 0.090), radius=0.024, scale=(1.4, 0.8, 0.5), rotation=(0.2, -0.3, 0.4), material=mats["BowlWhite"])
    smooth_shade(spoon_handle)
    smooth_shade(spoon_bowl)
    food_objects.extend([rest, chop1, chop2, spoon_handle, spoon_bowl])

    # ==========================================================
    # 2. SECONDARY PREP RAMEN BOWL
    # ==========================================================
    p_bx, p_by, p_bz = -0.25, 0.12, 0.985
    prep_bowl = create_open_ramen_bowl("Prep_Bowl", location=(p_bx, p_by, p_bz), scale=0.90, mats=mats, outer_mat_name="BowlBlack")
    food_objects.append(prep_bowl)
    
    prep_broth = create_cylinder("Prep_Broth", location=(p_bx, p_by, p_bz + 0.075), radius=0.12, depth=0.012, material=mats["Broth"])
    prep_noodles = create_torus("Prep_Noodles", location=(p_bx, p_by, p_bz + 0.080), major_radius=0.075, minor_radius=0.012, material=mats["Noodles"])
    smooth_shade(prep_broth)
    smooth_shade(prep_noodles)
    food_objects.extend([prep_broth, prep_noodles])

    # ==========================================================
    # 3. ATMOSPHERIC STEAM WISPS
    # ==========================================================
    steam_coords = [
        (-0.80, 0.90, 1.25, 0.05),
        (-0.76, 0.92, 1.38, 0.07),
        (-0.82, 0.88, 1.52, 0.09),
        (-0.25, 0.95, 1.30, 0.05),
        (-0.22, 0.94, 1.42, 0.07),
        (bx - 0.12, by - 0.04, bz + 0.16, 0.022),
        (bx - 0.15, by - 0.02, bz + 0.22, 0.030),
    ]
    for si, (sx, sy, sz, srad) in enumerate(steam_coords):
        steam_cloud = create_sphere(f"Steam_Puff_{si}", location=(sx, sy, sz), radius=srad, segments=12, ring_count=8, scale=(1.0, 0.9, 1.3), material=mats["Steam"])
        smooth_shade(steam_cloud)
        food_objects.append(steam_cloud)

    return food_objects
