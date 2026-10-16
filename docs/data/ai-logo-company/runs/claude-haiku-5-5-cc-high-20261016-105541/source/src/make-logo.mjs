// Generates the "Mycel" logo: a generative, organic mark in neutral tones.
// Shapes are seeded so the same SVG is produced on every run.
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, '..', 'output');
mkdirSync(outDir, { recursive: true });

// Small seeded PRNG (mulberry32) for reproducible randomness
function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const f = (v) => v.toFixed(2);

// Closed, smooth blob through n jittered points around a circle.
// Points are joined with Catmull-Rom splines converted to cubic Béziers.
function blobPath({ cx, cy, r, n, wobble, rand }) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const k = 1 + (rand() * 2 - 1) * wobble;
    pts.push([cx + Math.cos(a) * r * k, cy + Math.sin(a) * r * k]);
  }
  let d = `M${f(pts[0][0])},${f(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += `C${f(c1[0])},${f(c1[1])} ${f(c2[0])},${f(c2[1])} ${f(p2[0])},${f(p2[1])}`;
  }
  return d + 'Z';
}

const rand = mulberry32(20261016);
const CX = 256;
const CY = 256;

const layers = [
  { r: 170, n: 7, wobble: 0.12, fill: 'url(#sand)', opacity: 1 },
  { r: 118, n: 6, wobble: 0.15, fill: '#8C8478', opacity: 0.9 },
  { r: 62, n: 5, wobble: 0.1, fill: '#2F2B27', opacity: 1 },
];

const blobs = layers
  .map((l) => {
    const d = blobPath({ cx: CX, cy: CY, ...l, rand });
    return `    <path d="${d}" fill="${l.fill}" opacity="${l.opacity}"/>`;
  })
  .join('\n');

// Generative "spores" orbiting the outer form
const spores = [];
const SPORE_COUNT = 9;
for (let i = 0; i < SPORE_COUNT; i++) {
  const a = (i / SPORE_COUNT) * Math.PI * 2 + (rand() - 0.5) * 0.5;
  const dist = 196 + rand() * 30;
  const r = 6 + rand() * 12;
  const x = CX + Math.cos(a) * dist;
  const y = CY + Math.sin(a) * dist;
  const tone = ['#6B645A', '#A39A8C', '#5A544B'][Math.floor(rand() * 3)];
  spores.push(
    `    <path d="${blobPath({ cx: x, cy: y, r, n: 5, wobble: 0.2, rand })}" fill="${tone}"/>`
  );
}

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 512" width="960" height="512" role="img" aria-labelledby="title">
  <title id="title">Mycel logo</title>
  <defs>
    <linearGradient id="sand" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#EAE4D8"/>
      <stop offset="1" stop-color="#BDB3A3"/>
    </linearGradient>
  </defs>
  <rect width="960" height="512" fill="#F4F1EC"/>
  <g id="mark">
${blobs}
${spores.join('\n')}
  </g>
  <g id="wordmark" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif">
    <text x="500" y="300" font-size="124" font-weight="300" letter-spacing="-3" fill="#2F2B27">Mycel</text>
    <text x="504" y="352" font-size="26" font-weight="400" letter-spacing="7" fill="#8C8478">GENERATIVE SYSTEMS</text>
  </g>
</svg>
`;

writeFileSync(join(outDir, 'mycel-logo.svg'), svg);
console.log('wrote output/mycel-logo.svg');
