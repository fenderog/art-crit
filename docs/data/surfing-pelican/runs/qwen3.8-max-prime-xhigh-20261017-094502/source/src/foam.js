import * as THREE from "three";
import { GLSL_SKY_COMMON } from "./glsl-common.js";
import { oceanHeight } from "./waves.js";
import { lerp, clamp, smoothstep } from "./util.js";

/* ------------------------------------------------------------------ spray */

const SPRAY_VERT = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
uniform float uScale;
varying float vAlpha;
void main() {
  vAlpha = aAlpha;
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = max(1.0, aSize * uScale / max(0.05, -mv.z));
  gl_Position = projectionMatrix * mv;
}
`;

const SPRAY_FRAG = /* glsl */ `
uniform sampler2D uTex;
uniform vec3 uTint;
varying float vAlpha;
void main() {
  vec4 tex = texture2D(uTex, gl_PointCoord);
  float a = tex.a * vAlpha;
  if (a < 0.012) discard;
  gl_FragColor = vec4(tex.rgb * uTint, a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSpray({ texture, count = 700 }) {
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);
  const vel = new Float32Array(count * 3);
  const life = new Float32Array(count);
  const maxLife = new Float32Array(count);
  const baseSize = new Float32Array(count);

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
  geometry.setAttribute("aAlpha", new THREE.BufferAttribute(alphas, 1));
  geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 60);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTex: { value: texture },
      uScale: { value: 600 },
      uTint: { value: new THREE.Color("#fffaf0") },
    },
    vertexShader: SPRAY_VERT,
    fragmentShader: SPRAY_FRAG,
    transparent: true,
    depthWrite: false,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 3;

  let cursor = 0;

  function emit(o) {
    const i = cursor;
    cursor = (cursor + 1) % count;
    const i3 = i * 3;
    positions[i3] = o.x;
    positions[i3 + 1] = o.y;
    positions[i3 + 2] = o.z;
    const s = o.speed;
    vel[i3] = (o.dx + (Math.random() - 0.5) * o.spread) * s;
    vel[i3 + 1] = (o.dy + Math.random() * o.spread * 0.9) * s;
    vel[i3 + 2] = (o.dz + (Math.random() - 0.5) * o.spread) * s;
    maxLife[i] = life[i] = o.life * (0.65 + Math.random() * 0.7);
    baseSize[i] = o.size * (0.55 + Math.random() * 0.9);
    sizes[i] = baseSize[i];
    alphas[i] = o.alpha === undefined ? 0.9 : o.alpha;
  }

  function update(dt, time) {
    for (let i = 0; i < count; i++) {
      if (life[i] <= 0) {
        if (alphas[i] !== 0) {
          alphas[i] = 0;
          sizes[i] = 0;
        }
        continue;
      }
      life[i] -= dt;
      const i3 = i * 3;
      // gravity + drag + a little wind
      vel[i3 + 1] -= 9.2 * dt;
      const drag = Math.exp(-1.9 * dt);
      vel[i3] *= drag;
      vel[i3 + 1] *= drag;
      vel[i3 + 2] *= drag;
      positions[i3] += vel[i3] * dt;
      positions[i3 + 1] += vel[i3 + 1] * dt;
      positions[i3 + 2] += vel[i3 + 2] * dt;

      const k = clamp(life[i] / maxLife[i], 0, 1);
      alphas[i] = Math.pow(k, 0.7) * 0.95;
      sizes[i] = baseSize[i] * (1 + (1 - k) * 0.9);

      // dissolve on contact with the sea
      const surf = oceanHeight(positions[i3], positions[i3 + 2], time);
      if (positions[i3 + 1] < surf + 0.005 && vel[i3 + 1] < 0) {
        life[i] = Math.min(life[i], 0.12);
      }
    }
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.aSize.needsUpdate = true;
    geometry.attributes.aAlpha.needsUpdate = true;
  }

  return {
    points,
    material,
    emit,
    update,
    setScale(h, fov) {
      material.uniforms.uScale.value = h / (2 * Math.tan((fov * Math.PI) / 360));
    },
  };
}

/* ------------------------------------------------------------------- wake */

const WAKE_VERT = /* glsl */ `
attribute float aAge;
attribute float aSide;
varying float vAge;
varying float vSide;
varying vec3 vWorld;
void main() {
  vAge = aAge;
  vSide = aSide;
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vWorld = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const WAKE_FRAG = /* glsl */ `
uniform float uTime;
uniform vec3 uFoam;
uniform vec3 uShade;
varying float vAge;
varying float vSide;
varying vec3 vWorld;
${GLSL_SKY_COMMON}
void main() {
  float dist = length(cameraPosition - vWorld);
  float n = fbm(vWorld.xz * 3.1 + vec2(uTime * 0.35, -uTime * 0.22));
  float n2 = fbm(vWorld.xz * 9.0 - vec2(uTime * 0.6, uTime * 0.3));
  float body = smoothstep(0.24, 0.8, n * 0.7 + n2 * 0.5);
  float along = pow(1.0 - clamp(vAge, 0.0, 1.0), 1.35);
  float across = smoothstep(1.0, 0.25, abs(vSide));
  float a = body * along * across;
  a *= smoothstep(420.0, 90.0, dist);
  if (a < 0.01) discard;
  vec3 col = mix(uShade, uFoam, clamp(n * 0.9 + along * 0.4, 0.0, 1.0));
  gl_FragColor = vec4(col, a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createWake({ length = 128, interval = 0.04 }) {
  const pts = [];
  const positions = new Float32Array(length * 2 * 3);
  const ages = new Float32Array(length * 2);
  const sides = new Float32Array(length * 2);
  const indices = [];

  for (let i = 0; i < length; i++) {
    const age = i / (length - 1);
    ages[i * 2] = age;
    ages[i * 2 + 1] = age;
    sides[i * 2] = -1;
    sides[i * 2 + 1] = 1;
    if (i < length - 1) {
      const a = i * 2;
      indices.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aAge", new THREE.BufferAttribute(ages, 1));
  geometry.setAttribute("aSide", new THREE.BufferAttribute(sides, 1));
  geometry.setIndex(indices);
  geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 80);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uFoam: { value: new THREE.Color("#f2fcff") },
      uShade: { value: new THREE.Color("#9fd8dc") },
    },
    vertexShader: WAKE_VERT,
    fragmentShader: WAKE_FRAG,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = 2;
  mesh.visible = false;

  let acc = 0;
  const _t = new THREE.Vector3();
  const _n = new THREE.Vector3();

  function update(dt, time, tailWorld, halfWidth) {
    acc += dt;
    if (acc >= interval) {
      acc = 0;
      pts.unshift({ x: tailWorld.x, z: tailWorld.z });
      if (pts.length > length) pts.length = length;
    }
    material.uniforms.uTime.value = time;
    if (pts.length < 4) return;
    mesh.visible = true;

    for (let i = 0; i < length; i++) {
      const k = Math.min(i, pts.length - 1);
      const p = pts[k];
      const age = pts.length > 1 ? i / (pts.length - 1) : 1;
      // direction along the trail
      const pn = pts[Math.max(0, k - 1)];
      const pp = pts[Math.min(pts.length - 1, k + 1)];
      _t.set(pn.x - pp.x, 0, pn.z - pp.z);
      if (_t.lengthSq() < 1e-8) _t.set(1, 0, 0);
      _t.normalize();
      // sideways on the water surface
      _n.set(-_t.z, 0, _t.x);
      const surf = oceanHeight(p.x, p.z, time);
      const w = lerp(halfWidth * 0.55, halfWidth * 3.1, Math.pow(clamp(age, 0, 1), 0.7));
      const y = surf + 0.014 + 0.02 * (1 - age);
      const i6 = i * 6;
      positions[i6] = p.x - _n.x * w;
      positions[i6 + 1] = y;
      positions[i6 + 2] = p.z - _n.z * w;
      positions[i6 + 3] = p.x + _n.x * w;
      positions[i6 + 4] = y;
      positions[i6 + 5] = p.z + _n.z * w;
    }
    geometry.attributes.position.needsUpdate = true;
    geometry.computeBoundingSphere();
  }

  return { mesh, material, update, clear: () => (pts.length = 0) };
}

/* --------------------------------------------------------- contact shadow */

export function createContactShadow({ texture }) {
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({
      map: texture,
      color: new THREE.Color("#03222e"),
      transparent: true,
      opacity: 0.55,
      depthWrite: false,
    })
  );
  mesh.renderOrder = 1;
  mesh.frustumCulled = false;

  const up = new THREE.Vector3(0, 0, 1);
  const _n = new THREE.Vector3();

  function update(time, x, z, normal, sizeX, sizeZ, strength) {
    const surf = oceanHeight(x, z, time);
    mesh.position.set(x, surf + 0.02, z);
    _n.copy(normal);
    mesh.quaternion.setFromUnitVectors(up, _n);
    mesh.scale.set(sizeX, sizeZ, 1);
    mesh.material.opacity = strength;
  }

  return { mesh, update };
}

/* ------------------------------------------------------------- mist puffs */

/** Lazy drifting mist near the horizon so the sea does not look empty. */
export function createMist({ texture, count = 26 }) {
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);
  const seeds = [];
  for (let i = 0; i < count; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = 60 + Math.random() * 320;
    positions[i * 3] = Math.cos(a) * r;
    positions[i * 3 + 1] = 0.6 + Math.random() * 5.5;
    positions[i * 3 + 2] = Math.sin(a) * r;
    sizes[i] = 26 + Math.random() * 70;
    alphas[i] = 0.05 + Math.random() * 0.13;
    seeds.push({ sp: 0.4 + Math.random() * 1.4, ph: Math.random() * 10, x: positions[i * 3], z: positions[i * 3 + 2], y: positions[i * 3 + 1] });
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
  geometry.setAttribute("aAlpha", new THREE.BufferAttribute(alphas, 1));
  geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 600);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTex: { value: texture },
      uScale: { value: 600 },
      uTint: { value: new THREE.Color("#ffe6c4") },
    },
    vertexShader: SPRAY_VERT,
    fragmentShader: SPRAY_FRAG,
    transparent: true,
    depthWrite: false,
  });
  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.renderOrder = 0;

  function update(dt, time) {
    for (let i = 0; i < count; i++) {
      const s = seeds[i];
      positions[i * 3] = s.x + Math.sin(time * 0.02 * s.sp + s.ph) * 12;
      positions[i * 3 + 1] = s.y + Math.sin(time * 0.05 + s.ph) * 0.8;
      positions[i * 3 + 2] = s.z + Math.cos(time * 0.017 * s.sp + s.ph) * 12;
    }
    geometry.attributes.position.needsUpdate = true;
  }

  return {
    points,
    material,
    update,
    setScale(h, fov) {
      material.uniforms.uScale.value = h / (2 * Math.tan((fov * Math.PI) / 360));
    },
  };
}
