import * as THREE from "three";
import { oceanHeight } from "./waves.js";
import { clamp, lerp, smoothstep } from "./util.js";
import { DECK_Y } from "./board.js";

const HL = 1.32; // probe half-distance along the board
const HW = 0.3; // probe half-distance across the board

/** Cinematic "path" the pelican carves across the swell: a long ellipse with
 *  a couple of incommensurate harmonics on top so it never quite repeats. */
function pathPos(t, out) {
  out.x =
    5.5 * Math.sin(t * 0.19) + 1.35 * Math.sin(t * 0.437 + 1.7) + 0.4 * Math.sin(t * 0.83 + 0.4);
  out.z = 3.5 * Math.cos(t * 0.19 + 0.35) + 0.95 * Math.sin(t * 0.311 + 2.3);
  return out;
}

export function createSurfer({ rig, pelican, spray, wake, shadow }) {
  const pelicanRoot = pelican.root;
  pelicanRoot.position.y = DECK_Y;
  rig.add(pelicanRoot);

  const _p = { x: 0, z: 0 };
  const _pA = { x: 0, z: 0 };
  const _pB = { x: 0, z: 0 };
  const fwd = new THREE.Vector3(1, 0, 0);
  const right = new THREE.Vector3(0, 0, 1);
  const up = new THREE.Vector3(0, 1, 0);
  const surfUp = new THREE.Vector3(0, 1, 0);
  const basis = new THREE.Matrix4();
  const _a = new THREE.Vector3();
  const _b = new THREE.Vector3();
  const _c = new THREE.Vector3();

  const state = {
    yaw: 0,
    yawRate: 0,
    speed: 0,
    accel: 0,
    pitch: 0,
    roll: 0,
    y: 0,
    vy: 0,
    ay: 0,
    bank: 0,
    slip: 0,
    forward: new THREE.Vector3(1, 0, 0),
    right: new THREE.Vector3(0, 0, 1),
  };

  let tailAcc = 0;
  let railAcc = 0;
  let noseCooldown = 0;
  let prevVy = 0;
  let prevSpeed = 0;
  let prevYaw = 0;
  let first = true;

  const tailWorld = new THREE.Vector3();
  const noseWorld = new THREE.Vector3();
  const railWorld = new THREE.Vector3();

  function surfacePoint(out, lx, ly, lz) {
    out
      .copy(rig.position)
      .addScaledVector(fwd, lx)
      .addScaledVector(up, ly)
      .addScaledVector(right, lz);
    return out;
  }

  function update(t, dt) {
    dt = Math.min(dt, 0.05);

    /* ---- where the board is going --------------------------------- */
    const eps = 0.06;
    pathPos(t, _p);
    pathPos(t + eps, _pA);
    pathPos(t - eps, _pB);
    const vx = (_pA.x - _pB.x) / (2 * eps);
    const vz = (_pA.z - _pB.z) / (2 * eps);
    const speed = Math.hypot(vx, vz);

    // the board points mostly where it is going, with a carving slip angle
    const slip = 0.2 * Math.sin(t * 0.37) + 0.12 * Math.sin(t * 0.19 + 2.0);
    let heading = Math.atan2(vz, vx) + slip;

    // smooth the heading so the nose never snaps
    if (first) {
      state.yaw = heading;
      prevYaw = heading;
    } else {
      let d = heading - state.yaw;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      state.yaw += d * (1 - Math.exp(-6 * dt));
    }
    const yawRate = (state.yaw - prevYaw) / Math.max(dt, 1e-4);
    prevYaw = state.yaw;

    /* ---- sample the sea under the board ---------------------------- */
    const cx = _p.x;
    const cz = _p.z;
    const cosY = Math.cos(state.yaw);
    const sinY = Math.sin(state.yaw);
    fwd.set(cosY, 0, sinY);
    right.set(-sinY, 0, cosY);

    const hC = oceanHeight(cx, cz, t);
    const hN = oceanHeight(cx + fwd.x * HL, cz + fwd.z * HL, t);
    const hT = oceanHeight(cx - fwd.x * HL, cz - fwd.z * HL, t);
    const hR = oceanHeight(cx + right.x * HW, cz + right.z * HW, t);
    const hL = oceanHeight(cx - right.x * HW, cz - right.z * HW, t);
    const gF = (hN - hT) / (2 * HL);
    const gR = (hR - hL) / (2 * HW);

    // normal of the plane the board is lying on
    surfUp.set(0, 1, 0).addScaledVector(fwd, -gF).addScaledVector(right, -gR).normalize();

    // carve bank, eased so it never pops
    const targetBank = clamp(yawRate * 1.15, -0.55, 0.55) + 0.05 * Math.sin(t * 0.83);
    state.bank = lerp(state.bank, targetBank, 1 - Math.exp(-3.2 * dt));

    // 1) roll (up, right) about fwd by the bank angle
    const cb = Math.cos(state.bank);
    const sb = Math.sin(state.bank);
    _a.copy(surfUp).multiplyScalar(cb).addScaledVector(right, sb); // banked up
    _b.copy(right).multiplyScalar(cb).addScaledVector(surfUp, -sb); // banked right

    // 2) planing pitch: the nose rides high and pumps with the swell
    const pitch = 0.035 + 0.05 * Math.sin(t * 1.62) + 0.03 * Math.sin(t * 2.7 + 1.1);
    const cp = Math.cos(pitch);
    const sp = Math.sin(pitch);
    _c.copy(fwd).multiplyScalar(cp).addScaledVector(_a, sp); // pitched forward
    _a.multiplyScalar(cp).addScaledVector(fwd, -sp); // pitched up
    fwd.copy(_c);
    up.copy(_a);
    right.copy(_b);

    basis.makeBasis(fwd, up, right);
    rig.quaternion.setFromRotationMatrix(basis);

    /* ---- vertical ride --------------------------------------------- */
    const float = 0.05 + 0.03 * Math.sin(t * 1.62 + 0.9) + 0.04 * speed * 0.2;
    const y = hC + float;
    const vy = first ? 0 : (y - state.y) / Math.max(dt, 1e-4);
    const ay = first ? 0 : clamp((vy - prevVy) / Math.max(dt, 1e-4), -60, 60);
    prevVy = vy;
    rig.position.set(cx, y, cz);

    /* ---- derived motion cues --------------------------------------- */
    state.speed = speed;
    state.accel = first ? 0 : (speed - prevSpeed) / Math.max(dt, 1e-4);
    prevSpeed = speed;
    state.yawRate = yawRate;
    state.pitch = Math.asin(clamp(fwd.y, -1, 1));
    state.roll = Math.asin(clamp(-right.y, -1, 1));
    state.vy = vy;
    state.ay = ay;
    state.y = y;
    state.slip = slip;
    state.forward.copy(fwd);
    state.right.copy(right);
    first = false;

    pelican.update(t, dt, {
      pitch: state.pitch,
      roll: state.roll,
      heave: clamp(ay * 0.05, -0.5, 0.5),
      accelX: clamp(state.accel * 0.6, -1.2, 1.2),
      yawRate: clamp(yawRate, -1.5, 1.5),
      speed,
    });

    /* ---- foam: wake, contact shadow, spray -------------------------- */
    surfacePoint(tailWorld, -1.5, -DECK_Y, 0);
    surfacePoint(noseWorld, 1.55, -DECK_Y, 0);
    const inside = Math.sign(state.bank) || 1;
    surfacePoint(railWorld, -0.15, -DECK_Y, inside * 0.34);

    if (wake) wake.update(dt, t, tailWorld, 0.34);
    if (shadow) {
      shadow.update(t, cx, cz, surfUp, 4.1, 1.5, clamp(0.5 - float * 1.6, 0.18, 0.5));
    }

    if (spray) {
      const chop = Math.abs(gF) + Math.abs(gR);
      // tail wash — a steady rope of droplets off the back of the board
      tailAcc += dt * (40 + speed * 70 + chop * 120);
      while (tailAcc >= 1) {
        tailAcc -= 1;
        const side = Math.random() - 0.5;
        spray.emit({
          x: tailWorld.x + (Math.random() - 0.5) * 0.3,
          y: Math.max(tailWorld.y, oceanHeight(tailWorld.x, tailWorld.z, t)) + 0.02,
          z: tailWorld.z + (Math.random() - 0.5) * 0.3,
          dx: -fwd.x * 0.55 + right.x * side * 0.5,
          dy: 0.42 + Math.random() * 0.3,
          dz: -fwd.z * 0.55 + right.z * side * 0.5,
          spread: 0.5,
          speed: 0.9 + speed * 0.85 + Math.random() * 0.7,
          size: 0.03 + Math.random() * 0.06,
          life: 0.75 + Math.random() * 0.7,
        });
      }

      // rail spray — the fan thrown off the inside rail through a hard carve
      const carve = smoothstep(0.16, 0.6, Math.abs(yawRate)) * (0.6 + speed * 0.5);
      railAcc += dt * carve * 190;
      while (railAcc >= 1) {
        railAcc -= 1;
        spray.emit({
          x: railWorld.x + (Math.random() - 0.5) * 0.9,
          y: Math.max(railWorld.y, oceanHeight(railWorld.x, railWorld.z, t)) + 0.03,
          z: railWorld.z + (Math.random() - 0.5) * 0.9,
          dx: right.x * inside * 0.9 + fwd.x * -0.25,
          dy: 0.5 + Math.random() * 0.45,
          dz: right.z * inside * 0.9 + fwd.z * -0.25,
          spread: 0.45,
          speed: 1.6 + carve * 3.4 + Math.random() * 1.2,
          size: 0.035 + Math.random() * 0.08,
          life: 0.7 + Math.random() * 0.8,
          alpha: 0.85,
        });
      }

      // nose impact — when the board slams down into the trough
      noseCooldown -= dt;
      const slam = -ay * 0.06 - state.pitch * 1.4;
      if (noseCooldown <= 0 && slam > 0.42) {
        noseCooldown = 0.42 + Math.random() * 0.5;
        const n = 14 + Math.floor(Math.random() * 12);
        for (let i = 0; i < n; i++) {
          const side = (Math.random() - 0.5) * 2;
          spray.emit({
            x: noseWorld.x + (Math.random() - 0.5) * 0.35,
            y: Math.max(noseWorld.y, oceanHeight(noseWorld.x, noseWorld.z, t)) + 0.02,
            z: noseWorld.z + (Math.random() - 0.5) * 0.35,
            dx: fwd.x * 0.55 + right.x * side * 0.85,
            dy: 0.62 + Math.random() * 0.5,
            dz: fwd.z * 0.55 + right.z * side * 0.85,
            spread: 0.6,
            speed: 1.4 + Math.random() * 2.6,
            size: 0.05 + Math.random() * 0.11,
            life: 0.8 + Math.random() * 0.9,
          });
        }
      }
      spray.update(dt, t);
    }
  }

  return {
    rig,
    update,
    state,
    get tailWorld() {
      return tailWorld;
    },
  };
}
