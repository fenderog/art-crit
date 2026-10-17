import * as THREE from 'three';
import { PALETTE } from './theme.js';
import { waveHeight, waveNormal, SWELL } from './waves.js';
import { createSky, createSunSprite } from './sky.js';
import { createOcean } from './ocean.js';
import { createPelican } from './pelican.js';
import { createSpray, createGulls, createClouds, createFishFX } from './effects.js';

// Phase of the main swell where the pelican rides: just past the crest, on the
// steep front face (slope ~20°), so it travels with the wave like a real surfer.
const THETA_FACE = 2.3;

function makeRenderer() {
  const r = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  r.setSize(window.innerWidth, window.innerHeight);
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.12;
  r.setClearColor(new THREE.Color(PALETTE.horizon));
  document.body.appendChild(r.domElement);
  return r;
}

let renderer;
try {
  renderer = makeRenderer();
} catch (err) {
  const fb = document.getElementById('fallback');
  if (fb) fb.style.display = 'grid';
  throw err;
}

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(new THREE.Color(PALETTE.horizon), 80, 235); // for the standard-material props

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1600);
camera.position.set(-20, 10, 26); // starts wide; swoops in for the first seconds

const sunDir = new THREE.Vector3(0.62, 0.2, -0.42).normalize();

const sunLight = new THREE.DirectionalLight(0xffd9a8, 2.6);
sunLight.position.copy(sunDir).multiplyScalar(60);
scene.add(sunLight);
scene.add(new THREE.HemisphereLight(0xffd2b0, 0x123b46, 0.9));

// The "scenery rig": sky, sun, clouds and gulls ride along with the pelican so
// the distant backdrop behaves like a genuinely far-away world.
const rig = new THREE.Group();
scene.add(rig);
rig.add(createSky(sunDir));
rig.add(createSunSprite(sunDir));
const clouds = createClouds();
rig.add(clouds.group);
const gulls = createGulls();
rig.add(gulls.group);

const ocean = createOcean(sunDir);
scene.add(ocean.mesh);

const pelican = createPelican();
scene.add(pelican.board);

const spray = createSpray();
scene.add(spray.points);

const fish = createFishFX();
scene.add(fish.group);

// scratch objects (reused every frame)
const _n = new THREE.Vector3();
const _f = new THREE.Vector3();
const _r = new THREE.Vector3();
const _u = new THREE.Vector3();
const _camPos = new THREE.Vector3();
const _look = new THREE.Vector3();
const _spawn = new THREE.Vector3();
const _vel = new THREE.Vector3();
const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const AXIS_X = new THREE.Vector3(1, 0, 0);
const AXIS_Z = new THREE.Vector3(0, 0, 1);
const camLook = new THREE.Vector3(12, 1, 2);

const clock = new THREE.Clock();
let t = 0;
let sprayAcc = 0;

function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  t += dt;

  // ── kinematics: hold a fixed phase on the traveling swell while carving S-turns ──
  // swell phase: theta = k*x - omega*t + phase  =>  ride at theta = THETA_FACE
  const xBase = (THETA_FACE + SWELL.om * t - SWELL.phase) / SWELL.k;
  const x = xBase + 0.9 * Math.sin(0.19 * t + 0.6); // pumping down the face
  const z = 6.2 * Math.sin(0.12 * t) + 2.4 * Math.sin(0.29 * t + 1.7); // the carve
  const z1 = 6.2 * 0.12 * Math.cos(0.12 * t) + 2.4 * 0.29 * Math.cos(0.29 * t + 1.7); // z'
  const z2 = -6.2 * 0.0144 * Math.sin(0.12 * t) - 2.4 * 0.0841 * Math.sin(0.29 * t + 1.7); // z''
  const vx = SWELL.speed + 0.9 * 0.19 * Math.cos(0.19 * t + 0.6);
  const speed = Math.hypot(vx, z1);
  const carve = THREE.MathUtils.clamp(z1 / 0.9, -1, 1);
  const lean = THREE.MathUtils.clamp(z2 * 2.6, -0.6, 0.6); // heel into the turn
  const crouch = 0.5 + 0.5 * Math.sin(0.4 * t + 1.0);
  const y = waveHeight(x, z, t);

  pelican.board.position.set(x, y + 0.06, z);
  waveNormal(x, z, t, _n);
  _f.set(vx, 0, z1).normalize();
  _f.addScaledVector(_n, -_f.dot(_n)).normalize(); // travel dir, projected onto the surface
  _r.crossVectors(_f, _n).normalize();
  _u.crossVectors(_r, _f).normalize();
  _m.makeBasis(_f, _u, _r); // board: +X forward, +Y up (surface normal)
  pelican.board.quaternion.setFromRotationMatrix(_m);
  _q.setFromAxisAngle(AXIS_X, lean);
  pelican.board.quaternion.multiply(_q);
  _q.setFromAxisAngle(AXIS_Z, 0.05 * Math.sin(0.9 * t)); // gentle trim oscillation
  pelican.board.quaternion.multiply(_q);

  pelican.update({ t, dt, carve, lean, crouch, fishWorld: fish.active() });

  // ── spray off the nose, harder off the rail in turns ──
  sprayAcc += dt * (26 + Math.abs(lean) * 130 + Math.max(0, speed - 2.3) * 60 + Math.abs(carve) * 24);
  const emit = Math.floor(sprayAcc);
  sprayAcc -= emit;
  for (let i = 0; i < emit; i++) {
    pelican.nose.getWorldPosition(_spawn);
    _spawn.x += (Math.random() - 0.5) * 0.3;
    _spawn.z += (Math.random() - 0.5) * 0.3;
    _vel.set(
      vx * 0.28 + (Math.random() - 0.5) * 0.8,
      1.2 + Math.random() * 2.2,
      z1 * 0.28 - lean * 2.2 + (Math.random() - 0.5) * 1.4
    );
    spray.spawn(_spawn, _vel, 0.05 + Math.random() * 0.13, 0.45 + Math.random() * 0.55);
  }
  if (Math.abs(lean) > 0.22 && Math.random() < dt * 45) {
    // hard turn: fling a bucket off the outside rail
    (lean > 0 ? pelican.railR : pelican.railL).getWorldPosition(_spawn);
    _vel.set(vx * 0.2, 1.6 + Math.random() * 2, -lean * 3 + (Math.random() - 0.5));
    spray.spawn(_spawn, _vel, 0.08 + Math.random() * 0.16, 0.5 + Math.random() * 0.5);
  }
  spray.update(dt, t);

  fish.update(dt, t, pelican.board.position, spray);
  gulls.update(t);
  clouds.update(dt);

  // ── the world follows the rider ──
  rig.position.set(x, 0, z);
  ocean.mesh.position.set(x, 0, z); // shader works in world space, so waves stay seamless

  // ── camera: low chase cam over the rider's shoulder ──
  _camPos.set(x - 4.8, y + 2.4, z + 4.6 + 1.6 * Math.sin(0.05 * t));
  const minY = waveHeight(_camPos.x, _camPos.z, t) + 0.6;
  if (_camPos.y < minY) _camPos.y = minY; // never dip under a crest
  camera.position.lerp(_camPos, 1 - Math.exp(-2.2 * dt));
  _look.set(x + 1.8, y + 1.05, z + 0.4 * Math.sin(0.05 * t));
  camLook.lerp(_look, 1 - Math.exp(-3 * dt));
  camera.lookAt(camLook);

  ocean.uniforms.uTime.value = t;
  ocean.uniforms.uCamPos.value.copy(camera.position);

  renderer.render(scene, camera);
}

function onResize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h);
  spray.setScale(h, 50);
}
window.addEventListener('resize', onResize);
onResize();

renderer.setAnimationLoop(frame);
