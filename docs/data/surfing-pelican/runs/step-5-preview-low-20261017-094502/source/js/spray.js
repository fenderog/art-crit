// Rooster-tail spray thrown up behind the board. A small CPU particle pool
// rendered as additive-ish round sprites.

import * as THREE from 'three';
import { PALETTE } from './palette.js';

const MAX = 420;

const vertexShader = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
varying float vAlpha;
void main() {
  vAlpha = aAlpha;
  vec4 mv = modelViewMatrix * vec4( position, 1.0 );
  gl_PointSize = aSize * 260.0 / max( 0.001, -mv.z );
  gl_Position = projectionMatrix * mv;
}
`;

const fragmentShader = /* glsl */ `
precision highp float;
uniform vec3 uColor;
varying float vAlpha;
void main() {
  vec2 c = gl_PointCoord - 0.5;
  float d = length( c );
  if ( d > 0.5 || vAlpha <= 0.001 ) discard;
  float a = smoothstep( 0.5, 0.08, d ) * vAlpha;
  gl_FragColor = vec4( uColor, a );
  gl_FragColor = linearToOutputTexel( gl_FragColor );
}
`;

const lin = (hex) => new THREE.Color(hex).convertSRGBToLinear();

export function createSpray(scene) {
  const positions = new Float32Array(MAX * 3);
  const sizes = new Float32Array(MAX);
  const alphas = new Float32Array(MAX);
  const vel = new Float32Array(MAX * 3);
  const life = new Float32Array(MAX);
  const span = new Float32Array(MAX);

  for (let i = 0; i < MAX; i++) {
    positions[i * 3 + 1] = -999; // park dead droplets below the world
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));

  const material = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: lin(PALETTE.foam) } },
    vertexShader,
    fragmentShader,
    transparent: true,
    depthWrite: false,
  });

  const points = new THREE.Points(geo, material);
  points.name = 'spray';
  points.frustumCulled = false;
  points.renderOrder = 3;
  scene.add(points);

  let cursor = 0;
  let carry = 0;
  const spawnAt = new THREE.Vector3();
  const dir = new THREE.Vector3();

  function spawn(rider, intensity) {
    const st = rider.state;
    // just behind the tail of the board
    spawnAt.set(0, 0.35, -1.7).applyMatrix4(rider.group.matrixWorld);
    dir.copy(st.forward).multiplyScalar(-1);

    const i = cursor;
    cursor = (cursor + 1) % MAX;
    positions[i * 3] = spawnAt.x + (Math.random() - 0.5) * 0.5;
    positions[i * 3 + 1] = spawnAt.y + Math.random() * 0.25;
    positions[i * 3 + 2] = spawnAt.z + (Math.random() - 0.5) * 0.5;

    const back = 2.5 + Math.random() * 5.0;
    const up = 2.0 + Math.random() * 4.5 * intensity;
    const side = (Math.random() - 0.5) * 3.0;
    vel[i * 3] = dir.x * back + st.right.x * side;
    vel[i * 3 + 1] = up;
    vel[i * 3 + 2] = dir.z * back + st.right.z * side;

    life[i] = 1;
    span[i] = 0.7 + Math.random() * 1.5;
    sizes[i] = 0.05 + Math.random() * 0.14;
    alphas[i] = 1;
  }

  function update(t, dt, rider) {
    const st = rider.state;
    const intensity = Math.min(1, 0.35 + Math.abs(st.wave) * 0.9);

    // emit at a rate that follows the swell
    carry += dt * (34 + intensity * 46);
    let n = Math.floor(carry);
    carry -= n;
    n = Math.min(n, MAX - 1);
    for (let k = 0; k < n; k++) spawn(rider, intensity);

    for (let i = 0; i < MAX; i++) {
      if (life[i] <= 0) continue;
      life[i] -= dt / span[i];
      if (life[i] <= 0) {
        life[i] = 0;
        alphas[i] = 0;
        sizes[i] = 0;
        positions[i * 3 + 1] = -999;
        continue;
      }
      vel[i * 3 + 1] -= 7.5 * dt; // gravity
      positions[i * 3] += vel[i * 3] * dt;
      positions[i * 3 + 1] += vel[i * 3 + 1] * dt;
      positions[i * 3 + 2] += vel[i * 3 + 2] * dt;
      alphas[i] = Math.min(1, life[i] * 3.0) * life[i];
      sizes[i] += dt * 0.12;
    }

    geo.attributes.position.needsUpdate = true;
    geo.attributes.aSize.needsUpdate = true;
    geo.attributes.aAlpha.needsUpdate = true;
  }

  return { points, update };
}
