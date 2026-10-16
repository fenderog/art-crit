import math
legs=""
# tentacles
def tent(x0,y0,x1,y1,c,w=16):
    mx=(x0+x1)/2
    return f'<path d="M{x0} {y0} C{x0} {y0+60} {x1} {y0+10} {x1} {y1}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1b3a"/><stop offset="1" stop-color="#4a2c5e"/></linearGradient>
<radialGradient id="head" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#ff8f7a"/><stop offset="1" stop-color="#d9475a"/></radialGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a" stop-opacity=".8"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>
</defs>
<rect width="800" height="600" fill="url(#sky)"/>
<g fill="#ffe9a8" opacity=".8"><circle cx="80" cy="60" r="2"/><circle cx="300" cy="40" r="1.5"/><circle cx="700" cy="80" r="2"/><circle cx="560" cy="30" r="1.5"/><circle cx="180" cy="110" r="1.5"/></g>
<!-- booth frame -->
<rect x="70" y="120" width="660" height="30" fill="#7a2f2a"/>
<rect x="70" y="150" width="14" height="330" fill="#5b211f"/><rect x="716" y="150" width="14" height="330" fill="#5b211f"/>
<!-- awning -->
<path d="M50 70 H750 V150 H50Z" fill="#c8323c"/>
<g fill="#f6efe0">{"".join(f'<path d="M{50+i*50} 70 h25 v80 h-25z"/>' for i in range(0,14,2))}</g>
<g fill="#c8323c">{"".join(f'<path d="M{50+i*50} 150 a25 25 0 0 0 50 0z" />' for i in range(0,14,2))}</g>
<g fill="#f6efe0">{"".join(f'<path d="M{75+i*50} 150 a25 25 0 0 0 50 0z" />' for i in range(0,14,2))}</g>
<!-- lanterns -->
<g>
<line x1="150" y1="150" x2="150" y2="175" stroke="#222"/><ellipse cx="150" cy="200" rx="30" ry="26" fill="url(#glow)"/><ellipse cx="150" cy="200" rx="22" ry="26" fill="#e8402f"/><text x="150" y="208" font-size="22" text-anchor="middle" fill="#ffe9a8" font-family="serif">麺</text>
<line x1="650" y1="150" x2="650" y2="175" stroke="#222"/><ellipse cx="650" cy="200" rx="30" ry="26" fill="url(#glow)"/><ellipse cx="650" cy="200" rx="22" ry="26" fill="#e8402f"/><text x="650" y="208" font-size="22" text-anchor="middle" fill="#ffe9a8" font-family="serif">湯</text>
</g>
<!-- back shelf -->
<rect x="90" y="300" width="620" height="180" fill="#3a1f2e"/>
<g fill="#f6efe0"><rect x="110" y="270" width="40" height="30" rx="4"/><rect x="160" y="270" width="40" height="30" rx="4"/><rect x="600" y="260" width="30" height="40" rx="4"/></g>
<!-- steam pot -->
<rect x="540" y="330" width="120" height="90" rx="8" fill="#8d97a3"/><rect x="530" y="322" width="140" height="14" rx="6" fill="#b4bdc7"/>
<g stroke="#fff" stroke-width="5" fill="none" opacity=".5" stroke-linecap="round">
<path d="M570 310 q-15 -25 0 -45 q15 -20 0 -40"><animate attributeName="opacity" values=".1;.6;.1" dur="3s" repeatCount="indefinite"/></path>
<path d="M620 310 q15 -25 0 -45 q-15 -20 0 -40"><animate attributeName="opacity" values=".6;.1;.6" dur="3s" repeatCount="indefinite"/></path></g>
<!-- octopus tentacles behind counter -->
<g>
{tent(330,420,200,460,"#c93d50",22)}
{tent(470,420,600,460,"#c93d50",22)}
</g>
<!-- body -->
<ellipse cx="400" cy="400" rx="105" ry="80" fill="#d9475a"/>
<!-- head -->
<path d="M290 290 C290 140 510 140 510 290 C510 360 290 360 290 290Z" fill="url(#head)"/>
<g fill="#ffb3a3" opacity=".7"><circle cx="340" cy="210" r="7"/><circle cx="370" cy="190" r="5"/><circle cx="450" cy="215" r="6"/></g>
<!-- chef hat -->
<rect x="320" y="150" width="160" height="40" fill="#fff"/>
<g fill="#fff" stroke="#ddd" stroke-width="2"><circle cx="335" cy="125" r="35"/><circle cx="400" cy="100" r="42"/><circle cx="465" cy="125" r="35"/></g>
<rect x="320" y="140" width="160" height="50" fill="#fff"/><rect x="320" y="172" width="160" height="14" fill="#e6e6e6"/>
<!-- headband -->
<!-- eyes -->
<ellipse cx="355" cy="262" rx="26" ry="30" fill="#fff"/><ellipse cx="445" cy="262" rx="26" ry="30" fill="#fff"/>
<circle cx="362" cy="268" r="13" fill="#222"/><circle cx="438" cy="268" r="13" fill="#222"/>
<circle cx="367" cy="262" r="5" fill="#fff"/><circle cx="443" cy="262" r="5" fill="#fff"/>
<path d="M325 235 q30 -22 58 -2" stroke="#7a1f2e" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M417 233 q28 -20 58 2" stroke="#7a1f2e" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M375 318 q25 22 50 0" stroke="#7a1f2e" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="320" cy="295" r="12" fill="#ff7b8a" opacity=".6"/><circle cx="480" cy="295" r="12" fill="#ff7b8a" opacity=".6"/>
<!-- apron -->
<path d="M335 350 H465 L480 480 H320Z" fill="#f6efe0"/><path d="M335 350 Q400 380 465 350" stroke="#ccc" fill="none" stroke-width="3"/>
<text x="400" y="430" font-size="30" text-anchor="middle" fill="#c8323c" font-family="serif">ラーメン</text>
<!-- arms holding ladle & bowl -->
<path d="M320 380 C250 380 230 340 235 300" stroke="#d9475a" stroke-width="24" fill="none" stroke-linecap="round"/>
<path d="M480 380 C550 380 570 400 560 400" stroke="#d9475a" stroke-width="24" fill="none" stroke-linecap="round"/>
<path d="M235 300 l-10 -60" stroke="#6b4a2f" stroke-width="7" stroke-linecap="round"/><ellipse cx="222" cy="232" rx="18" ry="10" fill="#aab" />
<path d="M320 400 C270 420 280 460 330 440" stroke="#d9475a" stroke-width="22" fill="none" stroke-linecap="round"/>
<path d="M480 400 C530 420 520 460 470 440" stroke="#d9475a" stroke-width="22" fill="none" stroke-linecap="round"/>
<!-- counter -->
<rect x="60" y="460" width="680" height="28" rx="4" fill="#9a5a34"/><rect x="60" y="488" width="680" height="112" fill="#6e3b22"/>
<g stroke="#5a2e1a" stroke-width="2"><path d="M60 500 H740 M60 540 H740"/></g>
<!-- bowls -->
<g id="bowl">
<path d="M150 440 h110 a55 50 0 0 1 -110 0z" fill="#f6efe0" stroke="#c8323c" stroke-width="4"/>
<ellipse cx="205" cy="440" rx="55" ry="10" fill="#e9a23b"/>
<path d="M170 440 q10 -8 20 0 t20 0 t20 0" stroke="#fff3b0" stroke-width="4" fill="none"/>
<circle cx="190" cy="438" r="6" fill="#fff"/><circle cx="190" cy="438" r="2.5" fill="#e9a23b"/>
<rect x="225" y="434" width="18" height="5" fill="#2e6b3a"/>
</g>
<g>
<path d="M550 440 h110 a55 50 0 0 1 -110 0z" fill="#f6efe0" stroke="#c8323c" stroke-width="4" transform="translate(0 0)"/>
<ellipse cx="605" cy="440" rx="55" ry="10" fill="#e9a23b"/>
<path d="M570 440 q10 -8 20 0 t20 0 t20 0" stroke="#fff3b0" stroke-width="4" fill="none"/>
<circle cx="630" cy="438" r="6" fill="#fff"/><path d="M590 436 l14 -4 l4 8z" fill="#e87d9a"/>
<path d="M590 420 q-8 -20 0 -35" stroke="#fff" stroke-width="4" fill="none" opacity=".6" stroke-linecap="round"><animate attributeName="opacity" values=".1;.7;.1" dur="2.5s" repeatCount="indefinite"/></path>
<path d="M620 420 q8 -20 0 -35" stroke="#fff" stroke-width="4" fill="none" opacity=".6" stroke-linecap="round"><animate attributeName="opacity" values=".7;.1;.7" dur="2.5s" repeatCount="indefinite"/></path>
</g>
<!-- sign -->
<rect x="300" y="500" width="200" height="60" rx="8" fill="#f6efe0"/><text x="400" y="542" font-size="34" text-anchor="middle" fill="#c8323c" font-family="serif" font-weight="bold">TAKO RAMEN</text>
</svg>'''
open("output/octopus_ramen.svg","w").write(svg)
