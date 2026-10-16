#!/usr/bin/env python3
"""Octopus chef at a ramen booth — a self-contained SVG illustration.

Run from anywhere: python3 src/build_octopus_ramen.py
Writes ./output/octopus-chef-ramen-booth.svg
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLYPHS = {g["ch"]: g for g in json.loads((Path(__file__).parent / "glyphs.json").read_text())}

W, H = 1600, 1120

# Chef anchor
CX = 800
HEAD_CY, HEAD_RX, HEAD_RY = 524, 138, 118

# Counter plane. t=0 is the far edge, t=1 the near edge.
CB_Y, CF_Y = 748, 908
CB_L, CB_R = 400, 1200
CF_L, CF_R = 188, 1412
FACE_B = 1058
FACE_L, FACE_R = 236, 1364


def surface(t, u):
    """Point on the counter top. u=0 left, u=1 right."""
    y = CB_Y + t * (CF_Y - CB_Y)
    left = CB_L + t * (CF_L - CB_L)
    right = CB_R + t * (CF_R - CB_R)
    return left + u * (right - left), y


def face_x(y, side):
    span = FACE_B - CF_Y
    t = 0 if span == 0 else (y - CF_Y) / span
    t = max(0, min(1, t))
    if side == "l":
        return CF_L + t * (FACE_L - CF_L)
    return CF_R + t * (FACE_R - CF_R)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def chaikin(points, iterations=4):
    pts = list(points)
    for _ in range(iterations):
        nxt = [pts[0]]
        for i in range(len(pts) - 1):
            p, q = pts[i], pts[i + 1]
            nxt.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            nxt.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        nxt.append(pts[-1])
        pts = nxt
    return pts


def normals(center):
    """Unit normals, kept continuous so the sucker side does not flip."""
    n = len(center)
    out = []
    prev = None
    for i, (x, y) in enumerate(center):
        if i == 0:
            dx, dy = center[1][0] - x, center[1][1] - y
        elif i == n - 1:
            dx, dy = x - center[i - 1][0], y - center[i - 1][1]
        else:
            dx, dy = center[i + 1][0] - center[i - 1][0], center[i + 1][1] - center[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if prev is not None and nx * prev[0] + ny * prev[1] < 0:
            nx, ny = -nx, -ny
        prev = (nx, ny)
        out.append(prev)
    return out


def slice_center(points, samples=None):
    return samples if samples is not None else chaikin(points, 4)


def ribbon(center, norms, w0, w1, t0=0.0, t1=1.0, side_offset=0.0):
    """Tapered ribbon around a centerline. side_offset shifts it along the normal."""
    n = len(center)
    i0 = max(0, int(round(t0 * (n - 1))))
    i1 = min(n - 1, int(round(t1 * (n - 1))))
    if i1 - i0 < 2:
        i1 = min(n - 1, i0 + 2)
    left, right = [], []
    for i in range(i0, i1 + 1):
        t = i / (n - 1)
        k = t ** 0.85
        w = (w0 + (w1 - w0) * k) * 0.5
        nx, ny = norms[i]
        x, y = center[i]
        ox, oy = nx * side_offset, ny * side_offset
        left.append((x + ox + nx * w, y + oy + ny * w))
        right.append((x + ox - nx * w, y + oy - ny * w))
    poly = left + right[::-1]
    return poly


def path(points, close=True):
    if not points:
        return ""
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    return d + (" Z" if close else "")


def ellipse(cx, cy, rx, ry, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" {a}/>'


def circle(cx, cy, r, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {a}/>'


def rect(x, y, w, h, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {a}/>'


def dpath(d, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" {a}/>'


def group(content, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    inner = content if isinstance(content, str) else "\n".join(content)
    return f"<g {a}>\n{inner}\n</g>"


def glyph(ch, cx, cy, em, fill="#1B2744"):
    """Place a Hiragino glyph so its em square is `em` px and its bbox center sits at (cx, cy)."""
    g = GLYPHS[ch]
    x0, y0, x1, y1 = g["box"]
    s = em / 100.0
    gx = (x0 + x1) / 2
    gy = (y0 + y1) / 2
    return (
        f'<g fill="{fill}" transform="translate({cx:.2f} {cy:.2f}) scale({s:.4f}) '
        f'translate({-gx:.2f} {-gy:.2f})"><path d="{g["d"]}"/></g>'
    )


def end_pose(points):
    (x, y), (px, py) = points[-1], points[-2]
    ang = math.degrees(math.atan2(y - py, x - px))
    return x, y, ang


def quad(p0, p1, p2, t):
    u = 1 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


# ---------------------------------------------------------------------------
# Tentacles
# ---------------------------------------------------------------------------

def tentacle_geometry(spec):
    center = chaikin(spec["points"], 4)
    norms = normals(center)
    # Orient normals so +normal matches the requested sucker side.
    # `side` +1 means suckers on the left of travel (the default normal).
    side = spec.get("side", 1)
    if side < 0:
        norms = [(-nx, -ny) for nx, ny in norms]
    return center, norms


def draw_tentacle(spec, center, norms, t0=0.0, t1=1.0):
    w0, w1 = spec["w0"], spec["w1"]
    fill = spec.get("fill", "url(#tentMid)")
    main = ribbon(center, norms, w0, w1, t0, t1)
    under = ribbon(center, norms, w0 * 0.62, w1 * 0.62, t0, t1, side_offset=0)
    # Shift underside toward the sucker side (positive normal).
    under = ribbon(
        center, norms, w0 * 0.5, max(6, w1 * 0.55), t0, t1, side_offset=(w0 * 0.10)
    )
    parts = [
        dpath(path(main), fill=fill, stroke="#A83848", stroke_width="1.4",
              stroke_linejoin="round", stroke_linecap="round"),
        dpath(path(under), fill="#FFD0C4", opacity="0.95"),
    ]
    # Dorsal highlight: the edge opposite the suckers.
    n = len(center)
    i0 = max(0, int(round(t0 * (n - 1))))
    i1 = min(n - 1, int(round(t1 * (n - 1))))
    dorsal = []
    for i in range(i0, i1 + 1):
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * (t ** 0.85)) * 0.5
        nx, ny = norms[i]
        x, y = center[i]
        dorsal.append((x - nx * w * 0.82, y - ny * w * 0.82))
    parts.append(
        dpath(path(dorsal, close=False), fill="none", stroke="#FFD9CF",
              stroke_width="2.2", stroke_linecap="round", opacity="0.55")
    )
    parts.append(suckers(center, norms, w0, w1, t0, t1))
    return "\n".join(parts)


def suckers(center, norms, w0, w1, t0, t1):
    n = len(center)
    i0 = max(0, int(round(t0 * (n - 1))))
    i1 = min(n - 1, int(round(t1 * (n - 1))))
    bits = []
    acc = 999
    spacing = 20
    for i in range(i0, i1 + 1):
        if i > i0:
            acc += dist(center[i], center[i - 1])
        t = i / (n - 1)
        if t < t0 + 0.06 or t > t1 - 0.05:
            continue
        w = w0 + (w1 - w0) * (t ** 0.85)
        r = w * 0.20
        if r < 3.2:
            continue
        if acc < spacing * (0.85 + 0.4 * t):
            continue
        acc = 0
        nx, ny = norms[i]
        x, y = center[i]
        # Sit on the pale underside.
        sx = x + nx * w * 0.16
        sy = y + ny * w * 0.16
        bits.append(circle(sx, sy, r, fill="#E7A198"))
        bits.append(circle(sx, sy, r * 0.62, fill="#C45E5C"))
        bits.append(circle(sx + nx * r * 0.08, sy + ny * r * 0.08, r * 0.36, fill="#F6D2C8"))
        bits.append(circle(sx - r * 0.22, sy - r * 0.22, r * 0.14, fill="#FFFFFF", opacity="0.8"))
    return "\n".join(bits)


# ---------------------------------------------------------------------------
# Food
# ---------------------------------------------------------------------------

def broth_surface(cx, cy, rx, ry, clip, rich=True):
    parts = [
        ellipse(cx, cy, rx, ry, fill="url(#broth)"),
        ellipse(cx - rx * 0.18, cy - ry * 0.22, rx * 0.62, ry * 0.42, fill="#FBE6C2", opacity="0.55"),
        ellipse(cx + rx * 0.28, cy + ry * 0.1, rx * 0.18, ry * 0.16, fill="#FFE9C4", opacity="0.7"),
    ]
    # oil beads
    beads = [(-0.35, 0.15, 0.05), (0.15, -0.25, 0.035), (0.42, 0.2, 0.04), (-0.1, 0.35, 0.028)]
    for nx, ny, s in beads:
        parts.append(circle(cx + nx * rx, cy + ny * ry, max(2.2, rx * s), fill="#FFF1D2", opacity="0.8"))
    if rich:
        parts.append(circle(cx + rx * 0.22, cy - ry * 0.05, max(2.4, rx * 0.035), fill="#E24A32", opacity="0.85"))
        parts.append(circle(cx - rx * 0.05, cy + ry * 0.28, max(1.8, rx * 0.022), fill="#E24A32", opacity="0.7"))
    return group(parts, clip_path=f"url(#{clip})")


def noodle_nest(cx, cy, rx, ry, clip, gap=0.0):
    """Wavy noodle nest. `gap` opens a hole on the right where noodles are lifted out."""
    parts = []
    strands = 8
    for i in range(strands):
        yy = cy + (i - (strands - 1) / 2) * ry * 0.16
        amp = ry * (0.10 + (i % 3) * 0.03)
        phase = i * 0.7
        x_end = cx + rx * (0.72 - gap)
        d = [f"M {cx - rx * 0.78:.1f} {yy:.1f}"]
        steps = 6
        for s in range(steps):
            t = (s + 1) / steps
            x = cx - rx * 0.78 + t * (x_end - (cx - rx * 0.78))
            y = yy + math.sin(t * math.pi * 2 + phase) * amp
            c1x = cx - rx * 0.78 + (t - 0.5 / steps) * (x_end - (cx - rx * 0.78))
            c1y = yy + math.sin((t - 0.35 / steps) * math.pi * 2 + phase) * amp * 1.1
            d.append(f"Q {c1x:.1f} {c1y:.1f} {x:.1f} {y:.1f}")
        color = "#F4E2B0" if i % 2 == 0 else "#E6C888"
        width = 3.4 if i % 3 else 4.4
        parts.append(dpath(" ".join(d), fill="none", stroke=color, stroke_width=f"{width}",
                           stroke_linecap="round"))
    return group(parts, clip_path=f"url(#{clip})", opacity="0.95")


def chashu(cx, cy, s=1.0, rot=-28):
    """A slice of pork, marbled, rotated."""
    body = ellipse(0, 0, 26 * s, 17 * s, fill="#E08A78")
    edge = ellipse(0, 0, 26 * s, 17 * s, fill="none", stroke="#C46A62", stroke_width=str(1.4 * s))
    fat1 = dpath(
        f"M {-16*s:.1f} {-2*s:.1f} Q {-2*s:.1f} {-8*s:.1f} {14*s:.1f} {0:.1f}",
        fill="none", stroke="#F3C2B4", stroke_width=str(3.2 * s), stroke_linecap="round",
    )
    fat2 = dpath(
        f"M {-12*s:.1f} {6*s:.1f} Q {2*s:.1f} {2*s:.1f} {12*s:.1f} {7*s:.1f}",
        fill="none", stroke="#F7D2C6", stroke_width=str(2.2 * s), stroke_linecap="round",
    )
    hi = ellipse(-8 * s, -6 * s, 7 * s, 4 * s, fill="#FFFFFF", opacity="0.35")
    return group([body, edge, fat1, fat2, hi], transform=f"translate({cx:.1f} {cy:.1f}) rotate({rot})")


def egg_half(cx, cy, s=1.0):
    white = ellipse(cx, cy, 18 * s, 15 * s, fill="#FBF6EC")
    white_edge = ellipse(cx, cy, 18 * s, 15 * s, fill="none", stroke="#E4D3BC", stroke_width=str(1.2 * s))
    yolk = circle(cx + 1 * s, cy + 0.5 * s, 9.2 * s, fill="url(#yolk)")
    yolk_rim = circle(cx + 1 * s, cy + 0.5 * s, 9.2 * s, fill="none", stroke="#E08A18", stroke_width=str(1.1 * s))
    gloss = circle(cx - 2.5 * s, cy - 3 * s, 3.1 * s, fill="#FFF6D8", opacity="0.9")
    return "\n".join([white, white_edge, yolk, yolk_rim, gloss])


def nori_sheet(cx, cy, s=1.0, rot=-12):
    w, h = 30 * s, 42 * s
    d = (
        f"M {-w/2:.1f} {-h/2 + 4:.1f} "
        f"Q {-w/2 - 2:.1f} {0:.1f} {-w/2:.1f} {h/2 - 2:.1f} "
        f"Q {0:.1f} {h/2 + 3:.1f} {w/2:.1f} {h/2 - 2:.1f} "
        f"Q {w/2 + 2:.1f} {0:.1f} {w/2:.1f} {-h/2 + 4:.1f} "
        f"Q {0:.1f} {-h/2 - 1:.1f} {-w/2:.1f} {-h/2 + 4:.1f} Z"
    )
    sheet = dpath(d, fill="#1C3C34")
    sheen = dpath(
        f"M {-w*0.28:.1f} {-h*0.3:.1f} Q {-w*0.05:.1f} {0:.1f} {-w*0.22:.1f} {h*0.32:.1f}",
        fill="none", stroke="#2F6A56", stroke_width=str(3 * s), stroke_linecap="round", opacity="0.8",
    )
    return group([sheet, sheen], transform=f"translate({cx:.1f} {cy:.1f}) rotate({rot})")


def naruto(cx, cy, s=1.0):
    r = 12 * s
    parts = [
        circle(cx, cy, r, fill="#FFF8F4", stroke="#F3C2CE", stroke_width=str(1.2 * s)),
    ]
    # pink spiral
    d = []
    steps = 28
    for i in range(steps):
        t = i / (steps - 1)
        a = t * 2.15 * math.pi
        rr = r * 0.78 * t
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a)
        d.append(("M " if i == 0 else "L ") + f"{x:.1f} {y:.1f}")
    parts.append(dpath("".join(d), fill="none", stroke="#F090A8", stroke_width=str(2.0 * s),
                       stroke_linecap="round"))
    return "\n".join(parts)


def scallion_bits(cx, cy, rx, ry, n=7, spread=1.0):
    parts = []
    spots = [
        (-0.45, 0.05, 18), ( -0.2, 0.35, -24), (0.05, -0.15, 12),
        (0.28, 0.22, -8), (0.48, -0.05, 30), (-0.05, 0.05, 6),
        (0.18, -0.38, -16), (-0.32, -0.28, 22),
    ]
    for i, (nx, ny, rot) in enumerate(spots[:n]):
        x = cx + nx * rx * spread
        y = cy + ny * ry * spread
        col = "#3E9A52" if i % 2 == 0 else "#7DCA78"
        parts.append(
            rect(-5, -1.6, 10, 3.2, rx="1.4", fill=col,
                 transform=f"translate({x:.1f} {y:.1f}) rotate({rot})")
        )
    return "\n".join(parts)


def menma(cx, cy, s=1.0):
    parts = []
    for i, rot in enumerate((-18, 4, 16)):
        col = "#F0D59A" if i != 1 else "#E2C488"
        parts.append(
            rect(-11 * s, -2.2 * s, 22 * s, 4.4 * s, rx="2", fill=col,
                 transform=f"translate({cx + i * 3 * s:.1f} {cy + (i - 1) * 3 * s:.1f}) rotate({rot})")
        )
    return "\n".join(parts)


def bowl(cx, cy, scale, toppings, clip_id, variant="cream"):
    """3/4 view ramen bowl. `cy` is the rim center. Foot sits about `depth` below."""
    s = scale
    rx, ry, depth = 112 * s, 40 * s, 82 * s
    parts = []
    # contact shadow
    parts.append(ellipse(cx, cy + depth * 0.92, rx * 0.72, ry * 0.55,
                         fill="#1A0C08", opacity="0.28", filter="url(#blur8)"))
    # foot
    parts.append(ellipse(cx, cy + depth * 0.98, rx * 0.34, ry * 0.48, fill="#E4D5C4"))
    parts.append(ellipse(cx, cy + depth * 0.98, rx * 0.34, ry * 0.48, fill="none",
                         stroke="#CDBBA6", stroke_width="1.2"))
    # body
    body = (
        f"M {cx - rx:.1f} {cy:.1f} "
        f"C {cx - rx * 1.03:.1f} {cy + depth * 0.42:.1f}, {cx - rx * 0.52:.1f} {cy + depth:.1f}, {cx:.1f} {cy + depth:.1f} "
        f"C {cx + rx * 0.52:.1f} {cy + depth:.1f}, {cx + rx * 1.03:.1f} {cy + depth * 0.42:.1f}, {cx + rx:.1f} {cy:.1f} Z"
    )
    body_fill = "#F6F1E8" if variant != "red" else "#F3E6DE"
    parts.append(dpath(body, fill=body_fill))
    # right-side shade
    shade = (
        f"M {cx + rx * 0.15:.1f} {cy + 2:.1f} "
        f"C {cx + rx * 0.85:.1f} {cy + depth * 0.35:.1f}, {cx + rx * 0.55:.1f} {cy + depth * 0.9:.1f}, {cx + rx * 0.05:.1f} {cy + depth:.1f} "
        f"L {cx + rx:.1f} {cy:.1f} Z"
    )
    parts.append(dpath(shade, fill="#E7D3C2", opacity="0.55"))
    # gloss on the left belly
    parts.append(dpath(
        f"M {cx - rx * 0.72:.1f} {cy + depth * 0.18:.1f} "
        f"Q {cx - rx * 0.78:.1f} {cy + depth * 0.5:.1f} {cx - rx * 0.42:.1f} {cy + depth * 0.78:.1f}",
        fill="none", stroke="#FFFFFF", stroke_width=str(5 * s), stroke_linecap="round", opacity="0.35",
    ))
    if variant == "red":
        parts.append(dpath(
            f"M {cx - rx * 0.86:.1f} {cy + depth * 0.28:.1f} "
            f"Q {cx:.1f} {cy + depth * 0.55:.1f} {cx + rx * 0.86:.1f} {cy + depth * 0.28:.1f}",
            fill="none", stroke="#B4333A", stroke_width=str(7 * s), stroke_linecap="round", opacity="0.9",
        ))
    # rim disk (inner wall color) then broth
    parts.append(ellipse(cx, cy, rx * 0.98, ry * 0.98, fill="#E7D8C6"))
    # far inner wall slightly deeper
    parts.append(ellipse(cx, cy - ry * 0.08, rx * 0.86, ry * 0.62, fill="#D8C4AE", opacity="0.0"))
    brx, bry = rx * 0.80, ry * 0.62
    bcy = cy + ry * 0.06
    parts.append(
        f'<clipPath id="{clip_id}"><ellipse cx="{cx:.1f}" cy="{bcy:.1f}" rx="{brx:.1f}" ry="{bry:.1f}"/></clipPath>'
    )
    parts.append(broth_surface(cx, bcy, brx, bry, clip_id, rich=True))
    parts.append(noodle_nest(cx, bcy + 1, brx * 0.92, bry * 0.85, clip_id,
                             gap=0.35 if "lift" in toppings else 0.0))
    # toppings in bowl-local space. ny=-1 is the far side.
    def bp(nx, ny):
        return cx + nx * brx * 0.78, cy + ry * 0.06 + ny * bry * 0.62

    if "nori" in toppings:
        x, y = bp(0.05, -0.72)
        parts.append(nori_sheet(x, y - 8 * s, s * 0.95, rot=-6))
    if "menma" in toppings:
        x, y = bp(-0.05, -0.25)
        parts.append(menma(x, y, s))
    if "chashu" in toppings:
        x, y = bp(-0.38, 0.02)
        parts.append(chashu(x, y, s * 0.95, rot=-32))
        x2, y2 = bp(-0.18, 0.22)
        parts.append(chashu(x2, y2, s * 0.82, rot=-14))
    if "egg" in toppings:
        x, y = bp(0.36, 0.08)
        parts.append(egg_half(x, y, s * 0.95))
    if "naruto" in toppings:
        x, y = bp(-0.08, 0.48)
        parts.append(naruto(x, y, s))
    if "scallion" in toppings:
        parts.append(scallion_bits(cx, cy + ry * 0.05, brx, bry, n=6))
    # front lip
    lip = (
        f"M {cx - rx * 0.96:.1f} {cy + ry * 0.08:.1f} "
        f"A {rx * 0.96:.1f} {ry * 0.98:.1f} 0 0 0 {cx + rx * 0.96:.1f} {cy + ry * 0.08:.1f}"
    )
    band = "#2A4A72" if variant != "red" else "#8E242C"
    parts.append(dpath(lip, fill="none", stroke=band, stroke_width=str(3.4 * s), stroke_linecap="round"))
    parts.append(dpath(lip, fill="none", stroke="#FFFcf8", stroke_width=str(2.0 * s),
                       stroke_linecap="round", opacity="0.85",
                       transform=f"translate(0 {1.5 * s:.1f})"))
    return "\n".join(parts), (brx, bry)


def pot(cx, rim_y, rx, ry, body_h):
    base_y = rim_y + body_h
    parts = []
    parts.append(ellipse(cx, base_y + 8, rx * 0.8, ry * 0.7, fill="#1A0C08", opacity="0.3", filter="url(#blur8)"))
    body = (
        f"M {cx - rx:.1f} {rim_y:.1f} "
        f"L {cx - rx * 0.82:.1f} {base_y:.1f} "
        f"A {rx * 0.82:.1f} {ry * 0.72:.1f} 0 0 0 {cx + rx * 0.82:.1f} {base_y:.1f} "
        f"L {cx + rx:.1f} {rim_y:.1f} "
        f"A {rx:.1f} {ry:.1f} 0 0 1 {cx - rx:.1f} {rim_y:.1f} Z"
    )
    parts.append(dpath(body, fill="url(#iron)"))
    # left highlight
    parts.append(dpath(
        f"M {cx - rx * 0.78:.1f} {rim_y + 10:.1f} "
        f"Q {cx - rx * 0.7:.1f} {rim_y + body_h * 0.5:.1f} {cx - rx * 0.55:.1f} {base_y - 8:.1f}",
        fill="none", stroke="#8A6A5C", stroke_width="5", stroke_linecap="round", opacity="0.45",
    ))
    # handles
    for sign in (-1, 1):
        hx = cx + sign * rx * 1.02
        parts.append(ellipse(hx, rim_y + body_h * 0.28, 14, 8, fill="#3A342F", stroke="#2A2622", stroke_width="1.5"))
    # rim
    parts.append(ellipse(cx, rim_y, rx, ry, fill="#4A453F"))
    parts.append(ellipse(cx, rim_y, rx * 0.86, ry * 0.70, fill="#2C2824"))
    # broth
    parts.append(ellipse(cx, rim_y + ry * 0.08, rx * 0.74, ry * 0.52, fill="url(#broth)"))
    parts.append(ellipse(cx - rx * 0.12, rim_y - ry * 0.05, rx * 0.40, ry * 0.22, fill="#FBE6C2", opacity="0.45"))
    # swirl
    parts.append(dpath(
        f"M {cx - rx * 0.28:.1f} {rim_y:.1f} "
        f"C {cx - rx * 0.05:.1f} {rim_y - ry * 0.35:.1f}, {cx + rx * 0.3:.1f} {rim_y + ry * 0.1:.1f}, {cx + rx * 0.05:.1f} {rim_y + ry * 0.15:.1f}",
        fill="none", stroke="#E8C48A", stroke_width="2.5", stroke_linecap="round", opacity="0.7",
    ))
    # ripples
    parts.append(ellipse(cx + 8, rim_y + 2, 16, 6, fill="none", stroke="#FFF1D4", stroke_width="1.4", opacity="0.7"))
    parts.append(ellipse(cx + 8, rim_y + 2, 28, 10, fill="none", stroke="#FFF1D4", stroke_width="1.1", opacity="0.45"))
    return "\n".join(parts)


def paddle(handle_tip, blade_center, angle):
    """Wooden paddle. handle_tip is in the tentacle, blade_center in the broth."""
    x, y = blade_center
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    # blade
    parts = []
    parts.append(group([
        ellipse(0, 0, 26, 16, fill="#C4924E"),
        ellipse(0, 0, 26, 16, fill="none", stroke="#8C6230", stroke_width="1.5"),
        dpath("M -14 -2 Q 0 -8 16 0", fill="none", stroke="#E6C48A", stroke_width="2.4",
              stroke_linecap="round", opacity="0.7"),
    ], transform=f"translate({x:.1f} {y:.1f}) rotate({angle:.1f})"))
    # handle from blade back toward the grip
    hx, hy = handle_tip
    parts.append(dpath(
        f"M {x - dx * 20:.1f} {y - dy * 20:.1f} L {hx:.1f} {hy:.1f}",
        fill="none", stroke="#A8743C", stroke_width="7", stroke_linecap="round",
    ))
    parts.append(dpath(
        f"M {x - dx * 20:.1f} {y - dy * 18:.1f} L {hx:.1f} {hy - 1:.1f}",
        fill="none", stroke="#E2BC80", stroke_width="2", stroke_linecap="round", opacity="0.7",
    ))
    return "\n".join(parts)


def ladle(grip, angle, length=78):
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    gx, gy = grip
    cx, cy = gx + dx * length, gy + dy * length
    parts = []
    # handle
    parts.append(dpath(
        f"M {gx:.1f} {gy:.1f} L {cx - dx * 16:.1f} {cy - dy * 16:.1f}",
        fill="none", stroke="#C5CDD4", stroke_width="6", stroke_linecap="round",
    ))
    parts.append(dpath(
        f"M {gx:.1f} {gy - 1:.1f} L {cx - dx * 16:.1f} {cy - dy * 16:.1f}",
        fill="none", stroke="#FFFFFF", stroke_width="1.6", stroke_linecap="round", opacity="0.6",
    ))
    # cup
    parts.append(group([
        ellipse(0, 0, 20, 14, fill="#D5DDE2"),
        ellipse(0, 4, 14, 8, fill="#8EA0AA"),
        ellipse(-5, -3, 6, 3, fill="#FFFFFF", opacity="0.55"),
        ellipse(0, 0, 20, 14, fill="none", stroke="#6E808A", stroke_width="1.4"),
    ], transform=f"translate({cx:.1f} {cy:.1f}) rotate({angle:.1f})"))
    # drip just under the cup
    drop_x = cx + dx * 6
    drop_y = cy + dy * 18 + 16
    parts.append(dpath(
        f"M {drop_x:.1f} {drop_y - 9:.1f} "
        f"C {drop_x - 5:.1f} {drop_y:.1f} {drop_x - 4.5:.1f} {drop_y + 7:.1f} {drop_x:.1f} {drop_y + 9:.1f} "
        f"C {drop_x + 4.5:.1f} {drop_y + 7:.1f} {drop_x + 5:.1f} {drop_y:.1f} {drop_x:.1f} {drop_y - 9:.1f} Z",
        fill="#F0C27A",
    ))
    parts.append(ellipse(drop_x - 1.5, drop_y - 1, 1.6, 2.2, fill="#FFF4DC", opacity="0.8"))
    return "\n".join(parts), (cx, cy)


def chopsticks(grip, angle, length=108):
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    px, py = -dy, dx
    gx, gy = grip
    parts = []
    for sign, col, hi in ((-1, "#C49255", "#E6C48A"), (1, "#A87440", "#D7B07A")):
        ox, oy = px * sign * 3.2, py * sign * 3.2
        x0, y0 = gx + ox, gy + oy
        x1, y1 = gx + dx * length + ox * 0.3, gy + dy * length + oy * 0.3
        parts.append(dpath(f"M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}",
                           fill="none", stroke=col, stroke_width="3.4", stroke_linecap="round"))
        parts.append(dpath(f"M {x0:.1f} {y0 - 0.6:.1f} L {x1:.1f} {y1 - 0.6:.1f}",
                           fill="none", stroke=hi, stroke_width="1.1", stroke_linecap="round", opacity="0.8"))
    tip = (gx + dx * length * 0.92, gy + dy * length * 0.92)
    return "\n".join(parts), tip


def hanging_noodles(origin, bowl_xy, n=5):
    """Strands dropping from the chopsticks into the bowl, each a simple downward arc."""
    ox, oy = origin
    bx, by = bowl_xy
    parts = []
    for i in range(n):
        spread = (i - (n - 1) / 2) * 9
        x0 = ox + spread * 0.25
        x1 = bx + spread
        y1 = by + (i % 2) * 3
        c1x, c1y = x0 + spread * 0.15, oy + 26
        c2x, c2y = x1 - spread * 0.1, oy + (y1 - oy) * 0.62
        color = "#F8E7B6" if i % 2 == 0 else "#E7C98A"
        width = 4.0 if i % 2 == 0 else 2.8
        d = f"M {x0:.1f} {oy:.1f} C {c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {x1:.1f} {y1:.1f}"
        parts.append(dpath(d, fill="none", stroke="#C9A15E", stroke_width=str(width + 1.8),
                           stroke_linecap="round"))
        parts.append(dpath(d, fill="none", stroke=color, stroke_width=str(width),
                           stroke_linecap="round"))
    parts.append(circle(ox + 4, oy + 36, 3.3, fill="#F0C27A"))
    return "\n".join(parts)


def cloth(cx, cy, rot=-20):
    d = (
        "M -28 -16 Q -10 -28 8 -14 Q 22 -26 36 -8 "
        "Q 30 10 10 16 Q -6 8 -20 18 Q -36 6 -28 -16 Z"
    )
    stripe = dpath("M -18 -6 Q 0 2 20 -2", fill="none", stroke="#2A4A72", stroke_width="5",
                   stroke_linecap="round", opacity="0.85")
    return group([
        dpath(d, fill="#F7F4EE", stroke="#E0D8CC", stroke_width="1.2"),
        stripe,
        dpath("M -8 4 Q 6 10 16 2", fill="none", stroke="#FFFFFF", stroke_width="2",
              stroke_linecap="round", opacity="0.7"),
    ], transform=f"translate({cx:.1f} {cy:.1f}) rotate({rot})")


def falling_scallions(x0, y0, x1, y1):
    parts = []
    for i in range(7):
        t = (i + 1) / 8
        x = x0 + (x1 - x0) * t + math.sin(i * 1.7) * 10
        y = y0 + (y1 - y0) * t
        rot = -20 + i * 18
        col = "#3E9A52" if i % 2 == 0 else "#8ED68A"
        parts.append(rect(-6.5, -2.1, 13, 4.2, rx="1.6", fill=col,
                          transform=f"translate({x:.1f} {y:.1f}) rotate({rot})"))
    return "\n".join(parts)


def steam_wisps(x, y, scale=1.0, n=4, seed=0):
    parts = []
    for i in range(n):
        ox = (i - (n - 1) / 2) * 16 * scale + ((seed + i) % 3) * 4
        h = (46 + ((i * 17 + seed) % 20)) * scale
        wob = (8 + i * 3) * scale
        d = (
            f"M {x + ox:.1f} {y:.1f} "
            f"C {x + ox - wob:.1f} {y - h * 0.35:.1f}, {x + ox + wob:.1f} {y - h * 0.62:.1f}, "
            f"{x + ox + wob * 0.2:.1f} {y - h:.1f}"
        )
        parts.append(dpath(d, fill="none", stroke="#FFF8F2", stroke_width=str(6 * scale),
                           stroke_linecap="round", opacity=str(0.22 + (i % 3) * 0.05)))
    return group(parts, filter="url(#steamBlur)")


# ---------------------------------------------------------------------------
# Scene pieces
# ---------------------------------------------------------------------------

def background():
    parts = []
    parts.append(rect(0, 0, W, H, fill="url(#sky)"))
    # warm horizon haze behind the stall
    parts.append(ellipse(800, 620, 780, 280, fill="url(#haze)", opacity="0.9"))
    # bokeh lanterns down the alley
    bokeh = [
        (120, 280, 46, 0.18), (260, 210, 22, 0.14), (1460, 250, 54, 0.16),
        (1340, 180, 18, 0.12), (90, 420, 16, 0.1), (1520, 400, 20, 0.12),
        (700, 120, 10, 0.18),
    ]
    for x, y, r, o in bokeh:
        parts.append(circle(x, y, r, fill="#FF7A3C", opacity=str(o), filter="url(#blur12)"))
        parts.append(circle(x, y, r * 0.28, fill="#FFD7A4", opacity=str(min(0.8, o * 3))))
    # stars
    stars = [(180, 60, 1.4), (420, 36, 1.1), (640, 74, 1.6), (980, 40, 1.2),
             (1180, 68, 1.5), (1400, 48, 1.1), (300, 100, 1.0), (1080, 28, 1.3)]
    for x, y, r in stars:
        parts.append(circle(x, y, r, fill="#F4E8D4", opacity="0.75"))
    # string lights
    p0, p1, p2 = (30, 48), (800, 108), (1570, 42)
    wire = []
    bulbs = []
    for i in range(33):
        t = i / 32
        x, y = quad(p0, p1, p2, t)
        wire.append((x, y))
        if 1 <= i <= 31 and i % 2 == 0:
            bulbs.append((x, y + 8))
    parts.append(dpath(path(wire, close=False), fill="none", stroke="#2A2030", stroke_width="1.6"))
    for x, y in bulbs:
        parts.append(circle(x, y, 10, fill="#FFB050", opacity="0.35", filter="url(#blur8)"))
        parts.append(circle(x, y, 4.2, fill="#FFE6B4"))
        parts.append(circle(x - 1.1, y - 1.1, 1.4, fill="#FFFFFF", opacity="0.9"))
    # ground
    parts.append(rect(0, 980, W, H - 980, fill="#1A1412"))
    parts.append(ellipse(800, 1040, 760, 90, fill="#FFAA5C", opacity="0.16", filter="url(#blur12)"))
    # a few paving hints
    for i, y in enumerate((1010, 1055)):
        parts.append(dpath(f"M 80 {y} H 1520", fill="none", stroke="#2A211C", stroke_width="2", opacity="0.7"))
    return "\n".join(parts)


def stall_shell():
    """Back wall, posts, roof, wheels. Noren and counter are separate so the chef can sit between them."""
    parts = []
    # back wall
    parts.append(rect(150, 175, 1300, 600, fill="url(#wallLight)"))
    # a shelf rail shadow
    parts.append(rect(160, 175, 1280, 18, fill="#2A1812", opacity="0.35"))
    # posts
    for px in (138, 1422):
        parts.append(rect(px, 150, 42, 900, rx="6", fill="url(#post)"))
        parts.append(rect(px + 6, 160, 8, 860, rx="3", fill="#E2B56A", opacity="0.18"))
    # wheels, tucked under the skirt later
    for px, cxw in ((160, 168), (1444, 1432)):
        parts.append(circle(cxw, 1072, 46, fill="#3A2A22", stroke="#241810", stroke_width="4"))
        parts.append(circle(cxw, 1072, 10, fill="#C4A070"))
        for ang in (20, 80, 140):
            rad = math.radians(ang)
            x2, y2 = cxw + math.cos(rad) * 34, 1072 + math.sin(rad) * 34
            parts.append(dpath(f"M {cxw:.1f} 1072 L {x2:.1f} {y2:.1f}",
                               fill="none", stroke="#2A1C16", stroke_width="3"))
    # roof top plane
    parts.append(dpath(
        "M 120 188 L 1480 188 L 1404 124 Q 800 92 196 124 Z",
        fill="#6B3E2A",
    ))
    # fascia
    parts.append(dpath(
        "M 96 176 L 1504 176 L 1488 214 L 112 214 Z",
        fill="#4A2C1C",
    ))
    parts.append(dpath(
        "M 112 180 H 1488",
        fill="none", stroke="#C4894F", stroke_width="2", opacity="0.45",
    ))
    # soffit
    parts.append(dpath(
        "M 150 214 L 1450 214 L 1410 246 L 190 246 Z",
        fill="#3A2218",
    ))
    # hanging bulb
    parts.append(dpath("M 800 214 V 246", fill="none", stroke="#2A2420", stroke_width="2"))
    parts.append(circle(800, 258, 28, fill="#FFB15A", opacity="0.45", filter="url(#blur12)"))
    parts.append(circle(800, 258, 9, fill="#FFE1A8"))
    parts.append(circle(797, 255, 3, fill="#FFFFFF", opacity="0.85"))
    return "\n".join(parts)


def shelf_and_sign():
    parts = []
    # open sign, hanging in the upper right of the opening
    sx, sy, sw, sh = 1016, 268, 86, 236
    parts.append(dpath(f"M {sx + 18} 214 V {sy}", fill="none", stroke="#3A2A22", stroke_width="1.6"))
    parts.append(dpath(f"M {sx + sw - 18} 214 V {sy}", fill="none", stroke="#3A2A22", stroke_width="1.6"))
    parts.append(rect(sx, sy, sw, sh, rx="8", fill="#6B3E28", stroke="#3E2416", stroke_width="2"))
    parts.append(rect(sx + 6, sy + 6, sw - 12, sh - 12, rx="4", fill="#F3E6C8"))
    em = 62
    for i, ch in enumerate("営業中"):
        parts.append(glyph(ch, sx + sw / 2, sy + 48 + i * 70, em, fill="#1B2744"))
    # shelf
    parts.append(dpath(
        "M 980 548 L 1168 548 L 1188 566 L 968 566 Z",
        fill="#8A5430",
    ))
    parts.append(dpath("M 980 548 L 1168 548", fill="none", stroke="#E2B56A", stroke_width="2", opacity="0.5"))
    # stacked empty bowls
    for i, (bx, by) in enumerate(((1022, 534), (1022, 522), (1022, 512))):
        parts.append(ellipse(bx, by, 22 - i, 8, fill="#F6F1E8", stroke="#E0D3C4", stroke_width="1"))
    # soy dispenser
    parts.append(dpath(
        "M 1088 548 L 1082 500 Q 1085 492 1104 492 Q 1107 500 1101 548 Z",
        fill="#3A2420",
    ))
    parts.append(rect(1090, 480, 10, 16, rx="2", fill="#2A1A16"))
    parts.append(rect(1086, 516, 18, 14, rx="2", fill="#F3E6C8"))
    parts.append(circle(1095, 523, 3.2, fill="#B4333A"))
    # rayu jar
    parts.append(rect(1124, 516, 26, 32, rx="4", fill="#E4573A", opacity="0.92"))
    parts.append(rect(1126, 508, 22, 10, rx="2", fill="#2C2422"))
    parts.append(rect(1128, 524, 6, 16, rx="2", fill="#FFD0A8", opacity="0.35"))
    return "\n".join(parts)


def noren():
    parts = []
    # rod
    parts.append(dpath("M 168 222 H 1432", fill="none", stroke="#3A2618", stroke_width="8", stroke_linecap="round"))
    parts.append(dpath("M 168 219 H 1432", fill="none", stroke="#8A5A34", stroke_width="2", stroke_linecap="round"))
    panels = [
        (176, "ラ"),
        (348, "ー"),
        (1098, "メ"),
        (1270, "ン"),
    ]
    pw, ph = 156, 214
    for x, ch in panels:
        y = 230
        # cloth with a soft hem
        d = (
            f"M {x:.1f} {y:.1f} H {x + pw:.1f} "
            f"V {y + ph - 8:.1f} "
            f"Q {x + pw / 2:.1f} {y + ph + 10:.1f} {x:.1f} {y + ph - 8:.1f} Z"
        )
        parts.append(dpath(d, fill="url(#norenCloth)"))
        # fold shadow on the right
        parts.append(dpath(
            f"M {x + pw - 16:.1f} {y:.1f} H {x + pw:.1f} V {y + ph - 12:.1f} "
            f"Q {x + pw - 6:.1f} {y + ph:.1f} {x + pw - 16:.1f} {y + ph - 18:.1f} Z",
            fill="#E4D8C4", opacity="0.8",
        ))
        # top tuck where it meets the rod
        parts.append(dpath(
            f"M {x + 10:.1f} {y:.1f} Q {x + pw / 2:.1f} {y + 16:.1f} {x + pw - 10:.1f} {y:.1f}",
            fill="none", stroke="#E7DCCC", stroke_width="3",
        ))
        parts.append(glyph(ch, x + pw / 2, y + ph * 0.48, 118, fill="#1B2744"))
        # ring
        parts.append(circle(x + pw / 2, 222, 4.5, fill="#C4A070", stroke="#3A2618", stroke_width="1.5"))
    return "\n".join(parts)


def chef_body():
    parts = []
    # arm crown — tentacles appear to gather here, under the coat
    parts.append(ellipse(CX, 712, 158, 52, fill="url(#skin)"))
    parts.append(ellipse(CX - 20, 700, 70, 22, fill="#FFB3A4", opacity="0.35"))
    # coat
    coat = (
        f"M 692 590 "
        f"Q {CX} 566 908 590 "
        f"L 958 718 "
        f"Q {CX} 742 642 718 Z"
    )
    parts.append(dpath(coat, fill="url(#coat)"))
    # hem shadow
    parts.append(dpath(
        f"M 650 708 Q {CX} 732 950 708",
        fill="none", stroke="#D9D0C4", stroke_width="3", stroke_linecap="round",
    ))
    # lapel lines
    parts.append(dpath(
        f"M 760 600 L {CX} 700",
        fill="none", stroke="#E4DCD2", stroke_width="2",
    ))
    parts.append(dpath(
        f"M 840 600 L {CX} 700",
        fill="none", stroke="#E4DCD2", stroke_width="2",
    ))
    # neckerchief
    parts.append(dpath(
        f"M 762 608 L {CX} 672 L 838 608 Q {CX} 630 762 608 Z",
        fill="#B4333A",
    ))
    parts.append(dpath(
        f"M 786 612 L {CX} 656 L 814 612",
        fill="none", stroke="#E7B4A8", stroke_width="2", stroke_linecap="round", opacity="0.7",
    ))
    # buttons
    for i, by in enumerate((640, 672, 704)):
        bx = 836 + i * 2
        parts.append(circle(bx, by, 5.2, fill="#E0C27A", stroke="#A6843E", stroke_width="1"))
        parts.append(circle(bx - 1.2, by - 1.2, 1.6, fill="#FFF6D8", opacity="0.9"))
        parts.append(circle(768 - i * 2, by, 5.2, fill="#E0C27A", stroke="#A6843E", stroke_width="1"))
    # pocket and handkerchief
    parts.append(dpath(
        "M 700 676 H 748 V 708 Q 724 714 700 708 Z",
        fill="none", stroke="#E4DCD2", stroke_width="1.6",
    ))
    parts.append(dpath(
        "M 708 676 L 724 658 L 740 676",
        fill="#2A4A72",
    ))
    return "\n".join(parts)


def chef_head():
    parts = []
    # cast shadow on the wall
    parts.append(ellipse(CX + 18, HEAD_CY + 24, HEAD_RX + 10, HEAD_RY + 6,
                         fill="#2A140C", opacity="0.0"))
    # darker rim blob for volume, peeking on the lower right
    parts.append(ellipse(CX + 8, HEAD_CY + 10, HEAD_RX, HEAD_RY, fill="#B33E4C"))
    # head
    parts.append(ellipse(CX, HEAD_CY, HEAD_RX, HEAD_RY, fill="url(#skin)"))
    # lantern uplight, clipped
    parts.append(ellipse(CX, HEAD_CY + 70, 100, 46, fill="#FFB060", opacity="0.28",
                         clip_path="url(#headClip)"))
    # spots
    spots = [(892, 470, 13), (910, 530, 8), (868, 575, 11), (840, 430, 7),
             (900, 500, 5.5), (720, 430, 6)]
    for x, y, r in spots:
        parts.append(circle(x, y, r, fill="#C44752", opacity="0.28", clip_path="url(#headClip)"))
    # specular
    parts.append(ellipse(CX - 48, HEAD_CY - 62, 36, 16, fill="#FFFFFF", opacity="0.38",
                         transform=f"rotate(-28 {CX - 48} {HEAD_CY - 62})"))
    parts.append(ellipse(CX - 70, HEAD_CY - 30, 10, 6, fill="#FFFFFF", opacity="0.28"))
    # left rim light
    parts.append(dpath(
        f"M {CX - 118} {HEAD_CY - 20} "
        f"Q {CX - 132} {HEAD_CY + 30} {CX - 90} {HEAD_CY + 78}",
        fill="none", stroke="#FFD2C6", stroke_width="5", stroke_linecap="round", opacity="0.65",
    ))

    # eyes
    for ex, flip in ((CX - 52, 1), (CX + 54, -1)):
        ey = HEAD_CY - 6
        parts.append(ellipse(ex, ey, 38, 42, fill="#FFF8F2"))
        parts.append(ellipse(ex, ey + 2, 24, 26, fill="#2A1A16"))
        parts.append(circle(ex + 2, ey + 8, 15.5, fill="#140E10"))
        parts.append(circle(ex - 8, ey - 8, 7.2, fill="#FFFFFF"))
        parts.append(circle(ex + 6, ey + 2, 2.8, fill="#FFFFFF", opacity="0.85"))
        # lid
        parts.append(dpath(
            f"M {ex - 30} {ey - 6} Q {ex} {ey - 50} {ex + 30} {ey - 8}",
            fill="none", stroke="#D25A58", stroke_width="4.5", stroke_linecap="round",
        ))
        parts.append(dpath(
            f"M {ex - 26} {ey - 10} Q {ex} {ey - 44} {ex + 26} {ey - 12}",
            fill="none", stroke="#A33E48", stroke_width="1.8", stroke_linecap="round", opacity="0.7",
        ))
        # brows arch up in the middle — a pleased, relaxed chef
        if flip > 0:
            parts.append(dpath(
                f"M {ex - 32} {ey - 54} Q {ex - 2} {ey - 76} {ex + 26} {ey - 48}",
                fill="none", stroke="#C45458", stroke_width="5", stroke_linecap="round",
            ))
        else:
            parts.append(dpath(
                f"M {ex - 26} {ey - 48} Q {ex + 2} {ey - 76} {ex + 32} {ey - 56}",
                fill="none", stroke="#C45458", stroke_width="5", stroke_linecap="round",
            ))
    # blush
    parts.append(ellipse(CX - 78, HEAD_CY + 36, 26, 14, fill="#FF7A86", opacity="0.45", filter="url(#blur3)"))
    parts.append(ellipse(CX + 80, HEAD_CY + 36, 26, 14, fill="#FF7A86", opacity="0.45", filter="url(#blur3)"))
    # smile
    parts.append(dpath(
        f"M {CX - 44} {HEAD_CY + 48} Q {CX} {HEAD_CY + 94} {CX + 44} {HEAD_CY + 48} "
        f"Q {CX} {HEAD_CY + 74} {CX - 44} {HEAD_CY + 48} Z",
        fill="#7A3040",
    ))
    parts.append(dpath(
        f"M {CX - 26} {HEAD_CY + 58} Q {CX} {HEAD_CY + 78} {CX + 22} {HEAD_CY + 60}",
        fill="none", stroke="#C46878", stroke_width="2.4", stroke_linecap="round", opacity="0.75",
    ))
    return "\n".join(parts)


def toque():
    parts = []
    # puff lobes
    parts.append(ellipse(CX - 62, 360, 52, 40, fill="#F4F1EA"))
    parts.append(ellipse(CX + 66, 356, 48, 38, fill="#E7E2D8"))
    parts.append(ellipse(CX, 328, 108, 78, fill="url(#toque)"))
    parts.append(ellipse(CX + 30, 340, 48, 50, fill="#E4DFD6", opacity="0.55"))
    # pleat lines
    for ox in (-48, -16, 16, 48):
        parts.append(dpath(
            f"M {CX + ox} 292 Q {CX + ox + 6} 330 {CX + ox - 2} 372",
            fill="none", stroke="#E0DBD2", stroke_width="2", stroke_linecap="round", opacity="0.9",
        ))
    # highlight
    parts.append(ellipse(CX - 36, 300, 32, 16, fill="#FFFFFF", opacity="0.55",
                         transform=f"rotate(-18 {CX - 36} 300)"))
    # band
    parts.append(rect(CX - 96, 392, 192, 42, rx="10", fill="#FFFcf8", stroke="#E4DDD2", stroke_width="1.5"))
    parts.append(rect(CX - 96, 420, 192, 10, rx="2", fill="#E7E0D6", opacity="0.8"))
    # stitch
    parts.append(dpath(
        f"M {CX - 80} 404 H {CX + 80}",
        fill="none", stroke="#E4D8C8", stroke_width="1.4", stroke_dasharray="4 3",
    ))
    return group(parts, transform=f"rotate(-7 {CX} 370)")


def counter():
    parts = []
    # top surface
    top = (
        f"M {CB_L} {CB_Y} L {CB_R} {CB_Y} L {CF_R} {CF_Y} L {CF_L} {CF_Y} Z"
    )
    parts.append(dpath(top, fill="url(#counterTop)"))
    # perspective grain
    for u in (0.18, 0.37, 0.55, 0.74, 0.9):
        x0, y0 = surface(0.05, u)
        x1, y1 = surface(0.96, u + 0.015)
        parts.append(dpath(f"M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}",
                           fill="none", stroke="#E2B56A", stroke_width="2", opacity="0.18"))
    # near lip
    lip = (
        f"M {CF_L} {CF_Y} L {CF_R} {CF_Y} L {CF_R - 8} {CF_Y + 16} L {CF_L + 8} {CF_Y + 16} Z"
    )
    parts.append(dpath(lip, fill="#6B4024"))
    parts.append(dpath(f"M {CF_L} {CF_Y} L {CF_R} {CF_Y}",
                       fill="none", stroke="#E2B56A", stroke_width="2", opacity="0.55"))
    # front face
    face = (
        f"M {CF_L} {CF_Y + 16} L {CF_R} {CF_Y + 16} "
        f"L {FACE_R} {FACE_B} L {FACE_L} {FACE_B} Z"
    )
    parts.append(dpath(face, fill="url(#counterFace)"))
    # red festival panel
    y0, y1 = CF_Y + 36, CF_Y + 118
    panel = (
        f"M {face_x(y0, 'l') + 40:.1f} {y0:.1f} "
        f"L {face_x(y0, 'r') - 40:.1f} {y0:.1f} "
        f"L {face_x(y1, 'r') - 48:.1f} {y1:.1f} "
        f"L {face_x(y1, 'l') + 48:.1f} {y1:.1f} Z"
    )
    parts.append(dpath(panel, fill="#A32E36"))
    # seigaiha clipped to the panel
    parts.append(f'<clipPath id="waveClip"><path d="{panel}"/></clipPath>')
    waves = ['<g clip-path="url(#waveClip)" fill="none" stroke="#F0C36A" stroke-width="1.35" opacity="0.9">']
    cell = 26
    x_left = face_x(y0, "l") + 20
    x_right = face_x(y0, "r") - 20
    row = 0
    yy = y0 + 8
    while yy < y1 + cell:
        off = 0 if row % 2 == 0 else cell / 2
        x = x_left - cell + off
        while x < x_right + cell:
            for rad in (cell * 0.46, cell * 0.30, cell * 0.16):
                waves.append(
                    f'<path d="M {x - rad:.1f} {yy:.1f} A {rad:.1f} {rad:.1f} 0 0 1 {x + rad:.1f} {yy:.1f}"/>'
                )
            x += cell
        yy += cell * 0.48
        row += 1
    waves.append("</g>")
    parts.append("\n".join(waves))
    # gold rules
    for yy in (y0, y1):
        parts.append(dpath(
            f"M {face_x(yy, 'l') + 36:.1f} {yy:.1f} L {face_x(yy, 'r') - 36:.1f} {yy:.1f}",
            fill="none", stroke="#E2B56A", stroke_width="2", opacity="0.8",
        ))
    return "\n".join(parts)


def lantern(cx, cy):
    parts = []
    parts.append(ellipse(cx, cy + 10, 70, 80, fill="#FF7A3A", opacity="0.28", filter="url(#blur12)"))
    body = (
        f"M {cx} {cy - 62} "
        f"C {cx - 48} {cy - 48}, {cx - 52} {cy + 48}, {cx} {cy + 66} "
        f"C {cx + 52} {cy + 48}, {cx + 48} {cy - 48}, {cx} {cy - 62} Z"
    )
    parts.append(dpath(body, fill="url(#lantern)"))
    for ox in (-18, 0, 18):
        parts.append(dpath(
            f"M {cx + ox} {cy - 48} Q {cx + ox + (4 if ox >= 0 else -4)} {cy} {cx + ox} {cy + 50}",
            fill="none", stroke="#A02828", stroke_width="1.5", opacity="0.4",
        ))
    parts.append(ellipse(cx - 14, cy - 8, 10, 22, fill="#FFD0A0", opacity="0.35"))
    # caps
    parts.append(rect(cx - 16, cy - 74, 32, 14, rx="3", fill="#241810"))
    parts.append(rect(cx - 16, cy + 60, 32, 12, rx="3", fill="#241810"))
    parts.append(dpath(f"M {cx} {cy - 74} V {cy - 96}", fill="none", stroke="#241810", stroke_width="2"))
    parts.append(circle(cx, cy - 96, 3, fill="#C4A070"))
    return "\n".join(parts)


def water_glass(cx, cy):
    parts = []
    parts.append(dpath(
        f"M {cx - 16} {cy - 28} L {cx - 12} {cy + 18} L {cx + 12} {cy + 18} L {cx + 16} {cy - 28} Z",
        fill="#D5E4EC", opacity="0.55", stroke="#F4FBFF", stroke_width="1.2",
    ))
    parts.append(ellipse(cx, cy - 28, 16, 6, fill="#E7F3F8", stroke="#C5D8E2", stroke_width="1"))
    parts.append(ellipse(cx, cy - 4, 13, 5, fill="#A9D4E4", opacity="0.65"))
    parts.append(dpath(
        f"M {cx - 10} {cy - 18} V {cy + 8}",
        fill="none", stroke="#FFFFFF", stroke_width="2", stroke_linecap="round", opacity="0.6",
    ))
    return "\n".join(parts)


def cutting_board(cx, cy):
    parts = []
    parts.append(rect(cx - 46, cy - 18, 92, 40, rx="6", fill="#E6C48A", stroke="#C49858", stroke_width="1.2",
                      transform=f"rotate(-8 {cx} {cy})"))
    # scallion stalks lying on the board
    for i in range(5):
        x = cx - 30 + i * 12
        y = cy - 4 + (i % 2) * 3
        parts.append(rect(-16, -2, 22, 4, rx="2", fill="#F4F1E4",
                          transform=f"translate({x:.1f} {y:.1f}) rotate({-20 + i * 6})"))
        parts.append(rect(2, -2, 14, 4, rx="2", fill="#3E9A52",
                          transform=f"translate({x:.1f} {y:.1f}) rotate({-20 + i * 6})"))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Tentacle layout
# ---------------------------------------------------------------------------

def tentacle_specs():
    """Eight arms, each kept in its own lane so the actions stay readable.

    Left: stir the pot, ladle the broth, one arm resting on the counter.
    Center: chopsticks lift noodles. A thick arm drops through the gap to
    cradle the finished bowl. Right: set an egg, scatter scallions, hold a towel.
    """
    return [
        dict(name="stir", z="mid", fill="url(#tentBack)", side=1, w0=40, w1=15,
             points=[(705, 705), (630, 760), (560, 755), (510, 710)]),
        dict(name="ladle", z="mid", fill="url(#tentMid)", side=-1, w0=36, w1=14,
             points=[(742, 690), (670, 615), (590, 545), (555, 600), (590, 675)]),
        dict(name="rest", z="front", fill="url(#tentMid)", side=-1, w0=32, w1=13,
             points=[(690, 758), (610, 845), (540, 905), (475, 878)]),
        dict(name="chops", z="front", fill="url(#tentFront)", side=1, w0=32, w1=12,
             points=[(868, 702), (845, 668), (818, 678), (808, 718)]),
        dict(name="egg", z="front", fill="url(#tentFront)", side=-1, w0=32, w1=13,
             points=[(925, 698), (1030, 688), (1135, 730), (1165, 785)]),
        dict(name="scallion", z="front", fill="url(#tentMid)", side=1, w0=28, w1=12,
             points=[(990, 668), (1110, 628), (1235, 675), (1205, 748)]),
        dict(name="cradle", z="hero", fill="url(#tentFront)", side=1, w0=44, w1=16,
             points=[(948, 742), (972, 870), (990, 980), (1045, 1068),
                     (1148, 1088), (1224, 1048), (1246, 992)]),
        dict(name="cloth", z="front", fill="url(#tentBack)", side=-1, w0=30, w1=13,
             points=[(1085, 768), (1190, 830), (1290, 868), (1348, 838)]),
    ]


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

DEFS = f"""
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#100E22"/>
    <stop offset="38%" stop-color="#1C1738"/>
    <stop offset="64%" stop-color="#4A2C4C"/>
    <stop offset="82%" stop-color="#2C1A20"/>
    <stop offset="100%" stop-color="#1A1412"/>
  </linearGradient>
  <radialGradient id="haze" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#FF8A3A" stop-opacity="0.28"/>
    <stop offset="55%" stop-color="#C45A3A" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#C45A3A" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="wallLight" cx="50%" cy="42%" r="68%">
    <stop offset="0%" stop-color="#7A4E38"/>
    <stop offset="48%" stop-color="#4A2C20"/>
    <stop offset="100%" stop-color="#2A1812"/>
  </radialGradient>
  <linearGradient id="post" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#3E2618"/>
    <stop offset="35%" stop-color="#8A5430"/>
    <stop offset="70%" stop-color="#5C381F"/>
    <stop offset="100%" stop-color="#3A2218"/>
  </linearGradient>
  <linearGradient id="norenCloth" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#FFF9F0"/>
    <stop offset="70%" stop-color="#F3EBDD"/>
    <stop offset="100%" stop-color="#E7DCCC"/>
  </linearGradient>
  <radialGradient id="skin" cx="35%" cy="32%" r="75%">
    <stop offset="0%" stop-color="#FFC3B4"/>
    <stop offset="42%" stop-color="#F28474"/>
    <stop offset="78%" stop-color="#E15C58"/>
    <stop offset="100%" stop-color="#C4454E"/>
  </radialGradient>
  <linearGradient id="tentFront" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFB2A4"/>
    <stop offset="45%" stop-color="#F07A6A"/>
    <stop offset="100%" stop-color="#D45356"/>
  </linearGradient>
  <linearGradient id="tentMid" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#F7A090"/>
    <stop offset="50%" stop-color="#E36A5E"/>
    <stop offset="100%" stop-color="#C4474E"/>
  </linearGradient>
  <linearGradient id="tentBack" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#E8887C"/>
    <stop offset="100%" stop-color="#B33E4C"/>
  </linearGradient>
  <linearGradient id="coat" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFFcf8"/>
    <stop offset="55%" stop-color="#F4EFE6"/>
    <stop offset="100%" stop-color="#E0D8CC"/>
  </linearGradient>
  <radialGradient id="toque" cx="38%" cy="35%" r="70%">
    <stop offset="0%" stop-color="#FFFFFF"/>
    <stop offset="60%" stop-color="#F7F4EE"/>
    <stop offset="100%" stop-color="#E4DFD6"/>
  </radialGradient>
  <linearGradient id="counterTop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#D7A15C"/>
    <stop offset="40%" stop-color="#C4894A"/>
    <stop offset="100%" stop-color="#A86E38"/>
  </linearGradient>
  <linearGradient id="counterFace" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#8A5430"/>
    <stop offset="100%" stop-color="#5C381F"/>
  </linearGradient>
  <radialGradient id="broth" cx="40%" cy="40%" r="70%">
    <stop offset="0%" stop-color="#FDE6C0"/>
    <stop offset="45%" stop-color="#F0B56A"/>
    <stop offset="100%" stop-color="#D8883E"/>
  </radialGradient>
  <radialGradient id="yolk" cx="35%" cy="35%" r="70%">
    <stop offset="0%" stop-color="#FFE08A"/>
    <stop offset="55%" stop-color="#F0A020"/>
    <stop offset="100%" stop-color="#E08A18"/>
  </radialGradient>
  <linearGradient id="iron" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#5A5048"/>
    <stop offset="30%" stop-color="#3A342F"/>
    <stop offset="70%" stop-color="#2A2624"/>
    <stop offset="100%" stop-color="#1C1A1A"/>
  </linearGradient>
  <radialGradient id="lantern" cx="40%" cy="40%" r="65%">
    <stop offset="0%" stop-color="#FFB15A"/>
    <stop offset="40%" stop-color="#E4453A"/>
    <stop offset="100%" stop-color="#A32028"/>
  </radialGradient>
  <radialGradient id="vig" cx="50%" cy="46%" r="72%">
    <stop offset="62%" stop-color="#07060F" stop-opacity="0"/>
    <stop offset="100%" stop-color="#07060F" stop-opacity="0.55"/>
  </radialGradient>
  <filter id="blur3" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
  <filter id="blur8" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="8"/>
  </filter>
  <filter id="blur12" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="14"/>
  </filter>
  <filter id="steamBlur" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.4"/>
  </filter>
  <clipPath id="headClip">
    <ellipse cx="{CX}" cy="{HEAD_CY}" rx="{HEAD_RX}" ry="{HEAD_RY}"/>
  </clipPath>
</defs>
"""


def build():
    # Precompute tentacles once.
    specs = tentacle_specs()
    geos = {}
    for spec in specs:
        geos[spec["name"]] = (spec, *tentacle_geometry(spec))

    def arm(name, t0=0.0, t1=1.0):
        spec, center, norms = geos[name]
        return draw_tentacle(spec, center, norms, t0, t1)

    def tip(name):
        spec = geos[name][0]
        return end_pose(spec["points"])

    parts = []
    parts.append(background())
    parts.append(stall_shell())
    parts.append(shelf_and_sign())
    parts.append(chef_body())
    parts.append(chef_head())
    parts.append(toque())

    # Pot sits on the back-left of the counter, but is drawn after the counter
    # so its base reads as resting on the wood. Chef is already behind the counter.
    parts.append(counter())

    # ---- pot, paddle, ladle arm ----
    pot_cx, pot_rim, pot_rx, pot_ry = 548, 676, 104, 38
    parts.append(pot(pot_cx, pot_rim, pot_rx, pot_ry, body_h=112))
    # stir arm then paddle so the handle meets the tip
    parts.append(arm("stir"))
    sx, sy, sang = tip("stir")
    parts.append(paddle((sx, sy), (pot_cx + 6, pot_rim + 4), sang))
    parts.append(arm("ladle"))
    lx, ly, lang = tip("ladle")
    ladle_svg, _cup = ladle((lx, ly), lang, length=64)
    parts.append(ladle_svg)

    # cutting board between pot and the noodle bowl
    parts.append(cutting_board(612, 778))

    # ---- working bowls, set apart so each arm has a clear target ----
    b1 = (800, 804)
    b2 = (1172, 812)
    parts.append(bowl(b1[0], b1[1], 0.94, {"lift", "nori", "scallion", "naruto"}, "broth1", variant="cream")[0])
    parts.append(bowl(b2[0], b2[1], 0.94, {"chashu", "menma", "scallion"}, "broth2", variant="red")[0])

    # resting arm on the front-left of the counter, suckers up
    parts.append(arm("rest"))

    parts.append(arm("chops"))
    chop_svg, norigin = chopsticks(tip("chops")[:2], tip("chops")[2], length=70)
    parts.append(chop_svg)
    parts.append(hanging_noodles(norigin, (b1[0] + 4, b1[1] + 8), n=5))

    parts.append(arm("egg"))
    ex, ey, _ea = tip("egg")
    parts.append(egg_half(ex + 2, ey + 6, 1.25))

    parts.append(arm("scallion"))
    scx, scy, _sa = tip("scallion")
    parts.append(falling_scallions(scx, scy, b2[0] + 24, b2[1] - 8))

    parts.append(arm("cloth"))
    cx, cy, ca = tip("cloth")
    parts.append(cloth(cx + 4, cy + 2, rot=ca * 0.35))

    parts.append(water_glass(1390, 882))

    # ---- hero bowl, cradled. The arm passes behind the bowl, then the tip curls up in front. ----
    parts.append(arm("cradle", 0.0, 0.74))
    hero = (1030, 992)
    parts.append(bowl(hero[0], hero[1], 1.28,
                      {"nori", "menma", "chashu", "egg", "naruto", "scallion"},
                      "brothH", variant="cream")[0])
    parts.append(arm("cradle", 0.66, 1.0))

    # steam — in front, so it drifts over the food
    parts.append(steam_wisps(pot_cx, pot_rim - 10, scale=1.35, n=5, seed=1))
    parts.append(steam_wisps(b1[0], b1[1] - 36, scale=0.9, n=3, seed=3))
    parts.append(steam_wisps(b2[0] + 10, b2[1] - 34, scale=0.85, n=3, seed=5))
    parts.append(steam_wisps(hero[0] - 10, hero[1] - 48, scale=1.15, n=4, seed=2))

    # noren and lanterns in front of the stall opening
    parts.append(noren())
    parts.append(lantern(118, 318))
    parts.append(lantern(1492, 324))

    # vignette
    parts.append(rect(0, 0, W, H, fill="url(#vig)"))
    return "\n".join(parts)


def main():
    body = build()
    doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>Octopus chef at a ramen booth</title>
  <desc>An octopus in a white toque and chef's coat works a nighttime ramen yatai. Eight tentacles stir a stockpot, ladle broth, lift noodles, lay nori, set an egg, scatter scallions, hold a towel, and cradle a finished bowl. Noren curtains read ラーメン, and a wooden sign reads 営業中.</desc>
  {DEFS}
  {body}
</svg>
'''
    out = ROOT / "output" / "octopus-chef-ramen-booth.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
