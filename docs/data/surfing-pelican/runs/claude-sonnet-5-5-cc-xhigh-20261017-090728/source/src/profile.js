// Cross-section ("profile") of the breaking wave.
//
// A profile is a polyline in the (q, y) plane, q pointing towards the shore.
// It is walked from the offshore back of the wave, over the crest, along the
// outside of the lip, around its tip, back along the underside of the lip,
// down the inner wall of the barrel and out over the floor. Three keyframes
// (mellow shoulder, pitching lip, full barrel) share one index layout so they
// can be blended point by point; the vertex shader does exactly that.

export const NA = 36; // back slope
export const NB = 30; // outside of the lip
export const NC = 6; // rounded tip of the lip
export const ND = 60; // underside of the lip + inner wall of the barrel
export const NE = 28; // floor
export const NS = NA + NB + NC + ND + NE;
export const REG = { A: 0, B: NA, C: NA + NB, D: NA + NB + NC, E: NA + NB + NC + ND };

const DEG = Math.PI / 180;
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};

function newKey() {
  return {
    q: new Float32Array(NS),
    y: new Float32Array(NS),
    arc: new Float32Array(NS),
    thick: new Float32Array(NS),
    ao: new Float32Array(NS),
    foam: new Float32Array(NS),
    region: new Float32Array(NS),
  };
}

function finishKey(k) {
  let a = 0;
  for (let i = 0; i < NS; i++) {
    if (i > 0) a += Math.hypot(k.q[i] - k.q[i - 1], k.y[i] - k.y[i - 1]);
    k.arc[i] = a;
  }
  for (let i = 0; i < NS; i++) {
    k.region[i] = i < REG.B ? 0 : i < REG.C ? 1 : i < REG.D ? 2 : i < REG.E ? 3 : 4;
  }
  return k;
}

// back slope: power-law rise that meets the crest with the requested slope
function backSlope(k, qc, yc, slope, Q0) {
  const pw = 1.8;
  const a = Math.max((yc * pw) / Math.max(slope, 0.05), 0.5);
  const tail = Math.pow(1 + (qc + Q0) / a, -pw);
  for (let j = 0; j < NA; j++) {
    const t = j / NA;
    const q = qc - (qc + Q0) * Math.pow(1 - t, 3.0);
    const y = (yc * (Math.pow(1 + (qc - q) / a, -pw) - tail)) / (1 - tail);
    k.q[j] = q;
    k.y[j] = Math.max(y, 0);
  }
}

function floorRun(k, qStart, yb, Qf) {
  for (let j = 0; j < NE; j++) {
    const t = (j + 1) / NE;
    const q = qStart + (Qf - qStart) * Math.pow(t, 1.7);
    const d = q - qStart;
    k.q[REG.E + j] = q;
    k.y[REG.E + j] = yb * Math.exp(-(d * d) / (2.6 * 2.6));
  }
}

// ---------------------------------------------------------------- barrel ----
function polarKey(P) {
  const k = newKey();
  const cy = P.yb + P.ry;
  const phiT = P.phiT * DEG;
  const phiC = P.phiC * DEG;
  const inner = (phi) => [P.cq + P.rq * Math.cos(phi), cy + P.ry * Math.sin(phi)];
  const nrm = (phi) => {
    const nx = Math.cos(phi) / P.rq;
    const ny = Math.sin(phi) / P.ry;
    const l = Math.hypot(nx, ny);
    return [nx / l, ny / l];
  };
  const tan = (phi) => {
    const tx = -P.rq * Math.sin(phi);
    const ty = P.ry * Math.cos(phi);
    const l = Math.hypot(tx, ty);
    return [tx / l, ty / l];
  };
  const thickAt = (phi) => {
    const u = clamp((phi - phiT) / (phiC - phiT), 0, 1);
    return P.Ttip + (P.Tc - P.Ttip) * Math.pow(u, P.wExp);
  };
  const T_N = 0.45;

  // crest point and slope of the back
  const nC = nrm(phiC);
  const iC = inner(phiC);
  const tc = thickAt(phiC);
  const qc = iC[0] + nC[0] * tc;
  const yc = iC[1] + nC[1] * tc;
  const tC = tan(phiC);
  const slope = Math.max(-tC[1] / Math.max(-tC[0], 1e-3), 0.12);
  backSlope(k, qc, yc, P.backSlope ?? slope, P.Q0);
  for (let j = 0; j < NA; j++) {
    const d = qc - k.q[j];
    k.thick[j] = clamp((tc + 0.22 * d) / T_N, 0, 1);
    k.foam[j] = 0;
    k.ao[j] = 0;
  }

  // outside of lip: crest -> tip (phi decreasing)
  for (let j = 0; j < NB; j++) {
    const u = j / (NB - 1);
    const phi = phiC + (phiT - phiC) * u;
    const p = inner(phi);
    const n = nrm(phi);
    const th = thickAt(phi);
    k.q[REG.B + j] = p[0] + n[0] * th;
    k.y[REG.B + j] = p[1] + n[1] * th;
    k.thick[REG.B + j] = clamp(th / T_N, 0, 1);
    k.foam[REG.B + j] = 0.1 * (1 - u) + 0.55 * Math.pow(u, 4);
    k.ao[REG.B + j] = 0;
  }

  // tip cap
  {
    const p = inner(phiT);
    const n = nrm(phiT);
    const t = tan(phiT);
    const cx = p[0] + n[0] * P.Ttip * 0.5;
    const cyc = p[1] + n[1] * P.Ttip * 0.5;
    for (let j = 0; j < NC; j++) {
      const b = (Math.PI * (j + 1)) / (NC + 1);
      const r = P.Ttip * 0.5;
      k.q[REG.C + j] = cx + r * (Math.cos(b) * n[0] - Math.sin(b) * t[0]);
      k.y[REG.C + j] = cyc + r * (Math.cos(b) * n[1] - Math.sin(b) * t[1]);
      k.thick[REG.C + j] = clamp(P.Ttip / T_N, 0, 1);
      k.foam[REG.C + j] = 0.7;
      k.ao[REG.C + j] = 0.1;
    }
  }

  // underside + inner wall: tip -> floor (phi increasing to 270 deg)
  const phiE = 270 * DEG;
  for (let j = 0; j < ND; j++) {
    const u = j / (ND - 1);
    const phi = phiT + (phiE - phiT) * u;
    const p = inner(phi);
    k.q[REG.D + j] = p[0];
    k.y[REG.D + j] = p[1];
    const th = phi <= phiC ? thickAt(phi) : P.Tc + (phi - phiC) * 0.45;
    k.thick[REG.D + j] = clamp(th / T_N, 0, 1);
    k.foam[REG.D + j] = 0.35 * Math.pow(1 - u, 3) + 0.1 * smooth(0.85, 1, u);
    const deg = phi / DEG;
    k.ao[REG.D + j] = P.ao * smooth(phiT / DEG, phiT / DEG + 110, deg) * (1 - 0.55 * smooth(215, 270, deg));
  }

  // floor
  const tipQ = k.q[REG.C + 2];
  floorRun(k, P.cq, P.yb, P.Qf);
  for (let j = 0; j < NE; j++) {
    const q = k.q[REG.E + j];
    const splash = Math.exp(-Math.pow((q - tipQ) / 1.1, 2)) * P.splash;
    const wash = (q > tipQ - 0.2 ? Math.exp(-(q - tipQ + 0.2) / 3.2) : 1) * 0.5 * P.splash;
    const under = (q < tipQ ? 0.25 : 0) * P.splash;
    k.thick[REG.E + j] = 1;
    k.foam[REG.E + j] = clamp(Math.max(splash, wash, under) + 0.05, 0, 1);
    k.ao[REG.E + j] = q < tipQ ? P.ao * 0.45 * (1 - smooth(P.cq, tipQ, q) * 0.7) : 0;
  }
  return finishKey(k);
}

// -------------------------------------------------------------- shoulder ----
function bez(p0, p1, p2, p3, t) {
  const u = 1 - t;
  const b0 = u * u * u;
  const b1 = 3 * u * u * t;
  const b2 = 3 * u * t * t;
  const b3 = t * t * t;
  return [
    b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0],
    b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1],
  ];
}

function mellowKey(P) {
  const k = newKey();
  const qc = P.qc;
  const yc = P.yc;
  const T_N = 0.45;
  backSlope(k, qc, yc, P.backSlope, P.Q0);
  for (let j = 0; j < NA; j++) {
    k.thick[j] = clamp((0.12 + 0.22 * (qc - k.q[j])) / T_N, 0, 1);
    k.foam[j] = 0;
    k.ao[j] = 0;
  }
  const bd = [Math.cos(Math.atan(P.backSlope)), Math.sin(Math.atan(P.backSlope))];
  const fd = [Math.cos(-P.faceAng * DEG), Math.sin(-P.faceAng * DEG)];
  const pc = [qc, yc];
  const pt = [qc + P.round, yc - P.round * 0.32];
  // crest rounding
  for (let j = 0; j < NB; j++) {
    const u = j / (NB - 1);
    const a = P.round * 0.55;
    const p = bez(pc, [pc[0] + bd[0] * a, pc[1] + bd[1] * a], [pt[0] - fd[0] * a, pt[1] - fd[1] * a], pt, u);
    k.q[REG.B + j] = p[0];
    k.y[REG.B + j] = p[1];
    k.thick[REG.B + j] = clamp((0.12 + 0.1 * u) / T_N, 0, 1);
    k.foam[REG.B + j] = 0.05 + 0.25 * u * u;
    k.ao[REG.B + j] = 0;
  }
  for (let j = 0; j < NC; j++) {
    const s = (0.04 * (j + 1)) / NC;
    k.q[REG.C + j] = pt[0] + fd[0] * s;
    k.y[REG.C + j] = pt[1] + fd[1] * s;
    k.thick[REG.C + j] = 0.3;
    k.foam[REG.C + j] = 0.3;
    k.ao[REG.C + j] = 0;
  }
  const ps = [pt[0] + fd[0] * 0.04, pt[1] + fd[1] * 0.04];
  const pf = [P.cq, P.yb];
  const chord = Math.hypot(pf[0] - ps[0], pf[1] - ps[1]);
  for (let j = 0; j < ND; j++) {
    const u = j / (ND - 1);
    const p = bez(
      ps,
      [ps[0] + fd[0] * chord * 0.42, ps[1] + fd[1] * chord * 0.42],
      [pf[0] - chord * 0.5, pf[1]],
      pf,
      u,
    );
    k.q[REG.D + j] = p[0];
    k.y[REG.D + j] = p[1];
    k.thick[REG.D + j] = clamp((0.2 + 0.7 * u) / T_N, 0, 1);
    k.foam[REG.D + j] = 0.25 * Math.pow(1 - u, 4) + 0.04;
    k.ao[REG.D + j] = P.ao * smooth(0, 0.7, u) * (1 - smooth(0.7, 1, u));
  }
  floorRun(k, P.cq, P.yb, P.Qf);
  for (let j = 0; j < NE; j++) {
    k.thick[REG.E + j] = 1;
    k.foam[REG.E + j] = 0.04 + 0.12 * Math.exp(-Math.pow((k.q[REG.E + j] - P.cq) / 2.2, 2));
    k.ao[REG.E + j] = 0;
  }
  return finishKey(k);
}

// Keyframes: 0 = mellow shoulder, 1 = pitching lip, 2 = full barrel.
export function buildKeyframes() {
  const S = mellowKey({
    qc: -0.3,
    yc: 0.78,
    backSlope: 0.3,
    round: 0.85,
    faceAng: 34,
    cq: 3.8,
    yb: -0.05,
    Q0: 74,
    Qf: 74,
    ao: 0.05,
  });
  const M = polarKey({
    cq: 2.5,
    rq: 1.55,
    ry: 0.58,
    yb: -0.06,
    phiT: 62,
    phiC: 138,
    Ttip: 0.05,
    Tc: 0.2,
    wExp: 1.1,
    Q0: 74,
    Qf: 74,
    ao: 0.55,
    splash: 0.6,
  });
  const B = polarKey({
    cq: 2.0,
    rq: 0.74,
    ry: 0.62,
    yb: -0.06,
    phiT: -16,
    phiC: 126,
    Ttip: 0.045,
    Tc: 0.27,
    wExp: 1.25,
    Q0: 74,
    Qf: 74,
    ao: 1.0,
    splash: 1.0,
  });
  return [S, M, B];
}

// Pack keyframes into two float textures' worth of data (rows = keyframes).
export function packKeyframes(keys) {
  const t0 = new Float32Array(NS * keys.length * 4);
  const t1 = new Float32Array(NS * keys.length * 4);
  keys.forEach((k, r) => {
    for (let i = 0; i < NS; i++) {
      const o = (r * NS + i) * 4;
      t0[o] = k.q[i];
      t0[o + 1] = k.y[i];
      t0[o + 2] = k.arc[i];
      t0[o + 3] = k.thick[i];
      t1[o] = k.ao[i];
      t1[o + 1] = k.foam[i];
      t1[o + 2] = k.region[i];
      t1[o + 3] = 0;
    }
  });
  return [t0, t1];
}

// The three keyframes are blended with a quadratic through c = 0, 0.5, 1 (smooth, unlike a linear blend
// which would put a crease in the lip where c crosses 0.5).
export function blendWeights(c, out = [0, 0, 0]) {
  const x = clamp(c, 0, 1);
  out[0] = 2 * (x - 0.5) * (x - 1);
  out[1] = -4 * x * (x - 1);
  out[2] = 2 * x * (x - 0.5);
  return out;
}
const _w = [0, 0, 0];

// JS evaluation of the blended profile (used to place the surfer).
function lerpIdx(arr, i0, fi) {
  return arr[i0] * (1 - fi) + arr[i0 + 1] * fi;
}
export function profilePoint(keys, c, idx, out = [0, 0]) {
  blendWeights(c, _w);
  const i0 = clamp(Math.floor(idx), 0, NS - 2);
  const fi = clamp(idx - i0, 0, 1);
  out[0] = _w[0] * lerpIdx(keys[0].q, i0, fi) + _w[1] * lerpIdx(keys[1].q, i0, fi) + _w[2] * lerpIdx(keys[2].q, i0, fi);
  out[1] = _w[0] * lerpIdx(keys[0].y, i0, fi) + _w[1] * lerpIdx(keys[1].y, i0, fi) + _w[2] * lerpIdx(keys[2].y, i0, fi);
  return out;
}

export function profileArc(keys, c, idx) {
  blendWeights(c, _w);
  const i0 = clamp(Math.floor(idx), 0, NS - 2);
  const fi = clamp(idx - i0, 0, 1);
  return _w[0] * lerpIdx(keys[0].arc, i0, fi) + _w[1] * lerpIdx(keys[1].arc, i0, fi) + _w[2] * lerpIdx(keys[2].arc, i0, fi);
}
