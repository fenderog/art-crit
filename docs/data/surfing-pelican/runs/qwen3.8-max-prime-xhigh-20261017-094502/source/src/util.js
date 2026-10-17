import * as THREE from "three";

export const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const lerp = (a, b, t) => a + (b - a) * t;
export const invLerp = (a, b, v) => (b === a ? 0 : (v - a) / (b - a));

export function smoothstep(e0, e1, x) {
  const t = clamp((x - e0) / (e1 - e0 || 1e-6), 0, 1);
  return t * t * (3 - 2 * t);
}

/** Framerate independent exponential approach. */
export function damp(current, target, lambda, dt) {
  return lerp(current, target, 1 - Math.exp(-lambda * dt));
}

/** Cheap deterministic 1D value noise (smooth, no allocations). */
export function vnoise1(x) {
  const i = Math.floor(x);
  const f = x - i;
  const u = f * f * (3 - 2 * f);
  return lerp(hash1(i), hash1(i + 1), u);
}

export function hash1(n) {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return s - Math.floor(s);
}

/** Fractal noise built from vnoise1 — used for handheld camera drift. */
export function fbm1(x, octaves = 3) {
  let sum = 0;
  let amp = 0.5;
  let freq = 1;
  for (let i = 0; i < octaves; i++) {
    sum += amp * vnoise1(x * freq + i * 17.3);
    freq *= 2.03;
    amp *= 0.5;
  }
  return sum;
}

export const TAU = Math.PI * 2;

const _v = new THREE.Vector3();

/**
 * Tube along a curve with a radius that varies along its length
 * (three's TubeGeometry only supports a constant radius).
 */
export function taperedTube(curve, tubularSegments, radiusFn, radialSegments = 10) {
  const frames = curve.computeFrenetFrames(tubularSegments, false);
  const positions = [];
  const normals = [];
  const uvs = [];
  const indices = [];

  for (let i = 0; i <= tubularSegments; i++) {
    const u = i / tubularSegments;
    const r = radiusFn(u);
    const P = curve.getPoint(u, _v);
    const N = frames.normals[i];
    const B = frames.binormals[i];

    for (let j = 0; j <= radialSegments; j++) {
      const v = (j / radialSegments) * TAU;
      const sin = Math.sin(v);
      const cos = -Math.cos(v);

      const nx = cos * N.x + sin * B.x;
      const ny = cos * N.y + sin * B.y;
      const nz = cos * N.z + sin * B.z;

      normals.push(nx, ny, nz);
      positions.push(P.x + r * nx, P.y + r * ny, P.z + r * nz);
      uvs.push(i / tubularSegments, j / radialSegments);
    }
  }

  for (let j = 1; j <= tubularSegments; j++) {
    for (let i = 1; i <= radialSegments; i++) {
      const a = (radialSegments + 1) * (j - 1) + (i - 1);
      const b = (radialSegments + 1) * j + (i - 1);
      const c = (radialSegments + 1) * j + i;
      const d = (radialSegments + 1) * (j - 1) + i;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setIndex(indices);
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geo.computeBoundingSphere();
  return geo;
}

/** Bake a per-vertex colour ramp into a geometry (used for wings, tail, board). */
export function paintVertices(geometry, colorFn) {
  const pos = geometry.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    c.setRGB(1, 1, 1);
    colorFn(c, pos.getX(i), pos.getY(i), pos.getZ(i), i);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  return geometry;
}

/**
 * Build a THREE.Shape from a closed list of points using centripetal
 * Catmull-Rom sampling — handy for organic silhouettes.
 */
export function smoothShape(points, samples = 12, closed = true) {
  const pts = points.map((p) => new THREE.Vector2(p[0], p[1]));
  const curve = new THREE.SplineCurve(pts);
  curve.closed = closed;
  const shape = new THREE.Shape();
  const out = curve.getSpacedPoints(samples * pts.length);
  shape.moveTo(out[0].x, out[0].y);
  for (let i = 1; i < out.length; i++) shape.lineTo(out[i].x, out[i].y);
  return shape;
}
