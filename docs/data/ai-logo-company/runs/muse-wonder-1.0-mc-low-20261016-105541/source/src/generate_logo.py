#!/usr/bin/env python3
"""FORMA — generative AI logo. Organic bloom of five petals + generative nodes.
Neutral warm-stone palette. Outputs SVG (vector master) files to ./output/
"""
import math, pathlib
OUT = pathlib.Path("output"); OUT.mkdir(exist_ok=True)

# Neutral tones
INK   = "#2B2620"  # warm charcoal
CLAY  = "#7D7264"  # mid taupe-brown
TAUPE = "#A99B8A"  # taupe
SAND  = "#D8CFC0"  # sand
BONE  = "#F2EDE6"  # bone / off-white
SAGE  = "#969487"  # grey-sage neutral

def petal(cx, cy, angle, length=138, width=44, fill="", opacity=1):
    # Leaf/petal pointing up from centre, then rotated around centre.
    d = (f"M {cx} {cy+8} "
         f"C {cx-width} {cy-length*0.35} {cx-width*0.72} {cy-length*0.78} {cx} {cy-length} "
         f"C {cx+width*0.72} {cy-length*0.78} {cx+width} {cy-length*0.35} {cx} {cy+8} Z")
    return f'<path d="{d}" fill="{fill}" opacity="{opacity}" transform="rotate({angle} {cx} {cy})"/>'

def icon(cx=200, cy=200, mono=None, bg=None, idp="a"):
    """Bloom mark centred at cx,cy in its own coordinate space."""
    c = lambda col: (mono or col)
    parts = []
    if bg:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="188" fill="{bg}"/>')
    # generative node ring: dots on a loose organic orbit + faint links
    nodes = []
    for i in range(5):
        a = math.radians(-90 + i*72 + 18)
        r = 148
        nodes.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    links = "".join(
        f'<line x1="{nodes[i][0]:.1f}" y1="{nodes[i][1]:.1f}" x2="{nodes[(i+1)%5][0]:.1f}" y2="{nodes[(i+1)%5][1]:.1f}" stroke="{c(TAUPE)}" stroke-width="1.2" opacity="0.55"/>'
        for i in range(5))
    parts.append(links)
    # outer petals (sand), inner petals (taupe/clay) offset by 36deg
    for i in range(5):
        parts.append(petal(cx, cy, i*72,      132, 46, c(SAND),  0.95))
    for i in range(5):
        parts.append(petal(cx, cy, i*72 + 36, 104, 36, c(TAUPE), 0.90))
    for i in range(5):
        parts.append(petal(cx, cy, i*72 + 12,  72, 26, c(CLAY),  0.95))
    # seed / nucleus negative space
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="{c(BONE) if not bg else bg}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{c(INK)}" stroke-width="1.4" opacity="0.25"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{c(INK)}"/>')
    # nodes on top
    for i,(x,y) in enumerate(nodes):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if i%2 else 4.5}" fill="{c(INK)}"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{10.5 if i%2 else 9}" fill="none" stroke="{c(INK)}" stroke-width="1" opacity="0.35"/>')
    return "\n    ".join(parts)

FONT = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""

def svg(viewbox, body, title):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>FORMA generative AI — organic bloom mark in neutral warm-stone tones.</desc>
{body}
</svg>
'''

# 1 — Primary horizontal lockup (transparent)
primary = f'''  <g>
    {icon(160,160,idp="p")}
  </g>
  <g {FONT} fill="{INK}">
    <text x="368" y="168" font-size="72" font-weight="600" letter-spacing="14">FORMA</text>
    <text x="372" y="208" font-size="19" font-weight="400" letter-spacing="7.5" fill="{CLAY}">GENERATIVE&#160;AI</text>
  </g>
  <line x1="372" y1="182" x2="742" y2="182" stroke="{TAUPE}" stroke-width="1.2" opacity="0.7"/>'''
(OUT/"forma-logo-primary.svg").write_text(svg("0 0 820 320", primary, "FORMA — Generative AI (primary)"))

# 2 — Stacked lockup on bone background (presentation / app use)
stacked = f'''  <rect width="640" height="720" fill="{BONE}"/>
  <rect x="24" y="24" width="592" height="672" fill="none" stroke="{SAND}" stroke-width="1.5"/>
  {icon(320,290,idp="s")}
  <g {FONT} fill="{INK}" text-anchor="middle">
    <text x="320" y="548" font-size="64" font-weight="600" letter-spacing="16">FORMA</text>
    <text x="320" y="592" font-size="17" letter-spacing="8" fill="{CLAY}">GENERATIVE&#160;AI</text>
  </g>
  <line x1="250" y1="566" x2="390" y2="566" stroke="{TAUPE}" stroke-width="1.2"/>'''
(OUT/"forma-logo-stacked.svg").write_text(svg("0 0 640 720", stacked, "FORMA — Generative AI (stacked)"))

# 3 — Icon only (favicon / avatar, dark disc)
icon_only = f'''  <circle cx="200" cy="200" r="200" fill="{INK}"/>
  {icon(200,200, bg=None, idp="i")}'''
# recolour nucleus for dark ground: overpaint centre
icon_only = icon_only.replace(f'fill="{BONE}"/>', f'fill="{INK}"/>', 1)
(OUT/"forma-logo-icon.svg").write_text(svg("0 0 400 400", icon_only, "FORMA icon"))

# 4 — Monochrome (single-colour reproduction)
mono = f'''  <g>
    {icon(160,160, mono=INK, idp="m")}
  </g>
  <g {FONT} fill="{INK}">
    <text x="368" y="168" font-size="72" font-weight="600" letter-spacing="14">FORMA</text>
    <text x="372" y="208" font-size="19" letter-spacing="7.5">GENERATIVE&#160;AI</text>
  </g>
  <line x1="372" y1="182" x2="742" y2="182" stroke="{INK}" stroke-width="1.2"/>'''
(OUT/"forma-logo-mono.svg").write_text(svg("0 0 820 320", mono, "FORMA — monochrome"))

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))

# PNG preview of the stacked lockup (macOS sips, if available)
import shutil, subprocess
if shutil.which("sips"):
    subprocess.run(["sips", "-s", "format", "png",
                    str(OUT/"forma-logo-stacked.svg"),
                    "--out", str(OUT/"forma-logo-stacked.png")],
                   check=False, capture_output=True)
