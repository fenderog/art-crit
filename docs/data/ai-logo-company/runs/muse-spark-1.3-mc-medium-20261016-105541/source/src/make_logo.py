"""Generate an organic neutral-tone logo for a generative-AI company (MERISTEM)."""
import math

SIZE = 1200
CX, CY = 600, 500  # mark centre (wordmark below)

# Neutral palette (warm paper + stone/sage/umber/charcoal)
PAPER = "#F1ECE2"
BONE = "#DCD2C1"
SAND = "#C2B6A3"
TAUPE = "#A09A8D"
SAGE = "#9AA092"
UMBER = "#776F63"
CHAR = "#33302B"

def blob_path(cx, cy, r, wobble, lobes, phase, steps=14):
    """Smooth closed organic blob as cubic bezier path."""
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        rr = r * (1 + wobble * math.sin(lobes * t + phase) + 0.5 * wobble * math.sin(2 * t + phase * 1.7))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    # Catmull-Rom -> Bezier closed spline
    n = len(pts)
    d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n):
        p0 = pts[(i - 1) % n]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + "Z"

# Five overlapping growth-cells spiralling out from centre (phyllotaxis-ish)
blobs = [
    dict(cx=CX - 150, cy=CY - 60,  r=215, wobble=0.16, lobes=3, phase=0.4, fill=BONE,  op=0.95),
    dict(cx=CX + 140, cy=CY - 110, r=190, wobble=0.18, lobes=3, phase=2.1, fill=SAND,  op=0.92),
    dict(cx=CX + 170, cy=CY + 120, r=175, wobble=0.15, lobes=4, phase=4.0, fill=SAGE,  op=0.88),
    dict(cx=CX - 130, cy=CY + 140, r=185, wobble=0.17, lobes=3, phase=1.2, fill=TAUPE, op=0.90),
    dict(cx=CX + 10,  cy=CY + 10,  r=150, wobble=0.14, lobes=5, phase=5.1, fill=UMBER, op=0.92),
    dict(cx=CX + 10,  cy=CY + 5,   r=72,  wobble=0.12, lobes=3, phase=0.9, fill=CHAR,  op=1.0),
]

# Small seed dots (generative nodes) along the overlaps
dots = [(CX - 235, CY - 170, 10), (CX + 255, CY - 195, 8), (CX + 285, CY + 190, 9), (CX - 240, CY + 215, 7)]

paths = []
for b in blobs:
    paths.append(
        f'<path d="{blob_path(b["cx"], b["cy"], b["r"], b["wobble"], b["lobes"], b["phase"])}" '
        f'fill="{b["fill"]}" opacity="{b["op"]}" stroke="{PAPER}" stroke-width="6"/>'
    )
for x, y, r in dots:
    paths.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CHAR}" opacity="0.85"/>')

# Fine connecting arcs suggesting a generative network, kept subtle
links = (
    f'<g fill="none" stroke="{CHAR}" stroke-width="2.5" opacity="0.35">'
    f'<path d="M {CX-235},{CY-170} Q {CX-60},{CY-140} {CX+10},{CY+5}"/>'
    f'<path d="M {CX+255},{CY-195} Q {CX+150},{CY-60} {CX+10},{CY+5}"/>'
    f'<path d="M {CX+285},{CY+190} Q {CX+140},{CY+120} {CX+10},{CY+5}"/>'
    f'<path d="M {CX-240},{CY+215} Q {CX-140},{CY+120} {CX+10},{CY+5}"/>'
    f'</g>'
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <rect width="{SIZE}" height="{SIZE}" rx="240" fill="{PAPER}"/>
  <g>
    {''.join(paths)}
    {links}
  </g>
  <text x="600" y="930" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="92" letter-spacing="26" fill="{CHAR}">MERISTEM</text>
  <text x="612" y="985" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="30" letter-spacing="10" fill="{UMBER}">GENERATIVE INTELLIGENCE</text>
</svg>
"""

with open("output/logo.svg", "w") as f:
    f.write(svg)
print("wrote output/logo.svg", len(svg), "bytes")
