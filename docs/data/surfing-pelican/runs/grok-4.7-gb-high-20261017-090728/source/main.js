import * as THREE from "three";
import { WORLD_UP, composeRootQuaternion, rootBasis } from "./frame.js";
import { createOcean, createRideState, rideState } from "./ocean.js";
import { createPelican } from "./pelican.js";
import { createSky } from "./sky.js";
import { createSpray } from "./spray.js";

// Reflection of the face-side view about the wave normal, so the lip carries a sun path.
export const SUN_DIR = new THREE.Vector3(0.34, 0.86, -0.22).normalize();

const _ride = createRideState();
const _ahead = createRideState();
const _travel = new THREE.Vector3();
const _camQuat = new THREE.Quaternion();
const _camAxes = {
  right: new THREE.Vector3(),
  up: new THREE.Vector3(),
  back: new THREE.Vector3(),
  forward: new THREE.Vector3(),
};
const _boardAxes = {
  right: new THREE.Vector3(),
  up: new THREE.Vector3(),
  back: new THREE.Vector3(),
  forward: new THREE.Vector3(),
};
const _tail = new THREE.Vector3();
const _rail = new THREE.Vector3();
const _lip = new THREE.Vector3();
const _left = new THREE.Vector3();
const _camDesired = new THREE.Vector3();
const _lookDesired = new THREE.Vector3();
const _camPos = new THREE.Vector3();
const _camLook = new THREE.Vector3();

let cameraReady = false;

export function poseAt(t, pelican) {
  const ride = rideState(t, _ride);
  rideState(t + 0.2, _ahead);
  _travel.subVectors(_ahead.position, ride.position);
  composeRootQuaternion(_travel, ride.normal, pelican.root.quaternion);
  pelican.root.position.copy(ride.position);
  pelican.root.position.y += 0.015;
  pelican.animate(t, _travel);
  pelican.root.updateMatrixWorld(true);
  return ride;
}

function placeCamera(dt, t, ride, pelican, camera) {
  composeRootQuaternion(_travel, WORLD_UP, _camQuat);
  rootBasis(_camQuat, _camAxes);
  const narrow = camera.aspect < 0.9;
  const dist = narrow ? 9.0 : 7.5;
  _camDesired.copy(ride.position)
    .addScaledVector(_camAxes.right, -dist)
    .addScaledVector(_camAxes.back, dist * 0.22)
    .addScaledVector(WORLD_UP, narrow ? 0.28 : 0.02);
  _camDesired.y += Math.sin(t * 0.27) * 0.1;
  pelican.lookAnchor.getWorldPosition(_lookDesired);
  if (!cameraReady) {
    _camPos.copy(_camDesired);
    _camLook.copy(_lookDesired);
    cameraReady = true;
  } else {
    _camPos.lerp(_camDesired, 1 - Math.exp(-2.0 * dt));
    _camLook.lerp(_lookDesired, 1 - Math.exp(-3.0 * dt));
  }
  camera.position.copy(_camPos);
  camera.up.copy(WORLD_UP);
  camera.lookAt(_camLook);
}

export function start() {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0xf2a36a, 1);
  document.body.prepend(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.1, 700);

  const ocean = createOcean();
  const pelican = createPelican();
  const sky = createSky();
  const spray = createSpray();
  scene.add(sky.mesh, sky.clouds, ocean.mesh, pelican.root, spray.points);

  const sun = new THREE.DirectionalLight(0xffc89a, 3.5);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.00025;
  sun.shadow.normalBias = 0.03;
  const shadow = sun.shadow.camera;
  shadow.left = -6;
  shadow.right = 6;
  shadow.top = 6;
  shadow.bottom = -6;
  shadow.near = 0.5;
  shadow.far = 40;
  shadow.updateProjectionMatrix();
  scene.add(sun, sun.target);

  const hemi = new THREE.HemisphereLight(0xb7cbe0, 0xc4845a, 0.55);
  scene.add(hemi);

  const fill = new THREE.DirectionalLight(0x9ec4de, 0.72);
  const rim = new THREE.DirectionalLight(0xffe1c0, 1.05);
  scene.add(fill, fill.target, rim, rim.target);

  const fillDir = new THREE.Vector3(0.05, 0.42, -0.9).normalize();
  const rimDir = new THREE.Vector3(0.75, 0.45, 0.2).normalize();

  function onResize() {
    const aspect = window.innerWidth / Math.max(1, window.innerHeight);
    camera.aspect = aspect;
    camera.fov = aspect < 0.9 ? 42 : 36;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
  window.addEventListener("resize", onResize);
  onResize();

  let t = 0.4;

  function tick(dt) {
    t += dt;
    const ride = poseAt(t, pelican);
    rootBasis(pelican.root.quaternion, _boardAxes);
    pelican.anchors.tail.getWorldPosition(_tail);
    pelican.anchors.rail.getWorldPosition(_rail);
    _left.copy(_boardAxes.right).negate();
    _lip.copy(ride.position)
      .addScaledVector(_boardAxes.right, 0.9)
      .addScaledVector(WORLD_UP, 1.55)
      .addScaledVector(_boardAxes.back, 0.35);
    ocean.update(t, ride.position, _tail, {
      position: ride.position,
      forward: _boardAxes.forward,
      right: _boardAxes.right,
    });
    placeCamera(dt, t, ride, pelican, camera);
    ocean.uniforms.uCameraPos.value.copy(camera.position);
    ocean.uniforms.uSunDir.value.copy(SUN_DIR);
    sky.update(t, camera, SUN_DIR);
    spray.update(dt, {
      tail: _tail,
      rail: _rail,
      lip: _lip,
      back: _boardAxes.back,
      left: _left,
    });

    sun.position.copy(ride.position).addScaledVector(SUN_DIR, 22);
    sun.target.position.copy(ride.position);
    fill.position.copy(ride.position).addScaledVector(fillDir, 14);
    fill.target.position.copy(ride.position);
    rim.position.copy(ride.position).addScaledVector(rimDir, 12);
    rim.target.position.copy(ride.position);
  }

  for (let i = 0; i < 80; i++) tick(1 / 30);

  let last = performance.now();
  function frame(now) {
    const dt = Math.min(0.033, (now - last) / 1000 || 0.016);
    last = now;
    tick(dt);
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

if (typeof document !== "undefined") start();
