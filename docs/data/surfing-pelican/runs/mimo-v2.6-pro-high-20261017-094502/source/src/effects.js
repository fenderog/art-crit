/**
 * Water spray kicked up by the board and the foamy wake it leaves behind.
 */
import * as THREE from "three";
import { softCircleTexture, foamTexture } from "./textures.js";

const PARTICLE_COUNT = 560;

export function createSpray(scene) {
  const positions = new Float32Array(PARTICLE_COUNT * 3);
  const alphas = new Float32Array(PARTICLE_COUNT);
  const sizes = new Float32Array(PARTICLE_COUNT);
  const velocities = new Float32Array(PARTICLE_COUNT * 3);
  const life = new Float32Array(PARTICLE_COUNT);
  const maxLife = new Float32Array(PARTICLE_COUNT);

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    positions[i * 3 + 1] = -9999;
    maxLife[i] = 1;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aAlpha", new THREE.BufferAttribute(alphas, 1));
  geometry.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: softCircleTexture(64) },
      uColor: { value: new THREE.Color(1, 1, 1) },
      uPixelScale: { value: 700 },
    },
    vertexShader: /* glsl */ `
      attribute float aAlpha;
      attribute float aSize;
      uniform float uPixelScale;
      varying float vAlpha;

      void main() {
        vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
        gl_PointSize = aSize * uPixelScale / max( 0.35, -mvPosition.z );
        vAlpha = aAlpha;
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap;
      uniform vec3 uColor;
      varying float vAlpha;

      void main() {
        float a = texture2D( uMap, gl_PointCoord ).a * vAlpha;
        if ( a < 0.01 ) discard;
        gl_FragColor = vec4( uColor, a );
      }
    `,
    transparent: true,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 3;
  scene.add(points);

  let cursor = 0;
  let spawnAccumulator = 0;

  function spawn(origin, backDir) {
    const i = cursor;
    cursor = (cursor + 1) % PARTICLE_COUNT;

    positions[i * 3] = origin.x + (Math.random() - 0.5) * 0.75;
    positions[i * 3 + 1] = origin.y + Math.random() * 0.25;
    positions[i * 3 + 2] = origin.z + (Math.random() - 0.5) * 0.75;

    const speed = 1.4 + Math.random() * 3.6;
    velocities[i * 3] = backDir.x * speed + (Math.random() - 0.5) * 1.5;
    velocities[i * 3 + 1] = 1.4 + Math.random() * 3.2;
    velocities[i * 3 + 2] = backDir.z * speed + (Math.random() - 0.5) * 1.5;

    life[i] = 0;
    maxLife[i] = 0.55 + Math.random() * 0.75;
    sizes[i] = 0.16 + Math.random() * 0.36;
    alphas[i] = 0;
  }

  const backDir = new THREE.Vector3();

  return {
    points,
    setPixelScale(scale) {
      material.uniforms.uPixelScale.value = scale;
    },
    update(dt, origin, rigQuaternion) {
      backDir.set(0, 0, -1).applyQuaternion(rigQuaternion);

      spawnAccumulator += dt * 300;
      while (spawnAccumulator >= 1) {
        spawn(origin, backDir);
        spawnAccumulator -= 1;
      }

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        if (life[i] >= maxLife[i]) {
          alphas[i] = 0;
          positions[i * 3 + 1] = -9999;
          continue;
        }
        life[i] += dt;
        const t = life[i] / maxLife[i];

        velocities[i * 3 + 1] -= 8.6 * dt;
        positions[i * 3] += velocities[i * 3] * dt;
        positions[i * 3 + 1] += velocities[i * 3 + 1] * dt;
        positions[i * 3 + 2] += velocities[i * 3 + 2] * dt;

        alphas[i] = Math.min(1, t * 6) * (1 - t) * 0.95;
      }

      geometry.attributes.position.needsUpdate = true;
      geometry.attributes.aAlpha.needsUpdate = true;
      geometry.attributes.aSize.needsUpdate = true;
    },
  };
}

/** Foamy trail that scrolls backwards behind the board. */
export function createWake(rigGroup) {
  const map = foamTexture(256, 130);
  map.repeat.set(1.4, 1.8);

  const material = new THREE.MeshBasicMaterial({
    map,
    color: 0xeaf7ff,
    transparent: true,
    opacity: 0.24,
    depthWrite: false,
  });

  const wake = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  wake.geometry.rotateX(-Math.PI / 2);
  wake.position.set(0, -0.07, -3.3);
  wake.scale.set(2.3, 1, 5.6);
  wake.renderOrder = 1;
  rigGroup.add(wake);

  return {
    wake,
    update(t) {
      map.offset.y = (t * 0.34) % 1;
      material.opacity = 0.22 + Math.sin(t * 1.4) * 0.05;
    },
  };
}