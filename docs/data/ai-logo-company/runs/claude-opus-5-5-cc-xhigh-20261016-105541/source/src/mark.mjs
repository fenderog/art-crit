// The Flint mark: one river-stone silhouette, split into four fragments by fine
// fissures that radiate from a four-point spark held in the negative space.
import { deg, smax, cubicPts, polygonSDF, strokeSDF, trace } from './geom.mjs';

const rotP = ([x, y], a) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];

// Organic stone outline: low harmonics only, so it reads as a pebble rather than a splat.
export function stoneOutline({ r, harm, squash = 1, centre = [0, 0], n = 720 }) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const t = (i / n) * 2 * Math.PI;
    const k = 1 + harm.reduce((s, [m, a, p]) => s + a * Math.cos(m * t - p), 0);
    pts.push([centre[0] + r * k * Math.cos(t), centre[1] + r * k * Math.sin(t) * squash]);
  }
  return pts;
}

// Four-point spark whose tips are already one fissure wide: each concave side leaves a tip
// running parallel to the axis at ±w/2, so the fissures continue it with no seam.
export function sparkOutline({ tips, c, rot = 0, centre = [0, 0] }, w) {
  const h = w / 2;
  const corners = [ // [start, end] of each side, in the un-rotated frame (y down)
    [[h, -tips[0]], [tips[1], -h]],
    [[tips[1], h], [h, tips[2]]],
    [[-h, tips[2]], [-tips[3], h]],
    [[-tips[3], -h], [-h, -tips[0]]],
  ];
  const pts = [];
  for (const [A, B] of corners) {
    // control points slide along the tip axes toward the centre
    const aAxis = Math.abs(A[0]) === h ? [A[0], A[1] * (1 - c)] : [A[0] * (1 - c), A[1]];
    const bAxis = Math.abs(B[0]) === h ? [B[0], B[1] * (1 - c)] : [B[0] * (1 - c), B[1]];
    pts.push(...cubicPts(A, aAxis, bAxis, B, 120));
  }
  const tipPts = [[0, -tips[0]], [tips[1], 0], [0, tips[2]], [-tips[3], 0]];
  const place = p => { const q = rotP(p, rot * deg); return [q[0] + centre[0], q[1] + centre[1]]; };
  const dirs = tipPts.map(p => { const q = rotP(p, rot * deg); return Math.atan2(q[1], q[0]); });
  return { pts: pts.map(place), tips: tipPts.map(place), dirs };
}

// Fissure: starts just inside a spark tip, leaves along the tip axis and slowly turns
// (curvature grows from zero, so the join with the spark stays perfectly smooth).
function fissure(tip, dir, { bend, reach, w, n = 64 }) {
  const back = 3;
  const pts = [[tip[0] - Math.cos(dir) * back, tip[1] - Math.sin(dir) * back], [...tip]];
  let p = [...tip];
  for (let i = 1; i <= n; i++) {
    const s = (i - 0.5) / n, a = dir + bend * deg * s * s;
    p = [p[0] + Math.cos(a) * reach / n, p[1] + Math.sin(a) * reach / n];
    pts.push(p);
  }
  return { pts, hw: pts.map(() => w / 2) };
}

export function buildMark(P) {
  const stone = stoneOutline(P.stone);
  const spark = sparkOutline(P.spark, P.fissure.w);
  const dStone = polygonSDF(stone);
  const dSpark = polygonSDF(spark.pts);
  const fissures = spark.tips.map((t, i) => fissure(t, spark.dirs[i], P.fissure));
  const dFis = fissures.map(f => strokeSDF(f.pts, f.hw));
  const field = (x, y) => {
    let cut = dSpark(x, y);
    for (const d of dFis) cut = Math.min(cut, d(x, y));
    return smax(dStone(x, y), -cut, P.edgeRound);
  };
  const loops = trace(field, P.box, P.step, P.fitErr ?? 0.04, P.spacing ?? 0.5).filter(l => Math.abs(l.area) > 50);
  // order fragments clockwise starting top-left: TL, TR, BR, BL
  loops.forEach(l => { l.angle = (Math.atan2(l.centroid[1], l.centroid[0]) + 2 * Math.PI + Math.PI) % (2 * Math.PI); });
  loops.sort((a, b) => a.angle - b.angle);
  return { fragments: loops, stone, spark, fissures: fissures.map(f => f.pts.slice(1)), field };
}
