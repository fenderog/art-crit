import * as THREE from 'three';
import { PALETTE } from './theme.js';

// The star of the show: a pelican standing on a longboard, built entirely from
// primitives. The root group ("board") is positioned and oriented by the app
// each frame to sit on the wave; update() handles all the posing:
// S-carving lean, crouch pumping, balance wing-shimmies with occasional flap
// bursts, gulping pouch, tail wag, head tracking (it watches the fish), and a
// sagged leash line from the tail plug to its ankle.

const X_AXIS = new THREE.Vector3(1, 0, 0);
const _v1 = new THREE.Vector3();
const _v2 = new THREE.Vector3();
const _v3 = new THREE.Vector3();
const _q1 = new THREE.Quaternion();
const _q2 = new THREE.Quaternion();
const _e1 = new THREE.Euler();

function mat(color, opts = {}) {
  return new THREE.MeshStandardMaterial({ color: new THREE.Color(color), roughness: 0.62, ...opts });
}

// Smooth in-out bump: 0 -> 1 -> 0 once every `period` seconds, lasting `dur`.
function pulse(t, period, dur, phase = 0) {
  const x = ((((t / period + phase) % 1) + 1) % 1) * period;
  if (x >= dur) return 0;
  const u = x / dur;
  return Math.sin(u * Math.PI) ** 2;
}

export function createPelican() {
  const board = new THREE.Group(); // root: placed on the water by the app
  const deckY = 0.193;

  // deck height of the hull at a given x (hull radius * vertical squash)
  const deckAt = (x) => {
    const u = (x + 1.65) / 3.5;
    const taper = Math.sin(Math.PI * THREE.MathUtils.clamp(u, 0, 1) ** 0.9) ** 0.62;
    return 0.42 * 0.46 * taper;
  };

  // ── the longboard ──────────────────────────────────────────────
  const hullPts = [];
  for (let i = 0; i <= 30; i++) {
    const u = i / 30;
    const taper = Math.sin(Math.PI * u ** 0.9) ** 0.62;
    hullPts.push(new THREE.Vector2(Math.max(0.002, 0.46 * taper), -1.65 + 3.5 * u));
  }
  const hullGeo = new THREE.LatheGeometry(hullPts, 28);
  hullGeo.rotateZ(-Math.PI / 2); // length along +X (forward)
  const hull = new THREE.Mesh(hullGeo, mat(PALETTE.board, { roughness: 0.35 }));
  hull.scale.set(1, 0.42, 0.8); // flatten + narrow the circular cross-section
  board.add(hull);

  const matPaint = { roughness: 0.4 };
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.02, 0.15), mat(PALETTE.stripe, matPaint));
  stripe.position.set(0.05, 0.183, 0);
  board.add(stripe);
  for (const zz of [-0.105, 0.105]) {
    const pin = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.016, 0.03), mat(PALETTE.pinstripe, matPaint));
    pin.position.set(0.05, 0.181, zz);
    board.add(pin);
  }
  const patchN = new THREE.Mesh(new THREE.CircleGeometry(0.11, 20), mat(PALETTE.stripe, matPaint));
  patchN.rotation.x = -Math.PI / 2;
  patchN.position.set(1.42, deckAt(1.42) + 0.005, 0);
  board.add(patchN);
  const patchT = new THREE.Mesh(new THREE.CircleGeometry(0.13, 20), mat(PALETTE.fin, matPaint));
  patchT.rotation.x = -Math.PI / 2;
  patchT.position.set(-1.42, deckAt(-1.42) + 0.005, 0);
  board.add(patchT);

  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.34, 0.05), mat(PALETTE.fin, { roughness: 0.5 }));
  fin.position.set(-1.12, -0.26, 0);
  fin.rotation.z = 0.38; // raked back
  board.add(fin);

  // fake contact shadow under the bird
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.5, 24),
    new THREE.MeshBasicMaterial({ color: 0x39220f, transparent: true, opacity: 0.15, depthWrite: false })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.set(0.02, deckY + 0.006, 0);
  shadow.scale.set(1.5, 1.15, 1);
  board.add(shadow);

  // anchors: spray emitters + leash plug
  const nose = new THREE.Object3D();
  nose.position.set(1.85, 0.05, 0);
  board.add(nose);
  const railL = new THREE.Object3D();
  railL.position.set(0.55, 0.08, 0.34);
  board.add(railL);
  const railR = new THREE.Object3D();
  railR.position.set(0.55, 0.08, -0.34);
  board.add(railR);
  const leashTail = new THREE.Object3D();
  leashTail.position.set(-1.5, 0.1, 0.12);
  board.add(leashTail);

  // ── the pelican ────────────────────────────────────────────────
  const pel = new THREE.Group();
  pel.position.set(0.02, deckY - 0.03, 0); // feet on the deck
  board.add(pel);

  const matWhite = mat(PALETTE.pelicanWhite);
  const matDark = mat(PALETTE.pelicanDark, { roughness: 0.75 });
  const matBeak = mat(PALETTE.beak, { roughness: 0.45 });
  const matPouch = mat(PALETTE.pouch, { roughness: 0.55 });
  const matJaw = mat(PALETTE.jaw, { roughness: 0.5 });
  const matFoot = mat(PALETTE.foot, { roughness: 0.55 });
  const matTuft = mat(PALETTE.tuft, { roughness: 0.85 });

  const body = new THREE.Group();
  body.position.y = 0.72;
  pel.add(body);

  const torso = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 18), matWhite);
  torso.scale.set(1.28, 0.94, 0.84);
  body.add(torso);
  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.34, 20, 14), matWhite);
  chest.scale.set(1.2, 0.95, 0.9);
  chest.position.set(0.32, -0.12, 0);
  body.add(chest);

  // tail fan
  const tail = new THREE.Group();
  tail.position.set(-0.6, 0.06, 0);
  tail.rotation.z = -0.45;
  body.add(tail);
  const featherGeo = new THREE.BoxGeometry(0.46, 0.018, 0.1);
  featherGeo.translate(-0.23, 0, 0);
  const tipGeo = new THREE.BoxGeometry(0.16, 0.02, 0.1);
  tipGeo.translate(-0.08, 0, 0);
  for (let i = -2; i <= 2; i++) {
    const p = new THREE.Group();
    p.rotation.y = i * 0.16;
    p.rotation.z = -0.03 * Math.abs(i);
    p.add(new THREE.Mesh(featherGeo, matWhite));
    const tip = new THREE.Mesh(tipGeo, matDark);
    tip.position.set(-0.4, 0, 0);
    p.add(tip);
    tail.add(p);
  }

  // S-curved neck + head
  const neckCurve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0.26, 0.16, 0),
    new THREE.Vector3(0.6, 0.62, 0),
    new THREE.Vector3(0.5, 0.94, 0)
  );
  body.add(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 14, 0.095, 10), matWhite));
  const neckBase = new THREE.Mesh(new THREE.SphereGeometry(0.15, 14, 10), matWhite);
  neckBase.position.set(0.26, 0.16, 0);
  body.add(neckBase);

  const head = new THREE.Group();
  head.position.set(0.5, 0.94, 0);
  body.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.2, 20, 16), matWhite);
  skull.scale.set(1.12, 1.0, 0.9);
  head.add(skull);

  const tuft = new THREE.Group();
  head.add(tuft);
  const tuftGeo = new THREE.BoxGeometry(0.18, 0.03, 0.045);
  tuftGeo.translate(-0.09, 0, 0);
  for (const [dx, dz, rz] of [[-0.08, 0.03, -0.85], [-0.12, 0, -1.1], [-0.08, -0.03, -0.85]]) {
    const f = new THREE.Mesh(tuftGeo, matTuft);
    f.position.set(dx, 0.17, dz);
    f.rotation.z = rz;
    tuft.add(f);
  }

  for (const s of [1, -1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.031, 12, 10), mat(PALETTE.eye, { roughness: 0.25 }));
    eye.position.set(0.1, 0.05, s * 0.155);
    head.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.009, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    glint.position.set(0.118, 0.07, s * 0.166);
    head.add(glint);
  }

  // the famous beak: upper mandible + hinged jaw with a stretchy pouch
  const beak = new THREE.Group();
  beak.position.set(0.185, 0, 0);
  beak.rotation.z = -0.07;
  head.add(beak);
  const upperGeo = new THREE.CylinderGeometry(0.016, 0.058, 0.8, 10);
  upperGeo.rotateZ(-Math.PI / 2);
  const upper = new THREE.Mesh(upperGeo, matBeak);
  upper.position.set(0.4, 0.02, 0);
  beak.add(upper);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.02, 0.08, 8), matBeak);
  hook.position.set(0.815, 0, 0);
  hook.rotation.z = -Math.PI / 2 - 0.5;
  beak.add(hook);
  const jaw = new THREE.Group();
  jaw.position.set(0.02, -0.035, 0);
  beak.add(jaw);
  const mandible = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.018, 0.07), matJaw);
  mandible.position.set(0.31, 0, 0);
  jaw.add(mandible);
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.16, 18, 14), matPouch);
  pouch.scale.set(2.3, 1.0, 0.8);
  pouch.position.set(0.28, -0.07, 0);
  jaw.add(pouch);

  // legs + big webbed feet, staggered like a proper surf stance
  const toeGeo = new THREE.BoxGeometry(0.1, 0.016, 0.045);
  let backFoot = null;
  for (const [fx, fz] of [[0.3, 0.05], [-0.3, -0.05]]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.048, 0.27, 10), matFoot);
    leg.position.set(fx, 0.165, fz);
    pel.add(leg);
    const foot = new THREE.Group();
    foot.position.set(fx, 0.035, fz);
    pel.add(foot);
    const web = new THREE.Mesh(new THREE.BoxGeometry(0.19, 0.02, 0.24), matFoot);
    web.position.set(0.05, 0.006, 0);
    foot.add(web);
    for (const [tz, ry] of [[-0.07, 0.45], [0, 0], [0.07, -0.45]]) {
      const toe = new THREE.Mesh(toeGeo, matFoot);
      toe.position.set(0.14, 0.006, tz);
      toe.rotation.y = ry;
      foot.add(toe);
    }
    if (fx < 0) backFoot = foot;
  }
  const ankle = new THREE.Object3D();
  ankle.position.set(0, 0.06, 0.03);
  backFoot.add(ankle);

  // wings: shoulder -> flap pivot -> arm -> elbow -> forearm -> hand with
  // white secondaries and dark primaries, held half-open for balance
  const wings = [];
  for (const s of [1, -1]) {
    const shoulder = new THREE.Group();
    shoulder.position.set(0.02, 0.18, s * 0.32);
    shoulder.rotation.y = -s * 0.55; // swept back
    body.add(shoulder);
    const flap = new THREE.Group();
    shoulder.add(flap);
    const patch = new THREE.Mesh(new THREE.SphereGeometry(0.11, 14, 10), matWhite);
    patch.scale.set(1.35, 0.75, 1);
    flap.add(patch);
    const armGeo = new THREE.CapsuleGeometry(0.075, 0.4, 6, 12);
    armGeo.rotateX((s * Math.PI) / 2);
    const arm = new THREE.Mesh(armGeo, matWhite);
    arm.position.set(0, 0, s * 0.24);
    flap.add(arm);
    const elbow = new THREE.Group();
    elbow.position.set(0, 0, s * 0.5);
    flap.add(elbow);
    const foreGeo = new THREE.CapsuleGeometry(0.058, 0.34, 6, 12);
    foreGeo.rotateX((s * Math.PI) / 2);
    const forearm = new THREE.Mesh(foreGeo, matWhite);
    forearm.position.set(0, 0, s * 0.22);
    elbow.add(forearm);
    for (let j = 0; j < 3; j++) {
      const p = new THREE.Group();
      p.position.set(0, -0.02, s * (0.08 + 0.13 * j));
      p.rotation.y = -s * (0.04 + 0.11 * j);
      const g = new THREE.BoxGeometry(0.06, 0.012, 0.4);
      g.translate(0, 0, s * 0.2);
      p.add(new THREE.Mesh(g, matWhite));
      elbow.add(p);
    }
    const hand = new THREE.Group();
    hand.position.set(0, 0, s * 0.45);
    elbow.add(hand);
    const primLens = [0.4, 0.48, 0.54, 0.5, 0.42];
    for (let i = 0; i < 5; i++) {
      const p = new THREE.Group();
      p.rotation.y = -s * (0.1 + 0.17 * i);
      p.rotation.x = -s * 0.05 * i;
      const g = new THREE.BoxGeometry(0.07, 0.014, primLens[i]);
      g.translate(0, 0, (s * primLens[i]) / 2);
      p.add(new THREE.Mesh(g, matDark));
      hand.add(p);
    }
    wings.push({ s, shoulder, flap, elbow });
  }

  // leash: sagged polyline from tail plug to ankle, updated each frame
  const LEASH_N = 14;
  const leashArr = new Float32Array(LEASH_N * 3);
  const leashGeo = new THREE.BufferGeometry();
  leashGeo.setAttribute('position', new THREE.BufferAttribute(leashArr, 3).setUsage(THREE.DynamicDrawUsage));
  const leash = new THREE.Line(
    leashGeo,
    new THREE.LineBasicMaterial({ color: new THREE.Color(PALETTE.leash), transparent: true, opacity: 0.9 })
  );
  leash.frustumCulled = false;
  board.add(leash);

  function update(ctx) {
    const t = ctx.t;
    const dt = ctx.dt;

    // stance sway + body language
    pel.rotation.y = 0.14 * Math.sin(0.13 * t) + ctx.lean * 0.12;
    body.position.y = 0.72 + 0.03 * Math.sin(2.2 * t) - ctx.crouch * 0.1;
    body.rotation.z = -0.16 - ctx.crouch * 0.1 + ctx.lean * 0.3;
    body.rotation.x = ctx.lean * 0.38; // twist into the turn

    // wings: idle shimmer + periodic takeoff-style flap bursts
    const burst = pulse(t, 8.5, 1.9, 0.35);
    const flapA = 0.32 + 0.05 * Math.sin(1.4 * t) + burst * 0.5 * Math.sin(11 * t);
    for (const w of wings) {
      w.flap.rotation.x = -w.s * flapA;
      w.elbow.rotation.x = w.s * (0.3 + burst * 0.28 * Math.sin(11 * t - 0.9));
      w.shoulder.rotation.y = -w.s * (0.55 + Math.abs(ctx.lean) * 0.18);
    }

    // gulping pouch
    const gulp = pulse(t, 7.3, 1.3, 0.6);
    jaw.rotation.z = -0.55 * gulp;
    pouch.scale.set(2.3 * (1 + 0.1 * gulp), 1.0 * (1 + 0.55 * gulp), 0.8 * (1 + 0.16 * gulp));

    // head: track the jumping fish, otherwise idle around
    if (ctx.fishWorld) {
      head.getWorldPosition(_v1);
      head.parent.getWorldQuaternion(_q1).invert();
      _v2.copy(ctx.fishWorld).sub(_v1).normalize().applyQuaternion(_q1);
      const ang = Math.acos(THREE.MathUtils.clamp(_v2.x, -1, 1));
      if (ang > 1.15) {
        // clamp how far the neck can turn
        _v3.crossVectors(X_AXIS, _v2);
        if (_v3.lengthSq() < 1e-8) _v3.set(0, 1, 0);
        else _v3.normalize();
        _q2.setFromAxisAngle(_v3, 1.15);
      } else {
        _q2.setFromUnitVectors(X_AXIS, _v2);
      }
    } else {
      _q2.setFromEuler(_e1.set(0.05 * Math.sin(1.6 * t), -ctx.carve * 0.5, 0.07 * Math.sin(1.1 * t) + gulp * 0.22));
    }
    head.quaternion.slerp(_q2, 1 - Math.exp(-6 * dt));

    tail.rotation.y = -ctx.carve * 0.35 + 0.07 * Math.sin(2.0 * t);
    tuft.rotation.z = 0.05 * Math.sin(3.1 * t);

    // leash: sagged arc between tail plug and ankle, in board space
    board.updateMatrixWorld(true);
    ankle.getWorldPosition(_v1);
    board.worldToLocal(_v1);
    leashTail.getWorldPosition(_v2);
    board.worldToLocal(_v2);
    for (let i = 0; i < LEASH_N; i++) {
      const u = i / (LEASH_N - 1);
      leashArr[i * 3] = _v2.x + (_v1.x - _v2.x) * u;
      leashArr[i * 3 + 1] = _v2.y + (_v1.y - _v2.y) * u - Math.sin(Math.PI * u) * 0.2;
      leashArr[i * 3 + 2] = _v2.z + (_v1.z - _v2.z) * u;
    }
    leashGeo.attributes.position.needsUpdate = true;
  }

  return { board, update, nose, railL, railR };
}
