import * as THREE from 'three';

// Procedural surfing pelican standing on a surfboard, facing +X.
// createSurfer() returns { group, update(t) }; the caller samples the
// shared wave function so the rider sits on the animated ocean surface.

const MAT = {
  body: new THREE.MeshStandardMaterial({ color: 0xd9d2c4, roughness: 0.8 }),
  wing: new THREE.MeshStandardMaterial({ color: 0xc9c1b1, roughness: 0.85 }),
  wingTip: new THREE.MeshStandardMaterial({ color: 0x6f675c, roughness: 0.9 }),
  white: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 }),
  crown: new THREE.MeshStandardMaterial({ color: 0xf3c14f, roughness: 0.7 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xf29a3e, roughness: 0.55 }),
  nail: new THREE.MeshStandardMaterial({ color: 0xc96a24, roughness: 0.6 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xefa08b, roughness: 0.75 }),
  eye: new THREE.MeshStandardMaterial({ color: 0x14100c, roughness: 0.25 }),
  glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
  foot: new THREE.MeshStandardMaterial({ color: 0xe8823c, roughness: 0.7 }),
  board: new THREE.MeshStandardMaterial({ color: 0xff5a5f, roughness: 0.45 }),
  stripe: new THREE.MeshStandardMaterial({ color: 0xfff3df, roughness: 0.5 }),
};

function mesh(geo, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}

function buildBoard() {
  const board = new THREE.Group();

  const deckGeo = new THREE.CapsuleGeometry(0.42, 2.4, 6, 14);
  deckGeo.rotateZ(Math.PI / 2); // long axis along X
  const deck = mesh(deckGeo, MAT.board, 0, 0.16, 0);
  deck.scale.set(1, 0.32, 1);
  board.add(deck);

  board.add(mesh(new THREE.BoxGeometry(1.7, 0.03, 0.2), MAT.stripe, 0, 0.3, 0));

  const finGeo = new THREE.ConeGeometry(0.14, 0.4, 4);
  const fin = mesh(finGeo, MAT.stripe, -1.15, -0.05, 0);
  fin.rotation.x = Math.PI; // point down
  fin.scale.set(1, 1, 0.3);
  board.add(fin);

  board.rotation.z = 0.05; // nose slightly up
  board.position.y = 0.05;
  return board;
}

// side: +1 for the +Z wing, -1 for the -Z wing.
function buildWing(side) {
  const wing = new THREE.Group();
  wing.position.set(0.02, 1.02, side * 0.42);

  const inner = mesh(new THREE.SphereGeometry(0.5, 12, 8), MAT.wing, 0, 0, side * 0.45);
  inner.scale.set(0.62, 0.1, 1.05);
  wing.add(inner);

  const outer = new THREE.Group();
  outer.position.z = side * 0.9;
  const outerGeo = new THREE.ConeGeometry(0.3, 1.05, 7);
  const outerMesh = mesh(outerGeo, MAT.wing, 0, 0, side * 0.5);
  outerMesh.rotation.x = (side * Math.PI) / 2; // tip points outward
  outerMesh.scale.set(0.9, 1, 0.28); // flatten vertically
  outer.add(outerMesh);

  const tipGeo = new THREE.ConeGeometry(0.16, 0.5, 7);
  const tip = mesh(tipGeo, MAT.wingTip, 0, 0, side * 1.05);
  tip.rotation.x = (side * Math.PI) / 2;
  tip.scale.set(0.9, 1, 0.3);
  outer.add(tip);

  wing.add(outer);
  wing.rotation.y = -side * 0.18; // swept slightly back
  return { wing, outer };
}

function buildHead() {
  const head = new THREE.Group();
  head.position.set(0.62, 1.52, 0);

  head.add(mesh(new THREE.SphereGeometry(0.3, 18, 14), MAT.white));

  const crown = mesh(new THREE.SphereGeometry(0.2, 14, 10), MAT.crown, -0.07, 0.22, 0);
  crown.scale.set(1.05, 0.55, 0.95);
  head.add(crown);

  for (const side of [1, -1]) {
    head.add(mesh(new THREE.SphereGeometry(0.06, 10, 8), MAT.eye, 0.17, 0.07, side * 0.205));
    const glint = mesh(new THREE.SphereGeometry(0.02, 6, 6), MAT.glint, 0.205, 0.1, side * 0.235);
    glint.castShadow = false;
    head.add(glint);
  }

  // Long bill with a hanging pouch, pivoting at the face.
  const beak = new THREE.Group();
  beak.position.set(0.24, -0.03, 0);
  const upperGeo = new THREE.ConeGeometry(0.1, 1.3, 12);
  const upper = mesh(upperGeo, MAT.beak, 0.65, -0.02, 0);
  upper.rotation.z = -Math.PI / 2; // point forward (+X)
  beak.add(upper);

  const nailGeo = new THREE.ConeGeometry(0.045, 0.12, 8);
  const nail = mesh(nailGeo, MAT.nail, 1.3, -0.03, 0);
  nail.rotation.z = -Math.PI / 2 - 0.3; // small downward hook
  beak.add(nail);

  const pouch = mesh(new THREE.SphereGeometry(0.3, 14, 10), MAT.pouch, 0.62, -0.26, 0);
  pouch.scale.set(1.6, 0.85, 0.6);
  beak.add(pouch);

  beak.rotation.z = -0.1;
  head.add(beak);
  return { head, beak, pouch };
}

export function createSurfer() {
  const group = new THREE.Group();
  group.add(buildBoard());

  const pelican = new THREE.Group();
  pelican.position.y = 0.3; // standing on the deck
  group.add(pelican);

  // Feet planted in a surf stance, side by side.
  const footGeo = new THREE.SphereGeometry(0.16, 10, 8);
  for (const side of [1, -1]) {
    const foot = mesh(footGeo, MAT.foot, -0.05, 0.05, side * 0.2);
    foot.scale.set(1.6, 0.35, 1.0);
    pelican.add(foot);
    pelican.add(mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.35, 8), MAT.foot, -0.05, 0.22, side * 0.2));
  }

  const body = mesh(new THREE.SphereGeometry(0.62, 20, 16), MAT.body, 0, 0.78, 0);
  body.scale.set(1.15, 0.95, 0.85);
  body.rotation.z = -0.1;
  pelican.add(body);

  const tail = mesh(new THREE.ConeGeometry(0.2, 0.5, 7), MAT.wing, -0.68, 0.85, 0);
  tail.scale.set(1, 1, 1.6);
  tail.rotation.z = 1.25; // point back and slightly up
  pelican.add(tail);

  const neck = mesh(new THREE.CylinderGeometry(0.15, 0.21, 0.75, 12), MAT.white, 0.42, 1.15, 0);
  neck.rotation.z = -0.45;
  pelican.add(neck);

  const { head, beak, pouch } = buildHead();
  pelican.add(head);

  const right = buildWing(1);
  const left = buildWing(-1);
  pelican.add(right.wing);
  pelican.add(left.wing);

  function update(t, heightAt) {
    // Ride the actual wave surface: height from the crest, tilt from slope.
    const slopeX = (heightAt(0.9, 0, t) - heightAt(-0.9, 0, t)) / 1.8;
    const slopeZ = (heightAt(0, 0.9, t) - heightAt(0, -0.9, t)) / 1.8;
    const pitch = Math.atan(slopeX) * 0.8 + Math.sin(t * 0.7) * 0.02;
    const roll = -Math.atan(slopeZ) * 0.8 + Math.sin(t * 0.23 + 0.7) * 0.06;
    group.rotation.set(roll, Math.sin(t * 0.21) * 0.12, pitch);
    group.position.y = heightAt(0, 0, t) - 0.02 + Math.sin(t * 1.7) * 0.04;

    // Crouched body leans into the carve, head scans the wave.
    pelican.rotation.x = Math.sin(t * 0.21 - 0.7) * 0.1;
    pelican.rotation.z = -0.02 + Math.sin(t * 0.9) * 0.02;
    head.rotation.y = Math.sin(t * 0.45) * 0.38;
    head.rotation.x = Math.sin(t * 0.8) * 0.06;

    // Bill bobs, pouch jiggles.
    beak.rotation.z = -0.1 + Math.sin(t * 2.1) * 0.035;
    pouch.scale.y = 0.85 * (1 + Math.sin(t * 3.0) * 0.07);
    pouch.position.y = -0.26 + Math.sin(t * 2.1 - 0.4) * 0.02;

    // Wings held out for balance, adjusting against the roll.
    const common = 0.2 + Math.sin(t * 1.35) * 0.07;
    const diff =
      THREE.MathUtils.clamp(-roll * 1.6, -0.3, 0.3) + Math.sin(t * 0.9 + 1.0) * 0.06;
    right.wing.rotation.x = -(common + diff);
    left.wing.rotation.x = common - diff;
    const lag = 0.1 + Math.sin(t * 1.35 - 0.6) * 0.09;
    right.outer.rotation.x = -lag;
    left.outer.rotation.x = lag;

    tail.rotation.y = Math.sin(t * 2.0) * 0.12;
  }

  return { group, update };
}
