import * as THREE from 'three';

// ---------------------------------------------------------------------------
// geometry helpers
// ---------------------------------------------------------------------------

/** Box tapered toward +Z with an optional downward hook at the tip. */
function taperedBox(width, height, length, tipScale = 0.3, curveDown = 0, segs = 10) {
  const g = new THREE.BoxGeometry(width, height, length, 1, 1, segs);
  const pos = g.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i);
    // clamp: tiny negative k would make Math.pow return NaN
    const k = THREE.MathUtils.clamp(z / length + 0.5, 0, 1);
    const s = THREE.MathUtils.lerp(1, tipScale, Math.pow(k, 1.3));
    pos.setX(i, pos.getX(i) * s);
    pos.setY(i, pos.getY(i) * s - curveDown * k * k);
  }
  g.computeVertexNormals();
  return g;
}

/** Smooth tube swept along a curve with a variable radius. */
function makeTube(curve, tubularSegments, radialSegments, radiusFn) {
  const frames = curve.computeFrenetFrames(tubularSegments, false);
  const positions = [];
  const normals = [];
  const indices = [];
  const P = new THREE.Vector3();

  for (let i = 0; i <= tubularSegments; i++) {
    const u = i / tubularSegments;
    curve.getPointAt(u, P);
    const N = frames.normals[i];
    const B = frames.binormals[i];
    const r = radiusFn(u);
    for (let j = 0; j <= radialSegments; j++) {
      const v = (j / radialSegments) * Math.PI * 2;
      const sn = Math.sin(v);
      const cs = -Math.cos(v);
      const nx = cs * N.x + sn * B.x;
      const ny = cs * N.y + sn * B.y;
      const nz = cs * N.z + sn * B.z;
      positions.push(P.x + r * nx, P.y + r * ny, P.z + r * nz);
      normals.push(nx, ny, nz);
    }
  }
  for (let i = 0; i < tubularSegments; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const a = (radialSegments + 1) * i + j;
      const b = (radialSegments + 1) * (i + 1) + j;
      const c = (radialSegments + 1) * (i + 1) + j + 1;
      const d = (radialSegments + 1) * i + j + 1;
      indices.push(a, b, d, b, c, d);
    }
  }

  const g = new THREE.BufferGeometry();
  g.setIndex(indices);
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  return g;
}

/** Extruded flat blade (wing / feather / fin). */
function bladeShape(points, depth = 0.09, bevel = 0.05) {
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) {
    const p = points[i];
    if (p.length === 6) shape.bezierCurveTo(p[0], p[1], p[2], p[3], p[4], p[5]);
    else shape.lineTo(p[0], p[1]);
  }
  shape.closePath();
  return new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 2,
    curveSegments: 14,
  }).rotateX(-Math.PI / 2);
}

// ---------------------------------------------------------------------------
// materials
// ---------------------------------------------------------------------------

function buildMaterials() {
  return {
    white: new THREE.MeshStandardMaterial({ color: 0xf4f1e9, roughness: 0.72, metalness: 0.02 }),
    cream: new THREE.MeshStandardMaterial({ color: 0xe7e2d4, roughness: 0.78, metalness: 0.02 }),
    wing: new THREE.MeshStandardMaterial({
      color: 0xe9e6dc,
      roughness: 0.68,
      metalness: 0.02,
      side: THREE.DoubleSide,
    }),
    wingShade: new THREE.MeshStandardMaterial({
      color: 0xbfc0be,
      roughness: 0.72,
      side: THREE.DoubleSide,
    }),
    dark: new THREE.MeshStandardMaterial({
      color: 0x2e2d36,
      roughness: 0.62,
      side: THREE.DoubleSide,
    }),
    beakTop: new THREE.MeshStandardMaterial({ color: 0xe8a33c, roughness: 0.42, metalness: 0.06 }),
    beakBottom: new THREE.MeshStandardMaterial({ color: 0xcf7c2c, roughness: 0.5, metalness: 0.05 }),
    pouch: new THREE.MeshStandardMaterial({ color: 0xd4764a, roughness: 0.58, metalness: 0.03 }),
    eye: new THREE.MeshStandardMaterial({ color: 0x14111a, roughness: 0.22, metalness: 0.25 }),
    eyeRing: new THREE.MeshStandardMaterial({ color: 0xc8bda6, roughness: 0.6 }),
    glint: new THREE.MeshBasicMaterial({ color: 0xfffdf6 }),
    leg: new THREE.MeshStandardMaterial({ color: 0xdd7c2e, roughness: 0.55 }),
    fin: new THREE.MeshStandardMaterial({ color: 0x2b4550, roughness: 0.45, metalness: 0.1 }),
  };
}

// ---------------------------------------------------------------------------
// surfboard: smooth ellipsoid with painted vertex-colour stripes + a fin
// ---------------------------------------------------------------------------

function createSurfboard(mats) {
  const group = new THREE.Group();

  const geo = new THREE.SphereGeometry(1, 72, 36);
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const base = new THREE.Color(0xf2e3c6);
  const stripeRed = new THREE.Color(0xd9502f);
  const stripeTeal = new THREE.Color(0x2c6f86);
  const rail = new THREE.Color(0xb98c56);
  const c = new THREE.Color();

  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const z = pos.getZ(i);
    c.copy(base);
    if (Math.abs(z - 0.34) < 0.075) c.copy(stripeRed);
    if (Math.abs(z + 0.52) < 0.075) c.copy(stripeTeal);
    if (Math.abs(Math.abs(z) - 1.28) < 0.16) c.copy(stripeRed);
    if (Math.abs(x) > 0.945) c.copy(rail);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geo.scale(0.74, 0.135, 2.35);
  geo.computeVertexNormals();

  const boardMat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.32,
    metalness: 0.08,
  });
  const board = new THREE.Mesh(geo, boardMat);
  board.position.y = 0.225;
  board.castShadow = true;
  board.receiveShadow = true;
  group.add(board);

  // fin
  const fin = new THREE.Mesh(
    bladeShape(
      [
        [0, 0],
        [0.62, 0.1, 0.5, 0.42, 0.06, 0.78],
        [-0.02, 0.72, -0.16, 0.4, 0, 0],
      ],
      0.07,
      0.02
    ),
    mats.fin
  );
  fin.position.set(0, -0.02, -1.55);
  fin.rotation.x = -Math.PI / 2;
  fin.castShadow = true;
  group.add(fin);

  return group;
}

// ---------------------------------------------------------------------------
// wing: one broad extruded blade with a fan of feathers along the trailing edge
// ---------------------------------------------------------------------------

function createWing(mats) {
  const wing = new THREE.Group();

  const main = new THREE.Mesh(
    bladeShape(
      [
        [0, -0.3],
        [0.75, -0.44, 1.55, -0.34, 2.32, 0.0],
        [2.52, 0.1, 2.5, 0.28, 2.34, 0.36],
        [1.8, 0.62, 1.2, 0.92, 0.66, 0.98],
        [0.34, 0.92, 0.09, 0.62, 0, 0.3],
      ],
      0.11,
      0.055
    ),
    mats.wing
  );
  main.position.set(0, 0, 0.02);
  main.castShadow = true;
  wing.add(main);

  // secondary feathers fanning from the trailing edge
  const featherGeo = bladeShape(
    [
      [0, 0],
      [0.55, -0.17, 1.25, -0.21, 1.85, -0.06],
      [1.3, 0.15, 0.6, 0.19, 0, 0.13],
    ],
    0.055,
    0.026
  );

  const featherSpecs = [
    { x: 0.34, z: 0.3, rot: -0.36, s: 1.0, mat: mats.wingShade },
    { x: 0.68, z: 0.5, rot: -0.28, s: 1.05, mat: mats.wingShade },
    { x: 1.06, z: 0.62, rot: -0.2, s: 1.05, mat: mats.wing },
    { x: 1.44, z: 0.62, rot: -0.12, s: 1.0, mat: mats.wing },
  ];
  for (const spec of featherSpecs) {
    const f = new THREE.Mesh(featherGeo, spec.mat);
    f.position.set(spec.x, -0.025, spec.z);
    f.rotation.y = spec.rot;
    f.scale.setScalar(spec.s);
    f.castShadow = true;
    wing.add(f);
  }

  // black primaries at the tip
  const tipGeo = bladeShape(
    [
      [0, 0],
      [0.6, -0.2, 1.15, -0.16, 1.6, 0.02],
      [1.15, 0.24, 0.55, 0.26, 0, 0.12],
    ],
    0.05,
    0.022
  );
  for (const spec of [
    { x: 1.58, z: 0.36, rot: -0.3, s: 1.0 },
    { x: 1.82, z: 0.2, rot: -0.2, s: 0.94 },
    { x: 2.02, z: 0.0, rot: -0.08, s: 0.82 },
  ]) {
    const f = new THREE.Mesh(tipGeo, mats.dark);
    f.position.set(spec.x, -0.045, spec.z);
    f.rotation.y = spec.rot;
    f.scale.setScalar(spec.s);
    f.castShadow = true;
    wing.add(f);
  }

  return wing;
}

// ---------------------------------------------------------------------------
// the whole bird
// ---------------------------------------------------------------------------

export function createPelican() {
  const mats = buildMaterials();
  const group = new THREE.Group();

  // ---- board -------------------------------------------------------------
  const board = createSurfboard(mats);
  group.add(board);

  // ---- legs & feet -------------------------------------------------------
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.082, 0.072, 0.52, 12), mats.leg);
    leg.position.set(side * 0.36, 0.66, 0.16);
    leg.rotation.x = -0.16;
    leg.castShadow = true;
    group.add(leg);

    const foot = new THREE.Group();
    const web = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 12), mats.leg);
    web.scale.set(0.3, 0.055, 0.4);
    web.castShadow = true;
    foot.add(web);
    for (const toe of [-0.16, 0, 0.16]) {
      const t = new THREE.Mesh(taperedBox(0.11, 0.05, 0.3, 0.35, 0, 3), mats.leg);
      t.position.set(toe * side, 0.005, 0.3);
      t.rotation.y = toe * 1.3 * side;
      foot.add(t);
    }
    foot.position.set(side * 0.37, 0.42, 0.3);
    foot.rotation.y = side * 0.12;
    group.add(foot);
  }

  // ---- body --------------------------------------------------------------
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), mats.white);
  body.position.set(0, 1.42, -0.12);
  body.scale.set(0.92, 1.0, 1.44);
  body.castShadow = true;
  body.receiveShadow = true;
  group.add(body);

  // chest / shoulder volume so the neck blends in
  const chest = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), mats.white);
  chest.position.set(0, 1.78, 0.42);
  chest.scale.set(0.72, 0.72, 0.86);
  chest.castShadow = true;
  group.add(chest);

  // ---- tail ---------------------------------------------------------------
  const tail = new THREE.Group();
  const tailMain = new THREE.Mesh(taperedBox(0.62, 0.16, 1.25, 0.34, -0.12), mats.cream);
  tailMain.rotation.x = -Math.PI / 2 + 0.28;
  tailMain.position.set(0, 1.36, -1.62);
  tailMain.castShadow = true;
  tail.add(tailMain);
  const tailTip = new THREE.Mesh(taperedBox(0.5, 0.12, 0.62, 0.28, -0.05), mats.dark);
  tailTip.rotation.x = -Math.PI / 2 + 0.34;
  tailTip.position.set(0, 1.5, -2.16);
  tail.add(tailTip);
  group.add(tail);

  // ---- wings --------------------------------------------------------------
  const wingR = createWing(mats);
  wingR.position.set(0.72, 1.92, -0.18);
  wingR.rotation.set(-0.16, -0.14, 0.16);
  group.add(wingR);

  const wingL = createWing(mats);
  wingL.position.set(-0.72, 1.92, -0.18);
  wingL.rotation.set(-0.16, -0.14, 0.16);
  wingL.scale.x = -1;
  group.add(wingL);

  // ---- neck + head (pivots at the base of the neck) ------------------------
  const head = new THREE.Group();
  head.position.set(0, 1.95, 0.55);
  group.add(head);

  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, -0.06, -0.12),
    new THREE.Vector3(0, 0.34, 0.14),
    new THREE.Vector3(0, 0.74, 0.44),
    new THREE.Vector3(0, 0.92, 0.84),
    new THREE.Vector3(0, 0.97, 1.02),
  ]);
  const neck = new THREE.Mesh(
    makeTube(neckCurve, 30, 16, (u) => 0.31 + 0.19 * Math.pow(1 - u, 1.25)),
    mats.white
  );
  neck.castShadow = true;
  head.add(neck);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(1, 30, 22), mats.white);
  skull.position.set(0, 0.97, 1.07);
  skull.scale.set(0.41, 0.39, 0.52);
  skull.castShadow = true;
  head.add(skull);

  // beak
  const beakTop = new THREE.Mesh(taperedBox(0.31, 0.19, 1.58, 0.26, 0.3, 12), mats.beakTop);
  beakTop.position.set(0, 0.9, 2.16);
  beakTop.rotation.x = 0.075;
  beakTop.castShadow = true;
  head.add(beakTop);

  const beakBottom = new THREE.Mesh(taperedBox(0.26, 0.11, 1.28, 0.22, 0.12, 10), mats.beakBottom);
  beakBottom.position.set(0, 0.79, 2.06);
  beakBottom.rotation.x = 0.095;
  head.add(beakBottom);

  // gular pouch
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 26, 20), mats.pouch);
  pouch.position.set(0, 0.56, 1.82);
  pouch.scale.set(0.3, 0.36, 0.86);
  pouch.rotation.x = 0.12;
  head.add(pouch);

  // eyes
  const eyes = [];
  for (const side of [-1, 1]) {
    const ring = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 14), mats.eyeRing);
    ring.position.set(side * 0.285, 1.075, 1.29);
    ring.scale.set(0.105, 0.105, 0.085);
    head.add(ring);

    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.077, 18, 14), mats.eye);
    eye.position.set(side * 0.302, 1.078, 1.325);
    head.add(eye);
    eyes.push(eye);

    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.023, 10, 8), mats.glint);
    glint.position.set(side * 0.335, 1.115, 1.372);
    head.add(glint);
  }

  // ---- animation ----------------------------------------------------------
  const api = {
    group,
    board,
    head,
    tail,
    pouch,
    wingR,
    wingL,
    /** per-frame character animation (world placement happens in main.js) */
    update(t) {
      const flap = Math.sin(t * 1.45);
      const flap2 = Math.sin(t * 1.45 - 0.55);

      wingR.rotation.z = 0.16 + flap * 0.27;
      wingR.rotation.x = -0.16 + Math.sin(t * 1.45 + 0.7) * 0.11;
      wingR.rotation.y = -0.14 + Math.sin(t * 1.45 + 1.3) * 0.07;

      wingL.rotation.z = 0.16 + flap2 * 0.27;
      wingL.rotation.x = -0.16 + Math.sin(t * 1.45 + 0.7 - 0.55) * 0.11;
      wingL.rotation.y = -0.14 + Math.sin(t * 1.45 + 1.3 - 0.55) * 0.07;

      // look around, gentle neck sway
      head.rotation.y = Math.sin(t * 0.42) * 0.24 + Math.sin(t * 0.19) * 0.12;
      head.rotation.x = Math.sin(t * 0.31) * 0.075 + flap * 0.012;
      head.rotation.z = Math.sin(t * 0.27 + 1.1) * 0.05;

      // pouch breathes
      const p = 1 + Math.sin(t * 1.15) * 0.045;
      pouch.scale.set(0.3 * p, 0.36 * (1 + Math.sin(t * 1.15 + 1.2) * 0.07), 0.86);

      // tail counterbalance + body breathing
      tail.rotation.x = Math.sin(t * 0.83) * 0.075;
      tail.rotation.y = Math.sin(t * 0.61) * 0.06;
      body.scale.set(
        0.92 * (1 + Math.sin(t * 1.15) * 0.012),
        1.0 * (1 + Math.sin(t * 1.15 + 0.6) * 0.014),
        1.44
      );
    },
  };

  return api;
}