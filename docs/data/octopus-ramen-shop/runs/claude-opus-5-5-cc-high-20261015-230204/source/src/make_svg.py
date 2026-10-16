#!/usr/bin/env python3
"""Generate an SVG illustration: an octopus chef running a ramen yatai at night."""
import math
import random
import sys

W, H = 1600, 1200
INK = "#2b1622"
JP = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Yu Gothic',sans-serif"
JP_SERIF = "'Hiragino Mincho ProN','Noto Serif JP','Yu Mincho',serif"

out = []


def add(s):
    out.append(s)


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- geometry
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
    return x, y


def bez_d(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    return dx, dy


def poly_path(pts, close=True):
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return d + ("Z" if close else "")


def smooth_path(pts, close=True):
    """Catmull-Rom through points -> cubic bezier path."""
    n = len(pts)
    d = f"M{f(pts[0][0])},{f(pts[0][1])}"
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if close or i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if close or i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    return d + ("Z" if close else "")


# ---------------------------------------------------------------- tentacle
def tentacle(segs, w0, w1, side=1, n=26, sucker_every=2):
    """segs: list of cubic bezier control-point tuples. Draws a tapered arm with suckers."""
    centre, normals = [], []
    for si, (p0, p1, p2, p3) in enumerate(segs):
        for i in range(n + 1):
            if si > 0 and i == 0:
                continue
            t = i / n
            x, y = bez(p0, p1, p2, p3, t)
            dx, dy = bez_d(p0, p1, p2, p3, t)
            L = math.hypot(dx, dy) or 1
            centre.append((x, y))
            normals.append((-dy / L, dx / L))
    m = len(centre)
    widths = [w0 + (w1 - w0) * (i / (m - 1)) ** 0.85 for i in range(m)]
    left = [(c[0] + nn[0] * w / 2, c[1] + nn[1] * w / 2) for c, nn, w in zip(centre, normals, widths)]
    right = [(c[0] - nn[0] * w / 2, c[1] - nn[1] * w / 2) for c, nn, w in zip(centre, normals, widths)]
    # rounded tip
    tip = centre[-1]
    tx, ty = bez_d(*segs[-1], 1.0)
    L = math.hypot(tx, ty) or 1
    tipc = (tip[0] + tx / L * widths[-1] * 0.5, tip[1] + ty / L * widths[-1] * 0.5)
    outline = left + [tipc] + right[::-1]
    d = poly_path(outline)
    add(f'<path d="{d}" fill="url(#skin)" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    # soft highlight along the top edge
    hl = [(c[0] - nn[0] * side * w * 0.22, c[1] - nn[1] * side * w * 0.22)
          for c, nn, w in zip(centre, normals, widths)][2:-3]
    add(f'<path d="{poly_path(hl, False)}" fill="none" stroke="#ffb3a1" stroke-opacity="0.55" '
        f'stroke-width="{f(max(3, w0 * 0.12))}" stroke-linecap="round"/>')
    # sucker band (paler underside)
    band = [(c[0] + nn[0] * side * w * 0.5, c[1] + nn[1] * side * w * 0.5)
            for c, nn, w in zip(centre, normals, widths)]
    inner = [(c[0] + nn[0] * side * w * 0.18, c[1] + nn[1] * side * w * 0.18)
             for c, nn, w in zip(centre, normals, widths)]
    add(f'<path d="{poly_path(band + inner[::-1])}" fill="#f6b39a" opacity="0.85"/>')
    for i in range(3, m - 2, sucker_every):
        c, nn, w = centre[i], normals[i], widths[i]
        r = w * 0.17
        if r < 2.2:
            continue
        sx = c[0] + nn[0] * side * w * 0.33
        sy = c[1] + nn[1] * side * w * 0.33
        add(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(r)}" fill="#ffd9c7" stroke="#c4566a" stroke-width="{f(max(1, r * 0.35))}"/>')
        add(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(r * 0.38)}" fill="#e08a8f"/>')


# ---------------------------------------------------------------- props
def steam(x, y, h=160, delay=0.0, scale=1.0, wobble=22):
    for k, dx in enumerate((-22 * scale, 0, 22 * scale)):
        pts = []
        for i in range(7):
            t = i / 6
            pts.append((x + dx + math.sin(t * math.pi * 2 + k * 1.7) * wobble * scale * (0.4 + t),
                        y - t * h))
        d = smooth_path(pts, close=False)
        b = delay + k * 0.9
        add(f'<path d="{d}" fill="none" stroke="#fff6ea" stroke-width="{f(9 * scale)}" '
            f'stroke-linecap="round" opacity="0.35">'
            f'<animate attributeName="opacity" values="0.1;0.45;0.1" dur="3.2s" begin="{b:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,8;0,-14;0,8" '
            f'dur="3.2s" begin="{b:.1f}s" repeatCount="indefinite"/></path>')


def ramen_bowl(cx, top, rx, foot=True, toppings=True):
    ry = rx * 0.27
    depth = rx * 0.85
    # body
    add(f'<path d="M{f(cx - rx)},{f(top)} C{f(cx - rx)},{f(top + depth * 0.9)} {f(cx - rx * 0.45)},{f(top + depth)} '
        f'{f(cx)},{f(top + depth)} C{f(cx + rx * 0.45)},{f(top + depth)} {f(cx + rx)},{f(top + depth * 0.9)} '
        f'{f(cx + rx)},{f(top)}Z" fill="url(#bowlRed)" stroke="{INK}" stroke-width="4"/>')
    if foot:
        add(f'<path d="M{f(cx - rx * 0.36)},{f(top + depth * 0.93)} L{f(cx - rx * 0.4)},{f(top + depth + rx * 0.1)} '
            f'L{f(cx + rx * 0.4)},{f(top + depth + rx * 0.1)} L{f(cx + rx * 0.36)},{f(top + depth * 0.93)}Z" '
            f'fill="#7d1a20" stroke="{INK}" stroke-width="3.5"/>')
    # raimon (meander) band
    by = top + depth * 0.32
    pts = []
    steps = 9
    for i in range(steps):
        x0 = cx - rx * 0.86 + i * (rx * 1.72 / steps)
        s = rx * 1.72 / steps
        yy = by + abs(x0 - cx) / rx * 3
        pts.append(f"M{f(x0)},{f(yy + s * 0.25)} h{f(s * 0.7)} v{f(-s * 0.5)} h{f(-s * 0.45)} v{f(s * 0.25)} h{f(s * 0.2)}")
    add(f'<path d="{" ".join(pts)}" fill="none" stroke="#fbeee0" stroke-width="{f(max(2, rx * 0.035))}" '
        f'stroke-linejoin="round" opacity="0.9"/>')
    # rim & broth
    add(f'<ellipse cx="{f(cx)}" cy="{f(top)}" rx="{f(rx)}" ry="{f(ry)}" fill="#1c0d12" stroke="{INK}" stroke-width="4"/>')
    add(f'<ellipse cx="{f(cx)}" cy="{f(top + ry * 0.12)}" rx="{f(rx * 0.92)}" ry="{f(ry * 0.8)}" fill="url(#broth)"/>')
    if not toppings:
        return
    s = rx / 80
    # nori sheet sticking up at the back
    add(f'<path d="M{f(cx + 18 * s)},{f(top - 2 * s)} L{f(cx + 26 * s)},{f(top - 44 * s)} L{f(cx + 58 * s)},{f(top - 38 * s)} '
        f'L{f(cx + 54 * s)},{f(top + 2 * s)}Z" fill="#1f3326" stroke="{INK}" stroke-width="3"/>')
    add(f'<path d="M{f(cx + 30 * s)},{f(top - 30 * s)} L{f(cx + 50 * s)},{f(top - 27 * s)}" stroke="#3d5c45" stroke-width="2"/>')
    # noodles
    for k in range(5):
        yy = top + (k - 2) * 3.2 * s
        add(f'<path d="M{f(cx - 52 * s)},{f(yy)} q{f(8 * s)},{f(-6 * s)} {f(16 * s)},0 t{f(16 * s)},0 t{f(16 * s)},0 '
            f't{f(16 * s)},0" fill="none" stroke="#f3d27a" stroke-width="{f(3.2 * s)}" stroke-linecap="round"/>')
    # chashu
    add(f'<ellipse cx="{f(cx - 30 * s)}" cy="{f(top - 4 * s)}" rx="{f(20 * s)}" ry="{f(9 * s)}" fill="#c98a5a" stroke="#6b3a22" stroke-width="{f(3 * s)}" transform="rotate(-12 {f(cx - 30 * s)} {f(top - 4 * s)})"/>')
    # egg
    ex, ey = cx + 8 * s, top + 4 * s
    add(f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(15 * s)}" ry="{f(9 * s)}" fill="#fffaf0" stroke="#8a6a50" stroke-width="{f(1.8 * s)}"/>')
    add(f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(8 * s)}" ry="{f(5 * s)}" fill="#f29a1f"/>')
    # naruto
    nx, ny = cx + 40 * s, top + 3 * s
    add(f'<ellipse cx="{f(nx)}" cy="{f(ny)}" rx="{f(12 * s)}" ry="{f(7 * s)}" fill="#fff" stroke="#c9a" stroke-width="{f(1.5 * s)}"/>')
    add(f'<path d="M{f(nx)},{f(ny)} q{f(4 * s)},{f(-3 * s)} {f(6 * s)},0 q{f(1 * s)},{f(4 * s)} {f(-7 * s)},{f(4 * s)} '
        f'q{f(-6 * s)},0 {f(-5 * s)},{f(-5 * s)}" fill="none" stroke="#e6577e" stroke-width="{f(2 * s)}" stroke-linecap="round"/>')
    # scallions
    rnd = random.Random(int(cx))
    for _ in range(9):
        a = rnd.uniform(0, math.tau)
        rr = rnd.uniform(0.2, 0.8)
        add(f'<circle cx="{f(cx - 12 * s + math.cos(a) * rx * 0.5 * rr)}" cy="{f(top + math.sin(a) * ry * 0.55 * rr)}" '
            f'r="{f(2.6 * s)}" fill="#7dc24b" stroke="#3e7a26" stroke-width="{f(1 * s)}"/>')


# ================================================================= scene
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('<title>Octopus chef at a ramen booth</title>')
add('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0b0d2b"/><stop offset="0.55" stop-color="#2a1f55"/>
  <stop offset="0.85" stop-color="#6a3a6e"/><stop offset="1" stop-color="#b0596a"/>
</linearGradient>
<radialGradient id="moonGlow"><stop offset="0" stop-color="#fff3c9" stop-opacity="0.55"/><stop offset="1" stop-color="#fff3c9" stop-opacity="0"/></radialGradient>
<radialGradient id="warm" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb84d" stop-opacity="0.75"/><stop offset="0.5" stop-color="#ff8a3d" stop-opacity="0.25"/><stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/></radialGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a2618"/><stop offset="1" stop-color="#7a4426"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9773f"/><stop offset="1" stop-color="#8a5228"/></linearGradient>
<linearGradient id="counterTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3b27a"/><stop offset="1" stop-color="#c48a52"/></linearGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2a36"/><stop offset="1" stop-color="#211620"/></linearGradient>
<radialGradient id="skin" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#ff8e7a"/><stop offset="1" stop-color="#d9475a"/></radialGradient>
<radialGradient id="head" cx="0.38" cy="0.3" r="0.75"><stop offset="0" stop-color="#ff9d86"/><stop offset="0.6" stop-color="#ee6464"/><stop offset="1" stop-color="#c23a52"/></radialGradient>
<linearGradient id="bowlRed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8f1d24"/><stop offset="0.35" stop-color="#d8353a"/><stop offset="1" stop-color="#7e161d"/></linearGradient>
<radialGradient id="broth" cx="0.45" cy="0.4" r="0.6"><stop offset="0" stop-color="#f6c66a"/><stop offset="1" stop-color="#c9822f"/></radialGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5d6470"/><stop offset="0.3" stop-color="#d9dee6"/><stop offset="0.55" stop-color="#9aa3b0"/><stop offset="1" stop-color="#4a505b"/></linearGradient>
<linearGradient id="blade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef2f7"/><stop offset="1" stop-color="#8d96a3"/></linearGradient>
<radialGradient id="lantern" cx="0.45" cy="0.4" r="0.6"><stop offset="0" stop-color="#ffcf73"/><stop offset="0.45" stop-color="#f0533a"/><stop offset="1" stop-color="#a51f22"/></radialGradient>
<linearGradient id="noren" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2f5e"/><stop offset="1" stop-color="#27407a"/></linearGradient>
<linearGradient id="street" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2036"/><stop offset="1" stop-color="#140f1c"/></linearGradient>
<radialGradient id="pool" cx="0.5" cy="0.3" r="0.6"><stop offset="0" stop-color="#ffa64d" stop-opacity="0.45"/><stop offset="1" stop-color="#ffa64d" stop-opacity="0"/></radialGradient>
</defs>''')

rnd = random.Random(7)

# ---- sky, stars, moon
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
for _ in range(110):
    x, y = rnd.uniform(0, W), rnd.uniform(0, 620)
    r = rnd.choice((0.8, 1.1, 1.4, 2.0))
    dur = rnd.uniform(2, 5)
    add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#fff8e1" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.9;0.3;0.9" dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')
add('<circle cx="1420" cy="140" r="150" fill="url(#moonGlow)"/>')
add('<circle cx="1420" cy="140" r="56" fill="#fff1c4"/>')
add('<circle cx="1402" cy="128" r="10" fill="#ecd9a2" opacity="0.7"/><circle cx="1440" cy="160" r="7" fill="#ecd9a2" opacity="0.7"/>'
    '<circle cx="1436" cy="118" r="5" fill="#ecd9a2" opacity="0.6"/>')

# ---- city silhouettes
def buildings(base, color, win, count, hmin, hmax, seed):
    r = random.Random(seed)
    x = -20
    while x < W:
        bw = r.uniform(70, 150)
        top = base - r.uniform(hmin, hmax)
        add(f'<rect x="{f(x)}" y="{f(top)}" width="{f(bw)}" height="{f(base - top + 400)}" fill="{color}"/>')
        if r.random() < 0.3:
            add(f'<rect x="{f(x + bw * 0.3)}" y="{f(top - 24)}" width="{f(bw * 0.25)}" height="26" fill="{color}"/>')
        for wy in range(int(top + 18), int(base - 10), 28):
            for wx in range(int(x + 12), int(x + bw - 18), 24):
                if r.random() < win:
                    c = r.choice(("#ffd77a", "#ffc25e", "#ffe9a8", "#9fd3ff"))
                    add(f'<rect x="{wx}" y="{wy}" width="11" height="15" fill="{c}" opacity="{r.uniform(0.45, 0.9):.2f}"/>')
        x += bw + r.uniform(-5, 8)

buildings(1000, "#2a2148", 0.18, 0, 380, 700, 3)
buildings(1000, "#1c1634", 0.25, 0, 180, 420, 11)

# ---- street
add('<rect x="0" y="990" width="1600" height="210" fill="url(#street)"/>')
for row, y in enumerate(range(1010, 1200, 26)):
    off = (row % 2) * 30
    for x in range(-60 + off, W, 60):
        add(f'<rect x="{x + 3}" y="{y + 3}" width="54" height="20" rx="8" fill="#3a2d47" opacity="{0.25 + (y - 1000) / 900:.2f}"/>')
add('<clipPath id="streetClip"><rect x="0" y="990" width="1600" height="210"/></clipPath>')
add('<ellipse cx="800" cy="1010" rx="760" ry="190" fill="url(#pool)" clip-path="url(#streetClip)"/>')

# ---- booth: back wall & interior
add('<rect x="320" y="290" width="960" height="500" fill="url(#wall)"/>')
for x in range(330, 1280, 48):
    add(f'<line x1="{x}" y1="300" x2="{x}" y2="790" stroke="#3a1e12" stroke-width="2" opacity="0.6"/>')
add('<ellipse cx="800" cy="600" rx="420" ry="260" fill="url(#warm)" opacity="0.8"/>')

# menu board (left)
add(f'<rect x="352" y="388" width="232" height="104" rx="6" fill="#2a1a12" stroke="#c48a52" stroke-width="5"/>')
menu = [("醤油らーめん", "¥800"), ("味噌らーめん", "¥850"), ("たこ焼き", "¥500")]
for i, (a, b) in enumerate(menu):
    y = 420 + i * 29
    add(f'<text x="368" y="{y}" font-family="{JP}" font-size="20" fill="#fbe9c8">{a}</text>')
    add(f'<text x="570" y="{y}" font-family="{JP}" font-size="18" fill="#ffcf73" text-anchor="end">{b}</text>')

# shelf (left) with jars, sake bottle and a maneki-neko
add(f'<rect x="336" y="562" width="260" height="14" fill="#a8693a" stroke="{INK}" stroke-width="3"/>')
# maneki-neko
add(f'<g stroke="{INK}" stroke-width="3">'
    '<ellipse cx="380" cy="540" rx="22" ry="24" fill="#fffaf2"/>'
    '<circle cx="380" cy="508" r="18" fill="#fffaf2"/>'
    '<path d="M366,496 l-2,-14 l10,8Z M394,496 l2,-14 l-10,8Z" fill="#fffaf2" stroke-linejoin="round"/>'
    '<path d="M398,530 q16,-8 12,-34" fill="none" stroke-width="9" stroke-linecap="round"/>'
    '<path d="M398,530 q16,-8 12,-34" fill="none" stroke="#fffaf2" stroke-width="4" stroke-linecap="round"/>'
    '<circle cx="380" cy="545" r="7" fill="#f2c14e" stroke-width="2"/>'
    '</g>')
add('<path d="M372,508 q3,-3 6,0 M383,508 q3,-3 6,0" stroke="#2b1622" stroke-width="2" fill="none"/>'
    '<path d="M366,526 h28" stroke="#d9363e" stroke-width="4"/>')
# jars & bottles
add(f'<g stroke="{INK}" stroke-width="3">'
    '<rect x="420" y="520" width="40" height="42" rx="8" fill="#d9a35b"/><rect x="424" y="512" width="32" height="10" fill="#6b3a22"/>'
    '<rect x="468" y="528" width="34" height="34" rx="7" fill="#7fa36b"/><rect x="471" y="521" width="28" height="9" fill="#6b3a22"/>'
    '<path d="M520,562 v-44 q0,-10 8,-14 v-18 h12 v18 q8,4 8,14 v44Z" fill="#f2efe4"/>'
    '<path d="M560,562 v-30 q0,-8 6,-10 v-10 h10 v10 q6,2 6,10 v30Z" fill="#3d6b9c"/>'
    '</g>')
add(f'<text x="534" y="545" font-family="{JP_SERIF}" font-size="18" fill="#b52a2f" text-anchor="middle">酒</text>')

# hanging wooden tags (right)
tags = ["醤油", "味噌", "塩", "豚骨", "餃子"]
for i, t in enumerate(tags):
    x = 1078 + i * 30
    add(f'<line x1="{x + 13}" y1="378" x2="{x + 13}" y2="390" stroke="#2b1622" stroke-width="2"/>')
    add(f'<rect x="{x}" y="388" width="27" height="98" rx="3" fill="#f1d7a8" stroke="{INK}" stroke-width="2.5"/>')
    chars = list(t)
    for j, ch in enumerate(chars):
        add(f'<text x="{x + 13.5}" y="{414 + j * 24}" font-family="{JP_SERIF}" font-size="20" font-weight="bold" '
            f'fill="#2b1622" text-anchor="middle">{ch}</text>')
    add(f'<text x="{x + 13.5}" y="476" font-family="{JP}" font-size="8" fill="#b52a2f" text-anchor="middle">¥{[800, 850, 750, 900, 450][i]}</text>')
add('<line x1="1068" y1="378" x2="1232" y2="378" stroke="#6b3a22" stroke-width="5" stroke-linecap="round"/>')

# ---- stock pot (back counter, left)
add(f'<path d="M372,690 L372,782 Q450,800 528,782 L528,690Z" fill="url(#steel)" stroke="{INK}" stroke-width="4"/>')
add(f'<path d="M372,720 Q450,736 528,720" fill="none" stroke="#4a505b" stroke-width="3" opacity="0.6"/>')
add(f'<rect x="352" y="702" width="22" height="12" rx="5" fill="#5d6470" stroke="{INK}" stroke-width="3"/>')
add(f'<rect x="526" y="702" width="22" height="12" rx="5" fill="#5d6470" stroke="{INK}" stroke-width="3"/>')
add(f'<ellipse cx="450" cy="690" rx="80" ry="18" fill="#d4dae2" stroke="{INK}" stroke-width="4"/>')
add('<ellipse cx="450" cy="692" rx="70" ry="13" fill="#b9762f"/>')
add('<ellipse cx="438" cy="690" rx="40" ry="6" fill="#e5a352" opacity="0.7"/>')
# ladle handle (dips into pot)
add(f'<path d="M590,648 L470,700" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
    '<path d="M590,648 L470,700" stroke="#c9ced6" stroke-width="6" stroke-linecap="round"/>')
add('<ellipse cx="472" cy="698" rx="20" ry="6" fill="#9a5a24" opacity="0.8"/>')

# ---- counter top & front
add(f'<path d="M290,782 L1310,782 L1322,812 L278,812Z" fill="url(#counterTop)" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<rect x="300" y="812" width="1000" height="196" fill="url(#wood)" stroke="{INK}" stroke-width="4"/>')
for x in range(350, 1300, 50):
    add(f'<line x1="{x}" y1="816" x2="{x}" y2="1004" stroke="#6b3a1c" stroke-width="2.5" opacity="0.7"/>')
add(f'<rect x="300" y="962" width="1000" height="46" fill="#5c3418" stroke="{INK}" stroke-width="4"/>')
# little "open" sign on counter front
add(f'<line x1="1180" y1="826" x2="1170" y2="846" stroke="{INK}" stroke-width="2"/><line x1="1180" y1="826" x2="1190" y2="846" stroke="{INK}" stroke-width="2"/>'
    f'<circle cx="1180" cy="824" r="4" fill="#d9a35b" stroke="{INK}" stroke-width="2"/>'
    f'<rect x="1140" y="846" width="80" height="40" rx="5" fill="#fbf1dc" stroke="{INK}" stroke-width="3"/>'
    f'<text x="1180" y="874" font-family="{JP_SERIF}" font-size="22" font-weight="bold" fill="#b52a2f" text-anchor="middle">営業中</text>')

# ---- items on counter
# noodle bowl being filled (left of centre)
ramen_bowl(628, 762, 62, toppings=False)
# cutting board with scallions
add(f'<path d="M1060,772 L1250,772 L1258,792 L1052,792Z" fill="#f0d3a0" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
    f'<rect x="1052" y="792" width="206" height="10" fill="#c99a62" stroke="{INK}" stroke-width="3"/>')
for i in range(16):
    x = 1075 + i * 6.5 + (i % 3)
    add(f'<ellipse cx="{f(x)}" cy="{780 + (i % 2) * 3}" rx="3.4" ry="2.4" fill="#86c95a" stroke="#3e7a26" stroke-width="1.2"/>')
add(f'<path d="M1176,785 L1240,778" stroke="#3e7a26" stroke-width="9" stroke-linecap="round"/>'
    f'<path d="M1176,785 L1240,778" stroke="#8fd16a" stroke-width="5" stroke-linecap="round"/>'
    f'<path d="M1240,778 l12,-4 M1240,778 l13,2 M1240,778 l10,6" stroke="#f4f0dc" stroke-width="2"/>')
# chopstick cup & condiments near the right of the board
add(f'<g stroke="{INK}" stroke-width="3">'
    '<rect x="1262" y="742" width="28" height="42" rx="4" fill="#2f4a3a"/>'
    '<path d="M1268,742 l-6,-34 M1274,742 l-2,-38 M1280,742 l4,-36 M1285,742 l9,-30" stroke="#d8b07a" stroke-width="4"/>'
    '</g>')

# ---- tentacles (drawn before the head so their roots hide under it)
# 1 ladle (left)
tentacle([((752, 738), (650, 790), (560, 760), (596, 650))], 50, 13, side=1)
# 2 chopsticks lifting noodles
tentacle([((770, 750), (720, 800), (650, 740), (688, 640))], 46, 12, side=1)
# 3 wave (right, high)
tentacle([((842, 735), (1010, 712), (1190, 660), (1172, 540)),
          ((1172, 540), (1165, 488), (1110, 482), (1118, 520))], 46, 8, side=1)
# 4 presenting a bowl
tentacle([((838, 742), (930, 752), (1000, 720), (986, 642))], 48, 16, side=-1)
# 5 knife
tentacle([((850, 760), (960, 812), (1060, 800), (1112, 744))], 48, 14, side=1)

# chopsticks + noodles (over tentacle tip)
noodles = []
for k in range(6):
    x0 = 650 + k * 3.5
    pts = [(x0, 708), (x0 - 6 + k, 724), (x0 + 3 - k * 0.6, 742), (x0 - 4 + k * 1.2, 760), (630 + k * 5, 770)]
    noodles.append(smooth_path(pts, close=False))
for d in noodles:
    add(f'<path d="{d}" fill="none" stroke="#9c7a2e" stroke-width="5" stroke-linecap="round"/>')
for d in noodles:
    add(f'<path d="{d}" fill="none" stroke="#f6dc8a" stroke-width="3" stroke-linecap="round"/>')
add(f'<path d="M700,618 L652,712 M712,624 L662,714" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
    f'<path d="M700,618 L652,712 M712,624 L662,714" stroke="#e6b77a" stroke-width="4" stroke-linecap="round"/>')

# knife
add(f'<g transform="rotate(14 1118 744)">'
    f'<rect x="1094" y="736" width="46" height="16" rx="5" fill="#5a3320" stroke="{INK}" stroke-width="3"/>'
    f'<rect x="1138" y="738" width="6" height="12" fill="#c9ced6" stroke="{INK}" stroke-width="2"/>'
    f'<path d="M1144,734 L1224,734 Q1232,734 1232,744 L1232,770 L1144,764Z" fill="url(#blade)" stroke="{INK}" stroke-width="3.5"/>'
    f'<path d="M1150,740 L1222,740" stroke="#fff" stroke-width="2" opacity="0.7"/>'
    f'</g>')
# chop marks
add('<path d="M1196,758 l8,-6 M1208,762 l9,-5" stroke="#fff6d8" stroke-width="3" stroke-linecap="round"/>')

# ---- octopus head
add('<g id="octopus-head">')
head = [(800, 452), (900, 470), (958, 560), (962, 660), (920, 740), (860, 776), (800, 782),
        (740, 776), (680, 740), (638, 660), (642, 560), (700, 470)]
add(f'<path d="{smooth_path(head)}" fill="url(#head)" stroke="{INK}" stroke-width="5"/>')
# spots
for x, y, r in [(690, 560, 9), (712, 532, 5), (905, 545, 8), (926, 580, 5), (668, 600, 4), (930, 700, 6)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#c23a52" opacity="0.45"/>')
add('<path d="M700,510 q30,-30 70,-38" fill="none" stroke="#ffd0bf" stroke-width="10" stroke-linecap="round" opacity="0.55"/>')
# eyes
for ex in (742, 858):
    add(f'<ellipse cx="{ex}" cy="618" rx="34" ry="40" fill="#fffdf8" stroke="{INK}" stroke-width="4.5"/>')
    add(f'<ellipse cx="{ex + 4}" cy="626" rx="20" ry="24" fill="#24141c"/>')
    add(f'<circle cx="{ex + 11}" cy="614" r="7.5" fill="#fff"/><circle cx="{ex - 2}" cy="636" r="3.5" fill="#fff"/>')
    add(f'<path d="M{ex - 26},{570} q26,-16 52,-4" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
# cheeks & smile
add('<ellipse cx="692" cy="684" rx="24" ry="13" fill="#ff7f8f" opacity="0.65"/>'
    '<ellipse cx="908" cy="684" rx="24" ry="13" fill="#ff7f8f" opacity="0.65"/>')
add(f'<path d="M762,682 Q800,730 838,682 Q800,700 762,682Z" fill="#7a1f33" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
add('<path d="M782,704 Q800,694 818,704 Q800,716 782,704Z" fill="#ff8a96"/>')
# neckerchief
add(f'<path d="M716,742 Q800,772 884,742 L888,762 Q800,796 712,762Z" fill="#d9363e" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M800,770 L774,812 L800,800 L826,814Z" fill="#c22a33" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<circle cx="800" cy="772" r="11" fill="#e8484f" stroke="{INK}" stroke-width="4"/>')
for x in range(730, 880, 22):
    add(f'<circle cx="{x}" cy="{758 + abs(x - 800) * -0.12 + 6}" r="3" fill="#fff" opacity="0.8"/>')
# chef hat (toque)
add(f'<g stroke="{INK}" stroke-width="4.5" stroke-linejoin="round">'
    '<path d="M708,488 C690,440 700,398 740,396 C746,360 790,350 808,372 C830,344 880,356 878,398 '
    'C914,402 916,452 892,488Z" fill="#fffdf7"/>'
    '<path d="M702,486 Q800,462 898,486 L904,526 Q800,500 696,526Z" fill="#f4f1ea"/>'
    '</g>')
add('<path d="M760,404 q8,30 4,62 M840,400 q-8,30 -4,62" fill="none" stroke="#d9d3c6" stroke-width="3"/>'
    '<path d="M738,410 q10,-12 26,-10" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>')
add('</g>')

# ---- tentacles that sit in front (draped over the counter edge)
tentacle([((770, 772), (760, 840), (690, 860), (690, 912)),
          ((690, 912), (690, 948), (736, 950), (730, 918))], 50, 9, side=-1)
tentacle([((830, 772), (846, 846), (920, 850), (918, 900)),
          ((918, 900), (916, 938), (870, 944), (874, 912))], 50, 9, side=1)

# ---- presented bowl (over tentacle 4)
ramen_bowl(986, 590, 76)

# ---- steam
steam(450, 672, 190, 0.0, 1.2)
steam(628, 744, 120, 0.6, 0.8)
steam(986, 560, 190, 1.2, 1.1)

# ---- roof, sign, posts, noren
add(f'<rect x="300" y="290" width="28" height="720" fill="#8a5228" stroke="{INK}" stroke-width="4"/>')
add(f'<rect x="1272" y="290" width="28" height="720" fill="#8a5228" stroke="{INK}" stroke-width="4"/>')
add(f'<path d="M232,250 L1368,250 L1300,168 L300,168Z" fill="url(#roof)" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
for i in range(1, 18):
    x0 = 300 + i * 1000 / 18
    x1 = 232 + i * 1136 / 18
    add(f'<line x1="{f(x0)}" y1="170" x2="{f(x1)}" y2="248" stroke="#54404f" stroke-width="3"/>')
add(f'<rect x="250" y="248" width="1100" height="46" fill="#b0402f" stroke="{INK}" stroke-width="5"/>')
add(f'<rect x="250" y="290" width="1100" height="10" fill="#7a2a20" stroke="{INK}" stroke-width="3"/>')
# string of bulbs along the fascia
for i in range(22):
    x = 268 + i * 50
    y = 272 + math.sin(i * 0.9) * 2
    add(f'<circle cx="{x}" cy="{f(y)}" r="12" fill="#ffd77a" opacity="0.25"/>'
        f'<circle cx="{x}" cy="{f(y)}" r="5.5" fill="#fff0b8" stroke="#7a2a20" stroke-width="1.5">'
        f'<animate attributeName="opacity" values="1;0.6;1" dur="{1.6 + (i % 4) * 0.35:.2f}s" repeatCount="indefinite"/></circle>')
# rooftop sign
add(f'<rect x="640" y="70" width="320" height="104" rx="10" fill="#fbf1dc" stroke="{INK}" stroke-width="6"/>')
add(f'<rect x="652" y="82" width="296" height="80" rx="6" fill="none" stroke="#b52a2f" stroke-width="4"/>')
add(f'<rect x="690" y="166" width="14" height="12" fill="#5c3418"/><rect x="896" y="166" width="14" height="12" fill="#5c3418"/>')
add(f'<text x="800" y="148" font-family="{JP_SERIF}" font-size="64" font-weight="bold" fill="#2b1622" text-anchor="middle" letter-spacing="10">たこ麺</text>')
# noren curtains
labels = ["ラ", "ー", "メ", "ン"]
pw = 930 / 4
for i, ch in enumerate(labels):
    x = 335 + i * pw
    sway = (1 if i % 2 else -1) * 3
    add(f'<path d="M{f(x + 4)},300 L{f(x + pw - 4)},300 L{f(x + pw - 4 + sway)},356 Q{f(x + pw / 2)},362 {f(x + 4 + sway)},356Z" '
        f'fill="url(#noren)" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
    add(f'<text x="{f(x + pw / 2)}" y="345" font-family="{JP}" font-size="38" font-weight="bold" fill="#f6f1e6" text-anchor="middle">{ch}</text>')
# small white wave motif along the noren hem
add(f'<path d="M335,304 H1265" stroke="#a8b8d8" stroke-width="2" opacity="0.6"/>')

# ---- paper lanterns
def lantern(cx, top, txt):
    add(f'<circle cx="{cx}" cy="{top + 72}" r="150" fill="url(#warm)"/>')
    add(f'<line x1="{cx}" y1="{top - 10}" x2="{cx}" y2="{top + 4}" stroke="{INK}" stroke-width="3"/>')
    add(f'<rect x="{cx - 24}" y="{top}" width="48" height="12" rx="3" fill="#2b1622"/>')
    add(f'<ellipse cx="{cx}" cy="{top + 72}" rx="50" ry="62" fill="url(#lantern)" stroke="{INK}" stroke-width="4">'
        f'<animate attributeName="opacity" values="1;0.88;1;0.94;1" dur="2.7s" repeatCount="indefinite"/></ellipse>')
    for k in (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75):
        y = top + 72 + k * 62
        rx = 50 * math.sqrt(1 - k * k)
        add(f'<path d="M{f(cx - rx)},{f(y)} Q{cx},{f(y + 6)} {f(cx + rx)},{f(y)}" fill="none" stroke="#8a1c1e" stroke-width="1.8" opacity="0.7"/>')
    add(f'<rect x="{cx - 24}" y="{top + 130}" width="48" height="12" rx="3" fill="#2b1622"/>')
    add(f'<path d="M{cx - 8},{top + 142} v20 M{cx},{top + 142} v24 M{cx + 8},{top + 142} v20" stroke="#f2c14e" stroke-width="3"/>')
    add(f'<text x="{cx}" y="{top + 88}" font-family="{JP_SERIF}" font-size="40" font-weight="bold" fill="#2b1622" text-anchor="middle">{txt}</text>')

lantern(314, 306, "麺")
lantern(1286, 306, "蛸")

# ---- wheel and stools
add(f'<circle cx="252" cy="958" r="62" fill="none" stroke="{INK}" stroke-width="16"/>'
    f'<circle cx="252" cy="958" r="62" fill="none" stroke="#8a5228" stroke-width="10"/>')
for a in range(0, 360, 45):
    r = math.radians(a)
    add(f'<line x1="252" y1="958" x2="{f(252 + math.cos(r) * 58)}" y2="{f(958 + math.sin(r) * 58)}" stroke="#6b3a1c" stroke-width="6"/>')
add(f'<circle cx="252" cy="958" r="12" fill="#5c3418" stroke="{INK}" stroke-width="3"/>')

for sx in (520, 800, 1080):
    add(f'<ellipse cx="{sx}" cy="1166" rx="70" ry="14" fill="#000" opacity="0.3"/>')
    add(f'<path d="M{sx - 40},1036 L{sx - 54},1160 M{sx + 40},1036 L{sx + 54},1160 M{sx - 14},1040 L{sx - 18},1166 M{sx + 14},1040 L{sx + 18},1166" '
        f'stroke="{INK}" stroke-width="10" stroke-linecap="round"/>')
    add(f'<path d="M{sx - 40},1036 L{sx - 54},1160 M{sx + 40},1036 L{sx + 54},1160 M{sx - 14},1040 L{sx - 18},1166 M{sx + 14},1040 L{sx + 18},1166" '
        f'stroke="#8a5228" stroke-width="5" stroke-linecap="round"/>')
    add(f'<path d="M{sx - 48},1104 L{sx + 48},1104" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
        f'<path d="M{sx - 48},1104 L{sx + 48},1104" stroke="#8a5228" stroke-width="4" stroke-linecap="round"/>')
    add(f'<path d="M{sx - 70},1022 L{sx - 70},1036 A70,18 0 0 0 {sx + 70},1036 L{sx + 70},1022Z" fill="#8f1d24" stroke="{INK}" stroke-width="4"/>')
    add(f'<ellipse cx="{sx}" cy="1022" rx="70" ry="18" fill="#d8353a" stroke="{INK}" stroke-width="4"/>')
    add(f'<ellipse cx="{sx - 14}" cy="1018" rx="34" ry="6" fill="#ff7a6e" opacity="0.6"/>')

add('</svg>')

path = sys.argv[1] if len(sys.argv) > 1 else "output/octopus_chef_ramen_booth.svg"
with open(path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))
print(path)
