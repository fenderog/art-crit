import * as THREE from "three";

/* ------------------------------------------------------------------ *
 *  Pelican Surf — a small procedural, non-interactive 3D daydream.
 *  Everything (geometry, sky, clouds) is generated in code.
 * ------------------------------------------------------------------ */

const HORIZON = new THREE.Color(0.93, 0.78, 0.62);
const SUN_DIR = new THREE.Vector3(0.75, 0.26, -0.75).normalize();

const WAVES = [
  { dx: 0.9435, dz: 0.3302, amp: 0.55, k: 0.4488, speed: 1.4, phase: 0.0 },
  { dx: -0.3714, dz: 0.9285, amp: 0.38, k: 0.6981, speed: 1.9, phase: 1.7 },
  { dx: 0.8575, dz: -0.5145, amp: 0.2, k: 1.1424, speed: 2.6, phase: 4.1 },
  { dx: 0.1961, dz: 0.9806, amp: 0.12, k: 2.0944, speed: 3.2, phase: 2.6 },
  { dx: 0.995, dz: 0.0995, amp: 0.08, k: 2.856, speed: 3.9, phase: 5.2 },
];

function sampleWave(x, z, t) {
  let h = 0;
  let gx = 0;
  let gz = 0;
  for (const w of WAVES) {
    const a = (x * w.dx + z * w.dz) * w.k + t * w.speed + w.phase;
    h += w.amp * Math.sin(a);
    const c = w.amp * w.k * Math.cos(a);
    gx += w.dx * c;
    gz += w.dz * c;
  }
  return { h, gx, gz };
}

/* ----------------------------- renderer ---------------------------- */

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xeac7a0, 90, 280);

const camera = new THREE.PerspectiveCamera(
  42,
  window.innerWidth / window.innerHeight,
  0.1,
  900
);
camera.position.set(-4.5, 4.2, 9.5);

/* ------------------------------ lights ----------------------------- */

const hemi = new THREE.HemisphereLight(0xcfeaff, 0x2d5d64, 1.2);
scene.add(hemi);

const sunLight = new THREE.DirectionalLight(0xffc078, 2.35);
sunLight.position.copy(SUN_DIR).multiplyScalar(60);
scene.add(sunLight);

const fillLight = new THREE.DirectionalLight(0xa9ddec, 1.15);
fillLight.position.set(-26, 20, 34);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffe0b5, 0.75);
rimLight.position.set(10, 12, -40);
scene.add(rimLight);

const bounceLight = new THREE.DirectionalLight(0xa8dbe2, 0.65);
bounceLight.position.set(6, -8, 22);
scene.add(bounceLight);

/* -------------------------------- sky ------------------------------ */

const skyUniforms = {
  uSunDir: { value: SUN_DIR.clone() },
};

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(400, 40, 24),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: skyUniforms,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir;
      varying vec3 vDir;

      void main() {
        vec3 dir = normalize(vDir);
        float h = clamp(dir.y, -0.3, 1.0);

        vec3 horizon = vec3(1.00, 0.82, 0.61);
        vec3 mid     = vec3(0.55, 0.78, 0.84);
        vec3 top     = vec3(0.11, 0.32, 0.52);

        vec3 col = mix(horizon, mid, smoothstep(0.0, 0.17, h));
        col = mix(col, top, smoothstep(0.12, 0.78, h));

        float sd = max(dot(dir, uSunDir), 0.0);
        col += vec3(1.0, 0.62, 0.30) * pow(sd, 8.0) * 0.30;
        col += vec3(1.0, 0.76, 0.44) * pow(sd, 90.0) * 0.75;

        float disc = smoothstep(0.99925, 0.99972, sd);
        col = mix(col, vec3(1.0, 0.94, 0.78), disc * 0.95);

        // Below the horizon, ease into the sea haze.
        col = mix(vec3(0.82, 0.68, 0.54), col, smoothstep(-0.08, 0.015, dir.y));

        gl_FragColor = vec4(col, 1.0);
      }
    `,
  })
);
sky.frustumCulled = false;
scene.add(sky);

/* ------------------------------- ocean ----------------------------- */

const oceanUniforms = {
  uTime: { value: 0 },
  uSunDir: { value: SUN_DIR.clone() },
  uCamPos: { value: new THREE.Vector3() },
  uBoardPos: { value: new THREE.Vector2() },
};

const oceanMaterial = new THREE.ShaderMaterial({
  uniforms: oceanUniforms,
  vertexShader: /* glsl */ `
    uniform float uTime;
    varying vec3 vWorldPos;
    varying vec3 vNormal;

    void main() {
      vec4 wp = modelMatrix * vec4(position, 1.0);
      vec2 p = wp.xz;
      vec2 grad = vec2(0.0);
      float h = 0.0;

      #define WAVE(DX, DZ, AMP, K, SPEED, PHASE) do { \
        float a = dot(p, vec2(DX, DZ)) * (K) + uTime * (SPEED) + (PHASE); \
        h += (AMP) * sin(a); \
        grad += vec2(DX, DZ) * ((AMP) * (K) * cos(a)); \
      } while (false)

      WAVE( 0.9435,  0.3302, 0.55, 0.4488, 1.4, 0.0);
      WAVE(-0.3714,  0.9285, 0.38, 0.6981, 1.9, 1.7);
      WAVE( 0.8575, -0.5145, 0.20, 1.1424, 2.6, 4.1);
      WAVE( 0.1961,  0.9806, 0.12, 2.0944, 3.2, 2.6);
      WAVE( 0.9950,  0.0995, 0.08, 2.8560, 3.9, 5.2);

      wp.y = h;

      vWorldPos = wp.xyz;
      vNormal = normalize(vec3(-grad.x, 1.0, -grad.y));

      gl_Position = projectionMatrix * viewMatrix * wp;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform float uTime;
    uniform vec3 uSunDir;
    uniform vec3 uCamPos;
    uniform vec2 uBoardPos;
    varying vec3 vWorldPos;
    varying vec3 vNormal;

    float hash21(vec2 p) {
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }

    float vnoise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      float a = hash21(i);
      float b = hash21(i + vec2(1.0, 0.0));
      float c = hash21(i + vec2(0.0, 1.0));
      float d = hash21(i + vec2(1.0, 1.0));
      return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(uCamPos - vWorldPos);

      float fres = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 3.0);
      float rise = smoothstep(-1.1, 1.0, vWorldPos.y);

      vec3 deep = vec3(0.014, 0.150, 0.190);
      vec3 shallow = vec3(0.030, 0.400, 0.435);
      vec3 col = mix(deep, shallow, rise);

      // Soft sky reflection at grazing angles.
      col = mix(col, vec3(0.34, 0.66, 0.70), fres * 0.5);

      // Sun glitter.
      vec3 R = reflect(-V, N);
      float ndl = max(dot(R, uSunDir), 0.0);
      col += vec3(1.0, 0.76, 0.44) * pow(ndl, 240.0) * 0.85;
      col += vec3(1.0, 0.88, 0.65) * pow(ndl, 1400.0) * 1.4;

      // Foam on the crests.
      float n1 = vnoise(vWorldPos.xz * 1.45 + vec2(uTime * 0.35, -uTime * 0.28));
      float n2 = vnoise(vWorldPos.xz * 4.0 - vec2(uTime * 0.7, uTime * 0.4));
      float crest = smoothstep(0.92, 1.3, vWorldPos.y);
      float foam = crest * (0.30 + 0.70 * n1) * (0.6 + 0.4 * n2) * 0.7;

      // Contact shadow / dark water under the board.
      vec2 dp = (vWorldPos.xz - uBoardPos) / vec2(2.7, 1.05);
      float under = smoothstep(1.15, 0.15, length(dp));
      col *= 1.0 - under * 0.30;

      // Foam ring around the board.
      float dist = length(vWorldPos.xz - uBoardPos);
      float ring = smoothstep(2.7, 1.55, dist) * smoothstep(0.85, 1.25, dist);
      foam += ring * (0.35 + 0.65 * n1) * 0.75;

      // A wake trailing behind the board.
      float back = uBoardPos.x - vWorldPos.x;
      float t = clamp(back / 15.0, 0.0, 1.0);
      float width = 1.0 + t * 3.1;
      float lateral = abs(vWorldPos.z - uBoardPos.y);
      float trail = smoothstep(width, width * 0.22, lateral)
                  * (1.0 - t) * smoothstep(0.1, 0.9, back);
      foam += trail * (0.14 + 0.5 * n2) * 0.7;

      col = mix(col, vec3(0.90, 0.98, 0.98), clamp(foam, 0.0, 1.0));

      // Fade into the warm horizon.
      float dCam = length(vWorldPos.xz - uCamPos.xz);
      col = mix(col, vec3(0.93, 0.78, 0.62), smoothstep(65.0, 175.0, dCam));

      gl_FragColor = vec4(col, 1.0);
    }
  `,
});

const ocean = new THREE.Mesh(
  new THREE.PlaneGeometry(330, 330, 256, 256).rotateX(-Math.PI / 2),
  oceanMaterial
);
ocean.frustumCulled = false;
scene.add(ocean);

/* ------------------------------ clouds ----------------------------- */

function makeCloudTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 256;
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, 512, 256);

  for (let i = 0; i < 30; i++) {
    const x = 60 + Math.random() * 392;
    const y = 80 + Math.random() * 96;
    const r = 36 + Math.random() * 90;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, "rgba(255, 247, 235, 0.50)");
    g.addColorStop(0.45, "rgba(255, 242, 226, 0.20)");
    g.addColorStop(1, "rgba(255, 242, 226, 0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearFilter;
  return tex;
}

const cloudTexture = makeCloudTexture();
const cloudGroup = new THREE.Group();
scene.add(cloudGroup);

const cloudSpecs = [
  { a: 2.55, r: 255, y: 62, w: 150, h: 60, o: 0.5 },
  { a: 2.2, r: 285, y: 92, w: 200, h: 76, o: 0.36 },
  { a: 2.95, r: 238, y: 44, w: 120, h: 46, o: 0.55 },
  { a: 1.55, r: 300, y: 78, w: 185, h: 70, o: 0.4 },
  { a: 0.85, r: 280, y: 56, w: 130, h: 50, o: 0.42 },
  { a: 0.25, r: 320, y: 100, w: 230, h: 88, o: 0.3 },
  { a: 3.5, r: 260, y: 66, w: 145, h: 54, o: 0.38 },
  { a: 4.1, r: 300, y: 112, w: 210, h: 80, o: 0.26 },
  { a: -1.25, r: 270, y: 74, w: 160, h: 58, o: 0.46 },
  { a: -1.72, r: 305, y: 112, w: 215, h: 80, o: 0.3 },
  { a: -2.15, r: 282, y: 58, w: 135, h: 48, o: 0.48 },
  { a: -1.5, r: 330, y: 138, w: 240, h: 90, o: 0.2 },
];

for (const spec of cloudSpecs) {
  const mat = new THREE.SpriteMaterial({
    map: cloudTexture,
    transparent: true,
    depthWrite: false,
    opacity: spec.o,
    color: 0xfff1dc,
    fog: false,
  });
  const sprite = new THREE.Sprite(mat);
  sprite.position.set(
    Math.cos(spec.a) * spec.r,
    spec.y,
    Math.sin(spec.a) * spec.r
  );
  sprite.scale.set(spec.w, spec.h, 1);
  sprite.userData.baseX = sprite.position.x;
  sprite.userData.drift = 1.2 + Math.random() * 1.8;
  sprite.userData.phase = Math.random() * Math.PI * 2;
  cloudGroup.add(sprite);
}

/* --------------------------- distant rocks ------------------------- */

/* ----------------------------- surfboard --------------------------- */

const boardGroup = new THREE.Group();
boardGroup.rotation.order = "YXZ";
scene.add(boardGroup);

function buildSurfboard() {
  const shape = new THREE.Shape();
  shape.moveTo(-2.25, 0);
  shape.bezierCurveTo(-2.18, 0.48, -1.55, 0.74, -0.4, 0.76);
  shape.bezierCurveTo(1.0, 0.77, 1.95, 0.5, 2.42, 0);
  shape.bezierCurveTo(1.95, -0.5, 1.0, -0.77, -0.4, -0.76);
  shape.bezierCurveTo(-1.55, -0.74, -2.18, -0.48, -2.25, 0);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.16,
    bevelEnabled: true,
    bevelSegments: 4,
    bevelSize: 0.055,
    bevelThickness: 0.05,
    curveSegments: 26,
  });
  geo.rotateX(-Math.PI / 2);
  geo.computeBoundingBox();
  const deckTop = geo.boundingBox.max.y;
  geo.translate(0, -deckTop, 0);
  geo.computeVertexNormals();
  boardGroup.userData.deckTop = deckTop - deckTop; // local deck is now y = 0

  const boardMat = new THREE.MeshPhysicalMaterial({
    color: 0xf46b52,
    roughness: 0.32,
    metalness: 0.02,
    clearcoat: 0.85,
    clearcoatRoughness: 0.28,
  });
  const board = new THREE.Mesh(geo, boardMat);
  boardGroup.add(board);

  // Cream racing stripe with soft rounded ends.
  const stripeGeo = new THREE.CapsuleGeometry(0.11, 3.0, 4, 14);
  stripeGeo.rotateZ(Math.PI / 2);
  const stripe = new THREE.Mesh(
    stripeGeo,
    new THREE.MeshStandardMaterial({ color: 0xffe9c9, roughness: 0.55 })
  );
  stripe.scale.set(1, 0.16, 1.05);
  stripe.position.set(-0.3, 0.012, 0);
  boardGroup.add(stripe);

  const railGeo = new THREE.CapsuleGeometry(0.035, 2.45, 4, 10);
  railGeo.rotateZ(Math.PI / 2);
  const railMat = new THREE.MeshStandardMaterial({ color: 0x1b4a50, roughness: 0.6 });
  for (const side of [-1, 1]) {
    const rail = new THREE.Mesh(railGeo, railMat);
    rail.position.set(-0.05, 0.012, side * 0.4);
    boardGroup.add(rail);
  }

  // Tail traction pad.
  const pad = new THREE.Mesh(
    new THREE.BoxGeometry(0.92, 0.035, 0.9),
    new THREE.MeshStandardMaterial({ color: 0x173f45, roughness: 0.95 })
  );
  pad.position.set(-1.42, 0.022, 0);
  boardGroup.add(pad);

  // Fin.
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(-0.62, 0);
  finShape.lineTo(-0.34, -0.62);
  finShape.closePath();
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.06,
    bevelEnabled: true,
    bevelSize: 0.015,
    bevelThickness: 0.015,
    bevelSegments: 2,
  });
  finGeo.translate(0, 0, -0.03);
  const fin = new THREE.Mesh(
    finGeo,
    new THREE.MeshStandardMaterial({
      color: 0x0d3b42,
      roughness: 0.5,
      metalness: 0.05,
    })
  );
  fin.position.set(-1.55, -0.02, 0);
  boardGroup.add(fin);
}

buildSurfboard();

/* ------------------------------ pelican ---------------------------- */

const rider = new THREE.Group();
rider.position.y = 0.0;
boardGroup.add(rider);

const creamMat = new THREE.MeshStandardMaterial({
  color: 0xfbf3e3,
  roughness: 0.72,
  metalness: 0,
});
const shadowMat = new THREE.MeshStandardMaterial({
  color: 0xdde4e0,
  roughness: 0.85,
  metalness: 0,
});
const warmWhiteMat = new THREE.MeshStandardMaterial({
  color: 0xf2e3cd,
  roughness: 0.8,
  metalness: 0,
});
const beakMat = new THREE.MeshStandardMaterial({
  color: 0xffbe3f,
  roughness: 0.42,
  metalness: 0.02,
});
const pouchMat = new THREE.MeshStandardMaterial({
  color: 0xf4a44a,
  roughness: 0.52,
  metalness: 0.02,
});
const orangeMat = new THREE.MeshStandardMaterial({
  color: 0xe97b2b,
  roughness: 0.6,
  metalness: 0,
});
const darkMat = new THREE.MeshStandardMaterial({
  color: 0x1a2226,
  roughness: 0.35,
  metalness: 0.15,
});
const eyeMat = new THREE.MeshStandardMaterial({
  color: 0xffe3a3,
  roughness: 0.35,
  emissive: 0x3d2a08,
  emissiveIntensity: 0.25,
});

// Body
const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), creamMat);
body.scale.set(0.96, 0.92, 0.72);
body.position.set(0, 1.16, 0);
body.rotation.z = -0.08;
rider.add(body);

// Chest / belly sheen
const belly = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), warmWhiteMat);
belly.scale.set(0.6, 0.62, 0.5);
belly.position.set(0.3, 0.96, 0.36);
rider.add(belly);

// Tail feathers
const tailGeo = new THREE.ConeGeometry(0.16, 0.95, 7);
tailGeo.rotateZ(Math.PI / 2);
tailGeo.scale(1, 0.42, 1.1);
for (let i = 0; i < 4; i++) {
  const feather = new THREE.Mesh(
    tailGeo,
    i % 2 === 0 ? creamMat : shadowMat
  );
  feather.position.set(-0.72, 0.92 + i * 0.055, (i - 1.5) * 0.07);
  feather.rotation.y = (i - 1.5) * 0.2;
  feather.rotation.z = 0.28 + i * 0.03;
  rider.add(feather);
}

// Neck + head
const neckGroup = new THREE.Group();
neckGroup.position.set(0.48, 1.52, 0);
rider.add(neckGroup);

const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0.0, 0.0, 0),
  new THREE.Vector3(0.16, 0.3, 0),
  new THREE.Vector3(0.3, 0.58, 0),
  new THREE.Vector3(0.26, 0.84, 0),
]);
const neck = new THREE.Mesh(
  new THREE.TubeGeometry(neckCurve, 24, 0.2, 12, false),
  creamMat
);
neckGroup.add(neck);

const headGroup = new THREE.Group();
headGroup.position.set(0.37, 0.96, 0);
neckGroup.add(headGroup);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.37, 32, 24), creamMat);
head.scale.set(1.02, 0.94, 0.88);
headGroup.add(head);

// Little crest at the back of the head.
for (let i = 0; i < 3; i++) {
  const tuft = new THREE.Mesh(
    new THREE.ConeGeometry(0.055, 0.22, 5),
    i === 0 ? shadowMat : creamMat
  );
  tuft.position.set(-0.28 + i * 0.04, 0.22 + i * 0.025, (i - 1) * 0.08);
  tuft.rotation.z = 0.9 + i * 0.12;
  headGroup.add(tuft);
}

// Eyes
for (const side of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.082, 16, 12), eyeMat);
  eye.position.set(0.19, 0.09, side * 0.27);
  headGroup.add(eye);

  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.042, 12, 10), darkMat);
  pupil.position.set(0.245, 0.095, side * 0.292);
  headGroup.add(pupil);

  const glint = new THREE.Mesh(
    new THREE.SphereGeometry(0.014, 8, 6),
    new THREE.MeshBasicMaterial({ color: 0xffffff })
  );
  glint.position.set(0.275, 0.118, side * 0.3);
  headGroup.add(glint);
}

// Upper bill
const billGeo = new THREE.ConeGeometry(0.17, 1.52, 12);
billGeo.rotateZ(-Math.PI / 2);
billGeo.translate(0.76, 0, 0);
const bill = new THREE.Mesh(billGeo, beakMat);
bill.scale.set(1, 0.8, 1.3);
bill.position.set(0.2, 0.06, 0);
bill.rotation.z = -0.13;
headGroup.add(bill);

// Hooked tip
const hook = new THREE.Mesh(new THREE.ConeGeometry(0.075, 0.2, 8), orangeMat);
hook.position.set(1.76, -0.17, 0);
hook.rotation.z = Math.PI;
headGroup.add(hook);

// Pouch
const pouchGeo = new THREE.SphereGeometry(1, 30, 20);
{
  const pos = pouchGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    // Let the underside sag and the throat pull back.
    const sag = (1 - y) * 0.18;
    pos.setY(i, y * 0.3 - sag * 0.32);
    pos.setZ(i, z * (0.94 + y * 0.1));
    pos.setX(i, x * (1 - (1 - y) * 0.08));
  }
  pouchGeo.computeVertexNormals();
}
const pouch = new THREE.Mesh(pouchGeo, pouchMat);
pouch.position.set(1.05, -0.28, 0);
pouch.rotation.z = -0.13;
pouch.scale.set(0.82, 1, 0.22);
headGroup.add(pouch);

// Legs and webbed feet
function addLeg(side) {
  const leg = new THREE.Mesh(
    new THREE.CylinderGeometry(0.055, 0.07, 0.52, 8),
    orangeMat
  );
  leg.position.set(0.3, 0.33, side * 0.27);
  leg.rotation.z = 0.16;
  rider.add(leg);

  const foot = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 8), orangeMat);
  foot.scale.set(0.26, 0.055, 0.17);
  foot.position.set(0.48, 0.06, side * 0.28);
  rider.add(foot);

  for (let i = 0; i < 3; i++) {
    const toe = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.038, 0.22, 4, 8),
      orangeMat
    );
    toe.rotation.z = -Math.PI / 2;
    toe.rotation.y = (i - 1) * 0.3;
    toe.position.set(0.63, 0.05, side * 0.28 + (i - 1) * 0.075);
    rider.add(toe);
  }
}
addLeg(-1);
addLeg(1);

// Wings
function wingGeometry(side) {
  const lead = -side * 0.36;
  const trail = side * 0.48;

  const shape = new THREE.Shape();
  shape.moveTo(0, lead);
  shape.bezierCurveTo(0.55, lead * 1.55, 1.28, lead * 1.05, 1.72, 0.02);
  shape.bezierCurveTo(1.56, trail * 0.4, 1.34, trail * 0.62, 1.12, trail * 0.68);
  shape.quadraticCurveTo(1.1, trail * 1.12, 0.84, trail * 0.98);
  shape.quadraticCurveTo(0.8, trail * 1.32, 0.56, trail * 1.08);
  shape.bezierCurveTo(0.35, trail * 1.3, 0.14, trail * 1.15, 0, trail * 0.9);
  shape.closePath();

  const g = new THREE.ExtrudeGeometry(shape, {
    depth: 0.045,
    bevelEnabled: true,
    bevelSize: 0.018,
    bevelThickness: 0.014,
    bevelSegments: 2,
    curveSegments: 22,
  });
  g.rotateX(Math.PI / 2);
  return g;
}

const wingRoots = {};
for (const side of [-1, 1]) {
  const root = new THREE.Group();
  root.position.set(0.06, 1.42, side * 0.6);
  rider.add(root);

  const yaw = new THREE.Group();
  const sweep = 0.5;
  yaw.rotation.y = side === 1 ? -Math.PI / 2 - sweep : Math.PI / 2 + sweep;
  root.add(yaw);

  const shoulder = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), creamMat);
  shoulder.scale.set(0.3, 0.18, 0.34);
  shoulder.position.set(0, 0.02, 0);
  yaw.add(shoulder);

  const wing = new THREE.Mesh(wingGeometry(side), creamMat);
  yaw.add(wing);

  // A few grey primary-feather tips peeking out of the trailing edge.
  for (let i = 0; i < 3; i++) {
    const tip = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.065, 0.42, 4, 8),
      shadowMat
    );
    tip.rotation.z = -Math.PI / 2;
    tip.rotation.y = side * (0.1 + i * 0.16);
    tip.position.set(1.18 + i * 0.1, 0.035, side * (0.18 + i * 0.1));
    tip.scale.set(1, 0.55, 1.2);
    yaw.add(tip);
  }

  root.rotation.x = side === 1 ? -0.74 : 0.74;
  wingRoots[side === 1 ? "right" : "left"] = root;
}

// A tiny splash of colour: coral "surf club" band on one leg.
const band = new THREE.Mesh(
  new THREE.TorusGeometry(0.075, 0.018, 6, 18),
  new THREE.MeshStandardMaterial({ color: 0x20b2aa, roughness: 0.5 })
);
band.position.set(0.3, 0.46, -0.27);
band.rotation.x = Math.PI / 2;
rider.add(band);

/* ------------------------------ spray ------------------------------ */

const MAX_SPRAY = 420;
const sprayPositions = new Float32Array(MAX_SPRAY * 3);
const sprayLives = new Float32Array(MAX_SPRAY);
const spraySizes = new Float32Array(MAX_SPRAY);
const sprayVelocities = new Float32Array(MAX_SPRAY * 3);

for (let i = 0; i < MAX_SPRAY; i++) {
  sprayPositions[i * 3 + 1] = -100;
}

const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute(
  "position",
  new THREE.BufferAttribute(sprayPositions, 3).setUsage(THREE.DynamicDrawUsage)
);
sprayGeo.setAttribute(
  "aLife",
  new THREE.BufferAttribute(sprayLives, 1).setUsage(THREE.DynamicDrawUsage)
);
sprayGeo.setAttribute(
  "aSize",
  new THREE.BufferAttribute(spraySizes, 1).setUsage(THREE.DynamicDrawUsage)
);

const sprayMat = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  uniforms: { uDpr: { value: renderer.getPixelRatio() } },
  vertexShader: /* glsl */ `
    attribute float aLife;
    attribute float aSize;
    varying float vLife;
    uniform float uDpr;
    void main() {
      vLife = aLife;
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = aSize * uDpr * (150.0 / max(1.0, -mv.z));
      gl_Position = projectionMatrix * mv;
    }
  `,
  fragmentShader: /* glsl */ `
    varying float vLife;
    void main() {
      vec2 uv = gl_PointCoord - 0.5;
      float d = length(uv);
      float alpha = smoothstep(0.5, 0.06, d) * smoothstep(0.0, 0.3, vLife) * 0.7;
      vec3 col = mix(vec3(0.72, 0.94, 0.98), vec3(1.0, 0.99, 0.94), vLife);
      gl_FragColor = vec4(col, alpha);
    }
  `,
});

const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

let sprayCursor = 0;
let sprayAccumulator = 0;
const spawnPos = new THREE.Vector3();

function emitSpray(count, board, time) {
  for (let n = 0; n < count; n++) {
    const i = sprayCursor;
    sprayCursor = (sprayCursor + 1) % MAX_SPRAY;

    const side = Math.random() < 0.5 ? -1 : 1;
    spawnPos.set(
      -1.75 + Math.random() * 0.7,
      0.12 + Math.random() * 0.25,
      side * (0.45 + Math.random() * 0.3)
    );
    board.localToWorld(spawnPos);

    sprayPositions[i * 3] = spawnPos.x;
    sprayPositions[i * 3 + 1] = spawnPos.y;
    sprayPositions[i * 3 + 2] = spawnPos.z;

    sprayVelocities[i * 3] = -1.6 - Math.random() * 2.4;
    sprayVelocities[i * 3 + 1] = 2.0 + Math.random() * 3.2;
    sprayVelocities[i * 3 + 2] = side * (0.8 + Math.random() * 2.0);

    sprayLives[i] = 0.55 + Math.random() * 0.65;
    spraySizes[i] = 0.18 + Math.random() * 0.42;
  }
}

function updateSpray(dt, board, time) {
  // Emit more spray on the faster part of the carve.
  sprayAccumulator += dt * 260;
  const emitCount = Math.floor(sprayAccumulator);
  if (emitCount > 0) {
    sprayAccumulator -= emitCount;
    emitSpray(emitCount, board, time);
  }

  for (let i = 0; i < MAX_SPRAY; i++) {
    if (sprayLives[i] <= 0) continue;

    sprayLives[i] -= dt;
    const j = i * 3;
    sprayVelocities[j + 1] -= 9.0 * dt;
    sprayVelocities[j] *= 0.995;
    sprayVelocities[j + 2] *= 0.995;

    sprayPositions[j] += sprayVelocities[j] * dt;
    sprayPositions[j + 1] += sprayVelocities[j + 1] * dt;
    sprayPositions[j + 2] += sprayVelocities[j + 2] * dt;

    if (sprayLives[i] <= 0) {
      sprayPositions[j + 1] = -100;
    }
  }

  sprayGeo.attributes.position.needsUpdate = true;
  sprayGeo.attributes.aLife.needsUpdate = true;
  sprayGeo.attributes.aSize.needsUpdate = true;
}

/* --------------------------- board motion -------------------------- */

const boardState = {
  t: 0,
  x: 0,
  z: 0,
  dzdt: 0,
  y: 0,
};

const upVec = new THREE.Vector3();
const forwardVec = new THREE.Vector3();
const sideVec = new THREE.Vector3();
const basis = new THREE.Matrix4();
const leanQuat = new THREE.Quaternion();
const boardTarget = new THREE.Vector3();
const camTarget = new THREE.Vector3();
const camLook = new THREE.Vector3();
const lookSmooth = new THREE.Vector3(0, 1.8, 0);
const camOffset = new THREE.Vector3();
const tmpVec = new THREE.Vector3();

function updateBoard(t) {
  const speed = 2.15;
  const x = t * speed;
  const z = 2.55 * Math.sin(t * 0.34) + 0.85 * Math.sin(t * 0.77 + 1.0);
  const dzdt =
    2.55 * 0.34 * Math.cos(t * 0.34) +
    0.85 * 0.77 * Math.cos(t * 0.77 + 1.0);

  const sample = sampleWave(x, z, t);
  const y = sample.h + 0.2;

  boardState.t = t;
  boardState.x = x;
  boardState.z = z;
  boardState.dzdt = dzdt;
  boardState.y = y;

  boardGroup.position.set(x, y, z);

  const yaw = Math.atan2(-dzdt, speed);
  forwardVec.set(Math.cos(yaw), 0, -Math.sin(yaw));

  upVec.set(-sample.gx, 1, -sample.gz).normalize();
  forwardVec.addScaledVector(upVec, -forwardVec.dot(upVec)).normalize();
  sideVec.crossVectors(forwardVec, upVec).normalize();
  basis.makeBasis(forwardVec, upVec, sideVec);
  boardGroup.quaternion.setFromRotationMatrix(basis);

  // Lean into the carve a little.
  leanQuat.setFromAxisAngle(forwardVec, -dzdt * 0.035);
  boardGroup.quaternion.premultiply(leanQuat);

  boardGroup.updateMatrixWorld(true);
}

/* --------------------------- pelican motion ------------------------ */

const clock = new THREE.Clock();
let elapsed = 0;

function animateRider(t) {
  const flap = Math.sin(t * 2.05);
  const flap2 = Math.sin(t * 2.05 + 0.5);

  wingRoots.right.rotation.x = -0.74 - flap * 0.16 + flap2 * 0.04;
  wingRoots.left.rotation.x = 0.74 + flap * 0.16 - flap2 * 0.04;

  wingRoots.right.rotation.z = Math.sin(t * 1.3) * 0.025;
  wingRoots.left.rotation.z = -Math.sin(t * 1.3) * 0.025;

  rider.position.y = Math.sin(t * 3.6) * 0.022 + Math.sin(t * 5.7) * 0.01;
  rider.rotation.y = -0.19;
  rider.rotation.z = -0.035 + Math.sin(t * 0.8) * 0.035;
  rider.rotation.x =
    -boardState.dzdt * 0.075 + Math.sin(t * 1.15) * 0.028;

  headGroup.rotation.y = -0.16 + Math.sin(t * 0.52) * 0.09 + Math.sin(t * 1.7) * 0.025;
  headGroup.rotation.z = Math.sin(t * 0.93 + 0.7) * 0.055;
  headGroup.rotation.x = Math.sin(t * 1.35 + 1.2) * 0.045;

  neckGroup.rotation.z = 0.03 + Math.sin(t * 1.05) * 0.02;

  pouch.scale.y = 1 + Math.sin(t * 5.1 + 1.4) * 0.1;
  pouch.rotation.z = -0.13 + Math.sin(t * 3.8) * 0.045 + Math.sin(t * 5.3) * 0.012;
}

/* ------------------------------ camera ----------------------------- */

function updateCamera(dt, t) {
  camOffset.set(
    0.9 + Math.sin(t * 0.17) * 1.15 + Math.sin(t * 0.43) * 0.22,
    4.35 + Math.sin(t * 0.23) * 0.42,
    9.2 + Math.sin(t * 0.12) * 1.35
  );

  camTarget.set(
    boardState.x + Math.cos(t * 0.11) * 0.6,
    boardState.y + 1.85,
    boardState.z
  );

  const posDesired = tmpVec.copy(camTarget).add(camOffset);
  const lerp = 1 - Math.exp(-dt * 1.7);
  camera.position.lerp(posDesired, lerp);

  const lookDesired = camLook.set(
    boardState.x + 0.45,
    boardState.y + 1.78,
    boardState.z + 0.05
  );
  lookSmooth.lerp(lookDesired, 1 - Math.exp(-dt * 2.2));
  camera.lookAt(lookSmooth);

  // A whisper of camera roll keeps the horizon alive.
  camera.rotateZ(Math.sin(t * 0.21) * 0.008);
}

/* ------------------------------- loop ------------------------------ */

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  sprayMat.uniforms.uDpr.value = renderer.getPixelRatio();
}
window.addEventListener("resize", onResize);

function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;
  const t = elapsed;

  updateBoard(t);
  animateRider(t);

  ocean.position.set(boardState.x, 0, boardState.z);
  oceanUniforms.uTime.value = t;
  oceanUniforms.uBoardPos.value.set(boardState.x, boardState.z);

  updateCamera(dt, t);

  sky.position.copy(camera.position);
  oceanUniforms.uCamPos.value.copy(camera.position);

  cloudGroup.position.x = boardState.x;
  cloudGroup.position.z = boardState.z;
  for (const sprite of cloudGroup.children) {
    sprite.position.x =
      sprite.userData.baseX + Math.sin(t * 0.03 + sprite.userData.phase) * 10;
  }

  updateSpray(dt, boardGroup, t);

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(frame);
