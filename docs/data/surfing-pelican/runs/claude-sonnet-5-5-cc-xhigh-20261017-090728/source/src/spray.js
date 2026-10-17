import * as THREE from "three";
import { KIND } from "./particles.js";
import { slicePos } from "./surface.js";
import { REG } from "./profile.js";
import { WAVE } from "./wavefield.js";

const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const P3 = [0, 0, 0];

// Emits everything that flies: board spray, crest streamers, the falling lip curtain and the mist where it lands.
export function createSpray(particles, surfer) {
  const acc = { board: 0, tail: 0, crest: 0, lip: 0, land: 0 };
  const flow = V(-WAVE.speed * 0.85, 0, 0);
  const tmpP = V();
  const tmpV = V();
  const r = particles.rnd;
  const wind = V(-0.4, 0, 1.6);

  function update(t, dt) {
    const st = surfer.state;
    const f = st.forward;
    const up = st.up;
    const right = V().crossVectors(f, up).normalize();
    const energy = 0.35 + 0.65 * st.energy;

    // ---- board spray: a fine sheet off the rails and a tail of droplets
    acc.board += dt * (45 + 220 * energy);
    while (acc.board >= 1) {
      acc.board -= 1;
      const side = r() < 0.5 ? -1 : 1;
      const along = -0.55 + r() * 1.1;
      tmpP.copy(st.pos).addScaledVector(f, along).addScaledVector(right, side * (0.2 + 0.05 * r())).addScaledVector(up, -0.01);
      tmpV.copy(flow).addScaledVector(f, -0.5 - 1.4 * r()).addScaledVector(up, 0.8 + 2.4 * r() * (0.5 + energy)).addScaledVector(right, side * (0.4 + 1.8 * r() * energy));
      if (r() < 0.3) particles.spawn(KIND.drop, tmpP, tmpV.multiplyScalar(1.25), 0.5 + r() * 0.5, 0.012 + 0.012 * r(), 0.2, 1.0, 0.2);
      else particles.spawn(KIND.spray, tmpP, tmpV, 0.6 + r() * 0.7, 0.03 + 0.05 * r(), 1.4, 0.6, 0.5);
    }
    // rooster tail on hard turns
    acc.tail += dt * 160 * Math.pow(energy, 2.2);
    while (acc.tail >= 1) {
      acc.tail -= 1;
      tmpP.copy(st.pos).addScaledVector(f, -0.75).addScaledVector(right, (r() - 0.5) * 0.35);
      tmpV.copy(flow).addScaledVector(f, -1.0 - 2.0 * r()).addScaledVector(up, 2.2 + 3.2 * r()).addScaledVector(right, (r() - 0.5) * 2.4);
      particles.spawn(KIND.spray, tmpP, tmpV, 0.8 + r() * 0.8, 0.06 + 0.09 * r(), 1.6, 0.55, 0.6);
    }

    // ---- crest spray streaming off the back of the wave (offshore wind)
    acc.crest += dt * 95;
    while (acc.crest >= 1) {
      acc.crest -= 1;
      const x = st.pos.x - 40 + r() * 58;
      slicePos(x, REG.B + 4 * r(), t, P3);
      tmpP.set(P3[0], P3[1] + 0.05, P3[2]);
      tmpV.set(-1.2 - 1.8 * r(), 0.6 + 2.2 * r(), 2.2 + 3.6 * r());
      if (r() < 0.3) particles.spawn(KIND.mist, tmpP, tmpV, 1.6 + r() * 1.4, 0.4 + 0.6 * r(), 2.4, 0.14, 0.5, 1.2);
      else particles.spawn(KIND.spray, tmpP, tmpV.multiplyScalar(1.5), 0.9 + r() * 0.9, 0.035 + 0.05 * r(), 1.2, 0.7, 0.35, 3.5);
    }

    // ---- curtain falling from the tip of the lip
    acc.lip += dt * 130;
    while (acc.lip >= 1) {
      acc.lip -= 1;
      const x = st.pos.x - 34 + r() * 40;
      slicePos(x, REG.C + 1 + 3 * r(), t, P3);
      tmpP.set(P3[0], P3[1], P3[2]);
      tmpV.set(flow.x * 0.3 + (r() - 0.5) * 1.0, -0.4 - 1.4 * r(), -0.8 - 1.8 * r());
      particles.spawn(KIND.spray, tmpP, tmpV, 0.5 + r() * 0.5, 0.04 + 0.07 * r(), 1.2, 0.6, 0.3);
    }

    // ---- mist where the lip lands on the floor
    acc.land += dt * 35;
    while (acc.land >= 1) {
      acc.land -= 1;
      const x = st.pos.x - 34 + r() * 40;
      slicePos(x, REG.E + 3 + 5 * r(), t, P3);
      tmpP.set(P3[0], P3[1] + 0.1, P3[2]);
      tmpV.set((r() - 0.5) * 1.2 + flow.x * 0.3, 0.7 + 1.8 * r(), -0.6 - 1.4 * r());
      particles.spawn(KIND.mist, tmpP, tmpV, 1.2 + r() * 1.0, 0.7 + 0.9 * r(), 2.0, 0.16, 0.6, 1.0);
    }

    particles.update(dt, wind);
  }
  return { update };
}
