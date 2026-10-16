from pathlib import Path
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1120" viewBox="0 0 1000 1120">
<defs>
 <linearGradient id="night" x2="0" y2="1"><stop stop-color="#122d3b"/><stop offset="1" stop-color="#27515a"/></linearGradient>
 <linearGradient id="skin" x2="0.8" y2="1"><stop stop-color="#ffad83"/><stop offset="1" stop-color="#df6259"/></linearGradient>
 <linearGradient id="wood" x2="0" y2="1"><stop stop-color="#dd955f"/><stop offset="1" stop-color="#b46248"/></linearGradient>
 <radialGradient id="glow"><stop stop-color="#ffd686" stop-opacity=".3"/><stop offset="1" stop-color="#ffd686" stop-opacity="0"/></radialGradient>
 <pattern id="wave" width="90" height="45" patternUnits="userSpaceOnUse"><path d="M-45 45a45 45 0 0 1 90 0m-30 0a30 30 0 0 0-60 0m15 0a15 15 0 0 1 30 0M45 45a45 45 0 0 1 90 0m-30 0a30 30 0 0 0-60 0m15 0a15 15 0 0 1 30 0" fill="none" stroke="#81b1a5" stroke-opacity=".2" stroke-width="2"/></pattern>
</defs>
<!-- A little midnight eatery, somewhere beneath the waves. -->
<rect width="1000" height="1120" fill="#f5e8c9"/>
<rect x="22" y="22" width="956" height="1076" rx="24" fill="url(#night)"/>
<rect x="22" y="790" width="956" height="308" rx="24" fill="url(#wave)"/>
<circle cx="815" cy="400" r="215" fill="url(#glow)"/>
<g fill="none" stroke="#8db8ad" opacity=".35" stroke-width="2"><circle cx="102" cy="440" r="12"/><circle cx="81" cy="393" r="6"/><circle cx="921" cy="650" r="10"/><circle cx="906" cy="611" r="5"/><path d="M62 855q45-55 10-110m861 103q-36-36-5-96"/></g>
<text x="500" y="84" text-anchor="middle" fill="#e9d8b6" font-family="sans-serif" font-size="13" letter-spacing="5">OPEN LATE • EIGHT ARMS • ONE PERFECT BOWL</text>
<!-- roof -->
<path d="M112 223L162 143Q500 104 838 143L888 223Z" fill="#e58160" stroke="#102d36" stroke-width="8" stroke-linejoin="round"/>
<path d="M159 157Q500 120 841 157M141 184Q500 147 859 184" fill="none" stroke="#a44740" stroke-width="5"/>
<rect x="104" y="216" width="792" height="24" rx="8" fill="#f2b179" stroke="#102d36" stroke-width="7"/>
<!-- sign -->
<rect x="280" y="121" width="440" height="98" rx="13" fill="#f8e6b9" stroke="#173640" stroke-width="7"/>
<rect x="292" y="132" width="416" height="76" rx="6" fill="none" stroke="#cf7854" stroke-width="2"/>
<text x="500" y="176" text-anchor="middle" fill="#21414a" font-family="Georgia,serif" font-size="40" font-weight="bold" letter-spacing="3">OCTO RAMEN</text>
<text x="500" y="197" text-anchor="middle" fill="#ad5343" font-family="sans-serif" font-size="11" letter-spacing="5">THE MIDNIGHT NOODLE BAR</text>
<!-- frame and back wall -->
<path d="M158 244h684v516H158z" fill="#16323a"/>
<path d="M175 353h650v369H175z" fill="#28484a"/>
<g stroke="#41615c" stroke-width="2" opacity=".6"><path d="M175 427h650M175 502h650M175 577h650M175 652h650M250 353v369M400 353v369M550 353v369M700 353v369"/></g>
<g fill="url(#wood)" stroke="#15323b" stroke-width="7"><rect x="139" y="240" width="34" height="704" rx="5"/><rect x="827" y="240" width="34" height="704" rx="5"/></g>
<!-- split curtains -->
<g fill="#43857b" stroke="#173b40" stroke-width="5"><path d="M177 240h156v109q-76 35-156 0z"/><path d="M339 240h158v109q-79 35-158 0z"/><path d="M503 240h158v109q-79 35-158 0z"/><path d="M667 240h156v109q-76 35-156 0z"/></g>
<g fill="none" stroke="#e8d9ac" stroke-width="3" opacity=".8"><circle cx="253" cy="301" r="26"/><path d="M235 303q18-35 36 0m-36 0q-7 22 3 17t11-5q4 19 11 0t12 5"/><path d="M382 289h72m-64 12h56m-48 12h40M547 289h72m-64 12h56m-48 12h40"/><circle cx="745" cy="301" r="26"/><path d="M727 302h36l-6 16h-24zM731 289l27-7"/></g>
<!-- lantern -->
<path d="M785 241v132" stroke="#f4d4a0" stroke-width="4"/>
<rect x="755" y="369" width="60" height="12" rx="5" fill="#182f37"/>
<rect x="738" y="380" width="94" height="132" rx="38" fill="#ffcd80" stroke="#17323b" stroke-width="5"/>
<path d="M748 402h74m-83 24h92m-91 25h91m-83 25h77m-63-92q-15 62 0 120m46-120q15 62 0 120" fill="none" stroke="#de9560" stroke-width="2"/>
<rect x="757" y="510" width="56" height="12" rx="4" fill="#17323b"/>
<text x="785" y="446" text-anchor="middle" font-family="Georgia,serif" font-weight="bold" font-size="23" fill="#a7493e">夜</text>
<text x="785" y="471" text-anchor="middle" font-family="sans-serif" font-size="10" letter-spacing="2" fill="#a7493e">RAMEN</text>
<!-- menu -->
<g transform="rotate(-5 244 485)"><rect x="194" y="390" width="107" height="185" rx="3" fill="#efdcb0" stroke="#152f36" stroke-width="4"/><text x="247" y="421" text-anchor="middle" font-family="Georgia,serif" font-weight="bold" font-size="18" fill="#a95343">TONIGHT</text><path d="M210 433h75" stroke="#b46b4e"/><g font-family="sans-serif" fill="#29474a" font-size="12"><text x="211" y="458">MISO</text><text x="211" y="482">SHIO</text><text x="211" y="506">SHOYU</text></g><circle cx="246" cy="543" r="16" fill="#bf5c49"/><text x="246" y="547" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#ffe8bd">★</text></g>
<!-- eight busy arms -->
<g fill="none" stroke="#17343b" stroke-width="46" stroke-linecap="round" stroke-linejoin="round">
<path id="a" d="M415 586C356 612 327 564 325 514S292 472 279 493"/>
<path id="b" d="M409 627C331 666 304 627 260 641S223 687 252 686"/>
<path id="c" d="M441 660C364 672 392 754 334 768S272 742 300 732"/>
<path id="d" d="M474 671C442 732 481 803 438 824S383 803 404 791"/>
<path id="e" d="M532 674C546 722 518 784 560 812S616 797 596 781"/>
<path id="f" d="M566 651C616 658 625 738 675 734S700 697 681 701"/>
<path id="g" d="M592 612C650 653 687 649 712 612S748 591 750 611"/>
<path id="h" d="M590 576C642 578 658 537 652 493S675 450 692 464"/>
</g>
<g fill="none" stroke="url(#skin)" stroke-width="34" stroke-linecap="round"><use href="#a"/><use href="#b"/><use href="#c"/><use href="#d"/><use href="#e"/><use href="#f"/><use href="#g"/><use href="#h"/></g>
'''
# suckers along the curling limbs
for x,y,r in [(324,542,5),(329,560,5),(339,577,5),(355,588,5),(275,643,5),(256,651,5),(241,665,4),(390,698,5),(382,719,5),(369,742,5),(349,754,4),(452,743,5),(451,765,5),(446,788,5),(433,808,4),(541,741,5),(542,763,5),(549,786,5),(568,802,4),(635,698,5),(648,716,5),(667,723,4),(681,642,5),(698,631,5),(709,613,4),(646,542,5),(650,522,5),(648,502,4)]:
 svg+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd0a1"/>'
svg+='''
<!-- body -->
<path d="M391 574c-8-37-3-106 28-130 36-29 114-30 150 0 33 28 39 91 24 133l-10 79q-86 63-174-1z" fill="url(#skin)" stroke="#17343b" stroke-width="6"/>
<ellipse cx="418" cy="539" rx="18" ry="10" fill="#d85755" opacity=".6"/><ellipse cx="570" cy="539" rx="18" ry="10" fill="#d85755" opacity=".6"/>
<path d="M430 518q12-17 23 0m78 0q12-17 23 0" fill="none" stroke="#26353b" stroke-width="6" stroke-linecap="round"/>
<path d="M478 540q17 24 35 0" fill="#743d41" stroke="#26353b" stroke-width="4" stroke-linejoin="round"/>
<ellipse cx="470" cy="475" rx="22" ry="11" fill="#ffd2a4" opacity=".65" transform="rotate(-22 470 475)"/>
<!-- chef toque -->
<path d="M414 438l-7-41c-37-5-38-53-7-63 8-33 49-36 69-16 21-37 76-24 80 5 43-14 70 32 46 56-5 9-17 15-28 16l-3 43q-76 17-150 0z" fill="#fff0cf" stroke="#17343b" stroke-width="6"/>
<path d="M414 414q72 13 152 0m-130-18-5-28m39 30-2-45m36 45 5-37m29 36 7-27" fill="none" stroke="#d9c7a5" stroke-width="4" stroke-linecap="round"/>
<path d="M414 437q80 18 150 0" fill="none" stroke="#17343b" stroke-width="5"/>
<!-- apron and neckerchief -->
<path d="M429 571l-12 83q77 45 153 0l-12-83-22 10h-88z" fill="#f6e7c4" stroke="#17343b" stroke-width="5"/>
<path d="M421 566l68 22 76-22-24 37-51-12-46 12z" fill="#397b73" stroke="#17343b" stroke-width="4"/>
<path d="M490 588l-11 38 19-6 13-28" fill="#397b73" stroke="#17343b" stroke-width="4"/>
<!-- ladle in left arm -->
<path d="M287 487l-30-92" stroke="#15323a" stroke-width="12" stroke-linecap="round"/><path d="M287 487l-30-92" stroke="#d5ba8c" stroke-width="6" stroke-linecap="round"/>
<path d="M236 382q20-17 38-7l5 21q-21 22-38 4z" fill="#819e95" stroke="#17343b" stroke-width="4"/>
<!-- lifted noodles and chopsticks -->
<g fill="none" stroke="#f7d58d" stroke-width="4" stroke-linecap="round"><path d="M658 444c-10 32 19 32 8 64s15 43 0 69M669 441c-8 32 18 34 9 65s15 42 1 68M680 439c-8 32 15 35 8 65s14 41 4 65"/></g>
<path d="M630 452l114-31m-111 39 116-24" stroke="#172f36" stroke-width="8" stroke-linecap="round"/><path d="M630 452l114-31m-111 39 116-24" stroke="#e9bc77" stroke-width="4" stroke-linecap="round"/>
<!-- counter -->
<path d="M121 741h758v187H121z" fill="url(#wood)" stroke="#18343a" stroke-width="7"/>
<path d="M142 777h716v132H142z" fill="#b96b4c"/>
<path d="M160 784v115m169-115v115m170-115v115m170-115v115m170-115v115" stroke="#925239" stroke-width="4"/>
<path d="M112 716h776v36H112z" fill="#edb17c" stroke="#18343a" stroke-width="7" stroke-linejoin="round"/>
<path d="M129 728h740" stroke="#ffe0a4" stroke-width="3"/>
<rect x="393" y="790" width="214" height="88" rx="44" fill="#24484b" stroke="#e9bb80" stroke-width="3"/>
<text x="500" y="828" text-anchor="middle" font-family="Georgia,serif" font-size="25" fill="#f5dfb4">Made with</text><text x="500" y="855" text-anchor="middle" font-family="Georgia,serif" font-style="italic" font-size="23" fill="#f5dfb4">eightfold love.</text>
<!-- condiments -->
<rect x="202" y="656" width="34" height="58" rx="5" fill="#543d35" stroke="#19363b" stroke-width="4"/><rect x="207" y="645" width="24" height="14" rx="3" fill="#d95849" stroke="#19363b" stroke-width="3"/><rect x="208" y="676" width="22" height="23" rx="2" fill="#f1d9a5"/><circle cx="219" cy="687" r="6" fill="#bf5b45"/>
<path d="M757 656l-6-57m20 55 8-67m-12 68 1-73m12 73 15-58" stroke="#e5b778" stroke-width="6"/><path d="M744 646h48l-7 68h-34z" fill="#477c73" stroke="#17373b" stroke-width="4"/><path d="M752 657h32m-30 12h28" stroke="#94b49a" stroke-width="3"/>
<!-- hero bowl -->
<ellipse cx="502" cy="714" rx="133" ry="13" fill="#92583f" opacity=".45"/>
<path d="M380 644q15 68 95 76h54q78-12 96-76z" fill="#f7e5bb" stroke="#17343b" stroke-width="6"/>
<path d="M397 675q104 49 211 0" fill="none" stroke="#c75c48" stroke-width="10"/><path d="M418 700q83 26 169-1" fill="none" stroke="#c75c48" stroke-width="4"/>
<ellipse cx="502" cy="645" rx="123" ry="35" fill="#fbe8b8" stroke="#17343b" stroke-width="5"/>
<ellipse cx="502" cy="645" rx="109" ry="26" fill="#b9693c"/>
<g fill="none" stroke="#f4cf7f" stroke-width="4"><path d="M414 646q31-30 71-5t68-2 41 10M415 655q25-28 61-4t68-1 43 7M434 635q25-16 52 3t60-3M439 662q18-17 43-1t48 0"/></g>
<path d="M544 631l2-47 38 8-5 48z" fill="#284e42" stroke="#17383a" stroke-width="3"/><path d="M554 597l16 33m-17-15 20-5" stroke="#527357" stroke-width="3"/>
<ellipse cx="518" cy="630" rx="24" ry="17" transform="rotate(-25 518 630)" fill="#fff3d3" stroke="#d5b888" stroke-width="2"/><ellipse cx="521" cy="631" rx="12" ry="10" fill="#efa43b"/>
<g fill="#73aa65" stroke="#305f4c" stroke-width="2"><ellipse cx="465" cy="626" rx="9" ry="4" transform="rotate(25 465 626)"/><ellipse cx="477" cy="632" rx="9" ry="4" transform="rotate(-28 477 632)"/><ellipse cx="451" cy="633" rx="8" ry="4"/></g>
<g fill="none" stroke="#f7e3bc" stroke-width="4" stroke-linecap="round" opacity=".6"><path d="M453 604c-21-19 14-27 0-46M496 609c-17-19 15-25 9-43M594 608c-16-14 8-24 1-36"/></g>
<!-- little stools -->
<g stroke="#16353d" stroke-width="7" stroke-linejoin="round"><path d="M249 971l-13 65m81-65 13 65M681 971l-13 65m81-65 13 65" fill="none"/><path d="M242 1018h81m351 0h81" fill="none" stroke="#bc805a" stroke-width="5"/><ellipse cx="282" cy="966" rx="62" ry="20" fill="#b85d48"/><ellipse cx="282" cy="958" rx="62" ry="17" fill="#e79867"/><ellipse cx="714" cy="966" rx="62" ry="20" fill="#b85d48"/><ellipse cx="714" cy="958" rx="62" ry="17" fill="#e79867"/></g>
<text x="500" y="1063" text-anchor="middle" font-family="sans-serif" font-size="12" letter-spacing="4" fill="#ead7b1">PULL UP A STOOL. STAY FOR A BOWL.</text>
</svg>'''
Path('output/octo-ramen.svg').write_text(svg)
