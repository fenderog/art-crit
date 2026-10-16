#!/usr/bin/env python3
"""Octopus chef at a ramen booth -> ../output/octopus-ramen-chef.svg

Everything is drawn procedurally: tentacles are tapered ribbons built from
Catmull-Rom splines, so they can be re-posed by editing a few control points.
"""
import math
import os

W, H = 1200, 900
OUT = os.path.join(os.path.dirname(__file__), "..", "output", "octopus-ramen-chef.svg")


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
def catmull(pts, seg=24):
    P = [pts[0]] + list(pts) + [pts[-1]]
    res = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(seg):
            t = k / seg
            t2, t3 = t * t, t * t * t
            res.append(tuple(
                0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                       + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                for j in (0, 1)))
    res.append(tuple(pts[-1]))
    return res


def resample(S, step):
    cum = [0.0]
    for a, b in zip(S, S[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    total = cum[-1]
    n = max(2, int(total / step))
    out, j = [], 0
    for i in range(n + 1):
        d = total * i / n
        while j < len(cum) - 2 and cum[j + 1] < d:
            j += 1
        seg = cum[j + 1] - cum[j] or 1e-9
        u = (d - cum[j]) / seg
        out.append((S[j][0] + (S[j + 1][0] - S[j][0]) * u,
                    S[j][1] + (S[j + 1][1] - S[j][1]) * u))
    return out


LIGHT = (-0.45, -0.89)  # light comes from upper left


class Arm:
    def __init__(self, pts, w0, w1, power=0.85, step=3.0):
        self.S = resample(catmull(pts), step)
        n = len(self.S)
        self.n = n
        self.T, self.N = [], []
        for i in range(n):
            a = self.S[max(0, i - 1)]
            b = self.S[min(n - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            self.T.append((dx / L, dy / L))
            self.N.append((-dy / L, dx / L))
        self.w = [w1 + (w0 - w1) * (1 - i / (n - 1)) ** power for i in range(n)]

    def outline(self):
        S, N, w = self.S, self.N, self.w
        left = [(S[i][0] + N[i][0] * w[i] / 2, S[i][1] + N[i][1] * w[i] / 2) for i in range(self.n)]
        right = [(S[i][0] - N[i][0] * w[i] / 2, S[i][1] - N[i][1] * w[i] / 2) for i in range(self.n)]
        cap = []
        e = self.n - 1
        r = w[e] / 2
        a0 = math.atan2(N[e][1], N[e][0])
        # sweep from +normal through tangent to -normal
        ta = math.atan2(self.T[e][1], self.T[e][0])
        da = ((ta - a0 + math.pi) % (2 * math.pi)) - math.pi
        for k in range(1, 12):
            a = a0 + da * k / 12 * 2
            cap.append((S[e][0] + math.cos(a) * r, S[e][1] + math.sin(a) * r))
        pts = left + cap + right[::-1]
        return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"

    def ribbon(self, t0, t1, off_fn, wrel):
        """polygon following the arm; off_fn(i)-> offset in units of w."""
        i0, i1 = int(t0 * (self.n - 1)), int(t1 * (self.n - 1))
        A, B = [], []
        m = max(1, i1 - i0)
        for i in range(i0, i1 + 1):
            u = (i - i0) / m
            taper = min(1.0, u * 6, (1 - u) * 6)
            taper = math.sin(taper * math.pi / 2)
            w = self.w[i]
            o = off_fn(i) * w
            hw = wrel * w * taper / 2
            cx = self.S[i][0] + self.N[i][0] * o
            cy = self.S[i][1] + self.N[i][1] * o
            A.append((cx + self.N[i][0] * hw, cy + self.N[i][1] * hw))
            B.append((cx - self.N[i][0] * hw, cy - self.N[i][1] * hw))
        pts = A + B[::-1]
        return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"

    def lit(self, i):
        return self.N[i][0] * LIGHT[0] + self.N[i][1] * LIGHT[1]

    def suckers(self, t0, t1, side, off=0.18, rel=0.2, gap=1.25):
        i0, i1 = int(t0 * (self.n - 1)), int(t1 * (self.n - 1))
        out = []
        acc = 0.0
        last = None
        for i in range(i0, i1 + 1):
            w = self.w[i]
            r = rel * w
            if last is not None:
                acc += math.dist(self.S[i], self.S[last])
            if last is None or acc >= 2 * r * gap:
                acc = 0.0
                last = i
                x = self.S[i][0] + self.N[i][0] * side * off * w
                y = self.S[i][1] + self.N[i][1] * side * off * w
                out.append(
                    f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#ffd9e3"/>'
                    f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 0.58)}" fill="#e87fa2"/>')
        return "".join(out)

    def draw(self, sucker=None, shade=True, hilite=True, base="url(#armGrad)", stroke="#8a2a5a"):
        s = f'<path d="{self.outline()}" fill="{base}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
        if shade:
            s += f'<path d="{self.ribbon(0.03, 0.97, lambda i: -0.30 * self.lit(i), 0.34)}" fill="#7a1f4f" opacity=".22"/>'
        if hilite:
            s += f'<path d="{self.ribbon(0.04, 0.92, lambda i: 0.27 * self.lit(i), 0.15)}" fill="#ffd0dc" opacity=".42"/>'
        if sucker:
            s += self.suckers(*sucker)
        return s


# --------------------------------------------------------------------------
# glyphs (stroke art) - katakana ラーメン and Latin RAMEN
# --------------------------------------------------------------------------
KANA = {
    "ra": ["M27 16H73", "M16 44H84Q80 74 30 92"],
    "bar": ["M14 50H86"],
    "barv": ["M50 8V92"],
    "me": ["M68 12Q62 56 22 90", "M24 38Q52 54 84 88"],
    "n": ["M26 24L42 38", "M20 84Q66 74 82 28"],
}
LATIN = {
    "R": ["M8 100V0H36Q58 0 58 26Q58 52 36 52H8", "M34 52L60 100"],
    "A": ["M2 100L32 0L62 100", "M12 66H52"],
    "M": ["M6 100V0L32 60L58 0V100"],
    "E": ["M56 0H8V100H56", "M8 50H46"],
    "N": ["M8 100V0L56 100V0"],
    "O": ["M32 0C52 0 60 25 60 50S52 100 32 100 4 75 4 50 12 0 32 0Z"],
    "P": ["M8 100V0H36Q58 0 58 26Q58 52 36 52H8"],
}


def glyph(table, name, x, y, size, color, sw):
    s = size / 100
    paths = "".join(f'<path d="{d}"/>' for d in table[name])
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s:.3f})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / s:.2f}" stroke-linecap="round" stroke-linejoin="round">{paths}</g>')


# --------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------
def steam(x, y, h, wob, width=16, opacity=0.32, dur=5.0, begin=0.0, rise=16):
    d = (f"M{f(x)} {f(y)}C{f(x - wob)} {f(y - h * .25)} {f(x + wob)} {f(y - h * .5)} {f(x)} {f(y - h * .72)}"
         f"S{f(x - wob)} {f(y - h * .95)} {f(x + wob * .3)} {f(y - h)}")
    return (f'<g filter="url(#blur5)" opacity="{opacity}">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{f(wob * .6)} -{rise};0 0" '
            f'dur="{dur}s" begin="{-begin}s" repeatCount="indefinite"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{width}" stroke-linecap="round"/></g>')


def wavy(x0, y0, y1, amp, k, phase, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        a = amp * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.4)))
        pts.append((x0 + a * math.sin(k * t * 2 * math.pi + phase), y))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)


def bowl(cx, cy, uid, s=1.0, flip=False, noodle_mound=True):
    """Ramen bowl; (cx,cy) is the centre of the rim."""
    sx = -1 if flip else 1
    band_top = "".join(
        f"{'M' if i == 0 else 'L'}{f(x)} {f(19 * math.sqrt(max(0, 1 - (x / 70) ** 2)) + 6)}"
        for i, x in enumerate(range(-70, 71, 5)))
    band_bot = "".join(
        f"L{f(x)} {f(19 * math.sqrt(max(0, 1 - (x / 70) ** 2)) + 19)}" for x in range(70, -71, -5))
    squares = "".join(
        f'<rect x="{x - 3}" y="{f(19 * math.sqrt(max(0, 1 - (x / 70) ** 2)) + 9.5)}" width="6" height="6" fill="#fff" opacity=".9"/>'
        for x in range(-60, 61, 12))
    noodles = "".join(
        f'<path d="{wavy(-52 + i * 4.5 - 3, -2 + (i % 3) * 1.5, -2 + (i % 3) * 1.5, 0, 0, 0, 1)}"/>' for i in range(0))
    strands = ""
    for i in range(8):
        y = -9 + i * 2.6
        strands += (f'<path d="M-50 {f(y + 3)}Q-35 {f(y - 3)} -22 {f(y + 2)}T4 {f(y + 1)}T30 {f(y + 2)}T52 {f(y + 1)}" '
                    f'fill="none" stroke="{"#f2cf78" if i % 2 else "#e8bc5a"}" stroke-width="3.4" stroke-linecap="round"/>')
    mound = ""
    if noodle_mound:
        mound = (f'<ellipse cx="2" cy="-3" rx="48" ry="11" fill="#efc86c"/>{strands}'
                 f'<ellipse cx="2" cy="-3" rx="48" ry="11" fill="none" stroke="#c99a3d" stroke-width="1" opacity=".5"/>')
    return f'''
<g transform="translate({f(cx)} {f(cy)}) scale({f(sx * s)} {f(s)})">
  <defs>
    <clipPath id="bb-{uid}"><path d="M-70 0C-70 34 -46 58 -30 60L30 60C46 58 70 34 70 0Z"/></clipPath>
    <clipPath id="bi-{uid}"><ellipse cx="0" cy="1" rx="63" ry="16"/></clipPath>
  </defs>
  <ellipse cx="0" cy="68" rx="64" ry="12" fill="#1a0a05" opacity=".45" filter="url(#blur5)"/>
  <path d="M-30 58L-26 71Q0 75 26 71L30 58Z" fill="#d8d0c4" stroke="#bdb3a3" stroke-width="1.2"/>
  <path d="M-70 0C-70 34 -46 58 -30 60L30 60C46 58 70 34 70 0Z" fill="url(#bowlGrad)" stroke="#c9bfae" stroke-width="1.4"/>
  <g clip-path="url(#bb-{uid})">
    <path d="{band_top}{band_bot}Z" fill="#b9302e"/>
    {squares}
    <path d="M-70 40Q0 78 70 40L70 70L-70 70Z" fill="#8a7a66" opacity=".16"/>
  </g>
  <ellipse cx="0" cy="0" rx="70" ry="19" fill="#fbf7ee" stroke="#cfc5b3" stroke-width="1.4"/>
  <ellipse cx="0" cy="1" rx="63" ry="16" fill="url(#brothGrad)"/>
  <g clip-path="url(#bi-{uid})">
    {mound}
    <g>
      <ellipse cx="-33" cy="1" rx="19" ry="9" fill="#cf8d6a"/><ellipse cx="-33" cy="0" rx="15" ry="6.5" fill="#efb596"/>
      <path d="M-44 -1Q-33 3 -22 -1" stroke="#fbd8c0" stroke-width="1.6" fill="none"/>
      <ellipse cx="-12" cy="5" rx="17" ry="8" fill="#cf8d6a"/><ellipse cx="-12" cy="4" rx="13" ry="5.6" fill="#f2bf9f"/>
      <ellipse cx="29" cy="4" rx="15" ry="9" fill="#fffaf0"/><ellipse cx="29" cy="5" rx="7" ry="5" fill="#f5a41f"/>
      <ellipse cx="27" cy="3.4" rx="2.4" ry="1.5" fill="#ffd77a"/>
      <ellipse cx="49" cy="-3" rx="9" ry="6" fill="#fffaf0"/>
      <path d="M43 -3Q47 -6 50 -2T54 -3" stroke="#f08a9b" stroke-width="1.6" fill="none"/>
      <g fill="#57b44f"><circle cx="-4" cy="-6" r="2.2"/><circle cx="8" cy="-8" r="2"/><circle cx="14" cy="0" r="2.3"/><circle cx="-24" cy="-8" r="2"/><circle cx="40" cy="8" r="2"/><circle cx="-50" cy="4" r="2.2"/><circle cx="-1" cy="9" r="2"/></g>
    </g>
  </g>
  <path d="M-56 -8L-34 -34L-7 -29L-28 -1Z" fill="#1d3b2c" stroke="#2f5a42" stroke-width="1.2"/>
  <path d="M-48 -10L-31 -29M-37 -10L-22 -26" stroke="#3b6b50" stroke-width="1" opacity=".7"/>
</g>'''


def ladle(cx, cy, rot, handle_len=170):
    """cup centred at cx,cy (cup opening faces +y up after rotation)."""
    return f'''
<g transform="translate({f(cx)} {f(cy)}) rotate({rot})">
  <rect x="26" y="-5" width="{handle_len}" height="10" rx="5" fill="#7b4a2a"/>
  <rect x="26" y="-5" width="{handle_len}" height="4" rx="2" fill="#a56a3e"/>
  <circle cx="{handle_len + 26}" cy="0" r="7" fill="#7b4a2a"/>
  <path d="M-36 0A36 36 0 0 0 36 0Z" fill="url(#steelV)" stroke="#7d8793" stroke-width="1.5"/>
  <ellipse cx="0" cy="0" rx="36" ry="9" fill="#d9a448" stroke="#8d949c" stroke-width="2"/>
  <ellipse cx="-4" cy="-1" rx="26" ry="5" fill="#f0c36a" opacity=".8"/>
  <path d="M-26 12Q-18 26 -4 28" stroke="#fff" stroke-width="3" fill="none" opacity=".5" stroke-linecap="round"/>
</g>'''


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------
def build():
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    a('<title>Octopus chef at a ramen booth</title>')
    a('<desc>A cheerful pink octopus in a chef\'s toque and apron runs a night-time ramen stall: one arm ladles broth, '
      'one lifts noodles with chopsticks, one waves hello, and four more drape over the counter.</desc>')

    # ---------------- defs ----------------
    a('''<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0b1230"/><stop offset=".55" stop-color="#2a2160"/><stop offset="1" stop-color="#5a2f6e"/>
  </linearGradient>
  <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2b1712"/><stop offset=".6" stop-color="#4a2a1b"/><stop offset="1" stop-color="#5a3320"/>
  </linearGradient>
  <radialGradient id="halo" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#ff9d4a" stop-opacity=".55"/><stop offset=".55" stop-color="#d9622a" stop-opacity=".22"/><stop offset="1" stop-color="#d9622a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lampGlow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#ffb24f" stop-opacity=".85"/><stop offset=".4" stop-color="#ff8a3a" stop-opacity=".35"/><stop offset="1" stop-color="#ff7a30" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="armGrad" gradientUnits="userSpaceOnUse" x1="0" y1="330" x2="0" y2="880">
    <stop offset="0" stop-color="#ec7a9d"/><stop offset=".45" stop-color="#d4547f"/><stop offset="1" stop-color="#b03d6c"/>
  </linearGradient>
  <radialGradient id="headGrad" cx=".38" cy=".3" r=".85">
    <stop offset="0" stop-color="#f58bab"/><stop offset=".45" stop-color="#dc5a85"/><stop offset="1" stop-color="#a73566"/>
  </radialGradient>
  <linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8a5229"/><stop offset="1" stop-color="#c58a4c"/>
  </linearGradient>
  <linearGradient id="woodFront" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6b3e22"/><stop offset="1" stop-color="#3b2013"/>
  </linearGradient>
  <linearGradient id="post" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4a2c1a"/><stop offset=".35" stop-color="#7a4a2b"/><stop offset="1" stop-color="#2f1a0f"/>
  </linearGradient>
  <linearGradient id="roofG" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1b2036"/><stop offset="1" stop-color="#2d3350"/>
  </linearGradient>
  <linearGradient id="nore" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2a3d86"/><stop offset="1" stop-color="#1a2557"/>
  </linearGradient>
  <linearGradient id="bowlGrad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#e9e2d6"/><stop offset=".35" stop-color="#fffdf8"/><stop offset=".75" stop-color="#ece5d9"/><stop offset="1" stop-color="#c9bfae"/>
  </linearGradient>
  <radialGradient id="brothGrad" cx=".5" cy=".5" r=".6">
    <stop offset="0" stop-color="#eaa84a"/><stop offset="1" stop-color="#b3651b"/>
  </radialGradient>
  <linearGradient id="steel" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#6d7681"/><stop offset=".22" stop-color="#cdd4db"/><stop offset=".4" stop-color="#f1f4f6"/><stop offset=".7" stop-color="#a7b0ba"/><stop offset="1" stop-color="#5d6671"/>
  </linearGradient>
  <linearGradient id="steelV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e5e9ed"/><stop offset="1" stop-color="#8c96a1"/>
  </linearGradient>
  <linearGradient id="toqueG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fffdf8"/><stop offset=".6" stop-color="#f6f1ea"/><stop offset="1" stop-color="#cfc8dc"/>
  </linearGradient>
  <linearGradient id="apronG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#34478f"/><stop offset="1" stop-color="#1d2859"/>
  </linearGradient>
  <radialGradient id="vignette" cx=".5" cy=".47" r=".75">
    <stop offset=".55" stop-color="#05030c" stop-opacity="0"/><stop offset="1" stop-color="#05030c" stop-opacity=".62"/>
  </radialGradient>
  <filter id="blur5" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
  <filter id="blur10" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
  <clipPath id="armsClip"><rect x="0" y="652" width="1200" height="248"/></clipPath>
  <clipPath id="insideClip"><rect x="84" y="40" width="1032" height="618"/></clipPath>
</defs>''')

    # ---------------- exterior night ----------------
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # distant skyline slivers + bokeh visible past the posts
    for (x, w, h) in [(0, 30, 330), (30, 26, 250), (1146, 26, 280), (1170, 30, 360)]:
        a(f'<rect x="{x}" y="{H - h - 150}" width="{w}" height="{h + 150}" fill="#150f33"/>')
        for wy in range(H - h - 120, H - 300, 46):
            a(f'<rect x="{x + 6}" y="{wy}" width="8" height="12" fill="#ffd27a" opacity=".55"/>')
    for (x, y, r, c) in [(22, 420, 16, "#ff9ec2"), (40, 520, 11, "#7fd6ff"), (1165, 470, 15, "#ffd27a"),
                         (1150, 560, 10, "#ff9ec2"), (14, 610, 9, "#ffd27a"), (1184, 380, 8, "#7fd6ff")]:
        a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity=".45" filter="url(#blur2)"/>')

    # ---------------- interior back wall ----------------
    a('<g clip-path="url(#insideClip)">')
    a('<rect x="84" y="40" width="1032" height="618" fill="url(#wall)"/>')
    for x in range(84, 1120, 64):
        a(f'<rect x="{x}" y="40" width="2.5" height="618" fill="#1c0e09" opacity=".5"/>')
        a(f'<rect x="{x + 3}" y="40" width="1.5" height="618" fill="#8a5330" opacity=".18"/>')
    # warm halo behind the chef
    a('<ellipse cx="600" cy="420" rx="360" ry="330" fill="url(#halo)"/>')
    # lantern pools
    a('<circle cx="190" cy="215" r="230" fill="url(#lampGlow)" opacity=".7"><animate attributeName="opacity" values=".62;.8;.66;.78;.62" dur="3.6s" repeatCount="indefinite"/></circle>')
    a('<circle cx="1010" cy="215" r="230" fill="url(#lampGlow)" opacity=".7"><animate attributeName="opacity" values=".75;.62;.8;.64;.75" dur="4.1s" repeatCount="indefinite"/></circle>')

    # left: utensil rail
    a('<rect x="112" y="318" width="190" height="8" rx="3" fill="#2a160d"/><rect x="112" y="318" width="190" height="3" rx="1.5" fill="#6b3f24"/>')
    # ladle
    a('<g><path d="M140 326V398" stroke="#c9a36a" stroke-width="5" stroke-linecap="round"/><path d="M128 398A18 18 0 0 0 164 398Z" fill="url(#steelV)" stroke="#7d8793" stroke-width="1.5"/></g>')
    # strainer
    a('<g><path d="M205 326V352" stroke="#c9a36a" stroke-width="5" stroke-linecap="round"/><circle cx="205" cy="380" r="26" fill="#aeb7c0" fill-opacity=".18" stroke="#d3d9df" stroke-width="3"/>'
      '<path d="M185 366L225 394M185 394L225 366M179 380H231M205 354V406M191 360L219 400M219 360L191 400" stroke="#b6bfc8" stroke-width="1.2" opacity=".75"/></g>')
    # skimmer
    a('<g><path d="M268 326V372" stroke="#c9a36a" stroke-width="5" stroke-linecap="round"/><ellipse cx="268" cy="394" rx="21" ry="25" fill="url(#steelV)" stroke="#7d8793" stroke-width="1.5"/>'
      '<g fill="#5c6670"><circle cx="262" cy="384" r="2.5"/><circle cx="274" cy="384" r="2.5"/><circle cx="268" cy="394" r="2.5"/><circle cx="259" cy="403" r="2.5"/><circle cx="277" cy="403" r="2.5"/></g></g>')

    # right: hanging wooden menu slats
    slats = [(930, 270, 150), (974, 282, 138), (1018, 270, 150), (1062, 284, 136)]
    for i, (x, y, h) in enumerate(slats):
        a(f'<path d="M{x + 18} 240V{y}" stroke="#1a0d08" stroke-width="2"/>')
        a(f'<rect x="{x}" y="{y}" width="36" height="{h}" rx="3" fill="#d9b27a" stroke="#6b4423" stroke-width="2"/>')
        a(f'<rect x="{x + 3}" y="{y + 3}" width="5" height="{h - 6}" fill="#fff" opacity=".18"/>')
        gname = ["ra", "me", "n", "ra"][i]
        a(glyph(KANA, gname, x + 6, y + 12, 24, "#3a1d10", 3))
        a(f'<path d="M{x + 10} {y + 54}h16M{x + 12} {y + 64}h12M{x + 10} {y + 74}h16" stroke="#3a1d10" stroke-width="2.6" stroke-linecap="round"/>')
        a(f'<rect x="{x + 9}" y="{y + h - 36}" width="18" height="18" rx="2" fill="#c3312a"/>'
          f'<path d="M{x + 13} {y + h - 28}h10M{x + 18} {y + h - 32}v10" stroke="#ffe9d0" stroke-width="2"/>')
    a('</g>')

    # ---------------- stockpot (left) ----------------
    a('''<g transform="translate(22 0)">
  <ellipse cx="150" cy="664" rx="86" ry="10" fill="#120804" opacity=".5" filter="url(#blur5)"/>
  <path d="M76 512V640Q76 664 100 664H200Q224 664 224 640V512Z" fill="url(#steel)" stroke="#59626c" stroke-width="2"/>
  <path d="M76 600H224" stroke="#7d8793" stroke-width="2" opacity=".6"/>
  <path d="M96 524V640" stroke="#fff" stroke-width="6" opacity=".35" stroke-linecap="round"/>
  <ellipse cx="150" cy="512" rx="74" ry="15" fill="#d6dce2" stroke="#59626c" stroke-width="2"/>
  <ellipse cx="150" cy="514" rx="66" ry="11" fill="#7c4a1c"/>
  <ellipse cx="150" cy="515" rx="62" ry="8.5" fill="#c9893a"/>
  <ellipse cx="136" cy="514" rx="30" ry="3" fill="#f0c36a" opacity=".7"/>
  <path d="M70 536q-22 0 -22 12t22 12" fill="none" stroke="#59626c" stroke-width="7" stroke-linecap="round"/>
  <path d="M230 536q22 0 22 12t-22 12" fill="none" stroke="#59626c" stroke-width="7" stroke-linecap="round"/>
</g>''')

    # ---------------- octopus: arms behind the head ----------------
    a('<ellipse cx="600" cy="610" rx="120" ry="72" fill="url(#armGrad)" stroke="#8a2a5a" stroke-width="2"/>')

    # waving arm that rises from behind the counter on the right
    wave = Arm([(960, 710), (956, 650), (974, 596), (994, 546), (986, 496), (996, 446), (1022, 416), (1044, 388),
                (1060, 360), (1054, 332), (1030, 320), (1008, 336), (1008, 360), (1028, 370)], 54, 14, power=0.9)
    a('<g><animateTransform attributeName="transform" type="rotate" values="-2.5 960 700;3.5 960 700;-2.5 960 700" '
      'dur="2.6s" calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1" repeatCount="indefinite"/>')
    a(wave.draw(sucker=(0.5, 0.97, 1, 0.12, 0.2)))
    a('</g>')

    # chopsticks + noodle lift (right)
    gx, gy = 790, 452
    tipA, tipB = (895, 392), (890, 408)
    paths = []
    for i in range(9):
        x0 = 880 + i * 1.7 - 6 + (i % 3) * 2
        y0 = 398 + (i % 2) * 3
        paths.append(wavy_pts(x0, y0, 628, 7 + (i % 4) * 1.6, 1.5 + (i % 3) * 0.25, i * 0.9))
    col = ["#ecc15f", "#f4d27c"]

    def strand_svg(pts, lo, hi):
        sel = [(x, y) for x, y in pts if lo <= y <= hi]
        return (f'<path d="M{"L".join(f"{f(x)} {f(y)}" for x, y in sel)}" fill="none" stroke="__C__" '
                f'stroke-width="3.6" stroke-linecap="round"/>')

    # upper part of the noodles sits behind the chopsticks
    a('<g>' + "".join(strand_svg(p, 0, 440).replace("__C__", col[i % 2]) for i, p in enumerate(paths)) + '</g>')
    a(f'<g stroke-linecap="round" fill="none">'
      f'<path d="M{gx - 38} {gy + 22}L{tipA[0]} {tipA[1]}" stroke="#7a4b22" stroke-width="7.5"/>'
      f'<path d="M{gx - 38} {gy + 22}L{tipA[0]} {tipA[1]}" stroke="#d9a860" stroke-width="4"/>'
      f'<path d="M{gx - 30} {gy + 34}L{tipB[0]} {tipB[1]}" stroke="#7a4b22" stroke-width="7.5"/>'
      f'<path d="M{gx - 30} {gy + 34}L{tipB[0]} {tipB[1]}" stroke="#e5b873" stroke-width="4"/></g>')
    chop_arm = Arm([(650, 620), (715, 612), (760, 575), (785, 520), (790, 478), (802, 452), (822, 442), (828, 462),
                    (810, 476), (796, 470)], 40, 12, power=0.9)
    a(chop_arm.draw(sucker=(0.5, 0.97, -1, 0.14, 0.2)))

    # ladle arm (left)
    lad_c = (322, 548)
    a(ladle(lad_c[0], lad_c[1], -35))
    ladle_arm = Arm([(550, 620), (490, 610), (448, 570), (428, 520), (424, 492), (408, 470), (388, 470), (386, 492),
                     (404, 504), (418, 496)], 40, 12, power=0.9)
    a(ladle_arm.draw(sucker=(0.5, 0.97, 1, 0.14, 0.2)))

    # ---------------- head ----------------
    HEAD = "M600 252C700 252 738 340 728 420C722 486 692 536 652 560L548 560C508 536 478 486 472 420C462 340 500 252 600 252Z"
    a(f'<clipPath id="headClip"><path d="{HEAD}"/></clipPath>')
    a(f'<path d="{HEAD}" fill="url(#headGrad)" stroke="#8a2a5a" stroke-width="2.5" stroke-linejoin="round"/>')
    a('<g clip-path="url(#headClip)">')
    a('<ellipse cx="748" cy="430" rx="62" ry="210" fill="#6d1646" opacity=".3" filter="url(#blur10)"/>')
    a('<ellipse cx="600" cy="270" rx="110" ry="26" fill="#5c1240" opacity=".4" filter="url(#blur5)"/>')
    a('<ellipse cx="528" cy="345" rx="20" ry="60" fill="#fff" opacity=".22" transform="rotate(14 528 345)" filter="url(#blur5)"/>')
    for (x, y, r) in [(512, 372, 11), (528, 410, 7), (690, 322, 10), (705, 372, 7), (652, 290, 8), (540, 302, 8), (718, 410, 6), (498, 440, 6)]:
        a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f9a6bd" opacity=".55"/><circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#b6406f" stroke-width="1.2" opacity=".45"/>')
    a('</g>')

    # eyes (blink animation wraps them)
    a('<g transform="translate(0 430)"><g>'
      '<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 .07;1 1;1 1" keyTimes="0;.9;.94;.98;1" dur="5.2s" repeatCount="indefinite"/>'
      '<g transform="translate(0 -430)">')
    for cx, sgn in ((561, 1), (639, -1)):
        a(f'<clipPath id="eye{cx}"><ellipse cx="{cx}" cy="430" rx="34" ry="38"/></clipPath>')
        a(f'<ellipse cx="{cx}" cy="430" rx="34" ry="38" fill="#fff8f1" stroke="#8a2a5a" stroke-width="2.5"/>')
        a(f'<g clip-path="url(#eye{cx})">'
          f'<ellipse cx="{cx}" cy="395" rx="40" ry="14" fill="#c9628a" opacity=".35"/>'
          f'<circle cx="{cx + 1}" cy="435" r="26" fill="#e9a232"/><circle cx="{cx + 1}" cy="435" r="26" fill="none" stroke="#a55f14" stroke-width="2.5"/>'
          f'<circle cx="{cx + 1}" cy="436" r="16" fill="#2a0f2e"/>'
          f'<circle cx="{cx - 8}" cy="424" r="8" fill="#fff"/><circle cx="{cx + 9}" cy="443" r="3.8" fill="#fff" opacity=".9"/>'
          f'</g>')
    a('</g></g></g>')
    # brows
    a('<g fill="none" stroke="#6b2150" stroke-width="9" stroke-linecap="round">'
      '<path d="M522 376Q552 352 590 370"/><path d="M610 370Q648 352 678 376"/></g>')
    # cheeks + mouth
    a('<ellipse cx="520" cy="482" rx="19" ry="11" fill="#ff8aa8" opacity=".6"/><ellipse cx="680" cy="482" rx="19" ry="11" fill="#ff8aa8" opacity=".6"/>')
    a('<clipPath id="mouthClip"><path d="M568 478Q600 486 632 478Q626 518 600 518Q574 518 568 478Z"/></clipPath>')
    a('<path d="M568 478Q600 486 632 478Q626 518 600 518Q574 518 568 478Z" fill="#5a1a3c" stroke="#7a2150" stroke-width="2.5" stroke-linejoin="round"/>')
    a('<ellipse cx="600" cy="514" rx="15" ry="10" fill="#ef6f8f" clip-path="url(#mouthClip)"/>')

    # neck strap + apron bib
    a('<path d="M520 548Q600 590 680 548L682 568Q600 612 518 568Z" fill="#243257" stroke="#141c3c" stroke-width="1.5"/>')
    a('<path d="M556 584L644 584L682 668L518 668Z" fill="url(#apronG)" stroke="#141c3c" stroke-width="1.5"/>')
    a('<g transform="translate(600 622)"><circle r="19" fill="#f7f0e3"/>'
      '<path d="M-12 -2H12A12 12 0 0 1 -12 -2Z" fill="#fff" stroke="#b9302e" stroke-width="2.4"/>'
      '<path d="M-8 -9Q-5 -14 -8 -18M0 -9Q3 -14 0 -18M8 -9Q11 -14 8 -18" stroke="#b9302e" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>')

    # ---------------- chef's toque ----------------
    TOQ = ('<path d="M540 262C522 244 506 240 508 220A30 30 0 0 1 524 176A30 30 0 0 1 572 152A30 30 0 0 1 628 152'
           'A30 30 0 0 1 676 176A30 30 0 0 1 692 220C694 240 678 244 660 262Z"/>')
    a(f'<clipPath id="toqueClip">{TOQ}</clipPath>')
    a('<ellipse cx="610" cy="278" rx="86" ry="14" fill="#2a0a1c" opacity=".35" filter="url(#blur5)"/>')
    a(f'<g fill="url(#toqueG)" stroke="#d2c7b5" stroke-width="3" stroke-linejoin="round">{TOQ}</g>')
    a('<g clip-path="url(#toqueClip)" fill="none" stroke-linecap="round">'
      '<ellipse cx="600" cy="236" rx="96" ry="13" fill="#b9aebf" stroke="none" opacity=".35" filter="url(#blur5)"/>'
      '<path d="M524 176Q518 222 540 262M548 164Q546 220 556 264M572 152Q568 214 578 266M600 150V268M628 152Q632 214 622 266'
      'M652 164Q654 220 644 264M676 176Q682 222 660 262" stroke="#cfc5b6" stroke-width="2.2" opacity=".85"/>'
      '<ellipse cx="560" cy="156" rx="30" ry="12" fill="#fff" stroke="none" opacity=".7" filter="url(#blur2)"/>'
      '<path d="M690 190Q702 236 664 272" stroke="#a79bc0" stroke-width="16" opacity=".3" filter="url(#blur5)"/></g>')
    a('<path d="M532 252Q600 266 668 252L666 282Q600 296 534 282Z" fill="#c63a33" stroke="#8a1f22" stroke-width="1.5"/>')
    a('<path d="M538 258Q600 270 664 258" stroke="#ff8a7a" stroke-width="3" fill="none" opacity=".6" stroke-linecap="round"/>')

    # ---------------- counter ----------------
    a('<path d="M84 650H1116L1142 716H58Z" fill="url(#woodTop)"/>')
    a('<path d="M84 650H1116L1124 672H76Z" fill="#2a140a" opacity=".38"/>')
    for i in range(14):
        y = 658 + i * 4.2
        xa = 84 - (y - 650) * 0.4
        xb = 1116 + (y - 650) * 0.4
        a(f'<path d="M{f(xa)} {f(y)}H{f(xb)}" stroke="{"#e0a566" if i % 3 == 0 else "#5a3015"}" stroke-width="1" opacity=".28"/>')
    a('<rect x="58" y="716" width="1084" height="9" fill="#e2ae6c"/><rect x="58" y="716" width="1084" height="3" fill="#f6d39a"/>')
    a('<rect x="58" y="725" width="1084" height="175" fill="url(#woodFront)"/>')
    for x in range(58, 1150, 118):
        a(f'<rect x="{x}" y="725" width="3" height="175" fill="#1b0d07" opacity=".55"/><rect x="{x + 3}" y="725" width="2" height="175" fill="#a8683a" opacity=".22"/>')
    a('<rect x="58" y="725" width="1084" height="14" fill="#140804" opacity=".45" filter="url(#blur5)"/>')
    a('<ellipse cx="600" cy="860" rx="520" ry="110" fill="url(#halo)" opacity=".5"/>')

    # ---------------- bowls on the counter ----------------
    a(bowl(330, 636, "b1"))
    a(bowl(865, 632, "b2", flip=True))
    # broth stream from ladle lip into bowl 1
    lip = (lad_c[0] - 36 * math.cos(math.radians(35)), lad_c[1] + 36 * math.sin(math.radians(35)))
    sx, sy = lip
    a(f'<path d="M{f(sx + 2)} {f(sy)}C{f(sx - 5)} {f(sy + 22)} {f(sx - 1)} {f(sy + 44)} {f(sx - 3)} 636L{f(sx + 7)} 636C{f(sx + 9)} {f(sy + 44)} {f(sx + 12)} {f(sy + 22)} {f(sx + 8)} {f(sy)}Z" fill="#e0a043"/>')
    a(f'<path d="M{f(sx + 5)} {f(sy + 4)}C{f(sx)} {f(sy + 24)} {f(sx + 3)} {f(sy + 44)} {f(sx + 1)} 634" stroke="#ffe1a0" stroke-width="2" fill="none" opacity=".8" stroke-linecap="round"/>')
    a(f'<ellipse cx="{f(sx + 2)}" cy="640" rx="16" ry="5" fill="#f0c36a" opacity=".85"/>')
    a(f'<circle cx="{f(sx - 14)}" cy="622" r="2.2" fill="#e0a043"/><circle cx="{f(sx + 20)}" cy="618" r="1.8" fill="#e0a043"/><circle cx="{f(sx + 14)}" cy="628" r="1.5" fill="#e0a043"/>')
    # lower noodle strands drop into bowl 2
    a('<g>' + "".join(strand_svg(p, 430, 630).replace("__C__", col[i % 2]) for i, p in enumerate(paths)) + '</g>')

    # condiments (far right)
    a('''<g transform="translate(-26 0)">
  <ellipse cx="1080" cy="702" rx="62" ry="9" fill="#150803" opacity=".5" filter="url(#blur5)"/>
  <rect x="1038" y="640" width="26" height="58" rx="8" fill="#3a1a10" stroke="#1d0d07" stroke-width="1.5"/>
  <rect x="1043" y="628" width="16" height="16" rx="3" fill="#c3312a"/><rect x="1038" y="656" width="26" height="20" fill="#f1e6cf"/>
  <path d="M1044 666h14" stroke="#3a1d10" stroke-width="2.4" stroke-linecap="round"/>
  <rect x="1074" y="654" width="30" height="44" rx="8" fill="#b53a1d" opacity=".95" stroke="#6b1d0d" stroke-width="1.5"/>
  <rect x="1072" y="646" width="34" height="10" rx="3" fill="#2a2a2a"/><rect x="1080" y="666" width="18" height="12" rx="2" fill="#f5e6c8"/>
  <path d="M1110 698V664H1134V698Z" fill="#f7f1e4" stroke="#cfc5b3" stroke-width="1.5"/>
  <path d="M1116 664L1112 628M1122 664L1124 622M1128 664L1136 630" stroke="#d9a860" stroke-width="4" stroke-linecap="round"/>
</g>''')

    # steam
    a(steam(172, 500, 190, 20, 20, .30, 6.0, 0.0))
    a(steam(140, 505, 150, 16, 16, .24, 5.0, 2.0))
    a(steam(206, 505, 170, 18, 16, .24, 5.5, 3.5))
    a(steam(345, 604, 120, 14, 14, .28, 4.5, 0.5))
    a(steam(310, 606, 90, 11, 12, .22, 4.0, 2.0))
    a(steam(860, 600, 120, 14, 14, .26, 4.8, 1.0))

    # ---------------- draped front arms (clipped at the counter's back edge) ----------------
    a('<g clip-path="url(#armsClip)">')
    front = [
        (Arm([(545, 600), (520, 690), (470, 745), (410, 790), (350, 800), (308, 775), (310, 745), (336, 738), (346, 758)],
             40, 11, power=0.85), (0.35, 0.98, 1, 0.14, 0.2)),
        (Arm([(660, 600), (700, 690), (765, 742), (825, 778), (880, 778), (912, 756), (906, 730), (880, 730), (876, 752)],
             40, 11, power=0.85), (0.35, 0.98, -1, 0.14, 0.2)),
        (Arm([(575, 600), (565, 700), (562, 780), (540, 840), (494, 862), (452, 846), (450, 814), (476, 806), (486, 830)],
             40, 11, power=0.85), (0.35, 0.98, 1, 0.14, 0.2)),
        (Arm([(630, 600), (645, 700), (662, 780), (690, 842), (736, 864), (778, 848), (780, 816), (754, 808), (744, 832)],
             40, 11, power=0.85), (0.35, 0.98, -1, 0.14, 0.2)),
    ]
    for arm, suck in front:
        a(arm.draw(sucker=suck))
    a('</g>')
    # soft shadow where the arms cross the counter lip
    a('<rect x="58" y="722" width="1084" height="10" fill="#140804" opacity=".25" filter="url(#blur2)"/>')

    # front placards
    a('<rect x="112" y="772" width="196" height="84" rx="8" fill="#0d0605" opacity=".4" filter="url(#blur5)"/>')
    a('<rect x="108" y="766" width="196" height="84" rx="8" fill="#a8232b" stroke="#e5b24f" stroke-width="3.5"/>')
    a('<rect x="116" y="774" width="180" height="68" rx="4" fill="none" stroke="#e5b24f" stroke-width="1.3" opacity=".8"/>')
    for i, g in enumerate("RAMEN"):
        a(glyph(LATIN, g, 127 + i * 35, 786, 44, "#fff1d4", 5.2))
    a('<rect x="918" y="772" width="190" height="84" rx="8" fill="#0d0605" opacity=".4" filter="url(#blur5)"/>')
    a('<rect x="914" y="766" width="190" height="84" rx="8" fill="#20332c" stroke="#8a5a2c" stroke-width="5"/>')
    for i, g in enumerate("OPEN"):
        a(glyph(LATIN, g, 946 + i * 37, 786, 44, "#f4f1e6", 5.2))

    # ---------------- roof, beam, sign ----------------
    a('<path d="M-20 0H1220V44Q600 140 -20 44Z" fill="url(#roofG)"/>')
    for x in range(-20, 1230, 28):
        t = (x + 20) / 1240
        yb = 44 * (1 - 2 * t + 2 * t * t) + 280 * t * (1 - t)
        a(f'<path d="M{x} 0V{f(yb)}" stroke="#0e1124" stroke-width="2" opacity=".6"/>')
    a('<path d="M-20 44Q600 140 1220 44" fill="none" stroke="#d8c9a6" stroke-width="5"/>')
    a('<path d="M-20 50Q600 146 1220 50" fill="none" stroke="#0a0a14" stroke-width="3" opacity=".5"/>')
    a('<rect x="48" y="100" width="1104" height="24" fill="url(#woodFront)"/><rect x="48" y="100" width="1104" height="5" fill="#b4743f" opacity=".6"/>')
    a('<ellipse cx="600" cy="130" rx="520" ry="14" fill="#0a0504" opacity=".4" filter="url(#blur5)"/>')
    # sign
    a('<rect x="436" y="24" width="328" height="70" rx="8" fill="#0d0605" opacity=".45" filter="url(#blur5)"/>')
    a('<rect x="436" y="18" width="328" height="68" rx="8" fill="#a8232b" stroke="#e5b24f" stroke-width="4"/>')
    a('<rect x="446" y="28" width="308" height="48" rx="4" fill="none" stroke="#e5b24f" stroke-width="1.5" opacity=".8"/>')
    for i, g in enumerate(["ra", "bar", "me", "n"]):
        a(glyph(KANA, g, 463 + i * 71, 26, 52, "#fff1d4", 6.2))

    # noren curtains
    for rx0, rx1 in ((285, 495), (705, 915)):
        a(f'<rect x="{rx0}" y="121" width="{rx1 - rx0}" height="7" rx="3" fill="#3b2113"/>')
    for (x0, g) in [(292, "ra"), (392, "barv"), (712, "me"), (812, "n")]:
        a(f'<path d="M{x0} 126H{x0 + 96}V246Q{x0 + 72} 252 {x0 + 48} 245T{x0} 248Z" fill="url(#nore)" stroke="#121a42" stroke-width="1.5"/>')
        a(f'<path d="M{x0 + 30} 128V244M{x0 + 66} 128V246" stroke="#0f1744" stroke-width="3" opacity=".35"/>')
        a(f'<path d="M{x0} 232Q{x0 + 24} 238 {x0 + 48} 231T{x0 + 96} 234" stroke="#f1ead8" stroke-width="4" fill="none" opacity=".85"/>')
        a(glyph(KANA, g, x0 + 22, 148, 56, "#fff1d4", 6.5))

    # lanterns
    def lantern(cx, glyphs):
        s = f'<path d="M{cx} 122V150" stroke="#1a0d08" stroke-width="2.5"/>'
        s += f'<rect x="{cx - 22}" y="148" width="44" height="12" rx="3" fill="#1d1210"/>'
        s += (f'<path d="M{cx - 24} 160C{cx - 56} 176 {cx - 56} 244 {cx - 24} 260H{cx + 24}C{cx + 56} 244 {cx + 56} 176 {cx + 24} 160Z" '
              f'fill="#d3262c" stroke="#7a0f17" stroke-width="2"/>')
        s += f'<ellipse cx="{cx}" cy="210" rx="30" ry="46" fill="#ff7a4a" opacity=".55" filter="url(#blur10)"/>'
        for k, y in enumerate((178, 194, 210, 226, 242)):
            half = 50 - abs(y - 210) * 0.38
            s += f'<path d="M{cx - half:.0f} {y}Q{cx} {y + 6} {cx + half:.0f} {y}" stroke="#7a0f17" stroke-width="1.6" fill="none" opacity=".7"/>'
        for i, g in enumerate(glyphs):
            s += glyph(KANA, g, cx - 11, 170 + i * 22, 22, "#fff1d4", 2.8)
        s += f'<rect x="{cx - 22}" y="258" width="44" height="12" rx="3" fill="#1d1210"/>'
        s += f'<path d="M{cx} 270V292M{cx - 6} 270V286M{cx + 6} 270V286" stroke="#c9a14a" stroke-width="2.5" stroke-linecap="round"/>'
        return s
    a(lantern(190, ["ra", "barv", "me", "n"]))
    a(lantern(1010, ["ra", "barv", "me", "n"]))

    # posts
    for x in (48, 1116):
        a(f'<rect x="{x}" y="92" width="36" height="808" fill="url(#post)"/>')
        a(f'<rect x="{x + 6}" y="92" width="3" height="808" fill="#b4743f" opacity=".35"/>')
        a(f'<rect x="{x - 4}" y="92" width="44" height="14" rx="3" fill="#2a160d"/>')

    # vignette
    a(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    a('</svg>')
    return "\n".join(o)


def wavy_pts(x0, y0, y1, amp, k, phase, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        amp_t = amp * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.4)))
        pts.append((x0 + amp_t * math.sin(k * t * 2 * math.pi + phase), y))
    return pts


if __name__ == "__main__":
    svg = build()
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(svg)
    print("wrote", os.path.abspath(OUT), len(svg) // 1024, "KB")
