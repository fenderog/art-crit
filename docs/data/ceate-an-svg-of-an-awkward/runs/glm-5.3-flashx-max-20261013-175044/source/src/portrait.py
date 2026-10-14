#!/usr/bin/env python3
"""
Awkward Robot Family Portrait
=============================
One shared parametric scene (pure Python, stdlib only) rendered three ways:
  * SVG  (vector, the main deliverable)
  * PNG  (custom scanline rasterizer, 2x supersampled)
  * MP4  (frames -> ffmpeg h264, subtle looping awkward animations)

Cast (left to right):
  GRANDMA  - antique sage-green unit on a stool, wilting antenna, clutches purse
  DAD      - stiff slate-blue unit, forced grin, thumbs-up, clamps teen's shoulder
  TEEN     - slouched charcoal unit, arms crossed, half-lidded eyes looking away
  MOM      - coral hourglass unit, strained polite smile, one hand on teen's shoulder
  BABY     - cream peanut unit in mom's arm, cross-eyed, drooling oil
  KID      - chunky yellow cyclops, hugs teen's leg, gap-toothed grin, hopping
  ROBO-DOG - derpy pet, mid-wag antenna tail, tongue out
"""
import math, os, sys, zlib, struct

W, H = 1600, 1200
HORIZON = 880
DUR = 6.0
FPS = 12
TAU = math.tau
SHIFT_X = 75          # centers the composition

# ---------------------------------------------------------------- palette
BG_IN   = (143, 163, 184); BG_OUT = (74, 90, 106)
FL_TOP  = (113, 98, 89);   FL_BOT = (66, 57, 52)
SCR     = (26, 32, 44)     # face screens
EYEW    = (242, 246, 250); PUP = (28, 34, 46)
SHADOW  = (28, 32, 42)

D_BODY  = (96, 124, 158);  D_DARK = (66, 88, 118);  D_PANEL = (214, 224, 236)
D_GLOVE = (58, 78, 104);   GOLD = (222, 178, 84);  D_RED = (188, 84, 74)
D_TEAL  = (92, 168, 158)

M_BODY  = (219, 138, 118); M_DARK = (182, 106, 88); M_PANEL = (246, 236, 222)
M_GLOVE = (196, 116, 96);  PINK = (238, 158, 168)

T_BODY  = (76, 68, 90);    T_DARK = (56, 50, 68);  T_DARK2 = (44, 40, 56)
T_LEG   = (64, 60, 82);    MINT = (152, 228, 178); MINT_D = (108, 164, 128)
BUD     = (232, 236, 240)

K_BODY  = (240, 184, 66);  K_DARK = (204, 146, 44); RING = (70, 60, 54)
LENS    = (250, 246, 238); IRIS = (146, 88, 44);    MOUTH = (146, 60, 56)
K_RED   = (206, 84, 70)

G_BODY  = (142, 152, 120); G_DARK = (110, 120, 90); RUST = (172, 104, 60)
SHAWL   = (172, 162, 186); WOOD = (152, 112, 76);   PURSE = (150, 98, 66)
PURSE_D = (124, 78, 52);   RIM = (238, 240, 242);  LENSG = (190, 208, 226)

B_BODY  = (238, 226, 206); B_DARK = (206, 188, 162); CHEEK = (238, 150, 150)
LED     = (98, 190, 178);  B_MOUTH = (120, 70, 60); B_EYE = (60, 52, 48)

DG_BODY = (160, 168, 182); DG_DARK = (122, 130, 144); BELLY = (204, 210, 220)
TONGUE  = (226, 122, 132); COLLAR = (188, 72, 66);  NOSE = (52, 54, 60)

# ---------------------------------------------------------------- geometry helpers
def clamp(v, a, b): return a if v < a else (b if v > b else v)

def ell_pts(cx, cy, rx, ry, a0=0.0, a1=None, n=24):
    if a1 is None: a1 = TAU
    rx = max(0.5, rx); ry = max(0.5, ry)
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n),
             cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def rrect_pts(x, y, w, h, r, n=4):
    r = min(r, w / 2, h / 2)
    return (ell_pts(x + r, y + r, r, r, math.pi, 1.5 * math.pi, n) +
            ell_pts(x + w - r, y + r, r, r, 1.5 * math.pi, TAU, n) +
            ell_pts(x + w - r, y + h - r, r, r, 0, 0.5 * math.pi, n) +
            ell_pts(x + r, y + h - r, r, r, 0.5 * math.pi, math.pi, n))

def cap_pts(p0, p1, r0, r1=None, n=10):
    if r1 is None: r1 = r0
    th = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    return (ell_pts(p0[0], p0[1], r0, r0, th + math.pi / 2, th + 3 * math.pi / 2, n) +
            ell_pts(p1[0], p1[1], r1, r1, th - math.pi / 2, th + math.pi / 2, n))

def arc_thick(cx, cy, rx, ry, a0, a1, w, n=16):
    return (ell_pts(cx, cy, rx + w / 2, ry + w / 2, a0, a1, n) +
            ell_pts(cx, cy, max(0.6, rx - w / 2), max(0.6, ry - w / 2), a1, a0, n))

def bez(p0, p1, p2, p3, n=12):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
                    u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]))
    return pts

def blob_pts(cx, cy, r, k, n, seed):
    pts = []
    for i in range(n):
        a = TAU * i / n
        rr = r * (1 - k / 2 + k * (((i * 7 + seed * 13) % 10) / 10))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def star_pts(cx, cy, r1, r2, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = rot + math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def tear_pts(cx, cy, r):
    pts = ell_pts(cx, cy, r, r, 0, math.pi, 10)
    pts += bez((cx - r, cy), (cx - r * 0.95, cy - r * 1.5), (cx - r * 0.3, cy - r * 1.7), (cx, cy - r * 2.3), 8)
    pts += bez((cx, cy - r * 2.3), (cx + r * 0.3, cy - r * 1.7), (cx + r * 0.95, cy - r * 1.5), (cx + r, cy), 8)
    return pts

def rot_about(pts, cx, cy, ang):
    s, c = math.sin(ang), math.cos(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

def shift_pts(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]

def pulse(t, phase, width=0.10):
    """1.0 near phase (in loop turns), 0 outside."""
    d = abs((t / DUR - phase + 0.5) % 1.0 - 0.5)
    return max(0.0, 1.0 - d / width)

# ---------------------------------------------------------------- shape list
class L:
    def __init__(self): self.items = []
    def add(self, pts, c, a=255): self.items.append({'pts': pts, 'c': c, 'a': a})
    def poly(self, pts, c, a=255): self.add(pts, c, a)
    def circle(self, cx, cy, r, c, a=255, n=30): self.add(ell_pts(cx, cy, r, r, 0, TAU, n), c, a)
    def ell(self, cx, cy, rx, ry, c, a=255, n=30): self.add(ell_pts(cx, cy, rx, ry, 0, TAU, n), c, a)
    def rrect(self, x, y, w, h, r, c, a=255): self.add(rrect_pts(x, y, w, h, r), c, a)
    def cap(self, p0, p1, r, c, a=255, r1=None): self.add(cap_pts(p0, p1, r, r1), c, a)
    def arc(self, cx, cy, rx, ry, a0, a1, w, c, a=255): self.add(arc_thick(cx, cy, rx, ry, a0, a1, w), c, a)

def rot_group(items, start, cx, cy, ang):
    for s in items[start:]:
        s['pts'] = rot_about(s['pts'], cx, cy, ang)

def shift_group(items, start, dx, dy):
    if dx == 0 and dy == 0: return
    for s in items[start:]:
        s['pts'] = shift_pts(s['pts'], dx, dy)

# ---------------------------------------------------------------- cast
def shadows(g):
    for (x, y, rx, ry) in [(270, 1036, 100, 18), (480, 1034, 116, 20),
                           (694, 1042, 100, 18), (912, 1022, 116, 20),
                           (764, 1104, 62, 12), (1212, 1124, 86, 14)]:
        g.ell(x, y, rx * 1.14, ry * 1.4, SHADOW, 30)
        g.ell(x, y, rx, ry, SHADOW, 42)

# ..... GRANDMA -----------------------------------------------------------
def grandma(g, t):
    sway = 0.06 * math.sin(TAU * t / DUR)
    # stool
    for (x0, y0, x1, y1) in [(222, 928, 214, 1030), (278, 928, 286, 1030), (250, 932, 250, 1036)]:
        g.cap((x0, y0), (x1, y1), 7, WOOD)
    g.ell(250, 920, 56, 15, (128, 94, 62))
    g.ell(250, 914, 56, 15, WOOD)

    start = len(g.items)
    # skirt + legs + feet
    g.poly([(212, 892), (288, 892), (282, 984)] + bez((282, 984), (270, 996), (230, 996), (218, 984), 8), G_DARK)
    g.cap((230, 984), (224, 1020), 11, G_DARK)
    g.cap((270, 984), (276, 1020), 11, G_DARK)
    g.rrect(206, 1014, 44, 20, 9, (96, 104, 78))
    g.rrect(252, 1014, 44, 20, 9, (96, 104, 78))
    # torso
    g.rrect(188, 748, 124, 158, 26, G_BODY)
    g.poly(blob_pts(286, 784, 15, 0.7, 10, 3), RUST)
    g.poly(blob_pts(212, 866, 11, 0.7, 10, 5), RUST)
    # dial knobs
    for kx in (222, 278):
        g.circle(kx, 802, 10, G_DARK)
        g.circle(kx, 802, 6, (96, 104, 78))
        g.poly([(kx - 1, 802), (kx + 3, 794), (kx + 1, 802)], RIM)
    # shawl
    g.poly(bez((190, 782), (220, 752), (280, 752), (310, 782), 12) +
           [(296, 892), (250, 908), (204, 892)], SHAWL)
    g.arc(250, 780, 62, 20, math.pi, TAU, 5, (150, 140, 168))
    # arms + purse + hands
    g.cap((196, 788), (214, 858), 13, (126, 136, 102))
    g.cap((304, 788), (286, 858), 13, (126, 136, 102))
    g.cap((214, 858), (242, 898), 11, (126, 136, 102))
    g.cap((286, 858), (258, 898), 11, (126, 136, 102))
    g.arc(250, 890, 26, 20, math.pi, TAU, 5, PURSE_D)                    # handle
    g.rrect(220, 884, 60, 50, 10, PURSE)
    g.rrect(220, 884, 60, 22, 9, PURSE_D)
    g.circle(250, 908, 5, GOLD)
    g.circle(236, 902, 13, (126, 136, 102))
    g.circle(264, 902, 13, (126, 136, 102))
    # head
    g.ell(244, 696, 62, 58, G_BODY)
    g.ell(244, 712, 52, 44, (188, 196, 164))
    g.arc(244, 662, 42, 16, math.pi, TAU, 3, G_DARK)
    # glasses + squint eyes
    g.circle(222, 708, 18, RIM)
    g.circle(266, 708, 18, RIM)
    flick = 1.0 - 0.75 * pulse(t, 0.85, 0.10)
    g.circle(222, 708, 13, LENSG, int(110 * flick))
    g.circle(266, 708, 13, LENSG, int(110 * flick))
    g.arc(222, 710, 8, 6, math.pi, TAU, 4, (70, 76, 58))
    g.arc(266, 710, 8, 6, math.pi, TAU, 4, (70, 76, 58))
    g.cap((238, 706), (250, 706), 2.5, RIM)
    # smile + cheeks
    g.arc(244, 736, 15, 8, 0.15 * math.pi, 0.85 * math.pi, 5, (86, 92, 70))
    g.ell(214, 730, 8, 5, CHEEK, 70)
    g.ell(274, 730, 8, 5, CHEEK, 70)
    # wilting antenna (animated)
    a0 = len(g.items)
    g.cap((244, 648), (246, 576), 3.5, G_DARK)
    g.cap((246, 576), (272, 528), 3.5, G_DARK)
    g.circle(274, 524, 7, (96, 104, 78))
    g.circle(270, 530, 3, RUST)
    rot_group(g.items, a0, 244, 650, sway)
    rot_group(g.items, start, 250, 918, -0.05)   # gentle hunch

# ..... DAD ---------------------------------------------------------------
def dad_body(g, t):
    cx = 480
    wig = 0.05 * math.sin(TAU * 2 * t / DUR)
    # wind-up key (behind torso, wound tight)
    k0 = len(g.items)
    g.rrect(346, 612, 48, 12, 6, GOLD)
    g.rrect(320, 600, 28, 46, 12, GOLD)
    g.circle(334, 607, 14, GOLD)
    g.circle(334, 631, 14, GOLD)
    g.circle(334, 619, 5, (150, 112, 40))
    rot_group(g.items, k0, 394, 618, wig)
    # legs + feet
    g.cap((442, 1000), (442, 862), 20, D_DARK)
    g.cap((518, 1000), (518, 862), 20, D_DARK)
    g.rrect(408, 988, 66, 26, 11, D_GLOVE)
    g.rrect(486, 988, 66, 26, 11, D_GLOVE)
    g.rrect(418, 830, 124, 52, 18, D_DARK)
    # torso + panel
    g.rrect(380, 630, 200, 220, 28, D_BODY)
    g.rrect(412, 664, 136, 142, 16, D_PANEL)
    g.poly(star_pts(446, 700, 15, 6.5), GOLD)
    g.circle(514, 700, 8, D_RED)
    g.circle(514, 734, 8, D_TEAL)
    for yy in (772, 786, 800):
        g.rrect(432, yy, 96, 6, 3, (170, 182, 198))
    # neck + head + fins + antenna
    g.rrect(458, 596, 44, 44, 10, D_DARK)
    g.rrect(392, 448, 176, 160, 30, D_BODY)
    for fx in range(5):
        g.rrect(412 + fx * 29, 430, 13, 24, 4, D_DARK)
    g.cap((548, 452), (566, 404), 4, D_DARK)
    g.cap((566, 404), (582, 388), 4, D_DARK)
    g.circle(584, 386, 8, D_RED)
    # face
    g.rrect(412, 472, 136, 114, 22, SCR)
    blink = 1.0 - 0.94 * pulse(t, 0.50, 0.06)
    for ex in (444, 516):
        g.ell(ex, 522, 15, 15 * blink, EYEW)
        if blink > 0.35:
            g.ell(ex, 522, 5.5, 5.5 * blink, PUP)
    b0 = len(g.items)
    g.rrect(428, 492, 30, 7, 3, (208, 216, 226))
    rot_group(g.items, b0, 443, 495, -0.12)
    b1 = len(g.items)
    g.rrect(498, 484, 30, 7, 3, (208, 216, 226))
    rot_group(g.items, b1, 513, 487, 0.20)
    grin = 42 + 2.5 * math.sin(TAU * 2 * t / DUR)     # too-wide forced grin
    g.arc(cx, 550, grin, 20, 0.12 * math.pi, 0.88 * math.pi, 11, EYEW)
    # left arm (viewer left): stiff thumbs-up
    g.circle(388, 662, 26, D_BODY)
    g.cap((388, 662), (374, 756), 16, D_BODY)
    g.circle(374, 756, 15, D_DARK)
    g.cap((374, 756), (371, 876), 13, D_BODY)
    tw = 0.06 * math.sin(TAU * 3 * t / DUR)
    f0 = len(g.items)
    g.rrect(351, 874, 42, 40, 11, D_GLOVE)
    g.cap((372, 882), (379, 846), 7, D_GLOVE)
    g.arc(372, 894, 14, 8, 0.1 * math.pi, 0.9 * math.pi, 3, (44, 60, 82))
    rot_group(g.items, f0, 372, 894, tw)

def dad_clamp(g, t):
    """Dad's other arm: clamped on teen's shoulder, grip too tight."""
    g.circle(572, 662, 26, D_BODY)
    g.cap((572, 662), (610, 748), 16, D_BODY)
    g.circle(610, 748, 15, D_DARK)
    g.cap((610, 748), (641, 699), 13, D_BODY)
    g.circle(641, 697, 19, D_GLOVE)
    for i, ang in enumerate((-0.5, 0.0, 0.5)):        # dent / squeeze marks
        dx, dy = 641 + 20 * math.sin(ang), 697 + 14 + 4 * math.cos(ang)
        g.poly(rot_about([(-6, 0), (6, 0), (4, 5), (-4, 5)], 0, 0, ang * 0.8) if False
               else [(dx - 6, dy), (dx + 6, dy), (dx + 4, dy + 6), (dx - 4, dy + 6)], T_DARK2, 170)

# ..... TEEN --------------------------------------------------------------
def teen(g, t):
    cx, gy = 690, 1030
    sigh = math.sin(TAU * t / DUR)
    head_dy = -2.5 * (sigh if sigh > 0 else 0) ** 2
    look = 5 + 2.5 * math.sin(TAU * t / DUR + 1.0)
    # legs (planted)
    g.cap((658, 880), (652, 1014), 17, (78, 74, 100))
    g.cap((724, 880), (736, 1014), 17, (78, 74, 100))
    g.arc(734, 946, 10, 14, -0.6, 0.9, 3, (100, 96, 126))   # knee highlight
    g.rrect(624, 1008, 56, 26, 10, (40, 38, 50))
    g.rrect(714, 1008, 58, 26, 10, (40, 38, 50))
    g.rrect(624, 1008, 56, 8, 4, (88, 86, 96))
    g.rrect(714, 1008, 58, 8, 4, (88, 86, 96))
    # ---- upper body group (slouched away from dad) ----
    s0 = len(g.items)
    g.rrect(624, 688, 132, 200, 26, T_BODY)
    g.rrect(658, 798, 64, 58, 14, T_DARK)                # kangaroo pocket
    g.ell(690, 700, 60, 26, T_DARK2)                     # bunched hood
    g.cap((678, 716), (676, 742), 3, (150, 144, 162))
    g.cap((702, 714), (704, 742), 3, (150, 144, 162))
    g.circle(676, 744, 4, (150, 144, 162))
    g.circle(704, 742, 4, (150, 144, 162))
    # crossed arms
    g.circle(646, 708, 20, T_BODY)
    g.circle(734, 708, 20, T_BODY)
    g.cap((646, 708), (672, 786), 15, T_BODY)
    g.cap((734, 708), (708, 790), 15, T_BODY)
    g.cap((674, 790), (744, 760), 14, T_DARK)
    g.cap((708, 792), (644, 764), 14, T_DARK)
    rot_group(g.items, s0, 690, 884, 0.09)
    # ---- head group (tilted away) ----
    h0 = len(g.items)
    g.rrect(618, 556, 144, 136, 30, T_BODY)
    g.rrect(640, 578, 100, 88, 20, SCR)
    for ex in (668, 716):
        g.ell(ex, 622, 11, 8, MINT)
        g.circle(ex + look, 623, 3.5, (20, 26, 22))
    e0 = len(g.items)
    g.rrect(654, 604, 27, 6, 3, MINT_D)
    rot_group(g.items, e0, 667, 607, -0.15)
    e1 = len(g.items)
    g.rrect(705, 604, 27, 6, 3, MINT_D)
    rot_group(g.items, e1, 718, 607, 0.12)
    m0 = len(g.items)
    g.rrect(674, 650, 34, 7, 3, MINT_D)
    rot_group(g.items, m0, 691, 653, 0.05)
    # dent + scratches
    g.arc(754, 592, 14, 12, -1.2, 1.2, 5, T_DARK2)
    g.arc(752, 590, 9, 8, -0.9, 0.7, 2, (100, 92, 116))
    g.cap((738, 572), (750, 558), 2, (100, 92, 116), 170)
    g.cap((744, 588), (758, 580), 2, (100, 92, 116), 170)
    # stub antenna with tape
    g.cap((690, 558), (690, 534), 4, T_DARK2)
    g.circle(690, 532, 6, T_DARK2)
    tp0 = len(g.items)
    g.rrect(677, 539, 26, 12, 3, (200, 196, 186))
    rot_group(g.items, tp0, 690, 545, 0.5)
    # earbuds
    g.circle(652, 624, 8, BUD)
    g.circle(768, 624, 8, BUD)
    rot_group(g.items, h0, 690, 700, 0.16)
    shift_group(g.items, h0, 0, head_dy)
    # dangling earbud cable (drawn in final coords)
    bud_x, bud_y = rot_about([(768, 624)], 690, 700, 0.16)[0]
    bud_x, bud_y = bud_x, bud_y + head_dy
    px, py = rot_about([(695, 815)], 690, 884, 0.09)[0]
    path = bez((bud_x, bud_y), (bud_x + 14, bud_y + 70), (px + 46, py - 20), (px, py), 14)
    for i in range(0, 14, 2):
        g.cap(path[i], path[i + 2], 2.5, BUD)

# ..... MOM + BABY --------------------------------------------------------
def mom(g, t):
    cx = 912
    tilt = 0.02 * math.sin(TAU * t / DUR + 0.6)
    # neck
    g.rrect(884, 646, 30, 62, 12, M_DARK)
    g.rrect(884, 668, 30, 4, 2, (150, 88, 74))
    g.rrect(884, 686, 30, 4, 2, (150, 88, 74))
    # hourglass dress (one polygon, floor-length)
    pts = bez((815, 700), (819, 748), (847, 752), (851, 782), 10)
    pts += bez((851, 782), (855, 830), (823, 838), (821, 866), 10)
    pts += bez((821, 866), (793, 946), (818, 998), (802, 1010), 10)
    pts += ell_pts(895, 1010, 93, 16, math.pi, TAU, 12)
    pts += bez((988, 1010), (972, 946), (967, 940), (969, 866), 10)
    pts += bez((969, 866), (965, 830), (939, 830), (939, 782), 10)
    pts += bez((939, 782), (935, 752), (971, 748), (975, 700), 10)
    pts += ell_pts(895, 704, 80, 26, TAU, math.pi, 14)
    g.poly(pts, M_BODY)
    g.arc(895, 788, 44, 10, 0.12 * math.pi, 0.88 * math.pi, 4, M_DARK, 160)   # waist seam
    g.arc(895, 1010, 80, 12, 0.15 * math.pi, 0.85 * math.pi, 9, M_DARK, 110)  # hem
    g.arc(895, 710, 24, 9, math.pi, TAU, 5, M_DARK)                            # collar
    g.circle(895, 718, 9, GOLD)
    g.circle(895, 718, 4, M_PANEL)
    # ---- head group ----
    h0 = len(g.items)
    g.ell(912, 596, 94, 92, M_DARK)                       # sleek bob shell
    g.arc(912, 596, 94, 92, 0.6, 1.8, 6, (162, 94, 78))   # shell sheen
    g.ell(912, 604, 64, 72, M_BODY)
    g.ell(912, 608, 50, 58, SCR)
    blink = 1.0 - 0.94 * pulse(t, 0.72, 0.06)
    for ex in (890, 934):
        g.ell(ex, 596, 11, 14 * blink, EYEW)
        if blink > 0.35:
            g.ell(ex, 597, 4.5, 5 * blink, PUP)
        g.arc(ex, 585, 13, 6, 1.05 * math.pi, 1.95 * math.pi, 2.5, EYEW, 220)  # lid line
    g.arc(912, 642, 16, 7, 0.15 * math.pi, 0.85 * math.pi, 5, EYEW, 235)
    g.ell(872, 634, 10, 6, (238, 150, 140), 90)
    g.ell(952, 634, 10, 6, (238, 150, 140), 90)
    # flower antenna
    g.cap((886, 518), (860, 486), 3, (110, 140, 96))
    for i in range(5):
        a = TAU * i / 5 - math.pi / 2
        g.circle(854 + 10 * math.cos(a), 478 + 10 * math.sin(a), 7, PINK)
    g.circle(854, 478, 6, GOLD)
    rot_group(g.items, h0, 912, 650, tilt)
    # ---- baby ----
    bx = 980
    wander = 2 * math.sin(TAU * 2 * t / DUR)
    g.cap((954, 806), (932, 780), 8, B_DARK)
    g.cap((1006, 806), (1028, 782), 8, B_DARK)
    g.circle(930, 778, 7, B_DARK)
    g.circle(1030, 780, 7, B_DARK)
    g.cap((966, 856), (962, 888), 8, B_DARK)
    g.cap((994, 856), (1000, 888), 8, B_DARK)
    g.ell(960, 892, 11, 6, B_DARK)
    g.ell(1002, 892, 11, 6, B_DARK)
    g.rrect(948, 782, 64, 80, 20, B_BODY)
    g.circle(980, 824, 11, LED, 70)
    g.circle(980, 824, 7, LED)
    g.circle(980, 748, 46, B_BODY)                        # head
    g.arc(980, 698, 13, 9, -2.8, 0.7, 4, (120, 104, 88))  # curl
    for ex in (964, 996):
        g.circle(ex + wander, 744, 10, B_EYE)
        g.circle(ex + wander - 3, 741, 3, EYEW)
    g.ell(980, 770, 11, 8, B_MOUTH)
    g.ell(980, 773, 6, 4, TONGUE)
    g.ell(946, 762, 9, 6, CHEEK, 110)
    g.ell(1014, 762, 9, 6, CHEEK, 110)
    # oil drool (grows, falls, resets)
    ph = (t % 1.5) / 1.5
    if ph < 0.55:
        g.poly(tear_pts(991, 780, 2 + 3.5 * (ph / 0.55)), (146, 120, 70))
    elif ph < 0.8:
        f = (ph - 0.55) / 0.25
        g.poly(tear_pts(991, 780 + 60 * f * f, 5.5 - 3 * f), (146, 120, 70))
    # ---- mom's cradle arm (over baby) ----
    g.circle(995, 706, 20, M_BODY)
    g.cap((995, 706), (1008, 788), 13, M_BODY)
    g.cap((1008, 788), (1036, 862), 12, M_BODY)
    g.circle(1038, 866, 15, M_GLOVE)
    # ---- mom's clamp arm (on teen's shoulder) ----
    g.circle(829, 706, 20, M_BODY)
    g.cap((829, 706), (795, 764), 13, M_BODY)
    g.cap((795, 764), (747, 704), 12, M_BODY)
    g.circle(745, 701, 15, M_GLOVE)
    for ang in (-0.5, 0.0, 0.5):
        dx, dy = 745 + 15 * math.sin(ang), 715 + 3 * math.cos(ang)
        g.poly([(dx - 5, dy), (dx + 5, dy), (dx + 3, dy + 5), (dx - 3, dy + 5)], T_DARK2, 170)

# ..... KID ---------------------------------------------------------------
def kid(g, t):
    bob = 3 * math.sin(TAU * 2 * t / DUR + 0.8)
    ka = len(g.items)
    # torso (leaning onto teen's leg) + bolt
    g.rrect(754, 906, 68, 96, 22, K_BODY)
    g.poly([(782, 926), (800, 926), (790, 946), (802, 946), (774, 974), (784, 952), (772, 952)], K_RED)
    rot_group(g.items, ka, 788, 1002, -0.12)
    # arms hugging teen's leg
    g.cap((762, 916), (732, 948), 11, K_DARK)
    g.circle(729, 951, 11, K_DARK)
    g.cap((816, 912), (738, 944), 11, K_DARK)
    g.circle(735, 947, 11, K_DARK)
    # legs (one kicked back)
    g.cap((772, 996), (766, 1060), 11, K_DARK)
    g.rrect(744, 1054, 46, 22, 9, K_DARK)
    g.cap((806, 996), (834, 1038), 11, K_DARK)
    f0 = len(g.items)
    g.rrect(820, 1032, 42, 20, 8, K_DARK)
    rot_group(g.items, f0, 842, 1042, 0.7)
    g.arc(824, 1024, 34, 18, -0.5, 0.4, 3, EYEW, 100)
    # big head + cyclops lens
    g.circle(780, 842, 62, K_BODY)
    for ex in (718, 842):
        g.circle(ex, 846, 6, K_DARK)
    shut = 1.0 - 0.85 * pulse(t, 0.30, 0.05)
    g.ell(780, 834, 34, 34, RING)
    g.ell(780, 834, 27, 27 * shut, LENS)
    if shut > 0.3:
        g.ell(776, 824, 14, 14 * shut, IRIS)
        g.ell(777, 824, 7, 7 * shut, (40, 30, 24))
        g.circle(770, 818, 4, EYEW)
    # jagged grin with a missing tooth
    g.rrect(756, 874, 52, 24, 9, MOUTH)
    for tx in (762, 776, 794):
        g.rrect(tx, 876, 10, 9, 2, EYEW)
    g.ell(738, 860, 9, 6, K_RED, 110)
    g.ell(822, 860, 9, 6, K_RED, 110)
    # zigzag antenna
    g.cap((768, 782), (780, 764), 4, K_DARK)
    g.cap((780, 764), (768, 750), 4, K_DARK)
    g.cap((768, 750), (782, 736), 4, K_DARK)
    g.circle(784, 734, 6, K_RED)
    # crooked little bowtie (drawn after head so it shows)
    b0 = len(g.items)
    g.poly([(784, 908), (762, 898), (762, 918)], K_RED)
    g.poly([(784, 908), (806, 898), (806, 918)], K_RED)
    g.circle(784, 908, 5, (160, 60, 52))
    rot_group(g.items, b0, 788, 1002, -0.12)
    shift_group(g.items, ka, -24, bob)

# ..... ROBO-DOG ----------------------------------------------------------
def dog(g, t):
    d0 = len(g.items)
    wag = 0.5 * math.sin(TAU * 3 * t / DUR)
    tilt = 0.03 * math.sin(TAU * 2 * t / DUR + 2.1)
    # tail
    ang = -0.9 + wag
    tip = (1292 + 46 * math.cos(ang), 1030 + 46 * math.sin(ang))
    g.cap((1292, 1030), tip, 5, DG_DARK)
    g.circle(tip[0], tip[1], 8, DG_DARK)
    g.arc(1292, 1030, 56, 44, ang - 0.5, ang + 0.3, 3, EYEW, 90)
    # body
    g.ell(1246, 1062, 58, 58, DG_BODY)
    g.ell(1216, 1058, 32, 42, BELLY)
    g.cap((1200, 1058), (1196, 1112), 11, DG_BODY)
    g.cap((1228, 1058), (1224, 1112), 11, DG_BODY)
    g.ell(1194, 1116, 14, 7, DG_BODY)
    g.ell(1222, 1116, 14, 7, DG_BODY)
    # collar
    g.rrect(1176, 1022, 82, 16, 7, COLLAR)
    g.circle(1216, 1044, 8, GOLD)
    g.circle(1216, 1044, 3, (150, 112, 40))
    # head group (derpy tilt)
    h0 = len(g.items)
    tw = 2 * math.sin(TAU * 3 * t / DUR + 1.2)
    g.rrect(1198, 1000, 52, 34, 12, BELLY)              # snout
    g.rrect(1214, 994, 20, 14, 6, NOSE)
    g.cap((1234, 1022), (1246, 1022), 2.5, NOSE)
    g.rrect(1224 + tw, 1018, 17, 34, 8, TONGUE)
    g.cap((1232 + tw, 1026), (1232 + tw, 1044), 1.5, (196, 92, 104))
    g.rrect(1168, 946, 96, 88, 24, DG_BODY)
    g.circle(1192, 976, 9, EYEW)
    g.circle(1192, 977, 4, PUP)
    g.circle(1238, 974, 10, EYEW)
    g.circle(1242, 972, 4, PUP)                          # derpy offset pupil
    g.circle(1190, 973, 2, EYEW)
    g.circle(1240, 969, 2, EYEW)
    # ears: one folded, one flapping
    g.poly([(1176, 950), (1146, 984), (1180, 998)], DG_DARK)
    g.poly([(1172, 956), (1156, 980), (1174, 988)], (140, 148, 162))
    e0 = len(g.items)
    g.poly([(1250, 950), (1242, 910), (1274, 944)], DG_DARK)
    g.poly([(1252, 946), (1248, 922), (1266, 942)], (140, 148, 162))
    rot_group(g.items, e0, 1250, 948, 0.1 * math.sin(TAU * 3 * t / DUR))
    rot_group(g.items, h0, 1216, 1032, tilt)
    shift_group(g.items, d0, -26, 0)

# ---------------------------------------------------------------- scene
def build(t):
    g = L()
    shadows(g)
    grandma(g, t)
    dad_body(g, t)
    teen(g, t)
    dad_clamp(g, t)
    mom(g, t)
    kid(g, t)
    dog(g, t)
    items = [{'bg': True}] + g.items
    shift_group(items, 1, SHIFT_X, 0)
    return items

# ---------------------------------------------------------------- PNG rasterizer
_base_cache = {}

def make_base(w, h):
    key = (w, h)
    if key in _base_cache: return _base_cache[key]
    buf = bytearray(w * h * 3)
    hz = HORIZON * h / H
    cx, cy = w * 0.5, h * 0.35
    inv_r2 = 1.0 / (w * 0.62) ** 2
    ir, ig, ib = BG_IN; orr, og, ob = BG_OUT
    (ftr, ftg, ftb), (fbr, fbg, fbb) = FL_TOP, FL_BOT
    pcx, pcy, prx, pry = w * 0.5, h * 0.90, w * 0.45, h * 0.22
    xs2 = [(x - cx) ** 2 for x in range(w)]
    i = 0
    for y in range(h):
        vy2 = (y - cy) ** 2
        if y < hz:
            bt = (y - hz) / hz
            _ = bt
            for x in range(w):
                t = (xs2[x] + vy2) * inv_r2
                if t > 1.0: t = 1.0
                buf[i]     = int(ir + (orr - ir) * t)
                buf[i + 1] = int(ig + (og - ig) * t)
                buf[i + 2] = int(ib + (ob - ib) * t)
                i += 3
        else:
            u = (y - hz) / (h - hz)
            fr = ftr + (fbr - ftr) * u
            fg = ftg + (fbg - ftg) * u
            fb2 = ftb + (fbb - ftb) * u
            dy2 = ((y - pcy) / pry) ** 2
            prx2 = prx * prx
            for x in range(w):
                r = fr; gg = fg; b2 = fb2
                d = dy2 + (x - pcx) ** 2 / prx2
                if d < 1.0:
                    s = (1.0 - d) * 16
                    r += s; gg += s * 0.9; b2 += s * 0.75
                buf[i] = int(r); buf[i + 1] = int(gg); buf[i + 2] = int(b2)
                i += 3
    _base_cache[key] = buf
    return buf

def fill_poly(buf, w, h, pts, color, alpha):
    n = len(pts)
    edges = []
    miny, maxy = 1e9, -1e9
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        if y1 != y2:
            edges.append((x1, y1, x2, y2))
            if y1 < miny: miny = y1
            if y2 < miny: miny = y2
            if y1 > maxy: maxy = y1
            if y2 > maxy: maxy = y2
    if not edges: return
    y0 = max(0, int(math.floor(miny - 0.5)))
    y1 = min(h - 1, int(math.ceil(maxy - 0.5)))
    cr, cg, cb = color
    opaque = alpha >= 255
    af = alpha / 255.0; ia = 1 - af
    colb = bytes((cr, cg, cb))
    for y in range(y0, y1 + 1):
        yc = y + 0.5
        xs = []
        for (ex1, ey1, ex2, ey2) in edges:
            if (ey1 <= yc < ey2) or (ey2 <= yc < ey1):
                xs.append(ex1 + (yc - ey1) * (ex2 - ex1) / (ey2 - ey1))
        if not xs: continue
        xs.sort()
        row = y * w * 3
        for j in range(0, len(xs) - 1, 2):
            c0 = int(math.ceil(xs[j] - 0.5)); c1 = int(math.ceil(xs[j + 1] - 0.5))
            if c0 < 0: c0 = 0
            if c1 > w: c1 = w
            ln = c1 - c0
            if ln <= 0: continue
            st = row + c0 * 3
            if opaque:
                buf[st:st + ln * 3] = colb * ln
            else:
                i = st
                for _ in range(ln):
                    buf[i] = int(buf[i] * ia + cr * af)
                    buf[i + 1] = int(buf[i + 1] * ia + cg * af)
                    buf[i + 2] = int(buf[i + 2] * ia + cb * af)
                    i += 3

def downsample2(buf, w, h):
    w2, h2 = w // 2, h // 2
    out = bytearray(w2 * h2 * 3)
    rowlen = w * 3
    pos = 0
    for y in range(h2):
        a = buf[(2 * y) * rowlen: (2 * y) * rowlen + rowlen]
        b = buf[(2 * y + 1) * rowlen: (2 * y + 1) * rowlen + rowlen]
        for x in range(w2):
            i0 = x * 6; i1 = i0 + 3
            out[pos] = (a[i0] + a[i1] + b[i0] + b[i1]) >> 2
            out[pos + 1] = (a[i0 + 1] + a[i1 + 1] + b[i0 + 1] + b[i1 + 1]) >> 2
            out[pos + 2] = (a[i0 + 2] + a[i1 + 2] + b[i0 + 2] + b[i1 + 2]) >> 2
            pos += 3
    return out

def write_png(path, w, h, buf):
    def chunk(typ, data):
        return (struct.pack('>I', len(data)) + typ + data +
                struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))
    raw = b''.join(b'\x00' + bytes(buf[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    png = (b'\x89PNG\r\n\x1a\n' +
           chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) +
           chunk(b'IDAT', zlib.compress(raw, 6)) +
           chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)

def render_png(shapes, path, w, h):
    ss = 2
    sc = (w * ss) / W
    base = make_base(w * ss, h * ss)
    buf = bytearray(base)
    for s in shapes:
        if 'bg' in s: continue
        pts = [(x * sc, y * sc) for x, y in s['pts']]
        fill_poly(buf, w * ss, h * ss, pts, s['c'], s['a'])
    write_png(path, w, h, downsample2(buf, w * ss, h * ss))

# ---------------------------------------------------------------- SVG
def emit_svg(shapes, path):
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    o.append('<defs>')
    o.append('<radialGradient id="bg" gradientUnits="userSpaceOnUse" cx="800" cy="420" r="992">'
             '<stop offset="0" stop-color="rgb(%d,%d,%d)"/><stop offset="1" stop-color="rgb(%d,%d,%d)"/>'
             '</radialGradient>' % (BG_IN + BG_OUT))
    o.append('<linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="0" y1="880" x2="0" y2="1200">'
             '<stop offset="0" stop-color="rgb(%d,%d,%d)"/><stop offset="1" stop-color="rgb(%d,%d,%d)"/>'
             '</linearGradient>' % (FL_TOP + FL_BOT))
    o.append('<radialGradient id="pool" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" '
             'gradientTransform="translate(800,1080) scale(720,264)">'
             '<stop offset="0" stop-color="rgb(255,240,214)" stop-opacity="0.10"/>'
             '<stop offset="1" stop-color="rgb(255,240,214)" stop-opacity="0"/></radialGradient>')
    o.append('<clipPath id="floor"><rect x="0" y="880" width="1600" height="320"/></clipPath>')
    o.append('</defs>')
    o.append('<rect x="0" y="0" width="1600" height="880" fill="url(#bg)"/>')
    o.append('<rect x="0" y="880" width="1600" height="320" fill="url(#fl)"/>')
    o.append('<ellipse cx="800" cy="1080" rx="720" ry="264" fill="url(#pool)" clip-path="url(#floor)"/>')
    for s in shapes:
        if 'bg' in s: continue
        p = ' '.join('%.1f,%.1f' % (x, y) for x, y in s['pts'])
        att = 'fill="rgb(%d,%d,%d)"' % s['c']
        if s['a'] < 255:
            att += ' fill-opacity="%.3f"' % (s['a'] / 255.0)
        o.append('<polygon points="%s" %s/>' % (p, att))
    o.append('</svg>')
    with open(path, 'w') as f:
        f.write('\n'.join(o))

# ---------------------------------------------------------------- main
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    T_STILL = 2.55
    if cmd in ('svg', 'still', 'all'):
        os.makedirs('output', exist_ok=True)
        emit_svg(build(T_STILL), 'output/awkward-robot-family-portrait.svg')
        print('svg ok')
    if cmd in ('png', 'still', 'all'):
        os.makedirs('output', exist_ok=True)
        render_png(build(T_STILL), 'output/awkward-robot-family-portrait.png', W, H)
        print('png ok')
    if cmd in ('preview',):
        render_png(build(T_STILL), 'preview.png', 800, 600)
        print('preview ok')
    if cmd in ('frames', 'all'):
        os.makedirs('tmp/frames', exist_ok=True)
        vw, vh = 640, 480
        n = int(DUR * FPS)
        for i in range(n):
            render_png(build(i / FPS), 'tmp/frames/f%04d.png' % i, vw, vh)
            if i % 12 == 0: print('frame', i, '/', n, flush=True)
        print('frames ok')
