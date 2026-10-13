#!/usr/bin/env python3
"""SNES-style Eiffel Tower, 256x224, procedural pixel art (stdlib only)."""
import struct, zlib, math, random

W, H = 256, 224
random.seed(12)

# Palette (SNES-friendly, limited)
P = {
 'sky0':(32,32,88),'sky1':(56,56,128),'sky2':(88,88,168),'sky3':(128,120,192),
 'sky4':(200,128,168),'sky5':(248,168,120),'sky6':(255,200,128),'sun':(255,232,168),
 'cloud_d':(120,96,160),'cloud_m':(216,160,168),'cloud_l':(255,216,184),'cloud_w':(255,240,216),
 'far':(72,64,112),'far2':(96,80,128),'roof':(64,56,96),'win':(255,216,128),
 'iron_d':(24,20,40),'iron':(48,40,72),'iron_m':(80,72,104),'iron_l':(136,120,152),
 'iron_w':(192,176,184),'rust':(128,80,72),'gold':(255,200,96),'gold_l':(255,240,176),
 'grass_d':(24,56,40),'grass':(40,88,56),'grass_l':(72,128,72),'path':(200,168,128),
 'path_d':(168,136,104),'tree_d':(16,40,32),'tree':(32,72,48),'tree_l':(64,112,64),
 'trunk':(56,40,32),'white':(255,248,232),'black':(16,16,32),
 'water':(56,80,144),'water_l':(104,136,200),
}
buf = [[P['sky0']]*W for _ in range(H)]
def px(x,y,c):
    if 0<=x<W and 0<=y<H: buf[y][x]=P[c] if isinstance(c,str) else c
def rect(x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): px(x,y,c)
def hline(x0,x1,y,c):
    for x in range(x0,x1+1): px(x,y,c)
def vline(x,y0,y1,c):
    for y in range(y0,y1+1): px(x,y,c)

# --- sky: banded gradient with ordered dithering ---
sky_bands=[P['sky0'],P['sky1'],P['sky2'],P['sky3'],P['sky4'],P['sky5'],P['sky6']]
for y in range(0,176):
    t=y/175
    f=t*(len(sky_bands)-1)
    i=min(int(f),len(sky_bands)-2); frac=f-i
    for x in range(W):
        # Bayer-ish dither threshold
        th=((x&1)*2+(y&1))/4 + ((x>>1 &1)*0.06)
        buf[y][x]=sky_bands[i+1] if frac>th else sky_bands[i]

# stars (upper sky)
for _ in range(40):
    x=random.randrange(W); y=random.randrange(0,55)
    px(x,y,'white')
    if random.random()<0.3: px(x+1,y,P['sky3'])

# sun low left of tower
sunx,suny=58,108
for y in range(suny-16,suny+17):
    for x in range(sunx-16,sunx+17):
        d=math.hypot(x-sunx,y-suny)
        if d<=14: px(x,y,'sun' if d>11 else 'gold_l')
        elif d<=16: px(x,y,'sky6')

# clouds: chunky pixel ellipses
def cloud(cx,cy,w,scale=1):
    blobs=[(0,0,w,7),(-w//3,2,w//2,5),(w//3,1,w//2,6),(0,-3,w//2,5)]
    for (ox,oy,bw,bh) in blobs:
        for y in range(cy+oy-bh,cy+oy+bh+1):
            for x in range(cx+ox-bw,cx+ox+bw+1):
                if ((x-cx-ox)/bw)**2+((y-cy-oy)/bh)**2<=1:
                    px(x,y,'cloud_m')
    # highlight top, shadow bottom recolor by local pass
    for y in range(cy-10,cy+10):
        for x in range(cx-w-4,cx+w+5):
            if 0<=x<W and 0<=y<H and buf[y][x]==P['cloud_m']:
                if y<cy-1: buf[y][x]=P['cloud_l']
                if y<cy-4: buf[y][x]=P['cloud_w']
                if y>cy+3: buf[y][x]=P['cloud_d']
    # flat bottom
    # (keep as is)

cloud(38,28,26); cloud(200,20,30); cloud(228,52,20); cloud(22,62,18); cloud(172,72,16); cloud(92,14,18)

# distant Paris skyline silhouette (y 148-176)
def skyline(ybase,color,seed_off):
    random.seed(seed_off)
    x=0
    while x<W:
        bw=random.randint(10,22); bh=random.randint(6,20)
        rect(x,ybase-bh,min(x+bw,W-1),ybase,color)
        # mansard roof
        for i in range(bw//2):
            hline(x+i,x+bw-i,ybase-bh-i//2,color)
        # chimney
        cx=x+random.randint(2,max(2,bw-4))
        rect(cx,ybase-bh-4,cx+2,ybase-bh,color)
        x+=bw+random.randint(0,3)
skyline(176,'far2',7)
# dome (Invalides) right
for y in range(128,160):
    hw=int(12*math.sin((y-128)/32*math.pi/1.4))
    hline(206-hw,206+hw,y,'far')
rect(204,118,208,132,'far'); px(206,114,'far'); px(206,115,'far'); px(206,116,'far'); px(206,117,'far')
skyline(178,'far',21)
# lit windows in skyline
random.seed(33)
for _ in range(90):
    x=random.randrange(W); y=random.randrange(150,176)
    if buf[y][x] in (P['far'],P['far2']):
        px(x,y,'win')

# --- ground ---
rect(0,176,W-1,H-1,'grass_d')
for y in range(176,H):
    c='grass' if y<192 else 'grass_d'
    hline(0,W-1,y,c)
    for x in range(W):
        if (x*7+y*13)%29==0: px(x,y,'grass_l')
        if (x*11+y*5)%43==0: px(x,y,'grass_d')
# central path (perspective trapezoid)
for y in range(184,H):
    t=(y-184)/(H-184); hw=int(8+t*30)
    hline(128-hw,128+hw,y,'path_d' if y%6==0 else 'path')
    px(128-hw,y,'grass_d'); px(128+hw,y,'grass_d')
# path sparkles
random.seed(4)
for _ in range(40):
    y=random.randrange(186,H); t=(y-184)/(H-184); hw=int(8+t*30)
    px(128+random.randint(-hw,hw),y,'path_d')

# ============ EIFFEL TOWER ============
CX=128
TOP=16; BASE=188
def tower_hw(y):
    """Half-width of tower body (solid taper curve)."""
    if y<TOP or y>BASE: return 0
    t=(y-TOP)/(BASE-TOP)  # 0 top .. 1 base
    # Eiffel profile: narrow top, flaring curved legs
    return int(3 + 62*(t**1.85))

# Save sky/background for punching lattice holes later
bg=[row[:] for row in buf]

# Fill tower silhouette solid first
for y in range(TOP,BASE+1):
    hw=tower_hw(y)
    hline(CX-hw,CX+hw,y,'iron')

# Punch the great arch between legs (below first floor y~138)
for y in range(132,BASE+1):
    # arch opening: parabola peaking at y=132
    t=(y-132)/(BASE-132)
    arch_hw=int(34*(t**0.55)) if y>132 else 0
    # arch top curve
    for x in range(CX-arch_hw,CX+arch_hw+1):
        if 0<=x<W: buf[y][x]=bg[y][x]
# widen arch top smoothly
for y in range(126,133):
    hw=int(10*(y-126)/6)
    for x in range(CX-hw,CX+hw+1):
        buf[y][x]=bg[y][x]

# Punch lattice holes: diagonal cross pattern in the mid/upper body
# Create diamond lattice by restoring bg where lattice cells are open,
# leaving iron beams along diagonals.
for y in range(34,138):
    hw=tower_hw(y)
    cell=12 if y>95 else (10 if y>60 else 8)
    for x in range(CX-hw+3,CX+hw-2):
        u=(x-CX)+(y-34); v=(x-CX)-(y-34)
        # beams where u or v near multiple of cell
        beam = (u%cell<2) or (v%cell<2) or ((y-34)%cell==0)
        if not beam:
            buf[y][x]=bg[y][x]
# Leg lattice: X braces on each leg below first floor
for y in range(138,BASE+1):
    hw=tower_hw(y)
    t=(y-132)/(BASE-132); arch_hw=int(34*(t**0.55))
    for side in (-1,1):
        x0=CX+side*(arch_hw+2); x1=CX+side*(hw-2)
        lo,hi=min(x0,x1),max(x0,x1)
        for x in range(lo+1,hi):
            u=(x-lo)+(y-138); v=(x-lo)-(y-138)
            if not (u%11<2 or v%11<2 or (y-138)%11==0):
                if 0<=x<W: buf[y][x]=bg[y][x]

# Re-draw solid outer edges (2px) for crisp silhouette
for y in range(TOP,BASE+1):
    hw=tower_hw(y)
    for d in range(3):
        px(CX-hw+d,y,'iron_d' if d==0 else 'iron')
        px(CX+hw-d,y,'iron_d' if d==0 else 'iron')
    # sun-side highlight on left edge
    px(CX-hw+1,y,'iron_l')
    px(CX-hw+2,y,'iron_m')
# arch inner edges
for y in range(130,BASE+1):
    t=max(0,(y-132)/(BASE-132)); arch_hw=int(34*(t**0.55)) if y>132 else int(10*(y-126)/6)
    for d in range(2):
        px(CX-arch_hw-d,y,'iron_d' if d==1 else 'iron')
        px(CX+arch_hw+d,y,'iron_d' if d==1 else 'iron')

# Highlight lattice beams: lighten top-left lit beams
for y in range(34,138):
    for x in range(W):
        if buf[y][x]==P['iron']:
            # light from left sun: tint left half lighter
            if x<CX-6 and (x+y)%3==0: buf[y][x]=P['iron_m']
            if x<CX-14 and (x+y)%5==0: buf[y][x]=P['iron_l']

# Platforms: 1st floor (~y132), 2nd floor (~y92), summit (~y40)
def platform(y,hw_extra=6, h=6):
    y0=y; hw=tower_hw(y)+hw_extra
    rect(CX-hw,y0,CX+hw,y0+h-1,'iron_d')
    rect(CX-hw,y0,CX+hw,y0+1,'iron_l')   # top deck highlight
    rect(CX-hw,y0+2,CX+hw,y0+3,'iron')
    # railing posts + warm windows
    for x in range(CX-hw+2,CX+hw-1,3):
        px(x,y0-2,'iron_d'); px(x,y0-1,'iron_d')
    hline(CX-hw,CX+hw,y0-3,'iron_d')
    for x in range(CX-hw+3,CX+hw-2,5):
        px(x,y0+2,'gold'); px(x,y0+3,'gold')
platform(130,7,7)
platform(90,6,6)
platform(46,5,5)

# Summit cap + spire + beacon
rect(CX-5,34,CX+5,46,'iron_d')
rect(CX-5,34,CX+5,35,'iron_l')
for x in range(CX-3,CX+4,2): px(x,38,'gold'); px(x,39,'gold')
rect(CX-3,28,CX+3,34,'iron')
rect(CX-1,20,CX+1,28,'iron_d')
vline(CX,12,20,'iron_d')
# beacon glow
px(CX,10,'gold_l'); px(CX,11,'gold'); px(CX-1,11,'gold'); px(CX+1,11,'gold'); px(CX,12,'gold')
# (beacon glow only; no beam)
# French flag at summit? small tricolor to right of spire
rect(CX+2,14,CX+3,17,(32,64,160)); rect(CX+4,14,CX+5,17,(255,248,232)); rect(CX+6,14,CX+7,17,(216,48,64))

# Golden floodlight sparkles on tower (evening illumination dots)
random.seed(99)
for _ in range(70):
    y=random.randrange(40,BASE); hw=tower_hw(y)
    x=CX+random.randint(-hw,hw)
    if 0<=x<W and buf[y][x] in (P['iron'],P['iron_d'],P['iron_m']):
        px(x,y,'gold')

# feet bases
for side in (-1,1):
    fx=CX+side*tower_hw(BASE)
    rect(min(fx,CX+side*20)-2 if side<0 else CX+18,186,0,0,'iron_d')  # noop guard placeholder
# simpler: dark plinths at leg bottoms
rect(CX-66,186,CX-38,191,'iron_d'); rect(CX+38,186,CX+66,191,'iron_d')
hline(CX-66,CX-38,186,'iron_l'); hline(CX+38,CX+66,186,'iron_l')

# --- foreground trees ---
def tree(cx,by,s):
    rect(cx-1,by-6*s//2,cx+1,by,'trunk')
    for y in range(by-16*s//2-8,by-2):
        for x in range(cx-11*s//2-3,cx+11*s//2+4):
            d=((x-cx)/(9*s/2+3))**2+((y-(by-11*s//2-2))/(8*s/2+2))**2
            if d<=1:
                c='tree_l' if (x<cx and (x*3+y)%4==0) else ('tree' if (x+y)%3 else 'tree_d')
                px(x,y,c)
    # outline bottom
for (tx,ty,s) in [(18,196,3),(42,188,2),(214,190,2),(238,198,3),(62,206,3),(196,208,3),(84,192,2),(172,192,2)]:
    tree(tx,ty,s)

# lamp posts along path with glow
def lamp(x,y):
    vline(x,y-10,y,'black'); px(x,y-11,'gold_l'); px(x-1,y-11,'gold'); px(x+1,y-11,'gold'); px(x,y-12,'gold')
for (lx,ly) in [(100,196),(156,196),(88,210),(168,210),(112,188),(144,188)]:
    lamp(lx,ly)

# tiny people silhouettes on path
def person(x,y,c='black'):
    px(x,y-5,c); rect(x-1,y-4,x+1,y-1,c); px(x-1,y,c); px(x+1,y,c)
person(122,206); person(134,214); person(118,198,'iron_d'); person(140,202)

# flowers dots in grass foreground
random.seed(8)
for _ in range(50):
    x=random.randrange(W); y=random.randrange(194,H)
    if buf[y][x] in (P['grass'],P['grass_d']):
        px(x,y,random.choice(['gold','gold_l','white','cloud_l']))

# --- write PNG (indexed not needed; truecolor) ---
def write_png(path):
    raw=b''.join(b'\x00'+b''.join(bytes(p) for p in row) for row in buf)
    def chunk(typ,data):
        c=struct.pack('>I',len(data))+typ+data
        return c+struct.pack('>I',zlib.crc32(typ+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'
    png+=chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
    png+=chunk(b'IDAT',zlib.compress(raw,9))
    png+=chunk(b'IEND',b'')
    open(path,'wb').write(png)
    print(path, len(png), 'bytes')
write_png('output/eiffel-tower-snes.png')

# verify constraints
colors=set()
max_tile=0; worst=None
for ty in range(0,H,8):
    for tx in range(0,W,8):
        s=set()
        for y in range(ty,min(ty+8,H)):
            for x in range(tx,min(tx+8,W)):
                s.add(buf[y][x]); colors.add(buf[y][x])
        if len(s)>max_tile: max_tile=len(s); worst=(tx,ty)
print(f'size {W}x{H} total_colors={len(colors)} max_colors_per_8x8_tile={max_tile} at {worst}')
assert len(colors)<=128, 'too many colors'
assert max_tile<=16, 'tile color limit exceeded'
print('SNES constraints OK')
