import * as THREE from 'three';

function standard(color, extra = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: 0.75,
    metalness: 0.0,
    ...extra,
  });
}

function roundedFeatherShape() {
  const s = new THREE.Shape();
  s.moveTo(0, -0.35);
  s.bezierCurveTo(0.55, 0.0, 0.5, 1.4, 0.15, 2.3);
  s.bezierCurveTo(0.05, 2.55, -0.15, 2.55, -0.3, 2.35);
  s.bezierCurveTo(-0.7, 1.4, -0.75, 0.4, -0.45, -0.25);
  s.quadraticCurveTo(-0.25, -0.45, 0, -0.35);
  return s;
}

function boardShape() {
  const s = new THREE.Shape();
  s.moveTo(-2.05, 0);
  s.bezierCurveTo(-1.8, 0.5, -0.9, 0.62, 0.1, 0.6);
  s.bezierCurveTo(1.0, 0.58, 1.8, 0.4, 2.1, 0);
  s.bezierCurveTo(1.8, -0.4, 1.0, -0.58, 0.1, -0.6);
  s.bezierCurveTo(-0.9, -0.62, -1.8, -0.5, -2.05, 0);
  return s;
}

export function createPelican() {
  const group = new THREE.Group();

  const white = standard(0xf6f2e8, { roughness: 0.85 });
  const beakMat = standard(0xffa22e, { roughness: 0.4 });
  const pouchMat = standard(0xf27a1d, { roughness: 0.5 });
  const legMat = standard(0xf59a2b, { roughness: 0.5 });
  const eyeMat = standard(0x141414, { roughness: 0.25 });
  const boardMat = standard(0xff5a4d, { roughness: 0.3 });
  const stripeMat = standard(0xfff0c4, { roughness: 0.3 });
  const finMat = standard(0xffd24d, { roughness: 0.4 });

  /* ---------------------------------------------------------------- board */
  const boardGeo = new THREE.ExtrudeGeometry(boardShape(), {
    depth: 0.12,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.04,
    bevelSegments: 3,
    steps: 1,
    curveSegments: 24,
  });
  boardGeo.rotateX(-Math.PI / 2);
  boardGeo.translate(0, -0.15, 0);
  const board = new THREE.Mesh(boardGeo, boardMat);
  board.castShadow = true;
  group.add(board);

  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(3.4, 0.02, 0.2),
    stripeMat
  );
  stripe.position.set(0, -0.01, 0);
  group.add(stripe);

  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.bezierCurveTo(-0.35, -0.15, -0.45, -0.4, -0.2, -0.62);
  finShape.lineTo(0, -0.55);
  finShape.lineTo(0, 0);
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.04,
    bevelEnabled: true,
    bevelThickness: 0.01,
    bevelSize: 0.01,
    bevelSegments: 1,
    steps: 1,
  });
  finGeo.translate(0, 0, -0.02);
  const fin = new THREE.Mesh(finGeo, finMat);
  fin.position.set(-1.55, 0.0, 0);
  group.add(fin);

  /* ----------------------------------------------------------------- legs */
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.07, 0.08, 0.5, 10),
      legMat
    );
    leg.position.set(0.12, 0.25, side * 0.24);
    leg.rotation.z = -0.12;
    group.add(leg);

    const foot = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), legMat);
    foot.scale.set(0.3, 0.06, 0.2);
    foot.position.set(0.24, 0.02, side * 0.24);
    group.add(foot);
  }

  /* ----------------------------------------------------------------- body */
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), white);
  body.scale.set(1.15, 0.92, 0.82);
  body.position.set(-0.05, 1.2, 0);
  group.add(body);

  // Tail feathers
  const tail = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), white);
  tail.scale.set(0.42, 0.14, 0.5);
  tail.position.set(-1.12, 1.12, 0);
  tail.rotation.z = 0.18;
  group.add(tail);
  for (let i = -2; i <= 2; i++) {
    const feather = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.06, 0.6, 6),
      white
    );
    feather.position.set(-1.3, 1.1, i * 0.12);
    feather.rotation.z = Math.PI / 2 + 0.25;
    feather.rotation.x = i * 0.14;
    group.add(feather);
  }

  /* ----------------------------------------------------------------- neck */
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.3, 1.55, 0),
    new THREE.Vector3(0.7, 1.95, 0),
    new THREE.Vector3(0.92, 2.3, 0),
    new THREE.Vector3(0.9, 2.6, 0),
  ]);
  const neck = new THREE.Mesh(
    new THREE.TubeGeometry(neckCurve, 28, 0.26, 16, false),
    white
  );
  group.add(neck);

  /* ------------------------------------------------------------------ head */
  const headGroup = new THREE.Group();
  headGroup.position.set(0.9, 2.6, 0);
  group.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.36, 32, 24), white);
  head.scale.set(1.0, 0.95, 0.92);
  head.position.set(0.0, 0.05, 0);
  headGroup.add(head);

  // Bevelled crest at the back of the head
  const crest = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), white);
  crest.scale.set(0.8, 0.7, 0.7);
  crest.position.set(-0.26, 0.2, 0);
  headGroup.add(crest);

  // Upper mandible
  const upperGeo = new THREE.ConeGeometry(0.17, 2.05, 14);
  upperGeo.rotateZ(-Math.PI / 2);
  upperGeo.scale(1, 1.05, 0.55);
  const upper = new THREE.Mesh(upperGeo, beakMat);
  upper.position.set(0.95, -0.02, 0);
  upper.rotation.z = -0.09;
  headGroup.add(upper);

  // Pouch
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), pouchMat);
  const pouchBaseX = 0.92;
  const pouchBaseY = 0.4;
  const pouchBaseZ = 0.36;
  pouch.scale.set(pouchBaseX, pouchBaseY, pouchBaseZ);
  pouch.position.set(0.9, -0.36, 0);
  headGroup.add(pouch);

  // Eyes
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.065, 16, 12), eyeMat);
    eye.position.set(0.2, 0.12, side * 0.24);
    headGroup.add(eye);

    const ring = new THREE.Mesh(
      new THREE.SphereGeometry(0.1, 16, 12),
      standard(0xffe08a, { roughness: 0.4 })
    );
    ring.scale.set(0.35, 1.0, 1.0);
    ring.position.set(0.19, 0.12, side * 0.245);
    headGroup.add(ring);

    const glint = new THREE.Mesh(
      new THREE.SphereGeometry(0.022, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    glint.position.set(0.24, 0.15, side * 0.28);
    headGroup.add(glint);
  }

  /* ----------------------------------------------------------------- wings */
  const wingShape = roundedFeatherShape();
  const wingGeo = new THREE.ExtrudeGeometry(wingShape, {
    depth: 0.06,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 2,
    steps: 1,
    curveSegments: 16,
  });
  wingGeo.rotateX(Math.PI / 2); // span (shape +Y) now points +Z, thickness -Y

  const wingGeoLeft = wingGeo.clone();
  wingGeoLeft.scale(1, 1, -1);
  wingGeoLeft.computeVertexNormals();

  const wingMat = standard(0xf1ece0, {
    roughness: 0.85,
    side: THREE.DoubleSide,
  });

  const rightPivot = new THREE.Group();
  rightPivot.position.set(0.0, 1.5, 0.62);
  const rightWing = new THREE.Mesh(wingGeo, wingMat);
  rightPivot.add(rightWing);
  group.add(rightPivot);

  const leftPivot = new THREE.Group();
  leftPivot.position.set(0.0, 1.5, -0.62);
  const leftWing = new THREE.Mesh(wingGeoLeft, wingMat);
  leftPivot.add(leftWing);
  group.add(leftPivot);

  /* --------------------------------------------------------------- animate */
  let elapsed = 0;

  function update(t) {
    elapsed = t;

    const flap = 0.14 + 0.52 * Math.sin(t * 4.1);
    rightPivot.rotation.x = -flap;
    leftPivot.rotation.x = flap;
    rightPivot.rotation.y = 0.06 * Math.sin(t * 4.1 + 0.4);
    leftPivot.rotation.y = -0.06 * Math.sin(t * 4.1 + 0.4);

    // Gentle body bob and head sway
    body.position.y = 1.2 + 0.035 * Math.sin(t * 4.1 + 1.1);
    body.rotation.z = 0.02 * Math.sin(t * 2.2);
    neck.rotation.z = 0.02 * Math.sin(t * 2.2 + 0.5);

    headGroup.position.y = 2.6 + 0.04 * Math.sin(t * 2.0);
    headGroup.rotation.z = 0.05 * Math.sin(t * 2.0 + 0.7);

    // Pouch breathes / wobbles
    const wobble = Math.sin(t * 3.3);
    pouch.scale.set(
      pouchBaseX * (1 + 0.05 * wobble),
      pouchBaseY * (1 + 0.15 * wobble),
      pouchBaseZ * (1 + 0.08 * wobble)
    );
    pouch.position.y = -0.36 - 0.03 * wobble;
  }

  update(0);

  return { group, update, get elapsed() { return elapsed; } };
}
