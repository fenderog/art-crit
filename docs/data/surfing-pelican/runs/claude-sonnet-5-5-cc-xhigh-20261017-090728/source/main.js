import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { SMAAPass } from "three/addons/postprocessing/SMAAPass.js";
import { createGradePass } from "./src/grade.js";
import { createSky, SUN_DIR } from "./src/sky.js";
import { createWaterMaterials, createWaveGeometry, createOceanGeometry } from "./src/water.js";
import { createSurfer } from "./src/surfer.js";
import { createRig } from "./src/rig.js";
import { createParticles } from "./src/particles.js";
import { createSpray } from "./src/spray.js";
import { createTrail } from "./src/trail.js";
import { createHeadland, createGulls } from "./src/scenery.js";

// Development switches: ?t=12 renders one deterministic frame at 12 s, ?view=pelican shows the bird
// alone (&az, &el, &d, &ty orbit it), ?cam=x,y,z,tx,ty,tz,fov and ?rel=dx,dy,dz,fov,ax,ay,az place
// the camera by hand (rel is relative to the surfer).
const params = new URLSearchParams(location.search);
const fixedT = params.has("t") ? parseFloat(params.get("t")) : null;
const preview = params.get("view") === "pelican";

const maxPixelRatio = Math.min(window.devicePixelRatio || 1, 2);
let pixelRatio = Math.min(maxPixelRatio, 1.25);

const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance" });
renderer.setPixelRatio(pixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.88;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.1, 6000);

// ---- sky and light
const sky = createSky(renderer);
scene.add(sky.mesh);
scene.environment = sky.envMap;

const sun = new THREE.DirectionalLight(0xfff0d8, 3.2);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
const sc = sun.shadow.camera;
sc.left = sc.bottom = -8;
sc.right = sc.top = 8;
sc.near = 1;
sc.far = 90;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.02;
sun.shadow.intensity = 0.6;
scene.add(sun, sun.target);
// warm bounce from the whitewater, on the camera side of the surfer
const fill = new THREE.DirectionalLight(0xffe0bc, 1.5);
fill.position.set(8, 5, -14);
scene.add(fill);

// ---- the sea: a depth pre-pass for the wave keeps the expensive water shader to one pass per pixel
const water = createWaterMaterials(sky.envMap);
const waveMesh = new THREE.Mesh(createWaveGeometry(), water.wave);
const waveDepth = new THREE.Mesh(waveMesh.geometry, water.waveDepth);
const oceanMesh = new THREE.Mesh(createOceanGeometry(), water.ocean);
waveMesh.receiveShadow = true;
waveDepth.renderOrder = -10;
for (const m of [waveMesh, waveDepth, oceanMesh]) m.frustumCulled = false;
scene.add(waveDepth, waveMesh, oceanMesh);
const trail = createTrail(water.uniforms);

// ---- far away: the headland the wave peels from, and a few gulls
const headland = createHeadland();
const gulls = createGulls();
scene.add(headland, gulls.group);

// ---- the pelican, its spray and the camera that follows it
const surfer = createSurfer();
scene.add(surfer.group);
const particles = createParticles();
scene.add(particles.mesh);
const spray = createSpray(particles, surfer);
const rig = createRig(camera, surfer);

if (preview) {
  waveMesh.visible = waveDepth.visible = oceanMesh.visible = false;
  const floor = new THREE.Mesh(new THREE.CircleGeometry(30, 48), new THREE.MeshStandardMaterial({ color: 0x8a8f94, roughness: 0.9 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.06;
  floor.receiveShadow = true;
  scene.add(floor);
}

// ---- post: bloom, SMAA, tone mapping, grade
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType }));
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.22, 0.6, 1.0));
composer.addPass(new SMAAPass());
composer.addPass(new OutputPass());
const grade = createGradePass();
composer.addPass(grade);

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setPixelRatio(pixelRatio);
  renderer.setSize(w, h);
  composer.setPixelRatio(pixelRatio);
  composer.setSize(w, h);
  grade.uniforms.uRes.value.set(w * pixelRatio, h * pixelRatio);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

function placeCamera(t, dt) {
  const num = (key) => params.get(key).split(",").map(Number);
  if (preview) {
    const az = (parseFloat(params.get("az") || "30") * Math.PI) / 180;
    const el = (parseFloat(params.get("el") || "10") * Math.PI) / 180;
    const d = parseFloat(params.get("d") || "3.4");
    const ty = parseFloat(params.get("ty") || "0.5");
    camera.position.set(d * Math.cos(el) * Math.cos(az), ty + d * Math.sin(el), d * Math.cos(el) * Math.sin(az));
    camera.lookAt(0, ty, 0);
  } else if (params.has("rel")) {
    const v = num("rel");
    const p = surfer.state.pos;
    camera.position.set(p.x + v[0], p.y + v[1], p.z + v[2]);
    camera.lookAt(p.x + (v[4] || 0), p.y + (v[5] || 0.6), p.z + (v[6] || 0));
    camera.fov = v[3] || 40;
    camera.updateProjectionMatrix();
  } else if (params.has("cam")) {
    const v = num("cam");
    camera.position.set(v[0], v[1], v[2]);
    camera.lookAt(v[3], v[4], v[5]);
    camera.fov = v[6] || camera.fov;
    camera.updateProjectionMatrix();
  } else rig.update(t, dt);
}

// one step of the world
function simulate(t, dt) {
  water.uniforms.uTime.value = t;
  grade.uniforms.uTime.value = t;
  if (preview) {
    surfer.pelican.update(t, dt, { roll: 0, accelY: 0, speed: 0.5, crouch: 0.5, camLocal: surfer.pelican.root.worldToLocal(camera.position.clone()) });
    surfer.state.pos.set(0, 0, 0);
  } else {
    surfer.update(t, dt, camera);
    trail.update(t, dt, surfer.state);
    spray.update(t, dt);
  }
  sun.target.position.copy(surfer.state.pos);
  sun.position.copy(surfer.state.pos).addScaledVector(SUN_DIR, 40);
  placeCamera(t, dt);
  sky.update(camera, t);
  gulls.update(t, surfer.state.pos);
}

function render() {
  composer.render();
  renderer.domElement.classList.add("ready");
}

if (fixedT !== null) {
  // deterministic frame: step the world up to t, then draw it
  let t = Math.min(0, fixedT) - 3;
  for (; t < fixedT - 1e-6; t += 1 / 30) simulate(t, 1 / 30);
  simulate(fixedT, 1 / 30);
  render();
  render();
  window.__ready = true;
} else {
  // let the spray and the wake settle before the first frame
  for (let t = -4; t < 0; t += 1 / 30) simulate(t, 1 / 30);

  // hold the frame rate on slower machines by trading resolution
  let last = performance.now();
  let avg = 16;
  let frames = 0;
  let clock = 0;
  const loop = (now) => {
    const ms = Math.min(now - last, 100);
    last = now;
    avg += (ms - avg) * 0.08;
    const dt = Math.min(ms / 1000, 1 / 20);
    clock += dt;
    simulate(clock, dt);
    render();
    if (++frames % 30 === 0) {
      let next = pixelRatio;
      if (avg > 21 && pixelRatio > 0.55) next = Math.max(0.55, pixelRatio * 0.88);
      else if (avg < 13 && pixelRatio < maxPixelRatio) next = Math.min(maxPixelRatio, pixelRatio * 1.1);
      if (Math.abs(next - pixelRatio) > 0.01) {
        pixelRatio = next;
        resize();
      }
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}
