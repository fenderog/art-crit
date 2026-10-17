// Shared GLSL chunks. The sky function is used by the sky dome, by the ocean
// for reflections/fog, and (via PMREM) for image based lighting, so the whole
// scene agrees on one sunset.

export const NOISE_GLSL = /* glsl */ `
float hash12(vec2 p) {
  vec3 p3 = fract(vec3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}
float vnoise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  float a = hash12(i);
  float b = hash12(i + vec2(1.0, 0.0));
  float c = hash12(i + vec2(0.0, 1.0));
  float d = hash12(i + vec2(1.0, 1.0));
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
// value noise + analytic gradient (x: value, yz: d/dp)
vec3 vnoised(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  vec2 du = 6.0 * f * (1.0 - f);
  float a = hash12(i);
  float b = hash12(i + vec2(1.0, 0.0));
  float c = hash12(i + vec2(0.0, 1.0));
  float d = hash12(i + vec2(1.0, 1.0));
  float k = a - b - c + d;
  return vec3(a + (b - a) * u.x + (c - a) * u.y + k * u.x * u.y,
              du * (vec2(b - a, c - a) + k * u.yx));
}
const mat2 FBM_ROT = mat2(1.6, 1.2, -1.2, 1.6);
float fbm(vec2 p) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++) { s += a * vnoise(p); p = FBM_ROT * p; a *= 0.5; }
  return s;
}
float fbm3(vec2 p) {
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 3; i++) { s += a * vnoise(p); p = FBM_ROT * p; a *= 0.5; }
  return s * 1.14;
}
`;

export const SKY_GLSL = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uSkyZenith;
uniform vec3 uSkyMid;
uniform vec3 uSkyHorizon;
uniform vec3 uCloudLit;
uniform vec3 uCloudDark;
uniform float uTime;

vec3 skyColor(vec3 d, float disc) {
  float e = d.y;
  float eh = max(e, 0.0);
  float sd = max(dot(d, uSunDir), 0.0);
  vec3 col = mix(uSkyHorizon, uSkyMid, smoothstep(0.0, 0.2, eh));
  col = mix(col, uSkyZenith, smoothstep(0.12, 0.75, eh));
  // glow around the sun, hugging the horizon
  col += uSunColor * (0.05 * pow(sd, 4.0) + 0.16 * pow(sd, 32.0) + 0.8 * pow(sd, 400.0));
  col += uSunColor * 0.13 * pow(sd, 3.0) * exp(-eh * 14.0);
  float cl = 0.0;
  if (e > 0.004) {
    vec2 uv = d.xz / (e + 0.09);
    uv = uv * 0.5 + vec2(uTime * 0.006, 0.0);
    float n = fbm(uv * vec2(0.5, 1.8));
    float band = smoothstep(0.015, 0.09, e) * (1.0 - smoothstep(0.3, 0.75, e));
    cl = smoothstep(0.46, 0.72, n) * band;
    float edge = 1.0 - smoothstep(0.5, 0.8, n);
    float lit = clamp(0.12 + 0.95 * pow(sd, 4.0) + 0.35 * edge * pow(sd, 1.5), 0.0, 1.0);
    vec3 cc = mix(uCloudDark, uCloudLit, lit);
    cc += uSunColor * pow(sd, 20.0) * edge * 2.0;
    col = mix(col, cc, cl * 0.92);
  }
  // below the horizon (only visible past the far edge of the ocean)
  col = mix(col, uSkyHorizon * 0.9, smoothstep(0.0, -0.05, e));
  col += disc * uSunColor * 22.0 * smoothstep(0.99962, 0.99982, sd) * (1.0 - 0.8 * cl);
  return col;
}
`;

// Small travelling chop shared by the ocean vertex shader and the CPU (so the
// board and its wake ride the same bumps). p.x already includes the flow offset.
export const CHOP_GLSL = /* glsl */ `
float chop(vec3 p, float t) {
  return 0.07 * sin(dot(p.xz, vec2(0.55, 0.835)) * 0.95 + t * 1.6)
       + 0.05 * sin(dot(p.xz, vec2(-0.62, 0.785)) * 1.45 + p.y * 0.4 + t * 2.05)
       + 0.03 * sin(dot(p.xz, vec2(0.96, -0.28)) * 2.2 + p.y * 0.6 + t * 2.7);
}
`;
