from pathlib import Path
s = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1000 1000">
<defs>
 <linearGradient id="back" x2="0" y2="1"><stop stop-color="#a9bbb4"/><stop offset="1" stop-color="#d4d5bc"/></linearGradient>
 <linearGradient id="cream" x2=".8" y2="1"><stop stop-color="#f5dab0"/><stop offset="1" stop-color="#c49972"/></linearGradient>
 <linearGradient id="teal" x2="1" y2="1"><stop stop-color="#709e99"/><stop offset="1" stop-color="#335e60"/></linearGradient>
 <linearGradient id="red" x2="1" y2="1"><stop stop-color="#d78c71"/><stop offset="1" stop-color="#a35249"/></linearGradient>
 <linearGradient id="dark" x2="1" y2="1"><stop stop-color="#56666a"/><stop offset="1" stop-color="#2f424a"/></linearGradient>
 <radialGradient id="light"><stop stop-color="#eee5cc" stop-opacity=".8"/><stop offset="1" stop-color="#eee5cc" stop-opacity="0"/></radialGradient>
 <pattern id="paper" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="1" cy="2" r=".6" fill="#253e43" opacity=".09"/><circle cx="5" cy="5" r=".6" fill="#fff5d6" opacity=".25"/></pattern>
</defs>
<rect width="1000" height="1000" fill="#ede1c7"/>
<rect x="29" y="29" width="942" height="942" rx="5" fill="#283f45"/>
<rect x="40" y="40" width="920" height="920" fill="url(#back)"/>
<ellipse cx="500" cy="415" rx="420" ry="460" fill="url(#light)"/>
<!-- old-fashioned studio drapes -->
<path d="M40 40H194Q152 251 104 392L40 468Z" fill="#73918a"/>
<path d="M40 40H79Q104 183 58 386M139 40Q145 207 84 355" fill="none" stroke="#476f6c" stroke-width="9" opacity=".3"/>
<path d="M960 40H843Q868 210 926 350L960 392Z" fill="#73918a"/>
<path d="M905 40Q889 201 953 326" fill="none" stroke="#476f6c" stroke-width="10" opacity=".25"/>
<path d="M40 765Q500 718 960 765V960H40Z" fill="#afac93"/>
<path d="M40 833Q500 778 960 833M40 922Q500 851 960 922" fill="none" stroke="#89958a" opacity=".45"/>
<ellipse cx="511" cy="869" rx="362" ry="58" fill="#596f68" opacity=".22"/>
</svg>'''.replace('</svg>','')]
def add(x): s.append(x)
def circle(x,y,r,fill,sw=3): add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#2b4449" stroke-width="{sw}"/>')
def rect(x,y,w,h,r,fill,sw=3): add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="#2b4449" stroke-width="{sw}"/>')
def path(d,fill='none',stroke='#2b4449',width=3): add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
def bolt(x,y):
 circle(x,y,4,'#c7ba98',1.5);path(f'M{x-2} {y+2}l4 -4',width=1)
def limb(d,col,width=23):
 path(d,stroke='#2b4449',width=width+6);path(d,stroke=col,width=width)
# broad, anxious father behind everyone
limb('M400 545L391 736L370 835','#547e7a',34)
limb('M474 545L479 733L493 831','#547e7a',34)
rect(335,826,72,35,11,'url(#dark)');rect(467,825,76,35,11,'url(#dark)')
rect(328,340,194,228,29,'url(#teal)',4)
rect(354,361,141,169,15,'#81a69b',2)
path('M389 343L426 376L463 343','#dfd4b4')
path('M421 376L434 376L443 473L428 489L414 473Z','#b36854',width=2)
rect(380,305,91,44,8,'#b7baa5')
# antenna and large head
path('M418 199L409 167');circle(409,160,8,'#d99575')
rect(321,217,222,111,23,'url(#teal)',4)
rect(307,249,15,46,5,'#b7baa5');rect(543,246,16,44,5,'#b7baa5')
rect(345,236,173,47,14,'#293f45',2)
circle(388,258,12,'#f8dd9c',0);circle(476,258,12,'#f8dd9c',0)
path('M366 228l31 -4M462 223l32 8',stroke='#2b4449',width=6)
# painfully rigid smile
rect(389,296,86,13,3,'#e2cfac',2)
for x in range(401,470,13):path(f'M{x} 298v9',width=1.5)
for x,y in [(338,232),(528,232),(339,310),(525,310),(346,549),(503,549)]:bolt(x,y)
# mother tall asymmetrical, leaning affectionately into father
limb('M613 521L601 699L622 829','#c89f79',25)
limb('M666 527L679 711L692 831','#c89f79',25)
rect(597,821,61,34,9,'url(#red)');rect(668,825,65,30,9,'url(#red)')
add('<g transform="rotate(-7 627 375)">')
path('M581 337Q627 318 670 339L691 529Q636 559 563 527Z','url(#cream)',width=4)
path('M582 340L622 374L669 339','#f4dfbb')
path('M622 374L610 501M610 501l-24 27',stroke='#ad795e',width=2)
for y in (396,423,450):circle(637,y,5,'#b56652',1)
rect(608,291,32,41,6,'#81948b')
rect(568,186,124,115,35,'url(#cream)',4)
path('M577 212Q620 220 678 208',stroke='#b58568',width=2)
rect(584,224,93,36,15,'#3d5356',2)
# kindly squint, mismatched gaze
path('M597 245q9 -13 18 0M647 242q9 -12 18 0',stroke='#f5dca2',width=4)
path('M610 277q16 12 32 -1',width=3)
circle(571,267,8,'#bb7060',1);circle(688,263,8,'#bb7060',1)
# decorative antenna bun
path('M623 185v-20');circle(623,148,21,'#b7775f');circle(623,148,11,'#d3aa7f',2)
path('M640 141q26 -25 32 0q-17 13 -32 0M640 141q-11 -29 -25 -18q-2 23 25 18','#507e79',width=2)
add('</g>')
# mother's arm wraps across father: awkward possessive hand
limb('M577 358Q543 337 501 336L486 319','#d6b58f',22)
circle(546,342,13,'#9baa97')
rect(467,312,41,25,8,'url(#cream)',2)
for x in (476,485,494):path(f'M{x} 317v13',width=1.5)
# dad's dangling arm behind grandma
limb('M331 371L288 458L299 537','#608b84',25);circle(288,458,16,'#c0b899')
# mother's other arm on resistant teenager
limb('M683 364L737 446L749 483','#d6b58f',23);circle(735,441,14,'#84958a')
# upholstered portrait bench
rect(178,636,645,119,20,'#805f50',4)
rect(161,729,677,37,11,'#a8795b')
for x in (190,791):path(f'M{x} 765l-10 105h30l8 -105Z','#5c554b')
# Grandma squat vintage radio robot, seated
limb('M225 718L217 801L200 849','#bd9f78',26)
limb('M303 721L325 791L316 850','#bd9f78',26)
rect(168,841,66,32,13,'url(#dark)');rect(297,846,69,29,12,'url(#dark)')
path('M189 567Q258 546 326 567L346 718Q259 750 179 716Z','url(#red)',width=4)
# knitted collar scallops
path('M196 567q5 38 25 17q10 31 28 7q16 25 30 -2q24 19 27 -20L259 552Z','#e3ce9e',width=2)
for y in range(617,694,15):
 for x in range(209,320,17):path(f'M{x} {y}l5 4l5 -4',stroke='#edb48c',width=1.2)
rect(192,429,135,131,25,'url(#cream)',4)
rect(180,460,13,48,5,'#a98364');rect(328,460,13,48,5,'#a98364')
# head coil hair
for x,y in [(202,430),(216,418),(234,412),(254,411),(275,412),(296,418),(315,430)]:circle(x,y,12,'#8d9b91',2)
# lens spectacles
circle(227,477,24,'#d1d8bd',3);circle(288,477,24,'#d1d8bd',3)
path('M251 476q7 -9 13 0M203 472l-11 -6M312 472l14 -6',width=3)
path('M215 479l19 -3M280 476l17 4',stroke='#344b4b',width=5)
path('M211 465l8 -8M273 465l8 -8',stroke='#f7e9c8',width=3)
rect(227,519,64,15,5,'#705e51',2)
for x in (238,250,262,274):path(f'M{x} 521v10',stroke='#e6c59b',width=3)
# granny hand grips child (arm forward)
limb('M192 596L170 675L226 702','#bc8065',20);circle(171,675,12,'#b7b097')
limb('M324 595L361 654L418 641','#bc8065',20);circle(361,654,12,'#b7b097')
# teen leaning away, narrow black chassis
add('<g transform="rotate(11 749 654)">')
limb('M727 723L740 798L703 866','#52656a',24)
limb('M788 726L810 800L819 870','#52656a',24)
rect(667,855,75,31,8,'#33474e');rect(796,859,68,32,8,'#33474e')
path('M690 577L788 562L821 724Q761 747 706 725Z','url(#dark)',width=4)
path('M707 583l33 62l-10 83M773 576l-33 69',stroke='#809a93',width=3)
# diagonal enamel lightning badge
path('M770 652l-18 26h12l-7 21l28 -33h-14l11 -14Z','#d9b577',stroke='none')
rect(721,536,32,35,5,'#939f91')
rect(679,455,123,91,14,'url(#dark)',4)
# tuft of bent antennas
path('M718 455l-9 -28l-19 7M742 449l6 -34l15 4',stroke='#2b4449',width=6)
rect(693,478,95,32,6,'#1e343c',2)
path('M705 495h23M752 493h23',stroke='#d7cd98',width=4)
path('M699 477l32 9M750 483l33 -12',stroke='#7f9690',width=6)
path('M737 527l33 -3',stroke='#c4bda0',width=3)
# headphones
path('M680 494v-20q1 -38 61 -39q59 -1 64 33v27',stroke='#b67459',width=7)
rect(670,479,18,38,7,'#bd775b');rect(796,473,18,38,7,'#bd775b')
# tightly folded arms
limb('M699 599L692 653L782 623','#56696b',20)
limb('M793 594L810 637L728 656','#56696b',20)
circle(691,651,12,'#a8ae97');circle(808,636,12,'#a8ae97')
rect(768,613,29,20,6,'#9aa798',2);rect(716,647,32,20,6,'#9aa798',2)
add('</g>')
# mother's hand hovering on teen's shoulder, unreciprocated
rect(730,468,40,23,7,'url(#cream)',2)
for x in (738,747,756):path(f'M{x} 471v14',width=1.5)
# exuberant tiny child front and center, tilted head and mismatched limbs
limb('M456 758L437 828L405 872','#d0a168',21)
limb('M510 756L537 820L556 851','#d0a168',21)
rect(378,861,69,29,9,'url(#red)');rect(542,843,65,29,9,'url(#teal)')
rect(423,650,112,125,20,'#d6ac68',4)
rect(444,677,68,61,11,'#f0cc87',2)
circle(479,707,18,'#567c77',2)
path('M468 707h22M479 696v22',stroke='#e4d1a0',width=3)
for x,y in [(435,665),(522,665),(436,759),(522,759)]:bolt(x,y)
rect(460,625,35,27,5,'#7c938a')
add('<g transform="rotate(-12 478 589)">')
rect(420,546,116,89,19,'#dcb771',4)
rect(434,562,87,39,12,'#324c50',2)
circle(455,582,10,'#f7e2a2',0);circle(500,579,14,'#f7e2a2',0)
circle(502,577,5,'#324c50',0)
path('M456 612q23 27 42 -4Z','#3b5050',width=2)
path('M464 616l12 1l-1 8l-9 -2Z','#f3ddac',width=1)
path('M477 544v-24M451 519h53',stroke='#3b5050',width=3)
path('M477 519q-49 -29 -54 -8q19 17 54 8M478 519q29 -32 42 -18q-6 20 -42 18','#c57e61',width=2)
add('</g>')
# child's raised hand ruining the formal photo; bunny ears behind teen
limb('M532 670L584 634L584 565','#d6ac68',17);circle(584,633,11,'#95a798')
rect(566,540,34,31,8,'#d6ac68',2)
limb('M574 543L567 517','#d6ac68',8);limb('M587 542L591 513','#d6ac68',8)
path('M578 553l13 3',width=2)
limb('M424 674L397 717L366 701','#d6ac68',17);circle(397,718,11,'#95a798')
rect(345,685,31,28,9,'#d6ac68',2)
# granny fingers clasp the child's shoulder
rect(404,632,31,22,7,'url(#cream)',2)
for x in (412,420,428):path(f'M{x} 636v13',width=1.5)
# dad tries to make contact with his too-small offspring
limb('M520 394L556 486L533 543','#608b84',25);circle(556,486,16,'#c0b899')
rect(521,529,29,33,8,'url(#teal)',2)
for x in (528,535,542):path(f'M{x} 541v14',width=1.5)
# robot dog lying by their feet, looking up
path('M639 856q-23 -21 -33 4q-3 17 20 17',stroke='#485e5d',width=9)
rect(626,835,100,44,20,'#83988b',3)
rect(638,868,34,15,6,'#d6be94',2);rect(696,866,31,16,6,'#d6be94',2)
add('<g transform="rotate(-15 723 837)">')
rect(693,803,66,53,12,'url(#cream)',3)
path('M694 809l-17 10l4 37l14 -8Z','#697f77',width=2)
path('M748 804l18 14l-4 30l-14 -8Z','#697f77',width=2)
circle(713,823,5,'#30484c',1);circle(741,822,5,'#30484c',1)
path('M720 836h13l-6 7Z','#30484c',width=2)
add('</g>')
# subtle brushed-metal scuffs and photographic finish
path('M365 394v30M336 261v24M587 392l-8 63M200 543h12M444 748h14M733 701l6 12',stroke='#fff1cf',width=2)
add('<rect x="40" y="40" width="920" height="920" fill="url(#paper)" pointer-events="none"/>')
add('<rect x="49" y="49" width="902" height="902" rx="2" fill="none" stroke="#f1e2bd" stroke-opacity=".5" stroke-width="2"/>')
add('</svg>')
Path('output/family-portrait.svg').write_text('\n'.join(s))
