// Custom lowercase "flint" wordmark. Each letter is a set of monoline strokes (centre-line
// polylines) with flat terminals whose corners are softened, echoing the cut faces of the
// stone fragments in the mark.
import { deg, smin, smax, trace } from './geom.mjs';

// centre-line helpers
const line = (a, b, n = 2) => Array.from({ length: n }, (_, i) => [a[0] + (b[0] - a[0]) * i / (n - 1), a[1] + (b[1] - a[1]) * i / (n - 1)]);
const arc = (c, r, a0, a1, n = 90) => Array.from({ length: n + 1 }, (_, i) => { const a = (a0 + (a1 - a0) * i / n) * deg; return [c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]; });
const join = (...parts) => parts.reduce((acc, p) => acc.length ? acc.concat(p.slice(1)) : p.slice(), []);

// SDF of a stroke of width w along an open centre line, with flat (softened) end caps.
function strokeField(pts, w, soft) {
  const n = pts.length;
  let bx0 = Infinity, by0 = Infinity, bx1 = -Infinity, by1 = -Infinity;
  for (const [px, py] of pts) { bx0 = Math.min(bx0, px); by0 = Math.min(by0, py); bx1 = Math.max(bx1, px); by1 = Math.max(by1, py); }
  const t0 = norm2(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
  const t1 = norm2(pts[n - 1][0] - pts[n - 2][0], pts[n - 1][1] - pts[n - 2][1]);
  return (x, y) => {
    // far from this stroke's bounding box: a cheap lower bound is good enough
    const ox = Math.max(bx0 - x, 0, x - bx1), oy = Math.max(by0 - y, 0, y - by1);
    if (ox > w || oy > w) return Math.hypot(ox, oy) - w / 2;
    let best = Infinity;
    for (let i = 0; i < n - 1; i++) {
      const a = pts[i], b = pts[i + 1], ex = b[0] - a[0], ey = b[1] - a[1], wx = x - a[0], wy = y - a[1];
      let t = (wx * ex + wy * ey) / (ex * ex + ey * ey || 1e-12);
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      const d = Math.hypot(wx - ex * t, wy - ey * t);
      if (d < best) best = d;
    }
    let d = best - w / 2;
    // cap planes only act near their own end, so they never slice other parts of the stroke
    if (Math.hypot(x - pts[0][0], y - pts[0][1]) < w) d = smax(d, -((x - pts[0][0]) * t0[0] + (y - pts[0][1]) * t0[1]), soft);
    if (Math.hypot(x - pts[n - 1][0], y - pts[n - 1][1]) < w) d = smax(d, (x - pts[n - 1][0]) * t1[0] + (y - pts[n - 1][1]) * t1[1], soft);
    return d;
  };
}
function norm2(x, y) { const l = Math.hypot(x, y) || 1; return [x / l, y / l]; }

// A slightly irregular, tilted pebble for the tittle of the i.
function pebbleField(c, rx, ry, tilt) {
  const ct = Math.cos(tilt * deg), st = Math.sin(tilt * deg);
  return (x, y) => {
    const dx = x - c[0], dy = y - c[1], u = dx * ct + dy * st, v = -dx * st + dy * ct;
    const k = Math.hypot(u / rx, v / ry);
    return (k - 1) * Math.min(rx, ry);
  };
}

export function buildWordmark(M) {
  const { X, A, T, W, soft, crotch } = M;
  const strokes = [];
  const fields = [];
  // bars get a soft fillet where they cross a stem; everything else unions plainly
  const S = (pts, bar = false) => strokes.push({ pts, bar });
  // stem centre lines, set by stem-to-stem distances
  const xf = 0, xl = xf + M.dFL, xi = xl + M.dLI, xn = xi + M.dIN, xn2 = xn + 2 * M.nR, xt = xn2 + M.dNT;

  // f — stem rising into a hook that turns right over the top
  {
    const R = M.fHook, cy = -A + W / 2 + R;
    S(join(line([xf, 0], [xf, cy]), arc([xf + R, cy], R, 180, 180 + M.fSweep)));
    S(line([xf - M.barL, -X + W / 2], [xf + M.barR, -X + W / 2]), true);
  }
  // l
  S(line([xl, -A], [xl, 0]));
  // i, with a pebble for a tittle
  S(line([xi, -X], [xi, 0]));
  fields.push(pebbleField([xi + M.dotDx, -X - M.dotGap - M.dotR], M.dotR * M.dotAspect, M.dotR / M.dotAspect, M.dotTilt));
  // n — geometric arch springing from the stem
  {
    const R = M.nR, cy = -X - M.over + W / 2 + R;
    S(line([xn, -X], [xn, 0]));
    S(join(line([xn, cy + 12], [xn, cy]), arc([xn + R, cy], R, 180, 360), line([xn2, cy], [xn2, 0])));  // lead-in hides the cap inside the stem
  }
  // t — stem dropping into a foot that turns right, bookending the f
  {
    const R = M.tFoot, cy = -W / 2 - R + M.over;
    S(join(line([xt, -T], [xt, cy]), arc([xt + R, cy], R, 180, 180 - M.tSweep)));
    S(line([xt - M.barL, -X + W / 2], [xt + M.barR, -X + W / 2]), true);
  }
  const x = xt + Math.max(M.barR, M.tFoot * 1.6);
  const sf = strokes.filter(s => !s.bar).map(s => strokeField(s.pts, W, soft));
  const bars = strokes.filter(s => s.bar).map(s => strokeField(s.pts, W * (M.barW ?? 1), soft)); // bars a touch lighter, so they look equal
  const field = (px, py) => {
    let d = Infinity;
    for (const f of sf) d = Math.min(d, f(px, py));
    for (const f of bars) d = smin(d, f(px, py), crotch);
    for (const f of fields) d = Math.min(d, f(px, py));
    return d;
  };
  const width = x;
  const loops = trace(field, [xf - 40, -A - 20, width + 30, 30], M.step ?? 0.3, 0.02, 0.25).filter(l => Math.abs(l.area) > 20);
  return { loops, width, field };
}
