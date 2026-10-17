// A non-interactive, self-editing camera: a handful of long-lens style shots
// cut together with a short dip to black.

import * as THREE from 'three';
import { waveHeight } from './waves.js';

const SHOTS = [
  {
    name: 'chase',
    dur: 11,
    smooth: 3.0,
    fov: 50,
    fn(rider, out) {
      const s = rider.state;
      out.pos
        .copy(s.position)
        .addScaledVector(s.forward, -8.4)
        .addScaledVector(s.up, 3.2)
        .addScaledVector(s.right, 1.5);
      // aim a little behind the rider so it sits just above the centre
      out.target.copy(s.position).addScaledVector(s.up, 1.0).addScaledVector(s.forward, -1.5);
    },
  },
  {
    name: 'side',
    dur: 9,
    smooth: 2.6,
    fov: 46,
    fn(rider, out) {
      const s = rider.state;
      out.pos
        .copy(s.position)
        .addScaledVector(s.right, 10.5)
        .addScaledVector(s.up, 2.6)
        .addScaledVector(s.forward, -2.0);
      out.target.copy(s.position).addScaledVector(s.up, 1.2).addScaledVector(s.right, 1.0);
    },
  },
  {
    name: 'water',
    dur: 7,
    smooth: 3.6,
    fov: 62,
    fn(rider, out) {
      const s = rider.state;
      // skimming the surface, looking back up at the rider
      out.pos
        .copy(s.position)
        .addScaledVector(s.forward, -6.2)
        .addScaledVector(s.up, 0.75)
        .addScaledVector(s.right, 2.4);
      out.target.copy(s.position).addScaledVector(s.up, 1.5).addScaledVector(s.forward, -0.5);
    },
  },
  {
    name: 'top',
    dur: 8,
    smooth: 2.2,
    fov: 52,
    fn(rider, out) {
      const s = rider.state;
      out.pos
        .copy(s.position)
        .addScaledVector(s.forward, -2.0)
        .addScaledVector(s.up, 13.0)
        .addScaledVector(s.right, 4.0);
      out.target.copy(s.position).addScaledVector(s.up, 0.9).addScaledVector(s.forward, 0.5);
    },
  },
  {
    name: 'face',
    dur: 7,
    smooth: 3.2,
    fov: 44,
    fn(rider, out) {
      const s = rider.state;
      out.pos
        .copy(s.position)
        .addScaledVector(s.forward, 4.6)
        .addScaledVector(s.up, 1.45)
        .addScaledVector(s.right, 1.2);
      out.target.copy(s.position).addScaledVector(s.up, 1.45).addScaledVector(s.forward, 0.2);
    },
  },
  {
    name: 'wide',
    dur: 10,
    smooth: 2.4,
    fov: 54,
    fn(rider, out) {
      const s = rider.state;
      out.pos
        .copy(s.position)
        .addScaledVector(s.right, 14.0)
        .addScaledVector(s.up, 7.5)
        .addScaledVector(s.forward, -7.0);
      out.target.copy(s.position).addScaledVector(s.up, 1.2).addScaledVector(s.forward, -1.0);
    },
  },
];

export function createCameraRig(camera) {
  const pos = new THREE.Vector3();
  const target = new THREE.Vector3();
  const dPos = new THREE.Vector3();
  const dTarget = new THREE.Vector3();
  const up = new THREE.Vector3(0, 1, 0);
  const blended = new THREE.Vector3();
  const hold = { pos: new THREE.Vector3(), target: new THREE.Vector3() };

  let index = 0;
  let shotTime = 0;
  let changed = false;
  let started = false;

  function current() {
    return SHOTS[index];
  }

  return {
    get shot() {
      return current().name;
    },
    get changed() {
      const c = changed;
      changed = false;
      return c;
    },
    get shotTime() {
      return shotTime;
    },
    get shotDuration() {
      return current().dur;
    },
    /** jump straight to a point on the shot timeline (dev tool) */
    seek(time) {
      let acc = 0;
      for (let i = 0; i < SHOTS.length; i++) {
        if (time < acc + SHOTS[i].dur) {
          index = i;
          shotTime = time - acc;
          started = false; // let the next update snap the lens
          return;
        }
        acc += SHOTS[i].dur;
      }
      index = 0;
      shotTime = 0;
      started = false;
    },
    update(dt, rider) {
      const shot = current();
      shotTime += dt;
      if (shotTime > shot.dur) {
        shotTime = 0;
        index = (index + 1) % SHOTS.length;
        changed = true;
        started = true;
      }

      const s = rider.state;
      current().fn(rider, hold);

      // a gentle hand-held wobble so the frame never feels locked off
      const t = shotTime + index * 13.7;
      const w = 0.07;
      dPos.copy(hold.pos);
      dPos.x += Math.sin(t * 2.1) * w + Math.sin(t * 5.3) * w * 0.35;
      dPos.y += Math.sin(t * 1.7 + 1.0) * w * 0.7;
      dPos.z += Math.cos(t * 1.9) * w * 0.6;
      dTarget.copy(hold.target);

      if (!started) {
        pos.copy(dPos);
        target.copy(dTarget);
      } else {
        const k = 1 - Math.exp(-shot.smooth * dt);
        pos.lerp(dPos, k);
        target.lerp(dTarget, k);
      }

      // never let the lens dip below the surface
      const floor = waveHeight(pos.x, pos.z, s.time) + 0.55;
      if (pos.y < floor) pos.y = floor;

      camera.position.copy(pos);
      blended.copy(up).lerp(s.up, 0.1).normalize();
      camera.up.copy(blended);
      camera.lookAt(target);

      if (!started || camera.fov === 0) camera.fov = shot.fov;
      else camera.fov += (shot.fov - camera.fov) * (1 - Math.exp(-2.0 * dt));
      camera.updateProjectionMatrix();
    },
  };
}
