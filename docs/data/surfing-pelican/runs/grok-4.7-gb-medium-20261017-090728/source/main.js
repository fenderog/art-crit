import * as THREE from "three";
import { heightAt, createWater, createSky, TRAIL_N, HORIZON } from "./ocean.js";
import { createRideState, sampleRide, alignToSurface, flatRight } from "./ride.js";
import { createPelican, posePelican, sprayTexture } from "./pelican.js";

const SUN = new THREE.Vector3(0.32, 0.52, 0.62).normalize();

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.setClearColor(HORIZON, 1);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  38,
  window.innerWidth / Math.max(1, window.innerHeight),
  0.12,
  600,
);

scene.add(new THREE.AmbientLight(0xffe2cc, 0.22));
const hemi = new THREE.HemisphereLight(0xffc9a0, 0x16485a, 0.95);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff1d4, 2.15);
sun.target.position.set(0, 0, 0);
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0x9ec8ea, 0.45);
scene.add(fill, fill.target);

const sky = createSky();
scene.add(sky);
sky.material.uniforms.uSunDir.value.copy(SUN);

const water = createWater();
scene.add(water.mesh);
water.uniforms.uSunDir.value.copy(SUN);

const rig = createPelican();
rig.root.traverse((obj) => {
  obj.frustumCulled = false;
});
scene.add(rig.root);

const flock = createFlock();
scene.add(flock.group);
const clouds = createClouds();
scene.add(clouds);

const spray = createSpray();
scene.add(spray.points);

const ride = createRideState();
const right = new THREE.Vector3();
const look = new THREE.Vector3();
const lookSmooth = new THREE.Vector3();
const camDesired = new THREE.Vector3();
const focus = new THREE.Vector3();
const tailWorld = new THREE.Vector3();
const emitA = new THREE.Vector3();
const sunPos = new THREE.Vector3();
const trailPoint = new THREE.Vector2();
const worldUp = new THREE.Vector3(0, 1, 0);

const trail = water.uniforms.uTrail.value;
let trailWarm = false;
let lastTrail = new THREE.Vector2(1e4, 1e4);
let ready = false;

const clock = new THREE.Clock();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / Math.max(1, window.innerHeight);
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function frame(t, dt) {
  sampleRide(t, ride);
  alignToSurface(rig.root, ride.normal, ride.travel);
  rig.root.position.copy(ride.position);
  posePelican(rig, t, ride);

  flatRight(ride.travel, right);

  // The swell always travels +z and the line is +x, so the camera stays in that
  // frame: ahead of the beak and downhill, above the face.
  focus.copy(ride.position);
  camDesired.set(focus.x + 4.3, focus.y + 2.35, focus.z + 4.9);
  const camH = heightAt(camDesired.x, camDesired.z, t);
  if (camDesired.y < camH + 1.7) camDesired.y = camH + 1.7;
  look.set(focus.x - 0.3, focus.y + 0.9, focus.z - 0.2);

  if (!ready || camera.position.distanceTo(camDesired) > 6) {
    camera.position.copy(camDesired);
    lookSmooth.copy(look);
    ready = true;
  } else {
    const k = 1 - Math.exp(-3.4 * dt);
    camera.position.lerp(camDesired, k);
    lookSmooth.lerp(look, 1 - Math.exp(-5 * dt));
  }
  camera.up.copy(worldUp);
  camera.lookAt(lookSmooth);

  sunPos.copy(focus).addScaledVector(SUN, 40);
  sun.position.copy(sunPos);
  sun.target.position.copy(focus);
  fill.position.set(focus.x - 8, focus.y + 5, focus.z - 6);
  fill.target.position.copy(focus);

  sky.position.copy(camera.position);
  water.uniforms.uTime.value = t;

  const tile = water.tile;
  water.mesh.position.x = Math.floor(ride.position.x / tile) * tile;
  water.mesh.position.z = Math.floor(ride.position.z / tile) * tile;

  rig.tailMark.getWorldPosition(tailWorld);
  trailPoint.set(tailWorld.x, tailWorld.z);
  if (!trailWarm) {
    for (const p of trail) p.copy(trailPoint);
    lastTrail.copy(trailPoint);
    trailWarm = true;
  } else if (trailPoint.distanceTo(lastTrail) > 0.5) {
    for (let i = TRAIL_N - 1; i > 0; i--) trail[i].copy(trail[i - 1]);
    trail[0].copy(trailPoint);
    lastTrail.copy(trailPoint);
  }

  updateSpray(dt);
  updateFlock(t);
  clouds.position.set(ride.position.x, 0, ride.position.z);
}

function createSpray() {
  const n = 180;
  const positions = new Float32Array(n * 3);
  const ages = new Float32Array(n);
  const vels = new Float32Array(n * 3);
  ages.fill(0);
  for (let i = 0; i < n; i++) positions[i * 3 + 1] = -999;
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({
    color: 0xfff8f2,
    size: 0.22,
    map: sprayTexture(),
    transparent: true,
    depthWrite: false,
    opacity: 0.85,
    sizeAttenuation: true,
  });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  return { points, positions, ages, vels, n, cursor: 0 };
}

function updateSpray(dt) {
  const { positions, ages, vels, n } = spray;
  const energy = 0.45 + (1 - ride.lip) * 0.7 + ride.lip * ride.lip * 0.9;
  const births = Math.min(8, energy * dt * 70);
  for (let k = 0; k < births; k++) {
    const i = spray.cursor;
    spray.cursor = (spray.cursor + 1) % n;
    const fromTail = Math.random() < 0.65;
    if (fromTail) emitA.set(0.05 * (Math.random() - 0.5), 0.08, 1.05);
    else emitA.set(0.28, 0.06, 0.15);
    rig.root.localToWorld(emitA);
    const j = i * 3;
    positions[j] = emitA.x;
    positions[j + 1] = emitA.y;
    positions[j + 2] = emitA.z;
    const kick = 1.4 + Math.random() * 2.2;
    vels[j] = -ride.travel.x * kick + right.x * (0.4 + Math.random() * 1.3);
    vels[j + 1] = 1.1 + Math.random() * 2.4 + ride.lip * 1.6;
    vels[j + 2] = -ride.travel.z * kick + right.z * (0.4 + Math.random() * 1.3);
    ages[i] = 0.35 + Math.random() * 0.45;
  }
  for (let i = 0; i < n; i++) {
    const j = i * 3;
    if (ages[i] <= 0) {
      positions[j + 1] = -999;
      continue;
    }
    ages[i] -= dt;
    vels[j + 1] -= 5.2 * dt;
    positions[j] += vels[j] * dt;
    positions[j + 1] += vels[j + 1] * dt;
    positions[j + 2] += vels[j + 2] * dt;
  }
  spray.points.geometry.attributes.position.needsUpdate = true;
}

function createFlock() {
  const group = new THREE.Group();
  const birds = [];
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x2e3438, roughness: 0.6 });
  for (let i = 0; i < 4; i++) {
    const b = new THREE.Group();
    const wingGeo = new THREE.BoxGeometry(0.42, 0.02, 0.12);
    const left = new THREE.Mesh(wingGeo, bodyMat);
    const rightW = new THREE.Mesh(wingGeo, bodyMat);
    left.position.x = -0.24;
    rightW.position.x = 0.24;
    b.add(left, rightW);
    group.add(b);
    birds.push({ group: b, left, right: rightW, phase: i * 1.7, radius: 16 + i * 3, alt: 8.5 + i * 0.8 });
  }
  return { group, birds };
}

function updateFlock(t) {
  flock.group.position.set(ride.position.x, 0, ride.position.z);
  for (const b of flock.birds) {
    const a = t * 0.23 + b.phase;
    b.group.position.set(Math.cos(a) * b.radius, b.alt + Math.sin(a * 2) * 0.3, -6 + Math.sin(a) * 3.5);
    const flap = Math.sin(t * 6 + b.phase) * 0.5;
    b.left.rotation.z = 0.4 + flap;
    b.right.rotation.z = -0.4 - flap;
    b.group.rotation.y = -a + Math.PI / 2;
  }
}

function createClouds() {
  const group = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({
    color: 0xffe3d0,
    transparent: true,
    opacity: 0.78,
    depthWrite: false,
  });
  const geo = new THREE.SphereGeometry(1, 16, 12);
  const spots = [
    [-18, 11, -14, 3.2],
    [-8, 13, -22, 4.1],
    [16, 12, -16, 3.4],
    [6, 15, -28, 5],
    [-24, 14, -8, 2.6],
    [22, 16, -26, 3.8],
  ];
  for (const [x, y, z, s] of spots) {
    const puff = new THREE.Group();
    puff.position.set(x, y, z);
    for (let i = 0; i < 4; i++) {
      const m = new THREE.Mesh(geo, mat);
      m.position.set((i - 1.5) * s * 0.45, (i % 2) * 0.4, i * 0.15);
      m.scale.setScalar(s * (0.7 + (i % 3) * 0.12));
      puff.add(m);
    }
    group.add(puff);
  }
  return group;
}

function tick() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
  frame(t, dt);
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}

frame(0, 1 / 60);
renderer.render(scene, camera);
requestAnimationFrame(tick);
