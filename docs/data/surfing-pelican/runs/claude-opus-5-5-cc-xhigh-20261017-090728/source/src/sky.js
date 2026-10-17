import * as THREE from 'three';
import { NOISE_GLSL, SKY_GLSL } from './shaders.js';

export function createSky(shared) {
  const mat = new THREE.ShaderMaterial({
    uniforms: shared,
    vertexShader: /* glsl */ `
      varying vec3 vWorld;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorld = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uDisc;
      varying vec3 vWorld;
      ${NOISE_GLSL}
      ${SKY_GLSL}
      void main() {
        vec3 d = normalize(vWorld - cameraPosition);
        gl_FragColor = vec4(skyColor(d, uDisc), 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
    side: THREE.BackSide,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(2500, 64, 32), mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = -10;
  return mesh;
}

// A low hazy headland on the horizon, off towards the setting sun.
export function createHeadland(color) {
  const R = 1450;
  const n = 90;
  const pos = [];
  const idx = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    const az = THREE.MathUtils.degToRad(-38 - 46 * t);
    const env = Math.pow(Math.sin(Math.PI * Math.pow(t, 0.7)), 0.8);
    const h = env * (30 + 22 * Math.sin(t * 17.0) * Math.sin(t * 5.3 + 1) + 9 * Math.sin(t * 41.0)) + 4;
    const x = Math.sin(az) * R;
    const z = -Math.cos(az) * R;
    pos.push(x, -20, z, x, Math.max(2, h), z);
    if (i < n) {
      const a = i * 2;
      idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  const mat = new THREE.MeshBasicMaterial({ color, fog: false, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.renderOrder = -5;
  return mesh;
}
