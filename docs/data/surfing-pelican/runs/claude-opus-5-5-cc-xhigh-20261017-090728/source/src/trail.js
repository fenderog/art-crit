// Foamy carve line left on the face behind the board. Trail points live in
// wave coordinates (x along the line, u across the profile) and are carried
// backwards by the water rushing past.

import * as THREE from 'three';
import { surfaceSample, makeSample, chopAt, SURF_SPEED } from './wave.js';
import { NOISE_GLSL } from './shaders.js';

const MAX = 120;
const LIFE = 1.15;

export class Trail {
  constructor(shared) {
    this.pts = [];
    const n = MAX * 2;
    this.pos = new Float32Array(n * 3);
    this.data = new Float32Array(n * 3); // age, side, flow coord
    const geo = new THREE.BufferGeometry();
    this.posAttr = new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage);
    this.dataAttr = new THREE.BufferAttribute(this.data, 3).setUsage(THREE.DynamicDrawUsage);
    geo.setAttribute('position', this.posAttr);
    geo.setAttribute('aData', this.dataAttr);
    const idx = [];
    for (let i = 0; i < MAX - 1; i++) {
      const a = i * 2;
      idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }
    geo.setIndex(idx);
    geo.setDrawRange(0, 0);
    this.geo = geo;
    const mat = new THREE.ShaderMaterial({
      uniforms: { uTime: shared.uTime, uSunDir: shared.uSunDir, uSunColor: shared.uSunColor, uLife: { value: LIFE }, uFlow: { value: SURF_SPEED } },
      vertexShader: /* glsl */ `
        attribute vec3 aData;
        varying vec3 vData;
        varying vec3 vWorld;
        void main() {
          vData = aData;
          vec4 wp = modelMatrix * vec4(position, 1.0);
          vWorld = wp.xyz;
          gl_Position = projectionMatrix * viewMatrix * wp;
        }
      `,
      fragmentShader: /* glsl */ `
        uniform float uTime;
        uniform float uLife;
        uniform float uFlow;
        uniform vec3 uSunColor;
        varying vec3 vData;
        varying vec3 vWorld;
        ${NOISE_GLSL}
        void main() {
          float age = vData.x / uLife;
          float edge = 1.0 - abs(vData.y);
          vec2 q = vec2(vWorld.x + uFlow * uTime, vData.y * 1.5 + vData.z);
          float n = fbm(q * vec2(2.6, 2.0));
          float lace = 1.0 - abs(2.0 * fbm(q * vec2(4.0, 3.0) + 7.0) - 1.0);
          float body = smoothstep(0.0, 0.45, edge * (0.45 + n) - age * 0.4);
          float froth = smoothstep(0.35 + 0.35 * age, 0.75 + 0.15 * age, lace * 0.7 + n * 0.5);
          float a = body * froth * pow(1.0 - age, 1.6);
          a *= smoothstep(0.0, 0.12, vData.x);
          vec3 col = vec3(0.92, 0.9, 0.9) * (0.7 + 0.3 * uSunColor);
          gl_FragColor = vec4(col, a * 0.45);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }
      `,
      transparent: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2,
      polygonOffsetUnits: -4,
    });
    this.mesh = new THREE.Mesh(geo, mat);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 1;
    this.s = makeSample();
    this.side = new THREE.Vector3();
    this.dir = new THREE.Vector3();
  }

  update(t, dt, surfer) {
    for (const p of this.pts) {
      p.x -= SURF_SPEED * dt;
      p.u -= 0.22 * dt;   // water climbs the face
      p.age += dt;
    }
    while (this.pts.length && this.pts[0].age > LIFE) this.pts.shift();
    // newest point follows the tail; a new one is dropped every 25 ms
    const last = this.pts[this.pts.length - 1];
    if (!last || last.age >= 0.025) this.pts.push({ x: surfer.tail.x, u: surfer.u + 0.05, age: 0 });
    else { last.x = surfer.tail.x; last.u = surfer.u + 0.05; }
    while (this.pts.length > MAX) this.pts.shift();

    const n = this.pts.length;
    const { s, side, dir } = this;
    const samples = [];
    for (let i = 0; i < n; i++) {
      const p = this.pts[i];
      surfaceSample(p.x, p.u, s);
      const h = chopAt(s.pos.x, s.pos.y, s.pos.z, t);
      samples.push({ pos: s.pos.clone().addScaledVector(s.normal, h + 0.03), normal: s.normal.clone() });
    }
    for (let i = 0; i < n; i++) {
      const a = samples[Math.max(0, i - 1)].pos;
      const b = samples[Math.min(n - 1, i + 1)].pos;
      dir.subVectors(b, a).normalize();
      side.crossVectors(samples[i].normal, dir).normalize();
      const p = this.pts[i];
      const w = 0.06 + Math.pow(p.age, 0.7) * 0.2;
      for (let k = 0; k < 2; k++) {
        const sg = k === 0 ? -1 : 1;
        const j = (i * 2 + k) * 3;
        this.pos[j] = samples[i].pos.x + side.x * w * sg;
        this.pos[j + 1] = samples[i].pos.y + side.y * w * sg;
        this.pos[j + 2] = samples[i].pos.z + side.z * w * sg;
        this.data[j] = p.age;
        this.data[j + 1] = sg;
        this.data[j + 2] = p.u * 2.0;
      }
    }
    this.posAttr.needsUpdate = true;
    this.dataAttr.needsUpdate = true;
    this.geo.setDrawRange(0, Math.max(0, n - 1) * 6);
  }
}
