import * as THREE from "three";

// ---------------------------------------------------------------------------
// Surfing Pelican — a looping, non-interactive 3D vignette.
// Everything is procedural (no external assets), so the page runs offline.
// The camera drifts on its own; there are no controls or event handlers
// other than window resize.
// ---------------------------------------------------------------------------

const container = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fd4e8, 20, 58);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  200
);
const CAM_BASE = new THREE.Vector3(0.8, 3.2, 9.4);
const CAM_LOOK = new THREE.Vector3(0.2, 1.15, -0.6);
camera.position.copy(CAM_BASE);
camera.lookAt(CAM_LOOK);

// --- lights ---------------------------------------------------------------
scene.add(new THREE.HemisphereLight(0xcfeefc, 0x1a5a74, 0.9));

const sun = new THREE.DirectionalLight(0xfff2d8, 2.0);
sun.position.set(-8, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12;
sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12;
sun.shadow.camera.bottom = -8;
sun.shadow.camera.far = 40;
scene.add(sun);

// --- sky dome (gradient shader, no textures) -------------------------------
{
  const skyGeo = new THREE.SphereGeometry(80, 32, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x2f7fc4) },
      mid: { value: new THREE.Color(0x9fd4e8) },
      low: { value: new THREE.Color(0xfdf3d8) },
    },
    vertexShader: `
      varying vec3 vPos;
      void main() {
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform vec3 top; uniform vec3 mid; uniform vec3 low;
      varying vec3 vPos;
      void main() {
        float h = normalize(vPos).y;
        vec3 c = h > 0.12
          ? mix(mid, top, smoothstep(0.12, 0.65, h))
          : mix(low, mid, smoothstep(-0.08, 0.12, h));
        gl_FragColor = vec4(c, 1.0);
      }`,
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
}

// --- sun disc + glow (geometry + canvas-generated sprite) ------------------
function radialSprite(inner, outer) {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
  g.addColorStop(0, inner);
  g.addColorStop(1, outer);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
{
  const disc = new THREE.Mesh(
    new THREE.SphereGeometry(1.4, 24, 24),
    new THREE.MeshBasicMaterial({ color: 0xfff6d8, fog: false })
  );
  disc.position.set(-14, 11, -30);
  scene.add(disc);
  const glow = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: radialSprite("rgba(255,250,220,1)", "rgba(255,250,220,0)"),
      transparent: true,
      depthWrite: false,
      fog: false,
    })
  );
  glow.scale.setScalar(9);
  glow.position.copy(disc.position);
  scene.add(glow);
}

// --- ocean -----------------------------------------------------------------
const oceanGeo = new THREE.PlaneGeometry(80, 44, 104, 60);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshStandardMaterial({
    color: 0x1b7f9e,
    roughness: 0.35,
    metalness: 0.05,
  })
);
ocean.receiveShadow = true;
scene.add(ocean);

function waveHeight(x, z, t) {
  return (
    0.22 * Math.sin(x * 0.45 + t * 1.2) +
    0.16 * Math.sin(z * 0.7 - t * 1.6) +
    0.09 * Math.sin((x + z) * 0.55 + t * 0.8)
  );
}
function updateOcean(t) {
  const p = oceanGeo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    p.setY(i, waveHeight(x, z, t));
  }
  p.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// --- breaking swell behind the surfer --------------------------------------
const swell = new THREE.Group();
{
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0x2a9db8,
    roughness: 0.45,
    metalness: 0.05,
  });
  const wall = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), wallMat);
  wall.scale.set(11, 2.6, 2.8);
  wall.position.set(0, -0.4, -4.6);
  swell.add(wall);

  const lipMat = new THREE.MeshStandardMaterial({
    color: 0xf4fbff,
    roughness: 0.7,
  });
  const lip = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 20, 12), lipMat);
  lip.rotation.z = Math.PI / 2;
  lip.position.set(0, 1.85, -3.7);
  swell.add(lip);

  // curl rings along the crest for a stylised barrel read
  for (let i = -2; i <= 2; i++) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.9, 0.22, 10, 24, Math.PI * 1.1),
      lipMat
    );
    ring.position.set(i * 3.4, 1.55, -3.8);
    ring.rotation.y = Math.PI / 2;
    ring.rotation.x = 0.5;
    swell.add(ring);
  }

  // foam blobs on the crest
  const foamGeo = new THREE.IcosahedronGeometry(0.32, 1);
  const foamBlobs = new THREE.InstancedMesh(foamGeo, lipMat, 60);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3();
  const v = new THREE.Vector3();
  let seed = 7;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return seed / 2147483647;
  };
  for (let i = 0; i < 60; i++) {
    v.set((rand() - 0.5) * 20, 1.55 + rand() * 0.55, -3.8 + (rand() - 0.5) * 1.4);
    s.setScalar(0.5 + rand() * 1.1);
    q.setFromEuler(new THREE.Euler(rand() * 3, rand() * 3, rand() * 3));
    m.compose(v, q, s);
    foamBlobs.setMatrixAt(i, m);
  }
  swell.add(foamBlobs);
  scene.add(swell);
}

// --- surfboard ---------------------------------------------------------------
const boardGroup = new THREE.Group();
scene.add(boardGroup);
{
  const deckMat = new THREE.MeshStandardMaterial({
    color: 0xff6b4a,
    roughness: 0.5,
  });
  const deck = new THREE.Mesh(new THREE.CapsuleGeometry(0.5, 2.4, 6, 16), deckMat);
  deck.rotation.z = Math.PI / 2; // long axis -> X
  // NOTE: scale applies before rotation, and local X maps to world Y here,
  // so thin the board via local X.
  deck.scale.set(0.32, 1, 1); // thin vertically, full width
  deck.castShadow = true;
  boardGroup.add(deck);

  const stripe = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.16, 2.55, 4, 12),
    new THREE.MeshStandardMaterial({ color: 0xfff6e8, roughness: 0.5 })
  );
  stripe.rotation.z = Math.PI / 2;
  stripe.scale.set(0.55, 1, 1);
  stripe.position.y = 0.14;
  boardGroup.add(stripe);

  const fin = new THREE.Mesh(
    new THREE.ConeGeometry(0.16, 0.5, 8),
    new THREE.MeshStandardMaterial({ color: 0xfff6e8, roughness: 0.6 })
  );
  fin.rotation.x = Math.PI; // point down
  fin.rotation.z = 0.35;
  fin.position.set(-1.1, -0.3, 0);
  boardGroup.add(fin);

  boardGroup.position.y = 0.55;
  boardGroup.rotation.z = 0.05; // nose slightly up
}

// stern wake puffs (ride along with the board)
const wakePuffs = [];
{
  const mat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.8,
    transparent: true,
    opacity: 0.75,
  });
  [-1.7, -2.5, -3.4].forEach((x, i) => {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(0.35, 12, 10), mat.clone());
    puff.scale.set(1.6 - i * 0.2, 0.25, 1.0 - i * 0.15);
    puff.position.set(x, -0.35, 0);
    puff.material.opacity = 0.65 - i * 0.18;
    boardGroup.add(puff);
    wakePuffs.push(puff);
  });
}

// --- pelican (all primitives) ------------------------------------------------
const pelican = new THREE.Group();
boardGroup.add(pelican);
pelican.position.set(0.1, 0.18, 0);

const featherWhite = new THREE.MeshStandardMaterial({ color: 0xf7f4ec, roughness: 0.85 });
const featherGrey = new THREE.MeshStandardMaterial({ color: 0x9aa5ad, roughness: 0.85 });
const featherDark = new THREE.MeshStandardMaterial({ color: 0x5b6670, roughness: 0.85 });
const beakOrange = new THREE.MeshStandardMaterial({ color: 0xf59e2c, roughness: 0.55 });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xef9b5f, roughness: 0.65 });

function shadowed(mesh) {
  mesh.castShadow = true;
  return mesh;
}

// body (long axis -> X, facing +X)
{
  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.55, 28, 22), featherWhite));
  body.scale.set(1.25, 1.0, 0.85);
  body.position.set(0, 0.62, 0);
  body.rotation.z = -0.12;
  pelican.add(body);

  const chest = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.34, 20, 16), featherWhite));
  chest.position.set(0.42, 0.55, 0);
  pelican.add(chest);
}

// legs + feet
{
  const legGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.35, 10);
  [[0.08, 0.18], [0.08, -0.18]].forEach(([x, z]) => {
    const leg = shadowed(new THREE.Mesh(legGeo, beakOrange));
    leg.position.set(x, 0.2, z);
    pelican.add(leg);
    const foot = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 10), beakOrange));
    foot.scale.set(2.0, 0.45, 1.1);
    foot.position.set(x + 0.1, 0.03, z);
    pelican.add(foot);
  });
}

// wings (span along Z, flap around X for balance)
function makeWing(side) {
  const g = new THREE.Group();
  g.position.set(-0.05, 0.78, side * 0.38);
  const inner = shadowed(
    new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.5, 4, 10), featherGrey)
  );
  inner.rotation.x = Math.PI / 2; // axis -> Z
  inner.scale.y = 1;
  inner.scale.x = 1.4;
  inner.position.z = side * 0.32;
  g.add(inner);
  const tip = shadowed(
    new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.35, 4, 10), featherDark)
  );
  tip.rotation.x = Math.PI / 2;
  tip.position.z = side * 0.72;
  g.add(tip);
  pelican.add(g);
  return g;
}
const wingL = makeWing(1);
const wingR = makeWing(-1);

// tail
const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.55, 10), featherGrey));
tail.rotation.z = Math.PI / 2 - 0.35; // tip points back(-X) and up
tail.position.set(-0.72, 0.78, 0);
pelican.add(tail);

// neck + head + beak + pouch
const headGroup = new THREE.Group();
{
  const neck = shadowed(
    new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 0.55, 12), featherWhite)
  );
  neck.position.set(0.42, 1.0, 0);
  neck.rotation.z = -0.45;
  pelican.add(neck);

  headGroup.position.set(0.62, 1.28, 0);
  pelican.add(headGroup);

  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.26, 24, 18), featherWhite));
  headGroup.add(head);

  // swept-back crest feathers
  for (let i = 0; i < 3; i++) {
    const spike = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.3, 8), featherWhite));
    spike.position.set(-0.18 - i * 0.07, 0.2 - i * 0.03, 0);
    spike.rotation.z = Math.PI / 2 + 0.5;
    headGroup.add(spike);
  }

  // eyes
  const eyeGeo = new THREE.SphereGeometry(0.045, 12, 10);
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3 });
  const glintGeo = new THREE.SphereGeometry(0.015, 8, 8);
  const glintMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  [1, -1].forEach((side) => {
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(0.15, 0.07, side * 0.17);
    headGroup.add(eye);
    const glint = new THREE.Mesh(glintGeo, glintMat);
    glint.position.set(0.18, 0.085, side * 0.2);
    headGroup.add(glint);
  });

  // upper beak: long cone pointing +X, tilted slightly down
  const beak = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.085, 0.9, 12), beakOrange));
  beak.rotation.z = -Math.PI / 2 - 0.1;
  beak.position.set(0.62, -0.03, 0);
  headGroup.add(beak);
  const nail = new THREE.Mesh(
    new THREE.ConeGeometry(0.05, 0.14, 10),
    new THREE.MeshStandardMaterial({ color: 0xd97f1e, roughness: 0.5 })
  );
  nail.rotation.z = -Math.PI / 2 - 0.1;
  nail.position.set(1.06, -0.08, 0);
  headGroup.add(nail);
}

// throat pouch (hangs under the beak, wobbles while riding)
const pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.2, 20, 16), pouchMat));
pouch.scale.set(1.7, 1.0, 0.75);
pouch.position.set(0.55, -0.24, 0);
headGroup.add(pouch);

// --- spray particles ---------------------------------------------------------
const SPRAY_N = 240;
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayVel = new Float32Array(SPRAY_N * 3);
const sprayLife = new Float32Array(SPRAY_N);
function resetDrop(i, randomAge) {
  sprayPos[i * 3] = -1.4 + (Math.random() - 0.5) * 0.7;
  sprayPos[i * 3 + 1] = 0.45 + Math.random() * 0.3;
  sprayPos[i * 3 + 2] = (Math.random() - 0.5) * 1.1;
  sprayVel[i * 3] = -1.2 - Math.random() * 1.6;
  sprayVel[i * 3 + 1] = 1.6 + Math.random() * 2.2;
  sprayVel[i * 3 + 2] = (Math.random() - 0.5) * 1.6;
  sprayLife[i] = randomAge ? Math.random() * 1.2 : 0.8 + Math.random() * 0.6;
}
for (let i = 0; i < SPRAY_N; i++) resetDrop(i, true);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({
    size: 0.16,
    map: radialSprite("rgba(255,255,255,1)", "rgba(255,255,255,0)"),
    transparent: true,
    opacity: 0.85,
    depthWrite: false,
    color: 0xffffff,
  })
);
spray.frustumCulled = false;
boardGroup.add(spray);
function updateSpray(dt) {
  for (let i = 0; i < SPRAY_N; i++) {
    sprayLife[i] -= dt;
    if (sprayLife[i] <= 0) {
      resetDrop(i, false);
      continue;
    }
    sprayVel[i * 3 + 1] -= 4.5 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// --- clouds ------------------------------------------------------------------
const clouds = [];
{
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  const spots = [
    [-10, 7.5, -16, 1.6],
    [2, 8.5, -19, 2.1],
    [11, 7, -15, 1.3],
    [7, 6.2, -10, 0.9],
  ];
  spots.forEach(([x, y, z, s]) => {
    const g = new THREE.Group();
    for (let i = 0; i < 5; i++) {
      const puff = new THREE.Mesh(new THREE.SphereGeometry(0.6, 14, 12), mat);
      puff.position.set((i - 2) * 0.75, (i % 2) * 0.25, (i % 3) * 0.2 - 0.2);
      puff.scale.setScalar(0.7 + ((i * 37) % 10) / 18);
      g.add(puff);
    }
    g.position.set(x, y, z);
    g.scale.setScalar(s);
    scene.add(g);
    clouds.push({ g, speed: 0.12 + s * 0.06 });
  });
}

// --- distant gulls -------------------------------------------------------------
const gulls = [];
{
  const mat = new THREE.MeshBasicMaterial({ color: 0x3d4a54 });
  for (let i = 0; i < 3; i++) {
    const g = new THREE.Group();
    const wingGeo = new THREE.BoxGeometry(0.12, 0.03, 0.55);
    wingGeo.translate(0, 0, 0.27);
    const wl = new THREE.Mesh(wingGeo, mat);
    const wr = new THREE.Mesh(wingGeo, mat);
    wr.rotation.y = Math.PI;
    g.add(wl, wr);
    g.position.set(-14 + i * 7, 5.4 + i * 0.7, -8 - i * 2);
    scene.add(g);
    gulls.push({ g, wl, wr, phase: i * 2.1, speed: 0.9 + i * 0.25 });
  }
}

// --- animation -----------------------------------------------------------------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // ocean swell
  updateOcean(t);

  // board: bob, roll and pitch on the waves
  const bobY = 0.55 + waveHeight(0, 0, t) * 0.45 + 0.05 * Math.sin(t * 2.1);
  const roll = 0.09 * Math.sin(t * 1.3);
  const pitch = 0.05 * Math.sin(t * 1.1 + 1.0);
  boardGroup.position.y = bobY;
  boardGroup.position.x = 0.15 * Math.sin(t * 0.7);
  boardGroup.rotation.x = roll;
  boardGroup.rotation.z = 0.05 + pitch;

  // pelican: crouch, lean into the roll, wobble the pouch
  pelican.rotation.x = -roll * 0.7;
  pelican.rotation.z = -0.06 + 0.03 * Math.sin(t * 1.7);
  pelican.position.y = 0.18 + 0.02 * Math.sin(t * 2.6);

  // wings flap gently to keep balance (mirrored)
  const flap = 0.42 * Math.sin(t * 2.4) + 0.1 * Math.sin(t * 4.1);
  wingL.rotation.x = 0.3 + flap;
  wingR.rotation.x = -0.3 - flap;
  wingL.rotation.y = 0.15 * Math.sin(t * 1.2);
  wingR.rotation.y = -0.15 * Math.sin(t * 1.2);

  // head looks around, pouch wobbles
  headGroup.rotation.y = 0.35 * Math.sin(t * 0.5);
  headGroup.rotation.z = 0.08 * Math.sin(t * 0.9 + 0.4);
  pouch.scale.set(1.7, 1.0 + 0.07 * Math.sin(t * 2.5), 0.75);
  tail.rotation.y = 0.25 * Math.sin(t * 1.9);

  // wake puffs pulse
  wakePuffs.forEach((p, i) => {
    const k = 1 + 0.12 * Math.sin(t * 3 + i * 1.7);
    p.scale.set((1.6 - i * 0.2) * k, 0.25, (1.0 - i * 0.15) * k);
  });

  // spray, clouds, gulls
  updateSpray(dt);
  clouds.forEach((c) => {
    c.g.position.x += c.speed * dt;
    if (c.g.position.x > 22) c.g.position.x = -22;
  });
  gulls.forEach((gu) => {
    gu.g.position.x += gu.speed * dt;
    if (gu.g.position.x > 20) gu.g.position.x = -20;
    const f = 0.55 * Math.sin(t * 6 + gu.phase);
    gu.wl.rotation.x = f;
    gu.wr.rotation.x = -f;
  });

  // slow cinematic drift (no user control — still non-interactive)
  camera.position.set(
    CAM_BASE.x + 0.5 * Math.sin(t * 0.1),
    CAM_BASE.y + 0.15 * Math.sin(t * 0.13 + 1),
    CAM_BASE.z
  );
  camera.lookAt(CAM_LOOK);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
