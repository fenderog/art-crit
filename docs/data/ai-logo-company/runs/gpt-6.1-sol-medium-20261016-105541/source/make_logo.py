from pathlib import Path

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# A seed shape repeated around an open, three-way centre. Each Bézier
# contour is deliberately asymmetric: soft, living geometry rather than a gear.
seed = 'M 0,-14 C -18,-35 -59,-37 -71,-75 C -88,-124 -53,-163 -10,-163 C 34,-163 71,-129 61,-89 C 52,-51 19,-43 0,-14 Z'
colors = ['#544D42', '#938675', '#B9AA96']

def emblem(transform=''):
    return f'''<g transform="{transform}">
      <path d="{seed}" fill="{colors[0]}"/>
      <path d="{seed}" transform="rotate(120)" fill="{colors[1]}"/>
      <path d="{seed}" transform="rotate(240)" fill="{colors[2]}"/>
    </g>'''

# Lettering is drawn as vectors, not font-dependent text. Rounded joins and
# slightly open proportions echo the softness of the seed mark.
wordmark = '''<g fill="none" stroke="#393A32" stroke-width="19" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 710,375 V 488 Q 710,515 735,515"/>
    <path d="M 837,469 C 837,441 822,422 795,422 C 768,422 753,441 753,469 C 753,497 768,516 795,516 C 822,516 837,497 837,469 Z"/>
    <path d="M 953,469 C 953,441 937,422 911,422 C 884,422 868,441 868,469 C 868,497 884,516 911,516 C 937,516 953,497 953,469 M 953,425 V 515"/>
    <path d="M 995,515 V 425 M 995,455 C 995,436 1009,422 1028,422 C 1048,422 1062,436 1062,456 V 515 M 1062,456 C 1062,436 1076,422 1096,422 C 1116,422 1130,436 1130,456 V 515"/>
  </g>'''

primary = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000" role="img" aria-labelledby="title desc">
  <title id="title">loam — generative AI</title>
  <desc id="desc">An organic three-seed emblem in warm earth tones, paired with a custom rounded lowercase loam wordmark on an ivory field.</desc>
  <rect width="1600" height="1000" fill="#F3F0E9"/>
  <g transform="translate(55 0)">
    {emblem('translate(475 483) scale(.88)')}
    {wordmark}
    <text x="711" y="578" fill="#817B6F" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="15" font-weight="500" letter-spacing="4.5">GENERATIVE AI</text>
  </g>
</svg>
'''
(OUT / 'loam-logo.svg').write_text(primary)

icon = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="0 0 640 640" role="img" aria-labelledby="title desc">
  <title id="title">loam — seed symbol</title>
  <desc id="desc">Three organic seed forms turn around an open centre, suggesting ideas growing into new possibilities.</desc>
  <rect width="640" height="640" rx="144" fill="#F3F0E9"/>
  {emblem('translate(320 337) scale(1.36)')}
</svg>
'''
(OUT / 'loam-symbol.svg').write_text(icon)

# A transparent, tightly cropped lockup for practical use on light surfaces.
transparent = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="320" viewBox="0 0 900 320" role="img" aria-labelledby="title desc">
  <title id="title">loam</title>
  <desc id="desc">Transparent vector logo for loam, a generative AI company.</desc>
  <g transform="translate(-297 -305)">
    {emblem('translate(475 483) scale(.88)')}
    {wordmark}
  </g>
</svg>
'''
(OUT / 'loam-transparent.svg').write_text(transparent)
print('Created three SVG logo assets.')
