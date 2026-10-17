import * as THREE from 'three';
import { sampleWaves } from './waves.js';
import {
  createOcean,
  createSky,
  createSunGlow,
  createSpray,
  createContactShadow,
} from './ocean.js';
import { createPelican } from './pelican.js';
import { createBirds } from './birds.js';

// ---------------------------------------------------------------------------
// renderer / scene / camera
// ---------------------------------------------------------------------------

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 1600);

// ---------------------------------------------------------------------------
// palette + atmosphere
// ---------------------------------------------------------------------------

const sunDir = new THREE.Vector3(0.55, 0.36, -0.75).normalize();

const palette = {
  zenith: new THREE.Color(0x2d74c2),
  horizon: new THREE.Color(0xc7dfec),
  sunGlow: new THREE.Color(0xffd7a2),
  sunLight: new THREE.Color(0xfff3de),
  deep: new THREE.Color(0x09385a),
  shallow: new THREE.Color(0x2c8aa6),
};

scene.fog = new THREE.FogExp2(palette.horizon, 0.0062);

// ---------------------------------------------------------------------------
// world
// ---------------------------------------------------------------------------

const sky = createSky(sunDir, palette);
scene.add(sky);

const sunGlow = createSunGlow(sunDir);
scene.add(sunGlow);

const ocean = createOcean(sunDir, palette);
scene.add(ocean);

const birds = createBirds(7);
scene.add(birds.group);

// surf group: pelican + board + spray + contact shadow, riding the waves
const surfer = new THREE.Group();
scene.add(surfer);

const pelican = createPelican();
surfer.add(pelican.group);

const spray = createSpray(280);
surfer.add(spray);

const contactShadow = createContactShadow();
contactShadow.scale.set(1.62, 2.55, 1);
contactShadow.position.y = 0.035;
surfer.add(contactShadow);

// ---------------------------------------------------------------------------
// lights
// ---------------------------------------------------------------------------

const hemi = new THREE.HemisphereLight(0x9ed4f4, 0x2a6c8c, 0.95);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff1d8, 2.35);
sun.position.copy(sunDir).multiplyScalar(30);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 10;
sun.shadow.camera.far = 70;
sun.shadow.camera.left = -6.5;
sun.shadow.camera.right = 6.5;
sun.shadow.camera.top = 7.5;
sun.shadow.camera.bottom = -4.5;
sun.shadow.bias = -0.0008;
sun.shadow.normalBias = 0.022;
scene.add(sun);
scene.add(sun.target);

const fill = new THREE.DirectionalLight(0x8dc0e6, 0.75);
fill.position.set(-sunDir.x * 22, 12, -sunDir.z * 22);
scene.add(fill);

const bounce = new THREE.DirectionalLight(0x5fb3c9, 0.4);
bounce.position.set(0, -8, 8);
scene.add(bounce);

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------

const waveSample = { x: 0, y: 0, z: 0, nx: 0, ny: 1, nz: 0 };
const surfNormal = new THREE.Vector3(0, 1, 0);
const surfMatrix = new THREE.Matrix4();
const tangentF = new THREE.Vector3();
const tangentR = new THREE.Vector3();

/** Float the surfer on the wave field at parametric position (px, pz). */
function placeSurfer(px, pz, t) {
  sampleWaves(px, pz, t, waveSample);

  surfer.position.set(waveSample.x, waveSample.y, waveSample.z);

  surfNormal.set(waveSample.nx, waveSample.ny, waveSample.nz);
  // forward tangent = world +Z projected onto the wave surface
  tangentF.set(0, 0, 1).addScaledVector(surfNormal, -waveSample.nz).normalize();
  tangentR.crossVectors(surfNormal, tangentF).normalize();

  surfMatrix.makeBasis(tangentR, surfNormal, tangentF);
  surfer.quaternion.setFromRotationMatrix(surfMatrix);

  // small riding attitude: nose up, slight roll
  surfer.rotateX(-0.055 + Math.sin(t * 0.9) * 0.02);
  surfer.rotateZ(Math.sin(t * 0.63 + 1.2) * 0.045);
  surfer.rotateY(Math.sin(t * 0.37) * 0.08);
}

/** Local-space spray particles thrown up around the board. */
function updateSpray(t) {
  const seeds = spray.userData.seeds;
  const positions = spray.userData.positions;
  const count = spray.userData.count;
  for (let i = 0; i < count; i++) {
    const a = seeds[i * 4 + 0];
    const r = seeds[i * 4 + 1];
    const phase = seeds[i * 4 + 2];
    const speed = seeds[i * 4 + 3];

    const cyc = (t * 0.32 * speed + phase) % 1;
    const ang = a + t * 0.16 * Math.sign(Math.cos(a)) * speed;
    const spread = r * (0.5 + cyc * 1.9);

    positions[i * 3 + 0] = Math.cos(ang) * spread * 0.85;
    positions[i * 3 + 1] = 0.06 + Math.sin(cyc * Math.PI) * (0.42 + speed * 0.62) - cyc * 0.22;
    positions[i * 3 + 2] = Math.sin(ang) * spread * 2.1;
  }
  spray.geometry.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// animation
// ---------------------------------------------------------------------------

const startTime = performance.now();
const camTarget = new THREE.Vector3();
const camPos = new THREE.Vector3();
const camCenter = new THREE.Vector3();

function updateCamera(t, snap) {
  // orbit around the surfer, not the world origin, so it stays framed
  camCenter.copy(surfer.position);

  const angle = t * 0.085;
  const radius = 14.4 + Math.sin(t * 0.13) * 1.8;
  camPos.set(
    camCenter.x + Math.sin(angle) * radius,
    5.8 + Math.sin(t * 0.31) * 0.5 + Math.sin(t * 0.17) * 0.9,
    camCenter.z + Math.cos(angle) * radius
  );
  camTarget.set(
    camCenter.x + Math.sin(t * 0.21) * 0.35,
    2.15 + Math.sin(t * 0.42) * 0.16,
    camCenter.z + Math.cos(t * 0.17) * 0.35 + 0.3
  );
  if (snap) camera.position.copy(camPos);
  else camera.position.lerp(camPos, 0.055);
  camera.lookAt(camTarget);
}

function animate() {
  const t = (performance.now() - startTime) / 1000;

  // ocean + sky
  ocean.material.uniforms.uTime.value = t;
  sky.position.copy(camera.position);
  sunGlow.position.copy(sunDir).multiplyScalar(520).add(camera.position);

  // surfer rides the wave field near the origin
  placeSurfer(0.35 * Math.sin(t * 0.11), 0.28 * Math.cos(t * 0.09), t);
  pelican.update(t);
  updateSpray(t);
  birds.update(t);

  // slow, drifting orbit around the surfer
  updateCamera(t, false);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// start from a fully framed shot (no fly-in from the origin)
placeSurfer(0, 0, 0);
pelican.update(0);
updateCamera(0, true);
animate();

// ---------------------------------------------------------------------------
// resize
// ---------------------------------------------------------------------------

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});