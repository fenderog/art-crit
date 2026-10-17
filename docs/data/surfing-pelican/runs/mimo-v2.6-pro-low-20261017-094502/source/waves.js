// Shared Gerstner wave field.
// The same wave list drives the GLSL vertex shader of the ocean and the JS
// sampler used to float the pelican / surfboard on the surface, so the two
// always agree.

export const WAVES = [
  { dx: 1.0, dz: 0.42, amp: 1.05, freq: 0.085, speed: 0.72, phase: 0.0, steep: 0.62 },
  { dx: -0.55, dz: 1.0, amp: 0.66, freq: 0.16, speed: 1.05, phase: 1.9, steep: 0.50 },
  { dx: 0.9, dz: -0.8, amp: 0.36, freq: 0.29, speed: 1.55, phase: 3.4, steep: 0.42 },
  { dx: -1.0, dz: -0.35, amp: 0.17, freq: 0.47, speed: 2.10, phase: 5.1, steep: 0.34 },
];

// normalise directions once
for (const w of WAVES) {
  const len = Math.hypot(w.dx, w.dz);
  w.nx = w.dx / len;
  w.nz = w.dz / len;
}

export const MAX_WAVE_HEIGHT = WAVES.reduce((s, w) => s + w.amp, 0);

const f = (n) => n.toFixed(6);

/**
 * GLSL implementation of the exact same wave field.
 */
export function waveGLSL() {
  let body = '';
  for (const w of WAVES) {
    body += `
  ph = ${f(w.freq)} * (${f(w.nx)} * p.x + ${f(w.nz)} * p.y) + ${f(w.speed)} * t + ${f(w.phase)};
  cs = cos(ph); sn = sin(ph);
  disp.y += ${f(w.amp)} * sn;
  disp.x += ${f(w.steep * w.amp)} * ${f(w.nx)} * cs;
  disp.z += ${f(w.steep * w.amp)} * ${f(w.nz)} * cs;
  nrm.x -= ${f(w.nx * w.freq * w.amp)} * cs;
  nrm.z -= ${f(w.nz * w.freq * w.amp)} * cs;
  nrm.y -= ${f(w.steep * w.freq * w.amp)} * sn;
  hSum += ${f(w.amp)} * sn;
  chSum += abs(cs);`;
  }
  return `
// --- generated from waves.js -------------------------------------------
vec3 gerstner(vec2 p, float t, out vec3 nrm, out float crest) {
  vec3 disp = vec3(p.x, 0.0, p.y);
  vec3 n = vec3(0.0, 1.0, 0.0);
  float ph, cs, sn;
  float hSum = 0.0;
  float chSum = 0.0;
  ${body}
  nrm = normalize(n);
  crest = hSum / ${f(MAX_WAVE_HEIGHT)};
  return disp;
}
// -----------------------------------------------------------------------
`;
}

/**
 * CPU implementation of the same wave field.
 * Writes displaced position into `out` ({x,y,z}) and the surface normal into
 * `out` ({nx,ny,nz}). `out` is reused to avoid garbage.
 */
export function sampleWaves(x, z, t, out) {
  let px = x;
  let py = 0;
  let pz = z;
  let nx = 0;
  let ny = 1;
  let nz = 0;
  for (const w of WAVES) {
    const ph = w.freq * (w.nx * x + w.nz * z) + w.speed * t + w.phase;
    const cs = Math.cos(ph);
    const sn = Math.sin(ph);
    py += w.amp * sn;
    px += w.steep * w.amp * w.nx * cs;
    pz += w.steep * w.amp * w.nz * cs;
    nx -= w.nx * w.freq * w.amp * cs;
    nz -= w.nz * w.freq * w.amp * cs;
    ny -= w.steep * w.freq * w.amp * sn;
  }
  const inv = 1 / Math.hypot(nx, ny, nz);
  out.x = px;
  out.y = py;
  out.z = pz;
  out.nx = nx * inv;
  out.ny = ny * inv;
  out.nz = nz * inv;
  return out;
}