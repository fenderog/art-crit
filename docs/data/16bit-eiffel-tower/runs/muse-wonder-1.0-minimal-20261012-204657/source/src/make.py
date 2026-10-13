import struct, zlib, os, math, random
W,H=256,224
random.seed(7)
# palette RGB tuples
sky=[(24,32,96),(32,44,112),(44,60,132),(58,78,148),(74,96,164),(92,114,180),(112,132,192),(132,150,200),(152,166,208),(172,180,214),(192,192,218),(208,200,220),(224,204,216),(236,200,200),(244,196,180),(248,192,160)]
# use sky index by y
px=[[sky[0]]*W for _ in range(H)]

def setp(x,y,c):
    if 0<=x<W and 0<=y<H: px[y][x]=c
def rect(x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): setp(x,y,c)
def hline(x0,x1,y,c):
    rect(x0,y,x1,y,c)

# sky gradient with ordered dither at boundaries
for y in range(H):
    t=y/165
    if t>1: t=1
    f=t*(len(sky)-1); i=int(f); frac=f-i
    for x in range(W):
        c=sky[i]
        if i+1<len(sky) and frac>0.55 and ((x+y)&1)==0:
            c=sky[min(i+1,len(sky)-1)]
        px[y][x]=c

# stars in top
star=(232,236,255)
for _ in range(45):
    x=random.randrange(W); y=random.randrange(0,55)
    setp(x,y,star)
    if random.random()<.3: setp(x+1,y,sky[3])

# sun / glow low left? Moon crescent top right polished game
moon=(248,240,200); moon_sh=(224,210,170)
for yy in range(-14,15):
    for xx in range(-14,15):
        if xx*xx+yy*yy<=196:
            setp(218+xx,28+yy, moon if xx<4 else moon_sh)
# craters
for cx,cy in [(210,22),(218,34),(206,34)]:
    rect(cx-1,cy-1,cx+1,cy+1,moon_sh)

# clouds: layered ellipses, 4 colors
cloud_cols=[(250,250,255),(216,220,240),(176,188,220),(148,166,205)]
def cloud(cx,cy,s):
    blobs=[(0,0,22,7),(-14,2,14,5),(14,2,16,5),(-6,-4,13,6),(8,-3,12,5)]
    for ox,oy,rx,ry in blobs:
        rx=int(rx*s); ry=int(ry*s)
        for yy in range(-ry,ry+1):
            for xx in range(-rx,rx+1):
                if (xx*xx)/(rx*rx+1)+(yy*yy)/(ry*ry+1)<=1:
                    x=cx+int(ox*s)+xx; y=cy+int(oy*s)+yy
                    # shading bottom
                    col=cloud_cols[0] if yy<0 else (cloud_cols[1] if yy<ry-2 else cloud_cols[2])
                    setp(x,y,col)
    # bottom shadow line
    # highlight dots handled
cloud(45,38,1.0); cloud(165,58,0.8); cloud(95,22,0.65); cloud(235,72,0.7); cloud(20,82,0.6)

# distant Paris skyline
far=(86,84,140); far2=(104,98,158); roof=(58,54,110)
for x in range(W):
    base=168+ int(4*math.sin(x*0.11))+ (3 if (x//17)%2 else 0)
    h= 18+ ((x//13)*7)%16
    # buildings segmented
    bx=(x//16)*16; bh=14+((bx*37)%18)
    top=172-bh
    col=far if (bx//16)%2 else far2
    if y if False else True:
        pass
    for y in range(top,172):
        px[y][x]=col
    if x%16==0:
        for y in range(top,172): px[y][x]=far
    # roof triangle-ish
    # windows handled below
# rooftops & windows
for bx in range(0,W,16):
    bh=14+((bx*37)%18); top=172-bh
    rect(bx,top,bx+15,top+2,roof)
    rect(bx+2,top-2,bx+5,top-1,roof) # chimney/dome-ish
    for wy in range(top+5,168,6):
        for wx in range(bx+3,bx+13,5):
            if (wx+wy)%3: setp(wx,wy,(250,220,140)); setp(wx+1,wy,(250,220,140))
# dome silhouette left
for yy in range(0,18):
    w=int(16*math.sin(math.acos(max(-1,min(1,(yy-18)/18)))) ) if yy<18 else 16
    rect(28-w,154+yy,28+w,154+yy,far)
rect(26,136,30,154,far); setp(28,134,far); setp(28,133,far)

# mid ground trees / ground
ground=(36,92,62); ground2=(28,76,52); ground_d=(20,60,40)
rect(0,172,W-1,191,ground)
for y in range(172,192):
    for x in range(W):
        if ((x+y)&7)==0: setp(x,y,ground2)
# plaza foreground
plaza=(196,168,138); plaza2=(172,142,112); plaza3=(148,118,92)
for y in range(192,224):
    for x in range(W):
        # perspective trapezoid widening
        cx=128; half=28+(y-192)*2.2
        if abs(x-cx)<half:
            c=plaza if ((x//8)+(y//4))%2==0 else plaza2
            if y%8==0: c=plaza3
            setp(x,y,c)
        else:
            c=ground if ((x//6)+(y//5))%2 else ground2
            if y>210: c=ground2 if x%5 else ground_d
            setp(x,y,c)

# trees: dark blobs with highlights
tree_d=(18,58,36); tree_m=(28,84,48); tree_l=(52,120,66)
def tree(cx,cy,r):
    for yy in range(-r,r+1):
        for xx in range(-r,r+1):
            if xx*xx+yy*yy<=r*r:
                c=tree_m if yy<0 else tree_d
                if xx<-r//3 and yy<-r//4: c=tree_l
                setp(cx+xx,cy+yy,c)
    rect(cx-1,cy+r,cx+1,cy+r+5,(62,44,32))
for cx,cy,r in [(14,178,9),(38,184,11),(68,178,8),(188,180,9),(216,184,11),(242,178,8),(92,186,7),(164,186,7)]:
    tree(cx,cy,r)

# EIFFEL TOWER
iron=(52,36,48); iron_d=(32,22,36); iron_l=(108,76,72); iron_h=(188,132,96); iron_m=(78,54,58)
warm=(255,214,120); warm2=(255,176,80)

def tower_halfwidth(y):
    # returns half width of outer edge
    if y<28: return 1
    if y<46: return 2+(y-28)*0.12  # spire to top
    if y<108: # upper tapering outward
        return 4 + (y-46)*0.28
    if y<146:
        return 21 + (y-108)*0.42
    # legs flare
    return 37 + (y-146)*0.95

# draw silhouette filled with iron_m base then lattice cut?
for y in range(24,196):
    hw=tower_halfwidth(y)
    cx=128
    # legs region: below 146, interior arch empty between legs
    if y>=146:
        # arch top curve: empty width
        # arch opening: half width grows then?
        arch_hw = 8 + (y-146)*0.45
        # arch top at 158 curved
        if y>158:
            for x in range(int(cx-arch_hw), int(cx+arch_hw)+1):
                # keep sky/ground as is (skip) handled by only drawing legs sides
                pass
            # draw legs
            for x in range(int(cx-hw), int(cx+hw)+1):
                if abs(x-cx)>=arch_hw:
                    setp(x,y,iron_m)
        else:
            for x in range(int(cx-hw), int(cx+hw)+1): setp(x,y,iron_m)
    else:
        for x in range(int(cx-hw), int(cx+hw)+1): setp(x,y,iron_m)

# lattice: horizontal bands and diagonals in contrasting, plus inner sky holes upper sections
# create holes: for upper part, pattern diamonds showing sky
def sky_at(x,y): return sky[min(15,max(0,int(y/165*15)))]
for y in range(34,146):
    hw=tower_halfwidth(y)-3
    if hw<2: continue
    cx=128
    # diamond lattice holes
    # cell 10px
    for x in range(int(cx-hw), int(cx+hw)+1):
        # diagonal lines are iron, interior holes sky-ish at centers
        diag = ((x-cx)+(y))%12==0 or ((x-cx)-(y))%12==0
        horiz = (y%10==0)
        if not diag and not horiz:
            # inside fill lighter sky hole if not near edges
            if abs(x-cx) < hw-2:
                setp(x,y, sky_at(x,y) if y<120 else (140,150,190))
        # else keep iron
# redraw outer edges thick
for y in range(24,196):
    hw=tower_halfwidth(y); cx=128
    for dx in [-1,0,1]:
        setp(int(cx-hw)+dx,y,iron_d); setp(int(cx+hw)+dx,y,iron_d)
    # highlight inner edge of legs / left edge
    setp(int(cx-hw)+3,y,iron_l)
    if y>=146:
        ahw=8+(y-146)*0.45
        if y>156:
            for dx in [-1,0,1]:
                setp(int(cx-ahw)+dx,y,iron_d); setp(int(cx+ahw)+dx,y,iron_d)
            setp(int(cx-ahw)+3,y,iron_l)

# inner lattice lines over holes: diagonals dark thin
for y in range(34,196):
    hw=tower_halfwidth(y)-1; cx=128
    for x in range(int(cx-hw), int(cx+hw)+1):
        if ((x-cx)+y)%12==0 or ((x-cx)-y)%12==0:
            if y<146 or abs(x-cx)> (8+(y-146)*0.45):
                setp(x,y,iron)
        if y%10==0 and (y<146 or abs(x-cx)> (8+(y-146)*0.45)):
            setp(x,y,iron)
# arch curve
for a in range(-30,31):
    y=int(158 - (1-(a/30)**2)*14)
    setp(128+a,y,iron_d); setp(128+a,y+1,iron)

# leg lattice detail: light diagonals + diamond holes showing ground
for y in range(150,194):
    hw=tower_halfwidth(y); ahw=8+(y-146)*0.45; cx=128
    for x in range(int(cx-hw)+3,int(cx+hw)-2):
        if abs(x-cx)<ahw+2: continue
        if ((x-cx)+y)%14==0 or ((x-cx)-y)%14==0:
            setp(x,y,iron_h); setp(x+1,y,iron_l)
        if y%12==0: setp(x,y,iron_d)
    # diamond holes
    for hx,hy in [(cx-int((hw+ahw)/2),y) for y in (162,176,188)]:
        pass
for hy in (164,178,190):
    hw=tower_halfwidth(hy); ahw=8+(hy-146)*0.45; mid=int((hw+ahw)/2)
    for side in (-1,1):
        cx2=128+side*mid
        for yy in range(-4,5):
            for xx in range(-3,4):
                if abs(xx)+abs(yy)<=4: setp(cx2+xx,hy+yy, ground if hy>172 else (140,150,190))
# platforms
def platform(cy,hw):
    rect(128-hw,cy,128+hw,cy+3,iron_d)
    rect(128-hw,cy,128+hw,cy,iron_h)
    rect(128-hw-2,cy+3,128+hw+2,cy+4,iron_d)
    for x in range(128-hw,128+hw,4):
        setp(x,cy+1,warm); setp(x,cy+2,iron_l)
platform(104,26); platform(144,42)
# top cap & beacon
rect(126,18,130,26,iron_d); rect(127,14,129,18,iron_d); setp(128,12,iron_d); setp(128,11,iron_d)
# beacon light glow (few colors)
setp(128,10,warm); setp(127,10,warm2); setp(129,10,warm2); setp(128,9,warm2); setp(128,11,warm2)
# light rays subtle pixels
for i in range(1,10):
    if i%2==0: setp(128-i,10-(i//4),warm2); setp(128+i,10-(i//4),warm2)

# warm lights along edges / platforms dots
for y in range(30,194,6):
    hw=tower_halfwidth(y)
    setp(int(128-hw)+1,y,warm); setp(int(128+hw)-1,y,warm)
for x in range(102,155,4): setp(x,103,warm)
for x in range(86,171,4): setp(x,143,warm)

# tiny people / lamps foreground
lamp=(40,36,40)
for lx in [52,204,84,172]:
    rect(lx,192,lx,204,lamp); setp(lx,190,warm); setp(lx-1,191,warm2); setp(lx+1,191,warm2); setp(lx,189,warm)
# people silhouettes
for cx,cy in [(110,208),(145,212),(98,216)]:
    setp(cx,cy-3,(20,20,32)); rect(cx-1,cy-2,cx+1,cy+1,(20,20,32)); setp(cx-1,cy+2,(20,20,32)); setp(cx+1,cy+2,(20,20,32))

# vignette border dark corners like game? thin frame
# (keep within palette reuse iron_d)
for x in range(W): setp(x,0,iron_d); setp(x,H-1,iron_d)
for y in range(H): setp(0,y,iron_d); setp(W-1,y,iron_d)

# verify constraints
colors=set()
for row in px: colors.update(row)
print("colors",len(colors))
max_tile=0
for ty in range(0,H,8):
    for tx in range(0,W,8):
        s=set()
        for y in range(ty,ty+8):
            for x in range(tx,tx+8): s.add(px[y][x])
        max_tile=max(max_tile,len(s))
print("max tile colors",max_tile)
assert len(colors)<=128 and max_tile<=16, (len(colors),max_tile)

# write PNG RGB
raw=b''.join(b'\x00'+b''.join(bytes(c) for c in row) for row in px)
def chunk(t,data):
    ch=struct.pack('>I',len(data))+t+data
    return ch+struct.pack('>I',zlib.crc32(t+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'
png+=chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
png+=chunk(b'IDAT',zlib.compress(raw,9))
png+=chunk(b'IEND',b'')
os.makedirs('output',exist_ok=True)
open('output/eiffel_tower_snes.png','wb').write(png)
print("written",len(png))
