// sky.js — a huge inverted sphere that is pinned to the camera and painted with
// the same gradient the ocean fades into. Sun disc, halo, drifting cloud banks.

import * as THREE from 'three';
import { SKY_UNIFORMS, SKY_COLOR, NOISE, CLOUDS } from './glsl.js';

const VERT = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;            // the dome is centred on the camera
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const FRAG = /* glsl */ `
${SKY_UNIFORMS}
${SKY_COLOR}
${NOISE}
${CLOUDS}

varying vec3 vDir;
void main() {
  vec3 d = normalize(vDir);
  vec3 col = skyColor(d);
  col += cloudColor(d);
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSky(shared) {
  const geometry = new THREE.SphereGeometry(3000, 48, 28);
  const material = new THREE.ShaderMaterial({
    vertexShader: VERT,
    fragmentShader: FRAG,
    uniforms: shared,
    side: THREE.BackSide,
    depthWrite: false,
    depthTest: false,
    fog: false,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.renderOrder = -1000;
  mesh.frustumCulled = false;
  mesh.name = 'sky';

  return {
    mesh,
    update(camera) {
      mesh.position.copy(camera.position);
    },
  };
}
