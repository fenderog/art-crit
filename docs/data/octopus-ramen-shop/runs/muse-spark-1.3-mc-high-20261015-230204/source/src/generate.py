#!/usr/bin/env python3
"""Generate an octopus-chef ramen booth SVG."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "output" / "octopus-chef-ramen.svg"

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
<title id="title">Octopus chef at a ramen booth</title>
<desc id="desc">A cheerful octopus chef in a tall hat serves steaming ramen bowls from a cozy festival booth with lanterns and a striped awning.</desc>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1A2340"/><stop offset="0.55" stop-color="#2B3A67"/><stop offset="1" stop-color="#5A4A7A"/>
</linearGradient>
<linearGradient id="groundG" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#4A3B5C"/><stop offset="1" stop-color="#2A2138"/>
</linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#C98B54"/><stop offset="1" stop-color="#8A5A2E"/>
</linearGradient>
<linearGradient id="woodDark" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#A9713E"/><stop offset="1" stop-color="#6E4420"/>
</linearGradient>
<radialGradient id="octoBody" cx="0.5" cy="0.35" r="0.8">
<stop offset="0" stop-color="#FF8B8B"/><stop offset="0.55" stop-color="#F2606B"/><stop offset="1" stop-color="#C93A4E"/>
</radialGradient>
<radialGradient id="bowlG" cx="0.5" cy="0.3" r="0.9">
<stop offset="0" stop-color="#FFFFFF"/><stop offset="0.6" stop-color="#DCEAF5"/><stop offset="1" stop-color="#9FB8CC"/>
</radialGradient>
<radialGradient id="broth" cx="0.5" cy="0.5" r="0.6">
<stop offset="0" stop-color="#FFD98A"/><stop offset="0.6" stop-color="#F5A742"/><stop offset="1" stop-color="#C96A1B"/>
</radialGradient>
<radialGradient id="lanternG" cx="0.5" cy="0.45" r="0.65">
<stop offset="0" stop-color="#FFE9A8"/><stop offset="0.55" stop-color="#FFB84D"/><stop offset="1" stop-color="#E07B1A"/>
</radialGradient>
<linearGradient id="hatG" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D9DEE8"/>
</linearGradient>
<linearGradient id="awningRed" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#E94F4F"/><stop offset="1" stop-color="#B91F2E"/>
</linearGradient>
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="soft2" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>

<!-- background -->
<rect width="1200" height="900" fill="url(#sky)"/>
<g fill="#FFFFFF" opacity="0.85">
<circle cx="80" cy="80" r="3"/><circle cx="180" cy="150" r="2.2"/><circle cx="300" cy="70" r="2.6"/><circle cx="950" cy="90" r="3"/><circle cx="1060" cy="170" r="2.2"/><circle cx="1120" cy="70" r="2.6"/><circle cx="700" cy="60" r="2"/><circle cx="520" cy="120" r="2"/><circle cx="420" cy="180" r="1.8"/><circle cx="880" cy="200" r="1.8"/><circle cx="120" cy="240" r="1.6"/><circle cx="1080" cy="260" r="1.6"/>
</g>
<circle cx="1020" cy="130" r="52" fill="#FFF3C4" opacity="0.95"/>
<circle cx="1004" cy="118" r="46" fill="#2B3A67" opacity="0.18"/>
<circle cx="1020" cy="130" r="62" fill="#FFF3C4" opacity="0.14" filter="url(#soft)"/>
<rect y="640" width="1200" height="260" fill="url(#groundG)"/>
<ellipse cx="600" cy="830" rx="520" ry="60" fill="#000000" opacity="0.25" filter="url(#soft)"/>

<!-- festival string lights -->
<path d="M40,210 Q300,320 600,250 Q900,180 1160,260" fill="none" stroke="#1A1426" stroke-width="4"/>
<g>
<g><line x1="200" y1="263" x2="200" y2="288" stroke="#1A1426" stroke-width="3"/><circle cx="200" cy="298" r="12" fill="#FFD66B"/><circle cx="200" cy="298" r="18" fill="#FFD66B" opacity="0.25"/></g>
<g><line x1="340" y1="275" x2="340" y2="300" stroke="#1A1426" stroke-width="3"/><circle cx="340" cy="310" r="12" fill="#FF9D5C"/><circle cx="340" cy="310" r="18" fill="#FF9D5C" opacity="0.25"/></g>
<g><line x1="480" y1="268" x2="480" y2="293" stroke="#1A1426" stroke-width="3"/><circle cx="480" cy="303" r="12" fill="#FFD66B"/><circle cx="480" cy="303" r="18" fill="#FFD66B" opacity="0.25"/></g>
<g><line x1="620" y1="248" x2="620" y2="273" stroke="#1A1426" stroke-width="3"/><circle cx="620" cy="283" r="12" fill="#FF9D5C"/><circle cx="620" cy="283" r="18" fill="#FF9D5C" opacity="0.25"/></g>
<g><line x1="760" y1="225" x2="760" y2="250" stroke="#1A1426" stroke-width="3"/><circle cx="760" cy="260" r="12" fill="#FFD66B"/><circle cx="760" cy="260" r="18" fill="#FFD66B" opacity="0.25"/></g>
<g><line x1="900" y1="218" x2="900" y2="243" stroke="#1A1426" stroke-width="3"/><circle cx="900" cy="253" r="12" fill="#FF9D5C"/><circle cx="900" cy="253" r="18" fill="#FF9D5C" opacity="0.25"/></g>
<g><line x1="1030" y1="232" x2="1030" y2="257" stroke="#1A1426" stroke-width="3"/><circle cx="1030" cy="267" r="12" fill="#FFD66B"/><circle cx="1030" cy="267" r="18" fill="#FFD66B" opacity="0.25"/></g>
</g>

<!-- booth posts -->
<rect x="160" y="300" width="34" height="420" rx="8" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="3"/>
<rect x="1006" y="300" width="34" height="420" rx="8" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="3"/>

<!-- awning -->
<g>
<rect x="110" y="300" width="980" height="26" rx="10" fill="#5C3317"/>
<g>
<rect x="120" y="200" width="98" height="125" fill="url(#awningRed)" stroke="#7A1420" stroke-width="3"/>
<rect x="218" y="200" width="98" height="125" fill="#FFF6E8" stroke="#C9B89A" stroke-width="3"/>
<rect x="316" y="200" width="98" height="125" fill="url(#awningRed)" stroke="#7A1420" stroke-width="3"/>
<rect x="414" y="200" width="98" height="125" fill="#FFF6E8" stroke="#C9B89A" stroke-width="3"/>
<rect x="512" y="200" width="98" height="125" fill="url(#awningRed)" stroke="#7A1420" stroke-width="3"/>
<rect x="610" y="200" width="98" height="125" fill="#FFF6E8" stroke="#C9B89A" stroke-width="3"/>
<rect x="708" y="200" width="98" height="125" fill="url(#awningRed)" stroke="#7A1420" stroke-width="3"/>
<rect x="806" y="200" width="98" height="125" fill="#FFF6E8" stroke="#C9B89A" stroke-width="3"/>
<rect x="904" y="200" width="98" height="125" fill="url(#awningRed)" stroke="#7A1420" stroke-width="3"/>
<rect x="1002" y="200" width="98" height="125" fill="#FFF6E8" stroke="#C9B89A" stroke-width="3"/>
</g>
<g fill="#B91F2E">
<circle cx="169" cy="325" r="24"/><circle cx="267" cy="325" r="24"/><circle cx="365" cy="325" r="24"/><circle cx="463" cy="325" r="24"/><circle cx="561" cy="325" r="24"/><circle cx="659" cy="325" r="24"/><circle cx="757" cy="325" r="24"/><circle cx="855" cy="325" r="24"/><circle cx="953" cy="325" r="24"/><circle cx="1051" cy="325" r="24"/>
</g>
<g fill="#FFF6E8">
<circle cx="218" cy="325" r="24"/><circle cx="316" cy="325" r="24"/><circle cx="414" cy="325" r="24"/><circle cx="512" cy="325" r="24"/><circle cx="610" cy="325" r="24"/><circle cx="708" cy="325" r="24"/><circle cx="806" cy="325" r="24"/><circle cx="904" cy="325" r="24"/><circle cx="1002" cy="325" r="24"/>
</g>
<rect x="380" y="232" width="460" height="66" rx="12" fill="#1E2A52" stroke="#FFD66B" stroke-width="4"/>
<text x="610" y="277" text-anchor="middle" font-family="Verdana, sans-serif" font-weight="bold" font-size="36" fill="#FFD66B" letter-spacing="3">OCTOPUS RAMEN</text>
</g>

<!-- noren curtains -->
<g>
<rect x="300" y="349" width="180" height="130" rx="6" fill="#1E3A6E" stroke="#0F1F3F" stroke-width="3"/>
<rect x="492" y="349" width="180" height="130" rx="6" fill="#1E3A6E" stroke="#0F1F3F" stroke-width="3"/>
<rect x="684" y="349" width="180" height="130" rx="6" fill="#1E3A6E" stroke="#0F1F3F" stroke-width="3"/>
<text x="390" y="430" text-anchor="middle" font-family="Verdana, sans-serif" font-size="56" font-weight="bold" fill="#FFFFFF">たこ</text>
<text x="582" y="430" text-anchor="middle" font-family="Verdana, sans-serif" font-size="56" font-weight="bold" fill="#FFFFFF">ラー</text>
<text x="774" y="430" text-anchor="middle" font-family="Verdana, sans-serif" font-size="56" font-weight="bold" fill="#FFFFFF">メン</text>
<rect x="300" y="349" width="180" height="14" fill="#FFFFFF" opacity="0.15"/>
<rect x="492" y="349" width="180" height="14" fill="#FFFFFF" opacity="0.15"/>
<rect x="684" y="349" width="180" height="14" fill="#FFFFFF" opacity="0.15"/>
</g>

<!-- side lanterns -->
<g>
<line x1="160" y1="326" x2="160" y2="352" stroke="#1A1426" stroke-width="4"/>
<ellipse cx="160" cy="400" rx="52" ry="58" fill="url(#lanternG)" stroke="#8A4A12" stroke-width="3"/>
<ellipse cx="160" cy="400" rx="52" ry="58" fill="none" stroke="#8A4A12" stroke-width="2" opacity="0.4"/>
<path d="M112,385 Q160,395 208,385 M112,410 Q160,420 208,410" stroke="#8A4A12" stroke-width="2" fill="none" opacity="0.7"/>
<rect x="138" y="336" width="44" height="14" rx="4" fill="#3A2110"/>
<rect x="138" y="452" width="44" height="14" rx="4" fill="#3A2110"/>
<text x="160" y="420" text-anchor="middle" font-family="Verdana, sans-serif" font-size="30" font-weight="bold" fill="#7A2400">味</text>
<ellipse cx="160" cy="400" rx="70" ry="74" fill="#FFB84D" opacity="0.18" filter="url(#soft)"/>
</g>
<g>
<line x1="1040" y1="326" x2="1040" y2="352" stroke="#1A1426" stroke-width="4"/>
<ellipse cx="1040" cy="400" rx="52" ry="58" fill="url(#lanternG)" stroke="#8A4A12" stroke-width="3"/>
<path d="M992,385 Q1040,395 1088,385 M992,410 Q1040,420 1088,410" stroke="#8A4A12" stroke-width="2" fill="none" opacity="0.7"/>
<rect x="1018" y="336" width="44" height="14" rx="4" fill="#3A2110"/>
<rect x="1018" y="452" width="44" height="14" rx="4" fill="#3A2110"/>
<text x="1040" y="420" text-anchor="middle" font-family="Verdana, sans-serif" font-size="30" font-weight="bold" fill="#7A2400">麺</text>
<ellipse cx="1040" cy="400" rx="70" ry="74" fill="#FFB84D" opacity="0.18" filter="url(#soft)"/>
</g>

<!-- back shelf + menu -->
<g>
<rect x="230" y="500" width="740" height="90" rx="10" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="3"/>
<rect x="250" y="470" width="150" height="80" rx="8" fill="#FFF8E8" stroke="#4A2C14" stroke-width="3"/>
<text x="325" y="496" text-anchor="middle" font-size="17" font-family="Verdana, sans-serif" font-weight="bold" fill="#4A2C14">MENU</text>
<text x="325" y="518" text-anchor="middle" font-size="14" font-family="Verdana, sans-serif" fill="#7A4A22">Shoyu  ¥800</text>
<text x="325" y="538" text-anchor="middle" font-size="14" font-family="Verdana, sans-serif" fill="#7A4A22">Miso  ¥850</text>
<g>
<rect x="880" y="505" width="52" height="46" rx="6" fill="#7FB069" stroke="#3D6B2E" stroke-width="2"/>
<rect x="936" y="505" width="52" height="46" rx="6" fill="#E94F4F" stroke="#7A1420" stroke-width="2"/>
<ellipse cx="906" cy="498" rx="18" ry="10" fill="#5A8A4A"/>
<ellipse cx="962" cy="498" rx="18" ry="10" fill="#B93A3A"/>
</g>
<g>
<ellipse cx="470" cy="525" rx="34" ry="10" fill="#E8DCC2"/>
<rect x="440" y="525" width="60" height="26" rx="4" fill="#F6EEDC" stroke="#8A6A3E" stroke-width="2"/>
</g>
</g>

<!-- OCTOPUS CHEF -->
<g id="octopus">
<!-- back arms -->
<path d="M470,640 C400,640 350,600 345,545 C343,520 360,505 378,512 C396,519 398,545 415,570 C435,600 470,610 490,615 Z" fill="#C93A4E" stroke="#7E1F2E" stroke-width="4"/>
<path d="M730,640 C800,640 850,600 855,545 C857,520 840,505 822,512 C804,519 802,545 785,570 C765,600 730,610 710,615 Z" fill="#C93A4E" stroke="#7E1F2E" stroke-width="4"/>
<g fill="#FFD0D0" opacity="0.9">
<circle cx="362" cy="552" r="8"/><circle cx="372" cy="572" r="9"/><circle cx="388" cy="592" r="9"/>
<circle cx="838" cy="552" r="8"/><circle cx="828" cy="572" r="9"/><circle cx="812" cy="592" r="9"/>
</g>

<!-- body -->
<ellipse cx="600" cy="540" rx="155" ry="150" fill="url(#octoBody)" stroke="#7E1F2E" stroke-width="5"/>
<!-- head highlight -->
<ellipse cx="540" cy="470" rx="42" ry="58" fill="#FFFFFF" opacity="0.22" filter="url(#soft2)"/>
<!-- spots -->
<g fill="#B92E44" opacity="0.55">
<circle cx="500" cy="580" r="14"/><circle cx="700" cy="580" r="14"/><circle cx="520" cy="620" r="10"/><circle cx="680" cy="620" r="10"/>
</g>

<!-- scarf -->
<path d="M490,640 Q600,690 710,640 L700,670 Q600,720 500,670 Z" fill="#2AA5A0" stroke="#14605D" stroke-width="4"/>
<path d="M585,678 L575,730 L610,725 L625,682 Z" fill="#1F7F7B" stroke="#14605D" stroke-width="3"/>

<!-- apron -->
<path d="M520,660 Q600,690 680,660 L670,750 L530,750 Z" fill="#FFF6E8" stroke="#7E1F2E" stroke-width="4"/>
<text x="600" y="715" text-anchor="middle" font-family="Verdana, sans-serif" font-weight="bold" font-size="30" fill="#C93A4E">たこ</text>

<!-- chef hat -->
<g>
<ellipse cx="600" cy="415" rx="95" ry="22" fill="#BFC8DC" stroke="#7A8499" stroke-width="3"/>
<path d="M515,415 C500,340 520,300 560,305 C565,275 635,275 640,305 C680,300 700,340 685,415 Z" fill="url(#hatG)" stroke="#7A8499" stroke-width="4"/>
<path d="M550,330 Q555,370 550,405 M600,322 Q600,365 600,408 M650,330 Q645,370 650,405" stroke="#B9C2D4" stroke-width="4" fill="none" stroke-linecap="round"/>
<rect x="528" y="398" width="144" height="30" rx="10" fill="#FFFFFF" stroke="#7A8499" stroke-width="3"/>
</g>

<!-- face -->
<ellipse cx="545" cy="530" rx="34" ry="42" fill="#FFFFFF" stroke="#7E1F2E" stroke-width="4"/>
<ellipse cx="655" cy="530" rx="34" ry="42" fill="#FFFFFF" stroke="#7E1F2E" stroke-width="4"/>
<circle cx="548" cy="540" r="16" fill="#1E2130"/>
<circle cx="652" cy="540" r="16" fill="#1E2130"/>
<circle cx="554" cy="534" r="6" fill="#FFFFFF"/>
<circle cx="658" cy="534" r="6" fill="#FFFFFF"/>
<ellipse cx="500" cy="575" rx="20" ry="11" fill="#FF9AAE" opacity="0.85"/>
<ellipse cx="700" cy="575" rx="20" ry="11" fill="#FF9AAE" opacity="0.85"/>
<path d="M565,580 Q600,620 635,580 Q625,610 600,612 Q575,610 565,580 Z" fill="#6E1B28" stroke="#4A101A" stroke-width="3"/>
<ellipse cx="600" cy="592" rx="12" ry="6" fill="#FF7B8E"/>

<!-- front arms -->
<!-- left arm waving with towel -->
<path d="M485,600 C430,590 400,555 395,520" fill="none" stroke="#F2606B" stroke-width="46" stroke-linecap="round"/>
<path d="M485,600 C430,590 400,555 395,520" fill="none" stroke="#7E1F2E" stroke-width="54" stroke-linecap="round" opacity="0.25"/>
<path d="M485,600 C430,590 400,555 395,520" fill="none" stroke="#F2606B" stroke-width="46" stroke-linecap="round"/>
<g fill="#FFD9D9"><circle cx="412" cy="548" r="10"/><circle cx="428" cy="568" r="10"/><circle cx="452" cy="582" r="10"/></g>
<g transform="rotate(-18 390 505)">
<rect x="360" y="470" width="60" height="60" rx="8" fill="#FFFFFF" stroke="#7A8499" stroke-width="3"/>
<rect x="360" y="485" width="60" height="8" fill="#2AA5A0"/>
<rect x="360" y="500" width="60" height="8" fill="#E94F4F"/>
</g>

<!-- right arm holding ladle over pot -->
<path d="M715,600 C770,590 800,565 815,535" fill="none" stroke="#F2606B" stroke-width="46" stroke-linecap="round"/>
<g fill="#FFD9D9"><circle cx="788" cy="568" r="10"/><circle cx="768" cy="582" r="10"/><circle cx="744" cy="590" r="10"/></g>
<g>
<line x1="815" y1="535" x2="860" y2="460" stroke="#8A5A2E" stroke-width="10" stroke-linecap="round"/>
<circle cx="868" cy="444" r="26" fill="#9AA5B8" stroke="#4A5266" stroke-width="4"/>
<circle cx="868" cy="444" r="14" fill="#DDE4F0"/>
</g>

<!-- middle arm holding chopsticks with noodles -->
<path d="M650,650 C700,660 740,655 770,630" fill="none" stroke="#F2606B" stroke-width="40" stroke-linecap="round" opacity="1"/>
<g>
<line x1="770" y1="630" x2="880" y2="590" stroke="#C98B54" stroke-width="8" stroke-linecap="round"/>
<line x1="770" y1="645" x2="880" y2="610" stroke="#8A5A2E" stroke-width="8" stroke-linecap="round"/>
<path d="M825,610 Q820,640 810,655 Q800,670 815,685 Q830,700 820,720" fill="none" stroke="#FFE9A8" stroke-width="9" stroke-linecap="round"/>
<path d="M845,603 Q840,633 830,648 Q820,663 835,678 Q850,693 840,713" fill="none" stroke="#FFD66B" stroke-width="9" stroke-linecap="round"/>
</g>
<!-- other front arm resting -->
<path d="M550,650 C510,665 470,660 445,640" fill="none" stroke="#F2606B" stroke-width="40" stroke-linecap="round"/>
<g fill="#FFD9D9"><circle cx="478" cy="657" r="9"/><circle cx="500" cy="661" r="9"/></g>
</g>

<!-- big stock pot on side burner -->
<g>
<rect x="786" y="585" width="130" height="40" rx="8" fill="#3A3F52"/>
<ellipse cx="851" cy="585" rx="65" ry="14" fill="#222636"/>
<rect x="796" y="520" width="110" height="65" rx="10" fill="#B8C2D4" stroke="#4A5266" stroke-width="4"/>
<ellipse cx="851" cy="522" rx="55" ry="14" fill="#E8EEF7" stroke="#4A5266" stroke-width="4"/>
<ellipse cx="851" cy="524" rx="44" ry="10" fill="#F5A742"/>
<path d="M820,528 Q830,540 840,530 Q850,520 860,532 Q870,542 880,530" stroke="#C96A1B" stroke-width="3" fill="none"/>
<g stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" fill="none" opacity="0.75">
<path d="M820,490 Q810,470 822,450 Q834,430 824,410"/>
<path d="M851,492 Q845,468 857,448 Q869,428 859,406"/>
<path d="M882,490 Q874,470 886,452 Q897,433 888,413"/>
</g>
</g>

<!-- counter -->
<g>
<rect x="180" y="640" width="840" height="130" rx="12" fill="url(#wood)" stroke="#4A2C14" stroke-width="4"/>
<rect x="180" y="640" width="840" height="22" rx="11" fill="#E8B87E" opacity="0.8"/>
<line x1="300" y1="662" x2="300" y2="770" stroke="#4A2C14" stroke-width="3" opacity="0.5"/>
<line x1="450" y1="662" x2="450" y2="770" stroke="#4A2C14" stroke-width="3" opacity="0.5"/>
<line x1="750" y1="662" x2="750" y2="770" stroke="#4A2C14" stroke-width="3" opacity="0.5"/>
<line x1="900" y1="662" x2="900" y2="770" stroke="#4A2C14" stroke-width="3" opacity="0.5"/>
<rect x="200" y="760" width="800" height="22" rx="8" fill="#5C3317"/>
</g>

<!-- two ramen bowls on counter -->
<g id="bowl1">
<ellipse cx="380" cy="640" rx="78" ry="16" fill="#000000" opacity="0.25"/>
<path d="M305,620 L455,620 L440,690 Q380,705 320,690 Z" fill="url(#bowlG)" stroke="#4A5266" stroke-width="4"/>
<rect x="305" y="613" width="150" height="18" rx="9" fill="#2E6F9E"/>
<ellipse cx="380" cy="615" rx="68" ry="20" fill="url(#broth)" stroke="#8A4A12" stroke-width="3"/>
<path d="M330,612 Q340,600 350,610 Q360,620 370,608 Q380,596 390,608 Q400,620 412,610 Q422,600 430,612" stroke="#FFE9A8" stroke-width="6" fill="none" stroke-linecap="round"/>
<circle cx="355" cy="622" r="16" fill="#FFF6E8" stroke="#E8C87E" stroke-width="3"/>
<circle cx="355" cy="622" r="7" fill="#F5A742"/>
<circle cx="412" cy="620" r="15" fill="#FFFFFF" stroke="#E94F4F" stroke-width="4"/>
<circle cx="412" cy="620" r="6" fill="none" stroke="#E94F4F" stroke-width="3"/>
<g fill="#3D9E4D"><ellipse cx="385" cy="625" rx="7" ry="4" transform="rotate(-20 385 625)"/><ellipse cx="398" cy="618" rx="7" ry="4" transform="rotate(20 398 618)"/><ellipse cx="338" cy="625" rx="6" ry="3.5" transform="rotate(15 338 625)"/></g>
<g stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.7" fill="none">
<path d="M340,590 Q332,572 342,556 Q352,540 344,524"/>
<path d="M380,588 Q374,568 384,552 Q394,536 386,518"/>
<path d="M415,590 Q409,572 419,556 Q429,540 421,526"/>
</g>
<text x="380" y="692" text-anchor="middle" font-family="Verdana, sans-serif" font-size="15" font-weight="bold" fill="#E94F4F">たこ</text>
</g>

<g id="bowl2">
<ellipse cx="700" cy="648" rx="86" ry="17" fill="#000000" opacity="0.25"/>
<path d="M617,628 L783,628 L766,704 Q700,720 634,704 Z" fill="url(#bowlG)" stroke="#4A5266" stroke-width="4"/>
<rect x="617" y="621" width="166" height="19" rx="9" fill="#C93A4E"/>
<ellipse cx="700" cy="623" rx="75" ry="22" fill="url(#broth)" stroke="#8A4A12" stroke-width="3"/>
<path d="M648,620 Q660,606 672,618 Q684,630 696,616 Q708,604 720,616 Q732,628 748,616" stroke="#FFF1C0" stroke-width="7" fill="none" stroke-linecap="round"/>
<circle cx="668" cy="630" r="17" fill="#FFF6E8" stroke="#E8C87E" stroke-width="3"/>
<circle cx="668" cy="630" r="7.5" fill="#F5A742"/>
<circle cx="732" cy="628" r="16" fill="#FFFFFF" stroke="#E94F4F" stroke-width="4"/>
<path d="M724,628 Q732,620 740,628 Q732,636 724,628" fill="#E94F4F"/>
<g fill="#3D9E4D"><ellipse cx="700" cy="633" rx="7" ry="4"/><ellipse cx="712" cy="626" rx="7" ry="4" transform="rotate(20 712 626)"/><ellipse cx="650" cy="633" rx="6" ry="3.5"/></g>
<g>
<line x1="740" y1="600" x2="850" y2="556" stroke="#C98B54" stroke-width="9" stroke-linecap="round"/>
<line x1="744" y1="616" x2="854" y2="574" stroke="#8A5A2E" stroke-width="9" stroke-linecap="round"/>
</g>
<g stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.7" fill="none">
<path d="M660,596 Q652,578 662,562 Q672,546 664,530"/>
<path d="M700,594 Q694,574 704,558 Q714,542 706,526"/>
<path d="M738,596 Q732,578 742,562 Q752,546 744,530"/>
</g>
</g>

<!-- side dishes -->
<g>
<ellipse cx="920" cy="648" rx="52" ry="11" fill="#000000" opacity="0.22"/>
<rect x="878" y="612" width="84" height="28" rx="8" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="3"/>
<g fill="#E94F4F"><circle cx="900" cy="606" r="11"/><circle cx="920" cy="606" r="11"/><circle cx="940" cy="606" r="11"/></g>
<g fill="#7FB069"><ellipse cx="900" cy="600" rx="5" ry="8"/><ellipse cx="920" cy="600" rx="5" ry="8"/><ellipse cx="940" cy="600" rx="5" ry="8"/></g>
</g>
<g>
<ellipse cx="250" cy="648" rx="44" ry="10" fill="#000000" opacity="0.22"/>
<rect x="222" y="600" width="56" height="44" rx="6" fill="#F6EEDC" stroke="#8A6A3E" stroke-width="3"/>
<g stroke="#C98B54" stroke-width="5" stroke-linecap="round"><line x1="232" y1="596" x2="246" y2="560"/><line x1="244" y1="596" x2="258" y2="560"/><line x1="256" y1="596" x2="270" y2="560"/></g>
</g>

<!-- foreground stools -->
<g>
<rect x="320" y="800" width="90" height="22" rx="8" fill="#5C3317"/>
<rect x="332" y="782" width="66" height="24" rx="6" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="2"/>
<rect x="790" y="800" width="90" height="22" rx="8" fill="#5C3317"/>
<rect x="802" y="782" width="66" height="24" rx="6" fill="url(#woodDark)" stroke="#4A2C14" stroke-width="2"/>
</g>
<text x="600" y="872" text-anchor="middle" font-family="Verdana, sans-serif" font-size="22" fill="#FFD66B" letter-spacing="2">steaming bowls &#8226; happy tentacles &#8226; late-night ramen</text>
</svg>
"""

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(SVG, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
