import * as THREE from 'three';

const RAW_WAVES = [
  { dir: [0.82, 0.57], amp: 0.58, len: 32.0, phase: 0.4, speed: 0.9 },
  { dir: [-0.38, 0.925], amp: 0.32, len: 18.0, phase: 2.2, speed: 1.05 },
  { dir: [0.97, -0.24], amp: 0.16, len: 10.5, phase: 4.1, speed: 1.15 },
  { dir: [0.15, 0.99], amp: 0.085, len: 6.6, phase: 1.1, speed: 1.3 },
];

export const WAVES = RAW_WAVES.map((w) => {
  const len = Math.hypot(w.dir[0], w.dir[1]);
  const dx = w.dir[0] / len;
  const dz = w.dir[1] / len;
  const k = (Math.PI * 2) / w.len;
  return {
    dx,
    dz,
    amp: w.amp,
    k,
    omega: w.speed * Math.sqrt(9.81 * k),
    phase: w.phase,
  };
});

const f = (n) => n.toFixed(5);

const WAVE_GLSL = `
float waveHeight(vec2 p, float t) {
  float h = 0.0;
${WAVES.map(
  (w) =>
    `  h += ${f(w.amp)} * sin(dot(vec2(${f(w.dx)}, ${f(w.dz)}), p) * ${f(w.k)} - ${f(w.omega)} * t + ${f(w.phase)});`
).join('\n')}
  return h;
}

vec2 waveGrad(vec2 p, float t) {
  vec2 g = vec2(0.0);
${WAVES.map(
  (w) =>
    `  g += ${f(w.amp * w.k)} * vec2(${f(w.dx)}, ${f(w.dz)}) * cos(dot(vec2(${f(w.dx)}, ${f(w.dz)}), p) * ${f(w.k)} - ${f(w.omega)} * t + ${f(w.phase)});`
).join('\n')}
  return g;
}
`;

/** Analytic water height and gradient, shared with the board's motion. */
export function sampleOcean(x, z, t) {
  let height = 0;
  let dx = 0;
  let dz = 0;
  for (const w of WAVES) {
    const phase = w.k * (w.dx * x + w.dz * z) - w.omega * t + w.phase;
    height += w.amp * Math.sin(phase);
    const c = w.amp * w.k * Math.cos(phase);
    dx += c * w.dx;
    dz += c * w.dz;
  }
  return { height, dx, dz };
}

const vertexShader = /* glsl */ `
uniform float uTime;
uniform vec2 uOffset;

varying vec3 vWorldPos;
varying vec3 vNormalW;
varying float vHeight;
varying vec2 vWorldXZ;

${WAVE_GLSL}

void main() {
  vec2 wxz = position.xz + uOffset;
  float h = waveHeight(wxz, uTime);
  vec2 g = waveGrad(wxz, uTime);

  vec3 worldPos = vec3(wxz.x, h, wxz.y);
  vWorldPos = worldPos;
  vNormalW = normalize(vec3(-g.x, 1.0, -g.y));
  vHeight = h;
  vWorldXZ = wxz;

  gl_Position = projectionMatrix * viewMatrix * vec4(worldPos, 1.0);
}
`;

const fragmentShader = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uCrest;
uniform vec3 uHorizonFog;
uniform vec3 uSkyZenith;
uniform vec3 uSkyHorizon;

varying vec3 vWorldPos;
varying vec3 vNormalW;
varying float vHeight;
varying vec2 vWorldXZ;

float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

float vnoise(vec2 p) {
  vec2 i = floor(p);
  vec2 fr = fract(p);
  fr = fr * fr * (3.0 - 2.0 * fr);
  float a = hash21(i);
  float b = hash21(i + vec2(1.0, 0.0));
  float c = hash21(i + vec2(0.0, 1.0));
  float d = hash21(i + vec2(1.0, 1.0));
  return mix(mix(a, b, fr.x), mix(c, d, fr.x), fr.y);
}

float fbm(vec2 p) {
  float v = 0.0;
  float a = 0.5;
  for (int i = 0; i < 4; i++) {
    v += a * vnoise(p);
    p = p * 2.03 + vec2(1.7, 9.2);
    a *= 0.5;
  }
  return v;
}

void main() {
  vec3 N = normalize(vNormalW);

  // Small, shimmering ripples on top of the long swell.
  vec2 q = vWorldXZ * 0.5 + vec2(uTime * 0.16, -uTime * 0.11);
  float e = 0.09;
  float n0 = fbm(q);
  float nx = fbm(q + vec2(e, 0.0));
  float nz = fbm(q + vec2(0.0, e));
  N = normalize(N + vec3(-(nx - n0), 0.0, -(nz - n0)) * 1.6);

  vec3 V = normalize(cameraPosition - vWorldPos);
  vec3 L = normalize(uSunDir);
  vec3 R = reflect(-V, N);

  float fresnel = 0.02 + 0.98 * pow(1.0 - max(dot(N, V), 0.0), 5.0);
  fresnel = clamp(fresnel * 1.15, 0.0, 1.0);

  // Water body colour, warming as the swell rises toward the light.
  float depthMix = smoothstep(-0.75, 0.9, vHeight);
  vec3 base = mix(uDeep, uShallow, depthMix);
  float scatter = pow(max(dot(N, L), 0.0), 3.0) * smoothstep(-0.1, 0.9, vHeight);
  base += uCrest * scatter * 0.22;

  // Reflected sunset.
  vec3 skyRef = mix(uSkyHorizon, uSkyZenith, smoothstep(-0.04, 0.62, R.y));
  skyRef = mix(skyRef, vec3(1.0, 0.67, 0.4), exp(-max(R.y, 0.0) * 7.0) * 0.3);
  float sunAlign = max(dot(R, L), 0.0);
  skyRef += uSunColor * pow(sunAlign, 10.0) * 0.55;

  float spec = pow(sunAlign, 340.0) * 5.0 + pow(sunAlign, 70.0) * 0.35;
  float sparkle = smoothstep(0.5, 0.95, vnoise(vWorldXZ * 6.5 + vec2(uTime * 1.6, -uTime * 1.25)));
  spec *= 0.5 + 1.1 * sparkle;

  vec3 col = mix(base, skyRef, fresnel * 0.8);
  col += uSunColor * spec;

  // Whitecaps and thin foam streaks.
  float foamNoise = fbm(vWorldXZ * 0.65 + vec2(uTime * 0.06, -uTime * 0.04));
  float crest = smoothstep(0.38, 0.92, vHeight + (foamNoise - 0.5) * 0.55);
  float streak = smoothstep(0.32, 0.82, fbm(vWorldXZ * 1.7 + vec2(0.0, uTime * 0.16)));
  float foam = crest * (0.18 + 0.82 * streak);
  foam += smoothstep(0.83, 0.98, streak) * smoothstep(0.0, 0.55, vHeight) * 0.28;
  foam = clamp(foam, 0.0, 1.0);
  col = mix(col, vec3(0.93, 0.985, 0.98), foam * 0.78);

  // Aerial haze toward the horizon.
  float dist = length(cameraPosition - vWorldPos);
  float fogF = 1.0 - exp(-dist * 0.0046);
  fogF = clamp(fogF, 0.0, 1.0);
  col = mix(col, uHorizonFog, fogF);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean() {
  const size = 700;
  const segments = 420;
  const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
  geometry.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uOffset: { value: new THREE.Vector2() },
    uSunDir: { value: new THREE.Vector3(-0.86, 0.115, -0.34).normalize() },
    uSunColor: { value: new THREE.Color(0xffd096) },
    uDeep: { value: new THREE.Color(0x062f3b) },
    uShallow: { value: new THREE.Color(0x0b636b) },
    uCrest: { value: new THREE.Color(0x8fe2cf) },
    uHorizonFog: { value: new THREE.Color(0xf6bd8f) },
    uSkyZenith: { value: new THREE.Color(0x1c3a68) },
    uSkyHorizon: { value: new THREE.Color(0xffbf88) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    side: THREE.FrontSide,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = -1;

  const cell = size / segments;

  return {
    mesh,
    uniforms,
    update(time, focus) {
      uniforms.uTime.value = time;
      mesh.position.x = Math.round(focus.x / cell) * cell;
      mesh.position.z = Math.round(focus.z / cell) * cell;
      uniforms.uOffset.value.set(mesh.position.x, mesh.position.z);
    },
  };
}
