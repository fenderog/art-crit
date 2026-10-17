import * as THREE from 'three';
import { PALETTE } from './theme.js';
import { waveHeight } from './waves.js';
import { makeCloudTexture } from './textures.js';

// ── spray: a pooled point cloud for droplets off the nose/rails and splashes ──
export function createSpray() {
  const CAP = 800;
  const pos = new Float32Array(CAP * 3);
  const vel = new Float32Array(CAP * 3);
  const size = new Float32Array(CAP);
  const alpha = new Float32Array(CAP);
  const age = new Float32Array(CAP);
  const life = new Float32Array(CAP);
  let alive = 0;

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute('aSize', new THREE.BufferAttribute(size, 1).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute('aAlpha', new THREE.BufferAttribute(alpha, 1).setUsage(THREE.DynamicDrawUsage));
  geo.setDrawRange(0, 0);

  const mat = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: {
      uColor: { value: new THREE.Color(PALETTE.foam) },
      uScale: { value: 900 },
    },
    vertexShader: /* glsl */ `
      attribute float aSize;
      attribute float aAlpha;
      uniform float uScale;
      varying float vA;
      void main() {
        vA = aAlpha;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aSize * uScale / max(0.3, -mv.z);
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor;
      varying float vA;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        float a = (1.0 - smoothstep(0.18, 0.5, d)) * vA;
        if (a < 0.01) discard;
        gl_FragColor = vec4(uColor, a);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });

  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;

  function copySlot(i, j) {
    for (let k = 0; k < 3; k++) {
      pos[i * 3 + k] = pos[j * 3 + k];
      vel[i * 3 + k] = vel[j * 3 + k];
    }
    size[i] = size[j];
    alpha[i] = alpha[j];
    age[i] = age[j];
    life[i] = life[j];
  }

  const _p = new THREE.Vector3();
  const _v = new THREE.Vector3();

  function spawn(p, v, s, l) {
    if (alive >= CAP) return;
    const i = alive++;
    pos[i * 3] = p.x;
    pos[i * 3 + 1] = p.y;
    pos[i * 3 + 2] = p.z;
    vel[i * 3] = v.x;
    vel[i * 3 + 1] = v.y;
    vel[i * 3 + 2] = v.z;
    size[i] = s;
    age[i] = 0;
    life[i] = l;
    alpha[i] = 0;
  }

  function burst(p, n, opts = {}) {
    const spread = opts.spread ?? 1.5;
    const up = opts.up ?? 2.6;
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = Math.random();
      _p.set(p.x + Math.cos(a) * r * spread, p.y, p.z + Math.sin(a) * r * spread);
      _v.set(Math.cos(a) * (0.4 + Math.random()), up * (0.4 + Math.random() * 0.8), Math.sin(a) * (0.4 + Math.random()));
      spawn(_p, _v, (opts.size ?? 0.15) * (0.6 + Math.random() * 0.9), (opts.life ?? 0.8) * (0.6 + Math.random() * 0.8));
    }
  }

  function update(dt, t) {
    let n = alive;
    for (let i = 0; i < n; ) {
      age[i] += dt;
      if (age[i] >= life[i]) {
        n--;
        if (i !== n) copySlot(i, n);
        continue;
      }
      vel[i * 3 + 1] -= 7.5 * dt; // gravity
      pos[i * 3] += vel[i * 3] * dt;
      pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
      pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
      if (pos[i * 3 + 1] < waveHeight(pos[i * 3], pos[i * 3 + 2], t) - 0.06) {
        n--; // droplet lands back in the sea
        if (i !== n) copySlot(i, n);
        continue;
      }
      alpha[i] = 0.85 * Math.sin(Math.min(age[i] / life[i], 1) * Math.PI);
      i++;
    }
    alive = n;
    geo.setDrawRange(0, n);
    geo.attributes.position.needsUpdate = true;
    geo.attributes.aSize.needsUpdate = true;
    geo.attributes.aAlpha.needsUpdate = true;
  }

  // pixel-perfect point sizing: worldSize * (h / (2*tan(fov/2))) / distance
  function setScale(height, fovDeg) {
    mat.uniforms.uScale.value = height / (2 * Math.tan((fovDeg * Math.PI) / 360));
  }

  return { points, spawn, burst, update, setScale };
}

// ── seagulls: three silhouettes circling on the rig ──
export function createGulls() {
  const group = new THREE.Group();
  const matBody = new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.gullBody), roughness: 0.85 });
  const matWing = new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.gullWing), roughness: 0.85 });
  const gulls = [];
  for (const [R, h, w, ph] of [[16, 4.5, 0.21, 0.0], [22, 6.8, 0.17, 2.1], [27, 9.0, 0.135, 4.2]]) {
    const g = new THREE.Group();
    g.rotation.order = 'YXZ';
    const bodyM = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.16, 4, 8), matBody);
    bodyM.rotation.x = Math.PI / 2;
    g.add(bodyM);
    const wings = [];
    for (const s of [1, -1]) {
      const p = new THREE.Group();
      p.position.set(s * 0.03, 0.01, 0);
      const wg = new THREE.BoxGeometry(0.3, 0.012, 0.09);
      wg.translate(s * 0.15, 0, 0);
      p.add(new THREE.Mesh(wg, matWing));
      g.add(p);
      wings.push(p);
    }
    const tailM = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.01, 0.1), matWing);
    tailM.position.set(0, 0, -0.12);
    g.add(tailM);
    group.add(g);
    gulls.push({ g, wings, R, h, w, ph });
  }

  function update(t) {
    for (const u of gulls) {
      const a = u.w * t + u.ph;
      const bob = Math.sin(0.5 * t + u.ph) * 0.7;
      const vy = 0.35 * Math.cos(0.5 * t + u.ph);
      u.g.position.set(Math.cos(a) * u.R, u.h + bob, Math.sin(a) * u.R);
      u.g.rotation.y = Math.atan2(-Math.sin(a), Math.cos(a)); // fly along the tangent
      u.g.rotation.x = THREE.MathUtils.clamp(-vy * 0.8, -0.35, 0.35);
      u.g.rotation.z = -0.4; // banked into the circle
      const f = Math.sin(9 * t + u.ph * 3) * 0.55 - 0.1;
      u.wings[0].rotation.z = f;
      u.wings[1].rotation.z = -f;
    }
  }

  return { group, update };
}

// ── clouds: soft canvas sprites drifting on the rig ──
export function createClouds() {
  const group = new THREE.Group();
  const tex = makeCloudTexture();
  const clouds = [];
  for (let i = 0; i < 9; i++) {
    const m = new THREE.SpriteMaterial({
      map: tex,
      color: 0xffe9d8,
      transparent: true,
      opacity: 0.35 + Math.random() * 0.35,
      depthWrite: false,
    });
    const sp = new THREE.Sprite(m);
    const ang = (i / 9) * Math.PI * 2 + Math.random() * 0.6;
    const rad = 80 + Math.random() * 80;
    sp.position.set(Math.cos(ang) * rad, 16 + Math.random() * 26, Math.sin(ang) * rad);
    const w = 26 + Math.random() * 34;
    sp.scale.set(w, w * 0.42, 1);
    group.add(sp);
    clouds.push({ sp, vx: 0.2 + Math.random() * 0.35 });
  }
  function update(dt) {
    for (const c of clouds) {
      c.sp.position.x += c.vx * dt;
      if (c.sp.position.x > 170) c.sp.position.x = -170;
    }
  }
  return { group, update };
}

// ── fish: one brave fish leaps out of the sea now and then ──
export function createFishFX() {
  const group = new THREE.Group();
  const matFish = new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.fish), roughness: 0.45 });
  const matFin = new THREE.MeshStandardMaterial({ color: new THREE.Color('#e0743a'), roughness: 0.6 });
  const fish = new THREE.Group();
  fish.visible = false;
  const bodyM = new THREE.Mesh(new THREE.SphereGeometry(0.13, 14, 10), matFish);
  bodyM.scale.set(2.1, 0.85, 0.55);
  fish.add(bodyM);
  const tailF = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.16, 0.11), matFin);
  tailF.position.set(-0.3, 0, 0);
  fish.add(tailF);
  const dorsal = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.07, 0.02), matFin);
  dorsal.position.set(-0.02, 0.1, 0);
  fish.add(dorsal);
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0x101014 });
  for (const s of [1, -1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.018, 8, 6), eyeMat);
    eye.position.set(0.17, 0.03, s * 0.06);
    fish.add(eye);
  }
  group.add(fish);

  let jump = null;
  let nextJump = 4.0;
  const activePos = new THREE.Vector3();
  const _p = new THREE.Vector3();

  function update(dt, t, pelican, spray) {
    if (!jump && t >= nextJump) {
      const x = pelican.x + 5 + Math.random() * 7;
      const z = pelican.z + (Math.random() - 0.5) * 10;
      jump = { t0: t, x, z, vx: -0.5 - Math.random() * 0.8, vz: (pelican.z - z) * 0.2, vy: 5.2, dur: 1.25 };
      spray.burst(_p.set(x, waveHeight(x, z, t) + 0.05, z), 16, { up: 2.4, spread: 0.9, size: 0.13, life: 0.7 });
    }
    if (jump) {
      const tau = t - jump.t0;
      const x = jump.x + jump.vx * tau;
      const z = jump.z + jump.vz * tau;
      const y = waveHeight(x, z, t) + jump.vy * tau - 4.9 * tau * tau;
      fish.visible = true;
      fish.position.set(x, y, z);
      fish.rotation.z = 0.5 - 7 * tau; // dazed somersault
      fish.rotation.y = 0.4 * Math.sin(3 * tau);
      activePos.set(x, y, z);
      if (tau >= jump.dur || y < waveHeight(x, z, t) - 0.3) {
        spray.burst(_p.set(x, waveHeight(x, z, t) + 0.05, z), 14, { up: 1.8, spread: 0.7, size: 0.11, life: 0.55 });
        jump = null;
        nextJump = t + 6 + Math.random() * 7;
        fish.visible = false;
      }
    }
  }

  return { group, update, active: () => (jump ? activePos : null) };
}
