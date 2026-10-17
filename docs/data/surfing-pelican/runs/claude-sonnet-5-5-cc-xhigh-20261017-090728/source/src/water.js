import * as THREE from "three";
import { NS, REG, buildKeyframes, packKeyframes } from "./profile.js";
import { WAVE, waveGLSL } from "./wavefield.js";
import { SUN_DIR, PALETTE } from "./sky.js";
import { TRAIL_N, TRAIL_LIFE } from "./trail.js";

export const keyframes = buildKeyframes();

const vertexPars = /* glsl */ `
uniform sampler2D uProf0;
uniform sampler2D uProf1;
uniform float uTime;
uniform float uWScale;
uniform float uQMax;
varying vec3 vWPos;
varying vec3 vWN;
varying vec3 vWT;
varying vec3 vWB;
varying vec2 vPat;
varying vec4 vAttr;
${waveGLSL}
#define NS ${NS}
#define IDX_FLOOR ${REG.E}

vec4 profFetch(sampler2D tex, float c, int idx) {
  // quadratic blend through the three keyframes (c = 0, 0.5, 1)
  float x = clamp(c, 0.0, 1.0);
  float w0 = 2.0 * (x - 0.5) * (x - 1.0);
  float w1 = -4.0 * x * (x - 1.0);
  float w2 = 2.0 * x * (x - 0.5);
  return w0 * texelFetch(tex, ivec2(idx, 0), 0) + w1 * texelFetch(tex, ivec2(idx, 1), 0) + w2 * texelFetch(tex, ivec2(idx, 2), 0);
}
vec3 slicePos(float x, int idx) {
  float c, h;
  sliceState(x, uTime, c, h);
  vec4 p = profFetch(uProf0, c, idx);
  float q = clamp(p.x * h * uWScale, -uQMax, uQMax);
  return vec3(x, p.y * h * uWScale, -q);
}
`;

const vertexNormal = /* glsl */ `
#ifdef OCEAN
  vec3 wpos = position;
  vec3 wN = vec3(0.0, 1.0, 0.0);
  vec3 wT = vec3(1.0, 0.0, 0.0);
  vec3 wB = vec3(0.0, 0.0, -1.0);
  vPat = vec2(position.x, -position.z);
  vAttr = vec4(1.0, 0.0, 0.0, 4.0);
#else
  float gx = position.x;
  int gi = int(position.y + 0.5);
  float sc, sh;
  sliceState(gx, uTime, sc, sh);
  vec3 wpos = slicePos(gx, gi);
  vec3 pX1 = slicePos(gx + 0.35, gi);
  vec3 pX0 = slicePos(gx - 0.35, gi);
  vec3 pS1 = slicePos(gx, min(gi + 1, NS - 1));
  vec3 pS0 = slicePos(gx, max(gi - 1, 0));
  vec3 dX = pX1 - pX0;
  vec3 dS = pS1 - pS0;
  vec3 wN = cross(dX, dS);
  float nl = length(wN);
  wN = nl > 1e-6 ? wN / nl : vec3(0.0, 1.0, 0.0);
  vec3 wT = normalize(dX + vec3(1e-5, 0.0, 0.0));
  vec3 wB = normalize(cross(wN, wT));
  vec4 pr0 = profFetch(uProf0, sc, gi);
  vec4 pr1 = profFetch(uProf1, sc, gi);
  vec4 prE = profFetch(uProf0, sc, IDX_FLOOR);
  vPat = vec2(gx, (pr0.z - prE.z) * sh * uWScale);
  vAttr = vec4(clamp(pr0.w, 0.0, 1.0), clamp(pr1.x, 0.0, 1.0), clamp(pr1.y, 0.0, 1.0), pr1.z);
#endif
  vWPos = wpos;
  vWN = wN;
  vWT = wT;
  vWB = wB;
  vec3 objectNormal = wN;
`;

const fragPars = /* glsl */ `
uniform float uTime;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uGlow;
uniform vec3 uFoamCol;
uniform vec3 uHorizon;
uniform vec3 uHorizonCool;
uniform vec3 uSunTint;
uniform vec3 uSunDirW;
uniform float uSpeed;
uniform float uRipple;
uniform float uClimb;
#define TRAIL_N ${TRAIL_N}
#define TRAIL_LIFE ${TRAIL_LIFE.toFixed(2)}
uniform vec4 uTrail[TRAIL_N];
uniform vec4 uTrailBounds;
varying vec3 vWPos;
varying vec3 vWN;
varying vec3 vWT;
varying vec3 vWB;
varying vec2 vPat;
varying vec4 vAttr;

float h21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}
// value noise with analytic derivatives
vec3 noised(vec2 x) {
  vec2 i = floor(x);
  vec2 f = fract(x);
  vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  vec2 du = 30.0 * f * f * (f * (f - 2.0) + 1.0);
  float a = h21(i);
  float b = h21(i + vec2(1.0, 0.0));
  float c = h21(i + vec2(0.0, 1.0));
  float d = h21(i + vec2(1.0, 1.0));
  float k1 = b - a, k2 = c - a, k4 = a - b - c + d;
  return vec3(a + k1 * u.x + k2 * u.y + k4 * u.x * u.y, du * (vec2(k1, k2) + k4 * u.yx));
}
float fbm3(vec2 p) {
  float a = 0.5, s = 0.0;
  mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
  for (int i = 0; i < 3; i++) { s += a * noised(p).x; p = m * p; a *= 0.5; }
  return s * 1.14;
}
// smooth directional ripples: a sum of travelling sine waves (analytic gradient)
vec2 waveGrad(vec2 p, float px, float t) {
  vec2 g = vec2(0.0);
  const float lam[7] = float[7](5.3, 3.1, 1.85, 1.1, 0.66, 0.4, 0.24);
  const float sl[7] = float[7](0.024, 0.03, 0.034, 0.033, 0.029, 0.024, 0.018);
  const float ang[7] = float[7](0.15, -0.55, 0.9, -1.15, 0.45, -0.1, 1.25);
  const float om[7] = float[7](0.249, 0.325, 0.42, 0.545, 0.7, 0.9, 1.16);
  for (int i = 0; i < 7; i++) {
    float k = 6.2831853 / lam[i];
    float fade = 1.0 - smoothstep(0.35, 0.9, k * px);
    vec2 d = vec2(cos(ang[i]), sin(ang[i]));
    float ph = k * dot(d, p) + t * om[i] * 3.0 + float(i) * 1.7;
    g += d * sl[i] * cos(ph) * fade;
  }
  return g;
}
float worley(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  float m = 1.0;
  for (int y = -1; y <= 1; y++) {
    for (int x = -1; x <= 1; x++) {
      vec2 c = vec2(float(x), float(y));
      vec2 o = vec2(h21(i + c), h21(i + c + 17.3));
      vec2 d = c + o - f;
      m = min(m, dot(d, d));
    }
  }
  return sqrt(m);
}
float trailFoam(vec2 q) {
  if (q.x < uTrailBounds.x || q.x > uTrailBounds.y || q.y < uTrailBounds.z || q.y > uTrailBounds.w) return 0.0;
  // samples are sorted oldest first and spread evenly in x: only the ones near this pixel matter
  float x0 = uTrail[0].x;
  float x1 = uTrail[TRAIL_N - 1].x;
  int ic = int(clamp((q.x - x0) / max(x1 - x0, 1e-3), 0.0, 1.0) * float(TRAIL_N - 1));
  float f = 0.0;
  for (int j = -5; j <= 5; j++) {
    int i = ic + j;
    if (i < 0 || i >= TRAIL_N) continue;
    vec4 s = uTrail[i];
    float age = (uTime - s.z) / TRAIL_LIFE;
    if (age < 0.0 || age > 1.0 || s.w <= 0.0) continue;
    float wl = 0.1 + 0.34 * age;   // across the wake
    float wa = 0.42 + 0.5 * age;   // along the wake
    float arm = 0.1 + 0.45 * age;
    vec2 d = q - s.xy;
    vec2 dl = vec2(d.x, d.y - arm);
    vec2 dr = vec2(d.x, d.y + arm);
    float c = exp(-(d.x * d.x / (wa * wa) + d.y * d.y / (wl * wl)));
    float a1 = exp(-(dl.x * dl.x / (wa * wa) + dl.y * dl.y / (wl * wl * 0.8)));
    float a2 = exp(-(dr.x * dr.x / (wa * wa) + dr.y * dr.y / (wl * wl * 0.8)));
    f += (c + 0.5 * (a1 + a2)) * pow(1.0 - age, 1.5) * s.w * 0.45;
  }
  return f;
}
vec3 safeNorm(vec3 v) { return v / max(length(v), 1e-5); }
vec3 hazeColor(vec3 d) {
  float sd = max(dot(d, uSunDirW), 0.0);
  vec2 sdn = normalize(uSunDirW.xz);
  vec3 hor = mix(uHorizonCool, uHorizon, smoothstep(-0.35, 0.95, dot(normalize(d.xz + vec2(1e-5)), sdn)));
  return hor + uSunTint * (pow(sd, 3.0) * 0.16 + pow(sd, 10.0) * 0.2 + pow(sd, 90.0) * 0.45);
}
`;

const fragSurface = /* glsl */ `
  vec3 toEye = cameraPosition - vWPos;
  float dist = length(toEye);
  vec3 V = -toEye / dist;
  vec3 Nw = safeNorm(vWN);
  vec3 Tw = safeNorm(vWT);
  vec3 Bw = safeNorm(vWB);

  float thickness = vAttr.x;
  float aoIn = vAttr.y;
  float foamMask = vAttr.z;

  // pattern coordinates: the sea slides under the pattern and climbs the face
  float xp = vPat.x + uTime * uSpeed;
  float arc = vPat.y;
  vec2 pc = vec2(xp, arc + uTime * uClimb);
  float px = length(fwidth(pc));

  float distFade = 1.0 / (1.0 + dist * 0.01);
  // gentle domain warp so the wave trains do not look like a lattice
  vec2 wp = pc + 0.55 * vec2(sin(pc.y * 0.31 + pc.x * 0.17), sin(pc.x * 0.27 - pc.y * 0.23 + 1.3));
  vec2 gg = waveGrad(wp, px, uTime) * uRipple * distFade;
  Nw = normalize(Nw - (gg.x * Tw + gg.y * Bw));
  normal = normalize((viewMatrix * vec4(Nw, 0.0)).xyz);

  // ---- foam (the expensive noise only runs where there is foam to draw)
  float td = trailFoam(pc);
  float foam = 0.0;
  float lace = 1.0;
  if (foamMask > 0.02 || td > 0.01) {
    float fn = fbm3(pc * vec2(1.3, 1.1) + vec2(0.0, 4.0));
    float fs = fbm3(vec2(xp * 2.4, arc * 0.9 + uTime * 0.6) + 9.0);
    float nz = 0.6 * fn + 0.4 * fs;
    float thr = 1.0 - foamMask * 1.3;
    foam = smoothstep(thr, thr + 0.3, nz + foamMask * 0.2);
    if (td > 0.01) {
      float streak = fbm3(vec2(xp * 1.1, arc * 6.5) + 3.0);
      foam = max(foam, smoothstep(0.1, 0.5, td * (0.3 + 1.2 * streak)));
    }
    // bubbly lace, only worth the cost close to the camera
    lace = mix(0.5, 1.0, smoothstep(0.2, 0.8, fn)) * mix(0.8, 1.0, smoothstep(0.25, 0.75, fs));
    if (dist < 70.0) {
      float bub = worley(pc * vec2(5.5, 4.5) + vec2(2.0, 9.0));
      lace *= mix(0.68, 1.0, smoothstep(0.06, 0.38, bub));
    }
  }
  float fleck = smoothstep(0.8, 0.96, noised(pc * 0.45 + 3.0).x) * 0.5;
  foam = max(foam, fleck * (1.0 - foamMask) * 0.5);
  foam *= 1.0 - smoothstep(250.0, 800.0, dist);

  // ---- body colour: sunlight scattered inside the water, mostly independent of the surface normal
  float thin = clamp(1.0 - thickness, 0.0, 1.0);
  vec3 vol = mix(uDeep, uShallow, 0.1 + 0.9 * pow(thin, 1.25));
  float wrap = clamp(dot(Nw, uSunDirW) * 0.5 + 0.5, 0.0, 1.0);
  vec3 scatter = vol * (0.5 + 0.9 * wrap);
  float sunBack = pow(clamp(dot(V, uSunDirW), 0.0, 1.0), 2.0);
  scatter += uGlow * pow(thin, 1.4) * (0.22 + 1.5 * sunBack);
  scatter *= 1.0 - 0.6 * aoIn;

  // churned water: bright where aerated, bluish in the hollows between the bubbles
  diffuseColor.rgb = mix(vec3(0.5, 0.72, 0.82), uFoamCol, lace) * foam;
  roughnessFactor = mix(0.04 + smoothstep(30.0, 500.0, dist) * 0.25, 0.85, foam);
  vec3 waterGlow = scatter * (1.0 - foam);
`;

const fragFog = /* glsl */ `
  {
    float fogAmt = 1.0 - exp(-pow(dist * 0.0042, 1.25));
    vec3 fogCol = hazeColor(normalize(vec3(V.x, 0.0, V.z)));
    gl_FragColor.rgb = mix(gl_FragColor.rgb, fogCol, fogAmt);
    if (any(isnan(gl_FragColor.rgb)) || any(isinf(gl_FragColor.rgb))) gl_FragColor = vec4(fogCol, 1.0);
  }
`;

export function createWaterMaterials(envMap) {
  const [d0, d1] = packKeyframes(keyframes);
  const mk = (data) => {
    const t = new THREE.DataTexture(data, NS, keyframes.length, THREE.RGBAFormat, THREE.FloatType);
    t.minFilter = t.magFilter = THREE.NearestFilter;
    t.needsUpdate = true;
    return t;
  };
  const shared = {
    uTime: { value: 0 },
    uProf0: { value: mk(d0) },
    uProf1: { value: mk(d1) },
    uWScale: { value: WAVE.scale },
    uQMax: { value: WAVE.qMax },
    uSpeed: { value: WAVE.speed },
    uRipple: { value: 1.0 },
    uClimb: { value: WAVE.climb },
    uTrail: { value: Array.from({ length: TRAIL_N }, () => new THREE.Vector4(0, 0, -1e5, 0)) },
    uTrailBounds: { value: new THREE.Vector4(1, -1, 1, -1) },
    uDeep: { value: new THREE.Color("#0a4d66") },
    uShallow: { value: new THREE.Color("#22b9aa") },
    uGlow: { value: new THREE.Color("#4eeabf").multiplyScalar(0.9) },
    uFoamCol: { value: new THREE.Color("#f2fbff") },
    uHorizon: { value: PALETTE.horizon },
    uHorizonCool: { value: PALETTE.horizonCool },
    uSunTint: { value: PALETTE.sunTint },
    uSunDirW: { value: SUN_DIR },
  };

  const make = (ocean, depthOnly = false) => {
    const m = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.06,
      metalness: 0,
      envMap,
      envMapIntensity: 1.0,
    });
    m.defines = ocean ? { OCEAN: "" } : {};
    if (depthOnly) {
      // depth pre-pass: same displacement, no shading, so the colour pass shades each pixel only once
      m.colorWrite = false;
      m.polygonOffset = true;
      m.polygonOffsetFactor = 1;
      m.polygonOffsetUnits = 1;
    } else if (!ocean) {
      m.depthFunc = THREE.LessEqualDepth;
    }
    m.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, shared);
      shader.vertexShader = shader.vertexShader
        .replace("#include <common>", "#include <common>\n" + vertexPars)
        .replace("#include <beginnormal_vertex>", vertexNormal)
        .replace("#include <begin_vertex>", "vec3 transformed = wpos;");
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", "#include <common>\n" + fragPars)
        .replace("#include <normal_fragment_maps>", fragSurface)
        .replace("#include <emissivemap_fragment>", "#include <emissivemap_fragment>\n totalEmissiveRadiance += waterGlow;")
        .replace("#include <fog_fragment>", fragFog);
      if (depthOnly) shader.fragmentShader = "void main() { gl_FragColor = vec4(0.0); }";
    };
    m.customProgramCacheKey = () => (depthOnly ? "wave-depth" : ocean ? "ocean" : "wave");
    return m;
  };

  return { wave: make(false), waveDepth: make(false, true), ocean: make(true), uniforms: shared };
}

// Wave mesh: a grid over (slice x, profile index) evaluated entirely in the vertex shader.
export function createWaveGeometry() {
  const sideL = 170;
  const sideR = 90;
  const a = 3.5;
  const ex = (s) => (Math.exp(a * s) - 1) / (Math.exp(a) - 1);
  const list = [];
  for (let i = sideL; i >= 1; i--) list.push(WAVE.xMin * ex(i / sideL));
  list.push(0);
  for (let i = 1; i <= sideR; i++) list.push(WAVE.xMax * ex(i / sideR));
  const NX = list.length;
  const pos = new Float32Array(NX * NS * 3);
  for (let i = 0; i < NX; i++) {
    for (let j = 0; j < NS; j++) {
      const o = (i * NS + j) * 3;
      pos[o] = list[i];
      pos[o + 1] = j;
      pos[o + 2] = 0;
    }
  }
  const idx = new Uint32Array((NX - 1) * (NS - 1) * 6);
  let k = 0;
  for (let i = 0; i < NX - 1; i++) {
    for (let j = 0; j < NS - 1; j++) {
      const a0 = i * NS + j;
      const b0 = (i + 1) * NS + j;
      const c0 = i * NS + j + 1;
      const d0 = (i + 1) * NS + j + 1;
      idx[k++] = a0;
      idx[k++] = b0;
      idx[k++] = c0;
      idx[k++] = b0;
      idx[k++] = d0;
      idx[k++] = c0;
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  return g;
}

// Flat sea around the wave mesh (with a hole where the wave mesh lives).
export function createOceanGeometry() {
  const R = 9000;
  const x0 = WAVE.xMin;
  const x1 = WAVE.xMax;
  const z0 = -WAVE.qMax;
  const z1 = WAVE.qMax;
  const quads = [
    [-R, -R, x0, R], // left strip (full height)
    [x1, -R, R, R], // right strip
    [x0, -R, x1, z0], // near strip
    [x0, z1, x1, R], // far strip
  ];
  const pos = []; // counter-clockwise seen from above, so the normals face +Y
  for (const [ax, az, bx, bz] of quads) {
    pos.push(ax, 0, az, ax, 0, bz, bx, 0, az);
    pos.push(bx, 0, az, ax, 0, bz, bx, 0, bz);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  return g;
}
