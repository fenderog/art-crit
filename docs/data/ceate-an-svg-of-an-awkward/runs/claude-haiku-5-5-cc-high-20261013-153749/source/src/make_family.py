#!/usr/bin/env python3
"""Draw an awkward family portrait of robots as a text-free SVG.

Run from anywhere:  python3 -I src/make_family.py
Writes ../output/awkward_robot_family.svg relative to this script.
"""
import math
from pathlib import Path

W, H = 1200, 800
INK = "#2a2633"
OUT = Path(__file__).resolve().parent.parent / "output" / "awkward_robot_family.svg"


# ---------- tiny SVG helpers ----------

def el(tag, **attrs):
    body = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f"<{tag} {body}/>"


def g(items, transform=None):
    attr = f' transform="{transform}"' if transform else ""
    return f"<g{attr}>" + "".join(items) + "</g>"


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=3):
    return el("rect", x=x, y=y, width=w, height=h, rx=rx, fill=fill,
              stroke=stroke or "none", stroke_width=sw)


def circ(cx, cy, r, fill, stroke=None, sw=3):
    return el("circle", cx=cx, cy=cy, r=r, fill=fill,
              stroke=stroke or "none", stroke_width=sw)


def ell(cx, cy, rx, ry, fill, stroke=None, sw=3, **extra):
    return el("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, fill=fill,
              stroke=stroke or "none", stroke_width=sw, **extra)


def poly(pts, width, color):
    """A stroked limb: round caps and joints make a clean elbow."""
    return el("polyline", points=" ".join(f"{x},{y}" for x, y in pts), fill="none",
              stroke=color, stroke_width=width, stroke_linecap="round", stroke_linejoin="round")


def path(d, stroke=INK, width=4, fill="none"):
    return el("path", d=d, fill=fill, stroke=stroke, stroke_width=width,
              stroke_linecap="round", stroke_linejoin="round")


def shape(points, fill, stroke=INK, sw=2):
    return el("polygon", points=points, fill=fill, stroke=stroke, stroke_width=sw,
              stroke_linejoin="round")


def star(cx, cy, big, small, n=5):
    pts = []
    for i in range(2 * n):
        ang = -math.pi / 2 + i * math.pi / n
        rad = big if i % 2 == 0 else small
        pts.append(f"{cx + rad * math.cos(ang):.1f},{cy + rad * math.sin(ang):.1f}")
    return " ".join(pts)


def eye(cx, cy, r, pdx=0, pdy=0, pr=None):
    """White eye with a pupil nudged by (pdx, pdy) to suggest where it looks."""
    pr = pr or r * 0.45
    return circ(cx, cy, r, "#fff", INK, 2) + circ(cx + pdx, cy + pdy, pr, INK)


def lid(cx, cy, r, face):
    """Heavy eyelid: paints over the top of an eye, leaving a smug half-moon."""
    y_line = cy - 0.2 * r
    return (rect(cx - r - 2, cy - r - 2, 2 * r + 4, r * 0.8 + 2, face)
            + poly([(cx - r, y_line), (cx + r, y_line)], 3, INK))


# ---------- the family ----------

def dad():
    """Proud, stiff, hands on hips, one antenna bent from overconfidence."""
    b, d, face = "#4a6fa5", "#2f4a73", "#d6e4ef"
    legs = [poly([(400, 480), (396, 600), (396, 706)], 34, d),
            poly([(440, 480), (444, 600), (444, 706)], 34, d),
            ell(396, 710, 28, 12, INK), ell(444, 710, 28, 12, INK)]
    torso = [rect(345, 300, 150, 190, b, 30, INK),
             rect(380, 330, 80, 56, d, 10),
             circ(396, 350, 5, "#9be7a0"), circ(420, 350, 5, "#f2c14e"),
             circ(444, 350, 5, "#e4572e"),
             shape(star(420, 420, 17, 7), "#f2c14e")]
    neck = [rect(396, 280, 48, 28, d)]
    antennae = [poly([(400, 164), (392, 118)], 5, d), circ(392, 112, 7, "#e4572e", INK, 2),
                poly([(440, 164), (452, 130), (436, 106)], 5, d), circ(436, 102, 7, "#e4572e", INK, 2)]
    head = [rect(350, 160, 140, 122, b, 28, INK), rect(368, 188, 104, 86, face, 18),
            eye(393, 226, 13, 2, 2), eye(447, 226, 13, 2, 2),
            lid(393, 226, 13, face), lid(447, 226, 13, face),
            path("M390 256 Q420 278 450 256"), rect(412, 262, 14, 9, "#fff", 2, INK, 1.5)]
    arms = [poly([(355, 318), (318, 384), (368, 436)], 20, d), circ(368, 436, 13, d),
            poly([(485, 318), (522, 384), (468, 436)], 20, d), circ(468, 436, 13, d)]
    return g(legs + torso + neck + antennae + head + arms)


def mom():
    """Rigid posture, forced grin, eyes sliding off-frame. Her hand hovers above Dad."""
    b, d, face, bow = "#c96a8a", "#9c4468", "#f6dbe4", "#7a2044"
    legs = [poly([(620, 480), (614, 600), (614, 706)], 30, d),
            poly([(660, 480), (666, 600), (666, 706)], 30, d),
            ell(614, 712, 24, 11, INK), ell(666, 712, 24, 11, INK)]
    torso = [rect(592, 262, 96, 218, b, 40, INK), rect(620, 236, 40, 30, d)]
    head = [rect(577, 116, 126, 124, b, 52, INK), rect(592, 144, 96, 84, face, 40),
            shape("640,128 612,110 612,146", bow), shape("640,128 668,110 668,146", bow),
            circ(640, 128, 6, bow, INK, 2),
            eye(618, 176, 14, 9, 0, 6), eye(662, 176, 14, 9, 0, 6),
            path("M606 204 Q640 246 674 204 Z", INK, 3, "#4a1a2e"),
            rect(616, 206, 48, 8, "#fff", 3)]
    arms = [poly([(598, 280), (548, 300), (506, 290)], 18, d), circ(506, 290, 12, d),
            poly([(682, 280), (700, 360), (694, 440)], 18, d), circ(694, 440, 12, d)]
    return g(legs + torso + arms[:2] + head + arms[2:])


def teen():
    """Slouched, headphones on, bored eyes, hands shoved in the hoodie pocket."""
    b, d, face, acc = "#6c6f7d", "#4d505c", "#c9cdd9", "#e4572e"
    body = [poly([(808, 480), (812, 600), (806, 706)], 30, d),
            poly([(842, 480), (862, 590), (838, 700)], 30, d),
            ell(806, 712, 24, 11, INK), ell(838, 706, 24, 11, INK),
            rect(780, 318, 130, 170, b, 24, INK),
            rect(800, 422, 90, 38, d, 10),
            rect(806, 296, 34, 28, d),
            poly([(790, 336), (776, 400), (806, 436)], 18, d), circ(806, 436, 12, d),
            poly([(902, 336), (908, 400), (856, 432)], 18, d), circ(856, 432, 12, d)]
    head = [poly([(800, 192), (790, 160), (768, 156)], 5, d), circ(766, 156, 6, acc, INK, 2),
            rect(762, 190, 124, 112, b, 30, INK), rect(776, 212, 96, 72, face, 22),
            path("M756 240 Q756 166 824 166 Q892 166 892 240", INK, 9),
            rect(746, 222, 22, 44, acc, 9, INK, 2), rect(880, 222, 22, 44, acc, 9, INK, 2),
            poly([(788, 246), (814, 246)], 4, INK),
            path("M838 250 Q852 236 866 250", INK, 4),
            poly([(814, 276), (846, 268)], 4, INK)]
    return g(body + [g(head, "rotate(-14 824 246)")], "rotate(9 820 480)")


def grandbot():
    """Seated, cane in hand, one eye shut, monocle on the other. Reaches down to hold the kid's hand."""
    b, d, face, wood = "#b07a45", "#7d5230", "#f0d7aa", "#8e5a34"
    chair = [rect(150, 430, 176, 160, "#7a4a2a", 34, INK),
             rect(156, 626, 14, 86, d), rect(300, 626, 14, 86, d),
             rect(136, 588, 214, 40, wood, 14, INK)]
    lower = [poly([(226, 570), (322, 570)], 30, d),
             poly([(322, 570), (326, 706)], 28, d), ell(330, 712, 26, 11, INK)]
    torso = [rect(190, 400, 110, 176, b, 26, INK),
             circ(210, 430, 3, d), circ(280, 430, 3, d), circ(245, 470, 3, d),
             rect(228, 370, 34, 30, d)]
    head = [poly([(206, 272), (198, 244), (212, 230)], 5, d), circ(212, 228, 6, "#c2432b", INK, 2),
            rect(190, 270, 112, 110, b, 26, INK), rect(204, 296, 84, 70, face, 16),
            path("M216 326 Q226 336 236 326"),
            circ(268, 322, 14, "#fff", INK, 4), circ(271, 325, 5, INK),
            path("M280 334 Q292 350 286 368", "#c9a24a", 3),
            path("M218 352 Q244 360 272 344")]
    arms = [poly([(292, 420), (356, 486), (422, 566)], 20, b), circ(424, 568, 13, d),
            poly([(198, 420), (180, 488), (184, 520)], 20, b), circ(184, 520, 13, d)]
    cane = [poly([(186, 708), (184, 520), (184, 500), (196, 490)], 8, "#4e3420")]
    return g(chair + lower + torso + [g(head, "rotate(-10 246 325)")] + arms + cane)


def kid():
    """Tiny, front and center: one huge eye, one tiny eye, a propeller, a balloon, and a lifted foot."""
    b, d, face, acc = "#f2c94c", "#c9a02a", "#fff3c4", "#e4572e"
    legs = [poly([(490, 650), (486, 706)], 22, d), poly([(530, 650), (552, 690)], 22, d),
            ell(486, 710, 18, 8, INK), ell(560, 694, 16, 8, INK)]
    torso = [rect(470, 574, 82, 86, b, 22, INK)]
    prop = [poly([(511, 470), (511, 452)], 5, d),
            el("ellipse", cx=511, cy=450, rx=24, ry=5, fill=acc, stroke=INK,
               stroke_width=2, transform="rotate(-14 511 450)")]
    head = [rect(455, 470, 112, 104, b, 34, INK), rect(468, 490, 86, 70, face, 24),
            eye(494, 522, 14, 4, -1, 7), eye(530, 526, 7, 2, 1, 3.5),
            el("ellipse", cx=512, cy=548, rx=8, ry=10, fill="#7a2e12", stroke=INK, stroke_width=2)]
    arms = [poly([(474, 596), (446, 584), (426, 570)], 20, b), circ(426, 570, 13, b, INK, 2),
            poly([(548, 596), (578, 548), (598, 500)], 20, b), circ(598, 500, 13, b, INK, 2)]
    balloon = [poly([(598, 500), (626, 452)], 2, INK),
               ell(628, 420, 24, 30, acc, INK, 2)]
    return g(legs + torso + prop + head + arms + balloon)


def pet():
    """Dog-shaped helper bot, looking at Teen, tail antenna up, no interest in the photo."""
    b, d, acc = "#6ea37a", "#4f7d5b", "#e4572e"
    legs = [poly([(966, 664), (966, 706)], 14, d), poly([(986, 664), (986, 706)], 14, d),
            poly([(1038, 664), (1038, 706)], 14, d), poly([(1056, 664), (1056, 706)], 14, d)]
    body = [rect(950, 600, 120, 70, b, 30, INK)]
    head = [rect(880, 560, 80, 62, b, 26, INK), rect(858, 586, 40, 26, d, 12, INK),
            ell(900, 616, 10, 20, d, INK, 2), eye(918, 580, 9, -3, 0, 4.5)]
    tail = [path("M1066 612 Q1096 592 1090 548", INK, 10), path("M1066 612 Q1096 592 1090 548", d, 6),
            circ(1090, 544, 7, acc, INK, 2)]
    return g(legs + body + head + tail)


def scene():
    parts = []
    # wall, wallpaper dots, and a soft studio spotlight
    parts.append(rect(0, 0, W, 640, "url(#wall)"))
    parts.append(rect(0, 0, W, 640, "url(#dots)"))
    parts.append(el("ellipse", cx=600, cy=200, rx=620, ry=400, fill="url(#spot)"))

    # two crooked framed pictures and a potted plant
    parts.append(g([rect(70, 90, 170, 130, "#faf3e0", 6, "#7a5230", 12),
                    circ(120, 150, 16, "#f2c94c"),
                    shape("88,215 150,160 210,215", "#8fb3a0", "none", 0)],
                   "rotate(-6 155 155)"))
    parts.append(g([rect(930, 70, 150, 110, "#faf3e0", 6, "#7a5230", 12),
                    circ(1005, 125, 22, "none", "#4a6fa5", 8),
                    circ(1005, 125, 8, "#c96a8a")],
                   "rotate(5 1005 125)"))
    parts.append(g([ell(1130, 560, 12, 44, "#5f8f4e", INK, 2, transform="rotate(-22 1130 560)"),
                    ell(1152, 548, 12, 50, "#5f8f4e", INK, 2),
                    ell(1174, 562, 12, 44, "#5f8f4e", INK, 2, transform="rotate(22 1174 562)"),
                    shape("1120,610 1184,610 1174,664 1130,664", "#b5562f")]))

    # floor, baseboard, rug
    parts.append(rect(0, 626, W, 14, "#faf6ec"))
    parts.append(rect(0, 640, W, 160, "#b98b5e"))
    parts.append(el("line", x1=0, y1=664, x2=W, y2=664, stroke="#9c6f45", stroke_width=2))
    parts.append(ell(600, 700, 500, 44, "#4f7d7a"))
    parts.append(ell(600, 700, 440, 34, "none", "#e8c27a", 6))

    # shadows under everyone, drawn before anyone stands in them
    for cx, rx in [(420, 100), (640, 86), (826, 86), (240, 120), (511, 56), (1010, 120)]:
        parts.append(ell(cx, 716, rx, 12, "#000", opacity=0.18))

    # back row to front: Teen and Pet are the outliers, Kid and Grandbot are the closest
    parts.append(mom())
    parts.append(dad())
    parts.append(teen())
    parts.append(pet())
    parts.append(grandbot())
    parts.append(kid())
    return parts


def build():
    defs = (
        '<defs>'
        '<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#efe4cf"/><stop offset="1" stop-color="#dcc8a6"/>'
        '</linearGradient>'
        '<radialGradient id="spot">'
        '<stop offset="0" stop-color="#fffdf5" stop-opacity="0.45"/>'
        '<stop offset="1" stop-color="#fffdf5" stop-opacity="0"/>'
        '</radialGradient>'
        '<pattern id="dots" width="40" height="40" patternUnits="userSpaceOnUse">'
        '<circle cx="20" cy="20" r="3" fill="#d5bf98"/>'
        '</pattern>'
        '</defs>'
    )
    body = "".join(scene())
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">' + defs + body + "</svg>\n"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}")
