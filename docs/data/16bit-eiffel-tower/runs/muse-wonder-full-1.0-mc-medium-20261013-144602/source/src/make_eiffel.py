#!/usr/bin/env python3
"""SNES-style Eiffel Tower pixel art: 256x224, <=128 colors, <=16 colors per 8x8 tile.
Pure stdlib. Writes an indexed PNG to output/eiffel_tower_snes.png
"""
import zlib, struct, random, math, os
from collections import Counter

W, H = 256, 224
CX = 128

# ---------- palette ----------
PAL = []
IDX = {}
def C(hexstr):
    hexstr = hexstr.lstrip('#')
    rgb = tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))
    if rgb not in IDX:
        IDX[rgb] = len(PAL); PAL.append(rgb)
    return IDX[rgb]

# sky bands (top -> horizon)
SKY = [C(c) for c in ["16204a","23255c","342c68","4a356e","673e73","8a4776",
                      "ad5375","cf6468","e87c5c","f5985a","fab66a","fcd389","fee9a8"]]
SUN_D, SUN_L, SUN_C = C("ffb36b"), C("ffd98e"), C("fff3bc")
STAR, STAR2 = C("e8ecff"), C("9aa8e8")
# clouds
CL_SH, CL_D, CL_M, CL_L, CL_H = C("5a3d6e"), C("8e5a7d"), C("c77f8d"), C("eda08a"), C("ffcf9e")
CL_TOP_H = C("ffe3b8")
# distant Paris
CITY_D, CITY_M, CITY_L, CITY_WIN = C("332647"), C("483558"), C("5f4668"), C("ffd97a")
# iron
IR_0 = C("171016")  # outline / deepest
IR_1 = C("2b1b22")  # dark iron
IR_2 = C("452a30")  # mid iron
IR_3 = C("6b4038")  # warm iron
IR_4 = C("9a5f42")  # lit iron
IR_5 = C("c98a56")  # highlight
RIM  = C("f2bd7d")  # golden rim light
LIT  = C("ffe08a")  # tower lights
LIT2 = C("fff6c8")
BEACON = C("ff5a4e")
# ground / garden
GR_D, GR_M, GR_L, GR_H = C("1e3a2e"), C("2c5340"), C("3d7050"), C("57905e")
HEDGE_D, HEDGE_L = C("17301f"), C("2e5c36")
TREE_D, TREE_M, TREE_L, TREE_H = C("14291e"), C("214534"), C("356b45"), C("5d9a58")
TRUNK = C("3a2a22")
PATH_D, PATH_M, PATH_L = C("9a7a54"), C("c2a06e"), C("e0c088")
FLOW_R, FLOW_Y, FLOW_W = C("d9576b"), C("f2c654"), C("f4e8d0")
LAMP, LAMP_H = C("ffca6a"), C("fff0b0")
SIL = C("201826")  # tiny people / birds

img = [[SKY[0]] * W for _ in range(H)]
rng = random.Random(1889)

def px(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        img[y][x] = c

def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            px(x, y, c)

def line(x0, y0, x1, y1, c, thick=1):
    x0, y0, x1, y1 = map(float, (x0, y0, x1, y1))
    steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(steps + 1):
        t = i / steps if steps else 0
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = thick // 2
        for dy in range(-r, thick - r):
            for dx in range(-r, thick - r):
                px(x + dx, y + dy, c)

def disc(cx, cy, rx, ry, c):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / max(rx, .5)) ** 2 + ((y - cy) / max(ry, .5)) ** 2 <= 1:
                px(x, y, c)

# ---------- sky with dithered band transitions ----------
BAND_H = 184 / len(SKY)  # sky down to horizon y=184
for y in range(184):
    f = y / BAND_H
    i = min(int(f), len(SKY) - 1)
    frac = f - i
    for x in range(W):
        c = SKY[i]
        if i + 1 < len(SKY) and frac > 0.62:  # ordered dither into next band
            t = (frac - 0.62) / 0.38
            bayer = ((x & 1) * 2 + (y & 1)) / 4.0 + (0.25 if (x & 2) else 0)
            if bayer < t:
                c = SKY[i + 1]
        img[y][x] = c

# stars in upper sky
for _ in range(46):
    x, y = rng.randrange(W), rng.randrange(38)
    px(x, y, STAR if rng.random() < .5 else STAR2)
    if rng.random() < .25:
        px(x + 1, y, STAR2)

# ---------- low sun, left of tower ----------
for y in range(114, 162):  # dithered halo
    for x in range(22, 70):
        d = math.hypot(x - 46, y - 138)
        keep = (x + y) % 2 == 0 if d < 19 else (x % 2 == 0 and y % 2 == 0)
        if 15 < d < 23 and keep:
            px(x, y, SUN_D)
disc(46, 138, 15, 15, SUN_L); disc(46, 138, 11, 11, SUN_C)
for y in (150, 153):  # classic banded-sun slices near horizon
    for x in range(28, 65):
        if img[y][x] in (SUN_L, SUN_C):
            img[y][x] = SKY[min(int(y / BAND_H), len(SKY) - 1)]

# ---------- clouds ----------
def cloud(cx, cy, w, h, seed):
    r = random.Random(seed)
    bumps = []
    n = 4 + w // 16
    for i in range(n):
        bx = cx - w / 2 + w * (i + .5) / n + r.uniform(-3, 3)
        br = h * r.uniform(1.05, 1.6)
        bumps.append((bx, cy + h * .1 - abs(i - (n - 1) / 2) * .9 + r.uniform(-1, 1), br))
    def inside(x, y, shrink=0):
        if y > cy + h * .62 - shrink: return False
        return any(((x - bx) / max(br - shrink, 1)) ** 2 + ((y - by) / max(br * .8 - shrink, 1)) ** 2 <= 1
                   for bx, by, br in bumps)
    for y in range(int(cy - h), int(cy + h)):
        for x in range(int(cx - w / 2 - 4), int(cx + w / 2 + 5)):
            if not inside(x, y): continue
            if not inside(x, y + 2): px(x, y, CL_SH)          # underside shadow
            elif y > cy + h * .12: px(x, y, CL_D if (x + y) % 7 else CL_SH)
            elif not inside(x, y - 2): px(x, y, CL_TOP_H)     # sunlit top edge
            elif y < cy - h * .15: px(x, y, CL_L)
            else: px(x, y, CL_M if ((x // 3 + y) % 5) else CL_D)
    # a few highlight puffs
    for bx, by, br in bumps[::2]:
        disc(bx - br * .25, by - br * .3, max(br * .4, 1), max(br * .25, 1), CL_H)

cloud(40, 36, 52, 9, 1); cloud(205, 28, 64, 10, 2); cloud(158, 54, 44, 8, 3)
cloud(26, 76, 40, 8, 4);  cloud(226, 86, 46, 9, 5);  cloud(204, 118, 52, 8, 6)
cloud(62, 102, 34, 7, 7); cloud(90, 58, 26, 6, 8)

# birds
for bx, by, s in [(86, 46, 3), (98, 40, 2), (176, 66, 3), (168, 60, 2), (70, 62, 2)]:
    px(bx - s, by - 1, SIL); px(bx - s + 1, by, SIL); px(bx, by + 1, SIL)
    px(bx + s, by - 1, SIL); px(bx + s - 1, by, SIL)

# ---------- distant Paris rooftops ----------
def building(x, w, top, base=186, c=CITY_M, roof=CITY_D):
    rect(x, top, x + w, base, c)
    for i in range(w // 2 + 1):  # mansard roof slope
        px(x + i, top - 1 - i // 2, roof); px(x + w - i, top - 1 - i // 2, roof)
    for wy in range(top + 4, base - 2, 5):
        for wx in range(x + 2, x + w - 1, 4):
            if rng.random() < .45: px(wx, wy, CITY_WIN)

building(2, 22, 168); building(26, 16, 174); building(44, 20, 170)
building(192, 20, 171); building(214, 16, 175); building(232, 22, 167)
building(66, 12, 178); building(178, 12, 179)
for x in (8, 34, 52, 200, 222, 244): rect(x, 160 + (x % 7), x + 2, 168, CITY_D)  # chimneys
# domes glimpsed through the great arch, plus a low skyline on the axis
disc(103, 178, 8, 8, CITY_L); rect(95, 178, 111, 186, CITY_M)
rect(102, 167, 104, 171, CITY_L); px(103, 165, CITY_WIN)
disc(155, 180, 6, 6, CITY_L); rect(149, 180, 161, 186, CITY_M); px(155, 173, CITY_L)
rect(114, 181, 146, 186, CITY_D)
for wx in range(117, 145, 5): px(wx, 183, CITY_WIN)

# ---------- ground: Champ de Mars ----------
rect(0, 184, W - 1, H - 1, GR_M)
for y in range(184, H):
    for x in range(W):
        d = (y - 184) / 40
        if (x + y) % 2 == 0 and rng.random() < .08: img[y][x] = GR_D
        elif rng.random() < .025 + d * .02: img[y][x] = GR_L
rect(0, 184, W - 1, 185, GR_H)  # horizon light line
# perspective garden beds (trapezoid hedges either side of path)
for side in (-1, 1):
    for y in range(194, 220):
        t = (y - 194) / 26
        inner = CX + side * (16 + 44 * t); outer = CX + side * (52 + 66 * t)
        x0, x1 = sorted([int(inner), int(outer)])
        for x in range(x0, x1 + 1):
            edge = y in (194, 195, 218, 219) or x - x0 < 2 or x1 - x < 2
            px(x, y, HEDGE_D if edge else GR_D)
            if edge and x - x0 == 1: px(x, y, HEDGE_L)
            if not edge and y % 4 == 1 and (x * 7 + y) % 11 == 0:  # neat flower rows
                px(x, y, [FLOW_R, FLOW_Y, FLOW_W][(x + y) % 3])
# central path
for y in range(186, H):
    t = (y - 186) / 38
    hw = 7 + 42 * t * t + 8 * t
    for x in range(int(CX - hw), int(CX + hw) + 1):
        edge = abs(x - CX) > hw - 2
        px(x, y, PATH_D if edge else (PATH_L if (x + y) % 5 == 0 else PATH_M))
for y in (191, 195, 200, 207, 216):  # path cross seams, perspective spacing
    t = (y - 186) / 38; hw = 7 + 42 * t * t + 8 * t
    line(CX - hw, y, CX + hw, y, PATH_D)

# ============================================================
#  EIFFEL TOWER
# ============================================================
CTRL = [(22,3),(34,6),(50,9),(66,13),(78,17),(86,19),(102,25),(116,31),
        (127,36),(136,39),(156,47),(176,55),(193,63)]
def hw_at(y):
    if y <= CTRL[0][0]: return CTRL[0][1]
    for (y0, h0), (y1, h1) in zip(CTRL, CTRL[1:]):
        if y0 <= y <= y1:
            return h0 + (h1 - h0) * (y - y0) / (y1 - y0)
    return CTRL[-1][1]

def iron_at(x, base=IR_2):
    """Warm light from the left, shadow on the right."""
    if x < CX - 4: return IR_3 if base == IR_2 else base
    if x > CX + 4: return IR_1 if base == IR_2 else base
    return base

def truss_segment(y0, y1, step=9):
    """Filled lattice between two floors: outer chords, horizontals, X braces, inner chords."""
    # outer chords (thick, rim-lit on outer face)
    for side in (-1, 1):
        pts = [(CX + side * hw_at(y), y) for y in range(y0, y1 + 1, 4)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            line(ax, ay, bx, by, IR_1, 3)
            line(ax + side, ay, bx + side, by, RIM if side < 0 else IR_4, 1)
            line(ax - side, ay, bx - side, by, IR_0, 1)
    rows = list(range(y0, y1, step)) + [y1]
    # inner vertical chords at 1/3 points
    for frac in (-.45, 0, .45):
        pts = [(CX + frac * hw_at(y), y) for y in rows]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            line(ax, ay, bx, by, IR_2, 1)
    # horizontals + X braces per panel
    for ya, yb in zip(rows, rows[1:]):
        la, ra = CX - hw_at(ya), CX + hw_at(ya)
        lb, rb = CX - hw_at(yb), CX + hw_at(yb)
        line(la, ya, ra, ya, IR_2, 2)
        line(la, ya, ra, yb, IR_1, 1)
        line(ra, ya, lb, yb, IR_1, 1)
        line(CX + hw_at(ya) * -.45, ya, CX + hw_at(yb) * .45, yb, IR_2, 1)
        line(CX + hw_at(ya) * .45, ya, CX + hw_at(yb) * -.45, yb, IR_2, 1)

def leg_segment(y0, y1):
    """Two separate legs below the first floor, joined by the great arch."""
    for side in (-1, 1):
        rows = list(range(y0, y1, 9)) + [y1]
        for ya, yb in zip(rows, rows[1:]):
            oa, ob = CX + side * hw_at(ya), CX + side * hw_at(yb)
            ia, ib = CX + side * (hw_at(ya) - 13), CX + side * (hw_at(yb) - 15)
            line(oa, ya, ob, yb, IR_1, 3)
            line(oa + side, ya, ob + side, yb, RIM if side < 0 else IR_4, 1)
            line(ia, ya, ib, yb, IR_1, 2)
            line(ia, ya, ob, yb, IR_2, 1)   # X inside leg
            line(oa, ya, ib, yb, IR_2, 1)
            line(ia, ya, oa, ya, IR_2, 2)   # horizontal rung
        # foot / plinth
        fx = CX + side * (hw_at(y1) - 7)
        rect(min(fx, fx + side * 13), y1 - 2, max(fx, fx + side * 13), y1 + 1, IR_0)
        rect(min(fx, fx + side * 13), y1 - 2, max(fx, fx + side * 13), y1 - 2, IR_4)
    # great semicircular arch between legs
    for a_deg in range(0, 181, 2):
        a = math.radians(a_deg)
        x = CX + 47 * math.cos(a); y = 192 - 46 * math.sin(a)
        disc(x, y, 1.6, 1.6, IR_1)
    for a_deg in range(8, 173, 2):
        a = math.radians(a_deg)
        x = CX + 43 * math.cos(a); y = 192 - 42 * math.sin(a)
        px(x, y, IR_3)
    for a_deg in range(20, 165, 16):  # arch spokes
        a = math.radians(a_deg)
        line(CX + 40 * math.cos(a), 192 - 39 * math.sin(a),
             CX + 47 * math.cos(a), 192 - 46 * math.sin(a), IR_2, 1)

def platform(y, halfw, tall=7):
    x0, x1 = CX - halfw, CX + halfw
    rect(x0, y, x1, y + tall, IR_1)
    rect(x0, y, x1, y, RIM)                       # sunlit deck edge
    rect(x0, y + 1, x1, y + 1, IR_4)
    rect(x0 - 1, y + tall, x1 + 1, y + tall, IR_0)  # underside lip
    for x in range(int(x0) + 2, int(x1) - 1, 3):   # lit windows / railing
        px(x, y + 3, LIT); px(x, y + 4, IR_3)
    px(x0, y + 2, LIT2); px(x1, y + 2, LIT2)
    # support brackets under deck
    for fx in (-.7, -.35, 0, .35, .7):
        line(CX + fx * halfw, y + tall, CX + fx * halfw * .7, y + tall + 4, IR_1, 1)

# upper + middle truss, then legs
truss_segment(34, 78, step=9)
truss_segment(86, 127, step=10)
leg_segment(136, 192)
platform(78, 25, tall=8)    # second floor
platform(127, 44, tall=9)   # first floor

# summit: cap, balcony, spire, beacon
rect(CX - 7, 27, CX + 7, 34, IR_1); rect(CX - 7, 27, CX + 7, 27, RIM)
for x in range(CX - 4, CX + 5, 3): px(x, 30, LIT)
rect(CX - 5, 22, CX + 5, 27, IR_2); rect(CX - 5, 22, CX + 5, 22, IR_5)
px(CX - 2, 24, LIT); px(CX + 2, 24, LIT)
line(CX, 22, CX, 10, IR_1, 2); line(CX - 1, 20, CX - 1, 12, RIM, 1)
px(CX, 9, BEACON); px(CX, 8, LIT2)
line(CX - 3, 17, CX + 3, 17, IR_1, 1)

# elevator shafts: bright vertical runs inside legs
for side in (-1, 1):
    pts = [(CX + side * (hw_at(y) - 6.5), y) for y in range(140, 192, 6)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(ax, ay, bx, by, IR_4, 1)
    ex, ey = pts[3]
    rect(ex - 1, ey - 1, ex + 1, ey + 1, LIT)  # elevator cab light

# sparkling lights along outer chords
for y in range(38, 190, 7):
    for side in (-1, 1):
        if (y // 7 + (side > 0)) % 2 == 0:
            px(CX + side * (hw_at(y) + 1), y, LIT2 if y % 21 == 0 else LIT)
for i, y in enumerate(range(44, 124, 11)):
    px(CX, y, LIT if i % 2 else LIT2)

# ---------- foreground trees, lamps, people ----------
def tree(cx, base_y, s):
    rect(cx - 1, base_y - int(3 * s), cx, base_y, TRUNK)
    r = random.Random(int(cx * 7 + base_y))
    for _ in range(int(7 * s)):
        bx = cx + r.uniform(-4.5, 4.5) * s; by = base_y - (4 + r.uniform(0, 5)) * s
        disc(bx, by, 2.6 * s, 2.2 * s, TREE_D)
    for _ in range(int(6 * s)):
        bx = cx + r.uniform(-4, 4) * s; by = base_y - (5 + r.uniform(0, 4.5)) * s
        disc(bx, by, 1.9 * s, 1.6 * s, TREE_M)
    for _ in range(int(9 * s)):
        px(cx + r.uniform(-4.5, 2) * s, base_y - (5 + r.uniform(0, 4.5)) * s,
           TREE_L if r.random() < .7 else TREE_H)

# rows along the path, shrinking to the tower
for t, s in [(0, .55), (.35, .85), (.7, 1.15), (1.0, 1.6)]:
    y = 193 + int(24 * t); off = 22 + 52 * t
    tree(int(CX - off), y, s); tree(int(CX + off), y, s)
# big framing trees in near corners
tree(10, 224, 3.1); tree(246, 224, 3.1); tree(28, 222, 2.2)

def lamp(cx, base_y, h):
    line(cx, base_y, cx, base_y - h, SIL, 1)
    disc(cx, base_y - h - 1, 2, 2, LAMP_H); px(cx, base_y - h - 1, LIT2)
    px(cx, base_y - h - 3, LAMP); px(cx - 2, base_y - h - 1, LAMP); px(cx + 2, base_y - h - 1, LAMP)

for t in (0, .45, .9):
    y = 196 + int(22 * t); off = 13 + 38 * t; h = int(5 + 6 * t)
    lamp(int(CX - off), y, h); lamp(int(CX + off), y, h)

# tiny strollers on the path
def person(cx, base_y, h):
    px(cx, base_y - h, SIL)                                  # head
    rect(cx - 1, base_y - h + 1, cx, base_y - h // 2, SIL)   # torso
    line(cx - 1, base_y - h // 2, cx - 1, base_y, SIL)       # legs
    line(cx, base_y - h // 2, cx + 1, base_y, SIL)
person(CX - 6, 214, 7); person(CX + 10, 208, 6); person(CX + 3, 221, 8); person(CX - 13, 204, 5)
person(CX - 4, 214, 7)  # companion

# ---------- enforce SNES tile rule: <=16 colors per 8x8 ----------
def nearest(c, choices):
    r, g, b = PAL[c]
    return min(choices, key=lambda k: (PAL[k][0]-r)**2 + (PAL[k][1]-g)**2 + (PAL[k][2]-b)**2)

for ty in range(0, H, 8):
    for tx in range(0, W, 8):
        cnt = Counter(img[y][x] for y in range(ty, min(ty+8, H)) for x in range(tx, min(tx+8, W)))
        if len(cnt) > 16:
            keep = [c for c, _ in cnt.most_common(16)]
            remap = {c: nearest(c, keep) for c in cnt if c not in keep}
            for y in range(ty, min(ty+8, H)):
                for x in range(tx, min(tx+8, W)):
                    if img[y][x] in remap: img[y][x] = remap[img[y][x]]

# verify constraints
used = sorted(set(v for row in img for v in row))
max_tile = 0
for ty in range(0, H, 8):
    for tx in range(0, W, 8):
        s = set(img[y][x] for y in range(ty, min(ty+8, H)) for x in range(tx, min(tx+8, W)))
        max_tile = max(max_tile, len(s))
print(f"size {W}x{H}  palette {len(PAL)}  colors used {len(used)}  max colors/8x8 tile {max_tile}")
assert len(used) <= 128 and max_tile <= 16

# ---------- write indexed PNG (stdlib) ----------
def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

plte = b"".join(struct.pack("BBB", *rgb) for rgb in PAL)
raw = b"".join(b"\x00" + bytes(row) for row in img)
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 3, 0, 0, 0))
       + chunk(b"PLTE", plte)
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))
os.makedirs("output", exist_ok=True)
with open("output/eiffel_tower_snes.png", "wb") as f:
    f.write(png)
print("wrote output/eiffel_tower_snes.png", len(png), "bytes")
