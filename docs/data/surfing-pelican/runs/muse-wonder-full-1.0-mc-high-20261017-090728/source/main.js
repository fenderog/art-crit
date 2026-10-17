import * as THREE from "three";

// ---------- Renderer / Scene / Camera (fixed, non-interactive) ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xbfe8f2, 28, 75);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(8.2, 3.7, 8.6);
camera.lookAt(0.2, 1.9, 0);

// ---------- Sky dome (gradient shader, generated in code) ----------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(90, 24, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      top: { value: new THREE.Color(0x2f9fd8) },
      mid: { value: new THREE.Color(0x9fdcf0) },
      bot: { value: new THREE.Color(0xfff0cd) },
    },
    vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top; uniform vec3 mid; uniform vec3 bot;
      void main(){ float h=normalize(vP).y*0.5+0.5; vec3 c=h>0.52? mix(mid,top,smoothstep(0.52,0.95,h)) : mix(bot,mid,smoothstep(0.28,0.52,h)); gl_FragColor=vec4(c,1.0); }`,
  })
);
scene.add(sky);

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xcfeeff, 0x2e8aa8, 1.0));
const sunLight = new THREE.DirectionalLight(0xfff2d8, 1.9);
sunLight.position.set(10, 15, 5);
sunLight.castShadow = true;
sunLight.shadow.intensity = 0.6;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -16; sunLight.shadow.camera.right = 16;
sunLight.shadow.camera.top = 14; sunLight.shadow.camera.bottom = -8;
sunLight.shadow.camera.far = 40;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
const fill = new THREE.DirectionalLight(0xbfe8ff, 0.5);
fill.position.set(10, 4, -8);
scene.add(fill);

const sunBall = new THREE.Mesh(
  new THREE.SphereGeometry(1.6, 20, 20),
  new THREE.MeshBasicMaterial({ color: 0xfff3b0, fog: false })
);
sunBall.position.set(-26, 16, -34);
scene.add(sunBall);

// ---------- Ocean base plane (animated ripples) ----------
const oceanGeo = new THREE.PlaneGeometry(90, 60, 56, 34);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshStandardMaterial({ color: 0x0d7ea8, roughness: 0.45, metalness: 0.05, flatShading: true })
);
ocean.position.y = -0.12;
ocean.receiveShadow = true;
scene.add(ocean);

// ---------- The big curling wave ----------
// Profile runs: back trough -> up the back -> crest -> curling lip -> down the face -> front trough.
const profilePts = [
  [-12, 0.0], [-9, 0.25], [-6.5, 0.9], [-4.2, 2.0], [-2.4, 3.3], [-1.2, 4.35],
  [-0.2, 5.0], [0.9, 5.1], [1.9, 4.65], [2.45, 3.85], [2.15, 3.0], [1.25, 2.4],
  [0.2, 1.65], [0.9, 0.95], [2.6, 0.4], [5.5, 0.08], [10, 0.0], [14, 0.0],
].map(([x, y]) => new THREE.Vector3(x, y, 0));
const profileCurve = new THREE.CatmullRomCurve3(profilePts, false, "catmullrom", 0.35);
const PROFILE_N = 110, WIDTH_N = 44, WAVE_W = 34;
const wavePos = [], waveCol = [], waveIdx = [];
const cDeep = new THREE.Color(0x0a6d96), cTeal = new THREE.Color(0x1599b5),
  cLight = new THREE.Color(0x25b8a6), cFoam = new THREE.Color(0xffffff), tmpC = new THREE.Color();
for (let j = 0; j <= WIDTH_N; j++) {
  const z = -WAVE_W / 2 + (j / WIDTH_N) * WAVE_W;
  for (let i = 0; i <= PROFILE_N; i++) {
    const u = i / PROFILE_N;
    const p = profileCurve.getPoint(u);
    // Along-crest undulation so the lip isn't a perfect extrusion: crest height and lip advance vary with z.
    const wob = Math.sin(z * 0.35 + u * 4.0) * 0.07 * Math.sin(u * Math.PI);
    const lipW = Math.max(0, 1 - Math.abs(u - 0.52) / 0.1);
    wavePos.push(
      p.x + wob + Math.sin(z * 0.3 + 1.7) * 0.28 * lipW,
      p.y + Math.sin(z * 0.45) * 0.2 * Math.min(1, p.y / 4),
      z
    );
    // Color mostly by height (deep trough -> glassy light crest); foam only right at the lip tip.
    const hMix = THREE.MathUtils.clamp(p.y / 5.1, 0, 1);
    tmpC.copy(cDeep).lerp(cTeal, Math.min(1, hMix * 1.6)).lerp(cLight, Math.max(0, hMix - 0.55) / 0.45 * 0.55);
    if (u < 0.42) tmpC.lerp(cDeep, 0.35); // back of the wave reads as deeper water behind the crest
    // Single foam row at the exact lip tip; any wider blend washes the whole lip front white.
    if (Math.hypot(p.x - 2.45, p.y - 3.85) < 0.07) tmpC.copy(cFoam);
    waveCol.push(tmpC.r, tmpC.g, tmpC.b);
  }
}
for (let j = 0; j < WIDTH_N; j++) for (let i = 0; i < PROFILE_N; i++) {
  const a = j * (PROFILE_N + 1) + i, b = a + PROFILE_N + 1;
  waveIdx.push(a, b, a + 1, b, b + 1, a + 1);
}
const waveGeo = new THREE.BufferGeometry();
waveGeo.setAttribute("position", new THREE.Float32BufferAttribute(wavePos, 3));
waveGeo.setAttribute("color", new THREE.Float32BufferAttribute(waveCol, 3));
waveGeo.setIndex(waveIdx);
waveGeo.computeVertexNormals();
const waveBasePos = waveGeo.attributes.position.array.slice();
const wave = new THREE.Mesh(waveGeo, new THREE.MeshStandardMaterial({
  vertexColors: true, roughness: 0.85, metalness: 0.0, side: THREE.DoubleSide,
}));
wave.castShadow = true; wave.receiveShadow = true;
scene.add(wave);

// Rideable face: sampled from the same profile (lower face up into the barrel).
const faceCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(2.6, 0.42, 0), new THREE.Vector3(0.95, 0.98, 0),
  new THREE.Vector3(0.2, 1.68, 0), new THREE.Vector3(1.0, 2.35, 0),
], false, "catmullrom", 0.3);

// Whitewater foam strip where the lip lands in the trough.
const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, transparent: true, opacity: 0.85 });
const troughFoam = new THREE.Group();
for (let i = 0; i < 34; i++) {
  const s = new THREE.Mesh(new THREE.SphereGeometry(0.16 + Math.random() * 0.24, 10, 8), foamMat);
  s.scale.y = 0.25;
  s.position.set(2.2 + Math.random() * 1.6, 0.05, -16 + i * 0.95 + Math.random() * 0.4);
  troughFoam.add(s);
}
scene.add(troughFoam);

// ---------- Surfboard (canvas texture generated in code) ----------
function boardTexture() {
  const c = document.createElement("canvas"); c.width = 256; c.height = 512;
  const g = c.getContext("2d");
  g.fillStyle = "#ffd23f"; g.fillRect(0, 0, 256, 512);
  g.fillStyle = "#ff6b4a"; g.fillRect(0, 90, 256, 46); g.fillRect(0, 376, 256, 46);
  g.fillStyle = "#0d7ea8"; g.fillRect(118, 0, 20, 512);
  g.fillStyle = "#ffffff"; g.beginPath(); g.arc(128, 256, 34, 0, Math.PI * 2); g.fill();
  g.fillStyle = "#ff6b4a"; g.beginPath(); g.arc(128, 256, 20, 0, Math.PI * 2); g.fill();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  // ExtrudeGeometry UVs are raw shape coordinates; map the board outline onto 0..1.
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / 0.92, 1 / 3.1);
  t.offset.set(0.5, 0.5);
  return t;
}
const boardShape = new THREE.Shape();
boardShape.moveTo(0, 1.55);
boardShape.bezierCurveTo(0.42, 1.1, 0.46, 0.4, 0.44, -0.5);
boardShape.bezierCurveTo(0.42, -1.15, 0.22, -1.5, 0, -1.55);
boardShape.bezierCurveTo(-0.22, -1.5, -0.42, -1.15, -0.44, -0.5);
boardShape.bezierCurveTo(-0.46, 0.4, -0.42, 1.1, 0, 1.55);
const boardGeo = new THREE.ExtrudeGeometry(boardShape, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.04, bevelSegments: 2 });
boardGeo.rotateX(-Math.PI / 2); // long axis -> Z, deck facing up
const board = new THREE.Mesh(boardGeo, new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.35 }));
board.castShadow = true;
const fin = new THREE.Mesh(
  new THREE.BoxGeometry(0.04, 0.17, 0.3),
  new THREE.MeshStandardMaterial({ color: 0xff6b4a, roughness: 0.4 })
);
fin.position.set(0, -0.1, -1.05);
board.add(fin);

// ---------- Pelican ----------
// Built facing +X (beak toward +X, out of the wave face); wings spread along Z (the board axis).
const MAT = {
  feather: new THREE.MeshStandardMaterial({ color: 0xf8f4e9, roughness: 0.85 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xfff3cf, roughness: 0.85 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x3a3f44, roughness: 0.8 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.55 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xffb26b, roughness: 0.7 }),
  leg: new THREE.MeshStandardMaterial({ color: 0xf07f2e, roughness: 0.6 }),
  eye: new THREE.MeshStandardMaterial({ color: 0x14161a, roughness: 0.25 }),
};
function ball(rx, ry, rz, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), mat);
  m.scale.set(rx, ry, rz); m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}
const pelican = new THREE.Group();   // whole bird; bobs above the board
const bodyG = new THREE.Group();     // torso (crouch / lean)
pelican.add(bodyG);

bodyG.add(ball(1.02, 0.68, 0.6, MAT.feather, -0.08, 0.8, 0));          // body
bodyG.add(ball(0.6, 0.5, 0.48, MAT.cream, 0.42, 0.72, 0));              // chest
const tail = ball(0.55, 0.14, 0.42, MAT.feather, -0.95, 0.92, 0);
tail.rotation.z = 0.35; bodyG.add(tail);
const tailTip = ball(0.3, 0.1, 0.36, MAT.dark, -1.28, 1.02, 0);
tailTip.rotation.z = 0.35; bodyG.add(tailTip);

// Neck + head
const headG = new THREE.Group();
headG.position.set(0.62, 1.34, 0);
bodyG.add(headG);
const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.3, 0.7, 14), MAT.feather);
neck.position.set(-0.12, -0.2, 0); neck.rotation.z = -0.4; neck.castShadow = true;
headG.add(neck);
headG.add(ball(0.4, 0.36, 0.34, MAT.feather, 0.12, 0.18, 0));          // head
headG.add(ball(0.3, 0.14, 0.2, MAT.cream, -0.02, 0.46, 0));            // crest
for (const s of [-1, 1]) {                                             // eyes + rings
  headG.add(ball(0.075, 0.075, 0.075, MAT.eye, 0.36, 0.28, 0.24 * s));
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.022, 8, 18), MAT.beak);
  ring.position.set(0.36, 0.28, 0.25 * s); ring.rotation.y = 0.35 * s;
  headG.add(ring);
  headG.add(ball(0.028, 0.028, 0.028, new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.4, 0.33, 0.29 * s));
}
// Long beak: tapered, slightly hooked tip; pouch hangs below and jiggles.
const beakG = new THREE.Group();
beakG.position.set(0.42, 0.14, 0);
headG.add(beakG);
const upperBeak = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.045, 1.7, 12), MAT.beak);
upperBeak.rotation.z = Math.PI / 2 - 0.1; upperBeak.position.set(0.82, 0.02, 0);
upperBeak.scale.z = 0.55; upperBeak.castShadow = true;
beakG.add(upperBeak);
const beakTip = ball(0.07, 0.055, 0.045, new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.5 }), 1.66, -0.04, 0);
beakG.add(beakTip);
const pouch = ball(0.55, 0.19, 0.16, MAT.pouch, 0.6, -0.15, 0);
beakG.add(pouch);

// Wings: spread wide along the board for balance, dark flight-feather tips.
function makeWing(side) { // side: +1 toward nose (+Z), -1 toward tail (-Z)
  const g = new THREE.Group();
  g.position.set(-0.12, 1.14, 0.4 * side);
  const inner = ball(0.6, 0.1, 0.95, MAT.feather, -0.02, 0, 0.85 * side);
  const tip = ball(0.34, 0.06, 0.68, MAT.dark, -0.3, -0.02, 2.05 * side);
  g.add(inner, tip);
  bodyG.add(g);
  return g;
}
const wingNose = makeWing(1), wingTail = makeWing(-1);

// Legs + webbed feet planted along the board.
function makeLeg(z) {
  const g = new THREE.Group();
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.5, 10), MAT.leg);
  leg.position.set(0, -0.25, 0); leg.castShadow = true;
  const foot = ball(0.2, 0.045, 0.16, MAT.leg, 0.07, -0.5, 0);
  g.add(leg, foot);
  g.position.set(0.05, 0.52, z);
  pelican.add(g);
  return g;
}
makeLeg(0.48); makeLeg(-0.48);

// Rider group: board + pelican, posed on the wave face each frame.
const rider = new THREE.Group();
rider.add(board, pelican);
pelican.position.y = 0.14;
pelican.rotation.y = 0.55; // angled surfer stance: beak three-quarter to camera, wings diagonal
scene.add(rider);

// ---------- Clouds (drift slowly, wrap around) ----------
const clouds = [];
const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, emissive: 0x8b98a8, emissiveIntensity: 0.35 });
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  for (let i = 0; i < 5; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.7 + Math.random() * 0.6, 10, 8), cloudMat);
    m.position.set(i * 0.85 - 1.7, Math.random() * 0.35, Math.random() * 0.5);
    m.scale.y = 0.55;
    g.add(m);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g); clouds.push(g);
}
makeCloud(-16, 10.5, -24, 1.6); makeCloud(6, 12, -28, 2.0);
makeCloud(18, 9.5, -20, 1.3); makeCloud(-6, 13, -30, 1.8); makeCloud(24, 11.5, -26, 1.5);

// ---------- Spray particles (board tail + falling lip) ----------
const SPRAY_N = 420;
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayVel = new Float32Array(SPRAY_N * 3);
const sprayLife = new Float32Array(SPRAY_N);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
function sprayTexture() {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.55, "rgba(255,255,255,0.55)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  color: 0xffffff, size: 0.22, map: sprayTexture(), transparent: true, opacity: 0.8, depthWrite: false, sizeAttenuation: true,
}));
spray.frustumCulled = false;
scene.add(spray);
let sprayCursor = 0;
function spawnSpray(x, y, z, vx, vy, vz, life) {
  const i = sprayCursor; sprayCursor = (sprayCursor + 1) % SPRAY_N;
  sprayPos.set([x, y, z], i * 3); sprayVel.set([vx, vy, vz], i * 3); sprayLife[i] = life;
}
for (let i = 0; i < SPRAY_N; i++) { sprayPos[i * 3 + 1] = -10; sprayLife[i] = 0; }

// ---------- Animation ----------
const clock = new THREE.Clock();
const faceP = new THREE.Vector3(), faceT = new THREE.Vector3();
const camBase = camera.position.clone();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Ride: climb and drop on the lower-mid face (always clear of the lip) while carving along it.
  const rideU = 0.38 + Math.sin(t * 0.65) * 0.2;               // 0.18 .. 0.58 up the face
  faceCurve.getPoint(rideU, faceP);
  faceCurve.getTangent(rideU, faceT);
  const carve = Math.sin(t * 0.45);
  const climbSpeed = Math.cos(t * 0.65);                       // + climbing, - dropping
  // Face outward normal in the XY plane; sit the board just off the surface, deck aligned to it.
  const nx = faceT.y, ny = -faceT.x;
  const faceTilt = Math.atan2(-nx, ny) * 0.75;
  rider.position.set(faceP.x + nx * 0.05, faceP.y + ny * 0.05, carve * 1.6);
  rider.rotation.set(
    Math.sin(t * 0.9) * 0.05 - carve * 0.04,                   // slight fore/aft rock
    -carve * 0.16 + climbSpeed * 0.05,                         // yaw into the carve
    faceTilt                                                   // lean with the face slope
  );

  // Pelican body language: crouch on the drop, stretch on the climb.
  const bob = Math.sin(t * 2.1) * 0.05;
  bodyG.position.y = bob - Math.max(0, -climbSpeed) * 0.1;
  bodyG.rotation.z = -faceTilt * 0.45 - 0.05 + climbSpeed * 0.09; // stay fairly upright on the tilted board
  bodyG.rotation.x = carve * 0.1;
  pelican.position.y = 0.14 + Math.abs(Math.sin(t * 2.1)) * 0.03;

  // Wings work for balance, counter-phased, tips lagging the body roll.
  const flap = Math.sin(t * 2.3);
  wingNose.rotation.x = -0.16 - flap * 0.16 - carve * 0.1;
  wingTail.rotation.x = 0.16 - flap * 0.16 + carve * 0.1;
  wingNose.rotation.y = -0.38 + Math.sin(t * 1.4) * 0.08; // swept back, not pointing at the camera
  wingTail.rotation.y = 0.38 - Math.sin(t * 1.4) * 0.08;

  // Head steady and looking down the line; pouch jiggles with the bumps.
  headG.rotation.z = 0.06 + Math.sin(t * 1.7) * 0.06 - climbSpeed * 0.05;
  headG.rotation.y = -carve * 0.22;
  headG.position.y = 1.34 + Math.sin(t * 2.1 + 0.6) * 0.04;
  const jig = 1 + Math.sin(t * 5.2) * 0.09 + Math.sin(t * 8.1) * 0.04;
  pouch.scale.set(0.55 * (2 - jig) * 0.5 + 0.275, 0.19 * jig, 0.16);
  beakG.rotation.z = Math.sin(t * 3.1) * 0.03;
  tail.rotation.y = Math.sin(t * 1.9) * 0.18;
  tailTip.rotation.y = tail.rotation.y;

  // Wave surface breathes; foam pulses; ocean ripples roll underneath.
  const wp = waveGeo.attributes.position;
  for (let i = 0; i < wp.count; i++) {
    const bx = waveBasePos[i * 3], by = waveBasePos[i * 3 + 1], bz = waveBasePos[i * 3 + 2];
    wp.setX(i, bx + Math.sin(bz * 0.45 + t * 1.6 + by * 0.7) * 0.08 * Math.min(1, by * 0.4));
  }
  wp.needsUpdate = true;
  troughFoam.children.forEach((s, i) => { s.position.x = 2.6 + Math.sin(t * 1.3 + i * 1.7) * 0.45; });
  const op = oceanGeo.attributes.position;
  for (let i = 0; i < op.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    op.setY(i, Math.sin(x * 0.32 + t * 1.4) * 0.09 + Math.cos(z * 0.28 + t * 1.1) * 0.07);
  }
  op.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // Spray: sheet off the board's tail rail, plus droplets pitching off the lip.
  for (let n = 0; n < 4; n++) {
    spawnSpray(
      rider.position.x - 0.2 + Math.random() * 0.2, rider.position.y + 0.05, rider.position.z - 1.35,
      -0.6 - Math.random(), 1.2 + Math.random() * 1.6, -1.6 - Math.random() * 1.6, 0.55 + Math.random() * 0.4
    );
  }
  if (Math.random() < 0.6) {
    spawnSpray(2.45, 3.85, -16 + Math.random() * 32, 0.9 + Math.random(), -0.2, (Math.random() - 0.5) * 0.4, 0.7 + Math.random() * 0.5);
  }
  for (let i = 0; i < SPRAY_N; i++) {
    if (sprayLife[i] <= 0) continue;
    sprayLife[i] -= dt;
    sprayVel[i * 3 + 1] -= 5.5 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
    if (sprayLife[i] <= 0 || sprayPos[i * 3 + 1] < 0) { sprayPos[i * 3 + 1] = -10; sprayLife[i] = 0; }
  }
  sprayGeo.attributes.position.needsUpdate = true;

  for (const c of clouds) { c.position.x += dt * 0.35; if (c.position.x > 34) c.position.x = -34; }

  // Fixed camera with only a faint handheld sway — no user control of any kind.
  camera.position.set(
    camBase.x + Math.sin(t * 0.23) * 0.25,
    camBase.y + Math.sin(t * 0.31) * 0.12,
    camBase.z
  );
  camera.lookAt(0.2 + Math.sin(t * 0.45) * 0.3, 1.9, carve * 0.5);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});


