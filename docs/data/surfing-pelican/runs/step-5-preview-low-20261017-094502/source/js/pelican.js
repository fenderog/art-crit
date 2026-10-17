// The star of the show: a pelican on a surfboard, procedurally modelled from
// three.js primitives and extruded shapes. No external assets.

import * as THREE from 'three';
import { PALETTE } from './palette.js';
import { waveHeight, waveNormal } from './waves.js';

// ---------------------------------------------------------------------------
// small helpers
// ---------------------------------------------------------------------------

const std = (color, opts = {}) =>
  new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    roughness: 0.82,
    metalness: 0.0,
    ...opts,
  });

function extrude(shape, { depth, bevel, bevelSize, curveSegments = 14 }) {
  // NOTE: ExtrudeGeometry spans z from -bevel to depth + bevel, so pass the
  // half-thickness in `bevel` and the core thickness in `depth`.
  return new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize,
    bevelSegments: 4,
    curveSegments,
    steps: 1,
  });
}

function mesh(geometry, material, name) {
  const m = new THREE.Mesh(geometry, material);
  m.name = name;
  return m;
}

const thin = { side: THREE.DoubleSide };

// ---------------------------------------------------------------------------
// surfboard
// ---------------------------------------------------------------------------

function buildBoard() {
  const group = new THREE.Group();
  group.name = 'board';

  // plan-view outline (length along x, width along y) which is then rotated so
  // that the nose points towards +z.
  const s = new THREE.Shape();
  s.moveTo(0, 2.45);
  s.bezierCurveTo(0.42, 1.65, 0.5, 0.72, 0.48, 0.0);
  s.bezierCurveTo(0.46, -0.62, 0.4, -1.3, 0.0, -1.6);
  s.bezierCurveTo(-0.4, -1.3, -0.46, -0.62, -0.48, 0.0);
  s.bezierCurveTo(-0.5, 0.72, -0.42, 1.65, 0.0, 2.45);

  const geo = extrude(s, { depth: 0.2, bevel: 0.055, bevelSize: 0.045, curveSegments: 24 });
  geo.rotateX(Math.PI / 2);
  geo.rotateY(-Math.PI / 2);
  geo.computeBoundingBox();
  const bb = geo.boundingBox;
  // rest the board on y = 0 and centre it along its length
  geo.translate(0, -bb.min.y, -(bb.min.z + bb.max.z) / 2);

  group.add(mesh(geo, std(PALETTE.deck, { roughness: 0.62 }), 'deck'));

  const stringer = mesh(
    new THREE.BoxGeometry(0.075, 0.02, 4.1),
    std(PALETTE.stringer, { roughness: 0.5 }),
    'stringer',
  );
  stringer.position.set(0, 0.325, 0.05);
  group.add(stringer);

  for (const x of [-0.19, 0.19]) {
    const pin = mesh(
      new THREE.BoxGeometry(0.028, 0.016, 3.5),
      std(PALETTE.pinstripe, { roughness: 0.45, metalness: 0.2 }),
      'pinstripe',
    );
    pin.position.set(x, 0.322, 0.1);
    group.add(pin);
  }

  const pad = mesh(
    new THREE.BoxGeometry(0.16, 0.012, 0.7),
    std(PALETTE.stringer, { roughness: 0.7 }),
    'nosepad',
  );
  pad.position.set(0, 0.32, 1.3);
  group.add(pad);

  // tail fin
  const fin = mesh(new THREE.ConeGeometry(0.24, 0.6, 4), std(PALETTE.fin, { roughness: 0.6 }), 'fin');
  fin.scale.set(0.35, 1, 1.5);
  fin.rotation.x = -0.42;
  fin.position.set(0, -0.1, -1.45);
  group.add(fin);

  return group;
}

// ---------------------------------------------------------------------------
// pelican
// ---------------------------------------------------------------------------

// wing outline: x = span outwards, y = chord (forwards positive)
function wingShape() {
  const s = new THREE.Shape();
  s.moveTo(0, -0.3);
  s.quadraticCurveTo(0.45, -0.32, 0.86, -0.11);
  s.quadraticCurveTo(0.99, 0.02, 0.9, 0.13);
  s.quadraticCurveTo(0.5, 0.32, 0.0, 0.24);
  s.lineTo(0, -0.3);
  return s;
}

// mirror a geometry in x (positions + normals)
function mirrorX(geo) {
  const pos = geo.attributes.position;
  const nor = geo.attributes.normal;
  for (let i = 0; i < pos.count; i++) {
    pos.setX(i, -pos.getX(i));
    if (nor) nor.setX(i, -nor.getX(i));
  }
  pos.needsUpdate = true;
  if (nor) nor.needsUpdate = true;
  return geo;
}

function buildWing(sign) {
  const geo = extrude(wingShape(), { depth: 0.03, bevel: 0.02, bevelSize: 0.018, curveSegments: 20 });
  geo.rotateX(Math.PI / 2); // span -> x, chord -> z, thickness -> y
  if (sign < 0) mirrorX(geo);

  // dark wing tips through vertex colours
  const count = geo.attributes.position.count;
  const colors = new Float32Array(count * 3);
  const light = new THREE.Color(PALETTE.wing);
  const dark = new THREE.Color(PALETTE.wingTip);
  const c = new THREE.Color();
  const v = new THREE.Vector3();
  for (let i = 0; i < count; i++) {
    v.fromBufferAttribute(geo.attributes.position, i);
    const k = 1 - THREE.MathUtils.smoothstep(Math.abs(v.x), 0.6, 0.74);
    c.copy(dark).lerp(light, k);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

  return mesh(geo, std('#ffffff', { ...thin, vertexColors: true, roughness: 0.88 }), 'wing');
}

// tail fan: x = span outwards, y = chord (backwards positive)
function buildTail() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.06);
  s.bezierCurveTo(0.2, 0.22, 0.46, 0.2, 0.56, 0.04);
  s.bezierCurveTo(0.5, -0.08, 0.3, -0.16, 0.0, -0.2);
  s.lineTo(0, 0.06);
  const geo = extrude(s, { depth: 0.03, bevel: 0.02, bevelSize: 0.018, curveSegments: 16 });
  geo.rotateX(Math.PI / 2);
  geo.scale(1, 1, -1); // fan points backwards
  mirrorX(geo); // ... and keep the front faces pointing up
  return mesh(geo, std(PALETTE.body, { ...thin, roughness: 0.85 }), 'tail');
}

function buildPelican() {
  const g = new THREE.Group();
  g.name = 'pelican';

  // --- torso ---------------------------------------------------------------
  const bodyGeo = new THREE.SphereGeometry(0.42, 28, 20);
  bodyGeo.scale(0.72, 0.95, 1.5);
  const body = mesh(bodyGeo, std(PALETTE.body, { roughness: 0.9 }), 'body');
  body.position.set(0, 0.66, -0.08);
  g.add(body);

  // --- neck ----------------------------------------------------------------
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.86, 0.02),
    new THREE.Vector3(0.03, 1.12, 0.12),
    new THREE.Vector3(0.0, 1.36, 0.24),
    new THREE.Vector3(0.0, 1.5, 0.3),
  ]);
  const neckGeo = new THREE.TubeGeometry(curve, 28, 0.155, 16, false);
  g.add(mesh(neckGeo, std(PALETTE.body, { roughness: 0.9 }), 'neck'));

  // bandana collar around the neck
  const bt = curve.getTangentAt(0.16).normalize();
  const bp = curve.getPointAt(0.16);
  const collar = mesh(
    new THREE.TorusGeometry(0.163, 0.032, 8, 22),
    std(PALETTE.bandana, { roughness: 0.85 }),
    'collar',
  );
  collar.position.copy(bp);
  collar.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), bt);
  g.add(collar);
  const knot = mesh(new THREE.BoxGeometry(0.11, 0.07, 0.05), std(PALETTE.bandana), 'knot');
  knot.position.copy(bp).add(new THREE.Vector3(0.16, -0.02, 0).applyQuaternion(collar.quaternion));
  g.add(knot);

  // --- head ----------------------------------------------------------------
  const head = new THREE.Group();
  head.name = 'head';
  head.position.set(0, 1.52, 0.32);
  g.add(head);

  const skullGeo = new THREE.SphereGeometry(0.225, 24, 18);
  skullGeo.scale(0.95, 1.0, 1.05);
  head.add(mesh(skullGeo, std(PALETTE.body, { roughness: 0.85 }), 'skull'));

  const crest = mesh(new THREE.ConeGeometry(0.06, 0.17, 6), std(PALETTE.body), 'crest');
  crest.position.set(0, 0.2, -0.035);
  crest.rotation.x = -0.45;
  head.add(crest);

  // upper mandible: a thin, slightly hooked blade built as a side profile
  const bs = new THREE.Shape();
  bs.moveTo(-0.04, 0.07);
  bs.quadraticCurveTo(0.5, 0.11, 1.0, 0.07);
  bs.quadraticCurveTo(1.14, 0.05, 1.12, -0.01);
  bs.quadraticCurveTo(0.7, -0.05, -0.04, -0.05);
  bs.lineTo(-0.04, 0.07);
  const beakGeo = extrude(bs, { depth: 0.085, bevel: 0.025, bevelSize: 0.018, curveSegments: 20 });
  beakGeo.rotateY(-Math.PI / 2); // profile length -> +z
  beakGeo.translate(0, 0, -0.08);
  head.add(mesh(beakGeo, std(PALETTE.beak, { roughness: 0.55 }), 'beak'));

  // the pouch, hanging under the mandible
  const pouchGeo = new THREE.SphereGeometry(0.15, 20, 14);
  pouchGeo.scale(1.0, 0.78, 3.6);
  const pouch = mesh(pouchGeo, std(PALETTE.pouch, { roughness: 0.6 }), 'pouch');
  pouch.position.set(0, -0.07, 0.72);
  head.add(pouch);

  // eyes
  for (const x of [-1, 1]) {
    const eye = mesh(new THREE.SphereGeometry(0.038, 12, 10), std(PALETTE.eye, { roughness: 0.35 }), 'eye');
    eye.position.set(0.125 * x, 0.035, 0.11);
    head.add(eye);
    const gleam = mesh(
      new THREE.SphereGeometry(0.013, 8, 8),
      std('#ffffff', { roughness: 0.2, emissive: new THREE.Color('#ffffff'), emissiveIntensity: 0.2 }),
      'gleam',
    );
    gleam.position.set(0.134 * x, 0.05, 0.145);
    head.add(gleam);
  }

  // --- legs + webbed feet --------------------------------------------------
  for (const z of [0.5, -0.38]) {
    const leg = mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.3, 10), std(PALETTE.foot, { roughness: 0.8 }), 'leg');
    leg.position.set(0.02, 0.42, z);
    g.add(leg);
    const footGeo = new THREE.SphereGeometry(0.16, 14, 8);
    footGeo.scale(1.35, 0.4, 1.5);
    const foot = mesh(footGeo, std(PALETTE.foot, { roughness: 0.85 }), 'foot');
    foot.position.set(0.02, 0.31, z + 0.04);
    g.add(foot);
  }

  // --- wings ---------------------------------------------------------------
  const wingPivots = [];
  for (const sign of [1, -1]) {
    const pivot = new THREE.Group();
    pivot.name = sign > 0 ? 'wingL' : 'wingR';
    pivot.position.set(0.24 * sign, 0.9, -0.02);
    pivot.add(buildWing(sign));
    g.add(pivot);
    wingPivots.push(pivot);
  }

  return { group: g, head, wingPivots };
}

// ---------------------------------------------------------------------------
// rider: board + pelican riding the swell
// ---------------------------------------------------------------------------

const SPEED = 9.6;

export function createRider(scene) {
  const rider = new THREE.Group();
  rider.name = 'rider';
  scene.add(rider);

  const board = buildBoard();
  rider.add(board);

  const pelican = buildPelican();
  rider.add(pelican.group);
  pelican.group.position.y = 0.31;
  pelican.group.rotation.y = -0.42; // a loose sideways surf stance

  const state = {
    position: new THREE.Vector3(),
    forward: new THREE.Vector3(0, 0, 1),
    up: new THREE.Vector3(0, 1, 0),
    right: new THREE.Vector3(1, 0, 0),
    speed: 0,
    lean: 0,
    wave: 0,
  };

  const n = new THREE.Vector3();
  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const up = new THREE.Vector3();
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();

  function update(t) {
    // --- path: a long, lazy carve down the line ----------------------------
    const x = t * SPEED;
    const z = 26 * Math.sin(t * 0.078) + 7 * Math.sin(t * 0.31 + 1.1);
    const dx = SPEED;
    const dz = 26 * 0.078 * Math.cos(t * 0.078) + 7 * 0.31 * Math.cos(t * 0.31 + 1.1);
    const speed = Math.hypot(dx, dz);

    const h = waveHeight(x, z, t);
    waveNormal(x, z, t, n);

    fwd.set(dx, 0, dz).normalize();
    right.crossVectors(n, fwd).normalize();
    up.crossVectors(fwd, right).normalize();
    m.makeBasis(right, up, fwd);
    q.setFromRotationMatrix(m);

    // --- banking into the turns -------------------------------------------
    const curvature =
      (-26 * 0.078 * 0.078 * Math.sin(t * 0.078) -
        7 * 0.31 * 0.31 * Math.sin(t * 0.31 + 1.1)) /
      speed;
    const leanTarget = THREE.MathUtils.clamp(curvature * 6.0, -0.34, 0.34);
    state.lean += (leanTarget - state.lean) * 0.09;

    rider.position.set(x, h + 0.13, z);
    rider.quaternion.copy(q);
    rider.rotateZ(state.lean);

    state.position.copy(rider.position);
    state.forward.copy(fwd);
    state.up.copy(up);
    state.right.copy(right);
    state.speed = speed;
    state.wave = h;
    state.time = t;

    // --- body language -----------------------------------------------------
    const bob = Math.sin(t * 2.1) * 0.02 + Math.sin(t * 3.7 + 1.0) * 0.012;
    pelican.group.position.y = 0.31 + bob;
    pelican.group.rotation.z = -state.lean * 0.55 + Math.sin(t * 1.7) * 0.03;
    pelican.group.rotation.x = -0.04 + Math.sin(t * 2.6) * 0.02;

    pelican.head.rotation.y = 0.42 + Math.sin(t * 0.53) * 0.3 + Math.sin(t * 1.31) * 0.06;
    pelican.head.rotation.x = Math.sin(t * 0.77) * 0.09 - 0.05;
    pelican.head.rotation.z = -state.lean * 0.2;

    // wings glide most of the time, with a flap when the swell asks for it
    const flapEnv = 0.5 + 0.5 * Math.sin(t * 0.21 + Math.sin(t * 0.13) * 1.5);
    const flap = Math.sin(t * 4.6) * 0.44 * flapEnv + Math.sin(t * 1.15) * 0.05;
    const sweep = Math.sin(t * 2.3) * 0.12;
    const spread = 0.3 + Math.sin(t * 0.9) * 0.04;
    pelican.wingPivots[0].rotation.z = spread + flap;
    pelican.wingPivots[1].rotation.z = -(spread + flap);
    pelican.wingPivots[0].rotation.y = -0.26 + sweep;
    pelican.wingPivots[1].rotation.y = 0.26 - sweep;
  }

  update(0);
  return { group: rider, board, state, update };
}
