import * as THREE from "three";
import { Ocean } from "./ocean.js";
import { Pelican } from "./pelican.js";
import { Spray } from "./spray.js";
import { waveHeight, waveSlopeX, waveSlopeZ } from "./waves.js";

// ---- Renderer / scene / camera ----
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("app").appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fd8e8, 34, 95);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  300
);

// ---- Sky dome (vertical gradient shader) ----
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(140, 24, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      top: { value: new THREE.Color(0x2f8fc4) },
      bottom: { value: new THREE.Color(0xcdeef7) },
    },
    vertexShader: `
      varying vec3 vPos;
      void main() {
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 top;
      uniform vec3 bottom;
      varying vec3 vPos;
      void main() {
        float h = clamp(normalize(vPos).y * 0.5 + 0.5, 0.0, 1.0);
        gl_FragColor = vec4(mix(bottom, top, pow(h, 0.8)), 1.0);
      }
    `,
  })
);
sky.frustumCulled = false;
scene.add(sky);

// ---- Lights ----
const hemi = new THREE.HemisphereLight(0xbfe8ff, 0x1a5c74, 1.1);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff3d6, 1.6);
sun.position.set(-8, 12, 6);
scene.add(sun);

const ambient = new THREE.AmbientLight(0x88aacc, 0.35);
scene.add(ambient);

// ---- Sun disc ----
const sunDisc = new THREE.Mesh(
  new THREE.SphereGeometry(4, 20, 14),
  new THREE.MeshBasicMaterial({ color: 0xfff2b8, fog: false })
);
sunDisc.position.set(-46, 26, -70);
scene.add(sunDisc);

const sunGlow = new THREE.Mesh(
  new THREE.SphereGeometry(6.2, 20, 14),
  new THREE.MeshBasicMaterial({
    color: 0xffe9a0,
    transparent: true,
    opacity: 0.35,
    fog: false,
  })
);
sunGlow.position.copy(sunDisc.position);
scene.add(sunGlow);

// ---- Clouds (drifting puffs of spheres) ----
const cloudMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 1,
  flatShading: true,
});
const clouds = [];
for (let i = 0; i < 9; i++) {
  const cloud = new THREE.Group();
  const puffs = 3 + Math.floor(Math.random() * 3);
  for (let j = 0; j < puffs; j++) {
    const r = 1.1 + Math.random() * 1.4;
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), cloudMat);
    puff.position.set(j * 1.6 - puffs * 0.8, Math.random() * 0.7, Math.random() * 1.2);
    puff.scale.y = 0.55;
    cloud.add(puff);
  }
  const a = Math.random() * Math.PI * 2;
  const d = 40 + Math.random() * 35;
  cloud.position.set(Math.cos(a) * d, 14 + Math.random() * 12, Math.sin(a) * d);
  cloud.userData.speed = 0.25 + Math.random() * 0.4;
  scene.add(cloud);
  clouds.push(cloud);
}

// ---- World ----
const ocean = new Ocean();
scene.add(ocean.mesh);

const pelican = new Pelican();
scene.add(pelican.group);

const spray = new Spray();
scene.add(spray.points);

// Distant gulls (little gliding triangles).
const gullMat = new THREE.MeshBasicMaterial({ color: 0x35424a, side: THREE.DoubleSide });
const gulls = [];
for (let i = 0; i < 5; i++) {
  const gull = new THREE.Group();
  const wingGeo = new THREE.BufferGeometry();
  wingGeo.setAttribute(
    "position",
    new THREE.BufferAttribute(new Float32Array([0, 0, 0, 1.4, 0.25, 0.4, 1.4, 0.25, -0.4]), 3)
  );
  const left = new THREE.Mesh(wingGeo, gullMat);
  const right = new THREE.Mesh(wingGeo, gullMat);
  right.scale.z = -1;
  gull.add(left, right);
  gull.userData = {
    radius: 16 + Math.random() * 12,
    height: 7 + Math.random() * 6,
    speed: 0.15 + Math.random() * 0.2,
    phase: Math.random() * Math.PI * 2,
    flap: 1.5 + Math.random() * 2,
  };
  scene.add(gull);
  gulls.push(gull);
}

// ---- Animation loop ----
const clock = new THREE.Clock();
let pelicanYaw = 0;

function shortestAngle(from, to) {
  let d = (to - from) % (Math.PI * 2);
  if (d > Math.PI) d -= Math.PI * 2;
  if (d < -Math.PI) d += Math.PI * 2;
  return d;
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Board carves a lazy slalom around the origin.
  const bx = Math.sin(t * 0.22) * 7;
  const bz = Math.cos(t * 0.31) * 5;
  // Velocity of the board along its path.
  const vx = Math.cos(t * 0.22) * 0.22 * 7;
  const vz = -Math.sin(t * 0.31) * 0.31 * 5;
  // The pelican model faces +X; aim it along its velocity.
  const targetYaw = Math.atan2(-vz, vx);
  pelicanYaw += (shortestAngle(pelicanYaw, targetYaw)) * Math.min(1, dt * 2.5);

  const h = waveHeight(bx, bz, t);
  const sx = waveSlopeX(bx, bz, t);
  const sz = waveSlopeZ(bx, bz, t);

  pelican.group.position.x = bx;
  pelican.group.position.z = bz;
  pelican.group.rotation.y = pelicanYaw;
  pelican.update(t, h, sx, sz);

  spray.update(dt, bx, bz, vx >= 0 ? 1 : -1, t);

  ocean.update(t);

  // Clouds drift slowly.
  for (const c of clouds) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 85) c.position.x = -85;
  }

  // Gulls circle overhead, wings flapping.
  for (const g of gulls) {
    const u = g.userData;
    const a = t * u.speed + u.phase;
    g.position.set(Math.cos(a) * u.radius, u.height + Math.sin(t * 1.3 + u.phase) * 0.6, Math.sin(a) * u.radius);
    g.rotation.y = -a + Math.PI / 2;
    g.children[0].rotation.x = Math.sin(t * u.flap) * 0.5;
    g.children[1].rotation.x = -Math.sin(t * u.flap) * 0.5;
  }

  // Camera slowly orbits, always watching the pelican.
  const camA = t * 0.11;
  const camDist = 10.5;
  camera.position.set(
    pelican.group.position.x + Math.cos(camA) * camDist,
    4.2 + Math.sin(t * 0.4) * 0.6,
    pelican.group.position.z + Math.sin(camA) * camDist
  );
  camera.lookAt(pelican.group.position.x, pelican.group.position.y + 1.2, pelican.group.position.z);

  // Keep sky dome + sun centred on the camera (infinite backdrop).
  sky.position.copy(camera.position);
  sunDisc.position.set(
    camera.position.x - 46,
    camera.position.y + 22,
    camera.position.z - 70
  );
  sunGlow.position.copy(sunDisc.position);

  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
