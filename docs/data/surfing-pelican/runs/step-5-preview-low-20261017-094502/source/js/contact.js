// Soft "contact shadow" that the board throws onto the water. Cheaper (and far
// less moody) than a real shadow map for a transparent ocean shader.

import * as THREE from 'three';
import { PALETTE } from './palette.js';

const vertexShader = /* glsl */ `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}
`;

const fragmentShader = /* glsl */ `
precision highp float;
uniform vec3 uColor;
uniform float uStrength;
varying vec2 vUv;
void main() {
  vec2 c = vUv - 0.5;
  c.x *= 1.9; // shadow is longer than it is wide
  float d = length( c * vec2( 1.0, 1.35 ) );
  float a = smoothstep( 0.5, 0.05, d ) * uStrength;
  gl_FragColor = vec4( uColor, a );
  gl_FragColor = linearToOutputTexel( gl_FragColor );
}
`;

export function createContactShadow(scene) {
  const geo = new THREE.PlaneGeometry(9.5, 5.2);
  geo.rotateX(-Math.PI / 2); // lay flat, facing +y

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uColor: { value: new THREE.Color(PALETTE.deep).convertSRGBToLinear() },
      uStrength: { value: 0.5 },
    },
    vertexShader,
    fragmentShader,
    transparent: true,
    depthWrite: false,
  });

  const mesh = new THREE.Mesh(geo, material);
  mesh.name = 'shadow';
  mesh.renderOrder = 2;
  mesh.frustumCulled = false;
  scene.add(mesh);

  const up = new THREE.Vector3();
  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();

  return {
    mesh,
    update(rider) {
      const st = rider.state;
      up.copy(st.up);
      fwd.copy(st.forward);
      right.crossVectors(up, fwd).normalize();
      m.makeBasis(right, up, fwd);
      q.setFromRotationMatrix(m);
      mesh.position.copy(st.position);
      mesh.position.y += 0.09;
      mesh.quaternion.copy(q);
      // stronger, tighter shadow when the board sits deep in the face
      material.uniforms.uStrength.value = 0.38 + Math.min(0.4, Math.abs(st.wave) * 0.35);
    },
  };
}
