#!/usr/bin/env python3
"""Generate an awkward robot family portrait SVG (no text)."""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "output" / "family-portrait.svg"

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-label="Awkward family portrait of six robots">
<defs>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#2e3348"/><stop offset="0.7" stop-color="#565b78"/><stop offset="1" stop-color="#6e6a72"/>
</linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#8a6f52"/><stop offset="0.25" stop-color="#a58560"/><stop offset="1" stop-color="#5e4a36"/>
</linearGradient>
<radialGradient id="spot" cx="0.5" cy="0.35" r="0.9">
<stop offset="0" stop-color="#fff8e8" stop-opacity="0.55"/><stop offset="0.45" stop-color="#fff2d0" stop-opacity="0.18"/><stop offset="1" stop-color="#000000" stop-opacity="0.35"/>
</radialGradient>
<linearGradient id="dadBody" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#3c4a5e"/><stop offset="0.5" stop-color="#5b6f8a"/><stop offset="1" stop-color="#334052"/>
</linearGradient>
<linearGradient id="dadHead" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#7d90a8"/><stop offset="1" stop-color="#4a5a72"/>
</linearGradient>
<linearGradient id="momBody" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#4fa89a"/><stop offset="0.5" stop-color="#9ad9cc"/><stop offset="1" stop-color="#3d7f76"/>
</linearGradient>
<linearGradient id="teenBody" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#5b4a7a"/><stop offset="0.5" stop-color="#8a76b8"/><stop offset="1" stop-color="#463a63"/>
</linearGradient>
<linearGradient id="kidBody" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#c96a26"/><stop offset="0.5" stop-color="#f5a54a"/><stop offset="1" stop-color="#a34e1c"/>
</linearGradient>
<linearGradient id="babyBody" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#d9dee8"/><stop offset="1" stop-color="#8e98ac"/>
</linearGradient>
<linearGradient id="dogBody" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#b8a88e"/><stop offset="1" stop-color="#7a6c58"/>
</linearGradient>
<radialGradient id="flash" cx="0.35" cy="0.3" r="0.5">
<stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</radialGradient>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity="0.45"/>
</filter>
</defs>

<!-- backdrop -->
<rect width="1200" height="690" fill="url(#wall)"/>
<rect y="660" width="1200" height="240" fill="url(#floor)"/>
<!-- floor boards -->
<g stroke="#4a3828" stroke-width="3" opacity="0.5">
<line x1="0" y1="720" x2="1200" y2="710"/><line x1="0" y1="775" x2="1200" y2="760"/><line x1="0" y1="835" x2="1200" y2="820"/>
<line x1="150" y1="665" x2="110" y2="900"/><line x1="450" y1="665" x2="430" y2="900"/><line x1="750" y1="665" x2="760" y2="900"/><line x1="1050" y1="665" x2="1080" y2="900"/>
</g>
<!-- curtains -->
<g opacity="0.95">
<rect x="0" y="0" width="110" height="670" fill="#4a2430"/>
<g fill="#6b3444" opacity="0.9">
<rect x="8" y="0" width="18" height="670" rx="9"/><rect x="34" y="0" width="18" height="670" rx="9"/><rect x="60" y="0" width="18" height="670" rx="9"/><rect x="86" y="0" width="14" height="670" rx="7"/>
</g>
<rect x="1090" y="0" width="110" height="670" fill="#4a2430"/>
<g fill="#6b3444" opacity="0.9">
<rect x="1098" y="0" width="18" height="670" rx="9"/><rect x="1124" y="0" width="18" height="670" rx="9"/><rect x="1150" y="0" width="18" height="670" rx="9"/><rect x="1176" y="0" width="14" height="670" rx="7"/>
</g>
</g>
<!-- studio light stand hint left -->
<g opacity="0.5" stroke="#1c1e26" stroke-width="8" stroke-linecap="round">
<line x1="130" y1="660" x2="90" y2="430"/><line x1="90" y1="430" x2="170" y2="400"/>
</g>
<circle cx="178" cy="397" r="22" fill="#fff7d6" opacity="0.9"/>
<circle cx="178" cy="397" r="34" fill="#fff7d6" opacity="0.18"/>

<!-- rug -->
<ellipse cx="600" cy="805" rx="410" ry="72" fill="#7a2e35" opacity="0.95"/>
<ellipse cx="600" cy="805" rx="360" ry="58" fill="none" stroke="#d9b98a" stroke-width="6" stroke-dasharray="18 10" opacity="0.85"/>
<ellipse cx="600" cy="805" rx="300" ry="44" fill="#8f3a42" opacity="0.9"/>

<!-- crooked ancestor frame -->
<g transform="rotate(9 975 190)" filter="url(#soft)">
<rect x="905" y="120" width="140" height="140" rx="6" fill="#2a2118"/>
<rect x="913" y="128" width="124" height="124" fill="#cbbfa8"/>
<circle cx="975" cy="185" r="28" fill="#5a6a84"/>
<rect x="953" y="205" width="44" height="30" rx="6" fill="#5a6a84"/>
<circle cx="966" cy="183" r="6" fill="#ffe66d"/><circle cx="984" cy="183" r="6" fill="#ffe66d"/>
<rect x="962" y="198" width="26" height="5" rx="2.5" fill="#222"/>
</g>
<!-- small plant to fill awkward gap right -->
<g transform="translate(1065 560)">
<path d="M0 120 C -6 70 -10 40 0 0" stroke="#2f5a34" stroke-width="10" fill="none" stroke-linecap="round"/>
<ellipse cx="-28" cy="55" rx="30" ry="14" fill="#3f7a46" transform="rotate(-30 -28 55)"/>
<ellipse cx="28" cy="75" rx="30" ry="14" fill="#4d8f55" transform="rotate(25 28 75)"/>
<ellipse cx="-15" cy="25" rx="24" ry="11" fill="#57a060" transform="rotate(-20 -15 25)"/>
<path d="M-32 120 L32 120 L24 88 L-24 88 Z" fill="#8a4a32"/>
</g>

<!-- ======== TEEN (right, distant, slouched away) ======== -->
<g transform="translate(915 385)" filter="url(#soft)">
<!-- shadow -->
<ellipse cx="20" cy="420" rx="90" ry="14" fill="#000" opacity="0.3"/>
<!-- legs, one crossed, slouch -->
<rect x="-18" y="280" width="34" height="125" rx="12" fill="#33334a"/>
<rect x="22" y="280" width="34" height="125" rx="12" fill="#2b2b40" transform="rotate(8 39 280)"/>
<rect x="-28" y="395" width="60" height="22" rx="10" fill="#22222f"/>
<rect x="25" y="395" width="60" height="22" rx="10" fill="#22222f"/>
<!-- tall thin torso leaning right away from family -->
<g transform="rotate(7)">
<rect x="-55" y="140" width="125" height="155" rx="28" fill="url(#teenBody)"/>
<!-- hoodie pocket + stickers = personality -->
<rect x="-30" y="225" width="75" height="38" rx="10" fill="#2e2547" opacity="0.9"/>
<circle cx="-25" cy="170" r="12" fill="#ff6b9d" opacity="0.95"/>
<circle cx="-25" cy="170" r="5" fill="#2e2547"/>
<rect x="18" y="158" width="26" height="26" rx="4" fill="#ffe66d" transform="rotate(12 31 171)"/>
<rect x="20" y="200" width="34" height="10" rx="5" fill="#222" opacity="0.5"/>
<!-- crossed arms: defensive -->
<g stroke-linecap="round">
<path d="M-50 185 C -10 200 30 205 62 190" stroke="#463a63" stroke-width="28" fill="none"/>
<path d="M-48 215 C -5 200 35 195 60 210" stroke="#5d4f84" stroke-width="26" fill="none"/>
</g>
<circle cx="-52" cy="188" r="13" fill="#9aa2b8"/>
<circle cx="62" cy="208" r="13" fill="#9aa2b8"/>
</g>
<!-- head turned away to viewer's right, eye-roll -->
<g transform="translate(18 -10) rotate(-8)">
<rect x="-52" y="0" width="104" height="110" rx="32" fill="#aab3c8"/>
<rect x="-52" y="0" width="104" height="110" rx="32" fill="none" stroke="#463a63" stroke-width="6"/>
<!-- headphones -->
<path d="M-58 55 C -58 -10 58 -10 58 55" fill="none" stroke="#ff6b9d" stroke-width="14" stroke-linecap="round"/>
<rect x="-72" y="35" width="28" height="48" rx="12" fill="#ff6b9d"/>
<rect x="44" y="35" width="28" height="48" rx="12" fill="#ff6b9d"/>
<!-- visor eyes looking sideways (away from family) -->
<rect x="-36" y="42" width="72" height="30" rx="15" fill="#14141f"/>
<circle cx="18" cy="57" r="9" fill="#fff"/>
<circle cx="21" cy="54" r="4" fill="#14141f"/>
<circle cx="-12" cy="57" r="9" fill="#fff"/>
<circle cx="-9" cy="54" r="4" fill="#14141f"/>
<!-- flat annoyed mouth, off-center -->
<rect x="2" y="92" width="32" height="6" rx="3" fill="#2b2b3a"/>
<!-- chipped paint + bolt -->
<path d="M-48 12 l10 -6 l-4 10 Z" fill="#7a8299"/>
<circle cx="-38" cy="98" r="4" fill="#5a6378"/>
</g>
<!-- antenna bent down = mood -->
<line x1="40" y1="-6" x2="78" y2="18" stroke="#555" stroke-width="6" stroke-linecap="round"/>
<circle cx="82" cy="20" r="8" fill="#ff6b9d" opacity="0.6"/>
</g>

<!-- kid's sneaky arm, reaching behind dad to do bunny ears (drawn first = behind) -->
<g transform="translate(225 560)">
<path d="M48 85 C 110 40 128 -120 140 -250" stroke="#c96a26" stroke-width="28" fill="none" stroke-linecap="round"/>
<g transform="translate(140 -253) rotate(12)">
<circle cx="-14" cy="0" r="11" fill="#9aa2b8"/>
<circle cx="14" cy="0" r="11" fill="#9aa2b8"/>
<rect x="-19" y="-28" width="10" height="30" rx="5" fill="#9aa2b8"/>
<rect x="9" y="-28" width="10" height="30" rx="5" fill="#9aa2b8"/>
</g>
</g>

<!-- ======== DAD (tall stern box) ======== -->
<g transform="translate(415 250)" filter="url(#soft)">
<ellipse cx="0" cy="555" rx="115" ry="15" fill="#000" opacity="0.32"/>
<!-- legs stiff together -->
<rect x="-62" y="400" width="52" height="135" rx="10" fill="#2b3442"/>
<rect x="10" y="400" width="52" height="135" rx="10" fill="#2b3442"/>
<rect x="-72" y="525" width="72" height="26" rx="9" fill="#1c222c"/>
<rect x="0" y="525" width="72" height="26" rx="9" fill="#1c222c"/>
<!-- torso -->
<rect x="-105" y="190" width="210" height="225" rx="18" fill="url(#dadBody)"/>
<rect x="-105" y="190" width="210" height="225" rx="18" fill="none" stroke="#1e2733" stroke-width="6"/>
<!-- chest panel, tie = dad personality -->
<rect x="-55" y="225" width="110" height="95" rx="10" fill="#1e2a3a"/>
<circle cx="-30" cy="250" r="10" fill="#58ff9b"/>
<circle cx="0" cy="250" r="10" fill="#ffcf40"/>
<circle cx="30" cy="250" r="10" fill="#ff5a5a" opacity="0.9"/>
<rect x="-40" y="275" width="80" height="14" rx="7" fill="#7d90a8" opacity="0.6"/>
<rect x="-12" y="225" width="24" height="95" rx="6" fill="#8a1f2b"/>
<rect x="-12" y="225" width="24" height="18" rx="6" fill="#a82f3d"/>
<!-- left arm: heavy hand pinning the wiggling kid by the shoulder -->
<rect x="-145" y="195" width="42" height="190" rx="18" fill="#46586f"/>
<circle cx="-124" cy="395" r="22" fill="#8a98ad"/>
<!-- right arm hovering awkwardly toward mom -->
<g transform="rotate(-18 -10 200)">
<rect x="103" y="195" width="42" height="170" rx="18" fill="#46586f"/>
<circle cx="124" cy="375" r="22" fill="#8a98ad"/>
</g>
<!-- head square stern -->
<g>
<rect x="-80" y="40" width="160" height="135" rx="22" fill="url(#dadHead)"/>
<rect x="-80" y="40" width="160" height="135" rx="22" fill="none" stroke="#1e2733" stroke-width="6"/>
<!-- antennae -->
<line x1="-45" y1="40" x2="-60" y2="5" stroke="#333" stroke-width="8" stroke-linecap="round"/>
<line x1="45" y1="40" x2="60" y2="5" stroke="#333" stroke-width="8" stroke-linecap="round"/>
<circle cx="-61" cy="2" r="9" fill="#ff5a5a"/>
<circle cx="61" cy="2" r="9" fill="#ff5a5a"/>
<!-- mono-visor stern eyes, one half-blink from flash = awkward -->
<rect x="-62" y="85" width="124" height="38" rx="12" fill="#10151d"/>
<rect x="-56" y="90" width="50" height="28" rx="8" fill="#9df2ff"/>
<rect x="6" y="90" width="50" height="28" rx="8" fill="#9df2ff"/>
<circle cx="-31" cy="104" r="7" fill="#102030"/>
<circle cx="31" cy="104" r="7" fill="#102030"/>
<rect x="6" y="102" width="50" height="8" fill="#10151d" opacity="0.85"/>
<!-- thin forced straight mouth -->
<rect x="-35" y="140" width="70" height="7" rx="3.5" fill="#1c232e"/>
<!-- bolts jaw -->
<circle cx="-68" cy="155" r="7" fill="#2c3748" stroke="#aab6c8" stroke-width="2"/>
<circle cx="68" cy="155" r="7" fill="#2c3748" stroke="#aab6c8" stroke-width="2"/>
<!-- flash glare -->
<ellipse cx="-35" cy="65" rx="45" ry="22" fill="url(#flash)" opacity="0.7"/>
</g>
</g>

<!-- ======== KID (small goofy, bunny-ears prank on dad) ======== -->
<g transform="translate(225 560)" filter="url(#soft)">
<ellipse cx="0" cy="255" rx="75" ry="12" fill="#000" opacity="0.3"/>
<!-- legs mid-wiggle, one foot up -->
<rect x="-38" y="150" width="30" height="85" rx="12" fill="#5a3a20"/>
<rect x="8" y="150" width="30" height="60" rx="12" fill="#5a3a20" transform="rotate(18 23 150)"/>
<ellipse cx="-25" cy="240" rx="28" ry="12" fill="#2b2b33"/>
<ellipse cx="55" cy="210" rx="28" ry="12" fill="#2b2b33" transform="rotate(20 55 210)"/>
<!-- body -->
<rect x="-55" y="60" width="110" height="105" rx="26" fill="url(#kidBody)"/>
<rect x="-55" y="60" width="110" height="105" rx="26" fill="none" stroke="#5e2e12" stroke-width="5"/>
<rect x="-30" y="90" width="60" height="36" rx="8" fill="#5e2e12"/>
<circle cx="0" cy="108" r="12" fill="#ffe66d"/>
<!-- band-aid + tape = scrappy kid -->
<rect x="28" y="130" width="34" height="14" rx="7" fill="#f2d8b0" transform="rotate(15 45 137)"/>
<!-- sneaky bunny-ears arm is drawn behind dad, above -->
<!-- other arm bent, hand in pocket-ish -->
<path d="M-52 90 C -80 110 -70 145 -35 150" stroke="#c96a26" stroke-width="26" fill="none" stroke-linecap="round"/>
<!-- head big goofy -->
<g>
<circle cx="0" cy="0" r="58" fill="#f2b95e"/>
<circle cx="0" cy="0" r="58" fill="none" stroke="#5e2e12" stroke-width="5"/>
<!-- propeller beanie -->
<path d="M-50 -28 A58 58 0 0 1 50 -28 L50 -38 A66 20 0 0 0 -50 -38 Z" fill="#3a6fd8"/>
<line x1="0" y1="-52" x2="0" y2="-78" stroke="#333" stroke-width="6"/>
<g transform="translate(0 -82) rotate(18)">
<ellipse cx="-28" cy="0" rx="28" ry="9" fill="#ff5a5a" opacity="0.9"/>
<ellipse cx="28" cy="0" rx="28" ry="9" fill="#3a6fd8" opacity="0.9"/>
</g>
<circle cx="0" cy="-50" r="8" fill="#ffcf40"/>
<!-- huge uneven eyes -->
<ellipse cx="-20" cy="2" rx="16" ry="19" fill="#fff"/>
<ellipse cx="22" cy="6" rx="14" ry="16" fill="#fff"/>
<circle cx="-17" cy="6" r="7" fill="#1a1a1a"/>
<circle cx="25" cy="9" r="6" fill="#1a1a1a"/>
<circle cx="-15" cy="4" r="2.5" fill="#fff"/>
<!-- giant missing-tooth grin -->
<path d="M-32 32 C -10 52 20 52 36 28 C 20 38 0 42 -32 32 Z" fill="#4a1f1f"/>
<rect x="-8" y="42" width="14" height="12" fill="#fff"/>
<path d="M-32 32 C -10 52 20 52 36 28" fill="none" stroke="#4a1f1f" stroke-width="5" stroke-linecap="round"/>
</g>
<!-- motion wiggle lines -->
<g stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.6">
<path d="M-85 80 q-14 20 0 40"/><path d="M-100 80 q-14 20 0 40"/>
</g>
</g>

<!-- ======== MOM (round, clingy, leaning on dad) ======== -->
<g transform="translate(630 380) rotate(-7)" filter="url(#soft)">
<ellipse cx="0" cy="425" rx="105" ry="14" fill="#000" opacity="0.3"/>
<!-- legs short -->
<rect x="-45" y="300" width="36" height="110" rx="14" fill="#33413f"/>
<rect x="9" y="300" width="36" height="110" rx="14" fill="#33413f"/>
<ellipse cx="-27" cy="415" rx="30" ry="12" fill="#222"/>
<ellipse cx="27" cy="415" rx="30" ry="12" fill="#222"/>
<!-- dress-body -->
<path d="M-85 160 C -90 240 -105 280 -120 310 L120 310 C 105 280 90 240 85 160 Z" fill="url(#momBody)"/>
<path d="M-85 160 C -90 240 -105 280 -120 310 L120 310 C 105 280 90 240 85 160 Z" fill="none" stroke="#23423e" stroke-width="6"/>
<rect x="-85" y="150" width="170" height="90" rx="40" fill="url(#momBody)" stroke="#23423e" stroke-width="6"/>
<!-- apron heart -->
<path d="M0 250 c -18 -22 -52 -10 -40 14 c 8 16 28 26 40 34 c 12 -8 32 -18 40 -34 c 12 -24 -22 -36 -40 -14 Z" fill="#ff6b9d" opacity="0.95"/>
<!-- left arm linked toward dad -->
<g transform="rotate(18)">
<rect x="-135" y="165" width="36" height="130" rx="18" fill="#3d7f76"/>
<circle cx="-117" cy="300" r="18" fill="#9ad9cc"/>
</g>
<!-- right arm cradling baby -->
<g>
<path d="M85 175 C 130 200 145 250 120 285" stroke="#3d7f76" stroke-width="34" fill="none" stroke-linecap="round"/>
</g>
<!-- head tilted toward dad -->
<g transform="rotate(10)">
<ellipse cx="0" cy="60" rx="82" ry="78" fill="#bde8e0"/>
<ellipse cx="0" cy="60" rx="82" ry="78" fill="none" stroke="#23423e" stroke-width="6"/>
<!-- curly wire hair -->
<g fill="none" stroke="#23423e" stroke-width="7" stroke-linecap="round">
<path d="M-70 10 C -95 -10 -90 -40 -65 -38"/>
<path d="M-45 -10 C -60 -35 -45 -60 -25 -52"/>
<path d="M0 -15 C -5 -40 15 -58 30 -48"/>
<path d="M50 -5 C 60 -30 85 -28 80 -5"/>
<path d="M70 30 C 95 30 98 55 78 60"/>
</g>
<circle cx="-65" cy="-38" r="9" fill="#ff6b9d"/><circle cx="-25" cy="-52" r="9" fill="#ff6b9d"/><circle cx="30" cy="-48" r="9" fill="#ff6b9d"/>
<!-- bow antenna -->
<line x1="45" y1="-10" x2="75" y2="-50" stroke="#23423e" stroke-width="6"/>
<g transform="translate(80 -58) rotate(15)">
<ellipse cx="-12" cy="0" rx="14" ry="10" fill="#ff6b9d"/>
<ellipse cx="12" cy="0" rx="14" ry="10" fill="#ff6b9d"/>
<circle cx="0" cy="0" r="7" fill="#a82f5d"/>
</g>
<!-- overjoyed eyes + huge smile -->
<ellipse cx="-30" cy="55" rx="18" ry="22" fill="#fff"/>
<ellipse cx="30" cy="55" rx="18" ry="22" fill="#fff"/>
<circle cx="-30" cy="60" r="10" fill="#1e3a3a"/>
<circle cx="30" cy="60" r="10" fill="#1e3a3a"/>
<circle cx="-27" cy="56" r="3.5" fill="#fff"/><circle cx="33" cy="56" r="3.5" fill="#fff"/>
<!-- blush -->
<ellipse cx="-55" cy="90" rx="14" ry="8" fill="#ff9db8" opacity="0.8"/>
<ellipse cx="55" cy="90" rx="14" ry="8" fill="#ff9db8" opacity="0.8"/>
<path d="M-38 95 C -15 118 15 118 38 95 C 30 115 12 128 0 128 C -12 128 -30 115 -38 95 Z" fill="#5a1f2a"/>
<path d="M-30 102 C -12 114 12 114 30 102" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>
</g>
</g>

<!-- ======== BABY (held, wailing) ======== -->
<g transform="translate(730 560) rotate(12)" filter="url(#soft)">
<!-- blanket wrap -->
<rect x="-58" y="-20" width="116" height="110" rx="28" fill="url(#babyBody)" stroke="#4a5468" stroke-width="5"/>
<path d="M-58 30 L58 30 L40 90 L-40 90 Z" fill="#ff9db8" opacity="0.9"/>
<!-- arms flailing up (upset) -->
<path d="M-55 -5 L-85 -35" stroke="#8e98ac" stroke-width="18" stroke-linecap="round"/>
<path d="M55 -5 L85 -30" stroke="#8e98ac" stroke-width="18" fill="none" stroke-linecap="round"/>
<circle cx="-88" cy="-38" r="12" fill="#c8cfdd"/>
<circle cx="88" cy="-32" r="12" fill="#c8cfdd"/>
<!-- face -->
<circle cx="0" cy="18" r="42" fill="#e8ecf3" stroke="#4a5468" stroke-width="4"/>
<!-- squeezed crying eyes -->
<path d="M-28 12 q10 8 20 0" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M8 12 q10 8 20 0" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
<!-- oil tears -->
<path d="M-24 22 c -8 12 -8 18 0 22 c 8 -4 8 -10 0 -22 Z" fill="#58c4ff"/>
<path d="M24 22 c -8 12 -8 18 0 22 c 8 -4 8 -10 0 -22 Z" fill="#58c4ff"/>
<!-- wailing mouth -->
<ellipse cx="0" cy="48" rx="16" ry="18" fill="#5a1f2a"/>
<ellipse cx="0" cy="53" rx="8" ry="8" fill="#ff7a7a"/>
<!-- single propeller / rattle antenna -->
<line x1="0" y1="-20" x2="0" y2="-48" stroke="#4a5468" stroke-width="6"/>
<circle cx="0" cy="-54" r="12" fill="#ffe66d" stroke="#4a5468" stroke-width="4"/>
<circle cx="0" cy="-54" r="4" fill="#ff5a5a"/>
<!-- cry lines -->
<g stroke="#9df2ff" stroke-width="4" stroke-linecap="round" opacity="0.9">
<path d="M-52 -8 l-14 -8"/><path d="M-54 8 l-16 0"/><path d="M52 -8 l14 -8"/><path d="M54 8 l16 0"/>
</g>
</g>

<!-- ======== DOG (front, distracted by butterfly) ======== -->
<g transform="translate(560 700)" filter="url(#soft)">
<ellipse cx="0" cy="110" rx="110" ry="13" fill="#000" opacity="0.3"/>
<!-- tail wagging (motion) -->
<g stroke="#7a6c58" stroke-width="18" stroke-linecap="round">
<path d="M-70 70 C -110 60 -125 30 -115 10" fill="none"/>
</g>
<g stroke="#fff" stroke-width="4" opacity="0.5" stroke-linecap="round">
<path d="M-128 18 q-10 -10 0 -22"/><path d="M-142 24 q-10 -12 0 -26"/>
</g>
<!-- body loaf -->
<rect x="-75" y="30" width="150" height="70" rx="30" fill="url(#dogBody)"/>
<rect x="-75" y="30" width="150" height="70" rx="30" fill="none" stroke="#4a3f30" stroke-width="5"/>
<!-- legs -->
<rect x="-60" y="85" width="26" height="30" rx="10" fill="#6b5e4a"/>
<rect x="-10" y="85" width="26" height="30" rx="10" fill="#6b5e4a"/>
<rect x="40" y="85" width="26" height="30" rx="10" fill="#6b5e4a"/>
<!-- head turned 90deg away looking at butterfly, tongue out -->
<g transform="translate(75 10) rotate(18)">
<rect x="-40" y="-40" width="80" height="80" rx="24" fill="#c9bda6" stroke="#4a3f30" stroke-width="5"/>
<!-- ear floppy -->
<path d="M-35 -30 C -60 -25 -62 15 -35 25 Z" fill="#5e5342"/>
<rect x="10" y="-48" width="22" height="40" rx="10" fill="#5e5342" transform="rotate(20 21 -28)"/>
<!-- eyes looking up-right (not at camera) -->
<circle cx="5" cy="5" r="12" fill="#fff"/>
<circle cx="28" cy="5" r="12" fill="#fff"/>
<circle cx="9" cy="1" r="5" fill="#222"/>
<circle cx="32" cy="1" r="5" fill="#222"/>
<!-- nose -->
<ellipse cx="38" cy="28" rx="12" ry="9" fill="#222"/>
<!-- tongue lolling -->
<path d="M28 36 C 28 62 18 78 8 78 C -2 78 0 60 6 38 Z" fill="#ff7a8a" stroke="#a83a4a" stroke-width="3"/>
<line x1="16" y1="45" x2="12" y2="72" stroke="#a83a4a" stroke-width="3"/>
</g>
<!-- collar light -->
<rect x="-10" y="38" width="70" height="16" rx="8" fill="#b83a3a"/>
<circle cx="25" cy="46" r="8" fill="#ffe66d"/>
<!-- butterfly it stares at -->
<g transform="translate(190 -60)">
<ellipse cx="-12" cy="0" rx="14" ry="20" fill="#9db8ff" opacity="0.95" transform="rotate(-20 -12 0)"/>
<ellipse cx="12" cy="0" rx="14" ry="20" fill="#ff9db8" opacity="0.95" transform="rotate(20 12 0)"/>
<rect x="-4" y="-18" width="8" height="36" rx="4" fill="#333"/>
<path d="M-30 -30 q10 -10 20 -4 M-34 -22 q10 -6 18 0" stroke="#333" stroke-width="2" fill="none"/>
<path d="M-20 -5 q-15 10 -25 5 M-18 5 q-12 8 -22 4" stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/>
</g>
<path d="M150 -20 C 160 -5 170 0 185 -35" stroke="#fff" stroke-width="3" stroke-dasharray="6 8" fill="none" opacity="0.6"/>
</g>

<!-- flash vignette + grain -->
<rect width="1200" height="900" fill="url(#spot)"/>
<rect x="14" y="14" width="1172" height="872" fill="none" stroke="#f5ead0" stroke-width="10" opacity="0.85"/>
<rect x="14" y="14" width="1172" height="872" fill="none" stroke="#2a2118" stroke-width="3" opacity="0.9"/>
</svg>'''

OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size/1024:.1f} KB)")
# sanity: no text elements
t = OUT.read_text(encoding="utf-8")
assert "<text" not in t.lower(), "forbidden text found"
print("no-text check passed")
