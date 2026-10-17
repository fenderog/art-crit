import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { createSky, SUN_DIR, palette } from "./sky.js";
import { createOcean, heightAt, normalAt, VX, TRAIL_COUNT } from "./ocean.js";
import { createBoard } from "./board.js";
import { createPelican } from "./pelican.js";
import { createSpray } from "./spray.js";

// ---------- renderer / scene ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.05, 4000);

const sky = createSky();
scene.add(sky.group);

const ocean = createOcean();
scene.add(ocean.mesh);

// ---------- rider ----------
const rider = new THREE.Group();
scene.add(rider);
const board = createBoard();
rider.add(board.group);
const pelican = createPelican();
pelican.group.position.set(-0.05, board.deckHeight(-0.05) + 0.006, 0);
rider.add(pelican.group);

const spray = createSpray(5000);
scene.add(spray.points);

// ---------- lights ----------
const hemi = new THREE.HemisphereLight("#a9c8ff", "#2b7b80", 1.15);
scene.add(hemi);
const sun = new THREE.DirectionalLight(palette.sun, 2.7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -2.2;
sun.shadow.camera.right = 2.2;
sun.shadow.camera.top = 2.2;
sun.shadow.camera.bottom = -2.2;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.015;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight("#ffe0bf", 0.75);
scene.add(fill, fill.target);

// ---------- distant pelicans gliding in a line ----------
const flock = new THREE.Group();
scene.add(flock);
const birdMat = new THREE.MeshBasicMaterial({ color: new THREE.Color("#4a4f5c") });
const birds = [];
for (let i = 0; i < 4; i++) {
  const b = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), birdMat);
  body.scale.set(0.9, 0.22, 0.22);
  b.add(body);
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.9, 6), birdMat);
  beak.rotation.z = -Math.PI / 2;
  beak.position.set(1.2, 0.05, 0);
  b.add(beak);
  const wings = [1, -1].map((s) => {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 1.9), birdMat);
    w.geometry.translate(0, 0, 0.95 * s);
    b.add(w);
    return { w, s };
  });
  b.position.set(-i * 3.2, i * 0.15, -i * 1.6);
  flock.add(b);
  birds.push({ b, wings, phase: i * 0.45 });
}

// ---------- board motion along the wave face ----------
function boardPath(t) {
  return [
    2.6 * Math.sin(0.27 * t) + 0.9 * Math.sin(0.61 * t + 1.0),
    6.0 + 2.1 * Math.sin(0.62 * t) + 0.55 * Math.sin(1.37 * t + 2.0),
  ];
}

const trail = [];
for (let i = 0; i < TRAIL_COUNT; i++) trail.push({ x: 0, z: 0, age: 99 });
let trailCursor = 0;
let trailTimer = 0;
const TRAIL_LIFE = 2.6;

const tmp = {
  n: new THREE.Vector3(),
  f: new THREE.Vector3(),
  side: new THREE.Vector3(),
  up: new THREE.Vector3(),
  m: new THREE.Matrix4(),
  q: new THREE.Quaternion(),
  camLocal: new THREE.Vector3(),
};
let prevHeading = null;
let turnRate = 0;
let lean = 0;
let compress = 0;
const camTarget = new THREE.Vector3(0, 1.5, 6);
const camPos = new THREE.Vector3(5, 3, 14);
let first = true;

function rand(a, b) {
  return a + Math.random() * (b - a);
}

function updateRider(t, dt) {
  const [x, zRaw] = boardPath(t);
  const z = Math.max(3.7, zRaw);
  const h = 0.02;
  const [x1, z1] = boardPath(t + h);
  const [x0, z0] = boardPath(t - h);
  const hx = VX + (x1 - x0) / (2 * h);
  const hz = (Math.max(3.7, z1) - Math.max(3.7, z0)) / (2 * h);
  const speed = Math.hypot(hx, hz);
  const heading = Math.atan2(hz, hx);
  if (prevHeading !== null && dt > 0) {
    const raw = (heading - prevHeading) / dt;
    turnRate += (raw - turnRate) * Math.min(1, dt * 6);
  }
  prevHeading = heading;
  const targetLean = THREE.MathUtils.clamp(speed * turnRate * 0.16, -1, 1);
  lean += (targetLean - lean) * Math.min(1, dt * 4);

  // compression: going down the face (toward +z) loads the legs at the bottom turn
  const accel = (boardPath(t + h)[1] - 2 * zRaw + boardPath(t - h)[1]) / (h * h);
  const targetCompress = THREE.MathUtils.clamp(-accel * 0.25 + Math.abs(lean) * 0.4, 0, 1);
  compress += (targetCompress - compress) * Math.min(1, dt * 3);

  const n = normalAt(x, z, tmp.n);
  const f = tmp.f.set(hx, 0, hz).normalize();
  f.addScaledVector(n, -f.dot(n)).normalize();
  const side = tmp.side.crossVectors(f, n).normalize();
  const up = tmp.up.copy(n).addScaledVector(side, lean * 0.3).normalize();
  side.crossVectors(f, up).normalize();
  f.crossVectors(up, side).normalize();
  tmp.m.makeBasis(f, up, side);
  tmp.q.setFromRotationMatrix(tmp.m);
  if (first) rider.quaternion.copy(tmp.q);
  else rider.quaternion.slerp(tmp.q, Math.min(1, dt * 10));
  const y = heightAt(x, z);
  rider.position.set(x, y + 0.035, z);

  // foam trail left by the tail
  trailTimer += dt;
  if (trailTimer > 0.045) {
    trailTimer = 0;
    const p = trail[trailCursor];
    p.x = x - f.x * 0.95;
    p.z = z - f.z * 0.95;
    p.age = 0;
    trailCursor = (trailCursor + 1) % TRAIL_COUNT;
  }
  for (let i = 0; i < TRAIL_COUNT; i++) {
    const p = trail[i];
    p.age += dt;
    p.x -= VX * dt;
    p.z -= 0.9 * dt;
    const k = Math.min(1, p.age / TRAIL_LIFE);
    const r = 0.28 + p.age * 0.3;
    ocean.trail[i].set(p.x, p.z, Math.pow(1 - k, 1.3), 1 / (r * r));
  }
  ocean.uniforms.uBoard.value.copy(rider.position);

  // rail spray, heavier in hard turns
  const outward = lean >= 0 ? -1 : 1;
  const rate = 50 + 900 * Math.abs(lean) ** 1.5;
  const count = Math.floor(rate * dt + Math.random());
  for (let i = 0; i < count; i++) {
    const back = rand(0.4, 1.0);
    const px = x - f.x * back + side.x * outward * 0.26;
    const pz = z - f.z * back + side.z * outward * 0.26;
    const s = rand(1.2, 3.6) * (0.5 + Math.abs(lean));
    spray.spawn(
      px,
      y + 0.02,
      pz,
      side.x * outward * s - f.x * rand(0.5, 2) + up.x * rand(1, 3.5),
      up.y * rand(1.2, 3.8) * (0.6 + Math.abs(lean)),
      side.z * outward * s - f.z * rand(0.5, 2) + up.z * rand(1, 3.5),
      { life: rand(0.5, 1.1), size: rand(0.05, 0.16), alpha: 0.85, drag: 0.6, gravity: 9.8, airX: -VX, airZ: -2 }
    );
  }

  pelican.group.updateMatrixWorld();
  tmp.camLocal.copy(camera.position);
  pelican.group.worldToLocal(tmp.camLocal);
  pelican.update({ t, dt, lean, compress, camLocal: tmp.camLocal });
}

function updateWaveSpray(dt) {
  // offshore wind feathers mist off the lip
  let count = Math.floor(220 * dt + Math.random());
  for (let i = 0; i < count; i++) {
    const x = rand(-9, 40);
    const top = heightAt(x, 0) + 0.25;
    spray.spawn(x, top + rand(-0.1, 0.25), rand(1.7, 2.4), rand(-0.3, 0.3), rand(0.8, 2.6), rand(-1.5, -4.5), {
      life: rand(1.2, 2.4),
      size: rand(0.15, 0.4),
      alpha: 0.12,
      drag: 0.8,
      gravity: 2.2,
      airX: -VX,
      airZ: -6,
    });
  }
  // whitewater mist rolling off the broken section
  count = Math.floor(110 * dt + Math.random());
  for (let i = 0; i < count; i++) {
    const x = rand(-40, -9);
    const z = rand(-1, 7);
    spray.spawn(x, heightAt(x, z) + rand(0.1, 0.6), z, rand(-0.5, 0.5), rand(0.4, 1.2), rand(0.2, 1.4), {
      life: rand(2, 3.5),
      size: rand(0.7, 1.5),
      alpha: 0.09,
      drag: 0.5,
      gravity: 0.15,
      airX: -VX,
      airZ: 0.5,
    });
  }
  // chunky droplets tumbling down the broken face
  count = Math.floor(150 * dt + Math.random());
  for (let i = 0; i < count; i++) {
    const x = rand(-40, -8);
    spray.spawn(x, heightAt(x, 0) + rand(0.0, 0.4), rand(0.8, 1.8), rand(-0.4, 0.4), rand(1.5, 3.5), rand(1.5, 3.5), {
      life: rand(0.8, 1.4),
      size: rand(0.12, 0.3),
      alpha: 0.6,
      drag: 0.3,
      gravity: 9.8,
      airX: -VX,
      airZ: 0,
    });
  }
}

function updateCamera(t, dt) {
  const target = tmp.up.copy(rider.position).add(new THREE.Vector3(0.25, 0.65, 0));
  const k = first ? 1 : 1 - Math.exp(-dt * 2.5);
  camTarget.lerp(target, k);
  const az = 0.75 + 0.5 * Math.sin(t * 0.05) + 0.15 * Math.sin(t * 0.13 + 1.0);
  const dist = 3.9 + 1.1 * Math.sin(t * 0.043 + 1.0);
  const elev = 0.05 + 0.06 * Math.sin(t * 0.07 + 2.0);
  const desired = new THREE.Vector3(
    camTarget.x + Math.sin(az) * Math.cos(elev) * dist,
    camTarget.y + Math.sin(elev) * dist,
    camTarget.z + Math.cos(az) * Math.cos(elev) * dist
  );
  desired.y = Math.min(desired.y, camTarget.y + 0.9);
  desired.y = Math.max(desired.y, heightAt(desired.x, desired.z) + 0.7);
  camPos.lerp(desired, first ? 1 : 1 - Math.exp(-dt * 1.5));
  camera.position.copy(camPos);
  // a touch of handheld drift
  camera.position.x += Math.sin(t * 1.3) * 0.03;
  camera.position.y += Math.sin(t * 1.7 + 1) * 0.03;
  camera.lookAt(camTarget);
}

function updateLights() {
  sun.target.position.copy(rider.position);
  sun.position.copy(rider.position).addScaledVector(SUN_DIR, 20);
  fill.target.position.copy(rider.position);
  fill.position.copy(camera.position).add(new THREE.Vector3(0, 2, 0));
}

function updateFlock(t, dt) {
  const span = 260;
  const fx = ((t * 3.5) % span) - span / 2;
  flock.position.set(fx, 17 + Math.sin(t * 0.3) * 0.8, -55);
  for (const bd of birds) {
    const cycle = (t * 0.35 + bd.phase) % 1;
    const flapping = cycle < 0.35;
    const ang = flapping ? Math.sin(t * 7 + bd.phase * 5) * 0.45 : 0.06;
    for (const { w, s } of bd.wings) w.rotation.x = -s * ang;
    bd.b.position.y = bd.b.position.y * 0.98 + (Math.sin(t * 0.8 + bd.phase * 3) * 0.3) * 0.02;
  }
}

// ---------- post ----------
const rt = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.28, 0.4, 1.25);
composer.addPass(bloom);
composer.addPass(new OutputPass());

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.setSize(w, h);
  const px = h * renderer.getPixelRatio();
  spray.material.uniforms.uScale.value = (px * 0.5) / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
}
window.addEventListener("resize", resize);
resize();

// ---------- loop ----------
const timer = new THREE.Timer();
let t = 3;
function frame() {
  timer.update();
  const dt = Math.min(timer.getDelta(), 1 / 20);
  t += dt;
  ocean.update(t);
  updateRider(t, dt);
  updateWaveSpray(dt);
  spray.update(dt);
  updateCamera(t, dt);
  updateLights();
  updateFlock(t, dt);
  sky.update(camera);
  first = false;
  composer.render(dt);
  requestAnimationFrame(frame);
}
// warm the spray up so the first frame isn't empty
for (let i = 0; i < 90; i++) {
  ocean.update(t);
  updateRider(t, 1 / 30);
  updateWaveSpray(1 / 30);
  spray.update(1 / 30);
  t += 1 / 30;
  first = false;
}
first = true;
requestAnimationFrame(frame);
