import * as THREE from "three";

// Vertical sine waves. The same numbers drive the CPU sampler (board, spray,
// wake) and the vertex shader. Wave 0 is the swell the pelican rides.
export const WAVES = [
  { amp: 1.62, len: 18, dirX: 0, dirZ: 1, speed: 0.8 },
  { amp: 0.14, len: 9, dirX: 0.86, dirZ: 0.51, speed: 1.25 },
  { amp: 0.08, len: 5.2, dirX: -0.35, dirZ: 0.94, speed: 1.7 },
  { amp: 0.045, len: 2.8, dirX: 0.62, dirZ: -0.78, speed: 2.2 },
  { amp: 0.025, len: 1.6, dirX: -0.22, dirZ: 0.98, speed: 2.8 },
];

const TAU = Math.PI * 2;

for (const w of WAVES) {
  const len = Math.hypot(w.dirX, w.dirZ) || 1;
  w.dirX /= len;
  w.dirZ /= len;
  w.k = TAU / w.len;
}

// Ride just ahead of the crest, on the face that slopes down toward +z.
const FACE = Math.PI / 2 + 0.55;
const SURF_SPEED = 5.7;
const CARVE_PERIOD = 7.6;
const STEP = 1 / 60;
const BANK_GAIN = 1.85;
const BANK_BIAS = 0.1;

const UP = new THREE.Vector3(0, 1, 0);

export function sampleWater(x, z, t) {
  let h = 0;
  let dhdx = 0;
  let dhdz = 0;
  let crest = 0;
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    const phase = w.k * (w.dirX * x + w.dirZ * z) - w.speed * t;
    const s = Math.sin(phase);
    const c = Math.cos(phase);
    h += w.amp * s;
    const deriv = w.amp * w.k * c;
    dhdx += deriv * w.dirX;
    dhdz += deriv * w.dirZ;
    if (i === 0) crest = s * 0.5 + 0.5;
  }
  const normal = new THREE.Vector3(-dhdx, 1, -dhdz).normalize();
  return { h, normal, slope: Math.hypot(dhdx, dhdz), crest };
}

// Fractional phase of each wave at a world xz. The shader adds the small
// local offset from this point so sine() never sees a huge float.
export function writePhases(x, z, t, out) {
  for (let i = 0; i < WAVES.length; i++) {
    const w = WAVES[i];
    const p = w.k * (w.dirX * x + w.dirZ * z) - w.speed * t;
    out[i] = p - Math.floor(p / TAU) * TAU;
  }
  return out;
}

function pathPoint(t) {
  const w = WAVES[0];
  const phi = (t / CARVE_PERIOD) * TAU;
  const s = Math.sin(phi - 0.45);
  // Smooth bias down the face: the drop is longer than the climb to the lip.
  const zOff = 1.22 * s + 0.62 * s * s;
  const x = SURF_SPEED * t + 0.95 * Math.sin(phi * 0.5);
  const z = (FACE + w.speed * t) / w.k + zOff;
  return { x, z };
}

function flatForward(t) {
  const a = pathPoint(t);
  const b = pathPoint(t + STEP);
  return new THREE.Vector3(b.x - a.x, 0, b.z - a.z).normalize();
}

export function poseAt(t) {
  const a = pathPoint(t);
  const b = pathPoint(t + STEP);
  const surfA = sampleWater(a.x, a.z, t);
  const surfB = sampleWater(b.x, b.z, t + STEP);

  const vel = new THREE.Vector3(b.x - a.x, surfB.h - surfA.h, b.z - a.z);
  const speed = vel.length() / STEP;
  // Forward lies in the tangent plane so the nose follows the face.
  vel.addScaledVector(surfA.normal, -vel.dot(surfA.normal));
  const forward = vel.normalize();

  const f0 = flatForward(t);
  const f1 = flatForward(t + 0.08);
  // crossY > 0 is a left turn. Facing -z, left is -x: f0=(0,0,-1), f1=(-s,0,-c)
  // => f0.z*f1.x - f0.x*f1.z = (-1)*(-s) = s > 0.
  const crossY = f0.z * f1.x - f0.x * f1.z;
  const yawRate = crossY / 0.08;
  const bank = THREE.MathUtils.clamp(yawRate * BANK_GAIN + BANK_BIAS, -0.55, 0.7);

  // right = forward × up. Check: forward (0,0,-1), up (0,1,0) => right (1,0,0).
  const right = new THREE.Vector3().crossVectors(forward, surfA.normal);
  if (right.lengthSq() < 1e-8) right.crossVectors(forward, UP);
  right.normalize();

  // Positive bank leans left: the mast tilts toward -right (the low wing).
  const up = surfA.normal
    .clone()
    .multiplyScalar(Math.cos(bank))
    .addScaledVector(right, -Math.sin(bank))
    .normalize();

  // Object -Z is forward. Columns are right-handed: X × Y = Z.
  // zAxis = -forward, xAxis = up × zAxis, yAxis rebuilt so the frame stays orthonormal.
  const zAxis = forward.clone().negate();
  const xAxis = new THREE.Vector3().crossVectors(up, zAxis).normalize();
  const yAxis = new THREE.Vector3().crossVectors(zAxis, xAxis).normalize();

  const basis = new THREE.Matrix4().makeBasis(xAxis, yAxis, zAxis);
  const quaternion = new THREE.Quaternion().setFromRotationMatrix(basis);
  const position = new THREE.Vector3(a.x, surfA.h, a.z);

  return {
    position,
    quaternion,
    forward,
    up: yAxis,
    right: xAxis,
    normal: surfA.normal,
    bank,
    speed,
    slope: surfA.slope,
    crest: surfA.crest,
  };
}
