// fish.js — the incident that gives the film its plot. A silver fish leaps out
// of the water in front of the board and arcs straight into the pelican's beak.

import * as THREE from 'three';
import { plate, mesh } from './geom.js';

const std = (color, roughness, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0, ...extra });

const UP = new THREE.Vector3(0, 1, 0);

function tailShape() {
  const s = new THREE.Shape();
  s.moveTo(0.0, 0.0);
  s.quadraticCurveTo(-0.10, 0.16, -0.30, 0.24);
  s.quadraticCurveTo(-0.20, 0.10, -0.22, 0.0);
  s.quadraticCurveTo(-0.20, -0.10, -0.30, -0.24);
  s.quadraticCurveTo(-0.10, -0.16, 0.0, 0.0);
  return s;
}

export function createFish(riderRoot) {
  const group = new THREE.Group();      // carries the flight heading
  group.visible = false;
  riderRoot.add(group);

  const model = new THREE.Group();      // the body points along +X
  model.rotation.y = -Math.PI / 2;      // ...so +X ends up facing along +Z
  group.add(model);

  const bodyMat = std(0x9cc4d6, 0.32, { metalness: 0.45 });
  const body = mesh(new THREE.SphereGeometry(1, 18, 14), bodyMat);
  body.scale.set(0.30, 0.125, 0.062);
  model.add(body);

  const tail = mesh(plate(tailShape(), 0.02, 12), bodyMat);
  tail.position.set(-0.26, 0, 0);
  model.add(tail);

  const fin = mesh(plate(tailShape(), 0.016, 10), bodyMat);
  fin.scale.set(0.5, 0.45, 1);
  fin.position.set(0.02, 0.10, 0);
  model.add(fin);

  const eyeMat = std(0x11161c, 0.2);
  for (const s of [1, -1]) {
    const eye = mesh(new THREE.SphereGeometry(0.022, 8, 6), eyeMat);
    eye.position.set(0.22, 0.035, 0.05 * s);
    model.add(eye);
  }

  const A = new THREE.Vector3();
  const B = new THREE.Vector3();
  const p1 = new THREE.Vector3();
  const p2 = new THREE.Vector3();
  const delta = new THREE.Vector3();
  const zero = new THREE.Vector3();
  const m = new THREE.Matrix4();

  let phase = 'idle';
  let timer = 5.5;
  let u = 0;
  let arc = 1.25;

  const jump = (u0, out) => {
    out.copy(A).lerp(B, u0);
    out.y += arc * Math.sin(Math.PI * u0);
    out.y += 0.05 * Math.sin(u0 * 9.0);
    return out;
  };

  return {
    group,
    update(dt, t, ctx) {
      timer -= dt;

      if (phase === 'idle') {
        if (timer <= 0) {
          phase = 'jump';
          u = 0;
          arc = 1.1 + Math.random() * 0.5;
          A.set(1.95 + Math.random() * 0.4, 0, -0.45 + Math.random() * 0.3);
          group.visible = true;
          ctx.onLaunch?.();
        }
        return;
      }

      if (phase === 'jump') {
        u += dt / 1.15;
        if (u >= 1) {
          phase = 'catch';
          timer = 0.22;
          group.visible = false;
          ctx.onCatch?.(ctx.mouthWorld);
          return;
        }
        jump(u, p1);
        jump(Math.min(1, u + 0.02), p2);
        group.position.copy(p1);
        delta.copy(p2).sub(p1);
        if (delta.lengthSq() > 1e-9) {
          m.lookAt(delta.normalize(), zero, UP); // +Z along the direction of travel
          group.quaternion.setFromRotationMatrix(m);
        }
        model.rotation.x = Math.sin(t * 34) * 0.12;
        model.rotation.z = Math.sin(t * 26) * 0.10;
        if (u > 0.7) ctx.setBeakOpen?.(0.55);
        return;
      }

      if (timer <= 0) {
        phase = 'idle';
        timer = 11 + Math.random() * 9;
        ctx.setBeakOpen?.(0);
      }
    },
  };
}
