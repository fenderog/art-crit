import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0xa8d8ea, 30, 90);
const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 200);
camera.position.set(7.5, 3.6, 9);
camera.lookAt(0, 1.2, 0);

scene.add(new THREE.HemisphereLight(0xcfefff, 0x1a6a8a, 1.1));
const sun = new THREE.DirectionalLight(0xfff2c4, 2.2);
sun.position.set(8, 12, 6); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
scene.add(sun);

const M = (c, r = 0.7, extra = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, ...extra });
function mesh(geo, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true; return m;
}

// ---- Sky: sun disc + clouds ----
scene.add(mesh(new THREE.CircleGeometry(2.2, 32), new THREE.MeshBasicMaterial({ color: 0xffd93d }), -14, 10, -30));
const clouds = new THREE.Group();
const cloudMat = M(0xffffff, 1, { flatShading: true });
for (let i = 0; i < 7; i++) {
  const c = new THREE.Group();
  for (let j = 0; j < 4; j++) c.add(mesh(new THREE.SphereGeometry(0.7 + Math.random() * 0.6, 10, 8), cloudMat, j * 0.9 - 1.2, Math.random() * 0.3, 0));
  c.position.set(-20 + i * 6 + Math.random() * 2, 8 + Math.random() * 4, -18 - Math.random() * 10);
  c.userData.speed = 0.15 + Math.random() * 0.25; clouds.add(c);
}
scene.add(clouds);

// ---- Ocean (animated vertices) ----
const oceanGeo = new THREE.PlaneGeometry(90, 60, 72, 40);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, M(0x118ab2, 0.35, { flatShading: true }));
ocean.receiveShadow = true; ocean.position.y = -0.4; scene.add(ocean);

// ---- The big wave (curling barrel behind surfer) ----
const waveGroup = new THREE.Group(); scene.add(waveGroup);
const waveMat = M(0x06a8c7, 0.25, { flatShading: true, transparent: true, opacity: 0.92, side: THREE.DoubleSide });
// Curled sheet: parametric tube-like surface sweeping along X
function makeWave() {
  const pts = [];
  const segX = 28, segA = 20;
  const pos = [], idx = [];
  for (let i = 0; i <= segX; i++) {
    const x = -9 + (18 * i) / segX;
    const taper = 1 - Math.pow(Math.abs(x) / 11, 2) * 0.45;
    for (let j = 0; j <= segA; j++) {
      const t = j / segA; // 0 base -> 1 lip
      const ang = t * Math.PI * 1.05;
      const R = 3.2 * taper;
      const y = R * Math.sin(ang) - 0.2;
      const z = -2.2 + R * (1 - Math.cos(ang)) * 0.72 - t * 1.2;
      pos.push(x, y, z);
    }
  }
  for (let i = 0; i < segX; i++) for (let j = 0; j < segA; j++) {
    const a = i * (segA + 1) + j, b = a + segA + 1;
    idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx); g.computeVertexNormals();
  return new THREE.Mesh(g, waveMat);
}
const wave = makeWave(); wave.castShadow = true; waveGroup.add(wave);
// Foam crest along the lip
const foamMat = M(0xffffff, 0.9, { flatShading: true });
const foam = new THREE.Group();
for (let x = -8.5; x <= 8.5; x += 0.55) {
  const taper = 1 - Math.pow(Math.abs(x) / 11, 2) * 0.45;
  const s = mesh(new THREE.SphereGeometry(0.28 + Math.random() * 0.22, 8, 6), foamMat, x, 3.2 * taper - 0.15, -2.2 + 3.2 * taper * 0.72 - 1.15);
  foam.add(s);
  const base = mesh(new THREE.SphereGeometry(0.3 + Math.random() * 0.25, 8, 6), foamMat, x, -0.25, -1.4 + Math.random() * 0.5);
  base.scale.y = 0.5; foam.add(base);
}
waveGroup.add(foam);

// ---- Surfboard ----
const board = new THREE.Group();
const boardShape = new THREE.Shape();
boardShape.moveTo(0, 1.6); boardShape.bezierCurveTo(0.35, 1.0, 0.38, -0.6, 0.22, -1.5);
boardShape.lineTo(-0.22, -1.5); boardShape.bezierCurveTo(-0.38, -0.6, -0.35, 1.0, 0, 1.6);
const boardGeo = new THREE.ExtrudeGeometry(boardShape, { depth: 0.09, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.02 });
boardGeo.rotateX(-Math.PI / 2);
const deck = mesh(boardGeo, M(0xef476f, 0.4)); board.add(deck);
const stripe = mesh(new THREE.BoxGeometry(0.14, 0.02, 2.6), M(0xffd166, 0.4), 0, 0.1, 0); board.add(stripe);
const fin = mesh(new THREE.BoxGeometry(0.03, 0.35, 0.35), M(0x073b4c, 0.5), 0, -0.15, 1.15); board.add(fin);

// ---- Pelican ---- (facing +X travel computed by rotation below; built facing -Z nose of board = -Z? Board nose is -Z after rotateX: shape +Y -> -Z)
const pelican = new THREE.Group();
const white = M(0xf8f6f0, 0.85), grey = M(0xd9d4c8, 0.9), orange = M(0xff8c42, 0.6), dark = M(0x222222, 0.5);
// Body: plump teardrop
const body = mesh(new THREE.SphereGeometry(0.62, 24, 18), white, 0, 0.85, 0.15);
body.scale.set(0.9, 1, 1.25); pelican.add(body);
const belly = mesh(new THREE.SphereGeometry(0.5, 20, 14), M(0xfffaf0, 0.9), 0, 0.72, -0.05);
belly.scale.set(0.85, 0.9, 1.1); pelican.add(belly);
// Tail feathers
for (let i = -1; i <= 1; i++) {
  const t = mesh(new THREE.ConeGeometry(0.12, 0.55, 8), grey, i * 0.16, 1.0, 0.85);
  t.rotation.x = -1.9; t.rotation.z = i * 0.25; pelican.add(t);
}
// Neck + head group (animated bob)
const neckGroup = new THREE.Group(); neckGroup.position.set(0, 1.25, -0.35); pelican.add(neckGroup);
const neck = mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.7, 12), white, 0, 0.25, -0.08);
neck.rotation.x = 0.35; neckGroup.add(neck);
const head = mesh(new THREE.SphereGeometry(0.3, 20, 16), white, 0, 0.62, -0.28);
head.scale.set(0.9, 0.95, 1.1); neckGroup.add(head);
// Crest tuft
const crest = mesh(new THREE.ConeGeometry(0.09, 0.3, 8), M(0xffd166, 0.8), 0, 0.9, -0.18);
crest.rotation.x = -0.5; neckGroup.add(crest);
// Eyes
for (const s of [-1, 1]) {
  neckGroup.add(mesh(new THREE.SphereGeometry(0.05, 10, 8), dark, s * 0.17, 0.68, -0.48));
  neckGroup.add(mesh(new THREE.SphereGeometry(0.02, 8, 6), M(0xffffff, 0.2), s * 0.19, 0.71, -0.52));
}
// Long beak + pouch (pouch animated)
const beak = mesh(new THREE.ConeGeometry(0.11, 0.95, 10), orange, 0, 0.6, -0.95);
beak.rotation.x = -Math.PI / 2 - 0.08; beak.scale.set(1, 1, 0.55); neckGroup.add(beak);
const pouch = mesh(new THREE.SphereGeometry(0.22, 14, 10), M(0xffa552, 0.7), 0, 0.46, -0.72);
pouch.scale.set(0.75, 0.8, 1.7); neckGroup.add(pouch);
// Fish tail sticking out of pouch
const fish = mesh(new THREE.ConeGeometry(0.07, 0.22, 6), M(0x4cc9f0, 0.4), 0, 0.52, -0.55);
fish.rotation.x = 0.6; neckGroup.add(fish);
// Wings (animated balancing)
function makeWing(side) {
  const g = new THREE.Group(); g.position.set(side * 0.5, 1.15, 0.1);
  const w = mesh(new THREE.SphereGeometry(0.55, 16, 10), grey, side * 0.55, 0, 0.1);
  w.scale.set(1.35, 0.18, 0.65); g.add(w);
  const tip = mesh(new THREE.ConeGeometry(0.14, 0.6, 8), dark, side * 1.15, -0.02, 0.15);
  tip.rotation.z = side * Math.PI / 2; tip.scale.z = 0.4; g.add(tip);
  pelican.add(g); return g;
}
const wingL = makeWing(-1), wingR = makeWing(1);
// Legs + webbed feet planted on board
for (const s of [-1, 1]) {
  const leg = mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.35, 8), orange, s * 0.22, 0.32, s > 0 ? 0.35 : -0.25);
  pelican.add(leg);
  const foot = mesh(new THREE.SphereGeometry(0.16, 10, 8), orange, s * 0.22, 0.14, (s > 0 ? 0.35 : -0.25) - 0.1);
  foot.scale.set(0.9, 0.25, 1.6); pelican.add(foot);
}
// Sunglasses for flair
const shades = new THREE.Group(); shades.position.set(0, 0.7, -0.52); neckGroup.add(shades);
for (const s of [-1, 1]) { const lens = mesh(new THREE.BoxGeometry(0.16, 0.12, 0.03), dark, s * 0.14, 0, 0); shades.add(lens); }
shades.add(mesh(new THREE.BoxGeometry(0.14, 0.03, 0.03), dark, 0, 0.03, 0));

const surfer = new THREE.Group();
surfer.add(board); pelican.position.y = 0.12; surfer.add(pelican);
scene.add(surfer);

// ---- Spray particles ----
const N = 220, sprayPos = new Float32Array(N * 3), sprayVel = [];
for (let i = 0; i < N; i++) sprayVel.push({ life: Math.random() });
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.09, transparent: true, opacity: 0.85 }));
scene.add(spray);

// Distant gulls (simple V shapes drifting)
const gulls = new THREE.Group();
for (let i = 0; i < 5; i++) {
  const g = new THREE.Group();
  for (const s of [-1, 1]) { const w = mesh(new THREE.BoxGeometry(0.5, 0.03, 0.12), white, s * 0.25, 0, 0); w.rotation.z = s * 0.5; g.add(w); }
  g.position.set(-15 + i * 7, 6 + Math.random() * 3, -14 - Math.random() * 6);
  g.userData = { off: Math.random() * 9 }; gulls.add(g);
}
scene.add(gulls);

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Surfer rides along the wave face: travels in X, carves up/down, loops
  const travel = ((t * 0.9 + 6) % 12) - 6;          // -6..6
  const carve = Math.sin(t * 0.7);
  surfer.position.set(travel, 0.35 + carve * 0.55 + Math.sin(t * 3.1) * 0.06, -0.9 + carve * -0.5);
  surfer.rotation.set(Math.sin(t * 1.3) * 0.06 - carve * 0.18, -Math.PI / 2 + Math.cos(t * 0.7) * 0.35, Math.sin(t * 1.7) * 0.09 + carve * 0.12);

  // Pelican balancing
  wingL.rotation.z = 0.55 + Math.sin(t * 2.6) * 0.35;
  wingR.rotation.z = -0.55 - Math.sin(t * 2.6 + 0.6) * 0.35;
  wingL.rotation.x = Math.sin(t * 1.9) * 0.15; wingR.rotation.x = -wingL.rotation.x;
  neckGroup.rotation.x = Math.sin(t * 2.2) * 0.1;
  neckGroup.rotation.y = Math.sin(t * 0.5) * 0.25;
  pouch.scale.y = 0.8 + Math.sin(t * 3.4) * 0.12;
  fish.rotation.x = 0.6 + Math.sin(t * 6) * 0.3;
  pelican.rotation.z = Math.sin(t * 2.6) * 0.05;
  pelican.position.y = 0.12 + Math.abs(Math.sin(t * 2.2)) * 0.04; // knee-bend bounce

  // Ocean swell
  const p = oceanGeo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    p.setY(i, Math.sin(x * 0.35 + t * 1.6) * 0.18 + Math.cos(z * 0.5 + t * 1.1) * 0.14);
  }
  p.needsUpdate = true; oceanGeo.computeVertexNormals();

  // Wave gently breathes; foam jiggles
  waveGroup.position.y = Math.sin(t * 0.9) * 0.12;
  foam.children.forEach((s, i) => { s.position.y += Math.sin(t * 4 + i * 1.7) * 0.002; });

  // Spray from board tail
  for (let i = 0; i < N; i++) {
    const v = sprayVel[i]; v.life -= 0.016;
    if (v.life <= 0) {
      v.life = 0.4 + Math.random() * 0.6;
      sprayPos[i * 3] = surfer.position.x - 1.2; sprayPos[i * 3 + 1] = surfer.position.y; sprayPos[i * 3 + 2] = surfer.position.z + (Math.random() - 0.5) * 0.4;
      v.vx = -0.5 - Math.random(); v.vy = 1 + Math.random() * 1.6; v.vz = (Math.random() - 0.5) * 0.8;
    }
    v.vy -= 0.06;
    sprayPos[i * 3] += v.vx * 0.03; sprayPos[i * 3 + 1] += v.vy * 0.03; sprayPos[i * 3 + 2] += v.vz * 0.03;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  clouds.children.forEach(c => { c.position.x += c.userData.speed * 0.016; if (c.position.x > 24) c.position.x = -24; });
  gulls.children.forEach(g => { g.position.x += 0.02; g.position.y += Math.sin(t * 2 + g.userData.off) * 0.004; g.children.forEach((w, i) => w.rotation.z = (i ? 1 : -1) * (0.5 + Math.sin(t * 6 + g.userData.off) * 0.35)); if (g.position.x > 22) g.position.x = -22; });

  // Slow cinematic camera drift (non-interactive)
  camera.position.x = 7.5 + Math.sin(t * 0.11) * 1.6;
  camera.position.y = 3.6 + Math.sin(t * 0.17) * 0.5;
  camera.lookAt(surfer.position.x * 0.35, 1.3, 0);

  renderer.render(scene, camera);
}
animate();
