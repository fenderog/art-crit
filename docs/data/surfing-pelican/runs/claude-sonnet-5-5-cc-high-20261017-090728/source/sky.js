import * as THREE from "three";

export const SUN_DIR = new THREE.Vector3(-0.6, 0.25, -0.75).normalize();

export const noiseGLSL = /* glsl */ `
float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}
float vnoise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  float a = hash21(i), b = hash21(i + vec2(1.0, 0.0));
  float c = hash21(i + vec2(0.0, 1.0)), d = hash21(i + vec2(1.0, 1.0));
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
float fbm(vec2 p) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++) {
    s += a * vnoise(p);
    p = p * 2.03 + vec2(17.3, 9.1);
    a *= 0.5;
  }
  return s;
}
`;

// Golden-hour sky. Expects uniforms: uTime, uSunDir.
export const skyGLSL = /* glsl */ `
${noiseGLSL}
vec3 skyColor(vec3 d, bool withSun, float cloudAmt) {
  float h = max(d.y, 0.0);
  vec3 zen = vec3(0.04, 0.14, 0.40);
  vec3 mid = vec3(0.30, 0.38, 0.66);
  vec3 hor = vec3(0.92, 0.40, 0.18);
  vec3 col = mix(hor, mid, pow(smoothstep(0.0, 0.32, h), 0.55));
  col = mix(col, zen, smoothstep(0.22, 0.95, h));
  float s = max(dot(d, uSunDir), 0.0);
  col += vec3(1.0, 0.36, 0.10) * pow(s, 4.0) * 0.22;
  col += vec3(1.0, 0.62, 0.30) * pow(s, 60.0) * 0.6 + vec3(1.0, 0.8, 0.5) * pow(s, 400.0) * 1.2;
  if (withSun) col += vec3(14.0, 10.0, 6.5) * smoothstep(0.99975, 0.99988, s);

  // layered clouds on a flat plane
  if (d.y > 0.0) {
    vec2 p = d.xz / (d.y + 0.12) * 0.9 + vec2(uTime * 0.012, uTime * 0.004);
    float n = fbm(p * 0.9);
    float n2 = fbm(p * 0.9 + uSunDir.xz * 0.12);
    float cover = smoothstep(0.50, 0.78, n);
    float lit = clamp(0.5 + (n - n2) * 5.0, 0.0, 1.0);
    vec3 shade = mix(vec3(0.30, 0.30, 0.45), vec3(0.62, 0.40, 0.36), pow(1.0 - h, 2.0));
    vec3 bright = mix(vec3(0.95, 0.66, 0.46), vec3(0.95, 0.85, 0.78), h);
    vec3 cc = mix(shade, bright, lit);
    cc += vec3(1.0, 0.6, 0.3) * pow(s, 8.0) * 0.8 * (1.0 - cover * 0.3);
    float fade = smoothstep(0.02, 0.16, d.y);
    col = mix(col, cc, cover * fade * 0.92 * cloudAmt);
  }
  return col;
}
`;

const vertex = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const fragment = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
varying vec3 vDir;
${skyGLSL}
void main() {
  gl_FragColor = vec4(skyColor(normalize(vDir), true, 1.0), 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSky() {
  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: SUN_DIR },
  };
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: vertex,
    fragmentShader: fragment,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(3000, 48, 24), material);
  dome.frustumCulled = false;
  dome.renderOrder = -10;
  return { dome, uniforms, material };
}

// Bake the sky into an environment map for the PBR materials.
export function bakeEnvironment(renderer, skyMaterial) {
  const envScene = new THREE.Scene();
  const m = new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), skyMaterial);
  envScene.add(m);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const rt = pmrem.fromScene(envScene, 0.02);
  pmrem.dispose();
  return rt.texture;
}
