// Generates the "loam" logo: SVG sources plus PNG previews via a tiny built-in rasterizer.
import { writeFileSync, unlinkSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const PAL = {
  cream: '#F3EEE6', charcoal: '#3A3430',
  clay: '#B48A6E', sand: '#D8C3A5', stone: '#8E877C', moss: '#9A9A82',
};

// ---------- geometry ----------
function rng(seed) { return () => ((seed = (seed * 16807) % 2147483647) / 2147483647); }

// Organic petal: a teardrop whose radius wobbles with low-frequency harmonics.
function petal(cx, cy, angle, len, wid, seed) {
  const r = rng(seed), ph1 = r() * 6.28, ph2 = r() * 6.28;
  const pts = [];
  const N = 14;
  for (let i = 0; i < N; i++) {
    const t = (i / N) * Math.PI * 2;
    // teardrop: wide near the outer end, tapering toward the centre
    let x = Math.cos(t) * len;
    let y = Math.sin(t) * wid * (0.72 + 0.28 * Math.cos(t));
    const k = 1 + 0.05 * Math.sin(2 * t + ph1) + 0.035 * Math.sin(3 * t + ph2);
    x *= k; y *= k;
    const c = Math.cos(angle), s = Math.sin(angle);
    pts.push([cx + x * c - y * s, cy + x * s + y * c]);
  }
  return pts;
}

// Closed Catmull-Rom -> cubic beziers
function toBeziers(pts) {
  const n = pts.length, segs = [];
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    segs.push([p1,
      [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6],
      [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6], p2]);
  }
  return segs;
}
const f = v => +v.toFixed(2);
function bezPath(segs) {
  let d = `M${f(segs[0][0][0])} ${f(segs[0][0][1])}`;
  for (const [, c1, c2, p] of segs) d += `C${f(c1[0])} ${f(c1[1])} ${f(c2[0])} ${f(c2[1])} ${f(p[0])} ${f(p[1])}`;
  return d + 'Z';
}
function bezPoly(segs, steps = 24) {
  const out = [];
  for (const [a, b, c, d] of segs) for (let i = 0; i < steps; i++) {
    const t = i / steps, u = 1 - t;
    out.push([u*u*u*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t*t*t*d[0],
              u*u*u*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t*t*t*d[1]]);
  }
  return out;
}

// Mark in a 0..512 box: eccentric growth rings, like a cut stone or tree —
// each layer is generated from the previous one, drifting and slowly turning.
function mark(ox, oy, s, colors) {
  const items = [], L = colors.length;
  for (let i = 0; i < L; i++) {
    const t = i / (L - 1);
    const R = 214 - t * 168;
    const cx = 256 + t * 46, cy = 256 - t * 40;
    const N = 16, pts = [];
    for (let j = 0; j < N; j++) {
      const a = (j / N) * Math.PI * 2;
      const k = 1 + 0.06 * Math.sin(2 * a + 0.6 + t * 1.4) + 0.04 * Math.sin(3 * a + 2.1 - t * 0.9)
                  + 0.02 * Math.sin(5 * a + 0.3 + t * 2.0);
      pts.push([ox + (cx + Math.cos(a) * R * k * 1.04) * s, oy + (cy + Math.sin(a) * R * k * 0.96) * s]);
    }
    items.push({ kind: 'fill', segs: toBeziers(pts), color: colors[i], opacity: 1 });
  }
  return items;
}

// Wordmark "loam" built from round-capped strokes (x-height 100, baseline y).
function wordmark(x0, base, s, color) {
  const w = 17 * s, xh = 100 * s, R = 50 * s, items = [];
  const line = (x1, y1, x2, y2) => items.push({ kind: 'line', x1, y1, x2, y2, w, color });
  const arc = (cx, cy, r, a0, a1) => items.push({ kind: 'arc', cx, cy, r, a0, a1, w, color });
  let x = x0;
  // l  — tall stem with a soft foot curling right
  line(x, base - 150 * s, x, base); x += 38 * s;
  // o
  arc(x + R, base - R, R, 0, Math.PI * 2); x += 2 * R + 34 * s;
  // a  — bowl + right stem
  arc(x + R, base - R, R, 0, Math.PI * 2); line(x + 2 * R, base - xh, x + 2 * R, base); x += 2 * R + 34 * s;
  // m  — stem and two arches
  const r2 = 36 * s;
  line(x, base - xh, x, base);
  arc(x + r2, base - xh + r2, r2, Math.PI, Math.PI * 2); line(x + 2 * r2, base - xh + r2, x + 2 * r2, base);
  arc(x + 3 * r2, base - xh + r2, r2, Math.PI, Math.PI * 2); line(x + 4 * r2, base - xh + r2, x + 4 * r2, base);
  x += 4 * r2;
  return { items, width: x - x0 };
}

// ---------- SVG ----------
function svg(W, H, bg, items, title) {
  let body = '';
  for (const it of items) {
    if (it.kind === 'fill') body += `  <path d="${bezPath(it.segs)}" fill="${it.color}" fill-opacity="${it.opacity}"/>\n`;
    else if (it.kind === 'circle') body += `  <circle cx="${f(it.cx)}" cy="${f(it.cy)}" r="${f(it.r)}" fill="${it.color}"/>\n`;
    else if (it.kind === 'line') body += `  <path d="M${f(it.x1)} ${f(it.y1)}L${f(it.x2)} ${f(it.y2)}" stroke="${it.color}" stroke-width="${f(it.w)}" stroke-linecap="round" fill="none"/>\n`;
    else if (it.kind === 'arc') {
      const full = it.a1 - it.a0 >= Math.PI * 2 - 1e-6;
      if (full) body += `  <circle cx="${f(it.cx)}" cy="${f(it.cy)}" r="${f(it.r)}" stroke="${it.color}" stroke-width="${f(it.w)}" fill="none"/>\n`;
      else {
        const p = a => [it.cx + Math.cos(a) * it.r, it.cy + Math.sin(a) * it.r];
        const [sx, sy] = p(it.a0), [ex, ey] = p(it.a1);
        const large = it.a1 - it.a0 > Math.PI ? 1 : 0;
        body += `  <path d="M${f(sx)} ${f(sy)}A${f(it.r)} ${f(it.r)} 0 ${large} 1 ${f(ex)} ${f(ey)}" stroke="${it.color}" stroke-width="${f(it.w)}" stroke-linecap="round" fill="none"/>\n`;
      }
    }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${title}">\n  <title>${title}</title>\n` +
    (bg ? `  <rect width="${W}" height="${H}" fill="${bg}"/>\n` : '') + body + '</svg>\n';
}

// ---------- rasterizer ----------
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
function raster(W, H, bg, items, scale, file) {
  const w = Math.round(W * scale), h = Math.round(H * scale);
  const img = new Float32Array(w * h * 3), bc = hex(bg);
  for (let i = 0; i < w * h; i++) img.set(bc, i * 3);
  const blend = (i, c, a) => { for (let k = 0; k < 3; k++) img[i*3+k] += (c[k] - img[i*3+k]) * a; };
  const SS = 4, sCov = new Float32Array(w * h); let sCol = null;
  for (const it of items) {
    const col = hex(it.color);
    if (it.kind === 'fill' || it.kind === 'circle') {
      let poly;
      if (it.kind === 'fill') poly = bezPoly(it.segs);
      else poly = Array.from({ length: 256 }, (_, i) => [it.cx + Math.cos(i / 40.74) * it.r, it.cy + Math.sin(i / 40.74) * it.r]);
      poly = poly.map(([x, y]) => [x * scale, y * scale]);
      const cov = new Float32Array(w * h);
      for (let sy = 0; sy < h * SS; sy++) {
        const y = (sy + 0.5) / SS, xs = [];
        for (let i = 0; i < poly.length; i++) {
          const [ax, ay] = poly[i], [bx, by] = poly[(i + 1) % poly.length];
          if ((ay <= y) !== (by <= y)) xs.push(ax + (y - ay) / (by - ay) * (bx - ax));
        }
        xs.sort((a, b) => a - b);
        const row = Math.floor(sy / SS) * w;
        for (let i = 0; i + 1 < xs.length; i += 2)
          for (let sx = Math.ceil(xs[i] * SS - 0.5); (sx + 0.5) / SS < xs[i + 1]; sx++)
            if (sx >= 0 && sx < w * SS) cov[row + (sx / SS | 0)] += 1 / (SS * SS);
      }
      const op = it.opacity ?? 1;
      for (let i = 0; i < w * h; i++) if (cov[i] > 0) blend(i, col, cov[i] * op);
    } else {
      const hw = it.w * scale / 2, sc = scale; sCol = col;
      let x0, x1, y0, y1, dist;
      if (it.kind === 'line') {
        const ax = it.x1*sc, ay = it.y1*sc, bx = it.x2*sc, by = it.y2*sc, dx = bx-ax, dy = by-ay, L = dx*dx+dy*dy || 1;
        x0 = Math.min(ax, bx); x1 = Math.max(ax, bx); y0 = Math.min(ay, by); y1 = Math.max(ay, by);
        dist = (px, py) => { const t = Math.max(0, Math.min(1, ((px-ax)*dx + (py-ay)*dy) / L)); return Math.hypot(px-ax-t*dx, py-ay-t*dy); };
      } else {
        const cx = it.cx*sc, cy = it.cy*sc, r = it.r*sc;
        x0 = cx - r; x1 = cx + r; y0 = cy - r; y1 = cy + r;
        const full = it.a1 - it.a0 >= Math.PI * 2 - 1e-6;
        const pa = [cx + Math.cos(it.a0)*r, cy + Math.sin(it.a0)*r], pb = [cx + Math.cos(it.a1)*r, cy + Math.sin(it.a1)*r];
        dist = (px, py) => {
          let a = Math.atan2(py - cy, px - cx);
          if (!full) { while (a < it.a0) a += Math.PI * 2; if (a > it.a1) return Math.min(Math.hypot(px-pa[0], py-pa[1]), Math.hypot(px-pb[0], py-pb[1])); }
          return Math.abs(Math.hypot(px - cx, py - cy) - r);
        };
      }
      for (let y = Math.max(0, Math.floor(y0 - hw - 1)); y < Math.min(h, Math.ceil(y1 + hw + 1)); y++)
        for (let x = Math.max(0, Math.floor(x0 - hw - 1)); x < Math.min(w, Math.ceil(x1 + hw + 1)); x++) {
          const a = Math.max(0, Math.min(1, hw - dist(x + 0.5, y + 0.5) + 0.5));
          if (a > sCov[y * w + x]) sCov[y * w + x] = a;
        }
    }
  }
  if (sCol) for (let i = 0; i < w * h; i++) if (sCov[i] > 0) blend(i, sCol, sCov[i]);
  const buf = Buffer.alloc(w * h * 3);
  for (let i = 0; i < img.length; i++) buf[i] = Math.round(Math.max(0, Math.min(255, img[i])));
  const ppm = file + '.ppm';
  writeFileSync(ppm, Buffer.concat([Buffer.from(`P6\n${w} ${h}\n255\n`), buf]));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', ppm, file]);
  unlinkSync(ppm);
}

// ---------- compositions ----------
const out = 'output/';
const light = ['#E2D6C4', '#C9B293', '#A88B72', '#7E7468', PAL.charcoal];
const dark = ['#4A433D', '#6E6156', '#9C8470', '#C9B293', '#EFE6D8'];

// 1. Mark alone
const m = mark(46, 46, 0.82, light);
writeFileSync(out + 'loam-mark.svg', svg(512, 512, null, m, 'Loam mark'));
raster(512, 512, PAL.cream, m, 2, out + 'loam-mark.png');

// 2. Horizontal lockup
function lockup(W, H, colors, ink) {
  const ms = 0.54, gap = 64;
  const wmW = wordmark(0, 0, 1, ink).width, total = 512 * ms + gap + wmW, x0 = (W - total) / 2;
  const mark0 = mark(x0, (H - 512 * ms) / 2, ms, colors);
  const wm = wordmark(x0 + 512 * ms + gap, H / 2 + 50, 1, ink);
  return mark0.concat(wm.items);
}
const LW = 1000, LH = 400;
writeFileSync(out + 'loam-lockup.svg', svg(LW, LH, null, lockup(LW, LH, light, PAL.charcoal), 'Loam'));
raster(LW, LH, PAL.cream, lockup(LW, LH, light, PAL.charcoal), 1.6, out + 'loam-lockup.png');
raster(LW, LH, '#2E2A27', lockup(LW, LH, dark, PAL.cream), 1.6, out + 'loam-lockup-dark.png');
