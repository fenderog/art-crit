#!/usr/bin/env python3
"""
FORMA — generative AI company logo
Organic shapes, neutral tones.

Mark: three asymmetric petals rotated 120 degrees around a seed centre.
The pinwheel/bloom reads as growth, generation and unfolding; the tonal
progression (charcoal -> stone -> sand) suggests one form generating the next.
All artwork is flat vector paths — no effects, so it scales from favicon to signage.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT, exist_ok=True)

# --- palette (warm neutrals) -------------------------------------------------
CREAM = "#F3F0EA"
PAPER = "#FAF8F3"
INK   = "#2B2823"   # warm charcoal
UMBER = "#5D5344"
STONE = "#8F8271"   # mid stone / taupe
CLAY  = "#B4A48D"
SAND  = "#D8CEBC"
LINE  = "#DDD6C9"

FONT = "'Avenir Next','Helvetica Neue',Helvetica,Arial,sans-serif"

# --- the petal ----------------------------------------------------------------
# One fat, asymmetric petal/seed in a 120x120 box: round head leaning
# slightly right, wide base at the centre so the three rotated copies
# overlap and interlock like a bloom / dividing cells.
PETAL = (
    "M 60 62 "
    "C 36 48, 44 16, 66 2 "
    "C 80 16, 82 50, 60 62 Z"
)

_clip_n = [0]

def mark(x, y, size, fills, seed=None, stroke=None, seed_r=5.4, opacity=1.0):
    """Mark at top-left (x,y), `size` px square. The seed centre is a true
    transparent hole: petals are clipped by rect-minus-circle (even-odd),
    so it stays crisp on any background."""
    _clip_n[0] += 1
    cid = f"seedclip{_clip_n[0]}"
    s = size / 120.0
    hole = (f"M -40 -40 H 160 V 160 H -40 Z "
            f"M {60-seed_r} 60 A {seed_r} {seed_r} 0 1 0 {60+seed_r} 60 "
            f"A {seed_r} {seed_r} 0 1 0 {60-seed_r} 60 Z")
    sw = ""
    if stroke:
        sw = f' stroke="{stroke}" stroke-width="{2.4/s:.2f}" stroke-linejoin="round"'
    petals = ""
    for i, f in enumerate(fills):
        petals += f'<path d="{PETAL}" fill="{f}"{sw} transform="rotate({i*120} 60 60)"/>'
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" opacity="{opacity}">'
        f'<defs><clipPath id="{cid}"><path d="{hole}" clip-rule="evenodd"/></clipPath></defs>'
        f'<g clip-path="url(#{cid})">{petals}</g></g>'
    )

# Wordmark drawn as monoline stroke letters (not a font), so it renders
# identically everywhere. Baseline y=0, x-height 36, 'f' ascender 56.
# (advance, [path-data ...], [circle (cx,cy,r) ...])
LETTERS = {
    "f": (24, ["M20 -50 C20 -56 11 -56 11 -44 V0 M4 -34 H19"], []),
    "o": (36, [], [(18, -18, 17)]),
    "r": (27, ["M7 -36 V0 M7 -27 A9.5 9.5 0 0 1 26 -27"], []),
    "m": (52, ["M7 0 V-27 A9.5 9.5 0 0 1 26 -27 V0 "
               "M26 -27 A9.5 9.5 0 0 1 45 -27 V0"], []),
    "a": (37, ["M34 -36 V0"], [(17, -18, 17)]),
}
WORD_W = 207  # total advance incl. dot, at scale 1

def wordmark(x, y, scale=1.0, ink=INK, sub=STONE, align="start", tagline=True, dot=None):
    shapes, cx = "", 0
    for ch in "forma":
        adv, paths, circles = LETTERS[ch]
        for d in paths:
            shapes += f'<path d="{d}" transform="translate({cx} 0)"/>'
        for (ccx, ccy, r) in circles:
            shapes += f'<circle cx="{cx+ccx}" cy="{ccy}" r="{r}"/>'
        cx += adv + 5
    dotc = dot or (CLAY if ink == INK else SAND)
    shapes += f'<circle cx="{cx+2}" cy="-4" r="4.2" fill="{dotc}" stroke="none"/>'
    tag = ""
    if tagline:
        tag = (f'<text x="6" y="30" font-family="{FONT}" font-size="9" '
               f'font-weight="600" letter-spacing="1.9" '
               f'fill="{sub}">GENERATIVE INTELLIGENCE</text>')
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})">'
        f'<g fill="none" stroke="{ink}" stroke-width="7.2" '
        f'stroke-linecap="round" stroke-linejoin="round">{shapes}</g>'
        f'{tag}</g>'
    )

def svg(w, h, body, bg=None, title="Forma logo"):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
        f'<title>{title}</title>\n{bgrect}\n{body}\n</svg>\n'
    )

def save(name, content):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(name, len(content), "bytes")

PRIMARY_FILLS = [INK, STONE, CLAY]
DARK_FILLS    = ["#EDE6D8", "#B4A48D", "#7E7362"]

# --- 02 primary horizontal lockup (on cream) ---------------------------------
body = mark(52, 54, 172, PRIMARY_FILLS) + wordmark(258, 156, 1.15)
save("02-forma-logo-primary.svg", svg(560, 280, body, bg=CREAM, title="Forma — primary logo"))

# --- 03 dark lockup ------------------------------------------------------------
body = mark(52, 54, 172, DARK_FILLS) + wordmark(258, 156, 1.15, ink="#F3F0EA", sub="#A99C88")
save("03-forma-logo-dark.svg", svg(560, 280, body, bg=INK, title="Forma — logo on dark"))

# --- 04 mark only (transparent) ------------------------------------------------
body = mark(10, 10, 460, PRIMARY_FILLS, seed=CREAM)
save("04-forma-mark.svg", svg(480, 480, body, bg=None, title="Forma — mark"))

# --- 05 mono lockup --------------------------------------------------------------
body = (mark(52, 54, 172, [INK, INK, INK])
        + wordmark(258, 156, 1.15, ink=INK, sub=INK, dot=INK))
save("05-forma-logo-mono.svg", svg(560, 280, body, bg=PAPER, title="Forma — monochrome logo"))

# --- 06 app icon ------------------------------------------------------------------
body = (f'<rect width="480" height="480" rx="104" fill="{INK}"/>'
        + mark(101, 119, 292, DARK_FILLS))
save("06-forma-app-icon.svg", svg(480, 480, body, bg=None, title="Forma — app icon"))

# --- 01 brand sheet ---------------------------------------------------------------
W, H = 1400, 1050
parts = []
# header
parts.append(f'<text x="80" y="78" font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="4" fill="{STONE}">FORMA — GENERATIVE INTELLIGENCE</text>')
parts.append(f'<text x="1320" y="78" font-family="{FONT}" font-size="13" font-weight="500" letter-spacing="3" fill="{STONE}" text-anchor="end">BRAND MARK · 01</text>')
parts.append(f'<line x1="80" y1="102" x2="1320" y2="102" stroke="{LINE}" stroke-width="1"/>')

# hero lockup, centred
parts.append(mark(396, 150, 230, PRIMARY_FILLS))
parts.append(wordmark(670, 290, 1.55))
parts.append(f'<text x="700" y="452" font-family="{FONT}" font-size="17" fill="{UMBER}" text-anchor="middle">'
             f'Three organic petals, each generated from the last — growth, unfolding, emergence.</text>')
parts.append(f'<line x1="80" y1="492" x2="1320" y2="492" stroke="{LINE}" stroke-width="1"/>')

# three tiles
tiles = [
    ("PRIMARY MARK", CREAM, PRIMARY_FILLS, CREAM, None),
    ("ON CHARCOAL", INK, DARK_FILLS, INK, None),
    ("MONOCHROME", SAND, [INK, INK, INK], SAND, None),
]
tw, th, ty, gap = 393, 300, 522, 30
for i, (label, tbg, fills, seed, stroke) in enumerate(tiles):
    tx = 80 + i * (tw + gap)
    parts.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="{tbg}"/>')
    parts.append(mark(tx + (tw - 190) / 2, ty + 38, 190, fills, seed=seed, stroke=stroke))
    lc = "#A99C88" if tbg == INK else UMBER
    parts.append(f'<text x="{tx + tw/2}" y="{ty + th - 22}" font-family="{FONT}" font-size="11" font-weight="600" letter-spacing="3" fill="{lc}" text-anchor="middle">{label}</text>')

# palette row
py = 868
parts.append(f'<text x="80" y="{py - 18}" font-family="{FONT}" font-size="11" font-weight="600" letter-spacing="3" fill="{STONE}">NEUTRAL PALETTE</text>')
swatches = [(INK, "Charcoal", "#2B2823"), (UMBER, "Umber", "#5D5344"), (STONE, "Stone", "#8F8271"),
            (CLAY, "Clay", "#B4A48D"), (SAND, "Sand", "#D8CEBC"), (CREAM, "Cream", "#F3F0EA")]
sw = 1240 / len(swatches)
for i, (c, name, hx) in enumerate(swatches):
    sx = 80 + i * sw
    parts.append(f'<rect x="{sx:.0f}" y="{py}" width="{sw-12:.0f}" height="58" rx="6" fill="{c}" stroke="{LINE}"/>')
    parts.append(f'<text x="{sx:.0f}" y="{py+84}" font-family="{FONT}" font-size="13" font-weight="600" fill="{INK}">{name}</text>')
    parts.append(f'<text x="{sx:.0f}" y="{py+104}" font-family="{FONT}" font-size="11" fill="{STONE}">{hx}</text>')

parts.append(f'<text x="80" y="1018" font-family="{FONT}" font-size="12" fill="{STONE}">Construction — one asymmetric petal rotated 120° · seed centre · flat colour, no effects · clear space = height of seed ×4</text>')

save("01-forma-brand-sheet.svg", svg(W, H, "\n".join(parts), bg=PAPER, title="Forma — brand sheet"))
print("done")
