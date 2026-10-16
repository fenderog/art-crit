from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# Three germinating forms, repeated around a shared, open centre.
SEED = 'M 153 143 C 129 127 93 119 86 89 C 75 39 117 16 155 20 C 210 25 245 73 242 113 C 239 145 214 156 191 144 C 179 137 166 135 153 143 Z'
COLORS = ('#9B947E', '#C2B29D', '#6F7768')
INK = '#343B34'


def symbol():
    return '\n'.join(
        f'<path d="{SEED}" fill="{color}" transform="rotate({angle} 160 160)"/>'
        for color, angle in zip(COLORS, (0, 120, 240))
    )


# Bespoke, soft, single-storey lowercase lettering. Outlines/strokes rather
# than font references keep the identity identical on every SVG viewer.
WORDMARK = [
    'M 10 8 V 121 C 10 137 17 145 31 145',
    'M 107 50 C 79 50 63 69 63 98 C 63 127 79 146 107 146 C 135 146 151 127 151 98 C 151 69 135 50 107 50 Z',
    'M 269 98 C 269 69 252 50 225 50 C 198 50 181 69 181 98 C 181 127 198 146 225 146 C 252 146 269 127 269 98 M 269 51 V 145',
    'M 307 145 V 52 M 307 86 C 307 63 321 50 341 50 C 363 50 375 65 375 87 V 145 M 375 87 C 375 63 390 50 410 50 C 433 50 446 65 446 89 V 145',
]

# Small outlined descriptor, deliberately quiet and widely spaced.
CAPS = {
    'G': 'M6 2 C5.3 .7 4.4 0 3 0 C1 0 0 1.7 0 5 C0 8.3 1 10 3 10 C4.5 10 5.5 9.4 6 8 V5.5 H3.5',
    'E': 'M6 0 H0 V10 H6 M0 5 H5',
    'N': 'M0 10 V0 L6 10 V0',
    'R': 'M0 10 V0 H3 C5 0 6 1 6 2.5 C6 4 5 5 3 5 H0 M3 5 L6.5 10',
    'A': 'M0 10 L3 0 L6 10 M1.2 6.5 H4.8',
    'T': 'M0 0 H6 M3 0 V10',
    'I': 'M0 0 V10',
    'V': 'M0 0 L3 10 L6 0',
}


def descriptor():
    paths = []
    x = 0
    for char in 'GENERATIVE AI':
        if char == ' ':
            x += 7
            continue
        paths.append(f'<path d="{CAPS[char]}" transform="translate({x} 0)"/>')
        x += (1 if char == 'I' else 6) + 5
    return '\n'.join(paths)


def document(width, height, title, description, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
{content}
</svg>
'''


word_paths = '\n'.join(f'<path d="{d}"/>' for d in WORDMARK)
primary = f'''<rect width="1600" height="1000" fill="#F5F2EB"/>
<g transform="translate(300 316) scale(1.15)">
{symbol()}
</g>
<g transform="translate(735 363) scale(1.15)" fill="none" stroke="{INK}" stroke-width="17" stroke-linecap="round" stroke-linejoin="round">
{word_paths}
</g>
<g transform="translate(747 583) scale(1.6)" fill="none" stroke="#777C70" stroke-width="0.9" stroke-linecap="square" stroke-linejoin="round">
{descriptor()}
</g>'''

(OUT / 'loam-logo.svg').write_text(document(
    1600, 1000, 'loam — generative AI',
    'A three-seed organic emblem in sage, stone and sand, alongside a custom lowercase loam wordmark on warm ivory.',
    primary,
))

(OUT / 'loam-symbol.svg').write_text(document(
    512, 512, 'loam — organic seed emblem',
    'Three softly curved seed forms spiral around an open centre. Sage, stone and sand on a transparent background.',
    f'<g transform="translate(16 16) scale(1.5)">{symbol()}</g>',
))

print('Created output/loam-logo.svg and output/loam-symbol.svg')
