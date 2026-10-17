import * as THREE from "three";
import { WAVES, writePhases } from "./sim.js";
import {
  HAZE_DENSITY,
  SUN_DIR,
  horizonColor,
  skyTopColor,
  sunColor,
  deepColor,
  shallowColor,
  foamColor,
} from "./theme.js";

const N = WAVES.length;

const uniforms = {
  uPhase0: { value: new Float32Array(N) },
  uAmp: { value: new Float32Array(WAVES.map((w) => w.amp)) },
  uK: { value: new Float32Array(WAVES.map((w) => w.k)) },
  uDirX: { value: new Float32Array(WAVES.map((w) => w.dirX)) },
  uDirZ: { value: new Float32Array(WAVES.map((w) => w.dirZ)) },
  uTime: { value: 0 },
  uSunDir: { value: SUN_DIR.clone() },
  uHorizon: { value: horizonColor.clone() },
  uSkyTop: { value: skyTopColor.clone() },
  uSunColor: { value: sunColor.clone() },
  uDeep: { value: deepColor.clone() },
  uShallow: { value: shallowColor.clone() },
  uFoam: { value: foamColor.clone() },
  uHaze: { value: HAZE_DENSITY },
};

// Keep this displacement identical to sampleWater() in sim.js.
// Declarations stay outside the unrolled loop. Three duplicates the body
// into one scope, so a `float` inside the loop is a redefinition.
const waveLoop = `
float phase;
float s;
float c;
float deriv;
#pragma unroll_loop_start
for ( int i = 0; i < ${N}; i ++ ) {
  phase = uPhase0[ i ] + uK[ i ] * (uDirX[ i ] * x + uDirZ[ i ] * z);
  s = sin(phase);
  c = cos(phase);
  h += uAmp[ i ] * s;
  deriv = uAmp[ i ] * uK[ i ] * c;
  dhdx += deriv * uDirX[ i ];
  dhdz += deriv * uDirZ[ i ];
  if (UNROLLED_LOOP_INDEX == 0) crest = s * 0.5 + 0.5;
}
#pragma unroll_loop_end
`;

const vertexShader = /* glsl */ `
uniform float uPhase0[${N}];
uniform float uAmp[${N}];
uniform float uK[${N}];
uniform float uDirX[${N}];
uniform float uDirZ[${N}];

varying vec3 vWorld;
varying vec3 vNormal;
varying float vCrest;
varying float vHeight;
varying float vSlope;

void main() {
  float x = position.x;
  float z = position.z;
  float h = 0.0;
  float dhdx = 0.0;
  float dhdz = 0.0;
  float crest = 0.0;
  ${waveLoop}
  vec3 local = position;
  local.y += h;
  vec4 world = modelMatrix * vec4(local, 1.0);
  vWorld = world.xyz;
  vNormal = normalize(vec3(-dhdx, 1.0, -dhdz));
  vCrest = crest;
  vHeight = h;
  vSlope = length(vec2(dhdx, dhdz));
  vec4 mvPosition = viewMatrix * world;
  gl_Position = projectionMatrix * mvPosition;
}
`;

const fragmentShader = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uHorizon;
uniform vec3 uSkyTop;
uniform vec3 uSunColor;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFoam;
uniform float uHaze;
uniform float uTime;

varying vec3 vWorld;
varying vec3 vNormal;
varying float vCrest;
varying float vHeight;
varying float vSlope;

void main() {
  vec3 N = normalize(vNormal);
  float rip = sin(vWorld.x * 5.2 + uTime * 1.5) * sin(vWorld.z * 4.4 - uTime * 1.2);
  rip += 0.5 * sin(vWorld.x * 11.0 - vWorld.z * 9.0 + uTime * 2.4);
  N.x += rip * 0.03;
  N.z += rip * 0.025;
  N = normalize(N);

  vec3 V = normalize(cameraPosition - vWorld);
  vec3 R = reflect(-V, N);
  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.2);
  float lit = clamp(dot(N, uSunDir), 0.0, 1.0);

  vec3 waterCol = mix(uDeep, uShallow, clamp(0.12 + 0.4 * lit + 0.12 * vCrest, 0.0, 1.0));
  float skyH = smoothstep(-0.05, 0.72, R.y);
  vec3 skyCol = mix(uHorizon, uSkyTop, skyH);
  skyCol += uSunColor * pow(max(dot(R, uSunDir), 0.0), 14.0) * 0.28;

  vec3 col = mix(waterCol, skyCol, fres * 0.34 + 0.02);
  float spec = pow(max(dot(R, uSunDir), 0.0), 220.0);
  col += uSunColor * spec * 0.45;

  float lip = smoothstep(0.978, 0.998, vCrest);
  float grain = 0.55 + 0.45 * sin(vWorld.x * 3.7 + vWorld.z * 2.6 + uTime * 2.6);
  float foam = clamp(lip * grain, 0.0, 0.85);
  col = mix(col, uFoam, foam);

  float depth = length(vWorld - cameraPosition);
  float haze = 1.0 - exp(-uHaze * uHaze * depth * depth);
  col = mix(col, uHorizon, clamp(haze, 0.0, 1.0));

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createWater() {
  const size = 190;
  const seg = 200;
  const geo = new THREE.PlaneGeometry(size, size, seg, seg);
  geo.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader,
      fragmentShader,
    }),
  );
  mesh.frustumCulled = false;
  mesh.receiveShadow = false;
  return {
    mesh,
    seg: size / seg,
    setOrigin(snapX, snapZ, time) {
      writePhases(snapX, snapZ, time, uniforms.uPhase0.value);
      uniforms.uTime.value = time;
    },
  };
}
