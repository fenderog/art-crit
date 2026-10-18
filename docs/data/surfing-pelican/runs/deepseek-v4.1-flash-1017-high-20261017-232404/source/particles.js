import * as THREE from 'three';
import { sampleOcean } from './ocean.js';
import { makeSprayTexture } from './textures.js';

const COUNT = 620;

const vertexShader = /* glsl */ `
uniform float uPixelRatio;
attribute float aSize;
attribute float aAlpha;
varying float vAlpha;

void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = aSize * uPixelRatio * (330.0 / max(-mv.z, 0.1));
  gl_Position = projectionMatrix * mv;
  vAlpha = aAlpha;
}
`;

const fragmentShader = /* glsl */ `
uniform sampler2D uMap;
varying float vAlpha;

void main() {
  vec4 tex = texture2D(uMap, gl_PointCoord);
  if (tex.a < 0.012) discard;
  gl_FragColor = vec4(0.93, 0.985, 1.0, tex.a * vAlpha);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSpray() {
  const positions = new Float32Array(COUNT * 3);
  const sizes = new Float32Array(COUNT);
  const alphas = new Float32Array(COUNT);

  const vx = new Float32Array(COUNT);
  const vy = new Float32Array(COUNT);
  const vz = new Float32Array(COUNT);
  const age = new Float32Array(COUNT);
  const life = new Float32Array(COUNT);
  const size0 = new Float32Array(COUNT);
  const growth = new Float32Array(COUNT);
  const kind = new Uint8Array(COUNT);
  const alive = new Uint8Array(COUNT);

  const geometry = new THREE.BufferGeometry();
  const positionAttr = new THREE.BufferAttribute(positions, 3);
  const sizeAttr = new THREE.BufferAttribute(sizes, 1);
  const alphaAttr = new THREE.BufferAttribute(alphas, 1);
  positionAttr.setUsage(THREE.DynamicDrawUsage);
  sizeAttr.setUsage(THREE.DynamicDrawUsage);
  alphaAttr.setUsage(THREE.DynamicDrawUsage);
  geometry.setAttribute('position', positionAttr);
  geometry.setAttribute('aSize', sizeAttr);
  geometry.setAttribute('aAlpha', alphaAttr);
  geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: makeSprayTexture() },
      uPixelRatio: { value: Math.min(window.devicePixelRatio || 1, 2) },
    },
    vertexShader,
    fragmentShader,
    transparent: true,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 3;

  let cursor = 0;
  let sprayAccum = 0;
  let wakeAccum = 0;
  let sideAccum = 0;

  const tmpLocal = new THREE.Vector3();
  const tmpWorld = new THREE.Vector3();

  function spawn(type, origin, rider, time) {
    let index = -1;
    for (let n = 0; n < COUNT; n++) {
      const i = (cursor + n) % COUNT;
      if (!alive[i]) {
        index = i;
        cursor = (i + 1) % COUNT;
        break;
      }
    }
    if (index < 0) return;

    const i3 = index * 3;
    const f = rider.forward;
    const r = rider.right;

    positions[i3] = origin.x;
    positions[i3 + 1] = origin.y;
    positions[i3 + 2] = origin.z;

    if (type === 0) {
      // Bow spray: a quick fan of droplets thrown up and outward.
      const lateral = (Math.random() - 0.3) * 2.0;
      vx[index] = r.x * lateral + f.x * (0.15 + Math.random() * 0.35);
      vy[index] = 0.9 + Math.random() * 2.1;
      vz[index] = r.z * lateral + f.z * (0.15 + Math.random() * 0.35);
      life[index] = 0.45 + Math.random() * 0.65;
      size0[index] = 0.12 + Math.random() * 0.22;
      growth[index] = 1.7;
      kind[index] = 0;
    } else if (type === 1) {
      // Wake: foam dragged off the tail, then left behind on the surface.
      const lateral = (Math.random() - 0.5) * 1.1;
      const back = 0.35 + Math.random() * 1.1;
      vx[index] = -f.x * back + r.x * lateral;
      vy[index] = 0.15 + Math.random() * 0.3;
      vz[index] = -f.z * back + r.z * lateral;
      life[index] = 1.2 + Math.random() * 1.3;
      size0[index] = 0.07 + Math.random() * 0.14;
      growth[index] = 2.3;
      kind[index] = 1;
    } else {
      // Foam peeling off the board's waterline.
      const lateral = (Math.random() < 0.5 ? -1 : 1) * (0.25 + Math.random() * 0.55);
      vx[index] = r.x * lateral;
      vy[index] = 0.1;
      vz[index] = r.z * lateral;
      life[index] = 0.6 + Math.random() * 0.8;
      size0[index] = 0.04 + Math.random() * 0.08;
      growth[index] = 1.8;
      kind[index] = 1;
    }

    age[index] = 0;
    alphas[index] = 0;
    sizes[index] = size0[index];
    alive[index] = 1;
  }

  return {
    points,
    update(dt, time, rider) {
      rider.group.updateMatrixWorld(true);

      sprayAccum += dt * 92;
      wakeAccum += dt * 155;
      sideAccum += dt * 42;

      while (sprayAccum >= 1) {
        sprayAccum -= 1;
        tmpLocal.set(
          (Math.random() - 0.5) * 0.5,
          0.05 + Math.random() * 0.12,
          1.2 + Math.random() * 0.4
        );
        tmpWorld.copy(tmpLocal).applyMatrix4(rider.group.matrixWorld);
        spawn(0, tmpWorld, rider, time);
      }

      while (wakeAccum >= 1) {
        wakeAccum -= 1;
        tmpLocal.set(
          (Math.random() - 0.5) * 0.65,
          0.05,
          -1.35 - Math.random() * 0.35
        );
        tmpWorld.copy(tmpLocal).applyMatrix4(rider.group.matrixWorld);
        spawn(1, tmpWorld, rider, time);
      }

      while (sideAccum >= 1) {
        sideAccum -= 1;
        tmpLocal.set(
          (Math.random() < 0.5 ? -1 : 1) * (0.45 + Math.random() * 0.25),
          0.02,
          -0.1 + Math.random() * 1.2
        );
        tmpWorld.copy(tmpLocal).applyMatrix4(rider.group.matrixWorld);
        spawn(2, tmpWorld, rider, time);
      }

      for (let i = 0; i < COUNT; i++) {
        if (!alive[i]) {
          alphas[i] = 0;
          continue;
        }

        age[i] += dt;
        if (age[i] >= life[i]) {
          alive[i] = 0;
          alphas[i] = 0;
          continue;
        }

        const i3 = i * 3;
        if (kind[i] === 0) {
          vy[i] -= 5.4 * dt;
          positions[i3] += vx[i] * dt;
          positions[i3 + 1] += vy[i] * dt;
          positions[i3 + 2] += vz[i] * dt;

          const surface = sampleOcean(positions[i3], positions[i3 + 2], time).height;
          if (positions[i3 + 1] < surface + 0.02) {
            positions[i3 + 1] = surface + 0.02;
            vy[i] = 0;
            vx[i] *= 0.92;
            vz[i] *= 0.92;
            age[i] += dt * 2.4;
          }
        } else {
          positions[i3] += vx[i] * dt;
          positions[i3 + 2] += vz[i] * dt;
          const surface = sampleOcean(positions[i3], positions[i3 + 2], time).height;
          positions[i3 + 1] = surface + 0.035;
          vx[i] *= 1 - 1.1 * dt;
          vz[i] *= 1 - 1.1 * dt;
        }

        const t = age[i] / life[i];
        const fadeIn = Math.min(age[i] / 0.09, 1);
        const fadeOut = 1 - t * t;
        alphas[i] = fadeIn * fadeOut * 0.9;
        sizes[i] = size0[i] * (1 + growth[i] * t);
      }

      positionAttr.needsUpdate = true;
      sizeAttr.needsUpdate = true;
      alphaAttr.needsUpdate = true;
    },
  };
}
