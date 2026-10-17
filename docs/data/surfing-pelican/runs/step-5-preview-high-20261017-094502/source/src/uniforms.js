// uniforms.js — the shared uniform set + palette.
// The very same uniform objects are referenced by the sky, the ocean and the
// spray shaders, so "uTime" and the sun only need to be updated once.

import * as THREE from 'three';

export const PALETTE = {
  zenith: 0x14304f,      // top of the sky
  horizon: 0xc9ad86,     // warm haze at the horizon
  horizonGlow: 0xe9b881, // glow just above the water
  sun: 0xffeecb,
  deep: 0x0a2b3a,        // troughs
  shallow: 0x2a86a0,     // faces
  foam: 0xf3f9fb,
  island: 0x6e8b9e,
  lighthouse: 0xe8e2d4,
  lighthouseLight: 0xffd27a,
  bird: 0x39404c,
};

// Direction *to* the sun. Low, up-left, beyond the surfer: gives a long
// glitter path on the water and a rim light on the pelican.
export const SUN_DIR = new THREE.Vector3(-0.076, 0.246, 0.965).normalize();

export function createSharedUniforms() {
  return {
    uTime: { value: 0 },
    uSunDir: { value: SUN_DIR.clone() },
    uSunColor: { value: new THREE.Color(PALETTE.sun) },
    uZenithColor: { value: new THREE.Color(PALETTE.zenith) },
    uHorizonColor: { value: new THREE.Color(PALETTE.horizon) },
    uHorizonGlow: { value: new THREE.Color(PALETTE.horizonGlow) },
  };
}
