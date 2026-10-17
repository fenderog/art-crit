// waves.js
//
// The ocean surface is a sum of a few travelling sine swells.
// The exact same maths is used twice:
//   • in JS  -> to place / tilt the surfer so it always sits on the drawn surface
//   • in GLSL (generated below from the same constants) -> to draw the ocean
// Keeping one source of truth is what makes the bird really ride the water.

// dir = travelling direction (unit-ish, in the XZ plane),
// k   = angular wavenumber (2*PI / wavelength),
// amp = height, phase = offset, speed = angular frequency.
export const WAVES = [
  { dir: [0.28, -0.96], k: 0.20, amp: 0.40, phase: 0.0, speed: 0.32 },  // the long ground swell
  { dir: [-0.86, -0.51], k: 0.52, amp: 0.42, phase: 1.7, speed: 0.78 }, // the swell that breaks
  { dir: [0.93, 0.36], k: 1.35, amp: 0.15, phase: 3.1, speed: 1.7 },     // chop
  { dir: [0.55, 0.83], k: 2.6, amp: 0.05, phase: 2.2, speed: 2.4 },      // a fine skin of ripple
];

export const WAVE_AMP_SUM = WAVES.reduce((s, w) => s + w.amp, 0);

/** Surface height at world position (x, z) and time t. */
export function waveHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    h += w.amp * Math.sin(w.k * (w.dir[0] * x + w.dir[1] * z) + w.phase + w.speed * t);
  }
  return h;
}

const _slope = { x: 0, z: 0 };

/** Partial derivatives (dh/dx, dh/dz) of the surface. */
export function waveSlope(x, z, t, out = _slope) {
  out.x = 0;
  out.z = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    const c = w.amp * w.k * Math.cos(w.k * (w.dir[0] * x + w.dir[1] * z) + w.phase + w.speed * t);
    out.x += c * w.dir[0];
    out.z += c * w.dir[1];
  }
  return out;
}

/** Up vector of the water surface (length 1). */
export function waveNormalAt(x, z, t, out) {
  const s = waveSlope(x, z, t, _slope);
  return out.set(-s.x, 1, -s.z).normalize();
}

const n = (v) => (Number.isInteger(v) ? v.toFixed(1) : v.toFixed(5));

/** GLSL twin of the three functions above, generated from the same constants. */
export function waveGLSL() {
  const height = [];
  const grad = [];
  for (const w of WAVES) {
    const dir = `vec2(${n(w.dir[0])}, ${n(w.dir[1])})`;
    const ph = `${n(w.k)} * dot(${dir}, p) + ${n(w.phase)} + ${n(w.speed)} * t`;
    height.push(`  h += ${n(w.amp)} * sin(${ph});`);
    grad.push(`  g += ${n(w.amp)} * ${n(w.k)} * ${dir} * cos(${ph});`);
  }
  return `
float surfHeight(vec2 p, float t) {
  float h = 0.0;
${height.join('\n')}
  return h;
}

vec2 surfGrad(vec2 p, float t) {
  vec2 g = vec2(0.0);
${grad.join('\n')}
  return g;
}

vec3 surfNormal(vec2 p, float t) {
  vec2 g = surfGrad(p, t);
  return normalize(vec3(-g.x, 1.0, -g.y));
}
`;
}
