import * as THREE from "three";

// ---------------------------------------------------------------------------
// Surfing Pelican — animated, non-interactive 3JS vignette.
// Everything is procedural (no external assets), so the packaged page
// works offline in a sandboxed iframe.
// ---------------------------------------------------------------------------

const container = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c5e8);
scene.fog = new THREE.Fog(0x9fd3ec, 18, 55);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  200
);
camera.position.set(0, 3.4, 9.2);

// --- Lights ----------------------------------------------------------------
scene.add(new THREE.HemisphereLight(0xcfeaff, 0x2a6f8e, 0.95));

const sunLight = new THREE.DirectionalLight(0xfff2d9, 2.0);
sunLight.position.set(-6, 9, 5);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(1024, 1024);
sunLight.shadow.camera.left = -10;
sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10;
sunLight.shadow.camera.bottom = -10;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0x9fd8ff, 0.5);
fillLight.position.set(5, 3, -4);
scene.add(fillLight);

// --- Sky props: sun disc, clouds, distant islands ---------------------------
function makeGlowTexture() {
  const c = document.createElement("canvas");
  c.width = 128;
  c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
  g.addColorStop(0, "rgba(255,250,220,1)");
  g.addColorStop(0.35, "rgba(255,240,190,0.85)");
  g.addColorStop(1, "rgba(255,240,190,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const sun = new THREE.Mesh(
  new THREE.SphereGeometry(1.1, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff3c4, fog: false })
);
sun.position.set(-9, 8.5, -22);
scene.add(sun);

const glow = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: makeGlowTexture(),
    transparent: true,
    depthWrite: false,
    fog: false
  })
);
glow.scale.set(9, 9, 1);
glow.position.copy(sun.position);
scene.add(glow);

const cloudMaterial = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 1,
  flatShading: true
});
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const puffs = [
    [0, 0, 0, 0.9],
    [0.9, -0.1, 0.1, 0.65],
    [-0.9, -0.12, 0, 0.6],
    [0.35, 0.35, 0, 0.55],
    [-0.35, 0.3, 0.1, 0.5]
  ];
  for (const [px, py, pz, pr] of puffs) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(pr, 12, 10), cloudMaterial);
    m.position.set(px, py, pz);
    m.scale.y = 0.62;
    g.add(m);
  }
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  scene.add(g);
  clouds.push({ group: g, speed: 0.08 + Math.random() * 0.12, x });
}
makeCloud(-10, 7.2, -16, 1.4);
makeCloud(3, 8.4, -19, 1.8);
makeCloud(11, 6.6, -14, 1.1);

const islandMaterial = new THREE.MeshStandardMaterial({
  color: 0x3f7d5d,
  roughness: 1,
  flatShading: true
});
function makeIsland(x, z, s) {
  const m = new THREE.Mesh(new THREE.ConeGeometry(2.2 * s, 1.6 * s, 7), islandMaterial);
  m.position.set(x, -0.15, z);
  scene.add(m);
  const palm = new THREE.Mesh(
    new THREE.ConeGeometry(0.5 * s, 0.9 * s, 6),
    new THREE.MeshStandardMaterial({ color: 0x2f6b4c, flatShading: true, roughness: 1 })
  );
  palm.position.set(x, 0.8 * s, z);
  scene.add(palm);
}
makeIsland(-13, -18, 1.6);
makeIsland(14, -21, 2.1);

// --- Ocean ------------------------------------------------------------------
const OCEAN_SIZE = 70;
const OCEAN_SEG = 90;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1e86b8,
  roughness: 0.55,
  metalness: 0.05,
  flatShading: true
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.45 + t * 1.6) * 0.22 +
    Math.sin(z * 0.6 - t * 1.2) * 0.16 +
    Math.sin((x + z) * 0.3 + t * 2.1) * 0.1
  );
}

function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  const arr = pos.array;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    arr[i * 3 + 1] = waveHeight(x, z, t);
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// --- Stylised breaking swell behind the surfer ------------------------------
const swellMat = new THREE.MeshStandardMaterial({
  color: 0x2fa3c7,
  roughness: 0.4,
  metalness: 0.05,
  transparent: true,
  opacity: 0.92,
  side: THREE.DoubleSide,
  flatShading: true
});
const swell = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.2, 7, 24, 1, true, Math.PI * 0.05, Math.PI * 0.55), swellMat);
swell.rotation.z = Math.PI / 2;
swell.rotation.y = Math.PI / 2;
swell.position.set(0, 0.4, -3.4);
scene.add(swell);

const swellLipMat = new THREE.MeshStandardMaterial({
  color: 0xeafcff,
  roughness: 0.9,
  flatShading: true,
  transparent: true,
  opacity: 0.95
});
const swellLip = new THREE.Mesh(new THREE.TorusGeometry(4.2, 0.32, 8, 24, Math.PI * 0.55), swellLipMat);
swellLip.position.set(0, 0.4, -3.4);
swellLip.rotation.y = Math.PI / 2;
swellLip.rotation.z = Math.PI * 0.05;
scene.add(swellLip);

// --- Surfboard ----------------------------------------------------------------
const surfer = new THREE.Group(); // whole rider: board + pelican + foam
scene.add(surfer);

const boardMat = new THREE.MeshStandardMaterial({ color: 0xff5a5a, roughness: 0.35 });
const board = new THREE.Mesh(new THREE.CapsuleGeometry(0.5, 2.6, 8, 20), boardMat);
board.rotation.x = Math.PI / 2;
board.scale.set(1, 1, 0.22);
board.castShadow = true;
board.position.y = 0.55;
surfer.add(board);

const stripe = new THREE.Mesh(
  new THREE.CapsuleGeometry(0.16, 2.5, 4, 12),
  new THREE.MeshStandardMaterial({ color: 0xfff6e8, roughness: 0.5 })
);
stripe.rotation.x = Math.PI / 2;
stripe.scale.set(1, 1, 0.24);
stripe.position.set(0, 0.62, 0.05);
surfer.add(stripe);

// Foam collar around the board (wake)
const foamMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
const foam = new THREE.Mesh(new THREE.TorusGeometry(0.85, 0.16, 8, 28), foamMat);
foam.rotation.x = Math.PI / 2;
foam.scale.set(1, 1.9, 1);
foam.position.y = 0.42;
surfer.add(foam);

// --- Pelican (all primitives) --------------------------------------------------
const pelican = new THREE.Group();
pelican.position.y = 0.62;
surfer.add(pelican);

const bodyMat = new THREE.MeshStandardMaterial({ color: 0xe9e2d4, roughness: 0.8, flatShading: true });
const greyMat = new THREE.MeshStandardMaterial({ color: 0x9a938a, roughness: 0.85, flatShading: true });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x57504a, roughness: 0.9, flatShading: true });
const beakMat = new THREE.MeshStandardMaterial({ color: 0xf5a63b, roughness: 0.55, flatShading: true });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xef9d8c, roughness: 0.7, flatShading: true });
const legMat = new THREE.MeshStandardMaterial({ color: 0xe07b39, roughness: 0.8 });

const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 20, 16), bodyMat);
body.scale.set(1, 0.85, 1.35);
body.position.y = 0.62;
body.castShadow = true;
pelican.add(body);

const tail = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.55, 8), greyMat);
tail.rotation.x = -Math.PI / 2 - 0.35;
tail.position.set(0, 0.72, -0.78);
tail.castShadow = true;
pelican.add(tail);

// Feet planted in surf stance
function makeFoot(x, z) {
  const g = new THREE.Group();
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.3, 8), legMat);
  leg.position.y = 0.15;
  g.add(leg);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.07, 0.34), legMat);
  foot.position.set(0, 0.035, 0.08);
  foot.castShadow = true;
  g.add(foot);
  g.position.set(x, 0, z);
  return g;
}
pelican.add(makeFoot(-0.14, 0.28));
pelican.add(makeFoot(0.16, -0.3));

// Neck + head (head bobs as its own group)
const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.55, 10), bodyMat);
neck.position.set(0, 1.05, 0.5);
neck.rotation.x = 0.35;
neck.castShadow = true;
pelican.add(neck);

const headGroup = new THREE.Group();
headGroup.position.set(0, 1.38, 0.62);
pelican.add(headGroup);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 18, 14), bodyMat);
head.castShadow = true;
headGroup.add(head);

const crest = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.4, 6), greyMat);
crest.position.set(0, 0.18, -0.24);
crest.rotation.x = -0.9;
headGroup.add(crest);

for (const side of [-1, 1]) {
  const eye = new THREE.Mesh(
    new THREE.SphereGeometry(0.055, 10, 8),
    new THREE.MeshStandardMaterial({ color: 0x1c1a18, roughness: 0.3 })
  );
  eye.position.set(0.17 * side, 0.07, 0.22);
  headGroup.add(eye);
}

// Long beak pointing forward, pouch slung beneath
const beak = new THREE.Mesh(new THREE.ConeGeometry(0.11, 1.0, 10), beakMat);
beak.rotation.x = Math.PI / 2 + 0.12;
beak.position.set(0, -0.03, 0.62);
beak.castShadow = true;
headGroup.add(beak);

const beakTip = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.18, 8), beakMat);
beakTip.rotation.x = Math.PI / 2 + 0.35;
beakTip.position.set(0, -0.1, 1.12);
headGroup.add(beakTip);

const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.3, 14, 12), pouchMat);
pouch.scale.set(0.75, 0.85, 1.5);
pouch.position.set(0, -0.32, 0.5);
pouch.castShadow = true;
headGroup.add(pouch);

// Wings: pivoted at the shoulders, each with an outer tip segment
function makeWing(side) {
  const shoulder = new THREE.Group();
  shoulder.position.set(0.42 * side, 0.85, 0.05);

  const inner = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.09, 0.55), greyMat);
  inner.position.x = 0.45 * side;
  inner.castShadow = true;
  shoulder.add(inner);

  const tipPivot = new THREE.Group();
  tipPivot.position.x = 0.88 * side;
  shoulder.add(tipPivot);

  const tip = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.07, 0.42), darkMat);
  tip.position.x = 0.32 * side;
  tip.castShadow = true;
  tipPivot.add(tip);

  pelican.add(shoulder);
  return { shoulder, tipPivot };
}
const wingL = makeWing(-1);
const wingR = makeWing(1);

// --- Sea spray (procedural sprite points) -------------------------------------
function makeSprayTexture() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const SPRAY_N = 90;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_N * 3);
const spraySeed = new Float32Array(SPRAY_N * 2);
for (let i = 0; i < SPRAY_N; i++) {
  spraySeed[i * 2] = Math.random();
  spraySeed[i * 2 + 1] = Math.random();
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({
    map: makeSprayTexture(),
    size: 0.35,
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    color: 0xffffff
  })
);
scene.add(spray);

function updateSpray(t) {
  const arr = sprayGeo.attributes.position.array;
  const bx = surfer.position.x;
  const by = surfer.position.y;
  const bz = surfer.position.z;
  for (let i = 0; i < SPRAY_N; i++) {
    const s1 = spraySeed[i * 2];
    const s2 = spraySeed[i * 2 + 1];
    const life = (t * (0.5 + s1 * 0.7) + s2) % 1;
    arr[i * 3] = bx - 0.3 - life * (1.6 + s1 * 1.6) + Math.sin((t + i) * 3) * 0.15;
    arr[i * 3 + 1] = by + 0.3 + life * (1.1 + s2 * 1.2);
    arr[i * 3 + 2] = bz + Math.sin(i * 2.3) * 0.5 - life * 0.6;
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// --- Animation ------------------------------------------------------------------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Ocean swell
  updateOcean(t);

  // Surfer carves gently across the wave and rides it up and down
  const sx = Math.sin(t * 0.45) * 1.4;
  const sz = Math.sin(t * 0.3) * 0.5;
  const sy = waveHeight(sx, sz, t) + 0.08 + Math.sin(t * 2.2) * 0.05;
  surfer.position.set(sx, sy, sz);
  surfer.rotation.z = Math.sin(t * 0.9) * 0.1 - Math.cos(t * 0.45) * 0.08;
  surfer.rotation.x = Math.sin(t * 0.7 + 1) * 0.06;
  surfer.rotation.y = Math.sin(t * 0.45) * -0.25;

  // Pelican balance: squash-and-stretch bob, wings flap gently
  pelican.position.y = 0.62 + Math.sin(t * 2.2) * 0.03;
  pelican.rotation.z = Math.sin(t * 0.9 + 0.5) * 0.07;
  pelican.rotation.x = Math.sin(t * 1.7) * 0.03;

  const flap = Math.sin(t * 3.2) * 0.28;
  const balance = Math.sin(t * 0.9) * 0.18;
  wingL.shoulder.rotation.z = 0.25 + flap + balance;
  wingR.shoulder.rotation.z = -0.25 - flap + balance;
  wingL.shoulder.rotation.x = Math.sin(t * 1.3) * 0.12;
  wingR.shoulder.rotation.x = Math.sin(t * 1.3 + 0.6) * 0.12;
  wingL.tipPivot.rotation.z = 0.3 + Math.sin(t * 3.2 - 0.7) * 0.3;
  wingR.tipPivot.rotation.z = -0.3 - Math.sin(t * 3.2 - 0.7) * 0.3;

  // Head looks into the ride; pouch wobbles with the motion
  headGroup.rotation.y = Math.sin(t * 0.6) * 0.3;
  headGroup.rotation.x = Math.sin(t * 1.8) * 0.08 - 0.05;
  headGroup.position.y = 1.38 + Math.sin(t * 2.2 + 0.8) * 0.04;
  pouch.scale.set(0.75 + Math.sin(t * 4.1) * 0.03, 0.85 + Math.sin(t * 3.4) * 0.05, 1.5);

  // Wake pulses; swell lip shimmers
  foam.scale.set(1 + Math.sin(t * 3) * 0.06, 1.9 + Math.sin(t * 3) * 0.08, 1);
  foamMat.opacity = 0.7 + Math.sin(t * 3) * 0.12;
  swellLipMat.opacity = 0.8 + Math.sin(t * 1.8) * 0.15;

  // Clouds drift and loop
  for (const c of clouds) {
    c.group.position.x += c.speed * 0.016;
    if (c.group.position.x > 16) c.group.position.x = -16;
  }

  updateSpray(t);

  // Slow, automatic camera drift (no user input — the piece is non-interactive)
  camera.position.x = Math.sin(t * 0.18) * 0.5;
  camera.position.y = 3.4 + Math.sin(t * 0.25) * 0.15;
  camera.lookAt(0, 1.1, 0);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
