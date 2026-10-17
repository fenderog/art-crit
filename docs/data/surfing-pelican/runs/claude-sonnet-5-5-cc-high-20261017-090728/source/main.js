import * as THREE from "three";
import { surface, surfaceNormal, SLOPE, heroAmp } from "./waves.js";
import { createSky, bakeEnvironment, SUN_DIR } from "./sky.js";
import { createOcean } from "./ocean.js";
import { createBoard } from "./board.js";
import { createPelican } from "./pelican.js";
import { createSpray } from "./spray.js";
import { createTrail } from "./trail.js";
import { createIslands, createGulls } from "./scenery.js";

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 6000);

// --- world ---------------------------------------------------------------
const sky = createSky();
scene.add(sky.dome);
scene.environment = bakeEnvironment(renderer, sky.material);
scene.environmentIntensity = 0.55;

const ocean = createOcean();
scene.add(ocean.mesh);
scene.add(createIslands());
const gulls = createGulls();
scene.add(gulls.group);

// --- lights ----------------------------------------------------------------
const sun = new THREE.DirectionalLight(0xffc48a, 3.4);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -3.5;
sun.shadow.camera.right = 3.5;
sun.shadow.camera.top = 3.5;
sun.shadow.camera.bottom = -3.5;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.03;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0xffffff, 1.2);
scene.add(fill, fill.target);
scene.add(new THREE.HemisphereLight(0xf2f0ff, 0x3a8a80, 0.45));

// --- surfer ----------------------------------------------------------------
const rig = new THREE.Group();
scene.add(rig);
const board = createBoard();
rig.add(board);
const pelican = createPelican();
board.add(pelican.root);
pelican.root.position.set(0, 0.0, -0.05);
const spray = createSpray();
scene.add(spray.points);
const trail = createTrail();
scene.add(trail.mesh);

// --- helpers ---------------------------------------------------------------
const Q = new URLSearchParams(location.search);
const T0 = Number(Q.get("t")) || 0; // start offset (handy for stills)
const QD = Q.get("dist");
const QA = Q.get("az");
const W = 0.43; // carve rhythm (rad/s)
const pathAt = (t) => {
  const x0 = 8 * Math.sin(W * t);
  const u = 3.5 + 0.8 * Math.cos(W * t);
  return { x0, z0: u + SLOPE * x0 };
};
const rnd = (a, b) => a + Math.random() * (b - a);
const wrapPI = (a) => Math.atan2(Math.sin(a), Math.cos(a));

const P = new THREE.Vector3();
const P2 = new THREE.Vector3();
const tmp = new THREE.Vector3();
const up = new THREE.Vector3();
const fwd = new THREE.Vector3();
const left = new THREE.Vector3();
const basis = new THREE.Matrix4();
const targetQ = new THREE.Quaternion();
const camTarget = new THREE.Vector3();
const camPos = new THREE.Vector3();
const lookAt = new THREE.Vector3();

let yaw = null;
let turnRate = 0;
let camInit = false;
let accSurfer = 0;
let accCrest = 0;
let last = performance.now();
let tClock = 0;

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  // keep the subject framed on tall/narrow screens
  camera.fov = w / h < 1 ? 62 : 50;
  camera.updateProjectionMatrix();
  spray.uniforms.uScale.value = (h * renderer.getPixelRatio()) / (2 * Math.tan((camera.fov * Math.PI) / 360));
}
window.addEventListener("resize", resize);
resize();

function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  tClock += dt;
  const t = T0 + tClock;

  sky.uniforms.uTime.value = t;
  ocean.uniforms.uTime.value = t;

  // ---- surfer path ----
  const { x0, z0 } = pathAt(t);
  const p1 = pathAt(t + 0.06);
  surface(x0, z0, t, P);
  surface(p1.x0, p1.z0, t, P2);
  tmp.subVectors(P2, P).multiplyScalar(1 / 0.06);
  const speed = Math.hypot(tmp.x, tmp.z);
  const target = Math.atan2(tmp.x, tmp.z);
  if (yaw === null) yaw = target;
  const prevYaw = yaw;
  yaw += wrapPI(target - yaw) * (1 - Math.exp(-dt * 4.5));
  turnRate += (wrapPI(yaw - prevYaw) / Math.max(dt, 1e-3) - turnRate) * (1 - Math.exp(-dt * 6));

  const N = surfaceNormal(x0, z0, t, 0.9);
  up.copy(N).lerp(new THREE.Vector3(0, 1, 0), 0.45).normalize();
  fwd.set(Math.sin(yaw), 0, Math.cos(yaw));
  fwd.addScaledVector(up, -fwd.dot(up)).normalize();
  left.crossVectors(up, fwd).normalize();
  up.crossVectors(fwd, left).normalize();
  basis.makeBasis(left, up, fwd);
  targetQ.setFromRotationMatrix(basis);
  rig.position.copy(P).addScaledVector(up, 0.02);
  if (!camInit) rig.quaternion.copy(targetQ);
  else rig.quaternion.slerp(targetQ, 1 - Math.exp(-dt * 9));

  const pump = 0.5 + 0.5 * Math.sin(2 * W * t + 0.6);
  pelican.update(t, { turn: turnRate, bank: 0, speed, pump, sinYaw: Math.sin(yaw) });

  // ---- wake & spray ----
  trail.update(t, x0, z0, THREE.MathUtils.clamp(speed / 3.5, 0.2, 1));

  const tailPos = tmp.set(0, 0.05, -1.45).applyMatrix4(rig.matrixWorld.compose(rig.position, rig.quaternion, rig.scale));
  accSurfer += dt * (30 + speed * 22 + Math.abs(turnRate) * 55);
  const sideV = Math.sign(turnRate) || 1;
  while (accSurfer >= 1) {
    accSurfer -= 1;
    const k = Math.min(1, Math.abs(turnRate) * 0.8);
    const sx = rnd(-0.4, 0.4) + sideV * k * 0.2;
    spray.emit(
      tailPos.x + rnd(-0.25, 0.25), tailPos.y, tailPos.z + rnd(-0.2, 0.2),
      -fwd.x * speed * 0.25 + left.x * (sx * 3 - sideV * k * 2.2) + rnd(-0.4, 0.4),
      rnd(1.2, 2.8) + k * 1.5,
      -fwd.z * speed * 0.25 + left.z * (sx * 3 - sideV * k * 2.2) + rnd(-0.4, 0.4),
      rnd(0.12, 0.3), rnd(0.5, 1.1), 7, 0.5
    );
  }
  // mist torn off the lip by the offshore breeze
  accCrest += dt * 70;
  while (accCrest >= 1) {
    accCrest -= 1;
    const cx = rnd(-30, 30);
    const cu = rnd(0.2, 1.4);
    surface(cx, cu + SLOPE * cx, t, tmp);
    spray.emit(
      tmp.x, tmp.y + 0.1, tmp.z,
      rnd(-0.6, 0.6), rnd(0.6, 2.2), rnd(-6, -2.5),
      rnd(0.25, 0.7), rnd(1.0, 2.0), 1.5, 0.4
    );
  }
  spray.update(dt);

  // ---- lights follow the subject ----
  sun.position.copy(rig.position).addScaledVector(SUN_DIR, 30);
  sun.target.position.copy(rig.position).add(new THREE.Vector3(0, 1, 0));
  fill.position.copy(rig.position).add(new THREE.Vector3(5, 3, 9));
  fill.target.position.copy(rig.position);

  // ---- camera: slow drifting orbit in front of the face ----
  const az = QA ? Number(QA) : 0.5 * Math.sin(t * 0.061) + 0.22 * Math.sin(t * 0.143 + 1.3);
  const dist = QD ? Number(QD) : 8.5 + 2.0 * Math.sin(t * 0.047 + 0.6) + 0.8 * Math.sin(t * 0.11);
  const lift = 0.9 + 1.1 * (0.5 + 0.5 * Math.sin(t * 0.053 + 2.0)) + 0.4 * Math.sin(t * 0.13);
  camTarget.set(rig.position.x, rig.position.y + 0.9, rig.position.z);
  const follow = camInit ? 1 - Math.exp(-dt * 1.6) : 1;
  lookAt.lerp(camTarget, follow);
  if (!camInit) lookAt.copy(camTarget);
  camPos.set(lookAt.x + Math.sin(az) * dist, 0, lookAt.z + Math.cos(az) * dist);
  surface(camPos.x, camPos.z, t, tmp);
  camPos.y = tmp.y + lift;
  camera.position.copy(camPos);
  camera.position.x += 0.04 * Math.sin(t * 1.3);
  camera.position.y += 0.05 * Math.sin(t * 1.9);
  camera.lookAt(lookAt.x, lookAt.y + 0.5, lookAt.z);
  camera.rotation.z += 0.012 * Math.sin(t * 0.9);

  sky.dome.position.copy(camera.position);
  gulls.update(t);
  camInit = true;

  renderer.render(scene, camera);
}
requestAnimationFrame((n) => {
  last = n;
  frame(n);
});
