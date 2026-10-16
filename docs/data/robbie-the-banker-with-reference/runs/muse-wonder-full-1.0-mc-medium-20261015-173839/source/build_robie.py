import bpy, math, os
from mathutils import Vector

# ---------- clean ----------
# clear scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for c in list(bpy.data.cameras):
    bpy.data.cameras.remove(c)
for l in list(bpy.data.lights):
    bpy.data.lights.remove(l)
for c in list(bpy.data.curves):
    bpy.data.curves.remove(c)
scene = bpy.context.scene

def mat(name, color, rough=0.3, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    # coat if available
    for k in ("Coat Weight","Clearcoat"):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.55
    for k in ("Coat Roughness","Clearcoat Roughness"):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.22
    return m

YELLOW = mat("YellowPlastic", (1.0, 0.66, 0.005), 0.22)
YELLOW2 = mat("YellowPlastic2", (1.0, 0.65, 0.005), 0.28)
BLACK = mat("BlackPlastic", (0.012, 0.012, 0.014), 0.32)
BLACKSOFT = mat("BlackSoft", (0.03,0.03,0.035), 0.45)
WHITE = mat("White", (0.95,0.95,0.93), 0.28)
EYEWHITE = mat("EyeWhite", (0.88,0.87,0.84), 0.18)
DARKBROWN = mat("EyeRim", (0.08,0.05,0.03), 0.35, 0.2)
GRAY = mat("GraySeam", (0.15,0.13,0.02), 0.5)
GROOVE = mat("Groove", (0.30,0.20,0.0), 0.45)
_bs=BLACKSOFT.node_tree.nodes["Principled BSDF"]
for _k in ("Coat Weight","Clearcoat"):
    if _k in _bs.inputs: _bs.inputs[_k].default_value=0.05

def assign(obj, material):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.append(material)
    return obj

def smooth(obj):
    if obj.type=='MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def bevel(obj, width=0.02, seg=3):
    mod = obj.modifiers.new("bev","BEVEL"); mod.width=width; mod.segments=seg
    return obj

# ---------- lathe helper ----------
def lathe(name, profile, material, segments=64):
    # profile: list of (r,z) bottom center -> ... -> top center
    verts=[]; faces=[]
    # rings for r>0
    rings=[]
    for (r,z) in profile:
        if r<=0.0001:
            rings.append(None); continue
        idx=[]
        for i in range(segments):
            a=2*math.pi*i/segments
            idx.append(len(verts)); verts.append((r*math.cos(a), r*math.sin(a), z))
        rings.append(idx)
    # center verts
    centers=[]
    for (r,z) in profile:
        if r<=0.0001:
            centers.append(len(verts)); verts.append((0,0,z))
        else:
            centers.append(None)
    for i in range(len(profile)-1):
        r0=profile[i][0]; r1=profile[i+1][0]
        if r0>0 and r1>0:
            a=rings[i]; b=rings[i+1]
            for j in range(segments):
                j2=(j+1)%segments
                faces.append((a[j], a[j2], b[j2], b[j]))
        elif r0<=0 and r1>0:
            c=centers[i]; b=rings[i+1]
            for j in range(segments):
                j2=(j+1)%segments
                faces.append((c, b[j2], b[j]))  # bottom fan winding approx
        elif r0>0 and r1<=0:
            c=centers[i+1]; a=rings[i]
            for j in range(segments):
                j2=(j+1)%segments
                faces.append((a[j], a[j2], c))
    me=bpy.data.meshes.new(name+"Mesh"); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); scene.collection.objects.link(ob)
    assign(ob,material); smooth(ob)
    return ob

def cylinder(name, loc, radius, depth, material, rot=(0,0,0), verts=48, scale=(1,1,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    ob=bpy.context.active_object; ob.name=name; ob.scale=scale
    assign(ob,material); smooth(ob)
    return ob

def sphere(name, loc, radius, material, scale=(1,1,1), rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=radius, location=loc, rotation=rot)
    ob=bpy.context.active_object; ob.name=name; ob.scale=scale
    assign(ob,material); smooth(ob)
    return ob

def torus(name, loc, major, minor, material, rot=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=16, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    ob=bpy.context.active_object; ob.name=name; ob.scale=scale
    assign(ob,material); smooth(ob)
    return ob

def box(name, loc, size, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    ob=bpy.context.active_object; ob.name=name; ob.dimensions=size
    assign(ob,material)
    return ob

def curve_tube(name, points, radius, material, taper_tip=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    cu.bevel_depth=radius; cu.bevel_resolution=5; cu.resolution_u=12
    cu.fill_mode='FULL'
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for bp, co in zip(sp.bezier_points, points):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'; bp.radius=1.0
    if taper_tip:
        sp.bezier_points[-1].radius=0.55
        sp.bezier_points[0].radius=0.9
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob)
    assign(ob,material)
    # convert to mesh
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    ob=bpy.context.active_object; smooth(ob)
    return ob

def text_obj(name, txt, loc, rot, size, material, extrude=0.006, align='CENTER', fat=0.0):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=txt; cu.size=size; cu.extrude=extrude
    cu.align_x=align; cu.align_y='CENTER'
    # try bold-ish: space character
    cu.space_character=1.0
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob)
    ob.location=loc; ob.rotation_euler=rot
    assign(ob,material)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    return bpy.context.active_object

# ========== BODY ==========
# Front is -Y
body_profile=[
 (0.0,0.10),(0.55,0.10),(0.85,0.11),(0.96,0.16),(1.01,0.26),(1.02,0.45),
 (1.00,0.70),(0.97,0.95),(0.93,1.12),(0.89,1.22),(0.84,1.27),(0.70,1.30),(0.0,1.30)
]
body=lathe("Body", body_profile, YELLOW)

# black base ring
cylinder("BaseBlack",(0,0,0.09),0.93,0.14,BLACK,verts=64)
# thin black bottom disc slightly wider under body curve
torus("BaseTrim",(0,0,0.12),0.92,0.045,BLACK,scale=(1,1,0.7))

# ========== HEAD ==========
head_profile=[
 (0.0,1.32),(0.55,1.32),(0.70,1.34),(0.75,1.40),(0.76,1.55),(0.76,1.85),
 (0.75,2.00),(0.72,2.08),(0.67,2.12),(0.55,2.14),(0.0,2.14)
]
head=lathe("Head", head_profile, YELLOW)

# neck gap black
cylinder("NeckGap",(0,0,1.31),0.68,0.06,BLACK)

# top black disc
topdisc=cylinder("TopDisc",(0,0,2.145),0.64,0.045,BLACKSOFT,verts=64)
bevel(topdisc,0.015,2)
# grooves on top: 6 thin lines near back half (+Y side ?) In back view grooves at upper part (which is front? ) put near -Y strip
for i in range(6):
    y=-0.48+ i*0.04
    L=2*math.sqrt(max(0.05,0.62**2-y**2))*0.92
    b=box(f"TopGroove{i}",(0,y,2.17),(L,0.012,0.004),BLACKSOFT)
text_obj("TopText","Radio Shack",( -0.08,0.10,2.172),(0,0,0),0.15,WHITE,0.002)
text_obj("TopText2","ROBOTIC BANKER",(-0.08,-0.05,2.172),(0,0,0),0.065,WHITE,0.002)
torus("TopLogoRing",(0.38,0.10,2.17),0.075,0.008,WHITE,scale=(1,1,0.35))
text_obj("TopLogoDollar","$",(0.38,0.10,2.172),(0,0,0),0.11,WHITE,0.002)

# coin slot on back of head (+Y)
slot=box("CoinSlot",(0,0.755,1.52),(0.20,0.03,0.032),BLACK)
bevel(slot,0.008,2)

# ========== EYES ==========
for side, sx in (("L",-0.285),("R",0.285)):
    cylinder(f"EyeSocket{side}",(sx,-0.68,1.84),0.19,0.06,BLACK,rot=(math.radians(90),0,0))
    eye=sphere(f"Eye{side}",(sx,-0.71,1.84),0.175,EYEWHITE,scale=(1,0.32,1))
    torus(f"EyeRim{side}",(sx,-0.75,1.84),0.18,0.024,DARKBROWN,rot=(math.radians(90),0,0))
    sphere(f"Pupil{side}",(sx,-0.755,1.72),0.09,BLACK,scale=(1.1,0.30,0.65))

# two tiny white pegs under head front (seen in front view in neck gap)
for i,x in enumerate((-0.07,0.07)):
    cylinder(f"NeckPeg{i}",(x,-0.62,1.30),0.028,0.09,WHITE)

# ========== SEAMS ==========
# vertical seam front (-Y) and back (+Y) following body profile: thin tube curves
prof_seam=[(0.97,0.18),(1.015,0.30),(1.025,0.50),(1.005,0.75),(0.97,1.00),(0.92,1.18),(0.88,1.24)]
for sgn, nm in ((-1,"FrontSeam"),(1,"BackSeam")):
    pts=[(0, sgn*r, z) for r,z in prof_seam]
    curve_tube(nm, pts, 0.006, GROOVE)

# ========== SHOULDERS & ARMS ==========
for side, sx in (("L",-1),("R",1)):  # sx sign X ; +X is robot left (tray)
    # shoulder disc axis X
    sh=cylinder(f"Shoulder{side}",(sx*0.97,0,1.02),0.285,0.26,YELLOW,rot=(0,math.radians(90),0))
    bevel(sh,0.02,2)
    # inner ring groove
    torus(f"ShoulderGroove{side}",(sx*1.02,0,1.02),0.285,0.012,GROOVE,rot=(0,math.radians(90),0))

# Hook arm on -X side: hangs down then C-curl
# Path in roughly Y=-0.15 plane offset front a bit
hook_pts=[
 (-1.02,-0.08,0.92),
 (-1.20,-0.35,0.80),
 (-1.28,-0.55,0.65),
 (-1.24,-0.65,0.54),
 (-1.10,-0.68,0.50),
 (-0.96,-0.68,0.55),
 (-0.93,-0.66,0.66),
 (-1.02,-0.64,0.72),
]
curve_tube("HookArm", hook_pts, 0.072, BLACK, taper_tip=True)
sphere("HookTip",(-1.02,-0.64,0.72),0.055,BLACK)

# Tray arm on +X side: curves forward then up to tray underside
tray_pts=[
 (1.02,-0.02,0.92),
 (1.14,-0.25,0.70),
 (1.10,-0.60,0.58),
 (0.92,-0.88,0.60),
 (0.72,-0.98,0.72),
 (0.64,-1.00,0.82),
]
curve_tube("TrayArm", tray_pts, 0.070, BLACK)

# Tray disc: flat oval at front, deform one edge to a point
tray=cylinder("Tray",(0.42,-1.02,0.88),0.35,0.055,BLACK,scale=(1.12,0.82,1))
bpy.ops.object.select_all(action='DESELECT'); tray.select_set(True); bpy.context.view_layer.objects.active=tray
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for v in tray.data.vertices:
    d=(v.co.x*0.65 - v.co.y*0.75)
    if d>0.26:
        s=(d-0.26)*0.45
        v.co.x+=s*0.65; v.co.y-=s*0.75
tray.data.update()
bevel(tray,0.015,2)

torus("TrayRing",(0.42,-1.02,0.915),0.21,0.013,WHITE,scale=(1.12,0.82,0.30))
text_obj("TrayDollar","$",(0.42,-1.02,0.918),(0,0,0),0.34,WHITE,0.003)

# ========== FEET ==========
def make_foot(side, sx):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=1.0, location=(sx*0.88,-0.50,0.23))
    ob=bpy.context.active_object; ob.name=f"Foot{side}"
    ob.scale=(0.39,0.92,0.27)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    me=ob.data
    for v in me.vertices:
        t=(-v.co.y/0.92)
        if t>0:
            v.co.x*=(1.0-0.38*t*t)
            if v.co.z>0: v.co.z*=(1.0-0.35*t)
        elif v.co.y>0 and v.co.z>0:
            v.co.z*=(1.0+0.28*(v.co.y/0.92))
        if v.co.z < -0.16:
            v.co.z = -0.16 - (v.co.z+0.16)*0.25
    me.update()
    assign(ob,YELLOW); smooth(ob)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0, location=(sx*0.88,-0.50,0.055))
    sole=bpy.context.active_object; sole.name=f"Sole{side}"; sole.scale=(0.38,0.90,0.06)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in sole.data.vertices:
        t=(-v.co.y/0.90)
        if t>0: v.co.x*=(1.0-0.38*t*t)
    sole.data.update()
    assign(sole,BLACK); smooth(sole)
    for i, hy in enumerate((-0.02,0.08)):
        g=torus(f"FootGroove{side}{i}",(sx*0.88,hy,0.26),0.30,0.006,GROOVE, rot=(math.radians(90),0,0), scale=(1.10,0.63,1))

make_foot("L",-1)
make_foot("R",1)

# black under-body plate between feet (visible back view)
plate=box("UnderPlate",(0,0.25,0.09),(1.45,0.7,0.10),BLACK)
bevel(plate,0.03,2)

# ========== CHEST TEXT ROBIE ==========
# on front surface, left-of-centre (viewer left = -X). Slightly follow curvature: place flat tangent, embossed
rob=text_obj("RobieText","ROBIE",(-0.34,-0.985,1.02),(math.radians(90),0,0),0.26,BLACK,0.008,fat=0.035)
# bend text to follow cylindrical body front
_prof=[(0.10,0.96),(0.26,1.01),(0.45,1.02),(0.70,1.00),(0.95,0.97),(1.12,0.93),(1.22,0.89)]
def _body_r(z):
    for i in range(len(_prof)-1):
        z0,r0=_prof[i]; z1,r1=_prof[i+1]
        if z0<=z<=z1: return r0+(r1-r0)*(z-z0)/max(1e-6,(z1-z0))
    return _prof[-1][1]
_zs=[v.co.z for v in rob.data.vertices]; _zmin=min(_zs)
for v in rob.data.vertices:
    wx=rob.location.x+v.co.x; wz=rob.location.z+v.co.y
    r=_body_r(wz)
    if abs(wx)<r:
        surf=math.sqrt(r*r-wx*wx)
        d=v.co.z-_zmin
        v.co.z=rob.location.y+surf-0.012+d
rob.data.update()
# text orientation check later via render

# ========== GROUND / LIGHTS / CAMERA ==========
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,0))
gnd=bpy.context.active_object; gnd.name="Ground"
gm=mat("GroundMat",(0.92,0.92,0.92),0.85); assign(gnd,gm)

def area_light(name, loc, energy, size, rot):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new(name,ld); scene.collection.objects.link(lo); lo.location=loc; lo.rotation_euler=rot
    return lo

area_light("Key",(-3.5,-4,5),550,4,(math.radians(55),0,math.radians(-30)))
area_light("Fill",(4,-3,3),250,4,(math.radians(60),0,math.radians(35)))
area_light("Rim",(0,4.5,4.5),350,3,(math.radians(120),0,math.radians(180)))

world=bpy.data.worlds.new("World"); scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.95,0.95,0.95,1)
world.node_tree.nodes["Background"].inputs[1].default_value=0.35
try:
    scene.view_settings.exposure=-0.25
except: pass

cam_data=bpy.data.cameras.new("Cam"); cam_data.lens=42
cam=bpy.data.objects.new("Camera",cam_data); scene.collection.objects.link(cam)
scene.camera=cam
def set_cam(loc, look=(0,0,1.05)):
    cam.location=loc
    d=Vector(look)-Vector(loc)
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
set_cam((-3.2,-4.6,2.4))

scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=900; scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=64
# shadows
try: scene.eevee.use_shadows=True
except: pass

# apply bevel modifiers? keep for now, apply before export later
print("BUILD DONE", len(bpy.data.objects))
result={"objects":[o.name for o in bpy.data.objects]}
