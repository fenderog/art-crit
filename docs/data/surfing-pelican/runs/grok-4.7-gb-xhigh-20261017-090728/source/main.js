import * as THREE from "three";
import { poseAt } from "./sim.js";
import { createWater } from "./water.js";
import { createSky } from "./sky.js";
import { createSurfer } from "./surfer.js";
import { createFx } from "./fx.js";
import { SUN_DIR, horizonColor } from "./theme.js";

const canvas = document.querySelector("#c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.98;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(horizonColor, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(36, 1, 0.08, 900);

const hemi = new THREE.HemisphereLight(0xffe0c8, 0x1a6070, 0.95);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffd2a8, 2.7);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 2;
sun.shadow.camera.far = 26;
sun.shadow.camera.left = -4.5;
sun.shadow.camera.right = 4.5;
sun.shadow.camera.top = 4.5;
sun.shadow.camera.bottom = -4.5;
sun.shadow.camera.updateProjectionMatrix();
sun.shadow.bias = -0.0006;
sun.shadow.normalBias = 0.025;
scene.add(sun);
scene.add(sun.target);

const fill = new THREE.DirectionalLight(0xc5e4f2, 0.85);
fill.position.set(5, 3.2, 4);
scene.add(fill);

const bounce = new THREE.DirectionalLight(0xffb07a, 0.28);
bounce.position.set(-2, 0.4, 3);
scene.add(bounce);

const water = createWater();
const sky = createSky();
const surfer = createSurfer();
scene.add(water.mesh, sky.mesh, surfer.rig, ...sky.gulls);
const fx = createFx(scene);

const origin = new THREE.Vector3();
const camLocal = new THREE.Vector3();
const lookLocal = new THREE.Vector3();
const lookTarget = new THREE.Vector3();

function resize() {
  const w = window.innerWidth;
  const h = Math.max(1, window.innerHeight);
  camera.aspect = w / h;
  camera.fov = w < h ? 50 : 36;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h);
}
resize();
window.addEventListener("resize", resize);

function placeCamera(time, pose) {
  const breathe = Math.sin(time * 0.13);
  camLocal.set(2.15 + breathe * 0.3, 1.7 + Math.sin(time * 0.09) * 0.06, -7.15);
  lookLocal.set(0.0, 0.72, 0.05);
  camera.position.copy(pose.position).add(camLocal.applyQuaternion(pose.quaternion));
  const under = pose.position.y + 0.7;
  if (camera.position.y < under) camera.position.y = under;
  lookTarget.copy(pose.position).add(lookLocal.applyQuaternion(pose.quaternion));
  camera.position.sub(origin);
  lookTarget.sub(origin);
  camera.up.set(0, 1, 0);
  camera.lookAt(lookTarget);
}

function frame(time, dt) {
  const pose = poseAt(time);
  origin.set(pose.position.x, 0, pose.position.z);

  surfer.rig.position.set(0, pose.position.y, 0);
  surfer.rig.quaternion.copy(pose.quaternion);
  surfer.update(time, pose);

  const seg = water.seg;
  const snapX = Math.round(pose.position.x / seg) * seg;
  const snapZ = Math.round(pose.position.z / seg) * seg;
  water.mesh.position.set(snapX - origin.x, 0, snapZ - origin.z);
  water.setOrigin(snapX, snapZ, time);

  placeCamera(time, pose);
  sky.mesh.position.copy(camera.position);
  sky.update(time);

  sun.position.copy(SUN_DIR).multiplyScalar(14).add(surfer.rig.position);
  sun.target.position.set(0, pose.position.y + 0.5, 0);
  sun.target.updateMatrixWorld();

  fx.update(time, dt, pose, origin);
}

let time = 6.4;
for (let i = 0; i < 270; i++) {
  time += 1 / 60;
  frame(time, 1 / 60);
}
renderer.render(scene, camera);

let last = performance.now();
function loop(now) {
  const dt = Math.min(0.033, (now - last) / 1000);
  last = now;
  time += dt;
  frame(time, dt);
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
