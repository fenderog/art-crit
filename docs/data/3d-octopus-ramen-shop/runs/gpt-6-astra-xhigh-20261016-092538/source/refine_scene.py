import bpy, math, os
from mathutils import Vector
s=bpy.context.scene
# Richer enamel, cedar and coral while retaining creamy highlights.
colors={'Coral':(.78,.125,.075),'Coral light':(.95,.25,.145),'Blush':(.86,.065,.075),'Sucker rim':(.99,.57,.37),'Sucker well':(.55,.13,.08),'Deep teal':(.009,.085,.095),'Teal':(.018,.18,.18),'Teal light':(.035,.245,.22),'Wood':(.4,.15,.05),'Wood light':(.58,.275,.105),'Wood golden':(.73,.41,.17),'Wood dark':(.18,.06,.023),'Red':(.65,.04,.025),'Lantern':(1,.21,.055)}
for name,col in colors.items():
    m=bpy.data.materials[name]; m.diffuse_color=(*col,1); m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1)
# Lift the roof as a single assembly to reveal the toque silhouette.
for o in bpy.data.collections['03 | Scalloped teal roof & house sign'].objects: o.location.z+=.43
for o in bpy.data.objects:
    if o.name.startswith('Cedar upright'):
        o.location.z+=.33; o.scale.z*=5.42/4.76
    if o.name.startswith('Post highlight'):
        o.location.z+=.33; o.scale.z*=4.49/3.83
    if o.name.startswith('Lantern warmth'): o.location.z+=.43
col=bpy.data.collections['02 | Joinery & service bar']
def beam(n,loc,sc):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.append(bpy.data.materials['Wood dark']); m=o.modifiers.new('Rounded timber','BEVEL'); m.width=.035; m.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
for x in [-3,3]: beam('Upper side lintel',(x,.91,5.96),(.21,2.4,.20))
beam('Rear lintel',(0,1.98,5.94),(6.15,.2,.22))
# Eyes and mouth slightly friendlier dark mouth.
m=bpy.data.materials['Wood dark'];
bpy.data.objects['Happy smile'].data.materials.clear(); bpy.data.objects['Happy smile'].data.materials.append(bpy.data.materials['Ink'])
# Warmer and more directional studio lighting.
s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
bpy.data.lights['Large warm key'].energy=1500
bpy.data.lights['Cool fill'].energy=750
bpy.data.lights['Rim lantern glow'].energy=1500
bpy.data.lights['Face softbox'].energy=200
s.view_settings.exposure=-.15
s.eevee.taa_render_samples=96
s.eevee.use_fast_gi=True
s.eevee.fast_gi_quality=1.0
s.eevee.fast_gi_ray_count=4
s.eevee.shadow_ray_count=4
s.eevee.shadow_step_count=8
cam=s.camera; cam.location=(8.6,-17,8.8); target=Vector((0,0,3.18)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=10.35
s.render.resolution_x=1000; s.render.resolution_y=1000; s.render.filepath=os.path.join(os.getcwd(),'preview2.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.getcwd(),'scene-working.blend'))
result={'preview':s.render.filepath}
