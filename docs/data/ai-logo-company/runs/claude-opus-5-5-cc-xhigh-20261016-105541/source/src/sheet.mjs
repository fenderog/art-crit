// Brand presentation sheet: lockups, construction, one-colour use, icons and palette.
// Usage: node src/sheet.mjs out.svg   (rasterised to PNG by src/render.sh)
import fs from 'node:fs';
import { geometry, lockup, markOnly } from './build.mjs';
import { palette as C, fragmentTones, wordParams } from './design.mjs';
import { stoneOutline } from './mark.mjs';

const { markGeo, markBox, wordBox, placeMark, placeWord, markXform, markPaths, d } = geometry;
const W = 1600, H = 1000, M = 56, G = 24;
const font = `font-family="Avenir Next, Avenir, Helvetica Neue, sans-serif"`;
const demi = `font-family="Avenir Next Demi Bold, AvenirNext-DemiBold, Avenir Next, sans-serif"`;
const label = (x, y, text, fill = C.taupe) =>
  `<text x="${x}" y="${y}" ${demi} font-size="10.5" letter-spacing="2.2" fill="${fill}">${text}</text>`;
const note = (x, y, text, fill = C.taupe, anchor = 'start', size = 12) =>
  `<text x="${x}" y="${y}" ${font} font-size="${size}" font-weight="500" fill="${fill}" text-anchor="${anchor}">${text}</text>`;
const poly = (pts, close = true) => 'M' + pts.map(p => p.map(v => v.toFixed(2)).join(' ')).join('L') + (close ? 'Z' : '');
const g = (dx, dy, body) => `<g transform="translate(${dx} ${dy})">${body}</g>`;
const markW = h => (markBox.w / markBox.h) * h;
const wordW = xh => (wordBox.w / wordParams.X) * xh;

let s = '';
const panel = (x, y, w, h, fill) => { s += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${fill}"/>`; };

// header
s += `<text x="${M}" y="36" ${demi} font-size="12" letter-spacing="3" fill="${C.basalt}">FLINT</text>`;
s += note(M + 62, 36, 'Identity system — generative AI, grounded in nature', C.taupe, 'start', 12);
s += note(W - M, 36, 'Logo v1.0 · 2026', C.taupe, 'end', 12);

// A — primary lockup
{
  const x = M, y = M, w = 944, h = 500;
  panel(x, y, w, h, C.chalk);
  s += label(x + 24, y + 34, 'PRIMARY LOCKUP');
  const L = lockup(74, fragmentTones.light, C.basalt, { pad: 0 });
  s += g(x + (w - L.W) / 2, y + (h - L.H) / 2 + 6, L.body);
  s += note(x + 24, y + h - 24, 'Clear space: one x-height on every side · custom lowercase wordmark', C.stone, 'start', 11);
}
// B — reversed, stacked
{
  const x = M + 944 + G, y = M, w = W - M - x, h = 500;
  panel(x, y, w, h, C.night);
  s += label(x + 24, y + 34, 'REVERSED · STACKED', C.stone);
  const mh = 196, xh = 44;
  const mx = x + (w - markW(mh)) / 2, my = y + 98;
  s += markPaths(placeMark(mh, mx, my), fragmentTones.dark);
  const base = my + mh + 46 + xh * 1.42;
  s += `<path fill="${C.chalk}" d="${d(placeWord(xh, x + (w - wordW(xh)) / 2, base))}"/>`;
}

// Row 2
const y2 = M + 500 + G, h2 = H - M - y2, w2 = (W - 2 * M - 3 * G) / 4;

// C — construction
{
  const x = M, y = y2;
  panel(x, y, w2, h2, C.oat);
  s += label(x + 24, y + 34, 'CONSTRUCTION');
  const mh = 230, mx = x + (w2 - markW(mh)) / 2, my = y + 72;
  const T = markXform(mh, mx, my);
  s += `<g opacity="0.22">${markPaths(placeMark(mh, mx, my), ['basalt', 'basalt', 'basalt', 'basalt'])}</g>`;
  s += `<path d="${poly(markGeo.stone.map(T))}" fill="none" stroke="${C.basalt}" stroke-width="0.9" stroke-dasharray="3 3"/>`;
  s += `<path d="${poly(markGeo.spark.map(T))}" fill="none" stroke="${C.basalt}" stroke-width="1.1"/>`;
  // fissure centre lines, stopped a little past the stone edge
  const inside = ([px, py], pg) => { let c = false; for (let i = 0, j = pg.length - 1; i < pg.length; j = i++) { const [xi, yi] = pg[i], [xj, yj] = pg[j]; if ((yi > py) !== (yj > py) && px < xi + (xj - xi) * (py - yi) / (yj - yi)) c = !c; } return c; };
  for (const f of markGeo.fissures) {
    const out = f.findIndex(p => !inside(p, markGeo.stone));
    s += `<path d="${poly(f.slice(0, out < 0 ? f.length : Math.min(f.length, out + 8)).map(T), false)}" fill="none" stroke="${C.basalt}" stroke-width="0.9"/>`;
  }
  const c = T([0, 0]);
  s += `<circle cx="${c[0]}" cy="${c[1]}" r="2.2" fill="${C.basalt}"/>`;
  for (const t of markGeo.tips) { const p = T(t); s += `<circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${C.oat}" stroke="${C.basalt}" stroke-width="1"/>`; }
  s += note(x + 24, y + h2 - 24, 'River stone · four-point spark · four fissures', C.basalt, 'start', 11);
}
// D — one colour
{
  const x = M + w2 + G, y = y2;
  panel(x, y, w2, h2, C.chalk);
  s += `<path d="M${x + w2 / 2} ${y}H${x + w2 - 6}a6 6 0 0 1 6 6V${y + h2 - 6}a6 6 0 0 1-6 6H${x + w2 / 2}Z" fill="${C.taupe}"/>`;
  s += label(x + 24, y + 34, 'ONE COLOUR');
  const mh = 104;
  const m1 = placeMark(mh, x + (w2 / 2 - markW(mh)) / 2, y + (h2 - mh) / 2);
  const m2 = placeMark(mh, x + w2 / 2 + (w2 / 2 - markW(mh)) / 2, y + (h2 - mh) / 2);
  s += `<path fill="${C.basalt}" d="${d(m1)}"/><path fill="${C.chalk}" d="${d(m2)}"/>`;
  s += note(x + w2 / 4, y + h2 - 24, 'Basalt', C.taupe, 'middle', 11) + note(x + 3 * w2 / 4, y + h2 - 24, 'Chalk', C.chalk, 'middle', 11);
}
// E — icons & small sizes
{
  const x = M + 2 * (w2 + G), y = y2;
  panel(x, y, w2, h2, C.chalk);
  s += label(x + 24, y + 34, 'APP ICON · SMALL SIZES');
  const tile = 112, r = 26, ty = y + 76;
  const t1 = x + w2 / 2 - tile - 10, t2 = x + w2 / 2 + 10;
  s += `<rect x="${t1}" y="${ty}" width="${tile}" height="${tile}" rx="${r}" fill="${C.night}"/>`;
  s += markPaths(placeMark(66, t1 + (tile - markW(66)) / 2, ty + (tile - 66) / 2), fragmentTones.dark);
  s += `<rect x="${t2}" y="${ty}" width="${tile}" height="${tile}" rx="${r}" fill="#FBF9F6" stroke="${C.oat}" stroke-width="1"/>`;
  s += markPaths(placeMark(66, t2 + (tile - markW(66)) / 2, ty + (tile - 66) / 2), fragmentTones.light);
  const sizes = [48, 32, 24, 16];
  let sx = x + 34;
  const sy = ty + tile + 46;
  const totalW = sizes.reduce((a, z) => a + markW(z), 0) + 3 * 26;
  sx = x + (w2 - totalW) / 2;
  for (const z of sizes) {
    s += markPaths(placeMark(z, sx, sy + (48 - z) / 2), fragmentTones.light);
    s += note(sx + markW(z) / 2, sy + 72, `${z}px`, C.stone, 'middle', 10);
    sx += markW(z) + 26;
  }
}
// F — palette
{
  const x = M + 3 * (w2 + G), y = y2;
  panel(x, y, w2, h2, C.chalk);
  s += label(x + 24, y + 34, 'PALETTE');
  const sw = [['Chalk', 'chalk'], ['Oat', 'oat'], ['Sand', 'sand'], ['Stone', 'stone'], ['Taupe', 'taupe'], ['Basalt', 'basalt']];
  const harms = [[[2, .07, .4], [3, .03, 1.9]], [[2, .06, 1.6], [3, .04, .3]], [[2, .08, 2.5], [3, .025, 1.1]], [[2, .05, .9], [3, .04, 2.6]], [[2, .07, 2.0], [3, .03, .6]], [[2, .06, .2], [3, .035, 1.4]]];
  sw.forEach(([name, key], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const cx = x + w2 / 6 + col * w2 / 3, cy = y + 104 + row * 128;
    const pts = stoneOutline({ r: 30, harm: harms[i], squash: 0.86, centre: [cx, cy], n: 180 });
    s += `<path d="${poly(pts)}" fill="${C[key]}"${key === 'chalk' ? ` stroke="${C.oat}" stroke-width="1"` : ''}/>`;
    s += note(cx, cy + 50, name, C.basalt, 'middle', 11.5);
    s += note(cx, cy + 66, C[key], C.stone, 'middle', 10);
  });
}

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W * 2}" height="${H * 2}">
<rect width="${W}" height="${H}" fill="#E9E3DA"/>
${s}
</svg>
`;
fs.writeFileSync(process.argv[2] ?? 'sheet.svg', svg);
