import * as THREE from 'three';
import { WAVE_GLSL } from './waves.js';
import { makeNoiseTexture } from './textures.js';

const VERT = /* glsl */ `
uniform float uTime;
varying vec3 vWorldPos;
${WAVE_GLSL}
void main() {
  vec3 pos = position;
  float h;
  vec2 g;
  waveEval(pos.xz, uTime, h, g);
  pos.y += h;
  vec4 wp = modelMatrix * vec4(pos, 1.0);
  vWorldPos = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */ `
uniform float uTime;
uniform vec3 uCamPos;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uSkyTop;
uniform vec3 uHorizon;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFoamColor;
uniform vec2 uFogRange;
uniform sampler2D uNoise;
varying vec3 vWorldPos;
${WAVE_GLSL}
void main() {
  // per-pixel wave normal: smooth shading + exact match with the displacement
  float h;
  vec2 grad;
  waveEval(vWorldPos.xz, uTime, h, grad);
  vec3 n = normalize(vec3(-grad.x, 1.0, -grad.y));

  // fine ripple detail from the noise texture
  vec2 uv = vWorldPos.xz * 0.13 + vec2(uTime * 0.014, uTime * 0.009);
  float e = 0.085;
  float r0 = texture2D(uNoise, uv).r;
  float rx = texture2D(uNoise, uv + vec2(e, 0.0)).r;
  float rz = texture2D(uNoise, uv + vec2(0.0, e)).r;
  n = normalize(n + vec3((r0 - rx), 0.0, (r0 - rz)) * 1.15);

  vec3 viewDir = normalize(uCamPos - vWorldPos);
  float fres = pow(1.0 - clamp(dot(n, viewDir), 0.0, 1.0), 5.0);

  // water body colour: deep in troughs, lighter over the crests
  vec3 base = mix(uDeep, uShallow, clamp(h * 0.42 + 0.3, 0.0, 1.0));
  base = mix(base, uShallow * 1.12, smoothstep(0.55, 1.35, h) * 0.32);

  // sky reflection
  vec3 refl = reflect(-viewDir, n);
  float sky = clamp(refl.y * 1.5, 0.0, 1.0);
  vec3 skyCol = mix(uHorizon, uSkyTop, pow(sky, 0.6));
  skyCol = mix(skyCol, uSkyTop, 0.2);

  vec3 col = mix(base, skyCol, clamp(0.07 + fres * 0.82, 0.0, 1.0));

  // sun sparkle: tight glint + broad sheen
  vec3 halfV = normalize(uSunDir + viewDir);
  float ndh = max(dot(n, halfV), 0.0);
  col += uSunColor * (pow(ndh, 320.0) * 2.6 + pow(ndh, 26.0) * 0.16);

  // foam on steep faces and crests
  float foamA = texture2D(uNoise, vWorldPos.xz * 0.072 + vec2(uTime * 0.006, -uTime * 0.0045)).r;
  float foamB = texture2D(uNoise, vWorldPos.xz * 0.185 - vec2(uTime * 0.012, uTime * 0.008)).r;
  float crest = smoothstep(0.85, 1.55, h);
  float steep = smoothstep(0.16, 0.36, 1.0 - n.y);
  float foam = crest * smoothstep(0.5, 0.92, foamA * 0.66 + foamB * 0.55);
  foam += steep * smoothstep(0.6, 0.95, foamB) * 0.45;
  foam = clamp(foam, 0.0, 1.0);
  col = mix(col, uFoamColor, foam * 0.8);

  // haze into the horizon so the water meets the sky seamlessly
  float dist = length(uCamPos - vWorldPos);
  float fogF = smoothstep(uFogRange.x, uFogRange.y, dist);
  col = mix(col, uHorizon, fogF);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean({ palette, sunDir, size = 460, segments = 340 }) {
  const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
  geometry.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uCamPos: { value: new THREE.Vector3() },
    uSunDir: { value: sunDir.clone() },
    uSunColor: { value: new THREE.Color(palette.sunColor) },
    uSkyTop: { value: new THREE.Color(palette.skyTop) },
    uHorizon: { value: new THREE.Color(palette.skyHorizon) },
    uDeep: { value: new THREE.Color(palette.oceanDeep) },
    uShallow: { value: new THREE.Color(palette.oceanShallow) },
    uFoamColor: { value: new THREE.Color(palette.foam) },
    uFogRange: { value: new THREE.Vector2(70, 235) },
    uNoise: { value: makeNoiseTexture(256) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: VERT,
    fragmentShader: FRAG,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = -5;

  return {
    mesh,
    update(t, camera) {
      uniforms.uTime.value = t;
      uniforms.uCamPos.value.copy(camera.position);
    },
  };
}