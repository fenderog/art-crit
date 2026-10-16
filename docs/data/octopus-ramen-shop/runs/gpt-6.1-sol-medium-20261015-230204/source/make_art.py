from pathlib import Path
from math import sin, cos, pi

# Original vector illustration. All shapes and lettering are embedded in the SVG.
W=1200
parts=[]
def add(s): parts.append(s)
def path(d,fill='none',stroke=None,sw=3,extra=''):
    add(f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+f' {extra}/>')
def rect(x,y,w,h,fill,rx=0,stroke=None,sw=3):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def ellipse(x,y,rx,ry,fill,stroke=None,sw=3):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
def text(x,y,s,size=20,fill='#173e46',weight='600',extra=''):
    add(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Trebuchet MS, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{s}</text>')
ink='#173e46'; cream='#fff1d2'; coral='#ec795f'; light='#ffb18a'; teal='#3b8d85'; gold='#efb653'
add('''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200" role="img" aria-labelledby="title desc">
<title id="title">Tako Ramen — eight arms, one perfect bowl</title>
<desc id="desc">An eight-armed coral octopus chef in a tall white toque cooks noodles at a teal and vermilion ramen booth, under striped curtains and glowing paper lanterns.</desc>
<defs>
 <pattern id="paper" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="3" cy="5" r=".7" fill="#173e46" opacity=".08"/><circle cx="13" cy="14" r=".6" fill="#173e46" opacity=".06"/></pattern>
 <pattern id="waves" width="100" height="48" patternUnits="userSpaceOnUse"><path d="M-50 48a50 45 0 0 1 100 0m-38 0a38 33 0 0 1 76 0m-64 0a26 22 0 0 1 52 0m-40 0a14 11 0 0 1 28 0M50 48a50 45 0 0 1 100 0" fill="none" stroke="#8ac1ab" stroke-width="2" opacity=".35"/></pattern>
</defs>''')
rect(0,0,1200,1200,cream)
rect(0,0,1200,1200,'url(#paper)')
rect(31,31,1138,1138,'none',30,ink,2)
rect(43,43,1114,1114,'none',22,ink,1)
# Corner ornaments
for x,y in [(67,69),(1133,69),(67,1131),(1133,1131)]:
    ellipse(x,y,5,5,coral)
text(600,91,'THE LITTLE BOOTH WITH A LOT OF HANDS',14,ink,'700','letter-spacing="4"')
text(600,186,'TAKO RAMEN',91,ink,'900','letter-spacing="5"')
path('M166 213H1034',stroke=ink,sw=2)
text(600,244,'EIGHT ARMS. ONE PERFECT BOWL.',20,ink,'700','letter-spacing="3.5"')
# Tiny octopus crest flanking title
for x in [112,1088]:
    ellipse(x,149,19,22,coral,ink,2)
    for dx in [-14,0,14]:
        path(f'M{x+dx} 161q-10 29 -17 11',stroke=ink,sw=6)
        path(f'M{x+dx} 161q-10 29 -17 11',stroke=coral,sw=3)
    ellipse(x-6,148,2,3,ink);ellipse(x+6,148,2,3,ink)
# Booth shadow and rear panel
ellipse(600,1102,455,24,'#ded7b9')
rect(150,322,900,575,ink,10,ink,4)
rect(181,343,838,528,'#f6d999',0)
# warm circular backdrop and rays
ellipse(600,590,298,260,'#fbe9b9')
for a in range(205,341,15):
    r=a*pi/180
    path(f'M{600+280*cos(r):.2f} {612+260*sin(r):.2f}l{22*cos(r):.2f} {22*sin(r):.2f}',stroke='#d5a45b',sw=3)
# Vertical structure
for x in [150,1024]:
    rect(x,331,26,556,ink,5)
    path(f'M{x+8} 354v502',stroke='#46726a',sw=3)
# lantern ropes
for x in [262,938]:
    path(f'M{x} 342v63',stroke=ink,sw=4)
    rect(x-22,397,44,12,ink,4)
    ellipse(x,461,49,60,coral,ink,4)
    for dx in [-29,-13,13,29]:
        path(f'M{x+dx*.65} 409Q{x+dx*1.3} 461 {x+dx*.65} 513',stroke='#c95645',sw=2)
    path(f'M{x-42} 439h84m-89 23h94m-88 23h82',stroke='#ffc28b',sw=2)
    rect(x-22,513,44,12,ink,4)
    text(x,478,'麺' if False else '麵',30,cream,'800') if False else text(x,477,'R',39,cream,'800')
    path(f'M{x} 526v23m-6-9v15m12-15v15',stroke=gold,sw=3)
# small menu on back wall
rect(207,589,119,167,cream,5,ink,3)
text(266,618,'MENU',16,ink,'800','letter-spacing="2"')
path('M225 630h82',stroke=ink,sw=2)
for yy,label in [(654,'SHOYU'),(683,'MISO'),(712,'SPICY')]:
    text(266,yy,label,13,ink,'700','letter-spacing="1.5"')
text(266,741,'OPEN LATE',10,coral,'800','letter-spacing="1"')
# octopus tentacles, behind head and front objects
# outline then colored core, giving consistent hand-inked contours
def arm(d,w=43):
    path(d,stroke=ink,sw=w+7);path(d,stroke=coral,sw=w)
def suckers(points):
    for x,y,r in points:
        ellipse(x,y,r,r*.73,light)
        ellipse(x,y,r*.4,r*.27,'#d96555')
# 1: high left wok arm
arm('M527 653C453 666 415 599 402 549S354 513 361 548Q365 566 379 556',42)
suckers([(475,650,8),(446,630,8),(425,602,7),(415,574,7),(403,549,6)])
# 2: high right noodle lifting arm
arm('M673 648C759 654 799 584 792 513S834 438 849 468Q858 491 838 493',43)
suckers([(720,638,8),(748,620,8),(771,595,8),(785,566,7),(786,536,7),(795,503,6)])
# 3: lateral left curls
arm('M522 689C466 687 444 744 400 727S342 672 363 645Q381 624 392 643',43)
suckers([(482,700,8),(451,719,8),(419,728,8),(389,714,7),(369,692,7)])
# 4: lateral right ladle arm
arm('M679 690C740 683 772 739 818 717S868 665 842 651Q824 642 818 658',43)
suckers([(716,697,8),(745,714,8),(775,729,8),(807,725,7),(832,706,7)])
# 5 & 6 low sweeping arms
arm('M545 710C511 745 510 800 466 819S387 815 392 790Q398 772 412 786',46)
suckers([(520,753,8),(506,781,8),(485,805,8),(455,820,8),(426,822,7)])
arm('M654 713C697 751 689 797 738 816S818 814 812 791Q808 776 794 786',46)
suckers([(680,752,8),(694,783,8),(716,806,8),(747,820,8),(777,821,7)])
# body, smooth bell silhouette
path('M478 610C457 520 493 454 585 449C685 440 740 510 721 600L699 688Q686 742 602 747Q514 744 494 687Z',coral,ink,5)
path('M492 558C488 516 522 483 553 478',stroke=light,sw=13)
# face
ellipse(545,585,10,15,ink);ellipse(654,585,10,15,ink)
ellipse(542,580,3,4,cream);ellipse(651,580,3,4,cream)
path('M527 555q15-12 30 0M640 555q15-12 29 0',stroke=ink,sw=5)
ellipse(517,610,19,10,'#f7987c');ellipse(682,610,19,10,'#f7987c')
path('M575 615Q600 645 625 615',stroke=ink,sw=5)
# neckerchief
path('M499 676Q600 727 702 674L688 708Q599 751 513 709Z',teal,ink,4)
path('M603 720l-34 60 40-11 24 18 6-67',teal,ink,4)
ellipse(614,720,18,13,'#7bb7a3',ink,3)
# hat, cloud top
path('M495 471L486 420C444 411 446 359 481 348C477 307 527 291 554 317C577 278 632 285 649 319C688 295 729 326 720 359C763 379 743 427 708 428L701 471Z',cream,ink,5)
path('M512 355q-6 20 8 37m69-68q-17 24-9 57m80-42q17 23 6 46',stroke='#dfd7b6',sw=5)
path('M492 429Q599 407 708 430L701 474Q599 451 499 475Z',cream,ink,4)
path('M509 447q92-15 182 0',stroke=coral,sw=3)
# final two arms, in front of torso, serving a bowl
arm('M536 715C544 758 561 775 541 802Q526 821 502 810',36)
arm('M665 714C653 754 638 779 661 802Q675 816 694 808',36)
suckers([(544,754,6),(546,779,6),(532,800,6),(656,754,6),(654,780,6),(670,801,6)])
# Wok on left: airborne veg and noodles
path('M310 549l-52-25',stroke=ink,sw=12)
path('M306 542Q350 611 405 544Z',ink,ink,3)
path('M309 540Q359 525 405 540Q359 557 309 540Z',teal,ink,3)
for dx,dy in [(330,520),(345,506),(368,513),(384,525)]:
    path(f'M{dx} {dy}q9-20 19-3',stroke=gold,sw=4)
path('M332 490l8-10m32 13 8-12m-20-8-7-11',stroke=teal,sw=6)
# Chopsticks and hanging noodles
path('M804 467L936 415M808 479L944 434',stroke=ink,sw=8)
path('M804 467L936 415M808 479L944 434',stroke=gold,sw=4)
for i in range(5):
    x=885+i*7
    path(f'M{x} {445-i*2}C{x-12} 492 {x+13} 513 {x-2} 546S{x-18} 584 {x-7} 604',stroke=gold,sw=4)
# ladle on right
path('M836 661l48-78',stroke=ink,sw=10)
path('M836 661l48-78',stroke='#c88a52',sw=5)
path('M866 580q29-20 50 5q-4 35-33 31q-23-8-17-36',ink)
path('M875 581q20-9 30 6',stroke=teal,sw=4)
# roof/canvas curtain in front
rect(126,277,948,47,ink,12,ink,3)
path('M139 289h921',stroke=teal,sw=4)
# five split noren panels
for i in range(6):
    x=143+i*153
    path(f'M{x} 316h147v65q-73 32-147 0Z',coral if i%2==0 else cream,ink,4)
    path(f'M{x+12} 330v43',stroke='#b95545' if i%2==0 else '#decfa8',sw=2)
    if i in [1,4]:
        ellipse(x+74,351,19,19,ink)
        path(f'M{x+63} 351h22m-11-11v22',stroke=cream,sw=3)
# counter and steaming hero bowl
rect(123,860,954,36,ink,9,ink,4)
rect(137,860,927,14,'#d19a58',5)
path('M156 866h887',stroke='#efbe78',sw=2)
# condiment bottles left
rect(222,813,34,45,coral,5,ink,3);rect(228,797,22,18,ink,3)
rect(228,831,22,15,cream,1)
rect(277,804,34,54,gold,5,ink,3);rect(283,792,22,15,ink,2)
path('M286 823v21m9-21v21',stroke=cream,sw=3)
# chopsticks cup right
path('M908 797l8 61h48l8-61Z',teal,ink,3)
for x,off in [(922,-9),(934,3),(947,10),(957,5)]:
    path(f'M{x} 808l{off} -67',stroke=ink,sw=5)
    path(f'M{x} 808l{off} -67',stroke=gold,sw=2)
path('M912 810h56',stroke=cream,sw=3)
# Main ramen bowl
ellipse(600,841,134,16,'#916f4b',None)
path('M472 780Q485 849 563 860H638Q713 847 728 780Z',cream,ink,5)
path('M485 807Q600 842 715 807L704 827Q601 863 496 827Z',coral)
path('M562 857h77l-5 10h-67Z',ink)
ellipse(600,779,129,35,cream,ink,5)
ellipse(600,780,116,25,'#bb623b')
# noodle loops visible in soup
for i in range(7):
    path(f'M{501+i*14} 783q15-19 30-2t31 0',stroke=gold,sw=4)
# nori
path('M645 768l8-57 41 14-8 58Z',ink,ink,3)
for i in range(3):
    path(f'M{659+i*9} 728l-5 33',stroke=teal,sw=2)
# egg and pork
add('<g transform="rotate(-24 563 766)">')
ellipse(563,766,27,33,cream,ink,3);ellipse(563,771,15,17,gold);add('</g>')
path('M599 773q-18-41 17-44q34 0 27 33q-5 21-44 11',light,ink,3)
path('M608 762q-14-20 7-22q19 0 17 17q-2 10-15 6',stroke='#c76550',sw=3)
for x,y in [(511,771),(524,782),(635,786),(652,780),(672,790),(586,793)]:
    path(f'M{x} {y}l8-5 4 6-8 5Z',teal)
# steam, ivory against backdrop
for d in ['M539 720c-25-26 22-36 1-65','M589 705c-27-29 26-44 4-73','M626 704c-17-19 19-29 10-49']:
    path(d,stroke=cream,sw=6)
# booth lower front
rect(151,896,898,184,teal,2,ink,5)
rect(164,912,872,151,'url(#waves)',0)
rect(180,923,840,127,'none',2,'#8ac1ab',2)
# front central cartouche
rect(383,929,434,110,cream,55,ink,4)
text(600,973,'GOOD THINGS',23,ink,'900','letter-spacing="4"')
text(600,1009,'COME IN EIGHTS',23,ink,'900','letter-spacing="3"')
for x in [324,876]:
    ellipse(x,984,25,25,gold,ink,3)
    path(f'M{x-10} 984h20m-10-10v20',stroke=ink,sw=3)
# feet
for x in [186,978]: rect(x,1081,36,20,ink,3)
# bottom editorial line
text(600,1137,'HAND-PULLED  •  HEART-FELT  •  OCEAN-APPROVED',15,ink,'700','letter-spacing="2"')
add('</svg>')
Path('output/octopus-ramen.svg').write_text('\n'.join(parts))
