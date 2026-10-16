#!/usr/bin/env python3
"""Generates output/octopus_ramen_chef.svg - an octopus chef at a night-time ramen booth."""
import math
import os

W, H = 1200, 900
BODY = "#b8479a"
BODY_LIGHT = "#d56cb8"
BODY_DARK = "#7d2f78"
SUCKER = "#f6bfe0"

out = []


def add(s):
    out.append(s)


# ---------------------------------------------------------------- arm helper
def catmull(pts, per=18):
    p = [pts[0]] + list(pts) + [pts[-1]]
    res = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            res.append((x, y))
    res.append(pts[-1])
    return res


def arm(pts, w0, w1, side=1, s_from=0.12, s_to=0.97, fill=BODY, extra="", round_root=False):
    c = catmull(pts)
    n = len(c)
    # cumulative length
    L = [0.0]
    for i in range(1, n):
        L.append(L[-1] + math.dist(c[i], c[i - 1]))
    tot = L[-1]
    left, right, mid, norms, ws = [], [], [], [], []
    for i in range(n):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        s = L[i] / tot
        w = (w0 + (w1 - w0) * (s ** 0.85)) / 2
        left.append((c[i][0] + nx * w, c[i][1] + ny * w))
        right.append((c[i][0] - nx * w, c[i][1] - ny * w))
        norms.append((nx, ny))
        ws.append(w)
    poly = left + right[::-1]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z"
    g = [f'<g {extra}>']
    g.append(f'<path d="{d}" fill="{fill}"/>')
    g.append(f'<circle cx="{c[-1][0]:.1f}" cy="{c[-1][1]:.1f}" r="{ws[-1]:.1f}" fill="{fill}"/>')
    if round_root:
        g.append(f'<circle cx="{c[0][0]:.1f}" cy="{c[0][1]:.1f}" r="{ws[0]:.1f}" fill="{fill}"/>')
    # soft highlight along the side opposite to the suckers
    hl = [(c[i][0] - norms[i][0] * side * ws[i] * 0.45, c[i][1] - norms[i][1] * side * ws[i] * 0.45) for i in range(int(n * 0.03), int(n * 0.9))]
    g.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in hl) + f'" fill="none" stroke="{BODY_LIGHT}" stroke-width="{max(w0*0.16,2):.1f}" stroke-linecap="round" opacity=".75"/>')
    # suckers
    pos = L[int(n * s_from)]
    end = L[int(n * s_to) - 1]
    while pos < end:
        i = min(range(n), key=lambda k: abs(L[k] - pos))
        w = ws[i]
        cx = c[i][0] + norms[i][0] * side * w * 0.5
        cy = c[i][1] + norms[i][1] * side * w * 0.5
        r = max(w * 0.38, 1.6)
        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{BODY_DARK}" opacity=".55"/>')
        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.72:.1f}" fill="{SUCKER}"/>')
        pos += max(w * 1.15 + 3, 7)
    g.append('</g>')
    return "\n".join(g)


# ---------------------------------------------------------------- defs
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('<title>Octopus chef at a ramen booth</title>')
add('''<defs>
<linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1233"/><stop offset="1" stop-color="#2a1d4a"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#ffd48a"/><stop offset=".5" stop-color="#e58a46"/><stop offset="1" stop-color="#6b2d2a"/></radialGradient>
<radialGradient id="bodyg" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#d868bc"/><stop offset=".6" stop-color="#b8479a"/><stop offset="1" stop-color="#8b3585"/></radialGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9783f"/><stop offset="1" stop-color="#7a4624"/></linearGradient>
<linearGradient id="counterTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e7b273"/><stop offset="1" stop-color="#c58a50"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8e98a6"/><stop offset=".3" stop-color="#e8edf2"/><stop offset=".7" stop-color="#b6beca"/><stop offset="1" stop-color="#7c8593"/></linearGradient>
<linearGradient id="lantern" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b3201f"/><stop offset=".5" stop-color="#ff5a3c"/><stop offset="1" stop-color="#b3201f"/></linearGradient>
<linearGradient id="broth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8a94a"/><stop offset="1" stop-color="#c9822f"/></linearGradient>
<filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#2a0d2a" flood-opacity=".45"/></filter>
<pattern id="planks" width="60" height="40" patternUnits="userSpaceOnUse"><rect width="60" height="40" fill="none"/><path d="M0 0H60M30 0V40" stroke="#00000022" stroke-width="2" fill="none"/></pattern>
</defs>''')

# ---------------------------------------------------------------- backdrop
add(f'<rect width="{W}" height="{H}" fill="url(#night)"/>')
# interior wall
add(f'<rect x="40" y="110" width="1120" height="600" fill="url(#glow)"/>')
for x in range(40, 1160, 70):
    add(f'<path d="M{x} 110V710" stroke="#4a1f1a" stroke-opacity=".28" stroke-width="3"/>')
# posts
for x in (0, 1150):
    add(f'<rect x="{x}" y="0" width="50" height="{H}" fill="#4a2a18"/><rect x="{x+(8 if x==0 else 34)}" y="0" width="6" height="{H}" fill="#6b3f24"/>')
# distant night lights outside the posts
for (x, y, r) in [(18, 300, 5), (22, 420, 4), (1182, 340, 5), (1176, 470, 4), (20, 560, 3), (1180, 580, 3)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd27a" opacity=".6"/>')

# ---------------------------------------------------------------- awning
add('<g>')
add('<rect x="0" y="0" width="1200" height="96" fill="#8f1d22"/>')
for i in range(0, 24):
    if i % 2 == 0:
        add(f'<rect x="{i*50}" y="0" width="50" height="96" fill="#f4ecdc"/>')
for i in range(24):
    col = "#f4ecdc" if i % 2 == 0 else "#8f1d22"
    add(f'<path d="M{i*50} 96H{i*50+50}V104Q{i*50+25} 140 {i*50} 104Z" fill="{col}"/>')
add('<rect x="0" y="0" width="1200" height="14" fill="#2b1612"/>')
add('<path d="M0 104 H1200" stroke="#00000030" stroke-width="3"/>')
add('</g>')
# string bulbs under awning
add('<path d="M40 150 Q300 190 600 150 T1160 150" fill="none" stroke="#2b1612" stroke-width="2" opacity="0"/>')

# ---------------------------------------------------------------- lanterns
def lantern(cx, top):
    h = 140
    s = [f'<g>']
    s.append(f'<path d="M{cx} {top-34}V{top}" stroke="#2b1612" stroke-width="3"/>')
    s.append(f'<ellipse cx="{cx}" cy="{top+h/2}" rx="75" ry="85" fill="#ffb14a" opacity=".35" filter="url(#blur8)"/>')
    s.append(f'<rect x="{cx-22}" y="{top-8}" width="44" height="14" rx="3" fill="#2b1612"/>')
    s.append(f'<path d="M{cx-22} {top+4} C{cx-62} {top+30} {cx-62} {top+h-20} {cx-22} {top+h}H{cx+22}C{cx+62} {top+h-20} {cx+62} {top+30} {cx+22} {top+4}Z" fill="url(#lantern)"/>')
    for k in (28, 56, 84, 112):
        wv = 50 - abs(k - 70) * 0.18
        s.append(f'<path d="M{cx-wv} {top+k}Q{cx} {top+k+8} {cx+wv} {top+k}" fill="none" stroke="#6a1010" stroke-width="2" opacity=".55"/>')
    s.append(f'<rect x="{cx-26}" y="{top+h-4}" width="52" height="14" rx="3" fill="#2b1612"/>')
    s.append(f'<text x="{cx}" y="{top+h/2+10}" font-family="Helvetica, Arial, sans-serif" font-weight="800" font-size="25" letter-spacing="1" fill="#fff4dc" text-anchor="middle">RAMEN</text>')
    s.append('</g>')
    return "\n".join(s)

add(lantern(150, 170))
add(lantern(1050, 170))

# ---------------------------------------------------------------- noren curtains
def noren(x0, panels=3, pw=72):
    s = []
    s.append(f'<rect x="{x0-6}" y="112" width="{panels*pw+12}" height="10" rx="4" fill="#3a2214"/>')
    for i in range(panels):
        x = x0 + i * pw
        s.append(f'<path d="M{x+2} 122H{x+pw-2}V232Q{x+pw/2} 240 {x+2} 232Z" fill="#1f2f6b"/>')
        s.append(f'<path d="M{x+2} 122H{x+8}V236H{x+2}Z" fill="#00000030"/>')
        s.append(f'<circle cx="{x+pw/2}" cy="170" r="22" fill="none" stroke="#f4ecdc" stroke-width="4"/>')
        s.append(f'<path d="M{x+pw/2-12} 172Q{x+pw/2} 188 {x+pw/2+12} 172" fill="none" stroke="#f4ecdc" stroke-width="4" stroke-linecap="round"/>')
        s.append(f'<path d="M{x+pw/2-7} 160q3 -8 0 -12M{x+pw/2+3} 160q3 -8 0 -12" fill="none" stroke="#f4ecdc" stroke-width="3" stroke-linecap="round"/>')
    return "\n".join(s)

add(noren(262))
add(noren(722))

# ---------------------------------------------------------------- menu plaques
def plaque(x, y, w, text, price):
    return (f'<g><path d="M{x+w/2} 112V{y}" stroke="#2b1612" stroke-width="2" opacity="0"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="6" fill="#e9c68f" stroke="#6b3f24" stroke-width="4"/>'
            f'<text x="{x+w/2}" y="{y+25}" font-family="Helvetica, Arial, sans-serif" font-weight="800" font-size="19" fill="#4a1f1a" text-anchor="middle">{text}</text>'
            f'<text x="{x+w/2}" y="{y+44}" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="15" fill="#a3201f" text-anchor="middle">{price}</text></g>')

add(plaque(70, 318, 140, "SHOYU", "¥850"))
add(plaque(70, 380, 140, "TONKOTSU", "¥950"))
add(plaque(70, 442, 140, "TAKO MISO", "¥900"))
add(plaque(990, 318, 140, "GYOZA", "¥450"))
add(plaque(990, 380, 140, "TAKOYAKI", "¥500"))
add(plaque(990, 442, 140, "REFILL", "¥150"))

# ---------------------------------------------------------------- counter top (back part)
add('<rect x="40" y="650" width="1120" height="42" fill="url(#counterTop)"/>')
add('<rect x="40" y="650" width="1120" height="4" fill="#f4cf96"/>')

# ---------------------------------------------------------------- ARMS behind body (roots hidden by body)
shadow = 'filter="url(#shadow)"'

# tebo (noodle strainer) arm - upper left
tebo_arm = [(520, 520), (470, 440), (418, 380), (385, 345)]
# ladle arm
ladle_arm = [(520, 600), (480, 566), (450, 540), (432, 530)]
# bowl-presenting arm (right)
bowl_arm = [(680, 560), (760, 575), (830, 556), (880, 528), (898, 498), (888, 480)]
# chopstick arm
chop_arm = [(690, 480), (730, 400), (772, 320), (808, 280), (836, 268), (846, 282)]
# knife arm (right, along counter)
knife_arm = [(700, 620), (790, 650), (880, 652), (940, 628), (968, 596), (962, 574)]
# resting arm, left of body on counter
rest_arm = [(490, 625), (458, 658), (418, 672), (384, 666), (372, 650), (386, 642)]

# tebo + noodles (drawn before the arm so the hand grips the handle)
add('<g id="tebo">')
# strand of noodles falling back into the pot
for dx, ph in [(-24, 0), (-10, 1), (6, 2), (22, 3)]:
    x0 = 318 + dx
    add(f'<path d="M{x0} 440 C{x0+8*(1 if ph%2 else -1)} 465 {x0-8*(1 if ph%2 else -1)} 495 {x0+3} 525 L{x0+2} 548" fill="none" stroke="#f3d27a" stroke-width="5" stroke-linecap="round"/>')
    add(f'<path d="M{x0-1} 440 C{x0+7*(1 if ph%2 else -1)} 465 {x0-9*(1 if ph%2 else -1)} 495 {x0+2} 525" fill="none" stroke="#fff0b5" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>')
# handle
add('<path d="M380 352 L336 395" stroke="#6b3f24" stroke-width="9" stroke-linecap="round"/>')
# basket (shallow bowl of wire mesh)
add('<path d="M268 412 Q316 392 360 410 Q350 462 314 464 Q276 462 268 412Z" fill="#cdd5de" stroke="#6c7683" stroke-width="4"/>')
add('<path d="M280 424H350M286 438H346M296 452H336" stroke="#6c7683" stroke-width="2" opacity=".7"/>')
add('<path d="M296 418L306 460M314 416L318 464M332 416L328 460M348 418L338 450" stroke="#6c7683" stroke-width="2" opacity=".7"/>')
add('<ellipse cx="314" cy="410" rx="46" ry="9" fill="#f6dc8e" stroke="#6c7683" stroke-width="3"/>')
add('<path d="M280 410q10 -6 20 0t20 0t20 0" fill="none" stroke="#d9b45a" stroke-width="2"/>')
add('</g>')

# ladle
add('<g id="ladle">')
add('<path d="M346 560 L440 516" stroke="#6b3f24" stroke-width="8" stroke-linecap="round"/>')
add('<path d="M322 548 Q324 580 350 580 Q374 578 374 552 Z" fill="#aab3bf" stroke="#5f6a78" stroke-width="3"/>')
add('<ellipse cx="348" cy="550" rx="26" ry="6" fill="#d89a3e"/>')
add('</g>')

# chopsticks (above bowl)
add('<g id="chopsticks">')
add('<path d="M834 270 L858 390" stroke="#c4793a" stroke-width="5" stroke-linecap="round"/>')
add('<path d="M846 268 L880 386" stroke="#a96228" stroke-width="5" stroke-linecap="round"/>')
add('</g>')

# knife
add('<g id="knife" transform="translate(958 572) rotate(40) scale(.66)">')
add('<rect x="-6" y="-8" width="62" height="18" rx="8" fill="#6b3f24"/>')
add('<path d="M56 -6 H150 L176 16 H56Z" fill="#dde3ea" stroke="#7b8594" stroke-width="4" stroke-linejoin="round"/>')
add('<path d="M64 0 H140" stroke="#fff" stroke-width="3" opacity=".8"/>')
add('</g>')

# draw behind-body arms
add(arm(tebo_arm, 40, 11, side=1, extra=shadow))
add(arm(ladle_arm, 38, 11, side=-1, extra=shadow))
add(arm(bowl_arm, 44, 12, side=-1, extra=shadow))
add(arm(chop_arm, 40, 11, side=-1, extra=shadow))

# ---------------------------------------------------------------- BODY
add('<g id="octopus">')
# skirt + mantle
add(f'<path d="M482 430 C468 520 440 590 424 690 L776 690 C760 590 732 520 718 430Z" fill="url(#bodyg)"/>')
add(f'<ellipse cx="600" cy="340" rx="128" ry="158" fill="url(#bodyg)"/>')
# spots
for (x, y, r) in [(540, 262, 7), (566, 238, 5), (655, 270, 8), (690, 330, 5), (520, 318, 5), (672, 232, 4)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{BODY_LIGHT}" opacity=".7"/>')
# soft rim light on the mantle
add('<path d="M500 280 Q505 230 548 205" fill="none" stroke="#f0a6dc" stroke-width="7" stroke-linecap="round" opacity=".55"/>')

# face
add('<ellipse cx="553" cy="392" rx="29" ry="33" fill="#fff"/>')
add('<ellipse cx="647" cy="392" rx="29" ry="33" fill="#fff"/>')
add('<circle cx="560" cy="396" r="16" fill="#25122e"/><circle cx="654" cy="396" r="16" fill="#25122e"/>')
add('<circle cx="565" cy="389" r="6" fill="#fff"/><circle cx="659" cy="389" r="6" fill="#fff"/>')
add('<circle cx="555" cy="403" r="2.5" fill="#fff" opacity=".8"/><circle cx="649" cy="403" r="2.5" fill="#fff" opacity=".8"/>')
add('<path d="M520 348 Q552 328 582 346" fill="none" stroke="#5a1a58" stroke-width="7" stroke-linecap="round"/>')
add('<path d="M618 346 Q648 328 680 348" fill="none" stroke="#5a1a58" stroke-width="7" stroke-linecap="round"/>')
add('<ellipse cx="514" cy="436" rx="22" ry="13" fill="#ff8fa8" opacity=".6"/>')
add('<ellipse cx="686" cy="436" rx="22" ry="13" fill="#ff8fa8" opacity=".6"/>')
add('<path d="M566 430 Q600 480 634 430 Q600 442 566 430Z" fill="#4a1346" stroke="#4a1346" stroke-width="4" stroke-linejoin="round"/>')
add('<path d="M584 448 Q600 458 616 448 Q600 442 584 448Z" fill="#ff7b95"/>')

# apron bib
add('<path d="M548 482 H652 L672 608 Q600 626 528 608Z" fill="#f7f1e4" stroke="#d8cdb6" stroke-width="3"/>')
add('<path d="M536 480 Q600 506 664 480" fill="none" stroke="#a3201f" stroke-width="9" stroke-linecap="round"/>')
add('<path d="M556 574 H644" stroke="#d8cdb6" stroke-width="3"/>')
add('<g transform="translate(600 535)"><path d="M-22 -4 Q-22 20 0 20 Q22 20 22 -4Z" fill="#c8302a"/><ellipse cx="0" cy="-4" rx="22" ry="5" fill="#f3b24d"/><path d="M-14 -4 q5 -4 9 0 t9 0 t9 0" fill="none" stroke="#fff3b0" stroke-width="2"/></g>')
add('</g>')

# chef hat (toque)
add('<g id="hat">')
add('<circle cx="520" cy="178" r="40" fill="#fbfaf6"/><circle cx="690" cy="182" r="38" fill="#fbfaf6"/>')
add('<circle cx="580" cy="146" r="52" fill="#ffffff"/><circle cx="648" cy="152" r="48" fill="#ffffff"/>')
add('<circle cx="600" cy="188" r="60" fill="#fbfaf6"/>')
add('<rect x="494" y="190" width="212" height="60" rx="8" fill="#fbfaf6"/>')
add('<path d="M538 120 Q545 160 535 205M600 100 Q592 150 604 205M660 112 Q668 160 655 205" fill="none" stroke="#e1ddd2" stroke-width="3" stroke-linecap="round"/>')
add('<path d="M494 232 H706 V252 Q600 262 494 252Z" fill="#c8302a"/>')
add('<path d="M494 232 H706" stroke="#8f1d22" stroke-width="2"/>')
add('<path d="M498 200 Q496 235 500 245" stroke="#e1ddd2" stroke-width="3" fill="none"/>')
add('</g>')

# ---------------------------------------------------------------- front arms (hands over items)
add(arm(knife_arm, 34, 11, side=-1, extra=shadow))
add(arm(rest_arm, 28, 8, side=1, extra=shadow))

# ---------------------------------------------------------------- pot on counter
add('<g id="pot">')
add('<ellipse cx="270" cy="682" rx="130" ry="12" fill="#00000040"/>')
add('<path d="M150 548 V660 Q150 680 190 681 H350 Q390 680 390 660 V548Z" fill="url(#steel)"/>')
add('<rect x="150" y="595" width="240" height="6" fill="#00000018"/>')
add('<ellipse cx="270" cy="548" rx="120" ry="27" fill="#d7dde5" stroke="#7c8593" stroke-width="3"/>')
add('<ellipse cx="270" cy="550" rx="108" ry="21" fill="url(#broth)"/>')
add('<path d="M190 548q10 -5 20 0M230 556q10 -5 20 0M300 545q10 -5 20 0M340 554q9 -5 18 0" fill="none" stroke="#f6d27a" stroke-width="3" stroke-linecap="round" opacity=".8"/>')
# handles
add('<path d="M150 580 H128 Q118 580 118 590 V596 Q118 606 128 606 H150" fill="none" stroke="#5f6a78" stroke-width="7"/>')
add('<path d="M390 580 H412 Q422 580 422 590 V596 Q422 606 412 606 H390" fill="none" stroke="#5f6a78" stroke-width="7"/>')
add('</g>')
# re-draw ladle scoop front over broth + hand grips
add('<path d="M322 548 Q324 580 350 580 Q374 578 374 552 Z" fill="#aab3bf" stroke="#5f6a78" stroke-width="3"/>')
add('<ellipse cx="348" cy="550" rx="26" ry="6" fill="#d89a3e"/>')
add('<path d="M346 560 L440 516" stroke="#6b3f24" stroke-width="8" stroke-linecap="round"/>')

# ---------------------------------------------------------------- cutting board with chashu & scallions
add('<g id="board">')
add('<path d="M930 652 H1110 L1118 688 H922Z" fill="#d9a66a" stroke="#8a5a2d" stroke-width="3" stroke-linejoin="round"/>')
for (x, y) in [(960, 668), (992, 672), (1024, 668)]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="18" ry="8" fill="#b9684a"/><ellipse cx="{x}" cy="{y}" rx="12" ry="4.5" fill="#e3a07f"/>')
for (x, y) in [(1060, 668), (1074, 672), (1088, 666), (1066, 676), (1082, 678)]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="3" fill="#5fae45"/>')
add('</g>')
# knife drawn above board (re-draw blade tip on board) - hand over handle

# ---------------------------------------------------------------- the ramen bowl held aloft
add('<g id="bowl">')
add('<ellipse cx="852" cy="512" rx="100" ry="14" fill="#00000030" filter="url(#blur2)"/>')
add('<rect x="810" y="512" width="84" height="16" rx="5" fill="#8f1d22"/>')
add('<path d="M742 426 Q744 522 852 526 Q960 522 962 426Z" fill="#f8f4ea" stroke="#d3c9b3" stroke-width="3"/>')
add('<path d="M746 450 Q852 480 958 450" fill="none" stroke="#c8302a" stroke-width="8"/>')
# wave pattern
add('<path d="M768 490 q10 -14 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="#2c4aa0" stroke-width="3" opacity=".75"/>')
add('<ellipse cx="852" cy="426" rx="110" ry="24" fill="#f8f4ea" stroke="#d3c9b3" stroke-width="3"/>')
add('<ellipse cx="852" cy="428" rx="100" ry="19" fill="url(#broth)"/>')
# noodles
for i, x in enumerate(range(770, 940, 14)):
    add(f'<path d="M{x} {424 + (i%3)*3} q8 -7 16 0 t16 2" fill="none" stroke="#f6dc88" stroke-width="3.5" stroke-linecap="round"/>')
# toppings
add('<ellipse cx="806" cy="424" rx="19" ry="8" fill="#fff6ec" stroke="#e5d6bf" stroke-width="2"/><path d="M796 424q5 -5 10 0t10 0" fill="none" stroke="#ec6d8c" stroke-width="2.5"/>')
add('<ellipse cx="885" cy="418" rx="24" ry="10" fill="#b9684a"/><ellipse cx="885" cy="418" rx="17" ry="6.5" fill="#e3a07f"/>')
add('<ellipse cx="868" cy="432" rx="22" ry="9" fill="#a85a40"/><ellipse cx="868" cy="432" rx="15" ry="5.5" fill="#d99372"/>')
add('<ellipse cx="836" cy="433" rx="16" ry="8" fill="#fffaf0" stroke="#e5d6bf" stroke-width="1.5"/><ellipse cx="836" cy="433" rx="7" ry="4" fill="#f5a623"/>')
add('<path d="M918 428 L926 372 L944 374 L938 430Z" fill="#1d3a2a"/><path d="M924 410H940M925 394H941" stroke="#3f6b4f" stroke-width="2"/>')
for (x, y) in [(790, 436), (812, 440), (900, 434), (856, 420), (827, 418), (848, 440)]:
    add(f'<ellipse cx="{x}" cy="{y}" rx="4.5" ry="2.8" fill="#5fae45"/><ellipse cx="{x}" cy="{y}" rx="2" ry="1.1" fill="#d7f2b0"/>')
# noodles held up by chopsticks
for k, off in enumerate((-8, 0, 8)):
    add(f'<path d="M{858+off} 388 C{850+off} 405 {868+off} 410 {860+off} 428" fill="none" stroke="#f6dc88" stroke-width="3.5" stroke-linecap="round"/>')
add('</g>')

# the bowl arm's fingertip curling around the bowl
add(arm([(878, 534), (898, 510), (904, 488), (894, 470)], 18, 8, side=1, extra=shadow))

# chopstick arm tip over sticks (hand)
add(arm([(808, 281), (826, 266), (842, 270), (846, 284)], 14, 9, side=1, extra=''))

# ---------------------------------------------------------------- steam
def steam(x, y, h, op=0.4, sw=14):
    return (f'<path d="M{x} {y} C{x-26} {y-h*0.3} {x+26} {y-h*0.55} {x} {y-h*0.8} S{x+18} {y-h} {x-4} {y-h-20}" '
            f'fill="none" stroke="#fff" stroke-width="{sw}" stroke-linecap="round" opacity="{op}" filter="url(#blur2)"/>')

add('<g>')
for (x, y, h, op, sw) in [(220, 520, 130, .35, 16), (270, 516, 160, .4, 18), (325, 520, 120, .32, 14), (180, 524, 100, .25, 12)]:
    add(steam(x, y, h, op, sw))
for (x, y, h, op, sw) in [(800, 392, 80, .4, 12), (852, 388, 110, .45, 14), (905, 392, 70, .35, 10)]:
    if x != 852:
        add(steam(x, y, h, op, sw))
add('</g>')

# ---------------------------------------------------------------- counter front
add('<rect x="40" y="692" width="1120" height="208" fill="url(#wood)"/>')
add('<rect x="40" y="692" width="1120" height="208" fill="url(#planks)" opacity=".6"/>')
add('<rect x="40" y="688" width="1120" height="10" fill="#e7b273"/><rect x="40" y="696" width="1120" height="5" fill="#00000030"/>')
# front cloth sign
add('<g>')
add('<rect x="520" y="716" width="160" height="116" rx="6" fill="#a3201f" stroke="#2b1612" stroke-width="4"/>')
add('<circle cx="600" cy="768" r="40" fill="#f4ecdc"/>')
add('<path d="M572 764 Q572 790 600 790 Q628 790 628 764Z" fill="#c8302a"/><ellipse cx="600" cy="764" rx="28" ry="7" fill="#f3b24d"/><path d="M585 764q5 -5 10 0t10 0t10 0" fill="none" stroke="#fff3b0" stroke-width="2"/>')
add('<path d="M580 752q3 -8 0 -14M600 750q3 -8 0 -14M620 752q3 -8 0 -14" fill="none" stroke="#a3201f" stroke-width="3" stroke-linecap="round"/>')
add('<text x="600" y="822" font-family="Helvetica, Arial, sans-serif" font-weight="800" font-size="18" letter-spacing="3" fill="#f4ecdc" text-anchor="middle">TAKO RAMEN</text>')
add('</g>')

# hanging arms over the counter front
add(arm([(496, 560), (484, 620), (472, 650), (500, 705), (478, 760), (440, 800), (418, 788), (428, 770)], 40, 9, side=-1, s_from=0.2, extra='', round_root=True))
add(arm([(706, 560), (718, 620), (736, 650), (708, 706), (726, 764), (770, 800), (792, 786), (780, 768)], 40, 9, side=1, s_from=0.2, extra='', round_root=True))

# ground / floor strip
add('<rect x="0" y="880" width="1200" height="20" fill="#1a1020"/>')
# warm vignette
add('<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>')
add(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
add('</svg>')

os.makedirs(os.path.join(os.path.dirname(__file__), "..", "output"), exist_ok=True)
path = os.path.join(os.path.dirname(__file__), "..", "output", "octopus_ramen_chef.svg")
with open(path, "w") as f:
    f.write("\n".join(out))
print("wrote", path, os.path.getsize(path))
