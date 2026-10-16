"""
Octopus Chef at a Ramen Booth - Full Procedural 3D Scene Generator for Blender
Definitive Edition: Corrected food topping layers, elegant steam wisps, perfect wide camera framing.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

# ==============================================================================
# 1. SCENE CLEANUP & UTILITIES
# ==============================================================================

def clear_scene():
    """Remove all objects and orphan datablocks."""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for collection in [bpy.data.meshes, bpy.data.materials, bpy.data.curves, 
                       bpy.data.lights, bpy.data.cameras, bpy.data.images]:
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)

def smooth_shade(obj):
    """Set smooth shading on an object."""
    for poly in obj.data.polygons:
        poly.use_smooth = True

def add_bevel_modifier(obj, width=0.015, segments=2):
    """Add subtle bevel to hard edges."""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)
    return mod

def add_subsurf_modifier(obj, levels=1, render_levels=2):
    """Add subdivision surface modifier."""
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels
    return mod

# ==============================================================================
# 2. MATERIALS SETUP
# ==============================================================================

def get_or_create_material(name, base_color, roughness=0.5, metallic=0.0, specular=0.5, 
                          subsurface_weight=0.0, subsurface_radius=(1.0, 0.2, 0.1),
                          emission_color=(0, 0, 0, 1), emission_strength=0.0, 
                          transmission=0.0, ior=1.45, alpha=1.0):
    """Robust Principled BSDF material creator compatible with Blender 4/5."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    bsdf.location = (0, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    if 'Base Color' in bsdf.inputs:
        bsdf.inputs['Base Color'].default_value = base_color
    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = roughness
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = metallic
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = ior
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = specular
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = specular
        
    if 'Subsurface Weight' in bsdf.inputs and subsurface_weight > 0:
        bsdf.inputs['Subsurface Weight'].default_value = subsurface_weight
        if 'Subsurface Radius' in bsdf.inputs:
            bsdf.inputs['Subsurface Radius'].default_value = subsurface_radius
    elif 'Subsurface' in bsdf.inputs and subsurface_weight > 0:
        bsdf.inputs['Subsurface'].default_value = subsurface_weight
        
    if 'Emission Color' in bsdf.inputs and emission_strength > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    elif 'Emission' in bsdf.inputs and emission_strength > 0:
        bsdf.inputs['Emission'].default_value = emission_color
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission_strength
            
    if 'Transmission Weight' in bsdf.inputs and transmission > 0:
        bsdf.inputs['Transmission Weight'].default_value = transmission
    elif 'Transmission' in bsdf.inputs and transmission > 0:
        bsdf.inputs['Transmission'].default_value = transmission
        
    if 'Alpha' in bsdf.inputs and alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND'
        
    return mat

def setup_all_materials():
    """Create all materials used in the ramen shop scene."""
    mats = {}
    
    # Rich deep crimson-coral octopus skin
    mats['octopus_skin'] = get_or_create_material(
        'Mat_OctopusSkin', base_color=(0.86, 0.14, 0.09, 1.0), 
        roughness=0.20, specular=0.75, subsurface_weight=0.18, subsurface_radius=(1.0, 0.3, 0.1)
    )
    mats['octopus_sucker'] = get_or_create_material(
        'Mat_OctopusSucker', base_color=(0.98, 0.85, 0.82, 1.0),
        roughness=0.28, specular=0.55, subsurface_weight=0.25
    )
    mats['octopus_blush'] = get_or_create_material(
        'Mat_OctopusBlush', base_color=(0.98, 0.28, 0.42, 1.0),
        roughness=0.45, specular=0.3
    )
    mats['eye_black'] = get_or_create_material(
        'Mat_EyeBlack', base_color=(0.01, 0.01, 0.015, 1.0),
        roughness=0.02, specular=0.98
    )
    mats['eye_white'] = get_or_create_material(
        'Mat_EyeWhite', base_color=(0.98, 0.98, 0.98, 1.0),
        roughness=0.06, specular=0.88
    )
    mats['eye_gleam'] = get_or_create_material(
        'Mat_EyeGleam', base_color=(1.0, 1.0, 1.0, 1.0),
        roughness=0.0, emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=3.0
    )
    
    # Chef Attire
    mats['hachimaki_white'] = get_or_create_material(
        'Mat_HachimakiWhite', base_color=(0.97, 0.96, 0.94, 1.0),
        roughness=0.55, specular=0.35
    )
    mats['hachimaki_red'] = get_or_create_material(
        'Mat_HachimakiRed', base_color=(0.88, 0.08, 0.08, 1.0),
        roughness=0.45, specular=0.4
    )
    mats['apron_navy'] = get_or_create_material(
        'Mat_ApronNavy', base_color=(0.04, 0.08, 0.22, 1.0),
        roughness=0.6, specular=0.3
    )
    mats['apron_white'] = get_or_create_material(
        'Mat_ApronWhite', base_color=(0.96, 0.94, 0.90, 1.0),
        roughness=0.6, specular=0.3
    )
    mats['towel_white'] = get_or_create_material(
        'Mat_TowelWhite', base_color=(0.96, 0.95, 0.93, 1.0),
        roughness=0.75, specular=0.1
    )
    
    # Booth Wood
    mats['wood_counter'] = get_or_create_material(
        'Mat_WoodCounter', base_color=(0.56, 0.30, 0.13, 1.0),
        roughness=0.22, specular=0.72
    )
    mats['wood_dark'] = get_or_create_material(
        'Mat_WoodDark', base_color=(0.14, 0.08, 0.05, 1.0),
        roughness=0.55, specular=0.35
    )
    mats['wood_roof'] = get_or_create_material(
        'Mat_WoodRoof', base_color=(0.22, 0.13, 0.08, 1.0),
        roughness=0.68, specular=0.3
    )
    mats['wood_bamboo'] = get_or_create_material(
        'Mat_WoodBamboo', base_color=(0.80, 0.68, 0.44, 1.0),
        roughness=0.38, specular=0.5
    )
    mats['stool_leather'] = get_or_create_material(
        'Mat_StoolLeather', base_color=(0.18, 0.09, 0.05, 1.0),
        roughness=0.30, specular=0.6
    )
    
    # Metals & Glass
    mats['stainless_steel'] = get_or_create_material(
        'Mat_StainlessSteel', base_color=(0.86, 0.87, 0.89, 1.0),
        roughness=0.16, metallic=0.96, specular=0.95
    )
    mats['dark_metal'] = get_or_create_material(
        'Mat_DarkMetal', base_color=(0.10, 0.10, 0.11, 1.0),
        roughness=0.26, metallic=0.90, specular=0.65
    )
    mats['brass'] = get_or_create_material(
        'Mat_Brass', base_color=(0.92, 0.76, 0.30, 1.0),
        roughness=0.20, metallic=0.92, specular=0.92
    )
    
    # Lanterns & Noren
    mats['lantern_paper'] = get_or_create_material(
        'Mat_LanternPaper', base_color=(0.90, 0.06, 0.04, 1.0),
        roughness=0.45, specular=0.35,
        emission_color=(1.0, 0.25, 0.05, 1.0), emission_strength=2.2
    )
    mats['lantern_black'] = get_or_create_material(
        'Mat_LanternBlack', base_color=(0.02, 0.02, 0.02, 1.0),
        roughness=0.20, specular=0.7
    )
    mats['noren_red'] = get_or_create_material(
        'Mat_NorenRed', base_color=(0.80, 0.09, 0.07, 1.0),
        roughness=0.65, specular=0.25
    )
    mats['noren_cream'] = get_or_create_material(
        'Mat_NorenCream', base_color=(0.98, 0.95, 0.88, 1.0),
        roughness=0.65, specular=0.25
    )
    
    # Food & Bowls
    mats['ceramic_white'] = get_or_create_material(
        'Mat_CeramicWhite', base_color=(0.97, 0.96, 0.94, 1.0),
        roughness=0.08, specular=0.9
    )
    mats['ceramic_pattern'] = get_or_create_material(
        'Mat_CeramicPattern', base_color=(0.85, 0.08, 0.06, 1.0),
        roughness=0.10, specular=0.8
    )
    mats['ramen_broth'] = get_or_create_material(
        'Mat_RamenBroth', base_color=(0.76, 0.40, 0.08, 1.0),
        roughness=0.10, specular=0.95, transmission=0.45, ior=1.35
    )
    mats['noodle'] = get_or_create_material(
        'Mat_Noodle', base_color=(0.98, 0.84, 0.35, 1.0),
        roughness=0.22, specular=0.6, subsurface_weight=0.2
    )
    mats['chashu_meat'] = get_or_create_material(
        'Mat_ChashuMeat', base_color=(0.88, 0.64, 0.54, 1.0),
        roughness=0.35, specular=0.5, subsurface_weight=0.2
    )
    mats['chashu_rim'] = get_or_create_material(
        'Mat_ChashuRim', base_color=(0.28, 0.12, 0.06, 1.0),
        roughness=0.25, specular=0.6
    )
    mats['egg_white'] = get_or_create_material(
        'Mat_EggWhite', base_color=(0.96, 0.95, 0.92, 1.0),
        roughness=0.15, specular=0.7, subsurface_weight=0.25
    )
    mats['egg_yolk'] = get_or_create_material(
        'Mat_EggYolk', base_color=(1.0, 0.54, 0.01, 1.0),
        roughness=0.14, specular=0.85, subsurface_weight=0.45, subsurface_radius=(1.0, 0.5, 0.1)
    )
    mats['naruto_white'] = get_or_create_material(
        'Mat_NarutoWhite', base_color=(0.98, 0.97, 0.95, 1.0),
        roughness=0.22, specular=0.5
    )
    mats['naruto_pink'] = get_or_create_material(
        'Mat_NarutoPink', base_color=(0.98, 0.22, 0.50, 1.0),
        roughness=0.22, specular=0.5
    )
    mats['nori'] = get_or_create_material(
        'Mat_Nori', base_color=(0.05, 0.09, 0.06, 1.0),
        roughness=0.75, specular=0.2
    )
    mats['negi'] = get_or_create_material(
        'Mat_Negi', base_color=(0.14, 0.68, 0.14, 1.0),
        roughness=0.25, specular=0.6
    )
    mats['spice_red'] = get_or_create_material(
        'Mat_SpiceRed', base_color=(0.92, 0.12, 0.06, 1.0),
        roughness=0.75, specular=0.2
    )
    mats['steam'] = get_or_create_material(
        'Mat_Steam', base_color=(1.0, 1.0, 1.0, 1.0),
        roughness=0.15, specular=0.1, transmission=0.88, alpha=0.45, emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=0.3
    )
    
    return mats

# ==============================================================================
# 3. YATAI RAMEN BOOTH BUILDER
# ==============================================================================

def build_yamatai_booth(mats):
    """Create the Japanese ramen food stall structure."""
    booth_objects = []
    
    # 1. Base floor deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.3, 0.05))
    floor = bpy.context.active_object
    floor.name = "Floor_Deck"
    floor.scale = (3.5, 2.9, 0.1)
    floor.data.materials.append(mats['wood_dark'])
    add_bevel_modifier(floor, width=0.01)
    booth_objects.append(floor)
    
    for i in range(-6, 7):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.3 + i * 0.20, 0.105))
        plank = bpy.context.active_object
        plank.name = f"Floor_Plank_{i}"
        plank.scale = (3.46, 0.18, 0.02)
        plank.data.materials.append(mats['wood_dark'])
        add_bevel_modifier(plank, width=0.005)
        booth_objects.append(plank)
        
    # 2. Main Customer Counter (Front Bar)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.4, 0.95))
    counter = bpy.context.active_object
    counter.name = "Counter_Top"
    counter.scale = (2.5, 0.58, 0.08)
    counter.data.materials.append(mats['wood_counter'])
    add_bevel_modifier(counter, width=0.015, segments=3)
    booth_objects.append(counter)
    
    # Counter front panel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.64, 0.45))
    front_panel = bpy.context.active_object
    front_panel.name = "Counter_Front_Panel"
    front_panel.scale = (2.4, 0.04, 0.9)
    front_panel.data.materials.append(mats['wood_dark'])
    add_bevel_modifier(front_panel, width=0.01)
    booth_objects.append(front_panel)
    
    for x in [-1.05, -0.7, -0.35, 0.0, 0.35, 0.7, 1.05]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.67, 0.45))
        slat = bpy.context.active_object
        slat.name = f"Counter_Slat_{x:.2f}"
        slat.scale = (0.05, 0.03, 0.88)
        slat.data.materials.append(mats['wood_roof'])
        booth_objects.append(slat)
        
    for x in [-1.15, 1.15]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.4, 0.45))
        leg = bpy.context.active_object
        leg.name = f"Counter_Side_Leg_{x:.2f}"
        leg.scale = (0.08, 0.52, 0.9)
        leg.data.materials.append(mats['wood_dark'])
        booth_objects.append(leg)
        
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=2.4, location=(0, -0.72, 0.18), rotation=(0, math.pi/2, 0))
    footrest = bpy.context.active_object
    footrest.name = "Footrest_Bar"
    footrest.data.materials.append(mats['dark_metal'])
    booth_objects.append(footrest)
    
    # 3. Chef's Back Work Counter
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.9, 0.85))
    back_counter = bpy.context.active_object
    back_counter.name = "Back_Counter_Top"
    back_counter.scale = (2.4, 0.52, 0.08)
    back_counter.data.materials.append(mats['wood_dark'])
    add_bevel_modifier(back_counter, width=0.01)
    booth_objects.append(back_counter)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.9, 0.42))
    back_body = bpy.context.active_object
    back_body.name = "Back_Counter_Base"
    back_body.scale = (2.36, 0.48, 0.78)
    back_body.data.materials.append(mats['wood_dark'])
    booth_objects.append(back_body)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.14, 1.48))
    shelf1 = bpy.context.active_object
    shelf1.name = "Back_Shelf_High"
    shelf1.scale = (2.3, 0.22, 0.04)
    shelf1.data.materials.append(mats['wood_dark'])
    booth_objects.append(shelf1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.25, 1.35))
    back_wall = bpy.context.active_object
    back_wall.name = "Back_Lattice_Frame"
    back_wall.scale = (2.5, 0.04, 1.7)
    back_wall.data.materials.append(mats['wood_dark'])
    booth_objects.append(back_wall)
    
    for z in [0.7, 0.95, 1.2, 1.45, 1.7, 1.95]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.23, z))
        lattice_h = bpy.context.active_object
        lattice_h.scale = (2.46, 0.02, 0.03)
        lattice_h.data.materials.append(mats['wood_roof'])
        booth_objects.append(lattice_h)
        
    for x in [-1.0, -0.6, -0.2, 0.2, 0.6, 1.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 1.23, 1.35))
        lattice_v = bpy.context.active_object
        lattice_v.scale = (0.03, 0.02, 1.6)
        lattice_v.data.materials.append(mats['wood_roof'])
        booth_objects.append(lattice_v)
        
    # 4. Yatai Pillars & Beams
    pillar_coords = [
        (-1.30, -0.68), (1.30, -0.68),
        (-1.30, 1.15),  (1.30, 1.15)
    ]
    for x, y in pillar_coords:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 1.28))
        pillar = bpy.context.active_object
        pillar.name = f"Pillar_{x:.2f}_{y:.2f}"
        pillar.scale = (0.09, 0.09, 2.36)
        pillar.data.materials.append(mats['wood_dark'])
        add_bevel_modifier(pillar, width=0.008)
        booth_objects.append(pillar)
        
    for x in [-1.30, 1.30]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.24, 2.42))
        beam = bpy.context.active_object
        beam.name = f"Top_Beam_Y_{x:.2f}"
        beam.scale = (0.09, 2.05, 0.1)
        beam.data.materials.append(mats['wood_dark'])
        add_bevel_modifier(beam, width=0.008)
        booth_objects.append(beam)
        
    for y in [-0.68, 1.15]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, 2.42))
        beam = bpy.context.active_object
        beam.name = f"Top_Beam_X_{y:.2f}"
        beam.scale = (2.75, 0.09, 0.1)
        beam.data.materials.append(mats['wood_dark'])
        add_bevel_modifier(beam, width=0.008)
        booth_objects.append(beam)
        
    # 5. Pitched Roof
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 2.62))
    roof_front = bpy.context.active_object
    roof_front.name = "Roof_Front_Slope"
    roof_front.scale = (2.9, 1.30, 0.05)
    roof_front.rotation_euler = (math.radians(18), 0, 0)
    roof_front.data.materials.append(mats['wood_roof'])
    add_bevel_modifier(roof_front, width=0.01)
    booth_objects.append(roof_front)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.54, 2.62))
    roof_back = bpy.context.active_object
    roof_back.name = "Roof_Back_Slope"
    roof_back.scale = (2.9, 1.30, 0.05)
    roof_back.rotation_euler = (math.radians(-18), 0, 0)
    roof_back.data.materials.append(mats['wood_roof'])
    add_bevel_modifier(roof_back, width=0.01)
    booth_objects.append(roof_back)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.24, 2.82))
    roof_ridge = bpy.context.active_object
    roof_ridge.name = "Roof_Ridge_Cap"
    roof_ridge.scale = (2.96, 0.18, 0.08)
    roof_ridge.data.materials.append(mats['wood_dark'])
    add_bevel_modifier(roof_ridge, width=0.01)
    booth_objects.append(roof_ridge)
    
    for x in [-1.25, -0.85, -0.45, 0.0, 0.45, 0.85, 1.25]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.06, 2.65))
        bat_f = bpy.context.active_object
        bat_f.scale = (0.04, 1.28, 0.03)
        bat_f.rotation_euler = (math.radians(18), 0, 0)
        bat_f.data.materials.append(mats['wood_dark'])
        booth_objects.append(bat_f)
        
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.54, 2.65))
        bat_b = bpy.context.active_object
        bat_b.scale = (0.04, 1.28, 0.03)
        bat_b.rotation_euler = (math.radians(-18), 0, 0)
        bat_b.data.materials.append(mats['wood_dark'])
        booth_objects.append(bat_b)

    # 6. Noren Curtain
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=2.5, location=(0, -0.69, 2.34), rotation=(0, math.pi/2, 0))
    noren_rod = bpy.context.active_object
    noren_rod.name = "Noren_Rod"
    noren_rod.data.materials.append(mats['wood_bamboo'])
    booth_objects.append(noren_rod)
    
    panel_width = 0.44
    gap = 0.04
    start_x = -2 * (panel_width + gap)
    for i in range(5):
        px = start_x + i * (panel_width + gap)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.69, 2.14))
        panel = bpy.context.active_object
        panel.name = f"Noren_Panel_{i}"
        panel.scale = (panel_width, 0.012, 0.38)
        panel.rotation_euler = (math.radians(6), 0, 0)
        panel.data.materials.append(mats['noren_red'])
        add_bevel_modifier(panel, width=0.004)
        booth_objects.append(panel)
        
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.70, 2.10))
        symbol = bpy.context.active_object
        symbol.name = f"Noren_Symbol_{i}"
        if i == 2:
            symbol.scale = (0.18, 0.014, 0.18)
        else:
            symbol.scale = (0.13, 0.014, 0.06)
        symbol.rotation_euler = (math.radians(6), 0, 0)
        symbol.data.materials.append(mats['noren_cream'])
        booth_objects.append(symbol)

    # 7. Red Paper Lanterns (Chōchin)
    lantern_positions = [(-1.28, -0.69, 2.06), (1.28, -0.69, 2.06)]
    for idx, (lx, ly, lz) in enumerate(lantern_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.25, location=(lx, ly, lz + 0.22))
        cord = bpy.context.active_object
        cord.data.materials.append(mats['dark_metal'])
        booth_objects.append(cord)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.04, location=(lx, ly, lz + 0.12))
        tcap = bpy.context.active_object
        tcap.data.materials.append(mats['lantern_black'])
        booth_objects.append(tcap)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(lx, ly, lz))
        lbody = bpy.context.active_object
        lbody.name = f"Lantern_Body_{idx}"
        lbody.scale = (1.0, 1.0, 1.45)
        smooth_shade(lbody)
        lbody.data.materials.append(mats['lantern_paper'])
        booth_objects.append(lbody)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.192, depth=0.08, location=(lx, ly, lz))
        cband = bpy.context.active_object
        cband.data.materials.append(mats['lantern_black'])
        booth_objects.append(cband)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.195, depth=0.05, location=(lx, ly - 0.01, lz))
        cband_w = bpy.context.active_object
        cband_w.scale = (0.5, 0.5, 1.0)
        cband_w.data.materials.append(mats['noren_cream'])
        booth_objects.append(cband_w)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.04, location=(lx, ly, lz - 0.26))
        bcap = bpy.context.active_object
        bcap.data.materials.append(mats['lantern_black'])
        booth_objects.append(bcap)
        
        light_data = bpy.data.lights.new(name=f"Light_Lantern_{idx}", type='POINT')
        light_data.energy = 40.0
        light_data.color = (1.0, 0.42, 0.15)
        light_data.shadow_soft_size = 0.25
        light_obj = bpy.data.objects.new(name=f"Light_Lantern_{idx}", object_data=light_data)
        light_obj.location = (lx, ly, lz)
        bpy.context.scene.collection.objects.link(light_obj)
        booth_objects.append(light_obj)

    # 8. Stools
    for sx in [-0.70, 0.70]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.07, location=(sx, -1.15, 0.62))
        seat = bpy.context.active_object
        seat.name = f"Stool_Seat_{sx:.2f}"
        smooth_shade(seat)
        add_bevel_modifier(seat, width=0.015)
        seat.data.materials.append(mats['stool_leather'])
        booth_objects.append(seat)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.03, location=(sx, -1.15, 0.58))
        srim = bpy.context.active_object
        srim.data.materials.append(mats['wood_dark'])
        booth_objects.append(srim)
        
        for angle in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
            leg_x = sx + 0.14 * math.cos(angle)
            leg_y = -1.15 + 0.14 * math.sin(angle)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.58, location=(leg_x, leg_y, 0.30))
            sleg = bpy.context.active_object
            sleg.rotation_euler = (0.1 * math.sin(angle), -0.1 * math.cos(angle), 0)
            sleg.data.materials.append(mats['wood_dark'])
            booth_objects.append(sleg)
            
        bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.01, location=(sx, -1.15, 0.22))
        fring = bpy.context.active_object
        smooth_shade(fring)
        fring.data.materials.append(mats['dark_metal'])
        booth_objects.append(fring)

    return booth_objects

# ==============================================================================
# 4. FOOD & KITCHEN PROPS BUILDER
# ==============================================================================

def build_ramen_bowl(location, rotation, mats, is_hero=True, prefix="HeroRamen"):
    """Create a detailed ceramic ramen bowl with layered broth, noodles, chashu, ajitsuke egg, narutomaki, nori, scallions."""
    bowl_objs = []
    bowl_z = location[2]
    
    # 1. Deep Ceramic Bowl
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.24, depth=0.17,
        location=(location[0], location[1], bowl_z + 0.085)
    )
    bowl = bpy.context.active_object
    bowl.name = f"{prefix}_Bowl"
    bowl.rotation_euler = rotation
    
    bm = bmesh.new()
    bm.from_mesh(bowl.data)
    for v in bm.verts:
        if v.co.z < 0:
            factor = (v.co.z + 0.085) / 0.085
            v.co.x *= (0.55 + 0.45 * factor)
            v.co.y *= (0.55 + 0.45 * factor)
    top_faces = [f for f in bm.faces if f.normal.z > 0.9]
    bmesh.ops.delete(bm, geom=top_faces, context='FACES')
    bmesh.ops.solidify(bm, geom=bm.faces, thickness=0.015)
    bm.to_mesh(bowl.data)
    bm.free()
    
    smooth_shade(bowl)
    bowl.data.materials.append(mats['ceramic_white'])
    add_bevel_modifier(bowl, width=0.008)
    bowl_objs.append(bowl)
    
    # Rim pattern ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.238, minor_radius=0.009,
        location=(location[0], location[1], bowl_z + 0.165)
    )
    bowl_rim = bpy.context.active_object
    bowl_rim.name = f"{prefix}_Rim_Pattern"
    bowl_rim.rotation_euler = rotation
    smooth_shade(bowl_rim)
    bowl_rim.data.materials.append(mats['ceramic_pattern'])
    bowl_objs.append(bowl_rim)
    
    # Foot ring
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.11, depth=0.025,
        location=(location[0], location[1], bowl_z + 0.012)
    )
    foot = bpy.context.active_object
    foot.name = f"{prefix}_Foot"
    foot.rotation_euler = rotation
    smooth_shade(foot)
    foot.data.materials.append(mats['ceramic_white'])
    bowl_objs.append(foot)
    
    # 2. Rich Golden Broth Surface
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.22, depth=0.015,
        location=(location[0], location[1], bowl_z + 0.125)
    )
    broth = bpy.context.active_object
    broth.name = f"{prefix}_Broth"
    broth.rotation_euler = rotation
    smooth_shade(broth)
    broth.data.materials.append(mats['ramen_broth'])
    bowl_objs.append(broth)
    
    # 3. Noodle Base Mound (Flatter bed so toppings rest proudly on top)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.18,
        location=(location[0], location[1], bowl_z + 0.09)
    )
    noodles = bpy.context.active_object
    noodles.name = f"{prefix}_NoodleMound"
    noodles.scale = (1.0, 1.0, 0.28) # Top at bowl_z + 0.14
    noodles.rotation_euler = rotation
    smooth_shade(noodles)
    noodles.data.materials.append(mats['noodle'])
    bowl_objs.append(noodles)
    
    # Wavy noodle coils peeking around edges
    for ang in [0.3, 1.1, 2.0, 2.8, 3.7, 4.5, 5.3]:
        nx = location[0] + 0.095 * math.cos(ang)
        ny = location[1] + 0.095 * math.sin(ang)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.040, minor_radius=0.009,
            location=(nx, ny, bowl_z + 0.138),
            rotation=(0.35 * math.sin(ang), 0.35 * math.cos(ang), ang * 1.5)
        )
        strand = bpy.context.active_object
        strand.scale = (1.1, 0.85, 1.0)
        smooth_shade(strand)
        strand.data.materials.append(mats['noodle'])
        bowl_objs.append(strand)
        
    # 4. Chashu Pork Slices (Thick, clearly elevated on the noodles)
    chashu_offsets = [(-0.06, 0.04, 0.155, 0.35), (0.05, 0.06, 0.160, -0.25)]
    for idx, (dx, dy, dz, rot_z) in enumerate(chashu_offsets):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.068, depth=0.018,
            location=(location[0] + dx, location[1] + dy, bowl_z + dz),
            rotation=(math.radians(14), math.radians(6), rot_z)
        )
        chashu = bpy.context.active_object
        chashu.name = f"{prefix}_Chashu_{idx}"
        chashu.scale = (1.0, 0.85, 1.0)
        smooth_shade(chashu)
        chashu.data.materials.append(mats['chashu_meat'])
        bowl_objs.append(chashu)
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.065, minor_radius=0.007,
            location=(location[0] + dx, location[1] + dy, bowl_z + dz),
            rotation=(math.radians(14), math.radians(6), rot_z)
        )
        crim = bpy.context.active_object
        crim.scale = (1.0, 0.85, 1.0)
        smooth_shade(crim)
        crim.data.materials.append(mats['chashu_rim'])
        bowl_objs.append(crim)
        
    # 5. Ajitsuke Tamago (Half soft-boiled egg with glowing golden-orange yolk)
    ex, ey, ez = location[0] - 0.07, location[1] - 0.05, bowl_z + 0.155
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.058,
        location=(ex, ey, ez),
        rotation=(math.radians(16), math.radians(-12), math.radians(45))
    )
    egg = bpy.context.active_object
    egg.name = f"{prefix}_EggWhite"
    egg.scale = (1.2, 0.9, 0.5)
    smooth_shade(egg)
    egg.data.materials.append(mats['egg_white'])
    bowl_objs.append(egg)
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.035,
        location=(ex + 0.005, ey, ez + 0.018),
        rotation=(math.radians(16), math.radians(-12), math.radians(45))
    )
    yolk = bpy.context.active_object
    yolk.name = f"{prefix}_EggYolk"
    yolk.scale = (1.0, 0.9, 0.45)
    smooth_shade(yolk)
    yolk.data.materials.append(mats['egg_yolk'])
    bowl_objs.append(yolk)
    
    # 6. Narutomaki (White cylinder with bright pink center spiral)
    for n_idx, (ndx, ndy) in enumerate([(0.07, -0.04), (0.10, -0.01)]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.042, depth=0.014,
            location=(location[0] + ndx, location[1] + ndy, bowl_z + 0.156),
            rotation=(math.radians(14), math.radians(5), math.radians(30 * n_idx))
        )
        naruto = bpy.context.active_object
        naruto.name = f"{prefix}_Naruto_{n_idx}"
        smooth_shade(naruto)
        naruto.data.materials.append(mats['naruto_white'])
        bowl_objs.append(naruto)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022, depth=0.015,
            location=(location[0] + ndx, location[1] + ndy, bowl_z + 0.157),
            rotation=(math.radians(14), math.radians(5), math.radians(30 * n_idx))
        )
        npink = bpy.context.active_object
        npink.name = f"{prefix}_NarutoPink_{n_idx}"
        smooth_shade(npink)
        npink.data.materials.append(mats['naruto_pink'])
        bowl_objs.append(npink)
        
    # 7. Nori Seaweed Sheet (Standing angled against rim)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(location[0] - 0.13, location[1] + 0.13, bowl_z + 0.25),
        rotation=(math.radians(-25), math.radians(20), math.radians(-35))
    )
    nori = bpy.context.active_object
    nori.name = f"{prefix}_Nori"
    nori.scale = (0.10, 0.005, 0.18)
    smooth_shade(nori)
    nori.data.materials.append(mats['nori'])
    bowl_objs.append(nori)
    
    # 8. Fresh Scallion Rings (Negi)
    for g_idx in range(16):
        g_angle = g_idx * (2 * math.pi / 16) + 0.15
        g_rad = 0.018 + 0.045 * (g_idx % 3)
        gx = location[0] + g_rad * math.cos(g_angle)
        gy = location[1] + g_rad * math.sin(g_angle)
        gz = bowl_z + 0.158 + 0.004 * (g_idx % 2)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.008, depth=0.006,
            location=(gx, gy, gz),
            rotation=(0.2 * math.cos(g_angle), 0.2 * math.sin(g_angle), g_angle)
        )
        negi = bpy.context.active_object
        smooth_shade(negi)
        negi.data.materials.append(mats['negi'])
        bowl_objs.append(negi)
        
    # 9. Steam Wisps - Smooth curving spirals
    if is_hero:
        for s_idx, (sx_off, sz_off, s_rot) in enumerate([(-0.03, 0.23, 8), (0.02, 0.29, -12), (0.05, 0.35, 15)]):
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.025 + s_idx * 0.008,
                location=(location[0] + sx_off, location[1], bowl_z + sz_off)
            )
            steam = bpy.context.active_object
            steam.name = f"{prefix}_Steam_{s_idx}"
            steam.scale = (0.7, 0.7, 2.2)
            steam.rotation_euler = (math.radians(s_rot), 0, math.radians(s_rot * 2))
            smooth_shade(steam)
            steam.data.materials.append(mats['steam'])
            bowl_objs.append(steam)

    return bowl_objs

def build_kitchen_equipment(mats):
    """Stock pots, strainers, cutting board, condiment bottles, bowls on shelves."""
    equip_objs = []
    
    # 1. Broth Stock Pot
    pot_loc = (-0.72, 0.85, 0.95)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.42, location=(pot_loc[0], pot_loc[1], pot_loc[2] + 0.21))
    pot = bpy.context.active_object
    pot.name = "Broth_Stock_Pot"
    smooth_shade(pot)
    pot.data.materials.append(mats['stainless_steel'])
    equip_objs.append(pot)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.015, location=(pot_loc[0], pot_loc[1], pot_loc[2] + 0.42))
    pot_rim = bpy.context.active_object
    smooth_shade(pot_rim)
    pot_rim.data.materials.append(mats['stainless_steel'])
    equip_objs.append(pot_rim)
    
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.05, minor_radius=0.01,
            location=(pot_loc[0] + side * 0.24, pot_loc[1], pot_loc[2] + 0.35),
            rotation=(math.pi/2, 0, 0)
        )
        handle = bpy.context.active_object
        handle.scale = (0.6, 1.0, 1.0)
        smooth_shade(handle)
        handle.data.materials.append(mats['dark_metal'])
        equip_objs.append(handle)
        
    bpy.ops.mesh.primitive_cylinder_add(radius=0.21, depth=0.02, location=(pot_loc[0], pot_loc[1], pot_loc[2] + 0.38))
    pbroth = bpy.context.active_object
    smooth_shade(pbroth)
    pbroth.data.materials.append(mats['ramen_broth'])
    equip_objs.append(pbroth)
    
    # 2. Second Noodle Boiling Pot
    pot2_loc = (-0.25, 0.85, 0.95)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.35, location=(pot2_loc[0], pot2_loc[1], pot2_loc[2] + 0.175))
    pot2 = bpy.context.active_object
    pot2.name = "Noodle_Boiling_Pot"
    smooth_shade(pot2)
    pot2.data.materials.append(mats['stainless_steel'])
    equip_objs.append(pot2)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.19, depth=0.02,
        location=(pot2_loc[0] + 0.05, pot2_loc[1], pot2_loc[2] + 0.36),
        rotation=(math.radians(15), 0, 0)
    )
    lid = bpy.context.active_object
    smooth_shade(lid)
    lid.data.materials.append(mats['stainless_steel'])
    equip_objs.append(lid)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.025, depth=0.04,
        location=(pot2_loc[0] + 0.05, pot2_loc[1], pot2_loc[2] + 0.385),
        rotation=(math.radians(15), 0, 0)
    )
    lknob = bpy.context.active_object
    lknob.data.materials.append(mats['wood_dark'])
    equip_objs.append(lknob)
    
    # 3. Wooden Cutting Board on Right Counter
    board_loc = (0.55, -0.38, 0.99)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=board_loc)
    board = bpy.context.active_object
    board.name = "Cutting_Board"
    board.scale = (0.42, 0.28, 0.03)
    smooth_shade(board)
    add_bevel_modifier(board, width=0.01)
    board.data.materials.append(mats['wood_bamboo'])
    equip_objs.append(board)
    
    # Chashu roll log
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.055, depth=0.16,
        location=(board_loc[0] - 0.06, board_loc[1], board_loc[2] + 0.05),
        rotation=(0, math.pi/2, math.radians(15))
    )
    chashu_log = bpy.context.active_object
    chashu_log.name = "Chashu_Log"
    smooth_shade(chashu_log)
    chashu_log.data.materials.append(mats['chashu_meat'])
    equip_objs.append(chashu_log)
    
    for s_i, s_offset in enumerate([0.06, 0.09, 0.12]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.055, depth=0.016,
            location=(board_loc[0] + s_offset, board_loc[1] - 0.02 * s_i, board_loc[2] + 0.025),
            rotation=(math.radians(10), math.radians(5), math.radians(20))
        )
        cslice = bpy.context.active_object
        cslice.name = f"Board_Chashu_Slice_{s_i}"
        smooth_shade(cslice)
        cslice.data.materials.append(mats['chashu_meat'])
        equip_objs.append(cslice)

    # 4. Condiment Jars
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.10, location=(0.95, -0.42, 1.04))
    shaker = bpy.context.active_object
    shaker.name = "Shichimi_Jar"
    smooth_shade(shaker)
    shaker.data.materials.append(mats['ceramic_white'])
    equip_objs.append(shaker)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.031, depth=0.03, location=(0.95, -0.42, 1.10))
    shaker_cap = bpy.context.active_object
    shaker_cap.name = "Shichimi_Cap"
    smooth_shade(shaker_cap)
    shaker_cap.data.materials.append(mats['hachimaki_red'])
    equip_objs.append(shaker_cap)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.12, location=(0.85, -0.42, 1.05))
    soy = bpy.context.active_object
    soy.name = "Soy_Sauce_Bottle"
    smooth_shade(soy)
    soy.data.materials.append(mats['dark_metal'])
    equip_objs.append(soy)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.04, location=(0.85, -0.42, 1.12), rotation=(0, math.radians(20), 0))
    spout = bpy.context.active_object
    spout.data.materials.append(mats['brass'])
    equip_objs.append(spout)
    
    # 5. Chopstick Holder
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.12, location=(-0.95, -0.42, 1.05))
    c_cup = bpy.context.active_object
    c_cup.name = "Chopstick_Holder"
    smooth_shade(c_cup)
    c_cup.data.materials.append(mats['wood_dark'])
    equip_objs.append(c_cup)
    
    for c_i in range(8):
        c_ang = c_i * (2 * math.pi / 8)
        cx = -0.95 + 0.02 * math.cos(c_ang)
        cy = -0.42 + 0.02 * math.sin(c_ang)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.004, depth=0.22,
            location=(cx, cy, 1.14),
            rotation=(0.1 * math.sin(c_ang), 0.1 * math.cos(c_ang), c_ang)
        )
        chopstick = bpy.context.active_object
        chopstick.data.materials.append(mats['wood_bamboo'])
        equip_objs.append(chopstick)
        
    # 6. Stacked Bowls on Shelf
    for sx, num_bowls in [(-0.6, 4), (-0.1, 3), (0.4, 5)]:
        for b_i in range(num_bowls):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.10, depth=0.05,
                location=(sx, 1.14, 1.52 + b_i * 0.05)
            )
            s_bowl = bpy.context.active_object
            smooth_shade(s_bowl)
            s_bowl.data.materials.append(mats['ceramic_white'])
            equip_objs.append(s_bowl)

    return equip_objs

# ==============================================================================
# 5. OCTOPUS CHEF & 8 TENTACLES BUILDER
# ==============================================================================

def create_curve_tentacle(name, points_and_radii, bevel_depth=0.09):
    """Build a smooth tapered tentacle using 3D Bezier curve."""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 6
    curve_data.resolution_u = 12
    curve_data.fill_mode = 'FULL'
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points_and_radii) - 1)
    
    for i, (pt_co, rad) in enumerate(points_and_radii):
        bp = spline.bezier_points[i]
        bp.co = pt_co
        bp.radius = rad
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    obj = bpy.data.objects.new(name=name, object_data=curve_data)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def add_suckers_along_points(points_and_dirs, mats, prefix="Sucker"):
    """Place little cup-shaped suckers along tentacle undersides."""
    sucker_objs = []
    for idx, (pos, direction, scale) in enumerate(points_and_dirs):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022 * scale, depth=0.014 * scale,
            location=pos
        )
        sucker = bpy.context.active_object
        sucker.name = f"{prefix}_{idx}"
        
        dir_vec = Vector(direction).normalized()
        rot_quat = Vector((0, 0, 1)).rotation_difference(dir_vec)
        sucker.rotation_euler = rot_quat.to_euler()
        
        smooth_shade(sucker)
        sucker.data.materials.append(mats['octopus_sucker'])
        sucker_objs.append(sucker)
        
        inner_pos = Vector(pos) + dir_vec * (0.003 * scale)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.013 * scale, depth=0.010 * scale,
            location=inner_pos
        )
        inner = bpy.context.active_object
        inner.rotation_euler = rot_quat.to_euler()
        smooth_shade(inner)
        inner.data.materials.append(mats['octopus_blush'])
        sucker_objs.append(inner)
        
    return sucker_objs

def build_octopus_chef(mats):
    """Create the adorable stylized octopus chef with headband, apron, and 8 active tentacles."""
    octopus_objs = []
    
    # 1. Octopus Head & Mantle
    head_loc = Vector((0.0, 0.05, 1.48))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=24, radius=0.32, location=head_loc)
    head = bpy.context.active_object
    head.name = "Octopus_Head"
    head.scale = (1.0, 1.08, 1.25)
    smooth_shade(head)
    head.data.materials.append(mats['octopus_skin'])
    add_subsurf_modifier(head, levels=1)
    octopus_objs.append(head)
    
    # Torso mass behind counter
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.30, location=(0.0, 0.08, 1.15))
    torso = bpy.context.active_object
    torso.name = "Octopus_Torso"
    torso.scale = (1.1, 1.0, 0.9)
    smooth_shade(torso)
    torso.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(torso)
    
    # Siphon / Snout
    siphon_loc = Vector((0.0, -0.28, 1.34))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.12, location=siphon_loc, rotation=(math.radians(35), 0, 0))
    siphon = bpy.context.active_object
    siphon.name = "Octopus_Siphon"
    siphon.scale = (1.0, 0.8, 1.0)
    smooth_shade(siphon)
    siphon.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(siphon)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.03, location=(0.0, -0.33, 1.30), rotation=(math.radians(35), 0, 0))
    mouth = bpy.context.active_object
    mouth.name = "Octopus_Mouth"
    smooth_shade(mouth)
    mouth.data.materials.append(mats['eye_black'])
    octopus_objs.append(mouth)
    
    # Big expressive anime eyes
    eye_x_offset = 0.14
    eye_y = -0.26
    eye_z = 1.46
    
    for side, name_side in [(-1, "L"), (1, "R")]:
        ex = side * eye_x_offset
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(ex, eye_y, eye_z))
        eye_base = bpy.context.active_object
        eye_base.name = f"Eye_Base_{name_side}"
        eye_base.scale = (0.9, 0.5, 1.1)
        eye_base.rotation_euler = (math.radians(-10), side * math.radians(-10), side * math.radians(-12))
        smooth_shade(eye_base)
        eye_base.data.materials.append(mats['eye_white'])
        octopus_objs.append(eye_base)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.058, location=(ex, eye_y - 0.025, eye_z))
        pupil = bpy.context.active_object
        pupil.name = f"Pupil_{name_side}"
        pupil.scale = (0.85, 0.35, 1.05)
        pupil.rotation_euler = (math.radians(-10), side * math.radians(-10), side * math.radians(-12))
        smooth_shade(pupil)
        pupil.data.materials.append(mats['eye_black'])
        octopus_objs.append(pupil)
        
        # Catchlights
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(ex - side * 0.015, eye_y - 0.045, eye_z + 0.025))
        gleam1 = bpy.context.active_object
        gleam1.name = f"Eye_Gleam_Main_{name_side}"
        smooth_shade(gleam1)
        gleam1.data.materials.append(mats['eye_gleam'])
        octopus_objs.append(gleam1)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(ex + side * 0.015, eye_y - 0.045, eye_z - 0.02))
        gleam2 = bpy.context.active_object
        gleam2.name = f"Eye_Gleam_Sub_{name_side}"
        smooth_shade(gleam2)
        gleam2.data.materials.append(mats['eye_gleam'])
        octopus_objs.append(gleam2)
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(ex * 1.5, eye_y + 0.02, eye_z - 0.10))
        blush = bpy.context.active_object
        blush.name = f"Cheek_Blush_{name_side}"
        blush.scale = (0.9, 0.25, 0.5)
        blush.rotation_euler = (0, 0, side * math.radians(20))
        smooth_shade(blush)
        blush.data.materials.append(mats['octopus_blush'])
        octopus_objs.append(blush)

    # 2. Chef's Headband (Hachimaki)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.33, minor_radius=0.038,
        location=(head_loc[0], head_loc[1] + 0.02, head_loc[2] + 0.15),
        rotation=(math.radians(12), 0, 0)
    )
    band = bpy.context.active_object
    band.name = "Hachimaki_Band"
    band.scale = (1.0, 1.05, 1.0)
    smooth_shade(band)
    band.data.materials.append(mats['hachimaki_white'])
    octopus_objs.append(band)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.055, depth=0.014,
        location=(head_loc[0], head_loc[1] - 0.31, head_loc[2] + 0.18),
        rotation=(math.radians(12), 0, 0)
    )
    emblem = bpy.context.active_object
    emblem.name = "Hachimaki_Emblem"
    smooth_shade(emblem)
    emblem.data.materials.append(mats['hachimaki_red'])
    octopus_objs.append(emblem)
    
    knot_loc = (head_loc[0] + 0.34, head_loc[1] + 0.08, head_loc[2] + 0.13)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=knot_loc)
    knot = bpy.context.active_object
    knot.name = "Hachimaki_Knot"
    smooth_shade(knot)
    knot.data.materials.append(mats['hachimaki_white'])
    octopus_objs.append(knot)
    
    for t_idx, (rot_y, len_s) in enumerate([(0.2, 0.15), (-0.3, 0.19)]):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(knot_loc[0] + 0.03, knot_loc[1] + 0.04 * t_idx, knot_loc[2] - 0.08 * t_idx),
            rotation=(math.radians(10), rot_y, math.radians(15))
        )
        tail = bpy.context.active_object
        tail.name = f"Hachimaki_Tail_{t_idx}"
        tail.scale = (0.015, 0.06, len_s)
        smooth_shade(tail)
        tail.data.materials.append(mats['hachimaki_white'])
        octopus_objs.append(tail)

    # 3. Chef Apron (Maekake)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -0.18, 1.05),
        rotation=(math.radians(8), 0, 0)
    )
    apron = bpy.context.active_object
    apron.name = "Chef_Apron"
    apron.scale = (0.46, 0.02, 0.45)
    smooth_shade(apron)
    add_bevel_modifier(apron, width=0.01)
    apron.data.materials.append(mats['apron_navy'])
    octopus_objs.append(apron)
    
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.32, minor_radius=0.015,
        location=(0.0, 0.04, 1.25)
    )
    cord = bpy.context.active_object
    cord.name = "Apron_Cord"
    cord.scale = (1.05, 0.95, 1.0)
    smooth_shade(cord)
    cord.data.materials.append(mats['apron_white'])
    octopus_objs.append(cord)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -0.20, 1.06),
        rotation=(math.radians(8), 0, 0)
    )
    alogo = bpy.context.active_object
    alogo.name = "Apron_Logo"
    alogo.scale = (0.16, 0.005, 0.16)
    alogo.data.materials.append(mats['apron_white'])
    octopus_objs.append(alogo)

    # 4. The 8 Expressive Tentacles & Props
    
    # --- TENTACLE 1: Front-Left, holding Hero Ramen Bowl ---
    t1_pts = [
        (Vector((-0.18, 0.0, 1.18)), 1.0),
        (Vector((-0.28, -0.15, 1.10)), 0.85),
        (Vector((-0.35, -0.30, 1.05)), 0.70),
        (Vector((-0.42, -0.45, 1.03)), 0.55),
        (Vector((-0.30, -0.58, 1.04)), 0.40),
        (Vector((-0.18, -0.48, 1.06)), 0.25)
    ]
    t1 = create_curve_tentacle("Tentacle_1_Serving", t1_pts, bevel_depth=0.075)
    t1.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t1)
    
    suckers_t1 = [
        ((-0.30, -0.18, 1.05), (0.0, 0.0, -1.0), 0.85),
        ((-0.38, -0.34, 1.01), (0.0, 0.0, -1.0), 0.75),
        ((-0.36, -0.52, 1.03), (0.4, 0.3, 0.2), 0.65),
        ((-0.22, -0.54, 1.05), (0.0, 1.0, 0.0), 0.55)
    ]
    octopus_objs.extend(add_suckers_along_points(suckers_t1, mats, "Sucker_T1"))
    
    # --- TENTACLE 2: Back-Left, lifting Noodle Strainer (Tebo) ---
    t2_pts = [
        (Vector((-0.24, 0.12, 1.25)), 1.0),
        (Vector((-0.45, 0.30, 1.38)), 0.82),
        (Vector((-0.55, 0.55, 1.50)), 0.65),
        (Vector((-0.48, 0.70, 1.40)), 0.48),
        (Vector((-0.42, 0.76, 1.30)), 0.30)
    ]
    t2 = create_curve_tentacle("Tentacle_2_Strainer", t2_pts, bevel_depth=0.070)
    t2.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t2)
    
    tebo_loc = (-0.38, 0.80, 1.25)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.016, depth=0.28,
        location=(tebo_loc[0] - 0.08, tebo_loc[1] - 0.08, tebo_loc[2] + 0.12),
        rotation=(math.radians(35), math.radians(-25), 0)
    )
    thandle = bpy.context.active_object
    thandle.data.materials.append(mats['wood_bamboo'])
    octopus_objs.append(thandle)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.18, location=tebo_loc)
    tbasket = bpy.context.active_object
    smooth_shade(tbasket)
    tbasket.data.materials.append(mats['stainless_steel'])
    octopus_objs.append(tbasket)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(tebo_loc[0], tebo_loc[1], tebo_loc[2] + 0.08))
    tnood = bpy.context.active_object
    tnood.scale = (1.0, 1.0, 0.6)
    smooth_shade(tnood)
    tnood.data.materials.append(mats['noodle'])
    octopus_objs.append(tnood)
    
    # --- TENTACLE 3: High-Left, holding Saibashi Chopsticks with noodles ---
    t3_pts = [
        (Vector((-0.20, 0.02, 1.45)), 0.95),
        (Vector((-0.38, -0.05, 1.68)), 0.75),
        (Vector((-0.45, -0.18, 1.76)), 0.55),
        (Vector((-0.36, -0.28, 1.70)), 0.38),
        (Vector((-0.30, -0.25, 1.62)), 0.22)
    ]
    t3 = create_curve_tentacle("Tentacle_3_Chopsticks", t3_pts, bevel_depth=0.065)
    t3.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t3)
    
    for c_off, c_rot in [(-0.015, 0.1), (0.015, -0.05)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.007, depth=0.38,
            location=(-0.30 + c_off, -0.28, 1.58),
            rotation=(math.radians(65), c_rot, math.radians(-20))
        )
        cstick = bpy.context.active_object
        cstick.data.materials.append(mats['wood_bamboo'])
        octopus_objs.append(cstick)
        
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.035, minor_radius=0.012,
        location=(-0.28, -0.34, 1.48),
        rotation=(math.radians(20), math.radians(40), 0)
    )
    ndrape = bpy.context.active_object
    smooth_shade(ndrape)
    ndrape.data.materials.append(mats['noodle'])
    octopus_objs.append(ndrape)
    
    # --- TENTACLE 4: High-Right Arching, holding Broth Ladle high in clear silhouette ---
    t4_pts = [
        (Vector((0.15, 0.05, 1.48)), 0.95),
        (Vector((0.32, -0.02, 1.75)), 0.75),
        (Vector((0.28, -0.18, 1.85)), 0.55),
        (Vector((0.18, -0.25, 1.76)), 0.38),
        (Vector((0.12, -0.22, 1.68)), 0.22)
    ]
    t4 = create_curve_tentacle("Tentacle_4_Ladle", t4_pts, bevel_depth=0.065)
    t4.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t4)
    
    ladle_loc = (0.10, -0.22, 1.62)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.008, depth=0.32,
        location=(ladle_loc[0] + 0.05, ladle_loc[1] + 0.05, ladle_loc[2] + 0.12),
        rotation=(math.radians(-35), math.radians(45), 0)
    )
    lhandle = bpy.context.active_object
    lhandle.data.materials.append(mats['wood_bamboo'])
    octopus_objs.append(lhandle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=ladle_loc)
    lcup = bpy.context.active_object
    lcup.scale = (1.0, 1.0, 0.6)
    smooth_shade(lcup)
    lcup.data.materials.append(mats['stainless_steel'])
    octopus_objs.append(lcup)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.006, depth=0.15,
        location=(ladle_loc[0], ladle_loc[1] - 0.02, ladle_loc[2] - 0.10)
    )
    stream = bpy.context.active_object
    smooth_shade(stream)
    stream.data.materials.append(mats['ramen_broth'])
    octopus_objs.append(stream)
    
    # --- TENTACLE 5: Mid-Right, shaking Spice Shaker ---
    t5_pts = [
        (Vector((0.24, 0.05, 1.38)), 0.95),
        (Vector((0.44, -0.05, 1.52)), 0.75),
        (Vector((0.55, -0.18, 1.48)), 0.55),
        (Vector((0.50, -0.30, 1.38)), 0.38),
        (Vector((0.42, -0.28, 1.32)), 0.22)
    ]
    t5 = create_curve_tentacle("Tentacle_5_Spice", t5_pts, bevel_depth=0.065)
    t5.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t5)
    
    shk_loc = (0.44, -0.32, 1.32)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.026, depth=0.08,
        location=shk_loc,
        rotation=(math.radians(135), 0, math.radians(25))
    )
    held_shk = bpy.context.active_object
    smooth_shade(held_shk)
    held_shk.data.materials.append(mats['wood_bamboo'])
    octopus_objs.append(held_shk)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.027, depth=0.02,
        location=(shk_loc[0] - 0.015, shk_loc[1] - 0.02, shk_loc[2] - 0.03),
        rotation=(math.radians(135), 0, math.radians(25))
    )
    held_cap = bpy.context.active_object
    held_cap.data.materials.append(mats['hachimaki_red'])
    octopus_objs.append(held_cap)
    
    for sp_i in range(5):
        sp_x = shk_loc[0] - 0.02 + 0.01 * (sp_i % 3)
        sp_y = shk_loc[1] - 0.03 - 0.01 * (sp_i // 3)
        sp_z = shk_loc[2] - 0.06 - 0.03 * sp_i
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.005, location=(sp_x, sp_y, sp_z))
        sp_f = bpy.context.active_object
        sp_f.data.materials.append(mats['spice_red'])
        octopus_objs.append(sp_f)

    # --- TENTACLE 6: Low-Right, holding Japanese Santoku Knife ---
    t6_pts = [
        (Vector((0.26, 0.04, 1.22)), 0.95),
        (Vector((0.44, -0.12, 1.18)), 0.78),
        (Vector((0.56, -0.28, 1.15)), 0.60),
        (Vector((0.54, -0.38, 1.10)), 0.42),
        (Vector((0.48, -0.42, 1.08)), 0.25)
    ]
    t6 = create_curve_tentacle("Tentacle_6_Knife", t6_pts, bevel_depth=0.070)
    t6.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t6)
    
    knife_loc = (0.50, -0.38, 1.10)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.014, depth=0.12,
        location=knife_loc,
        rotation=(0, math.radians(70), math.radians(-30))
    )
    k_handle = bpy.context.active_object
    k_handle.data.materials.append(mats['wood_dark'])
    octopus_objs.append(k_handle)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(knife_loc[0] - 0.08, knife_loc[1] + 0.04, knife_loc[2] + 0.02),
        rotation=(0, math.radians(10), math.radians(-30))
    )
    k_blade = bpy.context.active_object
    k_blade.scale = (0.16, 0.004, 0.055)
    smooth_shade(k_blade)
    add_bevel_modifier(k_blade, width=0.003)
    k_blade.data.materials.append(mats['stainless_steel'])
    octopus_objs.append(k_blade)
    
    # --- TENTACLE 7: Far-Right Counter Grip ---
    t7_pts = [
        (Vector((0.24, 0.12, 1.12)), 0.95),
        (Vector((0.52, 0.05, 1.08)), 0.80),
        (Vector((0.74, -0.15, 1.03)), 0.62),
        (Vector((0.82, -0.35, 1.01)), 0.45),
        (Vector((0.76, -0.50, 1.00)), 0.30),
        (Vector((0.68, -0.48, 1.02)), 0.15)
    ]
    t7 = create_curve_tentacle("Tentacle_7_CounterGrip", t7_pts, bevel_depth=0.072)
    t7.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t7)
    
    suckers_t7 = [
        ((0.70, -0.22, 1.00), (0, 0, -1), 0.8),
        ((0.80, -0.36, 0.98), (0, 0, -1), 0.7),
        ((0.75, -0.48, 0.98), (0, 0, -1), 0.6)
    ]
    octopus_objs.extend(add_suckers_along_points(suckers_t7, mats, "Sucker_T7"))
    
    # --- TENTACLE 8: Front-Left Counter, holding White Towel ---
    t8_pts = [
        (Vector((-0.22, 0.10, 1.14)), 0.95),
        (Vector((-0.48, 0.02, 1.06)), 0.80),
        (Vector((-0.68, -0.18, 1.02)), 0.62),
        (Vector((-0.72, -0.36, 1.01)), 0.45),
        (Vector((-0.62, -0.48, 1.01)), 0.28)
    ]
    t8 = create_curve_tentacle("Tentacle_8_Towel", t8_pts, bevel_depth=0.070)
    t8.data.materials.append(mats['octopus_skin'])
    octopus_objs.append(t8)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-0.65, -0.46, 1.01),
        rotation=(0, 0, math.radians(20))
    )
    towel = bpy.context.active_object
    towel.name = "Kitchen_Towel"
    towel.scale = (0.16, 0.12, 0.035)
    smooth_shade(towel)
    add_bevel_modifier(towel, width=0.01)
    towel.data.materials.append(mats['towel_white'])
    octopus_objs.append(towel)

    return octopus_objs

# ==============================================================================
# 6. LIGHTING & CAMERA SETUP
# ==============================================================================

def setup_lighting():
    """Setup multi-point cinematic lighting for warm night-market ambiance."""
    lights = []
    
    # 1. Warm overhead counter key light
    key_data = bpy.data.lights.new(name="Light_Counter_Key", type='AREA')
    key_data.energy = 95.0
    key_data.color = (1.0, 0.88, 0.74)
    key_data.size = 2.2
    key_data.shape = 'RECTANGLE'
    key_data.size_y = 1.0
    key_obj = bpy.data.objects.new(name="Light_Counter_Key", object_data=key_data)
    key_obj.location = (0.0, -0.3, 2.3)
    key_obj.rotation_euler = (math.radians(25), 0, 0)
    bpy.context.scene.collection.objects.link(key_obj)
    lights.append(key_obj)
    
    # 2. Hero food spotlight
    spot_data = bpy.data.lights.new(name="Light_Food_Spot", type='SPOT')
    spot_data.energy = 60.0
    spot_data.color = (1.0, 0.94, 0.84)
    spot_data.spot_size = math.radians(45)
    spot_data.spot_blend = 0.4
    spot_obj = bpy.data.objects.new(name="Light_Food_Spot", object_data=spot_data)
    spot_obj.location = (-0.35, -0.95, 1.90)
    spot_obj.rotation_euler = (math.radians(35), math.radians(-15), 0)
    bpy.context.scene.collection.objects.link(spot_obj)
    lights.append(spot_obj)
    
    # 3. Cool rim light from behind
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 90.0
    rim_data.color = (0.75, 0.90, 1.0)
    rim_data.size = 2.2
    rim_obj = bpy.data.objects.new(name="Light_Rim_Back", object_data=rim_data)
    rim_obj.location = (0.0, 1.6, 2.3)
    rim_obj.rotation_euler = (math.radians(-40), 0, 0)
    bpy.context.scene.collection.objects.link(rim_obj)
    lights.append(rim_obj)
    
    # 4. Front camera fill light (soft, gentle)
    fill_data = bpy.data.lights.new(name="Light_Front_Fill", type='AREA')
    fill_data.energy = 22.0
    fill_data.color = (1.0, 0.94, 0.90)
    fill_data.size = 3.5
    fill_obj = bpy.data.objects.new(name="Light_Front_Fill", object_data=fill_data)
    fill_obj.location = (0.0, -3.5, 1.8)
    fill_obj.rotation_euler = (math.radians(75), 0, 0)
    bpy.context.scene.collection.objects.link(fill_obj)
    lights.append(fill_obj)
    
    return lights

def setup_cameras():
    """Create three carefully framed cameras."""
    cameras = {}
    
    # Camera 1: Hero Full Booth View
    # 26mm lens at Y = -4.40, Z = 1.82 captures the full roof, lanterns, noren, chef, counter, and stools
    cam1_data = bpy.data.cameras.new(name="Camera_Hero")
    cam1_data.lens = 26.0
    cam1_obj = bpy.data.objects.new(name="Camera_Hero", object_data=cam1_data)
    cam1_obj.location = (-0.08, -4.40, 1.82)
    cam1_obj.rotation_euler = (math.radians(78), 0, math.radians(-1))
    bpy.context.scene.collection.objects.link(cam1_obj)
    cameras['hero'] = cam1_obj
    
    # Camera 2: Chef Character Close-Up (Octopus chef from chest up, headband, cheerful eyes, tentacles with ladle and chopsticks, steaming bowl)
    cam2_data = bpy.data.cameras.new(name="Camera_Chef_Portrait")
    cam2_data.lens = 42.0
    cam2_obj = bpy.data.objects.new(name="Camera_Chef_Portrait", object_data=cam2_data)
    cam2_obj.location = (-0.08, -2.25, 1.48)
    cam2_obj.rotation_euler = (math.radians(85), 0, math.radians(-2))
    bpy.context.scene.collection.objects.link(cam2_obj)
    cameras['portrait'] = cam2_obj
    
    # Camera 3: Food Table & Counter Close-Up
    cam3_data = bpy.data.cameras.new(name="Camera_Food_Macro")
    cam3_data.lens = 42.0
    cam3_obj = bpy.data.objects.new(name="Camera_Food_Macro", object_data=cam3_data)
    cam3_obj.location = (-0.38, -1.45, 1.46)
    cam3_obj.rotation_euler = (math.radians(65), 0, math.radians(-14))
    bpy.context.scene.collection.objects.link(cam3_obj)
    cameras['food'] = cam3_obj
    
    bpy.context.scene.camera = cam1_obj
    return cameras

# ==============================================================================
# 7. MAIN ORCHESTRATOR
# ==============================================================================

def main():
    print("--- Starting Octopus Chef Ramen Shop Scene Generation ---")
    clear_scene()
    
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("RamenWorld")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.025, 0.03, 0.045, 1.0)
        bg_node.inputs['Strength'].default_value = 0.7
        
    mats = setup_all_materials()
    build_yamatai_booth(mats)
    build_kitchen_equipment(mats)
    
    # Hero Ramen Bowl on counter (sitting atop counter at Z=0.99)
    build_ramen_bowl(location=(-0.35, -0.42, 0.99), rotation=(0, 0, math.radians(15)), mats=mats, is_hero=True, prefix="HeroRamen")
    
    # Second bowl being prepped on back counter
    build_ramen_bowl(location=(0.15, 0.85, 0.89), rotation=(0, 0, math.radians(-10)), mats=mats, is_hero=False, prefix="PrepRamen")
    
    # Octopus Chef character & tentacles
    build_octopus_chef(mats)
    
    setup_lighting()
    cams = setup_cameras()
    
    print("--- Octopus Chef Ramen Shop Scene Generated Successfully! ---")
    return {
        "status": "success",
        "objects_count": len(bpy.data.objects),
        "materials_count": len(bpy.data.materials),
        "cameras": list(cams.keys())
    }

if __name__ == "__main__":
    result = main()
