#!/usr/bin/env python3
"""Awkward robot family portrait — hand-composed SVG, no text."""
import pathlib
out = pathlib.Path("output/awkward-robot-family-portrait.svg")
out.parent.mkdir(exist_ok=True)

s=[]
def add(x): s.append(x)
add('''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img">
<defs>
 <linearGradient id="backdrop" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#7fb3c8"/><stop offset=".55" stop-color="#c9dde6"/><stop offset="1" stop-color="#e8dcc3"/>
 </linearGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b99b78"/><stop offset="1" stop-color="#8a6f52"/></linearGradient>
 <linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8edf0"/><stop offset="1" stop-color="#9aa7ad"/></linearGradient>
 <linearGradient id="copper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f2b27a"/><stop offset="1" stop-color="#b96f3e"/></linearGradient>
 <linearGradient id="teal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7fd1cc"/><stop offset="1" stop-color="#2f7f7a"/></linearGradient>
 <linearGradient id="pink" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6c6d8"/><stop offset="1" stop-color="#c97a9a"/></linearGradient>
 <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe38a"/><stop offset="1" stop-color="#d99a2b"/></linearGradient>
 <radialGradient id="vignette"><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#203038" stop-opacity=".28"/></radialGradient>
 <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>''')

# --- studio backdrop: mottled photo-studio sweep, spotlight, rug ---
add('<rect width="1200" height="900" fill="url(#backdrop)"/>')
for cx,cy,r,o in [(220,180,180,.16),(600,140,240,.14),(980,200,190,.15),(400,340,150,.10),(820,360,170,.10)]:
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" opacity="{o}"/>')
add('<ellipse cx="600" cy="250" rx="430" ry="300" fill="#fff8e0" opacity=".22" filter="url(#soft)"/>')
add('<path d="M0 690 Q600 640 1200 690 L1200 900 L0 900 Z" fill="url(#floor)"/>')
add('<ellipse cx="600" cy="790" rx="470" ry="78" fill="#8f2f3a" opacity=".9"/>')
add('<ellipse cx="600" cy="790" rx="430" ry="64" fill="#a83a46"/>')
add('<ellipse cx="600" cy="790" rx="390" ry="52" fill="none" stroke="#e8c07a" stroke-width="4" stroke-dasharray="14 10" opacity=".8"/>')
add('<ellipse cx="600" cy="828" rx="520" ry="30" fill="#000" opacity=".16" filter="url(#soft)"/>')

def eye(x,y,r=9,look=(0,0),lid=False):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/><circle cx="{x+look[0]}" cy="{y+look[1]}" r="{r*0.55:.1f}" fill="#1d2b33"/>'
        f'<circle cx="{x+look[0]+2}" cy="{y+look[1]-2}" r="{r*0.18:.1f}" fill="#fff"/>')
    if lid: add(f'<path d="M{x-r} {y-2} Q{x} {y-r-4} {x+r} {y-2}" fill="none" stroke="#33424c" stroke-width="3" stroke-linecap="round"/>')
def mouth(x,y,w=34,kind="flat"):
    if kind=="flat": add(f'<path d="M{x-w/2} {y} H{x+w/2}" stroke="#33424c" stroke-width="4" stroke-linecap="round"/>')
    elif kind=="grin": add(f'<path d="M{x-w/2} {y} Q{x} {y+16} {x+w/2} {y}" fill="none" stroke="#33424c" stroke-width="4" stroke-linecap="round"/>')
    elif kind=="o": add(f'<ellipse cx="{x}" cy="{y}" rx="9" ry="12" fill="#33424c"/>')
    elif kind=="grim": add(f'<path d="M{x-w/2} {y+6} l8-8 l8 8 l8-8 l8 8" fill="none" stroke="#33424c" stroke-width="3.5" stroke-linejoin="round"/>')
    elif kind=="smirk": add(f'<path d="M{x-w/2} {y+4} Q{x+6} {y+10} {x+w/2} {y-4}" fill="none" stroke="#33424c" stroke-width="4" stroke-linecap="round"/>')
def antenna(x,y,dx,dy,color="#33424c"):
    add(f'<path d="M{x} {y} L{x+dx} {y+dy}" stroke="{color}" stroke-width="5" stroke-linecap="round"/><circle cx="{x+dx}" cy="{y+dy}" r="8" fill="#ffdf5a" stroke="{color}" stroke-width="2"/>')
def arm(x1,y1,x2,y2,x3,y3,color,w=20):
    add(f'<path d="M{x1} {y1} L{x2} {y2} L{x3} {y3}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{x3}" cy="{y3}" r="{w*0.62:.0f}" fill="{color}"/>')
def leg(x,y,dx,dy,color,w=22):
    add(f'<path d="M{x} {y} L{x+dx} {y+dy}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
        f'<ellipse cx="{x+dx}" cy="{y+dy+8}" rx="24" ry="10" fill="#33424c"/>')

# ============ GRANDMA (left, seated, knitting a wire scarf, asleep-ish) ============
# chair
add('<path d="M92 610 L118 470 M268 610 L242 470 M100 560 H260" stroke="#6b4a2f" stroke-width="14" stroke-linecap="round"/>')
add('<rect x="88" y="452" width="184" height="26" rx="12" fill="#7a5636"/>')
leg(150,600, -18,92, "#7a6a8a"); leg(215,600, 26,88, "#7a6a8a")
add('<rect x="118" y="430" width="124" height="178" rx="34" fill="#9b8bb5" stroke="#5d4e73" stroke-width="5"/>')  # lavender torso
add('<circle cx="180" cy="418" r="10" fill="#ffe38a"/><circle cx="180" cy="452" r="8" fill="#d9d2e8"/>')
add('<rect x="128" y="300" width="104" height="92" rx="26" fill="url(#steel)" stroke="#5d4e73" stroke-width="5"/>')  # head
add('<path d="M128 322 Q180 268 232 322 L232 306 Q180 258 128 306Z" fill="#e8e4f0"/>')  # hair bun hint
add('<circle cx="180" cy="272" r="20" fill="#e8e4f0" stroke="#b9b0cc" stroke-width="3"/>')
add('<path d="M142 344 Q156 336 170 344 M190 344 Q204 336 218 344" stroke="#33424c" stroke-width="4" fill="none" stroke-linecap="round"/>')  # closed happy eyes
mouth(180,372,30,"grin")
antenna(140,302,-16,-22); 
add('<circle cx="248" cy="352" r="7" fill="#c97a9a"/>')  # ear muff / dial
arm(122,470, 66,520, 118,566, "#8d7aa8"); arm(238,470, 288,512, 232,562, "#8d7aa8")
# knitting: two needles + tangled yarn scarf to kid
add('<path d="M118 566 L282 520 M232 562 L96 516" stroke="#d8d8d8" stroke-width="4" stroke-linecap="round"/>')
add('<path d="M118 566 Q190 610 250 560 Q300 600 330 640 Q380 690 430 660" fill="none" stroke="#e2543e" stroke-width="10" stroke-linecap="round"/>')
add('<circle cx="96" cy="640" r="24" fill="#e2543e"/><path d="M76 628 Q96 650 118 632 M78 646 Q98 626 116 648" stroke="#b93a28" stroke-width="3" fill="none"/>')

# ============ DAD (back centre-left, very tall & stiff, arm hovering) ============
leg(392,640,-8,116,"#4a5a66"); leg(452,640,14,116,"#4a5a66")
add('<rect x="352" y="392" width="148" height="258" rx="22" fill="url(#copper)" stroke="#7a4a26" stroke-width="5"/>')
add('<rect x="382" y="430" width="88" height="58" rx="8" fill="#5b3a22"/><circle cx="426" cy="459" r="16" fill="#ffe38a"/><circle cx="426" cy="459" r="7" fill="#b96f3e"/>')  # chest gauge
add('<path d="M370 540 h112 M370 566 h112" stroke="#8a5527" stroke-width="5"/>')
add('<rect x="356" y="238" width="140" height="128" rx="18" fill="url(#steel)" stroke="#6b4a2f" stroke-width="5"/>')
add('<rect x="356" y="238" width="140" height="26" rx="12" fill="#8a5527"/>')  # flat-top hair plate
eye(398,304,11,(0,3)); eye(454,304,11,(0,3))  # staring straight, frozen
add('<path d="M386 282 h28 M438 282 h28" stroke="#33424c" stroke-width="5" stroke-linecap="round"/>')  # raised brows
mouth(426,338,36,"flat")
antenna(426,238,0,-34)
# his arm meant for mum's shoulder — hovers 20px above it, fingers stiff
arm(358,430, 282,398, 268,452, "#b96f3e")
add('<path d="M252 452 h34 M254 466 h30" stroke="#8a5527" stroke-width="4" stroke-linecap="round"/>')
arm(496,430, 560,470, 548,540, "#b96f3e")  # other arm ramrod straight, thumbs-up nobody asked for
add('<path d="M548 540 l4-26 M548 514 l14-8" stroke="#b96f3e" stroke-width="9" stroke-linecap="round"/>')

# ============ MUM (centre, leaning away, holding baby, eye-roll) ============
leg(586,648,-20,108,"#7a4a5e"); leg(640,648,26,104,"#7a4a5e")
add('<path d="M540 420 L688 420 L664 652 L562 652 Z" fill="url(#pink)" stroke="#8a4a66" stroke-width="5" stroke-linejoin="round"/>')  # dress body, leaning
add('<circle cx="614" cy="478" r="12" fill="#fff"/><circle cx="614" cy="520" r="9" fill="#ffe38a"/><circle cx="614" cy="556" r="9" fill="#fff"/>')
add('<g transform="rotate(-7 614 330)"><rect x="556" y="262" width="116" height="104" rx="30" fill="url(#steel)" stroke="#8a4a66" stroke-width="5"/>'
    '<path d="M556 292 Q614 240 672 292 L672 276 Q614 226 556 276Z" fill="#c94f6d"/></g>')  # head tilted away + hair sweep
eye(592,318,10,(-3,-4),lid=True); eye(640,318,10,(-3,-4),lid=True)  # eyes rolled up-left
mouth(616,344,30,"smirk")
add('<path d="M566 366 Q614 388 662 366" stroke="#c9a0b4" stroke-width="4" fill="none"/>')  # necklace
# one arm cradling baby robot, other hand on hip
arm(548,448, 500,520, 566,548, "#c97a9a")
# BABY: tiny, mid-wail / delighted, one arm up, held at mum's side
add('<g transform="rotate(10 566 520)"><rect x="528" y="486" width="76" height="66" rx="20" fill="url(#gold)" stroke="#9a6b1e" stroke-width="4"/>'
    '<rect x="540" y="428" width="52" height="48" rx="14" fill="url(#steel)" stroke="#9a6b1e" stroke-width="4"/>'
    '<circle cx="554" cy="452" r="6" fill="#1d2b33"/><circle cx="578" cy="452" r="6" fill="#1d2b33"/>'
    '<ellipse cx="566" cy="466" rx="7" ry="9" fill="#8a3b2e"/></g>')
add('<path d="M534 500 L506 462" stroke="#d99a2b" stroke-width="11" stroke-linecap="round"/><circle cx="503" cy="458" r="8" fill="#d99a2b"/>')  # baby arm flailing up
add('<path d="M600 520 L632 486" stroke="#d99a2b" stroke-width="11" stroke-linecap="round"/>')
arm(682,448, 736,500, 700,566, "#c97a9a")  # hand-on-hip elbow out

# ============ TEEN (right of centre, slouched, headphones, phone, not looking) ============
leg(782,650,-34,96,"#3e4a3a"); leg(838,646,44,82,"#3e4a3a")  # one foot turned out, bored
add('<path d="M742 452 L874 438 L862 650 L756 650 Z" fill="url(#teal)" stroke="#245c58" stroke-width="5" stroke-linejoin="round"/>')  # slouched hoodie torso
add('<path d="M742 452 Q808 410 874 438 L866 486 Q808 458 750 490Z" fill="#245c58"/>')  # hood
add('<rect x="786" y="540" width="52" height="34" rx="6" fill="#1d2b33"/>')  # pocket
add('<g transform="rotate(9 812 356)"><rect x="758" y="292" width="108" height="98" rx="26" fill="url(#steel)" stroke="#245c58" stroke-width="5"/></g>')
add('<path d="M748 320 Q812 268 876 320 L876 344 Q812 296 748 344Z" fill="#2f7f7a"/>')  # headphone band
add('<rect x="738" y="330" width="24" height="46" rx="10" fill="#1d2b33"/><rect x="862" y="324" width="24" height="46" rx="10" fill="#1d2b33"/>')
eye(790,344,9,(4,5)); eye(836,344,9,(4,5))  # gaze down at phone
mouth(813,372,26,"flat")
add('<path d="M786 326 h20 M826 326 h20" stroke="#33424c" stroke-width="4" stroke-linecap="round"/>')  # flat unimpressed brows
# both arms bent down to phone at waist
arm(750,478, 716,560, 782,576, "#2f7f7a"); arm(868,472, 896,548, 830,576, "#2f7f7a")
add('<rect x="778" y="556" width="58" height="38" rx="7" fill="#141c22" stroke="#7fd1cc" stroke-width="3" transform="rotate(-6 807 575)"/>'
    '<circle cx="820" cy="566" r="4" fill="#7fd1cc" opacity=".8"/>')
# musical / boredom note drifting from headphones
add('<path d="M884 300 q14-8 12-24 M896 276 l16-6 v22" stroke="#5b7a86" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="890" cy="302" r="7" fill="#5b7a86"/><circle cx="906" cy="294" r="7" fill="#5b7a86"/>')

# ============ KID (front right, too close to camera, huge grin, waving, one shoe untied-ish) ============
add('<ellipse cx="1010" cy="842" rx="120" ry="22" fill="#000" opacity=".18" filter="url(#soft)"/>')
leg(972,690,-30,74,"#8a3b2e",26); leg(1048,690,42,64,"#8a3b2e",26)
add('<rect x="936" y="512" width="150" height="184" rx="36" fill="#e2543e" stroke="#8a3b2e" stroke-width="6"/>')  # oversized front body
add('<circle cx="1011" cy="576" r="20" fill="#ffe38a" stroke="#8a3b2e" stroke-width="4"/><circle cx="1011" cy="576" r="8" fill="#e2543e"/>')
add('<circle cx="1011" cy="630" r="10" fill="#fff"/>')
add('<rect x="928" y="356" width="166" height="140" rx="38" fill="url(#steel)" stroke="#8a3b2e" stroke-width="6"/>')  # big head, close to lens
eye(978,420,14,(-2,0)); eye(1044,420,14,(-2,0))
add('<path d="M950 448 Q1011 506 1072 448 Q1011 478 950 448Z" fill="#5b2320"/>')  # huge open grin
add('<path d="M972 462 h22 M1028 462 h22" stroke="#fff" stroke-width="7" stroke-linecap="round"/>')
antenna(970,360,-24,-34); antenna(1052,360,26,-30)
add('<path d="M1011 356 v-26" stroke="#33424c" stroke-width="5"/><circle cx="1011" cy="322" r="10" fill="#e2543e"/>')
# waving arm high, other clutching grandma's runaway yarn
arm(1082,540, 1148,470, 1128,392, "#c94a34",24)
add('<path d="M1128 392 l-12-22 M1136 388 l6-24 M1146 396 l18-16" stroke="#c94a34" stroke-width="8" stroke-linecap="round"/>')
arm(940,548, 872,606, 806,640, "#c94a34",24)
add('<path d="M806 640 Q700 690 560 672 Q470 662 430 660" fill="none" stroke="#e2543e" stroke-width="9" stroke-linecap="round"/>')  # yarn pulled across whole portrait

# dad's dropped spare hand / loose screw + a cat-bot pet peeking behind teen (family pet)
add('<g><ellipse cx="918" cy="742" rx="44" ry="28" fill="#8a97a0" stroke="#4a5a66" stroke-width="4"/>'
    '<circle cx="948" cy="716" r="22" fill="url(#steel)" stroke="#4a5a66" stroke-width="4"/>'
    '<path d="M934 700 l-6-18 l16 10 M956 698 l8-16 l6 18" fill="#8a97a0" stroke="#4a5a66" stroke-width="3"/>'
    '<circle cx="942" cy="714" r="4" fill="#1d2b33"/><circle cx="956" cy="714" r="4" fill="#1d2b33"/>'
    '<path d="M874 742 q-30 4-34-20" fill="none" stroke="#4a5a66" stroke-width="6" stroke-linecap="round"/></g>')

# camera-flash catchlights + vignette (portrait feel)
add('<rect width="1200" height="900" fill="url(#vignette)"/>')
add('</svg>')
out.write_text("\n".join(s), encoding="utf-8")
print(out, out.stat().st_size)
