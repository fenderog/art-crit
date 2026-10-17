import * as THREE from 'three';

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
export function smoothstep(a, b, x) {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}

// ---------------------------------------------------------------------------
// Loft: a tube with elliptical cross-sections swept along a polyline.
// Rings run along the path, each ring has (radial + 1) vertices (seam duplicated
// so the loft can carry UVs).
// ---------------------------------------------------------------------------

export function createLoftGeometry(rings, radial, colorFn) {
  const count = rings * (radial + 1);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  geo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  const uv = new Float32Array(count * 2);
  for (let i = 0; i < rings; i++) {
    for (let j = 0; j <= radial; j++) {
      const k = i * (radial + 1) + j;
      uv[k * 2] = j / radial;
      uv[k * 2 + 1] = i / (rings - 1);
    }
  }
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  if (colorFn) {
    const col = new Float32Array(count * 3);
    const c = new THREE.Color();
    for (let i = 0; i < rings; i++) {
      for (let j = 0; j <= radial; j++) {
        const th = (j / radial) * Math.PI * 2;
        colorFn(c, i / (rings - 1), Math.cos(th), Math.sin(th));
        const k = (i * (radial + 1) + j) * 3;
        col[k] = c.r; col[k + 1] = c.g; col[k + 2] = c.b;
      }
    }
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  }
  const idx = [];
  for (let i = 0; i < rings - 1; i++) {
    for (let j = 0; j < radial; j++) {
      const a = i * (radial + 1) + j;
      const b = a + radial + 1;
      const c = a + 1;
      const d = b + 1;
      idx.push(a, b, c, b, d, c);
    }
  }
  geo.setIndex(idx);
  geo.userData.rings = rings;
  geo.userData.radial = radial;
  return geo;
}

const _t = new THREE.Vector3();
const _s = new THREE.Vector3();
const _u = new THREE.Vector3();
const _ps = new THREE.Vector3(1, 0, 0);
const _sec = { rx: 0, ry: 0, ox: 0, oy: 0 };

// path: array of Vector3 (length === rings); section(t, out) fills rx, ry, ox, oy.
export function updateLoft(geo, path, section, upRef) {
  const { rings, radial } = geo.userData;
  const pos = geo.attributes.position.array;
  _ps.set(1, 0, 0);
  let r0 = 0, r1 = 0;
  for (let i = 0; i < rings; i++) {
    const p = path[i];
    _t.subVectors(path[Math.min(rings - 1, i + 1)], path[Math.max(0, i - 1)]).normalize();
    if (i === 0) {
      _s.crossVectors(_t, upRef);
    } else {
      // parallel transport the previous frame: no flips on curly paths
      _s.copy(_ps).addScaledVector(_t, -_t.dot(_ps));
    }
    if (_s.lengthSq() < 1e-10) _s.copy(_ps);
    else _s.normalize();
    _ps.copy(_s);
    _u.crossVectors(_s, _t).normalize();
    _sec.ox = 0; _sec.oy = 0;
    section(i / (rings - 1), _sec);
    if (i === 0) r0 = Math.max(_sec.rx, _sec.ry);
    if (i === rings - 1) r1 = Math.max(_sec.rx, _sec.ry);
    for (let j = 0; j <= radial; j++) {
      const th = (j / radial) * Math.PI * 2;
      const cx = _sec.ox + _sec.rx * Math.cos(th);
      const cy = _sec.oy + _sec.ry * Math.sin(th);
      const k = (i * (radial + 1) + j) * 3;
      pos[k] = p.x + _s.x * cx + _u.x * cy;
      pos[k + 1] = p.y + _s.y * cx + _u.y * cy;
      pos[k + 2] = p.z + _s.z * cx + _u.z * cy;
    }
  }
  geo.attributes.position.needsUpdate = true;
  geo.computeVertexNormals();
  const nrm = geo.attributes.normal.array;
  // weld the seam normals
  for (let i = 0; i < rings; i++) {
    const a = i * (radial + 1) * 3;
    const b = (i * (radial + 1) + radial) * 3;
    for (let c = 0; c < 3; c++) {
      const m = (nrm[a + c] + nrm[b + c]) * 0.5;
      nrm[a + c] = m; nrm[b + c] = m;
    }
  }
  // collapsed end rings get the path tangent as normal
  const capNormal = (ring, dir) => {
    _t.subVectors(path[ring === 0 ? 1 : rings - 1], path[ring === 0 ? 0 : rings - 2]).normalize().multiplyScalar(dir);
    for (let j = 0; j <= radial; j++) {
      const k = (ring * (radial + 1) + j) * 3;
      nrm[k] = _t.x; nrm[k + 1] = _t.y; nrm[k + 2] = _t.z;
    }
  };
  if (r0 < 1e-4) capNormal(0, -1);
  if (r1 < 1e-4) capNormal(rings - 1, 1);
  geo.attributes.normal.needsUpdate = true;
}

export function buildLoft(path, section, { radial = 16, upRef = new THREE.Vector3(0, 1, 0), colorFn } = {}) {
  const geo = createLoftGeometry(path.length, radial, colorFn);
  updateLoft(geo, path, section, upRef);
  geo.computeBoundingSphere();
  return geo;
}

// ---------------------------------------------------------------------------
// Feather: a cambered leaf strip. Base at the origin, tip at z = -1,
// max width 1 along x. Vertex colours give a pale shaft and fringe.
// ---------------------------------------------------------------------------
export function featherGeometry({ segs = 8, emarg = 0, shaft = 1.3, fringe = 1.12, base = 0.75 } = {}) {
  const pos = [];
  const col = [];
  const idx = [];
  for (let i = 0; i <= segs; i++) {
    const s = i / segs;
    let hw = 0.5 * (0.35 + 0.65 * Math.sin(Math.min(1, s * 1.7) * Math.PI * 0.5));
    hw *= Math.sqrt(Math.max(0, 1 - Math.pow(s, 5)));
    if (emarg) hw *= 1 - emarg * smoothstep(0.4, 0.7, s);
    const y = -0.06 * Math.sin(Math.PI * s);
    const z = -s;
    const shade = base + (1 - base) * smoothstep(0, 0.35, s);
    pos.push(-hw, y - 0.004, z, 0, y + 0.012, z, hw, y - 0.004, z);
    const e = shade * (s > 0.2 ? fringe : 1);
    const m = shade * shaft;
    col.push(e, e, e, m, m, m, e, e, e);
  }
  for (let i = 0; i < segs; i++) {
    const a = i * 3;
    for (let k = 0; k < 2; k++) {
      const v0 = a + k, v1 = a + k + 1, v2 = a + 3 + k, v3 = a + 4 + k;
      idx.push(v0, v2, v1, v1, v2, v3);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

// Add per-vertex colours to any geometry from a function of its normal/position.
export function paintGeometry(geo, fn) {
  const n = geo.attributes.normal;
  const p = geo.attributes.position;
  const col = new Float32Array(p.count * 3);
  const c = new THREE.Color();
  const nv = new THREE.Vector3();
  const pv = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    nv.fromBufferAttribute(n, i);
    pv.fromBufferAttribute(p, i);
    fn(c, nv, pv);
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  return geo;
}
