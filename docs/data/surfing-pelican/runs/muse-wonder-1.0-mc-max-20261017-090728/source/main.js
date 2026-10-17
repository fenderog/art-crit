import * as THREE from "three";

// Animated, non-interactive surfing pelican.
// Everything is procedural: no external assets, no controls, no storage.
const container = document.getElementById("scene");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const TIME_SCALE = reducedMotion ? 0.35 : 1;

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
scene.fog = new THREE.Fog(0xa8d8ea, 34, 95);

const camera = new THREE.PerspectiveCamera(
  42, window.innerWidth / window.innerHeight, 0.1, 300,
);
camera.position.set(7.2, 3.6, 9.4);

const hemi = new THREE.HemisphereLight(0xcfefff, 0x2f7f7a, 1.15);
scene.add(hemi);
const sunLight = new THREE.DirectionalLight(0xffe3b3, 2.4);
sunLight.position.set(-14, 18, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -16; sunLight.shadow.camera.right = 16;
sunLight.shadow.camera.top = 16; sunLight.shadow.camera.bottom = -16;
sunLight.shadow.camera.far = 60;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// --- Sky dome: vertical gradient, warm at the horizon --------------------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(140, 32, 18),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x5fb6dd) },
      mid: { value: new THREE.Color(0x9fd4ec) },
      low: { value: new THREE.Color(0xfff0d2) },
    },
    vertexShader: `
      varying vec3 vP;
      void main(){ vP = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `
      uniform vec3 top; uniform vec3 mid; uniform vec3 low;
      varying vec3 vP;
      void main(){
        float h = normalize(vP).y;
        vec3 c = h > 0.18 ? mix(mid, top, smoothstep(0.18, 0.75, h))
                          : mix(low, mid, smoothstep(-0.06, 0.18, h));
        gl_FragColor = vec4(c, 1.0);
      }`,
  }),
);
scene.add(sky);

const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(3.2, 40),
  new THREE.MeshBasicMaterial({ color: 0xffdf8a, fog: false }),
);
sunDisc.position.set(-38, 20, -62);
sunDisc.lookAt(camera.position);
scene.add(sunDisc);
const sunHalo = new THREE.Mesh(
  new THREE.CircleGeometry(5.4, 40),
  new THREE.MeshBasicMaterial({ color: 0xffe9b0, transparent: true, opacity: 0.35, fog: false }),
);
sunHalo.position.copy(sunDisc.position).z -= 0.5;
sunHalo.lookAt(camera.position);
scene.add(sunHalo);

function std(color, opts = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0.0, ...opts });
}
function shadowed(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }

// --- Ocean: one shared wave function drives mesh + surfer pose -----------
function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.26 + t * 1.05) * 0.34 +
    Math.cos(z * 0.31 + t * 0.78) * 0.27 +
    Math.sin((x + z) * 0.14 + t * 0.52) * 0.24 +
    Math.sin(x * 0.07 - t * 0.38) * 0.42
  );
}
const OCEAN_SIZE = 110, OCEAN_SEG = 118;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshPhongMaterial({
    color: 0x11999e, shininess: 90, specular: 0x99ddee, flatShading: true,
  }),
);
ocean.receiveShadow = true;
scene.add(ocean);

function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3], z = oceanBase[i * 3 + 2];
    pos.setY(i, waveHeight(x, z, t));
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// --- Surfboard: pointed nose (-X = direction of travel), rounded tail ----
function buildBoard() {
  const s = new THREE.Shape();
  s.moveTo(-1.85, 0);
  s.bezierCurveTo(-1.55, 0.46, -0.7, 0.52, 0.4, 0.5);
  s.bezierCurveTo(1.35, 0.48, 1.8, 0.3, 1.8, 0);
  s.bezierCurveTo(1.8, -0.3, 1.35, -0.48, 0.4, -0.5);
  s.bezierCurveTo(-0.7, -0.52, -1.55, -0.46, -1.85, 0);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.11, bevelEnabled: true, bevelThickness: 0.045, bevelSize: 0.05, bevelSegments: 2,
  });
  geo.rotateX(-Math.PI / 2);
  const board = shadowed(new THREE.Mesh(geo, std(0xff6b4a, { roughness: 0.55 })));
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.9, 0.03, 0.2), std(0xfff3d6, { roughness: 0.6 }),
  );
  stripe.position.set(-0.1, 0.13, 0);
  board.add(stripe);
  const fin = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.42, 4), std(0x12343b));
  fin.rotation.z = Math.PI; fin.position.set(1.35, -0.22, 0); fin.scale.z = 0.25;
  board.add(fin);
  return board;
}

// --- Pelican: stands sideways on the board, facing +Z (the camera) -------
// Returns every part the animation loop needs to pose.
function buildPelican() {
  const white = std(0xfff8ec, { roughness: 0.95 });
  const grey = std(0x46545e, { roughness: 0.9 });
  const orange = std(0xff8c2e, { roughness: 0.6 });
  const pouchMat = std(0xffb35c, { roughness: 0.7 });
  const root = new THREE.Group();

  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.62, 28, 22), white));
  body.scale.set(1.05, 0.92, 0.78);
  body.position.set(0, 0.98, 0.05);
  root.add(body);
  const breast = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.42, 22, 18), white));
  breast.scale.set(0.9, 1.0, 0.7);
  breast.position.set(0, 0.92, 0.38);
  root.add(breast);

  const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.85, 10), grey));
  tail.rotation.x = Math.PI / 2 + 0.5;
  tail.position.set(0, 1.12, -0.62);
  tail.scale.set(1.25, 1, 0.4);
  root.add(tail);

  // Wings: pivot at the shoulder so rotation.z reads as a flap.
  function wing(side) { // side: -1 toward nose, +1 toward tail
    const g = new THREE.Group();
    g.position.set(side * 0.5, 1.28, 0.02);
    const arm = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.5, 18, 14), white));
    arm.scale.set(1.5, 0.22, 0.62);
    arm.position.x = side * 0.62;
    g.add(arm);
    for (let i = 0; i < 3; i++) {
      const feather = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.62, 6), grey));
      feather.rotation.z = side * (Math.PI / 2 + 0.12 * i);
      feather.position.set(side * (1.25 + i * 0.1), -0.04 * i, -0.16 + i * 0.16);
      feather.scale.z = 0.35;
      g.add(feather);
    }
    root.add(g);
    return g;
  }
  const wingL = wing(-1), wingR = wing(1);

  // Neck + head + the unmistakable long beak and pouch.
  const headGroup = new THREE.Group();
  headGroup.position.set(0, 1.42, 0.28);
  root.add(headGroup);
  const neck = shadowed(new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, 0.21, 0.62, 12), white,
  ));
  neck.rotation.x = 0.38; neck.position.set(0, 0.22, 0.1);
  headGroup.add(neck);
  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.31, 24, 18), white));
  head.scale.set(0.92, 0.88, 1.05);
  head.position.set(0, 0.58, 0.28);
  headGroup.add(head);
  for (let i = 0; i < 3; i++) { // crest tuft
    const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.3, 6), std(0xffd23e));
    tuft.rotation.x = -0.7 - i * 0.22;
    tuft.position.set((i - 1) * 0.09, 0.84, 0.08 - i * 0.03);
    headGroup.add(tuft);
  }
  const beak = new THREE.Group();
  beak.position.set(0, 0.52, 0.52);
  headGroup.add(beak);
  const upper = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.13, 1.3, 10), orange));
  upper.rotation.x = Math.PI / 2;
  upper.position.z = 0.6; upper.scale.y = 1; upper.scale.x = 0.75;
  beak.add(upper);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.22, 8), std(0xe86a17));
  hook.rotation.x = Math.PI; hook.position.set(0, -0.05, 1.28);
  beak.add(hook);
  const pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.3, 18, 14), pouchMat));
  pouch.scale.set(0.62, 0.72, 1.7);
  pouch.position.set(0, -0.2, 0.55);
  beak.add(pouch);
  const eyeMat = std(0x1a2226, { roughness: 0.3 });
  for (const sx of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), eyeMat);
    eye.position.set(sx * 0.24, 0.66, 0.44);
    headGroup.add(eye);
    const brow = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), std(0xffe9a8));
    brow.scale.set(1, 0.55, 1);
    brow.position.set(sx * 0.25, 0.74, 0.42);
    headGroup.add(brow);
  }

  // Scarf: one touch of character, flutters in the wind.
  const scarf = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.075, 10, 22), std(0xe94f37, { roughness: 0.7 }));
  scarf.rotation.x = Math.PI / 2 - 0.35;
  scarf.position.set(0, 1.88, 0.32);
  root.add(scarf);
  const scarfTail = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.5, 0.04), std(0xe94f37)));
  scarfTail.position.set(-0.28, 1.72, 0.18);
  root.add(scarfTail);

  // Legs + webbed feet planted along the board.
  const legs = [];
  for (const fx of [-0.52, 0.55]) {
    const leg = new THREE.Group();
    leg.position.set(fx, 0.62, 0.06);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.065, 0.55, 8), orange);
    shin.position.y = -0.2;
    leg.add(shin);
    const foot = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.17, 0.42, 8), orange));
    foot.rotation.x = Math.PI / 2; foot.scale.set(1.25, 1, 0.28);
    foot.position.set(0, -0.5, 0.1);
    leg.add(foot);
    root.add(leg);
    legs.push(leg);
  }
  return { root, wingL, wingR, headGroup, beak, pouch, scarfTail, legs, body };
}

// --- Assemble the surfer --------------------------------------------------
const surfer = new THREE.Group();
scene.add(surfer);
const board = buildBoard();
board.position.y = 0.12;
surfer.add(board);
const pelican = buildPelican();
pelican.root.position.y = 0.18;
surfer.add(pelican.root);

// --- Set dressing: clouds, islands with palms, gulls ----------------------
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const m = std(0xffffff, { roughness: 1 });
  for (const [px, py, pz, r] of [[0, 0, 0, 1], [1.1, -0.12, 0.2, 0.75], [-1.05, -0.1, -0.15, 0.7], [0.35, 0.35, -0.2, 0.65], [-0.4, 0.28, 0.25, 0.55]]) {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 10), m);
    puff.position.set(px, py, pz); puff.scale.y = 0.62;
    g.add(puff);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g); clouds.push(g);
  return g;
}
makeCloud(-16, 10.5, -26, 1.7); makeCloud(10, 12, -32, 2.2);
makeCloud(22, 9, -18, 1.2); makeCloud(-26, 12.5, -14, 1.4);
makeCloud(2, 13.5, -38, 2.6); makeCloud(-8, 9, -30, 1.0);

function makeIsland(x, z, s) {
  const g = new THREE.Group();
  const hill = new THREE.Mesh(new THREE.SphereGeometry(3.2, 18, 12), std(0x2e8b74));
  hill.scale.set(1.5, 0.42, 1); hill.position.y = -0.5;
  g.add(hill);
  const sand = new THREE.Mesh(new THREE.CylinderGeometry(4.6, 5.1, 0.5, 20), std(0xf2d492));
  sand.position.y = -0.75; g.add(sand);
  for (const px of [-1.6, 1.4]) {
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 2.6, 7), std(0x8a6b46));
    trunk.position.set(px, 1.1, 0.4); trunk.rotation.z = px * 0.08;
    g.add(trunk);
    for (let i = 0; i < 6; i++) {
      const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.22, 1.9, 5), std(0x2fa36b));
      const a = (i / 6) * Math.PI * 2;
      leaf.position.set(px + Math.cos(a) * 0.65, 2.55, 0.4 + Math.sin(a) * 0.65);
      leaf.rotation.set(Math.sin(a) * 1.15, 0, -Math.cos(a) * 1.15);
      g.add(leaf);
    }
  }
  g.position.set(x, 0, z); g.scale.setScalar(s);
  scene.add(g);
}
makeIsland(-24, -30, 1.15);
makeIsland(27, -36, 1.5);

const gulls = [];
function makeGull(radius, height, speed, phase) {
  const g = new THREE.Group();
  const m = std(0xffffff, { roughness: 1 });
  const bodyG = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8), m);
  bodyG.scale.set(1, 0.7, 1.9); g.add(bodyG);
  const wings = [];
  for (const sx of [-1, 1]) {
    const w = new THREE.Group(); w.position.x = sx * 0.1;
    const wm = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.03, 0.28), m);
    wm.position.x = sx * 0.45; w.add(wm); g.add(w); wings.push(w);
  }
  scene.add(g);
  gulls.push({ g, wings, radius, height, speed, phase });
}
makeGull(15, 8.5, 0.16, 0); makeGull(19, 10, -0.12, 2.1);
makeGull(12, 7.2, 0.2, 4.0); makeGull(22, 11, 0.1, 1.2);

// --- Spray particles + expanding foam rings -------------------------------
const SPRAY_N = 260;
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayVel = new Float32Array(SPRAY_N * 3);
const sprayLife = new Float32Array(SPRAY_N);
for (let i = 0; i < SPRAY_N; i++) { sprayLife[i] = Math.random(); sprayPos[i * 3 + 1] = -10; }
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  color: 0xffffff, size: 0.17, transparent: true, opacity: 0.85, depthWrite: false,
}));
scene.add(spray);
let sprayCursor = 0;
function emitSpray(origin, count, spread) {
  for (let n = 0; n < count; n++) {
    const i = sprayCursor; sprayCursor = (sprayCursor + 1) % SPRAY_N;
    sprayLife[i] = 0.55 + Math.random() * 0.45;
    sprayPos[i * 3] = origin.x + (Math.random() - 0.5) * 0.5;
    sprayPos[i * 3 + 1] = origin.y + Math.random() * 0.12;
    sprayPos[i * 3 + 2] = origin.z + (Math.random() - 0.5) * 0.7;
    sprayVel[i * 3] = 1.6 + Math.random() * 1.8; // trailing +X, away from travel
    sprayVel[i * 3 + 1] = 1.1 + Math.random() * 1.7;
    sprayVel[i * 3 + 2] = (Math.random() - 0.5) * spread;
  }
}
const foamRings = [];
const foamMat = () => new THREE.MeshBasicMaterial({
  color: 0xffffff, transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide,
});
for (let i = 0; i < 12; i++) {
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.75, 1, 28), foamMat());
  ring.rotation.x = -Math.PI / 2;
  ring.userData.phase = i / 12;
  scene.add(ring); foamRings.push(ring);
}

// --- Animation: the whole show runs itself, no input needed --------------
const clock = new THREE.Clock();
const camTarget = new THREE.Vector3(0, 1.2, 0);
let simT = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  simT += dt * TIME_SCALE;
  const t = simT;

  updateOcean(t);

  // Carve path: the surfer sweeps side to side while the swell rolls under.
  const sx = Math.sin(t * 0.32) * 3.1;
  const sz = Math.sin(t * 0.21 + 1.3) * 1.7;
  const sy = waveHeight(sx, sz, t);
  surfer.position.set(sx, sy + 0.22, sz);
  const e = 0.65;
  const slopeX = (waveHeight(sx + e, sz, t) - waveHeight(sx - e, sz, t)) / (2 * e);
  const slopeZ = (waveHeight(sx, sz + e, t) - waveHeight(sx, sz - e, t)) / (2 * e);
  surfer.rotation.z = THREE.MathUtils.clamp(Math.atan(slopeX) * 0.9, -0.5, 0.5);
  surfer.rotation.x = THREE.MathUtils.clamp(-Math.atan(slopeZ) * 0.9, -0.45, 0.45);
  surfer.rotation.y = Math.cos(t * 0.32) * 0.24 + Math.sin(t * 0.13) * 0.08;

  // Pelican body language: crouch, lean into the carve, flap for balance.
  const carveLean = Math.cos(t * 0.32);
  pelican.root.position.y = 0.18 + Math.sin(t * 2.0) * 0.035;
  pelican.root.rotation.z = carveLean * 0.14;
  pelican.root.rotation.x = -0.06 + Math.sin(t * 0.9) * 0.05;
  const flap = Math.sin(t * 2.3) * 0.44;
  const balance = Math.sin(t * 0.64 + 0.6) * 0.16;
  pelican.wingL.rotation.z = -0.14 - flap - balance;
  pelican.wingR.rotation.z = 0.14 + flap * 0.85 - balance;
  pelican.wingL.rotation.x = Math.sin(t * 1.7) * 0.08;
  pelican.wingR.rotation.x = Math.sin(t * 1.7 + 0.9) * 0.08;
  pelican.headGroup.rotation.y = Math.sin(t * 0.55) * 0.3;
  pelican.headGroup.rotation.x = 0.04 + Math.sin(t * 1.7) * 0.06;
  pelican.beak.rotation.x = Math.sin(t * 1.3 + 1.0) * 0.055;
  const pouchPulse = Math.sin(t * 1.8) * 0.07;
  pelican.pouch.scale.set(0.62, 0.72 + pouchPulse, 1.7 + pouchPulse * 1.4);
  pelican.scarfTail.rotation.z = 0.45 + Math.sin(t * 3.1) * 0.38;
  pelican.scarfTail.rotation.x = Math.sin(t * 2.4) * 0.22;
  pelican.legs[0].rotation.x = Math.sin(t * 2.0) * 0.07;
  pelican.legs[1].rotation.x = Math.sin(t * 2.0 + Math.PI) * 0.07;
  pelican.body.position.y = 0.98 + Math.sin(t * 2.0 + 0.4) * 0.02;

  // Spray kicked up off the tail of the board.
  emitSpray(new THREE.Vector3(sx + 1.7, sy + 0.3, sz), 3, 1.6);
  if (Math.sin(t * 2.0) > 0.72) emitSpray(new THREE.Vector3(sx - 1.6, sy + 0.28, sz), 2, 1.1);
  for (let i = 0; i < SPRAY_N; i++) {
    if (sprayLife[i] <= 0) continue;
    sprayLife[i] -= dt * 0.85;
    sprayVel[i * 3 + 1] -= 4.6 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
    if (sprayLife[i] <= 0) sprayPos[i * 3 + 1] = -10;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  for (const ring of foamRings) {
    const p = (t * 0.22 + ring.userData.phase) % 1;
    const fx = sx + 1.3 + p * 4.5, fz = sz + Math.sin(p * 5 + ring.userData.phase * 9) * 0.3;
    ring.position.set(fx, waveHeight(fx, fz, t) + 0.07, fz);
    const s = 0.6 + p * 3.4;
    ring.scale.set(s, s, s);
    ring.material.opacity = (1 - p) * 0.42;
  }

  for (const c of clouds) {
    c.position.x += dt * 0.22 * TIME_SCALE;
    if (c.position.x > 46) c.position.x = -46;
  }
  for (const gu of gulls) {
    const a = gu.phase + t * gu.speed;
    gu.g.position.set(Math.cos(a) * gu.radius, gu.height + Math.sin(t * 0.9 + gu.phase) * 0.5, Math.sin(a) * gu.radius - 12);
    const a2 = a + 0.02 * Math.sign(gu.speed);
    gu.g.lookAt(Math.cos(a2) * gu.radius, gu.g.position.y, Math.sin(a2) * gu.radius - 12);
    const gf = Math.sin(t * 6 + gu.phase) * 0.55;
    gu.wings[0].rotation.z = gf; gu.wings[1].rotation.z = -gf;
  }

  // Slow cinematic drift — the camera watches, it is never steered.
  camera.position.set(
    7.2 + Math.sin(t * 0.11) * 1.3,
    3.6 + Math.sin(t * 0.17) * 0.4,
    9.4 + Math.cos(t * 0.09) * 0.9,
  );
  camTarget.lerp(new THREE.Vector3(sx * 0.55, sy + 1.25, sz * 0.55), 0.04);
  camera.lookAt(camTarget);
  sunDisc.lookAt(camera.position);
  sunHalo.lookAt(camera.position);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});




