import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { createOcean } from "./ocean.js";
import { createSky, SUN_DIR } from "./sky.js";
import { createPelican } from "./pelican.js";
import { createSpray } from "./spray.js";
import { placeRider } from "./ride.js";

const canvas = document.querySelector("#view");

function showError(err) {
  const note = document.createElement("pre");
  note.id = "gl-error";
  note.textContent = err && err.stack ? err.stack : String(err);
  document.body.appendChild(note);
}
window.addEventListener("error", (event) => showError(event.error || event.message));
window.addEventListener("unhandledrejection", (event) => showError(event.reason));

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color("#f3b48a");
scene.fog = new THREE.Fog("#f3b48a", 28, 78);

const camera = new THREE.PerspectiveCamera(34, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(-2.2, 2.4, 5.2);

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.045).texture;
pmrem.dispose();

const sky = createSky();
scene.add(sky.dome, sky.clouds);

const ocean = createOcean();
scene.add(ocean.mesh);

const pelican = createPelican();
scene.add(pelican.root);

const spray = createSpray();
scene.add(spray.group);

const hemi = new THREE.HemisphereLight(0xc5ddff, 0xe0a070, 0.7);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff1d4, 3.4);
sun.position.copy(SUN_DIR).multiplyScalar(18);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 2;
sun.shadow.camera.far = 36;
sun.shadow.camera.left = -6;
sun.shadow.camera.right = 6;
sun.shadow.camera.top = 6;
sun.shadow.camera.bottom = -6;
sun.shadow.bias = -0.0008;
scene.add(sun, sun.target);

const rim = new THREE.DirectionalLight(0xc9e4ff, 0.85);
rim.position.set(-6, 4, 8);
scene.add(rim);

const look = new THREE.Vector3();

function frame(t, dt) {
  const ride = placeRider(pelican.root, t);
  pelican.update(t, ride.turn);
  ocean.update(t, ride.originX);
  sky.update(t);
  spray.update(dt, pelican.root, ride.speed);

  sun.position.set(SUN_DIR.x * 18, SUN_DIR.y * 18, SUN_DIR.z * 18 + ride.z);
  sun.target.position.set(0, 0.6, ride.z);
  sun.target.updateMatrixWorld();

  const focusY = pelican.root.position.y;
  const focusZ = pelican.root.position.z;
  camera.up.set(0, 1, 0);
  camera.position.set(
    -2.15 + Math.sin(t * 0.23) * 0.1,
    focusY + 1.55 + Math.sin(t * 0.41) * 0.04,
    focusZ + 5.35,
  );
  look.set(0.35, focusY + 0.85, focusZ * 0.25);
  camera.lookAt(look);
}

let time = 0;
for (let i = 0; i < 50; i++) {
  time += 1 / 60;
  frame(time, 1 / 60);
}

function tick(now) {
  const dt = Math.min(0.033, (now - tick.last) / 1000 || 1 / 60);
  tick.last = now;
  time += dt;
  frame(time, dt);
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick.last = performance.now();
requestAnimationFrame(tick);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
