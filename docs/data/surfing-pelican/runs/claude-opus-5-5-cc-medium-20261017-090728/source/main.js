import * as THREE from "three";

// ---------- renderer / scene ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const FOG_COLOR = new THREE.Color(0xa9d6ee);
scene.fog = new THREE.Fog(FOG_COLOR, 50, 165);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 2000);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- lights ----------
const sunDir = new THREE.Vector3(-0.5, 0.55, 0.65).normalize();
scene.add(new THREE.HemisphereLight(0xcfeaff, 0x1d5a73, 1.1));
const sun = new THREE.DirectionalLight(0xfff1d6, 2.6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 120 });
sun.shadow.bias = -0.0005;
scene.add(sun, sun.target);

// ---------- sky dome, clouds, gulls (follow the camera) ----------
const skyGroup = new THREE.Group();
scene.add(skyGroup);

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(900, 32, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: { sunDir: { value: sunDir } },
    vertexShader: `varying vec3 vDir;
      void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vDir; uniform vec3 sunDir;
      void main(){
        float h = clamp(vDir.y, -0.2, 1.0);
        vec3 horizon = vec3(0.72, 0.86, 0.94);
        vec3 zenith = vec3(0.16, 0.45, 0.80);
        vec3 col = mix(horizon, zenith, pow(max(h, 0.0), 0.55));
        float s = max(dot(normalize(vDir), sunDir), 0.0);
        col += vec3(1.0, 0.9, 0.7) * (pow(s, 600.0) * 3.0 + pow(s, 12.0) * 0.35);
        gl_FragColor = vec4(col, 1.0);
      }`,
  })
);
skyGroup.add(sky);

const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0x8899aa, fog: false });
const puffGeo = new THREE.SphereGeometry(1, 16, 12);
function rand(a, b) { return a + Math.random() * (b - a); }
for (let i = 0; i < 16; i++) {
  const cloud = new THREE.Group();
  const n = 5 + Math.floor(Math.random() * 6);
  for (let j = 0; j < n; j++) {
    const p = new THREE.Mesh(puffGeo, cloudMat);
    const r = rand(12, 26);
    p.scale.set(r * 1.4, r * 0.6, r);
    p.position.set(rand(-40, 40), rand(0, 10), rand(-15, 15));
    cloud.add(p);
  }
  const a = (i / 16) * Math.PI * 2 + rand(-0.2, 0.2);
  const d = rand(450, 700);
  cloud.position.set(Math.cos(a) * d, rand(70, 160), Math.sin(a) * d);
  cloud.lookAt(0, cloud.position.y, 0);
  skyGroup.add(cloud);
}

const gulls = [];
const gullMat = new THREE.MeshBasicMaterial({ color: 0x334455, side: THREE.DoubleSide, fog: false });
for (let i = 0; i < 5; i++) {
  const g = new THREE.Group();
  const wingGeo = new THREE.PlaneGeometry(1.6, 0.35).translate(0.8, 0, 0);
  const l = new THREE.Mesh(wingGeo, gullMat);
  const r = new THREE.Mesh(wingGeo, gullMat);
  r.scale.x = -1;
  l.rotation.x = r.rotation.x = -Math.PI / 2;
  const wl = new THREE.Group(); wl.add(l);
  const wr = new THREE.Group(); wr.add(r);
  g.add(wl, wr);
  g.userData = { wl, wr, phase: rand(0, 6), radius: rand(40, 70), speed: rand(0.08, 0.15), h: rand(22, 40), off: rand(0, 6.28) };
  gulls.push(g);
  scene.add(g);
}

// ---------- ocean ----------
const TAU = Math.PI * 2;
const K = (Math.PI * 2) / 56; // swell wavenumber
const C = 8; // swell speed (+z)
const A = 6.0; // swell height
let lastCrest = 0; // signed phase distance from the crest of the last sample (+ = front face)
function waveHeight(x, z, t) {
  const p = K * (z - C * t) + 0.25 * Math.sin(x * 0.035);
  const s = 0.5 + 0.5 * Math.sin(p);
  lastCrest = ((((p - Math.PI / 2) % TAU) + TAU + Math.PI) % TAU) - Math.PI;
  const swell = A * Math.pow(s, 3.2);
  const chop =
    0.22 * Math.sin(0.55 * x + 1.1 * t) +
    0.16 * Math.sin(0.7 * z + 0.5 * x - 1.7 * t) +
    0.08 * Math.sin(1.6 * x - 1.2 * z + 2.4 * t) +
    0.05 * Math.sin(2.7 * z + 1.9 * x + 3.1 * t);
  return swell + chop;
}

const OCEAN_SIZE = 320;
const OCEAN_SEG = 256;
const SPACING = OCEAN_SIZE / OCEAN_SEG;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG).rotateX(-Math.PI / 2);
const oceanPos = oceanGeo.attributes.position;
const baseXZ = new Float32Array(oceanPos.count * 2);
for (let i = 0; i < oceanPos.count; i++) {
  baseXZ[i * 2] = oceanPos.getX(i);
  baseXZ[i * 2 + 1] = oceanPos.getZ(i);
}
const oceanColors = new Float32Array(oceanPos.count * 3);
oceanGeo.setAttribute("color", new THREE.BufferAttribute(oceanColors, 3));
const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.22, metalness: 0.05 })
);
ocean.receiveShadow = true;
scene.add(ocean);

const cDeep = new THREE.Color(0x0b3a5c);
const cMid = new THREE.Color(0x1680a0);
const cTop = new THREE.Color(0x46c9c4);
const cFoam = new THREE.Color(0xf4fbff);
const tmpC = new THREE.Color();

function smoothstep(a, b, x) {
  const t = Math.min(Math.max((x - a) / (b - a), 0), 1);
  return t * t * (3 - 2 * t);
}

function updateOcean(t, cx, cz) {
  const ox = Math.round(cx / SPACING) * SPACING;
  const oz = Math.round(cz / SPACING) * SPACING;
  ocean.position.set(ox, 0, oz);
  for (let i = 0; i < oceanPos.count; i++) {
    const wx = baseXZ[i * 2] + ox;
    const wz = baseXZ[i * 2 + 1] + oz;
    const h = waveHeight(wx, wz, t);
    oceanPos.setY(i, h);
    const d = lastCrest;
    const k = Math.min(Math.max(h / A, 0), 1);
    if (k < 0.5) tmpC.lerpColors(cDeep, cMid, k * 2);
    else tmpC.lerpColors(cMid, cTop, (k - 0.5) * 2);
    // foam streaks on crests, broken up by the chop
    const streak = 0.5 + 0.5 * Math.sin(wx * 0.9 + Math.sin(wz * 0.4 + t) * 2.0 + t * 1.3);
    // bright lip right at the crest, broken whitewater trailing behind it
    const lip = smoothstep(-0.12, 0.0, d) * (1 - smoothstep(0.08, 0.22 + 0.08 * streak, d));
    const wash = d < 0 ? Math.exp(d * (3.5 - 1.5 * streak)) * streak * 0.8 : 0;
    const foam = Math.min(1, Math.max(lip * 0.95, wash));
    tmpC.lerp(cFoam, foam);
    oceanColors[i * 3] = tmpC.r;
    oceanColors[i * 3 + 1] = tmpC.g;
    oceanColors[i * 3 + 2] = tmpC.b;
  }
  oceanPos.needsUpdate = true;
  oceanGeo.attributes.color.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------- surfboard ----------
const rider = new THREE.Group(); // positioned & oriented on the wave each frame (+x forward, +y up)
scene.add(rider);

function shadowed(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }

const boardGroup = new THREE.Group();
rider.add(boardGroup);
{
  const boardShape = new THREE.Shape();
  boardShape.moveTo(-1.6, 0);
  boardShape.bezierCurveTo(-1.6, 0.32, -0.8, 0.42, 0.0, 0.42);
  boardShape.bezierCurveTo(1.0, 0.42, 1.55, 0.25, 1.85, 0.0);
  boardShape.bezierCurveTo(1.55, -0.25, 1.0, -0.42, 0.0, -0.42);
  boardShape.bezierCurveTo(-0.8, -0.42, -1.6, -0.32, -1.6, 0);
  const boardGeo = new THREE.ExtrudeGeometry(boardShape, {
    depth: 0.06, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.04, bevelSegments: 4, curveSegments: 32,
  }).rotateX(-Math.PI / 2);
  const board = shadowed(new THREE.Mesh(boardGeo, new THREE.MeshStandardMaterial({ color: 0xffd23f, roughness: 0.35 })));
  board.position.y = 0.03;
  boardGroup.add(board);
  // racing stripes
  const stripeMat = new THREE.MeshStandardMaterial({ color: 0xe8432e, roughness: 0.4 });
  for (const zz of [-0.12, 0.12]) {
    const stripe = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.01, 0.06), stripeMat));
    stripe.position.set(0.1, 0.135, zz);
    boardGroup.add(stripe);
  }
  const fin = new THREE.Shape();
  fin.moveTo(0, 0); fin.lineTo(0.28, 0); fin.quadraticCurveTo(0.05, -0.1, -0.08, -0.32); fin.lineTo(0, 0);
  const finMesh = new THREE.Mesh(
    new THREE.ExtrudeGeometry(fin, { depth: 0.02, bevelEnabled: false }),
    new THREE.MeshStandardMaterial({ color: 0x222222 })
  );
  finMesh.position.set(-1.45, 0.02, -0.01);
  boardGroup.add(finMesh);
}

// ---------- pelican ----------
const pelican = new THREE.Group();
rider.add(pelican);

const featherMat = new THREE.MeshStandardMaterial({ color: 0xf2efe8, roughness: 0.85 });
const greyMat = new THREE.MeshStandardMaterial({ color: 0xb9b8b2, roughness: 0.85, side: THREE.DoubleSide });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x2b2a2a, roughness: 0.8, side: THREE.DoubleSide });
const beakMat = new THREE.MeshStandardMaterial({ color: 0xf2a33a, roughness: 0.5 });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xe9875a, roughness: 0.6 });
const legMat = new THREE.MeshStandardMaterial({ color: 0x8a8f96, roughness: 0.7 });
const footMat = new THREE.MeshStandardMaterial({ color: 0xf08a2c, roughness: 0.6, side: THREE.DoubleSide });
const crestMat = new THREE.MeshStandardMaterial({ color: 0xf5e7a8, roughness: 0.8 });

const upper = new THREE.Group(); // everything above the knees; bobs up and down
pelican.add(upper);

// body
const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), featherMat));
body.scale.set(0.62, 0.42, 0.38);
body.rotation.z = 0.35;
body.position.set(0, 0.95, 0);
upper.add(body);
// back / tail
const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.55, 12), greyMat));
tail.rotation.z = Math.PI / 2 + 0.5;
tail.position.set(-0.68, 0.72, 0);
upper.add(tail);
const belly = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), featherMat));
belly.scale.set(0.38, 0.38, 0.32);
belly.position.set(0.25, 1.05, 0);
upper.add(belly);

// neck (S-curve tube) and head live in a group so the head can bob
const neckGroup = new THREE.Group();
neckGroup.position.set(0.35, 1.15, 0);
upper.add(neckGroup);
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0.0, 0.0, 0),
  new THREE.Vector3(0.22, 0.32, 0),
  new THREE.Vector3(0.12, 0.62, 0),
  new THREE.Vector3(0.1, 0.85, 0),
  new THREE.Vector3(0.22, 1.0, 0),
]);
const neck = shadowed(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 40, 0.11, 12), featherMat));
neckGroup.add(neck);
const neckBase = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), featherMat));
neckGroup.add(neckBase);

const head = new THREE.Group();
head.position.set(0.24, 1.02, 0);
neckGroup.add(head);
const skull = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 18), featherMat));
skull.scale.set(1.15, 0.95, 0.9);
head.add(skull);
// yellowish crest
for (let i = 0; i < 4; i++) {
  const c = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.18, 6), crestMat));
  c.position.set(-0.1 - i * 0.03, 0.13, (i - 1.5) * 0.03);
  c.rotation.z = 1.0 + i * 0.12;
  head.add(c);
}
// eyes
for (const s of [-1, 1]) {
  const ring = new THREE.Mesh(new THREE.SphereGeometry(0.04, 12, 8), new THREE.MeshStandardMaterial({ color: 0xf6c9b4 }));
  ring.position.set(0.07, 0.04, s * 0.135);
  ring.scale.z = 0.4;
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.024, 12, 8), new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 }));
  eye.position.set(0.075, 0.042, s * 0.15);
  head.add(ring, eye);
}
// beak + pouch
const beak = new THREE.Group();
beak.position.set(0.14, -0.02, 0);
beak.rotation.z = -0.28;
head.add(beak);
const upperBill = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.06, 1.05, 12), beakMat));
upperBill.rotation.z = -Math.PI / 2;
upperBill.scale.z = 1.4;
upperBill.position.set(0.52, 0, 0);
beak.add(upperBill);
const hook = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.04, 10, 8), new THREE.MeshStandardMaterial({ color: 0xd9502b })));
hook.position.set(1.04, -0.02, 0);
hook.scale.set(1.2, 1, 0.9);
beak.add(hook);
const pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), pouchMat));
pouch.scale.set(0.46, 0.13, 0.085);
pouch.position.set(0.45, -0.1, 0);
beak.add(pouch);

// wings
const wings = [];
function makeShapeGeo(points) {
  const sh = new THREE.Shape();
  sh.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) sh.lineTo(points[i][0], points[i][1]);
  // x = chord (forward), shape y = span -> world +z
  return new THREE.ExtrudeGeometry(sh, { depth: 0.03, bevelEnabled: false }).rotateX(Math.PI / 2);
}
const innerWingGeo = makeShapeGeo([[0.22, 0], [0.2, 0.6], [0.14, 1.1], [-0.38, 1.1], [-0.42, 0.5], [-0.32, 0]]);
const outerWingGeo = makeShapeGeo([[0.14, 0], [0.1, 0.5], [-0.02, 0.8], [-0.36, 0.7], [-0.38, 0]]);
const primaryGeo = new THREE.SphereGeometry(1, 10, 6);
for (const side of [1, -1]) {
  const sideGroup = new THREE.Group();
  sideGroup.scale.z = side;
  sideGroup.position.set(0.05, 1.12, 0);
  upper.add(sideGroup);
  const shoulder = new THREE.Group();
  shoulder.position.z = 0.28;
  sideGroup.add(shoulder);
  shoulder.add(shadowed(new THREE.Mesh(innerWingGeo, greyMat)));
  const elbow = new THREE.Group();
  elbow.position.set(0, 0, 1.1);
  shoulder.add(elbow);
  elbow.add(shadowed(new THREE.Mesh(outerWingGeo, greyMat)));
  // dark primary "finger" feathers
  for (let i = 0; i < 6; i++) {
    const f = shadowed(new THREE.Mesh(primaryGeo, darkMat));
    f.scale.set(0.07, 0.015, 0.42);
    const a = -0.15 - i * 0.12;
    f.position.set(-0.05 - i * 0.065 + Math.sin(a) * 0.3, 0, 0.55 + Math.cos(a) * 0.3 - i * 0.04);
    f.rotation.y = a;
    elbow.add(f);
  }
  // dark trailing edge on inner wing
  const trailing = shadowed(new THREE.Mesh(primaryGeo, darkMat));
  trailing.scale.set(0.08, 0.012, 0.55);
  trailing.position.set(-0.36, -0.01, 0.55);
  shoulder.add(trailing);
  wings.push({ shoulder, elbow, side });
}
pelican.scale.setScalar(0.85);

// legs: hip -> knee -> foot, rebuilt each frame as the body bobs
function makeSegment(r) {
  const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 8), legMat));
  pelican.add(m);
  return m;
}
const _up = new THREE.Vector3(0, 1, 0);
const _dir = new THREE.Vector3();
function setSegment(mesh, a, b) {
  _dir.subVectors(b, a);
  const len = _dir.length();
  mesh.position.addVectors(a, b).multiplyScalar(0.5);
  mesh.scale.set(1, len, 1);
  mesh.quaternion.setFromUnitVectors(_up, _dir.normalize());
}
const legs = [];
for (const s of [-1, 1]) {
  const thigh = makeSegment(0.045);
  const shin = makeSegment(0.035);
  const knee = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), legMat));
  pelican.add(knee);
  const foot = new THREE.Shape();
  foot.moveTo(0, 0);
  foot.lineTo(0.32, 0.14); foot.quadraticCurveTo(0.3, 0, 0.34, -0.02);
  foot.quadraticCurveTo(0.3, -0.05, 0.32, -0.16); foot.lineTo(0, 0);
  const footMesh = shadowed(new THREE.Mesh(new THREE.ShapeGeometry(foot).rotateX(-Math.PI / 2), footMat));
  footMesh.position.set(0.0, 0.14, s * 0.24);
  footMesh.rotation.y = s * -0.25;
  pelican.add(footMesh);
  legs.push({ thigh, shin, knee, s });
}
const hip = new THREE.Vector3(), kneeP = new THREE.Vector3(), ankle = new THREE.Vector3();

// ---------- spray particles ----------
const SPRAY = 900;
const sprayPos = new Float32Array(SPRAY * 3).fill(-1000);
const sprayVel = new Float32Array(SPRAY * 3);
const sprayLife = new Float32Array(SPRAY);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const dotCanvas = document.createElement("canvas");
dotCanvas.width = dotCanvas.height = 64;
{
  const g = dotCanvas.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, "rgba(255,255,255,1)");
  grd.addColorStop(0.4, "rgba(255,255,255,0.7)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
}
const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({
    size: 0.45, map: new THREE.CanvasTexture(dotCanvas), transparent: true, depthWrite: false, color: 0xf2fbff, opacity: 0.85,
  })
);
spray.frustumCulled = false;
scene.add(spray);
let sprayNext = 0;
const tmpV = new THREE.Vector3();
const fwd = new THREE.Vector3(), up = new THREE.Vector3(), side = new THREE.Vector3();

function emitSpray(count, intensity) {
  for (let n = 0; n < count; n++) {
    const i = sprayNext;
    sprayNext = (sprayNext + 1) % SPRAY;
    const s = Math.random() < 0.75 ? 1 : -1; // more spray off the outside rail
    tmpV.set(rand(-1.5, -0.6), 0.05, s * 0.4).applyMatrix4(rider.matrixWorld);
    sprayPos[i * 3] = tmpV.x; sprayPos[i * 3 + 1] = tmpV.y; sprayPos[i * 3 + 2] = tmpV.z;
    const out = rand(1.5, 4.5) * intensity;
    const lift = rand(2, 5) * intensity;
    const back = rand(1, 4);
    sprayVel[i * 3] = side.x * s * out + up.x * lift - fwd.x * back + rand(-0.5, 0.5);
    sprayVel[i * 3 + 1] = side.y * s * out + up.y * lift - fwd.y * back;
    sprayVel[i * 3 + 2] = side.z * s * out + up.z * lift - fwd.z * back + rand(-0.5, 0.5);
    sprayLife[i] = rand(0.6, 1.3);
  }
}

function updateSpray(dt, t) {
  for (let i = 0; i < SPRAY; i++) {
    if (sprayLife[i] <= 0) continue;
    sprayLife[i] -= dt;
    sprayVel[i * 3 + 1] -= 9.8 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
    if (sprayLife[i] <= 0 || sprayPos[i * 3 + 1] < waveHeight(sprayPos[i * 3], sprayPos[i * 3 + 2], t) - 0.1) {
      sprayLife[i] = 0;
      sprayPos[i * 3 + 1] = -1000;
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------- rider path ----------
const VX = 11; // speed along the wave
function boardPos(t, out) {
  // phase on the swell face: just ahead of the crest, carving up and down
  const p = Math.PI / 2 + 0.55 + 0.32 * Math.sin(t * 0.85) + 0.1 * Math.sin(t * 2.1);
  const x = VX * t + 1.5 * Math.sin(t * 0.85 + 1.2);
  const z = (p - 0.25 * Math.sin(x * 0.035)) / K + C * t;
  return out.set(x, waveHeight(x, z, t), z);
}

function surfaceNormal(x, z, t, out) {
  const e = 0.4;
  const hx = waveHeight(x + e, z, t) - waveHeight(x - e, z, t);
  const hz = waveHeight(x, z + e, t) - waveHeight(x, z - e, t);
  return out.set(-hx, 2 * e, -hz).normalize();
}

const pos = new THREE.Vector3(), nextPos = new THREE.Vector3();
const smoothUp = new THREE.Vector3(0, 1, 0);
const basis = new THREE.Matrix4();
const camPos = new THREE.Vector3();
const camTarget = new THREE.Vector3();
let camInit = false;

// ---------- animate ----------
const clock = new THREE.Clock();
let t = 0;
function frame() {
  const dt = Math.min(clock.getDelta(), 1 / 20);
  t += dt;

  // board placement on the wave
  boardPos(t, pos);
  boardPos(t + 0.05, nextPos);
  surfaceNormal(pos.x, pos.z, t, up);
  smoothUp.lerp(up, 1 - Math.exp(-dt * 8)).normalize();
  fwd.subVectors(nextPos, pos);
  const speed = fwd.length() / 0.05;
  fwd.addScaledVector(smoothUp, -fwd.dot(smoothUp)).normalize();
  side.crossVectors(fwd, smoothUp).normalize();
  basis.makeBasis(fwd, smoothUp, side);
  rider.position.copy(pos);
  rider.quaternion.setFromRotationMatrix(basis);
  rider.updateMatrixWorld();

  // turning rate -> lean into the carve
  const carve = Math.cos(t * 0.85);
  pelican.rotation.x = carve * 0.18;
  pelican.rotation.z = -0.05 + 0.04 * Math.sin(t * 2.0);

  // pelican pose
  const bob = 0.07 * Math.sin(t * 1.7) + 0.04 * Math.sin(t * 4.3) - 0.04;
  upper.position.y = bob;
  upper.position.x = 0.03 * Math.sin(t * 1.3);
  upper.rotation.x = -carve * 0.08;
  neckGroup.rotation.z = 0.08 * Math.sin(t * 1.1 + 0.5);
  head.rotation.y = 0.35 * Math.sin(t * 0.37) + 0.15 * Math.sin(t * 1.3);
  head.rotation.z = -0.1 + 0.1 * Math.sin(t * 0.9);
  beak.rotation.z = -0.28 + 0.04 * Math.sin(t * 3.0);
  pouch.scale.y = 0.13 + 0.015 * Math.sin(t * 5.0);
  for (const w of wings) {
    // balance: wings out, flapping gently, outside wing lifts as the board carves
    const balance = carve * 0.25 * w.side;
    w.shoulder.rotation.y = -0.35 + 0.05 * Math.sin(t * 1.4);
    w.shoulder.rotation.x = -(0.15 + 0.18 * Math.sin(t * 2.6 + w.side * 0.4) + balance);
    w.elbow.rotation.x = -(-0.25 + 0.2 * Math.sin(t * 2.6 - 0.8 + w.side * 0.4));
    w.elbow.rotation.y = -0.15;
  }
  for (const L of legs) {
    hip.set(upper.position.x - 0.05, 0.78 + bob, L.s * 0.16);
    ankle.set(0.02, 0.15, L.s * 0.22);
    kneeP.set(0.26 + upper.position.x * 0.5 - bob * 0.8, 0.46 + bob * 0.5, L.s * 0.2);
    setSegment(L.thigh, hip, kneeP);
    setSegment(L.shin, kneeP, ankle);
    L.knee.position.copy(kneeP);
  }

  // spray
  const intensity = 0.7 + 0.5 * Math.abs(Math.sin(t * 0.85));
  emitSpray(Math.round(16 * intensity * (speed / 14)), intensity);
  updateSpray(dt, t);

  // ocean
  updateOcean(t, pos.x, pos.z);

  // camera: in front of the wave, swinging slowly around the rider
  const phi = -0.35 + 0.75 * Math.sin(t * 0.11);
  const dist = 7.5 + 2.0 * Math.sin(t * 0.07 + 1.0);
  const desired = new THREE.Vector3(pos.x + Math.sin(phi) * dist, 0, pos.z + Math.cos(phi) * dist);
  desired.y = Math.max(pos.y + 0.9 + 0.7 * Math.sin(t * 0.13), waveHeight(desired.x, desired.z, t) + 1.2);
  const target = tmpV.set(pos.x, pos.y + 1.1, pos.z);
  if (!camInit) { camPos.copy(desired); camTarget.copy(target); camInit = true; }
  camPos.lerp(desired, 1 - Math.exp(-dt * 2.5));
  camTarget.lerp(target, 1 - Math.exp(-dt * 6));
  camera.position.copy(camPos);
  camera.lookAt(camTarget);

  // things that follow the camera
  skyGroup.position.set(camPos.x, 0, camPos.z);
  sun.target.position.copy(pos);
  sun.position.copy(pos).addScaledVector(sunDir, 50);
  for (const g of gulls) {
    const u = g.userData;
    const a = t * u.speed + u.off;
    g.position.set(pos.x + 30 + Math.cos(a) * u.radius, u.h + Math.sin(t * 0.5 + u.phase) * 2, pos.z - 20 + Math.sin(a) * u.radius);
    g.rotation.y = -a;
    const flap = Math.sin(t * 5 + u.phase) * 0.45;
    u.wl.rotation.z = flap;
    u.wr.rotation.z = -flap;
  }

  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
