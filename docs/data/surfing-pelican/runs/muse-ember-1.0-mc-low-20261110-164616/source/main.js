import * as THREE from 'three';

// ---------- config ----------
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fe0f0, 28, 95);
const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 300);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

window.addEventListener('error', (e) => {
  const d = document.getElementById('err');
  d.style.display = 'block';
  d.textContent = 'Error: ' + (e.message || e.error);
});

function resize() {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

// ---------- sky ----------
{
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(140, 24, 16),
    new THREE.MeshBasicMaterial({ color: 0x7ecbe8, side: THREE.BackSide, fog: false })
  );
  scene.add(sky);
  const sun = new THREE.Mesh(new THREE.SphereGeometry(4.5, 16, 16), new THREE.MeshBasicMaterial({ color: 0xfff2b0, fog: false }));
  sun.position.set(-40, 28, -60);
  scene.add(sun);
  const sunGlow = new THREE.Mesh(
    new THREE.SphereGeometry(9, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xfff6c9, transparent: true, opacity: 0.25, fog: false })
  );
  sunGlow.position.copy(sun.position);
  scene.add(sunGlow);
}

// ---------- helpers ----------
const mat = (color, rough = 0.6, metal = 0) =>
  new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal });
function blob(geo, material, x = 0, y = 0, z = 0, sx = 1, sy = 1, sz = 1) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.scale.set(sx, sy, sz);
  m.castShadow = true;
  return m;
}
function capsule(r, len, m) {
  return new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, 12), m);
}

// foam sprite texture (drawn, not fetched)
function foamTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, 'rgba(255,255,255,1)');
  grad.addColorStop(0.6, 'rgba(255,255,255,.75)');
  grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

// ---------- ocean ----------
const OCEAN_SIZE = 140;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, 90, 90);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x12a8b5, roughness: 0.35, metalness: 0.1,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

function waveHeight(x, z, t) {
  return Math.sin(x * 0.10 + t * 1.1) * 0.7
       + Math.sin(z * 0.07 - t * 0.8) * 0.8
       + Math.sin((x + z) * 0.045 + t * 0.5) * 1.1;
}
function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    pos.setY(i, waveHeight(x, z, t) - 0.4);
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------- surfboard ----------
const board = new THREE.Group();
{
  const shape = new THREE.Shape();
  shape.moveTo(0, 1.6);
  shape.bezierCurveTo(0.35, 1.0, 0.38, 0.2, 0.32, -0.8);
  shape.bezierCurveTo(0.25, -1.4, 0.12, -1.55, 0, -1.6);
  shape.bezierCurveTo(-0.12, -1.55, -0.25, -1.4, -0.32, -0.8);
  shape.bezierCurveTo(-0.38, 0.2, -0.35, 1.0, 0, 1.6);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.08, bevelEnabled: true, bevelThickness: 0.03,
    bevelSize: 0.03, bevelSegments: 2, steps: 1,
  });
  geo.rotateX(Math.PI / 2);
  const deck = new THREE.Mesh(geo, mat(0xff8c3b, 0.35, 0));
  deck.castShadow = true;
  board.add(deck);
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(0.14, 0.02, 2.5),
    mat(0x14c8d8, 0.4, 0)
  );
  stripe.position.set(0, 0.07, 0.1);
  board.add(stripe);
  board.position.y = 0.05;
  board.rotation.z = -0.16;
  scene.add(board);
}

// ---------- pelican ----------
const pelican = new THREE.Group();
const featherWhite = mat(0xf7f4ec, 0.85, 0);
const featherCream = mat(0xefe4c8, 0.85, 0);
const orange = mat(0xff8c1a, 0.6, 0);
const dark = mat(0x2b2b2b, 0.7, 0);

const bodyG = new THREE.Group();
pelican.add(bodyG);

// body: ellipsoid
bodyG.add(blob(new THREE.SphereGeometry(0.62, 24, 18), featherWhite, 0, 0.55, 0, 1, 0.9, 1.25));

// tail
{
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.7, 8), featherCream);
  tail.position.set(0, 0.5, -0.75);
  tail.rotation.x = 1.9;
  tail.castShadow = true;
  bodyG.add(tail);
}

// legs
for (const s of [-1, 1]) {
  const leg = capsule(0.07, 0.32, orange);
  leg.position.set(s * 0.22, 0.02, 0.1);
  leg.rotation.z = s * 0.25;
  leg.castShadow = true;
  bodyG.add(leg);
  const foot = blob(new THREE.BoxGeometry(0.16, 0.05, 0.3), orange, s * 0.3, -0.18, 0.18, 1, 1, 1);
  foot.rotation.y = s * 0.4;
  bodyG.add(foot);
}

// neck: S-curve tube
const neckGroup = new THREE.Group();
neckGroup.position.set(0, 0.85, 0.45);
bodyG.add(neckGroup);
{
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0.3, 0.28),
    new THREE.Vector3(0, 0.62, 0.35),
    new THREE.Vector3(0, 0.8, 0.28),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(curve, 16, 0.19, 12), featherWhite);
  neck.castShadow = true;
  neckGroup.add(neck);
}

// head + beak + pouch
const headG = new THREE.Group();
headG.position.set(0, 0.88, 0.30);
neckGroup.add(headG);
headG.add(blob(new THREE.SphereGeometry(0.26, 20, 16), featherWhite, 0, 0, 0, 1, 0.95, 1.05));
// eyes
for (const s of [-1, 1]) {
  const eye = blob(new THREE.SphereGeometry(0.05, 10, 10), dark, s * 0.15, 0.06, 0.2, 1, 1, 0.6);
  eye.castShadow = false;
  headG.add(eye);
}
// crown
{
  const crown = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.3, 8), featherCream);
  crown.position.set(0, 0.24, -0.05);
  crown.rotation.x = 0.5;
  crown.castShadow = true;
  headG.add(crown);
}
// beak: long cone + pouch
{
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.85, 12), orange);
  beak.rotation.x = Math.PI / 2 + 0.12;
  beak.position.set(0, -0.02, 0.55);
  beak.scale.set(1, 1, 0.7);
  beak.castShadow = true;
  headG.add(beak);
  const pouch = blob(new THREE.SphereGeometry(0.2, 16, 12), mat(0xffb45e, 0.65, 0), 0, -0.16, 0.38, 1, 0.85, 1.7);
  headG.add(pouch);
}

// wings
function wing(side) {
  const g = new THREE.Group();
  g.position.set(side * 0.42, 0.7, -0.05);
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0.35 * side, 0.28, 0.75 * side, 0.5, 1.05 * side, 0.55);
  shape.bezierCurveTo(0.75 * side, 0.1, 0.5 * side, -0.2, 0.1, -0.28);
  shape.bezierCurveTo(0, -0.34, -0.05 * side, -0.2, 0, 0);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.05, bevelEnabled: true, bevelThickness: 0.02,
    bevelSize: 0.02, bevelSegments: 2,
  });
  const mesh = new THREE.Mesh(geo, featherCream);
  mesh.castShadow = true;
  g.add(mesh);
  // black flight tip
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.35, 8), dark);
  tip.position.set(side * 1.0, 0.5, 0.02);
  tip.rotation.z = side * 1.1;
  g.add(tip);
  return g;
}
const wingL = wing(-1);
const wingR = wing(1);
bodyG.add(wingL, wingR);

scene.add(pelican);

// ---------- distant island + palms ----------
{
  const island = new THREE.Mesh(new THREE.SphereGeometry(9, 20, 14), mat(0x2e8b57, 0.9, 0));
  island.scale.set(1.4, 0.28, 1);
  island.position.set(-38, -1.2, -45);
  scene.add(island);
  const sand = new THREE.Mesh(new THREE.SphereGeometry(7, 20, 14), mat(0xf2e0a0, 0.9, 0));
  sand.scale.set(1.3, 0.14, 1);
  sand.position.set(-38, -0.1, -42);
  scene.add(sand);
  for (let i = 0; i < 5; i++) {
    const x = -44 + i * 3.5;
    const trunk = capsule(0.14, 2.6, mat(0x8b5e3c, 0.9, 0));
    trunk.position.set(x, 1.4, -42 + (i % 2) * 2);
    trunk.rotation.z = (i % 2 ? -1 : 1) * 0.18;
    scene.add(trunk);
    for (let j = 0; j < 6; j++) {
      const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.5, 2.2, 6), mat(0x2f9e44, 0.85, 0));
      leaf.position.set(x + trunk.rotation.z * 1.9, 3.1, -42 + (i % 2) * 2);
      leaf.rotation.set(Math.PI / 2.3, 0, (j / 6) * Math.PI * 2);
      scene.add(leaf);
    }
  }
}

// clouds
const clouds = [];
for (let i = 0; i < 7; i++) {
  const c = new THREE.Group();
  const cm = mat(0xffffff, 1, 0);
  c.add(blob(new THREE.SphereGeometry(1.2, 12, 10), cm, 0, 0, 0, 1, 0.6, 1));
  c.add(blob(new THREE.SphereGeometry(0.9, 12, 10), cm, 1.2, 0.1, 0.2, 1, 0.55, 1));
  c.add(blob(new THREE.SphereGeometry(0.8, 12, 10), cm, -1.1, 0.05, -0.2, 1, 0.5, 1));
  c.position.set((Math.random() - 0.5) * 90, 15 + Math.random() * 8, -35 - Math.random() * 25);
  scene.add(c);
  clouds.push(c);
}

// spray particles
const SPRAY = 120;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY * 3);
sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  size: 0.22, map: foamTexture(), transparent: true, opacity: 0.85,
  depthWrite: false, color: 0xffffff,
}));
scene.add(spray);
const sprayVel = [];
for (let i = 0; i < SPRAY; i++) sprayVel.push(new THREE.Vector3());

// distant gulls
const gulls = [];
for (let i = 0; i < 3; i++) {
  const g = new THREE.Group();
  const wmat = mat(0xffffff, 0.9, 0);
  const w1 = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.03, 0.18), wmat);
  w1.position.x = -0.32;
  const w2 = w1.clone();
  w2.position.x = 0.32;
  const boid = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), wmat);
  boid.scale.set(1, 0.8, 1.8);
  g.add(w1, w2, boid);
  g.scale.setScalar(0.8);
  g.userData = { w1, w2, r: 26 + i * 8, h: 14 + i * 4, speed: 0.12 + i * 0.03, phase: i * 2.1 };
  scene.add(g);
  gulls.push(g);
}

// lights
const sunLight = new THREE.DirectionalLight(0xfff3d6, 2.2);
sunLight.position.set(-18, 26, -22);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -12; sunLight.shadow.camera.right = 12;
sunLight.shadow.camera.top = 12; sunLight.shadow.camera.bottom = -12;
sunLight.shadow.camera.far = 80;
scene.add(sunLight);
scene.add(new THREE.HemisphereLight(0xbfefff, 0x1a7a8c, 0.9));

// foam crest around board
const foamRing = [];
{
  const fm = new THREE.MeshBasicMaterial({ map: foamTexture(), transparent: true, opacity: 0.9, depthWrite: false });
  for (let i = 0; i < 14; i++) {
    const s = new THREE.Sprite(fm);
    s.scale.setScalar(0.4 + Math.random() * 0.5);
    scene.add(s);
    foamRing.push(s);
  }
}

// ---------- animation ----------
const clock = new THREE.Clock();
const camTarget = new THREE.Vector3();
let camAngle = -0.7;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  const dt = Math.min(clock.getDelta(), 0.05) + 0.016;
  const tt = reduced ? t * 0.3 : t;

  updateOcean(tt);

  // surfer rides with local wave
  const wx = Math.sin(tt * 0.35) * 3.2;
  const wz = Math.cos(tt * 0.35) * 2.0;
  const wy = waveHeight(wx, wz, tt) - 0.15;
  const carve = Math.sin(tt * 0.35 + Math.PI / 2);
  pelican.position.set(wx, wy + 0.35, wz);
  board.position.set(wx, wy + 0.08, wz);
  pelican.rotation.set(Math.sin(tt * 1.2) * 0.08, carve * 0.35, carve * 0.28 + Math.sin(tt * 0.9) * 0.06);
  board.rotation.set(pelican.rotation.x * 0.6, pelican.rotation.y, pelican.rotation.z * 0.7);
  // flap
  const flap = Math.sin(tt * 3.2) * (reduced ? 0.15 : 0.4) + 0.15;
  wingL.rotation.z = 0.3 + flap * 0.5;
  wingR.rotation.z = -0.3 - flap * 0.5;
  neckGroup.rotation.x = Math.sin(tt * 1.1) * 0.1;
  headG.rotation.y = Math.sin(tt * 0.7) * 0.2;
  bodyG.rotation.x = Math.sin(tt * 1.4) * 0.05;

  // spray behind board
  for (let i = 0; i < SPRAY; i++) {
    const p = new THREE.Vector3().fromBufferAttribute(sprayGeo.attributes.position, i);
    p.addScaledVector(sprayVel[i], dt);
    sprayVel[i].y -= 4.5 * dt;
    if (p.y < waveHeight(p.x, p.z, tt) - 0.4) {
      p.set(wx - carve * 0.8, wy + 0.1, wz);
      sprayVel[i].set(-carve * 1.2 + (Math.random() - 0.5) * 1.5, 1.5 + Math.random() * 1.5, (Math.random() - 0.5) * 1.5);
    }
    sprayGeo.attributes.position.setXYZ(i, p.x, p.y, p.z);
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // foam ring around board
  foamRing.forEach((s, i) => {
    const a = (i / foamRing.length) * Math.PI * 2 + tt * 0.5;
    s.position.set(wx + Math.cos(a) * 0.9, wy + 0.25 + Math.sin(tt * 3 + i) * 0.06, wz + Math.sin(a) * 0.9);
    s.material.opacity = 0.5 + Math.sin(tt * 2.5 + i * 1.3) * 0.35;
  });

  // clouds drift
  for (const c of clouds) {
    c.position.x += dt * 0.4;
    if (c.position.x > 60) c.position.x = -60;
  }

  // gulls circle
  for (const g of gulls) {
    const u = g.userData;
    const a = tt * u.speed + u.phase;
    g.position.set(Math.cos(a) * u.r, u.h + Math.sin(tt + u.phase) * 0.8, Math.sin(a) * u.r - 10);
    g.lookAt(g.position.x - Math.sin(a), g.position.y, g.position.z + Math.cos(a));
    const f = Math.sin(tt * 6 + u.phase) * 0.5;
    u.w1.rotation.z = f; u.w2.rotation.z = -f;
  }

  // camera: slow orbit, reduced-motion keeps it gentler
  if (!reduced) camAngle += dt * 0.08;
  camTarget.set(wx, 1.2, wz);
  camera.position.set(
    camTarget.x + Math.sin(camAngle) * 6.2,
    2.1 + Math.sin(tt * 0.4) * 0.35,
    camTarget.z + Math.cos(camAngle) * 6.2
  );
  camera.lookAt(camTarget);

  renderer.render(scene, camera);
}
animate();
