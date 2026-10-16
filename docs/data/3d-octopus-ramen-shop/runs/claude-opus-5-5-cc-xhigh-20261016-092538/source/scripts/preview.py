# Quick preview renders from arbitrary viewpoints.
import bpy, os
from mathutils import Vector


def preview(path, cam_loc, target, lens=35, res=(800, 450), engine='BLENDER_EEVEE', samples=16,
            work_light=True):
    s = bpy.context.scene
    cam = bpy.data.objects.get("PreviewCam")
    if cam is None:
        cd = bpy.data.cameras.new("PreviewCam")
        cam = bpy.data.objects.new("PreviewCam", cd)
        s.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_start = 0.05
    cam.data.clip_end = 200
    cam.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    old_cam = s.camera
    s.camera = cam
    wl = None
    if work_light and not any(o.type == 'LIGHT' for o in s.objects):
        ld = bpy.data.lights.new("PrevSun", 'SUN')
        ld.energy = 3.0
        wl = bpy.data.objects.new("PrevSun", ld)
        s.collection.objects.link(wl)
        wl.rotation_euler = (0.8, 0.2, -0.6)
    s.render.engine = engine
    if engine == 'CYCLES':
        s.cycles.samples = samples
        s.cycles.device = 'GPU'
        s.cycles.use_denoising = True
    else:
        s.eevee.taa_render_samples = samples
    s.render.resolution_x, s.render.resolution_y = res
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.render.filepath = os.path.abspath(path)
    bpy.ops.render.render(write_still=True)
    s.camera = old_cam
    if wl:
        bpy.data.objects.remove(wl, do_unlink=True)
    return path
