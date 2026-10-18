import * as THREE from 'three';
import { makeSoftCircleTexture, mulberry32 } from './utils.js';

export function createSpray(scene, boardGroup) {
  const count = 280;
  const rand = mulberry32(1987);
  const positions = new Float32Array(count * 3);
  const aLife = new Float32Array(count);
  const aSize = new Float32Array(count);
  const aWarmth = new Float32Array(count);

  const velocity = Array.from({ length: count }, () => new THREE.Vector3());
  const lifetime = new Float32Array(count);
  const maxLifetime = new Float32Array(count);
  const active = new Uint8Array(count);

  for (let i = 0; i < count; i++) {
    positions[i * 3 + 1] = -100;
    aSize[i] = 0.05;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('aLife', new THREE.BufferAttribute(aLife, 1));
  geometry.setAttribute('aSize', new THREE.BufferAttribute(aSize, 1));
  geometry.setAttribute('aWarmth', new THREE.BufferAttribute(aWarmth, 1));

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: makeSoftCircleTexture(128) },
      uColorA: { value: new THREE.Color(0xfff7e7) },
      uColorB: { value: new THREE.Color(0xffbd8c) }
    },
    vertexShader: /* glsl */ `
      attribute float aLife;
      attribute float aSize;
      attribute float aWarmth;
      varying float vLife;
      varying float vWarmth;

      void main() {
        vLife = aLife;
        vWarmth = aWarmth;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        float perspective = 270.0 / max(1.0, -mvPosition.z);
        gl_PointSize = aSize * perspective;
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap;
      uniform vec3 uColorA;
      uniform vec3 uColorB;
      varying float vLife;
      varying float vWarmth;

      void main() {
        float mask = texture2D(uMap, gl_PointCoord).a;
        float fadeIn = smoothstep(0.0, 0.15, vLife);
        float fadeOut = smoothstep(1.0, 0.72, vLife);
        float alpha = mask * fadeIn * fadeOut * 0.72;
        if (alpha < 0.005) discard;
        vec3 color = mix(uColorA, uColorB, vWarmth);
        gl_FragColor = vec4(color, alpha);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.NormalBlending
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 4;
  scene.add(points);

  let cursor = 0;
  let accumulator = 0;

  const localPos = new THREE.Vector3();
  const worldPos = new THREE.Vector3();
  const localVel = new THREE.Vector3();
  const worldVel = new THREE.Vector3();
  const worldUp = new THREE.Vector3(0, 1, 0);

  function spawn() {
    if (cursor >= count) cursor = 0;
    const i = cursor++;

    const tail = rand() < 0.72;
    if (tail) {
      localPos.set(1.22 + rand() * 0.42, 0.055 + rand() * 0.055, (rand() - 0.5) * 0.48);
      localVel.set(0.35 + rand() * 1.35, 1.0 + rand() * 2.9, (rand() - 0.5) * 1.15);
    } else {
      localPos.set(-1.08 + rand() * 0.7, 0.045, (rand() > 0.5 ? 1 : -1) * (0.3 + rand() * 0.18));
      localVel.set(-0.25 + rand() * 1.25, 1.35 + rand() * 3.2, (rand() - 0.5) * 1.7);
    }

    boardGroup.localToWorld(worldPos.copy(localPos));
    worldVel.copy(localVel).applyQuaternion(boardGroup.quaternion);
    worldVel.x += 0.25;
    worldVel.y += 0.35;

    positions[i * 3] = worldPos.x;
    positions[i * 3 + 1] = worldPos.y;
    positions[i * 3 + 2] = worldPos.z;

    velocity[i].copy(worldVel);
    lifetime[i] = 0.72 + rand() * 1.0;
    maxLifetime[i] = lifetime[i];
    active[i] = 1;
    aLife[i] = 1;
    aSize[i] = 0.035 + Math.pow(rand(), 2.2) * 0.23 + (tail ? 0.025 : 0);
    aWarmth[i] = rand() * 0.7;
  }

  function update(t, dt) {
    accumulator += dt * 125;
    let spawns = 0;
    while (accumulator >= 1 && spawns < 8) {
      spawn();
      accumulator -= 1;
      spawns++;
    }

    for (let i = 0; i < count; i++) {
      if (!active[i]) continue;
      lifetime[i] -= dt;
      if (lifetime[i] <= 0) {
        active[i] = 0;
        aLife[i] = 0;
        positions[i * 3 + 1] = -100;
        continue;
      }

      const lifeRatio = lifetime[i] / maxLifetime[i];
      aLife[i] = lifeRatio;
      if (lifeRatio < 0.2) aSize[i] *= 1.0 - dt * 1.4;

      const v = velocity[i];
      v.y -= 7.4 * dt;
      v.x += 0.35 * dt;
      v.multiplyScalar(1.0 - Math.min(0.5, dt * 0.6));
      positions[i * 3] += v.x * dt;
      positions[i * 3 + 1] += v.y * dt;
      positions[i * 3 + 2] += v.z * dt;
    }

    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.aLife.needsUpdate = true;
    geometry.attributes.aSize.needsUpdate = true;
    geometry.attributes.aWarmth.needsUpdate = true;
  }

  return { points, update };
}
