import * as THREE from "three";

// ---------- Renderer, scene, camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const HORIZON = new THREE.Color("#bfe6f5");
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(HORIZON, 18, 90);

const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 400);

// ---------- Lighting ----------
const SUN_DIR = new THREE.Vector3(-0.45, 0.55, -0.7).normalize();
scene.add(new THREE.HemisphereLight("#d7f1ff", "#1d5f78", 1.6));
const key = new THREE.DirectionalLight("#fff1d6", 2.4);
key.position.set(0.6, 1.0, 0.8);
scene.add(key);

// ---------- Sky: gradient plus a painted sun ----------
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(300, 32, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      top: { value: new THREE.Color("#2b74c9") },
      horizon: { value: HORIZON },
      sunDir: { value: SUN_DIR },
    },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 top;
      uniform vec3 horizon;
      uniform vec3 sunDir;
      varying vec3 vDir;
      void main() {
        float h = clamp(vDir.y, 0.0, 1.0);
        vec3 col = mix(horizon, top, pow(h, 0.6));
        float s = dot(normalize(vDir), sunDir);
        col += vec3(1.0, 0.9, 0.6) * (smoothstep(0.9975, 0.999, s) * 1.2 + pow(max(s, 0.0), 80.0) * 0.6);
        gl_FragColor = vec4(col, 1.0);
        #include <colorspace_fragment>
      }
    `,
  })
);
sky.renderOrder = -1;
scene.add(sky);

// ---------- Ocean ----------
const SEA_W = 90;
const SEA_D = 90;
const seaGeo = new THREE.PlaneGeometry(SEA_W, SEA_D, 180, 120);
seaGeo.rotateX(-Math.PI / 2);
const seaPos = seaGeo.attributes.position;
const seaCol = new THREE.BufferAttribute(new Float32Array(seaPos.count * 3), 3);
seaGeo.setAttribute("color", seaCol);
const sea = new THREE.Mesh(
  seaGeo,
  new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.25, metalness: 0 })
);
scene.add(sea);

const K = 0.75; // wave number along x; the swell travels toward +x

// Height of the travelling swell at (x, z) and time t.
function waveHeight(x, z, t) {
  return (
    0.42 * Math.sin(K * x - 1.2 * t + 0.25 * Math.sin(0.5 * z)) +
    0.14 * Math.sin(1.7 * K * x - 2.1 * t + 0.9 * z) +
    0.06 * Math.sin(3.1 * x + 1.7 * z - 3.5 * t)
  );
}

const DEEP = new THREE.Color("#0b4f6c");
const MID = new THREE.Color("#1a9bb0");
const FOAM = new THREE.Color("#f4fbff");
const tmpColor = new THREE.Color();

function updateSea(t) {
  for (let i = 0; i < seaPos.count; i++) {
    const x = seaPos.getX(i);
    const z = seaPos.getZ(i);
    const h = waveHeight(x, z, t);
    seaPos.setY(i, h);

    const k = THREE.MathUtils.clamp((h + 0.6) / 1.2, 0, 1);
    tmpColor.copy(DEEP).lerp(MID, k);
    const foam = THREE.MathUtils.smoothstep(h, 0.3, 0.55);
    tmpColor.lerp(FOAM, foam * 0.9);
    seaCol.setXYZ(i, tmpColor.r, tmpColor.g, tmpColor.b);
  }
  seaPos.needsUpdate = true;
  seaCol.needsUpdate = true;
  seaGeo.computeVertexNormals();
}

// ---------- Materials and helpers ----------
const mat = (color, opts = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.6, ...opts });
const M = {
  white: mat("#f2eee6"),
  wing: mat("#7f6d56"),
  wingTip: mat("#4e4134"),
  bill: mat("#e9b93c", { roughness: 0.4 }),
  pouch: mat("#e58f2e", { roughness: 0.5 }),
  leg: mat("#e07b2a", { roughness: 0.5 }),
  eye: mat("#151515", { roughness: 0.3 }),
  board: mat("#ff5e3a", { roughness: 0.35 }),
  fin: mat("#222a33", { roughness: 0.35 }),
};

// Ellipsoid centred on pos, with radii rx/ry/rz and optional Euler rotation.
function blob(material, radii, pos, rot = [0, 0, 0]) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), material);
  m.scale.set(...radii);
  m.position.set(...pos);
  m.rotation.set(...rot);
  return m;
}

// Tapered cylinder from point a (radius ra) to point b (radius rb).
function limb(a, b, ra, rb, material) {
  const start = new THREE.Vector3(...a);
  const end = new THREE.Vector3(...b);
  const dir = end.clone().sub(start);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rb, ra, dir.length(), 14), material);
  m.position.copy(start).add(end).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  return m;
}

// Wing outline in the XY plane, extending toward -X from its shoulder.
function makeWingGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.12);
  s.quadraticCurveTo(-0.3, 0.16, -0.62, 0.04);
  s.quadraticCurveTo(-0.7, 0.0, -0.64, -0.04);
  s.quadraticCurveTo(-0.4, -0.1, 0, -0.1);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, {
    depth: 0.03,
    bevelEnabled: true,
    bevelSize: 0.012,
    bevelThickness: 0.01,
    bevelSegments: 2,
    curveSegments: 14,
  });
  g.translate(0, 0, -0.015);
  return g;
}
const wingGeo = makeWingGeometry();

// ---------- Board ----------
const board = new THREE.Group();
const fin = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.13, 0.025), M.fin);
fin.position.set(-0.85, -0.09, 0);
board.add(blob(M.board, [1.15, 0.045, 0.32], [0, 0, 0]), fin);
scene.add(board);

// ---------- Pelican (local to the board, base at the deck) ----------
const pelican = new THREE.Group();
pelican.position.y = 0.05;
board.add(pelican);

const body = blob(M.white, [0.42, 0.3, 0.27], [0, 0.75, 0], [0, 0, 0.2]);
const tail = blob(M.wingTip, [0.22, 0.05, 0.16], [-0.6, 0.58, 0], [0, 0, 0.35]);

const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0.28, 0.8, 0),
  new THREE.Vector3(0.36, 0.98, 0),
  new THREE.Vector3(0.42, 1.14, 0),
  new THREE.Vector3(0.5, 1.28, 0),
  new THREE.Vector3(0.56, 1.38, 0),
]);
const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 40, 0.085, 14, false), M.white);

const head = blob(M.white, [0.16, 0.15, 0.14], [0.58, 1.42, 0]);
const eyeL = blob(M.eye, [0.03, 0.03, 0.03], [0.6, 1.46, 0.14]);
const eyeR = blob(M.eye, [0.03, 0.03, 0.03], [0.6, 1.46, -0.14]);

const billTop = limb([0.66, 1.42, 0], [1.28, 1.3, 0], 0.07, 0.025, M.bill);
const pouch = blob(M.pouch, [0.3, 0.13, 0.08], [0.9, 1.16, 0], [0, 0, -0.12]);

const legs = [
  limb([0, 0.5, 0.12], [0.02, 0.1, 0.14], 0.04, 0.03, M.leg),
  limb([0, 0.5, -0.12], [0.02, 0.1, -0.14], 0.04, 0.03, M.leg),
  blob(M.leg, [0.1, 0.025, 0.06], [0.05, 0.07, 0.14]),
  blob(M.leg, [0.1, 0.025, 0.06], [0.05, 0.07, -0.14]),
];

pelican.add(body, tail, neck, head, eyeL, eyeR, billTop, pouch, ...legs);

// Wings pivot at the shoulder and flap in the side profile.
function makeWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(0.02, 0.92, side * 0.3);
  pivot.add(new THREE.Mesh(wingGeo, M.wing));
  pelican.add(pivot);
  return pivot;
}
const wingNear = makeWing(1);
const wingFar = makeWing(-1);

// ---------- Spray thrown off the tail ----------
const SPRAY_N = 160;
const spray = new THREE.InstancedMesh(
  new THREE.SphereGeometry(0.03, 6, 4),
  new THREE.MeshStandardMaterial({
    color: "#ffffff",
    roughness: 0.4,
    emissive: "#c9ecff",
    emissiveIntensity: 0.4,
  }),
  SPRAY_N
);
spray.frustumCulled = false;
scene.add(spray);

const particles = Array.from({ length: SPRAY_N }, () => ({
  p: new THREE.Vector3(),
  v: new THREE.Vector3(),
  life: 0,
}));
const dummy = new THREE.Object3D();
const tmpVec = new THREE.Vector3();
let sprayAcc = 0;
let nextParticle = 0;

function emitSpray(dt, origin) {
  sprayAcc += dt * 70;
  while (sprayAcc >= 1) {
    sprayAcc -= 1;
    const q = particles[nextParticle];
    nextParticle = (nextParticle + 1) % SPRAY_N;
    q.p.copy(origin).add(tmpVec.set((Math.random() - 0.5) * 0.3, 0, (Math.random() - 0.5) * 0.5));
    q.v.set(-0.8 - Math.random() * 1.4, 0.9 + Math.random() * 1.6, (Math.random() - 0.5) * 1.2);
    q.life = 0.9 + Math.random() * 0.8;
  }
}

function updateSpray(dt, t) {
  for (let i = 0; i < SPRAY_N; i++) {
    const q = particles[i];
    if (q.life > 0) {
      q.life -= dt;
      q.v.y -= 6 * dt;
      q.p.addScaledVector(q.v, dt);
      if (q.p.y < waveHeight(q.p.x, q.p.z, t) - 0.05) q.life = 0;
    }
    dummy.position.copy(q.p);
    dummy.scale.setScalar(q.life > 0 ? 1 : 0);
    dummy.updateMatrix();
    spray.setMatrixAt(i, dummy.matrix);
  }
  spray.instanceMatrix.needsUpdate = true;
}

// ---------- Clouds ----------
const cloudMat = new THREE.MeshStandardMaterial({
  color: "#ffffff",
  roughness: 1,
  emissive: "#dfe9f2",
  emissiveIntensity: 0.25,
});

function makeCloud() {
  const g = new THREE.Group();
  for (let i = 0; i < 5; i++) {
    const r = 0.8 + Math.random() * 0.9;
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), cloudMat);
    puff.position.set((i - 2) * 1.1 + (Math.random() - 0.5), (Math.random() - 0.3) * 0.6, (Math.random() - 0.5) * 0.8);
    puff.scale.y = 0.7;
    g.add(puff);
  }
  return g;
}

const clouds = [];
for (let i = 0; i < 6; i++) {
  const c = makeCloud();
  c.userData.x0 = -60 + i * 20 + Math.random() * 6;
  c.userData.speed = 0.6 + Math.random() * 0.5;
  c.position.set(c.userData.x0, 11 + Math.random() * 5, -70 - Math.random() * 40);
  scene.add(c);
  clouds.push(c);
}

// ---------- Animation ----------
const clock = new THREE.Clock();
let time = 0;

function resize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener("resize", resize);

function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  time += dt;
  const t = time;

  updateSea(t);

  // Board sits on the surface at the origin and follows its slope.
  const EPS = 0.05;
  const h0 = waveHeight(0, 0, t);
  const dhdx = (waveHeight(EPS, 0, t) - waveHeight(-EPS, 0, t)) / (2 * EPS);
  const dhdz = (waveHeight(0, EPS, t) - waveHeight(0, -EPS, t)) / (2 * EPS);
  const normal = new THREE.Vector3(-dhdx, 1, -dhdz).normalize();
  const forward = new THREE.Vector3(1, 0, 0).addScaledVector(normal, -normal.x).normalize();
  const across = new THREE.Vector3().crossVectors(forward, normal);
  board.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(forward, normal, across));
  board.position.set(0, h0 + 0.01, 0);
  board.updateMatrixWorld(true);

  // Pelican keeps its balance: partly counter-leans against the board's tilt and wobbles.
  pelican.rotation.z = -Math.atan(dhdx) * 0.6 + Math.sin(t * 1.9) * 0.04;
  pelican.position.y = 0.05 + Math.sin(t * 2.1) * 0.01;

  // Wings flap for balance, slightly out of phase.
  wingNear.rotation.z = -0.35 + 0.45 * Math.sin(t * 6);
  wingFar.rotation.z = -0.35 + 0.45 * Math.sin(t * 6 + 0.6);

  // Spray from the tail fin.
  const tailWorld = board.localToWorld(new THREE.Vector3(-1.0, 0, 0));
  emitSpray(dt, tailWorld);
  updateSpray(dt, t);

  for (const c of clouds) {
    const span = 120;
    c.position.x = ((c.userData.x0 + t * c.userData.speed + 60) % span) - 60;
  }

  // Gentle camera drift, always framing the surfer in profile.
  camera.position.set(
    0.9 + Math.sin(t * 0.17) * 0.6,
    1.75 + Math.sin(t * 0.23) * 0.15,
    4.8 - Math.sin(t * 0.11) * 0.4
  );
  camera.lookAt(0.15, 0.85, 0);

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(frame);
