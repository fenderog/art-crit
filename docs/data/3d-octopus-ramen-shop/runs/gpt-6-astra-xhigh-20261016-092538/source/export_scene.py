import bpy, os
from collections import defaultdict
bpy.ops.object.select_all(action='DESELECT')
staging=bpy.data.collections.new('GLB export staging'); bpy.context.scene.collection.children.link(staging)
original_collections=[c for c in bpy.context.scene.collection.children if c.name[:2] in ['01','02','03','04','05','06']]
for c in original_collections:
    for src in list(c.objects):
        if src.type not in {'MESH','CURVE','FONT','SURFACE'}: continue
        ob=src.copy(); ob.data=src.data.copy(); staging.objects.link(ob); ob['section']=c.name; ob.select_set(True)
bpy.context.view_layer.objects.active=next(iter(staging.objects))
bpy.ops.object.convert(target='MESH')
# Consolidate compatible parts to keep the interactive model responsive.
groups=defaultdict(list)
for ob in list(staging.objects):
    key=(ob['section'],tuple(m.name if m else '' for m in ob.data.materials))
    groups[key].append(ob)
bpy.ops.object.select_all(action='DESELECT')
for (section,mats),obs in groups.items():
    for ob in obs: ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    if len(obs)>1: bpy.ops.object.join()
    ob=bpy.context.view_layer.objects.active; ob.name=section.split('|')[-1].strip()+' / '+', '.join(mats)
    ob.select_set(False)
for ob in staging.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=next(iter(staging.objects))
path=os.path.join(os.getcwd(),'output','tako-ramen.glb')
bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=False)
result={'path':path,'bytes':os.path.getsize(path),'meshes':len(staging.objects),'vertices':sum(len(o.data.vertices) for o in staging.objects),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in staging.objects)}
for ob in list(staging.objects): bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(staging)
