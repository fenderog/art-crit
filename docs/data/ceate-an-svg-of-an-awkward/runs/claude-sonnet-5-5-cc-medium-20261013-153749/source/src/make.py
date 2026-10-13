S=[]
a=S.append
a('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800">
<defs>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9d8b4"/><stop offset="1" stop-color="#d4bd8e"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a5a3c"/><stop offset="1" stop-color="#5a3622"/></linearGradient>
<linearGradient id="dad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6f8fb0"/><stop offset=".5" stop-color="#9ab7d4"/><stop offset="1" stop-color="#5f7e9f"/></linearGradient>
<linearGradient id="mom" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d9657f"/><stop offset=".5" stop-color="#f08fa3"/><stop offset="1" stop-color="#c85570"/></linearGradient>
<linearGradient id="teen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4a4f66"/><stop offset=".5" stop-color="#6a708c"/><stop offset="1" stop-color="#3f445a"/></linearGradient>
<linearGradient id="gma" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a8896a"/><stop offset=".5" stop-color="#cdb08c"/><stop offset="1" stop-color="#977858"/></linearGradient>
<linearGradient id="kid" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e8b52e"/><stop offset=".5" stop-color="#ffd860"/><stop offset="1" stop-color="#d9a420"/></linearGradient>
<pattern id="paper" width="60" height="60" patternUnits="userSpaceOnUse"><circle cx="30" cy="30" r="5" fill="#c9ad7c" opacity=".5"/><path d="M0 0L10 10M60 0L50 10M0 60L10 50M60 60L50 50" stroke="#c9ad7c" stroke-width="3" opacity=".5"/></pattern>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#2a1608" stop-opacity=".45"/></radialGradient>
<filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="1200" height="800" fill="url(#wall)"/><rect width="1200" height="640" fill="url(#paper)"/>
<rect y="620" width="1200" height="180" fill="url(#floor)"/>
<rect y="610" width="1200" height="14" fill="#f4ead2"/>
<ellipse cx="620" cy="700" rx="520" ry="70" fill="#9c3d3d"/><ellipse cx="620" cy="700" rx="470" ry="56" fill="none" stroke="#e9c97a" stroke-width="4" stroke-dasharray="14 10"/>
<g transform="rotate(-6 620 130)"><rect x="520" y="60" width="200" height="140" fill="#5b3a22"/><rect x="534" y="74" width="172" height="112" fill="#bfe0ea"/><circle cx="650" cy="110" r="20" fill="#f6d54a"/><path d="M534 186L590 120L630 160L670 130L706 186Z" fill="#6c9a6a"/></g>
<g transform="translate(1060 180)"><rect x="-10" y="-30" width="20" height="40" fill="#7a5a3a"/><ellipse cx="0" cy="-60" rx="55" ry="50" fill="#5f8f5a"/><ellipse cx="-30" cy="-40" rx="30" ry="25" fill="#4d7d4a"/><ellipse cx="25" cy="-80" rx="30" ry="25" fill="#73a56c"/></g>
<rect x="1020" y="150" width="80" height="80" rx="6" fill="#a8613a"/>
''')
def shadow(cx,cy,rx): a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="14" fill="#000" opacity=".3"/>')
def bolt(x,y,r=4): a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#444" opacity=".6"/>')
def hand(x,y,r=13,c="#555"): a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="#222" stroke-width="3"/>')
def eye(x,y,r,px=0,py=0,w="#fff"): a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{w}" stroke="#222" stroke-width="3"/><circle cx="{x+px}" cy="{y+py}" r="{r*.45}" fill="#111"/>')
def L(pts,w,c,o="#222"):
    p=" ".join(f"{x},{y}" for x,y in pts)
    a(f'<polyline points="{p}" fill="none" stroke="{o}" stroke-width="{w+6}" stroke-linecap="round" stroke-linejoin="round"/><polyline points="{p}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

# ---- GRANDPA (chair, left)
shadow(210,622,130)
a('<rect x="95" y="330" width="40" height="250" rx="8" fill="#6b3f26" stroke="#222" stroke-width="4"/><rect x="95" y="520" width="240" height="40" rx="8" fill="#7d4a2c" stroke="#222" stroke-width="4"/><rect x="110" y="560" width="22" height="60" fill="#6b3f26"/><rect x="300" y="560" width="22" height="60" fill="#6b3f26"/>')
a('<rect x="170" y="560" width="26" height="58" fill="#8a6c4e" stroke="#222" stroke-width="4"/><rect x="230" y="560" width="26" height="58" fill="#8a6c4e" stroke="#222" stroke-width="4"/><rect x="155" y="605" width="55" height="18" rx="8" fill="#444"/><rect x="220" y="605" width="55" height="18" rx="8" fill="#444"/>')
a('<rect x="140" y="380" width="150" height="150" rx="22" fill="url(#gma)" stroke="#222" stroke-width="4"/>')
a('<path d="M140 470H290V540H140Z" fill="#7a9a5c" stroke="#222" stroke-width="4"/><path d="M140 490H290M140 515H290" stroke="#e8e0a0" stroke-width="5"/><path d="M175 470V540M215 470V540M255 470V540" stroke="#e8e0a0" stroke-width="5"/>')
a('<rect x="150" y="408" width="130" height="40" rx="6" fill="#8d6e50" stroke="#222" stroke-width="3"/>'); 
for x in (170,200,230,260): bolt(x,428)
# rust
a('<circle cx="250" cy="400" r="9" fill="#a85a2a" opacity=".7"/><circle cx="165" cy="500" r="7" fill="#a85a2a" opacity=".6"/>')
# head
a('<rect x="155" y="285" width="120" height="100" rx="26" fill="url(#gma)" stroke="#222" stroke-width="4"/>')
a('<path d="M170 295Q215 270 262 295" fill="none" stroke="#eee" stroke-width="10" stroke-linecap="round"/>')
a('<path d="M205 285 Q195 250 215 240 Q235 230 225 205" fill="none" stroke="#333" stroke-width="4"/><path d="M225 205l-12-6 14-2-8-12 16 8-6 8z" fill="#ffe44d" stroke="#e08a00" stroke-width="2"/>')
a('<path d="M175 330q14-10 28 0" fill="none" stroke="#222" stroke-width="5" stroke-linecap="round"/>')  # asleep eye
eye(245,330,15,-6,4)  # one eye awake, glancing at dog side? looking right
a('<path d="M170 308l30-6M232 304l28 6" stroke="#eee" stroke-width="7" stroke-linecap="round"/>')
a('<ellipse cx="215" cy="364" rx="14" ry="10" fill="#3a1a1a" stroke="#222" stroke-width="3"/><path d="M190 352q25 10 50 0" fill="none" stroke="#eee" stroke-width="6" stroke-linecap="round"/>')
# cane + hands
L([(290,470),(310,580)],8,"#5a3a22"); a('<path d="M290 470q-2-24 -22-18" fill="none" stroke="#222" stroke-width="12" stroke-linecap="round"/><path d="M290 470q-2-24 -22-18" fill="none" stroke="#5a3a22" stroke-width="6" stroke-linecap="round"/>')
L([(285,430),(300,490)],18,"#a68868"); hand(300,490,14)
L([(145,430),(160,490)],18,"#a68868"); hand(160,490,14)

# ---- DAD
shadow(440,624,95)
L([(415,555),(415,610)],26,"#6f8fb0"); L([(465,555),(465,610)],26,"#6f8fb0")
a('<rect x="388" y="600" width="50" height="22" rx="8" fill="#333"/><rect x="442" y="600" width="50" height="22" rx="8" fill="#333"/>')
a('<rect x="370" y="330" width="140" height="235" rx="12" fill="url(#dad)" stroke="#222" stroke-width="4"/>')
a('<rect x="395" y="380" width="90" height="70" rx="6" fill="#4f6a88" stroke="#222" stroke-width="3"/>')
for i in range(4): a(f'<rect x="405" y="{392+i*14}" width="{50+ (i%2)*20}" height="6" fill="#bfe0ff"/>')
a('<path d="M440 330l-14 20 14 12 14-12z" fill="#b22" stroke="#222" stroke-width="3"/><path d="M440 360l-16 90 16 16 16-16z" fill="#c33" stroke="#222" stroke-width="3"/>')
for x,y in ((380,340),(500,340),(380,555),(500,555)): bolt(x,y)
L([(372,350),(358,460),(358,520)],20,"#6f8fb0"); hand(358,530,15)
L([(508,350),(540,385)],20,"#6f8fb0")
# head
a('<rect x="440" y="258" width="0" height="0"/><rect x="385" y="220" width="110" height="105" rx="10" fill="url(#dad)" stroke="#222" stroke-width="4"/>')
a('<path d="M440 220V190" stroke="#222" stroke-width="5"/><circle cx="440" cy="184" r="9" fill="#e33" stroke="#222" stroke-width="3"/>')
a('<rect x="400" y="248" width="80" height="32" rx="6" fill="#222"/>')
a('<rect x="408" y="253" width="26" height="22" fill="#9ff"/><rect x="446" y="253" width="26" height="22" fill="#9ff"/><rect x="418" y="258" width="8" height="12" fill="#134"/><rect x="456" y="258" width="8" height="12" fill="#134"/>')
a('<path d="M412 304H468" stroke="#222" stroke-width="6" stroke-linecap="round"/><path d="M468 304q6 -6 8 -12" stroke="#222" stroke-width="0"/>')
a('<path d="M400 238H480" stroke="#222" stroke-width="5" stroke-linecap="round" transform="rotate(0)"/>')

# ---- KID
shadow(575,624,55)
L([(560,555),(560,610)],14,"#e8b52e"); L([(592,555),(592,610)],14,"#e8b52e")
a('<ellipse cx="558" cy="615" rx="22" ry="9" fill="#d33" stroke="#222" stroke-width="3"/><ellipse cx="596" cy="612" rx="22" ry="9" fill="#3a3" stroke="#222" stroke-width="3" transform="rotate(-10 596 612)"/>')
a('<rect x="535" y="470" width="82" height="90" rx="18" fill="url(#kid)" stroke="#222" stroke-width="4"/>')
a('<circle cx="576" cy="515" r="16" fill="#e33" stroke="#222" stroke-width="3"/><path d="M570 515h12M576 509v12" stroke="#fff" stroke-width="4"/>')
a('<path d="M575 470v10" stroke="#222" stroke-width="4"/>')
# head (squished by dad's hand, tilted)
a('<g transform="rotate(-6 576 440)"><rect x="525" y="394" width="102" height="82" rx="30" fill="url(#kid)" stroke="#222" stroke-width="4"/>')
a('<path d="M560 394q-4-24 12-30M592 394q10-26 -2-34" fill="none" stroke="#222" stroke-width="4"/><circle cx="572" cy="362" r="6" fill="#e33"/><circle cx="590" cy="358" r="6" fill="#3a3"/>')
eye(553,430,16,3,-5); eye(600,436,10,-2,4)
a('<path d="M545 455q31 22 62 0" fill="#7a1f2a" stroke="#222" stroke-width="3"/><rect x="568" y="466" width="18" height="16" rx="8" fill="#ff7aa0" stroke="#222" stroke-width="3"/><rect x="560" y="454" width="10" height="9" fill="#fff"/><rect x="584" y="456" width="10" height="9" fill="#fff"/></g>')
hand(556,398,16)  # dad's hand pressing on head
L([(540,385),(552,396)],18,"#6f8fb0")
# kid arm up with balloon
L([(617,490),(655,450),(668,400)],12,"#e8b52e"); hand(668,396,11)
a('<path d="M668 396Q650 300 640 220" fill="none" stroke="#333" stroke-width="2"/><ellipse cx="636" cy="170" rx="42" ry="52" fill="#4fb3e8" stroke="#222" stroke-width="4"/><path d="M630 222l6 12 6-12z" fill="#4fb3e8" stroke="#222" stroke-width="3"/><ellipse cx="620" cy="150" rx="10" ry="18" fill="#fff" opacity=".6"/>')
L([(535,500),(515,545),(512,560)],12,"#e8b52e"); hand(512,562,11)

# ---- MOM
shadow(715,624,95)
a('<path d="M655 470H775L800 585H630Z" fill="url(#mom)" stroke="#222" stroke-width="4"/><path d="M650 540H780" stroke="#fff" stroke-width="5" stroke-dasharray="3 12" stroke-linecap="round"/>')
L([(690,585),(690,612)],14,"#c85570"); L([(740,585),(740,612)],14,"#c85570")
a('<rect x="670" y="605" width="42" height="17" rx="8" fill="#a33"/><rect x="718" y="605" width="42" height="17" rx="8" fill="#a33"/>')
a('<rect x="660" y="340" width="110" height="140" rx="30" fill="url(#mom)" stroke="#222" stroke-width="4"/>')
a('<path d="M690 345q25 30 50 0" fill="none" stroke="#fff" stroke-width="6"/>')
for i,x in enumerate((690,715,740)): a(f'<circle cx="{x}" cy="{365+i%2*8}" r="6" fill="#fff" stroke="#222" stroke-width="2"/>')
a('<rect x="680" y="400" width="70" height="40" rx="8" fill="#f9c5d0" stroke="#222" stroke-width="3"/><circle cx="715" cy="420" r="10" fill="#e66" stroke="#222" stroke-width="2"/>')
# head
a('<g transform="rotate(4 715 280)"><path d="M690 236q-28-30 -4-52q18-8 12 14M740 236q28-30 4-52q-18-8 -12 14" fill="none" stroke="#222" stroke-width="5"/><circle cx="684" cy="182" r="8" fill="#ffd860" stroke="#222" stroke-width="3"/><circle cx="746" cy="182" r="8" fill="#ffd860" stroke="#222" stroke-width="3"/>')
a('<rect x="660" y="232" width="110" height="105" rx="40" fill="url(#mom)" stroke="#222" stroke-width="4"/>')
eye(692,278,16,1,1);eye(738,278,16,1,1)
a('<path d="M674 258l-8-8M680 254l-4-10M754 254l4-10M760 258l8-8" stroke="#222" stroke-width="3" stroke-linecap="round"/><path d="M672 262q20-14 40-2M718 260q20-12 40 2" fill="none" stroke="#222" stroke-width="3"/>')
a('<circle cx="672" cy="305" r="9" fill="#ff6f8a" opacity=".6"/><circle cx="758" cy="305" r="9" fill="#ff6f8a" opacity=".6"/>')
a('<path d="M684 308q31 26 62 0Z" fill="#fff" stroke="#c22" stroke-width="5" stroke-linejoin="round"/><path d="M690 311v10M700 314v10M710 316v10M720 316v10M730 314v10M740 311v10" stroke="#999" stroke-width="2"/></g>')
# purse arm
L([(662,375),(640,430),(660,470)],18,"#c85570"); hand(662,474,13)
a('<path d="M660 474v18" stroke="#222" stroke-width="3"/><rect x="636" y="490" width="56" height="40" rx="8" fill="#7a3a8a" stroke="#222" stroke-width="3"/><circle cx="664" cy="500" r="4" fill="#ffd860"/>')

# ---- TEEN (leaning away)
shadow(930,624,70)
a('<g transform="rotate(8 925 620)">')
L([(905,560),(905,610)],18,"#4a4f66"); L([(950,560),(950,610)],18,"#4a4f66")
a('<rect x="880" y="600" width="52" height="22" rx="9" fill="#e8e8e8" stroke="#222" stroke-width="3"/><rect x="930" y="600" width="52" height="22" rx="9" fill="#e8e8e8" stroke="#222" stroke-width="3"/>')
a('<rect x="868" y="360" width="120" height="205" rx="16" fill="url(#teen)" stroke="#222" stroke-width="4"/>')
a('<path d="M868 380L928 450L988 380" fill="none" stroke="#222" stroke-width="4"/><rect x="895" y="480" width="66" height="36" rx="6" fill="#3b3f52" stroke="#222" stroke-width="3"/>')
a('<circle cx="905" cy="498" r="6" fill="#f5a"/><circle cx="928" cy="498" r="6" fill="#5ff"/><circle cx="950" cy="498" r="6" fill="#ff5"/>')
# crossed arms
a('<path d="M870 390Q850 450 920 470M986 390Q1000 450 930 480" fill="none" stroke="#222" stroke-width="26" stroke-linecap="round"/><path d="M870 390Q850 450 920 470M986 390Q1000 450 930 480" fill="none" stroke="#4a4f66" stroke-width="18" stroke-linecap="round"/>')
hand(930,478,11); hand(920,470,11)
# head
a('<g transform="rotate(10 928 320)"><rect x="875" y="250" width="106" height="100" rx="18" fill="url(#teen)" stroke="#222" stroke-width="4"/>')
a('<path d="M890 252q38-50 76 0" fill="#e44" stroke="#222" stroke-width="4"/><path d="M928 202v-20" stroke="#222" stroke-width="4"/><circle cx="928" cy="178" r="6" fill="#5ff"/>')
a('<path d="M878 296q-10-50 50-52q60 2 50 52" fill="none" stroke="#222" stroke-width="12" stroke-linecap="round"/><rect x="862" y="285" width="22" height="42" rx="9" fill="#e44" stroke="#222" stroke-width="3"/><rect x="972" y="285" width="22" height="42" rx="9" fill="#e44" stroke="#222" stroke-width="3"/>')
a('<ellipse cx="910" cy="300" rx="14" ry="12" fill="#fff" stroke="#222" stroke-width="3"/><ellipse cx="948" cy="300" rx="14" ry="12" fill="#fff" stroke="#222" stroke-width="3"/><circle cx="920" cy="296" r="6" fill="#111"/><circle cx="958" cy="296" r="6" fill="#111"/>')
a('<path d="M894 286H926M934 286H966" stroke="#222" stroke-width="10"/><path d="M894 286H926M934 286H966" stroke="#6a708c" stroke-width="5"/>')
a('<path d="M905 336q20-9 40 2" fill="none" stroke="#222" stroke-width="5" stroke-linecap="round"/></g></g>')
# mom's hand on teen's shoulder, arm stretched
L([(768,372),(820,372),(872,392)],18,"#c85570"); hand(880,398,14,"#c85570")

# ---- DOG
shadow(815,626,60)
a('<path d="M860 575q40-20 30-60" fill="none" stroke="#222" stroke-width="12" stroke-linecap="round"/><path d="M860 575q40-20 30-60" fill="none" stroke="#9aa" stroke-width="6" stroke-linecap="round"/><path d="M900 520q12-10 12-24M910 530q18-6 22-20" stroke="#222" stroke-width="3" fill="none" opacity=".5"/>')
a('<rect x="768" y="560" width="22" height="55" rx="8" fill="#aab" stroke="#222" stroke-width="3"/><rect x="826" y="570" width="22" height="45" rx="8" fill="#aab" stroke="#222" stroke-width="3"/>')
a('<rect x="760" y="520" width="100" height="70" rx="26" fill="#bcc" stroke="#222" stroke-width="4"/><rect x="772" y="605" width="36" height="14" rx="6" fill="#788"/>')
a('<rect x="775" y="460" width="76" height="62" rx="16" fill="#cdd" stroke="#222" stroke-width="4"/>')
a('<path d="M775 466l-22 10l-6 40l24-14z" fill="#899" stroke="#222" stroke-width="3"/><path d="M851 466l16-34l12 40l-24 8z" fill="#899" stroke="#222" stroke-width="3"/>')
eye(796,486,10,0,0);eye(830,486,10,0,0)
a('<rect x="800" y="500" width="26" height="14" rx="6" fill="#222"/><path d="M806 520q8 10 18 0v22q-9 10-18 0z" fill="#ff7a9a" stroke="#222" stroke-width="3"/><rect x="778" y="520" width="70" height="8" fill="#e33" stroke="#222" stroke-width="2"/><circle cx="813" cy="534" r="6" fill="#ffd860" stroke="#222" stroke-width="2"/>')

a('<rect width="1200" height="800" fill="url(#vig)"/></svg>')
open("output/family_portrait.svg","w").write("\n".join(S))
