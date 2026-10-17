import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3f2);
scene.fog = new THREE.Fog(0xa8dcf5, 35, 90);

const camera = new THREE.PerspectiveCamera(48, innerWidth / innerHeight, 0.1, 200);
camera.position.set(7.5, 3.6, 9);

scene.add(new THREE.HemisphereLight(0xcfeeff, 0x2a7a9a, 1.1));
const sun = new THREE.DirectionalLight(0xfff2cc, 2.2);
sun.position.set(8, 14, 6); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
scene.add(sun);

// Sun disc + clouds
const sunDisc = new THREE.Mesh(new THREE.CircleGeometry(2.2, 32), new THREE.MeshBasicMaterial({ color: 0xfff3a6 }));
sunDisc.position.set(-22, 13, -38); scene.add(sunDisc);
const clouds = new THREE.Group(); scene.add(clouds);
const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
function cloud(x, y, z, s) {
  const g = new THREE.Group();
  [[0,0,0,1.4],[1.4,-.1,0,1],[-1.3,-.15,0,.9],[.4,.5,0,1]].forEach(([a,b,c,r])=>{
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), cloudMat); m.position.set(a,b,c); m.scale.y=.55; g.add(m);
  });
  g.position.set(x,y,z); g.scale.setScalar(s); clouds.add(g);
}
cloud(-14,10,-28,1.4); cloud(10,12,-32,1.8); cloud(22,9,-24,1); cloud(-26,12,-22,1.1);

// Ocean — animated vertices
const waveH = (x, z, t) =>
  Math.sin(x * 0.32 + t * 1.4) * 0.55 + Math.sin(z * 0.45 - t * 1.1) * 0.35 +
  Math.sin((x + z) * 0.18 + t * 0.7) * 0.4;
const oceanGeo = new THREE.PlaneGeometry(90, 70, 90, 70);
oceanGeo.rotateX(-Math.PI / 2);
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({
  color: 0x1290b8, roughness: 0.35, metalness: 0.05, flatShading: true }));
ocean.receiveShadow = true; scene.add(ocean);
const oPos = oceanGeo.attributes.position;
const oBase = oPos.array.slice();

// Big curling wave the pelican rides (translucent barrel wall behind board)
const waveGroup = new THREE.Group(); scene.add(waveGroup);
const barrelGeo = new THREE.CylinderGeometry(2.6, 2.6, 14, 24, 1, true, Math.PI * 0.15, Math.PI * 0.95);
const barrel = new THREE.Mesh(barrelGeo, new THREE.MeshStandardMaterial({
  color: 0x1fb6d9, roughness: 0.25, transparent: true, opacity: 0.82, side: THREE.DoubleSide, flatShading: true }));
barrel.rotation.z = Math.PI / 2; barrel.rotation.y = Math.PI / 2;
barrel.position.set(0, 2.2, -2.2); waveGroup.add(barrel);
// Foam crest
const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
const foams = [];
for (let i = 0; i < 26; i++) {
  const f = new THREE.Mesh(new THREE.SphereGeometry(0.28 + Math.random() * 0.3, 8, 6), foamMat);
  f.position.set(-6.5 + i * 0.52, 4.55 + Math.sin(i) * 0.15, -1.1 + Math.random() * 0.3);
  f.scale.y = 0.6; foams.push(f); waveGroup.add(f);
}

// Materials
const M = {
  white: new THREE.MeshStandardMaterial({ color: 0xf7f3e8, roughness: 0.85 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xffe9b8, roughness: 0.85 }),
  orange: new THREE.MeshStandardMaterial({ color: 0xff8c2e, roughness: 0.6 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xffb03a, roughness: 0.7 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }),
  board: new THREE.MeshStandardMaterial({ color: 0xffd23f, roughness: 0.4 }),
  stripe: new THREE.MeshStandardMaterial({ color: 0xe63946, roughness: 0.4 }),
};
function mesh(geo, mat, x=0,y=0,z=0, parent) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x,y,z);
  m.castShadow = true; if (parent) parent.add(m); return m;
}

// Surfboard + pelican rig
const rig = new THREE.Group(); scene.add(rig);
const board = new THREE.Group(); rig.add(board);
{
  const shape = new THREE.Shape();
  shape.moveTo(0, -1.7); shape.quadraticCurveTo(0.55, -1.2, 0.5, 0.4);
  shape.quadraticCurveTo(0.45, 1.4, 0, 1.85); shape.quadraticCurveTo(-0.45, 1.4, -0.5, 0.4);
  shape.quadraticCurveTo(-0.55, -1.2, 0, -1.7);
  const g = new THREE.ExtrudeGeometry(shape, { depth: 0.09, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.04 });
  g.rotateX(-Math.PI/2);
  mesh(g, M.board, 0, 0, 0, board);
  mesh(new THREE.BoxGeometry(0.18, 0.03, 2.6), M.stripe, 0, 0.1, 0, board);
  const fin = mesh(new THREE.BoxGeometry(0.05, 0.35, 0.4), M.stripe, 0, -0.15, -1.3, board); fin.rotation.x = 0.3;
}

const pelican = new THREE.Group(); pelican.position.y = 0.12; rig.add(pelican);
// Legs + webbed feet planted on board
[-0.28, 0.28].forEach(x => {
  const leg = mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.55, 8), M.dark, x, 0.28, 0, pelican);
  leg.rotation.z = x > 0 ? -0.18 : 0.18;
  const foot = mesh(new THREE.SphereGeometry(0.16, 10, 8), M.orange, x * 1.15, 0.04, 0.1, pelican);
  foot.scale.set(1.1, 0.3, 1.7);
});
// Body — plump ellipsoid, leaning forward
const body = mesh(new THREE.SphereGeometry(0.85, 24, 18), M.white, 0, 1.05, -0.1, pelican);
body.scale.set(0.9, 0.95, 1.25); body.rotation.x = -0.18;
// Tail feathers
for (let i = -1; i <= 1; i++) {
  const t = mesh(new THREE.ConeGeometry(0.14, 0.8, 8), M.dark, i * 0.2, 1.15, -1.15, pelican);
  t.rotation.x = Math.PI / 2 + 0.5; t.rotation.z = i * 0.25;
}
// Neck (S-curve of spheres) + head group for bobbing
const headGroup = new THREE.Group(); headGroup.position.set(0, 1.55, 0.75); pelican.add(headGroup);
const neckPts = [[0,0,0],[0,0.35,0.12],[0,0.7,0.05],[0,1.0,0.2]];
neckPts.forEach(([x,y,z], i) => {
  const n = mesh(new THREE.SphereGeometry(0.26 - i*0.02, 14, 12), M.white, x, y, z, headGroup);
  n.scale.set(1, 1.35, 1);
});
const head = mesh(new THREE.SphereGeometry(0.32, 18, 14), M.cream, 0, 1.25, 0.28, headGroup);
head.scale.set(0.9, 0.9, 1.15);
// Crest tuft
const crest = mesh(new THREE.ConeGeometry(0.12, 0.45, 8), M.cream, 0, 1.58, 0.1, headGroup);
crest.rotation.x = -0.5;
// Eyes
[-0.2, 0.2].forEach(x => mesh(new THREE.SphereGeometry(0.055, 10, 8), M.dark, x, 1.33, 0.52, headGroup));
// Long beak: upper + pouch (pouch inflates in animation)
const upperBeak = mesh(new THREE.ConeGeometry(0.13, 1.5, 10), M.orange, 0, 1.22, 1.15, headGroup);
upperBeak.rotation.x = Math.PI / 2; upperBeak.scale.x = 0.55;
mesh(new THREE.SphereGeometry(0.07, 8, 8), M.stripe, 0, 1.2, 1.9, headGroup);
const pouch = mesh(new THREE.SphereGeometry(0.3, 14, 12), M.pouch, 0, 1.05, 1.05, headGroup);
pouch.scale.set(0.55, 0.6, 2.2);
// Wings — pivoted at shoulders, spread for balance
function wing(side) {
  const g = new THREE.Group(); g.position.set(side * 0.6, 1.45, -0.1); pelican.add(g);
  const w = mesh(new THREE.SphereGeometry(0.9, 16, 10), M.white, side * 0.85, 0, -0.15, g);
  w.scale.set(1.5, 0.18, 0.75);
  const tip = mesh(new THREE.SphereGeometry(0.5, 12, 8), M.dark, side * 1.75, 0, -0.3, g);
  tip.scale.set(1.3, 0.15, 0.6);
  return g;
}
const wingL = wing(-1), wingR = wing(1);

// Spray particles off the board's tail
const N = 260, sprayGeo = new THREE.BufferGeometry();
const sPos = new Float32Array(N * 3), sVel = [];
for (let i = 0; i < N; i++) sVel.push(new THREE.Vector3());
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.13, transparent: true, opacity: 0.9 }));
scene.add(spray);
function resetDrop(i) {
  sPos[i*3] = rig.position.x + (Math.random()-.5)*.5;
  sPos[i*3+1] = rig.position.y + 0.1;
  sPos[i*3+2] = rig.position.z - 1.5;
  sVel[i].set((Math.random()-.5)*1.6, 1.5 + Math.random()*2.2, -2 - Math.random()*2);
}
for (let i = 0; i < N; i++) { resetDrop(i); sPos[i*3+1] += Math.random()*1.5; }

// Wake foam trail (flattened spheres recycled behind board)
const wake = [];
for (let i = 0; i < 18; i++) {
  const f = mesh(new THREE.SphereGeometry(0.35, 8, 6), foamMat, 0, 0, 0, scene);
  f.scale.set(1.4, 0.25, 1); f.castShadow = false; wake.push(f);
}

// Distant gulls (simple V shapes flapping)
const gulls = [];
for (let i = 0; i < 5; i++) {
  const g = new THREE.Group();
  [-1, 1].forEach(s => {
    const w = mesh(new THREE.BoxGeometry(0.7, 0.04, 0.18), M.white, s*0.35, 0, 0, g); w.castShadow=false;
  });
  g.position.set(-18 + i*7, 8 + (i%3)*1.5, -20 - i*2);
  g.userData = { speed: 0.6 + Math.random()*0.5, phase: Math.random()*6 };
  gulls.push(g); scene.add(g);
}

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;

  // Ocean swell
  for (let i = 0; i < oPos.count; i++) {
    const x = oBase[i*3], z = oBase[i*3+2];
    oPos.setY(i, waveH(x, z, t) - 0.6);
  }
  oPos.needsUpdate = true; oceanGeo.computeVertexNormals();

  // Pelican carves side to side, riding up and down the wave face
  const carve = Math.sin(t * 0.55);
  rig.position.x = carve * 2.6;
  rig.position.y = 1.15 + Math.sin(t * 1.4) * 0.35 + Math.sin(t * 0.55 + 1) * 0.25;
  rig.position.z = Math.sin(t * 0.55 + 0.6) * 0.5;
  rig.rotation.z = -carve * 0.22 + Math.sin(t * 1.4) * 0.05;   // lean into turns
  rig.rotation.x = Math.sin(t * 1.4 + 0.5) * 0.09;            // pitch with swell
  rig.rotation.y = -carve * 0.35;                             // steer board
  waveGroup.position.x = rig.position.x * 0.35;
  waveGroup.position.y = Math.sin(t * 1.4) * 0.15;

  // Balance: wings counter-lean and flutter; body crouches; head bobs; pouch sways
  const flutter = Math.sin(t * 6) * 0.06;
  wingL.rotation.z =  0.35 + carve * 0.45 + flutter + Math.sin(t*1.4)*0.08;
  wingR.rotation.z = -0.35 + carve * 0.45 - flutter - Math.sin(t*1.4)*0.08;
  wingL.rotation.x = wingR.rotation.x = Math.sin(t * 2.2) * 0.08;
  pelican.position.y = 0.12 + Math.sin(t * 2.8) * 0.045;
  pelican.rotation.z = -carve * 0.12;
  headGroup.rotation.x = Math.sin(t * 2.8 + 0.4) * 0.12;
  headGroup.rotation.y = Math.sin(t * 0.4) * 0.35;           // looking around
  const inflate = 1 + Math.max(0, Math.sin(t * 0.8)) * 0.35;
  pouch.scale.set(0.55 * inflate, 0.6 * inflate, 2.2);
  crest.rotation.x = -0.5 + Math.sin(t * 3) * 0.15;

  // Foam crest churn
  foams.forEach((f, i) => { f.position.y = 4.55 + Math.sin(t*3 + i*0.7) * 0.14; f.rotation.y += dt; });

  // Spray
  for (let i = 0; i < N; i++) {
    sVel[i].y -= 6 * dt;
    sPos[i*3] += sVel[i].x*dt; sPos[i*3+1] += sVel[i].y*dt; sPos[i*3+2] += sVel[i].z*dt;
    if (sPos[i*3+1] < waveH(sPos[i*3], sPos[i*3+2], t)) resetDrop(i);
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Wake rings trail behind, recycled
  wake.forEach((f, i) => {
    const age = ((t * 1.2 + i / wake.length) % 1);
    f.position.set(rig.position.x - carve*age*2, waveH(0,0,t) - 0.35, rig.position.z - 1.2 - age * 9);
    const s = 0.6 + age * 2.2; f.scale.set(s*1.4, 0.25, s);
    f.material = foamMat;
  });

  clouds.children.forEach((c, i) => { c.position.x += dt * (0.25 + i*0.06); if (c.position.x > 34) c.position.x = -34; });
  gulls.forEach(g => {
    g.position.x += dt * g.userData.speed * 2;
    g.position.y += Math.sin(t*2 + g.userData.phase) * dt * 0.6;
    g.children[0].rotation.z =  Math.sin(t*7 + g.userData.phase) * 0.5;
    g.children[1].rotation.z = -Math.sin(t*7 + g.userData.phase) * 0.5;
    if (g.position.x > 30) g.position.x = -30;
  });

  // Slow cinematic camera drift (non-interactive)
  camera.position.set(7.5 + Math.sin(t * 0.11) * 1.6, 3.6 + Math.sin(t * 0.17) * 0.5, 9 + Math.cos(t * 0.09) * 1.2);
  camera.lookAt(rig.position.x * 0.5, 1.8, 0);

  renderer.render(scene, camera);
}
animate();
