import sys, os, importlib, time
exec(open('scripts/build_all.py').read())
exec(open('scripts/shoot.py').read())
setup_lights()
os.makedirs('output', exist_ok=True)
t0 = time.time()
shots = [
    ('01_front_view', dict(cam=(-0.4, -8.4, 2.3), target=(-0.1, 0.1, 1.75), lens=50, w=1600, h=1200)),
    ('02_chef_portrait', dict(cam=(0.5, -3.6, 1.95), target=(0.2, 0.2, 1.7), lens=50, w=1600, h=1200, fstop=3.2, focus=(0.0, 0.0, 1.62))),
    ('03_three_quarter', dict(cam=(-4.5, -6.5, 5.2), target=(0, 0.2, 1.8), lens=45, w=1600, h=1200)),
    ('04_counter_detail', dict(cam=(-1.7, -2.9, 1.5), target=(0.2, -0.5, 1.3), lens=40, w=1600, h=1200, fstop=4.0, focus=(0.2, -0.3, 1.3))),
    ('05_stove_side', dict(cam=(-0.5, -3.3, 1.75), target=(-0.8, 0.3, 1.55), lens=36, w=1600, h=1200)),
]
only = globals().get('ONLY')
for name, kw in shots:
    if only and name not in only:
        continue
    shoot(name, samples=96, fmt='JPEG', outdir='output', **kw)
result = {"t": time.time() - t0, "files": sorted(os.listdir('output'))}
