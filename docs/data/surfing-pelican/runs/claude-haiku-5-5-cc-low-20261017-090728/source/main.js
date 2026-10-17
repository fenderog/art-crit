import * as THREE from "three";

// Renderer, scene and camera
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3ff);
scene.fog = new THREE.Fog(0x8fd3ff, 25, 90);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200);

// Lighting
scene.add(new THREE.HemisphereLight(0xffffff, 0x3a6ea5, 1.1));
const sun = new THREE.DirectionalLight(0xfff4e0, 1.6);
sun.position.set(-10, 20, 8);
scene.add(sun);

// Ocean: a dense plane whose vertices are displaced by summed sine waves
const OCEAN_SIZE = 120;
const OCEAN_SEG = 120;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshPhongMaterial({
  color: 0x1a7fb8,
  shininess: 90,
  specular: 0x9fe6ff,
  flatShading: false,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
scene.add(ocean);
const basePositions = oceanGeo.attributes.position.array.slice();

function waveHeight(x, z, t) {
  return (
    Math.sin(x * 0.35 + t * 1.6) * 0.35 +
    Math.sin(z * 0.5 + t * 1.1) * 0.25 +
    Math.sin((x + z) * 0.22 + t * 0.9) * 0.3 +
    Math.sin(x * 0.9 - z * 0.7 + t * 2.3) * 0.08
  );
}

function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = basePositions[i * 3];
    const z = basePositions[i * 3 + 2];
    pos.setY(i, waveHeight(x, z, t));
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// Surfboard
const board = new THREE.Group();
const boardMat = new THREE.MeshPhongMaterial({ color: 0xff7a3d, shininess: 60 });
const boardBody = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), boardMat);
boardBody.scale.set(2.4, 0.09, 0.7);
board.add(boardBody);
const stripe = new THREE.Mesh(
  new THREE.SphereGeometry(1, 32, 8),
  new THREE.MeshPhongMaterial({ color: 0xfff3c4 })
);
stripe.scale.set(2.42, 0.095, 0.12);
board.add(stripe);
scene.add(board);

// Pelican
const pelican = new THREE.Group();
const white = new THREE.MeshPhongMaterial({ color: 0xf7f5ef, shininess: 30 });
const grey = new THREE.MeshPhongMaterial({ color: 0x8a949c, shininess: 20 });
const beakMat = new THREE.MeshPhongMaterial({ color: 0xf2b84b, shininess: 40 });
const pouchMat = new THREE.MeshPhongMaterial({ color: 0xf08a3c, shininess: 20 });
const eyeMat = new THREE.MeshPhongMaterial({ color: 0x111111, shininess: 100 });

const sphere = (r, mat, sx = 1, sy = 1, sz = 1) => {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 28, 18), mat);
  m.scale.set(sx, sy, sz);
  return m;
};

// Body (sits on the board, facing +x)
const body = new THREE.Group();
body.add(sphere(0.5, white, 1.3, 0.9, 0.85));
const tail = sphere(0.22, grey, 0.9, 0.5, 0.35);
tail.position.set(-0.7, 0.1, 0);
tail.rotation.z = 0.5;
body.add(tail);
body.position.y = 0.55;
pelican.add(body);

// Neck and head
const neck = sphere(0.22, white, 0.9, 1.6, 0.9);
neck.position.set(0.55, 1.0, 0);
neck.rotation.z = -0.5;
pelican.add(neck);

const head = sphere(0.28, white, 1, 0.95, 0.9);
head.position.set(0.8, 1.45, 0);
pelican.add(head);

const eye = sphere(0.05, eyeMat);
eye.position.set(0.95, 1.52, 0.2);
pelican.add(eye);
const eye2 = eye.clone();
eye2.position.z = -0.2;
pelican.add(eye2);

// Beak and pouch (cone pointing forward and slightly down)
const beakGroup = new THREE.Group();
beakGroup.position.set(0.95, 1.4, 0);
const beak = new THREE.Mesh(new THREE.ConeGeometry(0.1, 1.1, 20), beakMat);
beak.rotation.z = -Math.PI / 2 - 0.12;
beak.position.set(0.5, -0.05, 0);
beakGroup.add(beak);
const pouch = sphere(0.2, pouchMat, 0.7, 1.0, 0.5);
pouch.position.set(0.5, -0.22, 0);
beakGroup.add(pouch);
pelican.add(beakGroup);

// Wings: each wing pivots at the shoulder and flaps over time
function makeWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(0.1, 0.9, side * 0.4);
  const feathers = sphere(0.5, grey, 0.9, 0.12, 1.1);
  feathers.position.set(-0.45, 0, side * 0.45);
  const tip = sphere(0.3, grey, 0.8, 0.1, 0.9);
  tip.position.set(-1.0, 0.02, side * 0.7);
  pivot.add(feathers, tip);
  return pivot;
}
const wingL = makeWing(1);
const wingR = makeWing(-1);
pelican.add(wingL, wingR);

// Legs/feet are hidden by the board; a small crest adds character
const crest = sphere(0.08, grey, 0.4, 1.6, 0.25);
crest.position.set(0.7, 1.75, 0);
crest.rotation.z = -0.4;
pelican.add(crest);

pelican.scale.setScalar(1.0);
board.add(pelican);
pelican.position.set(0, 0.25, 0);

// Main loop
const clock = new THREE.Clock();
const BOARD_SPEED = 0.6;

function animate() {
  const t = clock.getElapsedTime();

  updateOcean(t);

  // The board travels along a gentle S-curve across the swell
  const phase = t * BOARD_SPEED * 0.4;
  const bx = Math.sin(phase) * 3;
  const bz = Math.sin(phase * 0.6) * 1.5;
  board.position.set(bx, 0, bz);

  // Board sits on the local wave surface and tilts with the slope
  const h = waveHeight(bx, bz, t);
  const dhdx = (waveHeight(bx + 0.1, bz, t) - waveHeight(bx - 0.1, bz, t)) / 0.2;
  const dhdz = (waveHeight(bx, bz + 0.1, t) - waveHeight(bx, bz - 0.1, t)) / 0.2;
  board.position.y = h + 0.02;
  board.rotation.set(0, 0, 0);
  board.rotation.z = Math.atan(dhdx) * 0.9;
  board.rotation.x = -Math.atan(dhdz) * 0.9;
  // Heading follows the direction of travel
  board.rotation.y = -Math.atan2(Math.cos(phase) * 3, Math.cos(phase * 0.6) * 0.9) * 0.3;

  // Pelican leans into the ride and bobs with the board
  pelican.rotation.z = Math.sin(t * 2.1) * 0.05 - 0.04;
  pelican.position.y = 0.25 + Math.sin(t * 3.0) * 0.03;
  body.position.y = 0.55 + Math.sin(t * 3.0) * 0.02;

  // Flapping wings to keep balance
  const flap = Math.sin(t * 5.5) * 0.45;
  wingL.rotation.z = 0.6 + flap;
  wingR.rotation.z = 0.6 + flap;
  wingL.rotation.x = 0.0;
  wingR.rotation.x = 0.0;

  // Camera slowly orbits the scene, always watching the surfer
  const orbit = t * 0.12;
  camera.position.set(
    board.position.x + Math.cos(orbit) * 7 - 2,
    3.2 + Math.sin(t * 0.3) * 0.4,
    board.position.z + Math.sin(orbit) * 7 + 3
  );
  camera.lookAt(board.position.x, 1.0, board.position.z);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
