import * as THREE from "three";

const container = document.getElementById("scene");
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xafe3ee);
scene.fog = new THREE.Fog(0xafe3ee, 18, 36);

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 3.4, 10.2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
container.appendChild(renderer.domElement);

// Lights
scene.add(new THREE.HemisphereLight(0xcdeffd, 0x2a7a8c, 1.15));
const sunLight = new THREE.DirectionalLight(0xffe3a3, 2.2);
sunLight.position.set(6, 9, 4);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10; sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10; sunLight.shadow.camera.bottom = -10;
scene.add(sunLight);
const fill = new THREE.DirectionalLight(0x9fd8e8, 0.55);
fill.position.set(-6, 4, -4);
scene.add(fill);

// Materials
const MAT = {
  white: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.65 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xfff6e8, roughness: 0.7 }),
  greyTip: new THREE.MeshStandardMaterial({ color: 0x3a4a52, roughness: 0.6 }),
  orange: new THREE.MeshStandardMaterial({ color: 0xff8a1a, roughness: 0.45 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xff9e6b, roughness: 0.55 }),
  black: new THREE.MeshStandardMaterial({ color: 0x10181c, roughness: 0.35 }),
  teal: new THREE.MeshStandardMaterial({ color: 0x14919b, roughness: 0.28, metalness: 0.05 }),
  tealDark: new THREE.MeshStandardMaterial({ color: 0x0f6f7e, roughness: 0.32 }),
  foam: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9 }),
};

function shadowed(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }
function sphere(r, mat, sx = 1, sy = 1, sz = 1) {
  const m = shadowed(new THREE.Mesh(new THREE.SphereGeometry(r, 28, 20), mat));
  m.scale.set(sx, sy, sz); return m;
}

// Sun + soft sky disc
const sun = sphere(0.72, new THREE.MeshBasicMaterial({ color: 0xffd66b }), 1, 1, 1);
sun.position.set(7.5, 5.6, -9); scene.add(sun);
const sunHalo = new THREE.Mesh(
  new THREE.CircleGeometry(1.35, 40),
  new THREE.MeshBasicMaterial({ color: 0xffe9a8, transparent: true, opacity: 0.45, depthWrite: false })
);
sunHalo.position.copy(sun.position); sunHalo.position.z -= 0.1; scene.add(sunHalo);

// Clouds (puffy sphere clusters)
const clouds = new THREE.Group(); scene.add(clouds);
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  [[0, 0, 0, 0.55], [0.55, -0.05, 0, 0.42], [-0.55, -0.02, 0, 0.4], [0.2, 0.22, 0, 0.38], [-0.2, 0.18, 0.1, 0.34]].forEach(([px, py, pz, r]) => {
    const b = new THREE.Mesh(new THREE.SphereGeometry(r, 20, 14), m); b.position.set(px, py, pz); g.add(b);
  });
  g.position.set(x, y, z); g.scale.setScalar(s); clouds.add(g); return g;
}
const cloudList = [makeCloud(-6.5, 5.4, -8, 1.2), makeCloud(3.8, 6.1, -9, 0.95), makeCloud(-1.5, 6.6, -10, 1.35), makeCloud(8, 4.6, -7, 0.8)];

// Ocean surface — animated vertices
const oceanGeo = new THREE.PlaneGeometry(36, 22, 72, 44);
oceanGeo.rotateX(-Math.PI / 2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({ color: 0x1aa6b5, roughness: 0.22, metalness: 0.05 }));
ocean.position.y = -0.55; ocean.receiveShadow = true; scene.add(ocean);

function waveHeight(x, z, t) {
  return Math.sin(x * 0.55 + t * 1.25) * 0.14 + Math.cos(z * 0.45 + t * 0.9) * 0.11 + Math.sin((x + z) * 0.3 + t * 0.6) * 0.07;
}

// Big curling wave behind the surfer (extruded profile)
const waveShape = new THREE.Shape();
waveShape.moveTo(-3.4, 0);
waveShape.bezierCurveTo(-3.4, 1.8, -2.4, 3.1, -0.7, 3.55);
waveShape.bezierCurveTo(0.7, 3.9, 1.9, 3.55, 2.15, 2.55);
waveShape.bezierCurveTo(2.3, 1.95, 1.65, 1.55, 1.05, 1.95);
waveShape.bezierCurveTo(0.55, 2.25, 0.75, 2.9, -0.15, 2.95);
waveShape.bezierCurveTo(-1.1, 3.0, -1.9, 2.0, -1.9, 0.6);
waveShape.lineTo(-1.55, 0);
waveShape.lineTo(-3.4, 0);
const waveGeo = new THREE.ExtrudeGeometry(waveShape, { depth: 13, bevelEnabled: true, bevelThickness: 0.18, bevelSize: 0.14, bevelSegments: 3, curveSegments: 28 });
waveGeo.rotateY(-Math.PI / 2);
const wave = shadowed(new THREE.Mesh(waveGeo, MAT.teal));
wave.position.set(6.5, -0.55, -2.6); wave.rotation.y = 0.02; scene.add(wave);
const waveInner = shadowed(new THREE.Mesh(waveGeo.clone(), MAT.tealDark));
waveInner.scale.set(0.985, 0.985, 0.985); waveInner.position.set(6.55, -0.52, -2.62); scene.add(waveInner);

// Foam crest — bumpy white spheres along the lip (runs across the wave, X axis)
const foamCrest = new THREE.Group(); scene.add(foamCrest);
for (let i = 0; i < 42; i++) {
  const x = -6.2 + i * 0.31;
  const s = sphere(0.16 + Math.random() * 0.13, MAT.foam);
  s.position.set(x, 2.55 + Math.cos(i * 2.3) * 0.08, -0.55 + Math.sin(i * 1.7) * 0.1);
  foamCrest.add(s);
}
for (let i = 0; i < 26; i++) {
  const s = sphere(0.1 + Math.random() * 0.1, MAT.foam);
  s.position.set(-6 + i * 0.48, 3.32 + Math.random() * 0.18, -1.1 + Math.random() * 0.5);
  foamCrest.add(s);
}

// Surfboard — striped top generated on a canvas (no external assets)
function boardTexture() {
  const c = document.createElement("canvas"); c.width = 512; c.height = 128;
  const ctx = c.getContext("2d");
  const stripes = ["#ff5a3c", "#ffb03a", "#fff3d6", "#14919b", "#fff3d6", "#ff8a1a"];
  const w = c.width / stripes.length;
  stripes.forEach((col, i) => { ctx.fillStyle = col; ctx.fillRect(i * w, 0, w + 1, c.height); });
  ctx.fillStyle = "rgba(255,255,255,.92)"; ctx.beginPath(); ctx.ellipse(256, 64, 52, 22, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#143642"; ctx.font = "bold 22px Georgia"; ctx.textAlign = "center"; ctx.fillText("PELI", 256, 72);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4; return tex;
}
const boardShape = new THREE.Shape();
boardShape.moveTo(0, -1.55);
boardShape.bezierCurveTo(0.52, -1.1, 0.58, 0.5, 0, 1.65);
boardShape.bezierCurveTo(-0.58, 0.5, -0.52, -1.1, 0, -1.55);
const boardGeo = new THREE.ExtrudeGeometry(boardShape, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 24 });
boardGeo.rotateX(-Math.PI / 2);
const board = shadowed(new THREE.Mesh(boardGeo, [
  new THREE.MeshStandardMaterial({ color: 0xfff3d6, roughness: 0.4 }),
  new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.35 }),
]));
// Extrude material index fallback: ensure top looks striped even if groups differ
board.material = new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.35 });

// Rider group: board + pelican move together
const rider = new THREE.Group(); scene.add(rider);
rider.add(board); board.position.y = 0;

// Pelican
const pelican = new THREE.Group(); pelican.position.y = 0.12; rider.add(pelican);
const body = sphere(0.62, MAT.white, 1, 0.82, 1.35); body.position.set(0, 0.62, -0.1); pelican.add(body);
const belly = sphere(0.55, MAT.cream, 0.92, 0.72, 1.15); belly.position.set(0, 0.5, 0.02); pelican.add(belly);
// Tail feathers
const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.34, 0.75, 14), MAT.white));
tail.rotation.x = Math.PI / 2 + 0.35; tail.position.set(0, 0.72, -0.92); tail.scale.set(1.25, 1, 0.45); pelican.add(tail);
const tailTip = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.4, 12), MAT.greyTip));
tailTip.rotation.x = Math.PI / 2 + 0.35; tailTip.position.set(0, 0.78, -1.18); tailTip.scale.set(1.3, 1, 0.4); pelican.add(tailTip);

// Neck — S-curve tube rising from the front of the body
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 0.78, 0.52),
  new THREE.Vector3(0, 1.02, 0.68),
  new THREE.Vector3(0, 1.28, 0.58),
  new THREE.Vector3(0, 1.52, 0.72),
]);
const neck = shadowed(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 20, 0.21, 12), MAT.white));
pelican.add(neck);

// Head group (bobs independently)
const headGroup = new THREE.Group(); headGroup.position.set(0, 1.56, 0.74); pelican.add(headGroup);
const head = sphere(0.34, MAT.white, 1, 0.92, 1.05); headGroup.add(head);
const crest = sphere(0.2, MAT.cream, 1, 0.6, 1); crest.position.set(0, 0.24, -0.12); headGroup.add(crest);
[-1, 1].forEach((side) => {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 10), MAT.black);
  eye.position.set(side * 0.22, 0.08, 0.24); headGroup.add(eye);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.016, 8, 18), MAT.orange);
  ring.position.copy(eye.position); ring.rotation.y = side * 0.5; headGroup.add(ring);
});
// Long beak + swinging pouch — the unmistakable pelican silhouette
const beak = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.13, 1.15, 12), MAT.orange));
beak.rotation.x = Math.PI / 2; beak.rotation.z = 0; beak.position.set(0, -0.02, 0.82); beak.scale.set(0.75, 1, 0.55); headGroup.add(beak);
const beakTip = sphere(0.07, MAT.black, 1, 0.8, 1); beakTip.position.set(0, -0.03, 1.38); headGroup.add(beakTip);
const pouch = sphere(0.3, MAT.pouch, 0.7, 0.85, 1.55); pouch.position.set(0, -0.24, 0.72); headGroup.add(pouch);

// Wings — flattened shapes that flap for balance
function makeWing(side) {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(side * 0.5, 0.22, side * 1.05, 0.18, side * 1.45, -0.08);
  shape.bezierCurveTo(side * 1.0, -0.22, side * 0.45, -0.28, 0, -0.18);
  shape.lineTo(0, 0);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.06, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1, curveSegments: 16 });
  geo.rotateX(-Math.PI / 2);
  const wing = new THREE.Group();
  const main = shadowed(new THREE.Mesh(geo, MAT.white)); wing.add(main);
  const tip = sphere(0.28, MAT.greyTip, 1.6, 0.28, 0.7); tip.position.set(side * 1.28, 0, -0.05); wing.add(tip);
  wing.position.set(side * 0.42, 0.88, -0.05);
  pelican.add(wing); return wing;
}
const wingL = makeWing(-1); const wingR = makeWing(1);

// Legs + webbed feet planted on the board
[-1, 1].forEach((side) => {
  const leg = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.42, 10), MAT.orange));
  leg.position.set(side * 0.22, 0.22, 0.08); leg.rotation.x = 0.12; pelican.add(leg);
  const foot = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.05, 0.42), MAT.orange));
  foot.position.set(side * 0.22, 0.03, 0.18); pelican.add(foot);
});

// Spray particles behind the board
const SPRAY = 140;
const sprayPos = new Float32Array(SPRAY * 3);
const sprayVel = [];
for (let i = 0; i < SPRAY; i++) {
  sprayPos.set([(Math.random() - 0.5) * 0.5, Math.random() * 0.3, -1 - Math.random() * 0.6], i * 3);
  sprayVel.push({ x: (Math.random() - 0.5) * 0.6, y: 0.8 + Math.random() * 1.4, z: -0.8 - Math.random() * 1.2, life: Math.random() });
}
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.09, transparent: true, opacity: 0.85, depthWrite: false }));
scene.add(spray);

// Distant birds — simple flapping V shapes
const birds = new THREE.Group(); scene.add(birds);
function makeBird(x, y, z, s) {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x2a4a56 });
  [-1, 1].forEach((side) => {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.03, 0.1), mat);
    w.position.x = side * 0.24; w.geometry.translate(side * 0.0, 0, 0); g.add(w);
    w.name = side < 0 ? "wl" : "wr";
  });
  g.position.set(x, y, z); g.scale.setScalar(s); birds.add(g); return g;
}
const birdList = [makeBird(-4, 4.6, -6, 1), makeBird(2.5, 5.1, -7, 0.8), makeBird(5.5, 4.2, -5, 0.65)];

// Foam trail blobs that fade behind the board
const trail = [];
for (let i = 0; i < 18; i++) {
  const b = sphere(0.14 + Math.random() * 0.12, MAT.foam);
  b.material = MAT.foam; scene.add(b); trail.push({ mesh: b, age: i / 18 });
}

const clock = new THREE.Clock();
const lookTarget = new THREE.Vector3(0, 1.1, 0);
let prevX = 0;

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // Ocean vertices
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i * 3]; const z = oceanBase[i * 3 + 2];
    pos.setY(i, waveHeight(x, z, t));
  }
  pos.needsUpdate = true; oceanGeo.computeVertexNormals();

  // Rider carves left-right across the wave face
  const carveX = Math.sin(t * 0.5) * 2.1;
  const carveZ = Math.sin(t * 0.33) * 0.35 - 0.2;
  const speedX = carveX - prevX; prevX = carveX;
  rider.position.set(carveX, 0.18 + waveHeight(carveX, carveZ, t) + Math.sin(t * 2.1) * 0.05, carveZ);
  rider.rotation.set(Math.sin(t * 1.7) * 0.06 - 0.03, -speedX * 1.4, THREE.MathUtils.clamp(-speedX * 2.2, -0.38, 0.38) + Math.sin(t * 2.1) * 0.04);
  board.rotation.y = -speedX * 0.9;

  // Pelican balance: squash, wing flap, head bob, pouch swing
  pelican.position.y = 0.12 + Math.sin(t * 2.4) * 0.035;
  pelican.rotation.z = Math.sin(t * 1.3) * 0.05;
  const flap = Math.sin(t * 2.6) * 0.32 + Math.sin(t * 0.9) * 0.12;
  wingL.rotation.z = 0.18 - flap; wingR.rotation.z = -0.18 + flap;
  wingL.rotation.y = Math.sin(t * 1.8) * 0.08; wingR.rotation.y = -Math.sin(t * 1.8) * 0.08;
  headGroup.rotation.x = Math.sin(t * 1.9) * 0.09 - 0.04;
  headGroup.rotation.y = Math.sin(t * 0.55) * 0.28;
  headGroup.rotation.z = Math.sin(t * 1.4) * 0.05;
  pouch.rotation.x = Math.sin(t * 2.2) * 0.14; pouch.position.y = -0.24 + Math.sin(t * 2.2) * 0.02;
  tail.rotation.x = Math.PI / 2 + 0.35 + Math.sin(t * 2.4) * 0.07;

  // Spray follows the board tail
  spray.position.set(carveX, rider.position.y + 0.05, carveZ - 0.4);
  spray.rotation.y = rider.rotation.y;
  const sp = sprayGeo.attributes.position;
  for (let i = 0; i < SPRAY; i++) {
    const v = sprayVel[i]; v.life += 0.016;
    if (v.life > 1) {
      v.life = 0; v.x = (Math.random() - 0.5) * 0.7; v.y = 0.9 + Math.random() * 1.5; v.z = -0.7 - Math.random() * 1.1;
      sp.setXYZ(i, (Math.random() - 0.5) * 0.45, 0, -1.1);
    } else {
      sp.setXYZ(i, sp.getX(i) + v.x * 0.016, Math.max(0, sp.getY(i) + v.y * 0.016 - v.life * 0.03), sp.getZ(i) + v.z * 0.016);
    }
  }
  sp.needsUpdate = true;

  // Foam trail
  trail.forEach((tr, i) => {
    tr.age += 0.008; if (tr.age > 1) tr.age = 0;
    tr.mesh.position.set(carveX - Math.sin(t * 0.5) * 0.2 + (Math.random() - 0.5) * 0.06, -0.28 + waveHeight(carveX, carveZ - 1 - tr.age * 3, t), carveZ - 0.8 - tr.age * 3.2);
    const s = 0.6 + tr.age * 1.6; tr.mesh.scale.set(s, 0.35, s);
    tr.mesh.material.opacity = 1;
  });

  // Ambient motion
  foamCrest.position.y = Math.sin(t * 1.4) * 0.05;
  foamCrest.children.forEach((c, i) => { const s = 1 + Math.sin(t * 2.2 + i) * 0.12; c.scale.setScalar(s); });
  cloudList.forEach((c, i) => { c.position.x += 0.0016 * (1 + i * 0.2); if (c.position.x > 11) c.position.x = -11; });
  birdList.forEach((b, i) => {
    b.position.x += 0.012 + i * 0.002; b.position.y += Math.sin(t * 2 + i * 2) * 0.002;
    if (b.position.x > 11) b.position.x = -11;
    b.children.forEach((w) => { w.rotation.z = (w.name === "wl" ? 1 : -1) * (0.25 + Math.sin(t * 9 + i) * 0.35); });
  });
  sun.position.x = 7.5 + Math.sin(t * 0.07) * 0.3;

  // Gentle non-interactive camera sway
  camera.position.x = Math.sin(t * 0.14) * 0.85;
  camera.position.y = 3.4 + Math.sin(t * 0.22) * 0.22;
  camera.position.z = 10.2 + Math.sin(t * 0.1) * 0.35;
  lookTarget.set(carveX * 0.35, 1.15 + Math.sin(t * 0.8) * 0.08, 0);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
animate();

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
