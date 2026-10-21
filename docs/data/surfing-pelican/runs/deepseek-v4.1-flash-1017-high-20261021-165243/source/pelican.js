import * as THREE from "three";

const white = new THREE.MeshStandardMaterial({
  color: "#f8f3e6",
  roughness: 0.62,
  metalness: 0.02,
});
const cream = new THREE.MeshStandardMaterial({
  color: "#efe4cf",
  roughness: 0.7,
});
const grey = new THREE.MeshStandardMaterial({
  color: "#cfd0c8",
  roughness: 0.7,
});
const orange = new THREE.MeshStandardMaterial({
  color: "#f5a13c",
  roughness: 0.46,
});
const pouchMat = new THREE.MeshStandardMaterial({
  color: "#ea8434",
  roughness: 0.5,
});
const dark = new THREE.MeshStandardMaterial({
  color: "#241f1b",
  roughness: 0.35,
});
const gold = new THREE.MeshStandardMaterial({
  color: "#e0ac52",
  roughness: 0.22,
  metalness: 0.85,
});
const lens = new THREE.MeshStandardMaterial({
  color: "#12252c",
  roughness: 0.08,
  metalness: 0.65,
});
const boardMat = new THREE.MeshStandardMaterial({
  color: "#ff6d4a",
  roughness: 0.38,
  metalness: 0.05,
});
const stripeMat = new THREE.MeshStandardMaterial({
  color: "#fff0cf",
  roughness: 0.42,
});
const tealMat = new THREE.MeshStandardMaterial({
  color: "#0f7c82",
  roughness: 0.35,
});

function roundedRectShape(halfW, halfH, r) {
  const s = new THREE.Shape();
  s.moveTo(-halfW + r, -halfH);
  s.lineTo(halfW - r, -halfH);
  s.quadraticCurveTo(halfW, -halfH, halfW, -halfH + r);
  s.lineTo(halfW, halfH - r);
  s.quadraticCurveTo(halfW, halfH, halfW - r, halfH);
  s.lineTo(-halfW + r, halfH);
  s.quadraticCurveTo(-halfW, halfH, -halfW, halfH - r);
  s.lineTo(-halfW, -halfH + r);
  s.quadraticCurveTo(-halfW, -halfH, -halfW + r, -halfH);
  return s;
}

function cylinderBetween(a, b, radius, material, radialSegments = 12) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(radius, radius * 1.05, len, radialSegments);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.copy(a).addScaledVector(dir, 0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  return mesh;
}

function makeWingShape() {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.quadraticCurveTo(0.34, -0.07, 0.68, -0.03);
  s.quadraticCurveTo(0.9, 0.01, 1.04, 0.13);
  s.lineTo(0.95, 0.21);
  s.quadraticCurveTo(0.86, 0.13, 0.79, 0.38);
  s.quadraticCurveTo(0.69, 0.2, 0.57, 0.45);
  s.quadraticCurveTo(0.46, 0.25, 0.31, 0.4);
  s.quadraticCurveTo(0.18, 0.2, 0.04, 0.17);
  s.lineTo(0, 0);
  return s;
}

function createWing(side) {
  // side: +1 = camera side, -1 = far side
  const outer = new THREE.Group();
  outer.position.set(0.08, 1.9, 0.48 * side);

  const span = new THREE.Vector3(0.28, 0.5, 0.92 * side).normalize();
  const chord = new THREE.Vector3(-1, -0.16, 0.04 * side).normalize();
  const normal = new THREE.Vector3().crossVectors(span, chord).normalize();
  const basis = new THREE.Matrix4().makeBasis(span, chord, normal);
  outer.quaternion.setFromRotationMatrix(basis);

  const inner = new THREE.Group();
  outer.add(inner);

  const shape = makeWingShape();
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.055,
    bevelEnabled: true,
    bevelThickness: 0.018,
    bevelSize: 0.018,
    bevelSegments: 2,
    curveSegments: 16,
  });
  geo.translate(0, 0, -0.027);

  const mesh = new THREE.Mesh(geo, white);
  mesh.material = white.clone();
  mesh.material.side = THREE.DoubleSide;
  mesh.scale.set(1.32, 1.24, 1);
  inner.add(mesh);

  // A smaller grey-blue layer suggests the primary feathers underneath.
  const under = new THREE.Mesh(geo.clone(), grey.clone());
  under.material.side = THREE.DoubleSide;
  under.material.color.set("#cfdad7");
  under.scale.set(0.8, 0.78, 1);
  under.position.set(0.16, 0.05, -0.05 * side);
  under.material.transparent = true;
  under.material.opacity = 0.45;
  inner.add(under);

  return { outer, inner };
}

export function createSurfer() {
  const group = new THREE.Group();

  // ---------- surfboard ----------
  const boardShape = new THREE.Shape();
  boardShape.moveTo(-2.15, -0.6);
  boardShape.quadraticCurveTo(-2.38, 0, -2.15, 0.6);
  boardShape.quadraticCurveTo(-0.5, 0.82, 1.15, 0.72);
  boardShape.quadraticCurveTo(1.98, 0.56, 2.5, 0);
  boardShape.quadraticCurveTo(1.98, -0.56, 1.15, -0.72);
  boardShape.quadraticCurveTo(-0.5, -0.82, -2.15, -0.6);

  const boardGeo = new THREE.ExtrudeGeometry(boardShape, {
    depth: 0.12,
    bevelEnabled: true,
    bevelThickness: 0.035,
    bevelSize: 0.035,
    bevelSegments: 4,
    curveSegments: 28,
  });
  boardGeo.rotateX(-Math.PI / 2);
  const board = new THREE.Mesh(boardGeo, boardMat);
  board.position.y = -0.075;
  group.add(board);

  const stripeShape = new THREE.Shape();
  stripeShape.moveTo(-1.82, -0.14);
  stripeShape.quadraticCurveTo(-1.98, 0, -1.82, 0.14);
  stripeShape.quadraticCurveTo(-0.2, 0.26, 1.35, 0.24);
  stripeShape.quadraticCurveTo(1.86, 0.2, 2.16, 0);
  stripeShape.quadraticCurveTo(1.86, -0.2, 1.35, -0.24);
  stripeShape.quadraticCurveTo(-0.2, -0.26, -1.82, -0.14);
  const stripeGeo = new THREE.ExtrudeGeometry(stripeShape, {
    depth: 0.008,
    bevelEnabled: false,
    curveSegments: 24,
  });
  stripeGeo.rotateX(-Math.PI / 2);
  const stripe = new THREE.Mesh(stripeGeo, stripeMat);
  stripe.position.y = 0.073;
  group.add(stripe);

  const centerLine = new THREE.Mesh(new THREE.BoxGeometry(3.25, 0.006, 0.042), tealMat);
  centerLine.position.set(-0.04, 0.083, 0);
  group.add(centerLine);

  // thin teal pin-lines either side of the cream stripe
  for (const z of [-0.27, 0.27]) {
    const pin = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.006, 0.025), tealMat);
    pin.position.set(-0.1, 0.079, z);
    pin.scale.x = 0.95;
    group.add(pin);
  }

  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(-0.58, 0);
  finShape.quadraticCurveTo(-0.62, -0.42, -0.42, -0.62);
  finShape.lineTo(-0.26, -0.3);
  finShape.lineTo(0, 0);
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.045,
    bevelEnabled: true,
    bevelThickness: 0.01,
    bevelSize: 0.01,
    bevelSegments: 2,
  });
  const fin = new THREE.Mesh(finGeo, tealMat);
  fin.position.set(-1.45, -0.05, -0.022);
  group.add(fin);

  // soft contact shadow on the deck
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(1, 32),
    new THREE.MeshBasicMaterial({
      color: "#7d3a25",
      transparent: true,
      opacity: 0.22,
      depthWrite: false,
    })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.scale.set(1.05, 0.58, 1);
  shadow.position.set(0.02, 0.084, 0);
  group.add(shadow);

  // ---------- pelican ----------
  const pelican = new THREE.Group();
  pelican.position.y = 0.08;
  group.add(pelican);

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), white);
  body.scale.set(1.02, 0.69, 0.62);
  body.position.set(0.05, 1.58, 0);
  body.rotation.z = -0.08;
  pelican.add(body);

  const chest = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), white);
  chest.scale.set(0.54, 0.55, 0.5);
  chest.position.set(0.52, 1.52, 0);
  pelican.add(chest);

  const rump = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 22), cream);
  rump.scale.set(0.56, 0.48, 0.5);
  rump.position.set(-0.66, 1.6, 0);
  pelican.add(rump);

  // neck
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.4, 1.9, 0),
    new THREE.Vector3(0.66, 2.14, 0),
    new THREE.Vector3(0.68, 2.42, 0),
    new THREE.Vector3(0.9, 2.65, 0),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 24, 0.185, 12, false), white);
  pelican.add(neck);

  const headGroup = new THREE.Group();
  pelican.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.36, 36, 26), white);
  head.scale.set(1.02, 0.96, 0.9);
  head.position.set(1.02, 2.76, 0);
  headGroup.add(head);

  // upper mandible
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.205, 1.36, 18), orange);
  beak.geometry.rotateZ(-Math.PI / 2);
  beak.scale.set(1, 0.7, 0.95);
  beak.position.set(2.0, 2.72, 0);
  beak.rotation.z = -0.055;
  headGroup.add(beak);

  const beakTip = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), pouchMat);
  beakTip.scale.set(1.4, 0.8, 0.9);
  beakTip.position.set(2.66, 2.69, 0);
  headGroup.add(beakTip);

  // characteristic throat pouch
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 30, 20), pouchMat);
  pouch.scale.set(0.56, 0.24, 0.24);
  pouch.position.set(1.8, 2.55, 0);
  pouch.rotation.z = 0.06;
  headGroup.add(pouch);

  const pouchRidge = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), orange);
  pouchRidge.scale.set(0.44, 0.075, 0.19);
  pouchRidge.position.set(1.82, 2.67, 0);
  headGroup.add(pouchRidge);

  // aviator shades
  for (const side of [-1, 1]) {
    const lensMesh = new THREE.Mesh(new THREE.CircleGeometry(0.175, 28), lens);
    lensMesh.scale.y = 0.82;
    lensMesh.position.set(1.23, 2.87, 0.305 * side);
    if (side === -1) lensMesh.rotation.y = Math.PI;
    headGroup.add(lensMesh);

    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.175, 0.018, 8, 28), gold);
    rim.scale.y = 0.82;
    rim.position.copy(lensMesh.position);
    rim.position.z += 0.008 * side;
    if (side === -1) rim.rotation.y = Math.PI;
    headGroup.add(rim);

    const arm = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.02, 0.022), gold);
    arm.position.set(1.06, 2.925, 0.315 * side);
    arm.rotation.y = 0.14 * side;
    headGroup.add(arm);

    const glint = new THREE.Mesh(
      new THREE.CircleGeometry(0.045, 16),
      new THREE.MeshBasicMaterial({ color: "#fff7dc", transparent: true, opacity: 0.75 })
    );
    glint.position.set(1.29, 2.915, 0.317 * side + 0.012 * side);
    if (side === -1) glint.rotation.y = Math.PI;
    headGroup.add(glint);
  }
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.022, 0.022, 0.58), gold);
  bridge.position.set(1.24, 2.955, 0);
  headGroup.add(bridge);

  // wings
  const rightWing = createWing(1);
  const leftWing = createWing(-1);
  pelican.add(rightWing.outer, leftWing.outer);

  // tail feathers
  const tail = new THREE.Group();
  tail.position.set(-0.98, 1.58, 0);
  pelican.add(tail);
  for (let i = -2; i <= 2; i++) {
    const feather = new THREE.Mesh(new THREE.ConeGeometry(0.105, 0.56, 10), i === 0 ? cream : grey);
    feather.rotation.z = Math.PI / 2 - 0.14;
    feather.scale.z = 0.42;
    feather.position.set(-0.25, 0, 0.09 * i);
    const pivot = new THREE.Group();
    pivot.rotation.y = i * 0.2;
    pivot.rotation.x = 0.1 * i;
    pivot.add(feather);
    tail.add(pivot);
  }

  // legs and webbed feet
  const footShape = new THREE.Shape();
  footShape.moveTo(-0.08, -0.09);
  footShape.quadraticCurveTo(0.08, -0.13, 0.26, -0.14);
  footShape.lineTo(0.37, -0.11);
  footShape.quadraticCurveTo(0.42, 0, 0.37, 0.11);
  footShape.lineTo(0.26, 0.14);
  footShape.quadraticCurveTo(0.08, 0.13, -0.08, 0.09);
  footShape.quadraticCurveTo(-0.14, 0, -0.08, -0.09);
  const footGeo = new THREE.ExtrudeGeometry(footShape, {
    depth: 0.022,
    bevelEnabled: true,
    bevelThickness: 0.008,
    bevelSize: 0.008,
    bevelSegments: 2,
    curveSegments: 18,
  });
  footGeo.rotateX(-Math.PI / 2);

  for (const side of [-1, 1]) {
    const hip = new THREE.Vector3(0.03, 1.16, 0.29 * side);
    const knee = new THREE.Vector3(0.23, 0.7, 0.32 * side);
    const ankle = new THREE.Vector3(-0.01, 0.14, 0.33 * side);
    pelican.add(cylinderBetween(hip, knee, 0.072, orange));
    pelican.add(cylinderBetween(knee, ankle, 0.058, orange));
    const joint = new THREE.Mesh(new THREE.SphereGeometry(0.062, 18, 12), orange);
    joint.position.copy(knee);
    pelican.add(joint);
    const ankleJoint = new THREE.Mesh(new THREE.SphereGeometry(0.052, 16, 10), orange);
    ankleJoint.position.copy(ankle);
    pelican.add(ankleJoint);

    const foot = new THREE.Mesh(footGeo, orange);
    foot.position.set(0.03, 0.083, 0.33 * side);
    pelican.add(foot);

    const webbing = new THREE.Mesh(footGeo, pouchMat);
    webbing.scale.set(0.82, 0.7, 0.92);
    webbing.position.set(0.035, 0.089, 0.33 * side);
    pelican.add(webbing);
  }

  const update = (t) => {
    const flap = Math.sin(t * 1.15) * 0.075;
    rightWing.inner.rotation.x = 0.05 + flap;
    leftWing.inner.rotation.x = 0.05 + Math.sin(t * 1.15 + 0.4) * 0.075;
    rightWing.inner.rotation.y = Math.sin(t * 0.7) * 0.04;
    leftWing.inner.rotation.y = -Math.sin(t * 0.7) * 0.04;

    headGroup.position.y = Math.sin(t * 1.15 + 0.6) * 0.025;
    headGroup.rotation.z = Math.sin(t * 0.55) * 0.025;
    pouch.scale.y = 0.24 + Math.sin(t * 2.1) * 0.018;
    pelican.rotation.z = Math.sin(t * 0.8) * 0.014;
  };

  return { group, update, pelican, board };
}

// A small dark silhouette of a distant bird, for a little extra life in the sky.
export function createDistantBird() {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({
    color: "#4c5b60",
    transparent: true,
    opacity: 0.55,
    side: THREE.DoubleSide,
  });
  const wingGeo = new THREE.PlaneGeometry(1, 0.18);
  wingGeo.translate(0.5, 0, 0);
  const l = new THREE.Mesh(wingGeo, mat);
  l.rotation.z = 0.28;
  const r = new THREE.Mesh(wingGeo, mat);
  r.rotation.y = Math.PI;
  r.rotation.z = -0.28;
  g.add(l, r);
  g.userData.wings = [l, r];
  return g;
}
