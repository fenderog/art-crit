import * as THREE from "three";

// ---------------------------------------------------------------- scene ----
const app = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xbfe8ff, 60, 220);

const camera = new THREE.PerspectiveCamera(
  55,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);
camera.position.set(0, 6, 18);

// ------------------------------------------------------------- lighting ----
scene.add(new THREE.HemisphereLight(0xbfe8ff, 0x1a5b7a, 0.9));
const sun = new THREE.DirectionalLight(0xfff3d6, 1.6);
sun.position.set(20, 30, 10);
scene.add(sun);

// ------------------------------------------------------------------ sky ----
const skyGeo = new THREE.SphereGeometry(300, 32, 16);
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  uniforms: {
    top: { value: new THREE.Color(0x2a7fd4) },
    bottom: { value: new THREE.Color(0xcdeeff) },
  },
  vertexShader: `varying vec3 vP; void main(){ vP = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `uniform vec3 top; uniform vec3 bottom; varying vec3 vP;
    void main(){ float h = clamp(normalize(vP).y * 1.6, 0.0, 1.0);
    gl_FragColor = vec4(mix(bottom, top, h), 1.0); }`,
});
scene.add(new THREE.Mesh(skyGeo, skyMat));

// sun disc
const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(14, 32),
  new THREE.MeshBasicMaterial({ color: 0xfff2b0, fog: false })
);
sunDisc.position.set(90, 80, -180);
sunDisc.lookAt(camera.position);
scene.add(sunDisc);

// ---------------------------------------------------------------- ocean ----
// Wave height function: a travelling swell the pelican rides, plus chop.
function waveHeight(x, z, t) {
  const swell = Math.sin(x * 0.18 - t * 1.4) * 1.6;
  const cross = Math.sin(z * 0.35 + t * 0.9) * 0.35;
  const chop = Math.sin(x * 0.9 + z * 1.3 + t * 2.2) * 0.12;
  return swell + cross + chop;
}

const oceanGeo = new THREE.PlaneGeometry(400, 400, 160, 160);
oceanGeo.rotateX(-Math.PI / 2);
const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x0e6ba8,
  roughness: 0.35,
  metalness: 0.15,
  flatShading: false,
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
scene.add(ocean);

const base = oceanGeo.attributes.position.array.slice(); // x, y, z layout

function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  const arr = pos.array;
  for (let i = 0; i < arr.length; i += 3) {
    arr[i + 1] = waveHeight(base[i], base[i + 2], t);
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

// foam: rings of small sprites near the crest around the pelican
const foamTex = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
})();

const FOAM = 240;
const foamGeo = new THREE.BufferGeometry();
foamGeo.setAttribute(
  "position",
  new THREE.BufferAttribute(new Float32Array(FOAM * 3), 3)
);
const foamMat = new THREE.PointsMaterial({
  size: 1.1,
  map: foamTex,
  transparent: true,
  depthWrite: false,
  opacity: 0.85,
});
const foam = new THREE.Points(foamGeo, foamMat);
scene.add(foam);

const foamSeeds = [];
for (let i = 0; i < FOAM; i++) {
  foamSeeds.push({
    a: Math.random() * Math.PI * 2,
    r: 0.6 + Math.random() * 4.5,
    h: Math.random(),
    s: 0.6 + Math.random() * 1.4,
  });
}

// -------------------------------------------------------------- pelican ----
const pelican = new THREE.Group();
scene.add(pelican);

const white = new THREE.MeshStandardMaterial({ color: 0xf5f2ea, roughness: 0.7 });
const grey = new THREE.MeshStandardMaterial({ color: 0x9aa3ab, roughness: 0.6 });
const beakMat = new THREE.MeshStandardMaterial({
  color: 0xf2a03d,
  roughness: 0.4,
});
const pouchMat = new THREE.MeshStandardMaterial({
  color: 0xe0703a,
  roughness: 0.5,
});
const black = new THREE.MeshStandardMaterial({ color: 0x22262b, roughness: 0.5 });

// body
const body = new THREE.Mesh(new THREE.SphereGeometry(1.1, 24, 18), white);
body.scale.set(1, 0.9, 1.5);
pelican.add(body);

// tail
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.45, 1.2, 10), grey);
tail.rotation.x = Math.PI / 2 + 0.15;
tail.position.set(0, 0.1, -1.7);
pelican.add(tail);

// neck + head (pelicans tuck the head while surfing — but keep it up, it's fun)
const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.5, 0.9, 14), white);
neck.position.set(0, 0.95, 0.95);
neck.rotation.x = -0.35;
pelican.add(neck);

const head = new THREE.Group();
head.position.set(0, 1.45, 1.35);
pelican.add(head);

const skull = new THREE.Mesh(new THREE.SphereGeometry(0.42, 20, 16), white);
head.add(skull);

// beak: long upper mandible + pouch below
const beak = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.1, 1.5), beakMat);
beak.position.set(0, 0.02, 1.0);
head.add(beak);

const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 12), pouchMat);
pouch.scale.set(0.9, 0.7, 2.6);
pouch.position.set(0, -0.14, 0.75);
head.add(pouch);

// eye
for (const s of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), black);
  eye.position.set(0.28 * s, 0.14, 0.3);
  head.add(eye);
}

// wings — flapping gently for balance; groups pivot at shoulder
const wings = [];
for (const side of [-1, 1]) {
  const wing = new THREE.Group();
  wing.position.set(0.75 * side, 0.35, 0.15);

  const inner = new THREE.Mesh(new THREE.SphereGeometry(0.8, 16, 12), grey);
  inner.scale.set(1.1, 0.16, 1.6);
  inner.position.set(0.65 * side, 0, -0.35);
  wing.add(inner);

  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.6, 14, 10), black);
  tip.scale.set(1.4, 0.1, 0.9);
  tip.position.set(1.75 * side, -0.02, -1.1);
  wing.add(tip);

  pelican.add(wing);
  wings.push(wing);
}

// feet on the board
const feet = [];
for (const side of [-1, 1]) {
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.1, 0.9), beakMat);
  foot.position.set(0.32 * side, -1.02, side > 0 ? -0.25 : 0.35);
  pelican.add(foot);
  feet.push(foot);
}

// ------------------------------------------------------------ surfboard ----
const surfboard = new THREE.Group();
pelican.add(surfboard);

const boardMat = new THREE.MeshStandardMaterial({
  color: 0xff5a3c,
  roughness: 0.3,
  metalness: 0.1,
});
const board = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 12), boardMat);
board.scale.set(0.75, 0.14, 3.2);
board.position.y = -1.12;
surfboard.add(board);

// stripe
const stripe = new THREE.Mesh(
  new THREE.BoxGeometry(0.34, 0.02, 3.0),
  new THREE.MeshStandardMaterial({ color: 0xfff6e8 })
);
stripe.position.y = -0.98;
surfboard.add(stripe);

// fin
const fin = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.5, 8), boardMat);
fin.rotation.x = Math.PI / 2.6;
fin.position.set(0, -1.35, -1.6);
surfboard.add(fin);

// wake spray behind the board
const sprayTex = foamTex;
const SPRAY = 120;
const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute(
  "position",
  new THREE.BufferAttribute(new Float32Array(SPRAY * 3), 3)
);
const sprayMat = new THREE.PointsMaterial({
  size: 0.9,
  map: sprayTex,
  transparent: true,
  depthWrite: false,
  opacity: 0.9,
  color: 0xffffff,
});
const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

const sprayParts = [];
for (let i = 0; i < SPRAY; i++) {
  sprayParts.push({
    t: Math.random(), // life 0..1
    speed: 0.25 + Math.random() * 0.5,
    x: (Math.random() - 0.5) * 1.2,
    z: -2 - Math.random() * 3,
    vy: 2.5 + Math.random() * 3,
  });
}

// ------------------------------------------------------------ animation ----
// The pelican carves back and forth across the wave (S-turns) while the
// camera drifts alongside. Non-interactive: everything is time-driven.
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  updateOcean(t);

  // pelican path: S-turn carving along z, advancing in x forever
  const px = t * 4.0; // moves toward -x visually; we recycle with modulo
  const carve = Math.sin(t * 0.7) * 6.0;
  const pxMod = ((px % 100) + 100) % 100 - 50; // wrap to stay near origin
  const x = pxMod;
  const z = carve;

  const y = waveHeight(x, z, t) + 0.35;
  pelican.position.set(x, y, z);

  // orient along motion: heading in +x, banking with the carve
  const dzdt = Math.cos(t * 0.7) * 6.0 * 0.7;
  pelican.rotation.y = -Math.atan2(dzdt, 4.0);
  pelican.rotation.z = THREE.MathUtils.lerp(
    pelican.rotation.z,
    -Math.sin(t * 0.7) * 0.35,
    0.1
  );
  // pitch follows the wave slope under the board
  const slope =
    (waveHeight(x + 0.5, z, t) - waveHeight(x - 0.5, z, t)) / 1.0;
  pelican.rotation.x = THREE.MathUtils.lerp(
    pelican.rotation.x,
    -slope * 0.35,
    0.08
  );

  // wing flapping for balance
  const flap = Math.sin(t * 3.0) * 0.25;
  wings[0].rotation.z = 0.25 + flap;
  wings[1].rotation.z = -0.25 - flap;

  // head bobs a little, looking down the wave
  head.rotation.x = -0.1 + Math.sin(t * 1.5) * 0.08;
  head.rotation.y = Math.sin(t * 0.5) * 0.15;

  // feet pump the board slightly
  feet[0].position.y = -1.02 + Math.sin(t * 2.5) * 0.05;
  feet[1].position.y = -1.02 - Math.sin(t * 2.5) * 0.05;

  // camera follows the pelican smoothly
  const cx = x + Math.sin(t * 0.2) * 3.0;
  camera.position.lerp(
    new THREE.Vector3(cx - 6, y + 5.5, z + 15),
    0.03
  );
  camera.lookAt(x, y + 1.2, z);

  // foam particles hugging the crest around the pelican
  const fp = foam.geometry.attributes.position.array;
  for (let i = 0; i < FOAM; i++) {
    const s = foamSeeds[i];
    const a = s.a + t * s.s;
    const fx = x + Math.cos(a) * s.r * 2.5;
    const fz = z + Math.sin(a) * s.r * 2.5 + 3;
    fp[i * 3] = fx;
    fp[i * 3 + 1] = waveHeight(fx, fz, t) + 0.15 + s.h * 0.5;
    fp[i * 3 + 2] = fz;
  }
  foam.geometry.attributes.position.needsUpdate = true;

  // spray from the tail of the board
  const sp = spray.geometry.attributes.position.array;
  const pp = pelican.position;
  const pr = pelican.rotation;
  for (let i = 0; i < SPRAY; i++) {
    const p = sprayParts[i];
    p.t += 0.016 * p.speed;
    if (p.t > 1) {
      p.t = 0;
      p.x = (Math.random() - 0.5) * 1.2;
      p.z = -2 - Math.random() * 3;
      p.vy = 2.5 + Math.random() * 3;
    }
    const life = p.t;
    // local spray point -> world (pelican has position + yaw only for this)
    const lx = p.x;
    const lz = p.z - life * 6.0 * p.speed;
    const ly = -1.0 + life * p.vy - life * life * 9.0;
    const cy = Math.cos(pr.y), sy = Math.sin(pr.y);
    sp[i * 3] = pp.x + lx * cy + lz * sy;
    sp[i * 3 + 1] = pp.y + ly;
    sp[i * 3 + 2] = pp.z - lx * sy + lz * cy;
  }
  spray.geometry.attributes.position.needsUpdate = true;
  sprayMat.opacity = 0.9;

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
