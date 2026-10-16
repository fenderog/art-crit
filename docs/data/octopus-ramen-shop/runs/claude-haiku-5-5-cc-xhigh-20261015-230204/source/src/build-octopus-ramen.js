// Builds output/octopus-ramen-booth.svg: an octopus chef serving ramen at a night-time noodle stall.
// Run from the working directory with: node src/build-octopus-ramen.js
'use strict';

const fs = require('fs');
const path = require('path');

const W = 1200;
const H = 900;
const OUT_FILE = path.join(__dirname, '..', 'output', 'octopus-ramen-booth.svg');

// Seeded PRNG so the stars, bokeh, and noodles come out identical on every build.
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(7);
const between = (lo, hi) => lo + (hi - lo) * rand();
const fmt = (v) => (Math.round(v * 10) / 10).toString();

// Tentacle: dark outline, purple body, soft highlight, and pale suckers.
// The sucker layer is a zero-length dash pattern, so it draws as dots along the path.
function tentacle(d, w) {
  return `
  <path d="${d}" fill="none" stroke="#3b1d5e" stroke-width="${fmt(w + 6)}" stroke-linecap="round"/>
  <path d="${d}" fill="none" stroke="#8c55c9" stroke-width="${fmt(w)}" stroke-linecap="round"/>
  <path d="${d}" fill="none" stroke="#c4a4f0" stroke-width="${fmt(w * 0.22)}" stroke-linecap="round" opacity="0.6" transform="translate(${fmt(-w * 0.22)} ${fmt(-w * 0.18)})"/>
  <path d="${d}" fill="none" stroke="#f7c6e6" stroke-width="${fmt(w * 0.2)}" stroke-linecap="round" stroke-dasharray="0 ${fmt(w * 0.6)}"/>`;
}

// Steam wisp that drifts up and fades, looping forever.
function steam(x, y, h, delay) {
  const d = `M${x} ${y} C${x - 14} ${y - h * 0.35} ${x + 14} ${y - h * 0.65} ${x} ${y - h}`;
  return `
  <path d="${d}" fill="none" stroke="#fff3dc" stroke-width="7" stroke-linecap="round" filter="url(#soft)" opacity="0.35">
    <animate attributeName="opacity" values="0.15;0.6;0.15" keyTimes="0;0.4;1" dur="3.2s" begin="${delay}s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 8;0 -8;0 -18" dur="3.2s" begin="${delay}s" repeatCount="indefinite"/>
  </path>`;
}

// Wavy noodle strands, clipped to the broth surface by the caller.
function noodles(cx, cy) {
  let out = '';
  for (let row = -3; row <= 3; row++) {
    const y = cy + row * 4.4 + between(-1, 1);
    let d = `M${fmt(cx - 150 + between(0, 30))} ${fmt(y)}`;
    for (let k = 0; k < 24; k++) d += ` q6 ${k % 2 ? 4 : -4} 12 0`;
    out += `<path d="${d}" fill="none" stroke="#ffe3a3" stroke-width="2.6" stroke-linecap="round" opacity="0.9"/>`;
  }
  return out;
}

// Green scallion rings scattered over the broth.
function scallions(cx, cy, rx, ry) {
  let out = '';
  for (let i = 0; i < 9; i++) {
    const a = between(0, Math.PI * 2);
    const r = Math.sqrt(rand()) * 0.85;
    const x = cx + Math.cos(a) * r * rx;
    const y = cy + Math.sin(a) * r * ry;
    out += `<circle cx="${fmt(x)}" cy="${fmt(y)}" r="2.8" fill="#6fbf4a" stroke="#3d7a2a" stroke-width="0.8"/>`;
  }
  return out;
}

// Jars on a wooden shelf whose top surface sits at y0.
function shelfJars(x0, y0, colors) {
  return colors
    .map((c, i) => {
      const h = 26 + ((i * 17) % 18);
      const x = x0 + i * 34;
      return `
  <rect x="${x}" y="${y0 - h}" width="22" height="${h}" rx="5" fill="${c}" stroke="#1d0f05" stroke-width="2"/>
  <rect x="${x + 5}" y="${y0 - h - 8}" width="12" height="9" rx="2" fill="#2b1709"/>`;
    })
    .join('');
}

// Hanging paper lantern from the awning.
function lantern(x) {
  const cy = 252;
  return `
  <line x1="${x}" y1="192" x2="${x}" y2="210" stroke="#2b1709" stroke-width="3"/>
  <circle cx="${x}" cy="${cy}" r="96" fill="url(#lanternGlow)"/>
  <ellipse cx="${x}" cy="${cy}" rx="32" ry="40" fill="#d62828" stroke="#6e0c10" stroke-width="3"/>
  <path d="M${x - 31} ${cy - 14} Q${x} ${cy - 19} ${x + 31} ${cy - 14} M${x - 31} ${cy + 14} Q${x} ${cy + 19} ${x + 31} ${cy + 14}" fill="none" stroke="#f4c542" stroke-width="4"/>
  <rect x="${x - 15}" y="210" width="30" height="8" rx="2" fill="#2b1709"/>
  <rect x="${x - 12}" y="290" width="24" height="7" rx="2" fill="#2b1709"/>
  <line x1="${x}" y1="297" x2="${x}" y2="312" stroke="#f4c542" stroke-width="3"/>`;
}

const defs = `
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#171129"/>
    <stop offset="0.6" stop-color="#2e1d4a"/>
    <stop offset="1" stop-color="#4a2a55"/>
  </linearGradient>
  <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="560" cy="430" r="520">
    <stop offset="0" stop-color="#ffc56b" stop-opacity="0.5"/>
    <stop offset="1" stop-color="#ffc56b" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="lanternGlow">
    <stop offset="0" stop-color="#ffd166" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#ffd166" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="woodTop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#d9a46b"/>
    <stop offset="1" stop-color="#b07444"/>
  </linearGradient>
  <linearGradient id="woodFront" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6e4528"/>
    <stop offset="1" stop-color="#442717"/>
  </linearGradient>
  <pattern id="awning" width="80" height="20" patternUnits="userSpaceOnUse">
    <rect width="40" height="20" fill="#b3262e"/>
    <rect x="40" width="40" height="20" fill="#f5efe1"/>
  </pattern>
  <clipPath id="broth">
    <ellipse cx="560" cy="580" rx="124" ry="19"/>
  </clipPath>
  <filter id="soft" x="-50%" y="-20%" width="200%" height="140%">
    <feGaussianBlur stdDeviation="2"/>
  </filter>
  <filter id="bokehBlur" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
</defs>`;

// Night backdrop: stars and out-of-focus city lights.
const stars = Array.from({ length: 30 }, () => {
  const x = between(0, W);
  const y = between(0, 250);
  const r = between(1, 2);
  const o = between(0.5, 0.9);
  return `<circle cx="${fmt(x)}" cy="${fmt(y)}" r="${fmt(r)}" fill="#fff" opacity="${fmt(o)}"/>`;
}).join('');

const palette = ['#ffb347', '#ff6f91', '#7fd1ff', '#ffd166', '#c3a6ff'];
const bokeh = Array.from({ length: 38 }, () => {
  const x = between(0, W);
  const y = between(0, 560);
  const r = between(6, 24);
  const c = palette[Math.floor(between(0, palette.length))];
  const o = between(0.15, 0.4);
  return `<circle cx="${fmt(x)}" cy="${fmt(y)}" r="${fmt(r)}" fill="${c}" opacity="${fmt(o)}"/>`;
}).join('');

// Back wall of warm wood with slats, glow, and two shelves of jars.
const slats = [];
for (let x = 196; x < 1054; x += 50) {
  slats.push(`<line x1="${x}" y1="170" x2="${x}" y2="610" stroke="#3a2112" stroke-width="3" opacity="0.8"/>`);
}
const wall = `
  <rect x="146" y="170" width="908" height="440" fill="#4a2c1a"/>
  ${slats.join('')}
  <rect x="146" y="170" width="908" height="440" fill="url(#glow)"/>
  <rect x="170" y="380" width="200" height="10" rx="3" fill="#2b1709"/>
  ${shelfJars(170, 380, ['#8b2e2e', '#c9a227', '#3d6b3a', '#d8cfb8', '#8b2e2e'])}
  <rect x="830" y="380" width="200" height="10" rx="3" fill="#2b1709"/>
  ${shelfJars(830, 380, ['#3d6b3a', '#d8cfb8', '#c9a227', '#8b2e2e', '#3d6b3a'])}
  <rect x="110" y="170" width="36" height="430" fill="#2b1709"/>
  <rect x="1054" y="170" width="36" height="430" fill="#2b1709"/>`;

// Tentacles that rest behind the chef and counter.
const backTentacles =
  tentacle('M450 500 C385 530 310 545 255 520 C215 502 185 520 200 540', 30) +
  tentacle('M660 500 C730 540 800 545 860 515 C905 492 940 515 925 538', 30);

// Chef's head (mantle), toque, face, and apron. Drawn in a group shifted down by 20px.
const head = `
  <g transform="translate(0 20)">
    <path d="M425 470 C398 370 425 280 520 270 C548 266 572 266 600 270 C695 280 722 370 695 470 C680 500 640 492 620 494 C590 500 530 500 500 494 C480 492 440 500 425 470 Z" fill="#8c55c9" stroke="#3b1d5e" stroke-width="4"/>
    <ellipse cx="478" cy="325" rx="22" ry="42" transform="rotate(-22 478 325)" fill="#b994e8" opacity="0.45"/>
    <circle cx="470" cy="300" r="4" fill="#d7a8f0" opacity="0.6"/>
    <circle cx="640" cy="318" r="3.5" fill="#d7a8f0" opacity="0.6"/>
    <circle cx="455" cy="380" r="3" fill="#d7a8f0" opacity="0.6"/>
    <circle cx="665" cy="395" r="3" fill="#d7a8f0" opacity="0.6"/>

    <path d="M490 292 C462 286 458 246 486 236 C482 206 518 190 540 206 C552 176 606 176 618 206 C642 194 680 214 668 240 C700 246 694 292 664 292 Z" fill="#fff" stroke="#b7bdc9" stroke-width="3"/>
    <rect x="488" y="282" width="144" height="34" rx="6" fill="#fbfbfb" stroke="#b7bdc9" stroke-width="3"/>

    <path d="M498 330 Q520 316 542 330 M582 330 Q602 316 622 330" fill="none" stroke="#2a1845" stroke-width="5" stroke-linecap="round"/>
    <ellipse cx="520" cy="372" rx="24" ry="28" fill="#fff" stroke="#2a1845" stroke-width="3"/>
    <ellipse cx="602" cy="372" rx="24" ry="28" fill="#fff" stroke="#2a1845" stroke-width="3"/>
    <circle cx="524" cy="380" r="12" fill="#1b1030"/>
    <circle cx="606" cy="380" r="12" fill="#1b1030"/>
    <circle cx="528" cy="373" r="4" fill="#fff"/>
    <circle cx="610" cy="373" r="4" fill="#fff"/>
    <ellipse cx="486" cy="408" rx="16" ry="9" fill="#ff6b9a" opacity="0.55"/>
    <ellipse cx="636" cy="408" rx="16" ry="9" fill="#ff6b9a" opacity="0.55"/>
    <path d="M548 414 Q561 438 576 414 Z" fill="#7a2140" stroke="#2a1845" stroke-width="2.5" stroke-linejoin="round"/>
    <ellipse cx="561" cy="428" rx="7" ry="4" fill="#ff8fb1"/>

    <path d="M478 434 C462 412 440 402 420 404 M646 434 C662 412 684 402 704 404" fill="none" stroke="#c9c1ad" stroke-width="9" stroke-linecap="round"/>
    <path d="M478 434 C462 412 440 402 420 404 M646 434 C662 412 684 402 704 404" fill="none" stroke="#fbf7ef" stroke-width="6" stroke-linecap="round"/>
    <path d="M478 432 Q561 442 646 432 L660 560 Q561 572 466 560 Z" fill="#fbf7ef" stroke="#c9c1ad" stroke-width="2.5"/>
    <rect x="510" y="500" width="100" height="40" rx="4" fill="none" stroke="#d9d1bd" stroke-width="2"/>
    <path d="M466 560 Q561 572 660 560" fill="none" stroke="#b3262e" stroke-width="5"/>
  </g>`;

// Pot of broth on the left, with a ladle standing in it.
const pot = `
  <rect x="134" y="588" width="22" height="12" rx="5" fill="#3e434d"/>
  <rect x="344" y="588" width="22" height="12" rx="5" fill="#3e434d"/>
  <path d="M154 570 V628 Q154 650 178 650 H322 Q346 650 346 628 V570 Z" fill="#6b7280" stroke="#2d313a" stroke-width="3"/>
  <rect x="154" y="604" width="192" height="7" fill="#b3262e"/>
  <rect x="166" y="580" width="8" height="54" rx="4" fill="#fff" opacity="0.18"/>
  <ellipse cx="250" cy="570" rx="96" ry="20" fill="#8a92a0" stroke="#2d313a" stroke-width="3"/>
  <ellipse cx="250" cy="572" rx="84" ry="14" fill="#e0943a"/>
  <ellipse cx="232" cy="569" rx="20" ry="3" fill="#ffd08a" opacity="0.7"/>
  <path d="M250 580 L336 398" stroke="#6b4423" stroke-width="7" stroke-linecap="round"/>
  <ellipse cx="250" cy="580" rx="15" ry="9" fill="#4a2e18" stroke="#2b1709" stroke-width="2"/>`;

// Ramen bowl at the centre of the counter.
const bowl = `
  <path d="M430 582 C436 630 490 646 560 646 C630 646 684 630 690 582 Z" fill="#f6f1e6" stroke="#c4b8a0" stroke-width="2.5"/>
  <path d="M440 614 Q560 644 680 614" fill="none" stroke="#b3262e" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="560" cy="580" rx="132" ry="24" fill="#fbf8f1" stroke="#c4b8a0" stroke-width="2.5"/>
  <ellipse cx="560" cy="580" rx="124" ry="19" fill="#e9a14a"/>
  <ellipse cx="548" cy="576" rx="84" ry="11" fill="#f2bb66" opacity="0.7"/>
  <g clip-path="url(#broth)">${noodles(560, 580)}</g>
  <ellipse cx="508" cy="578" rx="26" ry="14" fill="#c9674a" stroke="#7a2e20" stroke-width="2" transform="rotate(-12 508 578)"/>
  <ellipse cx="508" cy="578" rx="16" ry="7" fill="none" stroke="#f1cfb4" stroke-width="2" transform="rotate(-12 508 578)"/>
  <rect x="547" y="536" width="25" height="46" rx="3" fill="#1f3d2b" transform="rotate(-6 560 558)"/>
  <ellipse cx="606" cy="590" rx="24" ry="14" fill="#fffaf2" stroke="#c9bca8" stroke-width="1.5"/>
  <circle cx="608" cy="590" r="9" fill="#f5a623"/>
  ${scallions(560, 580, 124, 19)}`;

// Spare bowls stacked at the right end of the counter.
const bowlStack = `
  <path d="M1030 612 Q1034 640 1070 640 Q1106 640 1110 612 Z" fill="#f6f1e6" stroke="#c4b8a0" stroke-width="2.5"/>
  <path d="M1038 626 Q1070 636 1102 626" fill="none" stroke="#2f6f8f" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="1070" cy="612" rx="40" ry="9" fill="#fbf8f1" stroke="#c4b8a0" stroke-width="2.5"/>`;

// Arms that reach over the counter: one wraps the ladle, one holds chopsticks up high.
const frontTentacles = [
  tentacle('M445 470 C410 470 372 452 356 424 C346 404 326 398 318 412 C312 424 330 432 340 420', 34),
  tentacle('M455 478 C440 530 428 580 408 612 C398 628 372 634 372 618 C372 606 386 604 390 614', 32),
  tentacle('M705 478 C742 540 764 596 800 614 C822 624 848 614 836 600 C828 590 816 600 824 608', 32),
  tentacle('M715 462 C812 490 880 540 930 596 C952 620 972 640 954 644 C940 648 938 632 950 630', 30),
  tentacle('M690 470 C752 450 796 404 800 340 C802 300 830 282 846 296 C858 308 842 324 832 314', 32),
].join('');

const chopsticks = `
  <line x1="832" y1="314" x2="874" y2="232" stroke="#e3b678" stroke-width="5" stroke-linecap="round"/>
  <line x1="838" y1="310" x2="888" y2="242" stroke="#c98f4f" stroke-width="5" stroke-linecap="round"/>`;

// Counter: wooden top with a plank-front panel.
const counter = `
  <rect x="0" y="600" width="${W}" height="60" fill="url(#woodTop)"/>
  <rect x="0" y="600" width="${W}" height="3" fill="#e6b982"/>
  <rect x="0" y="652" width="${W}" height="10" fill="#8a5530"/>
  <rect x="0" y="662" width="${W}" height="238" fill="url(#woodFront)"/>
  <g stroke="#3a2312" stroke-width="3">
    <line x1="0" y1="720" x2="${W}" y2="720"/>
    <line x1="0" y1="790" x2="${W}" y2="790"/>
    <line x1="0" y1="860" x2="${W}" y2="860"/>
    <line x1="300" y1="662" x2="300" y2="720"/>
    <line x1="620" y1="720" x2="620" y2="790"/>
    <line x1="940" y1="662" x2="940" y2="720"/>
    <line x1="460" y1="790" x2="460" y2="860"/>
    <line x1="780" y1="860" x2="780" y2="${H}"/>
  </g>`;

// Awning with a scalloped lower edge, drawn last so it overlaps the chef's hat.
const awningEdge = (() => {
  let d = 'M120 92 H1080 V170';
  for (let k = 0; k < 12; k++) d += ' a40 22 0 0 1 -80 0';
  return d + ' Z';
})();
const awning = `
  <path d="${awningEdge}" fill="url(#awning)" stroke="#4a0e12" stroke-width="2"/>
  <rect x="120" y="92" width="960" height="8" fill="#3a0d10" opacity="0.5"/>
  <rect x="470" y="108" width="180" height="50" rx="6" fill="#f5efe1" stroke="#5a1216" stroke-width="3"/>
  <text x="560" y="145" text-anchor="middle" font-family="'Arial Black', Impact, 'Helvetica Neue', Arial, sans-serif" font-weight="900" font-size="34" letter-spacing="2" fill="#b3262e">RAMEN</text>`;

const steamWisps = [
  steam(222, 540, 110, 0),
  steam(252, 536, 130, 1.1),
  steam(282, 540, 100, 2.0),
  steam(544, 556, 90, 0.5),
  steam(578, 556, 80, 1.6),
].join('');

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
<title>Octopus chef serving ramen at a night-time noodle stall</title>
${defs}
<rect width="${W}" height="${H}" fill="url(#sky)"/>
<g fill="#fff">${stars}</g>
<g filter="url(#bokehBlur)">${bokeh}</g>
${wall}
${backTentacles}
${head}
${steamWisps}
${counter}
${pot}
${bowl}
${bowlStack}
${frontTentacles}
${chopsticks}
${awning}
${lantern(232)}
${lantern(968)}
</svg>
`;

fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });
fs.writeFileSync(OUT_FILE, svg);
console.log(`wrote ${path.relative(process.cwd(), OUT_FILE)} (${svg.length} bytes)`);
