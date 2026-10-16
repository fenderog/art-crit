#!/usr/bin/env python3
"""Morpha — logo for a generative AI company.

Concept: cell division / budding stones. A parent "pebble" carries an
opening growth-ring crescent, a younger stone buds from its upper right,
and a spore escapes along the same diagonal: one form generating the next.

Every stone — and every bowl in the custom monoline wordmark — is drawn
by the same polar-harmonic pebble function with a different seed, so the
geometry is itself generative: one algorithm, many generations.

Palette is warm neutrals only. Output is flat, few-node SVG paths
(Catmull-Rom -> cubic Bezier). Standard library only.
"""
import math

# ------------------------------------------------------------------ palette
INK   = "#2B2620"   # warm near-black
MID   = "#7A7062"   # warm mid-grey (the bud)
STONE = "#A39885"   # stone
CLAY  = "#C2B198"   # pale clay (the spore)
SAND  = "#E7DFD0"   # sand
BONE  = "#F5F1E9"   # warm paper
GREY  = "#6E655A"   # warm grey (text)

# ------------------------------------------------------------------- seeds
S_MAIN  = [(2, 0.050, 0.5), (3, 0.030, 2.2)]
S_BUD   = [(2, 0.055, 2.6), (3, 0.032, 0.8)]
S_SPORE = [(2, 0.045, 1.4), (3, 0.025, 3.9)]
S_LET   = [(2, 0.030, 1.1), (3, 0.018, 0.4)]   # letter bowls: near-round

# ---------------------------------------------------------------- geometry
def pebble_points(cx, cy, r, harmonics, rot=0.0, squash=1.0, n=12):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rad = r * (1.0 + sum(a * math.cos(k * t + p) for k, a, p in harmonics))
        x = rad * math.cos(t)
        y = rad * math.sin(t) * squash
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot),
                    cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts

def closed_path(pts):
    n = len(pts)
    d = [f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"]
    for i in range(n):
        p0 = pts[(i - 1) % n]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return "".join(d) + "Z"

def stone(cx, cy, r, seed, rot=0.0, squash=1.0, n=12):
    return closed_path(pebble_points(cx, cy, r, seed, rot, squash, n))

def _local_pts(cx, cy, r, seed, rot, squash, angles, scale=1.0):
    pts = []
    for t in angles:
        rad = r * scale * (1.0 + sum(a * math.cos(k * t + p) for k, a, p in seed))
        x = rad * math.cos(t); y = rad * math.sin(t) * squash
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot),
                    cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts

def arc_band(cx, cy, r, seed, rot, squash, t0, t1, s_mid=0.65, width=0.105, steps=24):
    """Tapered crescent following the stone's own contour (growth ring)."""
    angs = [t0 + (t1 - t0) * i / steps for i in range(steps + 1)]
    outer, inner = [], []
    for i, t in enumerate(angs):
        w = width * math.sin(math.pi * i / steps) ** 0.55
        outer += _local_pts(cx, cy, r, seed, rot, squash, [t], s_mid + w / 2)
        inner += _local_pts(cx, cy, r, seed, rot, squash, [t], s_mid - w / 2)
    return closed_path(outer + inner[::-1])

# -------------------------------------------------------------------- mark
# Drawn in a 240x240 field. phase/morph params enable the animated version.
MAIN = (96, 146, 66, 0.55, 0.86)
BUD  = (152, 94, 44, 0.55, 0.88)
SPORE = (208, 42, 12, 0.40, 1.00)

def _morph(seed, m):
    """Shift harmonic phases by m (radians, scaled per harmonic)."""
    return [(k, a, p + m * (0.9 if k == 2 else 1.4)) for k, a, p in seed]

def mark(ink=INK, mid=MID, pale=CLAY, morph=0.0, bud_shift=0.0, spore_r=None):
    cx, cy, r, rot, sq = MAIN
    sm = _morph(S_MAIN, morph)
    main = stone(cx, cy, r, sm, rot, sq)
    band = arc_band(cx, cy, r, sm, rot, sq, 0.95, 4.10)
    bx, by, br, brot, bsq = BUD
    bud = stone(bx + bud_shift * 0.7, by - bud_shift * 0.7, br, _morph(S_BUD, morph * 1.2), brot, bsq)
    sx, sy, sr, srot, ssq = SPORE
    spore = stone(sx, sy, spore_r or sr, _morph(S_SPORE, morph), srot, ssq)
    return (f'<path d="{main}{band}" fill="{ink}" fill-rule="evenodd"/>'
            f'<path d="{bud}" fill="{mid}"/>'
            f'<path d="{spore}" fill="{pale}"/>')

def mark_bbox(pad=0.0):
    pts = []
    for (cx, cy, r, rot, sq), seed in [(MAIN, S_MAIN), (BUD, S_BUD), (SPORE, S_SPORE)]:
        pts += pebble_points(cx, cy, r, seed, rot, sq, n=96)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad

# ---------------------------------------------------------------- wordmark
# Custom monoline lowercase. Baseline B, x-height T, ascender A, descender D.
B, T, A, D = 100, 46, 18, 130
SW = 11.5

def _bowl(cx, cy, r, squash=1.05):
    return stone(cx, cy, r, S_LET, 0.18, squash)

def _g_m():
    return (f"M8,{B} L8,62 C8,40 41,40 41,62 L41,{B} "
            f"M41,62 C41,40 74,40 74,62 L74,{B}"), 88

def _g_o():
    return _bowl(30, 73, 26.5), 62

def _g_r():
    return f"M9,{B} L9,60 C11,43 27,39 37,47 C44,52 44,61 38,69", 50

def _g_p():
    return (f"M11,{D} L11,64", _bowl(34, 68, 24.5)), 66

def _g_h():
    return (f"M9,{B} L9,{A} "
            f"M9,62 C9,40 45,40 45,62 L45,{B}"), 60

def _g_a():
    return (f"M52,60 L52,{B}", _bowl(27, 73, 26.5)), 64

GLYPHS = {"m": _g_m, "o": _g_o, "r": _g_r, "p": _g_p, "h": _g_h, "a": _g_a}

def wordmark(word="morpha", col=INK, tracking=3, sw=SW):
    """Returns (svg, width, (top, bottom)) in local units."""
    x = 0; parts = []
    for ch in word:
        res, adv = GLYPHS[ch]()
        for d in (res if isinstance(res, tuple) else (res,)):
            parts.append(f'<path d="{d}" transform="translate({x:.1f},0)" fill="none" '
                         f'stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
                         f'stroke-linejoin="round"/>')
        x += adv + tracking
    return "".join(parts), x - tracking, (A - sw / 2, D + sw / 2)

WM_W = wordmark()[1]          # 411
WM_TOP, WM_BOT = A - SW / 2, D + SW / 2
XHEIGHT = B - T               # 54

# ----------------------------------------------------------------- lockups
def svg_doc(viewbox, body, title="Morpha logo"):
    x, y, w, h = viewbox
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" role="img">'
            f'<title>{title}</title>{body}</svg>\n')

def mark_svg(ink=INK, mid=MID, pale=CLAY, pad=6):
    x0, y0, x1, y1 = mark_bbox(pad)
    return svg_doc((x0, y0, x1 - x0, y1 - y0), mark(ink, mid, pale), "Morpha mark")

def horizontal_svg(ink=INK, mid=MID, pale=CLAY, wm_col=None, pad=8):
    wm_col = wm_col or ink
    x0, y0, x1, y1 = mark_bbox()
    mh = y1 - y0
    scale = (mh * 0.34) / XHEIGHT            # wordmark x-height vs mark height
    gap = mh * 0.22
    wm, wm_w, _ = wordmark(col=wm_col)
    wm_x = x1 + gap
    # align wordmark x-height centre with mark centre
    wm_y = (y0 + y1) / 2 - (T + B) / 2 * scale
    body = (mark(ink, mid, pale)
            + f'<g transform="translate({wm_x:.1f},{wm_y:.1f}) scale({scale:.3f})">{wm}</g>')
    vx1 = wm_x + wm_w * scale
    vy0 = min(y0, wm_y + WM_TOP * scale); vy1 = max(y1, wm_y + WM_BOT * scale)
    return svg_doc((x0 - pad, vy0 - pad, vx1 - x0 + 2 * pad, vy1 - vy0 + 2 * pad),
                   body, "Morpha logo, horizontal lockup")

def stacked_svg(ink=INK, mid=MID, pale=CLAY, wm_col=None, tagline=True, pad=12):
    wm_col = wm_col or ink
    x0, y0, x1, y1 = mark_bbox()
    mw, mh = x1 - x0, y1 - y0
    wm, wm_w, _ = wordmark(col=wm_col)
    # Wordmark is the widest element in the stack; layout in local coords.
    scale = (mw * 1.45) / WM_W
    W = wm_w * scale
    body = f'<g transform="translate({(W - mw) / 2 - x0:.1f},{-y0:.1f})">{mark(ink, mid, pale)}</g>'
    wm_top = mh + mh * 0.14
    body += f'<g transform="translate(0,{wm_top - WM_TOP * scale:.1f}) scale({scale:.3f})">{wm}</g>'
    vy1 = wm_top + (WM_BOT - WM_TOP) * scale
    if tagline:
        # 13 glyphs at 13px + 5px tracking ~= 176 units, safely inside W
        ty = vy1 + 30
        body += (f'<text x="{W / 2 + 2.5:.1f}" y="{ty:.1f}" text-anchor="middle" '
                 f'font-family="Avenir Next,Helvetica Neue,Helvetica,Arial,sans-serif" '
                 f'font-size="13" letter-spacing="5" fill="{wm_col}">GENERATIVE AI</text>')
        vy1 = ty + 5
    return svg_doc((-pad, -pad, W + 2 * pad, vy1 + 2 * pad),
                   body, "Morpha logo, stacked lockup")
