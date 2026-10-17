// How the wave changes along its crest. The same functions exist in GLSL
// (see waveGLSL) and in JS so the surfer can ride exactly what the GPU draws.

export const WAVE = {
  scale: 2.5, // metres per profile unit
  speed: 4.0, // m/s the pattern slides past the surfer (peel speed)
  xMin: -340,
  xMax: 130,
  climb: 0.3, // m/s the sea climbs the face
  qMax: 230, // world half-extent of the wave mesh across the crest
};

const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (a, b, x) => {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
const mix = (a, b, t) => a + (b - a) * t;

// c: 0 = mellow shoulder, 1 = full barrel. h: size multiplier.
export function sliceState(x, t, out = { c: 0, h: 1 }) {
  const xp = x + t * WAVE.speed;
  let c = mix(1.0, 0.64, smooth(-8, 24, x));
  c = mix(c, 0.0, smooth(24, 100, x));
  c += 0.09 * Math.sin(xp / 11.0) + 0.06 * Math.sin(xp / 4.7 + 1.9) + 0.05 * Math.sin(xp / 27.0 + 0.7);
  c += 0.035 * Math.sin(xp / 2.3 + 0.4) * Math.sin(xp / 9.1 + 2.0) + 0.03 * Math.sin(xp / 3.7 + 1.1);
  c = clamp(c, 0, 1);
  let h = mix(1.0, 0.86, smooth(-30, 40, x));
  h *= 1.0 + 0.07 * Math.sin(xp / 19.0 + 2.3) + 0.04 * Math.sin(xp / 7.3) + 0.025 * Math.sin(xp / 3.1 + 0.9);
  h *= smooth(-340, -250, x) * (1 - smooth(60, 125, x));
  out.c = c;
  out.h = h;
  return out;
}

export const waveGLSL = /* glsl */ `
#define WAVE_SPEED ${WAVE.speed.toFixed(3)}
float sm01(float a, float b, float x) { float t = clamp((x - a) / (b - a), 0.0, 1.0); return t * t * (3.0 - 2.0 * t); }
void sliceState(float x, float t, out float c, out float h) {
  float xp = x + t * WAVE_SPEED;
  c = mix(1.0, 0.64, sm01(-8.0, 24.0, x));
  c = mix(c, 0.0, sm01(24.0, 100.0, x));
  c += 0.09 * sin(xp / 11.0) + 0.06 * sin(xp / 4.7 + 1.9) + 0.05 * sin(xp / 27.0 + 0.7);
  c += 0.035 * sin(xp / 2.3 + 0.4) * sin(xp / 9.1 + 2.0) + 0.03 * sin(xp / 3.7 + 1.1);
  c = clamp(c, 0.0, 1.0);
  h = mix(1.0, 0.86, sm01(-30.0, 40.0, x));
  h *= 1.0 + 0.07 * sin(xp / 19.0 + 2.3) + 0.04 * sin(xp / 7.3) + 0.025 * sin(xp / 3.1 + 0.9);
  h *= sm01(-340.0, -250.0, x) * (1.0 - sm01(60.0, 125.0, x));
}
`;
