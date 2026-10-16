// Geometry toolkit: signed distance fields -> marching squares -> cubic Bézier fitting.
// Shapes are designed as SDFs (so fillets, gaps and offsets are trivial), then traced
// and fitted back to compact, clean SVG paths.

export const deg = Math.PI / 180;
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const mul = (a, s) => [a[0] * s, a[1] * s];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
const len = a => Math.hypot(a[0], a[1]);
const norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l]; };

// ---------- smooth boolean ops ----------
export const smin = (a, b, k) => {
  if (k <= 0) return Math.min(a, b);
  const h = Math.max(k - Math.abs(a - b), 0) / k;
  return Math.min(a, b) - h * h * k / 4;
};
export const smax = (a, b, k) => -smin(-a, -b, k);

// ---------- curve sampling ----------
export function cubicPts(p0, p1, p2, p3, n = 64) {
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, u = 1 - t;
    out.push([
      u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
      u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
    ]);
  }
  return out;
}

// ---------- distance primitives (polygon / polyline), accelerated per grid ----------
// Signed distance to a closed polygon (negative inside).
export function polygonSDF(poly) {
  const n = poly.length;
  const ax = new Float64Array(n), ay = new Float64Array(n), ex = new Float64Array(n), ey = new Float64Array(n), ee = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    const a = poly[i], b = poly[(i + 1) % n];
    ax[i] = a[0]; ay[i] = a[1]; ex[i] = b[0] - a[0]; ey[i] = b[1] - a[1]; ee[i] = ex[i] * ex[i] + ey[i] * ey[i] || 1e-12;
  }
  return (x, y) => {
    let d = Infinity, inside = false;
    for (let i = 0; i < n; i++) {
      const wx = x - ax[i], wy = y - ay[i];
      let t = (wx * ex[i] + wy * ey[i]) / ee[i];
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      const dx = wx - ex[i] * t, dy = wy - ey[i] * t, dd = dx * dx + dy * dy;
      if (dd < d) d = dd;
      const y0 = ay[i], y1 = ay[i] + ey[i];
      if ((y0 > y) !== (y1 > y) && x < ax[i] + ex[i] * (y - y0) / (y1 - y0)) inside = !inside;
    }
    return inside ? -Math.sqrt(d) : Math.sqrt(d);
  };
}

// Distance to an open polyline with a per-vertex half-width (a tapered stroke).
export function strokeSDF(pts, halfW) {
  const n = pts.length;
  return (x, y) => {
    let best = Infinity;
    for (let i = 0; i < n - 1; i++) {
      const a = pts[i], b = pts[i + 1];
      const ex = b[0] - a[0], ey = b[1] - a[1], wx = x - a[0], wy = y - a[1];
      let t = (wx * ex + wy * ey) / (ex * ex + ey * ey || 1e-12);
      t = t < 0 ? 0 : t > 1 ? 1 : t;
      const d = Math.hypot(wx - ex * t, wy - ey * t) - (halfW[i] + (halfW[i + 1] - halfW[i]) * t);
      if (d < best) best = d;
    }
    return best;
  };
}

// ---------- field sampling + marching squares ----------
export function sampleField(fn, x0, y0, x1, y1, step) {
  const nx = Math.ceil((x1 - x0) / step) + 1, ny = Math.ceil((y1 - y0) / step) + 1;
  const v = new Float64Array(nx * ny);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) v[j * nx + i] = fn(x0 + i * step, y0 + j * step);
  return { v, nx, ny, x0, y0, step };
}

// Returns closed loops (arrays of [x,y]) of the zero level set, inside = negative.
export function contours(field) {
  const { v, nx, ny, x0, y0, step } = field;
  const key = (i, j, e) => `${i},${j},${e}`; // edge id: e=0 horizontal edge (i,j)-(i+1,j); e=1 vertical (i,j)-(i,j+1)
  const pt = new Map();
  const edgePoint = (i, j, e) => {
    const k = key(i, j, e);
    if (pt.has(k)) return k;
    const a = v[j * nx + i], b = e === 0 ? v[j * nx + i + 1] : v[(j + 1) * nx + i];
    const t = a / (a - b);
    pt.set(k, e === 0 ? [x0 + (i + t) * step, y0 + j * step] : [x0 + i * step, y0 + (j + t) * step]);
    return k;
  };
  const next = new Map();
  const link = (a, b) => next.set(a, b); // oriented so inside is on the left (consistent winding)
  for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
    const tl = v[j * nx + i], tr = v[j * nx + i + 1], br = v[(j + 1) * nx + i + 1], bl = v[(j + 1) * nx + i];
    const c = (tl < 0 ? 8 : 0) | (tr < 0 ? 4 : 0) | (br < 0 ? 2 : 0) | (bl < 0 ? 1 : 0);
    if (c === 0 || c === 15) continue;
    const T = () => edgePoint(i, j, 0), R = () => edgePoint(i + 1, j, 1), B = () => edgePoint(i, j + 1, 0), L = () => edgePoint(i, j, 1);
    const centre = (tl + tr + br + bl) / 4;
    switch (c) {
      case 1: link(L(), B()); break;
      case 2: link(B(), R()); break;
      case 3: link(L(), R()); break;
      case 4: link(R(), T()); break;
      case 5: if (centre < 0) { link(L(), T()); link(R(), B()); } else { link(L(), B()); link(R(), T()); } break;
      case 6: link(B(), T()); break;
      case 7: link(L(), T()); break;
      case 8: link(T(), L()); break;
      case 9: link(T(), B()); break;
      case 10: if (centre < 0) { link(T(), R()); link(B(), L()); } else { link(T(), L()); link(B(), R()); } break;
      case 11: link(T(), R()); break;
      case 12: link(R(), L()); break;
      case 13: link(R(), B()); break;
      case 14: link(B(), L()); break;
    }
  }
  const loops = [], seen = new Set();
  for (const start of next.keys()) {
    if (seen.has(start)) continue;
    const loop = [];
    let k = start;
    while (k !== undefined && !seen.has(k)) { seen.add(k); loop.push(pt.get(k)); k = next.get(k); }
    if (loop.length > 8) loops.push(loop);
  }
  return loops;
}

export const area = loop => loop.reduce((s, p, i) => { const q = loop[(i + 1) % loop.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0) / 2;
export const centroid = loop => {
  let cx = 0, cy = 0, a = 0;
  loop.forEach((p, i) => { const q = loop[(i + 1) % loop.length], c = p[0] * q[1] - q[0] * p[1]; a += c; cx += (p[0] + q[0]) * c; cy += (p[1] + q[1]) * c; });
  return [cx / (3 * a), cy / (3 * a)];
};

// Resample a closed loop at uniform arc length, with light smoothing to remove grid noise.
export function resample(loop, spacing) {
  const n = loop.length, cum = [0];
  for (let i = 1; i <= n; i++) cum.push(cum[i - 1] + len(sub(loop[i % n], loop[i - 1])));
  const total = cum[n], m = Math.max(12, Math.round(total / spacing)), out = [];
  let seg = 0;
  for (let k = 0; k < m; k++) {
    const s = k * total / m;
    while (cum[seg + 1] < s) seg++;
    const t = (s - cum[seg]) / (cum[seg + 1] - cum[seg] || 1);
    out.push(add(loop[seg], mul(sub(loop[(seg + 1) % n], loop[seg]), t)));
  }
  return out;
}

// Taubin (lambda|mu) smoothing: removes grid noise from a closed loop without shrinking it.
export function taubin(loop, iterations = 3, lambda = 0.5, mu = -0.53) {
  let pts = loop;
  for (let it = 0; it < iterations; it++) {
    for (const f of [lambda, mu]) {
      const n = pts.length;
      pts = pts.map((p, i) => {
        const a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n];
        return [p[0] + f * ((a[0] + b[0]) / 2 - p[0]), p[1] + f * ((a[1] + b[1]) / 2 - p[1])];
      });
    }
  }
  return pts;
}

// ---------- Schneider cubic fitting ----------
function bez(p, t) {
  const u = 1 - t;
  return add(add(mul(p[0], u * u * u), mul(p[1], 3 * u * u * t)), add(mul(p[2], 3 * u * t * t), mul(p[3], t * t * t)));
}
function bezD(p, t) {
  const u = 1 - t;
  return add(add(mul(sub(p[1], p[0]), 3 * u * u), mul(sub(p[2], p[1]), 6 * u * t)), mul(sub(p[3], p[2]), 3 * t * t));
}
function bezDD(p, t) {
  return add(mul(add(sub(p[2], mul(p[1], 2)), p[0]), 6 * (1 - t)), mul(add(sub(p[3], mul(p[2], 2)), p[1]), 6 * t));
}
function chordParams(pts) {
  const u = [0];
  for (let i = 1; i < pts.length; i++) u.push(u[i - 1] + len(sub(pts[i], pts[i - 1])));
  return u.map(x => x / u[u.length - 1]);
}
function generate(pts, u, t1, t2) {
  const p0 = pts[0], p3 = pts[pts.length - 1];
  let c00 = 0, c01 = 0, c11 = 0, x0 = 0, x1 = 0;
  u.forEach((t, i) => {
    const s = 1 - t, a1 = mul(t1, 3 * s * s * t), a2 = mul(t2, 3 * s * t * t);
    c00 += dot(a1, a1); c01 += dot(a1, a2); c11 += dot(a2, a2);
    const tmp = sub(pts[i], add(mul(p0, s * s * s + 3 * s * s * t), mul(p3, 3 * s * t * t + t * t * t)));
    x0 += dot(a1, tmp); x1 += dot(a2, tmp);
  });
  const det = c00 * c11 - c01 * c01, segLen = len(sub(p3, p0));
  let al = det ? (x0 * c11 - x1 * c01) / det : 0, ar = det ? (c00 * x1 - c01 * x0) / det : 0;
  if (al < 1e-6 * segLen || ar < 1e-6 * segLen) al = ar = segLen / 3;
  return [p0, add(p0, mul(t1, al)), add(p3, mul(t2, ar)), p3];
}
function maxErr(pts, bz, u) {
  let m = 0, at = pts.length >> 1;
  u.forEach((t, i) => { const d = len(sub(bez(bz, t), pts[i])); if (d > m) { m = d; at = i; } });
  return [m, at];
}
function reparam(pts, bz, u) {
  return u.map((t, i) => {
    const d = sub(bez(bz, t), pts[i]), d1 = bezD(bz, t), d2 = bezDD(bz, t);
    const den = dot(d1, d1) + dot(d, d2);
    return den ? Math.min(1, Math.max(0, t - dot(d, d1) / den)) : t;
  });
}
function fitCubic(pts, t1, t2, err, out) {
  if (pts.length === 2) {
    const d = len(sub(pts[1], pts[0])) / 3;
    out.push([pts[0], add(pts[0], mul(t1, d)), add(pts[1], mul(t2, d)), pts[1]]);
    return;
  }
  let u = chordParams(pts), bz = generate(pts, u, t1, t2), [e, split] = maxErr(pts, bz, u);
  if (e < err) { out.push(bz); return; }
  if (e < err * 4) {
    for (let k = 0; k < 20; k++) {
      u = reparam(pts, bz, u); bz = generate(pts, u, t1, t2); [e, split] = maxErr(pts, bz, u);
      if (e < err) { out.push(bz); return; }
    }
  }
  split = Math.min(Math.max(split, 1), pts.length - 2);
  const k = Math.min(3, split, pts.length - 1 - split);           // wider window -> steadier tangent
  const tc = norm(sub(pts[split - k], pts[split + k]));
  fitCubic(pts.slice(0, split + 1), t1, tc, err, out);
  fitCubic(pts.slice(split), mul(tc, -1), t2, err, out);
}

// Fit a closed loop. Corners (turning angle above cornerDeg) are kept sharp; elsewhere G1.
export function fitClosed(loop, err, cornerDeg = 50) {
  const n = loop.length;
  const turn = i => {
    const a = norm(sub(loop[i], loop[(i - 1 + n) % n])), b = norm(sub(loop[(i + 1) % n], loop[i]));
    return Math.acos(Math.max(-1, Math.min(1, dot(a, b)))) / deg;
  };
  let corners = [];
  for (let i = 0; i < n; i++) if (turn(i) > cornerDeg) corners.push(i);
  // start where the curve is flattest so the seam is invisible
  let start = corners.length ? corners[0] : 0;
  if (!corners.length) { let best = Infinity; for (let i = 0; i < n; i++) { const t = turn(i); if (t < best) { best = t; start = i; } } }
  const pts = [...loop.slice(start), ...loop.slice(0, start)];
  corners = corners.map(c => (c - start + n) % n).sort((a, b) => a - b);
  const breaks = corners.length ? [...corners, n] : [0, n];
  const out = [];
  const tanAt = (i, dir) => {
    const isCorner = corners.includes(i % n);
    if (isCorner) return dir > 0 ? norm(sub(pts[(i + 1) % n], pts[i % n])) : norm(sub(pts[(i - 1 + n) % n], pts[i % n]));
    const t = norm(sub(pts[(i + 3) % n], pts[(i - 3 + n) % n]));
    return dir > 0 ? t : mul(t, -1);
  };
  for (let k = 0; k < breaks.length - 1; k++) {
    const a = breaks[k], b = breaks[k + 1];
    const seg = [];
    for (let i = a; i <= b; i++) seg.push(pts[i % n]);
    fitCubic(seg, tanAt(a, 1), tanAt(b, -1), err, out);
  }
  return out;
}

export function pathData(curves, fmt = x => +x.toFixed(2)) {
  if (!curves.length) return '';
  let d = `M${fmt(curves[0][0][0])} ${fmt(curves[0][0][1])}`;
  for (const c of curves) d += `C${fmt(c[1][0])} ${fmt(c[1][1])} ${fmt(c[2][0])} ${fmt(c[2][1])} ${fmt(c[3][0])} ${fmt(c[3][1])}`;
  return d + 'Z';
}

// Convenience: field -> fitted loops with metadata
export function trace(fn, box, step, err = 0.06, spacing = 0.6, smooth = 0) {
  const field = sampleField(fn, box[0], box[1], box[2], box[3], step);
  return contours(field).map(loop => {
    const pts = smooth ? taubin(resample(loop, spacing), smooth) : resample(loop, spacing);
    return { loop: pts, area: area(pts), centroid: centroid(pts), curves: fitClosed(pts, err) };
  });
}

export { add, sub, mul, dot, len, norm };
