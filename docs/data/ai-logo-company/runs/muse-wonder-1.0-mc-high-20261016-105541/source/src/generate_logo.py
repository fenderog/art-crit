#!/usr/bin/env python3
"""
FORMA — generative AI logo generator.

The mark is genuinely generative: six organic petals are produced by a
seeded algorithm. Each petal shares one grammar (a leaf drawn with two
cubic Beziers from a common centre) but receives its own length, width,
curvature and warp, so the bloom is rotationally ordered yet never
mechanical — generation with variation, which is the company's subject.

Palette is strictly neutral, warm stone tones on warm paper / charcoal.

Outputs (./output/):
  forma-logo-primary.svg   horizontal lockup, transparent
  forma-logo-stacked.svg   stacked lockup, transparent
  forma-logo-dark.svg      horizontal lockup on charcoal
  forma-logo-icon.svg      mark only
  forma-logo-primary.png   horizontal lockup on warm paper (via sips)
  forma-logo-icon.png      mark only on warm paper

Run: python3 src/generate_logo.py
PNG conversion uses macOS `sips` when available (no third-party packages).
"""
import math
import os
import random
import subprocess
import sys

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
OUT = os.path.normpath(OUT)

# --- neutral palette -------------------------------------------------
INK = "#2B2926"        # warm charcoal
INK_SOFT = "#3E3B36"
STONE = "#7E776C"
STONE_LIGHT = "#A99E8B"
SAND = "#C9BFA9"
SAND_LIGHT = "#DDD4BF"
PAPER = "#FAF7F1"
CREAM = "#F2EDE3"
DARK_BG = "#211F1C"

# petal fills on light ground: dark -> light around the bloom
PETALS_LIGHT = [INK, "#57534C", STONE, STONE_LIGHT, SAND, "#8A8376"]
# petal fills on dark ground: light -> mid, still neutral
PETALS_DARK = [CREAM, SAND_LIGHT, SAND, STONE_LIGHT, "#6E675C", "#E4DCC8"]

SEED = 11


def petal_path(cx, cy, angle_deg, length, width, warp, rng):
    """One organic leaf petal from centre (cx, cy) pointing at angle_deg."""
    a = math.radians(angle_deg)
    ux, uy = math.sin(a), -math.cos(a)          # along petal
    vx, vy = math.cos(a), math.sin(a)           # across petal
    w1 = warp * rng.uniform(-1, 1)
    w2 = warp * rng.uniform(-1, 1)

    tip = (cx + ux * length, cy + uy * length)
    # left edge: centre -> tip
    lc1 = (cx + vx * width * 0.95 + ux * length * 0.28,
           cy + vy * width * 0.95 + uy * length * 0.28)
    lc2 = (tip[0] + vx * width * (0.42 + w1 * 0.1) - ux * length * 0.30,
           tip[1] + vy * width * (0.42 + w1 * 0.1) - uy * length * 0.30)
    # right edge: tip -> centre
    rc1 = (tip[0] - vx * width * (0.42 + w2 * 0.1) - ux * length * 0.30,
           tip[1] - vy * width * (0.42 + w2 * 0.1) - uy * length * 0.30)
    rc2 = (cx - vx * width * 0.95 + ux * length * 0.28,
           cy - vy * width * 0.95 + uy * length * 0.28)

    def f(p):
        return f"{p[0]:.1f} {p[1]:.1f}"

    return (f"M {cx:.1f} {cy:.1f} C {f(lc1)} {f(lc2)} {f(tip)} "
            f"C {f(rc1)} {f(rc2)} {cx:.1f} {cy:.1f} Z")


def halo_path(cx, cy, r_base, rng):
    """Large soft irregular blob behind the bloom (polar noise, smoothed
    into cubic segments with the midpoint-quadratic technique)."""
    n = 9
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = r_base * (1 + 0.055 * math.sin(3 * t + 0.7)
                      + 0.04 * math.sin(5 * t) + rng.uniform(-0.02, 0.02))
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    # closed smooth path through midpoints
    def mid(p, q):
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)

    d = f"M {mid(pts[-1], pts[0])[0]:.1f} {mid(pts[-1], pts[0])[1]:.1f}"
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        m = mid(p, q)
        d += f" Q {p[0]:.1f} {p[1]:.1f} {m[0]:.1f} {m[1]:.1f}"
    return d + " Z"


def mark_group(palette, seed=SEED, halo_fill=SAND, halo_opacity=0.35):
    """Return SVG markup for the 120x120 mark (centred at 60,60)."""
    rng = random.Random(seed)
    parts = [f'<path d="{halo_path(60, 60, 47, rng)}" fill="{halo_fill}" '
             f'opacity="{halo_opacity}"/>']
    # six petals, 60 deg apart, each with generated variation
    specs = []
    for i in range(6):
        specs.append((i * 60 + rng.uniform(-5, 5),
                      rng.uniform(40, 48),
                      rng.uniform(15.0, 19.5),
                      rng.uniform(0.6, 1.4)))
    for (ang, length, width, warp), fill in zip(specs, palette):
        parts.append(
            f'<path d="{petal_path(60, 60, ang, length, width, warp, rng)}" '
            f'fill="{fill}" opacity="0.92"/>')
    # seed: the origin every generation starts from
    parts.append(f'<circle cx="60" cy="60" r="5.2" fill="{PAPER}"/>')
    parts.append(f'<circle cx="60" cy="60" r="2.4" fill="{INK}"/>')
    # three satellite nodes — models / data points orbiting the bloom
    for ang, dist, r in ((28, 52, 2.1), (152, 54, 1.7), (268, 51, 1.9)):
        a = math.radians(ang)
        x, y = 60 + dist * math.cos(a), 60 + dist * math.sin(a)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                     f'fill="{STONE}"/>')
    return "\n    ".join(parts)


FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


def svg_doc(width, height, viewbox, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{viewbox}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">FORMA generative AI logo: a six-petal organic bloom generated with per-petal variation, in warm neutral stone tones.</desc>
{body}
</svg>
'''


def horizontal(palette, word_fill, tag_fill, halo_fill, halo_op, bg=None, w=640, h=160, px_w=640):
    bg_rect = f'  <rect width="640" height="160" fill="{bg}"/>\n' if bg else ""
    body = f'''{bg_rect}  <g transform="translate(20 20)">
    {mark_group(palette, halo_fill=halo_fill, halo_opacity=halo_op)}
  </g>
  <text x="164" y="82" font-family="{FONT}" font-size="52" font-weight="600" letter-spacing="13" fill="{word_fill}">FORMA</text>
  <text x="167" y="114" font-family="{FONT}" font-size="12.5" font-weight="500" letter-spacing="5.5" fill="{tag_fill}">GENERATIVE AI</text>'''
    px_h = round(px_w * h / w)
    return svg_doc(px_w, px_h, f"0 0 {w} {h}", body, "FORMA — Generative AI")


def stacked(palette, word_fill, tag_fill, halo_fill, halo_op):
    body = f'''  <g transform="translate(120 28) scale(1)">
    {mark_group(palette, halo_fill=halo_fill, halo_opacity=halo_op)}
  </g>
  <text x="180" y="212" text-anchor="middle" font-family="{FONT}" font-size="46" font-weight="600" letter-spacing="12" fill="{word_fill}">FORMA</text>
  <text x="180" y="244" text-anchor="middle" font-family="{FONT}" font-size="11.5" font-weight="500" letter-spacing="5" fill="{tag_fill}">GENERATIVE AI</text>'''
    return svg_doc(360, 264, "0 0 360 264", body, "FORMA — Generative AI (stacked)")


def icon(palette, halo_fill, halo_op, bg=None, rounded=False, px=120):
    rx = ' rx="22"' if rounded else ""
    bg_rect = (f'  <rect width="120" height="120"{rx} fill="{bg}"/>\n'
               if bg else "")
    body = f'''{bg_rect}  <g>
    {mark_group(palette, halo_fill=halo_fill, halo_opacity=halo_op)}
  </g>'''
    return svg_doc(px, px, "0 0 120 120", body, "FORMA icon")


def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {path} ({len(content)} bytes)")
    return path


def to_png(svg_path, png_path):
    if subprocess.run(["which", "sips"], capture_output=True).returncode != 0:
        print(f"sips not available; skipping PNG for {svg_path}",
              file=sys.stderr)
        return
    subprocess.run(["sips", "-s", "format", "png", svg_path,
                    "--out", png_path], check=True, capture_output=True)
    print(f"wrote {png_path} ({os.path.getsize(png_path)} bytes)")


def main():
    os.makedirs(OUT, exist_ok=True)

    write("forma-logo-primary.svg",
          horizontal(PETALS_LIGHT, INK, STONE, SAND, 0.35))
    write("forma-logo-stacked.svg",
          stacked(PETALS_LIGHT, INK, STONE, SAND, 0.35))
    write("forma-logo-dark.svg",
          horizontal(PETALS_DARK, CREAM, SAND, CREAM, 0.10, bg=DARK_BG))
    write("forma-logo-icon.svg",
          icon(PETALS_LIGHT, SAND, 0.35))

    # PNG sources: same lockups with an explicit ground so the raster is
    # self-contained (temporary files, removed after conversion).
    tmp_primary = os.path.join(OUT, "_png_primary.svg")
    with open(tmp_primary, "w", encoding="utf-8") as fh:
        fh.write(horizontal(PETALS_LIGHT, INK, STONE, SAND, 0.35,
                            bg=PAPER, px_w=2560))
    tmp_icon = os.path.join(OUT, "_png_icon.svg")
    with open(tmp_icon, "w", encoding="utf-8") as fh:
        fh.write(icon(PETALS_LIGHT, SAND, 0.35, bg=PAPER, px=1024))
    try:
        to_png(tmp_primary, os.path.join(OUT, "forma-logo-primary.png"))
        to_png(tmp_icon, os.path.join(OUT, "forma-logo-icon.png"))
    finally:
        for tmp in (tmp_primary, tmp_icon):
            if os.path.exists(tmp):
                os.remove(tmp)


if __name__ == "__main__":
    main()
