import * as THREE from "three";
import { SUN_DIR, palette } from "./sky.js";

// CPU-simulated spray: rail spray from the board, offshore wind blowing mist
// off the lip, and churning whitewater mist on the broken section.
export function createSpray(max = 5000) {
  const pos = new Float32Array(max * 3);
  const vel = new Float32Array(max * 3);
  const life = new Float32Array(max);
  const maxLife = new Float32Array(max).fill(1);
  const size = new Float32Array(max);
  const alpha = new Float32Array(max);
  const drag = new Float32Array(max);
  const grav = new Float32Array(max);
  const airX = new Float32Array(max);
  const airZ = new Float32Array(max);
  const baseAlpha = new Float32Array(max);
  let cursor = 0;

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute("aSize", new THREE.BufferAttribute(size, 1).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute("aAlpha", new THREE.BufferAttribute(alpha, 1).setUsage(THREE.DynamicDrawUsage));

  const material = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: {
      uScale: { value: 500 },
      uSunDir: { value: SUN_DIR },
      uSunColor: { value: palette.sun },
    },
    vertexShader: /* glsl */ `
      attribute float aSize;
      attribute float aAlpha;
      uniform float uScale;
      uniform vec3 uSunDir;
      varying float vAlpha;
      varying float vBack;
      void main() {
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = clamp(aSize * uScale / -mv.z, 0.0, 160.0);
        vec3 world = (modelMatrix * vec4(position, 1.0)).xyz;
        vec3 V = normalize(world - cameraPosition);
        vBack = pow(max(dot(V, uSunDir), 0.0), 4.0);
        // fade out anything that drifts right up to the lens
        vAlpha = aAlpha * smoothstep(0.6, 2.5, -mv.z);
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunColor;
      varying float vAlpha;
      varying float vBack;
      void main() {
        vec2 c = gl_PointCoord - 0.5;
        float r = length(c);
        float a = smoothstep(0.5, 0.0, r);
        a *= a;
        if (a * vAlpha < 0.003) discard;
        vec3 col = vec3(0.86, 0.92, 0.95) + uSunColor * vBack * 1.8;
        gl_FragColor = vec4(col, a * vAlpha);
      }`,
  });

  const points = new THREE.Points(geo, material);
  points.frustumCulled = false;

  function spawn(x, y, z, vx, vy, vz, o) {
    const i = cursor;
    cursor = (cursor + 1) % max;
    pos[i * 3] = x;
    pos[i * 3 + 1] = y;
    pos[i * 3 + 2] = z;
    vel[i * 3] = vx;
    vel[i * 3 + 1] = vy;
    vel[i * 3 + 2] = vz;
    life[i] = 0;
    maxLife[i] = o.life;
    size[i] = o.size;
    baseAlpha[i] = o.alpha;
    drag[i] = o.drag;
    grav[i] = o.gravity;
    airX[i] = o.airX;
    airZ[i] = o.airZ;
  }

  function update(dt) {
    for (let i = 0; i < max; i++) {
      if (life[i] >= maxLife[i]) {
        alpha[i] = 0;
        continue;
      }
      life[i] += dt;
      const k = life[i] / maxLife[i];
      const d = Math.min(1, drag[i] * dt);
      const j = i * 3;
      vel[j] += (airX[i] - vel[j]) * d;
      vel[j + 1] += -grav[i] * dt - vel[j + 1] * d * 0.3;
      vel[j + 2] += (airZ[i] - vel[j + 2]) * d;
      pos[j] += vel[j] * dt;
      pos[j + 1] += vel[j + 1] * dt;
      pos[j + 2] += vel[j + 2] * dt;
      // fade in quickly, out slowly; mist grows as it disperses
      alpha[i] = baseAlpha[i] * Math.min(1, k * 8) * (1 - k) * (1 - k * 0.3);
      size[i] *= 1 + dt * 0.6;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.aSize.needsUpdate = true;
    geo.attributes.aAlpha.needsUpdate = true;
  }

  return { points, spawn, update, material };
}
