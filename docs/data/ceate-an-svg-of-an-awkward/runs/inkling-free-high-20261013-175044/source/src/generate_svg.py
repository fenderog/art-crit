#!/usr/bin/env python3
"""Generate an awkward robot family portrait SVG."""

SVG_WIDTH = 1000
SVG_HEIGHT = 780

def rect(x, y, w, h, fill, stroke="#222", sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{min(8, w/4)}" ry="{min(8, h/4)}"/>'

def circle(cx, cy, r, fill, stroke="#222", sw=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def eye(cx, cy, r, color="#333", pupil_fill="#1a1a2e"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" stroke="#222" stroke-width="1"/>' + \
           f'<circle cx="{cx}" cy="{cy}" r="{r*0.35}" fill="{pupil_fill}"/>'

def line_path(points, stroke="#444", sw=3, fill="none"):
    d = "M" + " L".join(f"{p[0]},{p[1]}" for p in points)
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'

def polygon(points, fill, stroke="#222", sw=2):
    pts = " ".join(f"{p[0]},{p[1]}" for p in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def antenna(cx, cy, h, color="#bfa15f"):
    return f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-h}" stroke="{color}" stroke-width="4" stroke-linecap="round"/><circle cx="{cx}" cy="{cy-h}" r="6" fill="#e8a84a" stroke="#222" stroke-width="1.5"/>'

# Background curtain / backdrop
def backdrop():
    return f'<rect x="0" y="0" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="#1a1525"/><rect x="50" y="40" width="900" height="700" fill="#232038" stroke="#bfa15f" stroke-width="4" rx="12"/>'

# Individual robot functions

def robot_tall_dad(x, y, scale=1.0):
    """Tall, stoic rectangular dad robot. Too rigid, avoids eye contact."""
    s = scale
    # Body (tall rectangle)
    body = rect(x, y, 140*s, 260*s, "#4a5568", sw=3)
    # Head (square, tilted slightly awkward)
    head = rect(x+30*s, y-65*s, 80*s, 80*s, "#6b7b8c", sw=3)
    # Eyes: looking away to the right
    eyes = eye(x+55*s, y-30*s, 10*s) + eye(x+85*s, y-30*s, 10*s)
    # Antenna
    ant = antenna(x+70*s, y-105*s, 35*s)
    # Mouth: flat line (stoic)
    mouth = line_path([(x+45*s, y-5*s), (x+95*s, y-5*s)], stroke="#334155", sw=4)
    # Shoulders / arms stiff at sides
    arms = rect(x-10*s, y+60*s, 22*s, 130*s, "#556677", sw=2)
    # Right arm bent awkwardly outward
    arm_r = polygon([(x+138*s, y+70*s), (x+170*s, y+110*s), (x+160*s, y+130*s), (x+130*s, y+90*s)], "#556677", sw=2)
    # Legs straight
    legs = rect(x+45*s, y+250*s, 22*s, 90*s, "#3a4a5c", sw=2) + rect(x+73*s, y+250*s, 22*s, 90*s, "#3a4a5c", sw=2)
    # Small detail: chest panel
    panel = rect(x+55*s, y+110*s, 30*s, 40*s, "#2d3748", sw=2)
    # Buttons
    btns = circle(x+65*s, y+130*s, 4*s, "#bfa15f") + circle(x+65*s, y+145*s, 4*s, "#bfa15f")
    return body + head + eyes + ant + mouth + arms + arm_r + legs + panel + btns

def robot_round_mom(x, y, scale=1.0):
    """Round mother robot, warm colors, leaning in too close."""
    s = scale
    # Round body
    body = circle(x+60*s, y+180*s, 100*s, "#b87a5a", sw=3)
    # Head (oval, tilted toward dad)
    head = circle(x+60*s, y+70*s, 75*s, "#d4956a", sw=3)
    # Eyes: warm, looking at dad
    eyes = eye(x+42*s, y+60*s, 9*s) + eye(x+78*s, y+60*s, 9*s)
    # Smile curved (warm)
    smile = f'<path d="M {x+48*s} {y+78*s} Q {x+60*s} {y+90*s} {x+72*s} {y+78*s}" fill="none" stroke="#8a4b2e" stroke-width="3" stroke-linecap="round"/>'
    # Hair / decorative top ring
    hair = f'<circle cx="{x+60*s}" cy="{y+25*s}" r="{28*s}" fill="#8a4b2e" stroke="#5c2e1a" stroke-width="3"/>'
    # Little bow detail on hair
    bow = polygon([(x+48*s, y+18*s), (x+38*s, y+22*s), (x+48*s, y+35*s), (x+58*s, y+28*s), (x+48*s, y+45*s), (x+72*s, y+35*s), (x+58*s, y+20*s), (x+50*s, y+28*s)], "#e8a84a", sw=1)
    # Left arm reaching toward dad (awkward lean)
    arm_l = polygon([(x+20*s, y+150*s), (x-10*s, y+190*s), (x+15*s, y+210*s), (x+35*s, y+170*s)], "#c97a5a", sw=2)
    # Right arm at hip
    arm_r = rect(x+145*s, y+150*s, 25*s, 70*s, "#c97a5a", sw=2)
    # Small decorative circle on chest
    chest_dec = circle(x+60*s, y+180*s, 18*s, "#a05a3a", sw=2)
    # Legs hidden mostly behind body
    legs = rect(x+40*s, y+270*s, 18*s, 60*s, "#8a4b2e", sw=2) + rect(x+82*s, y+270*s, 18*s, 60*s, "#8a4b2e", sw=2)
    return body + head + eyes + smile + hair + bow + arm_l + arm_r + chest_dec + legs

def robot_teen(x, y, scale=1.0):
    """Teen robot, slouching, headphones, disinterested, leaning away."""
    s = scale
    # Slouch body (tilted rectangle)
    body = polygon([(x+35*s, y+140*s), (x+115*s, y+130*s), (x+100*s, y+270*s), (x+30*s, y+260*s)], "#5a6a7a", sw=3)
    # Head tilted down away
    head = circle(x+65*s, y+50*s, 60*s, "#708090", sw=3)
    # Eyes: half-closed / bored
    eyes = f'<ellipse cx="{x+50*s}" cy="{y+55*s}" rx="{8*s}" ry="{4*s}" fill="#ddd" stroke="#222" stroke-width="1"/>' + \
           f'<ellipse cx="{x+80*s}" cy="{y+55*s}" rx="{8*s}" ry="{4*s}" fill="#ddd" stroke="#222" stroke-width="1"/>'
    # Headphones (big, ignoring everyone)
    phones = f'<path d="M {x+15*s} {y+45*s} Q {x+5*s} {y+20*s} {x+40*s} {y+5*s} L {x+65*s} {y+15*s}" fill="none" stroke="#333" stroke-width="8" stroke-linecap="round"/>' + \
             f'<rect x="{x+8*s}" y="{y+25*s}" width="{16*s}" height="{35*s}" rx="{8*s}" fill="#333" stroke="#222" stroke-width="2"/>' + \
             f'<rect x="{x+86*s}" y="{y+25*s}" width="{16*s}" height="{35*s}" rx="{8*s}" fill="#333" stroke="#222" stroke-width="2"/>'
    # Frown mouth (slight downward)
    mouth = f'<path d="M {x+52*s} {y+72*s} Q {x+65*s} {y+78*s} {x+78*s} {y+72*s}" fill="none" stroke="#222" stroke-width="3" stroke-linecap="round"/>'
    # Hoodie hood pulled up
    hood = polygon([(x+35*s, y+30*s), (x+95*s, y+30*s), (x+110*s, y+55*s), (x+20*s, y+55*s)], "#4a5a6a", sw=2)
    # Arms crossed defensively
    arm_cross = polygon([(x+30*s, y+160*s), (x+110*s, y+170*s), (x+100*s, y+210*s), (x+40*s, y+200*s)], "#4a5a6a", sw=2)
    # Legs crossed awkwardly
    legs = polygon([(x+40*s, y+270*s), (x+60*s, y+260*s), (x+80*s, y+320*s), (x+60*s, y+330*s)], "#3a4a5c", sw=2)
    # Small antenna bent
    bent_ant = f'<line x1="{x+85*s}" y1="{y-10*s}" x2="{x+100*s}" y2="{y-30*s}" stroke="#bfa15f" stroke-width="3" stroke-linecap="round"/>' + \
               f'<circle cx="{x+100*s}" cy="{y-30*s}" r="{5*s}" fill="#e8a84a" stroke="#222" stroke-width="1"/>'
    return body + head + eyes + mouth + phones + hood + arm_cross + legs + bent_ant

def robot_small_kid(x, y, scale=1.0):
    """Small child robot, too close to camera, awkward oversized head, waving clumsily."""
    s = scale
    # Small body
    body = rect(x, y+110*s, 70*s, 90*s, "#d4a855", sw=2)
    # Huge head (disproportionate, awkward)
    head = circle(x+35*s, y+40*s, 65*s, "#e8b070", sw=3)
    # Very big excited eyes
    eyes = circle(x+20*s, y+35*s, 12*s, "#fff", sw=2) + circle(x+50*s, y+35*s, 12*s, "#fff", sw=2)
    # Big open mouth (too enthusiastic)
    mouth = f'<ellipse cx="{x+35*s}" cy="{y+60*s}" rx="{18*s}" ry="{14*s}" fill="#8a4b2e" stroke="#5c2e1a" stroke-width="2"/>'
    # Small antenna with star
    ant = antenna(x+35*s, y-15*s, 30*s)
    star = f'<polygon points="{x+35*s},{y-45*s} {x+38*s},{y-39*s} {x+44*s},{y-39*s} {x+40*s},{y-34*s} {x+42*s},{y-28*s} {x+35*s},{y-33*s} {x+28*s},{y-28*s} {x+30*s},{y-34*s}" fill="#e8a84a" stroke="#222" stroke-width="1"/>'
    # One arm waving high (awkward angle)
    arm_wave = polygon([(x+60*s, y+100*s), (x+95*s, y+60*s), (x+100*s, y+80*s), (x+70*s, y+115*s)], "#c98a50", sw=2)
    # Little hand circle at end
    hand = circle(x+95*s, y+65*s, 10*s, "#e8b070", sw=2)
    # Short legs
    legs = rect(x+15*s, y+190*s, 18*s, 50*s, "#b07a40", sw=2) + rect(x+47*s, y+190*s, 18*s, 50*s, "#b07a40", sw=2)
    # Small decorative circle on body
    dec = circle(x+35*s, y+140*s, 10*s, "#8a4b2e", sw=1)
    return body + head + eyes + mouth + ant + star + arm_wave + hand + legs + dec

def robot_elder(x, y, scale=1.0):
    """Elder robot, hunched, small, slightly separated, faded colors."""
    s = scale
    # Hunched body (curved top)
    body = polygon([(x+30*s, y+120*s), (x+120*s, y+130*s), (x+110*s, y+240*s), (x+40*s, y+230*s)], "#8899aa", sw=3)
    # Head small, tilted down
    head = circle(x+75*s, y+50*s, 45*s, "#aab0bc", sw=3)
    # Tired eyes (small, downcast)
    eyes = f'<ellipse cx="{x+65*s}" cy="{y+55*s}" rx="{6*s}" ry="{3*s}" fill="#6688aa" stroke="#334455" stroke-width="1"/>' + \
           f'<ellipse cx="{x+85*s}" cy="{y+55*s}" rx="{6*s}" ry="{3*s}" fill="#6688aa" stroke="#334455" stroke-width="1"/>'
    # Small sad mouth
    mouth = f'<path d="M {x+65*s} {y+68*s} Q {x+75*s} {y+72*s} {x+85*s} {y+68*s}" fill="none" stroke="#556677" stroke-width="2" stroke-linecap="round"/>'
    # Small cap/hat
    cap = f'<rect x="{x+55*s}" y="{y+15*s}" width="{40*s}" height="{18*s}" rx="{10*s}" fill="#556677" stroke="#334455" stroke-width="2"/>'
    # Cane (holds it, slightly bent posture)
    cane = f'<rect x="{x+110*s}" y="{y+80*s}" width="{5*s}" height="{130*s}" rx="{2*s}" fill="#7a5a3a" stroke="#5a3a20" stroke-width="1"/>' + \
           f'<circle cx="{x+112*s}" cy="{y+190*s}" r="{8*s}" fill="#8a6a40" stroke="#5a3a20" stroke-width="1.5"/>'
    # Small hunched shoulders
    shoulders = circle(x+30*s, y+110*s, 20*s, "#7788aa", sw=2) + circle(x+120*s, y+110*s, 20*s, "#7788aa", sw=2)
    # Short legs, one slightly bent
    legs = rect(x+50*s, y+240*s, 16*s, 60*s, "#667788", sw=2) + polygon([(x+80*s, y+240*s), (x+95*s, y+245*s), (x+90*s, y+300*s), (x+75*s, y+295*s)], "#667788", sw=2)
    # Small wire details on body
    wires = line_path([(x+50*s, y+160*s), (x+100*s, y+170*s)], stroke="#556677", sw=2)
    return body + head + eyes + mouth + cap + shoulders + cane + legs + wires

def robot_pet(x, y, scale=0.6):
    """Small pet robot, very small, near feet, awkwardly placed."""
    s = scale
    body = circle(x+35*s, y+70*s, 30*s, "#d48a6a", sw=2)
    head = circle(x+35*s, y+35*s, 25*s, "#e8a070", sw=2)
    # Big curious eyes
    eyes = circle(x+28*s, y+30*s, 6*s, "#fff", sw=1.5) + circle(x+42*s, y+30*s, 6*s, "#fff", sw=1.5)
    # Small nose dot
    nose = circle(x+35*s, y+40*s, 3*s, "#5c2e1a")
    # Tiny antenna
    ant = antenna(x+35*s, y+10*s, 18*s)
    # Little tail sticking out awkwardly behind
    tail = f'<line x1="{x+65*s}" y1="{y+70*s}" x2="{x+85*s}" y2="{y+60*s}" stroke="#b07a40" stroke-width="4" stroke-linecap="round"/>'
    # Tiny legs
    legs = rect(x+25*s, y+95*s, 10*s, 15*s, "#a05a40", sw=1) + rect(x+45*s, y+95*s, 10*s, 15*s, "#a05a40", sw=1)
    return body + head + eyes + nose + ant + tail + legs

# Main SVG generation
parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 780" width="100%" height="100%" style="background:#0d0a14;">')

# Background
def bg():
    return '<rect x="0" y="0" width="1000" height="780" fill="#0d0a14"/>' + \
           '<defs><radialGradient id="vignette" cx="50%" cy="50%" r="70%"><stop offset="0%" stop-color="transparent" stop-opacity="0"/><stop offset="100%" stop-color="#0d0a14" stop-opacity="0.7"/></radialGradient></defs>' + \
           '<rect x="0" y="0" width="1000" height="780" fill="url(#vignette)"/>' + \
           '<rect x="40" y="30" width="920" height="720" fill="#1a1525" stroke="#bfa15f" stroke-width="5" rx="8"/>' + \
           '<rect x="60" y="50" width="880" height="660" fill="#232038" stroke="#c4a86b" stroke-width="1" rx="4"/>'

parts.append(bg())

# Subtle floor shadow
parts.append('<ellipse cx="500" cy="680" rx="420" ry="40" fill="#1a1525" opacity="0.6"/>')

# Family members placed with awkward spacing and poses
# Dad - left, tall, rigid, looking away
parts.append(robot_tall_dad(140, 280, scale=0.95))

# Mom - center-left, leaning in toward dad
parts.append(robot_round_mom(340, 300, scale=0.9))

# Teen - right side, slouching away, headphones
parts.append(robot_teen(620, 240, scale=0.85))

# Elder - far right, slightly apart, hunched
parts.append(robot_elder(780, 340, scale=0.85))

# Small kid - front center-left, too big head, too close, waving
parts.append(robot_small_kid(380, 420, scale=1.0))

# Pet robot - near elder's cane, small
parts.append(robot_pet(860, 620, scale=0.7))

# Some decorative awkward elements: a picture frame hanging crooked on wall
frame = '<rect x="120" y="100" width="140" height="100" fill="#2a2240" stroke="#bfa15f" stroke-width="4" rx="3" transform="rotate(-8 190 150)"/>' + \
        '<rect x="130" y="108" width="120" height="84" fill="#3a3050" stroke="#6b5a7a" stroke-width="2"/>' + \
        '<circle cx="190" cy="140" r="15" fill="#8a6a8a"/>'
parts.append(frame)

# Another crooked frame on right
frame2 = '<rect x="780" y="120" width="130" height="90" fill="#2a2240" stroke="#bfa15f" stroke-width="3" rx="3" transform="rotate(6 845 165)"/>' + \
         '<rect x="790" y="128" width="110" height="74" fill="#3a3050" stroke="#6b5a7a" stroke-width="2"/>' + \
         '<rect x="820" y="145" width="50" height="30" fill="#6a5a6a" rx="2"/>'
parts.append(frame2)

# Awkward family portrait style: a decorative border with some broken lines
parts.append('<line x1="60" y1="720" x2="280" y2="720" stroke="#bfa15f" stroke-width="2" stroke-dasharray="12 6"/>')
parts.append('<line x1="720" y1="720" x2="940" y2="720" stroke="#bfa15f" stroke-width="2" stroke-dasharray="8 8"/>')

# Subtle decorative corner motifs
corner = '<polygon points="60,60 100,60 100,100 60,100" fill="none" stroke="#bfa15f" stroke-width="3"/>'
parts.append(corner)

parts.append('</svg>')

with open("output/awkward_family_portrait.svg", "w") as f:
    f.write("\n".join(parts))

print("SVG written to output/awkward_family_portrait.svg")
