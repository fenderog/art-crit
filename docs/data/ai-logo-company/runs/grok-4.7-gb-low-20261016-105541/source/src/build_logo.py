#!/usr/bin/env python3
"""Build the Calyx logo: an organic seed-pod mark and an outlined wordmark."""

import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "output"
OUTLINER = Path("/tmp/calyx-outline")

INK = "#2A2826"
TAUPE = "#8F877C"
STONE = "#C4BBB0"
PAPER = "#F3EFE8"
MIST = "#E6E0D6"

# Harmonic radii keep the silhouette soft without three-fold symmetry.
def contour(cx, cy, rx, ry, rot_deg, harmonics, samples=14, taper_top=0.0):
    rot = math.radians(rot_deg)
    pts = []
    for i in range(samples):
        t = 2 * math.pi * i / samples
        rmod = 1.0
        for k, amp, phase in harmonics:
            rmod += amp * math.sin(k * t + phase)
        x = math.cos(t) * rx * rmod
        y = math.sin(t) * ry * rmod
        # Smooth shoulder: full width at the sides, narrower toward the top. No kink at the equator.
        if taper_top:
            up = max(0.0, -math.sin(t))
            scale = 1.0 - taper_top * up * up
            x *= scale
            y *= 0.9 + 0.1 * scale
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        pts.append((cx + xr, cy + yr))
    # Uniform Catmull-Rom (tension 0.5) as cubic beziers.
    d = []
    n = len(pts)
    d.append(f"M {pts[0][0]:.2f} {pts[0][1]:.2f}")
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(
            f"C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
        )
    d.append("Z")
    return " ".join(d), pts


def translate_path(d, dx, dy):
    nums = []
    parts = d.replace(",", " ").split()
    out = []
    i = 0
    # Commands and coordinates alternate in our generator: letter, then pairs.
    while i < len(parts):
        token = parts[i]
        if token in ("M", "L", "C", "Q", "Z"):
            out.append(token)
            i += 1
            count = {"M": 1, "L": 1, "C": 3, "Q": 2, "Z": 0}[token]
            for _ in range(count):
                x = float(parts[i]) + dx
                y = float(parts[i + 1]) + dy
                out.append(f"{x:.2f}")
                out.append(f"{y:.2f}")
                i += 2
        else:
            raise SystemExit(f"unexpected path token {token}")
    return " ".join(out)


def outline(font, size, kern, text):
    proc = subprocess.run(
        [str(OUTLINER), font, str(size), str(kern), text],
        check=True,
        capture_output=True,
        text=True,
    )
    width, ascent, descent, path = proc.stdout.splitlines()
    return {
        "width": float(width),
        "ascent": float(ascent),
        "descent": float(descent),
        "d": path,
    }


def mark_paths():
    # Upright pod, heavier through the lower left, shoulder opening upper right.
    outer = contour(
        188,
        240,
        112,
        186,
        -14,
        [(1, 0.045, 0.7), (2, 0.07, 0.25), (3, 0.03, 1.15)],
        samples=16,
        taper_top=0.22,
    )
    # Off-center aperture high in the pod: a split, not a centered ring.
    inner = contour(
        196,
        178,
        36,
        50,
        24,
        [(1, 0.12, 0.3), (2, 0.055, 1.05), (3, -0.03, 0.5)],
        samples=12,
    )
    # Sepal tucked under the upper-right rim, partly visible through the split.
    sepal = contour(
        250,
        158,
        62,
        80,
        32,
        [(1, 0.08, 1.5), (2, 0.07, 0.45), (3, 0.03, 2.0)],
        samples=14,
        taper_top=0.12,
    )
    return outer, inner, sepal


def inside(pt, poly):
    x, y = pt
    n = len(poly)
    hit = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            hit = not hit
        j = i
    return hit


def svg_mark(outer, inner, sepal, vb, ink=INK, sepal_fill=TAUPE, paper=None):
    bg = f'  <rect width="100%" height="100%" fill="{paper}"/>\n' if paper else ""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb[0]:.2f} {vb[1]:.2f}" role="img" aria-labelledby="title desc">
  <title id="title">Calyx</title>
  <desc id="desc">Logo mark for Calyx, a generative AI company. An organic seed pod in warm neutral tones.</desc>
{bg}  <path fill="{sepal_fill}" d="{sepal}"/>
  <path fill="{ink}" fill-rule="evenodd" d="{outer} {inner}"/>
</svg>
'''


def svg_lockup(outer, inner, sepal, word, label, mark_vb, ink=INK, sepal_fill=TAUPE, label_fill=TAUPE):
    gap = 64
    word_x = mark_vb[0] + gap
    label_dy = 78
    block_h = word["ascent"] + label_dy + label["descent"]
    word_baseline = (mark_vb[1] - block_h) / 2 + word["ascent"] + 4
    label_baseline = word_baseline + label_dy
    label_x = word_x + 2
    width = word_x + max(word["width"], label["width"] + 2) + 4
    height = mark_vb[1]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" role="img" aria-labelledby="title desc">
  <title id="title">Calyx</title>
  <desc id="desc">Calyx wordmark and seed-pod mark. Generative AI company logo in warm neutral tones.</desc>
  <path fill="{sepal_fill}" d="{sepal}"/>
  <path fill="{ink}" fill-rule="evenodd" d="{outer} {inner}"/>
  <path fill="{ink}" transform="translate({word_x:.2f} {word_baseline:.2f})" d="{word["d"]}"/>
  <path fill="{label_fill}" transform="translate({label_x:.2f} {label_baseline:.2f})" d="{label["d"]}"/>
</svg>
'''


def svg_stacked(outer, inner, sepal, word, mark_vb, ink=INK, sepal_fill=TAUPE):
    word_w = word["width"]
    pad = 36
    mark_scale = 0.92
    mark_w = mark_vb[0] * mark_scale
    mark_h = mark_vb[1] * mark_scale
    canvas_w = max(mark_w + pad * 2, word_w + pad * 2)
    mark_x = (canvas_w - mark_w) / 2
    mark_y = pad
    word_x = (canvas_w - word_w) / 2
    word_baseline = mark_y + mark_h + 28 + word["ascent"]
    height = word_baseline + word["descent"] + pad
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w:.2f} {height:.2f}" role="img" aria-labelledby="title desc">
  <title id="title">Calyx</title>
  <desc id="desc">Stacked Calyx logo: organic seed-pod mark over the wordmark.</desc>
  <g transform="translate({mark_x:.2f} {mark_y:.2f}) scale({mark_scale})">
    <path fill="{sepal_fill}" d="{sepal}"/>
    <path fill="{ink}" fill-rule="evenodd" d="{outer} {inner}"/>
  </g>
  <path fill="{ink}" transform="translate({word_x:.2f} {word_baseline:.2f})" d="{word["d"]}"/>
</svg>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not OUTLINER.exists():
        subprocess.run(
            ["swiftc", "-O", "-o", str(OUTLINER), str(SRC / "outline.swift")],
            check=True,
        )
    (outer_d, outer_pts), (inner_d, inner_pts), (sepal_d, sepal_pts) = mark_paths()
    outside = [p for p in inner_pts if not inside(p, outer_pts)]
    if outside:
        raise SystemExit(f"aperture leaves the pod at {len(outside)} points")

    pts = outer_pts + sepal_pts
    minx = min(p[0] for p in pts)
    miny = min(p[1] for p in pts)
    maxx = max(p[0] for p in pts)
    maxy = max(p[1] for p in pts)
    pad = 28
    dx, dy = pad - minx, pad - miny
    outer_d = translate_path(outer_d, dx, dy)
    inner_d = translate_path(inner_d, dx, dy)
    sepal_d = translate_path(sepal_d, dx, dy)
    vb = (maxx - minx + pad * 2, maxy - miny + pad * 2)

    word = outline("Optima-Regular", 132, 5.5, "CALYX")
    label = outline("AvenirNext-Regular", 26, 8.5, "GENERATIVE")
    stacked_word = outline("Optima-Regular", 86, 4.0, "CALYX")

    mark = svg_mark(outer_d, inner_d, sepal_d, vb)
    lockup = svg_lockup(outer_d, inner_d, sepal_d, word, label, vb)
    stacked = svg_stacked(outer_d, inner_d, sepal_d, stacked_word, vb)
    inverse = svg_mark(outer_d, inner_d, sepal_d, vb, ink=PAPER, sepal_fill=STONE, paper=INK)

    files = {
        "calyx-mark.svg": mark,
        "calyx-lockup.svg": lockup,
        "calyx-stacked.svg": stacked,
        "calyx-mark-inverse.svg": inverse,
    }
    for name, text in files.items():
        (OUT / name).write_text(text)
        print(name, f"{vb[0]:.1f}x{vb[1]:.1f}", len(text))


if __name__ == "__main__":
    main()
