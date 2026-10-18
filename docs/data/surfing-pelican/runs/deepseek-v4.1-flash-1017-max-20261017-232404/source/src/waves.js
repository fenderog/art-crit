import * as THREE from 'three';

export const WAVE = {
  crestZ: -3.35,
  crestDrift: 0.68,
  crestWidth: 4.45,
  backWidth: 7.6,
  crestHeight: 3.08,
  crestPeak: 0.42,
  boardZ: 1.05
};

/** Shared CPU implementation of the ocean surface. */
export function waveHeight(x, z, t) {
  const zc = WAVE.crestZ + WAVE.crestDrift * Math.sin(t * 0.13);
  const width = z > zc ? WAVE.crestWidth : WAVE.backWidth;
  const d = (z - zc) / width;
  const ridge = Math.exp(-d * d);
  const peak = Math.exp(-Math.pow((z - zc) / 0.92, 2)) * (0.8 + 0.2 * Math.sin(x * 0.21 + t * 0.34));

  const envelope =
    1.0 +
    0.11 * Math.exp(-Math.pow((x + 5.8) / 5.0, 2)) -
    0.04 * Math.exp(-Math.pow((x - 7.5) / 4.8, 2));

  let h = envelope * (WAVE.crestHeight * ridge + WAVE.crestPeak * peak);
  h += 0.3 * ridge * Math.sin(x * 0.22 + z * 0.15 - t * 0.6);
  h += 0.1 * Math.sin(x * 0.52 + t * 1.15);
  h += 0.07 * Math.sin(z * 0.8 - t * 1.5 + x * 0.18);
  h += 0.055 * Math.sin((x + z) * 1.15 + t * 1.9);
  h +=
    0.34 *
    Math.exp(-Math.pow((z + 15) / 9, 2)) *
    (0.8 + 0.2 * Math.sin(x * 0.12 + t * 0.2));

  return h;
}

export function waveNormal(x, z, t, target = new THREE.Vector3()) {
  const e = 0.14;
  const hl = waveHeight(x - e, z, t);
  const hr = waveHeight(x + e, z, t);
  const hd = waveHeight(x, z - e, t);
  const hu = waveHeight(x, z + e, t);
  return target.set(hl - hr, 2 * e, hd - hu).normalize();
}

/** GLSL mirror of the functions above. */
export const waveGLSL = /* glsl */ `
  float waveHeight(vec2 p, float t) {
    float zc = -3.35 + 0.68 * sin(t * 0.13);
    float width = p.y > zc ? 4.45 : 7.6;
    float d = (p.y - zc) / width;
    float ridge = exp(-d * d);
    float peak = exp(-pow((p.y - zc) / 0.92, 2.0)) * (0.8 + 0.2 * sin(p.x * 0.21 + t * 0.34));

    float envelope = 1.0 + 0.11 * exp(-pow((p.x + 5.8) / 5.0, 2.0)) - 0.04 * exp(-pow((p.x - 7.5) / 4.8, 2.0));
    float h = envelope * (3.08 * ridge + 0.42 * peak);
    h += 0.3 * ridge * sin(p.x * 0.22 + p.y * 0.15 - t * 0.6);
    h += 0.1 * sin(p.x * 0.52 + t * 1.15);
    h += 0.07 * sin(p.y * 0.8 - t * 1.5 + p.x * 0.18);
    h += 0.055 * sin((p.x + p.y) * 1.15 + t * 1.9);
    h += 0.34 * exp(-pow((p.y + 15.0) / 9.0, 2.0)) * (0.8 + 0.2 * sin(p.x * 0.12 + t * 0.2));
    return h;
  }

  vec3 waveNormal(vec2 p, float t) {
    float e = 0.14;
    float hl = waveHeight(p - vec2(e, 0.0), t);
    float hr = waveHeight(p + vec2(e, 0.0), t);
    float hd = waveHeight(p - vec2(0.0, e), t);
    float hu = waveHeight(p + vec2(0.0, e), t);
    return normalize(vec3(hl - hr, 2.0 * e, hd - hu));
  }
`;
