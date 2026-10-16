import bpy

def get_or_create_material(name, base_color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0, 
                           emission_color=None, emission_strength=0.0, alpha=1.0, image_tex=None):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = base_color
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
        if alpha < 1.0:
            mat.blend_method = 'BLEND'
            
    if image_tex:
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.image = image_tex
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        if emission_strength > 0 and "Emission Color" in bsdf.inputs:
            links.new(tex_node.outputs["Color"], bsdf.inputs["Emission Color"])
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
        if alpha < 1.0 or "Alpha" in tex_node.outputs:
            links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
            mat.blend_method = 'CLIP'
    elif emission_color and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission_color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
            
    return mat

def create_all_materials(textures):
    mats = {}
    
    # Octopus Chef
    mats["OctopusSkin"] = get_or_create_material(
        "Mat_OctopusSkin", 
        base_color=(0.92, 0.22, 0.16, 1.0), 
        roughness=0.28, 
        metallic=0.0
    )
    mats["OctopusPeach"] = get_or_create_material(
        "Mat_OctopusPeach", 
        base_color=(0.98, 0.90, 0.85, 1.0), 
        roughness=0.22, 
        metallic=0.0
    )
    mats["OctopusBlush"] = get_or_create_material(
        "Mat_OctopusBlush", 
        base_color=(0.96, 0.38, 0.48, 1.0), 
        roughness=0.35
    )
    mats["EyeWhite"] = get_or_create_material(
        "Mat_EyeWhite", 
        base_color=(0.98, 0.98, 0.98, 1.0), 
        roughness=0.08
    )
    mats["EyePupil"] = get_or_create_material(
        "Mat_EyePupil", 
        base_color=(0.04, 0.03, 0.04, 1.0), 
        roughness=0.08
    )
    mats["EyeShine"] = get_or_create_material(
        "Mat_EyeShine", 
        base_color=(1.0, 1.0, 1.0, 1.0), 
        roughness=0.0,
        emission_color=(1.0, 1.0, 1.0, 1.0), 
        emission_strength=2.5
    )
    
    # Chef Attire
    mats["ChefHat"] = get_or_create_material(
        "Mat_ChefHat", 
        base_color=(0.98, 0.98, 0.98, 1.0), 
        roughness=0.60
    )
    mats["HachimakiRed"] = get_or_create_material(
        "Mat_HachimakiRed", 
        base_color=(0.92, 0.14, 0.12, 1.0), 
        roughness=0.55
    )
    mats["Apron"] = get_or_create_material(
        "Mat_Apron", 
        base_color=(0.08, 0.14, 0.26, 1.0), 
        roughness=0.70
    )
    mats["ApronStrap"] = get_or_create_material(
        "Mat_ApronStrap", 
        base_color=(0.95, 0.94, 0.90, 1.0), 
        roughness=0.60
    )
    
    # Booth Woodwork
    mats["WoodCounter"] = get_or_create_material(
        "Mat_WoodCounter", 
        base_color=(0.58, 0.34, 0.18, 1.0), 
        roughness=0.28
    )
    mats["WoodTimber"] = get_or_create_material(
        "Mat_WoodTimber", 
        base_color=(0.32, 0.18, 0.10, 1.0), 
        roughness=0.58
    )
    mats["WoodPlank"] = get_or_create_material(
        "Mat_WoodPlank", 
        base_color=(0.46, 0.28, 0.15, 1.0), 
        roughness=0.48
    )
    mats["RoofTile"] = get_or_create_material(
        "Mat_RoofTile", 
        base_color=(0.20, 0.22, 0.25, 1.0), 
        roughness=0.45
    )
    mats["StoneFloor"] = get_or_create_material(
        "Mat_StoneFloor", 
        base_color=(0.18, 0.20, 0.22, 1.0), 
        roughness=0.70
    )
    mats["Brass"] = get_or_create_material(
        "Mat_Brass", 
        base_color=(0.95, 0.82, 0.36, 1.0), 
        metallic=0.88, 
        roughness=0.22
    )
    
    # Fabric & Lanterns
    mats["Noren"] = get_or_create_material(
        "Mat_Noren", 
        image_tex=textures["noren"], 
        roughness=0.75
    )
    mats["Lantern"] = get_or_create_material(
        "Mat_Lantern", 
        image_tex=textures["lantern"], 
        roughness=0.35,
        emission_strength=0.8
    )
    mats["LanternBlack"] = get_or_create_material(
        "Mat_LanternBlack", 
        base_color=(0.06, 0.05, 0.05, 1.0), 
        roughness=0.35
    )
    
    # Kitchen Metals & Tools
    mats["StainlessSteel"] = get_or_create_material(
        "Mat_StainlessSteel", 
        base_color=(0.88, 0.90, 0.92, 1.0), 
        metallic=0.92, 
        roughness=0.18
    )
    mats["Bamboo"] = get_or_create_material(
        "Mat_Bamboo", 
        base_color=(0.88, 0.76, 0.50, 1.0), 
        roughness=0.40
    )
    mats["WireMesh"] = get_or_create_material(
        "Mat_WireMesh", 
        base_color=(0.78, 0.80, 0.82, 1.0), 
        metallic=0.85, 
        roughness=0.30
    )
    
    # Ramen & Ingredients
    mats["BowlRed"] = get_or_create_material(
        "Mat_BowlRed", 
        base_color=(0.84, 0.12, 0.10, 1.0), 
        roughness=0.18
    )
    mats["BowlBlack"] = get_or_create_material(
        "Mat_BowlBlack", 
        base_color=(0.08, 0.08, 0.09, 1.0), 
        roughness=0.16
    )
    mats["BowlWhite"] = get_or_create_material(
        "Mat_BowlWhite", 
        base_color=(0.97, 0.96, 0.94, 1.0), 
        roughness=0.14
    )
    mats["Broth"] = get_or_create_material(
        "Mat_Broth", 
        base_color=(0.82, 0.48, 0.12, 1.0), 
        roughness=0.08, 
        metallic=0.0
    )
    mats["Noodles"] = get_or_create_material(
        "Mat_Noodles", 
        base_color=(0.96, 0.84, 0.42, 1.0), 
        roughness=0.35
    )
    mats["EggWhite"] = get_or_create_material(
        "Mat_EggWhite", 
        base_color=(0.98, 0.97, 0.94, 1.0), 
        roughness=0.22
    )
    mats["EggRim"] = get_or_create_material(
        "Mat_EggRim", 
        base_color=(0.46, 0.26, 0.14, 1.0), 
        roughness=0.28
    )
    mats["EggYolk"] = get_or_create_material(
        "Mat_EggYolk", 
        base_color=(1.0, 0.58, 0.04, 1.0), 
        roughness=0.10
    )
    mats["Naruto"] = get_or_create_material(
        "Mat_Naruto", 
        image_tex=textures["naruto"], 
        roughness=0.28
    )
    mats["Chashu"] = get_or_create_material(
        "Mat_Chashu", 
        image_tex=textures["chashu"], 
        roughness=0.32
    )
    mats["Nori"] = get_or_create_material(
        "Mat_Nori", 
        base_color=(0.05, 0.08, 0.05, 1.0), 
        roughness=0.55
    )
    mats["Negi"] = get_or_create_material(
        "Mat_Negi", 
        base_color=(0.26, 0.76, 0.15, 1.0), 
        roughness=0.32
    )
    mats["Menma"] = get_or_create_material(
        "Mat_Menma", 
        base_color=(0.78, 0.54, 0.26, 1.0), 
        roughness=0.30
    )
    mats["Steam"] = get_or_create_material(
        "Mat_Steam", 
        base_color=(0.96, 0.98, 1.0, 1.0), 
        roughness=0.9, 
        alpha=0.20
    )
    
    return mats
