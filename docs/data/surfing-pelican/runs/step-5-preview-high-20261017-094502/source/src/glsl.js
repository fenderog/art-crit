// glsl.js — small library of GLSL snippets shared by the sky and the ocean so
// that the horizon colours always agree (the ocean fades into exactly the same
// sky gradient that is drawn behind it).

export const SKY_UNIFORMS = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uZenithColor;
uniform vec3 uHorizonColor;
uniform vec3 uHorizonGlow;
`;

export const SKY_COLOR = /* glsl */ `
vec3 skyColor(vec3 d) {
  float y = clamp(d.y, -0.35, 1.0);
  vec3 col = mix(uHorizonColor, uZenithColor, pow(clamp(y, 0.0, 1.0), 0.62));
  float low = exp(-max(y, 0.0) * 6.5);
  col = mix(col, uHorizonGlow, low * 0.62);
  float s = clamp(dot(d, uSunDir), -1.0, 1.0);
  col += uSunColor * pow(max(s, 0.0), 520.0) * 2.2;   // disc
  col += uSunColor * pow(max(s, 0.0), 18.0) * 0.22;   // halo
  col += uSunColor * pow(max(s, 0.0), 3.0) * 0.10 * low;
  col = mix(col, uHorizonColor * 0.55, smoothstep(0.0, -0.28, y));
  return col;
}
`;

export const NOISE = /* glsl */ `
float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

float vnoise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  float a = hash21(i);
  float b = hash21(i + vec2(1.0, 0.0));
  float c = hash21(i + vec2(0.0, 1.0));
  float d = hash21(i + vec2(1.0, 1.0));
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
  float s = 0.0;
  float a = 0.5;
  for (int i = 0; i < 5; i++) {
    s += a * vnoise(p);
    p = p * 2.03 + vec2(11.3, 7.7);
    a *= 0.5;
  }
  return s;
}
`;

// High frequency ripples. Only ever added to the normal (never to the
// displacement) so they can never alias the geometry.
export const DETAIL_NORMAL = /* glsl */ `
vec3 detailNormal(vec2 p, float t) {
  vec2 g = vec2(0.0);
  vec2 d1 = vec2(0.86, 0.51);
  g += 0.013 * 9.0 * d1 * cos(9.0 * dot(d1, p) + t * 3.1);
  vec2 d2 = vec2(-0.48, 0.88);
  g += 0.0055 * 17.0 * d2 * cos(17.0 * dot(d2, p) + t * 4.3 + 1.3);
  vec2 d3 = vec2(0.31, -0.95);
  g += 0.003 * 33.0 * d3 * cos(33.0 * dot(d3, p) + t * 5.6 + 2.1);
  return vec3(-g.x, 0.0, -g.y);
}
`;

export const CLOUDS = /* glsl */ `
vec3 cloudColor(vec3 d) {
  if (d.y < 0.025) return vec3(0.0);
  vec2 uv = d.xz / max(d.y, 0.03);
  uv = uv * vec2(0.55, 0.85) + vec2(uTime * 0.004, uTime * 0.0022);
  float f = fbm(uv * 1.15 + vec2(3.1, 1.7));
  float f2 = fbm(uv * 0.62 + vec2(-1.2, 4.4));
  float dens = smoothstep(0.62, 0.94, f * 0.78 + f2 * 0.32);
  // cloud banks hug the horizon, the upper sky stays blue
  float vert = smoothstep(0.025, 0.16, d.y) * (1.0 - smoothstep(0.34, 0.88, d.y) * 0.92);
  dens *= vert * 0.95;
  if (dens < 0.002) return vec3(0.0);
  float lit = clamp((f - fbm(uv * 1.15 + vec2(3.36, 1.7))) * 7.0, -1.0, 1.0);
  float sunAmt = pow(max(dot(d, uSunDir), 0.0), 8.0);
  vec3 darkC = vec3(0.44, 0.46, 0.55);
  vec3 litC = mix(vec3(1.0, 0.94, 0.86), vec3(1.0, 0.78, 0.60), sunAmt * 0.85);
  vec3 c = mix(darkC, litC, lit * 0.5 + 0.5);
  c = mix(c, litC, 0.35);
  return c * dens;
}
`;
