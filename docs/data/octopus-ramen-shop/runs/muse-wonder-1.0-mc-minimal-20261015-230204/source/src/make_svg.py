#!/usr/bin/env python3
"""Generate an SVG of an octopus chef at a ramen booth."""
import pathlib

svg = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
<title id="title">Octopus chef at a ramen booth</title>
<desc id="desc">A cheerful purple octopus wearing a chef hat and hachimaki, serving ramen behind a Japanese street-food booth with lanterns, noren curtains, bowls and steam.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1b2340"/><stop offset=".55" stop-color="#3a2a52"/><stop offset="1" stop-color="#f2a66b"/>
  </linearGradient>
  <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#a66a3a"/><stop offset="1" stop-color="#7a4522"/>
  </linearGradient>
  <radialGradient id="body" cx=".4" cy=".3" r=".9">
    <stop offset="0" stop-color="#c084fc"/><stop offset=".6" stop-color="#8b5cf6"/><stop offset="1" stop-color="#6d28d9"/>
  </radialGradient>
  <radialGradient id="lantern" cx=".5" cy=".45" r=".65">
    <stop offset="0" stop-color="#fff7c2"/><stop offset=".7" stop-color="#ffb84d"/><stop offset="1" stop-color="#f97316"/>
  </radialGradient>
  <linearGradient id="broth" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#f59e0b"/>
  </linearGradient>
</defs>

<rect width="1200" height="900" fill="url(#sky)"/>
<!-- stars -->
<g fill="#fff" opacity=".85">
  <circle cx="90" cy="70" r="3"/><circle cx="220" cy="120" r="2"/><circle cx="1020" cy="70" r="3"/>
  <circle cx="900" cy="140" r="2"/><circle cx="520" cy="60" r="2"/><circle cx="760" cy="45" r="3"/>
  <circle cx="340" cy="50" r="2"/><circle cx="1120" cy="150" r="2"/>
</g>
<circle cx="1055" cy="95" r="42" fill="#fef3c7"/><circle cx="1040" cy="85" r="36" fill="#3a2a52" opacity=".18"/>
<!-- distant roofs -->
<path d="M0 250 L160 190 L320 250 Z M880 250 L1040 185 L1200 250 Z" fill="#141a33"/>
<rect x="0" y="245" width="1200" height="18" fill="#141a33"/>

<!-- booth frame -->
<rect x="130" y="210" width="940" height="22" rx="8" fill="#5b2e1a"/>
<rect x="170" y="210" width="26" height="500" fill="#6b3418"/>
<rect x="1004" y="210" width="26" height="500" fill="#6b3418"/>
<!-- roof -->
<path d="M95 218 Q600 120 1105 218 L1050 258 Q600 180 150 258 Z" fill="#b91c1c"/>
<path d="M95 218 Q600 120 1105 218" fill="none" stroke="#7f1d1d" stroke-width="10"/>
<g fill="#7f1d1d"><circle cx="220" cy="193" r="7"/><circle cx="400" cy="168" r="7"/><circle cx="600" cy="158" r="7"/><circle cx="800" cy="168" r="7"/><circle cx="980" cy="193" r="7"/></g>

<!-- lanterns -->
<g text-anchor="middle" font-family="serif" font-weight="700">
  <g><line x1="290" y1="232" x2="290" y2="268" stroke="#111" stroke-width="4"/>
  <ellipse cx="290" cy="315" rx="48" ry="52" fill="url(#lantern)" stroke="#c2410c" stroke-width="3"/>
  <path d="M245 295 Q290 310 335 295 M245 335 Q290 350 335 335" fill="none" stroke="#ea580c" stroke-width="2"/>
  <text x="290" y="328" font-size="34" fill="#991b1b">麺</text></g>
  <g><line x1="910" y1="232" x2="910" y2="268" stroke="#111" stroke-width="4"/>
  <ellipse cx="910" cy="315" rx="48" ry="52" fill="url(#lantern)" stroke="#c2410c" stroke-width="3"/>
  <path d="M865 295 Q910 310 955 295 M865 335 Q910 350 955 335" fill="none" stroke="#ea580c" stroke-width="2"/>
  <text x="910" y="328" font-size="30" fill="#991b1b">蛸</text></g>
  <g><ellipse cx="600" cy="285" rx="38" ry="42" fill="url(#lantern)" stroke="#c2410c" stroke-width="3"/>
  <text x="600" y="297" font-size="26" fill="#991b1b">凧</text></g>
</g>

<!-- noren curtains -->
<g>
  <path d="M196 232 h808 v105 q-67 22 -134 0 q-67 22 -134 0 q-67 22 -135 0 q-67 22 -135 0 q-67 22 -135 0 q-67 22 -135 0 Z" fill="#1e3a5f"/>
  <g stroke="#f8fafc" stroke-width="3" opacity=".7"><line x1="330" y1="232" x2="330" y2="330"/><line x1="465" y1="232" x2="465" y2="338"/><line x1="600" y1="232" x2="600" y2="342"/><line x1="735" y1="232" x2="735" y2="338"/><line x1="870" y1="232" x2="870" y2="330"/></g>
  <text x="600" y="295" text-anchor="middle" font-family="sans-serif" font-size="34" font-weight="800" letter-spacing="6" fill="#fff">たこ ラーメン</text>
  <text x="600" y="322" text-anchor="middle" font-family="sans-serif" font-size="13" letter-spacing="5" fill="#fde68a">TAKO RAMEN • EST. 2026</text>
</g>

<!-- back shelf, pots, steam -->
<rect x="230" y="430" width="740" height="14" rx="6" fill="#5b2e1a"/>
<g>
  <path d="M300 430 v-55 h110 v55 Z" fill="#94a3b8" stroke="#475569" stroke-width="4"/>
  <rect x="290" y="365" width="130" height="14" rx="6" fill="#475569"/>
  <path d="M760 430 v-48 h120 v48 Z" fill="#cbd5e1" stroke="#475569" stroke-width="4"/>
  <rect x="750" y="372" width="140" height="14" rx="6" fill="#475569"/>
</g>
<g fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".75">
  <path d="M340 350 q-14 -22 0 -38 q14 -16 0 -34"/><path d="M375 350 q-14 -22 0 -38 q14 -16 0 -34"/>
  <path d="M810 358 q-14 -20 0 -34 q14 -14 0 -30"/>
</g>
<!-- small bowls on shelf -->
<g><path d="M500 430 a38 18 0 0 0 76 0 Z" fill="#dc2626"/><path d="M650 430 a38 18 0 0 0 76 0 Z" fill="#0ea5e9"/></g>

<!-- OCTOPUS -->
<g>
  <!-- tentacles behind counter -->
  <g fill="none" stroke="#7c3aed" stroke-width="34" stroke-linecap="round">
    <path d="M445 560 Q360 590 320 545 Q285 505 330 485"/>
    <path d="M755 560 Q840 590 880 545 Q915 505 870 485"/>
    <path d="M480 590 Q430 640 360 625"/>
    <path d="M720 590 Q770 640 840 625"/>
  </g>
  <g fill="#fde68a"><circle cx="330" cy="488" r="7"/><circle cx="305" cy="515" r="6"/><circle cx="872" cy="488" r="7"/><circle cx="897" cy="515" r="6"/></g>

  <!-- head/body -->
  <path d="M600 310 C470 310 430 410 435 500 C438 565 490 610 600 610 C710 610 762 565 765 500 C770 410 730 310 600 310Z" fill="url(#body)"/>
  <ellipse cx="520" cy="390" rx="55" ry="38" fill="#fff" opacity=".18"/>
  <!-- spots -->
  <g fill="#5b21b6" opacity=".5"><circle cx="490" cy="465" r="10"/><circle cx="715" cy="455" r="8"/><circle cx="680" cy="520" r="9"/><circle cx="505" cy="535" r="7"/></g>

  <!-- chef hat -->
  <g>
    <path d="M505 335 C470 275 530 235 565 262 C580 225 635 225 648 262 C690 235 745 280 705 335 Z" fill="#fff" stroke="#cbd5e1" stroke-width="4"/>
    <path d="M500 330 h210 v38 q-105 18 -210 0 Z" fill="#f8fafc" stroke="#cbd5e1" stroke-width="4"/>
    <!-- hachimaki -->
    <path d="M462 385 Q600 355 738 385 L738 415 Q600 385 462 415 Z" fill="#dc2626"/>
    <circle cx="600" cy="392" r="16" fill="#fff"/><circle cx="600" cy="392" r="9" fill="#dc2626"/>
    <path d="M738 395 l58 -28 M738 405 l60 -5" stroke="#dc2626" stroke-width="10" stroke-linecap="round"/>
  </g>

  <!-- face -->
  <circle cx="540" cy="455" r="28" fill="#fff"/><circle cx="660" cy="455" r="28" fill="#fff"/>
  <circle cx="545" cy="460" r="13" fill="#111827"/><circle cx="655" cy="460" r="13" fill="#111827"/>
  <circle cx="550" cy="455" r="4" fill="#fff"/><circle cx="660" cy="455" r="4" fill="#fff"/>
  <path d="M505 425 q35 -18 70 0 M625 425 q35 -18 70 0" fill="none" stroke="#4c1d95" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="495" cy="505" rx="24" ry="13" fill="#f9a8d4" opacity=".85"/>
  <ellipse cx="705" cy="505" rx="24" ry="13" fill="#f9a8d4" opacity=".85"/>
  <path d="M565 505 Q600 535 635 505" fill="none" stroke="#4c1d95" stroke-width="6" stroke-linecap="round"/>
  <path d="M585 522 q15 10 30 0" fill="#7f1d1d"/>
</g>

<!-- arms holding bowl + chopsticks -->
<g>
  <path d="M455 545 Q390 560 375 505" fill="none" stroke="#8b5cf6" stroke-width="30" stroke-linecap="round"/>
  <path d="M745 545 Q815 545 835 490" fill="none" stroke="#8b5cf6" stroke-width="30" stroke-linecap="round"/>
  <!-- main bowl -->
  <g>
    <path d="M295 500 h165 a82 82 0 0 1 -165 0Z" fill="#0f766e" stroke="#134e4a" stroke-width="4"/>
    <ellipse cx="378" cy="500" rx="83" ry="16" fill="url(#broth)"/>
    <path d="M315 498 q30 -14 60 0 q30 12 60 0" fill="none" stroke="#fef3c7" stroke-width="7" stroke-linecap="round"/>
    <circle cx="355" cy="496" r="12" fill="#fff"/><circle cx="355" cy="496" r="6" fill="#f59e0b"/>
    <circle cx="400" cy="498" r="10" fill="#86efac"/><rect x="322" y="488" width="28" height="8" rx="4" fill="#f472b6"/>
    <path d="M410 485 L500 425 M425 495 L505 440" stroke="#92400e" stroke-width="7" stroke-linecap="round"/>
    <path d="M470 435 q28 -30 55 -8" fill="none" stroke="#fef3c7" stroke-width="6" stroke-linecap="round"/>
  </g>
  <!-- ladle in other tentacle -->
  <g><path d="M835 490 L905 410" stroke="#92400e" stroke-width="8" stroke-linecap="round"/>
  <ellipse cx="915" cy="400" rx="26" ry="18" fill="#cbd5e1" stroke="#64748b" stroke-width="3" transform="rotate(-35 915 400)"/></g>
</g>

<!-- counter -->
<rect x="150" y="610" width="900" height="28" rx="8" fill="#8a4b24"/>
<rect x="170" y="638" width="860" height="105" fill="url(#wood)"/>
<g stroke="#5b2e1a" stroke-width="3" opacity=".6"><line x1="170" y1="672" x2="1030" y2="672"/><line x1="170" y1="708" x2="1030" y2="708"/></g>
<!-- sign on counter -->
<g><rect x="455" y="655" width="290" height="68" rx="10" fill="#fff7ed" stroke="#7c2d12" stroke-width="3"/>
<text x="600" y="685" text-anchor="middle" font-family="sans-serif" font-size="20" font-weight="800" fill="#7c2d12">本日のおすすめ</text>
<text x="600" y="710" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#9a3412">TAKO SHOYU RAMEN  ¥980</text></g>

<!-- bowls on counter -->
<g>
  <path d="M215 610 h130 a65 50 0 0 1 -130 0Z" fill="#dc2626"/><ellipse cx="280" cy="610" rx="65" ry="12" fill="url(#broth)"/>
  <path d="M245 608 q20 -10 40 0 q20 8 35 0" fill="none" stroke="#fff7cc" stroke-width="5"/>
  <path d="M855 610 h130 a65 50 0 0 1 -130 0Z" fill="#2563eb"/><ellipse cx="920" cy="610" rx="65" ry="12" fill="url(#broth)"/>
  <circle cx="905" cy="608" r="9" fill="#fff"/><circle cx="905" cy="608" r="4" fill="#f59e0b"/>
</g>
<!-- steam from bowls -->
<g fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".8">
  <path d="M270 585 q-12 -18 0 -30 q12 -12 0 -26"/><path d="M920 585 q-12 -18 0 -30 q12 -12 0 -26"/><path d="M378 470 q-12 -18 0 -30"/>
</g>

<!-- stools + ground -->
<rect x="0" y="743" width="1200" height="157" fill="#24162e"/>
<path d="M0 743 h1200" stroke="#f2a66b" stroke-width="3" opacity=".5"/>
<g fill="#7c2d12"><rect x="235" y="760" width="90" height="16" rx="8"/><rect x="270" y="776" width="18" height="55"/><rect x="855" y="760" width="90" height="16" rx="8"/><rect x="890" y="776" width="18" height="55"/><rect x="545" y="760" width="90" height="16" rx="8"/><rect x="580" y="776" width="18" height="55"/></g>
<!-- menu board -->
<g><rect x="60" y="480" width="105" height="150" rx="8" fill="#fff7ed" stroke="#7c2d12" stroke-width="4" transform="rotate(-4 112 555)"/>
<text x="112" y="515" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="800" fill="#7c2d12" transform="rotate(-4 112 555)">MENU</text>
<text x="112" y="545" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444" transform="rotate(-4 112 555)">醤油 ¥980</text>
<text x="112" y="570" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444" transform="rotate(-4 112 555)">味噌 ¥1050</text>
<text x="112" y="595" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444" transform="rotate(-4 112 555)">餃子 ¥450</text></g>

<text x="600" y="872" text-anchor="middle" font-family="sans-serif" font-size="15" letter-spacing="4" fill="#fde68a" opacity=".9">いらっしゃいませ！ WELCOME!</text>
</svg>
'''

out = pathlib.Path("output/octopus-ramen-chef.svg")
out.parent.mkdir(exist_ok=True)
out.write_text(svg, encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size} bytes)")
