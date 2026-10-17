import * as THREE from "three";

const _f = new THREE.Vector3();
const _u = new THREE.Vector3();
const _r = new THREE.Vector3();
const _f2 = new THREE.Vector3();
const _u2 = new THREE.Vector3();
const _m = new THREE.Matrix4();
const _fallback = new THREE.Vector3();

// Local -z becomes `forward`, local +y becomes `up`.
// Canonical: forward (0,0,-1), up (0,1,0) → right (1,0,0), because forward × up = right.
export function quaternionFacing(forward, up, target) {
  _f.copy(forward).normalize();
  _u.copy(up).normalize();
  _r.crossVectors(_f, _u);
  if (_r.lengthSq() < 1e-8) {
    _fallback.set(1, 0, 0);
    _r.crossVectors(_f, _fallback);
    if (_r.lengthSq() < 1e-8) {
      _fallback.set(0, 0, 1);
      _r.crossVectors(_f, _fallback);
    }
  }
  _r.normalize();
  // up × right = forward, rebuilt so the axes stay orthonormal.
  _f2.crossVectors(_u, _r).normalize();
  _u2.crossVectors(_r, _f2).normalize();
  // Object3D local forward is -z, so the matrix z column is -forward.
  _m.makeBasis(_r, _u2, _f2.clone().negate());
  target.setFromRotationMatrix(_m);
  return target;
}
