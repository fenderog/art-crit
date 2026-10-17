import * as THREE from 'three';

const UP = new THREE.Vector3(0, 1, 0);
const STANCE = 0.95; // sideways surf stance (radians)

// Oriented cylinder between two points.
function makeLimb(a, b, radius, material) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(radius * 0.75, radius, len, 7);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(a).addScaledVector(dir, 0.5);
  mesh.quaternion.setFromUnitVectors(UP, dir.normalize());
  return mesh;
}

// Wing plan outline (span outward in x, leading edge at +y -> +Z after rotation).
function wingShape(mirror) {
  const m = mirror ? -1 : 1;
  const s = new THREE.Shape();
  s.moveTo(0, 0.2);
  s.quadraticCurveTo(0.35 * m, 0.3, 0.62 * m, 0.14);
  s.quadraticCurveTo(0.75 * m, 0.02, 0.8 * m, -0.15);
  s.quadraticCurveTo(0.55 * m, -0.32, 0.28 * m, -0.3);
  s.quadraticCurveTo(0.1 * m, -0.34, 0, -0.24);
  s.closePath();
  return s;
}

export function createPelican() {
  const group = new THREE.Group(); // origin at deck level

  const bodyMat = new THREE.MeshStandardMaterial({ color: '#f6f1e3', flatShading: true, roughness: 0.85 });
  const wingMat = new THREE.MeshStandardMaterial({ color: '#b6c0cb', flatShading: true, roughness: 0.8 });
  const darkMat = new THREE.MeshStandardMaterial({ color: '#39424f', flatShading: true, roughness: 0.75 });
  const beakMat = new THREE.MeshStandardMaterial({ color: '#f0a132', flatShading: true, roughness: 0.55 });
  const pouchMat = new THREE.MeshStandardMaterial({ color: '#f7bd63', flatShading: true, roughness: 0.6 });
  const legMat = new THREE.MeshStandardMaterial({ color: '#e59a40', flatShading: true, roughness: 0.7 });
  const eyeMat = new THREE.MeshStandardMaterial({ color: '#1d222b', roughness: 0.25 });
  const glintMat = new THREE.MeshBasicMaterial({ color: '#ffffff' });

  // ---- feet planted on the deck (surf stance, toes toward the body's facing) ----
  const feet = [
    { x: 0.1, z: -0.48, rot: 1.25 }, // back foot
    { x: -0.12, z: 0.34, rot: 0.95 }, // front foot
  ];
  for (const f of feet) {
    const foot = new THREE.Group();
    const sole = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.045, 0.22), legMat);
    foot.add(sole);
    for (let i = -1; i <= 1; i++) {
      const toe = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.03, 0.15), legMat);
      toe.position.set(i * 0.05, -0.004, 0.145);
      toe.rotation.y = i * 0.3;
      foot.add(toe);
    }
    foot.position.set(f.x, 0.026, f.z);
    foot.rotation.y = f.rot;
    group.add(foot);
  }

  // ---- torso ----
  const bodyGroup = new THREE.Group();
  bodyGroup.position.set(0, 0.82, -0.05);
  bodyGroup.rotation.y = STANCE;
  group.add(bodyGroup);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 18, 12), bodyMat);
  body.scale.set(0.95, 0.82, 1.3);
  bodyGroup.add(body);

  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.3, 14, 10), bodyMat);
  chest.position.set(0, -0.03, 0.3);
  chest.scale.set(0.92, 0.86, 1.05);
  bodyGroup.add(chest);

  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.5, 6), wingMat);
  tail.position.set(0, 0.1, -0.58);
  tail.rotation.x = -Math.PI / 2 + 0.55; // points back and up
  bodyGroup.add(tail);

  // ---- legs (static; thighs hidden inside the body) ----
  for (const [hipX, foot] of [
    [0.11, feet[0]],
    [-0.11, feet[1]],
  ]) {
    const hip = new THREE.Vector3(hipX, 0, -0.06)
      .applyAxisAngle(UP, STANCE)
      .add(new THREE.Vector3(0, 0, -0.05));
    hip.y = 0.56;
    group.add(makeLimb(new THREE.Vector3(foot.x, 0.05, foot.z), hip, 0.048, legMat));
  }

  // ---- neck & head ----
  const neckGroup = new THREE.Group();
  neckGroup.position.set(0, 0.28, 0.34);
  bodyGroup.add(neckGroup);

  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.02, 0.02),
    new THREE.Vector3(0, 0.17, 0.1),
    new THREE.Vector3(0, 0.34, 0.12),
    new THREE.Vector3(0, 0.47, 0.1),
  ]);
  neckGroup.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 12, 0.115, 8), bodyMat));

  const headGroup = new THREE.Group();
  headGroup.position.set(0, 0.5, 0.1);
  headGroup.rotation.y = -STANCE + 0.15; // look down the line of travel
  neckGroup.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.165, 14, 10), bodyMat);
  head.scale.set(0.95, 0.9, 1.05);
  headGroup.add(head);

  const tuft = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.15, 5), wingMat);
  tuft.position.set(0, 0.15, -0.05);
  tuft.rotation.x = -0.55;
  headGroup.add(tuft);

  for (const s of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.032, 8, 6), eyeMat);
    eye.position.set(s * 0.105, 0.045, 0.112);
    headGroup.add(eye);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.011, 6, 4), glintMat);
    glint.position.set(s * 0.115, 0.062, 0.132);
    headGroup.add(glint);
  }

  // ---- beak with pouch ----
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, -0.005, 0.1);
  headGroup.add(beakGroup);

  const upper = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.62, 5), beakMat);
  upper.scale.set(1.5, 1, 0.45); // scale, then rotate: flat wide blade
  upper.rotation.x = Math.PI / 2;
  upper.position.set(0, 0.02, 0.3);
  beakGroup.add(upper);

  const pouchGroup = new THREE.Group();
  pouchGroup.position.set(0, -0.02, 0.02);
  beakGroup.add(pouchGroup);

  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), pouchMat);
  pouch.scale.set(1.15, 1.05, 3.4);
  pouch.position.set(0, -0.05, 0.3);
  pouchGroup.add(pouch);

  // ---- wings ----
  function buildWing(mirror) {
    const pivot = new THREE.Group(); // shoulder: sweep + slight incidence
    pivot.position.set((mirror ? -1 : 1) * 0.3, 0.16, -0.02);
    pivot.rotation.y = (mirror ? -1 : 1) * 0.16;
    pivot.rotation.x = 0.05;

    const flap = new THREE.Group(); // animated flapping axis
    pivot.add(flap);

    const geo = new THREE.ExtrudeGeometry(wingShape(mirror), {
      depth: 0.055,
      steps: 1,
      bevelEnabled: true,
      bevelThickness: 0.015,
      bevelSize: 0.02,
      bevelSegments: 1,
    });
    const mesh = new THREE.Mesh(geo, wingMat);
    mesh.rotation.x = Math.PI / 2; // +y leading edge -> +Z forward
    flap.add(mesh);

    // dark primary feathers at the trailing tip
    for (let i = 0; i < 3; i++) {
      const sgn = mirror ? -1 : 1;
      const feather = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.02, 0.08), darkMat);
      feather.position.set(sgn * (0.5 + i * 0.09), -0.005, -0.13 - i * 0.05);
      feather.rotation.y = sgn * -0.4;
      flap.add(feather);
    }
    bodyGroup.add(pivot);
    return flap;
  }

  const wingR = buildWing(false);
  const wingL = buildWing(true);

  // ---- animation ----
  function update(t, dt, state) {
    const { roll, pitch } = state;
    const crouch = Math.min(0.16, Math.abs(roll) * 0.35);

    bodyGroup.position.y = 0.82 + Math.sin(t * 2.1) * 0.045 - crouch;
    bodyGroup.rotation.z = roll * 1.15 + Math.sin(t * 1.4) * 0.02; // lean into carves
    bodyGroup.rotation.x = 0.09 + pitch * 0.6 + Math.sin(t * 2.6) * 0.03;

    // wings: mostly gliding, with occasional flapping bursts
    const burst = Math.pow(Math.max(0, Math.sin(t * 0.5 + 1.3)), 2);
    const flap = 0.16 + Math.sin(t * 2.7) * 0.06 + burst * (0.45 + 0.3 * Math.sin(t * 6.2));
    wingR.rotation.z = flap + Math.max(0, -roll) * 0.4;
    wingL.rotation.z = -(flap + Math.max(0, roll) * 0.4);

    tail.rotation.z = Math.sin(t * 2.3) * 0.12;
    tail.rotation.x = -Math.PI / 2 + 0.55 + Math.sin(t * 1.8) * 0.05;

    headGroup.rotation.x = Math.sin(t * 1.6) * 0.07 + pitch * 0.3;
    headGroup.rotation.z = Math.sin(t * 0.9) * 0.05 + roll * 0.35;

    // periodic pouch gulp
    const gulp = Math.pow(Math.max(0, Math.sin(t * 0.7)), 4);
    pouchGroup.rotation.x = gulp * 0.5;
    upper.rotation.x = Math.PI / 2 - gulp * 0.1;
    pouch.scale.set(1.15, 1.05 + gulp * 0.3, 3.4);
  }

  return { group, update };
}
