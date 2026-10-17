// The wave field, defined once and shared bit-for-bit between:
//   - JS   (waves.js):           so floating objects (board, camera clamp, spray,
//                               jumping fish) sit exactly on the shader's surface
//   - GLSL (via glslWaveChunk): so the ocean mesh is displaced by the same math
//
// Each wave is a directional sine:  h += amp * sin(dot(dir, p) * k - omega * t + phase)
// with k = 2*pi/lambda and omega = k * speed (deep-water-ish dispersion).

export const WAVES = [
  { dir: [1, 0], lambda: 30, speed: 2.4, amp: 1.5, phase: 0.0 },          // the swell the pelican rides
  { dir: [1, 0], lambda: 15, speed: 2.4, amp: 0.5, phase: -1.1 },         // harmonic: sharpens the crest
  { dir: [0.83, 0.56], lambda: 22, speed: 1.9, amp: 0.55, phase: 2.1 },   // crossing secondary swell
  { dir: [0.94, -0.34], lambda: 11, speed: 1.6, amp: 0.26, phase: 0.7 },  // wind chop
  { dir: [0.6, -0.8], lambda: 7, speed: 1.4, amp: 0.14, phase: 4.0 },     // finer chop
];

const TAU = Math.PI * 2;
for (const w of WAVES) {
  const len = Math.hypot(w.dir[0], w.dir[1]) || 1;
  w.dx = w.dir[0] / len;
  w.dz = w.dir[1] / len;
  w.k = TAU / w.lambda;
  w.om = w.k * w.speed;
}

export const SWELL = WAVES[0];

export function waveHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    h += w.amp * Math.sin((w.dx * x + w.dz * z) * w.k - w.om * t + w.phase);
  }
  return h;
}

// Analytic surface normal (unit, y-up).
export function waveNormal(x, z, t, out) {
  let gx = 0;
  let gz = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    const c = w.amp * w.k * Math.cos((w.dx * x + w.dz * z) * w.k - w.om * t + w.phase);
    gx += w.dx * c;
    gz += w.dz * c;
  }
  return out.set(-gx, 1, -gz).normalize();
}

// Format a number as a clean GLSL float literal (always has a decimal point).
function fmt(n) {
  let s = n.toFixed(6).replace(/(\.\d*?)0+$/, '$1');
  if (s.endsWith('.')) s = s.slice(0, -1);
  if (!/[.eE]/.test(s)) s += '.0';
  return s === '-0.0' ? '0.0' : s;
}

// Emits GLSL functions waveH(vec2 p, float t) and waveGrad(vec2 p, float t)
// generated from the exact same constants used by the JS functions above.
export function glslWaveChunk() {
  let hf = 'float waveH(vec2 p, float t) {\n  float h = 0.0;\n';
  let gf = 'vec2 waveGrad(vec2 p, float t) {\n  vec2 g = vec2(0.0);\n';
  for (const w of WAVES) {
    const th = `dot(vec2(${fmt(w.dx)}, ${fmt(w.dz)}), p) * ${fmt(w.k)} - ${fmt(w.om)} * t + (${fmt(w.phase)})`;
    hf += `  h += ${fmt(w.amp)} * sin(${th});\n`;
    gf += `  g += vec2(${fmt(w.dx)}, ${fmt(w.dz)}) * (${fmt(w.amp * w.k)} * cos(${th}));\n`;
  }
  hf += '  return h;\n}\n\n';
  gf += '  return g;\n}\n';
  return hf + gf;
}
