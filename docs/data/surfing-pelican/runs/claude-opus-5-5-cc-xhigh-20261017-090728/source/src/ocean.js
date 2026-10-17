// One continuous ocean mesh: the grid's rows follow the wave profile near the
// break and fan out to the horizon, its columns run along the wave line.

import * as THREE from 'three';
import { NOISE_GLSL, SKY_GLSL, CHOP_GLSL } from './shaders.js';
import { WAVE_SCALE, SURF_SPEED, WAVE_SPEED, NPTS, makePoints, profileAt, crEval, stageAt, ampAt, zoffAt } from './wave.js';
import { smoothstep } from './geom.js';

const FAR_BACK = [-1500, -900, -520, -300, -180, -110, -68, -42];
const FAR_FRONT = [36, 60, 110, 220];
// samples per profile segment (segment k joins control points k and k+1)
const SEG = [5, 6, 8, 9, 10, 12, 14, 14, 12, 10, 10, 10, 10, 12, 16];

function buildColumns() {
  const step = (x) => (x < -20 ? 0.22 + (-20 - x) * 0.07 : x > 28 ? 0.22 + (x - 28) * 0.07 : 0.22);
  const right = [];
  let x = 0;
  while (x < 1500) { right.push(x); x += step(x); }
  right.push(1500);
  const left = [];
  x = -step(0);
  while (x > -1500) { left.push(x); x -= step(x); }
  left.push(-1500);
  return left.reverse().concat(right);
}

const vertexShader = /* glsl */ `
uniform float uTime;
uniform float uFlowX;
attribute vec4 aSurf;   // stage, profile param, v (along-surface coord), amplitude
varying vec3 vWorld;
varying vec3 vNrm;
varying vec4 vSurf;
${NOISE_GLSL}
${CHOP_GLSL}
void main() {
  vec3 p = position;
  vec3 n = normal;
  float stage = aSurf.x;
  float rp = aSurf.y;
  vec3 pf = p + vec3(uFlowX * uTime, 0.0, 0.0);
  float h = chop(pf, uTime);
  float lip = exp(-pow((rp - 7.0) / 1.4, 2.0)) * smoothstep(1.0, 1.8, stage);
  h *= 1.0 - 0.75 * lip;
  // the throwing lip wobbles
  h += lip * (1.0 - smoothstep(2.6, 3.2, stage)) * 0.07 * sin(pf.x * 0.9 - uTime * 2.0 + rp * 1.3);
  // boiling whitewater
  float ww = smoothstep(2.3, 3.5, stage) * smoothstep(3.0, 5.0, rp) * (1.0 - smoothstep(12.5, 14.5, rp));
  vec2 wq = vec2(pf.x * 0.45, aSurf.z * 0.6);
  h += ww * ((vnoise(wq + vec2(0.0, uTime * 0.7)) - 0.4) * 0.6 + (vnoise(wq * 2.3 - vec2(uTime * 0.9, 0.0)) - 0.5) * 0.3);
  p += n * h;
  vec4 wp = modelMatrix * vec4(p, 1.0);
  vWorld = wp.xyz;
  vNrm = normalize(mat3(modelMatrix) * n);
  vSurf = aSurf;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
uniform float uFlowX;
uniform float uFlowV;
uniform float uWaveScale;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFoam;
varying vec3 vWorld;
varying vec3 vNrm;
varying vec4 vSurf;
${NOISE_GLSL}
${SKY_GLSL}

#define RW(DX, DY, K, A, S) { vec2 d = normalize(vec2(DX, DY)); float f = clamp(2.0 - (K) * fd, 0.0, 1.0); g += d * ((A) * (K) * cos(dot(d, q) * (K) + t * (S))) * f; }

vec2 rippleGrad(vec2 q, float t, float dist) {
  vec2 g = vec2(0.0);
  float fd = dist / 140.0;
  RW( 0.10,  1.00, 0.18, 0.30, 0.55)
  RW( 0.62,  0.78, 0.9, 0.060, 1.30)
  RW(-0.70,  0.71, 1.7, 0.032, 1.90)
  RW( 0.95, -0.25, 2.9, 0.017, 2.50)
  RW( 0.15,  0.99, 4.6, 0.010, 3.10)
  RW(-0.45, -0.89, 7.1, 0.0065, 3.90)
  RW( 0.80,  0.55, 10.5, 0.0042, 4.70)
  RW(-0.92,  0.35, 15.0, 0.0028, 5.60)
  float fn = clamp(1.6 - dist / 50.0, 0.0, 1.0);
  g += vnoised(q * vec2(1.3, 1.6) + vec2(t * 0.35, -t * 0.2)).yz * 0.05 * fn;
  g += vnoised(q * vec2(3.1, 3.7) - vec2(t * 0.5, t * 0.4)).yz * 0.022 * fn;
  return g;
}

void main() {
  float stage = vSurf.x;
  float rp = vSurf.y;
  float v = vSurf.z;
  float amp = vSurf.w;
  vec3 toCam = cameraPosition - vWorld;
  float dist = length(toCam);
  vec3 V = toCam / dist;
  vec3 N = normalize(vNrm);
  vec2 q = vec2(vWorld.x + uFlowX * uTime, v + uFlowV * uTime);

  // regions of the breaking wave
  float lip = exp(-pow((rp - 6.9) / 1.15, 2.0)) * smoothstep(1.15, 1.9, stage) * (1.0 - smoothstep(3.0, 3.7, stage));
  float tip = exp(-pow((rp - 7.0) / 0.5, 2.0)) * smoothstep(1.3, 2.0, stage) * (1.0 - smoothstep(3.2, 3.8, stage));
  float ww = smoothstep(2.3, 3.5, stage) * smoothstep(3.6, 5.0, rp) * (1.0 - smoothstep(13.0, 15.0, rp));
  float barrel = smoothstep(1.3, 2.0, stage) * (1.0 - smoothstep(2.8, 3.4, stage))
               * smoothstep(8.6, 9.6, rp) * (1.0 - smoothstep(11.6, 12.6, rp));

  // ripple normal in the surface tangent frame
  vec3 T = normalize(vec3(1.0, 0.0, 0.0) - N * N.x);
  vec3 B = cross(T, N);
  vec2 g = rippleGrad(q, uTime, dist) * (1.0 + ww * 1.5) * (1.0 - 0.5 * tip);
  vec3 n = normalize(N - g.x * T - g.y * B);

  // water body with light leaking through the thin crest and lip
  float hN = clamp(vWorld.y / (uWaveScale * max(amp, 0.15)), 0.0, 1.3);
  float flowN = fbm3(vec2(q.x * 0.9, q.y * 0.18) + vec2(0.0, uTime * 0.08));
  float veins = fbm3(vec2(q.x * 2.6, q.y * 0.35) + vec2(0.0, uTime * 0.15));
  float thin = clamp(smoothstep(0.6, 1.1, hN) * 0.6 + lip * 0.9, 0.0, 1.0) * (0.45 + 0.7 * flowN + 0.5 * veins);
  float backLit = pow(clamp(dot(-V, uSunDir), 0.0, 1.0), 2.5);
  float wrap = clamp(dot(normalize(N + (n - N) * 3.0), uSunDir) * 0.5 + 0.5, 0.0, 1.0);
  vec3 body = uDeep * (0.7 + 0.6 * wrap) * (0.9 + 0.25 * flowN);
  body += uShallow * uSunColor * thin * (0.06 + 0.75 * backLit);
  body += uShallow * 0.05 * smoothstep(0.2, 0.8, hN);
  body *= 1.0 - 0.5 * barrel;

  vec3 R = reflect(-V, n);
  R.y = abs(R.y);
  float F = 0.02 + 0.98 * pow(1.0 - clamp(dot(n, V), 0.0, 1.0), 5.0);
  vec3 refl = skyColor(R, 0.0) * (1.0 - 0.7 * barrel);
  float occl = 0.0;
  {
    float zc = 12.0 * (1.0 - exp(-vWorld.x * vWorld.x / 8000.0)) + uWaveScale * amp * 0.2;
    float d = vWorld.z - zc;
    float horiz = max(length(R.xz), 1e-3);
    if (d > 0.5 && R.z < 0.0 && rp > 12.0) {
      float H = uWaveScale * amp * mix(1.0, 0.55, smoothstep(2.5, 4.0, stage));
      float along = d * horiz / max(-R.z, 1e-3);
      float rel = (R.y / horiz) / (H / along);
      occl = 1.0 - smoothstep(0.55, 1.3, rel);
      vec3 waveCol = uDeep * 0.9 + uShallow * uSunColor * 0.45 * smoothstep(0.5, 1.0, rel);
      refl = mix(refl, waveCol, occl);
    }
  }
  vec3 col = mix(body, refl, F);
  float sd = max(dot(R, uSunDir), 0.0);
  col += uSunColor * (pow(sd, 1200.0) * 70.0 + pow(sd, 120.0) * 1.4 + pow(sd, 12.0) * 0.05) * (1.0 - barrel) * (1.0 - tip) * (1.0 - occl);

  // foam
  vec2 fq = q * vec2(0.5, 0.8);
  float n1 = fbm(fq + vec2(0.0, uTime * 0.1));
  float n2 = fbm(fq * 2.6 + vec2(uTime * 0.13, 3.7));
  float fn = n1 * 0.62 + n2 * 0.38;
  float foam = 0.0;
  float wwN = fbm3(q * vec2(1.1, 1.6) + vec2(uTime * 0.3, 0.0));
  foam = max(foam, ww * smoothstep(0.66 - 0.45 * ww, 0.78 - 0.42 * ww, fn) * (0.55 + 0.45 * smoothstep(0.25, 0.6, wwN)));
  float edgeLip = exp(-pow((rp - 7.15) / 0.75, 2.0)) * smoothstep(1.2, 2.0, stage) * (1.0 - smoothstep(3.0, 3.7, stage));
  foam = max(foam, lip * 0.6 * smoothstep(0.66, 0.8, fn));
  foam = max(foam, edgeLip * smoothstep(0.42, 0.62, fn + 0.08 * sin(q.x * 3.0)));
  foam = max(foam, tip * smoothstep(0.3, 0.5, fn + 0.1));
  float crest = exp(-pow((rp - 5.2) / 0.8, 2.0)) * smoothstep(0.35, 0.9, stage) * (1.0 - smoothstep(1.2, 1.6, stage));
  foam = max(foam, crest * 0.7 * smoothstep(0.6, 0.72, fn));
  // short foam streaks dragged up the face by the flow
  float steep = smoothstep(0.3, 0.7, 1.0 - N.y);
  float face = smoothstep(9.6, 10.6, rp) * (1.0 - smoothstep(12.2, 13.0, rp)) * steep
             * smoothstep(0.5, 1.2, stage) * (1.0 - smoothstep(2.6, 3.2, stage));
  // marbled foam lines: iso-contours of a stretched noise field
  float mf = fbm3(vec2(q.x * 0.6, q.y * 0.07) + vec2(0.0, uTime * 0.03));
  float mw = fwidth(mf) * 1.2 + 0.002;
  float iso = abs(fract(mf * 9.0) - 0.5) / 9.0;
  float mline = 1.0 - smoothstep(0.0, mw, iso);
  float mbreak = smoothstep(0.38, 0.6, fbm3(q * vec2(0.7, 0.3) + vec2(5.0, uTime * 0.12)));
  float mvar = 0.4 + 0.6 * vnoise(q * vec2(1.5, 0.4));
  foam = max(foam, face * 0.22 * mvar * mline * mbreak * (1.0 - smoothstep(25.0, 60.0, dist)));
  float lace = fbm3(q * vec2(0.16, 0.26) + 11.0);
  float front = smoothstep(12.8, 14.2, rp) * (0.25 + 0.6 * smoothstep(2.4, 3.8, stage) * (1.0 - smoothstep(14.5, 16.0, rp)));
  float backS = 1.0 - smoothstep(2.0, 3.6, rp);
  // remnant foam: thin lacy lines rather than blobs
  float lines = 1.0 - abs(2.0 * fbm3(q * vec2(0.22, 0.34) + 11.0) - 1.0);
  float patchy = smoothstep(0.86, 0.95, lines) * smoothstep(0.35, 0.6, n2 + lace * 0.3);
  foam = max(foam, (front * 0.8 + backS * 0.35) * patchy);
  // long scum lines left by earlier waves, lying parallel to the crest
  float sf = fbm3(vec2(q.x * 0.07, q.y * 0.3) + 21.0);
  float siso = abs(fract(sf * 3.0) - 0.5) / 3.0;
  float swid = 0.018 + 0.022 * vnoise(q * vec2(0.3, 1.0));
  float sband = 1.0 - smoothstep(swid * 0.35, swid, siso);
  float slace = smoothstep(0.38, 0.62, fbm3(q * vec2(2.2, 3.0) + 13.0));
  float sbreak = smoothstep(0.3, 0.55, fbm3(q * vec2(0.25, 0.5) + 8.0));
  float sreg = smoothstep(12.8, 13.6, rp) * (1.0 - smoothstep(50.0, 140.0, dist));
  foam = max(foam, sreg * 0.7 * sband * slace * sbreak);
  foam *= 1.0 - 0.6 * smoothstep(120.0, 600.0, dist);
  float bub = 0.8 + 0.2 * vnoise(q * 9.0);
  vec3 foamCol = uFoam * (0.5 + 0.5 * clamp(dot(n, uSunDir) * 0.5 + 0.5, 0.0, 1.0)) * bub;
  foamCol *= 1.0 - 0.45 * barrel;
  foamCol += uSunColor * uShallow * backLit * (lip + tip) * 0.8;
  col = mix(col, foamCol, clamp(foam, 0.0, 1.0));

  // aerial perspective towards the horizon
  vec3 hd = normalize(vec3(-V.x, 0.0005, -V.z));
  vec3 fogCol = skyColor(hd, 0.0);
  float fog = 1.0 - exp(-dist * 0.0028);
  fog = max(fog, smoothstep(600.0, 1400.0, dist));
  col = mix(col, fogCol, fog);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean(shared) {
  const xs = buildColumns();
  const profRows = [];
  for (let k = 0; k < NPTS - 1; k++) {
    for (let s = 0; s < SEG[k]; s++) profRows.push(k + s / SEG[k]);
  }
  profRows.push(NPTS - 1);
  const nb = FAR_BACK.length;
  const np = profRows.length;
  const nr = nb + np + FAR_FRONT.length;
  const nc = xs.length;

  const pos = new Float32Array(nc * nr * 3);
  const surf = new Float32Array(nc * nr * 4);
  const pts = makePoints();
  const r = { z: 0, y: 0, dz: 0, dy: 0 };
  const py = new Float32Array(np);
  const pz = new Float32Array(np);
  const arc = new Float32Array(np);

  for (let i = 0; i < nc; i++) {
    const x = xs[i];
    profileAt(x, pts);
    const st = stageAt(x);
    const amp = ampAt(x);
    const zo = zoffAt(x);
    for (let j = 0; j < np; j++) {
      crEval(pts, profRows[j], r);
      py[j] = r.y;
      pz[j] = r.z;
      arc[j] = j === 0 ? 0 : arc[j - 1] + Math.hypot(r.y - py[j - 1], r.z - pz[j - 1]);
    }
    const total = arc[np - 1];
    const z0 = pts[0][0];
    const z1 = pts[NPTS - 1][0];
    const put = (row, y, z, rp, v) => {
      const k = row * nc + i;
      pos[k * 3] = x; pos[k * 3 + 1] = y; pos[k * 3 + 2] = z;
      surf[k * 4] = st; surf[k * 4 + 1] = rp; surf[k * 4 + 2] = v; surf[k * 4 + 3] = amp;
    };
    for (let j = 0; j < nb; j++) put(j, 0, FAR_BACK[j] + zo, -1, FAR_BACK[j] + zo);
    for (let j = 0; j < np; j++) {
      const u = profRows[j];
      // along-surface coordinate: measured from the back before the lip and
      // from the front after it, blended across the lip so flat water stays ~z
      const vBack = z0 + arc[j];
      const vFront = z1 - (total - arc[j]);
      const v = vBack + (vFront - vBack) * smoothstep(5, 9, u);
      put(nb + j, py[j], pz[j], u, v);
    }
    for (let j = 0; j < FAR_FRONT.length; j++) put(nb + np + j, 0, FAR_FRONT[j] + zo, 16, FAR_FRONT[j] + zo);
  }

  const index = new Uint32Array((nr - 1) * (nc - 1) * 6);
  let o = 0;
  for (let j = 0; j < nr - 1; j++) {
    for (let i = 0; i < nc - 1; i++) {
      const a = j * nc + i;
      const b = a + nc;
      const c = a + 1;
      const d = b + 1;
      index[o++] = a; index[o++] = b; index[o++] = c;
      index[o++] = b; index[o++] = d; index[o++] = c;
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('aSurf', new THREE.BufferAttribute(surf, 4));
  geo.setIndex(new THREE.BufferAttribute(index, 1));
  geo.computeVertexNormals();
  geo.computeBoundingSphere();

  const mat = new THREE.ShaderMaterial({
    uniforms: {
      ...shared,
      uFlowX: { value: SURF_SPEED },
      uFlowV: { value: WAVE_SPEED },
      uWaveScale: { value: WAVE_SCALE },
      uDeep: { value: new THREE.Color('#0e4352') },
      uShallow: { value: new THREE.Color('#2ccab8') },
      uFoam: { value: new THREE.Color('#f4eee8') },
    },
    vertexShader,
    fragmentShader,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  return mesh;
}
