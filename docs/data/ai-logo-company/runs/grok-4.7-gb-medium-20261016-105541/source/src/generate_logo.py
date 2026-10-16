#!/usr/bin/env python3
"""LOAM — identity for a generative AI company.

Mark: a seed in section. An organic husk, split at the upper right, a warm
stone interior, and a kernel held clear of the wall. Wordmark: a custom
monoline grotesque. Palette is warm and neutral.

Writes finished SVG files into ./output/.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
PREVIEW = ROOT / "src" / "preview"

INK = "#2A2724"
INK_SOFT = "#746E66"
FLESH = "#D9D1C4"
FLESH_DARK = "#3A352F"
PAPER = "#F6F3ED"
PAPER_INK = "#F3EEE6"
DEEP = "#1A1816"

SW = 13.0
HALF = SW / 2.0


def fmt(n: float) -> str:
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


def pts_to_smooth(points: list[tuple[float, float]], closed: bool = True) -> str:
    p = [(float(x), float(y)) for x, y in points]
    n = len(p)
    if n < 2:
        raise ValueError("need points")
    parts = [f"M {fmt(p[0][0])} {fmt(p[0][1])}"]
    steps = n if closed else n - 1
    for i in range(steps):
        if closed:
            p0, p1, p2, p3 = p[(i - 1) % n], p[i % n], p[(i + 1) % n], p[(i + 2) % n]
        else:
            p1, p2 = p[i], p[i + 1]
            p0 = p[i - 1] if i else (2 * p[0][0] - p[1][0], 2 * p[0][1] - p[1][1])
            p3 = p[i + 2] if i + 2 < n else (2 * p[-1][0] - p[-2][0], 2 * p[-1][1] - p[-2][1])
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        parts.append(
            f"C {fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(p2[0])} {fmt(p2[1])}"
        )
    if closed:
        parts.append("Z")
    return " ".join(parts)


def _at(cx, cy, rx, ry, rot, harmonics, u: float) -> tuple[float, float]:
    m = 1.0
    for k, amp, phase in harmonics:
        m += amp * math.sin(k * u + phase)
    x = rx * m * math.cos(u)
    y = ry * m * math.sin(u)
    ca, sa = math.cos(rot), math.sin(rot)
    return (cx + x * ca - y * sa, cy + x * sa + y * ca)


def bbox(groups: list[list[tuple[float, float]]], pad: float) -> tuple[float, float, float, float]:
    xs = [p[0] for g in groups for p in g]
    ys = [p[1] for g in groups for p in g]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    return minx - pad, miny - pad, (maxx - minx) + 2 * pad, (maxy - miny) + 2 * pad


def min_dist(points: list[tuple[float, float]], poly: list[tuple[float, float]]) -> float:
    best = 1e9
    m = len(poly)
    for px, py in points:
        for i in range(m):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % m]
            dx, dy = x2 - x1, y2 - y1
            l2 = dx * dx + dy * dy or 1.0
            t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
            best = min(best, math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)))
    return best


def _ribbon(center: list[tuple[float, float]], widths: list[float]) -> list[tuple[float, float]]:
    """Variable-width round-capped stroke along an open centerline."""
    n = len(center)
    tangents, normals = [], []
    for i in range(n):
        if i == 0:
            dx, dy = center[1][0] - center[0][0], center[1][1] - center[0][1]
        elif i == n - 1:
            dx, dy = center[-1][0] - center[-2][0], center[-1][1] - center[-2][1]
        else:
            dx = center[i + 1][0] - center[i - 1][0]
            dy = center[i + 1][1] - center[i - 1][1]
        length = math.hypot(dx, dy) or 1.0
        tx, ty = dx / length, dy / length
        tangents.append((tx, ty))
        normals.append((-ty, tx))

    left, right = [], []
    for p, (nx, ny), w in zip(center, normals, widths):
        h = w / 2.0
        left.append((p[0] + nx * h, p[1] + ny * h))
        right.append((p[0] - nx * h, p[1] - ny * h))

    def semicircle(a, b, toward: tuple[float, float], samples: int = 16):
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        vx, vy = a[0] - mx, a[1] - my
        radius = math.hypot(vx, vy) or 1.0
        tl = math.hypot(toward[0], toward[1]) or 1.0
        tx, ty = toward[0] / tl * radius, toward[1] / tl * radius

        def arc(sign: float):
            pts = []
            for k in range(1, samples):
                ang = sign * math.pi * k / samples
                ca, sa = math.cos(ang), math.sin(ang)
                pts.append((mx + vx * ca - vy * sa, my + vx * sa + vy * ca))
            return pts

        pos, neg = arc(1.0), arc(-1.0)
        want = (mx + tx, my + ty)
        dp = math.hypot(pos[len(pos) // 2][0] - want[0], pos[len(pos) // 2][1] - want[1])
        dn = math.hypot(neg[len(neg) // 2][0] - want[0], neg[len(neg) // 2][1] - want[1])
        return pos if dp < dn else neg

    end_cap = semicircle(left[-1], right[-1], tangents[-1])
    start_cap = semicircle(right[0], left[0], (-tangents[0][0], -tangents[0][1]))
    return left + end_cap + list(reversed(right)) + start_cap


def build_mark() -> dict:
    cx, cy = 160.0, 168.0
    rx, ry = 118.0, 132.0
    rot = -0.28
    harmonics = (
        (2, 0.085, 0.55),
        (3, 0.040, 1.35),
        (5, 0.016, 0.2),
    )

    target = -0.95
    best_u, best_d = 0.0, 1e9
    for i in range(720):
        u = -math.pi + 2 * math.pi * i / 720
        px, py = _at(cx, cy, rx, ry, rot, harmonics, u)
        ang = math.atan2(py - cy, px - cx)
        d = abs((ang - target + math.pi) % (2 * math.pi) - math.pi)
        if d < best_d:
            best_d, best_u = d, u

    gap = 0.82
    a1 = best_u + gap / 2.0
    a0 = best_u - gap / 2.0 + 2 * math.pi
    samples = 170
    center, widths = [], []
    for i in range(samples):
        u = a1 + (a0 - a1) * i / (samples - 1)
        pt = _at(cx, cy, rx * 0.80, ry * 0.80, rot, harmonics, u)
        center.append(pt)
        depth = (pt[1] - (cy - ry)) / (2.2 * ry)
        depth = max(0.0, min(1.0, depth))
        side = (cx - pt[0]) / rx
        w = 33.0 + 13.5 * depth + 3.5 * max(0.0, side)
        end = min(i, samples - 1 - i) / 16.0
        if end < 1:
            w *= 0.88 + 0.12 * end
        widths.append(w)

    coat = _ribbon(center, widths)

    inner, normals = [], []
    for i, p in enumerate(center):
        if i == 0:
            dx, dy = center[1][0] - p[0], center[1][1] - p[1]
        elif i == len(center) - 1:
            dx, dy = p[0] - center[-2][0], p[1] - center[-2][1]
        else:
            dx = center[i + 1][0] - center[i - 1][0]
            dy = center[i + 1][1] - center[i - 1][1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        normals.append((nx, ny))
        inner.append((p[0] - nx * widths[i] / 2.0, p[1] - ny * widths[i] / 2.0))

    outer_probe = (
        center[80][0] + normals[80][0] * widths[80] / 2.0,
        center[80][1] + normals[80][1] * widths[80] / 2.0,
    )
    if math.hypot(inner[80][0] - cx, inner[80][1] - cy) > math.hypot(
        outer_probe[0] - cx, outer_probe[1] - cy
    ):
        inner = [
            (
                center[i][0] + normals[i][0] * widths[i] / 2.0,
                center[i][1] + normals[i][1] * widths[i] / 2.0,
            )
            for i in range(len(center))
        ]

    mouth_a, mouth_b = inner[0], inner[-1]
    mouth = []
    for k in range(1, 14):
        t = k / 14.0
        x = mouth_a[0] * (1 - t) + mouth_b[0] * t
        y = mouth_a[1] * (1 - t) + mouth_b[1] * t
        pull = 0.18 * math.sin(math.pi * t)
        mouth.append((x + (cx - x) * pull, y + (cy - y) * pull))
    flesh = list(reversed(inner)) + mouth

    # Kernel sits in the cavity, clear of the husk. Nudge until the gap holds.
    # Low in the cavity, nudged right of the thick left wall.
    k_cx, k_cy = cx - 12.0, cy + 24.0
    k_rx, k_ry = 21.5, 26.5
    k_rot = 0.42
    k_harm = ((2, 0.10, 0.35), (3, 0.05, 1.05))
    kernel: list[tuple[float, float]] = []
    clearance = 0.0
    for _ in range(24):
        kernel = [
            _at(k_cx, k_cy, k_rx, k_ry, k_rot, k_harm, 2 * math.pi * i / 56) for i in range(56)
        ]
        clearance = min_dist(kernel, coat)
        if clearance >= 13.0:
            break
        k_rx *= 0.955
        k_ry *= 0.955
        k_cy -= 1.6
        k_cx += 1.1
    return {
        "coat": coat,
        "flesh": flesh,
        "kernel": kernel,
        "clearance": clearance,
        "kernel_center": (k_cx, k_cy),
        "kernel_radii": (k_rx, k_ry),
    }


def mark_body(colors: dict[str, str]) -> tuple[str, tuple[float, float, float, float], dict]:
    m = build_mark()
    box = bbox([m["coat"], m["flesh"], m["kernel"]], 12.0)
    flesh = colors["flesh"]
    parts = []
    if flesh and flesh != "none":
        parts.append(f'<path d="{pts_to_smooth(m["flesh"])}" fill="{flesh}"/>')
    parts.append(f'<path d="{pts_to_smooth(m["coat"])}" fill="{colors["coat"]}"/>')
    parts.append(f'<path d="{pts_to_smooth(m["kernel"])}" fill="{colors["kernel"]}"/>')
    return "\n  ".join(parts), box, m


def ellipse_cmd(cx, cy, rx, ry) -> str:
    return (
        f"M {fmt(cx - rx)} {fmt(cy)} "
        f"A {fmt(rx)} {fmt(ry)} 0 1 1 {fmt(cx + rx)} {fmt(cy)} "
        f"A {fmt(rx)} {fmt(ry)} 0 1 1 {fmt(cx - rx)} {fmt(cy)} Z"
    )


def wordmark_paths() -> tuple[list[tuple[str, str]], float]:
    """LOAM centerlines. Cap box is y = 0..100. Returns (path, group) and width.

    group is 'flat' for letters whose diagonal caps should be clipped to the
    cap box (A, M), and 'free' for L and O (O overshoots).
    """
    top = HALF
    base = 100.0 - HALF
    items: list[tuple[str, str]] = []
    x = 0.0

    # L
    l_w = 60.0
    items.append((f"M {fmt(x + HALF)} {fmt(top)} V {fmt(base)} H {fmt(x + l_w - HALF)}", "free"))
    x += l_w + 17.0

    # O
    o_w = 78.0
    over = 3.4
    rx = (o_w - SW) / 2.0
    ry = (100.0 + 2 * over - SW) / 2.0
    items.append((ellipse_cmd(x + o_w / 2.0, 50.0, rx, ry), "free"))
    x += o_w + 15.0

    # A — legs clipped flat at the cap and the baseline. Crossbar stays free
    # so a clip can't shave it; it sits well inside the box anyway.
    a_w = 74.0
    apex_x = x + a_w / 2.0
    apex_y = 16.5
    items.append(
        (
            f"M {fmt(x + HALF)} {fmt(base)} L {fmt(apex_x)} {fmt(apex_y)} L {fmt(x + a_w - HALF)} {fmt(base)}",
            "flat",
        )
    )
    bar_y = 63.0

    def along(x0, y0, x1, y1, y):
        t = (y - y0) / (y1 - y0)
        return x0 + (x1 - x0) * t

    lx = along(x + HALF, base, apex_x, apex_y, bar_y)
    rx_ = along(x + a_w - HALF, base, apex_x, apex_y, bar_y)
    items.append((f"M {fmt(lx + 7.6)} {fmt(bar_y)} H {fmt(rx_ - 7.6)}", "free"))
    x += a_w + 14.0

    # M
    m_w = 94.0
    items.append(
        (
            f"M {fmt(x + HALF)} {fmt(base)} V {fmt(top)} "
            f"L {fmt(x + m_w / 2.0)} {fmt(base)} "
            f"L {fmt(x + m_w - HALF)} {fmt(top)} V {fmt(base)}",
            "flat",
        )
    )
    x += m_w
    return items, x


def wordmark_group(x: float, y: float, scale: float, color: str, clip_id: str) -> tuple[str, float]:
    items, width = wordmark_paths()
    free = "\n    ".join(f'<path d="{d}"/>' for d, g in items if g == "free")
    flat = "\n      ".join(f'<path d="{d}"/>' for d, g in items if g == "flat")
    group = f'''<g fill="none" stroke="{color}" stroke-width="{fmt(SW)}" stroke-linecap="square" stroke-linejoin="miter" stroke-miterlimit="3.2" transform="translate({fmt(x)} {fmt(y)}) scale({fmt(scale)})">
    <clipPath id="{clip_id}"><rect x="-20" y="0" width="800" height="100"/></clipPath>
    {free}
    <g clip-path="url(#{clip_id})">
      {flat}
    </g>
  </g>'''
    return group, width * scale


def _shift(d: str, dx: float) -> str:
    if dx == 0:
        return d
    out = []
    tokens = d.replace(",", " ").split()
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("M", "L"):
            out.append(f"{t} {fmt(float(tokens[i + 1]) + dx)} {tokens[i + 2]}")
            i += 3
        elif t == "C":
            nums = [float(tokens[i + k]) for k in range(1, 7)]
            nums[0] += dx
            nums[2] += dx
            nums[4] += dx
            out.append(
                f"C {fmt(nums[0])} {fmt(nums[1])} {fmt(nums[2])} {fmt(nums[3])} "
                f"{fmt(nums[4])} {fmt(nums[5])}"
            )
            i += 7
        elif t == "H":
            out.append(f"H {fmt(float(tokens[i + 1]) + dx)}")
            i += 2
        elif t == "V":
            out.append(f"V {tokens[i + 1]}")
            i += 2
        elif t == "A":
            x = float(tokens[i + 6]) + dx
            out.append(
                f"A {tokens[i + 1]} {tokens[i + 2]} {tokens[i + 3]} {tokens[i + 4]} {tokens[i + 5]} {fmt(x)} {tokens[i + 7]}"
            )
            i += 8
        elif t in ("Z", "z"):
            out.append("Z")
            i += 1
        else:
            raise ValueError(f"bad token {t!r} in {d!r}")
    return " ".join(out)


def _poly(pts: list[tuple[float, float]], closed: bool = True) -> str:
    d = "M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x, y in pts)
    return d + (" Z" if closed else "")


def _filled_r(r_w: float) -> list[str]:
    """Stem, bowl, and leg as filled shapes in local cap-100 coordinates."""
    br = 21.0
    bcx, bcy = HALF, HALF + br
    arc = _arc(bcx, bcy, br, -math.pi / 2, 1.05, 32)
    bowl = _ribbon(arc, [SW] * len(arc))
    leg_a = 0.15
    start = (bcx + br * math.cos(leg_a), bcy + br * math.sin(leg_a))
    # Past the baseline; the tagline clip cuts the foot flat.
    foot = (r_w - HALF, 114.0)
    leg = _ribbon([start, foot], [SW, SW])
    stem = [(0.0, 0.0), (SW, 0.0), (SW, 100.0), (0.0, 100.0)]
    return [_poly(stem), _poly(bowl), _poly(leg)]


def _arc(cx, cy, r, a0, a1, n=28) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + r * math.sin(a0 + (a1 - a0) * i / (n - 1)))
        for i in range(n)
    ]


def tagline_items(gap: float) -> tuple[list[tuple[str, str]], float]:
    """GENERATIVE. Local letter paths, shifted once. Cap box y=0..100."""
    top = HALF
    base = 100.0 - HALF
    mid = 50.0
    items: list[tuple[str, str]] = []
    cursor = 0.0

    def add(d: str, width: float, cap: str = "square") -> None:
        nonlocal cursor
        items.append((_shift(d, cursor), cap))
        cursor += width + gap

    # G — open ring through the left, spur at mid-right. Angles use y-down
    # (positive sin is down). Decreasing angle walks the long way, west.
    g_w = 74.0
    gr = 32.0
    gcx = 36.0
    g_pts = _arc(gcx, 50.0, gr, -1.02, -2 * math.pi + 0.92, 32)
    add(pts_to_smooth(g_pts, closed=False), g_w)
    cursor -= g_w + gap
    add(f"M {fmt(gcx + 1)} {fmt(mid + 1)} H {fmt(gcx + gr + 1)}", g_w)

    # E
    e_w = 58.0
    add(
        f"M {fmt(e_w - HALF)} {fmt(top)} H {fmt(HALF)} V {fmt(base)} H {fmt(e_w - HALF)} "
        f"M {fmt(HALF)} {fmt(mid)} H {fmt(e_w - 18)}",
        e_w,
    )

    # N
    n_w = 72.0
    add(f"M {fmt(HALF)} {fmt(base)} V {fmt(top)}", n_w)
    cursor -= n_w + gap
    add(
        f"M {fmt(HALF + 2)} {fmt(top + 2)} L {fmt(n_w - HALF - 2)} {fmt(base - 2)}",
        n_w,
        "butt",
    )
    cursor -= n_w + gap
    add(f"M {fmt(n_w - HALF)} {fmt(top)} V {fmt(base)}", n_w)

    # E (the second one — GEN E RATIVE)
    add(
        f"M {fmt(e_w - HALF)} {fmt(top)} H {fmt(HALF)} V {fmt(base)} H {fmt(e_w - HALF)} "
        f"M {fmt(HALF)} {fmt(mid)} H {fmt(e_w - 18)}",
        e_w,
    )

    # R is filled, not stroked: the leg has to leave the bowl at an angle,
    # and overlapping strokes leave a bite. Same-color fills cover it.
    r_w = 66.0
    for d in _filled_r(r_w):
        items.append((_shift(d, cursor), "fill"))
    cursor += r_w + gap

    # A
    a_w = 68.0
    apex_y = 15.0
    add(
        f"M {fmt(HALF)} {fmt(base)} L {fmt(a_w / 2)} {fmt(apex_y)} L {fmt(a_w - HALF)} {fmt(base)}",
        a_w,
    )
    # add() left cursor just past this letter, including its trailing gap.
    bar_y = 64.0

    def along(x0, y0, x1, y1, y):
        t = (y - y0) / (y1 - y0)
        return x0 + (x1 - x0) * t

    lx = along(HALF, base, a_w / 2, apex_y, bar_y)
    rx_ = along(a_w - HALF, base, a_w / 2, apex_y, bar_y)
    items.append(
        (_shift(f"M {fmt(lx + 6.5)} {fmt(bar_y)} H {fmt(rx_ - 6.5)}", cursor - a_w - gap), "butt")
    )

    # T
    t_w = 60.0
    add(f"M {fmt(HALF)} {fmt(top)} H {fmt(t_w - HALF)}", t_w)
    cursor -= t_w + gap
    add(f"M {fmt(t_w / 2)} {fmt(top)} V {fmt(base)}", t_w)

    # I
    add(f"M {fmt(HALF)} {fmt(top)} V {fmt(base)}", SW)

    # V — valley kept high enough that the miter lands on the baseline.
    v_w = 66.0
    add(
        f"M {fmt(HALF)} {fmt(top)} L {fmt(v_w / 2)} {fmt(84)} L {fmt(v_w - HALF)} {fmt(top)}",
        v_w,
    )

    # E
    add(
        f"M {fmt(e_w - HALF)} {fmt(top)} H {fmt(HALF)} V {fmt(base)} H {fmt(e_w - HALF)} "
        f"M {fmt(HALF)} {fmt(mid)} H {fmt(e_w - 18)}",
        e_w,
    )

    cursor -= gap
    return items, cursor


def tagline_group(x: float, y: float, target_width: float, color: str, clip_id: str) -> str:
    """Small caps, tracked so the line matches the wordmark measure."""
    # Cap height is chosen so a comfortable gap still fills the measure:
    # letters stay legible, tracking stays open.
    target_cap = 16.0
    lo, hi = 10.0, 220.0
    items: list[tuple[str, str]] = []
    natural = 1.0
    gap = 40.0
    for _ in range(16):
        gap = (lo + hi) / 2.0
        items, natural = tagline_items(gap)
        width = natural * (target_cap / 100.0)
        if width < target_width:
            lo = gap
        else:
            hi = gap
    scale = target_width / natural
    # If that scale makes the cap much taller than target, tracking was the
    # wrong knob — it won't, because we solved for this scale's height via gap.
    # scale * 100 is the resulting cap height.
    bits = []
    for d, cap in items:
        if cap == "fill":
            bits.append(f'<path d="{d}" fill="currentColor" stroke="none"/>')
        else:
            bits.append(f'<path d="{d}" stroke-linecap="{cap}"/>')
    body = "\n      ".join(bits)
    sw = SW * 0.90
    return (
        f'<g fill="none" stroke="{color}" color="{color}" stroke-width="{fmt(sw)}" '
        f'stroke-linejoin="miter" stroke-miterlimit="2.2" '
        f'transform="translate({fmt(x)} {fmt(y)}) scale({fmt(scale)})">\n      '
        f'<clipPath id="{clip_id}"><rect x="-30" y="0" width="4000" height="100"/></clipPath>\n      '
        f'<g clip-path="url(#{clip_id})">{body}</g>\n    </g>'
    )


def wrap(vb: str, body: str, bg: str | None = None) -> str:
    bg_rect = ""
    if bg:
        a, b, c, d = vb.split()
        bg_rect = f'<rect x="{a}" y="{b}" width="{c}" height="{d}" fill="{bg}"/>\n  '
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="none">\n  '
        f"{bg_rect}{body}\n</svg>\n"
    )


def mark_group(body: str, box, x: float, y: float, target_h: float) -> tuple[str, float]:
    bx, by, bw, bh = box
    scale = target_h / bh
    svg = (
        f'<g transform="translate({fmt(x - bx * scale)} {fmt(y - by * scale)}) scale({fmt(scale)})">\n    '
        + body
        + "\n  </g>"
    )
    return svg, bw * scale


def build_files() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    body, box, meta = mark_body({"flesh": FLESH, "coat": INK, "kernel": INK})
    mono, _, _ = mark_body({"flesh": "none", "coat": INK, "kernel": INK})
    rev, _, _ = mark_body({"flesh": FLESH_DARK, "coat": PAPER_INK, "kernel": PAPER_INK})
    bx, by, bw, bh = box
    vb = f"{fmt(bx)} {fmt(by)} {fmt(bw)} {fmt(bh)}"
    (OUT / "loam-mark.svg").write_text(wrap(vb, body), encoding="utf-8")
    (OUT / "loam-mark-mono.svg").write_text(wrap(vb, mono), encoding="utf-8")
    # Reverse mark is only used to render the dark PNG; it is not a deliverable.
    (PREVIEW / "loam-mark-reverse.svg").write_text(wrap(vb, rev), encoding="utf-8")

    lock_h = 320.0
    mark_h = 236.0
    mark, mark_w = mark_group(body, box, 36.0, (lock_h - mark_h) / 2.0, mark_h)
    text_x = 36.0 + mark_w + 44.0
    cap = 84.0
    tag_gap = 20.0
    tag_cap_est = 16.0
    block = cap + tag_gap + tag_cap_est
    text_y = (lock_h - block) / 2.0 - 4.0
    wm, wm_w = wordmark_group(text_x, text_y, cap / 100.0, INK, "clip-lock")
    tag = tagline_group(text_x, text_y + cap + tag_gap, wm_w, INK_SOFT, "clip-tag-lock")
    right = text_x + wm_w + 36.0
    lock_vb = f"0 0 {fmt(right)} {fmt(lock_h)}"
    (OUT / "loam-lockup.svg").write_text(wrap(lock_vb, mark + "\n  " + wm + "\n  " + tag), encoding="utf-8")

    st_w = 480.0
    s_h = 248.0
    sm_w = bw * (s_h / bh)
    sm, _ = mark_group(body, box, (st_w - sm_w) / 2.0, 12.0, s_h)
    s_cap = 70.0
    _, nat = wordmark_group(0, 0, s_cap / 100.0, INK, "clip-measure")
    wm_x = (st_w - nat) / 2.0
    s_top = 12.0 + s_h + 26.0
    s_wm, s_wmw = wordmark_group(wm_x, s_top, s_cap / 100.0, INK, "clip-stack")
    s_tag = tagline_group(wm_x, s_top + s_cap + 16.0, s_wmw, INK_SOFT, "clip-tag-stack")
    st_h = s_top + s_cap + 16.0 + 18.0 + 24.0
    (OUT / "loam-stack.svg").write_text(
        wrap(f"0 0 {fmt(st_w)} {fmt(st_h)}", sm + "\n  " + s_wm + "\n  " + s_tag),
        encoding="utf-8",
    )

    # Large tagline specimen, generous gap, so each letter can be judged.
    items, nat_w = tagline_items(28.0)
    bits = []
    for d, cap in items:
        if cap == "fill":
            bits.append(f'<path d="{d}" fill="{INK}" stroke="none"/>')
        else:
            bits.append(f'<path d="{d}" stroke-linecap="{cap}"/>')
    paths = "\n  ".join(bits)
    (PREVIEW / "tagline.svg").write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -20 {fmt(nat_w + 80)} 140">
  <rect x="-40" y="-20" width="{fmt(nat_w + 80)}" height="140" fill="{PAPER}"/>
  <clipPath id="spec"><rect x="-40" y="0" width="{fmt(nat_w + 80)}" height="100"/></clipPath>
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linejoin="miter" stroke-miterlimit="2.2" clip-path="url(#spec)">
  {paths}
  </g>
</svg>
''',
        encoding="utf-8",
    )

    for leftover_name in ("loam-mark-on-dark.svg", "loam-mark-reverse.svg"):
        leftover = OUT / leftover_name
        if leftover.exists():
            leftover.unlink()

    print("clearance", round(meta["clearance"], 2), "kernel", tuple(round(v, 1) for v in meta["kernel_center"]), "r", tuple(round(v, 1) for v in meta["kernel_radii"]))
    print("mark", tuple(round(v, 1) for v in box))
    print("lockup", lock_vb)
    return {"lock_vb": lock_vb, "stack_h": st_h, "stack_w": st_w, "mark": box}


if __name__ == "__main__":
    build_files()
