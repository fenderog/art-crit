import * as THREE from "three";
import {
  SUN_DIR,
  horizonColor,
  skyTopColor,
  zenithColor,
  warmColor,
  sunColor,
  cloudLitColor,
  cloudShadowColor,
} from "./theme.js";

const skyUniforms = {
  uSunDir: { value: SUN_DIR.clone() },
  uHorizon: { value: horizonColor.clone() },
  uTop: { value: skyTopColor.clone() },
  uZenith: { value: zenithColor.clone() },
  uWarm: { value: warmColor.clone() },
  uSun: { value: sunColor.clone() },
  uCloudLit: { value: cloudLitColor.clone() },
  uCloudShadow: { value: cloudShadowColor.clone() },
  uTime: { value: 0 },
};

const vertexShader = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const fragmentShader = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uHorizon;
uniform vec3 uTop;
uniform vec3 uZenith;
uniform vec3 uWarm;
uniform vec3 uSun;
uniform vec3 uCloudLit;
uniform vec3 uCloudShadow;
uniform float uTime;
varying vec3 vDir;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  float a = hash(i);
  float b = hash(i + vec2(1.0, 0.0));
  float c = hash(i + vec2(0.0, 1.0));
  float d = hash(i + vec2(1.0, 1.0));
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
  float v = 0.0;
  float a = 0.5;
  for (int i = 0; i < 5; i++) {
    v += a * noise(p);
    p = p * 2.05 + vec2(1.7, 9.2);
    a *= 0.5;
  }
  return v;
}

void main() {
  vec3 dir = normalize(vDir);
  float h = dir.y;
  vec3 col = mix(uHorizon, uTop, smoothstep(0.0, 0.2, h));
  col = mix(col, uZenith, smoothstep(0.08, 0.5, h));
  float band = 1.0 - smoothstep(0.0, 0.18, abs(h));
  col = mix(col, uWarm, band * 0.55);

  float sd = max(dot(dir, uSunDir), 0.0);
  col += uSun * pow(sd, 1400.0) * 1.8;
  col += uSun * pow(sd, 18.0) * 0.5;
  col += uSun * pow(sd, 4.0) * 0.16;

  if (dir.y > 0.0) {
    vec2 uv = dir.xz / (dir.y + 0.15);
    float n = fbm(uv * 0.72 + vec2(uTime * 0.0035, 0.2));
    float cloud = smoothstep(0.4, 0.72, n);
    float shade = smoothstep(0.5, 0.85, fbm(uv * 1.3 + vec2(4.0, uTime * 0.002)));
    vec3 cloudCol = mix(uCloudShadow, uCloudLit, 0.3 + 0.7 * shade);
    cloudCol += uSun * pow(sd, 2.0) * 0.18;
    float mask = smoothstep(0.02, 0.16, dir.y) * (1.0 - smoothstep(0.45, 0.85, dir.y));
    col = mix(col, cloudCol, cloud * mask * 0.88);
  }

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

function createGull() {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0xf7f4ef, roughness: 0.68 });
  const wingMat = new THREE.MeshStandardMaterial({ color: 0xd5d0c8, roughness: 0.64 });
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 8), bodyMat);
  body.scale.set(0.5, 0.42, 1.35);
  const wingGeo = new THREE.BoxGeometry(0.52, 0.02, 0.13);
  const wingL = new THREE.Mesh(wingGeo, wingMat);
  wingL.position.set(-0.3, 0.02, 0.02);
  const wingR = new THREE.Mesh(wingGeo, wingMat);
  wingR.position.set(0.3, 0.02, 0.02);
  g.add(body, wingL, wingR);
  g.userData.wingL = wingL;
  g.userData.wingR = wingR;
  return g;
}

export function createSky() {
  const geo = new THREE.SphereGeometry(420, 40, 28);
  const mesh = new THREE.Mesh(
    geo,
    new THREE.ShaderMaterial({
      uniforms: skyUniforms,
      vertexShader,
      fragmentShader,
      side: THREE.BackSide,
      depthWrite: false,
    }),
  );
  mesh.frustumCulled = false;
  mesh.renderOrder = -1;

  const gulls = [];
  const phases = [0.4, 2.1, 4.0];
  const radii = [20, 27, 24];
  const heights = [9.5, 12.5, 10.5];
  for (let i = 0; i < 3; i++) {
    const g = createGull();
    g.userData.phase = phases[i];
    g.userData.radius = radii[i];
    g.userData.height = heights[i];
    gulls.push(g);
  }

  return {
    mesh,
    gulls,
    update(time) {
      skyUniforms.uTime.value = time;
      for (const g of gulls) {
        const a = time * 0.18 + g.userData.phase;
        const radius = g.userData.radius;
        const x = Math.cos(a) * radius;
        const z = Math.sin(a) * radius * 0.62;
        const y = g.userData.height + Math.sin(time * 0.5 + g.userData.phase) * 0.35;
        g.position.set(x, y, z);
        const dx = -Math.sin(a);
        const dz = Math.cos(a) * 0.62;
        // -Z front faces travel d: yaw = atan2(-d.x, -d.z).
        g.rotation.y = Math.atan2(-dx, -dz);
        g.rotation.z = -dx * 0.25;
        const flap = Math.sin(time * 7.5 + g.userData.phase) * 0.42;
        g.userData.wingL.rotation.z = -0.2 - flap;
        g.userData.wingR.rotation.z = 0.2 + flap;
      }
    },
  };
}
