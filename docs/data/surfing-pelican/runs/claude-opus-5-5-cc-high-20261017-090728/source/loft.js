import * as THREE from "three";

// Sweeps an elliptical (or super-elliptical) cross-section along a smooth path.
// `radii(t)` returns [side, up] half-extents at t in [0,1].
// `color(t, offset)` optionally returns a THREE.Color per vertex; `offset` is the
// cross-section vector (in the same space as the path) from the path to the vertex.
export function loft(points, radii, opts = {}) {
  const {
    segments = 48,
    radial = 20,
    up = new THREE.Vector3(0, 1, 0),
    color = null,
    power = 1, // <1 gives boxier cross-sections
    curveType = "catmullrom",
  } = opts;

  const curve = new THREE.CatmullRomCurve3(points, false, curveType, 0.5);
  const pos = [];
  const col = [];
  const idx = [];

  let N = new THREE.Vector3();
  const T = new THREE.Vector3();
  const B = new THREE.Vector3();
  const P = new THREE.Vector3();
  const off = new THREE.Vector3();
  const c = new THREE.Color();

  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    curve.getPointAt(t, P);
    curve.getTangentAt(t, T).normalize();
    if (i === 0) {
      N.copy(up).addScaledVector(T, -up.dot(T)).normalize();
    } else {
      // parallel transport keeps the section from twisting
      N.addScaledVector(T, -N.dot(T)).normalize();
    }
    B.crossVectors(T, N).normalize();
    const [rs, ru] = radii(t);
    for (let j = 0; j < radial; j++) {
      const a = (j / radial) * Math.PI * 2;
      let ca = Math.cos(a);
      let sa = Math.sin(a);
      if (power !== 1) {
        ca = Math.sign(ca) * Math.pow(Math.abs(ca), power);
        sa = Math.sign(sa) * Math.pow(Math.abs(sa), power);
      }
      off.set(0, 0, 0).addScaledVector(N, ca * ru).addScaledVector(B, sa * rs);
      pos.push(P.x + off.x, P.y + off.y, P.z + off.z);
      if (color) {
        const cc = color(t, off, c);
        col.push(cc.r, cc.g, cc.b);
      }
    }
  }

  for (let i = 0; i < segments; i++) {
    for (let j = 0; j < radial; j++) {
      const a = i * radial + j;
      const b = i * radial + ((j + 1) % radial);
      const d = (i + 1) * radial + j;
      const e = (i + 1) * radial + ((j + 1) % radial);
      idx.push(a, b, d, b, e, d);
    }
  }

  // end caps (fans to the centre point) so open ends are never visible
  const capStart = pos.length / 3;
  const p0 = curve.getPointAt(0);
  pos.push(p0.x, p0.y, p0.z);
  const capEnd = capStart + 1;
  const p1 = curve.getPointAt(1);
  pos.push(p1.x, p1.y, p1.z);
  if (color) {
    const c0 = color(0, new THREE.Vector3(), c);
    col.push(c0.r, c0.g, c0.b);
    const c1 = color(1, new THREE.Vector3(), c);
    col.push(c1.r, c1.g, c1.b);
  }
  const last = segments * radial;
  for (let j = 0; j < radial; j++) {
    const jn = (j + 1) % radial;
    idx.push(capStart, jn, j);
    idx.push(capEnd, last + j, last + jn);
  }

  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  if (color) g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

export const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
