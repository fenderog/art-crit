import * as THREE from 'three';
import { makeDropTexture } from './textures.js';

const VERT = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
attribute vec3 aColor;
uniform float uPixelScale;
varying float vAlpha;
varying vec3 vColor;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = aSize * uPixelScale / max(0.35, -mv.z);
  gl_Position = projectionMatrix * mv;
  vAlpha = aAlpha;
  vColor = aColor;
}
`;

const FRAG = /* glsl */ `
uniform sampler2D uMap;
varying float vAlpha;
varying vec3 vColor;
void main() {
  float m = texture2D(uMap, gl_PointCoord).a;
  float a = m * vAlpha;
  if (a < 0.004) discard;
  gl_FragColor = vec4(vColor, a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

/** Foam / spray droplets kicked up by the board. */
export class Spray {
  constructor(count = 520) {
    this.count = count;
    this.cursor = 0;
    this.emitAccum = 0;

    this.pos = new Float32Array(count * 3);
    this.vel = new Float32Array(count * 3);
    this.age = new Float32Array(count);
    this.life = new Float32Array(count);
    this.size = new Float32Array(count);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    geometry.setAttribute('aColor', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
    geometry.setAttribute('aSize', new THREE.BufferAttribute(this.size, 1));
    geometry.setAttribute('aAlpha', new THREE.BufferAttribute(new Float32Array(count), 1));

    this.uniforms = {
      uMap: { value: makeDropTexture() },
      uPixelScale: { value: 700 },
    };

    const material = new THREE.ShaderMaterial({
      uniforms: this.uniforms,
      vertexShader: VERT,
      fragmentShader: FRAG,
      transparent: true,
      depthWrite: false,
      blending: THREE.NormalBlending,
    });

    this.points = new THREE.Points(geometry, material);
    this.points.frustumCulled = false;
    this.geometry = geometry;

    const col = geometry.attributes.aColor.array;
    const base = new THREE.Color(0xf2f9fb);
    for (let i = 0; i < count; i++) {
      const c = base.clone().offsetHSL(0, 0, (Math.random() - 0.5) * 0.12);
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
      this.age[i] = Infinity;
      this.life[i] = 1;
    }
    this.geometry.attributes.aColor.needsUpdate = true;

    this._tmp = new THREE.Vector3();
  }

  setPixelScale(v) {
    this.uniforms.uPixelScale.value = v;
  }

  /** Spawn one droplet at p with velocity v (world space). */
  spawn(px, py, pz, vx, vy, vz, size, life) {
    const i = this.cursor;
    this.cursor = (this.cursor + 1) % this.count;
    this.pos[i * 3] = px;
    this.pos[i * 3 + 1] = py;
    this.pos[i * 3 + 2] = pz;
    this.vel[i * 3] = vx;
    this.vel[i * 3 + 1] = vy;
    this.vel[i * 3 + 2] = vz;
    this.size[i] = size;
    this.life[i] = life;
    this.age[i] = 0;
  }

  /** Emit a steady wake of spray from the board's tail and bow. */
  emitWake(point, forward, dt, intensity = 1) {
    this.emitAccum += dt * 165 * intensity;
    const n = Math.floor(this.emitAccum);
    this.emitAccum -= n;
    const fx = forward.x;
    const fz = forward.z;

    for (let k = 0; k < n; k++) {
      const tail = Math.random() > 0.35;
      const spread = tail ? 0.32 : 0.2;
      const bx = point.x + (Math.random() - 0.5) * (tail ? 1.1 : 0.7);
      const bz = point.z + (Math.random() - 0.5) * (tail ? 0.5 : 0.6);
      const by = point.y + Math.random() * 0.12;

      // droplets fly back off the tail, or up off the bow
      const back = tail ? -1 : 1;
      const speed = tail ? 1.1 + Math.random() * 1.7 : 0.7 + Math.random() * 1.1;
      const up = tail ? 0.7 + Math.random() * 1.5 : 1.3 + Math.random() * 2.1;
      this.spawn(
        bx,
        by,
        bz,
        fx * speed * back + (Math.random() - 0.5) * spread * 3,
        up,
        fz * speed * back + (Math.random() - 0.5) * spread * 3,
        0.075 + Math.random() * 0.17,
        0.5 + Math.random() * 1.05,
      );
    }
  }

  update(dt) {
    const { pos, vel, age, life, size } = this;
    const alpha = this.geometry.attributes.aAlpha.array;
    const sizes = this.geometry.attributes.aSize.array;

    for (let i = 0; i < this.count; i++) {
      if (!Number.isFinite(age[i])) {
        alpha[i] = 0;
        continue;
      }
      age[i] += dt;
      if (age[i] >= life[i]) {
        age[i] = Infinity;
        alpha[i] = 0;
        continue;
      }
      const i3 = i * 3;
      vel[i3] *= 1 - 1.25 * dt;
      vel[i3 + 1] = vel[i3 + 1] * (1 - 0.9 * dt) - 6.4 * dt;
      vel[i3 + 2] *= 1 - 1.25 * dt;
      pos[i3] += vel[i3] * dt;
      pos[i3 + 1] += vel[i3 + 1] * dt;
      pos[i3 + 2] += vel[i3 + 2] * dt;

      const u = age[i] / life[i];
      const fadeIn = Math.min(1, u * 9);
      const fadeOut = 1 - u * u;
      alpha[i] = 0.8 * fadeIn * fadeOut;
      sizes[i] = size[i] * (1 + u * 1.7);
    }

    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.attributes.aAlpha.needsUpdate = true;
    this.geometry.attributes.aSize.needsUpdate = true;
  }
}