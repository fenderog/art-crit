import * as THREE from "three";

const TAU = Math.PI * 2;

// Primary wave (index 0) runs along +z: phase = k*z - w*t, crest at π/2.
// The surfer locks that phase and travels +x along the face. Other waves are chop.
// dir vectors are normalized below. Keep this list in sync with waveH() in the shader
// by passing the same values as uniforms — do not duplicate the numbers in GLSL.
const RAW = [
  { amp: 1.38, k: 0.232, w: 0.46, peak: 1.7, dir: [0, 1] },
  { amp: 0.16, k: 0.085, w: 0.15, peak: 1.0, dir: [1, 0.08] },
  { amp: 0.11, k: 0.54, w: 1.05, peak: 1.0, dir: [0.28, 0.96] },
  { amp: 0.04, k: 1.35, w: 1.9, peak: 1.0, dir: [-0.62, 0.78] },
];

function unit2(x, z) {
  const l = Math.hypot(x, z) || 1;
  return [x / l, z / l];
}

const dirs = RAW.map((w) => unit2(w.dir[0], w.dir[1]));

export const WAVES = {
  amp: RAW.map((w) => w.amp),
  k: RAW.map((w) => w.k),
  w: RAW.map((w) => w.w),
  peak: RAW.map((w) => w.peak),
  dirX: dirs.map((d) => d[0]),
  dirZ: dirs.map((d) => d[1]),
};

export function wrap(n, m) {
  return ((n % m) + m) % m;
}

/** Phase of wave i at world (x, z), reduced so large coordinates stay accurate. */
export function wavePhase(i, x, z, t) {
  const k = WAVES.k[i];
  const w = WAVES.w[i];
  const proj = WAVES.dirX[i] * x + WAVES.dirZ[i] * z;
  const projW = wrap(proj, TAU / k);
  const tW = wrap(t, TAU / w);
  return k * projW - w * tW;
}

function peaky(phase, peak) {
  const s = Math.sin(phase);
  return Math.sign(s) * Math.abs(s) ** peak;
}

export function heightAt(x, z, t) {
  let h = 0;
  for (let i = 0; i < RAW.length; i++) {
    h += WAVES.amp[i] * peaky(wavePhase(i, x, z, t), WAVES.peak[i]);
  }
  return h;
}

// Finite difference matches the shader: n = normalize(h - h(x+e), e, h - h(z+e)).
export function surfaceNormal(x, z, t, target) {
  const e = 0.22;
  const h = heightAt(x, z, t);
  const hx = heightAt(x + e, z, t);
  const hz = heightAt(x, z + e, t);
  return target.set(h - hx, e, h - hz).normalize();
}

export const HORIZON = new THREE.Color(0xf19a64);

export function createWater() {
  const SIZE = 120;
  const SEG = 240;
  const geo = new THREE.PlaneGeometry(SIZE, SIZE, SEG, SEG);
  geo.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uAmp: { value: new THREE.Vector4(...WAVES.amp) },
    uK: { value: new THREE.Vector4(...WAVES.k) },
    uW: { value: new THREE.Vector4(...WAVES.w) },
    uPeak: { value: new THREE.Vector4(...WAVES.peak) },
    uDirX: { value: new THREE.Vector4(...WAVES.dirX) },
    uDirZ: { value: new THREE.Vector4(...WAVES.dirZ) },
    uSunDir: { value: new THREE.Vector3() },
    uHorizon: { value: HORIZON.clone() },
    uTrail: {
      value: Array.from({ length: TRAIL_N }, () => new THREE.Vector2(1e4, 1e4)),
    },
  };

  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: WATER_VERT,
    fragmentShader: WATER_FRAG,
    toneMapped: true,
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  return { mesh, uniforms, tile: SIZE / SEG };
}

export const TRAIL_N = 28;

const WATER_VERT = /* glsl */ `
uniform float uTime;
uniform vec4 uAmp;
uniform vec4 uK;
uniform vec4 uW;
uniform vec4 uPeak;
uniform vec4 uDirX;
uniform vec4 uDirZ;
uniform vec2 uTrail[${TRAIL_N}];

varying vec3 vNormal;
varying vec3 vWorld;
varying float vFoam;
varying float vHeight;

float waveH(vec2 xz, float amp, float k, float w, float peak, float dx, float dz) {
  float proj = dx * xz.x + dz * xz.y;
  float lambda = 6.28318530718 / k;
  float period = 6.28318530718 / w;
  proj = mod(mod(proj, lambda) + lambda, lambda);
  float tw = mod(mod(uTime, period) + period, period);
  float p = k * proj - w * tw;
  float s = sin(p);
  return amp * sign(s) * pow(abs(s), peak);
}

float heightAt(vec2 xz) {
  return waveH(xz, uAmp.x, uK.x, uW.x, uPeak.x, uDirX.x, uDirZ.x)
       + waveH(xz, uAmp.y, uK.y, uW.y, uPeak.y, uDirX.y, uDirZ.y)
       + waveH(xz, uAmp.z, uK.z, uW.z, uPeak.z, uDirX.z, uDirZ.z)
       + waveH(xz, uAmp.w, uK.w, uW.w, uPeak.w, uDirX.w, uDirZ.w);
}

float distToSeg(vec2 p, vec2 a, vec2 b) {
  vec2 ab = b - a;
  float denom = dot(ab, ab);
  float t = denom < 1e-4 ? 0.0 : clamp(dot(p - a, ab) / denom, 0.0, 1.0);
  return length(p - (a + ab * t));
}

void main() {
  vec4 world0 = modelMatrix * vec4(position, 1.0);
  vec2 xz = world0.xz;
  float h = heightAt(xz);
  float e = 0.22;
  float hx = heightAt(xz + vec2(e, 0.0));
  float hz = heightAt(xz + vec2(0.0, e));
  vec3 n = normalize(vec3(h - hx, e, h - hz));
  float dhdx = (hx - h) / e;
  float dhdz = (hz - h) / e;
  float slope = length(vec2(dhdx, dhdz));

  float crest = smoothstep(0.78, 1.28, h);
  float lip = crest * smoothstep(0.08, 0.42, slope);

  float wake = 0.0;
  for (int i = 1; i < ${TRAIL_N}; i++) {
    float d = distToSeg(xz, uTrail[i - 1], uTrail[i]);
    float age = float(i) / float(${TRAIL_N - 1});
    float width = mix(0.55, 2.4, age);
    float band = (1.0 - age) * (1.0 - smoothstep(0.15, width, d));
    wake = max(wake, band);
  }

  vec3 pos = position;
  pos.y = h;
  vec4 world = modelMatrix * vec4(pos, 1.0);
  vWorld = world.xyz;
  vNormal = normalize(mat3(modelMatrix) * n);
  vHeight = h;
  vFoam = clamp(lip * 0.9 + wake * 0.8, 0.0, 1.0);
  gl_Position = projectionMatrix * viewMatrix * world;
}
`;

const WATER_FRAG = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uHorizon;

varying vec3 vNormal;
varying vec3 vWorld;
varying float vFoam;
varying float vHeight;

void main() {
  vec3 N = normalize(vNormal);
  vec3 V = normalize(cameraPosition - vWorld);
  vec3 L = normalize(uSunDir);
  float ndl = max(dot(N, L), 0.0);
  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.5);
  float spec = pow(max(dot(reflect(-L, N), V), 0.0), 90.0);
  float glint = pow(max(dot(reflect(-L, N), V), 0.0), 280.0);

  vec3 deep = vec3(0.012, 0.075, 0.13);
  vec3 midC = vec3(0.02, 0.30, 0.40);
  vec3 face = vec3(0.16, 0.55, 0.56);
  float h01 = clamp(vHeight * 0.32 + 0.48, 0.0, 1.0);
  vec3 col = mix(deep, midC, smoothstep(0.05, 0.72, h01));
  col = mix(col, face, ndl * 0.62);
  col += vec3(1.0, 0.78, 0.55) * pow(ndl, 1.4) * 0.18;
  col += vec3(0.05, 0.1, 0.12) * (1.0 - ndl) * 0.35;
  col += vec3(1.0, 0.94, 0.82) * spec * 0.75;
  col += vec3(1.0, 0.98, 0.95) * glint * 0.55;
  col += mix(vec3(0.35, 0.55, 0.6), vec3(1.0, 0.72, 0.5), 0.55) * fres * 0.28;

  vec3 foam = vec3(0.95, 0.93, 0.89);
  col = mix(col, foam, clamp(vFoam, 0.0, 1.0));
  col += vec3(1.0, 0.97, 0.92) * clamp(vFoam, 0.0, 1.0) * spec * 0.35;

  float dist = length(cameraPosition - vWorld);
  float fog = smoothstep(32.0, 88.0, dist);
  col = mix(col, uHorizon, fog);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSky() {
  const geo = new THREE.SphereGeometry(380, 32, 20);
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uSunDir: { value: new THREE.Vector3() },
      uHorizon: { value: HORIZON.clone() },
    },
    side: THREE.BackSide,
    depthWrite: false,
    toneMapped: true,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        vDir = world.xyz - cameraPosition;
        gl_Position = projectionMatrix * viewMatrix * world;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir;
      uniform vec3 uHorizon;
      varying vec3 vDir;
      void main() {
        vec3 dir = normalize(vDir);
        float h = dir.y;
        vec3 zenith = vec3(0.23, 0.46, 0.78);
        vec3 high = vec3(0.53, 0.72, 0.90);
        vec3 horizon = uHorizon;
        vec3 below = vec3(0.86, 0.38, 0.26);
        vec3 col = mix(below, horizon, smoothstep(-0.15, 0.04, h));
        col = mix(col, high, smoothstep(0.0, 0.38, h));
        col = mix(col, zenith, smoothstep(0.28, 0.9, h));
        float sun = pow(max(dot(dir, normalize(uSunDir)), 0.0), 1400.0);
        float glow = pow(max(dot(dir, normalize(uSunDir)), 0.0), 7.0);
        col += vec3(1.0, 0.96, 0.88) * sun * 3.0;
        col += vec3(1.0, 0.55, 0.28) * glow * 0.42;
        float band = exp(-pow((h - 0.015) / 0.055, 2.0));
        col = mix(col, vec3(1.0, 0.8, 0.58), band * 0.28);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = -2;
  return mesh;
}
