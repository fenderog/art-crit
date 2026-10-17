import * as THREE from 'three';
import { waveHeight } from './ocean.js';

// Gradient sky dome with a sun disc + glow, all procedural.
export function createSkyDome(sunDir) {
  const geo = new THREE.SphereGeometry(220, 32, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: { sunDir: { value: sunDir.clone().normalize() } },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vDir;
      uniform vec3 sunDir;
      void main() {
        float h = clamp(vDir.y, -1.0, 1.0);
        vec3 top = vec3(0.20, 0.55, 0.85);
        vec3 mid = vec3(0.55, 0.80, 0.92);
        vec3 bot = vec3(0.98, 0.87, 0.72);
        vec3 col = h > 0.0
          ? mix(mid, top, pow(h, 0.6))
          : mix(mid, bot, clamp(-h * 3.0, 0.0, 1.0));
        float s = max(dot(normalize(vDir), normalize(sunDir)), 0.0);
        col += vec3(1.0, 0.88, 0.66) * pow(s, 600.0) * 1.4;
        col += vec3(1.0, 0.80, 0.55) * pow(s, 8.0) * 0.18;
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  return new THREE.Mesh(geo, mat);
}

export function createLights(sunDir) {
  const group = new THREE.Group();
  group.add(new THREE.HemisphereLight(0xbfe3ff, 0x2a6f97, 0.9));
  const sun = new THREE.DirectionalLight(0xfff2dd, 2.2);
  sun.position.copy(sunDir).multiplyScalar(30);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -10;
  sun.shadow.camera.right = 10;
  sun.shadow.camera.top = 10;
  sun.shadow.camera.bottom = -10;
  sun.shadow.camera.near = 5;
  sun.shadow.camera.far = 70;
  sun.shadow.bias = -0.0005;
  group.add(sun);
  group.add(new THREE.AmbientLight(0x88aacc, 0.25));
  return group;
}

// Drifting puffy clouds made of merged spheres.
export function createClouds() {
  const group = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  const clouds = [];
  const puffs = [
    [[0, 0, 0, 1.5], [1.4, -0.2, 0.3, 1.1], [-1.4, -0.25, -0.2, 1.0], [0.5, 0.7, -0.3, 0.9]],
    [[0, 0, 0, 1.2], [1.1, -0.1, 0.2, 0.9], [-1.1, -0.2, 0.1, 0.85], [-0.2, 0.6, 0, 0.75]],
    [[0, 0, 0, 1.7], [1.6, -0.3, 0, 1.2], [-1.5, -0.2, 0.3, 1.1], [0.3, 0.8, -0.2, 1.0], [2.6, -0.4, -0.3, 0.8]],
  ];
  const spots = [
    [-22, 11, -28, 0.35], [8, 13, -34, 0.28], [26, 10, -20, 0.42],
    [-10, 12, 18, 0.3], [20, 14, 22, 0.24], [-30, 9, 6, 0.38],
  ];
  spots.forEach(([x, y, z, speed], i) => {
    const c = new THREE.Group();
    for (const [px, py, pz, r] of puffs[i % puffs.length]) {
      const m = new THREE.Mesh(new THREE.SphereGeometry(r, 18, 14), mat);
      m.position.set(px, py, pz);
      m.scale.y = 0.62;
      c.add(m);
    }
    c.position.set(x, y, z);
    group.add(c);
    clouds.push({ node: c, speed });
  });
  function update(dt) {
    for (const c of clouds) {
      c.node.position.x += c.speed * dt;
      if (c.node.position.x > 48) c.node.position.x = -48;
    }
  }
  return { group, update };
}

// Distant birds circling high up.
export function createDistantBirds() {
  const group = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x3d4a54, side: THREE.DoubleSide });
  const birds = [];
  const defs = [
    { r: 16, h: 8.5, w: 0.07, phase: 0.0 },
    { r: 20, h: 9.5, w: 0.055, phase: 2.2 },
    { r: 13, h: 7.5, w: 0.09, phase: 4.1 },
  ];
  for (const d of defs) {
    const b = new THREE.Group();
    const wingGeo = new THREE.PlaneGeometry(0.7, 0.2);
    wingGeo.translate(0.35, 0, 0);
    const wl = new THREE.Mesh(wingGeo, mat);
    const wr = new THREE.Mesh(wingGeo, mat);
    wr.rotation.y = Math.PI;
    const pivotL = new THREE.Group();
    const pivotR = new THREE.Group();
    pivotL.add(wl);
    pivotR.add(wr);
    b.add(pivotL, pivotR);
    group.add(b);
    birds.push({ node: b, pivotL, pivotR, ...d });
  }
  const tmp = new THREE.Vector3();
  function update(t) {
    for (const b of birds) {
      const a = t * b.w + b.phase;
      b.node.position.set(Math.cos(a) * b.r, b.h + Math.sin(t * 0.7 + b.phase) * 0.4, Math.sin(a) * b.r);
      tmp.set(Math.cos(a + 0.05) * b.r, b.h, Math.sin(a + 0.05) * b.r);
      b.node.lookAt(tmp);
      const flap = Math.sin(t * 6 + b.phase * 3) * 0.55;
      b.pivotL.rotation.z = flap;
      b.pivotR.rotation.z = -flap;
    }
  }
  return { group, update };
}

// Soft round sprite drawn on a canvas — no image files needed.
export function makeSoftCircleTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.5, 'rgba(255,255,255,0.6)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// Recyclable spray particles kicked up by the board.
export function createSpray(count = 260) {
  const positions = new Float32Array(count * 3);
  const vels = new Float32Array(count * 3);
  const life = new Float32Array(count);
  for (let i = 0; i < count; i++) positions[i * 3 + 1] = -60;
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({
    size: 0.16,
    map: makeSoftCircleTexture(),
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    color: 0xf4fbff,
  });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  let cursor = 0;

  function emit(ox, oy, oz, vx, vy, vz, spread, n) {
    for (let k = 0; k < n; k++) {
      const i = cursor;
      cursor = (cursor + 1) % count;
      positions[i * 3] = ox + (Math.random() - 0.5) * 0.15;
      positions[i * 3 + 1] = oy + Math.random() * 0.08;
      positions[i * 3 + 2] = oz + (Math.random() - 0.5) * 0.3;
      vels[i * 3] = vx + (Math.random() - 0.5) * spread;
      vels[i * 3 + 1] = vy + Math.random() * spread * 0.7;
      vels[i * 3 + 2] = vz + (Math.random() - 0.5) * spread;
      life[i] = 0.5 + Math.random() * 0.6;
    }
  }

  function update(dt) {
    for (let i = 0; i < count; i++) {
      if (life[i] <= 0) continue;
      life[i] -= dt;
      if (life[i] <= 0) {
        positions[i * 3 + 1] = -60;
        continue;
      }
      vels[i * 3 + 1] -= 5.5 * dt;
      positions[i * 3] += vels[i * 3] * dt;
      positions[i * 3 + 1] += vels[i * 3 + 1] * dt;
      positions[i * 3 + 2] += vels[i * 3 + 2] * dt;
    }
    geo.attributes.position.needsUpdate = true;
  }
  return { points, emit, update };
}

// Foam flecks riding the swell to give the sea texture.
export function createFoamFlecks(count = 130) {
  const positions = new Float32Array(count * 3);
  const seeds = [];
  for (let i = 0; i < count; i++) {
    seeds.push({
      x: (Math.random() - 0.5) * 60,
      z: (Math.random() - 0.5) * 36,
      speed: 0.25 + Math.random() * 0.45,
    });
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({
    size: 0.22,
    map: makeSoftCircleTexture(),
    transparent: true,
    opacity: 0.45,
    depthWrite: false,
    color: 0xffffff,
  });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  function update(t) {
    for (let i = 0; i < count; i++) {
      const s = seeds[i];
      let x = s.x + t * s.speed;
      x = ((x + 30) % 60 + 60) % 60 - 30;
      positions[i * 3] = x;
      positions[i * 3 + 1] = waveHeight(x, s.z, t) + 0.04;
      positions[i * 3 + 2] = s.z;
    }
    geo.attributes.position.needsUpdate = true;
  }
  update(0);
  return { points, update };
}

// Foamy wake trailing behind the board.
export function createWake() {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 128;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, 256, 128);
  for (let i = 0; i < 90; i++) {
    const x = Math.random() * 256;
    const y = 64 + (Math.random() - 0.5) * (20 + (256 - x) * 0.25);
    const r = 3 + Math.random() * 9;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, 'rgba(255,255,255,0.5)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const geo = new THREE.PlaneGeometry(3.6, 1.3);
  geo.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(
    geo,
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.85 }),
  );
  mesh.renderOrder = 2;
  function update(px, pz, yaw, t) {
    const fx = Math.cos(yaw);
    const fz = -Math.sin(yaw);
    const tx = px - fx * 2.3;
    const tz = pz - fz * 2.3;
    mesh.position.set(tx, waveHeight(tx, tz, t) + 0.05, tz);
    mesh.rotation.y = yaw;
    mesh.scale.x = 1 + Math.sin(t * 3.0) * 0.05;
  }
  return { mesh, update };
}

// A tiny background island with two palms.
export function createIsland() {
  const group = new THREE.Group();
  const sand = new THREE.Mesh(
    new THREE.SphereGeometry(6, 24, 16),
    new THREE.MeshStandardMaterial({ color: 0xe8d49a, roughness: 1 }),
  );
  sand.scale.set(1, 0.16, 0.7);
  group.add(sand);
  const green = new THREE.Mesh(
    new THREE.SphereGeometry(4.2, 24, 16),
    new THREE.MeshStandardMaterial({ color: 0x4da96b, roughness: 1 }),
  );
  green.scale.set(1, 0.16, 0.7);
  green.position.y = 0.35;
  group.add(green);
  const matTrunk = new THREE.MeshStandardMaterial({ color: 0x8a5a33, roughness: 1 });
  const matLeaf = new THREE.MeshStandardMaterial({ color: 0x2f9e5f, roughness: 1, side: THREE.DoubleSide });
  for (const [px, pz, lean] of [[-0.8, 0.3, 0.18], [1.2, -0.5, -0.14]]) {
    const palm = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, 3.4, 8), matTrunk);
    trunk.position.y = 1.7;
    trunk.rotation.z = lean;
    palm.add(trunk);
    const topX = -Math.sin(lean) * 3.4;
    for (let i = 0; i < 6; i++) {
      const leaf = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 0.5), matLeaf);
      const a = (i / 6) * Math.PI * 2;
      leaf.position.set(topX, 3.4, 0);
      leaf.rotation.y = a;
      leaf.rotation.z = -0.5;
      leaf.translateX(0.9);
      palm.add(leaf);
    }
    palm.position.set(px, 0.6, pz);
    group.add(palm);
  }
  group.position.set(-21, 0, -17);
  return group;
}
