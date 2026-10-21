import * as THREE from "three";

/* ============================================================
   Surfing Pelican — an animated, non-interactive WebGL scene.
   A pelican built from Three.js primitives rides a surfboard
   over a procedurally displaced ocean. Everything (sky, sun,
   clouds, birds, board, pelican, spray) is generated in code:
   no external assets, no network requests, no storage.
   ============================================================ */

// ------------------------------------------------------------
// Wave field — a single definition shared by the GLSL ocean
// shader and the JS logic that keeps the board on the surface.
// ------------------------------------------------------------
const waves = [
  { amp: 0.55, freq: 0.32, speed: 1.1, dir: [1.0, 0.35] },
  { amp: 0.32, freq: 0.58, speed: 1.7, dir: [0.75, -0.65] },
  { amp: 0.18, freq: 1.15, speed: 2.4, dir: [-0.7, 0.9] },
  { amp: 0.09, freq: 2.3, speed: 3.2, dir: [0.45, 0.55] },
];

const f = (n) => n.toFixed(4);
const phaseExpr = (w) =>
  `${f(w.freq)} * (x * ${f(w.dir[0])} + z * ${f(w.dir[1])}) + uTime * ${f(w.speed)}`;

const heightGLSL = waves
  .map((w) => `  h += ${f(w.amp)} * sin(${phaseExpr(w)});`)
  .join("\n");

const slopeGLSL = waves
  .map(
    (w) => `  dhdx += ${f(w.amp * w.freq * w.dir[0])} * cos(${phaseExpr(w)});
  dhdz += ${f(w.amp * w.freq * w.dir[1])} * cos(${phaseExpr(w)});`
  )
  .join("\n");

function waveHeight(x, z, t) {
  let h = 0;
  for (const w of waves) {
    h += w.amp * Math.sin(w.freq * (x * w.dir[0] + z * w.dir[1]) + t * w.speed);
  }
  return h;
}

function waveSlope(x, z, t) {
  let dx = 0;
  let dz = 0;
  for (const w of waves) {
    const a = w.freq * (x * w.dir[0] + z * w.dir[1]) + t * w.speed;
    dx += w.amp * w.freq * w.dir[0] * Math.cos(a);
    dz += w.amp * w.freq * w.dir[1] * Math.cos(a);
  }
  return [dx, dz];
}

// ------------------------------------------------------------
// Renderer / scene / camera
// ------------------------------------------------------------
const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ------------------------------------------------------------
// Canvas-generated textures (radial gradients, no asset files)
// ------------------------------------------------------------
function makeRadialTexture(stops, size = 64) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  for (const [o, col] of stops) g.addColorStop(o, col);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const dotTexture = makeRadialTexture([
  [0, "rgba(255,255,255,1)"],
  [0.4, "rgba(255,255,255,0.55)"],
  [1, "rgba(255,255,255,0)"],
]);

const glowTexture = makeRadialTexture(
  [
    [0, "rgba(255,255,255,0.9)"],
    [0.25, "rgba(255,240,200,0.45)"],
    [0.6, "rgba(255,220,160,0.12)"],
    [1, "rgba(255,220,160,0)"],
  ],
  128
);

// ------------------------------------------------------------
// Sky: gradient sphere + sun + glow
// ------------------------------------------------------------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(400, 32, 24),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        float h = clamp(normalize(vDir).y * 0.5 + 0.5, 0.0, 1.0);
        vec3 top = vec3(0.30, 0.60, 0.90);
        vec3 mid = vec3(0.66, 0.85, 0.95);
        vec3 bottom = vec3(1.0, 0.89, 0.76);
        vec3 col = mix(bottom, mid, smoothstep(0.35, 0.55, h));
        col = mix(col, top, smoothstep(0.55, 0.85, h));
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  })
);
scene.add(sky);

const sunDir = new THREE.Vector3(0.45, 0.75, 0.35).normalize();

const sun = new THREE.Mesh(
  new THREE.SphereGeometry(7, 32, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff2c4 })
);
sun.position.copy(sunDir).multiplyScalar(320);
scene.add(sun);

const sunGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: glowTexture,
    color: 0xffe9b0,
    transparent: true,
    blending: THREE.AdditiveBlending,
    opacity: 0.85,
    depthWrite: false,
  })
);
sunGlow.position.copy(sun.position);
sunGlow.scale.set(80, 80, 1);
scene.add(sunGlow);

// ------------------------------------------------------------
// Lights
// ------------------------------------------------------------
const sunLight = new THREE.DirectionalLight(0xfff1dc, 1.7);
sunLight.position.copy(sunDir).multiplyScalar(100);
scene.add(sunLight);
scene.add(new THREE.HemisphereLight(0xbfe8ff, 0xffe8c8, 0.55));

// ------------------------------------------------------------
// Ocean: high-segment plane displaced by a custom shader
// ------------------------------------------------------------
const oceanGeo = new THREE.PlaneGeometry(420, 420, 180, 180);
oceanGeo.rotateX(-Math.PI / 2); // bake "flat" so local x/z == world x/z

const oceanMat = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uSunDir: { value: sunDir },
    uCamPos: { value: new THREE.Vector3() },
  },
  vertexShader: /* glsl */ `
    uniform float uTime;
    varying vec3 vNormal;
    varying float vHeight;
    varying vec3 vWorldPos;
    void main() {
      vec3 p = position;
      float x = p.x;
      float z = p.z;
      float h = 0.0;
      float dhdx = 0.0;
      float dhdz = 0.0;
${heightGLSL}
${slopeGLSL}
      p.y += h;
      vHeight = h;
      vNormal = normalize(vec3(-dhdx, 1.0, -dhdz));
      vWorldPos = p;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform vec3 uSunDir;
    uniform vec3 uCamPos;
    varying vec3 vNormal;
    varying float vHeight;
    varying vec3 vWorldPos;
    void main() {
      vec3 N = normalize(vNormal);
      vec3 L = normalize(uSunDir);
      float diff = max(dot(N, L), 0.0);

      vec3 deep = vec3(0.03, 0.22, 0.42);
      vec3 shallow = vec3(0.12, 0.58, 0.62);
      vec3 base = mix(deep, shallow, smoothstep(-0.7, 0.9, vHeight));
      vec3 col = base * (0.35 + 0.75 * diff);

      // sun glint
      vec3 V = normalize(uCamPos - vWorldPos);
      vec3 H = normalize(L + V);
      col += vec3(1.0, 0.98, 0.9) * pow(max(dot(N, H), 0.0), 70.0) * 0.8;

      // foam on the crests
      float foam = smoothstep(0.6, 0.95, vHeight);
      col = mix(col, vec3(0.95, 0.98, 1.0), foam * 0.85);

      // haze toward the horizon
      float d = distance(uCamPos, vWorldPos);
      col = mix(col, vec3(1.0, 0.89, 0.76), smoothstep(55.0, 150.0, d));

      gl_FragColor = vec4(col, 1.0);
    }
  `,
});

const ocean = new THREE.Mesh(oceanGeo, oceanMat);
scene.add(ocean);

// ------------------------------------------------------------
// Clouds (drifting puff-balls)
// ------------------------------------------------------------
const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1.0 });
const clouds = [];

function makeCloud(x, y, z, s) {
  const c = new THREE.Group();
  const puffs = [
    [0, 0, 0, 1.0],
    [0.95, 0.18, 0.15, 0.75],
    [-0.9, 0.12, -0.2, 0.7],
    [0.45, -0.22, 0.1, 0.6],
    [-0.45, -0.18, -0.15, 0.55],
    [0.1, 0.3, -0.1, 0.55],
  ];
  for (const [px, py, pz, r] of puffs) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 20, 14), cloudMat);
    m.position.set(px, py, pz);
    c.add(m);
  }
  c.position.set(x, y, z);
  c.scale.setScalar(s);
  scene.add(c);
  clouds.push({ g: c, speed: 0.6 + Math.random() * 1.2 });
}

makeCloud(-30, 26, -70, 3.2);
makeCloud(15, 34, -90, 4.0);
makeCloud(55, 22, -55, 2.4);
makeCloud(-65, 40, -45, 3.4);
makeCloud(35, 48, -110, 5.0);
makeCloud(-5, 18, -35, 1.8);

// ------------------------------------------------------------
// Distant birds (two-cone silhouettes on lazy circles)
// ------------------------------------------------------------
const birdMat = new THREE.MeshStandardMaterial({ color: 0x33414e, roughness: 0.8 });
const birds = [];

function makeBird(radius, height, speed, phase) {
  const b = new THREE.Group();
  const wings = [];
  for (const s of [-1, 1]) {
    const wing = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.45, 8), birdMat);
    wing.rotation.x = s * (Math.PI / 2 - 0.55);
    wing.position.z = 0.02 * s;
    b.add(wing);
    wings.push({ m: wing, s });
  }
  scene.add(b);
  birds.push({ g: b, wings, radius, height, speed, phase });
}

makeBird(34, 20, 0.10, 0.0);
makeBird(48, 27, 0.07, 2.1);
makeBird(26, 15, 0.13, 4.2);

// ------------------------------------------------------------
// Surfboard (extruded outline, lying flat, nose toward +x)
// ------------------------------------------------------------
function buildSurfboard() {
  const shape = new THREE.Shape();
  shape.moveTo(2.3, 0);
  shape.quadraticCurveTo(1.4, 0.26, 0.4, 0.3);
  shape.quadraticCurveTo(-1.0, 0.34, -1.5, 0.24);
  shape.quadraticCurveTo(-2.1, 0.14, -2.1, 0.0);
  shape.quadraticCurveTo(-2.1, -0.14, -1.5, -0.24);
  shape.quadraticCurveTo(-1.0, -0.34, 0.4, -0.3);
  shape.quadraticCurveTo(1.4, -0.26, 2.3, 0);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.14,
    bevelEnabled: true,
    bevelThickness: 0.06,
    bevelSize: 0.05,
    bevelSegments: 4,
    curveSegments: 32,
  });
  geo.rotateX(-Math.PI / 2);
  geo.center();

  const board = new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({ color: 0xff6b5e, roughness: 0.55, metalness: 0.05 })
  );

  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(3.6, 0.02, 0.1),
    new THREE.MeshStandardMaterial({ color: 0xfff3e0, roughness: 0.6 })
  );
  stripe.position.y = 0.14;
  board.add(stripe);

  return board;
}

// ------------------------------------------------------------
// Pelican (primitives: body, neck, head, beak + pouch, eyes,
// flapping wings with dark tips, tail, feet)
// ------------------------------------------------------------
function buildPelican() {
  const g = new THREE.Group();

  const ivory = new THREE.MeshStandardMaterial({ color: 0xfbf3df, roughness: 0.85 });
  const grey = new THREE.MeshStandardMaterial({ color: 0x5c6670, roughness: 0.8 });
  const orange = new THREE.MeshStandardMaterial({ color: 0xff9440, roughness: 0.6 });
  const pouchMat = new THREE.MeshStandardMaterial({ color: 0xffc08a, roughness: 0.75 });

  // webbed feet on the deck
  for (const z of [-0.2, 0.2]) {
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.1, 0.14), orange);
    foot.position.set(0.15, 0.05, z);
    g.add(foot);
  }

  // body
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), ivory);
  body.scale.set(1.05, 0.78, 1.4);
  body.position.set(0.05, 0.86, 0);
  g.add(body);

  // tail
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.34, 1.0, 20), grey);
  tail.position.set(-1.05, 0.78, 0);
  tail.rotation.z = Math.PI / 2 + 0.45; // points back and slightly down
  g.add(tail);

  // neck
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 1.0, 20), ivory);
  neck.position.set(0.85, 1.5, 0);
  neck.rotation.z = -0.5; // leans forward, visible between body and head
  g.add(neck);

  // head group (head + beak + pouch + eyes) — gently nods
  const head = new THREE.Group();
  head.position.set(1.15, 2.12, 0);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.34, 32, 24), ivory);
  head.add(skull);

  // long beak, angled slightly down
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.09, 1.35, 20), orange);
  beak.position.set(0.3, -0.05, 0);
  beak.rotation.z = -(Math.PI / 2 + 0.3);
  head.add(beak);

  // pouch hanging under the beak
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.18, 24, 16), pouchMat);
  pouch.scale.set(2.6, 0.9, 0.85);
  pouch.position.set(0.78, -0.26, 0);
  pouch.rotation.z = 0.18;
  head.add(pouch);

  // eyes
  const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
  const pupilMat = new THREE.MeshStandardMaterial({ color: 0x20242a, roughness: 0.2 });
  for (const s of [-1, 1]) {
    const eyeWhite = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 12), eyeWhiteMat);
    eyeWhite.position.set(0.16, 0.1, 0.24 * s);
    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.038, 12, 10), pupilMat);
    pupil.position.set(0.19, 0.1, 0.28 * s);
    head.add(eyeWhite, pupil);
  }
  g.add(head);

  // flapping wings with dark tips
  const wings = [];
  for (const s of [-1, 1]) {
    const wing = new THREE.Group();
    wing.position.set(-0.15, 0.95, 0.42 * s);

    const feather = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 16), ivory);
    feather.scale.set(1.0, 0.32, 1.5);
    feather.position.set(-0.55, 0.0, 0.72 * s);
    wing.add(feather);

    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.3, 20, 14), grey);
    tip.scale.set(0.9, 0.8, 1.0);
    tip.position.set(-1.15, -0.02, 1.35 * s);
    wing.add(tip);

    g.add(wing);
    wings.push({ g: wing, s });
  }

  return { group: g, head, wings };
}

// ------------------------------------------------------------
// Surf rig: board + pelican, riding the wave field
// ------------------------------------------------------------
const surf = new THREE.Group();
scene.add(surf);

surf.add(buildSurfboard());

const pelican = buildPelican();
pelican.group.position.y = 0.12; // feet on the deck
surf.add(pelican.group);

// ------------------------------------------------------------
// Spray particles off the board's nose
// ------------------------------------------------------------
const SPRAY_COUNT = 90;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_COUNT * 3);
const sprayCol = new Float32Array(SPRAY_COUNT * 3);
const sprayVel = new Float32Array(SPRAY_COUNT * 3);
const sprayLife = new Float32Array(SPRAY_COUNT);
const sprayMaxLife = new Float32Array(SPRAY_COUNT);

sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
sprayGeo.setAttribute("color", new THREE.BufferAttribute(sprayCol, 3));

const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({
    size: 0.3,
    map: dotTexture,
    transparent: true,
    vertexColors: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })
);
spray.frustumCulled = false;
scene.add(spray);

const noseLocal = new THREE.Vector3(2.2, 0.18, 0);
const noseWorld = new THREE.Vector3();
const headWorld = new THREE.Vector3();

function updateSpray(dt) {
  noseWorld.copy(noseLocal).applyMatrix4(surf.matrixWorld);
  headWorld.set(1, 0, 0).transformDirection(surf.matrixWorld);

  for (let i = 0; i < SPRAY_COUNT; i++) {
    sprayLife[i] -= dt;
    if (sprayLife[i] <= 0) {
      // (re)spawn at the nose
      sprayMaxLife[i] = 0.5 + Math.random() * 0.9;
      sprayLife[i] = sprayMaxLife[i];
      sprayPos[i * 3] = noseWorld.x + (Math.random() - 0.5) * 0.35;
      sprayPos[i * 3 + 1] = noseWorld.y + Math.random() * 0.2;
      sprayPos[i * 3 + 2] = noseWorld.z + (Math.random() - 0.5) * 0.35;
      const back = 1.2 + Math.random() * 2.2;
      sprayVel[i * 3] = -headWorld.x * back + (Math.random() - 0.5) * 0.8;
      sprayVel[i * 3 + 1] = 0.8 + Math.random() * 2.2;
      sprayVel[i * 3 + 2] = -headWorld.z * back + (Math.random() - 0.5) * 0.8;
      sprayCol[i * 3] = 1;
      sprayCol[i * 3 + 1] = 1;
      sprayCol[i * 3 + 2] = 1;
      continue;
    }
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
    sprayVel[i * 3 + 1] -= 6.0 * dt;

    const k = Math.max(sprayLife[i] / sprayMaxLife[i], 0);
    sprayCol[i * 3] = k;
    sprayCol[i * 3 + 1] = k;
    sprayCol[i * 3 + 2] = k;
  }
  sprayGeo.attributes.position.needsUpdate = true;
  sprayGeo.attributes.color.needsUpdate = true;
}

// ------------------------------------------------------------
// Animation loop
// ------------------------------------------------------------
const timer = new THREE.Timer();
const camOffset = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  timer.update();
  const dt = Math.min(timer.getDelta(), 0.05);
  const t = timer.getElapsed();

  // --- surf rig: follow the wave field, tilt with the slope ---
  const wx = 1.2 + Math.sin(t * 0.21) * 2.6;
  const wz = Math.sin(t * 0.16 + 1.7) * 2.2;
  const h = waveHeight(wx, wz, t);
  const [sx, sz] = waveSlope(wx, wz, t);

  surf.position.set(wx, h + 0.06 + Math.sin(t * 2.1) * 0.06, wz);
  surf.rotation.x = -THREE.MathUtils.clamp(sz, -0.7, 0.7) * 0.75 + Math.sin(t * 1.2) * 0.05;
  surf.rotation.z = THREE.MathUtils.clamp(sx, -0.7, 0.7) * 0.75 + Math.sin(t * 0.9) * 0.07;
  surf.rotation.y = Math.sin(t * 0.14) * 0.25; // lazy heading sway
  surf.updateMatrixWorld();

  // --- pelican: bob, lean, nod, flap ---
  pelican.group.position.y = 0.12 + Math.sin(t * 2.3) * 0.04;
  pelican.group.rotation.x = Math.sin(t * 1.9) * 0.05;
  pelican.head.rotation.x = Math.sin(t * 1.6) * 0.07 + 0.02;
  pelican.head.rotation.y = Math.sin(t * 0.8) * 0.1;
  const flap = Math.sin(t * 5.2) * 0.4 + 0.06;
  for (const { g: wing, s } of pelican.wings) {
    wing.rotation.x = s * flap;
  }

  // --- spray ---
  updateSpray(dt);

  // --- clouds drift ---
  for (const c of clouds) {
    c.g.position.x += c.speed * dt;
    if (c.g.position.x > 100) c.g.position.x = -100;
  }

  // --- birds circle overhead, flapping ---
  for (const b of birds) {
    const a = t * b.speed + b.phase;
    b.g.position.set(
      Math.cos(a) * b.radius,
      b.height + Math.sin(t * 1.1 + b.phase) * 1.2,
      Math.sin(a) * b.radius * 0.55 - 20
    );
    b.g.rotation.y = -a - Math.PI / 2;
    const flapB = Math.sin(t * 10 + b.phase) * 0.35;
    for (const { m, s } of b.wings) {
      m.rotation.x = s * (Math.PI / 2 - 0.55) + s * flapB;
    }
  }

  // --- camera: slow drifting chase-cam (no user input) ---
  camOffset.set(
    6.6 + Math.sin(t * 0.11) * 1.1,
    3.6 + Math.sin(t * 0.27) * 0.5,
    6.1 + Math.cos(t * 0.17) * 1.0
  );
  camera.position.copy(surf.position).add(camOffset);
  camera.lookAt(surf.position.x, surf.position.y + 1.5, surf.position.z);

  // --- ocean uniforms ---
  oceanMat.uniforms.uTime.value = t;
  oceanMat.uniforms.uCamPos.value.copy(camera.position);

  renderer.render(scene, camera);
}

animate();
