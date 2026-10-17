import * as THREE from "three";

// Primary swell travels toward +x. phase = k*x - w*t.
// The rider locks to phaseOnFace so the board stays on the steep face
// while the mesh scrolls backward in the ride frame.
export const WAVE = {
  k: 0.58,
  w: 2.35,
  phaseOnFace: 0.22,
  A: 1.2,
  harmonic: 0.22,
};

const _tx = new THREE.Vector3();
const _tz = new THREE.Vector3();

export function waveHeight(x, z, t) {
  const p = x * WAVE.k - t * WAVE.w;
  let y = Math.sin(p) + WAVE.harmonic * Math.sin(2 * p + 0.85);
  y *= WAVE.A;
  y += 0.055 * Math.sin(z * 0.42 + t * 0.7);
  y += 0.04 * Math.sin(x * 0.15 + z * 0.28 - t * 1.25);
  return y;
}

// Writes an upward normal. Flat check: +x tangent × +z tangent is -y in
// y-up right-handed space, so the normal is tangentZ × tangentX.
export function writeWaveNormal(x, z, t, out) {
  const e = 0.22;
  _tx.set(2 * e, waveHeight(x + e, z, t) - waveHeight(x - e, z, t), 0);
  _tz.set(0, waveHeight(x, z + e, t) - waveHeight(x, z - e, t), 2 * e);
  return out.crossVectors(_tz, _tx).normalize();
}

export function rideState(t, outNormal) {
  const x = (WAVE.phaseOnFace + WAVE.w * t) / WAVE.k;
  const zFreq = 0.42;
  const zAmp = 2.05;
  const z = Math.sin(t * zFreq) * zAmp;
  const vz = Math.cos(t * zFreq) * zAmp * zFreq;
  const vx = WAVE.w / WAVE.k;
  const y = waveHeight(x, z, t);
  writeWaveNormal(x, z, t, outNormal);
  return { x, y, z, vx, vz };
}
