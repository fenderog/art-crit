import * as THREE from 'three';
import { createOcean } from './ocean.js';
import { createSky } from './sky.js';
import { createPelican } from './pelican.js';
import { createSpray } from './spray.js';

/* ------------------------------------------------------------------ setup */
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
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
const FOG_COLOR = new THREE.Color(0xbfdfee);
scene.fog = new THREE.Fog(FOG_COLOR, 45, 195);
scene.background = FOG_COLOR.clone();

const camera = new THREE.PerspectiveCamera(
  52,
  window.innerWidth / window.innerHeight,
  0.1,
  2200
);
camera.position.set(30, 8, 10);

/* ------------------------------------------------------------------ light */
const sunDirection = new THREE.Vector3(0.45, 0.42, 0.78).normalize();

const hemi = new THREE.HemisphereLight(0xd8ecff, 0x14506e, 1.05);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff0d2, 2.4);
sun.position.copy(sunDirection).multiplyScalar(120);
scene.add(sun);

const fill = new THREE.DirectionalLight(0x9fd0ff, 0.5);
fill.position.set(-0.6, 0.4, -0.5).multiplyScalar(80);
scene.add(fill);

scene.add(new THREE.AmbientLight(0x3a5a72, 0.35));

/* ------------------------------------------------------------------ world */
const ocean = createOcean();
scene.add(ocean.mesh);

const sky = createSky(sunDirection);
scene.add(sky.root);

const pelican = createPelican();
const surfer = pelican.group;
scene.add(surfer);

const spray = createSpray(900);
scene.add(spray.points);

// Soft foam disc that slides along the surface beneath the board.
function makeFoamTexture() {
  const size = 256;
  const c = document.createElement('canvas');
  c.width = size;
  c.height = size;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0.0, 'rgba(255,255,255,0.85)');
  g.addColorStop(0.35, 'rgba(235,250,255,0.45)');
  g.addColorStop(0.7, 'rgba(210,240,255,0.12)');
  g.addColorStop(1.0, 'rgba(200,235,255,0.0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const foam = new THREE.Mesh(
  new THREE.PlaneGeometry(9, 9),
  new THREE.MeshBasicMaterial({
    map: makeFoamTexture(),
    transparent: true,
    depthWrite: false,
    opacity: 0.8,
    color: 0xffffff,
  })
);
foam.rotation.x = -Math.PI / 2;
foam.renderOrder = 1;
scene.add(foam);

/* -------------------------------------------------------------- animation */
const clock = new THREE.Clock();
const PATH_RADIUS = 24;
const ANGULAR_SPEED = 0.2;
const BANK = 0.34;

const forward = new THREE.Vector3();
const waveN = new THREE.Vector3();
const zAxis = new THREE.Vector3();
const yAxis = new THREE.Vector3();
const basis = new THREE.Matrix4();
const lookTarget = new THREE.Vector3(0, 2, 0);
const camGoal = new THREE.Vector3();
const desiredLook = new THREE.Vector3();
const spawnPos = new THREE.Vector3();
const spawnVel = new THREE.Vector3();
const tmp = new THREE.Vector3();

function emitSpray(dt) {
  const rate = 150;
  let n = rate * dt;
  let count = Math.floor(n);
  if (Math.random() < n - count) count++;

  const tail = new THREE.Vector3(-2.0, -0.05, 0).applyMatrix4(surfer.matrixWorld);
  const back = tmp.copy(forward).multiplyScalar(-1);

  for (let i = 0; i < count; i++) {
    const side = Math.random() < 0.5 ? 1 : -1;
    spawnPos.copy(tail);
    spawnPos.x += (Math.random() - 0.5) * 0.4;
    spawnPos.z += (Math.random() - 0.5) * 0.4;
    spawnPos.y += 0.05;

    spawnVel
      .copy(back)
      .multiplyScalar(1.4 + Math.random() * 1.8)
      .addScaledVector(zAxis, side * (0.9 + Math.random() * 1.6))
      .addScaledVector(yAxis, 1.6 + Math.random() * 2.2);
    spawnVel.x += (Math.random() - 0.5) * 0.6;
    spawnVel.z += (Math.random() - 0.5) * 0.6;

    spray.spawn(
      spawnPos,
      spawnVel,
      0.08 + Math.random() * 0.16,
      0.7 + Math.random() * 0.9
    );
  }
}

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Path: a large carving circle on the open water.
  const angle = t * ANGULAR_SPEED;
  const px = Math.cos(angle) * PATH_RADIUS;
  const pz = Math.sin(angle) * PATH_RADIUS;

  forward.set(-Math.sin(angle), 0, Math.cos(angle));

  ocean.waveNormal(waveN, px, pz, t);
  waveN.applyAxisAngle(forward, BANK).normalize();

  const surfaceY = ocean.waveHeight(px, pz, t);

  zAxis.crossVectors(forward, waveN).normalize();
  yAxis.crossVectors(zAxis, forward).normalize();
  basis.makeBasis(forward, yAxis, zAxis);
  surfer.quaternion.setFromRotationMatrix(basis);
  surfer.position.set(px, surfaceY + 0.14, pz);
  surfer.updateMatrixWorld();

  pelican.update(t);
  ocean.update(t);
  sky.update(dt);

  // Foam disc sits just off the water under the board.
  foam.position.set(px, surfaceY + 0.04, pz);
  const foamPulse = 1 + 0.1 * Math.sin(t * 3.0);
  foam.scale.set(foamPulse, foamPulse * 1.35, 1);
  foam.rotation.z = angle + Math.PI / 2;
  foam.material.opacity = 0.55 + 0.15 * Math.sin(t * 2.3);

  emitSpray(dt);
  spray.update(dt);

  // Cinematic follow camera.
  const sway = Math.sin(t * 0.6) * 0.8;
  camGoal
    .copy(surfer.position)
    .addScaledVector(forward, -10.5)
    .addScaledVector(yAxis, 4.6 + Math.sin(t * 0.9) * 0.35)
    .addScaledVector(zAxis, -3.6 + sway);
  camera.position.lerp(camGoal, 1 - Math.exp(-dt * 2.6));

  desiredLook
    .copy(surfer.position)
    .addScaledVector(forward, 3.4)
    .addScaledVector(yAxis, 1.5);
  lookTarget.lerp(desiredLook, 1 - Math.exp(-dt * 3.2));
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
