import bpy, math, os
from mathutils import Vector

# clear
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for b in list(bpy.data.meshes): bpy.data.meshes.remove(b)
for b in list(bpy.data.curves): bpy.data.curves.remove(b)
for b in list(bpy.data.materials): bpy.data.materials.remove(b)

def mat(name, color, rough=0.7, metal=0.0, alpha=1.0, emit=None, emit_str=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    if alpha<1:
        bs.inputs["Alpha"].default_value=alpha
        m.surface_render_method='BLENDED'
    if emit:
        bs.inputs["Emission Color"].default_value=(*emit,1)
        bs.inputs["Emission Strength"].default_value=emit_str
    return m

M={}
M['octo']=mat("Octo", (0.98,0.22,0.18),0.5)
M['octo_dark']=mat("OctoDark", (0.75,0.18,0.18),0.6)
M['belly']=mat("Belly", (1.0,0.75,0.65),0.6)
M['white']=mat("White", (0.98,0.97,0.94),0.8)
M['wood']=mat("Wood", (0.55,0.32,0.16),0.8)
M['wood_dark']=mat("WoodDark", (0.32,0.18,0.09),0.85)
M['wood_light']=mat("WoodLight", (0.78,0.55,0.32),0.8)
M['red']=mat("Red", (0.85,0.12,0.15),0.6)
M['navy']=mat("Navy", (0.10,0.15,0.35),0.7)
M['cream']=mat("Cream", (0.96,0.88,0.70),0.8)
M['black']=mat("Black", (0.08,0.08,0.10),0.5)
M['ceramic']=mat("Ceramic", (0.15,0.35,0.65),0.3)
M['ceramic2']=mat("Ceramic2", (0.85,0.20,0.18),0.3)
M['broth']=mat("Broth", (0.98,0.65,0.20),0.35)
M['noodle']=mat("Noodle", (0.98,0.85,0.45),0.6)
M['green']=mat("Green", (0.25,0.65,0.25),0.6)
M['pink']=mat("Pink", (1.0,0.60,0.65),0.6)
M['egg']=mat("Egg", (0.99,0.75,0.15),0.5)
M['metal']=mat("Metal", (0.75,0.78,0.82),0.3,0.8)
M['pot']=mat("Pot", (0.35,0.36,0.40),0.35,0.7)
M['floor']=mat("Floor", (0.22,0.20,0.22),0.9)
M['lantern']=mat("Lantern", (1.0,0.55,0.25),0.6, emit=(1.0,0.45,0.15), emit_str=1.2)
M['steam']=mat("Steam", (1,1,1),1.0, alpha=0.28)

def assign(obj, material):
    if material: obj.data.materials.append(material)
    return obj

def box(name, loc, scale, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material); return o

def sphere(name, loc, scale, material, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=20, location=loc)
    o=bpy.context.active_object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material)
    # smooth
    for p in o.data.polygons: p.use_smooth=True
    return o

def cyl(name, loc, radius, depth, material, rot=(0,0,0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; assign(o, material); return o

def cone(name, loc, r1, r2, depth, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; assign(o, material); return o

def torus(name, loc, major, minor, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=28, minor_segments=12, location=loc, rotation=rot)
    o=bpy.context.active_object; o.name=name; assign(o, material); return o

def tube_from_points(name, points, radius, material, taper_end=0.35):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    cu.bevel_depth=radius; cu.bevel_resolution=4; cu.resolution_u=8
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for i,p in enumerate(points):
        bp=sp.bezier_points[i]; bp.co=p; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
        # taper via radius: 1 at start to taper_end
        t=i/(len(points)-1) if len(points)>1 else 0
        bp.radius=1.0*(1-t)+taper_end*t
    cu.materials.append(material)
    o=bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o=bpy.context.active_object; o.name=name
    for p in o.data.polygons: p.use_smooth=True
    o.select_set(False)
    return o

# ---------- FLOOR & BACKDROP ----------
box("Floor", (0,0,-0.06),(9,7,0.12), M['floor'])
box("BackWall", (0,2.8,1.6),(9,0.18,3.4), mat("Wall",(0.18,0.16,0.28),0.9))

# ---------- BOOTH STRUCTURE ----------
# counter
box("CounterTop", (0,0.55,0.55),(4.6,1.1,0.12), M['wood_light'])
box("CounterFront", (0,0.02,0),(4.6,0.08,1.0), M['wood_dark'])
# front slats
for i,x in enumerate([-1.8,-1.2,-0.6,0,0.6,1.2,1.8]):
    box(f"Slat{i}", (x, 0.07, 0),(0.09,0.04,1.0), M['wood_light'])
box("CounterSideL", (-2.26,0.55,0.25),(0.08,1.1,1.1), M['wood'])
box("CounterSideR", (2.26,0.55,0.25),(0.08,1.1,1.1), M['wood'])
# shelf behind
box("BackShelf", (0,1.85,1.15),(4.4,0.5,0.08), M['wood'])
box("BackShelfTop", (0,1.85,1.85),(4.4,0.5,0.08), M['wood_light'])
# posts
for x in [-2.3,2.3]:
    cyl(f"Post{x}", (x,1.2,1.55),0.07,3.1, M['wood_dark'])
    cyl(f"PostF{x}", (x,-0.3,1.55),0.07,3.1, M['wood_dark'])
# roof / awning - slanted
box("Awning", (0,0.45,3.25),(5.2,2.6,0.10), M['red'], rot=(math.radians(18),0,0))
# awning stripes
for i,x in enumerate([-2.0,-1.2,-0.4,0.4,1.2,2.0]):
    box(f"Stripe{i}", (x,0.42,3.27),(0.65,2.62,0.11), M['cream'], rot=(math.radians(18),0,0))
# roof beam
box("Beam", (0,-0.55,2.95),(5.0,0.12,0.18), M['wood_dark'])
box("BeamBack", (0,2.2,2.95),(5.0,0.12,0.18), M['wood_dark'])

# noren curtains (navy panels hanging from front beam)
for i,x in enumerate([-1.6,-0.8,0,0.8,1.6]):
    box(f"Noren{i}", (x,-0.55,2.62),(0.72,0.05,0.62), M['navy'])
    # white circle motif approximated by small flattened sphere
    sphere(f"NorenDot{i}", (x,-0.60,2.62),(0.13,0.03,0.13), M['white'], seg=20)

# sign board
box("Sign", (0,-1.05,3.55),(1.9,0.06,0.42), M['wood_dark'], rot=(__import__("math").radians(18),0,0))
# lanterns
for x in [-2.0,-1.0,0,1.0,2.0]:
    cyl(f"LanternStem{x}", (x,-0.6,2.68),0.015,0.14, M['black'])
    s=sphere(f"Lantern{x}", (x,-0.6,2.42),(0.17,0.17,0.20), M['lantern'], seg=20)
    torus(f"LanternRing{x}", (x,-0.6,2.60),0.09,0.018, M['red'], rot=(math.radians(90),0,0))

# stools in front
for x in [-1.5,-0.5,0.5,1.5]:
    cyl(f"StoolTop{x}", (x,-1.15,0.55),0.32,0.08, M['red'])
    cyl(f"StoolLeg{x}", (x,-1.15,0.27),0.05,0.55, M['wood_dark'])
    torus(f"StoolRing{x}", (x,-1.15,0.15),0.22,0.02, M['metal'], rot=(0,0,0))

# ---------- COOKING GEAR ON COUNTER ----------
# big pot left
cyl("Pot", (-1.55,0.75,0.95),0.42,0.55, M['pot'])
torus("PotRim", (-1.55,0.75,1.24),0.42,0.03, M['metal'])
cyl("PotBroth", (-1.55,0.75,1.20),0.38,0.04, M['broth'])
# pot lid leaning
cyl("Lid", (-1.05,0.95,0.72),0.30,0.04, M['metal'], rot=(math.radians(70),0,0))
# small bowls stack
for j in range(3):
    cyl(f"StackBowl{j}", (1.95,0.75,0.68+j*0.11),0.20-j*0.01,0.10, M['white'])
# jars
for i,(x,c) in enumerate([(-0.9,M['red']),(-0.65,M['green']),(1.35,M['ceramic'])]):
    cyl(f"Jar{i}", (x,0.85,0.78),0.11,0.34, c)
    cyl(f"JarLid{i}", (x,0.85,0.97),0.12,0.04, M['wood_dark'])

def make_bowl(name, loc, bowl_mat):
    # bowl: use cone/cylinder combo + rim + broth + noodles
    x,y,z=loc
    cone(name, (x,y,z+0.08), 0.10, 0.26, 0.18, bowl_mat)
    torus(name+"Rim", (x,y,z+0.17),0.26,0.025, bowl_mat)
    cyl(name+"Broth", (x,y,z+0.15),0.23,0.03, M['broth'])
    # noodle swirls: 3 small tori
    for k in range(3):
        torus(f"{name}Noodle{k}", (x-0.07+k*0.07, y+0.02*((k%2)*2-1), z+0.19),0.07,0.022, M['noodle'], rot=(math.radians(90),0,k))
    # narutomaki
    cyl(name+"Naruto", (x+0.10,y-0.06,z+0.20),0.06,0.03, M['pink'], rot=(math.radians(90),0,0))
    # egg half
    sphere(name+"Egg", (x-0.11,y+0.07,z+0.19),(0.07,0.07,0.04), M['white'], seg=16)
    sphere(name+"Yolk", (x-0.11,y+0.07,z+0.215),(0.035,0.035,0.025), M['egg'], seg=16)
    # green onion bits
    for k in range(4):
        cyl(f"{name}Green{k}", (x-0.12+k*0.07, y-0.10+ (k%2)*0.05, z+0.20),0.018,0.02, M['green'])

make_bowl("BowlFrontL", (-0.95,0.22,0.61), M['ceramic'])
make_bowl("BowlFrontR", (1.05,0.22,0.61), M['ceramic2'])
make_bowl("BowlCounter", (-0.15,0.72,0.61), M['ceramic2'])

# chopsticks on front bowls (thin cylinders)
for bx in [-0.95,1.05]:
    cyl(f"ChopA{bx}", (bx+0.05,0.27,0.95),0.012,0.55, M['wood_dark'], rot=(math.radians(55),0,math.radians(20)))
    cyl(f"ChopB{bx}", (bx+0.12,0.27,0.95),0.012,0.55, M['wood_dark'], rot=(math.radians(55),0,math.radians(28)))

# ---------- OCTOPUS CHEF ----------
# body/head: big rounded head behind counter
head = sphere("OctoHead", (0,1.05,1.32),(0.85,0.80,0.95), M['octo'], seg=40)
sphere("OctoBelly", (0,1.02,0.78),(0.62,0.45,0.55), M['belly'], seg=32)
# head spots
for (sx,sy,sz) in [(-0.45,1.35,2.15),(0.5,1.2,2.2),(0.2,1.55,2.05),(-0.3,0.75,2.25)]:
    sphere("Spot", (sx,sy,sz),(0.09,0.06,0.09), M['octo_dark'], seg=12)

# eyes
for ex in [-0.30,0.30]:
    sphere("EyeW", (ex,0.26,1.50),(0.16,0.07,0.18), M['white'], seg=24)
    sphere("Pupil", (ex,0.18,1.56),(0.085,0.04,0.10), M['black'], seg=20)
    sphere("Glint", (ex+0.03,0.15,1.64),(0.03,0.02,0.03), M['white'], seg=10)
# brows
for ex in [-0.30,0.30]:
    box("Brow", (ex,0.26,1.74),(0.28,0.04,0.06), M['black'], rot=(0,0, math.radians(-8 if ex<0 else 8)))
# mouth - smile torus arc approximated by torus segment (full small torus half hidden)
torus("Mouth", (0,0.26,1.20),0.16,0.028, M['black'], rot=(math.radians(20),0,0))
# cheeks
for ex in [-0.58,0.58]:
    sphere("Cheek", (ex,0.28,1.28),(0.13,0.05,0.10), M['pink'], seg=16)
# chef hat
cyl("HatBand", (0,1.05,2.12),0.62,0.28, M['white'])
sphere("HatTop", (0,1.05,2.32),(0.68,0.68,0.38), M['white'], seg=32)
cyl("HatButton", (0,1.05,2.68),0.08,0.08, M['white'])
# red hachimaki knot? small bow at side
sphere("Knot", (0.62,0.95,2.12),(0.10,0.08,0.10), M['red'], seg=12)

# tentacles: 8 total
# resting on counter front edge (3)
tube_from_points("Tent_L1", [( -0.55,0.85,1.15),(-0.85,0.55,0.85),(-1.05,0.30,0.68),(-0.95,0.12,0.66)], 0.16, M['octo'])
tube_from_points("Tent_R1", [( 0.55,0.85,1.15),(0.85,0.55,0.85),(1.05,0.30,0.68),(1.15,0.12,0.66)], 0.16, M['octo'])
tube_from_points("Tent_Mid", [( 0.0,0.80,1.05),(0.05,0.45,0.80),(-0.05,0.20,0.66),(0.12,0.05,0.64)], 0.15, M['octo'])
# raised left holding ladle
tube_from_points("Tent_LadleArm", [(-0.70,0.95,1.45),(-1.25,0.70,1.65),(-1.55,0.72,1.45),(-1.55,0.75,1.30)], 0.15, M['octo'])
# raised right holding chopsticks up
tube_from_points("Tent_ChopArm", [(0.70,0.95,1.45),(1.30,0.80,1.80),(1.55,0.85,1.95)], 0.15, M['octo'])
# side tentacles curling
tube_from_points("Tent_L2", [(-0.80,1.10,1.20),(-1.45,1.15,1.05),(-1.70,1.05,0.75),(-1.55,0.90,0.68)], 0.14, M['octo'])
tube_from_points("Tent_R2", [(0.80,1.10,1.20),(1.45,1.30,1.10),(1.70,1.45,0.90),(1.55,1.35,0.70)], 0.14, M['octo'])
# one holding bowl on right side
tube_from_points("Tent_BowlArm", [(0.65,1.25,1.10),(1.10,1.45,0.95),(1.05,1.30,0.80)], 0.13, M['octo'])

# suckers: small belly-colored spheres along front tentacles
for (sx,sy,sz) in [(-1.0,0.18,0.60),(-0.9,0.35,0.62),(1.1,0.18,0.60),(1.0,0.38,0.62),(0.08,0.10,0.58)]:
    sphere("Sucker", (sx,sy,sz),(0.045,0.045,0.03), M['belly'], seg=10)

# ladle in left tentacle
cyl("LadleHandle", (-1.55,0.75,1.55),0.025,0.55, M['wood_dark'])
sphere("LadleCup", (-1.55,0.75,1.28),(0.11,0.11,0.06), M['metal'], seg=16)
# chopsticks in right raised tentacle
cyl("UpChop1", (1.62,0.82,2.15),0.014,0.60, M['wood_dark'], rot=(math.radians(25),0,math.radians(-15)))
cyl("UpChop2", (1.70,0.88,2.15),0.014,0.60, M['wood_dark'], rot=(math.radians(25),0,math.radians(-5)))
# noodle strand hanging from chopsticks
tube_from_points("HangingNoodle", [(1.66,0.85,1.92),(1.60,0.80,1.70),(1.68,0.78,1.52)], 0.018, M['noodle'])

# steam wisps over pot and bowls (flattened transparent spheres)
for (sx,sy,sz,s) in [(-1.55,0.75,1.55,0.18),(-1.45,0.70,1.85,0.24),(-1.60,0.78,2.15,0.30),
                     (0.55,0.55,0.95,0.14),(0.60,0.50,1.20,0.19),
                     (-0.95,0.22,0.95,0.13)]:
    sphere("Steam", (sx,sy,sz),(s,s*1.4,s), M['steam'], seg=14)

# menu board on back shelf
box("Menu", ( -1.4,1.85,1.62),(0.9,0.05,0.55), M['cream'])
box("Menu2", ( 0.2,1.85,1.62),(0.9,0.05,0.55), M['cream'])
box("MenuLine", (-1.4,1.82,1.68),(0.7,0.06,0.06), M['red'])
box("MenuLine2", (0.2,1.82,1.68),(0.7,0.06,0.06), M['red'])
# bottles on shelf
for i,x in enumerate([-1.9,-1.65,1.1,1.35,1.6]):
    cyl(f"Bottle{i}", (x,1.9,1.55),0.07,0.45, M['green'] if i%2==0 else M['red'])

# ---------- LIGHTS & CAMERA ----------
# key light
bpy.ops.object.light_add(type='AREA', location=(3, -4, 5))
key=bpy.context.active_object; key.name="KeyLight"; key.data.energy=800; key.data.size=4
key.rotation_euler=(math.radians(55),0,math.radians(25))
bpy.ops.object.light_add(type='POINT', location=(-3,-2,3))
fill=bpy.context.active_object; fill.name="FillLight"; fill.data.energy=120; fill.data.color=(0.6,0.75,1.0)
# warm lantern point
bpy.ops.object.light_add(type='POINT', location=(0,-0.6,2.5))
warm=bpy.context.active_object; warm.name="LanternGlow"; warm.data.energy=40; warm.data.color=(1.0,0.6,0.3)

# world
w=bpy.data.worlds['World']; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.08,0.07,0.14,1); bg.inputs[1].default_value=0.7

# camera
bpy.ops.object.camera_add(location=(3.4,-5.6,2.7))
cam=bpy.context.active_object; cam.name="Camera"
# look at target
target=Vector((0,0.3,1.1))
d=target-Vector(cam.location); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
cam.data.lens=42
bpy.context.scene.camera=cam

# render settings
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=900; sc.render.resolution_y=700
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.eevee.taa_render_samples=64

os.makedirs("output", exist_ok=True)
# save blend for reference (not published required but keep in work dir)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("octopus_ramen.blend"))
print("BUILD DONE objects:", len(bpy.context.scene.objects))
