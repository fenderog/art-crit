import * as THREE from 'three';

const container = document.getElementById('app');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3ef);
scene.fog = new THREE.Fog(0x8fd3ef, 18, 42);

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 3.4, 10.5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xdff6ff, 0x1a6a8a, 1.6));
const sunLight = new THREE.DirectionalLight(0xfff2c8, 2.6);
sunLight.position.set(-6, 10, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10; sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10; sunLight.shadow.camera.bottom = -10;
scene.add(sunLight);

// --- materials ---
const M = {
  feather: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85 }),
  featherGrey: new THREE.MeshStandardMaterial({ color: 0xd9e2e8, roughness: 0.9 }),
  darkTip: new THREE.MeshStandardMaterial({ color: 0x2b3440, roughness: 0.8 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xff8c1a, roughness: 0.55 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xffb03a, roughness: 0.6 }),
  eye: new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.25 }),
  board: new THREE.MeshStandardMaterial({ color: 0x0fb5a8, roughness: 0.35 }),
  boardStripe: new THREE.MeshStandardMaterial({ color: 0xffd23f, roughness: 0.4 }),
  water: new THREE.MeshStandardMaterial({ color: 0x0e8fc2, roughness: 0.35, metalness: 0.05, transparent: true, opacity: 0.96 }),
  deep: new THREE.MeshStandardMaterial({ color: 0x0a6ea8, roughness: 0.45 }),
  foam: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9 }),
  sand: new THREE.MeshStandardMaterial({ color: 0xf2d492, roughness: 1 }),
  trunk: new THREE.MeshStandardMaterial({ color: 0x8a5a33, roughness: 1 }),
  leaf: new THREE.MeshStandardMaterial({ color: 0x2fa84f, roughness: 0.9 }),
  cloud: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 }),
  sun: new THREE.MeshBasicMaterial({ color: 0xffe89a }),
};

function mesh(geo, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

// --- sky sun & clouds ---
const sunBall = mesh(new THREE.SphereGeometry(0.9, 24, 24), M.sun, -7.5, 5.8, -12);
sunBall.castShadow = false; scene.add(sunBall);
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  [[0,0,0,1],[1.1,0.15,0,0.75],[-1.05,0.1,0,0.7],[0.4,0.45,0,0.65]].forEach(([px,py,pz,r])=>{
    const c = mesh(new THREE.SphereGeometry(r, 18, 14), M.cloud, px, py, pz);
    c.castShadow = false; g.add(c);
  });
  g.position.set(x, y, z); g.scale.setScalar(s); scene.add(g); clouds.push(g); return g;
}
makeCloud(-5, 5.2, -10, 1.1); makeCloud(4.5, 6, -11, 1.4); makeCloud(8, 4.2, -9, 0.8); makeCloud(-9, 4, -9, 0.9);

// --- ocean ---
const oceanGeo = new THREE.PlaneGeometry(70, 36, 90, 44);
oceanGeo.rotateX(-Math.PI / 2);
const ocean = new THREE.Mesh(oceanGeo, M.water);
ocean.position.y = -0.55; ocean.receiveShadow = true; scene.add(ocean);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = oceanPos.array.slice();

function waveY(x, z, t) {
  return Math.sin(x * 0.45 + t * 1.3) * 0.22 + Math.cos(z * 0.55 + t * 0.9) * 0.16 + Math.sin((x + z) * 0.28 + t * 0.6) * 0.1;
}

// --- big curling wave behind rider ---
const waveGroup = new THREE.Group(); waveGroup.position.set(0.5, -0.4, -3.2); scene.add(waveGroup);
const curl = mesh(new THREE.TorusGeometry(3.1, 1.05, 20, 40, Math.PI * 1.15), M.deep, -1.2, 2.2, 0);
curl.rotation.z = Math.PI * 0.85; curl.scale.set(1.25, 1, 0.55); waveGroup.add(curl);
const face = mesh(new THREE.CylinderGeometry(3.4, 3.4, 7.5, 24, 1, true, 0, Math.PI * 0.85), M.water, 0.6, 0.4, 0);
face.rotation.z = Math.PI / 2; face.rotation.y = Math.PI / 2; face.material = M.water; waveGroup.add(face);
const crestFoam = [];
for (let i = 0; i < 16; i++) {
  const a = (i / 15) * Math.PI * 1.05 + 0.5;
  const f = mesh(new THREE.SphereGeometry(0.28 + Math.random() * 0.22, 10, 8), M.foam,
    -1.2 + Math.cos(a) * 3.9, 2.2 + Math.sin(a) * 3.55, (Math.random() - 0.5) * 0.7);
  f.castShadow = false; waveGroup.add(f); crestFoam.push(f);
}

// --- distant islands with palms ---
function island(x, z, s) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.ConeGeometry(1.6, 0.7, 20), M.sand, 0, 0, 0));
  const trunk = mesh(new THREE.CylinderGeometry(0.07, 0.11, 1.5, 8), M.trunk, 0.25, 0.9, 0); trunk.rotation.z = -0.25; g.add(trunk);
  for (let i = 0; i < 5; i++) {
    const leaf = mesh(new THREE.ConeGeometry(0.16, 1.1, 6), M.leaf, 0.45, 1.75, 0);
    leaf.rotation.z = 1.15; leaf.rotation.y = (i / 5) * Math.PI * 2; leaf.position.x = 0.45 + Math.cos(i * 1.26) * 0.3; leaf.position.z = Math.sin(i * 1.26) * 0.3; g.add(leaf);
  }
  g.position.set(x, -0.45, z); g.scale.setScalar(s); scene.add(g);
}
island(-9, -8, 1.2); island(9.5, -9, 1.5);

// --- surfboard + pelican (the rider) ---
const rider = new THREE.Group(); scene.add(rider);

const board = new THREE.Group(); rider.add(board);
const deck = mesh(new THREE.SphereGeometry(1, 24, 16), M.board, 0, 0, 0); deck.scale.set(2.35, 0.11, 0.52); board.add(deck);
const stripe = mesh(new THREE.SphereGeometry(1, 24, 12), M.boardStripe, 0, 0.045, 0); stripe.scale.set(2.0, 0.07, 0.14); board.add(stripe);
const fin = mesh(new THREE.ConeGeometry(0.16, 0.4, 8), M.boardStripe, -1.7, -0.18, 0); fin.rotation.z = Math.PI; board.add(fin);

const pelican = new THREE.Group(); pelican.position.y = 0.12; board.add(pelican);

// feet & legs
[-0.35, 0.35].forEach((x) => {
  pelican.add(mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.42, 8), M.beak, x, 0.22, 0.08));
  const foot = mesh(new THREE.SphereGeometry(0.16, 10, 8), M.beak, x, 0.03, 0.16); foot.scale.set(1, 0.35, 1.6); pelican.add(foot);
});
// body
const body = mesh(new THREE.SphereGeometry(0.78, 28, 22), M.feather, 0, 0.78, 0); body.scale.set(1.15, 0.82, 0.72); pelican.add(body);
const belly = mesh(new THREE.SphereGeometry(0.62, 20, 16), M.featherGrey, 0.12, 0.62, 0.28); belly.scale.set(1, 0.7, 0.6); pelican.add(belly);
// tail
const tail = mesh(new THREE.ConeGeometry(0.34, 0.85, 10), M.featherGrey, -0.95, 0.92, 0); tail.rotation.z = 1.25; tail.scale.set(1, 1, 0.45); pelican.add(tail);

// neck as a tube along an S-curve
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0.62, 0.95, 0), new THREE.Vector3(0.95, 1.25, 0),
  new THREE.Vector3(0.82, 1.62, 0), new THREE.Vector3(1.02, 1.95, 0),
]);
const neck = mesh(new THREE.TubeGeometry(neckCurve, 20, 0.21, 12), M.feather); pelican.add(neck);

// head group (bobs independently)
const head = new THREE.Group(); head.position.set(1.05, 2.02, 0); pelican.add(head);
head.add(mesh(new THREE.SphereGeometry(0.34, 22, 18), M.feather, 0, 0, 0));
for (let i = 0; i < 3; i++) { const c = mesh(new THREE.ConeGeometry(0.09, 0.4, 6), M.featherGrey, -0.28, 0.22 - i * 0.07, (i - 1) * 0.12); c.rotation.z = 1.9; head.add(c); }
// long beak + pouch
const beak = mesh(new THREE.ConeGeometry(0.16, 1.55, 12), M.beak, 0.95, -0.06, 0); beak.rotation.z = -Math.PI / 2 + 0.12; beak.scale.set(1, 1, 0.55); head.add(beak);
const pouch = mesh(new THREE.SphereGeometry(0.3, 16, 12), M.pouch, 0.72, -0.28, 0); pouch.scale.set(1.9, 0.65, 0.7); head.add(pouch);
head.add(mesh(new THREE.SphereGeometry(0.07, 10, 8), M.beak, 1.68, 0.02, 0)); // beak tip knob
[-1, 1].forEach((side) => {
  const eye = mesh(new THREE.SphereGeometry(0.055, 10, 8), M.eye, 0.16, 0.1, 0.3 * side); head.add(eye);
  const ring = mesh(new THREE.TorusGeometry(0.09, 0.02, 8, 16), M.pouch, 0.16, 0.1, 0.31 * side); head.add(ring);
});

// wings on shoulder pivots (for balancing flap)
function makeWing(side) {
  const pivot = new THREE.Group(); pivot.position.set(-0.1, 1.05, 0.42 * side); pelican.add(pivot);
  const wing = mesh(new THREE.SphereGeometry(0.85, 18, 12), M.feather, -0.25, 0, 0.55 * side);
  wing.scale.set(1.15, 0.14, 0.75); pivot.add(wing);
  const tip = mesh(new THREE.SphereGeometry(0.5, 14, 10), M.darkTip, -0.75, 0, 1.05 * side);
  tip.scale.set(1.1, 0.1, 0.6); pivot.add(tip);
  return pivot;
}
const wingL = makeWing(1), wingR = makeWing(-1);

// --- spray particles ---
const sprayGeo = new THREE.BufferGeometry();
const sprayCount = 90, sprayPos = new Float32Array(sprayCount * 3), sprayVel = [];
for (let i = 0; i < sprayCount; i++) { sprayVel.push(new THREE.Vector3()); sprayPos[i * 3 + 1] = -10; }
sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.14, transparent: true, opacity: 0.85 }));
spray.castShadow = false; scene.add(spray);
let sprayIdx = 0;
function emitSpray(origin) {
  for (let n = 0; n < 3; n++) {
    const i = sprayIdx = (sprayIdx + 1) % sprayCount;
    sprayPos[i * 3] = origin.x - 1.6; sprayPos[i * 3 + 1] = origin.y; sprayPos[i * 3 + 2] = origin.z + (Math.random() - 0.5) * 0.6;
    sprayVel[i].set(-1 - Math.random() * 1.5, 1 + Math.random() * 1.6, (Math.random() - 0.5) * 1.2);
  }
}

// --- animation ---
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime() * (reduced ? 0.25 : 1);

  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    oceanPos.setY(i, waveY(x, z, t));
  }
  oceanPos.needsUpdate = true; oceanGeo.computeVertexNormals();

  const rx = Math.sin(t * 0.45) * 2.4;
  const rz = -0.6 + Math.sin(t * 0.3) * 0.3;
  const ry = 0.15 + waveY(rx, rz, t) + Math.abs(Math.sin(t * 1.8)) * 0.08;
  rider.position.set(rx, ry, rz);
  rider.rotation.set(Math.sin(t * 1.8) * 0.05 - 0.04, -0.35 + Math.cos(t * 0.45) * 0.18, Math.sin(t * 0.9) * 0.09);
  pelican.rotation.z = Math.sin(t * 1.8 + 0.6) * 0.045;
  pelican.position.y = 0.12 + Math.abs(Math.sin(t * 1.8)) * 0.05;

  wingL.rotation.x = 0.55 + Math.sin(t * 2.2) * 0.38;
  wingR.rotation.x = -0.55 - Math.sin(t * 2.2 + 0.4) * 0.38;
  wingL.rotation.z = wingR.rotation.z = Math.sin(t * 1.1) * 0.08;
  head.rotation.z = Math.sin(t * 1.4) * 0.09 - 0.05;
  head.rotation.y = Math.sin(t * 0.5) * 0.22;
  head.position.y = 2.02 + Math.sin(t * 1.8) * 0.04;
  pouch.scale.set(1.9 + Math.sin(t * 2.6) * 0.12, 0.65 + Math.sin(t * 2.6) * 0.08, 0.7);
  tail.rotation.x = Math.sin(t * 3) * 0.18;

  crestFoam.forEach((f, i) => { const s = 1 + Math.sin(t * 2.4 + i) * 0.18; f.scale.setScalar(s); });
  waveGroup.position.y = -0.4 + Math.sin(t * 0.8) * 0.12;
  clouds.forEach((c, i) => { c.position.x += 0.0022 * (i + 1); if (c.position.x > 13) c.position.x = -13; });

  emitSpray(rider.position);
  for (let i = 0; i < sprayCount; i++) {
    if (sprayPos[i * 3 + 1] < -5) continue;
    sprayVel[i].y -= 0.045;
    sprayPos[i * 3] += sprayVel[i].x * 0.03; sprayPos[i * 3 + 1] += sprayVel[i].y * 0.03; sprayPos[i * 3 + 2] += sprayVel[i].z * 0.03;
    if (sprayPos[i * 3 + 1] < -0.4) sprayPos[i * 3 + 1] = -10;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  camera.position.x = Math.sin(t * 0.22) * 0.9;
  camera.position.y = 3.4 + Math.sin(t * 0.5) * 0.18;
  camera.lookAt(0, 1.15, 0);
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
