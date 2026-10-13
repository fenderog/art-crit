#!/usr/bin/env python3
"""Awkward robot family portrait -> SVG (standard library only).

Run:  python3 src/make_portrait.py [out.svg]
"""
import math
import os
import sys

W, H = 1600, 1200
OUT = "#1b2230"
SW = 5

# ----------------------------------------------------------------- colour --


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    ca, cb = _rgb(a), _rgb(b)
    return _hex([ca[i] + (cb[i] - ca[i]) * t for i in range(3)])


def lighten(c, t):
    return mix(c, "#ffffff", t)


def darken(c, t):
    return mix(c, "#000000", t)


_grads = {}


def G(color):
    """Diagonal light->dark gradient fill for a base colour."""
    if color not in _grads:
        _grads[color] = "g%d" % len(_grads)
    return "url(#%s)" % _grads[color]


def grad_defs():
    out = []
    for c, i in _grads.items():
        out.append(
            f'<linearGradient id="{i}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{lighten(c, .26)}"/>'
            f'<stop offset=".5" stop-color="{c}"/>'
            f'<stop offset="1" stop-color="{darken(c, .24)}"/></linearGradient>')
    return "".join(out)


# --------------------------------------------------------------- primitives --


def _a(fill, stroke, sw, extra):
    s = f'fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"'
        if "stroke-linecap" not in extra:
            s += ' stroke-linecap="round"'
    if extra:
        s += " " + extra
    return s


def rect(x, y, w, h, r=0, fill="#fff", stroke=OUT, sw=SW, extra=""):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" {_a(fill, stroke, sw, extra)}/>')


def circ(cx, cy, r, fill="#fff", stroke=OUT, sw=SW, extra=""):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'{_a(fill, stroke, sw, extra)}/>')


def ell(cx, cy, rx, ry, fill="#fff", stroke=OUT, sw=SW, extra=""):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'{_a(fill, stroke, sw, extra)}/>')


def path(d, fill="none", stroke=OUT, sw=SW, extra=""):
    return f'<path d="{d}" {_a(fill, stroke, sw, extra)}/>'


def poly(pts, fill="#fff", stroke=OUT, sw=SW, extra=""):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" {_a(fill, stroke, sw, extra)}/>'


def grp(content, tx=0, ty=0, rot=0, sc=1, extra=""):
    return (f'<g transform="translate({tx:.1f},{ty:.1f}) rotate({rot}) '
            f'scale({sc})" {extra}>{content}</g>')


def rot_about(content, ang, cx, cy):
    return f'<g transform="rotate({ang} {cx} {cy})">{content}</g>'


def limb(pts, w, color, ow=SW, hl=True):
    """Outlined tube through a polyline, with a soft highlight."""
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    base = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    s = f'<path d="{d}" {base} stroke="{OUT}" stroke-width="{w + 2 * ow:.1f}"/>'
    s += f'<path d="{d}" {base} stroke="{color}" stroke-width="{w:.1f}"/>'
    if hl and w >= 14:
        off = w * 0.2
        s += (f'<path d="{d}" {base} stroke="#fff" stroke-opacity=".3" '
              f'stroke-width="{w * .2:.1f}" transform="translate({-off:.1f},{-off:.1f})"/>')
    return s


def hand(x, y, ang, color, s=1.0):
    """Three-fingered robot mitt; fingers point +y at ang=0."""
    g = ""
    for fx, fl in ((-10.5, 24), (0, 29), (10.5, 24)):
        g += rect(fx - 4.5, 8, 9, fl, 4.5, G(color), sw=3.5)
    g += rot_about(rect(-29, -2, 17, 10, 5, G(color), sw=3.5), 28, -20, 3)
    g += rect(-16, -12, 32, 26, 10, G(color), sw=4)
    g += circ(0, 0, 3.2, darken(color, .35), stroke=None)
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang}) '
            f'scale({s})">{g}</g>')


def joint(x, y, r, color):
    return (circ(x, y, r, G(color), sw=4) + circ(x, y, r * .32, darken(color, .4), stroke=None))


def shadow(cx, cy, rx, ry, op=.38):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#0b0d14" '
            f'opacity="{op}" filter="url(#soft)"/>')


class Fig:
    """Local coords: origin at the feet, y up is negative."""

    def __init__(self, ox, oy, rot=0.0, sc=1.0):
        self.ox, self.oy, self.rot, self.sc = ox, oy, rot, sc

    def pt(self, x, y):
        a = math.radians(self.rot)
        c, s = math.cos(a), math.sin(a)
        return (self.ox + self.sc * (x * c - y * s),
                self.oy + self.sc * (x * s + y * c))

    def wrap(self, content):
        return grp(content, self.ox, self.oy, self.rot, self.sc)


def two_bone(a, b, l1, l2, side=1):
    """Elbow position for a two-segment arm from a to b (side picks the bend)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    d = min(d, l1 + l2 - 1e-3)
    t = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - t * t, 0))
    ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    mx, my = a[0] + ux * t, a[1] + uy * t
    return (mx - uy * h * side, my + ux * h * side)


# ----------------------------------------------------------------- palette --
DAD_SHELL = "#e8ae3b"
DAD_VEST = "#a9473a"
SHIRT = "#f1e9d2"
TIE = "#24456b"
KHAKI = "#b5a27c"
STEEL = "#aab4c2"

MOM_DRESS = "#ee7f74"
MOM_SKIN = "#fbe6d8"
MOM_METAL = "#cfd5de"
HAIR = "#6a3a63"

TEEN_HOOD = "#7a5ccf"
TEEN_SCREEN = "#10141d"
LIME = "#b9f45a"
JEANS = "#2f3b5c"

KID = "#8fe0c0"
KID_CAP = "#e5483b"

GRAMPS = "#b97b4a"
CHAIR = "#8a3344"
CARDI = "#8c8a4a"

DOG = "#d5dce4"

# ----------------------------------------------------------------- setting --


def defs():
    return f"""
<defs>
  {grad_defs()}
  <radialGradient id="bgGrad" cx="50%" cy="38%" r="75%">
    <stop offset="0" stop-color="#5b93a3"/>
    <stop offset=".55" stop-color="#34606f"/>
    <stop offset="1" stop-color="#1b3340"/>
  </radialGradient>
  <linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8e6b52"/>
    <stop offset="1" stop-color="#3f2b22"/>
  </linearGradient>
  <linearGradient id="seam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0b0d14" stop-opacity="0"/>
    <stop offset="1" stop-color="#0b0d14" stop-opacity=".45"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="46%" r="72%">
    <stop offset=".55" stop-color="#05070c" stop-opacity="0"/>
    <stop offset="1" stop-color="#05070c" stop-opacity=".62"/>
  </radialGradient>
  <radialGradient id="flash" cx="50%" cy="40%" r="45%">
    <stop offset="0" stop-color="#fff6dc" stop-opacity=".30"/>
    <stop offset="1" stop-color="#fff6dc" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="curtain" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="52" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="#4a1724"/>
    <stop offset=".45" stop-color="#9a3a4d"/>
    <stop offset="1" stop-color="#4a1724"/>
  </linearGradient>
  <linearGradient id="column" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#9c917c"/>
    <stop offset=".4" stop-color="#e9dfc9"/>
    <stop offset="1" stop-color="#8d826e"/>
  </linearGradient>
  <radialGradient id="crt" cx="45%" cy="40%" r="70%">
    <stop offset="0" stop-color="#bfeab5"/>
    <stop offset=".7" stop-color="#8fc896"/>
    <stop offset="1" stop-color="#4f8a66"/>
  </radialGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".55"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shade" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".22"/>
    <stop offset=".5" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".28"/>
  </linearGradient>
  <pattern id="argyle" width="56" height="76" patternUnits="userSpaceOnUse">
    <rect width="56" height="76" fill="{DAD_VEST}"/>
    <polygon points="28,6 50,38 28,70 6,38" fill="#e2a94b"/>
    <polygon points="28,22 40,38 28,54 16,38" fill="#7a2c2e"/>
    <polygon points="0,0 12,0 0,18" fill="#7a2c2e"/>
    <polygon points="56,0 44,0 56,18" fill="#7a2c2e"/>
    <polygon points="0,76 12,76 0,58" fill="#7a2c2e"/>
    <polygon points="56,76 44,76 56,58" fill="#7a2c2e"/>
    <path d="M0,0 L56,76 M56,0 L0,76" stroke="#f1e9d2" stroke-width="1.6" opacity=".7"/>
  </pattern>
  <pattern id="plaid" width="44" height="44" patternUnits="userSpaceOnUse">
    <rect width="44" height="44" fill="#d9a441"/>
    <rect x="10" width="12" height="44" fill="#7b3f2a" opacity=".65"/>
    <rect y="10" width="44" height="12" fill="#7b3f2a" opacity=".65"/>
    <rect x="30" width="3" height="44" fill="#f4e6c4"/>
    <rect y="30" width="44" height="3" fill="#f4e6c4"/>
  </pattern>
  <pattern id="rugpat" width="60" height="30" patternUnits="userSpaceOnUse">
    <rect width="60" height="30" fill="#7b3544"/>
    <polygon points="30,3 52,15 30,27 8,15" fill="none" stroke="#d9b98a" stroke-width="2.4"/>
    <circle cx="30" cy="15" r="3" fill="#d9b98a"/>
  </pattern>
  <filter id="soft" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="soft3" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="3.5"/></filter>
  <filter id="cloudL" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.0032 0.0050" numOctaves="4" seed="11"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.78  0 0 0 0 0.92  0 0 0 0 0.95  2.1 0 0 0 -0.95"/>
  </filter>
  <filter id="cloudD" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.0042 0.0060" numOctaves="4" seed="29"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.04  0 0 0 0 0.12  0 0 0 0 0.18  2.1 0 0 0 -0.9"/>
  </filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="3"/>
    <feColorMatrix type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 -0.35"/>
  </filter>
  <clipPath id="crtClip"><rect x="-60" y="-452" width="120" height="92" rx="26"/></clipPath>
</defs>"""


def backdrop():
    s = f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>'
    s += f'<rect width="{W}" height="920" filter="url(#cloudL)" opacity=".55"/>'
    s += f'<rect width="{W}" height="920" filter="url(#cloudD)" opacity=".55"/>'
    s += f'<rect width="{W}" height="920" fill="url(#flash)"/>'
    # floor
    s += f'<rect y="900" width="{W}" height="{H - 900}" fill="url(#floorG)"/>'
    s += f'<rect y="840" width="{W}" height="64" fill="url(#seam)"/>'
    # rug
    s += ell(800, 1040, 745, 150, "#4b1f2b", stroke=OUT, sw=6)
    s += ell(800, 1040, 705, 128, "url(#rugpat)", stroke="#d9b98a", sw=4)
    s += ell(800, 1040, 640, 100, "none", stroke="#d9b98a", sw=2.5,
             extra='stroke-dasharray="3 9" opacity=".7"')
    return s


def drape():
    s = ""
    s += path("M-10,-10 L270,-10 C250,140 190,250 204,420 C214,560 250,700 226,904 L-10,904 Z",
              "url(#curtain)", sw=6)
    s += path("M-10,-10 L610,-10 C560,70 470,150 360,130 C250,112 130,100 -10,210 Z",
              "url(#curtain)", sw=6)
    return s


def leaf(cx, cy, ang, ln, wd, color):
    # leaf pointing along ang from (cx,cy)
    d = (f"M0,0 C{wd},{-ln * .3} {wd * .8},{-ln * .8} 0,{-ln} "
         f"C{-wd * .8},{-ln * .8} {-wd},{-ln * .3} 0,0 Z")
    return (f'<g transform="translate({cx},{cy}) rotate({ang})">'
            f'{path(d, G(color), sw=4)}{path(f"M0,-4 L0,{-ln * .85}", "none", stroke=darken(color, .45), sw=2.5)}</g>')


def column():
    s = ""
    s += rect(1478, 296, 128, 36, 8, G("#e9dfc9"), sw=5)
    s += rect(1492, 330, 100, 560, 6, "url(#column)", sw=5)
    for x in (1512, 1535, 1558, 1578):
        s += path(f"M{x},338 L{x},882", "none", stroke="#6f6553", sw=2, extra='opacity=".55"')
    s += rect(1470, 868, 140, 44, 8, G("#e9dfc9"), sw=5)
    # pot + plant
    s += path("M1508,296 L1520,236 L1580,236 L1592,296 Z", G("#c9663f"), sw=5)
    s += rect(1512, 226, 76, 18, 5, G("#d9784b"), sw=5)
    for ang, ln, wd, c in ((-70, 130, 24, "#3f8a4e"), (-38, 150, 26, "#4aa05a"),
                           (-8, 160, 26, "#3f8a4e"), (22, 150, 26, "#4aa05a"),
                           (54, 128, 24, "#3f8a4e"), (-100, 110, 22, "#4aa05a")):
        s += leaf(1550, 232, ang, ln, wd, c)
    return s


# -------------------------------------------------------------------- DAD --


def dad_body():
    s = ""
    # legs + shoes
    s += rect(-82, -246, 72, 204, 14, G(KHAKI))
    s += rect(10, -246, 72, 204, 14, G(KHAKI))
    s += path("M-46,-230 L-46,-60", "none", stroke=darken(KHAKI, .25), sw=2.5)  # crease
    s += path("M46,-230 L46,-60", "none", stroke=darken(KHAKI, .25), sw=2.5)
    s += rect(-104, -50, 100, 50, 22, G("#4d3528"))
    s += rect(4, -50, 100, 50, 22, G("#4d3528"))
    # torso: argyle vest
    body = dict(x=-128, y=-502, w=256, h=282, r=42)
    s += rect(body["x"], body["y"], body["w"], body["h"], body["r"], "url(#argyle)")
    s += rect(body["x"], body["y"], body["w"], body["h"], body["r"], "url(#shade)", stroke=None)
    # shirt + V-neck + tie
    s += poly([(-58, -498), (58, -498), (0, -372)], SHIRT, sw=4)
    s += poly([(-58, -498), (-22, -498), (-8, -478), (-30, -470)], "#ffffff", sw=3.5)
    s += poly([(58, -498), (22, -498), (8, -478), (30, -470)], "#ffffff", sw=3.5)
    s += rect(-11, -490, 22, 18, 5, G(TIE), sw=3.5)
    s += poly([(-10, -474), (10, -474), (20, -392), (0, -366), (-20, -392)], G(TIE), sw=3.5)
    for i in range(4):
        y = -452 + i * 20
        s += path(f"M-12,{y + 10} L12,{y - 2}", "none", stroke="#c8d6e8", sw=2.5, extra='opacity=".7"')
    # belt
    s += rect(-128, -244, 256, 28, 8, G("#35261f"))
    s += rect(-24, -248, 48, 36, 8, G("#e6c35a"), sw=4)
    s += rect(-12, -238, 24, 16, 4, "none", stroke="#8a6a1c", sw=3)
    # neck
    s += rect(-30, -520, 60, 26, 6, G(STEEL), sw=4)
    return s


def dad_head():
    s = ""
    # cowlick antenna
    s += path("M0,-690 C4,-724 -26,-722 -22,-752", "none", sw=5)
    s += circ(-22, -758, 9, "#d94a3a", sw=4)
    # ears
    s += rect(-128, -622, 26, 60, 9, G(STEEL), sw=4)
    s += rect(102, -622, 26, 60, 9, G(STEEL), sw=4)
    # head shell
    s += rect(-108, -692, 216, 190, 36, G(DAD_SHELL))
    for x, y in ((-90, -674), (90, -674), (-90, -520), (90, -520)):
        s += circ(x, y, 5, darken(DAD_SHELL, .35), sw=2.5)
    # screen
    s += rect(-84, -666, 168, 134, 24, "#121a26", sw=4)
    # wide, unblinking eyes
    for ex in (-44, 44):
        s += circ(ex, -611, 25, "#f6f8fc", sw=3.5)
        s += circ(ex, -611, 8, "#0b0d14", stroke=None)
        s += circ(ex - 2.5, -614, 2.8, "#fff", stroke=None)
    # worried-but-grinning brows
    s += path("M-76,-638 L-24,-653", "none", stroke="#e6f1ff", sw=6)
    s += path("M76,-638 L24,-653", "none", stroke="#e6f1ff", sw=6)
    # rigid grid grin
    s += rect(-68, -574, 136, 34, 11, "#f4f6fa", sw=3.5)
    for x in (-45, -22.5, 0, 22.5, 45):
        s += path(f"M{x},-574 L{x},-540", "none", sw=2.5)
    s += path("M-68,-557 L68,-557", "none", sw=2.5)
    s += path("M-77,-586 Q-84,-558 -72,-546", "none", stroke="#e6f1ff", sw=4)
    s += path("M77,-586 Q84,-558 72,-546", "none", stroke="#e6f1ff", sw=4)
    # nervous oil-sweat
    drop = "M0,-16 C13,2 14,12 0,15 C-14,12 -13,2 0,-16 Z"
    s += f'<g transform="translate(104,-664)">{path(drop, "#8fd8f7", sw=3.5)}</g>'
    s += f'<g transform="translate(-100,-540) scale(.7)">{path(drop, "#8fd8f7", sw=4)}</g>'
    return s


def dad(f):
    return f.wrap(dad_body() + dad_head())


# -------------------------------------------------------------------- MOM --


def mom_body():
    s = ""
    # legs
    for x in (-28, 28):
        s += limb([(x, -196), (x * 1.05, -36)], 22, MOM_METAL, hl=True)
    # shoes
    s += path("M-56,-34 L-8,-34 L-6,-12 Q4,-8 8,0 L-56,0 Z", G("#7a2638"), sw=4.5)
    s += path("M56,-34 L8,-34 L6,-12 Q-4,-8 -8,0 L56,0 Z", G("#7a2638"), sw=4.5)
    # neck + rings
    s += rect(-14, -590, 28, 64, 6, G(MOM_METAL), sw=4)
    for y in (-566, -552, -538):
        s += path(f"M-14,{y} L14,{y}", "none", sw=2.5)
    # dress
    s += path("M-70,-532 Q-74,-470 -52,-404 L-130,-186 Q0,-150 130,-186 L52,-404 "
              "Q74,-470 70,-532 Q0,-496 -70,-532 Z", G(MOM_DRESS))
    for x in (-86, -52, -18, 18, 52, 86):
        s += path(f"M{x * .42},-398 L{x * 1.05},-186", "none", stroke=darken(MOM_DRESS, .2), sw=2.5,
                  extra='opacity=".6"')
    # neckline + collar
    s += path("M-52,-530 Q0,-488 52,-530", "none", stroke=OUT, sw=4)
    s += poly([(-46, -528), (-20, -508), (-52, -496)], G(darken(MOM_DRESS, .12)), sw=3.5)
    s += poly([(46, -528), (20, -508), (52, -496)], G(darken(MOM_DRESS, .12)), sw=3.5)
    # pearls
    for i in range(11):
        t = i / 10
        x = -48 + 96 * t
        y = -526 + 34 * math.sin(math.pi * t) * 0.95
        s += circ(x, y, 7.2, "#fbf3e6", sw=2.8)
    # belt + brooch
    s += rect(-56, -418, 112, 22, 9, G("#8a3a4a"), sw=4)
    s += circ(0, -407, 11, "#e6c35a", sw=3.5)
    s += circ(0, -407, 4, "#d9455e", stroke=None)
    # cap sleeves
    s += ell(-72, -516, 26, 22, G(MOM_DRESS), sw=4.5)
    s += ell(72, -516, 26, 22, G(MOM_DRESS), sw=4.5)
    return s


def mom_head():
    s = ""
    cy = -652
    # hair back + curls
    s += ell(0, cy - 4, 82, 88, G(HAIR))
    s += ell(-74, cy + 46, 24, 20, G(HAIR), sw=4.5, extra='transform="rotate(-20 -74 %d)"' % (cy + 46))
    s += ell(74, cy + 46, 24, 20, G(HAIR), sw=4.5, extra='transform="rotate(20 74 %d)"' % (cy + 46))
    # face plate
    s += ell(0, cy, 62, 70, G(MOM_SKIN))
    # bangs
    s += path("M-62,-668 C-60,-724 -10,-740 36,-724 C62,-712 66,-690 62,-664 "
              "C40,-690 -10,-678 -62,-668 Z", G(HAIR), sw=4.5)
    # rollers still in!
    for x, y, a in ((-34, -724, -16), (2, -734, 4), (38, -726, 22)):
        g = rect(-17, -13, 34, 26, 12, G("#f6a8c4"), sw=4)
        g += path("M-9,-12 L-9,12 M0,-12 L0,12 M9,-12 L9,12", "none", sw=1.8, extra='opacity=".45"')
        g += rect(-6, -19, 12, 8, 3, G("#c9d0da"), sw=3)
        s += f'<g transform="translate({x},{y}) rotate({a})">{g}</g>'
    # earrings
    s += circ(-64, cy + 20, 7, "#fbf3e6", sw=3)
    s += circ(64, cy + 20, 7, "#fbf3e6", sw=3)
    # eyes: both sliding sideways toward the hand on her shoulder
    for ex in (-27, 27):
        s += ell(ex, -652, 17, 13.5, "#fff", sw=3)
        s += circ(ex + 9, -649, 8.2, "#2a8c9a", sw=2.5)
        s += circ(ex + 10.5, -649, 3.8, "#0b0d14", stroke=None)
        s += circ(ex + 7, -652.5, 2, "#fff", stroke=None)
        s += path(f"M{ex - 17},-654 Q{ex},-668 {ex + 17},-654", "none", sw=4)
    # lashes (outer corners)
    s += path("M-43,-658 L-52,-664 M-42,-652 L-52,-652 M-43,-646 L-51,-641", "none", sw=3)
    s += path("M43,-658 L52,-664 M42,-652 L52,-652 M43,-646 L51,-641", "none", sw=3)
    # brows: one arched, one flat and unimpressed
    s += path("M-47,-684 Q-28,-700 -8,-688", "none", stroke=darken(HAIR, .3), sw=4.5)
    s += path("M8,-676 Q28,-678 47,-668", "none", stroke=darken(HAIR, .3), sw=4.5)
    # blush
    s += circ(-42, -626, 11, "#ff8fa0", stroke=None, extra='opacity=".55"')
    s += circ(42, -626, 11, "#ff8fa0", stroke=None, extra='opacity=".55"')
    # fixed smile
    s += path("M-30,-614 Q0,-582 30,-614 Q0,-604 -30,-614 Z", "#c93c55", sw=3.5)
    s += path("M-30,-614 Q0,-598 30,-614", "none", stroke="#fff", sw=2, extra='opacity=".0"')
    s += path("M-36,-622 Q-39,-614 -34,-606", "none", sw=2.5)
    s += path("M36,-622 Q39,-614 34,-606", "none", sw=2.5)
    return s


def mom(f):
    return f.wrap(mom_body() + rot_about(mom_head(), -3, 0, -560))


# ------------------------------------------------------------------- TEEN --


def sneaker(x0, flip=1):
    d = (f"M{x0},0 L{x0},-30 Q{x0},-54 {x0 + 24 * flip},-54 L{x0 + 62 * flip},-52 "
         f"Q{x0 + 104 * flip},-48 {x0 + 108 * flip},-20 L{x0 + 108 * flip},0 Z")
    s = path(d, G("#f4f4ee"), sw=4.5)
    s += rect(min(x0, x0 + 108 * flip) - 2, -13, 112, 13, 5, G(LIME), sw=4)
    for i in range(3):
        xx = x0 + (30 + i * 12) * flip
        s += path(f"M{xx},-50 L{xx + 8 * flip},-40", "none", sw=2.5)
    return s


def teen_body():
    s = ""
    # legs
    s += limb([(-40, -280), (-42, -56)], 44, JEANS)
    s += limb([(44, -280), (52, -56)], 44, JEANS)
    s += sneaker(-60)
    s += sneaker(-12)
    # hoodie torso
    s += path("M-86,-524 Q0,-552 86,-524 L80,-262 Q0,-240 -80,-262 Z", G(TEEN_HOOD))
    s += path("M-56,-376 L56,-376 L66,-296 Q0,-282 -66,-296 Z", G(darken(TEEN_HOOD, .15)), sw=4)
    s += path("M-44,-376 L-56,-298 M44,-376 L56,-298", "none", sw=2.5, extra='opacity=".5"')
    # neck / hood base
    s += ell(0, -534, 72, 28, G(darken(TEEN_HOOD, .2)), sw=4.5)
    # drawstrings
    s += path("M-22,-516 L-26,-440", "none", stroke="#f4f4ee", sw=5)
    s += path("M22,-516 L26,-452", "none", stroke="#f4f4ee", sw=5)
    s += circ(-26, -434, 5.5, LIME, sw=3)
    s += circ(26, -446, 5.5, LIME, sw=3)
    return s


def teen_arms():
    # arms folded tight across the chest
    s = ""
    s += limb([(-88, -508), (-96, -410)], 38, TEEN_HOOD)
    s += limb([(88, -508), (98, -398)], 38, TEEN_HOOD)
    s += limb([(-96, -408), (-24, -382), (58, -420)], 36, TEEN_HOOD)
    s += joint(-96, -408, 15, darken(TEEN_HOOD, .1))
    s += limb([(98, -398), (30, -400), (-52, -440)], 36, darken(TEEN_HOOD, .08))
    s += joint(98, -398, 15, darken(TEEN_HOOD, .1))
    s += hand(66, -428, 70, STEEL, .75)
    s += hand(-60, -448, -70, STEEL, .75)
    return s


def teen_head():
    s = ""
    cy = -610
    # hood
    s += ell(0, cy, 100, 96, G(TEEN_HOOD))
    s += ell(2, cy + 4, 76, 72, G(darken(TEEN_HOOD, .35)), sw=4)
    # screen face
    s += rect(-62, cy - 44, 124, 90, 32, TEEN_SCREEN, sw=4)
    # half-lidded eyes, pupils dragged to the far edge
    for ex in (-26, 26):
        s += path(f"M{ex - 19},{cy - 4} A19,17 0 0 0 {ex + 19},{cy - 4} Z", LIME, sw=0,
                  stroke=None)
        s += circ(ex + 11, cy + 3, 6.8, TEEN_SCREEN, stroke=None)
        s += path(f"M{ex - 22},{cy - 4} L{ex + 22},{cy - 4}", "none", stroke=LIME, sw=5)
    # one lone raised brow, flat mouth with a little kink
    s += path(f"M-44,{cy - 22} L-14,{cy - 20}", "none", stroke=LIME, sw=4.5)
    s += path(f"M14,{cy - 30} L42,{cy - 24}", "none", stroke=LIME, sw=4.5)
    s += path(f"M-16,{cy + 30} L8,{cy + 30} L20,{cy + 25}", "none", stroke=LIME, sw=4.5)
    # headphones
    s += path(f"M-100,{cy + 6} C-108,{cy - 110} 108,{cy - 110} 100,{cy + 6}", "none", stroke=OUT, sw=17)
    s += path(f"M-100,{cy + 6} C-108,{cy - 110} 108,{cy - 110} 100,{cy + 6}", "none", stroke="#2c3345", sw=8)
    for sx in (-1, 1):
        s += rect(sx * 100 - 17, cy - 24, 34, 62, 14, G("#232a3b"), sw=4.5)
        s += rect(sx * 100 - 8 + sx * 3, cy - 12, 16, 38, 7, G(LIME), sw=3)
    return s


def teen(f):
    # slouch: body leans, head tilts further away from dad's hand
    return f.wrap(teen_body() + teen_arms() + rot_about(teen_head(), 7, 0, -540))


# -------------------------------------------------------------------- KID --


def propeller():
    s = ""
    s += rect(-4, -26, 8, 26, 3, G("#f0f0f0"), sw=3)
    s += ell(0, -28, 44, 10, "#ffd23f", stroke=None, extra='opacity=".35"')
    s += rot_about(ell(-24, -28, 24, 7, G("#ffd23f"), sw=3.5), -10, -24, -28)
    s += rot_about(ell(24, -28, 24, 7, G("#ffd23f"), sw=3.5), 10, 24, -28)
    s += circ(0, -28, 6, G("#e5483b"), sw=3.5)
    return s


def kid_body():
    s = ""
    # untied laces on the floor
    # legs + shoes
    s += limb([(-24, -82), (-24, -26)], 24, KID)
    s += limb([(24, -82), (24, -26)], 24, KID)
    s += path("M-52,0 L-52,-18 Q-52,-34 -34,-34 L-8,-34 L-6,-20 Q-4,-6 0,0 Z"
              .replace("-6,-20", "-4,-22"), G("#f08a3c"), sw=4.5)
    s += path("M52,0 L52,-18 Q52,-34 34,-34 L8,-34 L4,-22 Q4,-6 0,0 Z", G("#f08a3c"), sw=4.5)
    s += rect(-52, -12, 52, 12, 5, "#fff", sw=3.5)
    s += rect(0, -12, 52, 12, 5, "#fff", sw=3.5)
    for d in ("M-20,-30 C-34,-20 -56,-20 -62,-2", "M18,-30 C34,-18 58,-22 66,0"):
        s += path(d, "none", stroke=OUT, sw=9)
        s += path(d, "none", stroke="#fff", sw=4)
    # body
    s += ell(0, -122, 56, 66, G(KID))
    s += poly([(0, -150), (7, -132), (26, -132), (11, -120), (17, -102), (0, -112),
               (-17, -102), (-11, -120), (-26, -132), (-7, -132)], G("#ffd23f"), sw=3.5)
    return s


def kid_arms():
    s = ""
    # other hand clutching a lollipop
    s += limb([(-50, -150), (-74, -112), (-70, -80)], 22, KID)
    s += joint(-74, -112, 11, KID)
    s += path("M-70,-76 L-96,-150", "none", stroke="#f4f4ee", sw=7)
    s += circ(-70, -74, 12, G(STEEL), sw=3.5)
    s += circ(-98, -176, 30, "#fff", sw=4.5)
    sp = "M-98,-176 m-4,0 a4,4 0 1 1 8,0 a10,10 0 1 1 -20,0 a16,16 0 1 1 32,0 a22,22 0 1 1 -44,0"
    s += path(sp, "none", stroke="#ff5d8f", sw=5)
    s += path("M-98,-176 m-9,0 a9,9 0 1 1 18,0 a15,15 0 1 1 -30,0", "none", stroke="#38c6d9", sw=4)
    return s


def kid_pointer():
    """Arm thrust straight up at the fly (drawn over the head)."""
    s = limb([(50, -150), (104, -190), (116, -262)], 22, KID)
    s += joint(104, -190, 11, KID)
    s += rect(111, -312, 10, 34, 5, G(STEEL), sw=3)       # index finger
    s += circ(116, -266, 14, G(STEEL), sw=3.5)
    return s


def kid_head():
    s = ""
    cy = -252
    s += circ(-82, cy + 4, 14, G(STEEL), sw=4)
    s += circ(82, cy + 4, 14, G(STEEL), sw=4)
    s += circ(0, cy, 80, G(KID))
    # googly eyes, mismatched, both craned up and to the right
    s += circ(-30, cy + 8, 27, "#fff", sw=4)
    s += circ(-21, cy - 6, 11.5, "#0b0d14", stroke=None)
    s += circ(34, cy + 12, 22, "#fff", sw=4)
    s += circ(41, cy + 1, 9.5, "#0b0d14", stroke=None)
    # cheeks
    s += circ(-52, cy + 40, 11, "#ff9d6e", stroke=None, extra='opacity=".7"')
    s += circ(60, cy + 44, 11, "#ff9d6e", stroke=None, extra='opacity=".7"')
    # gaping mouth with a single big tooth
    s += ell(8, cy + 50, 19, 23, "#3a1620", sw=4)
    s += ell(8, cy + 62, 12, 8, "#ff7f93", stroke=None)
    s += rect(0, cy + 29, 14, 14, 3, "#fff", sw=3)
    # beanie (crooked)
    cap = (f"M-79,{cy - 14} A80,80 0 0 1 79,{cy - 14} "
           f"Q0,{cy + 8} -79,{cy - 14} Z")
    s += path(cap, G(KID_CAP), sw=SW)
    s += path(f"M-40,{cy - 62} Q-30,{cy - 30} -30,{cy - 4}", "none", sw=3, extra='opacity=".5"')
    s += path(f"M40,{cy - 62} Q30,{cy - 30} 30,{cy - 4}", "none", sw=3, extra='opacity=".5"')
    s += path(f"M0,{cy - 80} L0,{cy - 6}", "none", sw=3, extra='opacity=".5"')
    s += rect(-82, cy - 24, 164, 16, 7, G("#ffd23f"), sw=4)
    s += f'<g transform="translate(0,{cy - 78})">{propeller()}</g>'
    return s


def kid(f):
    return f.wrap(kid_body() + kid_arms() + rot_about(kid_head(), 8, 0, -176) + kid_pointer())


# ----------------------------------------------------------------- GRANDPA --


def chair_back():
    s = ""
    s += rect(-152, -548, 304, 372, 66, G(CHAIR))
    s += rect(-104, -498, 208, 300, 44, G(lighten(CHAIR, .1)), sw=4)
    for (x, y) in ((-60, -450), (0, -450), (60, -450), (-30, -400), (30, -400)):
        s += circ(x, y, 7, darken(CHAIR, .4), sw=3)
    # rolled wings
    s += ell(-150, -440, 24, 96, G(darken(CHAIR, .05)), sw=4.5)
    s += ell(150, -440, 24, 96, G(darken(CHAIR, .05)), sw=4.5)
    return s


def chair_seat():
    s = ""
    for x in (-124, 100):
        s += rect(x, -144, 24, 144, 8, G("#5a3a28"), sw=4.5)
    s += rect(-136, -214, 272, 72, 24, G(lighten(CHAIR, .08)))
    s += path("M-118,-190 L118,-190", "none", sw=2.5, extra='opacity=".4"')
    return s


def chair_arms():
    s = ""
    for x in (-180, 120):
        s += rect(x, -306, 62, 170, 28, G(CHAIR), sw=5)
        s += ell(x + 31, -290, 31, 22, G(lighten(CHAIR, .12)), sw=4.5)
    return s


def cane():
    d = "M-240,4 L-190,-322 Q-184,-352 -158,-346 Q-138,-342 -136,-318"
    s = path(d, "none", stroke=OUT, sw=17)
    s += path(d, "none", stroke="#8a5a35", sw=8)
    return s


def gramps_body():
    s = ""
    # legs under the blanket, slippers
    s += limb([(-46, -150), (-46, -26)], 40, "#5d5a67")
    s += limb([(46, -150), (46, -26)], 40, "#5d5a67")
    s += ell(-50, -12, 38, 17, G("#7a4a3a"), sw=4.5)
    s += ell(50, -12, 38, 17, G("#7a4a3a"), sw=4.5)
    # torso: slumped cardigan
    s += path("M-92,-186 Q-104,-298 -54,-340 L54,-340 Q104,-298 92,-186 Z", G(CARDI))
    s += poly([(-30, -340), (0, -296), (-4, -190), (-24, -190), (-52, -300)], G(SHIRT), sw=3.5)
    s += poly([(30, -340), (0, -296), (4, -190), (24, -190), (52, -300)], G(SHIRT), sw=3.5)
    s += path("M0,-296 L0,-190", "none", sw=3)
    for y in (-270, -238, -206):
        s += circ(0, y, 6, "#e9dcb0", sw=3)
    # bow tie
    s += poly([(-2, -322), (-30, -336), (-30, -308)], G("#d94a3a"), sw=3.5)
    s += poly([(2, -322), (30, -336), (30, -308)], G("#d94a3a"), sw=3.5)
    s += circ(0, -322, 6, "#a8322a", sw=3)
    return s


def blanket_and_arms():
    s = ""
    d = "M-124,-216 L124,-216 L138,-128 Q0,-96 -138,-128 Z"
    s += path(d, "url(#plaid)", sw=SW)
    s += path(d, "url(#shade)", stroke=None)
    s += path("M-138,-128 Q0,-96 138,-128", "none", stroke="#f4e6c4", sw=5, extra='stroke-dasharray="2 8"')
    # forearms folded in lap
    s += limb([(-82, -304), (-86, -250), (-24, -222)], 34, CARDI)
    s += limb([(82, -304), (86, -250), (24, -222)], 34, darken(CARDI, .08))
    s += joint(-86, -250, 14, CARDI)
    s += joint(86, -250, 14, CARDI)
    s += hand(-16, -228, 80, GRAMPS, .7)
    s += hand(16, -228, -80, GRAMPS, .7)
    return s


def gramps_head():
    """CRT-television head with rabbit ears; origin at the neck."""
    s = ""
    # neck
    s += rect(-22, -352, 44, 30, 6, G(STEEL), sw=4)
    # rabbit ears
    s += limb([(0, -466), (-66, -566)], 6, "#d8dee6", ow=3, hl=False)
    s += limb([(0, -466), (58, -552), (86, -540)], 6, "#d8dee6", ow=3, hl=False)
    s += circ(-66, -568, 8, G("#e6c35a"), sw=3.5)
    s += circ(86, -540, 8, G("#e6c35a"), sw=3.5)
    s += poly([(-38, -519), (-70, -536), (-56, -508)], "#e6e9ee", sw=3)  # foil scrap
    s += ell(0, -468, 24, 10, G(darken(GRAMPS, .1)), sw=4)
    # casing
    s += rect(-84, -472, 168, 132, 40, G(GRAMPS))
    for (x, y, r) in ((-72, -384, 7), (-54, -456, 9), (60, -452, 7)):
        s += circ(x, y, r, "#5d9b7a", stroke=None, extra='opacity=".55"')
    # speaker grille on the chin
    for i in range(3):
        s += path(f"M-30,{-352 + i * 0} L30,{-352}", "none", stroke="none", sw=0)
    # screen
    s += rect(-62, -454, 124, 96, 28, "url(#crt)", sw=5)
    f = ""
    # glasses (round) with closed eyes
    for ex in (-29, 29):
        f += circ(ex, -414, 21, "#e9ffe9", stroke="#2b3a2f", sw=3.5, extra='fill-opacity=".25"')
        f += path(f"M{ex - 13},{-416} Q{ex},{-404} {ex + 13},{-416}", "none", stroke="#1d3326", sw=4)
    f += path("M-8,-416 Q0,-422 8,-416", "none", stroke="#2b3a2f", sw=3.5)
    # bushy brows
    f += path("M-50,-440 q8,-8 14,0 q8,-8 14,0 q8,-6 12,2", "none", stroke="#f4f4ee", sw=5)
    f += path("M10,-438 q8,-8 14,0 q8,-8 14,0 q8,-6 12,2", "none", stroke="#f4f4ee", sw=5)
    # slack open mouth
    f += ell(0, -370, 8, 6, "#1d3326", stroke=None)
    # handlebar moustache
    mu = "M0,-388 C-10,-396 -30,-396 -42,-384 C-46,-378 -40,-374 -34,-376 C-24,-380 -12,-380 0,-388"
    mu2 = "M0,-388 C10,-396 30,-396 42,-384 C46,-378 40,-374 34,-376 C24,-380 12,-380 0,-388"
    f += path(mu, "#f4f4ee", sw=3.5) + path(mu2, "#f4f4ee", sw=3.5)
    s += f'<g clip-path="url(#crtClip)">{f}'
    # scanlines
    for y in range(-452, -358, 6):
        s += path(f"M-62,{y} L62,{y}", "none", stroke="#0e2a1a", sw=1.2, extra='opacity=".14"')
    s += "</g>"
    # glare
    s += path("M-52,-430 Q-48,-448 -20,-448 Q-40,-440 -52,-420 Z", "url(#glass)", stroke=None)
    s += rect(-60, -452, 120, 92, 26, "none", stroke="#1d3326", sw=2.5, extra='opacity=".5"')
    # low-battery OSD
    s += rect(24, -448, 30, 15, 4, "none", stroke="#d9362b", sw=3)
    s += rect(54, -444, 4, 7, 1.5, "#d9362b", stroke=None)
    s += rect(27, -445, 6, 9, 1.5, "#d9362b", stroke=None)
    # dials
    s += circ(62, -318, 0.1, "none", stroke=None)
    return s


def gramps(f):
    head = rot_about(gramps_head(), 9, 0, -340)
    return f.wrap(chair_back() + chair_seat() + gramps_body() + head
                  + blanket_and_arms() + chair_arms() + cane())


# --------------------------------------------------------------------- DOG --


def dog_body():
    s = ""
    # spring tail
    tail = "M52,-52 Q112,-56 104,-132"
    s += path(tail, "none", stroke=OUT, sw=24)
    s += path(tail, "none", stroke="#8c97a6", sw=14)
    s += path(tail, "none", stroke=OUT, sw=14, extra='stroke-dasharray="3 9" stroke-linecap="butt"')
    s += circ(104, -138, 12, G("#e5483b"), sw=4)
    s += path("M128,-150 Q146,-124 134,-96", "none", sw=4)
    s += path("M142,-166 Q166,-130 150,-88", "none", sw=4)
    # haunches
    s += ell(-62, -44, 26, 40, G(darken(DOG, .08)), sw=4.5)
    s += ell(62, -44, 26, 40, G(darken(DOG, .08)), sw=4.5)
    # body
    s += path("M-54,-124 Q-64,-40 -56,-8 L56,-8 Q64,-40 54,-124 Z", G(DOG))
    s += rect(-30, -96, 60, 44, 12, G(darken(DOG, .12)), sw=3.5)
    for y in (-86, -74, -62):
        s += path(f"M-20,{y} L20,{y}", "none", sw=2.5, extra='opacity=".6"')
    # front legs + paws
    for x in (-30, 30):
        s += limb([(x, -100), (x, -16)], 22, DOG)
        s += rect(x - 22, -22, 44, 22, 10, G(darken(DOG, .1)), sw=4)
    return s


def dog_head():
    s = ""
    # ears: one flopped, one perked
    s += path("M-60,-218 Q-102,-206 -110,-148 Q-102,-122 -84,-132 Q-64,-158 -56,-190 Z",
              G("#7e8fa3"), sw=4.5)
    s += path("M40,-220 Q50,-286 88,-280 Q98,-258 82,-206 Z", G("#7e8fa3"), sw=4.5)
    s += path("M55,-230 Q62,-266 82,-268 Q85,-252 76,-224 Z", "#c9d4e2", stroke=None)
    # head
    s += rect(-68, -224, 136, 104, 30, G(DOG))
    # snout
    s += rect(-46, -176, 92, 58, 24, G(lighten(DOG, .35)), sw=4)
    # eyes
    for ex in (-33, 33):
        s += circ(ex, -198, 17, "#fff", sw=3.5)
        s += circ(ex, -197, 10.5, "#0b0d14", stroke=None)
        s += circ(ex - 3.5, -202, 4, "#fff", stroke=None)
        s += circ(ex + 4, -193, 1.8, "#fff", stroke=None)
    s += path("M-52,-222 L-20,-218 M52,-222 L20,-218", "none", sw=3.5)
    # nose
    s += ell(0, -166, 14, 10, G("#1f2533"), sw=3.5)
    s += ell(-4, -169, 4, 2.5, "#8794aa", stroke=None)
    # mouth
    s += path("M-34,-148 Q0,-116 34,-148", "#2a1d22", sw=3.5)
    # tongue
    s += path("M14,-134 Q30,-136 28,-112 Q20,-100 12,-112 Q8,-122 14,-134 Z", "#ff7f93", sw=3.5)
    # collar + tag
    s += rect(-56, -124, 112, 18, 9, G("#e5483b"), sw=4.5)
    s += circ(0, -98, 11, G("#ffd23f"), sw=3.5)
    s += circ(-5, -98, 4.5, "#ffd23f", sw=3)
    s += circ(5, -98, 4.5, "#ffd23f", sw=3)
    return s


def plug():
    s = ""
    # prongs poke out of the right side of the mouth
    s += rect(18, -151, 24, 7, 2, G("#d9b45a"), sw=2.8)
    s += rect(18, -138, 24, 7, 2, G("#d9b45a"), sw=2.8)
    s += rect(-30, -158, 52, 34, 11, G("#f1f1ea"), sw=4)
    s += path("M-20,-150 L-20,-132 M-12,-150 L-12,-132", "none", sw=2, extra='opacity=".4"')
    # spark
    s += poly([(54, -154), (60, -146), (70, -148), (63, -140), (68, -131), (58, -136), (51, -130),
               (53, -140)], "#ffe66a", sw=2.5)
    return s


def dog(f):
    return f.wrap(dog_body() + dog_head() + plug())


# ---------------------------------------------------------------- the rest --


def fly(x, y):
    s = ""
    trail = (f"M{x - 70},{y + 52} C{x - 80},{y - 4} {x - 22},{y + 10} {x - 30},{y - 22} "
             f"C{x - 38},{y - 50} {x + 4},{y - 44} {x},{y - 6}")
    s += path(trail, "none", stroke="#f3e9c8", sw=2.8, extra='stroke-dasharray="2 8" opacity=".85"')
    g = ""
    g += rot_about(ell(-9, -10, 11, 6, "#e9f6ff", sw=2, extra='fill-opacity=".8"'), -28, -9, -10)
    g += rot_about(ell(9, -10, 11, 6, "#e9f6ff", sw=2, extra='fill-opacity=".8"'), 28, 9, -10)
    g += ell(0, 0, 7, 11, "#14171f", sw=2)
    g += circ(0, -12, 6.5, "#14171f", sw=2)
    g += circ(-3, -13, 2.2, "#e5483b", stroke=None)
    g += circ(3, -13, 2.2, "#e5483b", stroke=None)
    s += f'<g transform="translate({x},{y}) scale(1.35)">{g}</g>'
    return s


def cable_svg(d):
    base = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    s = (f'<path d="{d}" {base} stroke="#0b0d14" stroke-width="16" opacity=".35" '
         f'filter="url(#soft3)" transform="translate(0,10)"/>')
    s += f'<path d="{d}" {base} stroke="{OUT}" stroke-width="16"/>'
    s += f'<path d="{d}" {base} stroke="#586178" stroke-width="8"/>'
    s += (f'<path d="{d}" {base} stroke="#fff" stroke-opacity=".25" stroke-width="2.5" '
          f'transform="translate(-1.5,-2)"/>')
    return s


def build():
    mom_f = Fig(568, 935, rot=-4)
    teen_f = Fig(1262, 948, rot=8)
    dad_f = Fig(880, 935)
    gp_f = Fig(300, 1005)
    kid_f = Fig(702, 992, sc=.9)
    dog_f = Fig(1088, 1120)

    parts = []
    parts.append(backdrop())
    parts.append(drape())
    parts.append(column())

    # floor shadows
    parts.append(shadow(566, 945, 150, 18))
    parts.append(shadow(880, 944, 175, 18))
    parts.append(shadow(1290, 958, 150, 18))
    parts.append(shadow(300, 1008, 230, 22))
    parts.append(shadow(702, 1000, 90, 14))
    parts.append(shadow(1088, 1126, 120, 14))

    # cable from grandpa's chair, tucked behind its leg
    cable_a = "M412,990 C470,1090 580,1175 720,1158 C850,1142 940,1128 990,1098"
    parts.append(cable_svg(cable_a))
    # oil puddle (someone had an accident)
    parts.append(path("M1150,1148 C1148,1134 1186,1131 1214,1135 C1246,1137 1266,1147 1252,1156 "
                      "C1232,1166 1190,1163 1162,1160 C1150,1158 1151,1153 1150,1148 Z",
                      "#10131a", stroke=None, extra='opacity=".88"'))
    parts.append(path("M1170,1146 Q1192,1141 1218,1144", "none", stroke="#7d93b5", sw=2.5, extra='opacity=".75"'))
    parts.append(path("M1226,1150 Q1238,1148 1246,1151", "none", stroke="#a47ac9", sw=2, extra='opacity=".6"'))

    # back row
    parts.append(mom(mom_f))
    parts.append(teen(teen_f))
    parts.append(dad(dad_f))
    # front row
    parts.append(gramps(gp_f))
    parts.append(kid(kid_f))

    # --- arms (global space)
    skin_mom = MOM_METAL
    # mom -> grandpa's shoulder
    ms_l = mom_f.pt(-72, -516)
    g_sh = gp_f.pt(66, -334)
    el = two_bone(ms_l, g_sh, 150, 150, side=-1)
    parts.append(limb([ms_l, el, (g_sh[0], g_sh[1] - 22)], 24, skin_mom))
    parts.append(joint(el[0], el[1], 14, skin_mom))
    parts.append(hand(g_sh[0] + 2, g_sh[1] - 16, 8, skin_mom, .8))

    # mom -> kid's cap
    ms_r = mom_f.pt(72, -516)
    cap = kid_f.pt(-34, -330)
    el = two_bone(ms_r, (cap[0] + 4, cap[1] - 22), 152, 152, side=-1)
    parts.append(limb([ms_r, el, (cap[0] + 4, cap[1] - 24)], 24, skin_mom))
    parts.append(joint(el[0], el[1], 14, skin_mom))
    parts.append(hand(cap[0] + 6, cap[1] - 16, 14, skin_mom, .8))

    # dad -> mom's shoulder (elbow high, hand clamped on from above)
    ds_l = dad_f.pt(-128, -452)
    mh = (ms_r[0] + 2, ms_r[1] - 26)
    el = two_bone(ds_l, mh, 136, 140, side=1)
    parts.append(limb([ds_l, el, mh], 42, SHIRT))
    parts.append(joint(*el, 20, SHIRT))
    parts.append(joint(ds_l[0], ds_l[1], 24, SHIRT))
    # squeeze marks
    for dx, dy, ex, ey in ((-34, -6, -50, -14), (-30, 12, -44, 22), (4, -34, 6, -52)):
        parts.append(path(f"M{mh[0] + dx:.1f},{mh[1] + dy + 18:.1f} L{mh[0] + ex:.1f},{mh[1] + ey + 18:.1f}",
                          "none", stroke="#fff6dc", sw=4))
    parts.append(hand(mh[0], mh[1] + 6, 0, DAD_SHELL, 1.3))

    # dad -> teen's shoulder (nearly straight, taut)
    ds_r = dad_f.pt(128, -452)
    th = teen_f.pt(-84, -526)
    th = (th[0] + 2, th[1] - 14)
    el = two_bone(ds_r, th, 136, 140, side=-1)
    parts.append(limb([ds_r, el, th], 42, SHIRT))
    parts.append(joint(*el, 20, SHIRT))
    parts.append(joint(ds_r[0], ds_r[1], 24, SHIRT))
    parts.append(hand(th[0], th[1] + 8, 0, DAD_SHELL, 1.3))

    # dog + the stolen plug
    parts.append(dog(dog_f))
    mouth = dog_f.pt(-30, -141)
    parts.append(cable_svg(f"M990,1098 C1030,1074 1046,1040 {mouth[0]:.1f},{mouth[1]:.1f}"))
    # the plug's left end re-drawn over the cable so it reads as held
    parts.append(grp(rect(-30, -158, 52, 34, 11, G("#f1f1ea"), sw=4), dog_f.ox, dog_f.oy))

    parts.append(fly(722, 262))

    # finishing
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    parts.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".16"/>')

    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" aria-label="Awkward robot family portrait">\n'
            f'{defs()}\n{body}\n</svg>\n')


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "output", "awkward_robot_family_portrait.svg")
    svg = build()
    with open(out, "w") as fh:
        fh.write(svg)
    print("wrote", os.path.abspath(out), len(svg), "bytes")
