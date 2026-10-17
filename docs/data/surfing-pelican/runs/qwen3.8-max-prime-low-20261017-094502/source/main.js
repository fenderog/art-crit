import * as THREE from "three";

// ---------- Renderer / Scene / Camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.getElementById("scene").appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0xa8d8e8, 40, 120);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 300);

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xbfe3ff, 0x2a6f8e, 0.9));
const sun = new THREE.DirectionalLight(0xfff2d8, 1.6);
sun.position.set(-20, 30, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -30;
sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30;
sun.shadow.camera.bottom = -30;
scene.add(sun);

// ---------- Sun disc ----------
const sunDisc = new THREE.Mesh(
  new THREE.SphereGeometry(3, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff4c2 })
);
sunDisc.position.copy(sun.position).multiplyScalar(2.5);
scene.add(sunDisc);

// ---------- Clouds ----------
const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
const clouds = new THREE.Group();
for (let i = 0; i < 8; i++) {
  const cloud = new THREE.Group();
  const n = 3 + Math.floor(Math.random() * 3);
  for (let j = 0; j < n; j++) {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(1.2 + Math.random() * 1.5, 8, 8), cloudMat);
    puff.position.set(j * 1.8 - n * 0.9, Math.random() * 0.6, Math.random() * 0.8);
    puff.scale.y = 0.6;
    cloud.add(puff);
  }
  cloud.position.set((Math.random() - 0.5) * 160, 22 + Math.random() * 12, -60 - Math.random() * 50);
  clouds.add(cloud);
}
scene.add(clouds);

// ---------- Ocean ----------
const OCEAN_SIZE = 240;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, 96, 96);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshPhongMaterial({
  color: 0x1a6f9e,
  shininess: 90,
  specular: 0x88ccee,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = Float32Array.from(oceanPos.array);

function waveHeight(x, z, t) {
  // A primary traveling swell the pelican rides, plus ripples
  const swell = Math.sin(x * 0.35 + t * 1.6) * 0.9;
  return (
    swell +
    Math.sin(z * 0.28 - t * 1.1) * 0.5 +
    Math.sin((x + z) * 0.6 + t * 2.4) * 0.18 +
    Math.sin(x * 1.1 - t * 3.0) * 0.07
  );
}

function updateOcean(t) {
  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    oceanPos.setY(i, waveHeight(x, z, t));
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------- Surfboard ----------
const surfer = new THREE.Group(); // rides the wave
scene.add(surfer);

const boardGroup = new THREE.Group();
surfer.add(boardGroup);

function makeBoard() {
  const shape = new THREE.Shape();
  const L = 4.4, W = 0.85;
  shape.moveTo(-L / 2, 0);
  shape.bezierCurveTo(-L / 2 + 0.6, W, L / 2 - 1.0, W, L / 2, 0.05);
  shape.bezierCurveTo(L / 2 - 1.0, -W, -L / 2 + 0.6, -W, -L / 2, 0);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.18, bevelEnabled: true, bevelSize: 0.09, bevelThickness: 0.09, bevelSegments: 3, curveSegments: 24 });
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, 0.09, 0);
  const board = new THREE.Mesh(geo, new THREE.MeshPhongMaterial({ color: 0xffd23f, shininess: 60 }));
  board.castShadow = true;

  // stripe
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(L * 0.86, 0.02, 0.22),
    new THREE.MeshPhongMaterial({ color: 0xe8443a })
  );
  stripe.position.y = 0.29;
  board.add(stripe);

  // fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.6, 0);
  finShape.lineTo(0.35, -0.55);
  finShape.lineTo(0, 0);
  const fin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(finShape, { depth: 0.06, bevelEnabled: false }),
    new THREE.MeshPhongMaterial({ color: 0xe8443a })
  );
  fin.position.set(-L / 2 + 0.35, 0.02, -0.03);
  board.add(fin);
  return board;
}
boardGroup.add(makeBoard());

// ---------- Pelican ----------
const pelican = new THREE.Group();
boardGroup.add(pelican);

const feather = new THREE.MeshPhongMaterial({ color: 0xf5f2ea, shininess: 20 });
const featherShade = new THREE.MeshPhongMaterial({ color: 0xd8d2c4, shininess: 10 });
const beakMat = new THREE.MeshPhongMaterial({ color: 0xf6a623, shininess: 50 });
const pouchMat = new THREE.MeshPhongMaterial({ color: 0xf9c74f, shininess: 20 });
const darkMat = new THREE.MeshPhongMaterial({ color: 0x222222 });

function addMesh(parent, geo, mat, x, y, z) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true;
  parent.add(m);
  return m;
}

// Body — an egg leaning forward
const body = addMesh(pelican, new THREE.SphereGeometry(0.85, 20, 16), feather, 0, 1.25, -0.1);
body.scale.set(1, 0.9, 1.45);
body.rotation.x = -0.25;

// Tail feathers
const tail = addMesh(pelican, new THREE.ConeGeometry(0.35, 0.9, 8), featherShade, 0, 1.15, -1.45);
tail.rotation.x = Math.PI / 2 + 0.35;
tail.scale.set(1, 1, 0.5);

// Neck
const neck = addMesh(pelican, new THREE.CylinderGeometry(0.26, 0.34, 0.9, 12), feather, 0, 1.9, 0.55);
neck.rotation.x = 0.5;

// Head group
const head = new THREE.Group();
head.position.set(0, 2.35, 0.85);
pelican.add(head);
addMesh(head, new THREE.SphereGeometry(0.36, 16, 14), feather, 0, 0, 0);

// Eyes
for (const s of [-1, 1]) {
  const eye = addMesh(head, new THREE.SphereGeometry(0.07, 8, 8), darkMat, 0.16 * s, 0.12, 0.28);
  const glint = addMesh(head, new THREE.SphereGeometry(0.025, 6, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.18 * s, 0.15, 0.34);
}

// Upper beak — long spear
const beakUpper = addMesh(head, new THREE.ConeGeometry(0.13, 1.5, 10), beakMat, 0, -0.02, 1.05);
beakUpper.rotation.x = Math.PI / 2;
beakUpper.scale.set(1, 1, 0.6);
// beak hook tip
const hook = addMesh(head, new THREE.ConeGeometry(0.05, 0.18, 8), beakMat, 0, -0.05, 1.78);
hook.rotation.x = Math.PI / 2 + 0.4;

// Pouch — a stretchy sac under the beak, gently swinging
const pouchPivot = new THREE.Group();
pouchPivot.position.set(0, -0.16, 0.32);
head.add(pouchPivot);
const pouch = addMesh(pouchPivot, new THREE.SphereGeometry(0.34, 14, 12), pouchMat, 0, -0.12, 0.55);
pouch.scale.set(0.8, 0.9, 1.5);

// Wings — pivots at the shoulders so they can flap/tilt
function makeWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(0.55 * side, 1.75, 0.05);
  pelican.add(pivot);

  const upper = addMesh(pivot, new THREE.BoxGeometry(1.1, 0.1, 0.5), feather, 0.55 * side, -0.1, 0);
  upper.rotation.z = -0.15 * side;
  const tipGroup = new THREE.Group();
  tipGroup.position.set(1.05 * side, -0.25, 0);
  pivot.add(tipGroup);
  const tip = addMesh(tipGroup, new THREE.BoxGeometry(0.9, 0.08, 0.4), featherShade, 0.45 * side, 0, 0);
  tip.rotation.z = -0.25 * side;
  // black wingtip accents
  addMesh(tipGroup, new THREE.BoxGeometry(0.25, 0.09, 0.38), darkMat, 0.85 * side, 0, 0);
  return pivot;
}
const wingL = makeWing(1);
const wingR = makeWing(-1);

// Legs — bent, standing on the board
function makeLeg(side) {
  const leg = new THREE.Group();
  leg.position.set(0.3 * side, 0.85, -0.15);
  pelican.add(leg);
  const thigh = addMesh(leg, new THREE.CylinderGeometry(0.07, 0.06, 0.4, 8), beakMat, 0, -0.15, 0.05);
  thigh.rotation.x = 0.5;
  const shin = addMesh(leg, new THREE.CylinderGeometry(0.05, 0.05, 0.35, 8), beakMat, 0, -0.4, -0.1);
  shin.rotation.x = -0.5;
  const foot = addMesh(leg, new THREE.BoxGeometry(0.22, 0.05, 0.34), beakMat, 0, -0.56, 0.05);
  return leg;
}
makeLeg(1);
makeLeg(-1);

// ---------- Spray particles ----------
const SPRAY_COUNT = 160;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_COUNT * 3);
const sprayData = [];
for (let i = 0; i < SPRAY_COUNT; i++) {
  sprayData.push({
    life: Math.random(),
    speed: 0.6 + Math.random() * 1.4,
    angle: Math.random() * Math.PI * 2,
    spread: 0.3 + Math.random() * 0.9,
    size: Math.random(),
  });
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const sprayMat = new THREE.PointsMaterial({
  color: 0xffffff, size: 0.16, transparent: true, opacity: 0.8, depthWrite: false,
});
const spray = new THREE.Points(sprayGeo, sprayMat);
scene.add(spray);

function updateSpray(t, dt, boardPos) {
  const p = sprayGeo.attributes.position;
  for (let i = 0; i < SPRAY_COUNT; i++) {
    const d = sprayData[i];
    d.life += dt * d.speed;
    if (d.life > 1) {
      d.life -= 1;
      d.angle = Math.random() * Math.PI * 2;
    }
    const life = d.life;
    const back = -2.1; // wake behind the board
    const rise = Math.sin(life * Math.PI) * 0.9 * d.spread;
    const outward = life * d.spread * 1.2;
    p.setXYZ(
      i,
      boardPos.x + back + Math.cos(d.angle) * outward,
      boardPos.y + 0.2 + rise,
      boardPos.z + Math.sin(d.angle) * outward * 1.5
    );
  }
  p.needsUpdate = true;
}

// ---------- Resize ----------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- Animation loop ----------
const clock = new THREE.Clock();
const boardWorld = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  const dt = 0.016;

  updateOcean(t);

  // Surfer rides along the swell in a lazy figure-eight path
  const px = Math.sin(t * 0.5) * 5;
  const pz = Math.cos(t * 0.33) * 3 - 2;
  const py = waveHeight(px, pz, t);
  surfer.position.set(px, py + 0.15, pz);

  // Tilt with the wave slope
  const eps = 0.6;
  const slopeX = (waveHeight(px + eps, pz, t) - waveHeight(px - eps, pz, t)) / (2 * eps);
  const slopeZ = (waveHeight(px, pz + eps, t) - waveHeight(px, pz - eps, t)) / (2 * eps);
  surfer.rotation.z = THREE.MathUtils.lerp(surfer.rotation.z, Math.atan(slopeX) * 1.2, 0.1);
  surfer.rotation.x = THREE.MathUtils.lerp(surfer.rotation.x, -Math.atan(slopeZ) * 1.2, 0.1);
  surfer.rotation.y = Math.sin(t * 0.5) * 0.4 + Math.PI * 0.05;

  // Pelican balances: bobs and leans into turns
  pelican.position.y = Math.sin(t * 2.2) * 0.04;
  pelican.rotation.z = -surfer.rotation.z * 0.6 + Math.sin(t * 1.3) * 0.03;
  pelican.rotation.x = THREE.MathUtils.clamp(-surfer.rotation.x * 0.5, -0.2, 0.2);

  // Wings held out for balance, small corrective flaps
  const flap = Math.sin(t * 2.0) * 0.25 + Math.sin(t * 5.1) * 0.08;
  wingL.rotation.z = 0.35 + flap;
  wingR.rotation.z = -0.35 - flap;
  wingL.rotation.x = Math.sin(t * 1.7) * 0.08;
  wingR.rotation.x = Math.sin(t * 1.7 + 0.5) * 0.08;

  // Head looks around; pouch swings
  head.rotation.y = Math.sin(t * 0.8) * 0.35;
  head.rotation.x = Math.sin(t * 1.1) * 0.08 - 0.05;
  pouchPivot.rotation.x = Math.sin(t * 2.4) * 0.12;
  pouchPivot.rotation.z = Math.sin(t * 1.6) * 0.06;

  // Camera slowly orbits, keeping the surfer framed
  const camAngle = t * 0.12;
  const camR = 11 + Math.sin(t * 0.2) * 1.5;
  camera.position.set(
    px + Math.sin(camAngle) * camR,
    py + 3.6 + Math.sin(t * 0.3) * 0.6,
    pz + Math.cos(camAngle) * camR
  );
  camera.lookAt(px, py + 1.8, pz);

  // Spray at the board
  boardWorld.copy(surfer.position);
  updateSpray(t, 0.016, boardWorld);

  // Clouds drift
  clouds.children.forEach((c, i) => {
    c.position.x += 0.008 * (1 + i * 0.1);
    if (c.position.x > 100) c.position.x = -100;
  });

  renderer.render(scene, camera);
}
animate();
