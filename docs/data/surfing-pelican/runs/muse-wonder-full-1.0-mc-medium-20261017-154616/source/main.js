import * as THREE from "three";

// Animated, non-interactive surfing pelican. No controls, no input handling.

const container = document.getElementById("app");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const timeScale = reducedMotion ? 0.12 : 1;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3e8);
scene.fog = new THREE.Fog(0xa8dcec, 45, 110);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(16, 7, 8);

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xcfeeff, 0x2a7a8c, 1.1));
const sunLight = new THREE.DirectionalLight(0xfff2cf, 2.2);
sunLight.position.set(18, 24, -10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -25; sunLight.shadow.camera.right = 25;
sunLight.shadow.camera.top = 25; sunLight.shadow.camera.bottom = -25;
sunLight.shadow.camera.far = 70;
scene.add(sunLight);

// ---------- material helper ----------
const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0, ...opts });
function mesh(geo, material, parent, pos = [0, 0, 0], scale = [1, 1, 1]) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(...pos); m.scale.set(...scale);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}

// ---------- sky extras: sun, clouds ----------
const sun = mesh(new THREE.SphereGeometry(2.4, 32, 32),
  new THREE.MeshBasicMaterial({ color: 0xffdf6b }), scene, [-38, 24, -55]);
sun.castShadow = sun.receiveShadow = false;

const clouds = [];
const cloudMat = mat(0xffffff, { roughness: 1 });
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  for (const [dx, dy, dz, r] of [[0, 0, 0, 1.6], [1.7, -0.2, 0.2, 1.1], [-1.7, -0.25, -0.1, 1.2], [0.6, 0.55, -0.3, 1.0]]) {
    mesh(new THREE.SphereGeometry(r, 20, 16), cloudMat, g, [dx, dy, dz], [1, 0.55, 0.8]).castShadow = false;
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g); clouds.push(g);
}
makeCloud(-24, 18, -42, 1.4); makeCloud(6, 21, -50, 1.8);
makeCloud(28, 16, -38, 1.1); makeCloud(-6, 24, -58, 2.2);

// ---------- ocean floor ----------
const oceanGeo = new THREE.PlaneGeometry(160, 160, 72, 72);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, mat(0x1a9ab5, { roughness: 0.6, metalness: 0.02 }));
ocean.position.y = -0.15; ocean.receiveShadow = true;
scene.add(ocean);

// ---------- the breaker wave ----------
// Cross-section profile in XY: trough -> face -> curling lip. Extruded along Z.
const profileCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(10.5, -0.2, 0),
  new THREE.Vector3(7.5, 0.4, 0),
  new THREE.Vector3(5.0, 1.6, 0),
  new THREE.Vector3(3.2, 3.2, 0),
  new THREE.Vector3(2.2, 4.9, 0),
  new THREE.Vector3(2.0, 6.2, 0),
  new THREE.Vector3(2.6, 7.2, 0),
  new THREE.Vector3(3.9, 7.6, 0),
  new THREE.Vector3(5.2, 7.0, 0),
  new THREE.Vector3(5.9, 5.9, 0),
]);

function buildWaveGeometry() {
  const across = 48, along = 40, length = 72;
  const positions = [], indices = [], uvs = [];
  for (let j = 0; j <= along; j++) {
    const z = -length / 2 + (j / along) * length;
    for (let i = 0; i <= across; i++) {
      const p = profileCurve.getPoint(i / across);
      positions.push(p.x, p.y, z);
      uvs.push(i / across, j / along);
    }
  }
  for (let j = 0; j < along; j++) for (let i = 0; i < across; i++) {
    const a = j * (across + 1) + i, b = a + 1, c = a + across + 1, d = c + 1;
    indices.push(a, c, b, b, c, d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.setIndex(indices); g.computeVertexNormals();
  return g;
}
const waveGeo = buildWaveGeometry();
const waveBase = waveGeo.attributes.position.array.slice();
const wave = new THREE.Mesh(waveGeo, mat(0x12a3c4, { roughness: 0.55, metalness: 0.02, side: THREE.DoubleSide }));
wave.receiveShadow = true; wave.castShadow = false;
scene.add(wave);

// Foam lip: white tube following the curling crest, plus a foam band at the base.
const foamMat = mat(0xffffff, { roughness: 0.9 });
const crestPts = [];
for (let j = 0; j <= 20; j++) {
  const p = profileCurve.getPoint(0.8);
  crestPts.push(new THREE.Vector3(p.x, p.y + 0.12, -36 + j * 3.6));
}
const crest = new THREE.Mesh(
  new THREE.TubeGeometry(new THREE.CatmullRomCurve3(crestPts), 40, 0.14, 8), foamMat);
crest.castShadow = false; crest.receiveShadow = false; scene.add(crest);

const foamChunks = [];
// clumpy foam along the crest line
{
  const top = profileCurve.getPoint(0.8);
  for (let i = 0; i < 34; i++) {
    const r = 0.24 + ((i * 7) % 5) * 0.06;
    const s = mesh(new THREE.SphereGeometry(r, 10, 8), foamMat, scene,
      [top.x + ((i * 13) % 7 - 3) * 0.07, top.y + 0.05, -35 + i * 2.1], [1.2, 0.7, 1.2]);
    s.castShadow = false; foamChunks.push(s);
  }
}
for (let i = 0; i < 26; i++) {
  const s = mesh(new THREE.SphereGeometry(0.28 + (i % 4) * 0.09, 10, 8), foamMat, scene,
    [5.6 + (i % 5) * 0.35, 0.15, -34 + i * 2.7], [1.4, 0.5, 1]);
  s.castShadow = false; foamChunks.push(s);
}

// ---------- surfboard ----------
function boardShape(len, wid) {
  const s = new THREE.Shape();
  s.moveTo(0, len / 2);
  s.bezierCurveTo(wid / 2, len * 0.28, wid / 2, -len * 0.25, 0, -len / 2);
  s.bezierCurveTo(-wid / 2, -len * 0.25, -wid / 2, len * 0.28, 0, len / 2);
  return s;
}
const rider = new THREE.Group(); // board + pelican; local forward = +Z
scene.add(rider);

const boardGeo = new THREE.ExtrudeGeometry(boardShape(3.6, 1.05), { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2 });
boardGeo.rotateX(Math.PI / 2); // lay flat, length along Z
const board = mesh(boardGeo, mat(0xff6b4a, { roughness: 0.45 }), rider, [0, 0, 0]);
const stripeGeo = new THREE.ExtrudeGeometry(boardShape(3.3, 0.34), { depth: 0.02, bevelEnabled: false });
stripeGeo.rotateX(Math.PI / 2);
mesh(stripeGeo, mat(0xfff3d6, { roughness: 0.5 }), rider, [0, 0.012, 0]);
// fin hangs below the board's underside (board top surface is at local y=0)
mesh(new THREE.BoxGeometry(0.05, 0.34, 0.5), mat(0x11424e), rider, [0, -0.22, -1.35]);

// ---------- pelican ----------
const pelican = new THREE.Group();
pelican.position.y = -0.05;
rider.add(pelican);

const white = mat(0xf7f4ec, { roughness: 0.9 });
const cream = mat(0xefe3c8, { roughness: 0.9 });
const orange = mat(0xf28c28, { roughness: 0.6 });
const pouchMat = mat(0xf6a35c, { roughness: 0.7 });
const darkFeather = mat(0x2b2f36, { roughness: 0.9 });

// legs + webbed feet planted on the board
for (const side of [-1, 1]) {
  const leg = mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.55, 10), orange, pelican, [side * 0.22, 0.28, side * 0.12]);
  leg.rotation.x = side * 0.18;
  const foot = mesh(new THREE.ConeGeometry(0.17, 0.42, 4), orange, pelican, [side * 0.22, 0.02, side * 0.2 + 0.1], [1, 0.25, 1]);
  foot.rotation.x = Math.PI / 2; foot.rotation.y = Math.PI / 4;
}

// body: plump ellipsoid, chest up
const body = mesh(new THREE.SphereGeometry(0.72, 28, 22), white, pelican, [0, 0.88, -0.05], [0.82, 0.95, 1.25]);
body.rotation.x = -0.35;
mesh(new THREE.SphereGeometry(0.5, 22, 18), cream, pelican, [0, 0.78, 0.42], [0.75, 0.8, 0.8]); // belly/chest

// tail feathers
const tail = mesh(new THREE.ConeGeometry(0.34, 0.85, 12), darkFeather, pelican, [0, 0.95, -0.95], [1, 1, 0.45]);
tail.rotation.x = Math.PI / 2 + 0.35;

// wings on shoulder pivots so they can flap for balance
function makeWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(side * 0.48, 1.18, 0.05);
  pelican.add(pivot);
  const inner = mesh(new THREE.SphereGeometry(0.62, 20, 14), white, pivot, [side * 0.52, 0, -0.08], [1.05, 0.16, 0.62]);
  inner.rotation.y = side * -0.15;
  const tip = mesh(new THREE.SphereGeometry(0.5, 18, 12), darkFeather, pivot, [side * 1.25, -0.02, -0.22], [0.95, 0.12, 0.48]);
  tip.rotation.y = side * -0.3;
  return pivot;
}
const wingL = makeWing(-1), wingR = makeWing(1);

// S-curved neck rising from the chest
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 1.15, 0.45),
  new THREE.Vector3(0, 1.45, 0.28),
  new THREE.Vector3(0, 1.75, 0.38),
  new THREE.Vector3(0, 2.02, 0.62),
]);
mesh(new THREE.TubeGeometry(neckCurve, 20, 0.16, 12), white, pelican);

// head group (bobs while riding)
const head = new THREE.Group();
head.position.set(0, 2.08, 0.66);
pelican.add(head);
mesh(new THREE.SphereGeometry(0.27, 22, 18), white, head, [0, 0, 0], [0.85, 0.9, 1.1]);
for (const side of [-1, 1]) { // crest tuft
  const tuft = mesh(new THREE.ConeGeometry(0.07, 0.34, 8), cream, head, [side * 0.08, 0.2, -0.16]);
  tuft.rotation.x = -0.7; tuft.rotation.z = side * 0.3;
}
for (const side of [-1, 1]) { // eyes
  const eye = mesh(new THREE.SphereGeometry(0.045, 12, 10), mat(0x14181d, { roughness: 0.3 }), head, [side * 0.19, 0.07, 0.13]);
  eye.castShadow = false;
}
// long beak: flattened tapered upper bill + drooping pouch beneath
const beak = new THREE.Group();
beak.position.set(0, -0.04, 0.22); beak.rotation.x = 0.34; // angled down-forward
head.add(beak);
const upperBill = mesh(new THREE.CylinderGeometry(0.028, 0.105, 1.15, 10), orange, beak, [0, 0.03, 0.55], [0.85, 1, 1]);
upperBill.rotation.x = Math.PI / 2;
mesh(new THREE.ConeGeometry(0.05, 0.16, 10), mat(0xd96f1e), beak, [0, -0.01, 1.16]).rotation.x = Math.PI / 2 + 0.5;
const pouch = mesh(new THREE.SphereGeometry(0.24, 18, 14), pouchMat, beak, [0, -0.14, 0.45], [0.5, 0.62, 1.35]);

// ---------- distant gulls ----------
const gulls = [];
function makeGull(x, y, z, phase) {
  const g = new THREE.Group();
  const gm = mat(0xffffff, { roughness: 1 });
  mesh(new THREE.SphereGeometry(0.16, 10, 8), gm, g, [0, 0, 0], [0.7, 0.6, 1.6]).castShadow = false;
  const wings = [];
  for (const side of [-1, 1]) {
    const w = mesh(new THREE.BoxGeometry(0.85, 0.03, 0.22), gm, g, [side * 0.48, 0.05, 0]);
    w.geometry.translate(side * 0.0, 0, 0); w.castShadow = false; wings.push(w);
  }
  g.position.set(x, y, z);
  scene.add(g); gulls.push({ g, wings, phase, baseY: y });
}
makeGull(-14, 13, -26, 0); makeGull(-9, 15, -30, 2.1); makeGull(16, 14, -28, 4.0);

// ---------- spray particles off the board ----------
const SPRAY = 260;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = new Float32Array(SPRAY * 3);
const sprayLife = new Float32Array(SPRAY);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  color: 0xffffff, size: 0.16, transparent: true, opacity: 0.85, depthWrite: false,
}));
scene.add(spray);

// falling foam off the lip
const LIP = 160;
const lipPos = new Float32Array(LIP * 3);
const lipLife = new Float32Array(LIP).map(() => Math.random());
const lipGeo = new THREE.BufferGeometry();
lipGeo.setAttribute("position", new THREE.BufferAttribute(lipPos, 3));
scene.add(new THREE.Points(lipGeo, new THREE.PointsMaterial({
  color: 0xeafcff, size: 0.2, transparent: true, opacity: 0.7, depthWrite: false,
})));

// ---------- animation ----------
const clock = new THREE.Clock();
const lookTarget = new THREE.Vector3(3, 3, 0);
let sprayCursor = 0;

function animate() {
  requestAnimationFrame(animate);
  const rawDt = Math.min(clock.getDelta(), 0.05);
  const dt = rawDt * timeScale;
  const t = clock.elapsedTime * timeScale;

  // ocean swell
  const op = oceanGeo.attributes.position;
  for (let i = 0; i < op.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    op.array[i * 3 + 1] = Math.sin(x * 0.22 + t * 1.1) * 0.16 + Math.cos(z * 0.18 + t * 0.8) * 0.14;
  }
  op.needsUpdate = true; oceanGeo.computeVertexNormals();

  // wave face ripples travelling along the crest
  const wp = waveGeo.attributes.position;
  for (let i = 0; i < wp.count; i++) {
    const z = waveBase[i * 3 + 2], y = waveBase[i * 3 + 1];
    wp.array[i * 3] = waveBase[i * 3] + Math.sin(z * 0.35 - t * 2.2) * 0.08 * Math.min(1, y / 4);
    wp.array[i * 3 + 1] = y + Math.sin(z * 0.5 - t * 2.6) * 0.05;
  }
  wp.needsUpdate = true; waveGeo.computeVertexNormals();

  // pelican carving: runs along the wave (Z) while climbing/dropping the face
  const runZ = Math.sin(t * 0.32) * 13;
  const runZVel = Math.cos(t * 0.32); // sign of travel for yaw/roll
  const carve = 0.5 + 0.5 * Math.sin(t * 0.85); // 0 low on face .. 1 high near lip
  const s = 0.16 + carve * 0.16; // raw curve param: between profile pts 1.4-2.9, the open face
  const pos = profileCurve.getPoint(s);
  const tan = profileCurve.getTangent(s);
  const bob = Math.sin(t * 2.4) * 0.06;

  rider.position.set(pos.x + 0.95, pos.y + 0.22 + bob, runZ);
  // pitch to the face slope, yaw toward travel, roll into the carve
  const pitch = Math.atan2(tan.y, Math.abs(tan.x)) * 0.55;
  const yaw = runZVel >= 0 ? 0.25 * Math.sin(t * 0.85) : Math.PI - 0.25 * Math.sin(t * 0.85);
  rider.rotation.set(0, 0, 0);
  rider.rotateY(yaw + (runZVel >= 0 ? 0 : 0));
  rider.rotateX(pitch * (runZVel >= 0 ? 1 : -1) * 0.4);
  rider.rotateZ(-0.38 - Math.cos(t * 0.85) * 0.16); // lean into the wave face
  board.rotation.y = Math.sin(t * 1.7) * 0.03;

  // pelican body language: crouch, counter-lean, balancing wings, bobbing head
  pelican.position.y = -0.05 - carve * 0.1 + Math.abs(Math.sin(t * 2.4)) * 0.05;
  pelican.rotation.z = 0.22 + Math.cos(t * 0.85) * 0.1;
  pelican.rotation.x = Math.sin(t * 1.3) * 0.05;
  const flap = Math.sin(t * 3.1) * 0.28 + Math.sin(t * 0.85) * 0.2;
  wingL.rotation.z = 0.55 + flap;
  wingR.rotation.z = -0.55 - flap * 0.8 - 0.12;
  wingL.rotation.x = wingR.rotation.x = Math.sin(t * 1.6) * 0.08;
  head.rotation.x = Math.sin(t * 2.4 + 0.6) * 0.12;
  head.rotation.y = Math.sin(t * 0.6) * 0.25; // glances along the wave
  head.position.y = 2.08 + Math.sin(t * 2.4) * 0.045;
  pouch.scale.set(0.5, 0.62 + Math.sin(t * 3.4) * 0.07, 1.35); // pouch wobble
  tail.rotation.z = Math.sin(t * 2.0) * 0.12;

  // spray emitted from the board's tail rail
  const emit = Math.max(1, Math.round(3 * timeScale));
  for (let n = 0; n < emit; n++) {
    const i = sprayCursor; sprayCursor = (sprayCursor + 1) % SPRAY;
    sprayPos[i * 3] = rider.position.x + 0.3;
    sprayPos[i * 3 + 1] = rider.position.y;
    sprayPos[i * 3 + 2] = rider.position.z - Math.sign(runZVel || 1) * 1.4;
    sprayVel[i * 3] = 1.2 + Math.random() * 1.4;
    sprayVel[i * 3 + 1] = 1.6 + Math.random() * 2.0;
    sprayVel[i * 3 + 2] = -Math.sign(runZVel || 1) * (1 + Math.random() * 2) + (Math.random() - 0.5);
    sprayLife[i] = 0.7 + Math.random() * 0.5;
  }
  for (let i = 0; i < SPRAY; i++) {
    if (sprayLife[i] <= 0) { sprayPos[i * 3 + 1] = -10; continue; }
    sprayLife[i] -= dt;
    sprayVel[i * 3 + 1] -= 6.5 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // lip foam cascading down
  const lip = profileCurve.getPoint(0.86);
  for (let i = 0; i < LIP; i++) {
    lipLife[i] -= dt * 0.7;
    if (lipLife[i] <= 0) {
      lipLife[i] = 0.6 + Math.random() * 0.8;
      lipPos[i * 3] = lip.x + Math.random() * 0.5;
      lipPos[i * 3 + 1] = lip.y;
      lipPos[i * 3 + 2] = (Math.random() - 0.5) * 68;
    } else {
      lipPos[i * 3] += dt * 1.6; lipPos[i * 3 + 1] -= dt * 3.2;
    }
  }
  lipGeo.attributes.position.needsUpdate = true;

  // foam chunks pulse, clouds drift, gulls flap across
  foamChunks.forEach((f, i) => { f.scale.y = 0.5 + Math.sin(t * 1.8 + i) * 0.12; });
  clouds.forEach((c, i) => { c.position.x += dt * (0.25 + i * 0.06); if (c.position.x > 55) c.position.x = -55; });
  gulls.forEach(({ g, wings, phase, baseY }) => {
    g.position.x += dt * 2.2; if (g.position.x > 45) g.position.x = -45;
    g.position.y = baseY + Math.sin(t * 0.9 + phase) * 0.5;
    const f = Math.sin(t * 7 + phase) * 0.55;
    wings[0].rotation.z = f; wings[1].rotation.z = -f;
  });

  // fixed cinematic camera: gentle tracking drift, no user control
  const desired = new THREE.Vector3(
    rider.position.x + 12.5,
    rider.position.y + 3.2 + Math.sin(t * 0.23) * 0.4,
    rider.position.z + 8);
  // rider motion is already smooth, so anchor the camera to it directly
  camera.position.copy(desired);
  lookTarget.set(rider.position.x - 0.5, rider.position.y + 1.2, rider.position.z);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
