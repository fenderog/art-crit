import * as THREE from 'three';
import { buildSurfer } from './pelican.js';
import { createOcean, waveHeight } from './ocean.js';
import {
  createSkyDome,
  createLights,
  createClouds,
  createDistantBirds,
  createSpray,
  createFoamFlecks,
  createWake,
  createIsland,
} from './world.js';

// Renderer / scene / camera. Fixed cinematic camera — the piece is
// non-interactive; the only listener is window resize.
const container = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe8f2, 28, 110);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 500);
const camBase = new THREE.Vector3(2.4, 3.2, 8.8);

const sunDir = new THREE.Vector3(0.55, 0.38, 0.35).normalize();
scene.add(createSkyDome(sunDir));
scene.add(createLights(sunDir));
scene.add(createIsland());

const clouds = createClouds();
scene.add(clouds.group);
const birds = createDistantBirds();
scene.add(birds.group);
const ocean = createOcean();
scene.add(ocean.mesh);
const foam = createFoamFlecks();
scene.add(foam.points);
const spray = createSpray();
scene.add(spray.points);
const wake = createWake();
scene.add(wake.mesh);
const surfer = buildSurfer();
scene.add(surfer.group);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Local wave slope via finite differences, for pitch and roll.
function slopeAt(x, z, t) {
  const e = 0.35;
  return {
    dx: (waveHeight(x + e, z, t) - waveHeight(x - e, z, t)) / (2 * e),
    dz: (waveHeight(x, z + e, t) - waveHeight(x, z - e, t)) / (2 * e),
  };
}

const clock = new THREE.Clock();
const lookTarget = new THREE.Vector3();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  ocean.update(t);
  clouds.update(dt);
  birds.update(t);
  foam.update(t);

  // Surfer drifts gently on the swell, pitching and rolling with it.
  const px = Math.sin(t * 0.24) * 1.4;
  const pz = Math.sin(t * 0.17 + 1.0) * 0.9;
  const py = waveHeight(px, pz, t);
  const { dx, dz } = slopeAt(px, pz, t);
  const yaw = Math.sin(t * 0.3) * 0.22;
  const pitch = Math.atan(dx) * 0.9;
  const roll = -Math.atan(dz) * 0.9;
  surfer.group.position.set(px, py + 0.1, pz);
  surfer.group.rotation.set(
    roll + Math.sin(t * 1.1) * 0.02,
    yaw,
    pitch + Math.sin(t * 0.9) * 0.015,
  );
  surfer.update(t, roll);

  // Spray at the tail and the nose, wake trailing behind.
  const fx = Math.cos(yaw);
  const fz = -Math.sin(yaw);
  spray.emit(px - fx * 1.25, py + 0.12, pz - fz * 1.25, -fx * 1.8, 1.6, -fz * 1.8, 1.6, Math.max(1, Math.round(dt * 120)));
  spray.emit(px + fx * 1.3, py + 0.1, pz + fz * 1.3, fx * 0.6, 1.0, fz * 0.6, 1.0, Math.max(0, Math.round(dt * 30)));
  spray.update(dt);
  wake.update(px, pz, yaw, t);

  // Slow breathing camera that loosely follows the surfer.
  camera.position.set(
    camBase.x + Math.sin(t * 0.1) * 0.4 + px * 0.25,
    camBase.y + Math.sin(t * 0.13 + 2) * 0.18,
    camBase.z + Math.cos(t * 0.09) * 0.3,
  );
  lookTarget.set(px * 0.45, 1.0 + py * 0.25, pz * 0.45);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}

animate();
