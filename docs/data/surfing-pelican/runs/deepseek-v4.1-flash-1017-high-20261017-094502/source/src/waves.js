// A small, shared ocean model. The exact same waves are evaluated on the CPU
// (for the board / pelican / particles) and in the water shader.

const RAW_WAVES = [
  { dir: [0.88, 0.47], amp: 0.44, len: 28.0, speed: 0.9, phase: 0.0 },
  { dir: [-0.58, 0.81], amp: 0.2, len: 15.0, speed: 1.2, phase: 2.1 },
  { dir: [0.93, 0.36], amp: 0.105, len: 9.0, speed: 1.65, phase: 4.3 },
  { dir: [-0.34, -0.94], amp: 0.05, len: 5.6, speed: 2.2, phase: 1.2 },
];

export const WAVES = RAW_WAVES.map((w) => {
  const l = Math.hypot(w.dir[0], w.dir[1]);
  return {
    ...w,
    dir: [w.dir[0] / l, w.dir[1] / l],
    k: (Math.PI * 2) / w.len,
  };
});

export const WAVE_COUNT = WAVES.length;

export function waveHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    h += w.amp * Math.sin((x * w.dir[0] + z * w.dir[1]) * w.k - t * w.speed + w.phase);
  }
  return h;
}

export function waveGradient(x, z, t, out = { x: 0, z: 0 }) {
  let gx = 0;
  let gz = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    const c =
      w.amp * w.k * Math.cos((x * w.dir[0] + z * w.dir[1]) * w.k - t * w.speed + w.phase);
    gx += c * w.dir[0];
    gz += c * w.dir[1];
  }
  out.x = gx;
  out.z = gz;
  return out;
}

const f = (n) => {
  const s = n.toFixed(6);
  return /[.eE]/.test(s) ? s : `${s}.0`;
};

export const WAVE_GLSL = /* glsl */ `
float oceanHeight(vec2 p, float t) {
  float h = 0.0;
${WAVES.map(
  (w) =>
    `  h += ${f(w.amp)} * sin(dot(p, vec2(${f(w.dir[0])}, ${f(w.dir[1])})) * ${f(
      w.k,
    )} - t * ${f(w.speed)} + ${f(w.phase)});`,
).join('\n')}
  return h;
}

vec2 oceanGradient(vec2 p, float t) {
  vec2 g = vec2(0.0);
${WAVES.map(
  (w) =>
    `  g += ${f(w.amp * w.k)} * vec2(${f(w.dir[0])}, ${f(w.dir[1])}) * cos(dot(p, vec2(${f(
      w.dir[0],
    )}, ${f(w.dir[1])})) * ${f(w.k)} - t * ${f(w.speed)} + ${f(w.phase)});`,
).join('\n')}
  return g;
}
`;
