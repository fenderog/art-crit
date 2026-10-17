import * as THREE from "three";
import { createBoard } from "./board.js";
import { createPelican } from "./pelican.js";
import { slicePos, wallIndexAt, sliceArc } from "./surface.js";
import { NS } from "./profile.js";
import { clamp, lerp } from "./geo.js";

const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

// Where the surfer wants to be on the wave: along the crest (x) and height up the wall (h).
export function pathAt(t) {
  return {
    x: 24 + 2.3 * Math.sin(0.31 * t) + 1.2 * Math.sin(0.77 * t + 0.8),
    h: 0.56 + 0.4 * Math.sin(0.52 * t - 0.4) + 0.14 * Math.sin(1.37 * t + 1.1),
  };
}

export function createSurfer() {
  const group = new THREE.Group();
  const board = createBoard();
  board.position.y = -0.037;
  group.add(board);
  const pelican = createPelican();
  pelican.root.position.set(-0.05, 0, 0);
  pelican.root.scale.setScalar(1.25);
  group.add(pelican.root);

  const st = {
    pos: V(),
    quat: new THREE.Quaternion(),
    init: false,
    forward: V(1, 0, 0),
    up: V(0, 1, 0),
    prevY: 0,
    vy: 0,
    acc: 0, // vertical acceleration, drives the pelican's bounce and its pouch
    yawRate: 0,
    prevHeading: 0,
    roll: 0, // tilt of the board relative to gravity
    faceSpeed: 0, // speed up/down the wall
    energy: 0, // how hard the carve is: 0 cruising .. 1 hard turn
    tailX: 0,
    tailArc: 0,
  };
  const p0 = [0, 0, 0];
  const pA = V();
  const dX = V();
  const dS = V();
  const n = V();
  const f = V();
  const r = V();
  const m4 = new THREE.Matrix4();
  const qT = new THREE.Quaternion();
  const worldUp = V(0, 1, 0);
  const tmp = V();
  const camLocal = V();

  function surf(x, h, tp, out) {
    const idx = wallIndexAt(x, h, tp);
    slicePos(x, idx, tp, p0);
    out.set(p0[0], p0[1], p0[2]);
    return idx;
  }

  function normalAt(x, idx, tp, out) {
    slicePos(x + 0.35, idx, tp, p0);
    dX.set(p0[0], p0[1], p0[2]);
    slicePos(x - 0.35, idx, tp, p0);
    dX.sub(tmp.set(p0[0], p0[1], p0[2]));
    slicePos(x, Math.min(idx + 1, NS - 1), tp, p0);
    dS.set(p0[0], p0[1], p0[2]);
    slicePos(x, Math.max(idx - 1, 0), tp, p0);
    dS.sub(tmp.set(p0[0], p0[1], p0[2]));
    out.crossVectors(dX, dS);
    if (out.lengthSq() < 1e-10) out.set(0, 1, 0);
    return out.normalize();
  }

  function update(t, dt, camera) {
    dt = Math.max(dt, 1e-4);
    const P = pathAt(t);
    const idx = surf(P.x, P.h, t, pA);
    normalAt(P.x, idx, t, n);

    // heading: direction of travel in the frame of the wave, biased forward
    const e = 0.05;
    const Pa = pathAt(t + e);
    const Pb = pathAt(t - e);
    const va = V();
    const vb = V();
    surf(Pa.x, Pa.h, t, va);
    surf(Pb.x, Pb.h, t, vb);
    const vSteady = va.sub(vb).multiplyScalar(1 / (2 * e));
    const hv = V(5.0, 0, 0).addScaledVector(vSteady, 2.2);
    f.copy(hv).addScaledVector(n, -hv.dot(n));
    if (f.lengthSq() < 1e-8) f.set(1, 0, 0);
    f.normalize();

    // board up: mostly the surface normal, eased a little toward vertical
    const up = V().copy(n).lerp(worldUp, 0.12).normalize();
    f.addScaledVector(up, -f.dot(up)).normalize();
    r.crossVectors(f, up).normalize();
    // lean into the turn
    const heading = Math.atan2(f.y, f.x);
    const yr = (heading - st.prevHeading) / dt;
    st.prevHeading = heading;
    st.yawRate = lerp(st.yawRate, clamp(yr, -3, 3), 1 - Math.exp(-dt * 4));
    const lean = clamp(st.yawRate * 0.14, -0.4, 0.4);
    up.applyAxisAngle(f, lean);
    r.crossVectors(f, up).normalize();

    m4.makeBasis(f, up, r);
    qT.setFromRotationMatrix(m4);
    if (!st.init) {
      st.quat.copy(qT);
      st.init = true;
    } else st.quat.slerp(qT, 1 - Math.exp(-dt * 14));
    group.quaternion.copy(st.quat);

    // position: sit on the water, a little sunk
    const pos = V().copy(pA).addScaledVector(n, 0.045);
    group.position.copy(pos);

    // kinematics for the pelican's secondary motion
    const vy = (pos.y - st.prevY) / dt;
    st.acc = lerp(st.acc, clamp((vy - st.vy) / dt, -40, 40), 1 - Math.exp(-dt * 8));
    st.vy = vy;
    st.prevY = pos.y;
    st.faceSpeed = Math.hypot(vSteady.y, vSteady.z);
    st.energy = clamp(Math.max(Math.abs(st.yawRate) / 2.2, st.faceSpeed / 1.2), 0, 1);
    st.tailX = pos.x - f.x * 0.7;
    st.tailArc = sliceArc(P.x, idx, t);

    // roll of the board relative to gravity, about its own forward axis
    const bu = V(0, 1, 0).applyQuaternion(st.quat);
    const br = V(0, 0, 1).applyQuaternion(st.quat);
    st.roll = Math.atan2(worldUp.dot(br), worldUp.dot(bu));
    st.forward.set(1, 0, 0).applyQuaternion(st.quat);
    st.up.copy(bu);

    group.updateMatrixWorld(true);
    camLocal.copy(camera.position);
    pelican.root.worldToLocal(camLocal);
    pelican.update(t, dt, {
      roll: st.roll,
      accelY: st.acc,
      speed: clamp(1.15 - P.h * 0.9, 0, 1),
      crouch: clamp(0.35 + 0.5 * (1 - P.h) + Math.abs(st.yawRate) * 0.2, 0, 1),
      camLocal,
    });
    st.pos.copy(pos);
  }

  return { group, board, pelican, update, state: st };
}
