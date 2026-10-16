import bpy, math, os, random
from mathutils import Vector
random.seed(8)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for x in bpy.data.materials: bpy.data.materials.remove(x)
def mat(n,c,metal=0,rough=.45):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
coral=mat('Chef • persimmon',(.86,.19,.12)); pink=mat('Suckers • soft peach',(1,.56,.36)); dark=mat('Ink',(.025,.047,.057)); teal=mat('Deep jade enamel',(.025,.24,.24),.2); mint=mat('Celadon',(.29,.65,.56)); cream=mat('Warm porcelain',(.96,.87,.66)); white=mat('Chef whites',(.98,.97,.88)); wood=mat('Honey cedar',(.48,.23,.09)); edge=mat('End grain',(.24,.095,.044)); brass=mat('Brushed brass',(.83,.51,.17),.65); red=mat('Chili red',(.65,.055,.035)); broth=mat('Miso broth',(.49,.23,.045),.05,.25); noodle=mat('Golden noodles',(1,.72,.26)); green=mat('Scallions',(.12,.44,.16)); egg=mat('Egg yolk',(1,.48,.035)); seaweed=mat('Nori',(.035,.115,.07)); glow=mat('Lantern paper',(1,.63,.25)); p=glow.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.33,.08,1); p.inputs['Emission Strength'].default_value=.35

def apply(o,n,m):
 o.name=n; o.data.materials.append(m); return o
def uv(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc); o=bpy.context.object; o.scale=scale; apply(o,n,m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def cube(n,loc,scale,m,b=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); apply(o,n,m)
 if b: mod=o.modifiers.new('Soft crafted edges','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,dep,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=dep,location=loc); o=bpy.context.object; apply(o,n,m); mod=o.modifiers.new('Edge easing','BEVEL'); mod.width=.025; mod.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o
def line(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.resolution_u=16; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
 for b,p in zip(s.bezier_points,pts):b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); apply(o,n,m); return o
def text(n,body,loc,size,m):
 c=bpy.data.curves.new(n,'FONT'); c.body=body; c.align_x='CENTER'; c.align_y='CENTER'; c.size=size; c.extrude=.008; c.bevel_depth=.002; o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); apply(o,n,m); return o
def lathe(n,profile,loc,m):
 verts=[]; faces=[]; N=64
 for r,z in profile:
  verts.extend([(loc[0]+r*math.cos(i*2*math.pi/N),loc[1]+r*math.sin(i*2*math.pi/N),loc[2]+z) for i in range(N)])
 for j in range(len(profile)-1):
  for i in range(N):a=j*N+i; b=j*N+(i+1)%N; faces.append((a,b,b+N,a+N))
 mesh=bpy.data.meshes.new(n); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(n,mesh); bpy.context.collection.objects.link(o); apply(o,n,m)
 for p in mesh.polygons:p.use_smooth=True
 return o
# raised little street stage
cube('Floating diorama base',(0,0,.12),(6.3,4.5,.26),teal,.15)
cube('Stone inset',(0,0,.29),(6.05,4.25,.14),cream,.06)
for x in range(12):
 for y in range(8):cube('Paving joint',(-2.78+x*.505,-1.86+y*.52,.367),(.485,.50,.025),mint if (x+y)%7==0 else cream,.008)
# booth carcass
cube('Counter cabinet',(0,-.43,1.04),(5.35,1.03,1.35),teal,.09)
for x in [-2.35+i*.39 for i in range(13)]:cube('Cedar vertical fluting',(x,-.963,1.04),(.075,.045,1.15),wood,.015)
cube('Counter lower brass trim',(0,-1.0,.49),(5.25,.055,.06),brass)
cube('Thick cedar service counter',(0,-.47,1.78),(5.7,1.44,.22),wood,.09)
cube('Counter edge inlay',(0,-1.194,1.78),(5.48,.025,.045),brass,.005)
for x in [-2.65,2.65]:
 cube('Frame post',(x,.65,2.57),(.18,.21,4.42),edge)
 for z in [.65,4.45]:cube('Brass post collar',(x,.65,z),(.23,.26,.16),brass,.02)
cube('Back shelf',(0,1.32,1.68),(5.2,.63,.16),wood)
cube('Back panel',(0,1.67,1.02),(5.35,.15,1.3),teal)
# roof pitched stepped tile canopy
cube('Roof beam',(0,.57,4.61),(5.95,2.52,.20),edge)
for side in [-1,1]:
 for j in range(4):
  y=.57+side*(.16+j*.34); z=5.02-j*.105
  for i in range(15):
   o=cube('Jade roof tiles',(-2.84+i*.405,y,z),(.42,.49,.11),teal if (i+j)%3 else mint,.035); o.rotation_euler.x=side*-.28
cyl('Roof ridge',(0,.57,5.09),.09,5.95,brass).rotation_euler.y=math.pi/2
# hanging sign in front roof
cube('Signboard',(0,-.79,4.54),(3.35,.16,.65),teal,.08)
for x in [-1.61,1.61]:cube('Sign end caps',(x,-.89,4.54),(.055,.025,.50),brass,.01)
text('Shop name','OCTO RAMEN',(0,-.888,4.60),.35,cream)
text('Shop subtitle','EIGHT ARMS • ONE PERFECT BOWL',(0,-.89,4.35),.092,cream)
# cloth curtain rearward so chef clear
for i in range(6):
 x=-2.18+i*.87
 cube('Noren indigo fabric',(x,.77,4.10),(.83,.065,.63),teal,.055)
 text('Noren motif','~',(x,.723,4.05),.30,cream)
# chef
uv('Octopus mantle',(0,.30,2.92),(.77,.60,.91),coral)
uv('Lower body',(0,.26,2.26),(.68,.56,.43),coral)
# apron bib front
uv('Chef apron bib',(0,-.255,2.30),(.45,.08,.46),white)
line('Apron neck strap',[(-.40,-.20,2.60),(-.35,-.32,2.78),(0,-.36,2.65),(.35,-.32,2.78),(.40,-.20,2.60)],.035,cream)
text('Apron insignia','8',(0,-.345,2.28),.23,teal)
for x in [-.28,.28]:
 uv('Eye white',(x,-.247,3.12),(.185,.115,.22),white)
 uv('Friendly pupil',(x+.025,-.351,3.11),(.080,.045,.115),dark)
 uv('Eye sparkle',(x+.003,-.391,3.155),(.026,.015,.031),white)
 uv('Cheek',(x*1.8,-.19,2.90),(.13,.055,.065),pink)
line('Smile',[(-.16,-.303,2.86),(0,-.345,2.80),(.16,-.303,2.86)],.025,dark)
# toque
cyl('Toque band',(0,.30,3.71),.56,.27,white)
for i in range(7):
 a=i*math.tau/7; uv('Puffed chef hat',(.40*math.cos(a),.30+.34*math.sin(a),3.98),(.30,.27,.32),white)
uv('Toque crown',(0,.30,4.04),(.44,.39,.31),white)
# tapered sculptural tentacles using smooth samples of Bezier via catmull rom
arms=[[( -.43,.25,2.4),(-.95,.18,2.25),(-1.45,-.30,2.04),(-1.80,-.65,2.12),(-1.88,-.67,2.48)],[(.43,.25,2.4),(.92,.06,2.20),(1.5,-.26,2.15),(1.88,-.31,2.63),(1.92,-.30,2.89)],[(-.5,.5,2.35),(-1.1,.68,2.5),(-1.65,.66,2.92),(-1.85,.40,3.13),(-1.69,.16,3.19)],[(.5,.5,2.35),(1.1,.77,2.39),(1.43,.8,2.7),(1.35,.55,2.92),(1.15,.40,2.9)],[(-.3,.03,2.21),(-.7,-.48,1.99),(-.95,-1.12,1.95),(-1.22,-1.35,1.60),(-1.50,-1.30,1.73)],[(.30,.03,2.21),(.72,-.4,1.98),(.9,-1.06,1.94),(1.2,-1.34,1.48),(1.53,-1.27,1.67)],[(-.45,.63,2.22),(-1.1,1.04,1.94),(-2.03,.91,1.91),(-2.30,.56,2.10),(-2.21,.34,2.24)],[(.45,.63,2.22),(1.07,1.14,1.94),(2.02,.99,1.92),(2.30,.73,2.13),(2.18,.49,2.26)]]
for k,pts in enumerate(arms):
 ps=[Vector(p) for p in pts]; samples=[]
 for j in range(len(ps)-1):
  a=ps[max(j-1,0)];b=ps[j];c=ps[j+1];d=ps[min(j+2,len(ps)-1)]
  for s in range(10):
   t=s/10; samples.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 samples.append(ps[-1]); vs=[]; fs=[]
 for i,p in enumerate(samples):
  t=i/(len(samples)-1); r=.225*(1-t)**.65+.025; tangent=(samples[min(i+1,len(samples)-1)]-samples[max(i-1,0)]).normalized(); u=tangent.cross(Vector((0,1,0))).normalized(); v=tangent.cross(u).normalized()
  for h in range(12):vs.append(p+r*(u*math.cos(h*math.tau/12)+v*math.sin(h*math.tau/12)))
  if i%3==0 and i>3:
   # front facing suckers visible on each curling arm
   pos=p+Vector((0,-r*.85,-r*.28)); ob=uv('Arm %d • suction cup'%k,pos,(r*.44,.038,r*.42),pink)
   uv('Sucker inset',pos+Vector((0,-.030,0)),(r*.22,.012,r*.20),coral)
 for i in range(len(samples)-1):
  for h in range(12): a=i*12+h;b=i*12+(h+1)%12;fs.append((a,b,b+12,a+12))
 fs.extend([tuple(range(11,-1,-1)),tuple((len(samples)-1)*12+h for h in range(12))]); me=bpy.data.meshes.new('Tentacle');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('Tentacle %02d'%(k+1),me);bpy.context.collection.objects.link(ob);apply(ob,ob.name,coral)
 for p in me.polygons:p.use_smooth=True
# ramen bowls

def bowl(x,y,z,r=.54):
 lathe('Porcelain ramen bowl',[(.18,0),(.23,.045),(.30,.10),(r*.88,.29),(r,.40),(r,.435),(r-.035,.44),(r-.055,.39),(r*.78,.27),(.23,.10),(.18,.07)],(x,y,z),cream)
 lathe('Red bowl rim',[(r,.395),(r+.005,.425),(r-.005,.44)],(x,y,z),red)
 cyl('Rich miso soup',(x,y,z+.345),r*.88,.025,broth)
 for j in range(9):
  yy=y-.28+j*.063; pts=[]
  for i in range(9):pts.append((x-.30+i*.075,yy+.025*math.sin(i*2+j),z+.369+.009*math.cos(i+j)))
  line('Wavy ramen noodles',pts,.018,noodle)
 uv('Soy marinated egg',(x+.16,y+.08,z+.405),(.15,.19,.06),white);uv('Golden egg center',(x+.16,y+.065,z+.459),(.085,.11,.018),egg)
 ob=cube('Nori sheet',(x-.23,y+.19,z+.49),(.20,.045,.32),seaweed,.01);ob.rotation_euler.y=-.25
 for j in range(9):
  a=random.random()*math.tau; rr=random.uniform(.08,.35); cyl('Chopped scallion',(x+rr*math.cos(a),y+rr*math.sin(a),z+.397),.035,.032,green)
 for i in range(3):
  a=i*2.1; uv('Chashu pork',(x-.17+i*.13,y-.14,z+.405),(.13,.10,.025),pink)
bowl(-.7,-.69,1.90);bowl(1.8,-.77,1.90,.48)
# steam stylized fine wisps
steam=mat('Steam ivory',(.83,.88,.80))
for x in [-.89,-.57]:line('Steam curl',[(x,-.64,2.40),(x-.07,-.64,2.60),(x+.05,-.64,2.78),(x,-.64,2.92)],.012,steam)
# lifted noodles and chopsticks at right hand
for x in [1.86,2.0]:line('Held chopstick',[(x,-.32,2.95),(x-.63,-.55,2.52)],.021,wood)
for i in range(4):line('Dangling noodles',[(1.36+i*.045,-.52,2.65),(1.34+i*.045,-.54,2.44),(1.43+i*.045,-.59,2.28)],.014,noodle)
# ladle in upper left hand
line('Ladle handle',[(-1.70,.13,3.22),(-2.07,-.05,2.66)],.035,brass)
uv('Ladle scoop',(-2.10,-.07,2.62),(.18,.15,.07),brass)
# stock pot and condiments
cyl('Stock pot',(1.94,1.23,2.00),.37,.55,brass)
cyl('Stock pot lid',(1.94,1.23,2.29),.40,.055,cream);uv('Lid knob',(1.94,1.23,2.35),(.09,.09,.07),dark)
for x in [1.48,2.4]:line('Pot handles',[(x,1.23,2.07),(x,1.23,2.22),(x+(.10 if x<2 else -.1),1.23,2.23)],.035,dark)
for x in [-2.25,-1.95,-1.65]:
 cyl('Spice jar',(x,1.25,1.93),.11,.35,cream);cyl('Spice jar lid',(x,1.25,2.12),.12,.05,red)
cube('Serving tray',(-2.05,-.65,1.93),(.72,.54,.06),edge)
cyl('Soy bottle',(-2.22,-.65,2.13),.10,.35,dark);cyl('Soy red cap',(-2.22,-.65,2.33),.075,.06,red)
cyl('Chopstick cup',(-1.91,-.67,2.10),.12,.29,teal)
for i in range(5):line('Spare chopsticks',[(-1.96+i*.024,-.67,2.08),(-2.01+i*.043,-.66,2.51)],.012,wood)
# hanging lanterns at ends
for x in [-2.36,2.36]:
 line('Lantern suspension',[(x,-.47,4.62),(x,-.47,4.21)],.025,dark)
 uv('Paper lantern',(x,-.47,3.91),(.29,.29,.43),glow)
 for z in [3.52,4.30]:cyl('Lantern cap',(x,-.47,z),.16,.07,dark)
 for j in range(9):
  z=3.56+j*.085;rr=.29*math.sqrt(max(0,1-((z-3.91)/.43)**2));lathe('Lantern hoops',[(rr,z-.009),(rr,z+.009)],(x,-.47,0),wood)
 text('Lantern emblem','8',(x,-.758,3.92),.24,red)
# front badge
cube('Front logo plaque',(0,-1.01,1.08),(1.40,.075,.68),cream,.12)
text('Front badge','OCTO',(0,-1.057,1.18),.26,teal);text('Front sub','RAMEN BAR',(0,-1.059,.93),.12,teal)
# stools in street
for x in [-1.95,0,1.95]:
 for dx in [-.21,.21]:
  for dy in [-.18,.18]:line('Stool legs',[(x+dx*1.35,-1.70+dy*1.4,.40),(x+dx,-1.70+dy,.96)],.045,edge)
 cyl('Round stool seat',(x,-1.70,1.02),.37,.13,wood);cyl('Seat cushion',(x,-1.70,1.11),.32,.09,red)
# scene
world=bpy.data.worlds.new('Studio world') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.24,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
floor=mat('Backdrop',(.11,.18,.20));cube('Studio floor',(0,0,-.15),(200,200,.05),floor,.0)
def area(n,loc,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm key',(-3,-6,9),1100,6,(1,.80,.62));area('Cool fill',(6,-2,6),850,5,(.65,.85,1));area('Rim',(1,5,8),1250,4,(1,.63,.32))
bpy.ops.object.camera_add(location=(7,-11,7.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,2.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.4;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX'
os.makedirs('output',exist_ok=True)
sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.abspath('output/octo-ramen.png');bpy.ops.render.render(write_still=True)
# Exclude studio ground from portable asset
bpy.data.objects.remove(bpy.data.objects['Studio floor'],do_unlink=True)
# curves and text to meshes for glTF
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
 if o.type in {'CURVE','FONT'}:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
bpy.ops.export_scene.gltf(filepath=os.path.abspath('output/octo-ramen.glb'),export_format='GLB',export_cameras=False,export_lights=False)
