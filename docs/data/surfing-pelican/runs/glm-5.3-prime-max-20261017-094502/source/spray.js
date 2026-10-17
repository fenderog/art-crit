import * as THREE from 'three';
import { waveHeight } from './water.js';

const MAX = 110;

// Droplets kicked off the nose and carving rail.
export function createSpray() {
  const geo = new THREE.IcosahedronGeometry(1, 0);
  const mat = new THREE.MeshStandardMaterial({
    color: '#ffffff',
    flatShading: true,
    roughness: 0.35,
    transparent: true,
    opacity: 0.88,
  });
  const mesh = new THREE.InstancedMesh(geo, mat, MAX);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  mesh.frustumCulled = false;

  const pos = new Float32Array(MAX * 3);
  const vel = new Float32Array(MAX * 3);
  const life = new Float32Array(MAX);
  const maxLife = new Float32Array(MAX);
  const size = new Float32Array(MAX);
  const spin = [];
  for (let i = 0; i < MAX; i++) {
    spin.push(new THREE.Euler(Math.random() * 3, Math.random() * 3, Math.random() * 3));
  }

  const dummy = new THREE.Object3D();
  const hidden = new THREE.Matrix4().makeScale(0, 0, 0);
  for (let i = 0; i < MAX; i++) {
    mesh.setMatrixAt(i, hidden);
  }
  life.fill(0);

  let cursor = 0;

  function spawn(x, y, z, vx, vy, vz) {
    const i = cursor;
    cursor = (cursor + 1) % MAX;
    pos[i * 3] = x;
    pos[i * 3 + 1] = y;
    pos[i * 3 + 2] = z;
    vel[i * 3] = vx;
    vel[i * 3 + 1] = vy;
    vel[i * 3 + 2] = vz;
    life[i] = maxLife[i] = 0.45 + Math.random() * 0.5;
    size[i] = 0.035 + Math.random() * 0.055;
  }

  function update(dt, t) {
    for (let i = 0; i < MAX; i++) {
      if (life[i] <= 0) continue;
      life[i] -= dt;
      vel[i * 3 + 1] -= 7.5 * dt; // gravity
      pos[i * 3] += vel[i * 3] * dt;
      pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
      pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
      if (life[i] <= 0 || pos[i * 3 + 1] < waveHeight(pos[i * 3], pos[i * 3 + 2], t) + 0.02) {
        life[i] = 0;
        mesh.setMatrixAt(i, hidden);
        continue;
      }
      const frac = 1 - life[i] / maxLife[i];
      const s = size[i] * Math.sin(Math.PI * frac) + 0.004;
      dummy.position.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
      dummy.rotation.copy(spin[i]);
      dummy.scale.setScalar(s);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  }

  return { mesh, spawn, update };
}
