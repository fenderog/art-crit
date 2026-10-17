import * as THREE from 'three';
import { createSky } from './sky.js';
import { createWater, waveHeight } from './water.js';
import { createSurfboard } from './surfboard.js';
import { createPelican } from './pelican.js';
import { createSpray } from './spray.js';
import { createWake } from './wake.js';
import { createEnvironment } from './environment.js';
import { createBirds } from './birds.js';

// ---- renderer / scene / camera ----
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog('#ecd5a4', 65, 330);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  1600
);

// ---- sky & lights ----
const sky = createSky();
scene.add(sky.mesh);

const sun = new THREE.DirectionalLight('#ffdcae', 2.0);
sun.position.copy(sky.sunDir).multiplyScalar(90);
scene.add(sun);
scene.add(new THREE.HemisphereLight('#cfe8ff', '#0f5e6e', 0.75));

// ---- world ----
const water = createWater();
scene.add(water.mesh);

const environment = createEnvironment();
scene.add(environment.group);

const birds = createBirds();
scene.add(birds.group);

// ---- board + pelican ----
const boardGroup = new THREE.Group();
scene.add(boardGroup);
const surfboard = createSurfboard();
boardGroup.add(surfboard.group);
const pelican = createPelican();
pelican.group.position.y = surfboard.deckY;
boardGroup.add(pelican.group);

const spray = createSpray();
scene.add(spray.mesh);
const wake = createWake();
scene.add(wake.mesh);

// ---- board path (the pelican carves a lazy figure through the swell) ----
function boardPath(tt, out) {
  out.set(Math.sin(tt * 0.26) * 5.2, 0, Math.cos(tt * 0.21) * 3.8);
  return out;
}
function boardPathVel(tt, out = new THREE.Vector3()) {
  out.set(5.2 * 0.26 * Math.cos(tt * 0.26), 0, -3.8 * 0.21 * Math.sin(tt * 0.21));
  return out;
}

// ---- ride state ----
let t = 0;
let prevYaw = Math.atan2(boardPathVel(0).x, boardPathVel(0).z);
let rollS = 0;
let pitchS = 0;
let sprayAcc = 0;
let wakeTimer = 0;

const boardPos = new THREE.Vector3();
const boardVel = new THREE.Vector3();
const euler = new THREE.Euler(0, 0, 0, 'YXZ');
const dummy = new THREE.Object3D();
const camPos = new THREE.Vector3(9, 4.5, 9);
const camTarget = new THREE.Vector3();
const desired = new THREE.Vector3();
const lookAt = new THREE.Vector3();

boardPath(0, boardPos);
camTarget.copy(boardPos);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---- animation loop ----
const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05);
  t += dt;

  water.update(t);
  environment.update(t);
  birds.update(t);

  // --- board rides the wave surface ---
  boardPath(t, boardPos);
  boardPathVel(t, boardVel);
  const px = boardPos.x;
  const pz = boardPos.z;
  boardPos.y = waveHeight(px, pz, t) + 0.02;

  const yaw = Math.atan2(boardVel.x, boardVel.z);
  let dyaw = yaw - prevYaw;
  while (dyaw > Math.PI) dyaw -= Math.PI * 2;
  while (dyaw < -Math.PI) dyaw += Math.PI * 2;
  const turnRate = dt > 0 ? dyaw / dt : 0;
  prevYaw = yaw;

  const fx = Math.sin(yaw);
  const fz = Math.cos(yaw);
  const sx = Math.cos(yaw);
  const sz = -Math.sin(yaw);
  const hA = waveHeight(px + fx * 0.8, pz + fz * 0.8, t);
  const hB = waveHeight(px - fx * 0.8, pz - fz * 0.8, t);
  const hR = waveHeight(px + sx * 0.55, pz + sz * 0.55, t);
  const hL = waveHeight(px - sx * 0.55, pz - sz * 0.55, t);
  const pitch = -Math.atan2(hA - hB, 1.6) * 0.75; // follow the wave face
  const lateral = Math.atan2(hR - hL, 1.1);
  const bank = THREE.MathUtils.clamp(turnRate * 0.85, -0.5, 0.5); // lean into turns
  const roll = lateral * 0.65 - bank;

  const k = 1 - Math.exp(-dt * 8);
  pitchS += (pitch - pitchS) * k;
  rollS += (roll - rollS) * k;

  boardGroup.position.copy(boardPos);
  euler.set(pitchS, yaw, rollS);
  boardGroup.quaternion.setFromEuler(euler);
  boardGroup.updateMatrixWorld(true);

  pelican.update(t, dt, { roll: rollS, pitch: pitchS, speed: boardVel.length(), turnRate });

  // --- spray off the nose & the carving rail ---
  const speed = boardVel.length();
  sprayAcc += dt * (2 + speed * 6 + Math.abs(turnRate) * 26);
  while (sprayAcc >= 1) {
    sprayAcc -= 1;
    dummy.position.set((Math.random() - 0.5) * 0.5, 0.12, 1.3 + Math.random() * 0.35);
    boardGroup.localToWorld(dummy.position);
    spray.spawn(
      dummy.position.x,
      dummy.position.y,
      dummy.position.z,
      boardVel.x * 0.55 + (Math.random() - 0.5) * 2.4,
      1.3 + Math.random() * 2.3,
      boardVel.z * 0.55 + (Math.random() - 0.5) * 2.4
    );
    if (Math.abs(turnRate) > 0.45) {
      const side = Math.sign(turnRate);
      dummy.position.set(side * 0.42, 0.06, 0.35);
      boardGroup.localToWorld(dummy.position);
      spray.spawn(
        dummy.position.x,
        dummy.position.y,
        dummy.position.z,
        boardVel.x * 0.3 + sx * side * 3.2,
        1.6 + Math.random() * 2.0,
        boardVel.z * 0.3 + sz * side * 3.2
      );
    }
  }
  spray.update(dt, t);

  // --- foam wake behind the tail ---
  wakeTimer += dt;
  if (wakeTimer > 0.07) {
    wakeTimer = 0;
    dummy.position.set((Math.random() - 0.5) * 0.25, 0, -1.35);
    boardGroup.localToWorld(dummy.position);
    wake.spawn(dummy.position.x, dummy.position.z);
  }
  wake.update(dt, t);

  // --- slow drifting cinematic camera, never dips under the waves ---
  const ang = t * 0.11;
  const rad = 8.6 + Math.sin(t * 0.073) * 1.6;
  const hgt = 3.2 + Math.sin(t * 0.09) * 0.9 + Math.max(0, Math.sin(t * 0.05)) * 1.3;
  desired.set(boardPos.x + Math.cos(ang) * rad, hgt, boardPos.z + Math.sin(ang) * rad);
  desired.y = Math.max(desired.y, waveHeight(desired.x, desired.z, t) + 0.9);
  camPos.lerp(desired, 1 - Math.exp(-dt * 2.2));
  camPos.y = Math.max(camPos.y, waveHeight(camPos.x, camPos.z, t) + 0.55);
  camTarget.lerp(boardPos, 1 - Math.exp(-dt * 4));
  camera.position.copy(camPos);
  lookAt.copy(camTarget);
  lookAt.y += 1.0;
  camera.lookAt(lookAt);

  renderer.render(scene, camera);
});
