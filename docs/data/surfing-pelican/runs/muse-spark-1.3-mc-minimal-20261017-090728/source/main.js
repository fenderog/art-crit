import * as THREE from "three";

// Non-interactive animated scene: a low-poly pelican surfing a stylized wave.

const container = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c5e8);
scene.fog = new THREE.Fog(0x87c5e8, 30, 90);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 4.2, 13);
camera.lookAt(0, 1.6, 0);

scene.add(new THREE.HemisphereLight(0xcfeaff, 0x1a5f8a, 1.1));
const sun = new THREE.DirectionalLight(0xfff2cc, 2.0);
sun.position.set(6, 10, 6);
scene.add(sun);

// Sun disc + clouds (generated in code, no assets)
const sunBall = new THREE.Mesh(
  new THREE.SphereGeometry(1.4, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff3b0 })
);
sunBall.position.set(-10, 11, -30);
scene.add(sunBall);

function cloud(x, y, z, s) {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.92 });
  [[0, 0, 0, 1.4], [1.5, -0.2, 0, 1.0], [-1.5, -0.25, 0, 1.05], [0.4, 0.7, 0, 0.9]].forEach(([cx, cy, cz, r]) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 16), mat);
    m.position.set(cx, cy, cz);
    g.add(m);
  });
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  scene.add(g);
  return g;
}
const clouds = [cloud(-9, 8, -22, 1.2), cloud(4, 9.5, -26, 1.5), cloud(11, 7, -20, 0.9)];

// Ocean: plane with vertex waves animated per-frame
const oceanGeo = new THREE.PlaneGeometry(120, 60, 90, 40);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshPhongMaterial({ color: 0x1e86c4, shininess: 90, specular: 0x99ddff });
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.position.y = 0;
scene.add(ocean);
const oceanBase = oceanGeo.attributes.position.array.slice();

// Big curling wave face the pelican rides on
const waveGeo = new THREE.PlaneGeometry(26, 6, 60, 12);
const waveMat = new THREE.MeshPhongMaterial({
  color: 0x2aa5dd, shininess: 80, specular: 0xbfeaff,
  side: THREE.DoubleSide, transparent: true, opacity: 0.96
});
const wave = new THREE.Mesh(waveGeo, waveMat);
wave.position.set(0, 1.8, -4);
wave.rotation.x = -0.25;
scene.add(wave);
const waveBase = waveGeo.attributes.position.array.slice();

// Foam strip along the wave crest
const foamGeo = new THREE.PlaneGeometry(26, 1.2, 60, 4);
const foamMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85, side: THREE.DoubleSide });
const foam = new THREE.Mesh(foamGeo, foamMat);
foam.position.set(0, 4.4, -4.6);
foam.rotation.x = -0.35;
scene.add(foam);
const foamBase = foamGeo.attributes.position.array.slice();

// Surfboard
const board = new THREE.Group();
const deckMat = new THREE.MeshPhongMaterial({ color: 0xff6f61, shininess: 60 });
const deck = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), deckMat);
deck.scale.set(0.55, 0.12, 2.2);
board.add(deck);
const stripe = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), new THREE.MeshPhongMaterial({ color: 0xfff6e8 }));
stripe.scale.set(0.2, 0.13, 2.0);
stripe.position.y = 0.01;
board.add(stripe);
scene.add(board);

// --- Pelican built from primitives ---
const pelican = new THREE.Group();
const white = new THREE.MeshPhongMaterial({ color: 0xf7f4ec, shininess: 30 });
const grey = new THREE.MeshPhongMaterial({ color: 0x9aa3a8, shininess: 30 });
const orange = new THREE.MeshPhongMaterial({ color: 0xf2a03d, shininess: 40 });
const dark = new THREE.MeshBasicMaterial({ color: 0x222222 });

const body = new THREE.Mesh(new THREE.SphereGeometry(0.9, 24, 18), white);
body.scale.set(0.85, 1.0, 1.25);
pelican.add(body);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.45, 20, 16), white);
head.position.set(0, 1.05, 0.55);
pelican.add(head);

// Crest feathers
for (let i = 0; i < 3; i++) {
  const f = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.4, 8), grey);
  f.position.set((i - 1) * 0.16, 1.45, 0.35);
  f.rotation.x = -0.5;
  pelican.add(f);
}

// Eyes
for (const s of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 10), dark);
  eye.position.set(s * 0.22, 1.15, 0.9);
  pelican.add(eye);
}

// Long beak + pouch
const beak = new THREE.Mesh(new THREE.ConeGeometry(0.16, 1.5, 12), orange);
beak.rotation.x = Math.PI / 2 + 0.12;
beak.position.set(0, 0.98, 1.6);
pelican.add(beak);
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.28, 14, 12), new THREE.MeshPhongMaterial({ color: 0xe8833a }));
pouch.scale.set(0.8, 0.55, 1.6);
pouch.position.set(0, 0.72, 1.35);
pelican.add(pouch);

// Wings (pivot at shoulder so they can flap)
function makeWing(side) {
  const pivot = new THREE.Group();
  const w = new THREE.Mesh(new THREE.SphereGeometry(0.7, 16, 12), grey);
  w.scale.set(1.3, 0.18, 0.7);
  w.position.x = side * 0.9;
  pivot.add(w);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.9, 8), grey);
  tip.rotation.z = side * Math.PI / 2;
  tip.position.x = side * 1.9;
  pivot.add(tip);
  pivot.position.set(side * 0.5, 0.35, -0.1);
  pelican.add(pivot);
  return pivot;
}
const wingL = makeWing(-1);
const wingR = makeWing(1);

// Tail
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.8, 8), grey);
tail.rotation.x = -Math.PI / 2 - 0.3;
tail.position.set(0, 0.25, -1.25);
pelican.add(tail);

// Legs + feet planted on the board
for (const s of [-1, 1]) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.5, 8), orange);
  leg.position.set(s * 0.3, -0.95, 0.1);
  pelican.add(leg);
  const foot = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8), orange);
  foot.scale.set(1, 0.4, 1.6);
  foot.position.set(s * 0.3, -1.2, 0.25);
  pelican.add(foot);
}
pelican.position.y = 2.6;
scene.add(pelican);

// Spray particles at the board tail
const SPRAY = 120;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = [];
function resetDrop(i, randomAge) {
  sprayPos[i * 3] = -0.2 + Math.random() * 0.4;
  sprayPos[i * 3 + 1] = 1.2;
  sprayPos[i * 3 + 2] = -1.6 + Math.random() * 0.5;
  sprayVel[i] = { x: (Math.random() - 0.5) * 2, y: 2 + Math.random() * 3, z: -2 - Math.random() * 3, age: randomAge ? Math.random() : 0 };
}
for (let i = 0; i < SPRAY; i++) resetDrop(i, true);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.12, transparent: true, opacity: 0.9 }));
scene.add(spray);

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Ocean swell
  const op = oceanGeo.attributes.position;
  for (let i = 0; i < op.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    op.array[i * 3 + 1] = Math.sin(x * 0.35 + t * 1.4) * 0.35 + Math.cos(z * 0.5 + t) * 0.25;
  }
  op.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // Curling wave face ripple
  const wp = waveGeo.attributes.position;
  for (let i = 0; i < wp.count; i++) {
    const x = waveBase[i * 3];
    wp.array[i * 3 + 2] = Math.sin(x * 0.8 + t * 2.2) * 0.5;
  }
  wp.needsUpdate = true;

  // Foam shimmer
  const fp = foamGeo.attributes.position;
  for (let i = 0; i < fp.count; i++) {
    const x = foamBase[i * 3];
    fp.array[i * 3 + 2] = Math.sin(x * 1.2 + t * 3.0) * 0.3;
  }
  fp.needsUpdate = true;

  // Surfing motion: glide, bob, carve
  const bobY = Math.sin(t * 2.0) * 0.25;
  const carveX = Math.sin(t * 0.7) * 2.2;
  board.position.set(carveX, 1.35 + bobY, 0.6);
  board.rotation.z = Math.cos(t * 0.7) * -0.25;
  board.rotation.x = Math.sin(t * 2.0 + 0.5) * 0.08;

  pelican.position.set(carveX, 2.6 + bobY * 1.15, 0.45);
  pelican.rotation.z = Math.cos(t * 0.7) * -0.18;
  pelican.rotation.y = Math.sin(t * 0.5) * 0.25;
  pelican.rotation.x = Math.sin(t * 2.0) * 0.05;

  // Wing flap + head bob
  const flap = Math.sin(t * 6.0) * 0.45;
  wingL.rotation.z = 0.35 + flap;
  wingR.rotation.z = -0.35 - flap;
  head.position.y = 1.05 + Math.sin(t * 3.0) * 0.06;
  beak.rotation.x = Math.PI / 2 + 0.12 + Math.sin(t * 3.0) * 0.04;

  // Clouds drift
  for (const c of clouds) {
    c.position.x += 0.004;
    if (c.position.x > 16) c.position.x = -16;
  }

  // Spray follows the board
  const sp = sprayGeo.attributes.position;
  for (let i = 0; i < SPRAY; i++) {
    const v = sprayVel[i];
    v.age += 0.016;
    if (v.age > 1.1) { resetDrop(i, false); continue; }
    sp.array[i * 3] += v.x * 0.016;
    sp.array[i * 3 + 1] += v.y * 0.016;
    sp.array[i * 3 + 2] += v.z * 0.016;
    v.y -= 6 * 0.016;
    sp.array[i * 3] += carveX * 0.0; // board-relative handled below
  }
  spray.position.x = carveX;
  spray.position.y = bobY;
  sp.needsUpdate = true;

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
