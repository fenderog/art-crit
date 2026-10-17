// Shared wave maths. The hero wave is stationary in the scene (the camera and
// the surfer ride along with it); the sea streams through it toward -z.
// Everything here is mirrored in GLSL so the CPU (board, pelican, wake) and the
// GPU (ocean mesh) agree on where the water is.
import * as THREE from "three";

export const SLOPE = 0.12; // crest line tilt: crest z = SLOPE * x
export const A0 = 4.1; // hero wave height
export const BACK = 9.0; // gentle back-of-wave width
export const FRONT = 3.3; // steep face width
export const CURL = 2.6; // forward throw of the lip
export const CURL_C = 1.0; // lip centre (distance past the crest)
export const CURL_W = 1.15;

// kx, kz, speed, amplitude: ambient swell + chop
export const AMBIENT = [
  [0.038, 0.257, 0.9, 0.35],
  [-0.21, 0.51, 1.3, 0.16],
  [1.2, 1.2, 2.6, 0.05],
  [-2.0, 1.6, 3.1, 0.03],
  [0.7, 3.0, 4.0, 0.015],
];

const f = (n) => (Number.isInteger(n) ? n.toFixed(1) : String(n));

export const waveGLSL = /* glsl */ `
const float SLOPE = ${f(SLOPE)};
const float A0 = ${f(A0)};
float heroAmp(float x) {
  return A0 * (0.5 + 0.5 * exp(-pow(x / 40.0, 2.0))) * (1.0 + 0.05 * sin(uTime * 0.45));
}
float ambientH(vec2 p) {
  float h = 0.0;
  ${AMBIENT.map(([kx, kz, w, a]) => `h += ${f(a)} * sin(${f(kx)} * p.x + ${f(kz)} * p.y + ${f(w)} * uTime);`).join("\n  ")}
  return h;
}
// p = rest position (x0, z0) of a water particle; returns its world position.
// outputs: u = distance past the crest line, prof = hero profile 0..1
vec3 surf(vec2 p, out float u, out float prof) {
  u = p.y - SLOPE * p.x;
  float amp = heroAmp(p.x);
  prof = u < 0.0 ? exp(-pow(u / ${f(BACK)}, 2.0)) : exp(-pow(u / ${f(FRONT)}, 2.0));
  float curl = ${f(CURL)} * exp(-pow(p.x / 22.0, 2.0)) * exp(-pow((u - ${f(CURL_C)}) / ${f(CURL_W)}, 2.0));
  return vec3(p.x, amp * prof + ambientH(p), p.y + curl);
}
`;

export function heroAmp(x, t) {
  return A0 * (0.5 + 0.5 * Math.exp(-((x / 40) ** 2))) * (1 + 0.05 * Math.sin(t * 0.45));
}

export function ambientH(x, z, t) {
  let h = 0;
  for (const [kx, kz, w, a] of AMBIENT) h += a * Math.sin(kx * x + kz * z + w * t);
  return h;
}

export function surface(x0, z0, t, out = new THREE.Vector3()) {
  const u = z0 - SLOPE * x0;
  const amp = heroAmp(x0, t);
  const prof = u < 0 ? Math.exp(-((u / BACK) ** 2)) : Math.exp(-((u / FRONT) ** 2));
  const curl = CURL * Math.exp(-((x0 / 22) ** 2)) * Math.exp(-(((u - CURL_C) / CURL_W) ** 2));
  return out.set(x0, amp * prof + ambientH(x0, z0, t), z0 + curl);
}

const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _c = new THREE.Vector3();
const _d = new THREE.Vector3();
// smoothed surface normal around a rest position
export function surfaceNormal(x0, z0, t, e = 0.7, out = new THREE.Vector3()) {
  const px = _a.copy(surface(x0 + e, z0, t, _c)).sub(surface(x0 - e, z0, t, _d));
  const pz = _b.copy(surface(x0, z0 + e, t, _c)).sub(surface(x0, z0 - e, t, _d));
  return out.crossVectors(pz, px).normalize();
}
