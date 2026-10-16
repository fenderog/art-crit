"""Generates the LOAM logo (organic, neutral-tone mark + hand-built wordmark)."""
import math, random

rnd = random.Random(7)
BG = "#EFEAE2"
INK = "#3A352F"
PALETTE = ["#CFC4B3", "#B3A692", "#8F8272", "#6A5F53", "#4A433B"]

def closed_spline(pts, t=0.5):
    """Catmull-Rom through pts -> closed cubic Bezier path."""
    n = len(pts)
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[(i-1) % n], pts[i], pts[(i+1) % n], pts[(i+2) % n]
        c1 = (p1[0] + (p2[0]-p0[0])*t/3*1.0, p1[1] + (p2[1]-p0[1])*t/3*1.0)
        c2 = (p2[0] - (p3[0]-p1[0])*t/3*1.0, p2[1] - (p3[1]-p1[1])*t/3*1.0)
        d += f" C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d + "Z"

def blob(cx, cy, rx, ry, rot, jitter=0.12, n=9):
    pts = []
    for k in range(n):
        a = 2*math.pi*k/n
        j = 1 + rnd.uniform(-jitter, jitter)
        x, y = rx*math.cos(a)*j, ry*math.sin(a)*j
        # taper one end so it reads as a petal / seed
        taper = 1 - 0.28*max(0, -math.cos(a))
        y *= taper
        c, s = math.cos(rot), math.sin(rot)
        pts.append((cx + x*c - y*s, cy + x*s + y*c))
    return closed_spline(pts)

# ---- mark: petals grown around a seed
MX, MY = 295, 240
petals = []
count = 7
for i in range(count):
    ang = 2*math.pi*i/count - math.pi/2 + rnd.uniform(-0.05, 0.05)
    dist = 62 + rnd.uniform(-6, 6)
    rx = 78 + rnd.uniform(-8, 10)
    ry = 40 + rnd.uniform(-5, 6)
    cx, cy = MX + dist*math.cos(ang), MY + dist*math.sin(ang)
    col = PALETTE[i % len(PALETTE)] if i % 2 == 0 else PALETTE[(i*2+1) % len(PALETTE)]
    petals.append((blob(cx, cy, rx, ry, ang), col))

# inner ring of smaller leaves, offset between petals
inner = []
for i in range(count):
    ang = 2*math.pi*(i+0.5)/count - math.pi/2
    dist = 30
    cx, cy = MX + dist*math.cos(ang), MY + dist*math.sin(ang)
    inner.append((blob(cx, cy, 34, 18, ang, 0.1, 8), PALETTE[(i*3) % len(PALETTE)]))

seed = blob(MX, MY, 17, 15, 0.5, 0.08, 8)

# ---- wordmark: l o a m drawn as round-capped strokes
def wordmark(x0, base, h=104, sw=17):
    xh = h*0.62  # x-height
    top = base - xh
    r = xh/2
    parts = []
    x = x0
    # l
    parts.append(f"M{x},{base-h*1.0:.1f} L{x},{base:.1f}")
    x += 26 + r
    # o
    parts.append(f"M{x-r+0:.1f},{base-r:.1f} a{r:.1f},{r:.1f} 0 1,0 {2*r:.1f},0 a{r:.1f},{r:.1f} 0 1,0 {-2*r:.1f},0")
    x += r + 26 + r
    # a (bowl + stem)
    parts.append(f"M{x-r:.1f},{base-r:.1f} a{r:.1f},{r:.1f} 0 1,0 {2*r:.1f},0 a{r:.1f},{r:.1f} 0 1,0 {-2*r:.1f},0")
    parts.append(f"M{x+r:.1f},{top:.1f} L{x+r:.1f},{base:.1f}")
    x += r + 26
    # m (stem + two arches)
    w = r*1.55
    parts.append(f"M{x},{top:.1f} L{x},{base:.1f}")
    parts.append(f"M{x},{top+r*0.9:.1f} C{x},{top-r*0.25:.1f} {x+w},{top-r*0.25:.1f} {x+w},{top+r*0.9:.1f} L{x+w},{base:.1f}")
    parts.append(f"M{x+w},{top+r*0.9:.1f} C{x+w},{top-r*0.25:.1f} {x+2*w},{top-r*0.25:.1f} {x+2*w},{top+r*0.9:.1f} L{x+2*w},{base:.1f}")
    return " ".join(parts), x + 2*w

wm, wm_end = wordmark(475, 282)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" width="960" height="480" role="img" aria-labelledby="t">',
       '<title id="t">Loam — generative AI</title>',
       f'<rect width="960" height="480" fill="{BG}"/>',
       '<defs><filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.4"/></filter></defs>',
       '<g id="mark">']
for d, c in petals:
    svg.append(f'<path d="{d}" fill="{c}" fill-opacity="0.78"/>')
for d, c in inner:
    svg.append(f'<path d="{d}" fill="{c}" fill-opacity="0.85"/>')
svg.append(f'<path d="{seed}" fill="{INK}"/>')
svg.append('</g>')
svg.append(f'<path id="wordmark" d="{wm}" fill="none" stroke="{INK}" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>')
# tagline as small seed dots + text
svg.append(f'<text x="477" y="336" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="17" letter-spacing="6.5" fill="#7D7266">GENERATIVE INTELLIGENCE</text>')
svg.append('</svg>')
open("output/loam-logo.svg", "w").write("\n".join(svg))

# mark-only square version
sq = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="115 60 360 360" width="512" height="512">',
      f'<rect x="115" y="60" width="360" height="360" fill="{BG}"/>']
for d, c in petals: sq.append(f'<path d="{d}" fill="{c}" fill-opacity="0.78"/>')
for d, c in inner: sq.append(f'<path d="{d}" fill="{c}" fill-opacity="0.85"/>')
sq.append(f'<path d="{seed}" fill="{INK}"/></svg>')
open("output/loam-mark.svg", "w").write("\n".join(sq))
