#!/usr/bin/env python3
"""Octopus chef at a night-time ramen yatai — procedural SVG illustration.

Run from the project root:
    python3 src/make_octopus_ramen.py
Writes output/octopus_ramen_chef.svg (standard library only).
"""
import math
import os
import random

W, H = 1600, 1200
rng = random.Random(11)
svg = []


def add(*items):
    for it in items:
        if isinstance(it, (list, tuple)):
            svg.extend(it)
        else:
            svg.append(it)


def d_of(pts, close=True):
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + (" Z" if close else "")


# ---------------------------------------------------------------- geometry
def catmull(ctrl, samples=20):
    ctrl = [tuple(p) for p in ctrl]
    if len(ctrl) == 2:
        (x0, y0), (x1, y1) = ctrl
        return [(x0 + (x1 - x0) * i / samples, y0 + (y1 - y0) * i / samples) for i in range(samples + 1)]
    q = ([(2 * ctrl[0][0] - ctrl[1][0], 2 * ctrl[0][1] - ctrl[1][1])] + ctrl +
         [(2 * ctrl[-1][0] - ctrl[-2][0], 2 * ctrl[-1][1] - ctrl[-2][1])])
    res = []
    for i in range(len(ctrl) - 1):
        p0, p1, p2, p3 = q[i:i + 4]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            res.append(tuple(
                0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 +
                       (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    res.append(ctrl[-1])
    return res


def resample(poly, n):
    d = [0.0]
    for a, b in zip(poly, poly[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = d[-1]
    res, j = [], 0
    for k in range(n):
        s = total * k / (n - 1)
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        seg = (d[j + 1] - d[j]) or 1e-9
        u = (s - d[j]) / seg
        a, b = poly[j], poly[j + 1]
        res.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return res, total


def frames(pts):
    tans, nors = [], []
    n = len(pts)
    for i in range(n):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        tans.append((dx / ln, dy / ln))
        nors.append((-dy / ln, dx / ln))
    return tans, nors


def strip(pts, nors, wd, oa, ob, i0, i1):
    a = [(pts[i][0] + nors[i][0] * wd[i] * oa, pts[i][1] + nors[i][1] * wd[i] * oa) for i in range(i0, i1 + 1)]
    b = [(pts[i][0] + nors[i][0] * wd[i] * ob, pts[i][1] + nors[i][1] * wd[i] * ob) for i in range(i0, i1 + 1)]
    return a + b[::-1]


def rot(p, c, deg):
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def cap_arc(p, t, nn, r, steps=10, sign=1):
    pts = []
    for k in range(1, steps):
        a = math.pi * k / steps
        pts.append((p[0] + (nn[0] * math.cos(a) * sign + t[0] * math.sin(a) * sign) * r,
                    p[1] + (nn[1] * math.cos(a) * sign + t[1] * math.sin(a) * sign) * r))
    return pts


def ribbon_shape(ctrl, w0, w1, n=48, power=0.8, samples=14, round_start=True):
    """Closed tapered stroke polygon with rounded ends (brush strokes, steam, noodles)."""
    pts, _ = resample(catmull(ctrl, samples), n)
    tans, nors = frames(pts)
    wd = [w1 + (w0 - w1) * (1 - i / (n - 1)) ** power for i in range(n)]
    left = [(p[0] + q[0] * w / 2, p[1] + q[1] * w / 2) for p, q, w in zip(pts, nors, wd)]
    right = [(p[0] - q[0] * w / 2, p[1] - q[1] * w / 2) for p, q, w in zip(pts, nors, wd)]
    end = cap_arc(pts[-1], tans[-1], nors[-1], wd[-1] / 2)
    start = []
    if round_start:
        t0, n0 = tans[0], nors[0]
        start = cap_arc(pts[0], (-t0[0], -t0[1]), (-n0[0], -n0[1]), wd[0] / 2)
    return d_of(left + end + right[::-1] + start)


# ---------------------------------------------------------------- palette
OCTO = dict(body="#ec6650", under="#f8ad93", dark="#a3313a", light="#ffb59b", line="#5c1b29",
            sucker="#ffe4d2", ring="#d8776b", inner="#efa08d", sw=3.2)


def tentacle(ctrl, w0, w1, side=1, t0=0.0, t1=1.0, tip=True, n=170, power=0.85, sucker_from=0.08, pal=OCTO, dense=None):
    pts, total = resample(dense if dense else catmull(ctrl), n)
    tans, nors = frames(pts)
    wd = [w1 + (w0 - w1) * (1 - i / (n - 1)) ** power for i in range(n)]
    i0, i1 = int(round(t0 * (n - 1))), int(round(t1 * (n - 1)))
    full_tip = tip and i1 == n - 1
    left = [(pts[i][0] + nors[i][0] * wd[i] / 2, pts[i][1] + nors[i][1] * wd[i] / 2) for i in range(i0, i1 + 1)]
    right = [(pts[i][0] - nors[i][0] * wd[i] / 2, pts[i][1] - nors[i][1] * wd[i] / 2) for i in range(i0, i1 + 1)]
    cap = cap_arc(pts[-1], tans[-1], nors[-1], wd[-1] / 2, 12) if full_tip else []
    out = [f'<path d="{d_of(left + cap + right[::-1])}" fill="{pal["body"]}"/>']
    s = side
    ua, ub = sorted((s * 0.03, s * 0.5))
    out.append(f'<path d="{d_of(strip(pts, nors, wd, ua, ub, i0, i1))}" fill="{pal["under"]}"/>')
    da, db = sorted((-s * 0.5, -s * 0.32))
    out.append(f'<path d="{d_of(strip(pts, nors, wd, da, db, i0, i1))}" fill="{pal["dark"]}" opacity="0.42"/>')
    j1 = min(i1, int(0.9 * (n - 1)))
    if j1 > i0 + 1:
        ha, hb = sorted((-s * 0.27, -s * 0.15))
        out.append(f'<path d="{d_of(strip(pts, nors, wd, ha, hb, i0, j1))}" fill="{pal["light"]}" opacity="0.8"/>')
    # suckers keep the same spacing whichever sub-range is drawn, so redrawn segments line up
    sp, s_lo, se = sucker_from * total, t0 * total, min(t1, 0.95) * total
    while sp < se:
        i = int(round(sp / total * (n - 1)))
        w = wd[i]
        r = 0.15 * w
        if r < 1.2:
            break
        if sp < s_lo:
            sp += 2.35 * r
            continue
        p, q, t = pts[i], nors[i], tans[i]
        cx, cy = p[0] + q[0] * w * 0.27 * s, p[1] + q[1] * w * 0.27 * s
        ang = math.degrees(math.atan2(t[1], t[0]))
        out.append(
            f'<g transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.8:.1f}" fill="{pal["sucker"]}" '
            f'stroke="{pal["ring"]}" stroke-width="{max(0.7, r * 0.22):.1f}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 0.42:.1f}" ry="{r * 0.32:.1f}" fill="{pal["inner"]}"/></g>')
        sp += 2.35 * r
    line = f'fill="none" stroke="{pal["line"]}" stroke-width="{pal["sw"]}" stroke-linecap="round" stroke-linejoin="round"'
    if full_tip:
        out.append(f'<path d="{d_of(left + cap + right[::-1], False)}" {line}/>')
    else:
        out.append(f'<path d="{d_of(left, False)}" {line}/>')
        out.append(f'<path d="{d_of(right, False)}" {line}/>')
    return out


def t_at_y(ctrl, y, n=170):
    pts, _ = resample(catmull(ctrl), n)
    for i, p in enumerate(pts):
        if p[1] >= y:
            return i / (n - 1)
    return 1.0


class GripArm:
    """An arm whose tip spirals round a handle h0->h1. Draw .back() before the handle and .front() after it."""

    def __init__(self, ctrl, h0, h1, at, rod, w0, w1=4.0, turns=1.3, theta0=0.3, side=1, power=1.0,
                 n=280, wrap_w=13.0, tilt=0.25):
        dx, dy = h1[0] - h0[0], h1[1] - h0[1]
        ln = math.hypot(dx, dy)
        d = (dx / ln, dy / ln)
        m = (-d[1], d[0])
        base = (h0[0] + dx * at, h0[1] + dy * at)
        last = ctrl[-1]
        if (last[0] - base[0]) * m[0] + (last[1] - base[1]) * m[1] < 0:
            m = (-m[0], -m[1])          # +m is the side the arm arrives from
        radius = rod / 2 + wrap_w * 0.55
        # pitch large enough that the projected turning points stay rounder than the arm is wide
        pitch = 2 * math.pi * math.sqrt(radius * wrap_w / 2) * 1.3

        def helix_at(th):
            along = pitch * (th - theta0) / (2 * math.pi) - pitch * turns * 0.5 + tilt * radius * math.sin(th)
            return (base[0] + d[0] * along + m[0] * radius * math.cos(th),
                    base[1] + d[1] * along + m[1] * radius * math.cos(th))

        k_max = 140
        ths = [theta0 + 2 * math.pi * turns * k / (k_max - 1) for k in range(k_max)]
        helix = [helix_at(th) for th in ths]
        hdepth = [math.sin(th) for th in ths]
        approach = catmull(ctrl)
        # tangent-matched cubic bridge from the arm into the coil
        ta = (approach[-1][0] - approach[-3][0], approach[-1][1] - approach[-3][1])
        th_ = (helix[1][0] - helix[0][0], helix[1][1] - helix[0][1])
        ta = (ta[0] / math.hypot(*ta), ta[1] / math.hypot(*ta))
        th_ = (th_[0] / math.hypot(*th_), th_[1] / math.hypot(*th_))
        p0, p3 = approach[-1], helix[0]
        span = math.hypot(p3[0] - p0[0], p3[1] - p0[1]) * 0.5
        p1 = (p0[0] + ta[0] * span, p0[1] + ta[1] * span)
        p2 = (p3[0] - th_[0] * span, p3[1] - th_[1] * span)
        bridge = []
        for k in range(1, 30):
            t = k / 30
            u = 1 - t
            bridge.append(tuple(u ** 3 * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1)))
        self.dense = approach + bridge + helix
        dense_depth = [-1.0] * (len(approach) + len(bridge)) + hdepth
        cum = [0.0]
        for a_, b_ in zip(self.dense, self.dense[1:]):
            cum.append(cum[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
        total = cum[-1]
        self.n = n
        stations, j = [], 0
        for i in range(n):
            sv = total * i / (n - 1)
            while j < len(cum) - 2 and cum[j + 1] < sv:
                j += 1
            stations.append(dense_depth[j])
        self.runs, start = [], None
        for i, dv in enumerate(stations):
            if dv > 0.2 and start is None:
                start = i
            if (dv <= 0.2 or i == n - 1) and start is not None:
                self.runs.append((start, i))
                start = None
        self.kw = dict(side=side, power=power, n=n)
        self.w0, self.w1 = w0, w1

    def back(self):
        return tentacle(None, self.w0, self.w1, dense=self.dense, **self.kw)

    def front(self):
        out = []
        for i0, i1 in self.runs:
            out += tentacle(None, self.w0, self.w1, dense=self.dense, t0=i0 / (self.n - 1),
                            t1=i1 / (self.n - 1), **self.kw)
        return out


# ---------------------------------------------------------------- defs
HEAD = ("M 800 350 C 908 350 970 424 968 506 C 966 572 940 612 918 640 C 904 660 892 676 884 700 "
        "L 716 700 C 708 676 696 660 682 640 C 660 612 634 572 632 506 C 630 424 692 350 800 350 Z")

ROOF_EAVE_L, ROOF_EAVE_R, RIDGE_Y = 150, 1450, 100


def eave_y(x):
    u = (x - 800) / 650.0
    return 213 - 27 * u * u


ROOF = (f"M 300 {RIDGE_Y} L 1300 {RIDGE_Y} L {ROOF_EAVE_R} {eave_y(ROOF_EAVE_R):.1f} "
        f"Q 800 240 {ROOF_EAVE_L} {eave_y(ROOF_EAVE_L):.1f} Z")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<title>Octopus chef at a ramen yatai</title>',
    f'''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f2e"/><stop offset="0.55" stop-color="#1f2353"/><stop offset="1" stop-color="#48396b"/></linearGradient>
<radialGradient id="moonGlow"><stop offset="0" stop-color="#fff3c8" stop-opacity="0.5"/><stop offset="0.3" stop-color="#d9d0ff" stop-opacity="0.16"/><stop offset="1" stop-color="#d9d0ff" stop-opacity="0"/></radialGradient>
<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2b46"/><stop offset="1" stop-color="#121327"/></linearGradient>
<radialGradient id="wall" gradientUnits="userSpaceOnUse" cx="800" cy="520" r="640"><stop offset="0" stop-color="#9c5f37"/><stop offset="0.5" stop-color="#6e3d23"/><stop offset="1" stop-color="#3a1f12"/></radialGradient>
<radialGradient id="warm"><stop offset="0" stop-color="#ffd08a" stop-opacity="0.55"/><stop offset="1" stop-color="#ffd08a" stop-opacity="0"/></radialGradient>
<radialGradient id="lanternGlow"><stop offset="0" stop-color="#ff9050" stop-opacity="0.6"/><stop offset="0.35" stop-color="#ff5a3a" stop-opacity="0.2"/><stop offset="1" stop-color="#ff5a3a" stop-opacity="0"/></radialGradient>
<radialGradient id="lanternBody" cx="0.4" cy="0.42" r="0.68"><stop offset="0" stop-color="#ffc184"/><stop offset="0.4" stop-color="#f2533a"/><stop offset="1" stop-color="#8a171b"/></radialGradient>
<radialGradient id="head" gradientUnits="userSpaceOnUse" cx="742" cy="420" r="330"><stop offset="0" stop-color="#ffa586"/><stop offset="0.45" stop-color="#ef6b53"/><stop offset="1" stop-color="#b13c3d"/></radialGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4b525d"/><stop offset="0.14" stop-color="#8e98a3"/><stop offset="0.32" stop-color="#e6ebef"/><stop offset="0.45" stop-color="#b5bec7"/><stop offset="0.78" stop-color="#78818c"/><stop offset="1" stop-color="#3f4550"/></linearGradient>
<linearGradient id="steelDark" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a4049"/><stop offset="0.35" stop-color="#9aa4ae"/><stop offset="1" stop-color="#3a4049"/></linearGradient>
<linearGradient id="bowlBody" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c7bdad"/><stop offset="0.3" stop-color="#fffdf8"/><stop offset="0.55" stop-color="#f3eee4"/><stop offset="1" stop-color="#ada392"/></linearGradient>
<linearGradient id="bowlInside" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9b0a2"/><stop offset="1" stop-color="#fbf7ef"/></linearGradient>
<radialGradient id="broth" cx="0.45" cy="0.45" r="0.65"><stop offset="0" stop-color="#f6d9a2"/><stop offset="0.6" stop-color="#e5b46f"/><stop offset="1" stop-color="#c58640"/></radialGradient>
<radialGradient id="stock" cx="0.42" cy="0.45" r="0.7"><stop offset="0" stop-color="#f2d29a"/><stop offset="0.65" stop-color="#d79d55"/><stop offset="1" stop-color="#a86a2c"/></radialGradient>
<radialGradient id="water" cx="0.45" cy="0.45" r="0.7"><stop offset="0" stop-color="#e9f1f4"/><stop offset="0.7" stop-color="#b6c6cf"/><stop offset="1" stop-color="#8396a2"/></radialGradient>
<linearGradient id="steam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset="0.15" stop-color="#ffffff" stop-opacity="0.55"/><stop offset="0.6" stop-color="#ffffff" stop-opacity="0.22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
<linearGradient id="counterTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9824d"/><stop offset="1" stop-color="#dcaa6e"/></linearGradient>
<linearGradient id="counterEdge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c48a52"/><stop offset="1" stop-color="#8e5730"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f2213"/><stop offset="0.12" stop-color="#6b3a20"/><stop offset="1" stop-color="#4f2a17"/></linearGradient>
<linearGradient id="post" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3b1f12"/><stop offset="0.45" stop-color="#7b4529"/><stop offset="1" stop-color="#3b1f12"/></linearGradient>
<linearGradient id="noren" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c3d7c"/><stop offset="1" stop-color="#1a2552"/></linearGradient>
<linearGradient id="norenFold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.28"/><stop offset="0.18" stop-color="#fff" stop-opacity="0.06"/><stop offset="0.5" stop-color="#000" stop-opacity="0"/><stop offset="0.8" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#000" stop-opacity="0.3"/></linearGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#262a42"/><stop offset="1" stop-color="#4b5273"/></linearGradient>
<linearGradient id="stool" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a5732"/><stop offset="0.4" stop-color="#c99560"/><stop offset="1" stop-color="#7a4a2a"/></linearGradient>
<radialGradient id="yolk" cx="0.45" cy="0.4" r="0.6"><stop offset="0" stop-color="#ffc24a"/><stop offset="1" stop-color="#ec7618"/></radialGradient>
<radialGradient id="vignette" gradientUnits="userSpaceOnUse" cx="800" cy="620" r="1020"><stop offset="0.55" stop-color="#05061a" stop-opacity="0"/><stop offset="1" stop-color="#05061a" stop-opacity="0.6"/></radialGradient>
<filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="blur5" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="blur9" x="-60%" y="-30%" width="220%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="blur18" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>
<pattern id="mesh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0 H6 M0 0 V6" stroke="#dfe5ea" stroke-width="1" fill="none"/></pattern>
<clipPath id="headClip"><path d="{HEAD}"/></clipPath>
<clipPath id="roofClip"><path d="{ROOF}"/></clipPath>
<clipPath id="stallClip"><rect x="290" y="232" width="1020" height="520"/></clipPath>
</defs>''')

# ---------------------------------------------------------------- sky & city
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
for _ in range(110):
    x, y = rng.uniform(0, W), rng.uniform(0, 430) ** 1.0
    r = rng.choice([0.7, 0.9, 1.1, 1.4, 1.8])
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff8e6" opacity="{rng.uniform(0.35, 0.95):.2f}"/>')
for x, y in [(90, 60), (560, 40), (1210, 30), (1580, 300), (30, 330)]:
    add(f'<path d="M{x - 7} {y} L{x + 7} {y} M{x} {y - 7} L{x} {y + 7}" stroke="#fff8e6" stroke-width="1.3" '
        f'stroke-linecap="round" opacity="0.8"/>', f'<circle cx="{x}" cy="{y}" r="1.8" fill="#fff"/>')

# moon
add('<circle cx="1440" cy="76" r="170" fill="url(#moonGlow)"/>',
    '<circle cx="1440" cy="76" r="40" fill="#fff1c6"/>',
    '<circle cx="1452" cy="70" r="40" fill="#1f2353" opacity="0.0"/>',
    '<circle cx="1428" cy="66" r="7" fill="#efdca8" opacity="0.7"/>',
    '<circle cx="1452" cy="90" r="9" fill="#efdca8" opacity="0.6"/>',
    '<circle cx="1458" cy="62" r="4" fill="#efdca8" opacity="0.6"/>')

# far skyline
far = []
x = -10
while x < W + 10:
    w = rng.randint(50, 120)
    far.append((x, rng.randint(150, 290), w))
    x += w - 4
for x, top, w in far:
    add(f'<rect x="{x}" y="{top}" width="{w}" height="{1010 - top}" fill="#262957"/>')
    for wy in range(top + 14, 1000, 22):
        for wx in range(x + 8, x + w - 8, 14):
            if rng.random() < 0.18:
                add(f'<rect x="{wx}" y="{wy}" width="6" height="9" fill="#f4c97a" opacity="{rng.uniform(0.25, 0.55):.2f}"/>')


def building(x, top, w, color, lit=0.35):
    out = [f'<rect x="{x}" y="{top}" width="{w}" height="{1010 - top}" fill="{color}"/>',
           f'<rect x="{x}" y="{top}" width="{w}" height="5" fill="#ffffff" opacity="0.06"/>']
    cols = max(1, int((w - 14) // 20))
    gx = x + (w - cols * 20 + 8) / 2
    for wy in range(top + 22, 990, 30):
        for c in range(cols):
            wx = gx + c * 20
            if rng.random() < lit:
                out.append(f'<rect x="{wx:.1f}" y="{wy}" width="12" height="16" fill="#ffd27f" '
                           f'opacity="{rng.uniform(0.55, 0.95):.2f}"/>')
            else:
                out.append(f'<rect x="{wx:.1f}" y="{wy}" width="12" height="16" fill="#2f3466" opacity="0.8"/>')
    return out


add(building(-10, 330, 130, "#191c3e"), building(105, 240, 110, "#1d2147"), building(200, 380, 90, "#161937"))
add(building(1310, 300, 100, "#1a1d40"), building(1400, 225, 120, "#1d2148", 0.3), building(1505, 360, 110, "#171a39"))


GLYPHS = {
    "A": [[(0.12, 0.34), (0.88, 0.32)], [(0.5, 0.04), (0.5, 0.96)], [(0.47, 0.4), (0.14, 0.82)], [(0.53, 0.4), (0.9, 0.8)]],
    "B": [[(0.2, 0.18), (0.2, 0.86)], [(0.2, 0.18), (0.8, 0.18), (0.8, 0.86)], [(0.2, 0.52), (0.8, 0.52)], [(0.2, 0.86), (0.8, 0.86)]],
    "C": [[(0.2, 0.16), (0.8, 0.14)], [(0.28, 0.5), (0.72, 0.5)], [(0.08, 0.86), (0.92, 0.84)], [(0.5, 0.16), (0.5, 0.84)]],
    "E": [[(0.08, 0.46), (0.92, 0.44)], [(0.5, 0.08), (0.5, 0.94)], [(0.22, 0.12), (0.32, 0.26)], [(0.8, 0.12), (0.7, 0.26)], [(0.18, 0.7), (0.34, 0.86)]],
    "F": [[(0.1, 0.36), (0.9, 0.34)], [(0.52, 0.05), (0.46, 0.4), (0.12, 0.92)], [(0.5, 0.42), (0.92, 0.92)]],
    "G": [[(0.5, 0.04), (0.5, 0.82), (0.4, 0.74)], [(0.22, 0.34), (0.1, 0.7)], [(0.78, 0.34), (0.92, 0.7)]],
    "H": [[(0.14, 0.12), (0.14, 0.92)], [(0.14, 0.12), (0.86, 0.12), (0.86, 0.92), (0.76, 0.86)], [(0.36, 0.36), (0.64, 0.36)], [(0.36, 0.6), (0.64, 0.6)]],
    "I": [[(0.16, 0.2), (0.84, 0.2)], [(0.5, 0.2), (0.5, 0.94)], [(0.2, 0.56), (0.8, 0.56)], [(0.08, 0.94), (0.92, 0.94)]],
    "J": [[(0.3, 0.08), (0.7, 0.08)], [(0.12, 0.3), (0.88, 0.3)], [(0.24, 0.48), (0.24, 0.9)], [(0.24, 0.48), (0.76, 0.48), (0.76, 0.9)], [(0.24, 0.9), (0.76, 0.9)]],
}
RADICALS = [
    [[(0.3, 0.05), (0.06, 0.45)], [(0.2, 0.32), (0.2, 0.96)]],
    [[(0.06, 0.1), (0.2, 0.2)], [(0.03, 0.42), (0.18, 0.52)], [(0.05, 0.94), (0.26, 0.64)]],
    [[(0.04, 0.3), (0.04, 0.72)], [(0.04, 0.3), (0.3, 0.3), (0.3, 0.72)], [(0.04, 0.72), (0.3, 0.72)]],
    [[(0.02, 0.32), (0.34, 0.3)], [(0.19, 0.05), (0.19, 0.94), (0.1, 0.88)], [(0.03, 0.74), (0.34, 0.56)]],
    [[(0.04, 0.3), (0.34, 0.28)], [(0.19, 0.04), (0.19, 0.96)], [(0.17, 0.36), (0.02, 0.7)], [(0.21, 0.4), (0.33, 0.56)]],
]


def glyph(x, y, s, color, sw=2.0, kind=None):
    jit = lambda: rng.uniform(-0.035, 0.035) * s
    strokes = []
    if kind is None and rng.random() < 0.55:
        strokes += RADICALS[rng.randrange(len(RADICALS))]
        right = GLYPHS[rng.choice("ABCEFGHIJ")]
        strokes += [[(0.42 + px * 0.56, py) for px, py in st] for st in right]
    else:
        strokes = GLYPHS[kind or rng.choice("ABCEFGHIJ")]
    out = []
    for st in strokes:
        pts = [(x + px * s + jit(), y + py * s + jit()) for px, py in st]
        out.append(f'<path d="{d_of(pts, False)}" fill="none" stroke="{color}" stroke-width="{sw}" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
    return out


# neon signs
neon_l = []
neon_l.append('<rect x="40" y="268" width="52" height="236" rx="6" fill="#16122b" stroke="#ff5fa8" stroke-width="3"/>')
for k in range(5):
    neon_l += glyph(52, 282 + k * 44, 28, "#ffd1ea", 3.0)
add('<g opacity="0.85"><g filter="url(#blur5)">', [s.replace('#ffd1ea', '#ff4fa0') for s in neon_l], '</g>', neon_l, '</g>')
neon_r = ['<rect x="1418" y="420" width="96" height="44" rx="6" fill="#0f1a2b" stroke="#53e6ff" stroke-width="3"/>']
for k in range(3):
    neon_r += glyph(1428 + k * 28, 428, 26, "#c9f8ff", 2.8)
add('<g opacity="0.8"><g filter="url(#blur5)">', [s.replace('#c9f8ff', '#40dcff') for s in neon_r], '</g>', neon_r, '</g>')

# utility pole and wires
add('<g stroke="#0c0d1e" fill="none" stroke-linecap="round">',
    '<path d="M1490 98 Q 900 230 -20 120" stroke-width="2.2"/>',
    '<path d="M1566 98 Q 1590 110 1620 108" stroke-width="2.2"/>',
    '<path d="M1496 134 Q 900 300 -20 190" stroke-width="2"/>',
    '<path d="M1560 134 Q 1590 150 1620 150" stroke-width="2"/>',
    '<path d="M1528 210 Q 1440 330 1420 420" stroke-width="1.6"/>',
    '</g>',
    '<rect x="1520" y="-10" width="17" height="1022" fill="#0e1024"/>',
    '<rect x="1482" y="94" width="92" height="9" fill="#0e1024"/>',
    '<rect x="1488" y="130" width="80" height="8" fill="#0e1024"/>',
    '<rect x="1532" y="196" width="30" height="46" rx="5" fill="#141731"/>',
    '<circle cx="1492" cy="90" r="4" fill="#3d4266"/><circle cx="1566" cy="90" r="4" fill="#3d4266"/>',
    '<rect x="1520" y="-10" width="4" height="1022" fill="#ffffff" opacity="0.05"/>')

# ---------------------------------------------------------------- street
add('<rect x="0" y="1004" width="1600" height="196" fill="url(#ground)"/>',
    '<rect x="0" y="1004" width="1600" height="3" fill="#000" opacity="0.35"/>',
    '<ellipse cx="800" cy="1060" rx="700" ry="80" fill="#ffb060" opacity="0.18" filter="url(#blur18)"/>',
    '<ellipse cx="214" cy="1090" rx="34" ry="70" fill="#ff5a3a" opacity="0.2" filter="url(#blur9)"/>',
    '<ellipse cx="1386" cy="1090" rx="34" ry="70" fill="#ff5a3a" opacity="0.2" filter="url(#blur9)"/>',
    '<ellipse cx="66" cy="1080" rx="18" ry="60" fill="#ff4fa0" opacity="0.25" filter="url(#blur9)"/>',
    '<ellipse cx="1466" cy="1070" rx="40" ry="30" fill="#40dcff" opacity="0.15" filter="url(#blur9)"/>')
for k in range(14):
    y = rng.uniform(1030, 1190)
    x = rng.uniform(0, 1600)
    add(f'<path d="M{x:.0f} {y:.0f} h{rng.uniform(30, 110):.0f}" stroke="#8f8fc0" stroke-width="1.4" '
        f'stroke-linecap="round" opacity="{rng.uniform(0.08, 0.2):.2f}"/>')
add('<rect x="230" y="988" width="1140" height="26" fill="#000" opacity="0.45" filter="url(#blur5)"/>')

def puddle(cx, cy, rx, ry, reflections):
    pid = f"pud{cx}"
    o = [f'<clipPath id="{pid}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#2e3160"/>',
         f'<g clip-path="url(#{pid})">']
    for x, color, w, op in reflections:
        o.append(f'<ellipse cx="{x}" cy="{cy}" rx="{w}" ry="{ry * 1.6:.0f}" fill="{color}" opacity="{op}" filter="url(#blur5)"/>')
    for k in range(3):
        y = cy - ry * 0.4 + k * ry * 0.4
        o.append(f'<path d="M{cx - rx * 0.6:.0f} {y:.0f} h{rx * (0.5 + 0.3 * k):.0f}" stroke="#c9cbf2" stroke-width="1.2" opacity="0.25"/>')
    o.append('</g>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#8b8fd0" stroke-width="1.4" opacity="0.35"/>')
    return o


add(puddle(250, 1124, 150, 20, [(214, "#ff6a40", 30, 0.75), (300, "#ffb060", 60, 0.25), (66, "#ff4fa0", 20, 0.5)]))
add(puddle(1340, 1152, 175, 24, [(1386, "#ff6a40", 32, 0.75), (1466, "#40dcff", 34, 0.5), (1250, "#ffb060", 60, 0.25)]))
add(puddle(790, 1176, 110, 12, [(800, "#ffc078", 70, 0.4)]))

# ---------------------------------------------------------------- stall interior
add('<rect x="290" y="232" width="1020" height="520" fill="url(#wall)"/>')
add('<g clip-path="url(#stallClip)">')
for y in range(262, 760, 36):
    add(f'<path d="M290 {y} H1310" stroke="#3b2013" stroke-width="2" opacity="0.55"/>',
        f'<path d="M290 {y + 2} H1310" stroke="#c98a55" stroke-width="1" opacity="0.18"/>')
for x, y in [(380, 510), (1230, 620), (520, 690), (1100, 400), (880, 300)]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="11" ry="4" fill="none" stroke="#3b2013" stroke-width="1.5" opacity="0.5"/>')
add('</g>')

# menu plaques
add('<rect x="306" y="350" width="296" height="6" rx="2" fill="#2e180c"/>',
    '<rect x="998" y="350" width="296" height="6" rx="2" fill="#2e180c"/>')
prices = ["850", "950", "1100", "780", "300", "500", "880", "1000", "650", "250", "400", "920"]
k = 0
for gx in (314, 1006):
    for j in range(6):
        x = gx + j * 47
        add(f'<rect x="{x + 2}" y="358" width="40" height="98" rx="2" fill="#000" opacity="0.35"/>',
            f'<rect x="{x}" y="354" width="40" height="98" rx="2" fill="#dcb98a" stroke="#8a6a44" stroke-width="1.2"/>',
            f'<rect x="{x}" y="354" width="40" height="6" fill="#b48e5e" opacity="0.6"/>')
        for g in range(3):
            add(glyph(x + 10, 366 + g * 23, 20, "#2a1a10", 2.4))
        add(f'<text x="{x + 20}" y="447" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="11" font-weight="bold" fill="#b8251f">{prices[k]}</text>')
        k += 1

add('<rect x="262" y="226" width="28" height="530" fill="url(#post)"/>',
    '<rect x="1310" y="226" width="28" height="530" fill="url(#post)"/>')
add('<ellipse cx="800" cy="360" rx="520" ry="300" fill="url(#warm)"/>')
add('<rect x="290" y="232" width="1020" height="40" fill="#1a0c06" opacity="0.45" filter="url(#blur9)"/>')


# ---------------------------------------------------------------- pots
def pot(cx, rim_y, rx, ry, depth, contents, liquid_grad):
    left, right = cx - rx, cx + rx
    bot = rim_y + depth
    out = [f'<path d="M{left} {rim_y} L{left} {bot} L{right} {bot} L{right} {rim_y} '
           f'A{rx} {ry} 0 0 1 {left} {rim_y} Z" fill="url(#steel)"/>']
    for by in (rim_y + 34, rim_y + depth - 40):
        out.append(f'<path d="M{left} {by} A{rx} {ry} 0 0 0 {right} {by}" fill="none" stroke="#5a616b" stroke-width="2.4"/>')
        out.append(f'<path d="M{left} {by + 3} A{rx} {ry} 0 0 0 {right} {by + 3}" fill="none" stroke="#f2f5f7" '
                   f'stroke-width="1.2" opacity="0.6"/>')
    for sx in (-1, 1):
        hx = cx + sx * (rx + 2)
        out.append(f'<path d="M{hx} {rim_y + 20} q{sx * 22} 2 {sx * 20} 22 q-2 12 {-sx * 20} 12" fill="none" '
                   f'stroke="#6f7883" stroke-width="7" stroke-linecap="round"/>')
        out.append(f'<path d="M{hx} {rim_y + 20} q{sx * 22} 2 {sx * 20} 22" fill="none" stroke="#d5dbe0" '
                   f'stroke-width="2" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<ellipse cx="{cx}" cy="{rim_y}" rx="{rx}" ry="{ry}" fill="#2f343b"/>')
    out.append(f'<ellipse cx="{cx}" cy="{rim_y + 4}" rx="{rx - 9}" ry="{ry - 5}" fill="url(#{liquid_grad})"/>')
    out += contents
    out.append(f'<ellipse cx="{cx}" cy="{rim_y}" rx="{rx}" ry="{ry}" fill="none" stroke="#eef2f5" stroke-width="4.5"/>')
    out.append(f'<ellipse cx="{cx}" cy="{rim_y}" rx="{rx + 2.5}" ry="{ry + 2.5}" fill="none" stroke="#4b525c" stroke-width="1.5"/>')
    return out


bubbles = []
for _ in range(26):
    a = rng.uniform(0, 2 * math.pi)
    rr = math.sqrt(rng.random())
    bx, by = 468 + math.cos(a) * 106 * rr, 626 + math.sin(a) * 16 * rr
    br = rng.uniform(2, 6)
    bubbles.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{br:.1f}" ry="{br * 0.6:.1f}" fill="#ffffff" '
                   f'fill-opacity="0.35" stroke="#ffffff" stroke-width="1" opacity="0.85"/>')
bubbles.append('<path d="M360 616 L338 520" stroke="#5b3a22" stroke-width="8" stroke-linecap="round"/>')
bubbles.append('<path d="M360 616 L338 520" stroke="#a7774c" stroke-width="2.5" stroke-linecap="round" transform="translate(-2 0)"/>')
add(pot(468, 622, 128, 24, 150, bubbles, "water"))

stock_bits = []
for _ in range(16):
    a = rng.uniform(0, 2 * math.pi)
    rr = math.sqrt(rng.random())
    bx, by = 1160 + math.cos(a) * 96 * rr, 570 + math.sin(a) * 14 * rr
    br = rng.uniform(2, 5.5)
    stock_bits.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{br:.1f}" ry="{br * 0.55:.1f}" fill="#fff1c9" '
                      f'opacity="0.75" stroke="#b57a3a" stroke-width="0.8"/>')
stock_bits.append('<path d="M1210 568 q14 -8 26 -2" stroke="#7ab648" stroke-width="7" stroke-linecap="round" fill="none"/>')
stock_bits.append('<ellipse cx="1102" cy="572" rx="16" ry="6" fill="#f3ead8" stroke="#c8b38f" stroke-width="1.2"/>')
add(pot(1160, 566, 118, 22, 200, stock_bits, "stock"))

# ---------------------------------------------------------------- tools geometry
TEBO_RIM, TEBO_ANG = (450, 508), -12
TEBO_ATTACH = rot((TEBO_RIM[0] + 44, TEBO_RIM[1]), TEBO_RIM, TEBO_ANG)
TEBO_END = (606, 440)
LADLE_C, LADLE_ANG = (1150, 506), 30
LADLE_ATTACH = rot((LADLE_C[0] - 30, LADLE_C[1]), LADLE_C, LADLE_ANG)
LADLE_END = (1034, 426)


add(f'<path d="{HEAD}" transform="translate(22 18)" fill="#2a1209" opacity="0.32" filter="url(#blur18)"/>')
# ---------------------------------------------------------------- tentacles (behind head)
ARM_A = GripArm([(735, 646), (688, 670), (634, 662), (598, 628), (582, 576)],
                TEBO_ATTACH, TEBO_END, 0.74, 10, 46, side=1, turns=1.25, power=0.7, wrap_w=17)
ARM_C = GripArm([(866, 646), (932, 694), (1004, 692), (1046, 654), (1064, 598)],
                LADLE_ATTACH, LADLE_END, 0.6, 8, 46, side=-1, turns=1.25, power=0.7, wrap_w=17)
ARM_E = [(758, 650), (706, 672), (670, 704), (662, 738), (680, 760), (712, 766), (736, 754)]
ARM_F = [(1600 - x, y) for x, y in ARM_E]
ARM_G = [(728, 690), (680, 716), (626, 730), (590, 750), (572, 782), (568, 826), (580, 862), (604, 876), (622, 864), (618, 846)]

add(tentacle(ARM_G, 32, 6, side=-1))
add(ARM_A.back())
add(ARM_C.back())
add(tentacle(ARM_E, 36, 9, side=-1))
add(tentacle(ARM_F, 36, 9, side=1))

# ---------------------------------------------------------------- head
add(f'<path d="{HEAD}" fill="url(#head)"/>')
add('<g clip-path="url(#headClip)">',
    '<ellipse cx="800" cy="690" rx="200" ry="70" fill="#8e2a33" opacity="0.35" filter="url(#blur18)"/>',
    '<ellipse cx="985" cy="520" rx="60" ry="190" fill="#8e2a33" opacity="0.35" filter="url(#blur18)"/>',
    '<ellipse cx="728" cy="402" rx="58" ry="30" transform="rotate(-28 728 402)" fill="#fff" opacity="0.32" filter="url(#blur9)"/>',
    '<ellipse cx="712" cy="408" rx="16" ry="9" transform="rotate(-28 712 408)" fill="#fff" opacity="0.55" filter="url(#blur2)"/>')
for x, y, r in [(760, 382, 5), (845, 376, 4), (884, 404, 7), (918, 432, 4), (690, 432, 6), (668, 470, 3.5),
                (936, 548, 5), (664, 552, 4.5), (905, 590, 3.5), (812, 400, 3), (948, 474, 3), (700, 590, 3)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffa18a" opacity="0.7" stroke="#c9504a" stroke-width="1" stroke-opacity="0.5"/>')
add('</g>')
add(f'<path d="{HEAD}" fill="none" stroke="#5c1b29" stroke-width="3.6" stroke-linejoin="round"/>')

# hachimaki (twisted headband)
BAND = "M 626 452 Q 800 480 974 452 L 974 488 Q 800 516 626 488 Z"
add('<clipPath id="bandClip"><path d="' + BAND + '"/></clipPath>')
add('<path d="M 626 458 Q 800 488 974 458 L 974 494 Q 800 522 626 494 Z" fill="#7a2230" opacity="0.4" filter="url(#blur2)"/>')
add(f'<path d="{BAND}" fill="#fbf5ea"/>')
add('<g clip-path="url(#bandClip)">')
for x in range(600, 1000, 21):
    add(f'<path d="M{x} 440 L{x + 18} 530" stroke="#2f4f9a" stroke-width="6.5"/>',
        f'<path d="M{x + 8} 440 L{x + 26} 530" stroke="#d9d2c4" stroke-width="2" opacity="0.8"/>')
add('<path d="M 626 455 Q 800 483 974 455" stroke="#ffffff" stroke-width="3" fill="none" opacity="0.7"/>',
    '<path d="M 626 486 Q 800 514 974 486" stroke="#9c9486" stroke-width="5" fill="none" opacity="0.5"/>',
    '<rect x="626" y="440" width="40" height="90" fill="#000" opacity="0.15"/>',
    '<rect x="930" y="440" width="44" height="90" fill="#000" opacity="0.2"/>',
    '</g>')
add(f'<path d="{BAND}" fill="none" stroke="#3b2a35" stroke-width="2.6" stroke-linejoin="round"/>')
# knot and tails
for d_tail in ("M 966 462 Q 988 432 1014 416 Q 1010 438 1000 452 Q 990 468 976 478 Z",
               "M 970 478 Q 1000 484 1022 504 Q 1002 506 990 498 Q 980 492 970 488 Z"):
    add(f'<path d="{d_tail}" fill="#fbf5ea" stroke="#3b2a35" stroke-width="2.4" stroke-linejoin="round"/>')
add('<path d="M 990 440 L 1000 452 M 1004 426 L 1010 436 M 988 488 L 996 498 M 1004 494 L 1012 502" '
    'stroke="#2f4f9a" stroke-width="5" stroke-linecap="round"/>')
add('<ellipse cx="968" cy="472" rx="17" ry="15" fill="#fbf5ea" stroke="#3b2a35" stroke-width="2.4"/>',
    '<path d="M 956 464 Q 968 476 980 466 M 958 478 Q 968 486 978 480" stroke="#2f4f9a" stroke-width="4" fill="none" stroke-linecap="round"/>')

# face
for ex in (748, 852):
    lid = f"M{ex - 26} 581.5 Q{ex} 568 {ex + 26} 581.5 A29 35 0 0 1 {ex - 26} 581.5 Z"
    add(f'<ellipse cx="{ex}" cy="566" rx="29" ry="35" fill="#fffdf8" stroke="#4a1622" stroke-width="3"/>',
        f'<ellipse cx="{ex + 1}" cy="563" rx="18" ry="22" fill="#3a1a1f"/>',
        f'<ellipse cx="{ex + 1}" cy="565" rx="13" ry="17" fill="#120a10"/>',
        f'<circle cx="{ex - 6}" cy="553" r="7" fill="#fff"/>',
        f'<circle cx="{ex + 8}" cy="570" r="3" fill="#fff" opacity="0.9"/>',
        f'<path d="{lid}" fill="#ee6a52"/>',
        f'<path d="M{ex - 27} 582 Q{ex} 567 {ex + 27} 582" fill="none" stroke="#4a1622" stroke-width="3.2" stroke-linecap="round"/>',
        f'<path d="M{ex - 28} 552 Q{ex} 524 {ex + 28} 552" fill="none" stroke="#4a1622" stroke-width="3" stroke-linecap="round"/>')
add('<ellipse cx="704" cy="608" rx="21" ry="11" fill="#ff6f86" opacity="0.6" filter="url(#blur2)"/>',
    '<ellipse cx="896" cy="608" rx="21" ry="11" fill="#ff6f86" opacity="0.6" filter="url(#blur2)"/>')
# pursed tube mouth (classic tako face)
add('<path d="M 786 606 Q 800 598 816 606 L 820 630 Q 805 640 790 630 Z" fill="#d9534a" stroke="#5c1b29" stroke-width="2.6" stroke-linejoin="round"/>',
    '<ellipse cx="805" cy="630" rx="16" ry="11" fill="#f27a64" stroke="#5c1b29" stroke-width="2.8"/>',
    '<ellipse cx="806" cy="631" rx="8" ry="5.5" fill="#5c1b29"/>',
    '<path d="M 791 607 Q 800 603 809 606" stroke="#ffb59b" stroke-width="3" fill="none" stroke-linecap="round"/>')
# whistled notes
for nx, ny, sc in ((990, 640, 1.0), (1012, 596, 0.8)):
    add(f'<g transform="translate({nx} {ny}) scale({sc}) rotate(12)" fill="#fff4dc" stroke="#5c1b29" stroke-width="1.6">'
        '<ellipse cx="0" cy="0" rx="7" ry="5.5" transform="rotate(-20)"/>'
        '<path d="M5.5 -2 L5.5 -26 Q 12 -20 15 -14" fill="none" stroke-width="3" stroke="#fff4dc"/></g>')

# ---------------------------------------------------------------- tebo (noodle strainer) arm A
tebo = [f'<g transform="rotate({TEBO_ANG} {TEBO_RIM[0]} {TEBO_RIM[1]})">']
cx, cy = TEBO_RIM
body = (f"M{cx - 44} {cy} L{cx - 40} {cy + 50} Q{cx - 36} {cy + 76} {cx} {cy + 78} "
        f"Q{cx + 36} {cy + 76} {cx + 40} {cy + 50} L{cx + 44} {cy} Z")
tebo += [f'<path d="{body}" fill="#4d545e"/>', f'<path d="{body}" fill="url(#mesh)" opacity="0.75"/>',
         f'<path d="{body}" fill="url(#steelDark)" opacity="0.45"/>',
         f'<path d="{body}" fill="none" stroke="#2b3037" stroke-width="2.2"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="44" ry="10" fill="#2b3037"/>']
for k in range(7):
    yy = cy - 2 - k * 1.6
    amp = 6 + (k % 3) * 2
    pts = [(cx - 40 + i * 4, yy - abs(math.sin(i * 0.42 + k)) * amp - (12 if 3 < i < 17 else 4) * math.sin(i / 20 * math.pi))
           for i in range(21)]
    tebo.append(f'<path d="{d_of(pts, False)}" fill="none" stroke="#e7bd5a" stroke-width="5" stroke-linecap="round"/>')
    tebo.append(f'<path d="{d_of(pts, False)}" fill="none" stroke="#fde59b" stroke-width="2" stroke-linecap="round"/>')
tebo += [f'<path d="M{cx - 44} {cy} A44 10 0 0 0 {cx + 44} {cy}" fill="none" stroke="#e9eef2" stroke-width="3.5"/>',
         f'<path d="M{cx - 30} {cy + 74} Q{cx} {cy + 82} {cx + 30} {cy + 74}" fill="none" stroke="#2b3037" stroke-width="2"/>',
         '</g>']
add(tebo)
bottom = rot((cx, cy + 78), TEBO_RIM, TEBO_ANG)
for dx, dy, s in [(-14, 12, 1.0), (4, 22, 0.8), (16, 8, 0.9), (-4, 34, 0.7)]:
    x, y = bottom[0] + dx, bottom[1] + dy
    add(f'<path d="M{x} {y - 7 * s:.1f} Q{x + 4.5 * s:.1f} {y + 1:.1f} {x} {y + 4 * s:.1f} Q{x - 4.5 * s:.1f} {y + 1:.1f} {x} {y - 7 * s:.1f} Z" '
        f'fill="#e8f7ff" stroke="#8fb3c7" stroke-width="0.8"/>')
add('<path d="M440 626 q8 -8 16 0 M478 628 q6 -6 12 0" stroke="#ffffff" stroke-width="2" fill="none" opacity="0.8"/>')
for k, (mx, my) in enumerate([(388, 470), (372, 500)]):
    add(f'<path d="M{mx} {my} q-12 26 0 54" stroke="#ffffff" stroke-width="{3.2 - k}" fill="none" stroke-linecap="round" opacity="0.6"/>')
add(f'<path d="M{TEBO_ATTACH[0]:.1f} {TEBO_ATTACH[1]:.1f} L{TEBO_END[0]} {TEBO_END[1]}" stroke="#5a3820" stroke-width="10" stroke-linecap="round"/>',
    f'<path d="M{TEBO_ATTACH[0]:.1f} {TEBO_ATTACH[1] - 2:.1f} L{TEBO_END[0]} {TEBO_END[1] - 2}" stroke="#b07f50" stroke-width="2.6" stroke-linecap="round"/>')
fer = lerp(TEBO_ATTACH, TEBO_END, 0.12)
add(f'<path d="M{TEBO_ATTACH[0]:.1f} {TEBO_ATTACH[1]:.1f} L{fer[0]:.1f} {fer[1]:.1f}" stroke="#c7ced5" stroke-width="7" stroke-linecap="round"/>')
add(ARM_A.front())

# ---------------------------------------------------------------- ladle arm C
lad = [f'<g transform="rotate({LADLE_ANG} {LADLE_C[0]} {LADLE_C[1]})">']
cx, cy = LADLE_C
cup = f"M{cx - 30} {cy} L{cx - 28} {cy + 24} Q{cx} {cy + 40} {cx + 28} {cy + 24} L{cx + 30} {cy} Z"
lad += [f'<path d="{cup}" fill="url(#steel)" stroke="#3f4550" stroke-width="2"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="30" ry="8" fill="#d79d55" stroke="#eef2f5" stroke-width="3"/>',
        f'<ellipse cx="{cx - 6}" cy="{cy - 1}" rx="12" ry="3" fill="#f7deaa" opacity="0.8"/>',
        '</g>']
add(lad)
lip = rot((cx + 30, cy), LADLE_C, LADLE_ANG)
add(f'<path d="{ribbon_shape([lip, (lip[0] + 8, lip[1] + 18), (lip[0] + 12, lip[1] + 40), (lip[0] + 13, 568)], 8, 4)}" '
    f'fill="#e0a85e" opacity="0.92"/>',
    f'<path d="M{lip[0] + 3:.1f} {lip[1] + 6:.1f} Q{lip[0] + 10:.1f} {lip[1] + 22:.1f} {lip[0] + 12:.1f} {lip[1] + 40:.1f}" '
    f'stroke="#fbe2b0" stroke-width="1.6" fill="none" opacity="0.9"/>',
    f'<ellipse cx="{lip[0] + 13:.1f}" cy="569" rx="14" ry="4" fill="none" stroke="#fbe2b0" stroke-width="1.8" opacity="0.9"/>')
add(f'<path d="M{LADLE_ATTACH[0]:.1f} {LADLE_ATTACH[1]:.1f} L{LADLE_END[0]} {LADLE_END[1]}" stroke="#8d96a1" stroke-width="8" stroke-linecap="round"/>',
    f'<path d="M{LADLE_ATTACH[0]:.1f} {LADLE_ATTACH[1] - 2:.1f} L{LADLE_END[0]} {LADLE_END[1] - 2}" stroke="#eef2f5" stroke-width="2.2" stroke-linecap="round"/>',
    f'<circle cx="{LADLE_END[0]}" cy="{LADLE_END[1]}" r="5" fill="none" stroke="#8d96a1" stroke-width="2.5"/>')
add(ARM_C.front())

# ---------------------------------------------------------------- counter
add('<path d="M215 748 L1385 748 L1398 770 L202 770 Z" fill="url(#counterTop)"/>',
    '<path d="M215 748 L1385 748" stroke="#7a4a28" stroke-width="2"/>')
for k in range(9):
    y = 752 + k * 2.1
    x0 = rng.uniform(220, 900)
    add(f'<path d="M{x0:.0f} {y:.1f} h{rng.uniform(120, 420):.0f}" stroke="#9c6a3c" stroke-width="0.9" opacity="0.5"/>')
add('<rect x="202" y="770" width="1196" height="24" fill="url(#counterEdge)"/>',
    '<rect x="202" y="770" width="1196" height="2" fill="#f2c98f" opacity="0.7"/>',
    '<rect x="238" y="794" width="1124" height="196" fill="url(#panel)"/>')
for x in range(238 + 70, 1362, 70):
    add(f'<path d="M{x} 796 V988" stroke="#2c170b" stroke-width="2.5" opacity="0.7"/>',
        f'<path d="M{x + 2} 796 V988" stroke="#a0643a" stroke-width="1" opacity="0.35"/>')
add('<rect x="238" y="794" width="1124" height="18" fill="#1c0d05" opacity="0.5" filter="url(#blur5)"/>',
    '<rect x="232" y="978" width="1136" height="14" fill="#3b1f10"/>')


def octo_logo(cx, cy, s, fg, bg):
    o = [f'<ellipse cx="{cx}" cy="{cy - 0.17 * s:.1f}" rx="{0.34 * s:.1f}" ry="{0.32 * s:.1f}" fill="{fg}"/>']
    for k in range(6):
        u = (k - 2.5) / 2.5
        x0 = cx + u * 0.2 * s
        x1 = cx + u * 0.42 * s
        y1 = cy + 0.34 * s
        curl = 1 if u > 0 else -1
        o.append(f'<path d="M{x0:.1f} {cy + 0.05 * s:.1f} Q{cx + u * 0.36 * s:.1f} {cy + 0.2 * s:.1f} {x1:.1f} {y1:.1f} '
                 f'q{curl * 0.08 * s:.1f} {0.04 * s:.1f} {curl * 0.1 * s:.1f} {-0.05 * s:.1f}" fill="none" stroke="{fg}" '
                 f'stroke-width="{0.075 * s:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 0.35 * s:.1f} {cy - 0.25 * s:.1f} Q{cx} {cy - 0.15 * s:.1f} {cx + 0.35 * s:.1f} {cy - 0.25 * s:.1f}" '
             f'fill="none" stroke="{bg}" stroke-width="{0.07 * s:.1f}"/>')
    for ex in (-0.12, 0.12):
        o.append(f'<circle cx="{cx + ex * s:.1f}" cy="{cy - 0.04 * s:.1f}" r="{0.055 * s:.1f}" fill="{bg}"/>')
        o.append(f'<circle cx="{cx + ex * s + 0.01 * s:.1f}" cy="{cy - 0.03 * s:.1f}" r="{0.028 * s:.1f}" fill="{fg}"/>')
    o.append(f'<circle cx="{cx:.1f}" cy="{cy + 0.04 * s:.1f}" r="{0.04 * s:.1f}" fill="none" stroke="{bg}" stroke-width="{0.02 * s:.1f}"/>')
    return o


add('<circle cx="800" cy="890" r="64" fill="#f3e6cc" stroke="#2c170b" stroke-width="3"/>',
    '<circle cx="800" cy="890" r="56" fill="none" stroke="#c63a2e" stroke-width="2.5"/>')
add(octo_logo(800, 892, 96, "#c63a2e", "#f3e6cc"))

# ---------------------------------------------------------------- hero bowl
BX, BY, BRX, BRY = 800, 690, 138, 27


def hw(dy):
    return BRX - 80 * (max(dy, 0) / 70) ** 1.8


def bowl_pt(s, dy):
    h = hw(dy)
    u = (s - 0.5) * math.pi * 0.97
    return (BX + h * math.sin(u), BY + dy + BRY * h / BRX * math.cos(u))


def warp(poly, units, dy0, dy1, s0, s1):
    pts = []
    for (a, b) in zip(poly, poly[1:]):
        for k in range(5):
            t = k / 5
            u = a[0] + (b[0] - a[0]) * t
            v = a[1] + (b[1] - a[1]) * t
            pts.append(bowl_pt(s0 + (s1 - s0) * u, dy0 + (dy1 - dy0) * v))
    u, v = poly[-1]
    pts.append(bowl_pt(s0 + (s1 - s0) * u, dy0 + (dy1 - dy0) * v))
    return pts


add('<ellipse cx="800" cy="768" rx="150" ry="10" fill="#3a1f10" opacity="0.5" filter="url(#blur5)"/>')
left_prof = [(BX - hw(dy), BY + dy) for dy in range(0, 71, 5)]
right_prof = [(BX + hw(dy), BY + dy) for dy in range(70, -1, -5)]
foot_bottom = [(BX - 58 + 116 * i / 10, BY + 70 + 8 * math.sin(math.pi * i / 10)) for i in range(11)]
add(f'<path d="{d_of(left_prof + foot_bottom + right_prof, False)} A{BRX} {BRY} 0 0 1 {BX - BRX} {BY} Z" fill="url(#bowlBody)" '
    f'stroke="#6e5f4f" stroke-width="2.4"/>')
add(f'<path d="M{BX - 56} {BY + 70} Q{BX} {BY + 82} {BX + 56} {BY + 70} L{BX + 52} {BY + 77} Q{BX} {BY + 88} {BX - 52} {BY + 77} Z" '
    f'fill="#d8cfbf" stroke="#6e5f4f" stroke-width="2"/>')
RED = "#c3302a"
for dy in (8, 28, 34):
    add(f'<path d="{d_of([bowl_pt(i / 60, dy) for i in range(61)], False)}" fill="none" stroke="{RED}" '
        f'stroke-width="{2.4 if dy != 34 else 1.6}"/>')
spiral = [(0.12, 1), (0.12, 0), (0.88, 0), (0.88, 0.82), (0.32, 0.82), (0.32, 0.28), (0.68, 0.28), (0.68, 0.58), (0.5, 0.58)]
NU = 15
for k in range(NU):
    pts = warp(spiral, NU, 12, 24, k / NU, (k + 1) / NU)
    add(f'<path d="{d_of(pts, False)}" fill="none" stroke="{RED}" stroke-width="1.7" stroke-linejoin="miter"/>')
add(f'<ellipse cx="{BX - 70}" cy="{BY + 44}" rx="16" ry="22" fill="#ffffff" opacity="0.45" filter="url(#blur5)"/>')
# interior
add(f'<ellipse cx="{BX}" cy="{BY}" rx="{BRX}" ry="{BRY}" fill="url(#bowlInside)"/>',
    f'<ellipse cx="{BX}" cy="{BY + 5}" rx="{BRX - 12}" ry="{BRY - 6}" fill="url(#broth)"/>')
for _ in range(22):
    a = rng.uniform(0, 2 * math.pi)
    rr = math.sqrt(rng.random())
    ox, oy = BX + math.cos(a) * 112 * rr, BY + 5 + math.sin(a) * 18 * rr
    r = rng.uniform(1.6, 4.2)
    add(f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="{r:.1f}" ry="{r * 0.55:.1f}" fill="#fbe7b8" stroke="#c88a45" '
        f'stroke-width="0.7" opacity="0.85"/>')
# noodles nest
for k in range(9):
    y0 = BY + 1 + k * 2.2
    ph = rng.uniform(0, 6)
    pts = [(BX - 100 + i * 10, y0 + 3.5 * math.sin(i * 0.9 + ph) + (i - 10) ** 2 * -0.02) for i in range(21)]
    add(f'<path d="{d_of(pts, False)}" fill="none" stroke="#e2b552" stroke-width="5" stroke-linecap="round"/>',
        f'<path d="{d_of(pts, False)}" fill="none" stroke="#fde5a0" stroke-width="1.8" stroke-linecap="round"/>')
# nori
for nx, tilt, shade in ((866, 9, "#1c2a22"), (892, 15, "#22332a")):
    add(f'<g transform="rotate({tilt} {nx} 690)"><rect x="{nx - 26}" y="624" width="54" height="70" rx="2" fill="{shade}" '
        f'stroke="#0d1510" stroke-width="2"/>'
        f'<path d="M{nx - 18} 632 v52 M{nx - 4} 630 v56 M{nx + 12} 632 v52" stroke="#3d5546" stroke-width="1.4" opacity="0.6"/>'
        f'<path d="M{nx - 24} 628 h50" stroke="#55705e" stroke-width="2" opacity="0.6"/></g>')


def chashu(cx, cy, rx, ry, ang):
    return (f'<g transform="rotate({ang} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#7e3b22" stroke="#45190d" stroke-width="2"/>'
            f'<ellipse cx="{cx + 1}" cy="{cy + 1}" rx="{rx - 6}" ry="{ry - 5}" fill="#d99a7e"/>'
            f'<path d="M{cx - rx * 0.6:.1f} {cy:.1f} C{cx - rx * 0.4:.1f} {cy - ry * 0.7:.1f} {cx + rx * 0.5:.1f} {cy - ry * 0.6:.1f} '
            f'{cx + rx * 0.45:.1f} {cy + ry * 0.05:.1f} C{cx + rx * 0.4:.1f} {cy + ry * 0.5:.1f} {cx - rx * 0.2:.1f} {cy + ry * 0.45:.1f} '
            f'{cx - rx * 0.15:.1f} {cy + ry * 0.05:.1f}" fill="none" stroke="#f7dcca" stroke-width="3.5" stroke-linecap="round"/>'
            f'<ellipse cx="{cx - rx * 0.35:.1f}" cy="{cy - ry * 0.4:.1f}" rx="{rx * 0.22:.1f}" ry="{ry * 0.12:.1f}" fill="#fff" opacity="0.35"/>'
            f'</g>')


add(chashu(728, 678, 42, 30, -14), chashu(770, 683, 40, 28, -6))
for mx, my, ang in ((708, 703, 18), (720, 708, -10), (735, 704, 30), (700, 711, -4)):
    add(f'<rect x="{mx - 12}" y="{my - 3.5}" width="24" height="7" rx="3" transform="rotate({ang} {mx} {my})" fill="#c99b58" '
        f'stroke="#8e6630" stroke-width="1.2"/>')


def egg(cx, cy, ang):
    return (f'<g transform="rotate({ang} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="25" ry="17" fill="#f6e5cb" stroke="#b47a42" stroke-width="3.2"/>'
            f'<ellipse cx="{cx + 1}" cy="{cy - 1}" rx="14" ry="10" fill="url(#yolk)"/>'
            f'<ellipse cx="{cx + 1}" cy="{cy - 1}" rx="7.5" ry="5" fill="#ffd36b" opacity="0.85"/>'
            f'<ellipse cx="{cx - 4}" cy="{cy - 4}" rx="4" ry="2" fill="#fff" opacity="0.8"/></g>')


add(egg(858, 704, -8), egg(892, 698, 10))
# naruto
pts = []
for i in range(73):
    th = 2 * math.pi * i / 72
    r = 1 + 0.07 * math.cos(12 * th)
    pts.append((800 + 21 * r * math.cos(th), 711 + 13 * r * math.sin(th)))
add(f'<path d="{d_of(pts)}" fill="#fffaf3" stroke="#d9cbbb" stroke-width="1.4"/>')
sp = [(800 + (2 + t * 1.45) * math.cos(t) * 1.0, 711 + (2 + t * 1.45) * math.sin(t) * 0.62) for t in [i * 0.2 for i in range(56)]]
add(f'<path d="{d_of(sp, False)}" fill="none" stroke="#ec5f8e" stroke-width="2.8" stroke-linecap="round"/>')
# scallions + chili threads + sesame
for _ in range(46):
    a = rng.uniform(0, 2 * math.pi)
    rr = math.sqrt(rng.random())
    x, y = 798 + math.cos(a) * 46 * rr, 696 + math.sin(a) * 9 * rr
    add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.6" ry="2.4" fill="#c8eb8f" stroke="#4f9a2e" stroke-width="1.5"/>')
for _ in range(12):
    a = rng.uniform(0, 2 * math.pi)
    x, y = BX + math.cos(a) * rng.uniform(40, 110), BY + 6 + math.sin(a) * rng.uniform(6, 16)
    add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.2" ry="2.1" fill="#c8eb8f" stroke="#4f9a2e" stroke-width="1.3"/>')
for _ in range(8):
    x, y = 798 + rng.uniform(-22, 22), 690 + rng.uniform(-4, 6)
    a = rng.uniform(0, math.pi)
    add(f'<path d="M{x:.1f} {y:.1f} l{9 * math.cos(a):.1f} {4 * math.sin(a):.1f}" stroke="#d9261c" stroke-width="1.3" stroke-linecap="round"/>')
for _ in range(16):
    x, y = BX + rng.uniform(-100, 100), BY + 5 + rng.uniform(-12, 14)
    add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="1.6" ry="1" fill="#fff4dd"/>')
add(f'<ellipse cx="{BX}" cy="{BY}" rx="{BRX}" ry="{BRY}" fill="none" stroke="#fffdf8" stroke-width="4"/>',
    f'<ellipse cx="{BX}" cy="{BY}" rx="{BRX + 2}" ry="{BRY + 2}" fill="none" stroke="#6e5f4f" stroke-width="1.6"/>')

# tentacle tips cradling the bowl
add(tentacle(ARM_E, 36, 9, side=-1, t0=0.58))
add(tentacle(ARM_F, 36, 9, side=1, t0=0.58))
# arm G draped over the counter edge
add(tentacle(ARM_G, 32, 6, side=-1, t0=t_at_y(ARM_G, 749)))

# ---------------------------------------------------------------- counter props
# chopstick box
add('<rect x="306" y="712" width="52" height="50" rx="3" fill="#7a4628" stroke="#3b1f10" stroke-width="2"/>',
    '<rect x="306" y="712" width="52" height="9" fill="#a8693d"/>')
for k in range(9):
    x = 312 + k * 5.2
    add(f'<path d="M{x:.1f} 712 L{x + rng.uniform(-3, 3):.1f} {rng.uniform(684, 694):.1f}" stroke="#f0d9ae" stroke-width="3" stroke-linecap="round"/>')
add('<rect x="306" y="728" width="52" height="16" fill="#c63a2e" opacity="0.85"/>')
# shichimi gourd
add('<path d="M392 762 C372 762 370 736 384 730 C376 720 382 708 392 708 C402 708 408 720 400 730 C414 736 412 762 392 762 Z" '
    'fill="#c8331f" stroke="#5a1209" stroke-width="2"/>',
    '<rect x="386" y="699" width="12" height="11" rx="2" fill="#8a5a2e" stroke="#3b1f10" stroke-width="1.5"/>',
    '<ellipse cx="385" cy="744" rx="4" ry="8" fill="#fff" opacity="0.35"/>')
# soy dispenser
add('<path d="M428 762 C410 762 410 728 424 724 L424 714 L440 714 L440 724 C454 728 454 762 436 762 Z" fill="#3a1d12" '
    'stroke="#1a0b05" stroke-width="2" opacity="0.95"/>',
    '<path d="M421 712 L443 712 L440 700 L424 700 Z" fill="#d63a2a" stroke="#6a120a" stroke-width="1.5"/>',
    '<path d="M440 704 L452 698" stroke="#d63a2a" stroke-width="4" stroke-linecap="round"/>',
    '<ellipse cx="421" cy="742" rx="3" ry="9" fill="#fff" opacity="0.4"/>')
# pickled ginger pot
add('<path d="M470 762 L466 722 L514 722 L510 762 Z" fill="#efe6d6" stroke="#6e5f4f" stroke-width="2"/>',
    '<ellipse cx="490" cy="722" rx="25" ry="6" fill="#e86a7f" stroke="#6e5f4f" stroke-width="1.8"/>',
    '<path d="M468 738 L512 738" stroke="#3c4f8f" stroke-width="5"/>',
    '<rect x="478" y="712" width="24" height="5" rx="2" fill="#6e5f4f"/>')
# stacked bowls on the right
for k in range(3):
    y = 762 - k * 17
    add(f'<path d="M1222 {y - 16} L1318 {y - 16} L1302 {y} L1238 {y} Z" fill="url(#bowlBody)" stroke="#6e5f4f" stroke-width="1.8"/>',
        f'<path d="M1226 {y - 11} L1314 {y - 11}" stroke="{RED}" stroke-width="2"/>')
add('<ellipse cx="1270" cy="711" rx="49" ry="7" fill="#efe9de" stroke="#6e5f4f" stroke-width="1.8"/>')
# renge spoons
add('<path d="M1196 760 Q1176 762 1172 748 Q1184 738 1200 744 L1232 728" fill="#fbf7ef" stroke="#6e5f4f" stroke-width="2" stroke-linejoin="round"/>')

# cart wheels (edge-on)
for wx in (226, 1374):
    add(f'<ellipse cx="{wx}" cy="944" rx="24" ry="72" fill="#2a160c"/>',
        f'<ellipse cx="{wx}" cy="944" rx="15" ry="60" fill="#8a5432"/>',
        f'<ellipse cx="{wx}" cy="944" rx="7" ry="14" fill="#2a160c"/>',
        f'<path d="M{wx - 6} 890 Q{wx - 12} 944 {wx - 6} 998" stroke="#c48a55" stroke-width="2" fill="none" opacity="0.6"/>')


# ---------------------------------------------------------------- stools
def stool(cx, seat_y):
    o = [f'<ellipse cx="{cx}" cy="{seat_y + 160}" rx="80" ry="12" fill="#000" opacity="0.45" filter="url(#blur5)"/>']
    for lx, ex in ((-44, -54), (44, 54), (-20, -24), (20, 24)):
        shade = "#5e3a20" if abs(lx) < 30 else "#8a5732"
        o.append(f'<path d="M{cx + lx} {seat_y + 14} L{cx + ex} {seat_y + 158}" stroke="{shade}" stroke-width="10" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 50} {seat_y + 104} L{cx + 50} {seat_y + 104}" stroke="#6e4426" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 66} {seat_y} L{cx - 66} {seat_y + 16} A66 16 0 0 0 {cx + 66} {seat_y + 16} L{cx + 66} {seat_y} Z" '
             f'fill="url(#stool)" stroke="#3b1f10" stroke-width="2"/>')
    o.append(f'<ellipse cx="{cx}" cy="{seat_y}" rx="66" ry="16" fill="#d8a46a" stroke="#3b1f10" stroke-width="2"/>')
    o.append(f'<ellipse cx="{cx - 14}" cy="{seat_y - 3}" rx="34" ry="6" fill="#f3c98f" opacity="0.6"/>')
    return o


add(stool(520, 946), stool(1090, 946))


# ---------------------------------------------------------------- cat customer (seen from behind)
def cat(cx, seat_y):
    white, shade, black, line, rim = "#f5f1e8", "#d3cabd", "#26222b", "#4a4048", "#ffc98a"
    sh_y = 794                       # shoulders, just below the counter edge
    hx, hy = cx - 4, 744             # head peeks over the counter
    o = [f'<path d="M{cx + 34} {seat_y - 8} C{cx + 86} {seat_y + 2} {cx + 66} {seat_y + 70} {cx + 94} {seat_y + 104} '
         f'C{cx + 102} {seat_y + 114} {cx + 116} {seat_y + 106} {cx + 110} {seat_y + 94}" fill="none" stroke="{black}" '
         f'stroke-width="15" stroke-linecap="round"/>']
    # forelegs reaching up onto the counter top (drawn first so the body hides their roots)
    for sx in (-1, 1):
        leg = f"M{cx + sx * 22} {sh_y + 24} Q{cx + sx * 42} {sh_y + 4} {cx + sx * 44} {sh_y - 32}"
        o.append(f'<path d="{leg}" stroke="{line}" stroke-width="23" stroke-linecap="round" fill="none"/>')
        o.append(f'<path d="{leg}" stroke="{white}" stroke-width="18" stroke-linecap="round" fill="none"/>')
        o.append(f'<ellipse cx="{cx + sx * 45}" cy="{sh_y - 35}" rx="13" ry="7.5" fill="{white}" stroke="{line}" stroke-width="2"/>')
        o.append(f'<path d="M{cx + sx * 45 - 5} {sh_y - 40} v6 M{cx + sx * 45 + 4} {sh_y - 40} v6" stroke="#a0958b" stroke-width="1.3"/>')
    o.append(f'<ellipse cx="{cx}" cy="{seat_y - 16}" rx="50" ry="24" fill="{white}" stroke="{line}" stroke-width="2.4"/>')
    torso = (f"M{cx - 46} {seat_y - 14} C{cx - 54} {seat_y - 70} {cx - 44} {sh_y + 26} {cx - 34} {sh_y + 2} "
             f"Q{cx} {sh_y - 30} {cx + 34} {sh_y + 2} C{cx + 44} {sh_y + 26} {cx + 54} {seat_y - 70} {cx + 46} {seat_y - 14} "
             f"Q{cx} {seat_y} {cx - 46} {seat_y - 14} Z")
    o.append(f'<path d="{torso}" fill="{white}" stroke="{line}" stroke-width="2.4"/>')
    o.append(f'<path d="M{cx} {sh_y + 16} V{seat_y - 34}" stroke="{shade}" stroke-width="3" opacity="0.6"/>')
    o.append(f'<path d="M{cx - 8} {sh_y + 46} C{cx + 26} {sh_y + 32} {cx + 44} {sh_y + 72} {cx + 30} {sh_y + 98} '
             f'C{cx + 14} {sh_y + 118} {cx - 22} {sh_y + 98} {cx - 8} {sh_y + 46} Z" fill="{black}"/>')
    o.append(f'<path d="M{cx - 44} {seat_y - 18} Q{cx} {seat_y - 4} {cx + 44} {seat_y - 18}" stroke="{shade}" stroke-width="4" fill="none" opacity="0.7"/>')
    # head from behind: no face, just ears, a patch and whiskers poking out sideways
    rx_h, ry_h = 42, 36
    o.append(f'<g transform="rotate(-8 {hx} {hy})">')
    for sx in (-1, 1):
        ear_fill = black if sx < 0 else white
        o.append(f'<path d="M{hx + sx * 10} {hy - 28} L{hx + sx * 30} {hy - 62} L{hx + sx * 38} {hy - 16} Z" fill="{ear_fill}" '
                 f'stroke="{line}" stroke-width="2.2" stroke-linejoin="round"/>')
    o.append(f'<ellipse cx="{hx}" cy="{hy}" rx="{rx_h}" ry="{ry_h}" fill="{white}" stroke="{line}" stroke-width="2.4"/>')
    o.append(f'<path d="M{hx - 41} {hy - 4} C{hx - 40} {hy - 30} {hx - 22} {hy - 38} {hx - 2} {hy - 36} '
             f'C{hx + 4} {hy - 20} {hx - 14} {hy - 2} {hx - 30} {hy + 16} C{hx - 38} {hy + 12} {hx - 42} {hy + 4} {hx - 41} {hy - 4} Z" fill="{black}"/>')
    o.append(f'<path d="M{hx - 24} {hy + 28} Q{hx} {hy + 38} {hx + 24} {hy + 28}" stroke="{shade}" stroke-width="5" fill="none" opacity="0.55"/>')
    arc = [(hx + (rx_h - 2.5) * math.cos(a), hy + (ry_h - 2.5) * math.sin(a))
           for a in [math.radians(205 + 7 * k) for k in range(19)]]
    o.append(f'<path d="{d_of(arc, False)}" stroke="{rim}" stroke-width="2.6" fill="none" stroke-linecap="round" opacity="0.9"/>')
    o.append(f'<path d="M{hx - 40} {hy + 12} l-26 -6 M{hx - 39} {hy + 18} l-24 3 M{hx + 40} {hy + 12} l26 -6 M{hx + 39} {hy + 18} l24 3" '
             f'stroke="#f8f4ec" stroke-width="1.5" stroke-linecap="round"/>')
    o.append('</g>')
    o.append(f'<path d="M{cx - 38} {sh_y + 12} Q{cx - 50} {sh_y + 44} {cx - 52} {seat_y - 50}" stroke="{rim}" stroke-width="2.4" '
             f'fill="none" opacity="0.45"/>')
    return o


add(cat(1090, 942))


# ---------------------------------------------------------------- steam
def plume(x, y, h, w0, w1, sway, phase):
    ctrl = [(x + sway * math.sin(phase + k * 1.15) * (k / 5) ** 0.8, y - h * k / 5) for k in range(6)]
    pts, _ = resample(catmull(ctrl, 12), 44)
    tans, nors = frames(pts)
    wd = [w0 + (w1 - w0) * i / 43 for i in range(44)]
    left = [(p[0] + q[0] * w / 2, p[1] + q[1] * w / 2) for p, q, w in zip(pts, nors, wd)]
    right = [(p[0] - q[0] * w / 2, p[1] - q[1] * w / 2) for p, q, w in zip(pts, nors, wd)]
    end = cap_arc(pts[-1], tans[-1], nors[-1], wd[-1] / 2)
    return f'<path d="{d_of(left + end + right[::-1])}" fill="url(#steam)"/>'


add('<g filter="url(#blur9)">')
for (x, y, h, w0, w1, sw, ph) in [(420, 612, 250, 30, 70, 30, 0.3), (482, 608, 290, 34, 80, 36, 2.1), (540, 614, 220, 26, 60, 26, 4.0),
                                  (1110, 556, 220, 30, 70, 28, 1.0), (1176, 552, 250, 34, 80, 34, 3.1), (1236, 558, 200, 26, 62, 24, 5.0)]:
    add(plume(x, y, h, w0, w1, sw, ph))
add('</g>', '<g filter="url(#blur5)" opacity="0.85">')
for (x, y, h, w0, w1, sw, ph) in [(724, 664, 120, 10, 26, -28, 0.4), (798, 650, 70, 8, 18, 14, 2.4), (878, 664, 120, 10, 26, 30, 4.4)]:
    add(plume(x, y, h, w0, w1, sw, ph))
add('</g>')

# ---------------------------------------------------------------- roof
add(f'<path d="{ROOF}" fill="url(#roof)"/>')
add('<g clip-path="url(#roofClip)">')
for i in range(0, 44):
    xe = ROOF_EAVE_L + 15 + i * 30
    xr = 300 + (xe - ROOF_EAVE_L) / (ROOF_EAVE_R - ROOF_EAVE_L) * 1000
    ye = eave_y(xe) + 4
    add(f'<path d="M{xr:.1f} {RIDGE_Y} L{xe:.1f} {ye:.1f}" stroke="#171a2a" stroke-width="5"/>',
        f'<path d="M{xr + 6:.1f} {RIDGE_Y} L{xe + 8:.1f} {ye:.1f}" stroke="#7a82aa" stroke-width="2.4" opacity="0.55"/>')
for f in (0.25, 0.5, 0.75):
    pts = [(x, RIDGE_Y + (eave_y(x) - RIDGE_Y) * f) for x in range(140, 1470, 20)]
    add(f'<path d="{d_of(pts, False)}" stroke="#14172a" stroke-width="2" fill="none" opacity="0.55"/>')
add('</g>')
for i in range(0, 44):
    xe = ROOF_EAVE_L + 15 + i * 30
    ye = eave_y(xe)
    add(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="11" fill="#3b4160" stroke="#14172a" stroke-width="2"/>',
        f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="4.5" fill="#5f6790"/>')
add(f'<path d="M290 {RIDGE_Y - 6} L1310 {RIDGE_Y - 6} L1310 {RIDGE_Y + 10} L290 {RIDGE_Y + 10} Z" fill="#2a2e46" stroke="#14172a" stroke-width="2"/>',
    f'<path d="M290 {RIDGE_Y - 4} H1310" stroke="#6f779f" stroke-width="2" opacity="0.6"/>',
    f'<path d="M296 {RIDGE_Y + 10} L272 {RIDGE_Y - 22} L300 {RIDGE_Y - 8} Z" fill="#2a2e46" stroke="#14172a" stroke-width="2"/>',
    f'<path d="M1304 {RIDGE_Y + 10} L1328 {RIDGE_Y - 22} L1300 {RIDGE_Y - 8} Z" fill="#2a2e46" stroke="#14172a" stroke-width="2"/>')
add('<rect x="196" y="214" width="1208" height="22" fill="#4a2414"/>',
    '<rect x="196" y="214" width="1208" height="3" fill="#8a4a2a"/>',
    '<rect x="196" y="234" width="1208" height="3" fill="#1c0b05"/>')

# signboard on the ridge
add('<rect x="700" y="128" width="200" height="64" rx="4" fill="#2a160c" stroke="#d9b06a" stroke-width="3"/>',
    '<rect x="708" y="136" width="184" height="48" rx="2" fill="#f1e2c4"/>')
add(octo_logo(740, 162, 48, "#c63a2e", "#f1e2c4"))
add('<text x="818" y="171" text-anchor="middle" font-family="Georgia, \'Times New Roman\', serif" font-size="26" '
    'font-weight="bold" fill="#2a160c" letter-spacing="2">TAKO</text>')

# ---------------------------------------------------------------- noren
KATA = {
    "ra": [([(26, 15), (50, 14), (74, 13)], 11, 7), ([(16, 40), (50, 39), (79, 37), (77, 51), (69, 67), (53, 82), (30, 93)], 12, 4)],
    "cho": [([(12, 50), (50, 48), (88, 47)], 12, 9)],
    "me": [([(74, 10), (66, 38), (50, 62), (30, 80), (14, 90)], 12, 4), ([(28, 34), (48, 50), (66, 66), (80, 82)], 11, 6)],
    "n": [([(20, 22), (30, 30), (40, 39)], 12, 7), ([(18, 86), (42, 76), (62, 60), (76, 44), (86, 26)], 12, 4)],
}
add('<rect x="290" y="236" width="1020" height="9" rx="4" fill="#c9a46a"/>')
for x in range(330, 1300, 120):
    add(f'<rect x="{x}" y="235" width="3" height="11" fill="#8f6c3a"/>')
for i, ch in enumerate(("ra", "cho", "me", "n")):
    x0 = 308 + i * 248
    sway = (-2, 1, -1, 2)[i]
    add(f'<g transform="rotate({sway * 0.6} {x0 + 120} 240)">',
        f'<rect x="{x0}" y="238" width="240" height="102" fill="url(#noren)"/>',
        f'<rect x="{x0}" y="238" width="240" height="102" fill="url(#norenFold)"/>',
        f'<rect x="{x0}" y="238" width="240" height="12" fill="#121b40"/>',
        f'<rect x="{x0}" y="332" width="240" height="8" fill="#141e47"/>',
        f'<path d="M{x0 + 4} 336 H{x0 + 236}" stroke="#f0e6cf" stroke-width="1.2" stroke-dasharray="5 4" opacity="0.5"/>')
    s = 0.78
    ox, oy = x0 + 120 - 50 * s, 252
    for pts, w0, w1 in KATA[ch]:
        add(f'<path d="{ribbon_shape([(ox + px * s, oy + py * s) for px, py in pts], w0 * s * 1.15, w1 * s)}" fill="#f2e8d0"/>')
    add('</g>')
add('<g transform="rotate(1.2 1172 240)">',
    '<rect x="1258" y="306" width="18" height="18" rx="2" fill="#c63a2e"/>',
    '<path d="M1262 311 h10 M1267 309 v12 M1262 318 h10" stroke="#f2e8d0" stroke-width="1.8"/>',
    '</g>')


# ---------------------------------------------------------------- lanterns
def lantern(cx, top):
    o = [f'<circle cx="{cx}" cy="{top + 80}" r="200" fill="url(#lanternGlow)"/>',
         f'<path d="M{cx} {top - 10} V{top + 6}" stroke="#1b1717" stroke-width="2.5"/>']
    body_top, body_bot = top + 12, top + 150
    cy = (body_top + body_bot) / 2
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="46" ry="{(body_bot - body_top) / 2 + 6}" fill="url(#lanternBody)"/>')
    for y in range(body_top + 6, body_bot - 2, 11):
        dy = (y - cy) / ((body_bot - body_top) / 2 + 6)
        hw_ = 46 * math.sqrt(max(0, 1 - dy * dy))
        o.append(f'<path d="M{cx - hw_:.1f} {y} Q{cx} {y + 5} {cx + hw_:.1f} {y}" stroke="#7a1414" stroke-width="1.3" fill="none" opacity="0.55"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="25" fill="#f8e6c8" opacity="0.95"/>')
    o += octo_logo(cx, cy + 2, 40, "#1b1717", "#f8e6c8")
    o.append(f'<rect x="{cx - 26}" y="{top}" width="52" height="14" rx="3" fill="#1b1717" stroke="#b8893f" stroke-width="1.5"/>')
    o.append(f'<rect x="{cx - 26}" y="{body_bot - 4}" width="52" height="14" rx="3" fill="#1b1717" stroke="#b8893f" stroke-width="1.5"/>')
    for k in range(5):
        o.append(f'<path d="M{cx - 6 + k * 3} {body_bot + 10} L{cx - 8 + k * 4} {body_bot + 40}" stroke="#e8b04a" stroke-width="1.6"/>')
    o.append(f'<ellipse cx="{cx - 16}" cy="{cy - 30}" rx="10" ry="22" fill="#fff" opacity="0.18" filter="url(#blur2)"/>')
    return o


add(lantern(214, 244), lantern(1386, 244))

# ---------------------------------------------------------------- light & atmosphere
add('<ellipse cx="800" cy="560" rx="560" ry="360" fill="url(#warm)" opacity="0.35"/>',
    '<circle cx="214" cy="324" r="120" fill="url(#lanternGlow)" opacity="0.5"/>',
    '<circle cx="1386" cy="324" r="120" fill="url(#lanternGlow)" opacity="0.5"/>',
    f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')

add('</svg>')

os.makedirs("output", exist_ok=True)
with open("output/octopus_ramen_chef.svg", "w", encoding="utf-8") as fh:
    fh.write("\n".join(svg))
print("wrote output/octopus_ramen_chef.svg", sum(len(s) for s in svg) // 1024, "KB")
