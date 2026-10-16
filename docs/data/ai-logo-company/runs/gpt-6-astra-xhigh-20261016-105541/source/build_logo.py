#!/usr/bin/env python3
"""Build the Loam identity. Pure SVG geometry; no fonts or third-party packages.

Run: python3 build_logo.py
Optional macOS PNG export: python3 build_logo.py --png

The three unfurling seed shapes use the same Bezier geometry rotated 120°.
All wordmark letters and the small-cap descriptor are custom vector paths.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
PAPER = '#F4F1EA'
INK = '#353A32'
ASH = '#595F52'
STONE = '#999585'
OAT = '#C2B6A2'
MUTED = '#737468'

# A curled seed: full rounded outer contour, open counter, tapered growth tip.
SEED = ('M 9 -23 '
        'C -12 -37 -41 -48 -57 -75 '
        'C -82 -118 -56 -158 -15 -162 '
        'C 39 -167 98 -118 103 -75 '
        'C 108 -41 81 -10 51 -10 '
        'C 43 -10 36 -13 33 -20 '
        'C 28 -31 36 -42 48 -50 '
        'C 64 -61 66 -77 55 -90 '
        'C 42 -106 18 -111 0 -107 '
        'C -19 -103 -29 -92 -27 -76 '
        'C -24 -58 -4 -42 11 -24 '
        'Q 14 -20 9 -23 Z')

# Custom lowercase lettering. Counters use the even-odd fill rule.
LETTERS = [
    (0, 'M 0 0 H 27 V 151 C 27 164 33 170 46 170 H 56 V 194 H 43 '
        'C 15 194 0 178 0 152 Z'),
    (79, 'M 68 54 C 107 54 133 82 133 125 '
         'C 133 169 108 197 68 197 C 28 197 2 169 2 125 '
         'C 2 82 28 54 68 54 Z '
         'M 68 78 C 43 78 28 95 28 125 C 28 156 43 173 68 173 '
         'C 92 173 107 156 107 125 C 107 95 92 78 68 78 Z'),
    (242, 'M 64 54 C 84 54 100 62 110 75 V 57 H 136 V 194 H 111 V 176 '
          'C 100 190 84 197 64 197 C 26 197 0 169 0 126 '
          'C 0 83 26 54 64 54 Z '
          'M 68 78 C 43 78 26 96 26 126 C 26 155 42 173 68 173 '
          'C 94 173 110 155 110 126 C 110 96 94 78 68 78 Z'),
    (410, 'M 0 57 H 25 V 75 C 34 61 47 54 65 54 '
          'C 87 54 102 63 110 80 C 120 63 137 54 157 54 '
          'C 190 54 209 77 209 114 V 194 H 182 V 117 '
          'C 182 91 173 79 154 79 C 134 79 121 94 121 119 V 194 H 94 V 117 '
          'C 94 91 85 79 65 79 C 44 79 27 95 27 120 V 194 H 0 Z'),
]

# A quiet, letter-spaced single-line alphabet for the descriptor.
CAPS = {
    'A': 'M 0 10 L 3.5 0 L 7 10 M 1.3 6.5 H 5.7',
    'C': 'M 7 1.2 C 6.2 .4 5.2 0 3.7 0 C 1.2 0 0 1.9 0 5 '
         'C 0 8.1 1.2 10 3.7 10 C 5.2 10 6.2 9.6 7 8.8',
    'E': 'M 6.6 0 H 0 V 10 H 6.6 M 0 4.8 H 5.5',
    'G': 'M 7 1.2 C 6.2 .4 5.2 0 3.7 0 C 1.2 0 0 1.9 0 5 '
         'C 0 8.1 1.2 10 3.7 10 C 5.1 10 6.2 9.6 7 8.8 V 5.5 H 4',
    'I': 'M 0 0 V 10',
    'L': 'M 0 0 V 10 H 6.4',
    'N': 'M 0 10 V 0 L 7 10 V 0',
    'R': 'M 0 10 V 0 H 3.6 C 5.7 0 6.8 1 6.8 2.8 '
         'C 6.8 4.6 5.7 5.5 3.6 5.5 H 0 M 3.6 5.5 L 7.2 10',
    'T': 'M 0 0 H 7.6 M 3.8 0 V 10',
    'V': 'M 0 0 L 3.5 10 L 7 0',
}


def emblem(x, y, scale=1, mono=None):
    colors = [mono] * 3 if mono else [ASH, STONE, OAT]
    paths = '\n'.join(
        f'<path fill="{color}" transform="rotate({angle})" d="{SEED}"/>'
        for color, angle in zip(colors, (0, 120, 240)))
    return f'<g transform="translate({x} {y}) scale({scale})">{paths}</g>'


def wordmark(x, y, scale=1, color=INK):
    paths = '\n'.join(f'<path transform="translate({offset} 0)" d="{d}"/>'
                      for offset, d in LETTERS)
    return (f'<g fill="{color}" fill-rule="evenodd" '
            f'transform="translate({x} {y}) scale({scale})">{paths}</g>')


def descriptor(x, y, scale=1.4):
    position = 0
    parts = []
    for char in 'GENERATIVE INTELLIGENCE':
        if char == ' ':
            position += 6
            continue
        parts.append(f'<path transform="translate({position:g} 0)" d="{CAPS[char]}"/>')
        position += 5.2 if char == 'I' else 11.9
    return (f'<g transform="translate({x} {y}) scale({scale})" '
            f'fill="none" stroke="{MUTED}" stroke-width=".85" '
            'stroke-linejoin="round" stroke-linecap="round">'
            + ''.join(parts) + '</g>')


def svg(width, height, title, description, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{title}</title>\n<desc id="desc">{description}</desc>\n'
            f'{content}\n</svg>\n')


def build():
    OUT.mkdir(exist_ok=True)
    story = ('Loam, a generative AI company. Three unfurling organic seed shapes '
             'form a continuous cycle of growth, in ash, warm stone and oat. '
             'A custom lowercase wordmark balances the symbol.')
    hero = (f'<rect width="1600" height="1000" fill="{PAPER}"/>\n'
            + emblem(463, 503)
            + wordmark(667, 389)
            + descriptor(670, 627))
    (OUT / 'loam-presentation.svg').write_text(
        svg(1600, 1000, 'loam — generative intelligence', story, hero))

    lockup = emblem(188, 201) + wordmark(392, 87) + descriptor(395, 325)
    (OUT / 'loam-logo.svg').write_text(
        svg(1050, 400, 'loam — primary logo', story + ' Transparent background.', lockup))

    (OUT / 'loam-symbol.svg').write_text(
        svg(400, 400, 'loam — organic seed symbol', story + ' Transparent background.',
            emblem(200, 206)))


def render_png():
    """Render via macOS Quick Look and crop its square preview to the artboard.

    The temporary SVG uses percentage dimensions to avoid retina viewport clipping.
    All temporary files live in this directory and are automatically removed.
    """
    with tempfile.TemporaryDirectory(prefix='.render-', dir=ROOT) as temp:
        temp = Path(temp)
        source = (OUT / 'loam-presentation.svg').read_text()
        source = source.replace('width="1600" height="1000" viewBox',
                                'width="100%" height="100%" viewBox', 1)
        preview = temp / 'loam.svg'
        preview.write_text(source)
        subprocess.run(['qlmanage', '-t', '-s', '1600', '-o', str(temp), str(preview)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-i', str(temp / 'loam.svg.png'),
                        '-vf', 'crop=1600:1000:0:300', '-frames:v', '1',
                        str(OUT / 'loam-presentation.png')], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', action='store_true', help='also render a PNG using macOS Quick Look')
    args = parser.parse_args()
    build()
    if args.png:
        render_png()
    for file in sorted(OUT.iterdir()):
        print(f'{file.relative_to(ROOT)} ({file.stat().st_size:,} bytes)')
