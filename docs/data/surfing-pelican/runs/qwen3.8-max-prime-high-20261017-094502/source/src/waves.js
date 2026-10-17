/**
 * Shared swell field.
 *
 * One definition of the sea, used in three places so that everything agrees:
 *   1. the ocean surface shader   (GLSL, from `wavesGLSL()`)
 *   2. the foam-trail shader      (same GLSL chunk)
 *   3. the JS sampler `sampleSea`  (drives the board + pelican rig, the camera
 *                                   bob and the spray spawn points)
 *
 * Waves are Gerstner: each entry is a direction, a steepness, a wavelength and
 * a phase speed. `height()` / `sampleSea()` return the displaced surface.
 */

export const WAVES = [
  // dirX, dirY          steepness  wavelength  speed
  { dir: [0.98, 0.20], steepness: 0.235, wavelength: 46.0, speed: 6.4 },
  { dir: [0.86, -0.50], steepness: 0.165, wavelength: 27.0, speed: 5.1 },
  { dir: [1.00, 0.12], steepness: 0.125, wavelength: 15.0, speed: 4.0 },
  { dir: [-0.35, 0.94], steepness: 0.070, wavelength: 8.5, speed: 2.9 },
  { dir: [0.55, 0.84], steepness: 0.045, wavelength: 4.6, speed: 2.1 },
  { dir: [0.20, -1.00], steepness: 0.028, wavelength: 2.3, speed: 1.5 },
];

export const WAVE_COUNT = WAVES.length;

/** Highest point a crest can reach — handy for framing and for foam thresholds. */
export const SEA_MAX_HEIGHT = WAVES.reduce(
  (acc, w) => acc + (w.steepness * w.wavelength) / (2 * Math.PI),
  0
);

export function wavesUniforms() {
  const dirs = new Float32Array(WAVE_COUNT * 4); // dirX, dirY, steepness, wavelength
  const speeds = new Float32Array(WAVE_COUNT);
  WAVES.forEach((w, i) => {
    const len = Math.hypot(w.dir[0], w.dir[1]) || 1;
    dirs[i * 4 + 0] = w.dir[0] / len;
    dirs[i * 4 + 1] = w.dir[1] / len;
    dirs[i * 4 + 2] = w.steepness;
    dirs[i * 4 + 3] = w.wavelength;
    speeds[i] = w.speed;
  });
  return {
    uWaves: { value: Array.from({ length: WAVE_COUNT }, (_, i) => [
      dirs[i * 4 + 0], dirs[i * 4 + 1], dirs[i * 4 + 2], dirs[i * 4 + 3],
    ]) },
    uSpeeds: { value: Array.from(speeds) },
    uWaveCount: { value: WAVE_COUNT },
  };
}

/** GLSL fragment (pars) shared by every surface that must ride the swell. */
export function wavesGLSL() {
  return /* glsl */ `
  uniform vec4 uWaves[${WAVE_COUNT}];   // dirX, dirY, steepness, wavelength
  uniform float uSpeeds[${WAVE_COUNT}];
  uniform float uTime;
  uniform float uWaveAmp;

  #define PI 3.141592653589793

  // Displace flat point p (x, z) and build the analytic normal.
  // `crest` accumulates a cheap whitecap proxy (steep, high places).
  vec3 gerstnerSea(vec2 p, float t, out vec3 nrm, out float crest) {
    vec3 pos = vec3(p.x, 0.0, p.y);
    vec3 tangent  = vec3(1.0, 0.0, 0.0);
    vec3 binormal = vec3(0.0, 0.0, 1.0);
    crest = 0.0;

    for (int i = 0; i < ${WAVE_COUNT}; i++) {
      vec2  dir = normalize(uWaves[i].xy);
      float stp = uWaves[i].z * uWaveAmp;
      float wl  = uWaves[i].w;
      float k   = 2.0 * PI / wl;
      float a   = stp / k;
      float f   = k * (dot(dir, p) - uSpeeds[i] * t);
      float c   = cos(f);
      float s   = sin(f);

      pos.x += dir.x * a * c;
      pos.z += dir.y * a * c;
      pos.y += a * s;

      tangent  += vec3(-dir.x * dir.x * stp * s,  dir.x * stp * c, -dir.x * dir.y * stp * s);
      binormal += vec3(-dir.x * dir.y * stp * s,  dir.y * stp * c, -dir.y * dir.y * stp * s);

      crest += stp * s;   // near-crest energy, weighted by steepness
    }

    nrm = normalize(cross(binormal, tangent));
    return pos;
  }

  vec3 gerstnerSea(vec2 p, float t, out vec3 nrm) {
    float c;
    return gerstnerSea(p, t, nrm, c);
  }
`;
}

/* ------------------------------------------------------------------ *
 * JS mirror of the GLSL above.
 * ------------------------------------------------------------------ */

const _norm = WAVES.map((w) => {
  const len = Math.hypot(w.dir[0], w.dir[1]) || 1;
  return { dx: w.dir[0] / len, dy: w.dir[1] / len, ...w };
});

/**
 * Sample the sea at flat coordinates (x, z).
 * Writes into `out` = { x, y, z, nx, ny, nz } and returns it.
 */
export function sampleSea(x, z, t, amp, out) {
  let px = x;
  let py = 0;
  let pz = z;
  let tx = 1, ty = 0, tz = 0;
  let bx = 0, by = 0, bz = 1;

  for (let i = 0; i < _norm.length; i++) {
    const w = _norm[i];
    const stp = w.steepness * amp;
    const k = (2 * Math.PI) / w.wavelength;
    const a = stp / k;
    const f = k * (w.dx * x + w.dy * z - w.speed * t);
    const c = Math.cos(f);
    const s = Math.sin(f);

    px += w.dx * a * c;
    pz += w.dy * a * c;
    py += a * s;

    tx += -w.dx * w.dx * stp * s;
    ty += w.dx * stp * c;
    tz += -w.dx * w.dy * stp * s;

    bx += -w.dx * w.dy * stp * s;
    by += w.dy * stp * c;
    bz += -w.dy * w.dy * stp * s;
  }

  // normal = binormal x tangent
  const nx = by * tz - bz * ty;
  const ny = bz * tx - bx * tz;
  const nz = bx * ty - by * tx;
  const l = Math.hypot(nx, ny, nz) || 1;

  out.x = px;
  out.y = py;
  out.z = pz;
  out.nx = nx / l;
  out.ny = ny / l;
  out.nz = nz / l;
  return out;
}

/** Just the surface height at (x, z) — used for camera bob / spray seeding. */
export function seaHeight(x, z, t, amp) {
  let py = 0;
  for (let i = 0; i < _norm.length; i++) {
    const w = _norm[i];
    const stp = w.steepness * amp;
    const k = (2 * Math.PI) / w.wavelength;
    py += (stp / k) * Math.sin(k * (w.dx * x + w.dy * z - w.speed * t));
  }
  return py;
}
