#!/usr/bin/env python3
"""Generate an awkward robot family portrait as a standalone SVG (no text)."""
from pathlib import Path

INK = "#26313a"
S = []  # svg fragments


def add(s):
    S.append(s)


def r(x, y, w, h, fill, rx=8, sw=6, extra=""):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
        f'stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def c(cx, cy, rad, fill, sw=6, extra=""):
    add(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{fill}" '
        f'stroke="{INK}" stroke-width="{sw}" {extra}/>')


def e(cx, cy, rx, ry, fill, extra=""):
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>')


def p(d, fill="none", sw=6, col=None, extra=""):
    col = col or INK
    add(f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def poly(points, fill, sw=6, extra=""):
    add(f'<polygon points="{points}" fill="{fill}" stroke="{INK}" '
        f'stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def rivets(points, rad=4, fill="#d8dee2"):
    for x, y in points:
        add(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')


def claw(x, y, rot=0, col="#c9d2d8"):
    """A simple two-prong claw hand centred on (x, y)."""
    add(f'<g transform="translate({x},{y}) rotate({rot})">')
    c(0, 0, 15, col)
    p("M-13,-6 Q-22,-22 -8,-27", sw=6)
    p("M13,-6 Q22,-22 8,-27", sw=6)
    p("M0,-10 L0,-26", sw=6)
    add('</g>')


# ---------------------------------------------------------------- backdrop
def backdrop():
    add('''<defs>
  <radialGradient id="wall" cx="50%" cy="38%" r="78%">
    <stop offset="0%" stop-color="#b99b7d"/>
    <stop offset="42%" stop-color="#8f6f5c"/>
    <stop offset="74%" stop-color="#5d4a4a"/>
    <stop offset="100%" stop-color="#3c3138"/>
  </radialGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#6b5244"/>
    <stop offset="100%" stop-color="#3f302c"/>
  </linearGradient>
  <radialGradient id="spot" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffe9bd" stop-opacity="0.52"/>
    <stop offset="68%" stop-color="#ffe9bd" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="#ffe9bd" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vig" cx="50%" cy="46%" r="74%">
    <stop offset="64%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#140f12" stop-opacity="0.48"/>
  </radialGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="26"/>
  </filter>
  <filter id="soft2" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
</defs>''')
    add('<rect width="1200" height="900" fill="url(#wall)"/>')
    # mottled studio muslin
    for cx, cy, rx, ry, col, op in [
        (220, 210, 230, 130, "#d8b48e", .20), (980, 180, 260, 140, "#4b6a76", .22),
        (620, 320, 340, 170, "#e2c79e", .16), (130, 520, 200, 150, "#44606c", .18),
        (1080, 500, 210, 160, "#a87d65", .18), (480, 110, 220, 90, "#577b86", .14),
    ]:
        e(cx, cy, rx, ry, col, f'opacity="{op}" filter="url(#soft)"')
    # faint 80s laser backdrop lines, fanning behind the family
    for x1, x2, op in [(70, 520, .16), (70, 620, .20), (70, 730, .13), (1130, 690, .16), (1130, 590, .20)]:
        p(f"M{x1},640 L{x2},118", sw=5, col="#ff7d9c", extra=f'opacity="{op}"')
    for x1, x2, op in [(90, 560, .14), (1110, 650, .14)]:
        p(f"M{x1},660 L{x2},96", sw=4, col="#7fe3e0", extra=f'opacity="{op}"')
    e(600, 400, 530, 360, "url(#spot)")
    # floor and its seam with the wall
    add('<path d="M0,700 Q600,668 1200,700 L1200,900 L0,900 Z" fill="url(#floor)"/>')
    p("M0,700 Q600,668 1200,700", sw=4, col="#2e2422", extra='opacity="0.55"')
    # a tired studio rug nobody straightened
    add('<g transform="translate(600,800) rotate(-1.6)">')
    add(f'<ellipse cx="0" cy="0" rx="430" ry="72" fill="#7d3f4a" stroke="{INK}" stroke-width="5" opacity="0.92"/>')
    add('<ellipse cx="0" cy="0" rx="385" ry="58" fill="none" stroke="#d6a46d" stroke-width="4" opacity="0.7"/>')
    add('<ellipse cx="0" cy="0" rx="345" ry="46" fill="none" stroke="#4f7780" stroke-width="3" opacity="0.65"/>')
    add('</g>')


def shadow(cx, cy, rx, ry=20):
    e(cx, cy, rx, ry, "#1c1518", 'opacity="0.32" filter="url(#soft2)"')


# ---------------------------------------------------------------- grandpa
def grandpa():
    """Rusty, asleep, leaning onto Dad. One wheeled foot, a wrench for a cane."""
    shadow(348, 742, 118)
    add('<g transform="translate(350,468) rotate(5)">')
    # legs: one boot, one wheel
    r(-56, 150, 34, 96, "#8a5b3d", rx=10)
    r(-70, 238, 62, 26, "#5d3d2c", rx=9)
    r(24, 150, 32, 74, "#8a5b3d", rx=10)
    c(40, 242, 27, "#3d3430")
    c(40, 242, 9, "#c9b18d", sw=4)
    # dangling far arm
    p("M-88,6 Q-122,70 -112,138", sw=24, col="#9c6a43")
    p("M-88,6 Q-122,70 -112,138", sw=6)
    claw(-112, 148, 170, "#c9b18d")
    # barrel torso with a patch plate
    add(f'<path d="M-92,-42 Q-104,80 -76,158 L76,158 Q104,80 92,-42 Q0,-66 -92,-42 Z" '
        f'fill="#a96f42" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    r(-62, 42, 72, 58, "#7d8c8f", rx=8, sw=5)               # mismatched patch
    rivets([(-54, 52), (2, 52), (-54, 90), (2, 90)], 3.5, "#e6d7b8")
    p("M-78,18 L78,18", sw=4, extra='opacity="0.5"')        # barrel seam
    c(46, 58, 17, "#d9c28f", sw=5)                          # dim gauge
    p("M46,58 L38,48", sw=4)
    e(58, 122, 15, 26, "#4a2e20", 'opacity="0.5"')          # oil stain
    # head, nodded right down onto his chest toward Dad
    add('<g transform="translate(14,-92) rotate(17)">')
    r(-22, 44, 44, 28, "#8a5b3d", rx=6)                     # neck
    r(-66, -52, 132, 102, "#bf8a57", rx=26)
    r(-66, -52, 132, 24, "#9c6a43", rx=11, sw=5)            # brow band
    # wire beard
    p("M-52,42 Q-44,92 -28,70 Q-18,104 -4,74 Q8,108 18,72 Q32,100 42,66 Q52,88 52,42",
      sw=6, col="#e8e2d2")
    p("M-52,42 Q-44,92 -28,70 Q-18,104 -4,74 Q8,108 18,72 Q32,100 42,66 Q52,88 52,42", sw=2.2)
    # shut eyes, open snoring mouth
    p("M-46,-4 Q-32,6 -18,-4", sw=6)
    p("M18,-4 Q32,6 46,-4", sw=6)
    e(0, 28, 11, 14, "#39241a", f'stroke="{INK}" stroke-width="4"')
    # crooked spectacles sliding off
    add('<g transform="translate(0,2) rotate(-13)">')
    add(f'<circle cx="-32" cy="0" r="21" fill="#bcd6da" fill-opacity="0.22" stroke="{INK}" stroke-width="4"/>')
    add(f'<circle cx="32" cy="0" r="21" fill="#bcd6da" fill-opacity="0.22" stroke="{INK}" stroke-width="4"/>')
    p("M-11,0 L11,0", sw=4)
    p("M24,-11 L38,4", sw=2.5, extra='opacity="0.7"')       # cracked lens
    add('</g>')
    # hearing-horn antenna + bald dome bolt
    p("M-48,-48 Q-76,-82 -98,-76", sw=7)
    poly("-98,-92 -122,-70 -94,-60", "#d9c28f", sw=5)
    c(28, -58, 9, "#d9c28f", sw=4)
    add('</g>')
    # arm onto the wrench-cane
    p("M88,4 Q118,56 104,106", sw=22, col="#9c6a43")
    p("M88,4 Q118,56 104,106", sw=6)
    claw(102, 112, 20, "#c9b18d")
    add('</g>')
    # wrench cane stuck in the floor beside him
    add('<g transform="translate(462,600) rotate(9)">')
    r(-9, -32, 18, 150, "#9aa4a8", rx=8, sw=5)
    p("M-16,-52 A21,21 0 1,0 16,-52 L5,-40 L5,-24 L-5,-24 L-5,-40 Z", fill="#b7c0c4", sw=5)
    add('</g>')
    # snore bubbles drifting toward Dad's shoulder
    for cx, cy, rad in [(420, 352, 7), (446, 330, 10), (478, 302, 14), (516, 268, 18)]:
        add(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="#dfeef0" fill-opacity="0.35" '
            f'stroke="#dfeef0" stroke-width="2.5" stroke-opacity="0.8"/>')


# ---------------------------------------------------------------- dad
def dad():
    """Tall, proud, chest out, giving a thumbs-up to nobody in particular."""
    shadow(612, 750, 132)
    add('<g transform="translate(612,420)">')
    # legs and very polished boots
    r(-68, 170, 42, 118, "#46617c", rx=10)
    r(28, 170, 42, 118, "#46617c", rx=10)
    r(-86, 280, 76, 30, "#2e3d4c", rx=11)
    r(14, 280, 76, 30, "#2e3d4c", rx=11)
    e(-62, 290, 18, 6, "#eaf4ff", 'opacity="0.8"')
    # left arm: rigid thumbs-up, held too high and too long
    p("M-98,-52 Q-158,-30 -150,-96", sw=27, col="#5b7a99")
    p("M-98,-52 Q-158,-30 -150,-96", sw=6)
    add('<g transform="translate(-150,-102) rotate(-8)">')
    r(-21, -2, 42, 34, "#c9d2d8", rx=11)                    # the fist
    r(-19, -36, 21, 38, "#c9d2d8", rx=10)                   # the thumb, up
    for xx in (-8, 1, 10):
        p(f"M{xx},4 L{xx},26", sw=3)                        # curled fingers
    add('</g>')
    c(-98, -54, 24, "#46617c")                              # shoulder pad
    # torso, chest pushed out
    add(f'<path d="M-104,-84 L104,-84 L88,178 L-88,178 Z" fill="#5b7a99" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    add(f'<path d="M-104,-84 L-44,-84 L-58,178 L-88,178 Z" fill="#ffffff" opacity="0.10"/>')
    c(100, -54, 24, "#46617c")                              # right shoulder pad
    # tie, knotted slightly crooked
    add('<g transform="translate(0,-84) rotate(3)">')
    poly("-13,0 13,0 8,22 -8,22", "#a93f4c", sw=5)
    poly("-8,22 8,22 14,98 0,124 -14,98", "#bf4a58", sw=5)
    add('</g>')
    # chest gauge pinned at maximum, and a row of proud buttons
    c(-52, 18, 25, "#e9e2cf", sw=5)
    p("M-52,18 L-36,4", sw=5, col="#a93f4c")
    for a in (-66, -52, -38):
        p(f"M{a},-2 L{a},4", sw=3)
    for yy, col in [(6, "#ffd166"), (34, "#8fd0c5"), (62, "#ff8fa3")]:
        c(56, yy, 9, col, sw=4)
    r(-34, 118, 68, 26, "#46617c", rx=7, sw=5)              # belt plate
    rivets([(-88, -66), (88, -66), (-72, 158), (72, 158)])
    # head: square jaw, gaze fixed somewhere above the camera
    add('<g transform="translate(0,-168)">')
    r(-24, 58, 48, 30, "#46617c", rx=6)                     # neck
    r(-74, -64, 148, 128, "#7d9cba", rx=18)
    r(-74, -64, 148, 26, "#5b7a99", rx=11, sw=5)            # flat top plate
    # side ear-dials
    c(-78, 6, 13, "#46617c", sw=5)
    c(78, 6, 13, "#46617c", sw=5)
    # heavy brow, lowered on Grandpa's side
    p("M-58,-18 L-10,-8", sw=9)
    p("M12,-18 L58,-18", sw=9)
    # eyes looking up and away from the snoring
    r(-52, -6, 34, 24, "#dff6ff", rx=9, sw=5)
    r(18, -6, 34, 24, "#dff6ff", rx=9, sw=5)
    c(-28, 0, 7, INK, sw=0)
    c(42, 0, 7, INK, sw=0)
    # grille mouth set in a manly straight line
    r(-34, 34, 68, 20, "#33475c", rx=7, sw=5)
    for xx in (-22, -8, 6, 20):
        p(f"M{xx},38 L{xx},50", sw=3.5, col="#9fc3dd")
    # centre antenna, ramrod straight
    p("M0,-64 L0,-104", sw=7)
    c(0, -112, 10, "#ffd166", sw=5)
    # camera-flash glare on the forehead
    e(-42, -34, 26, 11, "#ffffff", 'opacity="0.55" transform="rotate(-14 -42 -34)"')
    add('</g>')
    add('</g>')


# ---------------------------------------------------------------- teen
def teen():
    """Slouched, headphones on, leaning as far out of the photo as physics allows."""
    shadow(912, 748, 104)
    add('<g transform="translate(896,448) rotate(10)">')
    # skinny legs, one toe tapping
    r(-48, 138, 30, 118, "#3a3550", rx=10)
    r(20, 138, 30, 104, "#3a3550", rx=10)
    r(-62, 248, 56, 24, "#241f33", rx=9)
    add('<g transform="translate(38,246) rotate(-22)">')
    r(-8, -6, 58, 24, "#241f33", rx=9)
    add('</g>')
    for d in ("M66,214 q18,10 16,28", "M80,204 q26,16 24,42"):
        p(d, sw=4, extra='opacity="0.6"')                   # tap-tap motion
    # tapered hoodie torso
    add(f'<path d="M-70,-66 L70,-66 L54,146 L-54,146 Z" fill="#4a3f66" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    add(f'<path d="M-70,-66 L70,-66 L64,-14 L-64,-14 Z" fill="#5d4f82" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    p("M-18,-14 L-8,146", sw=4, extra='opacity="0.45"')     # zipper seam
    r(-34, 96, 68, 34, "#3a3550", rx=9, sw=5)               # pouch pocket
    # arms crossed hard across the chest
    add(f'<path d="M-72,-46 L58,34 L46,62 L-78,-16 Z" fill="#5d4f82" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    add(f'<path d="M72,-46 L-54,42 L-42,70 L78,-16 Z" fill="#6c5c96" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    claw(-58, 54, -70, "#b9aed6")
    claw(58, 46, 70, "#b9aed6")
    # head: pushed forward, gaze sliding off the right edge of the frame
    add('<g transform="translate(-6,-138) rotate(4)">')
    r(-18, 46, 36, 28, "#3a3550", rx=6)
    r(-58, -50, 116, 102, "#8d84ad", rx=20)
    # drooping bent antenna
    p("M30,-48 Q58,-78 74,-62 Q86,-50 76,-38", sw=6)
    c(74, -34, 7, "#ff8fa3", sw=4)
    # a fringe plate flopped over one eye
    add(f'<path d="M-58,-50 L58,-50 L58,-22 Q18,-40 -22,-16 Q-44,-6 -58,-20 Z" '
        f'fill="#2c2740" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    # half-lidded eyes, pupils jammed to the side
    r(-44, -6, 32, 20, "#e8f6ff", rx=8, sw=5)
    r(12, -6, 32, 20, "#e8f6ff", rx=8, sw=5)
    c(-16, 4, 6.5, INK, sw=0)
    c(40, 4, 6.5, INK, sw=0)
    p("M-44,-4 L-12,-2", sw=7)                              # lids
    p("M12,-4 L44,-2", sw=7)
    # flat, unimpressed mouth
    p("M-24,32 L24,30", sw=6)
    # headphones clamped over everything
    p("M-62,-16 Q-60,-78 0,-80 Q60,-78 62,-16", sw=11, col="#241f33")
    r(-76, -22, 26, 48, "#ff5d7a", rx=11, sw=5)
    r(50, -22, 26, 48, "#ff5d7a", rx=11, sw=5)
    c(-63, 2, 6, "#ffd166", sw=3)
    c(63, 2, 6, "#ffd166", sw=3)
    add('</g>')
    # headphone cable trailing to the pocket
    p("M56,-92 Q88,-30 62,40 Q44,88 12,108", sw=4, col="#241f33")
    add('</g>')


# ---------------------------------------------------------------- middle child
def middle_child():
    """Almost entirely behind Mom: half a head, worried eyes, one hopeful hand."""
    add('<g transform="translate(706,438)">')
    # slim body sliver, the rest of it lost behind Mom and the baby
    r(-28, 28, 60, 132, "#a18cc0", rx=14)
    # a head squeezed in at Mom's shoulder, under Dad's resting hand
    add('<g transform="rotate(-7)">')
    r(-48, -56, 96, 96, "#c3b2dd", rx=24)
    p("M-28,-50 Q-46,-70 -35,-82 Q-26,-91 -17,-81 Q-11,-73 -20,-69", sw=6)  # anxious curl
    c(-21, -65, 6, "#ffd166", sw=3.5)
    # brows raised in the middle, eyes up at the grown-ups
    p("M-36,-18 L-12,-24", sw=6)
    p("M12,-24 L36,-18", sw=6)
    c(-22, 0, 13, "#eef8ff", sw=5)
    c(22, 0, 13, "#eef8ff", sw=5)
    c(-22, -5, 6, INK, sw=0)
    c(22, -5, 6, INK, sw=0)
    e(-25, -8, 3, 3, "#ffffff")
    e(19, -8, 3, 3, "#ffffff")
    p("M-10,26 Q0,20 10,26", sw=5)                          # small wobbly mouth
    add('</g>')
    add('</g>')


# ---------------------------------------------------------------- mom
def mom():
    """Front and centre, beaming straight at the lens, holding everyone in place."""
    shadow(598, 752, 142)
    add('<g transform="translate(598,548)">')
    # bell skirt base with two small feet peeping out
    add(f'<path d="M-58,34 L58,34 L112,190 Q0,212 -112,190 Z" fill="#d9675f" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    p("M-112,188 Q0,210 112,188", sw=5, col="#f2c14e")
    for xx in (-70, -35, 0, 35, 70):
        c(xx, 150 + abs(xx) // 9, 6, "#f4e3c2", sw=3.5)     # skirt rivet dots
    r(-86, 192, 52, 24, "#7a3b42", rx=10)
    r(36, 192, 52, 24, "#7a3b42", rx=10)
    # torso
    add(f'<path d="M-78,-96 L78,-96 L60,44 L-60,44 Z" fill="#ef8a7b" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    # pearl necklace of polished ball bearings
    for xx, yy in [(-42, -86), (-24, -72), (-6, -66), (12, -66), (28, -74), (40, -86)]:
        c(xx, yy, 8, "#f6f1e6", sw=3.5)
    # heart brooch (a shape, not a letter)
    add(f'<path d="M-38,-28 c-4,-12 -24,-10 -24,3 c0,11 12,17 24,28 c12,-11 24,-17 24,-28 '
        f'c0,-13 -20,-15 -24,-3 Z" fill="#ffd166" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    rivets([(-64, -80), (64, -80), (-48, 28), (48, 28)], 3.5, "#ffe3d3")
    # her near arm, curled into her lap under the baby and losing the argument
    p("M-76,-62 Q-124,-6 -92,52 Q-70,88 -18,82", sw=24, col="#ef8a7b")
    p("M-76,-62 Q-124,-6 -92,52 Q-70,88 -18,82", sw=6)
    claw(-12, 84, -62, "#ffe0cc")
    add('</g>')
    # head, tipped toward Dad, smiling with far too many teeth lit
    add('<g transform="translate(590,386) rotate(-8)">')
    r(-20, 52, 40, 26, "#cf6a5c", rx=6)
    c(-66, 8, 12, "#cf6a5c", sw=5)
    c(66, 8, 12, "#cf6a5c", sw=5)
    r(-66, -60, 132, 120, "#f2c9a7", rx=30)
    # coiled hair-bun antenna
    p("M0,-58 Q-4,-84 14,-90 Q34,-96 34,-80 Q34,-66 20,-68 Q8,-70 12,-80", sw=7)
    c(36, -74, 8, "#ffd166", sw=4)
    p("M-50,-52 Q0,-72 50,-52", sw=9, col="#b3543f")        # hairline sweep
    # eyes locked on the camera, lashes out
    for sgn in (-1, 1):
        cx = 30 * sgn
        c(cx, -12, 16, "#ffffff", sw=5)
        c(cx, -12, 8, "#3a6ea8", sw=3)
        c(cx, -12, 3.6, INK, sw=0)
        e(cx - 3, -16, 2.6, 2.6, "#ffffff")
        for dx, dy in [(-14, -13), (-9, -18), (-3, -20)]:
            p(f"M{cx + dx * sgn},{-24 + (dy + 13)} l{-6 * sgn},-7", sw=3.5)
    p("M-48,-38 Q-30,-46 -14,-38", sw=5)                    # brows
    p("M14,-38 Q30,-46 48,-38", sw=5)
    e(-46, 14, 11, 7, "#f09a8a", 'opacity="0.75"')          # blush plates
    e(46, 14, 11, 7, "#f09a8a", 'opacity="0.75"')
    # the enormous fixed grin
    add(f'<path d="M-40,16 Q0,52 40,16 Q30,48 0,50 Q-30,48 -40,16 Z" fill="#5a2d2b" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    for xx in range(-30, 31, 12):
        r(xx, 22, 10, 13, "#fff7e6", rx=3, sw=2.5)
    add('</g>')


# ---------------------------------------------------------------- baby
def baby():
    """Round, mint, and being held upside down. Cross-eyed at its own bolt."""
    add('<g transform="translate(688,600) rotate(148)">')
    # tiny kicking legs (which point up once the whole baby is inverted)
    for sgn, bend in ((-1, -10), (1, 14)):
        add(f'<g transform="rotate({bend})">')
        r(20 * sgn - 10, 34, 20, 32, "#8fd0c5", rx=8, sw=5)
        r(20 * sgn - 14, 60, 28, 16, "#e8f4f0", rx=7, sw=5)
        add('</g>')
    # diaper plate with a safety pin
    add(f'<path d="M-46,6 L46,6 L34,44 L-34,44 Z" fill="#f6f1e6" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    c(0, 24, 6, "#ffd166", sw=3.5)
    # one-piece round body/head
    c(0, -26, 52, "#a9ddcf")
    e(-20, -48, 16, 10, "#ffffff", 'opacity="0.5" transform="rotate(-18 -20 -48)"')
    # flailing arms
    p("M-48,-30 Q-74,-44 -80,-22", sw=15, col="#8fd0c5")
    p("M-48,-30 Q-74,-44 -80,-22", sw=5)
    p("M48,-28 Q72,-52 84,-40", sw=15, col="#8fd0c5")
    p("M48,-28 Q72,-52 84,-40", sw=5)
    c(-81, -18, 9, "#e8f4f0", sw=4)
    c(86, -38, 9, "#e8f4f0", sw=4)
    # cross-eyed, both pupils hunting the bolt in the middle
    c(-20, -38, 13, "#ffffff", sw=5)
    c(20, -38, 13, "#ffffff", sw=5)
    c(-12, -34, 5.5, INK, sw=0)
    c(12, -34, 5.5, INK, sw=0)
    # pacifier: a hex bolt on a ring
    add(f'<polygon points="0,-24 11,-18 11,-6 0,0 -11,-6 -11,-18" fill="#c9d2d8" '
        f'stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    c(0, -12, 4.5, "#7d8c93", sw=3)
    p("M0,0 Q2,12 -6,16", sw=4)
    # single curl antenna
    p("M0,-76 Q4,-94 18,-92 Q28,-90 24,-80", sw=6)
    c(23, -77, 6, "#ffd166", sw=3.5)
    add('</g>')
    # wobble lines in world space, around the upside-down baby
    for d in ("M614,556 q-14,16 -6,34", "M626,546 q-22,24 -12,52", "M758,560 q16,14 10,34"):
        p(d, sw=4, extra='opacity="0.55"')


# ---------------------------------------------------------------- little kid
def kid():
    """Mid-bounce, waving at full speed, one strap undone, swinging on a cane."""
    shadow(294, 796, 88, 16)
    add('<g transform="translate(292,676) rotate(-4)">')
    # bounce arcs under the airborne foot
    for d in ("M-58,116 q30,16 62,4", "M-70,132 q38,20 80,6"):
        p(d, sw=4, extra='opacity="0.55"')
    # legs: one planted (on Grandpa), one kicked up behind
    r(-42, 52, 28, 62, "#3f7f8c", rx=9)
    r(-56, 108, 50, 22, "#a93f4c", rx=9)
    add('<g transform="translate(26,58) rotate(-52)">')
    r(-14, 0, 28, 54, "#3f7f8c", rx=9)
    r(-22, 48, 48, 21, "#a93f4c", rx=9)
    add('</g>')
    # torso in overalls
    add(f'<path d="M-52,-44 L52,-44 L44,58 L-44,58 Z" fill="#f2c14e" '
        f'stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    add(f'<path d="M-44,58 L44,58 L40,4 L-40,4 Z" fill="#4f97a5" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    r(-38, -44, 16, 52, "#4f97a5", rx=6, sw=5)              # fastened strap
    c(-30, 2, 6, "#ffd166", sw=3.5)
    # undone strap flapping loose, with motion ghosts
    for op, rot in ((0.25, 62), (0.5, 44), (1.0, 26)):
        add(f'<g transform="translate(34,6) rotate({rot})" opacity="{op}">')
        r(-8, 0, 16, 46, "#4f97a5", rx=6, sw=5)
        add('</g>')
    c(36, 2, 6, "#ffd166", sw=3.5)
    # the waving arm, well above its head, with two translucent echo hands
    for op, rot in ((0.28, -30), (0.55, -15), (1.0, 0)):
        add(f'<g transform="translate(-48,-30) rotate({rot})" opacity="{op}">')
        p("M0,0 Q-38,-72 -30,-142", sw=17, col="#f2c14e")
        p("M0,0 Q-38,-72 -30,-142", sw=5)
        claw(-29, -152, -10, "#f6e3ae")
        add('</g>')
    # spring neck, stretched by the bounce
    p("M-14,-44 q14,-8 0,-16 q-14,-8 0,-16 q14,-8 2,-14", sw=6)
    # big round head
    add('<g transform="translate(0,-128) rotate(5)">')
    c(-60, 6, 11, "#d9a441", sw=5)
    c(60, 6, 11, "#d9a441", sw=5)
    r(-62, -54, 124, 108, "#ffd166", rx=32)
    # propeller cap, spinning
    add(f'<path d="M-48,-44 A52,38 0 0,1 48,-44 L48,-34 L-48,-34 Z" fill="#4f97a5" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    p("M-48,-34 L-68,-28", sw=8, col="#a93f4c")             # crooked brim
    p("M0,-76 L0,-96", sw=6)
    e(0, -100, 44, 9, "#ff8fa3", 'opacity="0.35"')          # blur disc
    e(-26, -100, 24, 8, "#ff5d7a", f'stroke="{INK}" stroke-width="4" transform="rotate(-8 -26 -100)"')
    e(26, -100, 24, 8, "#ff5d7a", f'stroke="{INK}" stroke-width="4" transform="rotate(8 26 -100)"')
    c(0, -100, 8, "#ffd166", sw=4)
    # one eye winking hard, the other huge and starry
    p("M-44,-6 L-22,2 L-44,10", sw=6)
    c(28, 0, 18, "#ffffff", sw=5)
    poly("28,-10 31,-3 38,-2 32,2 34,9 28,5 22,9 24,2 18,-2 25,-3", "#3a6ea8", sw=3)
    # open grin with exactly one tooth missing
    add(f'<path d="M-34,22 Q2,56 38,20 Q28,50 0,52 Q-28,50 -34,22 Z" fill="#5a2d2b" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    for xx in (-24, -12, 12, 24):
        r(xx, 27, 10, 12, "#fff7e6", rx=3, sw=2.5)
    add(f'<rect x="-1" y="29" width="10" height="12" rx="3" fill="#2b1715"/>')
    e(-40, 22, 9, 6, "#f09a6a", 'opacity="0.8"')
    e(42, 20, 9, 6, "#f09a6a", 'opacity="0.8"')
    add('</g>')
    add('</g>')


# ---------------------------------------------------------------- dog
def dog():
    """The pet: sitting beautifully, facing entirely the wrong way."""
    shadow(972, 796, 108, 16)
    add('<g transform="translate(968,724)">')
    # spring tail wagging, with a ghost
    for op, rot in ((0.3, -18), (1.0, 6)):
        add(f'<g transform="translate(-84,-18) rotate({rot})" opacity="{op}">')
        p("M0,0 q-18,-8 -14,-22 q3,-12 -10,-18", sw=6)
        add('</g>')
    # hind leg and one front paw already setting off
    r(-64, 22, 30, 44, "#8a97a0", rx=10)
    r(-76, 60, 48, 18, "#5f6d75", rx=8)
    add('<g transform="translate(52,26) rotate(-38)">')
    r(-11, 0, 24, 42, "#8a97a0", rx=9)
    r(-18, 38, 42, 17, "#5f6d75", rx=8)
    add('</g>')
    r(24, 26, 24, 40, "#7d8c93", rx=9)
    r(14, 60, 44, 18, "#5f6d75", rx=8)
    # body
    add(f'<path d="M-92,-30 L62,-30 Q92,-28 88,6 Q84,38 48,38 L-62,38 Q-94,36 -92,-30 Z" '
        f'fill="#aeb9bf" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    e(-38, -2, 26, 18, "#e08a4c", f'stroke="{INK}" stroke-width="4"')   # patch plate
    rivets([(-76, -18), (58, -18), (-70, 24), (64, 24)], 3.5)
    # head turned clean away to stare out of the frame
    add('<g transform="translate(96,-44) rotate(8)">')
    r(-20, 26, 36, 26, "#8a97a0", rx=7)
    # ears: one up, one flopped
    poly("-34,-34 -18,-78 2,-38", "#7d8c93", sw=5)
    add(f'<path d="M34,-36 Q62,-30 56,4 Q52,26 34,20 Z" fill="#e08a4c" '
        f'stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    r(-42, -42, 84, 68, "#c3ced3", rx=20)
    # muzzle pointing right, nose leading out of shot
    r(24, -10, 54, 36, "#aeb9bf", rx=14, sw=5)
    e(76, 2, 11, 9, INK, 'stroke="none"')
    e(72, -2, 3.5, 3, "#ffffff")
    # a single visible eye, gazing off after something better
    c(14, -20, 11, "#ffffff", sw=5)
    c(20, -20, 5.5, INK, sw=0)
    # metal tongue lolling
    add(f'<path d="M38,26 L62,26 Q64,48 50,50 Q36,48 38,26 Z" fill="#ff8fa3" '
        f'stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    p("M50,30 L50,44", sw=3)
    # collar with a bone-shaped tag
    p("M-24,30 Q4,42 34,28", sw=10, col="#a93f4c")
    add('<g transform="translate(6,44) rotate(-24)">')
    for dx, dy in ((-11, -5), (-11, 5), (11, -5), (11, 5)):
        c(dx, dy, 6, "#f6f1e6", sw=3)
    r(-11, -4, 22, 8, "#f6f1e6", rx=4, sw=3)
    add('</g>')
    add('</g>')
    add('</g>')
    # the something better: a small butterfly-bot just out of reach
    add('<g transform="translate(1128,618)">')
    e(-14, -8, 15, 9, "#ffd166", f'stroke="{INK}" stroke-width="3.5" transform="rotate(-28 -14 -8)"')
    e(14, -8, 15, 9, "#ffd166", f'stroke="{INK}" stroke-width="3.5" transform="rotate(28 14 -8)"')
    e(0, 0, 5, 11, "#5b7a99", f'stroke="{INK}" stroke-width="3.5"')
    p("M-3,-10 q-8,-8 -13,-6 M3,-10 q8,-8 13,-6", sw=3)
    add('</g>')
    p("M1096,646 q-26,6 -38,-8 q-10,-12 2,-22", sw=3, extra='opacity="0.55" stroke-dasharray="1 7"')


# ---------------------------------------------------------------- relationships
def relationships():
    """Drawn last, over everyone: the touches (and near-touches) between them."""
    # Dad's hand comes down for a fond shoulder-pat and lands, oblivious,
    # on the middle child's head, which is now serving as an armrest.
    p("M724,342 Q732,362 720,378", sw=26, col="#5b7a99")
    p("M724,342 Q732,362 720,378", sw=6)
    c(716, 380, 19, "#c9d2d8")                              # a big resting palm
    for d in ("M698,388 Q691,405 697,415", "M716,394 L716,414", "M734,388 Q741,405 735,415"):
        p(d, sw=6)                                          # fingers draped over the top
    for d in ("M688,392 l-10,-8", "M744,394 l10,-8"):       # the squash
        p(d, sw=3.5, extra='opacity="0.75"')
    # Mom's arm at full telescopic stretch: under the middle child's chin,
    # then up to clamp onto the teen's shoulder and haul him into frame.
    p("M668,494 Q736,512 792,492 Q838,476 844,420 Q846,404 846,394", sw=23, col="#ef8a7b")
    p("M668,494 Q736,512 792,492 Q838,476 844,420 Q846,404 846,394", sw=6)
    for t in range(5):  # exposed telescopic rings along the outstretched arm
        x = 696 + t * 26
        y = 503 - t * 3
        p(f"M{x},{y - 11} L{x + 4},{y + 11}", sw=4, extra='opacity="0.6"')
    p("M835,448 L855,446", sw=4, extra='opacity="0.6"')
    claw(848, 390, -84, "#ffe0cc")  # clamped on the teen's shoulder
    # strain ticks where the teen resists, leaning the other way
    for d in ("M814,366 l-14,-12", "M836,358 l-7,-16", "M858,360 l2,-16"):
        p(d, sw=4, extra='opacity="0.8"')
    # The kid is swinging itself around Grandpa's wrench-cane, mid-bounce,
    # while Grandpa sleeps through the whole performance.
    p("M340,634 Q408,602 456,572", sw=15, col="#f2c14e")
    p("M340,634 Q408,602 456,572", sw=5)
    claw(463, 568, -55, "#f6e3ae")
    for d in ("M358,606 q12,-2 20,6", "M352,594 q16,-4 28,4"):  # stretch shudder
        p(d, sw=3.5, extra='opacity="0.55"')
    # A loose leash from the teen's side to the dog, sagging with slack in it.
    p("M932,586 Q975,660 1015,690 Q1045,712 1072,720", sw=5, col="#d9c28f",
      extra='stroke-dasharray="10 6"')
    p("M932,586 Q928,606 936,620", sw=5)                    # handle loop, empty


# ---------------------------------------------------------------- photo finish
def photo_finish():
    # red-eye: two tiny flash dots nobody retouched
    e(618, 370, 2.3, 2.3, "#ff4d4d", 'opacity="0.9"')
    e(559, 378, 2.3, 2.3, "#ff4d4d", 'opacity="0.9"')
    # vignette and a blob of flash falloff
    add('<rect width="1200" height="900" fill="url(#vig)"/>')
    e(116, 84, 210, 120, "#ffffff", 'opacity="0.10" filter="url(#soft)"')
    # film grain: a scatter of faint specks, seeded so the picture is stable
    import random
    rng = random.Random(1987)
    for _ in range(240):
        x, y = rng.uniform(10, 1190), rng.uniform(10, 890)
        op = rng.uniform(0.03, 0.10)
        col = "#ffffff" if rng.random() < 0.5 else "#1a1214"
        add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(0.7, 1.9):.1f}" '
            f'fill="{col}" opacity="{op:.2f}"/>')
    # the white border of a printed studio portrait, slightly proud of the image
    add(f'<rect x="14" y="14" width="1172" height="872" fill="none" stroke="#f4ecdc" stroke-width="16"/>')
    add(f'<rect x="26" y="26" width="1148" height="848" fill="none" stroke="{INK}" '
        f'stroke-width="3" opacity="0.55"/>')
    # one corner of the print curling up
    add('<path d="M1200,900 L1200,842 Q1162,850 1148,900 Z" fill="#e7dcc4"/>')
    add(f'<path d="M1200,842 Q1162,850 1148,900" fill="none" stroke="{INK}" '
        f'stroke-width="3" opacity="0.6"/>')


def main():
    add('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" '
        'viewBox="0 0 1200 900">')
    backdrop()
    # back row, then the almost-hidden child, then the front row
    grandpa()
    dad()
    teen()
    middle_child()
    mom()
    baby()
    kid()
    dog()
    relationships()
    photo_finish()
    add('</svg>')
    out = Path(__file__).resolve().parent.parent / "output" / "awkward-robot-family-portrait.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(S) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
