import * as THREE from "three";
import { createOcean } from "./ocean.js";
import { createPelican } from "./pelican.js";
import { createSpray } from "./spray.js";
import { createSurfboard, poseSurfboard } from "./surfboard.js";

const HORIZON = 0xcfe9f5;
const ZENITH = 0x3f86d6;
const CAMERA_TARGET = new THREE.Vector3(0.3, 0.8, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
// Fog colour matches the sky's horizon so the far edge of the water dissolves into it.
scene.fog = new THREE.Fog(HORIZON, 14, 50);
scene.add(createSky());

const key = new THREE.DirectionalLight(0xfff1dc, 2.2);
key.position.set(-4, 9, 6);
scene.add(key, new THREE.HemisphereLight(0xdff4ff, 0x1d5a7a, 1.2));

const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 1000);

const ocean = createOcean();
const board = createSurfboard();
const pelican = createPelican();
const spray = createSpray();
board.add(pelican.root);
scene.add(ocean.mesh, board, spray.points);

function createSky() {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      zenith: { value: new THREE.Color(ZENITH) },
      horizon: { value: new THREE.Color(HORIZON) },
    },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform vec3 zenith;
      uniform vec3 horizon;
      varying vec3 vDir;
      void main() {
        float h = clamp(normalize(vDir).y, 0.0, 1.0);
        gl_FragColor = vec4(mix(horizon, zenith, pow(h, 0.5)), 1.0);
        #include <colorspace_fragment>
      }`,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), material);
  sky.renderOrder = -1;
  return sky;
}

function resize() {
  const { innerWidth: width, innerHeight: height } = window;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.fov = camera.aspect < 1 ? 40 / Math.sqrt(camera.aspect) : 40;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

let last = 0;
function frame(ms) {
  const t = ms / 1000;
  const dt = Math.min(t - last, 0.05);
  last = t;

  ocean.update(t);
  poseSurfboard(board, t);
  board.updateMatrixWorld(true);
  pelican.update(t);
  spray.update(dt, t, board);

  camera.position.set(-0.5 + 0.2 * Math.sin(0.12 * t), 1.45 + 0.08 * Math.sin(0.31 * t), 5.6);
  camera.lookAt(CAMERA_TARGET);
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
