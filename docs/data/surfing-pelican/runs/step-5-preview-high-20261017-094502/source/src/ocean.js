// ocean.js — the sea. A large grid displaced in the vertex shader by the
// shared swell function, then lit by hand in the fragment shader: fresnel sky
// reflection, sun glitter, caps of white water, and a permanent foam wake
// trailing behind the surfer.

import * as THREE from 'three';
import { waveGLSL } from './waves.js';
import { SKY_UNIFORMS, SKY_COLOR, NOISE, DETAIL_NORMAL } from './glsl.js';
import { PALETTE } from './uniforms.js';

export const OCEAN_SIZE = 760;
const SEGMENTS = 384;

const VERT = /* glsl */ `
uniform float uTime;
${waveGLSL()}

varying vec3 vWorld;
varying vec3 vNrm;
varying float vH;

void main() {
  vec3 p = position;
  float h = surfHeight(p.xz, uTime);
  p.y += h;
  vec3 n = surfNormal(p.xz, uTime);
  vec4 wp = modelMatrix * vec4(p, 1.0);
  vWorld = wp.xyz;
  vNrm = normalize(mat3(modelMatrix) * n);
  vH = h;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */ `
precision highp float;

${SKY_UNIFORMS}
${SKY_COLOR}
${waveGLSL()}
${NOISE}
${DETAIL_NORMAL}

uniform vec3 uDeepColor;
uniform vec3 uShallowColor;
uniform vec3 uFoamColor;
uniform vec2 uSurfer;
uniform vec2 uTravelDir;
uniform float uSurferRadius;
uniform float uFogDensity;

varying vec3 vWorld;
varying vec3 vNrm;
varying float vH;

// lower resolution noise far away, where it would otherwise alias
vec2 foamUV(vec2 p, float dist) {
  float lod = clamp(dist / 210.0, 0.14, 1.0);
  return p * lod;
}

void main() {
  vec3 V = normalize(cameraPosition - vWorld);
  float dist = length(cameraPosition - vWorld);

  vec3 N = normalize(vNrm);
  float detail = 1.0 - smoothstep(18.0, 240.0, dist);
  N = normalize(N + detailNormal(vWorld.xz, uTime) * detail * 0.55);

  // water body: darker in the troughs, glowing turquoise where it is thin
  float hn = clamp(vH * 0.62 + 0.5, 0.0, 1.0);
  vec3 water = mix(uDeepColor, uShallowColor, pow(hn, 1.45));
  water += uShallowColor * pow(1.0 - clamp(N.y, 0.0, 1.0), 2.0) * 0.35 * hn;

  // sky reflection (view direction towards the horizon)
  vec3 hdir = normalize(vec3(vWorld.x - cameraPosition.x, 0.06, vWorld.z - cameraPosition.z));
  vec3 R = reflect(-V, N);
  float sunR = max(dot(R, uSunDir), 0.0);

  vec3 refl = skyColor(hdir) * 0.92;
  refl += uSunColor * pow(sunR, 90.0) * 0.32;
  float fres = 0.02 + 0.72 * pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 5.0);
  vec3 col = mix(water, refl, clamp(fres, 0.0, 1.0));

  // sun glitter
  col += uSunColor * (pow(sunR, 260.0) * 1.1 + pow(sunR, 26.0) * 0.22) * (0.35 + 0.9 * detail);

  // ---- white water ---------------------------------------------------------
  vec2 g = surfGrad(vWorld.xz, uTime);
  float steep = length(g);
  float caps = smoothstep(0.20, 0.52, steep) * smoothstep(0.22, 0.60, vH);

  vec2 rel = vWorld.xz - uSurfer;
  float rr = uSurferRadius * (1.0 + 0.10 * sin(uTime * 3.1));
  float rag = fbm(foamUV(vWorld.xz, dist) * 1.9 + vec2(uTime * 1.4, -uTime * 0.9));
  float collar = smoothstep(rr * (1.15 + 0.30 * rag), rr * 0.32, length(rel));
  collar *= 0.62;

  float along = dot(rel, uTravelDir);
  float side = dot(rel, vec2(-uTravelDir.y, uTravelDir.x));
  float wakeMask = smoothstep(1.5, 14.0, -along) * smoothstep(70.0, 18.0, -along);
  float wakeN = fbm(foamUV(vec2(along, side), dist) * 1.3 + vec2(-uTime * 2.2, 0.0));
  float wake = exp(-abs(side) * 0.11) * wakeMask * (0.45 + 0.55 * wakeN);

  float foam = clamp(caps * 0.8 + collar + wake * 0.42 * detail, 0.0, 1.0);
  float sparkle = step(0.86, hash21(floor(vWorld.xz * 6.0 / max(0.25, detail))));
  col = mix(col, uFoamColor * (0.92 + 0.30 * sparkle), foam * 0.85);

  // ---- fade into the very same sky the dome draws --------------------------
  float fog = 1.0 - exp(-pow(dist * uFogDensity, 2.1));
  col = mix(col, skyColor(hdir), clamp(fog, 0.0, 1.0));

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean(shared) {
  const geometry = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, SEGMENTS, SEGMENTS);
  geometry.rotateX(-Math.PI / 2); // lay it flat: local .xz == world .xz, .y is height

  const uniforms = {
    ...shared,
    uDeepColor: { value: new THREE.Color(PALETTE.deep) },
    uShallowColor: { value: new THREE.Color(PALETTE.shallow) },
    uFoamColor: { value: new THREE.Color(PALETTE.foam) },
    uSurfer: { value: new THREE.Vector2(0, 0) },
    uTravelDir: { value: new THREE.Vector2(1, 0) },
    uSurferRadius: { value: 1.55 },
    uFogDensity: { value: 0.0029 },
  };

  const material = new THREE.ShaderMaterial({
    vertexShader: VERT,
    fragmentShader: FRAG,
    uniforms,
    side: THREE.FrontSide,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'ocean';
  mesh.frustumCulled = false;

  return {
    mesh,
    uniforms,
    /** near the surface there is a per-swell tendency to show caps first */
    setSurfer(x, z) {
      uniforms.uSurfer.value.set(x, z);
    },
  };
}
