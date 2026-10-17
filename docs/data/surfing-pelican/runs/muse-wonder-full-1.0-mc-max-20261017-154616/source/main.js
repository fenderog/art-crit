import * as THREE from "three";

// Pelican Break — an animated, non-interactive surfing pelican diorama.
// Everything is procedural: the curling wave, the pelican, its board,
// spray, wake, gulls and props are all built and animated in code.

const stage = document.getElementById("stage");
const fallback = document.getElementById("fallback");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
} catch (error) {
  fallback.hidden = false;
  throw error;
}
fallback.hidden = true;

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfeadf, 48, 150);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.set(0, 4.6, 17.5);

// ---------- helpers ----------
const rand = (min, max) => min + Math.random() * (max - min);
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const smoothstep = (a, b, x) => {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
const std = (color, options = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0, ...options });
function ball(radius, sx, sy, sz, material) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 24, 18), material);
  mesh.scale.set(sx, sy, sz);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xffe3b3, 0x1a7a72, 0.85));

const sunLight = new THREE.DirectionalLight(0xffd9a0, 2.4);
sunLight.position.set(-15, 20, 13);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -20;
sunLight.shadow.camera.right = 20;
sunLight.shadow.camera.top = 20;
sunLight.shadow.camera.bottom = -12;
sunLight.shadow.camera.near = 2;
sunLight.shadow.camera.far = 70;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xbfeaff, 0.65);
fillLight.position.set(10, 12, 18);
scene.add(fillLight);

// ---------- sky, sun disc, clouds ----------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(230, 32, 18),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x3f9fd8) },
      midColor: { value: new THREE.Color(0x8fd8e8) },
      horizonColor: { value: new THREE.Color(0xffd9a3) },
      sunDir: { value: new THREE.Vector3(-0.5, 0.22, -1).normalize() },
      sunColor: { value: new THREE.Color(0xffb85c) },
    },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      varying vec3 vDir;
      uniform vec3 topColor, midColor, horizonColor, sunDir, sunColor;
      void main() {
        float h = clamp(vDir.y, -0.08, 1.0);
        vec3 col = mix(horizonColor, midColor, smoothstep(0.0, 0.28, h));
        col = mix(col, topColor, smoothstep(0.22, 0.75, h));
        float glow = pow(max(dot(normalize(vDir), sunDir), 0.0), 18.0);
        col += sunColor * glow * 0.55;
        gl_FragColor = vec4(col, 1.0);
      }`,
  })
);
scene.add(sky);

const sunPosition = new THREE.Vector3(-52, 20, -105);

function makeGlowTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 128;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createRadialGradient(64, 64, 2, 64, 64, 64);
  gradient.addColorStop(0, "rgba(255, 214, 150, 0.9)");
  gradient.addColorStop(0.4, "rgba(255, 184, 92, 0.35)");
  gradient.addColorStop(1, "rgba(255, 184, 92, 0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(canvas);
}
const sunGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({ map: makeGlowTexture(), transparent: true, depthWrite: false, fog: false })
);
sunGlow.scale.setScalar(52);
sunGlow.position.copy(sunPosition);
scene.add(sunGlow);

const cloudMaterial = std(0xffffff, { roughness: 1, emissive: 0xfff1d6, emissiveIntensity: 0.35 });
const clouds = [];
for (let i = 0; i < 6; i++) {
  const cloud = new THREE.Group();
  const puffs = 3 + Math.floor(Math.random() * 3);
  for (let p = 0; p < puffs; p++) {
    const puff = ball(rand(1.6, 2.8), rand(1.4, 2.1), 0.5, 1, cloudMaterial);
    puff.castShadow = false;
    puff.position.set(p * rand(1.6, 2.2) - puffs * 0.9, rand(-0.3, 0.4), rand(-0.6, 0.6));
    cloud.add(puff);
  }
  cloud.position.set(rand(-80, 80), rand(15, 27), rand(-95, -55));
  cloud.userData.speed = rand(0.25, 0.6);
  scene.add(cloud);
  clouds.push(cloud);
}

// ---------- ocean ----------
const OCEAN_SEG = 52;
const oceanGeometry = new THREE.PlaneGeometry(170, 170, OCEAN_SEG, OCEAN_SEG);
oceanGeometry.rotateX(-Math.PI / 2);
const oceanBase = oceanGeometry.attributes.position.array.slice();
const ocean = new THREE.Mesh(
  oceanGeometry,
  std(0x14919b, { roughness: 0.55, flatShading: true })
);
ocean.receiveShadow = true;
scene.add(ocean);

function oceanHeight(x, z, t) {
  return (
    0.17 * Math.sin(x * 0.32 + t * 1.1) +
    0.13 * Math.sin(z * 0.4 - t * 0.85) +
    0.07 * Math.sin((x + z) * 0.21 + t * 0.6)
  );
}

// ---------- the hero wave ----------
// Profile runs toe (s=0) -> face -> crest -> curling lip (s=1), extruded
// along x with the shoulders tapering down into the ocean.
const WAVE_HALF = 13.5;
function waveTaper(x) {
  return 1 - 0.62 * Math.pow(Math.abs(x) / WAVE_HALF, 2.3);
}
function wavePoint(s, x, out = new THREE.Vector3()) {
  const rise = -0.7 + 7.5 * Math.pow(s, 1.15) - smoothstep(0.82, 1, s) * 1.7;
  const push = 5.4 - 5.9 * Math.pow(s, 1.3) + smoothstep(0.78, 1, s) * 2.7;
  const taper = waveTaper(x);
  out.set(
    x,
    -0.7 + (rise + 0.7) * taper,
    push + (5.4 - push) * (1 - taper) * 0.4 - 1.2
  );
  return out;
}
function waveNormal(s, x) {
  const e = 0.02;
  const p = wavePoint(s, x);
  const ps = wavePoint(Math.min(1, s + e), x);
  const px = wavePoint(s, x + 0.15);
  const ts = ps.sub(p);
  const tx = px.sub(wavePoint(s, x));
  const n = new THREE.Vector3().crossVectors(tx, ts).normalize();
  if (n.y < 0) n.negate();
  // Lip points curl toward the viewer; keep normals facing out of the face.
  return n;
}

const WAVE_SX = 76;
const WAVE_SS = 30;
const waveGeometry = new THREE.BufferGeometry();
{
  const positions = new Float32Array((WAVE_SX + 1) * (WAVE_SS + 1) * 3);
  const indices = [];
  const v = new THREE.Vector3();
  let k = 0;
  for (let i = 0; i <= WAVE_SS; i++) {
    for (let j = 0; j <= WAVE_SX; j++) {
      wavePoint(i / WAVE_SS, -WAVE_HALF + (2 * WAVE_HALF * j) / WAVE_SX, v);
      positions[k++] = v.x;
      positions[k++] = v.y;
      positions[k++] = v.z;
    }
  }
  for (let i = 0; i < WAVE_SS; i++) {
    for (let j = 0; j < WAVE_SX; j++) {
      const a = i * (WAVE_SX + 1) + j;
      const b = a + 1;
      const c = a + WAVE_SX + 1;
      const d = c + 1;
      indices.push(a, c, b, b, c, d);
    }
  }
  waveGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  waveGeometry.setIndex(indices);
  waveGeometry.computeVertexNormals();
}
const waveBase = waveGeometry.attributes.position.array.slice();
const waveMesh = new THREE.Mesh(
  waveGeometry,
  std(0x23bfa9, { roughness: 0.48, side: THREE.DoubleSide })
);
waveMesh.receiveShadow = true;
waveMesh.castShadow = true;
scene.add(waveMesh);

// Foam lip: a chunky white tube tracing the curl, plus scattered blobs.
const foamMaterial = std(0xffffff, { roughness: 0.95, emissive: 0xffffff, emissiveIntensity: 0.22 });
{
  const lipPoints = [];
  for (let j = 0; j <= 16; j++) {
    lipPoints.push(wavePoint(0.985, -WAVE_HALF + (2 * WAVE_HALF * j) / 16));
  }
  const lip = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(lipPoints), 64, 0.34, 10),
    foamMaterial
  );
  lip.castShadow = true;
  scene.add(lip);
}
const foamBlobs = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 9), foamMaterial, 110);
{
  const dummy = new THREE.Object3D();
  const v = new THREE.Vector3();
  for (let i = 0; i < 110; i++) {
    const nearLip = i < 70;
    const s = nearLip ? rand(0.9, 1) : rand(0, 0.1);
    const x = rand(-WAVE_HALF, WAVE_HALF) * 0.96;
    wavePoint(s, x, v);
    dummy.position.set(v.x + rand(-0.3, 0.3), v.y + rand(-0.08, 0.22), v.z + rand(-0.25, 0.35));
    const sc = rand(0.12, 0.34);
    dummy.scale.set(sc * rand(1.2, 2), sc * 0.5, sc);
    dummy.rotation.y = rand(0, Math.PI);
    dummy.updateMatrix();
    foamBlobs.setMatrixAt(i, dummy.matrix);
  }
}
foamBlobs.castShadow = true;
scene.add(foamBlobs);

// ---------- props: island, buoy, gulls, fish ----------
{
  const island = new THREE.Group();
  const sand = new THREE.Mesh(new THREE.ConeGeometry(7.5, 2.2, 24), std(0xe8d8a8, { roughness: 1 }));
  sand.position.y = 0.4;
  island.add(sand);
  const grass = new THREE.Mesh(new THREE.ConeGeometry(4.6, 1.6, 24), std(0x3f9e63, { roughness: 1 }));
  grass.position.y = 1.6;
  island.add(grass);
  for (const [px, pz, lean] of [[-1.4, 0.4, 0.24], [1.6, -0.8, -0.18]]) {
    const palm = new THREE.Group();
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(0.16, 0.26, 3.6, 8),
      std(0x8a6a4a, { roughness: 1 })
    );
    trunk.position.y = 1.8;
    trunk.rotation.z = lean;
    palm.add(trunk);
    const crown = new THREE.Group();
    crown.position.set(-Math.sin(lean) * 3.4, 3.55, 0);
    for (let f = 0; f < 7; f++) {
      const frond = new THREE.Mesh(
        new THREE.ConeGeometry(0.3, 2.4, 6),
        std(0x2e8f57, { roughness: 1 })
      );
      frond.scale.set(1, 1, 0.28);
      frond.position.y = 0.9;
      const holder = new THREE.Group();
      holder.rotation.y = (f / 7) * Math.PI * 2;
      holder.rotation.z = 1.05;
      holder.add(frond);
      crown.add(holder);
    }
    palm.add(crown);
    palm.position.set(px, 2, pz);
    island.add(palm);
  }
  island.position.set(-22, 0, -27);
  island.scale.setScalar(1.3);
  scene.add(island);
}

const buoy = new THREE.Group();
{
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.72, 0.9, 14), std(0xe84a3c, { roughness: 0.6 }));
  base.castShadow = true;
  buoy.add(base);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.57, 0.6, 0.28, 14), std(0xffffff, { roughness: 0.6 }));
  band.position.y = 0.12;
  buoy.add(band);
  const top = ball(0.3, 1, 1, 1, std(0xffc857, { roughness: 0.4 }));
  top.position.y = 0.75;
  buoy.add(top);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.9, 8), std(0x073b3a));
  pole.position.y = 1.1;
  buoy.add(pole);
  const flag = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.3, 0.03), std(0xff6b5e));
  flag.position.set(0.3, 1.35, 0);
  buoy.add(flag);
  buoy.position.set(8.8, 0.2, 8.4);
  scene.add(buoy);
}

const gulls = [];
for (let i = 0; i < 3; i++) {
  const gull = new THREE.Group();
  const bodyMesh = ball(0.32, 0.8, 0.65, 1.7, std(0xffffff));
  bodyMesh.castShadow = false;
  gull.add(bodyMesh);
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.34, 8), std(0xffa62b));
  beak.rotation.x = Math.PI / 2;
  beak.position.set(0, 0.02, 0.62);
  gull.add(beak);
  const wingGeo = new THREE.BoxGeometry(1.15, 0.035, 0.34);
  const wingMat = std(0xf4f7f7, { side: THREE.DoubleSide, emissive: 0xffffff, emissiveIntensity: 0.18 });
  const wingL = new THREE.Group();
  const wingR = new THREE.Group();
  const meshL = new THREE.Mesh(wingGeo, wingMat);
  meshL.position.x = 0.58;
  const meshR = new THREE.Mesh(wingGeo, wingMat);
  meshR.position.x = -0.58;
  wingL.add(meshL);
  wingR.add(meshR);
  wingL.position.y = wingR.position.y = 0.08;
  gull.add(wingL, wingR);
  gull.userData = {
    wingL,
    wingR,
    radius: rand(17, 27),
    height: rand(9.5, 13.5),
    speed: rand(0.14, 0.22) * (i % 2 ? -1 : 1),
    phase: rand(0, Math.PI * 2),
    flap: rand(5.5, 7),
  };
  scene.add(gull);
  gulls.push(gull);
}

const fish = new THREE.Group();
{
  const bodyMesh = ball(0.3, 0.7, 0.8, 1.6, std(0xff8c42, { roughness: 0.5 }));
  fish.add(bodyMesh);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.4, 8), std(0xe84a3c, { roughness: 0.5 }));
  tail.rotation.x = -Math.PI / 2;
  tail.position.z = -0.58;
  fish.add(tail);
  const eye = ball(0.05, 1, 1, 1, std(0x1a1a1a, { roughness: 0.3 }));
  eye.position.set(0.16, 0.08, 0.3);
  fish.add(eye);
  fish.position.set(-6.2, -1, 8.4);
  scene.add(fish);
}
const splashRing = new THREE.Mesh(
  new THREE.TorusGeometry(0.5, 0.07, 8, 24),
  std(0xffffff, { transparent: true, opacity: 0 })
);
splashRing.rotation.x = Math.PI / 2;
splashRing.position.set(-6.2, 0.15, 8.4);
scene.add(splashRing);

// ---------- surfboard ----------
// Local space: nose +Z, deck at y=0, width along X.
const surfGroup = new THREE.Group(); // rides the wave surface
const boardGroup = new THREE.Group(); // hop + trim motion
surfGroup.add(boardGroup);
scene.add(surfGroup);

{
  const shape = new THREE.Shape();
  shape.moveTo(0, -1.8);
  shape.bezierCurveTo(0.48, -1.68, 0.52, -0.4, 0.44, 0.7);
  shape.quadraticCurveTo(0.36, 1.5, 0, 1.9);
  shape.quadraticCurveTo(-0.36, 1.5, -0.44, 0.7);
  shape.bezierCurveTo(-0.52, -0.4, -0.48, -1.68, 0, -1.8);
  const boardGeo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.09,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 2,
    curveSegments: 24,
  });
  boardGeo.rotateX(Math.PI / 2); // shape +Y becomes nose +Z, deck lands on y=0
  const board = new THREE.Mesh(boardGeo, std(0xff6b5e, { roughness: 0.38 }));
  board.castShadow = true;
  board.receiveShadow = true;
  boardGroup.add(board);

  const stripeCream = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.016, 2.9), std(0xfff3d6, { roughness: 0.45 }));
  stripeCream.position.set(0, 0.04, 0.05);
  boardGroup.add(stripeCream);
  for (const sx of [-0.3, 0.3]) {
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.016, 2.5), std(0x0f766e, { roughness: 0.45 }));
    stripe.position.set(sx, 0.04, -0.05);
    boardGroup.add(stripe);
  }
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.42, -0.08);
  finShape.lineTo(0.1, -0.34);
  finShape.lineTo(0, -0.34);
  finShape.closePath();
  const finGeo = new THREE.ExtrudeGeometry(finShape, { depth: 0.05, bevelEnabled: false });
  const fin = new THREE.Mesh(finGeo, std(0x073b3a, { roughness: 0.5 }));
  fin.rotation.y = Math.PI / 2;
  fin.position.set(0.025, -0.08, -1.55);
  boardGroup.add(fin);
}

// ---------- the pelican ----------
// Stands on the board facing +Z, chest turned a touch toward the audience.
const pelican = new THREE.Group();
pelican.position.set(0, 0.045, -0.1);
pelican.rotation.y = -0.42;
boardGroup.add(pelican);

const featherWhite = std(0xffffff, { roughness: 0.85 });
const featherShade = std(0xe8f0ee, { roughness: 0.9 });
const beakOrange = std(0xff8c42, { roughness: 0.55 });
const pouchPink = std(0xffa26b, { roughness: 0.7 });
const inkBlack = std(0x22262b, { roughness: 0.6 });

// Webbed feet planted in a surfer stance, short orange legs.
for (const [fx, fz] of [[0.16, 0.38], [-0.16, -0.42]]) {
  const foot = ball(0.16, 1, 0.32, 1.9, beakOrange);
  foot.position.set(fx, 0.05, fz);
  pelican.add(foot);
  for (const toeX of [-0.07, 0, 0.07]) {
    const toe = ball(0.045, 1, 0.7, 1.6, beakOrange);
    toe.position.set(fx + toeX, 0.045, fz + 0.28);
    pelican.add(toe);
  }
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.065, 0.4, 10), beakOrange);
  leg.castShadow = true;
  leg.position.set(fx * 0.9, 0.26, fz * 0.92);
  leg.rotation.x = fz > 0 ? -0.14 : 0.14;
  pelican.add(leg);
}

const bodyGroup = new THREE.Group();
bodyGroup.position.y = 0.82;
pelican.add(bodyGroup);
{
  const bodyMesh = ball(0.62, 0.95, 0.88, 1.28, featherWhite);
  bodyGroup.add(bodyMesh);
  const belly = ball(0.5, 0.85, 0.75, 1.05, featherShade);
  belly.position.set(0, -0.18, 0.12);
  bodyGroup.add(belly);
}
const tailGroup = new THREE.Group();
tailGroup.position.set(0, 0.06, -0.68);
bodyGroup.add(tailGroup);
{
  const tail = ball(0.3, 1.5, 0.22, 1.1, featherWhite);
  tail.position.z = -0.18;
  tailGroup.add(tail);
  const tailTip = ball(0.22, 1.6, 0.2, 0.7, inkBlack);
  tailTip.position.z = -0.42;
  tailGroup.add(tailTip);
  tailGroup.rotation.x = -0.35;
}

// Wings spread for balance: white inner wing, black flight feathers.
function buildWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(side * 0.48, 0.22, -0.08);
  const inner = ball(0.5, 1.7, 0.22, 0.78, featherWhite);
  inner.position.x = side * 0.72;
  pivot.add(inner);
  const tip = ball(0.42, 1.5, 0.2, 0.66, inkBlack);
  tip.position.x = side * 1.62;
  tip.position.z = -0.04;
  pivot.add(tip);
  for (let f = 0; f < 3; f++) {
    const feather = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.03, 0.09), inkBlack);
    feather.castShadow = true;
    feather.position.set(side * (2.02 + f * 0.05), 0, -0.16 + f * 0.15);
    feather.rotation.y = side * (-0.3 + f * 0.28);
    pivot.add(feather);
  }
  bodyGroup.add(pivot);
  return pivot;
}
const wingRight = buildWing(1);
const wingLeft = buildWing(-1);

// S-curved neck, head, long orange beak and wobbly throat pouch.
const neckGroup = new THREE.Group();
neckGroup.position.set(0, 0.3, 0.5);
bodyGroup.add(neckGroup);
{
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, -0.05, 0),
    new THREE.Vector3(0, 0.26, -0.17),
    new THREE.Vector3(0, 0.6, -0.04),
    new THREE.Vector3(0, 0.88, 0.2),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 20, 0.185, 12), featherWhite);
  neck.castShadow = true;
  neckGroup.add(neck);
}
const headGroup = new THREE.Group();
headGroup.position.set(0, 0.94, 0.24);
neckGroup.add(headGroup);
const eyes = [];
let pouch;
{
  const skull = ball(0.34, 0.92, 0.86, 1.08, featherWhite);
  headGroup.add(skull);
  for (let c = 0; c < 3; c++) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.26, 8), featherWhite);
    crest.castShadow = true;
    crest.position.set((c - 1) * 0.09, 0.32, -0.14);
    crest.rotation.x = -0.5;
    crest.rotation.z = (c - 1) * 0.3;
    headGroup.add(crest);
  }
  for (const side of [1, -1]) {
    const eye = ball(0.052, 1, 1, 1, std(0x14171c, { roughness: 0.25 }));
    eye.position.set(side * 0.2, 0.09, 0.25);
    headGroup.add(eye);
    eyes.push(eye);
    const glint = ball(0.018, 1, 1, 1, std(0xffffff, { roughness: 0.2 }));
    glint.position.set(side * 0.22, 0.13, 0.29);
    headGroup.add(glint);
    const cheek = ball(0.09, 1, 0.6, 0.6, pouchPink);
    cheek.position.set(side * 0.26, -0.06, 0.14);
    headGroup.add(cheek);
  }
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, -0.03, 0.3);
  beakGroup.rotation.x = 0.1;
  headGroup.add(beakGroup);
  const upperBeak = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.105, 1.2, 12), beakOrange);
  upperBeak.castShadow = true;
  upperBeak.geometry.rotateX(Math.PI / 2);
  upperBeak.position.z = 0.58;
  upperBeak.scale.set(0.82, 1.15, 1);
  beakGroup.add(upperBeak);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.16, 8), beakOrange);
  hook.castShadow = true;
  hook.rotation.x = Math.PI;
  hook.position.set(0, -0.05, 1.18);
  beakGroup.add(hook);
  pouch = ball(0.3, 0.92, 1, 2.15, pouchPink);
  pouch.position.set(0, -0.24, 0.42);
  beakGroup.add(pouch);
  const pouchShadow = ball(0.24, 0.8, 0.55, 2, std(0xf08a52, { roughness: 0.75 }));
  pouchShadow.position.set(0, -0.36, 0.4);
  beakGroup.add(pouchShadow);
}

// ---------- spray particles (board tail + lip drizzle) ----------
const SPRAY_COUNT = 460;
const sprayPositions = new Float32Array(SPRAY_COUNT * 3).fill(-60);
const sprayData = Array.from({ length: SPRAY_COUNT }, () => ({
  life: 0,
  maxLife: 1,
  vx: 0,
  vy: 0,
  vz: 0,
}));
let sprayCursor = 0;
const sprayGeometry = new THREE.BufferGeometry();
sprayGeometry.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
function makeDotTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 64;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  gradient.addColorStop(0, "rgba(255,255,255,1)");
  gradient.addColorStop(0.6, "rgba(255,255,255,0.7)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(canvas);
}
const spray = new THREE.Points(
  sprayGeometry,
  new THREE.PointsMaterial({
    size: 0.22,
    map: makeDotTexture(),
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    color: 0xffffff,
  })
);
spray.frustumCulled = false;
scene.add(spray);

function emitSpray(origin, dirX, dirY, dirZ, spread, speed, life) {
  const p = sprayData[sprayCursor];
  p.life = p.maxLife = life * rand(0.7, 1.2);
  const i = sprayCursor * 3;
  sprayPositions[i] = origin.x + rand(-0.1, 0.1);
  sprayPositions[i + 1] = origin.y + rand(-0.05, 0.08);
  sprayPositions[i + 2] = origin.z + rand(-0.1, 0.1);
  p.vx = (dirX + rand(-spread, spread)) * speed;
  p.vy = (dirY + rand(-spread * 0.4, spread)) * speed;
  p.vz = (dirZ + rand(-spread, spread)) * speed;
  sprayCursor = (sprayCursor + 1) % SPRAY_COUNT;
}

// ---------- foamy wake left on the wave face ----------
const WAKE_COUNT = 26;
const wakePool = [];
for (let i = 0; i < WAKE_COUNT; i++) {
  const blob = new THREE.Mesh(
    new THREE.SphereGeometry(0.5, 14, 10),
    std(0xffffff, { roughness: 1, transparent: true, opacity: 0 })
  );
  blob.scale.set(1.1, 0.16, 0.6);
  blob.visible = false;
  blob.userData.age = 99;
  scene.add(blob);
  wakePool.push(blob);
}
let wakeCursor = 0;
let wakeTimer = 0;

// ---------- animation ----------
const MOTION = reduceMotion ? 0.35 : 1;
const clock = new THREE.Clock();
const lookTarget = new THREE.Vector3(0, 2.6, 0.4);
const _v1 = new THREE.Vector3();
const _v2 = new THREE.Vector3();
const _v3 = new THREE.Vector3();
const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _qBank = new THREE.Quaternion();
const Z_AXIS = new THREE.Vector3(0, 0, 1);

let yaw = 0.6;
let prevCos = 1;
let hopStart = -10;
let hopWasActive = false;
let pouchSquash = 0;
let riderX = 0;
let riderS = 0.5;

function wrapAngle(a) {
  return Math.atan2(Math.sin(a), Math.cos(a));
}

function updateWater(t) {
  const op = oceanGeometry.attributes.position;
  for (let i = 0; i < op.count; i++) {
    const bx = oceanBase[i * 3];
    const bz = oceanBase[i * 3 + 2];
    op.array[i * 3 + 1] = oceanHeight(bx, bz, t) * MOTION + (1 - MOTION) * oceanHeight(bx, bz, 0);
  }
  op.needsUpdate = true;

  const wp = waveGeometry.attributes.position;
  const amp = 0.055 * MOTION;
  for (let idx = 0; idx < wp.count; idx++) {
    const row = Math.floor(idx / (WAVE_SX + 1));
    const s = row / WAVE_SS;
    const bx = waveBase[idx * 3];
    wp.array[idx * 3 + 1] = waveBase[idx * 3 + 1] + Math.sin(bx * 1.25 + t * 2.3 + s * 7) * amp * s;
    wp.array[idx * 3 + 2] = waveBase[idx * 3 + 2] + Math.sin(bx * 0.85 - t * 1.6 + s * 4) * amp * 0.9 * s;
  }
  wp.needsUpdate = true;
  waveGeometry.computeVertexNormals();
}

function updateRider(t, dt) {
  const p = t * 0.42;
  const sinP = Math.sin(p);
  const cosP = Math.cos(p);
  riderX = 4.9 * sinP;
  riderS = 0.5 - 0.08 * Math.cos(2 * p); // drop for speed mid-face, climb into each turn

  // A playful hop at every cutback (when travel direction reverses).
  if (Math.sign(cosP) !== Math.sign(prevCos) && prevCos !== 0) {
    hopStart = t;
    boardGroup.localToWorld(_v1.set(0, 0.05, -1.65));
    for (let i = 0; i < 26; i++) emitSpray(_v1, rand(-0.6, 0.6), 1, rand(-0.6, 0.6), 0.5, rand(1.6, 3), 0.7);
  }
  prevCos = cosP;
  const hopPhase = (t - hopStart) / 0.62;
  const hopping = hopPhase >= 0 && hopPhase < 1 && !reduceMotion;
  if (hopWasActive && !hopping) pouchSquash = 1;
  hopWasActive = hopping;
  const hopLift = hopping ? Math.sin(hopPhase * Math.PI) : 0;

  // Heading: mostly across the face, always biased downhill (+Z).
  const vx = cosP * 1.5;
  const yawTarget = Math.atan2(vx, 0.62);
  yaw += wrapAngle(yawTarget - yaw) * (1 - Math.exp(-3.4 * dt));

  const pos = wavePoint(riderS, riderX, _v1);
  const normal = waveNormal(riderS, riderX);
  pos.addScaledVector(normal, 0.16 + hopLift * 0.55);
  surfGroup.position.copy(pos);

  // Orient the board onto the wave surface, facing the heading.
  _v2.set(Math.sin(yaw), 0, Math.cos(yaw)); // desired forward
  _v3.copy(_v2).addScaledVector(normal, -_v2.dot(normal)).normalize(); // forward on surface
  const xAxis = new THREE.Vector3().crossVectors(normal, _v3).normalize();
  _m.makeBasis(xAxis, normal, _v3);
  _q.setFromRotationMatrix(_m);
  const bank = clamp(-cosP * 0.34, -0.42, 0.42); // lean into the carve
  _qBank.setFromAxisAngle(Z_AXIS, bank);
  _q.multiply(_qBank);
  surfGroup.quaternion.slerp(_q, 1 - Math.exp(-6 * dt));

  boardGroup.rotation.x = -hopLift * 0.28 + Math.sin(t * 2.1) * 0.02 * MOTION;
  boardGroup.position.y = Math.sin(t * 2.6) * 0.03 * MOTION;

  // Pelican body language: bob, counter-lean, look into the turn.
  const bob = Math.sin(t * 2.6) * 0.045 * MOTION;
  bodyGroup.position.y = 0.82 + bob + hopLift * 0.06;
  bodyGroup.rotation.z = -bank * 0.55;
  bodyGroup.rotation.x = Math.sin(t * 1.7) * 0.04 * MOTION - hopLift * 0.12;
  neckGroup.rotation.z = Math.sin(t * 1.3 + 1) * 0.06 * MOTION;
  neckGroup.rotation.x = Math.sin(t * 2.2) * 0.05 * MOTION;
  headGroup.rotation.y = clamp(wrapAngle(yawTarget - yaw) * 1.4, -0.55, 0.55) + Math.sin(t * 0.6) * 0.14;
  headGroup.rotation.x = 0.06 + Math.sin(t * 2.6 - 0.6) * 0.05 * MOTION;
  tailGroup.rotation.y = Math.sin(t * 3.4) * 0.32 * MOTION;

  // Wings balance like a tightrope walker, with a happy flap during hops.
  const flapBurst = hopping ? Math.sin(hopPhase * Math.PI) * (0.5 + 0.45 * Math.sin(t * 26)) : 0;
  const raiseBase = 0.22 + Math.sin(t * 2.2) * 0.13 * MOTION + flapBurst;
  const raiseRight = raiseBase + bank * 0.7;
  const raiseLeft = raiseBase - bank * 0.7;
  wingRight.rotation.z = raiseRight;
  wingLeft.rotation.z = -raiseLeft;
  wingRight.rotation.x = wingLeft.rotation.x = -0.12 + Math.sin(t * 1.9) * 0.05 * MOTION;

  // Pouch wobbles a beat behind the body, and squashes on landing.
  pouchSquash = Math.max(0, pouchSquash - dt * 3.2);
  const squash = pouchSquash * Math.sin(pouchSquash * Math.PI);
  const wobble = 1 + Math.sin(t * 3.1 - 0.9) * 0.13 * MOTION + hopLift * 0.12;
  pouch.scale.set(0.92 * (2 - wobble) * (1 + squash * 0.25), wobble * (1 - squash * 0.3), 2.15);

  // Eyelid blink every few seconds.
  const blinkCycle = t % 3.4;
  const eyeScale = blinkCycle < 0.13 ? 0.12 : 1;
  for (const eye of eyes) eye.scale.y = eyeScale;

  // Spray sheets off the board tail, harder through turns.
  boardGroup.localToWorld(_v1.set(0, 0.02, -1.7));
  _v2.set(0, 0, 1).applyQuaternion(surfGroup.quaternion);
  const sprayRate = 2 + Math.abs(cosP) * 2 + (hopping ? 3 : 0);
  for (let i = 0; i < sprayRate; i++) {
    emitSpray(
      _v1,
      -_v2.x * 0.8 + normal.x * 0.4,
      0.75,
      -_v2.z * 0.8 + normal.z * 0.4,
      0.45,
      rand(1.1, 2.4),
      rand(0.45, 0.8)
    );
  }

  // Wake blobs trail behind on the face.
  wakeTimer -= dt;
  if (wakeTimer <= 0) {
    wakeTimer = 0.14;
    const blob = wakePool[wakeCursor];
    wakeCursor = (wakeCursor + 1) % WAKE_COUNT;
    wavePoint(Math.max(0.05, riderS - 0.04), riderX, blob.position);
    blob.position.addScaledVector(waveNormal(riderS, riderX), 0.07);
    blob.rotation.set(0, yaw, 0);
    blob.userData.age = 0;
    blob.visible = true;
  }
  return { normal, hopLift };
}

function updateSprayAndWake(t, dt) {
  // Lip drizzle: droplets shake off the curling crest.
  for (let i = 0; i < 2; i++) {
    wavePoint(0.97, rand(-11, 11), _v1);
    emitSpray(_v1, rand(-0.1, 0.1), -0.1, 0.55, 0.2, rand(0.5, 1.1), rand(0.6, 1));
  }
  for (let i = 0; i < SPRAY_COUNT; i++) {
    const p = sprayData[i];
    if (p.life <= 0) continue;
    p.life -= dt;
    const k = i * 3;
    if (p.life <= 0) {
      sprayPositions[k + 1] = -60;
      continue;
    }
    p.vy -= 5.6 * dt;
    sprayPositions[k] += p.vx * dt;
    sprayPositions[k + 1] += p.vy * dt;
    sprayPositions[k + 2] += p.vz * dt;
  }
  sprayGeometry.attributes.position.needsUpdate = true;

  for (const blob of wakePool) {
    if (!blob.visible) continue;
    blob.userData.age += dt;
    const k = blob.userData.age / 1.7;
    if (k >= 1) {
      blob.visible = false;
      continue;
    }
    blob.scale.set(1.1 + k * 1.7, 0.16, 0.6 + k * 0.55);
    blob.material.opacity = 0.7 * (1 - k);
  }
}

function updateProps(t, dt) {
  for (const cloud of clouds) {
    cloud.position.x += cloud.userData.speed * dt * MOTION;
    if (cloud.position.x > 100) cloud.position.x = -100;
  }
  buoy.position.y = 0.15 + oceanHeight(buoy.position.x, buoy.position.z, t);
  buoy.rotation.x = Math.sin(t * 1.1) * 0.14 * MOTION;
  buoy.rotation.z = Math.cos(t * 0.9) * 0.16 * MOTION;

  for (const gull of gulls) {
    const u = gull.userData;
    const a = u.phase + t * u.speed;
    gull.position.set(Math.cos(a) * u.radius, u.height + Math.sin(t * 0.8 + u.phase) * 0.5, -16 + Math.sin(a) * u.radius * 0.5);
    const a2 = a + 0.02 * Math.sign(u.speed);
    _v1.set(Math.cos(a2) * u.radius, gull.position.y, -16 + Math.sin(a2) * u.radius * 0.5);
    gull.lookAt(_v1);
    const flap = 0.12 + Math.sin(t * u.flap + u.phase) * 0.55;
    u.wingL.rotation.z = flap;
    u.wingR.rotation.z = -flap;
  }

  // Fish leaps clear of the water every few seconds.
  const cycle = t % 5.5;
  if (cycle < 1 && !reduceMotion) {
    const k = cycle;
    fish.position.set(-6.2, -0.55 + Math.sin(k * Math.PI) * 1.6, 8.4 - k * 1.4);
    fish.rotation.x = -0.95 + k * 1.9;
    fish.rotation.z = Math.sin(k * Math.PI * 4) * 0.18;
    const pulse = (c) => clamp(1 - Math.abs(k - c) / 0.16, 0, 1);
    const amt = Math.max(pulse(0.04), pulse(0.96));
    splashRing.position.set(-6.2, 0.18, fish.position.z);
    splashRing.scale.setScalar(0.5 + amt * 1.7);
    splashRing.material.opacity = amt * 0.85;
  } else {
    fish.position.y = -1.4;
    splashRing.material.opacity = 0;
  }
}

function updateCamera(t, dt) {
  // On narrow (portrait) screens, pull back and follow the rider more
  // closely so the pelican stays framed at the ends of each carve.
  const narrow = camera.aspect < 1;
  const fit = narrow ? Math.min(1.6, 1 / Math.sqrt(Math.max(camera.aspect, 0.4))) : 1;
  let px = 0;
  let py = 4.6 * fit;
  let pz = 17.5 * fit;
  if (!reduceMotion) {
    const az = Math.sin(t * 0.07) * 0.17;
    const radius = (17.2 + Math.sin(t * 0.045) * 1.3) * fit;
    px = Math.sin(az) * radius + riderX * (narrow ? 0.5 : 0.25);
    py = (4.7 + Math.sin(t * 0.06 + 1) * 0.55) * (narrow ? 1.2 : 1);
    pz = Math.cos(az) * radius * 0.94 + 1.6;
  } else {
    px = riderX * (narrow ? 0.45 : 0.2);
  }
  camera.position.lerp(_v1.set(px, py, pz), 1 - Math.exp(-2.2 * dt));
  lookTarget.lerp(_v2.set(riderX * (narrow ? 0.88 : 0.62), 2.55 + Math.sin(t * 0.5) * 0.12, 0.4), 1 - Math.exp(-3 * dt));
  camera.lookAt(lookTarget);
}

function animate() {
  const rawDt = clock.getDelta();
  const dt = Math.min(rawDt, 0.05);
  const t = clock.elapsedTime;
  updateWater(t);
  updateRider(t, dt);
  updateSprayAndWake(t, dt);
  updateProps(t, dt);
  // Camera smoothing uses the (near-)raw frame gap so framing keeps up
  // with the rider even when frames arrive slowly.
  updateCamera(t, Math.min(rawDt, 0.5));
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});

