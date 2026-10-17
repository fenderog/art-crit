import * as THREE from "three";

const WHITE = 0xf6f5f0;
const GREY = 0xa3adb6;
const BILL = 0xf2b233;
const POUCH = 0xe8922e;
const FEET = 0xef7a2a;
const INK = 0x1d1d1d;

// Pelican space: +x is forward (the way the board points), +y is up, +z is the pelican's left side.
// Origin sits on the deck, between the feet.

function place(geometry, material, { pos = [0, 0, 0], rot = [0, 0, 0], scale = [1, 1, 1] } = {}) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...pos);
  mesh.rotation.set(...rot);
  mesh.scale.set(...scale);
  return mesh;
}

// A long, feathered wing lying in the x-z plane with its root at the origin and its span along +z.
function createWingGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0.2);
  shape.lineTo(0.85, 0.16);
  shape.quadraticCurveTo(1.05, 0.12, 1.12, -0.04);
  shape.lineTo(0.98, -0.1);
  shape.lineTo(0.9, -0.2);
  shape.lineTo(0.7, -0.14);
  shape.lineTo(0.5, -0.2);
  shape.lineTo(0, -0.2);
  shape.closePath();

  const geometry = new THREE.ExtrudeGeometry(shape, { depth: 0.03, bevelEnabled: false });
  geometry.translate(0, 0, -0.015);
  // Shape (span, chord, thickness) -> wing space (chord along x, thickness along y, span along z).
  geometry.applyMatrix4(new THREE.Matrix4().set(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1));
  return geometry;
}

export function createPelican() {
  const group = new THREE.Group();

  const white = new THREE.MeshStandardMaterial({ color: WHITE, roughness: 0.6 });
  const grey = new THREE.MeshStandardMaterial({ color: GREY, roughness: 0.7 });
  const bill = new THREE.MeshStandardMaterial({ color: BILL, roughness: 0.4 });
  const pouch = new THREE.MeshStandardMaterial({ color: POUCH, roughness: 0.5 });
  const feet = new THREE.MeshStandardMaterial({ color: FEET, roughness: 0.5 });
  const ink = new THREE.MeshStandardMaterial({ color: INK, roughness: 0.3 });

  // Torso, tilted so the chest rises toward the neck.
  group.add(
    place(new THREE.SphereGeometry(1, 40, 28), white, {
      pos: [-0.02, 0.46, 0],
      rot: [0, 0, 0.08],
      scale: [0.55, 0.28, 0.3],
    }),
  );

  // Short tail feathers, angled up.
  group.add(
    place(new THREE.SphereGeometry(1, 16, 10), grey, {
      pos: [-0.62, 0.5, 0],
      rot: [0, 0, -0.3],
      scale: [0.28, 0.05, 0.2],
    }),
  );

  // Legs and webbed feet, planted on the deck.
  for (const z of [-0.1, 0.1]) {
    group.add(
      place(new THREE.CylinderGeometry(0.022, 0.022, 0.2, 10), feet, { pos: [0.02, 0.12, z] }),
      place(new THREE.SphereGeometry(1, 16, 8), feet, {
        pos: [0.07, 0.018, z],
        scale: [0.14, 0.018, 0.1],
      }),
    );
  }

  // S-shaped neck rising from the chest into the head.
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.36, 0.5, 0),
    new THREE.Vector3(0.5, 0.75, 0),
    new THREE.Vector3(0.42, 0.98, 0),
    new THREE.Vector3(0.56, 1.12, 0),
    new THREE.Vector3(0.74, 1.17, 0),
  ]);
  group.add(place(new THREE.TubeGeometry(neckCurve, 48, 0.09, 16, false), white));

  const head = new THREE.Vector3(0.74, 1.17, 0);
  group.add(place(new THREE.SphereGeometry(0.13, 28, 20), white, { pos: head.toArray() }));

  // Long bill angled forward and slightly down, with the pouch hanging beneath it.
  const billAngle = -0.22;
  const billDir = new THREE.Vector3(Math.cos(billAngle), Math.sin(billAngle), 0);
  const billLength = 0.55;
  const billBase = head.clone().add(new THREE.Vector3(0.06, 0.0, 0));
  const billCenter = billBase.clone().addScaledVector(billDir, billLength / 2);
  group.add(
    place(new THREE.CylinderGeometry(0.035, 0.07, billLength, 16), bill, {
      pos: billCenter.toArray(),
      rot: [0, 0, billAngle - Math.PI / 2],
    }),
    place(new THREE.SphereGeometry(1, 24, 16), pouch, {
      pos: [billCenter.x - 0.02, billCenter.y - 0.12, 0],
      scale: [0.2, 0.12, 0.1],
    }),
  );

  for (const z of [-0.125, 0.125]) {
    group.add(place(new THREE.SphereGeometry(0.028, 12, 8), ink, { pos: [0.79, 1.2, z] }));
  }

  // Wings hinge at the shoulders so they can be lifted out for balance.
  const wingGeometry = createWingGeometry();
  const wings = [];
  for (const sign of [1, -1]) {
    const pivot = new THREE.Group();
    pivot.position.set(-0.1, 0.56, 0.2 * sign);
    const wing = place(wingGeometry, grey, { scale: [1, 1, sign] });
    pivot.add(wing);
    group.add(pivot);
    wings.push({ pivot, sign });
  }

  function update(t) {
    // Wings held up and out, flapping for balance; raised high enough to read in profile.
    const lift = 0.95 + 0.3 * Math.sin(t * 3.2);
    for (const { pivot, sign } of wings) {
      pivot.rotation.x = -sign * lift;
      pivot.rotation.y = -sign * 0.15;
    }
    group.rotation.z = 0.04 * Math.sin(t * 1.7);
    group.rotation.x = 0.03 * Math.sin(t * 1.1);
  }

  return { group, update };
}
