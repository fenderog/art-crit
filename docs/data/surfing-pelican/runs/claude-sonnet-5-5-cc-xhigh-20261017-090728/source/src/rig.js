import * as THREE from "three";
import { slicePos, wallIndexAt } from "./surface.js";
import { REG } from "./profile.js";

const { lerp, degToRad, smoothstep } = THREE.MathUtils;

// Three framings the camera drifts between, always looking back down the wave at the pelican:
//   tele   - long lens from out on the open water, the whole curl of the lip in frame
//   pocket - inside the curl, looking back along the glowing tube
//   close  - a 3/4 portrait with the sun glowing through the lip behind
const SHOTS = [
  { name: "tele", phi: -26, R: 14, h: 1.1, fov: 23, inside: 0 },
  { name: "pocket", phi: -19, R: 6.4, h: 1.0, fov: 33, inside: 1 },
  { name: "close", phi: -62, R: 6.8, h: 1.2, fov: 32, inside: 0 },
];
const HOLD = 17; // seconds a framing is held
const MOVE = 9; // seconds to drift to the next one

export function createRig(camera, surfer) {
  const pos = new THREE.Vector3();
  const look = new THREE.Vector3();
  const desired = new THREE.Vector3();
  const tipP = [0, 0, 0];
  const wallP = [0, 0, 0];
  let init = false;

  const noise = (t, s) => Math.sin(t * 1.7 * s + 1.3) * 0.5 + Math.sin(t * 2.9 * s + 4.1) * 0.3 + Math.sin(t * 4.3 * s) * 0.2;

  function shot(t) {
    const cycle = HOLD + MOVE;
    const total = cycle * SHOTS.length;
    const u = ((t % total) + total) % total;
    const i = Math.floor(u / cycle);
    const k = smoothstep(u - i * cycle, HOLD, cycle);
    const a = SHOTS[i];
    const b = SHOTS[(i + 1) % SHOTS.length];
    const m = (key) => lerp(a[key], b[key], k);
    return {
      phi: degToRad(m("phi") + 5 * Math.sin(t * 0.13)),
      R: m("R") * (1 + 0.04 * Math.sin(t * 0.21)),
      h: m("h") + 0.25 * Math.sin(t * 0.17),
      fov: m("fov"),
      inside: m("inside"),
    };
  }

  function update(t, dt) {
    const sp = surfer.state.pos;
    const s = shot(t);
    desired.set(sp.x + s.R * Math.cos(s.phi), sp.y + s.h, sp.z + s.R * Math.sin(s.phi));
    desired.y = Math.max(desired.y, lerp(1.5, 1.2, s.inside));

    // Keep the lens out of the water: either well outside the lip's tip, or inside the pocket
    // between the tip and the wall.
    slicePos(desired.x, REG.C + 2, t, tipP);
    const out = Math.min(desired.z, tipP[2] - 3.6, sp.z - 4.2);
    let inn = out;
    if (s.inside > 0.001) {
      const idx = wallIndexAt(desired.x, Math.max(desired.y - 0.1, 0.2), t);
      slicePos(desired.x, idx, t, wallP);
      const lo = tipP[2] + 1.5;
      const hi = Math.min(wallP[2] - 1.6, sp.z - 2.0);
      inn = Math.min(Math.max(desired.z, lo), Math.max(hi, lo));
    }
    desired.z = lerp(out, inn, s.inside);

    // From outside the curl, drop low enough that the hanging tip of the lip does not hide the pelican's head.
    if (s.inside < 0.999) {
      const headY = sp.y + 1.3;
      let u = 0.5;
      for (let k = 0; k < 3; k++) {
        slicePos(sp.x + (desired.x - sp.x) * (1 - u), REG.C + 2, t, tipP);
        u = Math.min(Math.max((tipP[2] - desired.z) / (sp.z - desired.z), 0.05), 0.97);
      }
      const limit = (tipP[1] - 0.45 - u * headY) / (1 - u);
      desired.y = lerp(Math.max(Math.min(desired.y, limit), 0.75), desired.y, s.inside);
    }

    if (!init) {
      pos.copy(desired);
      look.copy(sp);
      init = true;
    } else {
      pos.lerp(desired, 1 - Math.exp(-dt * 2.2));
      look.lerp(sp, 1 - Math.exp(-dt * 3.0));
    }
    camera.position.copy(pos);
    // gentle handheld sway
    camera.position.x += 0.04 * noise(t, 0.9);
    camera.position.y += 0.05 * noise(t + 5, 1.1);
    camera.position.z += 0.04 * noise(t + 9, 0.8);
    const aim = look.clone();
    aim.y += 0.8;
    camera.lookAt(aim);
    camera.rotateZ(0.012 * noise(t + 3, 0.7));
    if (Math.abs(camera.fov - s.fov) > 1e-3) {
      camera.fov = s.fov;
      camera.updateProjectionMatrix();
    }
  }
  return { update, shot };
}
