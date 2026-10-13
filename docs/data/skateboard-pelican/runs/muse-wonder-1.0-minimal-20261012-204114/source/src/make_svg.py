import pathlib
svg = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900" role="img" aria-labelledby="t d">
<title id="t">Pelican riding a skateboard</title><desc id="d">A cheerful white pelican with a long orange beak cruising on a teal skateboard along a sunny seaside promenade.</desc>
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7ed6f2"/><stop offset=".65" stop-color="#c9f2fb"/><stop offset="1" stop-color="#fff3c9"/></linearGradient>
 <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2bb3c0"/><stop offset="1" stop-color="#147f9e"/></linearGradient>
 <linearGradient id="beak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffb340"/><stop offset="1" stop-color="#ff7a2f"/></linearGradient>
 <linearGradient id="deck" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5d73"/><stop offset="1" stop-color="#ffb340"/></linearGradient>
 <radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff7ae"/><stop offset=".7" stop-color="#ffd94d"/><stop offset="1" stop-color="#ffb340"/></radialGradient>
 <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="1200" height="900" fill="url(#sky)"/>
<circle cx="1035" cy="135" r="72" fill="url(#sun)"/><g stroke="#ffd94d" stroke-width="10" stroke-linecap="round"><path d="M1035 25v-15M1145 135h15M925 135h-15M1113 57l11-11M957 57l-11-11M1113 213l11 11M957 213l-11 11"/></g>
<g fill="#fff" opacity=".9"><ellipse cx="180" cy="130" rx="95" ry="34"/><ellipse cx="250" cy="110" rx="70" ry="38"/><ellipse cx="760" cy="90" rx="80" ry="26"/><ellipse cx="825" cy="75" rx="55" ry="28"/></g>
<!-- sea & beach -->
<path d="M0 470 Q300 440 600 470 T1200 470 V650 H0Z" fill="url(#sea)"/>
<g stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".7" fill="none"><path d="M70 520q40-18 80 0t80 0M820 540q40-18 80 0t80 0M420 590q40-18 80 0t80 0"/></g>
<path d="M0 640 Q600 610 1200 645 V900 H0Z" fill="#f7d99a"/>
<rect y="690" width="1200" height="210" fill="#e9b978"/>
<g stroke="#c98f4e" stroke-width="4" opacity=".55"><path d="M0 735h1200M0 790h1200M0 845h1200"/></g>
<!-- palms -->
<g stroke="#7a4a21" stroke-width="16" fill="none" stroke-linecap="round"><path d="M90 700Q75 560 110 470M1115 705Q1135 570 1100 485"/></g>
<g stroke="#2e9e5b" stroke-width="13" fill="none" stroke-linecap="round"><path d="M110 470Q50 430 15 455M110 470Q95 410 55 395M110 470Q150 410 195 405M110 470Q170 445 205 470M1100 485Q1040 445 1005 470M1100 485Q1090 425 1050 410M1100 485Q1140 425 1185 420"/></g>
<!-- speed lines -->
<g stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".8"><path d="M115 505h130M70 565h170M135 625h110"/></g>
<!-- shadow -->
<ellipse cx="610" cy="782" rx="285" ry="28" fill="#8a5a22" opacity=".28" filter="url(#soft)"/>
<!-- skateboard -->
<g transform="rotate(-3 610 735)">
 <rect x="360" y="718" width="520" height="30" rx="15" fill="url(#deck)"/>
 <rect x="360" y="718" width="520" height="10" rx="5" fill="#fff" opacity=".35"/>
 <g fill="#263238"><circle cx="455" cy="775" r="30"/><circle cx="785" cy="775" r="30"/></g>
 <g fill="#eceff1"><circle cx="455" cy="775" r="13"/><circle cx="785" cy="775" r="13"/></g>
 <circle cx="455" cy="775" r="5" fill="#ff5d73"/><circle cx="785" cy="775" r="5" fill="#ff5d73"/>
 <rect x="435" y="746" width="40" height="10" fill="#78909c"/><rect x="765" y="746" width="40" height="10" fill="#78909c"/>
</g>
<!-- pelican legs -->
<g stroke="#ff8a2a" stroke-width="15" stroke-linecap="round" fill="none"><path d="M565 640 L500 725 M680 630 L760 722"/></g>
<g fill="#ff8a2a"><path d="M500 725l-38 8 38 12 18-10zM760 722l42 6-32 16-22-10z"/></g>
<!-- body -->
<ellipse cx="615" cy="535" rx="185" ry="125" fill="#fff" transform="rotate(-8 615 535)"/>
<ellipse cx="650" cy="560" rx="140" ry="90" fill="#eef6f8" transform="rotate(-8 650 560)"/>
<!-- wing -->
<path d="M505 490 Q660 440 715 545 Q640 625 520 590 Q460 545 505 490Z" fill="#dbeef3"/>
<path d="M530 520 Q630 485 685 540 M545 560 Q625 540 670 570" stroke="#9fc6d3" stroke-width="7" fill="none" stroke-linecap="round"/>
<!-- tail -->
<path d="M445 500 L345 455 L370 520 L335 545 L445 570Z" fill="#e6f2f5"/>
<!-- neck head -->
<path d="M735 480 Q790 390 760 295 Q745 240 800 215" fill="none" stroke="#fff" stroke-width="62" stroke-linecap="round"/>
<circle cx="815" cy="215" r="58" fill="#fff"/>
<path d="M790 165 Q815 115 850 160 Q825 145 815 175 Q800 140 790 165Z" fill="#ffe082"/>
<!-- beak -->
<path d="M860 205 L1085 255 L865 255 Q845 230 860 205Z" fill="url(#beak)"/>
<path d="M865 250 Q970 285 1085 255 Q960 300 875 262Z" fill="#ff9435"/>
<circle cx="1085" cy="255" r="7" fill="#e65100"/>
<path d="M862 228 Q960 235 1030 248" stroke="#e65100" stroke-width="4" fill="none" opacity=".5"/>
<!-- eye / smile -->
<circle cx="828" cy="205" r="10" fill="#263238"/><circle cx="831" cy="202" r="3.5" fill="#fff"/>
<path d="M845 235 Q830 245 815 240" stroke="#90a4ae" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="795" cy="230" r="12" fill="#ffb3ba" opacity=".8"/>
<!-- scarf -->
<path d="M750 275 Q800 295 845 270 L855 295 Q800 325 745 300Z" fill="#ff5d73"/>
<path d="M755 292 Q700 320 660 305 L690 350 Q735 330 760 315Z" fill="#e63950"/>
<!-- fish in pouch hint -->
<circle cx="935" cy="272" r="8" fill="#4dd0e1"/>
<!-- birds -->
<g stroke="#37474f" stroke-width="4" fill="none" stroke-linecap="round"><path d="M300 180q15-15 30 0q15-15 30 0M390 215q12-12 24 0q12-12 24 0"/></g>
<text x="600" y="878" text-anchor="middle" font-family="Verdana, sans-serif" font-size="28" font-weight="700" letter-spacing="4" fill="#7a4a21">CRUISIN' THE COAST</text>
</svg>'''
out=pathlib.Path("output"); out.mkdir(exist_ok=True)
(out/"pelican-skateboard.svg").write_text(svg)
print(len(svg))
