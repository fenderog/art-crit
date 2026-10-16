#!/usr/bin/env python3
"""LOAM — logo for a generative AI company.

The mark is a river stone in section: an organic pebble with one calm pore
set off-center, the way a grain of soil holds a pocket of air. The wordmark
is an original grotesque, drawn to contrast that softness with flat terminals.

Design space is y-up. SVG export flips to y-down.
"""

from __future__ import annotations

import math
import os

INK = "#2A2724"
PAPER = "#F3F0EA"
STONE = "#8A837A"
CLAY = "#C9C1B6"
DARK = "#161412"

CAP = 1000.0
STEM = 132.0
BAR = 116.0
O_WALL = 142.0

# Locked after visual review.
M_MITER = 5.2
M_VALLEY = 175.0
M_WIDTH = 1170.0
TRACKING = 40.0
MARK_HEIGHT = 1.16  # × cap height, in the horizontal lockup
MARK_GAP = 400.0


class Loop:
    def __init__(self, pts, smooth=False):
        self.pts = [(float(x), float(y)) for x, y in pts]
        self.smooth = smooth


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def vmul(a, s):
    return (a[0] * s, a[1] * s)


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def vlen(a):
    return math.hypot(a[0], a[1])


def vnorm(a):
    L = vlen(a) or 1e-12
    return (a[0] / L, a[1] / L)


def lerp(a, b, t):
    return a + (b - a) * t


def rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def translate(loops, dx, dy):
    return [Loop([(x + dx, y + dy) for x, y in lp.pts], lp.smooth) for lp in loops]


def scale_about(loops, s, origin):
    ox, oy = origin
    out = []
    for lp in loops:
        pts = [((x - ox) * s + ox, (y - oy) * s + oy) for x, y in lp.pts]
        out.append(Loop(pts, lp.smooth))
    return out


def bounds(loops):
    xs, ys = [], []
    for lp in loops:
        for x, y in lp.pts:
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def ensure_ccw(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return pts if a > 0 else list(reversed(pts))


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xinter = (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-15) + x1
            if x < xinter:
                inside = not inside
    return inside


def min_dist_point_poly(pt, poly):
    best = 1e18
    n = len(poly)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        ab = vsub(b, a)
        L2 = vdot(ab, ab) or 1e-12
        t = max(0.0, min(1.0, vdot(vsub(pt, a), ab) / L2))
        best = min(best, vlen(vsub(pt, vadd(a, vmul(ab, t)))))
    return best


def line_hit(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def clip_halfplane(pts, inside, intersect):
    if not pts:
        return []
    out = []
    prev = pts[-1]
    prev_in = inside(prev)
    for cur in pts:
        cur_in = inside(cur)
        if cur_in:
            if not prev_in:
                out.append(intersect(prev, cur))
            out.append(cur)
        elif prev_in:
            out.append(intersect(prev, cur))
        prev, prev_in = cur, cur_in
    return out


def clip_y_max(pts, y_max):
    return clip_halfplane(
        pts,
        lambda p: p[1] <= y_max + 1e-7,
        lambda a, b: (
            lerp(a[0], b[0], (y_max - a[1]) / ((b[1] - a[1]) or 1e-15)),
            y_max,
        ),
    )


def clip_y_min(pts, y_min):
    return clip_halfplane(
        pts,
        lambda p: p[1] >= y_min - 1e-7,
        lambda a, b: (
            lerp(a[0], b[0], (y_min - a[1]) / ((b[1] - a[1]) or 1e-15)),
            y_min,
        ),
    )


def catmull_rom(pts):
    n = len(pts)
    segs = []
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        b1 = vadd(p1, vmul(vsub(p2, p0), 1 / 6))
        b2 = vsub(p2, vmul(vsub(p3, p1), 1 / 6))
        segs.append((p1, b1, b2, p2))
    return segs


def path_d(loops, prec=2):
    def f(v):
        return f"{v:.{prec}f}"

    parts = []
    for lp in loops:
        pts = lp.pts
        if lp.smooth and len(pts) >= 4:
            segs = catmull_rom(pts)
            p0 = segs[0][0]
            d = [f"M{f(p0[0])} {f(p0[1])}"]
            for _, b1, b2, p3 in segs:
                d.append(
                    f"C{f(b1[0])} {f(b1[1])} {f(b2[0])} {f(b2[1])} {f(p3[0])} {f(p3[1])}"
                )
            d.append("Z")
        else:
            d = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
            for x, y in pts[1:]:
                d.append(f"L{f(x)} {f(y)}")
            d.append("Z")
        parts.append("".join(d))
    return "".join(parts)


def flip_y(loops, top):
    return [Loop([(x, top - y) for x, y in lp.pts], lp.smooth) for lp in loops]


def organic_points(a, b, rot_ang, harmonics, n=72, n_exp=2.0):
    pts = []
    e = 2.0 / n_exp
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** e, c)
        y = math.copysign(abs(s) ** e, s)
        scale = 1.0
        for amp, freq, phase in harmonics:
            scale += amp * math.sin(freq * t + phase)
        pts.append(rot((a * x * scale, b * y * scale), rot_ang))
    return ensure_ccw(pts)


def inset_polygon(pts, dist):
    """Inset a CCW polygon. Inward is the left normal of the tangent."""
    pts = ensure_ccw(pts)
    n = len(pts)
    out = []
    for i in range(n):
        t = vnorm(vsub(pts[(i + 1) % n], pts[(i - 1) % n]))
        inward = vnorm((-t[1], t[0]))
        out.append(vadd(pts[i], vmul(inward, dist)))
    return out


# ---------------------------------------------------------------------------
# Mark
# ---------------------------------------------------------------------------


def loam_mark():
    """Organic pebble, pore offset toward the upper right.

    Outer harmonics stay under 3% so the silhouette reads as a stone,
    not a lump. The pore is a true ellipse: a calm void inside living matter.
    """
    outer = organic_points(
        100.0,
        78.0,
        -0.32,
        ((0.026, 2, 0.45), (0.012, 3, 1.15)),
        n=140,
        n_exp=2.22,
    )
    hole = organic_points(27.0, 31.0, -0.25, (), n=96, n_exp=2.0)
    hole = [(x + 16.0, y + 12.0) for x, y in hole]
    return [Loop(outer, True), Loop(ensure_ccw(hole), True)]


# ---------------------------------------------------------------------------
# Wordmark
# ---------------------------------------------------------------------------


def glyph_L():
    s, b, arm = STEM, BAR, 640.0
    pts = [(0, 0), (arm, 0), (arm, b), (s, b), (s, CAP), (0, CAP)]
    return [Loop(pts, False)], arm


def glyph_O():
    over = 18.0
    half_w, half_h = 468.0, CAP / 2 + over
    outer = organic_points(half_w, half_h, 0.0, (), n=96, n_exp=2.62)
    inner = inset_polygon(outer, O_WALL)
    minx = min(p[0] for p in outer)
    outer = [(x - minx, y + CAP / 2) for x, y in outer]
    inner = [(x - minx, y + CAP / 2) for x, y in inner]
    width = max(p[0] for p in outer)
    return [Loop(outer, True), Loop(inner, True)], width


def glyph_A():
    W, flat, T = 800.0, 78.0, 138.0
    h_apex = CAP / (1 - flat / W)
    apex = (W / 2, h_apex)
    FL, FR = (0.0, 0.0), (W, 0.0)
    TL = line_hit(FL, apex, (0.0, CAP), (1.0, CAP))
    TR = line_hit(FR, apex, (0.0, CAP), (1.0, CAP))

    def offset(p, q, dist):
        d = vnorm(vsub(q, p))
        n = (-d[1], d[0])
        return vadd(p, vmul(n, dist)), vadd(q, vmul(n, dist))

    inl_a, inl_b = offset(FL, apex, -T)
    inr_a, inr_b = offset(FR, apex, T)
    bar_top, bar_bot = 400.0, 280.0

    def at_y(p, q, y):
        return line_hit(p, q, (0.0, y), (1.0, y))

    silhouette = [
        TL,
        TR,
        FR,
        at_y(inr_a, inr_b, 0.0),
        at_y(inr_a, inr_b, bar_bot),
        at_y(inl_a, inl_b, bar_bot),
        at_y(inl_a, inl_b, 0.0),
        FL,
    ]
    hole = [
        line_hit(inl_a, inl_b, inr_a, inr_b),
        at_y(inr_a, inr_b, bar_top),
        at_y(inl_a, inl_b, bar_top),
    ]
    return [Loop(silhouette, False), Loop(hole, False)], W


def stroke_polyline(pts, width, miter_limit=4.0):
    hw = width / 2.0
    n = len(pts)
    dirs = [vnorm(vsub(pts[i + 1], pts[i])) for i in range(n - 1)]
    normals = [(-d[1], d[0]) for d in dirs]

    def offset_point(seg, at_end, side):
        base = pts[seg + 1] if at_end else pts[seg]
        return vadd(base, vmul(normals[seg], hw * side))

    def miter(seg0, seg1, side):
        a = offset_point(seg0, False, side)
        b = offset_point(seg0, True, side)
        c = offset_point(seg1, False, side)
        d = offset_point(seg1, True, side)
        return line_hit(a, b, c, d)

    left = [offset_point(0, False, +1)]
    right = [offset_point(0, False, -1)]
    for i in range(n - 2):
        joint = pts[i + 1]
        for side, rail in ((+1, left), (-1, right)):
            m = miter(i, i + 1, side)
            if m is not None and vlen(vsub(m, joint)) <= miter_limit * hw:
                rail.append(m)
            else:
                rail.append(offset_point(i, True, side))
                rail.append(offset_point(i + 1, False, side))
    left.append(offset_point(n - 2, True, +1))
    right.append(offset_point(n - 2, True, -1))
    return left + list(reversed(right))


def glyph_M():
    hw = STEM / 2.0
    skeleton = [
        (hw, 0.0),
        (hw, CAP),
        (M_WIDTH / 2.0, M_VALLEY),
        (M_WIDTH - hw, CAP),
        (M_WIDTH - hw, 0.0),
    ]
    outline = clip_y_min(clip_y_max(stroke_polyline(skeleton, STEM, M_MITER), CAP), 0.0)
    return [Loop(outline, False)], M_WIDTH


SIDE = {"L": (0.0, 40.0), "O": (20.0, 20.0), "A": (0.0, 0.0), "M": (30.0, 0.0)}
KERNS = {("L", "O"): 28.0, ("O", "A"): 8.0, ("A", "M"): 36.0}


def wordmark(tracking=TRACKING):
    glyphs = {"L": glyph_L(), "O": glyph_O(), "A": glyph_A(), "M": glyph_M()}
    pen = 0.0
    loops = []
    prev = None
    for ch in "LOAM":
        gl, width = glyphs[ch]
        lsb, rsb = SIDE[ch]
        if prev is not None:
            pen += KERNS.get((prev, ch), 0.0) + tracking
        pen += lsb
        loops.extend(translate(gl, pen, 0.0))
        pen += width + rsb
        prev = ch
    minx = bounds(loops)[0]
    return translate(loops, -minx, 0.0)


def normalize(loops, pad=0.0):
    minx, miny, maxx, maxy = bounds(loops)
    loops = translate(loops, -minx + pad, -miny + pad)
    w = maxx - minx + 2 * pad
    h = maxy - miny + 2 * pad
    return loops, w, h


def horizontal():
    """Mark and word in one y-up space, mark on the left."""
    mark, mw, mh = normalize(loam_mark(), 0)
    s = (CAP * MARK_HEIGHT) / mh
    mark = scale_about(mark, s, (0, 0))
    mark, mw, mh = normalize(mark, 0)
    words = wordmark()
    # Optical center of the mark sits on the cap-height center, lifted a hair.
    mark = translate(mark, 0.0, (CAP / 2.0 - mh / 2.0) + 10.0)
    words = translate(words, mw + MARK_GAP, 0.0)
    return mark, words


def stacked():
    words = wordmark(tracking=52.0)
    _minx, _miny, maxx, _maxy = bounds(words)
    word_w = maxx  # min x is 0 after wordmark() shifts to 0; overshoot y may be negative
    # wordmark() shifts x so min x is 0, but y is not normalized.
    mark, mw, mh = normalize(loam_mark(), 0)
    s = (word_w * 0.56) / mw
    mark = scale_about(mark, s, (0, 0))
    mark, mw, mh = normalize(mark, 0)
    gap = CAP * 0.32
    baseline_pad = 18.0  # O overshoot
    mark = translate(mark, (word_w - mw) / 2.0, CAP + gap)
    words = translate(words, 0.0, baseline_pad)
    return mark, words


# ---------------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------------


def svg(loops, fill, title, desc, bg=None, pad_ratio=0.012):
    loops, w, h = normalize(loops, 0)
    pad = max(w, h) * pad_ratio
    loops = translate(loops, pad, pad)
    W, H = w + 2 * pad, h + 2 * pad
    flipped = flip_y(loops, H)
    d = path_d(flipped, prec=2)
    bg_el = ""
    if bg:
        bg_el = f'  <rect width="{W:.2f}" height="{H:.2f}" fill="{bg}"/>\n'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
        f'fill="none" role="img">\n'
        f"  <title>{title}</title>\n"
        f"  <desc>{desc}</desc>\n"
        f"{bg_el}"
        f'  <path fill="{fill}" fill-rule="evenodd" d="{d}"/>\n'
        "</svg>\n"
    )


def inline_svg(loops, fill=INK, width_px=400):
    """Tight inline SVG for the board. Coordinates already y-up."""
    loops, w, h = normalize(loops, 0)
    flipped = flip_y(loops, h)
    d = path_d(flipped, prec=2)
    height_px = width_px * h / w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
        f'width="{width_px:.0f}" height="{height_px:.1f}" role="img">'
        f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>'
    )


DESC = "Logo for LOAM, a generative AI company. An organic stone with an offset pore."


def write_svgs(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mark = loam_mark()
    hm, hw = horizontal()
    sm, sw = stacked()
    files = {
        "loam-mark.svg": svg(mark, INK, "LOAM mark", DESC),
        "loam-lockup.svg": svg(hm + hw, INK, "LOAM", DESC),
        "loam-stacked.svg": svg(sm + sw, INK, "LOAM", DESC + " Stacked lockup."),
        "loam-reversed.svg": svg(
            hm + hw,
            PAPER,
            "LOAM",
            DESC + " Reversed for dark backgrounds.",
            bg=DARK,
            pad_ratio=0.08,
        ),
    }
    for name, text in files.items():
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(path)
    return hm, hw, sm, sw


def board_html():
    mark = loam_mark()
    hm, hw = horizontal()
    sm, sw = stacked()
    sizes = "".join(
        f'<div class="sz">{inline_svg(mark, width_px=px)}<span>{px}</span></div>'
        for px in (16, 24, 32, 48, 80)
    )
    swatches = "".join(
        f'<div class="sw"><i style="background:{c}"></i><span>{c}</span><em>{n}</em></div>'
        for c, n in (
            (INK, "Ink"),
            (STONE, "Stone"),
            (CLAY, "Clay"),
            (PAPER, "Paper"),
            (DARK, "Dark"),
        )
    )
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><title>LOAM</title>
<style>
  html,body {{ margin:0; background:{PAPER}; color:{INK};
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
  .page {{ width:1920px; height:1200px; box-sizing:border-box;
    padding:96px 100px 72px; display:grid;
    grid-template-columns: 640px 1fr; grid-template-rows: 1fr auto;
    column-gap:72px; }}
  .mark {{ display:flex; align-items:center; justify-content:center; }}
  .right {{ display:flex; flex-direction:column; justify-content:center; gap:56px; }}
  .row {{ display:flex; align-items:flex-end; gap:48px; }}
  .dark {{ background:{DARK}; padding:48px 40px; display:flex; align-items:center; }}
  .foot {{ grid-column: 1 / -1; display:flex; justify-content:space-between;
    align-items:flex-end; padding-top:28px; }}
  .sizes {{ display:flex; gap:22px; align-items:flex-end; }}
  .sz {{ display:flex; flex-direction:column; align-items:center; gap:8px; }}
  .sz span {{ font-size:11px; letter-spacing:.12em; color:{STONE}; }}
  .swatches {{ display:flex; gap:22px; }}
  .sw {{ display:flex; flex-direction:column; gap:6px; min-width:78px; }}
  .sw i {{ display:block; width:78px; height:28px;
    box-shadow: inset 0 0 0 1px rgba(42,39,36,.2); }}
  .sw span {{ font-size:11px; letter-spacing:.08em; color:{INK}; }}
  .sw em {{ font-style:normal; font-size:11px; letter-spacing:.14em;
    text-transform:uppercase; color:{STONE}; }}
  .caption {{ font-size:12px; letter-spacing:.28em; text-transform:uppercase;
    color:{STONE}; font-weight:500; }}
</style></head>
<body>
  <div class="page">
    <div class="mark">{inline_svg(mark, width_px=520)}</div>
    <div class="right">
      <div>{inline_svg(hm + hw, width_px=980)}</div>
      <div class="row">
        {inline_svg(sm + sw, width_px=300)}
        <div class="dark">{inline_svg(hm + hw, fill=PAPER, width_px=460)}</div>
      </div>
    </div>
    <div class="foot">
      <div>
        <div class="caption">Loam · Generative systems</div>
        <div class="sizes" style="margin-top:18px">{sizes}</div>
      </div>
      <div class="swatches">{swatches}</div>
    </div>
  </div>
</body></html>
'''


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "output")
    write_svgs(out)
    preview = os.path.join(root, "preview")
    os.makedirs(preview, exist_ok=True)
    with open(os.path.join(preview, "board.html"), "w", encoding="utf-8") as f:
        f.write(board_html())
    # sanity
    mark = loam_mark()
    wall = min(
        min_dist_point_poly(p, mark[0].pts) for p in mark[1].pts[::3]
    )
    inside = all(point_in_poly(p, mark[0].pts) for p in mark[1].pts[::4])
    print(f"pore wall {wall:.1f} inside {inside}")
    if not inside or wall < 18:
        raise SystemExit("mark failed containment check")


if __name__ == "__main__":
    main()
