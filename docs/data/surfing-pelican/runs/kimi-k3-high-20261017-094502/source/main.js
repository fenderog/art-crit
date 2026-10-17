import * as THREE from "three";

// ---------------------------------------------------------------------------
// Renderer / scene / camera
// ---------------------------------------------------------------------------
const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();

// Vertical gradient sky painted on a canvas, used as a flat background.
{
  const c = document.createElement("canvas");
  c.width = 2;
  c.height = 512;
  const ctx = c.getContext("2d");
  const grad = ctx.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0.0, "#7ec8f2");
  grad.addColorStop(0.45, "#a8dcf7");
  grad.addColorStop(0.72, "#fdeecb");
  grad.addColorStop(1.0, "#ffd9a0");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  scene.background = tex;
}

scene.fog = new THREE.Fog(0xcfe9f4, 70, 380);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  1200
);

// ---------------------------------------------------------------------------
// Lights
// ---------------------------------------------------------------------------
const hemi = new THREE.HemisphereLight(0xbfe3ff, 0x0e4a66, 0.9);
scene.add(hemi);

const sunLight = new THREE.DirectionalLight(0xfff1d6, 1.6);
sunLight.position.set(-40, 60, -30);
scene.add(sunLight);

const fill = new THREE.DirectionalLight(0x9fd0ff, 0.35);
fill.position.set(30, 20, 40);
scene.add(fill);

// Visible sun disc
{
  const sun = new THREE.Mesh(
    new THREE.CircleGeometry(18, 32),
    new THREE.MeshBasicMaterial({ color: 0xfff6d8, fog: false })
  );
  sun.position.set(-180, 130, -320);
  sun.lookAt(0, 40, 0);
  scene.add(sun);
  const halo = new THREE.Mesh(
    new THREE.CircleGeometry(30, 32),
    new THREE.MeshBasicMaterial({
      color: 0xfff0be,
      transparent: true,
      opacity: 0.35,
      fog: false,
    })
  );
  halo.position.copy(sun.position).add(new THREE.Vector3(0, 0, -1));
  halo.lookAt(0, 40, 0);
  scene.add(halo);
}

// ---------------------------------------------------------------------------
// Ocean — CPU-displaced plane with rolling swells plus a ridge that swells
// into the big breaking wave the pelican rides.
// ---------------------------------------------------------------------------
const OCEAN_SIZE = 600;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, 130, 130);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1468a0,
  roughness: 0.42,
  metalness: 0.08,
  flatShading: true,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
scene.add(ocean);

const oceanPos = oceanGeo.attributes.position;

function waveHeight(x, z, t) {
  let h = 0;
  h += 0.55 * Math.sin(0.14 * x + 0.9 * t);
  h += 0.35 * Math.sin(0.1 * z - 0.7 * t + 1.3);
  h += 0.28 * Math.sin(0.16 * (x * 0.7 + z * 0.7) + 1.6 * t + 4.0);
  h += 0.15 * Math.sin(0.33 * x - 1.9 * t + 2.2);
  // Ridge that feeds the big breaking wave (crest sits near x = -3.5).
  const rx = (x + 3.5) / 4.2;
  h += 2.4 * Math.exp(-rx * rx) * (0.85 + 0.15 * Math.sin(t * 1.1));
  return h;
}

function updateOcean(t) {
  const arr = oceanPos.array;
  for (let i = 0; i < arr.length; i += 3) {
    arr[i + 1] = waveHeight(arr[i], arr[i + 2], t);
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------------------------------------------------------------------------
// The big curling wave (extruded silhouette) + foam crest
// ---------------------------------------------------------------------------
const waveGroup = new THREE.Group();
scene.add(waveGroup);

{
  const s = new THREE.Shape();
  s.moveTo(-10, -2);
  s.quadraticCurveTo(-4.2, 6.0, -0.6, 6.9); // back slope up to the crest
  s.quadraticCurveTo(1.4, 7.4, 1.9, 5.8); // lip throwing forward
  s.quadraticCurveTo(2.2, 4.8, 1.6, 4.4); // lip tucking under
  s.quadraticCurveTo(3.4, 2.6, 5.2, 0.4); // front face
  s.quadraticCurveTo(6.2, -0.6, 7.5, -2);
  s.lineTo(-10, -2);

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 26,
    bevelEnabled: true,
    bevelThickness: 0.6,
    bevelSize: 0.6,
    bevelSegments: 2,
    curveSegments: 24,
  });
  geo.translate(0, 0, -13);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x1581a8,
    roughness: 0.3,
    metalness: 0.05,
  });
  const wave = new THREE.Mesh(geo, mat);
  waveGroup.add(wave);

  // Glassy inner barrel hint (slightly smaller, lighter, transparent shell)
  const inner = new THREE.Mesh(
    geo.clone(),
    new THREE.MeshStandardMaterial({
      color: 0x9fe4ee,
      roughness: 0.15,
      transparent: true,
      opacity: 0.22,
    })
  );
  inner.scale.set(0.985, 0.99, 0.96);
  waveGroup.add(inner);
}

// Foam blobs along the lip of the wave
const foamBlobs = [];
{
  const foamMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.95,
  });
  const lipPoints = [
    new THREE.Vector3(-1.4, 7.15, 0),
    new THREE.Vector3(-0.4, 7.25, 0),
    new THREE.Vector3(0.7, 7.15, 0),
    new THREE.Vector3(1.6, 6.5, 0),
    new THREE.Vector3(2.05, 5.6, 0),
    new THREE.Vector3(1.9, 4.8, 0),
  ];
  const foamGeo = new THREE.SphereGeometry(1, 10, 8);
  let seed = 7;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (const p of lipPoints) {
    for (let z = -12; z <= 12; z += 1.6) {
      const m = new THREE.Mesh(foamGeo, foamMat);
      const r = 0.28 + rand() * 0.34;
      m.scale.setScalar(r);
      m.position.set(
        p.x + (rand() - 0.5) * 0.7,
        p.y + (rand() - 0.5) * 0.7,
        z + (rand() - 0.5) * 1.2
      );
      m.userData = { phase: rand() * Math.PI * 2, base: r };
      foamBlobs.push(m);
      waveGroup.add(m);
    }
  }
  // Foam wash at the base of the wave front
  const wash = new THREE.Mesh(
    new THREE.SphereGeometry(1, 16, 10),
    new THREE.MeshStandardMaterial({
      color: 0xf2fbff,
      roughness: 1,
      transparent: true,
      opacity: 0.85,
    })
  );
  wash.scale.set(4.5, 0.8, 12);
  wash.position.set(4.6, 0.1, 0);
  waveGroup.add(wash);
}
waveGroup.position.set(-3, 0, 0);

// ---------------------------------------------------------------------------
// Surfboard
// ---------------------------------------------------------------------------
function makeSurfboard() {
  const g = new THREE.Group();

  const boardGeo = new THREE.CapsuleGeometry(0.55, 2.4, 6, 18);
  boardGeo.rotateZ(Math.PI / 2); // long axis along X
  boardGeo.scale(1, 0.22, 1);
  const board = new THREE.Mesh(
    boardGeo,
    new THREE.MeshStandardMaterial({ color: 0xff5d47, roughness: 0.35 })
  );
  g.add(board);

  // Racing stripe
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.9, 0.02, 0.22),
    new THREE.MeshStandardMaterial({ color: 0xfff3d6, roughness: 0.4 })
  );
  stripe.position.y = 0.13;
  g.add(stripe);

  // Fin
  const finGeo = new THREE.ConeGeometry(0.16, 0.42, 4);
  finGeo.scale(1.6, 1, 0.35);
  const fin = new THREE.Mesh(
    finGeo,
    new THREE.MeshStandardMaterial({ color: 0xd8453a, roughness: 0.4 })
  );
  fin.rotation.x = Math.PI;
  fin.position.set(-1.1, -0.28, 0);
  g.add(fin);

  return g;
}

// ---------------------------------------------------------------------------
// Pelican, built from primitives. Faces +X.
// ---------------------------------------------------------------------------
function makePelican() {
  const g = new THREE.Group();
  const mats = {
    body: new THREE.MeshStandardMaterial({ color: 0xf2efe6, roughness: 0.9 }),
    wing: new THREE.MeshStandardMaterial({ color: 0xd9d4c8, roughness: 0.9 }),
    tip: new THREE.MeshStandardMaterial({ color: 0x4a4a4f, roughness: 0.85 }),
    beak: new THREE.MeshStandardMaterial({ color: 0xf59b23, roughness: 0.55 }),
    pouch: new THREE.MeshStandardMaterial({ color: 0xe98a4e, roughness: 0.7 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x1c1c1e, roughness: 0.5 }),
    leg: new THREE.MeshStandardMaterial({ color: 0xe08b3a, roughness: 0.7 }),
  };

  // Body
  const bodyGeo = new THREE.SphereGeometry(1, 24, 18);
  bodyGeo.scale(1.05, 0.78, 0.82);
  const body = new THREE.Mesh(bodyGeo, mats.body);
  body.position.set(0, 1.5, 0);
  g.add(body);

  // Neck (leaning forward)
  const neck = new THREE.Mesh(
    new THREE.CylinderGeometry(0.2, 0.3, 1.0, 12),
    mats.body
  );
  neck.position.set(0.82, 2.2, 0);
  neck.rotation.z = -0.5;
  g.add(neck);

  // Head
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 20, 16), mats.body);
  head.position.set(1.18, 2.78, 0);
  g.add(head);

  // Crest tuft
  const crestGeo = new THREE.SphereGeometry(0.3, 12, 10);
  crestGeo.scale(1.1, 0.55, 0.7);
  const crest = new THREE.Mesh(crestGeo, mats.wing);
  crest.position.set(0.92, 2.95, 0);
  crest.rotation.z = 0.35;
  g.add(crest);

  // Eyes
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 8), mats.dark);
    eye.position.set(1.38, 2.92, side * 0.33);
    g.add(eye);
  }

  // Upper beak — long flattened cone pointing +X
  const beakGeo = new THREE.ConeGeometry(0.15, 1.7, 10);
  beakGeo.rotateZ(-Math.PI / 2);
  beakGeo.scale(1, 0.55, 1);
  const beak = new THREE.Mesh(beakGeo, mats.beak);
  beak.position.set(2.15, 2.8, 0);
  beak.rotation.z = -0.08;
  g.add(beak);

  // Pouch, hinged under the beak so it can wobble
  const pouchPivot = new THREE.Group();
  pouchPivot.position.set(1.5, 2.68, 0);
  const pouchGeo = new THREE.SphereGeometry(0.4, 16, 12);
  pouchGeo.scale(1.5, 0.85, 0.75);
  const pouch = new THREE.Mesh(pouchGeo, mats.pouch);
  pouch.position.set(0.55, -0.42, 0);
  pouchPivot.add(pouch);
  g.add(pouchPivot);

  // Wings — pivots at the shoulders, flapping for balance
  function makeWing(side) {
    const pivot = new THREE.Group();
    pivot.position.set(-0.05, 1.95, side * 0.55);

    const innerGeo = new THREE.CapsuleGeometry(0.34, 0.9, 4, 10);
    innerGeo.rotateX(Math.PI / 2);
    innerGeo.scale(1.15, 0.28, 1);
    innerGeo.translate(0, 0, side * 0.62);
    const inner = new THREE.Mesh(innerGeo, mats.wing);
    pivot.add(inner);

    const outerGeo = new THREE.CapsuleGeometry(0.24, 0.85, 4, 10);
    outerGeo.rotateX(Math.PI / 2);
    outerGeo.scale(0.9, 0.24, 1);
    outerGeo.translate(-0.12, 0, side * 1.45);
    const outer = new THREE.Mesh(outerGeo, mats.wing);
    pivot.add(outer);

    const tipGeo = new THREE.ConeGeometry(0.16, 0.5, 8);
    tipGeo.rotateX(side > 0 ? Math.PI / 2 : -Math.PI / 2);
    tipGeo.scale(0.8, 1, 0.3);
    tipGeo.translate(-0.2, 0, side * 1.95);
    const tip = new THREE.Mesh(tipGeo, mats.tip);
    pivot.add(tip);

    return pivot;
  }
  const wingL = makeWing(1);
  const wingR = makeWing(-1);
  g.add(wingL, wingR);

  // Tail
  const tailGeo = new THREE.ConeGeometry(0.32, 0.9, 8);
  tailGeo.rotateZ(Math.PI / 2);
  tailGeo.scale(1, 0.4, 1);
  const tail = new THREE.Mesh(tailGeo, mats.wing);
  tail.position.set(-1.2, 1.55, 0);
  g.add(tail);

  // Legs + webbed feet planted on the board
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.055, 0.06, 0.45, 8),
      mats.leg
    );
    leg.position.set(0.15 + side * 0.35, 0.9, side * 0.18);
    g.add(leg);

    const footGeo = new THREE.ConeGeometry(0.17, 0.34, 4);
    footGeo.rotateZ(-Math.PI / 2);
    footGeo.scale(1, 0.35, 1.4);
    const foot = new THREE.Mesh(footGeo, mats.leg);
    foot.position.set(0.22 + side * 0.35, 0.68, side * 0.18);
    g.add(foot);
  }

  return { group: g, wingL, wingR, pouchPivot, head };
}

// ---------------------------------------------------------------------------
// Surfer assembly: board + pelican + foam patch, tilted on the wave face
// ---------------------------------------------------------------------------
const surfer = new THREE.Group();
scene.add(surfer);

const board = makeSurfboard();
board.position.set(0, 0.55, 0);
surfer.add(board);

const pelican = makePelican();
surfer.add(pelican.group);

// Foam patch where the board carves the face
const carveFoam = new THREE.Mesh(
  new THREE.SphereGeometry(1, 16, 10),
  new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 1,
    transparent: true,
    opacity: 0.85,
  })
);
carveFoam.scale.set(1.9, 0.22, 1.1);
carveFoam.position.set(-0.5, 0.42, 0);
surfer.add(carveFoam);

surfer.position.set(-0.6, 2.15, 0);

// ---------------------------------------------------------------------------
// Spray particles trailing the board
// ---------------------------------------------------------------------------
const spray = [];
{
  const geo = new THREE.SphereGeometry(1, 6, 5);
  const mat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.9,
  });
  for (let i = 0; i < 60; i++) {
    const m = new THREE.Mesh(geo, mat.clone());
    m.visible = false;
    scene.add(m);
    spray.push({ mesh: m, vel: new THREE.Vector3(), life: 0, maxLife: 1 });
  }
}
let sprayCursor = 0;

function spawnSpray(origin, t) {
  const p = spray[sprayCursor];
  sprayCursor = (sprayCursor + 1) % spray.length;
  p.mesh.visible = true;
  p.mesh.position.copy(origin);
  p.mesh.position.x += (Math.random() - 0.5) * 0.6;
  p.mesh.position.z += (Math.random() - 0.5) * 0.9;
  p.vel.set(
    -1.5 - Math.random() * 2.5,
    1.2 + Math.random() * 2.2,
    (Math.random() - 0.5) * 2.0
  );
  p.life = 0;
  p.maxLife = 0.7 + Math.random() * 0.5;
  p.baseScale = 0.05 + Math.random() * 0.1;
  p.mesh.scale.setScalar(p.baseScale);
}

function updateSpray(dt) {
  for (const p of spray) {
    if (!p.mesh.visible) continue;
    p.life += dt;
    if (p.life >= p.maxLife) {
      p.mesh.visible = false;
      continue;
    }
    p.vel.y -= 7 * dt;
    p.mesh.position.addScaledVector(p.vel, dt);
    const k = 1 - p.life / p.maxLife;
    p.mesh.scale.setScalar(p.baseScale * (0.5 + k));
    p.mesh.material.opacity = 0.85 * k;
  }
}

// ---------------------------------------------------------------------------
// Clouds — puffy sphere clusters drifting by
// ---------------------------------------------------------------------------
const clouds = [];
{
  const mat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 1,
    flatShading: true,
  });
  let seed = 13;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 7; i++) {
    const cloud = new THREE.Group();
    const puffs = 3 + Math.floor(rand() * 3);
    for (let j = 0; j < puffs; j++) {
      const r = 2.5 + rand() * 3.5;
      const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), mat);
      puff.position.set((rand() - 0.5) * 9, (rand() - 0.5) * 2.5, (rand() - 0.5) * 5);
      puff.scale.y = 0.55;
      cloud.add(puff);
    }
    cloud.position.set(-260 + rand() * 520, 34 + rand() * 26, -180 + rand() * 240);
    cloud.userData.speed = 0.8 + rand() * 1.2;
    clouds.push(cloud);
    scene.add(cloud);
  }
}

// ---------------------------------------------------------------------------
// Distant gulls — simple flapping silhouettes circling high up
// ---------------------------------------------------------------------------
const gulls = [];
{
  const mat = new THREE.MeshBasicMaterial({ color: 0x2b3a44 });
  for (let i = 0; i < 3; i++) {
    const gull = new THREE.Group();
    const wingGeo = new THREE.BoxGeometry(1.4, 0.06, 0.3);
    const wl = new THREE.Mesh(wingGeo, mat);
    wl.position.x = -0.7;
    const wr = new THREE.Mesh(wingGeo, mat);
    wr.position.x = 0.7;
    gull.add(wl, wr);
    gull.userData = {
      wl,
      wr,
      radius: 55 + i * 14,
      height: 26 + i * 6,
      speed: 0.12 + i * 0.03,
      phase: i * 2.1,
    };
    gulls.push(gull);
    scene.add(gull);
  }
}

// ---------------------------------------------------------------------------
// Animation
// ---------------------------------------------------------------------------
const lookTarget = new THREE.Vector3();
let sprayTimer = 0;
let lastTime = performance.now();
let elapsed = 0;

function animate() {
  const now = performance.now();
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  elapsed += dt;
  const t = elapsed;

  updateOcean(t);

  // Big wave breathing / surging
  waveGroup.rotation.z = 0.028 * Math.sin(t * 0.9);
  waveGroup.position.y = 0.18 * Math.sin(t * 1.25 + 1);
  waveGroup.scale.y = 1 + 0.022 * Math.sin(t * 0.7);

  // Foam blobs jiggling on the lip
  for (const b of foamBlobs) {
    const k = 1 + 0.22 * Math.sin(t * 3.1 + b.userData.phase);
    b.scale.setScalar(b.userData.base * k);
  }

  // Surfer riding the face: bob, pitch and carve roll
  surfer.position.y = 2.15 + 0.22 * Math.sin(t * 1.25 + 0.6);
  surfer.position.x = -0.6 + 0.35 * Math.sin(t * 0.45);
  surfer.rotation.z = -0.42 + 0.05 * Math.sin(t * 1.1);
  surfer.rotation.x = 0.09 * Math.sin(t * 0.8 + 2.0);

  // Pelican balance animation
  const flap = Math.sin(t * 2.6);
  pelican.wingL.rotation.x = -0.12 + 0.28 * flap;
  pelican.wingR.rotation.x = 0.12 - 0.28 * flap;
  pelican.wingL.rotation.y = 0.1 * Math.sin(t * 1.3);
  pelican.wingR.rotation.y = -0.1 * Math.sin(t * 1.3);
  pelican.pouchPivot.rotation.z = 0.08 * Math.sin(t * 1.8 + 0.5);
  pelican.pouchPivot.rotation.x = 0.05 * Math.sin(t * 2.3);
  pelican.head.position.y = 2.78 + 0.04 * Math.sin(t * 2.6 + 1);
  pelican.group.rotation.y = 0.12 * Math.sin(t * 0.55);
  pelican.group.rotation.z = 0.06 + 0.05 * Math.sin(t * 1.25 + 0.6);

  // Board spray
  sprayTimer -= dt;
  if (sprayTimer <= 0) {
    sprayTimer = 0.03;
    const origin = new THREE.Vector3(-1.6, 0.6, 0).applyEuler(surfer.rotation).add(surfer.position);
    spawnSpray(origin, t);
  }
  updateSpray(dt);

  // Clouds drifting
  for (const c of clouds) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 300) c.position.x = -300;
  }

  // Gulls circling
  for (const g of gulls) {
    const u = g.userData;
    const a = t * u.speed + u.phase;
    g.position.set(Math.cos(a) * u.radius, u.height + Math.sin(t * 0.7 + u.phase) * 2, Math.sin(a) * u.radius);
    g.rotation.y = -a;
    const flapG = Math.sin(t * 6 + u.phase) * 0.5;
    u.wl.rotation.z = flapG;
    u.wr.rotation.z = -flapG;
  }

  // Slow cinematic orbit around the pelican
  const camA = t * 0.09;
  const camR = 24 + 2.5 * Math.sin(t * 0.17);
  camera.position.set(
    surfer.position.x + Math.cos(camA) * camR,
    8.5 + 1.6 * Math.sin(t * 0.23),
    Math.sin(camA) * camR
  );
  lookTarget.set(surfer.position.x - 1.5, 3.4, 0);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
