// Non-interactive cinematography: a loop of shots around the surfer with slow
// glides between them.

import * as THREE from 'three';
import { clamp } from './geom.js';

const V3 = THREE.Vector3;

const SHOTS = [
  // front three-quarter, sunset over the lip
  { off: new V3(3.8, 0.8, 6.0), look: new V3(-1.1, 0.55, -0.7), fov: 40 },
  // down the line from the shoulder, looking into the tube
  { off: new V3(7.2, 1.1, 3.8), look: new V3(-2.8, 0.45, -0.6), fov: 36 },
  // low and close, almost at water level
  { off: new V3(2.1, 0.0, 3.5), look: new V3(-0.5, 0.65, -0.3), fov: 44 },
  // wide establishing shot
  { off: new V3(1.0, 3.4, 12.5), look: new V3(-3.5, 0.9, -2.0), fov: 42 },
];
const HOLD = 13;
const GLIDE = 5;

const smoother = (x) => x * x * x * (x * (x * 6 - 15) + 10);

export class CameraRig {
  constructor(camera) {
    this.camera = camera;
    this.follow = new V3(1, 1, 2);
    this.lookAt = new V3();
    this.off = new V3();
    this.lk = new V3();
    this.anchor = new V3(0.8, 1.0, 1.6);
    this.first = true;
  }

  update(t, dt, target) {
    const n = SHOTS.length;
    const tt = t % (n * HOLD);
    const i = Math.floor(tt / HOLD);
    const local = tt - i * HOLD;
    const f = smoother(clamp((local - (HOLD - GLIDE)) / GLIDE, 0, 1));
    const a = SHOTS[i];
    const b = SHOTS[(i + 1) % n];
    this.off.lerpVectors(a.off, b.off, f);
    this.lk.lerpVectors(a.look, b.look, f);
    const fov = a.fov + (b.fov - a.fov) * f;

    // slow drift so a held shot never feels frozen
    this.off.x += Math.sin(t * 0.21) * 0.7;
    this.off.y += Math.sin(t * 0.17 + 1) * 0.25;
    this.off.z += Math.cos(t * 0.13) * 0.7;

    const k = this.first ? 1 : 1 - Math.exp(-dt * 1.4);
    this.first = false;
    this.follow.lerp(target, k);
    const base = new V3().lerpVectors(this.follow, this.anchor, 0.35);

    const cam = this.camera;
    cam.position.copy(base).add(this.off);
    // handheld-ish float
    cam.position.x += Math.sin(t * 1.3) * 0.03 + Math.sin(t * 2.9) * 0.012;
    cam.position.y += Math.sin(t * 1.1 + 0.5) * 0.04 + Math.sin(t * 3.1) * 0.01;
    cam.position.y = Math.max(cam.position.y, 0.55);
    this.lookAt.copy(this.follow).add(this.lk);
    cam.lookAt(this.lookAt);
    if (Math.abs(cam.fov - fov) > 1e-3) {
      cam.fov = fov;
      cam.updateProjectionMatrix();
    }
  }
}
