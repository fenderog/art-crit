#!/usr/bin/env python3
"""Draw an octopus chef working a night-market ramen booth.

The illustration is a single SVG. Sign and menu lettering is outlined
(see glyphs.py) so it stays put without embedded fonts.

Run: python3 src/generate_octopus_ramen.py
"""

import math
import os
from pathlib import Path

from glyphs import GLYPHS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "octopus-chef-ramen.svg"

W, H = 1200, 1200
DEBUG = os.environ.get("DEBUG") == "1"

# Locked stage geometry. Tweaked against raster previews.
HEAD = (600, 478, 162, 132)  # cx, cy, rx, ry
HAT_CX = 598
HAT_TOP = 96
HAT_BAND_Y = 348
BOWL_C = (804, 872)
BOWL_RX, BOWL_RY = 196, 74
POT_C = (308, 692)
POT_RX, POT_RY = 112, 42


def fmt(v):
    if isinstance(v, str):
        return v
    s = f"{float(v):.1f}"
    return s[:-2] if s.endswith(".0") else s


def poly(pts, close=True):
    if not pts:
        return ""
    cmds = [f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"]
    cmds.extend(f"L{fmt(x)} {fmt(y)}" for x, y in pts[1:])
    if close:
        cmds.append("Z")
    return "".join(cmds)


def catmull(points, samples=12):
    if len(points) < 2:
        return list(points)
    p = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for s in range(samples):
            t = s / samples
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            out.append((x, y))
    out.append(points[-1])
    return out


def resample(pts, step=4.2):
    if len(pts) < 2:
        return list(pts)
    seglen = []
    total = 0.0
    for i in range(1, len(pts)):
        L = math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        seglen.append(L)
        total += L
    if total < step:
        return [pts[0], pts[-1]]
    out = [pts[0]]
    target = step
    seg_i = 0
    acc = 0.0
    while target < total - 0.01 and seg_i < len(seglen):
        while seg_i < len(seglen) and acc + seglen[seg_i] < target:
            acc += seglen[seg_i]
            seg_i += 1
        if seg_i >= len(seglen) or seglen[seg_i] < 1e-8:
            break
        local = (target - acc) / seglen[seg_i]
        x0, y0 = pts[seg_i]
        x1, y1 = pts[seg_i + 1]
        out.append((x0 + (x1 - x0) * local, y0 + (y1 - y0) * local))
        target += step
    out.append(pts[-1])
    return out


def append_spiral(pts, turns=0.7, radius=26, clockwise=True, samples=26):
    """Hook the tip into a tightening curl whose start tangent matches the arm."""
    if len(pts) < 2 or radius <= 1:
        return pts
    x1, y1 = pts[-1]
    x0, y0 = pts[-2]
    direction = math.atan2(y1 - y0, x1 - x0)
    sign = 1.0 if clockwise else -1.0
    raw = []
    for i in range(samples + 1):
        t = i / samples
        theta = sign * t * turns * math.tau
        r = radius * (1 - t * 0.86)
        raw.append((r * math.cos(theta) - radius, r * math.sin(theta)))
    tang = math.atan2(raw[1][1] - raw[0][1], raw[1][0] - raw[0][0])
    rot = direction - tang
    ca, sa = math.cos(rot), math.sin(rot)
    out = list(pts)
    for x, y in raw[1:]:
        out.append((x1 + x * ca - y * sa, y1 + x * sa + y * ca))
    return out


def normals(pts):
    n = len(pts)
    raw = []
    for i in range(n):
        if i == 0:
            dx = pts[1][0] - pts[0][0]
            dy = pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx = pts[-1][0] - pts[-2][0]
            dy = pts[-1][1] - pts[-2][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        raw.append((-dy / L, dx / L))
    fixed = [raw[0]]
    for i in range(1, n):
        nx, ny = raw[i]
        if nx * fixed[-1][0] + ny * fixed[-1][1] < 0:
            nx, ny = -nx, -ny
        fixed.append((nx, ny))
    cur = fixed
    for _ in range(2):
        nxt = [cur[0]]
        for i in range(1, n - 1):
            x = cur[i - 1][0] + cur[i][0] + cur[i + 1][0]
            y = cur[i - 1][1] + cur[i][1] + cur[i + 1][1]
            L = math.hypot(x, y) or 1.0
            nxt.append((x / L, y / L))
        nxt.append(cur[-1])
        cur = nxt
    return cur


def width_profile(n, base, tip, bulge=0.08):
    ws = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        w = tip + (base - tip) * (1 - t) ** 0.76
        w *= 1 + bulge * math.sin(math.pi * t)
        ws.append(w)
    return ws


def semi_cap(tip, normal, width, forward=True, n=8):
    nx, ny = normal
    dx, dy = (ny, -nx) if forward else (-ny, nx)
    hw = width / 2
    pts = []
    for i in range(1, n):
        a = math.pi * i / n
        pts.append(
            (
                tip[0] + hw * (math.cos(a) * nx + math.sin(a) * dx),
                tip[1] + hw * (math.cos(a) * ny + math.sin(a) * dy),
            )
        )
    return pts


def ribbon_edges(pts, widths, norms):
    left, right = [], []
    for (x, y), (nx, ny), w in zip(pts, norms, widths):
        hw = w / 2
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    cap = semi_cap(pts[-1], norms[-1], widths[-1], True)
    base = semi_cap(pts[0], norms[0], widths[0], False)
    outline = left + cap + list(reversed(right)) + list(reversed(base))
    return outline, left, right


def sucker_positions(pts, widths, norms, side, rows):
    found = []
    dist = 0.0
    next_at = max(8.0, widths[0] * 0.55)
    next_row2 = next_at + 9
    for i in range(1, len(pts) - 1):
        dist += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        t = i / (len(pts) - 1)
        w = widths[i]
        r = max(2.4, w * 0.268)
        spacing = max(r * 2.2, 7.5)
        nx, ny = norms[i]
        if 0.07 < t < 0.9 and dist >= next_at:
            found.append(
                (
                    pts[i][0] + side * nx * w * 0.04,
                    pts[i][1] + side * ny * w * 0.04,
                    r,
                )
            )
            next_at = dist + spacing
        if rows >= 2 and w > 18 and 0.12 < t < 0.86 and dist >= next_row2:
            r2 = r * 0.86
            found.append(
                (
                    pts[i][0] + side * nx * w * 0.30,
                    pts[i][1] + side * ny * w * 0.30,
                    r2,
                )
            )
            next_row2 = dist + max(r2 * 2.35, 8)
    return found


def sucker_mark(cx, cy, r):
    return (
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="#F3B2A6"/>'
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 0.70)}" fill="#D25A56"/>'
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 0.36)}" fill="#9E333C"/>'
        f'<circle cx="{fmt(cx - r * 0.28)}" cy="{fmt(cy - r * 0.30)}" r="{fmt(r * 0.16)}" fill="#fff" opacity="0.8"/>'
    )


def draw_tentacle(points, base, tip, fill, sucker_side=1, rows=1, spiral=None, bulge=0.08):
    pts = catmull(points, 11)
    if spiral:
        pts = append_spiral(pts, **spiral)
    pts = resample(pts, 4.0)
    if len(pts) < 4:
        return ""
    ws = width_profile(len(pts), base, tip, bulge)
    norms = normals(pts)
    outline, left, right = ribbon_edges(pts, ws, norms)
    dorsal = right if sucker_side > 0 else left
    ventral = left if sucker_side > 0 else right
    parts = [
        f'<path d="{poly(outline)}" fill="{fill}"/>',
        f'<path d="{poly(dorsal, False)}" fill="none" stroke="#FFD5CB" stroke-width="3.4" stroke-linecap="round" opacity="0.8"/>',
        f'<path d="{poly(ventral, False)}" fill="none" stroke="#A83840" stroke-width="2.4" stroke-linecap="round" opacity="0.4"/>',
    ]
    for cx, cy, r in sucker_positions(pts, ws, norms, sucker_side, rows):
        parts.append(sucker_mark(cx, cy, r))
    if DEBUG:
        parts.append(
            f'<path d="{poly(pts, False)}" fill="none" stroke="#00e5ff" stroke-width="1"/>'
        )
    return "".join(parts)


def text_glyph(key, x, baseline, fill, anchor="left", dx=0, dy=0, opacity=1):
    d, w, _a = GLYPHS[key]
    if anchor == "center":
        x -= w / 2
    elif anchor == "right":
        x -= w
    op = "" if opacity == 1 else f' opacity="{opacity}"'
    return (
        f'<path d="{d}" fill="{fill}" fill-rule="evenodd"{op} '
        f'transform="translate({fmt(x + dx)} {fmt(baseline + dy)})"/>'
    )


def ellipse(cx, cy, rx, ry, fill, extra=""):
    return (
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" '
        f'fill="{fill}"{extra}/>'
    )


def steam_wisp(cx, y0, height, width, bend):
    """Tapered vertical puff. y0 is the base; the wisp rises by `height`."""
    pts = []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = y0 - height * t
        x = cx + math.sin(t * math.pi) * bend + math.sin(t * math.tau) * bend * 0.25
        pts.append((x, y))
    ws = [math.sin(i / n * math.pi) * width for i in range(n + 1)]
    ws[0] = 0.8
    ws[-1] = 0.6
    norms = normals(pts)
    outline, _, _ = ribbon_edges(pts, ws, norms)
    return poly(outline)


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

def defs():
    return """
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#101424"/>
  <stop offset="42%" stop-color="#1A1834"/>
  <stop offset="100%" stop-color="#2A2046"/>
</linearGradient>
<radialGradient id="skin" cx="36%" cy="32%" r="72%">
  <stop offset="0%" stop-color="#FFC8BC"/>
  <stop offset="42%" stop-color="#F27A6A"/>
  <stop offset="78%" stop-color="#E25C54"/>
  <stop offset="100%" stop-color="#C4454A"/>
</radialGradient>
<radialGradient id="blush" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#E85B62" stop-opacity="0.5"/>
  <stop offset="70%" stop-color="#E85B62" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="#E85B62" stop-opacity="0"/>
</radialGradient>
<linearGradient id="apron" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#FFFCFA"/>
  <stop offset="55%" stop-color="#FFF8F1"/>
  <stop offset="100%" stop-color="#E7D9C8"/>
</linearGradient>
<linearGradient id="awning" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#B4333C"/>
  <stop offset="55%" stop-color="#8E2430"/>
  <stop offset="100%" stop-color="#6E1826"/>
</linearGradient>
<linearGradient id="interior" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#F2C48A"/>
  <stop offset="55%" stop-color="#E0A05C"/>
  <stop offset="100%" stop-color="#C4843E"/>
</linearGradient>
<radialGradient id="halo" cx="50%" cy="42%" r="58%">
  <stop offset="0%" stop-color="#FFE0B0" stop-opacity="0.95"/>
  <stop offset="55%" stop-color="#F0B56A" stop-opacity="0.35"/>
  <stop offset="100%" stop-color="#E0A05C" stop-opacity="0"/>
</radialGradient>
<linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#F0D2A6"/>
  <stop offset="100%" stop-color="#D7B07A"/>
</linearGradient>
<linearGradient id="post" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#A87850"/>
  <stop offset="18%" stop-color="#7A4E32"/>
  <stop offset="78%" stop-color="#5C3A28"/>
  <stop offset="100%" stop-color="#3A2418"/>
</linearGradient>
<radialGradient id="broth" cx="40%" cy="38%" r="68%">
  <stop offset="0%" stop-color="#FFD56A"/>
  <stop offset="45%" stop-color="#F0A62E"/>
  <stop offset="100%" stop-color="#C47A18"/>
</radialGradient>
<radialGradient id="stock" cx="42%" cy="40%" r="70%">
  <stop offset="0%" stop-color="#FFF1D2"/>
  <stop offset="50%" stop-color="#F0D2A4"/>
  <stop offset="100%" stop-color="#E0B888"/>
</radialGradient>
<radialGradient id="yolk" cx="38%" cy="36%" r="65%">
  <stop offset="0%" stop-color="#FFE28A"/>
  <stop offset="55%" stop-color="#F5A020"/>
  <stop offset="100%" stop-color="#D87810"/>
</radialGradient>
<radialGradient id="lantern" cx="40%" cy="42%" r="65%">
  <stop offset="0%" stop-color="#FFD59A"/>
  <stop offset="28%" stop-color="#FF7A3C"/>
  <stop offset="70%" stop-color="#E4452E"/>
  <stop offset="100%" stop-color="#B82822"/>
</radialGradient>
<linearGradient id="iron" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#5A534C"/>
  <stop offset="30%" stop-color="#3A342F"/>
  <stop offset="100%" stop-color="#241E1C"/>
</linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#F4F7F8"/>
  <stop offset="40%" stop-color="#C5CED4"/>
  <stop offset="100%" stop-color="#8E9AA2"/>
</linearGradient>
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="5"/>
</filter>
<filter id="steam" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="5.5"/>
</filter>
<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="16"/>
</filter>
<filter id="glowSm" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="8"/>
</filter>
"""


def sky():
    parts = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    # Crescent moon, upper left, clear of the awning.
    parts.append(
        '<path fill="#F4E6C8" fill-rule="evenodd" d="'
        "M78,78 m-46,0 a46,46 0 1,0 92,0 a46,46 0 1,0 -92,0 Z "
        'M96,74 m-36,0 a36,36 0 1,1 72,0 a36,36 0 1,1 -72,0 Z"/>'
    )
    parts.append(ellipse(70, 70, 70, 70, "#F4E6C8", ' opacity="0.18" filter="url(#glow)"'))
    stars = [
        (36, 28, 1.5, 0.9), (58, 46, 1.0, 0.7), (168, 26, 1.6, 0.85),
        (214, 48, 1.1, 0.6), (268, 22, 1.3, 0.75), (390, 18, 1.7, 0.9),
        (448, 36, 1.0, 0.55), (520, 16, 1.4, 0.8), (700, 18, 1.2, 0.7),
        (768, 30, 1.5, 0.85), (834, 16, 1.1, 0.6), (910, 26, 1.6, 0.9),
        (978, 42, 1.0, 0.55), (1048, 20, 1.4, 0.8), (1110, 36, 1.2, 0.7),
        (1164, 18, 1.5, 0.85), (24, 88, 1.1, 0.5), (190, 96, 1.0, 0.45),
        (430, 58, 1.2, 0.5), (760, 56, 1.0, 0.4), (1148, 92, 1.2, 0.5),
        (48, 340, 1.3, 0.35), (28, 560, 1.0, 0.25), (1172, 380, 1.2, 0.3),
        (1160, 640, 1.0, 0.22),
    ]
    for x, y, r, o in stars:
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFF6E4" opacity="{o}"/>')
    bokeh = [
        (46, 300, 28, "#FFB15A", 0.45),
        (34, 470, 16, "#E4452E", 0.35),
        (58, 680, 20, "#FFD08A", 0.28),
        (1156, 280, 26, "#FFB15A", 0.4),
        (1170, 460, 14, "#FF8A3C", 0.32),
        (1148, 660, 22, "#E4452E", 0.26),
        (250, 36, 8, "#FFE1B0", 0.55),
        (980, 34, 7, "#FFE1B0", 0.4),
    ]
    for x, y, r, col, o in bokeh:
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="{o}" filter="url(#glowSm)"/>'
        )
    return "".join(parts)


def awning():
    parts = []
    # Cloth roof. The center arches up so the toque can break the skyline.
    cloth = "M64,164 Q600,102 1136,164 L1136,250 Q600,282 64,250 Z"
    hem = "M64,250 Q600,282 1136,250 L1136,268 Q600,302 64,268 Z"
    parts.append(f'<path d="{cloth}" fill="url(#awning)"/>')
    parts.append(f'<path d="{hem}" fill="#5A1420"/>')
    parts.append(
        '<path d="M78,248 Q600,278 1122,248" fill="none" stroke="#F6E2C0" '
        'stroke-width="3" stroke-linecap="round" opacity="0.85"/>'
    )
    # Soft highlight along the upper cloth.
    parts.append(
        '<path d="M120,168 Q600,124 1080,168" fill="none" stroke="#E86A72" '
        'stroke-width="10" stroke-linecap="round" opacity="0.35"/>'
    )
    # Shop name, split so the hat owns the center. Shadow then cream.
    for key, cx in (("TAKO", 328), ("RAMEN", 878)):
        parts.append(text_glyph(key, cx, 230, "#5A1220", "center", dx=0, dy=3))
        parts.append(text_glyph(key, cx, 230, "#FFF6E6", "center"))
    return "".join(parts)


def posts_and_interior():
    parts = []
    # Side posts.
    for x in (96, 1052):
        parts.append(
            f'<rect x="{x}" y="210" width="54" height="930" rx="6" fill="url(#post)"/>'
        )
        parts.append(
            f'<rect x="{x + 6}" y="230" width="7" height="860" rx="3" fill="#C49264" opacity="0.35"/>'
        )
    # Warm back wall.
    parts.append('<rect x="150" y="230" width="900" height="490" fill="url(#interior)"/>')
    parts.append(ellipse(600, 460, 340, 260, "url(#halo)"))
    # Plank seams, quiet.
    for x, op in ((230, 0.13), (380, 0.08), (820, 0.1), (960, 0.14)):
        parts.append(
            f'<path d="M{x},236 Q{x + 8},460 {x - 4},710" fill="none" stroke="#8A4E28" '
            f'stroke-width="3" opacity="{op}"/>'
        )
    return "".join(parts)


def menu_and_shelf():
    parts = []
    # Clear of the left noren (ends near x=242) and of the chef's cheek.
    x, y, w, h = 252, 252, 200, 156
    parts.append(
        f'<rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 16}" rx="8" fill="#6B4630"/>'
    )
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#1B2822"/>')
    parts.append(text_glyph("MENU", x + w / 2, y + 32, "#F2C14A", "center"))
    parts.append(
        f'<path d="M{x + 28},{y + 42} H{x + w - 28}" stroke="#F2C14A" stroke-width="1" opacity="0.7"/>'
    )
    rows = [("TONKOTSU", "P11"), ("MISO", "P10"), ("SHOYU", "P10"), ("AJITAMA", "P2")]
    for i, (name, price) in enumerate(rows):
        by = y + 68 + i * 26
        parts.append(text_glyph(name, x + 16, by, "#F6EBD8"))
        parts.append(text_glyph(price, x + w - 14, by, "#F2C14A", "right"))
        name_w = GLYPHS[name][1]
        price_w = GLYPHS[price][1]
        dot_x = x + 16 + name_w + 10
        dot_end = x + w - 14 - price_w - 8
        dx = dot_x
        while dx < dot_end:
            parts.append(f'<circle cx="{fmt(dx)}" cy="{fmt(by - 4)}" r="1.15" fill="#F6EBD8" opacity="0.45"/>')
            dx += 8
    # Shelf and a short row of bowls waiting under the menu.
    parts.append('<path d="M230,448 h250 l14,16 h-278 Z" fill="#A86B3C"/>')
    parts.append('<path d="M230,448 h250 l6,6 h-244 Z" fill="#E6C49A"/>')
    for i, bx in enumerate((268, 334, 400)):
        parts.append(_mini_bowl(bx, 444, 1.0 if i != 1 else 1.08, red=(i == 2)))
    # Back tentacle reaching for the bowls — kept below the menu board.
    parts.append(
        draw_tentacle(
            [(500, 610), (440, 550), (380, 510), (330, 478), (292, 458)],
            base=22,
            tip=8,
            fill="#D05350",
            sucker_side=-1,
            rows=1,
            spiral={"turns": 0.55, "radius": 16, "clockwise": False},
        )
    )
    return "".join(parts)


def _mini_bowl(cx, cy, s=1.0, red=False):
    rx, ry = 26 * s, 10 * s
    body = (
        f"M{fmt(cx - rx)},{fmt(cy)} "
        f"C{fmt(cx - rx)},{fmt(cy + 16 * s)} {fmt(cx - 16 * s)},{fmt(cy + 22 * s)} {fmt(cx - 12 * s)},{fmt(cy + 22 * s)} "
        f"Q{fmt(cx)},{fmt(cy + 28 * s)} {fmt(cx + 12 * s)},{fmt(cy + 22 * s)} "
        f"C{fmt(cx + 16 * s)},{fmt(cy + 22 * s)} {fmt(cx + rx)},{fmt(cy + 16 * s)} {fmt(cx + rx)},{fmt(cy)} Z"
    )
    lip = "#C4473A" if red else "#2A4574"
    bowl_fill = "#F4E4E0" if red else "#FFFCFA"
    return (
        f'<path d="{body}" fill="{bowl_fill}"/>'
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" fill="{bowl_fill}" stroke="{lip}" stroke-width="2.5"/>'
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx * 0.62)}" ry="{fmt(ry * 0.5)}" fill="none" stroke="{lip}" stroke-width="1.4" opacity="0.7"/>'
    )


def noren():
    parts = []
    parts.append('<rect x="150" y="246" width="900" height="8" rx="2" fill="#2A1A14"/>')

    def panel(x, y, w, h, wave, mon=False):
        d = (
            f"M{fmt(x)},{fmt(y)} L{fmt(x + w)},{fmt(y)} L{fmt(x + w)},{fmt(y + h)} "
            f"Q{fmt(x + w * 0.72)},{fmt(y + h + wave)} {fmt(x + w * 0.5)},{fmt(y + h - wave * 0.25)} "
            f"Q{fmt(x + w * 0.28)},{fmt(y + h + wave * 1.05)} {fmt(x)},{fmt(y + h + wave * 0.15)} Z"
        )
        g = [f'<path d="{d}" fill="#243B66"/>']
        # Fold shadow on the right, highlight on the left, clipped by re-stroking edges.
        g.append(
            f'<path d="M{fmt(x + w - 10)},{fmt(y)} L{fmt(x + w)},{fmt(y)} L{fmt(x + w)},{fmt(y + h)} '
            f'Q{fmt(x + w - 4)},{fmt(y + h - 8)} {fmt(x + w - 10)},{fmt(y + h - 6)} Z" fill="#14243F" opacity="0.45"/>'
        )
        g.append(
            f'<path d="M{fmt(x)},{fmt(y)} h8 V{fmt(y + h)} h-8 Z" fill="#fff" opacity="0.06"/>'
        )
        if mon:
            mcx, mcy = x + w / 2, y + h * 0.38
            g.append(f'<circle cx="{fmt(mcx)}" cy="{fmt(mcy)}" r="22" fill="#F4EFE4"/>')
            g.append(tako_mark(mcx, mcy + 1, 30, "#243B66"))
        return "".join(g)

    # Left panels stay left of the menu. Right panels frame the wave.
    parts.append(panel(148, 254, 48, 170, 12, False))
    parts.append(panel(204, 254, 46, 192, 14, True))
    parts.append(panel(908, 254, 62, 206, 14, True))
    parts.append(panel(980, 254, 62, 184, 11, False))
    return "".join(parts)


def tako_mark(cx, cy, size, fill):
    """Tiny octopus crest. Drawn in a 100-unit box, then scaled."""
    s = size / 100
    inner = (
        '<g fill="none" stroke="{fill}" stroke-width="8" stroke-linecap="round">'
        '<path d="M34,52 C24,70 16,78 18,92"/>'
        '<path d="M44,56 C36,78 30,90 36,100"/>'
        '<path d="M56,56 C64,78 70,90 64,100"/>'
        '<path d="M66,52 C76,70 84,78 82,92"/>'
        "</g>"
        '<ellipse cx="50" cy="40" rx="22" ry="20" fill="{fill}"/>'
        '<circle cx="42" cy="38" r="3.2" fill="#F4EFE4"/>'
        '<circle cx="58" cy="38" r="3.2" fill="#F4EFE4"/>'
    ).format(fill=fill)
    return (
        f'<g transform="translate({fmt(cx)} {fmt(cy)}) scale({fmt(s)}) translate(-50 -52)">{inner}</g>'
    )


def chef_body_back():
    """Straps and anything that should tuck behind the mantle."""
    parts = []
    # Apron straps, tucked behind the head.
    for d in (
        "M528,600 C486,530 470,470 508,390",
        "M672,600 C720,530 742,470 700,390",
    ):
        parts.append(
            f'<path d="{d}" fill="none" stroke="#E4D5C4" stroke-width="22" stroke-linecap="round"/>'
        )
        parts.append(
            f'<path d="{d}" fill="none" stroke="#FFF8F1" stroke-width="16" stroke-linecap="round"/>'
        )
    return "".join(parts)


def chef_head():
    cx, cy, rx, ry = HEAD
    parts = [
        f'<clipPath id="headClip"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>',
        ellipse(cx, cy, rx, ry, "url(#skin)"),
        # Form shadow, lower right, kept inside the mantle.
        f'<g clip-path="url(#headClip)">{ellipse(cx + 46, cy + 48, 130, 108, "#9E3040", " opacity=\"0.28\"")}'
        f'{ellipse(cx - 48, cy - 36, 78, 52, "#fff", " opacity=\"0.22\"")}'
        f'{ellipse(cx - 62, cy - 48, 28, 16, "#fff", " opacity=\"0.55\"")}</g>',
    ]
    # Cheeks sit under the eyes.
    parts.append(ellipse(508, 512, 36, 20, "url(#blush)"))
    parts.append(ellipse(700, 518, 34, 18, "url(#blush)"))
    parts.append(_eye(534, 462, 8, 5, "L"))
    parts.append(_eye(668, 470, 8, 5, "R"))
    # Brow creases sit above open eyes, lifted a little on the outer ends.
    parts.append(
        '<path d="M486,408 Q530,390 574,408" fill="none" stroke="#C4474A" stroke-width="5" '
        'stroke-linecap="round" opacity="0.7"/>'
    )
    parts.append(
        '<path d="M628,414 Q678,394 730,412" fill="none" stroke="#C4474A" stroke-width="5" '
        'stroke-linecap="round" opacity="0.7"/>'
    )
    # Proud, slightly uneven smile, the right corner lifted toward the bowl.
    parts.append(
        '<path d="M552,528 Q612,572 676,522" fill="none" stroke="#9E3340" stroke-width="5" '
        'stroke-linecap="round"/>'
    )
    parts.append(
        '<path d="M566,534 Q612,562 662,530" fill="none" stroke="#E88984" stroke-width="2" '
        'stroke-linecap="round" opacity="0.7"/>'
    )
    # A small glossy bead of kitchen heat, left temple.
    parts.append(
        '<path d="M458,470 C458,458 472,454 474,468 C476,482 458,486 458,470 Z" fill="#FFF6F2" opacity="0.9"/>'
        '<ellipse cx="466" cy="466" rx="3" ry="4" fill="#fff" opacity="0.8"/>'
    )
    return "".join(parts)


def _eye(cx, cy, dx, dy, tag):
    """Open, bright eye. The pupil leans a little toward the bowl."""
    rx, ry = 40, 38
    px, py = cx + dx, cy + dy
    return (
        f'<clipPath id="eye{tag}"><ellipse cx="{cx}" cy="{cy}" rx="{rx - 1.5}" ry="{ry - 1.5}"/></clipPath>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#FFFCFA"/>'
        f'<g clip-path="url(#eye{tag})">'
        f'<circle cx="{px}" cy="{py}" r="21" fill="#2A211F"/>'
        f'<circle cx="{px - 8}" cy="{py - 9}" r="7.2" fill="#fff"/>'
        f'<circle cx="{px + 7}" cy="{py + 6}" r="2.8" fill="#fff" opacity="0.9"/>'
        f'</g>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#B84548" stroke-width="2.4"/>'
    )


def hat():
    parts = []
    # Five plump pleats. Center lobe is tallest and clears the awning.
    lobes = 5
    lobe_w = 76
    total = 230
    step = (total - lobe_w) / (lobes - 1)
    left = HAT_CX - total / 2
    factors = [0.84, 0.94, 1.0, 0.93, 0.82]
    colors = ["#F6EFE6", "#FFFCFA", "#FFFDFB", "#F7F1E8", "#EFE4D6"]
    band_top = HAT_BAND_Y - 8
    for i in range(lobes):
        cx = left + lobe_w / 2 + i * step
        top = HAT_TOP + (1 - factors[i]) * 70
        height = band_top - top + 24
        cy = top + height / 2
        parts.append(
            f'<rect x="{fmt(cx - lobe_w / 2)}" y="{fmt(top)}" width="{fmt(lobe_w)}" height="{fmt(height)}" '
            f'rx="{fmt(lobe_w / 2)}" fill="{colors[i]}"/>'
        )
        # Right edge of each pleat, a warm shadow.
        parts.append(
            f'<path d="M{fmt(cx + lobe_w / 2 - 14)},{fmt(top + 30)} '
            f'Q{fmt(cx + lobe_w / 2 - 6)},{fmt(cy)} {fmt(cx + lobe_w / 2 - 14)},{fmt(band_top)} '
            f'L{fmt(cx + lobe_w / 2 - 2)},{fmt(band_top)} '
            f'Q{fmt(cx + lobe_w / 2 + 2)},{fmt(cy)} {fmt(cx + lobe_w / 2 - 2)},{fmt(top + 36)} Z" '
            f'fill="#E4D5C4" opacity="0.65"/>'
        )
    # Band.
    parts.append(ellipse(HAT_CX, HAT_BAND_Y + 16, 112, 26, "#E7DCCE"))
    parts.append(
        f'<rect x="{HAT_CX - 112}" y="{HAT_BAND_Y - 8}" width="224" height="28" fill="#FFF8F1"/>'
    )
    parts.append(ellipse(HAT_CX, HAT_BAND_Y - 8, 112, 24, "#FFFCF8"))
    parts.append(ellipse(HAT_CX, HAT_BAND_Y + 18, 112, 22, "#F3EBE1"))
    # Left sheen on the band.
    parts.append(
        f'<path d="M{HAT_CX - 90},{HAT_BAND_Y - 4} q20,-16 40,0" fill="none" stroke="#fff" '
        f'stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
    )
    return f'<g transform="rotate(-7 {HAT_CX} {HAT_BAND_Y})">{"".join(parts)}</g>'


def apron():
    # Bib over the lower mantle. The counter will cover the hem.
    d = (
        "M498,590 "
        "C470,670 456,760 488,830 "
        "L714,830 "
        "C748,760 734,670 702,590 "
        "Q600,636 498,590 Z"
    )
    parts = [
        f'<path d="{d}" fill="url(#apron)"/>',
        # Right-side fold.
        '<path d="M640,620 C700,690 724,760 700,830 L714,830 C748,760 734,670 702,590 Q680,608 640,620 Z" fill="#E7D9C8" opacity="0.9"/>',
        # Neckline shadow where cloth meets skin.
        '<path d="M498,590 Q600,636 702,590" fill="none" stroke="#E4D3C2" stroke-width="6" stroke-linecap="round"/>',
        '<path d="M506,596 Q600,638 694,596" fill="none" stroke="#C98A84" stroke-width="2" opacity="0.35" stroke-linecap="round"/>',
    ]
    # Armholes: dark openings the upper tentacles leave from.
    parts.append(ellipse(470, 676, 26, 18, "#5C2E32"))
    parts.append(ellipse(470, 674, 16, 10, "#3A1C22"))
    parts.append(ellipse(734, 668, 26, 18, "#5C2E32"))
    parts.append(ellipse(734, 666, 16, 10, "#3A1C22"))
    # Pocket with a scallion tucked in.
    parts.append('<path d="M612,700 h62 a8,8 0 0 1 8,8 v40 a8,8 0 0 1 -8,8 h-62 a8,8 0 0 1 -8,-8 v-40 a8,8 0 0 1 8,-8 Z" fill="#FFFCF8" stroke="#E4D5C4" stroke-width="2"/>')
    parts.append(
        '<g stroke-linecap="round">'
        '<path d="M632,704 C628,678 640,658 636,640" fill="none" stroke="#2F9A4A" stroke-width="5"/>'
        '<path d="M648,706 C652,676 644,654 650,634" fill="none" stroke="#3CB85C" stroke-width="5"/>'
        '<path d="M640,708 C638,686 646,668 642,650" fill="none" stroke="#1E7A38" stroke-width="4"/>'
        "</g>"
    )
    return "".join(parts)


def counter():
    parts = []
    # Skirt first (behind the lip and everything on the counter).
    parts.append('<path d="M118,812 L1082,812 L1104,1132 L96,1132 Z" fill="#243B66"/>')
    # Folds.
    for x, op in ((200, 0.18), (340, 0.1), (500, 0.14), (860, 0.12), (1000, 0.2)):
        parts.append(
            f'<path d="M{x},812 L{x + 28},1132 L{x + 70},1132 L{x + 36},812 Z" fill="#1A2C4E" opacity="{op}"/>'
        )
    # Hem stripes.
    parts.append('<path d="M104,1104 L1096,1104 L1100,1116 L100,1116 Z" fill="#F4EFE4"/>')
    parts.append('<path d="M102,1116 L1098,1116 L1102,1128 L98,1128 Z" fill="#8E2430"/>')
    # Wooden lip and top.
    parts.append('<path d="M120,786 L1080,786 L1100,832 L100,832 Z" fill="#8A5A38"/>')
    parts.append('<path d="M128,748 L1072,748 L1090,798 L110,798 Z" fill="url(#woodTop)"/>')
    # Grain.
    for x in (220, 360, 520, 700, 860, 990):
        parts.append(
            f'<path d="M{x},754 Q{x + 10},774 {x - 2},794" fill="none" stroke="#C49A68" stroke-width="2" opacity="0.45"/>'
        )
    # A hanging towel on the right skirt.
    parts.append(
        '<path d="M984,820 h46 l6,150 -8,10 -18,-16 -16,18 -8,-8 Z" fill="#FFFCFA"/>'
        '<path d="M988,930 h48 l2,14 h-52 Z" fill="#8E2430"/>'
        '<path d="M1000,820 l4,70" fill="none" stroke="#E4D5C4" stroke-width="3"/>'
    )
    return "".join(parts)


def pot_and_ladle():
    cx, cy = POT_C
    rx, ry = POT_RX, POT_RY
    foot = cy + 118
    body = (
        f"M{fmt(cx - rx)},{fmt(cy)} "
        f"C{fmt(cx - rx - 6)},{fmt(cy + 50)} {fmt(cx - 70)},{fmt(foot - 20)} {fmt(cx - 58)},{fmt(foot)} "
        f"Q{fmt(cx)},{fmt(foot + 18)} {fmt(cx + 58)},{fmt(foot)} "
        f"C{fmt(cx + 70)},{fmt(foot - 20)} {fmt(cx + rx + 6)},{fmt(cy + 50)} {fmt(cx + rx)},{fmt(cy)} "
        f"A{fmt(rx)},{fmt(ry)} 0 0 0 {fmt(cx - rx)},{fmt(cy)} Z"
    )
    parts = [
        ellipse(cx, foot + 8, 70, 12, "#1A1020", ' opacity="0.28" filter="url(#soft)"'),
        f'<path d="{body}" fill="url(#iron)"/>',
        # Rim and broth.
        ellipse(cx, cy, rx, ry, "#4A433C"),
        ellipse(cx, cy, rx - 10, ry - 6, "url(#stock)"),
        ellipse(cx - 24, cy - 8, 36, 12, "#fff", ' opacity="0.28"'),
        # Side lugs.
        f'<rect x="{fmt(cx - rx - 16)}" y="{fmt(cy + 28)}" width="22" height="14" rx="4" fill="#2A2422"/>',
        f'<rect x="{fmt(cx + rx - 6)}" y="{fmt(cy + 28)}" width="22" height="14" rx="4" fill="#2A2422"/>',
        # Highlight on the shoulder of the pot.
        f'<path d="M{fmt(cx - rx + 18)},{fmt(cy + 16)} Q{fmt(cx - 40)},{fmt(cy + 70)} {fmt(cx - 20)},{fmt(foot - 16)}" '
        f'fill="none" stroke="#8A847C" stroke-width="5" stroke-linecap="round" opacity="0.4"/>',
    ]
    # Bubbles clipped to the stock surface.
    parts.append(f'<clipPath id="stockClip"><ellipse cx="{cx}" cy="{cy}" rx="{rx - 14}" ry="{ry - 8}"/></clipPath>')
    bubbles = [
        (cx - 30, cy - 2, 5, 2.2, 0),
        (cx + 10, cy + 4, 3.5, 2.8, 0.4),
        (cx + 28, cy - 4, 4.5, 1.9, 0.8),
        (cx - 8, cy + 6, 2.6, 2.4, 1.1),
        (cx + 42, cy + 2, 3, 3.1, 0.2),
        (cx - 48, cy + 2, 2.8, 2.6, 1.4),
    ]
    bub = []
    for bx, by, r, dur, begin in bubbles:
        bub.append(
            f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="{fmt(r)}" fill="#FFF8EA" opacity="0.8">'
            f'<animate attributeName="cy" values="{fmt(by)};{fmt(by - 6)};{fmt(by - 1)}" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.35;0.85;0.4" dur="{dur}s" begin="{begin}s" '
            f'repeatCount="indefinite"/>'
            f"</circle>"
        )
    parts.append(f'<g clip-path="url(#stockClip)">{"".join(bub)}</g>')
    # Ladle: a real spoon cup in the stock, handle rising into the stirring arm.
    parts.append(
        f'<g transform="rotate(-28 {fmt(cx + 18)} {fmt(cy + 10)})">'
        f'{ellipse(cx + 18, cy + 10, 34, 16, "url(#metal)")}'
        f'{ellipse(cx + 18, cy + 12, 22, 9, "#E4C498")}'
        f'{ellipse(cx + 8, cy + 6, 8, 3.5, "#fff", " opacity=\"0.55\"")}'
        f"</g>"
    )
    parts.append(
        f'<path d="M{fmt(cx + 46)},{fmt(cy - 2)} C{fmt(cx + 90)},{fmt(cy - 36)} 400,648 436,618" '
        f'fill="none" stroke="#C4925A" stroke-width="9" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="M{fmt(cx + 46)},{fmt(cy - 2)} C{fmt(cx + 90)},{fmt(cy - 36)} 400,648 436,618" '
        f'fill="none" stroke="#EBD0A4" stroke-width="3.5" stroke-linecap="round"/>'
    )
    return "".join(parts)


def bottles():
    parts = []
    # Soy dispenser.
    parts.append(ellipse(468, 812, 20, 7, "#1A1020", ' opacity="0.25" filter="url(#soft)"'))
    parts.append('<rect x="454" y="742" width="28" height="70" rx="8" fill="#2A2422"/>')
    parts.append('<rect x="460" y="728" width="16" height="18" rx="3" fill="#3A302C"/>')
    parts.append('<path d="M476,734 h14 l6,-8 h-10 Z" fill="#4A4038"/>')
    parts.append('<rect x="458" y="768" width="20" height="22" rx="2" fill="#F6EBD8"/>')
    parts.append('<circle cx="468" cy="779" r="4" fill="#8E2430"/>')
    parts.append('<path d="M460,750 v48" stroke="#5A5048" stroke-width="2" opacity="0.5"/>')
    # Rayu jar.
    parts.append(ellipse(524, 818, 22, 7, "#1A1020", ' opacity="0.22" filter="url(#soft)"'))
    parts.append('<rect x="504" y="772" width="40" height="46" rx="6" fill="#F4E6D4"/>')
    parts.append('<rect x="508" y="786" width="32" height="28" rx="3" fill="#C4362A"/>')
    parts.append('<rect x="510" y="764" width="28" height="10" rx="2" fill="#2A2422"/>')
    parts.append(ellipse(520, 798, 8, 3, "#FFD56A", ' opacity="0.7"'))
    parts.append('<circle cx="516" cy="804" r="1.4" fill="#F6EBD8"/>')
    parts.append('<circle cx="526" cy="808" r="1.2" fill="#7A1E18"/>')
    parts.append('<circle cx="522" cy="800" r="1" fill="#F6EBD8" opacity="0.8"/>')
    return "".join(parts)


def bowl_back():
    """Ceramic body, far rim, soup, and the mound of noodles. Toppings come later."""
    cx, cy = BOWL_C
    rx, ry = BOWL_RX, BOWL_RY
    foot = cy + ry + 108
    body = (
        f"M{fmt(cx - rx)},{fmt(cy)} "
        f"C{fmt(cx - rx - 8)},{fmt(cy + 78)} {fmt(cx - 86)},{fmt(foot - 24)} {fmt(cx - 64)},{fmt(foot)} "
        f"Q{fmt(cx)},{fmt(foot + 20)} {fmt(cx + 64)},{fmt(foot)} "
        f"C{fmt(cx + 86)},{fmt(foot - 24)} {fmt(cx + rx + 8)},{fmt(cy + 78)} {fmt(cx + rx)},{fmt(cy)} "
        f"A{fmt(rx)},{fmt(ry)} 0 0 0 {fmt(cx - rx)},{fmt(cy)} Z"
    )
    parts = [
        ellipse(cx, foot + 6, 86, 16, "#1A1020", ' opacity="0.30" filter="url(#soft)"'),
        f'<path d="{body}" fill="#FFF8F0"/>',
        # Left glaze highlight and a hand-painted wave on the front of the bowl.
        f'<path d="M{fmt(cx - rx + 28)},{fmt(cy + 20)} C{fmt(cx - 120)},{fmt(cy + 90)} {fmt(cx - 70)},{fmt(foot - 30)} {fmt(cx - 20)},{fmt(foot - 18)}" '
        f'fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" opacity="0.45"/>',
        # A small crest, off to the side so it cannot read as a mouth.
        _bowl_crest(cx - 78, cy + 96),
        # Far rim (upper half of the ellipse).
        _rim_band(cx, cy, rx, ry, 16, near=False),
        # Soup surface.
        ellipse(cx, cy + 8, rx * 0.84, ry * 0.68, "url(#broth)"),
        ellipse(cx - 40, cy - 6, 54, 16, "#FFE7A2", ' opacity="0.45"'),
    ]
    # Oil beads and a sheen.
    for ox, oy, orx, ory, col, op in (
        (-20, 14, 28, 8, "#F8D48A", 0.45),
        (36, 22, 16, 5, "#E8892A", 0.35),
        (-55, 24, 10, 4, "#D4522A", 0.4),
    ):
        parts.append(ellipse(cx + ox, cy + oy, orx, ory, col, f' opacity="{op}"'))
    parts.append(_noodle_mound(cx, cy - 6))
    return "".join(parts)


def _bowl_crest(cx, cy):
    pts = []
    steps = 42
    for i in range(steps + 1):
        t = i / steps
        a = t * 2.05 * math.tau
        r = 1.2 + t * 9.5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return (
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="16" fill="none" stroke="#2A4574" stroke-width="2.2"/>'
        f'<path d="{poly(pts, False)}" fill="none" stroke="#2A4574" stroke-width="2.3" stroke-linecap="round"/>'
    )


def _rim_band(cx, cy, rx, ry, thickness, near=True):
    rxi = rx - thickness
    ryi = max(6, ry - thickness * 0.72)
    if near:
        # Lower half: left --clockwise--> right, back along the inner edge.
        d = (
            f"M{fmt(cx - rx)},{fmt(cy)} A{fmt(rx)},{fmt(ry)} 0 0 1 {fmt(cx + rx)},{fmt(cy)} "
            f"L{fmt(cx + rxi)},{fmt(cy)} A{fmt(rxi)},{fmt(ryi)} 0 0 0 {fmt(cx - rxi)},{fmt(cy)} Z"
        )
        red = (
            f"M{fmt(cx - rxi + 2)},{fmt(cy + 2)} A{fmt(rxi - 2)},{fmt(ryi - 2)} 0 0 1 "
            f"{fmt(cx + rxi - 2)},{fmt(cy + 2)}"
        )
    else:
        d = (
            f"M{fmt(cx - rx)},{fmt(cy)} A{fmt(rx)},{fmt(ry)} 0 0 0 {fmt(cx + rx)},{fmt(cy)} "
            f"L{fmt(cx + rxi)},{fmt(cy)} A{fmt(rxi)},{fmt(ryi)} 0 0 1 {fmt(cx - rxi)},{fmt(cy)} Z"
        )
        red = (
            f"M{fmt(cx - rxi + 2)},{fmt(cy)} A{fmt(rxi - 2)},{fmt(max(4, ryi - 2))} 0 0 0 "
            f"{fmt(cx + rxi - 2)},{fmt(cy)}"
        )
    return (
        f'<path d="{d}" fill="#FFF8F0"/>'
        f'<path d="{red}" fill="none" stroke="#C4473A" stroke-width="2.4" opacity="0.85"/>'
    )


def _noodle_strand(x0, y, length, amp, waves, phase, sag, width, color):
    pts = []
    n = 22
    for i in range(n + 1):
        t = i / n
        x = x0 + length * t
        yy = y + math.sin(t * waves * math.tau + phase) * amp + math.sin(t * math.pi) * sag
        pts.append((x, yy))
    return (
        f'<path d="{poly(pts, False)}" fill="none" stroke="{color}" stroke-width="{fmt(width)}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def _noodle_mound(cx, cy):
    # Hand-tuned pile so the noodles heap instead of scattering.
    specs = [
        (-78, -6, 150, 4.0, 3, 0.2, 6, 7.5, "#E2C890"),
        (-70, 0, 146, 5.0, 3, 1.4, 4, 8.0, "#F3E0B0"),
        (-74, 8, 154, 3.6, 4, 0.6, 7, 7.0, "#EBD7A4"),
        (-64, -14, 130, 4.4, 2, 2.0, 2, 8.5, "#F8E7C4"),
        (-60, 6, 128, 5.5, 3, 0.8, 5, 8.0, "#E8D0A0"),
        (-68, 14, 140, 3.2, 3, 1.8, 8, 7.2, "#F8E7C4"),
        (-50, -8, 112, 4.8, 2, 0.4, 3, 9.0, "#FFF3D8"),
        (-56, 4, 120, 3.8, 3, 2.4, 4, 7.4, "#E2C890"),
        (-40, 12, 96, 4.2, 2, 1.1, 6, 8.2, "#F3E0B0"),
        (-48, -2, 100, 3.4, 3, 0.3, 2, 7.6, "#FFF6E4"),
    ]
    return "".join(
        _noodle_strand(cx + x, cy + y, L, amp, waves, phase, sag, w, col)
        for x, y, L, amp, waves, phase, sag, w, col in specs
    )


def toppings():
    cx, cy = BOWL_C
    parts = []
    # Nori standing at the back-left, taller than the far rim.
    parts.append(
        f'<path d="M{fmt(cx - 108)},{fmt(cy - 8)} '
        f'C{fmt(cx - 102)},{fmt(cy - 70)} {fmt(cx - 78)},{fmt(cy - 130)} {fmt(cx - 70)},{fmt(cy - 138)} '
        f'C{fmt(cx - 40)},{fmt(cy - 124)} {fmt(cx - 28)},{fmt(cy - 60)} {fmt(cx - 34)},{fmt(cy + 6)} '
        f'C{fmt(cx - 70)},{fmt(cy + 10)} {fmt(cx - 100)},{fmt(cy + 4)} {fmt(cx - 108)},{fmt(cy - 8)} Z" '
        f'fill="#1C4034"/>'
    )
    parts.append(
        f'<path d="M{fmt(cx - 96)},{fmt(cy - 20)} C{fmt(cx - 90)},{fmt(cy - 80)} {fmt(cx - 74)},{fmt(cy - 120)} {fmt(cx - 68)},{fmt(cy - 126)}" '
        f'fill="none" stroke="#3E7A60" stroke-width="3" stroke-linecap="round" opacity="0.7"/>'
    )
    # Chashu, two overlapping slices on the left.
    parts.append(_chashu(cx - 62, cy + 2, -28))
    parts.append(_chashu(cx - 28, cy + 16, -8))
    # Menma.
    for i, (mx, my, rot) in enumerate(((-4, -8, -20), (16, 2, 12), (6, 14, -6))):
        col = "#F3D7A0" if i != 1 else "#E7C888"
        parts.append(
            f'<g transform="rotate({rot} {fmt(cx + mx)} {fmt(cy + my)})">'
            f'<rect x="{fmt(cx + mx - 16)}" y="{fmt(cy + my - 4)}" width="32" height="8" rx="3" fill="{col}"/>'
            f'<rect x="{fmt(cx + mx - 16)}" y="{fmt(cy + my - 4)}" width="8" height="8" rx="3" fill="#FFF6E0" opacity="0.6"/>'
            f"</g>"
        )
    # Egg, right of center.
    parts.append(_egg(cx + 62, cy + 2))
    # Narutomaki toward the front.
    parts.append(_naruto(cx - 6, cy + 30))
    # Scallion scatter.
    pieces = [
        (-20, 8, 40, 16),
        (8, 18, -25, 13),
        (40, 8, 55, 12),
        (-40, 22, 15, 14),
        (24, -6, -50, 11),
        (70, 16, 30, 13),
        (-8, 26, 70, 10),
        (48, 24, -15, 12),
        (-30, -2, 20, 11),
        (18, 10, 100, 9),
    ]
    for dx, dy, rot, length in pieces:
        parts.append(_scallion_piece(cx + dx, cy + dy, rot, length))
    # Sesame.
    for dx, dy, rot in ((-12, 4, 20), (22, 12, -30), (4, 20, 50), (36, -2, 10), (-48, 12, -20), (58, 6, 40)):
        parts.append(
            f'<ellipse cx="{fmt(cx + dx)}" cy="{fmt(cy + dy)}" rx="2.2" ry="1.3" fill="#F7E7C4" '
            f'transform="rotate({rot} {fmt(cx + dx)} {fmt(cy + dy)})"/>'
        )
    return "".join(parts)


def _chashu(cx, cy, rot):
    return (
        f'<g transform="rotate({rot} {fmt(cx)} {fmt(cy)})">'
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="40" ry="26" fill="#E7A090"/>'
        f'<ellipse cx="{fmt(cx - 2)}" cy="{fmt(cy)}" rx="30" ry="18" fill="#F3D0C4"/>'
        f'<ellipse cx="{fmt(cx - 4)}" cy="{fmt(cy + 1)}" rx="16" ry="10" fill="#C46B62"/>'
        f'<path d="M{fmt(cx - 18)},{fmt(cy - 2)} Q{fmt(cx)},{fmt(cy - 12)} {fmt(cx + 14)},{fmt(cy)}" '
        f'fill="none" stroke="#A85A54" stroke-width="2" stroke-linecap="round" opacity="0.7"/>'
        f'<ellipse cx="{fmt(cx - 14)}" cy="{fmt(cy - 8)}" rx="8" ry="4" fill="#fff" opacity="0.35"/>'
        f"</g>"
    )


def _egg(cx, cy):
    return (
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="40" ry="32" fill="#FFF6EA"/>'
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="40" ry="32" fill="none" stroke="#E6D3C0" stroke-width="1.5"/>'
        f'<circle cx="{fmt(cx + 2)}" cy="{fmt(cy + 1)}" r="18" fill="url(#yolk)"/>'
        f'<ellipse cx="{fmt(cx - 6)}" cy="{fmt(cy - 6)}" rx="7" ry="4" fill="#fff" opacity="0.65"/>'
        f'<circle cx="{fmt(cx - 8)}" cy="{fmt(cy - 7)}" r="2.2" fill="#fff"/>'
        f'<path d="M{fmt(cx - 22)},{fmt(cy + 8)} Q{fmt(cx)},{fmt(cy + 20)} {fmt(cx + 24)},{fmt(cy + 6)}" '
        f'fill="none" stroke="#E7D5C4" stroke-width="2" opacity="0.8"/>'
    )


def _naruto(cx, cy):
    # Pink spiral fish cake, standing nearly face-on.
    pts = []
    turns, n = 2.15, 70
    for i in range(n + 1):
        t = i / n
        a = t * turns * math.tau
        r = 2 + t * 13
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.92))
    return (
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="20" ry="18" fill="#FFFCFA" stroke="#F3C2D0" stroke-width="1"/>'
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="16" fill="none" stroke="#F4A2B8" stroke-width="3"/>'
        f'<path d="{poly(pts, False)}" fill="none" stroke="#F28BA8" stroke-width="3.2" stroke-linecap="round"/>'
    )


def _scallion_piece(x, y, rot, length):
    return (
        f'<g transform="rotate({rot} {fmt(x)} {fmt(y)})">'
        f'<rect x="{fmt(x - length / 2)}" y="{fmt(y - 3)}" width="{fmt(length)}" height="6" rx="3" fill="#2F9A4A"/>'
        f'<rect x="{fmt(x - length / 2)}" y="{fmt(y - 3)}" width="{fmt(length * 0.38)}" height="6" rx="3" fill="#D7EECB"/>'
        f"</g>"
    )


def lifted_noodles():
    """U-shaped strands pinched by the chopsticks, dripping back into the bowl."""
    tipx, tipy = 786, 778
    parts = []
    strands = [
        (-8, 6, 64, 2.0, "#E8D0A0", 6.4),
        (-2, 10, 96, 2.4, "#F8E7C4", 7.2),
        (4, 4, 118, 1.6, "#E2C890", 6.6),
        (0, 12, 78, 2.2, "#FFF3D8", 7.0),
        (6, 8, 102, 1.8, "#F3E0B0", 6.2),
        (-4, 2, 88, 2.6, "#EBD7A4", 7.4),
    ]
    for ox, oy, droop, wav, col, width in strands:
        pts = []
        n = 26
        x0, x1 = tipx - 7 + ox, tipx + 9 + ox
        y = tipy + oy
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            sag = math.sin(t * math.pi) * droop
            wave = math.sin(t * 6 * math.pi) * wav * math.sin(t * math.pi)
            pts.append((x, y + sag + wave))
        parts.append(
            f'<path d="{poly(pts, False)}" fill="none" stroke="{col}" stroke-width="{width}" '
            f'stroke-linecap="round"/>'
        )
    # Broth bead falling from the longest strand.
    dx, dy = tipx + 2, tipy + 104
    parts.append(
        f'<path d="M{fmt(dx)},{fmt(dy - 8)} C{fmt(dx - 5)},{fmt(dy - 2)} {fmt(dx - 4.5)},{fmt(dy + 5)} '
        f'{fmt(dx)},{fmt(dy + 8)} C{fmt(dx + 4.5)},{fmt(dy + 5)} {fmt(dx + 5)},{fmt(dy - 2)} {fmt(dx)},{fmt(dy - 8)} Z" '
        f'fill="#E39B2B"/>'
        f'<ellipse cx="{fmt(dx - 1.5)}" cy="{fmt(dy - 2)}" rx="1.6" ry="2.4" fill="#fff" opacity="0.65"/>'
    )
    return "".join(parts)


def chopsticks():
    # Two sticks. The tentacle will wrap their middle, so both ends stay visible.
    sticks = [
        ((688, 736), (778, 792), "#E0A868"),
        ((706, 726), (798, 804), "#C48A4A"),
    ]
    parts = []
    for (x0, y0), (x1, y1), col in sticks:
        parts.append(
            f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{col}" stroke-width="7" stroke-linecap="round"/>'
        )
        # Darker used tips.
        mx = x0 + (x1 - x0) * 0.72
        my = y0 + (y1 - y0) * 0.72
        parts.append(
            f'<line x1="{fmt(mx)}" y1="{fmt(my)}" x2="{x1}" y2="{y1}" stroke="#8A5A30" stroke-width="7" stroke-linecap="round"/>'
        )
    return "".join(parts)


def near_rim():
    cx, cy = BOWL_C
    return _rim_band(cx, cy, BOWL_RX, BOWL_RY, 20, near=True)


def tentacles():
    """Eight arms. Shade separates the ones tucked back from the ones in front."""
    T = {
        "back": "#D05350",
        "mid": "#E86358",
        "front": "#F27868",
    }
    parts = []
    # 1. Stirring arm, out of the left armhole and wrapped on the ladle handle.
    parts.append(
        draw_tentacle(
            [(470, 674), (455, 640), (430, 618), (404, 646)],
            base=30,
            tip=10,
            fill=T["mid"],
            sucker_side=1,
            spiral={"turns": 0.85, "radius": 20, "clockwise": True},
        )
    )
    # 2. Short grip on the pot's right lug.
    parts.append(
        draw_tentacle(
            [(530, 748), (490, 770), (450, 752), (424, 728)],
            base=22,
            tip=8,
            fill=T["mid"],
            sucker_side=-1,
            spiral={"turns": 0.55, "radius": 14, "clockwise": False},
        )
    )
    # 3. Presenting curl on the near-left rim of the bowl.
    parts.append(
        draw_tentacle(
            [(560, 800), (530, 860), (560, 930), (630, 948)],
            base=26,
            tip=8,
            fill=T["front"],
            sucker_side=1,
            spiral={"turns": 0.6, "radius": 18, "clockwise": True},
        )
    )
    return "".join(parts)


def tentacle_chopsticks():
    return draw_tentacle(
        [(600, 760), (650, 790), (700, 804), (724, 770)],
        base=28,
        tip=8,
        fill="#F27868",
        sucker_side=-1,
        spiral={"turns": 0.85, "radius": 22, "clockwise": False},
    )


def tentacle_scallion():
    parts = [
        draw_tentacle(
            [(760, 730), (830, 700), (900, 730), (910, 790)],
            base=24,
            tip=7,
            fill="#E86358",
            sucker_side=1,
            spiral={"turns": 0.65, "radius": 16, "clockwise": True},
        )
    ]
    # Stalks pinched in the curl, and a few cuts on the way down to the bowl.
    parts.append(
        '<g stroke-linecap="round">'
        '<path d="M900,770 C908,800 902,830 912,858" fill="none" stroke="#2F9A4A" stroke-width="5"/>'
        '<path d="M912,776 C924,808 916,836 926,860" fill="none" stroke="#3CB85C" stroke-width="4.5"/>'
        '<path d="M894,784 C900,812 894,840 902,866" fill="none" stroke="#1E7A38" stroke-width="4"/>'
        '<path d="M906,800 l-8,16" stroke="#D7EECB" stroke-width="4" opacity="0.8"/>'
        "</g>"
    )
    for x, y, rot, length in ((888, 830, 70, 12), (924, 848, -30, 11), (870, 868, 40, 13)):
        parts.append(_scallion_piece(x, y, rot, length))
    return "".join(parts)


def tentacle_drape():
    """Foreground arm along the skirt, suckers toward the guest."""
    return draw_tentacle(
        [(440, 830), (390, 920), (350, 1000), (340, 1060), (390, 1096)],
        base=38,
        tip=9,
        fill="#F27868",
        sucker_side=1,
        rows=2,
        bulge=0.12,
        spiral={"turns": 0.7, "radius": 26, "clockwise": True},
    )


def tentacle_wave():
    return draw_tentacle(
        [(734, 668), (800, 600), (870, 520), (940, 450), (980, 410)],
        base=32,
        tip=8,
        fill="#F27868",
        sucker_side=-1,
        rows=1,
        bulge=0.1,
        spiral={"turns": 0.7, "radius": 26, "clockwise": True},
    )


def lantern(cx, top, height, width, gid):
    rx, ry = width / 2, height / 2
    cy = top + ry + 10
    cap_w = width * 0.46
    parts = [
        f'<line x1="{fmt(cx)}" y1="250" x2="{fmt(cx)}" y2="{fmt(cy - ry - 8)}" stroke="#2A1C18" stroke-width="2"/>',
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx + 18)}" ry="{fmt(ry)}" fill="#FFB03A" opacity="0.45" filter="url(#glow)">'
        f'<animate attributeName="opacity" values="0.32;0.55;0.4;0.52" dur="{3.2 + (gid % 3) * 0.4}s" repeatCount="indefinite"/>'
        f"</ellipse>",
        ellipse(cx, cy, rx, ry, "url(#lantern)"),
        ellipse(cx - rx * 0.28, cy - ry * 0.08, rx * 0.28, ry * 0.62, "#FFD7A8", ' opacity="0.28"'),
    ]
    # Ribs.
    rib = [f'<clipPath id="lan{gid}"><ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx - 1)}" ry="{fmt(ry - 1)}"/></clipPath>', f'<g clip-path="url(#lan{gid})">']
    for i in range(1, 8):
        yy = cy - ry + (2 * ry) * i / 8
        rib.append(
            f'<ellipse cx="{fmt(cx)}" cy="{fmt(yy)}" rx="{fmt(rx)}" ry="3.2" fill="none" stroke="#9E221C" stroke-width="2" opacity="0.55"/>'
        )
    rib.append(
        f'<line x1="{fmt(cx)}" y1="{fmt(cy - ry)}" x2="{fmt(cx)}" y2="{fmt(cy + ry)}" stroke="#7A1A16" stroke-width="1.4" opacity="0.45"/>'
    )
    rib.append("</g>")
    parts.append("".join(rib))
    parts.append(
        f'<rect x="{fmt(cx - cap_w / 2)}" y="{fmt(cy - ry - 8)}" width="{fmt(cap_w)}" height="12" rx="3" fill="#1A1214"/>'
    )
    parts.append(
        f'<rect x="{fmt(cx - cap_w / 2)}" y="{fmt(cy + ry - 4)}" width="{fmt(cap_w)}" height="12" rx="3" fill="#1A1214"/>'
    )
    # Tassel.
    parts.append(
        f'<path d="M{fmt(cx)},{fmt(cy + ry + 8)} l-7,16 h14 Z" fill="#E6B14A"/>'
    )
    return "".join(parts)


def steam():
    groups = [
        ([(308, 650, 150, 16, 18), (286, 656, 120, 12, -14), (332, 648, 136, 14, 10)], "4.6"),
        ([(790, 800, 150, 18, 16), (760, 808, 120, 12, -18), (830, 804, 140, 14, 12), (806, 812, 100, 10, -8)], "5.4"),
    ]
    parts = []
    for wisps, dur in groups:
        paths = "".join(
            f'<path d="{steam_wisp(cx, y, h, w, b)}" fill="#FFF8F2"/>' for cx, y, h, w, b in wisps
        )
        parts.append(
            f'<g opacity="0.5" filter="url(#steam)">'
            f'<animate attributeName="opacity" values="0.28;0.55;0.24" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 6; 4 -16; -3 -30" dur="{dur}s" repeatCount="indefinite"/>'
            f"{paths}</g>"
        )
    return "".join(parts)


def ground():
    return (
        '<path d="M0,1148 H1200 V1200 H0 Z" fill="#14121F"/>'
        '<ellipse cx="620" cy="1172" rx="420" ry="22" fill="#FFB15A" opacity="0.16"/>'
        '<rect x="78" y="1108" width="86" height="64" rx="4" fill="#4A3020"/>'
        '<rect x="1036" y="1108" width="86" height="64" rx="4" fill="#4A3020"/>'
        '<rect x="86" y="1116" width="10" height="48" fill="#C49264" opacity="0.3"/>'
        '<rect x="1044" y="1116" width="10" height="48" fill="#C49264" opacity="0.3"/>'
    )


def build():
    # Order is back to front. Tentacles are split so each one can tuck
    # behind the thing it actually passes behind.
    sections = [
        ("sky", sky),
        ("awning", awning),
        ("stall", posts_and_interior),
        ("menu", menu_and_shelf),
        ("straps", chef_body_back),
        ("head", chef_head),
        ("hat", hat),
        ("apron", apron),
        ("noren", noren),
        ("counter", counter),
        ("pot", pot_and_ladle),
        ("bottles", bottles),
        ("arms-mid", tentacles),
        ("bowl-back", bowl_back),
        ("toppings", toppings),
        ("lifted", lifted_noodles),
        ("near-rim", near_rim),
        ("chopsticks", chopsticks),
        ("chopstick-arm", tentacle_chopsticks),
        ("scallion-arm", tentacle_scallion),
        ("drape-arm", tentacle_drape),
        ("wave", tentacle_wave),
        ("steam", steam),
        ("lanterns", lambda: lantern(132, 268, 150, 74, 1) + lantern(1066, 268, 150, 74, 2)),
        ("ground", ground),
    ]
    body = []
    for name, fn in sections:
        body.append(f"<!-- {name} -->")
        body.append(fn())
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
<title>Octopus chef at a ramen booth</title>
<desc>An octopus in a toque and apron runs a night-market ramen stall, waving, stirring a stockpot, and lifting noodles from a topped bowl.</desc>
<defs>
{defs()}
</defs>
{"".join(body)}
</svg>
'''


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg = build()
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
