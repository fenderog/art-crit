// Builds the Flint logo SVGs into ./output (and caches traced geometry in ./build).
// Usage: node src/build.mjs [outDir]
import fs from 'node:fs';
import path from 'node:path';
import { buildMark } from './mark.mjs';
import { buildWordmark } from './wordmark.mjs';
import { pathData } from './geom.mjs';
import { palette, markParams, wordParams, fragmentTones } from './design.mjs';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const cacheDir = path.join(root, 'build');
fs.mkdirSync(cacheDir, { recursive: true });

// ---------- geometry (traced once, cached) ----------
function cached(name, params, make) {
  const file = path.join(cacheDir, `${name}.json`);
  const key = JSON.stringify(params);
  if (fs.existsSync(file)) {
    const c = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (c.key === key) return c.data;
  }
  const data = make();
  fs.writeFileSync(file, JSON.stringify({ key, data }));
  return data;
}
const markGeo = cached('mark', markParams, () => {
  const m = buildMark(markParams);
  return { fragments: m.fragments.map(f => f.curves), stone: m.stone, spark: m.spark.pts, tips: m.spark.tips, fissures: m.fissures };
});
const mark = markGeo.fragments;
const word = cached('word', wordParams, () => {
  const w = buildWordmark(wordParams);
  return { width: w.width, loops: w.loops.map(l => l.curves) };
});

// ---------- helpers ----------
const bbox = loops => {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const loop of loops) for (const c of loop) for (const p of [c[0], c[3]]) {
    x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]);
  }
  return { x0, y0, x1, y1, w: x1 - x0, h: y1 - y0 };
};
const xf = (loops, s, dx, dy) => loops.map(l => l.map(c => c.map(([x, y]) => [x * s + dx, y * s + dy])));
const d = loops => loops.map(l => pathData(l)).join('');
const r2 = v => +v.toFixed(2);

const markBox = bbox(mark);
const wordBox = bbox(word.loops);

// Place the mark so its bounding box spans height h with top-left at (x, y).
const placeMark = (h, x, y) => { const s = h / markBox.h; return xf(mark, s, x - markBox.x0 * s, y - markBox.y0 * s); };
// Place the wordmark with x-height xh and baseline at (x, y) (x = left edge of ink).
const placeWord = (xh, x, y) => { const s = xh / wordParams.X; return xf(word.loops, s, x - wordBox.x0 * s, y); };

const markPaths = (frags, tones) => frags.map((f, i) => `<path fill="${palette[tones[i]]}" d="${pathData(f)}"/>`).join('\n  ');

function svgDoc(w, h, body, { bg, title } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${r2(w)} ${r2(h)}" width="${r2(w)}" height="${r2(h)}">
  <title>${title ?? 'Flint'}</title>
  ${bg ? `<rect width="${r2(w)}" height="${r2(h)}" fill="${bg}"/>\n  ` : ''}${body}
</svg>
`;
}

// ---------- layouts ----------
// Horizontal lockup proportions, all relative to the wordmark x-height (xh).
export const LOCKUP = { markH: 2.3, gap: 0.72, pad: 1 };

export function lockup(xh, tones, inkFill, { bg, pad = LOCKUP.pad } = {}) {
  const mh = LOCKUP.markH * xh;
  const P = pad * xh;
  const wordH = (wordBox.h / wordParams.X) * xh;
  // centre the mark on the x-height band, nudged up slightly for the ascenders
  const baseline = P + mh / 2 + xh / 2 - 0.06 * xh;
  const m = placeMark(mh, P, P);
  const wx = P + (markBox.w / markBox.h) * mh + LOCKUP.gap * xh;
  const w = placeWord(xh, wx, baseline);
  const W = wx + (wordBox.w / wordParams.X) * xh + P;
  const H = Math.max(P * 2 + mh, baseline + wordBox.y1 / wordParams.X * xh + P);
  const body = `${markPaths(m, tones)}\n  <path fill="${inkFill}" d="${d(w)}"/>`;
  return { W, H, body, wordH };
}

export function markOnly(h, tones, { pad = 0, bg } = {}) {
  const m = placeMark(h, pad, pad);
  const W = (markBox.w / markBox.h) * h + pad * 2, H = h + pad * 2;
  return { W, H, body: markPaths(m, tones) };
}

export function stacked(xh, tones, inkFill, { pad = 0.9 } = {}) {
  const mh = 3.1 * xh, P = pad * xh;
  const ww = (wordBox.w / wordParams.X) * xh, mw = (markBox.w / markBox.h) * mh;
  const W = Math.max(ww, mw) + 2 * P;
  const m = placeMark(mh, (W - mw) / 2, P);
  const baseline = P + mh + 0.95 * xh + (-wordBox.y0 / wordParams.X) * xh - xh;
  const w = placeWord(xh, (W - ww) / 2, baseline + xh * 0.0);
  const H = baseline + (wordBox.y1 / wordParams.X) * xh + P;
  return { W, H, body: `${markPaths(m, tones)}\n  <path fill="${inkFill}" d="${d(w)}"/>` };
}

// Map raw mark-space points into a placed mark (same transform as placeMark).
const markXform = (h, x, y) => { const s = h / markBox.h; return p => [p[0] * s + x - markBox.x0 * s, p[1] * s + y - markBox.y0 * s]; };

export const geometry = { mark, markGeo, word, markBox, wordBox, placeMark, placeWord, markXform, markPaths, d, svgDoc, bbox };

// ---------- write outputs ----------
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  const outDir = path.resolve(process.argv[2] ?? path.join(root, 'output'));
  fs.mkdirSync(outDir, { recursive: true });
  const L = fragmentTones.light, D = fragmentTones.dark;
  const write = (name, s) => { fs.writeFileSync(path.join(outDir, name), s); console.log('wrote', name, (s.length / 1024).toFixed(1) + 'KB'); };

  const prim = lockup(40, L, palette.basalt);
  write('flint-logo.svg', svgDoc(prim.W, prim.H, prim.body, { title: 'Flint — primary logo' }));

  const rev = lockup(40, D, palette.chalk);
  write('flint-logo-reversed.svg', svgDoc(rev.W, rev.H, rev.body, { bg: palette.night, title: 'Flint — reversed logo' }));

  const mk = markOnly(240, L, { pad: 0 });
  write('flint-mark.svg', svgDoc(mk.W, mk.H, mk.body, { title: 'Flint — mark' }));

  const mono = markOnly(240, ['basalt', 'basalt', 'basalt', 'basalt']);
  write('flint-mark-mono.svg', svgDoc(mono.W, mono.H, mono.body.replace(/<path fill="[^"]+" d="/g, '<path d="').replace(/^/, `<g fill="${palette.basalt}">\n  `) + '\n  </g>', { title: 'Flint — mark, one colour' }));
}
