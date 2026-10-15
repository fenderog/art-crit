import bpy, bmesh, math
from mathutils import Vector
M = {n:bpy.data.materials[k] for n,k in dict(body='BodyCream',blue='PaintBlue',green='VisorGreen',dark='DarkPlastic',chrome='Chrome',gold='Gold',red='RedPlastic',eye='EyeGlow',white='White').items()}
col = bpy.data.collections["Robie"]
X90=(math.pi/2,0,0)
def fin(o, m, bevel=0.0, smooth=True, name=None):
    if name: o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    if m: o.data.materials.append(M[m])
    if smooth:
        for p in o.data.polygons: p.use_smooth=True
    if bevel>0:
        md=o.modifiers.new("Bevel",'BEVEL'); md.width=bevel; md.segments=4; md.limit_method='ANGLE'
    return o
def box(name,loc,size,m,bevel=0.03,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot)
    o=bpy.context.active_object; o.scale=size
    bpy.ops.object.transform_apply(scale=True)
    return fin(o,m,bevel,True,name)
def cyl(name,loc,r,d,m,rot=(0,0,0),bevel=0.0,verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d,location=loc,rotation=rot)
    return fin(bpy.context.active_object,m,bevel,True,name)
def sph(name,loc,r,m,scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=r,location=loc)
    o=bpy.context.active_object; o.scale=scale
    return fin(o,m,0,True,name)
def text(name,body,loc,size,m,ext=0.01):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0))
    t=bpy.context.active_object; t.data.body=body; t.data.size=size
    t.data.align_x='CENTER'; t.data.align_y='CENTER'; t.data.extrude=ext
    bpy.ops.object.convert(target='MESH')
    o=bpy.context.active_object
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.append(M[m]); o.name=name
    return o
def limb(name,p0,p1,r,m):
    p0=Vector(p0);p1=Vector(p1);d=p1-p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d.length,location=(p0+p1)/2)
    o=bpy.context.active_object
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return fin(o,m,0,True,name)
