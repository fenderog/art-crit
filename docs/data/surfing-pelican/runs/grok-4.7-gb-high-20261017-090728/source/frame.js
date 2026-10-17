import * as THREE from "three";

export const WORLD_UP = new THREE.Vector3(0, 1, 0);

const _f = new THREE.Vector3();
const _u = new THREE.Vector3();
const _r = new THREE.Vector3();
const _b = new THREE.Vector3();
const _m = new THREE.Matrix4();

// Local forward is −Z. right = forward × up, back = right × up.
// Check: forward (0,0,−1), up (0,1,0) → right (1,0,0), back (0,0,1).
export function composeRootQuaternion(forward, up, quat) {
  const u = _u.copy(up).normalize();
  const f = _f.copy(forward).projectOnPlane(u);
  if (f.lengthSq() < 1e-8) {
    f.set(0, 0, -1).projectOnPlane(u);
    if (f.lengthSq() < 1e-8) f.set(1, 0, 0);
  }
  f.normalize();
  const right = _r.crossVectors(f, u).normalize();
  const back = _b.crossVectors(right, u).normalize();
  _m.makeBasis(right, u, back);
  return quat.setFromRotationMatrix(_m);
}

export function rootBasis(quaternion, target) {
  target.right.set(1, 0, 0).applyQuaternion(quaternion);
  target.up.set(0, 1, 0).applyQuaternion(quaternion);
  target.back.set(0, 0, 1).applyQuaternion(quaternion);
  target.forward.set(0, 0, -1).applyQuaternion(quaternion);
  return target;
}

export function selfTestFrame() {
  const q = new THREE.Quaternion();
  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const up = new THREE.Vector3();
  const failures = [];
  const check = (cond, msg, extra) => {
    if (!cond) failures.push(`${msg} ${extra ? JSON.stringify(extra) : ""}`);
  };

  composeRootQuaternion(new THREE.Vector3(0, 0, -1), WORLD_UP, q);
  fwd.set(0, 0, -1).applyQuaternion(q);
  right.set(1, 0, 0).applyQuaternion(q);
  up.set(0, 1, 0).applyQuaternion(q);
  check(fwd.dot(new THREE.Vector3(0, 0, -1)) > 0.999, "identity forward", fwd.toArray());
  check(right.dot(new THREE.Vector3(1, 0, 0)) > 0.999, "identity right", right.toArray());
  check(up.dot(WORLD_UP) > 0.999, "identity up", up.toArray());

  composeRootQuaternion(new THREE.Vector3(1, 0, 0), WORLD_UP, q);
  fwd.set(0, 0, -1).applyQuaternion(q);
  right.set(1, 0, 0).applyQuaternion(q);
  check(fwd.dot(new THREE.Vector3(1, 0, 0)) > 0.999, "east forward", fwd.toArray());
  check(right.dot(new THREE.Vector3(0, 0, 1)) > 0.999, "east right", right.toArray());

  const tilted = new THREE.Vector3(-0.4, 0.8, 0.2).normalize();
  const travel = new THREE.Vector3(0.9, -0.2, 0.3);
  composeRootQuaternion(travel, tilted, q);
  fwd.set(0, 0, -1).applyQuaternion(q);
  up.set(0, 1, 0).applyQuaternion(q);
  const travelPlane = travel.clone().projectOnPlane(tilted).normalize();
  check(fwd.dot(travelPlane) > 0.999, "tilted forward", fwd.toArray());
  check(up.dot(tilted) > 0.999, "tilted up", up.toArray());
  check(Math.abs(fwd.dot(up)) < 1e-4, "ortho", fwd.dot(up));

  if (failures.length) {
    throw new Error(failures.join("\n"));
  }
  return true;
}
