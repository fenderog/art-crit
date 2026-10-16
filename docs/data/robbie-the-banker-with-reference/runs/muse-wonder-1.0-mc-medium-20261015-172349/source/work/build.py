import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=0.28, metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bsdf=m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value=(*color,1)
    bsdf.inputs["Roughness"].default_value=rough
    bsdf.inputs["Metallic"].default_value=metal
    return m

YELLOW=mat("YellowPlastic",(1.0,0.66,0.0),0.30)
YELLOW2=mat("YellowPlastic2",(0.95,0.62,0.0),0.32)
BLACK=mat("BlackPlastic",(0.015,0.015,0.018),0.28)
BLACKM=mat("BlackMatte",(0.02,0.02,0.02),0.45)
WHITE=mat("WhitePlastic",(0.96,0.96,0.94),0.25)
BRONZE=mat("EyeRim",(0.28,0.18,0.08),0.35,0.35)
GREY=mat("Ground",(0.92,0.92,0.92),0.9)

def assign(obj,m):
    if m: obj.data.materials.append(m)
    return obj
def finish(obj,m=None):
    assign(obj,m)
    if obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True
    return obj

def lathe(name, profile, material, segments=72):
    verts=[]; faces=[]; rings=[]
    for r,z in profile:
        if r<1e-6:
            rings.append([len(verts)]); verts.append((0,0,z))
        else:
            idx=[]
            for i in range(segments):
                a=2*math.pi*i/segments
                idx.append(len(verts)); verts.append((r*math.cos(a), r*math.sin(a), z))
            rings.append(idx)
    for ri in range(len(rings)-1):
        a=rings[ri]; b=rings[ri+1]
        if len(a)==1:
            for i in range(segments): faces.append((a[0], b[i], b[(i+1)%segments]))
        elif len(b)==1:
            for i in range(segments): faces.append((a[i], b[0], a[(i+1)%segments]))
        else:
            for i in range(segments): faces.append((a[i], b[i], b[(i+1)%segments], a[(i+1)%segments]))
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    return finish(ob,material)

def cyl(name, loc, radius, depth, material, rot=(0,0,0), scale=(1,1,1), verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    ob=bpy.context.object; ob.name=name; ob.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod=ob.modifiers.new("bev","BEVEL"); mod.width=0.02; mod.segments=3
    return finish(ob,material)

def sphere(name, loc, radius, material, scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=radius, location=loc)
    ob=bpy.context.object; ob.name=name; ob.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob,material)

def box(name, loc, size, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob=bpy.context.object; ob.name=name; ob.dimensions=size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod=ob.modifiers.new("bev","BEVEL"); mod.width=min(size)*0.18; mod.segments=3
    return finish(ob,material)

def torus(name, loc, major, minor, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=16, location=loc, rotation=rot)
    ob=bpy.context.object; ob.name=name
    return finish(ob,material)

def tube(name, points, radius, material):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=6; cu.resolution_u=12
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for bp, co in zip(sp.bezier_points, points):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH'); ob=bpy.context.object; ob.name=name
    return finish(ob,material)

def text_obj(name, txt, loc, size, material, rot=(0,0,0), extrude=0.012):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    ob=bpy.context.object; ob.name=name; d=ob.data; d.body=txt; d.align_x='CENTER'; d.align_y='CENTER'; d.size=size; d.extrude=extrude; d.bevel_depth=0.002
    bpy.ops.object.convert(target='MESH'); ob=bpy.context.object; ob.name=name
    return finish(ob,material)

lathe("Body", [(0,0.34),(0.72,0.34),(0.98,0.38),(1.08,0.55),(1.11,0.95),(1.08,1.45),(1.00,1.82),(0.90,1.94),(0,1.94)], YELLOW)
lathe("Head", [(0,2.02),(0.88,2.02),(1.16,2.06),(1.26,2.22),(1.29,2.60),(1.25,2.86),(1.12,3.00),(0,3.02)], YELLOW)
cyl("HeadSeam", (0,0,1.985), 1.13, 0.035, BLACK)
cyl("MouthGap", (0,0,1.94), 1.02, 0.13, BLACK)
cyl("BaseBlack", (0,0,0.28), 1.04, 0.22, BLACK, scale=(1,0.92,1))
box("SeamFront", (0,-1.09,1.05), (0.018,0.03,1.35), BLACKM)
box("SeamBack", (0,1.09,1.05), (0.018,0.03,1.35), BLACKM)
cyl("TopDisc", (0,0,3.03), 1.10, 0.075, BLACK)
for i in range(5):
    box(f"TopRidge{i}", (-0.15, 0.62+i*0.09, 3.075), (1.55,0.035,0.018), BLACKM)
for dx in (-0.09,0.09):
    box("Tooth", (dx,-1.02,1.93), (0.11,0.08,0.16), WHITE)

for sx in (-1,1):
    x=sx*0.40
    cyl("EyeSocket", (x,-1.20,2.52), 0.30, 0.08, BLACKM, rot=(math.radians(90),0,0))
    torus("EyeRim", (x,-1.25,2.52), 0.285, 0.02, BRONZE, rot=(math.radians(90),0,0))
    sphere("Eyeball", (x,-1.24,2.54), 0.255, WHITE, scale=(1,0.48,1))
    sphere("Pupil", (x,-1.345,2.40), 0.165, BLACK, scale=(0.95,0.35,0.72))
    sphere("Highlight", (x-0.06,-1.34,2.62), 0.038, WHITE, scale=(1,0.4,1))

for sx in (-1,1):
    cyl("Shoulder", (sx*1.18,0,1.58), 0.29, 0.34, YELLOW, rot=(0,math.radians(90),0))
    cyl("ShoulderCap", (sx*1.36,0,1.58), 0.285, 0.06, YELLOW2, rot=(0,math.radians(90),0))

tube("ArmHang", [(-1.32,0,1.50),(-1.48,-0.22,1.10),(-1.48,-0.42,0.76),(-1.38,-0.54,0.60)], 0.095, BLACK)
tube("Claw", [(-1.38,-0.54,0.60),(-1.46,-0.60,0.40),(-1.36,-0.64,0.26),(-1.18,-0.64,0.28),(-1.14,-0.62,0.42)], 0.07, BLACK)
tube("ArmTray", [(1.32,0,1.50),(1.50,-0.32,1.24),(1.34,-0.78,1.10),(0.95,-1.02,1.04),(0.72,-1.08,1.04)], 0.095, BLACK)

cyl("Tray", (0.32,-1.12,1.05), 0.46, 0.06, BLACK, scale=(1,1.12,1))
box("TrayTab", (0.32,-0.62,1.05), (0.24,0.32,0.055), BLACK)
torus("DollarRing", (0.32,-1.12,1.085), 0.31, 0.02, WHITE)
text_obj("Dollar", "$", (0.32,-1.12,1.09), 0.50, WHITE, rot=(0,0,math.radians(180)))

def foot(sx):
    ob=sphere("Foot", (sx*0.92,-0.72,0.30), 0.5, YELLOW, scale=(0.70,1.30,0.44))
    for v in ob.data.vertices:
        t=(-v.co.y/0.5)
        if t>0:
            v.co.x*=(1-0.45*t*t); v.co.z*=(1-0.15*t)
    s=sphere("FootSole", (sx*0.92,-0.70,0.11), 0.5, BLACK, scale=(0.72,1.31,0.10))
    for v in s.data.vertices:
        t=(-v.co.y/0.5)
        if t>0: v.co.x*=(1-0.45*t*t)
foot(-1); foot(1)

text_obj("RobieText", "ROBIE", (-0.36,-1.13,1.68), 0.20, BLACK, rot=(math.radians(90),0,0), extrude=0.015)
box("CoinSlot", (0,1.24,2.66), (0.32,0.04,0.05), BLACK)
text_obj("TopBrand", "Radio Shack", (0,0.15,3.075), 0.20, WHITE, rot=(0,0,math.radians(180)))
text_obj("TopSub", "ROBOTIC BANKER", (0,-0.08,3.075), 0.105, WHITE, rot=(0,0,math.radians(180)))
text_obj("TopDollar", "$", (-0.55,0.15,3.075), 0.22, WHITE, rot=(0,0,math.radians(180)))

bpy.ops.mesh.primitive_circle_add(vertices=64, radius=7, fill_type='NGON', location=(0,0,0.02))
g=bpy.context.object; g.name="Ground"; assign(g,GREY)

world=bpy.data.worlds['World']; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(0.95,0.95,0.96,1)
world.node_tree.nodes['Background'].inputs[1].default_value=0.55

def add_light(name, loc, energy, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.size=size
    d=Vector(loc)*-1; l.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return l
add_light("Key", (-4,-5,6), 700, 5)
add_light("Fill", (5,-2,3), 250, 4)
add_light("Rim", (2,5,5), 400, 4)

bpy.ops.object.camera_add(location=(3.2,-5.4,3.9))
cam=bpy.context.object; cam.name="Camera"
d=(Vector((0,0,1.35))-cam.location); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
cam.data.lens=42
bpy.context.scene.camera=cam
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=900; scene.render.resolution_y=900
scene.render.image_settings.file_format='PNG'
scene.eevee.use_shadows=True
result={"objects":[o.name for o in bpy.context.scene.objects]}
