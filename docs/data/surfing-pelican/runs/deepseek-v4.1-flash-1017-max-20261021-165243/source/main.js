import * as THREE from "three";

/* -------------------------------------------------------------------------- */
/*  The Surfing Pelican                                                       */
/*  A tiny, entirely procedural golden-hour scene. No external assets.        */
/* -------------------------------------------------------------------------- */

const canvas = document.querySelector("#scene");
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.9;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xe7a184, 42, 165);

const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 420);
const CAMERA_BASE = new THREE.Vector3(4.0, 2.55, 9.4);
const LOOK_BASE = new THREE.Vector3(0.15, 1.62, 0);
camera.position.copy(CAMERA_BASE);

const clock = new THREE.Clock();
let elapsed = 0;

const pointer = {
  x: 0,
  y: 0,
  smoothX: 0,
  smoothY: 0,
  active: false,
};

const tempVec = new THREE.Vector3();

/* -------------------------------------------------------------------------- */
/*  Small helpers                                                             */
/* -------------------------------------------------------------------------- */

const PI = Math.PI;
const TAU = Math.PI * 2;

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smoothstep(min, max, v) {
  const x = clamp((v - min) / (max - min), 0, 1);
  return x * x * (3 - 2 * x);
}

function randomBetween(min, max) {
  return min + Math.random() * (max - min);
}

function makeCanvasTexture(width, height, draw) {
  const c = document.createElement("canvas");
  c.width = width;
  c.height = height;
  const ctx = c.getContext("2d");
  draw(ctx, width, height);
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

function makeGlowTexture(size = 256) {
  return makeCanvasTexture(size, size, (ctx, w, h) => {
    const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
    g.addColorStop(0, "rgba(255,255,255,1)");
    g.addColorStop(0.18, "rgba(255,250,235,0.95)");
    g.addColorStop(0.46, "rgba(255,228,188,0.38)");
    g.addColorStop(0.72, "rgba(255,204,160,0.08)");
    g.addColorStop(1, "rgba(255,200,150,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  });
}

function makeCloudTexture(seed = 1) {
  return makeCanvasTexture(1024, 512, (ctx, w, h) => {
    let rand = seed * 9721;
    const rnd = () => {
      rand = (rand * 16807) % 2147483647;
      return (rand - 1) / 2147483646;
    };

    ctx.clearRect(0, 0, w, h);

    const puffs = 20;
    for (let i = 0; i < puffs; i++) {
      const x = w * (0.16 + rnd() * 0.68);
      const y = h * (0.36 + rnd() * 0.28 - (x / w - 0.5) * 0.1);
      const rx = w * (0.08 + rnd() * 0.19);
      const ry = h * (0.05 + rnd() * 0.10);
      const g = ctx.createRadialGradient(x, y, 0, x, y, 1);
      const shade = 0.75 + rnd() * 0.25;
      g.addColorStop(0, `rgba(255, ${Math.round(240 * shade)}, ${Math.round(228 * shade)}, ${0.2 + rnd() * 0.16})`);
      g.addColorStop(0.46, `rgba(255, ${Math.round(228 * shade)}, ${Math.round(214 * shade)}, ${0.11 + rnd() * 0.1})`);
      g.addColorStop(1, "rgba(255,225,210,0)");
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(rx, ry);
      ctx.translate(-x, -y);
      ctx.fillStyle = g;
      ctx.fillRect(x - rx, y - ry, rx * 2, ry * 2);
      ctx.restore();
    }

    // A few soft horizontal wisps give the cloud its painted silhouette.
    for (let i = 0; i < 5; i++) {
      const y = h * (0.48 + i * 0.028);
      const g = ctx.createLinearGradient(w * 0.12, 0, w * 0.9, 0);
      g.addColorStop(0, "rgba(255,225,210,0)");
      g.addColorStop(0.35, "rgba(255,232,218,0.10)");
      g.addColorStop(0.62, "rgba(255,219,205,0.055)");
      g.addColorStop(1, "rgba(255,225,210,0)");
      ctx.fillStyle = g;
      ctx.fillRect(w * 0.08, y, w * 0.86, h * 0.018);
    }
  });
}

function makeFeatherBumpTexture() {
  return makeCanvasTexture(512, 512, (ctx, w, h) => {
    ctx.fillStyle = "#7f7f7f";
    ctx.fillRect(0, 0, w, h);
    let seed = 811;
    const rand = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };
    for (let row = 0; row < 16; row++) {
      const y = (row + 0.55) * (h / 16);
      const offset = (row % 2) * 0.5;
      for (let col = 0; col < 12; col++) {
        const x = (col + 0.5 + offset) * (w / 12) + (rand() - 0.5) * 8;
        const r = w * (0.018 + rand() * 0.013);
        ctx.lineWidth = 1.4;
        ctx.strokeStyle = "rgba(255,255,255,0.22)";
        ctx.beginPath();
        ctx.arc(x, y, r, 0.12 * Math.PI, 0.88 * Math.PI);
        ctx.stroke();
        ctx.strokeStyle = "rgba(0,0,0,0.24)";
        ctx.beginPath();
        ctx.arc(x, y + 1.5, r * 0.87, 0.18 * Math.PI, 0.82 * Math.PI);
        ctx.stroke();
      }
    }
  });
}

function makeFoamTexture() {
  return makeCanvasTexture(512, 256, (ctx, w, h) => {
    ctx.clearRect(0, 0, w, h);
    let seed = 913;
    const rand = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };
    const blob = (x, y, rx, ry, alpha) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, 1);
      g.addColorStop(0, `rgba(255, 249, 238, ${alpha})`);
      g.addColorStop(0.5, `rgba(255, 244, 226, ${alpha * 0.78})`);
      g.addColorStop(0.82, `rgba(255, 238, 218, ${alpha * 0.24})`);
      g.addColorStop(1, "rgba(255, 238, 218, 0)");
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(rx, ry);
      ctx.translate(-x, -y);
      ctx.fillStyle = g;
      ctx.fillRect(x - rx, y - ry, rx * 2, ry * 2);
      ctx.restore();
    };

    // Bright waterline froth around the hull.
    for (let i = 0; i < 110; i++) {
      const angle = rand() * TAU;
      const radial = Math.pow(rand(), 0.6);
      const x = w * (0.66 + Math.cos(angle) * radial * 0.22);
      const y = h * (0.5 + Math.sin(angle) * radial * 0.3);
      blob(x, y, 9 + rand() * 22, 5 + rand() * 15, 0.22 + rand() * 0.4);
    }

    // A long, feathery trail pulled out behind the tail.
    for (let i = 0; i < 115; i++) {
      const t = rand();
      const x = w * (0.04 + t * 0.58);
      const y = h * (0.5 + (rand() - 0.5) * (0.08 + t * 0.62));
      blob(x, y, 7 + rand() * 29, 2 + rand() * 8, 0.1 + rand() * 0.3);
    }

    // Sharp little lace holes and bright spray beads.
    for (let i = 0; i < 100; i++) {
      const t = rand();
      const x = w * (0.22 + t * 0.55);
      const y = h * (0.30 + rand() * 0.42);
      blob(x, y, 1.5 + rand() * 7, 1.2 + rand() * 5, 0.16 + rand() * 0.36);
    }
  });
}

/* -------------------------------------------------------------------------- */
/*  Palette & shared materials                                                */
/* -------------------------------------------------------------------------- */

const PALETTE = {
  skyTop: 0x192e4a,
  skyMid: 0x7b637d,
  horizon: 0xff9366,
  sun: 0xffe8b8,
  deepWater: 0x032b35,
  shallowWater: 0x0b606b,
  crestWater: 0x2ba499,
  foam: 0xf8ead6,
  cream: 0xf2e4cd,
  creamShadow: 0xd9c6ad,
  featherDark: 0x263b45,
  bill: 0xe77528,
  billLight: 0xf4ad51,
  pouch: 0xf2aa3f,
  shorts: 0x123d46,
  shortsLight: 0x2d6a6b,
  coral: 0xed7e59,
};

const MAT = {
  cream: new THREE.MeshStandardMaterial({
    color: PALETTE.cream,
    roughness: 0.82,
    metalness: 0,
  }),
  creamSoft: new THREE.MeshStandardMaterial({
    color: 0xf8eedb,
    roughness: 0.9,
    metalness: 0,
  }),
  bodyCream: new THREE.MeshStandardMaterial({
    color: 0xf2e4cd,
    roughness: 0.78,
    metalness: 0,
    sheen: 0.25,
    sheenColor: new THREE.Color(0xffe3bd),
  }),
  creamShadow: new THREE.MeshStandardMaterial({
    color: PALETTE.creamShadow,
    roughness: 0.92,
  }),
  feather: new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.76,
    metalness: 0,
    side: THREE.DoubleSide,
  }),
  bill: new THREE.MeshPhysicalMaterial({
    color: PALETTE.bill,
    roughness: 0.4,
    metalness: 0,
    clearcoat: 0.32,
    clearcoatRoughness: 0.52,
  }),
  billTip: new THREE.MeshStandardMaterial({
    color: 0xb94f2b,
    roughness: 0.43,
  }),
  pouch: new THREE.MeshPhysicalMaterial({
    color: PALETTE.pouch,
    roughness: 0.58,
    metalness: 0,
    sheen: 0.65,
    sheenColor: new THREE.Color(0xffd68a),
    sheenRoughness: 0.7,
  }),
  leg: new THREE.MeshStandardMaterial({
    color: 0xe9953e,
    roughness: 0.62,
  }),
  shorts: new THREE.MeshStandardMaterial({
    color: PALETTE.shorts,
    roughness: 0.78,
  }),
  shortsTrim: new THREE.MeshStandardMaterial({
    color: 0xebd6b5,
    roughness: 0.75,
  }),
  sunglasses: new THREE.MeshPhysicalMaterial({
    color: 0x0b2b2c,
    roughness: 0.065,
    metalness: 0.4,
    clearcoat: 1,
    clearcoatRoughness: 0.04,
  }),
  gold: new THREE.MeshStandardMaterial({
    color: 0xd9a554,
    roughness: 0.27,
    metalness: 0.72,
  }),
  board: new THREE.MeshPhysicalMaterial({
    color: PALETTE.coral,
    roughness: 0.38,
    metalness: 0.02,
    clearcoat: 0.72,
    clearcoatRoughness: 0.2,
  }),
  boardStripe: new THREE.MeshPhysicalMaterial({
    color: 0xf5e8cf,
    roughness: 0.44,
    clearcoat: 0.48,
    clearcoatRoughness: 0.3,
  }),
  boardDark: new THREE.MeshStandardMaterial({
    color: 0x113e48,
    roughness: 0.42,
    metalness: 0.12,
  }),
  coral: new THREE.MeshStandardMaterial({
    color: PALETTE.coral,
    roughness: 0.7,
  }),
  flower: new THREE.MeshStandardMaterial({
    color: 0xf19a83,
    roughness: 0.7,
    side: THREE.DoubleSide,
  }),
  flowerLight: new THREE.MeshStandardMaterial({
    color: 0xffd4bd,
    roughness: 0.7,
    side: THREE.DoubleSide,
  }),
  flowerCenter: new THREE.MeshStandardMaterial({
    color: 0xf4c85f,
    roughness: 0.7,
  }),
};

// A whisper of feather texture on the cream body.
const featherBump = makeFeatherBumpTexture();
featherBump.wrapS = THREE.RepeatWrapping;
featherBump.wrapT = THREE.RepeatWrapping;
featherBump.repeat.set(2.2, 1.7);
MAT.bodyCream.bumpMap = featherBump;
MAT.bodyCream.bumpScale = 0.012;

/* -------------------------------------------------------------------------- */
/*  Sky                                                                       */
/* -------------------------------------------------------------------------- */

const SUN_DIRECTION = new THREE.Vector3(-0.68, 0.085, -0.73).normalize();

const skyMaterial = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  depthWrite: false,
  fog: false,
  uniforms: {
    uSunDirection: { value: SUN_DIRECTION.clone() },
    uTop: { value: new THREE.Color(PALETTE.skyTop) },
    uMid: { value: new THREE.Color(PALETTE.skyMid) },
    uHorizon: { value: new THREE.Color(PALETTE.horizon) },
    uSun: { value: new THREE.Color(PALETTE.sun) },
    uTime: { value: 0 },
  },
  vertexShader: /* glsl */ `
    varying vec3 vDirection;
    void main() {
      vDirection = normalize(position);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform vec3 uSunDirection;
    uniform vec3 uTop;
    uniform vec3 uMid;
    uniform vec3 uHorizon;
    uniform vec3 uSun;
    uniform float uTime;
    varying vec3 vDirection;

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
        p = p * 2.03 + 11.1;
        a *= 0.5;
      }
      return v;
    }

    void main() {
      vec3 dir = normalize(vDirection);
      float y = dir.y;
      float sunDot = max(dot(dir, normalize(uSunDirection)), 0.0);

      float upT = smoothstep(-0.02, 0.78, y);
      vec3 color = mix(uHorizon, uMid, smoothstep(0.0, 0.16, upT));
      color = mix(color, uTop, smoothstep(0.16, 0.9, upT));
      // A thin ember band just above the sea line.
      vec3 ember = vec3(1.0, 0.49, 0.31);
      color = mix(color, ember, exp(-abs(y - 0.035) * 30.0) * 0.18);

      // A soft, dusty violet belt opposite the sunset.
      float antiSun = smoothstep(0.2, 0.9, -dot(normalize(vec3(uSunDirection.x, 0.0, uSunDirection.z)), normalize(vec3(dir.x, 0.001, dir.z))));
      color = mix(color, vec3(0.42, 0.42, 0.52), antiSun * 0.16 * smoothstep(0.05, 0.45, y));

      // Warm atmospheric bloom around the low sun.
      float glow = pow(sunDot, 22.0) * 0.12 + pow(sunDot, 90.0) * 0.32 + pow(sunDot, 420.0) * 0.8;
      color += uSun * glow;
      color += vec3(0.20, 0.08, 0.035) * pow(sunDot, 3.0) * 0.35;

      // The sun itself, with a little organic irregularity.
      float disk = smoothstep(0.99972, 0.99991, sunDot);
      float rim = smoothstep(0.99935, 0.99972, sunDot) * 0.22;
      color = mix(color, uSun * 1.35, disk);
      color += vec3(1.0, 0.77, 0.48) * rim;

      // High, painterly cirrus streaks.
      vec2 sphereUv = vec2(atan(dir.z, dir.x) * 1.65, dir.y * 4.0);
      float streakNoise = fbm(vec2(sphereUv.x * 0.75 + uTime * 0.002, sphereUv.y * 2.3));
      float streaks = smoothstep(0.59, 0.76, streakNoise) *
        smoothstep(0.035, 0.21, y) * (1.0 - smoothstep(0.52, 0.82, y));
      vec3 cloudTint = mix(vec3(0.87, 0.61, 0.58), vec3(0.98, 0.82, 0.68), pow(sunDot, 1.8));
      color = mix(color, cloudTint, streaks * 0.18);

      // Fine dithering keeps the enormous gradient from banding.
      float dither = hash(gl_FragCoord.xy) / 255.0 - 0.5 / 255.0;
      color += dither;

      gl_FragColor = vec4(color, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const sky = new THREE.Mesh(new THREE.SphereGeometry(240, 48, 32), skyMaterial);
sky.renderOrder = -100;
scene.add(sky);

// Sun halo sprite — adds a soft, photographic core above the horizon.
const glowTexture = makeGlowTexture(256);
const sunGlow = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: glowTexture,
    color: 0xffb96f,
    transparent: true,
    opacity: 0.34,
    depthWrite: false,
    depthTest: false,
    blending: THREE.AdditiveBlending,
    fog: false,
  })
);
sunGlow.position.copy(SUN_DIRECTION).multiplyScalar(185);
sunGlow.scale.set(6.5, 6.5, 1);
sunGlow.renderOrder = -50;
scene.add(sunGlow);

// Wispy, layered cloud sprites — painterly rather than photographic.
const cloudSprites = [];
for (let i = 0; i < 5; i++) {
  const texture = makeCloudTexture(i + 2);
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: texture,
      color: i % 2 ? 0xd8a69c : 0xf1b8a4,
      transparent: true,
      opacity: 0.10 + i * 0.018,
      depthWrite: false,
      fog: false,
      blending: THREE.NormalBlending,
    })
  );
  const positions = [
    [-42, 26, -105, 62, 22],
    [36, 34, -120, 72, 25],
    [-8, 17, -130, 90, 20],
    [76, 23, -95, 54, 16],
    [-88, 40, -80, 45, 16],
  ];
  const p = positions[i];
  sprite.position.set(p[0], p[1], p[2]);
  sprite.scale.set(p[3], p[4], 1);
  sprite.material.rotation = (i - 2) * 0.025;
  scene.add(sprite);
  cloudSprites.push(sprite);
}

/* -------------------------------------------------------------------------- */
/*  Lighting                                                                  */
/* -------------------------------------------------------------------------- */

const hemi = new THREE.HemisphereLight(0xffc8a4, 0x052e37, 0.5);
scene.add(hemi);

const sunLight = new THREE.DirectionalLight(0xffa25d, 4.1);
sunLight.position.copy(SUN_DIRECTION).multiplyScalar(28);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.near = 4;
sunLight.shadow.camera.far = 55;
sunLight.shadow.camera.left = -6;
sunLight.shadow.camera.right = 6;
sunLight.shadow.camera.top = 7;
sunLight.shadow.camera.bottom = -2;
sunLight.shadow.bias = -0.0003;
sunLight.shadow.normalBias = 0.02;
scene.add(sunLight);

const frontFill = new THREE.DirectionalLight(0xffe3cd, 0.72);
frontFill.position.set(6, 7, 9);
scene.add(frontFill);

const coolFill = new THREE.DirectionalLight(0x6bafc9, 0.4);
coolFill.position.set(-5, 4, 7);
scene.add(coolFill);

const bounce = new THREE.PointLight(0x3bb1b5, 3.0, 10, 2);
bounce.position.set(0.2, 0.2, 2.2);
scene.add(bounce);

// A hot rim from behind separates the bird from the huge backlit swell.
const rimLight = new THREE.DirectionalLight(0xff7c46, 2.5);
rimLight.position.set(-5.5, 4.4, -4.5);
scene.add(rimLight);

/* -------------------------------------------------------------------------- */
/*  Ocean                                                                     */
/* -------------------------------------------------------------------------- */

const waterGeometry = new THREE.PlaneGeometry(340, 280, 320, 260);
waterGeometry.rotateX(-Math.PI / 2);

const waterUniforms = {
  uTime: { value: 0 },
  uSunDirection: { value: SUN_DIRECTION.clone() },
  uOrigin: { value: new THREE.Vector2(0, -38) },
  uBoardPosition: { value: new THREE.Vector2(0.1, 0.8) },
  uDeep: { value: new THREE.Color(PALETTE.deepWater) },
  uShallow: { value: new THREE.Color(PALETTE.shallowWater) },
  uCrest: { value: new THREE.Color(PALETTE.crestWater) },
  uFoam: { value: new THREE.Color(PALETTE.foam) },
  uHorizon: { value: new THREE.Color(PALETTE.horizon) },
  uSky: { value: new THREE.Color(PALETTE.skyMid) },
  uSun: { value: new THREE.Color(0xffd29c) },
};

const waterMaterial = new THREE.ShaderMaterial({
  uniforms: waterUniforms,
  vertexShader: /* glsl */ `
    uniform float uTime;
    uniform vec2 uOrigin;
    uniform vec2 uBoardPosition;
    varying vec3 vWorldPosition;
    varying vec3 vNormal;
    varying float vHeight;
    varying float vHero;

    float boardSwell(vec2 p) {
      vec2 d = p - uBoardPosition;
      d.x *= 0.9;
      d.y *= 1.55;
      return 0.2 * exp(-dot(d, d) * 0.52);
    }

    float heroWave(vec2 p) {
      float across = exp(-pow((p.y + 8.0 + 1.6 * sin(p.x * 0.12 + uTime * 0.08)) / 5.4, 2.0));
      return across * 0.38;
    }

    float backSwell(vec2 p) {
      float across = exp(-pow((p.y + 19.0 + 2.5 * sin(p.x * 0.07 + 0.8)) / 6.5, 2.0));
      return across * (0.4 + 0.2 * sin(p.x * 0.12 + 2.0)) * 0.55;
    }

    float rollingSwell(vec2 p) {
      float s1 = exp(-pow((p.y + 5.8 + 1.4 * sin(p.x * 0.1 + uTime * 0.08)) / 3.7, 2.0)) * 0.74;
      float s2 = exp(-pow((p.y + 15.5 + 2.0 * sin(p.x * 0.06 - uTime * 0.05)) / 5.8, 2.0)) * 0.9;
      return s1 + s2;
    }

    float waveHeight(vec2 p) {
      float h = 0.0;
      h += sin(p.x * 0.23 + p.y * 0.14 + uTime * 0.63) * 0.14;
      h += sin(p.x * 0.42 - p.y * 0.30 - uTime * 0.92) * 0.075;
      h += sin(p.x * 0.83 + p.y * 0.22 + uTime * 1.35) * 0.030;
      h += sin(p.x * 0.30 - p.y * 0.63 + uTime * 0.47) * 0.045;
      h += heroWave(p);
      h += backSwell(p);
      float faceMask = smoothstep(0.35, 1.2, heroWave(p));
      h += sin(p.x * 0.92 + p.y * 0.42 + uTime * 1.2) * 0.045 * faceMask;
      h += sin(p.x * 1.55 - p.y * 0.71 - uTime * 1.8) * 0.022 * faceMask;
      h += rollingSwell(p);
      h += boardSwell(p);
      return h;
    }

    void main() {
      vec2 p = position.xz + uOrigin;
      float h = waveHeight(p);
      float eps = 0.28;
      float hx = waveHeight(p + vec2(eps, 0.0));
      float hz = waveHeight(p + vec2(0.0, eps));
      vec3 n = normalize(vec3(-(hx - h) / eps, 1.0, -(hz - h) / eps));

      vec3 displaced = vec3(position.x, h, position.z);
      vec4 worldPos = modelMatrix * vec4(displaced, 1.0);
      vWorldPosition = worldPos.xyz;
      vNormal = normalize(mat3(modelMatrix) * n);
      vHeight = h;
      vHero = heroWave(p);
      gl_Position = projectionMatrix * viewMatrix * worldPos;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform float uTime;
    uniform vec2 uBoardPosition;
    uniform vec3 uSunDirection;
    uniform vec3 uDeep;
    uniform vec3 uShallow;
    uniform vec3 uCrest;
    uniform vec3 uFoam;
    uniform vec3 uHorizon;
    uniform vec3 uSky;
    uniform vec3 uSun;
    varying vec3 vWorldPosition;
    varying vec3 vNormal;
    varying float vHeight;
    varying float vHero;

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
      for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p = p * 2.02 + vec2(9.7, 3.1);
        a *= 0.5;
      }
      return v;
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(cameraPosition - vWorldPosition);
      vec3 L = normalize(uSunDirection);

      float fresnel = pow(1.0 - max(dot(N, V), 0.0), 4.0);
      float heightTone = smoothstep(-0.45, 2.5, vHeight);
      float crestTone = smoothstep(0.8, 2.55, vHeight + vHero * 0.2);

      vec3 water = mix(uDeep, uShallow, 0.28 + heightTone * 0.56);
      water = mix(water, uCrest, crestTone * 0.60 + fresnel * 0.06);

      vec3 reflected = reflect(-V, N);
      float skyT = smoothstep(-0.03, 0.5, reflected.y);
      vec3 skyReflection = mix(uHorizon, uSky, skyT);
      water = mix(water, skyReflection, 0.06 + fresnel * 0.33);

      float diffuse = max(dot(N, L), 0.0);
      water += uSun * diffuse * 0.055;

      float sunSpec = pow(max(dot(reflect(-L, N), V), 0.0), 220.0);
      float sunBroad = pow(max(dot(reflect(-L, N), V), 0.0), 20.0);
      water += uSun * (sunSpec * 2.3 + sunBroad * 0.11);


      // The long, warm path of light under the sun.
      vec2 toSun = normalize(-uSunDirection.xz);
      vec2 relSun = vWorldPosition.xz * vec2(0.12, 0.28);
      float lightPath = exp(-abs(relSun.x - toSun.x * 1.0) * 2.8);
      water += uSun * lightPath * (0.022 + sunBroad * 0.35);

      // Subtle whitecaps catch on the two long swells behind the surfer.
      float crest1 = exp(-pow((vWorldPosition.z + 5.8 + 1.4 * sin(vWorldPosition.x * 0.1 + uTime * 0.08)) / 0.75, 2.0));
      float crest2 = exp(-pow((vWorldPosition.z + 15.5 + 2.0 * sin(vWorldPosition.x * 0.06 - uTime * 0.05)) / 1.25, 2.0));
      float capNoise = fbm(vWorldPosition.xz * vec2(2.2, 0.75) + vec2(uTime * 0.1, 0.0));
      float distantFoam = (crest1 * 0.44 + crest2 * 0.16) * smoothstep(0.56, 0.76, capNoise);
      water = mix(water, uFoam, clamp(distantFoam, 0.0, 0.41));

      // A tight collar of whitewater around the board, plus the beginnings of a wake.
      vec2 relBoard = vWorldPosition.xz - uBoardPosition;
      vec2 tightBoard = relBoard * vec2(0.95, 1.75);
      float boardCore = exp(-dot(tightBoard, tightBoard) * 0.74);
      float wakeTrail = exp(-length((relBoard + vec2(1.95, 0.08)) * vec2(0.44, 1.7)) * 1.35);
      float churnNoise = fbm(vWorldPosition.xz * 3.1 + vec2(-uTime * 0.32, uTime * 0.16));
      float foamMask = (boardCore * 0.56 + wakeTrail * 0.36) * smoothstep(0.34, 0.72, churnNoise);
      water = mix(water, uFoam, clamp(foamMask, 0.0, 0.72));
      water = mix(water, uCrest, boardCore * 0.22);

      // A warm, misty horizon dissolves the water into the sky.
      float dist = length(vWorldPosition.xz - cameraPosition.xz);
      float haze = 1.0 - exp(-pow(max(dist - 26.0, 0.0) * 0.0062, 2.0));
      water = mix(water, uHorizon, clamp(haze, 0.0, 0.96));
      water = mix(water, uDeep * 1.18, smoothstep(24.0, 5.0, dist) * 0.20);

      float dither = hash(gl_FragCoord.xy) / 255.0 - 0.5 / 255.0;
      water += dither;

      gl_FragColor = vec4(water, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const water = new THREE.Mesh(waterGeometry, waterMaterial);
water.position.z = -38;
water.frustumCulled = false;
scene.add(water);

// Matching height field on the CPU, used to keep the board planted in the ocean.
function heroWaveAt(x, z, t) {
  const across = Math.exp(-Math.pow((z + 8 + 1.6 * Math.sin(x * 0.12 + t * 0.08)) / 5.4, 2));
  return across * 0.38;
}

function waveHeightAt(x, z, t) {
  let h = 0;
  h += Math.sin(x * 0.23 + z * 0.14 + t * 0.63) * 0.14;
  h += Math.sin(x * 0.42 - z * 0.30 - t * 0.92) * 0.075;
  h += Math.sin(x * 0.83 + z * 0.22 + t * 1.35) * 0.03;
  h += Math.sin(x * 0.30 - z * 0.63 + t * 0.47) * 0.045;
  h += heroWaveAt(x, z, t);
  const back = Math.exp(-Math.pow((z + 19 + 2.5 * Math.sin(x * 0.07 + 0.8)) / 6.5, 2));
  h += back * (0.4 + 0.2 * Math.sin(x * 0.12 + 2.0)) * 0.55;
  const s1 = Math.exp(-Math.pow((z + 5.8 + 1.4 * Math.sin(x * 0.1 + t * 0.08)) / 3.7, 2)) * 0.74;
  const s2 = Math.exp(-Math.pow((z + 15.5 + 2.0 * Math.sin(x * 0.06 - t * 0.05)) / 5.8, 2)) * 0.9;
  h += s1 + s2;
  return h;
}

/* -------------------------------------------------------------------------- */
/*  Surfboard                                                                 */
/* -------------------------------------------------------------------------- */

function makeSurfboardShape() {
  const s = new THREE.Shape();
  s.moveTo(1.92, 0);
  s.bezierCurveTo(1.48, 0.24, 0.96, 0.38, 0.24, 0.405);
  s.bezierCurveTo(-0.72, 0.42, -1.52, 0.29, -1.75, 0.0);
  s.bezierCurveTo(-1.52, -0.29, -0.72, -0.42, 0.24, -0.405);
  s.bezierCurveTo(0.96, -0.38, 1.48, -0.24, 1.92, 0);
  return s;
}

function makeDeckStripeShape() {
  const s = new THREE.Shape();
  s.moveTo(-1.5, 0.0);
  s.bezierCurveTo(-0.9, 0.12, -0.1, 0.15, 0.9, 0.11);
  s.bezierCurveTo(1.28, 0.085, 1.58, 0.055, 1.78, 0.0);
  s.bezierCurveTo(1.58, -0.055, 1.28, -0.085, 0.9, -0.11);
  s.bezierCurveTo(-0.1, -0.15, -0.9, -0.12, -1.5, 0.0);
  return s;
}

function extrudeFlatShape(shape, depth, bevel, curveSegments = 40) {
  return new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: bevel > 0,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 3,
    curveSegments,
    steps: 1,
  });
}

const surfer = new THREE.Group();
surfer.position.set(0.1, 0.56, 0.9);
const SURFER_BASE = surfer.position.clone();
surfer.rotation.y = -0.06;
scene.add(surfer);

const boardGroup = new THREE.Group();
surfer.add(boardGroup);

const boardBody = new THREE.Group();
boardGroup.add(boardBody);

const boardGeometry = extrudeFlatShape(makeSurfboardShape(), 0.105, 0.035, 52);
boardGeometry.rotateX(-Math.PI / 2);
boardGeometry.translate(0, 0.11, 0);

// Give the deck a gentle rocker and upturned nose.
{
  const pos = boardGeometry.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    if (y > 0.1) {
      pos.setY(i, y + Math.pow(Math.max(0, x), 2) * 0.018);
    }
  }
  boardGeometry.computeVertexNormals();
}

const board = new THREE.Mesh(boardGeometry, MAT.board);
board.castShadow = true;
board.receiveShadow = true;
boardBody.add(board);

const deckStripe = new THREE.Mesh(extrudeFlatShape(makeDeckStripeShape(), 0.008, 0.006, 42), MAT.boardStripe);
deckStripe.geometry.rotateX(-Math.PI / 2);
deckStripe.geometry.translate(0, 0.165, 0);
deckStripe.castShadow = false;
deckStripe.receiveShadow = true;
boardBody.add(deckStripe);

// Thin inset pinlines.
for (const sign of [-1, 1]) {
  const line = new THREE.Mesh(
    new THREE.BoxGeometry(2.35, 0.007, 0.018),
    MAT.boardDark
  );
  line.position.set(0.39, 0.181, sign * 0.175);
  line.rotation.x = sign * 0.015;
  boardBody.add(line);
}

// A cream rail stringer catches the low light along the board's edge.
for (const sign of [-1, 1]) {
  const railPoints = [
    new THREE.Vector3(-1.66, 0.16, sign * 0.20),
    new THREE.Vector3(-1.15, 0.16, sign * 0.34),
    new THREE.Vector3(-0.28, 0.16, sign * 0.43),
    new THREE.Vector3(0.66, 0.17, sign * 0.42),
    new THREE.Vector3(1.4, 0.17, sign * 0.31),
    new THREE.Vector3(1.86, 0.18, sign * 0.06),
  ];
  const rail = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(railPoints), 40, 0.013, 5, false),
    MAT.boardStripe
  );
  boardBody.add(rail);
}

// Retro sun badge, built from simple solids so it has real depth.
const badge = new THREE.Group();
badge.position.set(1.18, 0.183, 0.0);
badge.rotation.x = -Math.PI / 2;
boardBody.add(badge);

const badgeDisc = new THREE.Mesh(new THREE.CircleGeometry(0.145, 32), MAT.boardDark);
badge.add(badgeDisc);

const badgeInner = new THREE.Mesh(new THREE.CircleGeometry(0.095, 32), MAT.boardStripe);
badgeInner.position.z = 0.002;
badge.add(badgeInner);

for (let i = 0; i < 8; i++) {
  const ray = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.045, 0.004), MAT.boardDark);
  ray.position.z = 0.003;
  ray.position.x = Math.cos((i / 8) * TAU) * 0.116;
  ray.position.y = Math.sin((i / 8) * TAU) * 0.116;
  ray.rotation.z = (i / 8) * TAU + Math.PI / 2;
  badge.add(ray);
}

// A dark tail pad to catch the deck light and give the stance some grip.
{
  const padShape = new THREE.Shape();
  const padW = 0.28;
  const padL = 0.27;
  padShape.moveTo(-padL, -padW * 0.4);
  padShape.quadraticCurveTo(-padL, -padW, -padL * 0.5, -padW);
  padShape.lineTo(padL * 0.6, -padW * 0.86);
  padShape.quadraticCurveTo(padL, -padW * 0.7, padL, -padW * 0.2);
  padShape.lineTo(padL, padW * 0.2);
  padShape.quadraticCurveTo(padL, padW * 0.7, padL * 0.6, padW * 0.86);
  padShape.lineTo(-padL * 0.5, padW);
  padShape.quadraticCurveTo(-padL, padW, -padL, padW * 0.4);
  const padGeo = extrudeFlatShape(padShape, 0.018, 0.008, 12);
  padGeo.rotateX(-Math.PI / 2);
  padGeo.translate(-0.72, 0.245, 0);
  const pad = new THREE.Mesh(padGeo, MAT.boardDark);
  pad.castShadow = false;
  pad.receiveShadow = true;
  boardBody.add(pad);

  for (let i = 0; i < 4; i++) {
    const groove = new THREE.Mesh(new THREE.BoxGeometry(0.014, 0.008, 0.34), MAT.boardDark);
    groove.position.set(-0.94 + i * 0.14, 0.272, 0);
    groove.rotation.y = 0.04;
    boardBody.add(groove);
  }
}

// Leash plug and a little curling leash.
const leashCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-1.58, 0.14, 0.17),
  new THREE.Vector3(-1.78, 0.03, 0.4),
  new THREE.Vector3(-1.62, -0.03, 0.63),
  new THREE.Vector3(-1.17, 0.00, 0.72),
]);
const leash = new THREE.Mesh(
  new THREE.TubeGeometry(leashCurve, 24, 0.012, 5, false),
  new THREE.MeshStandardMaterial({ color: 0xf0cf9c, roughness: 0.8 })
);
boardBody.add(leash);

// A painted foam wake follows the board, anchoring it to the sea surface.
const wakeFoamTexture = makeFoamTexture();
const wakeFoamGeometry = new THREE.PlaneGeometry(7.0, 3.8);
wakeFoamGeometry.rotateX(-Math.PI / 2);
const wakeFoam = new THREE.Mesh(
  wakeFoamGeometry,
  new THREE.MeshBasicMaterial({
    map: wakeFoamTexture,
    color: 0xfff4e7,
    transparent: true,
    opacity: 0.8,
    depthWrite: false,
    side: THREE.DoubleSide,
  })
);
wakeFoam.renderOrder = 2;
wakeFoam.frustumCulled = false;
scene.add(wakeFoam);

// A soft contact shadow under the bird's feet.
const contactShadow = new THREE.Mesh(
  new THREE.CircleGeometry(0.62, 32),
  new THREE.MeshBasicMaterial({
    color: 0x173d43,
    transparent: true,
    opacity: 0.2,
    depthWrite: false,
  })
);
contactShadow.rotation.x = -Math.PI / 2;
contactShadow.scale.set(1.35, 0.72, 1);
contactShadow.position.set(-0.04, 0.193, 0.03);
boardBody.add(contactShadow);

/* -------------------------------------------------------------------------- */
/*  Pelican anatomy                                                           */
/* -------------------------------------------------------------------------- */

const pelican = new THREE.Group();
pelican.position.set(-0.02, 0.2, 0.0);
pelican.rotation.y = 0.08;
boardGroup.add(pelican);

const torso = new THREE.Group();
pelican.add(torso);

const body = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 36), MAT.bodyCream);
body.scale.set(0.52, 0.73, 0.43);
body.position.set(0, 1.27, 0.0);
body.rotation.z = -0.035;
body.castShadow = true;
body.receiveShadow = true;
torso.add(body);

// A soft mantle of little shoulder feathers, more feather than six-pack.
for (const sign of [-1, 1]) {
  for (let i = 0; i < 3; i++) {
    const feather = new THREE.Mesh(
      makeFeatherGeometry(0.18 + i * 0.03, 0.11, 0.018, 0.9),
      MAT.creamSoft
    );
    feather.position.set(sign * (0.32 + i * 0.07), 1.46 - i * 0.08, 0.25 - i * 0.04);
    feather.rotation.set(-0.22, sign * -0.5, Math.PI * 0.5 + sign * 0.35 + i * 0.15);
    feather.castShadow = false;
    torso.add(feather);
  }
}

// Board shorts.
const shortsGroup = new THREE.Group();
shortsGroup.position.y = 0.73;
torso.add(shortsGroup);

const shorts = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20, 0, TAU, 0, Math.PI * 0.58), MAT.shorts);
shorts.scale.set(0.52, 0.51, 0.45);
shorts.rotation.x = Math.PI;
shorts.position.y = 0.12;
shorts.castShadow = true;
shorts.receiveShadow = true;
shortsGroup.add(shorts);

const waistband = new THREE.Mesh(new THREE.TorusGeometry(0.465, 0.048, 8, 36), MAT.shortsTrim);
waistband.rotation.x = Math.PI / 2;
waistband.scale.z = 0.86;
waistband.position.y = 0.38;
waistband.castShadow = true;
shortsGroup.add(waistband);

const drawstringKnot = new THREE.Mesh(new THREE.SphereGeometry(0.04, 12, 8), MAT.shortsTrim);
drawstringKnot.position.set(-0.12, 0.26, 0.42);
shortsGroup.add(drawstringKnot);
for (const dir of [-1, 1]) {
  const string = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.18, 6), MAT.shortsTrim);
  string.position.set(-0.12 + dir * 0.035, 0.16, 0.425);
  string.rotation.z = dir * 0.22;
  shortsGroup.add(string);
}

// A cream racing panel down the side of the shorts.
for (const sign of [-1, 1]) {
  const panel = new THREE.Mesh(new THREE.PlaneGeometry(0.07, 0.26), MAT.shortsTrim);
  panel.position.set(sign * 0.46, 0.12, 0.02);
  panel.rotation.y = sign * Math.PI / 2;
  panel.rotation.z = 0.02;
  shortsGroup.add(panel);
}

// A cream side seam gives the shorts a tailored, retro shape.
for (const sign of [-1, 1]) {
  const seamPoints = [
    new THREE.Vector3(sign * 0.34, 0.34, 0.27),
    new THREE.Vector3(sign * 0.44, 0.17, 0.22),
    new THREE.Vector3(sign * 0.42, 0.0, 0.16),
    new THREE.Vector3(sign * 0.29, -0.11, 0.23),
  ];
  const seam = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(seamPoints), 16, 0.012, 5, false),
    MAT.shortsTrim
  );
  seam.castShadow = true;
  shortsGroup.add(seam);
}

// Little leg cuffs.
for (const x of [-0.21, 0.21]) {
  const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.17, 0.12, 20, 1, true), MAT.shortsTrim);
  cuff.position.set(x, -0.12, 0.02);
  cuff.scale.z = 0.88;
  cuff.rotation.z = x * 0.35;
  cuffsShadow(cuff);
  shortsGroup.add(cuff);
}

function cuffsShadow(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
}

// Orange legs, with webbed feet planted in a surfer's stance.
function makeLeg(x, z, footZ, thighAngle, shinAngle) {
  const legGroup = new THREE.Group();
  legGroup.position.set(x, 0.82, z);

  const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.072, 0.06, 0.4, 12), MAT.leg);
  thigh.position.set(0, -0.19, 0);
  thigh.rotation.z = thighAngle;
  thigh.castShadow = true;
  legGroup.add(thigh);

  const knee = new THREE.Mesh(new THREE.SphereGeometry(0.067, 16, 10), MAT.leg);
  knee.position.set(Math.sin(thighAngle) * 0.35, -0.37, 0);
  knee.castShadow = true;
  legGroup.add(knee);

  const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.056, 0.048, 0.38, 12), MAT.leg);
  shin.position.set(Math.sin(thighAngle) * 0.36 + Math.sin(shinAngle) * 0.15, -0.55, footZ * 0.3);
  shin.rotation.z = shinAngle;
  shin.rotation.x = -0.08;
  shin.castShadow = true;
  legGroup.add(shin);

  const foot = makeWebbedFoot();
  foot.position.set(Math.sin(thighAngle) * 0.36 + Math.sin(shinAngle) * 0.25, -0.735, footZ * 0.6);
  foot.rotation.y = 0.04;
  legGroup.add(foot);

  torso.add(legGroup);
  return legGroup;
}

function makeWebbedFoot() {
  const g = new THREE.Group();
  const pad = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 14), MAT.leg);
  pad.scale.set(0.145, 0.052, 0.22);
  pad.position.z = 0.08;
  pad.castShadow = true;
  g.add(pad);

  for (let i = -1; i <= 1; i++) {
    const toe = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), MAT.leg);
    toe.scale.set(0.067, 0.035, 0.19);
    toe.position.set(i * 0.085, -0.004, 0.25 + (i === 0 ? 0.035 : 0));
    toe.rotation.y = i * 0.23;
    toe.castShadow = true;
    g.add(toe);
  }

  for (const sign of [-1, 1]) {
    const web = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 0.18), MAT.leg);
    web.rotation.x = -Math.PI / 2;
    web.rotation.z = sign * 0.27;
    web.position.set(sign * 0.077, -0.025, 0.155);
    g.add(web);
  }

  return g;
}

makeLeg(-0.26, 0.05, 0.31, 0.22, -0.16);
makeLeg(0.26, 0.03, -0.27, -0.2, 0.17);

// Neck.
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0.01, 1.66, 0.04),
  new THREE.Vector3(0.02, 1.9, 0.08),
  new THREE.Vector3(-0.015, 2.16, 0.15),
  new THREE.Vector3(0.0, 2.36, 0.21),
]);
const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 28, 0.19, 14, false), MAT.cream);
neck.castShadow = true;
torso.add(neck);

// Ruffled feather collar where neck meets chest.
for (let i = 0; i < 7; i++) {
  const a = -1.1 + (i / 6) * 2.2;
  const ruffle = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 8), MAT.creamSoft);
  ruffle.scale.set(0.12, 0.22, 0.06);
  ruffle.position.set(Math.sin(a) * 0.29, 1.56 + Math.cos(a) * 0.04, Math.cos(a) * 0.17 + 0.12);
  ruffle.rotation.z = -a * 0.55;
  ruffle.castShadow = false;
  torso.add(ruffle);
}

// Head group.
const headGroup = new THREE.Group();
headGroup.position.set(0.01, 2.5, 0.3);
headGroup.rotation.y = 1.32;
headGroup.rotation.x = -0.02;
headGroup.rotation.z = -0.035;
torso.add(headGroup);

const head = new THREE.Mesh(new THREE.SphereGeometry(0.42, 40, 28), MAT.bodyCream);
head.scale.set(1.0, 1.05, 1.02);
head.castShadow = true;
head.receiveShadow = true;
headGroup.add(head);

// Back-of-head feather tuft.
const crestFeathers = [];
for (let i = 0; i < 4; i++) {
  const crest = new THREE.Mesh(
    makeFeatherGeometry(0.44 + i * 0.04, 0.17, 0.018, 0.7),
    MAT.feather
  );
  crest.position.set(-0.04 + i * 0.035, 0.05, -0.25 + i * 0.02);
  crest.rotation.z = Math.PI - 0.5 + i * 0.12;
  crest.rotation.y = 0.1 - i * 0.06;
  crest.rotation.x = -0.2 + i * 0.02;
  crest.castShadow = true;
  headGroup.add(crest);
  crestFeathers.push(crest);
}

/* ------------------------------ bill & pouch ------------------------------ */

function makeLoftGeometry(sections, radialSegments = 12) {
  const positions = [];
  const indices = [];

  for (let i = 0; i < sections.length; i++) {
    const s = sections[i];
    for (let j = 0; j <= radialSegments; j++) {
      const a = (j / radialSegments) * TAU;
      const cx = Math.cos(a) * s.rx;
      const cy = Math.sin(a) * s.ry;
      positions.push(cx + (s.x || 0), cy + s.y, s.z);
    }
  }

  for (let i = 0; i < sections.length - 1; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const a = i * (radialSegments + 1) + j;
      const b = a + 1;
      const c = a + radialSegments + 1;
      const d = c + 1;
      indices.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}

const upperBill = new THREE.Mesh(
  makeLoftGeometry([
    { x: 0, y: 0.0, z: 0.0, rx: 0.17, ry: 0.11 },
    { x: 0, y: 0.01, z: 0.2, rx: 0.23, ry: 0.105 },
    { x: 0, y: -0.005, z: 0.48, rx: 0.245, ry: 0.09 },
    { x: 0, y: -0.055, z: 0.78, rx: 0.215, ry: 0.072 },
    { x: 0, y: -0.13, z: 1.02, rx: 0.16, ry: 0.05 },
    { x: 0, y: -0.205, z: 1.14, rx: 0.075, ry: 0.028 },
  ], 16),
  MAT.bill
);
upperBill.position.set(0.0, -0.02, 0.3);
upperBill.rotation.x = 0.015;
upperBill.castShadow = true;
headGroup.add(upperBill);

// Dark, hooked beak tip.
const beakHook = new THREE.Mesh(new THREE.SphereGeometry(0.085, 18, 12), MAT.billTip);
beakHook.scale.set(0.7, 0.75, 1.15);
beakHook.position.set(0, -0.205, 1.42);
beakHook.castShadow = true;
headGroup.add(beakHook);

// The famous fish net: a big, luminous throat pouch.
const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 36, 24), MAT.pouch);
pouch.scale.set(0.225, 0.22, 0.5);
pouch.position.set(0, -0.43, 0.86);
pouch.rotation.x = 0.14;
pouch.castShadow = true;
pouch.receiveShadow = true;
headGroup.add(pouch);

const pouchRim = new THREE.Mesh(
  new THREE.TubeGeometry(
    new THREE.CatmullRomCurve3([
      new THREE.Vector3(-0.22, -0.12, 0.37),
      new THREE.Vector3(-0.12, -0.25, 0.14),
      new THREE.Vector3(0, -0.275, 0.08),
      new THREE.Vector3(0.12, -0.25, 0.14),
      new THREE.Vector3(0.22, -0.12, 0.37),
    ]),
    30,
    0.022,
    7,
    false
  ),
  MAT.billTip
);
pouchRim.castShadow = true;
headGroup.add(pouchRim);

// The lower mandible rim follows the swell of the pouch to the beak tip.
for (const sign of [-1, 1]) {
  const sideRim = new THREE.Mesh(
    new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3([
        new THREE.Vector3(sign * 0.185, -0.1, 0.36),
        new THREE.Vector3(sign * 0.225, -0.26, 0.62),
        new THREE.Vector3(sign * 0.17, -0.35, 0.92),
        new THREE.Vector3(sign * 0.055, -0.32, 1.2),
      ]),
      28,
      0.017,
      6,
      false
    ),
    MAT.billTip
  );
  sideRim.castShadow = true;
  headGroup.add(sideRim);
}

// Two tiny nostril dashes on the upper mandible.
for (const sign of [-1, 1]) {
  const nostril = new THREE.Mesh(new THREE.CapsuleGeometry(0.008, 0.05, 3, 6), MAT.billTip);
  nostril.rotation.x = Math.PI / 2;
  nostril.rotation.z = sign * 0.16;
  nostril.position.set(sign * 0.1, 0.065, 0.47);
  headGroup.add(nostril);
}

/* ------------------------------ sunglasses -------------------------------- */

const shades = new THREE.Group();
shades.position.set(0, 0.13, 0.455);
const shadeTilt = new THREE.Group();
shadeTilt.rotation.x = 0.06;
shades.add(shadeTilt);

for (const sign of [-1, 1]) {
  const lens = new THREE.Mesh(new THREE.SphereGeometry(0.142, 28, 18), MAT.sunglasses);
  lens.scale.set(1.1, 0.88, 0.19);
  lens.position.set(sign * 0.18, 0.02, 0.02);
  lens.rotation.y = sign * -0.1;
  lens.castShadow = true;
  shadeTilt.add(lens);

  const rim = new THREE.Mesh(new THREE.TorusGeometry(0.145, 0.017, 8, 40), MAT.gold);
  rim.scale.set(1.1, 0.88, 1);
  rim.position.set(sign * 0.18, 0.02, 0.04);
  rim.rotation.y = sign * -0.1;
  shadeTilt.add(rim);

  const glint = new THREE.Mesh(
    new THREE.PlaneGeometry(0.062, 0.015),
    new THREE.MeshBasicMaterial({
      color: 0xffd6a4,
      transparent: true,
      opacity: 0.58,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
    })
  );
  glint.position.set(sign * 0.18 + 0.04, 0.075, 0.145);
  glint.rotation.z = -0.42;
  glint.rotation.y = sign * -0.1;
  shadeTilt.add(glint);

  // Temple arms.
  const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.009, 0.36, 6), MAT.gold);
  arm.rotation.x = Math.PI / 2;
  arm.rotation.z = sign * 0.05;
  arm.position.set(sign * 0.34, 0.035, -0.14);
  shadeTilt.add(arm);
}

const bridge = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.085, 8), MAT.gold);
bridge.rotation.z = Math.PI / 2;
bridge.position.set(0, 0.05, 0.036);
shadeTilt.add(bridge);

headGroup.add(shades);

/* ------------------------------ back feathers ----------------------------- */

function makeFeatherGeometry(length, width, thickness = 0.028, darkStart = 0.7) {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(length * 0.08, width * 0.13, length * 0.33, width * 0.49, length * 0.7, width * 0.48);
  shape.bezierCurveTo(length * 0.9, width * 0.47, length * 0.985, width * 0.2, length, 0);
  shape.bezierCurveTo(length * 0.985, -width * 0.2, length * 0.9, -width * 0.47, length * 0.7, -width * 0.48);
  shape.bezierCurveTo(length * 0.33, -width * 0.49, length * 0.08, -width * 0.13, 0, 0);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: thickness,
    bevelEnabled: true,
    bevelSegments: 2,
    bevelSize: thickness * 0.9,
    bevelThickness: thickness * 0.9,
    curveSegments: 14,
    steps: 1,
  });
  geo.translate(0, 0, -thickness * 0.5);

  const colors = [];
  const positions = geo.attributes.position;
  const cream = new THREE.Color(0xf2e3ca);
  const creamWarm = new THREE.Color(0xe3cdb0);
  const slate = new THREE.Color(0x223a45);
  const out = new THREE.Color();
  for (let i = 0; i < positions.count; i++) {
    const t = clamp(positions.getX(i) / length, 0, 1);
    if (t < darkStart) {
      out.copy(cream).lerp(creamWarm, t / darkStart * 0.7);
    } else {
      out.copy(creamWarm).lerp(slate, smoothstep(darkStart, 1, t));
    }
    colors.push(out.r, out.g, out.b);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  return geo;
}

// A jaunty tail fan behind the body.
const tailGroup = new THREE.Group();
tailGroup.position.set(0, 0.97, -0.35);
tailGroup.rotation.y = -0.22;
torso.add(tailGroup);
for (let i = 0; i < 5; i++) {
  const tail = new THREE.Mesh(
    makeFeatherGeometry(0.72 + Math.abs(2 - i) * 0.035, 0.28, 0.027, 0.72),
    MAT.feather
  );
  tail.position.set((i - 2) * 0.045, (i - 2) * 0.02, 0);
  tail.rotation.z = Math.PI - 0.3 + (i - 2) * 0.19;
  tail.rotation.x = -0.18 + (i - 2) * 0.06;
  tail.castShadow = true;
  tailGroup.add(tail);
}

/* ------------------------------ wings ------------------------------------- */

function makeWing(seed) {
  const wing = new THREE.Group();

  // Arm / leading edge.
  const armCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.0, 0.0, 0.0),
    new THREE.Vector3(0.22, 0.13, 0.02),
    new THREE.Vector3(0.58, 0.22, 0.045),
    new THREE.Vector3(0.94, 0.23, 0.06),
  ]);
  const arm = new THREE.Mesh(new THREE.TubeGeometry(armCurve, 20, 0.106, 10, false), MAT.cream);
  arm.material.side = THREE.DoubleSide;
  arm.castShadow = true;
  wing.add(arm);

  const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.16, 22, 14), MAT.cream);
  shoulder.position.set(0.03, 0.01, 0.0);
  shoulder.castShadow = true;
  wing.add(shoulder);

  const lengths = [0.98, 1.18, 1.32, 1.24, 1.04, 0.82];
  const angles = [0.47, 0.28, 0.09, -0.10, -0.28, -0.45];
  const widths = [0.31, 0.36, 0.39, 0.38, 0.34, 0.28];

  for (let i = 0; i < lengths.length; i++) {
    const feather = new THREE.Mesh(
      makeFeatherGeometry(lengths[i], widths[i], 0.022, 0.64),
      MAT.feather
    );
    feather.position.set(0.05 + i * 0.017, -0.015, 0.008 + i * 0.003);
    feather.rotation.z = angles[i];
    feather.rotation.x = 0.03 + i * 0.012;
    feather.rotation.y = seed * 0.012;
    feather.castShadow = true;
    wing.add(feather);
  }

  // Short, bright coverts layered over the shoulder.
  const coverts = [0.42, 0.52, 0.44, 0.34];
  const covertAngles = [0.42, 0.26, 0.09, -0.08];
  for (let i = 0; i < coverts.length; i++) {
    const covert = new THREE.Mesh(
      makeFeatherGeometry(coverts[i], 0.22 - i * 0.02, 0.018, 0.86),
      MAT.creamSoft
    );
    covert.position.set(0.02, 0.02, 0.06 + i * 0.005);
    covert.rotation.z = covertAngles[i];
    covert.rotation.x = 0.03;
    covert.castShadow = true;
    wing.add(covert);
  }

  return wing;
}

const rightWing = makeWing(1);
rightWing.position.set(0.4, 1.56, 0.04);
rightWing.rotation.z = 0.18;
rightWing.rotation.y = -0.08;
rightWing.userData.baseZ = 0.18;
rightWing.userData.phase = 0.0;
torso.add(rightWing);

const leftWing = makeWing(-1);
leftWing.position.set(-0.4, 1.56, 0.04);
leftWing.scale.x = -1;
leftWing.rotation.z = 0.5;
leftWing.rotation.y = 0.05;
leftWing.userData.baseZ = 0.5;
leftWing.userData.phase = 1.6;
torso.add(leftWing);

// A tiny hibiscus tucked behind the sunglasses.
const flowerGroup = new THREE.Group();
flowerGroup.position.set(-0.34, 0.29, -0.02);
flowerGroup.rotation.z = 0.38;
flowerGroup.rotation.y = -0.6;
headGroup.add(flowerGroup);
for (let i = 0; i < 5; i++) {
  const petal = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), i % 2 ? MAT.flower : MAT.flowerLight);
  petal.scale.set(0.12, 0.065, 0.025);
  petal.position.set(Math.cos((i / 5) * TAU) * 0.09, Math.sin((i / 5) * TAU) * 0.09, 0);
  petal.rotation.z = (i / 5) * TAU;
  flowerGroup.add(petal);
}
const flowerCenter = new THREE.Mesh(new THREE.SphereGeometry(0.04, 12, 8), MAT.flowerCenter);
flowerCenter.position.z = 0.025;
flowerGroup.add(flowerCenter);

// A small shell necklace.
const shellMaterial = new THREE.MeshStandardMaterial({ color: 0xf7d9ae, roughness: 0.5 });
for (let i = 0; i < 7; i++) {
  const t = i / 6;
  const shell = new THREE.Mesh(new THREE.SphereGeometry(0.032, 10, 8), shellMaterial);
  shell.scale.set(0.8, 1.3, 0.55);
  shell.position.set((t - 0.5) * 0.38, 1.7 - Math.sin(t * Math.PI) * 0.13, 0.425);
  shell.rotation.set(0.28, 0, (i - 3) * 0.06);
  torso.add(shell);
}

/* -------------------------------------------------------------------------- */
/*  Splash & spray                                                            */
/* -------------------------------------------------------------------------- */

const sprayTexture = makeCanvasTexture(64, 64, (ctx, w, h) => {
  const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(0.3, "rgba(244,244,230,0.8)");
  g.addColorStop(0.7, "rgba(235,245,240,0.2)");
  g.addColorStop(1, "rgba(235,245,240,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);
});

const MAX_SPRAY = 260;
const sprayPositions = new Float32Array(MAX_SPRAY * 3);
const spraySizes = new Float32Array(MAX_SPRAY);
const sprayAlphas = new Float32Array(MAX_SPRAY);
const sprayData = [];

for (let i = 0; i < MAX_SPRAY; i++) {
  sprayData.push({
    x: 0,
    y: -20,
    z: 0,
    vx: 0,
    vy: 0,
    vz: 0,
    life: 0,
    maxLife: 1,
    size: 0.1,
  });
  sprayPositions[i * 3 + 1] = -20;
}

const sprayGeometry = new THREE.BufferGeometry();
sprayGeometry.setAttribute("position", new THREE.BufferAttribute(sprayPositions, 3));
sprayGeometry.setAttribute("aSize", new THREE.BufferAttribute(spraySizes, 1));
sprayGeometry.setAttribute("aAlpha", new THREE.BufferAttribute(sprayAlphas, 1));

const sprayMaterial = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
  uniforms: {
    uMap: { value: sprayTexture },
    uPixelRatio: { value: renderer.getPixelRatio() },
    uColor: { value: new THREE.Color(0xfff4e2) },
  },
  vertexShader: /* glsl */ `
    attribute float aSize;
    attribute float aAlpha;
    varying float vAlpha;
    uniform float uPixelRatio;
    void main() {
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = aSize * uPixelRatio * (680.0 / max(0.1, -mvPosition.z));
      gl_Position = projectionMatrix * mvPosition;
      vAlpha = aAlpha;
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D uMap;
    uniform vec3 uColor;
    varying float vAlpha;
    void main() {
      vec4 tex = texture2D(uMap, gl_PointCoord);
      if (tex.a * vAlpha < 0.01) discard;
      gl_FragColor = vec4(uColor * (0.9 + tex.a * 0.3), tex.a * vAlpha);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const spray = new THREE.Points(sprayGeometry, sprayMaterial);
spray.frustumCulled = false;
scene.add(spray);

// Soft banners of spray behind the rail, to give the carve some punch.
const plumeTexture = makeCanvasTexture(256, 256, (ctx, w, h) => {
  ctx.clearRect(0, 0, w, h);
  let seed = 551;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
  for (let i = 0; i < 46; i++) {
    const x = w * (0.35 + rand() * 0.42);
    const y = h * (0.3 + rand() * 0.55);
    const r = 8 + rand() * 34;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, "rgba(255,255,255,0.8)");
    g.addColorStop(0.5, "rgba(255,255,255,0.22)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.fillRect(x - r, y - r, r * 2, r * 2);
  }
});
const plume = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: plumeTexture,
    color: 0xfff4e4,
    transparent: true,
    opacity: 0.32,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })
);
plume.scale.set(2.4, 1.5, 1);
plume.position.set(-1.75, 0.27, 0.12);
plume.renderOrder = 3;
surfer.add(plume);

const bowMist = new THREE.Sprite(
  new THREE.SpriteMaterial({
    map: plumeTexture,
    color: 0xffedd8,
    transparent: true,
    opacity: 0.17,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })
);
bowMist.scale.set(1.2, 0.7, 1);
bowMist.position.set(1.65, 0.24, 0.05);
bowMist.renderOrder = 3;
surfer.add(bowMist);

let sprayCursor = 0;
let splashEnergy = 0;
let clickImpulse = 0;

function spawnSpray(x, y, z, burst = 1) {
  const d = sprayData[sprayCursor];
  d.x = x + randomBetween(-0.22, 0.22);
  d.y = y + randomBetween(-0.02, 0.15);
  d.z = z + randomBetween(-0.2, 0.2);
  const angle = Math.random() * TAU;
  const speed = randomBetween(0.2, 0.9) * burst;
  d.vx = Math.cos(angle) * speed * 0.6 - 0.2 * burst;
  d.vy = randomBetween(0.5, 1.7) * burst;
  d.vz = Math.sin(angle) * speed * 0.5;
  d.maxLife = randomBetween(0.45, 1.1);
  d.life = d.maxLife;
  d.size = randomBetween(0.07, 0.21) * (0.8 + burst * 0.4);
  sprayCursor = (sprayCursor + 1) % MAX_SPRAY;
}

function spawnSplashBurst(count = 44, power = 1.4) {
  const boardWorld = new THREE.Vector3();
  surfer.getWorldPosition(boardWorld);
  for (let i = 0; i < count; i++) {
    const dir = Math.random() > 0.5 ? 1 : -1;
    spawnSpray(
      boardWorld.x + randomBetween(-0.6, 0.4) - 1.1,
      boardWorld.y + 0.05,
      boardWorld.z + dir * randomBetween(0.15, 0.5),
      randomBetween(0.9, 1.55) * power
    );
  }
  splashEnergy = Math.min(1.5, splashEnergy + 0.75);
  clickImpulse = 1.0;
}

function updateSpray(dt) {
  const boardWorld = new THREE.Vector3();
  surfer.getWorldPosition(boardWorld);

  // Continuous small trail, like a board throwing a thin wake.
  if (Math.random() < dt * 72) {
    const tailLocal = new THREE.Vector3(-1.35 + randomBetween(-0.35, 0.3), 0.22, randomBetween(-0.38, 0.38));
    const sideLocal = new THREE.Vector3(randomBetween(-0.4, 1.1), 0.18, (Math.random() > 0.5 ? 1 : -1) * randomBetween(0.32, 0.48));
    const p = Math.random() > 0.4 ? tailLocal : sideLocal;
    boardGroup.localToWorld(p);
    spawnSpray(p.x, p.y, p.z, randomBetween(0.6, 1.05));
  }

  const positions = sprayGeometry.attributes.position.array;
  const sizes = sprayGeometry.attributes.aSize.array;
  const alphas = sprayGeometry.attributes.aAlpha.array;
  for (let i = 0; i < MAX_SPRAY; i++) {
    const d = sprayData[i];
    if (d.life > 0) {
      d.life -= dt;
      d.vy -= dt * 2.4;
      d.vx *= 1 - dt * 0.95;
      d.vz *= 1 - dt * 0.95;
      d.x += d.vx * dt;
      d.y += d.vy * dt;
      d.z += d.vz * dt;
      if (d.y < -0.4) d.life = 0;
      positions[i * 3] = d.x;
      positions[i * 3 + 1] = d.y;
      positions[i * 3 + 2] = d.z;
      sizes[i] = d.size;
      alphas[i] = clamp(d.life / d.maxLife, 0, 1) * 0.9;
    } else {
      positions[i * 3 + 1] = -20;
      alphas[i] = 0;
    }
  }

  sprayGeometry.attributes.position.needsUpdate = true;
  sprayGeometry.attributes.aSize.needsUpdate = true;
  sprayGeometry.attributes.aAlpha.needsUpdate = true;
}

/* -------------------------------------------------------------------------- */
/*  Distant birds                                                             */
/* -------------------------------------------------------------------------- */

const distantBirds = [];
const birdMaterial = new THREE.MeshBasicMaterial({
  color: 0x3c4c56,
  side: THREE.DoubleSide,
  transparent: true,
  opacity: 0.46,
});

function makeDistantBird(x, y, z, scale) {
  const g = new THREE.Group();
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, 0);
  wingShape.quadraticCurveTo(0.55, 0.18, 1.4, 0.0);
  wingShape.quadraticCurveTo(0.74, -0.1, 0.3, -0.18);
  wingShape.quadraticCurveTo(0.1, -0.12, 0, 0);
  const wingGeo = new THREE.ShapeGeometry(wingShape);

  const left = new THREE.Mesh(wingGeo, birdMaterial);
  left.rotation.y = Math.PI;
  g.add(left);
  const right = new THREE.Mesh(wingGeo, birdMaterial);
  g.add(right);

  g.position.set(x, y, z);
  g.scale.setScalar(scale);
  g.userData.left = left;
  g.userData.right = right;
  g.userData.phase = Math.random() * TAU;
  g.userData.speed = randomBetween(3.2, 4.8);
  scene.add(g);
  distantBirds.push(g);
  return g;
}

makeDistantBird(-14, 15, -64, 0.7);
makeDistantBird(-10.4, 17.2, -70, 0.5);
makeDistantBird(-18, 12.6, -58, 0.45);
makeDistantBird(13, 19, -76, 0.55);
makeDistantBird(16, 16.8, -69, 0.4);

/* -------------------------------------------------------------------------- */
/*  A little flying fish                                                     */
/* -------------------------------------------------------------------------- */

const fishGroup = new THREE.Group();
fishGroup.visible = false;
scene.add(fishGroup);

const fishBodyMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xb3d5d6,
  roughness: 0.26,
  metalness: 0.45,
  clearcoat: 0.5,
  clearcoatRoughness: 0.2,
});
const fishBackMaterial = new THREE.MeshStandardMaterial({
  color: 0x315e68,
  roughness: 0.4,
  metalness: 0.2,
});
const fishFinMaterial = new THREE.MeshStandardMaterial({
  color: 0xf0a66d,
  roughness: 0.55,
  metalness: 0.05,
  transparent: true,
  opacity: 0.86,
  side: THREE.DoubleSide,
});
const fishEyeMaterial = new THREE.MeshStandardMaterial({
  color: 0x10252a,
  roughness: 0.2,
  metalness: 0.2,
});

const fishBody = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), fishBodyMaterial);
fishBody.scale.set(0.28, 0.092, 0.062);
fishBody.castShadow = true;
fishGroup.add(fishBody);

const fishBack = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), fishBackMaterial);
fishBack.scale.set(0.245, 0.072, 0.063);
fishBack.position.y = 0.018;
fishGroup.add(fishBack);

const fishBelly = new THREE.Mesh(
  new THREE.SphereGeometry(1, 24, 16),
  new THREE.MeshStandardMaterial({ color: 0xf3ddbe, roughness: 0.5, metalness: 0.08 })
);
fishBelly.scale.set(0.235, 0.052, 0.061);
fishBelly.position.set(0.01, -0.045, 0.002);
fishGroup.add(fishBelly);

const fishTail = new THREE.Group();
fishTail.position.x = -0.24;
fishTail.position.z = 0;
fishGroup.add(fishTail);
for (const sign of [-1, 1]) {
  const tailShape = new THREE.Shape();
  tailShape.moveTo(0, 0);
  tailShape.quadraticCurveTo(-0.08, sign * 0.06, -0.19, sign * 0.16);
  tailShape.quadraticCurveTo(-0.15, sign * 0.01, 0, 0);
  const tail = new THREE.Mesh(new THREE.ShapeGeometry(tailShape), fishFinMaterial);
  tail.rotation.y = sign * 0.15;
  fishTail.add(tail);
}

const fishFinGroup = [];
for (const sign of [-1, 1]) {
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.quadraticCurveTo(0.14, sign * 0.12, -0.08, sign * 0.28);
  finShape.quadraticCurveTo(-0.06, sign * 0.12, -0.1, 0);
  const fin = new THREE.Mesh(new THREE.ShapeGeometry(finShape), fishFinMaterial);
  fin.position.set(0.02, -0.005, sign * 0.055);
  fin.rotation.z = sign * 0.28;
  fin.rotation.y = sign * 0.72;
  fishGroup.add(fin);
  fishFinGroup.push(fin);
}
const dorsalShape = new THREE.Shape();
dorsalShape.moveTo(-0.13, 0);
dorsalShape.quadraticCurveTo(-0.02, 0.12, 0.12, 0.02);
dorsalShape.quadraticCurveTo(0.03, 0.03, -0.13, 0);
const dorsal = new THREE.Mesh(new THREE.ShapeGeometry(dorsalShape), fishFinMaterial);
dorsal.position.set(0.02, 0.06, 0);
fishGroup.add(dorsal);

for (const sign of [-1, 1]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.017, 10, 8), fishEyeMaterial);
  eye.position.set(0.2, 0.02, sign * 0.052);
  fishGroup.add(eye);
  const glare = new THREE.Mesh(
    new THREE.SphereGeometry(0.005, 8, 6),
    new THREE.MeshBasicMaterial({ color: 0xfff4dc })
  );
  glare.position.set(0.207, 0.027, sign * 0.064);
  fishGroup.add(glare);
}

let fishPhase = 2.8;
let fishWasAirborne = false;
const fishStart = new THREE.Vector3(2.9, 0, -0.35);
const fishEnd = new THREE.Vector3(4.85, 0, -0.55);
const fishFlight = 2.6;
const fishCycle = 6.5;

function fishWaterY(x, z, t) {
  return waveHeightAt(x, z, t) + 0.1;
}

function spawnFishSplash(x, z) {
  const y = waveHeightAt(x, z, elapsed) + 0.12;
  for (let i = 0; i < 22; i++) {
    spawnSpray(x + randomBetween(-0.25, 0.25), y, z + randomBetween(-0.2, 0.2), randomBetween(0.7, 1.25));
  }
}

function updateFish(t) {
  const phase = (t + fishPhase) % fishCycle;
  const airborne = phase < fishFlight;

  if (airborne) {
    const s = phase / fishFlight;
    const x = lerp(fishStart.x, fishEnd.x, s);
    const z = lerp(fishStart.z, fishEnd.z, s) + Math.sin(s * Math.PI) * 0.12;
    const waterY = fishWaterY(x, z, t);
    const y = waterY + 0.12 + Math.sin(s * Math.PI) * 1.18;
    fishGroup.position.set(x, y, z);

    const dx = fishEnd.x - fishStart.x;
    const dz = fishEnd.z - fishStart.z;
    const dy = Math.cos(s * Math.PI) * Math.PI * 1.18;
    const horizontal = Math.hypot(dx, dz) / fishFlight;
    const pitch = Math.atan2(dy, dx) * 0.85;
    fishGroup.rotation.set(0, -0.34 + Math.sin(t * 0.8) * 0.04, pitch);
    fishGroup.rotation.y = -0.3;
    fishGroup.visible = true;

    fishTail.rotation.y = Math.sin(t * 17 + 0.7) * 0.55;
    for (let i = 0; i < fishFinGroup.length; i++) {
      fishFinGroup[i].rotation.y = (i === 0 ? 0.72 : -0.72) + Math.sin(t * 12 + i * 1.2) * 0.18;
    }
    fishGroup.scale.setScalar(0.9);

    if (!fishWasAirborne) {
      spawnFishSplash(fishStart.x, fishStart.z);
    }
  } else {
    fishGroup.visible = false;
    if (fishWasAirborne) {
      spawnFishSplash(fishEnd.x, fishEnd.z);
    }
  }
  fishWasAirborne = airborne;
}

/* -------------------------------------------------------------------------- */
/*  Interaction                                                               */
/* -------------------------------------------------------------------------- */

function setPointer(clientX, clientY) {
  pointer.x = (clientX / window.innerWidth) * 2 - 1;
  pointer.y = -((clientY / window.innerHeight) * 2 - 1);
  pointer.active = true;
}

window.addEventListener("pointermove", (e) => {
  setPointer(e.clientX, e.clientY);
});

window.addEventListener("pointerdown", (e) => {
  if (e.target === canvas) {
    spawnSplashBurst(52, 1.5);
  }
});

window.addEventListener("pointerleave", () => {
  pointer.active = false;
});

window.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    spawnSplashBurst(62, 1.7);
  }
});

/* -------------------------------------------------------------------------- */
/*  Resize                                                                    */
/* -------------------------------------------------------------------------- */

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;

  // Portrait screens get a wider lens and a little more breathing room.
  const compact = w / h < 0.9;
  camera.fov = compact ? 46 : 34;
  camera.updateProjectionMatrix();

  const ratio = Math.min(window.devicePixelRatio, 2);
  renderer.setPixelRatio(ratio);
  sprayMaterial.uniforms.uPixelRatio.value = ratio;

  LOOK_BASE.set(compact ? 0.0 : 0.15, compact ? 1.58 : 1.62, 0);
  CAMERA_BASE.set(compact ? 3.2 : 4.0, compact ? 2.85 : 2.55, compact ? 11.4 : 9.4);
}

window.addEventListener("resize", resize);
resize();

/* -------------------------------------------------------------------------- */
/*  Animation                                                                 */
/* -------------------------------------------------------------------------- */


function animate() {
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  pointer.smoothX = lerp(pointer.smoothX, pointer.active ? pointer.x : 0, 1 - Math.pow(0.02, dt));
  pointer.smoothY = lerp(pointer.smoothY, pointer.active ? pointer.y : 0, 1 - Math.pow(0.02, dt));

  const t = elapsed;

  // A living board, with a little weight shift and lean.
  const boardBob = Math.sin(t * 1.12) * 0.055 + Math.sin(t * 0.47 + 1.2) * 0.035;
  const boardRoll = Math.sin(t * 0.86 + 0.6) * 0.032 + Math.sin(t * 1.9) * 0.012;
  const boardPitch = Math.cos(t * 1.04 + 0.4) * 0.018;

  boardGroup.position.y = boardBob;
  boardGroup.rotation.z = 0.052 + boardRoll;
  boardGroup.rotation.x = boardPitch + 0.12;
  boardGroup.rotation.y = -0.14 + Math.sin(t * 0.33) * 0.045;

  // A slow carve along the face of the swell, planted in the moving water.
  surfer.position.x = SURFER_BASE.x + Math.sin(t * 0.28) * 0.48;
  surfer.position.z = SURFER_BASE.z + Math.cos(t * 0.21) * 0.2;
  surfer.position.y = waveHeightAt(surfer.position.x, surfer.position.z, t) + 0.2 - 0.165;
  surfer.rotation.y = -0.1 + Math.sin(t * 0.28 - 0.6) * 0.09;

  if (plume) {
    plume.material.opacity = 0.22 + Math.sin(t * 2.1) * 0.04 + Math.abs(Math.cos(t * 0.29)) * 0.08;
    plume.scale.set(2.2 + Math.sin(t * 1.7) * 0.25, 1.25 + Math.sin(t * 1.3) * 0.14, 1);
    bowMist.material.opacity = 0.1 + Math.sin(t * 2.6 + 1.0) * 0.035;
  }

  // Character: a loose, happy sway on top of the board.
  torso.position.y = Math.sin(t * 1.3 + 0.8) * 0.025;
  torso.rotation.z = Math.sin(t * 0.72) * 0.035 + boardRoll * 0.7;
  torso.rotation.x = Math.sin(t * 0.9 + 0.5) * 0.02;
  torso.rotation.y = 0.01 + Math.sin(t * 0.38 + 0.3) * 0.05;

  // Head looks out across the water, occasionally glancing back at us.
  const headLook = Math.sin(t * 0.34 + 2.1) * 0.09 + pointer.smoothX * 0.12;
  headGroup.rotation.y = 1.32 + headLook;
  headGroup.rotation.x = -0.02 + Math.sin(t * 0.82 + 0.7) * 0.028 - pointer.smoothY * 0.06;
  headGroup.rotation.z = -0.035 + Math.sin(t * 0.58) * 0.022;

  // Bill and pouch secondary motion.
  upperBill.rotation.x = 0.015 + Math.sin(t * 1.7 + 0.2) * 0.008;
  pouch.scale.y = 0.22 + Math.sin(t * 1.8 + 1.1) * 0.006 + splashEnergy * 0.01;
  pouch.position.y = -0.43 + Math.sin(t * 1.8 + 1.1) * 0.004;

  // Wings balancing in the breeze; they get a little more energetic after a click.
  const flap = Math.sin(t * 1.6) * 0.055 + Math.sin(t * 0.7 + 0.9) * 0.025 + clickImpulse * Math.sin(t * 18) * 0.14;
  const flapLeft = Math.sin(t * 1.6 + leftWing.userData.phase) * 0.06 + clickImpulse * Math.sin(t * 18 + 0.4) * 0.12;
  rightWing.rotation.z = rightWing.userData.baseZ + flap + 0.04;
  leftWing.rotation.z = leftWing.userData.baseZ + flapLeft + 0.03;
  rightWing.rotation.y = -0.08 + Math.sin(t * 0.53) * 0.04;
  leftWing.rotation.y = 0.05 - Math.sin(t * 0.53 + 1.2) * 0.04;

  // Tail feathers fan a little wider in the fast sections.
  tailGroup.rotation.z = Math.sin(t * 0.9 + 0.3) * 0.05;
  tailGroup.rotation.x = -0.02 + Math.sin(t * 1.2 + 1.4) * 0.03;

  // Flower and crest flutter.
  flowerGroup.rotation.z = 0.38 + Math.sin(t * 1.9 + 0.4) * 0.04;
  for (let i = 0; i < crestFeathers.length; i++) {
    crestFeathers[i].rotation.z = Math.PI - 0.5 + i * 0.12 + Math.sin(t * 2.1 + i * 0.7) * 0.025;
  }

  clickImpulse *= Math.pow(0.02, dt);
  splashEnergy *= Math.pow(0.28, dt);

  // Camera breath: barely perceptible, but it keeps the still frame alive.
  const orbit = Math.sin(t * 0.095) * 0.18;
  const cameraDriftX = Math.sin(t * 0.17 + 0.7) * 0.07 + pointer.smoothX * 0.34;
  const cameraDriftY = Math.sin(t * 0.2 + 1.9) * 0.045 + pointer.smoothY * 0.16;
  const clickShake = clickImpulse * 0.035;
  camera.position.x = CAMERA_BASE.x + cameraDriftX + Math.sin(t * 0.71) * clickShake;
  camera.position.y = CAMERA_BASE.y + cameraDriftY + Math.cos(t * 0.64) * clickShake;
  camera.position.z = CAMERA_BASE.z + orbit * 0.45;

  const lookTarget = tempVec.copy(LOOK_BASE);
  lookTarget.x += pointer.smoothX * 0.09;
  lookTarget.y += pointer.smoothY * 0.06 + Math.sin(t * 0.38) * 0.025;
  camera.lookAt(lookTarget);

  // Ocean, sky and distant details.
  waterUniforms.uTime.value = t;
  skyMaterial.uniforms.uTime.value = t;

  const boardWorld = new THREE.Vector3();
  surfer.getWorldPosition(boardWorld);
  waterUniforms.uBoardPosition.value.set(boardWorld.x, boardWorld.z);

  const boardHeading = surfer.rotation.y + boardGroup.rotation.y;
  const wakeDistance = 1.12;
  wakeFoam.position.set(
    boardWorld.x - Math.cos(boardHeading) * wakeDistance,
    waveHeightAt(boardWorld.x, boardWorld.z, t) + 0.075,
    boardWorld.z + Math.sin(boardHeading) * wakeDistance
  );
  wakeFoam.rotation.y = boardHeading;
  wakeFoam.material.opacity = 0.7 + Math.sin(t * 2.2) * 0.06;
  bounce.position.x = boardWorld.x;
  bounce.position.z = boardWorld.z + 0.7;

  for (const bird of distantBirds) {
    const wingBeat = Math.sin(t * bird.userData.speed + bird.userData.phase);
    bird.userData.left.rotation.z = wingBeat * 0.42;
    bird.userData.right.rotation.z = wingBeat * 0.42;
    const drift = Math.sin(t * 0.035 + bird.userData.phase) * 0.5;
    bird.position.x += Math.sin(t * 0.014 + bird.userData.phase) * 0.002;
    bird.position.y += Math.cos(t * 0.5 + bird.userData.phase) * 0.0007 + drift * 0.0001;
  }

  for (let i = 0; i < cloudSprites.length; i++) {
    cloudSprites[i].material.rotation += dt * (0.0015 + i * 0.0004);
  }

  updateFish(t);
  updateSpray(dt);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// Start with one warm splash so the first frame already feels alive.
spawnSplashBurst(28, 0.9);
animate();
