from pathlib import Path

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# Three soft seed forms turn around a shared, open center.
# All artwork is vector, with no external assets or dependencies.
seed = 'M 3,-23 C -35,-33 -92,-62 -99,-110 C -107,-162 -67,-192 -24,-180 C 27,-167 78,-124 72,-83 C 68,-52 34,-26 3,-23 Z'
colors = ['#514D43', '#898676', '#B8AE9C']
def mark(transform):
    petals = '\n'.join(f'<path d="{seed}" fill="{color}" transform="rotate({i * 120})"/>' for i, color in enumerate(colors))
    return f'<g transform="{transform}">\n{petals}\n</g>'

primary = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" role="img" aria-labelledby="title desc">
<title id="title">Forma — generative intelligence</title>
<desc id="desc">An organic three-seed emblem in charcoal, sage gray and warm stone, paired with an elegant lowercase Forma wordmark on a warm ivory background.</desc>
<rect width="1440" height="900" fill="#F3F0E8"/>
{mark('translate(405 440) scale(.88)')}
<text x="613" y="474" fill="#393B33" font-family="Georgia, 'Times New Roman', serif" font-size="180" letter-spacing="-7">forma</text>
<text x="622" y="535" fill="#77776B" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" letter-spacing="4.2">GENERATIVE INTELLIGENCE</text>
</svg>'''

icon = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">
<title id="title">Forma symbol</title>
<desc id="desc">Three softly curved seed shapes in neutral earth tones, turning around an open center. Transparent background.</desc>
{mark('translate(256 256) scale(1.12)')}
</svg>'''
(OUT / 'forma-logo.svg').write_text(primary)
(OUT / 'forma-symbol.svg').write_text(icon)
