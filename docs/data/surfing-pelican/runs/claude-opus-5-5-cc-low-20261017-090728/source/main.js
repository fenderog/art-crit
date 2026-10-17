import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xf3b58a, 40, 160);

// Sky gradient dome
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(300, 32, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: `varying vec3 p; void main(){p=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `varying vec3 p; void main(){float h=normalize(p).y;
      vec3 c=mix(vec3(1.,.72,.5),vec3(.25,.45,.8),smoothstep(0.,.5,h));
      c=mix(c,vec3(1.,.55,.35),smoothstep(.1,-.05,h));gl_FragColor=vec4(c,1.);}`,
  })
);
scene.add(sky);

// Sun
const sun = new THREE.Mesh(new THREE.CircleGeometry(14, 32), new THREE.MeshBasicMaterial({ color: 0xfff1c0, fog: false }));
sun.position.set(-60, 22, -250);
scene.add(sun);

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 1000);
scene.add(new THREE.HemisphereLight(0xffe0c0, 0x1d5a80, 1.2));
const dir = new THREE.DirectionalLight(0xffd2a0, 2.2);
dir.position.set(-20, 30, -10);
dir.castShadow = true;
dir.shadow.mapSize.set(1024, 1024);
Object.assign(dir.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10 });
scene.add(dir);

// Ocean
const oceanGeo = new THREE.PlaneGeometry(400, 400, 200, 200);
oceanGeo.rotateX(-Math.PI / 2);
const basePos = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({
  color: 0x1f7fa8, roughness: 0.25, metalness: 0.1, flatShading: true,
}));
ocean.receiveShadow = true;
scene.add(ocean);

function waveHeight(x, z, t) {
  // Big swell moving in +x, with surfer riding its face
  const swell = 2.2 * Math.exp(-Math.pow((x - 0) / 9, 2) * 0.6) * (1 + 0.15 * Math.sin(z * 0.08 + t));
  return swell * 0 + // swell moves with surfer in local frame; we scroll the world instead
    2.4 * Math.exp(-Math.pow(x / 8, 2)) * (0.9 + 0.1 * Math.sin(z * 0.1 + t * 0.7)) +
    0.35 * Math.sin(x * 0.35 + t * 1.6) +
    0.25 * Math.sin(z * 0.45 - t * 1.2 + x * 0.1) +
    0.12 * Math.sin((x + z) * 1.1 + t * 2.5);
}

// Surfboard
const surfer = new THREE.Group();
scene.add(surfer);
const board = new THREE.Mesh(
  new THREE.SphereGeometry(1, 32, 12),
  new THREE.MeshStandardMaterial({ color: 0xff6b3d, roughness: 0.4 })
);
board.scale.set(0.55, 0.08, 2.4);
board.castShadow = true;
surfer.add(board);
const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.17, 4.2), new THREE.MeshStandardMaterial({ color: 0xffffff }));
surfer.add(stripe);

// Pelican
const white = new THREE.MeshStandardMaterial({ color: 0xf2efe6, roughness: 0.8 });
const grey = new THREE.MeshStandardMaterial({ color: 0x8a8f96, roughness: 0.8 });
const beakMat = new THREE.MeshStandardMaterial({ color: 0xf2a93b, roughness: 0.5 });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xe88a4a, roughness: 0.6 });
const legMat = new THREE.MeshStandardMaterial({ color: 0xe0782a });
const dark = new THREE.MeshStandardMaterial({ color: 0x111111 });
const mesh = (g, m) => { const o = new THREE.Mesh(g, m); o.castShadow = true; return o; };

const pelican = new THREE.Group();
pelican.rotation.y = Math.PI / 2; // stand sideways on board
surfer.add(pelican);

const legs = [];
for (const s of [-1, 1]) {
  const leg = new THREE.Group();
  leg.position.set(0, 0.1, s * 0.35);
  const upper = mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.9), legMat);
  upper.position.y = 0.45;
  const foot = mesh(new THREE.BoxGeometry(0.35, 0.04, 0.3), legMat);
  foot.position.set(0.08, 0, 0);
  leg.add(upper, foot);
  pelican.add(leg);
  legs.push(leg);
}

const body = new THREE.Group();
body.position.y = 1.3;
pelican.add(body);
const torso = mesh(new THREE.SphereGeometry(0.6, 24, 16), white);
torso.scale.set(1.35, 0.95, 0.9);
body.add(torso);
const tail = mesh(new THREE.ConeGeometry(0.3, 0.6, 12), grey);
tail.rotation.z = Math.PI / 2 + 0.3;
tail.position.set(-0.9, 0.05, 0);
body.add(tail);

const neck = new THREE.Group();
neck.position.set(0.55, 0.35, 0);
body.add(neck);
const neckMesh = mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.9, 12), white);
neckMesh.position.y = 0.4;
neckMesh.rotation.z = -0.2;
neck.add(neckMesh);
const head = new THREE.Group();
head.position.set(0.1, 0.9, 0);
neck.add(head);
head.add(mesh(new THREE.SphereGeometry(0.26, 16, 12), white));
const crest = mesh(new THREE.SphereGeometry(0.12, 8, 8), new THREE.MeshStandardMaterial({ color: 0xf6e27a }));
crest.position.set(-0.05, 0.22, 0);
head.add(crest);
for (const s of [-1, 1]) {
  const eye = mesh(new THREE.SphereGeometry(0.045, 8, 8), dark);
  eye.position.set(0.12, 0.07, s * 0.21);
  head.add(eye);
}
const beak = mesh(new THREE.ConeGeometry(0.09, 1.3, 8), beakMat);
beak.rotation.z = -Math.PI / 2 - 0.15;
beak.position.set(0.8, -0.08, 0);
head.add(beak);
const pouch = mesh(new THREE.SphereGeometry(0.5, 16, 12), pouchMat);
pouch.scale.set(1.05, 0.32, 0.32);
pouch.position.set(0.65, -0.24, 0);
head.add(pouch);

const wings = [];
for (const s of [-1, 1]) {
  const pivot = new THREE.Group();
  pivot.position.set(0.1, 0.25, s * 0.45);
  const wing = mesh(new THREE.BoxGeometry(1.1, 0.06, 1.6), white);
  wing.position.z = s * 0.8;
  const tip = mesh(new THREE.BoxGeometry(0.7, 0.05, 0.8), grey);
  tip.position.set(-0.15, 0, s * 1.9);
  pivot.add(wing, tip);
  body.add(pivot);
  wings.push({ pivot, s });
}

// Spray particles
const SPRAY = 400;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = new Float32Array(SPRAY * 3);
const sprayLife = new Float32Array(SPRAY);
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.15, transparent: true, opacity: 0.85 }));
scene.add(spray);
let sprayIdx = 0;

// Foam crest line
const foamGeo = new THREE.BufferGeometry();
const FOAM = 600;
const foamPos = new Float32Array(FOAM * 3);
foamGeo.setAttribute("position", new THREE.BufferAttribute(foamPos, 3));
const foam = new THREE.Points(foamGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.3, transparent: true, opacity: 0.7 }));
scene.add(foam);

const clock = new THREE.Clock();
function animate() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // Ocean surface
  const p = oceanGeo.attributes.position.array;
  for (let i = 0; i < p.length; i += 3) p[i + 1] = waveHeight(basePos[i], basePos[i + 2], t);
  oceanGeo.attributes.position.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // Surfer carves along the wave face (z) and up/down (x)
  const sz = Math.sin(t * 0.4) * 12;
  const sx = -3.5 + Math.sin(t * 0.9) * 2.2;
  const y = waveHeight(sx, sz, t);
  const e = 0.05;
  const dx = (waveHeight(sx + e, sz, t) - waveHeight(sx - e, sz, t)) / (2 * e);
  const dz = (waveHeight(sx, sz + e, t) - waveHeight(sx, sz - e, t)) / (2 * e);
  surfer.position.set(sx, y + 0.12, sz);
  const heading = Math.cos(t * 0.4) * 0.6 + Math.cos(t * 0.9) * 0.4;
  surfer.rotation.set(0, 0, 0);
  surfer.rotation.order = "YXZ";
  surfer.rotation.y = heading * 0.5;
  surfer.rotation.x = -Math.atan(dz) * 0.8;
  surfer.rotation.z = Math.atan(dx) * 0.8;

  // Pelican balancing
  const bal = Math.sin(t * 2.3);
  body.rotation.z = 0.1 * bal + Math.atan(dx) * -0.4;
  body.rotation.x = 0.12 * Math.sin(t * 1.7);
  body.position.y = 1.3 + 0.06 * Math.sin(t * 4.6);
  legs[0].rotation.x = 0.1 * bal; legs[1].rotation.x = -0.1 * bal;
  neck.rotation.z = 0.15 * Math.sin(t * 1.3);
  head.rotation.z = -0.15 * Math.sin(t * 1.3) + 0.05 * Math.sin(t * 5);
  for (const { pivot, s } of wings) {
    pivot.rotation.x = s * (0.25 + 0.35 * Math.sin(t * 3 + s * 0.6) + 0.15 * bal * s);
  }

  // Spray emission from board tail
  const tailW = new THREE.Vector3(0, 0, -2.2).applyQuaternion(surfer.quaternion).add(surfer.position);
  for (let k = 0; k < 6; k++) {
    const i = sprayIdx++ % SPRAY;
    sprayPos.set([tailW.x + (Math.random() - 0.5) * 0.5, tailW.y, tailW.z + (Math.random() - 0.5) * 0.5], i * 3);
    sprayVel.set([2 + Math.random() * 2, 2 + Math.random() * 3, -1 - Math.random() * 2 + Math.cos(t * 0.4) * -3], i * 3);
    sprayLife[i] = 1;
  }
  for (let i = 0; i < SPRAY; i++) {
    if (sprayLife[i] <= 0) { sprayPos[i * 3 + 1] = -100; continue; }
    sprayLife[i] -= dt;
    sprayVel[i * 3 + 1] -= 9.8 * dt;
    for (let a = 0; a < 3; a++) sprayPos[i * 3 + a] += sprayVel[i * 3 + a] * dt;
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Foam along crest
  for (let i = 0; i < FOAM; i++) {
    const z = -60 + (i / FOAM) * 120;
    const x = 1.5 + Math.sin(i * 12.9898) * 1.2 + Math.sin(t * 2 + i) * 0.2;
    foamPos.set([x, waveHeight(x, z, t) + 0.1 + Math.abs(Math.sin(i * 78.233 + t * 3)) * 0.3, z], i * 3);
  }
  foamGeo.attributes.position.needsUpdate = true;

  // Camera slow orbit tracking surfer
  const ca = -1.9 + Math.sin(t * 0.12) * 0.7;
  camera.position.set(surfer.position.x + Math.cos(ca) * 11, 4.5 + Math.sin(t * 0.2), surfer.position.z + Math.sin(ca) * 11);
  camera.lookAt(surfer.position.x, surfer.position.y + 1.2, surfer.position.z);
  dir.target.position.copy(surfer.position);
  dir.position.set(surfer.position.x - 20, 30, surfer.position.z - 10);
  dir.target.updateMatrixWorld();

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
