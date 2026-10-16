import bpy, math, random, os
from mathutils import Vector
from math import sin, cos, pi
random.seed(12)
OUT=os.path.join(os.getcwd(),'output'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)

def mat(name,color,metal=0,rough=.45,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color[:3],color[3] if len(color)>3 else 1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=m.diffuse_color; p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emission: p.inputs['Emission Color'].default_value=(*color[:3],1); p.inputs['Emission Strength'].default_value=emission
    if m.diffuse_color[3]<1: m.surface_render_method='DITHERED'
    return m
M={}
for n,c in {'ink':(.023,.075,.09),'teal':(.035,.28,.29),'roof':(.025,.22,.24),'roofHi':(.065,.38,.38),'wood':(.52,.245,.09),'woodLight':(.76,.43,.18),'woodEdge':(.90,.61,.30),'cream':(.98,.88,.66),'white':(.98,.96,.87),'coral':(.86,.22,.17),'coralHi':(.98,.36,.26),'underside':(1,.51,.37),'cup':(1,.73,.54),'cupIn':(.68,.22,.18),'eye':(.018,.028,.038),'red':(.69,.065,.055),'gold':(.93,.57,.16),'noodle':(1,.75,.27),'broth':(.47,.19,.035),'green':(.16,.42,.11),'greenLight':(.48,.69,.16),'nori':(.027,.105,.07),'egg':(1,.96,.74),'yolk':(1,.48,.015),'pink':(.96,.44,.41),'fat':(1,.76,.59),'tile':(.68,.57,.42),'tile2':(.78,.67,.49),'chalk':(.77,.9,.77)}.items(): M[n]=mat(n,c)
M['steel']=mat('Brushed stainless steel',(.43,.56,.57),.75,.25)
M['brass']=mat('Honey brass',(.72,.44,.15),.7,.28)
M['lantern']=mat('Warm paper lantern',(1,.53,.22),0,.6,.32)
M['steam']=mat('Soft ivory steam',(.94,.91,.76,.34),0,1,.15)

def material(o,m): o.data.materials.append(M[m] if isinstance(m,str) else m); return o

def smooth(o):
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True
    return o

def cube(name,loc,scale,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); material(o,m)
    if bevel:
        mod=o.modifiers.new('Soft crafted edges','BEVEL'); mod.width=bevel; mod.segments=3
        mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def uv(name,loc,scale,m,segments=28,rings=18):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; material(o,m); smooth(o); return o

def cyl(name,loc,r,depth,m,vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object;o.name=name;material(o,m);smooth(o)
    b=o.modifiers.new('Rounded rim','BEVEL');b.width=min(.025,depth*.15);b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,m,20);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def torus(name,loc,major,minor,m,normal=(0,0,1),seg=32,minorseg=8):
    bpy.ops.mesh.primitive_torus_add(major_segments=seg,minor_segments=minorseg,location=loc,major_radius=major,minor_radius=minor);o=bpy.context.object;o.name=name;material(o,m);o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler();smooth(o);return o

def curve(name,pts,r,m,cyclic=False):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);material(o,m);return o

def lathe(name,profile,loc,m,steps=64):
    verts=[];faces=[]
    for r,z in profile:
        for j in range(steps):a=2*pi*j/steps;verts.append((loc[0]+r*cos(a),loc[1]+r*sin(a),loc[2]+z))
    for i in range(len(profile)-1):
        for j in range(steps):k=i*steps+j;nj=i*steps+(j+1)%steps;faces.append((k,nj,nj+steps,k+steps))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);material(o,m);smooth(o);return o
FONT=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf')
REG=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial.ttf')
def text(name,body,loc,size,m,maxwidth=None,font=FONT):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.0018;c.bevel_depth=.0007;c.font=font
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(pi/2,0,0);material(o,m)
    bpy.context.view_layer.update()
    if maxwidth and o.dimensions.x>maxwidth:o.scale*=maxwidth/o.dimensions.x
    return o

# Floating, rounded display base.
cube('Deep blue display plinth',(0,-.05,.0),(7.9,6.3,.34),'ink',.24)
cube('Brass reveal around plinth',(0,-.05,.15),(7.77,6.17,.085),'brass',.2)
cube('Sandstone platform',(0,-.05,.23),(7.66,6.06,.16),'tile',.18)
for i in range(10):
    for j in range(8):
        x=-3.38+i*.75;y=-2.67+j*.75
        cube('Individual paving stone',(x,y,.325),(.715,.715,.055),'tile2' if (i+j)%3 else 'tile',.025)
# main booth base and panelled facade
cube('Counter cabinet',(0,.0,1.12),(5.5,2.1,1.53),'wood',.065)
for x in [-2.62,-1.74,-.87,0,.87,1.74,2.62]:
    cube('Facade raised stile',(x,-1.077,1.13),(.065,.075,1.36),'woodEdge',.015)
for z in [.49,1.78]:cube('Facade horizontal frame',(0,-1.09,z),(5.5,.09,.10),'woodEdge',.015)
for i in range(19):cube('Front warm wood slat',(-2.48+i*.275,-1.06,1.12),(.245,.025,1.16),'woodLight',.012)
for side in [-1,1]:
    for j in range(6):cube('Side cabinet boards',(side*2.77,-.85+j*.34,1.1),(.035,.30,1.25),'woodLight',.014)
cube('Dark counter shadow edge',(0,-.45,1.91),(6.04,2.05,.15),'ink',.06)
for i in range(4):cube('Thick maple counter board',(0,-1.25+i*.49,2.015),(6.15,.475,.13),'woodEdge',.038)
# counter trim hardware
for x in [-2.8,2.8]:
    for z in [.6,1.7]:uv('Cabinet brass pin',(x,-1.113,z),(.026,.016,.026),'brass',16,10)
# Back posts and half wall
for x in [-2.72,2.72]:
    cube('Yatai tall cedar post',(x,.9,2.95),(.18,.2,5.24),'wood',.045)
    cube('Post gold foot',(x,.9,.53),(.23,.25,.32),'brass',.025)
    cube('Post collar',(x,.9,4.92),(.24,.25,.13),'woodEdge',.025)
cube('Back sea green panel',(0,1.01,1.85),(5.33,.14,2.83),'teal',.04)
for x in [-2.4,-1.8,-1.2,-.6,0,.6,1.2,1.8,2.4]:cube('Back wall slim batten',(x,.91,1.65),(.038,.035,2.2),'roofHi',.008)
cube('Back shelf',(0,.68,2.77),(5.25,.73,.12),'woodLight',.04)
cube('Rear horizontal top rail',(0,1.05,4.9),(5.6,.18,.18),'woodEdge',.025)
# low front emblem plaque
cube('Front brand plaque',(0,-1.13,1.14),(2.02,.13,.88),'ink',.14)
text('Front brand','OCTO RAMEN',(0,-1.207,1.28),.22,'cream',1.75)
text('Front tagline','EIGHT ARMS • ONE PERFECT BOWL',(0,-1.209,.98),.082,'gold',1.76)
for x in [-.9,.9]:uv('Plaque rivet',(x,-1.21,1.15),(.025,.013,.025),'brass',16,10)
# Foot rail
rod('Brass foot rail',(-2.7,-1.48,.63),(2.7,-1.48,.63),.045,'brass')
for x in [-2.45,2.45]:rod('Rail bracket',(x,-1.1,.52),(x,-1.48,.63),.035,'brass')
# roof with curved shingle ribs: ridge runs left-right
roof_profile=[(-1.36,5.47),(-1.18,5.46),(-.8,5.59),(-.35,5.87),(.15,6.1),(.55,6.19),(1.0,6.12),(1.5,5.88),(1.95,5.57),(2.15,5.52),(2.27,5.58)]
verts=[];faces=[]
for y,z in roof_profile:verts.extend([(-3.28,y,z),(3.28,y,z),(-3.28,y,z-.12),(3.28,y,z-.12)])
for i in range(len(roof_profile)-1):
    k=i*4;faces.extend([(k,k+1,k+5,k+4),(k+2,k+6,k+7,k+3),(k,k+4,k+6,k+2),(k+1,k+3,k+7,k+5)])
faces.extend([(0,2,3,1),(40,41,43,42)])
me=bpy.data.meshes.new('Curved roof surface');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Sweeping teal tiled canopy',me);bpy.context.collection.objects.link(ob);material(ob,'roof');smooth(ob)
for i in range(29):
    x=-3.25+i*6.5/28
    curve('Raised glazed tile seam',[(x,y,z+.018) for y,z in roof_profile],.035,'roofHi')
for j in [0,2,4,6,8,10]:
    y,z=roof_profile[j];rod('Horizontal roof tile joint',(-3.27,y,z+.02),(3.27,y,z+.02),.018,'teal')
for x in [-3.31,3.31]:curve('Carved golden roof end',[(x,y,z-.045) for y,z in roof_profile],.067,'woodEdge')
rod('Rounded ridge cap',(-3.38,.55,6.23),(3.38,.55,6.23),.09,'roofHi')
for x in [-3.4,3.4]:uv('Ridge finial',(x,.55,6.23),(.14,.13,.13),'brass')
# front sign
cube('Main sign maple surround',(0,-1.39,5.57),(4.36,.18,.72),'woodEdge',.12)
cube('Main sign enamel face',(0,-1.495,5.57),(4.18,.045,.56),'ink',.085)
text('INK & NOODLE title','INK & NOODLE',(0,-1.528,5.59),.40,'cream',3.88)
for x in [-1.98,1.98]:uv('Sign brass nail',(x,-1.53,5.57),(.028,.014,.028),'brass',16,10)
# cream noren panels, open at center
for x in [-2.33,-1.58,1.58,2.33]:
    # fabric simple gently bowed mesh
    vs=[];fs=[]
    for i in range(9):
        xx=x+(i/8-.5)*.71
        for j in range(5):
            zz=5.27-j*.15; yy=-.82-.025*cos(i*pi/2)-.02*sin(j*pi/4)
            vs.append((xx,yy,zz+.025*cos(i*pi/4)*(j/4)))
    for i in range(8):
        for j in range(4):k=i*5+j;fs.append((k,k+5,k+6,k+1))
    me=bpy.data.meshes.new('Noren textile');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('Split ivory noren curtain',me);bpy.context.collection.objects.link(ob);material(ob,'cream');smooth(ob)
    sol=ob.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.015
    curve('Noren teal bottom hem',[(x-.35,-.86,4.72),(x,-.86,4.69),(x+.35,-.86,4.72)],.012,'teal')
    if abs(x)>2: text('Noren symbol','08',(x,-.868,4.99),.22,'red')
    else:
        # small ramen bowl pictogram on fabric
        curve('Noren bowl emblem',[(x-.18,-.87,5.06),(x-.12,-.87,4.92),(x+.12,-.87,4.92),(x+.18,-.87,5.06)],.022,'teal')
        rod('Bowl emblem rim',(x-.2,-.87,5.06),(x+.2,-.87,5.06),.018,'teal')
# Lanterns
for x in [-2.78,2.78]:
    rod('Lantern hanging bracket',(x,.9,5.0),(x,-.78,5.0),.045,'ink')
    rod('Lantern cord',(x,-.76,5.0),(x,-.76,4.7),.024,'ink')
    uv('Glowing ribbed paper lantern',(x,-.76,4.21),(.35,.35,.51),'lantern',40,28)
    for j in range(11):
        z=3.77+j*.087;r=.35*math.sqrt(max(.05,1-((z-4.21)/.51)**2))
        torus('Lantern paper hoop',(x,-.76,z),r,.009,'gold',seg=40,minorseg=6)
    for z in [3.73,4.7]:cyl('Lantern black cap',(x,-.76,z),.19,.075,'ink')
    text('Lantern label','麺',(x,-1.102,4.23),.30,'red',font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    text('Lantern small label','RAMEN',(x,-1.09,3.99),.083,'ink')
    ld=bpy.data.lights.new('Lantern warm glow','POINT');lo=bpy.data.objects.new('Lantern warm glow',ld);bpy.context.collection.objects.link(lo);lo.location=(x,-.9,4.15);ld.energy=23;ld.color=(1,.43,.15);ld.shadow_soft_size=.45
# chef silhouette
uv('Chef mantle - coral octopus',(0,.19,3.38),(.86,.68,.94),'coralHi',48,32)
uv('Chef lower skirt',(0,.21,2.73),(.83,.61,.43),'coral',40,24)
# speckles at sides of mantle
for side in [-1,1]:
    for i in range(9):
        a=random.uniform(.15,.85);z=random.uniform(3.2,3.95);x=side*(.69+random.uniform(-.035,.035));y=-.10+random.uniform(-.05,.22)
        uv('Tiny mantle freckles',(x,y,z),(.025,.015,.027),'coral',12,8)
# face, aimed to front
for x in [-.29,.29]:
    uv('Ivory expressive eye',(x,-.414,3.57),(.205,.102,.255),'white')
    uv('Big ink pupil',(x+.025,-.505,3.565),(.105,.048,.149),'eye')
    uv('Eye catchlight',(x-.008,-.548,3.627),(.038,.014,.048),'white',20,12)
    uv('Tiny eye sparkle',(x+.062,-.547,3.54),(.015,.009,.018),'white',16,10)
    curve('Friendly raised eyebrow',[(x-.14,-.391,3.88),(x,-.435,3.93),(x+.13,-.4,3.9)],.032,'coral')
for x in [-.53,.53]:uv('Rosy cheek',(x,-.386,3.28),(.12,.038,.067),'pink')
uv('Protruding octopus muzzle',(0,-.463,3.24),(.20,.17,.18),'coral')
torus('Round smiling octopus mouth',(0,-.628,3.23),.096,.04,'underside',normal=(0,-1,0))
uv('Mouth inset',(0,-.632,3.23),(.07,.012,.069),'eye',24,12)
# fitted apron front trapezoid
verts=[(-.34,-.407,3.05),(.34,-.407,3.05),(.58,-.45,2.49),(-.58,-.45,2.49)]
me=bpy.data.meshes.new('Apron bib');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('Ocean teal apron',me);bpy.context.collection.objects.link(ob);material(ob,'teal');so=ob.modifiers.new('Apron fabric depth','SOLIDIFY');so.thickness=.035;be=ob.modifiers.new('Apron soft corners','BEVEL');be.width=.05;be.segments=4
for side in [-1,1]:
    curve('Apron cream piping',[(side*.33,-.435,3.04),(side*.47,-.485,2.72),(side*.56,-.48,2.51)],.014,'cream')
    curve('Apron neck strap',[(side*.32,-.40,2.98),(side*.40,-.39,3.18),(side*.50,-.25,3.19)],.042,'teal')
cube('Apron front pocket',(0,-.485,2.69),(.42,.055,.19),'roofHi',.035)
text('Apron embroidered 08','08',(0,-.52,2.7),.115,'cream')
# chef hat band + tall cloud top
cyl('Chef hat lower brim',(0,.20,4.19),.66,.20,'white')
# hat band cylinder scaled depth y
ob=bpy.context.object;ob.scale.y=.83
cyl('Chef hat broad rolled edge',(0,.20,4.17),.69,.065,'cream').scale.y=.84
uv('Toque central cloud',(0,.23,4.57),(.65,.50,.47),'white')
for x,y,z,s in [(-.49,.20,4.55,.35),(.49,.20,4.57,.35),(-.24,-.09,4.67,.37),(.23,-.10,4.7,.36),(0,.50,4.64,.36)]:uv('Soft pleated toque puff',(x,y,z),(s,s*.85,s*.92),'white')
for x in [-.43,-.22,0,.22,.43]:curve('Toque stitched pleat',[(x,-.36,4.18),(x*.98,-.37,4.29),(x*.96,-.34,4.37)],.009,'cream')
# flowing tapered octopus arms with front-facing suction pads

def catmull(points,per=10):
    ps=[Vector(points[0])]+[Vector(p) for p in points]+[Vector(points[-1])];out=[]
    for i in range(1,len(ps)-2):
        p0,p1,p2,p3=ps[i-1:i+3]
        for j in range(per):
            t=j/per;out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    out.append(Vector(points[-1]));return out

def arm(name,pts,r=.23):
    path=catmull(pts,10);N=len(path);vs=[];fs=[];frames=[];rads=[]
    for i,p in enumerate(path):
        tangent=(path[min(i+1,N-1)]-path[max(i-1,0)]).normalized();front=Vector((0,-1,-.15));a=(front-tangent*front.dot(tangent)).normalized();b=tangent.cross(a).normalized();rr=r*(1-i/(N-1))**.65+.032;rads.append(rr);frames.append((a,b,tangent))
        for j in range(16):ang=2*pi*j/16;vs.append(p+rr*(a*cos(ang)+b*sin(ang)))
    for i in range(N-1):
        for j in range(16):fs.append((i*16+j,i*16+(j+1)%16,(i+1)*16+(j+1)%16,(i+1)*16+j))
    fs.extend([tuple(range(15,-1,-1)),tuple((N-1)*16+j for j in range(16))])
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);material(o,'coralHi');material(o,'underside');smooth(o)
    for p in me.polygons:
        if p.index<(N-1)*16 and ((p.index%16)<=2 or (p.index%16)>=13):p.material_index=1
    for i in range(7,N-3,4):
        a,b,t=frames[i];rr=rads[i]
        for side in [-1,1]:
            norm=(a*.94+b*(side*.32)).normalized();pos=path[i]+norm*(rr+.009);cr=rr*.28
            torus(name+' ivory suction rim',pos,cr,.012 if cr>.037 else .009,'cup',normal=norm,seg=14,minorseg=6)
            disc=uv(name+' inset suction cup',pos-norm*.006,(cr*.78,cr*.78,.014),'cupIn',14,8);disc.rotation_euler=norm.to_track_quat('Z','Y').to_euler()
    uv(name+' rounded tip',path[-1],(.034,.034,.034),'coralHi',16,10)
arm('01 waving curl',[(-.58,.15,2.91),(-1.08,.03,3.12),(-1.40,-.07,3.52),(-1.48,-.08,4.00),(-1.70,-.08,4.22),(-1.95,-.08,4.12),(-1.95,-.08,3.90),(-1.80,-.08,3.87)],.235)
arm('02 noodle lifting arm',[(.59,.1,2.87),(1.03,-.02,3.10),(1.36,-.22,3.48),(1.66,-.43,3.77),(1.93,-.48,3.75),(2.0,-.54,3.59),(1.82,-.59,3.53)],.235)
arm('03 soup ladle arm',[(-.64,.21,2.74),(-1.14,.16,2.66),(-1.58,.04,2.92),(-1.96,-.05,3.05),(-2.16,-.24,2.89),(-2.03,-.39,2.75),(-1.88,-.34,2.84)],.225)
arm('04 serving bowl arm',[(.64,.25,2.70),(1.12,.18,2.69),(1.63,-.1,2.49),(2.09,-.48,2.47),(2.38,-.69,2.61),(2.34,-.90,2.69),(2.14,-.97,2.68)],.24)
arm('05 left counter curl',[(-.48,-.10,2.66),(-.84,-.49,2.37),(-1.07,-.94,2.22),(-1.44,-1.34,2.19),(-1.37,-1.58,2.17),(-1.09,-1.61,2.19),(-.97,-1.45,2.23)],.24)
arm('06 right counter curl',[(.48,-.09,2.63),(.75,-.50,2.35),(.97,-.98,2.19),(1.28,-1.43,2.17),(1.59,-1.49,2.22),(1.78,-1.33,2.28),(1.65,-1.17,2.32)],.24)
arm('07 left rear arm',[(-.53,.55,2.69),(-1.01,.62,2.39),(-1.38,.52,2.18),(-1.72,.28,2.19),(-1.66,.03,2.30),(-1.45,-.02,2.33)],.21)
arm('08 right rear arm',[(.52,.58,2.69),(.94,.78,2.34),(1.43,.71,2.20),(1.88,.48,2.20),(2.15,.31,2.30),(2.04,.12,2.39)],.21)
# ramen bowls, toppings and steam

def steam(x,y,z,h=1):
    for s in [-1,1]:
        curve('Curl of aromatic steam',[(x+s*.13,y,z),(x+s*.20,y+.02,z+h*.23),(x+s*.07,y+.03,z+h*.45),(x+s*.17,y+.035,z+h*.7),(x+s*.12,y+.04,z+h)],.018,'steam')

def bowl(name,x,y,z,s=1,details=True):
    prof=[(0,0),(.24,0),(.26,.05),(.32,.09),(.44,.22),(.56,.41),(.57,.46),(.535,.47),(.52,.42),(.40,.23),(.28,.13),(0,.13)]
    lathe(name+' ceramic bowl',[(r*s,h*s) for r,h in prof],(x,y,z),'cream')
    torus(name+' red lip',(x,y,z+.452*s),.556*s,.025*s,'red')
    torus(name+' foot',(x,y,z+.045*s),.25*s,.022*s,'teal')
    for a in range(0,360,30):
        aa=math.radians(a);xx=x+.49*s*cos(aa);yy=y+.49*s*sin(aa)
        # decorative marks follow outer wall
        rod(name+' blue brush mark',(xx,yy,z+.30*s),(x+.53*s*cos(aa+.04),y+.53*s*sin(aa+.04),z+.39*s),.017*s,'teal')
    cyl(name+' glossy amber broth',(x,y,z+.375*s),.505*s,.025*s,'broth',64)
    # interlocking golden noodle coils on soup
    for k in range(7):
        cx=x+(k%3-1)*.13*s;cy=y+(k//3-1)*.12*s
        pts=[]
        for j in range(17):
            a=j/16*2*pi;pts.append((cx+.16*s*cos(a),cy+.095*s*sin(a),z+(.402+.003*k)*s))
        curve(name+' curly noodles',pts,.018*s,'noodle')
    if details:
        # nori sheets, fan of bamboo shoots
        ob=cube(name+' upright nori',(x-.22*s,y+.24*s,z+.65*s),(.31*s,.026*s,.43*s),'nori',.015*s);ob.rotation_euler=(math.radians(-16),math.radians(-18),-.22)
        for i in range(4):
            rod(name+' nori texture',(x-.37*s+i*.08*s,y+.213*s,z+.48*s),(x-.42*s+i*.08*s,y+.29*s,z+.79*s),.007*s,'green')
        for i in range(3):
            ob=cube(name+' bamboo shoot',(x+(.12+i*.063)*s,y+.23*s,z+.43*s),(.045*s,.26*s,.035*s),'gold',.012*s);ob.rotation_euler.z=-.35+i*.18
        # egg white and rich orange yolk: raised slices
        e=uv(name+' halved egg white',(x+.25*s,y-.17*s,z+.443*s),(.16*s,.215*s,.065*s),'egg');e.rotation_euler.z=-.4
        e=uv(name+' soft egg yolk',(x+.25*s,y-.19*s,z+.501*s),(.10*s,.119*s,.022*s),'yolk');e.rotation_euler.z=-.4
        # chashu spiral
        uv(name+' chashu pork',(x-.24*s,y-.16*s,z+.439*s),(.19*s,.16*s,.045*s),'pink')
        pts=[]
        for j in range(42):
            a=j/41*pi*4;rr=(.015+.13*j/41)*s;pts.append((x-.24*s+rr*cos(a),y-.16*s+rr*.8*sin(a),z+.479*s))
        curve(name+' pork fat swirl',pts,.012*s,'fat')
        # scallion ring cluster
        for i in range(10):
            a=random.random()*2*pi;rr=random.uniform(.01,.13)*s
            torus(name+' fresh scallion',(x+.03*s+cos(a)*rr,y+.08*s+sin(a)*rr,z+.443*s+random.random()*.025*s),.034*s,.012*s,'greenLight',seg=16,minorseg=6)
    return z+.47*s
bowl('Signature tonkotsu',-.05,-.98,2.09,1.05)
steam(-.25,-.91,2.65,.81)
bowl('Bowl balanced on tentacle',2.30,-.81,2.71,.67)
steam(2.30,-.81,3.08,.56)
# chopsticks and dangling lifted noodles
for yy in [-.66,-.79]:rod('Chef long bamboo chopsticks',(.39,yy,3.67),(2.13,yy+.12,3.88),.025,'woodEdge')
for i in range(7):
    x=.44+i*.047;y=-.73+(i%2)*.045
    curve('Hanging ribbon of ramen',[(x,y,3.70),(x-.02,y,3.48),(x+.015,y-.015,3.14),(x-.10,y-.05,2.80),(x-.16,y-.1,2.53)],.018,'noodle')
# stove and stockpot
cyl('Portable stove',(-2.16,-.39,2.14),.54,.13,'ink')
torus('Burner brass ring',(-2.16,-.39,2.23),.38,.025,'brass')
lathe('Open stainless stock pot',[(0,0),(.4,0),(.46,.06),(.46,.57),(.49,.59),(.49,.63),(.445,.63),(.43,.57),(.43,.08),(0,.08)],(-2.16,-.39,2.23),'steel')
torus('Stock pot upper rolled edge',(-2.16,-.39,2.85),.47,.027,'steel')
cyl('Stock pot soup surface',(-2.16,-.39,2.76),.43,.02,'broth')
for xx in [-2.73,-1.59]:
    curve('Pot loop handle',[(xx+(.11 if xx<0 else -.11),-.51,2.67),(xx,-.53,2.71),(xx,-.25,2.71),(xx+(.11 if xx<0 else -.11),-.26,2.67)],.04,'ink')
rod('Ladle silver shaft',(-2.02,-.29,3.17),(-2.25,-.47,2.78),.025,'steel')
rod('Ladle wooden grip',(-2.02,-.29,3.17),(-1.89,-.20,3.38),.046,'wood')
uv('Ladle bowl',(-2.25,-.47,2.78),(.15,.13,.055),'steel')
steam(-2.24,-.36,2.87,.7)
# prep props right rear, jars on shelf
cube('Cutting board',(1.59,.23,2.12),(.94,.49,.06),'wood',.07)
for i in range(3):
    rod('Fresh spring onion white',(1.36+i*.085,.15,2.18),(1.40+i*.085,.35,2.18),.028,'white')
    rod('Fresh spring onion green',(1.40+i*.085,.35,2.18),(1.49+i*.085,.62,2.2),.024,'green')
for x in [-2.05,-1.55,1.62,2.13]:
    if x<0:
        for j in range(3):
            lathe('Stacked spare blue bowl',[(.13,0),(.20,.05),(.29,.18),(.265,.2),(.18,.08)],(x,.58,2.83+j*.12),'cream' if j%2 else 'teal',40)
    else:
        cyl('Ceramic ingredient jar',(x,.62,3.04),.18,.42,'cream')
        cyl('Jar cedar lid',(x,.62,3.27),.19,.06,'wood')
        uv('Jar lid knob',(x,.62,3.32),(.045,.045,.035),'ink')
        text('Jar hand label','SALT' if x<2 else 'MISO',(x,.43,3.05),.071,'teal')
# Condiment tray on front left end
cube('Condiment tray',(-2.58,-1.12,2.11),(.60,.40,.06),'ink',.04)
cyl('Soy sauce bottle',(-2.71,-1.14,2.29),.09,.30,'broth')
cyl('Soy red cap',(-2.71,-1.14,2.47),.10,.07,'red')
cube('Soy bottle ivory label',(-2.71,-1.224,2.30),(.12,.015,.13),'cream',.012)
cyl('Chilli shaker',(-2.47,-1.14,2.26),.075,.23,'red')
cyl('Shaker metal lid',(-2.47,-1.14,2.39),.081,.045,'steel')
for i in range(5):
    a=i*2*pi/5;cyl('Shaker perforation',(-2.47+.045*cos(a),-1.14+.045*sin(a),2.415),.009,.003,'ink',12)
# upright chopstick holder at far right
cyl('Teal chopstick crock',(2.65,.22,2.28),.15,.36,'teal')
torus('Crock cream lip',(2.65,.22,2.46),.15,.017,'cream')
for i in range(9):
    x=2.65+random.uniform(-.09,.09);y=.22+random.uniform(-.08,.08)
    rod('Spare bamboo chopstick',(x,y,2.34),(x+random.uniform(-.1,.1),y+random.uniform(-.08,.08),2.85+random.random()*.13),.014,'woodEdge')
# stools out front, each four legs and teal seat
for x in [-2.06,2.06]:
    y=-2.22
    for a in [pi/4,3*pi/4,5*pi/4,7*pi/4]:
        rod('Stool splayed cedar leg',(x+.34*cos(a),y+.34*sin(a),.39),(x+.23*cos(a),y+.23*sin(a),1.12),.052,'wood')
    torus('Stool brass cross brace',(x,y,.66),.28,.025,'brass')
    cyl('Stool maple seat',(x,y,1.13),.44,.14,'woodEdge')
    cyl('Stool thick teal cushion',(x,y,1.23),.40,.12,'teal')
    torus('Cushion cream piping',(x,y,1.27),.385,.015,'cream')
# freestanding small menu at side front; front text
cube('Menu chalkboard wood frame',(-3.15,-.46,1.22),(.73,.14,1.52),'woodEdge',.06)
cube('Menu blackboard',(-3.15,-.545,1.24),(.62,.03,1.36),'ink',.035)
text('Menu header','MENU',(-3.15,-.57,1.75),.145,'gold')
text('Menu rule','— — —',(-3.15,-.57,1.59),.11,'cream')
for body,z in [('TONKOTSU',1.4),('12',1.23),('MISO',1.04),('10',.88)]:text('Menu chalk lettering',body,(-3.15,-.57,z),.093 if len(body)>3 else .12,'cream',.53)
for xx in [-3.4,-2.9]:rod('Menu A frame leg',(xx,-.30,1.89),(xx,.20,.36),.035,'wood')
text('Menu footer','HOT • FRESH',(-3.15,-.57,.68),.07,'chalk')
# welcome mat & scattered graphic markings
cube('Woven indigo welcome mat',(0,-2.25,.38),(1.8,.81,.045),'teal',.06)
for x in [-.82,.82]:cube('Welcome mat cream border',(x,-2.25,.408),(.025,.67,.006),'cream',.005)
text('Mat greeting','SLURP!',(0,-2.31,.415),.23,'cream')
ob=bpy.context.object;ob.rotation_euler=(0,0,0)
# tiny front plinth plaque
cube('Edition label',(0,-3.174,.06),(2.18,.022,.18),'brass',.025)
text('Edition inscription','INK & NOODLE   /   No. 08',(0,-3.19,.07),.091,'ink',1.98)
# stage, camera, lighting
M['backdrop']=mat('Backdrop warm mist',(.16,.225,.25))
cube('Studio ground',(0,0,-.33),(200,200,.2),'backdrop',0)
world=bpy.data.worlds.new('Evening studio') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.25,.3,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35

def area(name,loc,power,col,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=col;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Large warm key',(-5,-7,11),1250,(1,.79,.57),7,(0,0,2.6))
area('Cool soft fill',(6,-2,7),950,(.57,.81,1),6,(0,0,2.8))
area('Roof rim light',(1,6,10),1600,(1,.74,.45),5,(0,0,3))
area('Face softbox',(0,-7,4.8),220,(1,.85,.68),3,(0,0,3.1))
bpy.ops.object.camera_add(location=(8.8,-14,8.3));cam=bpy.context.object;cam.name='Hero camera';cam.rotation_euler=(Vector((0,.05,2.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=10.2;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1400;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.film_transparent=False
# save work scene outside output; exported later after preview
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.getcwd(),'scene_work.blend'))
print('Created',len(bpy.data.objects),'objects')
