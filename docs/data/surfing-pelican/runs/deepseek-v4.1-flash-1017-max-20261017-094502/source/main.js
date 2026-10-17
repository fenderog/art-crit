import * as THREE from 'three';
import { createWorld } from './src/world.js';
import { createPelican } from './src/pelican.js';
import { SpraySystem } from './src/spray.js';

const canvas = document.getElementById('scene');

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  stencil: false,
  powerPreference: 'high-performance'
});
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.setClearColor(0x7f9fba, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 1200);

const world = createWorld(scene, camera, renderer);
const pelican = createPelican(scene, camera);
const spray = new SpraySystem(scene, renderer, camera);

// --------------------------------------------------------------- camera rig
const cameraState = {
  baseAzimuth: 0.37,
  baseElevation: 0.105,
  radius: 10.2,
  targetY: 2.3,
  dragYaw: 0,
  dragPitch: 0,
  targetDragYaw: 0,
  targetDragPitch: 0,
  pointerX: 0,
  pointerY: 0,
  targetPointerX: 0,
  targetPointerY: 0
};

const cameraTarget = new THREE.Vector3(0, 2.3, -0.15);
const desiredPosition = new THREE.Vector3();
const smoothedLook = cameraTarget.clone();
let cameraReady = false;

function responsiveCamera() {
  const portrait = window.innerWidth / Math.max(1, window.innerHeight) < 0.82;
  camera.fov = portrait ? 50 : 38;
  cameraState.radius = portrait ? 12.4 : 10.2;
  cameraState.baseElevation = portrait ? 0.14 : 0.105;
  cameraState.baseAzimuth = portrait ? 0.3 : 0.37;
  cameraState.targetY = portrait ? 2.15 : 2.3;
  camera.updateProjectionMatrix();
}

function resize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(1, height);
  responsiveCamera();
}

function updateCamera(time, dt, boardPosition, immediate = false) {
  const damping = immediate ? 1 : 1 - Math.exp(-dt * 3.8);
  const pointerDamping = immediate ? 1 : 1 - Math.exp(-dt * 3.2);

  cameraState.dragYaw +=
    (cameraState.targetDragYaw - cameraState.dragYaw) * (immediate ? 1 : 1 - Math.exp(-dt * 7));
  cameraState.dragPitch +=
    (cameraState.targetDragPitch - cameraState.dragPitch) * (immediate ? 1 : 1 - Math.exp(-dt * 7));
  cameraState.pointerX +=
    (cameraState.targetPointerX - cameraState.pointerX) * pointerDamping;
  cameraState.pointerY +=
    (cameraState.targetPointerY - cameraState.pointerY) * pointerDamping;

  const autoDrift = Math.sin(time * 0.055) * 0.065 + Math.sin(time * 0.019 + 1.2) * 0.025;
  const azimuth =
    cameraState.baseAzimuth +
    autoDrift +
    cameraState.dragYaw +
    cameraState.pointerX * 0.045;
  const elevation = THREE.MathUtils.clamp(
    cameraState.baseElevation +
      cameraState.dragPitch +
      cameraState.pointerY * 0.018 +
      Math.sin(time * 0.047 + 0.4) * 0.012,
    0.025,
    0.55
  );

  const boardLift = (boardPosition.y - 0.32) * 0.15;
  cameraTarget.set(
    0,
    cameraState.targetY + boardLift + Math.sin(time * 0.44) * 0.012,
    -0.12
  );

  const radius = cameraState.radius + Math.sin(time * 0.042) * 0.16;
  desiredPosition.set(
    cameraTarget.x + Math.sin(azimuth) * Math.cos(elevation) * radius,
    cameraTarget.y + Math.sin(elevation) * radius,
    cameraTarget.z + Math.cos(azimuth) * Math.cos(elevation) * radius
  );

  if (!cameraReady || immediate) {
    camera.position.copy(desiredPosition);
    smoothedLook.copy(cameraTarget);
    camera.lookAt(smoothedLook);
    cameraReady = true;
    return;
  }

  camera.position.lerp(desiredPosition, damping);
  smoothedLook.lerp(cameraTarget, damping);
  camera.lookAt(smoothedLook);
}

// ---------------------------------------------------------------- interact
const interaction = {
  dragging: false,
  pointerId: null,
  lastX: 0,
  lastY: 0,
  downX: 0,
  downY: 0,
  travel: 0
};

function normalisePointer(event) {
  cameraState.targetPointerX = (event.clientX / window.innerWidth) * 2 - 1;
  cameraState.targetPointerY = (event.clientY / window.innerHeight) * 2 - 1;
}

canvas.addEventListener('pointerdown', (event) => {
  interaction.dragging = true;
  interaction.pointerId = event.pointerId;
  interaction.lastX = event.clientX;
  interaction.lastY = event.clientY;
  interaction.downX = event.clientX;
  interaction.downY = event.clientY;
  interaction.travel = 0;
  canvas.setPointerCapture(event.pointerId);
  document.body.classList.add('is-dragging');
  normalisePointer(event);
});

canvas.addEventListener('pointermove', (event) => {
  normalisePointer(event);
  if (!interaction.dragging) return;

  const dx = event.clientX - interaction.lastX;
  const dy = event.clientY - interaction.lastY;
  interaction.lastX = event.clientX;
  interaction.lastY = event.clientY;
  interaction.travel += Math.abs(dx) + Math.abs(dy);

  cameraState.targetDragYaw = THREE.MathUtils.clamp(
    cameraState.targetDragYaw - dx * 0.005,
    -0.78,
    0.78
  );
  cameraState.targetDragPitch = THREE.MathUtils.clamp(
    cameraState.targetDragPitch + dy * 0.003,
    -0.09,
    0.27
  );
});

function endPointer(event) {
  if (!interaction.dragging) return;
  interaction.dragging = false;
  document.body.classList.remove('is-dragging');
  if (canvas.hasPointerCapture(event.pointerId)) {
    canvas.releasePointerCapture(event.pointerId);
  }

  if (interaction.travel < 8) {
    pelican.triggerFlap(clock.getElapsedTime());
    spray.burst(pelican.rider, 86);
    document.body.classList.add('has-interacted');
  }
}

canvas.addEventListener('pointerup', endPointer);
canvas.addEventListener('pointercancel', (event) => {
  if (!interaction.dragging) return;
  interaction.dragging = false;
  document.body.classList.remove('is-dragging');
  if (canvas.hasPointerCapture(event.pointerId)) {
    canvas.releasePointerCapture(event.pointerId);
  }
});

canvas.addEventListener('pointerleave', () => {
  if (!interaction.dragging) {
    cameraState.targetPointerX = 0;
    cameraState.targetPointerY = 0;
  }
});

window.addEventListener('keydown', (event) => {
  if (event.code === 'Space' || event.code === 'Enter') {
    event.preventDefault();
    pelican.triggerFlap(clock.getElapsedTime());
    spray.burst(pelican.rider, 64);
    document.body.classList.add('has-interacted');
  }
});

window.addEventListener('resize', resize);

// ------------------------------------------------------------------- loop
const clock = new THREE.Clock();
let firstFrame = true;
let elapsed = 0;

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  const boardState = pelican.update(elapsed, dt);
  spray.update(dt, pelican.rider);
  world.update(elapsed, dt, boardState.position, boardState.forward);
  updateCamera(elapsed, dt, boardState.position);

  renderer.render(scene, camera);

  if (firstFrame) {
    firstFrame = false;
    requestAnimationFrame(() => {
      document.body.classList.remove('is-loading');
      document.body.classList.add('is-ready');
    });
  }
}

resize();
pelican.update(0, 1 / 60);
updateCamera(0, 1 / 60, pelican.rider.position, true);
try {
  renderer.compile(scene, camera);
} catch (error) {
  console.warn('Shader precompile skipped:', error);
}
animate();
