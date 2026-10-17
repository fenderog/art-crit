// Surfing Pelican — an endless, non-interactive summer glide.
//
// Everything is generated in code: the swell, the sky, the pelican, the board,
// the spray. No textures, no models, no network.

import * as THREE from 'three';
import { PALETTE, SUN_DIR, FOG_DENSITY } from './js/palette.js';
import { createOcean } from './js/ocean.js';
import { createSky } from './js/sky.js';
import { createRider } from './js/pelican.js';
import { createSpray } from './js/spray.js';
import { createFlock } from './js/flock.js';
import { createIslands } from './js/islands.js';
import { createContactShadow } from './js/contact.js';
import { createCameraRig } from './js/camera.js';

const canvas = document.getElementById('scene');
const fadeEl = document.getElementById('fade');

// ---------------------------------------------------------------------------
// renderer / scene / camera
// ---------------------------------------------------------------------------

let renderer;
try {
  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    powerPreference: 'high-performance',
  });
} catch (err) {
  fadeEl.style.opacity = '1';
  fadeEl.style.background = '#08222f';
  fadeEl.innerHTML =
    '<div style="padding:12vh 8vw;color:#eaf6ff;font:16px/1.5 system-ui,sans-serif">' +
    'This page needs WebGL, which this browser would not give us.<br>' +
    String(err && err.message ? err.message : err) +
    '</div>';
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
renderer.setSize(window.innerWidth, window.innerHeight, false);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(new THREE.Color(PALETTE.haze), FOG_DENSITY);

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / Math.max(1, window.innerHeight),
  1,
  60000,
);
scene.add(camera);

// ---------------------------------------------------------------------------
// lights
// ---------------------------------------------------------------------------

const sunDir = new THREE.Vector3(SUN_DIR.x, SUN_DIR.y, SUN_DIR.z).normalize();

const sun = new THREE.DirectionalLight(new THREE.Color(PALETTE.sun), 3.4);
scene.add(sun);
scene.add(sun.target);

// sky above, sunlit water below, plus a warm bounce so whites stay warm
const skyLight = new THREE.HemisphereLight(
  new THREE.Color('#a9cfe6'),
  new THREE.Color('#1e6b7d'),
  0.9,
);
scene.add(skyLight);

const fill = new THREE.DirectionalLight(new THREE.Color('#ffd9ae'), 1.0);
scene.add(fill);
scene.add(fill.target);

// ---------------------------------------------------------------------------
// the ensemble
// ---------------------------------------------------------------------------

const sky = createSky(camera);
const ocean = createOcean(scene);
const rider = createRider(scene);
const spray = createSpray(scene);
const flock = createFlock(scene);
const islands = createIslands(scene);
const contact = createContactShadow(scene);
const rig = createCameraRig(camera);

const fillOffset = new THREE.Vector3();

function placeLights() {
  const p = rider.state.position;
  sun.position.copy(p).addScaledVector(sunDir, 120);
  sun.target.position.copy(p);
  fillOffset.set(-sunDir.x * 0.6 + 0.4, 0.55, -sunDir.z * 0.6).normalize();
  fill.position.copy(p).addScaledVector(fillOffset, 90);
  fill.target.position.copy(p);
}

// ---------------------------------------------------------------------------
// frame loop
// ---------------------------------------------------------------------------

let t = 0; // animation time (seconds)
let fade = 1; // dip-to-black level
let lastFade = -1;
let lastFrame = performance.now();

function updateFade(t, dt) {
  // open from black, then dip to black across each cut
  let target;
  if (t < 1.4) {
    target = 1 - t / 1.4;
  } else {
    const st = rig.shotTime;
    const dur = rig.shotDuration;
    const lead = 0.55;
    target = st > dur - lead ? Math.min(1, (st - (dur - lead)) / lead) : 0;
  }
  fade += (target - fade) * (1 - Math.exp(-9 * dt));
  if (Math.abs(fade - lastFade) > 0.004) {
    lastFade = fade;
    fadeEl.style.opacity = fade.toFixed(3);
  }
}

function frame() {
  const now = performance.now();
  const dt = Math.min(0.05, (now - lastFrame) / 1000);
  lastFrame = now;
  t += dt;

  rider.update(t);
  rig.update(dt, rider);
  camera.updateMatrixWorld();

  const rp = rider.state.position;
  ocean.mesh.position.set(rp.x, 0, rp.z);
  ocean.uniforms.uTime.value = t;
  ocean.uniforms.uRider.value.set(rp.x, rp.z);
  ocean.uniforms.uRiderFwd.value.set(rider.state.forward.x, rider.state.forward.z);

  placeLights();
  sky.update(t);
  contact.update(rider);
  islands.update(rider);
  flock.update(t, rider);
  spray.update(t, dt, rider);

  updateFade(t, dt);
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(frame);

// ---------------------------------------------------------------------------
// resize
// ---------------------------------------------------------------------------

function resize() {
  const w = Math.max(1, window.innerWidth);
  const h = Math.max(1, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

window.addEventListener('resize', resize);
resize();

// expose a little state for debugging in the console
window.__pelican = {
  get t() {
    return t;
  },
  rider,
  rig,
  ocean,
  scene,
  /** jump the animation to a point on the timeline and render one frame */
  seek(sec) {
    t = sec;
    fade = 0;
    lastFade = -1;
    rig.seek(sec);
    frame();
  },
};
