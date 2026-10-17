import * as THREE from "three";

import { createOcean, OCEAN_COLORS } from "./src/ocean.js";
import { createSky } from "./src/sky.js";
import { createPelican } from "./src/pelican.js";
import { createBoard } from "./src/board.js";
import { createSurfer } from "./src/surfer.js";
import { createSpray, createWake, createContactShadow, createMist } from "./src/foam.js";
import { createGulls } from "./src/gulls.js";
import { createCameraRig } from "./src/camera.js";
import {
  featherBumpTexture,
  softDotTexture,
  blobShadowTexture,
  speckleTexture,
} from "./src/textures.js";

/** Low sun out of the north-west: golden, backlit, long glitter path. */
const SUN_DIR = new THREE.Vector3(-0.5248, 0.225, -0.8264).normalize();
const START_TIME = 21.7;

function main() {
  const host = document.getElementById("app");
  const curtain = document.getElementById("curtain");
  const fallback = document.getElementById("fallback");

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
      stencil: false,
    });
  } catch (err) {
    if (fallback) fallback.style.display = "grid";
    if (curtain) curtain.classList.add("up");
    return;
  }
  if (!renderer || !renderer.getContext()) {
    if (fallback) fallback.style.display = "grid";
    if (curtain) curtain.classList.add("up");
    return;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute("aria-hidden", "true");
  host.appendChild(renderer.domElement);

  /* ---- scene ------------------------------------------------------- */
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(OCEAN_COLORS.fog.getHex(), 0.0072);
  const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.18, 4200);
  camera.position.set(9, 3.2, 11);

  /* ---- light -------------------------------------------------------- */
  const sun = new THREE.DirectionalLight(new THREE.Color("#ffd8a6"), 4.3);
  sun.position.copy(SUN_DIR).multiplyScalar(160);
  scene.add(sun);

  const hemi = new THREE.HemisphereLight(
    new THREE.Color("#a8c9f2"),
    new THREE.Color("#0d5f6c"),
    1.0
  );
  scene.add(hemi);

  const fill = new THREE.DirectionalLight(new THREE.Color("#a8c4ea"), 1.15);
  fill.position.set(60, 42, 85);
  scene.add(fill);

  // teal bounce off the water onto the belly of the bird
  const bounce = new THREE.DirectionalLight(new THREE.Color("#5fd8c6"), 0.34);
  bounce.position.set(-6, -22, 10);
  scene.add(bounce);

  /* ---- world -------------------------------------------------------- */
  const textures = {
    feather: featherBumpTexture(),
    dot: softDotTexture(),
    blob: blobShadowTexture(),
    speckle: speckleTexture(),
  };

  const sky = createSky();
  scene.add(sky.mesh);

  const ocean = createOcean();
  ocean.uniforms.uSunDir.value.copy(SUN_DIR);
  ocean.uniforms.uSunColor.value.set("#ffd9a3");
  scene.add(ocean.mesh);

  const gulls = createGulls(7);
  scene.add(gulls.group);

  const mist = createMist({ texture: textures.dot, count: 24 });
  scene.add(mist.points);

  const spray = createSpray({ texture: textures.dot, count: 760 });
  scene.add(spray.points);

  const wake = createWake({ length: 132, interval: 0.04 });
  scene.add(wake.mesh);

  const shadow = createContactShadow({ texture: textures.blob });
  scene.add(shadow.mesh);

  const rig = new THREE.Group();
  scene.add(rig);
  const board = createBoard({ speckleTex: textures.speckle });
  rig.add(board.group);
  const pelican = createPelican({ featherTex: textures.feather });
  const surfer = createSurfer({ rig, pelican, spray, wake, shadow });

  const camRig = createCameraRig(camera);

  /* ---- resize ------------------------------------------------------- */
  function resize() {
    const w = Math.max(1, window.innerWidth);
    const h = Math.max(1, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    spray.setScale(h * renderer.getPixelRatio(), camera.fov);
    mist.setScale(h * renderer.getPixelRatio(), camera.fov);
  }
  window.addEventListener("resize", resize);
  window.addEventListener("orientationchange", resize);
  resize();

  /* ---- loop --------------------------------------------------------- */
  const reduced =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const timeScale = reduced ? 0.45 : 1;

  let last = performance.now() / 1000;
  let t = START_TIME;
  let running = true;
  let frames = 0;

  // read-only peek for debugging / harnesses (never used by the scene itself)
  try {
    Object.defineProperty(window, "__surf", {
      value: { get t() { return t; }, get frames() { return frames; }, get state() { return surfer.state; } },
      configurable: true,
    });
  } catch (_) {
    /* sandboxed frames may refuse; ignore */
  }

  renderer.domElement.addEventListener("webglcontextlost", (e) => {
    e.preventDefault();
    running = false;
  });
  renderer.domElement.addEventListener("webglcontextrestored", () => {
    running = true;
    last = performance.now() / 1000;
  });

  function frame() {
    const now = performance.now() / 1000;
    let dt = now - last;
    last = now;
    dt = Math.min(Math.max(dt, 0.0005), 0.05);
    if (running) t += dt * timeScale;

    frames++;
    const st = surfer.state;
    surfer.update(t, dt * timeScale);

    ocean.update(t, dt, SUN_DIR);
    ocean.setSplash(
      rig.position.x,
      rig.position.z,
      0.3 + Math.min(0.45, st.speed * 0.28)
    );
    sky.update(t, SUN_DIR);
    gulls.update(t);
    mist.update(dt * timeScale, t);
    camRig.update(t, dt, rig.position, {
      speed: st.speed,
      forward: st.forward,
    });

    renderer.render(scene, camera);
  }

  renderer.setAnimationLoop(frame);

  requestAnimationFrame(() => {
    if (curtain) curtain.classList.add("up");
  });
}

main();
