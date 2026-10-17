import * as THREE from "three";
import { rideState } from "./wave.js";
import { quaternionFacing } from "./frame.js";

const _normal = new THREE.Vector3();
const _fwd = new THREE.Vector3();
const _up = new THREE.Vector3();
const _worldUp = new THREE.Vector3(0, 1, 0);

// Keeps the rider near the origin. `originX` is the world scroll passed to the ocean.
export function placeRider(object, t) {
  const state = rideState(t, _normal);
  const speed = Math.hypot(state.vx, state.vz);
  const turn = state.vz / speed;

  _fwd.set(state.vx, 0, state.vz).normalize();
  // Soften the surface normal so the bird stays readable on the steep face.
  _up.copy(_normal).lerp(_worldUp, 0.34).normalize();
  _fwd.addScaledVector(_up, -_fwd.dot(_up));
  if (_fwd.lengthSq() < 1e-8) _fwd.set(1, 0, 0);
  _fwd.normalize();

  // Positive turn (velocity toward the bird's right, +z) rolls the right wing down.
  // Checked by sampling local +x after the quaternion: this sign lowers that side.
  _up.applyAxisAngle(_fwd, turn * 1.15);

  quaternionFacing(_fwd, _up, object.quaternion);
  object.position.set(0, state.y, state.z);
  object.position.addScaledVector(_normal, 0.2);

  return {
    originX: state.x,
    y: state.y,
    z: state.z,
    vx: state.vx,
    vz: state.vz,
    speed,
    turn,
  };
}
