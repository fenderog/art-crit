// Entry point: renderer, lights, world assembly and the animation loop.

import * as THREE from 'three';
import { createOcean } from './ocean.js';
import { createSky } from './sky.js';
import { createSurfer } from './surfer.js';
import { createSpray } from './spray.js';

/* ------------------------------------------------------------------ */
/* renderer                                                            */
/* ------------------------------------------------------------------ */

const container = document.getElementById('app');

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 2600);

const FOG_COLOR = new THREE.Color(0xe2e2da);
const FOG_DENSITY = 0.0058;
scene.fog = new THREE.FogExp2(FOG_COLOR.getHex(), FOG_DENSITY);

/* ------------------------------------------------------------------ */
/* light                                                               */
/* ------------------------------------------------------------------ */

const sunDir = new THREE.Vector3(0.42, 0.27, -0.86).normalize();

const sunLight = new THREE.DirectionalLight(0xffe2b8, 3.6);
sunLight.position.copy(sunDir).multiplyScalar(160);
scene.add(sunLight);

const hemi = new THREE.HemisphereLight(0xffe3c6, 0x276175, 1.4);
scene.add(hemi);

// cool bounce from the water, keeps the shadow side alive
const bounce = new THREE.DirectionalLight(0x6fc7d8, 0.55);
bounce.position.set(-0.5, -0.25, 0.8).multiplyScalar(80);
scene.add(bounce);

/* ------------------------------------------------------------------ */
/* world                                                               */
/* ------------------------------------------------------------------ */

const ocean = createOcean({ sunDir, fogColor: FOG_COLOR, fogDensity: FOG_DENSITY });
scene.add(ocean.mesh);

const sky = createSky({ sunDir });
scene.add(sky.group);

const surfer = createSurfer();
scene.add(surfer.root);

const spray = createSpray({ max: 1200 });
scene.add(spray.points);

/* ------------------------------------------------------------------ */
/* resize                                                              */
/* ------------------------------------------------------------------ */

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);

  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(ratio);
  renderer.setSize(w, h);
  spray.setPixelRatio(ratio);
}
window.addEventListener('resize', resize);

/* ------------------------------------------------------------------ */
/* spray choreography                                                  */
/* ------------------------------------------------------------------ */

const mistAcc = { value: 0 };
const washAcc = { value: 0 };
const p = new THREE.Vector3();
const v = new THREE.Vector3();

function emitMist(dt, state) {
  // steady plume torn off the tail and rails, thrown backwards relative to
  // the board (the swell travels towards -X, the board points +X)
  mistAcc.value += dt * 72;
  while (mistAcc.value >= 1) {
    mistAcc.value -= 1;
    surfer.boardPoint(-1.25 + Math.random() * 0.55, Math.random() * 0.12, (Math.random() - 0.5) * 0.8, p);
    v.set(-2.2 - Math.random() * 2.4, 0.6 + Math.random() * 2.0, (Math.random() - 0.5) * 1.7);
    spray.emit(p.x, p.y, p.z, v.x, v.y, v.z, 0.18 + Math.random() * 0.26, 0.5, 0.5 + Math.random() * 0.6);
  }

  washAcc.value += dt * 46;
  while (washAcc.value >= 1) {
    washAcc.value -= 1;
    const side = Math.random() < 0.5 ? -1 : 1;
    surfer.boardPoint(-0.55 - Math.random() * 0.7, Math.random() * 0.05, side * (0.42 + Math.random() * 0.16), p);
    v.set(-1.6 - Math.random() * 1.4, 0.35 + Math.random() * 0.8, side * (0.3 + Math.random() * 0.9));
    spray.emit(p.x, p.y, p.z, v.x, v.y, v.z, 0.1 + Math.random() * 0.18, 0.55, 0.35 + Math.random() * 0.45);
  }

  // when the nose digs in on a steep face, fling a fan of spray forward
  const dig = Math.max(0, -state.pitchRate - 0.35);
  if (dig > 0) {
    const count = Math.min(9, Math.ceil(dig * 26 * dt * 60));
    for (let i = 0; i < count; i++) {
      surfer.boardPoint(1.35, 0.02 + Math.random() * 0.1, (Math.random() - 0.5) * 0.8, p);
      v.set(0.9 + Math.random() * 2.2, 1.8 + Math.random() * 3.0, (Math.random() - 0.5) * 2.6);
      spray.emit(p.x, p.y, p.z, v.x, v.y, v.z, 0.07 + Math.random() * 0.17, 0.6, 0.45 + Math.random() * 0.45);
    }
  }
}

/* ------------------------------------------------------------------ */
/* camera choreography                                                 */
/* ------------------------------------------------------------------ */

const focus = new THREE.Vector3();
const lookTarget = new THREE.Vector3();

function placeCamera(t, state) {
  focus.set(0, state.height + 1.35, 0);

  const angle = 0.5 - t * 0.06;
  const radius = 7.2 + Math.sin(t * 0.11) * 0.8 + Math.sin(t * 0.043) * 0.45;
  const height = state.height + 2.5 + Math.sin(t * 0.19) * 0.7;

  camera.position.set(
    focus.x + Math.sin(angle) * radius,
    height,
    focus.z + Math.cos(angle) * radius,
  );

  lookTarget.set(
    focus.x + Math.sin(angle + 1.5) * 0.55,
    focus.y + Math.sin(t * 0.7) * 0.06,
    focus.z + Math.cos(angle + 1.5) * 0.55,
  );
  camera.lookAt(lookTarget);

  // a touch of handheld dutch angle
  camera.rotateZ(Math.sin(t * 0.23) * 0.016 + Math.sin(t * 0.57) * 0.006);
}

/* ------------------------------------------------------------------ */
/* loop                                                                */
/* ------------------------------------------------------------------ */

let prevTime = performance.now() / 1000;
let elapsed = 0;

function animate() {
  const now = performance.now() / 1000;
  const dt = Math.min(now - prevTime, 0.05);
  prevTime = now;
  elapsed += dt;
  const t = elapsed;

  ocean.update(t);
  sky.update(t, dt);

  const state = surfer.update(t, dt);

  emitMist(dt, state);
  spray.update(dt);

  placeCamera(t, state);

  renderer.render(scene, camera);
}

// prime the camera before the first frame
placeCamera(0, surfer.update(0, 0));
renderer.setAnimationLoop(animate);

// handy for debugging in the console, harmless in the bundled page
window.__pelican = { scene, camera, renderer, surfer, ocean, sky, spray };
