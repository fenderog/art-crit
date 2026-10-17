// The breaking wave, described in the frame that travels with the surfer.
//
// The wave crest runs along x. Its cross-section (z, y) is a Catmull-Rom curve
// through 16 control points. The control points morph along x through five
// "break stages": an unbroken shoulder ahead of the surfer, the steep pocket,
// the full barrel, the closing barrel and finally whitewater behind. Because
// the curve is parametric the lip can overhang and fold back into a tube.

import * as THREE from 'three';
import { smoothstep } from './geom.js';

export const WAVE_SCALE = 4.4;   // wave height in scene units (pelican ~1.2 tall)
export const SURF_SPEED = 7.0;   // surfer speed along the line, relative to the water
export const WAVE_SPEED = 2.2;   // shoreward speed of the wave
export const NPTS = 16;

// (z, y) per control point, in units of wave height. Index meaning:
// 0-3 back of wave, 4 crest, 5 lip top, 6 lip curve, 7 lip tip,
// 8-9 lip underside / tube ceiling, 10-12 face, 13 trough, 14-15 flat front.
const STAGES = [
  // 0: shoulder (unbroken)
  [[-7, 0], [-3.5, 0.04], [-1.8, 0.27], [-0.9, 0.56], [-0.35, 0.76], [0, 0.82], [0.18, 0.8], [0.32, 0.75],
    [0.42, 0.69], [0.52, 0.62], [0.62, 0.53], [0.76, 0.4], [1.0, 0.2], [1.5, 0.04], [2.8, 0], [7, 0]],
  // 1: pocket, lip starting to pitch
  [[-7, 0], [-3.5, 0.06], [-1.8, 0.35], [-0.8, 0.75], [-0.2, 1.0], [0.25, 1.05], [0.55, 0.98], [0.68, 0.86],
    [0.6, 0.8], [0.48, 0.76], [0.4, 0.66], [0.36, 0.45], [0.48, 0.18], [1.05, 0], [2.6, 0], [7, 0]],
  // 2: barrel
  [[-7, 0], [-3.5, 0.06], [-1.8, 0.36], [-0.8, 0.78], [-0.1, 1.05], [0.6, 1.0], [1.08, 0.66], [1.18, 0.28],
    [1.0, 0.5], [0.62, 0.86], [0.28, 0.76], [0.12, 0.5], [0.22, 0.2], [0.8, 0], [2.4, 0], [7, 0]],
  // 3: closing barrel / foam ball
  [[-7, 0], [-3.5, 0.05], [-1.8, 0.3], [-0.85, 0.62], [-0.15, 0.82], [0.5, 0.75], [1.1, 0.55], [1.6, 0.25],
    [1.45, 0.3], [1.2, 0.38], [0.95, 0.38], [0.9, 0.22], [1.3, 0.06], [2.2, 0], [3.2, 0], [7, 0]],
  // 4: whitewater
  [[-7, 0], [-3.5, 0.04], [-1.8, 0.2], [-0.9, 0.4], [-0.2, 0.55], [0.4, 0.58], [1.0, 0.5], [1.6, 0.36],
    [1.85, 0.3], [2.1, 0.22], [2.35, 0.15], [2.6, 0.1], [2.9, 0.05], [3.4, 0], [4.2, 0], [7, 0]],
];

export function stageAt(x) {
  return smoothstep(22, 5, x) + smoothstep(5, -3, x) + smoothstep(-3, -9, x) + smoothstep(-9, -16, x);
}

export function ampAt(x) {
  if (x > 14) return 1 - 0.82 * smoothstep(14, 110, x);
  if (x < -30) return 1 - 0.4 * smoothstep(-30, -160, x);
  return 1;
}

// the crest line bends gently towards the shore away from the peak
export function zoffAt(x) {
  return 12 * (1 - Math.exp(-(x * x) / 8000));
}

export function makePoints() {
  return Array.from({ length: NPTS }, () => [0, 0]);
}

export function profileAt(x, out) {
  const s = stageAt(x);
  const a = ampAt(x) * WAVE_SCALE;
  const zo = zoffAt(x);
  const i = Math.min(3, Math.floor(s));
  const f = s - i;
  const A = STAGES[i];
  const B = STAGES[i + 1];
  for (let k = 0; k < NPTS; k++) {
    out[k][0] = (A[k][0] + (B[k][0] - A[k][0]) * f) * a + zo;
    out[k][1] = (A[k][1] + (B[k][1] - A[k][1]) * f) * a;
  }
  return out;
}

// Centripetal Catmull-Rom (same formulation as THREE.CatmullRomCurve3)
const _p0 = [0, 0];
const _p3 = [0, 0];
function dist4(a, b) {
  const dx = a[0] - b[0], dy = a[1] - b[1];
  return Math.pow(dx * dx + dy * dy, 0.25);
}
export function crEval(pts, u, res) {
  const n = pts.length;
  let seg = Math.floor(u);
  if (seg > n - 2) seg = n - 2;
  if (seg < 0) seg = 0;
  const t = u - seg;
  const p1 = pts[seg];
  const p2 = pts[seg + 1];
  let p0, p3;
  if (seg > 0) p0 = pts[seg - 1];
  else { _p0[0] = 2 * p1[0] - p2[0]; _p0[1] = 2 * p1[1] - p2[1]; p0 = _p0; }
  if (seg + 2 < n) p3 = pts[seg + 2];
  else { _p3[0] = 2 * p2[0] - p1[0]; _p3[1] = 2 * p2[1] - p1[1]; p3 = _p3; }
  let d0 = dist4(p0, p1), d1 = dist4(p1, p2), d2 = dist4(p2, p3);
  if (d1 < 1e-4) d1 = 1;
  if (d0 < 1e-4) d0 = d1;
  if (d2 < 1e-4) d2 = d1;
  for (let c = 0; c < 2; c++) {
    let t1 = (p1[c] - p0[c]) / d0 - (p2[c] - p0[c]) / (d0 + d1) + (p2[c] - p1[c]) / d1;
    let t2 = (p2[c] - p1[c]) / d1 - (p3[c] - p1[c]) / (d1 + d2) + (p3[c] - p2[c]) / d2;
    t1 *= d1; t2 *= d1;
    const c0 = p1[c];
    const c2 = -3 * p1[c] + 3 * p2[c] - 2 * t1 - t2;
    const c3 = 2 * p1[c] - 2 * p2[c] + t1 + t2;
    const v = c0 + t1 * t + c2 * t * t + c3 * t * t * t;
    const dv = t1 + 2 * c2 * t + 3 * c3 * t * t;
    if (c === 0) { res.z = v; res.dz = dv; } else { res.y = v; res.dy = dv; }
  }
  return res;
}

const _pa = makePoints();
const _pb = makePoints();
const _ra = { z: 0, y: 0, dz: 0, dy: 0 };
const _rb = { z: 0, y: 0, dz: 0, dy: 0 };

export function makeSample() {
  return { pos: new THREE.Vector3(), normal: new THREE.Vector3(), tx: new THREE.Vector3(), tu: new THREE.Vector3(), stage: 0 };
}

// Surface point at line position x and profile parameter u (0..15).
export function surfaceSample(x, u, out) {
  const h = 0.04;
  profileAt(x, _pa);
  crEval(_pa, u, _ra);
  profileAt(x + h, _pb);
  crEval(_pb, u, _rb);
  out.pos.set(x, _ra.y, _ra.z);
  out.tu.set(0, _ra.dy, _ra.dz);
  out.tx.set(1, (_rb.y - _ra.y) / h, (_rb.z - _ra.z) / h);
  out.normal.crossVectors(out.tu, out.tx).normalize();
  out.stage = stageAt(x);
  return out;
}

// CPU twin of CHOP_GLSL
export function chopAt(x, y, z, t) {
  const px = x + SURF_SPEED * t;
  return 0.07 * Math.sin((px * 0.55 + z * 0.835) * 0.95 + t * 1.6)
    + 0.05 * Math.sin((px * -0.62 + z * 0.785) * 1.45 + y * 0.4 + t * 2.05)
    + 0.03 * Math.sin((px * 0.96 + z * -0.28) * 2.2 + y * 0.6 + t * 2.7);
}
