import * as THREE from 'three';

// Shared wave definition. These parameters are used both by the GPU
// (vertex displacement of the ocean) and by the CPU (buoyancy of the surfer),
// so the pelican always sits exactly on the visible surface.

export const WAVES = [
  { dir: new THREE.Vector2(1.0, 0.25).normalize(), amplitude: 0.55, wavelength: 26.0, speed: 0.95 },
  { dir: new THREE.Vector2(1.0, 0.60).normalize(), amplitude: 0.30, wavelength: 14.0, speed: 1.25 },
  { dir: new THREE.Vector2(1.0, -0.40).normalize(), amplitude: 0.16, wavelength: 8.0, speed: 1.70 },
  { dir: new THREE.Vector2(0.5, 1.00).normalize(), amplitude: 0.09, wavelength: 5.2, speed: 2.10 },
];

export function waveHeight(x, z, t) {
  let h = 0;
  for (const w of WAVES) {
    const k = (2 * Math.PI) / w.wavelength;
    const omega = k * w.speed;
    const phase = k * (w.dir.x * x + w.dir.y * z) - omega * t;
    h += w.amplitude * Math.sin(phase);
  }
  return h;
}

export function waveNormal(target, x, z, t) {
  let nx = 0;
  let nz = 0;
  for (const w of WAVES) {
    const k = (2 * Math.PI) / w.wavelength;
    const omega = k * w.speed;
    const phase = k * (w.dir.x * x + w.dir.y * z) - omega * t;
    const c = Math.cos(phase);
    nx += -w.dir.x * k * w.amplitude * c;
    nz += -w.dir.y * k * w.amplitude * c;
  }
  return target.set(nx, 1, nz).normalize();
}

// Generates GLSL with the same waves baked in as constants.
export function waveGLSL() {
  let height = 'float waveHeight(vec2 p, float t) {\n  float h = 0.0;\n';
  let normal = 'vec3 waveNormal(vec2 p, float t) {\n  vec3 n = vec3(0.0, 1.0, 0.0);\n';

  for (const w of WAVES) {
    const k = (2 * Math.PI) / w.wavelength;
    const omega = k * w.speed;
    const dx = w.dir.x;
    const dz = w.dir.y;
    const a = w.amplitude;
    const nx = -dx * k * a;
    const nz = -dz * k * a;

    height += `  { float ph = ${k} * (${dx} * p.x + ${dz} * p.y) - ${omega} * t;\n`;
    height += `    h += ${a} * sin(ph); }\n`;

    normal += `  { float ph = ${k} * (${dx} * p.x + ${dz} * p.y) - ${omega} * t;\n`;
    normal += `    float c = cos(ph);\n`;
    normal += `    n.x += ${nx} * c;\n`;
    normal += `    n.z += ${nz} * c; }\n`;
  }

  height += '  return h;\n}\n';
  normal += '  return normalize(n);\n}\n';
  return height + normal;
}
