import bpy, math, os
from mathutils import Vector

# clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes):
    if m.users==0: bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    if m.users==0: bpy.data.materials.remove(m)

def mat(name, color, rough=0.55, metal=0.0, emit=None, emit_str=0.0, alpha=1.0):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Alpha"].default_value=alpha
    if emit:
        try:
            bs.inputs["Emission Color"].default_value=(*emit,1)
            bs.inputs["Emission Strength"].default_value=emit_str
        except Exception: pass
    if alpha<1:
        try: m.surface_render_method='DITHERED'
        except Exception: pass
    return m

WOOD=mat("Wood",(0.45,0.22,0.09),0.7); WOOD_D=mat("WoodDark",(0.25,0.11,0.045),0.75)
WOOD_L=mat("WoodLight",(0.72,0.45,0.22),0.65)
RED=mat("Red",(0.72,0.08,0.06),0.5); RED_D=mat("RedDark",(0.45,0.04,0.035),0.55)
CREAM=mat("Cream",(0.98,0.88,0.65),0.6); WHITE=mat("White",(0.98,0.97,0.94),0.5)
TEAL=mat("Teal",(0.05,0.42,0.45),0.55); NAVY=mat("Navy",(0.06,0.12,0.32),0.6)
OCTO=mat("Octopus",(0.78,0.14,0.06),0.5); OCTO_L=mat("OctoLight",(1.0,0.42,0.22),0.4)
OCTO_D=mat("OctoDark",(0.45,0.06,0.04),0.4); SUCKER=mat("Sucker",(1.0,0.62,0.42),0.45)
BLACK=mat("Black",(0.02,0.02,0.03),0.35); METAL=mat("Metal",(0.42,0.46,0.52),0.35,0.35)
BROTH=mat("Broth",(0.9,0.42,0.06),0.2); NOODLE=mat("Noodle",(1.0,0.52,0.08),0.45)
GREEN=mat("GreenOnion",(0.15,0.7,0.2),0.5); PINK=mat("Pink",(1.0,0.45,0.6),0.5)
YOLK=mat("Yolk",(1.0,0.55,0.05),0.35); NORI=mat("Nori",(0.03,0.12,0.06),0.7)
LANTERN=mat("Lantern",(1.0,0.62,0.18),0.4,emit=(1.0,0.45,0.08),emit_str=2.2)
STEAM=mat("Steam",(0.95,0.97,1.0),0.9,alpha=0.35)
GROUND_M=mat("Ground",(0.08,0.16,0.18),0.9); CERAMIC=mat("CeramicBlue",(0.12,0.25,0.65),0.3)
CERAMIC2=mat("CeramicRed",(0.8,0.15,0.12),0.3)

def link(obj, material=None):
    if material: obj.data.materials.append(material)
    return obj

def box(name, loc, scale, material, rot=(0,0,0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel>0:
        mod=o.modifiers.new("bev","BEVEL"); mod.width=bevel; mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return link(o,material)

def cyl(name, loc, r1, r2, depth, material, rot=(0,0,0), verts=28):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name
    for p in o.data.polygons: p.use_smooth=True
    return link(o,material)

def sph(name, loc, scale, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in o.data.polygons: p.use_smooth=True
    return link(o,material)

def torus(name, loc, major, minor, material, rot=(0,0,0), scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=12, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in o.data.polygons: p.use_smooth=True
    return link(o,material)

def catmull(points, samples):
    pts=[Vector(p) for p in points]
    pts=[pts[0]*2-pts[1]]+pts+[pts[-1]*2-pts[-2]]
    out=[]
    n=len(pts)-3
    for i in range(samples+1):
        t=i/samples*n; seg=min(int(t),n-1); u=t-seg
        p0,p1,p2,p3=pts[seg],pts[seg+1],pts[seg+2],pts[seg+3]
        out.append(0.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u))
    return out

def tube(name, points, r0, r1, material, radial=12, samples=30, suckers=False, sucker_dir=(0,-1,-0.3)):
    path=catmull(points, samples)
    verts=[]; faces=[]
    up=Vector((0,0,1))
    for i,p in enumerate(path):
        if i==0: tan=(path[1]-path[0]).normalized()
        elif i==len(path)-1: tan=(path[-1]-path[-2]).normalized()
        else: tan=(path[i+1]-path[i-1]).normalized()
        side=tan.cross(up)
        if side.length<0.1: side=tan.cross(Vector((0,1,0)))
        side.normalize(); norm=side.cross(tan).normalized()
        r=r0+(r1-r0)*(i/(len(path)-1))
        # slight bulge
        r*=1+0.08*math.sin(i/(len(path)-1)*math.pi)
        for j in range(radial):
            a=j/radial*math.tau
            v=p+(side*math.cos(a)+norm*math.sin(a))*r
            verts.append(tuple(v))
    for i in range(len(path)-1):
        for j in range(radial):
            a=i*radial+j; b=i*radial+(j+1)%radial; c=(i+1)*radial+(j+1)%radial; d=(i+1)*radial+j
            faces.append((a,b,c,d))
    # end caps as fans
    verts.append(tuple(path[0])); ci=len(verts)-1
    for j in range(radial): faces.append((ci,(j+1)%radial,j))
    verts.append(tuple(path[-1])); cj=len(verts)-1; base=(len(path)-1)*radial
    for j in range(radial): faces.append((cj,base+j,base+(j+1)%radial))
    me=bpy.data.meshes.new(name+"Mesh"); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o)
    for p in me.polygons: p.use_smooth=True
    link(o,material)
    if suckers:
        sd=Vector(sucker_dir).normalized()
        for k in range(3,samples-2,3):
            p=path[k]; r=r0+(r1-r0)*(k/samples)
            s=sph(name+f"_sucker{k}", tuple(p+sd*(r*0.92)), (r*0.42,r*0.42,r*0.42), SUCKER)
    return o

def text_obj(name, txt, loc, size, material, rot=(math.pi/2,0,0), extrude=0.04):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; o.data.body=txt; o.data.size=size
    o.data.align_x='CENTER'; o.data.align_y='CENTER'; o.data.extrude=extrude
    bpy.ops.object.convert(target='MESH')
    o=bpy.context.active_object; link(o,material); return o

# ---------- ground / platform ----------
box("Ground",(0,0,-0.08),(12,10,0.16),GROUND_M)
cyl("PlazaDisc",(0,-0.6,0.02),4.6,4.6,0.08,mat("Stone",(0.055,0.08,0.09),0.9),verts=48)
# scattered cobbles front
import random; random.seed(7)
for i in range(26):
    x=random.uniform(-4.2,4.2); y=random.uniform(-3.6,-1.2); s=random.uniform(0.12,0.28)
    sph(f"Cobble{i}",(x,y,0.07),(s,s*0.8,0.04),mat("Cobble",(0.045,0.06,0.065),0.9))
box("Platform",(0,0.9,0.12),(6.4,3.6,0.24),WOOD_D,bevel=0.04)
for i in range(7):
    box(f"Plank{i}",(-2.7+i*0.9,0.9,0.26),(0.82,3.5,0.05),WOOD if i%2 else WOOD_L)

# ---------- booth structure ----------
# back wall & sides
box("BackWall",(0,2.55,2.1),(6.0,0.18,3.6),mat("Wall",(0.85,0.72,0.52),0.8))
for i in range(6):
    box(f"BackSlat{i}",(-2.5+i*1.0,2.44,2.1),(0.12,0.06,3.6),WOOD_D)
box("SideL",(-2.95,1.4,1.55),(0.16,2.4,2.5),WOOD)
box("SideR",(2.95,1.4,1.55),(0.16,2.4,2.5),WOOD)
# back shelf with jars / bottles
box("BackShelf",(0,2.32,2.9),(5.4,0.35,0.1),WOOD_D)
for i,x in enumerate([-2.3,-1.7,-1.1,1.2,1.8,2.4]):
    cyl(f"Jar{i}",(x,2.32,3.15),0.18,0.14,0.4,[CERAMIC,CERAMIC2,TEAL][i%3])
    cyl(f"JarLid{i}",(x,2.32,3.38),0.15,0.15,0.06,WOOD_D)
for i,x in enumerate([-0.4,0.1,0.55]):
    cyl(f"Bottle{i}",(x,2.32,3.2),0.09,0.06,0.5,mat("GlassG",(0.1,0.45,0.25),0.2))
# menu boards on back wall
for i,x in enumerate([-1.9,1.9]):
    box(f"MenuBoard{i}",(x,2.42,2.15),(1.1,0.06,1.3),WOOD_D)
    for r in range(4):
        box(f"MenuLine{i}_{r}",(x,2.38,2.55-r*0.27),(0.75,0.03,0.09),CREAM)
        sph(f"MenuDot{i}_{r}",(x-0.42,2.38,2.55-r*0.27),(0.05,0.03,0.05),RED)

# posts
for sx in (-2.95,2.95):
    for sy in (-0.6,):
        box("Post",(sx,sy,2.25),(0.28,0.28,4.2),WOOD_D,bevel=0.03)
box("HeaderBeam",(0,-0.6,4.25),(6.3,0.32,0.32),WOOD_D,bevel=0.03)
box("BackBeam",(0,2.55,4.0),(6.2,0.25,0.25),WOOD_D)

# roof: two sloped slabs + ridge + tiles suggestion
box("RoofFront",(0,0.15,4.85),(6.9,2.6,0.16),RED_D,rot=(math.radians(28),0,0),bevel=0.03)
box("RoofBack",(0,1.95,4.85),(6.9,2.2,0.16),RED_D,rot=(math.radians(-28),0,0),bevel=0.03)
cyl("Ridge",(0,1.05,5.45),0.18,0.18,6.9,TEAL,rot=(0,math.pi/2,0))
for i in range(9):
    x=-3.0+i*0.75
    box(f"RoofTileF{i}",(x,0.15,4.97),(0.55,2.45,0.06),RED if i%2 else RED_D,rot=(math.radians(28),0,0))
# roof ornament octopus ball
sph("RoofOrnament",(0,1.05,5.78),(0.32,0.32,0.32),OCTO)
for i in range(6):
    a=i/6*math.tau
    sph(f"OrnTent{i}",(math.cos(a)*0.35,1.05+math.sin(a)*0.2,5.6),(0.09,0.09,0.16),OCTO)

# striped awning under roof front
for i in range(8):
    x=-2.8+i*0.8
    box(f"Awning{i}",(x,-1.0,4.38),(0.78,0.62,0.07),RED if i%2 else CREAM,rot=(math.radians(32),0,0))

# noren curtains
for i,x in enumerate([-2.05,2.05]):
    box(f"Noren{i}",(x,-0.58,3.98),(1.55,0.06,0.62),NAVY)
    cyl(f"NorenCircle{i}",(x,-0.63,3.98),0.22,0.22,0.05,WHITE,rot=(math.pi/2,0,0))
    cyl(f"NorenInner{i}",(x,-0.64,3.98),0.12,0.12,0.06,RED,rot=(math.pi/2,0,0))

# sign
box("SignBoard",(0,-0.78,4.62),(4.4,0.14,0.85),WOOD_D,bevel=0.05)
box("SignFace",(0,-0.86,4.62),(4.2,0.05,0.65),CREAM)
text_obj("SignText","OCTO RAMEN",(0,-0.92,4.62),0.42,RED_D)
# small vertical signs on posts
for sx,word in [(-3.12,"HOT"),(3.12,"SOUP")]:
    box("VSign",(sx,-0.6,3.1),(0.08,0.5,1.5),CREAM)
    text_obj("VSignText",word,(sx-0.06 if sx<0 else sx+0.06,-0.6,3.1),0.22,RED_D,rot=(math.pi/2,0,math.pi/2 if sx<0 else -math.pi/2))

# ---------- counter ----------
box("CounterBody",(0,0.05,1.08),(5.8,1.15,1.7),WOOD,bevel=0.04)
box("CounterTop",(0,-0.02,2.0),(6.15,1.45,0.16),WOOD_L,bevel=0.05)
for i in range(9):
    box(f"CounterSlat{i}",(-2.55+i*0.64,-0.55,1.05),(0.42,0.05,1.45),WOOD_D if i%2 else WOOD)
box("CounterTrim",(0,-0.58,1.82),(5.9,0.07,0.14),RED)
# foot rail
cyl("FootRail",(0,-0.75,0.45),0.05,0.05,5.4,METAL,rot=(0,math.pi/2,0))

# stools
for i,x in enumerate([-1.9,0,1.9]):
    cyl(f"StoolSeat{i}",(x,-1.35,1.05),0.42,0.36,0.12,RED if i!=1 else TEAL)
    cyl(f"StoolPost{i}",(x,-1.35,0.55),0.09,0.09,0.9,WOOD_D)
    cyl(f"StoolBase{i}",(x,-1.35,0.08),0.32,0.36,0.08,WOOD_D)
    torus(f"StoolRing{i}",(x,-1.35,0.35),0.28,0.03,METAL)

# ---------- ramen bowl factory ----------
def make_bowl(prefix, cx, cy, cz, s=1.0, ceramic=CERAMIC, noodles_up=False):
    # cz = counter top surface
    cyl(prefix+"_foot",(cx,cy,cz+0.05*s),0.20*s,0.24*s,0.1*s,ceramic)
    cyl(prefix+"_bowl",(cx,cy,cz+0.28*s),0.22*s,0.52*s,0.42*s,ceramic)  # cone radius1 bottom, radius2 top
    torus(prefix+"_rim",(cx,cy,cz+0.49*s),0.5*s,0.055*s,WHITE)
    cyl(prefix+"_stripe",(cx,cy,cz+0.30*s),0.40*s,0.46*s,0.08*s,WHITE)
    cyl(prefix+"_broth",(cx,cy,cz+0.48*s),0.47*s,0.47*s,0.04*s,BROTH)
    # noodle pile: flattened tori
    for i in range(5):
        a=i*1.25
        torus(prefix+f"_noodle{i}",(cx+math.cos(a)*0.13*s,cy+math.sin(a)*0.13*s,cz+0.53*s),0.16*s,0.045*s,NOODLE,rot=(0.2,0.1,a))
    # egg half
    sph(prefix+"_eggW",(cx+0.24*s,cy-0.12*s,cz+0.55*s),(0.16*s,0.13*s,0.07*s),WHITE)
    sph(prefix+"_eggY",(cx+0.24*s,cy-0.12*s,cz+0.59*s),(0.085*s,0.07*s,0.045*s),YOLK)
    # narutomaki
    cyl(prefix+"_naru",(cx-0.24*s,cy+0.12*s,cz+0.54*s),0.11*s,0.11*s,0.05*s,WHITE)
    torus(prefix+"_naruP",(cx-0.24*s,cy+0.12*s,cz+0.57*s),0.055*s,0.02*s,PINK)
    # nori sheets
    box(prefix+"_nori1",(cx-0.28*s,cy+0.28*s,cz+0.68*s),(0.28*s,0.03*s,0.38*s),NORI,rot=(0.2,0,0.25))
    box(prefix+"_nori2",(cx-0.05*s,cy+0.34*s,cz+0.68*s),(0.28*s,0.03*s,0.38*s),NORI,rot=(0.2,0,-0.15))
    # green onion rings
    for i,(dx,dy) in enumerate([(0.05,0.18),(-0.12,-0.18),(0.18,0.05),(-0.02,0.0)]):
        torus(prefix+f"_go{i}",(cx+dx*s,cy+dy*s,cz+0.58*s),0.045*s,0.018*s,GREEN)
    # chashu slices
    cyl(prefix+"_pork",(cx+0.05*s,cy-0.28*s,cz+0.53*s),0.16*s,0.16*s,0.045*s,mat("Chashu",(0.75,0.4,0.22),0.5),rot=(0.3,0,0))
    if noodles_up:
        for i,dx in enumerate([-0.12,-0.04,0.04,0.12]):
            tube(prefix+f"_lift{i}",[(cx+dx*s,cy,cz+0.55*s),(cx+dx*1.4*s,cy-0.05,cz+1.0*s),(cx+dx*s,cy,cz+1.45*s)],0.028*s,0.028*s,NOODLE,radial=7,samples=14)
    return cz+0.5*s

# pot on counter left-back
cyl("Pot",( -2.05,0.35,2.45),0.62,0.58,0.75,METAL)
torus("PotRim",(-2.05,0.35,2.82),0.58,0.05,METAL)
cyl("PotBroth",(-2.05,0.35,2.80),0.54,0.54,0.04,BROTH)
torus("PotHandleL",(-2.68,0.35,2.6),0.16,0.035,METAL,rot=(0,math.pi/2,0))
torus("PotHandleR",(-1.42,0.35,2.6),0.16,0.035,METAL,rot=(0,math.pi/2,0))
box("Burner",(-2.05,0.35,2.12),(1.0,0.9,0.12),BLACK)
# bubbles in pot
for i,(dx,dy) in enumerate([(0.2,0.1),(-0.25,-0.05),(0.0,0.25),(-0.1,-0.25)]):
    sph(f"Bubble{i}",(-2.05+dx,0.35+dy,2.85),(0.09,0.09,0.05),CREAM)
# steam puffs over pot
for i,(dx,dy,dz,sc) in enumerate([(-0.15,0,0.25,0.13),(0.12,0.05,0.55,0.17),(-0.08,-0.05,0.9,0.21),(0.15,0,1.25,0.25)]):
    sph(f"SteamPot{i}",(-2.05+dx,0.35+dy,2.85+dz),(sc,sc*0.8,sc*0.7),STEAM)

make_bowl("BowlL",-1.9,-0.25,2.08,1.0,CERAMIC)
make_bowl("BowlC",0.95,-0.35,2.08,1.15,CERAMIC2,noodles_up=True)
make_bowl("BowlR",2.05,-0.2,2.08,1.0,CERAMIC)
# steam over center bowl
for i,(dx,dz,sc) in enumerate([(0,0.3,0.11),(0.1,0.6,0.15),(-0.05,0.95,0.19)]):
    sph(f"SteamBowl{i}",(0.95+dx,-0.35,2.7+dz),(sc,sc*0.7,sc*0.6),STEAM)

# extras on counter: chopstick holder, spice jars, stacked bowls, spoon rest
cyl("StickHolder",(1.45,0.35,2.3),0.16,0.13,0.45,CERAMIC)
for i in range(5):
    a=-0.28+i*0.14
    cyl(f"Stick{i}",(1.45+math.sin(a)*0.18,0.35,2.62),0.016,0.012,0.65,WOOD_L,rot=(a,0,a*0.5))
for i,x in enumerate([2.45,2.7]):
    cyl(f"Spice{i}",(x,0.32,2.28),0.09,0.08,0.36,[RED,WHITE][i])
    cyl(f"SpiceTop{i}",(x,0.32,2.49),0.07,0.07,0.06,BLACK)
for i in range(3):
    cyl(f"StackBowl{i}",(-1.05,0.42,2.2+i*0.14),0.2,0.36,0.16,[CERAMIC,CERAMIC2,WHITE][i])
# cutting board with green onions right side
box("Board",(1.7,0.3,2.13),(0.9,0.7,0.06),WOOD_L)
for i in range(4):
    cyl(f"OnionCut{i}",(1.5+i*0.14,0.25,2.18),0.05,0.05,0.04,GREEN)
box("KnifeBlade",(1.9,0.42,2.2),(0.45,0.1,0.03),METAL,rot=(0,0,0.5))
cyl("KnifeHandle",(2.15,0.52,2.2),0.03,0.03,0.3,WOOD_D,rot=(math.pi/2,0,0.5))

# ---------- lanterns ----------
def lantern(prefix,x,y,z,s=1.0):
    sph(prefix,(x,y,z),(0.30*s,0.30*s,0.36*s),LANTERN)
    for i in range(3):
        torus(prefix+f"_rib{i}",(x,y,z-0.16*s+i*0.16*s),0.29*s,0.015*s,RED_D)
    cyl(prefix+"_capT",(x,y,z+0.38*s),0.12*s,0.12*s,0.07*s,BLACK)
    cyl(prefix+"_capB",(x,y,z-0.38*s),0.12*s,0.12*s,0.07*s,BLACK)
    cyl(prefix+"_string",(x,y,z+0.65*s),0.015,0.015,0.5*s,BLACK)
    box(prefix+"_tassel",(x,y,z-0.52*s),(0.05,0.05,0.22*s),RED)
    # glow core
    sph(prefix+"_glow",(x,y-0.05,z),(0.1*s,0.1*s,0.14*s),mat("Glow",(1,0.85,0.4),0.3,emit=(1,0.7,0.2),emit_str=4))
lantern("LanternL",-2.6,-0.85,3.55,1.0)
lantern("LanternR",2.6,-0.85,3.55,1.0)
lantern("LanternML",-1.85,-0.9,3.95,0.7)
lantern("LanternMR",1.85,-0.9,3.95,0.7)
# festoon string across front
tube("Festoon",[(-2.9,-0.85,4.4),(-1.4,-0.95,4.12),(0,-0.98,4.08),(1.4,-0.95,4.12),(2.9,-0.85,4.4)],0.018,0.018,BLACK,radial=6,samples=24)
for i,x in enumerate([-2.2,-1.1,0,1.1,2.2]):
    z=4.12+ (0.18 if abs(x)>1.5 else 0.0)
    sph(f"Bulb{i}",(x,-0.97,z-0.12),(0.07,0.07,0.09),mat("Bulb",(1,0.8,0.35),0.3,emit=(1,0.65,0.15),emit_str=3))



# ---------- octopus chef ----------
def rod(name,p1,p2,r,material):
    return tube(name,[p1,p2],r,r,material,radial=8,samples=2)

OX,OY=-0.15,0.62
# lower body / mantle
sph("OctoBody",(OX,OY,2.25),(0.82,0.72,0.65),OCTO)
sph("OctoHead",(OX,OY,3.00),(0.88,0.80,0.92),OCTO)
sph("OctoBelly",(OX,OY-0.48,2.42),(0.55,0.30,0.55),OCTO_L)
# head spots
for i,(dx,dy,dz,s) in enumerate([(-0.55,-0.48,3.5,0.12),(0.48,-0.6,3.62,0.09),(-0.25,-0.7,3.72,0.08),(0.68,-0.35,3.22,0.10),(-0.72,-0.2,3.18,0.08)]):
    sph(f"Spot{i}",(OX+dx,OY+dy,dz),(s,s*0.55,s),OCTO_D)
# eyes (front is -Y)
for side in (-1,1):
    sph(f"EyeW{side}",(OX+side*0.33,OY-0.71,3.14),(0.19,0.12,0.23),WHITE)
    sph(f"EyeP{side}",(OX+side*0.33,OY-0.81,3.14),(0.10,0.07,0.13),BLACK)
    sph(f"EyeH{side}",(OX+side*0.29,OY-0.87,3.24),(0.04,0.03,0.05),WHITE)
    # happy brow arc
    tube(f"Brow{side}",[(OX+side*0.15,OY-0.76,3.44),(OX+side*0.34,OY-0.80,3.53),(OX+side*0.52,OY-0.76,3.44)],0.03,0.03,BLACK,radial=6,samples=10)
# cheeks + mouth (open smile tube arc + tongue)
for side in (-1,1):
    sph(f"Cheek{side}",(OX+side*0.55,OY-0.69,2.80),(0.15,0.07,0.10),PINK)
tube("Mouth",[(OX-0.20,OY-0.78,2.84),(OX-0.07,OY-0.84,2.73),(OX+0.11,OY-0.84,2.73),(OX+0.22,OY-0.78,2.86)],0.035,0.035,BLACK,radial=6,samples=14)
sph("Tongue",(OX+0.02,OY-0.80,2.75),(0.09,0.05,0.06),PINK)

# chef hat (tilted)
cyl("HatBand",(OX-0.08,OY,3.84),0.54,0.58,0.30,WHITE,rot=(0.06,0.10,0.06))
for i,(dx,dy,dz,s) in enumerate([(0,0,4.06,0.42),(-0.32,0.05,4.0,0.34),(0.32,0.05,4.0,0.34),(0.02,-0.26,4.0,0.32),(0.0,0.28,4.02,0.32)]):
    sph(f"HatPuff{i}",(OX-0.08+dx,OY+dy,dz),(s,s,s*0.55),WHITE)
# neckerchief
torus("Scarf",(OX,OY-0.12,2.28),0.62,0.13,TEAL,rot=(math.radians(72),0,0))
sph("ScarfKnot",(OX+0.12,OY-0.72,2.22),(0.15,0.12,0.14),TEAL)
box("ScarfTail",(OX+0.22,OY-0.72,1.98),(0.2,0.05,0.38),TEAL,rot=(0,0,0.4))
# apron front (just above counter back edge)
box("Apron",(OX,OY-0.68,2.18),(0.95,0.07,0.55),WHITE,rot=(math.radians(-8),0,0),bevel=0.03)
box("ApronPocket",(OX,OY-0.73,2.12),(0.4,0.04,0.22),CREAM)

# ----- 8 tentacles -----
# 1 front-left resting curl on counter
tube("Tent1_restL",[(-0.55,0.85,2.15),(-1.05,0.25,2.2),(-1.45,-0.25,2.22),(-1.25,-0.55,2.30),(-0.95,-0.45,2.38)],0.20,0.07,OCTO,suckers=True,sucker_dir=(0,-0.4,-1))
# 2 front-right holding chopsticks over center bowl
tube("Tent2_chopsticks",[(0.45,0.7,2.2),(1.05,0.15,2.7),(1.15,-0.2,3.4),(0.98,-0.34,3.88),(0.8,-0.36,3.76)],0.20,0.06,OCTO,suckers=True,sucker_dir=(0,-1,-0.2))
# 3 left holding ladle into pot
tube("Tent3_ladle",[(-0.8,1.0,2.5),(-1.45,0.55,2.9),(-1.7,0.25,3.35),(-1.55,0.1,3.5)],0.20,0.06,OCTO,suckers=True,sucker_dir=(0,-1,0))
# 4 right waving high
tube("Tent4_wave",[(0.55,0.85,2.55),(1.35,0.75,3.1),(1.8,0.6,3.7),(1.55,0.45,4.05),(1.3,0.42,3.85)],0.19,0.06,OCTO,suckers=True,sucker_dir=(0,-1,0))
# 5 left-mid holding egg up
tube("Tent5_egg",[(-0.85,1.2,2.7),(-1.6,1.0,3.15),(-1.95,0.85,3.55),(-1.8,0.75,3.78)],0.18,0.06,OCTO)
# 6 right presenting / curling by right bowl
tube("Tent6_present",[(0.7,0.8,2.1),(1.35,0.1,2.18),(1.85,-0.45,2.25),(2.15,-0.6,2.42),(2.0,-0.75,2.5)],0.20,0.07,OCTO,suckers=True,sucker_dir=(0,-0.4,-1))
# 7 back-left holding nori sheet
tube("Tent7_nori",[(-0.6,1.45,2.6),(-1.25,1.35,3.1),(-1.5,1.2,3.7),(-1.35,1.05,3.95)],0.17,0.05,OCTO)
# 8 back-right sprinkling shaker over right bowl
tube("Tent8_shaker",[(0.6,1.45,2.6),(1.4,1.2,3.0),(2.0,0.55,3.3),(2.15,0.1,3.35)],0.17,0.05,OCTO)

# props in tentacle tips
# chopsticks from tip down to lifted noodles (center bowl top ~3.7 noodle ends, sticks cross there)
rod("Chopstick1",(0.86,-0.4,4.28),(0.94,-0.34,3.66),0.025,WOOD_D)
rod("Chopstick2",(1.05,-0.31,4.24),(0.97,-0.34,3.66),0.025,WOOD_D)
# ladle: handle from tip down to pot + cup
rod("LadleHandle",(-1.55,0.12,3.5),(-1.95,0.30,2.95),0.035,WOOD_D)
sph("LadleCup",(-2.0,0.32,2.88),(0.20,0.20,0.10),METAL)
sph("LadleBroth",(-2.0,0.32,2.94),(0.15,0.15,0.05),BROTH)
# egg in tent5
sph("HeldEggW",(-1.78,0.72,3.88),(0.20,0.17,0.13),WHITE)
sph("HeldEggY",(-1.78,0.62,3.92),(0.10,0.08,0.07),YOLK)
# nori sheet in tent7
box("HeldNori",(-1.32,1.02,3.98),(0.5,0.04,0.5),NORI,rot=(0.15,0,0.3))
# shaker in tent8, tilted, with sprinkle dots falling to right bowl
cyl("HeldShaker",(2.18,0.02,3.28),0.09,0.09,0.28,RED,rot=(math.radians(45),0,0.4))
cyl("HeldShakerTop",(2.26,-0.10,3.18),0.07,0.07,0.07,BLACK,rot=(math.radians(45),0,0.4))
for i in range(8):
    import random as _r; _r.seed(i+3)
    sph(f"Sprinkle{i}",(2.05+_r.uniform(-0.18,0.18),-0.2+_r.uniform(-0.12,0.12),2.75+ i*0.05),(0.025,0.025,0.025),GREEN)

# extra steam wisps as tubes over pot
tube("SteamWisp1",[(-2.1,0.3,2.9),(-1.95,0.25,3.3),(-2.15,0.3,3.7),(-2.0,0.25,4.05)],0.05,0.09,STEAM,radial=8,samples=18)
tube("SteamWisp2",[(0.9,-0.35,2.75),(1.05,-0.35,3.1),(0.92,-0.35,3.45)],0.035,0.06,STEAM,radial=8,samples=14)

# ---------- ground props ----------
# crate with veg left front, barrel right
box("Crate",(-3.6,-0.9,0.35),(0.9,0.9,0.55),WOOD,bevel=0.03)
for i in range(4):
    sph(f"CrateVeg{i}",(-3.85+(i%2)*0.45,-1.1+(i//2)*0.4,0.68),(0.2,0.2,0.18),GREEN if i%2 else mat("OnionW",(0.95,0.9,0.75),0.5))
cyl("Barrel",(3.65,-0.8,0.55),0.42,0.48,1.05,WOOD)
torus("BarrelRing1",(3.65,-0.8,0.85),0.47,0.03,METAL)
torus("BarrelRing2",(3.65,-0.8,0.3),0.44,0.03,METAL)
sph("BarrelBowl",(3.65,-0.8,1.12),(0.3,0.3,0.12),CERAMIC)
# small sign easel front right
box("EaselBoard",(2.9,-2.1,0.75),(0.95,0.07,1.1),WOOD_D,rot=(math.radians(-10),0,math.radians(-12)))
text_obj("EaselText","RAMEN",(2.9,-2.16,0.95),0.24,CREAM)
text_obj("EaselText2","500",(2.9,-2.17,0.58),0.22,LANTERN)
for dx in (-0.35,0.35):
    rod("EaselLeg",(2.9+dx,-2.05,0.85),(2.9+dx*1.4,-1.95,0.02),0.035,WOOD_D)

# ---------- lights / world / camera ----------
scene=bpy.context.scene
world=bpy.data.worlds["World"]; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.03,0.06,0.13,1)
world.node_tree.nodes["Background"].inputs[1].default_value=0.55

def light_obj(name,typ,loc,energy,color,rot=(0,0,0),angle=None):
    ld=bpy.data.lights.new(name,typ); ld.energy=energy; ld.color=color
    if angle and typ=='SPOT': ld.spot_size=angle
    o=bpy.data.objects.new(name,ld); o.location=loc; o.rotation_euler=rot
    scene.collection.objects.link(o); return o
light_obj("Sun","SUN",(4,-4,8),2.2,(1,0.85,0.65),rot=(math.radians(50),math.radians(10),math.radians(30)))
light_obj("WarmFront","POINT",(-1.5,-3.2,3.8),700,(1,0.62,0.25))
light_obj("Fill","POINT",(1.5,-6,4.5),500,(0.65,0.78,1.0))
light_obj("BoothGlow","POINT",(0,-1.7,3.7),450,(1,0.7,0.35))

cam_data=bpy.data.cameras.new("Camera"); cam=bpy.data.objects.new("Camera",cam_data)
scene.collection.objects.link(cam); scene.camera=cam
cam_data.lens=38
def set_cam(loc, look=(0,0.4,2.4)):
    cam.location=loc
    d=Vector(look)-Vector(loc)
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
set_cam((4.6,-9.4,2.95))

scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1100; scene.render.resolution_y=850
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
try: scene.eevee.taa_render_samples=32
except Exception: pass
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'

bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("octo_ramen.blend"))
result={"objects":len(bpy.data.objects),"saved":"octo_ramen.blend"}
