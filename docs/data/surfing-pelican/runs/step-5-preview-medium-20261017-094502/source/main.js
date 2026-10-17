import * as THREE from 'three';

/* ============================================================================
   Surfing Pelican — an autonomous, animated three.js scene.
   No interaction: the camera, the pelican and the sea all do their own thing.

   Contents
     1. helpers
     2. wave field (shared by JS placement code and the ocean shader)
     3. renderer / scene / camera / lights
     4. sky dome + sun
     5. ocean (procedural grid + displacement shader)
     6. the pelican and its surfboard
     7. spray particles
     8. seagulls + a distant sailboat
     9. animation loop
   ========================================================================== */

/* ---------------------------------------------------------------- 1. helpers */
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const rand = (a, b) => a + Math.random() * (b - a);
const smoothstep = t => {
  t = clamp(t, 0, 1);
  return t * t * (3 - 2 * t);
};

/** Shader-friendly number formatting (always keeps a decimal point). */
const f5 = n => (Math.abs(n) < 1e-5 ? '0.0' : n.toFixed(5));

/* ------------------------------------------------------------ 2. wave field */
const WAVES = [
  { dir: [1.0, 0.22], amp: 0.42, len: 26.0, spd: 1.0 },
  { dir: [-0.55, 0.86], amp: 0.28, len: 15.0, spd: 1.45 },
  { dir: [0.72, -0.94], amp: 0.16, len: 9.5, spd: 2.1 },
].map(w => {
  const l = Math.hypot(w.dir[0], w.dir[1]);
  const k = (Math.PI * 2) / w.len;
  return { nx: w.dir[0] / l, nz: w.dir[1] / l, k, omega: k * w.spd, amp: w.amp };
});

/** Surface height at a world position (the water plane is y = 0). */
function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    h += w.amp * Math.sin(w.k * (w.nx * x + w.nz * z) - w.omega * t);
  }
  return h;
}

/** Unit surface normal at a world position. */
function waveNormal(x, z, t, target) {
  const e = 0.35;
  const hl = waveHeight(x - e, z, t);
  const hr = waveHeight(x + e, z, t);
  const hb = waveHeight(x, z - e, t);
  const hf = waveHeight(x, z + e, t);
  return target.set(-(hr - hl) / (2 * e), 1, -(hf - hb) / (2 * e)).normalize();
}

/** The identical wave field, expressed for the ocean vertex shader. */
function waveGLSL() {
  const body = WAVES
    .map(
      w =>
        `  h += ${f5(w.amp)} * sin(${f5(w.k)} * dot(vec2(${f5(w.nx)}, ${f5(w.nz)}), p)` +
        ` - ${f5(w.omega)} * t);`,
    )
    .join('\n');
  return `
float waveH(vec2 p, float t) {
  float h = 0.0;
${body}
  return h;
}`;
}

const WATER_LEVEL = 0.0;

/* --------------------------------------------------------------- 3. the scene */
const container = document.getElementById('scene');

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: 'high-performance',
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  52,
  window.innerWidth / Math.max(1, window.innerHeight),
  0.1,
  3200,
);
camera.position.set(-42, 15, 36);

/* palette — golden hour over a tropical swell */
const PAL = {
  zenith: new THREE.Color('#1c3f78'),
  horizon: new THREE.Color('#ffb476'),
  haze: new THREE.Color('#ffd9a8'),
  sun: new THREE.Color('#fff0c4'),
  deep: new THREE.Color('#17384e'),
  shallow: new THREE.Color('#3c7d8d'),
  foam: new THREE.Color('#f4f8f6'),
};
const SUN_DIR = new THREE.Vector3(0.44, 0.17, 0.9).normalize();
// matches (closely) the sky dome's own horizon band
const FOG_COLOR = PAL.horizon.clone().lerp(PAL.zenith, 0.39).multiplyScalar(0.92);
const FOG_DENSITY = 0.0062;

scene.fog = new THREE.FogExp2(FOG_COLOR.getHex(), FOG_DENSITY);

/* lights (the pelican uses standard materials, the sea lights itself) */
const sunLight = new THREE.DirectionalLight(PAL.sun, 2.4);
sunLight.position.copy(SUN_DIR).multiplyScalar(400);
scene.add(sunLight);

const skyFill = new THREE.HemisphereLight(
  new THREE.Color('#8fc4ff'),
  new THREE.Color('#12486b'),
  1.15,
);
scene.add(skyFill);

const rimLight = new THREE.DirectionalLight(new THREE.Color('#ff9d5c'), 0.9);
rimLight.position.set(-220, 90, -260);
scene.add(rimLight);

/* ------------------------------------------------------------ 4. sky and sun */
const skyUniforms = {
  uSunDir: { value: SUN_DIR },
  uSunColor: { value: PAL.sun },
  uHorizon: { value: PAL.horizon },
  uHaze: { value: PAL.haze },
  uZenith: { value: PAL.zenith },
};

/** Sky colour for a view direction — reused by the ocean for reflections. */
const SKY_FN_GLSL = /* glsl */ `
vec3 skyColor(vec3 d, vec3 sunDir, vec3 sunCol, vec3 horizon, vec3 haze, vec3 zenith) {
  d = normalize(d);
  float h = clamp(d.y, -1.0, 1.0);
  vec3 col = mix(horizon, zenith, pow(h * 0.5 + 0.5, 1.35));
  col = mix(col * 0.32, col, smoothstep(-0.25, 0.02, h));
  float s = max(dot(d, sunDir), 0.0);
  col += sunCol * pow(s, 6.0) * 0.12;       // wide hazy glow
  col += haze * pow(s, 26.0) * 0.30;        // tighter glow
  col += sunCol * pow(s, 1600.0) * 3.0;     // the disc itself
  return col;
}`;

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(1500, 48, 32),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: skyUniforms,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        vDir = world.xyz - cameraPosition;
        gl_Position = projectionMatrix * viewMatrix * world;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir, uSunColor, uHorizon, uHaze, uZenith;
      varying vec3 vDir;
      ${SKY_FN_GLSL}
      void main() {
        gl_FragColor = vec4(skyColor(vDir, uSunDir, uSunColor, uHorizon, uHaze, uZenith), 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  }),
);
sky.frustumCulled = false;
sky.renderOrder = -1;
scene.add(sky);

/* ----------------------------------------------------------------- 5. ocean */
const OCEAN_SIZE = 760;
const OCEAN_SEG = 300;

const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEG, OCEAN_SEG);
oceanGeo.rotateX(-Math.PI / 2); // bake: geometry now lies in the XZ plane at y = 0

const oceanUniforms = {
  uTime: { value: 0 },
  uLevel: { value: WATER_LEVEL },
  uSunDir: { value: SUN_DIR },
  uSunColor: { value: PAL.sun },
  uHorizon: { value: PAL.horizon },
  uHaze: { value: PAL.haze },
  uZenith: { value: PAL.zenith },
  uDeep: { value: PAL.deep },
  uShallow: { value: PAL.shallow },
  uFoam: { value: PAL.foam },
  uFogDensity: { value: FOG_DENSITY },
};

const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.ShaderMaterial({
    uniforms: oceanUniforms,
    vertexShader: /* glsl */ `
      uniform float uTime;
      uniform float uLevel;
      varying vec3 vWorld;
      varying vec3 vNormal;
      varying float vH;
      varying float vDist;
      ${waveGLSL()}
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        world.y += waveH(world.xz, uTime) + uLevel;
        // normal from central differences on the very same wave field
        float e = 0.45;
        float hx0 = waveH(world.xz - vec2(e, 0.0), uTime);
        float hx1 = waveH(world.xz + vec2(e, 0.0), uTime);
        float hz0 = waveH(world.xz - vec2(0.0, e), uTime);
        float hz1 = waveH(world.xz + vec2(0.0, e), uTime);
        vNormal = normalize(vec3(hx0 - hx1, 2.0 * e, hz0 - hz1));
        vH = world.y;
        vWorld = world.xyz;
        vec4 view = viewMatrix * world;
        vDist = length(view.xyz);
        gl_Position = projectionMatrix * view;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir, uSunColor, uHorizon, uHaze, uZenith;
      uniform vec3 uDeep, uShallow, uFoam;
      uniform float uFogDensity, uTime;
      varying vec3 vWorld;
      varying vec3 vNormal;
      varying float vH;
      varying float vDist;

      ${SKY_FN_GLSL}

      float hash21(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }
      float vnoise(vec2 p) {
        vec2 i = floor(p), fr = fract(p);
        vec2 u = fr * fr * (3.0 - 2.0 * fr);
        float a = hash21(i);
        float b = hash21(i + vec2(1.0, 0.0));
        float c = hash21(i + vec2(0.0, 1.0));
        float d = hash21(i + vec2(1.0, 1.0));
        return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
      }

      // cheap horizon target for distance fog (the full skyColor() is only
           // needed for reflections)
      vec3 skyFog(vec3 d, vec3 horizon, vec3 zenith, vec3 haze, vec3 sunDir) {
        float h = clamp(normalize(d).y, -1.0, 1.0);
        vec3 col = mix(horizon, zenith, pow(h * 0.5 + 0.5, 1.35));
        col = mix(col * 0.32, col, smoothstep(-0.25, 0.02, h));
        float s = max(dot(normalize(d), sunDir), 0.0);
        col += haze * pow(s, 26.0) * 0.30;
        return col;
      }

      void main() {
        vec3 N = normalize(vNormal);
        vec3 V = normalize(cameraPosition - vWorld);

        // water body: darker in the troughs, bright on the swell
        float hN = smoothstep(-0.62, 0.72, vH);
        vec3 water = mix(uDeep, uShallow, hN);
        water += uSunColor * 0.05 * smoothstep(0.15, 0.8, vH);

        // sky reflection, fresnel-boosted at grazing angles
        float fres = pow(1.0 - max(dot(N, V), 0.0), 4.0);
        fres = clamp(0.03 + 0.97 * fres, 0.0, 1.0);
        vec3 R = reflect(-V, N);
        R.y = abs(R.y) + 0.015;
        vec3 sky = skyColor(R, uSunDir, uSunColor, uHorizon, uHaze, uZenith);

        vec3 col = mix(water, sky, fres * 0.88);

        // sun glitter
        vec3 H = normalize(uSunDir + V);
        col += uSunColor * pow(max(dot(N, H), 0.0), 420.0) * 2.2;
        col += vec3(1.0, 0.96, 0.9) * pow(max(dot(N, H), 0.0), 2600.0) * 3.0;

        // foam: crest lines plus whitecaps on the steep faces
        float steep = clamp(1.0 - N.y, 0.0, 1.0);
        float crest = smoothstep(0.30, 0.74, vH);
        float n1 = vnoise(vWorld.xz * 0.5 + vec2(uTime * 0.09, -uTime * 0.05));
        float n2 = vnoise(vWorld.xz * 1.7 - vec2(uTime * 0.19, uTime * 0.12));
        float foam = smoothstep(0.72, 1.06, crest * 1.08 + n1 * 0.5 - 0.16) * (0.4 + 0.6 * n2);
        foam += smoothstep(0.3, 0.52, steep) * 0.32 * n2;
        col = mix(col, uFoam, clamp(foam, 0.0, 1.0) * 0.82);

        // exponential-squared fog that fades into the actual sky, so the
        // horizon seam disappears no matter where the sun is
        float fog = 1.0 - exp(-uFogDensity * uFogDensity * vDist * vDist);
        vec3 horizonCol = skyFog(vWorld - cameraPosition, uHorizon, uZenith, uHaze, uSunDir);
        col = mix(col, horizonCol, clamp(fog, 0.0, 1.0));

        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  }),
);
ocean.frustumCulled = false;
scene.add(ocean);

/* ------------------------------------------- 6. the pelican and its surfboard */
const FEATHER = new THREE.MeshStandardMaterial({ color: '#f4ecdd', roughness: 0.82, metalness: 0 });
const FEATHER_WING = new THREE.MeshStandardMaterial({
  color: '#ded6c6', roughness: 0.9, metalness: 0, side: THREE.DoubleSide,
});
const FEATHER_TIP = new THREE.MeshStandardMaterial({
  color: '#5b5f68', roughness: 0.9, metalness: 0, side: THREE.DoubleSide,
});
const BEAK = new THREE.MeshStandardMaterial({ color: '#f0912e', roughness: 0.45, metalness: 0.05 });
const POUCH = new THREE.MeshStandardMaterial({ color: '#e07a2c', roughness: 0.5, metalness: 0.05 });
const FOOT = new THREE.MeshStandardMaterial({ color: '#e2792c', roughness: 0.55 });
const EYE = new THREE.MeshStandardMaterial({ color: '#14161c', roughness: 0.25 });
const SPARK = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.2 });
const FINISH = new THREE.MeshStandardMaterial({ color: '#2f6f8f', roughness: 0.4, metalness: 0.1 });
const DARK_BIRD = new THREE.MeshStandardMaterial({
  color: '#33383f', roughness: 0.9, side: THREE.DoubleSide,
});

/** Candy-stripe deck texture, generated in code (no external assets). */
function makeBoardTexture() {
  const c = document.createElement('canvas');
  c.width = 128;
  c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = '#e0452f';
  g.fillRect(0, 0, 128, 128);
  g.fillStyle = '#2f6f8f';
  g.fillRect(0, 34, 128, 5);
  g.fillStyle = '#f7efe2';
  g.fillRect(0, 62, 128, 12);
  g.fillStyle = '#f7efe2';
  g.fillRect(0, 88, 128, 6);
  g.fillStyle = '#f2b93c';
  g.beginPath();
  g.arc(26, 70, 9, 0, Math.PI * 2);
  g.fill();
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(0.35, 0.5263); // ~1 tile across the rails
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/** Surfboard: a 2D outline extruded with rounded rails. */
function makeSurfboard() {
  const s = new THREE.Shape();
  s.moveTo(-3.15, 0);
  s.bezierCurveTo(-2.5, 0.8, -1.5, 0.95, -0.65, 0.95);
  s.bezierCurveTo(-0.2, 0.8, 1.15, 0.5, 2.35, 0.22);
  s.bezierCurveTo(3.0, 0.07, 3.35, 0.01, 3.4, 0.0);
  s.bezierCurveTo(3.35, -0.02, 3.0, -0.08, 2.35, -0.22);
  s.bezierCurveTo(1.15, -0.5, -0.2, -0.8, -0.65, -0.95);
  s.bezierCurveTo(-1.5, -0.95, -2.5, -0.8, -3.15, 0.0);

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.28,
    bevelEnabled: true,
    bevelThickness: 0.1,
    bevelSize: 0.14,
    bevelSegments: 4,
    steps: 1,
  });
  geo.translate(0.12, 0, -0.14); // centre the outline, centre the thickness
  geo.rotateX(-Math.PI / 2); // lay flat: X = forward, Z = rail, Y = up
  geo.scale(1, 1.35, 0.9); // a little extra thickness under the feet

  return new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({
      map: makeBoardTexture(),
      roughness: 0.32,
      metalness: 0.08,
    }),
  );
}

/** Wing plan-form: leading/trailing edge are linear along the span. */
const WING_PROFILE = [
  [0.0, 0.0, 0.0],
  [0.45, 0.15, -0.4],
  [1.1, 0.32, -0.66],
  [1.85, 0.44, -0.63],
  [2.45, 0.43, -0.5],
  [2.95, 0.33, -0.31],
  [3.45, 0.15, -0.07],
];

function wingEdgeAt(x) {
  const p = WING_PROFILE;
  if (x <= p[0][0]) return [p[0][1], p[0][2]];
  const last = p[p.length - 1];
  if (x >= last[0]) return [last[1], last[2]];
  for (let i = 0; i < p.length - 1; i++) {
    if (x >= p[i][0] && x <= p[i + 1][0]) {
      const t = (x - p[i][0]) / (p[i + 1][0] - p[i][0]);
      return [lerp(p[i][1], p[i + 1][1], t), lerp(p[i][2], p[i + 1][2], t)];
    }
  }
  return [0, 0];
}

/** Wing membrane for a span slice [x0 .. x1]: span on local +Z, chord +X, thickness +Y. */
function makeWingGeometry(x0, x1, samples = 10) {
  const s = new THREE.Shape();
  for (let i = 0; i <= samples; i++) {
    const x = lerp(x0, x1, i / samples);
    const [lead] = wingEdgeAt(x);
    if (i === 0) s.moveTo(x, lead);
    else s.lineTo(x, lead);
  }
  for (let i = samples; i >= 0; i--) {
    const x = lerp(x0, x1, i / samples);
    const [, trail] = wingEdgeAt(x);
    s.lineTo(x, trail);
  }
  s.closePath();

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.04,
    bevelSegments: 2,
    steps: 1,
  });
  geo.translate(0, 0, -0.035);
  geo.rotateX(-Math.PI / 2); // span -> X, chord -> Z, thickness -> Y
  geo.rotateY(-Math.PI / 2); // span -> +Z, chord -> +X, thickness -> Y
  return geo;
}

function buildPelican() {
  // outer group: rides the wave --------------------------------------------
  const ride = new THREE.Group();

  const board = makeSurfboard();
  board.position.y = 0.3;
  ride.add(board);

  const finGeo = new THREE.ConeGeometry(0.22, 0.85, 4);
  finGeo.rotateZ(Math.PI / 2); // point backwards
  finGeo.scale(1, 1, 0.16);
  const fin = new THREE.Mesh(finGeo, FINISH);
  fin.position.set(-2.35, 0.06, 0);
  ride.add(fin);

  // pelican body group (stands on the deck, does the bobbing) ---------------
  const body = new THREE.Group();
  body.position.y = 0.46; // deck level
  ride.add(body);

  // pear-shaped body: three overlapping spheres give a tapered silhouette
  const torso = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), FEATHER);
  torso.scale.set(1.72, 1.02, 1.05);
  torso.position.set(0, 1.04, 0);
  body.add(torso);

  const chest = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), FEATHER);
  chest.scale.set(0.8, 0.74, 0.82);
  chest.position.set(1.16, 1.0, 0);
  body.add(chest);

  const rump = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 16), FEATHER);
  rump.scale.set(0.68, 0.62, 0.74);
  rump.position.set(-1.3, 0.94, 0);
  body.add(rump);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 16), FEATHER_WING);
  belly.scale.set(1.5, 0.6, 0.98);
  belly.position.set(0.3, 0.84, 0);
  body.add(belly);

  const tailGeo = new THREE.ConeGeometry(0.62, 1.5, 6);
  tailGeo.rotateZ(Math.PI * 0.46);
  tailGeo.scale(1, 1, 0.4);
  const tail = new THREE.Mesh(tailGeo, FEATHER);
  tail.position.set(-1.62, 1.5, 0);
  body.add(tail);

  // neck: a thick pelican S-curve, held high
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.95, 1.72, 0.0),
    new THREE.Vector3(1.55, 2.15, 0.02),
    new THREE.Vector3(2.08, 2.24, 0.05),
    new THREE.Vector3(2.44, 2.12, 0.06),
  ]);
  const neck = new THREE.Mesh(
    new THREE.TubeGeometry(neckCurve, 26, 0.3, 12, false),
    FEATHER,
  );
  body.add(neck);

  // head
  const head = new THREE.Group();
  head.position.set(2.52, 2.08, 0.06);
  body.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 18), FEATHER);
  skull.scale.set(0.92, 0.95, 1.0);
  head.add(skull);

  const crest = new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 12), FEATHER);
  crest.scale.set(0.7, 0.55, 1.6);
  crest.position.set(-0.28, 0.3, 0);
  head.add(crest);

  // beak: long upper mandible, hanging pouch, thin lower mandible
  const upperGeo = new THREE.ConeGeometry(0.34, 1.55, 10);
  upperGeo.rotateZ(-Math.PI / 2);
  upperGeo.scale(1, 0.42, 1);
  const upper = new THREE.Mesh(upperGeo, BEAK);
  upper.position.set(1.16, 0.06, 0);
  head.add(upper);

  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.44, 20, 14), POUCH);
  pouch.scale.set(1.3, 0.95, 0.72);
  pouch.position.set(0.78, -0.16, 0);
  head.add(pouch);

  const lowerGeo = new THREE.ConeGeometry(0.2, 1.35, 8);
  lowerGeo.rotateZ(-Math.PI / 2);
  lowerGeo.scale(1, 0.34, 0.72);
  const lower = new THREE.Mesh(lowerGeo, BEAK);
  lower.position.set(0.95, -0.28, 0);
  head.add(lower);

  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.095, 12, 10), EYE);
    eye.position.set(0.16, 0.22, side * 0.4);
    head.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.032, 8, 6), SPARK);
    glint.position.set(0.22, 0.29, side * 0.45);
    head.add(glint);
  }

  // wings — spread wide for balance while carving
  const wingL = new THREE.Group();
  const wingR = new THREE.Group();
  wingL.position.set(0.15, 1.86, 0.5);
  wingR.position.set(0.15, 1.86, -0.5);
  wingL.add(new THREE.Mesh(makeWingGeometry(0, 3.45), FEATHER_WING));
  wingR.add(new THREE.Mesh(makeWingGeometry(0, 3.45).scale(1, 1, -1), FEATHER_WING));

  const tipL = new THREE.Mesh(makeWingGeometry(2.5, 3.45), FEATHER_TIP);
  tipL.position.y = 0.014; // painted just above the membrane
  const tipR = new THREE.Mesh(makeWingGeometry(2.5, 3.45).scale(1, 1, -1), FEATHER_TIP);
  tipR.position.y = 0.014;
  wingL.add(tipL);
  wingR.add(tipR);
  body.add(wingL, wingR);

  // legs + webbed feet planted on the deck
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.09, 0.55, 8), FOOT);
    leg.position.set(0.05, 0.3, side * 0.5);
    body.add(leg);
    const footGeo = new THREE.ConeGeometry(0.32, 0.34, 10);
    footGeo.rotateX(Math.PI / 2);
    footGeo.scale(1, 1, 0.45);
    const foot = new THREE.Mesh(footGeo, FOOT);
    foot.position.set(0.18, 0.08, side * 0.62);
    foot.rotation.y = side * 0.35;
    body.add(foot);
  }

  return { ride, body, head, wingL, wingR, board, fin };
}

const pelican = buildPelican();
scene.add(pelican.ride);

/* --------------------------------------------------------------- 7. spray */
const SPRAY_MAX = 360;
const sprayPos = new Float32Array(SPRAY_MAX * 3);
const sprayAlpha = new Float32Array(SPRAY_MAX);
const spraySize = new Float32Array(SPRAY_MAX);
const sprayVel = new Float32Array(SPRAY_MAX * 3);
const sprayLife = new Float32Array(SPRAY_MAX);
const sprayMaxLife = new Float32Array(SPRAY_MAX);
let sprayCursor = 0;

const sprayGeo = new THREE.BufferGeometry();
sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPos, 3));
sprayGeo.setAttribute('aAlpha', new THREE.BufferAttribute(sprayAlpha, 1));
sprayGeo.setAttribute('aSize', new THREE.BufferAttribute(spraySize, 1));
sprayGeo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

const spray = new THREE.Points(
  sprayGeo,
  new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    uniforms: { uColor: { value: new THREE.Color('#ffe9cf') } },
    vertexShader: /* glsl */ `
      attribute float aAlpha;
      attribute float aSize;
      varying float vA;
      void main() {
        vA = aAlpha;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aSize * (190.0 / max(-mv.z, 0.001));
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor;
      varying float vA;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5)) * 2.0;
        gl_FragColor = vec4(uColor, smoothstep(1.0, 0.12, d) * vA);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  }),
);
spray.frustumCulled = false;
scene.add(spray);

const _sp = new THREE.Vector3();
function emitSpray(worldPos, dirX, dirZ, count, power) {
  for (let i = 0; i < count; i++) {
    const idx = sprayCursor;
    sprayCursor = (sprayCursor + 1) % SPRAY_MAX;
    const i3 = idx * 3;
    sprayPos[i3] = worldPos.x + rand(-0.25, 0.25);
    sprayPos[i3 + 1] = worldPos.y + rand(-0.05, 0.2);
    sprayPos[i3 + 2] = worldPos.z + rand(-0.25, 0.25);
    sprayVel[i3] = -dirX * rand(1.5, 5.5) * power + rand(-1.2, 1.2);
    sprayVel[i3 + 1] = rand(1.2, 4.4) * power;
    sprayVel[i3 + 2] = -dirZ * rand(1.5, 5.5) * power + rand(-1.2, 1.2);
    const life = rand(0.7, 1.5);
    sprayLife[idx] = life;
    sprayMaxLife[idx] = life;
    spraySize[idx] = rand(0.7, 2.3) * power;
    sprayAlpha[idx] = rand(0.35, 0.85);
  }
}

function updateSpray(dt) {
  for (let i = 0; i < SPRAY_MAX; i++) {
    if (sprayLife[i] <= 0) {
      sprayAlpha[i] = 0;
      continue;
    }
    sprayLife[i] -= dt;
    const i3 = i * 3;
    sprayVel[i3 + 1] -= 9.0 * dt; // gravity
    sprayPos[i3] += sprayVel[i3] * dt;
    sprayPos[i3 + 1] += sprayVel[i3 + 1] * dt;
    sprayPos[i3 + 2] += sprayVel[i3 + 2] * dt;
    const k = clamp(sprayLife[i] / sprayMaxLife[i], 0, 1);
    sprayAlpha[i] = k * k * 0.9;
    spraySize[i] *= 1 + dt * 0.6;
    if (sprayPos[i3 + 1] < WATER_LEVEL) sprayLife[i] = 0; // kissed the sea
  }
  sprayGeo.attributes.position.needsUpdate = true;
  sprayGeo.attributes.aAlpha.needsUpdate = true;
  sprayGeo.attributes.aSize.needsUpdate = true;
}

/* ------------------------------------------------------- 8. birds + sailboat */
function makeBird() {
  const tilt = new THREE.Group(); // carries the bank
  const bodyGeo = new THREE.SphereGeometry(0.3, 10, 8);
  bodyGeo.scale(3.4, 0.8, 0.8);
  tilt.add(new THREE.Mesh(bodyGeo, DARK_BIRD));

  const wings = [new THREE.Group(), new THREE.Group()];
  wings[0].add(new THREE.Mesh(makeWingGeometry(0, 1.85), DARK_BIRD));
  wings[1].add(new THREE.Mesh(makeWingGeometry(0, 1.85).scale(1, 1, -1), DARK_BIRD));
  tilt.add(wings[0], wings[1]);

  const bird = new THREE.Group();
  bird.add(tilt);
  bird.userData.tilt = tilt;
  bird.userData.wings = wings;
  return bird;
}

const birds = [];
for (let i = 0; i < 6; i++) {
  const b = makeBird();
  b.scale.setScalar(rand(0.7, 1.6));
  b.userData.orbit = {
    r: rand(70, 190),
    h: rand(26, 62),
    cx: rand(-120, 120),
    cz: rand(-120, 140),
    a: rand(0, Math.PI * 2),
    speed: rand(0.1, 0.22) * (Math.random() < 0.5 ? -1 : 1),
    phase: rand(0, 10),
    flap: rand(5.5, 9),
  };
  scene.add(b);
  birds.push(b);
}

const sailboat = (() => {
  const hullGeo = new THREE.SphereGeometry(1, 22, 12, 0, Math.PI * 2, 0, Math.PI * 0.52);
  hullGeo.scale(4.4, 1.5, 1.25);
  const hull = new THREE.Mesh(hullGeo, new THREE.MeshStandardMaterial({
    color: '#e9e2d4', roughness: 0.5,
  }));
  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.07, 0.07, 5.2, 6),
    new THREE.MeshStandardMaterial({ color: '#8a6a44', roughness: 0.7 }),
  );
  mast.position.y = 2.2;
  const sailShape = new THREE.Shape();
  sailShape.moveTo(0, 0);
  sailShape.lineTo(0.08, 3.9);
  sailShape.lineTo(2.2, 0.15);
  sailShape.lineTo(0, 0);
  const sail = new THREE.Mesh(
    new THREE.ExtrudeGeometry(sailShape, { depth: 0.05, bevelEnabled: false }),
    new THREE.MeshStandardMaterial({
      color: '#fdf6ea', roughness: 0.85, side: THREE.DoubleSide,
    }),
  );
  sail.position.set(0.05, 0.5, 0);
  const g = new THREE.Group();
  g.add(hull, mast, sail);
  g.position.set(-180, 0, 210);
  g.rotation.y = 0.7;
  scene.add(g);
  return g;
})();

/* ----------------------------------------------------------- 9. animation */
const ELLIPSE_A = 210;
const ELLIPSE_B = 118;

const rideState = {
  theta: 0,
  speed: 0.115, // radians / second along the circuit
  x: 0,
  z: ELLIPSE_B,
  yaw: 0,
  bank: 0,
  forward: new THREE.Vector3(1, 0, 0),
  normal: new THREE.Vector3(0, 1, 0),
};

const camOffsetLocal = new THREE.Vector3(-13.5, 6.8, 11.8);
const camPosTarget = new THREE.Vector3();
const camLookTarget = new THREE.Vector3();
const camLookSmooth = new THREE.Vector3(0, 3, 40);
const boardQuat = new THREE.Quaternion();
const boardMat = new THREE.Matrix4();
const camOffsetTmp = new THREE.Vector3();
const trimQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), -0.05);
const xAxis = new THREE.Vector3();
const yAxis = new THREE.Vector3();
const zAxis = new THREE.Vector3();
const inward = new THREE.Vector3();

// wing flapping: relaxed soaring with an occasional energetic burst
let flapBurst = 0;
let nextFlap = 3.5;
let flapClock = 0;
let flapRate = 1.6;

const clock = new THREE.Clock();
let elapsed = 0;
let introTime = 0;

function updateRide(t) {
  // position + heading along an oval circuit (always moving forward)
  const th = rideState.theta;
  rideState.x = ELLIPSE_A * Math.sin(th);
  rideState.z = ELLIPSE_B * Math.cos(th);

  const dx = ELLIPSE_A * Math.cos(th);
  const dz = -ELLIPSE_B * Math.sin(th);
  const speed = Math.hypot(dx, dz);
  rideState.forward.set(dx / speed, 0, dz / speed);
  rideState.yaw = Math.atan2(dz, dx);

  // ellipse curvature (closed form) drives the bank angle
  const ddx = -ELLIPSE_A * Math.sin(th);
  const ddz = -ELLIPSE_B * Math.cos(th);
  const cross = dx * ddz - dz * ddx;
  const curvature = Math.abs(cross) / Math.pow(speed, 3);
  rideState.bank = clamp(curvature * 26.0, 0, 0.62);

  const iLen = Math.hypot(ddx, ddz) || 1;
  inward.set(ddx / iLen, 0, ddz / iLen);

  waveNormal(rideState.x, rideState.z, t, rideState.normal);

  // board up = wave normal, tilted toward the inside of the turn
  yAxis.copy(rideState.normal).addScaledVector(inward, Math.tan(rideState.bank)).normalize();
  xAxis.copy(rideState.forward);
  zAxis.crossVectors(xAxis, yAxis);
  if (zAxis.lengthSq() < 1e-6) zAxis.set(0, 0, 1);
  zAxis.normalize();
  yAxis.crossVectors(zAxis, xAxis).normalize(); // re-orthogonalise

  boardQuat.setFromRotationMatrix(boardMat.makeBasis(xAxis, yAxis, zAxis));
  boardQuat.multiply(trimQuat); // a touch of nose-up trim

  pelican.ride.position.set(
    rideState.x,
    waveHeight(rideState.x, rideState.z, t) + 0.42,
    rideState.z,
  );
  pelican.ride.quaternion.copy(boardQuat);
  pelican.ride.updateMatrixWorld(true);
}

function updateCamera(dt, t) {
  // establishing shot: start wide and swing in over the first ~6 seconds
  introTime += dt;
  const intro = smoothstep(1 - introTime / 6);
  const wide = camOffsetTmp.copy(camOffsetLocal).multiplyScalar(1 + intro * 1.1);
  const lateral = intro * Math.sin(t * 0.25) * 9;
  wide.x += lateral;
  wide.y += intro * 4;
  wide.z += lateral * 0.6;

  camPosTarget.copy(wide).applyMatrix4(pelican.ride.matrixWorld);
  camera.position.lerp(camPosTarget, 1 - Math.exp(-3.4 * dt));

  camLookTarget.copy(pelican.ride.position).addScaledVector(rideState.forward, 6);
  camLookTarget.y += 2.6;
  camLookSmooth.lerp(camLookTarget, 1 - Math.exp(-4.5 * dt));

  // subtle handheld float so the shot never feels locked
  camera.position.y += Math.sin(t * 0.9) * 0.16 + Math.sin(t * 2.3) * 0.05;
  camera.position.x += Math.sin(t * 0.53) * 0.18;

  camera.lookAt(camLookSmooth);
}

function updatePelican(t, dt) {
  // bob / crouch
  pelican.body.position.y = 0.46 + Math.sin(t * 2.15) * 0.055 + Math.sin(t * 3.7) * 0.02;
  pelican.body.rotation.z = Math.sin(t * 1.35) * 0.035 - 0.045;
  pelican.body.rotation.x = Math.sin(t * 1.05 + 1.2) * 0.025;

  // wings: soft cruising adjustments plus energetic bursts
  flapClock += dt;
  flapBurst = Math.max(0, flapBurst - dt * 1.15);
  let amp, freq;
  if (flapBurst > 0.05) {
    amp = 0.55 + flapBurst * 0.45;
    freq = flapRate * (2.2 + flapBurst * 2.0);
  } else {
    amp = 0.05 + 0.02 * Math.sin(t * 0.6);
    freq = flapRate * 0.55;
  }
  const flap = Math.sin(flapClock * Math.PI * 2 * freq) * amp;
  pelican.wingL.rotation.x = -flap - 0.12;
  pelican.wingR.rotation.x = flap - 0.12;
  pelican.wingL.rotation.y = 0.06 + flap * 0.12;
  pelican.wingR.rotation.y = -0.06 - flap * 0.12;

  if (flapClock > nextFlap) {
    flapBurst = 1;
    flapClock = 0;
    nextFlap = rand(4.5, 9.5);
    flapRate = rand(1.5, 2.3);
  }

  // head: slow scanning, dipping now and then
  pelican.head.rotation.set(
    Math.sin(t * 0.63 + 2.0) * 0.14 - 0.06,
    Math.sin(t * 0.48) * 0.42 + Math.sin(t * 1.31) * 0.1,
    Math.sin(t * 0.9) * 0.06,
  );
}

function updateSprayEmission(dt) {
  // rooster tail off the tail, plus rail spray while carving
  _sp.set(-2.6, 0.55, 0).applyMatrix4(pelican.ride.matrixWorld);
  emitSpray(_sp, rideState.forward.x, rideState.forward.z, 2, 0.85);

  const carve = clamp(rideState.bank * 1.6, 0.3, 1.5);
  const side = carve > 1 ? 0.8 : 0.45;
  _sp.set(-2.4, 0.4, side).applyMatrix4(pelican.ride.matrixWorld);
  emitSpray(_sp, rideState.forward.x, rideState.forward.z, carve > 1 ? 3 : 1, carve);

  updateSpray(dt);
}

function animate() {
  const dt = Math.min(clock.getDelta(), 1 / 20);
  elapsed += dt;
  const t = elapsed;

  rideState.theta += rideState.speed * dt;
  updateRide(t);
  updatePelican(t, dt);

  // The ocean rides along with the camera in grid-sized steps; waves are
  // sampled in world space, so the surface stays continuous underneath.
  const step = OCEAN_SIZE / OCEAN_SEG;
  ocean.position.set(
    Math.round(camera.position.x / step) * step,
    0,
    Math.round(camera.position.z / step) * step,
  );
  oceanUniforms.uTime.value = t;

  updateCamera(dt, t);
  updateSprayEmission(dt);

  // seagulls
  for (const b of birds) {
    const o = b.userData.orbit;
    o.a += o.speed * dt;
    const x = o.cx + Math.cos(o.a) * o.r;
    const z = o.cz + Math.sin(o.a) * o.r;
    b.position.set(x, o.h + Math.sin(t * 0.6 + o.phase) * 2.5, z);
    const vx = -Math.sin(o.a) * o.speed * 40;
    const vz = Math.cos(o.a) * o.speed * 40;
    b.rotation.y = Math.atan2(-vz, vx); // model forward is +X
    b.userData.tilt.rotation.x = clamp(-o.speed * 2.4, -0.5, 0.5); // bank
    const fl = Math.sin(t * o.flap + o.phase) * 0.6;
    const [wl, wr] = b.userData.wings;
    wl.rotation.x = fl;
    wr.rotation.x = -fl;
  }

  // the distant sailboat rides the swell
  sailboat.position.y = waveHeight(sailboat.position.x, sailboat.position.z, t) - 0.1;
  sailboat.rotation.z = Math.sin(t * 1.3) * 0.05;
  sailboat.rotation.x = Math.sin(t * 0.9 + 1.0) * 0.045;

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / Math.max(1, window.innerHeight);
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
