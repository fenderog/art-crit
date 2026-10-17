import * as THREE from "three";
import { skyGLSL, skyUniforms } from "./sky.js";

// Everything is simulated in a frame that rides along with the surfer:
// the wave crest sits on the x axis (z = 0) and breaks toward +z.
// The open water slides past at (VX, VZ) to sell the motion.
export const VX = 4.2; // surfer speed along the wave
export const VZ = 7.0; // wave travel speed
const NOISE_PERIOD = 289 / 0.05; // simplex noise repeats every 289 lattice units
const AMP_PERIOD = (Math.PI * 2) / 0.05;
export const TRAIL_COUNT = 56;

// small travelling swells: [dirX, dirZ, wavelength, amplitude]
const SMALL = [
  [0.0, 1.0, 9.0, 0.11],
  [0.3, 0.95, 5.6, 0.07],
  [-0.5, 0.86, 3.8, 0.05],
  [0.8, 0.6, 2.4, 0.03],
  [-0.9, 0.42, 1.7, 0.02],
];
const waves = SMALL.map(([dx, dz, L, a]) => {
  const l = Math.hypot(dx, dz);
  const k = (Math.PI * 2) / L;
  return { dx: dx / l, dz: dz / l, k, a, w: Math.sqrt(9.8 * k) };
});

const state = { offS: 0, phases: new Float32Array(waves.length) };

export function heroProfile(z) {
  const w = z > 0 ? 4.0 : 11.0;
  return Math.exp((-z * z) / (w * w));
}
export function brokenAmt(x) {
  return 1 - smoothstep(-17, -7, x);
}
function heroAmp(x) {
  const s = x + state.offS;
  const a = 3.7 + 0.3 * Math.sin(s * 0.05) + 0.2 * Math.sin(s * 0.15 + 1.3);
  return a * (1 - 0.5 * brokenAmt(x));
}
function swells(x, z) {
  return (
    heroAmp(x) * heroProfile(z) +
    1.8 * Math.exp(-(((z + 38) / 12) ** 2)) * (1 + 0.2 * Math.sin((x + state.offS) * 0.05 + 2.0)) +
    1.2 * Math.exp(-(((z + 75) / 14) ** 2))
  );
}
function smallWaves(x, z) {
  let h = 0;
  for (let i = 0; i < waves.length; i++) {
    const w = waves[i];
    h += w.a * Math.sin(w.k * (w.dx * x + w.dz * z) + state.phases[i]);
  }
  return h;
}

// Water height at frame coordinates (ignores the lip push, which only
// matters above where the board ever goes).
export function heightAt(x, z) {
  return swells(x, z) + smallWaves(x, z) * (1 - 0.6 * heroProfile(z));
}

export function normalAt(x, z, out = new THREE.Vector3()) {
  const e = 0.12;
  const hx = heightAt(x + e, z) - heightAt(x - e, z);
  const hz = heightAt(x, z + e) - heightAt(x, z - e);
  return out.set(-hx, 2 * e, -hz).normalize();
}

function smoothstep(a, b, x) {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
}

const noiseGLSL = /* glsl */ `
vec3 permute3(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute3(permute3(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
  m = m * m; m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
`;

const commonGLSL = /* glsl */ `
uniform float uTime;
uniform vec2 uOffN;
uniform float uOffS;
uniform vec4 uWaves[5];
uniform float uPhase[5];

float heroProfile(float z) { float w = z > 0.0 ? 4.0 : 11.0; return exp(-z * z / (w * w)); }
float brokenAmt(float x) { return 1.0 - smoothstep(-17.0, -7.0, x); }
float heroAmp(float x) {
  float s = x + uOffS;
  float a = 3.7 + 0.3 * sin(s * 0.05) + 0.2 * sin(s * 0.15 + 1.3);
  return a * (1.0 - 0.5 * brokenAmt(x));
}
float swells(vec2 p) {
  return heroAmp(p.x) * heroProfile(p.y)
    + 1.8 * exp(-pow((p.y + 38.0) / 12.0, 2.0)) * (1.0 + 0.2 * sin((p.x + uOffS) * 0.05 + 2.0))
    + 1.2 * exp(-pow((p.y + 75.0) / 14.0, 2.0));
}
float smallWaves(vec2 p) {
  float h = 0.0;
  for (int i = 0; i < 5; i++) h += uWaves[i].w * sin(uWaves[i].z * dot(uWaves[i].xy, p) + uPhase[i]);
  return h;
}
`;

const vertexShader = /* glsl */ `
${noiseGLSL}
${commonGLSL}
varying vec3 vWorld;
varying vec3 vNormal;
varying vec2 vFrame;
varying float vProf;

vec3 displace(vec2 p) {
  float prof = heroProfile(p.y);
  float broken = brokenAmt(p.x);
  float h = swells(p) + smallWaves(p) * (1.0 - 0.6 * prof);
  // churning whitewater on the broken section
  vec2 q = p + uOffN;
  float churn = snoise(q * 0.4 + vec2(0.0, uTime * 0.35)) * 0.5 + snoise(q * 0.8 - vec2(uTime * 0.5, 0.0)) * 0.25;
  float wwMask = broken * smoothstep(-3.0, 1.0, p.y) * (1.0 - smoothstep(10.0, 30.0, p.y));
  h += churn * 0.45 * wwMask;
  // the lip pitches forward on the unbroken section
  float lip = pow(prof, 8.0) * (1.0 - broken);
  float dz = 2.1 * lip;
  h += 0.25 * lip;
  // the broken section's crest rolls forward as a soft foam wall
  dz += 1.2 * pow(prof, 4.0) * broken;
  return vec3(p.x, h, p.y + dz);
}

void main() {
  vec2 p = position.xz;
  vec3 P = displace(p);
  float e = 0.12;
  vec3 Px = displace(p + vec2(e, 0.0));
  vec3 Pz = displace(p + vec2(0.0, e));
  vNormal = normalize(cross(Pz - P, Px - P));
  vFrame = p;
  vProf = heroProfile(p.y);
  vec4 world = modelMatrix * vec4(P, 1.0);
  vWorld = world.xyz;
  gl_Position = projectionMatrix * viewMatrix * world;
}
`;

const fragmentShader = /* glsl */ `
${noiseGLSL}
${commonGLSL}
${skyGLSL}
uniform vec3 uDeep;
uniform vec3 uFace;
uniform vec3 uGlow;
uniform vec4 uTrail[${TRAIL_COUNT}];
uniform vec3 uBoard;

varying vec3 vWorld;
varying vec3 vNormal;
varying vec2 vFrame;
varying float vProf;

float fbm(vec2 p) {
  float f = 0.0, a = 0.5;
  for (int i = 0; i < 4; i++) { f += a * snoise(p); p *= 2.0; a *= 0.5; }
  return f;
}

vec2 rippleGrad(vec2 q, float t) {
  vec2 g = vec2(0.0);
  // [dirAngle, k, amp]
  vec3 R[6];
  R[0] = vec3(0.3, 2.1, 0.030);
  R[1] = vec3(-0.7, 3.3, 0.020);
  R[2] = vec3(1.4, 4.7, 0.014);
  R[3] = vec3(-1.9, 6.9, 0.009);
  R[4] = vec3(2.6, 9.3, 0.006);
  R[5] = vec3(0.9, 13.0, 0.004);
  for (int i = 0; i < 6; i++) {
    vec2 d = vec2(sin(R[i].x), cos(R[i].x));
    float w = sqrt(9.8 * R[i].y);
    float c = cos(R[i].y * dot(d, q) - w * t);
    g += d * (R[i].y * R[i].z * c);
  }
  return g;
}

void main() {
  vec3 N = normalize(vNormal);
  if (!gl_FrontFacing) N = -N;
  vec3 toCam = cameraPosition - vWorld;
  float dist = length(toCam);
  vec3 V = toCam / dist;

  vec2 q = vFrame + uOffN;
  float broken = brokenAmt(vFrame.x);

  // fine ripples (fade out with distance to avoid shimmer)
  vec2 rg = rippleGrad(q, uTime) * exp(-dist * 0.025);
  N = normalize(N + vec3(-rg.x, 0.0, -rg.y));

  float NdV = max(dot(N, V), 0.0);
  float fres = 0.02 + 0.98 * pow(1.0 - NdV, 5.0);
  vec3 R = reflect(-V, N);
  R.y = abs(R.y);
  vec3 refl = skyColor(R);

  // body colour: deep blue on the flats, turquoise up the face
  float face = smoothstep(0.05, 0.7, vProf) * (vFrame.y > -6.0 ? 1.0 : 0.4);
  vec3 body = mix(uDeep, uFace, face);
  float NdL = max(dot(N, uSunDir), 0.0);
  body *= 0.55 + 0.45 * NdL;

  // light shining through the thin lip
  float thin = smoothstep(0.45, 0.98, vProf) * (1.0 - broken * 0.7);
  float back = pow(clamp(dot(-V, uSunDir) * 0.5 + 0.5, 0.0, 1.0), 3.0);
  vec3 sss = uGlow * thin * (0.35 + 1.6 * back);
  body += sss * (0.6 + 0.4 * (1.0 - NdV));

  vec3 col = mix(body, refl, fres);

  // sun glints
  float sp = max(dot(R, uSunDir), 0.0);
  col += uSunColor * (pow(sp, 900.0) * 10.0 + pow(sp, 90.0) * 0.18) * (0.4 + 0.6 * fres);

  // ---- foam ----
  float n1 = fbm(q * 0.4 + vec2(0.0, uTime * 0.05));
  float n2 = fbm(q * vec2(0.8, 1.6) - vec2(uTime * 0.1, 0.0));
  // feathering lip
  float lipFoam = smoothstep(0.86, 0.985, vProf) * smoothstep(-2.0, 0.5, vFrame.y);
  lipFoam *= smoothstep(-0.15, 0.35, n2 + 0.25);
  // whitewater on the broken section and the foam it leaves on the flats
  float ww = broken * smoothstep(-6.0, 0.0, vFrame.y) * (1.0 - smoothstep(8.0, 34.0, vFrame.y));
  float wwFoam = ww * smoothstep(-0.25, 0.25, n1 + 0.45 - 0.5 * smoothstep(4.0, 30.0, vFrame.y));
  // old foam streaks drifting on the flats and over the back
  // thin lacy lines: ridges of noise rather than blobs
  float sn = fbm(q * vec2(0.18, 0.5)) + 0.25 * n2;
  float streak = (1.0 - smoothstep(0.0, 0.06, abs(sn - 0.1))) * smoothstep(0.15, 0.55, fbm(q * 0.9 + 3.0) + 0.2) * 0.32;
  streak *= 1.0 - smoothstep(0.2, 0.7, vProf) * step(0.0, vFrame.y);
  // board trail
  float trail = 0.0;
  for (int i = 0; i < ${TRAIL_COUNT}; i++) {
    vec4 t = uTrail[i];
    vec2 d = vFrame - t.xy;
    trail += t.z * exp(-dot(d, d) * t.w);
  }
  trail = clamp(trail, 0.0, 1.0) * smoothstep(-0.2, 0.4, n2 + trail * 0.6);
  float foam = max(max(lipFoam, wwFoam), max(streak, trail));

  vec3 foamCol = vec3(0.92, 0.95, 0.97) * (0.62 + 0.38 * NdL) + uGlow * thin * back * 1.4;
  foamCol += uSunColor * 0.12;
  col = mix(col, foamCol, clamp(foam, 0.0, 1.0));

  // contact shadow under the board
  vec2 bd = vFrame - uBoard.xz;
  col *= 1.0 - 0.35 * exp(-dot(bd, bd) * 1.3);

  // aerial haze toward the horizon
  vec3 hz = normalize(vec3(-V.x, max(-V.y, 0.0) * 0.3, -V.z));
  float fogF = 1.0 - exp(-max(dist - 30.0, 0.0) * 0.0032);
  col = mix(col, skyColor(hz), fogF);

  gl_FragColor = vec4(col, 1.0);
}
`;

function warpedGrid(size, segs) {
  // dense near the surfer, coarse toward the horizon
  const coord = (u) => size * Math.sign(u) * (0.08 * Math.abs(u) + 0.92 * Math.pow(Math.abs(u), 4));
  const pos = new Float32Array((segs + 1) * (segs + 1) * 3);
  let k = 0;
  for (let j = 0; j <= segs; j++) {
    const z = coord((j / segs) * 2 - 1);
    for (let i = 0; i <= segs; i++) {
      const x = coord((i / segs) * 2 - 1);
      pos[k++] = x;
      pos[k++] = 0;
      pos[k++] = z;
    }
  }
  const idx = [];
  for (let j = 0; j < segs; j++) {
    for (let i = 0; i < segs; i++) {
      const a = j * (segs + 1) + i;
      const b = a + 1;
      const c = a + segs + 1;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setIndex(idx);
  return g;
}

export function createOcean() {
  const trail = [];
  for (let i = 0; i < TRAIL_COUNT; i++) trail.push(new THREE.Vector4(0, 0, 0, 1));
  const uniforms = {
    ...skyUniforms,
    uTime: { value: 0 },
    uOffN: { value: new THREE.Vector2() },
    uOffS: { value: 0 },
    uWaves: { value: waves.map((w) => new THREE.Vector4(w.dx, w.dz, w.k, w.a)) },
    uPhase: { value: Array.from(state.phases) },
    uDeep: { value: new THREE.Color("#06304a") },
    uFace: { value: new THREE.Color("#0f6a78") },
    uGlow: { value: new THREE.Color("#35d6be") },
    uTrail: { value: trail },
    uBoard: { value: new THREE.Vector3() },
  };
  const mesh = new THREE.Mesh(
    warpedGrid(1300, 420),
    new THREE.ShaderMaterial({ uniforms, vertexShader, fragmentShader, side: THREE.DoubleSide })
  );
  mesh.frustumCulled = false;

  return {
    mesh,
    uniforms,
    trail,
    update(t) {
      // offsets are accumulated in double precision on the CPU and wrapped
      // at the period of whatever consumes them
      const ox = VX * t;
      const oz = VZ * t;
      state.offS = ox % AMP_PERIOD;
      for (let i = 0; i < waves.length; i++) {
        const w = waves[i];
        state.phases[i] = (w.k * (w.dx * ox + w.dz * oz) - w.w * t) % (Math.PI * 2);
        uniforms.uPhase.value[i] = state.phases[i];
      }
      uniforms.uTime.value = t;
      uniforms.uOffS.value = state.offS;
      uniforms.uOffN.value.set(ox % NOISE_PERIOD, oz % NOISE_PERIOD);
    },
  };
}
