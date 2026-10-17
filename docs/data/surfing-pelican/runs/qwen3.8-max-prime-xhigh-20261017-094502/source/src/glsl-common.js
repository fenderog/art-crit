/** GLSL helpers shared by the ocean and sky shaders. */
export const GLSL_SKY_COMMON = /* glsl */ `
float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
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
  float s = 0.0, a = 0.55;
  for (int i = 0; i < 4; i++) {
    s += a * vnoise(p);
    p = p * 2.07 + vec2(11.3, 7.7);
    a *= 0.5;
  }
  return s;
}
vec3 skyRadiance(vec3 dir, vec3 sunDir, vec3 zenith, vec3 horizon, vec3 sunColor, vec3 seaRefl) {
  vec3 d = normalize(dir);
  float y = d.y;
  // below the horizon a reflected ray sees more sea, not bright sky
  vec3 c = y >= 0.0
    ? mix(horizon, zenith, pow(y, 0.5))
    : mix(seaRefl, horizon, smoothstep(-0.09, 0.0, y));
  float sd = max(dot(d, sunDir), 0.0);
  c += sunColor * pow(sd, 260.0) * 6.0;
  c += sunColor * pow(sd, 14.0) * 0.30;
  return c;
}
`;
