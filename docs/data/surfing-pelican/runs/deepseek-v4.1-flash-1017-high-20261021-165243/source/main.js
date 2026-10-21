import * as THREE from "three";
import { createOcean, waveHeight, waveNormal } from "./ocean.js";
import { createSurfer } from "./pelican.js";

const canvas = document.querySelector("#scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2("#e6c6a6", 0.0035);

const camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.1, 1600);
camera.position.set(6.2, 3.8, 8.4);

// ---------------------------------------------------------------- sky
const sunDirection = new THREE.Vector3(-0.42, 0.2, -0.88).normalize();

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(720, 48, 32),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      uSunDir: { value: sunDirection },
      uTop: { value: new THREE.Color("#2c7ea7") },
      uMid: { value: new THREE.Color("#8ac7d9") },
      uHorizon: { value: new THREE.Color("#ffd3a2") },
      uSun: { value: new THREE.Color("#fff2c9") },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vDir = normalize(wp.xyz - cameraPosition);
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir;
      uniform vec3 uTop;
      uniform vec3 uMid;
      uniform vec3 uHorizon;
      uniform vec3 uSun;
      varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir);
        float h = clamp(d.y, 0.0, 1.0);
        vec3 col = mix(uHorizon, uMid, smoothstep(0.0, 0.26, h));
        col = mix(col, uTop, smoothstep(0.18, 0.72, h));

        float s = max(dot(d, uSunDir), 0.0);
        col += uSun * pow(s, 320.0) * 1.2;
        col += uSun * pow(s, 16.0) * 0.18;
        col += vec3(1.0, 0.62, 0.32) * pow(1.0 - abs(d.y), 22.0) * 0.10 * smoothstep(-0.2, 0.8, dot(d, uSunDir));

        // faint horizontal haze bands
        float haze = sin(d.y * 46.0 + 0.8) * 0.5 + 0.5;
        col = mix(col, uHorizon, smoothstep(0.02, 0.0, d.y) * 0.35 * haze);
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  })
);
sky.renderOrder = -10;
scene.add(sky);

// ---------------------------------------------------------------- light
const hemi = new THREE.HemisphereLight("#c8ecf5", "#0b3b47", 1.02);
scene.add(hemi);

const sun = new THREE.DirectionalLight("#ffe3b0", 2.8);
sun.position.copy(sunDirection).multiplyScalar(60);
sun.position.y += 14;
scene.add(sun);

const rim = new THREE.DirectionalLight("#9ed4ff", 1.0);
rim.position.set(14, 10, 22);
scene.add(rim);

const fill = new THREE.DirectionalLight("#ffb98c", 0.55);
fill.position.set(-18, 4, 14);
scene.add(fill);

// ---------------------------------------------------------------- ocean
const ocean = createOcean();
scene.add(ocean.mesh);

// ---------------------------------------------------------------- clouds
function makeCloudTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 256;
  const ctx = c.getContext("2d");
  let seed = 13;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return seed / 2147483647;
  };
  for (let i = 0; i < 34; i++) {
    const x = 70 + rand() * 372;
    const y = 95 + rand() * 70;
    const rx = 32 + rand() * 70;
    const ry = 14 + rand() * 30;
    const g = ctx.createRadialGradient(x, y, 0, x, y, rx);
    const alpha = 0.06 + rand() * 0.09;
    g.addColorStop(0, `rgba(255, 244, 226, ${alpha})`);
    g.addColorStop(0.55, `rgba(255, 236, 214, ${alpha * 0.6})`);
    g.addColorStop(1, "rgba(255, 236, 214, 0)");
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(1, ry / rx);
    ctx.translate(-x, -y);
    ctx.fillStyle = g;
    ctx.fillRect(x - rx, y - rx, rx * 2, rx * 2);
    ctx.restore();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const cloudTexture = makeCloudTexture();
const cloudData = [
  [-140, 44, -260, 210, 66, 0.72],
  [-40, 58, -300, 260, 76, 0.5],
  [120, 38, -280, 190, 52, 0.62],
  [235, 64, -230, 180, 60, 0.34],
  [-250, 72, -160, 200, 62, 0.4],
  [200, 92, -120, 150, 44, 0.26],
];
for (const [x, y, z, w, h, o] of cloudData) {
  const mat = new THREE.SpriteMaterial({
    map: cloudTexture,
    color: "#ffe9cd",
    transparent: true,
    opacity: o,
    depthWrite: false,
    fog: false,
  });
  const sprite = new THREE.Sprite(mat);
  sprite.position.set(x, y, z);
  sprite.scale.set(w, h, 1);
  scene.add(sprite);
}

// ---------------------------------------------------------------- surfer
const surfer = createSurfer();
scene.add(surfer.group);

// foam collar where the board meets the water
const collarGeo = new THREE.RingGeometry(0.74, 1.16, 56);
collarGeo.rotateX(-Math.PI / 2);
const collar = new THREE.Mesh(
  collarGeo,
  new THREE.MeshBasicMaterial({
    color: "#fff6e3",
    transparent: true,
    opacity: 0.38,
    depthWrite: false,
    side: THREE.DoubleSide,
  })
);
collar.scale.set(2.35, 1, 0.8);
scene.add(collar);

// ---------------------------------------------------------------- spray
function makeSoftDisc() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(0.35, "rgba(255,250,235,0.85)");
  g.addColorStop(1, "rgba(255,250,235,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const sprayCount = 320;
const sprayPositions = new Float32Array(sprayCount * 3);
const sprayData = Array.from({ length: sprayCount }, () => ({
  life: 0,
  max: 1,
  vel: new THREE.Vector3(),
}));

for (let i = 0; i < sprayCount; i++) sprayPositions[i * 3 + 1] = -100;

const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
const sprayMat = new THREE.PointsMaterial({
  map: makeSoftDisc(),
  color: "#fff7e9",
  size: 0.16,
  transparent: true,
  opacity: 0.95,
  depthWrite: false,
  blending: THREE.NormalBlending,
  sizeAttenuation: true,
});
const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

const worldTail = new THREE.Vector3();
const worldNose = new THREE.Vector3();
const tailLocal = new THREE.Vector3(-1.95, 0.1, 0);
const noseLocal = new THREE.Vector3(2.35, 0.1, 0);

let spawnAccumulator = 0;

function spawnParticle(tailOrNose, spread, upSpeed) {
  const idx = sprayData.findIndex((p) => p.life <= 0);
  if (idx === -1) return;
  const p = sprayData[idx];
  p.max = 0.55 + Math.random() * 0.65;
  p.life = p.max;
  const src = tailOrNose === "nose" ? worldNose : worldTail;
  sprayPositions[idx * 3] = src.x + (Math.random() - 0.5) * 0.5;
  sprayPositions[idx * 3 + 1] = src.y + Math.random() * 0.18;
  sprayPositions[idx * 3 + 2] = src.z + (Math.random() - 0.5) * spread;
  p.vel.set(
    -1.6 - Math.random() * 3.2,
    upSpeed + Math.random() * 1.8,
    (Math.random() - 0.5) * 2.0
  );
}

function updateSpray(dt) {
  for (let i = 0; i < sprayCount; i++) {
    const p = sprayData[i];
    if (p.life > 0) {
      p.life -= dt;
      p.vel.y -= 7.0 * dt;
      sprayPositions[i * 3] += p.vel.x * dt;
      sprayPositions[i * 3 + 1] += p.vel.y * dt;
      sprayPositions[i * 3 + 2] += p.vel.z * dt;
      if (p.life <= 0) {
        sprayPositions[i * 3 + 1] = -50;
      }
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- wake
function makeWakeTexture() {
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 128;
  const ctx = c.getContext("2d");
  const img = ctx.createImageData(256, 128);
  let seed = 7;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return seed / 2147483647;
  };
  for (let y = 0; y < 128; y++) {
    for (let x = 0; x < 256; x++) {
      const u = x / 255;
      const v = y / 127;
      const edge = Math.pow(Math.sin(Math.PI * v), 1.0);
      const fade = Math.pow(1 - u, 1.25);
      const grain = 0.55 + 0.45 * Math.sin(x * 0.55 + y * 1.7) * Math.sin(y * 0.19 - x * 0.12);
      const ridge = 0.45 + 0.55 * Math.pow(Math.abs(2 * v - 1), 0.7);
      let a = edge * fade * grain * ridge * 240;
      if (u < 0.06) a *= 0.4 + u / 0.1;
      const i = (y * 256 + x) * 4;
      img.data[i] = 255;
      img.data[i + 1] = 249;
      img.data[i + 2] = 234;
      img.data[i + 3] = Math.max(0, Math.min(255, a));
    }
  }
  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const wakeCols = 26;
const wakeRows = 5;
const wakeGeo = new THREE.BufferGeometry();
const wakePos = new Float32Array(wakeCols * wakeRows * 3);
const wakeUv = new Float32Array(wakeCols * wakeRows * 2);
const wakeIdx = [];
for (let i = 0; i < wakeCols; i++) {
  for (let j = 0; j < wakeRows; j++) {
    const k = i * wakeRows + j;
    wakeUv[k * 2] = i / (wakeCols - 1);
    wakeUv[k * 2 + 1] = j / (wakeRows - 1);
  }
}
for (let i = 0; i < wakeCols - 1; i++) {
  for (let j = 0; j < wakeRows - 1; j++) {
    const a = i * wakeRows + j;
    const b = (i + 1) * wakeRows + j;
    wakeIdx.push(a, b, a + 1, b, b + 1, a + 1);
  }
}
wakeGeo.setIndex(wakeIdx);
wakeGeo.setAttribute("position", new THREE.BufferAttribute(wakePos, 3));
wakeGeo.setAttribute("uv", new THREE.BufferAttribute(wakeUv, 2));
const wake = new THREE.Mesh(
  wakeGeo,
  new THREE.MeshBasicMaterial({
    map: makeWakeTexture(),
    color: "#fff5e2",
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    side: THREE.DoubleSide,
  })
);
wake.frustumCulled = false;
wake.renderOrder = 2;
scene.add(wake);

function updateWake(t, bx, bz) {
  const length = 8.5;
  for (let i = 0; i < wakeCols; i++) {
    const u = i / (wakeCols - 1);
    const d = u * length;
    const x = bx - 1.98 - d;
    const half = 0.62 + d * 0.24;
    for (let j = 0; j < wakeRows; j++) {
      const v = j / (wakeRows - 1);
      const z = bz + (v - 0.5) * 2 * half + Math.sin(t * 0.9 - d * 0.55) * 0.13 * u;
      const k = (i * wakeRows + j) * 3;
      wakePos[k] = x;
      wakePos[k + 1] = waveHeight(x, z, t) + 0.045;
      wakePos[k + 2] = z;
    }
  }
  wakeGeo.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- animation
let elapsed = 0;
let lastTime = performance.now();

function animate(now = performance.now()) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  elapsed += dt;
  const t = elapsed;

  ocean.update(t);
  surfer.update(t);

  // board rides the surface
  const bx = Math.sin(t * 0.31) * 0.28;
  const bz = Math.sin(t * 0.22 + 1.1) * 0.16;
  const y = waveHeight(bx, bz, t) + 0.1;
  const n = waveNormal(bx, bz, t);
  surfer.group.position.set(bx, y, bz);
  surfer.group.rotation.order = "YXZ";
  surfer.group.rotation.y = Math.sin(t * 0.24) * 0.075 + 0.02;
  surfer.group.rotation.x = Math.atan2(n.z, n.y);
  surfer.group.rotation.z = Math.atan2(-n.x, n.y) + Math.sin(t * 0.7) * 0.015;
  surfer.group.position.y += Math.sin(t * 1.9) * 0.025;

  surfer.group.updateMatrixWorld();

  worldTail.copy(tailLocal).applyMatrix4(surfer.group.matrixWorld);
  worldNose.copy(noseLocal).applyMatrix4(surfer.group.matrixWorld);

  spawnAccumulator += dt * 105;
  while (spawnAccumulator > 1) {
    spawnAccumulator -= 1;
    spawnParticle(Math.random() < 0.82 ? "tail" : "nose", 1.1, 2.0);
  }
  updateSpray(dt);

  collar.position.set(bx, y - 0.075, bz);
  collar.rotation.y = surfer.group.rotation.y;
  collar.material.opacity = 0.22 + Math.sin(t * 1.7) * 0.045;

  updateWake(t, bx, bz);

  // slow, cinematic camera drift
  const angle = 0.64 + Math.sin(t * 0.065) * 0.14;
  const radius = 10.9 + Math.sin(t * 0.11) * 0.55;
  camera.position.set(
    Math.sin(angle) * radius,
    3.65 + Math.sin(t * 0.17) * 0.32,
    Math.cos(angle) * radius
  );
  camera.lookAt(0.15, 1.95 + Math.sin(t * 0.35) * 0.06, 0);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener("resize", onResize);

animate();
