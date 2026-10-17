import * as THREE from "three";

// ---------- Setup ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8ecae6);
scene.fog = new THREE.Fog(0x8ecae6, 60, 160);

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);
camera.position.set(0, 8, 22);
camera.lookAt(0, 2, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ---------- Lights ----------
const sun = new THREE.DirectionalLight(0xfff3d6, 2.2);
sun.position.set(20, 30, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
scene.add(sun);
scene.add(new THREE.HemisphereLight(0xbde0fe, 0x0a9396, 0.9));
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

// ---------- Sky sun billboard ----------
const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(8, 32),
  new THREE.MeshBasicMaterial({ color: 0xffd166, fog: false })
);
sunDisc.position.set(-50, 35, -90);
scene.add(sunDisc);

// ---------- Ocean ----------
const oceanGeo = new THREE.PlaneGeometry(400, 400, 120, 120);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x0077b6,
  roughness: 0.35,
  metalness: 0.15,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.receiveShadow = true;
scene.add(ocean);

// wave animation: displace vertices with layered sine waves
const oceanPos = oceanGeo.attributes.position;
const basePos = new Float32Array(oceanPos.array);
function updateOcean(t) {
  for (let i = 0; i < oceanPos.count; i++) {
    const x = basePos[i * 3];
    const z = basePos[i * 3 + 2];
    const h =
      0.45 * Math.sin(x * 0.12 + t * 1.4) +
      0.3 * Math.sin(z * 0.15 + t * 1.1) +
      0.2 * Math.sin((x + z) * 0.08 + t * 0.7);
    oceanPos.setY(i, h);
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// ---------- Wave crest (surfable break near pelican) ----------
// A crescent of foam + a curling lip that sweeps along the break
const foamMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.6,
  transparent: true,
  opacity: 0.9,
});
const foam = new THREE.Mesh(new THREE.TorusGeometry(14, 0.7, 12, 80), foamMat);
foam.rotation.x = Math.PI / 2;
foam.position.set(0, 0.5, -6);
scene.add(foam);

// curling wave lip: partial torus standing upright
const lip = new THREE.Mesh(
  new THREE.TorusGeometry(5, 1.4, 12, 60, Math.PI * 1.2),
  new THREE.MeshStandardMaterial({
    color: 0x48cae4,
    roughness: 0.3,
    transparent: true,
    opacity: 0.85,
  })
);
lip.position.set(0, 3.5, -12);
lip.rotation.y = Math.PI / 2;
scene.add(lip);

// ---------- Pelican ----------
const pelican = new THREE.Group();

const bodyMat = new THREE.MeshStandardMaterial({
  color: 0xfdfcdc,
  roughness: 0.8,
});
const beakMat = new THREE.MeshStandardMaterial({ color: 0xf4a261, roughness: 0.6 });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8 });

const body = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), bodyMat);
body.scale.set(1.35, 1, 1);
body.castShadow = true;
pelican.add(body);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.45, 20, 16), bodyMat);
head.position.set(1.1, 1.0, 0);
head.castShadow = true;
pelican.add(head);

const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.3, 1.1, 12), bodyMat);
neck.position.set(0.75, 0.55, 0);
neck.rotation.z = -0.5;
pelican.add(neck);

// pouch + beak
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.28, 16, 12), beakMat);
pouch.scale.set(1.6, 0.9, 0.8);
pouch.position.set(1.5, 0.72, 0);
pelican.add(pouch);
const upperBeak = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.7, 10), beakMat);
upperBeak.rotation.z = -Math.PI / 2;
upperBeak.position.set(1.9, 0.88, 0);
pelican.add(upperBeak);

// eye
const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), darkMat);
eye.position.set(1.25, 1.15, 0.3);
pelican.add(eye);
const eye2 = eye.clone();
eye2.position.z = -0.3;
pelican.add(eye2);

// tail
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.4, 1.2, 10), bodyMat);
tail.rotation.z = Math.PI / 2 + 0.35;
tail.position.set(-1.5, 0.25, 0);
pelican.add(tail);

// wings
function makeWing(side) {
  const wing = new THREE.Group();
  const inner = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.12, 0.55), bodyMat);
  inner.position.x = side * 0.55;
  inner.castShadow = true;
  wing.add(inner);
  const outer = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.1, 0.42), bodyMat);
  outer.position.set(side * 1.45, 0.05, 0);
  outer.rotation.z = side * -0.25;
  outer.castShadow = true;
  wing.add(outer);
  const tip = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.08, 0.3), darkMat);
  tip.position.set(side * 2.1, 0.15, 0);
  tip.rotation.z = side * -0.6;
  wing.add(tip);
  wing.position.set(0, 0.4, 0);
  return wing;
}
const leftWing = makeWing(1);
const rightWing = makeWing(-1);
pelican.add(leftWing, rightWing);

// webbed feet
function makeFoot(z) {
  const foot = new THREE.Group();
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.5, 8), beakMat);
  leg.position.y = -0.25;
  foot.add(leg);
  const web = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.05, 0.3), beakMat);
  web.position.y = -0.5;
  foot.add(web);
  foot.position.set(0.2, -0.85, z);
  return foot;
}
const footL = makeFoot(0.3);
const footR = makeFoot(-0.3);
pelican.add(footL, footR);

pelican.position.set(0, 4.5, 4);
scene.add(pelican);

// ---------- Surfboard ----------
const board = new THREE.Mesh(
  new THREE.SphereGeometry(1.6, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2),
  new THREE.MeshStandardMaterial({ color: 0xe76f51, roughness: 0.4 })
);
board.scale.set(1, 0.12, 0.35);
board.castShadow = true;
const boardGroup = new THREE.Group();
boardGroup.add(board);
// stripe
const stripe = new THREE.Mesh(
  new THREE.BoxGeometry(3.0, 0.05, 0.08),
  new THREE.MeshStandardMaterial({ color: 0xffe8d6 })
);
stripe.position.y = 0.02;
boardGroup.add(stripe);
boardGroup.position.set(0, 1.6, 4);
scene.add(boardGroup);

pelican.position.y = 2.1;
pelican.position.z = 4;

// ---------- Particles: spray ----------
const sprayCount = 160;
const sprayGeo = new THREE.BufferGeometry();
const sprayPositions = new Float32Array(sprayCount * 3);
const sprayVel = new Float32Array(sprayCount * 3);
for (let i = 0; i < sprayCount; i++) {
  sprayPositions[i * 3] = (Math.random() - 0.5) * 6;
  sprayPositions[i * 3 + 1] = Math.random() * 3;
  sprayPositions[i * 3 + 2] = 3 + (Math.random() - 0.5) * 3;
  sprayVel[i * 3] = (Math.random() - 0.5) * 2;
  sprayVel[i * 3 + 1] = Math.random() * 3 + 1;
  sprayVel[i * 3 + 2] = (Math.random() - 0.5) * 2;
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
const spray = new THREE.Points(
  sprayGeo,
  new THREE.PointsMaterial({ color: 0xffffff, size: 0.18, transparent: true, opacity: 0.85 })
);
scene.add(spray);

// ---------- Animation loop ----------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  updateOcean(t);

  // pelican rides: gentle bob + sway, carve along the wave
  const bob = Math.sin(t * 2.0) * 0.25 + Math.sin(t * 3.3) * 0.1;
  pelican.position.y = 2.15 + bob;
  pelican.position.x = Math.sin(t * 0.7) * 2.2;
  pelican.rotation.z = Math.sin(t * 0.7 + 0.6) * 0.18;
  pelican.rotation.y = Math.sin(t * 0.7) * 0.25;
  pelican.rotation.x = Math.cos(t * 2.0) * 0.08;

  // board follows pelican
  boardGroup.position.x = pelican.position.x;
  boardGroup.position.y = 1.55 + Math.sin(t * 2.0 - 0.3) * 0.18;
  boardGroup.rotation.z = pelican.rotation.z * 0.8;
  boardGroup.rotation.y = pelican.rotation.y * 0.5;

  // wing flapping
  const flap = Math.sin(t * 5) * 0.55;
  leftWing.rotation.z = 0.15 + flap;
  rightWing.rotation.z = -0.15 - flap;

  // head looks around slightly
  head.rotation.y = Math.sin(t * 0.9) * 0.25;

  // foam ring pulses
  foam.rotation.z = t * 0.4;
  foam.scale.setScalar(1 + Math.sin(t * 1.6) * 0.03);
  lip.rotation.x = Math.sin(t * 0.9) * 0.15;
  lip.scale.setScalar(1 + Math.sin(t * 1.3) * 0.05);

  // spray particles: rise, drift, reset
  for (let i = 0; i < sprayCount; i++) {
    let y = sprayPositions[i * 3 + 1] + sprayVel[i * 3 + 1] * 0.016;
    sprayPositions[i * 3] += sprayVel[i * 3] * 0.016 + Math.sin(t * 2 + i) * 0.01;
    sprayPositions[i * 3 + 2] += sprayVel[i * 3 + 2] * 0.016;
    sprayPositions[i * 3 + 1] = y;
    if (y > 6) {
      sprayPositions[i * 3] = pelican.position.x + (Math.random() - 0.5) * 3;
      sprayPositions[i * 3 + 1] = 0;
      sprayPositions[i * 3 + 2] = 3.5 + (Math.random() - 0.5) * 2;
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // camera drifts slowly for cinematic feel
  camera.position.x = Math.sin(t * 0.15) * 4;
  camera.position.y = 8 + Math.sin(t * 0.25) * 1.5;
  camera.lookAt(pelican.position.x * 0.5, 2.5, 2);

  renderer.render(scene, camera);
}
animate();

// ---------- Resize ----------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
