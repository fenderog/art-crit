import * as THREE from 'three';
import { waveHeight } from './water.js';

const MAX = 60;

// Expanding foam patches trailing behind the tail, riding the wave surface.
export function createWake() {
  const geo = new THREE.SphereGeometry(1, 8, 6);
  const mat = new THREE.MeshStandardMaterial({
    color: '#ffffff',
    flatShading: true,
    roughness: 0.55,
    transparent: true,
    opacity: 0.75,
  });
  const mesh = new THREE.InstancedMesh(geo, mat, MAX);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  mesh.frustumCulled = false;

  const xs = new Float32Array(MAX);
  const zs = new Float32Array(MAX);
  const life = new Float32Array(MAX);
  const maxLife = new Float32Array(MAX);

  const dummy = new THREE.Object3D();
  const hidden = new THREE.Matrix4().makeScale(0, 0, 0);
  const white = new THREE.Color('#ffffff');
  const waterCol = new THREE.Color('#39b7a9');
  const c = new THREE.Color();
  for (let i = 0; i < MAX; i++) {
    mesh.setMatrixAt(i, hidden);
    mesh.setColorAt(i, white);
    life[i] = 0;
  }

  let cursor = 0;

  function spawn(x, z) {
    const i = cursor;
    cursor = (cursor + 1) % MAX;
    xs[i] = x;
    zs[i] = z;
    life[i] = maxLife[i] = 2.4 + Math.random() * 0.9;
  }

  function update(dt, t) {
    for (let i = 0; i < MAX; i++) {
      if (life[i] <= 0) continue;
      life[i] -= dt;
      if (life[i] <= 0) {
        mesh.setMatrixAt(i, hidden);
        continue;
      }
      const frac = 1 - life[i] / maxLife[i];
      const fade = frac > 0.8 ? (1 - frac) / 0.2 : 1;
      const s = (0.16 + 0.95 * frac) * fade;
      dummy.position.set(xs[i], waveHeight(xs[i], zs[i], t) + 0.05, zs[i]);
      dummy.scale.set(s, Math.max(s * 0.2, 0.001), s);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
      c.copy(white).lerp(waterCol, frac * 0.85); // foam dissolving back into water
      mesh.setColorAt(i, c);
    }
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }

  return { mesh, spawn, update };
}
