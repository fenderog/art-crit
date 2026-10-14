"""Awkward robot family portrait.

Scene is described once and emitted as SVG (vector master) and PNG (raster).
No text anywhere: everything is geometry.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Canvas, solid, linear, radial  # noqa: E402

W, H = 1200, 900
FLOOR_Y = 706

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

cv = Canvas(W, H)


def grad(c1, c2, p0, p1):
    return linear([(0.0, c1), (1.0, c2)], p0, p1)


def rr(x, y, w, h, rx=0, fill=None, stroke=None, sw=2, rot=None):
    cv.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx, rot=rot)


def limb(x0, y0, x1, y1, w, fill):
    cv.line(x0, y0, x1, y1, stroke=fill, sw=w)


def glow(cx, cy, r, rgb, a=0.45, a0=0.0):
    cv.circle(cx, cy, r, fill=radial([(0.0, rgb, a), (0.55, rgb, a * 0.45), (1.0, rgb, a0)], (cx, cy), r))


def soft_shadow(cx, cy, rx, ry, a=0.34):
    cv.ellipse(cx, cy, rx, ry, fill=radial([(0.0, (12, 8, 16), a), (0.6, (12, 8, 16), a * 0.5), (1.0, (12, 8, 16), 0.0)],
                                           (cx, cy), max(rx, ry)))


# =========================================================== backdrop

cv.rect(0, 0, W, FLOOR_Y + 4, fill=grad((34, 44, 66), (62, 78, 100), (0, 0), (0, FLOOR_Y)))
cv.rect(0, 0, W, FLOOR_Y, fill=radial([(0.0, (126, 145, 172), 0.55), (0.55, (96, 116, 148), 0.22), (1.0, (60, 74, 100), 0.0)],
                                      (596, 330), 720))

# draped curtain, left
curtain_stops = [(0.0, (22, 30, 50), 1.0), (0.5, (48, 62, 92), 1.0), (1.0, (26, 35, 56), 1.0)]
folds = [(-30, 62), (26, 58), (78, 52), (124, 46), (164, 40)]
for i, (x0, wd) in enumerate(folds):
    wob = 10 + 6 * math.sin(i * 1.7)
    cv.path([('M', x0, -20),
             ('C', x0 + 10, 180, x0 - 12, 420, x0 + 6, 620),
             ('C', x0 + 12, 668, x0 - 6, 700, x0 + 2, 726),
             ('L', x0 + wd + 2, 726),
             ('C', x0 + wd - 6, 690, x0 + wd + 12, 660, x0 + wd - 4, 618),
             ('C', x0 + wd - 14, 420, x0 + wd + 10, 180, x0 + wd - 2, -20),
             ('Z',)],
            fill=linear(curtain_stops, (x0, 0), (x0 + wd, 0)))
cv.path([('M', -30, 726), ('C', 60, 712, 120, 736, 214, 720), ('L', 214, 742), ('C', 120, 756, 60, 734, -30, 748), ('Z',)],
        fill=solid((18, 25, 42)))

# floor
cv.rect(0, FLOOR_Y - 4, W, H - FLOOR_Y + 4, fill=grad((74, 66, 78), (32, 27, 36), (0, FLOOR_Y), (0, H)))
cv.rect(0, FLOOR_Y - 6, W, 10, fill=linear([(0.0, (150, 138, 148), 0.35), (1.0, (150, 138, 148), 0.0)], (0, FLOOR_Y - 6), (0, FLOOR_Y + 4)))
cv.ellipse(600, 812, 640, 150, fill=radial([(0.0, (168, 148, 152), 0.30), (0.6, (140, 122, 130), 0.12), (1.0, (120, 104, 116), 0.0)],
                                           (600, 812), 640))

# wall props: two slightly crooked frames
rr(196, 108, 178, 128, 4, fill=grad((44, 56, 78), (30, 39, 58), (196, 108), (374, 236)), stroke=solid((146, 124, 88)), sw=11, rot=(-4, 285, 172))
rr(212, 124, 146, 96, 2, fill=radial([(0.0, (108, 132, 158), 0.55), (1.0, (52, 66, 92), 0.15)], (285, 172), 90), rot=(-4, 285, 172))
rr(872, 122, 128, 96, 4, fill=grad((48, 58, 80), (32, 41, 60), (872, 122), (1000, 218)), stroke=solid((132, 112, 82)), sw=9, rot=(3.5, 936, 170))

# wall speckle texture
rnd = random.Random(7)
for _ in range(260):
    x = rnd.uniform(0, W)
    y = rnd.uniform(0, FLOOR_Y - 10)
    r = rnd.uniform(1.2, 3.4)
    a = rnd.uniform(0.03, 0.10)
    cv.circle(x, y, r, fill=solid((214, 222, 238), a))


# =========================================================== helpers

def metal(x, y, w, h, rx, light, dark, rot=None, rim=True):
    """Rounded metal plate with a light from the upper left."""
    rr(x, y, w, h, rx, fill=grad(light, dark, (x, y), (x + w * 0.75, y + h)), rot=rot)
    if rim:
        rr(x + 3, y + 3, w - 6, max(2, h * 0.10), max(2, rx * 0.6),
           fill=solid((255, 255, 255), 0.16), rot=rot)


def antenna(x0, y0, x1, y1, ball_r, rod, ball, bend=None):
    if bend:
        cv.path([('M', x0, y0), ('C', bend[0], bend[1], bend[2], bend[3], x1, y1)], stroke=rod, sw=9)
    else:
        limb(x0, y0, x1, y1, 9, rod)
    glow(x1, y1, ball_r * 2.6, (255, 210, 140), 0.30)
    cv.circle(x1, y1, ball_r, fill=grad((255, 236, 190), (226, 156, 84), (x1 - ball_r, y1 - ball_r), (x1 + ball_r, y1 + ball_r)), stroke=ball, sw=2)


def bolt(cx, cy, r, c1, c2, rot=0.0):
    pts = []
    for i in range(6):
        a = math.radians(rot + 60 * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    cv.polygon(pts, fill=grad(c1, c2, (cx - r, cy - r), (cx + r, cy + r)))


# =========================================================== grandma's chair (drawn behind grandma)

CHAIR_X, CHAIR_Y = 946, 640
rr(CHAIR_X, CHAIR_Y, 176, 26, 10, fill=grad((104, 76, 58), (66, 46, 34), (CHAIR_X, CHAIR_Y), (CHAIR_X, CHAIR_Y + 26)))
rr(CHAIR_X + 8, CHAIR_Y + 22, 16, 132, 6, fill=solid((58, 41, 31)))
rr(CHAIR_X + 150, CHAIR_Y + 22, 16, 132, 6, fill=solid((58, 41, 31)))
rr(CHAIR_X + 148, CHAIR_Y - 176, 18, 200, 8, fill=grad((112, 82, 62), (64, 46, 34), (CHAIR_X + 148, CHAIR_Y - 176), (CHAIR_X + 166, CHAIR_Y)))
rr(CHAIR_X + 62, CHAIR_Y - 168, 104, 18, 8, fill=grad((112, 82, 62), (72, 52, 38), (CHAIR_X + 62, CHAIR_Y - 168), (CHAIR_X + 166, CHAIR_Y - 150)))


# =========================================================== grandpa (back right, standing)

GX = 1116
soft_shadow(GX + 8, 792, 108, 30, 0.32)

# legs
rr(GX - 44, 612, 40, 186, 14, fill=grad((122, 82, 52), (72, 46, 28), (GX - 44, 612), (GX - 4, 798)))
rr(GX + 6, 608, 40, 190, 14, fill=grad((122, 82, 52), (72, 46, 28), (GX + 6, 608), (GX + 46, 798)))
rr(GX - 56, 776, 66, 28, 12, fill=solid((58, 38, 26)))
rr(GX - 4, 778, 68, 28, 12, fill=solid((58, 38, 26)))

# torso
rr(GX - 62, 372, 132, 258, 20, fill=grad((176, 118, 72), (94, 58, 33), (GX - 62, 372), (GX + 70, 630)))
rr(GX - 56, 378, 120, 22, 10, fill=solid((255, 255, 255), 0.12))
for bx, by in [(GX - 50, 392), (GX + 54, 392), (GX - 50, 606), (GX + 54, 606), (GX - 50, 500), (GX + 54, 500)]:
    cv.circle(bx, by, 6, fill=solid((214, 152, 92)))
    cv.circle(bx - 1.5, by - 1.5, 2.4, fill=solid((255, 216, 168), 0.8))
# chest gauge
cv.circle(GX + 4, 462, 34, fill=grad((238, 218, 178), (186, 156, 112), (GX - 26, 432), (GX + 34, 492)), stroke=solid((78, 48, 28)), sw=5)
cv.circle(GX + 4, 462, 25, fill=solid((212, 190, 152)))
for i in range(9):
    a = math.radians(-190 + i * 25)
    limb(GX + 4 + 19 * math.cos(a), 462 + 19 * math.sin(a), GX + 4 + 24 * math.cos(a), 462 + 24 * math.sin(a), 3, solid((96, 62, 36)))
limb(GX + 4, 462, GX + 22, 442, 5, solid((178, 66, 44)))
cv.circle(GX + 4, 462, 5, fill=solid((84, 52, 32)))
# shoulder pads
rr(GX - 74, 382, 52, 44, 18, fill=grad((150, 100, 62), (92, 58, 34), (GX - 74, 382), (GX - 22, 426)))
rr(GX + 34, 380, 52, 44, 18, fill=grad((150, 100, 62), (92, 58, 34), (GX + 34, 380), (GX + 86, 424)))

# head
rr(GX - 50, 276, 116, 98, 22, fill=grad((196, 136, 86), (112, 70, 40), (GX - 50, 276), (GX + 66, 374)))
rr(GX - 44, 282, 104, 20, 9, fill=solid((255, 255, 255), 0.14))
rr(GX - 46, 356, 108, 16, 8, fill=solid((92, 58, 34)))
# eyes + monocle
cv.circle(GX - 20, 318, 13, fill=solid((46, 30, 22)))
cv.circle(GX - 20, 318, 6, fill=solid((255, 214, 150)))
cv.circle(GX - 23, 314, 2.6, fill=solid((255, 246, 226)))
cv.circle(GX + 28, 318, 12, fill=solid((46, 30, 22)))
cv.circle(GX + 28, 318, 5.5, fill=solid((255, 214, 150)))
cv.circle(GX + 28, 318, 22, fill=solid((255, 232, 178), 0.16), stroke=solid((244, 214, 150)), sw=5)
cv.path([('M', GX + 22, 340), ('C', GX + 30, 358, GX + 26, 372, GX + 40, 386)], stroke=solid((226, 194, 132)), sw=3)
# whisker moustache
for s in (-1, 1):
    cv.path([('M', GX + 2 + s * 6, 346), ('C', GX + 2 + s * 16, 340, GX + 2 + s * 26, 344, GX + 2 + s * 32, 352)],
            stroke=solid((226, 206, 172)), sw=7)
antenna(GX + 12, 276, GX + 30, 232, 8, solid((140, 92, 54)), solid((96, 62, 34)))

# grandpa's arm resting on the chair back
limb(GX - 66, 412, GX - 118, 462, 30, grad((150, 100, 62), (94, 60, 36), (GX - 118, 412), (GX - 66, 462)))
rr(GX - 142, 452, 44, 30, 13, fill=grad((176, 118, 72), (110, 70, 42), (GX - 142, 452), (GX - 98, 482)))
# other arm
limb(GX + 72, 414, GX + 86, 552, 28, grad((150, 100, 62), (94, 60, 36), (GX + 60, 414), (GX + 100, 552)))
rr(GX + 70, 548, 38, 32, 13, fill=grad((176, 118, 72), (110, 70, 42), (GX + 70, 548), (GX + 108, 580)))


# =========================================================== grandma (seated, warm lamp head)

MX, MY = 1006, 500
soft_shadow(MX + 6, 782, 118, 28, 0.30)

# legs / lap
rr(MX - 58, 618, 44, 152, 16, fill=grad((122, 82, 106), (72, 46, 64), (MX - 58, 618), (MX - 14, 770)), rot=(6, MX - 36, 620))
rr(MX + 12, 616, 44, 154, 16, fill=grad((122, 82, 106), (72, 46, 64), (MX + 12, 616), (MX + 56, 770)), rot=(-4, MX + 34, 618))
rr(MX - 74, 754, 70, 28, 12, fill=solid((62, 40, 56)), rot=(4, MX - 40, 768))
rr(MX + 2, 758, 72, 28, 12, fill=solid((62, 40, 56)), rot=(-3, MX + 38, 772))

# torso
rr(MX - 74, 456, 152, 196, 42, fill=grad((170, 112, 136), (86, 52, 74), (MX - 74, 456), (MX + 78, 652)))
# shawl
cv.path([('M', MX - 78, 470), ('C', MX - 34, 508, MX + 30, 508, MX + 78, 468),
         ('L', MX + 86, 536), ('C', MX + 34, 570, MX - 34, 570, MX - 86, 534), ('Z',)],
        fill=grad((214, 150, 166), (150, 92, 112), (MX - 86, 462), (MX + 86, 570)))
for i in range(9):
    dx = -72 + i * 18
    cv.circle(MX + dx, 512 + 14 * math.cos(dx / 40.0), 5, fill=solid((236, 186, 196), 0.75))
# collar doily
for i in range(11):
    a = math.radians(200 + i * 14)
    cv.circle(MX + 62 * math.cos(a), 470 + 26 * math.sin(a), 9, fill=solid((238, 198, 206)))
# folded hands
rr(MX - 34, 600, 44, 34, 16, fill=grad((206, 168, 128), (150, 108, 76), (MX - 34, 600), (MX + 10, 634)), rot=(-8, MX - 12, 617))
rr(MX + 2, 604, 44, 32, 16, fill=grad((206, 168, 128), (150, 108, 76), (MX + 2, 604), (MX + 46, 636)), rot=(7, MX + 24, 620))

# neck + head
rr(MX - 20, 424, 40, 46, 12, fill=solid((120, 82, 60)))
rr(MX - 52, 330, 104, 104, 28, fill=grad((216, 166, 116), (128, 86, 52), (MX - 52, 330), (MX + 52, 434)))
rr(MX - 46, 336, 92, 18, 8, fill=solid((255, 255, 255), 0.16))
# happy eyes (closed arcs) + spectacles
for s in (-1, 1):
    cv.path([('M', MX + s * 22 - 13, 372), ('C', MX + s * 22 - 5, 358, MX + s * 22 + 5, 358, MX + s * 22 + 13, 372)],
            stroke=solid((72, 44, 30)), sw=6)
    cv.circle(MX + s * 22, 368, 19, fill=solid((255, 236, 196), 0.18), stroke=solid((248, 224, 168)), sw=4)
limb(MX - 6, 366, MX + 6, 366, 4, solid((248, 224, 168)))
cv.path([('M', MX - 16, 396), ('C', MX - 4, 408, MX + 8, 408, MX + 18, 396)], stroke=solid((96, 58, 38)), sw=5)
# lamp shade + glow
glow(MX + 2, 300, 190, (255, 206, 138), 0.34)
cv.polygon([(MX - 62, 332), (MX + 66, 332), (MX + 44, 276), (MX - 40, 276)],
           fill=grad((252, 204, 128), (206, 132, 70), (MX - 62, 276), (MX + 66, 332)))
rr(MX - 44, 264, 92, 18, 8, fill=grad((255, 226, 168), (218, 150, 88), (MX - 44, 264), (MX + 48, 282)))
glow(MX + 2, 288, 96, (255, 218, 158), 0.42)
# cane
limb(MX + 108, 782, MX + 128, 588, 11, grad((150, 104, 62), (92, 60, 34), (MX + 108, 588), (MX + 128, 782)))
cv.path([('M', MX + 128, 592), ('C', MX + 132, 566, MX + 156, 566, MX + 158, 588)], stroke=solid((126, 84, 48)), sw=11)


# =========================================================== dad (centre, tall and stiff)

DX = 548
soft_shadow(DX + 4, 802, 132, 32, 0.36)

# legs + feet
rr(DX - 52, 618, 48, 168, 14, fill=grad((104, 116, 136), (58, 66, 82), (DX - 52, 618), (DX - 4, 786)))
rr(DX + 8, 618, 48, 168, 14, fill=grad((104, 116, 136), (58, 66, 82), (DX + 8, 618), (DX + 56, 786)))
rr(DX - 68, 774, 80, 32, 13, fill=grad((70, 78, 94), (44, 50, 62), (DX - 68, 774), (DX + 12, 806)))
rr(DX - 4, 776, 82, 32, 13, fill=grad((70, 78, 94), (44, 50, 62), (DX - 4, 776), (DX + 78, 808)))

# torso
rr(DX - 92, 368, 190, 272, 28, fill=grad((148, 160, 180), (72, 82, 100), (DX - 92, 368), (DX + 98, 640)))
rr(DX - 84, 376, 174, 22, 11, fill=solid((255, 255, 255), 0.16))
# chest panel
rr(DX - 56, 424, 116, 116, 12, fill=grad((56, 66, 84), (34, 42, 56), (DX - 56, 424), (DX + 60, 540)))
for i, (c, a) in enumerate([((255, 196, 96), 1.0), ((226, 96, 74), 0.35), ((112, 214, 196), 0.9)]):
    cx = DX - 34 + i * 32
    glow(cx, 452, 17, c, 0.30 * a)
    cv.circle(cx, 452, 8, fill=solid(c, a))
rr(DX - 42, 486, 88, 12, 6, fill=solid((22, 28, 38)))
rr(DX - 42, 506, 52, 12, 6, fill=solid((22, 28, 38)))
cv.circle(DX + 32, 516, 12, fill=grad((196, 206, 220), (110, 122, 140), (DX + 20, 504), (DX + 44, 528)), stroke=solid((30, 36, 48)), sw=3)
# tie
cv.polygon([(DX - 22, 384), (DX + 22, 384), (DX + 14, 416), (DX - 14, 416)], fill=grad((212, 96, 70), (156, 62, 44), (DX - 22, 384), (DX + 22, 416)))
cv.polygon([(DX - 14, 418), (DX + 14, 418), (DX + 22, 500), (DX, 522), (DX - 22, 500)],
           fill=grad((214, 100, 72), (150, 60, 44), (DX - 22, 418), (DX + 22, 522)))
# shoulder yoke
rr(DX - 112, 372, 232, 52, 24, fill=grad((132, 145, 166), (78, 88, 108), (DX - 112, 372), (DX + 120, 424)))

# neck + head
rr(DX - 26, 322, 54, 56, 10, fill=grad((96, 106, 124), (58, 66, 82), (DX - 26, 322), (DX + 28, 378)))
rr(DX - 88, 178, 178, 152, 30, fill=grad((176, 188, 208), (86, 96, 116), (DX - 88, 178), (DX + 90, 330)))
rr(DX - 80, 186, 162, 22, 11, fill=solid((255, 255, 255), 0.18))
# face screen
rr(DX - 62, 214, 128, 96, 18, fill=grad((38, 48, 64), (22, 28, 40), (DX - 62, 214), (DX + 66, 310)))
# mismatched eyes
glow(DX - 24, 258, 40, (126, 226, 255), 0.36)
cv.circle(DX - 24, 258, 22, fill=grad((152, 232, 255), (42, 118, 158), (DX - 42, 240), (DX - 6, 278)))
cv.circle(DX - 24, 258, 10, fill=solid((16, 30, 42)))
cv.circle(DX - 31, 250, 6, fill=solid((240, 252, 255), 0.9))
rr(DX + 14, 240, 38, 34, 8, fill=grad((178, 226, 246), (72, 130, 162), (DX + 14, 240), (DX + 52, 274)))
rr(DX + 22, 250, 22, 14, 5, fill=solid((26, 44, 58)))
# mouth grille
rr(DX - 34, 292, 70, 12, 5, fill=solid((96, 118, 142), 0.9))
for i in range(5):
    rr(DX - 28 + i * 14, 294, 6, 8, 2, fill=solid((30, 40, 54)))
antenna(DX + 42, 180, DX + 74, 132, 11, solid((126, 138, 158)), solid((86, 96, 114)), bend=(DX + 52, 158, DX + 60, 142))

# left arm, hanging stiffly
limb(DX - 118, 420, DX - 128, 566, 42, grad((132, 145, 166), (74, 84, 102), (DX - 150, 420), (DX - 100, 566)))
rr(DX - 152, 552, 52, 46, 16, fill=grad((126, 138, 158), (70, 80, 98), (DX - 152, 552), (DX - 100, 598)))
rr(DX - 144, 588, 14, 18, 6, fill=solid((58, 66, 82)))
rr(DX - 124, 588, 14, 18, 6, fill=solid((58, 66, 82)))

# right arm: the stiff "hover" arm above mum's shoulder
limb(DX + 112, 412, DX + 196, 366, 42, grad((140, 152, 172), (78, 88, 108), (DX + 112, 366), (DX + 196, 412)))
limb(DX + 196, 366, DX + 250, 388, 36, grad((140, 152, 172), (78, 88, 108), (DX + 196, 366), (DX + 250, 400)))
rr(DX + 232, 372, 58, 36, 15, fill=grad((150, 162, 182), (86, 96, 116), (DX + 232, 372), (DX + 290, 408)), rot=(-10, DX + 261, 390))
rr(DX + 278, 376, 16, 26, 7, fill=grad((140, 152, 172), (86, 96, 116), (DX + 278, 376), (DX + 294, 402)), rot=(-18, DX + 286, 389))
rr(DX + 278, 358, 16, 22, 7, fill=grad((140, 152, 172), (86, 96, 116), (DX + 278, 358), (DX + 294, 380)), rot=(-24, DX + 286, 369))


# =========================================================== mum (centre right, poised)

UX = 772
soft_shadow(UX + 4, 792, 118, 30, 0.34)

# legs + feet
rr(UX - 42, 604, 38, 168, 14, fill=grad((150, 162, 178), (82, 92, 108), (UX - 42, 604), (UX - 4, 772)))
rr(UX + 6, 600, 38, 172, 14, fill=grad((150, 162, 178), (82, 92, 108), (UX + 6, 600), (UX + 44, 772)))
rr(UX - 58, 758, 68, 26, 12, fill=grad((104, 114, 130), (62, 70, 84), (UX - 58, 758), (UX + 10, 784)))
rr(UX - 2, 762, 70, 26, 12, fill=grad((104, 114, 130), (62, 70, 84), (UX - 2, 762), (UX + 68, 788)))

# torso: tapered
cv.path([('M', UX - 60, 392),
         ('C', UX - 72, 470, UX - 44, 520, UX - 50, 588),
         ('L', UX + 52, 588),
         ('C', UX + 46, 520, UX + 72, 470, UX + 60, 392),
         ('C', UX + 36, 366, UX - 36, 366, UX - 60, 392), ('Z',)],
        fill=grad((226, 234, 242), (116, 128, 144), (UX - 60, 380), (UX + 52, 588)))
cv.path([('M', UX - 46, 402), ('C', UX - 54, 462, UX - 30, 508, UX - 36, 574), ('L', UX - 18, 574),
         ('C', UX - 14, 508, UX - 34, 462, UX - 26, 402), ('Z',)], fill=solid((255, 255, 255), 0.22))
# brooch
glow(UX + 4, 448, 34, (255, 158, 122), 0.30)
cv.circle(UX + 4, 448, 17, fill=grad((255, 186, 150), (206, 92, 70), (UX - 10, 434), (UX + 18, 462)), stroke=solid((150, 70, 56)), sw=3)
cv.circle(UX - 2, 442, 5, fill=solid((255, 236, 224), 0.85))
rr(UX - 30, 512, 72, 10, 5, fill=solid((122, 134, 150), 0.55))

# neck + head
rr(UX - 22, 344, 44, 54, 12, fill=grad((150, 162, 178), (92, 102, 118), (UX - 22, 344), (UX + 22, 398)))
cv.path([('M', UX - 46, 380), ('C', UX - 12, 402, UX + 16, 402, UX + 50, 378),
         ('L', UX + 58, 404), ('C', UX + 18, 432, UX - 18, 432, UX - 56, 404), ('Z',)],
        fill=grad((232, 128, 102), (176, 84, 64), (UX - 56, 372), (UX + 58, 432)))
rr(UX - 58, 240, 122, 116, 30, fill=grad((238, 244, 250), (128, 142, 158), (UX - 58, 240), (UX + 64, 356)), rot=(-3, UX, 300))
rr(UX - 50, 248, 106, 20, 10, fill=solid((255, 255, 255), 0.30), rot=(-3, UX, 300))
# visor
rr(UX - 42, 278, 88, 54, 20, fill=grad((48, 60, 78), (26, 34, 48), (UX - 42, 278), (UX + 46, 332)), rot=(-3, UX, 300))
for s in (-1, 1):
    ex = UX + s * 21
    glow(ex, 304, 22, (150, 232, 255), 0.38)
    cv.ellipse(ex, 304, 12, 8, fill=grad((196, 242, 255), (78, 160, 196), (ex - 12, 296), (ex + 12, 312)), rot=(-3, UX, 300))
cv.path([('M', UX - 20, 318), ('C', UX - 8, 328, UX + 8, 328, UX + 20, 318)], stroke=solid((126, 216, 246), 0.9), sw=4)
# dish antenna tilted towards dad
limb(UX + 46, 262, UX + 74, 232, 8, solid((150, 162, 178)))
cv.ellipse(UX + 82, 222, 30, 14, fill=grad((226, 234, 242), (136, 148, 164), (UX + 52, 208), (UX + 112, 236)), rot=(-38, UX + 82, 222), stroke=solid((110, 122, 138)), sw=3)
cv.ellipse(UX + 76, 216, 12, 6, fill=solid((255, 255, 255), 0.35), rot=(-38, UX + 82, 222))

# right arm on hip
limb(UX + 62, 420, UX + 96, 508, 30, grad((186, 198, 212), (104, 116, 132), (UX + 62, 420), (UX + 96, 508)))
limb(UX + 96, 508, UX + 42, 552, 26, grad((186, 198, 212), (104, 116, 132), (UX + 42, 508), (UX + 96, 552)))
rr(UX + 22, 538, 40, 32, 13, fill=grad((226, 232, 240), (128, 140, 156), (UX + 22, 538), (UX + 62, 570)), rot=(-26, UX + 42, 554))
# left arm reaching down towards the kid (not quite touching)
limb(UX - 62, 416, UX - 88, 502, 28, grad((186, 198, 212), (104, 116, 132), (UX - 88, 416), (UX - 62, 502)))
limb(UX - 88, 502, UX - 112, 566, 24, grad((186, 198, 212), (104, 116, 132), (UX - 112, 502), (UX - 88, 566)))
rr(UX - 130, 556, 38, 34, 13, fill=grad((226, 232, 240), (128, 140, 156), (UX - 130, 556), (UX - 92, 590)), rot=(18, UX - 111, 573))


# =========================================================== kid (front centre, sunny)

KX, KY = 660, 632
soft_shadow(KX + 2, 782, 82, 22, 0.32)

# legs
rr(KX - 38, 700, 28, 62, 12, fill=grad((226, 162, 74), (166, 104, 44), (KX - 38, 700), (KX - 10, 762)))
rr(KX + 12, 700, 28, 62, 12, fill=grad((226, 162, 74), (166, 104, 44), (KX + 12, 700), (KX + 40, 762)), rot=(-10, KX + 26, 702))
rr(KX - 48, 756, 46, 24, 11, fill=grad((196, 128, 58), (128, 78, 34), (KX - 48, 756), (KX - 2, 780)))
rr(KX + 4, 758, 48, 24, 11, fill=grad((196, 128, 58), (128, 78, 34), (KX + 4, 758), (KX + 52, 782)), rot=(-10, KX + 28, 770))
# body
rr(KX - 48, 606, 96, 116, 34, fill=grad((250, 196, 96), (196, 122, 50), (KX - 48, 606), (KX + 48, 722)))
rr(KX - 40, 614, 80, 16, 8, fill=solid((255, 255, 255), 0.22))
rr(KX - 34, 664, 68, 12, 6, fill=solid((170, 98, 40), 0.6))
# head
glow(KX, 566, 96, (255, 214, 132), 0.22)
cv.circle(KX, 566, 50, fill=grad((255, 216, 128), (214, 132, 52), (KX - 46, 520), (KX + 46, 612)))
cv.circle(KX - 10, 552, 16, fill=solid((255, 255, 255), 0.30))
cv.circle(KX, 572, 35, fill=grad((48, 58, 72), (28, 36, 48), (KX - 35, 537), (KX + 35, 607)))
for s in (-1, 1):
    ex = KX + s * 15
    glow(ex, 564, 18, (255, 232, 176), 0.35)
    cv.circle(ex, 564, 9, fill=solid((255, 236, 190)))
    cv.circle(ex - 3, 560, 3.4, fill=solid((255, 255, 255)))
cv.path([('M', KX - 16, 586), ('C', KX - 6, 598, KX + 6, 598, KX + 16, 586)], stroke=solid((255, 226, 170)), sw=6)
antenna(KX + 16, 522, KX + 34, 484, 9, solid((214, 150, 70)), solid((160, 100, 44)), bend=(KX + 22, 506, KX + 28, 496))
# arm reaching up to mum (gap!)
limb(KX - 40, 634, KX - 62, 596, 22, grad((238, 178, 88), (186, 116, 50), (KX - 62, 596), (KX - 40, 634)))
cv.circle(KX - 72, 582, 17, fill=grad((250, 200, 110), (196, 124, 56), (KX - 88, 566), (KX - 56, 598)))
# other arm hugging a bolt-plush
limb(KX + 42, 634, KX + 56, 676, 22, grad((238, 178, 88), (186, 116, 50), (KX + 42, 634), (KX + 56, 676)))
cv.circle(KX + 58, 688, 16, fill=grad((250, 200, 110), (196, 124, 56), (KX + 44, 674), (KX + 72, 702)))
bolt(KX + 40, 700, 24, (150, 196, 216), (76, 122, 152), rot=12)
cv.circle(KX + 32, 694, 4, fill=solid((36, 58, 76)))
cv.circle(KX + 48, 694, 4, fill=solid((36, 58, 76)))
cv.path([('M', KX + 32, 706), ('C', KX + 38, 712, KX + 44, 712, KX + 50, 706)], stroke=solid((36, 58, 76)), sw=3)


# =========================================================== teen (left, slouching away)

TX = 254
soft_shadow(TX - 10, 796, 116, 28, 0.34)

# legs (one straight, one on a wheel)
rr(TX - 54, 552, 40, 218, 15, fill=grad((84, 94, 112), (46, 54, 68), (TX - 54, 552), (TX - 14, 770)), rot=(4, TX - 34, 556))
rr(TX + 4, 548, 38, 176, 15, fill=grad((84, 94, 112), (46, 54, 68), (TX + 4, 548), (TX + 42, 724)), rot=(-8, TX + 23, 552))
rr(TX - 72, 758, 72, 26, 12, fill=grad((64, 72, 88), (38, 44, 56), (TX - 72, 758), (TX, 784)))
cv.circle(TX + 34, 736, 30, fill=grad((70, 80, 96), (34, 40, 52), (TX + 6, 708), (TX + 62, 764)), stroke=solid((26, 32, 42)), sw=4)
cv.circle(TX + 34, 736, 12, fill=grad((128, 142, 160), (66, 76, 92), (TX + 24, 726), (TX + 44, 746)))
# torso, tilted away
rr(TX - 62, 340, 122, 232, 26, fill=grad((92, 102, 122), (44, 52, 66), (TX - 62, 340), (TX + 60, 572)), rot=(-7, TX, 450))
rr(TX - 54, 350, 106, 18, 9, fill=solid((255, 255, 255), 0.12), rot=(-7, TX, 450))
rr(TX - 58, 356, 118, 40, 18, fill=grad((72, 82, 100), (40, 48, 62), (TX - 58, 356), (TX + 60, 396)), rot=(-7, TX, 450))
rr(TX - 30, 420, 62, 12, 6, fill=solid((36, 42, 54)), rot=(-7, TX, 450))
rr(TX - 30, 444, 40, 12, 6, fill=solid((36, 42, 54)), rot=(-7, TX, 450))
# head + screen
rr(TX - 52, 252, 108, 96, 22, fill=grad((78, 88, 106), (38, 46, 60), (TX - 52, 252), (TX + 56, 348)), rot=(-7, TX, 300))
rr(TX - 38, 272, 82, 58, 12, fill=grad((30, 38, 50), (18, 24, 34), (TX - 38, 272), (TX + 44, 330)), rot=(-7, TX, 300))
rr(TX - 28, 292, 26, 8, 4, fill=solid((138, 206, 226), 0.85), rot=(-7, TX, 300))
rr(TX + 6, 292, 20, 8, 4, fill=solid((138, 206, 226), 0.6), rot=(-7, TX, 300))
rr(TX - 18, 314, 38, 6, 3, fill=solid((110, 132, 152), 0.6), rot=(-7, TX, 300))
# headphones
cv.path([('M', TX - 62, 296), ('C', TX - 58, 236, TX + 58, 232, TX + 62, 292)], stroke=grad((58, 66, 82), (32, 38, 50), (TX - 62, 240), (TX + 62, 300)), sw=13)
rr(TX - 78, 288, 30, 52, 13, fill=grad((66, 76, 94), (34, 40, 52), (TX - 78, 288), (TX - 48, 340)), rot=(-7, TX, 300))
rr(TX + 52, 282, 30, 52, 13, fill=grad((66, 76, 94), (34, 40, 52), (TX + 52, 282), (TX + 82, 334)), rot=(-7, TX, 300))
cv.circle(TX - 63, 314, 9, fill=solid((120, 200, 222), 0.8), rot=(-7, TX, 300))
cv.path([('M', TX - 70, 340), ('C', TX - 96, 396, TX - 58, 434, TX - 78, 492)], stroke=solid((30, 36, 48)), sw=5)
# crossed arm + arm resting on the dog
limb(TX - 52, 424, TX + 52, 452, 28, grad((104, 116, 136), (52, 60, 76), (TX - 52, 424), (TX + 52, 452)))
cv.circle(TX + 62, 456, 15, fill=grad((112, 124, 144), (58, 66, 82), (TX + 48, 442), (TX + 76, 470)))
limb(TX + 56, 400, TX + 44, 470, 26, grad((104, 116, 136), (52, 60, 76), (TX + 44, 400), (TX + 60, 470)))
cv.circle(TX + 34, 478, 14, fill=grad((112, 124, 144), (58, 66, 82), (TX + 22, 466), (TX + 46, 492)))
limb(TX + 52, 470, TX + 96, 566, 24, grad((104, 116, 136), (52, 60, 76), (TX + 52, 470), (TX + 96, 566)))
cv.circle(TX + 104, 588, 17, fill=grad((118, 130, 150), (62, 70, 86), (TX + 88, 572), (TX + 120, 604)))


# =========================================================== dog (looking up at the teen)

DGX = 352
soft_shadow(DGX + 8, 786, 96, 22, 0.28)

for lx in (-32, -8, 16, 38):
    rr(DGX + lx, 736, 17, 42, 8, fill=grad((120, 132, 152), (66, 76, 92), (DGX + lx, 736), (DGX + lx + 17, 778)))
rr(DGX - 42, 682, 96, 62, 22, fill=grad((152, 164, 184), (78, 88, 106), (DGX - 42, 682), (DGX + 54, 744)))
rr(DGX - 34, 690, 80, 12, 6, fill=solid((255, 255, 255), 0.16))
rr(DGX - 40, 700, 26, 34, 12, fill=grad((128, 140, 160), (72, 82, 100), (DGX - 40, 700), (DGX - 14, 734)))
# tail up
limb(DGX - 44, 700, DGX - 78, 656, 11, solid((110, 122, 142)))
cv.circle(DGX - 82, 650, 9, fill=solid((128, 140, 160)))
# head
rr(DGX + 34, 632, 68, 58, 20, fill=grad((170, 182, 200), (88, 98, 116), (DGX + 34, 632), (DGX + 102, 690)))
rr(DGX + 84, 658, 42, 30, 13, fill=grad((140, 152, 172), (78, 88, 106), (DGX + 84, 658), (DGX + 126, 688)))
cv.circle(DGX + 122, 672, 9, fill=solid((34, 42, 56)))
cv.circle(DGX + 119, 669, 3, fill=solid((190, 202, 218), 0.7))
glow(DGX + 62, 654, 20, (255, 214, 138), 0.32)
cv.circle(DGX + 62, 654, 11, fill=grad((255, 226, 168), (216, 152, 82), (DGX + 52, 644), (DGX + 72, 664)))
cv.circle(DGX + 58, 650, 4, fill=solid((255, 252, 240)))
# floppy ear + antenna ear
cv.path([('M', DGX + 40, 638), ('C', DGX + 12, 612, DGX + 6, 668, DGX + 26, 686), ('C', DGX + 32, 668, DGX + 36, 652, DGX + 46, 644), ('Z',)],
        fill=grad((112, 124, 144), (58, 66, 82), (DGX + 6, 612), (DGX + 46, 686)))
antenna(DGX + 86, 632, DGX + 92, 592, 8, solid((126, 138, 158)), solid((84, 94, 112)))
rr(DGX + 36, 622, 54, 13, 6, fill=grad((226, 128, 102), (166, 78, 60), (DGX + 36, 622), (DGX + 90, 635)), rot=(-6, DGX + 63, 628))


# =========================================================== baby (floor, toppled)

BX, BY = 470, 742
soft_shadow(BX + 10, 802, 86, 22, 0.30)

rr(BX - 34, 706, 72, 76, 28, fill=grad((150, 214, 190), (66, 132, 112), (BX - 34, 706), (BX + 38, 782)), rot=(22, BX, 742))
rr(BX - 26, 712, 56, 14, 7, fill=solid((255, 255, 255), 0.24), rot=(22, BX, 742))
# waving arm
limb(BX + 22, 722, BX + 52, 686, 19, grad((150, 214, 190), (78, 148, 126), (BX + 22, 686), (BX + 52, 722)))
cv.circle(BX + 58, 678, 14, fill=grad((176, 228, 208), (86, 152, 128), (BX + 46, 666), (BX + 70, 692)))
limb(BX - 30, 726, BX - 52, 752, 19, grad((150, 214, 190), (78, 148, 126), (BX - 52, 726), (BX - 30, 752)))
cv.circle(BX - 58, 758, 13, fill=grad((176, 228, 208), (86, 152, 128), (BX - 70, 746), (BX - 46, 770)))
# legs + wheel
rr(BX - 30, 766, 22, 34, 10, fill=grad((122, 186, 162), (66, 122, 104), (BX - 30, 766), (BX - 8, 800)), rot=(18, BX - 20, 768))
cv.circle(BX + 26, 790, 19, fill=grad((92, 108, 124), (44, 54, 68), (BX + 10, 774), (BX + 42, 806)), stroke=solid((34, 42, 54)), sw=3)
cv.circle(BX + 26, 790, 7, fill=solid((146, 162, 180)))
# head
cv.circle(BX - 18, 706, 37, fill=grad((186, 234, 214), (88, 158, 134), (BX - 50, 676), (BX + 14, 738)))
cv.circle(BX - 30, 694, 11, fill=solid((255, 255, 255), 0.32))
cv.circle(BX - 34, 702, 8, fill=solid((38, 62, 58)))
cv.circle(BX - 2, 700, 8, fill=solid((38, 62, 58)))
cv.circle(BX - 36, 699, 3, fill=solid((236, 255, 250)))
cv.circle(BX - 4, 697, 3, fill=solid((236, 255, 250)))
# pacifier
cv.circle(BX - 16, 722, 13, fill=grad((226, 236, 242), (150, 168, 182), (BX - 28, 710), (BX - 4, 734)))
cv.circle(BX - 16, 722, 22, fill=solid((255, 255, 255), 0.0), stroke=solid((206, 216, 226)), sw=6)
limb(BX - 6, 676, BX + 2, 660, 6, solid((110, 168, 146)))
cv.circle(BX + 5, 652, 8, fill=grad((176, 228, 208), (86, 152, 128), (BX - 2, 645), (BX + 12, 659)))
# loose bolt rolling away
bolt(BX - 128, 802, 13, (150, 162, 178), (72, 82, 98), rot=18)
cv.ellipse(BX - 128, 816, 17, 5, fill=solid((18, 12, 20), 0.22))


# =========================================================== potted plant (between mum and grandma)

PX = 886
rr(PX, 640, 78, 92, 12, fill=grad((186, 118, 82), (108, 62, 42), (PX, 640), (PX + 78, 732)))
rr(PX - 6, 628, 90, 22, 10, fill=grad((204, 136, 96), (128, 76, 52), (PX - 6, 628), (PX + 84, 650)))
for i, (ang, ln, wdt, c) in enumerate([(-118, 96, 22, (112, 158, 118)), (-72, 118, 26, (134, 182, 132)),
                                       (-30, 92, 20, (98, 146, 108)), (-150, 74, 18, (126, 172, 126)),
                                       (-96, 132, 24, (118, 168, 122))]):
    a = math.radians(ang)
    x1, y1 = PX + 40 + ln * math.cos(a), 636 + ln * math.sin(a)
    limb(PX + 40, 642, x1, y1, 7, solid((88, 118, 88)))
    cv.ellipse(x1, y1, wdt, wdt * 0.5, fill=grad((170, 212, 158), c, (x1 - wdt, y1 - wdt), (x1 + wdt, y1 + wdt)),
               rot=(ang + 90, x1, y1))


# =========================================================== finishing light

cv.rect(0, 0, W, H, fill=radial([(0.0, (255, 232, 196), 0.055), (0.55, (255, 214, 170), 0.02), (1.0, (12, 10, 18), 0.0)],
                                (596, 360), 760))
cv.rect(0, 0, W, H, fill=radial([(0.0, (0, 0, 0), 0.0), (0.58, (0, 0, 0), 0.06), (0.82, (4, 4, 10), 0.30), (1.0, (2, 2, 8), 0.62)],
                                (600, 430), 860))


# =========================================================== write

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'portrait.svg'), 'w') as fh:
    fh.write(cv.to_svg())
cv.to_png(os.path.join(OUT, 'portrait.png'), ss=2, bg=(30, 38, 56))
print('done', len(cv.cmds), 'commands')