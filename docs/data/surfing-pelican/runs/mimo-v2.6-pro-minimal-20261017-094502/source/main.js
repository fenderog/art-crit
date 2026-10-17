import * as THREE from 'three';
import { createOcean } from './ocean.js';
import { createSky } from './sky.js';
import { createSurfer } from './pelican.js';
import { Spray } from './spray.js';
import { waveHeight } from './waves.js';

const palette = {
  skyTop: 0x2d63b6,
  skyHorizon: 0xffd0a0,
  sunColor: 0xffeec4,
  oceanDeep: 0x0a3c64,
  oceanShallow: 0x2e90ac,
  foam: 0xeef6f7,
};

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: 'high-performance',
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  42,
  window.innerWidth / window.innerHeight,
  0.1,
  2000,
);

// ---------------- lighting ----------------
const sunDir = new THREE.Vector3(-0.5, 0.36, -0.79).normalize();

const sun = new THREE.DirectionalLight(0xffe7bd, 3.1);
sun.position.copy(sunDir).multiplyScalar(48);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 24;
sun.shadow.camera.far = 96;
sun.shadow.camera.left = -7.5;
sun.shadow.camera.right = 7.5;
sun.shadow.camera.top = 7.5;
sun.shadow.camera.bottom = -7.5;
sun.shadow.bias = -0.0012;
sun.shadow.normalBias = 0.022;
scene.add(sun, sun.target);

const fill = new THREE.DirectionalLight(0xa9cdf2, 1.15);
fill.position.set(9, 6, 18);
scene.add(fill);

const hemi = new THREE.HemisphereLight(0xbcd9f7, 0x1c5875, 1.35);
scene.add(hemi);

// ---------------- world ----------------
const sky = createSky({ palette, sunDir });
scene.add(sky.group);

const ocean = createOcean({ palette, sunDir });
scene.add(ocean.mesh);

const surfer = createSurfer();
scene.add(surfer.root);

const spray = new Spray(560);
scene.add(spray.points);

// ---------------- camera choreography ----------------
const camBase = new THREE.Vector3(0, 4.5, 11.6);
const camTarget = new THREE.Vector3(0, 2.7, 0);
const lookTarget = new THREE.Vector3();
const camOffset = new THREE.Vector3(0, 1.35, 0);

function updateCamera(t) {
  camera.position.set(
    camBase.x + Math.sin(t * 0.07) * 1.75 + Math.sin(t * 0.19) * 0.4,
    camBase.y + Math.sin(t * 0.13 + 1.1) * 0.45,
    camBase.z + Math.sin(t * 0.05) * 1.0,
  );
  lookTarget
    .copy(camTarget)
    .lerp(surfer.state.position, 0.3)
    .add(camOffset);
  lookTarget.x += Math.sin(t * 0.11) * 0.35;
  lookTarget.y += Math.sin(t * 0.21) * 0.12;
  camera.lookAt(lookTarget);
}

// ---------------- resize ----------------
function onResize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h);
  spray.setPixelScale(
    renderer.domElement.height / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)),
  );
}
window.addEventListener('resize', onResize);
onResize();

// ---------------- main loop ----------------
const clock = new THREE.Clock();
let t = 12.5; // start mid-scene so the wave is already running
// (debug hook, ignored in normal use)
const startParam = Number(new URLSearchParams(window.location.search).get('t'));
if (Number.isFinite(startParam) && startParam > 0) t = startParam;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 1 / 24);
  t += dt;

  surfer.update(t);
  sky.update(t);
  ocean.update(t, camera);
  updateCamera(t);

  const wake = surfer.getWakePoint();
  wake.y = waveHeight(wake.x, wake.z, t) + 0.06;
  spray.emitWake(wake, surfer.state.forward, dt, 1);
  spray.update(dt);

  renderer.render(scene, camera);
}

animate();