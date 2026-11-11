import * as THREE from "three";

// ---------- renderer / scene / camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd4ee);
scene.fog = new THREE.Fog(0x8fd4ee, 28, 70);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(7.5, 3.6, 8.5);
camera.lookAt(0, 1.4, 0);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xcfefff, 0x2a6b7a, 0.95));
const sun = new THREE.DirectionalLight(0xfff2d0, 1.9);
sun.position.set(8, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
sun.shadow.camera.far = 40;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x9fd8ff, 0.35);
fill.position.set(-6, 4, -6);
scene.add(fill);

// ---------- materials ----------
const M = {
  body:   new THREE.MeshStandardMaterial({ color: 0xf8f4e8, roughness: 0.9 }),
  wing:   new THREE.MeshStandardMaterial({ color: 0xf1ead8, roughness: 0.9 }),
  tip:    new THREE.MeshStandardMaterial({ color: 0x3a3f45, roughness: 0.85 }),
  beak:   new THREE.MeshStandardMaterial({ color: 0xff8c1a, roughness: 0.55 }),
  pouch:  new THREE.MeshStandardMaterial({ color: 0xffb27a, roughness: 0.6 }),
  eye:    new THREE.MeshStandardMaterial({ color: 0x14181c, roughness: 0.3 }),
  foot:   new THREE.MeshStandardMaterial({ color: 0xff8c1a, roughness: 0.6 }),
  board:  new THREE.MeshStandardMaterial({ color: 0x14b8a6, roughness: 0.35 }),
  boardStripe: new THREE.MeshStandardMaterial({ color: 0xff6b5e, roughness: 0.4 }),
  glass:  new THREE.MeshStandardMaterial({ color: 0x111418, roughness: 0.15, metalness: 0.2 }),
  water:  new THREE.MeshStandardMaterial({ color: 0x1a9ec4, roughness: 0.35, metalness: 0.1 }),
  foam:   new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, transparent: true, opacity: 0.95, emissive: 0xffffff, emissiveIntensity: 0.45 }),
  cloud:  new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1.0, emissive: 0x8899aa, emissiveIntensity: 0.35 }),
};

function shadowed(mesh) { mesh.castShadow = true; mesh.receiveShadow = true; return mesh; }

// ---------- sky dome (gradient) ----------
{
  const skyGeo = new THREE.SphereGeometry(90, 32, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x3fa7dd) }, bottom: { value: new THREE.Color(0xd8f3fb) } },
    vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top; uniform vec3 bottom;
      void main(){ float h = normalize(vP).y*0.5+0.5; gl_FragColor = vec4(mix(bottom, top, smoothstep(0.35,0.85,h)),1.0); }`,
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
}

// ---------- sun disc ----------
{
  const disc = new THREE.Mesh(
    new THREE.SphereGeometry(3, 24, 16),
    new THREE.MeshBasicMaterial({ color: 0xfff3b0, fog: false })
  );
  disc.position.set(30, 32, -22);
  scene.add(disc);
}

// ---------- clouds ----------
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const puffs = [[0,0,0,1.4],[1.3,0.15,0.2,1.0],[-1.3,0.1,-0.1,1.05],[0.4,0.55,0,0.95]];
  for (const [px,py,pz,r] of puffs) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 10), M.cloud);
    m.position.set(px, py, pz); m.scale.y = 0.62; g.add(m);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g); clouds.push(g);
  return g;
}
makeCloud(-14, 8, -18, 1.5); makeCloud(10, 9, -24, 1.9);
makeCloud(-4, 10, -30, 1.3); makeCloud(18, 7, -12, 1.1);

// ---------- distant palm island ----------
{
  const isl = new THREE.Group();
  const sand = new THREE.Mesh(new THREE.SphereGeometry(3.2, 20, 12),
    new THREE.MeshStandardMaterial({ color: 0xe8d9a8, roughness: 1 }));
  sand.scale.y = 0.35; sand.position.y = -0.4; isl.add(sand);
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 2.6, 8),
    new THREE.MeshStandardMaterial({ color: 0x8a5a33, roughness: 1 }));
  trunk.position.y = 1.0; trunk.rotation.z = 0.18; isl.add(trunk);
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x2fa84f, roughness: 0.9, side: THREE.DoubleSide });
  for (let i = 0; i < 6; i++) {
    const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.45, 2.2, 4), leafMat);
    leaf.position.y = 2.3; leaf.rotation.z = 1.25;
    const holder = new THREE.Group(); holder.rotation.y = (i / 6) * Math.PI * 2;
    leaf.position.set(0.7, 2.15, 0); leaf.rotation.z = 1.9; leaf.rotation.x = 0.3;
    holder.add(leaf); isl.add(holder);
  }
  isl.position.set(-24, 0, -28);
  isl.scale.setScalar(1.5);
  scene.add(isl);
}

// ---------- ocean ----------
const oceanSize = 110, oceanSeg = 110;
const oceanGeo = new THREE.PlaneGeometry(oceanSize, oceanSize, oceanSeg, oceanSeg);
oceanGeo.rotateX(-Math.PI / 2);
const ocean = new THREE.Mesh(oceanGeo, M.water);
ocean.receiveShadow = true;
scene.add(ocean);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = oceanPos.array.slice();

function oceanHeight(x, z, t) {
  let y = Math.sin(x * 0.35 + t * 1.15) * 0.16
        + Math.sin(z * 0.5 - t * 0.9) * 0.13
        + Math.sin((x + z) * 0.22 + t * 0.6) * 0.10;
  // swell rising toward the wave line (z near -3.2), fading with distance
  const d = Math.abs(z + 3.4);
  y += Math.exp(-(d * d) / 14) * (1.6 + 0.25 * Math.sin(t * 1.3 + x * 0.4));
  return y;
}

// ---------- curling wave wall ----------
{
  // cross-section in (z, y): rises from the trough, curls forward (+z) over the face
  const prof = [
    [-7.5, -0.2], [-6.0, 0.45], [-4.6, 0.95], [-3.6, 1.4],
    [-2.8, 1.8], [-1.9, 2.05], [-0.9, 2.12], [0.1, 2.0],
    [0.85, 1.7], [1.15, 1.3], [0.85, 0.9], [0.15, 0.7],
  ];
  const segsX = 48, segsP = prof.length;
  const pos = [], idx = [], uv = [];
  for (let ix = 0; ix <= segsX; ix++) {
    const x = -11 + (22 * ix) / segsX;
    const taper = 1 - Math.pow(Math.abs(x) / 11, 3) * 0.55;
    for (let ip = 0; ip < segsP; ip++) {
      const [pz, py] = prof[ip];
      pos.push(x, py * taper, pz);
      uv.push(ix / segsX, ip / (segsP - 1));
    }
  }
  for (let ix = 0; ix < segsX; ix++)
    for (let ip = 0; ip < segsP - 1; ip++) {
      const a = ix * segsP + ip, b = (ix + 1) * segsP + ip;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  const waveMat = new THREE.MeshStandardMaterial({
    color: 0x2fb9e0, roughness: 0.18, metalness: 0.05,
    side: THREE.DoubleSide, transparent: true, opacity: 0.88,
    emissive: 0x0a4a66, emissiveIntensity: 0.35,
  });
  const wave = new THREE.Mesh(g, waveMat);
  wave.castShadow = true; wave.receiveShadow = true;
  scene.add(wave);
}

// foam lip along the crest (runs along X at the crest top)
const crestFoam = (() => {
  const pts = [
    new THREE.Vector3(-7.5, 2.08, -1.05),
    new THREE.Vector3(-4, 2.24, -0.9),
    new THREE.Vector3(0, 2.3, -0.85),
    new THREE.Vector3(4, 2.24, -0.9),
    new THREE.Vector3(7.5, 2.08, -1.05),
  ];
  const tube = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 32, 0.17, 8),
    M.foam
  );
  scene.add(tube); return tube;
})();

// ---------- surfboard ----------
function makeBoard() {
  const g = new THREE.Group();
  const shape = new THREE.Shape();
  shape.moveTo(-1.7, 0);
  shape.quadraticCurveTo(-1.85, 0.28, -1.2, 0.34);
  shape.lineTo(1.2, 0.34);
  shape.quadraticCurveTo(1.85, 0.26, 1.7, 0);
  shape.quadraticCurveTo(1.85, -0.26, 1.2, -0.34);
  shape.lineTo(-1.2, -0.34);
  shape.quadraticCurveTo(-1.85, -0.28, -1.7, 0);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, steps: 1 });
  geo.rotateX(-Math.PI / 2);
  const board = shadowed(new THREE.Mesh(geo, M.board));
  board.position.y = 0.05;
  g.add(board);
  // coral stripe
  const stripe = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.03, 0.2), M.boardStripe));
  stripe.position.set(-0.2, 0.12, 0);
  g.add(stripe);
  const tip2 = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.03, 0.14), M.boardStripe));
  tip2.position.set(1.05, 0.12, 0);
  g.add(tip2);
  return g;
}

// ---------- pelican ----------
const pelican = new THREE.Group();
const bodyGroup = new THREE.Group();
pelican.add(bodyGroup);
let pouch, wingL, wingR, headGroup, tail;
{
  // body — plump ellipsoid, front toward +X
  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.62, 28, 20), M.body));
  body.scale.set(1.45, 0.95, 0.92);
  body.position.set(0, 0.62, 0);
  bodyGroup.add(body);
  // belly highlight
  const belly = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.55, 24, 16), M.body));
  belly.scale.set(1.25, 0.8, 0.8); belly.position.set(0.12, 0.45, 0);
  bodyGroup.add(belly);

  // tail
  tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.7, 4), M.tip));
  tail.scale.set(1.0, 1.0, 0.35);
  tail.position.set(-0.95, 0.78, 0);
  tail.rotation.z = 1.15;
  bodyGroup.add(tail);

  // neck — S curve tube
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.55, 0.75, 0),
    new THREE.Vector3(0.85, 1.05, 0),
    new THREE.Vector3(0.95, 1.35, 0),
    new THREE.Vector3(1.05, 1.55, 0),
  ]);
  const neck = shadowed(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 16, 0.21, 12), M.body));
  bodyGroup.add(neck);

  // head group (animated slightly)
  headGroup = new THREE.Group();
  headGroup.position.set(1.12, 1.62, 0);
  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.26, 24, 18), M.body));
  head.scale.set(1.15, 1.0, 0.92);
  headGroup.add(head);
  // crest feather
  const crest = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.3, 6), M.body));
  crest.position.set(-0.1, 0.26, 0); crest.rotation.z = 0.5;
  headGroup.add(crest);
  // eyes
  for (const s of [1, -1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 10), M.eye);
    eye.position.set(0.17, 0.06, s * 0.2);
    headGroup.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.015, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff }));
    glint.position.set(0.2, 0.09, s * 0.23);
    headGroup.add(glint);
  }
  // sunglasses
  const shades = new THREE.Group();
  for (const s of [1, -1]) {
    const lens = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.11, 0.2), M.glass);
    lens.position.set(0.2, 0.07, s * 0.16);
    shades.add(lens);
  }
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.03, 0.14), M.glass);
  bridge.position.set(0.2, 0.09, 0); shades.add(bridge);
  headGroup.add(shades);

  // upper beak — long, flattened, slightly drooping
  const beakGeo = new THREE.CylinderGeometry(0.035, 0.15, 1.95, 10);
  beakGeo.rotateZ(-Math.PI / 2);
  beakGeo.scale(1, 0.5, 0.3);
  const beak = shadowed(new THREE.Mesh(beakGeo, M.beak));
  beak.position.set(1.1, 0.03, 0);
  beak.rotation.z = -0.16;
  headGroup.add(beak);
  // beak tip hook
  const hook = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.16, 8), M.beak));
  hook.position.set(2.08, -0.08, 0); hook.rotation.z = -Math.PI / 2 - 0.4;
  headGroup.add(hook);

  // pouch — sagging under the beak (smaller, tucked up)
  pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.34, 20, 14), M.pouch));
  pouch.scale.set(1.9, 0.62, 0.62);
  pouch.position.set(0.8, -0.18, 0);
  headGroup.add(pouch);
  bodyGroup.add(headGroup);

  // wings — extruded teardrop extending backward (-X), pivoted at shoulder
  function makeWing(side) {
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.quadraticCurveTo(-0.35, 0.42, -0.85, 0.38);
    shape.quadraticCurveTo(-1.25, 0.3, -1.35, 0.05);
    shape.quadraticCurveTo(-1.1, -0.12, -0.6, -0.12);
    shape.quadraticCurveTo(-0.2, -0.12, 0, 0);
    const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.07, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1 });
    geo.rotateX(-Math.PI / 2);
    const w = shadowed(new THREE.Mesh(geo, M.wing));
    w.scale.set(1.1, 1, 1.1);
    const tipM = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.5, 4), M.tip));
    tipM.scale.set(1, 0.35, 1); tipM.position.set(-1.35, 0.02, 0); tipM.rotation.z = Math.PI / 2;
    const holder = new THREE.Group();
    holder.add(w); holder.add(tipM);
    holder.position.set(0.1, 0.85, side * 0.45);
    holder.rotation.x = side * 0.15;
    holder.rotation.y = side > 0 ? 0 : Math.PI;
    if (side < 0) { w.scale.z = -1.1; }
    bodyGroup.add(holder);
    return holder;
  }
  wingL = makeWing(1);
  wingR = makeWing(-1);

  // legs + webbed feet on the board
  for (const s of [1, -1]) {
    const leg = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.42, 8), M.foot));
    leg.position.set(0.05, 0.3, s * 0.28);
    bodyGroup.add(leg);
    const foot = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.05, 0.24), M.foot));
    foot.position.set(0.1, 0.13, s * 0.28);
    bodyGroup.add(foot);
    for (let i = -1; i <= 1; i++) {
      const toe = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.18, 6), M.foot));
      toe.position.set(0.3, 0.13, s * 0.28 + i * 0.08);
      toe.rotation.z = -Math.PI / 2;
      bodyGroup.add(toe);
    }
  }
}
const board = makeBoard();
pelican.add(board);
board.position.y = -0.05;
pelican.scale.setScalar(1.4);
scene.add(pelican);
pelican.position.set(0, 1.3, 0.4);
pelican.rotation.y = -0.55;

// wake foam behind board
const wake = new THREE.Mesh(
  new THREE.PlaneGeometry(4.5, 1.0),
  new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.45, roughness: 1, depthWrite: false })
);
wake.rotation.x = -Math.PI / 2; wake.rotation.z = 0.15;
wake.position.set(-2.6, 1.02, 0.45);
scene.add(wake);

// ---------- spray particles ----------
const sprayCount = 90;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(sprayCount * 3);
const sprayVel = [];
for (let i = 0; i < sprayCount; i++) {
  sprayPos[i * 3 + 1] = -10;
  sprayVel.push(new THREE.Vector3());
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({
  color: 0xffffff, size: 0.14, transparent: true, opacity: 0.9, depthWrite: false,
}));
scene.add(spray);
let sprayTimer = 0;
function updateSpray(dt, t) {
  sprayTimer -= dt;
  const p = sprayGeo.attributes.position.array;
  for (let i = 0; i < sprayCount; i++) {
    let y = p[i * 3 + 1];
    if (y < -5 || sprayTimer <= 0 && Math.random() < 0.02) {
      // respawn at board tail
      p[i * 3] = pelican.position.x - 1.6 + Math.random() * 0.5;
      p[i * 3 + 1] = pelican.position.y + 0.15;
      p[i * 3 + 2] = pelican.position.z + (Math.random() - 0.5) * 0.6;
      sprayVel[i].set(-2.2 - Math.random() * 1.5, 1.2 + Math.random() * 1.2, (Math.random() - 0.5) * 1.4);
    } else {
      sprayVel[i].y -= 5.5 * dt;
      p[i * 3] += sprayVel[i].x * dt;
      p[i * 3 + 1] += sprayVel[i].y * dt;
      p[i * 3 + 2] += sprayVel[i].z * dt;
    }
  }
  sprayTimer = 0.05;
  sprayGeo.attributes.position.needsUpdate = true;
}

// ---------- animation ----------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // ocean vertices
  for (let i = 0; i < oceanPos.count; i++) {
    const bx = oceanBase[i * 3], bz = oceanBase[i * 3 + 2];
    oceanPos.array[i * 3 + 1] = oceanHeight(bx, bz, t);
  }
  oceanPos.needsUpdate = true;
  oceanGeo.computeVertexNormals();

  // pelican carve: slide along the face, lean, bob
  const carve = Math.sin(t * 0.45);
  pelican.position.x = carve * 1.1;
  pelican.position.z = 0.4 + carve * 0.35;
  pelican.position.y = 1.3 + Math.sin(t * 1.7) * 0.10 + Math.abs(carve) * 0.12;
  pelican.rotation.z = -carve * 0.16;          // lean into the turn
  pelican.rotation.x = Math.sin(t * 1.7) * 0.05;
  pelican.rotation.y = -0.55 - carve * 0.22;
  bodyGroup.rotation.z = Math.sin(t * 2.1) * 0.04;
  bodyGroup.position.y = Math.sin(t * 1.7) * 0.03;

  // head looks ahead, pouch jiggles
  headGroup.rotation.z = Math.sin(t * 1.3) * 0.06 - 0.05;
  headGroup.rotation.y = Math.sin(t * 0.4) * 0.12;
  pouch.scale.y = 0.85 + Math.sin(t * 3.2) * 0.06;

  // wings flap / balance
  const flap = Math.sin(t * 2.6) * 0.35 + Math.sin(t * 0.9) * 0.15;
  wingL.rotation.z = flap;
  wingR.rotation.z = -flap;
  wingL.rotation.x = 0.25 + flap * 0.4;
  wingR.rotation.x = -0.25 - flap * 0.4;
  tail.rotation.x = Math.sin(t * 2.0) * 0.12;

  // wave crest foam pulses
  crestFoam.material.opacity = 0.75 + Math.sin(t * 2.2) * 0.15;
  crestFoam.scale.setScalar(1 + Math.sin(t * 1.8) * 0.06);

  // wake follows board
  wake.position.x = pelican.position.x - 2.6;
  wake.position.z = pelican.position.z + 0.05;
  wake.position.y = pelican.position.y - 0.18;
  wake.material.opacity = 0.35 + Math.sin(t * 3.0) * 0.12;

  updateSpray(dt, t);

  // clouds drift
  for (const c of clouds) {
    c.position.x += dt * 0.35;
    if (c.position.x > 30) c.position.x = -30;
  }

  // slow cinematic camera drift (non-interactive)
  const cx = Math.sin(t * 0.08) * 1.4;
  camera.position.set(7.5 + cx, 3.6 + Math.sin(t * 0.11) * 0.5, 8.5 + Math.cos(t * 0.07) * 0.8);
  camera.lookAt(pelican.position.x * 0.4, 1.4, 0);

  renderer.render(scene, camera);
}
animate();


