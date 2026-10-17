// pelican.js — the star. A stylised white pelican on a longboard, built from
// primitives, with flapping wings, a fluttering scarf, sunglasses and a beak
// that snaps open when dinner arrives.

import * as THREE from 'three';
import { taperedTube, plate, flattenXZ, mesh } from './geom.js';
import { waveHeight, waveNormalAt } from './waves.js';

const std = (color, roughness, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0, ...extra });

/** Paint a plate by how far out along its span it is (wingtips go dark). */
function colourBySpan(geometry, from, dark, light) {
  const pos = geometry.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const d = new THREE.Color(dark);
  const l = new THREE.Color(light);
  for (let i = 0; i < pos.count; i++) {
    const z = Math.abs(pos.getZ(i));
    const c = z > from ? d : l;
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  return geometry;
}

function boardGeometry() {
  const geo = new THREE.SphereGeometry(1, 40, 22);
  geo.scale(0.40, 0.088, 1.02);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    const t = x / 0.40; // -1 .. 1 along the board
    // rocker: the nose and tail lift out of the water
    const bend = 0.055 * t * t + 0.10 * Math.pow(Math.max(0, Math.abs(t) - 0.52) / 0.48, 1.8);
    pos.setY(i, y + bend);
    // taper the outline towards both ends
    const taper = 1 - 0.62 * Math.pow(Math.max(0, Math.abs(t) - 0.30) / 0.70, 1.7);
    pos.setZ(i, z * taper);
  }
  // classic livery: cream with a coral centre stripe and dark pinstripes
  const colors = new Float32Array(pos.count * 3);
  const cream = new THREE.Color(0xf2ece0);
  const coral = new THREE.Color(0xe0653f);
  const stripe = new THREE.Color(0x22303c);
  const deck = new THREE.Color(0x2b333d);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    const a = Math.abs(z);
    if (y > 0.075 && x < -0.95) c.copy(deck);
    else if (a < 0.045) c.copy(stripe);
    else if (a < 0.15) c.copy(coral);
    else c.copy(cream);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.computeVertexNormals();
  return geo;
}

function finGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0.34, 0.0);
  s.quadraticCurveTo(0.10, -0.10, -0.18, -0.14);
  s.quadraticCurveTo(-0.26, -0.06, -0.20, 0.0);
  s.quadraticCurveTo(-0.10, 0.06, 0.10, 0.02);
  s.quadraticCurveTo(0.22, 0.02, 0.34, 0.0);
  return plate(s, 0.035, 14);
}

function wingShape() {
  const s = new THREE.Shape();
  s.moveTo(0.30, 0.03);
  s.quadraticCurveTo(0.14, 0.56, -0.04, 1.12);
  s.quadraticCurveTo(-0.09, 1.16, -0.17, 1.10);
  s.quadraticCurveTo(-0.30, 0.62, -0.40, 0.03);
  s.closePath();
  return s;
}

function featherShape() {
  const s = new THREE.Shape();
  s.moveTo(0.05, 0.01);
  s.quadraticCurveTo(0.04, 0.16, 0.015, 0.30);
  s.quadraticCurveTo(-0.035, 0.16, -0.05, 0.01);
  s.closePath();
  return s;
}

/** A plate whose span runs along +Z (side=+1) or -Z (side=-1). */
function spanPlate(shape, thickness, side, curveSegments = 12) {
  const geo = plate(shape, thickness, curveSegments);
  if (side > 0) geo.rotateX(Math.PI / 2);
  else geo.rotateX(-Math.PI / 2);
  return geo;
}

function footShape() {
  const s = new THREE.Shape();
  s.moveTo(0.16, 0.0);
  s.quadraticCurveTo(0.04, 0.10, -0.08, 0.13);
  s.quadraticCurveTo(-0.16, 0.12, -0.15, 0.0);
  s.quadraticCurveTo(-0.16, -0.12, -0.08, -0.13);
  s.quadraticCurveTo(0.04, -0.10, 0.16, 0.0);
  return s;
}

function tailShape() {
  const s = new THREE.Shape();
  s.moveTo(0.42, 0.04);
  s.quadraticCurveTo(0.20, 0.15, -0.14, 0.21);
  s.quadraticCurveTo(-0.26, 0.13, -0.22, 0.01);
  s.quadraticCurveTo(-0.28, -0.13, -0.14, -0.21);
  s.quadraticCurveTo(0.20, -0.15, 0.42, -0.04);
  s.closePath();
  return s;
}

function scarfGeometry() {
  return new THREE.PlaneGeometry(0.17, 0.60, 4, 10);
}

/** rounded rectangle outline (used for the sunglasses lenses) */
function roundedRect(w, h, r = 0.035) {
  const s = new THREE.Shape();
  const x = -w / 2;
  const y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

export function createRider() {
  const root = new THREE.Group();
  root.name = 'rider';

  const boardGroup = new THREE.Group();
  root.add(boardGroup);

  // ---------------- board ------------------------------------------------
  const boardMat = std(0xffffff, 0.45, { vertexColors: true });
  const board = mesh(boardGeometry(), boardMat);
  board.position.y = 0.02;
  boardGroup.add(board);

  const finMat = std(0xf2ece0, 0.5);
  const fin = mesh(finGeometry(), finMat);
  fin.position.set(-0.62, -0.075, 0);
  fin.rotation.z = 0.06;
  boardGroup.add(fin);

  // ---------------- bird -------------------------------------------------
  const rig = new THREE.Group();
  rig.position.y = 0.105;
  root.add(rig);

  const featherMat = std(0xf8f2e7, 0.92);
  const wingMat = std(0xeaeef4, 0.85, { vertexColors: true });
  const darkMat = std(0x2b3040, 0.72);
  const beakMat = std(0xf08a2e, 0.42);
  const pouchMat = std(0xf8b56c, 0.6);
  const footMat = std(0xe5842f, 0.55);
  const glassMat = std(0x121722, 0.2);
  const scarfMat = std(0xd4483f, 0.85, { side: THREE.DoubleSide });

  // body
  const body = mesh(new THREE.SphereGeometry(1, 32, 24), featherMat);
  body.scale.set(1.0, 0.85, 0.68);
  body.position.set(0, 0.95, 0);
  rig.add(body);

  // belly shading trick: a slightly darker underside cap
  const belly = mesh(new THREE.SphereGeometry(1, 32, 24), std(0xe8ddc9, 0.95));
  belly.scale.set(0.98, 0.6, 0.6);
  belly.position.set(0.03, 0.62, 0);
  rig.add(belly);

  // tail
  const tailGroup = new THREE.Group();
  tailGroup.position.set(-0.86, 0.98, 0);
  const tail = mesh(flattenXZ(plate(tailShape(), 0.05, 16)), featherMat);
  tailGroup.add(tail);
  const tailTip = mesh(flattenXZ(plate(tailShape(), 0.055, 16)), darkMat);
  tailTip.position.set(-0.05, 0.004, 0);
  tailTip.scale.set(0.52, 1, 0.62);
  tailTip.position.set(-0.10, 0.004, 0);
  tailGroup.add(tailTip);
  rig.add(tailGroup);

  // neck
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.02, 1.42, 0.03),
    new THREE.Vector3(0.22, 1.62, 0.03),
    new THREE.Vector3(0.40, 1.80, 0.0),
    new THREE.Vector3(0.55, 1.99, -0.02),
    new THREE.Vector3(0.62, 2.12, -0.03),
  ]);
  const neck = mesh(
    taperedTube(neckCurve, 26, 16, (t) => 0.235 * (1 - 0.24 * t)),
    featherMat,
  );
  rig.add(neck);

  // head
  const headGroup = new THREE.Group();
  headGroup.position.set(0.62, 2.12, -0.03);
  rig.add(headGroup);

  const head = mesh(new THREE.SphereGeometry(0.19, 28, 22), featherMat);
  head.scale.set(1.05, 0.95, 0.93);
  headGroup.add(head);

  // little crest feathers
  for (let i = 0; i < 3; i++) {
    const crest = mesh(new THREE.ConeGeometry(0.028 - i * 0.005, 0.20, 8), featherMat);
    crest.position.set(-0.14, 0.06 + i * 0.035, -0.05 + i * 0.05);
    crest.rotation.set(-0.5, 0.4, 1.9);
    headGroup.add(crest);
  }

  // eyes
  const eyeMat = std(0x11151d, 0.25);
  const glintMat = std(0xffffff, 0.2, { emissive: 0x444444, emissiveIntensity: 0.4 });
  for (const s of [1, -1]) {
    const eye = mesh(new THREE.SphereGeometry(0.047, 16, 12), eyeMat);
    eye.position.set(0.10, 0.05, 0.135 * s);
    headGroup.add(eye);
    const glint = mesh(new THREE.SphereGeometry(0.014, 10, 8), glintMat);
    glint.position.set(0.115, 0.075, 0.152 * s);
    headGroup.add(glint);

    // sunglasses
    const lens = mesh(
      plate(roundedRect(0.14, 0.10), 0.014, 10).rotateY(Math.PI / 2),
      glassMat,
    );
    lens.material = glassMat;
    lens.position.set(0.185, -0.005, 0.115 * s);
    headGroup.add(lens);
  }
  const bridge = mesh(new THREE.BoxGeometry(0.02, 0.014, 0.07), glassMat);
  bridge.position.set(0.2, -0.005, 0);
  headGroup.add(bridge);

  // beak — upper mandible
  const beakUpper = mesh(new THREE.CylinderGeometry(0.028, 0.145, 0.66, 14), beakMat);
  beakUpper.geometry.rotateZ(-Math.PI / 2);
  beakUpper.scale.set(1, 0.34, 1.18);
  beakUpper.position.set(0.99, 0.02, -0.03);
  headGroup.add(beakUpper);

  // beak — lower mandible + pouch, hinged so it can open
  const lowerPivot = new THREE.Group();
  lowerPivot.position.set(0.76, -0.045, -0.03);
  headGroup.add(lowerPivot);

  const beakLower = mesh(new THREE.CylinderGeometry(0.022, 0.125, 0.58, 14), beakMat);
  beakLower.geometry.rotateZ(-Math.PI / 2);
  beakLower.scale.set(1, 0.55, 1.10);
  beakLower.position.set(0.28, 0, 0);
  lowerPivot.add(beakLower);

  const pouch = mesh(new THREE.SphereGeometry(1, 22, 16), pouchMat);
  pouch.scale.set(0.30, 0.15, 0.135);
  pouch.position.set(0.24, -0.10, 0);
  lowerPivot.add(pouch);
  const beakTip = mesh(new THREE.ConeGeometry(0.032, 0.09, 10), beakMat);
  beakTip.geometry.rotateZ(-Math.PI / 2);
  beakTip.position.set(0.55, 0, 0);
  lowerPivot.add(beakTip);

  // beak tip world position (used by the fish to fly into the mouth)
  const mouth = new THREE.Object3D();
  mouth.position.set(0.20, 0.0, 0);
  lowerPivot.add(mouth);

  // wings
  const wingGeoRight = colourBySpan(
    spanPlate(wingShape(), 0.05, 1, 16), 0.74, 0x2b3040, 0xeaeef4,
  );
  const wingGeoLeft = colourBySpan(
    spanPlate(wingShape(), 0.05, -1, 16), 0.74, 0x2b3040, 0xeaeef4,
  );
  const featherGeoRight = spanPlate(featherShape(), 0.028, 1, 10);

  const wings = [];
  for (const side of [1, -1]) {
    const shoulder = new THREE.Group();
    shoulder.position.set(0.16, 1.28, 0.42 * side);
    rig.add(shoulder);

    const w = mesh(side > 0 ? wingGeoRight : wingGeoLeft, wingMat);
    shoulder.add(w);

    const tip = new THREE.Group();
    tip.position.set(-0.10, 0.02, 1.06 * side);
    shoulder.add(tip);
    for (let i = 0; i < 3; i++) {
      const f = mesh(featherGeoRight, darkMat);
      if (side < 0) f.scale.z = -1;
      f.position.set(0, 0, 0);
      f.rotation.x = (i - 1) * 0.16 * side;
      f.rotation.y = (i - 1) * -0.12 * side;
      f.position.set(0.03 * (i - 1), 0, 0);
      tip.add(f);
    }
    wings.push({ side, shoulder, tip });
  }

  // feet — a surfer stance, one towards the nose, one towards the tail
  const feet = [];
  const footGeo = flattenXZ(plate(footShape(), 0.03, 14));
  for (const [x, z] of [[0.46, 0.10], [-0.50, -0.04]]) {
    const foot = mesh(footGeo, footMat);
    foot.position.set(x, 0.012, z);
    foot.rotation.y = x > 0 ? 0.1 : -0.12;
    rig.add(foot);
    feet.push(foot);
  }

  // scarf — the only thing that takes this sport seriously
  const scarf = mesh(scarfGeometry(), scarfMat);
  scarf.position.set(0.10, 1.40, 0.17);
  scarf.rotation.y = Math.PI / 2;
  rig.add(scarf);
  const scarfBase = scarf.geometry.attributes.position.array.slice();

  // ---------------- animation state --------------------------------------
  const state = {
    x: 0,
    z: 0,
    height: 0,
    yaw: 0,
    fwd: new THREE.Vector3(1, 0, 0),
    normal: new THREE.Vector3(0, 1, 0),
  };

  const tmpN = new THREE.Vector3();
  const tmpQ = new THREE.Quaternion();
  const upVec = new THREE.Vector3(0, 1, 0);
  let beakOpen = 0;
  let beakTarget = 0;
  let gull = 0;
  let burstT = 2.5;
  let burstAge = 99;
  let leanSmooth = 0;
  let bankSmooth = 0;
  let prevYaw = 0;
  let prevYawRate = 0;
  let tPrev = 0;

  const rider = {
    root,
    rig,
    boardGroup,
    state,
    headGroup,
    /** world position of the beak tip */
    mouthWorld(mouthWorldOut) {
      return mouth.getWorldPosition(mouthWorldOut);
    },
    setBeakOpen(v) {
      beakTarget = Math.max(0, Math.min(1, v));
    },
    swallow() {
      beakOpen = 1;
      gull = 1;
    },
    update(dt, t) {
      const dtc = Math.min(dt, 0.05);

      // ---- ride the water ------------------------------------------------
      const driftX = 0.55 * Math.sin(t * 0.11);
      const driftZ = 0.85 * Math.sin(t * 0.083 + 1.7);
      const yaw = 0.13 * Math.sin(t * 0.23);
      const h = waveHeight(driftX, driftZ, t);
      waveNormalAt(driftX, driftZ, t, tmpN);

      root.position.set(driftX, h + 0.03, driftZ);
      // align the plank with the water, then aim it down the line
      tmpQ.setFromUnitVectors(upVec, tmpN);
      const yawQ = new THREE.Quaternion().setFromAxisAngle(upVec, yaw);
      yawQ.multiply(tmpQ);
      root.quaternion.slerp(yawQ, 1 - Math.pow(0.0008, dtc));

      state.x = driftX;
      state.z = driftZ;
      state.height = h;
      state.yaw = yaw;
      state.normal.copy(tmpN);
      state.fwd.set(Math.cos(yaw), 0, -Math.sin(yaw)).applyQuaternion(root.quaternion);

      // ---- counter-rotate the bird so it stays upright -------------------
      const noseUp = Math.asin(THREE.MathUtils.clamp(state.fwd.y, -1, 1));
      const yawRate = (yaw - prevYaw) / Math.max(dtc, 1e-4);
      prevYaw = yaw;
      prevYawRate = THREE.MathUtils.lerp(prevYawRate, yawRate, 1 - Math.pow(0.02, dtc));
      const bank = THREE.MathUtils.clamp(prevYawRate * 0.9, -0.5, 0.5);
      const lean = -noseUp * 0.45;
      leanSmooth = THREE.MathUtils.lerp(leanSmooth, lean, 1 - Math.pow(0.02, dtc));
      bankSmooth = THREE.MathUtils.lerp(bankSmooth, bank, 1 - Math.pow(0.02, dtc));

      rig.rotation.z = leanSmooth - 0.06;
      rig.rotation.x = bankSmooth * 0.55;
      rig.rotation.y = THREE.MathUtils.lerp(
        rig.rotation.y,
        THREE.MathUtils.clamp(-prevYawRate * 0.35, -0.3, 0.3),
        1 - Math.pow(0.02, dtc),
      );
      rig.position.y = 0.105 + 0.022 * Math.sin(t * 2.7) + 0.05 * gull * Math.cos(t * 16);

      // ---- wings ---------------------------------------------------------
      burstT -= dt;
      if (burstT <= 0) {
        burstT = 5 + Math.random() * 5;
        burstAge = 0;
      }
      burstAge += dt;
      const b = Math.max(0, 1 - burstAge / 0.85);
      const burstEnv = b * b * (3 - 2 * b);
      const flap = 0.11 * Math.sin(t * 3.4) + burstEnv * 0.40 * Math.sin(t * 12.5);
      for (const wing of wings) {
        wing.shoulder.rotation.x = -0.22 * wing.side - flap * wing.side;
        wing.shoulder.rotation.y = -0.16 * wing.side;
        wing.tip.rotation.x = flap * 0.55 * wing.side;
      }

      // ---- head & beak ---------------------------------------------------
      const g = gull;
      gull *= Math.pow(0.02, dtc);
      headGroup.rotation.y = 0.30 * Math.sin(t * 0.45) - 0.06 * prevYawRate;
      headGroup.rotation.x = -0.05 + 0.10 * Math.sin(t * 0.63) - 0.28 * g;
      headGroup.rotation.z = 0.07 * Math.sin(t * 0.51) + prevYawRate * 0.2;

      beakOpen = THREE.MathUtils.lerp(beakOpen, beakTarget, 1 - Math.pow(0.001, dtc));
      lowerPivot.rotation.z = -0.16 - beakOpen * 0.75;
      pouch.scale.set(0.30 + beakOpen * 0.05, 0.15 - beakOpen * 0.04, 0.135 - beakOpen * 0.02);

      // ---- small life ----------------------------------------------------
      tailGroup.rotation.z = 0.12 * Math.sin(t * 1.35) + leanSmooth * 0.3;
      tailGroup.rotation.y = 0.07 * Math.sin(t * 0.9);
      tailGroup.rotation.x = -0.12 - 0.05 * Math.sin(t * 1.1);

      feet[0].position.x = 0.46 + 0.022 * Math.sin(t * 1.7);
      feet[1].position.x = -0.50 + 0.022 * Math.sin(t * 1.7 + 2.1);

      const sp = scarf.geometry.attributes.position;
      for (let i = 0; i < sp.count; i++) {
        const bx = scarfBase[i * 3];
        const by = scarfBase[i * 3 + 1];
        const s = 1 - (by + 0.30) / 0.60; // 0 at the knot, 1 at the tip
        sp.setXYZ(
          i,
          bx - 0.06 - 0.30 * s + Math.sin(s * 6.0 - t * 13.0 + bx * 4.0) * 0.055 * s,
          by + 0.02 * s + Math.sin(s * 4.0 - t * 9.0) * 0.025 * s,
          scarfBase[i * 3 + 2] + Math.sin(s * 7.0 - t * 11.0 + bx * 3.0) * 0.10 * s,
        );
      }
      sp.needsUpdate = true;
      scarf.geometry.computeVertexNormals();

      tPrev = t;
      return state;
    },
  };

  return rider;
}
