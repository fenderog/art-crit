import bpy
import os
import sys

# Ensure current working directory is in sys.path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

import build_scene

def run_export():
    out_dir = os.path.abspath("output")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Build the full clean scene
    print("Building full scene...")
    build_info = build_scene.build_entire_scene()
    
    # 2. Export single .glb file (glTF binary, no Draco, no meshopt)
    glb_path = os.path.join(out_dir, "octopus_chef_ramen_booth.glb")
    print(f"Exporting GLB to {glb_path}...")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        export_draco_mesh_compression_enable=False,
        export_image_format='AUTO',
        export_apply=True
    )
    
    glb_size = os.path.getsize(glb_path)
    glb_size_mb = glb_size / (1024 * 1024)
    print(f"GLB exported: {glb_size_mb:.2f} MB (limit 15 MB)")
    
    # 3. Render final images from chosen cinematic cameras
    cameras_to_render = [
        ("Camera_Hero", "octopus_ramen_booth_hero.jpg", 1920, 1080),
        ("Camera_Chef", "octopus_chef_portrait.jpg", 1920, 1080),
        ("Camera_Food", "ramen_bowl_closeup.jpg", 1920, 1080),
        ("Camera_Customer", "customer_pov.jpg", 1920, 1080),
        ("Camera_Isometric", "booth_isometric_diorama.jpg", 1920, 1080)
    ]
    
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 92 # high quality JPEG, compact size ~400-800KB
    
    renders_info = []
    for cam_name, file_name, rx, ry in cameras_to_render:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: camera {cam_name} not found!")
            continue
            
        scene.camera = cam_obj
        scene.render.resolution_x = rx
        scene.render.resolution_y = ry
        scene.render.resolution_percentage = 100
        
        img_path = os.path.join(out_dir, file_name)
        scene.render.filepath = img_path
        print(f"Rendering {cam_name} to {file_name}...")
        bpy.ops.render.render(write_still=True)
        
        img_size = os.path.getsize(img_path)
        img_size_mb = img_size / (1024 * 1024)
        renders_info.append({
            "name": file_name,
            "camera": cam_name,
            "size_bytes": img_size,
            "size_mb": round(img_size_mb, 2),
            "under_2mb": img_size_mb < 2.0
        })
        print(f"Rendered {file_name}: {img_size_mb:.2f} MB")
        
    all_files = os.listdir(out_dir)
    return {
        "status": "success",
        "output_dir": out_dir,
        "total_files": len(all_files),
        "files": all_files,
        "glb": {
            "name": "octopus_chef_ramen_booth.glb",
            "size_bytes": glb_size,
            "size_mb": round(glb_size_mb, 2),
            "under_15mb": glb_size_mb < 15.0
        },
        "renders": renders_info,
        "scene_stats": build_info
    }

if __name__ == "__main__":
    res = run_export()
    print("Export Summary:", res)
