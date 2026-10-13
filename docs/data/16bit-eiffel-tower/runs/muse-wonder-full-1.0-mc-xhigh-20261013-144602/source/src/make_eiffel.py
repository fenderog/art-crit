#!/usr/bin/env python3
"""SNES-style Eiffel Tower pixel art, 256x224, <=128 colours, <=16 per 8x8 tile.
Pure standard library. Writes output/eiffel_tower_snes.png
"""
import zlib, struct, random, math, os

W, H = 256, 224
CX = 128

# ---------- palette ----------
def C(hexs):
    hexs = hexs.lstrip('#')
    return tuple(int(hexs[i:i+2], 16) for i in (0, 2, 4))

SKY = [C(c) for c in [
    "1B244C","232E5E","2F3A74","41468A","58509A","755AA0",
    "96659E","B87492","D68680","EE9C6E","F7B464","FCD47E",
]]
SUN_CORE = C("FDE9A8"); SUN_EDGE = C("FBCF7A"); SUN_GLOW = C("F2A878")
CLOUD_HI = C("F8D8C8"); CLOUD_MID = C("E8A89C"); CLOUD_SH = C("9A6A9A")
CLOUD_DK = C("6A5488")
STAR = C("FFF4D8")
FAR_CITY = C("5A4A6E"); FAR_ROOF = C("4A3A60")
NEAR_CITY = C("332845"); NEAR_ROOF = C("241C38")
WIN = C("F8D87A"); WIN2 = C("FFF0B0")
IRON_D = C("261A2A")     # near-black iron (silhouette)
IRON_M = C("4A3040")     # mid iron
IRON_L = C("7A4A3E")     # warm lit iron
RIM    = C("E89058")     # sunset rim light
LIGHT  = C("FFD76A"); LIGHT2 = C("FFF0A0")
DECK_HI = C("C88A5E")
GRASS_D = C("1D352B"); GRASS_M = C("234433"); GRASS_L = C("2E5A3E")
TREE_D = C("183626"); TREE_M = C("2A5C38"); TREE_L = C("5A9A4F"); TRUNK = C("2A1E22")
PATH_C = C("9A8560"); PATH_L = C("BFA678"); PATH_D = C("77653F")
BUSH = C("12261C")
LAMP = C("FFE9A0")

buf = [[SKY[0]]*W for _ in range(H)]

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        buf[y][x] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1+1):
        for x in range(x0, x1+1):
            px(x, y, c)

def hline(x0, x1, y, c, t=1):
    for yy in range(y, y+t):
        for x in range(min(x0,x1), max(x0,x1)+1):
            px(x, yy, c)

def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1-x0); dy = abs(y1-y0)
    sx = 1 if x1 >= x0 else -1; sy = 1 if y1 >= y0 else -1
    err = dx - dy; x, y = x0, y0
    r = t//2
    while True:
        for yy in range(y-r, y-r+t):
            for xx in range(x-r, x-r+t):
                px(xx, yy, c)
        if x == x1 and y == y1: break
        e2 = 2*err
        if e2 > -dy: err -= dy; x += sx
        if e2 < dx: err += dx; y += sy

def disc(cx, cy, rx, ry, c):
    for y in range(cy-ry, cy+ry+1):
        for x in range(cx-rx, cx+rx+1):
            if rx and ry and ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0:
                px(x, y, c)

rng = random.Random(1889)

# ---------- sky with dithered band transitions ----------
BAND = 14
BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
HORIZON = 190
for y in range(HORIZON):
    bi = min(y // BAND, len(SKY)-1)
    base = SKY[bi]
    # rows in last 5 of a band dither into next band
    into = y - bi*BAND
    nxt = SKY[bi+1] if bi+1 < len(SKY) else base
    for x in range(W):
        c = base
        if into >= BAND-5 and bi+1 < len(SKY):
            frac = (into-(BAND-5)+1) / 6.0   # ~0.16..0.83
            if BAYER[y % 4][x % 4] / 16.0 < frac:
                c = nxt
        buf[y][x] = c

# stars (upper sky only)
for _ in range(46):
    x = rng.randrange(2, W-2); y = rng.randrange(2, 58)
    if rng.random() < (58-y)/58:
        px(x, y, STAR)
        if rng.random() < 0.25:
            px(x+1, y, STAR)

# small crescent moon, top right
disc(224, 24, 7, 7, CLOUD_HI)
disc(228, 21, 6, 6, SKY[1])

# ---------- sun behind tower ----------
disc(CX, 112, 40, 40, SUN_GLOW)
disc(CX, 112, 36, 36, SUN_EDGE)
disc(CX, 112, 32, 32, SUN_CORE)
# ---------- clouds ----------
def cloud(cx, cy, w, main, hi, sh):
    # puffy cloud from overlapping circles of varied radius (bumpy top)
    s = w / 40.0
    blobs = [(-13, 2, 5), (-7, -2, 6), (0, -4, 7), (7, -2, 6), (13, 2, 5), (0, 3, 6)]
    blobs = [(int(dx*s), int(dy*s), max(2, int(r*s))) for dx, dy, r in blobs]
    for dx, dy, r in blobs:
        disc(cx+dx, cy+dy+2, r, r, sh)
    for dx, dy, r in blobs:
        disc(cx+dx, cy+dy, r, r, main)
    # short highlight ticks on the two tallest bumps only
    for dx, dy, r in (blobs[2], blobs[1]):
        for x in range(cx+dx-2, cx+dx+2):
            px(x, cy+dy-r, hi)
        px(cx+dx-1, cy+dy-r+1, hi)

cloud(40, 34, 38, CLOUD_DK, CLOUD_SH, C("4A4470"))
cloud(198, 48, 44, CLOUD_SH, CLOUD_MID, CLOUD_DK)
cloud(48, 82, 42, CLOUD_MID, CLOUD_HI, CLOUD_SH)
cloud(212, 100, 40, CLOUD_MID, CLOUD_HI, CLOUD_SH)
cloud(26, 124, 30, CLOUD_MID, CLOUD_HI, CLOUD_SH)
cloud(230, 134, 32, CLOUD_MID, CLOUD_HI, CLOUD_SH)

# birds (tiny "m" gulls)
for (bx, by) in [(58, 58), (68, 52), (190, 70), (200, 64), (84, 30)]:
    px(bx-2, by, IRON_D); px(bx-1, by-1, IRON_D); px(bx, by, IRON_D)
    px(bx+1, by-1, IRON_D); px(bx+2, by, IRON_D)

# ---------- Paris skyline (two silhouette layers) ----------
def skyline(base_y, col, roof, seed, min_h, max_h, windows):
    r = random.Random(seed)
    x = -4
    while x < W:
        bw = r.randrange(14, 30)
        bh = r.randrange(min_h, max_h)
        top = base_y - bh
        rect(x, top, x+bw, base_y, col)
        # mansard roof
        for i in range(3):
            hline(x+1+i, x+bw-1-i, top-1-i, roof)
        # chimney
        cx_ = x + r.randrange(3, max(4, bw-3))
        rect(cx_, top-6, cx_+2, top-2, col)
        if windows:
            for wy in range(top+4, base_y-2, 5):
                for wx in range(x+3, x+bw-2, 5):
                    if r.random() < 0.32:
                        px(wx, wy, WIN); px(wx, wy+1, WIN)
        x += bw + r.randrange(1, 4)

skyline(HORIZON, FAR_CITY, FAR_ROOF, 7, 14, 26, False)
skyline(HORIZON, NEAR_CITY, NEAR_ROOF, 21, 6, 15, True)
# a dome (Invalides-like) on the left, small church spire right
disc(28, 172, 7, 6, NEAR_CITY); rect(21, 172, 35, HORIZON, NEAR_CITY)
line(28, 158, 28, 168, NEAR_CITY, 2); px(28, 157, WIN2)
for i in range(9):
    hline(236+i//2, 244-i//2, 162+i, NEAR_CITY)
rect(235, 171, 245, HORIZON, NEAR_CITY)

# ---------- Eiffel Tower ----------
BASE_Y, TOP_Y = 190, 34
def outer_hw(y):
    t = (BASE_Y - y) / (BASE_Y - TOP_Y)
    t = max(0.0, min(1.0, t))
    return 3 + 55 * ((1-t) ** 1.3)

def inner_hw(y):
    s = (y - 134) / (BASE_Y - 134)
    s = max(0.0, min(1.0, s))
    return 21 + 17 * (s ** 0.9)

def pillar(points, t, c):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), c, t)

def outer_points(y0, y1, side):
    return [(CX + side*outer_hw(y), y) for y in range(y0, y1+1, 4)]

# levels (girder rows) for the two enclosed sections
UPPER = [36, 47, 58, 69, 80]          # top section -> 2nd platform
MIDDLE = [84, 95, 106, 117, 128]      # 2nd platform -> 1st platform

def truss_section(levels, double=False):
    # X-braces between consecutive levels
    for ya, yb in zip(levels, levels[1:]):
        la, ra = CX-outer_hw(ya), CX+outer_hw(ya)
        lb, rb = CX-outer_hw(yb), CX+outer_hw(yb)
        if double:
            line(int(la), ya, CX, yb, IRON_D, 2); line(CX, ya, int(lb), yb, IRON_D, 2)
            line(CX, ya, int(rb), yb, IRON_D, 2); line(int(ra), ya, CX, yb, IRON_D, 2)
            line(CX, ya, CX, yb, IRON_M, 2)
        else:
            line(int(la), ya, int(rb), yb, IRON_D, 2)
            line(int(ra), ya, int(lb), yb, IRON_D, 2)
            line(CX, ya, CX, yb, IRON_M, 1)
    # horizontal girders
    for y in levels:
        hw = outer_hw(y)
        hline(int(CX-hw), int(CX+hw), y, IRON_L, 1)
        hline(int(CX-hw), int(CX+hw), y+1, IRON_D, 2)

truss_section(UPPER, double=False)
truss_section(MIDDLE, double=True)

# legs: outer + inner pillars, rungs and X-braces within each leg
LEG_LEVELS = [134, 145, 156, 167, 178, 189]
for side in (-1, 1):
    for ya, yb in zip(LEG_LEVELS, LEG_LEVELS[1:]):
        oa, ia = CX+side*outer_hw(ya), CX+side*inner_hw(ya)
        ob, ib = CX+side*outer_hw(yb), CX+side*inner_hw(yb)
        line(int(oa), ya, int(ib), yb, IRON_D, 2)
        line(int(ia), ya, int(ob), yb, IRON_D, 2)
    for y in LEG_LEVELS:
        o, i = CX+side*outer_hw(y), CX+side*inner_hw(y)
        line(int(o), y, int(i), y, IRON_D, 2)
        line(int(o), y-1, int(i), y-1, IRON_L, 1)

# outer pillars over everything (crisp silhouette edge), tapering
for side in (-1, 1):
    pillar(outer_points(TOP_Y, 80, side), 3, IRON_D)
    pillar(outer_points(80, 128, side), 3, IRON_D)
    pillar(outer_points(128, BASE_Y, side), 4, IRON_D)
    # inner leg pillars
    pts = [(CX + side*inner_hw(y), y) for y in range(134, BASE_Y+1, 4)]
    pillar(pts, 3, IRON_D)
    # sunset rim light on the sun-facing (inner) edge of outer pillars
    rim_pts = [(CX + side*(outer_hw(y)-2), y) for y in range(TOP_Y, BASE_Y, 3)]
    pillar(rim_pts, 1, IRON_M)
    # warm rim on outer edge, upper part only (against sky)
    rim2 = [(CX + side*(outer_hw(y)+1), y) for y in range(TOP_Y, 120, 3)]
    pillar(rim2, 1, RIM)

# decorative arch between the legs
arch_pts = []
for a in range(0, 181, 6):
    rad = math.radians(a)
    x = CX - 33*math.cos(rad)
    y = 172 - 26*math.sin(rad)
    arch_pts.append((x, y))
pillar(arch_pts, 3, IRON_D)
arch_hi = [(x, y-2) for x, y in arch_pts]
pillar(arch_hi, 1, IRON_L)
# small radial spokes above arch
for a in range(20, 170, 22):
    rad = math.radians(a)
    x0 = CX - 33*math.cos(rad); y0 = 172 - 26*math.sin(rad)
    x1 = CX - 27*math.cos(rad); y1 = 172 - 31*math.sin(rad)
    line(int(x0), int(y0), int(x1), int(y1), IRON_D, 1)

# feet / foundation pads
for side in (-1, 1):
    o = int(CX + side*outer_hw(BASE_Y)); i = int(CX + side*inner_hw(BASE_Y))
    rect(min(o, i)-1, BASE_Y-1, max(o, i)+1, BASE_Y+1, IRON_D)
    hline(min(o, i)-1, max(o, i)+1, BASE_Y-1, IRON_L)

def platform(cy, extra, deck_h, windows=True):
    hw = outer_hw(cy) + extra
    x0, x1 = int(CX-hw), int(CX+hw)
    # railing
    for x in range(x0+1, x1, 3):
        px(x, cy-deck_h-2, IRON_D)
    hline(x0, x1, cy-deck_h-3, IRON_D, 1)
    # deck
    rect(x0, cy-deck_h, x1, cy+deck_h, IRON_D)
    hline(x0, x1, cy-deck_h, DECK_HI, 1)
    hline(x0, x1, cy-deck_h+1, IRON_L, 1)
    hline(x0-1, x1+1, cy+deck_h+1, IRON_D, 1)
    if windows:
        for x in range(x0+3, x1-2, 4):
            px(x, cy, WIN2); px(x+1, cy, WIN)
    # support brackets
    line(x0+2, cy+deck_h+1, int(CX-outer_hw(cy+8)), cy+8, IRON_D, 2)
    line(x1-2, cy+deck_h+1, int(CX+outer_hw(cy+8)), cy+8, IRON_D, 2)

platform(82, 8, 3)     # second floor
platform(130, 8, 4)    # first floor

# summit: cupola + spire + beacon
for y in range(23, 36):
    hw = {23:1,24:2,25:3,26:4,27:4,28:4,29:3,30:3,31:4,32:5,33:5,34:6,35:6}[y]
    hline(CX-hw, CX+hw, y, IRON_D)
hline(CX-6, CX+6, 35, DECK_HI, 1)
px(CX, 27, WIN2); px(CX, 28, WIN); px(CX-2, 27, WIN); px(CX+2, 27, WIN)
line(CX, 12, CX, 23, IRON_D, 1)
line(CX-1, 16, CX+1, 16, IRON_D, 1)
px(CX, 11, LIGHT2); px(CX, 10, LIGHT2)
px(CX-1, 11, LIGHT); px(CX+1, 11, LIGHT); px(CX, 12, LIGHT)

# golden floodlights dotted along outer pillars + arch
for y in range(38, BASE_Y-2, 7):
    for side in (-1, 1):
        x = int(CX + side*(outer_hw(y)-1))
        px(x, y, LIGHT)
        if y % 14 == 3:
            px(x, y+1, LIGHT2)
for a in range(10, 175, 14):
    rad = math.radians(a)
    px(int(CX-33*math.cos(rad)), int(172-26*math.sin(rad)), LIGHT)

# ---------- ground: Champ de Mars ----------
for y in range(HORIZON, H):
    for x in range(W):
        buf[y][x] = GRASS_L if ((x+y)//14) % 2 == 0 else GRASS_M
    if y > 212:
        for x in range(W):
            if (x+y) % 2 == 0:
                buf[y][x] = GRASS_D
# central path (perspective trapezoid)
for y in range(HORIZON-1, H):
    t = (y-(HORIZON-1)) / (H-HORIZON+1)
    hw = 11 + 22*t
    for x in range(int(CX-hw), int(CX+hw)+1):
        c = PATH_C
        if (y % 9) < 1 and (x+y) % 3: c = PATH_D
        if rng.random() < 0.04: c = PATH_L
        px(x, y, c)
    px(int(CX-hw), y, PATH_L); px(int(CX+hw), y, PATH_L)
    px(int(CX-hw)-1, y, GRASS_D); px(int(CX+hw)+1, y, GRASS_D)

def tree(cx, gy, r):
    # layered round canopy from overlapping circles; gy = ground line
    hline(cx-r, cx+r, gy+1, GRASS_D, 1)
    rect(cx-1, gy-4, cx, gy, TRUNK)
    cy = gy - r - 3
    disc(cx-r//2, cy+2, max(r*3//4, 2), max(r*3//4, 2), TREE_D)
    disc(cx+r//2, cy+2, max(r*3//4, 2), max(r*3//4, 2), TREE_D)
    disc(cx, cy, r, r, TREE_D)
    disc(cx-1, cy-1, max(r-2, 2), max(r-2, 2), TREE_M)
    px(cx-r//2, cy-r+1, TREE_L); px(cx-1, cy-r, TREE_L); px(cx+1, cy-r+2, TREE_L)
    px(cx-r+2, cy-1, TREE_L)

# small trees near horizon flanking the tower, larger toward viewer
for (tx, ty, tr) in [(52,193,4),(202,193,4),(38,199,5),(216,199,5),
                     (64,203,5),(190,203,5),(22,213,7),(232,213,7),
                     (78,215,6),(176,215,6)]:
    tree(tx, ty, tr)

# lampposts along the path
for (lx, ly, lh) in [(96,198,9),(158,198,9),(92,214,12),(162,214,12),(106,191,6),(148,191,6)]:
    line(lx, ly-lh, lx, ly, IRON_D, 1)
    px(lx, ly-lh-1, LAMP); px(lx, ly-lh-2, LAMP)
    px(lx-1, ly-lh-1, WIN); px(lx+1, ly-lh-1, WIN)

# tiny strollers on the path
def person(x, y, shirt):
    px(x, y-4, C("E8B88A")); px(x, y-3, shirt); px(x, y-2, shirt)
    px(x, y-1, IRON_D); px(x+ (1 if y % 2 else -1), y, IRON_D)
person(120, 205, C("C84A5A")); person(138, 213, C("4A7AC8")); person(124, 195, C("E8E0C8"))

# foreground bushes framing bottom corners (scalloped, low)
for (bx, by, br) in [(2,224,11),(20,225,9),(253,224,11),(235,225,9),(10,220,7),(245,220,7)]:
    disc(bx, by, br, br//2+2, BUSH)
    disc(bx-br//3, by-br//3, max(br//2,1), max(br//3,1), TREE_D)
    px(bx-br//3, by-br//2, TREE_M); px(bx+2, by-br//2+1, TREE_M)

# ---------- verify SNES limits ----------
colours = set()
max_tile = 0; worst = None
for ty in range(0, H, 8):
    for tx in range(0, W, 8):
        s = set()
        for y in range(ty, ty+8):
            for x in range(tx, tx+8):
                s.add(buf[y][x]); colours.add(buf[y][x])
        if len(s) > max_tile:
            max_tile = len(s); worst = (tx, ty, sorted(s))
print(f"size {W}x{H}  total colours {len(colours)}  max colours in an 8x8 tile {max_tile}")
assert len(colours) <= 128, "too many colours"
assert max_tile <= 16, f"tile at {worst[:2]} has {max_tile} colours"

# ---------- write PNG (RGB, no filtering tricks) ----------
def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return c

raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in buf)
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))
os.makedirs("output", exist_ok=True)
with open("output/eiffel_tower_snes.png", "wb") as f:
    f.write(png)
print("wrote output/eiffel_tower_snes.png", len(png), "bytes")
