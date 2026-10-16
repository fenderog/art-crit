import bpy, math, os, random
from mathutils import Vector
from math import sin, cos, pi
random.seed(11)
OUT=os.path.join(os.getcwd(),'output'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)

def mat(name,color,metal=0,rough=.4):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 return m
coral=mat('Chef • persimmon coral',(.87,.19,.12)); coralLight=mat('Mantle flecks',(.98,.36,.23)); suck=mat('Suction cups • peach', (1,.65,.43)); cupdark=mat('Sucker recess',(.55,.13,.085)); cream=mat('Warm porcelain',(.96,.86,.65)); white=mat('Chef whites',(.97,.97,.86)); ink=mat('Midnight indigo',(.025,.075,.10)); teal=mat('Lagoon enamel',(.035,.38,.36),.12); darkteal=mat('Deep teal',(.025,.19,.20)); red=mat('Vermilion lacquer',(.72,.055,.04)); gold=mat('Warm brass',(.8,.48,.13),.65,.25); wood=mat('Honey cedar',(.48,.23,.09)); woodlight=mat('Cedar edge',(.73,.40,.18)); wooddark=mat('Cedar end grain',(.25,.10,.035)); noodle=mat('Golden noodles',(.98,.68,.22)); broth=mat('Miso broth',(.54,.22,.045),0,.24); green=mat('Scallion green',(.12,.43,.15)); greenlight=mat('Scallion centers',(.58,.73,.24)); yolk=mat('Marinated egg yolk',(1,.43,.035),0,.27); pork=mat('Chashu',(.67,.28,.17)); pink=mat('Naruto pink',(.97,.33,.44)); steel=mat('Brushed steel',(.43,.52,.54),.8,.25); steam=mat('Steam ivory',(.80,.87,.79)); floor=mat('Studio background',(.105,.17,.21))
def finish(o,name,ma,smooth=False):
 o.name=name
 if ma:o.data.materials.append(ma)
 if smooth and o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def cube(name,loc,scale,ma,bev=.05):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); finish(o,name,ma)
 if bev: mod=o.modifiers.new('Soft crafted edges','BEVEL'); mod.width=bev; mod.segments=3; o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def uv(name,loc,scale,ma):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc); o=bpy.context.object; o.scale=scale; return finish(o,name,ma,True)
def cyl(name,loc,r,depth,ma,vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); return finish(bpy.context.object,name,ma,True)
def torus(name,loc,r,t,ma,normal=(0,0,1)):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=32,minor_segments=10,location=loc); o=bpy.context.object; o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler(); return finish(o,name,ma,True)
def line(name,pts,r,ma):
 cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12; cu.bevel_depth=r; cu.bevel_resolution=3
 sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
 for b,co in zip(sp.bezier_points,pts): b.co=co; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o
def rod(name,a,b,r,ma):
 d=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,r,d.length,ma,24); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o
def text(name,body,loc,size,ma,extr=.003):
 cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=extr; cu.bevel_depth=.0015
 o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(pi/2,0,0); o.data.materials.append(ma); return o
# platform and stall
cube('Floating diorama plinth',(0,0,.18),(6.9,4.65,.36),darkteal,.18)
cube('Brass plinth reveal',(0,0,.365),(6.72,4.48,.045),gold,.02)
for i in range(15): cube('Deck cedar plank %02d'%i,(-3.15+i*.45,0,.43),(.43,4.3,.13),woodlight if i%3 else wood,.025)
for x in [-2.65,2.65]:
 for y in [-.27,1.42]:
  cube('Booth structural upright',(x,y,2.95),(.16,.16,5.0),wood,.035)
  cube('Post brass shoe',(x,y,.72),(.21,.21,.44),gold,.025)
# enclosure
cube('Back teal panel',(0,1.48,1.66),(5.4,.16,2.2),darkteal)
for x in [-2.68,2.68]:cube('Side enamel cabinet',(x,.52,1.45),(.12,1.9,1.7),teal)
cube('Counter cabinet',(0,-.57,1.4),(5.35,.2,1.8),teal)
for x in [-2.48,-1.65,-.82,0,.82,1.65,2.48]:cube('Cabinet battens',(x,-.70,1.4),(.055,.055,1.65),gold,.015)
cube('Cabinet lower rail',(0,-.73,.64),(5.5,.09,.12),woodlight)
cube('Counter top dark edge',(0,-.35,2.23),(5.95,1.9,.20),wooddark,.07)
for i in range(4):cube('Counter top long plank',(0,-1.02+i*.46,2.36),(5.92,.44,.12),woodlight if i%2 else wood,.03)
cube('Front foot rail',(0,-1.12,.8),(5.8,.10,.10),gold,.04)
for x in [-2.4,2.4]:rod('Rail support',(x,-.65,.8),(x,-1.12,.8),.045,gold)
# back shelving
for z in [2.6,3.18]:cube('Back wall shelf',(0,1.24,z),(4.95,.48,.10),woodlight)
for x in [-2.3,-1.95,-1.6,1.55,1.9,2.25]:
 cyl('Stock jar',(x,1.2,2.85),.12,.42,cream if x<0 else teal)
 cyl('Jar lid',(x,1.2,3.08),.135,.055,wooddark)
 cube('Jar paper label',(x,1.072,2.86),(.13,.012,.17),white,.005)
# roof, curved stripe awning
cube('Roof ridge beam',(0,.57,5.43),(5.85,.15,.18),wooddark)
for x in [-2.75,2.75]:rod('Roof lateral support',(x,-1.33,5.16),(x,1.65,5.16),.07,wood)
for j in range(12):
 x1=-2.96+j*.493; x2=x1+.493; verts=[]; faces=[]
 for k in range(17):
  y=-1.43+k*3.17/16; z=5.16+.50*sin(pi*k/16)
  verts.extend([(x1,y,z),(x2,y,z)])
 for k in range(16):faces.append((2*k,2*k+1,2*k+3,2*k+2))
 me=bpy.data.meshes.new('Woven canopy'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Canvas stripe %02d'%j,me); bpy.context.collection.objects.link(o); finish(o,o.name,red if j%2==0 else cream,True); mod=o.modifiers.new('Canvas thickness','SOLIDIFY'); mod.thickness=.035
 # scalloped front valance
 pts=[(x1,-1.44,5.17),(x2,-1.44,5.17),(x2,-1.44,4.99)]
 for k in range(9):
  t=k*pi/8; pts.append(((x1+x2)/2+(x2-x1)/2*cos(t),-1.44,4.99-.12*sin(t)))
 pts.append((x1,-1.44,5.17)); me=bpy.data.meshes.new('Scallop'); me.from_pydata(pts,[],[tuple(range(len(pts)))]); me.update(); o=bpy.data.objects.new('Scalloped canvas edge',me); bpy.context.collection.objects.link(o); finish(o,o.name,red if j%2==0 else cream); m=o.modifiers.new('Hem thickness','SOLIDIFY');m.thickness=.025
# rooftop marquee positioned above roof
cube('Marquee frame',(0,-.02,5.98),(4.60,.20,.80),wooddark,.12)
cube('Marquee enamel',(0,-.136,5.98),(4.40,.045,.63),cream,.08)
text('Shop title','O C T O   R A M E N',(0,-.169,6.05),.38,ink)
text('Shop subtitle','EIGHT ARMS  /  ONE PERFECT BOWL',(0,-.172,5.80),.105,red)
for x in [-2.08,2.08]:uv('Marquee screw',(x,-.17,5.98),(.035,.018,.035),gold)
# lanterns
for x in [-2.29,2.29]:
 rod('Lantern cord',(x,-.76,5.17),(x,-.76,4.8),.015,ink)
 uv('Paper lantern',(x,-.76,4.43),(.28,.26,.42),cream)
 for k in range(9):
  z=4.07+k*.09; rr=.28*math.sqrt(max(.1,1-((z-4.43)/.42)**2));torus('Lantern bamboo rib',(x,-.76,z),rr,.012,woodlight)
 for z in [4.03,4.83]:cyl('Lantern cap',(x,-.76,z),.13,.075,ink)
 text('Lantern glyph','8',(x,-1.016,4.45),.29,red)
# chef mantle
uv('Octopus mantle',(0,.27,3.64),(.86,.69,.92),coral)
uv('Lower mantle',(0,.20,3.02),(.72,.57,.45),coral)
# spots scattered on upper temples
for side in [-1,1]:
 for i in range(7):
  x=side*(.57+.13*sin(i*1.4)); z=3.65+i*.07; y=.27-.68*math.sqrt(max(.05,1-(x/.87)**2-((z-3.64)/.93)**2))-.012
  uv('Mantle dapple',(x,y,z),(.045,.018,.055),coralLight)
for x in [-.32,.32]:
 uv('Eye ivory',(x,-.365,3.69),(.235,.105,.27),white)
 uv('Eye dark',(x+.018,-.462,3.69),(.118,.055,.155),ink)
 uv('Eye sparkle',(x-.016,-.509,3.753),(.037,.014,.047),white)
 line('Happy brow',[(x-.14,-.39,4.00),(x,-.43,4.055),(x+.13,-.39,4.015)],.031,ink)
uv('Little smiling mouth',(0,-.43,3.32),(.13,.055,.105),ink)
uv('Tongue',(0,-.483,3.286),(.075,.014,.032),pink)
for x in [-.57,.57]:uv('Rosy cheek',(x,-.292,3.39),(.14,.035,.07),pink)
# apron, neckerchief
uv('Apron bib',(0,-.303,2.98),(.47,.12,.39),white)
line('Apron neck cord',[(-.46,-.27,3.25),(0,-.39,3.08),(.46,-.27,3.25)],.035,cream)
uv('Neckerchief knot',(0,-.455,3.12),(.10,.07,.10),red)
for x in [-.09,.09]:
 o=uv('Neckerchief tails',(x,-.43,2.98),(.07,.04,.19),red);o.rotation_euler[1]=x*3
text('Apron logo','8',(0,-.432,2.82),.18,teal)
# chef toque
cyl('Toque band',(0,.25,4.38),.57,.24,white)
torus('Toque band piping',(0,.25,4.28),.56,.028,cream)
for x,y,z,s in [(-.39,.24,4.65,.32),(.37,.24,4.67,.33),(0,.06,4.77,.38),(0,.47,4.74,.34)]:uv('Puffy chef toque',(x,y,z),(s,s*.88,s*.95),white)
# 8 sculpted arms with tapered tube mesh
arms=[
 [(-.52,.18,3.05),(-1.0,-.1,2.90),(-1.39,-.67,2.62),(-1.86,-1.0,2.55),(-2.1,-1.02,2.76),(-1.95,-.97,2.91)],
 [(-.3,-.03,2.95),(-.57,-.61,2.73),(-.84,-1.23,2.59),(-1.14,-1.38,2.46),(-1.44,-1.35,2.56),(-1.40,-1.28,2.73)],
 [(.18,-.03,2.94),(.52,-.70,2.62),(.90,-1.22,2.5),(1.42,-1.27,2.53),(1.62,-1.14,2.73),(1.48,-1.03,2.84)],
 [(.55,.2,3.02),(1.08,-.05,2.95),(1.60,-.30,3.20),(1.79,-.45,3.66),(1.58,-.53,3.86),(1.40,-.54,3.76)],
 [(-.64,.40,3.12),(-1.18,.34,3.34),(-1.55,.01,3.62),(-1.88,-.13,3.65),(-2.04,-.16,3.46),(-1.9,-.20,3.35)],
 [(.65,.44,3.12),(1.29,.65,3.16),(2.03,.55,3.0),(2.65,.05,2.94),(2.96,-.13,3.29),(2.90,-.19,3.60),(2.70,-.19,3.64)],
 [(-.51,.65,3.04),(-1.08,.91,2.85),(-1.85,.88,2.89),(-2.55,.65,3.01),(-2.94,.38,3.4),(-2.94,.19,3.77),(-2.74,.12,3.83)],
 [(.37,.69,3.0),(.76,1.01,2.8),(1.48,1.04,2.77),(2.03,.87,2.6),(2.46,.40,2.52),(2.69,.03,2.63),(2.58,-.09,2.80)]
]
def catmull(points,n=9):
 p=[Vector(points[0])]+[Vector(a) for a in points]+[Vector(points[-1])];out=[]
 for i in range(1,len(p)-2):
  a,b,c,d=p[i-1:i+3]
  for j in range(n):
   t=j/n;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 out.append(Vector(points[-1]));return out
for ai,pts in enumerate(arms):
 path=catmull(pts);vs=[];fs=[];rs=[]
 for i,p in enumerate(path):
  t=i/(len(path)-1);r=.245*(1-t)**.72+.022;rs.append(r);tang=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized(); v=tang.cross(Vector((0,1,0))).normalized();w=tang.cross(v).normalized()
  for j in range(12):vs.append(p+r*(v*cos(j*2*pi/12)+w*sin(j*2*pi/12)))
 for i in range(len(path)-1):
  for j in range(12):a=i*12+j;b=i*12+(j+1)%12;fs.append((a,b,b+12,a+12))
 fs.append(tuple(range(11,-1,-1)));fs.append(tuple((len(path)-1)*12+j for j in range(12)))
 me=bpy.data.meshes.new('Tapered arm mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Arm %d / sculpted curl'%(ai+1),me);bpy.context.collection.objects.link(o);finish(o,o.name,coral,True)
 for i in range(7,len(path)-2,4):
  p=path[i];r=rs[i];tang=(path[i+1]-path[i-1]).normalized();normal=Vector((0,-1,-.28));normal=(normal-tang*normal.dot(tang)).normalized();pos=p+normal*r*.94
  torus('Arm %d suction lip'%(ai+1),pos,r*.39,r*.115,suck,normal)
  o=uv('Suction cup inset',pos-normal*.008,(r*.30,r*.30,.017),cupdark);o.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
# lathed hollow bowls

def lathe(name,loc,profile,ma):
 vs=[];fs=[];n=64
 for r,z in profile:
  for j in range(n):vs.append((loc[0]+r*cos(j*2*pi/n),loc[1]+r*sin(j*2*pi/n),loc[2]+z))
 for i in range(len(profile)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;fs.append((a,b,b+n,a+n))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,ma,True);return o

def ramen(x,y,z,s=1):
 profile=[(0,0),(.24,0),(.26,.06),(.34,.11),(.48,.25),(.57,.47),(.57,.50),(.53,.50),(.51,.45),(.43,.25),(.27,.12),(0,.12)]
 lathe('Ramen bowl • ceramic',(x,y,z),[(r*s,h*s) for r,h in profile],cream)
 torus('Bowl vermilion rim',(x,y,z+.48*s),.55*s,.026*s,red)
 torus('Bowl foot',(x,y,z+.045*s),.24*s,.023*s,teal)
 for a in range(0,360,30):
  t=math.radians(a);o=uv('Bowl indigo dash',(x+.475*s*cos(t),y+.475*s*sin(t),z+.28*s),(.022*s,.022*s,.055*s),teal)
 cyl('Rich miso surface',(x,y,z+.406*s),.505*s,.024*s,broth)
 for i in range(10):
  pts=[]
  for k in range(9):
   t=k*pi/4; r=(.24+.027*i)*s;pts.append((x+r*cos(t),y+r*.60*sin(t),z+(.43+.012*sin(k*1.7+i))*s))
  line('Coiled ramen noodles',pts,.018*s,noodle)
 # pork slices
 for off in [-.17,.10]:
  uv('Chashu slice',(x+off*s,y+.20*s,z+.46*s),(.21*s,.14*s,.045*s),pork)
  line('Chashu fat swirl',[(x+off*s+.14*s*cos(t),y+.20*s+.08*s*sin(t),z+.502*s) for t in [j*5*pi/16 for j in range(17)]],.014*s,cream)
 # egg lying visible top
 o=uv('Egg half',(x-.22*s,y-.15*s,z+.48*s),(.18*s,.23*s,.075*s),white)
 uv('Golden soft yolk',(x-.22*s,y-.17*s,z+.546*s),(.11*s,.13*s,.026*s),yolk)
 # nori back angled rectangular
 o=cube('Nori sheet',(x+.29*s,y+.20*s,z+.65*s),(.22*s,.045*s,.39*s),darkteal,.018);o.rotation_euler[1]=-.22
 for j in range(4):line('Nori embossed streak',[(x+(.21+j*.05)*s,y+.172*s,z+.49*s),(x+(.13+j*.05)*s,y+.172*s,z+.80*s)],.005*s,green)
 # naruto disc and spiral
 uv('Fish cake',(x+.24*s,y-.18*s,z+.47*s),(.15*s,.13*s,.025*s),white)
 pts=[]
 for j in range(35):
  a=j*.35;r=.004+j*.0025;pts.append((x+(.24+r*cos(a))*s,y+(-.18+r*sin(a))*s,z+.5*s))
 line('Narutomaki spiral',pts,.011*s,pink)
 for i in range(11):
  xx=x+random.uniform(-.1,.3)*s;yy=y+random.uniform(-.05,.14)*s
  torus('Fresh scallion', (xx,yy,z+.48*s),.032*s,.011*s,green)
ramen(.35,-.86,2.43,1.12)
ramen(-1.82,-.59,2.43,.78)
# chopsticks suspended from arm and strands rising
for dx in [-.07,.07]:rod('Chef chopsticks',(1.62+dx,-.55,3.81),(.60+dx,-.77,3.30),.023,wooddark)
for i in range(6):
 x=.58+i*.028
 line('Lifted noodle strand',[(x,-.77,3.34),(x-.06,-.79,3.16),(x+.015,-.80,2.98),(x-.10,-.79,2.95)],.013,noodle)
# ladle arm left
rod('Ladle wooden grip',(-1.89,-.12,3.57),(-1.62,.28,2.98),.035,wooddark)
rod('Ladle metal stem',(-1.62,.28,2.98),(-1.50,.44,2.77),.022,steel)
uv('Ladle cup',(-1.50,.44,2.76),(.14,.14,.075),steel)
# pot back left
lathe('Stockpot',(-1.55,.67,2.43),[(0,0),(.43,0),(.44,.08),(.44,.46),(.41,.48),(.39,.45),(.39,.1),(0,.1)],steel)
torus('Pot rolled rim',(-1.55,.67,2.9),.43,.025,steel)
cyl('Pot broth',(-1.55,.67,2.82),.39,.025,broth)
for x in [-2.06,-1.04]:torus('Pot loop handle',(x,.67,2.72),.11,.025,steel,(0,1,0))
# graphic steam curls (solid ivory stylized)
for x,z in [(-1.64,2.92),(-1.43,2.94)]:line('Aromatic steam',[(x,.66,z),(x-.08,.66,z+.18),(x+.035,.66,z+.35),(x-.03,.66,z+.51)],.013,steam)
# accessories right
cyl('Chopstick crock',(2.18,-.55,2.61),.16,.36,teal)
torus('Crock rim',(2.18,-.55,2.8),.15,.018,gold)
for i in range(7):
 a=i*2*pi/7;rod('Spare chopstick',(2.18+.08*cos(a),-.55+.08*sin(a),2.65),(2.18+.14*cos(a),-.55+.14*sin(a),3.11+random.uniform(-.06,.05)),.013,wooddark)
for x,ma in [(1.92,red),(2.48,ink)]:
 cyl('Condiment bottle',(x,.17,2.61),.10,.35,ma);cyl('Bottle cap',(x,.17,2.82),.065,.09,gold)
 cube('Condiment label',(x,.066,2.61),(.12,.014,.15),cream,.005)
# stack of dishes right rear
for i in range(3):
 cyl('Stacked side plates',(1.47,.75,2.45+i*.065),.29,.05,cream)
 torus('Plate rim',(1.47,.75,2.48+i*.065),.27,.014,teal)
# front graphic medallion
cyl_o=cyl('Cabinet round crest',(0,-.733,1.42),.50,.07,cream);cyl_o.rotation_euler=(pi/2,0,0)
text('Cabinet 8','8',(0,-.785,1.46),.67,red)
text('Cabinet wordmark','HAND-PULLED',(0,-.79,.98),.105,cream)
# menu sign hung front left
for x in [-2.0,-1.3]:rod('Menu hanger',(x,-.81,2.2),(x,-.83,1.96),.012,gold)
cube('Menu wood frame',(-1.65,-.84,1.46),(1.15,.09,1.1),wooddark,.06)
cube('Menu board',(-1.65,-.897,1.46),(1.04,.025,.98),ink,.025)
text('Menu title','TODAY',(-1.65,-.916,1.79),.16,cream)
text('Menu rule','––––––––',(-1.65,-.916,1.65),.12,gold)
text('Menu item one','MISO     12',(-1.65,-.916,1.48),.123,cream)
text('Menu item two','SHOYU  12',(-1.65,-.916,1.28),.123,cream)
text('Menu footer','MADE WITH LOVE',(-1.65,-.916,1.08),.075,suck)
text('Counter right slogan','SLURP!',(1.62,-.729,1.47),.30,cream)
text('Right footer','HOT  •  FRESH  •  HAPPY',(1.62,-.731,1.17),.09,cream)
# two small customer stools in foreground
for x in [-2.25,2.25]:
 for dx in [-.21,.21]:
  for dy in [-.2,.2]:rod('Stool splayed leg',(x+dx*1.24,-1.81+dy*1.24,.51),(x+dx,-1.81+dy,1.12),.045,wooddark)
 torus('Stool brass footrest',(x,-1.81,.72),.29,.023,gold)
 cyl('Round stool wood',(x,-1.81,1.15),.40,.13,woodlight)
 cyl('Round teal seat',(x,-1.81,1.24),.38,.09,teal)
 torus('Seat piping',(x,-1.81,1.27),.36,.015,gold)
# little pavement plaque
cube('Welcome plaque',(0,-1.98,.525),(1.6,.36,.04),cream,.035)
# flat top text
ob=text('Welcome mat','OPEN / 08–23',(0,-1.98,.55),.15,ink);ob.rotation_euler=(0,0,0)
# scene setup
world=bpy.data.worlds.new('Soft midnight studio') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.24,.29,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
# ground is for render only, excluded from export
stage=cube('Studio floor',(0,0,-.13),(200,200,.20),floor,.02)
def area(name,loc,energy,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,2.5))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key softbox',(-4,-6,10),1100,(1,.81,.62),7)
area('Cool fill',(5,-2,7),900,(.65,.84,1),6)
area('Warm rim',(1,5,9),1400,(1,.57,.30),5)
bpy.ops.object.camera_add(location=(8.3,-13,8.2));cam=bpy.context.object;cam.name='Hero camera';cam.rotation_euler=(Vector((0,-.05,2.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=9.6;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
sc.world.color=(.15,.15,.15);sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(OUT,'octo-ramen-hero.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.getcwd(),'scene.blend'))
result={'objects':len(bpy.data.objects),'ready':True}
