#!/usr/bin/env python3
"""ōra — generative AI logo. Organic 3-petal bloom, neutral tones. Outputs to ./output/"""
import os
os.makedirs("output", exist_ok=True)
CREAM="#F4F0E9"; STONE="#E6DED3"; TAUPE="#C9B8A6"; CLAY="#A99B8A"; CHARCOAL="#23201D"; WARM="#6B655E"

PETAL = "M 0,14 C -40,-16 -34,-80 0,-96 C 34,-80 40,-16 0,14 Z"

def mark(cx, cy, scale=1.0, mono=False):
    c1 = CHARCOAL if mono else TAUPE
    c2 = CHARCOAL if mono else CHARCOAL
    c3 = CHARCOAL if mono else STONE
    fill3 = "none" if mono else STONE
    return f'''
  <g transform="translate({cx},{cy}) scale({scale})">
    <g transform="rotate(-28)"><path d="{PETAL}" fill="{c1}"/></g>
    <g transform="rotate(92)"><path d="{PETAL}" fill="{c2}"/></g>
    <g transform="rotate(212)"><path d="{PETAL}" fill="{fill3}" stroke="{CHARCOAL}" stroke-width="1.4"/></g>
    <circle r="14" fill="{CREAM}"/><circle r="6" fill="{CHARCOAL}"/>
    <circle cx="50" cy="-68" r="5" fill="{CHARCOAL}"/><circle cx="68" cy="-50" r="3.2" fill="{CLAY}"/><circle cx="76" cy="-74" r="2.2" fill="{TAUPE}"/>
    <path d="M 40,-56 Q 48,-62 50,-68 M 58,-56 Q 64,-54 68,-50" stroke="{CLAY}" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.7"/>
  </g>'''

primary = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640" role="img" aria-label="ora generative AI logo">
  <rect width="1200" height="640" fill="{CREAM}"/>
  <path d="M 920,40 C 1020,20 1120,90 1100,190 C 1082,278 960,300 900,240 C 840,180 830,60 920,40 Z" fill="{STONE}" opacity="0.55"/>
  <path d="M 60,520 C 140,500 210,540 200,600 C 192,642 80,650 40,610 C 6,576 -10,538 60,520 Z" fill="{STONE}" opacity="0.5"/>
  {mark(230,300,1.25)}
  <g fill="{CHARCOAL}">
    <text x="400" y="330" font-family="Georgia, 'Times New Roman', serif" font-size="118" letter-spacing="-2">ōra</text>
    <text x="406" y="382" font-family="Inter, Helvetica, Arial, sans-serif" font-size="19" letter-spacing="5.5" fill="{WARM}">GENERATIVE INTELLIGENCE</text>
    <line x1="406" y1="412" x2="822" y2="412" stroke="{TAUPE}" stroke-width="1.5"/>
    <text x="406" y="446" font-family="Inter, Helvetica, Arial, sans-serif" font-size="15.5" fill="{WARM}">Grown, not built — AI that evolves with you.</text>
  </g>
  <text x="600" y="595" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="11" letter-spacing="3" fill="#B8A99A">ORGANIC  •  NEUTRAL  •  GENERATIVE</text>
</svg>'''

icon = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 400 400" role="img" aria-label="ora icon">
  <rect width="400" height="400" rx="88" fill="{CREAM}"/>
  <rect x="10" y="10" width="380" height="380" rx="80" fill="none" stroke="{STONE}"/>
  {mark(200,200,1.15)}
</svg>'''

mono = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360" viewBox="0 0 1000 360" role="img" aria-label="ora mono logo">
  <rect width="1000" height="360" fill="white"/>
  {mark(170,180,0.95, mono=True)}
  <g fill="{CHARCOAL}">
    <text x="300" y="188" font-family="Georgia, 'Times New Roman', serif" font-size="92" letter-spacing="-1">ōra</text>
    <text x="304" y="228" font-family="Inter, Helvetica, Arial, sans-serif" font-size="15" letter-spacing="5" fill="{WARM}">GENERATIVE INTELLIGENCE</text>
  </g>
</svg>'''

for name, data in [("logo-primary.svg", primary), ("logo-icon.svg", icon), ("logo-mono.svg", mono)]:
    open(f"output/{name}", "w").write(data)
    print(name, len(data))

# --- PNG preview of the icon (pure stdlib rasteriser, same petal geometry) ---
import zlib, struct, math
W = H = 800; S = 2.3
px = [[(244, 240, 233)] * W for _ in range(H)]
def _cubic(p0, p1, p2, p3, n=48):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],
             (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1])
            for t in (i/n for i in range(n+1))]
_petal = _cubic((0,14),(-40,-16),(-34,-80),(0,-96)) + _cubic((0,-96),(34,-80),(40,-16),(0,14))
def _fill(pts, color):
    pts = [(400+x*S, 400+y*S) for x, y in pts]
    for y in range(max(0, int(min(p[1] for p in pts))), min(H, int(max(p[1] for p in pts))+1)):
        xs = sorted(pts[i][0]+(y-pts[i][1])/(pts[(i+1)%len(pts)][1]-pts[i][1])*(pts[(i+1)%len(pts)][0]-pts[i][0])
                    for i in range(len(pts)) if (pts[i][1] <= y < pts[(i+1)%len(pts)][1]) or (pts[(i+1)%len(pts)][1] <= y < pts[i][1]))
        for i in range(0, len(xs)-1, 2):
            for x in range(max(0, int(xs[i])), min(W, int(xs[i+1])+1)): px[y][x] = color
def _rot(pts, d):
    r = math.radians(d); return [(x*math.cos(r)-y*math.sin(r), x*math.sin(r)+y*math.cos(r)) for x, y in pts]
def _circ(cx, cy, r, color):
    cx, cy, r = 400+cx*S, 400+cy*S, r*S
    for y in range(int(cy-r), int(cy+r+1)):
        for x in range(int(cx-r), int(cx+r+1)):
            if 0 <= x < W and 0 <= y < H and (x-cx)**2+(y-cy)**2 <= r*r: px[y][x] = color
_fill(_rot(_petal, -28), (201,184,166)); _fill(_rot(_petal, 92), (35,32,29)); _fill(_rot(_petal, 212), (230,222,211))
_circ(0,0,14,(244,240,233)); _circ(0,0,6,(35,32,29)); _circ(50,-68,5,(35,32,29)); _circ(68,-50,3.2,(169,155,138)); _circ(76,-74,2.2,(201,184,166))
_raw = b''.join(b'\x00' + b''.join(struct.pack('BBB', *px[y][x]) for x in range(W)) for y in range(H))
def _chunk(t, d):
    c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)
open("output/logo-icon.png", "wb").write(b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) + _chunk(b'IDAT', zlib.compress(_raw)) + _chunk(b'IEND', b''))
print("logo-icon.png written")
