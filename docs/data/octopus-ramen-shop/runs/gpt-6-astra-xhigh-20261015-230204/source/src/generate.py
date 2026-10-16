#!/usr/bin/env python3
"""Draw a self-contained, hand-built vector poster. No external assets or packages."""
from pathlib import Path
from math import sin, cos, pi, atan2, degrees, hypot
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
W, H = 1440, 1560
INK = '#19343e'
NIGHT = '#20434d'
TEAL = '#417874'
PALE = '#f7e8c7'
WHITE = '#fff3d5'
GOLD = '#efbc61'
CORAL = '#ef826d'
RED = '#c65552'
parts = []

def add(s): parts.append(s)
def path(d, fill='none', stroke=INK, sw=4, extra=''):
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')
def rect(x,y,w,h,fill,stroke=INK,sw=4,rx=0,extra=''):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def ellipse(x,y,rx,ry,fill,stroke=INK,sw=4,extra=''):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def circle(x,y,r,fill,stroke='none',sw=0,extra=''):
    ellipse(x,y,r,r,fill,stroke,sw,extra)
def text(x,y,s,size=24,fill=PALE,font='sans-serif',weight='normal',spacing=0,extra=''):
    add(f'<text x="{x}" y="{y}" text-anchor="middle" fill="{fill}" font-family="{font}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" {extra}>{s}</text>')
def use(name,x,y,scale=1,rot=0):
    add(f'<use href="#{name}" transform="translate({x} {y}) rotate({rot}) scale({scale})"/>')

add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description">
<title id="title">Octo Ramen — Eight arms. One perfect bowl.</title>
<desc id="description">A joyful coral octopus in a chef's hat cooks at a lantern-lit Japanese ramen booth. Eight curling, sucker-lined arms juggle a ladle, a bowl, scallions, a knife, a spice shaker, chopsticks, tea, and an egg. Golden noodles fall into a beautifully garnished bowl. An illustrated midnight-market poster in indigo, cream, vermilion, and gold.</desc>
<defs>
 <linearGradient id="night" x2="0" y2="1"><stop stop-color="#18363f"/><stop offset="1" stop-color="#315e63"/></linearGradient>
 <radialGradient id="lampGlow"><stop stop-color="#efb95e" stop-opacity=".27"/><stop offset=".5" stop-color="#efb95e" stop-opacity=".11"/><stop offset="1" stop-color="#efb95e" stop-opacity="0"/></radialGradient>
 <linearGradient id="head" x1="0" y1="0" x2=".2" y2="1"><stop stop-color="#f69a7c"/><stop offset=".6" stop-color="#ef826d"/><stop offset="1" stop-color="#d76861"/></linearGradient>
 <linearGradient id="pot" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#467873"/><stop offset=".37" stop-color="#7da49a"/><stop offset="1" stop-color="#38635f"/></linearGradient>
 <linearGradient id="lantern" x2="1" y2="0"><stop stop-color="#d68c4a"/><stop offset=".45" stop-color="#ffda8a"/><stop offset="1" stop-color="#e7a953"/></linearGradient>
 <linearGradient id="redLantern" x2="1" y2="0"><stop stop-color="#bd504c"/><stop offset=".48" stop-color="#f79573"/><stop offset="1" stop-color="#d76a58"/></linearGradient>
 <clipPath id="poster"><rect x="42" y="42" width="1356" height="1476" rx="16"/></clipPath>
 <pattern id="paper" width="94" height="88" patternUnits="userSpaceOnUse">
  <path d="M7 12h2m40 15h1m28-20h2M18 57h2m48 14h2M85 43h1M35 83h2" stroke="#704e37" opacity=".15" stroke-width="1"/>
  <path d="M23 24h1m45 18h2M8 78h1m75 5h2M46 53h1" stroke="#fff7d9" opacity=".2" stroke-width="1"/>
 </pattern>
 <pattern id="waves" width="80" height="40" patternUnits="userSpaceOnUse">
   <path d="M-40 40a40 40 0 0 1 80 0a40 40 0 0 1 80 0M-30 40a30 30 0 0 1 60 0m20 0a30 30 0 0 1 60 0M-20 40a20 20 0 0 1 40 0m40 0a20 20 0 0 1 40 0M-10 40a10 10 0 0 1 20 0m60 0a10 10 0 0 1 20 0" fill="none" stroke="#e6bc74" stroke-width="2"/>
 </pattern>
 <g id="spark"><path d="M0-15Q3-3 13 0Q3 3 0 15Q-3 3-13 0Q-3-3 0-15Z" fill="#efbc61"/></g>
 <g id="scallion"><ellipse rx="10" ry="6" fill="#83a76d" stroke="#244e48" stroke-width="2.5"/><ellipse rx="4.2" ry="2.4" fill="#f4dc9c"/></g>
 <g id="seed"><ellipse rx="2" ry="4" fill="#ffedb7" transform="rotate(30)"/></g>
 <g id="bowlIcon" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M-29 2Q-25 29 0 29Q25 29 29 2ZM-12 32h24M-32 1h64M-11-7c-10-10 9-11 0-22M3-7c-10-10 9-11 0-22M17-7c-10-10 9-11 0-22"/>
 </g>
 <g id="octoSeal" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M-17 5v-14a17 17 0 0 1 34 0V5M-16 4c-12 0-12 17-23 11-6-4-3-10 1-10M-11 8c-7 10-7 24-17 22-7-2-5-9-2-10M-5 11c-2 12-1 27-9 27-6 0-6-6-4-9M16 4c12 0 12 17 23 11 6-4 3-10-1-10M11 8c7 10 7 24 17 22 7-2 5-9 2-10M5 11c2 12 1 27 9 27 6 0 6-6 4-9M0 13v18"/>
  <circle cx="-6" cy="-7" r="2" fill="currentColor" stroke="none"/><circle cx="6" cy="-7" r="2" fill="currentColor" stroke="none"/>
 </g>
</defs>''')

# The paper edge and the night-market setting.
rect(0,0,W,H,PALE,'none',0)
rect(27,27,1386,1506,'none',INK,2,22)
rect(42,42,1356,1476,'url(#night)','none',0,16)
add('<g clip-path="url(#poster)">')
circle(721,866,567,'#426a69','none',0,extra='opacity=".30"')
circle(721,866,531,'none','#6d9185',1,extra='opacity=".12"')
# Quiet silhouettes, not a competing cityscape.
path('M42 1105V733h86v-63h90v91h77v405H42Z','#21434b','none',0)
path('M1167 1170V745h88v-99h73v69h70v455Z','#21434b','none',0)
for x,y in [(77,779),(77,827),(147,713),(147,761),(1240,775),(1291,696),(1291,746),(1338,790),(1338,840)]:
    rect(x,y,22,28,'#789184','none',0,2,extra='opacity=".25"')
path('M87 1121V934m0 26h44m-24-26v187M1311 1135V929m-24 35h49m-28-35v206',stroke='#739084',sw=2,extra='opacity=".20"')
# Distant paper-light flecks.
rng=random.Random(8)
for _ in range(155):
    x=rng.uniform(73,1367); y=rng.uniform(318,1364)
    circle(round(x,2),round(y,2),rng.choice([.8,1,1.3,1.8]),'#e6ce93','none',0,extra=f'opacity="{rng.uniform(.12,.37):.2f}"')
for x,y,s in [(134,345,.8),(1275,378,.9),(119,579,.55),(1311,608,.6),(156,904,.6),(1286,1114,.5),(1100,322,.4),(334,308,.45)]:
    use('spark',x,y,s)
# Crescent moon, cut with the same quiet sky colour.
path('M1233 280A40 40 0 1 0 1273 329A34 34 0 0 1 1233 280Z',GOLD,'none',0)
path('M1226 272l-4-8m65 50 9 1m-11 29 7 5',stroke='#8da397',sw=2)
# Ground and its softly cut printed shadow.
ellipse(723,1370,569,58,'#183b43','none',0)
ellipse(739,1374,470,29,'#142f39','none',0,extra='opacity=".65"')
path('M113 1378h103m1033 0h76M174 1401h151m775 0h91',stroke='#709187',sw=2,extra='opacity=".45"')

# The stall's structural frame and warm interior.
rect(250,491,940,555,'#182f39',INK,7,6)
rect(275,514,890,507,'#335654','none',0)
rect(288,602,865,364,'#263f42','none',0)
# The back shelf has a few useful, not distracting, kitchen things.
path('M288 849h864v22H288Z','#a67d4e',INK,4)
path('M300 855h838',stroke='#e1b677',sw=2)
for x,ht in [(321,70),(351,90),(1031,79),(1064,58)]:
    rect(x,846-ht,25,ht,'#789084',INK,3,4)
    rect(x+4,840-ht,17,10,GOLD,INK,2,2)
    rect(x+4,813-ht/2,17,23,PALE,'none',0,2)
# Warm light under the canopy, with radial lantern light.
path('M277 514H1165L1084 674H353Z','#b09a66','none',0,extra='opacity=".10"')
for x,y in [(290,664),(1150,668)]: circle(x,y,225,'url(#lampGlow)')
# Back-wall chopsticks and hanging utensils.
path('M953 565h155',stroke='#9eac91',sw=3)
for x in [979,1027,1076]:
    path(f'M{x} 565v19q-10 9 0 17',stroke=GOLD,sw=3)
path('M1027 602v82',stroke='#b7c0a4',sw=7)
ellipse(1027,701,17,25,'#77938a',INK,3)
path('M1017 691q8-13 18 0',stroke='#b7c0a4',sw=2)
path('M1076 600v79m-12 0h24l-3 40h-18Z','#77938a',INK,3)
for x in [1072,1079]: path(f'M{x} 687v24',stroke='#29474a',sw=2)
# Floor supports and two visible feet.
path('M244 1268v94q16 15 45 0l7-94M1153 1268l2 94q25 14 45 0v-94','#8b674a',INK,6)
path('M256 1334v23m912-25v26',stroke='#c99a60',sw=4)
# Uprights, with woodgrain and iron collars.
for x in [234,1169]:
    rect(x,480,38,863,'#a77b4d',INK,6,4)
    path(f'M{x+10} 519v483m0 102v200M{x+27} 535v166m0 51v243',stroke='#d1a568',sw=3)
    for y in [550,974,1283]:
        rect(x-3,y,44,15,INK,INK,2,2)
        circle(x+8,y+7,2.3,'#d5af70');circle(x+31,y+7,2.3,'#d5af70')

# Deep blue split noren with little wave borders.
for i in range(5):
    x=323+i*158
    path(f'M{x} 506h151v98q-70 18-151-1Z',TEAL,INK,4)
    path(f'M{x+9} 521h133',stroke='#75968a',sw=2)
    add(f'<path d="M{x+5} 569h140v27H{x+5}Z" fill="url(#waves)" opacity=".35"/>')
    if i in [0,4]:
        circle(x+75,550,20,'none',PALE,2,extra='opacity=".7"')
        add(f'<use href="#bowlIcon" transform="translate({x+75} 548) scale(.43)" color="{PALE}"/>')

# The striped cloth roof, curved scallops and narrow hand-painted trim.
roof='M279 355Q721 335 1161 355L1281 472H159Z'
path(roof,CORAL,INK,7)
add(f'<clipPath id="roofClip"><path d="{roof}"/></clipPath><g clip-path="url(#roofClip)">')
for i in range(11):
    if i%2==0:
        a=279+i*882/11;b=279+(i+1)*882/11
        c=159+(i+1)*1122/11;d=159+i*1122/11
        path(f'M{a:.2f} 345L{b:.2f} 345L{c:.2f} 476H{d:.2f}Z',GOLD,'none',0)
path('M161 457h1120v18H161Z','#924c43','none',0,extra='opacity=".22"')
add('</g>')
path(roof,'none',INK,7)
path('M285 355Q721 338 1156 355',stroke='#f9d69a',sw=4)
for i in range(11):
    x=159+i*102
    path(f'M{x} 470h102v34q-51 47-102 0Z',GOLD if i%2==0 else CORAL,INK,4)
    path(f'M{x+13} 507q38 24 76 0',stroke='#f9d29b' if i%2==0 else '#ffae88',sw=3)
path('M159 472h1122',stroke=INK,sw=6)
# Small round house seal, centred on the roof above the chef's hat.
add('<g transform="translate(0 -30)">')
circle(720,456,52,INK,INK,4)
circle(720,451,49,PALE,INK,4)
circle(720,451,41,'none','#c58a4b',2)
add(f'<use href="#octoSeal" transform="translate(720 442) scale(.78)" color="{INK}"/>')
for x in [679,761]:circle(x,451,2.2,INK)
add('</g>')

# Booth front and its joinery, before the chef and countertop props.
rect(266,1052,906,284,'#b5794a',INK,7,3)
rect(286,1085,866,228,TEAL,INK,4,3)
for x in [300,399,1042,1140]: path(f'M{x} 1095v205',stroke='#71978a',sw=2,extra='opacity=".5"')
rect(310,1110,818,177,PALE,INK,4,10)
rect(322,1122,794,153,'none','#b7864b',1.6,5)
# Inset corner brackets.
for x,sign in [(331,1),(1107,-1)]:
    for y,sgn in [(1131,1),(1266,-1)]:
        path(f'M{x} {y+17*sgn}v{-17*sgn}h{17*sign}',stroke='#b7864b',sw=2)
text(720,1152,'THE NIGHT MARKET KITCHEN',16,INK,'sans-serif','bold',3.6)
text(720,1222,'NOODLES &amp; BROTH',56,INK,'Georgia, serif','bold',.4)
text(720,1255,'HOUSE SPECIAL  /  EVERY NIGHT',15,INK,'sans-serif','normal',3)
# Small side emblems occupy the sign's ends.
for x in [372,1068]:
    circle(x,1199,30,'none','#b7864b',2)
    if x==372: add(f'<use href="#bowlIcon" transform="translate({x} 1195) scale(.62)" color="{INK}"/>')
    else:
        text(x,1209,'08',27,INK,'Georgia, serif','bold',0)
path('M289 1316h861',stroke=GOLD,sw=3)
path('M306 1336v8m823-8v8',stroke=INK,sw=5)
# Broad counter with an angled top and thick wooden nose.
path('M250 987H1181L1222 1041H208Z',GOLD,INK,6)
path('M266 995h896l23 31H235Z','#f0cf8c','none',0)
path('M208 1041h1014v38H208Z','#bd8252',INK,6)
path('M216 1050h998',stroke='#f8d18b',sw=4)
path('M227 1068h248m38 0h92m358 0h233',stroke='#8f5c40',sw=2)
# Discreet countertop seams.
for x in [324,489,654,984,1149]:path(f'M{x} 994l-7 38',stroke='#bb8f53',sw=2)

# An eight-arm octopus. Each limb is a custom tapered ribbon, not a uniform stroke.
def bezier(p0,p1,p2,p3,t):
    u=1-t
    return (u*u*u*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*p3[0], u*u*u*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*p3[1])
def points_for(start,segments):
    pts=[start];p=start
    for a,b,c in segments:
        pts.extend(bezier(p,a,b,c,i/32) for i in range(1,33));p=c
    return pts

def arm(name,start,segs,side=1,base=75,tip=15,cups=15):
    pts=points_for(start,segs)
    lengths=[0]
    for a,b in zip(pts,pts[1:]):lengths.append(lengths[-1]+hypot(b[0]-a[0],b[1]-a[1]))
    normals=[];widths=[]
    for i,p in enumerate(pts):
        a=pts[max(0,i-1)];b=pts[min(len(pts)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];ln=hypot(dx,dy)
        normals.append((-dy/ln,dx/ln));t=lengths[i]/lengths[-1]
        widths.append(tip+(base-tip)*(1-t)**.72)
    def offset(i,k):
        p=pts[i];n=normals[i];return(p[0]+n[0]*widths[i]*k,p[1]+n[1]*widths[i]*k)
    def poly(ps):return 'M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in ps)+'Z'
    shape=poly([offset(i,.5) for i in range(len(pts))]+[offset(i,-.5) for i in reversed(range(len(pts)))])
    path(shape,CORAL,'none',0)
    # A narrow coral-shadow underside, with a row of pale suction cups.
    band=poly([offset(i,.49*side) for i in range(len(pts))]+[offset(i,.07*side) for i in reversed(range(len(pts)))])
    path(band,'#cb5e59','none',0)
    for j in range(cups):
        target=lengths[-1]*(.18+.76*j/max(cups-1,1))
        i=min(range(len(pts)),key=lambda i:abs(lengths[i]-target))
        x,y=offset(i,.275*side)
        rx=max(3.3,widths[i]*.155);ry=rx*.73
        angle=degrees(atan2(normals[i][1],normals[i][0]))+90
        ellipse(round(x,2),round(y,2),round(rx,2),round(ry,2),'#ffd3ac','#a84e50',1.7,extra=f'transform="rotate({angle:.2f} {x:.2f} {y:.2f})"')
        ellipse(round(x,2),round(y,2),round(rx*.38,2),round(ry*.36,2),'#d97a69','none',0,extra=f'transform="rotate({angle:.2f} {x:.2f} {y:.2f})"')
    path(shape,'none',INK,5)
    # Short, irregular reflected highlights down the upper edge.
    run=[]
    for i in range(int(len(pts)*.22),int(len(pts)*.57)):
        x,y=offset(i,-.31*side);run.append((x,y))
    d='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in run)
    path(d,'none','#ffb18c',4)

# Long handles sit behind the gripping ends.
path('M463 720L402 895',stroke=INK,sw=16)
path('M463 720L402 895',stroke='#ce9c59',sw=9)
path('M463 720l-14 41',stroke='#f3d195',sw=3)
# Salt/spice jar, tipped toward the noodles.
add('<g transform="rotate(24 970 696)">')
rect(946,626,49,106,'#e5b35e',INK,4,9)
rect(947,618,47,17,'#cfdbba',INK,4,4)
path('M956 618v-4m14 4v-4m14 4v-4',stroke=INK,sw=3)
rect(951,650,39,28,PALE,INK,2,3)
path('M964 657q-8 8 0 13q10 0 10-9q-2-8-10-4Z',RED,'none',0)
path('M971 657q4-8 10-6',stroke=TEAL,sw=2)
path('M953 638v7',stroke='#ffe5aa',sw=3)
add('</g>')
# The six outside arms establish a readable radial silhouette.
arm('ladle',(637,833),[((559,850),(519,802),(515,759)),((511,714),(470,687),(449,711)),((432,735),(462,752),(479,728))],1,78,15,18)
arm('spice',(806,833),[((875,843),(904,783),(915,730)),((923,681),(969,675),(988,704)),((1005,730),(981,752),(962,732))],-1,76,15,17)
arm('side-bowl',(630,867),[((560,842),(516,853),(483,877)),((446,903),(407,874),(391,831))],1,73,20,14)
arm('chopsticks',(841,859),[((904,824),(950,832),(988,851)),((1034,875),(1083,847),(1082,809)),((1082,782),(1066,771),(1053,784))],1,74,15,17)
arm('scallions',(649,892),[((566,904),(537,968),(479,984)),((428,1001),(384,966),(357,976)),((331,984),(332,1013),(353,1016)),((368,1018),(377,1007),(369,998))],-1,75,14,21)
arm('tea',(838,891),[((918,885),(969,943),(1019,958)),((1067,975),(1115,953),(1118,922)),((1122,897),(1093,887),(1083,906))],1,74,16,18)
# Two close arms spill across the work surface.
arm('knife',(672,907),[((639,948),(669,996),(637,1031)),((606,1065),(545,1065),(526,1031)),((509,1002),(529,981),(552,997))],-1,77,18,16)
arm('egg',(801,908),[((824,956),(867,976),(909,1002)),((951,1035),(996,1019),(1007,986)),((1017,960),(995,945),(977,958))],1,75,17,16)

# The round mantle, with a soft coral lower edge.
head='M589 817C565 779 574 718 612 677C644 642 688 634 735 642C791 636 840 665 861 710C886 760 868 808 851 847C829 887 779 913 721 911C660 912 608 876 589 817Z'
path(head,'url(#head)',INK,6)
path('M594 799Q617 860 673 875Q748 905 824 860Q795 907 724 908Q634 906 597 836Z','#cc615b','none',0)
path('M602 726Q612 691 641 680M599 748l-2 11',stroke='#ffc19a',sw=7)
# A few organic speckles are part of the mantle, not extra eyes.
for x,y,r in [(824,719,4),(835,731,3),(817,735,2.5),(610,786,3),(616,799,2.3),(830,801,3.5),(820,811,2)]:
    circle(x,y,r,'#be5654','none',0,extra='opacity=".55"')
# The cap casts a small, clean graphic shadow.
path('M616 666Q732 642 835 668L832 685Q726 663 615 681Z','#c45c53','none',0,extra='opacity=".5"')
# Face: delighted, alert, and a little mischievous.
path('M646 724q16-13 31-1M763 720q15-11 28 1',stroke=INK,sw=5)
ellipse(665,754,9,14,INK,'none',0)
ellipse(778,751,9,14,INK,'none',0)
circle(667,749,2.5,WHITE);circle(780,746,2.5,WHITE)
ellipse(636,781,24,13,'#e46864','none',0)
ellipse(803,778,23,13,'#e46864','none',0)
for x,y in [(627,780),(637,783),(647,779),(794,778),(804,781),(814,776)]:
    path(f'M{x} {y-3}l-1 6',stroke='#c75556',sw=2)
path('M701 785Q726 802 752 783Q752 817 730 820Q709 818 701 785Z',INK,INK,3)
path('M715 811Q732 799 745 809Q731 825 715 811Z','#f3aa8f','none',0)
path('M696 783l7 2m48-3 7-3',stroke=INK,sw=3)
# Neck cloth and small apron with the restaurant's badge.
path('M643 836Q716 865 805 833L807 855Q718 879 642 853Z',TEAL,INK,4)
path('M786 851l32 6-6 36-27-28-16-8Z',TEAL,INK,4)
path('M799 861l8 16',stroke='#86a392',sw=2)
path('M653 852Q724 880 796 851L815 918Q738 951 642 916Z',WHITE,INK,5)
path('M658 859l-4 46m134-44 13 46',stroke='#d2bd95',sw=3)
path('M664 915Q731 937 794 917',stroke='#9fbaa2',sw=3)
circle(728,901,24,TEAL,INK,2)
add(f'<use href="#bowlIcon" transform="translate(728 898) scale(.51)" color="{WHITE}"/>')
# Chef's hat: three asymmetric puffs, a folded brim, and ink creases.
cap='M614 622C577 623 567 595 578 570C584 553 601 543 623 545C624 516 649 501 678 509C697 479 744 479 766 507C802 489 839 508 842 538C875 540 887 567 874 590C867 606 853 614 833 613L833 651Q719 673 615 650Z'
path(cap,WHITE,INK,6)
path('M581 591Q596 613 626 603L638 630Q733 646 833 625L833 651Q719 673 615 650L614 622Q584 622 581 591Z','#ddcba8','none',0)
path('M615 623Q714 646 837 620L833 651Q720 673 615 650Z',PALE,INK,4)
path('M631 635Q725 655 817 636',stroke='#b89f79',sw=2)
path('M624 546q-3 18 11 31m43-67q-11 18-8 39m96-41q14 15 9 35m67-3q-19 0-23 19',stroke='#cfbc98',sw=4)
path('M694 519q12-14 29-12',stroke='#fffaf0',sw=5)
# Three little embroidered stitches on the band.
for x in [706,720,734]:path(f'M{x} 639l5 6m-5 0 5-6',stroke=TEAL,sw=2)

# Useful mise en place on the left. Stove and stockpot.
rect(299,973,199,35,INK,INK,4,7)
rect(311,979,176,17,'#687f73',INK,3,3)
for x in [331,362,393,424,455]:path(f'M{x} 981l-3 11',stroke=INK,sw=3)
path('M311 924q-43-15-30 26q6 13 31 8M477 924q42-15 29 26q-6 13-30 8','none',INK,12)
path('M311 924q-43-15-30 26q6 13 31 8M477 924q42-15 29 26q-6 13-30 8','none','#a4b2a0',5)
path('M310 895H480V966Q397 1007 310 966Z','url(#pot)',INK,5)
path('M324 907v52q11 10 22 11v-63Z','#b5c2a9','none',0,extra='opacity=".5"')
path('M467 907v51',stroke='#244b4b',sw=4)
ellipse(395,895,85,23,'#c8cfb3',INK,5)
ellipse(395,896,73,15,'#785337',INK,3)
path('M329 897q35-16 100-5',stroke='#d9aa5f',sw=3)
# Ladle is visible again above the soup's surface.
path('M463 720L408 882',stroke=INK,sw=12)
path('M463 720L408 882',stroke='#d7ad70',sw=6)
path('M385 876q19-11 42 3l-2 13q-20 18-38-1Z','#8ca89a',INK,3)
ellipse(405,879,20,7,'#d1d3ac',INK,2)
# The end of the first arm folds over the wooden handle.
path('M449 735q17 15 30-7',stroke=INK,sw=20)
path('M449 735q17 15 30-7',stroke=CORAL,sw=13)
ellipse(468,738,4.6,3.3,'#ffd3ac','#a84e50',1.5,extra='transform="rotate(-20 468 738)"')
# Steaming stock, cream strokes on the midnight blue wall.
for d in ['M349 864C322 842 371 824 351 795C340 781 344 768 351 756','M390 862C417 840 371 819 396 790','M428 866C453 848 424 835 435 819']:
    path(d,stroke='#e5d9ad',sw=4,extra='opacity=".6"')
path('M366 840q-12-13 1-25',stroke='#fff1c8',sw=2,extra='opacity=".35"')

# Side bowl, balanced on an arm.
path('M313 808Q324 866 390 867Q456 866 468 808Z',WHITE,INK,5)
path('M321 830Q389 851 460 830',stroke=TEAL,sw=8)
path('M331 847Q389 876 447 847',stroke='#d6ba8e',sw=3)
ellipse(390,808,78,22,WHITE,INK,4)
ellipse(390,807,68,14,'#b27b3e',INK,2)
for x,y in [(350,806),(366,802),(386,809),(408,805)]:
    path(f'M{x-11} {y}q7-11 20-3q10 9 19 1',stroke='#f8d37c',sw=3)
use('scallion',427,808,.7,20);use('scallion',408,799,.55,-25)
path('M445 794l-9-26-23 9 8 23Z','#2c5148',INK,3)
path('M365 779q-17-15-1-30m30 29q17-17 2-30',stroke=PALE,sw=3,extra='opacity=".7"')
# A tea cup on the other side, with a real handle and saucer.
ellipse(1120,926,47,11,'#d8c9a5',INK,3)
ellipse(1120,923,34,5,'none','#9ba78d',2)
path('M1142 876q29-8 27 12q-2 20-26 15',stroke=INK,sw=12)
path('M1142 876q29-8 27 12q-2 20-26 15',stroke=PALE,sw=6)
path('M1090 871h59l-6 43q-22 15-46 0Z',PALE,INK,4)
path('M1098 888h43v17q-21 8-41 0Z',TEAL,'none',0)
ellipse(1119,871,29,9,WHITE,INK,3)
ellipse(1119,872,22,5,'#805431','none',0)
path('M1110 851q-14-15 0-27m16 27q14-14 1-23',stroke=PALE,sw=3,extra='opacity=".55"')
# Garnish board and a short chef's knife, held by the front-left curl.
path('M474 1009l107-9 53 17-121 15Z','#a86e42',INK,3)
path('M484 1007l98-8 48 13-116 14Z','#dcaf6c',INK,3)
path('M497 1010l49 8m-22-15 43 12',stroke='#b48149',sw=1.7)
# Scallion bunch gathered by the far-left tip.
for d in ['M369 1001Q379 967 390 951','M375 1001Q385 971 412 953','M379 1003Q397 978 420 975','M367 1000Q363 974 371 953']:
    path(d,stroke=INK,sw=10)
    path(d,stroke='#74956b',sw=5)
path('M367 1001l11 5',stroke=PALE,sw=8)
for x,y,s,r in [(573,1010,.7,20),(589,1011,.65,-10),(605,1016,.6,20),(558,1015,.65,40),(581,1019,.6,-25),(601,1004,.55,5)]:use('scallion',x,y,s,r)
# Broad, glinting knife blade and dark wooden handle.
path('M545 986l-54-20-9 20 53 15Z','#a5b9ae',INK,3)
path('M485 984l51 13',stroke=WHITE,sw=3)
path('M544 986l27 11-6 14-29-12Z','#71503c',INK,3)
circle(551,996,2,GOLD);circle(562,1001,2,GOLD)
path('M540 994q8-4 15 5',stroke=INK,sw=16)
path('M540 994q8-4 15 5',stroke=CORAL,sw=10)

# A halved marinated egg, offered toward the hero bowl.
add('<g transform="rotate(-28 972 941)">')
ellipse(972,941,25,33,WHITE,INK,4)
path('M955 943q-3 27 20 28q15-9 17-26q-6 21-18 20q-17-1-19-22Z','#d8c5a0','none',0)
ellipse(973,940,15,18,'#eeaf49','#c6803e',2)
path('M967 930q9-7 15 3',stroke='#ffd776',sw=4)
add('</g>')
path('M974 959q12 9 22-3',stroke=INK,sw=17)
path('M974 959q12 9 22-3',stroke=CORAL,sw=11)

# Chopsticks and the long, individually drawn strands lifted from the broth.
for a,b,c,d in [(1076,768,878,874),(1084,782,889,884)]:
    path(f'M{a} {b}L{c} {d}',stroke=INK,sw=10)
    path(f'M{a} {b}L{c} {d}',stroke='#e7b65d',sw=5)
    path(f'M{a-2} {b+1}l-39 21',stroke='#8f4c35',sw=5)
# Front edge of the sixth arm pinches the chopsticks.
path('M1065 783q-2-9-12 1',stroke=INK,sw=19)
path('M1065 783q-2-9-12 1',stroke=CORAL,sw=12)
# Noodle stream: alternating ochre contours and warm gold centres.
noodles=[
 'M888 868C870 878 892 899 876 920C862 940 879 962 857 989',
 'M895 866C881 889 902 907 887 931C872 950 887 969 868 991',
 'M903 861C893 879 912 907 896 929C886 949 902 975 879 993',
 'M910 858C901 881 925 902 907 929C897 947 913 970 890 991',
 'M916 855C914 878 935 907 918 932C907 953 924 974 901 993',
 'M884 875C863 888 875 903 866 917C853 941 861 960 845 986'
]
for d in noodles:path(d,stroke='#8c5734',sw=8)
for d in noodles:path(d,stroke='#f6ce77',sw=4.5)
path('M884 869q13-16 30-13',stroke='#ffe8a2',sw=3)
# A few flying seasoning flakes stay deliberately sparse.
for x,y,r in [(942,751,2),(939,772,2.5),(919,792,2),(937,811,1.7),(920,838,2.1),(947,790,1.7),(928,760,1.7)]:
    circle(x,y,r,GOLD)

# Main ramen bowl. Its rim, toppings and wave motif are all vector artwork.
ellipse(787,1103,111,13,'#81583e','none',0,extra='opacity=".4"')
path('M647 1002C658 1079 704 1114 786 1116C868 1114 914 1079 926 1002Z',WHITE,INK,6)
path('M667 1053Q785 1109 905 1053Q876 1112 787 1116Q706 1115 667 1053Z','#d5c5a3','none',0)
# A sweeping indigo decoration rather than a flat stripe.
path('M656 1035Q788 1083 917 1035L911 1050Q787 1104 663 1050Z',TEAL,'none',0)
path('M676 1061Q735 1086 787 1085Q843 1087 898 1061',stroke=INK,sw=2)
path('M727 1105q58 15 117 0l-7 14q-50 13-102 0Z',TEAL,INK,3)
# Three cream wave crests on the blue bowl band.
for x,y in [(732,1065),(786,1072),(840,1064)]:
    path(f'M{x-18} {y}q13-17 27-1q-12-6-14 4q-1 6 10 6',stroke=WHITE,sw=2.5)
ellipse(786,1002,139,38,WHITE,INK,5)
ellipse(786,1003,126,29,'#b17a3c',INK,2.5)
ellipse(786,1004,115,23,'#d99945','none',0)
# Tiny broth oil droplets.
for x,y,r in [(677,1003,3),(693,1015,2.4),(754,1024,3),(881,1012,3),(897,1002,2),(811,1024,2),(846,1019,2.5),(707,1008,2),(867,993,3)]:
    circle(x,y,r,'#f3c36a','#9f6a37',.8)
# Nori, with inked crosshatching.
path('M841 976l-2-47 42-11 16 58Z','#294e48',INK,4)
path('M849 937l7 32m5-35 8 33m4-38 10 33M846 945l34-10m-32 23 36-11',stroke='#68806a',sw=2)
# Nest of fine noodles on the near-left side.
for d in ['M676 1002q23-25 59-5q29 19 53-2','M679 1008q26-19 54-1q20 13 45 0','M688 990q25-13 49 1q21 17 39 8','M700 1017q29-12 44 1q14 7 30-2','M786 1016q26-18 45-5q16 10 28-3','M799 1008q14-14 34-3q15 7 22-2']:
    path(d,stroke='#f6ce77',sw=4)
# Chashu pork, hand-drawn concentric marbling.
add('<g transform="rotate(15 725 983)">')
ellipse(725,983,37,25,'#bc6b4e',INK,3)
ellipse(725,981,31,20,'#e7ac7d','#f7d1a0',3)
path('M705 980C706 964 743 967 745 981C749 996 714 1000 713 985C712 977 734 975 735 983C736 990 724 991 722 985',stroke='#a95645',sw=4)
path('M698 985q5 10 15 11m22-28 9 7',stroke='#f8d6a7',sw=3)
add('</g>')
# Egg half nestled into the bowl.
add('<g transform="rotate(27 817 977)">')
ellipse(817,977,27,35,WHITE,INK,3.5)
ellipse(818,978,17,20,'#eda63d','#c88336',2)
path('M807 972q8-12 17-3',stroke='#ffd676',sw=4)
add('</g>')
# A scalloped narutomaki slice and its coral spiral.
add('<g transform="translate(777 1004) rotate(-12)">')
path('M-24 0q-7-9 2-13q1-10 11-8q6-8 14-2q10-5 15 4q12 0 11 10q8 8-1 14q-1 11-12 9q-7 8-15 2q-11 4-14-6q-12 0-11-10Z',WHITE,'#d9b68e',2)
path('M-15 1C-18-12 8-15 15-4C23 9-6 16-9 5C-12-3 5-5 6 1C7 5 0 7-2 3',stroke='#df7d80',sw=3.5)
add('</g>')
# Fresh greens on the soup, in an irregular cluster.
for x,y,s,r in [(856,990,.9,-18),(871,998,.8,25),(849,1003,.75,30),(839,993,.65,-30),(865,984,.68,15),(891,992,.55,-25),(837,1011,.6,-10)]:
    use('scallion',x,y,s,r)
for x,y in [(695,991),(741,1011),(804,1015),(879,1008),(844,981)]:use('seed',x,y,.8)
# Highlights on the porcelain lip and steam above the bowl.
path('M668 1020Q787 1062 905 1020',stroke='#fff8e1',sw=4)
for d in ['M743 949C713 930 753 909 737 886','M789 935C811 915 779 901 790 878','M830 937C847 923 831 910 840 897']:
    path(d,stroke='#fff0c4',sw=3.5,extra='opacity=".67"')

# A pair of paper lanterns hangs in front of the frame.
def lantern(cx,cy,red=False):
    path(f'M{cx} 511v{cy-85-511}',stroke=INK,sw=5)
    path(f'M{cx-5} 516v{cy-87-516}',stroke='#b8a47b',sw=1.5)
    rect(cx-23,cy-88,46,14,INK,INK,2,4)
    d=f'M{cx-26} {cy-76}C{cx-66} {cy-58} {cx-65} {cy+54} {cx-26} {cy+75}Q{cx} {cy+86} {cx+26} {cy+75}C{cx+65} {cy+54} {cx+66} {cy-58} {cx+26} {cy-76}Q{cx} {cy-85} {cx-26} {cy-76}Z'
    path(d,'url(#redLantern)' if red else 'url(#lantern)',INK,5)
    for dy,spread in [(-62,41),(-43,51),(-23,56),(0,57),(23,55),(44,48),(62,36)]:
        path(f'M{cx-spread} {cy+dy}Q{cx} {cy+dy+12} {cx+spread} {cy+dy}',stroke='#934c3e' if red else '#b57a3e',sw=2,extra='opacity=".5"')
    path(f'M{cx-15} {cy-74}Q{cx-39} {cy} {cx-15} {cy+74}M{cx+15} {cy-74}Q{cx+39} {cy} {cx+15} {cy+74}',stroke='#ffdfa5',sw=2,extra='opacity=".3"')
    rect(cx-22,cy+77,44,13,INK,INK,2,3)
    path(f'M{cx} {cy+90}v24m-6-9v13m12-13v13',stroke='#c69255',sw=3)
    if red:
        text(cx,cy+9,'08',48,WHITE,'Georgia, serif','bold',-2)
        path(f'M{cx-15} {cy+28}h30',stroke=WHITE,sw=2)
        circle(cx,cy-34,4,WHITE)
    else:
        add(f'<use href="#bowlIcon" transform="translate({cx} {cy+1}) scale(1.03)" color="{INK}"/>')
        path(f'M{cx-12} {cy+45}h24',stroke=INK,sw=2)
lantern(289,667)
lantern(1151,667,True)

# Small market-side details: a crate, a folded cloth, and a potted herb.
# These sit low so the working silhouette stays clean.
path('M1206 1240l100-13 34 24-100 15Z','#bd8c51',INK,4)
path('M1206 1240l28 26v87l-28-24Z','#916843',INK,4)
path('M1234 1266l100-15v87l-100 15Z','#c29457',INK,4)
for y in [1289,1317]:path(f'M1243 {y}l82-12',stroke='#76553d',sw=5)
path('M1216 1262l9 8m-9 23 9 8m-9 22 9 8',stroke='#76553d',sw=3)
for x,y in [(1244,1278),(1324,1265),(1244,1338),(1324,1327)]:circle(x,y,2.4,INK)
# Stack of ceramic bowls atop the crate.
for y in [1230,1218,1206]:
    path(f'M1221 {y}q8 33 47 33q38 0 46-33Z',PALE,INK,3)
    ellipse(1268,y,46,10,'#91a398',INK,3)
    path(f'M1230 {y+14}q38 13 76 0',stroke=TEAL,sw=3)
# Herb pot and leaves on the opposite side.
path('M116 1284h84l-11 62q-29 17-60 0Z','#c66f52',INK,4)
path('M132 1306l7 35m44-35-5 35',stroke='#edaa77',sw=3)
ellipse(158,1284,43,13,'#694c37',INK,4)
for d in ['M158 1284q-21-48-37-72','M157 1284q14-54 39-83','M157 1284q-5-67 4-98','M158 1284q30-27 48-32','M151 1283q-27-28-48-29']:
    path(d,stroke='#9bb388',sw=3)
for x,y,rot in [(121,1213,-45),(135,1237,-50),(157,1206,5),(166,1185,20),(182,1226,40),(197,1201,37),(197,1256,65),(116,1261,-65),(146,1257,-10),(173,1247,35)]:
    add(f'<g transform="translate({x} {y}) rotate({rot})">')
    path('M0 13Q-25-2 0-27Q23-2 0 13Z','#75956e',INK,2.5)
    path('M0 9v-26',stroke='#bac293',sw=1.5)
    add('</g>')
# A hanging tea towel catches the light on the left post.
path('M238 1091l50 4-8 109q-23 11-49-4Z',PALE,INK,4)
path('M241 1098l-5 94m17-93-7 97m21-94-5 95m16-92-6 88',stroke='#b8bb9b',sw=2)
path('M234 1177l48 3m-49 9 48 3',stroke=TEAL,sw=4)
# Tiny wisps and a spark to balance the largest open spaces.
use('spark',1260,920,.65)
use('spark',178,1091,.5)

# Restrained print texture: self-contained, resolution-independent.
rect(42,42,1356,1476,'url(#paper)','none',0,16,extra='pointer-events="none"')
add('</g>')

# Poster typography is kept outside the illustration, with generous breathing room.
text(720,113,'A LITTLE BOOTH. A LOT OF SOUL.',19,PALE,'sans-serif','normal',5.2)
text(720,231,'OCTO RAMEN',126,PALE,'Georgia, serif','bold',2,extra='textLength="1050" lengthAdjust="spacingAndGlyphs"')
text(720,281,'FRESH NOODLES  /  DEEP BROTH  /  LATE NIGHTS',17,'#c6cfb4','sans-serif','normal',3.1)
use('spark',129,190,.8);use('spark',1311,190,.8)
path('M104 135v-42h44m1188 42v-42h-44',stroke='#d7bb81',sw=2)
# The bottom line reads like the signature on a printed restaurant poster.
path('M150 1433h201m738 0h201',stroke='#9aaa8e',sw=1.5)
text(720,1440,'EIGHT ARMS. ONE PERFECT BOWL.',23,PALE,'sans-serif','bold',3)
text(720,1480,'—  THE MIDNIGHT SPECIAL  ·  NO. 08  —',13,'#bac9ad','sans-serif','normal',3.4)
# Last few paper-fibre marks on the outer cream margin.
for x,y in [(17,283),(1426,1100),(314,1540),(876,18),(14,1374),(1195,1539)]:
    path(f'M{x} {y}h3',stroke='#cfb998',sw=1)
add('</svg>')

svg='\n'.join(parts)
(OUT/'octo-ramen.svg').write_text(svg,encoding='utf-8')
print(f'Wrote {OUT / "octo-ramen.svg"} ({len(svg.encode()):,} bytes)')
