/**
 * Surfing Pelican — an animated, non-interactive 3D vignette.
 *
 * A pelican rides the swell on a surfboard while the camera drifts slowly
 * around it. Everything is procedural: no models, no textures, no network.
 */
import * as THREE from "three";
import { createOcean } from "./src/ocean.js";
import { createSky } from "./src/sky.js";
import { createSurfRig } from "./src/pelican.js";
import { createSpray, createWake } from "./src/effects.js";

const SUN_DIRECTION = new THREE.Vector3(-0.52, 0.4, -0.72).normalize();

// ------------------------------------------------------------------ renderer
const container = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
container.appendChild(renderer.domElement);

// --------------------------------------------------------------------- scene
const scene = new THREE.Scene();
scene.fog = null;

const camera = new THREE.PerspectiveCamera(
  42,
  window.innerWidth / window.innerHeight,
  0.5,
  1200
);
camera.position.set(4, 6, 15);

// -------------------------------------------------------------------- lights
const sun = new THREE.DirectionalLight(0xfff1d6, 2.7);
sun.position.copy(SUN_DIRECTION).multiplyScalar(70);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 30;
sun.shadow.camera.far = 160;
sun.shadow.camera.left = -9;
sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9;
sun.shadow.camera.bottom = -9;
sun.shadow.bias = -0.0007;
sun.shadow.normalBias = 0.035;
scene.add(sun);
scene.add(sun.target);

const fill = new THREE.DirectionalLight(0x9dc6ee, 0.85);
fill.position.set(28, 18, 34);
scene.add(fill);

const hemi = new THREE.HemisphereLight(0xa9d8ff, 0x1c5c8c, 1.25);
scene.add(hemi);

// ------------------------------------------------------------------- content
const sky = createSky(scene, SUN_DIRECTION);
const ocean = createOcean(scene, SUN_DIRECTION);
const rig = createSurfRig(scene);
const spray = createSpray(scene);
const wake = createWake(rig.group);

// shadows only for the solid parts of the rig
rig.group.traverse((obj) => {
  if (obj.isMesh && obj.material && obj.material.transparent !== true) {
    obj.castShadow = true;
    obj.receiveShadow = true;
  }
});

// -------------------------------------------------------------------- camera
const lookTarget = new THREE.Vector3(0, 2.6, 0);

function updateCamera(t) {
  const azimuth = 0.72 + Math.sin(t * 0.052) * 0.32 + Math.sin(t * 0.021) * 0.13;
  const distance = 11.7 + Math.sin(t * 0.043) * 1.25;
  const height = 4.85 + Math.sin(t * 0.128) * 0.5 + Math.sin(t * 0.071) * 0.35;

  camera.position.set(
    Math.sin(azimuth) * distance,
    height + rig.group.position.y * 0.35,
    Math.cos(azimuth) * distance
  );

  lookTarget.set(
    Math.sin(t * 0.09) * 0.35,
    2.62 + rig.group.position.y * 0.55 + Math.sin(t * 0.11) * 0.22,
    0.25
  );
  camera.lookAt(lookTarget);
}

// -------------------------------------------------------------------- resize
function updatePixelScale() {
  const fovRad = THREE.MathUtils.degToRad(camera.fov);
  spray.setPixelScale(renderer.domElement.height / (2 * Math.tan(fovRad / 2)));
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  updatePixelScale();
}
window.addEventListener("resize", onResize);
updatePixelScale();

// ------------------------------------------------------------------- animate
const timer = new THREE.Timer();
timer.connect(document);
const nose = new THREE.Vector3();

renderer.setAnimationLoop(() => {
  timer.update();
  const dt = Math.min(timer.getDelta(), 0.05);
  const t = timer.getElapsed();

  ocean.update(t);
  sky.update(t, dt);
  rig.update(t, dt);
  wake.update(t);

  rig.nosePosition(nose);
  spray.update(dt, nose, rig.group.quaternion);

  updateCamera(t);
  renderer.render(scene, camera);
});