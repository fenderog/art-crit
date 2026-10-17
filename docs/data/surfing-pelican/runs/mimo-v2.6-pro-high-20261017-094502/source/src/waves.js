/**
 * Shared wave field.
 *
 * The exact same sum of directional sine waves is evaluated three ways:
 *  - on the CPU (to float the surf rig on the surface),
 *  - in the ocean vertex shader (to displace the water mesh),
 *  - in the ocean vertex shader again for the analytic surface normal.
 *
 * The GLSL is generated from the data below so the two always agree.
 */
import * as THREE from "three";

/** dir must be a unit [x, z] direction the crest travels along. */
export const WAVES = [
  { dir: [0.31, 0.95], amp: 1.02, k: 0.118, omega: 0.86, phase: 0.0 },
  { dir: [-0.74, 0.67], amp: 0.68, k: 0.191, omega: 1.16, phase: 1.72 },
  { dir: [0.88, -0.47], amp: 0.42, k: 0.315, omega: 1.78, phase: 3.05 },
  { dir: [-0.4, -0.92], amp: 0.24, k: 0.53, omega: 2.42, phase: 4.41 },
  { dir: [0.98, 0.2], amp: 0.13, k: 0.92, omega: 3.31, phase: 0.94 },
];

export const TOTAL_AMPLITUDE = WAVES.reduce((s, w) => s + w.amp, 0);

const f = (n) => n.toFixed(5);

/** Height of the water surface at world (x, z) at time t. */
export function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    h += w.amp * Math.sin(w.k * (x * w.dir[0] + z * w.dir[1]) - w.omega * t + w.phase);
  }
  return h;
}

const _n = new THREE.Vector3();

/** Analytic surface normal of the water at world (x, z) at time t. */
export function waveNormal(x, z, t, target = _n) {
  let dhx = 0;
  let dhz = 0;
  for (const w of WAVES) {
    const c = w.amp * w.k * Math.cos(w.k * (x * w.dir[0] + z * w.dir[1]) - w.omega * t + w.phase);
    dhx += c * w.dir[0];
    dhz += c * w.dir[1];
  }
  return target.set(-dhx, 1, -dhz).normalize();
}

/** GLSL implementation of the two functions above. */
export function waveGLSL() {
  const height = WAVES.map(
    (w) =>
      `\t${f(w.amp)} * sin( ${f(w.k)} * dot( p, vec2( ${f(w.dir[0])}, ${f(w.dir[1])} ) ) - ${f(
        w.omega
      )} * t + ${f(w.phase)} )`
  ).join(" +\n");

  const grad = WAVES.map(
    (w) =>
      `\t{\n\t\tfloat c = ${f(w.amp * w.k)} * cos( ${f(w.k)} * dot( p, vec2( ${f(
        w.dir[0]
      )}, ${f(w.dir[1])} ) ) - ${f(w.omega)} * t + ${f(w.phase)} );\n` +
      `\t\tdhx += c * ${f(w.dir[0])};\n\t\tdhz += c * ${f(w.dir[1])};\n\t}`
  ).join("\n");

  return `
float waveHeight( vec2 p, float t ) {
  return
${height}
  ;
}

vec3 waveNormal( vec2 p, float t ) {
  float dhx = 0.0;
  float dhz = 0.0;
${grad}
  return normalize( vec3( -dhx, 1.0, -dhz ) );
}
`;
}