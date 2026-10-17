import * as THREE from "three";

// ---------- Renderer / Scene / Camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 30, 90);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(6, 3.2, 9);
camera.lookAt(0, 1.5, 0);

// ---------- Lights ----------
const sun = new THREE.DirectionalLight(0xfff3d6, 2.2);
sun.position.set(10, 14, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -15;
sun.shadow.camera.right = 15;
sun.shadow.camera.top = 15;
sun.shadow.camera.bottom = -15;
scene.add(sun);
scene.add(new THREE.AmbientLight(0xbfd9e8, 0.9));
const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x0a5f7a, 0.5);
scene.add(hemi);

// ---------- Ocean ----------
const oceanGeo = new THREE.PlaneGeometry(200, 200, 128, 128);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshPhongMaterial({
  color: 0x1b7f9e,
  shininess: 120,
  specular: 0x99ddff,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = oceanPos.array.slice();

function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.25 + t * 1.2) * 0.45 +
    Math.sin(z * 0.18 - t * 0.9) * 0.35 +
    Math.sin((x + z) * 0.12 + t * 0.6) * 0.5
  );
}

// ---------- Wave crest (the big wave the pelican rides) ----------
const crestGeo = new THREE.PlaneGeometry(40, 14, 80, 24);
crestGeo.rotateX(-Math.PI / 2);
const crestMat = new THREE.MeshPhongMaterial({
  color: 0x2fa8c9,
  shininess: 90,
  specular: 0xaaeeff,
  flatShading: true,
});
const crest = new THREE.Mesh(crestGeo, crestMat);
crest.receiveShadow = true;
scene.add(crest);
const crestPos = crestGeo.attributes.position;
const crestBase = crestPos.array.slice();

function crestHeight(x, z, t) {
  // Big rolling swell along z with a curl
  const swell = Math.sin(z * 0.45 - t * 1.5) * 1.6;
  const chop = Math.sin(x * 0.6 + t * 2.0) * 0.18;
  return swell + chop;
}

// ---------- Foam particles at wave lip ----------
const foamCount = 300;
const foamGeo = new THREE.BufferGeometry();
const foamPositions = new Float32Array(foamCount * 3);
const foamSeeds = new Float32Array(foamCount);
for (let i = 0; i < foamCount; i++) foamSeeds[i] = Math.random();
foamGeo.setAttribute("position", new THREE.BufferAttribute(foamPositions, 3));
const foam = new THREE.Points(
  foamGeo,
  new THREE.PointsMaterial({ color: 0xffffff, size: 0.16, transparent: true, opacity: 0.85 })
);
scene.add(foam);

// ---------- Surfboard ----------
function makeBoard() {
  const shape = new THREE.Shape();
  shape.moveTo(0, -1.8);
  shape.quadraticCurveTo(0.55, -1.2, 0.55, 0);
  shape.quadraticCurveTo(0.55, 1.4, 0, 1.9);
  shape.quadraticCurveTo(-0.55, 1.4, -0.55, 0);
  shape.quadraticCurveTo(-0.55, -1.2, 0, -1.8);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.1, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.05 });
  const board = new THREE.Group();
  const mat = new THREE.MeshPhongMaterial({ color: 0xff8c42, shininess: 80 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.rotation.x = -Math.PI / 2;
  board.add(mesh);
  // stripe
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(0.16, 0.03, 3.2),
    new THREE.MeshPhongMaterial({ color: 0xfff4e0 })
  );
  stripe.position.y = 0.1;
  board.add(stripe);
  return board;
}

// ---------- Pelican (built from primitives) ----------
const featherMat = new THREE.MeshPhongMaterial({ color: 0xf2ede2, shininess: 30, flatShading: true });
const darkMat = new THREE.MeshPhongMaterial({ color: 0x3a3430, shininess: 20, flatShading: true });
const beakMat = new THREE.MeshPhongMaterial({ color: 0xf4a83c, shininess: 40, flatShading: true });
const pouchMat = new THREE.MeshPhongMaterial({ color: 0xe8b57a, shininess: 25, flatShading: true });

function makeWing() {
  const wing = new THREE.Group();
  const inner = new THREE.Mesh(new THREE.SphereGeometry(0.5, 8, 6), featherMat);
  inner.scale.set(0.9, 0.25, 0.5);
  inner.castShadow = true;
  wing.add(inner);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.9, 6), darkMat);
  tip.rotation.z = -Math.PI / 2 - 0.35;
  tip.position.set(0.85, 0.12, 0);
  tip.scale.z = 0.5;
  tip.castShadow = true;
  wing.add(tip);
  return wing;
}

function makePelican() {
  const p = new THREE.Group();

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), featherMat);
  body.scale.set(1, 0.85, 1.35);
  body.castShadow = true;
  p.add(body);

  // neck
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.7, 8), featherMat);
  neck.position.set(0, 0.55, 0.55);
  neck.rotation.x = 0.35;
  neck.castShadow = true;
  p.add(neck);

  // head group (for subtle head bob)
  const head = new THREE.Group();
  head.position.set(0, 0.95, 0.72);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.26, 10, 8), featherMat);
  skull.castShadow = true;
  head.add(skull);
  // crest tuft
  const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.3, 6), darkMat);
  tuft.position.set(0, 0.2, -0.14);
  tuft.rotation.x = -0.7;
  head.add(tuft);
  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.045, 6, 6);
  const eyeL = new THREE.Mesh(eyeGeo, darkMat);
  eyeL.position.set(0.14, 0.06, 0.17);
  const eyeR = eyeL.clone();
  eyeR.position.x = -0.14;
  head.add(eyeL, eyeR);
  // long beak + pouch
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.1, 1.15, 8), beakMat);
  beak.rotation.x = Math.PI / 2 - 0.12;
  beak.position.set(0, -0.02, 0.62);
  beak.scale.set(0.8, 1, 0.5);
  beak.castShadow = true;
  head.add(beak);
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), pouchMat);
  pouch.scale.set(0.8, 0.9, 1.9);
  pouch.position.set(0, -0.14, 0.5);
  head.add(pouch);
  p.add(head);

  // wings (pivot at shoulder)
  const wingL = makeWing();
  wingL.position.set(0.4, 0.15, 0);
  const wingR = makeWing();
  wingR.position.set(-0.4, 0.15, 0);
  wingR.scale.x = -1;
  p.add(wingL, wingR);

  // tail
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.6, 6), darkMat);
  tail.rotation.x = Math.PI / 2 + 0.5;
  tail.position.set(0, 0.05, -0.85);
  tail.scale.z = 0.4;
  p.add(tail);

  // legs
  const legGeo = new THREE.CylinderGeometry(0.045, 0.045, 0.5, 6);
  const footGeo = new THREE.BoxGeometry(0.16, 0.04, 0.28);
  for (const s of [1, -1]) {
    const leg = new THREE.Mesh(legGeo, beakMat);
    leg.position.set(0.2 * s, -0.6, 0.1);
    leg.rotation.z = -0.25 * s;
    const foot = new THREE.Mesh(footGeo, beakMat);
    foot.position.set(0.26 * s, -0.85, 0.15);
    p.add(leg, foot);
  }

  return { group: p, wingL, wingR, head };
}

// ---------- Surfer rig ----------
const rider = new THREE.Group();
const board = makeBoard();
const pelican = makePelican();
pelican.group.position.set(0, 1.0, -0.1);
pelican.group.rotation.y = Math.PI; // face forward (-z travel direction looks better)
pelican.group.rotation.x = -0.12;   // surfing lean
rider.add(board, pelican.group);
scene.add(rider);

// ---------- Clouds ----------
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const m = new THREE.MeshPhongMaterial({ color: 0xffffff, flatShading: true });
  for (let i = 0; i < 4; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.8 - i * 0.1, 8, 6), m);
    b.position.set(i * 0.9 - 1.2, Math.sin(i * 2) * 0.2, Math.cos(i * 3) * 0.3);
    g.add(b);
  }
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  scene.add(g);
  return g;
}
const clouds = [
  makeCloud(-14, 9, -18, 1.4),
  makeCloud(10, 11, -25, 1.8),
  makeCloud(2, 8, -14, 1.0),
  makeCloud(-6, 12, -30, 2.2),
];

// ---------- Sun disc ----------
const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(2.2, 32),
  new THREE.MeshBasicMaterial({ color: 0xfff2b0, fog: false })
);
sunDisc.position.set(18, 16, -45);
sunDisc.lookAt(camera.position);
scene.add(sunDisc);

// ---------- Animation ----------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // ocean waves
  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    oceanPos.array[i * 3 + 1] = waveHeight(x, z, t) * 0.5 - 1.2;
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // crest wave
  for (let i = 0; i < crestPos.count; i++) {
    const x = crestBase[i * 3];
    const z = crestBase[i * 3 + 2];
    crestPos.array[i * 3 + 1] = crestHeight(x, z, t);
  }
  crestPos.needsUpdate = true;
  crestGeo.computeVertexNormals();

  // rider follows the crest surface
  const rx = Math.sin(t * 0.35) * 3.0; // carve along the wave
  const rz = 0;
  const h = crestHeight(rx, rz, t);
  rider.position.set(rx, h + 0.12, rz);
  rider.rotation.z = -Math.cos(t * 0.35) * 0.35;      // lean into carves
  rider.rotation.x = Math.cos(rz * 0.45 - t * 1.5) * 0.28; // pitch with swell slope
  rider.rotation.y = Math.sin(t * 0.35) * 0.4;

  // pelican wing flap + balance wobble
  const flap = Math.sin(t * 3.2) * 0.55 + 0.25;
  pelican.wingL.rotation.z = flap;
  pelican.wingR.rotation.z = -flap;
  pelican.head.rotation.x = Math.sin(t * 2.1) * 0.12;
  pelican.head.rotation.y = Math.sin(t * 0.7) * 0.3;
  pelican.group.rotation.z = Math.sin(t * 1.6) * 0.08;

  // foam at wave lip
  for (let i = 0; i < foamCount; i++) {
    const s = foamSeeds[i];
    const fx = (s - 0.5) * 38;
    const phase = (t * 0.8 + s * 10) % 6;
    foamPositions[i * 3] = fx + Math.sin(t + s * 20) * 0.4;
    foamPositions[i * 3 + 1] = crestHeight(fx, -3, t) + 0.3 + Math.max(0, 1.5 - phase) * (s * 0.8);
    foamPositions[i * 3 + 2] = -3.4 + phase * 0.6;
  }
  foamGeo.attributes.position.needsUpdate = true;

  // clouds drift
  clouds.forEach((c, i) => {
    c.position.x += 0.008 + i * 0.002;
    if (c.position.x > 35) c.position.x = -35;
  });

  // gentle camera sway
  camera.position.x = 6 + Math.sin(t * 0.2) * 0.6;
  camera.position.y = 3.2 + Math.sin(t * 0.3) * 0.25;
  camera.lookAt(rider.position.x * 0.5, 1.6, 0);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
