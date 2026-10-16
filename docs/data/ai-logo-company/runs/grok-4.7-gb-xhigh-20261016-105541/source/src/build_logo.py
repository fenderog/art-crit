"""Build the Loam logo: an organic bud mark and a geometric wordmark.

Loam is a generative AI company. The mark is two superellipses — a grounded
body and a smaller bud emerging at the upper right. The one-color version is
their softened union. The duotone version draws the bud in clay behind the
ink body, so only the new growth shows.

Run from the repo root: python3 src/build_logo.py
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mark_geometry import (
    catmull_rom_path,
    centroid,
    classify_loops,
    clip_polygon_horizontal,
    ellipse_beziers,
    fit_in_box,
    laplacian_closed,
    marching_squares,
    orient,
    polygon_path,
    resample_closed,
    stroke_polyline,
)
from raster import (
    content_box,
    flatten_catmull,
    flatten_ellipse,
    rasterize,
    render,
    write_png,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
PREVIEW = ROOT / "preview"

INK = "#191816"
PAPER = "#F1EEE6"
CLAY = "#8C7B68"
SAND = "#D5CBBC"  # lighter bud tone; the reversed lockup stays one color

# Body, then the bud that grows from its upper-right shoulder.
# Coordinates are y-up.
PARENT = dict(cx=-0.06, cy=-0.10, rx=1.02, ry=1.20, rot=-0.22, n=2.45)
BUD = dict(cx=0.62, cy=0.70, rx=0.50, ry=0.46, rot=0.42, n=2.45)
UNION_K = 11.0

# Wordmark tuning. Stroke and gaps are fractions of cap height.
STROKE = 0.10
GAPS = (0.18, 0.15, 0.14)
MARK_INK_H = 1.52  # ink height of the mark relative to cap height
LOCKUP_GAP = 0.38
STACK_GAP = 0.46
STACK_MARK_W = 0.72  # mark ink width relative to the word width
STACK_NUDGE = 0.0  # fraction of mark width; positive shifts the stacked mark right


def superellipse(cx, cy, rx, ry, rot, n, count=120):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(count):
        t = (i / count) * math.tau
        ct, st = math.cos(t), math.sin(t)
        x = rx * math.copysign(abs(ct) ** (2.0 / n), ct)
        y = ry * math.copysign(abs(st) ** (2.0 / n), st)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def _soft_union(vals, k):
    m = max(vals)
    acc = 0.0
    for v in vals:
        acc += math.exp(k * (v - m))
    return m + math.log(acc) / k


def _inside(x, y, spec):
    c, s = math.cos(spec["rot"]), math.sin(spec["rot"])
    dx, dy = x - spec["cx"], y - spec["cy"]
    lx = (dx * c + dy * s) / spec["rx"]
    ly = (-dx * s + dy * c) / spec["ry"]
    n = spec["n"]
    return 1.0 - (abs(lx) ** n + abs(ly) ** n) ** (1.0 / n)


def union_ring():
    def field(x, y):
        return _soft_union((_inside(x, y, PARENT), _inside(x, y, BUD)), UNION_K)

    loops = marching_squares(field, -2.4, -2.4, 2.4, 2.4, 520, 520, 0.0)
    outer, _holes = classify_loops(loops, min_area=0.02)
    if outer is None:
        raise RuntimeError("union contour failed")
    outer = resample_closed(outer, 200)
    outer = laplacian_closed(outer, iters=1, amount=0.16)
    return resample_closed(outer, 88)


def screen_fit(rings, box=1000.0):
    """Fit y-up rings into a square and return y-down rings plus the ink bbox."""
    fitted = fit_in_box(rings, box, 0.0)
    screen = []
    for i, ring in enumerate(fitted):
        ring = orient(ring, ccw=(i == 0))
        screen.append([(x, box - y) for x, y in ring])
    pts = [p for ring in screen for p in ring]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    return screen, bbox


# --- wordmark -------------------------------------------------------------

def _shift(polys, dx):
    return [[(x + dx, y) for x, y in poly] for poly in polys]


def make_L(cap, stroke):
    foot_w = cap * 0.50
    foot_h = stroke * 0.90
    return [[
        (0, 0),
        (stroke, 0),
        (stroke, cap - foot_h),
        (foot_w, cap - foot_h),
        (foot_w, cap),
        (0, cap),
    ]]


def make_O(cap, stroke):
    over = cap * 0.016
    r = cap / 2 + over
    inner = r - stroke * 0.96
    # Center sits on the left edge so the circle advances by its diameter.
    return (r, cap / 2, r, inner), 2 * r


def make_A(cap, stroke, width_ratio=0.76):
    tip_y = -cap * 0.018
    half = cap * width_ratio / 2
    width = width_ratio * cap
    T = (half, tip_y)
    L0 = (0.0, cap)
    R0 = (width, cap)

    def inward_normal(origin, dest, toward):
        dx, dy = dest[0] - origin[0], dest[1] - origin[1]
        length = math.hypot(dx, dy) or 1.0
        n1 = (-dy / length, dx / length)
        n2 = (dy / length, -dx / length)
        mx = (origin[0] + dest[0]) * 0.5
        my = (origin[1] + dest[1]) * 0.5
        d1 = (mx + n1[0] - toward[0]) ** 2 + (my + n1[1] - toward[1]) ** 2
        d2 = (mx + n2[0] - toward[0]) ** 2 + (my + n2[1] - toward[1]) ** 2
        return n1 if d1 < d2 else n2

    center = (half, cap * 0.55)
    nL = inward_normal(T, L0, center)
    nR = inward_normal(T, R0, center)

    def offset(p, n):
        return (p[0] + n[0] * stroke, p[1] + n[1] * stroke)

    def hit(p, d, q, e):
        den = d[0] * e[1] - d[1] * e[0]
        if abs(den) < 1e-9:
            return p
        t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
        return (p[0] + t * d[0], p[1] + t * d[1])

    dL = (L0[0] - T[0], L0[1] - T[1])
    dR = (R0[0] - T[0], R0[1] - T[1])
    inner_tip = hit(offset(T, nL), dL, offset(T, nR), dR)

    def at_y(p, d, y):
        t = (y - p[1]) / d[1]
        return (p[0] + t * d[0], y)

    L1 = at_y(offset(T, nL), dL, cap)
    R1 = at_y(offset(T, nR), dR, cap)
    poly = [T, L0, L1, inner_tip, R1, R0]

    bar_h = stroke * 0.84
    bar_mid = cap * 0.625

    def x_at(p, q, y):
        t = (y - p[1]) / (q[1] - p[1])
        return p[0] + t * (q[0] - p[0])

    outer_l = x_at(T, L0, bar_mid)
    inner_l = x_at(inner_tip, L1, bar_mid)
    outer_r = x_at(T, R0, bar_mid)
    inner_r = x_at(inner_tip, R1, bar_mid)
    x0 = inner_l + (outer_l - inner_l) * 0.42
    x1 = inner_r + (outer_r - inner_r) * 0.42
    bar = [
        (x0, bar_mid - bar_h / 2),
        (x1, bar_mid - bar_h / 2),
        (x1, bar_mid + bar_h / 2),
        (x0, bar_mid + bar_h / 2),
    ]
    return [poly, bar]


def make_M(cap, stroke, width_ratio=0.98):
    W = cap * width_ratio
    stem = stroke
    left = [(0, 0), (stem, 0), (stem, cap), (0, cap)]
    right = [(W - stem, 0), (W, 0), (W, cap), (W - stem, cap)]
    mid_x = W / 2
    joint_y = cap * 0.82
    vpoly = []
    for _ in range(8):
        vpoly = stroke_polyline(
            [(stem, 0.0), (mid_x, joint_y), (W - stem, 0.0)],
            stroke,
            miter_limit=8.0,
        )
        vpoly = clip_polygon_horizontal(vpoly, 0.0, keep_above=True)
        tip = max(p[1] for p in vpoly)
        err = tip - cap
        if abs(err) < 0.15:
            break
        joint_y -= err
    return [left, right, vpoly]


def layout_word(cap):
    stroke = cap * STROKE
    parts = []
    cursor = 0.0
    builders = [
        ("poly", make_L(cap, stroke)),
        ("o", make_O(cap, stroke)),
        ("poly", make_A(cap, stroke)),
        ("poly", make_M(cap, stroke)),
    ]
    for i, (kind, built) in enumerate(builders):
        if kind == "poly":
            minx = min(x for poly in built for x, _y in poly)
            maxx = max(x for poly in built for x, _y in poly)
            parts.append(("poly", _shift(built, cursor - minx)))
            cursor += maxx - minx
        else:
            spec, width = built
            parts.append(("o", spec, cursor))
            cursor += width
        if i < 3:
            cursor += cap * GAPS[i]
    return parts, cursor



class Item:
    def __init__(self, fill, polys, d, rule="nonzero", alpha=1.0, group=None):
        self.fill = fill
        self.polys = polys
        self.d = d
        self.rule = rule
        self.alpha = alpha
        self.group = group


class Scene:
    def __init__(self, viewbox, items):
        self.viewbox = viewbox
        self.items = items


def shift_d(d, dx, dy):
    tokens = re.findall(r"[MLCZmlcz]|[-+]?(?:\d+\.?\d*|\.\d+)", d)
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in "Zz":
            out.append("Z")
            i += 1
        elif t in "Mm":
            x = float(tokens[i + 1]) + dx
            y = float(tokens[i + 2]) + dy
            out.append(f"M{x:.2f} {y:.2f}")
            i += 3
        elif t in "Ll":
            x = float(tokens[i + 1]) + dx
            y = float(tokens[i + 2]) + dy
            out.append(f"L{x:.2f} {y:.2f}")
            i += 3
        elif t in "Cc":
            pairs = []
            for k in range(3):
                x = float(tokens[i + 1 + 2 * k]) + dx
                y = float(tokens[i + 2 + 2 * k]) + dy
                pairs.append(f"{x:.2f} {y:.2f}")
            out.append("C" + " ".join(pairs))
            i += 7
        else:
            raise RuntimeError(f"unexpected path token {t}")
    return "".join(out)


def shift_item(item, dx, dy):
    polys = [[(x + dx, y + dy) for x, y in poly] for poly in item.polys]
    return Item(item.fill, polys, shift_d(item.d, dx, dy), item.rule, item.alpha, item.group)


def finalize(viewbox, items):
    x, y, w, h = viewbox
    return Scene((0.0, 0.0, w, h), [shift_item(item, -x, -y) for item in items])


def word_items(cap, fill, origin=(0.0, 0.0)):
    parts, width = layout_word(cap)
    ox, oy = origin
    items = []
    for item in parts:
        if item[0] == "poly":
            for poly in item[1]:
                pts = [(x + ox, y + oy) for x, y in poly]
                items.append(Item(fill, [pts], polygon_path(pts), group="word"))
        else:
            spec, xoff = item[1], item[2]
            cx, cy, r, inner = spec
            cx += ox + xoff
            cy += oy
            d = ellipse_beziers(cx, cy, r, r) + ellipse_beziers(cx, cy, inner, inner)
            outer = flatten_ellipse(cx, cy, r, r)
            hole = flatten_ellipse(cx, cy, inner, inner)
            items.append(Item(fill, [outer, hole], d, rule="evenodd", group="word"))
    return items, width


def mark_geometry():
    parent = superellipse(**PARENT)
    bud = superellipse(**BUD)
    union = union_ring()
    duo_screen, duo_box = screen_fit([parent, bud])
    union_screen, union_box = screen_fit([union])
    return {
        "parent": duo_screen[0],
        "bud": duo_screen[1],
        "union": union_screen[0],
        "duo_box": duo_box,
        "union_box": union_box,
    }


def transform_for(box, target_h, left, cy):
    minx, miny, maxx, maxy = box
    scale = target_h / (maxy - miny)
    ty = cy - ((miny + maxy) / 2) * scale
    tx = left - minx * scale
    return tx, ty, scale, tx + maxx * scale, ty + miny * scale, ty + maxy * scale


def place_rings(rings, fills, box, target_h, left, cy):
    tx, ty, scale, right, top, bottom = transform_for(box, target_h, left, cy)
    items = []
    for ring, fill in zip(rings, fills):
        pts = [(tx + x * scale, ty + y * scale) for x, y in ring]
        items.append(Item(fill, [flatten_catmull(pts, 0.2)], catmull_rom_path(pts)))
    return items, right, top, bottom


def horizontal_scene(geo, fill, bud_fill=None):
    cap = 200.0
    mark_h = cap * MARK_INK_H
    cy = cap / 2
    if bud_fill is None:
        items, right, top, bottom = place_rings(
            [geo["union"]], [fill], geo["union_box"], mark_h, 0.0, cy
        )
    else:
        items, right, top, bottom = place_rings(
            [geo["bud"], geo["parent"]],
            [bud_fill, fill],
            geo["duo_box"],
            mark_h,
            0.0,
            cy,
        )
    word, width = word_items(cap, fill, origin=(right + cap * LOCKUP_GAP, 0.0))
    over = cap * 0.02
    minx = 0.0
    miny = min(top, -over)
    maxx = right + cap * LOCKUP_GAP + width
    maxy = max(bottom, cap + over)
    pad = cap * 0.42
    vb = (minx - pad, miny - pad, (maxx - minx) + pad * 2, (maxy - miny) + pad * 2)
    return finalize(vb, items + word)


def stacked_scene(geo, fill):
    cap = 200.0
    _word, width = word_items(cap, fill, origin=(0.0, 0.0))
    mark_w = width * STACK_MARK_W
    minx, miny, maxx, maxy = geo["union_box"]
    aspect = (maxy - miny) / (maxx - minx)
    mark_h = mark_w * aspect
    left = (width - mark_w) / 2 + mark_w * STACK_NUDGE
    items, right, top, bottom = place_rings(
        [geo["union"]], [fill], geo["union_box"], mark_h, left, mark_h / 2
    )
    word_y = bottom + cap * STACK_GAP
    word, width = word_items(cap, fill, origin=(0.0, word_y))
    over = cap * 0.02
    minx_b = min(left, 0.0)
    miny_b = min(top, word_y - over)
    maxx_b = max(right, width)
    maxy_b = word_y + cap + over
    pad = cap * 0.48
    vb = (
        minx_b - pad,
        miny_b - pad,
        (maxx_b - minx_b) + pad * 2,
        (maxy_b - miny_b) + pad * 2,
    )
    return finalize(vb, items + word)


def mark_scene(geo, fills, kind):
    box = geo["union_box"] if kind == "union" else geo["duo_box"]
    rings = [geo["union"]] if kind == "union" else [geo["bud"], geo["parent"]]
    items, right, top, bottom = place_rings(rings, fills, box, 1000.0, 0.0, 500.0)
    pad = 120.0
    vb = (-pad, top - pad, right + pad * 2, (bottom - top) + pad * 2)
    return finalize(vb, items)


def square_scene(scene):
    _x, _y, w, h = scene.viewbox
    side = max(w, h)
    dx = (side - w) / 2
    dy = (side - h) / 2
    return Scene((0.0, 0.0, side, side), [shift_item(item, dx, dy) for item in scene.items])


def svg_document(scene, title, desc, background=None):
    _x, _y, w, h = scene.viewbox
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<svg xmlns="http://www.w3.org/2000/svg" ',
        f'viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.2f}" height="{h:.2f}" ',
        'role="img" aria-labelledby="title desc">\n',
        f'<title id="title">{title}</title>\n',
        f'<desc id="desc">{desc}</desc>\n',
    ]
    if background:
        parts.append(f'<rect width="{w:.2f}" height="{h:.2f}" fill="{background}"/>')
    for item in scene.items:
        rule = ' fill-rule="evenodd"' if item.rule == "evenodd" else ""
        parts.append(f'<path{rule} fill="{item.fill}" d="{item.d}"/>')
    parts.append("\n</svg>\n")
    return "".join(parts)


DESC = "Logo for Loam, a generative AI company. An organic bud grows from a grounded body."


def write_svg(path, scene, title, background=None):
    text = svg_document(scene, title, DESC, background)
    if "transform=" in text:
        raise RuntimeError(f"{path.name} still has a transform")
    path.write_text(text)


def margins_of(path):
    w, h, box, _raw = content_box(path)
    minx, miny, maxx, maxy = box
    if maxx < 0:
        raise RuntimeError(f"{path} has no content")
    return w, h, minx, miny, w - 1 - maxx, h - 1 - maxy


def expect_margins(path, lo, hi):
    w, h, left, top, right, bottom = margins_of(path)
    print(f"  {path.name:28} {w}x{h}  L{left} T{top} R{right} B{bottom}")
    for name, value, size in (
        ("left", left, w),
        ("right", right, w),
        ("top", top, h),
        ("bottom", bottom, h),
    ):
        frac = value / size
        if not (lo <= frac <= hi):
            raise RuntimeError(
                f"{path.name} {name} margin {value}px ({frac:.1%}) outside {lo:.0%}-{hi:.0%}"
            )


def clay_present(path):
    _w, _h, _box, raw = content_box(path)
    clay = (0x8C, 0x7B, 0x68)
    ink = (0x19, 0x18, 0x16)
    paper = (0xF1, 0xEE, 0xE6)
    count = 0
    for i in range(0, len(raw), 3):
        pixel = (raw[i], raw[i + 1], raw[i + 2])
        dc = abs(pixel[0] - clay[0]) + abs(pixel[1] - clay[1]) + abs(pixel[2] - clay[2])
        di = abs(pixel[0] - ink[0]) + abs(pixel[1] - ink[1]) + abs(pixel[2] - ink[2])
        dp = abs(pixel[0] - paper[0]) + abs(pixel[1] - paper[1]) + abs(pixel[2] - paper[2])
        if dc < 48 and dc < di and dc < dp:
            count += 1
    print(f"  clay pixels {count}")
    if count < 500:
        raise RuntimeError("duotone bud is missing from the mark raster")


def build_stills():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    geo = mark_geometry()

    mark = mark_scene(geo, [INK], "union")
    duo = mark_scene(geo, [CLAY, INK], "duo")
    lock = horizontal_scene(geo, INK)
    stack = stacked_scene(geo, INK)
    write_svg(OUT / "loam-mark.svg", mark, "Loam mark")
    write_svg(OUT / "loam-mark-duotone.svg", duo, "Loam mark, duotone")
    write_svg(OUT / "loam-lockup.svg", lock, "Loam")
    write_svg(OUT / "loam-stacked.svg", stack, "Loam")

    rasterize(lock.items, lock.viewbox, OUT / "loam-lockup.png", 2200, PAPER)
    rev = horizontal_scene(geo, PAPER)
    rasterize(rev.items, rev.viewbox, OUT / "loam-lockup-reversed.png", 2200, INK)
    avatar = square_scene(duo)
    rasterize(avatar.items, avatar.viewbox, OUT / "loam-mark.png", 1600, PAPER)
    stacked_png = PREVIEW / "stacked-check.png"
    rasterize(stack.items, stack.viewbox, stacked_png, 1400, PAPER)
    try:
        expect_margins(OUT / "loam-lockup.png", 0.04, 0.22)
        expect_margins(OUT / "loam-lockup-reversed.png", 0.04, 0.22)
        expect_margins(OUT / "loam-mark.png", 0.08, 0.28)
        expect_margins(stacked_png, 0.04, 0.16)
        clay_present(OUT / "loam-mark.png")
    finally:
        stacked_png.unlink(missing_ok=True)
        try:
            PREVIEW.rmdir()
        except OSError:
            pass
    print("stills written")
    for path in sorted(OUT.iterdir()):
        print(f"  {path.name:32} {path.stat().st_size:8d}")


def smootherstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def interval(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    return smootherstep((t - a) / (b - a))


def frame_items(geo, t, frame=1080):
    """Duotone lockup posed for time t, in a square of `frame` user units."""
    cap = 168.0
    mark_h = cap * MARK_INK_H
    _tx, _ty, _scale, right, top, bottom = transform_for(geo["duo_box"], mark_h, 0.0, cap / 2)
    tx, ty, scale = _tx, _ty, _scale
    _word, word_w = word_items(cap, INK)
    gap = cap * LOCKUP_GAP
    lock_w = right + gap + word_w
    over = cap * 0.02
    lock_top = min(top, -over)
    lock_bot = max(bottom, cap + over)
    lock_h = lock_bot - lock_top
    ox = (frame - lock_w) / 2
    oy = (frame - lock_h) / 2 - lock_top

    body_p = interval(t, 0.25, 1.45)
    bud_p = interval(t, 1.15, 2.55)
    word_p = interval(t, 3.05, 4.25)
    body_s = 0.96 + 0.04 * body_p
    bud_s = 0.55 + 0.45 * bud_p
    word_dy = (1.0 - word_p) * 12.0
    bcx, bcy = centroid(geo["bud"])
    pcx, pcy = centroid(geo["parent"])

    def place(ring, cx, cy, s):
        pts = []
        for x, y in ring:
            x = cx + (x - cx) * s
            y = cy + (y - cy) * s
            pts.append((ox + tx + x * scale, oy + ty + y * scale))
        return flatten_catmull(pts, 0.25)

    items = []
    if bud_p > 0.001:
        items.append(Item(CLAY, [place(geo["bud"], bcx, bcy, bud_s)], "", alpha=bud_p))
    if body_p > 0.001:
        items.append(Item(INK, [place(geo["parent"], pcx, pcy, body_s)], "", alpha=body_p))
    if word_p > 0.001:
        word, _w = word_items(cap, INK, origin=(ox + right + gap, oy + word_dy))
        for item in word:
            item.alpha = word_p
        items.extend(word)
    return items


def build_video(geo=None):
    if geo is None:
        geo = mark_geometry()
    frame = 1080
    ss = 2
    hi = frame * ss
    fps = 24
    nframes = fps * 6
    mp4 = OUT / "loam-emerge.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{hi}x{hi}",
        "-framerate", str(fps), "-i", "pipe:0",
        "-vf", f"scale={frame}:{frame}:flags=lanczos",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-movflags", "+faststart", "-an", str(mp4),
    ]
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    try:
        for i in range(nframes):
            items = frame_items(geo, i / fps, frame)
            proc.stdin.write(render(items, frame, frame, hi, hi, PAPER))
            if i % 24 == 0:
                print(f"  frame {i}/{nframes}", flush=True)
        proc.stdin.close()
        err = proc.stderr.read()
        code = proc.wait()
        if code != 0:
            raise RuntimeError(err.decode()[-2000:])
    except Exception:
        proc.kill()
        raise
    print(f"video {mp4.name} {mp4.stat().st_size}")


def preview_motion(geo=None):
    if geo is None:
        geo = mark_geometry()
    dest = PREVIEW / "motion"
    dest.mkdir(parents=True, exist_ok=True)
    for t in (0.0, 0.8, 1.6, 2.4, 3.6, 5.5):
        items = frame_items(geo, t)
        buf = render(items, 1080, 1080, 1080, 1080, PAPER)
        write_png(buf, 1080, 1080, dest / f"t{t:.1f}.png", 1080, 1080)
        print(f"  motion t={t:.1f}")


def _self_check():
    got = shift_d("M-15.25 -52.00L0.00 1.50Z", 10, 20)
    expect = "M-5.25 -32.00L10.00 21.50Z"
    if got != expect:
        raise RuntimeError(got)


if __name__ == "__main__":
    _self_check()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        build_stills()
    elif cmd == "motion":
        preview_motion()
    elif cmd == "video":
        build_video()
    else:
        raise SystemExit(f"unknown command {cmd}")
