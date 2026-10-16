"""Generate an organic, neutral-toned SVG logo for "Mycel", a generative AI company.

Each mark is a set of smooth, closed blob outlines whose radii are perturbed by
seeded noise, so the output is deterministic. Blobs are drawn with
multiply-style blending so overlaps read like layered ink or stone.
"""

import math
import random
from pathlib import Path

WIDTH, HEIGHT = 800, 800
SEED = 7
OUT = Path(__file__).resolve().parent.parent / "output" / "mycel-logo.svg"

# Neutral palette: warm greys, sand, taupe, stone, bone.
PALETTE = {
    "bone": "#F3EFE8",
    "sand": "#D9CFC1",
    "taupe": "#B0A596",
    "stone": "#8A8178",
    "umber": "#5E5750",
    "ink": "#2F2B28",
}


def blob_path(cx, cy, r, wobble, points, rng, phase=0.0):
    """Return a closed smooth SVG path (Catmull-Rom converted to cubic Bezier)."""
    # Low-frequency noise: a few random harmonics give a soft, organic outline.
    harmonics = [(k, rng.uniform(0.4, 1.0) / k, rng.uniform(0, 2 * math.pi)) for k in (2, 3, 4, 5)]
    pts = []
    for i in range(points):
        t = 2 * math.pi * i / points + phase
        n = sum(a * math.sin(k * t + ph) for k, a, ph in harmonics)
        rad = r * (1 + wobble * n / 2.0)
        pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))

    d = [f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"]
    for i in range(points):
        p0 = pts[(i - 1) % points]
        p1 = pts[i]
        p2 = pts[(i + 1) % points]
        p3 = pts[(i + 2) % points]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(
            f"C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}"
        )
    return " ".join(d) + "Z"


def build():
    rng = random.Random(SEED)
    shapes = []

    # Background: bone paper with a soft radial sand glow.
    shapes.append(
        f'<defs><radialGradient id="glow" cx="50%" cy="45%" r="60%">'
        f'<stop offset="0%" stop-color="{PALETTE["bone"]}"/>'
        f'<stop offset="100%" stop-color="{PALETTE["sand"]}"/>'
        f"</radialGradient>"
        f'<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feGaussianBlur stdDeviation="1.2"/></filter></defs>'
    )
    shapes.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#glow)"/>')

    # Central mark: a cluster of nested organic lobes, like a growing colony.
    cx, cy = 400, 360
    layers = [
        # (offset_x, offset_y, radius, wobble, color, opacity)
        (0, 0, 170, 0.22, PALETTE["taupe"], 0.85),
        (-70, 30, 120, 0.25, PALETTE["stone"], 0.55),
        (80, -40, 110, 0.28, PALETTE["sand"], 0.7),
        (30, 80, 90, 0.3, PALETTE["umber"], 0.35),
        (-40, -60, 70, 0.26, PALETTE["bone"], 0.8),
    ]
    shapes.append('<g style="mix-blend-mode:multiply" filter="url(#soft)">')
    for ox, oy, r, wob, color, op in layers:
        d = blob_path(cx + ox, cy + oy, r, wob, 9, rng, phase=rng.uniform(0, 1))
        shapes.append(f'<path d="{d}" fill="{color}" fill-opacity="{op}"/>')
    shapes.append("</g>")

    # Filaments: thin tapering strokes radiating from the core, suggesting a
    # hyphal network that generates outward.
    shapes.append(
        f'<g fill="none" stroke="{PALETTE["umber"]}" stroke-linecap="round" opacity="0.8">'
    )
    for i in range(7):
        a0 = rng.uniform(0, 2 * math.pi)
        length = rng.uniform(190, 240)
        x0, y0 = cx + 150 * math.cos(a0), cy + 150 * math.sin(a0)
        bend = rng.uniform(-0.6, 0.6)
        a1 = a0 + bend
        x1, y1 = cx + length * math.cos(a1), cy + length * math.sin(a1)
        mx = (x0 + x1) / 2 + 40 * math.cos(a0 + math.pi / 2) * bend
        my = (y0 + y1) / 2 + 40 * math.sin(a0 + math.pi / 2) * bend
        width = rng.uniform(1.6, 3.0)
        shapes.append(
            f'<path d="M{x0:.2f},{y0:.2f} Q{mx:.2f},{my:.2f} {x1:.2f},{y1:.2f}" '
            f'stroke-width="{width:.2f}"/>'
        )
    shapes.append("</g>")

    # Wordmark, set in a rounded-sans fallback stack.
    shapes.append(
        f'<text x="400" y="650" text-anchor="middle" '
        f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
        f'font-size="64" font-weight="300" letter-spacing="14" fill="{PALETTE["ink"]}">MYCEL</text>'
    )
    shapes.append(
        f'<text x="400" y="695" text-anchor="middle" '
        f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" '
        f'font-size="15" letter-spacing="5" fill="{PALETTE["stone"]}">GENERATIVE SYSTEMS</text>'
    )

    body = "\n  ".join(shapes)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Mycel logo">\n'
        f"  <title>Mycel</title>\n  {body}\n</svg>\n"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}")
