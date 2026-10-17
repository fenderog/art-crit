import * as THREE from "three";

// ---------------------------------------------------------------------------
// Renderer / Scene / Camera
// ---------------------------------------------------------------------------
const container = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c5e8);
scene.fog = new THREE.Fog(0x87c5e8, 60, 220);

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);
camera.position.set(0, 6, 16);

// ---------------------------------------------------------------------------
// Sky gradient dome (drawn behind everything)
// ---------------------------------------------------------------------------
{
  const skyGeo = new THREE.SphereGeometry(400, 32, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x3f8fd8) },
      bottomColor: { value: new THREE.Color(0xcfe9f7) },
      offset: { value: 40 },
      exponent: { value: 0.7 },
    },
    vertexShader: /* glsl */ `
      varying vec3 vWorldPos;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorldPos = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 topColor;
      uniform vec3 bottomColor;
      uniform float offset;
      uniform float exponent;
      varying vec3 vWorldPos;
      void main() {
        float h = normalize(vWorldPos + vec3(0.0, offset, 0.0)).y;
        gl_FragColor = vec4(mix(bottomColor, topColor, pow(max(h, 0.0), exponent)), 1.0);
      }
    `,
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
}

// ---------------------------------------------------------------------------
// Lights
// ---------------------------------------------------------------------------
const hemi = new THREE.HemisphereLight(0xbfe3ff, 0x2a6f9e, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff2d8, 1.6);
sun.position.set(-30, 45, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -25;
sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;
sun.shadow.camera.bottom = -25;
sun.shadow.camera.far = 150;
scene.add(sun);

// Sun disc
{
  const sunMat = new THREE.SpriteMaterial({
    map: makeGlowTexture(),
    color: 0xfff6d0,
    fog: false,
    depthWrite: false,
  });
  const sunSprite = new THREE.Sprite(sunMat);
  sunSprite.position.set(-140, 70, -260);
  sunSprite.scale.set(70, 70, 1);
  scene.add(sunSprite);
}

function makeGlowTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, "rgba(255,255,240,1)");
  g.addColorStop(0.35, "rgba(255,244,200,0.9)");
  g.addColorStop(1, "rgba(255,240,190,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  return tex;
}

// ---------------------------------------------------------------------------
// Ocean — vertex-displaced plane driven by a shared wave function
// ---------------------------------------------------------------------------
const WAVE = {
  // shared height function so the board rides exactly on the surface
  height(x, z, t) {
    return (
      Math.sin(x * 0.35 + t * 1.1) * 0.55 +
      Math.sin(z * 0.28 - t * 0.9) * 0.45 +
      Math.sin((x + z) * 0.18 + t * 0.7) * 0.7 +
      Math.sin(x * 0.9 + z * 0.6 - t * 1.7) * 0.12
    );
  },
  slope(x, z, t) {
    const e = 0.25;
    const dx = (this.height(x + e, z, t) - this.height(x - e, z, t)) / (2 * e);
    const dz = (this.height(x, z + e, t) - this.height(x, z - e, t)) / (2 * e);
    return { dx, dz };
  },
};

const oceanGeo = new THREE.PlaneGeometry(400, 400, 140, 140);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1a7f9e,
  roughness: 0.25,
  metalness: 0.1,
  flatShading: false,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

const oceanPos = oceanGeo.attributes.position;
const oceanBase = oceanPos.array.slice(); // keep base positions

function updateOcean(t) {
  const arr = oceanPos.array;
  for (let i = 0; i < arr.length; i += 3) {
    const x = oceanBase[i];
    const z = oceanBase[i + 2];
    arr[i + 1] = WAVE.height(x, z, t);
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// Foam streaks (flat translucent quads drifting on the surface)
const foamGroup = new THREE.Group();
scene.add(foamGroup);
{
  const foamMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.35,
    depthWrite: false,
  });
  for (let i = 0; i < 24; i++) {
    const f = new THREE.Mesh(
      new THREE.PlaneGeometry(3 + Math.random() * 5, 0.5 + Math.random() * 0.8, 12, 1),
      foamMat.clone()
    );
    f.rotation.x = -Math.PI / 2;
    f.userData = {
      x: (Math.random() - 0.5) * 90,
      z: (Math.random() - 0.5) * 90,
      drift: 0.5 + Math.random() * 1.5,
      phase: Math.random() * Math.PI * 2,
    };
    foamGroup.add(f);
  }
}

// ---------------------------------------------------------------------------
// Surfboard + Pelican rig
// ---------------------------------------------------------------------------
const surfer = new THREE.Group(); // positioned on the wave
scene.add(surfer);

// -- Surfboard --------------------------------------------------------------
function buildBoard() {
  const board = new THREE.Group();

  // Deck shape via extruded outline
  const shape = new THREE.Shape();
  const L = 3.4, W = 0.62;
  shape.moveTo(-L, 0);
  shape.bezierCurveTo(-L * 0.55, W, L * 0.5, W, L, 0);
  shape.bezierCurveTo(L * 0.5, -W, -L * 0.55, -W, -L, 0);

  const deckGeo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.16,
    bevelEnabled: true,
    bevelThickness: 0.05,
    bevelSize: 0.05,
    bevelSegments: 3,
    curveSegments: 24,
  });
  deckGeo.rotateX(-Math.PI / 2);
  deckGeo.translate(0, 0.05, 0);
  const deck = new THREE.Mesh(
    deckGeo,
    new THREE.MeshStandardMaterial({ color: 0xf7e9c9, roughness: 0.5 })
  );
  deck.castShadow = true;
  board.add(deck);

  // Stripe
  const stripeGeo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.185,
    bevelEnabled: false,
    curveSegments: 24,
  });
  stripeGeo.rotateX(-Math.PI / 2);
  stripeGeo.scale(0.18, 1, 1.05);
  stripeGeo.translate(0.5, 0.05, 0);
  const stripe = new THREE.Mesh(
    stripeGeo,
    new THREE.MeshStandardMaterial({ color: 0xe0562f, roughness: 0.45 })
  );
  board.add(stripe);

  // Fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.5, 0);
  finShape.quadraticCurveTo(0.35, -0.55, -0.1, -0.5);
  finShape.quadraticCurveTo(-0.05, -0.2, 0, 0);
  const fin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(finShape, {
      depth: 0.06,
      bevelEnabled: false,
      curveSegments: 10,
    }),
    new THREE.MeshStandardMaterial({ color: 0xe0562f, roughness: 0.4 })
  );
  fin.rotation.y = Math.PI / 2;
  fin.position.set(-2.6, -0.02, 0.03);
  board.add(fin);

  return board;
}
const board = buildBoard();
surfer.add(board);

// -- Pelican ----------------------------------------------------------------
const pelican = new THREE.Group();
pelican.position.set(0.2, 0.2, 0);
surfer.add(pelican);

const matBody = new THREE.MeshStandardMaterial({ color: 0xf4f1ea, roughness: 0.75 });
const matWing = new THREE.MeshStandardMaterial({ color: 0xd8d2c4, roughness: 0.8 });
const matBeak = new THREE.MeshStandardMaterial({ color: 0xf2a93b, roughness: 0.45 });
const matPouch = new THREE.MeshStandardMaterial({ color: 0xf6c05a, roughness: 0.5 });
const matDark = new THREE.MeshStandardMaterial({ color: 0x2a2622, roughness: 0.6 });

// Body
{
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.62, 24, 18), matBody);
  body.scale.set(1.25, 0.95, 0.9);
  body.position.set(0, 0.85, 0);
  body.castShadow = true;
  pelican.add(body);

  // Tail feathers
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.7, 12), matWing);
  tail.rotation.z = Math.PI / 2 + 0.35;
  tail.scale.set(1, 1, 0.5);
  tail.position.set(-0.85, 1.0, 0);
  tail.castShadow = true;
  pelican.add(tail);
}

// Neck + head group (bobs / leans)
const headGroup = new THREE.Group();
headGroup.position.set(0.55, 1.15, 0);
pelican.add(headGroup);
{
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.24, 0.75, 12), matBody);
  neck.position.set(-0.05, 0.25, 0);
  neck.rotation.z = -0.35;
  neck.castShadow = true;
  headGroup.add(neck);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 20, 16), matBody);
  head.position.set(0.15, 0.62, 0);
  head.scale.set(1.1, 0.95, 0.9);
  head.castShadow = true;
  headGroup.add(head);

  // Eyes
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), matDark);
    eye.position.set(0.32, 0.68, side * 0.18);
    headGroup.add(eye);
  }

  // Upper beak
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.13, 1.15, 12), matBeak);
  beak.rotation.z = -Math.PI / 2 - 0.08;
  beak.scale.set(1, 1, 0.7);
  beak.position.set(0.85, 0.62, 0);
  beak.castShadow = true;
  headGroup.add(beak);

  // Throat pouch (hangs under beak, wobbles)
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 12), matPouch);
  pouch.scale.set(2.1, 0.85, 0.85);
  pouch.position.set(0.72, 0.46, 0);
  pouch.castShadow = true;
  headGroup.add(pouch);
  pelican.userData.pouch = pouch;
}

// Wings — pivot at shoulder, flap in a surfing "balance" motion
function buildWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(-0.15, 1.25, side * 0.42);

  const wing = new THREE.Mesh(new THREE.SphereGeometry(0.5, 18, 12), matWing);
  wing.scale.set(1.7, 0.12, 0.72);
  wing.position.set(-0.25, 0, side * 0.45);
  wing.rotation.y = side * 0.25;
  wing.castShadow = true;
  pivot.add(wing);

  // wing tip
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.6, 10), matWing);
  tip.scale.set(1, 1, 0.4);
  tip.rotation.z = Math.PI / 2;
  tip.rotation.y = side * 0.25;
  tip.position.set(-0.95, 0, side * 0.85);
  pivot.add(tip);

  return pivot;
}
const wingL = buildWing(1);
const wingR = buildWing(-1);
pelican.add(wingL, wingR);

// Legs + webbed feet planted on the board
for (const side of [-1, 1]) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.5, 8), matBeak);
  leg.position.set(side * 0.1, 0.32, side * 0.22);
  leg.rotation.x = side * 0.15;
  leg.castShadow = true;
  pelican.add(leg);

  const foot = new THREE.Mesh(new THREE.SphereGeometry(0.14, 10, 8), matBeak);
  foot.scale.set(1.6, 0.35, 1.1);
  foot.position.set(side * 0.1 + 0.08, 0.09, side * 0.24);
  foot.castShadow = true;
  pelican.add(foot);
}

// ---------------------------------------------------------------------------
// Spray particles behind the board
// ---------------------------------------------------------------------------
const SPRAY_COUNT = 140;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_COUNT * 3);
const sprayData = [];
for (let i = 0; i < SPRAY_COUNT; i++) {
  sprayData.push({
    life: Math.random(),
    speed: 1.5 + Math.random() * 2.5,
    dx: -1,
    dy: 0.4 + Math.random() * 1.2,
    dz: (Math.random() - 0.5) * 1.4,
  });
  sprayPos.set([0, -10, 0], i * 3);
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const sprayMat = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 0.14,
  transparent: true,
  opacity: 0.8,
  depthWrite: false,
});
const spray = new THREE.Points(sprayGeo, sprayMat);
scene.add(spray);

function updateSpray(dt, t) {
  const arr = sprayGeo.attributes.position.array;
  const origin = new THREE.Vector3();
  surfer.localToWorld(origin.set(-2.9, -0.1, 0));
  for (let i = 0; i < SPRAY_COUNT; i++) {
    const d = sprayData[i];
    d.life -= dt * 0.9;
    if (d.life <= 0) {
      d.life = 1;
      arr[i * 3] = origin.x + (Math.random() - 0.5) * 0.4;
      arr[i * 3 + 1] = origin.y + Math.random() * 0.3;
      arr[i * 3 + 2] = origin.z + (Math.random() - 0.5) * 0.8;
      d.speed = 1.5 + Math.random() * 2.5;
      d.dy = 0.4 + Math.random() * 1.2;
      d.dz = (Math.random() - 0.5) * 1.4;
    } else {
      arr[i * 3] += d.dx * d.speed * dt;
      arr[i * 3 + 1] += d.dy * dt;
      arr[i * 3 + 2] += d.dz * dt;
      d.dy -= 3.2 * dt; // gravity
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// Clouds
// ---------------------------------------------------------------------------
const clouds = new THREE.Group();
scene.add(clouds);
{
  const cloudMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 1,
    flatShading: true,
  });
  for (let i = 0; i < 10; i++) {
    const cloud = new THREE.Group();
    const puffs = 3 + Math.floor(Math.random() * 4);
    for (let j = 0; j < puffs; j++) {
      const puff = new THREE.Mesh(
        new THREE.SphereGeometry(1.2 + Math.random() * 1.6, 10, 8),
        cloudMat
      );
      puff.position.set(j * 1.8 + Math.random(), Math.random() * 0.6, Math.random() * 1.2);
      puff.scale.y = 0.55;
      cloud.add(puff);
    }
    cloud.position.set(
      (Math.random() - 0.5) * 260,
      26 + Math.random() * 20,
      -60 - Math.random() * 160
    );
    cloud.userData.speed = 0.4 + Math.random() * 0.8;
    clouds.add(cloud);
  }
}

// ---------------------------------------------------------------------------
// Distant gulls (little V shapes circling)
// ---------------------------------------------------------------------------
const gulls = [];
{
  const gullMat = new THREE.MeshBasicMaterial({ color: 0x33414d, side: THREE.DoubleSide });
  for (let i = 0; i < 5; i++) {
    const g = new THREE.Group();
    for (const side of [-1, 1]) {
      const wShape = new THREE.Shape();
      wShape.moveTo(0, 0);
      wShape.quadraticCurveTo(0.4, 0.25, 0.9, 0.05);
      wShape.quadraticCurveTo(0.45, 0.02, 0, -0.08);
      const w = new THREE.Mesh(new THREE.ShapeGeometry(wShape, 8), gullMat);
      w.scale.x = side;
      g.add(w);
    }
    g.userData = {
      radius: 22 + Math.random() * 16,
      height: 14 + Math.random() * 8,
      speed: 0.15 + Math.random() * 0.15,
      phase: Math.random() * Math.PI * 2,
      flapSpeed: 6 + Math.random() * 4,
    };
    scene.add(g);
    gulls.push(g);
  }
}

// ---------------------------------------------------------------------------
// Animation loop
// ---------------------------------------------------------------------------
const clock = new THREE.Clock();
const BOARD_X = 0;
const BOARD_Z = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Ocean
  updateOcean(t);

  // Foam drifts and hugs the surface
  for (const f of foamGroup.children) {
    const u = f.userData;
    const x = u.x + Math.sin(t * 0.1 + u.phase) * 3;
    const z = (((u.z - t * u.drift + 45) % 90) + 90) % 90 - 45;
    f.position.set(x, WAVE.height(x, z, t) + 0.06, z);
    f.material.opacity = 0.18 + 0.17 * Math.sin(t * 1.3 + u.phase);
  }

  // Surfer rides the wave: position + tilt from slope
  const h = WAVE.height(BOARD_X, BOARD_Z, t);
  const s = WAVE.slope(BOARD_X, BOARD_Z, t);
  surfer.position.set(BOARD_X, h + 0.12, BOARD_Z);
  surfer.rotation.z = Math.atan2(s.dx, 1) * 0.9; // tilt along wave slope
  surfer.rotation.x = -Math.atan2(s.dz, 1) * 0.9;
  // gentle extra carve left/right
  const carve = Math.sin(t * 0.5) * 0.12;
  surfer.rotation.y = carve;
  surfer.position.x = Math.sin(t * 0.5) * 1.4;

  // Pelican body language
  pelican.rotation.z = -carve * 0.6 + Math.sin(t * 2.1) * 0.02;
  pelican.position.y = 0.2 + Math.abs(Math.sin(t * 1.4)) * 0.03; // subtle crouch

  // Wings: outstretched for balance, quick corrective flaps
  const flap =
    Math.sin(t * 2.6) * 0.22 +
    Math.max(0, Math.sin(t * 0.8)) * Math.sin(t * 9.0) * 0.5; // occasional burst
  wingL.rotation.x = -0.15 + flap;
  wingR.rotation.x = 0.15 - flap;
  wingL.rotation.z = 0.1 + flap * 0.3;
  wingR.rotation.z = -0.1 - flap * 0.3;

  // Head: looks around, pouch wobbles with motion
  headGroup.rotation.z = Math.sin(t * 0.7) * 0.12;
  headGroup.rotation.y = Math.sin(t * 0.45 + 1.3) * 0.4;
  pelican.userData.pouch.scale.y =
    0.85 + Math.sin(t * 3.3) * 0.06 + Math.abs(s.dx) * 0.1;

  // Spray behind the board
  updateSpray(dt, t);

  // Clouds drift
  for (const c of clouds.children) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 160) c.position.x = -160;
  }

  // Gulls circle and flap
  for (const g of gulls) {
    const u = g.userData;
    const a = t * u.speed + u.phase;
    g.position.set(Math.cos(a) * u.radius, u.height + Math.sin(t * 0.5 + u.phase) * 1.5, Math.sin(a) * u.radius - 20);
    g.rotation.y = -a + Math.PI / 2;
    const flapA = Math.sin(t * u.flapSpeed + u.phase) * 0.6;
    g.children[0].rotation.y = flapA;
    g.children[1].rotation.y = -flapA;
  }

  // Camera: slow cinematic orbit, no user input needed
  const camA = t * 0.12;
  const camR = 13 + Math.sin(t * 0.23) * 3.5;
  const camY = 5.2 + Math.sin(t * 0.31) * 1.6;
  camera.position.set(Math.sin(camA) * camR, camY, Math.cos(camA) * camR);
  camera.lookAt(surfer.position.x * 0.6, surfer.position.y + 1.4, 0);

  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
