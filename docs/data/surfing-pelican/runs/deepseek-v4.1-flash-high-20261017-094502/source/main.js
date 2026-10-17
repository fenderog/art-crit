import * as THREE from 'three';
import { createEnvironment, createBirds } from './environment.js';
import { createOcean } from './ocean.js';
import { createPelican } from './pelican.js';
import { Spray } from './spray.js';
import { waveHeight, waveNormal } from './waves.js';

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
renderer.toneMappingExposure = 0.97;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe8f2, 110, 380);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  900,
);

const environment = createEnvironment(scene, renderer);
const birds = createBirds(scene, 7);
const ocean = createOcean();
scene.add(ocean.mesh);

const pelican = createPelican();
pelican.root.scale.setScalar(1.3);
scene.add(pelican.root);

const spray = new Spray(scene, 700);

// ---------------------------------------------------------------------------
// Animation state
// ---------------------------------------------------------------------------
const X_AXIS = new THREE.Vector3(1, 0, 0);
const forward = new THREE.Vector3();
const normal = new THREE.Vector3();
const zAxis = new THREE.Vector3();
const basis = new THREE.Matrix4();
const orientation = new THREE.Quaternion();
const roll = new THREE.Quaternion();
const flapQuat = new THREE.Quaternion();
const localZ = new THREE.Vector3(0, 0, 1);
const tailLocal = new THREE.Vector3();
const backDir = new THREE.Vector3();
const camDesired = new THREE.Vector3();
const camLook = new THREE.Vector3();
const lookTarget = new THREE.Vector3();

const SPEED = 6.2;
let px = 0;
let pz = 0;

camera.position.set(-9, 4.5, 6);
camLook.set(2, 1.5, 0);

pelican.wings.forEach((w, i) => {
  w.rate = 2.3 + i * 0.25;
  w.phase = i * 1.7;
});

const timer = new THREE.Timer();
timer.connect(document);

function frame() {
  timer.update();
  const dt = Math.min(timer.getDelta(), 0.05);
  const elapsed = timer.getElapsed();

  // ---- Ride path ----------------------------------------------------------
  px += SPEED * dt;
  pz = Math.sin(px * 0.035) * 2.8 + Math.sin(px * 0.011) * 1.4;

  const y = waveHeight(px, pz, elapsed) + 0.05;
  waveNormal(px, pz, elapsed, normal);

  // Forward is world +X projected onto the local tangent plane.
  forward.copy(X_AXIS).addScaledVector(normal, -X_AXIS.dot(normal)).normalize();
  zAxis.crossVectors(forward, normal).normalize();

  basis.makeBasis(forward, normal, zAxis);
  orientation.setFromRotationMatrix(basis);

  // Lean/roll around the direction of travel.
  roll.setFromAxisAngle(
    forward,
    Math.sin(elapsed * 0.7) * 0.11 + Math.sin(elapsed * 0.23) * 0.06,
  );
  orientation.premultiply(roll);

  pelican.root.position.set(px, y, pz);
  pelican.root.quaternion.copy(orientation);

  // ---- Rider body language ------------------------------------------------
  pelican.torso.position.y = Math.sin(elapsed * 2.1) * 0.035;
  pelican.torso.rotation.z = Math.sin(elapsed * 1.6) * 0.05;
  pelican.torso.rotation.x = Math.sin(elapsed * 1.15) * 0.04;
  pelican.headPivot.rotation.y = -0.5 + Math.sin(elapsed * 0.8) * 0.09;
  pelican.headPivot.rotation.z = -0.06 + Math.sin(elapsed * 1.3) * 0.03;

  for (const w of pelican.wings) {
    const flap = Math.sin(elapsed * w.rate + w.phase) * 0.16;
    flapQuat.setFromAxisAngle(localZ, flap * w.side);
    w.pivot.quaternion.copy(w.base).multiply(flapQuat);
  }

  // ---- Bow spray ----------------------------------------------------------
  pelican.root.updateMatrixWorld(true);
  tailLocal.set(-1.25, 0.12, 0);
  pelican.root.localToWorld(tailLocal);
  backDir.copy(forward).negate();
  spray.spawn(tailLocal, backDir, normal, zAxis, dt);
  spray.update(dt);

  // ---- Camera -------------------------------------------------------------
  camDesired
    .copy(pelican.root.position)
    .addScaledVector(forward, -5.6)
    .addScaledVector(normal, 2.4)
    .addScaledVector(zAxis, 4.4);
  camDesired.x += Math.sin(elapsed * 0.35) * 0.9;
  camDesired.y += Math.sin(elapsed * 0.5) * 0.4;

  camera.position.lerp(camDesired, 1 - Math.exp(-dt * 2.2));

  lookTarget
    .copy(pelican.root.position)
    .addScaledVector(forward, 2.6)
    .addScaledVector(normal, 1.5);
  camLook.lerp(lookTarget, 1 - Math.exp(-dt * 3.0));
  camera.lookAt(camLook);

  // ---- World --------------------------------------------------------------
  ocean.update(elapsed, camera.position);
  environment.update(dt);
  birds.update(elapsed);

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(frame);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
