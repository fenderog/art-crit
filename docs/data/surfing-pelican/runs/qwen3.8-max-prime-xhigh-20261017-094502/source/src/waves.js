/**
 * The ocean is one analytic height field: a sum of directional sine components.
 * The very same parameter list is evaluated on the CPU (so the board, the wake
 * and the camera sit exactly on the rendered surface) and code-generated into
 * GLSL (so the surface itself is displaced + shaded).
 */

export const GRAVITY = 9.81;

/** Everything under water runs in gentle slow motion — a surf-film ramp that
 *  also keeps the swell phase speed in step with the board's carving speed. */
export const TIME_SCALE = 0.34;

/** angle = travel direction in the XZ plane. ~PI/2 means the swell runs toward +Z,
 *  so crests line up along X — which is the direction our pelican travels. */
export const SWELL = [
  { angle: 1.5, wavelength: 52.0, amp: 0.72, speed: 1.0 },
  { angle: 1.62, wavelength: 31.0, amp: 0.44, speed: 1.0 },
  { angle: 1.42, wavelength: 19.5, amp: 0.27, speed: 1.03 },
  { angle: 1.7, wavelength: 12.4, amp: 0.15, speed: 1.06 },
  { angle: 1.36, wavelength: 7.6, amp: 0.06, speed: 1.1 },
  { angle: 1.78, wavelength: 4.6, amp: 0.032, speed: 1.14 },
];

/** Short wind chop. Only used to perturb the shading normal (never displaced),
 *  which keeps the silhouette cheap while the surface still sparkles up close. */
export const CHOP = [
  { angle: 0.62, wavelength: 1.62, amp: 0.031, speed: 1.25 },
  { angle: 2.14, wavelength: 1.03, amp: 0.02, speed: 1.4 },
  { angle: 4.21, wavelength: 0.66, amp: 0.012, speed: 1.55 },
  { angle: 5.61, wavelength: 0.41, amp: 0.007, speed: 1.7 },
];

export const MAX_HEIGHT = SWELL.reduce((s, w) => s + w.amp, 0);

export function expand(wave) {
  const k = (Math.PI * 2) / wave.wavelength;
  return {
    amp: wave.amp,
    kx: Math.cos(wave.angle) * k,
    kz: Math.sin(wave.angle) * k,
    omega: Math.sqrt(GRAVITY * k) * wave.speed * TIME_SCALE,
  };
}

const SWELL_P = SWELL.map(expand);
const CHOP_P = CHOP.map(expand);

const n = (v) => v.toFixed(6);

/** --- CPU side ------------------------------------------------------- */

export function oceanHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < SWELL_P.length; i++) {
    const w = SWELL_P[i];
    h += w.amp * Math.sin(w.kx * x + w.kz * z - w.omega * t);
  }
  return h;
}

/** Returns [dh/dx, dh/dz]. */
export function oceanSlope(x, z, t, out) {
  let dx = 0;
  let dz = 0;
  for (let i = 0; i < SWELL_P.length; i++) {
    const w = SWELL_P[i];
    const c = w.amp * Math.cos(w.kx * x + w.kz * z - w.omega * t);
    dx += c * w.kx;
    dz += c * w.kz;
  }
  out = out || [0, 0];
  out[0] = dx;
  out[1] = dz;
  return out;
}

const _slope = [0, 0];

/** Unit surface normal, cached vector (do not hold onto it). */
export function oceanNormal(x, z, t, target) {
  oceanSlope(x, z, t, _slope);
  return target.set(-_slope[0], 1, -_slope[1]).normalize();
}

/** --- GLSL side ------------------------------------------------------ */

function glslComponents(list) {
  return list.map((w) => {
    const p = expand(w);
    return {
      dot: `dot(vec2(${n(p.kx)}, ${n(p.kz)}), p)`,
      amp: n(p.amp),
      kx: n(p.kx),
      kz: n(p.kz),
      omega: n(p.omega),
    };
  });
}

export const OCEAN_GLSL = /* glsl */ `
float oceanHeight(vec2 p, float t) {
  float h = 0.0;
${glslComponents(SWELL)
  .map((c) => `  h += ${c.amp} * sin(${c.dot} - ${c.omega} * t);`)
  .join("\n")}
  return h;
}

vec2 oceanSlope(vec2 p, float t) {
  vec2 d = vec2(0.0);
${glslComponents(SWELL)
  .map(
    (c, i) =>
      `  float c${i} = ${c.amp} * cos(${c.dot} - ${c.omega} * t);\n  d += vec2(${c.kx}, ${c.kz}) * c${i};`
  )
  .join("\n")}
  return d;
}

vec2 chopSlope(vec2 p, float t) {
  vec2 d = vec2(0.0);
${glslComponents(CHOP)
  .map(
    (c, i) =>
      `  float k${i} = ${c.amp} * cos(${c.dot} - ${c.omega} * t);\n  d += vec2(${c.kx}, ${c.kz}) * k${i};`)
  .join("\n")}
  return d;
}
`;
