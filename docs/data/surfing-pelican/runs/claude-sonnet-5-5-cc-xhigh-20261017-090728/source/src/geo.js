import * as THREE from "three";

export const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (a, b, x) => {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};

// Smooth interpolation through a list of numeric rows (Catmull-Rom).
export function crow(rows, u) {
  const n = rows.length - 1;
  const f = clamp(u, 0, 1) * n;
  const i = Math.min(Math.floor(f), n - 1);
  const t = f - i;
  const p0 = rows[Math.max(i - 1, 0)];
  const p1 = rows[i];
  const p2 = rows[i + 1];
  const p3 = rows[Math.min(i + 2, n)];
  const out = new Array(p1.length);
  for (let k = 0; k < p1.length; k++) {
    const a = -0.5 * p0[k] + 1.5 * p1[k] - 1.5 * p2[k] + 0.5 * p3[k];
    const b = p0[k] - 2.5 * p1[k] + 2 * p2[k] - 0.5 * p3[k];
    const c = -0.5 * p0[k] + 0.5 * p2[k];
    out[k] = ((a * t + b) * t + c) * t + p1[k];
  }
  return out;
}

// ---------------------------------------------------------------------------
// Axis-aligned loft: rings of ellipses stacked along +x. rows: [x, yc, zc, ry, rz]
export function axisLoft(rows, nU, nV) {
  const pos = [];
  const uv = [];
  const idx = [];
  for (let i = 0; i <= nU; i++) {
    const r = crow(rows, i / nU);
    for (let j = 0; j <= nV; j++) {
      const a = (j / nV) * Math.PI * 2;
      const c = Math.cos(a);
      const s = Math.sin(a);
      pos.push(r[0], r[1] + r[3] * s, r[2] + r[4] * c);
      uv.push(j / nV, i / nU);
    }
  }
  for (let i = 0; i < nU; i++) {
    for (let j = 0; j < nV; j++) {
      const a = i * (nV + 1) + j;
      const b = a + 1;
      const c = a + nV + 1;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

// ---------------------------------------------------------------------------
// Tube along a polyline of points with per-ring radii (parallel transport frames).
// Updatable: call tube.update(points, radii) every frame.
export function makeTube(nU, nV, material, { flat = 1 } = {}) {
  const geom = new THREE.BufferGeometry();
  const pos = new Float32Array((nU + 1) * (nV + 1) * 3);
  const uv = new Float32Array((nU + 1) * (nV + 1) * 2);
  const idx = [];
  for (let i = 0; i <= nU; i++) {
    for (let j = 0; j <= nV; j++) {
      uv[(i * (nV + 1) + j) * 2] = j / nV;
      uv[(i * (nV + 1) + j) * 2 + 1] = i / nU;
    }
  }
  for (let i = 0; i < nU; i++) {
    for (let j = 0; j < nV; j++) {
      const a = i * (nV + 1) + j;
      const b = a + 1;
      const c = a + nV + 1;
      const d = c + 1;
      idx.push(a, b, c, b, d, c);
    }
  }
  geom.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geom.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  geom.setIndex(idx);
  const mesh = new THREE.Mesh(geom, material);
  mesh.frustumCulled = false;

  const T = new THREE.Vector3();
  const N = new THREE.Vector3();
  const B = new THREE.Vector3();
  const prevT = new THREE.Vector3();
  const axis = new THREE.Vector3();
  const up = new THREE.Vector3(0, 0, 1);
  const tmp = new THREE.Vector3();

  // pts: array of Vector3 (nU+1), radii: array of numbers or [ry, rz]
  mesh.userData.update = (pts, rad, extra) => {
    for (let i = 0; i <= nU; i++) {
      const a = pts[Math.max(i - 1, 0)];
      const b = pts[Math.min(i + 1, nU)];
      T.subVectors(b, a).normalize();
      if (i === 0) {
        N.copy(up).addScaledVector(T, -up.dot(T)).normalize();
      } else {
        axis.crossVectors(prevT, T);
        const s = axis.length();
        if (s > 1e-6) {
          axis.divideScalar(s);
          const ang = Math.asin(clamp(s, -1, 1));
          N.applyAxisAngle(axis, ang);
        }
      }
      prevT.copy(T);
      B.crossVectors(T, N).normalize();
      const r = rad[i];
      const rN = Array.isArray(r) ? r[0] : r;
      const rB = Array.isArray(r) ? r[1] : r * flat;
      for (let j = 0; j <= nV; j++) {
        const ang = (j / nV) * Math.PI * 2;
        const c = Math.cos(ang);
        const s = Math.sin(ang);
        const o = (i * (nV + 1) + j) * 3;
        tmp.copy(pts[i]).addScaledVector(N, rN * c).addScaledVector(B, rB * s);
        pos[o] = tmp.x;
        pos[o + 1] = tmp.y;
        pos[o + 2] = tmp.z;
      }
    }
    geom.attributes.position.needsUpdate = true;
    geom.computeVertexNormals();
  };
  return mesh;
}

// ---------------------------------------------------------------------------
// Feather: length 1 along +x, total width 1 along z, curved gently downward (-y).
// Rachis sits at z = 0; leading vane (z < 0) is narrower than the trailing vane.
export function featherGeometry({
  segs = 9,
  across = 4,
  lead = 0.34,
  trail = 0.66,
  droop = 0.1,
  camber = 0.08,
  tip = 0.28,
  base = 0.35,
  colorFn = null,
} = {}) {
  const pos = [];
  const uv = [];
  const col = [];
  const idx = [];
  for (let i = 0; i <= segs; i++) {
    const t = i / segs;
    // outline: narrow base, full body, rounded tip
    let w = base + (1 - base) * smoothstep(0.0, 0.3, t);
    if (t > 1 - tip) {
      const k = (t - (1 - tip)) / tip;
      w *= Math.sqrt(Math.max(1 - k * k, 0.0));
    }
    const wl = lead * w;
    const wt = trail * w;
    for (let j = 0; j <= across; j++) {
      const v = j / across;
      const z = -wl + (wl + wt) * v;
      const side = z < 0 ? z / Math.max(lead, 1e-3) : z / Math.max(trail, 1e-3);
      const y = -droop * t * t - camber * side * side * (0.4 + 0.6 * t);
      pos.push(t, y, z);
      uv.push(0.5 + z * 0.75, 1 - t);
      if (colorFn) {
        const c = colorFn(t, v);
        col.push(c[0], c[1], c[2]);
      } else col.push(1, 1, 1);
    }
  }
  for (let i = 0; i < segs; i++) {
    for (let j = 0; j < across; j++) {
      const a = i * (across + 1) + j;
      const b = a + 1;
      const c = a + across + 1;
      const d = c + 1;
      idx.push(a, b, c, b, d, c);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

// ---------------------------------------------------------------------------
// Canvas textures
export function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Fine barbs fanning from the shaft; used as colour + bump for feathers.
export function featherTexture() {
  const W = 128;
  const H = 512;
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const g = c.getContext("2d");
  g.fillStyle = "#ececec";
  g.fillRect(0, 0, W, H);
  const rnd = mulberry(7);
  // texture space: x = across (0..W) rachis at W*0.34 (matches lead fraction), y = length (0..H, tip at top?)
  const rx = W * 0.5 - 0.0;
  g.lineCap = "round";
  for (let i = 0; i < 520; i++) {
    const y = rnd() * H;
    const side = rnd() < 0.5 ? -1 : 1;
    const len = 30 + rnd() * 40;
    const shade = 190 + rnd() * 65;
    g.strokeStyle = `rgba(${shade},${shade},${shade},0.55)`;
    g.lineWidth = 0.8 + rnd() * 1.3;
    g.beginPath();
    g.moveTo(rx, y);
    g.lineTo(rx + side * len, y + len * 0.9);
    g.stroke();
  }
  g.strokeStyle = "rgba(255,255,255,0.9)";
  g.lineWidth = 3;
  g.beginPath();
  g.moveTo(rx, 0);
  g.lineTo(rx, H);
  g.stroke();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

// Overlapping feather scallops for body plumage.
export function plumageTexture() {
  const W = 256;
  const H = 256;
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const g = c.getContext("2d");
  g.fillStyle = "#f4f4f4";
  g.fillRect(0, 0, W, H);
  const rnd = mulberry(11);
  const rows = 14;
  const cols = 16;
  for (let r = rows; r >= -1; r--) {
    for (let k = -1; k <= cols; k++) {
      const x = ((k + (r % 2) * 0.5) / cols) * W + (rnd() - 0.5) * 4;
      const y = (r / rows) * H + (rnd() - 0.5) * 3;
      const w = (W / cols) * 0.62;
      const h = (H / rows) * 1.25;
      const sh = 244 + rnd() * 11;
      const grd = g.createLinearGradient(0, y - h * 0.2, 0, y + h);
      grd.addColorStop(0, `rgb(${sh},${sh},${sh})`);
      grd.addColorStop(1, `rgb(${sh - 12},${sh - 12},${sh - 12})`);
      g.fillStyle = grd;
      g.beginPath();
      g.moveTo(x - w, y - h * 0.3);
      g.quadraticCurveTo(x - w * 1.05, y + h * 0.7, x, y + h);
      g.quadraticCurveTo(x + w * 1.05, y + h * 0.7, x + w, y - h * 0.3);
      g.closePath();
      g.fill();
      g.strokeStyle = "rgba(255,255,255,0.2)";
      g.lineWidth = 0.7;
      g.beginPath();
      g.moveTo(x, y);
      g.lineTo(x, y + h * 0.8);
      g.stroke();
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 4;
  return t;
}
