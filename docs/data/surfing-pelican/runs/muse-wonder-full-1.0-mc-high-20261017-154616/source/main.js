import * as THREE from "three";

const canvas = document.getElementById("scene");
const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
const TIME_SCALE = reducedMotion ? 0.35 : 1;

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xa8d8ea, 34, 95);

const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(0, 3.4, 12.5);

// ---------- sky, sun, lights ----------
function gradientTexture(top, mid, bottom) {
  const c = document.createElement("canvas");
  c.width = 4; c.height = 256;
  const g = c.getContext("2d");
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0, top); grad.addColorStop(0.55, mid); grad.addColorStop(1, bottom);
  g.fillStyle = grad; g.fillRect(0, 0, 4, 256);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(140, 24, 16),
  new THREE.MeshBasicMaterial({ map: gradientTexture("#2f7fc4", "#7ec8e3", "#ffe9c4"), side: THREE.BackSide, fog: false })
);
scene.add(sky);

const sun = new THREE.Mesh(
  new THREE.CircleGeometry(4.2, 32),
  new THREE.MeshBasicMaterial({ color: 0xfff2b0, fog: false })
);
sun.position.set(-26, 20, -70);
scene.add(sun);
const sunGlow = new THREE.Mesh(
  new THREE.CircleGeometry(7.5, 32),
  new THREE.MeshBasicMaterial({ color: 0xffe98a, transparent: true, opacity: 0.35, fog: false })
);
sunGlow.position.copy(sun.position).z -= 0.5;
scene.add(sunGlow);

scene.add(new THREE.HemisphereLight(0xbfe6ff, 0x1d6f7a, 1.2));
const sunlight = new THREE.DirectionalLight(0xfff1cf, 2.3);
sunlight.position.set(-4, 16, 18);
sunlight.castShadow = true;
sunlight.shadow.mapSize.set(2048, 2048);
sunlight.shadow.camera.left = -16; sunlight.shadow.camera.right = 16;
sunlight.shadow.camera.top = 16; sunlight.shadow.camera.bottom = -16;
sunlight.shadow.camera.far = 70;
sunlight.shadow.bias = -0.0004;
scene.add(sunlight);
const fill = new THREE.DirectionalLight(0x9fd8ff, 0.85);
fill.position.set(12, 6, 14);
scene.add(fill);

// ---------- shared helpers / materials ----------
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0, flatShading: true, ...opts });
const WHITE = mat(0xf7f3e8, { roughness: 0.9 });
const CREAM = mat(0xefe6d0, { roughness: 0.9 });
const BLACK_FEATHER = mat(0x2b2f36, { roughness: 0.85 });
const ORANGE = mat(0xf28c28, { roughness: 0.55 });
const POUCH = mat(0xf6a95c, { roughness: 0.65 });
const EYE = new THREE.MeshStandardMaterial({ color: 0x14181d, roughness: 0.25 });

function limb(from, to, radius, material) {
  const dir = new THREE.Vector3().subVectors(to, from);
  const len = dir.length();
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius * 0.85, len, 8), material);
  mesh.position.copy(from).addScaledVector(dir, 0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  mesh.castShadow = true;
  return mesh;
}
function blob(material, sx, sy, sz, x = 0, y = 0, z = 0, seg = 18) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, seg, Math.max(10, seg - 4)), material);
  m.scale.set(sx, sy, sz); m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}

// ---------- ocean surface (animated low-poly swell) ----------
const oceanGeo = new THREE.PlaneGeometry(180, 120, 72, 48);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, mat(0x1299b8, { roughness: 0.38, metalness: 0.05 }));
ocean.position.y = -0.55;
ocean.receiveShadow = true;
scene.add(ocean);

function oceanHeight(x, z, t) {
  return (
    Math.sin(x * 0.16 + t * 1.1) * 0.22 +
    Math.sin(z * 0.21 - t * 0.85 + x * 0.05) * 0.18 +
    Math.sin((x + z) * 0.07 + t * 0.5) * 0.16
  );
}
function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    // Flatten a "face" lane near the breaking wave so the ride reads clearly.
    const lane = THREE.MathUtils.smoothstep(Math.abs(z + 2.5), 2.2, 7);
    pos.setY(i, oceanHeight(x, z, t) * (0.25 + 0.75 * lane));
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------- the breaking wave the pelican rides ----------
// A parametric sheet: u runs along the crest (x), v runs up the face and
// curls over the lip toward the camera, forming a small barrel.
const WAVE_LEN = 34, WAVE_U = 56, WAVE_V = 22;
function wavePoint(u, v, t, out) {
  const x = (u - 0.5) * WAVE_LEN;
  const shoulder = 1 - Math.pow(Math.abs(u - 0.5) * 2, 3) * 0.55; // wave lowers at the ends
  const breathe = 1 + Math.sin(t * 0.9 + u * 5) * 0.03;
  const h = 6.4 * shoulder * breathe;
  // Profile, seen from the side: the trough sits toward the camera (+Z),
  // the face rises as it runs back (-Z) to the crest, then the lip curls
  // forward (+Z) and drops, throwing over the face.
  const upFace = Math.min(v / 0.82, 1);
  let y = -0.55 + Math.pow(upFace, 1.3) * h + Math.sin(u * 22 + t * 2) * 0.04 * v;
  let z = -0.8 - Math.pow(upFace, 1.1) * 3.6;
  const curl = Math.max(0, (v - 0.82) / 0.18); // 0 at crest, 1 at lip tip
  z += curl * curl * 2.2;
  y -= curl * curl * 1.3;
  out.set(x, y, z);
  return out;
}
const waveGeo = new THREE.BufferGeometry();
{
  const verts = [], colors = [], idx = [];
  const deep = new THREE.Color(0x0b7f9e), face = new THREE.Color(0x1cb5cf), lip = new THREE.Color(0xbdf3ec);
  const tmp = new THREE.Vector3(), col = new THREE.Color();
  for (let i = 0; i <= WAVE_U; i++) {
    for (let j = 0; j <= WAVE_V; j++) {
      const u = i / WAVE_U, v = j / WAVE_V;
      wavePoint(u, v, 0, tmp);
      verts.push(tmp.x, tmp.y, tmp.z);
      col.copy(deep).lerp(face, Math.min(1, v * 1.4)).lerp(lip, Math.max(0, v - 0.78) * 3.2);
      colors.push(col.r, col.g, col.b);
    }
  }
  for (let i = 0; i < WAVE_U; i++) {
    for (let j = 0; j < WAVE_V; j++) {
      const a = i * (WAVE_V + 1) + j, b = a + WAVE_V + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  waveGeo.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
  waveGeo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  waveGeo.setIndex(idx);
  waveGeo.computeVertexNormals();
}
const wave = new THREE.Mesh(waveGeo, new THREE.MeshStandardMaterial({
  vertexColors: true, roughness: 0.32, metalness: 0.05, side: THREE.DoubleSide, flatShading: true,
}));
wave.receiveShadow = true;
scene.add(wave);
const _wp = new THREE.Vector3();
function updateWave(t) {
  const pos = waveGeo.attributes.position;
  let n = 0;
  for (let i = 0; i <= WAVE_U; i++) {
    for (let j = 0; j <= WAVE_V; j++, n++) {
      wavePoint(i / WAVE_U, j / WAVE_V, t, _wp);
      pos.setXYZ(n, _wp.x, _wp.y, _wp.z);
    }
  }
  pos.needsUpdate = true;
  waveGeo.computeVertexNormals();
}
// Height/slope of the rideable face at a given x and height up the face (v).
function ridePose(x, t, v = 0.52) {
  const u = THREE.MathUtils.clamp(x / WAVE_LEN + 0.5, 0.05, 0.95);
  const p = wavePoint(u, v, t, new THREE.Vector3());
  const pUp = wavePoint(u, Math.min(0.95, v + 0.1), t, new THREE.Vector3());
  const pitch = Math.atan2(pUp.y - p.y, Math.abs(pUp.z - p.z) + 0.001);
  return { y: p.y, z: p.z, pitch };
}
// Foam puffs tumbling along the lip.
const foam = new THREE.Group();
const foamPuffs = [];
const foamMat = mat(0xffffff, { roughness: 1 });
for (let i = 0; i < 120; i++) {
  const s = 0.06 + Math.random() * 0.11;
  const puff = blob(foamMat, s * 2.4, s * 0.7, s * 1.2, 0, 0, 0, 7);
  puff.castShadow = false;
  foamPuffs.push({ mesh: puff, u: i / 120 + Math.random() * 0.006, phase: Math.random() * Math.PI * 2 });
  foam.add(puff);
}
scene.add(foam);

// ---------- island with palms (backdrop, right) ----------
function makePalm(height, lean) {
  const palm = new THREE.Group();
  const trunkMat = mat(0x8a6b46);
  let from = new THREE.Vector3(0, 0, 0);
  for (let i = 1; i <= 4; i++) {
    const to = new THREE.Vector3(lean * i * i * 0.09, (height / 4) * i, 0);
    palm.add(limb(from, to, 0.11 - i * 0.012, trunkMat));
    from = to;
  }
  const leafMat = mat(0x2e9e5b, { side: THREE.DoubleSide });
  for (let i = 0; i < 7; i++) {
    const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.22, 2.1, 5), leafMat);
    const a = (i / 7) * Math.PI * 2;
    leaf.position.copy(from).add(new THREE.Vector3(Math.cos(a) * 0.7, 0.32, Math.sin(a) * 0.7));
    leaf.rotation.set(Math.sin(a) * 1.15, 0, -Math.cos(a) * 1.15);
    leaf.castShadow = true;
    palm.add(leaf);
  }
  const nut = blob(mat(0x6d532f), 0.16, 0.16, 0.16, from.x, from.y - 0.08, from.z, 8);
  palm.add(nut);
  return palm;
}
const island = new THREE.Group();
{
  const sand = new THREE.Mesh(new THREE.ConeGeometry(5.2, 2.0, 9), mat(0xf2d492, { roughness: 1 }));
  sand.position.y = 0.35; sand.castShadow = true; sand.receiveShadow = true;
  island.add(sand);
  const green = new THREE.Mesh(new THREE.ConeGeometry(3.4, 1.5, 9), mat(0x43b06a, { roughness: 1 }));
  green.position.y = 1.15; green.castShadow = true;
  island.add(green);
  const p1 = makePalm(3.2, 0.7); p1.position.set(-0.8, 1.7, 0.4); island.add(p1);
  const p2 = makePalm(2.5, -0.9); p2.position.set(1.1, 1.5, -0.7); p2.scale.setScalar(0.85); island.add(p2);
  const p3 = makePalm(2.8, 0.4); p3.position.set(0.5, 1.45, 1.2); p3.scale.setScalar(0.7); island.add(p3);
}
island.position.set(23, -0.4, -24);
island.scale.setScalar(1.5);
scene.add(island);

// ---------- drifting clouds ----------
const clouds = [];
const cloudMat = mat(0xffffff, { roughness: 1, flatShading: false });
function makeCloud(x, y, z, s, speed) {
  const g = new THREE.Group();
  const n = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < n; i++) {
    const r = 0.8 + Math.random() * 0.9;
    const puff = blob(cloudMat, r, r * 0.55, r * 0.8, (i - n / 2) * 1.05, Math.random() * 0.3, Math.random() * 0.4, 12);
    puff.castShadow = false;
    g.add(puff);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g);
  clouds.push({ g, speed });
}
makeCloud(-18, 11, -30, 1.6, 0.35); makeCloud(6, 13.5, -38, 2.1, 0.22);
makeCloud(22, 10, -28, 1.3, 0.45); makeCloud(-4, 15, -48, 2.6, 0.16);
makeCloud(-30, 13, -44, 1.9, 0.28);

// ---------- surfboard ----------
function boardTexture() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 128;
  const g = c.getContext("2d");
  const stripes = ["#ff7a3d", "#ffd23f", "#fff7e6", "#0fa3a3", "#fff7e6", "#ffd23f", "#ff7a3d"];
  const w = c.height / stripes.length;
  stripes.forEach((col, i) => { g.fillStyle = col; g.fillRect(0, i * w, c.width, w + 1); });
  g.fillStyle = "#083344";
  g.beginPath(); g.arc(400, 64, 20, 0, Math.PI * 2); g.fill(); // nose dot logo
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(0.32, 1.1); tex.offset.set(0.5, 0.02);
  return tex;
}
function makeBoard() {
  const s = new THREE.Shape();
  s.moveTo(-1.65, 0);
  s.bezierCurveTo(-1.65, 0.34, -0.7, 0.46, 0.35, 0.44);
  s.bezierCurveTo(1.25, 0.42, 1.85, 0.24, 1.95, 0); // pointed nose at +x
  s.bezierCurveTo(1.85, -0.24, 1.25, -0.42, 0.35, -0.44);
  s.bezierCurveTo(-0.7, -0.46, -1.65, -0.34, -1.65, 0);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.04, bevelSegments: 2, steps: 1 });
  geo.rotateX(-Math.PI / 2);
  const board = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.35, metalness: 0.05 }));
  board.castShadow = true; board.receiveShadow = true;
  // Centre fin underneath the tail.
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.26, 0.05), mat(0x083344));
  fin.position.set(-1.25, -0.13, 0); fin.rotation.z = 0.25;
  board.add(fin);
  return board;
}

// ---------- the pelican ----------
// Built facing +Z (out of the wave face, toward the camera) in a sideways
// surf stance: webbed feet spread along the board (+/-X), wings held out
// like a surfer's arms, long beak pointing at the viewer.
function makeWing(side) { // side: +1 right (+X), -1 left
  const shoulder = new THREE.Group();
  const inner = blob(WHITE, 0.85, 0.13, 0.34, side * 0.78, 0, -0.05, 12);
  inner.rotation.z = side * -0.08;
  shoulder.add(inner);
  const elbow = new THREE.Group();
  elbow.position.set(side * 1.5, 0.02, -0.08);
  const outer = blob(WHITE, 0.62, 0.1, 0.27, side * 0.5, 0, -0.03, 12);
  elbow.add(outer);
  // Black flight feathers, fanned at the tip (a pelican hallmark).
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.045, 0.13), BLACK_FEATHER);
    f.position.set(side * (1.05 + i * 0.05), 0, -0.2 + i * 0.13);
    f.rotation.y = side * (-0.32 + i * 0.2);
    f.castShadow = true;
    elbow.add(f);
  }
  shoulder.add(elbow);
  shoulder.userData.elbow = elbow;
  return shoulder;
}
function makeFoot() {
  const foot = new THREE.Group();
  const pad = blob(ORANGE, 0.3, 0.055, 0.2, 0, 0, 0.04, 10);
  foot.add(pad);
  for (let i = -1; i <= 1; i++) {
    const toe = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.26, 6), ORANGE);
    toe.rotation.x = Math.PI / 2;
    toe.position.set(i * 0.13, 0, 0.26);
    toe.rotation.y = i * -0.35;
    toe.castShadow = true;
    foot.add(toe);
  }
  return foot;
}
function makePelican() {
  const bird = new THREE.Group();
  const bodyG = new THREE.Group(); // crouches/bobs above the legs
  bird.add(bodyG);

  const body = blob(WHITE, 0.82, 0.66, 0.62, 0, 0, -0.05, 20);
  bodyG.add(body);
  const belly = blob(CREAM, 0.68, 0.54, 0.5, 0, -0.14, 0.14, 16);
  bodyG.add(belly);
  // Tail fan at the back (-Z), grey-tipped.
  for (let i = -1; i <= 1; i++) {
    const t = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.05, 0.55), i === 0 ? WHITE : mat(0xb9bec6));
    t.position.set(i * 0.2, 0.05, -0.72);
    t.rotation.set(-0.45, i * 0.35, 0);
    t.castShadow = true;
    bodyG.add(t);
  }
  const wingL = makeWing(-1); wingL.position.set(-0.62, 0.38, -0.05); bodyG.add(wingL);
  const wingR = makeWing(1); wingR.position.set(0.62, 0.38, -0.05); bodyG.add(wingR);

  // S-curved neck + head, pivoted at the chest so it can bob and weave.
  const neckG = new THREE.Group();
  neckG.position.set(0, 0.38, 0.32);
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0.34, 0.2),
    new THREE.Vector3(0, 0.66, 0.1),
    new THREE.Vector3(0, 0.88, 0.3),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(curve, 14, 0.155, 10), WHITE);
  neck.castShadow = true;
  neckG.add(neck);
  const headG = new THREE.Group();
  headG.position.set(0, 0.92, 0.34);
  const head = blob(WHITE, 0.3, 0.27, 0.32, 0, 0, 0, 16);
  headG.add(head);
  const crest = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.3, 6), CREAM);
  crest.position.set(0, 0.28, -0.12); crest.rotation.x = -0.7; crest.castShadow = true;
  headG.add(crest);
  // Eyes with the pelican's bare blue-grey skin patch.
  for (const sx of [-1, 1]) {
    const patch = blob(mat(0x7fb6c9, { roughness: 0.6 }), 0.085, 0.085, 0.085, sx * 0.24, 0.07, 0.16, 10);
    headG.add(patch);
    const eye = blob(EYE, 0.05, 0.05, 0.05, sx * 0.265, 0.085, 0.2, 10);
    headG.add(eye);
    const glint = blob(new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.016, 0.016, 0.016, sx * 0.285, 0.11, 0.235, 6);
    glint.castShadow = false;
    headG.add(glint);
  }
  // The great orange bill: flattened upper mandible + wobbling pouch.
  const beakG = new THREE.Group();
  beakG.position.set(0, -0.02, 0.26);
  const upper = new THREE.Mesh(new THREE.ConeGeometry(0.13, 1.35, 8), ORANGE);
  upper.scale.set(1, 1, 0.55);
  upper.rotation.x = Math.PI / 2 + 0.1;
  upper.position.set(0, 0.03, 0.62);
  upper.castShadow = true;
  beakG.add(upper);
  const nail = blob(mat(0xd96c1e), 0.07, 0.07, 0.1, 0, -0.02, 1.3, 8);
  beakG.add(nail);
  const pouch = blob(POUCH, 0.17, 0.2, 0.62, 0, -0.18, 0.55, 12);
  beakG.add(pouch);
  headG.add(beakG);
  neckG.add(headG);
  bodyG.add(neckG);

  // Bent orange legs in a surf stance, feet planted on the board.
  const legs = new THREE.Group();
  for (const sx of [-1, 1]) {
    const hip = new THREE.Vector3(sx * 0.34, 0.62, 0.02);
    const knee = new THREE.Vector3(sx * 0.62, 0.34, 0.16);
    const ankle = new THREE.Vector3(sx * 0.58, 0.08, 0.02);
    legs.add(limb(hip, knee, 0.075, ORANGE));
    legs.add(limb(knee, ankle, 0.06, ORANGE));
    const foot = makeFoot();
    foot.position.set(sx * 0.58, 0.03, 0.02);
    legs.add(foot);
    // Thigh feathering where leg meets body.
    legs.add(blob(WHITE, 0.2, 0.22, 0.2, sx * 0.36, 0.6, 0.02, 10));
  }
  bird.add(legs);
  bodyG.position.y = 1.02;
  return { bird, bodyG, wingL, wingR, neckG, headG, pouch, beakG };
}

const rider = new THREE.Group();
const board = makeBoard();
board.position.y = 0.02;
rider.add(board);
const pel = makePelican();
pel.bird.position.y = 0.1;
rider.add(pel.bird);
scene.add(rider);

// ---------- spray kicked up by the board ----------
const SPRAY_N = 340;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayData = [];
for (let i = 0; i < SPRAY_N; i++) sprayData.push({ life: Math.random(), vel: new THREE.Vector3(), origin: new THREE.Vector3(0, -10, 0) });
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  color: 0xffffff, size: 0.14, transparent: true, opacity: 0.9, depthWrite: false, sizeAttenuation: true,
}));
spray.frustumCulled = false;
scene.add(spray);
function respawnSpray(p, emitter, kick) {
  p.life = 0;
  p.origin.copy(emitter);
  p.vel.set(
    -1.6 - Math.random() * 2.2 - kick * 1.4,           // trailing behind the nose (+X travel)
    1.2 + Math.random() * 2.4 + kick,
    0.6 + Math.random() * 1.4                          // sheeting out of the face, toward camera
  );
}
function updateSpray(dt, emitter, kick) {
  for (let i = 0; i < SPRAY_N; i++) {
    const p = sprayData[i];
    p.life += dt / (0.55 + (i % 7) * 0.06);
    if (p.life >= 1) respawnSpray(p, emitter, kick);
    const lt = p.life * 0.85;
    sprayPos[i * 3] = p.origin.x + p.vel.x * lt;
    sprayPos[i * 3 + 1] = p.origin.y + p.vel.y * lt - 4.4 * lt * lt;
    sprayPos[i * 3 + 2] = p.origin.z + p.vel.z * lt;
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------- gulls circling overhead ----------
const gulls = [];
function makeGull(radius, height, speed, phase, cx, cz) {
  const g = new THREE.Group();
  const body = blob(WHITE, 0.16, 0.13, 0.42, 0, 0, 0, 10);
  g.add(body);
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.22, 6), ORANGE);
  beak.rotation.x = Math.PI / 2; beak.position.set(0, 0, 0.5);
  g.add(beak);
  const wings = [];
  for (const sx of [-1, 1]) {
    const w = new THREE.Group();
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.03, 0.34), WHITE);
    panel.position.x = sx * 0.55; panel.castShadow = true;
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.03, 0.26), mat(0x9aa3ad));
    tip.position.x = sx * 1.15;
    w.add(panel, tip);
    g.add(w);
    wings.push({ w, sx });
  }
  scene.add(g);
  gulls.push({ g, wings, radius, height, speed, phase, cx, cz });
}
makeGull(13, 8.5, 0.16, 0, -4, -14);
makeGull(17, 10.5, -0.11, 2.4, 3, -18);
makeGull(9, 7.2, 0.22, 4.2, 6, -10);
makeGull(21, 12, 0.09, 1.2, -8, -24);

// ---------- a dolphin that leaps now and then ----------
const dolphin = new THREE.Group();
{
  const skin = mat(0x6f93ad, { roughness: 0.45 });
  const pale = mat(0xdcebf4, { roughness: 0.5 });
  const body = blob(skin, 1.25, 0.34, 0.36, 0, 0, 0, 14); dolphin.add(body);
  dolphin.add(blob(pale, 1.05, 0.24, 0.28, 0.05, -0.14, 0, 12));
  const snout = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.55, 8), skin);
  snout.rotation.z = -Math.PI / 2; snout.position.set(1.42, -0.03, 0); snout.castShadow = true; dolphin.add(snout);
  const dorsal = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.5, 6), skin);
  dorsal.position.set(-0.1, 0.42, 0); dorsal.rotation.z = 0.35; dorsal.scale.z = 0.35; dolphin.add(dorsal);
  for (const sz of [-1, 1]) {
    const flip = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.05, 0.22), skin);
    flip.position.set(-1.32, 0.05, sz * 0.22); flip.rotation.set(sz * 0.5, sz * -0.5, 0.2); dolphin.add(flip);
    const pec = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.04, 0.18), skin);
    pec.position.set(0.55, -0.22, sz * 0.34); pec.rotation.set(sz * 0.7, 0, -0.3); dolphin.add(pec);
    dolphin.add(blob(EYE, 0.045, 0.045, 0.045, 1.05, 0.08, sz * 0.3, 8));
  }
}
dolphin.position.set(-11, -2, 3.5);
scene.add(dolphin);
const splashRing = new THREE.Mesh(
  new THREE.TorusGeometry(0.8, 0.07, 6, 24),
  new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0, roughness: 1 })
);
splashRing.rotation.x = Math.PI / 2;
splashRing.position.set(-11, -0.35, 3.5);
scene.add(splashRing);

// ---------- animation ----------
const clock = new THREE.Clock();
let elapsed = 0;
const lookTarget = new THREE.Vector3(0, 1.8, -3);
const _emitter = new THREE.Vector3();
const _foamP = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05) * TIME_SCALE;
  elapsed += dt;
  const t = elapsed;

  updateOcean(t);
  updateWave(t);

  // Foam puffs tumble along the lip and spill down the face.
  for (const f of foamPuffs) {
    const spill = (Math.sin(t * 0.7 + f.phase) * 0.5 + 0.5) * 0.015;
    wavePoint(f.u, 0.998 - spill, t, _foamP);
    f.mesh.position.copy(_foamP);
    f.mesh.position.y += 0.05;
    f.mesh.position.z += 0.12;
    f.mesh.rotation.y = t * 0.6 + f.phase;
  }

  // The ride: slow traverse along the crest, pumping up and down the face.
  const traverse = Math.sin(t * 0.24) * 3.4 + Math.sin(t * 0.11) * 1.2;
  const pump = Math.sin(t * 0.95);                    // -1 low on face, +1 high
  const vRide = 0.38 + pump * 0.1;
  const pose = ridePose(traverse, t, vRide);
  const hopPulse = Math.pow(Math.max(0, Math.sin(t * 0.45 + 1.2)), 14); // brief hop every ~14 s
  const hop = hopPulse * 0.55;
  rider.position.set(traverse, pose.y + 0.1 + hop, pose.z + 0.55);
  rider.rotation.set(
    pose.pitch * 0.38 - hopPulse * 0.18 + Math.sin(t * 1.9) * 0.03,
    -0.28 + Math.sin(t * 0.24 + 0.6) * 0.1,
    pump * -0.16 + Math.cos(t * 0.95) * 0.08
  );

  // Pelican body language: crouch with the pump, wings out for balance.
  const flapSpeed = 2.6 + hopPulse * 7;
  const flap = Math.sin(t * flapSpeed) * (0.14 + hopPulse * 0.35);
  const balance = Math.cos(t * 0.95) * 0.22;
  pel.bodyG.position.y = 1.02 - Math.max(0, -pump) * 0.12 + Math.sin(t * 1.9) * 0.03 + hopPulse * 0.08;
  pel.bodyG.rotation.z = balance * 0.35;
  pel.bodyG.rotation.x = 0.08 + Math.sin(t * 1.3) * 0.04;
  pel.wingL.rotation.z = 0.12 + flap + balance * 0.6;
  pel.wingR.rotation.z = -0.12 - flap + balance * 0.6;
  pel.wingL.rotation.x = Math.sin(t * 1.7) * 0.08;
  pel.wingR.rotation.x = Math.sin(t * 1.7 + 0.8) * 0.08;
  pel.wingL.userData.elbow.rotation.z = 0.25 + Math.sin(t * flapSpeed - 0.7) * 0.22;
  pel.wingR.userData.elbow.rotation.z = -0.25 - Math.sin(t * flapSpeed - 0.7) * 0.22;
  // Neck weaves against the body roll, head stays level and curious.
  pel.neckG.rotation.z = -balance * 0.55 + Math.sin(t * 0.8) * 0.06;
  pel.neckG.rotation.x = Math.sin(t * 1.15) * 0.07 - hopPulse * 0.15;
  pel.headG.rotation.y = Math.sin(t * 0.5) * 0.38;
  pel.headG.rotation.z = Math.sin(t * 0.9 + 2) * 0.09;
  pel.beakG.rotation.x = Math.sin(t * 1.4) * 0.045;
  const jiggle = 1 + Math.sin(t * 5.2) * 0.07 + hopPulse * Math.sin(t * 16) * 0.12;
  pel.pouch.scale.set(0.17 * jiggle, 0.2 * (2 - jiggle) * 0.96 + 0.02, 0.62);

  // Spray from the board's tail rail.
  rider.updateMatrixWorld();
  _emitter.set(-1.45, 0.05, 0.1).applyMatrix4(rider.matrixWorld);
  updateSpray(dt, _emitter, 0.5 + Math.abs(Math.cos(t * 0.95)) * 0.8 + hopPulse * 1.6);

  // Gulls on lazy circles, flapping in bursts.
  for (const gl of gulls) {
    const a = t * gl.speed + gl.phase;
    gl.g.position.set(gl.cx + Math.cos(a) * gl.radius, gl.height + Math.sin(t * 0.7 + gl.phase) * 0.5, gl.cz + Math.sin(a) * gl.radius * 0.55);
    gl.g.rotation.y = -a + (gl.speed > 0 ? 0 : Math.PI);
    gl.g.rotation.z = gl.speed > 0 ? 0.3 : -0.3;
    const burst = Math.max(0.15, Math.sin(t * 0.6 + gl.phase * 3)) ;
    const f = Math.sin(t * 7 + gl.phase) * 0.55 * burst;
    for (const { w, sx } of gl.wings) w.rotation.z = sx * f;
  }

  // Dolphin leap: a 2.4 s arc every 9 s, alternating direction of travel.
  const leapCycle = (t % 9) / 9;
  const leapT = leapCycle / 0.27;
  const flipDir = Math.floor(t / 9) % 2 === 0 ? 1 : -1;
  if (leapT < 1) {
    const x0 = flipDir > 0 ? -8.5 : -2;
    dolphin.visible = true;
    dolphin.position.set(
      x0 + flipDir * leapT * 6.5,
      -0.9 + Math.sin(leapT * Math.PI) * 2.5,
      3.5 + Math.sin(Math.floor(t / 9) * 2.3) * 1.2
    );
    dolphin.rotation.set(0, flipDir > 0 ? 0 : Math.PI, flipDir * Math.cos(leapT * Math.PI) * 0.75);
    const splash = leapT < 0.14 ? leapT / 0.14 : leapT > 0.86 ? (1 - leapT) / 0.14 : 0;
    splashRing.material.opacity = (1 - splash) * 0.0 + (leapT < 0.2 || leapT > 0.8 ? 0.75 : 0);
    splashRing.position.x = dolphin.position.x;
    splashRing.position.z = dolphin.position.z;
    const ringScale = 1 + ((leapT < 0.5 ? leapT : 1 - leapT) * 6);
    splashRing.scale.setScalar(Math.min(3.2, ringScale));
  } else {
    dolphin.visible = false;
    splashRing.material.opacity = 0;
  }

  // Clouds drift and wrap around.
  for (const c of clouds) {
    c.g.position.x += c.speed * dt;
    if (c.g.position.x > 42) c.g.position.x = -42;
  }
  island.rotation.y = Math.sin(t * 0.05) * 0.04;

  // Non-interactive camera: a slow, gentle dolly that follows the rider.
  const camX = traverse * 0.55 + Math.sin(t * 0.09) * 1.6;
  const camY = 4.1 + Math.sin(t * 0.13) * 0.55 + pump * 0.25;
  const camZ = (13.2 + Math.sin(t * 0.07) * 1.0) * (camera.aspect < 1 ? 1.4 : 1);
  camera.position.lerp(new THREE.Vector3(camX, camY, camZ), 1 - Math.pow(0.0015, dt));
  lookTarget.lerp(new THREE.Vector3(traverse * 0.85, rider.position.y + 1.5, rider.position.z), 1 - Math.pow(0.0008, dt));
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
updateOcean(0);
updateWave(0);
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});




