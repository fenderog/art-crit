"""Camera, lights, world and render settings."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *


def set_world(color_top='#1a2142', color_bottom='#0b0f22', strength=1.0):
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    mp = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
    mp.inputs['From Min'].default_value = 0.35
    mp.inputs['From Max'].default_value = 0.85
    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = hexc(color_bottom)
    ramp.color_ramp.elements[1].color = hexc(color_top)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def add_light(name, kind, loc, energy, color='#ffffff', size=None, rot=None, target=None, spot=None, parent=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = hexc(color)[:3]
    if kind == 'AREA' and size:
        ld.size = size if not isinstance(size, tuple) else size[0]
        if isinstance(size, tuple):
            ld.shape = 'RECTANGLE'
            ld.size_y = size[1]
    if kind == 'POINT' and size:
        ld.shadow_soft_size = size
    if kind == 'SUN' and size:
        ld.angle = size
    if kind == 'SPOT':
        ld.spot_size = radians(spot or 60)
        ld.spot_blend = 0.5
        if size:
            ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if target is not None:
        d = Vector(target) - Vector(loc)
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    elif rot is not None:
        ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    return ob


def set_camera(loc, target, lens=50, name="Camera", fstop=None, focus=None):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        bpy.context.scene.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_start = 0.05
    cam.data.clip_end = 100
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = (Vector(focus if focus is not None else target) - Vector(loc)).length
    else:
        cam.data.dof.use_dof = False
    return cam


def render_settings(w=1600, h=1000, samples=64):
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.render.resolution_x = w
    s.render.resolution_y = h
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.render.film_transparent = False
    try:
        s.eevee.taa_render_samples = samples
        s.eevee.use_raytracing = True
        s.eevee.use_shadows = True
    except Exception as e:
        pass
    try:
        s.view_settings.view_transform = 'Khronos PBR Neutral'
    except Exception:
        s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'None'


def enable_glow(strength=0.5, size=0.6, threshold=1.0):
    sc = bpy.context.scene
    old = sc.compositing_node_group
    if old is not None:
        sc.compositing_node_group = None
        bpy.data.node_groups.remove(old)
    ng = bpy.data.node_groups.new("Comp", 'CompositorNodeTree')
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers')
    gl = ng.nodes.new('CompositorNodeGlare')
    out = ng.nodes.new('NodeGroupOutput')
    gl.inputs['Type'].default_value = 'Bloom'
    gl.inputs['Threshold'].default_value = threshold
    gl.inputs['Strength'].default_value = strength
    gl.inputs['Size'].default_value = size
    ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
    ng.links.new(gl.outputs[0], out.inputs[0])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True


def render(path, fmt='PNG', quality=92):
    s0 = bpy.context.scene
    s0.render.image_settings.file_format = fmt
    if fmt == 'JPEG':
        s0.render.image_settings.quality = quality
    s0.render.image_settings.color_mode = 'RGB'
    path = path if path.lower().endswith(('.png', '.jpg')) else path
    s = bpy.context.scene
    s.render.filepath = os.path.abspath(path)
    bpy.ops.render.render(write_still=True)
    return s.render.filepath
