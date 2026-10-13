#!/usr/bin/env python3
"""SNES Eiffel Tower pixel art, 256x224, <=128 colors, <=16 colors per 8x8 tile."""
import zlib, struct, math, os

W, H = 256, 224

# Palette (RGB tuples) - kept small on purpose
def C(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))

SKY = [C("1B2A6B"),C("2E3E8F"),C("4A5AB5"),C("6B6FBF"),C("9A6FB8"),C("C97A9A"),C("F09A6B"),C("FBC06B")]
SUN_CORE=C("FFF3B0"); SUN_MID=C("FFD86B"); SUN_EDGE=C("FFB35C")
CLOUD_L=C("FFF0E6"); CLOUD_M=C("FFC4B3"); CLOUD_D=C("D98AA6"); CLOUD_S=C("9A6FB8")
STAR=C("FFFCE8")
FAR=C("5A4A7A"); FAR_D=C("3E3460"); ROOF=C("2E2A4F"); WIN=C("FFD86B"); WIN2=C("FFB35C")
IRON_D=C("2F2233"); IRON=C("5A3A3F"); IRON_M=C("8A5A48"); IRON_L=C("C98A5A"); IRON_HL=C("FFD27A")
GOLD=C("FFD86B"); GOLD_L=C("FFF3B0")
GRASS_D=C("2F6B3A"); GRASS=C("4A9A4F"); GRASS_L=C("7ABF6B"); LAWN_D=C("256032")
PATH=C("E8C99A"); PATH_D=C("C9A876"); PATH_EDGE=C("8A6F4F")
TREE_D=C("1F4F2F"); TREE=C("2F7A3F"); TREE_L=C("5AAF5A"); TRUNK=C("5A3A2A")
BUSH_D=C("256032"); FLOWER_R=C("FF6B8A"); FLOWER_Y=C("FFD86B"); FLOWER_W=C("FFF0E6")
LAMP=C("FFD86B"); POLE=C("2F2233")
BIRD=C("2E2A4F")

buf = [[SKY[0]]*W for _ in range(H)]
def px(x,y,c):
    if 0<=x<W and 0<=y<H: buf[y][x]=c
def get(x,y): return buf[y][x]
def rect(x0,y0,x1,y1,c):
    for y in range(max(0,y0),min(H,y1+1)):
        for x in range(max(0,x0),min(W,x1+1)): buf[y][x]=c
def hline(x0,x1,y,c): rect(min(x0,x1),y,max(x0,x1),y,c)
def vline(x,y0,y1,c): rect(x,min(y0,y1),x,max(y0,y1),c)
def line(x0,y0,x1,y1,c,th=1):
    n=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(n+1):
        x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n)
        for dx in range(th):
            for dy in range(th): px(x+dx,y+dy,c)
def disc(cx,cy,r,c):
    for y in range(cy-r,cy+r+1):
        for x in range(cx-r,cx+r+1):
            if (x-cx)**2+(y-cy)**2<=r*r: px(x,y,c)

HORIZON=168
# --- sky banded gradient with checker dither at boundaries ---
band_h = HORIZON//len(SKY)
for y in range(HORIZON):
    idx=min(len(SKY)-1, y//band_h)
    for x in range(W): buf[y][x]=SKY[idx]
# dither bands: 4 rows around boundary alternate
for b in range(1,len(SKY)):
    yb=b*band_h
    for dy in range(-2,3):
        y=yb+dy
        if 0<=y<HORIZON:
            # probability fades
            for x in range(W):
                if dy<0 and ((x+y)&1)==0 and dy==-1: buf[y][x]=SKY[b]
                elif dy>=0 and ((x+y)&1)==0 and dy==0: buf[y][x]=SKY[b-1]

# stars top
stars=[(12,8),(38,14),(64,6),(90,18),(110,5),(150,9),(180,15),(210,7),(236,13),(24,26),(200,24),(128,12),(70,28),(168,28)]
for x,y in stars: px(x,y,STAR)
for x,y in [(38,14),(150,9),(210,7)]:
    px(x-1,y,STAR); px(x+1,y,STAR); px(x,y-1,STAR); px(x,y+1,STAR)

# sun low left
disc(40,128,17,SUN_EDGE); disc(40,128,14,SUN_MID); disc(40,128,10,SUN_CORE)
# sun band cuts (retro)
for y in (138,141,144):
    for x in range(22,59):
        if get(x,y) in (SUN_EDGE,SUN_MID,SUN_CORE):
            # restore sky band color approx
            idx=min(len(SKY)-1, y//band_h); px(x,y,SKY[idx])

# clouds: puffy clusters (ellipses via discs) with shadow bottom
def cloud(cx,cy,s=1):
    puffs=[(0,0,10),( -9,2,7),(9,2,8),(-4,-4,7),(5,-3,6)]
    for dx,dy,r in puffs:
        r=int(r*s)
        # shadow offset
        disc(cx+dx,cy+dy+2,r,CLOUD_D)
    for dx,dy,r in puffs:
        disc(cx+dx,cy+dy,int(r*s),CLOUD_M)
    for dx,dy,r in puffs:
        disc(cx+dx-1,cy+dy-2,int(r*s*0.65),CLOUD_L)
    # flatten bottom
    # sparkle top line
cloud(58,44,1); cloud(198,32,0.85); cloud(224,58,0.7); cloud(28,72,0.65); cloud(96,22,0.55)

# birds
def bird(x,y):
    px(x-3,y,BIRD); px(x-2,y-1,BIRD); px(x-1,y,BIRD); px(x,y,BIRD); px(x+1,y,BIRD); px(x+2,y-1,BIRD); px(x+3,y,BIRD)
bird(178,44); bird(190,52); bird(82,58); bird(92,50)

# --- distant Paris skyline silhouette ---
# base silhouette band
rect(0,150,W-1,HORIZON-1,FAR)
# building blocks varied heights
buildings=[(0,138,22),(18,132,18),(34,142,20),(52,136,16),(66,144,24),(168,140,20),(186,134,22),(206,142,18),(222,136,20),(240,144,16)]
for x,top,w in buildings:
    rect(x,top,x+w,HORIZON-1,FAR)
    rect(x,top,x+w,top+2,ROOF)  # mansard roof
    # chimney
    rect(x+3,top-4,x+5,top,ROOF)
# dome (Invalides-like) right
for i in range(14):
    w=int(12*math.sin(math.pi*(i+1)/15))
    hline(216-w,216+w,138-i,FAR_D)
vline(216,120,126,FAR_D); px(216,119,GOLD)
# small dome left
for i in range(10):
    w=int(9*math.sin(math.pi*(i+1)/11))
    hline(30-w,30+w,136-i,FAR_D)
# windows (sparse, keep tile counts low)
wins=[(6,146),(12,152),(24,140),(28,150),(42,148),(58,144),(74,152),(176,148),(192,142),(198,152),(212,150),(228,144),(236,152),(246,150),(16,158),(48,156),(184,158),(220,158)]
for i,(x,y) in enumerate(wins):
    c=WIN if i%3 else WIN2
    px(x,y,c); px(x+1,y,c); px(x,y+1,c); px(x+1,y+1,c)

# --- ground / Champ de Mars ---
rect(0,HORIZON,W-1,H-1,GRASS)
# mow stripes diagonal-ish bands
for y in range(HORIZON,H):
    for x in range(W):
        band=(x//28)%2
        buf[y][x]=GRASS if band else GRASS_D
# lawn panels left/right of path with light edges
# central gravel path in perspective: narrow at horizon, wide at bottom
def path_hw(y):
    t=(y-HORIZON)/(H-1-HORIZON)
    return int(10+ t*t*38 + t*8)  # 10 -> ~56
CX=128
for y in range(HORIZON,H):
    hw=path_hw(y)
    for x in range(CX-hw,CX+hw+1):
        c=PATH
        if y%9==0 or (x-CX)%14==0: c=PATH_D
        px(x,y,c)
    px(CX-hw,y,PATH_EDGE); px(CX-hw-1,y,GRASS_L); px(CX+hw,y,PATH_EDGE); px(CX+hw+1,y,GRASS_L)
# horizontal promenade at tower base
rect(56,184,200,192,PATH_D)
for x in range(56,201,8): vline(x,184,192,PATH_EDGE)
hline(56,200,184,PATH_EDGE); hline(56,200,192,PATH_EDGE)

# flower beds along path
for (x,y) in [(62,206),(70,214),(58,218),(186,206),(194,214),(182,218),(78,196),(172,196)]:
    for dx,dy,c in [(0,0,FLOWER_R),(2,1,FLOWER_Y),(4,0,FLOWER_W),(1,2,FLOWER_R),(3,2,FLOWER_Y),(-1,1,FLOWER_W)]:
        px(x+dx,y+dy,c); px(x+dx+1,y+dy,c)

# ================= EIFFEL TOWER =================
# profile keypoints (y, halfwidth)
pts=[(16,0),(22,2),(30,4),(38,6),(50,8),(70,11),(90,15),(96,17),(110,21),(130,27),(136,29),(155,38),(175,46),(188,52),(192,53)]
def halfw(y):
    if y<=pts[0][0]: return pts[0][1]
    for i in range(len(pts)-1):
        y0,h0=pts[i]; y1,h1=pts[i+1]
        if y0<=y<=y1:
            t=(y-y0)/max(1,(y1-y0))
            # ease curve for Eiffel flare
            return h0+(h1-h0)*(t**1.15)
    return pts[-1][1]

# Save sky/background under tower to carve arch holes later: we draw legs only, so no fill needed.
# Leg thickness tapers upward
def thick(y):
    # 11 at base -> 3 near top of legs
    t=max(0,min(1,(y-32)/160))
    return max(3,int(round(3+8*(t**0.7))))

# Draw back lattice braces first (darker), then front legs
# Sections: base->1F (192-136), 1F->2F (136-96), 2F->summit (96-32)
def draw_brace_section(y_top,y_bot,n):
    for i in range(n):
        ya=int(y_bot-(y_bot-y_top)*i/n); yb=int(y_bot-(y_bot-y_top)*(i+1)/n)
        xa_l=int(CX-halfw(ya)+thick(ya)//2); xa_r=int(CX+halfw(ya)-thick(ya)//2)
        xb_l=int(CX-halfw(yb)+thick(yb)//2); xb_r=int(CX+halfw(yb)-thick(yb)//2)
        line(xa_l,ya,xb_r,yb,IRON,1); line(xa_r,ya,xb_l,yb,IRON,1)
        # horizontal rung
        hline(xa_l,xa_r,ya,IRON)
draw_brace_section(140,186,3)
draw_brace_section(100,132,3)
draw_brace_section(40,92,4)

# Arch between legs below 1st floor: curved brace connecting legs
for a in range(0,65):
    t=a/64; ang=math.pi*(1-t)
    # arch spans between inner leg edges at y~178 up to y~152 center
    ax=int(CX+math.cos(ang)*36); ay=int(178-math.sin(ang)*26)
    for dy in range(3):
        px(ax,ay+dy,IRON_M); px(ax+1,ay+dy,IRON_M)
    px(ax,ay,IRON_L)

# Legs (front) with shading: dark outer edge, mid, highlight inner-left (sun side)
for y in range(34,193):
    hw=halfw(y); th=thick(y)
    lx0=int(CX-hw); lx1=lx0+th
    rx1=int(CX+hw); rx0=rx1-th
    for x in range(lx0,lx1+1):
        c=IRON_M
        if x==lx0: c=IRON_D
        elif x==lx0+1: c=IRON_HL if y%1==0 else IRON_L  # sunlit outer left edge
        elif x>=lx1-1: c=IRON
        px(x,y,c)
    for x in range(rx0,rx1+1):
        c=IRON
        if x==rx1: c=IRON_D
        elif x==rx0: c=IRON_M
        elif x==rx0+1: c=IRON_L
        px(x,y,c)
    # inner lattice rivet dots / cross detail on leg every 8px
    if y%8==0:
        px(lx0+th//2,y,IRON_D); px(rx0+th//2,y,IRON_D)
    if y%8==4:
        px(lx0+th//2,y,GOLD); px(rx0+th//2,y,GOLD)

# Above 2nd floor the shaft is narrow: fill centre column
for y in range(34,96):
    hw=int(halfw(y))
    rect(CX-1,y,CX+1,y,IRON)
    if y%10==0: hline(CX-hw,CX+hw,y,IRON)

# Platforms
def platform(y,hw_extra,yh=6):
    hw=int(halfw(y))+hw_extra
    rect(CX-hw,y,CX+hw,y+yh,IRON)
    rect(CX-hw,y,CX+hw,y+1,IRON_HL)     # lit top edge
    rect(CX-hw,y+yh-1,CX+hw,y+yh,IRON_D)
    # railing posts + glass warm windows
    for x in range(CX-hw+2,CX+hw-1,4):
        px(x,y-2,IRON_D); px(x,y-1,GOLD)
    hline(CX-hw,CX+hw,y-3,IRON_D)
    for x in range(CX-hw+3,CX+hw-2,6):
        px(x,y+3,GOLD_L); px(x+1,y+3,GOLD)
    # supports under platform
    line(CX-hw,y+yh,CX-hw+6,y+yh+5,IRON_D,1); line(CX+hw,y+yh,CX+hw-6,y+yh+5,IRON_D,1)
platform(132,7,7)   # 1st floor
platform(92,6,6)    # 2nd floor

# Summit
rect(CX-6,28,CX+6,36,IRON)
rect(CX-6,28,CX+6,29,IRON_HL)
rect(CX-4,31,CX+4,33,GOLD)
rect(CX-3,23,CX+3,28,IRON_M)
px(CX-1,25,GOLD_L); px(CX+1,25,GOLD_L)
vline(CX,10,23,IRON_D); vline(CX-1,16,23,IRON)
# beacon + sparkle
px(CX,9,GOLD_L); px(CX,8,GOLD); px(CX-1,9,GOLD); px(CX+1,9,GOLD); px(CX,10,GOLD)
# searchlight beam (subtle, 2px dotted)
for i in range(1,28):
    if i%3: px(CX+i,9-i//4,GOLD)

# String lights along outer edges (gold dots every 6px) - iconic sparkle
for y in range(40,190,6):
    hw=int(halfw(y))
    px(CX-hw-1,y,GOLD_L); px(CX+hw+1,y,GOLD_L)
    if y%12==0:
        px(CX-hw-2,y,GOLD); px(CX+hw+2,y,GOLD)
# sparkles
for (x,y) in [(CX-30,140),(CX+22,104),(CX-14,66),(CX+40,172),(CX-44,178)]:
    px(x,y,GOLD_L); px(x-2,y,GOLD); px(x+2,y,GOLD); px(x,y-2,GOLD); px(x,y+2,GOLD)

# Feet foundations
rect(CX-56,188,CX-40,193,IRON_D); rect(CX+40,188,CX+56,193,IRON_D)
rect(CX-56,188,CX-40,189,IRON_L); rect(CX+40,188,CX+56,189,IRON_L)

# --- foreground trees (frame corners) ---
def tree(cx,base,s=1.0):
    th=int(14*s)
    rect(cx-1,base-th,cx+1,base,TRUNK)
    for dx,dy,r in [(0,-th-8,10),(-7,-th-3,7),(7,-th-3,7),(0,-th-13,7)]:
        disc(cx+dx,base+dy,int(r*s),TREE_D)
    for dx,dy,r in [(0,-th-9,8),(-6,-th-4,5),(6,-th-4,5)]:
        disc(cx+dx,base+dy,int(r*s),TREE)
    for dx,dy,r in [(-3,-th-11,4),(3,-th-8,3)]:
        disc(cx+dx,base+dy,int(r*s),TREE_L)
tree(22,214,1.15); tree(234,214,1.15); tree(50,196,0.7); tree(206,196,0.7); tree(14,192,0.6); tree(242,192,0.6)
# hedges
for hx in (8,196):
    rect(hx,200,hx+52,206,BUSH_D); rect(hx,200,hx+52,201,TREE_L)
# lampposts along path
def lamp(x,y):
    vline(x,y-14,y,POLE); px(x,y-15,LAMP); px(x-1,y-15,GOLD); px(x+1,y-15,GOLD); px(x,y-16,GOLD_L); px(x,y-14,GOLD)
lamp(84,202); lamp(172,202); lamp(96,188); lamp(160,188)

# tiny strollers on path (2-3px, SNES charm)
def person(x,y,c1,c2):
    px(x,y-6,c2); px(x,y-5,c1); px(x,y-4,c1); px(x-1,y-3,c1); px(x+1,y-3,c1); px(x,y-2,IRON_D); px(x-1,y-1,IRON_D); px(x+1,y,IRON_D)
person(118,212,FLOWER_R,GOLD); person(124,214,C("4A6FBF"),CLOUD_L); person(140,200,C("FFF0E6"),IRON_D)

# --- verify constraints ---
colors=set()
for row in buf:
    for c in row: colors.add(c)
max_tile=0; worst=None
for ty in range(0,H,8):
    for tx in range(0,W,8):
        s=set()
        for y in range(ty,min(ty+8,H)):
            for x in range(tx,min(tx+8,W)): s.add(buf[y][x])
        if len(s)>max_tile: max_tile=len(s); worst=(tx,ty,s)
print(f"size {W}x{H} colors={len(colors)} max per 8x8 tile={max_tile} worst={worst[:2] if worst else None}")
assert len(colors)<=128, len(colors)
assert max_tile<=16, (max_tile, worst)

# --- write PNG (indexed would be ideal; write RGB truecolor, still same pixels) ---
def write_png(path):
    raw=b""
    for row in buf:
        raw+=b"\x00"+b"".join(bytes(c) for c in row)
    comp=zlib.compress(raw,9)
    def chunk(typ,data):
        c=struct.pack(">I",len(data))+typ+data
        c+=struct.pack(">I",zlib.crc32(typ+data)&0xffffffff)
        return c
    png=b"\x89PNG\r\n\x1a\n"
    png+=chunk(b"IHDR",struct.pack(">IIBBBBB",W,H,8,2,0,0,0))
    png+=chunk(b"IDAT",comp)
    png+=chunk(b"IEND",b"")
    open(path,"wb").write(png)
    print(path, len(png), "bytes")

os.makedirs("output",exist_ok=True)
write_png("output/eiffel-tower-snes.png")
