"""Merea — generative AI logo. Organic shapes, neutral tones.
Mark: three irregular 'cell' blobs merging into one growing form; their
translucent overlaps (the generative part) create new tones where they meet,
with a small nucleus in each cell and a bright seed at the shared centre.
"""
import math, os
OUT = "output"; os.makedirs(OUT, exist_ok=True)

CREAM="#F2EDE4"; PAPER="#EAE3D6"; STONE="#B7AA97"; TAUPE="#8A7B68"
CLAY="#6E6152"; CHAR="#3B362F"; INK="#27231E"

def blob(cx, cy, r, wob, phase=0.0):
    """Closed smooth blob path: radius modulated by two harmonics."""
    pts=[]
    n=14
    for i in range(n):
        a=2*math.pi*i/n
        rr=r*(1+wob[0]*math.sin(2*a+phase)+wob[1]*math.sin(3*a+phase*1.7)+wob[2]*math.cos(a-phase))
        pts.append((cx+rr*math.cos(a), cy+rr*math.sin(a)))
    # Catmull-Rom -> cubic Bezier, closed
    d=f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n):
        p0,p1,p2,p3=pts[i-1],pts[i],pts[(i+1)%n],pts[(i+2)%n]
        c1=(p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6)
        c2=(p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6)
        d+=f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d+"Z"

def mark(cx=100, cy=100, scale=1.0, colors=(STONE,TAUPE,CHAR), seed=CREAM,
         mono=None, spores=True):
    c=[mono]*3 if mono else list(colors)
    cells=[(77, 79, 45, (.06,.04,.03), 0.4, c[0]),
           (125, 83, 41, (.05,.05,.03), 2.1, c[1]),
           (99, 125, 44, (.06,.03,.04), 4.0, c[2])]
    op = 0.88 if not mono else 1.0
    g=[f'<g transform="translate({cx} {cy}) scale({scale}) translate(-100 -100)">']
    for x,y,r,w,ph,col in cells:
        g.append(f'<path d="{blob(x,y,r,w,ph)}" fill="{col}" fill-opacity="{op}"/>')
    if mono:  # keep cells legible in 1-colour: paper keylines between them
        for x,y,r,w,ph,col in cells:
            g.append(f'<path d="{blob(x,y,r,w,ph)}" fill="none" stroke="{seed}" stroke-width="2.5"/>')
    # nuclei
    for (x,y,r) in [(64,64,4.0),(138,72,3.3),(86,140,3.6)]:
        g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{seed}" fill-opacity="0.85"/>')
    # seed at the shared centre — where the three cells generate something new
    g.append(f'<circle cx="102" cy="102" r="7" fill="{seed}"/>')
    if spores:
        sc=mono or CLAY
        for (x,y,r,o) in [(176,38,3.2,.8),(188,62,1.9,.55),(20,158,2.4,.65),
                          (12,134,1.6,.45),(168,176,2.0,.6),(30,26,1.7,.4)]:
            g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{sc}" fill-opacity="{o}"/>')
    g.append('</g>')
    return "\n".join(g)

def svg(w,h,body,bg=None):
    b=f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{b}\n{body}\n</svg>\n')

FONT="font-family=\"'Avenir Next','Segoe UI',Helvetica,Arial,sans-serif\""
def wordmark(x,y,size,color,anchor="start",tagcolor=None):
    return (f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="300" '
            f'letter-spacing="{size*0.34:.1f}" fill="{color}" text-anchor="{anchor}">merea</text>\n'
            f'<text x="{x+2}" y="{y+size*0.62:.0f}" {FONT} font-size="{size*0.205:.0f}" font-weight="400" '
            f'letter-spacing="{size*0.16:.1f}" fill="{tagcolor or color}" fill-opacity="0.62" '
            f'text-anchor="{anchor}">GENERATIVE INTELLIGENCE</text>')

open(f"{OUT}/01-merea-primary.svg","w").write(
    svg(860,320, mark(152,160,1.22)+"\n"+wordmark(315,162,64,INK,tagcolor=CLAY), CREAM))
open(f"{OUT}/02-merea-mark.svg","w").write(svg(400,400, mark(200,200,1.9)))
open(f"{OUT}/03-merea-stacked-dark.svg","w").write(
    svg(600,500, mark(300,185,1.3,colors=(PAPER,STONE,TAUPE),seed=CHAR)
        +"\n"+wordmark(312,408,52,CREAM,anchor="middle",tagcolor=STONE), CHAR))
open(f"{OUT}/04-merea-mono.svg","w").write(
    svg(860,320, mark(152,160,1.22,mono=INK,seed="#FFFFFF")
        +"\n"+wordmark(315,162,64,INK), "#FFFFFF"))
print("wrote", sorted(os.listdir(OUT)))
