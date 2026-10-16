#!/usr/bin/env python3
"""Generate organic generative-AI logo SVG."""
svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
<rect width="800" height="800" rx="180" fill="#EDE8DF"/>
<!-- soft shadow blobs -->
<path d="M400 150 C520 150 620 240 630 370 C640 500 560 620 420 640 C280 660 160 570 150 430 C140 290 270 150 400 150 Z" fill="#D8CFC0"/>
<path d="M400 210 C490 210 565 275 570 375 C575 475 510 565 410 575 C310 585 225 515 220 405 C215 295 305 210 400 210 Z" fill="#C4B7A3"/>
<path d="M360 280 C440 260 530 300 545 390 C560 480 490 555 395 555 C300 555 235 485 250 395 C262 320 290 295 360 280 Z" fill="#8A8478"/>
<!-- generative nodes: organic cluster -->
<g fill="#EDE8DF">
<circle cx="400" cy="400" r="52"/>
<circle cx="330" cy="360" r="30"/>
<circle cx="470" cy="355" r="34"/>
<circle cx="350" cy="470" r="28"/>
<circle cx="460" cy="465" r="32"/>
<circle cx="400" cy="300" r="18"/>
</g>
<g stroke="#EDE8DF" stroke-width="7" stroke-linecap="round" opacity="0.85">
<line x1="400" y1="400" x2="330" y2="360"/>
<line x1="400" y1="400" x2="470" y2="355"/>
<line x1="400" y1="400" x2="350" y2="470"/>
<line x1="400" y1="400" x2="460" y2="465"/>
<line x1="400" y1="400" x2="400" y2="300"/>
<line x1="330" y1="360" x2="400" y2="300"/>
<line x1="470" y1="355" x2="400" y2="300"/>
</g>
<g fill="#3E3A33">
<circle cx="400" cy="400" r="12"/>
<circle cx="330" cy="360" r="7"/>
<circle cx="470" cy="355" r="7"/>
<circle cx="350" cy="470" r="7"/>
<circle cx="460" cy="465" r="7"/>
</g>
<text x="400" y="700" text-anchor="middle" font-family="Georgia, serif" font-size="44" letter-spacing="8" fill="#3E3A33">EMERGENCE</text>
<text x="400" y="728" text-anchor="middle" font-family="Georgia, serif" font-size="16" letter-spacing="5" fill="#8A8478">GENERATIVE INTELLIGENCE</text>
</svg>'''
open("output/logo.svg","w").write(svg)
print("wrote output/logo.svg", len(svg))
