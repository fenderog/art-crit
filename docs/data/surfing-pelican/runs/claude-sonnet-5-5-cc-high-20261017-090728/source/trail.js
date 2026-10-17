import * as THREE from "three";
import { noiseGLSL } from "./sky.js";
import { surface } from "./waves.js";

const MAX = 120;
const LIFE = 4.0;

const vertex = /* glsl */ `
attribute float aAge;
attribute vec2 aUV;
varying float vAge;
varying vec2 vUV;
varying vec3 vWorld;
void main() {
  vAge = aAge;
  vUV = aUV;
  vWorld = position;
  gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
}
`;

const fragment = /* glsl */ `
uniform float uTime;
varying float vAge;
varying vec2 vUV;
varying vec3 vWorld;
${noiseGLSL}
void main() {
  float across = abs(vUV.y);
  float n = fbm(vWorld.xz * 2.2 + vec2(0.0, uTime * 0.6));
  float edge = smoothstep(1.0, 0.35 + vAge * 0.2, across + (n - 0.5) * 0.7);
  float a = edge * pow(1.0 - vAge, 1.4);
  a *= smoothstep(0.25, 0.5, n + 0.45 - vAge * 0.45);
  a = clamp(a * 1.3, 0.0, 0.95);
  if (a < 0.01) discard;
  gl_FragColor = vec4(vec3(0.93, 0.97, 0.98), a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

// A foam wake that lives on the water: points are stored as water-particle
// rest positions and drift up the face toward the crest.
export function createTrail() {
  const pts = []; // {x, z, born}
  const pos = new Float32Array(MAX * 2 * 3);
  const age = new Float32Array(MAX * 2);
  const uv = new Float32Array(MAX * 2 * 2);
  const idx = [];
  for (let i = 0; i < MAX - 1; i++) {
    const a = i * 2;
    idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setAttribute("aAge", new THREE.BufferAttribute(age, 1));
  g.setAttribute("aUV", new THREE.BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.setDrawRange(0, 0);
  const uniforms = { uTime: { value: 0 } };
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: vertex,
    fragmentShader: fragment,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    polygonOffset: true,
    polygonOffsetFactor: -2,
    polygonOffsetUnits: -2,
  });
  const mesh = new THREE.Mesh(g, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = 2;

  const P = new THREE.Vector3();
  const Q = new THREE.Vector3();
  let lastSpawn = -1;

  function update(t, x0, z0, strength) {
    uniforms.uTime.value = t;
    if (t - lastSpawn > 0.05) {
      lastSpawn = t;
      pts.unshift({ x: x0, z: z0, born: t });
    }
    while (pts.length > MAX || (pts.length && t - pts[pts.length - 1].born > LIFE)) pts.pop();
    // drift with the water, up the face
    const n = pts.length;
    let count = 0;
    for (let i = 0; i < n; i++) {
      const p = pts[i];
      const a = (t - p.born) / LIFE;
      const dz = -(t - p.born) * 0.55;
      surface(p.x, p.z + dz, t, P);
      // direction along trail
      const j = Math.min(i + 1, n - 1);
      const k = Math.max(i - 1, 0);
      const pj = pts[j];
      const pk = pts[k];
      const dx = pk.x - pj.x;
      const ddz = pk.z - (t - pk.born) * 0.55 - (pj.z - (t - pj.born) * 0.55);
      let len = Math.hypot(dx, ddz) || 1;
      const nx = -ddz / len;
      const nz = dx / len;
      const w = (0.55 + a * 2.0) * (0.45 + 0.55 * strength) * (i === 0 ? 0.6 : 1);
      Q.set(P.x, P.y + 0.05, P.z);
      const o = i * 2;
      pos.set([Q.x + nx * w, Q.y, Q.z + nz * w, Q.x - nx * w, Q.y, Q.z - nz * w], o * 3);
      age[o] = age[o + 1] = a;
      uv.set([0, 1, 0, -1], o * 2);
      count++;
    }
    g.setDrawRange(0, Math.max(count - 1, 0) * 6);
    g.attributes.position.needsUpdate = true;
    g.attributes.aAge.needsUpdate = true;
    g.attributes.aUV.needsUpdate = true;
  }

  return { mesh, update };
}
