# Generates an organic-shape logo for "Loam" — a generative AI company.
import math
W, H = 800, 800
cx, cy = 400, 330

def blob(r, seed, n=7, amp=0.12, rot=0):
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n + rot
        rr = r*(1 + amp*math.sin(seed + i*2.3) + amp*0.5*math.cos(seed*1.7 + i*1.1))
        pts.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
    # smooth closed Catmull-Rom -> cubic bezier
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i-1], pts[i], pts[(i+1)%n], pts[(i+2)%n]
        c1 = (p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6)
        c2 = (p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + "Z"

layers = [(200,1.0,"#C9BBA8",0.10,0.0),(165,2.4,"#A89580",0.13,0.4),
          (128,3.9,"#7E6E5E",0.15,0.9),(88,5.1,"#55493F",0.17,1.5)]
paths = "\n".join(f'  <path d="{blob(r,s,amp=a,rot=ro)}" fill="{c}" opacity="0.92"/>' for r,s,c,a,ro in layers)
# seed: small light core suggests a spark of generation
core = blob(34, 7.3, n=5, amp=0.2, rot=0.3)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <rect width="{W}" height="{H}" fill="#F3EEE6"/>
{paths}
  <path d="{core}" fill="#EFE6D8"/>
  <text x="400" y="650" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="88" letter-spacing="14" fill="#3E352E">loam</text>
  <text x="400" y="705" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="20" letter-spacing="9" fill="#8A7B6C">GENERATIVE INTELLIGENCE</text>
</svg>'''
open("output/loam_logo.svg","w").write(svg)
