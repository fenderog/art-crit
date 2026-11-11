import * as THREE from "three";

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const MOTION = reducedMotion ? 0.35 : 1;

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe8ec, 26, 75);

const camera = new THREE.PerspectiveCamera(44, window.innerWidth / window.innerHeight, 0.1, 240);
function fitCamera() {
  const aspect = window.innerWidth / window.innerHeight;
  camera.aspect = aspect;
  camera.fov = aspect < 0.8 ? 64 : 44;
  camera.updateProjectionMatrix();
}

// ---------- Sky dome (gradient + sun glow) ----------
const skyGeo = new THREE.SphereGeometry(110, 32, 24);
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  depthWrite: false,
  uniforms: {
    topColor: { value: new THREE.Color(0x4aa8dc) },
    midColor: { value: new THREE.Color(0xbfe6f2) },
    botColor: { value: new THREE.Color(0xfdf3d8) },
    sunDir: { value: new THREE.Vector3(0.55, 0.62, 0.35).normalize() },
  },
  vertexShader: /* glsl */ `
    varying vec3 vDir;
    void main() {
      vDir = normalize(position);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    varying vec3 vDir;
    uniform vec3 topColor;
    uniform vec3 midColor;
    uniform vec3 botColor;
    uniform vec3 sunDir;
    void main() {
      float h = clamp(vDir.y, -0.2, 1.0);
      vec3 col = mix(botColor, midColor, smoothstep(-0.1, 0.22, h));
      col = mix(col, topColor, smoothstep(0.18, 0.72, h));
      float sunAmt = pow(max(dot(normalize(vDir), normalize(sunDir)), 0.0), 90.0);
      col += vec3(1.0, 0.82, 0.45) * sunAmt * 0.85;
      float glow = pow(max(dot(normalize(vDir), normalize(sunDir)), 0.0), 6.0);
      col += vec3(1.0, 0.9, 0.6) * glow * 0.16;
      gl_FragColor = vec4(col, 1.0);
    }
  `,
});
scene.add(new THREE.Mesh(skyGeo, skyMat));

// Sun disc
const sun = new THREE.Mesh(
  new THREE.SphereGeometry(3.2, 24, 16),
  new THREE.MeshBasicMaterial({ color: 0xfff2b8, fog: false })
);
sun.position.set(38, 44, 24);
scene.add(sun);

// ---------- Lights ----------
scene.add(new THREE.HemisphereLight(0xcfefff, 0x0d5a68, 0.85));

const sunLight = new THREE.DirectionalLight(0xfff1c9, 2.4);
sunLight.position.set(16, 22, 12);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -14;
sunLight.shadow.camera.right = 14;
sunLight.shadow.camera.top = 14;
sunLight.shadow.camera.bottom = -14;
sunLight.shadow.camera.far = 70;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xbfe8ff, 0.55);
fillLight.position.set(-10, 8, -14);
scene.add(fillLight);

// ---------- Ocean ----------
const OCEAN_SIZE = 150;
const OCEAN_SEG = 96;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1293a5,
  roughness: 0.42,
  metalness: 0.05,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

const oceanPos = oceanGeo.attributes.position;
const oceanBase = new Float32Array(oceanPos.count * 3);
for (let i = 0; i < oceanPos.count; i++) {
  oceanBase[i * 3] = oceanPos.getX(i);
  oceanBase[i * 3 + 1] = 0;
  oceanBase[i * 3 + 2] = oceanPos.getZ(i);
}

function waveHeight(x, z, t) {
  const damp = Math.max(0, 1 - Math.hypot(x, z) / 78);
  return (
    damp *
    (Math.sin(x * 0.32 + t * 1.25) * 0.34 +
      Math.sin(z * 0.48 - t * 0.85) * 0.24 +
      Math.sin((x + z) * 0.2 + t * 0.55) * 0.46 +
      Math.sin(x * 0.9 - t * 2.2) * 0.08)
  );
}

function updateOcean(t) {
  for (let i = 0; i < oceanPos.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    oceanPos.setY(i, waveHeight(x, z, t));
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}
updateOcean(0);

// ---------- Shared materials ----------
const MAT = {
  white: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.55 }),
  featherShade: new THREE.MeshStandardMaterial({ color: 0xe8eef0, roughness: 0.65 }),
  blackTip: new THREE.MeshStandardMaterial({ color: 0x1c2428, roughness: 0.5 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xff7a00, roughness: 0.38 }),
  beakTip: new THREE.MeshStandardMaterial({ color: 0xd95500, roughness: 0.4 }),
  pouch: new THREE.MeshStandardMaterial({
    color: 0xffd9a8,
    roughness: 0.5,
    transparent: true,
    opacity: 0.92,
  }),
  legs: new THREE.MeshStandardMaterial({ color: 0xff8a1d, roughness: 0.45 }),
  board: new THREE.MeshStandardMaterial({ color: 0xff5a49, roughness: 0.35 }),
  boardStripe: new THREE.MeshStandardMaterial({ color: 0xffe066, roughness: 0.35 }),
  foam: new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.9,
    transparent: true,
    opacity: 0.85,
  }),
  dark: new THREE.MeshStandardMaterial({ color: 0x10181c, roughness: 0.3 }),
};

// ---------- Surfboard (pointed oval extrude) ----------
function buildBoard() {
  const L = 3.6, W = 0.95;
  const shape = new THREE.Shape();
  shape.moveTo(-L / 2, 0);
  shape.bezierCurveTo(-L / 2 + 0.25, W / 2, -L / 2 + 1.1, W / 2, 0, W / 2);
  shape.bezierCurveTo(L / 2 - 1.1, W / 2, L / 2 - 0.25, W / 2, L / 2, 0);
  shape.bezierCurveTo(L / 2 - 0.25, -W / 2, L / 2 - 1.1, -W / 2, 0, -W / 2);
  shape.bezierCurveTo(-L / 2 + 1.1, -W / 2, -L / 2 + 0.25, -W / 2, -L / 2, 0);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.09,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.04,
    bevelSegments: 2,
  });
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, -0.05, 0);
  const board = new THREE.Mesh(geo, MAT.board);
  board.castShadow = true;
  board.receiveShadow = true;

  const group = new THREE.Group();
  group.add(board);

  // Yellow stringer stripe
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(3.1, 0.035, 0.1), MAT.boardStripe);
  stripe.position.y = 0.085;
  group.add(stripe);

  // Traction pad
  const pad = new THREE.Mesh(
    new THREE.BoxGeometry(0.8, 0.03, 0.55),
    new THREE.MeshStandardMaterial({ color: 0x1c2428, roughness: 0.9 })
  );
  pad.position.set(-0.1, 0.1, 0);
  group.add(pad);

  // Fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.42, 0);
  finShape.lineTo(0.08, -0.34);
  finShape.closePath();
  const finGeo = new THREE.ExtrudeGeometry(finShape, { depth: 0.03, bevelEnabled: false });
  const fin = new THREE.Mesh(finGeo, MAT.boardStripe);
  fin.position.set(-1.15, -0.06, -0.015);
  fin.rotation.y = Math.PI / 2;
  group.add(fin);
  return group;
}

// ---------- Pelican ----------
const WHITE = 0xffffff;

function buildPelican() {
  const bird = new THREE.Group();

  // Body — plump ellipsoid, leaning forward (+X is facing / travel direction)
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.62, 28, 22), MAT.white);
  body.scale.set(1.55, 1.0, 0.94);
  body.position.set(0, 1.32, 0);
  body.rotation.z = -0.18;
  body.castShadow = true;
  bird.add(body);

  // Tail — flattened cone pointing back
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.75, 12), MAT.white);
  tail.scale.set(1, 1, 0.45);
  tail.position.set(-1.0, 1.5, 0);
  tail.rotation.z = Math.PI / 2 + 0.55;
  tail.castShadow = true;
  bird.add(tail);

  const tailTip = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.26, 10), MAT.blackTip);
  tailTip.scale.set(1, 1, 0.5);
  tailTip.position.set(-1.2, 1.56, 0);
  tailTip.rotation.z = Math.PI / 2 + 0.4;
  bird.add(tailTip);

  // Neck — thick cylinder rising from front of body to head
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 0.85, 14), MAT.white);
  neck.position.set(0.72, 1.98, 0);
  neck.rotation.z = -0.42;
  neck.castShadow = true;
  bird.add(neck);

  // Head group (animated: bob + look around)
  const head = new THREE.Group();
  head.position.set(1.02, 2.42, 0);
  bird.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.34, 24, 18), MAT.white);
  skull.scale.set(1.12, 0.98, 0.95);
  skull.castShadow = true;
  head.add(skull);

  // Crest feathers
  for (let i = 0; i < 3; i++) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.26, 8), MAT.featherShade);
    crest.position.set(-0.26 - i * 0.07, 0.3 - Math.abs(i - 1) * 0.04, (i - 1) * 0.1);
    crest.rotation.z = 0.5 + i * 0.18;
    head.add(crest);
  }

  // Upper beak — long orange cone pointing forward (+X)
  const upperBeak = new THREE.Mesh(new THREE.ConeGeometry(0.11, 1.55, 14), MAT.beak);
  upperBeak.rotation.z = -Math.PI / 2;
  upperBeak.position.set(1.0, -0.02, 0);
  upperBeak.castShadow = true;
  head.add(upperBeak);

  // Nail (hook tip)
  const nail = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.22, 10), MAT.beakTip);
  nail.rotation.z = -Math.PI / 2 - 0.18;
  nail.position.set(1.78, -0.06, 0);
  head.add(nail);

  // Throat pouch — hangs below the beak (the pelican giveaway)
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 14), MAT.pouch);
  pouch.scale.set(1.45, 0.55, 0.78);
  pouch.position.set(0.8, -0.28, 0);
  pouch.castShadow = true;
  head.add(pouch);

  // Eyes
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.055, 12, 10), MAT.dark);
    eye.position.set(0.12, 0.08, side * 0.29);
    head.add(eye);
    const glint = new THREE.Mesh(
      new THREE.SphereGeometry(0.018, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    glint.position.set(0.16, 0.11, side * 0.335);
    head.add(glint);
  }

  // Sunglasses — surfer style, sit over the eyes
  const glasses = new THREE.Group();
  const lensGeo = new THREE.BoxGeometry(0.1, 0.18, 0.22);
  for (const side of [-1, 1]) {
    const lens = new THREE.Mesh(lensGeo, MAT.dark);
    lens.position.set(0.16, 0.06, side * 0.21);
    lens.rotation.z = -0.08;
    glasses.add(lens);
  }
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.06, 0.24), MAT.dark);
  bridge.position.set(0.17, 0.1, 0);
  glasses.add(bridge);
  for (const side of [-1, 1]) {
    const strap = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.045, 0.045), MAT.dark);
    strap.position.set(-0.06, 0.13, side * 0.27);
    strap.rotation.y = side * 0.35;
    glasses.add(strap);
  }
  head.add(glasses);

  // Wings — pivot at shoulder, white with black primaries.
  // Slim and swept back so the body stays visible from the side.
  function buildWing(side) {
    const pivot = new THREE.Group();
    pivot.position.set(-0.05, 1.66, side * 0.42);
    const wing = new THREE.Mesh(new THREE.SphereGeometry(0.5, 18, 12), MAT.white);
    wing.scale.set(1.9, 0.13, 0.55);
    wing.position.set(-0.28, 0.04, side * 0.55);
    wing.rotation.y = side * -0.22;
    wing.castShadow = true;
    pivot.add(wing);
    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.24, 14, 10), MAT.blackTip);
    tip.scale.set(1.6, 0.11, 0.5);
    tip.position.set(-0.5, 0.05, side * 0.78);
    tip.rotation.y = side * -0.3;
    pivot.add(tip);
    pivot.rotation.x = side * 0.55; // raised droop
    bird.add(pivot);
    return pivot;
  }
  const wingL = buildWing(1);
  const wingR = buildWing(-1);

  // Legs + webbed feet (surf stance, knees bent)
  function buildLeg(zPos, bend) {
    const g = new THREE.Group();
    g.position.set(0.12, 0.95, zPos);
    const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.07, 0.6, 10), MAT.legs);
    thigh.position.set(-0.1, -0.28, 0);
    thigh.rotation.z = 0.35 + bend;
    g.add(thigh);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.62, 10), MAT.legs);
    shin.position.set(0.16, -0.72, 0);
    shin.rotation.z = -0.3;
    g.add(shin);
    const foot = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.55, 10), MAT.legs);
    foot.scale.set(1, 1, 0.3);
    foot.rotation.z = -Math.PI / 2;
    foot.position.set(0.34, -1.02, 0);
    g.add(foot);
    for (let i = 0; i < 3; i++) {
      const toe = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.22, 6), MAT.legs);
      toe.scale.set(1, 1, 0.35);
      toe.rotation.z = -Math.PI / 2;
      toe.rotation.y = (i - 1) * 0.4;
      toe.position.set(0.52, -1.0, (i - 1) * 0.12);
      g.add(toe);
    }
    bird.add(g);
    return g;
  }
  buildLeg(0.28, 0.05);
  buildLeg(-0.28, -0.06);

  return { bird, head, pouch, wingL, wingR };
}

// ---------- Assemble surfer (board + pelican) ----------
const surfer = new THREE.Group();
const board = buildBoard();
surfer.add(board);
const pelican = buildPelican();
surfer.add(pelican.bird);
scene.add(surfer);

// Foam wake — pulsing ellipse behind the board
const wakeGeo = new THREE.RingGeometry(0.55, 1.35, 28);
wakeGeo.rotateX(-Math.PI / 2);
const wake = new THREE.Mesh(
  wakeGeo,
  new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55, depthWrite: false })
);
wake.scale.set(1.6, 1, 1.1);
wake.position.set(-1.9, 0.06, 0);
surfer.add(wake);

// Foam mound trailing behind the board (half-submerged white water)
const mound = new THREE.Mesh(new THREE.SphereGeometry(0.95, 18, 12), MAT.foam.clone());
mound.material.opacity = 0.55;
mound.scale.set(1.25, 0.2, 0.75);
mound.position.set(-1.6, 0.05, 0);
scene.add(mound);

// Secondary wider wake ring for a fuller foam trail
const wake2Geo = new THREE.RingGeometry(1.4, 2.3, 36);
wake2Geo.rotateX(-Math.PI / 2);
const wake2 = new THREE.Mesh(
  wake2Geo,
  new THREE.MeshBasicMaterial({ color: 0xdff4f7, transparent: true, opacity: 0.15, depthWrite: false })
);
wake2.scale.set(1.35, 1, 0.95);
wake2.position.set(-1.9, 0.05, 0);
scene.add(wake2);

// ---------- Spray particles ----------
const SPRAY_N = 150;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayVel = new Float32Array(SPRAY_N * 3);
const sprayLife = new Float32Array(SPRAY_N);
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const sprayTexCanvas = document.createElement("canvas");
sprayTexCanvas.width = sprayTexCanvas.height = 64;
{
  const ctx = sprayTexCanvas.getContext("2d");
  const grad = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.6, "rgba(255,255,255,0.7)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 64);
}
const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.22,
    map: new THREE.CanvasTexture(sprayTexCanvas),
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    sizeAttenuation: true,
  })
);
scene.add(spray);

function respawnSpray(i, surferX, surferY) {
  const r1 = Math.random(), r2 = Math.random(), r3 = Math.random();
  sprayPos[i * 3] = surferX - 1.2 - r1 * 0.9;
  sprayPos[i * 3 + 1] = surferY + 0.15 + r1 * 0.25;
  sprayPos[i * 3 + 2] = (r2 - 0.5) * 1.4;
  sprayVel[i * 3] = -0.8 - r1 * 2.0;
  sprayVel[i * 3 + 1] = 1.2 + r3 * 1.8;
  sprayVel[i * 3 + 2] = (r2 - 0.5) * 1.6;
  sprayLife[i] = 0.7 + r3 * 0.7;
}
for (let i = 0; i < SPRAY_N; i++) {
  respawnSpray(i, 0, 0.4);
  sprayLife[i] = Math.random() * 1.4;
}

function updateSpray(dt, surferY) {
  for (let i = 0; i < SPRAY_N; i++) {
    sprayLife[i] -= dt;
    if (sprayLife[i] <= 0) {
      respawnSpray(i, surfer.position.x, surferY);
      continue;
    }
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
    sprayVel[i * 3 + 1] -= 4.5 * dt;
    if (sprayPos[i * 3 + 1] < waveHeight(sprayPos[i * 3], sprayPos[i * 3 + 2], tNow) - 0.05) {
      sprayLife[i] = 0;
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------- Clouds ----------
const clouds = [];
const cloudMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  emissive: 0xffffff,
  emissiveIntensity: 0.22,
  roughness: 1,
  transparent: true,
  opacity: 0.95,
});
function buildCloud(x, y, z, s) {
  const g = new THREE.Group();
  const puffs = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < puffs; i++) {
    const r = 1.2 + Math.random() * 1.6;
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 10), cloudMat);
    m.position.set(i * 1.9 - puffs, Math.random() * 0.7, (Math.random() - 0.5) * 1.6);
    m.scale.y = 0.62;
    g.add(m);
  }
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  scene.add(g);
  clouds.push(g);
}
buildCloud(-30, 8.5, -40, 0.8);
buildCloud(22, 9, -44, 0.65);
buildCloud(36, 7.5, -20, 0.5);
buildCloud(-16, 8, 38, 0.7);
buildCloud(4, 9.5, -50, 0.9);

// ---------- Distant birds ----------
const skyBirds = [];
function buildSkyBird(x, y, z) {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x2c3e42 });
  for (const side of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.05, 0.22), mat);
    w.position.x = side * 0.45;
    w.rotation.z = side * 0.25;
    g.add(w);
  }
  g.position.set(x, y, z);
  scene.add(g);
  skyBirds.push(g);
}
buildSkyBird(-20, 14, -30);
buildSkyBird(16, 17, -26);
buildSkyBird(4, 13, -36);

// ---------- Animation ----------
let lastNow = performance.now();
let tNow = 0;

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now - lastNow) / 1000, 0.05);
  lastNow = now;
  const t = (tNow += dt * MOTION);

  updateOcean(t);

  // Pelican rides the swell near the origin, carving side to side
  const carve = Math.sin(t * 0.42) * 2.2 * MOTION;
  const rise = waveHeight(carve, Math.sin(t * 0.3) * 1.2, t);
  surfer.position.set(carve, rise + 0.28 + Math.sin(t * 1.6) * 0.07 * MOTION, Math.sin(t * 0.3) * 1.2);
  surfer.rotation.y = Math.cos(t * 0.42) * 0.28;
  surfer.rotation.z = Math.sin(t * 0.42) * 0.16 + Math.sin(t * 1.6) * 0.03 * MOTION;
  surfer.rotation.x = Math.sin(t * 0.9) * 0.06 * MOTION;

  // Wings flap gently for balance
  const flap = Math.sin(t * 2.4) * 0.32 * MOTION + 0.18;
  pelican.wingL.rotation.x = 0.55 + flap;
  pelican.wingR.rotation.x = -(0.55 + flap);

  // Head checks the horizon; pouch wobbles with the ride
  pelican.head.rotation.y = Math.sin(t * 0.7) * 0.35 * MOTION;
  pelican.head.rotation.x = Math.sin(t * 1.3) * 0.08 * MOTION;
  pelican.head.position.y = 2.42 + Math.sin(t * 1.6) * 0.045 * MOTION;
  const pouchScale = 1 + Math.sin(t * 3.1) * 0.045 * MOTION;
  pelican.pouch.scale.set(1.45 * pouchScale, 0.55 / pouchScale, 0.78 * pouchScale);

  // Wake pulses; foam mound bobs behind the board
  wake.material.opacity = 0.3 + Math.sin(t * 2.2) * 0.12;
  const wakePulse = 1 + Math.sin(t * 2.2) * 0.12 * MOTION;
  wake.scale.set(1.6 * wakePulse, 1, 1.1 * wakePulse);
  wake2.material.opacity = 0.12 + Math.sin(t * 1.7) * 0.05;
  mound.position.y = 0.05 + Math.sin(t * 1.1) * 0.05 * MOTION;
  mound.position.x = surfer.position.x - 1.6;
  mound.position.z = surfer.position.z;
  wake.position.x = surfer.position.x - 1.9;
  wake.position.z = surfer.position.z;
  wake2.position.x = surfer.position.x - 1.9;
  wake2.position.z = surfer.position.z;

  updateSpray(dt, surfer.position.y);

  // Clouds drift; sky birds flap far away
  for (const c of clouds) {
    c.position.x += dt * 0.45 * MOTION;
    if (c.position.x > 60) c.position.x = -60;
  }
  for (let i = 0; i < skyBirds.length; i++) {
    const b = skyBirds[i];
    b.position.x += dt * (0.9 + i * 0.2) * MOTION;
    if (b.position.x > 55) b.position.x = -55;
    b.children.forEach((w, j) => {
      w.rotation.z = ((j === 0 ? 1 : -1) * (0.25 + Math.sin(t * 6 + i) * 0.3));
    });
  }

  // Slow cinematic orbit (non-interactive: camera does the moving)
  const orbitA = t * 0.07 * MOTION + 0.65;
  const camX = surfer.position.x * 0.6 + Math.cos(orbitA) * 8.6;
  const camZ = surfer.position.z * 0.6 + Math.sin(orbitA) * 8.6;
  camera.position.set(camX, 3.4 + Math.sin(t * 0.35) * 0.5 * MOTION, camZ);
  camera.lookAt(surfer.position.x * 0.7, 1.5, surfer.position.z * 0.7);

  renderer.render(scene, camera);
}
animate();

fitCamera();
window.addEventListener("resize", () => {
  fitCamera();
  renderer.setSize(window.innerWidth, window.innerHeight);
});


