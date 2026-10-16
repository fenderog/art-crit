// Logo reveal: a whole pebble cracks from the centre, the spark opens in the negative space,
// the fragments settle into their tones, then the wordmark arrives.
// Frames are rasterised straight from the signed distance fields and piped to ffmpeg.
// Usage: node src/reveal.mjs out.mp4 [tagline.png]
import { spawn } from 'node:child_process';
import { smax, cubicPts, polygonSDF, strokeSDF, sampleField, deg } from './geom.mjs';
import { stoneOutline, sparkOutline } from './mark.mjs';
import { buildWordmark } from './wordmark.mjs';
import { geometry, LOCKUP } from './build.mjs';
import { palette, markParams as P, wordParams, fragmentTones } from './design.mjs';

const out = process.argv[2] ?? 'reveal.mp4';  // (or --stills sheet.png)
const tagline = process.argv[3];
const FW = 1920, FH = 1080, FPS = 30, DUR = 7.0, N = Math.round(FPS * DUR);
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const BG = hex(palette.chalk), INK = hex(palette.basalt), BASE = hex('#9C8F80');
const TONES = fragmentTones.light.map(k => hex(palette[k]));

// ---------- easing ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const inOut = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const outCubic = x => 1 - Math.pow(1 - x, 3);
const outBack = (x, s = 1.4) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
const lerp = (a, b, t) => a + (b - a) * t;

// ---------- static geometry ----------
const { markBox, wordBox } = geometry;
const stoneD = (() => { // stone SDF sampled once on a fine grid, bilinear lookups per pixel
  const [x0, y0, x1, y1] = [-115, -112, 115, 112], step = 0.25;
  const f = sampleField(polygonSDF(stoneOutline(P.stone)), x0, y0, x1, y1, step);
  return (x, y) => {
    const gx = (x - x0) / step, gy = (y - y0) / step;
    if (gx < 0 || gy < 0 || gx >= f.nx - 1 || gy >= f.ny - 1) return 20;
    const i = gx | 0, j = gy | 0, fx = gx - i, fy = gy - j, v = f.v, n = f.nx;
    return (v[j * n + i] * (1 - fx) + v[j * n + i + 1] * fx) * (1 - fy) + (v[(j + 1) * n + i] * (1 - fx) + v[(j + 1) * n + i + 1] * fx) * fy;
  };
})();

// Full fissure centre lines (centre -> final tip -> curved path), revealed by arc length.
const finalSpark = sparkOutline(P.spark, P.fissure.w);
const fissureLines = finalSpark.tips.map((tip, i) => {
  const dir = finalSpark.dirs[i], pts = [[0, 0]];
  const r = Math.hypot(tip[0], tip[1]);
  for (let k = 1; k <= 12; k++) pts.push([Math.cos(dir) * r * k / 12, Math.sin(dir) * r * k / 12]);
  let p = [...tip];
  for (let k = 1; k <= 64; k++) {
    const s = (k - 0.5) / 64, a = dir + P.fissure.bend * deg * s * s;
    p = [p[0] + Math.cos(a) * P.fissure.reach / 64, p[1] + Math.sin(a) * P.fissure.reach / 64];
    pts.push(p);
  }
  return pts;
});
const truncate = (pts, L) => {
  const outPts = [pts[0]];
  let acc = 0;
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    if (acc + d >= L) { const t = (L - acc) / d; outPts.push([lerp(pts[i - 1][0], pts[i][0], t), lerp(pts[i - 1][1], pts[i][1], t)]); return outPts; }
    acc += d; outPts.push(pts[i]);
  }
  return outPts;
};
// angle of each fissure as a function of radius, for colouring fragments by sector
const fissureAngleAt = fissureLines.map(pts => {
  const polar = pts.slice(1).map(([x, y]) => [Math.hypot(x, y), Math.atan2(y, x)]);
  return r => {
    if (r <= polar[0][0]) return polar[0][1];
    for (let i = 1; i < polar.length; i++) if (polar[i][0] >= r) {
      const t = (r - polar[i - 1][0]) / (polar[i][0] - polar[i - 1][0]);
      let a0 = polar[i - 1][1], a1 = polar[i][1];
      if (a1 - a0 > Math.PI) a1 -= 2 * Math.PI; if (a0 - a1 > Math.PI) a1 += 2 * Math.PI;
      return a0 + (a1 - a0) * t;
    }
    return polar[polar.length - 1][1];
  };
});
const wrap = a => ((a % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
// fissures are N, E, S, W; fragment between W->N is TL(0), N->E TR(1), E->S BR(2), S->W BL(3)
const sectorOf = (x, y) => {
  const r = Math.hypot(x, y), a = Math.atan2(y, x);
  const f = fissureAngleAt.map(fn => fn(r));
  for (let i = 0; i < 4; i++) {
    const lo = f[(i + 3) % 4], span = wrap(f[i] - lo);
    if (wrap(a - lo) < span) return i;
  }
  return 0;
};

// ---------- layout (final lockup centred in frame) ----------
const xh = 150;
const mh = LOCKUP.markH * xh, sFinal = mh / markBox.h;
const markWpx = markBox.w * sFinal, wordWpx = wordBox.w / wordParams.X * xh;
const contentW = markWpx + LOCKUP.gap * xh + wordWpx;
const left = (FW - contentW) / 2, top = (FH - mh) / 2 - 34;
const originFinal = [left - markBox.x0 * sFinal, top - markBox.y0 * sFinal];
const sStart = sFinal * 1.32;
const originStart = [FW / 2 - (markBox.x0 + markBox.w / 2) * sStart, FH / 2 - (markBox.y0 + markBox.h / 2) * sStart];
const wordX = left + markWpx + LOCKUP.gap * xh, baseline = top + mh / 2 + xh / 2 - 0.06 * xh;
const tagY = Math.round(top + mh + 64);

// wordmark SDF on the pixel grid (in px), sampled with a sub-pixel slide offset
const word = (() => {
  const w = buildWordmark({ ...wordParams, step: 2 }); // field only; the coarse trace is discarded
  const s = xh / wordParams.X;
  const x0 = Math.floor(wordX - 80), y0 = Math.floor(baseline + (wordBox.y0 - 10) / wordParams.X * xh * 1.0 - 10);
  const x1 = Math.ceil(wordX + wordWpx + 20), y1 = Math.ceil(baseline + 40);
  const gw = x1 - x0 + 1, gh = y1 - y0 + 1, v = new Float32Array(gw * gh);
  for (let j = 0; j < gh; j++) for (let i = 0; i < gw; i++) {
    const ux = (x0 + i + 0.5 - wordX) / s + wordBox.x0, uy = (y0 + j + 0.5 - baseline) / s;
    v[j * gw + i] = w.field(ux, uy) * s;
  }
  return { x0, y0, gw, gh, v };
})();

// ---------- frame rendering ----------
function renderFrame(t) {
  const buf = Buffer.alloc(FW * FH * 3);
  for (let i = 0; i < FW * FH; i++) { buf[i * 3] = BG[0]; buf[i * 3 + 1] = BG[1]; buf[i * 3 + 2] = BG[2]; }

  // timeline
  const appear = outCubic(seg(t, 0.0, 0.9));
  const crack = inOut(seg(t, 0.9, 1.8));
  const open = seg(t, 1.55, 2.75);
  const tone = inOut(seg(t, 1.7, 2.9));
  const move = inOut(seg(t, 3.0, 4.0));
  const wordIn = outCubic(seg(t, 3.85, 4.85));

  const sc = lerp(sStart, sFinal, move) * lerp(0.86, 1, appear);
  const ox = lerp(originStart[0], originFinal[0], move), oy = lerp(originStart[1], originFinal[1], move);
  const alpha = appear;
  const w = crack > 0 ? lerp(0.9, 2.0, crack) + (P.fissure.w - 2.0) * outCubic(open) : 0;
  const L = crack * 230;
  const sig = open > 0 ? outBack(open, 1.25) : 0;
  const tips = P.spark.tips.map(v => v * sig);
  const spark = sig > 0 && Math.min(...tips) > w / 2 + 0.6 ? sparkOutline({ ...P.spark, tips }, w) : null;
  const dSpark = spark ? polygonSDF(spark.pts) : null;
  const maxTip = Math.max(...tips);
  const dFis = crack > 0 ? fissureLines.map(f => { const p = truncate(f, L); return p.length > 1 ? strokeSDF(p, p.map(() => w / 2)) : null; }).filter(Boolean) : [];
  const cols = TONES.map(c => c.map((v, k) => lerp(BASE[k], v, tone)));

  // mark pixels
  const bx0 = Math.max(0, Math.floor(ox + markBox.x0 * sc - 4)), bx1 = Math.min(FW - 1, Math.ceil(ox + markBox.x1 * sc + 4));
  const by0 = Math.max(0, Math.floor(oy + markBox.y0 * sc - 4)), by1 = Math.min(FH - 1, Math.ceil(oy + markBox.y1 * sc + 4));
  for (let py = by0; py <= by1; py++) for (let px = bx0; px <= bx1; px++) {
    const x = (px + 0.5 - ox) / sc, y = (py + 0.5 - oy) / sc;
    const ds = stoneD(x, y);
    if (ds * sc > 1.5) continue;
    let cut = Infinity;
    for (const f of dFis) cut = Math.min(cut, f(x, y));
    if (dSpark) { const r = Math.hypot(x, y); if (r - maxTip < cut) cut = Math.min(cut, dSpark(x, y)); }
    const field = cut === Infinity ? ds : smax(ds, -cut, P.edgeRound);
    const a = clamp(0.5 - field * sc) * alpha;
    if (a <= 0) continue;
    const c = cols[sectorOf(x, y)], o = (py * FW + px) * 3;
    for (let k = 0; k < 3; k++) buf[o + k] = Math.round(buf[o + k] * (1 - a) + c[k] * a);
  }

  // wordmark
  if (wordIn > 0) {
    const dx = (1 - wordIn) * 46;
    for (let j = 0; j < word.gh; j++) for (let i = 0; i < word.gw; i++) {
      const gx = i - dx; if (gx < 0) continue;
      const i0 = Math.floor(gx), fx = gx - i0; if (i0 + 1 >= word.gw) continue;
      const d = word.v[j * word.gw + i0] * (1 - fx) + word.v[j * word.gw + i0 + 1] * fx;
      const a = clamp(0.5 - d) * wordIn;
      if (a <= 0) continue;
      const px = word.x0 + i, py = word.y0 + j;
      if (px < 0 || px >= FW || py < 0 || py >= FH) continue;
      const o = (py * FW + px) * 3;
      for (let k = 0; k < 3; k++) buf[o + k] = Math.round(buf[o + k] * (1 - a) + INK[k] * a);
    }
  }
  return buf;
}

// ---------- stills (contact sheet for checking key moments) ----------
if (process.argv[2] === '--stills') {
  const times = [0.5, 1.4, 1.9, 2.3, 3.0, 3.8, 4.4, 6.5];
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', `${FW}x${FH}`, '-i', '-',
    '-vf', 'scale=640:-1,tile=4x2:padding=6:color=white', '-frames:v', '1', process.argv[3]], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (const t of times) ff.stdin.write(renderFrame(t));
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  process.exit(0);
}

// ---------- encode ----------
const args = ['-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', `${FW}x${FH}`, '-r', `${FPS}`, '-i', '-'];
if (tagline) {
  args.push('-loop', '1', '-framerate', `${FPS}`, '-i', tagline,
    '-filter_complex', `[1:v]format=rgba,fade=t=in:st=4.9:d=0.8:alpha=1[tg];[0:v][tg]overlay=x=(W-w)/2:y=${tagY}:shortest=1,format=yuv420p[v]`, '-map', '[v]');
} else args.push('-pix_fmt', 'yuv420p');
args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-movflags', '+faststart', '-t', `${DUR}`, out);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let f = 0; f < N; f++) {
  const frame = renderFrame(f / FPS);
  if (!ff.stdin.write(frame)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 30 === 0) console.log(`frame ${f}/${N}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
console.log('wrote', out);
