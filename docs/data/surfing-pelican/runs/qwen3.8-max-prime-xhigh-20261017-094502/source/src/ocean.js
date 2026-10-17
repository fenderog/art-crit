import * as THREE from "three";
import { OCEAN_GLSL, MAX_HEIGHT, oceanHeight, oceanNormal } from "./waves.js";
import { GLSL_SKY_COMMON } from "./glsl-common.js";

/* ---------------------------------------------------------------- geometry */

/**
 * A polar ("clipmap-ish") disc: dense rings near the surfer where the camera
 * gets close, rings that widen geometrically toward the horizon. One mesh, so
 * there is no seam to hide, and ~40k vertices cover a 1.8km wide sea.
 */
export function createOceanGeometry({
  minSpacing = 0.42,
  detailRadius = 34,
  maxRadius = 900,
  maxRings = 300,
  angular = 288,
} = {}) {
  const radii = [];
  let r = minSpacing;
  while (r < maxRadius && radii.length < maxRings) {
    radii.push(r);
    r += Math.min(minSpacing * (1 + Math.pow(r / detailRadius, 1.85)), 52);
  }
  radii.push(maxRadius);

  const rings = radii.length;
  const ringCount = angular + 1; // duplicated seam column for clean uv/wrap
  const positions = new Float32Array((1 + rings * ringCount) * 3);
  const indices = [];

  // centre vertex
  positions[0] = 0;
  positions[1] = 0;
  positions[2] = 0;

  let vi = 1;
  for (let i = 0; i < rings; i++) {
    const rad = radii[i];
    for (let j = 0; j < ringCount; j++) {
      const a = (j / angular) * Math.PI * 2;
      const o = vi * 3;
      positions[o] = Math.cos(a) * rad;
      positions[o + 1] = 0;
      positions[o + 2] = Math.sin(a) * rad;
      vi++;
    }
  }

  // centre fan (wound so the geometric normal points +Y)
  for (let j = 0; j < angular; j++) {
    indices.push(0, 1 + j + 1, 1 + j);
  }
  // ring quads
  for (let i = 1; i < rings; i++) {
    const a0 = 1 + (i - 1) * ringCount; // inner ring
    const b0 = 1 + i * ringCount; // outer ring
    for (let j = 0; j < angular; j++) {
      indices.push(a0 + j, a0 + j + 1, b0 + j + 1);
      indices.push(a0 + j, b0 + j + 1, b0 + j);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), maxRadius * 1.2);
  return geo;
}

/* ------------------------------------------------------------------ shader */

const VERT = /* glsl */ `
uniform float uTime;
varying vec3 vWorld;
varying vec3 vNrm;
varying float vH;
varying float vSlope;

${OCEAN_GLSL}

void main() {
  vec2 xz = position.xz;
  float r = length(xz);
  // the far sea flattens out: keeps the horizon clean and kills ring aliasing
  float flatten = 1.0 - smoothstep(220.0, 700.0, r);
  float h = oceanHeight(xz, uTime) * flatten;
  vec2 sl = oceanSlope(xz, uTime) * flatten;
  vec3 p = vec3(position.x, h, position.z);
  vNrm = normalize(vec3(-sl.x, 1.0, -sl.y));
  vH = h;
  vSlope = length(sl);
  vec4 wp = modelMatrix * vec4(p, 1.0);
  vWorld = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uDeep;
uniform vec3 uMid;
uniform vec3 uShallow;
uniform vec3 uFoamColor;
uniform vec3 uZenith;
uniform vec3 uHorizon;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform float uMaxH;
uniform float uWhitecaps;
uniform vec2 uSplash;      // xy of the board
uniform float uSplashAmt;  // extra foam kicked up around the board

varying vec3 vWorld;
varying vec3 vNrm;
varying float vH;
varying float vSlope;

${OCEAN_GLSL}
${GLSL_SKY_COMMON}

void main() {
  vec3 V = normalize(cameraPosition - vWorld);
  float dist = length(cameraPosition - vWorld);

  // surface normal = swell slope (vertex) + wind chop (per-pixel, faded out far away)
  float detail = 1.0 - smoothstep(24.0, 110.0, dist);
  vec2 chop = chopSlope(vWorld.xz, uTime) * detail;
  vec3 N = normalize(vec3(vNrm.x - chop.x * 2.2, vNrm.y, vNrm.z - chop.y * 2.2));

  float crest = clamp(vH / uMaxH, -1.0, 1.0);
  float facing = clamp(dot(N, V), 0.0, 1.0);

  // ---- body colour: deep troughs -> translucent crests
  vec3 water = mix(uDeep, uMid, smoothstep(-0.62, 0.34, crest));
  water = mix(water, uShallow, smoothstep(0.3, 0.92, crest) * 0.85);

  // ---- sky reflection (fresnel weighted)
  vec3 R = reflect(-V, N);
  vec3 sky = skyRadiance(R, uSunDir, uZenith, uHorizon, uSunColor, uMid * 0.8 + uHorizon * 0.14);
  float fres = 0.02 + 0.98 * pow(1.0 - facing, 5.0);
  vec3 col = mix(water, sky, clamp(fres, 0.0, 1.0) * 0.72);

  // ---- backlit translucency through the wave face
  vec3 sssDir = normalize(uSunDir + N * 0.35);
  float sss = pow(clamp(dot(V, -sssDir), 0.0, 1.0), 3.0) * smoothstep(-0.05, 0.75, crest);
  col += uShallow * sss * 0.8;
  col += uSunColor * sss * 0.18;

  // ---- sun glints
  vec3 H = normalize(uSunDir + V);
  float ndh = max(dot(N, H), 0.0);
  float glitterMask = fbm(vWorld.xz * 1.9 + vec2(uTime * 0.25, -uTime * 0.18));
  float spec = pow(ndh, 900.0) * (0.55 + 0.9 * glitterMask) * 3.6;
  spec += pow(ndh, 140.0) * 0.10;
  spec *= 1.0 - smoothstep(300.0, 700.0, dist);
  col += uSunColor * spec;

  // ---- whitecaps: only some crests actually break
  float n1 = fbm(vWorld.xz * 0.42 + vec2(uTime * 0.10, -uTime * 0.06));
  float n2 = fbm(vWorld.xz * 1.7 - vec2(uTime * 0.22, uTime * 0.13));
  float gate = smoothstep(0.52, 0.74, n1);
  float capMask = smoothstep(0.25, 0.95, crest) * 0.85 + vSlope * 1.05;
  float caps = smoothstep(0.72, 1.05, capMask) * gate;
  caps *= uWhitecaps;
  caps *= 1.0 - smoothstep(260.0, 620.0, dist) * 0.75;

  // foam stirred up by the board
  float dS = length(vWorld.xz - uSplash);
  float churn = smoothstep(3.4, 0.2, dS);
  caps = max(caps, churn * uSplashAmt * smoothstep(0.3, 0.72, n2));

  float foamShade = 0.72 + 0.28 * n2;
  col = mix(col, uFoamColor * foamShade, clamp(caps, 0.0, 0.95));
  col += uSunColor * caps * pow(ndh, 20.0) * 0.35;

  // ---- distance fog, warmed toward the sun near the horizon
  float fogAmt = 1.0 - exp(-pow(max(dist - 6.0, 0.0) * uFogDensity, 1.85));
  vec3 fogCol = uFogColor;
  float sunAz = pow(max(dot(normalize(vec3(V.x, 0.0, V.z)), normalize(vec3(uSunDir.x, 0.0, uSunDir.z))), 0.0), 4.0);
  fogCol = mix(fogCol, uHorizon * 1.05 + uSunColor * 0.35, sunAz * 0.55);
  col = mix(col, fogCol, clamp(fogAmt, 0.0, 1.0));
  // settle the mid-distance into a calmer tone so the swell pattern reads soft
  col = mix(col, uMid * 0.8 + uHorizon * 0.18, smoothstep(40.0, 210.0, dist) * 0.75);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

/* ------------------------------------------------------------------ public */

export const OCEAN_COLORS = {
  deep: new THREE.Color("#053a48"),
  mid: new THREE.Color("#0a5a68"),
  shallow: new THREE.Color("#26a896"),
  foam: new THREE.Color("#eefaff"),
  zenith: new THREE.Color("#2b62a8"),
  horizon: new THREE.Color("#f7bd85"),
  fog: new THREE.Color("#e3b489"),
};

export function createOcean(uniformOverrides = {}) {
  const geometry = createOceanGeometry();
  const uniforms = Object.assign(
    {
      uTime: { value: 0 },
      uSunDir: { value: new THREE.Vector3(0, 1, 0) },
      uSunColor: { value: new THREE.Color("#ffd9a3") },
      uDeep: { value: OCEAN_COLORS.deep },
      uMid: { value: OCEAN_COLORS.mid },
      uShallow: { value: OCEAN_COLORS.shallow },
      uFoamColor: { value: OCEAN_COLORS.foam },
      uZenith: { value: OCEAN_COLORS.zenith },
      uHorizon: { value: OCEAN_COLORS.horizon },
      uFogColor: { value: OCEAN_COLORS.fog },
      uFogDensity: { value: 0.0052 },
      uMaxH: { value: MAX_HEIGHT },
      uWhitecaps: { value: 0.55 },
      uSplash: { value: new THREE.Vector2(0, 0) },
      uSplashAmt: { value: 0 },
    },
    uniformOverrides
  );

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: VERT,
    fragmentShader: FRAG,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = -1;

  const _n = new THREE.Vector3();

  return {
    mesh,
    material,
    uniforms,
    /** height of the simulated sea at a world position */
    heightAt: (x, z, t) => oceanHeight(x, z, t),
    normalAt: (x, z, t, target = _n) => oceanNormal(x, z, t, target),
    setSplash(x, z, amount) {
      uniforms.uSplash.value.set(x, z);
      uniforms.uSplashAmt.value = amount;
    },
    update(t, dt, sunDir) {
      uniforms.uTime.value = t;
      if (sunDir) uniforms.uSunDir.value.copy(sunDir);
    },
  };
}
