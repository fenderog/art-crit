import * as THREE from 'three';
import { createSurfer } from './pelican.js';
import { createOcean, waveHeight } from './ocean.js';
import { createSky } from './sky.js';

// Animated, non-interactive surfing pelican. Fixed camera with a gentle
// drift; no controls, no input handling, no storage, no network.

const container = document.getElementById('scene');

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd9eef2, 38, 135);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 600);
const camBase = new THREE.Vector3(8.4, 3.7, 10.6);
const camTarget = new THREE.Vector3(0.3, 1.7, -1.2);
camera.position.copy(camBase);
camera.lookAt(camTarget);

scene.add(new THREE.HemisphereLight(0xcfe8ff, 0x9c8f7a, 0.85));

const sun = new THREE.DirectionalLight(0xfff1d6, 2.4);
sun.position.set(10, 14, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -15;
sun.shadow.camera.right = 15;
sun.shadow.camera.top = 15;
sun.shadow.camera.bottom = -15;
sun.shadow.camera.near = 2;
sun.shadow.camera.far = 45;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.03;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xbfe0ff, 0.5);
fill.position.set(-8, 4, -6);
scene.add(fill);

const sky = createSky(scene);
const ocean = createOcean(scene);
const surfer = createSurfer();
scene.add(surfer.group);

function frame(t, dt) {
  sky.update(t, dt);
  ocean.update(t);
  surfer.update(t, waveHeight);
  camera.position.set(
    camBase.x + Math.sin(t * 0.16) * 0.3,
    camBase.y + Math.sin(t * 0.23 + 1) * 0.12,
    camBase.z,
  );
  camera.lookAt(camTarget);
  renderer.render(scene, camera);
}

const reduceMotion =
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  if (reduceMotion) frame(1.4, 0); // re-render the still composition
}
window.addEventListener('resize', onResize);

if (reduceMotion) {
  frame(1.4, 0);
} else {
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.05);
    frame(clock.elapsedTime, dt);
  });
}
