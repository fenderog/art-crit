"""Generate Loam's original, fully outlined SVG identity. No dependencies."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
INK = '#353A33'
PAPER = '#F3F0E8'

# Three gently curled seed husks. Their inward tips leave an open, living center.
PETAL = '''M 8,-9
C 42,-22 78,-52 79,-95
C 80,-139 47,-169 8,-167
C -36,-165 -68,-134 -67,-94
C -67,-54 -44,-35 -18,-22
C -8,-17 -4,-11 -4,-2
C 0,-5 4,-7 8,-9 Z'''

# Bespoke lowercase lettering: soft bowls, a low shoulder, and a curled l.
LETTERS = [
    '''M 12,0 C 5,0 0,5 0,12 L 0,151
    C 0,173 12,184 34,184 L 49,184 L 49,159 L 40,159
    C 31,159 27,154 27,145 L 27,12 C 27,5 22,0 15,0 Z''',
    '''M 126,53 C 89,53 65,78 65,118 C 65,158 88,184 125,184
    C 164,184 188,157 188,117 C 188,78 165,53 126,53 Z
    M 125,78 C 147,78 161,93 161,118 C 161,144 148,159 125,159
    C 103,159 92,144 92,118 C 92,93 104,78 125,78 Z''',
    '''M 269,53 C 230,53 207,78 207,118 C 207,158 229,184 264,184
    C 285,184 300,174 307,161 L 307,180 L 332,180 L 332,57 L 307,57
    L 307,73 C 298,60 284,53 269,53 Z
    M 270,78 C 294,78 307,93 307,118 C 307,143 293,159 270,159
    C 247,159 234,142 234,118 C 234,93 247,78 270,78 Z''',
    '''M 359,57 L 384,57 L 384,73 C 393,60 406,53 423,53
    C 443,53 457,63 464,79 C 475,61 489,53 508,53
    C 541,53 558,74 558,108 L 558,180 L 531,180 L 531,111
    C 531,89 522,78 505,78 C 487,78 476,93 476,115 L 476,180
    L 449,180 L 449,111 C 449,89 440,78 423,78
    C 404,78 386,94 386,116 L 386,180 L 359,180 Z'''
]

# Small uppercase architectural lettering, also paths rather than font references.
GLYPHS = {
    'G': 'M 10,2 C 8,0 2,0 1,5 L 1,9 C 1,14 7,15 10,12 L 10,8 L 6,8',
    'E': 'M 10,1 L 1,1 L 1,14 L 10,14 M 1,7.5 L 8,7.5',
    'N': 'M 1,14 L 1,1 L 10,14 L 10,1',
    'R': 'M 1,14 L 1,1 L 6,1 C 12,1 12,7.5 6,7.5 L 1,7.5 M 6,7.5 L 11,14',
    'A': 'M 0,14 L 5.5,1 L 11,14 M 2.3,9 L 8.7,9',
    'T': 'M 0,1 L 11,1 M 5.5,1 L 5.5,14',
    'I': 'M 5.5,1 L 5.5,14',
    'V': 'M 0,1 L 5.5,14 L 11,1',
    'L': 'M 1,1 L 1,14 L 10,14',
    'C': 'M 10,2.5 C 7,-0.5 1,0 1,6 L 1,9 C 1,15 7,15 10,12.5',
}

def symbol(x=0, y=0, scale=1):
    paths = '\n'.join(f'<path d="{PETAL}" fill="{color}" transform="rotate({angle})"/>'
                      for angle, color in [(0, '#858673'), (120, '#B2A38E'), (240, '#575E50')])
    return f'<g transform="translate({x} {y}) scale({scale})">{paths}</g>'

def wordmark(x, y, scale=1):
    paths = ''.join(f'<path d="{p}"/>' for p in LETTERS)
    return f'<g fill="{INK}" fill-rule="evenodd" transform="translate({x} {y}) scale({scale})">{paths}</g>'

def descriptor(x, y, scale=1):
    offset = 0
    paths = []
    for char in 'GENERATIVE INTELLIGENCE':
        if char == ' ':
            offset += 13
        else:
            paths.append(f'<path transform="translate({offset} 0)" d="{GLYPHS[char]}"/>')
            offset += 18
    return f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{INK}" stroke-width="1.18" stroke-linejoin="round" stroke-linecap="round">{"".join(paths)}</g>'

def svg(width, height, content, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{label}</title>
<desc id="desc">Loam, generative intelligence. Three organic seed forms unfold around an open center, paired with a custom lowercase wordmark. Warm stone, muted olive-grey and charcoal.</desc>
{content}
</svg>\n'''

# Spacious presentation artboard.
presentation = f'<rect width="1600" height="1000" fill="{PAPER}"/>'
presentation += symbol(421, 494, 1.03)
presentation += wordmark(649, 377, 1.14)
presentation += descriptor(653, 628, 1.04)
(OUT / 'loam-logo.svg').write_text(svg(1600, 1000, presentation, 'Loam — generative intelligence'))

# Transparent production assets; the wordmark is completely outlined.
lockup = symbol(177, 190, 0.92) + wordmark(384, 88, 1.05) + descriptor(388, 319, 0.96)
(OUT / 'loam-lockup.svg').write_text(svg(1010, 380, lockup, 'Loam — transparent logo lockup'))
(OUT / 'loam-symbol.svg').write_text(svg(400, 400, symbol(200, 200, 1.02), 'Loam — organic seed symbol'))
print('Created 3 SVG assets in output/')
