from pathlib import Path

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# Three individually drawn seed forms rotate around an open, generative centre.
PETAL = 'M -6,-20 C -45,-35 -76,-77 -58,-111 C -40,-146 9,-151 39,-124 C 72,-94 61,-56 34,-35 C 19,-23 5,-18 -6,-20 Z'

def symbol(x, y, scale=1):
    return f'''<g transform="translate({x} {y}) scale({scale})">
      <path d="{PETAL}" fill="#797B66"/>
      <path d="{PETAL}" transform="rotate(120)" fill="#B3A38D"/>
      <path d="{PETAL}" transform="rotate(240)" fill="#D3C8B5"/>
    </g>'''

# Outlined custom lettering: no font dependency in the primary wordmark.
def wordmark(x, y):
    return f'''<g transform="translate({x} {y})" fill="none" stroke="#373C32" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 0,83 V 19 M 0,43 C 0,9 49,8 49,43 V 83 M 49,43 C 49,9 98,8 98,43 V 83"/>
      <path d="M 192,51 C 192,7 126,7 126,51 C 126,95 192,95 192,51 Z"/>
      <path d="M 222,83 V 19 M 222,46 C 222,25 237,16 253,19"/>
      <path d="M 336,51 C 336,7 270,7 270,51 C 270,95 336,95 336,51 Z M 336,19 V 83"/>
    </g>'''

# Descriptor uses restrained, widely spaced system sans-serif type.
primary = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="960" viewBox="0 0 1440 960" role="img" aria-labelledby="title desc">
  <title id="title">Mora — Generative intelligence</title>
  <desc id="desc">Three organic seed shapes in olive, warm taupe and sand form a growing spiral beside a custom lowercase mora wordmark, on an ivory ground.</desc>
  <rect width="1440" height="960" fill="#F5F2EB"/>
  {symbol(478, 472, 1.05)}
  {wordmark(688, 407)}
  <text x="690" y="539" fill="#797B6E" font-family="Arial, Helvetica, sans-serif" font-size="12" letter-spacing="3.1">GENERATIVE INTELLIGENCE</text>
</svg>
'''
icon = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="0 0 640 640" role="img" aria-labelledby="title desc">
  <title id="title">Mora symbol</title>
  <desc id="desc">An open spiral of three organic seed forms in neutral earth tones.</desc>
  {symbol(320, 320, 1.65)}
</svg>
'''
(OUT / 'mora-logo.svg').write_text(primary)
(OUT / 'mora-symbol.svg').write_text(icon)
