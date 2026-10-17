import * as THREE from "three";

// Animated, non-interactive surfing pelican. Everything procedural, no assets.

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c5e8);
scene.fog = new THREE.Fog(0x9fd3ec, 30, 90);

const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200);
camera.position.set(0, 4.2, 13.5);
camera.lookAt(0, 1.6, 0);

function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

// Lights
scene.add(new THREE.HemisphereLight(0xcdeaff, 0x2e6f9e, 0.9));
const sun = new THREE.DirectionalLight(0xfff3dd, 2.0);
sun.position.set(-6, 10, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
scene.add(sun);
const rim = new THREE.DirectionalLight(0xffd9b0, 0.6);
rim.position.set(6, 3, -6);
scene.add(rim);

// Sun disc + clouds (procedural sprites from canvas-free geometry)
const sunBall = new THREE.Mesh(
  new THREE.SphereGeometry(1.2, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff6d8, fog: false })
);
sunBall.position.set(-14, 11, -30);
scene.add(sunBall);

const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
const clouds = [];
for (let i = 0; i < 5; i++) {
  const g = new THREE.Group();
  const n = 3 + (i % 3);
  for (let j = 0; j < n; j++) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.7 + Math.random() * 0.7, 10, 10), cloudMat);
    s.position.set(j * 1.1 - n * 0.5, Math.sin(j * 1.7) * 0.25, Math.cos(j) * 0.3);
    s.scale.y = 0.55;
    g.add(s);
  }
  g.position.set(-20 + i * 9 + Math.random() * 3, 8 + Math.random() * 3.5, -22 - Math.random() * 6);
  scene.add(g);
  clouds.push({ g, speed: 0.08 + Math.random() * 0.12 });
}

// Ocean
const oceanGeo = new THREE.PlaneGeometry(120, 70, 110, 48);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1e86c4, roughness: 0.55, metalness: 0.1, flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);
const basePositions = oceanGeo.attributes.position.array.slice();

function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.35 + t * 1.6) * 0.32 +
    Math.sin(z * 0.5 - t * 1.1) * 0.22 +
    Math.sin((x + z) * 0.22 + t * 2.2) * 0.14
  );
}

// Big stylized curling wave face the pelican rides
const curlMat = new THREE.MeshStandardMaterial({
  color: 0x2fa3dd, roughness: 0.5, flatShading: true,
  side: THREE.DoubleSide, transparent: true, opacity: 0.96,
});
const curlGeo = new THREE.CylinderGeometry(4.6, 4.6, 16, 24, 1, true, 0, Math.PI * 1.05);
const curl = new THREE.Mesh(curlGeo, curlMat);
curl.rotation.z = Math.PI / 2;
curl.rotation.y = Math.PI / 2;
curl.position.set(0, 0.4, -4.2);
curl.scale.set(1, 1, 0.9);
scene.add(curl);

// Foam crest on the curl
const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
const foam = new THREE.Group();
for (let i = 0; i < 26; i++) {
  const s = new THREE.Mesh(new THREE.SphereGeometry(0.22 + Math.random() * 0.3, 8, 8), foamMat);
  s.position.set(-7.5 + i * 0.6 + Math.random() * 0.3, 4.35 + Math.random() * 0.5, -4.0 + Math.random() * 0.8);
  s.scale.y = 0.6;
  foam.add(s);
}
scene.add(foam);

// Wake foam blobs trailing the board
const wake = new THREE.Group();
const wakeBlobs = [];
for (let i = 0; i < 22; i++) {
  const s = new THREE.Mesh(new THREE.SphereGeometry(0.12 + Math.random() * 0.22, 8, 8), foamMat);
  wake.add(s);
  wakeBlobs.push({ m: s, seed: Math.random() * 100 });
}
scene.add(wake);

// Spray particles off the wave lip
const sprayGeo = new THREE.BufferGeometry();
const SPRAY_N = 90;
const sprayPos = new Float32Array(SPRAY_N * 3);
const spraySeed = [];
for (let i = 0; i < SPRAY_N; i++) spraySeed.push(Math.random() * 100);
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.16 }));
scene.add(spray);

// ---- Surfboard ----
function makeBoard() {
  const g = new THREE.Group();
  const shape = new THREE.Shape();
  shape.moveTo(0, -2.2);
  shape.bezierCurveTo(0.75, -1.2, 0.75, 1.0, 0, 2.2);
  shape.bezierCurveTo(-0.75, 1.0, -0.75, -1.2, 0, -2.2);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.12, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 2 });
  geo.rotateX(-Math.PI / 2);
  const board = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0xff5d5d, roughness: 0.4 }));
  board.castShadow = true;
  g.add(board);
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(0.28, 0.02, 3.4),
    new THREE.MeshStandardMaterial({ color: 0xfff4e0, roughness: 0.5 })
  );
  stripe.position.y = 0.14;
  g.add(stripe);
  const fin = new THREE.Mesh(
    new THREE.BoxGeometry(0.06, 0.5, 0.4),
    new THREE.MeshStandardMaterial({ color: 0xffe9c4 })
  );
  fin.position.set(0, -0.25, 1.5);
  fin.rotation.x = 0.3;
  g.add(fin);
  return g;
}

// ---- Pelican (low-poly, procedural) ----
function makePelican() {
  const p = new THREE.Group();
  const grey = new THREE.MeshStandardMaterial({ color: 0xe8e4da, roughness: 0.8, flatShading: true });
  const darkGrey = new THREE.MeshStandardMaterial({ color: 0x8a8f96, roughness: 0.8, flatShading: true });
  const orange = new THREE.MeshStandardMaterial({ color: 0xf59b23, roughness: 0.6, flatShading: true });
  const pouchMat = new THREE.MeshStandardMaterial({ color: 0xf2b544, roughness: 0.7, flatShading: true });

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.85, 18, 14), grey);
  body.scale.set(1, 0.95, 1.35);
  body.position.y = 1.05;
  body.castShadow = true;
  p.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 16, 12), grey);
  head.position.set(0, 1.95, -0.55);
  head.castShadow = true;
  p.add(head);

  // crest feathers
  for (let i = 0; i < 3; i++) {
    const f = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.4, 6), darkGrey);
    f.position.set((i - 1) * 0.14, 2.3, -0.4);
    f.rotation.x = -0.5;
    p.add(f);
  }

  // beak (upper) + pouch (lower), pointing forward (-z)
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.13, 1.5, 10), orange);
  beak.rotation.x = -Math.PI / 2 - 0.08;
  beak.position.set(0, 1.9, -1.35);
  p.add(beak);
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.3, 12, 10), pouchMat);
  pouch.scale.set(0.75, 0.9, 1.7);
  pouch.position.set(0, 1.62, -1.05);
  p.add(pouch);

  // eyes
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0x1c1c1c });
  for (const sx of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.055, 8, 8), eyeMat);
    e.position.set(sx * 0.24, 2.02, -0.82);
    p.add(e);
  }

  // wings (pivot at shoulder for flapping)
  const wings = [];
  for (const sx of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.set(sx * 0.7, 1.25, 0.1);
    const w = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.1, 0.85), darkGrey);
    w.position.x = sx * 0.85;
    w.castShadow = true;
    pivot.add(w);
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.08, 0.55), grey);
    tip.position.set(sx * 1.85, 0, 0.1);
    pivot.add(tip);
    p.add(pivot);
    wings.push({ pivot, sx });
  }

  // tail
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.8, 8), darkGrey);
  tail.rotation.x = Math.PI / 2 + 0.35;
  tail.position.set(0, 1.15, 1.25);
  p.add(tail);

  // legs gripping board
  const legMat = new THREE.MeshStandardMaterial({ color: 0xf59b23, roughness: 0.7 });
  for (const sx of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.5, 8), legMat);
    leg.position.set(sx * 0.3, 0.45, 0.15);
    p.add(leg);
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.07, 0.45), legMat);
    foot.position.set(sx * 0.3, 0.22, 0.0);
    p.add(foot);
  }
  return { group: p, wings, head, pouch };
}

const board = makeBoard();
board.rotation.y = Math.PI; // nose faces -z (forward)
const surfer = new THREE.Group();
surfer.add(board);
const pelican = makePelican();
pelican.group.position.y = 0.1;
surfer.add(pelican.group);
scene.add(surfer);

// Seagull silhouettes circling far away
const gulls = [];
const gullMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
for (let i = 0; i < 3; i++) {
  const g = new THREE.Group();
  const wgeo = new THREE.BoxGeometry(0.9, 0.05, 0.18);
  const wl = new THREE.Mesh(wgeo, gullMat);
  wl.position.x = -0.45;
  const wr = new THREE.Mesh(wgeo, gullMat);
  wr.position.x = 0.45;
  const pl = new THREE.Group(), pr = new THREE.Group();
  pl.add(wl); pr.add(wr);
  g.add(pl, pr);
  scene.add(g);
  gulls.push({ g, pl, pr, r: 12 + i * 3, h: 8 + i, ph: i * 2.1, sp: 0.25 + i * 0.05 });
}

// Animation
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Ocean swell
  const pos = oceanGeo.attributes.position;
  const arr = pos.array;
  for (let i = 0; i < arr.length; i += 3) {
    const x = basePositions[i], z = basePositions[i + 2];
    arr[i + 1] = waveHeight(x, z, t);
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // Surfer carves along the wave face
  const sx = Math.sin(t * 0.7) * 3.4;
  const sz = -1.2 + Math.cos(t * 0.45) * 0.7;
  const sy = 1.15 + Math.sin(t * 2.0) * 0.22 + Math.cos(t * 3.1) * 0.08;
  surfer.position.set(sx, sy, sz);
  surfer.rotation.z = Math.cos(t * 0.7) * -0.28;
  surfer.rotation.x = Math.sin(t * 1.3) * 0.1 - 0.06;
  surfer.rotation.y = Math.cos(t * 0.7) * 0.25;

  // Pelican balance: lean, bob, flap
  pelican.group.rotation.z = Math.sin(t * 2.0 + 0.6) * 0.12;
  pelican.group.rotation.x = Math.sin(t * 1.6) * 0.06;
  for (const { pivot, sx: s } of pelican.wings) {
    pivot.rotation.z = s * (0.25 + Math.sin(t * 3.2) * 0.45);
    pivot.rotation.y = s * Math.sin(t * 1.1) * 0.12;
  }
  pelican.head.position.y = 1.95 + Math.sin(t * 2.6) * 0.06;
  pelican.pouch.scale.y = 0.9 + Math.sin(t * 2.6) * 0.08;

  // Foam + curl pulse
  foam.children.forEach((f, i) => {
    f.position.y = 4.35 + Math.sin(t * 3 + i * 1.3) * 0.22;
    f.scale.x = f.scale.z = 1 + Math.sin(t * 4 + i) * 0.15;
  });
  curl.rotation.x = Math.sin(t * 0.9) * 0.05;
  foam.position.x = Math.sin(t * 0.7) * 0.6;

  // Wake follows board
  wakeBlobs.forEach((b, i) => {
    const k = (i / wakeBlobs.length);
    b.m.position.set(
      sx + Math.sin(t * 3 + b.seed) * 0.3 * k + k * 1.2,
      0.35 + Math.sin(t * 4 + b.seed) * 0.1,
      sz + 1.2 + k * 3.2
    );
    const s = (1 - k) * 0.9 + 0.2;
    b.m.scale.set(s, s * 0.4, s);
  });

  // Spray arcs off the lip
  const sp = sprayGeo.attributes.position.array;
  for (let i = 0; i < SPRAY_N; i++) {
    const sd = spraySeed[i];
    const life = ((t * 0.9 + sd) % 1.6) / 1.6;
    sp[i * 3] = sx * 0.4 + Math.sin(sd * 9) * 4 - life * 3;
    sp[i * 3 + 1] = 4.3 + life * 1.6 - life * life * 3.2;
    sp[i * 3 + 2] = -3.6 + Math.cos(sd * 7) * 1.4;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Clouds + gulls drift
  for (const c of clouds) {
    c.g.position.x += c.speed * 0.016;
    if (c.g.position.x > 26) c.g.position.x = -26;
  }
  for (const gu of gulls) {
    const a = t * gu.sp + gu.ph;
    gu.g.position.set(Math.cos(a) * gu.r, gu.h + Math.sin(t * 0.8 + gu.ph) * 0.6, -12 + Math.sin(a) * 4);
    const flap = Math.sin(t * 6 + gu.ph) * 0.5;
    gu.pl.rotation.z = flap; gu.pr.rotation.z = -flap;
  }

  renderer.render(scene, camera);
}
animate();
