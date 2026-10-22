// Surfing Pelican — animated, non-interactive Three.js scene.
// A great white pelican balances on a striped surfboard, riding an endless
// turquoise curl. No controls: just open the page and watch.
import * as THREE from "three";

// ============================== renderer / scene ==============================
const app = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fdcf5, 22, 46);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 120);
camera.position.set(3.9, 2.45, 7.7);

// Gradient sky dome
{
  const skyGeo = new THREE.SphereGeometry(55, 24, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x1a9fe8) },
      mid: { value: new THREE.Color(0x63c7f2) },
      bot: { value: new THREE.Color(0xd6f2fd) },
    },
    vertexShader: [
      "varying vec3 vP;",
      "void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    ].join("\n"),
    fragmentShader: [
      "uniform vec3 top; uniform vec3 mid; uniform vec3 bot; varying vec3 vP;",
      "void main(){",
      "  float h = normalize(vP).y;",
      "  vec3 c = h > 0.12 ? mix(mid, top, smoothstep(0.12, 0.65, h)) : mix(bot, mid, smoothstep(-0.08, 0.12, h));",
      "  gl_FragColor = vec4(c, 1.0);",
      "}",
    ].join("\n"),
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
}

// ============================== lights ==============================
scene.add(new THREE.HemisphereLight(0xcfeeff, 0x1a6f8f, 0.95));
const sun = new THREE.DirectionalLight(0xfff3d6, 2.2);
sun.position.set(6, 10, 5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -9; sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9; sun.shadow.camera.bottom = -6;
sun.shadow.camera.far = 30; sun.shadow.bias = -0.0004;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xbfe8ff, 0.55);
fill.position.set(-7, 4, -4);
scene.add(fill);

// ============================== materials ==============================
const M = {
  feather: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.62, metalness: 0 }),
  featherShade: new THREE.MeshStandardMaterial({ color: 0xf1ead9, roughness: 0.7, metalness: 0 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xf57d20, roughness: 0.42, metalness: 0 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xf9a13a, roughness: 0.5, metalness: 0 }),
  leg: new THREE.MeshStandardMaterial({ color: 0xef6f1a, roughness: 0.55, metalness: 0 }),
  eyeWhite: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.25 }),
  eyeBlack: new THREE.MeshStandardMaterial({ color: 0x16181c, roughness: 0.18 }),
  water: new THREE.MeshStandardMaterial({ color: 0x0aa2c8, roughness: 0.55, metalness: 0 }),
  waveFace: new THREE.MeshStandardMaterial({ color: 0x12b5dd, roughness: 0.28, metalness: 0.05 }),
  foam: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85 }),
  cloud: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, emissive: 0x8fa5b8, emissiveIntensity: 0.45 }),
};
function mesh(geo, mat, parent, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  if (parent) parent.add(m);
  return m;
}
function ellipsoid(parent, mat, r, sx, sy, sz, x, y, z) {
  const m = mesh(new THREE.SphereGeometry(r, 28, 22), mat, parent, x, y, z);
  m.scale.set(sx, sy, sz);
  return m;
}

// ============================== ocean ==============================
const oceanGeo = new THREE.PlaneGeometry(70, 36, 96, 48);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, M.water);
ocean.receiveShadow = true;
ocean.position.y = -0.55;
scene.add(ocean);

// Same swell the board rides — sampled for the ocean surface and the surfer.
function swell(x, z, t) {
  return Math.sin(x * 0.55 - t * 1.6) * 0.16
       + Math.sin(z * 0.8 + x * 0.25 - t * 1.1) * 0.11
       + Math.sin((x + z) * 0.35 - t * 0.7) * 0.08;
}

// ============================== the big curling wave ==============================
const waveGroup = new THREE.Group();
waveGroup.position.set(-2.6, -0.5, -3.4);
waveGroup.rotation.y = 0.38;
scene.add(waveGroup);
{
  // Cartoon curl profile, extruded across the background.
  const s = new THREE.Shape();
  s.moveTo(-3.4, 0);
  s.bezierCurveTo(-3.2, 1.8, -2.2, 3.4, -0.4, 4.1);   // rising back
  s.bezierCurveTo(1.2, 4.7, 2.9, 4.3, 3.4, 3.1);     // crest curling over
  s.bezierCurveTo(3.8, 2.2, 3.2, 1.5, 2.4, 1.6);     // lip tucking in
  s.bezierCurveTo(1.7, 1.7, 1.6, 2.5, 0.9, 2.9);     // inside of the barrel
  s.bezierCurveTo(0.0, 3.4, -1.4, 2.6, -1.9, 1.2);   // hollow face
  s.bezierCurveTo(-2.2, 0.6, -2.4, 0.2, -2.6, 0);
  s.lineTo(-3.4, 0);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 5.2, bevelEnabled: true, bevelThickness: 0.35, bevelSize: 0.35, bevelSegments: 3, curveSegments: 36,
  });
  geo.translate(0, 0, -2.6);
  const wave = mesh(geo, M.waveFace, waveGroup);
  wave.receiveShadow = true;
}
// Foam crest: clustered white blobs marching along the lip.
const crestFoam = new THREE.Group();
waveGroup.add(crestFoam);
const crestBlobs = [];
{
  // Crest profile (x,y) of the extruded wave, swept along its depth (z).
  const crestProfile = [[-1.4, 3.75], [-0.4, 4.2], [0.8, 4.55], [2.0, 4.35], [2.9, 3.7], [3.45, 2.9], [3.5, 2.2]];
  function crestAt(u) {
    const f = u * (crestProfile.length - 1);
    const i = Math.min(Math.floor(f), crestProfile.length - 2);
    const k = f - i;
    return [crestProfile[i][0] + (crestProfile[i + 1][0] - crestProfile[i][0]) * k,
            crestProfile[i][1] + (crestProfile[i + 1][1] - crestProfile[i][1]) * k];
  }
  for (let i = 0; i < 34; i++) {
    const [px, py] = crestAt(Math.random());
    const r = 0.18 + Math.random() * 0.24;
    const b = ellipsoid(crestFoam, M.foam, r, 1.25, 0.8, 1.1,
      px + (Math.random() - 0.5) * 0.3, py + 0.48 + (Math.random() - 0.5) * 0.2, -2.5 + Math.random() * 5.0); // +bevel so blobs sit on the lip
    b.castShadow = false;
    crestBlobs.push({ m: b, base: b.scale.x, ph: Math.random() * Math.PI * 2 });
  }
  // Whitewash where the wave lands.
  for (let i = 0; i < 18; i++) {
    ellipsoid(crestFoam, M.foam, 0.14 + Math.random() * 0.2, 1.6, 0.4, 1.2,
      1.8 + Math.random() * 2.0, 0.1, -2.4 + Math.random() * 4.8).castShadow = false;
  }
}

// ============================== clouds & distant gulls ==============================
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  g.position.set(x, y, z); g.scale.setScalar(s);
  const puffs = [[0, 0, 0, 1], [0.9, -0.08, 0.1, 0.75], [-0.85, -0.1, 0, 0.7], [0.35, 0.28, -0.15, 0.62], [-0.3, 0.22, 0.15, 0.55]];
  for (const [px, py, pz, pr] of puffs) {
    const p = ellipsoid(g, M.cloud, pr, 1.25, 0.62, 0.9, px, py, pz);
    p.castShadow = false; p.receiveShadow = false;
  }
  scene.add(g); clouds.push(g);
  return g;
}
makeCloud(-9, 7.2, -14, 1.1); makeCloud(7.5, 8.0, -16, 1.3);
makeCloud(-2, 9.0, -20, 1.6); makeCloud(13, 6.6, -12, 0.8); makeCloud(-14, 6.4, -11, 0.75);

const gulls = [];
for (let i = 0; i < 3; i++) {
  const g = new THREE.Group();
  const wgeoL = new THREE.BoxGeometry(0.16, 0.03, 0.62); wgeoL.translate(0, 0, 0.31);
  const wgeoR = new THREE.BoxGeometry(0.16, 0.03, 0.62); wgeoR.translate(0, 0, -0.31);
  const wl = mesh(wgeoL, M.cloud, g); wl.castShadow = false;
  const wr = mesh(wgeoR, M.cloud, g); wr.castShadow = false;
  ellipsoid(g, M.cloud, 0.09, 1.7, 0.8, 0.8, 0, 0, 0).castShadow = false; // body along +X travel
  g.position.set(-14 + i * 6, 5.4 + i * 0.7, -11 - i * 2);
  scene.add(g);
  gulls.push({ g, wl, wr, speed: 0.55 + i * 0.14, ph: i * 2.1 });
}

// ============================== surfboard ==============================
function boardTexture() {
  const c = document.createElement("canvas"); c.width = 512; c.height = 160;
  const g = c.getContext("2d");
  const stripes = ["#e63950", "#f6c445", "#14919b", "#f6c445", "#e63950", "#f2f0e4"];
  const w = c.height / stripes.length;
  stripes.forEach((col, i) => { g.fillStyle = col; g.fillRect(0, i * w, c.width, w + 1); });
  g.fillStyle = "rgba(255,255,255,0.16)"; g.fillRect(0, 0, c.width, 10);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  // ExtrudeGeometry UVs are raw shape coords (x -1.85..1.92, y -0.54..0.54): remap to 0..1.
  tex.repeat.set(1 / 3.85, 1 / 1.12);
  tex.offset.set(0.49, 0.5);
  return tex;
}
function makeBoard() {
  const s = new THREE.Shape();
  s.moveTo(-1.85, 0);
  s.bezierCurveTo(-1.85, 0.34, -1.2, 0.52, -0.2, 0.54);
  s.bezierCurveTo(0.9, 0.54, 1.65, 0.34, 1.92, 0.02);
  s.bezierCurveTo(1.65, -0.34, 0.9, -0.54, -0.2, -0.54);
  s.bezierCurveTo(-1.2, -0.52, -1.85, -0.34, -1.85, 0);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.09, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.045, bevelSegments: 2, curveSegments: 32,
  });
  geo.rotateX(-Math.PI / 2); // outline now lies in XZ, thickness upward
  geo.translate(0, 0.1, 0);
  const mat = new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.38, metalness: 0.02 });
  const board = mesh(geo, mat, null);
  // Little fin underneath the tail.
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0); finShape.lineTo(0.3, 0); finShape.lineTo(0.12, -0.24); finShape.lineTo(0, -0.24); finShape.lineTo(0, 0);
  const fin = mesh(new THREE.ExtrudeGeometry(finShape, { depth: 0.03, bevelEnabled: false }),
    new THREE.MeshStandardMaterial({ color: 0xe63950, roughness: 0.4 }), board, -1.55, -0.02, -0.015);
  fin.castShadow = false;
  return board;
}

// ============================== pelican ==============================
// Wing: feathered outline (scalloped trailing edge) extruded thin.
// Built extending +X in shape space, then turned so the span runs along Z.
function makeWing(side) { // side: +1 front (+Z), -1 back (-Z)
  const s = new THREE.Shape();
  s.moveTo(0, 0.34);
  s.bezierCurveTo(0.55, 0.44, 1.25, 0.4, 1.78, 0.12); // leading edge to tip
  s.bezierCurveTo(1.86, 0.07, 1.84, 0.0, 1.74, -0.02);
  // Scalloped trailing edge: five primary-feather arcs back to the root.
  const tips = [[1.5, -0.14], [1.22, -0.22], [0.94, -0.27], [0.64, -0.3], [0.34, -0.31]];
  let prev = [1.74, -0.02];
  for (const [tx, ty] of tips) {
    const mx = (prev[0] + tx) / 2, my = Math.min(prev[1], ty) + 0.09;
    s.quadraticCurveTo(mx, my, tx, ty);
    prev = [tx, ty];
  }
  s.bezierCurveTo(0.12, -0.3, 0.0, -0.16, 0, 0.34);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.055, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1, curveSegments: 20,
  });
  geo.translate(0, 0, -0.028);
  geo.rotateX(-Math.PI / 2); // lay flat: span stays X, chord -> Z, thickness -> Y
  const wing = mesh(geo, M.feather, null);
  // Feather grooves: thin shaded slivers fanning toward the tip (chord now runs along Z).
  for (let i = 0; i < 4; i++) {
    const fx = 0.55 + i * 0.3;
    const f = mesh(new THREE.BoxGeometry(0.5, 0.06, 0.012), M.featherShade, wing, fx, 0.045, 0.05 + i * 0.045);
    f.rotation.y = 0.16 + i * 0.05; f.castShadow = false;
  }
  if (side < 0) wing.scale.z = -1; // mirror chord so the leading edge still faces forward
  const inner = new THREE.Group();
  inner.add(wing);
  inner.rotation.y = side > 0 ? -Math.PI / 2 : Math.PI / 2; // span -> ±Z
  const pivot = new THREE.Group(); // outer pivot: flap = rotation.x
  pivot.add(inner);
  return pivot;
}

function makeFoot() {
  // Webbed foot: fan outline with three toes, extruded flat.
  const s = new THREE.Shape();
  s.moveTo(-0.1, 0);
  s.lineTo(0.05, 0.09); s.lineTo(0.3, 0.16); s.lineTo(0.17, 0.05);
  s.lineTo(0.34, 0.02); s.lineTo(0.18, -0.05); s.lineTo(0.3, -0.15);
  s.lineTo(0.04, -0.1); s.lineTo(-0.1, -0.06); s.lineTo(-0.1, 0);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.025, bevelEnabled: true, bevelThickness: 0.008, bevelSize: 0.01, bevelSegments: 1 });
  geo.rotateX(-Math.PI / 2);
  const foot = mesh(geo, M.leg, null, 0, 0.03, 0);
  return foot;
}

const surfer = new THREE.Group();   // board + pelican, rides the swell
scene.add(surfer);
const board = makeBoard();
surfer.add(board);

const pelican = new THREE.Group();
surfer.add(pelican);

// Legs & feet stay planted on the board; the torso above them does the balancing.
for (const dz of [0.24, -0.24]) {
  const leg = mesh(new THREE.CylinderGeometry(0.045, 0.038, 0.66, 10), M.leg, pelican, dz > 0 ? 0.12 : -0.16, 0.45, dz);
  leg.rotation.z = dz > 0 ? -0.12 : 0.1;
  const foot = makeFoot();
  foot.position.set(dz > 0 ? 0.12 : -0.18, 0.1, dz);
  foot.rotation.y = dz > 0 ? -0.15 : 0.2;
  pelican.add(foot);
}

const torso = new THREE.Group();
torso.position.y = 0.72;
pelican.add(torso);

// Body: plump egg, breast forward (+X).
const body = ellipsoid(torso, M.feather, 0.62, 1.42, 0.92, 0.8, -0.02, 0.3, 0);
body.rotation.z = -0.18;
ellipsoid(torso, M.feather, 0.4, 0.9, 0.95, 0.78, 0.3, 0.3, 0); // breast
// Shaggy chest tuft.
for (let i = 0; i < 5; i++) {
  const tuft = mesh(new THREE.ConeGeometry(0.05, 0.22, 7), M.featherShade, torso,
    0.56 - Math.abs(i - 2) * 0.015, 0.42 - i * 0.07, (i - 2) * 0.07);
  tuft.rotation.z = 2.7; tuft.castShadow = false;
}
// Tail: short fan of flattened feathers at the back.
const tail = new THREE.Group();
tail.position.set(-0.62, 0.42, 0);
torso.add(tail);
for (let i = -2; i <= 2; i++) {
  const f = ellipsoid(tail, M.featherShade, 0.16, 1.5, 0.28, 0.5, -0.16, 0, i * 0.075);
  f.rotation.y = i * 0.16; f.rotation.z = 0.25;
}

// Wings spread wide for balance.
const wingFront = makeWing(1);
wingFront.position.set(-0.02, 0.62, 0.32);
wingFront.scale.setScalar(1.3);
torso.add(wingFront);
const wingBack = makeWing(-1);
wingBack.position.set(-0.02, 0.62, -0.32);
wingBack.scale.setScalar(1.3);
torso.add(wingBack);

// Neck: gentle S-curve tube rising from the breast.
const neckGroup = new THREE.Group();
neckGroup.position.set(0.28, 0.62, 0);
torso.add(neckGroup);
{
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0), new THREE.Vector3(-0.08, 0.3, 0),
    new THREE.Vector3(0.02, 0.58, 0), new THREE.Vector3(0.12, 0.8, 0),
  ]);
  mesh(new THREE.TubeGeometry(curve, 24, 0.115, 12), M.feather, neckGroup);
}
// Head, crest, beak and pouch.
const headGroup = new THREE.Group();
headGroup.position.set(0.14, 0.84, 0);
neckGroup.add(headGroup);
ellipsoid(headGroup, M.feather, 0.24, 1.12, 0.98, 0.86, 0.02, 0.08, 0);
for (let i = 0; i < 4; i++) { // crest spikes swept back
  const spike = mesh(new THREE.ConeGeometry(0.035, 0.2, 6), M.feather, headGroup, -0.08 - i * 0.035, 0.3 - i * 0.012, (i - 1.5) * 0.045);
  spike.rotation.z = 0.85 + i * 0.14;
}
for (const dz of [0.135, -0.135]) { // eyes
  ellipsoid(headGroup, M.eyeWhite, 0.075, 1, 1.15, 0.62, 0.17, 0.16, dz).castShadow = false;
  const pupil = ellipsoid(headGroup, M.eyeBlack, 0.04, 1, 1.2, 0.6, 0.215, 0.15, dz * 1.08);
  pupil.castShadow = false;
  const glint = ellipsoid(headGroup, M.eyeWhite, 0.013, 1, 1, 1, 0.24, 0.19, dz * 1.14);
  glint.castShadow = false;
}
// Upper beak: long flattened dagger, hooked tip.
const beakGroup = new THREE.Group();
beakGroup.position.set(0.2, 0.1, 0);
headGroup.add(beakGroup);
{
  const upper = ellipsoid(beakGroup, M.beak, 0.3, 1.65, 0.44, 0.5, 0.42, 0.03, 0);
  upper.rotation.z = -0.05;
  const hook = mesh(new THREE.ConeGeometry(0.05, 0.14, 8), M.beak, beakGroup, 0.92, -0.03, 0);
  hook.rotation.z = Math.PI + 0.5;
  // Nail ridge along the top of the beak.
  const ridge = ellipsoid(beakGroup, M.pouch, 0.2, 2.0, 0.16, 0.18, 0.4, 0.1, 0);
  ridge.castShadow = false;
}
// Pouch: sagging orange half-bowl swinging under the beak.
const pouchGroup = new THREE.Group();
pouchGroup.position.set(0.22, 0.02, 0);
headGroup.add(pouchGroup);
{
  const pouch = ellipsoid(pouchGroup, M.pouch, 0.3, 1.35, 0.82, 0.55, 0.36, -0.17, 0);
  pouch.rotation.z = 0.12;
  const lower = ellipsoid(pouchGroup, M.beak, 0.2, 1.9, 0.14, 0.22, 0.42, -0.02, 0); // lower mandible rim
  lower.castShadow = false;
}

// ============================== foam & spray around the board ==============================
const boardFoam = new THREE.Group();
scene.add(boardFoam);
const foamBlobs = [];
{
  for (let i = 0; i < 22; i++) {
    const a = (i / 22) * Math.PI * 2;
    const fx = Math.cos(a) * (1.75 + Math.random() * 0.35);
    const fz = Math.sin(a) * (0.62 + Math.random() * 0.3);
    const b = ellipsoid(boardFoam, M.foam, 0.08 + Math.random() * 0.09, 1.5, 0.38, 1.1, fx, -0.03, fz);
    b.castShadow = false;
    foamBlobs.push({ m: b, ph: Math.random() * Math.PI * 2, base: b.scale.x });
  }
  // Wake trailing behind the tail.
  for (let i = 0; i < 7; i++) {
    const b = ellipsoid(boardFoam, M.foam, 0.09 + Math.random() * 0.09, 1.8, 0.35, 1.0,
      -1.95 - i * 0.3, -0.03, (Math.random() - 0.5) * (0.25 + i * 0.07));
    b.castShadow = false;
    foamBlobs.push({ m: b, ph: Math.random() * Math.PI * 2, base: b.scale.x });
  }
}
function dropletTexture() {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.55, "rgba(230,250,255,0.85)");
  grad.addColorStop(1, "rgba(220,245,255,0)");
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const SPRAY = 160;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = [];
for (let i = 0; i < SPRAY; i++) {
  sprayVel.push({ vx: 0, vy: 0, vz: 0, life: Math.random() });
}
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  map: dropletTexture(), size: 0.16, transparent: true, opacity: 0.9,
  depthWrite: false, color: 0xffffff, sizeAttenuation: true,
}));
spray.frustumCulled = false;
scene.add(spray);
function respawnDrop(i, t) {
  const tail = Math.random() < 0.72;
  sprayPos[i * 3] = tail ? -1.7 + (Math.random() - 0.5) * 0.5 : 1.55 + (Math.random() - 0.5) * 0.4;
  sprayPos[i * 3 + 1] = 0.05;
  sprayPos[i * 3 + 2] = (Math.random() - 0.5) * 0.85;
  sprayVel[i].vx = tail ? -0.9 - Math.random() * 1.1 : 0.3 + Math.random() * 0.5;
  sprayVel[i].vy = 0.9 + Math.random() * 1.5;
  sprayVel[i].vz = (Math.random() - 0.5) * 1.1;
  sprayVel[i].life = 0.55 + Math.random() * 0.5;
}

// ============================== animation ==============================
const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const camAmp = reduced ? 0.25 : 1;
let lastNow = performance.now() / 1000;
let elapsed = 0;
const lookTarget = new THREE.Vector3(0.2, 1.35, 0);
let distScale = 1;
function updateDistScale() {
  const a = window.innerWidth / window.innerHeight;
  distScale = a >= 1 ? 1 : Math.min(2.0, 0.88 / Math.max(a, 0.4));
}
updateDistScale();

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now() / 1000;
  const dt = Math.min(now - lastNow, 0.05);
  lastNow = now;
  elapsed += dt;
  const t = elapsed;

  // Ocean surface follows the swell.
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    pos.setY(i, swell(x, z, t));
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // Surfer rides the same swell: heave, pitch from the slope, gentle roll.
  const h = swell(0, 0, t);
  const slope = (swell(0.9, 0, t) - swell(-0.9, 0, t)) / 1.8;
  surfer.position.set(Math.sin(t * 0.22) * 0.25, -0.42 + h + Math.sin(t * 1.7) * 0.035, Math.sin(t * 0.16) * 0.18);
  surfer.rotation.z = Math.atan(slope) * 0.85 + Math.sin(t * 0.9) * 0.03;
  surfer.rotation.x = Math.sin(t * 0.75) * 0.09;
  surfer.rotation.y = Math.sin(t * 0.3) * 0.06;

  // Balancing act: torso counter-leans, wings seesaw against the roll.
  const roll = Math.sin(t * 0.75);
  torso.rotation.x = -roll * 0.13 + Math.sin(t * 1.3) * 0.03;
  torso.rotation.z = Math.sin(t * 0.9 + 0.6) * 0.05;
  torso.position.y = 0.72 + Math.sin(t * 1.7) * 0.025;
  const flap = Math.sin(t * 2.1) * 0.14 + roll * 0.12;
  wingFront.rotation.x = -0.30 - flap;           // +Z wing: negative X-rot lifts it
  wingFront.rotation.y = 0.22;                   // slight backward sweep
  wingBack.rotation.x = 0.36 + Math.sin(t * 2.1 + 0.55) * 0.14 - roll * 0.12;
  wingBack.rotation.y = -0.22;
  body.scale.y = 0.92 + Math.sin(t * 1.7) * 0.015;

  // Head bobs with the ride; the pouch swings a beat behind.
  neckGroup.rotation.z = Math.sin(t * 1.35) * 0.06;
  headGroup.rotation.z = Math.sin(t * 1.35 + 0.7) * 0.07 - 0.03;
  headGroup.rotation.y = Math.sin(t * 0.45) * 0.14;
  pouchGroup.rotation.z = Math.sin(t * 1.35 - 0.6) * 0.13;
  pouchGroup.rotation.x = Math.sin(t * 0.9) * 0.07;
  tail.rotation.y = Math.sin(t * 2.4) * 0.14;
  tail.rotation.z = Math.sin(t * 1.8) * 0.07;

  // Foam hugging the board, breathing with the swell.
  boardFoam.position.set(surfer.position.x, surfer.position.y + 0.02, surfer.position.z);
  boardFoam.rotation.y = surfer.rotation.y;
  for (const f of foamBlobs) {
    const s = f.base * (1 + Math.sin(t * 2.6 + f.ph) * 0.22);
    f.m.scale.x = s; f.m.scale.z = s * 0.75;
  }
  for (const b of crestBlobs) {
    const s = b.base * (1 + Math.sin(t * 2.0 + b.ph) * 0.16);
    b.m.scale.x = s; b.m.scale.y = s * 0.64;
  }
  waveGroup.position.y = -0.5 + Math.sin(t * 0.6) * 0.07;

  // Spray kicked up at the nose and tail.
  for (let i = 0; i < SPRAY; i++) {
    const v = sprayVel[i];
    v.life -= dt;
    if (v.life <= 0) { respawnDrop(i, t); continue; }
    v.vy -= 3.4 * dt;
    sprayPos[i * 3] += v.vx * dt;
    sprayPos[i * 3 + 1] += v.vy * dt;
    sprayPos[i * 3 + 2] += v.vz * dt;
    if (sprayPos[i * 3 + 1] < -0.1) v.life = 0;
  }
  sprayGeo.attributes.position.needsUpdate = true;
  spray.position.set(surfer.position.x, surfer.position.y + 0.05, surfer.position.z);

  // Sky life: drifting clouds, distant gulls crossing.
  for (const c of clouds) {
    c.position.x += dt * 0.22;
    if (c.position.x > 20) c.position.x = -20;
  }
  for (const gu of gulls) {
    gu.g.position.x += dt * gu.speed;
    gu.g.position.y += Math.sin(t * 1.4 + gu.ph) * dt * 0.25;
    if (gu.g.position.x > 17) gu.g.position.x = -17;
    const w = Math.sin(t * 5 + gu.ph) * 0.5;
    gu.wl.rotation.x = -w; gu.wr.rotation.x = w; // flap around the travel axis
  }

  // Slow cinematic sway — the camera is not user-controlled.
  camera.position.x = (3.9 + Math.sin(t * 0.11) * 0.85 * camAmp) * distScale;
  camera.position.y = 2.45 * (0.7 + distScale * 0.3) + Math.sin(t * 0.17) * 0.28 * camAmp;
  camera.position.z = (7.7 + Math.sin(t * 0.07) * 0.5 * camAmp) * distScale;
  camera.lookAt(lookTarget.x + surfer.position.x * 0.5, lookTarget.y, 0);

  renderer.render(scene, camera);
}
for (let i = 0; i < SPRAY; i++) respawnDrop(i, 0);
animate();

window.addEventListener("resize", () => {
  updateDistScale();
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});



