import * as THREE from "three";

// ---------------------------------------------------------------------------
// The Morning Break — an animated, non-interactive surfing pelican.
// Everything is procedural: the pelican, surfboard, curling wave, ocean,
// spray, clouds and distant birds are built and animated in code.
// There are deliberately no controls; the camera drifts cinematically.
// ---------------------------------------------------------------------------

const canvas = document.querySelector("#scene");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const MOTION = prefersReducedMotion ? 0.25 : 1;

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe9ec, 26, 78);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 220);
camera.position.set(0.5, 3.4, 12.2);

// --- Lighting: warm golden-hour sun with a cool sky fill -------------------
const hemisphere = new THREE.HemisphereLight(0xbfe6f2, 0x1d6b74, 0.85);
scene.add(hemisphere);

const sun = new THREE.DirectionalLight(0xffd9a0, 2.0);
sun.position.set(-9, 10, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -14;
sun.shadow.camera.right = 14;
sun.shadow.camera.top = 12;
sun.shadow.camera.bottom = -8;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 40;
sun.shadow.bias = -0.0004;
scene.add(sun);

const bounce = new THREE.DirectionalLight(0x8fd8e0, 0.45);
bounce.position.set(8, 3, -6);
scene.add(bounce);

// --- Sky dome: soft vertical gradient, warm at the horizon -----------------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(110, 32, 20),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      top: { value: new THREE.Color(0x6fb9dc) },
      mid: { value: new THREE.Color(0xbfe4ee) },
      horizon: { value: new THREE.Color(0xffe3ae) },
    },
    vertexShader: `
      varying vec3 vWorld;
      void main() {
        vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform vec3 top; uniform vec3 mid; uniform vec3 horizon;
      varying vec3 vWorld;
      void main() {
        float h = clamp(normalize(vWorld).y * 1.6 + 0.22, 0.0, 1.0);
        vec3 col = mix(horizon, mid, smoothstep(0.0, 0.45, h));
        col = mix(col, top, smoothstep(0.4, 1.0, h));
        gl_FragColor = vec4(col, 1.0);
      }`,
  }),
);
scene.add(sky);

// Visible sun disc low over the water.
const sunDisc = new THREE.Mesh(
  new THREE.SphereGeometry(2.6, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xffc46b, fog: false }),
);
sunDisc.position.set(-24, 5.8, -58);
scene.add(sunDisc);
const sunGlow = new THREE.Mesh(
  new THREE.SphereGeometry(4.6, 24, 24),
  new THREE.MeshBasicMaterial({ color: 0xffd9a0, transparent: true, opacity: 0.28, fog: false }),
);
sunGlow.position.copy(sunDisc.position);
scene.add(sunGlow);

// --- Shared helpers ---------------------------------------------------------
function standard(color, options = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.72, metalness: 0.02, ...options });
}
function shadowed(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

// --- Ocean: a wide plane animated with layered sine swells ------------------
const oceanGeometry = new THREE.PlaneGeometry(120, 80, 96, 56);
oceanGeometry.rotateX(-Math.PI / 2);
const oceanBase = oceanGeometry.attributes.position.array.slice();
const ocean = new THREE.Mesh(
  oceanGeometry,
  new THREE.MeshStandardMaterial({
    color: 0x0d7d8c,
    roughness: 0.32,
    metalness: 0.08,
  }),
);
ocean.position.set(0, -0.28, -14);
ocean.receiveShadow = true;
scene.add(ocean);

function waveHeightAt(x, z, t) {
  return (
    Math.sin(x * 0.22 + t * 0.9) * 0.22 +
    Math.sin(z * 0.3 - t * 0.7) * 0.18 +
    Math.sin((x + z) * 0.12 + t * 0.45) * 0.26
  );
}

function updateOcean(t) {
  const pos = oceanGeometry.attributes.position;
  for (let i = 0; i < pos.count; i += 1) {
    const x = oceanBase[i * 3];
    const z = oceanBase[i * 3 + 2];
    pos.setY(i, waveHeightAt(x, z, t) * MOTION + waveHeightAt(x, z, 0) * (1 - MOTION));
  }
  pos.needsUpdate = true;
  oceanGeometry.computeVertexNormals();
}

// --- The hero wave: a curling face the pelican rides -----------------------
// Built from a plane bent through a breaking-wave profile: a steep face
// rising from the trough, then a lip that curls forward over the barrel.
function buildWaveFace() {
  const geo = new THREE.PlaneGeometry(44, 7.2, 88, 36);
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const deep = new THREE.Color(0x0a6d83);
  const mid = new THREE.Color(0x14a7ba);
  const lip = new THREE.Color(0x63d8d9);
  const tmp = new THREE.Color();
  for (let i = 0; i < pos.count; i += 1) {
    const x = pos.getX(i);
    const v = (pos.getY(i) + 3.6) / 7.2; // 0 at trough, 1 at lip
    // Steep face that leans back, then curls forward at the top.
    const heightMod = 1 + Math.sin(x * 0.32) * 0.045 + Math.sin(x * 0.13 + 1.7) * 0.055;
    const rise = Math.pow(v, 1.25) * 5.4 * heightMod;
    const leanBack = -Math.pow(v, 1.6) * 3.1;
    const curlT = THREE.MathUtils.smoothstep(v, 0.68, 1.0);
    const curlForward = curlT * curlT * 4.1;
    const curlDrop = curlT * curlT * 1.7 * heightMod;
    // The ends of the wave peel lower so the barrel feels open in the middle.
    const edgeDrop = Math.pow(Math.abs(x) / 22, 2.4) * 1.5 * v;
    pos.setXYZ(i, x, rise - curlDrop - edgeDrop, leanBack + curlForward);
    // Gradient from deep trough to sunlit lip gives the face its form.
    if (v < 0.55) tmp.copy(deep).lerp(mid, v / 0.55);
    else tmp.copy(mid).lerp(lip, (v - 0.55) / 0.45);
    colors[i * 3] = tmp.r;
    colors[i * 3 + 1] = tmp.g;
    colors[i * 3 + 2] = tmp.b;
  }
  geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  return geo;
}

const waveGroup = new THREE.Group();
waveGroup.position.set(0, -0.72, -4.3);
scene.add(waveGroup);

const waveFace = new THREE.Mesh(
  buildWaveFace(),
  new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.55,
    metalness: 0,
    side: THREE.DoubleSide,
  }),
);
waveFace.receiveShadow = true;
waveGroup.add(waveFace);

// Foam lip: a broken chain of soft white blobs tracing the curling crest.
const foamMaterial = standard(0xffffff, { roughness: 1, emissive: 0xa8c4d4, emissiveIntensity: 0.28 });
const foamBlobs = [];
for (let i = 0; i < 24; i += 1) {
  const x = -18 + (i / 23) * 36;
  const edgeDrop = Math.pow(Math.abs(x) / 22, 2.4) * 1.5;
  const heightMod = 1 + Math.sin(x * 0.32) * 0.045 + Math.sin(x * 0.13 + 1.7) * 0.055;
  const blob = new THREE.Mesh(new THREE.SphereGeometry(0.22 + Math.random() * 0.16, 10, 8), foamMaterial);
  blob.position.set(x + (Math.random() - 0.5) * 0.7, 3.38 * heightMod - edgeDrop + (Math.random() - 0.5) * 0.3, 1.3 + (Math.random() - 0.5) * 0.5);
  blob.scale.set(1.75, 0.55, 0.8);
  waveGroup.add(blob);
  foamBlobs.push({ mesh: blob, seed: Math.random() * Math.PI * 2, baseY: blob.position.y, baseScale: blob.scale.clone() });
}
// Whitewater churning at the base of the wave.
for (let i = 0; i < 18; i += 1) {
  const x = -13 + Math.random() * 26;
  const puff = new THREE.Mesh(new THREE.SphereGeometry(0.22 + Math.random() * 0.34, 10, 8), foamMaterial);
  puff.position.set(x, 0.38 + Math.random() * 0.2, 0.15 + Math.random() * 1.0);
  puff.scale.set(1.4, 0.32, 0.8);
  waveGroup.add(puff);
  foamBlobs.push({ mesh: puff, seed: Math.random() * Math.PI * 2, baseY: puff.position.y, baseScale: puff.scale.clone() });
}

// --- Surfboard: extruded pointed-oval deck with a fin -----------------------
function buildSurfboard() {
  const shape = new THREE.Shape();
  // Nose at +X, tail at -X (travel direction is +X).
  shape.moveTo(-1.7, 0);
  shape.bezierCurveTo(-1.7, 0.42, -0.7, 0.52, 0.2, 0.5);
  shape.bezierCurveTo(1.1, 0.48, 1.75, 0.28, 1.95, 0);
  shape.bezierCurveTo(1.75, -0.28, 1.1, -0.48, 0.2, -0.5);
  shape.bezierCurveTo(-0.7, -0.52, -1.7, -0.42, -1.7, 0);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.09,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.04,
    bevelSegments: 2,
    curveSegments: 24,
  });
  geo.rotateX(-Math.PI / 2);
  const board = new THREE.Group();
  const deck = shadowed(new THREE.Mesh(geo, standard(0xff5a3c, { roughness: 0.45 })));
  board.add(deck);
  // Cream racing stripe down the middle of the deck.
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.7, 0.02, 0.2),
    standard(0xfff3d6, { roughness: 0.5 }),
  );
  stripe.position.set(0.05, 0.13, 0);
  board.add(stripe);
  // Single fin under the tail.
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.3, 0.04), standard(0x12303a, { roughness: 0.5 }));
  fin.position.set(-1.25, -0.14, 0);
  fin.rotation.z = 0.25;
  board.add(fin);
  return board;
}

// --- Pelican ------------------------------------------------------------------
// Built facing the camera (+Z) in a surfer's sideways stance: feet planted
// along the board, wings spread for balance, head turned into the ride so
// the long orange beak reads in profile.
const MAT = {
  feathers: standard(0xfdfdf6, { roughness: 0.9 }),
  cream: standard(0xf6ead2, { roughness: 0.9 }),
  darkFeathers: standard(0x23272e, { roughness: 0.85 }),
  beak: standard(0xff8c2e, { roughness: 0.55 }),
  pouch: standard(0xffb03a, { roughness: 0.65 }),
  feet: standard(0xf2761f, { roughness: 0.7 }),
  eye: standard(0x14181c, { roughness: 0.25 }),
  eyeSkin: standard(0x5aa7c9, { roughness: 0.6 }),
};

function buildWing(side) {
  // side: +1 reaches toward the nose, -1 toward the tail.
  const pivot = new THREE.Group();
  const arm = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.5, 14, 10), MAT.feathers));
  arm.scale.set(1.3, 0.2, 0.4);
  arm.position.x = side * 0.55;
  pivot.add(arm);
  const tip = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.34, 12, 8), MAT.darkFeathers));
  tip.scale.set(1.15, 0.16, 0.38);
  tip.position.set(side * 1.22, -0.02, -0.05);
  pivot.add(tip);
  // Three finger-like primary feathers at the tip.
  for (let i = 0; i < 3; i += 1) {
    const feather = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.42, 6), MAT.darkFeathers));
    feather.position.set(side * (1.52 + i * 0.05), -0.03, -0.14 + i * 0.13);
    feather.rotation.z = side * -Math.PI / 2;
    feather.rotation.y = side * (-0.25 + i * 0.22);
    pivot.add(feather);
  }
  return pivot;
}

function buildFoot() {
  const foot = new THREE.Group();
  const web = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), MAT.feet));
  web.scale.set(0.9, 0.28, 1.25);
  web.position.set(0, 0.03, 0.08);
  foot.add(web);
  for (let i = -1; i <= 1; i += 1) {
    const toe = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.045, 0.24, 6), MAT.feet);
    toe.rotation.x = Math.PI / 2;
    toe.rotation.y = i * 0.35;
    toe.position.set(i * 0.09, 0.03, 0.28);
    foot.add(toe);
  }
  return foot;
}

function buildPelican() {
  const pelican = new THREE.Group();

  // Plump body, leaned slightly into the ride.
  const bodyGroup = new THREE.Group();
  bodyGroup.position.set(0, 1.02, 0);
  pelican.add(bodyGroup);
  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.66, 20, 16), MAT.feathers));
  body.scale.set(0.98, 0.9, 0.76);
  bodyGroup.add(body);
  const belly = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.52, 16, 12), MAT.cream));
  belly.scale.set(0.85, 0.75, 0.6);
  belly.position.set(0, -0.14, 0.2);
  bodyGroup.add(belly);

  // Fanned tail at the back.
  const tail = new THREE.Group();
  tail.position.set(0, 0.08, -0.52);
  for (let i = -1; i <= 1; i += 1) {
    const feather = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.55, 6), MAT.feathers));
    feather.rotation.x = -Math.PI / 2 - 0.35;
    feather.rotation.z = i * 0.3;
    feather.position.set(i * 0.13, 0, -0.16);
    tail.add(feather);
  }
  bodyGroup.add(tail);

  // Wings spread wide for balance, pivoted at the shoulders.
  const wingFront = buildWing(1);
  wingFront.position.set(0.42, 0.32, 0.02);
  wingFront.rotation.y = 0.3; // swept slightly back
  bodyGroup.add(wingFront);
  const wingBack = buildWing(-1);
  wingBack.position.set(-0.42, 0.32, 0.02);
  wingBack.rotation.y = -0.3;
  bodyGroup.add(wingBack);

  // S-curved neck: a tube swept along a gentle S, with the head at its end.
  const neckGroup = new THREE.Group();
  neckGroup.position.set(0.08, 0.42, 0.16);
  bodyGroup.add(neckGroup);
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0.02, 0.28, 0.14),
    new THREE.Vector3(0.06, 0.55, 0.02),
    new THREE.Vector3(0.1, 0.78, 0.14),
  ]);
  const neck = shadowed(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 16, 0.155, 10, false), MAT.feathers));
  neckGroup.add(neck);

  // Head turned toward the direction of travel (+X).
  const headGroup = new THREE.Group();
  headGroup.position.set(0.1, 0.82, 0.16);
  headGroup.rotation.y = 1.05;
  neckGroup.add(headGroup);
  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.27, 18, 14), MAT.feathers));
  head.scale.set(0.92, 0.9, 1.05);
  headGroup.add(head);
  // Shaggy crest feathers swept back by the sea breeze.
  for (let i = 0; i < 3; i += 1) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.3, 5), MAT.cream);
    crest.position.set(-0.08 + i * 0.07, 0.24, -0.1 - i * 0.03);
    crest.rotation.x = -0.9;
    crest.rotation.z = -0.2 + i * 0.2;
    headGroup.add(crest);
  }
  // Bare blue skin patches and bright eyes on both sides of the head.
  [1, -1].forEach((s) => {
    const eyePatch = new THREE.Mesh(new THREE.SphereGeometry(0.085, 10, 8), MAT.eyeSkin);
    eyePatch.scale.set(1, 1, 0.45);
    eyePatch.position.set(s * 0.2, 0.05, 0.16);
    eyePatch.rotation.y = s * 0.7;
    headGroup.add(eyePatch);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), MAT.eye);
    eye.position.set(s * 0.24, 0.06, 0.2);
    headGroup.add(eye);
    const glint = new THREE.Mesh(
      new THREE.SphereGeometry(0.016, 6, 6),
      new THREE.MeshBasicMaterial({ color: 0xffffff }),
    );
    glint.position.set(s * 0.265, 0.085, 0.225);
    headGroup.add(glint);
  });

  // The famous long beak: flattened upper mandible, hooked tip, and pouch.
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, -0.03, 0.24);
  headGroup.add(beakGroup);
  const upperBeak = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.15, 1.35, 12), MAT.beak));
  upperBeak.scale.set(0.85, 1, 0.55);
  upperBeak.rotation.x = Math.PI / 2;
  upperBeak.position.set(0, 0.03, 0.68);
  beakGroup.add(upperBeak);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.16, 8), MAT.beak);
  hook.position.set(0, -0.05, 1.34);
  hook.rotation.x = Math.PI;
  beakGroup.add(hook);
  const pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.3, 14, 10), MAT.pouch));
  pouch.scale.set(0.55, 0.62, 1.9);
  pouch.position.set(0, -0.17, 0.62);
  beakGroup.add(pouch);

  // Bent orange legs and webbed feet gripping the deck.
  const legs = [];
  [-0.38, 0.38].forEach((x) => {
    const leg = new THREE.Group();
    leg.position.set(x, 0.62, 0.02);
    const thigh = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.17, 10, 8), MAT.feathers));
    thigh.scale.set(0.8, 1.1, 0.8);
    leg.add(thigh);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 0.42, 7), MAT.feet);
    shin.position.set(0, -0.3, 0.06);
    shin.rotation.x = 0.18;
    leg.add(shin);
    const foot = buildFoot();
    foot.position.set(0, -0.52, 0.1);
    leg.add(foot);
    pelican.add(leg);
    legs.push(leg);
  });

  return { group: pelican, bodyGroup, neckGroup, headGroup, beakGroup, pouch, wingFront, wingBack, legs, tail };
}

// Rider = board + pelican, animated as one unit along the wave face.
const rider = new THREE.Group();
scene.add(rider);
const board = buildSurfboard();
board.position.y = 0.02;
rider.add(board);
const pelicanRig = buildPelican();
pelicanRig.group.position.y = 0.14;
rider.add(pelicanRig.group);
// A leash cord trailing from board tail to ankle adds surfer credibility.
const leashCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-1.55, 0.12, 0),
  new THREE.Vector3(-1.15, 0.02, 0.22),
  new THREE.Vector3(-0.75, 0.1, 0.14),
  new THREE.Vector3(-0.4, 0.22, 0.1),
]);
const leash = new THREE.Mesh(
  new THREE.TubeGeometry(leashCurve, 16, 0.022, 6, false),
  standard(0x12303a, { roughness: 0.6 }),
);
rider.add(leash);
// Foamy wake hugging the board so it always reads as planing on water.
const wake = new THREE.Mesh(new THREE.SphereGeometry(0.7, 14, 10), foamMaterial);
wake.scale.set(1.7, 0.12, 0.68);
wake.position.set(-0.7, -0.07, 0.08);
rider.add(wake);
const bowFoam = new THREE.Mesh(new THREE.SphereGeometry(0.4, 12, 8), foamMaterial);
bowFoam.scale.set(1.0, 0.18, 0.7);
bowFoam.position.set(1.1, -0.05, 0.08);
rider.add(bowFoam);

// --- Clouds: soft clusters of flattened spheres drifting overhead ----------
const clouds = [];
function buildCloud(scale) {
  const cloud = new THREE.Group();
  const mat = standard(0xffffff, { roughness: 1, emissive: 0xc7dbe8, emissiveIntensity: 0.32 });
  const puffs = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < puffs; i += 1) {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(0.7 + Math.random() * 0.6, 12, 8), mat);
    puff.position.set((i - puffs / 2) * 0.75, (Math.random() - 0.5) * 0.3, (Math.random() - 0.5) * 0.5);
    puff.scale.y = 0.5;
    cloud.add(puff);
  }
  cloud.scale.setScalar(scale);
  return cloud;
}
[
  [-14, 8.2, -26, 1.6],
  [9, 9.4, -30, 2.1],
  [18, 7.2, -22, 1.2],
  [-4, 10.5, -34, 1.8],
  [-20, 6.6, -18, 1.0],
].forEach(([x, y, z, s]) => {
  const cloud = buildCloud(s);
  cloud.position.set(x, y, z);
  scene.add(cloud);
  clouds.push({ group: cloud, speed: 0.12 + Math.random() * 0.18 });
});

// --- Distant seabirds: simple flapping silhouettes crossing the sky --------
const distantBirds = [];
function buildDistantBird() {
  const bird = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x2b4c57 });
  const wingGeo = new THREE.BoxGeometry(0.85, 0.03, 0.22);
  const left = new THREE.Mesh(wingGeo, mat);
  left.position.x = -0.42;
  const right = new THREE.Mesh(wingGeo, mat);
  right.position.x = 0.42;
  const leftPivot = new THREE.Group();
  leftPivot.add(left);
  const rightPivot = new THREE.Group();
  rightPivot.add(right);
  bird.add(leftPivot, rightPivot);
  const bodyBird = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), mat);
  bodyBird.scale.set(1, 0.8, 2.2);
  bird.add(bodyBird);
  return { group: bird, leftPivot, rightPivot };
}
for (let i = 0; i < 6; i += 1) {
  const b = buildDistantBird();
  b.group.position.set(-30 + i * 4.5, 8 + Math.random() * 4, -20 - Math.random() * 10);
  b.group.rotation.y = Math.PI / 2;
  scene.add(b.group);
  distantBirds.push({ ...b, speed: 1.1 + Math.random() * 0.7, seed: Math.random() * 10 });
}

// Soft round sprite generated in code so spray reads as droplets, not squares.
function makeDotTexture() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const ctx = c.getContext("2d");
  const grad = ctx.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.55, "rgba(255,255,255,0.75)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}
const dotTexture = makeDotTexture();

// --- Spray: particles kicked up behind the board's tail ---------------------
const SPRAY_COUNT = 260;
const sprayPositions = new Float32Array(SPRAY_COUNT * 3);
const sprayData = [];
for (let i = 0; i < SPRAY_COUNT; i += 1) {
  sprayData.push({ life: Math.random(), vx: 0, vy: 0, vz: 0, x: 0, y: -10, z: 0 });
}
const sprayGeometry = new THREE.BufferGeometry();
sprayGeometry.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
const spray = new THREE.Points(
  sprayGeometry,
  new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.22,
    map: dotTexture,
    transparent: true,
    opacity: 0.85,
    depthWrite: false,
    sizeAttenuation: true,
  }),
);
spray.frustumCulled = false;
scene.add(spray);

// Fine mist falling from the curling lip.
const MIST_COUNT = 160;
const mistPositions = new Float32Array(MIST_COUNT * 3);
const mistData = [];
for (let i = 0; i < MIST_COUNT; i += 1) {
  mistData.push({
    x: -13 + Math.random() * 26,
    y: 1.2 + Math.random() * 2.0,
    z: -3.2 + Math.random() * 0.8,
    speed: 0.5 + Math.random() * 0.9,
    drift: Math.random() * Math.PI * 2,
  });
}
const mistGeometry = new THREE.BufferGeometry();
mistGeometry.setAttribute("position", new THREE.BufferAttribute(mistPositions, 3));
const mist = new THREE.Points(
  mistGeometry,
  new THREE.PointsMaterial({
    color: 0xeafcff,
    size: 0.16,
    map: dotTexture,
    transparent: true,
    opacity: 0.22,
    depthWrite: false,
  }),
);
mist.frustumCulled = false;
scene.add(mist);

// --- Animation ---------------------------------------------------------------
// The ride is an endless loop on a standing wave: the pelican pumps up and
// down the face, traverses slowly along it, and throws in a little hop
// every twelve seconds. Spray, foam and camera drift sell the speed.
const clock = new THREE.Clock();
const lookTarget = new THREE.Vector3(0, 2.2, -2);
const tailWorld = new THREE.Vector3();

function updateSpray(delta) {
  rider.updateMatrixWorld();
  tailWorld.set(-1.75, 0.05, 0).applyMatrix4(rider.matrixWorld);
  for (let i = 0; i < SPRAY_COUNT; i += 1) {
    const p = sprayData[i];
    p.life -= delta * 1.4;
    if (p.life <= 0) {
      p.life = 0.45 + Math.random() * 0.55;
      p.x = tailWorld.x + (Math.random() - 0.5) * 0.3;
      p.y = tailWorld.y + Math.random() * 0.12;
      p.z = tailWorld.z + (Math.random() - 0.5) * 0.35;
      p.vx = -1.6 - Math.random() * 1.8;
      p.vy = 1.1 + Math.random() * 1.7;
      p.vz = 0.5 + (Math.random() - 0.5) * 1.1;
    }
    p.vy -= 4.2 * delta;
    p.x += p.vx * delta;
    p.y += p.vy * delta;
    p.z += p.vz * delta;
    sprayPositions[i * 3] = p.x;
    sprayPositions[i * 3 + 1] = p.y;
    sprayPositions[i * 3 + 2] = p.z;
  }
  sprayGeometry.attributes.position.needsUpdate = true;
}

function updateMist(delta, t) {
  for (let i = 0; i < MIST_COUNT; i += 1) {
    const p = mistData[i];
    p.y -= p.speed * delta * MOTION;
    if (p.y < 0.8) {
      p.y = 3.0 + Math.random() * 0.5;
      p.x = -13 + Math.random() * 26;
    }
    mistPositions[i * 3] = p.x + Math.sin(t * 0.8 + p.drift) * 0.18;
    mistPositions[i * 3 + 1] = p.y;
    mistPositions[i * 3 + 2] = p.z;
  }
  mistGeometry.attributes.position.needsUpdate = true;
}

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  updateOcean(t);
  waveGroup.position.y = -0.72 + Math.sin(t * 0.7) * 0.05 * MOTION;
  foamBlobs.forEach(({ mesh, seed, baseY, baseScale }) => {
    const pulse = 1 + Math.sin(t * 2.1 + seed) * 0.12 * MOTION;
    mesh.scale.set(baseScale.x * pulse, baseScale.y * pulse, baseScale.z * pulse);
    mesh.position.y = baseY + Math.sin(t * 1.6 + seed) * 0.05 * MOTION;
  });

  // Rider path: traverse, pump, and the occasional hop.
  const traverse = Math.sin(t * 0.34);
  const pump = Math.sin(t * 0.92);
  const pumpVel = Math.cos(t * 0.92);
  const cycle = t % 12;
  const hopU = THREE.MathUtils.clamp((cycle - 9.4) / 1.1, 0, 1);
  const hop = hopU > 0 && hopU < 1 ? Math.sin(hopU * Math.PI) : 0;

  // Sit the board on the wave-face surface itself: sample the same profile
  // used to build the face, then offset a touch toward the camera.
  const riderX = traverse * 2.5 * MOTION;
  const heightMod = 1 + Math.sin(riderX * 0.32) * 0.045 + Math.sin(riderX * 0.13 + 1.7) * 0.055;
  const vRide = 0.3 + pump * 0.11 * MOTION;
  const faceY = Math.pow(vRide, 1.25) * 5.4 * heightMod + waveGroup.position.y;
  const faceZ = -Math.pow(vRide, 1.6) * 3.1 + waveGroup.position.z;
  const riderY = faceY + 0.08 + hop * 0.75 * MOTION;
  rider.position.set(riderX, riderY, faceZ + 0.42 + hop * 0.35 * MOTION);
  rider.rotation.set(
    (0.36 + pump * 0.06) * MOTION + 0.05, // board planing on the sloped face
    traverse * -0.14 * MOTION,
    (pumpVel * 0.14 + hop * 0.35) * MOTION, // nose rises as she climbs / hops
  );

  // Pelican body language: crouch to absorb, wings counter-balance the carve.
  const crouch = (0.5 - pump * 0.5) * 0.14 * MOTION;
  pelicanRig.bodyGroup.position.y = 1.02 - crouch + Math.sin(t * 1.84) * 0.025 * MOTION;
  pelicanRig.bodyGroup.rotation.z = Math.sin(t * 0.92 + 0.6) * 0.07 * MOTION;
  pelicanRig.bodyGroup.rotation.x = 0.06 + Math.sin(t * 1.3) * 0.03 * MOTION;
  const balance = Math.sin(t * 0.92 + 0.9) * 0.22 * MOTION + hop * 0.5 * MOTION;
  pelicanRig.wingFront.rotation.z = 0.18 + balance;
  pelicanRig.wingBack.rotation.z = -0.18 + balance * 0.85;
  pelicanRig.wingFront.rotation.x = Math.sin(t * 1.7) * 0.08 * MOTION;
  pelicanRig.wingBack.rotation.x = Math.sin(t * 1.7 + 1.2) * 0.08 * MOTION;
  pelicanRig.neckGroup.rotation.z = Math.sin(t * 0.92 + 1.4) * 0.09 * MOTION;
  pelicanRig.neckGroup.rotation.x = Math.sin(t * 1.15) * 0.06 * MOTION;
  pelicanRig.headGroup.rotation.x = Math.sin(t * 1.84 + 0.4) * 0.07 * MOTION - hop * 0.12 * MOTION;
  pelicanRig.headGroup.rotation.y = 1.05 + Math.sin(t * 0.5) * 0.1 * MOTION;
  // The pouch wobbles a beat behind every pump, like a water balloon.
  const wobble = Math.sin(t * 0.92 - 1.1) * 0.09 * MOTION;
  pelicanRig.pouch.scale.set(0.55 + wobble * 0.4, 0.62 + wobble, 1.9 - wobble * 0.5);
  pelicanRig.tail.rotation.y = Math.sin(t * 2.3) * 0.18 * MOTION;
  pelicanRig.legs.forEach((leg, i) => {
    leg.rotation.x = crouch * (i === 0 ? 1.4 : 1.1);
  });

  updateSpray(delta);
  updateMist(delta, t);

  clouds.forEach(({ group, speed }) => {
    group.position.x += speed * delta * MOTION;
    if (group.position.x > 30) group.position.x = -30;
  });
  distantBirds.forEach((b) => {
    b.group.position.x += b.speed * delta * MOTION;
    b.group.position.y += Math.sin(t * 0.9 + b.seed) * 0.0025;
    if (b.group.position.x > 34) b.group.position.x = -34;
    const flap = Math.sin(t * 6 + b.seed) * 0.55 * MOTION;
    b.leftPivot.rotation.z = flap;
    b.rightPivot.rotation.z = -flap;
  });

  // Cinematic camera: a slow, endless drift that keeps the rider framed.
  // Pull back on narrow (portrait) viewports so the ride stays in frame.
  const aspectComp = THREE.MathUtils.clamp(1.12 / camera.aspect, 1, 1.9);
  camera.position.set(
    2.1 + Math.sin(t * 0.1) * 2.2 * MOTION + rider.position.x * 0.22,
    4.35 + Math.sin(t * 0.07) * 0.5 * MOTION,
    (13.8 + Math.sin(t * 0.051) * 1.1 * MOTION) * aspectComp,
  );
  lookTarget.lerp(new THREE.Vector3(rider.position.x * 0.55, rider.position.y + 1.05, rider.position.z), 0.04);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});
