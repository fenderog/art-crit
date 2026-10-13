#!/usr/bin/env python3
"""Awkward robot family portrait.

A studio photograph that did not quite work. Gaze, touch, and spacing
carry the relationships; the picture contains no text.

  Grandpa  — proud obsolete unit, enormous earnest eyes, hand heavy on his son
  Dad      — anxious, overdressed, smile one pixel too wide
  Mom      — holding the baby and the shot together; eyes slip at the shutter
  Baby     — new factory model, watching the softbox, fist in mom's cheek
  Kid      — spare parts from both parents, rabbit ears, one foot on dad
  Teen     — body leaving, eyes down on the dog
  Dog      — bought by dad (his tie's color on the collar), devoted to the teen
"""

import math
import os

W, H = 1600, 1000
FLOOR = 900

# Foot / seat anchors
TEEN_X, TEEN_R = 188, -7
DOG_X, DOG_Y = 348, 952
GP_X = 528
DAD_X, DAD_R = 812, 0
MOM_X, MOM_R = 1052, 4
KID_X, KID_Y, KID_R = 868, 952, -3

INK = "#243038"
INK_SOFT = "#243038"

# Metals
DAD = "#4d6b7e"
DAD_D = "#314858"
DAD_L = "#8aa4b4"
DAD_FACE = "#e4ebef"
SHIRT = "#f4f1e8"
SHIRT_S = "#e2ddd0"
TIE = "#8e3b49"
TIE_D = "#6c2c38"
MOM = "#f0b48e"
MOM_D = "#c4815c"
MOM_L = "#f7d4bc"
MOM_FACE = "#f8c9ac"
DRESS = "#c4546c"
DRESS_D = "#993e54"
DRESS_L = "#d9788a"
GP = "#7e8c5a"
GP_D = "#5a663f"
GP_L = "#aeb888"
GP_FACE = "#ead8b6"
BRASS = "#e4c27a"
BRASS_D = "#b58d45"
BRASS_L = "#f3deb0"
KID = "#f0be3a"
KID_D = "#d3981a"
KID_L = "#ffe59a"
KID_FACE = "#ffebc0"
OVR = "#3c7eab"
OVR_D = "#2c6086"
OVR_L = "#6aa4c8"
TEEN = "#2e3138"
TEEN_M = "#3c404a"
TEEN_L = "#555a66"
TEEN_FACE = "#efe8de"
MAG = "#e4548c"
MAG_D = "#b43368"
BABY_C = "#c5ece0"
BABY_D = "#8fcfb8"
BABY_FACE = "#f4fffb"
DOG = "#f6f3ed"
DOG_D = "#d9d2c6"
DOG_SPOT = "#c47b48"
TONGUE = "#ef7d8b"
WOOD = "#a67c52"
WOOD_D = "#7a5436"
SOLE = "#2a2724"


class D:
    def __init__(self):
        self.o = []

    def add(self, t):
        self.o.append(t)

    def g(self, attrs=""):
        self.add(f"<g {attrs}>" if attrs else "<g>")

    def ge(self):
        self.add("</g>")

    def rect(self, x, y, w, h, r, fill, sw=0, stroke=INK, op=1, extra=""):
        so = f' stroke="{stroke}" stroke-width="{sw}"' if sw else ' stroke="none"'
        oo = f' opacity="{op}"' if op != 1 else ""
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r:.1f}" fill="{fill}"{so}{oo} {extra}/>'
        )

    def ell(self, cx, cy, rx, ry, fill, sw=0, stroke=INK, op=1, extra=""):
        so = f' stroke="{stroke}" stroke-width="{sw}"' if sw else ' stroke="none"'
        oo = f' opacity="{op}"' if op != 1 else ""
        self.add(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}"{so}{oo} {extra}/>'
        )

    def circ(self, cx, cy, r, fill, sw=0, stroke=INK, op=1, extra=""):
        self.ell(cx, cy, r, r, fill, sw, stroke, op, extra)

    def line(self, x1, y1, x2, y2, stroke, sw, op=1, cap="round"):
        oo = f' opacity="{op}"' if op != 1 else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{oo}/>'
        )

    def path(self, d, fill="none", sw=0, stroke=INK, op=1, extra=""):
        so = f' stroke="{stroke}" stroke-width="{sw}"' if sw else ' stroke="none"'
        oo = f' opacity="{op}"' if op != 1 else ""
        self.add(f'<path d="{d}" fill="{fill}"{so}{oo} {extra}/>')

    def bone(self, x1, y1, x2, y2, w, fill, sw=3.2):
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        length = math.hypot(x2 - x1, y2 - y1)
        self.add(
            f'<rect x="0" y="{-w / 2:.1f}" width="{length:.1f}" height="{w:.1f}" '
            f'rx="{w / 2:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" '
            f'transform="translate({x1:.1f},{y1:.1f}) rotate({ang:.2f})"/>'
        )
        # specular streak along the top of the limb
        ox, oy = -math.sin(math.radians(ang)) * (w * 0.22), math.cos(math.radians(ang)) * (w * 0.22)
        # offset toward a consistent "up-left" light by flipping if needed
        self.line(
            x1 + ox * 0.15, y1 + oy * 0.15, x2 + ox * 0.15, y2 + oy * 0.15,
            "#ffffff", max(2.0, w * 0.13), op=0.28,
        )

    def joint(self, x, y, r, fill, bolt=BRASS_D):
        self.circ(x, y, r, fill, sw=3)
        self.circ(x, y, r * 0.38, bolt, sw=1.4)
        self.circ(x - r * 0.12, y - r * 0.14, r * 0.12, "#ffffff", op=0.55)

    def spec(self, cx, cy, rx, ry, op=0.28):
        self.ell(cx, cy, rx, ry, "#ffffff", op=op)

    def shade(self, cx, cy, rx, ry, op=0.13):
        self.ell(cx, cy, rx, ry, "#1a2328", op=op)

    def text_free_badge(self, cx, cy, s=11, fill=BRASS, rot=0, sw=2.2):
        """Family maker's mark: a plain triangle. No lettering."""
        h = s * 1.15
        pts = f"{cx:.1f},{cy - h * 0.62:.1f} {cx - s:.1f},{cy + h * 0.48:.1f} {cx + s:.1f},{cy + h * 0.48:.1f}"
        extra = f'transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"' if rot else ""
        self.add(
            f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>'
        )

    def __str__(self):
        return "\n".join(self.o)


def hand(d, x, y, ang, fill, lengths, spread=9, thick=8, palm=15, thumb=True, thumb_spread=58, sw=2.4):
    """Palm center (x, y). Fingers point along ang (deg, 0=right, -90=up)."""
    a = math.radians(ang)
    n = len(lengths)
    pcx = x
    pcy = y
    # fingers first so the palm caps their bases
    fx = []
    for i, flen in enumerate(lengths):
        off = (i - (n - 1) / 2.0) * (thick + 3.2)
        fa = math.radians(ang + (i - (n - 1) / 2.0) * spread)
        bx = pcx + math.cos(a) * (palm * 0.55) + math.cos(a + math.pi / 2) * off
        by = pcy + math.sin(a) * (palm * 0.55) + math.sin(a + math.pi / 2) * off
        tx = bx + math.cos(fa) * flen
        ty = by + math.sin(fa) * flen
        d.bone(bx, by, tx, ty, thick, fill, sw=sw)
        fx.append((tx, ty))
    d.ell(pcx, pcy, palm, palm * 0.86, fill, sw=sw + 0.4)
    d.spec(pcx - palm * 0.25, pcy - palm * 0.28, palm * 0.28, palm * 0.18, 0.35)
    if thumb:
        ta = math.radians(ang + thumb_spread)
        bx = pcx + math.cos(ta) * palm * 0.2 + math.cos(a + math.pi / 2) * palm * 0.15
        by = pcy + math.sin(ta) * palm * 0.2 + math.sin(a + math.pi / 2) * palm * 0.15
        # place thumb on the side opposite the finger fan's "inner"
        side = thumb_spread / abs(thumb_spread) if thumb_spread else 1
        bx = pcx + math.cos(a + side * math.pi / 2) * palm * 0.72
        by = pcy + math.sin(a + side * math.pi / 2) * palm * 0.72
        tx = bx + math.cos(ta) * palm * 0.95
        ty = by + math.sin(ta) * palm * 0.95
        d.bone(bx, by, tx, ty, thick * 1.05, fill, sw=sw)
    return fx


def eye(d, cx, cy, rx, ry, dx, dy, iris, skin, lid=0.0, cloudy=False, ring="#c5d0d6"):
    """Lid is 0..1 coverage from the top, painted in the face color."""
    d.ell(cx, cy, rx + 6.5, ry + 6.5, INK)
    d.ell(cx, cy, rx + 3.2, ry + 3.2, ring)
    d.ell(cx, cy, rx, ry, "#f5f8f8")
    d.ell(cx + dx, cy + dy, rx * 0.62, ry * 0.66, iris)
    d.ell(cx + dx, cy + dy, rx * 0.30, ry * 0.34, "#16191c")
    # catchlight, upper right — the in-frame softbox
    d.ell(cx + dx + rx * 0.26, cy + dy - ry * 0.30, max(2.2, rx * 0.16), max(1.8, ry * 0.14), "#ffffff")
    d.ell(cx + dx - rx * 0.18, cy + dy + ry * 0.22, max(1.2, rx * 0.07), max(1.0, ry * 0.06), "#ffffff", op=0.7)
    if cloudy:
        d.ell(cx, cy, rx * 0.92, ry * 0.92, "#d5ddd8", op=0.55)
        d.ell(cx + 4, cy + 3, rx * 0.35, ry * 0.22, "#ffffff", op=0.25)
    if lid > 0:
        cover = ry * (0.15 + 1.15 * lid)
        # skin-colored lid cap
        d.path(
            f"M {cx - rx - 7:.1f} {cy + ry * 0.15:.1f} "
            f"Q {cx:.1f} {cy - ry - 8 + cover * 0.15:.1f} {cx + rx + 7:.1f} {cy + ry * 0.15:.1f} "
            f"L {cx + rx + 8:.1f} {cy - ry - 14:.1f} L {cx - rx - 8:.1f} {cy - ry - 14:.1f} Z",
            fill=skin,
        )
        # lash line
        d.path(
            f"M {cx - rx + 1:.1f} {cy - ry * (0.15 + lid * 0.7):.1f} "
            f"Q {cx:.1f} {cy - ry * (0.55 + lid * 0.5):.1f} {cx + rx - 1:.1f} {cy - ry * (0.15 + lid * 0.7):.1f}",
            sw=3.2, stroke=INK,
        )


def brow(d, cx, cy, w, rot, color, thick=7):
    d.add(
        f'<rect x="{cx - w / 2:.1f}" y="{cy - thick / 2:.1f}" width="{w:.1f}" height="{thick:.1f}" '
        f'rx="{thick / 2:.1f}" fill="{color}" stroke="{INK}" stroke-width="1.6" '
        f'transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"/>'
    )


def vent_nose(d, cx, cy, s=1.0, color=None):
    color = color or INK
    for i, w in enumerate((16, 12, 8)):
        ww = w * s
        d.rect(cx - ww / 2, cy + i * 6.2 * s, ww, 3.1 * s, 1.4 * s, color, sw=1.2)


def button_nose(d, cx, cy, r=7, fill=None):
    fill = fill or "#e09878"
    d.circ(cx, cy, r, fill, sw=2.2)
    d.circ(cx - r * 0.28, cy - r * 0.32, r * 0.28, "#ffffff", op=0.65)


def rivet(d, x, y, r=4.2, fill=BRASS):
    d.circ(x, y, r, fill, sw=1.6)
    d.line(x - r * 0.5, y, x + r * 0.5, y, BRASS_D, 1.2)


def studio(d):
    # Muslin sweep. Cool, a little tired, lighter behind the cluster
    # (they missed the mark, which sits further right).
    d.rect(0, 0, W, H, 0, "#5e7c86")
    d.ell(760, 380, 620, 460, "#86a4ac", op=0.55)
    d.ell(700, 340, 340, 280, "#c3d4d4", op=0.22)
    d.ell(-40, 80, 380, 320, "#3e5962", op=0.28)
    d.ell(1680, 60, 420, 300, "#3a5360", op=0.25)
    d.ell(200, 520, 260, 180, "#6d8e96", op=0.18)
    d.ell(1100, 180, 220, 160, "#78969e", op=0.16)
    d.ell(1420, 460, 280, 220, "#4c6872", op=0.20)
    # blotches — painted muslin, not a flat ramp
    blot = [
        (280, 160, 90, 50, 0.07),
        (520, 90, 120, 40, 0.06),
        (900, 140, 80, 36, 0.05),
        (1240, 220, 100, 46, 0.07),
        (640, 260, 70, 30, 0.05),
        (1040, 80, 90, 34, 0.06),
    ]
    for x, y, rx, ry, op in blot:
        d.ell(x, y, rx, ry, "#d5e4e4", op=op)
        d.ell(x + 30, y + 18, rx * 0.6, ry * 0.5, "#3e5962", op=op)

    # Unfortunate seam in the gap between the teen and grandpa.
    d.path(
        "M392 0 C 404 80, 378 160, 396 260 C 414 360, 372 460, 390 560 C 400 620, 384 660, 392 720",
        sw=14, stroke="#6e9096", op=0.35,
    )
    d.path(
        "M402 0 C 414 80, 388 160, 406 260 C 424 360, 382 460, 400 560 C 410 620, 394 660, 402 720",
        sw=3, stroke="#e4f0f0", op=0.35,
    )

    # Floor of the sweep, warmer where the strobe hits.
    d.path(
        "M0 630 C 260 548, 980 540, 1280 600 C 1420 632, 1520 640, 1600 626 L1600 1000 L0 1000 Z",
        fill="#b7a48c",
    )
    d.path(
        "M0 650 C 280 580, 1000 572, 1280 628 C 1440 658, 1540 660, 1600 650 L1600 1000 L0 1000 Z",
        fill="#cbb89a", op=0.85,
    )
    d.path(
        "M0 600 C 300 530, 1100 524, 1600 610",
        sw=18, stroke="#000000", op=0.06,
    )
    # scuffed highlight along the curve
    d.path(
        "M40 640 C 340 575, 1080 568, 1500 640",
        sw=3, stroke="#efe4d0", op=0.35,
    )
    # soft floor falloff at the edges
    d.ell(-20, 980, 500, 220, "#8d7b64", op=0.35)
    d.ell(1620, 990, 480, 240, "#8a7862", op=0.28)
    d.ell(820, 1040, 700, 120, "#d8c7ad", op=0.25)

    # Paper clips along the top, and a peeled corner — the sweep is tired.
    for cx in (180, 610, 1040):
        d.rect(cx - 16, -6, 32, 22, 3, "#2e3438", sw=2)
        d.rect(cx - 8, 8, 16, 10, 2, "#8d97a0", sw=1.5)
    # peeled top-right corner
    d.path(
        "M1488 0 L1600 0 L1600 78 L1564 52 Q1524 36 1488 0 Z",
        fill="#d9e3e2", sw=2.4,
    )
    d.path("M1600 78 Q1560 48 1510 28", sw=2, stroke="#b7c4c4", op=0.8)

    # Light stand accidentally in frame. One barn door hanging open.
    sx = 1496
    d.line(sx, 214, sx, 848, "#c5ccd1", 8)
    d.line(sx - 2, 214, sx - 2, 848, "#ffffff", 2, op=0.35)
    d.line(sx, 820, sx - 78, 910, "#b7c0c6", 6)
    d.line(sx, 820, sx + 62, 906, "#b7c0c6", 6)
    d.line(sx, 820, sx + 4, 932, "#aeb8be", 6)
    d.circ(sx - 78, 910, 7, "#8d979e", sw=2)
    d.circ(sx + 62, 906, 7, "#8d979e", sw=2)
    d.circ(sx + 4, 932, 7, "#8d979e", sw=2)
    # softbox mounted on the pole, tilted a little high
    d.g(f'transform="translate({sx},168) rotate(-7)"')
    d.rect(-8, 36, 16, 28, 3, "#8d979e", sw=2)
    d.rect(-86, -58, 172, 112, 10, "#2c3136", sw=3)
    d.rect(-72, -46, 144, 88, 5, "#f4f7f8", sw=2)
    d.ell(-8, -10, 34, 20, "#ffffff", op=0.55)
    d.rect(-104, -50, 16, 96, 2, "#1e2328", sw=2.2)
    d.ge()
    d.g(f'transform="translate({sx + 78},132) rotate(42)"')
    d.rect(0, -8, 56, 16, 2, "#1e2328", sw=2.2)
    d.ge()
    d.path(
        f"M{sx} 848 C {sx + 32} 828, {sx + 58} 888, {sx + 18} 900 C {sx - 18} 910, {sx - 32} 852, {sx + 16} 844",
        sw=4, stroke="#2a3136",
    )

    # Gaffer mark they were supposed to stand on. Empty.
    d.g('transform="translate(1310,868) rotate(-6)"')
    d.rect(-46, -7, 92, 14, 2, "#e2b434", sw=0)
    d.rect(-7, -7, 14, 46, 2, "#e2b434", sw=0)
    d.rect(-46, -7, 92, 3, 1, "#f2d98a", sw=0, op=0.7)
    d.ge()

    # Small plastic fern, too green, one leaf giving up.
    d.g('transform="translate(1368,792)"')
    d.path("M-18 78 L-26 118 L30 118 L20 78 Z", fill="#8d6244", sw=2.4)
    d.ell(0, 78, 26, 9, "#a67c52", sw=2.2)
    d.ell(0, 74, 16, 5, "#c4a27a", op=0.7)
    for ang, col, ry in (
        (-50, "#3f8f62", 34),
        (-20, "#2f7a52", 40),
        (15, "#46a06e", 36),
        (42, "#2c6e48", 30),
        (68, "#c2b24a", 26),  # yellowing
    ):
        d.g(f'transform="rotate({ang} 0 70)"')
        d.ell(0, 70 - ry, 8, ry, col, sw=2)
        d.line(0, 70, 0, 70 - ry * 1.5, "#1e4630", 1.4, op=0.7)
        d.ge()
    d.ge()


def shadows(d):
    # Merged pool under the pile that stood too close, and a separate one
    # under the teen. The dog's shadow is the bridge.
    d.ell(860, 892, 430, 34, "#2a241c", op=0.16, extra='filter="url(#blur18)"')
    d.ell(200, 888, 78, 15, "#2a241c", op=0.16, extra='filter="url(#blur12)"')
    d.ell(348, 940, 80, 15, "#2a241c", op=0.15, extra='filter="url(#blur12)"')
    # contact
    for x, y, rx in (
        (200, 896, 46),
        (528, 898, 70),
        (812, 898, 62),
        (1048, 898, 58),
        (900, 946, 36),
        (348, 948, 40),
    ):
        d.ell(x, y, rx, 8, "#241e18", op=0.28, extra='filter="url(#blur4)"')


def dad_body(d):
    """Anxious middle model. Same skull as his father, panels instead of rivets."""
    d.g(f'transform="translate({DAD_X},{FLOOR}) rotate({DAD_R})"')

    # feet, obedient, both aimed at the lens. Right shoe gets stepped on later.
    for sx, lean in ((-86, 0), (28, 0)):
        d.ell(sx + 30, -6, 36, 14, "#1c2126", op=0.25)
        d.rect(sx, -38, 66, 30, 10, DAD_D, sw=3)
        d.rect(sx + 4, -34, 58, 12, 6, DAD, sw=0)
        d.spec(sx + 16, -30, 16, 4, 0.4)
        d.rect(sx + 8, -14, 50, 8, 3, SOLE, sw=0)

    # legs
    d.bone(-52, -250, -58, -48, 40, DAD, sw=3.2)
    d.bone(58, -250, 64, -48, 40, DAD, sw=3.2)
    d.joint(-58, -150, 16, DAD_D)
    d.joint(64, -148, 16, DAD_D)
    # knee highlights already in joint

    # hips and the dad-bod plate
    d.rect(-96, -318, 196, 78, 22, DAD, sw=3.2)
    d.ell(18, -300, 74, 46, DAD, sw=3)
    d.shade(18, -278, 60, 22, 0.1)
    d.rect(-100, -308, 204, 24, 8, DAD_D, sw=2.6)
    d.rect(-20, -312, 40, 22, 4, BRASS, sw=2.2)
    d.rect(-12, -307, 24, 12, 2, BRASS_L, sw=0)

    # torso
    d.rect(-104, -548, 210, 250, 32, DAD, sw=3.4)
    d.shade(10, -360, 80, 40, 0.08)
    d.spec(-40, -500, 50, 22, 0.16)
    # shirt panel
    d.path(
        "M-78 -530 L78 -524 L70 -360 Q 0 -348 -74 -366 Z",
        fill=SHIRT, sw=3,
    )
    d.shade(0, -390, 50, 18, 0.05)
    # collar
    d.path("M-28 -528 L-6 -490 L8 -528", fill=SHIRT, sw=2.6)
    d.path("M-22 -530 L-2 -498", sw=2.4, stroke=SHIRT_S)
    d.path("M22 -526 L4 -496", sw=2.4, stroke=SHIRT_S)
    # crooked tie — the knot sits off to his left, the blade drifts right
    d.path(
        "M-4 -512 L14 -508 L22 -360 L4 -352 L-8 -366 Z",
        fill=TIE, sw=2.6,
    )
    d.path("M2 -500 L16 -496 L12 -470 L0 -474 Z", fill=TIE_D, sw=0)
    d.line(6, -450, 14, -370, "#c46874", 3, op=0.45)
    # family mark, pinned a few degrees off
    d.text_free_badge(46, -470, s=10, fill=BRASS, rot=-8, sw=1.8)
    # pen in the pocket, also crooked
    d.rect(36, -430, 16, 22, 2, SHIRT_S, sw=1.4)
    d.g('transform="rotate(8 44 -418)"')
    d.rect(40, -448, 5, 28, 1.5, "#2d4a62", sw=1)
    d.rect(40, -450, 5, 6, 1, BRASS, sw=0.8)
    d.ge()
    # subtle panel seams
    d.line(-104, -430, 106, -424, INK, 1.5, op=0.18)
    d.line(4, -524, 8, -330, INK, 1.4, op=0.12)

    # neck
    d.rect(-30, -590, 62, 52, 14, DAD, sw=3)
    d.rect(-22, -582, 46, 10, 4, DAD_L, sw=0, op=0.7)

    # shoulders
    d.circ(-118, -500, 38, DAD, sw=3.2)
    d.spec(-132, -516, 12, 8, 0.3)
    d.circ(122, -492, 38, DAD, sw=3.2)
    d.spec(108, -508, 12, 8, 0.25)

    # hanging arm (his right / image left) — he does not know what to do with it
    d.bone(-118, -500, -156, -390, 36, DAD)
    d.bone(-156, -390, -142, -270, 32, DAD_D)
    d.joint(-156, -390, 16, DAD_L)
    d.joint(-142, -270, 12, DAD_L)
    hand(d, -142, -250, 78, DAD, [16, 18, 16, 14], spread=7, thick=8, palm=13, thumb_spread=-60)

    # head — tall rounded skull, the updated version of grandpa's
    d.rect(-82, -778, 164, 200, 42, DAD, sw=3.4)
    d.shade(8, -640, 60, 28, 0.08)
    d.spec(-30, -740, 40, 18, 0.22)
    # face plate
    d.rect(-66, -754, 132, 156, 34, DAD_FACE, sw=2.6)
    d.shade(0, -640, 48, 20, 0.05)
    # ear plates (same design as grandpa, smaller bolts)
    d.rect(-100, -700, 22, 36, 8, DAD_D, sw=2.4)
    d.rect(78, -696, 22, 36, 8, DAD_D, sw=2.4)
    d.circ(-90, -682, 4, BRASS_D, sw=1)
    d.circ(90, -678, 4, BRASS_D, sw=1)

    # worried brows, inner corners up
    brow(d, -34, -724, 32, -18, DAD_D, thick=7)
    brow(d, 36, -722, 32, 16, DAD_D, thick=7)
    # wide eyes, too much sclera, pupils pinned on the lens
    eye(d, -32, -688, 18, 20, 0, -1, "#3d8f9a", DAD_FACE, lid=0.02)
    eye(d, 34, -686, 18, 20, 1, -1, "#3d8f9a", DAD_FACE, lid=0.02)
    vent_nose(d, 2, -652, s=1.05)
    # too-wide LED smile, last tooth dead, whole grille crooked
    d.g('transform="rotate(-5 4 -600)"')
    d.rect(-52, -618, 108, 30, 12, "#1c2428", sw=2.6)
    for i in range(8):
        col = "#f4faf6" if i != 7 else "#2c3a36"
        d.rect(-44 + i * 12.4, -612, 8.6, 16, 2, col, sw=1)
    d.ge()
    # oil bead at the temple
    d.circ(62, -724, 5.5, "#7f97a4", sw=1.6)
    d.circ(60, -726, 2, "#ffffff", op=0.75)
    d.ell(66, -714, 2.2, 3.4, "#7f97a4", sw=1.2)

    d.ge()


def grandpa(d):
    """Seated on a stool that is too small. Holds his son's dangling hand and does not notice."""
    d.g(f'transform="translate({GP_X},{FLOOR})"')

    # Stool, shifted left: he is perched on its right edge.
    d.line(-58, -150, -78, -4, WOOD_D, 7)
    d.line(-6, -150, -18, -2, WOOD, 6)
    d.line(18, -148, 28, -4, WOOD, 6)
    d.line(46, -150, 70, -2, WOOD_D, 7)
    d.path("M-62 -78 Q 0 -90 58 -74", sw=4.5, stroke="#6a4630")
    d.ell(-16, -154, 52, 15, WOOD_D, sw=2.4)
    d.ell(-16, -160, 52, 14, WOOD, sw=2.6)
    d.spec(-36, -164, 18, 4, 0.4)

    d.ell(6, -168, 70, 30, GP, sw=3.2)

    # Torso, vest, the one perfect bow tie.
    d.rect(-74, -352, 152, 200, 26, GP, sw=3.3)
    d.spec(-28, -324, 34, 14, 0.16)
    d.path(
        "M-54 -338 L56 -334 L48 -178 Q 4 -166 -48 -182 Z",
        fill=GP_D, sw=2.8,
    )
    d.path("M-14 -340 L16 -338 L12 -286 L-12 -288 Z", fill="#f0e6d2", sw=2)
    d.ell(-16, -346, 13, 8, BRASS, sw=2.2)
    d.ell(16, -346, 13, 8, BRASS, sw=2.2)
    d.circ(0, -346, 6, BRASS_D, sw=2)
    d.spec(-20, -350, 4, 2, 0.65)
    for yy in (-308, -268, -228):
        d.circ(2, yy, 5.2, BRASS, sw=1.8)
        d.line(-1, yy, 5, yy, BRASS_D, 1.2)
    d.text_free_badge(0, -268, s=12, fill=BRASS_L, rot=0, sw=2)
    d.path("M16 -268 C 36 -260, 44 -224, 32 -210", sw=2, stroke=BRASS_D)
    d.circ(30, -202, 10, BRASS, sw=2)
    d.circ(30, -202, 6.5, "#f4efe4", sw=1.2)
    d.line(30, -202, 30, -197, INK, 1.3)
    d.circ(30, -202, 1.3, INK)
    d.ell(-44, -210, 9, 6, "#a85a38", op=0.5)

    # Neck and shoulders.
    d.rect(-24, -390, 50, 44, 12, GP, sw=3)
    d.circ(-84, -332, 28, GP, sw=3.2)
    d.circ(82, -328, 28, GP, sw=3.2)
    rivet(d, -96, -332, 3.4)
    rivet(d, 94, -328, 3.4)

    # Image-right arm lays across his son's hanging forearm. The fist stays closed.
    d.bone(82, -328, 150, -340, 30, GP)
    d.bone(150, -340, 196, -360, 26, GP_L)
    d.joint(150, -340, 13, GP_D, bolt=BRASS)

    # Image-left arm comes forward onto the cane between his knees.
    d.bone(-84, -332, -60, -240, 28, GP)
    d.bone(-60, -240, -28, -180, 24, GP_D)
    d.joint(-60, -240, 12, GP_L, bolt=BRASS)

    # Head. Same wide earnest CRT, now at a seated height.
    d.rect(-96, -572, 190, 196, 36, GP, sw=3.4)
    d.spec(-40, -544, 44, 16, 0.18)
    d.shade(0, -420, 68, 22, 0.08)
    d.rect(-78, -552, 156, 158, 28, GP_FACE, sw=2.8)
    d.rect(-118, -500, 26, 42, 10, GP_D, sw=2.6)
    d.rect(90, -496, 26, 42, 10, GP_D, sw=2.6)
    rivet(d, -106, -480, 4)
    rivet(d, 104, -476, 4)
    d.line(18, -572, 18, -628, GP_D, 6)
    d.path("M18 -628 Q 18 -656 38 -654", sw=6, stroke=GP_D)
    d.circ(42, -654, 9, BRASS, sw=2.4)
    d.spec(38, -658, 3, 2, 0.7)
    rivet(d, -62, -430, 3.6)
    rivet(d, 64, -426, 3.6)
    rivet(d, -70, -530, 3.3)
    rivet(d, 72, -526, 3.3)
    d.ell(-46, -500, 7, 5, "#a85a38", op=0.4)
    brow(d, -40, -524, 40, -6, "#6a6248", thick=8)
    brow(d, 42, -522, 40, 6, "#6a6248", thick=8)
    eye(d, -38, -484, 26, 28, 0, 0, "#6aa4a8", GP_FACE, lid=0.0, cloudy=True, ring=BRASS)
    eye(d, 42, -482, 26, 28, 0, 0, "#6aa4a8", GP_FACE, lid=0.0, ring=BRASS)
    vent_nose(d, 2, -436, s=1.2, color="#5c5346")
    d.path("M-26 -410 Q 2 -396 32 -408", sw=4, stroke="#5c5346")
    d.rect(-34, -400, 70, 26, 6, "#5c5346", sw=2)
    for i in range(4):
        d.rect(-28, -394 + i * 5.6, 58, 2.2, 1, GP_FACE, sw=0)
    d.path("M-8 -418 Q -30 -408 -16 -398", sw=3.4, stroke="#b7a48a")
    d.path("M8 -418 Q 32 -406 18 -396", sw=3.4, stroke="#b7a48a")

    # Seat lip in front of the hips, then a wide bent-leg sit so the stool reads.
    d.path(
        "M-110 -150 C -70 -118, 70 -118, 110 -150 L 104 -162 C 66 -136, -66 -136, -104 -162 Z",
        fill=WOOD, sw=2.4,
    )
    d.bone(-36, -156, -128, -124, 40, GP)
    d.bone(40, -154, 124, -118, 40, GP)
    d.joint(-128, -124, 22, GP_D, bolt=BRASS)
    d.joint(124, -118, 22, GP_D, bolt=BRASS)
    d.ell(116, -112, 9, 6, "#a85a38", op=0.45)
    d.bone(-128, -124, -116, -36, 30, GP_D)
    d.bone(124, -118, 112, -36, 30, GP_D)
    for sx in (-148, 80):
        d.rect(sx, -34, 64, 28, 9, GP_D, sw=3)
        d.rect(sx + 3, -30, 56, 10, 5, GP_L, sw=0)
        d.spec(sx + 16, -26, 16, 3.5, 0.6)
        d.rect(sx + 8, -12, 48, 7, 2, SOLE, sw=0)

    # Cane between his knees, handle in the hand.
    d.line(-24, -172, -18, -4, BRASS_D, 7)
    d.line(-22, -172, -16, -4, BRASS_L, 2.2, op=0.5)
    d.path("M-24 -172 C -62 -178, -66 -140, -30 -132", sw=7, stroke=BRASS_D)
    d.circ(-18, 0, 6.5, "#6a4630", sw=2)
    hand(d, -30, -164, 100, GP, [12, 14, 12], spread=6, thick=8, palm=13, thumb_spread=-55)

    # Laid over the son's forearm.
    hand(d, 210, -368, -16, GP_L, [16, 18, 15], spread=7, thick=9, palm=15, thumb_spread=60)

    d.ge()


def mom_and_baby(d):
    """She aimed her face at the camera. Her eyes went to the baby anyway."""
    d.g(f'transform="translate({MOM_X},{FLOOR}) rotate({MOM_R})"')

    # feet, one turned slightly toward the baby
    d.g('transform="translate(-70,-8) rotate(8)"')
    d.rect(-20, -28, 58, 28, 10, MOM_D, sw=3)
    d.rect(-16, -24, 48, 10, 5, MOM_L, sw=0)
    d.rect(-12, -8, 42, 7, 2, SOLE, sw=0)
    d.ge()
    d.g('transform="translate(28,-4) rotate(-12)"')
    d.rect(-16, -28, 58, 28, 10, MOM_D, sw=3)
    d.rect(-12, -24, 48, 10, 5, MOM_L, sw=0)
    d.rect(-8, -8, 42, 7, 2, SOLE, sw=0)
    d.ge()

    # legs
    d.bone(-46, -250, -52, -40, 36, MOM)
    d.bone(40, -246, 48, -36, 36, MOM)
    d.joint(-50, -140, 14, MOM_D)

    # hips / skirt
    d.path(
        "M-92 -300 Q -120 -80 -78 -20 L 96 -8 Q 132 -90 100 -300 Z",
        fill=DRESS, sw=3.3,
    )
    d.path(
        "M-70 -286 Q -92 -90 -58 -36 L 78 -26 Q 104 -100 82 -290 Z",
        fill=DRESS_L, sw=0, op=0.35,
    )
    # hem band a little uneven
    d.path("M-78 -28 Q 10 -8 98 -16", sw=8, stroke=DRESS_D)
    # pocket with a wrench she did not have time to put down
    d.rect(-78, -150, 40, 32, 6, DRESS_D, sw=2)
    d.path("M-70 -168 L-62 -168 L-64 -146 L-58 -146 L-60 -168 L-52 -168", sw=3, stroke=BRASS, fill="none")
    d.circ(-61, -144, 4, BRASS, sw=1.4)

    # torso
    d.path(
        "M-78 -520 C -110 -460 -100 -340 -92 -300 L 100 -300 C 112 -360 100 -470 82 -518 Z",
        fill=MOM, sw=3.3,
    )
    d.spec(-30, -490, 30, 16, 0.2)
    # dress bodice
    d.path(
        "M-64 -500 C -86 -450 -78 -360 -70 -318 L 78 -318 C 86 -380 74 -460 66 -502 Z",
        fill=DRESS, sw=2.8,
    )
    # buttons down the front, one skipped (she dressed in a hurry)
    for i, yy in enumerate((-470, -430, -350)):
        d.circ(4, yy, 4.5, BRASS_L, sw=1.5)
    # the skipped button, thread hole only
    d.circ(4, -390, 2.2, DRESS_D, sw=1)

    # neck
    d.rect(-24, -558, 50, 46, 14, MOM, sw=3)
    # pearls, one missing on the baby side
    for i, (px, py) in enumerate(
        ((-28, -546), (-14, -538), (0, -534), (16, -536), (32, -544), (48, -558))
    ):
        if i == 4:
            continue  # baby has this one
        d.circ(px, py, 6.2, "#f7f3ea", sw=1.8)
        d.spec(px - 2, py - 2, 2, 1.4, 0.8)

    # shoulders
    d.circ(-96, -490, 32, MOM, sw=3.2)
    d.circ(102, -486, 34, MOM, sw=3.2)
    d.spec(-110, -504, 10, 6, 0.35)

    # her right arm (image left): frozen mid-reach toward the kid's undone strap.
    # Dad's hand has pinned the shoulder, so the forearm just hovers.
    d.bone(-96, -490, -70, -390, 30, MOM)
    d.bone(-70, -390, -150, -300, 26, MOM_D)
    d.joint(-70, -390, 13, MOM_L)
    d.joint(-150, -300, 11, MOM_L)
    hand(d, -168, -286, 168, MOM, [20, 22, 20, 16], spread=10, thick=7.5, palm=13, thumb_spread=64)

    # her left arm (image right) cradles the baby — competent, tired
    d.bone(102, -486, 150, -400, 32, MOM)
    d.bone(150, -400, 128, -300, 30, MOM_D)
    d.joint(150, -400, 14, MOM_L)
    # forearm continues under the baby; hand peeks behind baby's legs later

    # coil bob. one coil has sprung free on the side away from dad's hand.
    coils = [
        (-58, -610, 26), (-36, -660, 24), (0, -688, 26),
        (40, -664, 24), (62, -618, 26), (-78, -560, 20),
        (78, -552, 20), (-20, -640, 22), (24, -630, 20),
    ]
    for cx, cy, r in coils:
        d.circ(cx, cy, r, MOM_D, sw=2.6)
        d.spec(cx - 6, cy - 8, r * 0.35, r * 0.25, 0.35)
    # the escaped coil
    d.g('transform="translate(-96,-640) rotate(-28)"')
    d.ell(0, 0, 16, 28, MOM_D, sw=2.6)
    d.ell(-4, -8, 6, 10, MOM_L, op=0.45)
    d.ge()

    # head
    d.ell(4, -600, 74, 80, MOM, sw=3.4)
    d.spec(-24, -650, 28, 16, 0.25)
    d.ell(4, -598, 60, 64, MOM_FACE, sw=2.6)
    # ears
    d.ell(-74, -590, 14, 18, MOM, sw=2.6)
    d.ell(82, -586, 14, 18, MOM, sw=2.6)
    # one earring left. the other is in the baby's fist.
    d.circ(-86, -578, 7, "#f7f3ea", sw=1.8)
    d.spec(-88, -580, 2.2, 1.6, 0.8)
    d.circ(92, -574, 2.4, MOM_D, sw=1)  # empty piercing

    # brows: the baby-side one is up
    brow(d, -24, -640, 28, -8, "#a86448", thick=6)
    brow(d, 30, -642, 28, -14, "#a86448", thick=6)
    # eyes slid toward the baby (image right and a little down)
    eye(d, -24, -612, 16, 15, 5, 4, "#c46a4a", MOM_FACE, lid=0.18)
    eye(d, 28, -610, 16, 15, 6, 5, "#c46a4a", MOM_FACE, lid=0.22)
    button_nose(d, 4, -578, r=7, fill="#e09878")
    # OLED smile, soft, rose — the baby will cover the near corner
    d.path(
        "M-22 -548 Q 4 -532 26 -546",
        sw=5, stroke="#b84d62",
    )
    d.path(
        "M-22 -548 Q 4 -536 26 -546",
        sw=2, stroke="#f0a0ae", op=0.7,
    )
    # blush
    d.ell(-44, -574, 12, 7, "#e08080", op=0.28)
    d.ell(50, -572, 12, 7, "#e08080", op=0.28)
    # locket circle — she has her own mark, not the triangle
    d.circ(6, -470, 8, BRASS, sw=1.8)
    d.circ(6, -470, 3.5, "#f4efe4", sw=1)

    # ---------- baby, cheek to cheek on her left side ----------
    # body
    d.ell(132, -360, 58, 50, BABY_C, sw=3.2)
    d.spec(112, -386, 18, 10, 0.4)
    d.shade(132, -332, 36, 14, 0.08)
    # onesie band
    d.ell(132, -348, 40, 16, "#f7f4ee", sw=2.2)
    d.text_free_badge(132, -348, s=7, fill=BRASS, rot=0, sw=1.5)
    # navel bolt
    d.circ(132, -372, 3.2, BABY_D, sw=1.2)
    # mismatched booties dangling — one parent each
    d.g('transform="translate(108,-300) rotate(16)"')
    d.ell(0, 0, 16, 11, DAD, sw=2.4)
    d.ell(-4, -3, 5, 3, DAD_L, op=0.6)
    d.ge()
    d.g('transform="translate(156,-296) rotate(-10)"')
    d.ell(0, 0, 16, 11, MOM_D, sw=2.4)
    d.ell(-4, -3, 5, 3, MOM_L, op=0.6)
    d.ge()
    # little legs
    d.bone(120, -340, 108, -304, 16, BABY_C, sw=2.4)
    d.bone(148, -338, 156, -302, 16, BABY_C, sw=2.4)

    # head, overlapping mom's cheek
    d.ell(118, -470, 52, 48, BABY_C, sw=3.2)
    d.ell(118, -472, 42, 38, BABY_FACE, sw=2.4)
    d.spec(100, -496, 14, 8, 0.45)
    # single curl antenna
    d.path("M118 -516 C 118 -540, 142 -538, 140 -520 C 138 -508, 150 -512, 152 -500", sw=4, stroke=BABY_D)
    d.circ(154, -498, 4, BABY_D, sw=1.4)
    # ears nubs
    d.ell(70, -470, 8, 11, BABY_C, sw=2)
    d.ell(166, -466, 8, 11, BABY_C, sw=2)
    # enormous eyes looking UP at the softbox, not at the lens
    eye(d, 100, -482, 15, 16, 5, -9, "#67b8c4", BABY_FACE, lid=0.0)
    eye(d, 136, -480, 15, 16, 6, -9, "#67b8c4", BABY_FACE, lid=0.0)
    button_nose(d, 118, -458, r=5, fill="#f0b0a4")
    # wonder mouth
    d.ell(118, -440, 7, 8, "#2a3338", sw=2)
    d.ell(116, -442, 2.4, 2, "#ffffff", op=0.35)
    # blush
    d.ell(86, -458, 8, 5, "#f0b0b0", op=0.45)
    d.ell(150, -456, 8, 5, "#f0b0b0", op=0.4)

    # fist in mom's cheek, covering the corner of her smile
    hand(d, 62, -530, 168, BABY_C, [9, 10, 8], spread=8, thick=7, palm=11, thumb_spread=50, sw=2)
    # other arm up, proudly holding the stolen pearl
    d.bone(150, -456, 168, -512, 18, BABY_C, sw=2.6)
    d.joint(164, -494, 8, BABY_D, bolt="#f4efe4")
    hand(d, 172, -528, -78, BABY_C, [8, 9, 7], spread=8, thick=7, palm=11, thumb_spread=-48, sw=2.2)
    d.circ(178, -548, 7.4, "#f7f3ea", sw=1.8)
    d.spec(175, -551, 2.4, 1.6, 0.85)

    # mom's supporting hand under the baby's seat
    hand(d, 150, -300, -70, MOM, [16, 18, 16, 14], spread=6, thick=7.5, palm=13, thumb_spread=-40)

    d.ge()


def dad_arm(d):
    """Chicken-wing arm hooked over mom's near shoulder. He committed late."""
    d.g(f'transform="translate({DAD_X},{FLOOR}) rotate({DAD_R})"')
    # shoulder already drawn; this arm leaves it
    d.bone(122, -492, 168, -560, 34, DAD)
    d.bone(168, -560, 214, -478, 30, DAD_D)
    d.joint(168, -560, 15, DAD_L)
    d.joint(214, -478, 12, DAD_L)
    # splayed clamp-ish hand, one finger higher than the others, sitting on her neck
    hand(
        d, 228, -468, 20, DAD,
        [22, 26, 18, 14], spread=16, thick=8.5, palm=15, thumb_spread=-70,
    )
    d.ge()


def teen(d):
    """Showed up. Hood up. Arms full of their own arms. Eyes on the dog."""
    d.g(f'transform="translate({TEEN_X},{FLOOR}) rotate({TEEN_R})"')

    # image-left shoe turned toward the door. The lace is a loose cable.
    d.path(
        "M-36 -6 L-36 -24 Q-44 -38 -78 -34 L-118 -26 Q-128 -16 -112 -6 Z",
        fill="#1a1c20", sw=3,
    )
    d.path("M-70 -30 L-96 -18", sw=2.2, stroke=TEEN_L)
    d.path("M-88 -8 C -96 8, -78 14, -70 6", sw=2.4, stroke=MAG)
    d.rect(10, -32, 58, 26, 8, "#1a1c20", sw=3)
    d.rect(14, -28, 46, 8, 3, TEEN_L, sw=0)
    d.rect(18, -12, 42, 6, 2, SOLE, sw=0)

    # long thin legs, weight on the exit-side hip
    d.bone(-40, -250, -72, -30, 28, TEEN)
    d.bone(36, -246, 40, -38, 28, TEEN_M)
    d.joint(-46, -140, 11, TEEN_L, bolt=MAG_D)
    d.joint(38, -138, 11, TEEN_L, bolt=MAG_D)

    # narrow hips
    d.rect(-58, -300, 112, 60, 18, TEEN, sw=3.2)
    d.rect(-60, -286, 116, 16, 6, "#1a1c20", sw=2.2)
    d.rect(-8, -290, 18, 14, 3, MAG_D, sw=1.4)

    # torso, sunk
    d.rect(-70, -470, 136, 180, 26, TEEN, sw=3.3)
    d.spec(-30, -440, 28, 14, 0.12)
    # hoodie pocket
    d.path("M-40 -360 Q 0 -340 40 -362 L 36 -320 Q 0 -308 -36 -322 Z", fill=TEEN_M, sw=2.4)
    # family triangle almost covered by a magenta sticker, one corner sticking out
    d.text_free_badge(-2, -400, s=11, fill="#8d939c", rot=6, sw=1.6)
    d.circ(2, -396, 12, MAG, sw=2)
    d.circ(2, -396, 5, MAG_D, sw=0)

    # cowl / hood mass over the shoulders
    d.path(
        "M-88 -450 C -120 -520 -90 -640 0 -668 C 96 -644 116 -520 84 -450 C 70 -500 40 -520 0 -524 C -44 -520 -70 -490 -88 -450 Z",
        fill=TEEN_M, sw=3.2,
    )
    # shoulders inside the cowl
    d.circ(-78, -450, 26, TEEN, sw=3)
    d.circ(76, -444, 26, TEEN, sw=3)

    # crossed arms, high and tight
    d.bone(-78, -450, -108, -360, 26, TEEN)
    d.bone(76, -444, 104, -352, 26, TEEN_M)
    # forearms across the chest
    d.bone(-108, -360, 86, -392, 24, TEEN_L)
    d.bone(104, -352, -80, -378, 24, TEEN)
    d.joint(-108, -360, 11, TEEN_L, bolt=MAG_D)
    d.joint(104, -352, 11, TEEN_L, bolt=MAG_D)
    # fingertips visible on the opposite sleeves
    for fx, fy, rot in ((-70, -372, 20), (-58, -368, 8), (64, -386, -10), (76, -382, 6)):
        d.g(f'transform="translate({fx},{fy}) rotate({rot})"')
        d.rect(-3, -10, 7, 16, 3, TEEN_FACE, sw=1.6)
        d.ge()

    # neckless: head sits in the hood
    d.g('transform="rotate(10 0 -560)"')  # cocked back toward the family, contradicting the lean
    # hood behind / around head
    d.ell(0, -575, 78, 86, TEEN_M, sw=3.2)
    d.path(
        "M-70 -600 C -88 -500 -60 -470 0 -468 C 64 -470 90 -508 72 -608",
        fill=TEEN, sw=2.6,
    )
    # face plate — pale, still the family color, framed by the hood
    d.ell(2, -572, 52, 58, TEEN_FACE, sw=2.6)
    # flat jaw plate inherited from dad, under mom's round cranium
    d.path("M-40 -540 L40 -536 L34 -522 Q 0 -512 -36 -524 Z", fill="#d9d3c8", sw=2.2)
    # drawstrings, uneven
    d.line(-18, -500, -26, -430, MAG, 2.6)
    d.circ(-26, -426, 3.5, MAG, sw=1.2)
    d.line(16, -498, 22, -454, "#cfc6ba", 2.4)
    d.circ(22, -450, 3.2, "#cfc6ba", sw=1.2)

    # half-lidded emissive eyes. pupils dropped toward the dog (down, image right).
    eye(d, -20, -586, 14, 13, 6, 6, MAG, TEEN_FACE, lid=0.42, ring="#2a2c31")
    eye(d, 24, -584, 14, 13, 7, 6, MAG, TEEN_FACE, lid=0.34, ring="#2a2c31")
    # faint glow
    d.ell(-20, -584, 18, 10, MAG, op=0.10)
    d.ell(24, -582, 18, 10, MAG, op=0.10)
    # thin brows: one bored flat, one a fraction up (the dog is, unfortunately, funny)
    brow(d, -22, -612, 24, 4, "#3a342e", thick=4.5)
    brow(d, 26, -616, 24, -12, "#3a342e", thick=4.5)
    # dad's vent, small, on a rounder face
    vent_nose(d, 2, -558, s=0.72, color="#8a8178")
    # status-bar mouth, not a smile
    d.g('transform="rotate(3 4 -534)"')
    d.rect(-14, -538, 32, 6, 3, "#8d8680", sw=1.5)
    d.ge()
    # embarrassed, would deny it
    d.ell(-36, -552, 9, 5, "#e7a0a8", op=0.28)
    d.ell(40, -550, 9, 5, "#e7a0a8", op=0.22)
    d.ge()

    # headphones, taken off the ears and not put away. one cup lower.
    d.path("M-64 -640 Q 0 -700 66 -632", sw=8, stroke="#1a1c20")
    d.path("M-64 -640 Q 0 -700 66 -632", sw=3, stroke=TEEN_L, op=0.5)
    d.rect(-86, -624, 24, 34, 8, "#1a1c20", sw=2.4)
    d.rect(-82, -620, 16, 22, 5, MAG_D, sw=1.4)
    d.rect(64, -600, 24, 34, 8, "#1a1c20", sw=2.4)  # this one slipped
    d.rect(68, -596, 16, 22, 5, "#2a2c31", sw=1.4)
    # cable from the low cup, down across the hip, dies on the floor
    # (the dog will sit on the middle of it)
    d.path(
        "M76 -566 C 90 -520, 70 -480, 48 -450 C 20 -410, -10 -420, -20 -360 "
        "C -30 -300, 10 -260, 30 -200 C 50 -140, 20 -80, 70 -20 C 110 28, 180 36, 250 18",
        sw=3.4, stroke="#2a2c31",
    )
    # plug, short of everyone
    d.g('transform="translate(258,16) rotate(18)"')
    d.rect(-8, -6, 20, 12, 2, "#3a3e46", sw=1.6)
    d.rect(10, -3, 8, 3, 1, BRASS, sw=1)
    d.rect(10, 2, 8, 3, 1, BRASS, sw=1)
    d.ge()

    d.ge()


def kid(d):
    """Built from spare parts. Having a wonderful time. Foot on dad. Ears on dad."""
    d.g(f'transform="translate({KID_X},{KID_Y}) rotate({KID_R})"')

    # near foot, planted wide, closer to the lens
    d.ell(46, -4, 28, 12, "#1c2126", op=0.2)
    d.rect(16, -30, 52, 26, 9, KID_D, sw=3)
    d.rect(20, -26, 42, 9, 4, KID_L, sw=0)
    d.rect(24, -12, 36, 7, 2, SOLE, sw=0)
    # far foot planted on dad's right shoe
    d.g('transform="translate(-46,-128) rotate(-6)"')
    d.rect(-16, -16, 50, 22, 8, KID_D, sw=3)
    d.rect(-12, -12, 38, 8, 3, KID_L, sw=0)
    d.rect(-8, -2, 32, 6, 2, SOLE, sw=0)
    d.ge()

    # legs: near one straight, far one bent up onto the shoe
    d.bone(40, -150, 44, -36, 28, KID)
    d.bone(-4, -150, -28, -124, 26, KID_D)
    d.joint(42, -92, 11, KID_D, bolt=BRASS_D)
    d.joint(-46, -78, 11, KID_D, bolt=BRASS_D)
    # scuffed knees
    d.ell(40, -100, 8, 5, "#b8882a", op=0.7)
    d.ell(-40, -86, 7, 4, "#b8882a", op=0.65)

    # hips
    d.rect(-58, -196, 112, 56, 16, OVR, sw=3.2)
    d.shade(0, -160, 40, 12, 0.08)

    # overalls torso
    d.rect(-64, -330, 124, 150, 22, OVR, sw=3.2)
    d.spec(-24, -300, 24, 12, 0.18)
    # yellow chest showing where the strap gave up
    d.path("M-20 -330 L40 -326 L36 -250 L-16 -254 Z", fill=KID, sw=2.4)
    # bib
    d.path("M-48 -300 L-10 -308 L-6 -230 L-44 -226 Z", fill=OVR_D, sw=2.2)
    # one strap on (image left, over the blue inherited arm)
    d.rect(-52, -360, 16, 70, 5, OVR_D, sw=2)
    d.circ(-44, -300, 5, BRASS, sw=1.6)
    # the other strap hanging down the copper side
    d.path("M46 -250 C 58 -250, 64 -220, 52 -200", sw=10, stroke=OVR_D)
    d.path("M46 -250 C 58 -250, 64 -220, 52 -200", sw=4, stroke=OVR_L, op=0.5)
    d.circ(50, -196, 5, BRASS, sw=1.5)
    # pocket
    d.rect(-16, -250, 30, 22, 4, OVR_D, sw=1.8)
    # family triangle stuck on upside down
    d.text_free_badge(36, -280, s=9, fill=KID_L, rot=180, sw=1.6)

    # neck
    d.rect(-16, -358, 32, 32, 8, KID, sw=2.6)

    # shoulders
    d.circ(-70, -320, 20, KID, sw=2.8)
    d.circ(66, -316, 20, KID, sw=2.8)

    # image-right arm: mom's spare copper, akimbo, showing off
    d.bone(66, -316, 108, -250, 22, MOM_D, sw=2.8)
    d.bone(108, -250, 96, -190, 20, MOM, sw=2.8)
    d.joint(108, -250, 10, MOM_L, bolt=BRASS)
    hand(d, 86, -172, 100, MOM, [12, 14, 12, 10], spread=7, thick=6.5, palm=11, thumb_spread=-56, sw=2)

    # head
    d.circ(0, -430, 62, KID, sw=3.3)
    d.circ(0, -432, 50, KID_FACE, sw=2.6)
    d.spec(-18, -466, 18, 10, 0.35)
    # ears: round like mom, bolted like dad
    d.ell(-64, -430, 12, 16, KID, sw=2.4)
    d.ell(64, -426, 12, 16, KID, sw=2.4)
    rivet(d, -64, -430, 3.2, BRASS_D)
    rivet(d, 64, -426, 3.2, BRASS_D)
    # dad's jaw bolt under a toy face
    d.rect(-18, -384, 36, 12, 4, DAD, sw=2)

    # propeller cap, askew, one blade chipped
    d.g('transform="translate(-6,-492) rotate(-14)"')
    d.ell(0, 8, 46, 14, OVR, sw=2.6)
    d.ell(0, 4, 40, 9, OVR_L, op=0.35)
    d.rect(-16, -8, 32, 16, 4, OVR_D, sw=2)
    d.circ(0, -8, 6, BRASS, sw=1.6)
    for ang, length, col in ((-70, 28, KID_D), (50, 34, KID), (170, 18, "#c48a16")):
        d.g(f'transform="rotate({ang} 0 -8)"')
        d.ell(0, -8 - length * 0.5, 7, length * 0.5, col, sw=2)
        d.ge()
    d.ge()

    # open eye (image right) locked on the camera; the other winks
    eye(d, 20, -446, 15, 16, 0, -1, "#3d8f9a", KID_FACE, lid=0.04)
    # wink
    d.path("M-36 -440 Q -18 -454 -2 -440", sw=4, stroke=INK)
    d.line(-32, -446, -36, -454, INK, 2)
    d.line(-20, -452, -20, -462, INK, 2)
    d.line(-8, -446, -4, -454, INK, 2)
    # brow only over the open eye, high
    brow(d, 22, -478, 26, -16, KID_D, thick=6)
    # bandage on the wink cheek
    d.g('transform="rotate(-18 -36 -424)"')
    d.rect(-50, -432, 22, 12, 3, "#f4efe4", sw=1.6)
    d.line(-46, -426, -32, -426, "#e7b2b2", 1.5)
    d.ge()
    # dad's vent nose on mom's round face
    vent_nose(d, 2, -418, s=0.85)
    # open mouth, missing a tooth, tongue out
    d.ell(2, -388, 16, 13, "#2a2428", sw=2.4)
    d.rect(-10, -398, 7, 8, 1.5, "#fff8ea", sw=1)
    d.rect(4, -398, 7, 8, 1.5, "#fff8ea", sw=1)
    # gap where a tooth isn't, between them
    d.ell(2, -376, 8, 6, TONGUE, sw=1.6)
    d.line(2, -380, 2, -372, "#d06070", 1.2)
    # blush
    d.ell(-28, -412, 9, 5, "#f0a0a0", op=0.4)
    d.ell(34, -414, 9, 5, "#f0a0a0", op=0.35)

    d.ge()

    # Spare blue arm, telescoped, sneaking up the gap beside dad.
    # Two fingers clear the crown; the ears are off-center anyway.
    d.g(f'transform="translate({KID_X},{KID_Y}) rotate({KID_R})"')
    d.bone(-70, -320, -150, -460, 22, DAD, sw=2.8)
    d.bone(-150, -460, -148, -640, 15, DAD_D, sw=2.4)
    d.bone(-148, -640, -96, -790, 13, DAD, sw=2.4)
    for (x, y) in ((-140, -520), (-148, -600), (-124, -720)):
        d.circ(x, y, 8, DAD_D, sw=2)
        d.circ(x, y, 3.1, BRASS_D, sw=1)
    d.joint(-150, -460, 10, DAD_L, bolt=BRASS)
    d.joint(-148, -640, 8, DAD_L, bolt=BRASS)
    hand(
        d, -78, -808, -92,
        DAD,
        [9, 46, 44, 8],
        spread=7, thick=7.5, palm=12, thumb_spread=70, sw=2.2,
    )
    d.ge()


def dog(d):
    """Consumer pet-bot. Collar is dad's taste. Face is the teen's."""
    d.g(f'transform="translate({DOG_X},{DOG_Y})"')

    # splayed hind leg — the sit went wrong
    d.bone(48, -40, 92, -8, 18, DOG_D, sw=2.6)
    d.ell(100, -4, 14, 9, DOG, sw=2.2)
    # haunch
    d.ell(36, -62, 52, 40, DOG, sw=3.2)
    d.shade(40, -42, 36, 14, 0.08)
    d.spec(16, -84, 16, 8, 0.35)
    # rust spot
    d.ell(58, -78, 14, 10, DOG_SPOT, sw=2)
    # chest
    d.ell(-8, -58, 40, 34, DOG, sw=3)
    # front legs, straight, trying to be good
    d.bone(-24, -50, -30, -8, 16, DOG, sw=2.6)
    d.bone(8, -50, 14, -8, 16, DOG, sw=2.6)
    d.ell(-32, -4, 12, 8, DOG, sw=2.2)
    d.ell(16, -4, 12, 8, DOG, sw=2.2)
    # toes
    for tx in (-40, -30, -22, 6, 16, 26):
        d.circ(tx, 2, 2.4, DOG_D, sw=0)

    # tail, a spring, mid-wag so it is blurred into two ghosts
    d.path(
        "M78 -84 C 112 -100, 118 -60, 100 -52 C 84 -44, 96 -78, 118 -70",
        sw=7, stroke="#c5beb2", op=0.35,
    )
    d.path(
        "M78 -84 C 108 -96, 114 -64, 98 -56 C 86 -50, 98 -76, 114 -72",
        sw=6, stroke=DOG_D,
    )

    # neck + collar (burgundy, same dye lot as the tie)
    d.bone(-6, -86, -16, -112, 22, DOG, sw=2.6)
    d.ell(-16, -108, 20, 10, TIE, sw=2.4)
    d.circ(-8, -100, 7, BRASS, sw=1.8)
    d.spec(-10, -102, 2.5, 1.6, 0.7)
    d.ell(-4, -92, 5, 6, BRASS_L, sw=1.4)  # tag, blank

    # head turned toward the teen: muzzle to image left, both eyes still visible
    d.g('transform="translate(-24,-150) rotate(-18)"')
    d.ell(10, 10, 40, 34, DOG, sw=3.2)
    d.ell(-18, 16, 22, 16, DOG, sw=2.6)  # muzzle
    d.spec(-4, -8, 12, 7, 0.4)
    # nose
    d.ell(-36, 14, 8, 6, "#2a2428", sw=1.8)
    d.spec(-38, 12, 2.4, 1.4, 0.5)
    # floppy ear, outside color, rust tip
    d.g('transform="translate(28,8) rotate(18)"')
    d.ell(0, 26, 14, 28, DOG_D, sw=2.4)
    d.ell(0, 10, 12, 16, DOG, sw=2)
    d.ell(4, 36, 8, 10, DOG_SPOT, sw=1.6)
    d.ge()
    # inside-out ear (the near one, toward the teen) — pink copper showing
    d.g('transform="translate(-8,-8) rotate(-30)"')
    d.ell(0, 8, 13, 24, "#e7a090", sw=2.4)
    d.ell(0, 4, 7, 12, "#f3c4b8", op=0.7)
    d.line(0, -8, 0, 24, "#c47868", 1.4, op=0.6)
    d.ge()
    # eyes up toward the teen. the near eye carries a hotter catchlight.
    eye(d, -6, -2, 11, 12, -3, -4, "#6a5348", DOG, lid=0.05, ring="#cfc6ba")
    eye(d, 22, 0, 10, 11, -4, -4, "#6a5348", DOG, lid=0.08, ring="#cfc6ba")
    # bigger flash hit on the eye that faces the softbox more
    d.ell(26, -4, 4.5, 3.5, "#ffffff", op=0.85)
    # open pant, tongue
    d.path("M-30 22 Q -16 34 -4 22", sw=2.4, stroke=INK, fill="#3a3330")
    d.ell(-16, 34, 7, 10, TONGUE, sw=1.8)
    d.line(-16, 30, -16, 40, "#d06070", 1.2)
    d.ge()

    d.ge()


def grade(d):
    # strobe wash from the softbox side, then a print vignette
    d.rect(0, 0, W, H, 0, "url(#softbox)")
    d.rect(0, 0, W, H, 0, "url(#vig)")


def defs():
    return f'''<defs>
  <filter id="blur18" x="-40%" y="-80%" width="180%" height="260%">
    <feGaussianBlur stdDeviation="16"/>
  </filter>
  <filter id="blur12" x="-40%" y="-80%" width="180%" height="260%">
    <feGaussianBlur stdDeviation="10"/>
  </filter>
  <filter id="blur4" x="-40%" y="-80%" width="180%" height="260%">
    <feGaussianBlur stdDeviation="3.5"/>
  </filter>
  <radialGradient id="vig" cx="48%" cy="42%" r="68%">
    <stop offset="58%" stop-color="#1a2428" stop-opacity="0"/>
    <stop offset="100%" stop-color="#1a2428" stop-opacity="0.38"/>
  </radialGradient>
  <radialGradient id="softbox" cx="90%" cy="16%" r="62%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.16"/>
    <stop offset="45%" stop-color="#ffffff" stop-opacity="0.04"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
</defs>'''


def build():
    d = D()
    d.add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" stroke-linejoin="round" stroke-linecap="round">'
    )
    d.add(defs())
    studio(d)
    shadows(d)
    dad_body(d)
    grandpa(d)
    mom_and_baby(d)
    dad_arm(d)
    teen(d)
    kid(d)
    dog(d)
    grade(d)
    d.add("</svg>")
    return "\n".join(d.o) + "\n"


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "output", "awkward-robot-family.svg")
    svg = build()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    preview = os.path.join(root, "build", "preview.html")
    os.makedirs(os.path.dirname(preview), exist_ok=True)
    with open(preview, "w", encoding="utf-8") as f:
        f.write(
            "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
            "html,body{margin:0;padding:0;background:#222;}svg{display:block;}"
            "</style></head><body>\n"
            + svg
            + "\n</body></html>"
        )
    print(out)
    print(f"svg_bytes={len(svg.encode('utf-8'))}")


if __name__ == "__main__":
    main()
