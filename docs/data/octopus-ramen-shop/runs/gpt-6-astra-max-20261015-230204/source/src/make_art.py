#!/usr/bin/env python3
"""Eight Arms — an original, entirely vector night-market illustration.
Run from the project root with `python3 src/make_art.py` (macOS CoreText is used
only at build time to outline the type). The delivered SVG is self-contained.
"""
from pathlib import Path
import math
import random
import json
import subprocess
from html import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
W, H = 1400, 1600
INK = '#18383D'
CREAM = '#F9EBCB'
GOLD = '#EFB65F'
CORAL = '#E9806C'
TEAL = '#2B6867'
parts = []
texts = []

def emit(s): parts.append(s)
def attrs(d):
    return ' '.join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k,v in d.items() if v is not None)
def path(d, fill='none', stroke=INK, sw=4, **kw):
    emit(f'<path d="{d}" {attrs(dict(fill=fill, stroke=stroke, stroke_width=sw, stroke_linecap="round", stroke_linejoin="round", **kw))}/>')
def rect(x,y,w,h,fill,stroke=INK,sw=4,r=0,**kw):
    emit(f'<rect {attrs(dict(x=x,y=y,width=w,height=h,rx=r,fill=fill,stroke=stroke,stroke_width=sw,**kw))}/>')
def ellipse(x,y,rx,ry,fill,stroke=INK,sw=3,**kw):
    emit(f'<ellipse {attrs(dict(cx=x,cy=y,rx=rx,ry=ry,fill=fill,stroke=stroke,stroke_width=sw,**kw))}/>')
def circle(x,y,r,fill,stroke='none',sw=0,**kw):
    ellipse(x,y,r,r,fill,stroke,sw,**kw)
def line(x1,y1,x2,y2,stroke=INK,sw=3,**kw):
    path(f'M{x1},{y1} L{x2},{y2}',stroke=stroke,sw=sw,**kw)
def group(**kw): emit('<g '+attrs(kw)+'>')
def end(): emit('</g>')
def text(s,x,y,size=20,fill=INK,font='AvenirNext-DemiBold',spacing=0,anchor='middle',maxwidth=None):
    index = len(texts)
    texts.append(dict(text=s,x=x,y=y,size=size,fill=fill,font=font,spacing=spacing,anchor=anchor,maxwidth=maxwidth))
    emit(f'__LETTERING_{index}__')
def star(x,y,r=7,fill=GOLD):
    path(f'M{x},{y-r} Q{x+1},{y-1} {x+r},{y} Q{x+1},{y+1} {x},{y+r} Q{x-1},{y+1} {x-r},{y} Q{x-1},{y-1} {x},{y-r}Z',fill,'none',0)
def steam(d,width=6,opacity=.75):
    path(d,stroke=CREAM,sw=width,opacity=opacity)
def bowl_icon(cx,cy,s=1,color=CREAM):
    group(transform=f'translate({cx},{cy}) scale({s})')
    path('M-35,-7 Q-31,20 0,22 Q31,20 35,-7 Z','none',color,3)
    ellipse(0,-7,35,9,'none',color,3)
    line(-12,26,12,26,color,3)
    for x in [-13,1,15]:
        path(f'M{x},-21 C{x-10},-29 {x+10},-34 {x},-44',stroke=color,sw=3)
    end()
def octo_icon(cx,cy,s=1,color=INK):
    group(transform=f'translate({cx},{cy}) scale({s})')
    path('M-18,3 C-28,-33 28,-33 18,3 M-18,3 C-34,23 -42,3 -29,1 M-12,6 C-21,34 -33,24 -27,16 M-5,8 C-7,34 -20,35 -18,24 M5,8 C7,34 20,35 18,24 M12,6 C21,34 33,24 27,16 M18,3 C34,23 42,3 29,1',stroke=color,sw=5)
    circle(-7,-7,2.8,color)
    circle(7,-7,2.8,color)
    end()
def wave_band(x,y,width,scale=1,color=CREAM,opacity=1):
    group(transform=f'translate({x},{y}) scale({scale})',opacity=opacity)
    count = int(width/(48*scale))+1
    for i in range(count):
        xx=i*48
        for r in (13,21,29):
            path(f'M{xx-r},18 A{r},{r} 0 0 1 {xx+r},18',stroke=color,sw=2.3)
    end()

emit('''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1400" height="1600" viewBox="0 0 1400 1600" role="img" aria-labelledby="title desc">
<title id="title">Eight Arms — Midnight Ramen</title>
<desc id="desc">A cheerful coral octopus in a chef's toque works all eight arms at a golden wooden ramen booth. Chopsticks lift long noodles, a ladle pours broth, and steaming bowls glow under paper lanterns in a teal night market.</desc>
<defs>
  <linearGradient id="night" x2="0" y2="1"><stop stop-color="#13323D"/><stop offset=".62" stop-color="#245452"/><stop offset="1" stop-color="#356661"/></linearGradient>
  <radialGradient id="warmth"><stop stop-color="#E8AD60" stop-opacity=".25"/><stop offset="1" stop-color="#E8AD60" stop-opacity="0"/></radialGradient>
  <radialGradient id="lanternGlow"><stop stop-color="#FFD684" stop-opacity=".28"/><stop offset=".5" stop-color="#FFC477" stop-opacity=".12"/><stop offset="1" stop-color="#FFC477" stop-opacity="0"/></radialGradient>
  <linearGradient id="roof" x2="0" y2="1"><stop stop-color="#F3C878"/><stop offset="1" stop-color="#D89C50"/></linearGradient>
  <linearGradient id="wood" x2="1" y2="0"><stop stop-color="#C78146"/><stop offset=".36" stop-color="#DDA057"/><stop offset=".7" stop-color="#E7B46A"/><stop offset="1" stop-color="#C98949"/></linearGradient>
  <linearGradient id="head" x1="0" y1="0" x2=".45" y2="1"><stop stop-color="#F5AB85"/><stop offset=".5" stop-color="#ED8C75"/><stop offset="1" stop-color="#D66B64"/></linearGradient>
  <linearGradient id="arm" x1="0" y1="0" x2=".2" y2="1"><stop stop-color="#F09A7A"/><stop offset=".55" stop-color="#E5806D"/><stop offset="1" stop-color="#D66B63"/></linearGradient>
  <linearGradient id="redLantern" x2="1" y2="0"><stop stop-color="#CB624F"/><stop offset=".45" stop-color="#F7AB6A"/><stop offset=".7" stop-color="#F1A16A"/><stop offset="1" stop-color="#D57253"/></linearGradient>
  <linearGradient id="goldLantern" x2="1" y2="0"><stop stop-color="#D89F55"/><stop offset=".5" stop-color="#FFE4A0"/><stop offset="1" stop-color="#E4B265"/></linearGradient>
  <linearGradient id="pot" x2="1" y2="0"><stop stop-color="#347374"/><stop offset=".4" stop-color="#78A9A0"/><stop offset=".7" stop-color="#689A92"/><stop offset="1" stop-color="#326768"/></linearGradient>
  <linearGradient id="ceramic" x2="0" y2="1"><stop stop-color="#FFF2D5"/><stop offset="1" stop-color="#DBC5A0"/></linearGradient>
  <pattern id="paper" width="31" height="29" patternUnits="userSpaceOnUse"><circle cx="4" cy="8" r=".7" fill="#FFF5D8" opacity=".16"/><circle cx="19" cy="23" r=".6" fill="#102B32" opacity=".13"/><path d="M25 4h2 M9 20h1" stroke="#FFF7DC" stroke-width=".6" opacity=".12"/></pattern>
  <pattern id="wall" width="86" height="200" patternUnits="userSpaceOnUse"><path d="M0 0V200 M8 0V200" fill="none" stroke="#E2B16A" stroke-opacity=".06" stroke-width="2"/></pattern>
  <clipPath id="scene"><rect x="40" y="40" width="1320" height="1520" rx="32"/></clipPath>
  <clipPath id="frontPanel"><rect x="235" y="1113" width="930" height="250" rx="5"/></clipPath>
</defs>''')
# A softly weathered print border.
rect(0,0,W,H,CREAM,'none',0)
rect(23,23,1354,1554,'none',INK,2,43)
rect(40,40,1320,1520,'url(#night)','none',0,32)
group(clip_path='url(#scene)')
# Quiet, distant buildings and a late-night sky.
for d,c in [
 ('M40,514 L90,480 90,373 190,373 190,410 276,410 276,325 347,325 347,1000 40,1000Z','#1A4148'),
 ('M1013,970V365H1094V427H1196V345H1287V440H1360V1000Z','#1B4247'),
 ('M40,904V664H158V607H232V1010Z','#214C50'),
 ('M1192,1010V607H1311V559H1360V1010Z','#224D4F')]: path(d,c,'none',0)
for x,y in [(116,438),(161,438),(116,500),(300,374),(315,430),(1216,390),(1250,390),(1220,457),(1293,690),(90,723),(125,723)]:
    rect(x,y,13,26,'#D5A760','none',0,2,opacity=.20)
for x in [112,170,1207,1255,1310]:
    line(x,560,x,1006,'#47716B',1,opacity=.23)
# Roof outlines, distant street banners, and tiny warm windows.
path('M55,661 L159,637 218,665 M1192,593 L1283,564 1375,590',stroke='#49706A',sw=3,opacity=.5)
path('M55,344 Q163,394 289,352 M1125,340 Q1260,393 1362,350',stroke='#577D72',sw=2)
for x,y in [(83,359),(136,375),(191,377),(246,367),(1161,355),(1210,369),(1260,373),(1310,368)]:
    line(x,y-5,x,y+10,'#577D72',2)
    ellipse(x,y+15,6,8,'#E6B96F','none',0,opacity=.65)
# Crescent moon, restrained stars, graphic drifting clouds.
circle(1177,170,38,'#F3D598')
circle(1192,155,35,'#15363F')
for x,y,r in [(132,176,8),(224,265,6),(310,119,5),(1090,112,6),(1262,272,7),(975,111,4),(89,282,4),(1290,110,4),(198,120,3)]: star(x,y,r,'#D8BB7B')
for x,y,r in [(181,213,2),(268,164,2),(1084,259,2),(1296,214,2),(99,129,2),(1044,152,2),(337,264,2),(1207,289,2),(302,217,1.8)]:circle(x,y,r,'#D5BC84')
path('M105,278 H153 Q146,261 162,254 Q176,245 190,258 Q201,238 219,247 Q231,252 230,268 H267',stroke='#53726B',sw=3,opacity=.55)
path('M1048,285 H1090 Q1084,270 1097,264 Q1113,256 1121,271 H1145',stroke='#53726B',sw=3,opacity=.45)
# Ground and its quiet pools of reflected light.
path('M40,1274 Q700,1180 1360,1280V1560H40Z','#2B5A55','none',0)
ellipse(702,1397,554,93,'#183D3F','none',0,opacity=.65)
ellipse(711,1434,432,43,'#193F40','none',0,opacity=.5)
for x,y,rx,ry,c in [(196,1457,62,6,'#598176'),(1211,1422,73,5,'#678779'),(692,1469,165,4,'#577D6B'),(1131,1494,103,4,'#406D62'),(222,1330,97,4,'#8B9774'),(1275,1311,57,3,'#6A8D77'),(102,1384,34,3,'#557D70'),(515,1497,57,3,'#416D61')]:ellipse(x,y,rx,ry,c,'none',0,opacity=.6)
# The booth's inner darkness and timber skeleton.
rect(226,485,948,867,'#123A3F',INK,7,8)
rect(260,524,879,530,'#214B4C','none',0)
rect(260,524,879,530,'url(#wall)','none',0)
ellipse(701,750,462,370,'url(#warmth)','none',0)
rect(271,991,861,84,'#153C3E','none',0)
# Interior shelves, stacks of bowls and ingredient jars.
rect(294,841,236,19,'#AE7748',INK,4,3)
rect(891,839,223,19,'#AE7748',INK,4,3)
line(304,846,519,846,'#E6B26E',3)
for yy in [825,809,793]:
    path(f'M325,{yy} Q335,{yy+25} 381,{yy+25} Q427,{yy+25} 437,{yy}Z','#E6D5AD',INK,3)
    ellipse(381,yy,56,11,'#3D7471',INK,3)
    path(f'M342,{yy+12} Q381,{yy+24} 421,{yy+12}',stroke='#4D8076',sw=3)
for x,h,c in [(915,66,'#8DA68B'),(973,91,'#C98C53'),(1033,60,'#E2C188')]:
    rect(x,838-h,43,h,c,INK,3,7)
    rect(x+2,832-h,39,13,'#B97742',INK,3,3)
    rect(x+8,856-h,27,27,'#E7D5AE','none',0,2)
    for j in range(3): line(x+14,865-h+j*5,x+29,865-h+j*5,'#526A58',1.8)
# A tiny handwritten specials card.
group(transform='rotate(4 1013 679)')
rect(955,606,126,152,'#132F34','none',0,5,opacity=.32,transform='translate(5 6)')
rect(950,601,126,152,'#E9D6AF',INK,4,3)
line(959,610,1067,610,'#B48D5D',1)
line(961,640,1065,640,'#C29B6A',2)
text('TONIGHT',1013,630,14,INK,spacing=1.7)
text('SHOYU',964,668,16,INK,anchor='start')
text('MISO',964,697,16,INK,anchor='start')
text('EXTRA LOVE',1013,732,10,'#AF604B',spacing=1)
for y in [663,692]:
    line(1044,y,1060,y,'#B47C50',2)
    circle(1063,y,2,'#B47C50')
end()
# Warm upright posts with their woodgrain and simple joinery.
for x in [231,1123]:
    rect(x,480,46,880,'url(#wood)',INK,6,4)
    line(x+10,518,x+10,1315,'#F3C580',3)
    path(f'M{x+30},589 C{x+15},666 {x+39},705 {x+28},807 S{x+17},1019 {x+31},1131 S{x+24},1247 {x+30},1335',stroke='#9C6B42',sw=2,opacity=.62)
    ellipse(x+27,1171,8,20,'none','#A67544',2)
    ellipse(x+27,1171,3,9,'none','#A67544',1.5)
    for yy in [533,1000,1329]:circle(x+24,yy,4,INK)
    rect(x-6,1318,58,48,'#214749',INK,4,3)
# Cross brace under the roof.
rect(219,477,963,61,'#B17A46',INK,6,6)
line(241,517,1157,517,'#EAB36C',3)
for x in [296,1086]:
    path(f'M{x},535 L{x+34},535 L{x+34 if x<500 else x-22},600Z','#CB9456',INK,4)
# Indigo split noren. Gently irregular hems keep the stall handmade.
for i in range(5):
    x=302+i*158
    path(f'M{x},513 H{x+151} L{x+148},603 Q{x+76},621 {x+3},602Z','#245859',INK,4)
    path(f'M{x+8},526 L{x+7},592 M{x+140},525 L{x+137},593',stroke='#5F8B7B',sw=2,opacity=.65)
    line(x+11,596,x+136,596,'#D3C192',2,opacity=.6)
    if i in [0,4]:
        circle(x+75,561,25,'none','#E4D9B5',2.7)
        wave_band(x+51,554,48,.5,'#E4D9B5')
    elif i in [1,3]:
        bowl_icon(x+75,566,.57,'#E8D8AF')
    else: octo_icon(x+75,560,.65,'#E8D8AF')
# The large striped canvas canopy.
path('M209,341 L1191,341 L1270,478 Q702,515 130,478Z','#102E34','none',0,transform='translate(0 13)',opacity=.35)
path('M220,334 L1180,334 L1263,476 Q700,507 137,476Z','url(#roof)',INK,7)
for i in [1,3,5,7]:
    # Eight evenly spaced fabric gores fan out to match the valance.
    a,b=220+i*120,220+(i+1)*120
    c,d=139+i*140,139+(i+1)*140
    path(f'M{a},338 H{b} L{d},478 Q{(d+c)/2},500 {c},490Z','#C97052','none',0)
for i in range(9):
    top,bottom=220+i*120,139+i*140
    path(f'M{top},342 Q{(top+bottom)/2},411 {bottom},481',stroke='#8E633D',sw=2,opacity=.7)
path('M225,344 H1176',stroke='#F9D997',sw=5)
path('M158,471 Q700,496 1242,471',stroke='#F8D18C',sw=3,opacity=.75)
# Broad alternating scallops across the awning lip.
for i in range(8):
    x=139+i*140
    color='#F0BB6B' if i%2==0 else '#CC7658'
    path(f'M{x},478 Q{x+70},483 {x+140},478 V511 Q{x+70},544 {x},511Z',color,INK,4)
    path(f'M{x+9},508 Q{x+70},533 {x+131},508',stroke='#F4CD87' if i%2==0 else '#E9936E',sw=2)
path('M139,478 Q700,502 1259,478',stroke=INK,sw=6)
# Title sign, attached to the roof rather than floating over the scene.
for x in [412,969]:
    rect(x,283,18,63,'#986944',INK,4,2)
rect(337,160,736,168,'#102F35','none',0,19,transform='translate(9 9)',opacity=.55)
rect(332,151,736,169,'#C9844D',INK,7,17)
rect(344,162,712,145,'#F5DEAD',INK,3,9)
rect(354,172,692,124,'none','#BD8650',2,4)
text('EIGHT ARMS',700,243,73,INK,'Rockwell-Bold',spacing=1.1,maxwidth=643)
text('MIDNIGHT RAMEN',700,281,20,'#9E5944','AvenirNext-Heavy',spacing=5.4)
for x in [365,1035]:
    for y in [184,285]:
        circle(x,y,3.3,'#906143')
        line(x-1.5,y+1.5,x+1.5,y-1.5,'#F1D5A1',1)
# Lantern halos are vector gradients; the body is ribbed paper.
for x,y,r in [(254,710,154),(1147,699,148)]:circle(x,y,r,'url(#lanternGlow)')
def lantern(cx,cy,kind):
    # cy is the vertical center, 190px body.
    line(cx,521,cx,cy-111,INK,5)
    line(cx+3,525,cx+3,cy-112,'#DDB168',1.7)
    ellipse(cx,cy-97,39,10,'#AE774A',INK,4)
    path(f'M{cx-41},{cy-92} C{cx-83},{cy-66} {cx-83},{cy+60} {cx-40},{cy+91} Q{cx},{cy+106} {cx+40},{cy+91} C{cx+83},{cy+60} {cx+83},{cy-66} {cx+41},{cy-92} Q{cx},{cy-103} {cx-41},{cy-92}Z','url(#redLantern)' if kind=='red' else 'url(#goldLantern)',INK,5)
    for dy in [-72,-48,-24,0,24,48,72]:
        ww=60 if abs(dy)<50 else 51
        path(f'M{cx-ww},{cy+dy} Q{cx},{cy+dy+12} {cx+ww},{cy+dy}',stroke='#9D653E',sw=2,opacity=.43)
    path(f'M{cx-27},{cy-86} C{cx-46},{cy-38} {cx-46},{cy+42} {cx-24},{cy+85}',stroke='#FFD294',sw=4,opacity=.55)
    path(f'M{cx+30},{cy-87} C{cx+50},{cy-30} {cx+50},{cy+40} {cx+27},{cy+86}',stroke='#9E633E',sw=2,opacity=.5)
    rect(cx-37,cy+91,74,13,'#8F6140',INK,4,3)
    rect(cx-36,cy-105,72,13,'#98613D',INK,4,3)
    line(cx,cy+106,cx,cy+123,INK,3)
    if kind=='red':
        text('麺',cx,cy+25,63,INK,'HiraginoSans-W6')
        path(f'M{cx-19},{cy+56} Q{cx},{cy+64} {cx+19},{cy+56}',stroke=INK,sw=2)
        for dx in [-5,0,5]:line(cx+dx,cy+124,cx+dx,cy+144,'#C88453',2)
    else:
        star(cx,cy-54,8,INK)
        text('OPEN',cx,cy-5,23,INK,'AvenirNext-Heavy',spacing=1)
        text('LATE',cx,cy+27,26,INK,'AvenirNext-Heavy',spacing=1.3)
        line(cx-22,cy+44,cx+22,cy+44,INK,2)
lantern(250,705,'red')
lantern(1150,695,'gold')
# Bézier swept outlines give each of the eight arms a tapering, living contour.
def cubic(p0,p1,p2,p3,t):
    u=1-t
    p=(u*u*u*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*p3[0],u*u*u*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*p3[1])
    v=(3*u*u*(p1[0]-p0[0])+6*u*t*(p2[0]-p1[0])+3*t*t*(p3[0]-p2[0]),3*u*u*(p1[1]-p0[1])+6*u*t*(p2[1]-p1[1])+3*t*t*(p3[1]-p2[1]))
    mag=math.hypot(*v) or 1
    return p,(-v[1]/mag,v[0]/mag),math.degrees(math.atan2(v[1],v[0]))
def poly(points,close=True):
    return 'M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+('Z' if close else '')
def arm(name,start,segments,side=1,root=40,cups=True):
    samples=[]; p0=start
    for p1,p2,p3 in segments:
        for j in range(30): samples.append(cubic(p0,p1,p2,p3,j/30))
        p0=p3
    samples.append(cubic(start if len(segments)==1 else segments[-2][2],*segments[-1],1))
    distances=[0]
    for i in range(1,len(samples)):
        distances.append(distances[-1]+math.dist(samples[i][0],samples[i-1][0]))
    total=distances[-1]
    widths=[root*(1-(s/total))**.72+4 for s in distances]
    left=[];right=[]
    for (p,n,a),r in zip(samples,widths):
        left.append((p[0]+n[0]*r,p[1]+n[1]*r));right.append((p[0]-n[0]*r,p[1]-n[1]*r))
    d=poly(left+right[::-1])
    emit(f'<g id="{name}"><clipPath id="clip-{name}"><path d="{d}"/></clipPath>')
    path(d,'url(#arm)',INK,5.6)
    group(clip_path=f'url(#clip-{name})')
    ribbon1=[];ribbon2=[];highlight=[]
    for (p,n,a),r in zip(samples,widths):
        ribbon1.append((p[0]+n[0]*r*side*.17,p[1]+n[1]*r*side*.17))
        ribbon2.append((p[0]+n[0]*r*side*.92,p[1]+n[1]*r*side*.92))
        highlight.append((p[0]-n[0]*r*side*.63,p[1]-n[1]*r*side*.63))
    path(poly(ribbon1+ribbon2[::-1]),'#F5B08A','none',0)
    path(poly(highlight[:-5],False),stroke='#FFBC91',sw=3.5,opacity=.72)
    if cups:
        nextcup=75
        for (p,n,a),r,dd in zip(samples,widths,distances):
            if dd>=nextcup and r>6:
                xx=p[0]+n[0]*r*side*.57; yy=p[1]+n[1]*r*side*.57
                rx=min(9.7,r*.32); ry=rx*.68
                ellipse(round(xx,2),round(yy,2),round(rx,2),round(ry,2),'#FFE0AE','#C47060',1.7,transform=f'rotate({a:.2f} {xx:.2f} {yy:.2f})')
                ellipse(round(xx,2),round(yy,2),round(rx*.36,2),round(ry*.40,2),'#D68C70','none',0,transform=f'rotate({a:.2f} {xx:.2f} {yy:.2f})')
                nextcup=dd+max(13,r*.78)
    end();end()
# Rear utensils: the upper right arm grips a long ladle.
path('M971,658 L1058,849',stroke=INK,sw=15)
path('M971,658 L1058,849',stroke='#E5BD79',sw=8)
line(978,674,1049,833,'#F9DCA0',2.4)
ellipse(1066,863,31,17,'#73A29A',INK,4,transform='rotate(-25 1066 863)')
ellipse(1066,859,24,10,'#CFB774',INK,2.5,transform='rotate(-25 1066 859)')
# The broth forms a continuous, golden pour.
path('M1078,872 C1081,885 1070,897 1070,909 C1070,918 1079,922 1074,936',stroke='#F2C368',sw=7)
path('M1079,875 C1081,893 1071,900 1073,911',stroke='#FFE1A0',sw=2)
# Uppermost and middle arms, exactly four behind the head.
arm('arm-1-noodles',(600,880),[
 ((521,870),(546,777),(486,763)),((421,748),(391,728),(420,699)),((439,680),(461,695),(451,712))],side=-1,root=38)
arm('arm-2-ladle',(792,877),[
 ((889,875),(858,771),(933,750)),((992,734),(1027,702),(997,676)),((978,660),(957,677),(967,692))],side=1,root=38)
arm('arm-3-seasoning',(598,914),[
 ((511,900),(495,964),(416,943)),((361,929),(338,881),(369,861)),((387,850),(408,865),(398,877))],side=-1,root=36)
arm('arm-4-greens',(804,914),[
 ((868,907),(893,955),(965,947)),((1029,939),(1063,892),(1035,869)),((1018,853),(999,865),(1008,879))],side=1,root=37)
# Chopsticks, long unbroken strands, and a curled gripping fingertip.
for x1,y1,x2,y2 in [(407,682,555,739),(405,696,551,751)]:
    line(x1,y1,x2,y2,INK,8)
    line(x1,y1,x2,y2,'#DDB36B',4.5)
    line(x1+5,y1+1,x2-4,y2-1,'#FADE99',1.5)
# Five individually drawn noodles hang into the bowl at lower left.
for i in range(6):
    x=539+i*4
    d=f'M{x},{742+i*.9} C{x-20},{786+i*2} {x+7},{822+i*2} {x-14},{857+i*2} S{474+i*4},{919-i} {464+i*6},{953+i*.2}'
    path(d,stroke='#805E3C',sw=6.1)
    path(d,stroke='#F2CF82',sw=3.5)
# A few quiet noodle highlights.
path('M544,766 C533,797 546,812 538,840',stroke='#FFE2A0',sw=1.4)
path('M443,695 Q460,702 451,712',stroke=INK,sw=19)
path('M443,695 Q460,702 451,712',stroke='#F09A7A',sw=12)
# Seasoning jar, tilted toward the waiting bowl.
group(transform='rotate(-27 389 850)')
rect(369,818,41,59,'#F1D8A6',INK,4,7)
rect(373,805,33,18,'#9C5745',INK,3,3)
line(380,811,400,811,'#D68D60',2)
rect(375,837,29,24,'#D47C58','none',0,3)
for xx,yy in [(384,844),(395,846),(389,854)]:ellipse(xx,yy,2,3,CREAM,'none',0,transform=f'rotate(30 {xx} {yy})')
end()
for x,y,r in [(418,880,2),(430,893,2.5),(421,902,1.8),(439,915,2.3),(450,925,2.1),(435,935,1.8)]:circle(x,y,r,'#F0CF8C')
# A bouquet of fresh scallions in the right-hand curl.
group(transform='rotate(-19 1007 870)')
for d,c in [('M1002,879 Q981,845 960,814 Q985,822 1008,873Z','#A3B77B'),('M1007,879 Q997,827 986,797 Q1007,816 1013,874Z','#6E9D73'),('M1012,878 Q1019,833 1032,809 Q1028,850 1018,883Z','#B2BE7E'),('M1013,872 Q1005,826 1014,793 Q1022,833 1019,877Z','#4F8A69')]:path(d,c,INK,2.5)
path('M1004,875 L1012,890 M1010,874 L1017,887 M1016,873 L1021,884',stroke='#ECE1B0',sw=5)
end()
# The expressive, gently pear-shaped chef's head.
path('M554,759 C546,701 592,649 647,646 C703,622 790,646 830,699 C873,758 854,853 808,902 C766,944 632,944 584,898 C553,866 541,808 554,759Z','url(#head)',INK,6)
path('M570,756 C563,715 600,679 630,675 C605,706 589,732 589,761 C588,785 567,790 570,756Z','#FBC298','none',0,opacity=.62)
path('M835,763 C849,821 824,883 793,897 C757,918 655,920 619,903 C694,919 806,893 824,824Z','#CA6560','none',0,opacity=.36)
# Speckles on the skin are placed, not noise filtered.
for x,y,r in [(595,723,4),(608,708,3),(589,739,2.8),(608,743,2),(807,738,4),(815,754,3),(800,719,2.7),(821,778,2),(579,802,2),(799,858,3),(816,839,2),(590,838,3),(603,855,2)]:circle(x,y,r,'#C86E61',opacity=.52)
ellipse(606,813,25,14,'#D76C64','none',0,opacity=.56)
ellipse(791,813,25,14,'#D76C64','none',0,opacity=.56)
path('M620,785 Q639,763 657,786 M740,785 Q758,763 776,785',stroke=INK,sw=7)
path('M624,752 Q640,745 652,753 M743,752 Q758,745 771,751',stroke='#B85D54',sw=3)
path('M673,814 Q699,825 725,813 C723,847 679,850 673,814Z',INK,INK,3)
path('M681,834 Q700,824 718,834 Q699,849 681,834Z','#F4B096','none',0)
path('M694,796 Q698,802 704,797',stroke='#BE6459',sw=3)
for x,y in [(595,808),(607,805),(618,811),(780,810),(792,805),(802,810)]:circle(x,y,2.5,'#F6B08A')
# Toque with a generous asymmetric silhouette and tailored band.
path('M598,645 C556,650 541,619 552,590 C561,560 589,553 613,564 C621,516 679,512 705,548 C735,516 784,527 790,565 C828,553 859,582 849,616 C844,639 825,654 802,650 L795,683 Q698,705 596,680Z','#F9EBCB',INK,6)
path('M559,610 Q559,574 588,574 M629,555 Q655,531 679,551 M728,551 Q757,538 772,562 M812,577 Q841,588 834,610',stroke='#FFF7E1',sw=7)
path('M561,625 Q581,646 609,635 M614,586 Q602,610 613,633 M697,572 Q684,598 694,621 M789,589 Q801,610 786,632 M813,631 Q831,628 837,616',stroke='#CEBB96',sw=3)
path('M595,644 Q699,666 804,643 L798,685 Q696,709 594,681Z','#E4D4AF',INK,4)
path('M603,651 Q699,671 794,650 L791,672 Q698,691 604,672Z','#FFF1D4','none',0)
path('M604,678 Q699,698 791,678',stroke='#BCA882',sw=1.5)
octo_icon(699,671,.34,'#AF7954')
# Apron and the little sea-green neckerchief.
path('M625,894 Q700,915 776,891 L793,996 Q700,1032 608,993Z','#EFE0B9',INK,5)
path('M636,920 L626,986 Q699,1011 780,988',stroke='#C9B28E',sw=3)
line(767,924,777,978,'#FFF3D3',4)
path('M602,875 Q700,908 797,873 L786,902 Q698,930 615,904Z','#29625F',INK,4)
path('M688,907 L702,896 719,907 704,925Z','#4E8D7B',INK,3)
path('M699,920 L673,951 665,919Z','#34736C',INK,3)
path('M709,922 L735,947 741,913Z','#34736C',INK,3)
line(679,922,677,936,'#95B99C',2)
line(722,923,730,936,'#95B99C',2)
bowl_icon(701,978,.65,'#49776C')
# Counter in three planes, visibly resting on the timber posts.
path('M217,1019 H1185 L1244,1070 H160Z','#E9B66A',INK,6)
path('M227,1027 H1176 L1211,1056 H192Z','#F2C985','none',0)
path('M262,1032 C462,1046 724,1028 903,1041 S1077,1040 1166,1048',stroke='#C89455',sw=2)
path('M208,1057 Q410,1064 529,1059 M951,1059 Q1067,1056 1210,1063',stroke='#A57748',sw=2)
rect(178,1070,1052,48,'#BC7F48',INK,6,4)
line(184,1080,1223,1080,'#E9B46B',3)
rect(232,1119,936,248,'#BC804D',INK,6,5)
group(clip_path='url(#frontPanel)')
rect(232,1119,936,248,'url(#wood)','none',0)
for x in range(238,1170,86):
    line(x,1122,x,1366,'#8F603D',3)
    line(x+5,1122,x+5,1360,'#EAB472',2)
    path(f'M{x+48},1120 C{x+19},1190 {x+65},1233 {x+39},1365',stroke='#AC7947',sw=2,opacity=.58)
# Painted sea-green fascia, with restrained Japanese wave ornament.
rect(276,1179,848,158,'#265B58',INK,4,9)
rect(287,1190,826,136,'none','#96AD87',1.6,5)
wave_band(335,1231,172,1.05,'#91AA88',.8)
wave_band(906,1231,172,1.05,'#91AA88',.8)
# central medallion and a playful maker's motto.
ellipse(700,1237,91,49,'#E9D4A6',INK,3)
bowl_icon(700,1238,.85,'#285B56')
text('SLOW BROTH. FAST ARMS.',700,1310,21,'#F4DFB4','AvenirNext-Heavy',spacing=3)
end()
rect(226,1351,948,24,'#8B5D3B',INK,5,3)
line(242,1355,1157,1355,'#D89F60',2)
# Two front service arms, supporting a bowl and steadying the stockpot.
arm('arm-5-serving',(639,957),[
 ((585,987),(526,1026),(468,1025)),((424,1024),(410,1004),(424,991)),((436,982),(451,987),(446,997))],side=-1,root=36)
arm('arm-6-stockpot',(771,956),[
 ((827,997),(908,1022),(974,1003)),((1019,990),(1036,963),(1014,950)),((998,942),(989,953),(997,962))],side=1,root=36)
# A folded service towel at the right corner of the counter.
path('M1117,1027 L1170,1024 1204,1051 1199,1129 Q1173,1142 1140,1127 L1144,1055Z','#E9DFC2',INK,4)
path('M1149,1056 L1146,1126 M1158,1056 L1155,1130 M1178,1054 L1176,1131 M1187,1055 L1184,1129',stroke='#53837A',sw=3)
path('M1126,1031 L1154,1050 H1193',stroke='#C0B294',sw=2)
# The two long foreground curls bring the octopus over the edge of the booth.
arm('arm-7-front-left',(660,964),[
 ((599,1026),(615,1114),(533,1148)),((482,1169),(433,1133),(448,1096)),((459,1068),(493,1071),(492,1093)),((492,1104),(482,1107),(477,1102))],side=-1,root=38)
arm('arm-8-front-right',(749,964),[
 ((788,1028),(797,1123),(878,1154)),((935,1176),(990,1138),(974,1100)),((962,1073),(933,1079),(937,1099)),((939,1108),(948,1112),(953,1106))],side=1,root=38)
# A dark wooden spoon and chopstick crock on the far left.
ellipse(317,1047,39,9,'#684F37','none',0,opacity=.33)
for i,(x,angle) in enumerate([(301,-10),(311,-5),(319,1),(326,8),(333,14)]):
    group(transform=f'rotate({angle} {x} 992)')
    line(x,1006,x,917,INK,7)
    line(x,1005,x,917,'#BC8553',3.6)
    line(x,926,x,937,'#F0C884',4)
    end()
path('M286,976 L294,1040 Q317,1051 342,1040 L348,976Z','#D58D54',INK,4)
ellipse(317,976,31,8,'#694F38',INK,3)
path('M300,987 L304,1034 M333,987 L330,1037',stroke='#F1BE76',sw=2)
# Main stockpot: brass rim, broth, side handles and silver-green enamel.
ellipse(1056,1038,83,15,'#8D7148','none',0,opacity=.36)
path('M985,957 C952,947 950,996 983,990 M1123,955 C1153,944 1160,991 1126,992',stroke=INK,sw=11)
path('M985,957 C952,947 950,996 983,990 M1123,955 C1153,944 1160,991 1126,992',stroke='#80A59B',sw=5)
path('M984,938 L992,1015 Q1056,1053 1120,1015 L1127,938Z','url(#pot)',INK,5)
path('M1005,959 L1010,1013 Q1039,1024 1068,1024',stroke='#B7CBB0',sw=4,opacity=.7)
line(1106,957,1102,1011,'#2F6867',3)
ellipse(1055,938,72,21,'#9EAD8C',INK,4)
ellipse(1055,938,62,15,'#C78C44',INK,3)
path('M1007,938 Q1054,924 1099,936',stroke='#EBC271',sw=3)
for x,y,r in [(1033,941,4),(1053,934,3),(1077,940,4),(1095,935,2)]:ellipse(x,y,r,r*.48,'#F0C77A','none',0)
rect(1029,978,50,25,'#D6C89E',INK,2,6)
star(1054,990,8,'#416F65')
# A small bowl in the serving arm.
ellipse(469,1019,76,11,'#694D36','none',0,opacity=.25)
ellipse(469,1009,29,7,'#D6C29B',INK,3)
path('M387,948 Q397,1000 448,1010 H486 Q538,1002 551,948Z','#EAD8B0',INK,4)
path('M397,968 Q469,997 541,968',stroke='#C86F55',sw=9)
path('M405,983 Q469,1007 534,984',stroke='#41786F',sw=3)
ellipse(469,948,82,23,'#EEDBB6',INK,4)
ellipse(469,948,73,17,'#BB8042',INK,2.5)
# Tangles of golden noodles, a nori sheet, scallions, half an egg.
path('M489,941 L503,911 526,922 516,948Z','#284F44',INK,2.5)
for xx in [501,509,517]:line(xx,926,xx-6,944,'#699275',1.5)
for d in ['M415,950 C443,930 444,964 466,943 S504,950 520,947','M424,955 C449,942 463,967 482,948 S505,950 514,953','M436,944 Q462,924 481,944 T516,945']:
    path(d,stroke='#F3CF7C',sw=3)
group(transform='rotate(-23 435 942)')
ellipse(435,942,17,23,'#FFF0CC',INK,2.5)
ellipse(435,944,10,13,'#F1AF45','#D28C3D',1.5)
end()
for x,y,a in [(474,940,20),(483,947,-10),(492,941,25),(475,951,-30)]:
    rect(x,y,9,5,'#87AA6B','#3F7059',1,1,transform=f'rotate({a} {x} {y})')
# The hero bowl at the center, a generous arrangement of ramen toppings.
ellipse(700,1074,142,16,'#6E4D36','none',0,opacity=.3)
ellipse(700,1069,49,10,'#D8C19B',INK,4)
path('M560,978 Q576,1047 662,1068 Q699,1077 739,1067 Q826,1046 840,978Z','url(#ceramic)',INK,5)
path('M570,1002 Q699,1049 831,1001',stroke='#C66751',sw=13)
path('M575,1015 Q700,1057 826,1015',stroke='#F5E8C6',sw=4)
# Painted blue wave motifs on the curving porcelain.
for x,y in [(620,1032),(655,1042),(691,1048),(727,1045),(762,1037)]:
    path(f'M{x-13},{y} Q{x},{y-15} {x+13},{y} M{x-8},{y+2} Q{x},{y-7} {x+8},{y+2}',stroke='#38756C',sw=2.5)
ellipse(700,978,140,35,'#F4DEB4',INK,5)
ellipse(700,975,128,26,'#BC8141',INK,3)
path('M587,977 Q700,1017 813,977',stroke='#E6B15B',sw=3)
# Dark nori at the back and its delicate broken grid.
path('M759,963 L773,913 819,930 807,974Z','#254C43',INK,3)
path('M772,951 L780,925 808,935 799,961 M778,936 L805,946 M775,945 L802,954 M789,929 L781,954 M799,933 L792,958',stroke='#608875',sw=1.7)
# Menma bamboo shoots, left of the egg.
for x,y,angle in [(601,965,-23),(608,955,-17),(615,963,-14)]:
    group(transform=f'rotate({angle} {x} {y})')
    rect(x,y,40,9,'#D2A256','#815D34',1.8,2)
    line(x+6,y+4,x+35,y+4,'#F2C97C',1.5)
    end()
# Noodle knots in the visible broth.
for d in ['M640,979 C654,958 677,990 690,974 S728,983 740,973','M620,982 C650,968 658,997 682,981 S719,991 737,980','M651,988 C673,974 684,997 706,982 S745,994 765,981','M709,974 C730,953 746,979 771,968','M592,976 C615,969 629,989 647,977']:
    path(d,stroke='#F4CF7B',sw=4)
# Chashu pork with a stylized spiral grain.
group(transform='rotate(15 752 973)')
ellipse(752,973,38,23,'#A66044',INK,2.5)
ellipse(752,971,33,19,'#DFAC81','#EDC597',3)
path('M726,970 C734,953 768,954 777,969 C783,984 746,992 735,976 C729,966 760,959 765,970 C770,980 746,981 745,972 Q750,967 755,973',stroke='#B57559',sw=3)
end()
# Jammy egg half, clearly silhouetted against the soup.
group(transform='rotate(-24 646 959)')
path('M622,963 C618,945 630,925 643,925 C663,926 678,949 671,967 C664,987 629,987 622,963Z','#FFF1D1',INK,3)
ellipse(647,958,16,18,'#EBA33A','#CF8631',2)
path('M639,948 Q646,941 655,949',stroke='#FFD472',sw=3)
end()
# A pink narutomaki spiral nestled at the back.
group(transform='rotate(-8 700 953)')
path('M676,953 Q672,945 680,942 Q681,933 689,936 Q698,929 704,936 Q714,932 718,941 Q728,942 723,951 Q728,960 719,963 Q716,970 707,966 Q699,973 693,966 Q682,969 680,961 Q672,960 676,953Z','#F7E6C3',INK,2.5)
path('M687,954 C681,941 705,938 714,949 C720,959 701,963 694,956 C688,949 705,946 706,953',stroke='#DB8A88',sw=3.3)
end()
# Scallion rings and sesame flecks.
for x,y,rx,a in [(669,971,6,25),(679,968,6,-10),(688,976,6,-20),(707,983,5,25),(722,978,6,-15),(796,976,5,30),(789,970,6,20),(662,980,5,-20)]:
    ellipse(x,y,rx,rx*.55,'#92B36E','#47785C',1.8,transform=f'rotate({a} {x} {y})')
    ellipse(x,y,rx*.35,rx*.18,'#D8D596','none',0,transform=f'rotate({a} {x} {y})')
for x,y in [(615,979),(731,969),(738,983),(776,985),(721,962),(623,990),(685,989)]:
    line(x,y,x+3,y-2,'#FFE4A7',1.7)
# Steam is last: soft curls, with space around the smiling face.
steam('M623,927 C604,908 624,893 615,879 C605,864 603,854 614,842',5,.74)
steam('M688,921 C670,898 692,888 682,869',5,.7)
steam('M748,925 C771,906 748,893 764,873 C773,861 775,852 769,842',5,.72)
steam('M448,912 C431,894 449,881 440,866',4,.62)
steam('M1023,913 C1001,895 1025,882 1020,867',4,.55)
steam('M1099,905 C1116,881 1090,873 1103,851 C1112,836 1104,825 1098,818',5,.72)
# A hanging price tile tucked beside the left post.
line(261,1119,270,1180,INK,2.5)
line(312,1119,306,1178,INK,2.5)
group(transform='rotate(-7 286 1211)')
rect(248,1177,77,91,'#F1D59A',INK,4,5)
rect(255,1184,63,76,'none','#BD8851',1.5,2)
text('ONE',286,1206,13,INK,spacing=2)
text('MORE',286,1226,13,INK,spacing=1)
text('BOWL?',286,1247,14,'#B5644B','AvenirNext-Heavy',spacing=.8)
end()
# Inviting, empty stools, with sturdy cross-bracing and little brass collars.
def stool(x,y):
    ellipse(x,y+112,94,12,'#173E3E','none',0,opacity=.6)
    for dx in [-35,35]:
        path(f'M{x+dx},{y+7} L{x+dx*1.6},{y+108}',stroke=INK,sw=16)
        path(f'M{x+dx},{y+7} L{x+dx*1.6},{y+108}',stroke='#B7804E',sw=9)
        path(f'M{x+dx*1.5},{y+94} L{x+dx*1.6},{y+107}',stroke='#E6B268',sw=9)
    path(f'M{x-47},{y+65} Q{x},{y+89} {x+47},{y+65} M{x-43},{y+53} Q{x},{y+39} {x+43},{y+53}',stroke=INK,sw=8)
    path(f'M{x-47},{y+65} Q{x},{y+89} {x+47},{y+65}',stroke='#C68D54',sw=4)
    path(f'M{x-69},{y-2} V{y+15} Q{x},{y+45} {x+69},{y+15} V{y-2}Z','#A95D43',INK,5)
    ellipse(x,y-2,69,22,'#D98159',INK,5)
    ellipse(x,y-5,59,15,'#E8A76C','none',0)
    path(f'M{x-43},{y-10} Q{x},{y-21} {x+40},{y-9}',stroke='#F6C586',sw=2.5)
    path(f'M{x-33},{y+20} Q{x},{y+28} {x+30},{y+20}',stroke='#E6A36C',sw=2)
stool(353,1338)
stool(1052,1338)
# A tiny fallen blossom and a few street glints.
for x,y in [(171,1448),(1203,1466),(1253,1366)]:
    path(f'M{x-4},{y} Q{x-8},{y-9} {x},{y-5} Q{x+8},{y-10} {x+6},{y} Q{x+3},{y+8} {x},{y+2} Q{x-7},{y+8} {x-4},{y}Z','#CC966D','none',0,opacity=.65)
# Bottom line is spaced like a print edition, not an interface.
line(404,1501,486,1501,'#BDBB8F',1.5)
line(914,1501,996,1501,'#BDBB8F',1.5)
star(391,1501,4,'#DCC994');star(1009,1501,4,'#DCC994')
text('PULL UP A STOOL.',700,1508,19,'#EBD8AC','AvenirNext-DemiBold',spacing=4.6)
# A subtle all-vector paper tooth unifies the flat colors.
rect(40,40,1320,1520,'url(#paper)','none',0,32,pointer_events='none')
end() # scene clip
# Fine inset framing, and small corner details in the paper margin.
rect(40,40,1320,1520,'none',INK,3,32)
for x,y,a in [(23,23,0),(1377,23,90),(1377,1577,180),(23,1577,270)]:
    group(transform=f'translate({x} {y}) rotate({a})')
    path('M0,25V8 Q0,0 8,0H25',stroke=INK,sw=2)
    end()
emit('</svg>')
# Outline all type in one CoreText pass. The SVG contains no external font links.
requests=[dict(text=t['text'],size=t['size'],font=t['font'],spacing=t['spacing']) for t in texts]
result=subprocess.run(['swift',str(ROOT/'src'/'outline_text.swift')],input=json.dumps(requests),capture_output=True,text=True,check=True)
outlined=json.loads(result.stdout)
svg='\n'.join(parts)
for i,(t,o) in enumerate(zip(texts,outlined)):
    width=o['width']; scale=1
    if t['maxwidth'] and width>t['maxwidth']:scale=t['maxwidth']/width
    dx=width*scale/2 if t['anchor']=='middle' else (width*scale if t['anchor']=='end' else 0)
    markup=f'<g aria-label="{escape(t["text"],quote=True)}" transform="translate({t["x"]-dx:.3f} {t["y"]}) scale({scale:.6f} -1)"><path fill="{t["fill"]}" d="{o["d"]}"/></g>'
    svg=svg.replace(f'__LETTERING_{i}__',markup)
(OUT/'eight-arms-ramen.svg').write_text(svg)
print(f'Created output/eight-arms-ramen.svg ({len(svg):,} bytes)')
