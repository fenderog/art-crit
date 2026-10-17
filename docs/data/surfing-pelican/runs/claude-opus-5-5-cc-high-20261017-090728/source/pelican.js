import * as THREE from "three";
import { loft, v3 } from "./loft.js";

// A brown pelican in breeding plumage, built from lofted primitives.
// Local frame: forward +X, up +Y, left +Z. Origin is on the deck between the feet.

const C = {
  back: new THREE.Color("#a59c8e"),
  backStreak: new THREE.Color("#6f665b"),
  belly: new THREE.Color("#665446"),
  white: new THREE.Color("#f4efe4"),
  crown: new THREE.Color("#f3d77a"),
  chestnut: new THREE.Color("#5a2e1f"),
  covert: new THREE.Color("#bdb6aa"),
  covertDark: new THREE.Color("#7c7368"),
  flight: new THREE.Color("#2e2520"),
  underwing: new THREE.Color("#4f463f"),
  bill: new THREE.Color("#c9b9a6"),
  billTip: new THREE.Color("#e8692e"),
  pouch: new THREE.Color("#6e3a33"),
  leg: new THREE.Color("#2f3033"),
};

const feather = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 });
const glossy = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.45 });
const legMat = new THREE.MeshStandardMaterial({ color: C.leg, roughness: 0.7 });

function mesh(geo, mat = feather) {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

function featherGeo(length, width, color, blunt = 0) {
  return loft(
    [v3(0, 0, 0), v3(length * 0.5, 0, 0.004), v3(length, 0, 0)],
    (t) => {
      const pointy = Math.pow(Math.sin(Math.PI * Math.min(1, 0.08 + t * 0.92)), 0.6) * (1 - 0.35 * t);
      const round = Math.sqrt(Math.max(0, 1 - Math.pow(Math.max(0, t - 0.75) / 0.25, 2))) * Math.min(1, 0.4 + t * 3);
      return [width * (pointy * (1 - blunt) + round * blunt), 0.006];
    },
    { segments: 10, radial: 8, color: (t, off, c) => c.copy(color).multiplyScalar(off.y < 0 ? 0.8 : 1) }
  );
}

function buildWing(side) {
  const s = side; // +1 left, -1 right
  const shoulder = new THREE.Group();
  shoulder.rotation.order = "YXZ";

  const inner = mesh(
    loft(
      [v3(-0.08, 0, 0), v3(-0.09, 0.012, 0.25 * s), v3(-0.11, 0, 0.5 * s)],
      (t) => [0.175 - 0.035 * t, 0.036 - 0.018 * t],
      {
        segments: 20,
        radial: 16,
        color: (t, off, c) => {
          if (off.y < -0.002) return c.copy(C.underwing);
          if (off.x > -0.02) {
            // streaky silver coverts on the leading half
            const k = 0.5 + 0.5 * Math.sin(t * 60 + off.x * 90);
            return c.copy(C.covert).lerp(C.covertDark, k * 0.25 + (off.x > 0.1 ? 0.25 : 0));
          }
          return c.copy(C.flight);
        },
      }
    )
  );
  shoulder.add(inner);

  // secondaries break up the trailing edge
  for (let i = 0; i < 13; i++) {
    const f = mesh(featherGeo(0.16 + 0.015 * Math.sin(i * 1.7), 0.04, C.flight, 0.85));
    f.position.set(-0.2 - i * 0.003, -0.006 + (i % 2) * 0.004, (0.03 + i * 0.037) * s);
    f.rotation.y = Math.PI + s * (0.12 + i * 0.015);
    shoulder.add(f);
  }

  const wrist = new THREE.Group();
  wrist.rotation.order = "YXZ";
  wrist.position.set(-0.08, 0, 0.5 * s);
  shoulder.add(wrist);

  const hand = mesh(
    loft(
      [v3(-0.01, 0, -0.07 * s), v3(-0.02, 0, 0.11 * s), v3(-0.05, 0, 0.24 * s)],
      (t) => [0.14 - 0.06 * t, 0.018 - 0.008 * t],
      {
        segments: 12,
        radial: 14,
        color: (t, off, c) =>
          off.y < -0.002 ? c.copy(C.underwing) : off.x > 0.02 ? c.copy(C.covertDark) : c.copy(C.flight),
      }
    )
  );
  wrist.add(hand);

  // primaries fan from the tip of the hand
  const primaries = [];
  for (let i = 0; i < 7; i++) {
    const len = 0.32 + 0.06 * Math.sin((i / 6) * Math.PI) - i * 0.01;
    const f = mesh(featherGeo(len, 0.034, C.flight));
    const pivot = new THREE.Group();
    pivot.position.set(-0.03 - i * 0.022, 0, (0.2 + 0.01 * i) * s);
    const baseAng = 0.15 - i * 0.16;
    // feather geometry points along +X; turn it to point outward along the span
    pivot.rotation.y = -s * (Math.PI / 2) + s * baseAng;
    pivot.add(f);
    wrist.add(pivot);
    primaries.push({ pivot, baseAng });
  }

  return { shoulder, wrist, primaries, side: s };
}

function buildLegMesh(rTop, rBot) {
  const g = new THREE.CylinderGeometry(rTop, rBot, 1, 10, 1);
  g.translate(0, 0.5, 0); // spans y 0..1, bottom at origin
  return g;
}

function buildFoot(side) {
  const sh = new THREE.Shape();
  sh.moveTo(-0.025, 0);
  const tips = [
    [0.1, 0.07],
    [0.14, 0.012],
    [0.11, -0.055],
  ];
  sh.lineTo(tips[0][0], tips[0][1]);
  sh.quadraticCurveTo(0.08, 0.035, tips[1][0], tips[1][1]);
  sh.quadraticCurveTo(0.08, -0.015, tips[2][0], tips[2][1]);
  sh.lineTo(-0.025, -0.012);
  sh.lineTo(-0.025, 0);
  const g = new THREE.ExtrudeGeometry(sh, { depth: 0.012, bevelEnabled: true, bevelSize: 0.006, bevelThickness: 0.004, bevelSegments: 2 });
  g.rotateX(-Math.PI / 2);
  if (side < 0) g.scale(1, 1, -1);
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: C.leg, roughness: 0.7, side: THREE.DoubleSide }));
  m.castShadow = true;
  return m;
}

export function createPelican() {
  const root = new THREE.Group();
  const hips = new THREE.Group();
  hips.rotation.order = "YXZ";
  hips.position.set(-0.04, 0.3, 0);
  root.add(hips);

  // ---- body ----
  const body = mesh(
    loft(
      [v3(-0.58, 0.02, 0), v3(-0.36, 0.06, 0), v3(-0.08, 0.15, 0), v3(0.15, 0.28, 0), v3(0.24, 0.4, 0)],
      (t) => {
        const f = Math.pow(Math.sin(Math.PI * Math.min(1, Math.pow(t, 0.85) * 0.97 + 0.02)), 0.55);
        return [0.24 * f, 0.21 * f];
      },
      {
        segments: 40,
        radial: 22,
        color: (t, off, c) => {
          if (off.y < -0.03 || (t > 0.75 && off.x > 0.05)) return c.copy(C.belly);
          const k = 0.5 + 0.5 * Math.sin(t * 70 + off.z * 40);
          return c.copy(C.back).lerp(C.backStreak, k * 0.5);
        },
      }
    )
  );
  hips.add(body);

  // tail fan
  for (let i = 0; i < 5; i++) {
    const f = mesh(featherGeo(0.17, 0.035, C.flight));
    f.position.set(-0.52, 0.03, (i - 2) * 0.025);
    f.rotation.set(0, Math.PI + (i - 2) * 0.22, -0.15);
    hips.add(f);
  }

  // ---- neck ----
  const neckPts = [v3(0.12, 0.3, 0), v3(0.22, 0.48, 0), v3(0.15, 0.62, 0), v3(0.17, 0.75, 0), v3(0.26, 0.82, 0)];
  const neck = mesh(
    loft(neckPts, (t) => [0.1 - 0.042 * t, 0.105 - 0.045 * t], {
      segments: 30,
      radial: 18,
      up: v3(1, 0, 0),
      color: (t, off, c) => {
        // dark chestnut hind-neck, white front and sides
        const back = -off.x / (Math.hypot(off.x, off.z) + 1e-5);
        if (back > 0.55 && t > 0.12 && t < 0.95) return c.copy(C.chestnut);
        if (t < 0.1) return c.copy(C.back).lerp(C.white, t * 10);
        return c.copy(C.white);
      },
    })
  );
  hips.add(neck);

  // ---- head ----
  const head = new THREE.Group();
  head.rotation.order = "YXZ";
  head.position.set(0.27, 0.83, 0);
  hips.add(head);

  const skull = mesh(new THREE.SphereGeometry(1, 24, 16), new THREE.MeshStandardMaterial({ color: C.white, roughness: 0.8 }));
  skull.scale.set(0.095, 0.072, 0.064);
  skull.position.set(0.03, 0.005, 0);
  head.add(skull);
  const crown = mesh(new THREE.SphereGeometry(1, 20, 12), new THREE.MeshStandardMaterial({ color: C.crown, roughness: 0.8 }));
  crown.scale.set(0.07, 0.035, 0.05);
  crown.position.set(0.04, 0.05, 0);
  head.add(crown);

  const eyes = [];
  for (const s of [1, -1]) {
    const eye = new THREE.Group();
    eye.position.set(0.075, 0.018, 0.05 * s);
    const ring = mesh(new THREE.SphereGeometry(0.02, 16, 12), new THREE.MeshStandardMaterial({ color: "#e7a7a0", roughness: 0.6 }));
    ring.scale.set(1, 1, 0.5);
    eye.add(ring);
    const ball = mesh(new THREE.SphereGeometry(0.015, 16, 12), new THREE.MeshStandardMaterial({ color: "#f6f1d6", roughness: 0.2 }));
    ball.position.z = 0.006 * s;
    eye.add(ball);
    const pupil = mesh(new THREE.SphereGeometry(0.0085, 12, 10), new THREE.MeshStandardMaterial({ color: "#0d0b0a", roughness: 0.1 }));
    pupil.position.set(0.004, 0.001, 0.0145 * s);
    eye.add(pupil);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.0028, 8, 6), new THREE.MeshBasicMaterial({ color: "#ffffff" }));
    glint.position.set(0.008, 0.006, 0.02 * s);
    eye.add(glint);
    head.add(eye);
    eyes.push(eye);
  }

  // upper mandible with an orange hooked tip
  const billPts = [v3(0.08, 0.0, 0), v3(0.3, -0.04, 0), v3(0.52, -0.09, 0), v3(0.6, -0.11, 0), v3(0.635, -0.125, 0), v3(0.64, -0.15, 0)];
  const upper = mesh(
    loft(
      billPts,
      (t) => [0.04 - 0.02 * t, t > 0.9 ? 0.016 - (t - 0.9) * 0.1 : 0.017],
      {
        segments: 40,
        radial: 14,
        power: 0.8,
        color: (t, off, c) => {
          if (t > 0.88) return c.copy(C.billTip);
          const k = Math.max(0, (t - 0.55) / 0.33);
          return c.copy(C.bill).lerp(C.billTip, k * k * 0.6);
        },
      }
    ),
    glossy
  );
  head.add(upper);

  // lower mandible + sagging gular pouch, hinged so the bill can open
  const jaw = new THREE.Group();
  jaw.position.set(0.07, -0.02, 0);
  head.add(jaw);
  const pouchGeo = loft(
    [v3(0.0, -0.01, 0), v3(0.14, -0.06, 0), v3(0.3, -0.09, 0), v3(0.46, -0.1, 0), v3(0.56, -0.105, 0)],
    (t) => [0.034 - 0.012 * t, 0.012 + 0.032 * Math.pow(Math.sin(Math.PI * Math.min(1, t * 1.1)), 1.3)],
    {
      segments: 30,
      radial: 16,
      color: (t, off, c) => (off.y > 0.006 ? c.copy(C.bill).multiplyScalar(0.85) : c.copy(C.pouch).lerp(C.chestnut, 0.3 * (1 - t))),
    }
  );
  const pouch = mesh(pouchGeo, glossy);
  jaw.add(pouch);

  // ---- wings ----
  const wings = [buildWing(1), buildWing(-1)];
  for (const w of wings) {
    w.shoulder.position.set(0.06, 0.27, 0.15 * w.side);
    hips.add(w.shoulder);
  }

  // ---- legs (posed with two-bone IK every frame) ----
  const legs = [1, -1].map((s) => {
    const upperLeg = mesh(buildLegMesh(0.042, 0.022), new THREE.MeshStandardMaterial({ color: C.belly, roughness: 0.9 }));
    const lowerLeg = mesh(buildLegMesh(0.02, 0.016), legMat);
    const knee = mesh(new THREE.SphereGeometry(0.022, 10, 8), legMat);
    const foot = buildFoot(s);
    const footPos = v3(s > 0 ? 0.03 : -0.04, 0.004, 0.1 * s);
    foot.position.copy(footPos).add(v3(-0.015, 0, 0));
    foot.rotation.y = s * 0.15;
    root.add(upperLeg, lowerLeg, knee, foot);
    return { upperLeg, lowerLeg, knee, foot, footPos, hipLocal: v3(-0.02, 0.0, 0.085 * s), side: s };
  });

  const anim = {
    blinkT: 2,
    flap: 0,
    flapT: 5,
    clap: 0,
    clapT: 9,
    lookT: 6,
    look: 0,
    lookTarget: 0,
  };

  const tmpA = new THREE.Vector3();
  const tmpB = new THREE.Vector3();
  const tmpC = new THREE.Vector3();
  const Y = new THREE.Vector3(0, 1, 0);

  function placeBone(m, from, to) {
    tmpC.subVectors(to, from);
    const len = tmpC.length();
    m.position.copy(from);
    m.quaternion.setFromUnitVectors(Y, tmpC.divideScalar(len));
    m.scale.set(1, len, 1);
  }

  function solveLegs() {
    hips.updateMatrix();
    const L1 = 0.17;
    const L2 = 0.15;
    for (const leg of legs) {
      const H = tmpA.copy(leg.hipLocal).applyMatrix4(hips.matrix);
      const F = leg.footPos;
      const dir = tmpB.subVectors(F, H);
      let d = dir.length();
      dir.divideScalar(d);
      d = Math.min(d, L1 + L2 - 0.001);
      const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d);
      const h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
      // the ankle points backward, like a real bird
      const hint = new THREE.Vector3(-1, 0, 0.15 * leg.side);
      hint.addScaledVector(dir, -hint.dot(dir)).normalize();
      const K = H.clone().addScaledVector(dir, a).addScaledVector(hint, h);
      const Fc = H.clone().addScaledVector(dir, d);
      placeBone(leg.upperLeg, K, H);
      placeBone(leg.lowerLeg, Fc, K);
      leg.knee.position.copy(K);
    }
  }

  // ctx: { lean, compress, camLocal (Vector3 in root space), dt, t }
  function update(ctx) {
    const { t, dt, lean, compress } = ctx;

    // posture: crouch into compression, bank with the board
    hips.position.y = 0.3 - compress * 0.05 + Math.sin(t * 2.3) * 0.008;
    hips.position.x = -0.04 - compress * 0.02;
    hips.rotation.z = -0.12 - compress * 0.12 + Math.sin(t * 1.1) * 0.02;
    hips.rotation.x = lean * 0.22 + Math.sin(t * 0.9) * 0.02;
    hips.rotation.y = -lean * 0.08;

    // head stays level and occasionally glances at the camera
    anim.lookT -= dt;
    if (anim.lookT < 0) {
      if (anim.lookTarget === 0) {
        const c = ctx.camLocal;
        anim.lookTarget = THREE.MathUtils.clamp(Math.atan2(-c.z, c.x), -1.1, 1.1);
        anim.lookT = 1.6 + Math.random() * 1.2;
      } else {
        anim.lookTarget = 0;
        anim.lookT = 4 + Math.random() * 5;
      }
    }
    anim.look += (anim.lookTarget - anim.look) * Math.min(1, dt * 5);
    head.rotation.y = anim.look - hips.rotation.y + Math.sin(t * 1.7) * 0.04;
    head.rotation.x = -hips.rotation.x * 0.9;
    head.rotation.z = -hips.rotation.z * 0.85 - 0.1 + Math.sin(t * 2.9) * 0.03;

    // blink
    anim.blinkT -= dt;
    let lid = 1;
    if (anim.blinkT < 0) {
      const b = -anim.blinkT / 0.14;
      lid = Math.abs(1 - 2 * Math.min(1, b));
      if (b >= 1) anim.blinkT = 2 + Math.random() * 3.5;
    }
    for (const e of eyes) e.scale.y = Math.max(0.08, lid);

    // the odd bill clap
    anim.clapT -= dt;
    if (anim.clapT < 0) {
      anim.clap += dt / 0.7;
      if (anim.clap >= 1) {
        anim.clap = 0;
        anim.clapT = 7 + Math.random() * 7;
      }
    }
    const open = anim.clap > 0 ? Math.sin(anim.clap * Math.PI * 2) ** 2 * 0.22 : 0;
    jaw.rotation.z = -open - 0.01;
    pouch.scale.y = 1 + Math.sin(t * 7.0) * 0.04 + compress * 0.08;

    // wings: held out for balance, constantly trimming, with an occasional flap
    anim.flapT -= dt;
    if (anim.flapT < 0 && anim.flap === 0) anim.flap = 0.0001;
    let flapLift = 0;
    if (anim.flap > 0) {
      anim.flap += dt / 1.1;
      const f = anim.flap;
      flapLift = Math.sin(f * Math.PI * 4) * Math.sin(f * Math.PI) * 0.5;
      if (f >= 1) {
        anim.flap = 0;
        anim.flapT = 5 + Math.random() * 6;
      }
    }
    for (const w of wings) {
      const s = w.side;
      const trim =
        Math.sin(t * 2.1 + s * 1.3) * 0.08 + Math.sin(t * 5.3 + s * 0.7) * 0.035 + Math.sin(t * 0.7 + s) * 0.06;
      // raise the wing on the outside of the turn
      const raise = 0.28 + trim + flapLift - s * lean * 0.45 + compress * 0.12;
      w.shoulder.rotation.x = -s * raise;
      w.shoulder.rotation.y = -s * (0.18 + 0.05 * Math.sin(t * 1.3 + s));
      w.shoulder.rotation.z = 0.12 + 0.06 * Math.sin(t * 2.1 + s * 1.3 + 0.6) - flapLift * 0.2;
      // wrist bends against the flap so the hand trails
      w.wrist.rotation.x = s * (0.12 + flapLift * 0.35 + trim * 0.4);
      w.wrist.rotation.y = -s * (0.32 + 0.06 * Math.sin(t * 1.9 + s));
      const spread = 1 + 0.15 * Math.sin(t * 3.1 + s) - flapLift * 0.2;
      for (const p of w.primaries) {
        p.pivot.rotation.y = -s * (Math.PI / 2) + s * p.baseAng * spread;
        p.pivot.rotation.z = flapLift * 0.15 * s;
      }
    }

    solveLegs();
  }

  return { group: root, update, hips, head };
}
