import * as THREE from "three";
import { PALETTE, SUN_DIR } from "./palette.js";
import { wavesUniforms, wavesGLSL } from "./waves.js";
import { GLSL_NOISE, GLSL_FOG, glslSky, FOG_DENSITY } from "./glsl.js";

/**
 * Uniform objects shared by the sky dome, the ocean and the foam trail so that
 * every surface agrees on where the sun is, what colour the haze is and what
 * moment in time it is.
 */
export const shared = {
  uTime: { value: 0 },
  uWaveAmp: { value: 1 },
  uSunDir: { value: SUN_DIR.clone() },
  uSkyZenith: { value: new THREE.Color(PALETTE.zenith) },
  uSkyMid: { value: new THREE.Color(PALETTE.midSky) },
  uSkyHorizon: { value: new THREE.Color(PALETTE.horizonSky) },
  uSkyHaze: { value: new THREE.Color(PALETTE.haze) },
  uSunGlowCol: { value: new THREE.Color(PALETTE.sunGlow) },
  uFogColor: { value: new THREE.Color(PALETTE.haze) },
  uFogDensity: { value: FOG_DENSITY },
  ...wavesUniforms(),
};

/* ------------------------------------------------------------------ */

const OCEAN_VERT = /* glsl */ `
  ${wavesGLSL()}
  varying vec3 vWorld;
  varying vec3 vNrm;
  varying float vCrest;
  varying float vHeight;
  varying float vDist;

  void main() {
    vec2 p = vec2(position.x, position.z);
    vec3 nrm;
    float crest;
    vec3 displaced = gerstnerSea(p, uTime, nrm, crest);

    vWorld = displaced;
    vNrm = nrm;
    vCrest = crest;
    vHeight = displaced.y;
    vDist = distance(cameraPosition, displaced);

    gl_Position = projectionMatrix * viewMatrix * vec4(displaced, 1.0);
  }
`;

const OCEAN_FRAG = /* glsl */ `
  precision highp float;
  ${GLSL_NOISE}
  ${glslSky()}
  ${GLSL_FOG}
  uniform float uTime;
  uniform vec3 uDeep;
  uniform vec3 uMid;
  uniform vec3 uShallow;
  uniform vec3 uFoamCol;
  uniform vec3 uSSS;
  uniform vec3 uSunCol;

  varying vec3 vWorld;
  varying vec3 vNrm;
  varying float vCrest;
  varying float vHeight;
  varying float vDist;

  float ripple(vec2 p) {
    return vnoise(p) * 0.62 + vnoise(p * 2.37 + 4.1) * 0.38;
  }

  void main() {
    vec3 V = normalize(cameraPosition - vWorld);
    vec3 N = normalize(vNrm);
    vec3 L = normalize(uSunDir);

    // --- micro surface detail, faded out with distance -------------------
    float detail = 1.0 - smoothstep(14.0, 62.0, vDist);
    if (detail > 0.001) {
      vec2 np = vWorld.xz * 2.1 + vec2(uTime * 0.42, -uTime * 0.27);
      float e = 0.16;
      float h0 = ripple(np);
      float hx = ripple(np + vec2(e, 0.0));
      float hz = ripple(np + vec2(0.0, e));
      N = normalize(N + vec3(-(hx - h0), 0.0, -(hz - h0)) * (0.85 * detail));
    }

    float ndv = clamp(dot(N, V), 0.0, 1.0);

    // --- body colour: deep troughs, teal shoulders, bright crests --------
    vec3 body = mix(uDeep, uMid, smoothstep(-1.5, 1.1, vHeight));
    body = mix(body, uShallow, smoothstep(0.35, 1.9, vHeight) * 0.75);

    // --- sky reflection with fresnel -------------------------------------
    vec3 R = reflect(-V, N);
    vec3 sky = skyLookup(R);
    float fres = 0.022 + 0.978 * pow(1.0 - ndv, 5.0);
    vec3 col = mix(body, sky, clamp(fres, 0.0, 1.0));

    // --- translucency where light passes through a thin crest ------------
    float back = pow(clamp(dot(V, -L) * 0.5 + 0.5, 0.0, 1.0), 4.0);
    float thin = smoothstep(0.15, 1.7, vHeight) * (0.45 + 0.55 * vCrest);
    col += uSSS * back * thin * 0.85;

    // --- sun specular: tight glitter + soft sheen ------------------------
    vec3 H = normalize(L + V);
    float ndh = max(dot(N, H), 0.0);
    float sparkle = mix(0.35, 1.65, vnoise(vWorld.xz * 6.5 + uTime * 0.6));
    float specTight = pow(ndh, 620.0) * 5.5 * sparkle;
    float specWide = pow(ndh, 34.0) * 0.42;
    float glintMask = smoothstep(0.0, 0.35, ndh);
    col += uSunCol * (specTight + specWide) * glintMask;

    // --- whitecaps & chop foam -------------------------------------------
    float streak = fbm(vWorld.xz * 0.42 + vec2(-uTime * 0.85, uTime * 0.12));
    float wc = smoothstep(0.24, 0.52, vCrest + (streak - 0.5) * 0.30);
    float chop = smoothstep(0.55, 0.95, streak) * smoothstep(-0.1, 0.6, vCrest) * 0.35;
    float bubbles = smoothstep(0.62, 0.88, fbm(vWorld.xz * 3.1 + uTime * 0.5));
    float foam = clamp(wc * (0.45 + 0.75 * bubbles) + chop * bubbles, 0.0, 1.0);
    foam *= 1.0 - smoothstep(120.0, 260.0, vDist);   // no foam specks in the haze
    vec3 foamLit = mix(uFoamCol, uFoamCol * 0.72 + uSunCol * 0.35, 1.0 - ndv);
    col = mix(col, foamLit, foam);

    // --- haze to the horizon ---------------------------------------------
    col = mix(col, uFogColor, hazeAmount(vDist));

    gl_FragColor = vec4(col, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

/* ------------------------------------------------------------------ */

/** Ring of water from `inner` to `outer` with geometric radial spacing. */
function farRingGeometry(inner, outer, thetaSegs, radialSegs) {
  const positions = [];
  const indices = [];
  const ratio = outer / inner;

  for (let j = 0; j <= radialSegs; j++) {
    const r = inner * Math.pow(ratio, j / radialSegs);
    for (let i = 0; i <= thetaSegs; i++) {
      const a = (i / thetaSegs) * Math.PI * 2;
      positions.push(Math.cos(a) * r, 0, Math.sin(a) * r);
    }
  }
  const row = thetaSegs + 1;
  for (let j = 0; j < radialSegs; j++) {
    for (let i = 0; i < thetaSegs; i++) {
      const a = j * row + i;
      const b = a + 1;
      const c = a + row;
      const d = c + 1;
      indices.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeBoundingSphere();
  return geo;
}

export function createOcean() {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      ...shared,
      uDeep: { value: new THREE.Color(PALETTE.deepWater) },
      uMid: { value: new THREE.Color(PALETTE.midWater) },
      uShallow: { value: new THREE.Color(PALETTE.shallowWater) },
      uFoamCol: { value: new THREE.Color(PALETTE.foam) },
      uSSS: { value: new THREE.Color("#2fd0a2") },
      uSunCol: { value: new THREE.Color("#ffe6bb") },
    },
    vertexShader: OCEAN_VERT,
    fragmentShader: OCEAN_FRAG,
    side: THREE.FrontSide,
    fog: false,
  });

  const hero = new THREE.PlaneGeometry(250, 250, 250, 250);
  hero.rotateX(-Math.PI / 2);
  const heroMesh = new THREE.Mesh(hero, material);
  heroMesh.name = "ocean-hero";
  heroMesh.frustumCulled = false;

  const far = farRingGeometry(110, 3200, 168, 40);
  const farMesh = new THREE.Mesh(far, material);
  farMesh.name = "ocean-far";
  farMesh.frustumCulled = false;

  const group = new THREE.Group();
  group.add(heroMesh, farMesh);

  return { group, material, shared };
}
