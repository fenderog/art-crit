import bpy, math, os, random
from mathutils import Vector
random.seed(8)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
os.makedirs('output',exist_ok=True)
def mat(n,c,rough=.45,metal=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
coral=mat('Chef • persimmon coral',(.82,.205,.13));lightcoral=mat('Suction cups • peach', (1,.56,.37));dark=mat('Ink • deep aubergine',(.055,.035,.052));cream=mat('Porcelain & cotton',(.96,.91,.73));white=mat('Eye whites',(1,.97,.88));teal=mat('Stall • petrol enamel',(.025,.25,.27));teallight=mat('Edge • jade',(.09,.45,.44));wood=mat('Honey bamboo',(.55,.26,.095));woodlight=mat('Cut wood',(.77,.44,.19));red=mat('Vermilion',(.72,.08,.035));gold=mat('Brass',(.8,.51,.15),.28,.65);steel=mat('Steel',(.31,.43,.45),.24,.75);broth=mat('Miso broth',(.53,.22,.045),.22);noodle=mat('Egg noodles',(.98,.72,.27));green=mat('Scallion',(.15,.4,.09));egg=mat('Egg white',(1,.94,.75));yolk=mat('Jammy yolk',(1,.43,.025));pink=mat('Fishcake swirl',(.98,.3,.4));black=mat('Nori',(.025,.09,.063));floor=mat('Display plinth',(.13,.2,.23));bg=mat('Backdrop',(.055,.1,.13));lantern=mat('Lantern • warm rice paper',(1,.49,.16));p=lantern.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.22,.035,1);p.inputs['Emission Strength'].default_value=.4

def apply(o,m):o.data.materials.append(m);return o
def bevel(o,b=.06):mod=o.modifiers.new('Soft handcrafted edges','BEVEL');mod.width=b;mod.segments=3;o.modifiers.new('Corner normals','WEIGHTED_NORMAL');return o
def box(n,loc,scale,m,b=.05):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False, rotation=False, scale=True);apply(o,m)
 if b:bevel(o,b)
 return o
def uv(n,loc,sc,m,seg=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.name=n;o.scale=sc;apply(o,m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def cyl(n,loc,r,depth,m,vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;apply(o,m);bevel(o,.025);return o
def line(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for b,p in zip(s.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);apply(o,m);return o
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,24);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def text(n,txt,loc,size,m):
 c=bpy.data.curves.new(n,'FONT');c.body=txt;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.008;c.bevel_depth=.003;o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);apply(o,m);return o
# floating display foundation
box('Rounded diorama base',(0,0,.12),(6.5,4.8,.32),floor,.18)
box('Bamboo floor',(0,0,.32),(6.15,4.45,.15),wood,.06)
for x in range(13):
 box('Floorboard seam',(-2.9+x*.48,0,.401),(.012,4.25,.006),woodlight,.001)
# Booth structure
for x in [-2.7,2.7]:
 for y in [.95,-1.02]:
  box('Timber upright',(x,y,2.65),(.15,.15,4.5),wood,.035)
  box('Brass foot',(x,y,.6),(.21,.21,.3),gold,.02)
box('Counter cabinet',(0,-.92,1.05),(5.5,.88,1.25),teal,.09)
for x in [-2.4,-1.2,0,1.2,2.4]:box('Front inset panel',(x,-1.375,1.08),(1.07,.045,.87),teallight,.04)
for z in [.58,1.58]:box('Counter brass trim',(0,-1.41,z),(5.35,.035,.035),gold,.008)
box('Broad counter top',(0,-.95,1.76),(5.85,1.25,.2),woodlight,.08)
box('Counter dark edge',(0,-1.6,1.73),(5.8,.035,.1),wood,.015)
# rear cupboard & cooking worktop
box('Back cabinet',(0,1.25,1.1),(5.1,.65,1.3),teal,.07)
box('Back worktop',(0,1.22,1.8),(5.35,.85,.16),steel,.04)
for x in [-1.8,-.6,.6,1.8]:
 box('Rear drawer',(x,.904,1.32),(1.08,.04,.48),teallight,.025);rod('Drawer pull',(x-.16,.85,1.36),(x+.16,.85,1.36),.025,gold)
# roof canopy, planks
box('Canopy beam',(0,0,4.75),(5.9,2.8,.17),wood,.04)
for i in range(17):
 x=-2.88+i*.36
 o=box('Striped canopy',(x,0,4.89),(.355,3.05,.16),teal if i%2 else teallight,.04)
 uv('Scalloped awning edge',(x,-1.52,4.69),(.179,.065,.22),teal if i%2 else teallight,20,12)
# big header
box('Sign brass surround',(0,-1.64,4.38),(3.75,.14,.68),gold,.07)
box('Sign enamel face',(0,-1.73,4.38),(3.62,.06,.56),dark,.04)
text('Shop title','TAKO RAMEN',(0,-1.773,4.4),.37,cream)
# decorative corner sign dots
for x in [-1.66,1.66]:uv('Sign rivet',(x,-1.78,4.39),(.035,.018,.035),gold,16,8)
# hanging lanterns
for x in [-2.28,2.28]:
 rod('Lantern hanger',(x,-1.18,4.72),(x,-1.18,4.28),.022,dark)
 uv('Paper lantern',(x,-1.18,3.93),(.3,.29,.43),lantern)
 for z in [3.56,4.3]:cyl('Lantern cap',(x,-1.18,z),.18,.075,dark)
 for z in [3.64,3.75,3.87,3.99,4.11,4.22]:
  rr=.3*math.sqrt(max(.1,1-((z-3.93)/.43)**2));pts=[(x+rr*math.cos(t*math.tau/48),-1.18+rr*math.sin(t*math.tau/48),z) for t in range(49)];line('Lantern rib',pts,.009,wood)
 text('Lantern emblem','麺' if False else '8',(x,-1.475,3.95),.27,dark)
# octopus body and eight arms
uv('Octopus mantle',(0,.25,2.76),(.77,.61,.83),coral)
uv('Lower mantle',(0,.23,2.2),(.65,.54,.43),coral)
# tube with catmull sampling
paths=[ [(-.43,.2,2.35),(-.96,-.08,2.24),(-1.32,-.55,2.32),(-1.6,-.8,2.7),(-1.48,-.8,3.03)],[(.43,.2,2.35),(.97,-.05,2.3),(1.38,-.25,2.65),(1.58,-.32,3.03),(1.83,-.33,3.16)], [(-.5,.4,2.2),(-1.17,.7,2.12),(-1.86,.68,2.24),(-2.03,.46,2.58),(-1.88,.25,2.72)],[(.5,.4,2.2),(1.17,.7,2.14),(1.9,.8,2.22),(2.13,.54,2.46),(2.0,.32,2.59)], [(-.37,-.02,2.18),(-.78,-.62,2.03),(-.95,-1.16,1.99),(-1.25,-1.52,1.99),(-1.59,-1.53,2.1),(-1.55,-1.35,2.24)],[(.37,-.02,2.18),(.77,-.61,2.03),(.98,-1.18,1.99),(1.26,-1.52,2.0),(1.64,-1.53,2.12),(1.6,-1.31,2.24)], [(-.28,.5,2.12),(-.6,.95,1.98),(-.88,1.24,2.02),(-1.12,1.28,2.2)],[(.28,.5,2.12),(.57,1.0,1.99),(.82,1.37,2.04),(1.03,1.42,2.23)] ]
def tentacle(idx,points):
 ps=[Vector(p) for p in points];samples=[]
 for j in range(len(ps)-1):
  a=ps[max(0,j-1)];b=ps[j];c=ps[j+1];d=ps[min(len(ps)-1,j+2)]
  for k in range(10):
   t=k/10;samples.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 samples.append(ps[-1]);vs=[];fs=[]
 for j,p in enumerate(samples):
  tangent=(samples[min(j+1,len(samples)-1)]-samples[max(0,j-1)]).normalized();u=tangent.cross(Vector((0,1,0))).normalized();v=tangent.cross(u).normalized();r=.22*(1-j/(len(samples)-1))**.7+.024
  for k in range(12):vs.append(p+r*(u*math.cos(k*math.tau/12)+v*math.sin(k*math.tau/12)))
  if j:
   for k in range(12):fs.append(((j-1)*12+k,(j-1)*12+(k+1)%12,j*12+(k+1)%12,j*12+k))
  if j>6 and j%4==0:
   # pale suction cups toward viewer
   pos=p+Vector((0,-r*.89,-r*.12));uv('Arm %d suction cup'%idx,pos,(r*.48,.034,r*.48),lightcoral,16,8);uv('Suction inset',pos+Vector((0,-.029,0)),(r*.25,.008,r*.25),coral,12,8)
 mesh=bpy.data.meshes.new('Tapered arm');mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new('Tentacle %02d'%idx,mesh);bpy.context.collection.objects.link(o);apply(o,coral)
 for p in mesh.polygons:p.use_smooth=True
for i,p in enumerate(paths):tentacle(i+1,p)
# face visible front
for x in [-.28,.28]:
 uv('Eye',(x,-.299,2.9),(.19,.115,.235),white);uv('Pupil',(x+.025,-.403,2.9),(.083,.035,.112),dark);uv('Eye sparkle',(x+.005,-.435,2.945),(.026,.012,.031),white,16,10)
 uv('Cheek blush',(x*1.7,-.29,2.65),(.12,.035,.065),lightcoral)
line('Happy smile',[(-.18,-.365,2.62),(0,-.409,2.54),(.18,-.365,2.62)],.026,dark)
# hat band + cloud toque
cyl('Chef hat band',(0,.25,3.47),.5,.22,cream)
for x,y,z,s in [(-.34,.25,3.7,.32),(0,.25,3.82,.4),(.33,.25,3.72,.33),(0,.02,3.71,.3),(0,.48,3.72,.3)]:uv('Puffy chef toque',(x,y,z),(s,s*.85,s*.82),white)
# neckerchief
for x in [-.17,.17]:
 o=uv('Chef scarf',(x,-.28,2.23),(.18,.075,.21),cream);o.rotation_euler[1]=x*2
uv('Scarf knot',(0,-.36,2.34),(.1,.065,.09),cream)
# serving bowl lathed cross section
def bowl(n,x,y,z,r=.53):
 profile=[(0,0),(.24,.0),(.29,.035),(.32,.12),(.43,.28),(.53,.42),(.54,.46),(.49,.46),(.46,.39),(.36,.23),(.24,.14),(0,.14)]
 vs=[];fs=[]
 for rr,zz in profile:
  for k in range(64):vs.append((x+rr*r/.53*math.cos(k*math.tau/64),y+rr*r/.53*math.sin(k*math.tau/64),z+zz))
 for j in range(len(profile)-1):
  for k in range(64):fs.append((j*64+k,j*64+(k+1)%64,(j+1)*64+(k+1)%64,(j+1)*64+k))
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);apply(o,cream)
 for f in me.polygons:f.use_smooth=True
 for zz,rr in [(.4,.52),(.45,.535)]:line('Bowl red rim',[(x+rr*r/.53*math.cos(t*math.tau/64),y+rr*r/.53*math.sin(t*math.tau/64),z+zz) for t in range(65)],.018,red)
 cyl('Rich broth',(x,y,z+.365),r*.86,.025,broth)
 for j in range(8):
  yy=y-.24+j*.064;pts=[(x-.29+k*.058,yy+.025*math.sin(k*2+j),z+.39+.01*math.cos(k+j)) for k in range(11)];line('Wavy ramen noodle',pts,.018,noodle)
 uv('Egg half',(x+.19,y+.04,z+.426),(.14,.19,.055),egg);uv('Golden egg yolk',(x+.19,y+.04,z+.476),(.081,.11,.018),yolk)
 for j in range(9):
  xx=x+random.uniform(-.27,.18);yy=y+random.uniform(-.24,.2);o=cyl('Scallion slice',(xx,yy,z+.425),.032,.025,green,12)
 o=box('Nori sheet',(x-.24,y+.19,z+.5),(.19,.03,.26),black,.01);o.rotation_euler[1]=-.3
 uv('Naruto fishcake',(x-.15,y-.13,z+.435),(.105,.095,.025),egg)
 line('Fishcake pink spiral',[(x-.15+(.008+i*.002)*math.cos(i*.5),y-.13+(.008+i*.002)*math.sin(i*.5),z+.462) for i in range(30)],.009,pink)
 return z+.46
bowl('Signature ramen',0,-1.09,1.86,.57)
bowl('Side ramen',-2.02,-.91,1.86,.4)
# raised noodle strands from left arm with chopsticks
for dx in [0,.085]:rod('Held bamboo chopsticks',(-1.6+dx,-.8,3.11),(-.42+dx,-.97,2.56),.023,woodlight)
for j in range(5):line('Lifted noodles',[(-.63+j*.04,-.96,2.65),(-.6+j*.04,-.98,2.49),(-.64+j*.045,-1.0,2.34),(-.52+j*.045,-1.0,2.28)],.014,noodle)
# ladle in right arm
rod('Ladle handle',(1.8,-.32,3.2),(1.24,-.5,2.45),.035,wood)
uv('Ladle cup',(1.22,-.5,2.41),(.18,.16,.075),steel)
# stockpot in rear left
cyl('Stove ring',(-1.85,1.15,1.94),.43,.1,dark)
cyl('Stock pot',(-1.85,1.15,2.17),.36,.4,steel)
cyl('Pot lid',(-1.85,1.15,2.39),.39,.045,steel)
uv('Lid knob',(-1.85,1.15,2.45),(.075,.075,.055),dark)
for xx in [-2.28,-1.42]:line('Pot handles',[(xx+.08,1.15,2.28),(xx,1.15,2.29),(xx,1.15,2.12),(xx+.08,1.15,2.13)],.032,steel)
# condiments right counter
for x,m in [(1.95,red),(2.31,gold)]:
 cyl('Condiment jar',(x,-.92,2.03),.115,.32,m);cyl('Jar lid',(x,-.92,2.21),.123,.05,dark);box('Bottle label',(x,-1.038,2.04),(.12,.012,.14),cream,.01)
cyl('Chopstick holder',(2.58,-.67,2.01),.13,.3,teal)
for j in range(7):rod('Spare chopstick',(2.58+random.uniform(-.085,.085),-.67+random.uniform(-.07,.07),2.02),(2.58+random.uniform(-.13,.13),-.67+random.uniform(-.1,.1),2.57),.014,woodlight)
# small menu standing front right
ob=box('Menu board',(1.05,-1.44,2.13),(.53,.085,.52),dark,.025);text('Menu header','MENU',(1.05,-1.49,2.27),.105,cream);text('Menu items','MISO  12\nSHOYU  10\nSPICY  14',(1.05,-1.49,2.08),.073,cream)
# stools front
for x in [-1.85,1.85]:
 cyl('Stool seat',(x,-2.0,.94),.34,.14,red)
 for dx in [-.19,.19]:
  for dy in [-.16,.16]:rod('Stool leg',(x+dx,-2+dy,.43),(x+dx*.8,-2+dy*.8,.9),.045,wood)
 line('Stool foot ring',[(x+.23*math.cos(t*math.tau/32),-2+.23*math.sin(t*math.tau/32),.62) for t in range(33)],.025,gold)
# booth front identity plaque
box('Front badge',(0,-1.434,1.09),(.78,.045,.65),dark,.09)
text('Front badge octo','8',(0,-1.467,1.17),.42,cream)
text('Front badge year','EST. 2024',(0,-1.468,.89),.078,gold)
# steam curls, subtle opaque warm pale
steam=mat('Steam',(.64,.75,.73),.9)
for i in range(2):line('Steam rising',[(-1.9+i*.2,1.15,2.5),(-2+i*.2,1.15,2.67),(-1.84+i*.2,1.15,2.84),(-1.92+i*.2,1.15,3.0)],.014,steam)
# scene
box('Ground',(0,0,-.18),(200,200,.2),bg,.0)
world=bpy.context.scene.world;world.color=(.17,.17,.17);world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.13,.2,.25,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.45

def area(n,loc,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm key',(-3,-6,9),1100,(1,.79,.59),6);area('Cool fill',(5,-2,6),850,(.59,.82,1),5);area('Top rim',(1,4,8),1400,(1,.52,.27),4)
for x in [-2.28,2.28]:
 bpy.ops.object.light_add(type='POINT',location=(x,-1.2,3.9));bpy.context.object.data.energy=25;bpy.context.object.data.color=(1,.36,.08);bpy.context.object.data.shadow_soft_size=.5
bpy.ops.object.camera_add(location=(8,-12,8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,2.35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.6;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.abspath('output/tako-ramen.png');scene.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene.blend'))
bpy.ops.render.render(write_still=True)
