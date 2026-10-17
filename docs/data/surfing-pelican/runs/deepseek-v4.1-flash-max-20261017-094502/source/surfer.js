// The surfer: a procedurally modelled pelican standing on a longboard.
// Everything is built from primitives and a few extruded shapes; the only
// external dependency on the world is the ocean's height field.

import * as THREE from 'three';
import { sampleWater } from './ocean.js';

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */

/** A tapered cylinder between two points, used for legs and wing arms. */
function bone(a, b, rTop, rBottom, material, radialSegments = 9) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(rTop, rBottom, len, radialSegments, 1);
  geo.translate(0, len / 2, 0);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(a);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  return mesh;
}

function circleShadow(radius, opacity) {
  const mesh = new THREE.Mesh(
    new THREE.CircleGeometry(radius, 20),
    new THREE.MeshBasicMaterial({
      color: 0x0c2c38,
      transparent: true,
      opacity,
      depthWrite: false,
    }),
  );
  mesh.rotation.x = -Math.PI / 2;
  return mesh;
}

/* ------------------------------------------------------------------ */
/* surfboard                                                           */
/* ------------------------------------------------------------------ */

function boardOutline(L = 1.72, W = 0.5) {
  const s = new THREE.Shape();
  s.moveTo(L, 0);
  s.bezierCurveTo(L, 0.3, 0.95, W, 0.5, W);
  s.lineTo(-0.5, W);
  s.bezierCurveTo(-1.05, W, -L, 0.3, -L, 0);
  s.bezierCurveTo(-L, -0.3, -1.05, -W, -0.5, -W);
  s.lineTo(0.5, -W);
  s.bezierCurveTo(0.95, -W, L, -0.3, L, 0);
  return s;
}

function makeBoard(materials) {
  const group = new THREE.Group();

  const boardGeo = new THREE.ExtrudeGeometry(boardOutline(), {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.022,
    bevelSize: 0.024,
    bevelSegments: 3,
    curveSegments: 20,
  });
  boardGeo.rotateX(-Math.PI / 2);
  boardGeo.computeBoundingBox();
  const boardTop = boardGeo.boundingBox.max.y;
  boardGeo.translate(0, -boardGeo.boundingBox.min.y, 0);

  const deck = new THREE.Mesh(boardGeo, [materials.deck, materials.rail]);
  group.add(deck);

  // centre stripe
  const stripeGeo = new THREE.ExtrudeGeometry(boardOutline(1.22, 0.08), {
    depth: 0.012,
    bevelEnabled: false,
    curveSegments: 14,
  });
  stripeGeo.rotateX(-Math.PI / 2);
  const stripe = new THREE.Mesh(stripeGeo, materials.stripe);
  stripe.position.y = boardTop - 0.006;
  group.add(stripe);

  // round wax patch near the nose
  const patch = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.012, 24), materials.patch);
  patch.position.set(0.6, boardTop - 0.004, 0);
  group.add(patch);

  // skeg / fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.3, 0);
  finShape.quadraticCurveTo(0.12, -0.18, 0.08, -0.3);
  finShape.quadraticCurveTo(0.02, -0.18, 0, 0);
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.022,
    bevelEnabled: true,
    bevelThickness: 0.006,
    bevelSize: 0.006,
    bevelSegments: 2,
    curveSegments: 10,
  });
  finGeo.translate(0, 0, -0.011);
  const fin = new THREE.Mesh(finGeo, materials.fin);
  fin.position.set(-1.42, 0.07, 0);
  group.add(fin);

  // a slim leash running from the bird's ankle along the rail to the tail
  const leashCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.06, boardTop + 0.05, 0.17),
    new THREE.Vector3(0.28, boardTop + 0.015, 0.34),
    new THREE.Vector3(-0.5, boardTop + 0.008, 0.38),
    new THREE.Vector3(-1.3, 0.06, 0.2),
    new THREE.Vector3(-1.62, 0.05, 0.04),
  ]);
  const leash = new THREE.Mesh(new THREE.TubeGeometry(leashCurve, 24, 0.012, 6, false), materials.leash);
  group.add(leash);

  return { group, boardTop };
}

/* ------------------------------------------------------------------ */
/* pelican                                                             */
/* ------------------------------------------------------------------ */

function bodyGeometry() {
  const profile = [
    [0.001, -0.8], [0.2, -0.7], [0.4, -0.46], [0.53, -0.1],
    [0.53, 0.26], [0.46, 0.54], [0.35, 0.74], [0.001, 0.86],
  ].map(([r, y]) => new THREE.Vector2(r, y));

  const geo = new THREE.LatheGeometry(profile, 30);
  geo.rotateZ(-Math.PI / 2); // lathe axis becomes +X (nose of the body)
  geo.computeVertexNormals();
  return geo;
}

/** A smooth S-curve neck: a tube whose rings are tapered by vertex scaling. */
function neckGeometry() {
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.3, 0.3, 0),
    new THREE.Vector3(0.66, 0.5, 0),
    new THREE.Vector3(0.76, 0.84, 0),
    new THREE.Vector3(0.6, 1.08, 0),
    new THREE.Vector3(0.5, 1.2, 0),
  ]);
  const geo = new THREE.TubeGeometry(curve, 36, 0.165, 12, false);
  const pos = geo.attributes.position;
  const uv = geo.attributes.uv;
  const p = new THREE.Vector3();
  const center = new THREE.Vector3();

  for (let i = 0; i < pos.count; i++) {
    const s = Math.min(uv.getX(i), 1);
    const taper = THREE.MathUtils.lerp(1.0, 0.62, s);
    curve.getPointAt(s, center);
    p.set(pos.getX(i), pos.getY(i), pos.getZ(i));
    p.sub(center).multiplyScalar(taper).add(center);
    pos.setXYZ(i, p.x, p.y, p.z);
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  return geo;
}

function wingGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.2);
  // leading edge
  s.bezierCurveTo(0.45, 0.38, 1.05, 0.31, 1.5, 0.05);
  s.quadraticCurveTo(1.68, -0.03, 1.72, -0.2);
  // trailing edge with feather scallops
  s.quadraticCurveTo(1.48, -0.44, 1.31, -0.23);
  s.quadraticCurveTo(1.2, -0.54, 0.99, -0.32);
  s.quadraticCurveTo(0.86, -0.61, 0.63, -0.36);
  s.quadraticCurveTo(0.46, -0.56, 0.27, -0.34);
  s.quadraticCurveTo(0.12, -0.44, 0, -0.24);
  s.closePath();

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.03,
    bevelEnabled: true,
    bevelThickness: 0.011,
    bevelSize: 0.013,
    bevelSegments: 2,
    curveSegments: 18,
  });
  geo.rotateX(-Math.PI / 2);
  geo.computeVertexNormals();

  // shade the primary feathers towards the tip
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const base = new THREE.Color(0xfffdf6);
  const tip = new THREE.Color(0xdfd5c0);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const k = THREE.MathUtils.smoothstep(pos.getX(i), 0.85, 1.7);
    c.copy(base).lerp(tip, k * 0.7);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geo.scale(0.85, 1, 0.8); // trim the span and chord a little
  return geo;
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, -0.03);
  s.quadraticCurveTo(-0.07, 0.0, -0.11, 0.2);
  s.quadraticCurveTo(-0.05, 0.14, 0, 0.26);
  s.quadraticCurveTo(0.05, 0.14, 0.11, 0.2);
  s.quadraticCurveTo(0.07, 0.0, 0, -0.03);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.026,
    bevelEnabled: true,
    bevelThickness: 0.008,
    bevelSize: 0.008,
    bevelSegments: 2,
    curveSegments: 10,
  });
  geo.rotateX(-Math.PI / 2);
  geo.computeVertexNormals();
  return geo;
}

function tailGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.07);
  s.quadraticCurveTo(0.32, 0.2, 0.62, 0.21);
  s.lineTo(0.74, 0.08);
  s.quadraticCurveTo(0.6, 0.06, 0.74, -0.08);
  s.lineTo(0.62, -0.21);
  s.quadraticCurveTo(0.32, -0.2, 0, -0.07);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.022,
    bevelEnabled: true,
    bevelThickness: 0.008,
    bevelSize: 0.008,
    bevelSegments: 2,
    curveSegments: 12,
  });
  geo.rotateX(-Math.PI / 2);
  geo.computeVertexNormals();
  return geo;
}

function makePelican(materials, boardTop) {
  const root = new THREE.Group(); // origin at the deck, +X is forward
  root.position.y = boardTop;

  /* ---- legs (planted on the board) ---- */
  for (const side of [-1, 1]) {
    const z = 0.17 * side;
    root.add(bone(new THREE.Vector3(0.03, 0.56, z * 0.92), new THREE.Vector3(0.15, 0.29, z), 0.04, 0.047, materials.leg));
    root.add(bone(new THREE.Vector3(0.15, 0.29, z), new THREE.Vector3(0.06, 0.05, z), 0.034, 0.04, materials.leg));

    const foot = new THREE.Mesh(footGeometry(), materials.leg);
    foot.rotation.y = -Math.PI / 2;
    foot.position.set(0.04, 0.012, z);
    root.add(foot);

    const shadow = circleShadow(0.19, 0.22);
    shadow.position.set(0.1, 0.004, z);
    root.add(shadow);
  }

  // soft shadow pooling under the body
  const bodyShadow = circleShadow(0.55, 0.08);
  bodyShadow.position.set(0.02, 0.002, 0);
  root.add(bodyShadow);

  /* ---- torso: everything that bobs with the body ---- */
  const torso = new THREE.Group();
  torso.position.y = 0.8;
  root.add(torso);

  const body = new THREE.Mesh(bodyGeometry(), materials.feather);
  body.rotation.z = 0.06;
  torso.add(body);

  // tail
  const tail = new THREE.Mesh(tailGeometry(), materials.featherShade);
  tail.rotation.y = Math.PI;
  tail.rotation.z = -0.28;
  tail.position.set(-0.66, 0.2, 0);
  torso.add(tail);

  // neck
  const neck = new THREE.Mesh(neckGeometry(), materials.feather);
  torso.add(neck);

  // blend spheres where the neck meets the body
  const neckBase = new THREE.Mesh(new THREE.SphereGeometry(0.19, 18, 14), materials.feather);
  neckBase.position.set(0.38, 0.32, 0);
  torso.add(neckBase);

  /* ---- head ---- */
  const head = new THREE.Group();
  head.position.set(0.5, 1.22, 0);
  torso.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.215, 28, 20), materials.feather);
  skull.scale.set(1.08, 1.0, 0.98);
  head.add(skull);

  // a small swept-back nape tuft
  for (const [i, z] of [[0, 0], [1, 0.055], [2, -0.055]]) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.022, 0.11 - i * 0.012, 6), materials.featherShade);
    crest.rotation.z = 1.7 + i * 0.12;
    crest.position.set(-0.14 - i * 0.02, 0.16 - i * 0.025, z);
    head.add(crest);
  }

  // eyes with a warm ring and a glint
  for (const side of [-1, 1]) {
    const z = 0.178 * side;
    const eyeRing = new THREE.Mesh(new THREE.TorusGeometry(0.046, 0.014, 8, 20), materials.eyeRing);
    eyeRing.position.set(0.07, 0.05, z);
    head.add(eyeRing);

    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.042, 16, 12), materials.eye);
    eye.position.set(0.07, 0.05, z * 1.02);
    head.add(eye);

    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 8), materials.glint);
    glint.position.set(0.095, 0.072, z * 1.1);
    head.add(glint);
  }

  /* ---- bill: upper mandible + gular pouch, hinged at the base ---- */
  const billBase = new THREE.Group();
  billBase.position.set(0.15, 0.02, 0);
  head.add(billBase);

  // the upper mandible and its hooked tip hinge as one piece
  const upperPivot = new THREE.Group();
  upperPivot.rotation.z = -0.1;
  billBase.add(upperPivot);

  const upperGeo = new THREE.CylinderGeometry(0.022, 0.098, 1.0, 12, 1);
  upperGeo.translate(0, 0.5, 0);
  upperGeo.rotateZ(-Math.PI / 2); // point along +X
  upperGeo.scale(1, 0.72, 1.0); // flatter than wide
  upperGeo.computeVertexNormals();
  const upper = new THREE.Mesh(upperGeo, materials.beak);
  upperPivot.add(upper);

  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.1, 8), materials.beak);
  hook.rotation.z = Math.PI; // point down
  hook.position.set(0.97, -0.03, 0);
  upperPivot.add(hook);

  // the gular pouch hangs from the base of the bill
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.2, 22, 16), materials.pouch);
  pouch.scale.set(1.28, 0.5, 0.64);
  pouch.position.set(0.42, -0.19, 0);
  pouch.rotation.z = -0.22;
  billBase.add(pouch);

  const pouchTip = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 12), materials.pouch);
  pouchTip.scale.set(1.25, 0.38, 0.55);
  pouchTip.position.set(0.78, -0.155, 0);
  pouchTip.rotation.z = -0.24;
  billBase.add(pouchTip);

  /* ---- wings ---- */
  const wingGeo = wingGeometry();

  function makeWing(side) {
    const group = new THREE.Group();
    group.position.set(0.02, 0.36, 0.31 * side);
    if (side < 0) group.scale.z = -1;

    const wing = new THREE.Mesh(wingGeo, materials.wing);
    wing.rotation.y = -Math.PI / 2; // span +X -> +Z (outboard)
    group.add(wing);

    // shoulder / humerus hidden under the feathers (mirrored with the group)
    group.add(bone(new THREE.Vector3(0, -0.005, -0.04), new THREE.Vector3(0, 0.005, 0.34), 0.04, 0.055, materials.feather));

    torso.add(group);
    return group;
  }

  const wingL = makeWing(1);
  const wingR = makeWing(-1);

  return { root, torso, head, billBase, upperPivot, pouch, pouchTip, wingL, wingR };
}

/* ------------------------------------------------------------------ */
/* surfer assembly + animation                                         */
/* ------------------------------------------------------------------ */

export function createSurfer() {
  const materials = {
    deck: new THREE.MeshStandardMaterial({ color: 0xff7a4d, roughness: 0.42, metalness: 0.04 }),
    rail: new THREE.MeshStandardMaterial({ color: 0xfdf1de, roughness: 0.5 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0x16b2a8, roughness: 0.45 }),
    patch: new THREE.MeshStandardMaterial({ color: 0xffd98a, roughness: 0.55 }),
    fin: new THREE.MeshStandardMaterial({ color: 0xffc861, roughness: 0.5 }),
    leash: new THREE.MeshStandardMaterial({ color: 0xf4f0e6, roughness: 0.8 }),
    feather: new THREE.MeshStandardMaterial({ color: 0xfffdf6, roughness: 0.85, side: THREE.DoubleSide }),
    featherShade: new THREE.MeshStandardMaterial({ color: 0xe3d9c4, roughness: 0.85, side: THREE.DoubleSide }),
    wing: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, side: THREE.DoubleSide, vertexColors: true }),
    beak: new THREE.MeshStandardMaterial({ color: 0xf3a03a, roughness: 0.48 }),
    pouch: new THREE.MeshStandardMaterial({ color: 0xf1a63a, roughness: 0.6 }),
    leg: new THREE.MeshStandardMaterial({ color: 0xef8d38, roughness: 0.58 }),
    eyeRing: new THREE.MeshStandardMaterial({ color: 0xe8b23c, roughness: 0.5 }),
    eye: new THREE.MeshStandardMaterial({ color: 0x15110d, roughness: 0.28 }),
    glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
  };

  const root = new THREE.Group(); // placed on the water surface
  const boardGroup = new THREE.Group();
  root.add(boardGroup);

  const { group: board, boardTop } = makeBoard(materials);
  boardGroup.add(board);

  const pelican = makePelican(materials, boardTop);
  boardGroup.add(pelican.root);

  /* Reused temporary — keeps the animation loop garbage-free. */
  const local = new THREE.Vector3();

  const state = {
    height: 0,
    pitch: 0,
    roll: 0,
    pitchRate: 0,
    speed: 0,
  };

  let prevPitch = 0;
  let prevY = 0;

  const api = {
    root,
    boardGroup,
    boardTop,

    /** Local point on the board (y measured from the deck) in world space. */
    boardPoint(x, y, z, out = new THREE.Vector3()) {
      local.set(x, boardTop + y, z);
      return boardGroup.localToWorld(out.copy(local));
    },

    update(t, dt) {
      const hN = sampleWater(1.35, 0, t).height;
      const hT = sampleWater(-1.35, 0, t).height;
      const hL = sampleWater(0, 0.45, t).height;
      const hR = sampleWater(0, -0.45, t).height;

      const pitch = Math.atan2(hN - hT, 2.7);
      const roll = -Math.atan2(hR - hL, 0.9);
      const y = (hN + hT) * 0.5 + 0.02;

      root.position.set(0, y, 0);
      root.rotation.set(roll, Math.sin(t * 0.43) * 0.06, pitch);

      state.pitch = pitch;
      state.roll = roll;
      state.height = y;
      state.pitchRate = dt > 0 ? (pitch - prevPitch) / dt : 0;
      state.speed = dt > 0 ? Math.abs(y - prevY) / dt : 0;
      prevPitch = pitch;
      prevY = y;

      /* ---- idle animation ---- */
      pelican.torso.position.y = 0.8 + Math.sin(t * 3.1) * 0.02 + Math.sin(t * 7.4) * 0.005;
      pelican.torso.rotation.z = 0.06 + Math.sin(t * 0.82) * 0.028;
      pelican.torso.rotation.y = Math.sin(t * 0.31) * 0.05;

      pelican.head.rotation.y = Math.sin(t * 0.47) * 0.24;
      pelican.head.rotation.z = Math.sin(t * 0.83 + 1.3) * 0.06;
      pelican.head.rotation.x = Math.sin(t * 0.62) * 0.05;

      // every ~9 seconds the bill opens for a moment, as if taking a breath
      const cyc = (t * 0.115) % 1;
      const open = cyc > 0.9 ? Math.sin(((cyc - 0.9) / 0.1) * Math.PI) : 0;
      pelican.billBase.rotation.z = open * 0.16;
      pelican.billBase.position.y = 0.02 - open * 0.045;
      pelican.upperPivot.rotation.z = -0.1 + open * 0.1;
      pelican.pouch.scale.y = 0.52 + open * 0.2;
      pelican.pouchTip.scale.y = 0.38 + open * 0.16;

      // outstretched wings balancing on the swell, held with a touch of droop
      const flap = Math.sin(t * 1.9) * 0.08 + Math.sin(t * 0.37 + 1.2) * 0.16;
      const droop = 0.1;
      pelican.wingL.rotation.x = -(flap + droop);
      pelican.wingR.rotation.x = flap + droop;
      pelican.wingL.rotation.y = 0.06 + Math.sin(t * 1.9 + 0.5) * 0.05;
      pelican.wingR.rotation.y = -0.06 - Math.sin(t * 1.9 + 0.5) * 0.05;
      pelican.wingL.rotation.z = Math.sin(t * 0.9) * 0.04;
      pelican.wingR.rotation.z = -Math.sin(t * 0.9) * 0.04;

      root.updateMatrixWorld(true);
      return state;
    },
  };

  // place the surfer before the first frame is drawn
  api.update(0, 0);

  // warm up world matrices so boardPoint works immediately
  root.updateMatrixWorld(true);
  return api;
}
