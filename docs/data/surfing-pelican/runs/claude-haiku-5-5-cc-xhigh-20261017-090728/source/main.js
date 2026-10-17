import * as THREE from "three";
import { createOcean } from "./ocean.js";
import { createSurfer } from "./surfer.js";

const HORIZON = "#bfe6f7";

// Vertical sky gradient, drawn to a canvas so no image file is needed.
function createSkyTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 2;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, "#3a8ccf");
  gradient.addColorStop(0.6, HORIZON);
  gradient.addColorStop(1, "#e9f7fb");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const container = document.getElementById("scene");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = createSkyTexture();
scene.fog = new THREE.Fog(HORIZON, 24, 60);

const camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 2.1, 8.5);

scene.add(new THREE.HemisphereLight(0xdff3ff, 0x2a6f8f, 0.8));
scene.add(new THREE.AmbientLight(0xffffff, 0.35));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(6, 10, 8);
scene.add(sun);

const ocean = createOcean();
scene.add(ocean.mesh);

const surfer = createSurfer();
scene.add(surfer.root);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const clock = new THREE.Clock();

renderer.setAnimationLoop(() => {
  const t = clock.getElapsedTime();

  ocean.update(t);
  surfer.update(t);

  // Slow drift keeps the scene from feeling static without any user input.
  camera.position.x = 0.4 * Math.sin(t * 0.12);
  camera.lookAt(0.3, 0.7, 0);

  renderer.render(scene, camera);
});
