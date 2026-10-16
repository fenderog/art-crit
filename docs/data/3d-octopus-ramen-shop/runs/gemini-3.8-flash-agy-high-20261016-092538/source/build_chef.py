import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
from mesh_utils import create_cube, create_cylinder, create_sphere, create_torus, create_plane, smooth_shade

def create_tentacle_with_suckers(name, control_points, radii, mats, inner_bias=Vector((0, -0.3, -0.7)), num_suckers=9, bevel_depth=0.065):
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 4
    curve_data.resolution_u = 12
    curve_data.use_fill_caps = True # close tentacle ends with smooth caps
    
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(len(control_points) - 1)
    
    for i, pt in enumerate(control_points):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.radius = radii[i]
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    tentacle_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(tentacle_obj)
    
    bpy.context.view_layer.objects.active = tentacle_obj
    tentacle_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    tentacle_obj.data.materials.append(mats["OctopusSkin"])
    smooth_shade(tentacle_obj)
    
    # Place double rows of suckers along the inner curve
    sucker_objs = []
    n_pts = len(control_points)
    
    for s_idx in range(num_suckers):
        t_global = 0.15 + 0.70 * (s_idx / max(1, num_suckers - 1))
        seg_idx = min(int(t_global * (n_pts - 1)), n_pts - 2)
        local_t = (t_global * (n_pts - 1)) - seg_idx
        
        p_start = control_points[seg_idx]
        p_end = control_points[seg_idx + 1]
        pt = p_start.lerp(p_end, local_t)
        
        r_start = radii[seg_idx]
        r_end = radii[seg_idx + 1]
        r_blend = (r_start * (1.0 - local_t) + r_end * local_t) * bevel_depth
        
        tangent = (p_end - p_start).normalized()
        norm = inner_bias - tangent * inner_bias.dot(tangent)
        if norm.length < 1e-4:
            norm = Vector((0, 0, -1)) - tangent * Vector((0, 0, -1)).dot(tangent)
        norm.normalize()
        binorm = tangent.cross(norm).normalized()
        
        for side in [-1, 1]:
            sucker_r = r_blend * 0.35
            offset_dir = (norm * 0.95 + binorm * (side * 0.45)).normalized()
            sucker_pos = pt + offset_dir * (r_blend * 0.95)
            
            sucker_disc = create_cylinder(
                f"{name}_Sucker_{s_idx}_{side}",
                location=sucker_pos,
                radius=max(0.007, sucker_r),
                depth=max(0.004, sucker_r * 0.35),
                vertices=10,
                material=mats["OctopusPeach"]
            )
            smooth_shade(sucker_disc)
            sucker_objs.append(sucker_disc)
            
    return tentacle_obj, sucker_objs

def build_chef(mats):
    chef_objects = []
    
    # --- 1. Octopus Head / Mantle ---
    mantle = create_sphere(
        "Chef_Mantle", 
        location=(0.0, 0.54, 1.35), 
        radius=0.22, 
        segments=28, 
        ring_count=20, 
        scale=(0.95, 1.05, 1.25), 
        rotation=(0.12, 0, 0),
        material=mats["OctopusSkin"]
    )
    smooth_shade(mantle)
    chef_objects.append(mantle)
    
    # Peach belly / chest patch
    belly = create_sphere(
        "Chef_Belly",
        location=(0.0, 0.43, 1.24),
        radius=0.18,
        segments=20,
        ring_count=14,
        scale=(0.85, 0.45, 0.95),
        rotation=(0.15, 0, 0),
        material=mats["OctopusPeach"]
    )
    smooth_shade(belly)
    chef_objects.append(belly)
    
    # --- 2. Expressive Face & Eyes ---
    eye_l = create_sphere("Chef_Eye_L", location=(-0.11, 0.37, 1.38), radius=0.048, segments=20, ring_count=16, material=mats["EyeWhite"])
    eye_r = create_sphere("Chef_Eye_R", location=(0.11, 0.37, 1.38), radius=0.048, segments=20, ring_count=16, material=mats["EyeWhite"])
    smooth_shade(eye_l)
    smooth_shade(eye_r)
    chef_objects.extend([eye_l, eye_r])
    
    pupil_l = create_sphere("Chef_Pupil_L", location=(-0.11, 0.33, 1.38), radius=0.030, scale=(1.25, 0.5, 1.0), material=mats["EyePupil"])
    pupil_r = create_sphere("Chef_Pupil_R", location=(0.11, 0.33, 1.38), radius=0.030, scale=(1.25, 0.5, 1.0), material=mats["EyePupil"])
    smooth_shade(pupil_l)
    smooth_shade(pupil_r)
    chef_objects.extend([pupil_l, pupil_r])
    
    shine_l1 = create_sphere("Chef_EyeShine_L1", location=(-0.10, 0.315, 1.395), radius=0.010, material=mats["EyeShine"])
    shine_l2 = create_sphere("Chef_EyeShine_L2", location=(-0.12, 0.315, 1.365), radius=0.005, material=mats["EyeShine"])
    shine_r1 = create_sphere("Chef_EyeShine_R1", location=(0.12, 0.315, 1.395), radius=0.010, material=mats["EyeShine"])
    shine_r2 = create_sphere("Chef_EyeShine_R2", location=(0.10, 0.315, 1.365), radius=0.005, material=mats["EyeShine"])
    chef_objects.extend([shine_l1, shine_l2, shine_r1, shine_r2])
    
    brow_l = create_cylinder("Chef_Brow_L", location=(-0.11, 0.36, 1.43), radius=0.010, depth=0.08, rotation=(0, 0.25, 0.3), material=mats["OctopusSkin"])
    brow_r = create_cylinder("Chef_Brow_R", location=(0.11, 0.36, 1.43), radius=0.010, depth=0.08, rotation=(0, -0.25, -0.3), material=mats["OctopusSkin"])
    smooth_shade(brow_l)
    smooth_shade(brow_r)
    chef_objects.extend([brow_l, brow_r])
    
    blush_l = create_sphere("Chef_Blush_L", location=(-0.18, 0.40, 1.32), radius=0.026, scale=(1.0, 0.4, 0.7), material=mats["OctopusBlush"])
    blush_r = create_sphere("Chef_Blush_R", location=(0.18, 0.40, 1.32), radius=0.026, scale=(1.0, 0.4, 0.7), material=mats["OctopusBlush"])
    smooth_shade(blush_l)
    smooth_shade(blush_r)
    chef_objects.extend([blush_l, blush_r])
    
    siphon = create_cylinder("Chef_Siphon", location=(0.0, 0.36, 1.28), radius=0.032, depth=0.07, rotation=(0.4, 0, 0), material=mats["OctopusSkin"])
    smooth_shade(siphon)
    siphon_rim = create_torus("Chef_Siphon_Rim", location=(0.0, 0.33, 1.265), major_radius=0.030, minor_radius=0.008, rotation=(0.4, 0, 0), material=mats["OctopusPeach"])
    smooth_shade(siphon_rim)
    # Happy mouth smile line
    smile = create_torus("Chef_Smile", location=(0.0, 0.36, 1.22), major_radius=0.032, minor_radius=0.006, scale=(1.0, 0.5, 0.5), rotation=(0.8, 0, 0), material=mats["OctopusSkin"])
    smooth_shade(smile)
    chef_objects.extend([siphon, siphon_rim, smile])
    
    # --- 3. Snug Hachimaki Headband & White Chef Toque Hat ---
    hachimaki = create_torus("Chef_Hachimaki", location=(0.0, 0.52, 1.47), major_radius=0.20, minor_radius=0.018, scale=(1.0, 1.05, 0.8), rotation=(0.12, 0, 0), material=mats["HachimakiRed"])
    smooth_shade(hachimaki)
    knot = create_sphere("Chef_Hachimaki_Knot", location=(-0.21, 0.50, 1.48), radius=0.032, scale=(1.0, 0.8, 1.2), material=mats["HachimakiRed"])
    tail1 = create_cube("Chef_Hachimaki_Tail1", location=(-0.24, 0.57, 1.45), scale=(0.015, 0.11, 0.035), rotation=(0.2, 0.3, -0.4), material=mats["HachimakiRed"])
    tail2 = create_cube("Chef_Hachimaki_Tail2", location=(-0.25, 0.61, 1.40), scale=(0.015, 0.09, 0.030), rotation=(0.4, 0.2, -0.6), material=mats["HachimakiRed"])
    smooth_shade(knot)
    smooth_shade(tail1)
    smooth_shade(tail2)
    chef_objects.extend([hachimaki, knot, tail1, tail2])
    
    # White Chef Toque
    hat_band = create_cylinder("Chef_Hat_Band", location=(0.0, 0.55, 1.58), radius=0.16, depth=0.05, rotation=(0.12, 0, 0), material=mats["ChefHat"])
    smooth_shade(hat_band)
    hat_puff = create_sphere("Chef_Hat_Puff", location=(0.0, 0.56, 1.69), radius=0.21, scale=(1.05, 1.05, 0.68), rotation=(0.12, 0, 0), material=mats["ChefHat"])
    smooth_shade(hat_puff)
    chef_objects.extend([hat_band, hat_puff])
    
    # --- 4. Japanese Chef Apron ---
    apron_waist = create_torus("Chef_Apron_Belt", location=(0.0, 0.52, 1.14), major_radius=0.23, minor_radius=0.018, scale=(1.0, 1.05, 0.7), rotation=(0.12, 0, 0), material=mats["ApronStrap"])
    smooth_shade(apron_waist)
    apron_cloth = create_cube("Chef_Apron_Cloth", location=(0.0, 0.33, 1.02), scale=(0.34, 0.02, 0.24), rotation=(0.12, 0, 0), material=mats["Apron"])
    smooth_shade(apron_cloth)
    chef_objects.extend([apron_waist, apron_cloth])
    
    # --- 5. The 8 Dynamic Tentacles & Culinary Props ---
    
    # T1: Left Front - Holding Noodle Strainer (Tebo) lifting steaming noodles
    t1_pts = [
        Vector((-0.12, 0.46, 1.14)),
        Vector((-0.32, 0.40, 1.25)),
        Vector((-0.55, 0.52, 1.40)),
        Vector((-0.72, 0.65, 1.50)),
        Vector((-0.80, 0.78, 1.40))
    ]
    t1_obj, t1_suckers = create_tentacle_with_suckers("Tentacle_1_Tebo", t1_pts, [1.0, 0.85, 0.65, 0.45, 0.12], mats, inner_bias=Vector((0, 0, -1)))
    chef_objects.append(t1_obj)
    chef_objects.extend(t1_suckers)
    
    tebo_held = create_cylinder("Held_Tebo_Basket", location=(-0.82, 0.85, 1.28), radius=0.08, depth=0.16, material=mats["WireMesh"])
    tebo_handle = create_cylinder("Held_Tebo_Handle", location=(-0.80, 0.80, 1.40), radius=0.016, depth=0.22, rotation=(-0.4, 0.2, 0), material=mats["Bamboo"])
    smooth_shade(tebo_held)
    smooth_shade(tebo_handle)
    tebo_noodles = create_sphere("Held_Tebo_Noodles", location=(-0.82, 0.85, 1.34), radius=0.075, scale=(1.0, 1.0, 0.6), material=mats["Noodles"])
    smooth_shade(tebo_noodles)
    chef_objects.extend([tebo_held, tebo_handle, tebo_noodles])
    
    # T2: Left Middle - Holding Long Cooking Chopsticks (Saibashi)
    t2_pts = [
        Vector((-0.16, 0.42, 1.12)),
        Vector((-0.34, 0.30, 1.22)),
        Vector((-0.46, 0.16, 1.28)),
        Vector((-0.42, 0.04, 1.24))
    ]
    t2_obj, t2_suckers = create_tentacle_with_suckers("Tentacle_2_Chopsticks", t2_pts, [1.0, 0.8, 0.55, 0.12], mats, inner_bias=Vector((0, -0.5, -0.5)))
    chef_objects.append(t2_obj)
    chef_objects.extend(t2_suckers)
    
    chop1 = create_cylinder("Saibashi_1", location=(-0.40, 0.02, 1.20), radius=0.005, depth=0.34, rotation=(0.5, 0.3, -0.4), material=mats["Bamboo"])
    chop2 = create_cylinder("Saibashi_2", location=(-0.38, 0.03, 1.21), radius=0.005, depth=0.34, rotation=(0.52, 0.28, -0.38), material=mats["Bamboo"])
    smooth_shade(chop1)
    smooth_shade(chop2)
    noodle_curl = create_torus("Noodle_Swirl", location=(-0.34, -0.06, 1.10), major_radius=0.035, minor_radius=0.008, rotation=(0.4, 0.5, 0.2), material=mats["Noodles"])
    smooth_shade(noodle_curl)
    chef_objects.extend([chop1, chop2, noodle_curl])
    
    # T3: Center Left - Holding Wooden Soup Ladle (Hishaku) Pouring Broth
    t3_pts = [
        Vector((-0.08, 0.38, 1.10)),
        Vector((-0.16, 0.24, 1.16)),
        Vector((-0.24, 0.10, 1.20)),
        Vector((-0.26, -0.02, 1.14))
    ]
    t3_obj, t3_suckers = create_tentacle_with_suckers("Tentacle_3_Ladle", t3_pts, [1.0, 0.8, 0.55, 0.12], mats, inner_bias=Vector((0, -0.7, -0.3)))
    chef_objects.append(t3_obj)
    chef_objects.extend(t3_suckers)
    
    ladle_cup = create_cylinder("Ladle_Cup", location=(-0.25, -0.10, 1.10), radius=0.045, depth=0.05, rotation=(0.6, 0.2, 0), material=mats["Bamboo"])
    ladle_handle = create_cylinder("Ladle_Handle", location=(-0.24, 0.02, 1.16), radius=0.008, depth=0.28, rotation=(-0.8, 0.1, 0), material=mats["Bamboo"])
    smooth_shade(ladle_cup)
    smooth_shade(ladle_handle)
    broth_stream = create_cylinder("Broth_Stream", location=(-0.24, 0.00, 1.05), radius=0.010, depth=0.10, rotation=(0.3, 0.1, 0), material=mats["Broth"])
    smooth_shade(broth_stream)
    chef_objects.extend([ladle_cup, ladle_handle, broth_stream])
    
    # T4: Center Right - Holding Chef Tongs Plating Chashu on Hero Bowl
    t4_pts = [
        Vector((0.08, 0.38, 1.10)),
        Vector((0.14, 0.22, 1.14)),
        Vector((0.10, 0.08, 1.12)),
        Vector((0.04, -0.02, 1.08))
    ]
    t4_obj, t4_suckers = create_tentacle_with_suckers("Tentacle_4_Tongs", t4_pts, [1.0, 0.75, 0.5, 0.12], mats, inner_bias=Vector((0, -0.8, -0.2)))
    chef_objects.append(t4_obj)
    chef_objects.extend(t4_suckers)
    
    # Stainless Steel Tongs gripping chashu slice
    tong_l = create_cube("Tong_Arm_L", location=(0.045, -0.04, 1.10), scale=(0.004, 0.10, 0.010), rotation=(-0.35, 0.15, 0), material=mats["StainlessSteel"])
    tong_r = create_cube("Tong_Arm_R", location=(0.028, -0.04, 1.10), scale=(0.004, 0.10, 0.010), rotation=(-0.35, -0.15, 0), material=mats["StainlessSteel"])
    chef_objects.extend([tong_l, tong_r])
    
    # T5: Right Center - Holding Shichimi Seasoning Shaker
    t5_pts = [
        Vector((0.16, 0.42, 1.12)),
        Vector((0.32, 0.28, 1.22)),
        Vector((0.44, 0.14, 1.28)),
        Vector((0.40, 0.02, 1.22))
    ]
    t5_obj, t5_suckers = create_tentacle_with_suckers("Tentacle_5_Shichimi", t5_pts, [1.0, 0.8, 0.55, 0.12], mats, inner_bias=Vector((-0.3, -0.6, -0.4)))
    chef_objects.append(t5_obj)
    chef_objects.extend(t5_suckers)
    
    shaker_body = create_cylinder("Shichimi_Body", location=(0.38, 0.00, 1.16), radius=0.025, depth=0.08, rotation=(0.7, 0.2, -0.3), material=mats["HachimakiRed"])
    shaker_cap = create_cylinder("Shichimi_Cap", location=(0.36, -0.04, 1.12), radius=0.026, depth=0.025, rotation=(0.7, 0.2, -0.3), material=mats["BowlBlack"])
    smooth_shade(shaker_body)
    smooth_shade(shaker_cap)
    spice1 = create_sphere("Spice_1", location=(0.34, -0.06, 1.06), radius=0.006, material=mats["HachimakiRed"])
    spice2 = create_sphere("Spice_2", location=(0.33, -0.07, 1.03), radius=0.005, material=mats["HachimakiRed"])
    spice3 = create_sphere("Spice_3", location=(0.32, -0.08, 1.00), radius=0.005, material=mats["HachimakiRed"])
    chef_objects.extend([shaker_body, shaker_cap, spice1, spice2, spice3])
    
    # T6: Right Upper - Welcoming "Irasshaimase!" Wave
    t6_pts = [
        Vector((0.15, 0.50, 1.18)),
        Vector((0.36, 0.46, 1.38)),
        Vector((0.54, 0.38, 1.58)),
        Vector((0.62, 0.28, 1.74)),
        Vector((0.54, 0.20, 1.82)),
        Vector((0.44, 0.22, 1.76))
    ]
    t6_obj, t6_suckers = create_tentacle_with_suckers("Tentacle_6_Wave", t6_pts, [1.0, 0.85, 0.7, 0.5, 0.3, 0.10], mats, inner_bias=Vector((-0.5, -0.5, -0.3)), num_suckers=11)
    chef_objects.append(t6_obj)
    chef_objects.extend(t6_suckers)
    
    # T7: Front Left - Counter Anchor
    t7_pts = [
        Vector((-0.18, 0.52, 1.08)),
        Vector((-0.34, 0.38, 1.02)),
        Vector((-0.46, 0.18, 0.98)),
        Vector((-0.52, 0.00, 0.965)),
        Vector((-0.56, -0.12, 0.965))
    ]
    t7_obj, t7_suckers = create_tentacle_with_suckers("Tentacle_7_Counter_L", t7_pts, [1.0, 0.8, 0.6, 0.4, 0.12], mats, inner_bias=Vector((0, 0, -1)))
    chef_objects.append(t7_obj)
    chef_objects.extend(t7_suckers)
    
    # T8: Front Right - Resting on Counter with Kitchen Towel
    t8_pts = [
        Vector((0.18, 0.52, 1.08)),
        Vector((0.34, 0.38, 1.02)),
        Vector((0.46, 0.18, 0.98)),
        Vector((0.52, 0.00, 0.965)),
        Vector((0.56, -0.10, 0.965))
    ]
    t8_obj, t8_suckers = create_tentacle_with_suckers("Tentacle_8_Counter_R", t8_pts, [1.0, 0.8, 0.6, 0.4, 0.12], mats, inner_bias=Vector((0, 0, -1)))
    chef_objects.append(t8_obj)
    chef_objects.extend(t8_suckers)
    
    towel = create_cube("Chef_Towel", location=(0.58, -0.08, 0.96), scale=(0.14, 0.18, 0.02), rotation=(0, 0, 0.15), material=mats["ChefHat"])
    smooth_shade(towel)
    chef_objects.append(towel)

    return chef_objects
