import bpy, math, os
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene

def mat(name, color, roughness=0.3, metallic=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    if coat:
        for k in ('Coat Weight','Clearcoat'):
            if k in b.inputs: b.inputs[k].default_value = coat; break
    return m

YELLOW = mat('Yellow Plastic', (0.95,0.69,0.015), 0.24, coat=0.25)
BLACK  = mat('Black Plastic', (0.012,0.012,0.014), 0.32, coat=0.15)
BLACKM = mat('Black Matte', (0.02,0.02,0.02), 0.65)
WHITE  = mat('White', (0.96,0.96,0.94), 0.25)
EYEW   = mat('Eye White', (0.90,0.90,0.88), 0.15)
PUPIL  = mat('Pupil', (0.004,0.004,0.004), 0.18)
GROOVE = mat('Groove Shadow', (0.45,0.32,0.0), 0.6)
DARKLN = mat('Dark Line', (0.05,0.05,0.05), 0.8)
PRINT  = mat('Top Print', (0.82,0.82,0.82), 0.5)

robie=[]
def reg(obj, material=None, name=None):
    if name: obj.name=name
    if material and hasattr(obj.data,'materials'): obj.data.materials.append(material)
    robie.append(obj); return obj
def smooth(obj):
    if obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True
    return obj
def bevel(obj,w=0.02,s=3):
    if obj.type=='MESH':
        m=obj.modifiers.new('Bevel','BEVEL'); m.width=w; m.segments=s; m.limit_method='ANGLE'
    return obj
def apply_scale(obj):
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def lathe(name, profile, material, segments=64):
    verts=[]; faces=[]; rings=[]
    for r,z in profile:
        if r<1e-6:
            idx=len(verts); verts.append((0,0,z)); rings.append([idx]*segments)
        else:
            ring=[]
            for i in range(segments):
                a=2*math.pi*i/segments; ring.append(len(verts)); verts.append((r*math.cos(a),r*math.sin(a),z))
            rings.append(ring)
    for j in range(len(profile)-1):
        for i in range(segments):
            i2=(i+1)%segments
            a,b,c,d=rings[j][i],rings[j][i2],rings[j+1][i2],rings[j+1][i]
            if a==b:  # bottom centre fan
                faces.append((a,c,d))
            elif c==d:  # top centre fan
                faces.append((a,b,c))
            else:
                faces.append((a,b,c,d))
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    mesh.materials.append(material); smooth(obj); robie.append(obj); return obj

def add_text(name, body, size, location, rotation, material, align='CENTER', extrude=0.004, font='Arial Bold.ttf'):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x=align; cu.align_y='CENTER'
    cu.extrude=extrude; cu.bevel_depth=0.0008
    try: cu.font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/'+font)
    except Exception as e: print('font',e)
    obj=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(obj)
    obj.location=location; obj.rotation_euler=rotation; cu.materials.append(material); robie.append(obj); return obj

# Body / Head
lathe('Body',[(0,0.30),(0.38,0.30),(0.55,0.315),(0.625,0.36),(0.655,0.46),(0.65,0.62),(0.63,0.80),(0.605,0.95),(0.575,1.03),(0.52,1.05),(0,1.05)],YELLOW)
lathe('Head',[(0,1.07),(0.50,1.07),(0.585,1.09),(0.62,1.16),(0.635,1.28),(0.635,1.44),(0.62,1.54),(0.57,1.595),(0.48,1.61),(0,1.61)],YELLOW)

bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.565,depth=0.028,location=(0,0,1.06))
reg(smooth(bpy.context.active_object),BLACKM,'NeckGap')
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.56,depth=0.055,location=(0,0,0.28))
reg(smooth(bpy.context.active_object),BLACK,'BasePlate')
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.515,depth=0.028,location=(0,0,1.613))
reg(smooth(bpy.context.active_object),BLACK,'TopDisc')

# Top grooves near back edge
for i in range(5):
    y=0.20+i*0.042
    length=2*math.sqrt(max(0.515**2-y*y,0.01))-0.08
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,1.628))
    o=bpy.context.active_object; o.dimensions=(length,0.010,0.004); reg(o,DARKLN,f'TopGroove{i}')

add_text('TopLogo','Radio Shack',0.105,(-0.04,-0.05,1.628),(0,0,0),PRINT,extrude=0.002)
add_text('TopSub','ROBOTIC BANKER',0.042,(-0.04,-0.155,1.628),(0,0,0),PRINT,extrude=0.002)
bpy.ops.mesh.primitive_torus_add(major_radius=0.052,minor_radius=0.007,major_segments=32,minor_segments=8,location=(0.30,-0.05,1.628))
reg(bpy.context.active_object,PRINT,'TopBadgeRing')
add_text('TopBadge','$',0.075,(0.30,-0.05,1.629),(0,0,0),PRINT,extrude=0.002)

# Eyes: rim on head surface, eyeball recessed, pupil low
for side,sx in [('L',-0.215),('R',0.215)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.128,minor_radius=0.018,major_segments=40,minor_segments=12,location=(sx*1.01,-0.603,1.375))
    rim=bpy.context.active_object
    rim.rotation_mode='QUATERNION'
    rim.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((sx,-0.598,0)).normalized())
    reg(smooth(rim),BLACK,f'EyeRim{side}')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=24,radius=0.108,location=(sx,-0.568,1.375))
    reg(smooth(bpy.context.active_object),EYEW,f'Eyeball{side}')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=0.062,location=(sx,-0.643,1.315))
    o=bpy.context.active_object; o.scale=(1.0,0.55,0.72); reg(smooth(o),PUPIL,f'Pupil{side}')

for i,tx in enumerate((-0.05,0.05)):
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=0.020,radius2=0.010,depth=0.06,location=(tx,-0.535,1.045),rotation=(math.radians(180),0,0))
    reg(smooth(bpy.context.active_object),WHITE,f'Tooth{i}')

# ROBIE logo (front, left of seam) - rotation X+90 faces -Y, readable from front
add_text('ROBIE_Logo','ROBIE',0.125,(-0.235,-0.625,0.905),(math.radians(90),0,0),BLACK,extrude=0.005,font='Arial Black.ttf')

for nm,y in [('SeamFront',-0.642),('SeamBack',0.628)]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,0.68))
    o=bpy.context.active_object; o.dimensions=(0.005,0.008,0.64); reg(o,GROOVE,nm)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0.616,1.13))
o=bpy.context.active_object; o.dimensions=(0.13,0.015,0.020); reg(o,BLACKM,'CoinSlot')

# Shoulders
for side,sx in [('L',-1),('R',1)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=0.205,depth=0.22,location=(sx*0.66,0,0.845),rotation=(0,math.radians(90),0))
    o=smooth(bpy.context.active_object); bevel(o,0.02); reg(o,YELLOW,f'Shoulder{side}')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.205,minor_radius=0.006,major_segments=36,minor_segments=8,location=(sx*0.575,0,0.845),rotation=(0,math.radians(90),0))
    reg(bpy.context.active_object,GROOVE,f'ShoulderGroove{side}')

# Arms
def tube(name,points,radius=0.042):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=5; cu.resolution_u=10
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for bp,p in zip(sp.bezier_points,points):
        bp.co=p; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(obj); cu.materials.append(BLACK); robie.append(obj); return obj

tube('ArmTray',[(0.68,-0.02,0.80),(0.76,-0.12,0.62),(0.70,-0.40,0.51),(0.50,-0.62,0.56)])
tube('ArmClaw',[(-0.68,-0.02,0.80),(-0.78,-0.12,0.58),(-0.76,-0.32,0.40),(-0.73,-0.42,0.36)])

bpy.ops.mesh.primitive_torus_add(major_radius=0.155,minor_radius=0.041,major_segments=36,minor_segments=12,location=(-0.71,-0.44,0.26),rotation=(math.radians(90),0,math.radians(-10)))
claw=smooth(bpy.context.active_object); reg(claw,BLACK,'ClawHook')
bpy.ops.mesh.primitive_cube_add(size=1,location=(-0.565,-0.44,0.33))
cutter=bpy.context.active_object; cutter.dimensions=(0.22,0.22,0.24)
bpy.context.view_layer.objects.active=claw
mod=claw.modifiers.new('ClawCut','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cutter
bpy.ops.object.modifier_apply(modifier='ClawCut'); bpy.data.objects.remove(cutter,do_unlink=True)

# Coin tray
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=0.255,depth=0.035,location=(0.26,-0.80,0.58))
o=bpy.context.active_object; o.scale=(1.28,0.88,1.0); apply_scale(o); bevel(o,0.010,2); reg(smooth(o),BLACK,'CoinTray')
bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=0.060,radius2=0.005,depth=0.15,location=(0.625,-0.80,0.58),rotation=(0,math.radians(-90),0))
o=bpy.context.active_object; o.scale=(0.28,1,1)
# local X maps to world Z after the Y rotation, so this flattens the cone vertically
reg(smooth(o),BLACK,'TraySpout')
bpy.ops.mesh.primitive_torus_add(major_radius=0.155,minor_radius=0.009,major_segments=48,minor_segments=8,location=(0.26,-0.80,0.599))
reg(bpy.context.active_object,WHITE,'TrayRing')
add_text('TrayDollar','$',0.23,(0.26,-0.80,0.599),(0,0,0),WHITE,extrude=0.003,font='Arial Black.ttf')

# Feet (unit sphere, tapered in local coords, object scale retained)
def make_foot(side,sx):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=28,radius=1.0,location=(sx*0.52,-0.42,0.12))
    o=bpy.context.active_object
    for v in o.data.vertices:
        if v.co.y<0:
            t=abs(v.co.y)
            v.co.x*=max(1.0-0.38*t*t,0.45)
            v.co.z*=max(1.0-0.22*t*t,0.55)
        if v.co.z<-0.60: v.co.z=-0.60
    o.data.update()
    o.scale=(0.205,0.48,0.165); o.rotation_euler=(0,0,math.radians(-sx*6))
    reg(smooth(o),YELLOW,f'Foot{side}')
    sole=o.copy(); sole.data=o.data.copy(); bpy.context.collection.objects.link(sole)
    sole.name=f'Sole{side}'; sole.scale=(0.215,0.49,0.055); sole.location=(sx*0.52,-0.42,0.038)
    sole.data.materials.clear(); sole.data.materials.append(BLACK); robie.append(sole)
    for i,dy in enumerate((0.20,0.26)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.175,minor_radius=0.004,major_segments=32,minor_segments=6,
            location=(sx*0.52 - math.sin(math.radians(-sx*6))*dy, -0.42+dy*math.cos(math.radians(6)), 0.125),
            rotation=(math.radians(90),0,math.radians(-sx*6)))
        g=bpy.context.active_object; g.scale=(1,0.72,1); reg(g,GROOVE,f'FootGroove{side}{i}')
make_foot('L',-1); make_foot('R',1)

# Scene
world=bpy.data.worlds['World']; world.use_nodes=True
bg=world.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.88,0.88,0.88,1); bg.inputs[1].default_value=0.55
bpy.ops.mesh.primitive_plane_add(size=14,location=(0,0,0))
ground=bpy.context.active_object; ground.name='Ground'; ground.data.materials.append(mat('GroundMat',(0.86,0.86,0.86),0.9))
def area(name,loc,energy,size=3):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new(name,ld); bpy.context.collection.objects.link(lo); lo.location=loc
    lo.rotation_euler=(Vector((0,0,0.8))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area('Key',(2.5,-3.0,3.5),420); area('Fill',(-3.0,-1.5,2.0),170); area('Top',(0,1.5,4.0),200)
camd=bpy.data.cameras.new('Camera'); camd.lens=42
cam=bpy.data.objects.new('Camera',camd); bpy.context.collection.objects.link(cam); scene.camera=cam
def set_cam(loc,target=(0,-0.08,0.82)):
    cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.cycles.use_denoising=True
scene.render.resolution_x=900; scene.render.resolution_y=900
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0.88
os.makedirs('renders',exist_ok=True)
for name,loc in {'front':(0,-3.6,1.15),'front34':(2.4,-3.0,1.7),'side':(3.6,-0.5,1.2),'back34':(-2.2,3.0,1.9),'top':(0.6,-1.9,3.8)}.items():
    set_cam(loc); scene.render.filepath=f'renders/preview_{name}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='robie.blend')
result={'count':len(robie),'names':[o.name for o in robie]}
