import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

import { createSky, createHeadland } from './src/sky.js';
import { createOcean } from './src/ocean.js';
import { Surfer } from './src/surfer.js';
import { Spray } from './src/spray.js';
import { Trail } from './src/trail.js';
import { Flock } from './src/flock.js';
import { CameraRig } from './src/camera.js';

// ---------------------------------------------------------------- renderer
const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 6000);

// ---------------------------------------------------------------- sunset
const sunDir = new THREE.Vector3(-0.3, 0.17, -0.94).normalize();
const shared = {
  uTime: { value: 0 },
  uDisc: { value: 1 },
  uSunDir: { value: sunDir },
  uSunColor: { value: new THREE.Color('#ffbd7a').multiplyScalar(1.25) },
  uSkyZenith: { value: new THREE.Color('#1c2a5e') },
  uSkyMid: { value: new THREE.Color('#c06c8a') },
  uSkyHorizon: { value: new THREE.Color('#ff9a62') },
  uCloudLit: { value: new THREE.Color('#ffb27e') },
  uCloudDark: { value: new THREE.Color('#584669') },
};

const sky = createSky(shared);
scene.add(sky);

// image based lighting from the same sky (without the sun disc)
const pmrem = new THREE.PMREMGenerator(renderer);
const envScene = new THREE.Scene();
envScene.add(createSky(shared));
shared.uDisc.value = 0;
const envRT = pmrem.fromScene(envScene, 0, 0.1, 6000);
shared.uDisc.value = 1;
scene.environment = envRT.texture;
scene.environmentIntensity = 0.75;
pmrem.dispose();

scene.fog = new THREE.FogExp2(new THREE.Color('#e9a48a'), 0.0045);
scene.add(createHeadland(new THREE.Color('#8a6274')));

const sun = new THREE.DirectionalLight(new THREE.Color('#ffcf9e'), 2.8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -2.2;
sun.shadow.camera.right = 2.2;
sun.shadow.camera.top = 2.2;
sun.shadow.camera.bottom = -2.2;
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 40;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.015;
sun.shadow.radius = 3;
scene.add(sun, sun.target);

// cool fill from the open sky behind the camera
const FILL_DIR = new THREE.Vector3(0.3, 0.8, 1);
const fill = new THREE.DirectionalLight(new THREE.Color('#9fb6ff'), 0.9);
scene.add(fill, fill.target);

// ---------------------------------------------------------------- world
const ocean = createOcean(shared);
scene.add(ocean);

const surfer = new Surfer();
scene.add(surfer.group);

const spray = new Spray(shared);
scene.add(spray.group);

const trail = new Trail(shared);
scene.add(trail.mesh);

const flock = new Flock();
scene.add(flock.group);

const rig = new CameraRig(camera);

// ---------------------------------------------------------------- post
const rt = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.3, 0.45, 1.1);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const grade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uAspect: { value: 1 } },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uAspect;
    varying vec2 vUv;
    void main() {
      vec4 c = texture2D(tDiffuse, vUv);
      vec2 p = (vUv - 0.5) * vec2(uAspect, 1.0);
      float vig = smoothstep(1.15, 0.35, length(p));
      c.rgb *= mix(0.72, 1.0, vig);
      c.rgb = mix(c.rgb, c.rgb * vec3(1.03, 0.99, 0.95), 0.6);
      gl_FragColor = c;
    }
  `,
});
composer.addPass(grade);

// resolution scale adapts to keep the frame rate smooth on slower GPUs
const maxRatio = Math.min(window.devicePixelRatio, 2);
let pixelRatio = Math.min(maxRatio, 1.5);
let ratioCeiling = maxRatio;
let frameAcc = 0;
let frameCount = 0;

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const pr = pixelRatio;
  renderer.setPixelRatio(pr);
  renderer.setSize(w, h);
  composer.setPixelRatio(pr);
  composer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  grade.uniforms.uAspect.value = w / h;
}
window.addEventListener('resize', resize);
resize();

// ---------------------------------------------------------------- loop
// time wraps every ~2 hours (a multiple of the camera loop) so shader noise
// coordinates never lose float precision
const WRAP = 52 * 138;
let t = 0;

function step(dt) {
  shared.uTime.value = t;
  surfer.update(t, dt);
  trail.update(t, dt, surfer);
  spray.update(t, dt, surfer);
  flock.update(t);
}

// pre-roll so spray and the carve line are already in the air on the first frame
t = -3;
for (let i = 0; i < 90; i++) {
  step(1 / 30);
  t += 1 / 30;
}
t = 0;

let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, Math.max(0, (now - last) / 1000));
  last = now;
  t = (t + dt) % WRAP;
  step(dt);
  rig.update(t, dt, surfer.pos);
  sky.position.copy(camera.position);
  spray.setScale(renderer.domElement.height / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)));

  sun.target.position.copy(surfer.pos);
  sun.position.copy(surfer.pos).addScaledVector(sunDir, 20);
  fill.target.position.copy(surfer.pos);
  fill.position.copy(surfer.pos).addScaledVector(FILL_DIR, 10);

  composer.render();

  frameAcc += dt;
  frameCount++;
  if (frameAcc > 1.5) {
    const avg = frameAcc / frameCount;
    let next = pixelRatio;
    if (avg > 1 / 40) {
      next = Math.max(0.6, pixelRatio - 0.25);
      ratioCeiling = next; // never climb back to a level that was too slow
    } else if (avg < 1 / 58) {
      next = Math.min(ratioCeiling, pixelRatio + 0.25);
    }
    if (next !== pixelRatio) {
      pixelRatio = next;
      resize();
    }
    frameAcc = 0;
    frameCount = 0;
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
