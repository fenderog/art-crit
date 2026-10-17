import * as THREE from 'three';

// A pool of recycled water-spray particles rendered as soft additive points.
export function createSpray(count = 900) {
  const positions = new Float32Array(count * 3);
  const alphas = new Float32Array(count);
  const sizes = new Float32Array(count);
  const velocities = new Float32Array(count * 3);
  const lives = new Float32Array(count);
  const maxLives = new Float32Array(count);
  let cursor = 0;

  // Park all particles far below the world until they are emitted.
  for (let i = 0; i < count; i++) {
    positions[i * 3 + 1] = -1000;
    alphas[i] = 0;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));
  geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));

  const material = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    blending: THREE.NormalBlending,
    uniforms: {},
    vertexShader: /* glsl */ `
      attribute float aAlpha;
      attribute float aSize;
      varying float vAlpha;
      void main() {
        vAlpha = aAlpha;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aSize * (320.0 / max(-mv.z, 0.001));
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: /* glsl */ `
      varying float vAlpha;
      void main() {
        vec2 d = gl_PointCoord - vec2(0.5);
        float r = length(d);
        float a = smoothstep(0.5, 0.08, r) * vAlpha;
        if (a <= 0.001) discard;
        gl_FragColor = vec4(0.96, 0.99, 1.0, a);
      }
    `,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;

  const attrPos = geometry.getAttribute('position');
  const attrAlpha = geometry.getAttribute('aAlpha');
  const attrSize = geometry.getAttribute('aSize');

  function spawn(position, velocity, size, life) {
    const i = cursor;
    cursor = (cursor + 1) % count;
    const i3 = i * 3;
    positions[i3] = position.x;
    positions[i3 + 1] = position.y;
    positions[i3 + 2] = position.z;
    velocities[i3] = velocity.x;
    velocities[i3 + 1] = velocity.y;
    velocities[i3 + 2] = velocity.z;
    lives[i] = life;
    maxLives[i] = life;
    sizes[i] = size;
    alphas[i] = 0.9;
  }

  function update(dt) {
    for (let i = 0; i < count; i++) {
      if (lives[i] <= 0) continue;
      const i3 = i * 3;
      lives[i] -= dt;
      if (lives[i] <= 0) {
        alphas[i] = 0;
        positions[i3 + 1] = -1000;
        continue;
      }
      velocities[i3 + 1] -= 7.5 * dt;
      positions[i3] += velocities[i3] * dt;
      positions[i3 + 1] += velocities[i3 + 1] * dt;
      positions[i3 + 2] += velocities[i3 + 2] * dt;
      alphas[i] = Math.min(1, lives[i] / maxLives[i]) * 0.9;
    }
    attrPos.needsUpdate = true;
    attrAlpha.needsUpdate = true;
    attrSize.needsUpdate = true;
  }

  return { points, spawn, update };
}
