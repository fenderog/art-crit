import * as THREE from "three";

/* ============================ renderer / scene =========================== */

const app = document.getElementById("app") ?? document.body;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd8edf7, 48, 175);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);

/* ------------------------------- sky + sun ------------------------------- */

function makeSkyTexture() {
  const c = document.createElement("canvas");
  c.width = 4;
  c.height = 512;
  const g = c.getContext("2d");
  const grad = g.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0.0, "#5fb8ea");
  grad.addColorStop(0.45, "#9ad7f2");
  grad.addColorStop(0.75, "#d7effa");
  grad.addColorStop(1.0, "#eef9fd");
  g.fillStyle = grad;
  g.fillRect(0, 0, 4, 512);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
scene.background = makeSkyTexture();

function makeGlowTexture(stops) {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  for (const [at, col] of stops) grad.addColorStop(at, col);
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const sunDir = new THREE.Vector3(-65, 42, -95);

const sunLight = new THREE.DirectionalLight(0xfff1d8, 2.4);
sunLight.position.copy(sunDir);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -9;
sunLight.shadow.camera.right = 9;
sunLight.shadow.camera.top = 9;
sunLight.shadow.camera.bottom = -9;
sunLight.shadow.camera.near = 80;
sunLight.shadow.camera.far = 170;
sunLight.shadow.bias = -0.0004;
sunLight.shadow.normalBias = 0.03;
scene.add(sunLight, sunLight.target);

scene.add(new THREE.HemisphereLight(0xcfe9ff, 0x2e6f8e, 1.0));

const sunBall = new THREE.Mesh(
  new THREE.SphereGeometry(7, 24, 16),
  new THREE.MeshBasicMaterial({ color: 0xfff7d6, fog: false })
);
sunBall.position.copy(sunDir).multiplyScalar(1.7);
scene.add(sunBall);

const sunGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: makeGlowTexture([
      [0, "rgba(255,246,214,0.85)"],
      [0.35, "rgba(255,240,200,0.3)"],
      [1, "rgba(255,240,200,0)"],
    ]),
    transparent: true,
    depthWrite: false,
    fog: false,
  })
);
sunGlow.scale.setScalar(80);
sunGlow.position.copy(sunBall.position);
scene.add(sunGlow);

/* --------------------------------- ocean --------------------------------- */

// Sum of directional sine swells, travelling roughly toward +z.
const SWELL = [
  { a: 0.55, k: 0.32, dx: 0.0, dz: 1.0, w: 1.15, p: 0.0 },
  { a: 0.28, k: 0.5, dx: 0.35, dz: 0.94, w: 1.5, p: 1.7 },
  { a: 0.18, k: 0.9, dx: -0.6, dz: 0.8, w: 2.1, p: 4.1 },
  { a: 0.1, k: 1.6, dx: 1.0, dz: 0.12, w: 2.6, p: 2.3 },
];

function waterHeight(x, z, t) {
  let h = 0;
  for (let i = 0; i < SWELL.length; i++) {
    const s = SWELL[i];
    h += s.a * Math.sin(s.k * (s.dx * x + s.dz * z) - s.w * t + s.p);
  }
  return h;
}

function waterSlope(x, z, t, out) {
  let sx = 0;
  let sz = 0;
  for (let i = 0; i < SWELL.length; i++) {
    const s = SWELL[i];
    const c = s.a * s.k * Math.cos(s.k * (s.dx * x + s.dz * z) - s.w * t + s.p);
    sx += c * s.dx;
    sz += c * s.dz;
  }
  out.x = sx;
  out.y = sz;
}

const oceanGeo = new THREE.PlaneGeometry(230, 230, 150, 150);
oceanGeo.rotateX(-Math.PI / 2);
const oceanCount = oceanGeo.attributes.position.count;
oceanGeo.setAttribute(
  "color",
  new THREE.BufferAttribute(new Float32Array(oceanCount * 3), 3)
);
const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.28,
    metalness: 0.05,
  })
);
ocean.receiveShadow = true;
scene.add(ocean);

const oceanPos = oceanGeo.attributes.position;
const oceanCol = oceanGeo.attributes.color;

function updateOcean(t) {
  const p = oceanPos.array;
  const c = oceanCol.array;
  for (let i = 0; i < p.length; i += 3) {
    const h = waterHeight(p[i], p[i + 2], t);
    p[i + 1] = h;
    let s = (h + 1.0) * 0.5;
    s = s < 0 ? 0 : s > 1 ? 1 : s;
    let r = 0.05 + 0.11 * s;
    let g = 0.3 + 0.25 * s;
    let b = 0.46 + 0.26 * s;
    if (s > 0.82) {
      const w = ((s - 0.82) / 0.18) * 0.35;
      r += w;
      g += w;
      b += w;
    }
    c[i] = r;
    c[i + 1] = g;
    c[i + 2] = b;
  }
  oceanPos.needsUpdate = true;
  oceanCol.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

/* ------------------------------- surfboard ------------------------------- */

function boardShape() {
  const w = 0.37;
  const L = 1.45;
  const s = new THREE.Shape();
  s.moveTo(0, L);
  s.quadraticCurveTo(w * 0.9, L * 0.8, w * 0.98, 0.2);
  s.quadraticCurveTo(w, -L * 0.5, w * 0.7, -L * 0.88);
  s.quadraticCurveTo(w * 0.45, -L, 0, -L);
  s.quadraticCurveTo(-w * 0.45, -L, -w * 0.7, -L * 0.88);
  s.quadraticCurveTo(-w, -L * 0.5, -w * 0.98, 0.2);
  s.quadraticCurveTo(-w * 0.9, L * 0.8, 0, L);
  return s;
}

function makeDeckTexture() {
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 512;
  const g = c.getContext("2d");
  g.fillStyle = "#fdf3e0";
  g.fillRect(0, 0, 256, 512);
  g.fillStyle = "#1f8a8c";
  g.fillRect(108, 0, 40, 512);
  g.fillStyle = "#ff6f61";
  g.fillRect(86, 0, 10, 512);
  g.fillRect(160, 0, 10, 512);
  const eg = g.createLinearGradient(0, 0, 256, 0);
  eg.addColorStop(0, "rgba(60,20,10,0.16)");
  eg.addColorStop(0.14, "rgba(60,20,10,0)");
  eg.addColorStop(0.86, "rgba(60,20,10,0)");
  eg.addColorStop(1, "rgba(60,20,10,0.16)");
  g.fillStyle = eg;
  g.fillRect(0, 0, 256, 512);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

const shape = boardShape();

const boardGeo = new THREE.ExtrudeGeometry(shape, {
  depth: 0.06,
  bevelEnabled: true,
  bevelThickness: 0.035,
  bevelSize: 0.03,
  bevelSegments: 3,
  curveSegments: 28,
  steps: 1,
});
boardGeo.rotateX(Math.PI / 2);
boardGeo.computeBoundingBox();
const bb = boardGeo.boundingBox;
const boardHalf = (bb.max.y - bb.min.y) / 2;
boardGeo.translate(0, -(bb.max.y + bb.min.y) / 2, 0);
const board = new THREE.Mesh(
  boardGeo,
  new THREE.MeshStandardMaterial({ color: 0xff7a5c, roughness: 0.4 })
);
board.castShadow = true;

const deckGeo = new THREE.ShapeGeometry(shape, 28);
deckGeo.rotateX(-Math.PI / 2);
deckGeo.rotateY(Math.PI);
{
  const uv = deckGeo.attributes.uv;
  let uMin = Infinity,
    uMax = -Infinity,
    vMin = Infinity,
    vMax = -Infinity;
  for (let i = 0; i < uv.count; i++) {
    const u = uv.getX(i);
    const v = uv.getY(i);
    if (u < uMin) uMin = u;
    if (u > uMax) uMax = u;
    if (v < vMin) vMin = v;
    if (v > vMax) vMax = v;
  }
  const du = uMax - uMin;
  const dv = vMax - vMin;
  for (let i = 0; i < uv.count; i++) {
    uv.setXY(i, (uv.getX(i) - uMin) / du, (uv.getY(i) - vMin) / dv);
  }
  uv.needsUpdate = true;
}
deckGeo.scale(0.92, 1, 0.97);
const deck = new THREE.Mesh(
  deckGeo,
  new THREE.MeshStandardMaterial({ map: makeDeckTexture(), roughness: 0.45 })
);
deck.position.y = boardHalf + 0.002;

const fin = new THREE.Mesh(
  new THREE.BoxGeometry(0.025, 0.18, 0.3),
  new THREE.MeshStandardMaterial({ color: 0xd84f3f, roughness: 0.5 })
);
fin.position.set(0, -boardHalf - 0.06, -0.95);
fin.rotation.x = 0.28;
fin.castShadow = true;

/* -------------------------------- pelican -------------------------------- */

function buildPelican() {
  const mats = {
    white: new THREE.MeshStandardMaterial({ color: 0xf4efe4, roughness: 0.85 }),
    gray: new THREE.MeshStandardMaterial({ color: 0x8d9299, roughness: 0.85 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x22262b, roughness: 0.6 }),
    beak: new THREE.MeshStandardMaterial({ color: 0xd9c087, roughness: 0.55 }),
    orange: new THREE.MeshStandardMaterial({ color: 0xe07f35, roughness: 0.6 }),
  };

  const root = new THREE.Group();

  const add = (parent, geo, mat, x = 0, y = 0, z = 0) => {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.castShadow = true;
    parent.add(m);
    return m;
  };

  // legs (scaled for crouching) + webbed feet planted on the deck
  const legGeo = new THREE.CylinderGeometry(0.045, 0.05, 0.34, 8);
  legGeo.translate(0, 0.17, 0);
  const legL = add(root, legGeo, mats.orange, -0.17, 0.01, 0.3);
  const legR = add(root, legGeo, mats.orange, 0.17, 0.01, -0.1);

  const footGeo = new THREE.BoxGeometry(0.17, 0.035, 0.3);
  const footL = add(root, footGeo, mats.orange, -0.17, 0.03, 0.36);
  footL.rotation.y = -0.22;
  const footR = add(root, footGeo, mats.orange, 0.17, 0.03, -0.04);
  footR.rotation.y = 0.22;

  // body group: bobs with the crouch
  const body = new THREE.Group();
  body.position.y = 0.52;
  root.add(body);

  const bodyMesh = add(body, new THREE.SphereGeometry(0.5, 26, 18), mats.white);
  bodyMesh.scale.set(0.96, 0.84, 1.32);

  const tail = add(
    body,
    new THREE.BoxGeometry(0.3, 0.045, 0.42),
    mats.gray,
    0,
    0.04,
    -0.66
  );
  tail.rotation.x = 0.35;

  // wide wings, held out for balance
  function makeWing(side) {
    const g = new THREE.Group();
    g.position.set(side * 0.4, 0.2, 0.05);
    const inner = add(
      g,
      new THREE.SphereGeometry(0.5, 20, 12),
      mats.white,
      side * 0.55,
      0,
      0
    );
    inner.scale.set(1.45, 0.2, 0.6);
    const outer = add(
      g,
      new THREE.SphereGeometry(0.5, 18, 10),
      mats.gray,
      side * 1.32,
      -0.05,
      -0.12
    );
    outer.scale.set(1.15, 0.14, 0.42);
    outer.rotation.z = -side * 0.14;
    g.rotation.y = -side * 0.16;
    body.add(g);
    return g;
  }
  const wingR = makeWing(1);
  const wingL = makeWing(-1);

  // S-curved neck + head + huge beak with pouch
  const headAsm = new THREE.Group();
  headAsm.position.set(0, 0.26, 0.42);
  body.add(headAsm);

  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, -0.05, 0),
    new THREE.Vector3(0, 0.16, 0.03),
    new THREE.Vector3(0, 0.38, -0.01),
    new THREE.Vector3(0, 0.56, 0.07),
  ]);
  add(headAsm, new THREE.TubeGeometry(neckCurve, 14, 0.115, 10), mats.white);

  add(headAsm, new THREE.SphereGeometry(0.19, 20, 14), mats.white, 0, 0.6, 0.1);

  const crest = add(
    headAsm,
    new THREE.ConeGeometry(0.07, 0.18, 8),
    mats.white,
    0,
    0.73,
    -0.03
  );
  crest.rotation.x = -0.5;

  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, 0.58, 0.22);
  beakGroup.rotation.x = 0.05;
  headAsm.add(beakGroup);

  const beakGeo = new THREE.ConeGeometry(0.075, 0.82, 12);
  beakGeo.scale(1, 1, 0.55);
  beakGeo.rotateX(Math.PI / 2); // apex -> +z
  add(beakGroup, beakGeo, mats.beak, 0, 0, 0.41);

  const pouch = add(
    beakGroup,
    new THREE.SphereGeometry(0.15, 14, 10),
    mats.orange,
    0,
    -0.1,
    0.36
  );
  pouch.scale.set(0.45, 0.8, 2.1);

  const eyeGeo = new THREE.SphereGeometry(0.032, 10, 8);
  add(headAsm, eyeGeo, mats.dark, -0.14, 0.66, 0.23);
  add(headAsm, eyeGeo, mats.dark, 0.14, 0.66, 0.23);

  return { root, body, wingL, wingR, headAsm, legL, legR };
}

/* --------------------------- surfer group + foam -------------------------- */

const surfer = new THREE.Group();
surfer.rotation.order = "YXZ";
scene.add(surfer);
surfer.add(board, deck, fin);

const pelican = buildPelican();
pelican.root.position.y = boardHalf + 0.004;
surfer.add(pelican.root);

// soft foam wash ring floating on the water around the board
const ring = new THREE.Mesh(
  new THREE.PlaneGeometry(3.6, 2.8),
  new THREE.MeshBasicMaterial({
    map: makeGlowTexture([
      [0, "rgba(255,255,255,0)"],
      [0.42, "rgba(255,255,255,0.4)"],
      [0.72, "rgba(255,255,255,0.14)"],
      [1, "rgba(255,255,255,0)"],
    ]),
    transparent: true,
    depthWrite: false,
    opacity: 0.9,
  })
);
ring.renderOrder = 2;
scene.add(ring);

// spray / foam trail particles
const MAXP = 340;
const foamGeo = new THREE.BufferGeometry();
const foamPos = new Float32Array(MAXP * 3);
const foamCol = new Float32Array(MAXP * 3);
foamGeo.setAttribute(
  "position",
  new THREE.BufferAttribute(foamPos, 3).setUsage(THREE.DynamicDrawUsage)
);
foamGeo.setAttribute(
  "color",
  new THREE.BufferAttribute(foamCol, 3).setUsage(THREE.DynamicDrawUsage)
);
const foam = new THREE.Points(
  foamGeo,
  new THREE.PointsMaterial({
    size: 0.15,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    sizeAttenuation: true,
  })
);
foam.frustumCulled = false;
scene.add(foam);

const parts = [];
for (let i = 0; i < MAXP; i++) {
  parts.push({
    x: 0,
    y: -10,
    z: 0,
    vx: 0,
    vy: 0,
    vz: 0,
    life: -Math.random() * 2,
    maxLife: 1.5,
  });
}

let surferYaw = 0;

function updateFoam(dt, t, sx, sy, sz) {
  const fx = Math.sin(surferYaw);
  const fz = Math.cos(surferYaw);
  const px = Math.cos(surferYaw);
  const pz = -Math.sin(surferYaw);
  for (let i = 0; i < MAXP; i++) {
    const pt = parts[i];
    pt.life -= dt;
    if (pt.life <= 0) {
      const back = 1.15 + Math.random() * 0.45;
      const lat = (Math.random() - 0.5) * 0.7;
      pt.x = sx - fx * back + px * lat;
      pt.z = sz - fz * back + pz * lat;
      pt.y = waterHeight(pt.x, pt.z, t) + 0.05;
      pt.vx = -fx * (0.9 + Math.random() * 0.9) + px * (Math.random() - 0.5);
      pt.vz = -fz * (0.9 + Math.random() * 0.9) + pz * (Math.random() - 0.5);
      pt.vy = 0.4 + Math.random() * 1.1;
      pt.maxLife = 1.1 + Math.random() * 1.1;
      pt.life = pt.maxLife;
    } else {
      pt.vy -= 3.0 * dt;
      pt.x += pt.vx * dt;
      pt.y += pt.vy * dt;
      pt.z += pt.vz * dt;
      const wh = waterHeight(pt.x, pt.z, t);
      if (pt.y < wh + 0.02) {
        pt.y = wh + 0.02;
        pt.vy = 0;
        const drag = Math.max(0, 1 - 2.5 * dt);
        pt.vx = pt.vx * drag - fx * 0.5 * dt;
        pt.vz = pt.vz * drag - fz * 0.5 * dt;
      }
    }
    const fade = Math.max(pt.life, 0) / pt.maxLife;
    const j = i * 3;
    foamPos[j] = pt.x;
    foamPos[j + 1] = pt.y;
    foamPos[j + 2] = pt.z;
    foamCol[j] = 1 - 0.38 * (1 - fade);
    foamCol[j + 1] = 1 - 0.22 * (1 - fade);
    foamCol[j + 2] = 1 - 0.15 * (1 - fade);
  }
  foamGeo.attributes.position.needsUpdate = true;
  foamGeo.attributes.color.needsUpdate = true;
}

/* ----------------------------- clouds + birds ---------------------------- */

const cloudMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 1,
  flatShading: true,
  transparent: true,
  opacity: 0.92,
});
const puffGeo = new THREE.SphereGeometry(1, 10, 8);
const clouds = [];
for (let i = 0; i < 8; i++) {
  const g = new THREE.Group();
  const n = 3 + Math.floor(Math.random() * 3);
  for (let k = 0; k < n; k++) {
    const m = new THREE.Mesh(puffGeo, cloudMat);
    m.position.set(
      (Math.random() - 0.5) * 4.5,
      (Math.random() - 0.5) * 1.2,
      (Math.random() - 0.5) * 2
    );
    m.scale.set(
      1.6 + Math.random() * 1.8,
      0.9 + Math.random() * 0.7,
      1.2 + Math.random()
    );
    g.add(m);
  }
  g.position.set(
    (Math.random() - 0.5) * 260,
    15 + Math.random() * 11,
    (Math.random() - 0.5) * 260
  );
  scene.add(g);
  clouds.push({ g, vx: 0.5 + Math.random() * 0.8 });
}

function makeBird() {
  const mat = new THREE.MeshStandardMaterial({
    color: 0x33404c,
    roughness: 0.9,
    side: THREE.DoubleSide,
  });
  const g = new THREE.Group();
  const bodyGeo = new THREE.ConeGeometry(0.07, 0.5, 6);
  bodyGeo.rotateX(Math.PI / 2);
  g.add(new THREE.Mesh(bodyGeo, mat));
  const wingGeoR = new THREE.PlaneGeometry(0.72, 0.24);
  wingGeoR.translate(0.36, 0, 0);
  const wingGeoL = new THREE.PlaneGeometry(0.72, 0.24);
  wingGeoL.translate(-0.36, 0, 0);
  const wr = new THREE.Mesh(wingGeoR, mat);
  const wl = new THREE.Mesh(wingGeoL, mat);
  g.add(wr, wl);
  g.rotation.y = Math.PI / 2; // face +x
  scene.add(g);
  return { g, wr, wl };
}

const birds = [];
for (let i = 0; i < 6; i++) {
  const b = makeBird();
  birds.push({
    ...b,
    speed: 3.5 + Math.random() * 2,
    off: Math.random() * 100,
    y: 11 + Math.random() * 5,
    z: -28 - i * 7,
  });
}

/* -------------------------------- animate -------------------------------- */

const clock = new THREE.Clock();
const slope = { x: 0, y: 0 };

function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  updateOcean(t);

  // surfer carving across the swell
  const sx = Math.sin(t * 0.33) * 2.4;
  const sz = Math.sin(t * 0.21) * 1.1;
  const sy = waterHeight(sx, sz, t);
  waterSlope(sx, sz, t, slope);
  surferYaw = 0.35 * Math.sin(t * 0.26) + 0.15;
  surfer.position.set(sx, sy + 0.02, sz);
  surfer.rotation.y = surferYaw;
  surfer.rotation.x = Math.atan(slope.y) * 0.85;
  surfer.rotation.z = -Math.atan(slope.x) * 0.8 + 0.07 * Math.sin(t * 1.1);

  // pelican balancing act
  const pitch = surfer.rotation.x;
  const crouch = 0.5 + 0.5 * Math.sin(t * 1.15 + 0.7);
  const legScale = 1 - 0.3 * crouch * crouch;
  pelican.legL.scale.y = legScale;
  pelican.legR.scale.y = legScale;
  pelican.body.position.y = 0.52 - 0.34 * (1 - legScale);
  pelican.body.rotation.x = -pitch * 0.45 + 0.04 * Math.sin(t * 2.1);
  pelican.body.rotation.z = -surfer.rotation.z * 0.4;

  const big = Math.pow(Math.max(0, Math.sin(t * 0.42)), 3);
  const flap = (0.1 + 0.5 * big) * Math.sin(t * (2.4 + 3.5 * big));
  const spread = 0.14 + 0.1 * big;
  pelican.wingR.rotation.z = spread + flap;
  pelican.wingL.rotation.z = -(spread + flap);

  pelican.headAsm.rotation.y = 0.45 * Math.sin(t * 0.36 + 1.3);
  pelican.headAsm.rotation.x = 0.07 * Math.sin(t * 0.9) - pitch * 0.3;

  // foam wash ring
  ring.position.set(sx, sy + 0.045, sz);
  ring.rotation.set(-Math.PI / 2, 0, surferYaw);
  const rp = 1 + 0.06 * Math.sin(t * 2.2);
  ring.scale.set(rp, rp, 1);

  updateFoam(dt, t, sx, sy, sz);

  for (const b of birds) {
    b.g.position.set(
      ((t * b.speed + b.off * 10) % 240) - 120,
      b.y + Math.sin(t * 0.8 + b.off) * 0.6,
      b.z
    );
    const f = Math.sin(t * 9 + b.off) * 0.6;
    b.wr.rotation.z = f + 0.1;
    b.wl.rotation.z = -f - 0.1;
  }

  for (const c of clouds) {
    c.g.position.x += c.vx * dt;
    if (c.g.position.x > 150) c.g.position.x = -150;
  }

  // slow cinematic orbit around the surfer
  const ang = t * 0.09 + 0.6;
  const rad = 9.0 + 1.1 * Math.sin(t * 0.05);
  const cx = sx + Math.sin(ang) * rad;
  const cz = sz + Math.cos(ang) * rad;
  const cy = Math.max(
    3.3 + 0.6 * Math.sin(t * 0.07),
    waterHeight(cx, cz, t) + 1.5
  );
  camera.position.set(cx, cy, cz);
  camera.lookAt(sx, sy + 1.05, sz);

  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

tick();
