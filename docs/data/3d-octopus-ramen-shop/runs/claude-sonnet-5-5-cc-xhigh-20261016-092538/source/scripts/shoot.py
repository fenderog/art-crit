import sys, os, importlib
sys.path.insert(0, os.path.abspath('scripts'))
import staging; importlib.reload(staging)
from lib import *

def setup_lights(key=0.55, fill=0.5, rim=0.8, bulb=0.35, lant=1.0, counter=0.6, exposure=0.0):
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o)
    staging.set_world('#2b3a6e', '#101733', 1.0)
    T = (0, 0.2, 1.6)
    staging.add_light("Key", 'AREA', (2.8, -5.0, 4.2), 700 * key, color='#fff0dd', size=4, target=T)
    staging.add_light("Fill", 'AREA', (-4.0, -3.5, 2.0), 300 * fill, color='#ffc890', size=4, target=T)
    staging.add_light("Rim", 'AREA', (0, 4.5, 4.5), 500 * rim, color='#9fb4ff', size=4, target=T)
    staging.add_light("Bulb", 'POINT', (0, 0.6, 2.7), 350 * bulb, color='#ffc870', size=0.1)
    staging.add_light("LanternL", 'POINT', (-1.8, -1.4, 2.8), 60 * lant, color='#ff6a3a', size=0.2)
    staging.add_light("LanternR", 'POINT', (1.8, -1.4, 2.8), 60 * lant, color='#ff6a3a', size=0.2)
    staging.add_light("Counter", 'AREA', (0, -2.2, 2.5), 250 * counter, color='#ffe2bd', size=(3.0, 1.0), target=(0, -0.5, 1.2))
    bpy.context.scene.view_settings.exposure = exposure

def shoot(name, cam, target, lens=50, w=1500, h=1200, samples=48, fstop=None, focus=None, fmt='PNG', outdir='renders', glow=True):
    staging.set_camera(cam, target, lens=lens, fstop=fstop, focus=focus)
    staging.render_settings(w, h, samples)
    if glow and bpy.context.scene.compositing_node_group is None:
        staging.enable_glow()
    ext = 'jpg' if fmt == 'JPEG' else 'png'
    return staging.render(f'{outdir}/{name}.{ext}', fmt=fmt)
