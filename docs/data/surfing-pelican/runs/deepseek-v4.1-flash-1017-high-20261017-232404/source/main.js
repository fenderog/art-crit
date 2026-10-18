import * as THREE from 'three';
import { createOcean } from './ocean.js';
import { createSky, SUN_DIR } from './sky.js';
import { createRider } from './pelican.js';
import { createSpray } from './particles.js';

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
renderer.toneMappingExposure = 0.95;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf3bf96);

const camera = new THREE.PerspectiveCamera(
  42,
  window.innerWidth / window.innerHeight,
  0.1,
  3000
);

// ---------------------------------------------------------------------------
// Light: a warm key from the camera side, a hot rim from the setting sun.
// ---------------------------------------------------------------------------

const keyLight = new THREE.DirectionalLight(0xffd7b4, 2.4);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.near = 0.5;
keyLight.shadow.camera.far = 40;
keyLight.shadow.camera.left = -6;
keyLight.shadow.camera.right = 6;
keyLight.shadow.camera.top = 7;
keyLight.shadow.camera.bottom = -5;
keyLight.shadow.bias = -0.0006;
keyLight.shadow.normalBias = 0.035;
scene.add(keyLight);
scene.add(keyLight.target);

const rimLight = new THREE.DirectionalLight(0xffb26e, 2.8);
scene.add(rimLight);
scene.add(rimLight.target);

const fillLight = new THREE.DirectionalLight(0x9fd6ff, 0.55);
fillLight.position.set(-8, 4, 6);
scene.add(fillLight);

const hemi = new THREE.HemisphereLight(0x9ed6ff, 0x16454f, 1.05);
scene.add(hemi);

scene.add(new THREE.AmbientLight(0xffe1c4, 0.14));

// ---------------------------------------------------------------------------
// World.
// ---------------------------------------------------------------------------

const ocean = createOcean();
ocean.uniforms.uSunDir.value.copy(SUN_DIR);
ocean.uniforms.uSkyZenith.value.set(0x1c3a68);
ocean.uniforms.uSkyHorizon.value.set(0xffbf88);
scene.add(ocean.mesh);

const sky = createSky();
scene.add(sky.group);

const rider = createRider();
scene.add(rider.group);

const spray = createSpray();
scene.add(spray.points);


// ---------------------------------------------------------------------------
// Camera path: a slow, breathing orbit just ahead of the board.
// ---------------------------------------------------------------------------

const orbitAngle = (time) => 0.55 + Math.sin(time * 0.052) * 0.16;
const cameraRadius = (time) => 8.6 + Math.sin(time * 0.031) * 0.4;
const cameraHeight = (time) => 2.62 + Math.sin(time * 0.068) * 0.14;

const camOffset = new THREE.Vector3();
const desiredCam = new THREE.Vector3();
const lookTarget = new THREE.Vector3();
const desiredLook = new THREE.Vector3();
const axisY = new THREE.Vector3(0, 1, 0);

function placeCamera(time, dt, snap = false) {
  const a = orbitAngle(time);
  const fit = Math.max(1, 0.72 / camera.aspect);
  const r = cameraRadius(time) * fit;
  camOffset.set(Math.sin(a) * r, 0, Math.cos(a) * r);
  camOffset.applyAxisAngle(axisY, rider.yaw);

  desiredCam.copy(rider.position).add(camOffset);
  desiredCam.y = rider.group.position.y + cameraHeight(time) * (1 + (fit - 1) * 0.45);

  desiredLook.copy(rider.position);
  desiredLook.y = rider.group.position.y + 1.42;
  desiredLook.x += rider.forward.x * 0.15;
  desiredLook.z += rider.forward.z * 0.15;

  if (snap) {
    camera.position.copy(desiredCam);
    lookTarget.copy(desiredLook);
  } else {
    camera.position.lerp(desiredCam, 1 - Math.exp(-dt * 2.6));
    lookTarget.lerp(desiredLook, 1 - Math.exp(-dt * 4.2));
  }
  camera.lookAt(lookTarget);
}

// ---------------------------------------------------------------------------
// Animation loop.
// ---------------------------------------------------------------------------

let time = 0;
let lastFrame = performance.now();
let started = false;

placeCamera(0, 0, true);

function animate(now) {
  requestAnimationFrame(animate);

  const dt = Math.min((now - lastFrame) / 1000, 0.05);
  lastFrame = now;
  time += dt;

  rider.update(time, dt);
  placeCamera(time, dt);

  ocean.update(time, rider.position);
  sky.update(time, camera);

  // Keep the shadow rig travelling with the bird.
  keyLight.position.set(
    rider.position.x + 7.5,
    rider.group.position.y + 11,
    rider.position.z + 8
  );
  keyLight.target.position.set(rider.position.x, rider.group.position.y + 0.8, rider.position.z);
  keyLight.target.updateMatrixWorld();

  rimLight.position.set(
    rider.position.x + SUN_DIR.x * 30,
    rider.group.position.y + SUN_DIR.y * 30 + 4,
    rider.position.z + SUN_DIR.z * 30
  );
  rimLight.target.position.set(rider.position.x, rider.group.position.y + 1, rider.position.z);
  rimLight.target.updateMatrixWorld();

  spray.update(dt, time, rider);

  renderer.render(scene, camera);

  if (!started) {
    started = true;
    const fade = document.getElementById('fade');
    if (fade) {
      requestAnimationFrame(() => {
        fade.style.opacity = '0';
      });
    }
  }
}

requestAnimationFrame(animate);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
});
