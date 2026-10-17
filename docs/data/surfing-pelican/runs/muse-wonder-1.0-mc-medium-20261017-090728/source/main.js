import * as THREE from "three";

// ---------- Renderer / Scene / Camera ----------
const container = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfeef5, 38, 95);

const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(9, 4.2, 11);

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xcfeeff, 0x2a7f9e, 1.15));
const sunLight = new THREE.DirectionalLight(0xffe3b3, 2.4);
sunLight.position.set(-14, 18, 8);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -18; sunLight.shadow.camera.right = 18;
sunLight.shadow.camera.top = 18; sunLight.shadow.camera.bottom = -18;
sunLight.shadow.camera.far = 60;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
const fill = new THREE.DirectionalLight(0x9fd8ff, 0.55);
fill.position.set(12, 6, -10);
scene.add(fill);

// ---------- Helpers ----------
const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.82, metalness: 0.02, flatShading: true, ...opts });
function mesh(geo, material, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  return m;
}
function makeCanvasTexture(draw, w = 256, h = 256) {
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------- Sky dome (gradient shader, generated in code) ----------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(140, 24, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x2f9fd6) }, mid: { value: new THREE.Color(0x9fdcf2) }, low: { value: new THREE.Color(0xffe6bd) } },
    vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top; uniform vec3 mid; uniform vec3 low;
      void main(){ float h=normalize(vP).y; vec3 c=h>0.12?mix(mid,top,smoothstep(0.12,0.65,h)):mix(low,mid,smoothstep(-0.08,0.12,h)); gl_FragColor=vec4(c,1.0); }`,
  })
);
scene.add(sky);

// Sun disc + glow sprite (canvas texture)
const sunTex = makeCanvasTexture((g, w, h) => {
  const r = g.createRadialGradient(w/2, h/2, 8, w/2, h/2, w/2);
  r.addColorStop(0, "rgba(255,244,200,1)"); r.addColorStop(0.28, "rgba(255,214,130,0.95)"); r.addColorStop(1, "rgba(255,190,90,0)");
  g.fillStyle = r; g.fillRect(0, 0, w, h);
});
const sunSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: sunTex, transparent: true, depthWrite: false, fog: false }));
sunSprite.position.set(-34, 20, -58); sunSprite.scale.setScalar(34);
scene.add(sunSprite);

// ---------- Ocean ----------
const oceanGeo = new THREE.PlaneGeometry(190, 190, 88, 88);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = mesh(oceanGeo, new THREE.MeshStandardMaterial({ color: 0x1593b8, roughness: 0.55, metalness: 0.05, flatShading: true }));
ocean.position.y = -0.55; ocean.castShadow = false;
scene.add(ocean);

// ---------- Breaking wave (extruded profile) ----------
function buildWave() {
  const profile = [
    [-7.5, 0.0], [-5.5, 0.25], [-3.4, 0.9], [-1.8, 2.0], [-0.7, 3.4],
    [0.1, 4.9], [0.45, 6.1], [0.15, 7.0], [-0.9, 7.45], [-2.1, 7.0], [-2.7, 5.9],
  ].map(([z, y]) => new THREE.Vector2(z, y));
  const curve = new THREE.SplineCurve(profile);
  const pts = curve.getPoints(36);
  const W = 46, segX = 56;
  const pos = [], idx = [], uvs = [];
  for (let i = 0; i <= segX; i++) {
    const x = -W / 2 + (i / segX) * W;
    const lift = Math.sin((x / W) * Math.PI) * 0.55;
    for (let j = 0; j < pts.length; j++) {
      pos.push(x, pts[j].y + lift * (pts[j].y / 7.5), pts[j].x);
      uvs.push(i / segX * 6, j / (pts.length - 1));
    }
  }
  const cols = pts.length;
  for (let i = 0; i < segX; i++) for (let j = 0; j < cols - 1; j++) {
    const a = i * cols + j, b = a + cols;
    idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}
const waveTex = makeCanvasTexture((g, w, h) => {
  g.fillStyle = "#18a8c8"; g.fillRect(0, 0, w, h);
  g.strokeStyle = "rgba(255,255,255,0.20)"; g.lineWidth = 5;
  for (let i = -4; i < 10; i++) { g.beginPath(); g.moveTo(i * 42, h); g.bezierCurveTo(i * 42 + 30, h * 0.6, i * 42 + 6, h * 0.35, i * 42 + 38, 0); g.stroke(); }
}, 256, 256);
waveTex.wrapS = waveTex.wrapT = THREE.RepeatWrapping;
const waveGroup = new THREE.Group();
const wave = mesh(buildWave(), new THREE.MeshStandardMaterial({ map: waveTex, color: 0x7fd8ea, roughness: 0.45, flatShading: false, side: THREE.DoubleSide }));
wave.castShadow = false;
waveGroup.add(wave);
// Foamy lip along the curl
const lipPts = [];
for (let x = -22; x <= 22; x += 2) lipPts.push(new THREE.Vector3(x, 7.35 + Math.sin((x / 46) * Math.PI) * 0.55, -3.05 + Math.sin(x * 0.4) * 0.12));
const lip = mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(lipPts), 64, 0.42, 8), mat(0xffffff, { roughness: 0.95 }));
lip.castShadow = false;
waveGroup.add(lip);
waveGroup.position.set(0, -0.45, -4.2);
scene.add(waveGroup);

// ---------- Surfboard + Pelican (the rider) ----------
const rider = new THREE.Group(); // moves along the wave face
const boardGroup = new THREE.Group();
rider.add(boardGroup);
scene.add(rider);

const boardTex = makeCanvasTexture((g, w, h) => {
  g.fillStyle = "#ffcf3f"; g.fillRect(0, 0, w, h);
  g.fillStyle = "#e94f37"; g.fillRect(0, h * 0.08, w, h * 0.16); g.fillRect(0, h * 0.76, w, h * 0.16);
  g.fillStyle = "#147d9e"; g.beginPath(); g.ellipse(w/2, h/2, w*0.20, h*0.30, 0, 0, Math.PI*2); g.fill();
  g.fillStyle = "#ffffff"; g.beginPath(); g.ellipse(w/2, h/2, w*0.10, h*0.17, 0, 0, Math.PI*2); g.fill();
}, 256, 512);
const board = mesh(new THREE.SphereGeometry(1, 28, 14), new THREE.MeshStandardMaterial({ map: boardTex, roughness: 0.4 }));
board.scale.set(0.62, 0.09, 2.35);
boardGroup.add(board);
const fin = mesh(new THREE.ConeGeometry(0.16, 0.42, 4), mat(0xe94f37));
fin.position.set(0, -0.14, -1.85); fin.rotation.x = Math.PI; fin.scale.z = 0.35;
boardGroup.add(fin);

// Pelican
const pelican = new THREE.Group();
boardGroup.add(pelican);
const white = mat(0xf7f3e8), grey = mat(0xb9c4c9), orange = mat(0xf28c28), pouchMat = mat(0xffab6b, { roughness: 0.9 });
const body = mesh(new THREE.SphereGeometry(1, 24, 18), white);
body.scale.set(0.78, 0.68, 1.05); body.position.set(0, 0.72, -0.15); body.rotation.x = -0.18;
pelican.add(body);
// Tail feathers
for (let i = -1; i <= 1; i++) {
  const t = mesh(new THREE.ConeGeometry(0.16, 0.85, 5), grey);
  t.position.set(i * 0.20, 0.82, -1.12); t.rotation.x = Math.PI / 2 + 0.35; t.rotation.z = i * 0.18; t.scale.y = 1;
  pelican.add(t);
}
// S-curved neck (tube)
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 0.95, 0.55), new THREE.Vector3(0, 1.25, 0.78),
  new THREE.Vector3(0, 1.62, 0.62), new THREE.Vector3(0, 1.88, 0.92),
]);
const neck = mesh(new THREE.TubeGeometry(neckCurve, 20, 0.21, 10), white);
pelican.add(neck);
const headGroup = new THREE.Group();
headGroup.position.set(0, 1.92, 0.98);
pelican.add(headGroup);
const head = mesh(new THREE.SphereGeometry(0.34, 20, 16), white);
head.scale.set(0.92, 0.88, 1.05);
headGroup.add(head);
// Crest tuft
const crest = mesh(new THREE.ConeGeometry(0.10, 0.34, 5), grey);
crest.position.set(0, 0.30, -0.18); crest.rotation.x = -0.7;
headGroup.add(crest);
// Long beak: upper cone + pouch underneath
const beak = mesh(new THREE.ConeGeometry(0.17, 1.55, 10), orange);
beak.rotation.x = Math.PI / 2 - 0.10; beak.position.set(0, -0.04, 0.92); beak.scale.set(0.72, 1, 1.35);
headGroup.add(beak);
const pouch = mesh(new THREE.SphereGeometry(0.30, 14, 10), pouchMat);
pouch.scale.set(0.55, 0.62, 2.15); pouch.position.set(0, -0.24, 0.78); pouch.rotation.x = 0.10;
headGroup.add(pouch);
const beakTip = mesh(new THREE.SphereGeometry(0.075, 10, 8), mat(0xd96c12));
beakTip.position.set(0, -0.10, 1.68);
headGroup.add(beakTip);
// Eyes
for (const s of [-1, 1]) {
  const eye = mesh(new THREE.SphereGeometry(0.052, 10, 8), mat(0x10222b, { roughness: 0.3 }));
  eye.position.set(s * 0.235, 0.09, 0.24); eye.castShadow = false;
  headGroup.add(eye);
  const ring = mesh(new THREE.TorusGeometry(0.075, 0.018, 6, 14), mat(0x7ec8e3));
  ring.position.copy(eye.position); ring.rotation.y = s * 0.5; ring.castShadow = false;
  headGroup.add(ring);
}
// Wings (pivot at shoulder so they can flap for balance)
function makeWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(side * 0.55, 1.02, 0.05);
  const w = mesh(new THREE.SphereGeometry(1, 18, 12), white);
  w.scale.set(1.35, 0.13, 0.62); w.position.set(side * 1.05, 0, -0.12); w.rotation.y = side * -0.12;
  pivot.add(w);
  const tip = mesh(new THREE.SphereGeometry(1, 14, 10), grey);
  tip.scale.set(0.62, 0.09, 0.48); tip.position.set(side * 2.15, -0.02, -0.28);
  pivot.add(tip);
  pelican.add(pivot);
  return pivot;
}
const wingL = makeWing(-1), wingR = makeWing(1);
// Legs + big webbed feet planted on the board
for (const s of [-1, 1]) {
  const leg = mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.48, 8), orange);
  leg.position.set(s * 0.26, 0.28, s > 0 ? 0.28 : -0.28);
  pelican.add(leg);
  const foot = mesh(new THREE.SphereGeometry(0.24, 12, 8), orange);
  foot.scale.set(0.85, 0.22, 1.55); foot.position.set(s * 0.26, 0.06, (s > 0 ? 0.28 : -0.28) + 0.14);
  pelican.add(foot);
}
pelican.position.y = 0.10;

// ---------- Clouds ----------
const clouds = [];
const cloudMat = mat(0xffffff, { roughness: 1, flatShading: false });
for (let i = 0; i < 7; i++) {
  const c = new THREE.Group();
  const n = 3 + Math.floor(Math.random() * 3);
  for (let j = 0; j < n; j++) {
    const s = mesh(new THREE.SphereGeometry(1 + Math.random() * 1.1, 12, 10), cloudMat);
    s.position.set(j * 1.5 - n * 0.7, Math.random() * 0.5, Math.random() * 0.8 - 0.4);
    s.scale.y = 0.55; s.castShadow = false;
    c.add(s);
  }
  c.position.set(-55 + i * 16 + Math.random() * 6, 13 + Math.random() * 8, -38 - Math.random() * 22);
  scene.add(c); clouds.push(c);
}

// ---------- Distant sailboats + flying birds ----------
const boats = [];
function makeBoat(x, z, sailColor) {
  const b = new THREE.Group();
  const hull = mesh(new THREE.CylinderGeometry(0.55, 0.25, 2.6, 6), mat(0x8a4b2a));
  hull.rotation.z = Math.PI / 2; hull.scale.z = 0.6; b.add(hull);
  const mast = mesh(new THREE.CylinderGeometry(0.05, 0.05, 3.2, 6), mat(0x5a3a22));
  mast.position.y = 1.7; b.add(mast);
  const shape = new THREE.Shape([new THREE.Vector2(0, 0), new THREE.Vector2(0, 2.9), new THREE.Vector2(1.7, 0.3)]);
  const sail = mesh(new THREE.ShapeGeometry(shape), new THREE.MeshStandardMaterial({ color: sailColor, side: THREE.DoubleSide, roughness: 0.9 }));
  sail.position.set(0.08, 0.35, 0); b.add(sail);
  b.position.set(x, 0.1, z); b.rotation.y = 0.6;
  scene.add(b); boats.push(b); return b;
}
makeBoat(-26, -34, 0xffffff); makeBoat(24, -42, 0xff8a6b); makeBoat(8, -55, 0xfff2b0);

const birds = [];
const birdMat = mat(0x23404d, { flatShading: true });
for (let i = 0; i < 5; i++) {
  const bird = new THREE.Group();
  for (const s of [-1, 1]) {
    const w = mesh(new THREE.ConeGeometry(0.14, 1.15, 4), birdMat);
    w.position.x = s * 0.55; w.rotation.z = s * Math.PI / 2; w.scale.z = 0.25; w.castShadow = false;
    w.name = s < 0 ? "wl" : "wr";
    bird.add(w);
  }
  bird.position.set(-30 + i * 11, 11 + (i % 3) * 2.2, -26 - i * 3);
  scene.add(bird); birds.push(bird);
}

// ---------- Spray particles behind the board ----------
const SPRAY = 260;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = [];
for (let i = 0; i < SPRAY; i++) sprayVel.push(new THREE.Vector3());
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const sprayTex = makeCanvasTexture((g, w, h) => {
  const r = g.createRadialGradient(w/2, h/2, 2, w/2, h/2, w/2);
  r.addColorStop(0, "rgba(255,255,255,0.95)"); r.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = r; g.fillRect(0, 0, w, h);
}, 64, 64);
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ size: 0.55, map: sprayTex, transparent: true, depthWrite: false, opacity: 0.85 }));
spray.frustumCulled = false;
scene.add(spray);
let sprayIdx = 0;
function emitSpray(origin, count) {
  for (let n = 0; n < count; n++) {
    const i = sprayIdx; sprayIdx = (sprayIdx + 1) % SPRAY;
    sprayPos[i * 3] = origin.x + (Math.random() - 0.5) * 0.5;
    sprayPos[i * 3 + 1] = origin.y + Math.random() * 0.2;
    sprayPos[i * 3 + 2] = origin.z - 0.6 - Math.random() * 0.6;
    sprayVel[i].set((Math.random() - 0.5) * 1.6, 1.2 + Math.random() * 2.0, -1.5 - Math.random() * 2.0);
  }
}

// Foam flecks drifting on the surface near the wave
const foamGeo = new THREE.BufferGeometry();
const foamCount = 180, foamPos = new Float32Array(foamCount * 3);
for (let i = 0; i < foamCount; i++) { foamPos[i*3] = (Math.random()-0.5)*44; foamPos[i*3+1] = 0; foamPos[i*3+2] = -8 + Math.random()*10; }
foamGeo.setAttribute("position", new THREE.BufferAttribute(foamPos, 3));
const foam = new THREE.Points(foamGeo, new THREE.PointsMaterial({ size: 0.42, map: sprayTex, transparent: true, depthWrite: false, opacity: 0.6, color: 0xffffff }));
foam.frustumCulled = false;
scene.add(foam);

// ---------- Animation (fully automatic — no interaction) ----------
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const speed = reduced ? 0.35 : 1;
const clock = new THREE.Clock();
const camTarget = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05) * speed;
  const t = clock.elapsedTime * speed;

  // Ocean swell
  const p = oceanGeo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    const d = Math.hypot(x, z);
    let y = Math.sin(x * 0.16 + t * 1.1) * 0.28 + Math.cos(z * 0.13 + t * 0.85) * 0.26 + Math.sin((x + z) * 0.07 + t * 0.5) * 0.18;
    if (d < 14) y *= 0.35 + (d / 14) * 0.65; // calm the lane the surfer rides in
    p.setY(i, y);
  }
  p.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // The ride: carve left/right along the wave face, bob and lean into turns
  const carve = Math.sin(t * 0.42);
  rider.position.x = carve * 5.2;
  rider.position.z = 0.4 + Math.sin(t * 0.84) * 0.35;
  rider.position.y = 0.55 + Math.sin(t * 1.7) * 0.22 + Math.sin(t * 0.42 + 1.2) * 0.15;
  boardGroup.rotation.z = -carve * 0.22 + Math.sin(t * 1.7) * 0.04;
  boardGroup.rotation.x = Math.sin(t * 1.35) * 0.07 - 0.04;
  boardGroup.rotation.y = -carve * 0.38;

  // Pelican balancing act
  pelican.rotation.z = Math.sin(t * 1.15) * 0.07 - carve * 0.10;
  pelican.rotation.x = Math.sin(t * 0.9) * 0.04;
  pelican.position.y = 0.10 + Math.abs(Math.sin(t * 2.2)) * 0.05; // little knee-bounce
  const flap = Math.sin(t * 2.3);
  wingL.rotation.z = 0.55 + flap * 0.38 + carve * 0.18;
  wingR.rotation.z = -0.55 - Math.sin(t * 2.3 + 0.7) * 0.38 + carve * 0.18;
  wingL.rotation.x = Math.sin(t * 1.4) * 0.12;
  wingR.rotation.x = -Math.sin(t * 1.4) * 0.12;
  headGroup.rotation.y = Math.sin(t * 0.55) * 0.38; // looking around, pleased with itself
  headGroup.rotation.x = Math.sin(t * 1.8) * 0.07;
  headGroup.rotation.z = Math.sin(t * 0.8) * 0.06;
  pouch.scale.y = 0.62 + Math.sin(t * 2.0) * 0.07; // pouch wobble
  pouch.rotation.z = Math.sin(t * 1.6) * 0.05;

  // Wave breathing + scrolling stripes
  waveGroup.position.y = -0.45 + Math.sin(t * 0.7) * 0.12;
  waveGroup.rotation.z = Math.sin(t * 0.3) * 0.008;
  waveTex.offset.x = (t * 0.06) % 1;
  lip.scale.set(1, 1 + Math.sin(t * 2.6) * 0.10, 1 + Math.sin(t * 2.6) * 0.10);

  // Spray trail
  emitSpray(rider.position, 3);
  for (let i = 0; i < SPRAY; i++) {
    sprayVel[i].y -= 4.5 * dt;
    sprayPos[i * 3] += sprayVel[i].x * dt;
    sprayPos[i * 3 + 1] += sprayVel[i].y * dt;
    sprayPos[i * 3 + 2] += sprayVel[i].z * dt;
    if (sprayPos[i * 3 + 1] < -0.6) { sprayPos[i * 3 + 1] = -0.6; sprayVel[i].set(0, 0, 0); }
  }
  sprayGeo.attributes.position.needsUpdate = true;
  foam.position.y = 0.15 + Math.sin(t * 1.1) * 0.08;

  // Ambient life
  for (const c of clouds) { c.position.x += dt * 0.55; if (c.position.x > 70) c.position.x = -70; }
  boats.forEach((b, i) => { b.position.y = 0.1 + Math.sin(t * 0.8 + i * 2) * 0.22; b.rotation.z = Math.sin(t * 0.6 + i) * 0.05; b.position.x += Math.sin(t * 0.05 + i) * dt * 0.2; });
  birds.forEach((b, i) => {
    b.position.x += dt * (1.6 + i * 0.18);
    b.position.y += Math.sin(t * 2 + i) * dt * 0.35;
    if (b.position.x > 48) b.position.x = -48;
    const f = Math.sin(t * 7 + i * 1.7) * 0.55;
    const wl = b.getObjectByName("wl"), wr = b.getObjectByName("wr");
    if (wl) wl.rotation.x = f; if (wr) wr.rotation.x = -f;
  });
  sunSprite.material.opacity = 0.92 + Math.sin(t * 0.5) * 0.08;

  // Slow cinematic camera drift (non-interactive)
  const a = Math.sin(t * 0.07) * 0.38;
  camera.position.set(Math.sin(a) * 12.5, 4.1 + Math.sin(t * 0.11) * 0.7, Math.cos(a) * 11.5);
  camTarget.set(rider.position.x * 0.55, 2.0, 0);
  camera.lookAt(camTarget);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});



