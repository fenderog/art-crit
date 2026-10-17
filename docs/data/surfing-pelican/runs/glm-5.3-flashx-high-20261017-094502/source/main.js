import * as THREE from "three";

// ---------------------------------------------------------------------------
// Renderer / scene / camera
// ---------------------------------------------------------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xbfe8f7, 40, 140);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  400
);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------------------------------------------------------------------------
// Lighting
// ---------------------------------------------------------------------------
const sun = new THREE.DirectionalLight(0xfff3d6, 2.2);
sun.position.set(30, 40, -20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -30;
sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30;
sun.shadow.camera.bottom = -30;
scene.add(sun);

scene.add(new THREE.HemisphereLight(0xbfe8ff, 0x2a6d8f, 1.0));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// ---------------------------------------------------------------------------
// Sky: gradient dome generated in code
// ---------------------------------------------------------------------------
function makeSkyTexture() {
  const c = document.createElement("canvas");
  c.width = 16;
  c.height = 256;
  const ctx = c.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0.0, "#2a7fc9"); // deep blue at zenith
  g.addColorStop(0.55, "#7cc4ec");
  g.addColorStop(0.8, "#cdeefb");
  g.addColorStop(1.0, "#ffe9c4"); // warm horizon
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 16, 256);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const skyGeo = new THREE.SphereGeometry(180, 32, 16);
const skyMat = new THREE.MeshBasicMaterial({
  map: makeSkyTexture(),
  side: THREE.BackSide,
  fog: false,
  depthWrite: false,
});
const sky = new THREE.Mesh(skyGeo, skyMat);
scene.add(sky);

// A few soft clouds (billboarded planes with a radial-gradient texture)
function makeCloudTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const ctx = c.getContext("2d");
  const blobs = 12;
  for (let i = 0; i < blobs; i++) {
    const x = 20 + Math.random() * 88;
    const y = 40 + Math.random() * 48;
    const r = 14 + Math.random() * 22;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, "rgba(255,255,255,0.9)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const cloudTex = makeCloudTexture();
for (let i = 0; i < 8; i++) {
  const w = 20 + Math.random() * 30;
  const cloud = new THREE.Mesh(
    new THREE.PlaneGeometry(w, w * 0.55),
    new THREE.MeshBasicMaterial({
      map: cloudTex,
      transparent: true,
      depthWrite: false,
      fog: false,
      opacity: 0.85,
    })
  );
  const a = Math.random() * Math.PI * 2;
  const r = 70 + Math.random() * 60;
  cloud.position.set(Math.cos(a) * r, 25 + Math.random() * 25, Math.sin(a) * r);
  cloud.lookAt(0, cloud.position.y * 0.5, 0);
  scene.add(cloud);
}

// ---------------------------------------------------------------------------
// Sun disc
// ---------------------------------------------------------------------------
const sunDisc = new THREE.Mesh(
  new THREE.SphereGeometry(6, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff2b0, fog: false })
);
sunDisc.position.set(90, 70, -110);
scene.add(sunDisc);

// ---------------------------------------------------------------------------
// Ocean
// ---------------------------------------------------------------------------
const OCEAN_SIZE = 240;
const OCEAN_SEGS = 120;
const oceanGeo = new THREE.PlaneGeometry(
  OCEAN_SIZE,
  OCEAN_SIZE,
  OCEAN_SEGS,
  OCEAN_SEGS
);
oceanGeo.rotateX(-Math.PI / 2);

const oceanMat = new THREE.MeshPhongMaterial({
  color: 0x1a7f9e,
  emissive: 0x04303f,
  specular: 0xbfefFF,
  shininess: 90,
  transparent: true,
  opacity: 0.94,
  side: THREE.DoubleSide,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

// Keep a copy of original positions for the wave displacement
const oceanBase = oceanGeo.attributes.position.array.slice();

// Wave field: analytic sum of sines so the pelican can ride the same surface.
function waveHeight(x, z, t) {
  return (
    0.9 * Math.sin(x * 0.14 + t * 1.1) +
    0.55 * Math.sin(z * 0.21 + t * 1.5 + 1.3) +
    0.35 * Math.sin((x + z) * 0.11 + t * 0.8) +
    0.2 * Math.sin((x - z * 0.5) * 0.27 + t * 2.1)
  );
}

// ---------------------------------------------------------------------------
// Pelican
// ---------------------------------------------------------------------------
const pelican = new THREE.Group();
scene.add(pelican);

const whiteMat = new THREE.MeshStandardMaterial({
  color: 0xf7f5ef,
  roughness: 0.85,
  metalness: 0.0,
});
const grayMat = new THREE.MeshStandardMaterial({
  color: 0xd9d4c8,
  roughness: 0.9,
});
const beakMat = new THREE.MeshStandardMaterial({
  color: 0xf2a03d,
  roughness: 0.55,
});
const pouchMat = new THREE.MeshStandardMaterial({
  color: 0xf7c073,
  roughness: 0.7,
});
const darkMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.4 });

// Body: stretched egg shape
const body = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), whiteMat);
body.scale.set(1.25, 1.0, 1.7);
body.castShadow = true;
pelican.add(body);

// Tail feathers
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.6, 16), grayMat);
tail.rotation.x = Math.PI * 0.62;
tail.position.set(0, 0.05, -1.9);
tail.castShadow = true;
pelican.add(tail);

// Neck: tube along a curve from body up to the head
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 0.35, 1.1),
  new THREE.Vector3(0, 0.9, 1.7),
  new THREE.Vector3(0, 1.7, 2.0),
  new THREE.Vector3(0, 2.3, 1.9),
]);
const neck = new THREE.Mesh(
  new THREE.TubeGeometry(neckCurve, 24, 0.42, 16),
  whiteMat
);
neck.castShadow = true;
pelican.add(neck);

// Head
const head = new THREE.Mesh(new THREE.SphereGeometry(0.52, 24, 18), whiteMat);
head.position.set(0, 2.35, 1.85);
head.castShadow = true;
pelican.add(head);

// Crest tuft
const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.45, 8), grayMat);
tuft.position.set(0.06, 2.85, 1.72);
tuft.rotation.x = -0.6;
pelican.add(tuft);

// Beak: long flat upper bill
const beak = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.14, 1.9), beakMat);
beak.position.set(0, 2.28, 2.9);
beak.castShadow = true;
pelican.add(beak);
const beakTip = new THREE.Mesh(new THREE.ConeGeometry(0.17, 0.5, 10), beakMat);
beakTip.rotation.x = Math.PI / 2;
beakTip.position.set(0, 2.28, 3.95);
pelican.add(beakTip);

// Throat pouch: squashed sphere hanging under the bill, on a pivot so it can stretch
const pouchPivot = new THREE.Group();
pouchPivot.position.set(0, 2.22, 2.0);
pelican.add(pouchPivot);
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 16), pouchMat);
pouch.scale.set(0.75, 1.0, 1.9);
pouch.position.set(0, -0.35, 0.95);
pouch.castShadow = true;
pouchPivot.add(pouch);

// Eyes
const eyeGeo = new THREE.SphereGeometry(0.09, 12, 12);
const eyeL = new THREE.Mesh(eyeGeo, darkMat);
eyeL.position.set(0.3, 2.55, 1.95);
const eyeR = eyeL.clone();
eyeR.position.x = -0.3;
pelican.add(eyeL, eyeR);

// Sunglasses — every cool surfing pelican wears them
const shadeBar = new THREE.Mesh(
  new THREE.BoxGeometry(0.72, 0.13, 0.1),
  new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.25, metalness: 0.6 })
);
shadeBar.position.set(0, 2.6, 2.15);
shadeBar.rotation.x = -0.15;
pelican.add(shadeBar);
const shadeL = new THREE.Mesh(
  new THREE.SphereGeometry(0.15, 12, 12),
  new THREE.MeshStandardMaterial({ color: 0x0a0a12, roughness: 0.15, metalness: 0.7 })
);
shadeL.scale.set(1, 0.8, 0.5);
shadeL.position.set(0.21, 2.57, 2.28);
const shadeR = shadeL.clone();
shadeR.position.x = -0.21;
pelican.add(shadeL, shadeR);

// Wings: flattened cone/sphere hybrid on shoulder pivots so they can flap
function makeWing(sign) {
  const pivot = new THREE.Group();
  pivot.position.set(0.95 * sign, 0.45, 0.15);
  const wing = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12), grayMat);
  wing.scale.set(0.28, 0.16, 1.5);
  wing.position.set(0.5 * sign, 0, -0.2);
  wing.castShadow = true;
  pivot.add(wing);
  const featherTip = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.9, 10), grayMat);
  featherTip.rotation.x = -Math.PI / 2;
  featherTip.scale.set(1, 1, 0.5);
  featherTip.position.set(0.5 * sign, 0, -1.55);
  pivot.add(featherTip);
  pelican.add(pivot);
  return pivot;
}
const wingL = makeWing(1);
const wingR = makeWing(-1);

// Orange webbed feet planted on the board
function makeFoot(sign) {
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.1, 0.7), beakMat);
  foot.position.set(0.42 * sign, 0, 0.3);
  foot.castShadow = true;
  return foot;
}
const feet = new THREE.Group();
feet.add(makeFoot(1), makeFoot(-1));
pelican.add(feet);

// ---------------------------------------------------------------------------
// Surfboard
// ---------------------------------------------------------------------------
const board = new THREE.Group();
scene.add(board);

const boardMat = new THREE.MeshStandardMaterial({
  color: 0xff5f6d,
  roughness: 0.35,
  metalness: 0.05,
});
// Deck: scaled + flattened sphere gives a nice rounded surfboard silhouette
const deck = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), boardMat);
deck.scale.set(0.85, 0.12, 2.6);
deck.castShadow = true;
board.add(deck);

// Striped deck pad
const pad = new THREE.Mesh(
  new THREE.CircleGeometry(0.5, 24),
  new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9 })
);
pad.rotation.x = -Math.PI / 2;
pad.scale.set(0.75, 1.9, 1);
pad.position.y = 0.1;
board.add(pad);

// Fin under the tail of the board
const fin = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.7, 12), new THREE.MeshStandardMaterial({ color: 0xffd166, roughness: 0.4 }));
fin.position.set(0, -0.35, -1.7);
fin.rotation.x = Math.PI; // points down
board.add(fin);

// Pelican stands slightly behind the centre of the board
pelican.position.set(0, 0.28, -0.35);
board.add(pelican);

// ---------------------------------------------------------------------------
// Splash particles
// ---------------------------------------------------------------------------
const splashCount = 60;
const splashGeo = new THREE.SphereGeometry(0.1, 8, 8);
const splashMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true });
const splashes = [];
for (let i = 0; i < splashCount; i++) {
  const m = new THREE.Mesh(splashGeo, splashMat.clone());
  m.visible = false;
  scene.add(m);
  splashes.push({
    mesh: m,
    life: 0,
    vel: new THREE.Vector3(),
  });
}
let splashTimer = 0;

function emitSplash(pos, baseVel) {
  for (const s of splashes) {
    if (s.life <= 0) {
      s.life = 0.6 + Math.random() * 0.5;
      s.maxLife = s.life;
      s.mesh.position.copy(pos);
      s.mesh.visible = true;
      s.mesh.scale.setScalar(0.5 + Math.random() * 0.9);
      s.vel.copy(baseVel)
        .add(new THREE.Vector3(
          (Math.random() - 0.5) * 2.5,
          Math.random() * 2.5 + 1,
          (Math.random() - 0.5) * 2.5
        ));
      s.mesh.material.opacity = 1;
      return;
    }
  }
}

// ---------------------------------------------------------------------------
// Animation loop
// ---------------------------------------------------------------------------
const clock = new THREE.Clock();

const camTarget = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // --- ocean vertices -------------------------------------------------------
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    pos.setY(i, waveHeight(x, z, t));
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // --- board rides the wave -------------------------------------------------
  // The board carves a big smooth loop across the ocean so it always looks in
  // motion, with the pelican facing along the direction of travel.
  const orbitAngle = t * 0.15;
  const loopR = 16;
  const bx = Math.cos(orbitAngle) * loopR + Math.sin(t * 1.7) * 0.6;
  const bz = Math.sin(orbitAngle) * loopR + Math.sin(t * 2.3) * 0.5;

  const h = waveHeight(bx, bz, t);
  const hx1 = waveHeight(bx + 0.5, bz, t);
  const hx0 = waveHeight(bx - 0.5, bz, t);
  const hz1 = waveHeight(bx, bz + 0.5, t);
  const hz0 = waveHeight(bx, bz - 0.5, t);
  const nx = -(hx1 - hx0);
  const nz = -(hz1 - hz0);

  board.position.set(bx, h + 0.18, bz);
  // Align board to wave slope, heading along the loop tangent
  const pitch = Math.atan2(hz1 - hz0, 1.0) * 0.6;
  const roll = Math.atan2(hx1 - hx0, 1.0) * 0.6;
  board.rotation.set(pitch, -orbitAngle, roll, "YXZ");
  // Carve wiggle + slight bob
  board.rotation.z += Math.sin(t * 2.3) * 0.12;
  board.position.y += Math.sin(t * 3.1) * 0.05;

  // --- pelican life ---------------------------------------------------------
  // Body bob & lean
  pelican.position.y = 0.28 + Math.sin(t * 3.1) * 0.06;
  pelican.rotation.z = Math.sin(t * 2.3 + 0.6) * 0.08;
  pelican.rotation.x = Math.sin(t * 1.4) * 0.05;

  // Wing flapping: bursts every few seconds, otherwise tucked
  const flapCycle = (t * 0.35) % 1;
  let flap = 0;
  if (flapCycle < 0.35) {
    flap = Math.sin(flapCycle * Math.PI / 0.35 * 4) * (1 - flapCycle / 0.35);
  }
  const flapAngle = 0.15 + flap * 0.9;
  wingL.rotation.z = -flapAngle;
  wingR.rotation.z = flapAngle;
  wingL.rotation.x = Math.sin(t * 6) * 0.1 * flap;
  wingR.rotation.x = -Math.sin(t * 6) * 0.1 * flap;

  // Pouch stretch — occasionally opens wide like a squawk
  const squawk = Math.max(0, Math.sin(t * 0.9)) ** 8;
  pouchPivot.scale.y = 1 + squawk * 0.9;
  pouchPivot.rotation.x = -squawk * 0.35;

  // Head looks where it's going, with a little lookahead sway
  head.rotation.y = Math.sin(t * 0.7) * 0.25;
  neck.rotation.y = Math.sin(t * 0.7) * 0.12;

  // --- splashes -------------------------------------------------------------
  splashTimer -= dt;
  if (splashTimer <= 0) {
    splashTimer = 0.05 + Math.random() * 0.08;
    const tailPos = new THREE.Vector3(0, 0, -2.2).applyEuler(board.rotation)
      .add(board.position);
    emitSplash(tailPos, new THREE.Vector3(0, 0.5, 0));
  }
  for (const s of splashes) {
    if (s.life > 0) {
      s.life -= dt;
      if (s.life <= 0) {
        s.mesh.visible = false;
        continue;
      }
      s.vel.y -= 9.0 * dt;
      s.mesh.position.addScaledVector(s.vel, dt);
      s.mesh.material.opacity = s.life / s.maxLife;
    }
  }

  // --- camera: slow cinematic orbit with a hand-held sway --------------------
  const orbit = t * 0.12;
  const camR = 14 + Math.sin(t * 0.23) * 2.5;
  camera.position.set(
    Math.cos(orbit) * camR,
    5.5 + Math.sin(t * 0.4) * 1.2,
    bz + Math.sin(orbit) * camR
  );
  camTarget.set(bx, board.position.y + 2.2, bz);
  camera.lookAt(camTarget);

  sky.position.copy(camera.position);

  renderer.render(scene, camera);
}

animate();
