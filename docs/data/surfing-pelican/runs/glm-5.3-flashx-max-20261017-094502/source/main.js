import * as THREE from "three";
import { createOcean } from "./ocean.js";
import { createRider } from "./rider.js";
import { createSky } from "./sky.js";

// ---- renderer / scene / camera --------------------------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById("app").appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfeef7, 55, 240);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 900);
camera.position.set(0, 6.2, 13.5);

// ---- lights ----------------------------------------------------------------
scene.add(new THREE.HemisphereLight(0xbfe3ff, 0x0c6e86, 0.9));

const sunLight = new THREE.DirectionalLight(0xfff1cf, 1.5);
sunLight.position.set(-38, 29, -75); // matches the visible sun
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(1024, 1024);
sunLight.shadow.camera.near = 30;
sunLight.shadow.camera.far = 170;
sunLight.shadow.camera.left = -14;
sunLight.shadow.camera.right = 14;
sunLight.shadow.camera.top = 14;
sunLight.shadow.camera.bottom = -14;
sunLight.shadow.bias = -0.0006;
sunLight.shadow.camera.updateProjectionMatrix();
scene.add(sunLight);

// ---- scene content ----------------------------------------------------------
const sky = createSky();
scene.add(sky.group);

const ocean = createOcean();
scene.add(ocean.mesh);

const rider = createRider();
scene.add(rider.group);

// ---- animation loop ---------------------------------------------------------
const clock = new THREE.Clock();

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  ocean.update(t);
  rider.update(t);
  sky.update(t, dt);

  // slow cinematic camera sway (no user interaction)
  camera.position.x = Math.sin(t * 0.22) * 1.4;
  camera.position.y = 6.2 + Math.sin(t * 0.4) * 0.35;
  camera.lookAt(0, 2.2, 0);

  renderer.render(scene, camera);
});

// ---- resize -----------------------------------------------------------------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
