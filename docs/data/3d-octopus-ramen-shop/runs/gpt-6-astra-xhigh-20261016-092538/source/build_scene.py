import bpy, math, random, os
from mathutils import Vector
from math import sin, cos, pi
random.seed(18)
OUT=os.path.join(os.getcwd(),'output'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
# Palette
M={}
def mat(name, color, rough=.45, metal=0, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    M[name]=m; return m
mat('Coral',(.87,.205,.135),.36); mat('Coral light',(1,.36,.24),.42); mat('Blush',(.95,.135,.135)); mat('Sucker rim',(1,.65,.46),.4); mat('Sucker well',(.69,.23,.16),.55)
mat('Ink',(.018,.065,.078),.38); mat('Deep teal',(.025,.155,.17)); mat('Teal',(.035,.265,.27)); mat('Teal light',(.065,.34,.32)); mat('Ivory',(.98,.88,.67)); mat('Porcelain',(1,.96,.85),.25)
mat('Wood',(.55,.255,.105)); mat('Wood light',(.74,.4,.18)); mat('Wood golden',(.85,.53,.26)); mat('Wood dark',(.25,.105,.052)); mat('Brass',(.72,.43,.14),.3,.65)
mat('Red',(.72,.075,.045),.35); mat('Lantern',(1,.29,.095),.48,0,.25); mat('Lantern rib',(.7,.115,.035)); mat('Noodle',(.98,.73,.31),.5); mat('Broth',(.38,.13,.027),.22)
mat('Egg',(1,.9,.64),.36); mat('Yolk',(1,.46,.025),.35); mat('Pork',(.66,.245,.2)); mat('Fat',(.98,.65,.49)); mat('Nori',(.025,.085,.038),.65); mat('Scallion',(.3,.64,.18)); mat('Green',(.085,.31,.1)); mat('Steam',(.94,.9,.74),.8)
mat('Metal',(.24,.34,.34),.28,.72); mat('Black',(.008,.015,.018),.23); mat('Backdrop',(.68,.75,.71),.85); mat('Stone',(.78,.73,.61),.8)
COL=None
def collection(name):
    global COL
    COL=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(COL)
def link(o):
    if COL:
        for c in list(o.users_collection): c.objects.unlink(o)
        COL.objects.link(o)
    return o
def finish(o,name,ma=None,smooth=False):
    o.name=name; link(o)
    if ma: o.data.materials.append(M[ma] if isinstance(ma,str) else ma)
    if smooth and o.type=='MESH':
        for p in o.data.polygons: p.use_smooth=True
    return o
def bevel(o,amount=.06,seg=3):
    m=o.modifiers.new('Soft crafted edges','BEVEL'); m.width=amount; m.segments=seg
    m=o.modifiers.new('Corner normals','WEIGHTED_NORMAL'); m.keep_sharp=True
    return o
def cube(n,loc,scale,ma,b=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); finish(o,n,ma)
    if b: bevel(o,b)
    return o
def uv(n,loc,scale,ma,seg=32,rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc); o=bpy.context.object; o.scale=scale; return finish(o,n,ma,True)
def cyl(n,loc,r,depth,ma,vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=finish(bpy.context.object,n,ma,True); bevel(o,min(.025,depth*.16),2); return o
def between(n,a,b,r,ma,vertices=20):
    a,b=Vector(a),Vector(b); o=cyl(n,(a+b)/2,r,(b-a).length,ma,vertices); o.rotation_mode='QUATERNION'; o.rotation_quaternion=(b-a).to_track_quat('Z','Y'); return o
def torus(n,loc,major,minor,ma,normal=None,seg=40):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=seg,minor_segments=8,location=loc)
    o=finish(bpy.context.object,n,ma,True)
    if normal is not None: o.rotation_mode='QUATERNION'; o.rotation_quaternion=Vector(normal).to_track_quat('Z','Y')
    return o
def curve(n,pts,r,ma):
    cu=bpy.data.curves.new(n,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12; cu.bevel_depth=r; cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,cu); COL.objects.link(o); cu.materials.append(M[ma]); return o
def mesh(n,verts,faces,ma,smooth=True):
    me=bpy.data.meshes.new(n); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(n,me); COL.objects.link(o); o.data.materials.append(M[ma])
    if smooth:
        for p in me.polygons: p.use_smooth=True
    return o
def lathe(n,loc,profile,ma,steps=64):
    vs=[]; fs=[]
    for r,z in profile:
        for j in range(steps):
            a=2*pi*j/steps; vs.append((loc[0]+r*cos(a),loc[1]+r*sin(a),loc[2]+z))
    for i in range(len(profile)-1):
        for j in range(steps): a=i*steps+j; b=i*steps+(j+1)%steps; fs.append((a,b,b+steps,a+steps))
    return mesh(n,vs,fs,ma)
font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf')
font2=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf')
def text(n,body,loc,size,ma,fontuse=font,extr=.004):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=body; cu.size=size; cu.font=fontuse; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=extr; cu.bevel_depth=.002; cu.bevel_resolution=1
    o=bpy.data.objects.new(n,cu); COL.objects.link(o); o.location=loc; o.rotation_euler=(pi/2,0,0); cu.materials.append(M[ma]); return o

collection('01 | Floating street corner')
cube('Rounded midnight plinth',(0,0,.16),(7.65,5.85,.32),'Deep teal',.2)
cube('Golden reveal',(0,0,.315),(7.47,5.67,.07),'Brass',.1)
cube('Warm terrazzo pavement',(0,0,.4),(7.4,5.6,.15),'Stone',.14)
# Subtle pavement divisions and inset front tiles
for x in [-2.8,-1.4,0,1.4,2.8]:
    cube('Paving joint',(x,-2.04,.482),(.018,1.45,.008),'Ivory',.002)
for x in range(7):
    cube('Front border tile',(-3.12+x*1.04,-2.56,.494),(.98,.36,.022),'Ivory',.035)
# elevated wood floor behind bar
cube('Booth floor',(0,.85,.57),(6.05,2.8,.2),'Wood dark',.08)
for i in range(14): cube('Floorboards',(-2.8+i*.43,.85,.69),(.405,2.66,.05),'Wood light',.014)

collection('02 | Joinery & service bar')
for x in [-3,3]:
    for y in [-.15,1.98]:
        cube('Cedar upright',(x,y,3.02),(.16,.18,4.76),'Wood dark',.025)
        cube('Brass post shoe',(x,y,.89),(.21,.23,.4),'Brass',.025)
        cube('Post highlight',(x-.012,y-.101,3.13),(.055,.015,3.83),'Wood light',.008)
# lower back wall
cube('Back rail',(0,1.98,1.79),(6.0,.16,2.18),'Wood',.04)
for i in range(20): cube('Back timber slat',(-2.84+i*.3,1.865,1.74),(.265,.065,1.95),'Wood light' if i%3 else 'Wood golden',.018)
cube('Rear shelf',(0,1.7,2.84),(5.92,.55,.13),'Wood dark',.04)
# counter body
cube('Counter carcass',(0,-.82,1.2),(5.95,1.0,1.1),'Wood dark',.07)
for i in range(18): cube('Counter cedar flutes',(-2.79+i*.328,-1.344,1.23),(.298,.06,.98),'Wood light' if i%4 else 'Wood golden',.015)
cube('Front top rail',(0,-1.39,1.76),(6.07,.10,.12),'Wood golden',.025)
cube('Front bottom rail',(0,-1.38,.75),(6.07,.11,.12),'Wood golden',.025)
cube('Bar dark underlip',(0,-.82,1.94),(6.38,1.44,.16),'Deep teal',.08)
cube('Serving counter',(0,-.82,2.035),(6.42,1.48,.11),'Wood golden',.055)
for y in [-1.14,-.7,-.26]: cube('Counter plank seam',(0,y,2.092),(6.22,.012,.004),'Wood',.002)
# small inset sign on counter
cube('Counter badge',(0,-1.401,1.26),(1.33,.06,.68),'Deep teal',.12)
text('Counter name','TAKO',(0,-1.443,1.35),.28,'Ivory')
text('Counter number','EST. 08',(0,-1.443,1.1),.115,'Wood golden',font2)
# brass foot rail front
between('Foot rail',(-2.87,-1.67,.81),(2.87,-1.67,.81),.037,'Brass')
for x in [-2.6,0,2.6]: between('Foot rail bracket',(x,-1.35,.81),(x,-1.67,.81),.026,'Brass')
# corner braces
for x in [-3,3]:
    between('Eave brace',(x,-.15,4.72),(x,-.65,5.43),.055,'Wood light')

collection('03 | Scalloped teal roof & house sign')
# back noren, deliberately behind the chef
between('Noren pole',(-2.88,1.68,5.0),(2.88,1.68,5.0),.035,'Brass')
for i in range(5):
    x=-2.25+i*1.125
    cube('Noren fabric',(x,1.7,4.6),(1.07,.045,.78),'Ivory',.035)
    cube('Noren hem',(x,1.668,4.24),(1.02,.012,.035),'Teal',.005)
    for j in [-1,0,1]:
        curve('Printed wave',[(x-.42,1.663,4.43+j*.09),(x-.21,1.663,4.49+j*.09),(x,1.663,4.43+j*.09),(x+.21,1.663,4.49+j*.09),(x+.42,1.663,4.43+j*.09)],.009,'Teal')
# Roof slats curved across depth
profile=[(-.95,5.63),(-.73,5.62),(-.35,5.69),(.15,5.89),(.73,6.12),(1.27,6.0),(1.84,5.77),(2.3,5.66),(2.58,5.72)]
for i in range(26):
    x=-3.48+i*.268; vs=[]; fs=[]
    for xx in [x,x+.254]:
        for y,z in profile: vs.append((xx,y,z+.17*(abs(xx)/3.5)**8))
    for j in range(len(profile)-1): fs.append((j,j+1,j+1+len(profile),j+len(profile)))
    o=mesh('Glazed curved roof tile',vs,fs,['Deep teal','Teal','Teal','Teal light'][i%4]); sol=o.modifiers.new('Tile thickness','SOLIDIFY'); sol.thickness=.07; bevel(o,.025,2)
for x in [-3.52,3.52]: curve('Gold swept verge',[(x,y,z+.17) for y,z in profile],.047,'Brass')
curve('Ridge cap',[(-3.55,.73,6.29),(-2.5,.73,6.16),(0,.73,6.16),(2.5,.73,6.16),(3.55,.73,6.29)],.09,'Deep teal')
curve('Front eave lip',[(-3.53,-.96,5.81),(-2.75,-.96,5.66),(0,-.96,5.64),(2.75,-.96,5.66),(3.53,-.96,5.81)],.055,'Brass')
cube('Sign dark frame',(0,-.73,5.36),(5.63,.21,.69),'Wood dark',.1)
cube('Cream enamel sign',(0,-.857,5.36),(5.42,.055,.52),'Ivory',.075)
text('House wordmark','TAKO RAMEN',(.12,-.903,5.37),.47,'Deep teal')
# Decorative four-square sign nails
for x in [-2.56,2.56]:
    for z in [5.19,5.54]: uv('Sign rivet',(x,-.904,z),(.027,.014,.027),'Brass',16,8)
# Lanterns
for x in [-2.73,2.73]:
    between('Lantern suspension',(x,-.55,5.12),(x,-.55,4.94),.025,'Black')
    lp=[(.18,-.43),(.29,-.37),(.36,-.23),(.38,0),(.36,.23),(.29,.37),(.18,.43)]
    lathe('Papery lantern',(x,-.55,4.48),lp,'Lantern',48)
    for z in [-.44,.44]: cyl('Lantern cap',(x,-.55,4.48+z),.2,.07,'Ink')
    for z in [-.32,-.21,-.1,.01,.12,.23,.33]:
        r=.38*math.sqrt(max(.1,1-(z/.55)**2))
        torus('Horizontal bamboo rib',(x,-.55,4.48+z),r,.009,'Lantern rib',seg=32)
    for a in [0,pi/2,pi,3*pi/2]:
        curve('Lantern meridian',[(x+r*cos(a),-.55+r*sin(a),4.48+z) for r,z in lp],.008,'Lantern rib')
    text('Lantern mark','08',(x,-.934,4.49),.27,'Ivory')
    between('Lantern tassel',(x,-.55,4.01),(x,-.55,3.88),.018,'Brass')

collection('04 | Chef Tako')
# eight muscular tapering arms, with raised double rows of suction cups
def cat(a,b,c,d,t): return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
def sample(points,radii,sub=9):
    ps=[Vector(p) for p in points]; ss=[]; rr=[]
    for i in range(len(ps)-1):
        for j in range(sub):
            t=j/sub; ss.append(cat(ps[max(0,i-1)],ps[i],ps[i+1],ps[min(len(ps)-1,i+2)],t)); rr.append(max(.022,cat(radii[max(0,i-1)],radii[i],radii[i+1],radii[min(len(ps)-1,i+2)],t)))
    ss.append(ps[-1]); rr.append(radii[-1]); return ss,rr
def cup(n,p,normal,r):
    normal=normal.normalized(); u=normal.cross(Vector((0,0,1)))
    if u.length<.01: u=normal.cross(Vector((0,1,0)))
    u.normalize(); v=normal.cross(u); vs=[]; fs=[]
    prof=[(.79,0),(1,.018),(1,.045),(.72,.064),(.47,.036),(.22,.025)]
    for ra,z in prof:
        for k in range(12):
            a=2*pi*k/12; vs.append(p+r*ra*(cos(a)*u+sin(a)*v)+normal*z*(r/.085))
    for k in range(len(prof)-1):
        for j in range(12): fs.append((k*12+j,k*12+(j+1)%12,(k+1)*12+(j+1)%12,(k+1)*12+j))
    fs.append(tuple(range((len(prof)-1)*12,len(prof)*12)))
    o=mesh(n,vs,fs,'Sucker rim'); o.data.materials.append(M['Sucker well'])
    for poly in o.data.polygons:
        if poly.index>=48: poly.material_index=1

def arm(n,points,radii):
    ps,rs=sample(points,radii); vs=[]; fs=[]; frames=[]; nr=14
    for i,(p,r) in enumerate(zip(ps,rs)):
        t=ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]; t.normalize(); front=Vector((0,-1,-.16)); u=(front-t*front.dot(t)).normalized(); v=t.cross(u).normalized(); frames.append((u,v))
        for j in range(nr):
            a=2*pi*j/nr; vs.append(p+r*(cos(a)*u+sin(a)*v))
    for i in range(len(ps)-1):
        for j in range(nr): fs.append((i*nr+j,i*nr+(j+1)%nr,(i+1)*nr+(j+1)%nr,(i+1)*nr+j))
    fs.append(tuple(reversed(range(nr)))); fs.append(tuple(range((len(ps)-1)*nr,len(ps)*nr)))
    o=mesh(n,vs,fs,'Coral'); o.data.materials.append(M['Coral light'])
    for f in o.data.polygons:
        if f.index%nr in [0,1,12,13]: f.material_index=1
    for i in range(5,len(ps)-3,3):
        r=rs[i]; u,v=frames[i]
        for a in [-.46,.46]:
            normal=(u*cos(a)+v*sin(a)).normalized(); cup(n+' / suction cup',ps[i]+normal*r*.97,normal,min(.095,r*.35))
arm('01 • stirring arm',[(-.42,.16,2.95),(-1.03,.1,2.72),(-1.58,.03,2.93),(-1.94,-.06,3.4),(-2.17,-.1,3.55),(-2.32,-.2,3.34)],[.31,.27,.22,.16,.11,.035])
arm('02 • left greeting curl',[(-.55,.05,2.83),(-1.15,-.4,2.64),(-1.61,-.95,2.42),(-2.05,-1.52,2.43),(-2.39,-1.54,2.67),(-2.38,-1.5,2.92),(-2.19,-1.49,2.92)],[.29,.26,.22,.18,.13,.08,.025])
arm('03 • left counter drape',[(-.31,-.05,2.78),(-.7,-.62,2.57),(-.93,-1.28,2.28),(-1.08,-1.59,1.82),(-1.48,-1.65,1.62),(-1.78,-1.65,1.85),(-1.62,-1.64,2.01)],[.29,.26,.22,.17,.12,.075,.023])
arm('04 • noodle lifting arm',[(.47,.18,2.92),(1.08,.12,2.84),(1.47,-.03,3.23),(1.61,-.22,3.71),(1.86,-.34,3.94),(2.11,-.44,3.82),(1.99,-.49,3.65)],[.31,.26,.22,.17,.12,.08,.025])
arm('05 • right serving arm',[(.48,.04,2.83),(1.04,-.4,2.58),(1.79,-.66,2.43),(2.35,-1.07,2.48),(2.65,-1.03,2.79),(2.49,-.97,2.97)],[.3,.265,.23,.175,.11,.025])
arm('06 • right counter drape',[(.24,-.06,2.78),(.57,-.72,2.5),(.35,-1.3,2.27),(.36,-1.65,1.84),(.72,-1.68,1.65),(.98,-1.66,1.88),(.83,-1.64,2.02)],[.28,.25,.22,.17,.12,.07,.025])
arm('07 • back herb arm',[(-.43,.54,2.89),(-1.05,.85,2.6),(-1.6,1.15,2.79),(-1.89,.94,3.14),(-1.77,.76,3.3)],[.29,.25,.19,.12,.028])
arm('08 • back curl',[(.46,.54,2.86),(1.07,.94,2.63),(1.74,1.02,2.57),(2.16,.67,2.79),(2.4,.37,3.15),(2.24,.22,3.34),(2.06,.18,3.21)],[.29,.25,.2,.165,.12,.07,.025])
# domed head taper, made from smooth spheres
uv('Chef mantle',(0,.22,3.49),(.91,.68,.92),'Coral',48,32)
uv('Lower mantle',(0,.18,2.97),(.67,.54,.53),'Coral',40,24)
# darker freckles over upper forehead and sides
for x,y,z,s in [(-.59,-.24,3.95,.047),(-.45,-.35,4.1,.035),(-.7,-.15,3.83,.03),(.62,-.2,3.99,.043),(.75,-.08,3.86,.028),(.52,-.31,4.1,.027)]: uv('Mantle freckle',(x,y,z),(s,.018,s),'Coral light',16,10)
# expressive eyes attached to the forward surface
for x in [-.335,.335]:
    uv('Ivory eye',(x,-.406,3.59),(.24,.123,.29),'Porcelain')
    uv('Eye pupil',(x+.026,-.522,3.57),(.116,.06,.155),'Black')
    uv('Eye glint',(x-.011,-.576,3.635),(.038,.017,.049),'Porcelain',20,12)
    uv('Tiny eye glint',(x+.06,-.577,3.53),(.016,.008,.02),'Porcelain',16,8)
    curve('Friendly eyebrow',[(x-.14,-.427,3.91),(x-.03,-.469,3.96),(x+.10,-.432,3.93)],.032,'Wood dark')
    uv('Rosy cheek',(x*1.67,-.348,3.33),(.145,.033,.08),'Blush')
uv('Happy smile',(0,-.472,3.24),(.136,.049,.108),'Wood dark')
uv('Smile tongue',(0,-.515,3.205),(.08,.013,.035),'Coral light',24,12)
# bib curves closely over lower body
vs=[]; fs=[]
for iz in range(9):
    z=2.73+iz*.065; w=.33+(.03 if iz<5 else -.035)*(1 if iz<5 else iz-4)
    for ix in range(11):
        x=w*(ix/5-1); y=.15-.55*math.sqrt(max(.05,1-(x/.75)**2-((z-2.98)/.7)**2))-.02; vs.append((x,y,z))
for iz in range(8):
    for ix in range(10): a=iz*11+ix; fs.append((a,a+1,a+12,a+11))
o=mesh('Ivory apron bib',vs,fs,'Ivory'); so=o.modifiers.new('Cotton thickness','SOLIDIFY'); so.thickness=.025; bevel(o,.015,2)
for x in [-.28,.28]: curve('Apron shoulder strap',[(x,-.375,3.18),(x*1.5,-.31,3.31),(x*1.9,.05,3.31)],.035,'Ivory')
uv('Apron red seal',(0,-.442,2.99),(.12,.019,.12),'Red',24,16)
text('Apron eight','8',(0,-.465,2.99),.17,'Ivory')
# chef toque band and five puffy lobes
cyl('Toque lower band',(0,.22,4.235),.65,.26,'Porcelain',48)
torus('Toque piping',(0,.22,4.13),.64,.025,'Ivory')
for i in range(13):
    a=2*pi*i/13; curve('Toque pleat',[(.648*cos(a),.22+.648*sin(a),4.15),(.65*cos(a),.22+.65*sin(a),4.3)],.008,'Ivory')
uv('Toque crown',(0,.23,4.61),(.69,.52,.43),'Porcelain',40,24)
for x,y,z,s in [(-.46,.17,4.6,.32),(-.23,-.02,4.77,.35),(.14,-.04,4.8,.36),(.47,.18,4.65,.33),(.09,.48,4.77,.32)]: uv('Puffy chef hat',(x,y,z),(s,s*.87,s),'Porcelain',32,20)

collection('05 | Ramen mise en place')
def bowl(n,x,y,z,r=.58):
    lathe(n,(x,y,z),[(.17,0),(.21,.025),(.23,.065),(.35,.13),(.48,.25),(r,.4),(r+.014,.43),(r-.035,.447),(r-.065,.4),(.43,.27),(.3,.15),(.18,.1)],'Porcelain')
    torus(n+' indigo rim',(x,y,z+.423),r,.022,'Deep teal')
    torus(n+' foot',(x,y,z+.024),.2,.021,'Deep teal')
    cyl(n+' broth',(x,y,z+.363),r-.062,.025,'Broth',48)
    # blue dashes around outside
    for k in range(22):
        a=2*pi*k/22; p=(x+(r-.065)*cos(a),y+(r-.065)*sin(a),z+.316); q=(x+(r-.01)*cos(a+.015),y+(r-.01)*sin(a+.015),z+.391)
        between(n+' painted dash',p,q,.016,'Teal',10)
    return z+.39
z=bowl('House special',1.15,-1.15,2.105,.64)
# noodles nest on surface
for i in range(11):
    a=i*2*pi/11; rr=.12+(i%3)*.07
    pts=[]
    for j in range(13):
        t=j*pi/6; pts.append((1.06+rr*cos(t)+.055*cos(a),-1.18+rr*.7*sin(t)+.08*sin(a),z+.015+.009*sin(t*3+i)))
    curve('Tangled golden ramen',pts,.022,'Noodle')
# pork coins and marbling
for x,y,ang in [(1.43,-1.09,.35),(1.53,-1.3,-.1)]:
    o=uv('Chashu pork',(x,y,z+.035),(.2,.15,.045),'Pork'); o.rotation_euler[2]=ang
    for r in [.075,.125]:
        pts=[(x+r*cos(a)*1.1,y+r*sin(a)*.77,z+.075) for a in [k*2*pi/18 for k in range(19)]]; curve('Pork fat spiral',pts,.015,'Fat')
# egg half at front left
uv('Soft egg white',(.85,-1.36,z+.042),(.19,.145,.073),'Egg')
uv('Jammy golden yolk',(.855,-1.366,z+.108),(.095,.082,.02),'Yolk')
# nori as wavy sheet protruding at rear
vs=[]; fs=[]
for i in range(5):
    for j in range(6): vs.append((.73+i*.07,-.79+j*.018+.022*sin(i*2+j),z+j*.088))
for i in range(4):
    for j in range(5): a=i*6+j; fs.append((a,a+6,a+7,a+1))
o=mesh('Nori sail',vs,fs,'Nori'); so=o.modifiers.new('Seaweed thickness','SOLIDIFY'); so.thickness=.012
for i in range(18):
    x=1.08+random.uniform(-.2,.21); y=-1.13+random.uniform(-.18,.13)
    o=torus('Fresh scallion ring',(x,y,z+.045),random.uniform(.025,.039),.009,'Scallion',seg=12); o.rotation_euler=(random.uniform(-.4,.4),random.uniform(-.3,.3),0)
# lifted noodles draping from paired chopsticks
between('Bamboo chopstick A',(2.28,-.43,3.96),(.92,-.9,3.45),.025,'Wood golden')
between('Bamboo chopstick B',(2.31,-.48,3.9),(.99,-.99,3.43),.024,'Wood golden')
for i in range(6):
    x=.96+i*.045
    curve('Suspended noodle',[(x,-.93,3.46),(x-.04,-.98,3.29),(x+.015,-1.01,3.03),(x-.05,-1.03,2.77),(x+.03,-1.08,z+.06)],.018,'Noodle')
# little second bowl left with garnish
zz=bowl('Shoyu bowl',-1.28,-.91,2.105,.39)
for i in range(5):
    rr=.07+i*.03; curve('Shoyu noodles',[(-1.28+rr*cos(k*pi/6),-.91+rr*.65*sin(k*pi/6),zz) for k in range(13)],.016,'Noodle')
uv('Second egg',(-1.39,-1.03,zz+.02),(.1,.075,.025),'Egg'); uv('Second yolk',(-1.39,-1.03,zz+.045),(.052,.046,.012),'Yolk')
# burner and stock pot, behind left bar
cube('Portable enamel stove',(-2.07,.23,2.04),(1.06,.83,.22),'Deep teal',.08)
for x in [-2.35,-1.81]:
    o=cyl('Stove knob',(x,-.208,2.055),.074,.036,'Brass'); o.rotation_euler=(pi/2,0,0)
    cube('Knob index',(x,-.235,2.075),(.01,.012,.05),'Ink',.002)
torus('Burner ring',(-2.07,.23,2.2),.34,.048,'Black')
lathe('Stockpot',(-2.07,.23,2.22),[(.3,0),(.43,.055),(.46,.16),(.46,.51),(.48,.55),(.43,.56),(.418,.5),(.418,.1),(.3,.06)],'Metal')
torus('Pot rolled rim',(-2.07,.23,2.76),.46,.035,'Brass'); cyl('Stock liquid',(-2.07,.23,2.66),.416,.02,'Broth')
for x,sgn in [(-2.53,-1),(-1.61,1)]:
    curve('Pot loop handle',[(x,.15,2.64),(x+sgn*.21,.14,2.63),(x+sgn*.22,.39,2.63),(x,.4,2.64)],.044,'Ink')
between('Ladle handle',(-2.29,-.17,3.46),(-2.04,.19,2.74),.032,'Wood dark')
uv('Ladle scoop',(-2.04,.19,2.73),(.14,.14,.06),'Metal')
# graphic steam swirls
for dx in [-.16,.14]:
    curve('Stock steam',[(-2.07+dx,.23,2.8),(-2.15+dx,.25,3.01),(-2.03+dx,.26,3.19),(-2.11+dx,.28,3.39)],.016,'Steam')
# herbs in rear tentacle
for i in range(4):
    curve('Bunch of spring onions',[(-1.81,.75,3.21),(-1.85+i*.045,.74,3.48),(-1.98+i*.11,.73,3.75)],.022,'Scallion')
# serving paddle held on right arm
between('Serving paddle handle',(2.48,-.99,2.89),(2.68,-.82,3.08),.035,'Wood dark')
o=uv('Serving paddle',(2.72,-.68,3.12),(.26,.22,.035),'Wood golden')
for i in range(3):
    o=uv('Gyoza',(2.57+i*.14,-.68,3.18),(.09,.135,.055),'Egg',24,12)
    for j in range(4): curve('Gyoza crimp',[(2.52+i*.14+j*.025,-.76,3.2),(2.52+i*.14+j*.025,-.68,3.24),(2.52+i*.14+j*.025,-.6,3.2)],.008,'Noodle')
# condiment station right edge
cube('Condiment tray',(2.53,-.21,2.13),(.77,.53,.055),'Wood dark',.035)
for x,y,r,h,ma in [(2.33,-.22,.115,.33,'Red'),(2.62,-.1,.105,.26,'Ivory')]:
    cyl('Condiment crock',(x,y,2.16+h/2),r,h,ma)
    cyl('Condiment lid',(x,y,2.17+h),r*1.08,.035,'Ink')
    text('Condiment label','•',(x,y-r-.005,2.15+h*.52),.12,'Ivory')
cyl('Chopstick crock',(2.81,-.16,2.31),.105,.3,'Teal')
for i in range(6):
    x=2.81+random.uniform(-.06,.06); y=-.16+random.uniform(-.05,.05); between('Spare chopsticks',(x,y,2.22),(x+random.uniform(-.07,.07),y,2.82+random.uniform(-.06,.04)),.013,'Wood golden',12)
# rear storage jars
for x in [-2.45,-1.93,1.69,2.22]:
    cyl('Pantry jar',(x,1.7,3.08),.17,.37,'Ivory' if x<0 else 'Teal')
    cyl('Pantry jar lid',(x,1.7,3.29),.185,.065,'Wood dark')
    cube('Pantry label',(x,1.522,3.09),(.19,.012,.15),'Ivory' if x>0 else 'Red',.015)

collection('06 | Menu, stools & small details')
# right hanging chalk menu, tucked behind cooking action
cube('Menu frame',(2.08,1.63,3.94),(1.15,.12,1.05),'Wood golden',.045)
cube('Menu enamel',(2.08,1.556,3.94),(1.03,.03,.93),'Deep teal',.025)
text('Menu title','MENU',(2.08,1.526,4.24),.2,'Ivory',font2)
text('Menu item one','SHOYU   08',(2.08,1.524,4.02),.105,'Ivory',font2)
text('Menu item two','MISO      10',(2.08,1.524,3.84),.105,'Ivory',font2)
text('Menu item three','TEA        03',(2.08,1.524,3.66),.105,'Ivory',font2)
for x in [-2.32,2.22]:
    y=-2.18
    cyl('Round stool rim',(x,y,1.13),.43,.14,'Wood dark',40)
    cyl('Round stool cushion',(x,y,1.23),.405,.115,'Red',40)
    torus('Stool piping',(x,y,1.26),.387,.018,'Wood golden')
    for dx,dy in [(-.21,-.2),(.21,-.2),(-.21,.2),(.21,.2)]:
        between('Stool splayed leg',(x+dx*1.3,y+dy*1.3,.51),(x+dx,y+dy,1.1),.045,'Deep teal')
        cyl('Brass stool foot',(x+dx*1.3,y+dy*1.3,.55),.047,.09,'Brass',16)
    torus('Stool footrest',(x,y,.78),.285,.024,'Brass')
# little front welcome plaque on left upright
cube('Open plaque',(-3.11,-.3,3.4),(.5,.08,.52),'Ivory',.045)
text('Open','OPEN',(-3.11,-.347,3.46),.13,'Red',font2)
text('Hours','18 - 24',(-3.11,-.347,3.28),.08,'Deep teal',font2)
# enamel plaque inset into front of base
cube('Diorama title plaque',(0,-2.853,.22),(2.3,.045,.19),'Brass',.025)
text('Edition title','TAKO / THE NIGHT KITCHEN',(0,-2.881,.22),.105,'Ink',font2,.001)

collection('07 | Studio (not exported)')
cube('Studio floor',(0,0,-.14),(200,200,.15),'Backdrop',.02)
world=bpy.data.worlds.new('Soft sage studio'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.76,.73,1); world.node_tree.nodes['Background'].inputs[1].default_value=.6

def area(n,loc,energy,color,size,target=(0,0,2.5)):
    data=bpy.data.lights.new(n,'AREA'); data.energy=energy; data.color=color; data.shape='DISK'; data.size=size; ob=bpy.data.objects.new(n,data); COL.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('Large warm key',(-5,-7,11),1800,(1,.84,.68),7)
area('Cool fill',(6,-1,8),1200,(.67,.87,1),6)
area('Rim lantern glow',(-1,5,10),1800,(1,.67,.38),5)
area('Face softbox',(0,-6,5),280,(1,.8,.67),3)
for x in [-2.73,2.73]:
    d=bpy.data.lights.new('Lantern warmth','POINT'); d.energy=20; d.color=(1,.32,.08); d.shadow_soft_size=.5; ob=bpy.data.objects.new('Lantern warmth',d); COL.objects.link(ob); ob.location=(x,-.65,4.43)
camd=bpy.data.cameras.new('Presentation camera'); cam=bpy.data.objects.new('Presentation camera',camd); COL.objects.link(cam); cam.location=(9,-16,10); target=Vector((0,0,2.95)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='ORTHO'; camd.ortho_scale=10.2; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGB'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.render.image_settings.color_depth='8'
scene.render.filepath=os.path.join(OUT,'tako-ramen.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.getcwd(),'scene-working.blend'))
result={'objects':len(bpy.data.objects),'materials':len(bpy.data.materials)}
