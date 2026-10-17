// Moves the board over the wave face (in the wave's frame) and poses the pelican.

import * as THREE from 'three';
import { surfaceSample, makeSample, chopAt } from './wave.js';
import { createSurfboard } from './surfboard.js';
import { Pelican } from './pelican.js';
import { clamp } from './geom.js';

const V3 = THREE.Vector3;
const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _v = new V3();

export class Surfer {
  constructor() {
    this.group = new THREE.Group();
    this.board = createSurfboard();
    this.group.add(this.board);
    this.pelican = new Pelican();
    this.board.add(this.pelican.body);
    this.board.add(this.pelican.legs);

    this.s = makeSample();
    this.x = 0;
    this.u = 12;
    this.pos = new V3();
    this.normal = new V3(0, 1, 0);
    this.fwd = new V3(1, 0, 0);
    this.up = new V3(0, 1, 0);
    this.along = new V3(1, 0, 0);
    this.upFace = new V3(0, 1, 0);
    this.psi = 0;
    this.psiRate = 0;
    this.bank = 0;
    this.carve = 0;
    this.lookBack = 0;
    this.tail = new V3();
    this.blend = 0.8;
    this.s2 = makeSample();
  }

  // distance (along z) between the wave wall and the pelican's head / bill tip
  headClearance(worldUpLocal, blend) {
    const up = new V3(0, 1, 0).lerp(worldUpLocal, blend).normalize();
    const head = new V3(0, 0.08, 0.3).addScaledVector(up, 1.05).applyQuaternion(this.board.quaternion).add(this.board.position);
    const tip = new V3(this.fwd.x, 0, this.fwd.z).normalize().multiplyScalar(0.62).add(head);
    return Math.min(this.wallGap(head), this.wallGap(tip));
  }

  wallGap(P) {
    for (let u = 12.6; u > 8.5; u -= 0.05) {
      surfaceSample(P.x, u, this.s2);
      if (this.s2.pos.y >= P.y) return P.z - this.s2.pos.z;
    }
    return 9;
  }

  path(t) {
    // slow drift along the line (in and out of the tube) and carves up/down the face
    const w1 = 0.23, w2 = 0.61, w3 = 1.05, w4 = 2.2;
    const x = 0.6 + 2.0 * Math.sin(t * w1) + 0.6 * Math.sin(t * w2 + 1.3);
    const u = 12.0 + 0.38 * Math.sin(t * w3) + 0.08 * Math.sin(t * w4 + 0.7);
    const du = 0.38 * w3 * Math.cos(t * w3) + 0.08 * w4 * Math.cos(t * w4 + 0.7);
    return { x, u, du };
  }

  update(t, dt) {
    const s = this.s;
    const { x, du } = this.path(t);
    let { u } = this.path(t);
    surfaceSample(x, u, s);
    // stay off the overhanging part of the face
    for (let k = 0; k < 30 && s.normal.y < 0.22; k++) {
      u += 0.04;
      surfaceSample(x, u, s);
    }
    this.x = x;
    this.u = u;
    this.normal.copy(s.normal);
    this.along.copy(s.tx).normalize();
    // direction up the face, perpendicular to the line
    this.upFace.crossVectors(s.normal, this.along).normalize();
    if (this.upFace.y < 0) this.upFace.negate();

    // heading: mostly down the line, pitched up/down the face as it carves
    const psi = clamp(-du * 1.1, -0.7, 0.7);
    const rate = dt > 0 ? (psi - this.psi) / dt : 0;
    this.psi = psi;
    this.psiRate += (rate - this.psiRate) * (1 - Math.exp(-dt * 6));
    this.carve = this.psiRate;

    const fwd = _v.copy(this.along).multiplyScalar(Math.cos(psi)).addScaledVector(this.upFace, Math.sin(psi)).normalize();
    // bank: lean into the turn, rail digs in
    const bankTarget = clamp(this.psiRate * 0.35, -0.35, 0.35);
    this.bank += (bankTarget - this.bank) * (1 - Math.exp(-dt * 5));
    const up = this.up.copy(s.normal).multiplyScalar(Math.cos(this.bank)).addScaledVector(this.upFace, Math.sin(this.bank)).normalize();
    fwd.addScaledVector(up, -fwd.dot(up)).normalize();
    this.fwd.copy(fwd);

    const h = chopAt(s.pos.x, s.pos.y, s.pos.z, t);
    this.pos.copy(s.pos).addScaledVector(s.normal, h - 0.012);
    const right = new V3().crossVectors(up, fwd);
    _m.makeBasis(right, up, fwd);
    this.board.quaternion.setFromRotationMatrix(_m);
    this.board.position.copy(this.pos);
    this.board.updateMatrixWorld(true);
    this.tail.copy(this.pos).addScaledVector(fwd, -0.8);

    // pelican: body stays closer to world-up than the board does, but leans
    // out with the board when the tube wall gets close to its head
    _q.copy(this.board.quaternion).invert();
    const worldUpLocal = new V3(0, 1, 0).applyQuaternion(_q);
    let blend = 0.8;
    while (blend > 0 && this.headClearance(worldUpLocal, blend) < 0.5) blend -= 0.1;
    this.blend += (blend - this.blend) * (1 - Math.exp(-dt * (blend < this.blend ? 14 : 3)));
    const bodyUp = new V3(0, 1, 0).lerp(worldUpLocal, this.blend);
    const lean = clamp(-this.psiRate * 0.25 + 0.12 * Math.sin(t * 0.8), -0.6, 0.6);
    bodyUp.x += lean * 0.25;
    const crouch = clamp(0.45 + this.psiRate * 0.6 + 0.15 * Math.sin(t * 2.3), 0, 1);

    // occasional balance flap
    const fp = (t + 2.0) % 9.0;
    const flap = fp < 1.0 ? Math.sin(fp * Math.PI * 2) * Math.sin(fp * Math.PI) : 0;

    // glance back at the tube now and then
    const lb = (t % 11.0) > 7.5 && (t % 11.0) < 9.6 ? 1 : 0;
    this.lookBack += (lb - this.lookBack) * (1 - Math.exp(-dt * 3));
    const lookDir = new V3(fwd.x, 0, fwd.z).normalize();
    const back = new V3(-0.55, 0.05, 0.75).normalize();
    lookDir.lerp(back, this.lookBack * 0.85).normalize();

    this.pelican.update(t, dt, { bodyUp, lean, crouch, flap, lookDir });
  }
}

