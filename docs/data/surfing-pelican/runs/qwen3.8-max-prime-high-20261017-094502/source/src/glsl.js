/** Shared GLSL snippets (noise, sky lookup, haze) used by sea + foam shaders. */

export const GLSL_NOISE = /* glsl */ `
  float hash21(vec2 p) {
    p = fract(p * vec2(233.34, 851.73));
    p += dot(p, p + 23.45);
    return fract(p.x * p.y);
  }

  float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) {
      v += a * vnoise(p);
      p = p * 2.03 + vec2(11.7, -5.3);
      a *= 0.5;
    }
    return v;
  }
`;

/**
 * Cheap analytic sky used for reflections. Must agree with src/sky.js so the
 * sea reflects the same sky the camera sees.
 */
export function glslSky(sunDirJS) {
  return /* glsl */ `
  uniform vec3 uSunDir;
  uniform vec3 uSkyZenith;
  uniform vec3 uSkyMid;
  uniform vec3 uSkyHorizon;
  uniform vec3 uSkyHaze;
  uniform vec3 uSunGlowCol;

  vec3 skyLookup(vec3 dir) {
    float h = dir.y;
    vec3 col = mix(uSkyHorizon, uSkyMid, smoothstep(0.0, 0.22, h));
    col = mix(col, uSkyZenith, smoothstep(0.14, 0.85, h));
    col = mix(col, uSkyHaze, exp(-abs(h) * 13.0) * 0.55);
    float sd = max(dot(dir, uSunDir), 0.0);
    col += uSunGlowCol * (pow(sd, 42.0) * 0.55 + pow(sd, 6.0) * 0.16);
    col += vec3(1.0, 0.96, 0.87) * smoothstep(0.99885, 0.99945, sd) * 3.0;
    col = mix(col, uSkyHaze * 0.92, smoothstep(0.0, -0.10, h));
    return col;
  }
`;
}

export const GLSL_FOG = /* glsl */ `
  uniform vec3 uFogColor;
  uniform float uFogDensity;

  float hazeAmount(float dist) {
    return 1.0 - exp(-pow(max(dist, 0.0) * uFogDensity, 1.55));
  }
`;

export const FOG_DENSITY = 0.0062;
