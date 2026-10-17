import * as THREE from "three";
import { waveGLSL } from "./waves.js";
import { skyGLSL, SUN_DIR } from "./sky.js";

// 1D vertex coordinates: fine spacing in the core, growing outward.
function axis(lo, hi, coreLo, coreHi, step, grow) {
  const out = [];
  for (let v = coreLo; v <= coreHi + 1e-6; v += step) out.push(v);
  let s = step;
  for (let v = coreHi; v < hi; ) {
    s *= grow;
    v += s;
    out.push(v);
  }
  s = step;
  for (let v = coreLo; v > lo; ) {
    s *= grow;
    v -= s;
    out.unshift(v);
  }
  return out;
}

function buildGrid() {
  const xs = axis(-900, 900, -28, 28, 0.28, 1.06);
  const zs = axis(-1000, 80, -10, 14, 0.14, 1.06);
  const nx = xs.length;
  const nz = zs.length;
  const pos = new Float32Array(nx * nz * 3);
  for (let j = 0; j < nz; j++) {
    for (let i = 0; i < nx; i++) {
      const k = (j * nx + i) * 3;
      pos[k] = xs[i];
      pos[k + 2] = zs[j];
    }
  }
  const idx = new Uint32Array((nx - 1) * (nz - 1) * 6);
  let q = 0;
  for (let j = 0; j < nz - 1; j++) {
    for (let i = 0; i < nx - 1; i++) {
      const a = j * nx + i;
      const b = a + 1;
      const c = a + nx;
      const d = c + 1;
      idx[q++] = a;
      idx[q++] = c;
      idx[q++] = b;
      idx[q++] = b;
      idx[q++] = c;
      idx[q++] = d;
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  return g;
}

const vertex = /* glsl */ `
uniform float uTime;
varying vec3 vWorld;
varying vec3 vNormal;
varying vec2 vRest;
varying float vU;
varying float vProf;
varying float vAmp;

${waveGLSL}

void main() {
  vec2 p = position.xz;
  float u, prof;
  vec3 P = surf(p, u, prof);
  float e = 0.1;
  float u2, p2;
  vec3 px = surf(p + vec2(e, 0.0), u2, p2) - surf(p - vec2(e, 0.0), u2, p2);
  vec3 pz = surf(p + vec2(0.0, e), u2, p2) - surf(p - vec2(0.0, e), u2, p2);
  vNormal = normalize(cross(pz, px));
  vWorld = P;
  vRest = p;
  vU = u;
  vProf = prof;
  vAmp = heroAmp(p.x);
  gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
}
`;

const fragment = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
varying vec3 vWorld;
varying vec3 vNormal;
varying vec2 vRest;
varying float vU;
varying float vProf;
varying float vAmp;

${skyGLSL}

void main() {
  vec3 L = uSunDir;
  vec3 V = normalize(cameraPosition - vWorld);
  vec3 N = normalize(vNormal);
  if (dot(N, V) < 0.0) N = -N;
  float dist = length(cameraPosition - vWorld);

  // fine ripples, scrolling toward the wave
  vec2 rp = vec2(vWorld.x * 1.6, vWorld.z * 1.6 + uTime * 1.8);
  float r0 = vnoise(rp);
  float rx = vnoise(rp + vec2(0.07, 0.0));
  float rz = vnoise(rp + vec2(0.0, 0.07));
  vec2 rp2 = vec2(vWorld.x * 4.1 - uTime * 0.4, vWorld.z * 4.1 + uTime * 2.6);
  float s0 = vnoise(rp2);
  float sx = vnoise(rp2 + vec2(0.07, 0.0));
  float sz = vnoise(rp2 + vec2(0.0, 0.07));
  float rippleFade = exp(-dist * 0.012);
  N = normalize(N + vec3(rx - r0, 0.0, rz - r0) * 0.4 * rippleFade
                  + vec3(sx - s0, 0.0, sz - s0) * 0.2 * rippleFade);

  float ndv = max(dot(N, V), 0.0);
  float fres = 0.02 + 0.98 * pow(1.0 - ndv, 5.0);

  // body colour: dark troughs, glowing turquoise on the lit face
  float hn = clamp(vWorld.y / 4.0, 0.0, 1.0);
  vec3 deep = vec3(0.010, 0.075, 0.120);
  vec3 mid = vec3(0.020, 0.250, 0.300);
  vec3 glow = vec3(0.10, 0.62, 0.48);
  vec3 body = mix(deep, mid, smoothstep(0.0, 0.45, hn));
  float diff = max(dot(N, L), 0.0);
  body *= 0.55 + 0.9 * diff;

  // light shining through the thin, steep part of the wave (sun behind it)
  float toSun = max(dot(-V, L), 0.0);
  float thin = smoothstep(0.30, 0.95, vProf) * smoothstep(-0.2, 0.7, N.z);
  float back = 0.30 + 1.5 * pow(toSun, 1.5);
  body += glow * thin * back * (0.35 + 0.65 * smoothstep(0.3, 1.0, hn));
  body += vec3(0.8, 0.9, 0.3) * pow(thin, 4.0) * pow(toSun, 3.0) * 0.5;

  vec3 R = reflect(-V, N);
  R.y = abs(R.y);
  vec3 refl = skyColor(normalize(R), false, 0.06);
  vec3 col = mix(body, refl, fres * 0.9);

  // sun glitter
  vec3 H = normalize(L + V);
  float nh = max(dot(N, H), 0.0);
  float spec = pow(nh, 420.0) * 9.0 + pow(nh, 60.0) * 0.45;
  col += vec3(1.0, 0.78, 0.5) * spec;

  // --- foam ---
  float u = vU;
  float x = vRest.x;
  // lip & crest: ragged foam that reaches further down the face in places
  float lipN = fbm(vec2(x * 1.1, u * 1.4 - uTime * 0.25));
  float lipD = fbm(vec2(x * 3.4 + 7.0, u * 2.0 - uTime * 0.4));
  float edge = vProf + (lipN - 0.5) * 0.55 + (lipD - 0.5) * 0.25;
  float lip = smoothstep(0.80, 0.90, edge) * smoothstep(-1.4, -0.4, u) * smoothstep(3.2, 2.0, u);
  // streaks tumbling down the face
  float streakN = fbm(vec2(x * 5.0, u * 0.32 - uTime * 0.9));
  float streak = smoothstep(0.60, 0.70, streakN) * smoothstep(3.2, 1.0, u) * smoothstep(0.2, 1.0, u);
  streak *= (exp(-pow(x / 24.0, 2.0)) * 0.85 + 0.15) * 0.8;
  // churned foot of the wave
  float footN = fbm(vec2(x * 0.9, (u + uTime * 0.7) * 0.8));
  float foot = smoothstep(0.50, 0.75, footN) * smoothstep(3.2, 5.0, u) * smoothstep(11.0, 6.0, u) * 0.75;
  // white water where the wave has already closed out
  float closed = smoothstep(14.0, 26.0, abs(x));
  float whiteN = fbm(vec2(x * 0.7, (u + uTime * 0.9) * 0.7) + 3.0);
  float white = closed * smoothstep(0.38, 0.6, whiteN) * smoothstep(-3.0, 0.5, u) * smoothstep(16.0, 8.0, u);
  // flecks drifting across the open sea
  float fleckN = vnoise(vec2(vWorld.x * 0.9, vWorld.z * 0.9 + uTime * 1.5));
  float fleck = smoothstep(0.82, 0.95, fleckN) * 0.35 * smoothstep(0.4, 1.0, hn + 0.3);

  float foam = clamp(max(max(lip, streak), max(max(foot, white), fleck)), 0.0, 1.0);
  vec3 foamCol = mix(vec3(0.70, 0.84, 0.88), vec3(1.0, 0.97, 0.92), clamp(diff * 0.8 + 0.3, 0.0, 1.0));
  foamCol += vec3(1.0, 0.6, 0.3) * pow(max(dot(N, L), 0.0), 2.0) * 0.15;
  col = mix(col, foamCol, foam * 0.92);

  // aerial perspective
  float fogA = 1.0 - exp(-dist * 0.0050);
  vec3 fogCol = skyColor(normalize(vec3(-V.x, 0.012, -V.z)), false, 0.0);
  col = mix(col, fogCol, fogA);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean() {
  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: SUN_DIR },
  };
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: vertex,
    fragmentShader: fragment,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(buildGrid(), material);
  mesh.frustumCulled = false;
  return { mesh, uniforms };
}
