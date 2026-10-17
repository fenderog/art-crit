// The ocean swell.
//
// One single source of truth: WAVES is precomputed here and used both by the
// CPU (to float the pelican + board) and to generate the GLSL that displaces
// the water mesh, so what you see is exactly what the surfer rides.

const TAU = Math.PI * 2;
const G = 9.81;

// dir: direction the swell travels towards (the pelican rides along the
// crests, i.e. across it). A couple of them run the other way so the pattern
// interferes instead of looking like corrugated iron.
// amp: wave height, len: wavelength, speed: speed multiplier, phase.
const DEFS = [
  { dir: [0.14, 0.99], amp: 0.8, len: 44.0, speed: 1.0, phase: 0.0 },
  { dir: [0.72, 0.69], amp: 0.4, len: 25.0, speed: 1.12, phase: 1.7 },
  { dir: [-0.78, 0.62], amp: 0.2, len: 15.0, speed: 1.3, phase: 3.1 },
  { dir: [0.45, -0.89], amp: 0.09, len: 9.5, speed: 1.5, phase: 4.4 },
  { dir: [-0.2, -0.98], amp: 0.05, len: 6.5, speed: 1.7, phase: 5.9 },
];

export const WAVES = DEFS.map((w) => {
  const l = Math.hypot(w.dir[0], w.dir[1]);
  const dx = w.dir[0] / l;
  const dz = w.dir[1] / l;
  const k = TAU / w.len;
  return {
    kx: dx * k,
    kz: dz * k,
    amp: w.amp,
    phase: w.phase,
    omega: Math.sqrt(G * k) * w.speed,
  };
});

/** Height of the water surface at (x, z) and time t. */
export function waveHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    h += w.amp * Math.sin(w.kx * x + w.kz * z + w.phase + w.omega * t);
  }
  return h;
}

// Finite differences are used on both sides so the board and the mesh agree.
const EPS = 0.5;

/** Surface normal at (x, z), written into `target`. */
export function waveNormal(x, z, t, target) {
  const hx = (waveHeight(x + EPS, z, t) - waveHeight(x - EPS, z, t)) / (2 * EPS);
  const hz = (waveHeight(x, z + EPS, t) - waveHeight(x, z - EPS, t)) / (2 * EPS);
  return target.set(-hx, 1, -hz).normalize();
}

const f = (v) => {
  const s = v.toFixed(6);
  return s === '-0.000000' ? '0.0' : s;
};

/** GLSL that mirrors waveHeight() exactly. `p` is (world X, world Z). */
export const WAVE_GLSL = `
float waveAt( vec2 p, float t ) {
  float h = 0.0;
${WAVES.map(
  (w) =>
    `  h += ${f(w.amp)} * sin( p.x * ${f(w.kx)} + p.y * ${f(w.kz)} + ${f(
      w.phase,
    )} + t * ${f(w.omega)} );`,
).join('\n')}
  return h;
}
`;
