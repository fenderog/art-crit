import * as THREE from "three";

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c8e8);
scene.fog = new THREE.Fog(0x9fd0ea, 28, 70);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);
camera.position.set(7.5, 3.6, 9.5);

const sunLight = new THREE.DirectionalLight(0xffdfae, 3);
sunLight.position.set(-6, 9, 4);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10; sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10; sunLight.shadow.camera.bottom = -10;
scene.add(sunLight, new THREE.HemisphereLight(0xbfe6ff, 0x1a5a7a, 1.1));

// --- Materials ---
const mat = (c, r = 0.7, extra = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, ...extra });
const white = mat(0xf7f4ec, 0.85), grey = mat(0xc9d2d6, 0.9), orange = mat(0xf59a2e, 0.55),
  pink = mat(0xf2a18a, 0.8), dark = mat(0x22303a, 0.5), boardMat = mat(0xffcf3f, 0.35);

// --- Ocean ---
const oceanGeo = new THREE.PlaneGeometry(90, 60, 90, 60);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({ color: 0x1483b8, roughness: 0.35, metalness: 0.05, transparent: true, opacity: 0.96 }));
ocean.receiveShadow = true;
scene.add(ocean);

// Curling wave the pelican rides (a bent sheet, animated)
function makeWave() {
  const g = new THREE.PlaneGeometry(16, 4.6, 48, 16);
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x1a9ec7, roughness: 0.3, side: THREE.DoubleSide, transparent: true, opacity: 0.97 }));
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
const wave = makeWave();
wave.position.set(0, 0.2, -1.2);
scene.add(wave);
const waveBase = wave.geometry.attributes.position.array.slice();

// Foam crest
const foam = new THREE.Mesh(new THREE.TorusGeometry(3.4, 0.28, 10, 40, Math.PI * 0.9),
  new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 }));
foam.rotation.set(0.4, 0, 2.4); foam.position.set(-3.2, 2.4, -1.4);
scene.add(foam);

// --- Surfboard ---
const rider = new THREE.Group(); // board + pelican, surfs together
scene.add(rider);
const board = new THREE.Group();
{
  const shape = new THREE.Shape();
  shape.moveTo(0, -2.2); shape.bezierCurveTo(0.55, -1.6, 0.55, 1.2, 0, 2.3);
  shape.bezierCurveTo(-0.55, 1.2, -0.55, -1.6, 0, -2.2);
  const g = new THREE.ExtrudeGeometry(shape, { depth: 0.12, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.05 });
  g.rotateX(-Math.PI / 2);
  const b = new THREE.Mesh(g, boardMat); b.castShadow = true; board.add(b);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.03, 3.6), mat(0xe94f37, 0.4));
  stripe.position.y = 0.13; board.add(stripe);
}
board.rotation.y = -0.35;
rider.add(board);

// --- Pelican (built from primitives, standing on board) ---
const pelican = new THREE.Group();
pelican.position.y = 0.18;
rider.add(pelican);
const add = (parent, geo, material, x, y, z, sx = 1, sy = 1, sz = 1) => {
  const m = new THREE.Mesh(geo, material); m.position.set(x, y, z); m.scale.set(sx, sy, sz);
  m.castShadow = true; parent.add(m); return m;
};
const sph = new THREE.SphereGeometry(1, 28, 22);

// Body, tail, neck, head
add(pelican, sph, white, 0, 1.05, 0, 0.78, 0.66, 1.05);
const tail = add(pelican, new THREE.ConeGeometry(0.42, 1.1, 14), grey, 0, 1.25, -1.15);
tail.rotation.x = -1.9;
const neck = new THREE.Group(); neck.position.set(0, 1.35, 0.75); pelican.add(neck);
add(neck, sph, white, 0, 0.35, 0.12, 0.30, 0.52, 0.30);
const head = new THREE.Group(); head.position.set(0, 0.78, 0.28); neck.add(head);
add(head, sph, white, 0, 0, 0, 0.34, 0.30, 0.36);
add(head, sph, mat(0xffe9a8, 0.9), 0, 0.18, -0.05, 0.30, 0.14, 0.30); // crown
for (const s of [-1, 1]) {
  const eye = add(head, sph, dark, s * 0.20, 0.07, 0.26, 0.055, 0.055, 0.055);
  eye.castShadow = false;
  add(head, sph, mat(0xffffff, 0.3), s * 0.22, 0.10, 0.30, 0.02, 0.02, 0.02);
}
// Long beak + pouch
const beak = new THREE.Group(); beak.position.set(0, -0.04, 0.30); head.add(beak);
const upper = add(beak, new THREE.ConeGeometry(0.13, 1.55, 12), orange, 0, 0.02, 0.75);
upper.rotation.x = Math.PI / 2; upper.scale.z = 0.55;
const pouch = add(beak, sph, pink, 0, -0.16, 0.62, 0.16, 0.18, 0.62);
const lower = add(beak, new THREE.ConeGeometry(0.09, 1.35, 10), orange, 0, -0.05, 0.65);
lower.rotation.x = Math.PI / 2;

// Wings (pivot at shoulder for flapping)
function wing(side) {
  const w = new THREE.Group(); w.position.set(side * 0.62, 1.35, -0.1); pelican.add(w);
  const inner = add(w, sph, white, side * 0.55, 0, -0.1, 0.62, 0.13, 0.42);
  inner.rotation.z = side * 0.15;
  const tip = add(w, sph, grey, side * 1.25, -0.05, -0.35, 0.55, 0.09, 0.34);
  tip.rotation.y = side * -0.35;
  add(w, sph, dark, side * 1.62, -0.06, -0.55, 0.28, 0.07, 0.22);
  return w;
}
const wingL = wing(-1), wingR = wing(1);

// Legs + webbed feet on the board
for (const s of [-1, 1]) {
  add(pelican, new THREE.CylinderGeometry(0.055, 0.055, 0.55, 8), orange, s * 0.28, 0.28, 0.1);
  const foot = add(pelican, sph, orange, s * 0.28, 0.04, 0.22, 0.16, 0.04, 0.28);
  foot.castShadow = true;
}

// --- Scenery: sun, clouds, distant island, spray ---
const sun = add(scene, sph, new THREE.MeshBasicMaterial({ color: 0xffd98a }), -14, 7, -22, 1.8, 1.8, 1.8);
sun.castShadow = false;
const clouds = new THREE.Group(); scene.add(clouds);
for (let i = 0; i < 6; i++) {
  const c = new THREE.Group();
  for (let j = 0; j < 4; j++) add(c, sph, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 }), j * 0.7 - 1, Math.sin(j) * 0.15, 0, 0.65, 0.4, 0.5).castShadow = false;
  c.position.set(-18 + i * 7 + (i % 2) * 2, 6.5 + (i % 3), -16 - (i % 2) * 5);
  clouds.add(c);
}
const island = new THREE.Group(); island.position.set(13, 0, -20); scene.add(island);
add(island, new THREE.ConeGeometry(4, 1.6, 24), mat(0x2e9e6b, 1), 0, 0.6, 0);
for (let i = 0; i < 3; i++) {
  add(island, new THREE.CylinderGeometry(0.09, 0.13, 1.8, 6), mat(0x7a5230, 1), -1.4 + i * 1.3, 1.8, (i % 2) - 0.4);
  add(island, new THREE.ConeGeometry(0.8, 0.7, 8), mat(0x1f8a4d, 1), -1.4 + i * 1.3, 2.8, (i % 2) - 0.4);
}
// Spray particles behind the board
const sprayGeo = new THREE.BufferGeometry();
const N = 220, sprayPos = new Float32Array(N * 3), sprayVel = [];
for (let i = 0; i < N; i++) { sprayPos.set([(Math.random() - .5), Math.random() * .4, -1 - Math.random() * 2], i * 3); sprayVel.push({ x: (Math.random() - .5) * .6, y: 1 + Math.random() * 1.6, z: -1 - Math.random() }); }
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.14, transparent: true, opacity: 0.85 }));
rider.add(spray);
// A few gulls
const gulls = new THREE.Group(); scene.add(gulls);
for (let i = 0; i < 4; i++) {
  const g = new THREE.Group();
  for (const s of [-1, 1]) { const w = add(g, sph, white, s * 0.35, 0, 0, 0.38, 0.05, 0.14); w.rotation.z = s * 0.5; }
  g.position.set(-8 + i * 4, 5 + i % 2, -9 - i); g.userData.phase = i * 1.7; gulls.add(g);
}

// --- Animation (fully automatic, no interaction) ---
const clock = new THREE.Clock();
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener("resize", resize); resize();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime() * (reduced ? 0.25 : 1);

  // Ocean swell
  const p = ocean.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    p.setY(i, Math.sin(x * 0.35 + t * 1.4) * 0.22 + Math.cos(z * 0.4 + t) * 0.18);
  }
  p.needsUpdate = true; ocean.geometry.computeVertexNormals();

  // Curling wave face
  const wp = wave.geometry.attributes.position;
  for (let i = 0; i < wp.count; i++) {
    const x = waveBase[i * 3], y = waveBase[i * 3 + 1];
    const curl = Math.max(0, y - 0.8) * 0.55;
    wp.setZ(i, Math.sin(x * 0.5 + t * 1.6) * 0.25 - curl * curl + Math.sin(t * 2 + x) * 0.08);
    wp.setY(i, y + Math.sin(x * 0.6 + t * 1.6) * 0.12);
  }
  wp.needsUpdate = true; wave.geometry.computeVertexNormals();
  foam.position.y = 2.4 + Math.sin(t * 1.6) * 0.12;
  foam.rotation.z = 2.4 + Math.sin(t * 0.8) * 0.05;

  // Rider carves back and forth, bobbing and banking
  rider.position.set(Math.sin(t * 0.55) * 2.2, 1.55 + Math.sin(t * 1.6) * 0.28, Math.sin(t * 0.35) * 0.6);
  rider.rotation.set(Math.sin(t * 1.6) * 0.06 - 0.04, -0.2 + Math.sin(t * 0.55) * 0.18, Math.cos(t * 0.55) * 0.16);
  board.rotation.z = Math.sin(t * 1.6 + 0.5) * 0.05;

  // Pelican: balance, flap, head-bob, pouch sway
  pelican.rotation.z = Math.sin(t * 1.3) * 0.07;
  pelican.position.y = 0.18 + Math.abs(Math.sin(t * 2.2)) * 0.05;
  const flap = Math.sin(t * 2.2) * 0.55 - 0.15;
  wingL.rotation.z = flap; wingR.rotation.z = -flap;
  wingL.rotation.y = Math.sin(t * 2.2 + 0.4) * 0.12; wingR.rotation.y = -wingL.rotation.y;
  neck.rotation.x = Math.sin(t * 1.8) * 0.10;
  head.rotation.set(Math.sin(t * 2.4) * 0.08, Math.sin(t * 0.7) * 0.35, Math.sin(t * 1.8) * 0.05);
  beak.rotation.x = Math.sin(t * 2.0) * 0.06;
  pouch.scale.y = 0.18 + Math.sin(t * 2.0) * 0.03;
  tail.rotation.z = Math.sin(t * 1.6) * 0.12;

  // Spray recycles upward behind board
  const sp = spray.geometry.attributes.position;
  for (let i = 0; i < N; i++) {
    let y = sp.getY(i) + sprayVel[i].y * 0.016, x = sp.getX(i) + sprayVel[i].x * 0.016, z = sp.getZ(i) + sprayVel[i].z * 0.016;
    if (y > 1.6) { x = (Math.random() - .5) * .8; y = 0.05; z = -1.4 - Math.random(); }
    sp.setXYZ(i, x, y, z);
  }
  sp.needsUpdate = true;

  clouds.children.forEach((c, i) => { c.position.x += 0.0035 * (1 + i % 3); if (c.position.x > 24) c.position.x = -24; });
  gulls.children.forEach(g => {
    g.position.x += 0.02; g.position.y += Math.sin(t * 3 + g.userData.phase) * 0.008;
    g.children.forEach((w, j) => w.rotation.z = (j ? -1 : 1) * (0.5 + Math.sin(t * 6 + g.userData.phase) * 0.45));
    if (g.position.x > 16) g.position.x = -16;
  });

  // Slow cinematic camera drift (non-interactive)
  camera.position.set(7.5 + Math.sin(t * 0.18) * 1.6, 3.6 + Math.sin(t * 0.3) * 0.5, 9.5 + Math.cos(t * 0.15) * 1.2);
  camera.lookAt(rider.position.x * 0.6, 1.8, 0);
  renderer.render(scene, camera);
}
animate();
