#!/usr/bin/env python3
"""SNES-style Eiffel Tower pixel art: 256x224, <=128 colours, <=16 colours per 8x8 tile.
Pure stdlib. Writes output/eiffel_tower_snes.png
"""
import zlib, struct, math, random, os

W, H = 256, 224
random.seed(1889)

def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

# ---------- palette (named, deliberately limited) ----------
P = {
    # sky gradient (top -> horizon), 14 bands
    'sky': [hx(c) for c in (
        '#181a46','#20245c','#2b3070','#374284','#46589c','#5973b2',
        '#7492c4','#94b0d2','#b6c3d6','#dcc2a6','#f2b47e','#f99e61',
        '#fb8a52','#f97d4e')],
    'sun_core': hx('#fff3c4'), 'sun_mid': hx('#ffe08a'), 'sun_glow': hx('#fbbf7a'),
    'star': hx('#eef2ff'),
    'cloud_hi': hx('#fff6e6'), 'cloud_mid': hx('#fbd3b6'), 'cloud_sh': hx('#d99a90'),
    'cloud_deep': hx('#a87aa0'),
    'city_far': hx('#6f6aa0'), 'city_mid': hx('#575488'), 'city_dark': hx('#3e3c66'),
    'city_roof': hx('#2f2e54'), 'win': hx('#ffd97a'),
    'grass_dark': hx('#245c32'), 'grass': hx('#357540'), 'grass_hi': hx('#4d9a4c'),
    'grass_lite': hx('#6fbc5e'),
    'tree_dark': hx('#173d26'), 'tree': hx('#265c34'), 'tree_hi': hx('#3d8a44'),
    'tree_lite': hx('#63b257'), 'trunk': hx('#3a2a24'),
    'path': hx('#dcc49c'), 'path_sh': hx('#bda27a'), 'path_hi': hx('#efe0bc'),
    'iron_out': hx('#171018'), 'iron_dark': hx('#2c212e'), 'iron': hx('#4a3340'),
    'iron_warm': hx('#73503f'), 'iron_hi': hx('#a97b58'), 'iron_lite': hx('#dcb07c'),
    'plat_hi': hx('#e8c88f'), 'light': hx('#ffec9e'), 'light_or': hx('#ffb84a'),
    'beacon': hx('#ff5a4a'),
    'flower_r': hx('#e85a6e'), 'flower_w': hx('#f6f0da'),
    'person1': hx('#22223a'), 'person2': hx('#7a3040'),
}
SKY = P['sky']

buf = [[SKY[0]] * W for _ in range(H)]

def px(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        buf[y][x] = c

def get(x, y):
    if 0 <= x < W and 0 <= y < H:
        return buf[y][x]
    return None

def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            px(x, y, c)

def ellipse(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if rx and ry and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                px(x, y, c)

def line(x0, y0, x1, y1, c, thick=1, hi=None):
    """Bresenham-ish thick line; hi colours the upper/left 1px edge when thick>=2."""
    steps = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 1
    r = thick / 2.0
    for i in range(steps + 1):
        t = i / steps
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for dy in range(-int(math.ceil(r)), int(math.ceil(r)) + 1):
            for dx in range(-int(math.ceil(r)), int(math.ceil(r)) + 1):
                if dx * dx + dy * dy <= r * r + 0.6:
                    col = c
                    if hi is not None and thick >= 2 and (dx == -int(math.ceil(r)) or dy == -int(math.ceil(r))):
                        col = hi
                    px(x + dx, y + dy, col)

def interp(points, y):
    """Smooth (Catmull-Rom) interpolation of half-width vs y."""
    if y <= points[0][0]:
        return points[0][1]
    if y >= points[-1][0]:
        return points[-1][1]
    for i in range(len(points) - 1):
        y0, v0 = points[i]; y1, v1 = points[i + 1]
        if y0 <= y <= y1:
            vm = points[i - 1][1] if i > 0 else v0
            vp = points[i + 2][1] if i + 2 < len(points) else v1
            t = (y - y0) / (y1 - y0)
            t2, t3 = t * t, t * t * t
            return 0.5 * ((2 * v0) + (-vm + v1) * t +
                          (2 * vm - 5 * v0 + 4 * v1 - vp) * t2 +
                          (-vm + 3 * v0 - 3 * v1 + vp) * t3)
    return points[-1][1]

# ================= SKY =================
HORIZON = 184
for y in range(HORIZON):
    f = y / HORIZON * (len(SKY) - 1)
    i = int(math.floor(f)); frac = f - i
    for x in range(W):
        # ordered dither in the lower part of each band
        if frac > 0.62 and i + 1 < len(SKY) and ((x + y) & 1):
            buf[y][x] = SKY[i + 1]
        else:
            buf[y][x] = SKY[i]

# stars in the deep top sky
for _ in range(42):
    x = random.randrange(W); y = random.randrange(0, 52)
    px(x, y, P['star'])
    if random.random() < 0.25:
        px(x + 1, y, P['star']); px(x, y + 1, P['star'])

# pale evening moon, upper left
SX, SY, SR = 40, 42, 10
ellipse(SX, SY, SR + 1, SR + 1, P['sun_mid'])
ellipse(SX, SY, SR, SR, P['sun_core'])
for cx, cy, r in [(SX - 3, SY - 2, 2), (SX + 2, SY + 3, 2), (SX + 4, SY - 4, 1), (SX - 1, SY + 5, 1)]:
    ellipse(cx, cy, r, r, P['sun_mid'])

# distant glow band behind tower (sunset bloom, dithered)
for y in range(120, HORIZON):
    for x in range(W):
        d = abs(x - 128)
        if d < 70 and ((x + y) & 1) == 0 and random.random() < 0.35:
            if get(x, y) in SKY:
                px(x, y, P['sun_glow'])

# ================= CLOUDS =================
def cloud(cx, cy, s):
    puffs = [(-2.0, 0.2, 1.5, 0.62), (-1.0, -0.25, 1.2, 0.7), (0.2, -0.4, 1.35, 0.78),
             (1.2, -0.15, 1.15, 0.66), (2.0, 0.25, 1.2, 0.55), (0.2, 0.35, 1.7, 0.6)]
    for ox, oy, rx, ry in puffs:  # shadow pass, offset down
        ellipse(cx + ox * s, cy + oy * s + 0.45 * s, rx * s, ry * s, P['cloud_deep'])
    for ox, oy, rx, ry in puffs:
        ellipse(cx + ox * s, cy + oy * s, rx * s, ry * s, P['cloud_mid'])
    for ox, oy, rx, ry in puffs[:4]:  # lit tops
        ellipse(cx + ox * s, cy + oy * s - 0.28 * s, rx * s * 0.82, ry * s * 0.62, P['cloud_hi'])
    # warm underside flecks
    for x in range(int(cx - 3 * s), int(cx + 3 * s)):
        for y in range(int(cy), int(cy + 1.2 * s)):
            if get(x, y) == P['cloud_mid'] and ((x + y) & 1):
                px(x, y, P['cloud_sh'])

cloud(196, 30, 7)
cloud(88, 22, 5)
cloud(222, 66, 6)
cloud(22, 84, 6)
cloud(168, 92, 4.2)
cloud(66, 116, 5)
cloud(214, 128, 4.5)

# birds
for bx, by in [(104, 52), (114, 47), (178, 58), (188, 53), (58, 66)]:
    px(bx - 2, by, P['city_dark']); px(bx - 1, by + 1, P['city_dark'])
    px(bx, by, P['city_dark'])
    px(bx + 1, by + 1, P['city_dark']); px(bx + 2, by, P['city_dark'])

# ================= DISTANT PARIS =================
BASE = HORIZON
def building(x, w, h, tone):
    rect(x, BASE - h, x + w, BASE, tone)
    # mansard roof
    for i in range(4):
        rect(x - 1 + i, BASE - h - 4 + i, x + w + 1 - i, BASE - h - 4 + i, P['city_roof'])
    px(x + w // 2, BASE - h - 6, P['city_roof']); px(x + w // 2, BASE - h - 5, P['city_roof'])
    for wy in range(BASE - h + 3, BASE - 3, 5):
        for wx in range(x + 2, x + w - 1, 4):
            if random.random() < 0.42:
                px(wx, wy, P['win']); px(wx, wy + 1, P['win'])

random.seed(7)
x = -4
while x < W:
    w = random.choice([18, 22, 26, 30]); h = random.choice([16, 20, 24, 28])
    building(x, w, h, random.choice([P['city_far'], P['city_mid']]))
    x += w + random.choice([2, 4, 6])

# Invalides-style dome, left
DX = 34
rect(DX - 11, BASE - 18, DX + 11, BASE, P['city_mid'])
ellipse(DX, BASE - 19, 10, 7, P['city_dark'])
ellipse(DX, BASE - 23, 5, 5, P['city_dark'])
rect(DX - 1, BASE - 32, DX + 1, BASE - 24, P['city_dark'])
px(DX, BASE - 34, P['win']); px(DX, BASE - 33, P['city_dark'])
for wy in range(BASE - 14, BASE - 2, 4):
    for wx in range(DX - 8, DX + 9, 4):
        if random.random() < 0.4:
            px(wx, wy, P['win'])

# church spire, right
SPX = 226
rect(SPX - 7, BASE - 16, SPX + 7, BASE, P['city_mid'])
for i in range(16):
    rect(SPX - max(1, 5 - i // 3), BASE - 17 - i, SPX + max(1, 5 - i // 3), BASE - 17 - i, P['city_roof'])
px(SPX, BASE - 34, P['win'])

# ================= GROUND: CHAMP DE MARS =================
for y in range(HORIZON, H):
    t = (y - HORIZON) / (H - HORIZON)
    c = P['grass_dark'] if t < 0.25 else P['grass'] if t < 0.62 else P['grass_hi']
    rect(0, y, W - 1, y, c)
# lawn mowing stripes (perspective bands)
for y in range(HORIZON, H):
    if ((y - HORIZON) // 6) % 2 == 0:
        for x in range(W):
            if get(x, y) == P['grass']:
                px(x, y, P['grass_hi'])
            elif get(x, y) == P['grass_hi'] and ((x + y) & 1):
                px(x, y, P['grass_lite'])
# central gravel path, widening toward viewer
for y in range(HORIZON - 2, H):
    t = (y - (HORIZON - 2)) / (H - HORIZON + 2)
    half = 7 + t * t * 34
    for x in range(int(128 - half), int(128 + half) + 1):
        c = P['path_hi'] if abs(x - 128) < half * 0.45 else P['path']
        if abs(x - 128) > half - 2:
            c = P['path_sh']
        px(x, y, c)
# side paths
for y in range(HORIZON + 6, H):
    t = (y - HORIZON) / (H - HORIZON)
    for cx in (46 - t * 20, 210 + t * 20):
        for x in range(int(cx - 3 - t * 5), int(cx + 3 + t * 5) + 1):
            px(x, y, P['path'] if ((x + y) & 1) else P['path_sh'])

# tree line along horizon (behind tower legs)
def tree(cx, base_y, s, dark=False):
    lo = P['tree_dark'] if dark else P['tree']
    rect(cx - 1, base_y - int(3 * s), cx + 1, base_y, P['trunk'])
    cy = base_y - int(4.2 * s)
    for ox, oy, r in [(-1.5, 0.4, 1.5), (1.5, 0.4, 1.5), (0, -0.7, 1.9), (-0.7, 0.8, 1.4), (0.8, 0.8, 1.4), (0, 0.2, 1.8)]:
        ellipse(cx + ox * s, cy + oy * s, r * s, r * s * 0.92, lo)
    for ox, oy, r in [(-0.9, -0.5, 1.1), (0.7, -0.8, 1.0), (0, -0.1, 1.2)]:
        ellipse(cx + ox * s, cy + oy * s, r * s, r * s * 0.85, P['tree_hi'])
    for _ in range(int(7 * s)):
        px(cx + random.randint(int(-2 * s), int(2 * s)), cy + random.randint(int(-2 * s), int(1 * s)), P['tree_lite'])

random.seed(31)
for tx in list(range(6, 120, 15)) + list(range(140, 254, 15)):
    tree(tx + random.randint(-3, 3), HORIZON + 4, random.uniform(2.6, 3.6), dark=True)

# ================= THE TOWER =================
CX = 128
OUTER = [(18, 1.2), (26, 2.5), (34, 5), (44, 7), (60, 9.5), (76, 12.5),
         (84, 15), (102, 19), (122, 24), (132, 27), (148, 33), (166, 42), (182, 54), (196, 67)]
INNER = [(132, 6), (142, 10), (156, 16), (170, 23), (184, 32), (196, 43)]
def ow(y): return interp(OUTER, y)
def iw(y): return interp(INNER, y)

IRON, IRON_D, IRON_O = P['iron'], P['iron_dark'], P['iron_out']
WARM, HI, LITE = P['iron_warm'], P['iron_hi'], P['iron_lite']

def beam(x0, y0, x1, y1, thick, warm_left=True):
    """Iron beam: dark body, warm lit edge on the sun (left/top) side."""
    line(x0, y0, x1, y1, IRON_O, thick + 1)
    line(x0, y0, x1, y1, IRON_D, thick)
    # warm rim, offset toward the sun
    line(x0 - 0.7, y0 - 0.5, x1 - 0.7, y1 - 0.5, WARM if warm_left else IRON, 1)

def truss_section(y_top, y_bot, step):
    ys = list(range(y_top, y_bot, step)) + [y_bot]
    L = [(CX - ow(y), y) for y in ys]; R = [(CX + ow(y), y) for y in ys]
    for i in range(len(ys) - 1):
        beam(L[i][0], L[i][1], R[i + 1][0], R[i + 1][1], 1)   # X
        beam(R[i][0], R[i][1], L[i + 1][0], L[i + 1][1], 1)
        beam(L[i][0], L[i][1], R[i][0], R[i][1], 1)           # horizontal
    # centre elevator shaft
    line(CX, y_top, CX, y_bot, IRON_O, 2); line(CX, y_top, CX, y_bot, IRON, 1)
    for i in range(len(ys) - 1):  # heavy outer chords on top of lattice
        beam(L[i][0], L[i][1], L[i + 1][0], L[i + 1][1], 3)
        beam(R[i][0], R[i][1], R[i + 1][0], R[i + 1][1], 3, warm_left=False)
    return ys

def leg(side):  # side -1 left, +1 right
    ys = list(range(132, 197, 11)) + [197]
    O = [(CX + side * ow(y), y) for y in ys]
    I = [(CX + side * iw(y), y) for y in ys]
    for i in range(len(ys) - 1):
        beam(O[i][0], O[i][1], I[i + 1][0], I[i + 1][1], 1)
        beam(I[i][0], I[i][1], O[i + 1][0], O[i + 1][1], 1)
        beam(O[i][0], O[i][1], I[i][0], I[i][1], 1)
    for i in range(len(ys) - 1):
        beam(O[i][0], O[i][1], O[i + 1][0], O[i + 1][1], 3, warm_left=(side < 0))
        beam(I[i][0], I[i][1], I[i + 1][0], I[i + 1][1], 3, warm_left=(side < 0))
    # foot
    fx = CX + side * (ow(197) + iw(197)) / 2
    rect(min(fx - 10, fx + 10), 194, max(fx - 10, fx + 10), 199, IRON_O)
    rect(min(fx - 10, fx + 10), 194, max(fx - 10, fx + 10), 195, WARM)
    rect(min(fx - 8, fx + 8), 199, max(fx - 8, fx + 8), 200, IRON_D)

# legs first, then shaft sections
leg(-1); leg(1)

# great arch under the first floor (decorative arc + spokes)
prev = None
for deg in range(180, -1, -3):
    a = math.radians(deg)
    x = CX + 40 * math.cos(a); y = 168 - 34 * math.sin(a)
    if prev:
        beam(prev[0], prev[1], x, y, 2)
    prev = (x, y)
for deg in range(165, 14, -15):  # arch spokes up to first floor
    a = math.radians(deg)
    x0 = CX + 40 * math.cos(a); y0 = 168 - 34 * math.sin(a)
    beam(x0, y0, x0 * 0.55 + CX * 0.45, 132, 1)

truss_section(84, 124, 10)    # between 2nd and 1st floors
truss_section(34, 76, 11)     # between summit and 2nd floor

# summit + spire
beam(CX - ow(30), 34, CX - 2, 20, 2)
beam(CX + ow(30), 34, CX + 2, 20, 2, warm_left=False)
rect(CX - 3, 19, CX + 3, 23, IRON_D); rect(CX - 3, 19, CX + 3, 20, P['plat_hi'])
line(CX, 19, CX, 11, IRON_O, 1)
px(CX, 10, P['beacon']); px(CX - 1, 10, P['light']); px(CX + 1, 10, P['light']); px(CX, 9, P['light'])
px(CX - 1, 21, P['win']); px(CX + 1, 21, P['win'])

def platform(y, half, h=7):
    rect(CX - half - 2, y, CX + half + 2, y + h, IRON_O)          # outline slab
    rect(CX - half, y + 1, CX + half, y + h - 1, IRON_D)
    rect(CX - half, y + 1, CX + half, y + 2, P['plat_hi'])        # lit deck edge
    rect(CX - half, y + 3, CX + half, y + 3, WARM)
    for x in range(int(CX - half) + 2, int(CX + half) - 1, 3):   # railing / windows
        px(x, y + 4, P['win']); px(x, y + 5, P['light_or'])
    rect(CX - half, y + h - 1, CX + half, y + h - 1, IRON)        # underside
    # corbel supports
    for sx in (-0.7, -0.35, 0.35, 0.7):
        line(CX + sx * half, y + h, CX + sx * half * 0.55, y + h + 4, IRON_O, 1)

platform(76, 19, 8)     # second floor
platform(124, 31, 8)    # first floor
platform(30, 8, 5)      # summit terrace

# golden lights tracing the outer chords (evening illumination)
for y in range(36, 196, 6):
    if 74 <= y <= 86 or 122 <= y <= 134:
        continue
    for s in (-1, 1):
        x = CX + s * ow(y)
        px(x, y, P['light']); px(x, y + 1, P['light_or'])
        if y > 134:  # inner leg lights
            xi = CX + s * iw(y)
            px(xi, y, P['light'])

# ================= FOREGROUND =================
random.seed(99)
for tx, s in [(18, 5.2), (48, 4.2), (206, 4.4), (238, 5.4)]:
    tree(tx, 222, s)
for tx in (76, 180):  # mid foreground trees flanking the path
    tree(tx, 214, 3.6)

def lamppost(x, base_y, h):
    rect(x, base_y - h, x, base_y, P['iron_out'])
    rect(x - 2, base_y - h - 3, x + 2, base_y - h, P['iron_out'])
    rect(x - 1, base_y - h - 2, x + 1, base_y - h - 1, P['light'])
    px(x, base_y - h - 2, P['sun_core'])
    for dx, dy in [(-3, -2), (3, -2), (-3, 0), (3, 0), (0, -4)]:
        px(x + dx, base_y - h + dy, P['light_or'])
    rect(x - 2, base_y, x + 2, base_y, P['iron_out'])

lamppost(96, 206, 15); lamppost(159, 206, 15)
lamppost(84, 219, 18); lamppost(171, 219, 18)

def person(x, y, c):
    px(x, y - 6, c); rect(x - 1, y - 5, x + 1, y - 2, c)
    px(x - 1, y - 1, c); px(x + 1, y - 1, c); px(x - 1, y, c); px(x + 1, y, c)

person(118, 205, P['person1']); person(123, 206, P['person2'])
person(140, 212, P['person1']); person(108, 216, P['person2']); person(150, 220, P['person1'])

# grass texture + flowers, kept off the paths
random.seed(4)
for _ in range(500):
    x = random.randrange(W); y = random.randrange(HORIZON + 2, H)
    if get(x, y) in (P['grass'], P['grass_hi'], P['grass_dark']):
        px(x, y, random.choice([P['grass_lite'], P['grass_dark'], P['grass_hi']]))
for _ in range(46):
    x = random.randrange(4, W - 4); y = random.randrange(196, H)
    if get(x, y) in (P['grass'], P['grass_hi'], P['grass_lite']):
        px(x, y, random.choice([P['flower_r'], P['flower_w'], P['win']]))

# ================= PNG OUT + VERIFY =================
def write_png(path):
    raw = b''
    for y in range(H):
        raw += b'\x00' + b''.join(bytes(c) for c in buf[y])
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)

os.makedirs('output', exist_ok=True)
out = 'output/eiffel_tower_snes.png'
write_png(out)

colours = {c for row in buf for c in row}
tile_max, worst = 0, None
for ty in range(H // 8):
    for tx in range(W // 8):
        s = {buf[y][x] for y in range(ty * 8, ty * 8 + 8) for x in range(tx * 8, tx * 8 + 8)}
        if len(s) > tile_max:
            tile_max, worst = len(s), (tx, ty)
print(f'{out}: {W}x{H}, {len(colours)} colours (limit 128), '
      f'max per 8x8 tile = {tile_max} at tile {worst} (limit 16), {os.path.getsize(out)} bytes')
assert len(colours) <= 128 and tile_max <= 16
