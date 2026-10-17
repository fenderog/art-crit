import * as THREE from "three";

// Direction from the scene toward the sun. Shared by the sky, the water
// specular, and the key light so the highlights agree.
// From the shoulder the camera sits on, so the lit flank is the one we see.
export const SUN_DIR = new THREE.Vector3(0.22, 0.78, 0.48).normalize();

// Exponential haze in linear color, applied before tone mapping so the far
// water dissolves into the same horizon the sky paints.
export const HAZE_DENSITY = 0.0175;

export const horizonColor = new THREE.Color(0xf3b08a);
export const skyTopColor = new THREE.Color(0x3c719c);
export const zenithColor = new THREE.Color(0x12325c);
export const warmColor = new THREE.Color(0xffc4a4);
export const sunColor = new THREE.Color(0xffe3b8);
export const cloudLitColor = new THREE.Color(0xfff6ee);
export const cloudShadowColor = new THREE.Color(0xd88878);
export const deepColor = new THREE.Color(0x083444);
export const shallowColor = new THREE.Color(0x16848a);
export const foamColor = new THREE.Color(0xfff8f1);
