// main.js — Surfing Pelican.
// An animated, non-interactive short film: one pelican, one longboard, one
// swell. Everything below is generated in code; nothing is fetched at runtime.

import * as THREE from 'three';
import { createSharedUniforms, PALETTE, SUN_DIR } from './src/uniforms.js';
import { createSky } from './src/sky.js';
import { createOcean } from './src/ocean.js';
import { createRider } from './src/pelican.js';
import { createSpray, createRipples } from './src/spray.js';
import { createFish } from './src/fish.js';
import { createIsland, createBirds } from './src/extras.js';
import { createCameraRig } from './src/cameraRig.js';
import { createHud, showFallback } from './src/hud.js';
import { waveHeight } from './src/waves.js';

const stage = document.getElementById('stage');

let renderer;
try {
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance',
    // keep the last frame around: the page is often captured as a still
    // (sandboxed iframe previews, screen recording) and would otherwise
    // sometimes be grabbed between two frames, i.e. black
    preserveDrawingBuffer: true,
  });
} catch (err) {
  showFallback('This film needs WebGL, which this browser will not give us.');
  throw err;
}

const MAX_DPR = 2;
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_DPR));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.94;
stage.appendChild(renderer.domElement);

// ---------------------------------------------------------------------------
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(new THREE.Color(PALETTE.horizon), 90, 640);

const camera = new THREE.PerspectiveCamera(
  41,
  window.innerWidth / Math.max(1, window.innerHeight),
  0.1,
  6000,
);
camera.position.set(-25, 8.5, -29);

// light: low sun behind the bird, cool fill from the camera side
const sunLight = new THREE.DirectionalLight(0xffd9a8, 2.5);
sunLight.position.copy(SUN_DIR).multiplyScalar(120);
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xa9cbe4, 0.9);
fillLight.position.set(28, 16, -46);
scene.add(fillLight);

scene.add(new THREE.HemisphereLight(0x9dc6e8, 0x0b3a46, 0.85));

// ---------------------------------------------------------------------------
const shared = createSharedUniforms();
const sky = createSky(shared);
scene.add(sky.mesh);

const ocean = createOcean(shared);
scene.add(ocean.mesh);

const rider = createRider();
scene.add(rider.root);

const spray = createSpray(rider.root, 400);
const ripples = createRipples(scene);

const fish = createFish(rider.root);
const island = createIsland();
scene.add(island);
const birds = createBirds();
scene.add(birds.group);

const rig = createCameraRig(camera);
const hud = createHud(stage, rig.total);

// ---------------------------------------------------------------------------
const riderView = {
  position3: new THREE.Vector3(),
  bob: 0,
  bank: 0,
};

const mouthWorld = new THREE.Vector3();
const localTmp = new THREE.Vector3();
const worldTmp = new THREE.Vector3();
const wakeDir = new THREE.Vector3(0.42, 0.9, 0);

let sprayTimer = 0;
let t0 = -1;
let lastNow = 0;
let lastFov = camera.fov;
// "?t=42" starts the film at 42s, handy for reviewing a particular set-up
const startAt = Math.max(
  0,
  Number(new URLSearchParams(window.location.search).get('t')) || 0,
);
const holdAt = Number(new URLSearchParams(window.location.search).get('hold')) || 0; // TEMP
let frames = 0;
let frameSum = 0;
let qualityLevel = 0; // 0 = full, 1 = reduced
const DPR_STEPS = [Math.min(window.devicePixelRatio || 1, MAX_DPR), 1, 0.75];

function onResize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(DPR_STEPS[qualityLevel]);
  renderer.setSize(w, h);
  spray.setPixelScale(pixelsPerWorld());
}

/** drawing-buffer pixels per world unit at a distance of one unit */
function pixelsPerWorld() {
  return (
    (0.5 * renderer.domElement.height) /
    Math.tan(THREE.MathUtils.degToRad(camera.fov) * 0.5)
  );
}
window.addEventListener('resize', onResize);

function sprayForMotion(steepness) {
  // the board kicks up more water the steeper the wave it is climbing
  const n = 1 + Math.round(steepness * 3);
  spray.emit(
    n,
    -1.15,
    0.16,
    0,
    wakeDir,
    0.42,
    { up: 1.0, speed: 2.4 + steepness * 2.4, size: 0.035 + steepness * 0.02, life: 1.1 },
  );
}

const fishCtx = {
  mouthWorld,
  setBeakOpen: (v) => rider.setBeakOpen(v),
  onLaunch: () => {
    // a fish breaking the surface throws a little fountain of its own
    rider.root.updateMatrixWorld(true);
    const local = localTmp.copy(fish.group.position);
    local.y = 0.05;
    spray.emit(
      26,
      local.x,
      local.y,
      local.z,
      new THREE.Vector3(0.15, 1, -0.2),
      0.85,
      { up: 1.0, speed: 4.2, size: 0.05, life: 1.2 },
    );
    const w = fish.group.getWorldPosition(worldTmp);
    ripples.spawn(w.x, 0, w.z, 2.2, 1.2);
  },
  onCatch: (world) => {
    rider.swallow();
    rider.root.updateMatrixWorld(true);
    const local = rider.root.worldToLocal(localTmp.copy(world));
    spray.emit(
      16,
      local.x,
      local.y - 0.05,
      local.z,
      new THREE.Vector3(0.2, 0.8, -0.3),
      1.0,
      { up: 1.0, speed: 2.2, size: 0.04, life: 0.9 },
    );
    ripples.spawn(world.x, 0, world.z, 2.8, 1.5);
  },
};

// ---------------------------------------------------------------------------
function frame(now) {
  requestAnimationFrame(frame);

  if (t0 < 0) {
    t0 = now;
    lastNow = now;
  }
  // the film clock is "seconds since we started" (plus ?t=), so the rAF
  // timestamp rather than a frame counter decides where the story is
  const rawTime = startAt + (now - t0) / 1000;
  const filmTime = holdAt > 0 ? Math.min(rawTime, holdAt) : rawTime; // TEMP
  let dt = (now - lastNow) / 1000;
  lastNow = now;
  if (dt <= 0) dt = 1 / 60;
  dt = Math.min(dt, 0.1);

  shared.uTime.value = filmTime;

  const state = rider.update(dt, filmTime);
  rider.root.updateMatrixWorld(true);
  rider.mouthWorld(mouthWorld);

  // the ocean needs to know where the surfer is (foam collar + wake)
  ocean.setSurfer(state.x, state.z);

  // continuous spray off the tail of the board
  sprayTimer -= dt;
  if (sprayTimer <= 0) {
    sprayTimer = 0.055;
    sprayForMotion(Math.min(1, Math.abs(state.normal.x) * 1.6 + (state.fwd.y > 0 ? 0.25 : 0)));
  }

  fish.update(dt, filmTime, fishCtx);
  island.update(filmTime);
  birds.update(filmTime);
  ripples.update(dt, filmTime, waveHeight);

  riderView.position3.copy(rider.root.position);
  riderView.bob = rider.rig.position.y - 0.105;
  riderView.bank = -rider.rig.rotation.x;
  rig.update(filmTime, dt, riderView);
  sky.update(camera);

  // particle screen size follows the (slowly changing) lens
  if (Math.abs(camera.fov - lastFov) > 0.02) {
    lastFov = camera.fov;
    spray.setPixelScale(pixelsPerWorld());
  }

  hud.update(filmTime);

  renderer.render(scene, camera);

  // ---- gentle adaptive resolution (keeps the iframe happy on slow GPUs) ----
  frameSum += dt;
  frames++;
  if (frames >= 80) {
    const avg = frameSum / frames;
    frames = 0;
    frameSum = 0;
    if (avg > 0.024 && qualityLevel < DPR_STEPS.length - 1) {
      qualityLevel++;
      onResize();
    } else if (avg < 0.013 && qualityLevel > 0) {
      qualityLevel--;
      onResize();
    }
  }
}

onResize();
requestAnimationFrame(frame);

// expose a little state for debugging in the console
window.__pelican = { scene, camera, renderer, ocean, rider };
