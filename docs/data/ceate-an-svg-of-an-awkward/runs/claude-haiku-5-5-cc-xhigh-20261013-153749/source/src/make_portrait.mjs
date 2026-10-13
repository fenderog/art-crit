// Builds ./output/robot_family_portrait.svg: an awkward family portrait of robots.
// Each robot is drawn in its own local space (origin at its feet, y up is negative)
// and placed on a shared floor line. No text elements are used.
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, '..', 'output');
mkdirSync(outDir, { recursive: true });

const W = 1600;
const H = 1000;
const FLOOR = 820;
const INK = '#2b2622';
const outline = (w = 5) =>
  `stroke="${INK}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const OUT = outline(5);

// A limb is a thick round-capped stroke with a dark outline stroke underneath.
function limb(d, color, w = 26) {
  const cap = 'fill="none" stroke-linecap="round" stroke-linejoin="round"';
  return `<path d="${d}" ${cap} stroke="${INK}" stroke-width="${w + 10}"/>` +
    `<path d="${d}" ${cap} stroke="${color}" stroke-width="${w}"/>`;
}

const line = (d, color, w, opacity = 1) =>
  `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" opacity="${opacity}"/>`;

const shadow = (x, rx) =>
  `<ellipse cx="${x}" cy="${FLOOR + 8}" rx="${rx}" ry="15" fill="#3b2a1a" opacity="0.3"/>`;

// --- Background -----------------------------------------------------------

function background() {
  const planks = [850, 880, 910, 940, 970]
    .map((y) => line(`M0,${y} L${W},${y}`, '#9a6e44', 3, 0.45))
    .join('');
  const panels = [200, 400, 600, 800, 1000, 1200, 1400]
    .map((x) => line(`M${x},672 L${x},${FLOOR}`, '#b59d74', 4))
    .join('');

  return `
  <defs>
    <pattern id="wallDots" width="56" height="56" patternUnits="userSpaceOnUse">
      <circle cx="14" cy="14" r="4" fill="#d8c39b"/>
      <circle cx="42" cy="42" r="4" fill="#d8c39b"/>
    </pattern>
    <radialGradient id="lampGlow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff3c4" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#fff3c4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="0.5" cy="0.47" r="0.72">
      <stop offset="0.62" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.38"/>
    </radialGradient>
  </defs>

  <rect width="${W}" height="${H}" fill="#ead9b8"/>
  <rect width="${W}" height="${FLOOR}" fill="#efe2c6"/>
  <rect width="${W}" height="${FLOOR}" fill="url(#wallDots)" opacity="0.7"/>

  <!-- wainscoting and floor -->
  <rect y="660" width="${W}" height="160" fill="#c9b28a"/>
  <rect y="652" width="${W}" height="12" fill="#a8906a"/>
  ${panels}
  <rect y="${FLOOR}" width="${W}" height="${H - FLOOR}" fill="#b98b5e"/>
  ${planks}

  <!-- crooked framed picture -->
  <g transform="rotate(-4 1110 200)">
    <rect x="1000" y="120" width="220" height="150" fill="#6b4a2f" ${OUT}/>
    <rect x="1018" y="138" width="184" height="114" fill="#f6efdc"/>
    <circle cx="1098" cy="186" r="22" fill="#f0a04b"/>
    <path d="M1018,252 Q1080,196 1140,236 Q1170,212 1202,236 L1202,252 Z" fill="#7aa27a"/>
  </g>

  <!-- potted plant, left -->
  <g>
    ${[-40, -20, 0, 20, 40]
      .map((a, i) => `<ellipse cx="110" cy="628" rx="22" ry="80" fill="${i % 2 ? '#3f7a48' : '#4f8f52'}" ${outline(4)} transform="rotate(${a} 110 700)"/>`)
      .join('')}
    <path d="M60,700 L160,700 L146,${FLOOR + 2} L74,${FLOOR + 2} Z" fill="#b65c3a" ${OUT}/>
  </g>

  <!-- floor lamp, far right, leaning toward the teen -->
  <circle cx="1500" cy="250" r="230" fill="url(#lampGlow)"/>
  <rect x="1494" y="300" width="12" height="520" fill="#5d4a3a"/>
  <ellipse cx="1500" cy="${FLOOR}" rx="50" ry="12" fill="#5d4a3a" ${OUT}/>
  <g transform="rotate(-8 1500 300)">
    <path d="M1452,300 L1548,300 L1526,236 L1474,236 Z" fill="#f3d68a" ${OUT}/>
  </g>

  <!-- rug, slightly askew -->
  <g transform="rotate(-2 800 905)">
    <ellipse cx="800" cy="905" rx="660" ry="84" fill="#9c4a35" ${OUT}/>
    <ellipse cx="800" cy="905" rx="610" ry="66" fill="none" stroke="#e7c99a" stroke-width="10"/>
    <ellipse cx="800" cy="905" rx="540" ry="44" fill="none" stroke="#e7c99a" stroke-width="4" opacity="0.6"/>
  </g>`;
}

// --- Dad: squat, mustard, eager, sweating, glancing sideways at the teen ----

function dad() {
  const skin = '#f0c46b';
  const body = '#e0a93b';
  return `
    ${limb('M-34,-160 L-38,-30', '#5e4a33', 40)}
    ${limb('M34,-160 L38,-30', '#5e4a33', 40)}
    <ellipse cx="-42" cy="-14" rx="36" ry="14" fill="#3b2f24" ${OUT}/>
    <ellipse cx="42" cy="-14" rx="36" ry="14" fill="#3b2f24" ${OUT}/>
    <rect x="-92" y="-300" width="184" height="176" rx="62" fill="${body}" ${OUT}/>
    <path d="M0,-282 L-15,-262 L-9,-210 L0,-200 L9,-210 L15,-262 Z" fill="#c0392b" ${OUT}/>
    ${limb('M-88,-272 L-126,-186', body, 30)}
    <circle cx="-128" cy="-176" r="18" fill="${skin}" ${OUT}/>
    ${limb('M88,-272 L150,-306 L142,-370', body, 30)}
    <circle cx="142" cy="-368" r="20" fill="${skin}" ${OUT}/>
    ${limb('M140,-374 L148,-402', skin, 14)}

    <g transform="translate(0 -370) rotate(8)">
      ${line('M-6,-72 Q-14,-104 10,-110 Q28,-114 32,-100', INK, 9)}
      ${line('M-6,-72 Q-14,-104 10,-110 Q28,-114 32,-100', '#c9d2d9', 4)}
      <circle cx="34" cy="-100" r="10" fill="#ff6b5b" ${OUT}/>
      <ellipse cx="0" cy="0" rx="92" ry="80" fill="${skin}" ${OUT}/>
      <ellipse cx="-38" cy="-12" rx="25" ry="27" fill="#fff" ${OUT}/>
      <ellipse cx="38" cy="-12" rx="25" ry="27" fill="#fff" ${OUT}/>
      <circle cx="-26" cy="-16" r="12" fill="#1d2a33"/>
      <circle cx="50" cy="-16" r="12" fill="#1d2a33"/>
      ${line('M-60,-48 Q-40,-68 -14,-52', INK, 6)}
      ${line('M14,-44 Q40,-58 60,-44', INK, 6)}
      <path d="M64,-70 Q78,-48 74,-38 Q68,-30 62,-36 Q54,-48 64,-70 Z" fill="#9fdcff" ${outline(4)}/>
      <path d="M-54,34 Q0,36 54,34 Q48,80 0,80 Q-48,80 -54,34 Z" fill="#4a1f1f" ${OUT}/>
      <path d="M-44,38 L44,38 L38,52 L-38,52 Z" fill="#fff"/>
    </g>
  `;
}

// --- Mom: tall, chrome, perfectly symmetrical, in charge of the photo -------

function mom() {
  const chrome = '#c9d7e2';
  return `
    ${limb('M-40,-170 L-40,-22', '#4b5663', 38)}
    ${limb('M40,-170 L40,-22', '#4b5663', 38)}
    <ellipse cx="-42" cy="-10" rx="38" ry="14" fill="#2f3741" ${OUT}/>
    <ellipse cx="42" cy="-10" rx="38" ry="14" fill="#2f3741" ${OUT}/>
    <rect x="-20" y="-374" width="40" height="44" fill="#8e9aa6" ${OUT}/>
    <path d="M-96,-335 Q0,-352 96,-335 Q112,-332 110,-312 L84,-172 Q80,-150 58,-150 L-58,-150 Q-80,-150 -84,-172 L-110,-312 Q-112,-332 -96,-335 Z" fill="${chrome}" ${OUT}/>
    <path d="M-84,-236 Q0,-222 84,-236 L82,-214 Q0,-200 -82,-214 Z" fill="#e0738f" ${OUT}/>
    <path d="M0,-338 L-22,-354 L-22,-322 Z M0,-338 L22,-354 L22,-322 Z" fill="#e0738f" ${OUT}/>

    ${limb('M-96,-322 Q-152,-288 -146,-236 Q-140,-214 -90,-210', chrome, 24)}
    <circle cx="-88" cy="-210" r="16" fill="${chrome}" ${OUT}/>
    ${limb('M96,-322 Q150,-336 168,-286', chrome, 24)}
    ${limb('M160,-296 L150,-270', chrome, 8)}
    <circle cx="170" cy="-282" r="18" fill="${chrome}" ${OUT}/>

    <path d="M-86,-430 Q-92,-500 0,-500 Q92,-500 86,-430 L88,-352 Q88,-336 72,-336 L-72,-336 Q-88,-336 -88,-352 Z" fill="#3d3346" ${OUT}/>
    ${limb('M-22,-482 L-30,-526', '#9aa7b3', 6)}
    ${limb('M22,-482 L30,-526', '#9aa7b3', 6)}
    <circle cx="-31" cy="-534" r="10" fill="#f6c343" ${OUT}/>
    <circle cx="31" cy="-534" r="10" fill="#f6c343" ${OUT}/>
    <rect x="-72" y="-482" width="144" height="116" rx="46" fill="#dfe8ef" ${OUT}/>
    <rect x="-44" y="-444" width="28" height="24" rx="9" fill="#17212b" ${outline(3)}/>
    <rect x="16" y="-444" width="28" height="24" rx="9" fill="#17212b" ${outline(3)}/>
    <circle cx="-36" cy="-438" r="4" fill="#fff"/>
    <circle cx="24" cy="-438" r="4" fill="#fff"/>
    ${line('M-50,-462 L-14,-452', INK, 6)}
    ${line('M50,-462 L14,-452', INK, 6)}
    ${line('M-34,-398 Q0,-372 34,-398', INK, 5)}
    ${line('M-8,-390 L-8,-380 M8,-390 L8,-380', INK, 3)}
  `;
}

// --- Teen: slouched, hood up, bored, crossed arms, leaning away -------------

function teen() {
  const hoodie = '#5b6d7a';
  return `
    ${limb('M-30,-170 L-36,-24', '#34414d', 40)}
    ${limb('M32,-170 L44,-44', '#34414d', 40)}
    <ellipse cx="-42" cy="-12" rx="40" ry="14" fill="#b8f03d" ${OUT}/>
    <ellipse cx="54" cy="-40" rx="40" ry="14" fill="#b8f03d" ${OUT}/>
    <path d="M-90,-330 Q0,-350 90,-330 L100,-190 Q96,-156 66,-150 L-66,-150 Q-96,-156 -100,-190 Z" fill="${hoodie}" ${OUT}/>

    <rect x="-22" y="-374" width="44" height="46" fill="#34414d" ${OUT}/>
    <path d="M-86,-360 Q-100,-504 0,-508 Q100,-504 86,-360 Z" fill="#46576a" ${OUT}/>
    <path d="M-84,-430 Q0,-540 84,-430" fill="none" stroke="${INK}" stroke-width="16" stroke-linecap="round"/>
    <path d="M-84,-430 Q0,-540 84,-430" fill="none" stroke="#8a9aa6" stroke-width="7" stroke-linecap="round"/>
    <rect x="-102" y="-448" width="30" height="62" rx="13" fill="#b8f03d" ${OUT}/>
    <rect x="72" y="-448" width="30" height="62" rx="13" fill="#b8f03d" ${OUT}/>
    <rect x="-66" y="-480" width="132" height="118" rx="34" fill="#1f2d38" ${OUT}/>
    <path d="M-44,-428 L-14,-428 Q-29,-412 -44,-428 Z" fill="#6ff0ff"/>
    <path d="M14,-428 L44,-428 Q29,-412 14,-428 Z" fill="#6ff0ff"/>
    ${line('M-20,-392 Q4,-388 22,-398', '#6ff0ff', 5)}

    ${limb('M-98,-300 Q-96,-236 36,-226', '#728796', 30)}
    ${limb('M98,-300 Q96,-236 -36,-226', '#728796', 30)}
  `;
}

// --- Grandpa and his rocking chair: asleep, glasses slipped, cardigan ------

function grandpaAndChair() {
  const wood = '#8a5a33';
  const cardi = '#8e5d6f';
  const head = '#b9c0c4';
  return `
    <path d="M-100,-200 L-100,-440 Q-100,-472 -68,-472 L68,-472 Q100,-472 100,-440 L100,-200 Z" fill="${wood}" ${OUT}/>
    <rect x="-70" y="-446" width="140" height="16" rx="6" fill="#a06a3c" ${outline(4)}/>
    <rect x="-116" y="-228" width="232" height="30" rx="12" fill="#a06a3c" ${OUT}/>
    ${limb('M-84,-200 L-96,-40', wood, 16)}
    ${limb('M84,-200 L96,-40', wood, 16)}
    ${limb('M-140,-56 Q0,40 140,-56', wood, 18)}

    ${limb('M-18,-170 L60,-170', '#6e6f73', 44)}
    ${limb('M60,-170 L66,-44', '#6e6f73', 40)}
    <ellipse cx="78" cy="-24" rx="34" ry="16" fill="#3b2f24" ${OUT}/>
    <rect x="-18" y="-354" width="36" height="28" fill="#7b8288" ${OUT}/>
    <path d="M-70,-332 Q0,-348 70,-332 Q86,-324 86,-300 L86,-196 Q86,-178 66,-178 L-64,-178 Q-84,-178 -84,-196 L-84,-300 Q-84,-324 -70,-332 Z" fill="${cardi}" ${OUT}/>
    ${line('M0,-330 L0,-180', '#5e3c4a', 4)}
    <circle cx="0" cy="-296" r="7" fill="#f3e2a9" ${outline(3)}/>
    <circle cx="0" cy="-254" r="7" fill="#f3e2a9" ${outline(3)}/>
    <circle cx="0" cy="-212" r="7" fill="#f3e2a9" ${outline(3)}/>
    ${limb('M-82,-300 Q-70,-236 40,-232', '#a66f80', 30)}
    <circle cx="40" cy="-232" r="16" fill="${head}" ${OUT}/>
    ${limb('M82,-300 Q66,-222 -44,-222', '#a66f80', 30)}
    <circle cx="-44" cy="-222" r="16" fill="${head}" ${OUT}/>

    <g transform="translate(0 -392) rotate(-10)">
      ${line('M20,-60 Q34,-92 60,-86', INK, 8)}
      <circle cx="66" cy="-84" r="9" fill="#ffd34d" ${OUT}/>
      <ellipse cx="0" cy="0" rx="74" ry="66" fill="${head}" ${OUT}/>
      ${line('M-44,-34 Q-36,-28 -30,-38', '#7d868c', 4)}
      ${line('M30,-40 Q42,-34 46,-46', '#7d868c', 4)}
      ${line('M-56,8 Q-48,14 -44,4', '#7d868c', 4)}
      ${line('M-42,-4 Q-30,8 -18,-4', INK, 5)}
      ${line('M18,-4 Q30,8 42,-4', INK, 5)}
      <circle cx="-30" cy="-2" r="20" fill="none" stroke="#3b3b3b" stroke-width="4"/>
      <circle cx="30" cy="-2" r="20" fill="none" stroke="#3b3b3b" stroke-width="4"/>
      ${line('M-10,-4 Q0,-10 10,-4', '#3b3b3b', 4)}
      <ellipse cx="4" cy="34" rx="9" ry="7" fill="#3b2a2a"/>
    </g>
  `;
}

// --- Sprocket the dog-bot: leaning in, one eye on the ball, tongue out ------

function dog() {
  const fur = '#c08a4a';
  return `
    ${limb('M-44,-40 L-46,-6', fur, 26)}
    ${limb('M44,-40 L46,-6', fur, 26)}
    ${limb('M74,-70 Q118,-110 104,-160', fur, 14)}
    ${line('M116,-190 Q126,-176 120,-160', INK, 3, 0.6)}
    ${line('M132,-180 Q144,-168 138,-150', INK, 3, 0.6)}
    <ellipse cx="0" cy="-70" rx="78" ry="56" fill="${fur}" ${OUT}/>
    <ellipse cx="0" cy="-54" rx="44" ry="30" fill="#e8c28a" opacity="0.85"/>
    <rect x="-46" y="-104" width="92" height="14" rx="6" fill="#b2423a" ${outline(4)}/>
    <g transform="translate(-6 -150) rotate(12)">
      <path d="M-62,-30 Q-104,-30 -98,14 Q-86,24 -62,8 Z" fill="#8a5a2b" ${OUT}/>
      <path d="M62,-30 Q104,-30 98,14 Q86,24 62,8 Z" fill="#8a5a2b" ${OUT}/>
      <rect x="-64" y="-56" width="128" height="112" rx="42" fill="${fur}" ${OUT}/>
      <circle cx="-24" cy="-14" r="18" fill="#fff" ${OUT}/>
      <circle cx="26" cy="-10" r="15" fill="#fff" ${OUT}/>
      <circle cx="-18" cy="-16" r="8" fill="#1d2a33"/>
      <circle cx="32" cy="-12" r="7" fill="#1d2a33"/>
      <ellipse cx="0" cy="18" rx="16" ry="11" fill="${INK}"/>
      <path d="M-12,24 Q-2,52 8,24 Z" fill="#ff8aa0" ${outline(3)}/>
    </g>
  `;
}

// --- Toddler-bot: mid-bounce, one antenna snapped, holding a red ball -------

function toddler() {
  const c = '#f2766b';
  return `
    ${line('M-86,-14 L-124,-14 M-78,-30 L-116,-30 M86,-14 L124,-14', '#5b3b22', 5, 0.4)}
    ${limb('M-30,-30 L-34,-6', c, 26)}
    ${limb('M30,-30 L36,-4', c, 26)}
    <ellipse cx="-34" cy="-4" rx="26" ry="11" fill="#3b2f24" ${OUT}/>
    <ellipse cx="38" cy="-2" rx="26" ry="11" fill="#3b2f24" ${OUT}/>
    <ellipse cx="0" cy="-104" rx="72" ry="84" fill="${c}" ${OUT}/>
    <circle cx="0" cy="-112" r="12" fill="#9ff0c0" ${outline(3)}/>
    ${limb('M-66,-122 L-104,-196', c, 22)}
    <circle cx="-106" cy="-208" r="15" fill="${c}" ${OUT}/>
    ${limb('M66,-120 L98,-150', c, 22)}
    <circle cx="112" cy="-176" r="24" fill="#d62f2f" ${OUT}/>
    <circle cx="104" cy="-184" r="6" fill="#ff9a8f"/>
    <circle cx="98" cy="-150" r="13" fill="${c}" ${OUT}/>

    <g transform="translate(0 -226) rotate(-10)">
      ${limb('M-24,-58 L-32,-96', '#9aa7b3', 6)}
      <circle cx="-33" cy="-104" r="9" fill="#ffd34d" ${OUT}/>
      ${limb('M22,-58 Q56,-54 60,-30', '#9aa7b3', 6)}
      <circle cx="62" cy="-26" r="9" fill="#ffd34d" ${OUT}/>
      <circle cx="0" cy="0" r="64" fill="#f78a7f" ${OUT}/>
      <circle cx="-22" cy="-6" r="22" fill="#fff" ${OUT}/>
      <circle cx="-18" cy="-2" r="11" fill="#1d2a33"/>
      <circle cx="-14" cy="-8" r="3" fill="#fff"/>
      ${line('M12,-2 Q24,14 36,-2', INK, 5)}
      <ellipse cx="2" cy="36" rx="16" ry="20" fill="#3b1a1a" ${outline(3)}/>
      <ellipse cx="4" cy="46" rx="9" ry="6" fill="#ff9aa8"/>
    </g>
  `;
}

// --- Cake table: a birthday nobody is quite ready for ------------------------

function cakeTable() {
  const flame = (cx, cy = -246) =>
    `<path d="M${cx},${cy - 26} Q${cx + 9},${cy - 10} ${cx},${cy} Q${cx - 9},${cy - 10} ${cx},${cy - 26} Z" fill="#ffb703" ${outline(3)}/>`;
  return `
    <rect x="-8" y="-124" width="16" height="124" fill="#8a5a33" ${OUT}/>
    <ellipse cx="0" cy="0" rx="56" ry="12" fill="#6b4424" ${OUT}/>
    <ellipse cx="0" cy="-124" rx="92" ry="22" fill="#a06a3c" ${OUT}/>
    <rect x="-52" y="-196" width="104" height="72" rx="8" fill="#f7c6d6" ${OUT}/>
    <rect x="-52" y="-160" width="104" height="14" fill="#b65c8a"/>
    <path d="M-56,-196 Q-46,-214 -36,-196 Q-26,-210 -14,-196 Q-4,-212 8,-196 Q20,-208 30,-196 Q42,-212 56,-196 Z" fill="#fff3f7" ${outline(4)}/>
    ${[-34, -12, 12].map((x) => `<rect x="${x - 4}" y="-244" width="8" height="46" fill="#fff" ${outline(3)}/>${flame(x)}`).join('')}
    <g transform="rotate(-22 34 -198)">
      <rect x="30" y="-244" width="8" height="46" fill="#fff" ${outline(3)}/>
      ${flame(34)}
    </g>
  `;
}

// --- Assemble ----------------------------------------------------------------

function place(x, y, s, inner) {
  return `<g transform="translate(${x} ${y}) scale(${s})">${inner}</g>`;
}

function build() {
  const scene = [
    background(),
    shadow(880, 110),
    shadow(620, 110),
    shadow(330, 120),
    shadow(480, 80),
    shadow(730, 80),
    shadow(1040, 80),
    shadow(1190, 80),
    // back to front: Dad first so Mom's hand can rest on his shoulder
    place(880, FLOOR, 1, dad()),
    place(620, FLOOR, 1, mom()),
    `<g transform="translate(1190 ${FLOOR}) rotate(9)">${teen()}</g>`,
    place(330, FLOOR, 1, grandpaAndChair()),
    place(480, FLOOR, 0.9, dog()),
    place(730, FLOOR, 0.95, toddler()),
    place(1040, FLOOR, 1, cakeTable()),
    `<rect width="${W}" height="${H}" fill="url(#vignette)"/>`,
  ].join('\n');

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
${scene}
</svg>
`;
}

const file = join(outDir, 'robot_family_portrait.svg');
writeFileSync(file, build());
console.log(`wrote ${file}`);
