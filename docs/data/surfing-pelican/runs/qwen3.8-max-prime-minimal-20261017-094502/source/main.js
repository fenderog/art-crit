import * as THREE from "three";

// ---------------------------------------------------------------------------
// Renderer / Scene / Camera
// ---------------------------------------------------------------------------
const canvas = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fd8ef, 60, 260);

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);
camera.position.set(14, 7, 16);

// ---------------------------------------------------------------------------
// Sky dome (gradient shader)
// ---------------------------------------------------------------------------
{
  const skyGeo = new THREE.SphereGeometry(400, 32, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x2f7fc4) },
      midColor: { value: new THREE.Color(0x9fd8ef) },
      bottomColor: { value: new THREE.Color(0xffe9c9) },
    },
    vertexShader: /* glsl */ `
      varying vec3 vWorld;
      void main() {
        vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 topColor;
      uniform vec3 midColor;
      uniform vec3 bottomColor;
      varying vec3 vWorld;
      void main() {
        float h = normalize(vWorld).y;
        vec3 col = h > 0.0
          ? mix(midColor, topColor, pow(clamp(h, 0.0, 1.0), 0.7))
          : mix(midColor, bottomColor, clamp(-h * 4.0, 0.0, 1.0));
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
}

// ---------------------------------------------------------------------------
// Lights
// ---------------------------------------------------------------------------
const sunDir = new THREE.Vector3(-0.5, 0.55, -0.6).normalize();

scene.add(new THREE.HemisphereLight(0xbfe6ff, 0x2e5d78, 0.85));

const sun = new THREE.DirectionalLight(0xfff2d8, 2.2);
sun.position.copy(sunDir).multiplyScalar(80);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -20;
sun.shadow.camera.right = 20;
sun.shadow.camera.top = 20;
sun.shadow.camera.bottom = -20;
sun.shadow.camera.far = 200;
scene.add(sun);
scene.add(sun.target);

// Visible sun disc
{
  const sunDisc = new THREE.Mesh(
    new THREE.SphereGeometry(9, 24, 24),
    new THREE.MeshBasicMaterial({ color: 0xfff6cf, fog: false })
  );
  sunDisc.position.copy(sunDir).multiplyScalar(360);
  scene.add(sunDisc);
}

// ---------------------------------------------------------------------------
// Ocean — shared wave field (JS + GLSL generated from the same table)
// ---------------------------------------------------------------------------
const WAVES = [
  { a: 0.85, kx: 0.16, kz: 0.1, s: 1.15 },
  { a: 0.5, kx: -0.11, kz: 0.19, s: 1.55 },
  { a: 0.32, kx: 0.27, kz: -0.14, s: 2.1 },
  { a: 0.2, kx: -0.31, kz: -0.29, s: 2.7 },
  { a: 0.12, kx: 0.47, kz: 0.38, s: 3.4 },
];

function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    h += w.a * Math.sin(w.kx * x + w.kz * z + t * w.s);
  }
  return h;
}

function waveNormal(x, z, t, out) {
  // analytic gradient
  let dx = 0, dz = 0;
  for (const w of WAVES) {
    const ph = w.kx * x + w.kz * z + t * w.s;
    const c = Math.cos(ph);
    dx += w.a * w.kx * c;
    dz += w.a * w.kz * c;
  }
  out.set(-dx, 1, -dz).normalize();
  return out;
}

const oceanUniforms = {
  uTime: { value: 0 },
  uDeep: { value: new THREE.Color(0x0b4f6c) },
  uShallow: { value: new THREE.Color(0x2fa3b8) },
  uFoam: { value: new THREE.Color(0xeafcff) },
  uSunDir: { value: sunDir.clone() },
  uSky: { value: new THREE.Color(0x9fd8ef) },
};

const oceanMat = new THREE.ShaderMaterial({
  uniforms: oceanUniforms,
  vertexShader: /* glsl */ `
    uniform float uTime;
    varying vec3 vPos;
    varying vec3 vNormal;
    void main() {
      vec3 p = position; // plane in XY, we rotate mesh; work in local x,y
      float x = p.x, z = p.y;
      float h = 0.0;
      float dx = 0.0, dz = 0.0;
      ${WAVES.map(
        (w) => `
      {
        float ph = ${w.kx.toFixed(4)} * x + ${w.kz.toFixed(4)} * z + uTime * ${w.s.toFixed(3)};
        float c = cos(ph), s = sin(ph);
        h += ${w.a.toFixed(3)} * s;
        dx += ${(w.a * w.kx).toFixed(5)} * c;
        dz += ${(w.a * w.kz).toFixed(5)} * c;
      }`
      ).join("")}
      p.z += h;
      vNormal = normalize(vec3(-dx, -dz, 1.0));
      vPos = p;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform vec3 uDeep, uShallow, uFoam, uSunDir, uSky;
    uniform float uTime;
    varying vec3 vPos;
    varying vec3 vNormal;
    void main() {
      // rotate normal into world space (mesh is rotated -PI/2 on X, z-up local -> y-up world)
      vec3 n = normalize(vec3(vNormal.x, vNormal.z, -vNormal.y));
      vec3 viewDir = normalize(cameraPosition - vec3(vPos.x, vPos.z, -vPos.y));

      float slope = clamp(n.y * 0.5 + 0.5, 0.0, 1.0);
      vec3 water = mix(uDeep, uShallow, pow(slope, 1.5));

      // foam on wave crests
      float crest = smoothstep(0.9, 1.8, vPos.z + sin(vPos.x * 0.9 + uTime * 1.7) * 0.25
                                   + sin(vPos.y * 1.3 - uTime * 2.1) * 0.15);
      water = mix(water, uFoam, crest * 0.75);

      // specular sun glint
      vec3 hv = normalize(uSunDir + viewDir);
      float spec = pow(max(dot(n, hv), 0.0), 140.0) * 1.6;

      // fresnel-ish sky reflection
      float fres = pow(1.0 - max(dot(n, viewDir), 0.0), 3.0);
      water = mix(water, uSky, fres * 0.45);
      water += spec;

      float dist = length(cameraPosition - vec3(vPos.x, vPos.z, -vPos.y));
      float fogF = smoothstep(60.0, 260.0, dist);
      water = mix(water, uSky, fogF * 0.9);

      gl_FragColor = vec4(water, 1.0);
    }
  `,
});

const ocean = new THREE.Mesh(new THREE.PlaneGeometry(500, 500, 220, 220), oceanMat);
ocean.rotation.x = -Math.PI / 2;
scene.add(ocean);

// ---------------------------------------------------------------------------
// Materials helper
// ---------------------------------------------------------------------------
const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0.0, ...opts });

const pelicanWhite = mat(0xf6f4ee);
const pelicanGrey = mat(0xb9bec6);
const pelicanDark = mat(0x6d747e);
const beakYellow = mat(0xf5b83d, { roughness: 0.5 });
const pouchOrange = mat(0xf2903f, { roughness: 0.55 });
const legOrange = mat(0xef8b32, { roughness: 0.6 });
const eyeBlack = mat(0x1a1a1a, { roughness: 0.25 });

// ---------------------------------------------------------------------------
// Pelican
// ---------------------------------------------------------------------------
const pelican = new THREE.Group();

// --- body ---
const body = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), pelicanWhite);
body.scale.set(0.85, 0.8, 1.35);
body.castShadow = true;
pelican.add(body);

// belly shading
const belly = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), pelicanGrey);
belly.scale.set(0.75, 0.62, 1.15);
belly.position.set(0, -0.28, 0.05);
pelican.add(belly);

// --- tail ---
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1.1, 12), pelicanGrey);
tail.rotation.x = Math.PI / 2 + 0.45;
tail.scale.set(1, 1, 0.45);
tail.position.set(0, 0.12, -1.5);
tail.castShadow = true;
pelican.add(tail);

// --- neck & head ---
const neck = new THREE.Group();
neck.position.set(0, 0.55, 0.95);
pelican.add(neck);

const neckMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.42, 1.05, 16), pelicanWhite);
neckMesh.position.set(0, 0.45, 0.18);
neckMesh.rotation.x = -0.42;
neckMesh.castShadow = true;
neck.add(neckMesh);

const headGroup = new THREE.Group();
headGroup.position.set(0, 1.0, 0.42);
neck.add(headGroup);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 18), pelicanWhite);
head.scale.set(0.9, 0.95, 1.05);
head.castShadow = true;
headGroup.add(head);

// little feather tuft
const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.4, 8), pelicanDark);
tuft.position.set(0, 0.42, -0.12);
tuft.rotation.x = -0.5;
headGroup.add(tuft);

// eyes
for (const s of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 12), eyeBlack);
  eye.position.set(0.27 * s, 0.14, 0.3);
  headGroup.add(eye);
  const glint = new THREE.Mesh(
    new THREE.SphereGeometry(0.025, 8, 8),
    new THREE.MeshBasicMaterial({ color: 0xffffff })
  );
  glint.position.set(0.3 * s, 0.17, 0.36);
  headGroup.add(glint);
}

// --- beak + pouch ---
const beakGroup = new THREE.Group();
beakGroup.position.set(0, -0.02, 0.36);
headGroup.add(beakGroup);

const upperBeak = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.05, 1.7, 12), beakYellow);
upperBeak.rotation.x = Math.PI / 2;
upperBeak.scale.set(1, 1, 0.55);
upperBeak.position.set(0, 0.06, 0.85);
upperBeak.castShadow = true;
beakGroup.add(upperBeak);

// beak tip hook
const beakTip = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 10), beakYellow);
beakTip.position.set(0, 0.05, 1.72);
beakGroup.add(beakTip);

// throat pouch (wobbles)
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.4, 20, 16), pouchOrange);
pouch.scale.set(0.85, 0.9, 1.9);
pouch.position.set(0, -0.24, 0.72);
pouch.castShadow = true;
beakGroup.add(pouch);

// --- wings (spread for balance) ---
function makeWing(side) {
  const wing = new THREE.Group();

  const upper = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.12, 0.7), pelicanGrey);
  upper.position.set(0.75 * side, 0, 0);
  upper.rotation.y = 0.15 * side;
  upper.castShadow = true;
  wing.add(upper);

  const lower = new THREE.Group();
  lower.position.set(1.45 * side, 0, 0);
  wing.add(lower);

  const fore = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.1, 0.55), pelicanDark);
  fore.position.set(0.6 * side, 0, -0.05);
  fore.rotation.y = 0.25 * side;
  fore.castShadow = true;
  lower.add(fore);

  // feather tips
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.06, 0.14), pelicanDark);
    f.position.set((1.25 + i * 0.02) * side, 0, -0.18 + i * 0.12);
    f.rotation.y = (0.35 + i * 0.08) * side;
    lower.add(f);
  }

  wing.userData.lower = lower;
  wing.position.set(0, 0.25, -0.25);
  return wing;
}

const wingL = makeWing(-1);
const wingR = makeWing(1);
pelican.add(wingL, wingR);

// --- legs & webbed feet (crouched surf stance) ---
function makeLeg(side) {
  const leg = new THREE.Group();
  const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.09, 0.55, 10), legOrange);
  thigh.position.y = -0.27;
  leg.add(thigh);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.07, 0.6), legOrange);
  foot.position.set(0, -0.56, 0.18);
  leg.add(foot);
  leg.position.set(0.32 * side, -0.55, 0.1);
  leg.rotation.x = 0.18;
  return leg;
}
pelican.add(makeLeg(-1), makeLeg(1));

// ---------------------------------------------------------------------------
// Surfboard
// ---------------------------------------------------------------------------
const board = new THREE.Group();
{
  const shape = new THREE.Shape();
  const L = 3.4, W = 0.62;
  shape.moveTo(0, -L / 2);
  shape.bezierCurveTo(W, -L / 2 + 0.3, W, L / 2 - 0.5, 0, L / 2);
  shape.bezierCurveTo(-W, L / 2 - 0.5, -W, -L / 2 + 0.3, 0, -L / 2);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.16,
    bevelEnabled: true,
    bevelThickness: 0.07,
    bevelSize: 0.07,
    bevelSegments: 4,
    curveSegments: 24,
  });
  geo.rotateX(Math.PI / 2);
  geo.translate(0, -0.08, 0);
  geo.scale(1, 1, 1);

  const deck = new THREE.Mesh(geo, mat(0xf2f7f7, { roughness: 0.35 }));
  deck.castShadow = true;
  deck.receiveShadow = true;
  board.add(deck);

  // stripe
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(0.22, 0.03, L * 0.86),
    mat(0xe8452f, { roughness: 0.4 })
  );
  stripe.position.y = 0.09;
  board.add(stripe);

  // fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.quadraticCurveTo(0.45, -0.1, 0.15, -0.6);
  finShape.lineTo(0, -0.55);
  const fin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(finShape, { depth: 0.06, bevelEnabled: false }),
    mat(0xe8452f, { roughness: 0.4 })
  );
  fin.position.set(-0.03, -0.05, -L / 2 + 0.5);
  fin.rotation.y = Math.PI / 2;
  fin.rotation.x = 0;
  board.add(fin);
}

// rig: board + pelican grouped so they ride waves together
const surfer = new THREE.Group();
board.rotation.y = Math.PI; // nose forward (+z travel dir)
surfer.add(board);
pelican.position.set(0, 0.62, -0.1);
pelican.rotation.x = -0.06;
surfer.add(pelican);
scene.add(surfer);

// ---------------------------------------------------------------------------
// Spray particles around the board
// ---------------------------------------------------------------------------
const SPRAY_N = 220;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_N * 3);
const sprayData = [];
for (let i = 0; i < SPRAY_N; i++) {
  sprayData.push({
    life: Math.random(),
    speed: 1.5 + Math.random() * 2.5,
    angle: Math.random() * Math.PI * 2,
    spread: Math.random(),
    size: 0.05 + Math.random() * 0.12,
  });
}
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
const sprayMat = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 0.16,
  transparent: true,
  opacity: 0.85,
  depthWrite: false,
  sizeAttenuation: true,
});
const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

// ---------------------------------------------------------------------------
// Clouds
// ---------------------------------------------------------------------------
const cloudMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 1,
  flatShading: true,
});
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const puffs = 5 + Math.floor(Math.random() * 4);
  for (let i = 0; i < puffs; i++) {
    const puff = new THREE.Mesh(
      new THREE.SphereGeometry(1.2 + Math.random() * 1.4, 10, 8),
      cloudMat
    );
    puff.position.set(
      (Math.random() - 0.5) * 6 * s,
      (Math.random() - 0.5) * 1.2 * s,
      (Math.random() - 0.5) * 2.5 * s
    );
    puff.scale.y = 0.6;
    g.add(puff);
  }
  g.position.set(x, y, z);
  g.scale.setScalar(s);
  g.userData.speed = 0.4 + Math.random() * 0.5;
  scene.add(g);
  clouds.push(g);
}
makeCloud(-45, 28, -70, 2.2);
makeCloud(50, 34, -90, 2.8);
makeCloud(10, 30, -120, 3.2);
makeCloud(-80, 26, -40, 1.8);
makeCloud(75, 30, -50, 2.0);

// ---------------------------------------------------------------------------
// Distant gliding seagulls
// ---------------------------------------------------------------------------
const gulls = [];
const gullMat = mat(0xdfe4e8, { roughness: 1 });
function makeGull() {
  const g = new THREE.Group();
  const b = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 8), gullMat);
  b.scale.set(1, 0.8, 1.8);
  g.add(b);
  const wL = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.04, 0.22), gullMat);
  wL.position.x = -0.5;
  const wR = wL.clone();
  wR.position.x = 0.5;
  g.add(wL, wR);
  g.userData = { wL, wR, phase: Math.random() * Math.PI * 2 };
  scene.add(g);
  gulls.push(g);
  return g;
}
for (let i = 0; i < 5; i++) makeGull();

// ---------------------------------------------------------------------------
// Animation loop
// ---------------------------------------------------------------------------
const clock = new THREE.Clock();
const _n = new THREE.Vector3();
const _up = new THREE.Vector3(0, 1, 0);
const _q = new THREE.Quaternion();
const _m = new THREE.Matrix4();
const _fwd = new THREE.Vector3();
const _right = new THREE.Vector3();

// surfer "travels" along +x conceptually; keep it near origin by moving waves
// instead we let the surfer weave gently around a home point
const HOME = new THREE.Vector3(0, 0, 0);

function updateSpray(t, dt, boardPos) {
  const pos = sprayGeo.attributes.position.array;
  for (let i = 0; i < SPRAY_N; i++) {
    const d = sprayData[i];
    d.life += dt * 0.9;
    if (d.life > 1) {
      d.life = 0;
      d.angle = Math.random() * Math.PI * 2;
      d.speed = 1.5 + Math.random() * 2.5;
      d.spread = Math.random();
    }
    const l = d.life;
    const r = d.speed * l * (0.6 + d.spread);
    const side = Math.sin(d.angle) > 0 ? 1 : -1;
    const x = boardPos.x - 1.4 + Math.cos(d.angle) * r * 0.4;
    const y = boardPos.y - 0.2 + r * 0.9 - 2.2 * l * l;
    const z = boardPos.z + side * (0.5 + d.spread * 0.5) + Math.sin(t * 3 + i) * 0.1;
    pos[i * 3] = x;
    pos[i * 3 + 1] = Math.max(y, waveHeight(x, z, t) + 0.05);
    pos[i * 3 + 2] = z;
  }
  sprayGeo.attributes.position.needsUpdate = true;
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  oceanUniforms.uTime.value = t;

  // --- surfer path: gentle weaving around home ---
  const px = HOME.x + Math.sin(t * 0.23) * 5.5;
  const pz = HOME.z + Math.cos(t * 0.17) * 4.5;
  const h = waveHeight(px, pz, t);
  waveNormal(px, pz, t, _n);

  surfer.position.set(px, h + 0.18, pz);

  // orient board to wave slope + travel direction
  _fwd.set(Math.cos(t * 0.23) * 0.23 * 5.5, 0, -Math.sin(t * 0.17) * 0.17 * 4.5)
    .normalize();
  if (_fwd.lengthSq() < 0.001) _fwd.set(1, 0, 0);
  // build board basis from wave normal + projected forward direction
  const proj = _fwd.clone().sub(_n.clone().multiplyScalar(_fwd.dot(_n))).normalize();
  const rt = new THREE.Vector3().crossVectors(_n, proj).normalize();
  _m.makeBasis(rt, _n, proj);
  _q.setFromRotationMatrix(_m);
  surfer.quaternion.slerp(_q, 0.15);

  // extra lean into turns
  surfer.rotateZ(Math.sin(t * 0.23) * 0.18);

  // --- pelican animation ---
  // crouch/bob with the swell
  pelican.position.y = 0.62 + Math.sin(t * 2.3) * 0.05;
  pelican.rotation.x = -0.06 + Math.sin(t * 1.9) * 0.05;
  pelican.rotation.z = Math.sin(t * 0.23) * -0.22 + Math.sin(t * 3.1) * 0.03;

  // wing balancing: dihedral flapping, asymmetric with lean
  const flap = Math.sin(t * 2.6) * 0.16;
  wingL.rotation.z = -0.35 + flap + pelican.rotation.z * 0.5;
  wingR.rotation.z = 0.35 + flap - pelican.rotation.z * 0.5;
  wingL.rotation.x = Math.sin(t * 2.6 + 1.2) * 0.1;
  wingR.rotation.x = Math.sin(t * 2.6 + 1.2) * 0.1;
  wingL.userData.lower.rotation.z = -0.2 + Math.sin(t * 2.6 + 0.6) * 0.18;
  wingR.userData.lower.rotation.z = 0.2 + Math.sin(t * 2.6 + 0.6) * 0.18;

  // head look-around + pouch wobble
  headGroup.rotation.y = Math.sin(t * 0.7) * 0.5;
  headGroup.rotation.x = Math.sin(t * 1.3) * 0.12 - 0.05;
  const wob = 1 + Math.sin(t * 3.4) * 0.06;
  pouch.scale.set(0.85 * wob, 0.9 / wob, 1.9);
  beakGroup.rotation.x = Math.sin(t * 1.1) * 0.05;

  // tail wag
  tail.rotation.y = Math.sin(t * 2.2) * 0.15;

  // --- spray ---
  updateSpray(t, dt, surfer.position);

  // --- clouds drift ---
  for (const c of clouds) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 160) c.position.x = -160;
  }

  // --- gulls circle in the distance ---
  gulls.forEach((g, i) => {
    const a = t * (0.12 + i * 0.02) + (i * Math.PI * 2) / gulls.length;
    const R = 40 + i * 9;
    g.position.set(
      Math.cos(a) * R,
      16 + Math.sin(t * 0.5 + i) * 2.5 + i * 1.5,
      Math.sin(a) * R - 30
    );
    g.rotation.y = -a + Math.PI / 2;
    g.rotation.z = 0.35; // banking
    const f = Math.sin(t * 3 + g.userData.phase) * 0.35;
    g.userData.wL.rotation.z = f;
    g.userData.wR.rotation.z = -f;
  });

  // --- camera: slow cinematic orbit, looks at surfer ---
  const camA = t * 0.08;
  const camR = 17 + Math.sin(t * 0.11) * 4;
  const camTarget = new THREE.Vector3(
    surfer.position.x * 0.6 + Math.cos(camA) * camR,
    6.5 + Math.sin(t * 0.15) * 1.5,
    surfer.position.z * 0.6 + Math.sin(camA) * camR
  );
  camera.position.lerp(camTarget, 0.05);
  const look = new THREE.Vector3().lerpVectors(
    surfer.position,
    new THREE.Vector3(surfer.position.x, surfer.position.y + 1.6, surfer.position.z),
    0.5
  );
  camera.lookAt(look);

  // keep sun shadow centered on the surfer
  sun.target.position.copy(surfer.position);
  sun.position.copy(surfer.position).addScaledVector(sunDir, 80);

  renderer.render(scene, camera);
}

animate();

// ---------------------------------------------------------------------------
// Resize
// ---------------------------------------------------------------------------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
