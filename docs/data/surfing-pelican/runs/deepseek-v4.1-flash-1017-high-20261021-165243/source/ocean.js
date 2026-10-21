import * as THREE from "three";

// CPU mirror of the GLSL wave function, used to keep the board on the surface.
export function waveHeight(x, z, t) {
  let h = 0;
  h += Math.sin(x * 0.16 + t * 0.9) * Math.cos(z * 0.12 + t * 0.7) * 1.05;
  h += Math.sin((x + z) * 0.21 - t * 1.25) * 0.55;
  h += Math.sin(x * 0.45 - z * 0.3 + t * 2.0) * 0.18;
  h += Math.sin(x * 0.9 + z * 0.6 + t * 2.8) * 0.07;
  return h;
}

export function waveNormal(x, z, t) {
  const e = 0.35;
  const hx = waveHeight(x + e, z, t) - waveHeight(x - e, z, t);
  const hz = waveHeight(x, z + e, t) - waveHeight(x, z - e, t);
  return new THREE.Vector3(-hx, 2 * e, -hz).normalize();
}

const vertexShader = /* glsl */ `
uniform float uTime;
varying vec3 vWorldPos;
varying vec3 vNormalW;
varying float vH;

float wave(vec2 p, float t) {
  float h = 0.0;
  h += sin(p.x * 0.16 + t * 0.9) * cos(p.y * 0.12 + t * 0.7) * 1.05;
  h += sin((p.x + p.y) * 0.21 - t * 1.25) * 0.55;
  h += sin(p.x * 0.45 - p.y * 0.3 + t * 2.0) * 0.18;
  h += sin((p.x * 0.9 + p.y * 0.6) + t * 2.8) * 0.07;
  return h;
}

void main() {
  vec3 pos = position;
  float h = wave(pos.xz, uTime);
  pos.y += h;

  float e = 0.35;
  float hx = wave(pos.xz + vec2(e, 0.0), uTime) - wave(pos.xz - vec2(e, 0.0), uTime);
  float hz = wave(pos.xz + vec2(0.0, e), uTime) - wave(pos.xz - vec2(0.0, e), uTime);
  vec3 n = normalize(vec3(-hx, 2.0 * e, -hz));

  vec4 wp = modelMatrix * vec4(pos, 1.0);
  vWorldPos = wp.xyz;
  vNormalW = normalize(mat3(modelMatrix) * n);
  vH = h;

  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFoam;
uniform vec3 uHorizon;

varying vec3 vWorldPos;
varying vec3 vNormalW;
varying float vH;

void main() {
  vec2 p = vWorldPos.xz;
  float t = uTime;

  // Fine ripples break up the specular highlights into glitter.
  float ph1 = p.x * 1.9 + p.y * 1.1 + t * 2.1;
  float ph2 = p.x * -0.8 + p.y * 2.4 - t * 1.7;
  float ph3 = p.x * 4.2 + p.y * 3.6 + t * 3.1;
  vec3 detail = vec3(
    -cos(ph1) * 1.9 * 0.045 - cos(ph2) * -0.8 * 0.036 + cos(ph3) * 4.2 * 0.006,
    0.0,
    -cos(ph1) * 1.1 * 0.045 - cos(ph2) * 2.4 * 0.036 + cos(ph3) * 3.6 * 0.006
  );
  vec3 N = normalize(vNormalW + detail);
  vec3 V = normalize(cameraPosition - vWorldPos);

  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.0);
  float heightMix = smoothstep(-1.5, 1.4, vH);

  vec3 water = mix(uDeep, uShallow, clamp(heightMix * 0.7 + 0.12, 0.0, 1.0));

  vec3 skyRef = mix(vec3(1.0, 0.79, 0.54), vec3(0.42, 0.71, 0.84),
                    smoothstep(-0.4, 0.65, N.y));
  water = mix(water, skyRef, fres * 0.55);

  float diff = max(dot(N, uSunDir), 0.0);
  water += vec3(1.0, 0.78, 0.48) * diff * 0.13;

  vec3 H = normalize(uSunDir + V);
  float spec = pow(max(dot(N, H), 0.0), 110.0);
  water += vec3(1.0, 0.86, 0.6) * spec * 1.15;

  float ripple = sin(p.x * 2.7 + t * 1.3 + sin(p.y * 1.9 - t * 0.9) * 2.0)
               * sin(p.y * 3.1 - t * 1.1);
  float crest = smoothstep(0.45, 1.2, vH + ripple * 0.22);
  float lace = smoothstep(0.5, 0.95, sin(p.x * 1.4 + p.y * 2.2 + t * 0.7 + sin(p.y * 0.7) * 2.0) * 0.5 + 0.5);
  float foam = crest * (0.5 + lace * 0.35) + smoothstep(1.25, 1.7, vH) * 0.35;
  water = mix(water, uFoam, clamp(foam, 0.0, 1.0) * 0.85);

  float dist = length(cameraPosition - vWorldPos);
  float fog = 1.0 - exp(-pow(dist * 0.0034, 1.7));
  water = mix(water, uHorizon, clamp(fog, 0.0, 1.0));

  gl_FragColor = vec4(water, 1.0);
}
`;

export function createOcean() {
  const geometry = new THREE.PlaneGeometry(520, 520, 340, 340);
  geometry.rotateX(-Math.PI / 2);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uSunDir: { value: new THREE.Vector3(-0.4, 0.26, -0.88).normalize() },
      uDeep: { value: new THREE.Color("#0a4659") },
      uShallow: { value: new THREE.Color("#168394") },
      uFoam: { value: new THREE.Color("#f8efe0") },
      uHorizon: { value: new THREE.Color("#e9c8a5") },
    },
    vertexShader,
    fragmentShader,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  return {
    mesh,
    update(t) {
      material.uniforms.uTime.value = t;
    },
  };
}
