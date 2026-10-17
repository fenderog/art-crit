// Shared ocean wave math. The same constants drive the GLSL displacement in
// ocean.js and the CPU sampling used to place the pelican on the water, so the
// bird always sits exactly on the surface.

export const WAVE = {
  a1: 1.4, k1: 0.08, w1: 0.8, // long swell along X
  a2: 0.9, k2: 0.11, w2: 0.6, // swell along Z
  a3: 1.2, k3: 0.05, w3: 0.5, // diagonal swell
  a4: 0.35, k4: 0.21, w4: 1.3, // small ripple X
  a5: 0.25, k5: 0.27, w5: 1.7, // small ripple Z
  a6: 0.16, k6: 0.55, w6: 2.4, // chop X
  a7: 0.12, k7: 0.62, w7: 2.9, // chop Z
};

const f = (v) => Number(v).toFixed(8);

// GLSL twin of waveHeight() below. Expects a `uniform float uTime;` in scope.
export const waveGLSL = /* glsl */ `
float waveHeight(vec2 p) {
  float t = uTime;
  return ${f(WAVE.a1)} * sin(${f(WAVE.k1)} * p.x + ${f(WAVE.w1)} * t)
       + ${f(WAVE.a2)} * sin(${f(WAVE.k2)} * p.y - ${f(WAVE.w2)} * t)
       + ${f(WAVE.a3)} * sin(${f(WAVE.k3)} * (p.x + p.y) + ${f(WAVE.w3)} * t)
       + ${f(WAVE.a4)} * sin(${f(WAVE.k4)} * p.x - ${f(WAVE.w4)} * t)
       + ${f(WAVE.a5)} * sin(${f(WAVE.k5)} * p.y + ${f(WAVE.w5)} * t)
       + ${f(WAVE.a6)} * sin(${f(WAVE.k6)} * p.x + ${f(WAVE.w6)} * t)
       + ${f(WAVE.a7)} * sin(${f(WAVE.k7)} * p.y - ${f(WAVE.w7)} * t);
}
`;

export function waveHeight(x, z, t) {
  return (
    WAVE.a1 * Math.sin(WAVE.k1 * x + WAVE.w1 * t) +
    WAVE.a2 * Math.sin(WAVE.k2 * z - WAVE.w2 * t) +
    WAVE.a3 * Math.sin(WAVE.k3 * (x + z) + WAVE.w3 * t) +
    WAVE.a4 * Math.sin(WAVE.k4 * x - WAVE.w4 * t) +
    WAVE.a5 * Math.sin(WAVE.k5 * z + WAVE.w5 * t) +
    WAVE.a6 * Math.sin(WAVE.k6 * x + WAVE.w6 * t) +
    WAVE.a7 * Math.sin(WAVE.k7 * z - WAVE.w7 * t)
  );
}

// Analytic surface normal via partial derivatives of the wave sum.
export function waveNormal(x, z, t, out) {
  const dhdx =
    WAVE.a1 * WAVE.k1 * Math.cos(WAVE.k1 * x + WAVE.w1 * t) +
    WAVE.a3 * WAVE.k3 * Math.cos(WAVE.k3 * (x + z) + WAVE.w3 * t) +
    WAVE.a4 * WAVE.k4 * Math.cos(WAVE.k4 * x - WAVE.w4 * t) +
    WAVE.a6 * WAVE.k6 * Math.cos(WAVE.k6 * x + WAVE.w6 * t);
  const dhdz =
    WAVE.a2 * WAVE.k2 * Math.cos(WAVE.k2 * z - WAVE.w2 * t) +
    WAVE.a3 * WAVE.k3 * Math.cos(WAVE.k3 * (x + z) + WAVE.w3 * t) +
    WAVE.a5 * WAVE.k5 * Math.cos(WAVE.k5 * z + WAVE.w5 * t) +
    WAVE.a7 * WAVE.k7 * Math.cos(WAVE.k7 * z - WAVE.w7 * t);
  return out.set(-dhdx, 1, -dhdz).normalize();
}
