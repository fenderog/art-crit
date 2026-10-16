# glTF export: make materials glTF-friendly, pick the diorama objects, write a .glb.
EXPORT_COLLS = {"Booth", "Kitchen", "Octopus", "Steam"}
STREET_KEEP = ("Crate_", "Bucket", "Gas_Tank", "Gas_Hose")


def sanitize_materials_for_gltf():
    """Strip render-only shading (bump from colour, procedural roughness, volumetric steam)
    so every material maps cleanly onto glTF PBR."""
    for m in bpy.data.materials:
        nt = m.node_tree
        if nt is None:
            continue
        for n in list(nt.nodes):
            if n.get("render_only"):
                nt.nodes.remove(n)
        out = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial']
        if not out:
            continue
        out = out[0]
        if m.get("steam"):
            for n in list(nt.nodes):
                if n.name != out.name:
                    nt.nodes.remove(n)
            p = nt.nodes.new('ShaderNodeBsdfPrincipled')
            p.inputs['Base Color'].default_value = (1.0, 0.98, 0.95, 1)
            p.inputs['Roughness'].default_value = 1.0
            p.inputs['Alpha'].default_value = 0.10
            p.inputs['Emission Color'].default_value = (1.0, 0.95, 0.9, 1)
            p.inputs['Emission Strength'].default_value = 0.15
            nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
            m.surface_render_method = 'BLENDED'
            continue
        ps = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled']
        if not ps:
            continue
        p = ps[0]
        for sock in ('Roughness', 'Metallic', 'Normal'):
            for l in list(p.inputs[sock].links):
                if l.from_node.bl_idname not in ('ShaderNodeTexImage', 'ShaderNodeNormalMap'):
                    nt.links.remove(l)


def build_glb_base():
    """Round asphalt base so the exported diorama sits on a patch of wet street."""
    gm = bpy.data.materials.get("Asphalt_Wet")
    C = get_coll("GLB_Only")
    verts, faces = [], []
    n = 72
    R = 3.0
    cx, cy = 0.15, 0.25
    verts.append((cx, cy, 0.0))
    for i in range(n):
        a = 2 * PI * i / n
        verts.append((cx + math.cos(a) * R, cy + math.sin(a) * R, 0.0))
    for i in range(n):
        a = 2 * PI * i / n
        verts.append((cx + math.cos(a) * R, cy + math.sin(a) * R, -0.08))
    for i in range(n):
        j = (i + 1) % n
        faces.append([0, 1 + i, 1 + j])
        faces.append([1 + i, 1 + n + i, 1 + n + j, 1 + j])
    ob = obj_from_data("GLB_Street_Base", verts, faces, gm, C, smooth=False)
    me = ob.data
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (co.x / 2.0, co.y / 2.0 + co.z)
    return ob


def export_glb(path):
    sanitize_materials_for_gltf()
    base = build_glb_base()
    for ob in bpy.context.scene.objects:
        ob.select_set(False)
    chosen = []
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        cols = {c.name for c in ob.users_collection}
        keep = bool(cols & EXPORT_COLLS) or ob.name == base.name
        if "Street" in cols and ob.name.startswith(STREET_KEEP):
            keep = True
        if keep:
            ob.select_set(True)
            chosen.append(ob)
    bpy.context.view_layer.objects.active = chosen[0]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_lights=False, export_cameras=False,
                              export_draco_mesh_compression_enable=False,
                              export_meshopt_compression_enable=False,
                              export_image_format='AUTO', export_yup=True)
    return {"objects": len(chosen), "size_mb": os.path.getsize(path) / 1e6}
