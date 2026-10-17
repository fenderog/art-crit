// spray.js — water thrown up by the board and by diving fish, plus the
// expanding rings they leave on the surface. The particles are integrated on
// the GPU (damped ballistic paths), so a few hundred of them cost nothing.

import * as THREE from 'three';

const VERT = /* glsl */ `
attribute vec3 aVel;
attribute vec4 aData;   // x: birth, y: life, z: world size, w: alpha

uniform float uTime;
uniform float uSizeScale;

varying float vA;

void main() {
  float age = uTime - aData.x;
  float life = max(aData.y, 0.0001);
  if (age < 0.0 || age > life) {
    gl_Position = vec4(0.0, 0.0, 2.0, 1.0);
    vA = 0.0;
    return;
  }
  float k = 2.4;                                   // air drag
  vec3 p = position
         + aVel * ((1.0 - exp(-k * age)) / k)
         + vec3(0.0, -9.5, 0.0) * age * age * 0.5  // gravity
         + vec3(-1.1, 0.25, -0.8) * age * 0.35;    // wind
  vec4 mv = modelViewMatrix * vec4(p, 1.0);
  vA = smoothstep(0.0, 0.10, age) * (1.0 - smoothstep(life * 0.28, life, age)) * aData.w;
  gl_PointSize = aData.z * uSizeScale / max(0.35, -mv.z);
  gl_Position = projectionMatrix * mv;
}
`;

const FRAG = /* glsl */ `
precision mediump float;
uniform vec3 uColor;
varying float vA;
void main() {
  float r = length(gl_PointCoord - 0.5) * 2.0;
  float a = smoothstep(1.0, 0.2, r);
  if (a * vA < 0.004) discard;
  gl_FragColor = vec4(uColor, a * vA);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSpray(parent, canvasHeight0) {
  const COUNT = 320;

  const origin = new Float32Array(COUNT * 3);
  const vel = new Float32Array(COUNT * 3);
  const data = new Float32Array(COUNT * 4);

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(origin, 3));
  geometry.setAttribute('aVel', new THREE.BufferAttribute(vel, 3));
  geometry.setAttribute('aData', new THREE.BufferAttribute(data, 4));

  const uniforms = {
    uTime: { value: 0 },
    uSizeScale: { value: canvasHeight0 * 0.5 },
    uColor: { value: new THREE.Color(0xffffff) },
  };

  const material = new THREE.ShaderMaterial({
    vertexShader: VERT,
    fragmentShader: FRAG,
    uniforms,
    transparent: true,
    depthWrite: false,
    blending: THREE.NormalBlending,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 5;
  parent.add(points);

  const attrs = {
    position: geometry.attributes.position,
    aVel: geometry.attributes.aVel,
    aData: geometry.attributes.aData,
  };

  let cursor = 0;

  /**
   * Throw `count` droplets from local point (ox, oy, oz).
   * dir = unit direction, spread = cone half angle in radians.
   */
  function emit(count, ox, oy, oz, dir, spread, opts = {}) {
    const up = opts.up ?? 1.0;
    const speed = opts.speed ?? 3.4;
    const size = opts.size ?? 0.05;
    const life = opts.life ?? 1.5;
    const alpha = opts.alpha ?? 0.85;
    const birth = uniforms.uTime.value;
    for (let i = 0; i < count; i++) {
      const idx = cursor % COUNT;
      cursor++;
      // random direction inside the cone
      const a = Math.random() * Math.PI * 2;
      const s = Math.tan(spread * Math.sqrt(Math.random()));
      const side = Math.random() * 2 - 1;
      let dx = dir.x + s * (Math.cos(a) * 0.9 + side * 0.35);
      let dy = dir.y + s * (Math.sin(a) * 0.9) * up;
      let dz = dir.z + s * (Math.sin(a) * 0.3 + side * 0.9);
      const l = Math.hypot(dx, dy, dz) || 1;
      dx /= l;
      dy /= l;
      dz /= l;
      const sp = speed * (0.55 + Math.random() * 0.9);
      attrs.position.array[idx * 3] = ox;
      attrs.position.array[idx * 3 + 1] = oy;
      attrs.position.array[idx * 3 + 2] = oz;
      attrs.aVel.array[idx * 3] = dx * sp;
      attrs.aVel.array[idx * 3 + 1] = dy * sp;
      attrs.aVel.array[idx * 3 + 2] = dz * sp;
      attrs.aData.array[idx * 4] = birth - Math.random() * 0.05;
      attrs.aData.array[idx * 4 + 1] = life * (0.6 + Math.random() * 0.8);
      attrs.aData.array[idx * 4 + 2] = size * (0.6 + Math.random() * 0.9);
      attrs.aData.array[idx * 4 + 3] = alpha * (0.6 + Math.random() * 0.7);
    }
    attrs.position.needsUpdate = true;
    attrs.aVel.needsUpdate = true;
    attrs.aData.needsUpdate = true;
  }

  return {
    points,
    uniforms,
    emit,
    setPixelScale(px) {
      uniforms.uSizeScale.value = px;
    },
  };
}

export function createRipples(scene) {
  const rings = [];
  const geo = new THREE.RingGeometry(0.55, 1.0, 56, 1);
  geo.rotateX(-Math.PI / 2);
  for (let i = 0; i < 4; i++) {
    const mat = new THREE.MeshBasicMaterial({
      color: 0xeaf6fa,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      side: THREE.DoubleSide,
      fog: false,
    });
    const m = new THREE.Mesh(geo, mat);
    m.visible = false;
    m.renderOrder = 3;
    scene.add(m);
    rings.push({ mesh: m, age: 99, life: 1.6, size: 1 });
  }
  let cursor = 0;

  return {
    /** spawn a ring at world position with a final radius */
    spawn(x, y, z, size = 2.6, life = 1.4) {
      const r = rings[cursor % rings.length];
      cursor++;
      r.mesh.position.set(x, y, z);
      r.size = size;
      r.life = life;
      r.age = 0;
      r.mesh.visible = true;
    },
    update(dt, t, waveHeight) {
      for (const r of rings) {
        if (!r.mesh.visible) continue;
        r.age += dt;
        const k = r.age / r.life;
        if (k >= 1) {
          r.mesh.visible = false;
          continue;
        }
        const s = 0.4 + k * r.size;
        r.mesh.scale.setScalar(s);
        r.mesh.position.y = waveHeight(r.mesh.position.x, r.mesh.position.z, t) + 0.04;
        r.mesh.material.opacity = 0.55 * (1 - k) * (1 - k);
      }
    },
  };
}
