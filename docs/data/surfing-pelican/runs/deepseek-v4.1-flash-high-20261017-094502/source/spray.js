import * as THREE from 'three';

function makeSprayTexture() {
  const size = 64;
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(
    size / 2, size / 2, 0,
    size / 2, size / 2, size / 2,
  );
  g.addColorStop(0.0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.75)');
  g.addColorStop(1.0, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// CPU particle system for the bow spray thrown up by the board.
export class Spray {
  constructor(scene, max = 700) {
    this.max = max;
    this.pos = new Float32Array(max * 3);
    this.vel = new Float32Array(max * 3);
    this.life = new Float32Array(max);
    this.maxLife = new Float32Array(max);
    this.size = new Float32Array(max);
    this.alpha = new Float32Array(max);
    this.cursor = 0;
    this.emitAcc = 0;

    for (let i = 0; i < max; i++) this.pos[i * 3 + 1] = -9999;


    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    geo.setAttribute('aSize', new THREE.BufferAttribute(this.size, 1));
    geo.setAttribute('aAlpha', new THREE.BufferAttribute(this.alpha, 1));

    const mat = new THREE.ShaderMaterial({
      uniforms: { uTex: { value: makeSprayTexture() } },
      vertexShader: /* glsl */ `
        attribute float aSize;
        attribute float aAlpha;
        varying float vAlpha;
        void main() {
          vAlpha = aAlpha;
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = aSize * (170.0 / max(-mv.z, 0.1));
          gl_Position = projectionMatrix * mv;
        }
      `,
      fragmentShader: /* glsl */ `
        uniform sampler2D uTex;
        varying float vAlpha;
        void main() {
          vec4 t = texture2D(uTex, gl_PointCoord);
          gl_FragColor = vec4(0.92, 0.97, 1.0, t.a * vAlpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.NormalBlending,
    });

    this.points = new THREE.Points(geo, mat);
    this.points.frustumCulled = false;
    scene.add(this.points);
  }

  spawn(origin, back, up, right, dt) {
    this.emitAcc += dt * 260;
    while (this.emitAcc >= 1) {
      this.emitAcc -= 1;
      const i = this.cursor;
      this.cursor = (this.cursor + 1) % this.max;

      const spread = 0.7;
      this.pos[i * 3 + 0] = origin.x + (Math.random() - 0.5) * spread;
      this.pos[i * 3 + 1] = origin.y + Math.random() * 0.15;
      this.pos[i * 3 + 2] = origin.z + (Math.random() - 0.5) * spread;

      const bs = 2.0 + Math.random() * 3.0;
      const us = 1.6 + Math.random() * 3.0;
      const rs = (Math.random() - 0.5) * 2.6;
      this.vel[i * 3 + 0] = back.x * bs + up.x * us + right.x * rs;
      this.vel[i * 3 + 1] = back.y * bs + up.y * us + right.y * rs;
      this.vel[i * 3 + 2] = back.z * bs + up.z * us + right.z * rs;

      const life = 0.6 + Math.random() * 0.8;
      this.life[i] = life;
      this.maxLife[i] = life;
      this.size[i] = 0.12 + Math.random() * 0.3;
    }
  }

  update(dt) {
    const gravity = -5.2;
    for (let i = 0; i < this.max; i++) {
      if (this.life[i] <= 0) {
        this.alpha[i] = 0;
        continue;
      }
      this.life[i] -= dt;
      if (this.life[i] <= 0) {
        this.alpha[i] = 0;
        this.pos[i * 3 + 1] = -9999;
        continue;
      }
      this.vel[i * 3 + 1] += gravity * dt;
      this.pos[i * 3 + 0] += this.vel[i * 3 + 0] * dt;
      this.pos[i * 3 + 1] += this.vel[i * 3 + 1] * dt;
      this.pos[i * 3 + 2] += this.vel[i * 3 + 2] * dt;

      const t = this.life[i] / this.maxLife[i];
      this.alpha[i] = Math.min(1, t * 1.8) * (0.25 + 0.75 * t);
    }

    this.points.geometry.attributes.position.needsUpdate = true;
    this.points.geometry.attributes.aSize.needsUpdate = true;
    this.points.geometry.attributes.aAlpha.needsUpdate = true;
  }
}
