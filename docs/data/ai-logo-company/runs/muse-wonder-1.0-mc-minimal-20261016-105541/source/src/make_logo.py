#!/usr/bin/env python3
"""Generative AI logo — organic shapes, neutral tones.
Mark: three interlocking organic blobs / seed forms growing from a centre,
suggesting emergence, generation and a neural bloom. No text baked into mark;
wordmark set in clean sans below/beside.
Palette (neutral): warm stone, taupe, charcoal, off-white.
"""
import pathlib
OUT = pathlib.Path("output"); OUT.mkdir(exist_ok=True)

# Organic blob path helper (closed smooth shape around centre)
def blob(cx, cy, r, points):
    return points  # hand-tuned below for control

# Hand-crafted organic paths (viewBox 0 0 240 240 for mark)
MARK = """
  <!-- three overlapping seed / petal forms, rotated 0 / 120 / 240 deg -->
  <g>
    <path d="M120 28 C 152 52, 168 88, 158 122 C 149 152, 132 168, 120 172 C 108 168, 91 152, 82 122 C 72 88, 88 52, 120 28 Z" fill="#8A7D6B"/>
    <path d="M120 28 C 152 52, 168 88, 158 122 C 149 152, 132 168, 120 172 C 108 168, 91 152, 82 122 C 72 88, 88 52, 120 28 Z" fill="#B8AA94" transform="rotate(120 120 120)"/>
    <path d="M120 28 C 152 52, 168 88, 158 122 C 149 152, 132 168, 120 172 C 108 168, 91 152, 82 122 C 72 88, 88 52, 120 28 Z" fill="#3C3730" transform="rotate(240 120 120)"/>
    <!-- cut-out veins: background-coloured organic slits showing generation / growth -->
    <path d="M120 52 C 132 78, 134 108, 120 148 C 106 108, 108 78, 120 52 Z" fill="{bg}"/>
    <path d="M120 52 C 132 78, 134 108, 120 148 C 106 108, 108 78, 120 52 Z" fill="{bg}" transform="rotate(120 120 120)"/>
    <path d="M120 52 C 132 78, 134 108, 120 148 C 106 108, 108 78, 120 52 Z" fill="{bg}" transform="rotate(240 120 120)"/>
    <circle cx="120" cy="120" r="14" fill="#E8E0D1"/>
    <circle cx="120" cy="120" r="6" fill="#3C3730"/>
  </g>
"""

def svg_primary():
    mark = MARK.format(bg="#F4F1EB")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 240" width="1440" height="480" role="img" aria-label="Lumenform logo">
  <title>Lumenform — Generative AI</title>
  <rect width="720" height="240" fill="#F4F1EB"/>
  {mark}
  <text x="268" y="118" font-family="Helvetica Neue, Arial, sans-serif" font-size="52" font-weight="600" letter-spacing="-1" fill="#2B2721">lumenform</text>
  <text x="270" y="152" font-family="Helvetica Neue, Arial, sans-serif" font-size="13" letter-spacing="4.5" fill="#8A7D6B">GENERATIVE  INTELLIGENCE</text>
</svg>'''

def svg_mark():
    mark = MARK.format(bg="#F4F1EB")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="960" height="960" role="img" aria-label="Lumenform mark">
  <title>Lumenform mark</title>
  <rect width="240" height="240" rx="52" fill="#F4F1EB"/>
  {mark}
</svg>'''

def svg_dark():
    mark = MARK.format(bg="#23201B")
    # on dark, centre dot contrast adjusted via same palette still reads
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 240" width="1440" height="480" role="img" aria-label="Lumenform logo on dark">
  <title>Lumenform — Generative AI (dark)</title>
  <rect width="720" height="240" fill="#23201B"/>
  {mark}
  <text x="268" y="118" font-family="Helvetica Neue, Arial, sans-serif" font-size="52" font-weight="600" letter-spacing="-1" fill="#F4F1EB">lumenform</text>
  <text x="270" y="152" font-family="Helvetica Neue, Arial, sans-serif" font-size="13" letter-spacing="4.5" fill="#B8AA94">GENERATIVE  INTELLIGENCE</text>
</svg>'''

def svg_stacked():
    mark = MARK.format(bg="#F4F1EB")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 400" width="900" height="1000" role="img" aria-label="Lumenform stacked logo">
  <title>Lumenform stacked</title>
  <rect width="360" height="400" fill="#F4F1EB"/>
  <g transform="translate(60,8)">{mark}</g>
  <text x="180" y="292" text-anchor="middle" font-family="Helvetica Neue, Arial, sans-serif" font-size="38" font-weight="600" letter-spacing="-0.5" fill="#2B2721">lumenform</text>
  <text x="180" y="324" text-anchor="middle" font-family="Helvetica Neue, Arial, sans-serif" font-size="10.5" letter-spacing="4" fill="#8A7D6B">GENERATIVE INTELLIGENCE</text>
</svg>'''

(OUT/"logo-primary.svg").write_text(svg_primary())
(OUT/"logo-mark.svg").write_text(svg_mark())
(OUT/"logo-dark.svg").write_text(svg_dark())
(OUT/"logo-stacked.svg").write_text(svg_stacked())
print("wrote 4 SVGs to output/")
