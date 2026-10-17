import * as THREE from "three";

// One shared sky function: used for the visible dome and, with the sun disc
// removed, for the image based lighting that the water, board and pelican share.

export const SUN_DIR = new THREE.Vector3(0.3, 0.46, 0.84).normalize();

export const PALETTE = {
  zenith: new THREE.Color("#1747a8"),
  mid: new THREE.Color("#3f9be8"),
  horizon: new THREE.Color("#ffcf97"),
  horizonCool: new THREE.Color("#a9d6f3"),
  sunTint: new THREE.Color("#ffb55c"),
  sunColor: new THREE.Color("#fff1d2"),
  ground: new THREE.Color("#4f9aa6"),
};

const skyFrag = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uZenith;
uniform vec3 uMid;
uniform vec3 uHorizon;
uniform vec3 uHorizonCool;
uniform vec3 uSunTint;
uniform vec3 uSunColor;
uniform vec3 uGround;
uniform float uTime;
uniform float uSunDisc;
varying vec3 vDir;

float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}
float vnoise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash21(i), hash21(i + vec2(1, 0)), f.x),
             mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y);
}
float fbm(vec2 p) {
  float a = 0.5, s = 0.0;
  mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
  for (int i = 0; i < 5; i++) { s += a * vnoise(p); p = m * p; a *= 0.5; }
  return s;
}

vec3 skyColor(vec3 d) {
  float h = d.y;
  float hh = max(h, 0.0);
  float sd = max(dot(d, uSunDir), 0.0);

  vec2 hd = normalize(d.xz + vec2(1e-5));
  vec2 sdn = normalize(uSunDir.xz);
  vec3 hor = mix(uHorizonCool, uHorizon, smoothstep(-0.35, 0.95, dot(hd, sdn)));
  vec3 col = mix(hor, uMid, pow(smoothstep(0.0, 0.3, hh), 0.7));
  col = mix(col, uZenith, smoothstep(0.22, 0.95, hh));

  // warm glow around the sun, stronger low on the horizon
  float lowGlow = exp(-hh * 6.0);
  // (the lighting version keeps only a faint halo: the directional light already is the sun)
  col += uSunTint * (pow(sd, 3.0) * 0.16 * lowGlow + pow(sd, 10.0) * 0.2 + pow(sd, 90.0) * 0.45) * (0.35 + 0.65 * uSunDisc);

  // the sun bleaches the blue around it toward warm white
  col = mix(col, mix(uHorizon, vec3(1.0, 0.95, 0.85), 0.5), pow(sd, 5.0) * 0.55);

  // clouds
  if (h > 0.0) {
    vec2 p = d.xz / (h * 0.85 + 0.16);
    vec2 drift = vec2(uTime * 0.012, uTime * 0.004);
    float n = fbm(p * 0.42 + drift);
    float cover = smoothstep(0.46, 0.74, n);
    float n2 = fbm(p * 0.42 + drift + normalize(uSunDir.xz + 1e-4) * 0.06);
    float lit = clamp((n - n2) * 7.0 + 0.5, 0.0, 1.0);
    float fadeH = smoothstep(0.0, 0.10, h);
    vec3 shade = mix(vec3(0.46, 0.56, 0.74), hor * 0.9, 0.35);
    vec3 bright = mix(vec3(1.0, 0.97, 0.92), uSunTint * 1.5, pow(sd, 4.0) * 0.6);
    vec3 cc = mix(shade, bright, lit);
    // thin high wisps
    float wisp = smoothstep(0.55, 0.9, fbm(vec2(p.x * 0.18, p.y * 0.9) + drift * 0.5 + 7.0)) * 0.35 * smoothstep(0.05, 0.4, h);
    col = mix(col, cc, clamp(cover * fadeH * 0.92 + wisp * fadeH, 0.0, 1.0));
  }

  // below the horizon: the sea's own colour so reflections stay coherent
  vec3 below = mix(hor * 0.92, uGround, smoothstep(0.0, -0.45, h));
  col = mix(col, below, smoothstep(0.015, -0.03, h));

  // sun disc
  col += uSunColor * smoothstep(0.99935, 0.99975, sd) * 18.0 * uSunDisc;
  return col;
}

void main() {
  gl_FragColor = vec4(skyColor(normalize(vDir)), 1.0);
}
`;

const skyVert = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;
  vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  gl_Position = p.xyww;
}
`;

function makeSkyMaterial(disc, depth = false) {
  return new THREE.ShaderMaterial({
    uniforms: {
      uSunDir: { value: SUN_DIR },
      uZenith: { value: PALETTE.zenith },
      uMid: { value: PALETTE.mid },
      uHorizon: { value: PALETTE.horizon },
      uHorizonCool: { value: PALETTE.horizonCool },
      uSunTint: { value: PALETTE.sunTint },
      uSunColor: { value: PALETTE.sunColor },
      uGround: { value: PALETTE.ground },
      uTime: { value: 0 },
      uSunDisc: { value: disc },
    },
    vertexShader: skyVert,
    fragmentShader: skyFrag,
    side: THREE.BackSide,
    depthWrite: false,
    depthTest: depth,
  });
}

export function createSky(renderer) {
  const geo = new THREE.SphereGeometry(1000, 48, 24);
  // drawn after the opaque scene and depth-tested at the far plane, so it only shades the pixels the sea does not cover
  const mesh = new THREE.Mesh(geo, makeSkyMaterial(1, true));
  mesh.frustumCulled = false;
  mesh.renderOrder = 5;

  // environment (no sun disc: the directional light supplies the sun itself)
  const envScene = new THREE.Scene();
  const envMesh = new THREE.Mesh(geo, makeSkyMaterial(0));
  envMesh.frustumCulled = false;
  envScene.add(envMesh);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envRT = pmrem.fromScene(envScene, 0, 1, 3000);
  pmrem.dispose();

  return {
    mesh,
    envMap: envRT.texture,
    update(camera, t) {
      mesh.position.copy(camera.position);
      mesh.material.uniforms.uTime.value = t;
    },
  };
}
