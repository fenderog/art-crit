#!/usr/bin/env python3
"""Generates the awkward robot family portrait as a single SVG (no text)."""
import math
import os
import sys

W, H = 1200, 800
OUT = "#2b2233"          # outline ink
defs, body = [], []
_gid = [0]


def shade(hexc, f):
    hexc = hexc.lstrip("#")
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    if f >= 0:
        r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    else:
        r, g, b = (int(c * (1 + f)) for c in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


def grad(color, horizontal=True):
    """Soft cylindrical shading gradient; returns url(#id)."""
    _gid[0] += 1
    gid = f"g{_gid[0]}"
    x2, y2 = ("1", "0") if horizontal else ("0", "1")
    defs.append(
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
        f'<stop offset="0" stop-color="{shade(color, .28)}"/>'
        f'<stop offset=".45" stop-color="{color}"/>'
        f'<stop offset="1" stop-color="{shade(color, -.28)}"/></linearGradient>')
    return f"url(#{gid})"


def add(s):
    body.append(s)


def rr(x, y, w, h, r, fill, sw=4, stroke=OUT, extra=""):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def ell(cx, cy, rx, ry, fill, sw=4, stroke=OUT, extra=""):
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def path(d, fill="none", sw=4, stroke=OUT, extra=""):
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def limb(d, color, w=24):
    """Tube-like arm/leg: dark outline stroke, colour stroke, highlight."""
    path(d, sw=w + 8, stroke=OUT)
    path(d, sw=w, stroke=color)
    path(d, sw=max(3, w // 4), stroke=shade(color, .35), extra='opacity=".55" transform="translate(-3,-3)"')


def hand(cx, cy, r, color):
    ell(cx, cy, r, r * .9, color, 4)


def bolt(cx, cy, r=5, color="#cfd3d8"):
    ell(cx, cy, r, r, color, 2)
    path(f"M{cx - r * .6} {cy} L{cx + r * .6} {cy}", sw=1.6)


def eye(cx, cy, r, px=0, py=0, pr=None, lid=0, lidc="#6b6f78", fill="#fffdf4"):
    """Round eye with pupil offset; lid = fraction of eye covered from the top."""
    pr = pr or r * .45
    cid = f"c{cx}_{cy}_{int(r)}"
    defs.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    ell(cx, cy, r, r, fill, 3.5)
    add(f'<g clip-path="url(#{cid})"><circle cx="{cx + px}" cy="{cy + py}" r="{pr}" fill="{OUT}"/>'
        f'<circle cx="{cx + px - pr * .3}" cy="{cy + py - pr * .3}" r="{pr * .28}" fill="#fff"/>'
        + (f'<rect x="{cx - r - 2}" y="{cy - r - 2}" width="{2 * r + 4}" height="{2 * r * lid + 2}" fill="{lidc}"/>' if lid else "")
        + '</g>')
    if lid:
        add(f'<line x1="{cx - r}" y1="{cy - r + 2 * r * lid + 1}" x2="{cx + r}" y2="{cy - r + 2 * r * lid + 1}" '
            f'stroke="{OUT}" stroke-width="3"/>')


# ---------------------------------------------------------------- backdrop
def backdrop():
    defs.append('<pattern id="stripes" width="64" height="10" patternUnits="userSpaceOnUse">'
                '<rect width="64" height="10" fill="#6d9a96"/><rect width="30" height="10" fill="#79a7a2"/>'
                '<circle cx="47" cy="5" r="3" fill="#8bb5ae" opacity=".7"/></pattern>')
    defs.append('<radialGradient id="spot" cx=".5" cy=".42" r=".75">'
                '<stop offset="0" stop-color="#fff6d0" stop-opacity=".4"/>'
                '<stop offset=".6" stop-color="#fff6d0" stop-opacity="0"/>'
                '<stop offset="1" stop-color="#1a1020" stop-opacity=".55"/></radialGradient>')
    defs.append('<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#8a5b3c"/><stop offset="1" stop-color="#5a3a2a"/></linearGradient>')
    defs.append('<filter id="soft" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="9"/></filter>')
    defs.append('<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.2"/></filter>')
    add(f'<rect width="{W}" height="{H}" fill="url(#stripes)"/>')
    # wainscot + baseboard
    add('<rect y="470" width="1200" height="160" fill="#4e7773"/>')
    for x in range(0, 1200, 80):
        add(f'<rect x="{x + 10}" y="490" width="60" height="110" rx="4" fill="none" stroke="#3d615e" stroke-width="3"/>')
    add('<rect y="466" width="1200" height="10" fill="#d9c9a3"/><rect y="620" width="1200" height="16" fill="#d9c9a3"/>')
    # floor
    add('<rect y="636" width="1200" height="170" fill="url(#floor)"/>')
    for y in [668, 704, 748, 800]:
        add(f'<line x1="0" y1="{y}" x2="1200" y2="{y}" stroke="#4a2e20" stroke-width="2.5" opacity=".6"/>')
    for x0 in range(-200, 1400, 150):
        add(f'<line x1="{x0 + 40}" y1="636" x2="{x0 - 20 + (x0 - 600) * .25}" y2="800" stroke="#4a2e20" stroke-width="2" opacity=".35"/>')
    # rug
    ell(600, 725, 470, 58, "#7c2f3e", 0, extra='opacity=".9"')
    ell(600, 725, 440, 48, "none", 4, "#e9c46a", extra='opacity=".8" stroke-dasharray="14 10"')
    # crooked wall frame with an ancestor toaster
    add('<g transform="rotate(-5 600 120)">')
    rr(535, 52, 130, 100, 6, "#caa45a", 6)
    rr(547, 64, 106, 76, 3, "#e8dcc0", 3)
    rr(570, 90, 60, 38, 8, "#b9bcc2", 3)
    rr(580, 82, 14, 12, 2, "#8b8f96", 2.5)
    rr(606, 82, 14, 12, 2, "#8b8f96", 2.5)
    eye(587, 106, 6, 1, 1)
    eye(613, 106, 6, 1, 1)
    path("M591 118 Q600 123 609 118", sw=2.5)
    add('</g>')
    # wall clock, wrong and sulky
    ell(300, 105, 34, 34, "#f1e8d0", 5)
    path("M300 105 L300 84", sw=4)
    path("M300 105 L318 112", sw=4)
    for a in range(12):
        x1 = 300 + 27 * math.sin(a * math.pi / 6)
        y1 = 105 - 27 * math.cos(a * math.pi / 6)
        add(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="2" fill="{OUT}"/>')
    # potted plant
    path("M958 402 Q950 340 930 320 M958 402 Q962 330 985 300 M958 402 Q990 360 1020 350", sw=6, stroke="#3e7a4a")
    ell(930, 320, 18, 11, "#4f9a5c", 3, extra='transform="rotate(-30 930 320)"')
    ell(985, 298, 18, 11, "#4f9a5c", 3, extra='transform="rotate(50 985 298)"')
    ell(1022, 350, 18, 11, "#4f9a5c", 3, extra='transform="rotate(20 1022 350)"')
    rr(930, 400, 56, 66, 8, "#b5654a", 4)
    # curtains
    defs.append('<linearGradient id="curt" x1="0" y1="0" x2="1" y2="0">'
                '<stop offset="0" stop-color="#4a1424"/><stop offset=".25" stop-color="#8a2a42"/>'
                '<stop offset=".5" stop-color="#5a1a2d"/><stop offset=".75" stop-color="#8f2d46"/>'
                '<stop offset="1" stop-color="#4a1424"/></linearGradient>')
    add('<path d="M0 0 H150 Q130 100 160 250 Q120 420 150 800 H0Z" fill="url(#curt)" stroke="#2b1020" stroke-width="4"/>')
    add('<path d="M1200 0 H1055 Q1085 120 1050 280 Q1085 460 1060 800 H1200Z" fill="url(#curt)" stroke="#2b1020" stroke-width="4"/>')
    add('<rect x="0" y="0" width="1200" height="26" fill="#3a1220"/>')
    for x in range(20, 1200, 60):
        add(f'<circle cx="{x}" cy="13" r="6" fill="#e9c46a" stroke="{OUT}" stroke-width="2"/>')


def floor_shadow(cx, cy, rx, ry=14):
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#1a0f14" opacity=".45" filter="url(#soft)"/>')


# ---------------------------------------------------------------- Dad
def dad_body():
    C = "#5b86b3"
    floor_shadow(400, 652, 110)
    # legs
    rr(346, 540, 44, 108, 8, grad(shade(C, -.2)))
    rr(410, 540, 44, 108, 8, grad(shade(C, -.2)))
    rr(332, 634, 66, 22, 9, "#2f3e55")
    rr(402, 634, 66, 22, 9, "#2f3e55")
    # torso
    rr(318, 326, 164, 232, 20, grad(C))
    rr(340, 358, 120, 78, 8, shade(C, -.35), 3)
    for i, c in enumerate(["#e9c46a", "#7bd389", "#e76f51"]):
        ell(366 + i * 34, 380, 9, 9, c, 3)
    for k in range(4):
        add(f'<rect x="{352 + k * 24}" y="404" width="14" height="22" rx="3" fill="#cfe0ee" stroke="{OUT}" stroke-width="2.5"/>')
    # tie
    path("M386 440 L414 440 L426 470 L400 545 L374 470Z", "#c0392b", 4)
    path("M386 440 L414 440 L408 452 L392 452Z", "#8f2a20", 3)
    # neck + head
    rr(380, 302, 40, 30, 4, "#8a97a8", 4)
    add('<g transform="rotate(-2 400 235)">')
    path("M400 172 L400 140", sw=5)
    path("M400 140 L412 124", sw=5)           # bent antenna
    ell(414, 120, 7, 7, "#e76f51", 3)
    rr(338, 170, 124, 138, 16, grad(C))
    rr(352, 190, 96, 98, 10, "#16202e", 3.5)    # face screen
    # eyes: wide, fixed on camera
    for ex in (378, 422):
        eye(ex, 226, 15, 0, 0, 5.5)
    path("M360 202 L394 205 M440 202 L406 205", sw=5)     # level, serious brows
    # rigid teeth grin
    rr(366, 256, 68, 24, 5, "#fffdf4", 3.5)
    for k in range(1, 6):
        add(f'<line x1="{366 + k * 11.3}" y1="257" x2="{366 + k * 11.3}" y2="279" stroke="{OUT}" stroke-width="2.5"/>')
    add(f'<line x1="367" y1="268" x2="433" y2="268" stroke="{OUT}" stroke-width="2.5"/>')
    bolt(346, 182)
    bolt(454, 182)
    bolt(346, 296)
    bolt(454, 296)
    # nervous oil drop
    path("M470 214 Q480 232 470 240 Q460 232 470 214Z", "#e9c46a", 2.5)
    add('</g>')


def dad_arms(kid_head_xy):
    C = "#5b86b3"
    # right arm (viewer's right) rests on the grandma's chair, stiff 90-degree
    limb("M470 352 L520 400 L512 452", shade(C, -.05), 26)
    hand(512, 456, 15, "#e8ecef")
    # left arm pushes the kid's head down
    kx, ky = kid_head_xy
    limb(f"M330 352 L262 420 L{kx - 8} {ky - 36}", shade(C, -.05), 26)
    hand(kx - 6, ky - 26, 18, "#e8ecef")
    for k in range(3):
        add(f'<line x1="{kx - 14 + k * 8}" y1="{ky - 24}" x2="{kx - 14 + k * 8}" y2="{ky - 12}" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>')


# ---------------------------------------------------------------- Mom
def mom_body():
    C = "#e07a8a"
    floor_shadow(800, 652, 100)
    # legs
    rr(774, 560, 18, 88, 6, "#c9ced6")
    rr(808, 560, 18, 88, 6, "#c9ced6")
    rr(762, 640, 40, 16, 8, "#7a2c3e")
    rr(800, 640, 40, 16, 8, "#7a2c3e")
    # dress
    path("M762 330 Q800 316 838 330 L880 566 Q800 584 720 566Z", grad(C), 4)
    path("M740 480 Q800 500 860 480", sw=3, stroke=shade(C, -.3))
    path("M744 520 Q800 540 856 520", sw=3, stroke=shade(C, -.3))
    # neck
    rr(789, 296, 22, 36, 4, "#9aa3b0", 3.5)
    # pearls
    for k in range(9):
        t = k / 8
        ell(768 + 64 * t, 336 + 24 * (1 - (2 * t - 1) ** 2), 6, 6, "#fbf5ea", 2.5)
    # head, tilted toward the teen
    add('<g transform="rotate(7 800 245)">')
    path("M786 192 C760 150 740 160 755 120 M814 192 C840 150 860 160 845 120", sw=5)
    ell(755, 118, 8, 8, "#fbd46a", 3)
    ell(845, 118, 8, 8, "#fbd46a", 3)
    rr(738, 186, 124, 118, 50, grad(C))
    rr(752, 204, 96, 84, 34, "#2a1c26", 3.5)
    # eyes: one on camera, one sliding sideways toward the teen
    eye(779, 238, 14, 2, 0, 5.5, lid=0.18, lidc="#2a1c26")
    eye(821, 238, 14, 8, 1, 5.5, lid=0.18, lidc="#2a1c26")
    path("M762 222 L768 226 M772 216 L776 222 M838 222 L832 226 M828 216 L824 222", sw=3, stroke="#fbf5ea")
    # tight, quivering smile
    path("M776 268 Q790 280 800 276 Q812 280 826 266 L832 262", sw=4.5, stroke="#fbf5ea")
    ell(756, 262, 7, 4, "#f4a6b4", 0, extra='opacity=".7"')
    ell(845, 262, 7, 4, "#f4a6b4", 0, extra='opacity=".7"')
    add('</g>')


def mom_arms(teen_shoulder):
    C = "#e07a8a"
    # left arm: hand on grandma's chair
    limb("M766 350 L722 410 L702 452", shade(C, .05), 22)
    hand(700, 456, 14, "#f5e6ea")
    # right arm reaches over to the teen's shoulder
    tx, ty = teen_shoulder
    limb(f"M836 350 L900 398 L{tx - 12} {ty - 6}", shade(C, .05), 22)
    ell(tx, ty - 4, 17, 14, "#f5e6ea", 4)
    for k in range(3):
        add(f'<line x1="{tx - 6 + k * 7}" y1="{ty - 2}" x2="{tx - 6 + k * 7}" y2="{ty + 8}" stroke="{OUT}" stroke-width="2.5" stroke-linecap="round"/>')


# ---------------------------------------------------------------- Armchair + Grandma
def chair_and_grandma():
    UPH = "#9c4a3b"
    floor_shadow(600, 652, 150)
    # chair back
    path("M492 640 L492 410 Q492 330 560 326 L640 326 Q708 330 708 410 L708 640Z", grad(UPH), 5)
    for (x, y) in [(560, 372), (600, 356), (640, 372), (530, 430), (670, 430)]:
        ell(x, y, 8, 8, shade(UPH, -.35), 0, extra='opacity=".6"')
        path(f"M{x - 6} {y} Q{x} {y - 8} {x + 6} {y}", sw=1.8, stroke="#e9c46a")
    # chair legs
    rr(500, 630, 18, 26, 4, "#4a2a1c")
    rr(682, 630, 18, 26, 4, "#4a2a1c")

    G = "#d9a441"
    # Grandma body
    path("M550 508 Q552 440 600 430 Q648 440 650 508 L668 600 L532 600Z", grad(G), 4)
    # doily collar
    path("M562 446 Q600 478 638 446 Q630 436 600 432 Q570 436 562 446Z", "#fbf5ea", 3)
    # neck
    rr(584, 408, 32, 22, 4, "#9aa3b0", 3.5)
    add('<g transform="rotate(-10 600 395)">')   # head lolling to the side
    # spring bun
    path("M590 336 C575 320 600 312 600 326 C600 338 585 336 590 326 C595 312 618 320 610 334", sw=5)
    ell(600, 327, 17, 11, "#cbd0d8", 4)
    rr(544, 340, 112, 96, 46, grad("#b7b0a0"))
    rr(556, 360, 88, 62, 24, "#2a2430", 3.5)
    # round spectacles over closed eyes
    for ex in (580, 620):
        ell(ex, 390, 16, 16, "#bfe3e8", 3.5, extra='fill-opacity=".35"')
        path(f"M{ex - 10} 392 Q{ex} 400 {ex + 10} 392", sw=3.5, stroke="#fbf5ea")
    path("M596 388 Q600 384 604 388", sw=3.5)
    path("M564 384 L556 378 M636 384 L644 378", sw=3)
    # slack open mouth + dangling cog
    ell(600, 414, 9, 6, "#0d0a10", 2.5)
    path("M606 418 L606 436", sw=2.5, stroke="#cfd3d8")
    ell(606, 442, 7, 7, "#cfd3d8", 2.5)
    add('</g>')
    # sleep bubbles
    ell(660, 338, 6, 6, "#fffdf4", 2.5, extra='opacity=".9"')
    ell(678, 316, 10, 10, "#fffdf4", 2.5, extra='opacity=".9"')
    ell(708, 280, 26, 22, "#fffdf4", 3, extra='opacity=".92"')
    bolt(708, 282, 8, "#e9c46a")
    # lap + knitting
    path("M526 530 Q600 505 674 530 L690 600 Q600 620 510 600Z", grad("#b78a2f"), 4)
    ell(590, 548, 24, 24, "#e76f51", 4)
    path("M572 540 Q590 530 608 540 M568 552 Q590 542 612 554 M574 564 Q590 556 606 564", sw=2.5, stroke="#8f2a20")
    path("M620 526 L668 480", sw=4, stroke="#e8ecef")
    path("M630 540 L690 490", sw=4, stroke="#e8ecef")
    # arms sag onto the lap
    limb("M556 478 Q532 520 556 548", G, 22)
    hand(560, 552, 13, "#d8d2c0")
    limb("M644 478 Q668 520 648 546", G, 22)
    hand(644, 550, 13, "#d8d2c0")
    # chair arm rests (front)
    rr(478, 470, 40, 150, 18, grad(UPH), 5)
    rr(682, 470, 40, 150, 18, grad(UPH), 5)
    rr(472, 462, 52, 24, 12, shade(UPH, .15), 4)
    rr(676, 462, 52, 24, 12, shade(UPH, .15), 4)
    # seat front + feet
    rr(500, 596, 200, 44, 12, grad(shade(UPH, -.1), False), 5)
    rr(560, 640, 36, 14, 6, "#4a3a35")
    rr(606, 640, 36, 14, 6, "#4a3a35")


# ---------------------------------------------------------------- Teen
def teen():
    C = "#6d4ea8"
    floor_shadow(1000, 686, 90)
    add('<g transform="rotate(9 1000 680)">')
    # long legs
    rr(966, 520, 30, 160, 8, "#2f2a42")
    rr(1004, 520, 30, 160, 8, "#2f2a42")
    rr(948, 666, 52, 20, 10, "#e8ecef")
    rr(1002, 666, 52, 20, 10, "#e8ecef")
    # hoodie torso
    path("M948 362 Q1000 340 1052 362 L1060 548 Q1000 566 940 548Z", grad(C), 4)
    path("M974 528 Q1000 540 1026 528 L1030 560 Q1000 570 970 560Z", shade(C, -.2), 3)   # pocket
    path("M984 362 L990 420 M1016 362 L1010 420", sw=3.5, stroke="#e8ecef")             # hood strings
    ell(990, 424, 4, 4, "#e8ecef", 2)
    ell(1010, 424, 4, 4, "#e8ecef", 2)
    # neck + slouched head pushed forward
    add('<g transform="rotate(14 1000 330)">')
    rr(988, 318, 24, 30, 4, "#7f8794", 3.5)
    path("M934 292 C930 220 970 200 1004 200 C1046 200 1074 230 1068 292 C1060 322 1030 330 1000 330 C966 330 940 320 934 292Z", grad(shade(C, -.1)), 4)
    rr(954, 236, 108, 80, 30, "#14161f", 3.5)
    # half-lidded eyes rolling up
    for ex in (982, 1030):
        ell(ex, 274, 16, 13, "#fffdf4", 3)
        add(f'<circle cx="{ex + 3}" cy="266" r="5.5" fill="{OUT}"/>')
        add(f'<path d="M{ex - 18} 276 L{ex - 18} 256 L{ex + 18} 256 L{ex + 18} 270 Z" fill="#14161f"/>')
        path(f"M{ex - 18} 276 L{ex + 18} 270", sw=4.5)
    path("M964 238 L996 246 M1048 246 L1018 244", sw=4, stroke="#7de0b6")
    path("M994 304 L1024 302", sw=4.5, stroke="#7de0b6")
    # headphones
    path("M930 280 C920 190 1070 170 1070 280", sw=9, stroke=OUT)
    path("M930 280 C920 190 1070 170 1070 280", sw=5, stroke="#7de0b6")
    rr(920, 262, 24, 50, 10, "#7de0b6", 4)
    rr(1056, 262, 24, 50, 10, "#7de0b6", 4)
    add('</g>')
    # arms crossed
    limb("M956 392 Q980 470 1050 450", C, 24)
    limb("M1046 392 Q1030 470 950 452", shade(C, .06), 24)
    hand(1052, 450, 12, "#d6d0e8")
    hand(948, 452, 12, "#d6d0e8")
    add('</g>')


# ---------------------------------------------------------------- Kid
def kid():
    C = "#f2a03d"
    cx = 330
    floor_shadow(cx, 742, 74)
    # spring legs
    for lx in (cx - 22, cx + 22):
        sp = f"M{lx} 672 q-12 6 0 12 q12 6 0 12 q-12 6 0 12 q12 6 0 10"
        path(sp, sw=7, stroke=OUT)
        path(sp, sw=3, stroke="#cfd3d8")
        rr(lx - 20, 716, 40, 22, 10, "#e63946")
    # body
    rr(cx - 46, 600, 92, 80, 34, grad(C), 4)
    ell(cx, 640, 18, 18, "#fff3c4", 3.5)
    path(f"M{cx - 10} 640 L{cx + 2} 630 L{cx + 2} 650Z", "#e63946", 2.5)
    # waving arm (right) with motion marks
    limb(f"M{cx + 44} 620 Q{cx + 90} 590 {cx + 96} 540", C, 18)
    hand(cx + 98, 534, 14, "#fff3c4")
    path(f"M{cx + 126} 520 q8 10 2 22 M{cx + 136} 506 q12 14 4 32", sw=3, stroke="#fff6d0", extra='opacity=".8"')
    # balloon arm (left), balloon bobbing off to the side clear of Dad
    limb(f"M{cx - 44} 620 Q{cx - 90} 600 {cx - 100} 540", C, 18)
    hand(cx - 100, 534, 14, "#fff3c4")
    path(f"M{cx - 100} 524 C{cx - 90} 470 {cx - 130} 440 {cx - 112} 404", sw=2.5, stroke="#fbf5ea")
    ell(cx - 112, 350, 42, 52, "#4cc9f0", 4)
    path(f"M{cx - 112} 402 l-7 12 h14z", "#4cc9f0", 3)
    ell(cx - 126, 332, 9, 14, "#fff", 0, extra=f'opacity=".55" transform="rotate(20 {cx - 126} 332)"')
    # squashed head (dad's hand pushes down)
    add(f'<g transform="translate({cx} 575) scale(1.05 .88)">')
    rr(-64, -50, 128, 100, 38, grad(C), 4.5)
    add('</g>')
    ell(cx - 70, 578, 10, 10, "#cfd3d8", 3.5)
    ell(cx + 70, 578, 10, 10, "#cfd3d8", 3.5)
    # face: cross-eyed, mismatched, tongue out
    rr(cx - 50, 552, 100, 56, 22, "#1b1424", 3)
    eye(cx - 22, 574, 15, 6, 2, 6)
    eye(cx + 24, 578, 10, -5, 1, 4.5)
    path(f"M{cx - 20} 598 Q{cx} 610 {cx + 20} 596", sw=4, stroke="#fff3c4")
    rr(cx - 2, 598, 18, 20, 8, "#ff7b9c", 3)
    path(f"M{cx + 7} 600 L{cx + 7} 612", sw=2, stroke="#c0405f")
    # little antenna sprouting from the squashed head
    path(f"M{cx + 28} 528 q10 -14 -2 -24", sw=4)
    ell(cx + 26, 502, 6, 6, "#7bd389", 3)


# ---------------------------------------------------------------- Dog
def dog_figure(dx, op, blur=False):
    C = "#7bd1b5"
    f = ' filter="url(#blur)"' if blur else ""
    add(f'<g transform="translate({dx} 0)" opacity="{op}"{f}>')
    for lx in (800, 830, 904, 934):
        rr(lx - 8, 706, 18, 38, 6, shade(C, -.2), 3.5)
    # tail (spring, mid-wag)
    tail = "M944 690 q22 -12 20 -34 q-2 -14 12 -22"
    path(tail, sw=7, stroke=OUT)
    path(tail, sw=3, stroke="#cfd3d8", extra='stroke-dasharray="5 4"')
    ell(978, 632, 7, 7, "#e63946", 3)
    rr(780, 664, 176, 62, 28, grad(C, False), 4)
    for k in range(3):
        add(f'<line x1="{850 + k * 28}" y1="676" x2="{850 + k * 28}" y2="708" stroke="{OUT}" stroke-width="2.5" opacity=".5"/>')
    # head, turned away from camera, chewing yarn
    rr(740, 654, 70, 62, 22, grad(C), 4)
    path("M772 656 L760 628 L792 648Z", shade(C, -.2), 3.5)
    eye(776, 678, 8, -3, 1, 3.5)
    rr(722, 690, 36, 22, 9, shade(C, -.1), 3.5)
    ell(730, 694, 5, 4, OUT, 0)
    ell(790, 711, 6, 6, "#e63946", 2.5)    # tag
    add('</g>')


def yarn():
    R = "#e76f51"
    path("M590 572 C560 640 520 650 540 690 C560 720 640 700 650 716 "
         "C660 730 700 700 720 716 C735 728 730 704 735 700", sw=3.5, stroke=R)
    path("M545 705 C520 725 470 718 440 700 C420 690 460 676 500 690", sw=3, stroke=R)
    # tangled around the dad's shoes
    path("M345 650 C380 664 420 664 460 652 M350 658 C390 644 430 644 452 660", sw=3, stroke=R)


# ---------------------------------------------------------------- build
def build():
    backdrop()
    dad_body()
    mom_body()
    chair_and_grandma()
    teen()
    mom_arms((982, 388))
    yarn()
    dog_figure(-24, .3, True)
    dog_figure(22, .3, True)
    dog_figure(0, .95)
    kid()
    dad_arms((330, 575))
    add(f'<rect width="{W}" height="{H}" fill="url(#spot)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="An awkward family portrait of robots">'
            f'<defs>{"".join(defs)}</defs>{"".join(body)}</svg>')


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "output/robot_family_portrait.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build())
    print("wrote", out)
