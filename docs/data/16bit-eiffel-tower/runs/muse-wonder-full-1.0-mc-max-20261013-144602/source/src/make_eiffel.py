#!/usr/bin/env python3
"""SNES-style Eiffel Tower pixel art, 256x224, stdlib only.

All colours are 15-bit SNES values (multiples of 8). A final pass
guarantees <=128 colours total and <=16 colours per 8x8 tile.
"""
import math, random, struct, zlib
from collections import Counter

W, H = 256, 224
CX = 128
rng = random.Random(1889)

# --- palette (r,g,b), each channel a multiple of 8 -------------------------
def C(r, g, b): return (r, g, b)

SKY = [C(16,16,56), C(32,24,80), C(48,32,104), C(72,48,128),
       C(96,56,136), C(128,72,136), C(160,88,128), C(192,104,112),
       C(216,128,96), C(232,152,80), C(240,176,80), C(248,200,104),
       C(248,216,136)]
SUN_OUT = C(240,176,96); SUN_MID = C(248,192,104); SUN_IN = C(248,216,128)
SUN_CORE = C(248,232,160); HALO = C(224,144,104)
STAR = C(248,240,216); STAR2 = C(184,184,224)
CL_HI = C(248,192,168); CL_MID = C(216,136,144); CL_SH = C(152,88,120)
CL_DK = C(104,64,104)
FAR = C(120,88,120); FAR_ROOF = C(88,64,104)
NEAR = C(56,40,80); NEAR2 = C(72,48,88); ROOF = C(32,24,56)
WIN_LIT = C(248,208,104); WIN_DIM = C(216,160,88); WIN_DK = C(24,16,40)
DOME = C(184,136,80); DOME_HI = C(248,208,120)
HAZE = C(232,176,128)
LAWN_T = C(40,88,48); LAWN_M = C(32,72,40); LAWN_D = C(24,56,32)
LAWN_F = C(16,40,24); HEDGE = C(16,48,24); HEDGE_HI = C(48,104,48)
PATH = C(168,144,112); PATH_D = C(136,112,88); PATH_L = C(192,168,136)
PATH_E = C(88,72,56)
TREE_HI = C(56,120,56); TREE_M = C(32,88,40); TREE_D = C(16,56,24)
TRUNK = C(56,32,24)
STONE = C(120,112,104); STONE_D = C(72,64,64)
IRON_DK = C(24,16,32); IRON = C(48,32,40); IRON_M = C(80,48,48)
IRON_L = C(128,80,64); RIM = C(240,168,104); RIM2 = C(248,208,136)
GOLD = C(248,216,112); GOLD_D = C(232,160,48); GLASS = C(248,192,96)
WHITE = C(248,248,232)
PINK = C(240,144,168); FLOW_W = C(248,232,192); FLOW_Y = C(240,192,64)
SHADOW = C(16,32,24)

px = [[SKY[0]] * W for _ in range(H)]

def P(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: px[y][x] = c

def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1): P(x, y, c)

def hline(x0, x1, y, c):
    for x in range(int(x0), int(x1) + 1): P(x, y, c)

def line(x0, y0, x1, y1, c, t=1):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err, x, y = dx + dy, x0, y0; r = t // 2
    while True:
        for oy in range(-r, t - r):
            for ox in range(-r, t - r): P(x + ox, y + oy, c)
        if x == x1 and y == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x += sx
        if e2 <= dx: err += dx; y += sy

def ellipse(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: P(x, y, c)

def interp(keys, y):
    if y <= keys[0][0]: return keys[0][1]
    for (y0, v0), (y1, v1) in zip(keys, keys[1:]):
        if y <= y1: return v0 + (v1 - v0) * (y - y0) / max(1, y1 - y0)
    return keys[-1][1]

# --- sky, stars, sun, clouds -----------------------------------------------
def draw_sky():
    bounds = [0, 14, 28, 42, 56, 70, 84, 98, 112, 126, 138, 150, 160, 176]
    for i, col in enumerate(SKY):
        rect(0, bounds[i], W - 1, bounds[i + 1] - 1, col)
    # checker dither across each band boundary (classic SNES gradient)
    for i in range(len(SKY) - 1):
        yb = bounds[i + 1]
        for dy in range(-1, 1):
            for x in range(W):
                if (x + dy) % 2 == 0 and dy >= 0: P(x, yb + dy, SKY[i])
                if (x + dy) % 2 == 0 and dy < 0: P(x, yb + dy, SKY[i + 1])
    for _ in range(46):  # stars, fading toward the glow
        x, y = rng.randrange(W), rng.randrange(2, 58)
        P(x, y, STAR if rng.random() < .6 else STAR2)
        if rng.random() < .22:
            P(x - 1, y, STAR2); P(x + 1, y, STAR2)
            P(x, y - 1, STAR2); P(x, y + 1, STAR2)

def draw_sun():
    cx, cy = CX, 106
    ellipse(cx, cy, 44, 44, HALO)
    # dithered halo edge
    for y in range(cy - 48, cy + 49):
        for x in range(cx - 48, cx + 49):
            d = math.hypot(x - cx, y - cy)
            if 43 < d <= 46 and (x + y) % 2 == 0: P(x, y, HALO)
    ellipse(cx, cy, 36, 36, SUN_OUT)
    ellipse(cx, cy, 30, 30, SUN_MID)
    ellipse(cx, cy - 3, 19, 19, SUN_IN)
    ellipse(cx, cy - 5, 9, 9, SUN_CORE)

def cloud(cx, cy, w, hi=CL_HI, mid=CL_MID, sh=CL_SH):
    """Lobed top, flat base: three bumps standing on a stepped body."""
    base = cy + 5
    cells = set()
    bumps = [(cx - w * .30, w * .17), (cx - w * .06, w * .25), (cx + w * .20, w * .19),
             (cx + w * .38, w * .11)]
    for bx, r in bumps:
        by = base - r * .45
        for y in range(int(by - r) - 1, int(by + r) + 2):
            for x in range(int(bx - r) - 1, int(bx + r) + 2):
                if (x - bx) ** 2 + (y - by) ** 2 <= r * r and y <= base: cells.add((x, y))
    for y in range(base - 4, base + 1):                   # body, ends stepping in
        inset = 0 if y > base - 3 else 3
        for x in range(int(cx - w / 2 + 3 + inset), int(cx + w / 2 - 2 - inset)):
            cells.add((x, y))
    if not cells: return
    ymax = {}
    for (x, y) in cells: ymax[x] = max(ymax.get(x, -99), y)
    for (x, y) in cells:
        if (x, y - 2) not in cells: P(x, y, hi)           # lit top
        elif y >= ymax[x] - 1: P(x, y, sh)                # shaded belly
        else: P(x, y, mid)

def draw_clouds_and_birds():
    cloud(38, 34, 52); cloud(214, 26, 58); cloud(180, 58, 40)
    cloud(50, 74, 44); cloud(226, 90, 38)
    cloud(68, 104, 36, CL_HI, CL_SH, CL_DK)              # small cloud at sun's edge
    cloud(210, 118, 36, CL_HI, CL_MID, CL_SH)
    for bx, by in [(64, 52), (78, 59), (196, 44), (92, 46)]:
        P(bx, by, IRON_DK)
        for i in (1, 2):                                 # steep little chevron wings
            P(bx - i, by - i, IRON_DK); P(bx + i, by - i, IRON_DK)

# --- Paris skyline ----------------------------------------------------------
def building(x, w, top, base, body, roof, lit_p):
    rect(x, top + 5, x + w - 1, base, body)
    for i in range(5):  # mansard roof, stepping in
        hline(x + i // 2, x + w - 1 - i // 2, top + 4 - i, roof)
    if w > 12: rect(x + 3, top - 3, x + 5, top, roof)     # chimney
    if w > 18: rect(x + w - 6, top - 2, x + w - 4, top, roof)
    for wy in range(top + 9, base - 2, 7):
        for wx in range(x + 3, x + w - 3, 6):
            r = rng.random()
            c = WIN_LIT if r < lit_p else (WIN_DIM if r < lit_p + .15 else WIN_DK)
            P(wx, wy, c); P(wx, wy + 1, c)

def dome(cx, base, w, body, roof, gold=False):
    dc = DOME if gold else roof
    rect(cx - w // 2, base - 14, cx + w // 2, base, body)
    hline(cx - w // 2 - 1, cx + w // 2 + 1, base - 15, dc)  # cornice
    for i, hw in enumerate([w // 2 - 1, w // 2 - 1, w // 2 - 2, w // 2 - 3,
                            w // 2 - 5, w // 2 - 8]):       # rounded stepped cupola
        for yy in (base - 16 - i * 2, base - 17 - i * 2):
            hline(cx - hw, cx + hw, yy, dc)
            if gold: P(cx - hw, yy, DOME_HI); P(cx - hw + 1, yy, DOME_HI)
    rect(cx - 2, base - 31, cx + 2, base - 28, dc)
    line(cx, base - 36, cx, base - 31, IRON_DK, 1)
    P(cx, base - 37, GOLD)
    for wx in range(cx - w // 2 + 3, cx + w // 2 - 2, 6):
        P(wx, base - 10, WIN_LIT if rng.random() < .6 else WIN_DK)
        P(wx, base - 5, WIN_LIT if rng.random() < .5 else WIN_DK)

def draw_skyline():
    base = 176
    hline(0, W - 1, base - 1, HAZE); hline(0, W - 1, base, HAZE)
    far = [(0, 26, 150), (24, 20, 156), (60, 24, 152), (84, 18, 158),
           (150, 22, 154), (172, 18, 158), (206, 24, 152), (230, 26, 156)]
    for x, w, t in far: building(x, w, t, base, FAR, FAR_ROOF, .25)
    dome(50, base, 22, FAR, FAR_ROOF)                     # distant dome L
    near = [(0, 30, 158), (28, 22, 164), (68, 24, 160), (164, 26, 160),
            (188, 20, 165), (222, 34, 158)]
    for x, w, t in near: building(x, w, t, base, NEAR, ROOF, .45)
    building(96, 18, 166, base, NEAR2, ROOF, .4)          # glimpsed through arch
    building(142, 18, 166, base, NEAR2, ROOF, .4)
    building(110, 36, 168, base, FAR, FAR_ROOF, .35)      # low block on the axis
    for tx in range(100, 160, 11):                        # tree line on the horizon
        ellipse(tx, 172, 5, 3, C(56, 80, 56))
    dome(206, base, 24, NEAR, ROOF, gold=True)            # Invalides-style dome R

# --- Champ de Mars gardens --------------------------------------------------
def draw_ground():
    bands = [(176, LAWN_T), (188, LAWN_M), (200, LAWN_D), (212, LAWN_F)]
    for (y0, c), (y1, _) in zip(bands, bands[1:] + [(224, None)]):
        rect(0, y0, W - 1, y1 - 1, c)
    for i in range(len(bands) - 1):                       # dither joins
        yb = bands[i + 1][0]
        for x in range(W):
            if x % 2 == 0: P(x, yb - 1, bands[i + 1][1])
    # central allee, widening in perspective
    for y in range(176, H):
        half = 18 + (y - 176) * 0.55
        for x in range(int(CX - half), int(CX + half) + 1):
            c = PATH if y < 198 else PATH_D
            if (x * 7 + y * 13) % 11 == 0: c = PATH_L if y < 198 else PATH
            P(x, y, c)
        P(CX - half, y, PATH_E); P(CX - half - 1, y, PATH_E)
        P(CX + half, y, PATH_E); P(CX + half + 1, y, PATH_E)
    for y in (192, 206, 218):                             # cross joints in gravel
        half = 18 + (y - 176) * 0.55
        hline(CX - half, CX + half, y, PATH_E)
    # side walks + lawn panels
    for s in (-1, 1):
        line(CX + s * 52, 176, CX + s * 108, 223, PATH_E, 2)
        line(CX + s * 52, 177, CX + s * 108, 223, PATH, 1)
    hline(0, W - 1, 196, PATH_E); hline(0, W - 1, 197, PATH)
    for hx, hy, hw in [(8, 182, 42), (206, 182, 42), (6, 202, 58), (192, 202, 58)]:
        rect(hx, hy, hx + hw, hy + 9, HEDGE)              # parterre hedges
        hline(hx, hx + hw, hy, HEDGE_HI); hline(hx, hx + hw, hy + 1, HEDGE_HI)
        for _ in range(8):
            P(rng.randrange(hx + 1, hx + hw), rng.randrange(hy + 2, hy + 9),
              rng.choice([PINK, FLOW_W, FLOW_Y]))
    for _ in range(80):                                   # grass texture ticks
        x, y = rng.randrange(W), rng.randrange(178, H)
        if px[y][x] in (LAWN_T, LAWN_M, LAWN_D, LAWN_F): P(x, y, HEDGE_HI if y < 200 else LAWN_M)

# --- the tower --------------------------------------------------------------
OUTER = [(20, 1), (26, 3), (34, 5), (46, 8), (60, 11), (72, 14), (80, 15),
         (96, 20), (110, 26), (118, 31), (126, 33), (140, 39), (155, 46),
         (170, 53), (182, 59)]
INNER = [(126, 8), (136, 16), (148, 23), (160, 30), (172, 37), (182, 42)]
def ow(y): return interp(OUTER, y)
def iw(y): return interp(INNER, y)

def pillar_row(y, half, w, side, inner=False):
    """One row of a rim-lit pillar. side=-1 left, +1 right."""
    edge = CX + side * half
    for i in range(int(w)):
        x = edge - side * i
        c = RIM if i == 0 else (IRON_M if i == 1 else (IRON if i < w - 1 else IRON_DK))
        if inner and i == 0: c = RIM
        P(x, y, c)
    P(edge + side, y, IRON_DK)  # crisp dark outline just outside the rim

def platform(y0, half, h):
    for x in range(int(CX - half) + 1, int(CX + half), 4):  # railing posts above
        P(x, y0 - 2, IRON_DK); P(x, y0 - 1, IRON_DK)
    hline(CX - half, CX + half, y0 - 2, IRON_DK)
    P(CX - half, y0 - 1, IRON_DK); P(CX + half, y0 - 1, IRON_DK)  # end posts
    rect(CX - half, y0, CX + half, y0 + h - 1, IRON)
    hline(CX - half, CX + half, y0, RIM)                  # lit top edge
    hline(CX - half, CX + half, y0 + 1, IRON_DK)
    for x in range(int(CX - half) + 2, int(CX + half) - 1, 4):  # glass band
        lit = rng.random() < .78
        for yy in range(y0 + 2, y0 + h - 2):
            P(x, yy, GLASS if lit else IRON_DK); P(x + 1, yy, GOLD_D if lit else IRON)
    hline(CX - half, CX + half, y0 + h - 2, IRON_M)
    hline(CX - half, CX + half, y0 + h - 1, IRON_DK)
    for i in range(3):                                    # stepped corbels below
        hline(CX - half + i + 1, CX + half - i - 1, y0 + h + i, IRON_DK if i else IRON)

def lattice(y_top, y_bot, levels, split=False):
    """X-braced trunk; `split` adds a centre post and an X in each half."""
    if split:
        for y in range(levels[0], levels[-1] + 1):        # centre post
            P(CX - 1, y, IRON_M); P(CX, y, IRON_DK); P(CX + 1, y, IRON_DK)
    for a, b in zip(levels, levels[1:]):
        lt, rt = CX - ow(a) + 3, CX + ow(a) - 3
        lb, rb = CX - ow(b) + 3, CX + ow(b) - 3
        if split:
            line(lt, a, CX - 1, b, IRON_DK, 2); line(CX + 1, a, lb, b, IRON_DK, 2)
            line(CX - 1, a, rb, b, IRON_DK, 2); line(rt, a, CX + 1, b, IRON_DK, 2)
        else:
            line(lt, a, rb, b, IRON_DK, 2); line(rt, a, lb, b, IRON_DK, 2)
            line(lt, a, rb, b, IRON, 1)
        hline(CX - ow(b) + 2, CX + ow(b) - 2, b, IRON_DK)
        hline(CX - ow(b) + 2, CX + ow(b) - 2, b - 1, IRON_M)
        P(CX, (a + b) // 2, GOLD_D)                       # rivet / floodlight glint

def draw_tower():
    ellipse(CX - 50, 184, 16, 3, SHADOW)                  # shadow under each foot
    ellipse(CX + 50, 184, 16, 3, SHADOW)
    # outer pillars (whole height) + inner leg pillars
    for y in range(26, 183):
        w = 3 if y < 46 else (4 if y < 80 else (5 if y < 126 else 6))
        if not (73 <= y <= 81 or 119 <= y <= 128):        # platforms drawn later
            pillar_row(y, ow(y), w, -1); pillar_row(y, ow(y), w, +1)
        if y >= 126:
            for i in range(5):                            # inner legs, painted outward
                c = RIM if i == 0 else (IRON_M if i == 1 else (IRON if i < 4 else IRON_DK))
                P(CX + iw(y) + i, y, c); P(CX - iw(y) - i, y, c)
            P(CX + iw(y) - 1, y, IRON_DK); P(CX - iw(y) + 1, y, IRON_DK)
    lattice(34, 72, [36, 45, 54, 63, 72])                 # summit -> 2nd floor
    lattice(80, 118, [82, 91, 100, 109, 118], split=True)  # 2nd -> 1st floor
    # lattice inside each leg
    lv = [128, 140, 152, 164, 176, 182]
    for s in (-1, 1):
        for a, b in zip(lv, lv[1:]):
            line(CX + s * (iw(a) + 4), a, CX + s * (ow(b) - 5), b, IRON_DK, 2)
            line(CX + s * (ow(a) - 5), a, CX + s * (iw(b) + 4), b, IRON_DK, 2)
            hline(min(CX + s * (iw(b) + 3), CX + s * (ow(b) - 4)),
                  max(CX + s * (iw(b) + 3), CX + s * (ow(b) - 4)), b, IRON_M)
    # the great arch between the legs
    for t in range(0, 181, 2):
        a = math.radians(t)
        for r in range(4):
            P(CX + math.cos(a) * (31 - r), 160 - math.sin(a) * (25 - r * .7),
              RIM if r == 3 else (IRON_M if r == 2 else IRON_DK))
    for fx in (-24, -13, 0, 13, 24):                      # fan braces arch -> 1st floor
        ya = 160 - 25 * math.sqrt(max(0.0, 1 - (fx / 31) ** 2))
        line(CX + fx * .72, 129, CX + fx, ya + 1, IRON_DK, 2)
    rect(CX - 20, 99, CX - 15, 105, IRON_DK)              # lift cabin on the pillar track
    rect(CX - 19, 100, CX - 16, 103, GOLD_D); P(CX - 18, 101, GOLD); P(CX - 17, 101, GOLD)
    platform(73, 20, 7)                                   # second floor
    platform(119, 38, 8)                                  # first floor
    # summit + beacon
    platform(32, 8, 3)
    rect(CX - 5, 23, CX + 5, 32, IRON)
    hline(CX - 5, CX + 5, 23, RIM); hline(CX - 4, CX + 4, 22, IRON_M)
    rect(CX - 4, 26, CX + 4, 28, GLASS)                   # summit glass band
    for x in (CX - 2, CX + 1, CX + 4):
        for yy in (26, 27, 28): P(x, yy, IRON_DK)
    P(CX - 3, 27, GOLD_D); P(CX + 2, 27, GOLD_D)
    hline(CX - 5, CX + 5, 31, IRON_DK)
    line(CX, 22, CX, 13, IRON_DK, 1)
    P(CX, 12, WHITE); P(CX, 11, GOLD)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        P(CX + dx, 12 + dy, RIM2)                         # beacon sparkle
    P(CX, 12, WHITE)
    # stone footings
    for s in (-1, 1):
        fx = CX + s * 50
        rect(fx - 9, 179, fx + 9, 184, STONE)
        hline(fx - 9, fx + 9, 179, STONE_D); hline(fx - 9, fx + 9, 184, STONE_D)
        for i in range(4): P(fx - 6 + i * 4, 182, STONE_D)
    # sparkling floodlights along the pillars
    for y in range(30, 180, 7):
        for s in (-1, 1):
            if rng.random() < .75: P(CX + s * (ow(y) - 2), y, GOLD)
        if rng.random() < .4: P(CX + rng.randrange(-3, 4), y, GOLD)

# --- foreground: trees, lamps, people ---------------------------------------
def tree(cx, base, r):
    rect(cx - 1, base - r, cx + 1, base, TRUNK)
    cells = set()
    for bx, by, br in [(cx, base - r - r // 2, r), (cx - r // 2, base - r - 2, r * 2 // 3),
                       (cx + r // 2, base - r - 2, r * 2 // 3)]:
        for y in range(by - br, by + br + 1):
            for x in range(bx - br, bx + br + 1):
                if (x - bx) ** 2 + (y - by) ** 2 <= br * br: cells.add((x, y))
    for (x, y) in cells:
        if (x, y - 2) not in cells or (x - 2, y) not in cells: P(x, y, TREE_HI)
        elif (x, y + 2) not in cells: P(x, y, TREE_D)
        else: P(x, y, TREE_M)
    for _ in range(r):                                    # leaf speckle
        x, y = rng.choice(sorted(cells)); P(x, y, TREE_HI if rng.random() < .5 else TREE_D)

def lamp(x, base, h):
    line(x, base, x, base - h, IRON_DK, 1); line(x + 1, base, x + 1, base - h, IRON_DK, 1)
    gy = base - h - 2
    for dx, dy in [(-2, 0), (3, 0), (0, -3), (1, 2), (-1, -1), (2, -1), (-1, 1), (2, 1)]:
        P(x + dx, gy + dy, GOLD_D)                        # halo
    rect(x - 1, gy - 1, x + 2, gy + 1, GOLD); P(x, gy, WHITE); P(x + 1, gy, WHITE)
    P(x, gy - 2, IRON_DK); P(x + 1, gy - 2, IRON_DK)
    ellipse(x, base + 1, 5, 1, PATH_L)                    # pool of light

def person(x, base, h, c):
    top = base - h
    P(x, top, IRON_DK); P(x + 1, top, IRON_DK)            # head
    P(x, top + 1, C(240, 192, 144)); P(x + 1, top + 1, C(240, 192, 144))
    for yy in range(top + 2, top + 2 + max(2, h // 2)):   # coat, 3 px wide
        P(x - 1, yy, c); P(x, yy, c); P(x + 1, yy, c)
    for yy in range(top + 2 + max(2, h // 2), base):      # legs
        P(x - 1, yy, IRON_DK); P(x + 1, yy, IRON_DK)
    hline(x - 2, x + 3, base, SHADOW)

def draw_foreground():
    for off, base, r in [(30, 187, 5), (38, 198, 7), (48, 212, 9), (58, 223, 11)]:
        tree(CX - off - 8, base, r); tree(CX + off + 8, base, r)
    for off, base, h in [(24, 190, 9), (33, 202, 12), (44, 216, 15)]:
        lamp(CX - off, base, h); lamp(CX + off, base, h)
    person(112, 205, 9, C(40, 48, 96)); person(139, 200, 8, C(160, 56, 72))
    person(150, 214, 11, C(56, 40, 32)); person(101, 218, 11, C(48, 88, 120))
    person(124, 196, 7, C(120, 88, 40))

# --- SNES limits + PNG output ------------------------------------------------
def nearest(c, cands):
    return min(cands, key=lambda k: (c[0]-k[0])**2 + (c[1]-k[1])**2 + (c[2]-k[2])**2)

def enforce_limits():
    for ty in range(0, H, 8):                             # <=16 colours / 8x8 tile
        for tx in range(0, W, 8):
            while True:
                cnt = Counter(px[y][x] for y in range(ty, ty+8) for x in range(tx, tx+8))
                if len(cnt) <= 16: break
                rare = cnt.most_common()[-1][0]
                keep = [c for c, _ in cnt.most_common(15)]
                rep = nearest(rare, keep)
                for y in range(ty, ty+8):
                    for x in range(tx, tx+8):
                        if px[y][x] == rare: px[y][x] = rep
    while True:                                           # <=128 colours total
        cnt = Counter(c for row in px for c in row)
        if len(cnt) <= 128: break
        rare = cnt.most_common()[-1][0]
        rep = nearest(rare, [c for c, _ in cnt.most_common(127)])
        for y in range(H):
            for x in range(W):
                if px[y][x] == rare: px[y][x] = rep

def write_png(path):
    raw = b"".join(b"\x00" + b"".join(bytes(c) for c in row) for row in px)
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(png)

def report():
    cols = Counter(c for row in px for c in row)
    worst = max(len({px[y][x] for y in range(ty, ty+8) for x in range(tx, tx+8)})
                for ty in range(0, H, 8) for tx in range(0, W, 8))
    print(f"size={W}x{H} colours={len(cols)} worst_tile={worst} tiles={W//8}x{H//8}")

if __name__ == "__main__":
    draw_sky(); draw_sun(); draw_clouds_and_birds(); draw_skyline()
    draw_ground(); draw_tower(); draw_foreground()
    enforce_limits(); report()
    write_png("output/eiffel_tower_snes.png")
    print("wrote output/eiffel_tower_snes.png")



