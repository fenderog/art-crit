import * as THREE from "three";
import { SUN_DIR, PALETTE } from "./sky.js";

// Spray, mist and droplets: a CPU-simulated pool drawn as camera-facing soft quads.
const KIND = { spray: 0, mist: 1, drop: 2 };
export { KIND };

const vert = /* glsl */ `
attribute vec3 aPos;
attribute vec4 aParams; // size, alpha, kind, seed
attribute vec3 aVel;
varying vec2 vUv;
varying vec4 vP;
varying vec3 vWorld;
varying float vNear;
void main() {
  vUv = position.xy * 2.0;
  vP = aParams;
  vWorld = aPos;
  vec4 mv = viewMatrix * vec4(aPos, 1.0);
  vNear = smoothstep(2.5, 7.0, -mv.z);
  if (aParams.z > 0.5 && aParams.z < 1.5) vNear *= smoothstep(4.0, 10.0, -mv.z);
  // rotate quad by a per-particle angle for variety
  float a = aParams.w * 6.2831;
  float c = cos(a), s = sin(a);
  vec2 q = vec2(c * position.x - s * position.y, s * position.x + c * position.y);
  if (aParams.z > 1.5 || (aParams.z < 0.5 && aParams.x < 0.12)) {
    // droplets and fine spray: stretch along the velocity (motion streaks)
    vec3 vv = (viewMatrix * vec4(aVel, 0.0)).xyz;
    vec2 d2 = vv.xy;
    float sp = length(d2);
    if (sp > 0.05) {
      vec2 dir = d2 / sp;
      vec2 perp = vec2(-dir.y, dir.x);
      float lenS = aParams.x * (1.0 + clamp(sp * 0.2, 0.0, 2.2));
      q = dir * position.x * 2.0 * lenS / aParams.x + perp * position.y * 1.0;
    }
  }
  mv.xy += q * aParams.x;
  gl_Position = projectionMatrix * mv;
}
`;

const frag = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uSunTint;
uniform vec3 uSky;
varying vec2 vUv;
varying vec4 vP;
varying vec3 vWorld;
varying float vNear;

float h21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}
float vn(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(h21(i), h21(i + vec2(1.0, 0.0)), f.x), mix(h21(i + vec2(0.0, 1.0)), h21(i + vec2(1.0, 1.0)), f.x), f.y);
}
void main() {
  float r = length(vUv);
  if (r > 1.0) discard;
  float kind = vP.z;
  float alpha;
  if (kind < 0.5) {
    // spray puff: soft, slightly lumpy
    alpha = smoothstep(1.0, 0.0, r);
    alpha = alpha * alpha * (3.0 - 2.0 * alpha);
  } else if (kind < 1.5) {
    // wispy rather than a flat disc
    float wisp = 0.45 + 1.1 * vn(vUv * 1.6 + vP.w * 37.0);
    alpha = exp(-r * r * 3.6) * smoothstep(1.0, 0.7, r) * 0.8 * wisp;
  } else {
    alpha = smoothstep(1.0, 0.55, r);
  }
  alpha *= vP.y * vNear;
  vec3 V = normalize(vWorld - cameraPosition);
  float fwd = pow(clamp(dot(V, uSunDir), 0.0, 1.0), 4.0);
  vec3 base = mix(uSky, vec3(1.0, 0.99, 0.97), 0.85);
  vec3 col = base + uSunTint * fwd * 1.6;
  if (kind > 1.5) col += vec3(0.6) * fwd;
  gl_FragColor = vec4(col, alpha);
}
`;

export function createParticles(capacity = 3200) {
  const N = capacity;
  const pos = new Float32Array(N * 3);
  const vel = new Float32Array(N * 3);
  const age = new Float32Array(N).fill(1e9);
  const life = new Float32Array(N).fill(1);
  const size0 = new Float32Array(N);
  const grow = new Float32Array(N);
  const alpha0 = new Float32Array(N);
  const kind = new Float32Array(N);
  const seed = new Float32Array(N);
  const drag = new Float32Array(N);
  const grav = new Float32Array(N);

  const aPos = new THREE.InstancedBufferAttribute(new Float32Array(N * 3), 3);
  const aParams = new THREE.InstancedBufferAttribute(new Float32Array(N * 4), 4);
  const aVel = new THREE.InstancedBufferAttribute(new Float32Array(N * 3), 3);
  aVel.setUsage(THREE.DynamicDrawUsage);
  aPos.setUsage(THREE.DynamicDrawUsage);
  aParams.setUsage(THREE.DynamicDrawUsage);
  const base = new THREE.PlaneGeometry(1, 1);
  const geo = new THREE.InstancedBufferGeometry();
  geo.index = base.index;
  geo.setAttribute("position", base.attributes.position);
  geo.setAttribute("aPos", aPos);
  geo.setAttribute("aParams", aParams);
  geo.setAttribute("aVel", aVel);
  geo.instanceCount = N;

  const mat = new THREE.ShaderMaterial({
    vertexShader: vert,
    fragmentShader: frag,
    transparent: true,
    depthWrite: false,
    uniforms: {
      uSunDir: { value: SUN_DIR },
      uSunTint: { value: PALETTE.sunTint },
      uSky: { value: PALETTE.horizonCool },
    },
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = 10;

  let head = 0;
  let rand = 12345;
  const rnd = () => {
    rand = (rand * 1664525 + 1013904223) >>> 0;
    return rand / 4294967296;
  };

  function spawn(k, p, v, lifeS, size, growth, a, dragK = 0.4, g = 9.8) {
    const i = head;
    head = (head + 1) % N;
    pos[i * 3] = p.x;
    pos[i * 3 + 1] = p.y;
    pos[i * 3 + 2] = p.z;
    vel[i * 3] = v.x;
    vel[i * 3 + 1] = v.y;
    vel[i * 3 + 2] = v.z;
    age[i] = 0;
    life[i] = lifeS;
    size0[i] = size;
    grow[i] = growth;
    alpha0[i] = a;
    kind[i] = k;
    seed[i] = rnd();
    drag[i] = dragK;
    grav[i] = g;
  }

  function update(dt, wind) {
    const pa = aPos.array;
    const pp = aParams.array;
    const pv = aVel.array;
    for (let i = 0; i < N; i++) {
      let a = age[i];
      if (a >= life[i]) {
        pp[i * 4 + 1] = 0;
        pp[i * 4] = 0;
        pa[i * 3 + 1] = -1000;
        continue;
      }
      a += dt;
      age[i] = a;
      const d = Math.exp(-drag[i] * dt);
      vel[i * 3] = vel[i * 3] * d + wind.x * dt * 0.5;
      vel[i * 3 + 1] = vel[i * 3 + 1] * d - grav[i] * dt;
      vel[i * 3 + 2] = vel[i * 3 + 2] * d + wind.z * dt * 0.5;
      pos[i * 3] += vel[i * 3] * dt;
      pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
      pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
      const u = a / life[i];
      pa[i * 3] = pos[i * 3];
      pa[i * 3 + 1] = pos[i * 3 + 1];
      pa[i * 3 + 2] = pos[i * 3 + 2];
      pv[i * 3] = vel[i * 3];
      pv[i * 3 + 1] = vel[i * 3 + 1];
      pv[i * 3 + 2] = vel[i * 3 + 2];
      const fade = Math.min(1, a * 12) * (1 - u) * (1 - u);
      pp[i * 4] = size0[i] * (1 + grow[i] * u);
      pp[i * 4 + 1] = alpha0[i] * fade;
      pp[i * 4 + 2] = kind[i];
      pp[i * 4 + 3] = seed[i];
    }
    aPos.needsUpdate = true;
    aParams.needsUpdate = true;
    aVel.needsUpdate = true;
  }

  // water-plane kill helper: particles falling below a plane die
  function killBelow(planePoint, planeNormal, margin = 0) {
    for (let i = 0; i < N; i++) {
      if (age[i] >= life[i]) continue;
      const dx = pos[i * 3] - planePoint.x;
      const dy = pos[i * 3 + 1] - planePoint.y;
      const dz = pos[i * 3 + 2] - planePoint.z;
      if (dx * planeNormal.x + dy * planeNormal.y + dz * planeNormal.z < margin && vel[i * 3 + 1] < 0 && kind[i] !== 1) {
        age[i] = life[i];
      }
    }
  }

  return { mesh, spawn, update, killBelow, rnd };
}
