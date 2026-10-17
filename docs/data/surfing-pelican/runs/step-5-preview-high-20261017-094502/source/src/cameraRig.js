// cameraRig.js — a tiny virtual camera operator. The page is non-interactive,
// so the shot plans itself: a sequence of set-ups that dissolve into each other,
// each with its own slow drift, plus a touch of handheld noise.

import * as THREE from 'three';

const smoothstep = (a, b, x) => {
  const k = THREE.MathUtils.clamp((x - a) / (b - a), 0, 1);
  return k * k * (3 - 2 * k);
};

const SHOTS = [
  { name: 'establishing', dur: 21, pos: [-25, 8.5, -29], look: [-0.8, 2.2, 3.4], fov: 41 },
  { name: 'alongside', dur: 17, pos: [-8.5, 2.5, -9.5], look: [0.5, 1.9, 0.6], fov: 48 },
  { name: 'sunlit', dur: 16, pos: [-13.5, 3.6, -13.5], look: [0.3, 2.1, 3.6], fov: 52 },
  { name: 'overhead', dur: 19, pos: [9, 17, -15], look: [-0.4, 1.3, 3.2], fov: 37 },
];

const TOTAL = SHOTS.reduce((s, x) => s + x.dur, 0);
const BLEND = 3.2;

export function createCameraRig(camera) {
  const posA = new THREE.Vector3();
  const posB = new THREE.Vector3();
  const lookA = new THREE.Vector3();
  const lookB = new THREE.Vector3();
  const target = new THREE.Vector3();
  const desired = new THREE.Vector3();
  const riderPos = new THREE.Vector3();
  let fovCurrent = SHOTS[0].fov;
  let initialised = false;

  const shotAt = (time) => {
    let phase = time % TOTAL;
    if (phase < 0) phase += TOTAL;
    for (let i = 0; i < SHOTS.length; i++) {
      if (phase < SHOTS[i].dur) return { i, local: phase };
      phase -= SHOTS[i].dur;
    }
    return { i: 0, local: 0 };
  };

  return {
    total: TOTAL,
    shots: SHOTS,
    update(t, dt, riderState) {
      const cur = shotAt(t);
      const nxt = SHOTS[(cur.i + 1) % SHOTS.length];
      const cur$ = SHOTS[cur.i];
      const k = smoothstep(cur$.dur - BLEND, cur$.dur, cur.local);

      // each shot drifts slowly so the camera is never dead still
      const sway = (seed, amp, speed) =>
        Math.sin(t * speed + seed) * amp + Math.sin(t * speed * 2.3 + seed * 1.7) * amp * 0.35;

      posA.copy(riderState.position3).add(
        new THREE.Vector3(cur$.pos[0], cur$.pos[1], cur$.pos[2]),
      );
      posB.copy(riderState.position3).add(
        new THREE.Vector3(nxt.pos[0], nxt.pos[1], nxt.pos[2]),
      );
      lookA.copy(riderState.position3).add(
        new THREE.Vector3(cur$.look[0], cur$.look[1], cur$.look[2]),
      );
      lookB.copy(riderState.position3).add(
        new THREE.Vector3(nxt.look[0], nxt.look[1], nxt.look[2]),
      );

      const i = cur.i;
      posA.x += sway(i, 1.1, 0.19);
      posA.y += sway(i + 3, 0.5, 0.23);
      posA.z += sway(i + 7, 1.4, 0.17);

      desired.lerpVectors(posA, posB, k);
      target.lerpVectors(lookA, lookB, k);
      // the look target rides up and down with the bird
      target.y += riderState.bob * 0.5;

      // handheld noise
      const shake = 0.035;
      desired.x += Math.sin(t * 1.7 + i) * shake + Math.sin(t * 4.3) * shake * 0.4;
      desired.y += Math.sin(t * 1.3 + 2.0) * shake * 0.7 + Math.sin(t * 5.1) * shake * 0.3;
      desired.z += Math.sin(t * 1.9 + 4.0) * shake;

      camera.position.lerp(desired, initialised ? 1 - Math.pow(0.0006, dt) : 1);
      camera.lookAt(target);

      // a touch of roll: the operator leans the same way the surfer does
      camera.rotateZ(-riderState.bank * 0.35);

      const fovTarget = THREE.MathUtils.lerp(cur$.fov, nxt.fov, k);
      fovCurrent = THREE.MathUtils.lerp(fovCurrent, fovTarget, 1 - Math.pow(0.05, dt));
      if (Math.abs(camera.fov - fovCurrent) > 1e-4) {
        camera.fov = fovCurrent;
        camera.updateProjectionMatrix();
      }
      initialised = true;
      riderPos.copy(riderState.position3);
    },
  };
}
