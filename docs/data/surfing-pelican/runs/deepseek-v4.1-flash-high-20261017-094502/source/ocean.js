import * as THREE from 'three';
import { waveGLSL } from './waves.js';

// A GPU-displaced ocean plane. The mesh stays at the origin and is panned in
// the vertex shader by `uOffset`, so the water is effectively endless.

const SIZE = 620;
const SEGMENTS = 300;
const SNAP = SIZE / SEGMENTS;

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform vec2 uOffset;

  varying vec3 vWorld;
  varying vec3 vNormal;
  varying float vWave;

  ${waveGLSL}

  void main() {
    vec2 world = position.xz + uOffset;
    float h = waveHeight(world);
    vWave = h;

    vec3 pos = position;
    pos.x += uOffset.x;
    pos.z += uOffset.y;
    pos.y = h;

    // Surface normal from finite differences of the same wave function.
    float e = 0.45;
    float hL = waveHeight(world - vec2(e, 0.0));
    float hR = waveHeight(world + vec2(e, 0.0));
    float hD = waveHeight(world - vec2(0.0, e));
    float hU = waveHeight(world + vec2(0.0, e));
    vNormal = normalize(vec3(hL - hR, 2.0 * e, hD - hU));

    vec4 wp = modelMatrix * vec4(pos, 1.0);
    vWorld = wp.xyz;

    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const fragmentShader = /* glsl */ `
  uniform float uTime;
  uniform vec3 uDeep;
  uniform vec3 uShallow;
  uniform vec3 uSky;
  uniform vec3 uHorizon;
  uniform vec3 uSunDir;
  uniform vec3 uCamPos;

  varying vec3 vWorld;
  varying vec3 vNormal;
  varying float vWave;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(uCamPos - vWorld);

    float fres = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 3.0);

    vec3 base = mix(uDeep, uShallow, smoothstep(-1.5, 2.6, vWave));
    vec3 col = mix(base, uSky, fres * 0.85);

    // Sun glint.
    vec3 L = normalize(uSunDir);
    vec3 H = normalize(L + V);
    float spec = pow(max(dot(N, H), 0.0), 460.0);
    col += vec3(1.0, 0.94, 0.82) * spec * 1.0;

    // Translucent glow on the wave crests.
    float crest = smoothstep(1.0, 2.4, vWave);
    col += uShallow * crest * 0.55;

    // Foam near the highest crests, broken up by a bit of procedural noise.
    float foam = smoothstep(1.95, 2.7, vWave);
    float n = sin(vWorld.x * 2.7 + uTime * 1.7) *
              sin(vWorld.z * 3.3 - uTime * 2.1);
    foam *= 0.55 + 0.45 * (n * 0.5 + 0.5);
    col = mix(col, vec3(0.93, 0.98, 1.0), foam * 0.85);

    // Fade into the horizon color with distance.
    float d = length(uCamPos - vWorld);
    col = mix(col, uHorizon, smoothstep(130.0, 380.0, d));

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function createOcean() {
  const geometry = new THREE.PlaneGeometry(SIZE, SIZE, SEGMENTS, SEGMENTS);
  geometry.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uOffset: { value: new THREE.Vector2() },
    uDeep: { value: new THREE.Color(0x114b67) },
    uShallow: { value: new THREE.Color(0x1a9ab0) },
    uSky: { value: new THREE.Color(0xaddcf3) },
    uHorizon: { value: new THREE.Color(0xcfe8f2) },
    uSunDir: { value: new THREE.Vector3(0.5, 0.45, -0.72).normalize() },
    uCamPos: { value: new THREE.Vector3() },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    side: THREE.FrontSide,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  return {
    mesh,
    uniforms,
    update(time, cameraPos) {
      uniforms.uTime.value = time;
      uniforms.uOffset.value.set(
        Math.round(cameraPos.x / SNAP) * SNAP,
        Math.round(cameraPos.z / SNAP) * SNAP,
      );
      uniforms.uCamPos.value.copy(cameraPos);
    },
  };
}
