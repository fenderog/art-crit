import sys, os, importlib
sys.path.insert(0, os.path.abspath('scripts'))
import lib, layout, octopus, arms, staging
for m in (lib, layout, octopus, arms, staging):
    importlib.reload(m)
from lib import *
import layout as L

reset()
M = octopus.octo_mats()
root = group("Octopus")
octopus.build_body(root, M)
octopus.build_face(root, M)
octopus.build_toque(root, M)
octopus.build_scarf(root, M)
info = arms.build(root, M)
# proxy counter and floor
wood = mat('proxy_wood', '#c9a066', rough=0.6)
make("proxy_counter", box(3.0, 0.75, 0.06, 0.01), wood, loc=(0, -0.575, 0.97))
make("proxy_front", box(3.0, 0.05, 0.97), mat('proxy_dark', '#7d2e22'), loc=(0, -0.92, 0.485))
make("proxy_floor", box(6, 4, 0.1), mat('proxy_floor', '#444a58'), loc=(0, 0, -0.05))
make("proxy_stove", box(1.0, 0.9, 0.95), mat('proxy_stove', '#3a3d47'), loc=(-1.0, 0.45, 0.475))
staging.set_world()
staging.add_light("Key", 'AREA', (2.5, -4.0, 4.0), 700, size=3, target=(0, 0.3, 1.5))
staging.add_light("Fill", 'AREA', (-3.5, -3.0, 2.5), 300, color='#ffd9b0', size=3, target=(0, 0.3, 1.5))
staging.add_light("Rim", 'AREA', (0, 3.5, 3.5), 500, color='#9fb4ff', size=3, target=(0, 0.3, 1.5))
staging.set_camera((0, -5.8, 1.9), (0, 0.2, 1.45), lens=50)
staging.render_settings(1200, 800, 32)
path = staging.render('renders/octo_test.png')
staging.set_camera((0.0, -2.4, 1.75), (0, 0.2, 1.65), lens=60)
staging.render('renders/octo_face.png')
staging.set_camera((0, -5.8, 1.9), (0, 0.2, 1.45), lens=50)
result = {k: (round(v['length'], 2), v['n_suckers']) for k, v in info.items()}
