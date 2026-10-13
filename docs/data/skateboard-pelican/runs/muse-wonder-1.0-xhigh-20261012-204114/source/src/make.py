from pathlib import Path
svg = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">
<title>Pelican riding a skateboard</title>
<desc>A cheerful pelican in a teal cap and pink scarf rides a skateboard along a sunny seaside boardwalk.</desc>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#63BCE5"/><stop offset=".55" stop-color="#AEE3F5"/><stop offset="1" stop-color="#FFE7B3"/></linearGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#25A8B5"/><stop offset="1" stop-color="#62C9B0"/></linearGradient>
<radialGradient id="sun"><stop offset="0" stop-color="#FFE873"/><stop offset="1" stop-color="#FF9E4F"/></radialGradient>
<linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#DDEEF6"/></linearGradient>
<linearGradient id="beak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFB03A"/><stop offset="1" stop-color="#FF7E3D"/></linearGradient>
<linearGradient id="pouch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFA25E"/><stop offset="1" stop-color="#FF6B4A"/></linearGradient>
<linearGradient id="deck" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00B4A6"/><stop offset=".55" stop-color="#0096C7"/><stop offset="1" stop-color="#4361EE"/></linearGradient>
</defs>
<style>.o{stroke:#16324A;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}.thin{stroke:#16324A;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;fill:none}</style>
<!-- sky, sun, clouds -->
<rect width="1200" height="900" fill="url(#sky)"/>
<circle cx="985" cy="165" r="118" fill="#FFD93D" opacity=".28"/><circle cx="985" cy="165" r="84" fill="url(#sun)" stroke="#E87D2E" stroke-width="5"/>
<g fill="#fff" opacity=".92"><ellipse cx="210" cy="135" rx="92" ry="34"/><ellipse cx="265" cy="118" rx="62" ry="42"/><ellipse cx="145" cy="118" rx="48" ry="28"/></g>
<g fill="#fff" opacity=".8"><ellipse cx="565" cy="92" rx="72" ry="26"/><ellipse cx="608" cy="78" rx="46" ry="32"/></g>
<g fill="#fff" opacity=".75"><ellipse cx="1085" cy="330" rx="62" ry="22"/><ellipse cx="1118" cy="318" rx="38" ry="26"/></g>
<g class="thin" stroke-width="3"><path d="M350 190q14-14 28 0q14-14 28 0"/><path d="M430 235q11-11 22 0q11-11 22 0"/><path d="M90 285q11-11 22 0q11-11 22 0"/></g>
<!-- sea and sailboat -->
<rect y="520" width="1200" height="135" fill="url(#sea)"/>
<g stroke="#DFF9F5" stroke-width="5" stroke-linecap="round" opacity=".8"><path d="M60 565q28-16 56 0t56 0"/><path d="M720 580q28-16 56 0t56 0"/><path d="M960 615q28-16 56 0t56 0"/><path d="M300 620q28-16 56 0t56 0"/></g>
<g><path d="M148 592h92l-16 24h-58z" fill="#EF476F" class="o"/><path d="M192 590V535l38 55z" fill="#fff" class="o"/><path d="M186 590V548l-28 42z" fill="#FFD166" class="o"/></g>
<!-- boardwalk -->
<rect y="650" width="1200" height="250" fill="#F2A65A"/>
<rect y="650" width="1200" height="18" fill="#C97B3D"/>
<g stroke="#C97B3D" stroke-width="5" opacity=".65"><path d="M0 715H1200M0 782H1200M0 850H1200"/><path d="M180 668v47M520 715v67M900 668v47M260 782v68M760 782v68M1080 715v67"/></g>
<g opacity=".5" fill="#FFE3B3"><ellipse cx="190" cy="688" rx="70" ry="7"/><ellipse cx="920" cy="755" rx="90" ry="7"/><ellipse cx="420" cy="825" rx="80" ry="7"/></g>
<!-- palm tree left -->
<path d="M78 660C92 520 88 390 62 255" fill="none" stroke="#8B5A2B" stroke-width="24" stroke-linecap="round"/>
<path d="M78 660C92 520 88 390 62 255" fill="none" stroke="#B07A45" stroke-width="8" stroke-linecap="round" stroke-dasharray="2 34"/>
<g fill="none" stroke="#1B9E6B" stroke-width="17" stroke-linecap="round"><path d="M64 258Q-10 205 -48 245"/><path d="M64 252Q10 160 -42 150"/><path d="M66 248Q80 145 150 125"/><path d="M68 254Q155 185 218 205"/><path d="M66 260Q140 250 178 292"/></g>
<circle cx="52" cy="272" r="17" fill="#7A4A21" class="o"/><circle cx="82" cy="278" r="15" fill="#8B5A2B" class="o"/>
<!-- ground props -->
<g transform="translate(1035 825)"><path d="M0-28l9 20 22 2-17 14 5 22-19-12-19 12 5-22-17-14 22-2z" fill="#FF8C42" class="o"/></g>
<g transform="translate(135 838) rotate(-18)"><path d="M-34 12Q-30-24 8-28Q42-24 34 12Q0 28-34 12z" fill="#FFB4C8" class="o"/><path class="thin" d="M-18-12Q0 8 18-14M-26 2Q0 16 26 0"/></g>
<ellipse cx="600" cy="812" rx="315" ry="30" fill="#7A3B12" opacity=".18"/>
<!-- speed lines -->
<g stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".85"><path d="M92 455h150M55 515h190M118 590h130"/></g>
<g stroke="#2AA8B5" stroke-width="7" stroke-linecap="round" opacity=".7"><path d="M150 485h105M95 555h120"/></g>
'''
Path("output").mkdir(exist_ok=True)
Path("output/pelican-skateboard.svg").write_text(svg, encoding="utf-8")
print("part1")
