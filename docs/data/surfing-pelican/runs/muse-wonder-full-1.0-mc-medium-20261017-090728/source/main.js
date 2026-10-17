import * as THREE from "three";
import { createOcean, createBarrel, waveHeight, waveNormal } from "./ocean.js";
import { createPelican, createSurfboard } from "./pelican.js";

const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const amp = reduced ? 0.45 : 1;

const container = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe8ee, 55, 130);

const camera = new THREE.PerspectiveCamera(46, window.innerWidth / window.innerHeight, 0.1, 400);

// --- Sky dome (gradient shader), sun, lights ---
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(180, 24, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      top: { value: new THREE.Color(0x3f8fd2) },
      mid: { value: new THREE.Color(0xa8d8e8) },
      low: { value: new THREE.Color(0xffd9a3) },
    },
    vertexShader: "varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    fragmentShader: `varying vec3 vP; uniform vec3 top; uniform vec3 mid; uniform vec3 low;
      void main(){ float h = normalize(vP).y; vec3 c = h > 0.18 ? mix(mid, top, smoothstep(0.18, 0.75, h)) : mix(low, mid, smoothstep(-0.08, 0.18, h)); gl_FragColor = vec4(c, 1.0); }`,
  })
);
scene.add(sky);

const sun = new THREE.Mesh(new THREE.CircleGeometry(7, 32), new THREE.MeshBasicMaterial({ color: 0xfff0bf, fog: false }));
sun.position.set(-55, 26, -95);
sun.lookAt(0, 4, 0);
scene.add(sun);
const sunGlow = new THREE.Mesh(new THREE.CircleGeometry(13, 32), new THREE.MeshBasicMaterial({ color: 0xffe3a3, transparent: true, opacity: 0.35, fog: false }));
sunGlow.position.copy(sun.position).multiplyScalar(1.01);
sunGlow.lookAt(0, 4, 0);
scene.add(sunGlow);

scene.add(new THREE.HemisphereLight(0xbfe6f5, 0x1d6f7a, 0.95));
const dir = new THREE.DirectionalLight(0xfff1cf, 2.2);
dir.position.set(-22, 28, -14);
dir.castShadow = true;
dir.shadow.mapSize.set(2048, 2048);
dir.shadow.camera.left = -16; dir.shadow.camera.right = 16;
dir.shadow.camera.top = 16; dir.shadow.camera.bottom = -16;
dir.shadow.camera.far = 90;
scene.add(dir);

// --- Ocean, barrel wave, rider ---
const ocean = createOcean();
scene.add(ocean.mesh);
const barrel = createBarrel();
scene.add(barrel);

const rider = new THREE.Group();
const board = createSurfboard();
rider.add(board);
const pelican = createPelican();
rider.add(pelican.group);
scene.add(rider);

// --- Clouds ---
const clouds = [];
const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
for (let i = 0; i < 7; i++) {
  const cloud = new THREE.Group();
  const n = 4 + Math.floor(Math.random() * 3);
  for (let j = 0; j < n; j++) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(1 + Math.random() * 1.4, 8, 6), cloudMat);
    s.position.set(j * 1.5 - n * 0.7, Math.random() * 0.5, Math.random() * 0.8);
    s.scale.y = 0.55;
    cloud.add(s);
  }
  cloud.position.set(-70 + Math.random() * 140, 17 + Math.random() * 12, -55 - Math.random() * 45);
  scene.add(cloud);
  clouds.push({ cloud, speed: 0.4 + Math.random() * 0.5 });
}

// --- Distant island with palms ---
const island = new THREE.Group();
const hill = new THREE.Mesh(new THREE.SphereGeometry(9, 16, 10), new THREE.MeshStandardMaterial({ color: 0x2e7d6b, roughness: 1, flatShading: true }));
hill.scale.set(1.4, 0.32, 0.7);
island.add(hill);
for (const [px, pz, lean] of [[-4, 0, 0.25], [1, 1.5, -0.2], [5, -1, 0.35]]) {
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.3, 5, 7), new THREE.MeshStandardMaterial({ color: 0x8a6a48, roughness: 1 }));
  trunk.position.set(px, 3.4, pz);
  trunk.rotation.z = lean;
  island.add(trunk);
  for (let i = 0; i < 6; i++) {
    const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.28, 3.2, 5), new THREE.MeshStandardMaterial({ color: 0x2f9e63, roughness: 1, flatShading: true }));
    const a = (i / 6) * Math.PI * 2;
    leaf.position.set(px - Math.sin(lean) * 2.4 + Math.cos(a) * 1.1, 6, pz + Math.sin(a) * 1.1);
    leaf.rotation.set(Math.sin(a) * 1.15, 0, -Math.cos(a) * 1.15);
    island.add(leaf);
  }
}
island.position.set(52, -0.5, -68);
scene.add(island);

// --- Distant gulls ---
const gulls = [];
const gullMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
for (let i = 0; i < 4; i++) {
  const gull = new THREE.Group();
  const w1 = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.32), gullMat);
  w1.position.x = -0.72;
  const w2 = w1.clone(); w2.position.x = 0.72;
  const p1 = new THREE.Group(); p1.add(w1);
  const p2 = new THREE.Group(); p2.add(w2);
  gull.add(p1, p2);
  gull.position.set(-60 + i * 22, 13 + i * 1.6, -38 - i * 6);
  scene.add(gull);
  gulls.push({ gull, p1, p2, speed: 1.6 + i * 0.35, phase: i * 1.7 });
}

// --- Spray particles behind the board ---
function sprayTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,0.95)");
  grad.addColorStop(0.55, "rgba(220,245,255,0.55)");
  grad.addColorStop(1, "rgba(220,245,255,0)");
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const SPRAY = 320;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = new Float32Array(SPRAY * 3);
const sprayLife = new Float32Array(SPRAY);
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  size: 0.42, map: sprayTexture(), transparent: true, depthWrite: false, opacity: 0.9, color: 0xeafcff,
}));
spray.frustumCulled = false;
scene.add(spray);
let sprayCursor = 0;

// Foam patches drifting on the surface.
const foams = [];
const foamMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.13 });
for (let i = 0; i < 12; i++) {
  const f = new THREE.Mesh(new THREE.CircleGeometry(0.5 + Math.random() * 1.0, 24), foamMat);
  f.rotation.x = -Math.PI / 2;
  f.position.set(-30 + Math.random() * 60, 0, -25 + Math.random() * 50);
  scene.add(f);
  foams.push(f);
}

// Rider path: carves back and forth across the swell, forever.
function riderPath(t) {
  return new THREE.Vector2(Math.sin(t * 0.42) * 3.4 * amp, Math.sin(t * 0.19 + 0.8) * 1.6);
}

let lastNow = performance.now();
let elapsed = 0;
const lookTarget = new THREE.Vector3();
let prevPos = riderPath(0);

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min((now - lastNow) / 1000, 0.05);
  lastNow = now;
  elapsed += dt;
  const t = elapsed;

  ocean.update(t);
  barrel.position.y = 3.0 + Math.sin(t * 0.7) * 0.18 * amp;
  barrel.rotation.y = Math.sin(t * 0.21) * 0.04;

  // Rider follows the wave field, leaning into each carve.
  const p = riderPath(t);
  const vel = new THREE.Vector2().subVectors(p, prevPos);
  prevPos = p.clone();
  const y = waveHeight(p.x, p.y, t);
  rider.position.set(p.x, y + 0.18, p.y);

  const normal = waveNormal(p.x, p.y, t);
  const carve = THREE.MathUtils.clamp(-vel.x * 55, -0.5, 0.5) * amp;
  // Fixed base yaw keeps beak and outstretched wings both readable from the camera arc.
  const yaw = 0.05 + Math.sin(t * 0.42) * 0.3 * amp;
  rider.rotation.order = "YXZ";
  rider.rotation.set(Math.asin(THREE.MathUtils.clamp(normal.z, -1, 1)) * 0.8, yaw + carve * 0.35, carve - Math.asin(THREE.MathUtils.clamp(normal.x, -1, 1)) * 0.6);

  // Pelican body language: balance, bob, and a bigger wing-beat every few seconds.
  const P = pelican.parts;
  const bigFlap = Math.max(0, Math.sin(t * 0.9)) ** 6;
  const flap = (Math.sin(t * 2.1) * 0.14 + bigFlap * Math.sin(t * 9) * 0.35) * amp;
  P.wingFront.rotation.x = 0.22 + flap + carve * 0.7;
  P.wingBack.rotation.x = -0.22 - flap * 0.85 + carve * 0.7;
  P.body.position.y = 1.28 + Math.sin(t * 2.4) * 0.045 * amp;
  P.body.rotation.z = Math.sin(t * 1.3) * 0.05 * amp + carve * 0.25;
  P.neck.rotation.z = Math.sin(t * 1.7) * 0.08 * amp - carve * 0.3;
  P.neck.rotation.x = Math.sin(t * 0.83) * 0.1 * amp;
  P.head.rotation.y = Math.sin(t * 0.53) * 0.28 * amp;
  P.head.rotation.z = Math.sin(t * 2.3 + 1) * 0.05 * amp;
  const pouchWobble = 1 + Math.sin(t * 3.1) * 0.08 * amp;
  P.pouch.scale.set(0.5 * pouchWobble, 0.17 / Math.sqrt(pouchWobble), 0.13);
  P.tail.rotation.x = Math.sin(t * 2.8) * 0.16 * amp;
  P.tail.rotation.z = 0.12 + Math.sin(t * 1.9) * 0.06 * amp;

  // Spray kicked up from the board's tail.
  const back = new THREE.Vector3(0, 0.15, -1.9).applyQuaternion(rider.quaternion);
  for (let k = 0; k < 5; k++) {
    const i = sprayCursor = (sprayCursor + 1) % SPRAY;
    sprayPos[i * 3] = rider.position.x + back.x + (Math.random() - 0.5) * 0.5;
    sprayPos[i * 3 + 1] = rider.position.y + back.y;
    sprayPos[i * 3 + 2] = rider.position.z + back.z + (Math.random() - 0.5) * 0.5;
    sprayVel[i * 3] = back.x * (1.4 + Math.random() * 1.4) + (Math.random() - 0.5);
    sprayVel[i * 3 + 1] = 1.6 + Math.random() * 1.9;
    sprayVel[i * 3 + 2] = back.z * (1.4 + Math.random() * 1.4) + (Math.random() - 0.5);
    sprayLife[i] = 0.7 + Math.random() * 0.5;
  }
  for (let i = 0; i < SPRAY; i++) {
    if (sprayLife[i] <= 0) { sprayPos[i * 3 + 1] = -50; continue; }
    sprayLife[i] -= dt;
    sprayVel[i * 3 + 1] -= 4.6 * dt;
    sprayPos[i * 3] += sprayVel[i * 3] * dt;
    sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
    sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Ambient life: clouds drift, foam rides the surface, gulls cross the sky.
  for (const { cloud, speed } of clouds) {
    cloud.position.x += speed * dt;
    if (cloud.position.x > 85) cloud.position.x = -85;
  }
  for (const f of foams) {
    f.position.y = waveHeight(f.position.x, f.position.z, t) + 0.06;
    f.position.x += dt * 0.7;
    if (f.position.x > 38) f.position.x = -38;
  }
  for (const g of gulls) {
    g.gull.position.x += g.speed * dt;
    g.gull.position.y += Math.sin(t * 1.4 + g.phase) * dt * 0.5;
    const flapG = Math.sin(t * 7 + g.phase) * 0.55;
    g.p1.rotation.z = flapG; g.p2.rotation.z = -flapG;
    if (g.gull.position.x > 75) g.gull.position.x = -75;
  }

  // Self-driving camera: a slow, lazy arc around the rider. No user input.
  const ang = 0.65 + Math.sin(t * 0.11) * 0.38 * amp;
  const radius = 10.5 + Math.sin(t * 0.07 + 2) * 1.3;
  camera.position.set(
    rider.position.x + Math.sin(ang) * radius,
    3.1 + Math.sin(t * 0.23) * 0.45 * amp,
    rider.position.z + Math.cos(ang) * radius
  );
  lookTarget.lerp(new THREE.Vector3(rider.position.x, rider.position.y + 1.25, rider.position.z), 0.06);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
