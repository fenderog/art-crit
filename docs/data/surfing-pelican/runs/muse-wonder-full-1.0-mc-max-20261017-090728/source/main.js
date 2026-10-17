// The Surfing Pelican — a non-interactive Three.js loop.
// Everything is procedural: the pelican, surfboard, curling wave, ocean,
// spray, clouds and gulls are all built and animated in code.
// There are deliberately no controls — the camera drifts on its own.

import * as THREE from "three";

const canvas = document.getElementById("scene");
const fallback = document.getElementById("fallback");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const MOTION = reducedMotion ? 0.3 : 1; // gentler motion when requested

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
} catch (err) {
  fallback.hidden = false;
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd6f0f7, 34, 92);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 220);
camera.position.set(8.0, 5.15, camera.aspect < 0.85 ? 19.8 : camera.aspect < 1.25 ? 14.6 : 12.0);

// ---------- helpers ----------

function softDotTexture(size = 64) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(0.45, "rgba(255,255,255,0.85)");
  g.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function boardTexture() {
  const c = document.createElement("canvas");
  c.width = 1024; c.height = 288;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#ff6b4a"; // coral deck
  ctx.fillRect(0, 0, c.width, c.height);
  ctx.fillStyle = "#2a9db4"; // teal rails
  ctx.fillRect(0, 0, c.width, 26);
  ctx.fillRect(0, c.height - 26, c.width, 26);
  ctx.fillStyle = "#fff3d6"; // cream centre stripe
  ctx.fillRect(0, c.height / 2 - 34, c.width, 68);
  ctx.fillStyle = "#ffb703"; // gold pinstripes
  ctx.fillRect(0, c.height / 2 - 52, c.width, 10);
  ctx.fillRect(0, c.height / 2 + 42, c.width, 10);
  // three little wave lines near the nose
  ctx.strokeStyle = "#0b6e8c";
  ctx.lineWidth = 8;
  ctx.lineCap = "round";
  for (const dy of [-22, 0, 22]) {
    ctx.beginPath();
    ctx.moveTo(838, c.height / 2 + dy);
    ctx.bezierCurveTo(862, c.height / 2 + dy - 17, 888, c.height / 2 + dy + 17, 914, c.height / 2 + dy);
    ctx.stroke();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  // ExtrudeGeometry cap UVs are the shape xy coordinates, so map the
  // shape bounding box [-1.78..1.78] x [-0.5..0.5] into 0..1.
  tex.repeat.set(1 / 3.56, 1 / 1.0);
  tex.offset.set(0.5, 0.5);
  return tex;
}

const rand = (a, b) => a + Math.random() * (b - a);
const clamp = THREE.MathUtils.clamp;

// ---------- sky, sun, lights ----------

const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  depthWrite: false,
  fog: false,
  uniforms: {
    top: { value: new THREE.Color(0x3f9fd6) },
    mid: { value: new THREE.Color(0x8fd0ec) },
    horizon: { value: new THREE.Color(0xffeec2) },
  },
  vertexShader: `
    varying vec3 vPos;
    void main() {
      vPos = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 top; uniform vec3 mid; uniform vec3 horizon;
    varying vec3 vPos;
    void main() {
      float h = normalize(vPos).y;
      vec3 col = mix(horizon, mid, smoothstep(-0.02, 0.22, h));
      col = mix(col, top, smoothstep(0.18, 0.65, h));
      col = mix(vec3(0.16, 0.55, 0.68), col, smoothstep(-0.25, 0.0, h));
      gl_FragColor = vec4(col, 1.0);
    }`,
});
scene.add(new THREE.Mesh(new THREE.SphereGeometry(110, 32, 20), skyMat));

const sunPos = new THREE.Vector3(-29, 16, -42);
const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({
  map: softDotTexture(128), color: 0xffe9a8, transparent: true, opacity: 0.95, fog: false, depthWrite: false,
}));
sunGlow.position.copy(sunPos);
sunGlow.scale.setScalar(26);
scene.add(sunGlow);
const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(3.1, 40),
  new THREE.MeshBasicMaterial({ color: 0xfff6d8, fog: false })
);
sunDisc.position.copy(sunPos);
sunDisc.lookAt(0, 4, 14);
scene.add(sunDisc);

scene.add(new THREE.HemisphereLight(0xcdefff, 0x2a7f9e, 1.15));
const sunLight = new THREE.DirectionalLight(0xfff1cf, 2.6);
sunLight.position.set(-14, 20, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -18; sunLight.shadow.camera.right = 18;
sunLight.shadow.camera.top = 16; sunLight.shadow.camera.bottom = -8;
sunLight.shadow.camera.near = 2; sunLight.shadow.camera.far = 60;
sunLight.shadow.bias = -0.0006;
sunLight.shadow.normalBias = 0.03;
scene.add(sunLight);
const bounce = new THREE.DirectionalLight(0x9fe3f2, 0.55);
bounce.position.set(8, 4, 16);
scene.add(bounce);

// ---------- the curling wave ----------
// The wave is a swept surface: one curl profile (in the YZ plane) swept
// along X. The profile runs from the trough, up the face, over the lip
// and back down inside the barrel, so the tube reads from the front.

const profileCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, -0.25, 6.4),
  new THREE.Vector3(0, 0.05, 4.6),
  new THREE.Vector3(0, 0.75, 2.9),
  new THREE.Vector3(0, 1.9, 1.55),
  new THREE.Vector3(0, 3.05, 0.55),
  new THREE.Vector3(0, 4.15, -0.25),
  new THREE.Vector3(0, 5.15, -0.75),
  new THREE.Vector3(0, 6.05, -0.55),
  new THREE.Vector3(0, 6.8, 0.45),
  new THREE.Vector3(0, 7.0, 1.65),
  new THREE.Vector3(0, 6.4, 2.25),
  new THREE.Vector3(0, 5.95, 1.85),
], false, "centripetal");

const PROFILE = profileCurve.getSpacedPoints(220);

function profileAt(t) {
  const f = clamp(t, 0, 1) * (PROFILE.length - 1);
  const i = Math.min(Math.floor(f), PROFILE.length - 2);
  const a = PROFILE[i], b = PROFILE[i + 1], k = f - i;
  return { y: a.y + (b.y - a.y) * k, z: a.z + (b.z - a.z) * k };
}

// The break is centred at x = -2 and peels toward +X: tallest and
// throwing its lip furthest at the break, easing to an open shoulder
// down the line where the pelican rides.
function waveShape(x) {
  const d = (x + 2) / 8;
  const s = Math.exp(-d * d);
  return { s, height: 0.72 + 0.38 * s };
}

function wavePoint(x, t) {
  const p = profileAt(t);
  const { s, height } = waveShape(x);
  const lipThrow = Math.max(0, t - 0.62) / 0.38 * 0.75 * s;
  return { y: p.y * height, z: p.z * (0.93 + 0.07 * s) + lipThrow };
}

// Point, outward normal and face tilt where the board rides.
function faceAt(x, t) {
  const c = wavePoint(x, t);
  const a = wavePoint(x, Math.max(0, t - 0.02));
  const b = wavePoint(x, Math.min(1, t + 0.02));
  let ty = b.y - a.y, tz = b.z - a.z;
  const len = Math.hypot(ty, tz) || 1;
  ty /= len; tz /= len;
  return { y: c.y, z: c.z, ny: -tz, nz: ty, tilt: Math.atan2(ty, -tz) };
}

const WAVE_LEN = 38, LEN_SEG = 104, PRO_SEG = 52;
const waveGeo = new THREE.BufferGeometry();
{
  const cols = LEN_SEG + 1, rows = PRO_SEG + 1;
  const pos = new Float32Array(cols * rows * 3);
  const col = new Float32Array(cols * rows * 3);
  const uv = new Float32Array(cols * rows * 2);
  const stops = [
    [0.0, new THREE.Color(0x0a6a8f)], [0.3, new THREE.Color(0x1193b5)],
    [0.58, new THREE.Color(0x25b3c4)], [0.76, new THREE.Color(0x4fd0cd)],
    [0.845, new THREE.Color(0x93e6da)], [0.89, new THREE.Color(0xf2fefa)],
    [0.945, new THREE.Color(0xa8dee2)], [1.0, new THREE.Color(0x63bccd)],
  ];
  const colorAt = (t) => {
    for (let i = 1; i < stops.length; i++) {
      if (t <= stops[i][0]) {
        const [t0, c0] = stops[i - 1], [t1, c1] = stops[i];
        return c0.clone().lerp(c1, (t - t0) / (t1 - t0));
      }
    }
    return stops[stops.length - 1][1].clone();
  };
  let n = 0, m = 0;
  for (let i = 0; i < cols; i++) {
    const x = -WAVE_LEN / 2 + WAVE_LEN * (i / LEN_SEG);
    for (let j = 0; j < rows; j++) {
      const t = j / PRO_SEG;
      const p = wavePoint(x, t);
      pos[n] = x; pos[n + 1] = p.y; pos[n + 2] = p.z;
      const c = colorAt(t);
      col[n] = c.r; col[n + 1] = c.g; col[n + 2] = c.b;
      n += 3;
      uv[m] = i / LEN_SEG; uv[m + 1] = t; m += 2;
    }
  }
  const idx = [];
  for (let i = 0; i < LEN_SEG; i++) {
    for (let j = 0; j < PRO_SEG; j++) {
      const a = i * rows + j, b = (i + 1) * rows + j;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  waveGeo.setIndex(idx);
  waveGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  waveGeo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  waveGeo.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  waveGeo.computeVertexNormals();
}
const waveBase = waveGeo.attributes.position.array.slice();
const wave = new THREE.Mesh(waveGeo, new THREE.MeshStandardMaterial({
  vertexColors: true, roughness: 0.42, metalness: 0.0, side: THREE.DoubleSide,
}));
wave.receiveShadow = true;
scene.add(wave);

function updateWave(T) {
  const arr = waveGeo.attributes.position.array;
  const rows = PRO_SEG + 1;
  for (let i = 0; i <= LEN_SEG; i++) {
    const x = -WAVE_LEN / 2 + WAVE_LEN * (i / LEN_SEG);
    for (let j = 0; j < rows; j++) {
      const t = j / PRO_SEG;
      const k = (i * rows + j) * 3;
      const amp = (0.25 + t) * (0.4 + 0.6 * MOTION);
      arr[k + 1] = waveBase[k + 1]
        + Math.sin(x * 0.75 + T * 2.6 + t * 5.0) * 0.055 * amp
        + (t > 0.85 ? Math.sin(x * 1.7 + T * 5.2) * 0.05 * amp : 0);
      arr[k + 2] = waveBase[k + 2]
        + Math.sin(x * 0.45 + T * 1.9 + t * 3.0) * 0.045 * amp;
    }
  }
  waveGeo.attributes.position.needsUpdate = true;
  waveGeo.computeVertexNormals();
}

// ---------- ocean floor of the scene ----------

const oceanGeo = new THREE.PlaneGeometry(130, 85, 46, 30);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({
  color: 0x0d7ea6, roughness: 0.38, metalness: 0.0,
}));
ocean.rotation.x = -Math.PI / 2;
ocean.position.set(0, -0.38, 8);
ocean.receiveShadow = true;
scene.add(ocean);

function updateOcean(T) {
  const arr = oceanGeo.attributes.position.array;
  for (let i = 0; i < arr.length; i += 3) {
    const x = oceanBase[i], y = oceanBase[i + 1];
    arr[i + 2] = (Math.sin(x * 0.28 + T * 1.4) + Math.sin(y * 0.42 - T * 1.1)) * 0.09 * (0.4 + 0.6 * MOTION);
  }
  oceanGeo.attributes.position.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// Foam: a churned line along the crest and lip (one instanced mesh).
{
  const count = 240;
  const foam = new THREE.InstancedMesh(
    new THREE.SphereGeometry(1, 10, 8),
    new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95 }),
    count
  );
  const dummy = new THREE.Object3D();
  for (let i = 0; i < count; i++) {
    // Foam concentrates near the break at x = -2, thinning down the line.
    const x = Math.random() < 0.75 ? rand(-12, 4.5) : rand(-14.5, 7);
    // t is arc length along the profile: the crest/lip tip sits near
    // t = 0.88, so foam hugs 0.82-0.905, clear of the lip underside.
    const t = rand(0.82, 0.905);
    const p = wavePoint(x, t);
    dummy.position.set(x + rand(-0.14, 0.14), p.y + rand(-0.1, 0.06), p.z + rand(-0.14, 0.14));
    dummy.rotation.set(rand(0, 3), rand(0, 3), rand(0, 3));
    dummy.scale.set(rand(0.16, 0.42), rand(0.08, 0.2), rand(0.16, 0.38));
    dummy.updateMatrix();
    foam.setMatrixAt(i, dummy.matrix);
  }
  foam.instanceMatrix.needsUpdate = true;
  scene.add(foam);
}

// Speed streaks flowing down the face sell the endless forward rush.
const streaks = [];
{
  const geo = new THREE.PlaneGeometry(1, 1);
  for (let i = 0; i < 26; i++) {
    const mat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: rand(0.1, 0.3), depthWrite: false, side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);
    streaks.push({
      mesh, x: rand(-18, 18), t: rand(0.24, 0.66),
      speed: rand(5.5, 9.5), len: rand(1.3, 3.4), wid: rand(0.05, 0.14),
    });
  }
}

function updateStreaks(dt) {
  for (const s of streaks) {
    s.x -= s.speed * dt * (0.35 + 0.65 * MOTION);
    if (s.x < -19) { s.x = 19; s.t = rand(0.24, 0.66); }
    const f = faceAt(s.x, s.t);
    s.mesh.position.set(s.x, f.y + f.ny * 0.07, f.z + f.nz * 0.07);
    s.mesh.rotation.set(-Math.PI / 2 + f.tilt, 0, 0);
    s.mesh.scale.set(s.len, s.wid, 1);
  }
}

// ---------- drifting clouds and gulls ----------

const clouds = [];
{
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  const puff = new THREE.SphereGeometry(1, 12, 10);
  for (let i = 0; i < 6; i++) {
    const cloud = new THREE.Group();
    const blobs = 4 + Math.floor(Math.random() * 3);
    for (let b = 0; b < blobs; b++) {
      const m = new THREE.Mesh(puff, mat);
      m.position.set(b * rand(0.9, 1.3) - blobs * 0.55, rand(-0.2, 0.35), rand(-0.4, 0.4));
      m.scale.set(rand(1.0, 1.9), rand(0.5, 0.75), rand(0.8, 1.2));
      cloud.add(m);
    }
    cloud.position.set(rand(-42, 42), rand(11, 18), rand(-38, -24));
    cloud.scale.setScalar(rand(1.1, 2.0));
    cloud.userData.speed = rand(0.25, 0.6);
    scene.add(cloud);
    clouds.push(cloud);
  }
}

const gulls = [];
{
  const white = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.8, side: THREE.DoubleSide });
  const tip = new THREE.MeshStandardMaterial({ color: 0x3a4248, roughness: 0.8, side: THREE.DoubleSide });
  for (let i = 0; i < 4; i++) {
    const gull = new THREE.Group();
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.5, 4, 8), white);
    body.rotation.x = Math.PI / 2;
    gull.add(body);
    const wings = [];
    for (const side of [-1, 1]) {
      const pivot = new THREE.Group();
      const w = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.035, 0.3), white);
      w.position.x = side * 0.55;
      const t = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.035, 0.24), tip);
      t.position.x = side * 1.2;
      pivot.add(w, t);
      gull.add(pivot);
      wings.push({ pivot, side });
    }
    gull.userData = {
      wings, radius: rand(16, 30), height: rand(11, 17),
      speed: rand(0.05, 0.1) * (Math.random() < 0.5 ? 1 : -1),
      phase: rand(0, 6.28), flap: rand(5, 7.5),
    };
    scene.add(gull);
    gulls.push(gull);
  }
}

function updateSkyLife(T, dt) {
  for (const c of clouds) {
    c.position.x += c.userData.speed * dt * (0.3 + 0.7 * MOTION);
    if (c.position.x > 52) c.position.x = -52;
  }
  for (const g of gulls) {
    const u = g.userData;
    const a = u.phase + T * u.speed * (0.3 + 0.7 * MOTION);
    const x = Math.cos(a) * u.radius, z = -26 + Math.sin(a) * u.radius * 0.35;
    g.position.set(x, u.height + Math.sin(T * 0.7 + u.phase) * 0.6, z);
    g.rotation.y = -a + (u.speed > 0 ? 0 : Math.PI);
    const flap = Math.sin(T * u.flap * (0.4 + 0.6 * MOTION) + u.phase) * 0.55;
    for (const w of u.wings) w.pivot.rotation.z = w.side * flap * 0.7 + flap * 0.3 * w.side;
  }
}

// ---------- surfboard ----------

function makeSurfboard() {
  const shape = new THREE.Shape();
  shape.moveTo(-1.68, 0);
  shape.bezierCurveTo(-1.68, 0.42, -0.95, 0.5, -0.1, 0.49);
  shape.bezierCurveTo(0.85, 0.48, 1.45, 0.3, 1.78, 0);
  shape.bezierCurveTo(1.45, -0.3, 0.85, -0.48, -0.1, -0.49);
  shape.bezierCurveTo(-0.95, -0.5, -1.68, -0.42, -1.68, 0);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.13, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.045, bevelSegments: 2, steps: 1,
  });
  geo.translate(0, 0, -0.065);
  geo.rotateX(-Math.PI / 2); // lie flat: length X, width Z, thickness Y
  const board = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    map: boardTexture(), roughness: 0.35, metalness: 0.0,
  }));
  board.castShadow = true;
  board.receiveShadow = true;
  const fin = new THREE.Mesh(
    new THREE.BoxGeometry(0.36, 0.27, 0.05),
    new THREE.MeshStandardMaterial({ color: 0x0b6e8c, roughness: 0.5 })
  );
  fin.position.set(-1.28, -0.17, 0);
  fin.rotation.z = 0.35;
  const group = new THREE.Group();
  group.add(board, fin);
  return group;
}

// ---------- the pelican ----------
// Local axes: +Z is where the beak points (toward the viewer/shore),
// +X is the direction of travel along the wave, +Y is up.
// The rider group sits on the wave face; the board takes the full face
// tilt while the stance counter-tilts so the bird stays fairly upright.

const MAT = {
  feather: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.65, side: THREE.DoubleSide }),
  cream: new THREE.MeshStandardMaterial({ color: 0xf7ecd4, roughness: 0.7, side: THREE.DoubleSide }),
  mantle: new THREE.MeshStandardMaterial({ color: 0xe6edf1, roughness: 0.75 }),
  flight: new THREE.MeshStandardMaterial({ color: 0x232a30, roughness: 0.7, side: THREE.DoubleSide }),
  crest: new THREE.MeshStandardMaterial({ color: 0xffe1a1, roughness: 0.8 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xf59a23, roughness: 0.45 }),
  beakTip: new THREE.MeshStandardMaterial({ color: 0xe4572e, roughness: 0.45 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xffa94d, roughness: 0.5 }),
  skin: new THREE.MeshStandardMaterial({ color: 0x9fd4e8, roughness: 0.6 }),
  leg: new THREE.MeshStandardMaterial({ color: 0xe8890c, roughness: 0.6 }),
  eye: new THREE.MeshStandardMaterial({ color: 0x14181c, roughness: 0.25 }),
  glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
};

function wingSegmentGeo(len, rootChord, tipChord, sign) {
  const s = new THREE.Shape();
  const x = (v) => v * sign;
  s.moveTo(x(0), -rootChord * 0.42);
  s.quadraticCurveTo(x(len * 0.55), -rootChord * 0.5, x(len), -tipChord * 0.28);
  s.quadraticCurveTo(x(len * 1.04), 0, x(len), tipChord * 0.4);
  s.quadraticCurveTo(x(len * 0.5), rootChord * 0.62, x(0), rootChord * 0.58);
  s.quadraticCurveTo(x(-len * 0.04), 0, x(0), -rootChord * 0.42);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.06, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.03, bevelSegments: 1, steps: 1,
  });
  geo.translate(0, 0, -0.03);
  geo.rotateX(-Math.PI / 2);
  return geo;
}

function makeWing(sign) {
  const shoulder = new THREE.Group();
  const inner = new THREE.Mesh(wingSegmentGeo(1.12, 0.92, 0.66, sign), MAT.feather);
  shoulder.add(inner);
  const elbow = new THREE.Group();
  elbow.position.set(sign * 1.08, 0.01, 0.02);
  const outer = new THREE.Mesh(wingSegmentGeo(0.98, 0.64, 0.32, sign), MAT.feather);
  elbow.add(outer);
  // black primary feathers splayed at the tip
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.035, 0.11), MAT.flight);
    f.position.set(sign * 1.08, -0.01, -0.16 + i * 0.11);
    f.rotation.y = sign * (-0.22 + i * 0.13);
    elbow.add(f);
  }
  // black tip patch over the outer wing's end
  const patch = new THREE.Mesh(wingSegmentGeo(0.5, 0.34, 0.28, sign), MAT.flight);
  patch.position.set(sign * 0.52, 0.015, 0.01);
  elbow.add(patch);
  shoulder.add(elbow);
  return { shoulder, elbow, sign };
}

function makeHead() {
  const head = new THREE.Group();
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.4, 24, 18), MAT.feather);
  skull.scale.set(0.88, 0.82, 1.02);
  head.add(skull);
  // shaggy crest swept back
  for (let i = 0; i < 4; i++) {
    const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.065, 0.44, 7), MAT.crest);
    tuft.position.set(-0.11 + i * 0.075, 0.3, -0.2 - Math.abs(i - 1.5) * 0.02);
    tuft.rotation.x = -1.15;
    tuft.rotation.z = -0.25 + i * 0.16;
    head.add(tuft);
  }
  // bare skin patch + eyes
  for (const side of [-1, 1]) {
    const patch = new THREE.Mesh(new THREE.SphereGeometry(0.135, 12, 10), MAT.skin);
    patch.position.set(side * 0.26, 0.07, 0.2);
    patch.scale.set(0.55, 0.85, 0.9);
    head.add(patch);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.062, 12, 10), MAT.eye);
    eye.position.set(side * 0.3, 0.09, 0.27);
    head.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 6), MAT.glint);
    glint.position.set(side * 0.32, 0.13, 0.32);
    head.add(glint);
  }
  // the great bill: flattened upper mandible with a hooked nail
  const upper = new THREE.Mesh(new THREE.ConeGeometry(0.17, 1.48, 14), MAT.beak);
  upper.rotation.x = Math.PI / 2;
  upper.scale.set(1.05, 1, 0.55);
  upper.position.set(0, -0.03, 1.0);
  head.add(upper);
  const nail = new THREE.Mesh(new THREE.ConeGeometry(0.068, 0.24, 10), MAT.beakTip);
  nail.rotation.x = Math.PI;
  nail.position.set(0, -0.1, 1.7);
  head.add(nail);
  const lower = new THREE.Mesh(new THREE.ConeGeometry(0.1, 1.34, 12), MAT.beak);
  lower.rotation.x = Math.PI / 2;
  lower.scale.set(1.1, 1, 0.42);
  lower.position.set(0, -0.13, 0.94);
  head.add(lower);
  // throat pouch, plump and wobbly
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 16), MAT.pouch);
  pouch.scale.set(0.52, 0.62, 1.28);
  pouch.position.set(0, -0.36, 0.95);
  head.add(pouch);
  const chin = new THREE.Mesh(new THREE.SphereGeometry(0.21, 14, 12), MAT.pouch);
  chin.position.set(0, -0.3, 0.28);
  head.add(chin);
  return { head, pouch };
}

function makePelican() {
  const rider = new THREE.Group();
  const boardGroup = makeSurfboard();
  boardGroup.position.y = 0.02;
  rider.add(boardGroup);

  const stance = new THREE.Group();
  rider.add(stance);

  // legs and webbed feet planted along the board
  for (const footX of [-0.55, 0.5]) {
    const thigh = new THREE.Mesh(new THREE.CapsuleGeometry(0.165, 0.3, 4, 10), MAT.feather);
    thigh.position.set(footX * 0.7, 0.74, 0.03);
    thigh.rotation.z = footX > 0 ? -0.38 : 0.38;
    stance.add(thigh);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.065, 0.52, 10), MAT.leg);
    shin.position.set(footX, 0.36, 0.04);
    shin.rotation.z = footX > 0 ? 0.14 : -0.14;
    stance.add(shin);
    const foot = new THREE.Group();
    foot.position.set(footX, 0.1, 0.08);
    const web = new THREE.Mesh(new THREE.SphereGeometry(0.24, 14, 10), MAT.leg);
    web.scale.set(0.88, 0.22, 1.45);
    foot.add(web);
    for (let i = 0; i < 3; i++) {
      const toe = new THREE.Mesh(new THREE.SphereGeometry(0.085, 10, 8), MAT.leg);
      toe.position.set(-0.11 + i * 0.11, 0, 0.3);
      toe.scale.set(0.7, 0.25, 1.35);
      toe.rotation.y = -0.3 + i * 0.3;
      foot.add(toe);
    }
    stance.add(foot);
  }

  const body = new THREE.Group();
  stance.add(body);

  const torso = new THREE.Mesh(new THREE.SphereGeometry(0.85, 28, 22), MAT.feather);
  torso.scale.set(0.86, 0.8, 1.18);
  torso.position.set(0, 1.3, -0.02);
  torso.rotation.x = -0.1;
  body.add(torso);
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.72, 24, 18), MAT.cream);
  belly.scale.set(0.78, 0.72, 0.95);
  belly.position.set(0, 1.12, 0.3);
  body.add(belly);
  const mantle = new THREE.Mesh(new THREE.SphereGeometry(0.8, 24, 18), MAT.mantle);
  mantle.scale.set(0.8, 0.55, 1.02);
  mantle.position.set(0, 1.62, -0.2);
  body.add(mantle);

  // S-curved neck carrying the head
  const neck = new THREE.Group();
  neck.position.set(0, 1.46, 0.44);
  body.add(neck);
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, -0.18, 0.14),
    new THREE.Vector3(0, 0.26, -0.1),
    new THREE.Vector3(0, 0.6, -0.05),
    new THREE.Vector3(0, 0.86, 0.16),
  ]);
  const neckMesh = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 20, 0.235, 12), MAT.feather);
  neck.add(neckMesh);
  const neckBase = new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 12), MAT.feather);
  neckBase.position.set(0, -0.14, 0.1);
  neck.add(neckBase);

  const { head, pouch } = makeHead();
  head.position.set(0, 0.94, 0.22);
  neck.add(head);

  // wings held out for balance
  const wings = [];
  for (const sign of [-1, 1]) {
    const w = makeWing(sign);
    w.shoulder.position.set(sign * 0.62, 1.58, -0.02);
    body.add(w.shoulder);
    wings.push(w);
  }

  // short wedge tail, fanned
  const tail = new THREE.Group();
  tail.position.set(0, 1.36, -0.92);
  body.add(tail);
  for (let i = 0; i < 5; i++) {
    const pivot = new THREE.Group();
    pivot.rotation.y = -0.34 + i * 0.17;
    pivot.rotation.x = 0.3;
    const feather = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.045, 0.64), MAT.feather);
    feather.position.z = -0.3;
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.048, 0.18), MAT.flight);
    tip.position.z = -0.62;
    pivot.add(feather, tip);
    tail.add(pivot);
  }

  rider.traverse((o) => { if (o.isMesh) { o.castShadow = true; } });
  return { rider, boardGroup, stance, body, neck, head, pouch, wings, tail };
}

const PEL = makePelican();
PEL.rider.scale.setScalar(0.94);
scene.add(PEL.rider);
const pouchBase = PEL.pouch.scale.clone();

// ---------- spray and sparkle particles ----------

const dotTex = softDotTexture(64);

function makeParticles(count, size, opacity) {
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) positions[i * 3 + 1] = -60;
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const points = new THREE.Points(geo, new THREE.PointsMaterial({
    size, map: dotTex, transparent: true, opacity, color: 0xffffff,
    depthWrite: false, sizeAttenuation: true,
  }));
  points.frustumCulled = false;
  scene.add(points);
  return {
    points, positions, count,
    vel: new Float32Array(count * 3),
    life: new Float32Array(count),
    cursor: 0,
  };
}

function spawn(sys, px, py, pz, vx, vy, vz, life) {
  const i = sys.cursor;
  sys.cursor = (sys.cursor + 1) % sys.count;
  sys.positions[i * 3] = px; sys.positions[i * 3 + 1] = py; sys.positions[i * 3 + 2] = pz;
  sys.vel[i * 3] = vx; sys.vel[i * 3 + 1] = vy; sys.vel[i * 3 + 2] = vz;
  sys.life[i] = life;
}

function updateParticles(sys, dt, gravity) {
  for (let i = 0; i < sys.count; i++) {
    if (sys.life[i] <= 0) continue;
    sys.life[i] -= dt;
    if (sys.life[i] <= 0) { sys.positions[i * 3 + 1] = -60; continue; }
    sys.vel[i * 3 + 1] -= gravity * dt;
    sys.positions[i * 3] += sys.vel[i * 3] * dt;
    sys.positions[i * 3 + 1] += sys.vel[i * 3 + 1] * dt;
    sys.positions[i * 3 + 2] += sys.vel[i * 3 + 2] * dt;
  }
  sys.points.geometry.attributes.position.needsUpdate = true;
}

const boardSpray = makeParticles(380, 0.16, 0.9);
const lipMist = makeParticles(170, 0.6, 0.32);
let sprayAcc = 0, mistAcc = 0;
const tailWorld = new THREE.Vector3();

function emitParticles(dt, riderX, intensity) {
  PEL.boardGroup.updateWorldMatrix(true, false);
  sprayAcc += dt * (36 + intensity * 150) * (0.35 + 0.65 * MOTION);
  while (sprayAcc >= 1) {
    sprayAcc -= 1;
    const atTail = Math.random() < 0.72;
    tailWorld.set(atTail ? rand(-1.7, -1.1) : rand(-0.6, 0.4), 0.08, atTail ? rand(-0.2, 0.2) : -0.42);
    PEL.boardGroup.localToWorld(tailWorld);
    spawn(boardSpray, tailWorld.x, tailWorld.y, tailWorld.z,
      -rand(2.2, 4.6) - intensity * 2.6, rand(1.4, 3.9) + intensity * 0.9, rand(0.4, 2.0),
      rand(0.5, 1.05));
  }
  mistAcc += dt * 26 * (0.35 + 0.65 * MOTION);
  while (mistAcc >= 1) {
    mistAcc -= 1;
    const x = -2 + rand(-4.5, 4.5); // mist rises off the breaking section
    const p = wavePoint(clamp(x, -13, 13), rand(0.86, 0.92));
    spawn(lipMist, x, p.y + rand(-0.2, 0.3), p.z + rand(-0.2, 0.4),
      rand(-0.6, 0.3), rand(-0.7, 0.1), rand(0.7, 1.7), rand(1.1, 2.0));
  }
}

let sparkleMat;
{
  const count = 170;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = rand(-26, 26);
    positions[i * 3 + 1] = -0.1;
    positions[i * 3 + 2] = rand(5, 24);
  }
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  sparkleMat = new THREE.PointsMaterial({
    size: 0.24, map: dotTex, transparent: true, opacity: 0.5, color: 0xd9f7ff,
    depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const sparkles = new THREE.Points(geo, sparkleMat);
  sparkles.frustumCulled = false;
  scene.add(sparkles);
}

// ---------- the endless ride ----------
// The pelican surfs a standing wave: it stays centre stage, carving from
// a low bottom turn to a high cutback and back, forever. Water streaks,
// spray and lip mist rushing past sell the speed.

function updateRider(T) {
  const amp = 0.35 + 0.65 * MOTION;
  const phase = T * 0.55;
  const carve = Math.sin(phase);       // -1 low on the face, +1 high
  const carveVel = Math.cos(phase);    // + climbing, - dropping back down
  const rideT = 0.455 + 0.055 * carve * amp + 0.01 * Math.sin(T * 1.7) * MOTION;
  // The pelican rides the open shoulder ahead of the break (x ~ +3.6),
  // with the curling section peeling behind it.
  const x = 3.6 + 1.15 * Math.sin(phase - 0.65) * amp + 0.25 * Math.sin(T * 1.13) * MOTION;
  const f = faceAt(x, rideT);

  PEL.rider.position.set(x, f.y + f.ny * 0.12, f.z + f.nz * 0.12);
  const yaw = 0.38 * carveVel * amp + 0.05 * Math.sin(T * 0.9) * MOTION;
  PEL.rider.rotation.y = yaw;

  PEL.boardGroup.rotation.x = f.tilt + 0.055 * Math.sin(T * 1.7) * MOTION;
  PEL.boardGroup.rotation.z = (0.09 * Math.sin(T * 1.31 + 0.4) + 0.07 * carveVel) * MOTION;
  PEL.boardGroup.position.y = 0.02 + 0.03 * Math.sin(T * 2.3) * MOTION;

  PEL.stance.rotation.x = f.tilt * 0.4 + 0.06 * carveVel * amp;
  PEL.stance.rotation.z = -0.1 * carve * amp + 0.03 * Math.sin(T * 1.6) * MOTION;

  PEL.body.position.y = 0.05 * Math.sin(T * 2.3) * MOTION - 0.07 * carve * carve * amp;
  PEL.body.rotation.x = (0.07 * Math.sin(T * 1.9) + 0.09 * carveVel) * MOTION;
  PEL.body.rotation.y = -yaw * 0.35 + 0.07 * Math.sin(T * 0.8) * MOTION;
  PEL.body.rotation.z = 0.06 * Math.sin(T * 1.6 + 1) * MOTION;

  PEL.neck.rotation.x = 0.1 * Math.sin(T * 2.3 + 0.6) * MOTION - 0.04;
  PEL.neck.rotation.y = 0.16 * Math.sin(phase - 0.4) * amp;
  PEL.head.rotation.y = (0.3 * Math.sin(phase - 0.25) + 0.07 * Math.sin(T * 0.83)) * amp;
  PEL.head.rotation.x = (0.08 * Math.sin(T * 2.3 + 1.1) + 0.05 * carve) * MOTION;
  PEL.head.rotation.z = 0.06 * Math.sin(T * 1.4) * MOTION;

  // pouch wobble, lagging behind the head like jelly
  const w = (Math.sin(T * 3.0 - 0.9) * 0.07 + Math.sin(T * 5.3) * 0.02) * MOTION;
  PEL.pouch.scale.set(
    pouchBase.x * (1 + w),
    pouchBase.y * (1 - w * 0.8 + 0.05 * Math.sin(T * 2.3 - 1.2) * MOTION),
    pouchBase.z * (1 + w * 0.4)
  );
  PEL.pouch.rotation.x = 0.08 * Math.sin(T * 2.8 - 0.7) * MOTION;

  // wings: slow balancing, plus a quick flurry near each top turn
  const flurryEnv = Math.pow(Math.max(0, Math.sin(phase + 0.9)), 6);
  const flap = (Math.sin(T * 2.3) * 0.1 + carveVel * 0.16) * MOTION;
  const flapFast = flurryEnv * Math.sin(T * 11) * 0.36 * MOTION;
  for (const wing of PEL.wings) {
    const s = wing.sign;
    wing.shoulder.rotation.z = s * (0.16 + flap + flapFast) + carveVel * 0.1 * MOTION;
    wing.shoulder.rotation.y = s * (0.22 + 0.09 * Math.sin(T * 1.7 + s) * MOTION + flurryEnv * 0.14);
    wing.shoulder.rotation.x = -0.18 + 0.05 * Math.sin(T * 2.0 + s) * MOTION;
    wing.elbow.rotation.z = s * (-0.08 + Math.sin(T * 2.3 - 0.55) * 0.12 * MOTION + flapFast * 0.9);
    wing.elbow.rotation.y = s * (0.12 + 0.08 * Math.sin(T * 1.9 - 0.4) * MOTION);
  }

  PEL.tail.rotation.x = 0.16 * Math.sin(T * 2.6 + 0.3) * MOTION;
  PEL.tail.rotation.y = 0.13 * Math.sin(T * 1.8) * MOTION;

  return { x, intensity: 0.45 + Math.abs(carveVel) * 0.8 + flurryEnv * 0.7 };
}

// ---------- camera: a slow, hands-free drift ----------

const lookTarget = new THREE.Vector3(camera.aspect < 0.85 ? 3.1 : camera.aspect < 1.25 ? 1.9 : 0.9, 3.55, 0.1);
const desiredCam = new THREE.Vector3();
const desiredLook = new THREE.Vector3();

function updateCamera(T, dt, riderX) {
  const aspect = camera.aspect;
  const narrow = aspect < 0.85;
  const dist = narrow ? 1.65 : aspect < 1.25 ? 1.22 : 1.0;
  const lookBaseX = narrow ? 3.1 : aspect < 1.25 ? 1.9 : 0.9;
  const follow = narrow ? 0.8 : 0.45;
  const sway = (narrow ? 0.4 : 1.0) * MOTION;
  desiredCam.set(
    8.0 + (riderX - 3.6) * 0.3 + Math.sin(T * 0.12) * 1.5 * sway,
    5.15 + Math.sin(T * 0.19) * 0.5 * MOTION,
    12.0 * dist + Math.sin(T * 0.09) * 0.8 * sway
  );
  desiredLook.set(lookBaseX + (riderX - 3.6) * follow, 3.55 + Math.sin(T * 0.23) * 0.2 * MOTION, 0.1);
  const k = 1 - Math.exp(-dt * 2.2);
  camera.position.lerp(desiredCam, k);
  lookTarget.lerp(desiredLook, k);
  camera.lookAt(lookTarget);
}

// ---------- main loop ----------

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});

const timer = new THREE.Timer();
timer.connect(document); // avoids a time jump after a hidden tab

function animate() {
  requestAnimationFrame(animate);
  timer.update();
  const rawDt = timer.getDelta();
  const dt = Math.min(rawDt, 0.05);
  const T = timer.getElapsed();

  const { x, intensity } = updateRider(T);
  updateWave(T);
  updateOcean(T);
  updateStreaks(dt);
  emitParticles(dt, x, intensity);
  updateParticles(boardSpray, dt, 6.5);
  updateParticles(lipMist, dt, 0.35);
  sparkleMat.opacity = 0.35 + 0.25 * (0.5 + 0.5 * Math.sin(T * 2.7));
  updateSkyLife(T, dt);
  updateCamera(T, Math.min(rawDt, 0.5), x); // camera may catch up faster than physics after sparse frames
  renderer.render(scene, camera);
}
animate();
