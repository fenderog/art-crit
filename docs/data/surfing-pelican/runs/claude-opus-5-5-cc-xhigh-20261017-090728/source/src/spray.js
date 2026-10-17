// Spray, lip mist, falling curtain drops and whitewater bursts.

import * as THREE from 'three';
import { surfaceSample, makeSample, SURF_SPEED, WAVE_SPEED } from './wave.js';
import { mulberry32 } from './geom.js';

const rnd = mulberry32(99);
const r = (a, b) => a + (b - a) * rnd();
const GRAVITY = -13;
const OFFSHORE = 2.5; // wind blowing from the shore out to sea (-z)

const vertexShader = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
uniform float uScale;
varying float vAlpha;
varying vec3 vWorld;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * mv;
  gl_PointSize = min(aSize * uScale / max(-mv.z, 0.1), 900.0);
  vAlpha = aAlpha;
  vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
}
`;

const fragmentShader = /* glsl */ `
uniform vec3 uColor;
uniform vec3 uSunColor;
uniform vec3 uSunDir;
uniform float uSoft;
uniform float uGlow;
varying float vAlpha;
varying vec3 vWorld;
void main() {
  vec2 c = gl_PointCoord * 2.0 - 1.0;
  float r2 = dot(c, c);
  if (r2 > 1.0 || vAlpha < 0.002) discard;
  float a = uSoft > 0.5 ? exp(-r2 * 3.0) * (1.0 - r2) : smoothstep(1.0, 0.45, r2);
  vec3 V = normalize(cameraPosition - vWorld);
  float back = pow(max(dot(-V, uSunDir), 0.0), 5.0);
  vec3 col = uColor + uSunColor * (0.25 + back * uGlow);
  gl_FragColor = vec4(col, a * vAlpha);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

class Particles {
  constructor(max, shared, { soft, color, glow }) {
    this.max = max;
    this.pos = new Float32Array(max * 3);
    this.vel = new Float32Array(max * 3);
    this.age = new Float32Array(max).fill(1e9);
    this.life = new Float32Array(max).fill(1);
    this.s0 = new Float32Array(max);
    this.s1 = new Float32Array(max);
    this.a0 = new Float32Array(max);
    this.drag = new Float32Array(max);
    this.grav = new Float32Array(max);
    this.size = new Float32Array(max);
    this.alpha = new Float32Array(max);
    this.cursor = 0;
    const geo = new THREE.BufferGeometry();
    this.posAttr = new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage);
    this.sizeAttr = new THREE.BufferAttribute(this.size, 1).setUsage(THREE.DynamicDrawUsage);
    this.alphaAttr = new THREE.BufferAttribute(this.alpha, 1).setUsage(THREE.DynamicDrawUsage);
    geo.setAttribute('position', this.posAttr);
    geo.setAttribute('aSize', this.sizeAttr);
    geo.setAttribute('aAlpha', this.alphaAttr);
    this.uniforms = {
      uScale: { value: 500 },
      uColor: { value: new THREE.Color(color) },
      uSunColor: shared.uSunColor,
      uSunDir: shared.uSunDir,
      uSoft: { value: soft ? 1 : 0 },
      uGlow: { value: glow },
    };
    const mat = new THREE.ShaderMaterial({
      uniforms: this.uniforms,
      vertexShader,
      fragmentShader,
      transparent: true,
      depthWrite: false,
    });
    this.points = new THREE.Points(geo, mat);
    this.points.frustumCulled = false;
    this.points.renderOrder = soft ? 3 : 2;
  }

  emit(p, v, life, s0, s1, a, drag, grav = 1) {
    const i = this.cursor;
    this.cursor = (this.cursor + 1) % this.max;
    this.pos[i * 3] = p.x; this.pos[i * 3 + 1] = p.y; this.pos[i * 3 + 2] = p.z;
    this.vel[i * 3] = v.x; this.vel[i * 3 + 1] = v.y; this.vel[i * 3 + 2] = v.z;
    this.age[i] = 0;
    this.life[i] = life;
    this.s0[i] = s0;
    this.s1[i] = s1;
    this.a0[i] = a;
    this.drag[i] = drag;
    this.grav[i] = grav;
  }

  update(dt) {
    // air is still in the earth frame, so in the surfer's frame it streams by
    const ax = -SURF_SPEED, az = -WAVE_SPEED - OFFSHORE;
    for (let i = 0; i < this.max; i++) {
      const age = (this.age[i] += dt);
      const k = age / this.life[i];
      if (k >= 1) { this.alpha[i] = 0; continue; }
      const d = Math.min(1, this.drag[i] * dt);
      const j = i * 3;
      this.vel[j] += (ax - this.vel[j]) * d;
      this.vel[j + 1] += GRAVITY * this.grav[i] * dt - this.vel[j + 1] * d * 0.3;
      this.vel[j + 2] += (az - this.vel[j + 2]) * d;
      this.pos[j] += this.vel[j] * dt;
      this.pos[j + 1] += this.vel[j + 1] * dt;
      this.pos[j + 2] += this.vel[j + 2] * dt;
      if (this.pos[j + 1] < -0.2) { this.age[i] = 1e9; this.alpha[i] = 0; continue; }
      this.size[i] = this.s0[i] + (this.s1[i] - this.s0[i]) * Math.sqrt(k);
      this.alpha[i] = this.a0[i] * Math.min(1, k * 12) * Math.pow(1 - k, 1.3);
    }
    this.posAttr.needsUpdate = true;
    this.sizeAttr.needsUpdate = true;
    this.alphaAttr.needsUpdate = true;
  }
}

export class Spray {
  constructor(shared) {
    this.drops = new Particles(3500, shared, { soft: false, color: '#c9c4c8', glow: 2.2 });
    this.mist = new Particles(1400, shared, { soft: true, color: '#b7b0b8', glow: 1.6 });
    this.group = new THREE.Group();
    this.group.add(this.drops.points, this.mist.points);
    this.s = makeSample();
    this.p = new THREE.Vector3();
    this.v = new THREE.Vector3();
    this.acc = { board: 0, lip: 0, curtain: 0, burst: 0, burstMist: 0 };
  }

  setScale(px) {
    this.drops.uniforms.uScale.value = px;
    this.mist.uniforms.uScale.value = px;
  }

  count(key, rate, dt) {
    this.acc[key] += rate * dt;
    const n = Math.floor(this.acc[key]);
    this.acc[key] -= n;
    return n;
  }

  update(t, dt, surfer) {
    const { s, p, v } = this;

    // board spray: fans off the tail rail, big on hard turns
    const carve = Math.abs(surfer.carve);
    const nb = this.count('board', 140 + carve * 1500, dt);
    for (let i = 0; i < nb; i++) {
      const side = rnd() < 0.5 ? -1 : 1;
      p.copy(surfer.tail).addScaledVector(surfer.fwd, r(-0.1, 0.35));
      p.addScaledVector(surfer.upFace, side * 0.18).addScaledVector(surfer.normal, 0.03);
      const k = r(0.6, 1.0) * (0.6 + carve * 1.6);
      v.copy(surfer.fwd).multiplyScalar(-r(1.0, 3.0));
      v.addScaledVector(surfer.normal, r(1.5, 3.2) * k).addScaledVector(surfer.upFace, r(0.5, 2.5) * k);
      v.y += r(0.5, 2.0) * k;
      this.drops.emit(p, v, r(0.5, 1.0), r(0.015, 0.035), r(0.03, 0.05), 0.8, 1.4);
      if (rnd() < 0.15) this.mist.emit(p, v.multiplyScalar(0.5), r(0.8, 1.4), 0.25, r(0.7, 1.2), 0.1, 1.5, 0.15);
    }

    // mist torn off the crest by the offshore wind
    const nl = this.count('lip', 150, dt);
    for (let i = 0; i < nl; i++) {
      const x = r(-7, 26);
      surfaceSample(x, r(4.4, 5.6), s);
      p.copy(s.pos).addScaledVector(s.normal, 0.08);
      v.set(r(-1, 1) - SURF_SPEED * 0.3, r(0.8, 2.2), r(-1.5, -0.2));
      const big = x < 12 ? 1 : 0.6;
      this.mist.emit(p, v, r(1.4, 2.6), r(0.3, 0.6) * big, r(1.2, 2.4) * big, 0.13, 0.7, 0.05);
      if (rnd() < 0.5) this.drops.emit(p, v.multiplyScalar(1.2), r(0.6, 1.1), 0.02, 0.035, 0.45, 0.8, 0.6);
    }

    // drops falling from the lip into the tube
    const nc = this.count('curtain', 220, dt);
    for (let i = 0; i < nc; i++) {
      const x = r(-6, 2.5);
      surfaceSample(x, r(6.6, 7.4), s);
      if (s.stage < 1.4) continue;
      p.copy(s.pos).addScaledVector(s.normal, 0.03);
      v.set(-SURF_SPEED * r(0.85, 1.0), r(-1.2, 0.2), r(0.2, 1.2));
      this.drops.emit(p, v, r(0.35, 0.7), r(0.015, 0.035), 0.04, 0.6, 0.1);
    }

    // whitewater explosion where the lip lands
    const nw = this.count('burst', 380, dt);
    for (let i = 0; i < nw; i++) {
      const x = r(-17, -5);
      surfaceSample(x, r(5.5, 9.5), s);
      p.copy(s.pos).addScaledVector(s.normal, 0.1);
      const f = Math.max(0, 1 - Math.abs(x + 9) / 9);
      v.set(-SURF_SPEED * r(0.8, 1.0), r(1.5, 6.5) * (0.4 + f), r(0.5, 3.0) * f);
      this.drops.emit(p, v, r(0.7, 1.6), r(0.04, 0.09), r(0.09, 0.2), 0.75, 0.5);
    }
    const nm = this.count('burstMist', 90, dt);
    for (let i = 0; i < nm; i++) {
      const x = r(-22, -4);
      surfaceSample(x, r(5, 10), s);
      p.copy(s.pos).addScaledVector(s.normal, 0.2);
      v.set(-SURF_SPEED * r(0.85, 1.0), r(0.8, 3.0), r(0.0, 1.5));
      this.mist.emit(p, v, r(1.5, 3.0), r(0.8, 1.4), r(2.5, 4.5), 0.16, 0.6, 0.05);
    }

    this.drops.update(dt);
    this.mist.update(dt);
  }
}
