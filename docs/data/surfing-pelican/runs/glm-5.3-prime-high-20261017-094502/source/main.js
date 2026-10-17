import * as THREE from "three";

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

const { lerp, clamp } = THREE.MathUtils;
const DEEP = new THREE.Color(0x1567a8);
const CREST = new THREE.Color(0xdcf7ff);

function damp(current, target, lambda, dt) {
  return lerp(current, target, 1 - Math.exp(-lambda * dt));
}

function unwrapAngle(prev, next) {
  let d = (next - prev) % (Math.PI * 2);
  if (d > Math.PI) d -= Math.PI * 2;
  if (d < -Math.PI) d += Math.PI * 2;
  return prev + d;
}

/** Stylized ocean: sum of travelling sine swells. */
function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.09 + t * 1.1) * 1.5 +
    Math.sin(x * 0.035 - t * 0.55) * 1.0 +
    Math.cos(z * 0.075 + t * 0.8) * 0.7 +
    Math.sin((x + z) * 0.045 + t * 0.5) * 0.45
  );
}

function stdMat(color, extra = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    flatShading: true,
    roughness: 0.7,
    metalness: 0.02,
    ...extra,
  });
}

/* ------------------------------------------------------------------ */
/* Renderer / scene / camera / lights                                  */
/* ------------------------------------------------------------------ */

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xdff2fb, 55, 250);

// Gradient sky, generated in code (no external assets).
const skyCanvas = document.createElement("canvas");
skyCanvas.width = 32;
skyCanvas.height = 256;
{
  const ctx = skyCanvas.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0, "#3e8fd8");
  g.addColorStop(0.55, "#9fd6f5");
  g.addColorStop(1, "#eaf9ff");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 32, 256);
}
const skyTex = new THREE.CanvasTexture(skyCanvas);
skyTex.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTex;

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);
camera.position.set(-12, 9, 22);

scene.add(new THREE.HemisphereLight(0xcfeeff, 0x0c4a6e, 0.9));
const sunLight = new THREE.DirectionalLight(0xfff2cc, 1.6);
sunLight.position.set(50, 80, -60);
scene.add(sunLight);

// Sun disc
const sun = new THREE.Mesh(
  new THREE.SphereGeometry(7, 16, 12),
  new THREE.MeshBasicMaterial({ color: 0xfff6c9, fog: false })
);
sun.position.set(140, 70, -180);
scene.add(sun);

/* ------------------------------------------------------------------ */
/* Ocean                                                               */
/* ------------------------------------------------------------------ */

const oceanGeo = new THREE.PlaneGeometry(420, 420, 128, 128);
oceanGeo.rotateX(-Math.PI / 2);
const oceanPos = oceanGeo.attributes.position;
const oceanCount = oceanPos.count;
oceanGeo.setAttribute(
  "color",
  new THREE.BufferAttribute(new Float32Array(oceanCount * 3), 3)
);
const oceanCol = oceanGeo.attributes.color;

const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshStandardMaterial({
    vertexColors: true,
    flatShading: true,
    roughness: 0.55,
    metalness: 0.05,
  })
);
scene.add(ocean);

const tmpColor = new THREE.Color();
function updateOcean(t) {
  for (let i = 0; i < oceanCount; i++) {
    const x = oceanPos.getX(i);
    const z = oceanPos.getZ(i);
    const h = waveHeight(x, z, t);
    oceanPos.setY(i, h);
    const m = clamp((h - 0.5) / 2.2, 0, 1); // foam on the crests
    tmpColor.copy(DEEP).lerp(CREST, m);
    oceanCol.setXYZ(i, tmpColor.r, tmpColor.g, tmpColor.b);
  }
  oceanPos.needsUpdate = true;
  oceanCol.needsUpdate = true;
}

/* ------------------------------------------------------------------ */
/* Clouds                                                              */
/* ------------------------------------------------------------------ */

const cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const n = 3 + Math.floor(Math.random() * 3);
  for (let i = 0; i < n; i++) {
    const r = s * (0.55 + Math.random() * 0.5);
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 7, 6), cloudMat);
    puff.position.set((i - (n - 1) / 2) * s * 0.9, (Math.random() - 0.5) * s * 0.3, (Math.random() - 0.5) * s * 0.6);
    puff.scale.y = 0.55;
    g.add(puff);
  }
  g.position.set(x, y, z);
  scene.add(g);
  clouds.push({ group: g, speed: 0.6 + Math.random() * 0.7 });
}
makeCloud(-80, 30, -120, 5);
makeCloud(-20, 36, -150, 7);
makeCloud(45, 28, -110, 4);
makeCloud(100, 34, -140, 6);
makeCloud(140, 27, -100, 4);
makeCloud(-140, 32, -130, 5);

/* ------------------------------------------------------------------ */
/* Distant gulls                                                       */
/* ------------------------------------------------------------------ */

const gullMat = new THREE.MeshBasicMaterial({
  color: 0xfdfdfd,
  side: THREE.DoubleSide,
});
const gulls = [];
function makeGull(cx, cy, cz, radius, speed, phase) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.14, 6, 5), gullMat);
  body.scale.set(1.8, 0.8, 1);
  g.add(body);
  const wingGeo = new THREE.PlaneGeometry(1.0, 0.34);
  wingGeo.rotateX(-Math.PI / 2);
  wingGeo.translate(0, 0, 0.5);
  const wingL = new THREE.Mesh(wingGeo, gullMat);
  const wingR = new THREE.Mesh(wingGeo, gullMat);
  wingR.scale.z = -1;
  g.add(wingL, wingR);
  scene.add(g);
  gulls.push({ group: g, wingL, wingR, cx, cy, cz, radius, speed, phase });
}
makeGull(-20, 13, -45, 28, 0.28, 0);
makeGull(30, 17, -70, 42, 0.2, 2.1);
makeGull(0, 11, -30, 20, 0.34, 4.2);

function updateGulls(t) {
  for (const g of gulls) {
    const a = t * g.speed + g.phase;
    const x = g.cx + Math.cos(a) * g.radius;
    const z = g.cz + Math.sin(a) * g.radius;
    const y = g.cy + Math.sin(a * 2) * 1.4;
    // tangent direction
    const dx = -Math.sin(a);
    const dz = Math.cos(a);
    g.group.position.set(x, y, z);
    g.group.rotation.y = Math.atan2(-dz, dx); // model faces +x
    const flap = Math.sin(t * 8 + g.phase * 3) * 0.55;
    g.wingL.rotation.x = flap;
    g.wingR.rotation.x = -flap;
  }
}

/* ------------------------------------------------------------------ */
/* The pelican surfer                                                  */
/* ------------------------------------------------------------------ */

const WHITE = stdMat(0xf7f3ea);
const DARK = stdMat(0x2f3640);
const BEAK = stdMat(0xf6a028);
const POUCH = stdMat(0xef7c1a);
const FEET = stdMat(0xd97b1f);
const EYE = stdMat(0x1c1c1c);
const BOARD = stdMat(0xe4572e, { roughness: 0.45 });
const STRIPE = stdMat(0xffd166, { roughness: 0.45 });

const surfer = new THREE.Group(); // board + pelican, origin at water surface
surfer.rotation.order = "YXZ";
scene.add(surfer);

/* --- surfboard --- */
const boardGroup = new THREE.Group();
surfer.add(boardGroup);
{
  const shape = new THREE.Shape();
  shape.ellipse(0, 0, 1.9, 0.62, 0, Math.PI * 2);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.18,
    bevelEnabled: true,
    bevelThickness: 0.04,
    bevelSize: 0.05,
    bevelSegments: 2,
  });
  geo.rotateX(-Math.PI / 2);
  const board = new THREE.Mesh(geo, BOARD);
  board.position.y = -0.05;
  boardGroup.add(board);

  const stripe = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.03, 0.34), STRIPE);
  stripe.position.set(0.05, 0.2, 0);
  boardGroup.add(stripe);

  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.45, 0.06), BOARD);
  fin.position.set(-1.45, -0.15, 0);
  fin.rotation.z = 0.35;
  boardGroup.add(fin);
}

/* --- pelican (faces +x) --- */
const pelican = new THREE.Group();
surfer.add(pelican);

// body
const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 8, 6), WHITE);
body.position.set(0, 0.95, 0);
body.scale.set(1.6, 0.85, 1.05);
pelican.add(body);

// tail
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.6, 6), WHITE);
tail.position.set(-0.95, 1.05, 0);
tail.rotation.z = Math.PI / 2 - 0.25;
pelican.add(tail);

// neck (S-curve tube)
{
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.35, 1.2, 0),
    new THREE.Vector3(0.55, 1.65, 0),
    new THREE.Vector3(0.72, 2.0, 0),
    new THREE.Vector3(0.9, 2.15, 0),
  ]);
  const neck = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 10, 0.14, 7, false),
    WHITE
  );
  pelican.add(neck);
}

// head group (animated)
const headGroup = new THREE.Group();
headGroup.position.set(0.9, 2.15, 0);
pelican.add(headGroup);
{
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.26, 8, 6), WHITE);
  head.position.set(0.12, 0.1, 0);
  headGroup.add(head);

  const beak = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.05, 0.14), BEAK);
  beak.position.set(0.62, 0.06, 0);
  beak.rotation.z = -0.05;
  headGroup.add(beak);
}
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.5, 8, 6), POUCH);
pouch.scale.set(0.55, 0.3, 0.2);
pouch.position.set(0.5, -0.07, 0);
headGroup.add(pouch);
for (const side of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.05, 6, 5), EYE);
  eye.position.set(0.26, 0.18, side * 0.2);
  headGroup.add(eye);
}

// legs + feet
for (const side of [-1, 1]) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.32, 6), FEET);
  leg.position.set(0.2, 0.37, side * 0.24);
  pelican.add(leg);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.07, 0.22), FEET);
  foot.position.set(0.22, 0.2, side * 0.26);
  pelican.add(foot);
}

// wings (extruded shapes, mirrored)
function wingShape(points) {
  const s = new THREE.Shape();
  s.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) s.lineTo(points[i][0], points[i][1]);
  s.closePath();
  return s;
}
const wingMain = wingShape([
  [0.35, 0], [0.05, 0.75], [-0.9, 1.45], [-1.15, 1.2], [-0.7, 0.45], [-0.5, 0],
]);
const wingTip = wingShape([
  [-0.55, 0.85], [-0.9, 1.45], [-1.15, 1.2], [-0.8, 0.6],
]);
const wingMainGeo = new THREE.ExtrudeGeometry(wingMain, { depth: 0.06, bevelEnabled: false });
const wingTipGeo = new THREE.ExtrudeGeometry(wingTip, { depth: 0.07, bevelEnabled: false });
wingMainGeo.rotateX(-Math.PI / 2);
wingTipGeo.rotateX(-Math.PI / 2);

const wingGroups = [];
for (const side of [-1, 1]) {
  const wg = new THREE.Group();
  wg.position.set(0, 1.35, side * 0.42);
  const main = new THREE.Mesh(wingMainGeo, WHITE);
  const tip = new THREE.Mesh(wingTipGeo, DARK);
  tip.position.y = 0.01;
  if (side === 1) {
    main.scale.z = -1;
    tip.scale.z = -1;
  }
  wg.add(main, tip);
  pelican.add(wg);
  wingGroups.push(wg);
}

/* ------------------------------------------------------------------ */
/* Spray / splash particles                                            */
/* ------------------------------------------------------------------ */

const SPLASH_N = 140;
const splash = new THREE.InstancedMesh(
  new THREE.SphereGeometry(0.1, 6, 5),
  new THREE.MeshBasicMaterial({ color: 0xeafcff }),
  SPLASH_N
);
splash.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
splash.frustumCulled = false;
scene.add(splash);

const particles = [];
for (let i = 0; i < SPLASH_N; i++) {
  particles.push({ pos: new THREE.Vector3(), vel: new THREE.Vector3(), life: 0, maxLife: 1, size: 1 });
}
let splashIndex = 0;
const dummy = new THREE.Object3D();
for (let i = 0; i < SPLASH_N; i++) {
  dummy.scale.setScalar(0);
  dummy.updateMatrix();
  splash.setMatrixAt(i, dummy.matrix);
}

function spawnSplash(pos, vel, size) {
  const p = particles[splashIndex];
  splashIndex = (splashIndex + 1) % SPLASH_N;
  p.pos.copy(pos);
  p.vel.copy(vel);
  p.maxLife = 0.7 + Math.random() * 0.5;
  p.life = p.maxLife;
  p.size = size;
}

const noseLocal = new THREE.Vector3();
const tailLocal = new THREE.Vector3();
const tmpVel = new THREE.Vector3();

function updateSplash(dt, t) {
  for (let i = 0; i < SPLASH_N; i++) {
    const p = particles[i];
    if (p.life > 0) {
      p.life -= dt;
      p.vel.y -= 11 * dt;
      p.pos.addScaledVector(p.vel, dt);
      if (p.pos.y < waveHeight(p.pos.x, p.pos.z, t) - 0.1) p.life = 0;
    }
    const s = p.life > 0 ? p.size * (0.4 + 0.6 * (p.life / p.maxLife)) : 0;
    dummy.position.copy(p.pos);
    dummy.scale.setScalar(Math.max(s, 0.0001));
    dummy.updateMatrix();
    splash.setMatrixAt(i, dummy.matrix);
  }
  splash.instanceMatrix.needsUpdate = true;
}

/* ------------------------------------------------------------------ */
/* Ride path + animation loop                                          */
/* ------------------------------------------------------------------ */

const pathX = (t) => 48 * Math.sin(t * 0.3);
const pathZ = (t) => 14 * Math.sin(t * 0.51 + 1.7);

let yawSmooth = 0;
let yawUnwrapped = 0;
let prevYawUnwrapped = 0;
let pitchSmooth = 0;
let rollSmooth = 0;

const camOffset = new THREE.Vector3(-11, 6.5, 15);
const camGoal = new THREE.Vector3();
const lookGoal = new THREE.Vector3();
const lookTarget = new THREE.Vector3(0, 2, 0);
const forward = new THREE.Vector3();

const clock = new THREE.Clock();

renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  updateOcean(t);
  updateGulls(t);

  // --- path & velocity (numeric derivative) ---
  const eps = 0.05;
  const px = pathX(t);
  const pz = pathZ(t);
  const vx = (pathX(t + eps) - pathX(t - eps)) / (2 * eps);
  const vz = (pathZ(t + eps) - pathZ(t - eps)) / (2 * eps);
  const speed = Math.hypot(vx, vz);

  // --- board pose ---
  const yawRaw = Math.atan2(-vz, vx);
  yawUnwrapped = unwrapAngle(yawUnwrapped, yawRaw);
  const yawRate = (yawUnwrapped - prevYawUnwrapped) / Math.max(dt, 1e-4);
  prevYawUnwrapped = yawUnwrapped;
  yawSmooth = damp(yawSmooth, yawUnwrapped, 5, dt);

  forward.set(Math.cos(yawSmooth), 0, -Math.sin(yawSmooth));
  const h = waveHeight(px, pz, t);
  const hAhead = waveHeight(px + forward.x * 1.6, pz + forward.z * 1.6, t);
  const pitchTarget = Math.atan2(hAhead - h, 1.6) + speed * 0.004;
  const rollTarget = clamp(-yawRate * 0.32, -0.4, 0.4);

  pitchSmooth = damp(pitchSmooth, pitchTarget, 6, dt);
  rollSmooth = damp(rollSmooth, rollTarget, 4, dt);

  surfer.position.set(px, h * 0.96 + 0.12, pz);
  surfer.rotation.set(rollSmooth, yawSmooth, pitchSmooth);

  // --- pelican body language ---
  pelican.position.y = 0.03 * Math.sin(t * 2.3);
  pelican.rotation.z = 0.04 * Math.sin(t * 1.7);
  headGroup.rotation.y = 0.16 * Math.sin(t * 0.8);
  headGroup.rotation.z = 0.06 * Math.sin(t * 2.6);
  const jiggle = 1 + 0.25 * Math.sin(t * 6);
  pouch.scale.y = 0.3 * jiggle;
  const flap = 0.15 * Math.sin(t * 2.4) + Math.abs(rollSmooth) * 0.55 + speed * 0.008;
  wingGroups[0].rotation.x = flap; // -z wing lifts with +
  wingGroups[1].rotation.x = -flap;

  // --- spray off the nose while moving ---
  surfer.updateMatrixWorld(true);
  if (speed > 2) {
    noseLocal.set(2.0, 0.08, (Math.random() - 0.5) * 0.5);
    boardGroup.localToWorld(noseLocal);
    tmpVel.set(-vx * 0.28 + (Math.random() - 0.5) * 2, 2.5 + Math.random() * 2.5, -vz * 0.28 + (Math.random() - 0.5) * 2);
    spawnSplash(noseLocal, tmpVel, 0.8 + Math.random() * 0.8);

    if (Math.abs(rollSmooth) > 0.12 || Math.random() < 0.4) {
      tailLocal.set(-1.8, 0.05, (Math.random() - 0.5) * 0.8);
      boardGroup.localToWorld(tailLocal);
      tmpVel.set(-vx * 0.15 + (Math.random() - 0.5), 0.8 + Math.random() * 1.2, -vz * 0.15 + (Math.random() - 0.5));
      spawnSplash(tailLocal, tmpVel, 0.6 + Math.random() * 0.6);
    }
  }
  updateSplash(dt, t);

  // --- clouds drift ---
  for (const c of clouds) {
    c.group.position.x += c.speed * dt;
    if (c.group.position.x > 180) c.group.position.x = -180;
  }

  // --- camera follows the ride ---
  camGoal.copy(surfer.position).add(camOffset);
  camera.position.lerp(camGoal, 1 - Math.exp(-2.5 * dt));
  lookGoal
    .copy(surfer.position)
    .addScaledVector(forward, 2.5)
    .add(noseLocal.set(0, 1.5, 0));
  lookTarget.lerp(lookGoal, 1 - Math.exp(-3 * dt));
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
