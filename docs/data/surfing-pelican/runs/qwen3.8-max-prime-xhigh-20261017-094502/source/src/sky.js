import * as THREE from "three";
import { GLSL_SKY_COMMON } from "./glsl-common.js";

const VERT = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const FRAG = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uZenith;
uniform vec3 uHorizon;
uniform vec3 uSeaHaze;
uniform vec3 uCloudLit;
uniform vec3 uCloudShade;
varying vec3 vDir;

${GLSL_SKY_COMMON}

float cloudLayer(vec2 cp, float t, float scale, float speed) {
  float n = fbm(cp * scale + vec2(t * speed, t * speed * 0.35));
  float n2 = fbm(cp * scale * 2.7 - vec2(t * speed * 1.6, t * speed * 0.5));
  return smoothstep(0.46, 0.72, n * 0.82 + n2 * 0.28);
}

void main() {
  vec3 d = normalize(vDir);
  float y = d.y;

  // ---- atmosphere gradient
  vec3 col = mix(uHorizon, uZenith, pow(clamp(y, 0.0, 1.0), 0.7));
  // warm band sitting right on the horizon
  col = mix(col, uHorizon * 1.12 + uSunColor * 0.26, exp(-abs(y) * 11.0) * 0.7);
  // below the horizon line: hazy sea mist
  col = mix(uSeaHaze, col, smoothstep(-0.05, 0.012, y));

  // ---- sun
  float sd = max(dot(d, uSunDir), 0.0);
  col += uSunColor * pow(sd, 2400.0) * 26.0;   // disc
  col += uSunColor * pow(sd, 220.0) * 3.4;     // corona
  col += uSunColor * pow(sd, 22.0) * 0.42;     // inner glow
  col += uSunColor * pow(sd, 4.5) * 0.13;      // wide bloom

  // ---- two drifting cloud decks projected onto planes above the viewer
  if (y > 0.004) {
    float t = uTime * 0.55;
    vec2 cp = d.xz / (y + 0.055);

    // a continent-scale mask keeps big clear patches of sky
    float mask = smoothstep(0.26, 0.52, fbm(cp * 0.1 + vec2(3.1, 7.7) + vec2(t * 0.004, 0.0)));
    float high = cloudLayer(cp, t, 0.26, 0.012) * (0.25 + 0.95 * mask);
    float low = cloudLayer(cp + vec2(240.0, -180.0), t, 0.85, 0.024) * (0.2 + 0.9 * mask);
    low *= smoothstep(0.03, 0.34, y);
    high *= smoothstep(0.01, 0.16, y);

    float cover = clamp(high * 1.0 + low * 0.42, 0.0, 1.0);
    float lit = 0.42 + 0.58 * pow(max(dot(d, uSunDir), 0.0), 2.2);
    float density = clamp(high * 0.7 + low * 0.9, 0.0, 1.0);
    vec3 cloudCol = mix(uCloudShade, uCloudLit, lit);
    cloudCol = mix(cloudCol, uCloudShade * 0.82, density * (1.0 - lit) * 0.7);
    // silver lining when looking toward the sun
    cloudCol += uSunColor * pow(sd, 9.0) * cover * 0.35;
    col = mix(col, cloudCol, cover);
  }

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export const SKY_COLORS = {
  zenith: new THREE.Color("#2a6bd0"),
  horizon: new THREE.Color("#f7bd85"),
  seaHaze: new THREE.Color("#e3b489"),
  cloudLit: new THREE.Color("#ffe9c8"),
  cloudShade: new THREE.Color("#6f7fa0"),
  sun: new THREE.Color("#ffe2b0"),
};

export function createSky() {
  const geometry = new THREE.SphereGeometry(1700, 64, 40);
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uSunDir: { value: new THREE.Vector3(0, 1, 0) },
      uSunColor: { value: SKY_COLORS.sun },
      uZenith: { value: SKY_COLORS.zenith },
      uHorizon: { value: SKY_COLORS.horizon },
      uSeaHaze: { value: SKY_COLORS.seaHaze },
      uCloudLit: { value: SKY_COLORS.cloudLit },
      uCloudShade: { value: SKY_COLORS.cloudShade },
    },
    vertexShader: VERT,
    fragmentShader: FRAG,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = -10;

  return {
    mesh,
    material,
    update(t, sunDir) {
      material.uniforms.uTime.value = t;
      if (sunDir) material.uniforms.uSunDir.value.copy(sunDir);
    },
  };
}
