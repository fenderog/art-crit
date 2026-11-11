import * as THREE from "three";

/* ============================================================
   Surfing Pelican — animated non-interactive Three.js scene
   Sections: config, helpers, renderer, world, pelican, state,
   input, camera, effects, main loop, boot.
   ============================================================ */

// ---------- config ----------
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const MOTION = REDUCED ? 0.22 : 1.0;
const COLORS = {
  sky: new THREE.Color(0xbfe8ef),
  water: new THREE.Color(0x1a94ad),
  waterDeep: new THREE.Color(0x0e6e8c),
  foam: new THREE.Color(0xf4fffd),
  sand: new THREE.Color(0xeed9a4),
  palm: new THREE.Color(0x2e8b57),
  feather: new THREE.Color(0xfafafa),
  featherShade: new THREE.Color(0xd9e2e6),
  beak: new THREE.Color(0xf2a541),
  pouch: new THREE.Color(0xf6b688),
  legs: new THREE.Color(0xd9762b),
  deck: new THREE.Color(0xff6b4a),
  sun: new THREE.Color(0xffd95e),
  shade: new THREE.Color(0x141310),
};

// ---------- helpers ----------
const errorBox = document.getElementById("error");
function showError(message) {
  if (!errorBox) return;
  errorBox.textContent = String(message);
  errorBox.style.display = "block";
}
window.addEventListener("error", (event) => {
  showError(`Something went wrong loading the scene.\n\n${event.message || "Unknown error"}`);
});
window.addEventListener("unhandledrejection", (event) => {
  showError(`Something went wrong loading the scene.\n\n${event.reason || "Unknown error"}`);
});
function rand(a, b) { return a + Math.random() * (b - a); }
function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
function lerp(a, b, t) { return a + (b - a) * t; }

// Wave height shared by the ocean mesh and the surfer grounding.
function waveHeight(x, z, t) {
  return (
    0.55 * Math.sin(0.55 * x + 1.5 * t) +
    0.45 * Math.sin(0.38 * z - 1.1 * t + 0.6) +
    0.22 * Math.sin(0.9 * x + 0.7 * z + 2.3 * t)
  );
}

// Soft round sprite for spray particles (drawn in code, no assets).
function makeDotTexture() {
  const c = document.createElement("canvas");
  c.width = 64; c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.55, "rgba(255,255,255,0.85)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// Striped deck texture for the surfboard.
function makeDeckTexture() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 256;
  const g = c.getContext("2d");
  const bands = ["#ff6b4a", "#fff3d6", "#19a7b8", "#173f6b", "#fff3d6", "#ff6b4a"];
  const w = c.width / bands.length;
  bands.forEach((col, i) => { g.fillStyle = col; g.fillRect(i * w, 0, w + 1, c.height); });
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = THREE.RepeatWrapping;
  return tex;
}

// ---------- renderer and scene ----------
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true });
} catch (err) {
  showError(`WebGL is not available in this browser.\n\n${err.message}`);
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById("app").prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = COLORS.sky;
scene.fog = new THREE.Fog(COLORS.sky, 26, 78);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 220);
camera.position.set(7.5, 4.4, 7.5);

const hemi = new THREE.HemisphereLight(0xdff4ff, 0xeed9a4, 0.9);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff2cf, 2.1);
sun.position.set(-10, 16, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -16; sun.shadow.camera.right = 16;
sun.shadow.camera.top = 16; sun.shadow.camera.bottom = -16;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 50;
sun.shadow.bias = -0.0004;
scene.add(sun);
scene.add(sun.target);

// ---------- world: ocean, barrel, sky props ----------
const OCEAN_W = 90, OCEAN_D = 90, SEG = 78;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_W, OCEAN_D, SEG, SEG);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: COLORS.water, roughness: 0.32, metalness: 0.05, flatShading: false,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
ocean.position.y = 0;
scene.add(ocean);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = new Float32Array(oceanPos.count * 2);
for (let i = 0; i < oceanPos.count; i++) {
  oceanBase[i * 2] = oceanPos.getX(i);
  oceanBase[i * 2 + 1] = oceanPos.getZ(i);
}

// Breaking barrel behind the rider: hollow half-cylinder along X.
const barrelMat = new THREE.MeshPhysicalMaterial({
  color: 0x2db3c6, roughness: 0.38, metalness: 0.0,
  transparent: true, opacity: 0.94, side: THREE.DoubleSide,
});
const barrelGeo = new THREE.CylinderGeometry(2.6, 2.6, 26, 28, 1, true, 0, Math.PI);
const barrel = new THREE.Mesh(barrelGeo, barrelMat);
// Cylinder axis runs along Y; tip it onto X, then spin so open half faces camera.
barrel.rotation.z = Math.PI / 2;
barrel.rotation.y = Math.PI;
barrel.position.set(0, 0.5, -5.4);
barrel.castShadow = false;
barrel.receiveShadow = true;
scene.add(barrel);

// Foam lip along the barrel crest.
const lipCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-9, 2.55, -5.4),
  new THREE.Vector3(-4.5, 3.05, -5.4),
  new THREE.Vector3(0, 3.15, -5.4),
  new THREE.Vector3(4.5, 3.05, -5.4),
  new THREE.Vector3(9, 2.55, -5.4),
]);
const lip = new THREE.Mesh(
  new THREE.TubeGeometry(lipCurve, 32, 0.26, 10, false),
  new THREE.MeshStandardMaterial({ color: COLORS.foam, roughness: 0.95 }),
);
scene.add(lip);

// Sun disc + clouds + islands (far layer, haze over distance).
const sunDisc = new THREE.Mesh(
  new THREE.SphereGeometry(1.6, 20, 14),
  new THREE.MeshBasicMaterial({ color: COLORS.sun, fog: false }),
);
sunDisc.position.set(-22, 15, -34);
scene.add(sunDisc);

const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
const clouds = [];
function makeCloud(x, y, z, s) {
  const grp = new THREE.Group();
  const blobs = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < blobs; i++) {
    const r = rand(0.7, 1.5) * s;
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 10), cloudMat);
    m.position.set(i * 1.1 - blobs * 0.55, rand(-0.15, 0.25) * s, rand(-0.4, 0.4) * s);
    grp.add(m);
  }
  grp.position.set(x, y, z);
  scene.add(grp);
  clouds.push(grp);
  return grp;
}
makeCloud(-16, 11, -20, 1.2);
makeCloud(6, 12.5, -26, 1.5);
makeCloud(18, 10, -14, 0.9);
makeCloud(-8, 13, 12, 1.1);
makeCloud(12, 9.5, 14, 0.8);

function makeIsland(x, z, s) {
  const grp = new THREE.Group();
  const hill = new THREE.Mesh(
    new THREE.ConeGeometry(3.2 * s, 2.2 * s, 10),
    new THREE.MeshStandardMaterial({ color: COLORS.sand, roughness: 0.9 }),
  );
  hill.position.y = 0.6 * s;
  grp.add(hill);
  const fringe = new THREE.Mesh(
    new THREE.ConeGeometry(3.45 * s, 1.0 * s, 10),
    new THREE.MeshStandardMaterial({ color: COLORS.palm, roughness: 0.9 }),
  );
  fringe.position.y = 0.3 * s;
  grp.add(fringe);
  grp.position.set(x, 0, z);
  scene.add(grp);
  return grp;
}
makeIsland(-14, -13, 1.0);
makeIsland(15, -17, 1.35);
makeIsland(20, 10, 0.7);

function makePalm(x, z, lean) {
  const grp = new THREE.Group();
  const trunkCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(lean * 0.6, 1.3, 0),
    new THREE.Vector3(lean * 1.2, 2.6, 0),
  ]);
  const trunk = new THREE.Mesh(
    new THREE.TubeGeometry(trunkCurve, 10, 0.12, 8),
    new THREE.MeshStandardMaterial({ color: 0x8a5a33, roughness: 0.9 }),
  );
  grp.add(trunk);
  const leafMat = new THREE.MeshStandardMaterial({ color: COLORS.palm, roughness: 0.85, side: THREE.DoubleSide });
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2;
    const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.28, 2.0, 4), leafMat);
    leaf.position.set(lean * 1.2 + Math.cos(a) * 0.9, 2.75, Math.sin(a) * 0.9);
    leaf.rotation.set(Math.sin(a) * 0.9, 0, Math.cos(a) * 0.9 + Math.PI / 2.2);
    grp.add(leaf);
  }
  grp.position.set(x, 1.0, z);
  scene.add(grp);
}
makePalm(-12.6, -11.5, 0.5);
makePalm(16.5, -14.5, -0.4);

// ---------- subject: surfboard + pelican ----------
function buildSurfboard() {
  const g = new THREE.Group();
  const L = 3.6, W = 0.92;
  // Outline in shape XY -> later laid flat with length along X.
  const s = new THREE.Shape();
  s.moveTo(L / 2, 0);
  s.quadraticCurveTo(L / 2 + 0.35, W * 0.42, L / 2 - 0.9, W / 2);
  s.lineTo(-L / 2 + 0.9, W / 2);
  s.quadraticCurveTo(-L / 2 - 0.3, W * 0.34, -L / 2, 0);
  s.quadraticCurveTo(-L / 2 - 0.3, -W * 0.34, -L / 2 + 0.9, -W / 2);
  s.lineTo(L / 2 - 0.9, -W / 2);
  s.quadraticCurveTo(L / 2 + 0.35, -W * 0.42, L / 2, 0);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.09, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.045, bevelSegments: 3,
  });
  geo.rotateX(-Math.PI / 2); // thickness becomes vertical, length stays in X
  const deck = new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({ map: makeDeckTexture(), roughness: 0.38, metalness: 0.02 }),
  );
  deck.castShadow = true;
  deck.receiveShadow = true;
  g.add(deck);
  // Fin under the tail.
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0); finShape.lineTo(0.5, 0); finShape.lineTo(0.12, -0.42); finShape.lineTo(0, 0);
  const fin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(finShape, { depth: 0.04, bevelEnabled: false }),
    new THREE.MeshStandardMaterial({ color: 0x173f6b, roughness: 0.4 }),
  );
  fin.position.set(-1.35, -0.05, -0.02);
  fin.rotation.y = Math.PI / 2;
  g.add(fin);
  return g;
}

function wingGeo() {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.quadraticCurveTo(0.8, 0.24, 1.55, 0.14);
  s.quadraticCurveTo(1.12, -0.08, 0.35, -0.22);
  s.quadraticCurveTo(0.1, -0.15, 0, 0);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.015, bevelSize: 0.02, bevelSegments: 2 });
  return geo;
}

function buildPelican() {
  const g = new THREE.Group(); // body group (leans/sways as one bird)
  const feather = new THREE.MeshStandardMaterial({ color: COLORS.feather, roughness: 0.55, metalness: 0.0 });
  const shade = new THREE.MeshStandardMaterial({ color: COLORS.featherShade, roughness: 0.7 });

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 22), feather);
  body.scale.set(0.85, 0.54, 0.58);
  body.position.set(0, 1.12, 0);
  body.castShadow = true;
  g.add(body);

  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.20, 0.62, 8), shade);
  tail.scale.set(1, 1, 0.38);
  tail.rotation.z = Math.PI / 2 - 0.5;
  tail.position.set(-0.82, 1.28, 0);
  tail.castShadow = true;
  g.add(tail);

  // S-neck from breast to head.
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.55, 1.32, 0),
    new THREE.Vector3(0.85, 1.55, 0),
    new THREE.Vector3(1.05, 1.78, 0),
    new THREE.Vector3(1.25, 2.00, 0),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 16, 0.16, 10), feather);
  neck.castShadow = true;
  g.add(neck);

  const head = new THREE.Group();
  head.position.set(1.45, 2.06, 0);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.34, 24, 18), feather);
  skull.scale.set(1.05, 0.92, 0.88);
  skull.castShadow = true;
  head.add(skull);
  const crest = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.34, 6), shade);
  crest.position.set(-0.24, 0.24, 0);
  crest.rotation.z = 0.7;
  head.add(crest);
  // Eyes + highlights.
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.3 });
  const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  [-1, 1].forEach((sgn) => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), eyeMat);
    eye.position.set(0.24, 0.06, sgn * 0.23);
    head.add(eye);
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.016, 8, 6), hlMat);
    hl.position.set(0.28, 0.09, sgn * 0.265);
    head.add(hl);
  });
  // Surfer shades over both eyes.
  const lensMat = new THREE.MeshStandardMaterial({ color: COLORS.shade, roughness: 0.25, metalness: 0.2 });
  [-1, 1].forEach((sgn) => {
    const lens = new THREE.Mesh(new THREE.SphereGeometry(0.12, 14, 10), lensMat);
    lens.scale.set(1.15, 0.78, 0.35);
    lens.position.set(0.26, 0.07, sgn * 0.24);
    head.add(lens);
  });
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.035, 0.42), lensMat);
  bridge.position.set(0.28, 0.11, 0);
  head.add(bridge);
  g.add(head);

  // Long beak + pouch, angled slightly down for the surf pose.
  const beakGroup = new THREE.Group();
  beakGroup.position.set(1.52, 2.00, 0);
  beakGroup.rotation.z = -0.10;
  const beakMat = new THREE.MeshStandardMaterial({ color: COLORS.beak, roughness: 0.5 });
  const upper = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.10, 0.21), beakMat);
  upper.position.x = 0.68;
  upper.castShadow = true;
  beakGroup.add(upper);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.075, 0.26, 8), beakMat);
  tip.scale.set(1, 1, 0.55);
  tip.rotation.z = -Math.PI / 2;
  tip.position.x = 1.42;
  beakGroup.add(tip);
  const pouch = new THREE.Mesh(
    new THREE.SphereGeometry(0.60, 20, 14),
    new THREE.MeshStandardMaterial({ color: COLORS.pouch, roughness: 0.6 }),
  );
  pouch.scale.set(1.0, 0.36, 0.38);
  pouch.position.set(0.58, -0.24, 0);
  pouch.castShadow = true;
  beakGroup.add(pouch);
  g.add(beakGroup);

  // Legs + webbed feet planted on the deck.
  const legMat = new THREE.MeshStandardMaterial({ color: COLORS.legs, roughness: 0.6 });
  [-1, 1].forEach((sgn) => {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.62, 8), legMat);
    leg.position.set(0.05, 0.62, sgn * 0.20);
    leg.castShadow = true;
    g.add(leg);
    const foot = new THREE.Mesh(new THREE.ConeGeometry(0.20, 0.42, 3), legMat);
    foot.scale.set(1, 1, 0.35);
    foot.rotation.x = Math.PI / 2;
    foot.rotation.z = sgn * 0.0;
    foot.position.set(0.18, 0.22, sgn * 0.20);
    g.add(foot);
  });

  // One wing out for balance, one folded on the back.
  const wingMat = new THREE.MeshStandardMaterial({ color: COLORS.feather, roughness: 0.6, side: THREE.DoubleSide });
  const outWing = new THREE.Mesh(wingGeo(), wingMat);
  outWing.position.set(-0.15, 1.45, 0.52);
  outWing.rotation.set(0.55, 0.35, 0.15);
  outWing.castShadow = true;
  g.add(outWing);
  const folded = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 12), shade);
  folded.scale.set(1.15, 0.28, 0.55);
  folded.position.set(-0.25, 1.38, -0.30);
  folded.rotation.set(0.25, 0, 0.35);
  g.add(folded);

  return { group: g, head, beakGroup, pouch, outWing };
}

const surfer = new THREE.Group();
const board = buildSurfboard();
surfer.add(board);
const bird = buildPelican();
surfer.add(bird.group);
scene.add(surfer);

// White wake foam tucked under the board.
const wake = new THREE.Mesh(
  new THREE.SphereGeometry(1, 18, 12),
  new THREE.MeshStandardMaterial({ color: COLORS.foam, roughness: 1, transparent: true, opacity: 0.85 }),
);
wake.scale.set(2.2, 0.18, 0.8);
wake.position.set(-0.6, 0.02, 0);
surfer.add(wake);

// ---------- effects: spray ----------
const SPRAY_N = 240;
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayVel = new Float32Array(SPRAY_N * 3);
const sprayLife = new Float32Array(SPRAY_N);
const sprayGeo = new THREE.BufferGeometry();
for (let i = 0; i < SPRAY_N; i++) { sprayLife[i] = Math.random(); }
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  size: 0.22, map: makeDotTexture(), transparent: true, opacity: 0.9,
  color: 0xffffff, depthWrite: false, sizeAttenuation: true,
}));
spray.frustumCulled = false;
scene.add(spray);
function resetParticle(i, sx, sz, sy) {
  sprayPos[i * 3] = sx + rand(-0.4, 0.4);
  sprayPos[i * 3 + 1] = sy + rand(0, 0.25);
  sprayPos[i * 3 + 2] = sz + rand(-0.5, 0.5);
  sprayVel[i * 3] = rand(-2.4, -0.8);
  sprayVel[i * 3 + 1] = rand(1.2, 3.2);
  sprayVel[i * 3 + 2] = rand(-0.9, 0.9);
  sprayLife[i] = rand(0.5, 1);
}

// ---------- state + input + camera ----------
function fitRadius(base) {
  const aspect = window.innerWidth / Math.max(1, window.innerHeight);
  if (aspect >= 1) return base;
  return base * clamp(1.0 / aspect, 1, 1.55);
}
const viewTarget = new THREE.Vector3(0, 1.5, 0);
const orbit = { theta: 0.65, phi: 1.05, radius: fitRadius(12.5) };
const orbitGoal = { ...orbit };
const VIEWS = {
  hero: { theta: 0.65, phi: 1.05, radius: 12.5 },
  side: { theta: 0.0, phi: 1.2, radius: 13.5 },
  top: { theta: 0.65, phi: 0.38, radius: 15 },
  follow: { theta: 0.45, phi: 1.0, radius: 10 },
};
let activeView = "hero";
const viewButtons = [...document.querySelectorAll("[data-view]")];
function setActiveView(name) {
  activeView = name;
  viewButtons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === name)));
  const v = VIEWS[name];
  if (v) { orbitGoal.theta = v.theta; orbitGoal.phi = v.phi; orbitGoal.radius = fitRadius(v.radius); }
}
viewButtons.forEach((b) => {
  b.addEventListener("click", () => setActiveView(b.dataset.view));
});

const dom = renderer.domElement;
dom.setAttribute("tabindex", "0");
dom.setAttribute("aria-label", "Drag to orbit the camera. Use mouse wheel or pinch to zoom.");
let dragging = false, lastX = 0, lastY = 0;
let pinchDist = 0;
const pointers = new Map();
dom.addEventListener("pointerdown", (e) => {
  dom.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  dragging = true; lastX = e.clientX; lastY = e.clientY;
  activeView = "free";
  viewButtons.forEach((b) => b.setAttribute("aria-pressed", "false"));
  if (pointers.size === 2) {
    const pts = [...pointers.values()];
    pinchDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
  }
});
dom.addEventListener("pointermove", (e) => {
  if (!pointers.has(e.pointerId)) return;
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 2) {
    const pts = [...pointers.values()];
    const d = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    if (pinchDist > 0) orbitGoal.radius = clamp(orbitGoal.radius * (pinchDist / d), 5, 17);
    pinchDist = d;
    return;
  }
  if (!dragging) return;
  orbitGoal.theta -= (e.clientX - lastX) * 0.006;
  orbitGoal.phi = clamp(orbitGoal.phi - (e.clientY - lastY) * 0.005, 0.25, 1.5);
  lastX = e.clientX; lastY = e.clientY;
});
function endPointer(e) {
  pointers.delete(e.pointerId);
  if (pointers.size === 0) dragging = false;
}
dom.addEventListener("pointerup", endPointer);
dom.addEventListener("pointercancel", endPointer);
dom.addEventListener("wheel", (e) => {
  e.preventDefault();
  orbitGoal.radius = clamp(orbitGoal.radius + e.deltaY * 0.012, 5, 17);
}, { passive: false });
dom.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") orbitGoal.theta += 0.12;
  if (e.key === "ArrowRight") orbitGoal.theta -= 0.12;
  if (e.key === "ArrowUp") orbitGoal.phi = clamp(orbitGoal.phi - 0.08, 0.25, 1.5);
  if (e.key === "ArrowDown") orbitGoal.phi = clamp(orbitGoal.phi + 0.08, 0.25, 1.5);
  if (e.key === "+" || e.key === "=") orbitGoal.radius = clamp(orbitGoal.radius - 0.5, 5, 17);
  if (e.key === "-" || e.key === "_") orbitGoal.radius = clamp(orbitGoal.radius + 0.5, 5, 17);
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- main loop ----------
let lastNow = performance.now();
let tSim = 0;
function updateOcean(t) {
  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 2], z = oceanBase[i * 2 + 1];
    oceanPos.setY(i, waveHeight(x, z, t));
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}
function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now - lastNow) / 1000, 0.05);
  lastNow = now;
  tSim += dt * MOTION;
  const t = tSim;

  updateOcean(t);

  // Ground the surfer on the live wave + slope tilt.
  const sx = Math.sin(t * 0.35) * 1.1;
  const sz = 0.6 + Math.sin(t * 0.22) * 0.4;
  surfer.position.set(sx, waveHeight(sx, sz, t) + 0.14, sz);
  const slopeX = (waveHeight(sx + 0.5, sz, t) - waveHeight(sx - 0.5, sz, t));
  const slopeZ = (waveHeight(sx, sz + 0.5, t) - waveHeight(sx, sz - 0.5, t));
  surfer.rotation.z = clamp(slopeX * 0.55, -0.35, 0.35);
  surfer.rotation.x = clamp(slopeZ * 0.5, -0.3, 0.3);
  surfer.rotation.y = 0.15 * Math.sin(t * 0.3);

  // Bird body language: lean, head bob, pouch wobble, wing balance.
  bird.group.rotation.z = Math.sin(t * 1.4) * 0.09 * MOTION;
  bird.group.rotation.x = Math.sin(t * 0.9) * 0.03 * MOTION;
  bird.head.position.y = 2.06 + Math.sin(t * 2.1) * 0.035 * MOTION;
  bird.head.rotation.y = Math.sin(t * 0.7) * 0.14 * MOTION;
  const wob = 1 + Math.sin(t * 3.3) * 0.06 * MOTION;
  bird.pouch.scale.set(1.0 * wob, 0.36 * (2 - wob) * 0.5 + 0.36 * 0.5, 0.38);
  bird.outWing.rotation.x = 0.55 + Math.sin(t * 1.8) * 0.12 * MOTION;
  bird.outWing.rotation.z = 0.15 + Math.sin(t * 1.1) * 0.08 * MOTION;
  wake.material.opacity = 0.65 + Math.sin(t * 2.6) * 0.2;

  // Spray arcs off the board's tail.
  if (!REDUCED) {
    for (let i = 0; i < SPRAY_N; i++) {
      sprayLife[i] -= dt;
      if (sprayLife[i] <= 0) resetParticle(i, sx - 1.2, sz, surfer.position.y + 0.1);
      sprayVel[i * 3 + 1] -= 5.5 * dt;
      sprayPos[i * 3] += sprayVel[i * 3] * dt;
      sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
      sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
      if (sprayPos[i * 3 + 1] < 0.05) { sprayLife[i] = 0; resetParticle(i, sx - 1.2, sz, surfer.position.y + 0.1); }
    }
    sprayGeo.attributes.position.needsUpdate = true;
  } else {
    spray.visible = false;
  }

  // Drifting clouds + lazy barrel bob.
  clouds.forEach((c, i) => {
    c.position.x += dt * 0.25 * MOTION * (i % 2 === 0 ? 1 : -0.7);
    if (c.position.x > 30) c.position.x = -30;
    if (c.position.x < -30) c.position.x = 30;
  });
  barrel.position.y = 0.5 + Math.sin(t * 0.8) * 0.12 * MOTION;

  // Camera: damped orbit, follow mode tracks the rider.
  if (activeView === "follow") viewTarget.lerp(new THREE.Vector3(sx, surfer.position.y + 1.5, sz), 0.06);
  else viewTarget.lerp(new THREE.Vector3(0, 1.6, 0), 0.08);
  orbit.theta = lerp(orbit.theta, orbitGoal.theta, 0.08);
  orbit.phi = lerp(orbit.phi, orbitGoal.phi, 0.08);
  orbit.radius = lerp(orbit.radius, orbitGoal.radius, 0.08);
  const sp = Math.sin(orbit.phi), cp = Math.cos(orbit.phi);
  camera.position.set(
    viewTarget.x + orbit.radius * sp * Math.sin(orbit.theta),
    viewTarget.y + orbit.radius * cp,
    viewTarget.z + orbit.radius * sp * Math.cos(orbit.theta),
  );
  camera.lookAt(viewTarget);

  renderer.render(scene, camera);
}

// ---------- boot ----------
setActiveView("hero");
for (let i = 0; i < SPRAY_N; i++) resetParticle(i, -1.2, 0.6, 0.4);
animate();



