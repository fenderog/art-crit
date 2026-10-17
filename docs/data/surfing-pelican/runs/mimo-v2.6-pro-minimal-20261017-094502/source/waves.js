// Shared ocean-wave field. The exact same parameters are used from JavaScript
// (to place the surfer on the surface) and from GLSL (to displace + shade the
// ocean), so the board always sits on the water.

const G = 9.81;

function normalize2(x, y) {
  const l = Math.hypot(x, y);
  return [x / l, y / l];
}

// amp: wave height, wavelength: crest distance, speed: dispersion multiplier,
// sharp: >1 sharpens crests and flattens troughs (classic ocean profile).
export const WAVES = [
  { dir: [1.0, 0.26], amp: 0.72, wavelength: 31.0, speed: 1.0, sharp: 1.32 },
  { dir: [0.82, -0.58], amp: 0.40, wavelength: 17.5, speed: 1.03, sharp: 1.45 },
  { dir: [0.96, 0.29], amp: 0.21, wavelength: 9.2, speed: 1.12, sharp: 1.5 },
  { dir: [0.52, 0.85], amp: 0.125, wavelength: 5.4, speed: 1.22, sharp: 1.35 },
  { dir: [-0.18, 0.98], amp: 0.082, wavelength: 3.1, speed: 1.3, sharp: 1.22 },
];

export const WAVE_DATA = WAVES.map((w) => {
  const [dx, dz] = normalize2(w.dir[0], w.dir[1]);
  const k = (2 * Math.PI) / w.wavelength;
  return {
    dx,
    dz,
    k,
    omega: w.speed * Math.sqrt(G * k),
    amp: w.amp,
    p: w.sharp,
  };
});

/** Surface height at (x, z) for time t. */
export function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVE_DATA) {
    const ph = w.k * (w.dx * x + w.dz * z) + w.omega * t;
    const u = 0.5 + 0.5 * Math.sin(ph);
    h += w.amp * (2 * Math.pow(u, w.p) - 1);
  }
  return h;
}

/** Gradient (dh/dx, dh/dz) at (x, z) for time t. */
export function waveGradient(x, z, t) {
  let gx = 0;
  let gz = 0;
  for (const w of WAVE_DATA) {
    const ph = w.k * (w.dx * x + w.dz * z) + w.omega * t;
    const u = Math.min(1, Math.max(1e-4, 0.5 + 0.5 * Math.sin(ph)));
    const d = w.amp * 2 * w.p * Math.pow(u, w.p - 1) * (0.5 * Math.cos(ph)) * w.k;
    gx += d * w.dx;
    gz += d * w.dz;
  }
  return [gx, gz];
}

/** Unit surface normal at (x, z) for time t. */
export function waveNormal(x, z, t, target) {
  const [gx, gz] = waveGradient(x, z, t);
  const out = target || { x: 0, y: 0, z: 0 };
  const inv = 1 / Math.sqrt(gx * gx + 1 + gz * gz);
  out.x = -gx * inv;
  out.y = inv;
  out.z = -gz * inv;
  return out;
}

const f = (v) => {
  const s = Number(v).toFixed(7);
  return s.includes('.') ? s : `${s}.0`;
};

/** GLSL twin of waveHeight()/waveGradient(). */
export const WAVE_GLSL = /* glsl */ `
void waveEval(vec2 p, float t, out float h, out vec2 grad) {
  h = 0.0;
  grad = vec2(0.0);
${WAVE_DATA.map(
  (w) => /* glsl */ `
  {
    float ph = ${f(w.k)} * (${f(w.dx)} * p.x + ${f(w.dz)} * p.y) + ${f(w.omega)} * t;
    float u = clamp(0.5 + 0.5 * sin(ph), 1e-4, 1.0);
    float pu = pow(u, ${f(w.p - 1)});
    h += ${f(w.amp)} * (2.0 * u * pu - 1.0);
    float d = ${f(w.amp * 2 * w.p * w.k)} * pu * (0.5 * cos(ph));
    grad += vec2(${f(w.dx)}, ${f(w.dz)}) * d;
  }`,
).join('')}
}
`;