import bpy
import os
import sys
import math
from mathutils import Vector, Euler

# Ensure current working directory is in sys.path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

import generate_textures
import materials
import mesh_utils
import build_booth
import build_chef
import build_food

def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam, do_unlink=True)
    for c in list(bpy.data.curves):
        bpy.data.curves.remove(c, do_unlink=True)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img, do_unlink=True)

def setup_world():
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.016, 0.022, 0.035, 1.0)
        bg_node.inputs["Strength"].default_value = 0.70

def setup_lighting():
    lights = []
    
    # 1. Main Key Spotlight (warm market light focused on counter and chef)
    key_data = bpy.data.lights.new(name="Light_Key", type='SPOT')
    key_data.color = (1.0, 0.94, 0.86)
    key_data.energy = 160.0
    key_data.spot_size = math.radians(72)
    key_data.spot_blend = 0.35
    key_data.shadow_soft_size = 0.12
    key_obj = bpy.data.objects.new(name="Light_Key", object_data=key_data)
    key_obj.location = (0.3, -1.8, 3.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(8), math.radians(-10))
    bpy.context.collection.objects.link(key_obj)
    lights.append(key_obj)
    
    # 2. Food Focus Spotlight (warm pool directly illuminating the hero ramen bowl)
    food_data = bpy.data.lights.new(name="Light_FoodSpot", type='SPOT')
    food_data.color = (1.0, 0.94, 0.82)
    food_data.energy = 70.0
    food_data.spot_size = math.radians(45)
    food_data.spot_blend = 0.45
    food_data.shadow_soft_size = 0.08
    food_obj = bpy.data.objects.new(name="Light_FoodSpot", object_data=food_data)
    food_obj.location = (0.0, -0.65, 1.95)
    food_obj.rotation_euler = (math.radians(35), 0, 0)
    bpy.context.collection.objects.link(food_obj)
    lights.append(food_obj)
    
    # 3. Soft Fill Light (front-left cool ambient fill)
    fill_data = bpy.data.lights.new(name="Light_Fill", type='POINT')
    fill_data.color = (0.80, 0.88, 1.0)
    fill_data.energy = 60.0
    fill_data.shadow_soft_size = 0.4
    fill_obj = bpy.data.objects.new(name="Light_Fill", object_data=fill_data)
    fill_obj.location = (-2.0, -1.8, 2.2)
    bpy.context.collection.objects.link(fill_obj)
    lights.append(fill_obj)
    
    # 4. Front Counter Facade Fill
    front_data = bpy.data.lights.new(name="Light_CounterFront", type='POINT')
    front_data.color = (1.0, 0.78, 0.55)
    front_data.energy = 35.0
    front_data.shadow_soft_size = 0.35
    front_obj = bpy.data.objects.new(name="Light_CounterFront", object_data=front_data)
    front_obj.location = (0.0, -2.0, 0.75)
    bpy.context.collection.objects.link(front_obj)
    lights.append(front_obj)

    # 5. Rim / Hair Backlight (cyan/blue separation rim light)
    rim_data = bpy.data.lights.new(name="Light_Rim", type='SPOT')
    rim_data.color = (0.45, 0.75, 1.0)
    rim_data.energy = 110.0
    rim_data.spot_size = math.radians(75)
    rim_data.spot_blend = 0.4
    rim_data.shadow_soft_size = 0.15
    rim_obj = bpy.data.objects.new(name="Light_Rim", object_data=rim_data)
    rim_obj.location = (0.0, 2.0, 2.7)
    rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))
    bpy.context.collection.objects.link(rim_obj)
    lights.append(rim_obj)
    
    # 6. Back Kitchen Warm Glow
    kitchen_data = bpy.data.lights.new(name="Light_Kitchen", type='POINT')
    kitchen_data.color = (1.0, 0.70, 0.40)
    kitchen_data.energy = 45.0
    kitchen_data.shadow_soft_size = 0.25
    kitchen_obj = bpy.data.objects.new(name="Light_Kitchen", object_data=kitchen_data)
    kitchen_obj.location = (-0.5, 0.9, 1.6)
    bpy.context.collection.objects.link(kitchen_obj)
    lights.append(kitchen_obj)

    return lights

def setup_cameras():
    cameras = {}
    
    # 1. Camera_Hero (Master cinematic establishing shot)
    cam1_data = bpy.data.cameras.new("Cam_Hero_Data")
    cam1_data.lens = 26.0 # wide enough to capture roof, signboard, lanterns, chef, and stools
    cam1_obj = bpy.data.objects.new("Camera_Hero", cam1_data)
    cam1_obj.location = (0.08, -3.85, 2.05)
    cam1_obj.rotation_euler = (math.radians(76.5), 0, math.radians(1.2))
    bpy.context.collection.objects.link(cam1_obj)
    cameras["hero"] = cam1_obj
    
    # 2. Camera_Chef (Medium portrait & dynamic tentacle action)
    cam2_data = bpy.data.cameras.new("Cam_Chef_Data")
    cam2_data.lens = 42.0
    cam2_obj = bpy.data.objects.new("Camera_Chef", cam2_data)
    cam2_obj.location = (0.05, -1.82, 1.48)
    cam2_obj.rotation_euler = (math.radians(82), 0, math.radians(1.5))
    bpy.context.collection.objects.link(cam2_obj)
    cameras["chef"] = cam2_obj
    
    # 3. Camera_Food (Mouthwatering close-up of hero ramen & plating tentacles)
    cam3_data = bpy.data.cameras.new("Cam_Food_Data")
    cam3_data.lens = 48.0
    cam3_obj = bpy.data.objects.new("Camera_Food", cam3_data)
    cam3_obj.location = (0.16, -0.74, 1.38)
    cam3_obj.rotation_euler = (math.radians(62), 0, math.radians(12.0))
    bpy.context.collection.objects.link(cam3_obj)
    cameras["food"] = cam3_obj

    # 4. Camera_Customer (First-person seated perspective looking down at bowl & chef)
    cam4_data = bpy.data.cameras.new("Cam_Customer_Data")
    cam4_data.lens = 32.0
    cam4_obj = bpy.data.objects.new("Camera_Customer", cam4_data)
    cam4_obj.location = (-0.60, -1.15, 1.54)
    cam4_obj.rotation_euler = (math.radians(66), 0, math.radians(-26.0))
    bpy.context.collection.objects.link(cam4_obj)
    cameras["customer"] = cam4_obj
    
    # 5. Camera_Isometric (High 3/4 diorama perspective showing entire roof & kitchen)
    cam5_data = bpy.data.cameras.new("Cam_Isometric_Data")
    cam5_data.lens = 44.0
    cam5_obj = bpy.data.objects.new("Camera_Isometric", cam5_data)
    cam5_obj.location = (3.8, -3.6, 4.0)
    cam5_obj.rotation_euler = (math.radians(52), 0, math.radians(45.0))
    bpy.context.collection.objects.link(cam5_obj)
    cameras["isometric"] = cam5_obj
    
    bpy.context.scene.camera = cam1_obj
    return cameras

def build_entire_scene():
    print("Clearing old scene...")
    clear_scene()
    
    print("Setting up world & environment...")
    setup_world()
    
    print("Generating textures...")
    textures = {
        "noren": generate_textures.create_noren_texture(),
        "lantern": generate_textures.create_lantern_texture(),
        "naruto": generate_textures.create_narutomaki_texture(),
        "chashu": generate_textures.create_chashu_texture(),
        "bowl": generate_textures.create_bowl_pattern_texture(),
    }
    
    print("Creating materials...")
    mats = materials.create_all_materials(textures)
    
    print("Building ramen booth architecture...")
    booth_objs = build_booth.build_booth(mats)
    
    print("Building Octopus Chef & tentacles...")
    chef_objs = build_chef.build_chef(mats)
    
    print("Building food, hero ramen bowl & accessories...")
    food_objs = build_food.build_food(mats)
    
    print("Setting up lighting...")
    lights = setup_lighting()
    
    print("Setting up cinematic cameras...")
    cameras = setup_cameras()
    
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    total_objects = len(bpy.data.objects)
    total_polys = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    total_verts = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    
    return {
        "status": "success",
        "total_objects": total_objects,
        "total_polygons": total_polys,
        "total_vertices": total_verts,
        "cameras": list(cameras.keys())
    }
