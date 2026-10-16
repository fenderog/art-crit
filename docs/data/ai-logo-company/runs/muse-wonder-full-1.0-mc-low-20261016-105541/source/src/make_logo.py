#!/usr/bin/env python3
"""Forma — generative AI logo. Organic tri-petal / seed mark in neutral warm tones."""
import pathlib, math
OUT = pathlib.Path("output"); OUT.mkdir(exist_ok=True)

# Neutral palette
INK    = "#2B2620"  # espresso
STONE  = "#8A7D6B"  # stone
TAUPE  = "#B3A48F"  # taupe
SAND   = "#D6CBB8"  # sand
CREAM  = "#F4F0E8"  # warm cream
SAGE   = "#A3A596"  # muted sage-grey (still neutral)
CLAY   = "#C4B29E"

# One organic petal, pointing up, origin = mark centre.
# Asymmetric cubic blob — fat shoulder left, tapered waist right.
PETAL = ("M 0 16 "
         "C -40 -14 -46 -68 -2 -106 "
         "C 38 -74 34 -16 0 16 Z")

def mark(cx, cy, scale, colors, center_dot, nodes=True, opacities=(1,1,1), ring=None):
    """Return SVG group for the tri-petal mark centred at cx,cy."""
    parts = [f'<g transform="translate({cx} {cy}) scale({scale})">']
    if ring:
        parts.append(f'<circle r="132" fill="none" stroke="{ring}" stroke-width="1.4" '
                     f'stroke-dasharray="2 7" stroke-linecap="round" opacity="0.55"/>')
    for i,(col,op) in enumerate(zip(colors,opacities)):
        ang = -18 + i*120
        parts.append(f'<path d="{PETAL}" fill="{col}" opacity="{op}" transform="rotate({ang})"/>')
    # generative nodes: small satellite dots just beyond each petal tip
    if nodes:
        for i in range(3):
            ang = math.radians(-18 + i*120)
            dx, dy = math.sin(ang), -math.cos(ang)
            nx, ny = dx*118, dy*118
            parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{4.6-i*0.6:.1f}" fill="{colors[i]}"/>')
    # negative-space seed at centre
    parts.append(f'<circle r="9.5" fill="{center_dot}"/>')
    parts.append('</g>')
    return "\n".join(parts)

def svg(w,h,body,bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="Forma — generative AI logo">\n'
            f'<title>Forma — Generative AI</title>\n{bgrect}\n{body}\n</svg>\n')

FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"

def wordmark(x, y, size, color, tag_color, anchor="start", tag=True):
    t = [f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="650" '
         f'letter-spacing="-1.5" fill="{color}" text-anchor="{anchor}">forma</text>']
    if tag:
        # nudge tagline to align under wordmark depending on anchor
        tx = x + 3 if anchor=="start" else x
        t.append(f'<text x="{tx}" y="{y+size*0.52:.0f}" font-family="{FONT}" font-size="{size*0.205:.1f}" '
                 f'font-weight="560" letter-spacing="6.5" fill="{tag_color}" text-anchor="{anchor}">GENERATIVE AI</text>')
    return "\n".join(t)

# ---------- 1. Primary horizontal lockup on cream ----------
body = mark(150,150,0.92,[INK,TAUPE,SAND],CREAM) + wordmark(300,158,86,INK,STONE)
(OUT/"forma-logo-primary.svg").write_text(svg(760,300,body,CREAM))

# ---------- 2. Dark lockup ----------
body = mark(150,150,0.92,[SAND,TAUPE,STONE],INK) + wordmark(300,158,86,CREAM,"#A99F8E")
(OUT/"forma-logo-dark.svg").write_text(svg(760,300,body,INK))

# ---------- 3. Icon only (transparent) ----------
body = mark(160,160,1.05,[INK,TAUPE,SAND],CREAM, ring=STONE)
(OUT/"forma-icon.svg").write_text(svg(320,320,body))

# ---------- 4. Mono lockup (single-colour, transparent) ----------
body = mark(150,150,0.92,[INK,INK,INK],CREAM,opacities=(1,0.62,0.32)) + wordmark(300,158,86,INK,INK)
(OUT/"forma-logo-mono.svg").write_text(svg(760,300,body))

# ---------- 5. App-icon / avatar (squircle) ----------
body = (f'<rect x="8" y="8" width="304" height="304" rx="72" fill="{INK}"/>'
        + mark(160,160,0.98,[SAND,TAUPE,STONE],INK,ring="#6E6355"))
(OUT/"forma-app-icon.svg").write_text(svg(320,320,body))

# ---------- 6. Brand sheet ----------
def swatch(x,y,col,name,hexv):
    return (f'<rect x="{x}" y="{y}" width="104" height="72" rx="16" fill="{col}" stroke="#00000018"/>'
            f'<text x="{x}" y="{y+94}" font-family="{FONT}" font-size="13" font-weight="650" fill="{INK}">{name}</text>'
            f'<text x="{x}" y="{y+112}" font-family="{FONT}" font-size="11" fill="{STONE}">{hexv}</text>')

sheet = []
sheet.append(f'<rect width="1200" height="1500" fill="{CREAM}"/>')
sheet.append(f'<text x="72" y="92" font-family="{FONT}" font-size="15" font-weight="650" letter-spacing="5" fill="{STONE}">BRAND MARK  ·  GENERATIVE AI</text>')
# hero lockup
sheet.append(mark(210,300,1.25,[INK,TAUPE,SAND],CREAM))
sheet.append(wordmark(420,318,118,INK,STONE))
sheet.append(f'<text x="72" y="520" font-family="{FONT}" font-size="19" fill="#5C554B">Three organic petals grow from a single seed — a form being generated,</text>')
sheet.append(f'<text x="72" y="550" font-family="{FONT}" font-size="19" fill="#5C554B">not drawn. Small nodes at each tip hint at the model behind the bloom.</text>')
# divider
sheet.append(f'<line x1="72" y1="610" x2="1128" y2="610" stroke="{SAND}" stroke-width="2"/>')
# variations row: dark tile, app icon, mono
sheet.append(f'<text x="72" y="668" font-family="{FONT}" font-size="14" font-weight="650" letter-spacing="4" fill="{STONE}">VARIATIONS</text>')
sheet.append(f'<rect x="72" y="692" width="330" height="330" rx="28" fill="{INK}"/>')
sheet.append(mark(237,857,1.18,[SAND,TAUPE,STONE],INK))
sheet.append(f'<rect x="435" y="692" width="330" height="330" rx="28" fill="#EAE3D6"/>')
sheet.append(mark(600,857,1.18,[INK,INK,INK],CREAM,opacities=(1,0.62,0.32)))
sheet.append(f'<rect x="798" y="692" width="330" height="330" rx="72" fill="{INK}"/>')
sheet.append(mark(963,857,1.05,[SAND,TAUPE,SAGE],INK,ring="#6E6355"))
for x,label in [(72,"On dark"),(435,"Mono — one colour"),(798,"App icon")]:
    sheet.append(f'<text x="{x}" y="1056" font-family="{FONT}" font-size="14" font-weight="600" fill="{INK}">{label}</text>')
# scale test
sheet.append(f'<text x="72" y="1130" font-family="{FONT}" font-size="14" font-weight="650" letter-spacing="4" fill="{STONE}">SCALE</text>')
for s,x in [(0.55,130),(0.34,270),(0.20,380),(0.11,460)]:
    sheet.append(mark(x,1215,s,[INK,TAUPE,SAND],CREAM,nodes=(s>0.15)))
sheet.append(wordmark(560,1235,54,INK,STONE))
# palette
sheet.append(f'<text x="72" y="1345" font-family="{FONT}" font-size="14" font-weight="650" letter-spacing="4" fill="{STONE}">NEUTRAL PALETTE</text>')
pal = [(INK,"Espresso"),(STONE,"Stone"),(TAUPE,"Taupe"),(CLAY,"Clay"),(SAND,"Sand"),(SAGE,"Sage grey"),(CREAM,"Cream")]
for i,(c,n) in enumerate(pal):
    sheet.append(swatch(72+i*152,1365,c,n,c))
(OUT/"forma-brand-sheet.svg").write_text(svg(1200,1500,"\n".join(sheet)))

print("wrote:", sorted(p.name for p in OUT.iterdir()))
