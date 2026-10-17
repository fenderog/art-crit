// Ocean: a single displaced plane rendered with a custom shader.
// The same wave train is evaluated on the CPU (sampleWater) so the surfer
// rides exactly the GPU-displaced surface.

import * as THREE from 'three';

/**
 * Wave train shared by GPU and CPU.
 * dir   - travel direction (will be normalized), waves travel along +dir
 * amp   - amplitude in metres
 * len   - wavelength in metres
 * speed - phase speed in m/s
 * phase - phase offset
 */
export const WAVES = [
  { dir: [-1.00, 0.12], amp: 1.15, len: 40.0, speed: 6.6, phase: 0.0 },
  { dir: [-0.92, -0.39], amp: 0.58, len: 23.0, speed: 5.4, phase: 1.9 },
  { dir: [-0.52, 0.85], amp: 0.33, len: 13.5, speed: 4.0, phase: 4.2 },
  { dir: [-0.99, 0.42], amp: 0.16, len: 7.4, speed: 3.1, phase: 2.4 },
  { dir: [0.32, 0.95], amp: 0.09, len: 5.0, speed: 2.5, phase: 5.6 },
];

for (const w of WAVES) {
  const l = Math.hypot(w.dir[0], w.dir[1]) || 1;
  w.dir[0] /= l;
  w.dir[1] /= l;
}

const TAU = Math.PI * 2;

/** Height of the water surface at (x, z) and time t. */
export function waterHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    const k = TAU / w.len;
    h += w.amp * Math.sin(k * (w.dir[0] * x + w.dir[1] * z) - w.speed * k * t + w.phase);
  }
  return h;
}

/** Height and analytic slope of the water surface at (x, z) and time t. */
export function sampleWater(x, z, t) {
  let h = 0;
  let sx = 0;
  let sz = 0;
  for (const w of WAVES) {
    const k = TAU / w.len;
    const ph = k * (w.dir[0] * x + w.dir[1] * z) - w.speed * k * t + w.phase;
    h += w.amp * Math.sin(ph);
    const c = w.amp * k * Math.cos(ph);
    sx += c * w.dir[0];
    sz += c * w.dir[1];
  }
  return { height: h, slopeX: sx, slopeZ: sz };
}

const VERTEX = /* glsl */ `
  uniform float uTime;
  uniform vec2 uWaveDir[5];
  uniform vec4 uWave[5]; // amp, wavelength, speed, phase

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vHeight;
  varying vec2 vXZ;

  void main() {
    vec3 pos = position;
    float h = 0.0;
    vec2 slope = vec2(0.0);

    for (int i = 0; i < 5; i++) {
      vec2 d = uWaveDir[i];
      float A = uWave[i].x;
      float L = uWave[i].y;
      float S = uWave[i].z;
      float P = uWave[i].w;
      float k = 6.28318530718 / L;
      float phase = k * dot(d, pos.xz) - S * k * uTime + P;
      h += A * sin(phase);
      slope += A * k * d * cos(phase);
    }

    pos.y += h;

    vec4 world = modelMatrix * vec4(pos, 1.0);
    vWorldPos = world.xyz;
    vNormal = normalize(vec3(-slope.x, 1.0, -slope.y));
    vHeight = h;
    vXZ = pos.xz;

    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const FRAGMENT = /* glsl */ `
  precision highp float;

  uniform float uTime;
  uniform vec3 uSunDir;
  uniform vec3 uDeepColor;
  uniform vec3 uShallowColor;
  uniform vec3 uSkyColor;
  uniform vec3 uHorizonColor;
  uniform vec3 uFoamColor;
  uniform vec3 uFogColor;
  uniform float uFogDensity;

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vHeight;
  varying vec2 vXZ;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 4; i++) {
      v += a * vnoise(p);
      p = p * 2.03 + vec2(11.7, 7.3);
      a *= 0.5;
    }
    return v;
  }

  void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(cameraPosition - vWorldPos);
    vec3 L = normalize(uSunDir);

    float facing = clamp(dot(N, V), 0.0, 1.0);

    // Water body colour: deep troughs, translucent teal faces, glowing crests.
    vec3 water = mix(uDeepColor, uShallowColor, smoothstep(-1.7, 1.9, vHeight));
    water = mix(water, uShallowColor * 1.25, smoothstep(0.7, 2.0, vHeight) * 0.35);

    // Sky reflection.
    vec3 R = reflect(-V, N);
    vec3 sky = mix(uHorizonColor, uSkyColor, clamp(R.y * 1.15, 0.0, 1.0));
    float fres = pow(1.0 - facing, 4.0);
    vec3 col = mix(water, sky, clamp(fres * 1.1, 0.0, 1.0));

    // Sun glints dancing on the faces.
    vec3 H = normalize(L + V);
    float ndh = max(dot(N, H), 0.0);
    float glint = pow(ndh, 380.0) * 2.2 + pow(ndh, 48.0) * 0.28;
    float sparkle = fbm(vXZ * 2.7 + vec2(uTime * 1.5, uTime * 0.9));
    col += vec3(1.0, 0.93, 0.80) * glint * (0.55 + 0.95 * sparkle);

    // Foam on breaking crests and steep faces.
    float n = fbm(vXZ * 0.5 + vec2(uTime * 0.5, uTime * 0.22));
    float steep = length(N.xz);
    float crest = smoothstep(1.5, 2.4, vHeight + n * 0.45);
    float faceFoam = smoothstep(0.16, 0.34, steep) * smoothstep(0.3, 1.2, vHeight) * 0.35;
    float foam = clamp(crest + faceFoam * n, 0.0, 1.0);
    col = mix(col, uFoamColor, foam * 0.9);

    // Exponential-squared distance haze matching the sky at the horizon.
    float d = length(cameraPosition - vWorldPos);
    float fog = 1.0 - exp(-uFogDensity * uFogDensity * d * d);
    col = mix(col, uFogColor, fog);

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function createOcean({ sunDir, fogColor, fogDensity }) {
  const geometry = new THREE.PlaneGeometry(420, 420, 256, 256);
  geometry.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uWaveDir: { value: WAVES.map((w) => new THREE.Vector2(w.dir[0], w.dir[1])) },
    uWave: { value: WAVES.map((w) => new THREE.Vector4(w.amp, w.len, w.speed, w.phase)) },
    uSunDir: { value: sunDir.clone() },
    uDeepColor: { value: new THREE.Color(0x0f4f6c) },
    uShallowColor: { value: new THREE.Color(0x27a3b2) },
    uSkyColor: { value: new THREE.Color(0x86b6e0) },
    uHorizonColor: { value: new THREE.Color(0xe8dfd2) },
    uFoamColor: { value: new THREE.Color(0xf6fbff) },
    uFogColor: { value: fogColor.clone() },
    uFogDensity: { value: fogDensity },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: VERTEX,
    fragmentShader: FRAGMENT,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  return {
    mesh,
    material,
    update(t) {
      uniforms.uTime.value = t;
    },
  };
}
