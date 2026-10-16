"""Generate an SVG illustration: an octopus chef running a ramen yatai booth at night."""
import math
import os
import random

W, H = 1200, 900
random.seed(7)
out = []


def add(s):
    out.append(s)


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def tentacle(pts, w0, w1, fill="url(#skin)", sucker_side=1, suckers=True, n=40):
    """Tapered tentacle along a cubic bezier, with suckers on one side."""
    samples = [bez(*pts, i / n) for i in range(n + 1)]
    left, right, normals = [], [], []
    for i, (x, y) in enumerate(samples):
        a = samples[max(i - 1, 0)]
        b = samples[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * (i / n)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
        normals.append((nx, ny, w))
    tip = samples[-1]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in left)
    d += f" A{w1/2:.1f},{w1/2:.1f} 0 0 1 {right[-1][0]:.1f},{right[-1][1]:.1f}"
    d += " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(right))
    d += f" A{w0/2:.1f},{w0/2:.1f} 0 0 1 {left[0][0]:.1f},{left[0][1]:.1f} Z"
    add(f'<path d="{d}" fill="{fill}" stroke="#5b1f4a" stroke-width="3" stroke-linejoin="round"/>')
    if suckers:
        for i in range(4, n - 1, 4):
            x, y = samples[i]
            nx, ny, w = normals[i]
            r = max(w * 0.42, 2.2)
            sx, sy = x - sucker_side * nx * w * 0.55, y - sucker_side * ny * w * 0.55
            add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" fill="#f7c6c9" stroke="#c46a8a" stroke-width="1.5"/>')
            add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r*0.4:.1f}" fill="#d98aa3"/>')
    return tip


def steam(x, y, h, scale=1.0, delay=0.0, opacity=0.55):
    d = (f"M{x},{y} c{-18*scale},{-h*0.18} {18*scale},{-h*0.32} 0,{-h*0.5} "
         f"s{-18*scale},{-h*0.32} 0,{-h*0.5}")
    add(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{9*scale:.1f}" '
        f'stroke-linecap="round" opacity="{opacity}" filter="url(#soft)">'
        f'<animate attributeName="opacity" values="0;{opacity};0" dur="3s" begin="{delay}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0,10;0,-25" dur="3s" begin="{delay}s" repeatCount="indefinite"/>'
        f'</path>')


# ---------------------------------------------------------------- defs
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#140f33"/><stop offset="0.55" stop-color="#3b2361"/>
  <stop offset="0.85" stop-color="#a24a6b"/><stop offset="1" stop-color="#f08a5d"/>
</linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#ffcf7a" stop-opacity="0.75"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/>
</radialGradient>
<radialGradient id="skin" cx="0.4" cy="0.35" r="0.75">
  <stop offset="0" stop-color="#ff9fb2"/><stop offset="0.6" stop-color="#e5607f"/><stop offset="1" stop-color="#b83a64"/>
</radialGradient>
<radialGradient id="head" cx="0.38" cy="0.3" r="0.8">
  <stop offset="0" stop-color="#ffb3c2"/><stop offset="0.55" stop-color="#ec6a88"/><stop offset="1" stop-color="#a8325c"/>
</radialGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#b9763f"/><stop offset="1" stop-color="#7d4a24"/>
</linearGradient>
<linearGradient id="woodDark" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#6e3d1e"/><stop offset="1" stop-color="#3e2010"/>
</linearGradient>
<linearGradient id="interior" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffd38a"/><stop offset="1" stop-color="#e79a52"/>
</linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6d7480"/><stop offset="0.3" stop-color="#e7ebf0"/>
  <stop offset="0.55" stop-color="#a9b0ba"/><stop offset="1" stop-color="#4c525c"/>
</linearGradient>
<radialGradient id="broth" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#f6c06a"/><stop offset="1" stop-color="#c27a2c"/>
</radialGradient>
<radialGradient id="lantern" cx="0.4" cy="0.4" r="0.7">
  <stop offset="0" stop-color="#ffb070"/><stop offset="0.5" stop-color="#e2392b"/><stop offset="1" stop-color="#8f1a16"/>
</radialGradient>
<linearGradient id="noren" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#1f3f73"/><stop offset="1" stop-color="#14294d"/>
</linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter>
</defs>''')

# ---------------------------------------------------------------- sky & city
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
for _ in range(70):
    x, y = random.uniform(0, W), random.uniform(0, 380)
    r = random.choice([0.8, 1.1, 1.5, 2])
    add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{random.uniform(0.4, 0.9):.2f}"/>')
add('<circle cx="1040" cy="110" r="46" fill="#fff4d6"/><circle cx="1058" cy="98" r="46" fill="#2a1a4e" opacity="0.0"/>')
add('<circle cx="1040" cy="110" r="80" fill="#fff4d6" opacity="0.12"/>')
# distant buildings
x = 0
while x < W:
    bw = random.randint(50, 110)
    bh = random.randint(140, 320)
    add(f'<rect x="{x}" y="{700-bh}" width="{bw}" height="{bh+10}" fill="#24183f"/>')
    for wy in range(700 - bh + 18, 690, 28):
        for wx in range(x + 10, x + bw - 14, 20):
            if random.random() < 0.3:
                add(f'<rect x="{wx}" y="{wy}" width="9" height="13" fill="#ffd27a" opacity="{random.uniform(0.35,0.8):.2f}"/>')
    x += bw + random.randint(0, 12)
# street
add(f'<rect x="0" y="760" width="{W}" height="140" fill="#2c2238"/>')
add(f'<rect x="0" y="760" width="{W}" height="6" fill="#463656"/>')
add('<ellipse cx="600" cy="800" rx="520" ry="40" fill="#ffb661" opacity="0.18" filter="url(#soft)"/>')

# ---------------------------------------------------------------- booth back
add('<ellipse cx="600" cy="460" rx="520" ry="320" fill="url(#glow)"/>')
add('<rect x="190" y="230" width="820" height="400" fill="url(#interior)"/>')
# back shelf with bowls & jars
add('<rect x="220" y="330" width="760" height="12" fill="#8a5129"/>')
for i, bx in enumerate(range(250, 960, 62)):
    if 470 < bx < 740:
        continue
    if i % 3 == 0:
        add(f'<rect x="{bx}" y="292" width="34" height="38" rx="6" fill="#d9ecef" stroke="#7a8f99" stroke-width="2"/>'
            f'<rect x="{bx-2}" y="286" width="38" height="9" rx="3" fill="#c0392b"/>')
    else:
        for k in range(3):
            add(f'<path d="M{bx},{318-k*11} h40 l-6,12 h-28 z" fill="#fbf7ef" stroke="#2a4a7f" stroke-width="2"/>')
# menu tags hanging on back wall
menu_cols = ["#fff8e7", "#ffe9c2", "#fff8e7", "#ffe9c2"]
for i, mx in enumerate([250, 300, 870, 920]):
    add(f'<rect x="{mx}" y="360" width="38" height="96" fill="{menu_cols[i]}" stroke="#a0703f" stroke-width="2"/>')
    for ly in range(372, 446, 14):
        add(f'<rect x="{mx+12}" y="{ly}" width="14" height="6" rx="2" fill="#3a2a1f" opacity="0.75"/>')

# posts
for px in (170, 1010):
    add(f'<rect x="{px}" y="200" width="22" height="580" fill="url(#woodDark)"/>')

# ---------------------------------------------------------------- chef (body behind counter)
# lower tentacles peeking behind (drawn first)
tentacle(((520, 560), (470, 600), (430, 590), (410, 620)), 46, 20, sucker_side=-1)
tentacle(((680, 560), (730, 600), (770, 590), (790, 620)), 46, 20, sucker_side=1)

# mantle / head
add('<g transform="translate(0,-38)">')
add('<path d="M600,250 C720,250 770,340 760,430 C752,500 705,560 600,566 '
    'C495,560 448,500 440,430 C430,340 480,250 600,250 Z" fill="url(#head)" stroke="#5b1f4a" stroke-width="4"/>')
# spots
for (sx, sy, r) in [(520, 330, 10), (690, 320, 13), (705, 370, 7), (500, 380, 7), (650, 290, 8), (548, 296, 6)]:
    add(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#c84874" opacity="0.55"/>')
add('<ellipse cx="545" cy="300" rx="38" ry="22" fill="#fff" opacity="0.28" transform="rotate(-25 545 300)"/>')

# hachimaki headband
add('<path d="M447,372 C520,350 680,350 754,372 L752,402 C680,380 520,380 449,402 Z" '
    'fill="#fbfbfb" stroke="#5b1f4a" stroke-width="3"/>')
add('<path d="M470,368 C540,354 660,354 730,368" fill="none" stroke="#d6d6d6" stroke-width="3"/>')
# knot & tails on the right side
add('<circle cx="752" cy="386" r="13" fill="#fbfbfb" stroke="#5b1f4a" stroke-width="3"/>')
add('<path d="M760,380 C790,360 810,350 832,356 C815,370 800,382 764,392 Z" fill="#fbfbfb" stroke="#5b1f4a" stroke-width="3"/>')
add('<path d="M762,394 C795,400 812,414 826,432 C800,428 784,418 758,402 Z" fill="#fbfbfb" stroke="#5b1f4a" stroke-width="3"/>')
# red rising-sun dot on band
add('<circle cx="600" cy="378" r="11" fill="#d7263d"/>')

# face
for ex in (548, 652):
    add(f'<ellipse cx="{ex}" cy="455" rx="30" ry="34" fill="#fff" stroke="#5b1f4a" stroke-width="3"/>')
    add(f'<ellipse cx="{ex+4}" cy="462" rx="17" ry="21" fill="#2b1633"/>')
    add(f'<circle cx="{ex+10}" cy="452" r="7" fill="#fff"/>')
    add(f'<circle cx="{ex-2}" cy="472" r="3" fill="#fff"/>')
# eyebrows (focused, happy)
add('<path d="M520,412 Q548,400 574,414" fill="none" stroke="#5b1f4a" stroke-width="5" stroke-linecap="round"/>')
add('<path d="M626,414 Q652,400 680,412" fill="none" stroke="#5b1f4a" stroke-width="5" stroke-linecap="round"/>')
# cheeks
add('<ellipse cx="508" cy="506" rx="20" ry="11" fill="#ff7f9a" opacity="0.8"/>')
add('<ellipse cx="692" cy="506" rx="20" ry="11" fill="#ff7f9a" opacity="0.8"/>')
# mouth: puckered octopus smile
add('<path d="M578,510 Q600,534 622,510" fill="#7a1f3d" stroke="#5b1f4a" stroke-width="4" stroke-linecap="round"/>')
add('<path d="M590,519 Q600,527 610,519" fill="#ff8fa6"/>')

add('</g>')

# ---------------------------------------------------------------- counter-top tentacles (behind counter edge)
# far-left: stirring the stock pot with a ladle
tip = tentacle(((470, 520), (400, 520), (360, 470), (325, 455)), 50, 18, sucker_side=1)
add('<g transform="rotate(-8 322 455)">'
    '<rect x="316" y="410" width="10" height="150" rx="5" fill="#c9ced6" stroke="#4c525c" stroke-width="2"/></g>')
tentacle(((330, 470), (322, 455), (310, 446), (300, 452)), 14, 8, suckers=False)

# ---------------------------------------------------------------- counter
add('<rect x="150" y="610" width="900" height="30" rx="6" fill="url(#wood)" stroke="#4a2814" stroke-width="3"/>')
add('<rect x="150" y="610" width="900" height="6" rx="3" fill="#e0a368" opacity="0.7"/>')
add('<rect x="175" y="640" width="850" height="140" fill="url(#woodDark)" stroke="#2c160a" stroke-width="3"/>')
for px in range(205, 1000, 55):
    add(f'<line x1="{px}" y1="645" x2="{px}" y2="775" stroke="#2c160a" stroke-width="2" opacity="0.55"/>')
# wheels of the cart
for wx in (250, 950):
    add(f'<circle cx="{wx}" cy="780" r="44" fill="#3a2414" stroke="#1d0f07" stroke-width="5"/>')
    add(f'<circle cx="{wx}" cy="780" r="10" fill="#8a5129"/>')
    for a in range(0, 360, 45):
        r = math.radians(a)
        add(f'<line x1="{wx}" y1="780" x2="{wx+38*math.cos(r):.1f}" y2="{780+38*math.sin(r):.1f}" stroke="#8a5129" stroke-width="4"/>')

# ---------------------------------------------------------------- stock pot (left)
add('<ellipse cx="320" cy="612" rx="96" ry="10" fill="#000" opacity="0.25"/>')
add('<path d="M228,500 L228,600 Q320,625 412,600 L412,500 Z" fill="url(#steel)" stroke="#3b4048" stroke-width="3"/>')
add('<ellipse cx="320" cy="500" rx="92" ry="20" fill="#7d838d" stroke="#3b4048" stroke-width="3"/>')
add('<ellipse cx="320" cy="503" rx="82" ry="14" fill="url(#broth)"/>')
for hx in (222, 418):
    add(f'<rect x="{hx-10}" y="525" width="20" height="10" rx="4" fill="#4c525c"/>')
add('<path d="M262,540 h116" stroke="#fff" stroke-width="3" opacity="0.35"/>')
for i, sx in enumerate((270, 315, 360)):
    steam(sx, 480, 150, 1.1, delay=i * 0.9)

# ---------------------------------------------------------------- noodle strainer tentacle (right)
tentacle(((720, 520), (800, 520), (860, 470), (875, 420)), 50, 18, sucker_side=-1)
# tebo strainer handle and basket with dangling noodles
add('<line x1="880" y1="420" x2="905" y2="500" stroke="#9a6a3a" stroke-width="9" stroke-linecap="round"/>')
add('<path d="M884,500 L932,500 L922,548 Q908,560 894,548 Z" fill="#c9ced6" stroke="#4c525c" stroke-width="3"/>')
for gx in range(890, 930, 8):
    add(f'<line x1="{gx}" y1="503" x2="{gx+2}" y2="550" stroke="#6d7480" stroke-width="1.2"/>')
for i, nx in enumerate(range(896, 924, 5)):
    ln = 40 + (i * 13) % 30
    add(f'<path d="M{nx},548 q{6 if i%2 else -6},{ln/3} 0,{ln*2/3} t0,{ln/3}" fill="none" stroke="#f3d27a" stroke-width="3.5" stroke-linecap="round"/>')
tentacle(((875, 432), (885, 418), (898, 420), (900, 432)), 15, 8, suckers=False)
# drip water
add('<circle cx="912" cy="610" r="3" fill="#bfe6ff"/><circle cx="902" cy="596" r="2.5" fill="#bfe6ff"/>')

# ---------------------------------------------------------------- ramen bowl (center front)
add('<g transform="translate(600,612) scale(0.82) translate(-600,-612)">')
add('<ellipse cx="600" cy="612" rx="140" ry="12" fill="#000" opacity="0.3"/>')
add('<path d="M465,540 Q470,610 560,618 L640,618 Q730,610 735,540 Z" fill="#c8372d" stroke="#4a1410" stroke-width="3"/>')
# bowl pattern (raimon-like band)
add('<path d="M478,560 Q600,575 722,560" fill="none" stroke="#f3e2c2" stroke-width="6"/>')
for k in range(9):
    bx = 500 + k * 25
    add(f'<path d="M{bx},565 h8 v-6 h8 v6" fill="none" stroke="#7a1a12" stroke-width="2"/>')
add('<ellipse cx="600" cy="540" rx="135" ry="26" fill="#f3e2c2" stroke="#4a1410" stroke-width="3"/>')
add('<ellipse cx="600" cy="542" rx="124" ry="20" fill="url(#broth)"/>')
# noodles swirl
for k in range(7):
    y = 534 + k * 3
    add(f'<path d="M{510+k*4},{y} q20,-8 40,0 t40,0 t40,0 t40,0" fill="none" stroke="#f7d985" stroke-width="3" opacity="0.9"/>')
# chashu
add('<ellipse cx="560" cy="534" rx="30" ry="13" fill="#b5683a" stroke="#5a2c12" stroke-width="2.5"/>')
add('<ellipse cx="560" cy="534" rx="18" ry="7" fill="#e2a678" opacity="0.8"/>')
# egg half
add('<ellipse cx="640" cy="532" rx="22" ry="12" fill="#fffaf0" stroke="#8a6a3a" stroke-width="2"/>')
add('<ellipse cx="642" cy="532" rx="11" ry="7" fill="#f5a623"/>')
# naruto
add('<ellipse cx="605" cy="547" rx="16" ry="8" fill="#fff" stroke="#d95b7a" stroke-width="2"/>')
add('<path d="M597,547 q4,-5 8,0 t8,0" fill="none" stroke="#e74c78" stroke-width="2.5"/>')
# nori
add('<path d="M680,512 L712,520 L704,548 L674,540 Z" fill="#1d3b2a" stroke="#0c1f14" stroke-width="2"/>')
# scallions
for (gx, gy) in [(585, 528), (595, 535), (622, 545), (575, 545), (660, 545), (530, 545), (615, 527)]:
    add(f'<ellipse cx="{gx}" cy="{gy}" rx="4" ry="3" fill="#7dc95e" stroke="#3f7a2a" stroke-width="1"/>')
for i, sx in enumerate((560, 605, 650)):
    steam(sx, 515, 120, 0.9, delay=0.4 + i * 0.8, opacity=0.5)

# ---------------------------------------------------------------- tentacle with chopsticks, sprinkling over bowl
tentacle(((640, 560), (640, 600), (690, 600), (700, 585)), 40, 16, sucker_side=1)
add('<line x1="698" y1="582" x2="655" y2="520" stroke="#e8c48a" stroke-width="5" stroke-linecap="round"/>')
add('<line x1="704" y1="584" x2="668" y2="517" stroke="#d6ad6c" stroke-width="5" stroke-linecap="round"/>')
# tentacle presenting the bowl (left side, curled under bowl rim)
tentacle(((560, 560), (560, 605), (505, 605), (480, 580)), 40, 14, sucker_side=-1)

add('</g>')

# ---------------------------------------------------------------- counter props
# chopstick holder + condiments (right)
add('<g transform="translate(-40,0)">')
add('<rect x="770" y="560" width="34" height="52" rx="4" fill="#3d2a1a" stroke="#1d120a" stroke-width="2"/>')
for k in range(6):
    add(f'<line x1="{775+k*5}" y1="562" x2="{773+k*6}" y2="528" stroke="#e8c48a" stroke-width="3"/>')
add('<path d="M822,612 v-40 q0,-12 12,-12 h4 v-12 h10 v12 h4 q12,0 12,12 v40 z" fill="#2d1a10" stroke="#120a05" stroke-width="2"/>')
add('<rect x="826" y="580" width="34" height="18" fill="#f2e3c4"/>')
add('<path d="M875,612 v-34 q0,-10 10,-10 h14 q10,0 10,10 v34 z" fill="#c0392b" stroke="#5a1410" stroke-width="2"/>')
add('<rect x="879" y="560" width="26" height="10" rx="3" fill="#e2e2e2"/>')
add('</g>')
# gyoza plate (left)
add('<ellipse cx="460" cy="608" rx="48" ry="9" fill="#f6f2ea" stroke="#2a4a7f" stroke-width="2"/>')
for k in range(4):
    gx = 430 + k * 20
    add(f'<path d="M{gx-12},604 q12,-22 24,0 z" fill="#f2c46d" stroke="#9a6a2a" stroke-width="1.5"/>')

# ---------------------------------------------------------------- roof & noren (foreground top)
add('<path d="M90,230 L600,120 L1110,230 L1080,248 L120,248 Z" fill="#5a2a14" stroke="#2c140a" stroke-width="4"/>')
for k in range(0, 21):
    x0 = 120 + k * 48
    add(f'<path d="M{x0},248 L{600 + (x0-600)*0.15:.0f},135" stroke="#2c140a" stroke-width="2" opacity="0.45"/>')
add('<rect x="110" y="240" width="980" height="18" fill="#8a3b1c" stroke="#2c140a" stroke-width="3"/>')
add('<rect x="180" y="258" width="840" height="12" fill="#3e2010"/>')
# noren curtain panels
panels = 6
pw = 840 / panels
for i in range(panels):
    x0 = 180 + i * pw + 2
    sway = 4 if i % 2 else -4
    add(f'<path d="M{x0:.1f},268 h{pw-4:.1f} l{sway},54 h{-(pw-4):.1f} z" fill="url(#noren)" stroke="#0d1a33" stroke-width="2"/>')
    add(f'<path d="M{x0+4:.1f},316 h{pw-12:.1f}" stroke="#f3e2c2" stroke-width="2" opacity="0.6"/>')
# emblems on noren: bowl, chopsticks, octopus
cx_list = [180 + pw * (i + 0.5) for i in range(panels)]
for i, cx in enumerate(cx_list):
    cy = 294
    if i in (0, 5):
        add(f'<circle cx="{cx:.0f}" cy="{cy}" r="22" fill="none" stroke="#f3e2c2" stroke-width="3"/>')
        add(f'<path d="M{cx-14:.0f},{cy-2} q14,20 28,0 z" fill="#f3e2c2"/>')
        add(f'<line x1="{cx-6:.0f}" y1="{cy-16}" x2="{cx+10:.0f}" y2="{cy-2}" stroke="#f3e2c2" stroke-width="2.5"/>')
        add(f'<line x1="{cx-1:.0f}" y1="{cy-18}" x2="{cx+14:.0f}" y2="{cy-4}" stroke="#f3e2c2" stroke-width="2.5"/>')
    elif i in (1, 4):
        # steaming bowl
        add(f'<path d="M{cx-22:.0f},{cy} q22,30 44,0 z" fill="#f3e2c2"/>')
        for s in (-10, 0, 10):
            add(f'<path d="M{cx+s:.0f},{cy-6} q-5,-7 0,-14 t0,-12" fill="none" stroke="#f3e2c2" stroke-width="2.5" stroke-linecap="round"/>')
    else:
        # tiny octopus mascot
        add(f'<path d="M{cx-16:.0f},{cy+4} q0,-26 16,-26 q16,0 16,26 z" fill="#f3e2c2"/>')
        for t in range(5):
            tx = cx - 16 + t * 8
            add(f'<path d="M{tx:.0f},{cy+2} q-3,10 2,14" fill="none" stroke="#f3e2c2" stroke-width="3" stroke-linecap="round"/>')
        add(f'<circle cx="{cx-5:.0f}" cy="{cy-8}" r="2.5" fill="#1f3f73"/><circle cx="{cx+5:.0f}" cy="{cy-8}" r="2.5" fill="#1f3f73"/>')
# sign board on roof
add('<rect x="470" y="168" width="260" height="62" rx="8" fill="#f3e2c2" stroke="#2c140a" stroke-width="4"/>')
add('<rect x="480" y="176" width="240" height="46" rx="5" fill="none" stroke="#c0392b" stroke-width="2"/>')
add('<text x="600" y="212" text-anchor="middle" font-family="Georgia, \'Times New Roman\', serif" '
    'font-size="27" font-weight="bold" fill="#c0392b" letter-spacing="3">TAKO RAMEN</text>')

# ---------------------------------------------------------------- lanterns
for lx in (140, 1060):
    add(f'<ellipse cx="{lx}" cy="330" rx="80" ry="80" fill="url(#glow)" opacity="0.8"/>')
    add(f'<line x1="{lx}" y1="252" x2="{lx}" y2="272" stroke="#222" stroke-width="3"/>')
    add(f'<rect x="{lx-22}" y="270" width="44" height="10" rx="2" fill="#1c1c1c"/>')
    add(f'<ellipse cx="{lx}" cy="330" rx="40" ry="52" fill="url(#lantern)" stroke="#5a0f0c" stroke-width="2"/>')
    for k in (-26, -13, 0, 13, 26):
        ry = 52 * math.sqrt(max(0, 1 - (k / 52) ** 2))
        add(f'<ellipse cx="{lx}" cy="{330+k}" rx="{40*math.sqrt(1-(k/52)**2):.1f}" ry="3" fill="none" stroke="#7a1410" stroke-width="1.2" opacity="0.6"/>')
    add(f'<rect x="{lx-22}" y="380" width="44" height="10" rx="2" fill="#1c1c1c"/>')
    add(f'<line x1="{lx}" y1="390" x2="{lx}" y2="412" stroke="#e7b84a" stroke-width="3"/>')
    add(f'<path d="M{lx-6},412 h12 l-2,14 h-8 z" fill="#e7b84a"/>')
    # a little glyph: bowl
    add(f'<path d="M{lx-14},{332} q14,18 28,0 z" fill="#2a0806" opacity="0.75"/>')

# ---------------------------------------------------------------- stools in front
for sx in (420, 780):
    add(f'<rect x="{sx-6}" y="760" width="12" height="90" fill="#3b2a20"/>')
    add(f'<ellipse cx="{sx}" cy="758" rx="52" ry="14" fill="#c0392b" stroke="#4a1410" stroke-width="3"/>')
    add(f'<ellipse cx="{sx}" cy="853" rx="40" ry="7" fill="#000" opacity="0.35"/>')

add('</svg>')

os.makedirs(os.path.join(os.path.dirname(__file__), "..", "output"), exist_ok=True)
path = os.path.join(os.path.dirname(__file__), "..", "output", "octopus_chef_ramen.svg")
with open(path, "w") as f:
    f.write("\n".join(out))
print("wrote", os.path.normpath(path), os.path.getsize(path), "bytes")
