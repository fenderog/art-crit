from pathlib import Path

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# A three-leaf, rotational growth mark. Each leaf shares the same organic
# contour; the small open core is intentionally left as negative space.
leaf = 'M -12 -31 C -64 -66 -73 -122 -33 -153 C 11 -189 82 -170 112 -127 C 132 -98 134 -66 121 -39 C 111 -76 81 -99 51 -87 C 23 -76 26 -43 16 -23 C 9 -10 -1 -19 -12 -31 Z'
colors = ['#454E43', '#969883', '#B7AA96']

def mark(transform=''):
    return f'<g transform="{transform}">' + ''.join(
        f'<path d="{leaf}" fill="{c}" transform="rotate({i*120})"/>'
        for i, c in enumerate(colors)
    ) + '</g>'

# Purpose-drawn lowercase lettering, rather than a dependency on installed fonts.
# Rounded strokes echo the soft shoulders of the growth mark.
wordmark = '''<g fill="none" stroke="#343C34" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 0 80 V 21 M 0 47 C 0 10 57 10 57 47 V 80"/>
  <path d="M 89 22 V 56 C 89 92 146 92 146 56 V 22 M 146 56 V 80"/>
  <path d="M 181 80 V 22 M 181 48 C 181 27 196 18 215 22"/>
  <path d="M 306 50 C 306 10 246 10 246 50 C 246 91 306 91 306 50 Z M 306 22 V 80"/>
</g>'''

primary = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img" aria-labelledby="title description">
<title id="title">Nura — Generative intelligence</title>
<desc id="description">An organic three-leaf growth symbol in moss, sage and warm stone, paired with a custom lowercase Nura wordmark on an ivory background.</desc>
<rect width="1600" height="1000" fill="#F4F1EA"/>
{mark('translate(487 500) scale(.94)')}
<g transform="translate(735 425) scale(1.2)">{wordmark}</g>
<text x="735" y="578" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" letter-spacing="3.3" fill="#73776B">GENERATIVE INTELLIGENCE</text>
</svg>'''

icon = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800" role="img" aria-labelledby="title description">
<title id="title">Nura growth symbol</title>
<desc id="description">Three organic leaves spiraling around an open core. Transparent background.</desc>
{mark('translate(400 400) scale(1.9)')}
</svg>'''

(OUT / 'nura-logo.svg').write_text(primary)
(OUT / 'nura-symbol.svg').write_text(icon)
