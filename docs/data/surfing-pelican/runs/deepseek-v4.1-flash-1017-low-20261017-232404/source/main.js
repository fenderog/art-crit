import * as THREE from "three";

/* ------------------------------------------------------------------ *
 *  Surfing Pelican — a small procedural, continuously animated scene
 * ------------------------------------------------------------------ */

const app = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  42,
  window.innerWidth / window.innerHeight,
  0.1,
  900,
);
camera.position.set(8, 3.2, 7);

const FOG_COLOR = new THREE.Color("#e8ad84");
scene.fog = new THREE.Fog(FOG_COLOR, 38, 135);

const sunDir = new THREE.Vector3(-0.58, 0.15, -0.80).normalize();

/* ----------------------------- lighting ---------------------------- */

const hemi = new THREE.HemisphereLight(0xcfe5f2, 0x24535b, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffd2a1, 3.0);
sun.position.copy(sunDir).multiplyScalar(42);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 90;
sun.shadow.camera.left = -9;
sun.shadow.camera.right = 9;
sun.shadow.camera.top = 9;
sun.shadow.camera.bottom = -9;
sun.shadow.bias = -0.0009;
sun.shadow.normalBias = 0.035;
scene.add(sun);
scene.add(sun.target);

const fill = new THREE.DirectionalLight(0xffb989, 1.0);
fill.position.set(8, 4, 10);
scene.add(fill);
scene.add(fill.target);

/* ------------------------------- sky ------------------------------- */

const skyMaterial = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  depthWrite: false,
  uniforms: {
    uSunDir: { value: sunDir },
    uTop: { value: new THREE.Color("#3a6c9d") },
    uMid: { value: new THREE.Color("#93abc0") },
    uHorizon: { value: new THREE.Color("#f4bd8e") },
    uBelow: { value: new THREE.Color("#c37d63") },
  },
  vertexShader: /* glsl */ `
    varying vec3 vDir;
    void main() {
      vec4 wp = modelMatrix * vec4(position, 1.0);
      vDir = wp.xyz - cameraPosition;
      gl_Position = projectionMatrix * viewMatrix * wp;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform vec3 uSunDir;
    uniform vec3 uTop;
    uniform vec3 uMid;
    uniform vec3 uHorizon;
    uniform vec3 uBelow;
    varying vec3 vDir;

    void main() {
      vec3 d = normalize(vDir);
      float h = d.y;

      vec3 col = mix(uHorizon, uMid, smoothstep(-0.01, 0.22, h));
      col = mix(col, uTop, smoothstep(0.18, 0.72, h));
      col = mix(col, uBelow, smoothstep(0.0, -0.22, h));

      float sd = max(dot(d, uSunDir), 0.0);
      col += vec3(1.0, 0.52, 0.26) * pow(sd, 5.0) * 0.32;
      col += vec3(1.0, 0.73, 0.44) * pow(sd, 42.0) * 0.62;
      col += vec3(1.0, 0.90, 0.72) * pow(sd, 620.0) * 1.9;

      // faint warm haze hanging over the horizon
      col += vec3(0.10, 0.035, 0.0) * exp(-abs(h) * 22.0);

      gl_FragColor = vec4(col, 1.0);
    }
  `,
});

const sky = new THREE.Mesh(new THREE.SphereGeometry(520, 48, 32), skyMaterial);
sky.frustumCulled = false;
scene.add(sky);

/* --------------------------- wave model ---------------------------- */

const WAVES = [
  { dir: [1.0, 0.24], amp: 0.47, len: 26.0, phase: 0.35 },
  { dir: [-0.38, 1.0], amp: 0.26, len: 16.5, phase: 1.15 },
  { dir: [0.72, -0.68], amp: 0.145, len: 10.5, phase: 2.05 },
  { dir: [-1.0, -0.22], amp: 0.078, len: 6.8, phase: 0.7 },
  { dir: [0.2, 1.0], amp: 0.048, len: 4.7, phase: 3.9 },
];
const TOTAL_AMP = WAVES.reduce((s, w) => s + w.amp, 0);
const GRAVITY = 9.81;
const WAVE_SPEED = 0.55;

const normalizedWaves = WAVES.map((w) => {
  const l = Math.hypot(w.dir[0], w.dir[1]);
  return { ...w, dx: w.dir[0] / l, dz: w.dir[1] / l };
});

function waveInfo(x, z, t) {
  let h = 0;
  let dhx = 0;
  let dhz = 0;
  for (const w of normalizedWaves) {
    const k = (Math.PI * 2) / w.len;
    const omega = Math.sqrt(GRAVITY * k) * WAVE_SPEED;
    const ph = k * (w.dx * x + w.dz * z) - omega * t + w.phase;
    h += w.amp * Math.sin(ph);
    const c = w.amp * k * Math.cos(ph);
    dhx += c * w.dx;
    dhz += c * w.dz;
  }
  return { h, dhx, dhz };
}

/* ------------------------------ water ------------------------------ */

const waterUniforms = {
  uTime: { value: 0 },
  uWaveDirs: { value: normalizedWaves.map((w) => new THREE.Vector2(w.dx, w.dz)) },
  uWaveAmp: { value: normalizedWaves.map((w) => w.amp) },
  uWaveLen: { value: normalizedWaves.map((w) => w.len) },
  uWavePhase: { value: normalizedWaves.map((w) => w.phase) },
  uSunDir: { value: sunDir },
  uTotalAmp: { value: TOTAL_AMP },
  uBoardPos: { value: new THREE.Vector3(0, 0, 0) },
  uBoardYaw: { value: 0 },
  uFogColor: { value: FOG_COLOR },
  uFogNear: { value: 38 },
  uFogFar: { value: 135 },
};

const waterMaterial = new THREE.ShaderMaterial({
  uniforms: waterUniforms,
  vertexShader: /* glsl */ `
    uniform float uTime;
    uniform vec2 uWaveDirs[5];
    uniform float uWaveAmp[5];
    uniform float uWaveLen[5];
    uniform float uWavePhase[5];

    varying vec3 vWorldPos;
    varying vec3 vNormal;
    varying float vHeight;
    varying float vFogDepth;

    void main() {
      vec2 p = position.xz;
      float h = 0.0;
      vec2 slope = vec2(0.0);

      for (int i = 0; i < 5; i++) {
        float k = 6.28318530718 / uWaveLen[i];
        float omega = sqrt(9.81 * k) * 0.55;
        vec2 dir = normalize(uWaveDirs[i]);
        float ph = k * dot(dir, p) - omega * uTime + uWavePhase[i];
        h += uWaveAmp[i] * sin(ph);
        slope += uWaveAmp[i] * k * dir * cos(ph);
      }

      vec3 displaced = vec3(position.x, h, position.z);
      vNormal = normalize(vec3(-slope.x, 1.0, -slope.y));
      vHeight = h;

      vec4 wp = modelMatrix * vec4(displaced, 1.0);
      vWorldPos = wp.xyz;
      vec4 mv = viewMatrix * wp;
      vFogDepth = -mv.z;
      gl_Position = projectionMatrix * mv;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform float uTime;
    uniform vec3 uSunDir;
    uniform vec3 uBoardPos;
    uniform float uBoardYaw;
    uniform float uTotalAmp;
    uniform vec3 uFogColor;
    uniform float uFogNear;
    uniform float uFogFar;

    varying vec3 vWorldPos;
    varying vec3 vNormal;
    varying float vHeight;
    varying float vFogDepth;

    float hash(vec2 p) {
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }

    float noise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }

    float fbm(vec2 p) {
      float v = 0.0;
      float a = 0.5;
      for (int i = 0; i < 4; i++) {
        v += a * noise(p);
        p = p * 2.03 + vec2(17.1, 9.2);
        a *= 0.5;
      }
      return v;
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(cameraPosition - vWorldPos);
      float fres = pow(1.0 - max(dot(N, V), 0.0), 3.0);

      vec2 p = vWorldPos.xz;
      float hn = clamp(vHeight / uTotalAmp * 0.5 + 0.5, 0.0, 1.0);

      vec3 deep = vec3(0.008, 0.072, 0.096);
      vec3 shallow = vec3(0.048, 0.275, 0.305);
      vec3 water = mix(deep, shallow, smoothstep(0.15, 0.92, hn) * 0.72);
      water = mix(water, vec3(0.02, 0.16, 0.19), 0.2);

      // reflected sky
      vec3 R = reflect(-V, N);
      float ry = clamp(R.y, 0.0, 1.0);
      vec3 skyRef = mix(vec3(1.0, 0.69, 0.46), vec3(0.33, 0.55, 0.74),
                        smoothstep(0.02, 0.62, ry));
      float sunRef = pow(max(dot(R, uSunDir), 0.0), 340.0);
      float sunHalo = pow(max(dot(R, uSunDir), 0.0), 16.0);
      skyRef += vec3(1.0, 0.63, 0.34) * sunHalo * 0.10;
      skyRef += vec3(1.0, 0.78, 0.5) * sunRef * 1.4;

      vec3 col = mix(water, skyRef, clamp(fres * 0.92 + 0.08, 0.0, 1.0));

      // direct sun glint
      vec3 H = normalize(V + uSunDir);
      float spec = pow(max(dot(N, H), 0.0), 260.0);
      col += vec3(1.0, 0.73, 0.42) * spec * 1.8;

      // chop / micro sparkle
      float micro = fbm(p * 4.5 + vec2(uTime * 0.22, -uTime * 0.16));
      col += vec3(0.35, 0.5, 0.55) * smoothstep(0.55, 0.95, micro) * 0.10;

      // whitecaps on the crests
      float crest = smoothstep(0.68, 0.94, hn);
      float foamNoise = fbm(p * 2.2 + vec2(uTime * 0.35, uTime * 0.12));
      float foam = crest * smoothstep(0.42, 0.82, foamNoise) * 0.85;

      // foam collar and wake around the board
      vec2 rel = p - uBoardPos.xz;
      float dist = length(rel);
      float ring = smoothstep(1.35, 0.28, dist);
      float closeFoam = ring * smoothstep(0.35, 0.7, fbm(p * 5.0 + vec2(0.0, uTime * 0.5)));

      float c = cos(uBoardYaw);
      float s = sin(uBoardYaw);
      vec2 local = vec2(c * rel.x - s * rel.y, s * rel.x + c * rel.y);
          float width = 0.32 + (-local.y) * 0.12;
      float trail = smoothstep(width, width * 0.15, abs(local.x))
                  * (1.0 - smoothstep(-7.0, -0.4, local.y))
                  * smoothstep(-8.0, -7.0, local.y);
      float wake = (trail * 0.65 + closeFoam * 0.65) * (0.35 + foamNoise * 0.65);
      foam += wake * 0.8;

      col = mix(col, vec3(0.93, 0.94, 0.89), clamp(foam, 0.0, 0.9));

      float fog = smoothstep(uFogNear, uFogFar, vFogDepth);
      col = mix(col, uFogColor, fog);

      gl_FragColor = vec4(col, 1.0);
    }
  `,
});

const waterGeometry = new THREE.PlaneGeometry(320, 320, 380, 380);
waterGeometry.rotateX(-Math.PI / 2);
const water = new THREE.Mesh(waterGeometry, waterMaterial);
water.frustumCulled = false;
scene.add(water);

/* ---------------------------- textures ----------------------------- */

function makeRadialTexture(inner, outer, stops) {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, inner, 64, 64, outer);
  for (const [at, color] of stops) g.addColorStop(at, color);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const dotTexture = makeRadialTexture(0, 64, [
  [0, "rgba(255,255,255,1)"],
  [0.45, "rgba(255,255,255,0.7)"],
  [1, "rgba(255,255,255,0)"],
]);

const shadowTexture = makeRadialTexture(2, 64, [
  [0, "rgba(20,16,12,0.55)"],
  [0.55, "rgba(20,16,12,0.25)"],
  [1, "rgba(20,16,12,0)"],
]);

function makeCloudTexture(seed) {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 256;
  const ctx = c.getContext("2d");
  let s = seed;
  const rand = () => {
    s = (s * 16807) % 2147483647;
    return (s - 2) / 2147483645;
  };
  ctx.clearRect(0, 0, 512, 256);
  for (let i = 0; i < 30; i++) {
    const x = 90 + rand() * 332;
    const y = 105 + rand() * 60;
    const r = 24 + rand() * 52;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, "rgba(255,244,230,0.34)");
    g.addColorStop(0.55, "rgba(255,238,220,0.16)");
    g.addColorStop(1, "rgba(255,238,220,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 512, 256);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* ------------------------------ clouds ----------------------------- */

const cloudMats = [];
for (let i = 0; i < 9; i++) {
  const tex = makeCloudTexture(7919 + i * 421);
  const mat = new THREE.SpriteMaterial({
    map: tex,
    transparent: true,
    depthWrite: false,
    fog: false,
    opacity: 0.5 + (i % 3) * 0.09,
  });
  const sprite = new THREE.Sprite(mat);
  const angle = (i / 9) * Math.PI * 2 + 0.5;
  const radius = 145 + (i % 4) * 24;
  sprite.position.set(
    Math.cos(angle) * radius,
    17 + (i % 5) * 7,
    Math.sin(angle) * radius,
  );
  const sc = 54 + (i % 4) * 18;
  sprite.scale.set(sc, sc * 0.42, 1);
  scene.add(sprite);
  cloudMats.push(mat);
}

/* ---------------------------- surfboard ---------------------------- */

const boardShape = new THREE.Shape();
boardShape.moveTo(0, -1.62);
boardShape.bezierCurveTo(0.26, -1.35, 0.43, -0.55, 0.47, 0.18);
boardShape.bezierCurveTo(0.5, 0.92, 0.43, 1.42, 0.29, 1.56);
boardShape.bezierCurveTo(0.14, 1.68, -0.14, 1.68, -0.29, 1.56);
boardShape.bezierCurveTo(-0.43, 1.42, -0.5, 0.92, -0.47, 0.18);
boardShape.bezierCurveTo(-0.43, -0.55, -0.26, -1.35, 0, -1.62);

const boardGeo = new THREE.ExtrudeGeometry(boardShape, {
  depth: 0.1,
  bevelEnabled: true,
  bevelThickness: 0.035,
  bevelSize: 0.032,
  bevelSegments: 3,
  curveSegments: 26,
});
boardGeo.rotateX(-Math.PI / 2);

const boardMat = new THREE.MeshStandardMaterial({
  color: 0xf1dfbd,
  roughness: 0.38,
  metalness: 0.02,
});
const board = new THREE.Mesh(boardGeo, boardMat);
board.position.y = 0.02;
board.castShadow = true;
board.receiveShadow = true;

const stripeGeo = new THREE.CapsuleGeometry(0.052, 2.18, 5, 12);
stripeGeo.rotateX(Math.PI / 2);
const stripe = new THREE.Mesh(
  stripeGeo,
  new THREE.MeshStandardMaterial({ color: 0xd96750, roughness: 0.42 }),
);
stripe.position.set(0, 0.152, -0.05);
stripe.castShadow = false;

const stripeTwoGeo = new THREE.CapsuleGeometry(0.018, 1.72, 4, 10);
stripeTwoGeo.rotateX(Math.PI / 2);
const stripeTwo = new THREE.Mesh(
  stripeTwoGeo,
  new THREE.MeshStandardMaterial({ color: 0x2f6c72, roughness: 0.45 }),
);
stripeTwo.position.set(0, 0.157, -0.02);

const finShape = new THREE.Shape();
finShape.moveTo(0, 0);
finShape.lineTo(0.58, 0);
finShape.lineTo(0.38, 0.34);
finShape.lineTo(0.04, 0.44);
finShape.closePath();
const finGeo = new THREE.ExtrudeGeometry(finShape, {
  depth: 0.035,
  bevelEnabled: true,
  bevelThickness: 0.008,
  bevelSize: 0.01,
  bevelSegments: 2,
});
finGeo.rotateY(Math.PI / 2);
const fin = new THREE.Mesh(
  finGeo,
  new THREE.MeshStandardMaterial({ color: 0x24565c, roughness: 0.5 }),
);
fin.position.set(0, -0.45, -0.72);
fin.castShadow = true;

const boardShadow = new THREE.Mesh(
  new THREE.PlaneGeometry(1.55, 2.0),
  new THREE.MeshBasicMaterial({
    map: shadowTexture,
    transparent: true,
    depthWrite: false,
    opacity: 0.55,
  }),
);
boardShadow.rotation.x = -Math.PI / 2;
boardShadow.position.y = 0.164;
boardShadow.position.z = 0.12;

/* --------------------------- pelican body -------------------------- */

const pelican = new THREE.Group();
pelican.position.y = -0.03;

const whiteMat = new THREE.MeshStandardMaterial({
  color: 0xf8f2e4,
  roughness: 0.78,
  metalness: 0.0,
});
const creamMat = new THREE.MeshStandardMaterial({
  color: 0xefe4cf,
  roughness: 0.82,
});
const beakMat = new THREE.MeshStandardMaterial({
  color: 0xe9a75f,
  roughness: 0.56,
});
const pouchMat = new THREE.MeshStandardMaterial({
  color: 0xd98b4f,
  roughness: 0.66,
});
const darkMat = new THREE.MeshStandardMaterial({
  color: 0x5d584e,
  roughness: 0.82,
});
const legMat = new THREE.MeshStandardMaterial({
  color: 0xe28e3d,
  roughness: 0.7,
});

const bodyGroup = new THREE.Group();
pelican.add(bodyGroup);

const body = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), whiteMat);
body.scale.set(0.43, 0.61, 0.51);
body.position.set(0, 1.08, 0.01);
body.rotation.x = -0.12;
body.castShadow = true;
body.receiveShadow = true;
bodyGroup.add(body);

const chest = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), creamMat);
chest.scale.set(0.34, 0.42, 0.34);
chest.position.set(0, 1.07, 0.32);
chest.castShadow = true;
bodyGroup.add(chest);

// neck
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 1.42, 0.2),
  new THREE.Vector3(0, 1.62, 0.27),
  new THREE.Vector3(0, 1.82, 0.31),
  new THREE.Vector3(0, 1.99, 0.37),
]);
const neck = new THREE.Mesh(
  new THREE.TubeGeometry(neckCurve, 24, 0.145, 14, false),
  whiteMat,
);
neck.castShadow = true;
bodyGroup.add(neck);

// slight shoulder blend
const neckBase = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 14), whiteMat);
neckBase.scale.set(0.19, 0.23, 0.2);
neckBase.position.set(0, 1.44, 0.21);
neckBase.castShadow = true;
bodyGroup.add(neckBase);

// head
const headGroup = new THREE.Group();
headGroup.position.set(0, 2.1, 0.4);
bodyGroup.add(headGroup);

const head = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), whiteMat);
head.scale.set(0.245, 0.265, 0.29);
head.castShadow = true;
headGroup.add(head);

// crown / little crest
for (let i = 0; i < 3; i++) {
  const crest = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), creamMat);
  crest.scale.set(0.035, 0.085, 0.045);
  crest.position.set((i - 1) * 0.055, 0.205, -0.08 - i * 0.03);
  crest.rotation.x = -0.5;
  headGroup.add(crest);
}

// eyes
const eyeGeo = new THREE.SphereGeometry(0.039, 14, 10);
const glintGeo = new THREE.SphereGeometry(0.012, 8, 6);
for (const side of [-1, 1]) {
  const eye = new THREE.Mesh(eyeGeo, new THREE.MeshStandardMaterial({
    color: 0x17191a,
    roughness: 0.25,
  }));
  eye.position.set(side * 0.172, 0.045, 0.205);
  headGroup.add(eye);

  const glint = new THREE.Mesh(glintGeo, new THREE.MeshBasicMaterial({
    color: 0xffffff,
  }));
  glint.position.set(side * 0.16, 0.066, 0.235);
  headGroup.add(glint);
}

// upper mandible — custom elliptical, slightly down-curved taper
function makeBeakGeometry() {
  const rings = 18;
  const segs = 12;
  const positions = [];
  const indices = [];

  for (let i = 0; i <= rings; i++) {
    const t = i / rings;
    const z = 0.2 + 1.18 * t;
    const y = 0.018 - 0.095 * t - 0.04 * t * t;
    const rx = THREE.MathUtils.lerp(0.108, 0.012, Math.pow(t, 0.75));
    const ry = THREE.MathUtils.lerp(0.062, 0.008, Math.pow(t, 0.7));

    for (let s = 0; s < segs; s++) {
      const a = (s / segs) * Math.PI * 2;
      positions.push(
        Math.cos(a) * rx,
        y + Math.sin(a) * ry,
        z,
      );
    }
  }

  for (let i = 0; i < rings; i++) {
    for (let s = 0; s < segs; s++) {
      const a = i * segs + s;
      const b = i * segs + ((s + 1) % segs);
      const c = (i + 1) * segs + ((s + 1) % segs);
      const d = (i + 1) * segs + s;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

const beak = new THREE.Mesh(makeBeakGeometry(), beakMat);
beak.castShadow = true;
headGroup.add(beak);

// throat pouch — a long soft bag hanging beneath the mandible
function makePouchGeometry() {
  const rings = 22;
  const segs = 14;
  const positions = [];
  const indices = [];

  for (let i = 0; i <= rings; i++) {
    const t = i / rings;
    const z = 0.27 + 1.09 * t;
    const lineY = 0.018 - 0.095 * t - 0.04 * t * t;
    const depth = 0.028 + 0.19 * Math.sin(Math.PI * Math.min(1, t * 0.96 + 0.04));
    const rx = 0.108 * (1 - 0.78 * t) + 0.006;
    const ry = depth * 0.5;
    const cy = lineY - 0.006 - depth * 0.55;

    for (let s = 0; s < segs; s++) {
      const a = (s / segs) * Math.PI * 2;
      positions.push(Math.cos(a) * rx, cy + Math.sin(a) * ry, z);
    }
  }

  for (let i = 0; i < rings; i++) {
    for (let s = 0; s < segs; s++) {
      const a = i * segs + s;
      const b = i * segs + ((s + 1) % segs);
      const c = (i + 1) * segs + ((s + 1) % segs);
      const d = (i + 1) * segs + s;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

const pouch = new THREE.Mesh(makePouchGeometry(), pouchMat);
pouch.castShadow = true;
headGroup.add(pouch);

// wings — a fan of long, individually layered feathers
function makeFeatherGeometry() {
  const rings = 12;
  const segs = 10;
  const positions = [];
  const indices = [];

  for (let i = 0; i <= rings; i++) {
    const t = i / rings;
    const prof = Math.pow(Math.sin(Math.PI * (t * 0.92 + 0.04)), 0.62);
    for (let s = 0; s < segs; s++) {
      const a = (s / segs) * Math.PI * 2;
      positions.push(t, Math.sin(a) * 0.042 * prof, Math.cos(a) * 0.5 * prof);
    }
  }

  for (let i = 0; i < rings; i++) {
    for (let s = 0; s < segs; s++) {
      const a = i * segs + s;
      const b = i * segs + ((s + 1) % segs);
      const c = (i + 1) * segs + ((s + 1) % segs);
      const d = (i + 1) * segs + s;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

const featherGeo = makeFeatherGeometry();
const wings = [];
for (const side of [-1, 1]) {
  const wingGroup = new THREE.Group();
  wingGroup.position.set(side * 0.36, 1.4, 0.02);
  if (side < 0) wingGroup.scale.x = -1;
  wingGroup.rotation.z = side < 0 ? -0.14 : 0.14;
  wingGroup.rotation.y = 0.08;
  wingGroup.rotation.x = -0.04;

  const covert = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), creamMat);
  covert.scale.set(0.4, 0.075, 0.24);
  covert.position.set(0.18, 0.015, 0.02);
  covert.castShadow = true;
  wingGroup.add(covert);

  for (let i = 0; i < 9; i++) {
    const t = i / 8;
    const len = 1.5 - 0.26 * t + 0.08 * Math.sin(t * Math.PI);
    const width = 0.2 + 0.09 * Math.sin(t * Math.PI);
    const theta = -0.14 + t * 0.56;

    const feather = new THREE.Mesh(featherGeo, i >= 6 ? darkMat : creamMat);
    feather.position.set(0.05, 0.02 - i * 0.0035, 0.02 - i * 0.004);
    feather.scale.set(len, 1, width);
    feather.rotation.y = theta;
    feather.rotation.z = 0.015 + (i % 2) * 0.01;
    feather.castShadow = true;
    wingGroup.add(feather);
  }

  bodyGroup.add(wingGroup);
  wings.push({ group: wingGroup, side });
}

// tail feathers
const tailGroup = new THREE.Group();
tailGroup.position.set(0, 1.02, -0.4);
bodyGroup.add(tailGroup);
for (let i = 0; i < 5; i++) {
  const f = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 7), creamMat);
  f.scale.set(0.065, 0.035, 0.28);
  f.position.set((i - 2) * 0.065, 0, -0.12 - Math.abs(i - 2) * 0.015);
  f.rotation.y = (i - 2) * 0.13;
  f.rotation.x = -0.15;
  f.castShadow = true;
  tailGroup.add(f);
}

// legs and webbed feet
for (const side of [-1, 1]) {
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.042, 0.34, 10), legMat);
  leg.position.set(side * 0.16, 0.4, 0.06);
  leg.rotation.z = side * 0.05;
  leg.castShadow = true;
  bodyGroup.add(leg);

  const foot = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 8), legMat);
  foot.scale.set(0.11, 0.035, 0.2);
  foot.position.set(side * 0.16, 0.225, 0.19);
  foot.rotation.y = side * 0.18;
  foot.castShadow = true;
  bodyGroup.add(foot);
}

/* ------------------------- assemble the rider ----------------------- */

const rider = new THREE.Group();
rider.add(board, stripe, stripeTwo, fin, boardShadow, pelican);
scene.add(rider);

/* --------------------------- spray particles ----------------------- */

const SPRAY_COUNT = 240;
const sprayPositions = new Float32Array(SPRAY_COUNT * 3);
const spraySizes = new Float32Array(SPRAY_COUNT);
const sprayAlphas = new Float32Array(SPRAY_COUNT);
const sprayData = [];
for (let i = 0; i < SPRAY_COUNT; i++) {
  sprayPositions[i * 3 + 1] = -100;
  spraySizes[i] = 0.1;
  sprayData.push({ life: 0, maxLife: 1, vx: 0, vy: 0, vz: 0, size: 0.2 });
}

const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
sprayGeo.setAttribute("aSize", new THREE.BufferAttribute(spraySizes, 1));
sprayGeo.setAttribute("aAlpha", new THREE.BufferAttribute(sprayAlphas, 1));

const sprayMat = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
  uniforms: {
    uMap: { value: dotTexture },
  },
  vertexShader: /* glsl */ `
    attribute float aSize;
    attribute float aAlpha;
    varying float vAlpha;
    void main() {
      vAlpha = aAlpha;
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = aSize * (330.0 / max(-mv.z, 0.1));
      gl_Position = projectionMatrix * mv;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D uMap;
    varying float vAlpha;
    void main() {
      vec4 tex = texture2D(uMap, gl_PointCoord);
      gl_FragColor = vec4(1.0, 0.96, 0.88, tex.a * vAlpha);
    }
  `,
});

const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

let spawnAccumulator = 0;
let sprayCursor = 0;

const tmpVec = new THREE.Vector3();
const tmpVec2 = new THREE.Vector3();

function spawnSpray(dt) {
  spawnAccumulator += dt * 105;
  const quat = rider.quaternion;
  while (spawnAccumulator >= 1) {
    spawnAccumulator -= 1;
    const idx = sprayCursor;
    sprayCursor = (sprayCursor + 1) % SPRAY_COUNT;
    const d = sprayData[idx];

    const side = Math.random() < 0.5 ? -1 : 1;
    tmpVec.set(side * (0.42 + Math.random() * 0.2), 0.06, -1.0 + Math.random() * 1.6);
    rider.localToWorld(tmpVec);
    tmpVec2.set(side * (1.8 + Math.random() * 2.0), 1.4 + Math.random() * 1.4, -1.4 + Math.random() * 1.0);
    tmpVec2.applyQuaternion(quat);

    sprayPositions[idx * 3] = tmpVec.x;
    sprayPositions[idx * 3 + 1] = Math.max(tmpVec.y, 0.05);
    sprayPositions[idx * 3 + 2] = tmpVec.z;
    d.vx = tmpVec2.x;
    d.vy = tmpVec2.y;
    d.vz = tmpVec2.z;
    d.maxLife = d.life = 0.55 + Math.random() * 0.65;
    d.size = 0.06 + Math.random() * 0.17 + (Math.random() < 0.08 ? 0.14 : 0);
    spraySizes[idx] = d.size;
  }
}

function updateSpray(dt) {
  for (let i = 0; i < SPRAY_COUNT; i++) {
    const d = sprayData[i];
    if (d.life <= 0) {
      sprayAlphas[i] = 0;
      continue;
    }
    d.life -= dt;
    if (d.life <= 0) {
      sprayAlphas[i] = 0;
      sprayPositions[i * 3 + 1] = -100;
      continue;
    }
    d.vy -= 5.2 * dt;
    sprayPositions[i * 3] += d.vx * dt;
    sprayPositions[i * 3 + 1] += d.vy * dt;
    sprayPositions[i * 3 + 2] += d.vz * dt;
    const f = d.life / d.maxLife;
    sprayAlphas[i] = Math.sin(Math.min(1, (1 - f) * 6) * Math.PI * 0.5) * Math.pow(f, 1.5) * 0.62;
  }
  sprayGeo.attributes.position.needsUpdate = true;
  sprayGeo.attributes.aAlpha.needsUpdate = true;
  sprayGeo.attributes.aSize.needsUpdate = true;
}

/* --------------------------- distant birds ------------------------- */

const birds = [];
const birdMat = new THREE.MeshBasicMaterial({
  color: 0x5b5860,
  side: THREE.DoubleSide,
  fog: false,
});
const birdGeo = new THREE.BufferGeometry();
birdGeo.setAttribute("position", new THREE.Float32BufferAttribute([
  0, 0, 0,
  0.95, 0.12, 0.08,
  0.92, -0.04, -0.02,
], 3));
birdGeo.computeVertexNormals();

for (let i = 0; i < 5; i++) {
  const g = new THREE.Group();
  const left = new THREE.Mesh(birdGeo, birdMat);
  left.scale.x = -1;
  const right = new THREE.Mesh(birdGeo, birdMat);
  g.add(left, right);
  g.position.set(
    -30 + i * 17 + Math.random() * 6,
    16 + Math.random() * 10,
    -46 - Math.random() * 34,
  );
  g.scale.setScalar(0.55 + Math.random() * 0.4);
  g.userData = {
    left,
    right,
    speed: 0.25 + Math.random() * 0.35,
    phase: Math.random() * Math.PI * 2,
    baseZ: g.position.z,
  };
  scene.add(g);
  birds.push(g);
}

/* ----------------------------- animation --------------------------- */

const startTime = performance.now();
let lastTime = startTime;
const riderTarget = new THREE.Vector3();
const cameraTarget = new THREE.Vector3(0, 1.8, 0);
const desiredCam = new THREE.Vector3();
const camLook = new THREE.Vector3();
const forward = new THREE.Vector3();
const right = new THREE.Vector3();
const forwardOnPlane = new THREE.Vector3();
const normal = new THREE.Vector3();
const basis = new THREE.Matrix4();

let riderYaw = 0;

function updateRider(t, dt) {
  const px = Math.sin(t * 0.23) * 2.9 + Math.sin(t * 0.071 + 1.7) * 0.8;
  const pz = Math.sin(t * 0.171 + 0.8) * 1.7;
  const vx = 0.23 * 2.9 * Math.cos(t * 0.23) + 0.071 * 0.8 * Math.cos(t * 0.071 + 1.7);
  const vz = 0.171 * 1.7 * Math.cos(t * 0.171 + 0.8);

  const info = waveInfo(px, pz, t);
  riderTarget.set(px, info.h + 0.055, pz);
  rider.position.copy(riderTarget);

  riderYaw = Math.atan2(vx, vz);
  forward.set(Math.sin(riderYaw), 0, Math.cos(riderYaw));
  normal.set(-info.dhx, 1, -info.dhz).normalize();
  right.crossVectors(normal, forward).normalize();
  forwardOnPlane.crossVectors(right, normal).normalize();
  basis.makeBasis(right, normal, forwardOnPlane);
  rider.quaternion.setFromRotationMatrix(basis);

  // gentle carving bank
  const bank = Math.sin(t * 0.53) * 0.055 + Math.sin(t * 0.23) * 0.035;
  rider.rotateZ(bank);

  waterUniforms.uBoardPos.value.set(px, info.h, pz);
  waterUniforms.uBoardYaw.value = riderYaw;
}

function updatePelican(t) {
  const sway = Math.sin(t * 1.15);
  const bob = Math.sin(t * 2.05);

  pelican.position.y = -0.03 + bob * 0.018;
  bodyGroup.rotation.z = sway * 0.025;
  bodyGroup.rotation.x = Math.sin(t * 0.83 + 0.6) * 0.018;
  bodyGroup.rotation.y = Math.sin(t * 0.37) * 0.04;

  headGroup.rotation.y = Math.sin(t * 0.43 + 0.4) * 0.16;
  headGroup.rotation.x = Math.sin(t * 1.6 + 1.0) * 0.028;
  headGroup.position.y = 2.1 + Math.sin(t * 1.7 + 0.3) * 0.012;

  for (const w of wings) {
    const flap = Math.sin(t * 1.55 + (w.side > 0 ? 0 : 0.5)) * 0.09;
    const base = w.side < 0 ? 0.1 : -0.1;
    w.group.rotation.z = base + (w.side < 0 ? flap : -flap);
    w.group.rotation.x = Math.sin(t * 0.9 + w.side) * 0.03;
  }

  tailGroup.rotation.y = Math.sin(t * 0.9) * 0.1;
  tailGroup.rotation.x = -0.15 + Math.sin(t * 1.4) * 0.03;
}

function updateCamera(t) {
  const angle = Math.PI / 2 - riderYaw + 0.16 + Math.sin(t * 0.09) * 0.4;
  const radius = 9.85 + Math.sin(t * 0.11) * 0.45;
  desiredCam.set(
    rider.position.x + Math.cos(angle) * radius,
    2.82 + Math.sin(t * 0.19) * 0.3,
    rider.position.z + Math.sin(angle) * radius,
  );
  camera.position.lerp(desiredCam, 0.028);

  camLook.set(
    rider.position.x + Math.sin(t * 0.17) * 0.25,
    rider.position.y + 1.12,
    rider.position.z + Math.cos(t * 0.17) * 0.2,
  );
  cameraTarget.lerp(camLook, 0.055);
  camera.lookAt(cameraTarget);

  // keep the sun light near the rider for stable shadows
  sun.position.set(
    rider.position.x + sunDir.x * 42,
    sunDir.y * 42,
    rider.position.z + sunDir.z * 42,
  );
  sun.target.position.copy(rider.position);
  sun.target.updateMatrixWorld();

  // warm fill from roughly the camera side, so the bird reads against the sun
  fill.position.set(
    rider.position.x + (camera.position.x - rider.position.x) * 0.55,
    rider.position.y + 4.5,
    rider.position.z + (camera.position.z - rider.position.z) * 0.55,
  );
  fill.target.position.copy(rider.position);
  fill.target.updateMatrixWorld();
}

function updateBirds(t, dt) {
  for (const b of birds) {
    b.position.x += b.userData.speed * dt;
    if (b.position.x > 58) b.position.x = -58;
    const flap = Math.sin(t * 2.5 + b.userData.phase) * 0.55;
    b.userData.left.rotation.z = -0.1 + flap;
    b.userData.right.rotation.z = 0.1 - flap;
    b.rotation.y = -0.1;
  }
}

let firstFrame = true;

function animate() {
  const now = performance.now();
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  const t = (now - startTime) / 1000;

  waterUniforms.uTime.value = t;
  updateRider(t, dt);
  updatePelican(t);
  updateCamera(t);
  updateBirds(t, dt);
  spawnSpray(dt);
  updateSpray(dt);

  // slow drift of the clouds
  for (let i = 0; i < cloudMats.length; i++) {
    cloudMats[i].rotation = Math.sin(t * 0.02 + i) * 0.04;
  }

  renderer.render(scene, camera);

  if (firstFrame) {
    firstFrame = false;
    requestAnimationFrame(() => app.classList.add("ready"));
  }
}

renderer.setAnimationLoop(animate);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
});
