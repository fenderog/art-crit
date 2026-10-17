import * as THREE from "three";
import { createSurfer } from "./pelican.js";
import { createOcean } from "./ocean.js";

// Non-interactive animated scene: no controls or input handlers. The camera
// sways on its own and the pelican carves the same wave in an endless loop.

const container = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe9ec, 26, 62);

const camera = new THREE.PerspectiveCamera(
  44, window.innerWidth / window.innerHeight, 0.1, 160);
camera.position.set(1.2, 2.9, 7.8);

// warm afternoon light
const sunLight = new THREE.DirectionalLight(0xffe2b0, 2.6);
sunLight.position.set(-9, 11, 6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10;
sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10;
sunLight.shadow.camera.bottom = -6;
sunLight.shadow.camera.far = 40;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
scene.add(new THREE.HemisphereLight(0xbfe6f2, 0x2e7d8c, 0.95));
const fill = new THREE.DirectionalLight(0xdff4ff, 0.5);
fill.position.set(7, 4, 9);
scene.add(fill);

const ocean = createOcean();
scene.add(ocean.group);
const surfer = createSurfer();
scene.add(surfer.group);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// gentler motion for viewers who prefer it
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const speed = reduced ? 0.45 : 1;
const sway = reduced ? 0.3 : 1;

const clock = new THREE.Clock();
let elapsed = 0;
const lookTarget = new THREE.Vector3();

renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05) * speed;
  elapsed += dt;
  const t = elapsed;

  surfer.update(t, dt);
  ocean.update(t, dt);

  // slow cinematic sway, always framing the pelican
  const p = surfer.group.position;
  camera.position.set(
    p.x * 0.45 + 1.1 + Math.sin(t * 0.11) * 0.9 * sway,
    2.9 + Math.sin(t * 0.17) * 0.3 * sway,
    7.8 + Math.sin(t * 0.07) * 0.5 * sway);
  lookTarget.set(p.x * 0.8, p.y + 1.5, p.z);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
});
