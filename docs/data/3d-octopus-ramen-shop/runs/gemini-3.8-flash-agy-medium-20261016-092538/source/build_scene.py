import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix, Quaternion
import math
import random
import os

print("=== Starting Perfected Octopus Ramen Chef Scene Generation ===")

# ==========================================
# 1. SCENE CLEANUP & RENDER SETTINGS
# ==========================================
def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)

clean_scene()

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Raytracing in Blender 5 EEVEE Next
scene.eevee.use_raytracing = True
scene.eevee.use_fast_gi = True
scene.eevee.taa_render_samples = 64

# Color management
scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
scene.view_settings.look = 'Medium High Contrast'

# Dark atmospheric night market world
world = scene.world
if not world:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.015, 0.018, 0.028, 1.0)
    bg_node.inputs['Strength'].default_value = 0.55

# ==========================================
# 2. MATERIAL LIBRARY (Principled BSDF)
# ==========================================
def make_mat(name, base_color, roughness=0.5, metallic=0.0, emission_color=None, emission_strength=0.0, alpha=1.0, subsurface_weight=0.0, transmission_weight=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if 'Base Color' in bsdf.inputs:
        bsdf.inputs['Base Color'].default_value = base_color
    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = roughness
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = metallic
    if 'Alpha' in bsdf.inputs:
        bsdf.inputs['Alpha'].default_value = alpha
    if 'Subsurface Weight' in bsdf.inputs and subsurface_weight > 0.0:
        bsdf.inputs['Subsurface Weight'].default_value = subsurface_weight
        if 'Subsurface Radius' in bsdf.inputs:
            bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.15)
    if 'Transmission Weight' in bsdf.inputs and transmission_weight > 0.0:
        bsdf.inputs['Transmission Weight'].default_value = transmission_weight
    if emission_color and 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = emission_color
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission_strength
            
    if alpha < 1.0 or transmission_weight > 0.0:
        mat.blend_method = 'BLEND'
    return mat

# Materials
M_OCTOPUS = make_mat("M_Octopus", (0.88, 0.22, 0.14, 1.0), roughness=0.25, subsurface_weight=0.25)
M_SUCKER = make_mat("M_Sucker", (0.98, 0.84, 0.80, 1.0), roughness=0.30, subsurface_weight=0.2)
M_EYE_WHITE = make_mat("M_EyeWhite", (0.96, 0.96, 0.97, 1.0), roughness=0.1)
M_EYE_PUPIL = make_mat("M_EyePupil", (0.01, 0.01, 0.02, 1.0), roughness=0.05)
M_EYE_SPARKLE = make_mat("M_EyeSparkle", (1.0, 1.0, 1.0, 1.0), roughness=0.0, emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=3.0)
M_BLUSH = make_mat("M_Blush", (0.95, 0.35, 0.45, 1.0), roughness=0.5)
M_HACHIMAKI = make_mat("M_Hachimaki", (0.95, 0.95, 0.95, 1.0), roughness=0.6)
M_HACHIMAKI_RED = make_mat("M_HachimakiRed", (0.88, 0.06, 0.06, 1.0), roughness=0.5)
M_APRON = make_mat("M_Apron", (0.07, 0.12, 0.26, 1.0), roughness=0.7)

M_WOOD_LIGHT = make_mat("M_WoodLight", (0.58, 0.36, 0.18, 1.0), roughness=0.30)
M_WOOD_MEDIUM = make_mat("M_WoodMedium", (0.42, 0.24, 0.12, 1.0), roughness=0.45)
M_WOOD_DARK = make_mat("M_WoodDark", (0.22, 0.12, 0.06, 1.0), roughness=0.55)
M_ROOF = make_mat("M_Roof", (0.13, 0.14, 0.16, 1.0), roughness=0.55)

M_NOREN_INDIGO = make_mat("M_NorenIndigo", (0.06, 0.10, 0.24, 1.0), roughness=0.75)
M_NOREN_CREAM = make_mat("M_NorenCream", (0.94, 0.90, 0.82, 1.0), roughness=0.75)

# Rich warm red-orange lantern paper
M_LANTERN_RED = make_mat("M_LanternRed", (0.92, 0.14, 0.06, 1.0), roughness=0.35, emission_color=(1.0, 0.24, 0.06, 1.0), emission_strength=1.8)
M_LANTERN_BLACK = make_mat("M_LanternBlack", (0.03, 0.03, 0.03, 1.0), roughness=0.25)
M_STEEL = make_mat("M_Steel", (0.85, 0.86, 0.88, 1.0), roughness=0.18, metallic=0.92)
M_GOLD_BRASS = make_mat("M_GoldBrass", (0.88, 0.68, 0.24, 1.0), roughness=0.22, metallic=0.85)

M_RAMEN_BROTH = make_mat("M_RamenBroth", (0.72, 0.36, 0.10, 1.0), roughness=0.06, transmission_weight=0.35)
M_RAMEN_NOODLE = make_mat("M_RamenNoodle", (0.96, 0.80, 0.36, 1.0), roughness=0.22)
M_CHASHU_MEAT = make_mat("M_ChashuMeat", (0.60, 0.28, 0.18, 1.0), roughness=0.45)
M_CHASHU_FAT = make_mat("M_ChashuFat", (0.95, 0.92, 0.86, 1.0), roughness=0.3)
M_CHASHU_CRUST = make_mat("M_ChashuCrust", (0.24, 0.10, 0.04, 1.0), roughness=0.6)
M_EGG_WHITE = make_mat("M_EggWhite", (0.92, 0.86, 0.76, 1.0), roughness=0.22)
M_EGG_YOLK = make_mat("M_EggYolk", (1.0, 0.46, 0.02, 1.0), roughness=0.10, subsurface_weight=0.45)
M_NARUTO_WHITE = make_mat("M_NarutoWhite", (0.96, 0.95, 0.94, 1.0), roughness=0.35)
M_NARUTO_PINK = make_mat("M_NarutoPink", (0.98, 0.15, 0.50, 1.0), roughness=0.35)
M_NORI = make_mat("M_Nori", (0.04, 0.07, 0.04, 1.0), roughness=0.65)
M_MENMA = make_mat("M_Menma", (0.78, 0.58, 0.28, 1.0), roughness=0.4)
M_SCALLION = make_mat("M_Scallion", (0.16, 0.68, 0.10, 1.0), roughness=0.35)
M_SCALLION_WHITE = make_mat("M_ScallionWhite", (0.86, 0.92, 0.78, 1.0), roughness=0.35)

M_BOWL_EXT = make_mat("M_BowlExt", (0.06, 0.06, 0.07, 1.0), roughness=0.22)
M_BOWL_INT = make_mat("M_BowlInt", (0.85, 0.12, 0.10, 1.0), roughness=0.16)
M_BOWL_WHITE = make_mat("M_BowlWhite", (0.95, 0.95, 0.95, 1.0), roughness=0.15)
M_CERAMIC_WHITE = make_mat("M_CeramicWhite", (0.92, 0.92, 0.92, 1.0), roughness=0.20)
M_CHOPSTICK_WOOD = make_mat("M_ChopstickWood", (0.75, 0.55, 0.32, 1.0), roughness=0.35)
M_CHOPSTICK_RED = make_mat("M_ChopstickRed", (0.78, 0.12, 0.12, 1.0), roughness=0.22)
M_GYOZA_TOP = make_mat("M_GyozaTop", (0.92, 0.85, 0.72, 1.0), roughness=0.45)
M_GYOZA_BROWN = make_mat("M_GyozaBrown", (0.45, 0.22, 0.08, 1.0), roughness=0.55)
M_STEAM = make_mat("M_Steam", (0.95, 0.95, 0.98, 1.0), roughness=0.3, alpha=0.30)
M_CLOTH_WHITE = make_mat("M_ClothWhite", (0.92, 0.92, 0.94, 1.0), roughness=0.8)

# ==========================================
# 3. MESH MODELING HELPERS
# ==========================================
def link_object(obj, collection=None):
    if collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(obj)
    return obj

def create_lathe_mesh(name, profile_pts, segments=32, mat=None):
    bm = bmesh.new()
    num_pts = len(profile_pts)
    rings = []
    
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        ring_verts = []
        for r, z in profile_pts:
            v = bm.verts.new((r * cos_t, r * sin_t, z))
            ring_verts.append(v)
        rings.append(ring_verts)
        
    bm.verts.ensure_lookup_table()
    
    for i in range(segments):
        next_i = (i + 1) % segments
        for j in range(num_pts - 1):
            v1 = rings[i][j]
            v2 = rings[next_i][j]
            v3 = rings[next_i][j + 1]
            v4 = rings[i][j + 1]
            
            if profile_pts[j][0] == 0 and profile_pts[j+1][0] == 0:
                continue
            elif profile_pts[j][0] == 0:
                bm.faces.new((v1, v2, v3))
            elif profile_pts[j+1][0] == 0:
                bm.faces.new((v1, v3, v4))
            else:
                bm.faces.new((v1, v2, v3, v4))
                
    for face in bm.faces:
        face.smooth = True
        
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    return link_object(obj)

def create_box(name, size, location=(0,0,0), rotation=(0,0,0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_cylinder(name, radius, height, location=(0,0,0), rotation=(0,0,0), vertices=32, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=vertices, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_sphere(name, radius, location=(0,0,0), scale=(1,1,1), segments=32, rings=16, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=rings, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_torus(name, major_r, minor_r, location=(0,0,0), rotation=(0,0,0), mat=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r, major_segments=32, minor_segments=16, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

# ==========================================
# 4. ROBUST TENTACLE BUILDER (UNDERBELLY SUCKERS)
# ==========================================
def catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        (2.0 * p1) +
        (-p0 + p2) * t +
        (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
        (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
    )

def interpolate_spline(control_points, samples_per_segment=6):
    pts = [Vector(p) for p in control_points]
    if len(pts) < 2:
        return pts
    extended = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    res = []
    for i in range(len(pts) - 1):
        p0 = extended[i]
        p1 = extended[i+1]
        p2 = extended[i+2]
        p3 = extended[i+3]
        for s in range(samples_per_segment):
            t = s / samples_per_segment
            res.append(catmull_rom(p0, p1, p2, p3, t))
    res.append(pts[-1])
    return res

def create_tentacle(name, control_pts, r_base=0.075, r_tip=0.015, ring_segments=14, mat=M_OCTOPUS, sucker_mat=M_SUCKER, sucker_step=3, belly_target=Vector((0, 0.2, 1.0))):
    spline_pts = interpolate_spline(control_pts, samples_per_segment=6)
    N = len(spline_pts)
    
    tangents = []
    for i in range(N):
        if i == 0:
            t = (spline_pts[1] - spline_pts[0]).normalized()
        elif i == N - 1:
            t = (spline_pts[-1] - spline_pts[-2]).normalized()
        else:
            t = (spline_pts[i+1] - spline_pts[i-1]).normalized()
        tangents.append(t)
        
    normals = []
    binormals = []
    
    for i in range(N):
        t = tangents[i]
        p = spline_pts[i]
        desired_belly = (Vector((0, 0, -1.0)) + (belly_target - p).normalized() * 0.5).normalized()
        norm = (desired_belly - desired_belly.dot(t) * t)
        if norm.length < 1e-3:
            norm = Vector((0, 1, 0)) - Vector((0, 1, 0)).dot(t) * t
        norm = norm.normalized()
        binorm = t.cross(norm).normalized()
        normals.append(norm)
        binormals.append(binorm)
        
    bm = bmesh.new()
    rings = []
    radii = []
    for i in range(N):
        factor = i / (N - 1)
        r = r_base * (1.0 - factor * 0.82)
        radii.append(r)
        
    for i in range(N):
        p = spline_pts[i]
        r = radii[i]
        ni = normals[i]
        bi = binormals[i]
        ring_v = []
        for s in range(ring_segments):
            theta = 2.0 * math.pi * s / ring_segments
            offset = (math.cos(theta) * ni + math.sin(theta) * bi) * r
            v = bm.verts.new(p + offset)
            ring_v.append(v)
        rings.append(ring_v)
        
    bm.verts.ensure_lookup_table()
    
    for i in range(N - 1):
        for s in range(ring_segments):
            s_next = (s + 1) % ring_segments
            v1 = rings[i][s]
            v2 = rings[i+1][s]
            v3 = rings[i+1][s_next]
            v4 = rings[i][s_next]
            bm.faces.new((v1, v2, v3, v4))
            
    tip_center = bm.verts.new(spline_pts[-1])
    for s in range(ring_segments):
        s_next = (s + 1) % ring_segments
        bm.faces.new((rings[-1][s], tip_center, rings[-1][s_next]))
        
    base_center = bm.verts.new(spline_pts[0])
    for s in range(ring_segments):
        s_next = (s + 1) % ring_segments
        bm.faces.new((rings[0][s], rings[0][s_next], base_center))
        
    for f in bm.faces:
        f.smooth = True
        
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    tentacle_obj = bpy.data.objects.new(name, mesh)
    tentacle_obj.data.materials.append(mat)
    link_object(tentacle_obj)
    
    sucker_objs = []
    for i in range(2, N - 3, sucker_step):
        p = spline_pts[i]
        r = radii[i]
        ni = normals[i]
        bi = binormals[i]
        ti = tangents[i]
        
        suck_pos = p + ni * (r * 0.88)
        suck_scale = r * 0.38
        
        rot_mat = Matrix([bi, ti, ni]).transposed()
        rot_quat = rot_mat.to_quaternion()
        
        suck = create_torus(f"{name}_suck_{i}", suck_scale, suck_scale * 0.38, location=suck_pos, mat=sucker_mat)
        suck.rotation_mode = 'QUATERNION'
        suck.rotation_quaternion = rot_quat
        sucker_objs.append(suck)
        
    return tentacle_obj, sucker_objs

# ==========================================
# 5. BUILD THE RAMEN BOOTH (YATAI)
# ==========================================
def build_booth():
    print("Building Ramen Booth (Yatai)...")
    
    # Floor platform / deck with wooden floorboards
    deck = create_box("FloorDeck", (2.8, 2.2, 0.08), location=(0.0, 0.15, 0.04), mat=M_WOOD_DARK)
    for b_i in range(9):
        by = -0.8 + b_i * 0.22
        create_box(f"FloorBoard_{b_i}", (2.78, 0.20, 0.01), location=(0.0, by, 0.085), mat=M_WOOD_MEDIUM)
    
    # 4 Main Wooden Corner Posts
    post_x = 1.18
    post_y_front = -0.45
    post_y_back = 0.95
    post_h = 2.45
    post_w = 0.09
    
    for x in [-post_x, post_x]:
        for y in [post_y_front, post_y_back]:
            create_box(f"Post_{x}_{y}", (post_w, post_w, post_h), location=(x, y, post_h / 2.0), mat=M_WOOD_DARK)
            create_box(f"PostFoot_{x}_{y}", (post_w + 0.02, post_w + 0.02, 0.08), location=(x, y, 0.12), mat=M_STEEL)
            
    # Overhead Beams
    create_box("Beam_Front", (post_x * 2 + 0.35, post_w, post_w * 1.3), location=(0, post_y_front, 2.22), mat=M_WOOD_DARK)
    create_box("Beam_Back", (post_x * 2 + 0.35, post_w, post_w * 1.3), location=(0, post_y_back, 2.22), mat=M_WOOD_DARK)
    create_box("Beam_Left", (post_w, (post_y_back - post_y_front) + 0.2, post_w), location=(-post_x, (post_y_front + post_y_back)/2, 2.22), mat=M_WOOD_DARK)
    create_box("Beam_Right", (post_w, (post_y_back - post_y_front) + 0.2, post_w), location=(post_x, (post_y_front + post_y_back)/2, 2.22), mat=M_WOOD_DARK)
    
    # Japanese Roof Brackets
    for x in [-post_x, post_x]:
        for y in [post_y_front, post_y_back]:
            create_box(f"Bracket_{x}_{y}", (0.16, 0.16, 0.06), location=(x, y, 2.28), mat=M_WOOD_MEDIUM)
            
    # Gabled Roof Structure
    roof_w = post_x * 2 + 0.55
    ridge_y = (post_y_front + post_y_back) / 2
    create_box("Roof_Ridge", (roof_w, 0.12, 0.12), location=(0, ridge_y, 2.76), mat=M_WOOD_DARK)
    
    # Front slope
    slope_len_f = math.sqrt((ridge_y - (post_y_front - 0.25))**2 + (2.76 - 2.18)**2)
    angle_f = math.atan2(2.76 - 2.18, ridge_y - (post_y_front - 0.25))
    create_box("Roof_Slope_Front", (roof_w + 0.08, slope_len_f + 0.08, 0.05), 
               location=(0, (ridge_y + post_y_front - 0.25) / 2, (2.76 + 2.18) / 2 + 0.03), 
               rotation=(math.radians(90) - angle_f, 0, 0), mat=M_ROOF)
               
    for tx in range(15):
        tile_x = -1.25 + tx * 0.18
        create_cylinder(f"Roof_Tile_{tx}", 0.025, slope_len_f + 0.06, 
                        location=(tile_x, (ridge_y + post_y_front - 0.25) / 2, (2.76 + 2.18) / 2 + 0.06), 
                        rotation=(math.radians(90) - angle_f, 0, 0), mat=M_ROOF)
                        
    # Back slope
    slope_len_b = math.sqrt(((post_y_back + 0.25) - ridge_y)**2 + (2.76 - 2.18)**2)
    angle_b = math.atan2(2.76 - 2.18, (post_y_back + 0.25) - ridge_y)
    create_box("Roof_Slope_Back", (roof_w + 0.08, slope_len_b + 0.08, 0.05), 
               location=(0, (ridge_y + post_y_back + 0.25) / 2, (2.76 + 2.18) / 2 + 0.03), 
               rotation=(-(math.radians(90) - angle_b), 0, 0), mat=M_ROOF)
               
    # Front Wooden Counter (Polished Hinoki Bar)
    counter_w = 2.20
    counter_d = 0.46
    counter_h = 0.07
    counter_z = 0.90
    counter_y = -0.32
    create_box("Counter_Top", (counter_w, counter_d, counter_h), location=(0, counter_y, counter_z), mat=M_WOOD_LIGHT)
    
    # Counter front vertical decorative wooden slats
    slat_z_h = counter_z - 0.08
    for s_i in range(18):
        sx = -1.0 + s_i * 0.118
        create_box(f"Counter_Slat_{s_i}", (0.09, 0.03, slat_z_h), location=(sx, counter_y - counter_d/2 + 0.015, (counter_z - 0.04)/2), mat=M_WOOD_MEDIUM)
        
    create_cylinder("Footrest_Bar", 0.022, counter_w - 0.1, location=(0, counter_y - counter_d/2 - 0.12, 0.18), rotation=(0, math.radians(90), 0), mat=M_STEEL)
    
    # Back Prep Table / Kitchen Station
    prep_d = 0.55
    prep_z = 0.85
    prep_y = 0.65
    create_box("Prep_Table", (counter_w, prep_d, counter_h), location=(0, prep_y, prep_z), mat=M_STEEL)
    create_box("Prep_Table_Under", (counter_w - 0.1, prep_d - 0.1, prep_z - 0.06), location=(0, prep_y, prep_z/2), mat=M_WOOD_DARK)
    
    # Traditional Noren Fabric Curtains hanging across the front top beam
    noren_y = post_y_front + 0.02
    noren_z_top = 2.20
    noren_h = 0.44
    panel_w = 0.45
    gap = 0.04
    
    create_cylinder("Noren_Rod", 0.016, counter_w + 0.1, location=(0, noren_y, noren_z_top + 0.02), rotation=(0, math.radians(90), 0), mat=M_WOOD_LIGHT)
    
    for i in range(4):
        px = -0.74 + i * (panel_w + gap)
        create_box(f"Noren_Panel_{i}", (panel_w, 0.012, noren_h), location=(px, noren_y, noren_z_top - noren_h/2), mat=M_NOREN_INDIGO)
        create_box(f"Noren_Insignia_{i}", (panel_w * 0.42, 0.014, noren_h * 0.36), location=(px, noren_y - 0.002, noren_z_top - noren_h/2), mat=M_NOREN_CREAM)
        create_cylinder(f"Noren_RedDot_{i}", 0.045, 0.016, location=(px, noren_y - 0.003, noren_z_top - noren_h/2), rotation=(math.radians(90), 0, 0), mat=M_HACHIMAKI_RED)
        
    # Red Glowing Paper Lanterns (Chōchin)
    lantern_xs = [-1.08, 1.08]
    for lx in lantern_xs:
        ly = post_y_front - 0.14
        lz = 1.82
        create_box(f"Lantern_Bracket_{lx}", (0.04, 0.22, 0.04), location=(lx, ly + 0.10, lz + 0.32), mat=M_WOOD_DARK)
        create_cylinder(f"Lantern_Top_{lx}", 0.14, 0.04, location=(lx, ly, lz + 0.22), mat=M_LANTERN_BLACK)
        
        # Ribbed paper lantern body
        body_prof = [
            (0.12, -0.22), (0.19, -0.15), (0.22, -0.05), (0.23, 0.0), (0.22, 0.08), (0.18, 0.17), (0.12, 0.22)
        ]
        create_lathe_mesh(f"Lantern_Body_{lx}", body_prof, segments=24, mat=M_LANTERN_RED).location = (lx, ly, lz)
        
        # Decorative black horizontal rings around lantern
        for r_z in [-0.10, 0.0, 0.10]:
            r_rad = 0.225 if r_z == 0.0 else 0.205
            create_torus(f"Lantern_Ring_{lx}_{r_z}", r_rad, 0.006, location=(lx, ly, lz + r_z), mat=M_LANTERN_BLACK)
            
        create_cylinder(f"Lantern_Bottom_{lx}", 0.12, 0.04, location=(lx, ly, lz - 0.22), mat=M_LANTERN_BLACK)
        create_cylinder(f"Lantern_Tassel_{lx}", 0.025, 0.12, location=(lx, ly, lz - 0.29), mat=M_HACHIMAKI_RED)
        
        # Warm Point Light inside lantern
        pl = bpy.data.lights.new(f"Lantern_Light_{lx}", 'POINT')
        pl.color = (1.0, 0.38, 0.14)
        pl.energy = 55.0
        pl.shadow_soft_size = 0.22
        pl_obj = bpy.data.objects.new(f"Lantern_Light_{lx}", pl)
        pl_obj.location = (lx, ly, lz)
        link_object(pl_obj)
        
    # Customer Bar Stools in front of counter
    for sx in [-0.55, 0.55]:
        sy = counter_y - counter_d/2 - 0.40
        create_cylinder(f"Stool_Seat_{sx}", 0.18, 0.05, location=(sx, sy, 0.60), mat=M_WOOD_LIGHT)
        create_cylinder(f"Stool_Leg_{sx}", 0.035, 0.58, location=(sx, sy, 0.29), mat=M_WOOD_DARK)
        create_cylinder(f"Stool_Base_{sx}", 0.16, 0.03, location=(sx, sy, 0.03), mat=M_WOOD_DARK)
        create_torus(f"Stool_Footring_{sx}", 0.12, 0.012, location=(sx, sy, 0.22), mat=M_STEEL)

# ==========================================
# 6. FOOD & PROPS MODELING
# ==========================================
def create_ramen_bowl(name, loc, scale=1.0):
    r_outer = [
        (0.0, 0.0), (0.09, 0.0), (0.095, 0.025), (0.088, 0.03),
        (0.12, 0.07), (0.17, 0.12), (0.21, 0.16), (0.22, 0.175), (0.215, 0.18)
    ]
    bowl = create_lathe_mesh(f"{name}_Bowl", r_outer, segments=36, mat=M_BOWL_EXT)
    bowl.location = loc
    bowl.scale = (scale, scale, scale)
    
    r_inner = [
        (0.0, 0.035), (0.075, 0.04), (0.11, 0.072), (0.16, 0.122), (0.205, 0.162), (0.212, 0.174)
    ]
    interior = create_lathe_mesh(f"{name}_Interior", r_inner, segments=36, mat=M_BOWL_INT)
    interior.location = loc
    interior.scale = (scale, scale, scale)
    
    # Rich Broth liquid disc raised near top of bowl for maximum visibility
    broth_z = loc[2] + 0.162 * scale
    broth = create_cylinder(f"{name}_Broth", 0.204 * scale, 0.01 * scale, location=(loc[0], loc[1], broth_z), mat=M_RAMEN_BROTH)
    
    return bowl, broth

def populate_hero_ramen(bowl_loc):
    bx, by, bz = bowl_loc
    top_z = bz + 0.164
    
    # Ramen Noodles swirl bundle
    create_torus("Noodle_Cluster", 0.12, 0.042, location=(bx, by, top_z - 0.01), mat=M_RAMEN_NOODLE)
    
    # 2 Slices of Chashu Pork Belly (tilted toward camera for delicious presentation!)
    for i, (dx, dy, rot_z, tilt_x) in enumerate([(-0.06, 0.04, 25, 20), (-0.01, 0.07, -10, 22)]):
        chashu_loc = (bx + dx, by + dy, top_z + 0.012 + i * 0.007)
        rot_e = (math.radians(tilt_x), 0, math.radians(rot_z))
        create_cylinder(f"Chashu_Crust_{i}", 0.065, 0.012, location=chashu_loc, rotation=rot_e, mat=M_CHASHU_CRUST)
        create_cylinder(f"Chashu_Meat_{i}", 0.063, 0.014, location=chashu_loc, rotation=rot_e, mat=M_CHASHU_MEAT)
        create_cylinder(f"Chashu_Fat_{i}", 0.042, 0.015, location=chashu_loc, rotation=rot_e, mat=M_CHASHU_FAT)
        create_cylinder(f"Chashu_Core_{i}", 0.022, 0.016, location=chashu_loc, rotation=rot_e, mat=M_CHASHU_MEAT)
        
    # Soft-Boiled Ajitsuke Tamago (2 halves with glowing jammy yolk, angled toward camera)
    egg_configs = [
        (bx + 0.08, by + 0.03, top_z + 0.015, 22, -25),
        (bx + 0.09, by - 0.03, top_z + 0.015, 24, 10)
    ]
    for i, (ex, ey, ez, tilt_x, rot_z) in enumerate(egg_configs):
        rot_e = (math.radians(tilt_x), 0, math.radians(rot_z))
        create_sphere(f"Egg_White_{i}", 0.040, location=(ex, ey, ez), scale=(1.2, 0.85, 0.65), mat=M_EGG_WHITE)
        create_sphere(f"Egg_Yolk_{i}", 0.027, location=(ex, ey - 0.004, ez + 0.010), scale=(1.0, 1.0, 0.70), mat=M_EGG_YOLK)
        
    # Narutomaki (fish cake with pink spiral)
    for i, (nx, ny, nrot_z, tilt_x) in enumerate([(bx - 0.08, by - 0.03, 35, 20), (bx - 0.05, by - 0.07, 10, 22)]):
        nloc = (nx, ny, top_z + 0.015 + i * 0.006)
        rot_e = (math.radians(tilt_x), 0, math.radians(nrot_z))
        create_cylinder(f"Naruto_White_{i}", 0.038, 0.01, location=nloc, rotation=rot_e, vertices=20, mat=M_NARUTO_WHITE)
        create_torus(f"Naruto_Pink_{i}", 0.018, 0.006, location=nloc, rotation=rot_e, mat=M_NARUTO_PINK)
        
    # Nori Seaweed Sheets standing upright against back rim
    for i, (nx, ny, nrot_z, tilt) in enumerate([(bx - 0.06, by + 0.12, 15, -18), (bx + 0.03, by + 0.13, -10, -22)]):
        create_box(f"Nori_Sheet_{i}", (0.095, 0.004, 0.13), location=(nx, ny, top_z + 0.055), 
                   rotation=(math.radians(tilt), 0, math.radians(nrot_z)), mat=M_NORI)
                   
    # Menma Bamboo Shoots
    for i in range(4):
        ang = math.radians(55 + i * 16)
        mx = bx - 0.09 + math.cos(ang) * 0.03
        my = by + 0.01 + math.sin(ang) * 0.03
        create_box(f"Menma_{i}", (0.014, 0.055, 0.008), location=(mx, my, top_z + 0.014), 
                   rotation=(math.radians(15), 0, ang), mat=M_MENMA)
                   
    # Green Scallion (Negi) sliced rings
    for i in range(32):
        ox = bx + random.uniform(-0.035, 0.035)
        oy = by + random.uniform(-0.035, 0.035)
        oz = top_z + 0.018 + random.uniform(0.001, 0.018)
        s_mat = M_SCALLION if random.random() > 0.3 else M_SCALLION_WHITE
        create_torus(f"Scallion_{i}", 0.007, 0.0025, location=(ox, oy, oz), 
                     rotation=(math.radians(random.uniform(-30, 30)), math.radians(random.uniform(-30, 30)), math.radians(random.uniform(0, 360))), 
                     mat=s_mat)
                     
    # Chirirenge (Traditional Ceramic Soup Spoon) resting in bowl
    spoon_loc = (bx + 0.12, by - 0.08, top_z + 0.02)
    create_sphere("Spoon_Bowl", 0.026, location=spoon_loc, scale=(1.6, 0.9, 0.45), mat=M_CERAMIC_WHITE)
    create_box("Spoon_Handle", (0.016, 0.08, 0.008), location=(spoon_loc[0] + 0.04, spoon_loc[1] - 0.04, spoon_loc[2] + 0.03), 
               rotation=(math.radians(-35), math.radians(20), math.radians(-35)), mat=M_CERAMIC_WHITE)
               
    # Wooden Chopsticks resting on ceramic rest
    rest_loc = (bx + 0.28, by - 0.05, bz + 0.012)
    create_box("Hashioki_Rest", (0.035, 0.018, 0.014), location=rest_loc, mat=M_CERAMIC_WHITE)
    for c_i, c_off in enumerate([-0.008, 0.008]):
        create_cylinder(f"Table_Chopstick_{c_i}", 0.004, 0.24, location=(rest_loc[0] + c_off, rest_loc[1], rest_loc[2] + 0.012), 
                        rotation=(math.radians(90), 0, math.radians(5)), mat=M_CHOPSTICK_WOOD)

def build_kitchen_equipment():
    print("Building Kitchen Equipment & Side Dishes...")
    
    # 2 Large Stainless Stock Pots on Prep Counter
    # Pot 1 (Left): Simmering Broth Stock Pot
    pot1_loc = (-0.65, 0.65, 0.88)
    pot1_r = 0.22
    pot1_h = 0.44
    create_cylinder("StockPot_Broth", pot1_r, pot1_h, location=(pot1_loc[0], pot1_loc[1], pot1_loc[2] + pot1_h/2), mat=M_STEEL)
    create_cylinder("StockPot_Liquid", pot1_r - 0.015, 0.02, location=(pot1_loc[0], pot1_loc[1], pot1_loc[2] + pot1_h - 0.04), mat=M_RAMEN_BROTH)
    create_torus("StockPot_Rim", pot1_r, 0.012, location=(pot1_loc[0], pot1_loc[1], pot1_loc[2] + pot1_h), mat=M_STEEL)
    for side in [-1, 1]:
        create_torus(f"StockPot_Handle_{side}", 0.045, 0.01, location=(pot1_loc[0] + side * (pot1_r + 0.02), pot1_loc[1], pot1_loc[2] + pot1_h - 0.08), 
                     rotation=(math.radians(90), 0, 0), mat=M_STEEL)
        
    # Pot 2: Noodle Boiling Tank
    pot2_loc = (-0.20, 0.65, 0.88)
    pot2_r = 0.19
    pot2_h = 0.40
    create_cylinder("NoodlePot", pot2_r, pot2_h, location=(pot2_loc[0], pot2_loc[1], pot2_loc[2] + pot2_h/2), mat=M_STEEL)
    create_cylinder("NoodlePot_Water", pot2_r - 0.015, 0.02, location=(pot2_loc[0], pot2_loc[1], pot2_loc[2] + pot2_h - 0.03), mat=M_STEAM)
    create_torus("NoodlePot_Rim", pot2_r, 0.01, location=(pot2_loc[0], pot2_loc[1], pot2_loc[2] + pot2_h), mat=M_STEEL)
    
    # Wooden Cutting Board on Right Prep Counter
    board_loc = (0.58, 0.62, 0.88)
    create_box("Cutting_Board", (0.44, 0.32, 0.04), location=(board_loc[0], board_loc[1], board_loc[2] + 0.02), mat=M_WOOD_LIGHT)
    
    # Roll of braised chashu pork belly on cutting board
    create_cylinder("Chashu_Roll", 0.055, 0.16, location=(board_loc[0] - 0.08, board_loc[1], board_loc[2] + 0.08), rotation=(0, math.radians(90), 0), mat=M_CHASHU_CRUST)
    for i in range(3):
        create_cylinder(f"Board_Slice_{i}", 0.054, 0.012, location=(board_loc[0] + 0.04 + i * 0.03, board_loc[1], board_loc[2] + 0.05), 
                        rotation=(0, math.radians(90), math.radians(15 * i)), mat=M_CHASHU_MEAT)
        
    # Side Dish: Pan-Fried Gyoza Plate on Counter
    gyoza_plate_loc = (-0.72, -0.28, 0.94)
    create_box("Gyoza_Plate", (0.28, 0.16, 0.015), location=gyoza_plate_loc, mat=M_CERAMIC_WHITE)
    for i in range(4):
        gx = gyoza_plate_loc[0] - 0.09 + i * 0.06
        gy = gyoza_plate_loc[1]
        gz = gyoza_plate_loc[2] + 0.022
        create_sphere(f"Gyoza_Top_{i}", 0.024, location=(gx, gy, gz), scale=(0.8, 1.4, 0.6), mat=M_GYOZA_TOP)
        create_box(f"Gyoza_Base_{i}", (0.028, 0.055, 0.005), location=(gx, gy, gz - 0.01), mat=M_GYOZA_BROWN)
    create_cylinder("Gyoza_Dip_Dish", 0.038, 0.015, location=(gyoza_plate_loc[0] + 0.11, gyoza_plate_loc[1], gyoza_plate_loc[2] + 0.01), mat=M_BOWL_EXT)
    create_cylinder("Gyoza_Sauce", 0.034, 0.006, location=(gyoza_plate_loc[0] + 0.11, gyoza_plate_loc[1], gyoza_plate_loc[2] + 0.018), mat=M_RAMEN_BROTH)
    
    # Condiments on counter (right side)
    c_base = (0.78, -0.28, 0.94)
    shoyu_prof = [(0.0, 0.0), (0.035, 0.0), (0.038, 0.05), (0.022, 0.08), (0.015, 0.11), (0.016, 0.12)]
    create_lathe_mesh("Shoyu_Bottle", shoyu_prof, segments=20, mat=M_CERAMIC_WHITE).location = (c_base[0] - 0.10, c_base[1], c_base[2])
    create_cylinder("Shoyu_Spout", 0.005, 0.035, location=(c_base[0] - 0.12, c_base[1], c_base[2] + 0.095), rotation=(0, math.radians(-45), 0), mat=M_CERAMIC_WHITE)
    
    create_cylinder("Rayu_Jar", 0.032, 0.055, location=(c_base[0] - 0.02, c_base[1], c_base[2] + 0.028), mat=M_LANTERN_RED)
    create_cylinder("Rayu_Lid", 0.035, 0.012, location=(c_base[0] - 0.02, c_base[1], c_base[2] + 0.06), mat=M_LANTERN_BLACK)
    
    create_cylinder("Chopstick_Canister", 0.045, 0.12, location=(c_base[0] + 0.08, c_base[1], c_base[2] + 0.06), mat=M_BOWL_WHITE)
    for i in range(8):
        ang = i * (2.0 * math.pi / 8) + random.uniform(-0.2, 0.2)
        tilt = random.uniform(5, 14)
        create_cylinder(f"Canister_Stick_{i}", 0.0035, 0.22, 
                        location=(c_base[0] + 0.08 + math.cos(ang) * 0.02, c_base[1] + math.sin(ang) * 0.02, c_base[2] + 0.14), 
                        rotation=(math.radians(tilt * math.cos(ang)), math.radians(tilt * math.sin(ang)), 0), mat=M_CHOPSTICK_WOOD)

# ==========================================
# 7. THE OCTOPUS CHEF ("TAKO-SAN")
# ==========================================
def build_octopus_chef():
    print("Sculpting Octopus Chef & 8 Animated Tentacles...")
    
    chef_center = Vector((0.0, 0.20, 1.40))
    
    # Bulbous Mantle Head
    head = create_sphere("Octopus_Head", 0.35, location=chef_center, scale=(1.02, 0.98, 1.18), rings=24, segments=36, mat=M_OCTOPUS)
    
    # Expressive Anime / Chibi Eyes
    eye_z = chef_center.z - 0.02
    eye_y = chef_center.y - 0.30
    eye_spacing = 0.14
    
    for side, sx in [("L", -eye_spacing), ("R", eye_spacing)]:
        create_sphere(f"Eye_White_{side}", 0.070, location=(sx, eye_y, eye_z), scale=(1.0, 0.75, 1.15), mat=M_EYE_WHITE)
        create_sphere(f"Eye_Pupil_{side}", 0.050, location=(sx, eye_y - 0.040, eye_z), scale=(1.0, 0.45, 1.1), mat=M_EYE_PUPIL)
        create_sphere(f"Eye_Glint1_{side}", 0.018, location=(sx + 0.014, eye_y - 0.055, eye_z + 0.020), mat=M_EYE_SPARKLE)
        create_sphere(f"Eye_Glint2_{side}", 0.010, location=(sx - 0.014, eye_y - 0.052, eye_z - 0.016), mat=M_EYE_SPARKLE)
        create_torus(f"Eye_Lid_{side}", 0.068, 0.010, location=(sx, eye_y - 0.02, eye_z + 0.042), rotation=(math.radians(-35), 0, 0), mat=M_OCTOPUS)
        create_sphere(f"Cheek_Blush_{side}", 0.045, location=(sx * 1.65, eye_y + 0.04, eye_z - 0.075), scale=(1.2, 0.3, 0.7), mat=M_BLUSH)
        
    # Cheerful Smiling Mouth (Smiling curve upwards!)
    create_torus("Octopus_Mouth", 0.035, 0.009, location=(0.0, eye_y - 0.02, eye_z - 0.10), rotation=(math.radians(35), 0, 0), mat=M_CHASHU_CRUST)
    
    # Traditional Japanese Chef Headband (Hachimaki)
    hachi_z = chef_center.z + 0.20
    create_torus("Hachimaki_Band", 0.35, 0.030, location=(chef_center.x, chef_center.y, hachi_z), rotation=(math.radians(-14), 0, 0), mat=M_HACHIMAKI)
    create_cylinder("Hachimaki_Sun", 0.048, 0.014, location=(0.0, chef_center.y - 0.33, hachi_z + 0.07), rotation=(math.radians(76), 0, 0), mat=M_HACHIMAKI_RED)
    knot_loc = (chef_center.x + 0.30, chef_center.y + 0.15, hachi_z)
    create_sphere("Hachimaki_Knot", 0.042, location=knot_loc, mat=M_HACHIMAKI)
    create_box("Hachimaki_Tail1", (0.04, 0.14, 0.014), location=(knot_loc[0] + 0.04, knot_loc[1] + 0.06, knot_loc[2] - 0.06), rotation=(math.radians(25), math.radians(-35), math.radians(20)), mat=M_HACHIMAKI)
    create_box("Hachimaki_Tail2", (0.035, 0.17, 0.014), location=(knot_loc[0] + 0.02, knot_loc[1] + 0.08, knot_loc[2] - 0.10), rotation=(math.radians(35), math.radians(-25), math.radians(-10)), mat=M_HACHIMAKI)
    
    # Chef Apron / Collar
    create_cylinder("Chef_Apron_Bib", 0.33, 0.22, location=(chef_center.x, chef_center.y - 0.04, chef_center.z - 0.28), mat=M_APRON)
    
    # ==========================================
    # 8 DYNAMIC TENTACLES IN CHEF ACTION
    # ==========================================
    print("Rigging 8 Specialized Chef Tentacles...")
    base_z = chef_center.z - 0.24
    
    # ----------------------------------------------------
    # TENTACLE 1 (Left): Holding Noodle Strainer Basket (Tebo) dipping in boiling pot
    # ----------------------------------------------------
    t1_pts = [
        Vector((-0.20, 0.12, base_z)),
        Vector((-0.35, 0.16, base_z + 0.05)),
        Vector((-0.46, 0.28, 1.30)),
        Vector((-0.38, 0.48, 1.32)),
        Vector((-0.26, 0.58, 1.25)),
        Vector((-0.20, 0.62, 1.18))
    ]
    create_tentacle("Tentacle_1_Tebo", t1_pts, r_base=0.075, r_tip=0.022)
    tebo_pos = (-0.20, 0.65, 1.12)
    create_cylinder("Tebo_Handle", 0.014, 0.22, location=(tebo_pos[0] - 0.02, tebo_pos[1] - 0.06, tebo_pos[2] + 0.08), rotation=(math.radians(-35), math.radians(20), 0), mat=M_WOOD_LIGHT)
    create_cylinder("Tebo_Basket", 0.065, 0.14, location=(tebo_pos[0], tebo_pos[1], tebo_pos[2] - 0.02), mat=M_STEEL)
    create_cylinder("Tebo_Noodles", 0.060, 0.04, location=(tebo_pos[0], tebo_pos[1], tebo_pos[2] + 0.02), mat=M_RAMEN_NOODLE)
    
    # ----------------------------------------------------
    # TENTACLE 2 (Left-Center High): Chopsticks & Lifted Noodles (Shifted left to fully clear face!)
    # ----------------------------------------------------
    t2_pts = [
        Vector((-0.18, 0.06, base_z)),
        Vector((-0.32, -0.04, 1.28)),
        Vector((-0.44, -0.14, 1.50)),
        Vector((-0.42, -0.22, 1.72)),
        Vector((-0.32, -0.26, 1.78)),
        Vector((-0.24, -0.28, 1.70))
    ]
    create_tentacle("Tentacle_2_Chopsticks", t2_pts, r_base=0.072, r_tip=0.018)
    chop_origin = (-0.26, -0.30, 1.70)
    create_cylinder("Saibashi_Stick1", 0.005, 0.38, location=(chop_origin[0], chop_origin[1], chop_origin[2]), rotation=(math.radians(15), math.radians(72), math.radians(-10)), mat=M_CHOPSTICK_RED)
    create_cylinder("Saibashi_Stick2", 0.005, 0.38, location=(chop_origin[0] + 0.015, chop_origin[1] - 0.02, chop_origin[2]), rotation=(math.radians(12), math.radians(78), math.radians(-12)), mat=M_CHOPSTICK_RED)
    
    # Lifted wavy ramen noodles cascade dripping into left side of bowl
    noodle_start = Vector((chop_origin[0] + 0.02, chop_origin[1] - 0.02, chop_origin[2] - 0.02))
    noodle_end = Vector((-0.12, -0.32, 1.06))
    for n_idx in range(7):
        n_ctrl = []
        offset_x = (n_idx - 3) * 0.010
        for step in range(6):
            t = step / 5.0
            pos = noodle_start.lerp(noodle_end, t)
            w_amp = math.sin(t * math.pi * 5.0 + n_idx) * 0.014
            n_ctrl.append(pos + Vector((offset_x + w_amp, w_amp * 0.5, 0.0)))
        create_tentacle(f"Lifted_Noodle_{n_idx}", n_ctrl, r_base=0.004, r_tip=0.0035, ring_segments=8, mat=M_RAMEN_NOODLE, sucker_step=999)
        
    # ----------------------------------------------------
    # TENTACLE 3 (Right-Center): Holding Broth Ladle pouring into right side of bowl
    # ----------------------------------------------------
    t3_pts = [
        Vector((0.16, 0.06, base_z)),
        Vector((0.28, -0.04, 1.28)),
        Vector((0.36, -0.15, 1.40)),
        Vector((0.32, -0.25, 1.44)),
        Vector((0.22, -0.32, 1.38))
    ]
    create_tentacle("Tentacle_3_Ladle", t3_pts, r_base=0.070, r_tip=0.020)
    ladle_pos = (0.18, -0.34, 1.35)
    create_cylinder("Ladle_Handle", 0.009, 0.28, location=(ladle_pos[0] + 0.08, ladle_pos[1] + 0.06, ladle_pos[2] + 0.06), rotation=(math.radians(-40), math.radians(35), math.radians(-20)), mat=M_WOOD_LIGHT)
    create_sphere("Ladle_Cup", 0.038, location=ladle_pos, scale=(1.0, 1.0, 0.75), mat=M_STEEL)
    create_sphere("Ladle_Liquid", 0.034, location=(ladle_pos[0], ladle_pos[1], ladle_pos[2] + 0.005), scale=(0.95, 0.95, 0.6), mat=M_RAMEN_BROTH)
    
    # Stream of broth pouring into bowl
    pour_ctrl = [
        Vector((ladle_pos[0] - 0.02, ladle_pos[1] - 0.02, ladle_pos[2] - 0.01)),
        Vector((ladle_pos[0] - 0.04, ladle_pos[1] - 0.03, 1.25)),
        Vector((ladle_pos[0] - 0.06, ladle_pos[1] - 0.02, 1.16)),
        Vector((0.06, -0.32, 1.06))
    ]
    create_tentacle("Broth_Pour_Stream", pour_ctrl, r_base=0.012, r_tip=0.008, ring_segments=10, mat=M_RAMEN_BROTH, sucker_step=999)
    
    # ----------------------------------------------------
    # TENTACLE 4 (Right): Holding Chef Knife slicing chashu roll
    # ----------------------------------------------------
    t4_pts = [
        Vector((0.20, 0.10, base_z)),
        Vector((0.36, 0.18, base_z + 0.02)),
        Vector((0.48, 0.35, 1.22)),
        Vector((0.55, 0.50, 1.18)),
        Vector((0.56, 0.60, 1.06))
    ]
    create_tentacle("Tentacle_4_Knife", t4_pts, r_base=0.072, r_tip=0.020)
    knife_loc = (0.56, 0.62, 1.04)
    create_cylinder("Knife_Handle", 0.012, 0.12, location=knife_loc, rotation=(math.radians(90), 0, math.radians(15)), vertices=8, mat=M_WOOD_DARK)
    create_box("Knife_Blade", (0.004, 0.16, 0.045), location=(knife_loc[0] - 0.02, knife_loc[1] - 0.12, knife_loc[2] - 0.01), rotation=(math.radians(10), 0, math.radians(15)), mat=M_STEEL)
    
    # ----------------------------------------------------
    # TENTACLE 5 (Far Right): Holding Shichimi Togarashi Spice Shaker
    # ----------------------------------------------------
    t5_pts = [
        Vector((0.26, 0.14, base_z + 0.04)),
        Vector((0.48, 0.06, 1.26)),
        Vector((0.66, -0.05, 1.34)),
        Vector((0.72, -0.18, 1.30)),
        Vector((0.64, -0.24, 1.22))
    ]
    create_tentacle("Tentacle_5_Shaker", t5_pts, r_base=0.068, r_tip=0.018)
    shaker_pos = (0.62, -0.26, 1.20)
    create_cylinder("Shaker_Body", 0.022, 0.07, location=shaker_pos, rotation=(math.radians(35), math.radians(-25), 0), mat=M_WOOD_LIGHT)
    create_cylinder("Shaker_RedCap", 0.024, 0.02, location=(shaker_pos[0] - 0.01, shaker_pos[1] - 0.015, shaker_pos[2] - 0.035), rotation=(math.radians(35), math.radians(-25), 0), mat=M_HACHIMAKI_RED)
    
    # ----------------------------------------------------
    # TENTACLE 6 (Front Left): Wiping polished cedar counter with folded fukin towel
    # ----------------------------------------------------
    t6_pts = [
        Vector((-0.20, 0.04, base_z - 0.02)),
        Vector((-0.34, -0.10, 1.15)),
        Vector((-0.46, -0.22, 1.05)),
        Vector((-0.48, -0.34, 0.98)),
        Vector((-0.40, -0.40, 0.96))
    ]
    create_tentacle("Tentacle_6_Towel", t6_pts, r_base=0.072, r_tip=0.020)
    towel_loc = (-0.40, -0.40, 0.945)
    create_box("Chef_Towel", (0.12, 0.09, 0.022), location=towel_loc, rotation=(0, 0, math.radians(25)), mat=M_CLOTH_WHITE)
    
    # ----------------------------------------------------
    # TENTACLE 7 (Rear Left): Dynamic arch in background
    # ----------------------------------------------------
    t7_pts = [
        Vector((-0.18, 0.20, base_z + 0.02)),
        Vector((-0.32, 0.30, 1.28)),
        Vector((-0.48, 0.36, 1.50)),
        Vector((-0.55, 0.22, 1.62)),
        Vector((-0.50, 0.10, 1.70)),
        Vector((-0.40, 0.12, 1.76))
    ]
    create_tentacle("Tentacle_7_RearLeft", t7_pts, r_base=0.074, r_tip=0.016)
    
    # ----------------------------------------------------
    # TENTACLE 8 (Rear Right): Dynamic arch framing the chef's silhouette
    # ----------------------------------------------------
    t8_pts = [
        Vector((0.18, 0.20, base_z + 0.02)),
        Vector((0.32, 0.30, 1.28)),
        Vector((0.46, 0.38, 1.48)),
        Vector((0.54, 0.24, 1.62)),
        Vector((0.48, 0.12, 1.72)),
        Vector((0.36, 0.14, 1.76))
    ]
    create_tentacle("Tentacle_8_RearRight", t8_pts, r_base=0.074, r_tip=0.016)

# ==========================================
# 8. STYLIZED STEAM PUFFS
# ==========================================
def create_steam_trails():
    print("Creating Stylized Steam Swirls...")
    steam_sources = [
        Vector((-0.65, 0.65, 1.34)),  # Broth pot
        Vector((-0.20, 0.65, 1.30)),  # Noodle boiler
        Vector((0.08, -0.30, 1.18)),  # Hero ramen bowl (offset from center)
        Vector((-0.26, -0.28, 1.72))  # Lifted hot noodles
    ]
    
    for s_i, origin in enumerate(steam_sources):
        for trail in range(2):
            pts = []
            h_steps = 6
            for step in range(h_steps):
                t = step / (h_steps - 1)
                z = origin.z + t * 0.45
                w = math.sin(t * math.pi * 3.0 + trail * 2.0) * 0.04
                c = math.cos(t * math.pi * 2.5 + trail * 1.5) * 0.03
                pts.append(Vector((origin.x + w, origin.y + c, z)))
            create_tentacle(f"Steam_Trail_{s_i}_{trail}", pts, r_base=0.012, r_tip=0.003, ring_segments=8, mat=M_STEAM, sucker_step=999)

# ==========================================
# 9. LIGHTING & CAMERAS SETUP
# ==========================================
def setup_lighting_and_cameras():
    print("Setting Up Cinematic Lighting & Cameras...")
    
    # 1. Warm overhead pendant light under roof
    pendant = bpy.data.lights.new("Pendant_Light", 'POINT')
    pendant.color = (1.0, 0.82, 0.60)
    pendant.energy = 160.0
    pendant.shadow_soft_size = 0.45
    pendant_obj = bpy.data.objects.new("Pendant_Light", pendant)
    pendant_obj.location = (0.0, -0.10, 2.30)
    link_object(pendant_obj)
    
    # 2. Key food light (soft warm spotlight on counter)
    key_food = bpy.data.lights.new("Key_Food_Light", 'SPOT')
    key_food.color = (1.0, 0.90, 0.78)
    key_food.energy = 85.0
    key_food.spot_size = math.radians(85)
    key_food.spot_blend = 0.7
    key_food.shadow_soft_size = 0.45
    key_food_obj = bpy.data.objects.new("Key_Food_Light", key_food)
    key_food_obj.location = (0.35, -1.50, 2.05)
    key_food_obj.rotation_euler = (math.radians(46), math.radians(14), math.radians(-18))
    link_object(key_food_obj)
    
    # 3. Cool Rim / Back Light (Separates octopus silhouette against dark night)
    rim = bpy.data.lights.new("Rim_Light", 'SPOT')
    rim.color = (0.45, 0.72, 1.0)
    rim.energy = 240.0
    rim.spot_size = math.radians(85)
    rim.spot_blend = 0.4
    rim_obj = bpy.data.objects.new("Rim_Light", rim)
    rim_obj.location = (-0.7, 1.4, 2.4)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(-25), math.radians(145))
    link_object(rim_obj)
    
    # 4. Soft frontal warm fill light
    fill = bpy.data.lights.new("Fill_Light", 'POINT')
    fill.color = (1.0, 0.90, 0.82)
    fill.energy = 140.0
    fill.shadow_soft_size = 0.7
    fill_obj = bpy.data.objects.new("Fill_Light", fill)
    fill_obj.location = (0.0, -2.4, 1.55)
    link_object(fill_obj)
    
    # CAMERAS
    # Camera 1: Hero Front View (Full framed view of booth, chef, food, lanterns)
    cam_hero = bpy.data.cameras.new("Camera_Hero")
    cam_hero.lens = 30
    cam_hero_obj = bpy.data.objects.new("Camera_Hero", cam_hero)
    cam_hero_obj.location = (0.0, -2.85, 1.84)
    cam_hero_obj.rotation_euler = (math.radians(75.5), 0, 0)
    link_object(cam_hero_obj)
    
    # Camera 2: Close-up Food & Chef View (Intimate hero shot showing bowl & smiling chef)
    cam_closeup = bpy.data.cameras.new("Camera_Closeup")
    cam_closeup.lens = 40
    cam_closeup_obj = bpy.data.objects.new("Camera_Closeup", cam_closeup)
    cam_closeup_obj.location = (0.12, -1.68, 1.50)
    cam_closeup_obj.rotation_euler = (math.radians(72), 0, math.radians(5))
    link_object(cam_closeup_obj)
    
    # Camera 3: Three-Quarter Dynamic Perspective View
    cam_angle = bpy.data.cameras.new("Camera_Angle")
    cam_angle.lens = 32
    cam_angle_obj = bpy.data.objects.new("Camera_Angle", cam_angle)
    cam_angle_obj.location = (2.15, -2.15, 1.82)
    cam_angle_obj.rotation_euler = (math.radians(69), math.radians(4), math.radians(44))
    link_object(cam_angle_obj)
    
    scene.camera = cam_hero_obj

# ==========================================
# 10. MAIN EXECUTION PIPELINE
# ==========================================
def main():
    build_booth()
    
    bowl_pos = (0.0, -0.32, 0.935)
    create_ramen_bowl("Hero", bowl_pos, scale=1.0)
    populate_hero_ramen(bowl_pos)
    
    build_kitchen_equipment()
    build_octopus_chef()
    create_steam_trails()
    setup_lighting_and_cameras()
    
    print("=== Octopus Ramen Chef Scene Complete! ===")

if __name__ == "__main__":
    main()
