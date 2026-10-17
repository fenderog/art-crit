import * as THREE from "three";
import { WAVES, heightAt, surfaceNormal } from "./ocean.js";

const UP = new THREE.Vector3(0, 1, 0);
const CARVE = 0.42;

const _fwd = new THREE.Vector3();
const _x = new THREE.Vector3();
const _y = new THREE.Vector3();
const _z = new THREE.Vector3();
const _m = new THREE.Matrix4();
const _normal = new THREE.Vector3();

/** Where the pelican sits on the primary face. carve +1 is low, -1 is the lip. */
export function ridePhase(t) {
  const u = t * CARVE;
  const carve = Math.tanh(Math.sin(u) * 1.35);
  const down = carve * 0.5 + 0.5;
  const phase = Math.PI / 2 + 0.18 + 1.02 * down;
  return { u, carve, phase, down };
}

export function rideXZ(t) {
  const { u, phase } = ridePhase(t);
  const x = 5.6 * t + 1.85 * Math.sin(u + 0.7);
  // phase = k*z - w*t  →  z = (phase + w*t) / k
  const z = (phase + WAVES.w[0] * t) / WAVES.k[0];
  return { x, z, phase };
}

export function createRideState() {
  return {
    position: new THREE.Vector3(),
    normal: new THREE.Vector3(),
    travel: new THREE.Vector3(),
    bank: 0,
    pitch: 0,
    lip: 0,
    phase: 0,
  };
}

export function sampleRide(t, out) {
  const { phase } = ridePhase(t);
  const here = rideXZ(t);
  const ahead = rideXZ(t + 0.05);
  out.travel.set(ahead.x - here.x, 0, ahead.z - here.z);
  if (out.travel.lengthSq() < 1e-8) out.travel.set(1, 0, 0);
  else out.travel.normalize();

  const y = heightAt(here.x, here.z, t);
  surfaceNormal(here.x, here.z, t, _normal);
  out.position.set(here.x, y, here.z);
  out.normal.copy(_normal);

  const prev = ridePhase(t - 0.05);
  const dPhase = phase - prev.phase;
  // dPhase > 0: sliding down the face, toward the trough.
  // Positive bank drops the crest-side rail (see alignToSurface).
  out.bank = THREE.MathUtils.clamp(-dPhase * 1.15, -0.4, 0.4);
  out.pitch = THREE.MathUtils.clamp(dPhase * 0.7 - 0.04, -0.2, 0.18);
  out.lip = THREE.MathUtils.clamp(1 - (phase - (Math.PI / 2 + 0.18)) / 1.02, 0, 1);
  out.phase = phase;
  return out;
}

/**
 * Point object's local -z along travel, local +y along the surface normal.
 * forward × up = right, so local +x is the pelican's right.
 * On the primary wave, crest is -z from the face and trough is +z;
 * with travel along +x, local +x points downhill (trough) and local -x toward the crest.
 */
export function alignToSurface(object, normal, travel) {
  _y.copy(normal).normalize();
  _fwd.copy(travel);
  _fwd.y = 0;
  if (_fwd.lengthSq() < 1e-8) _fwd.set(1, 0, 0);
  else _fwd.normalize();
  _fwd.addScaledVector(_y, -_fwd.dot(_y)).normalize();
  _x.crossVectors(_fwd, _y).normalize();
  _z.copy(_fwd).negate();
  _m.makeBasis(_x, _y, _z);
  object.quaternion.setFromRotationMatrix(_m);
}

/** Flat right vector: travel × up. For travel +x this is +z, down the face. */
export function flatRight(travel, target) {
  _fwd.copy(travel);
  _fwd.y = 0;
  if (_fwd.lengthSq() < 1e-8) _fwd.set(1, 0, 0);
  else _fwd.normalize();
  return target.crossVectors(_fwd, UP).normalize();
}
