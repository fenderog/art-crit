import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def create_cube(name, location=(0,0,0), scale=(1,1,1), material=None, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def create_cylinder(name, location=(0,0,0), radius=0.5, depth=1.0, vertices=24, material=None, rotation=(0,0,0), scale=(1,1,1), unwrap_caps=False):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if unwrap_caps:
        unwrap_cylinder_caps(obj, radius * scale[0])
    if material:
        obj.data.materials.append(material)
    return obj

def unwrap_cylinder_caps(obj, radius):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    
    for face in bm.faces:
        if abs(face.normal.z) > 0.7:
            for loop in face.loops:
                v = loop.vert.co
                u = 0.5 + 0.5 * (v.x / max(1e-4, radius))
                v_coord = 0.5 + 0.5 * (v.y / max(1e-4, radius))
                loop[uv_layer].uv = (u, v_coord)
                
    bm.to_mesh(obj.data)
    bm.free()

def create_sphere(name, location=(0,0,0), radius=0.5, segments=24, ring_count=16, material=None, scale=(1,1,1), rotation=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=ring_count, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def create_torus(name, location=(0,0,0), major_radius=0.5, minor_radius=0.1, major_segments=24, minor_segments=12, material=None, rotation=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, minor_radius=minor_radius,
        major_segments=major_segments, minor_segments=minor_segments,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def create_plane(name, location=(0,0,0), size=1.0, material=None, rotation=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def smooth_shade(obj):
    if obj and obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
