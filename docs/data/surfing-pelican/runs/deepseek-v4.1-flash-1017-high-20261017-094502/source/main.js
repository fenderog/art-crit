import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { createSurfingPelican } from './src/pelican.js';
import { createEnvironment, SUN_DIR } from './src/environment.js';
import { createParticles } from './src/particles.js';
import { makeGrainDataURL } from './src/textures.js';
import { waveGradient, waveHeight } from './src/waves.js';

const app = document.getElementById('app');

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: 'high-performance',
  alpha: false,
  stencil: false,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#e9c4a8');

const camera = new THREE.PerspectiveCamera(
  40,
  window.innerWidth / window.innerHeight,
  0.1,
  1200,
);

const environment = createEnvironment(scene, camera);
const surfer = createSurfingPelican();
scene.add(surfer.group);
const particles = createParticles(scene);

// ---------------------------------------------------------------- post fx
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

const bloom = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.3,
  0.62,
  0.9,
);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// Multisampled offscreen buffer (WebGL2)
if (composer.renderTarget1) composer.renderTarget1.samples = 4;
if (composer.renderTarget2) composer.renderTarget2.samples = 4;

// ------------------------------------------------------------------ state
const SPEED = 3.35;
const board = {
  position: new THREE.Vector3(),
  forward: new THREE.Vector3(1, 0, 0),
  right: new THREE.Vector3(0, 0, 1),
  yaw: 0,
};

surfer.group.rotation.order = 'YXZ';

const grad = { x: 0, z: 0 };
const pointer = new THREE.Vector2(0, 0);
const pointerTarget = new THREE.Vector2(0, 0);
const lookTarget = new THREE.Vector3(0, 1.7, 0);
const desiredCam = new THREE.Vector3();
const baseOffset = new THREE.Vector3(2.45, 2.42, 7.9);

let simTime = 0;
let lastFrame = performance.now();
let started = false;

function resetPointer() {
  pointerTarget.set(0, 0);
}

window.addEventListener('pointermove', (event) => {
  pointerTarget.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointerTarget.y = (event.clientY / window.innerHeight) * 2 - 1;
});
window.addEventListener('pointerleave', resetPointer);
window.addEventListener('blur', resetPointer);

function setSizes() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
  renderer.setSize(w, h);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.setSize(w, h);
  bloom.setSize(w, h);
  particles.setPixelScale(camera, renderer);
}

window.addEventListener('resize', setSizes);

const grain = document.getElementById('grain');
if (grain) grain.style.backgroundImage = `url(${makeGrainDataURL()})`;

// ------------------------------------------------------------------ motion
function updateBoard(t) {
  const x = t * SPEED;
  const z =
    Math.sin(x * 0.031) * 2.3 +
    Math.sin(t * 0.13 + 0.4) * 0.45;
  const vz =
    Math.cos(x * 0.031) * 0.031 * 2.3 * SPEED +
    Math.cos(t * 0.13 + 0.4) * 0.13 * 0.45;
  const vx = SPEED;
  const yaw = -Math.atan2(vz, vx);

  const y = waveHeight(x, z, t) + 0.03;
  board.position.set(x, y, z);
  board.yaw = yaw;
  board.forward.set(Math.cos(yaw), 0, -Math.sin(yaw));
  board.right.set(Math.sin(yaw), 0, Math.cos(yaw));

  waveGradient(x, z, t, grad);

  const pitch = Math.atan(grad.x * 1.35);
  const roll = Math.atan(-grad.z * 1.35);
  const bank = Math.sin(t * 0.23 + 1.4) * 0.035;
  surfer.group.position.copy(board.position);
  surfer.group.rotation.set(roll + bank, yaw, pitch);

  return { pitch, roll };
}

function updateCamera(t, dt) {
  pointer.lerp(pointerTarget, 1 - Math.exp(-dt * 3.0));

  // slow, cinematic breathing orbit + a gentle opening push-in
  const intro = 1 + 0.55 * Math.exp(-t * 0.22);
  const driftX = Math.sin(t * 0.073) * 0.55 + Math.sin(t * 0.021 + 1.7) * 0.35;
  const driftY = Math.sin(t * 0.11 + 0.6) * 0.22;
  const driftZ = Math.sin(t * 0.061 + 2.1) * 0.4;

  desiredCam.set(
    board.position.x + (baseOffset.x + driftX) * intro + pointer.x * 0.8,
    board.position.y + (baseOffset.y + driftY) * intro + pointer.y * -0.35,
    board.position.z + (baseOffset.z + driftZ) * intro,
  );

  const lerp = 1 - Math.exp(-dt * (started ? 2.4 : 20));
  camera.position.lerp(desiredCam, lerp);

  const target = new THREE.Vector3(
    board.position.x + 0.42 + pointer.x * 0.22,
    board.position.y + 1.66 + pointer.y * -0.1,
    board.position.z,
  );
  lookTarget.lerp(target, 1 - Math.exp(-dt * 3.2));
  camera.lookAt(lookTarget);
}

function tick(now) {
  const dt = Math.min(Math.max(0, (now - lastFrame) / 1000), 0.05);
  lastFrame = now;
  simTime += dt;
  const t = simTime;

  const slopes = updateBoard(t);
  surfer.update(t, dt, slopes.pitch, slopes.roll);
  updateCamera(t, dt);
  environment.update(t, dt, board.position);
  particles.update(t, dt, board);

  composer.render();

  if (!started) {
    started = true;
    camera.position.copy(desiredCam);
    lookTarget.set(
      board.position.x + 0.42,
      board.position.y + 1.66,
      board.position.z,
    );
    document.body.classList.add('is-ready');
  }
}

renderer.setAnimationLoop(tick);

// Start with a sensible framing so the very first frame is already composed.
updateBoard(0);
camera.position.set(
  board.position.x + baseOffset.x * 1.4,
  board.position.y + baseOffset.y * 1.4,
  board.position.z + baseOffset.z * 1.4,
);
lookTarget.set(board.position.x + 0.42, board.position.y + 1.66, board.position.z);
camera.lookAt(lookTarget);
setSizes();
