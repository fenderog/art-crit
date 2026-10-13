#!/usr/bin/env python3
"""
SNES Eiffel Tower pixel art generator
- 256x224, no scaling
- <=128 colours total, <=16 colours per 8x8 tile (verified at the end)
- Pure stdlib: writes PNG via zlib/struct
"""
import zlib, struct, random, math, os

W, H = 256, 224
CX = 128

def C(h):
    h = h.lstrip('#')
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

# ---------------- palette ----------------
SKY = [C(x) for x in [
    "#232A5C","#2E3468","#3B3A72","#4B447C","#624F82","#7E5E88",
    "#9D6E8C","#BF7E8A","#DE8F7E","#F2A46B","#FDBE71","#FFD98C"]]
SUN_CORE, SUN_MID, SUN_HALO = C("#FFF3B0"), C("#FFE29A"), C("#FFC98A")
CLOUD_TOP, CLOUD_MID, CLOUD_SH = C("#FFF0DC"), C("#FFC9AF"), C("#DE93A6")
CLOUD_FAR = C("#D99DB0")
STAR = C("#FFEFD0")
BIRD = C("#2E2440")

IRON_D = C("#261827")   # outline / deepest iron
IRON   = C("#3A2436")   # main iron
IRON_M = C("#57313E")   # mid iron
IRON_L = C("#7E4A3E")   # warm side
IRON_H = C("#C67F4E")   # sunlit edge
LIT, LIT2 = C("#FFD86B"), C("#FFF1A0")
BEACON = C("#FF6B5E")
FLAG_B, FLAG_W, FLAG_R = C("#3A5FB5"), C("#FFF4E0"), C("#D94F5A")

BLD_FAR = C("#51466E")
ROOF_FAR = C("#3A3560")
BLD_A, ROOF_A = C("#8A6B7E"), C("#403A66")
BLD_B, ROOF_B = C("#6E5574"), C("#332F58")
BLD_SH = C("#4A3A5E")
WIN_D = C("#3E3456")

TREE_D, TREE_M, TREE_L, TREE_H = C("#1E4228"), C("#2C5C30"), C("#437A36"), C("#6CA848")
TRUNK = C("#3A2733")
LAWN, LAWN_D, LAWN_L, LAWN_M = C("#2F7036"), C("#265C2E"), C("#4C9040"), C("#3A7F38")
HEDGE, HEDGE_L = C("#1C4526"), C("#356F32")
PATH, PATH_D, PATH_L = C("#E9CB9A"), C("#C7A678"), C("#F7E3B8")
PLAZA, PLAZA_D = C("#DCC096"), C("#B99B72")
SOIL = C("#4A3040")
FLOWERS = [C("#E85D75"), C("#FFD23F"), C("#FF8A5C"), C("#F2F0FF")]
POST = C("#1E182C")
GLOW = C("#FFE98A")
SHADOW = C("#20482A")  # ground shadow on lawn
PATH_SH = C("#B99B72")

PEOPLE = [(C("#D94F4F"), C("#F2C99A")), (C("#3A7BD5"), C("#8A5A3C")),
          (C("#FFD23F"), C("#F2C99A")), (C("#7A4FA3"), C("#6B4232"))]

# ---------------- framebuffer ----------------
fb = [[SKY[0] for _ in range(W)] for _ in range(H)]
rng = random.Random(1624)

def px(x,y,c):
    if 0 <= x < W and 0 <= y < H:
        fb[int(y)][int(x)] = c

def rect(x,y,w,h,c):
    for yy in range(int(y), int(y+h)):
        for xx in range(int(x), int(x+w)):
            px(xx,yy,c)

def hline(x,y,w,c):
    for xx in range(int(x), int(x+w)): px(xx,y,c)
def vline(x,y,h,c):
    for yy in range(int(y), int(y+h)): px(x,yy,c)

def line(x0,y0,x1,y1,c,thick=1):
    dx, dy = abs(x1-x0), -abs(y1-y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x,y = x0,y0
    off = thick//2
    while True:
        for a in range(-off, thick-off):
            for b in range(-off, thick-off):
                # round-ish stamp for thick lines
                if thick <= 2 or a*a+b*b <= off*off+1:
                    px(x+a,y+b,c)
        if x==x1 and y==y1: break
        e2 = 2*err
        if e2 >= dy: err += dy; x += sx
        if e2 <= dx: err += dx; y += sy

def ellipse(cx,cy,rx,ry,c):
    for yy in range(int(cy-ry), int(cy+ry+1)):
        for xx in range(int(cx-rx), int(cx+rx+1)):
            if rx and ry and ((xx-cx)/rx)**2 + ((yy-cy)/ry)**2 <= 1.0:
                px(xx,yy,c)

def circle(cx,cy,r,c): ellipse(cx,cy,r,r*0.92,c)

BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

# ---------------- sky ----------------
def draw_sky():
    n = len(SKY)
    for y in range(152):
        t = y/151 * (n-1)
        i = int(t); f = t-i
        for x in range(W):
            if i >= n-1:
                c = SKY[-1]
            elif f > 0.55 and (BAYER[y%4][x%4]/16.0) < (f-0.55)/0.45:
                c = SKY[i+1]
            else:
                c = SKY[i]
            fb[y][x] = c
    # faint stars in upper sky
    for _ in range(38):
        x = rng.randrange(W); y = rng.randrange(0,44)
        if rng.random() < 0.8: px(x,y,STAR)
        else:
            px(x,y,STAR); px(x+1,y,STAR); px(x,y-1,STAR); px(x,y+1,STAR)

def draw_sun():
    cx, cy, r = 198, 46, 17
    # halo, dithered ring
    for yy in range(cy-24, cy+25):
        for xx in range(cx-24, cx+25):
            d = math.hypot(xx-cx, (yy-cy)*1.05)
            if r < d < 23 and (BAYER[yy%4][xx%4] < 6):
                px(xx,yy,SUN_HALO)
    circle(cx,cy,r,SUN_MID)
    circle(cx,cy,r-5,SUN_CORE)
    # SNES banding on sun
    for yy in (cy+9, cy+12):
        hline(cx-r+3, yy, 2*r-6, SUN_MID)

def cloud(cx,cy,s,c_top,c_mid,c_sh,far=False):
    # blocky flat-bottom cloud made of stacked stepped ellipses
    ellipse(cx,cy,16*s,5*s,c_mid)
    ellipse(cx-10*s,cy+1*s,9*s,4*s,c_mid)
    ellipse(cx+11*s,cy+1*s,10*s,4*s,c_mid)
    ellipse(cx-4*s,cy-2*s,10*s,4*s,c_top)
    ellipse(cx+5*s,cy-3*s,7*s,3*s,c_top)
    if not far:
        hline(cx-13*s,cy+3*s,26*s,c_sh)
        hline(cx-8*s,cy+4*s,16*s,c_sh)
        for x in range(int(cx-12*s), int(cx+13*s), 4):
            px(x,cy-4*s,c_top)

def draw_clouds():
    cloud(46,34,1,CLOUD_TOP,CLOUD_MID,CLOUD_SH)
    cloud(214,84,1,CLOUD_TOP,CLOUD_MID,CLOUD_SH)
    cloud(78,92,0,CLOUD_TOP,CLOUD_MID,CLOUD_SH)  # scaled below via s=1 small handled separately
    # far small clouds (pink silhouettes)
    for (x,y,w) in [(18,64,22),(150,24,18),(104,58,16),(232,120,20),(36,116,18)]:
        ellipse(x,y,w,3,CLOUD_FAR)
        ellipse(x-4,y-2,w//2,2,CLOUD_FAR)
        hline(x-w+2,y+3,w*2-4,CLOUD_FAR)

def draw_birds():
    for (x,y,s) in [(58,52,1),(72,44,1),(166,30,1),(92,66,0),(182,64,0)]:
        if s:
            px(x-3,y,BIRD); px(x-2,y-1,BIRD); px(x-1,y,BIRD)
            px(x+1,y,BIRD); px(x+2,y-1,BIRD); px(x+3,y,BIRD); px(x,y,BIRD)
        else:
            px(x-2,y-1,BIRD); px(x-1,y,BIRD); px(x+1,y,BIRD); px(x+2,y-1,BIRD)

# ---------------- skyline ----------------
def building(x, base, w, h, roof_h, wall, roof, lit_prob=0.35):
    rect(x, base-h, w, h, wall)
    # mansard roof: stepped trapezoid
    for i in range(roof_h):
        inset = int(i * (w*0.18) / max(1,roof_h))
        rect(x+inset, base-h-roof_h+i, w-2*inset, 1, roof)
    # chimney
    rect(x+w//3, base-h-roof_h-3, 3, 3, roof)
    px(x+w//3, base-h-roof_h-4, roof)
    # side shade
    rect(x+w-3, base-h, 3, h, BLD_SH if wall != BLD_FAR else ROOF_FAR)
    # windows
    for wy in range(base-h+5, base-4, 7):
        for wx in range(x+3, x+w-4, 6):
            c = LIT if rng.random() < lit_prob else WIN_D
            rect(wx,wy,2,3,c)

def draw_skyline():
    # far layer
    for (x,w,h) in [(0,30,20),(28,26,26),(52,22,18),(176,24,22),(198,30,18),(226,30,24)]:
        building(x,152,w,h,5,BLD_FAR,ROOF_FAR,0.15)
    # Les Invalides dome, left distance
    rect(96,140,16,12,BLD_FAR); rect(99,132,10,8,ROOF_FAR)
    ellipse(104,132,6,4,ROOF_FAR); vline(104,124,5,ROOF_FAR); px(104,123,LIT)
    # near layer left / right
    building(2,154,34,30,7,BLD_A,ROOF_A)
    building(34,154,28,24,6,BLD_B,ROOF_B)
    building(196,154,30,27,6,BLD_B,ROOF_B)
    building(224,154,32,32,7,BLD_A,ROOF_A)
    building(62,153,20,17,5,BLD_B,ROOF_B,0.25)
    building(176,153,20,16,5,BLD_A,ROOF_A,0.25)

# ---------------- ground / gardens ----------------
def draw_ground():
    rect(0,152,W,72,LAWN)
    # mow stripes (horizontal, subtle)
    for i,y in enumerate(range(152,224,9)):
        if i % 2 == 0: rect(0,y,W,9,LAWN_M)
    # distant tree line
    for x in range(-4, W, 10):
        if 78 < x < 180:  # behind plaza, sparser
            if x % 20: continue
        circle(x+4,149,6,TREE_D); circle(x+2,147,4,TREE_M)
    # plaza under tower (trapezoid)
    for y in range(164,186):
        t = (y-164)/21
        hw = int(56 + 14*t)
        hline(CX-hw,y,2*hw, PLAZA if (y//3)%2 else PLAZA_D)
        px(CX-hw,y,PLAZA_D); px(CX+hw-1,y,PLAZA_D)
    # central path to viewer
    for y in range(182,224):
        t = (y-182)/41
        hw = int(13 + 17*t)
        hline(CX-hw,y,2*hw, PATH)
        # edge + hedge shadow
        px(CX-hw,y,PATH_D); px(CX-hw-1,y,HEDGE); px(CX-hw-2,y,HEDGE)
        px(CX+hw-1,y,PATH_D); px(CX+hw,y,HEDGE); px(CX+hw+1,y,HEDGE)
        px(CX-hw-2,y+0,HEDGE)
    # diagonal garden hedges
    line(70,186,22,222,HEDGE,2); line(186,186,234,222,HEDGE,2)
    line(72,184,24,220,HEDGE_L,1)
    # cobble / lawn speckle (deterministic, sparse)
    for _ in range(420):
        x = rng.randrange(W); y = rng.randrange(154,224)
        # keep off path centre mostly by colour choice below
        c = LAWN_D if rng.random()<0.6 else LAWN_L
        px(x,y,c)
    for _ in range(90):
        x = rng.randrange(W); y = rng.randrange(164,224)
        px(x,y,PATH_D if rng.random()<0.7 else PATH_L)
    # flower beds flanking path
    for (x0,x1) in [(78,108),(148,178)]:
        for y in range(198,212):
            t=(y-198)/13
            xa = int(x0-6*t); xb = int(x1+2*t)
            hline(xa,y,xb-xa,SOIL)
        for _ in range(46):
            x = rng.randrange(x0-4,x1+4); y = rng.randrange(199,211)
            px(x,y,rng.choice(FLOWERS))

def tree(x, base, s):
    """s ~ canopy radius"""
    rect(x-1, base-s-2, 2, s+2, TRUNK)
    circle(x, base-s-4, s, TREE_D)
    circle(x-s//2, base-s-6, s*2//3, TREE_M)
    circle(x+s//3, base-s-8, s//2, TREE_M)
    for _ in range(s*2):
        px(x+rng.randrange(-s,s), base-s-4+rng.randrange(-s//2,s//2), TREE_L)
    for _ in range(max(2,s//2)):
        px(x+rng.randrange(0,s), base-s-6+rng.randrange(-3,2), TREE_H)
    ellipse(x, base+1, s//2+2, 1, SHADOW)

def lamp(x, base, h):
    top = base-h
    vline(x, top+6, h-6, POST); vline(x-1, top+6, h-6, POST)
    hline(x-3, top+5, 7, POST)
    # lantern
    rect(x-3, top, 7, 6, POST)
    rect(x-2, top+1, 5, 4, GLOW)
    px(x, top+2, LIT2)
    # halo pixels
    for (dx,dy) in [(-5,2),(5,2),(0,-3),(-4,-1),(4,-1)]:
        px(x+dx, top+dy, GLOW)
    ellipse(x, base+1, 5, 1, SHADOW if base>190 else PATH_SH)

def people():
    def person(x,y,h,shirt,skin):
        head = max(1,h//6)
        rect(x, y-h, 2, head+1, skin)
        rect(x-1, y-h+head+1, 4, h//3, shirt)
        rect(x-1, y-h//3, 2, h//3, POST); rect(x+1, y-h//3, 2, h//3, POST)
        ellipse(x, y+1, 4, 1, PATH_SH)
    person(112,204,10,*PEOPLE[0])
    person(118,206,8,*PEOPLE[1])
    person(142,196,7,*PEOPLE[2])
    person(96,186,6,*PEOPLE[3])
    person(158,214,11,*PEOPLE[1])
    person(104,220,12,*PEOPLE[0])

# ---------------- Eiffel Tower ----------------
HW_PTS = [(12,1),(18,3),(26,4),(34,6),(48,9),(64,12),(70,14),(78,16),
          (92,20),(108,25),(116,28),(124,31),(140,38),(156,46),(172,54),(180,55)]
def hw(y):
    if y <= HW_PTS[0][0]: return HW_PTS[0][1]
    for (y0,h0),(y1,h1) in zip(HW_PTS, HW_PTS[1:]):
        if y0 <= y <= y1:
            return h0 + (h1-h0)*(y-y0)/(y1-y0)
    return HW_PTS[-1][1]

def inner_hw(y):
    pts = [(120,18),(135,20),(150,23),(165,26),(180,29)]
    for (y0,h0),(y1,h1) in zip(pts, pts[1:]):
        if y0 <= y <= y1: return h0 + (h1-h0)*(y-y0)/(y1-y0)
    return pts[-1][1]

def deck(y, half, label_h=6):
    # railing
    hline(CX-half, y-4, 2*half, IRON_D)
    for x in range(CX-half, CX+half, 4): vline(x, y-4, 4, IRON_D)
    # body
    rect(CX-half-2, y, 2*half+4, label_h, IRON)
    hline(CX-half-2, y, 2*half+4, IRON_H)
    hline(CX-half-2, y+label_h-1, 2*half+4, IRON_D)
    # lit gallery windows
    for x in range(CX-half, CX+half-1, 4):
        rect(x, y+2, 2, 2, LIT)
    px(CX-half-2, y+2, IRON_D); px(CX+half+1, y+2, IRON_D)

def draw_tower():
    # ---- upper solid-ish lattice: edges + horizontals + diagonals only
    horiz = [30,40,50,60, 76,86,96,106]
    # diagonals per panel
    panels = [(26,66),(74,112)]
    for (y0,y1) in panels:
        steps = 4 if y1-y0>35 else 4
        sub = (y1-y0)/steps
        for i in range(steps):
            ya = int(y0+i*sub); yb = int(y0+(i+1)*sub)
            line(int(CX-hw(ya)),ya, int(CX+hw(yb)),yb, IRON_M,1)
            line(int(CX+hw(ya)),ya, int(CX-hw(yb)),yb, IRON_M,1)
    # horizontals
    for y in horiz:
        w_ = int(hw(y))
        hline(CX-w_, y, 2*w_, IRON_D); hline(CX-w_, y-1, 2*w_, IRON)
    # edge beams (drawn last within lattice so silhouette is crisp)
    for y in range(24, 114):
        w_ = hw(y)
        lx, rx = int(CX-w_), int(CX+w_)
        px(lx,y,IRON_D); px(lx+1,y,IRON); px(lx+2,y,IRON_M)
        px(rx,y,IRON_D); px(rx-1,y,IRON_H); px(rx-2,y,IRON_L)
    # central elevator shaft
    for y in range(28,112):
        px(CX-1,y,IRON); px(CX,y,IRON_D)
    for y in range(34,112,12): px(CX,y,LIT)

    # summit
    rect(CX-4,20,9,7,IRON); rect(CX-4,20,9,2,IRON_M)
    for x in range(CX-3,CX+4,3): px(x,23,LIT)
    line(CX-6,27,CX-4,20,IRON_D,1); line(CX+6,27,CX+4,20,IRON_D,1)
    # antenna + flag + beacon
    vline(CX,8,13,IRON_D)
    # tricolore flag flying right
    for i,col in enumerate([FLAG_B,FLAG_W,FLAG_R]):
        rect(CX+1+i*2, 9, 2, 4, col)
    px(CX+7,10,FLAG_R)
    px(CX,6,BEACON); px(CX-1,7,BEACON); px(CX+1,7,BEACON); px(CX,7,LIT2); px(CX,8,BEACON)

    # decks
    deck(66, 16, 6)    # second floor
    deck(112, 31, 7)   # first floor

    # ---- legs below first floor (y 119..180)
    leg_panels = [122,134,146,158,170]
    for side in (-1,1):
        for y0,y1 in zip(leg_panels, leg_panels[1:]):
            ox0, ix0 = CX+side*hw(y0), CX+side*inner_hw(y0)
            ox1, ix1 = CX+side*hw(y1), CX+side*inner_hw(y1)
            line(int(ox0),y0,int(ix1),y1,IRON_M,1)
            line(int(ix0),y0,int(ox1),y1,IRON_M,1)
        # cross horizontals
        for y in leg_panels:
            ox, ix = CX+side*hw(y), CX+side*inner_hw(y)
            x0,x1 = (int(ix),int(ox)) if side>0 else (int(ox),int(ix))
            hline(x0,y,x1-x0,IRON_D)
    for y in range(119,181):
        wo, wi = hw(y), inner_hw(y)
        for side in (-1,1):
            ox = int(CX+side*wo); ix = int(CX+side*wi)
            # outer beam 3px, inner beam 3px (toward centre)
            for d in range(3):
                px(ox - side*d, y, IRON_D if d==0 else IRON)
                px(ix + side*d, y, IRON_D if d==0 else IRON)
            if side>0:
                px(ox,y,IRON_H); px(ox-1,y,IRON_L)
    # decorative arch between legs
    for dx in range(-28,29):
        ya = int(149 - 16*(1-(dx/28)**2))
        for t in range(4):
            px(CX+dx, ya+t, IRON_D if t in (0,3) else IRON)
        px(CX+dx, ya-1, IRON_H)
    # feet / piles
    for side in (-1,1):
        ox = int(CX+side*hw(176)); ix = int(CX+side*inner_hw(176))
        x0,x1 = (ix,ox) if side>0 else (ox,ix)
        rect(int(x0)-2,176,int(x1-x0)+4,6,IRON)
        hline(int(x0)-2,176,int(x1-x0)+4,IRON_H)
        rect(int(x0)-3,181,int(x1-x0)+6,3,IRON_D)
    # sparkle lights up both edges
    for y in range(30,172,9):
        w_ = int(hw(y))
        px(CX-w_+3, y, LIT); px(CX+w_-3, y, LIT)
        if y % 18 == 0: px(CX-w_+3, y-1, LIT2); px(CX+w_-3, y-1, LIT2)
    for x in range(CX-30, CX+31, 6):
        px(x, 110, LIT2)

# ---------------- compose ----------------
draw_sky()
draw_sun()
draw_clouds()
draw_birds()
draw_skyline()
draw_ground()
# midground trees + lamps (behind tower feet line visually, drawn before tower)
for (x,b,s) in [(52,168,9),(84,172,11),(172,172,11),(204,168,9),(30,182,12),(226,182,12)]:
    tree(x,b,s)
draw_tower()
# foreground garden trees, lamps, people
for (x,b,s) in [(36,214,14),(220,214,14)]:
    tree(x,b,s)
lamp(70,196,26); lamp(186,196,26)
lamp(88,172,16); lamp(168,172,16)
people()
lamp(18,224,46); lamp(238,224,46)

# ---------------- verify constraints & write PNG ----------------
colours = set()
for row in fb: colours.update(row)
max_tile = 0; worst=None
for ty in range(0,H,8):
    for tx in range(0,W,8):
        s = {fb[y][x] for y in range(ty,min(ty+8,H)) for x in range(tx,min(tx+8,W))}
        if len(s) > max_tile: max_tile, worst = len(s), (tx,ty,s)
print(f"colours total: {len(colours)} (limit 128)")
print(f"max colours in any 8x8 tile: {max_tile} (limit 16) worst={worst[0:2] if worst else None}")
assert len(colours) <= 128, "too many colours"
assert max_tile <= 16, f"tile too colourful: {worst}"

os.makedirs("output", exist_ok=True)
raw = b"".join(b"\x00" + bytes([v for pix in row for v in pix]) for row in fb)
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ+data) & 0xffffffff)
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W,H,8,2,0,0,0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))
out = "output/eiffel_snes.png"
with open(out,"wb") as f: f.write(png)
print(f"wrote {out} {len(png)} bytes  {W}x{H}")
