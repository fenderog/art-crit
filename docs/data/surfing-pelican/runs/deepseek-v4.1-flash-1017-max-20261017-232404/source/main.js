import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

import { createSky, SUN_DIR } from './src/sky.js';
import { createOcean } from './src/ocean.js';
import { createSurfboard } from './src/surfboard.js';
import { createPelican } from './src/pelican.js';
import { createSpray } from './src/spray.js';
import { waveHeight, waveNormal, WAVE } from './src/waves.js';
import { makeGrainDataURL } from './src/utils.js';

/* -------------------------------------------------------------------------- */
/*  Renderer and scene                                                        */
/* -------------------------------------------------------------------------- */

const canvas = document.querySelector('#scene');
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  powerPreference: 'high-performance'
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.9;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x150f23);

const camera = new THREE.PerspectiveCamera(37, 1, 0.1, 700);
camera.position.set(-5.6, 3.15, 8.4);

/* -------------------------------------------------------------------------- */
/*  Environment lighting                                                      */
/* -------------------------------------------------------------------------- */

function createEnvironmentTexture(rendererInstance) {
  const canvasEl = document.createElement('canvas');
  canvasEl.width = 1024;
  canvasEl.height = 512;
  const ctx = canvasEl.getContext('2d');

  const grad = ctx.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0.0, '#24183d');
  grad.addColorStop(0.26, '#5e335a');
  grad.addColorStop(0.43, '#d46b6d');
  grad.addColorStop(0.5, '#ffc58b');
  grad.addColorStop(0.53, '#b56a66');
  grad.addColorStop(0.6, '#174d57');
  grad.addColorStop(1.0, '#04222b');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 1024, 512);

  const sun = ctx.createRadialGradient(690, 258, 2, 690, 258, 150);
  sun.addColorStop(0, 'rgba(255,250,224,1)');
  sun.addColorStop(0.04, 'rgba(255,231,173,0.98)');
  sun.addColorStop(0.18, 'rgba(255,172,103,0.42)');
  sun.addColorStop(1, 'rgba(255,128,91,0)');
  ctx.fillStyle = sun;
  ctx.beginPath();
  ctx.arc(690, 258, 150, 0, Math.PI * 2);
  ctx.fill();

  const texture = new THREE.CanvasTexture(canvasEl);
  texture.mapping = THREE.EquirectangularReflectionMapping;
  texture.colorSpace = THREE.SRGBColorSpace;

  const pmrem = new THREE.PMREMGenerator(rendererInstance);
  pmrem.compileEquirectangularShader();
  const envMap = pmrem.fromEquirectangular(texture).texture;
  envMap.name = 'golden-hour-environment';
  texture.dispose();
  pmrem.dispose();
  return envMap;
}

const environment = createEnvironmentTexture(renderer);
scene.environment = environment;
scene.environmentIntensity = 0.35;

/* -------------------------------------------------------------------------- */
/*  Lights                                                                    */
/* -------------------------------------------------------------------------- */

const hemisphere = new THREE.HemisphereLight(0xffc9a4, 0x092a34, 0.72);
scene.add(hemisphere);

const keyLight = new THREE.DirectionalLight(0xffc197, 2.15);
keyLight.position.set(-10, 13, 9);
keyLight.target.position.set(0, 1.2, 0);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.left = -6;
keyLight.shadow.camera.right = 6;
keyLight.shadow.camera.top = 7;
keyLight.shadow.camera.bottom = -5;
keyLight.shadow.camera.near = 1;
keyLight.shadow.camera.far = 40;
keyLight.shadow.bias = -0.0004;
keyLight.shadow.normalBias = 0.025;
scene.add(keyLight, keyLight.target);

const rimLight = new THREE.DirectionalLight(0xff8154, 1.55);
rimLight.position.copy(SUN_DIR).multiplyScalar(28);
rimLight.position.y += 5;
rimLight.target.position.set(0, 1.2, 0);
scene.add(rimLight, rimLight.target);

const fillLight = new THREE.DirectionalLight(0x81d4d8, 0.95);
fillLight.position.set(7, 4, 9);
fillLight.target.position.set(0, 1.2, 0);
scene.add(fillLight, fillLight.target);

/* -------------------------------------------------------------------------- */
/*  World                                                                     */
/* -------------------------------------------------------------------------- */

const sky = createSky(scene);
const ocean = createOcean(scene);

const boardRig = createSurfboard();
const boardGroup = boardRig.group;
scene.add(boardGroup);

const pelican = createPelican();
pelican.root.position.set(0, boardRig.deckY + 0.01, 0);
boardGroup.add(pelican.root);

const spray = createSpray(scene, boardGroup);

/* -------------------------------------------------------------------------- */
/*  Post processing                                                           */
/* -------------------------------------------------------------------------- */

const composer = new EffectComposer(renderer);
// 4x multisampled HDR buffers keep the fine feathers and horizon clean.
composer.renderTarget1.samples = 4;
composer.renderTarget2.samples = 4;

const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.32,
  0.42,
  0.92
);
composer.addPass(bloomPass);
composer.addPass(new OutputPass());

/* -------------------------------------------------------------------------- */
/*  Surfboard / camera motion                                                 */
/* -------------------------------------------------------------------------- */

const up = new THREE.Vector3(0, 1, 0);
const normal = new THREE.Vector3();
const tiltQuaternion = new THREE.Quaternion();
const yawQuaternion = new THREE.Quaternion();
const cameraTarget = new THREE.Vector3();
const cameraPosition = new THREE.Vector3();

const boardAnchor = new THREE.Vector3(0, 0, WAVE.boardZ);

function updateBoard(t) {
  boardAnchor.x = Math.sin(t * 0.19 + 0.7) * 0.32;
  const h = waveHeight(boardAnchor.x, boardAnchor.z, t);
  waveNormal(boardAnchor.x, boardAnchor.z, t, normal);

  boardGroup.position.set(boardAnchor.x, h + 0.035, boardAnchor.z);
  tiltQuaternion.setFromUnitVectors(up, normal);
  yawQuaternion.setFromAxisAngle(up, 0.17 + Math.sin(t * 0.31) * 0.055);
  boardGroup.quaternion.copy(tiltQuaternion).multiply(yawQuaternion);

  // A tiny extra side-to-side edge roll makes it feel hand-guided.
  boardGroup.rotateX(Math.sin(t * 0.9 + 0.4) * 0.028);
}

function updateCamera(t) {
  cameraPosition.set(
    -5.6 + Math.sin(t * 0.055 + 0.3) * 0.62,
    3.05 + Math.sin(t * 0.073 + 1.1) * 0.13,
    8.45 + Math.cos(t * 0.047 + 0.2) * 0.43
  );
  camera.position.copy(cameraPosition);

  cameraTarget.set(
    0.05 + boardGroup.position.x * 0.4 + Math.sin(t * 0.043 + 0.8) * 0.08,
    2.2 + Math.sin(t * 0.061 + 0.4) * 0.06,
    0.24
  );
  camera.lookAt(cameraTarget);
  camera.rotation.z += Math.sin(t * 0.032 + 0.2) * 0.0055 + 0.006;
}

/* -------------------------------------------------------------------------- */
/*  Resize & grain                                                            */
/* -------------------------------------------------------------------------- */

function onResize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 1.7);

  renderer.setPixelRatio(dpr);
  renderer.setSize(w, h, false);
  composer.setPixelRatio(dpr);
  composer.setSize(w, h);

  camera.aspect = w / h;
  camera.updateProjectionMatrix();

  bloomPass.resolution.set(w * dpr, h * dpr);
}

window.addEventListener('resize', onResize);
onResize();

const grainEl = document.querySelector('#grain');
if (grainEl) grainEl.style.backgroundImage = `url(${makeGrainDataURL(180)})`;

/* -------------------------------------------------------------------------- */
/*  Animation loop                                                            */
/* -------------------------------------------------------------------------- */

const startTime = performance.now();
let elapsed = 0;
let firstFrame = true;

function animate() {
  const now = performance.now();
  const dt = Math.min((now - startTime) / 1000 - elapsed, 0.05);
  elapsed += Math.max(0, dt);
  const t = elapsed;

  updateBoard(t);
  pelican.update(t);
  boardGroup.updateMatrixWorld(true);

  sky.update(t);
  ocean.update(t, boardGroup.position);
  spray.update(t, dt);
  updateCamera(t);

  composer.render();

  if (firstFrame) {
    firstFrame = false;
    window.setTimeout(() => {
      document.body.classList.add('is-loaded');
      const loader = document.querySelector('#loader');
      if (loader) loader.setAttribute('aria-hidden', 'true');
    }, 420);
  }

  window.__world = { renderer, scene, camera, composer, bloomPass, ocean, boardGroup, pelican, sky, spray };
requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
