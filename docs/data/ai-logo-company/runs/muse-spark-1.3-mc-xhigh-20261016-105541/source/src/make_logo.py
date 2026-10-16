#!/usr/bin/env python3
"""Generative-AI logo generator: 'loam — generative intelligence'.

Design: overlapping organic harmonic blobs (sand / stone / taupe) with an
open orbit ring and a small satellite 'spore' dot suggesting generation.
Warm neutral palette, vertical lockup with a serif wordmark.

Outputs (written by main()):
  ../output/loam-primary.svg   full lockup on bone
  ../output/loam-dark.svg      full lockup on charcoal
  ../output/loam-mark.svg      icon only, transparent background
  frames/frameXXX.svg          animation frames for the bloom video

Only the standard library is used. No randomness: fully deterministic.
"""

import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "..", "output")
FRAMES = os.path.join(HERE, "frames")

# ---------------------------------------------------------------- palettes
LIGHT = {
    "bg": "#F4EFE6",
    "blob_a": "#D9CDB2",   # sand
    "blob_b": "#B3A68C",   # stone
    "blob_c": "#7E7460",   # moss taupe
    "ring": "#6B6252",
    "sat": "#33302A",      # satellite spore
    "speck": "#B3A68C",
    "ink": "#33302A",      # wordmark
    "sub": "#6B6252",      # caption
}

DARK = {
    "bg": "#2C2924",
    "blob_a": "#CDBFA3",
    "blob_b": "#9A8E74",
    "blob_c": "#EFE7D6",
    "ring": "#B3A68C",
    "sat": "#EFE7D6",
    "speck": "#9A8E74",
    "ink": "#F4EFE6",
    "sub": "#CDBFA3",
}

# ------------------------------------------------------- organic blob math
def blob_samples(cx, cy, r, a3, p3, a2, p2, n=16):
    """Sample a smooth harmonic blob: r(t) = R*(1 + a3*cos(3t+p3) + a2*cos(2t+p2))."""
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        rr = r * (1.0 + a3 * math.cos(3 * t + p3) + a2 * math.cos(2 * t + p2))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return pts


def smooth_closed_path(pts):
    """Closed Catmull-Rom spline through pts -> cubic Bezier path data."""
    n = len(pts)
    d = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    d.append("Z")
    return " ".join(d)


def blob_path(cx, cy, r, a3, p3, a2, p2, n=16):
    return smooth_closed_path(blob_samples(cx, cy, r, a3, p3, a2, p2, n))


def arc_path(cx, cy, r, a0_deg, a1_deg):
    """Circular arc from angle a0 to a1 (degrees, SVG y-down convention)."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    sweep = (a1_deg - a0_deg) % 360.0
    large = 1 if sweep > 180.0 else 0
    return f"M {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {large} 1 {x1:.2f} {y1:.2f}"


# ---------------------------------------------------------------- mark
# Blob shape recipes: (key, cx, cy, r, a3, p3, a2, p2)
BLOBS = [
    ("blob_a", 400, 480, 215, 0.055, 0.6, 0.040, 2.1),
    ("blob_b", 522, 418, 168, 0.060, 2.4, 0.045, 0.3),
    ("blob_c", 458, 542, 132, 0.065, 4.2, 0.050, 5.0),
]

SAT_ANGLE = -38.0      # degrees; upper right
SAT_DIST = 302.0
SAT_R = 34.0
RING_R = 302.0
GAP_HALF = 23.0        # ring gap half-width in degrees


def mark_group(pal, breathe=0.0, sat_angle=SAT_ANGLE, sat_dist=SAT_DIST):
    """SVG <g> of the mark. breathe: fractional radius pulse. Angles in degrees."""
    s = (1.0 + breathe) if not isinstance(breathe, tuple) else None
    parts = []
    for key, cx, cy, r, a3, p3, a2, p2 in BLOBS:
        pulse = 1.0 + breathe if isinstance(breathe, float) else 1.0
        parts.append(
            f'<path d="{blob_path(cx, cy, r * pulse, a3, p3, a2, p2)}" fill="{pal[key]}"/>'
        )
    # orbit ring with a gap where the satellite sits
    parts.append(
        f'<path d="{arc_path(450, 470, RING_R, sat_angle + GAP_HALF, sat_angle + 360 - GAP_HALF)}" '
        f'fill="none" stroke="{pal["ring"]}" stroke-width="9" stroke-linecap="round" opacity="0.85"/>'
    )
    # trailing speck on the ring, just behind the satellite
    th = math.radians(sat_angle + 26)
    sx, sy = 450 + (RING_R - 4) * math.cos(th), 470 + (RING_R - 4) * math.sin(th)
    parts.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="10" fill="{pal["speck"]}"/>')
    # satellite spore: a tiny organic blob, not a perfect circle
    sa = math.radians(sat_angle)
    scx, scy = 450 + sat_dist * math.cos(sa), 470 + sat_dist * math.sin(sa)
    parts.append(
        f'<path d="{blob_path(scx, scy, SAT_R * (1.0 + breathe), 0.07, 1.1, 0.05, 3.3, n=12)}" '
        f'fill="{pal["sat"]}"/>'
    )
    return "\n      ".join(parts)


GRAIN = """
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>"""


def grain_rect(w, h, opacity=0.05):
    return f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity="{opacity}"/>'


def lockup_svg(pal, with_bg=True):
    """Full vertical lockup: mark + 'loam' wordmark + caption. Square 1600x1600
    so system thumbnail renderers capture the whole composition uncropped."""
    bg = f'  <rect width="1600" height="1600" fill="{pal["bg"]}"/>\n' if with_bg else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1600" viewBox="0 0 1600 1600">
  <title>loam — generative intelligence</title>
  <defs>{GRAIN}
  </defs>
{bg}  <g transform="translate(800 560) scale(0.92) translate(-450 -470)">
      {mark_group(pal)}
  </g>
  <text x="800" y="1205" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="190" letter-spacing="2" fill="{pal["ink"]}">loam</text>
  <text x="806" y="1300" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="35" letter-spacing="13" fill="{pal["sub"]}">GENERATIVE INTELLIGENCE</text>
  {grain_rect(1600, 1600, opacity=0.04)}
</svg>
"""


def mark_svg(pal, with_bg=False):
    """Icon only. 1000x1000, transparent unless with_bg."""
    bg = f'  <rect width="1000" height="1000" fill="{pal["bg"]}"/>\n' if with_bg else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <title>loam mark</title>
  <defs>{GRAIN}
  </defs>
{bg}  <g transform="translate(500 492) scale(1.02) translate(-450 -470)">
      {mark_group(pal)}
  </g>
  {grain_rect(1000, 1000, opacity=0.04 if with_bg else 0.0)}
</svg>
"""


def frame_svg(pal, t):
    """Animation frame (t in 0..1): gentle breathing + satellite drift. 960x960."""
    breathe = 0.035 * math.sin(2 * math.pi * t)
    sat_angle = SAT_ANGLE + 9.0 * math.sin(2 * math.pi * t)
    sat_dist = SAT_DIST + 9.0 * math.sin(2 * math.pi * t + 1.2)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="960" viewBox="0 0 960 960">
  <rect width="960" height="960" fill="{pal["bg"]}"/>
  <g transform="translate(480 470) scale(1.0) translate(-450 -470)">
      {mark_group(pal, breathe=breathe, sat_angle=sat_angle, sat_dist=sat_dist)}
  </g>
  <text x="480" y="872" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="72" letter-spacing="2" fill="{pal["ink"]}">loam</text>
</svg>
"""


def main():
    os.makedirs(OUTPUT, exist_ok=True)
    files = {
        "loam-primary.svg": lockup_svg(LIGHT),
        "loam-dark.svg": lockup_svg(DARK),
        "loam-mark.svg": mark_svg(LIGHT),
    }
    for name, content in files.items():
        with open(os.path.join(OUTPUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", name, len(content), "bytes")

    os.makedirs(FRAMES, exist_ok=True)
    n = 144  # 6 s at 24 fps
    for i in range(n):
        with open(os.path.join(FRAMES, f"frame{i:03d}.svg"), "w", encoding="utf-8") as f:
            f.write(frame_svg(LIGHT, i / n))
    print("wrote", n, "frames to", FRAMES)


if __name__ == "__main__":
    main()
