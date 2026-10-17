/**
 * Surfing Pelican — an animated, non-interactive three.js scene.
 *
 * A stylised pelican rides a surfboard down an endless, procedurally animated
 * ocean swell. Everything is generated in code: the wave field (shared between
 * JS and GLSL), the foam, the sky, the clouds, the spray and the bird itself.
 * No textures, no network, no storage.
 */

import * as THREE from "three";

// ---------------------------------------------------------------------------
// Renderer / scene / camera
// ---------------------------------------------------------------------------

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xa9cbe4, 46, 210);

const camera = new THREE.PerspectiveCamera(
  44,
  window.innerWidth / window.innerHeight,
  0.1,
  900
);
camera.position.set(0, 3.4, 9);

// ---------------------------------------------------------------------------
// Lighting
// ---------------------------------------------------------------------------

const SUN_DIR = new THREE.Vector3(-0.38, 0.34, -0.86).normalize(); // where the sun sits in the sky

const hemi = new THREE.HemisphereLight(0x9ed6f7, 0x2a6d9e, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff0d2, 2.15);
sun.position.copy(SUN_DIR).multiplyScalar(70);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 20;
sun.shadow.camera.far = 160;
sun.shadow.camera.left = -16;
sun.shadow.camera.right = 16;
sun.shadow.camera.top = 16;
sun.shadow.camera.bottom = -16;
sun.shadow.bias = -0.0012;
sun.shadow.normalBias = 0.035;
scene.add(sun, sun.target);

const fill = new THREE.DirectionalLight(0x8fc6ff, 0.55);
fill.position.set(16, 9, 22);
scene.add(fill);

const rim = new THREE.DirectionalLight(0xffd9a8, 0.5);
rim.position.copy(SUN_DIR).multiplyScalar(-24).setY(10);
scene.add(rim);

// ---------------------------------------------------------------------------
// Sky dome (gradient + sun glow, generated in a shader)
// ---------------------------------------------------------------------------

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(420, 40, 24),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      uZenith: { value: new THREE.Color(0x2f74c4) },
      uHorizon: { value: new THREE.Color(0xcfe6f2) },
      uSunColor: { value: new THREE.Color(0xffe9b8) },
      uSunDir: { value: SUN_DIR.clone() },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      varying vec3 vDir;
      uniform vec3 uZenith, uHorizon, uSunColor, uSunDir;
      void main() {
        vec3 dir = normalize(vDir);
        float up = clamp(dir.y, 0.0, 1.0);
        vec3 col = mix(uHorizon, uZenith, pow(up, 0.62));
        // hazy band right at the horizon
        col = mix(col, uHorizon * 1.06, smoothstep(0.14, 0.0, abs(dir.y)) * 0.5);
        float d = max(dot(dir, uSunDir), 0.0);
        col += uSunColor * (pow(d, 260.0) * 2.2 + pow(d, 26.0) * 0.42 + pow(d, 5.0) * 0.16);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  })
);
scene.add(sky);

// ---------------------------------------------------------------------------
// Wave field — one definition, emitted both as JS and as GLSL
// ---------------------------------------------------------------------------

// dir = travel direction in XZ, amp = height, len = wavelength, the phase speed
// follows deep-water dispersion: omega = sqrt(g / k)
const WAVE_DEFS = [
  { dir: [0.18, 0.98], amp: 1.15, len: 23.0 }, // the big swell the pelican rides
  { dir: [0.85, 0.53], amp: 0.42, len: 8.5 },
  { dir: [-0.62, 0.78], amp: 0.3, len: 5.2 },
  { dir: [1.0, -0.16], amp: 0.15, len: 2.9 },
  { dir: [-0.97, -0.24], amp: 0.1, len: 1.9 },
  { dir: [0.36, -0.93], amp: 0.06, len: 1.15 },
];

const WAVES = WAVE_DEFS.map((w) => {
  const len = Math.hypot(w.dir[0], w.dir[1]);
  const dx = w.dir[0] / len;
  const dz = w.dir[1] / len;
  const k = (Math.PI * 2) / w.len;
  return { dx, dz, k, amp: w.amp, omega: Math.sqrt(9.81 * k) };
});

/** Vertical displacement of the ocean surface at (x, z) for time t. */
function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    h += w.amp * Math.sin(w.k * (w.dx * x + w.dz * z) - t * w.omega);
  }
  return h;
}

/** Analytic surface normal of the ocean at (x, z) for time t. */
function waveNormal(x, z, t, out = new THREE.Vector3()) {
  let dhx = 0;
  let dhz = 0;
  for (const w of WAVES) {
    const c = w.amp * w.k * Math.cos(w.k * (w.dx * x + w.dz * z) - t * w.omega);
    dhx += c * w.dx;
    dhz += c * w.dz;
  }
  return out.set(-dhx, 1, -dhz).normalize();
}

function waveGLSL() {
  let h = "";
  let dx = "";
  let dz = "";
  for (const w of WAVES) {
    const a = w.amp.toFixed(5);
    const k = w.k.toFixed(6);
    const om = w.omega.toFixed(6);
    const px = w.dx.toFixed(6);
    const pz = w.dz.toFixed(6);
    h += `  h += ${a} * sin(${k} * (${px} * x + ${pz} * z) - t * ${om});\n`;
    dx += `  dhx += ${a} * ${k} * ${px} * cos(${k} * (${px} * x + ${pz} * z) - t * ${om});\n`;
    dz += `  dhz += ${a} * ${k} * ${pz} * cos(${k} * (${px} * x + ${pz} * z) - t * ${om});\n`;
  }
  return /* glsl */ `
    float waveHeight(float x, float z, float t) {
      float h = 0.0;
    ${h}  return h;
    }
    vec3 waveNormal(float x, float z, float t) {
      float dhx = 0.0;
      float dhz = 0.0;
    ${dx}${dz}  return normalize(vec3(-dhx, 1.0, -dhz));
    }
  `;
}

const oceanUniforms = {
  uTime: { value: 0 },
};

const oceanMaterial = new THREE.MeshStandardMaterial({
  color: 0x1a6aa4,
  roughness: 0.52,
  metalness: 0.02,
  envMapIntensity: 0.8,
});

oceanMaterial.onBeforeCompile = (shader) => {
  shader.uniforms.uTime = oceanUniforms.uTime;

  const common = /* glsl */ `
    uniform float uTime;
    varying float vHeight;
    varying vec3 vWorldPos;
    ${waveGLSL()}
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
  `;

  shader.vertexShader = common + shader.vertexShader;
  shader.vertexShader = shader.vertexShader.replace(
    "#include <beginnormal_vertex>",
    /* glsl */ `
      vec3 oceanNormal = waveNormal(position.x, position.z, uTime);
      vec3 objectNormal = oceanNormal;
      #ifdef USE_TANGENT
        vec3 objectTangent = vec3(1.0, 0.0, 0.0);
      #endif
    `
  );
  shader.vertexShader = shader.vertexShader.replace(
    "#include <begin_vertex>",
    /* glsl */ `
      vec3 transformed = vec3(position.x, waveHeight(position.x, position.z, uTime), position.z);
      vHeight = transformed.y;
      vWorldPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
    `
  );

  shader.fragmentShader = common + shader.fragmentShader;
  shader.fragmentShader = shader.fragmentShader.replace(
    "#include <color_fragment>",
    /* glsl */ `
      #include <color_fragment>
      {
        float n = vnoise(vWorldPos.xz * 1.15 + vec2(uTime * 0.16, -uTime * 0.11));
        n = n * 0.55 + vnoise(vWorldPos.xz * 3.1 + vec2(-uTime * 0.22, uTime * 0.18)) * 0.45;
        float crest = smoothstep(0.98, 1.85, vHeight);
        float foam = smoothstep(0.52, 0.95, crest * (0.28 + n * 0.82));
        // faint wind streaks on the flatter water
        float streak = smoothstep(0.74, 1.0, vnoise(vWorldPos.xz * vec2(0.35, 1.7) + vec2(uTime * 0.05, 0.0))) * crest;
        vec3 deep = diffuseColor.rgb;
        diffuseColor.rgb = mix(deep, vec3(0.93, 0.97, 1.0), clamp(foam * 0.88 + streak * 0.30, 0.0, 1.0));
      }
    `
  );
};

const ocean = new THREE.Mesh(
  new THREE.PlaneGeometry(240, 240, 320, 320),
  oceanMaterial
);
ocean.geometry.rotateX(-Math.PI / 2);
ocean.receiveShadow = true;
ocean.castShadow = false;
scene.add(ocean);

// ---------------------------------------------------------------------------
// Helpers: tiny procedural canvas textures (no external assets)
// ---------------------------------------------------------------------------

function makeSoftDiscTexture(size = 64, inner = "rgba(255,255,255,1)", outer = "rgba(255,255,255,0)") {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, inner);
  g.addColorStop(0.45, "rgba(255,255,255,0.55)");
  g.addColorStop(1, outer);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function makeCloudTexture(size = 256) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const blobs = [
    [0.5, 0.58, 0.32],
    [0.32, 0.62, 0.24],
    [0.68, 0.63, 0.26],
    [0.44, 0.46, 0.22],
    [0.6, 0.5, 0.2],
    [0.25, 0.72, 0.17],
    [0.75, 0.73, 0.16],
  ];
  for (const [bx, by, br] of blobs) {
    const g = ctx.createRadialGradient(
      bx * size,
      by * size,
      0,
      bx * size,
      by * size,
      br * size
    );
    g.addColorStop(0, "rgba(255,255,255,0.85)");
    g.addColorStop(0.55, "rgba(255,255,255,0.35)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, size, size);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// ---------------------------------------------------------------------------
// Pelican + surfboard
// ---------------------------------------------------------------------------

const MAT = {
  feather: new THREE.MeshStandardMaterial({
    color: 0xfaf4e6,
    roughness: 0.72,
    metalness: 0.0,
  }),
  featherShade: new THREE.MeshStandardMaterial({
    color: 0xd9d2c2,
    roughness: 0.8,
  }),
  beak: new THREE.MeshStandardMaterial({ color: 0xf3a63c, roughness: 0.5 }),
  pouch: new THREE.MeshStandardMaterial({
    color: 0xffb453,
    roughness: 0.55,
  }),
  leg: new THREE.MeshStandardMaterial({ color: 0xef9836, roughness: 0.55 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x241c16, roughness: 0.35 }),
  glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
  board: new THREE.MeshStandardMaterial({
    color: 0xf2543c,
    roughness: 0.28,
    metalness: 0.12,
  }),
  boardDeck: new THREE.MeshStandardMaterial({ color: 0xfdf3e6, roughness: 0.4 }),
  boardFin: new THREE.MeshStandardMaterial({ color: 0x2c3d4c, roughness: 0.4 }),
};

function shadowed(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function makeWing(side) {
  // side: -1 left, +1 right. The wing sweeps back and up from the shoulder.
  const pivot = new THREE.Group();
  pivot.position.set(0.78 * side, 1.92, 0.16);

  const shoulder = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.56, 20, 16), MAT.feather));
  shoulder.scale.set(0.82, 0.6, 1.15);
  shoulder.position.set(0.1 * side, -0.02, -0.04);
  pivot.add(shoulder);

  // inner wing — short and deep
  const inner = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.56, 20, 16), MAT.feather));
  inner.scale.set(1.25, 0.36, 1.3);
  inner.position.set(0.66 * side, -0.1, -0.34);
  inner.rotation.set(0, -0.3 * side, -0.1 * side);
  pivot.add(inner);

  // outer wing — swept back, thinner, tip raised
  const outer = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.56, 20, 16), MAT.feather));
  outer.scale.set(1.15, 0.22, 1.15);
  outer.position.set(1.52 * side, 0.08, -1.14);
  outer.rotation.set(0, -0.62 * side, -0.3 * side);
  pivot.add(outer);

  // primary feathers fanning off the trailing edge of the wing tip
  const featherGeo = new THREE.BoxGeometry(1.0, 0.055, 0.26);
  for (let i = 0; i < 5; i++) {
    const f = shadowed(new THREE.Mesh(featherGeo, MAT.featherShade));
    const t = i / 4;
    f.position.set(side * (2.16 + t * 0.36), 0.24 - t * 0.14, -1.58 - t * 0.66);
    f.rotation.set(0, side * (-0.72 - t * 0.5), side * (-0.32 + t * 0.3));
    f.scale.set(0.8 + t * 0.45, 1, 1);
    pivot.add(f);
  }
  return pivot;
}

function makePelican() {
  const bird = new THREE.Group();

  // --- body -------------------------------------------------------------
  const body = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), MAT.feather));
  body.position.set(0, 1.28, -0.18);
  body.scale.set(1.02, 1.02, 1.62);
  body.rotation.x = -0.08;
  bird.add(body);

  const chest = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.85, 28, 20), MAT.feather));
  chest.position.set(0, 1.5, 0.72);
  chest.scale.set(0.92, 1.02, 0.96);
  bird.add(chest);

  // tail — cocked up behind the body
  const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.46, 1.35, 4), MAT.featherShade));
  tail.position.set(0, 1.5, -1.86);
  tail.rotation.set(-Math.PI / 2 + 0.3, Math.PI / 4, 0);
  tail.scale.set(1, 1, 0.3);
  bird.add(tail);

  // --- neck & head ------------------------------------------------------
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 1.95, 0.62),
    new THREE.Vector3(0, 2.42, 0.82),
    new THREE.Vector3(0, 2.92, 0.86),
    new THREE.Vector3(0, 3.16, 1.12),
  ]);
  const neck = shadowed(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 28, 0.32, 14, false), MAT.feather));
  bird.add(neck);

  const head = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.52, 28, 20), MAT.feather));
  head.position.set(0, 3.22, 1.3);
  head.scale.set(0.92, 1.0, 1.16);
  bird.add(head);

  const crown = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.32, 18, 14), MAT.featherShade));
  crown.position.set(0, 3.5, 0.98);
  crown.scale.set(0.86, 0.5, 1.05);
  bird.add(crown);

  // --- beak: long straight mandible, hooked tip, throat pouch hanging under it
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, 3.16, 1.5);
  beakGroup.rotation.x = 0.06;
  bird.add(beakGroup);

  const upper = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.13, 1.42), MAT.beak));
  upper.position.set(0, 0.03, 0.62);
  beakGroup.add(upper);

  const ridge = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.06, 1.22), MAT.beak));
  ridge.position.set(0, 0.11, 0.56);
  beakGroup.add(ridge);

  const upperTaper = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.115, 0.78, 4), MAT.beak));
  upperTaper.position.set(0, 0.02, 1.58);
  upperTaper.rotation.set(Math.PI / 2, Math.PI / 4, 0);
  upperTaper.scale.set(1, 1, 0.62);
  beakGroup.add(upperTaper);

  const hook = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 10), MAT.beak));
  hook.position.set(0, -0.06, 1.95);
  hook.scale.set(0.85, 1.15, 1.35);
  beakGroup.add(hook);

  const pouch = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.42, 22, 16), MAT.pouch));
  pouch.position.set(0, -0.19, 0.6);
  pouch.scale.set(0.52, 0.66, 1.5);
  beakGroup.add(pouch);

  const pouchTip = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), MAT.pouch));
  pouchTip.position.set(0, -0.25, 1.28);
  pouchTip.scale.set(0.72, 0.82, 1.25);
  beakGroup.add(pouchTip);

  // --- eyes -------------------------------------------------------------
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.115, 14, 12), MAT.dark);
    eye.position.set(0.34 * side, 3.36, 1.56);
    bird.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.042, 8, 8), MAT.glint);
    glint.position.set(0.38 * side, 3.41, 1.65);
    bird.add(glint);
    const brow = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.14, 10, 8), MAT.featherShade));
    brow.position.set(0.32 * side, 3.47, 1.5);
    brow.scale.set(1.1, 0.5, 1.2);
    bird.add(brow);
  }

  // --- wings ------------------------------------------------------------
  const leftWing = makeWing(-1);
  const rightWing = makeWing(1);
  bird.add(leftWing, rightWing);

  // --- legs & webbed feet ----------------------------------------------
  const legGeo = new THREE.CylinderGeometry(0.1, 0.085, 1.05, 12);
  const padGeo = new THREE.BoxGeometry(0.26, 0.07, 0.42);
  const toeGeo = new THREE.BoxGeometry(0.115, 0.055, 0.62);
  for (const side of [-1, 1]) {
    const leg = shadowed(new THREE.Mesh(legGeo, MAT.leg));
    leg.position.set(0.42 * side, 0.66, 0.3);
    leg.rotation.x = 0.1;
    leg.rotation.z = -0.08 * side;
    bird.add(leg);

    const pad = shadowed(new THREE.Mesh(padGeo, MAT.leg));
    pad.position.set(0.48 * side, 0.14, 0.36);
    pad.rotation.y = -0.1 * side;
    bird.add(pad);

    // three splayed toes = webbed foot
    for (const ry of [-0.5, 0, 0.5]) {
      const toe = shadowed(new THREE.Mesh(toeGeo, MAT.leg));
      toe.position.set(
        0.48 * side + Math.sin(ry * side) * 0.36,
        0.125,
        0.36 + Math.cos(ry * side) * 0.34
      );
      toe.rotation.y = ry * side;
      bird.add(toe);
    }
  }

  return {
    group: bird,
    leftWing,
    rightWing,
    head,
    beakGroup,
    pouch,
  };
}

function makeSurfboard() {
  const board = new THREE.Group();

  const hull = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), MAT.board));
  hull.scale.set(1.06, 0.135, 2.62);
  board.add(hull);

  // raised deck pad + racing stripe
  const deck = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), MAT.boardDeck));
  deck.position.y = 0.035;
  deck.scale.set(0.94, 0.115, 2.42);
  board.add(deck);

  const stripe = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.02, 3.9), MAT.board));
  stripe.position.y = 0.145;
  board.add(stripe);

  const nose = shadowed(new THREE.Mesh(new THREE.SphereGeometry(0.26, 18, 12), MAT.boardDeck));
  nose.position.set(0, 0.02, 2.34);
  nose.scale.set(1, 0.5, 1.9);
  board.add(nose);

  const fin = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.34, 0.72, 3), MAT.boardFin));
  fin.position.set(0, -0.12, -2.0);
  fin.rotation.set(Math.PI / 2, 0, 0);
  fin.scale.set(1, 1, 0.24);
  board.add(fin);

  return board;
}

const rider = new THREE.Group(); // board + bird, positioned on the wave
const board = makeSurfboard();
const pelican = makePelican();
pelican.group.position.set(0, 0.12, -0.06);
rider.add(board, pelican.group);
scene.add(rider);

// ---------------------------------------------------------------------------
// Spray particles thrown off the tail of the board
// ---------------------------------------------------------------------------

const SPRAY_COUNT = 320;
const sprayGeo = new THREE.BufferGeometry();
const sprayPositions = new Float32Array(SPRAY_COUNT * 3);
const sprayAlpha = new Float32Array(SPRAY_COUNT);
const spraySize = new Float32Array(SPRAY_COUNT);
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
sprayGeo.setAttribute("aAlpha", new THREE.BufferAttribute(sprayAlpha, 1));
sprayGeo.setAttribute("aSize", new THREE.BufferAttribute(spraySize, 1));

const sprayParticles = [];
for (let i = 0; i < SPRAY_COUNT; i++) {
  sprayParticles.push({
    life: 0,
    maxLife: 1,
    pos: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    size: 1,
  });
  sprayPositions[i * 3 + 1] = -999;
}

const sprayMaterial = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  uniforms: {
    uMap: { value: makeSoftDiscTexture(64) },
    uColor: { value: new THREE.Color(0xf2fbff) },
  },
  vertexShader: /* glsl */ `
    attribute float aAlpha;
    attribute float aSize;
    varying float vAlpha;
    void main() {
      vAlpha = aAlpha;
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = aSize * (260.0 / max(0.5, -mv.z));
      gl_Position = projectionMatrix * mv;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D uMap;
    uniform vec3 uColor;
    varying float vAlpha;
    void main() {
      float a = texture2D(uMap, gl_PointCoord).a * vAlpha;
      if (a < 0.01) discard;
      gl_FragColor = vec4(uColor, a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const spray = new THREE.Points(sprayGeo, sprayMaterial);
spray.frustumCulled = false;
scene.add(spray);

let sprayCursor = 0;
function emitSpray(pos, count, speedScale = 1) {
  for (let n = 0; n < count; n++) {
    const p = sprayParticles[sprayCursor];
    sprayCursor = (sprayCursor + 1) % SPRAY_COUNT;
    p.life = p.maxLife = 0.55 + Math.random() * 0.75;
    p.pos.copy(pos);
    p.pos.x += (Math.random() - 0.5) * 0.55;
    p.pos.y += (Math.random() - 0.5) * 0.22;
    p.pos.z += (Math.random() - 0.5) * 0.75;
    p.vel.set(
      (Math.random() - 0.5) * 1.5,
      1.1 + Math.random() * 1.9,
      -(1.4 + Math.random() * 2.6)
    ).multiplyScalar(speedScale);
    p.size = 0.28 + Math.random() * 0.85;
  }
}

function updateSpray(dt) {
  for (let i = 0; i < SPRAY_COUNT; i++) {
    const p = sprayParticles[i];
    if (p.life <= 0) {
      sprayAlpha[i] = 0;
      continue;
    }
    p.life -= dt;
    p.vel.y -= 4.6 * dt;
    p.vel.multiplyScalar(1 - 1.1 * dt);
    p.pos.addScaledVector(p.vel, dt);
    const t = Math.max(p.life / p.maxLife, 0);
    sprayAlpha[i] = t * t * 0.85;
    spraySize[i] = p.size * (1.25 - t * 0.45);
    sprayPositions[i * 3] = p.pos.x;
    sprayPositions[i * 3 + 1] = p.pos.y;
    sprayPositions[i * 3 + 2] = p.pos.z;
  }
  sprayGeo.attributes.position.needsUpdate = true;
  sprayGeo.attributes.aAlpha.needsUpdate = true;
  sprayGeo.attributes.aSize.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// Clouds
// ---------------------------------------------------------------------------

const cloudTexture = makeCloudTexture(256);
const clouds = [];
for (let i = 0; i < 11; i++) {
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: cloudTexture,
      transparent: true,
      opacity: 0.34 + Math.random() * 0.32,
      depthWrite: false,
      fog: true,
    })
  );
  const angle = (i / 11) * Math.PI * 2 + Math.random() * 0.5;
  const radius = 120 + Math.random() * 110;
  sprite.position.set(
    Math.cos(angle) * radius,
    22 + Math.random() * 40,
    Math.sin(angle) * radius
  );
  const s = 40 + Math.random() * 62;
  sprite.scale.set(s, s * (0.42 + Math.random() * 0.2), 1);
  sprite.userData.drift = 0.25 + Math.random() * 0.6;
  scene.add(sprite);
  clouds.push(sprite);
}

// ---------------------------------------------------------------------------
// Distant birds (two flapping wings each)
// ---------------------------------------------------------------------------

function makeDistantBird() {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color: 0xf2f6f8,
    roughness: 0.9,
    side: THREE.DoubleSide,
    fog: true,
  });
  const wingGeo = new THREE.BoxGeometry(0.9, 0.035, 0.32);
  const wings = [];
  for (const side of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.x = 0.42 * side;
    const wing = new THREE.Mesh(wingGeo, mat);
    wing.position.x = 0.42 * side;
    pivot.add(wing);
    g.add(pivot);
    wings.push(pivot);
  }
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), mat);
  body.scale.set(1, 0.7, 1.7);
  g.add(body);
  g.userData.wings = wings;
  return g;
}

const distantBirds = [];
for (let i = 0; i < 7; i++) {
  const b = makeDistantBird();
  b.userData.phase = Math.random() * Math.PI * 2;
  b.userData.radius = 22 + Math.random() * 26;
  b.userData.height = 6 + Math.random() * 9;
  b.userData.speed = 0.06 + Math.random() * 0.08;
  b.userData.flap = 4.2 + Math.random() * 2.2;
  b.scale.setScalar(0.8 + Math.random() * 0.8);
  scene.add(b);
  distantBirds.push(b);
}

// ---------------------------------------------------------------------------
// Sun glow sprite (matches the sky shader sun)
// ---------------------------------------------------------------------------

const sunGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: makeSoftDiscTexture(128, "rgba(255,240,205,1)", "rgba(255,225,170,0)"),
    transparent: true,
    opacity: 0.9,
    depthWrite: false,
    fog: false,
    blending: THREE.AdditiveBlending,
  })
);
sunGlow.position.copy(SUN_DIR).multiplyScalar(330);
sunGlow.scale.setScalar(120);
scene.add(sunGlow);

// ---------------------------------------------------------------------------
// Animation
// ---------------------------------------------------------------------------

const clock = new THREE.Timer();
let waveTime = 0;

const tmpNormal = new THREE.Vector3();
const tmpQuat = new THREE.Quaternion();
const tmpQuat2 = new THREE.Quaternion();
const UP = new THREE.Vector3(0, 1, 0);
const camTarget = new THREE.Vector3(0, 1.9, 0);
const camDesired = new THREE.Vector3();
const riderTargetQuat = new THREE.Quaternion();

function animate() {
  requestAnimationFrame(animate);
  clock.update();
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.getElapsed();
  waveTime += dt;

  // ---- ocean ----
  oceanUniforms.uTime.value = waveTime;

  // ---- rider path: slow meander so the pelican "travels" with the swell ----
  const rx = Math.sin(t * 0.17) * 2.1;
  const rz = Math.sin(t * 0.13 + 1.1) * 1.6 + Math.sin(t * 0.061) * 1.2;

  const surfaceY = waveHeight(rx, rz, waveTime);
  const bob =
    Math.sin(t * 1.35) * 0.06 + Math.sin(t * 2.1 + 0.7) * 0.035;

  rider.position.set(rx, surfaceY + 0.16 + bob, rz);

  // orient the board to the local wave slope, plus a lazy yaw/roll of its own
  waveNormal(rx, rz, waveTime, tmpNormal);
  tmpQuat.setFromUnitVectors(UP, tmpNormal);
  const yaw = Math.sin(t * 0.11) * 0.34 + Math.sin(t * 0.043) * 0.18;
  const roll = Math.sin(t * 0.52) * 0.07 + Math.sin(t * 0.19 + 1.9) * 0.05;
  const pitch = Math.sin(t * 0.37) * 0.06;
  tmpQuat2.setFromEuler(new THREE.Euler(pitch, yaw, roll, "YXZ"));
  riderTargetQuat.copy(tmpQuat).multiply(tmpQuat2);
  rider.quaternion.identity();

  // ---- pelican life ----
  const flapPhase = t * 2.05;
  const glide = 0.55 + 0.45 * Math.sin(t * 0.23); // alternates glide / active flap
  const flap = Math.sin(flapPhase) * (0.22 + glide * 0.5);
  const flap2 = Math.sin(flapPhase - 0.22) * (0.22 + glide * 0.5);
  pelican.leftWing.rotation.z = -0.26 - flap;
  pelican.rightWing.rotation.z = 0.26 + flap2;
  pelican.leftWing.rotation.x = 0.1 + Math.sin(flapPhase * 2 + 0.4) * 0.07;
  pelican.rightWing.rotation.x = 0.1 + Math.sin(flapPhase * 2) * 0.07;

  pelican.head.position.y = 3.22 + Math.sin(t * 1.1) * 0.045;
  pelican.head.rotation.z = Math.sin(t * 0.63) * 0.12;
  pelican.head.rotation.x = -0.05 + Math.sin(t * 0.42) * 0.09;
  pelican.beakGroup.rotation.x = 0.06 + Math.sin(t * 0.85) * 0.045;
  pelican.pouch.scale.y = 0.66 + Math.sin(t * 1.7) * 0.035;

  // ---- spray ----
  const sprayPos = tmpNormal.copy(rider.position);
  sprayPos.y += 0.12;
  sprayPos.z -= 2.5;
  sprayPos.x += Math.sin(t * 0.31) * 0.25;
  if (Math.random() < dt * 60) emitSpray(sprayPos, 3 + Math.floor(Math.random() * 5));
  emitSpray(sprayPos, Math.random() < 0.75 ? 1 : 0, 0.85);
  updateSpray(dt);

  // ---- clouds & distant birds ----
  for (const c of clouds) {
    c.position.x += c.userData.drift * dt;
    if (c.position.x > 240) c.position.x = -240;
  }
  for (const b of distantBirds) {
    const a = t * b.userData.speed + b.userData.phase;
    b.position.set(
      Math.cos(a) * b.userData.radius,
      b.userData.height + Math.sin(t * 0.4 + b.userData.phase) * 0.8,
      Math.sin(a) * b.userData.radius - 26
    );
    b.rotation.y = -a + Math.PI / 2;
    const f = Math.sin(t * b.userData.flap + b.userData.phase) * 0.85;
    b.userData.wings[0].rotation.z = -f;
    b.userData.wings[1].rotation.z = f;
  }

  // ---- camera: slow cinematic sway around the rider ----
  const camAngle = 0.35;
  const dist = 13.5;
  camDesired.set(
    rider.position.x + Math.sin(camAngle) * dist,
    rider.position.y + 2.4,
    rider.position.z + Math.cos(camAngle) * dist
  );
  camera.position.lerp(camDesired, 1 - Math.pow(0.06, dt));
  camTarget.lerp(
    tmpNormal.copy(rider.position).add(new THREE.Vector3(0, 2.3, 0)),
    1 - Math.pow(0.02, dt)
  );
  camera.lookAt(camTarget);

  renderer.render(scene, camera);
}

animate();

// ---------------------------------------------------------------------------
// Resize
// ---------------------------------------------------------------------------

window.addEventListener("resize", () => {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
});