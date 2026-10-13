from pathlib import Path
Path('output').mkdir(exist_ok=True)
s = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1400" viewBox="0 0 1200 1400">
<defs>
 <radialGradient id="bg"><stop stop-color="#f3d9aa"/><stop offset="1" stop-color="#bf997d"/></radialGradient>
 <linearGradient id="metal" x2=".85" y2="1"><stop stop-color="#bbd0c0"/><stop offset=".48" stop-color="#82a99d"/><stop offset="1" stop-color="#58877e"/></linearGradient>
 <linearGradient id="coral" x2=".9" y2="1"><stop stop-color="#f5b399"/><stop offset=".6" stop-color="#d7806c"/><stop offset="1" stop-color="#b85951"/></linearGradient>
 <linearGradient id="gold" x2="1" y2="1"><stop stop-color="#edd89c"/><stop offset="1" stop-color="#b99956"/></linearGradient>
 <linearGradient id="plum" x2="1" y2=".7"><stop stop-color="#b1a7bd"/><stop offset="1" stop-color="#79758f"/></linearGradient>
 <pattern id="paper" width="13" height="13" patternUnits="userSpaceOnUse"><circle cx="3" cy="5" r=".6" fill="#493e37" opacity=".13"/><circle cx="10" cy="11" r=".5" fill="#fff8dc" opacity=".28"/></pattern>
 <pattern id="wall" width="96" height="108" patternUnits="userSpaceOnUse"><path d="M48 24v22m-11-11h22M0 78v12m-6-6h12M96 78v12m-6-6h12" stroke="#725e51" stroke-width="1" opacity=".16"/><circle cx="48" cy="89" r="2" fill="#725e51" opacity=".12"/></pattern>
 <filter id="shadow" x="-30%" y="-30%" width="160%" height="180%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<!-- The little rented portrait studio -->
<rect width="1200" height="1400" fill="#263f3e"/>
<rect x="26" y="26" width="1148" height="1348" rx="9" fill="#d7bd98"/>
<rect x="43" y="43" width="1114" height="1314" rx="5" fill="url(#bg)" stroke="#816d57" stroke-width="2"/>
<path d="M117 1147V492C117 32 1083 32 1083 492V1147Z" fill="#dfc5a1" stroke="#ad8970" stroke-width="2"/>
<path d="M134 1147V492C134 59 1066 59 1066 492V1147Z" fill="url(#wall)"/>
<path d="M44 1067Q600 1024 1156 1067V1356H44Z" fill="#b99079"/>
<path d="M44 1067Q600 1024 1156 1067" fill="none" stroke="#8b7262" stroke-width="3"/>
<path d="M44 1163Q598 1094 1156 1163M44 1300Q598 1177 1156 1300" fill="none" stroke="#a4806b" stroke-width="2"/>
<ellipse cx="597" cy="1184" rx="477" ry="100" fill="#84796a" opacity=".3"/>
<ellipse cx="597" cy="1172" rx="458" ry="87" fill="#d3af86" stroke="#8b7360" stroke-width="3"/>
<ellipse cx="597" cy="1172" rx="437" ry="72" fill="none" stroke="#a08264" stroke-width="2" stroke-dasharray="5 9"/>
<ellipse cx="602" cy="1159" rx="388" ry="43" fill="#374c47" opacity=".2" filter="url(#shadow)"/>
<!-- Tall, painfully formal father: antenna tilted by the occasion -->
<g stroke="#293f3c" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="M422 280V230l-25-20" fill="none"/><circle cx="394" cy="207" r="11" fill="#d58265"/>
<!-- father legs -->
<path d="M391 793l-13 301M472 793l20 301" stroke="#344f49" stroke-width="49"/>
<path d="M391 806l-10 268M471 806l18 268" stroke="#90ad9c" stroke-width="32"/>
<circle cx="384" cy="955" r="24" fill="#e1cb95"/><circle cx="481" cy="955" r="24" fill="#e1cb95"/>
<path d="M376 945l15 20m84-20 14 20" stroke-width="3"/>
<path d="M350 1091h45l9 51q-28 15-92 5v-17q2-25 38-39Z" fill="#41645d"/>
<path d="M478 1091h34q39 13 42  forty" fill="none" stroke="none"/>
<path d="M473 1091h36q41 11 47 41v17h-86Z" fill="#41645d"/>
<path d="M313 1135h89m70 0h80" stroke="#b1c4ac" stroke-width="3"/>
<!-- torso and jacket -->
<rect x="342" y="507" width="177" height="308" rx="37" fill="url(#metal)"/>
<path d="M351 529l71 95-28 173h-42m158-268-68 95 30 173h39" fill="#779b8c" stroke-width="3"/>
<path d="M397 512h64l-28 128Z" fill="#e7d9b7" stroke-width="3"/>
<path d="m414 534 26-4 9 23-15 17 19 106-21 27-23-25 13-108-14-18Z" fill="#c07755" stroke-width="3"/>
<path d="m412 603 29 17m-33 14 37 21" stroke="#e0ae75" stroke-width="5"/>
<rect x="468" y="640" width="33" height="50" rx="3" fill="#486f65" stroke-width="3"/>
<path d="M478 649v29m10-29v29" stroke="#ddcd9f" stroke-width="3"/>
<circle cx="431" cy="751" r="6" fill="#e6cf97"/>
<!-- stiff elbow and hand on grandpa -->
<circle cx="338" cy="549" r="28" fill="#d9c69b"/>
<path d="m329 569-44 76-32-4" fill="none" stroke="#344e47" stroke-width="29"/>
<path d="m329 569-44 76-32-4" fill="none" stroke="#87a998" stroke-width="18"/>
<circle cx="285" cy="643" r="18" fill="#d9c69b"/>
<!-- arm almost but not quite touching partner -->
<path d="m522 550 70 35 29 68" fill="none" stroke="#2a413d" stroke-width="32"/>
<path d="m522 550 70 35 29 68" fill="none" stroke="#86a999" stroke-width="21"/>
<circle cx="589" cy="586" r="20" fill="#d9c69b"/>
<!-- neck -->
<path d="M405 475h53v39h-53Z" fill="#527b70"/>
<path d="M410 489h43m-43 11h43" stroke="#b9c8ae" stroke-width="3"/>
<!-- box head slightly crooked -->
<g transform="rotate(-4 430 390)">
<rect x="320" y="339" width="24" height="81" rx="9" fill="#ad9e72"/><rect x="516" y="339" width="24" height="81" rx="9" fill="#ad9e72"/>
<rect x="338" y="277" width="182" height="205" rx="24" fill="url(#metal)"/>
<path d="M351 312v-12q0-10 13-10h115" fill="none" stroke="#d7e0bd" stroke-width="4"/>
<rect x="359" y="341" width="141" height="64" rx="13" fill="#304e47"/>
<circle cx="393" cy="372" r="17" fill="#e5d499"/><circle cx="466" cy="372" r="17" fill="#e5d499"/>
<circle cx="396" cy="373" r="6" fill="#273d39" stroke="none"/><circle cx="469" cy="373" r="6" fill="#273d39" stroke="none"/>
<path d="m369 329 35-7m46 0 35 10" fill="none"/>
<rect x="388" y="436" width="87" height="17" rx="3" fill="#e7d6ac" stroke-width="3"/>
<path d="M405 438v13m18-13v13m18-13v13m17-13v13" stroke-width="2"/>
<circle cx="354" cy="461" r="4" fill="#e5d5ac" stroke-width="2"/><circle cx="503" cy="461" r="4" fill="#e5d5ac" stroke-width="2"/>
</g>
</g>
<!-- Mother, trying to physically hold this photograph together -->
<g stroke="#493f3b" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
<path d="m657 790-15 295m94-295 7 295" fill="none" stroke="#483e3b" stroke-width="38"/>
<path d="m657 790-15 295m94-295 7 295" fill="none" stroke="#c97c65" stroke-width="25"/>
<circle cx="649" cy="966" r="20" fill="#efd09a"/><circle cx="741" cy="966" r="20" fill="#efd09a"/>
<path d="M622 1079h39v64h-81q-4-35 42-64Zm104 0h35q42 27 40 64h-77Z" fill="#a9554d"/>
<path d="M584 1132h74m71 0h67" stroke="#e7b18b" stroke-width="3"/>
<path d="M652 525q-43 6-49 67l-16 207q101 42 204-2l-30-204q-9-65-47-68Z" fill="url(#coral)"/>
<path d="M611 773q85 29 172-1m-172 14q85 29 172-1" fill="none" stroke="#f0bf93" stroke-width="3"/>
<path d="M671 501v39q23 17 45-2v-43" fill="#a65f52"/>
<!-- maternal reaching arms -->
<circle cx="610" cy="575" r="26" fill="#e1be88"/>
<path d="m599 593-43 104 48 135" fill="none" stroke="#493f3b" stroke-width="31"/>
<path d="m599 593-43 104 48 135" fill="none" stroke="#df997c" stroke-width="21"/>
<circle cx="557" cy="698" r="21" fill="#dfbd87"/>
<circle cx="765" cy="575" r="25" fill="#e1be88"/>
<path d="m779 590 56 106-91 132" fill="none" stroke="#493f3b" stroke-width="31"/>
<path d="m779 590 56 106-91 132" fill="none" stroke="#db9276" stroke-width="21"/>
<circle cx="832" cy="697" r="22" fill="#dfbd87"/>
<!-- brooch and panel -->
<path d="m620 540 74 58 65-57" fill="none" stroke="#f0c697" stroke-width="9"/>
<circle cx="693" cy="600" r="16" fill="#456f66"/><path d="m693 590 7 10-7 10-7-10Z" fill="#e2d7a8" stroke="none"/>
<rect x="638" y="645" width="98" height="88" rx="22" fill="#b76c5d" stroke-width="3"/>
<path d="M656 669h60m-60 13h60m-60 13h60m-60 13h37" stroke="#edbd92" stroke-width="4"/>
<!-- head, gentle smile and overalert eyes -->
<g transform="rotate(7 695 439)">
<path d="M625 411q-27-91 55-108 69-6 89 72" fill="#8b5550"/>
<path d="M640 337q45-42 91 10m-103 9q52-42 111 8" fill="none" stroke="#cc8e72" stroke-width="5"/>
<circle cx="613" cy="432" r="19" fill="#cdaa75"/><circle cx="778" cy="432" r="19" fill="#cdaa75"/>
<rect x="619" y="359" width="155" height="157" rx="58" fill="url(#coral)"/>
<path d="M635 388q54-26 120 0" fill="none" stroke="#f7cbae" stroke-width="4"/>
<ellipse cx="657" cy="428" rx="20" ry="25" fill="#f6deb1"/><ellipse cx="730" cy="428" rx="20" ry="25" fill="#f6deb1"/>
<ellipse cx="659" cy="431" rx="7" ry="11" fill="#394944" stroke="none"/><ellipse cx="731" cy="431" rx="7" ry="11" fill="#394944" stroke="none"/>
<path d="m641 398 24-7m55-1 23 8" fill="none" stroke-width="4"/>
<path d="M674 477q25 17 46-1" fill="none" stroke-width="4"/>
<circle cx="642" cy="463" r="10" fill="#b7655a" stroke="none"/><circle cx="747" cy="463" r="10" fill="#b7655a" stroke="none"/>
<path d="M785 449v21m-181-21v21" stroke="#e7ca88" stroke-width="7"/>
</g>
</g>
<!-- The slouching teenager, pointedly looking out of the frame -->
<g stroke="#363c43" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="m899 854 53 119-60 144m76-246 32 112-33 145" fill="none" stroke="#363c43" stroke-width="34"/>
<path d="m899 854 53 119-60 144m76-246 32 112-33 145" fill="none" stroke="#868298" stroke-width="23"/>
<circle cx="952" cy="974" r="20" fill="#b0a2ae"/><circle cx="999" cy="982" r="20" fill="#b0a2ae"/>
<path d="m875 1107 29 11 3 35q-59 20-85 1 4-27 53-47Zm77 6 27 5 8 29q47 3 47 28h-92Z" fill="#464c57"/>
<path d="m826 1156 76-2m45 12h82" stroke="#e3cdaa" stroke-width="6"/>
<g transform="rotate(12 930 745)">
<rect x="866" y="656" width="137" height="227" rx="28" fill="url(#plum)"/>
<path d="M881 669v200m103-191v187" stroke="#c3b3bf" stroke-width="3"/>
<path d="m915 698 38 2-17 35 29-2-45 64 10-47-27 1Z" fill="#e6b96f" stroke-width="3"/>
<path d="M889 818h91v36h-91Z" fill="#68697d" stroke-width="3"/>
<circle cx="858" cy="687" r="23" fill="#b09d9e"/>
<path d="m850 703-17 83 107 14" fill="none" stroke="#363c43" stroke-width="29"/>
<path d="m850 703-17 83 107 14" fill="none" stroke="#a399ae" stroke-width="18"/>
<circle cx="834" cy="784" r="17" fill="#c0a69f"/>
<path d="m1008 692 25 88-81 27" fill="none" stroke="#363c43" stroke-width="29"/>
<path d="m1008 692 25 88-81 27" fill="none" stroke="#a399ae" stroke-width="18"/>
<circle cx="1033" cy="780" r="17" fill="#c0a69f"/>
<path d="m925 803 19-8 14 4m-24 12 23-5m-26 12 22-4" fill="none" stroke="#d4bbaa" stroke-width="7"/>
<rect x="909" y="624" width="47" height="34" fill="#696b7c"/>
<rect x="857" y="502" width="151" height="139" rx="29" fill="url(#plum)"/>
<!-- uneven metal fringe -->
<path d="m858 544 9-47 31-8 6-25 21 22 31-20 2 23 35-9-6 21 27 9-20 50-25-26-10 21-31-26-15 18-23-13Z" fill="#434b55"/>
<path d="M875 567h47m26 0h42" stroke="#e5d6b3" stroke-width="16"/>
<path d="M912 565v11m67-11v11" stroke="#303e42" stroke-width="7"/>
<path d="m875 558 46 7m28-2 39-12" stroke-width="6"/>
<path d="m930 609 35-5" stroke-width="4"/>
<path d="M848 578v-43q0-57 72-63 75-7 91 60v46" fill="none" stroke="#323f44" stroke-width="10"/>
<rect x="839" y="549" width="24" height="51" rx="10" fill="#ddaa67"/><rect x="1000" y="549" width="24" height="51" rx="10" fill="#ddaa67"/>
<path d="M1010 600q22 90-45 93" fill="none" stroke-width="3"/>
</g>
</g>
<!-- Grandpa on his stool, a dignified obsolete model -->
<g stroke="#454339" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
<path d="m174 986-22 163m125-163 24 163" stroke="#69594a" stroke-width="13"/>
<rect x="143" y="959" width="180" height="39" rx="14" fill="#725c4f"/>
<path d="M191 944v115l-22 53m91-168 17 101-9 70" fill="none" stroke="#454339" stroke-width="34"/>
<path d="M191 944v115l-22 53m91-168 17 101-9 70" fill="none" stroke="#c1a76e" stroke-width="23"/>
<circle cx="192" cy="1052" r="20" fill="#dbc58a"/><circle cx="277" cy="1045" r="20" fill="#dbc58a"/>
<path d="M154 1100h30v42h-75q0-24 45-42Zm99 3h31l29 23v21h-68Z" fill="#776e50"/>
<rect x="155" y="779" width="156" height="184" rx="36" fill="url(#gold)"/>
<path d="M170 801q66 44 122-4l-12 132H180Z" fill="#807f64" stroke-width="3"/>
<path d="m206 820 21 17-18 20-14-37m32 17 24-22 11 35-35-13" fill="#965d4a" stroke-width="3"/>
<circle cx="232" cy="881" r="6" fill="#e4cf99"/><circle cx="232" cy="907" r="6" fill="#e4cf99"/>
<path d="m271 851 10 44q-4 38-27 31" fill="none" stroke="#debc78" stroke-width="3"/>
<path d="M168 817l-35 78 40 33m129-110 25 69 28 6" fill="none" stroke="#454339" stroke-width="27"/>
<path d="M168 817l-35 78 40 33m129-110 25 69 28 6" fill="none" stroke="#cfb77c" stroke-width="17"/>
<circle cx="135" cy="892" r="17" fill="#ddc389"/>
<!-- cane -->
<path d="M349 1146V905q0-24 18-24 21 0 21 24" fill="none" stroke="#594d40" stroke-width="12"/>
<path d="M344 1113h11" stroke="#d9bd7e" stroke-width="7"/>
<path d="m349 888 17 1m-19 10 20 1m-20 9h15" stroke="#e4c88b" stroke-width="8"/>
<path d="M161 919q17-6 25 3l9 15-13 7-17-9" fill="#d8c085" stroke-width="3"/>
<!-- head tipped toward his son -->
<g transform="rotate(-9 232 713)">
<path d="M201 778v23h56v-30" fill="#948452"/>
<path d="M224 626v-25m-25-8q23-23 48-3" fill="none" stroke-width="4"/>
<ellipse cx="226" cy="594" rx="27" ry="8" fill="#c8b27b" stroke-width="3"/>
<rect x="133" y="690" width="27" height="48" rx="7" fill="#8b8462"/><rect x="300" y="690" width="26" height="48" rx="7" fill="#8b8462"/>
<rect x="152" y="637" width="151" height="148" rx="51" fill="url(#gold)"/>
<path d="M171 666q49-26 106 0" fill="none" stroke="#f1dfab" stroke-width="4"/>
<path d="M176 707q15-17 30 0m45 0q15-17 29 0" fill="none" stroke-width="5"/>
<circle cx="263" cy="706" r="26" fill="none" stroke="#6e7058" stroke-width="3"/>
<path d="M289 710q21 69-3 130" fill="none" stroke="#756b4a" stroke-width="2"/>
<path d="m180 686 23-7m46 0 26 6" stroke-width="4"/>
<path d="M205 741q11-12 23-3 13-9 27 1l13 11q-21 8-40-4-17 15-38 7Z" fill="#f0e1b6" stroke-width="3"/>
<path d="M217 762h22" stroke-width="3"/>
</g>
<!-- Dad's overly firm shoulder grip -->
<path d="M276 652q-10-16-28-15l-22 7 1 23m13-27-1 25m12-25 1 25m10-22 2 17" fill="#91ae99" stroke-width="4"/>
</g>
<!-- Youngest: cannot stay still, wearing a wonky party bow -->
<g stroke="#344845" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
<path d="m560 1037-24 67-53 22m137-92 29 68 4  forty" stroke="none" fill="none"/>
<path d="m560 1037-24 67-53 22m137-92 29 68 4 31" fill="none" stroke="#344845" stroke-width="28"/>
<path d="m560 1037-24 67-53 22m137-92 29 68 4 31" fill="none" stroke="#d0ae67" stroke-width="18"/>
<circle cx="536" cy="1101" r="17" fill="#e2c681"/><circle cx="648" cy="1102" r="17" fill="#e2c681"/>
<path d="m470 1114 29 12-6 27-61-19q0-24 38-20Zm167 16h32q31 3 40 27h-76Z" fill="#ce9554"/>
<g transform="rotate(-10 587 967)">
<rect x="529" y="937" width="119" height="121" rx="27" fill="url(#gold)"/>
<rect x="552" y="965" width="74" height="61" rx="13" fill="#8f9e7d" stroke-width="3"/>
<path d="M568 990h13m-6-7v14" stroke="#e6d6a1" stroke-width="4"/>
<circle cx="607" cy="989" r="6" fill="#c27357" stroke-width="2"/><circle cx="594" cy="1009" r="4" fill="#ecdc9c" stroke-width="2"/>
<path d="m530 959-40-19-32-68m189 88 51-30 15-54" fill="none" stroke="#344845" stroke-width="25"/>
<path d="m530 959-40-19-32-68m189 88 51-30 15-54" fill="none" stroke="#d6b874" stroke-width="15"/>
<circle cx="490" cy="940" r="15" fill="#e9cf91"/><circle cx="696" cy="930" r="15" fill="#e9cf91"/>
<!-- waving pincers -->
<path d="m456 880-17-14 1-22m19 28 13-20-6-17m245 44-12-21 7-21m9 32 17-14-2-22" fill="none" stroke="#344845" stroke-width="11"/>
<path d="m456 880-17-14 1-22m19 28 13-20-6-17m245 44-12-21 7-21m9 32 17-14-2-22" fill="none" stroke="#d9bd7d" stroke-width="6"/>
<path d="M567 925v15h42v-18" fill="#93916a"/>
<rect x="515" y="812" width="142" height="125" rx="26" fill="#dfb965"/>
<path d="M527 839v-7q0-9 12-9h86" fill="none" stroke="#f5dda0" stroke-width="4"/>
<circle cx="551" cy="868" r="21" fill="#f3dfa7"/><circle cx="620" cy="862" r="25" fill="#f3dfa7"/>
<circle cx="555" cy="867" r="8" fill="#324b45" stroke="none"/><circle cx="623" cy="862" r="10" fill="#324b45" stroke="none"/>
<path d="M561 898q26 36 49-2Z" fill="#364d45" stroke-width="3"/>
<path d="m573 902 1 8 11 1 1-10" fill="#f5e5b5" stroke="none"/>
<path d="m570 811-9-26m1 1-23-16-7 27 30-11 22-21 13 27Z" fill="#c36d59" stroke-width="3"/>
<circle cx="562" cy="786" r="6" fill="#ebc184" stroke-width="2"/>
</g>
<!-- mother holding the little one's shoulders, too late -->
<path d="M591 834q-6-17-18-17l-18 3m19 2 2 17m7-15 2 15" fill="none" stroke="#483f39" stroke-width="12"/>
<path d="M591 834q-6-17-18-17l-18 3m19 2 2 17m7-15 2 15" fill="none" stroke="#e4a789" stroke-width="7"/>
<path d="m745 826-13 7-10 18m8-16-10 5" fill="none" stroke="#483f39" stroke-width="13"/>
<path d="m745 826-13 7-10 18m8-16-10 5" fill="none" stroke="#e4a789" stroke-width="8"/>
</g>
<!-- Family dog: the only one facing the camera without reservations -->
<g stroke="#344843" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M876 1113q50-92 68-54 12 24-18 28" fill="none" stroke-width="10"/>
<path d="M876 1113q50-92 68-54 12 24-18 28" fill="none" stroke="#afbc9b" stroke-width="5"/>
<rect x="780" y="1092" width="121" height=" seventy" fill="none" stroke="none"/>
<rect x="784" y="1096" width="109" height="65" rx="26" fill="#8da28a"/>
<path d="M800 1143v31h-26m99-31v31h25" fill="none" stroke-width="17"/>
<path d="M800 1143v31h-26m99-31v31h25" fill="none" stroke="#afbc98" stroke-width="10"/>
<path d="M802 1106q18-15 40-7" stroke="#c37555" stroke-width="11" fill="none"/>
<circle cx="824" cy="1110" r="7" fill="#e6cb84" stroke-width="2"/>
<g transform="rotate(-8 795 1080)">
<path d="m755 1061-15-47 33 12m38 2 27-17 8 55" fill="#648477"/>
<rect x="754" y="1041" width="84" height="69" rx="19" fill="#b4c29e"/>
<circle cx="776" cy="1069" r="9" fill="#e8d9a7"/><circle cx="816" cy="1069" r="9" fill="#e8d9a7"/>
<circle cx="778" cy="1068" r="3" fill="#344843" stroke="none"/><circle cx="818" cy="1068" r="3" fill="#344843" stroke="none"/>
<path d="m786 1085 12 10 11-10Z" fill="#344843"/>
<path d="M795 1097v19q12 11 18-1v-17" fill="#d58a74" stroke-width="3"/>
</g>
</g>
<!-- Small loose hardware; family resemblance -->
<g fill="#d9c89c" stroke="#3a4940" stroke-width="2">
<circle cx="363" cy="533" r="4"/><circle cx="495" cy="533" r="4"/><circle cx="363" cy="783" r="4"/><circle cx="495" cy="783" r="4"/>
<circle cx="619" cy="752" r="4"/><circle cx="761" cy="752" r="4"/>
<circle cx="175" cy="945" r="4"/><circle cx="290" cy="945" r="4"/>
</g>
<rect x="43" y="43" width="1114" height="1314" fill="url(#paper)" pointer-events="none"/>
<!-- Double-rule archival mount -->
<rect x="62" y="62" width="1076" height="1276" rx="3" fill="none" stroke="#f4dfb9" stroke-width="2"/>
<path d="M79 121v-42h42m958 0h42v42M79 1279v42h42m958 0h42v-42" fill="none" stroke="#7e705a" stroke-width="2"/>
</svg>'''
# Discard hidden construction guides, keeping the delivered SVG strictly valid.
s = '\n'.join(line for line in s.splitlines() if 'forty' not in line and 'seventy' not in line)
Path('output/awkward-family.svg').write_text(s)
