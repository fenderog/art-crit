import * as THREE from 'three';
import {
  createFeatherGeometry,
  createLoft,
  createTaperedTube,
  orientXAlong
} from './utils.js';

const UP = new THREE.Vector3(0, 1, 0);

function makeWebbedFoot() {
  const shape = new THREE.Shape();
  shape.moveTo(0.08, 0);
  shape.quadraticCurveTo(-0.04, 0.11, -0.26, 0.19);
  shape.quadraticCurveTo(-0.24, 0.09, -0.37, 0.065);
  shape.quadraticCurveTo(-0.28, 0.02, -0.44, 0.0);
  shape.quadraticCurveTo(-0.28, -0.02, -0.37, -0.065);
  shape.quadraticCurveTo(-0.24, -0.09, -0.26, -0.19);
  shape.quadraticCurveTo(-0.04, -0.11, 0.08, 0);
  shape.closePath();

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.025,
    bevelEnabled: true,
    bevelSize: 0.012,
    bevelThickness: 0.012,
    bevelSegments: 2,
    curveSegments: 14
  });
  geometry.rotateX(-Math.PI / 2);
  geometry.translate(0, 0, 0.0125);
  return geometry;
}

function createLegs(material) {
  const group = new THREE.Group();
  const legCurves = [
    [
      new THREE.Vector3(0.02, 0.66, 0.23),
      new THREE.Vector3(-0.08, 0.38, 0.275),
      new THREE.Vector3(-0.31, 0.14, 0.255)
    ],
    [
      new THREE.Vector3(0.42, 0.66, -0.22),
      new THREE.Vector3(0.46, 0.38, -0.265),
      new THREE.Vector3(0.37, 0.14, -0.245)
    ]
  ];

  const footGeometry = makeWebbedFoot();

  legCurves.forEach((points, i) => {
    const curve = new THREE.CatmullRomCurve3(points);
    const leg = new THREE.Mesh(
      createTaperedTube(curve, (t) => 0.062 - t * 0.018, 16, 9),
      material
    );
    group.add(leg);

    const foot = new THREE.Mesh(footGeometry, material);
    foot.position.set(points[2].x, 0.015, points[2].z);
    foot.rotation.y = i === 0 ? 0.18 : -0.12;
    group.add(foot);
  });

  return group;
}

function createRibbon(upper, material, { length, width, anchor, phase, rise, drift }) {
  const segments = 22;
  const positions = new Float32Array((segments + 1) * 2 * 3);
  const uvs = new Float32Array((segments + 1) * 2 * 2);
  const indices = [];

  for (let i = 0; i <= segments; i++) {
    uvs[(i * 2) * 2] = i / segments;
    uvs[(i * 2) * 2 + 1] = 0;
    uvs[(i * 2 + 1) * 2] = i / segments;
    uvs[(i * 2 + 1) * 2 + 1] = 1;
    if (i < segments) {
      const a = i * 2;
      indices.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex(indices);

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  upper.add(mesh);

  const p = new THREE.Vector3();
  const next = new THREE.Vector3();
  const tangent = new THREE.Vector3();
  const side = new THREE.Vector3();
  const halfWidth = new THREE.Vector3();

  function sample(s, t, out) {
    out.set(
      anchor.x + s * length + Math.sin(s * 4.5 - t * 2.2 + phase) * 0.055 * s,
      anchor.y + s * rise - s * s * 0.13 + Math.sin(s * 5.1 - t * 4.8 + phase) * 0.065 * s,
      anchor.z + s * drift + Math.sin(s * 6.1 - t * 3.7 + phase * 1.3) * 0.075 * s
    );
    return out;
  }

  function update(t) {
    const pos = geometry.getAttribute('position');
    for (let i = 0; i <= segments; i++) {
      const s = i / segments;
      sample(s, t, p);
      sample(Math.min(1, s + 0.02), t, next);
      tangent.subVectors(next, p).normalize();
      side.crossVectors(tangent, UP);
      if (side.lengthSq() < 1e-6) side.set(0, 0, 1);
      side.normalize();
      const twist = 0.45 * Math.sin(s * 5.5 - t * 3.3 + phase);
      side.applyAxisAngle(tangent, twist);
      const w = width * (1.0 - s * 0.42) * (0.75 + 0.25 * Math.sin(Math.PI * s));
      halfWidth.copy(side).multiplyScalar(w * 0.5);
      const a = i * 6;
      positions[a] = p.x + halfWidth.x;
      positions[a + 1] = p.y + halfWidth.y;
      positions[a + 2] = p.z + halfWidth.z;
      positions[a + 3] = p.x - halfWidth.x;
      positions[a + 4] = p.y - halfWidth.y;
      positions[a + 5] = p.z - halfWidth.z;
    }
    pos.needsUpdate = true;
    geometry.computeVertexNormals();
  }

  return { mesh, update };
}

export function createPelican() {
  const root = new THREE.Group();
  root.name = 'pelican';

  const upper = new THREE.Group();
  upper.position.set(0.1, 0.55, 0);
  root.add(upper);

  const whiteMaterial = new THREE.MeshStandardMaterial({
    color: 0xf8ead6,
    roughness: 0.78,
    metalness: 0.0,
    envMapIntensity: 0.38
  });

  const creamMaterial = new THREE.MeshStandardMaterial({
    color: 0xf6dfc0,
    roughness: 0.82,
    metalness: 0.0,
    envMapIntensity: 0.3
  });

  const featherMaterial = new THREE.MeshStandardMaterial({
    vertexColors: true,
    color: 0xffffff,
    roughness: 0.8,
    metalness: 0.0,
    side: THREE.DoubleSide,
    envMapIntensity: 0.3
  });

  const crestMaterial = new THREE.MeshStandardMaterial({
    color: 0xf7e7d0,
    roughness: 0.86,
    metalness: 0.0,
    side: THREE.DoubleSide
  });

  const orangeMaterial = new THREE.MeshStandardMaterial({
    color: 0xf47c24,
    roughness: 0.57,
    metalness: 0.0,
    envMapIntensity: 0.45
  });

  const beakMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xffa12c,
    roughness: 0.42,
    metalness: 0.0,
    clearcoat: 0.5,
    clearcoatRoughness: 0.35,
    envMapIntensity: 0.55
  });

  const pouchMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xffb449,
    roughness: 0.5,
    metalness: 0.0,
    clearcoat: 0.35,
    clearcoatRoughness: 0.45,
    sheen: 0.25,
    sheenColor: new THREE.Color(0xffd58b),
    sheenRoughness: 0.7,
    envMapIntensity: 0.45
  });

  const mouthMaterial = new THREE.MeshStandardMaterial({
    color: 0x9b4c1e,
    roughness: 0.7
  });

  const eyeGoldMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xffc64b,
    roughness: 0.22,
    metalness: 0.1,
    clearcoat: 1.0,
    clearcoatRoughness: 0.08
  });

  const pupilMaterial = new THREE.MeshPhysicalMaterial({
    color: 0x17121a,
    roughness: 0.08,
    metalness: 0.0,
    clearcoat: 1.0,
    clearcoatRoughness: 0.03
  });

  const scarfMaterial = new THREE.MeshPhysicalMaterial({
    color: 0x078b89,
    roughness: 0.58,
    metalness: 0.0,
    sheen: 0.65,
    sheenColor: new THREE.Color(0x94ffe8),
    sheenRoughness: 0.45,
    side: THREE.DoubleSide,
    envMapIntensity: 0.4
  });

  /* --------------------------------- legs --------------------------------- */
  const legs = createLegs(orangeMaterial);
  root.add(legs);

  /* --------------------------------- torso -------------------------------- */
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), whiteMaterial);
  body.position.set(0.12, 0.5, 0);
  body.rotation.z = 0.1;
  body.scale.set(0.64, 0.51, 0.44);
  upper.add(body);

  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.15, 0.64, 0.0),
    new THREE.Vector3(-0.31, 0.89, 0.012),
    new THREE.Vector3(-0.51, 1.11, 0.01),
    new THREE.Vector3(-0.64, 1.3, 0.0)
  ]);
  const neck = new THREE.Mesh(
    createTaperedTube(neckCurve, (t) => 0.215 - t * 0.035, 24, 12),
    whiteMaterial
  );
  upper.add(neck);

  /* ---------------------------------- head -------------------------------- */
  const head = new THREE.Group();
  head.position.set(-0.68, 1.4, 0);
  upper.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), whiteMaterial);
  skull.scale.set(0.34, 0.33, 0.315);
  head.add(skull);

  // A softly flattened crown.
  const crown = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), creamMaterial);
  crown.position.set(0.04, 0.13, -0.01);
  crown.scale.set(0.29, 0.18, 0.28);
  head.add(crown);

  // Upper mandible.
  const upperBeakSections = [
    { x: -0.24, y: 0.01, w: 0.2, h: 0.155 },
    { x: -0.49, y: -0.025, w: 0.18, h: 0.13 },
    { x: -0.78, y: -0.085, w: 0.135, h: 0.1 },
    { x: -1.05, y: -0.17, w: 0.085, h: 0.072 },
    { x: -1.23, y: -0.27, w: 0.032, h: 0.04 }
  ];
  const upperBeak = new THREE.Mesh(createLoft(upperBeakSections, 30, 16), beakMaterial);
  head.add(upperBeak);

  const hook = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), beakMaterial);
  hook.position.set(-1.235, -0.29, 0);
  hook.scale.set(0.037, 0.055, 0.032);
  head.add(hook);

  // Gular pouch.
  const pouchSections = [
    { x: -0.26, y: -0.15, w: 0.15, h: 0.18 },
    { x: -0.49, y: -0.33, w: 0.225, h: 0.25 },
    { x: -0.77, y: -0.39, w: 0.215, h: 0.215 },
    { x: -1.03, y: -0.33, w: 0.155, h: 0.145 },
    { x: -1.225, y: -0.235, w: 0.055, h: 0.058 }
  ];
  const pouch = new THREE.Mesh(createLoft(pouchSections, 32, 18), pouchMaterial);
  head.add(pouch);

  // A dark mouth seam along both sides.
  for (const side of [-1, 1]) {
    const mouthCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-0.3, -0.075, side * 0.155),
      new THREE.Vector3(-0.53, -0.16, side * 0.17),
      new THREE.Vector3(-0.8, -0.225, side * 0.14),
      new THREE.Vector3(-1.04, -0.285, side * 0.082),
      new THREE.Vector3(-1.22, -0.31, side * 0.025)
    ]);
    const mouth = new THREE.Mesh(
      createTaperedTube(mouthCurve, (t) => 0.009 - t * 0.003, 22, 5),
      mouthMaterial
    );
    head.add(mouth);
  }

  // Eyes, with a warm pelican-gold iris and a bright pinprick catchlight.
  for (const side of [-1, 1]) {
    const iris = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), eyeGoldMaterial);
    iris.position.set(-0.145, 0.075, side * 0.293);
    iris.scale.set(0.088, 0.09, 0.042);
    head.add(iris);

    const pupil = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), pupilMaterial);
    pupil.position.set(-0.153, 0.08, side * 0.326);
    pupil.scale.set(0.053, 0.06, 0.026);
    head.add(pupil);

    const catchlight = new THREE.Mesh(
      new THREE.SphereGeometry(1, 10, 8),
      new THREE.MeshBasicMaterial({ color: 0xfff8e8 })
    );
    catchlight.position.set(-0.175, 0.105, side * 0.344);
    catchlight.scale.set(0.014, 0.014, 0.009);
    head.add(catchlight);
  }

  /* -------------------------------- crest --------------------------------- */
  const crest = new THREE.Group();
  crest.position.set(0.16, 0.2, 0.01);
  head.add(crest);
  const crestFeatherGeo = createFeatherGeometry();
  const crestSpecs = [
    { a: 0.58, l: 0.36, w: 0.82, x: 0.02 },
    { a: 0.82, l: 0.43, w: 0.72, x: 0.0 },
    { a: 1.04, l: 0.32, w: 0.62, x: -0.015 }
  ];
  for (const spec of crestSpecs) {
    const feather = new THREE.Mesh(crestFeatherGeo, crestMaterial);
    feather.position.set(spec.x, 0, 0.01);
    feather.rotation.z = spec.a;
    feather.scale.set(spec.l, spec.w, 1);
    crest.add(feather);
  }

  /* --------------------------------- wings -------------------------------- */
  const featherGeometry = createFeatherGeometry();

  function createWing(side) {
    const wing = new THREE.Group();

    const armCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0.22, 0.045, 0),
      new THREE.Vector3(0.46, 0.075, 0)
    ]);
    const arm = new THREE.Mesh(
      createTaperedTube(armCurve, (t) => 0.085 - t * 0.024, 14, 8),
      whiteMaterial
    );
    wing.add(arm);

    const covert = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), creamMaterial);
    covert.position.set(0.16, 0.02, 0.005);
    covert.scale.set(0.26, 0.12, 0.055);
    wing.add(covert);

    const panelShape = new THREE.Shape();
    panelShape.moveTo(0.02, -0.07);
    panelShape.bezierCurveTo(0.24, 0.12, 0.72, 0.15, 1.02, 0.045);
    panelShape.bezierCurveTo(0.72, -0.14, 0.26, -0.16, 0.02, -0.07);
    panelShape.closePath();
    const panelGeometry = new THREE.ExtrudeGeometry(panelShape, {
      depth: 0.018,
      bevelEnabled: true,
      bevelThickness: 0.008,
      bevelSize: 0.01,
      bevelSegments: 2,
      curveSegments: 20
    });
    panelGeometry.translate(0, 0, -0.009);
    const panel = new THREE.Mesh(panelGeometry, creamMaterial);
    panel.position.set(0.08, 0.005, -0.026);
    panel.scale.set(0.82, 0.9, 1);
    wing.add(panel);

    const featherCount = 7;
    const lengths = [0.76, 0.92, 1.05, 1.13, 1.07, 0.93, 0.74];
    const widths = [0.88, 0.96, 1.03, 1.08, 1.01, 0.91, 0.8];
    const feathers = [];

    for (let i = 0; i < featherCount; i++) {
      const mesh = new THREE.Mesh(featherGeometry, featherMaterial);
      const angle = -0.27 + i * 0.135;
      mesh.position.set(0.13 + i * 0.032, 0.01, (i % 2) * 0.006);
      mesh.rotation.z = angle;
      mesh.scale.set(lengths[i], widths[i], 0.9);
      mesh.userData.baseAngle = angle;
      wing.add(mesh);
      feathers.push(mesh);
    }

    for (let i = 0; i < 3; i++) {
      const covertFeather = new THREE.Mesh(featherGeometry, crestMaterial);
      covertFeather.position.set(0.14 + i * 0.07, -0.02, 0.02);
      covertFeather.rotation.z = -0.1 + i * 0.22;
      covertFeather.scale.set(0.38 + i * 0.06, 0.7, 0.7);
      wing.add(covertFeather);
    }

    // A slight dihedral twist makes the fan feel less like a paper cut-out.
    wing.rotation.z = side * 0.015;
    return { wing, feathers };
  }

  const leftWing = createWing(1);
  const rightWing = createWing(-1);
  leftWing.wing.position.set(0.06, 0.74, 0.36);
  rightWing.wing.position.set(0.06, 0.74, -0.36);
  upper.add(leftWing.wing, rightWing.wing);

  /* ---------------------------------- tail -------------------------------- */
  const tail = new THREE.Group();
  tail.position.set(0.68, 0.6, 0);
  upper.add(tail);

  const tailSpecs = [
    { a: -0.3, l: 0.52, w: 0.82, z: -0.015 },
    { a: -0.13, l: 0.66, w: 0.92, z: 0 },
    { a: 0.06, l: 0.76, w: 1.0, z: 0.012 },
    { a: 0.25, l: 0.65, w: 0.9, z: 0.006 },
    { a: 0.43, l: 0.52, w: 0.8, z: -0.008 }
  ];
  for (const spec of tailSpecs) {
    const feather = new THREE.Mesh(featherGeometry, featherMaterial);
    feather.position.set(0, 0, spec.z);
    feather.rotation.z = spec.a;
    feather.scale.set(spec.l, spec.w, 0.75);
    tail.add(feather);
  }
  orientXAlong(tail, new THREE.Vector3(0.9, 0.28, 0.14));

  /* --------------------------------- scarf -------------------------------- */
  const neckAxis = new THREE.Vector3(0.13, 0.38, 0).normalize();
  const scarfRingGeometry = new THREE.TorusGeometry(0.198, 0.046, 8, 22);
  scarfRingGeometry.rotateX(Math.PI / 2);
  const scarfRing = new THREE.Mesh(scarfRingGeometry, scarfMaterial);
  scarfRing.position.set(-0.31, 0.84, 0);
  scarfRing.quaternion.setFromUnitVectors(UP, neckAxis);
  upper.add(scarfRing);

  const knot = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), scarfMaterial);
  knot.position.set(-0.2, 0.83, 0.17);
  knot.scale.set(0.105, 0.075, 0.085);
  upper.add(knot);

  const ribbonMain = createRibbon(upper, scarfMaterial, {
    length: 1.7,
    width: 0.19,
    anchor: new THREE.Vector3(-0.2, 0.89, 0.17),
    phase: 0.2,
    rise: 0.5,
    drift: 0.4
  });
  const ribbonSecond = createRibbon(upper, scarfMaterial, {
    length: 1.18,
    width: 0.125,
    anchor: new THREE.Vector3(-0.24, 0.86, 0.2),
    phase: 2.1,
    rise: 0.58,
    drift: 0.53
  });

  /* -------------------------------- shadows ------------------------------- */
  root.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  const leftDir = new THREE.Vector3();
  const rightDir = new THREE.Vector3();

  function update(t) {
    const surf = Math.sin(t * 0.72);
    const flap = Math.sin(t * 1.15 + 0.7);

    upper.position.y = 0.55 + Math.sin(t * 1.55) * 0.012;
    upper.rotation.z = 0.085 + Math.sin(t * 0.74 + 0.4) * 0.028 + surf * 0.014;
    upper.rotation.x = Math.sin(t * 0.63) * 0.012;
    upper.rotation.y = Math.sin(t * 0.43 + 1.1) * 0.018;

    head.position.y = 1.4 + Math.sin(t * 1.55 + 0.18) * 0.012;
    head.rotation.y = 0.08 * Math.sin(t * 0.33 + 0.9) + Math.sin(t * 0.71) * 0.015;
    head.rotation.z = 0.018 + Math.sin(t * 0.81 + 0.3) * 0.018;
    head.rotation.x = Math.sin(t * 0.55 + 2.1) * 0.012;

    leftDir.set(0.57 + flap * 0.028, 0.42 + flap * 0.085, 0.7);
    orientXAlong(leftWing.wing, leftDir);

    rightDir.set(-0.58, 0.68 + Math.sin(t * 1.15 + 2.2) * 0.085, -0.43);
    orientXAlong(rightWing.wing, rightDir);

    leftWing.feathers.forEach((feather, i) => {
      feather.rotation.z = feather.userData.baseAngle + Math.sin(t * 2.0 + i * 0.7) * 0.012;
    });
    rightWing.feathers.forEach((feather, i) => {
      feather.rotation.z = feather.userData.baseAngle + Math.sin(t * 1.8 + i * 0.6 + 1.7) * 0.01;
    });

    tail.rotation.z = Math.sin(t * 1.05 + 0.2) * 0.03;
    ribbonMain.update(t);
    ribbonSecond.update(t);
  }

  return { root, upper, head, leftWing, rightWing, update };
}
