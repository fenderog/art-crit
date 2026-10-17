import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xaadff0, 28, 75);

// Sky gradient generated in code
{
  const c = document.createElement("canvas"); c.width = 4; c.height = 256;
  const g = c.getContext("2d"), gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, "#4aa8d8"); gr.addColorStop(0.55, "#8fd3e8"); gr.addColorStop(1, "#d8f3e8");
  g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  scene.background = tex;
}

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 200);
camera.position.set(0, 3.2, 13);

scene.add(new THREE.HemisphereLight(0xdff6ff, 0x2a7a8a, 1.1));
const sunLight = new THREE.DirectionalLight(0xfff2cc, 2.2);
sunLight.position.set(8, 14, 6); sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -12; sunLight.shadow.camera.right = 12;
sunLight.shadow.camera.top = 12; sunLight.shadow.camera.bottom = -12;
scene.add(sunLight);

const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.65, metalness: 0, ...opts });
function mesh(geo, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, material); m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true; return m;
}

// Sun + clouds
const sun = mesh(new THREE.SphereGeometry(1.6, 24, 24), new THREE.MeshBasicMaterial({ color: 0xffdf6b }), 11, 8, -22);
sun.castShadow = false; scene.add(sun);
const clouds = new THREE.Group();
for (const [x, y, z, s] of [[-10, 7.5, -20, 1], [2, 9, -24, 1.3], [-3, 6.5, -18, 0.75], [13, 6, -18, 0.8]]) {
  const cl = new THREE.Group();
  for (let i = 0; i < 5; i++) {
    const p = mesh(new THREE.SphereGeometry(0.9 - i * 0.08, 16, 16), mat(0xffffff, { roughness: 1 }), i * 0.9 - 1.8, Math.sin(i * 1.7) * 0.22, 0);
    p.scale.y = 0.55; p.castShadow = false; cl.add(p);
  }
  cl.position.set(x, y, z); cl.scale.setScalar(s); clouds.add(cl);
}
scene.add(clouds);

// ---------- Ocean ----------
const oceanGeo = new THREE.PlaneGeometry(90, 46, 90, 44);
oceanGeo.rotateX(-Math.PI / 2);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = oceanPos.array.slice();
const ocean = new THREE.Mesh(oceanGeo, mat(0x1899b8, { roughness: 0.35, flatShading: true }));
ocean.receiveShadow = true; ocean.position.y = -1.15; scene.add(ocean);

// ---------- The big breaking wave (behind the rider) ----------
// Parametric curl: profile sweeps from flat water up and over into a lip.
function wavePoint(u, v, t) {
  // u: 0..1 across (x), v: 0..1 up the face and over the curl
  const x = (u - 0.5) * 34;
  const a = v * Math.PI * 1.15;                 // curl angle
  const R = 3.4 - v * 0.6;
  const crestY = 2.6, crestZ = -4.2;
  const y = crestY - Math.cos(a) * R + Math.sin(u * 9 + t * 1.4) * 0.08 * v;
  const z = crestZ + Math.sin(a) * R - v * 1.2;
  return [x, y, z];
}
const WAVE_U = 60, WAVE_V = 28;
const waveGeo = new THREE.BufferGeometry();
{
  const verts = [], idx = [];
  for (let j = 0; j <= WAVE_V; j++) for (let i = 0; i <= WAVE_U; i++) verts.push(...wavePoint(i / WAVE_U, j / WAVE_V, 0));
  for (let j = 0; j < WAVE_V; j++) for (let i = 0; i < WAVE_U; i++) {
    const a = j * (WAVE_U + 1) + i, b = a + 1, c = a + WAVE_U + 1, d = c + 1;
    idx.push(a, c, b, b, c, d);
  }
  waveGeo.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
  waveGeo.setIndex(idx); waveGeo.computeVertexNormals();
}
const wave = new THREE.Mesh(waveGeo, mat(0x14a8c8, { roughness: 0.3, flatShading: true, side: THREE.DoubleSide }));
wave.receiveShadow = true; scene.add(wave);

// Foam lip: bright tube following the curl edge
let foamTube;
function buildFoam(t) {
  const pts = [];
  for (let i = 0; i <= 40; i++) { const [x, y, z] = wavePoint(i / 40, 1, t); pts.push(new THREE.Vector3(x, y, z)); }
  const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 60, 0.28, 8);
  if (foamTube) { foamTube.geometry.dispose(); foamTube.geometry = geo; }
  else { foamTube = mesh(geo, mat(0xffffff, { roughness: 0.9 })); foamTube.castShadow = false; scene.add(foamTube); }
}
buildFoam(0);

// Wave face height where the board rides (matches wavePoint at v≈0.45, z front of wave)
function ridePose(x, t) {
  const u = x / 34 + 0.5;
  const [_, y, z] = wavePoint(THREE.MathUtils.clamp(u, 0, 1), 0.42, t);
  return { y: y + 0.12, z: z + 1.55 };
}

// ---------- Surfboard ----------
const board = new THREE.Group();
{
  const s = new THREE.Shape();
  s.moveTo(0, 1.65); s.bezierCurveTo(0.42, 1.1, 0.46, -0.6, 0.34, -1.5);
  s.quadraticCurveTo(0, -1.72, -0.34, -1.5); s.bezierCurveTo(-0.46, -0.6, -0.42, 1.1, 0, 1.65);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.09, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.04, bevelSegments: 2 });
  geo.rotateX(-Math.PI / 2);
  board.add(mesh(geo, mat(0xff8a3d, { roughness: 0.4 })));
  const stripe = mesh(new THREE.BoxGeometry(0.14, 0.03, 2.7), mat(0xfff3d6), 0, 0.1, 0);
  board.add(stripe);
  const fin = mesh(new THREE.BoxGeometry(0.04, 0.32, 0.42), mat(0xd6452a), 0, -0.18, -1.25);
  board.add(fin);
}

// ---------- Pelican ----------
const pelican = new THREE.Group();
const WHITE = mat(0xf7f3e8), GREY = mat(0xd9d4c8), ORANGE = mat(0xf59b23, { roughness: 0.5 }), DARK = mat(0x2b2b2b);

const body = mesh(new THREE.SphereGeometry(0.78, 24, 20), WHITE, 0, 0.85, 0);
body.scale.set(0.92, 0.88, 1.35); body.rotation.x = 0.25; pelican.add(body);
// tail
const tail = mesh(new THREE.ConeGeometry(0.34, 0.85, 12), GREY, 0, 1.05, -1.05);
tail.rotation.x = -1.15; tail.scale.set(1.2, 1, 0.45); pelican.add(tail);

// S-curved neck via tube
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 1.05, 0.75), new THREE.Vector3(0, 1.55, 0.95),
  new THREE.Vector3(0, 1.95, 0.72), new THREE.Vector3(0, 2.18, 0.95),
]);
pelican.add(mesh(new THREE.TubeGeometry(neckCurve, 20, 0.21, 12), WHITE));

// Head group (bobs)
const head = new THREE.Group(); head.position.set(0, 2.22, 1.0); pelican.add(head);
const skull = mesh(new THREE.SphereGeometry(0.34, 20, 16), WHITE); skull.scale.set(0.9, 0.95, 1.15); head.add(skull);
// crest tuft
for (let i = 0; i < 3; i++) {
  const tuft = mesh(new THREE.ConeGeometry(0.07, 0.34, 8), mat(0xf2d06b), (i - 1) * 0.1, 0.32, -0.12);
  tuft.rotation.x = -0.5; tuft.rotation.z = (i - 1) * 0.3; head.add(tuft);
}
// long beak: upper (flattened cone) + pouch below
const upperBeak = mesh(new THREE.ConeGeometry(0.16, 1.55, 12), ORANGE, 0, -0.02, 0.95);
upperBeak.rotation.x = Math.PI / 2; upperBeak.scale.set(0.75, 1, 0.55); head.add(upperBeak);
const pouch = mesh(new THREE.SphereGeometry(0.42, 16, 12), mat(0xf7b24a, { roughness: 0.55 }), 0, -0.3, 0.72);
pouch.scale.set(0.55, 0.62, 1.55); head.add(pouch);
// eyes + shades (he's cool)
for (const side of [-1, 1]) {
  head.add(mesh(new THREE.SphereGeometry(0.055, 10, 10), DARK, side * 0.27, 0.1, 0.22));
  const lens = mesh(new THREE.BoxGeometry(0.05, 0.14, 0.24), mat(0x123240, { roughness: 0.2 }), side * 0.3, 0.1, 0.24);
  head.add(lens);
}
head.add(mesh(new THREE.BoxGeometry(0.56, 0.04, 0.04), DARK, 0, 0.16, 0.3));

// Wings: flattened, tapered shapes pivoting at shoulders for balance
function makeWing(side) {
  const g = new THREE.Group(); g.position.set(side * 0.55, 1.25, 0.1);
  const shape = new THREE.Shape();
  shape.moveTo(0, 0); shape.quadraticCurveTo(side * 0.9, 0.28, side * 1.75, 0.05);
  shape.quadraticCurveTo(side * 0.9, -0.32, 0, -0.42); shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.07, bevelEnabled: false });
  const w = mesh(geo, WHITE); w.rotation.x = -0.15; g.add(w);
  const tipShape = new THREE.Shape();
  tipShape.moveTo(side * 1.15, 0.16); tipShape.quadraticCurveTo(side * 1.55, 0.2, side * 1.75, 0.05);
  tipShape.quadraticCurveTo(side * 1.4, -0.18, side * 1.15, -0.2); tipShape.closePath();
  const tip = mesh(new THREE.ExtrudeGeometry(tipShape, { depth: 0.075, bevelEnabled: false }), mat(0x3a3a3a));
  tip.rotation.x = -0.15; g.add(tip);
  pelican.add(g); return g;
}
const wingL = makeWing(-1), wingR = makeWing(1);

// Legs + big webbed feet planted on the board
for (const side of [-1, 1]) {
  const leg = mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.55, 8), mat(0x8a8a8a), side * 0.28, 0.32, side * 0.18);
  leg.rotation.x = side * 0.25; pelican.add(leg);
  const foot = mesh(new THREE.SphereGeometry(0.22, 12, 10), ORANGE, side * 0.28, 0.06, side * 0.3 + 0.08);
  foot.scale.set(1.1, 0.28, 1.5); pelican.add(foot);
}

// Rider assembly: pelican stands on board
const rider = new THREE.Group();
rider.add(board); pelican.position.y = 0.14; rider.add(pelican); scene.add(rider);

// ---------- Spray particles ----------
const SPRAY = 260;
const sprayPos = new Float32Array(SPRAY * 3), sprayVel = [];
for (let i = 0; i < SPRAY; i++) sprayVel.push(new THREE.Vector3());
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.13, transparent: true, opacity: 0.9 }));
spray.frustumCulled = false; scene.add(spray);
let sprayIdx = 0;
function emitSpray(origin, dir, n) {
  for (let k = 0; k < n; k++) {
    const i = sprayIdx = (sprayIdx + 1) % SPRAY;
    sprayPos.set([origin.x, origin.y, origin.z], i * 3);
    sprayVel[i].set(dir.x + (Math.random() - 0.5) * 1.6, Math.random() * 2.2 + 0.6, dir.z + (Math.random() - 0.5) * 1.2);
  }
}

// Distant gulls: two triangles flapping
const gulls = [];
for (let i = 0; i < 4; i++) {
  const gull = new THREE.Group();
  for (const side of [-1, 1]) {
    const w = mesh(new THREE.ConeGeometry(0.09, 0.7, 4), mat(0xffffff), side * 0.32, 0, 0);
    w.rotation.z = side * Math.PI / 2; w.castShadow = false; w.name = side < 0 ? "l" : "r"; gull.add(w);
  }
  gull.position.set(-14 + i * 3, 6 + (i % 2), -14 - i * 2);
  gulls.push(gull); scene.add(gull);
}

// ---------- Animation (fully automatic, no input) ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Ocean swell
  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    oceanPos.array[i * 3 + 1] = Math.sin(x * 0.35 + t * 1.3) * 0.22 + Math.sin(z * 0.5 - t * 1.8) * 0.18;
  }
  oceanPos.needsUpdate = true; oceanGeo.computeVertexNormals();

  // Wave face shimmer
  const wp = waveGeo.attributes.position;
  for (let j = 0; j <= WAVE_V; j++) for (let i = 0; i <= WAVE_U; i++) {
    const [x, y, z] = wavePoint(i / WAVE_U, j / WAVE_V, t);
    wp.setXYZ(j * (WAVE_U + 1) + i, x, y, z);
  }
  wp.needsUpdate = true; waveGeo.computeVertexNormals();
  if ((t * 10 | 0) % 3 === 0) buildFoam(t);

  // Rider carves back and forth along the face
  const carve = Math.sin(t * 0.45);              // -1..1 across the wave
  const x = carve * 6.5;
  const { y, z } = ridePose(x, t);
  const speed = Math.cos(t * 0.45);              // direction of travel
  const bob = Math.sin(t * 2.1) * 0.12;
  // occasional hop off the lip
  const hopCycle = (t % 9); const hop = hopCycle > 7.6 ? Math.sin((hopCycle - 7.6) / 1.4 * Math.PI) * 0.9 : 0;
  rider.position.set(x, y + bob + hop, z);
  rider.rotation.set(
    -0.32 + Math.sin(t * 2.1) * 0.05 - hop * 0.25,   // pitch down the face
    speed * 0.55,                                     // face travel direction
    -carve * 0.08 + Math.sin(t * 1.7) * 0.04          // lean into turns
  );

  // Pelican balancing act
  wingL.rotation.z = 0.55 + Math.sin(t * 2.3) * 0.28 + hop * 0.7;
  wingR.rotation.z = -0.55 - Math.sin(t * 2.3 + 0.6) * 0.28 - hop * 0.7;
  wingL.rotation.y = Math.sin(t * 1.4) * 0.15; wingR.rotation.y = -Math.sin(t * 1.4) * 0.15;
  head.rotation.set(Math.sin(t * 2.6) * 0.08, speed * 0.35, Math.sin(t * 1.9) * 0.06);
  head.position.y = 2.22 + Math.sin(t * 2.6) * 0.04;
  pouch.scale.y = 0.62 + Math.sin(t * 3.1) * 0.07;  // pouch wobble
  pouch.rotation.x = Math.sin(t * 3.1) * 0.06;
  tail.rotation.z = Math.sin(t * 2.8) * 0.12;
  pelican.rotation.z = Math.sin(t * 2.3) * 0.05;

  // Spray off the board's tail
  const tailWorld = new THREE.Vector3(0, 0, -1.5).applyEuler(rider.rotation).add(rider.position);
  emitSpray(tailWorld, new THREE.Vector3(-speed * 2.2, 0, -1), hop > 0.1 ? 1 : 4);
  for (let i = 0; i < SPRAY; i++) {
    sprayVel[i].y -= 5.5 * 0.016;
    sprayPos[i * 3] += sprayVel[i].x * 0.016; sprayPos[i * 3 + 1] += sprayVel[i].y * 0.016; sprayPos[i * 3 + 2] += sprayVel[i].z * 0.016;
    if (sprayPos[i * 3 + 1] < -1.2) sprayPos[i * 3 + 1] = -10;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Clouds drift, gulls flap across
  clouds.children.forEach((c, i) => { c.position.x += 0.002 * (i + 1) * 0.4; if (c.position.x > 20) c.position.x = -20; });
  gulls.forEach((g, i) => {
    g.position.x += 0.03 + i * 0.004; if (g.position.x > 18) g.position.x = -18;
    g.position.y += Math.sin(t * 2 + i) * 0.004;
    g.children.forEach(w => { w.rotation.x = Math.sin(t * 7 + i * 2) * 0.5; });
  });

  // Gentle cinematic camera sway (no controls)
  camera.position.set(Math.sin(t * 0.18) * 1.6 + x * 0.18, 3.1 + Math.sin(t * 0.3) * 0.3, 12.5);
  camera.lookAt(x * 0.55, 1.4, 0);

  renderer.render(scene, camera);
}
animate();

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
