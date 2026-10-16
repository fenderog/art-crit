#!/usr/bin/env python3
"""
forma — generative AI logo
Concept: a pebble-bloom. Four hand-varied organic petals cycle from
pale sand to warm charcoal (generation as growth), leaving a small
negative-space seed at the centre. One detached spore to the north-east
is the thing newly generated. All neutral, warm-stone tones.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT, exist_ok=True)

INK   = "#2B2620"   # warm charcoal
TAUPE = "#7D6F5E"
STONE = "#A99A8B"
SAND  = "#C9BBA6"
PALE  = "#E9E1D3"
PAPER = "#F7F3EC"

FONT = "'Helvetica Neue', Inter, 'Segoe UI', Arial, sans-serif"

# One organic petal, pointing up. Inner tip near centre, rounded pebble
# outer end, apex nudged left and right flank fuller than the left so
# no petal reads as a perfect geometric leaf.
PETAL = (
    "M 0,-7 "
    "C 12,-10 26,-22 28,-38 "
    "C 30,-54 20,-66 4,-67 "
    "C -12,-68 -26,-58 -27,-42 "
    "C -28,-27 -12,-10 0,-7 Z"
)

# angle, scale-x, scale-y, colour-key  (varied like grown, not stamped)
PETALS = [
    (  0, 1.00, 1.00, "sand"),    # top    — lightest, newest
    ( 94, 0.94, 0.96, "stone"),   # right
    (182, 1.02, 1.04, "taupe"),   # bottom — fullest
    (268, 0.92, 0.98, "ink"),     # left   — darkest, anchor
]

def mark(cx, cy, scale, palette, seed=True, seed_fill=None):
    parts = [f'<g transform="translate({cx} {cy}) rotate(-14) scale({scale})">']
    for ang, sx, sy, key in PETALS:
        parts.append(
            f'<path d="{PETAL}" fill="{palette[key]}" '
            f'transform="rotate({ang}) scale({sx} {sy})"/>'
        )
    if seed:
        parts.append(
            f'<circle cx="50" cy="-50" r="6.5" fill="{seed_fill or palette["taupe"]}"/>'
        )
    parts.append("</g>")
    return "\n    ".join(parts)

LIGHT = {"sand": SAND, "stone": STONE, "taupe": TAUPE, "ink": INK}
DARK  = {"sand": PALE, "stone": SAND,  "taupe": STONE, "ink": "#91826F"}
MONO  = {"sand": INK,  "stone": INK,   "taupe": INK,   "ink": INK}

def wordmark(x, y, size, fill, sub_fill, anchor="start", sub=True):
    s = [
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="500" letter-spacing="{-size*0.035:.1f}" fill="{fill}" '
        f'text-anchor="{anchor}">forma</text>'
    ]
    if sub:
        # letter-spaced caps sit under the word; nudge x so the optical
        # left edge lines up with the 'f'
        sx = x + size * 0.045 if anchor == "start" else x + size * 0.09
        s.append(
            f'<text x="{sx:.0f}" y="{y + size*0.52:.0f}" font-family="{FONT}" '
            f'font-size="{size*0.185:.1f}" font-weight="500" '
            f'letter-spacing="{size*0.11:.1f}" fill="{sub_fill}" '
            f'text-anchor="{anchor}">GENERATIVE AI</text>'
        )
    return "\n  ".join(s)

def svg(w, h, body, bg=None, title="forma — generative AI"):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
        f"  <title>{title}</title>\n  {bgrect}\n  {body}\n</svg>\n"
    )

def save(name, text):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(text)
    print(name, len(text), "bytes")

# 1 — Primary horizontal lockup on warm paper -------------------------------
body = mark(160, 170, 1.35, LIGHT) + "\n  " + wordmark(308, 184, 96, INK, TAUPE)
save("forma-logo-primary.svg", svg(900, 340, body, bg=PAPER))

# 2 — Stacked lockup on warm charcoal ---------------------------------------
body = mark(360, 230, 1.5, DARK, seed_fill=SAND) + "\n  " + \
       wordmark(360, 468, 84, PAPER, SAND, anchor="middle")
save("forma-logo-dark.svg", svg(720, 600, body, bg=INK))

# 3 — Mark only, transparent (favicon / avatar / app use) --------------------
body = mark(256, 256, 2.3, LIGHT)
save("forma-mark.svg", svg(512, 512, body))

# 4 — One-colour version, transparent ----------------------------------------
body = mark(160, 170, 1.35, MONO, seed_fill=INK) + "\n  " + \
       wordmark(308, 184, 96, INK, INK)
save("forma-logo-mono.svg", svg(900, 340, body))
