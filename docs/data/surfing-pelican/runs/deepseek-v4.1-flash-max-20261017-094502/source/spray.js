// CPU particle system used for the spray and foam kicked up by the board.
// One THREE.Points object with per-particle size and alpha attributes.

import * as THREE from 'three';

const VERTEX = /* glsl */ `
  attribute float aSize;
  attribute float aAlpha;

  uniform float uPixelRatio;

  varying float vAlpha;

  void main() {
    vAlpha = aAlpha;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = aSize * uPixelRatio * 320.0 / max(-mv.z, 0.1);
    gl_Position = projectionMatrix * mv;
  }
`;

const FRAGMENT = /* glsl */ `
  precision mediump float;

  uniform sampler2D uMap;
  varying float vAlpha;

  void main() {
    float a = texture2D(uMap, gl_PointCoord).a * vAlpha;
    if (a < 0.003) discard;
    gl_FragColor = vec4(vec3(0.94, 0.98, 1.0), a);
  }
`;

function makeDropletTexture() {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0.0, 'rgba(255,255,255,1)');
  g.addColorStop(0.42, 'rgba(255,255,255,0.72)');
  g.addColorStop(1.0, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createSpray({ max = 1000 } = {}) {
  const positions = new Float32Array(max * 3);
  const sizes = new Float32Array(max);
  const alphas = new Float32Array(max);
  const velocities = new Float32Array(max * 3);
  const life = new Float32Array(max);
  const maxLife = new Float32Array(max);
  const baseSize = new Float32Array(max);
  const baseAlpha = new Float32Array(max);
  let cursor = 0;

  const geometry = new THREE.BufferGeometry();
  const posAttr = new THREE.BufferAttribute(positions, 3).setUsage(THREE.DynamicDrawUsage);
  const sizeAttr = new THREE.BufferAttribute(sizes, 1).setUsage(THREE.DynamicDrawUsage);
  const alphaAttr = new THREE.BufferAttribute(alphas, 1).setUsage(THREE.DynamicDrawUsage);
  geometry.setAttribute('position', posAttr);
  geometry.setAttribute('aSize', sizeAttr);
  geometry.setAttribute('aAlpha', alphaAttr);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: makeDropletTexture() },
      uPixelRatio: { value: 1 },
    },
    vertexShader: VERTEX,
    fragmentShader: FRAGMENT,
    transparent: true,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;

  function emit(x, y, z, vx, vy, vz, size, alpha, lifetime) {
    const i = cursor;
    cursor = (cursor + 1) % max;

    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;
    velocities[i * 3] = vx;
    velocities[i * 3 + 1] = vy;
    velocities[i * 3 + 2] = vz;
    life[i] = lifetime;
    maxLife[i] = lifetime;
    baseSize[i] = size;
    baseAlpha[i] = alpha;
    sizes[i] = size;
    alphas[i] = alpha;
  }

  function update(dt) {
    for (let i = 0; i < max; i++) {
      if (life[i] <= 0) {
        alphas[i] = 0;
        continue;
      }
      life[i] -= dt;

      if (life[i] <= 0) {
        alphas[i] = 0;
        continue;
      }

      const drag = Math.exp(-1.15 * dt);
      velocities[i * 3] *= drag;
      velocities[i * 3 + 1] = velocities[i * 3 + 1] * drag - 7.6 * dt;
      velocities[i * 3 + 2] *= drag;

      positions[i * 3] += velocities[i * 3] * dt;
      positions[i * 3 + 1] += velocities[i * 3 + 1] * dt;
      positions[i * 3 + 2] += velocities[i * 3 + 2] * dt;

      const progress = 1 - life[i] / maxLife[i];
      const fadeIn = Math.min(1, progress * 7.0);
      alphas[i] = baseAlpha[i] * fadeIn * (1 - progress) * (1 - progress * 0.25);
      sizes[i] = baseSize[i] * (1 + progress * 1.1);
    }

    posAttr.needsUpdate = true;
    sizeAttr.needsUpdate = true;
    alphaAttr.needsUpdate = true;
  }

  function setPixelRatio(ratio) {
    material.uniforms.uPixelRatio.value = ratio;
  }

  return { points, emit, update, setPixelRatio };
}
