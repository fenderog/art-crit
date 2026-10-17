import * as THREE from 'three';
import { makeBoardTexture, makeContactShadow } from './textures.js';

const C = {
  feather: 0xfff7e9,
  featherShade: 0xf1e6d2,
  wingRoot: 0xf7f2e5,
  wingMid: 0xdde2df,
  wingTip: 0x9fadb2,
  beak: 0xf7a62c,
  beakDark: 0xd87d1e,
  pouch: 0xf9b897,
  leg: 0xe88733,
  legDark: 0xcf6f23,
  eye: 0x241f1c,
  bandana: 0xf05e40,
  bandanaDark: 0xd14832,
  rail: 0xf6ead6,
  tail: 0xf4eddd,
};

const matte = (color, roughness = 0.86) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0 });

function createTaperedTube(points, radiusAt, tubular = 48, radial = 14) {
  const curve = new THREE.CatmullRomCurve3(
    points.map((p) => new THREE.Vector3(...p)),
    false,
    'catmullrom',
    0.5,
  );
  const frames = curve.computeFrenetFrames(tubular, false);
  const positions = [];
  const uvs = [];
  const normals = [];
  const indices = [];

  for (let i = 0; i <= tubular; i++) {
    const u = i / tubular;
    const p = curve.getPointAt(u);
    const N = frames.normals[i];
    const B = frames.binormals[i];
    const r = radiusAt(u);
    for (let j = 0; j <= radial; j++) {
      const v = (j / radial) * Math.PI * 2;
      const sin = Math.sin(v);
      const cos = -Math.cos(v);
      const nx = cos * N.x + sin * B.x;
      const ny = cos * N.y + sin * B.y;
      const nz = cos * N.z + sin * B.z;
      positions.push(p.x + r * nx, p.y + r * ny, p.z + r * nz);
      normals.push(nx, ny, nz);
      uvs.push(u, j / radial);
    }
  }

  for (let i = 1; i <= tubular; i++) {
    for (let j = 1; j <= radial; j++) {
      const a = (radial + 1) * (i - 1) + (j - 1);
      const b = (radial + 1) * i + (j - 1);
      const c = (radial + 1) * i + j;
      const d = (radial + 1) * (i - 1) + j;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setIndex(indices);
  return geo;
}

function featherGeometry(length = 1, width = 0.16, thickness = 0.025) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(width, length * 0.16, width * 0.92, length * 0.72, 0, length);
  s.bezierCurveTo(-width * 0.92, length * 0.72, -width, length * 0.16, 0, 0);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: thickness,
    bevelEnabled: true,
    bevelThickness: 0.006,
    bevelSize: 0.006,
    bevelSegments: 1,
    curveSegments: 12,
  });
  geo.translate(0, 0, -thickness * 0.5);
  return geo;
}

function createWingGeometry(span = 1.78) {
  const shape = new THREE.Shape();
  shape.moveTo(0, -0.31);
  shape.bezierCurveTo(0.38, -0.44, 0.9, -0.46, 1.32, -0.33);
  shape.quadraticCurveTo(1.62, -0.23, span, -0.015);

  // Scalloped trailing edge: pointed primaries and soft notches
  shape.lineTo(1.6, 0.07);
  shape.lineTo(1.61, 0.35);
  shape.lineTo(1.44, 0.1);
  shape.lineTo(1.3, 0.42);
  shape.lineTo(1.12, 0.15);
  shape.lineTo(0.96, 0.47);
  shape.lineTo(0.79, 0.2);
  shape.lineTo(0.61, 0.49);
  shape.lineTo(0.45, 0.23);
  shape.lineTo(0.26, 0.45);
  shape.lineTo(0.12, 0.3);
  shape.lineTo(0, 0.29);
  shape.closePath();

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.05,
    bevelEnabled: true,
    bevelThickness: 0.018,
    bevelSize: 0.018,
    bevelSegments: 2,
    curveSegments: 18,
  });

  // Gradient from warm white at the shoulder to cool grey at the primaries
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const cRoot = new THREE.Color(C.wingRoot);
  const cMid = new THREE.Color(C.wingMid);
  const cTip = new THREE.Color(C.wingTip);
  const tmp = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const t = THREE.MathUtils.clamp(x / span, 0, 1);
    if (t < 0.55) {
      tmp.copy(cRoot).lerp(cMid, t / 0.55);
    } else {
      tmp.copy(cMid).lerp(cTip, Math.pow((t - 0.55) / 0.45, 1.5));
    }
    // Slightly darker toward the trailing feather tips
    if (y > 0.15) tmp.multiplyScalar(0.94);
    colors[i * 3] = tmp.r;
    colors[i * 3 + 1] = tmp.g;
    colors[i * 3 + 2] = tmp.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  return geo;
}

function mirrorGeometryZ(source) {
  const geo = source.clone();
  geo.applyMatrix4(new THREE.Matrix4().makeScale(1, 1, -1));
  // Mirroring reverses triangle winding; swap two corners of each triangle
  // so normals point outwards again.
  for (const name of ['position', 'normal', 'uv', 'color']) {
    const attr = geo.attributes[name];
    if (!attr) continue;
    const size = attr.itemSize;
    for (let i = 0; i + 2 < attr.count; i += 3) {
      for (let k = 0; k < size; k++) {
        const a = (i + 1) * size + k;
        const b = (i + 2) * size + k;
        const tmp = attr.array[a];
        attr.array[a] = attr.array[b];
        attr.array[b] = tmp;
      }
    }
    attr.needsUpdate = true;
  }
  geo.computeVertexNormals();
  return geo;
}

function surfboardGeometry() {
  // Board outline built in the shape's XY plane (X = length, Y = width)
  const s = new THREE.Shape();
  const L = 2.45;
  s.moveTo(L, 0);
  s.bezierCurveTo(2.4, 0.2, 2.05, 0.38, 1.55, 0.45);
  s.bezierCurveTo(0.75, 0.56, 0.1, 0.57, -0.55, 0.56);
  s.bezierCurveTo(-1.35, 0.53, -1.95, 0.42, -2.28, 0.24);
  s.bezierCurveTo(-2.42, 0.14, -2.46, 0.05, -2.42, 0);
  s.bezierCurveTo(-2.46, -0.05, -2.42, -0.14, -2.28, -0.24);
  s.bezierCurveTo(-1.95, -0.42, -1.35, -0.53, -0.55, -0.56);
  s.bezierCurveTo(0.1, -0.57, 0.75, -0.56, 1.55, -0.45);
  s.bezierCurveTo(2.05, -0.38, 2.4, -0.2, L, 0);

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.13,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 3,
    curveSegments: 40,
  });
  // Lie the board flat, centre its thickness around y = 0
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, -0.065, 0);
  return geo;
}

function finGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(-0.24, -0.03, -0.42, -0.2, -0.46, -0.48);
  s.bezierCurveTo(-0.24, -0.4, -0.06, -0.2, 0.02, -0.02);
  s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.035,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.012,
    bevelSegments: 2,
    curveSegments: 16,
  });
  geo.translate(0, 0, -0.0175);
  return geo;
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(-0.09, 0);
  s.bezierCurveTo(0.02, -0.12, 0.2, -0.19, 0.34, -0.19);
  s.quadraticCurveTo(0.5, -0.19, 0.56, -0.12);
  s.quadraticCurveTo(0.38, -0.05, 0.37, 0.0);
  s.quadraticCurveTo(0.38, 0.05, 0.56, 0.12);
  s.quadraticCurveTo(0.5, 0.19, 0.34, 0.19);
  s.bezierCurveTo(0.2, 0.19, 0.02, 0.12, -0.09, 0);
  s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.028,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.012,
    bevelSegments: 2,
    curveSegments: 18,
  });
  geo.rotateX(-Math.PI / 2);
  return geo;
}

export function createSurfingPelican() {
  const group = new THREE.Group();
  group.name = 'board-and-pelican';

  // ---------------------------------------------------------------- board
  const boardTex = makeBoardTexture();
  const deckMat = new THREE.MeshPhysicalMaterial({
    map: boardTex,
    roughness: 0.34,
    metalness: 0.0,
    clearcoat: 0.65,
    clearcoatRoughness: 0.28,
  });
  const railMat = new THREE.MeshPhysicalMaterial({
    color: C.rail,
    roughness: 0.3,
    clearcoat: 0.5,
    clearcoatRoughness: 0.3,
  });

  const board = new THREE.Mesh(surfboardGeometry(), [deckMat, railMat]);
  board.castShadow = false;
  board.receiveShadow = false;
  group.add(board);

  const fin = new THREE.Mesh(finGeometry(), matte(0xe46a4c, 0.5));
  fin.position.set(-1.72, -0.06, 0);
  group.add(fin);

  const contact = new THREE.Mesh(
    new THREE.PlaneGeometry(2.75, 1.5),
    new THREE.MeshBasicMaterial({
      map: makeContactShadow(),
      transparent: true,
      opacity: 0.6,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2,
    }),
  );
  contact.rotation.x = -Math.PI / 2;
  contact.position.set(-0.15, 0.099, 0);
  group.add(contact);

  // -------------------------------------------------------------- pelican
  const pelicanRoot = new THREE.Group();
  pelicanRoot.position.y = 0.1;
  group.add(pelicanRoot);

  const featherMat = matte(C.feather, 0.78);
  const featherShadeMat = matte(C.featherShade, 0.82);
  const beakMat = matte(C.beak, 0.55);
  const beakDarkMat = matte(C.beakDark, 0.5);
  const pouchMat = new THREE.MeshStandardMaterial({
    color: C.pouch,
    roughness: 0.72,
    metalness: 0,
  });
  const legMat = matte(C.leg, 0.66);
  const eyeMat = new THREE.MeshStandardMaterial({
    color: C.eye,
    roughness: 0.12,
    metalness: 0.1,
  });
  const glintMat = new THREE.MeshBasicMaterial({ color: 0xfff8e8 });

  const bodyGroup = new THREE.Group();
  bodyGroup.position.y = 1.1;
  pelicanRoot.add(bodyGroup);

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 36), featherMat);
  body.scale.set(1.06, 0.72, 0.66);
  body.position.set(0.04, 0.12, 0);
  body.rotation.z = -0.04;
  bodyGroup.add(body);

  // ------------------------------------------------------------- tail
  const tailGroup = new THREE.Group();
  tailGroup.position.set(-0.72, 0.19, 0);
  bodyGroup.add(tailGroup);
  const tailMat = matte(C.tail, 0.82);
  for (let i = 0; i < 3; i++) {
    const f = new THREE.Mesh(featherGeometry(0.78 - i * 0.06, 0.13, 0.028), tailMat);
    f.position.set(0, 0, (i - 1) * 0.13);
    f.rotation.z = 1.43 + (i - 1) * 0.05;
    f.rotation.y = (i - 1) * 0.17;
    tailGroup.add(f);
  }

  // -------------------------------------------------------------- neck
  const neckGroup = new THREE.Group();
  neckGroup.position.set(0.34, 0.5, 0);
  bodyGroup.add(neckGroup);

  const neckCurvePoints = [
    [0.0, -0.08, 0.0],
    [0.19, 0.24, 0.01],
    [0.1, 0.54, 0.0],
    [0.31, 0.78, 0.0],
    [0.39, 0.93, 0.0],
  ];
  const neckGeo = createTaperedTube(
    neckCurvePoints,
    (u) => 0.285 - 0.11 * Math.pow(u, 0.7),
    44,
    16,
  );
  neckGroup.add(new THREE.Mesh(neckGeo, featherMat));

  // -------------------------------------------------------------- head
  const headGroup = new THREE.Group();
  headGroup.position.set(0.4, 0.95, 0);
  neckGroup.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 40, 30), featherMat);
  head.position.set(0.05, 0.1, 0);
  head.scale.set(1.14, 1.03, 0.97);
  headGroup.add(head);

  // crest feathers
  const crestMat = matte(0xe4e2d8, 0.9);
  for (let i = 0; i < 3; i++) {
    const f = new THREE.Mesh(featherGeometry(0.34 - i * 0.04, 0.055, 0.018), crestMat);
    f.position.set(-0.22, 0.2, (i - 1) * 0.055);
    f.rotation.z = 2.05 + (i - 1) * 0.12;
    f.rotation.x = (i - 1) * 0.12;
    headGroup.add(f);
  }

  // eyes + warm eye patches
  const patchMat = matte(0xf1d59e, 0.9);
  for (const side of [-1, 1]) {
    const patch = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 16), patchMat);
    patch.scale.set(0.085, 0.072, 0.032);
    patch.position.set(0.24, 0.17, side * 0.215);
    headGroup.add(patch);

    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.05, 20, 16), eyeMat);
    eye.position.set(0.26, 0.18, side * 0.232);
    headGroup.add(eye);

    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.013, 10, 8), glintMat);
    glint.position.set(0.29, 0.2, side * 0.258);
    headGroup.add(glint);
  }

  // -------------------------------------------------------------- beak
  const beakPivot = new THREE.Group();
  beakPivot.position.set(0.32, 0.075, 0);
  beakPivot.rotation.z = -0.2;
  headGroup.add(beakPivot);

  const billShape = new THREE.Shape();
  billShape.moveTo(0, 0.14);
  billShape.bezierCurveTo(0.42, 0.145, 0.88, 0.07, 1.18, 0.012);
  billShape.quadraticCurveTo(1.23, -0.004, 1.16, -0.032);
  billShape.bezierCurveTo(0.82, -0.095, 0.4, -0.145, 0, -0.135);
  billShape.closePath();
  const billGeo = new THREE.ExtrudeGeometry(billShape, {
    depth: 0.075,
    bevelEnabled: true,
    bevelThickness: 0.018,
    bevelSize: 0.018,
    bevelSegments: 2,
    curveSegments: 24,
  });
  billGeo.rotateX(Math.PI / 2);
  billGeo.translate(0, 0, 0); // y runs -0.075..0
  const bill = new THREE.Mesh(billGeo, beakMat);
  beakPivot.add(bill);

  // hook at the tip
  const hook = new THREE.Mesh(new THREE.SphereGeometry(0.065, 18, 14), beakDarkMat);
  hook.scale.set(0.75, 0.62, 0.9);
  hook.position.set(1.17, -0.035, 0);
  beakPivot.add(hook);

  // dark mouth line
  const mouthCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.04, -0.02, 0),
    new THREE.Vector3(0.42, -0.045, 0),
    new THREE.Vector3(0.84, -0.075, 0),
    new THREE.Vector3(1.17, -0.088, 0),
  ]);
  const mouth = new THREE.Mesh(
    new THREE.TubeGeometry(mouthCurve, 20, 0.012, 6, false),
    beakDarkMat,
  );
  beakPivot.add(mouth);

  // nostrils
  for (const side of [-1, 1]) {
    const nostril = new THREE.Mesh(new THREE.SphereGeometry(0.028, 12, 10), beakDarkMat);
    nostril.scale.set(0.55, 0.28, 0.5);
    nostril.position.set(0.21, 0.017, side * 0.055);
    beakPivot.add(nostril);
  }

  // pouch
  const pouchGroup = new THREE.Group();
  pouchGroup.position.set(0, 0, 0);
  pouchGroup.rotation.z = 0.02;
  beakPivot.add(pouchGroup);

  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 26), pouchMat);
  pouch.scale.set(0.61, 0.31, 0.265);
  pouch.position.set(0.55, -0.215, 0);
  pouchGroup.add(pouch);

  const throat = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 22), pouchMat);
  throat.scale.set(0.31, 0.32, 0.265);
  throat.position.set(0.13, -0.16, 0);
  pouchGroup.add(throat);

  // -------------------------------------------------------------- wings
  const wingGeoR = createWingGeometry();
  wingGeoR.rotateX(Math.PI / 2);
  wingGeoR.rotateY(-Math.PI / 2);
  const wingGeoL = mirrorGeometryZ(wingGeoR);

  const wingMat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.82,
    metalness: 0,
    side: THREE.DoubleSide,
  });

  const wingR = new THREE.Group();
  wingR.position.set(0.04, 0.52, 0.52);
  wingR.scale.setScalar(0.9);
  wingR.rotation.x = -0.98;
  wingR.rotation.y = -0.05;
  bodyGroup.add(wingR);
  const wingRMesh = new THREE.Mesh(wingGeoR, wingMat);
  wingR.add(wingRMesh);

  const wingL = new THREE.Group();
  wingL.position.set(0.04, 0.52, -0.52);
  wingL.scale.setScalar(0.9);
  wingL.rotation.x = 0.98;
  wingL.rotation.y = 0.05;
  bodyGroup.add(wingL);
  const wingLMesh = new THREE.Mesh(wingGeoL, wingMat);
  wingL.add(wingLMesh);

  // soft shoulder coverts
  for (const side of [-1, 1]) {
    const covert = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), featherMat);
    covert.scale.set(0.39, 0.22, 0.33);
    covert.position.set(0.07, 0.58, side * 0.55);
    covert.rotation.z = -0.15;
    bodyGroup.add(covert);
  }

  // -------------------------------------------------------------- legs
  const legsGroup = new THREE.Group();
  pelicanRoot.add(legsGroup);

  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.072, 0.34, 6, 12), legMat);
    leg.position.set(0.4, 0.31, side * 0.3);
    leg.rotation.z = -0.07;
    legsGroup.add(leg);

    const ankle = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 12), legMat);
    ankle.position.set(0.39, 0.46, side * 0.3);
    legsGroup.add(ankle);

    const foot = new THREE.Mesh(footGeometry(), legMat);
    foot.position.set(0.43, 0.035, side * 0.3);
    foot.rotation.y = -side * 0.08;
    legsGroup.add(foot);

    // tiny claws
    for (let k = -1; k <= 1; k++) {
      const claw = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.07, 6), beakDarkMat);
      claw.rotation.z = -Math.PI / 2;
      claw.position.set(0.99 + Math.abs(k) * -0.03, 0.045, side * 0.3 + k * 0.105);
      legsGroup.add(claw);
    }
  }

  // ------------------------------------------------------------- bandana
  const bandanaMat = matte(C.bandana, 0.8);
  const bandanaDarkMat = matte(C.bandanaDark, 0.82);

  const scarfRing = new THREE.Mesh(
    new THREE.TorusGeometry(0.235, 0.055, 12, 36),
    bandanaMat,
  );
  scarfRing.rotation.x = Math.PI / 2;
  scarfRing.position.set(0.02, 0.42, 0);
  scarfRing.scale.set(1.06, 1.0, 1.0);
  neckGroup.add(scarfRing);

  const knot = new THREE.Mesh(new THREE.SphereGeometry(0.075, 18, 14), bandanaDarkMat);
  knot.position.set(-0.02, 0.39, 0.255);
  knot.scale.set(1.15, 1.0, 0.85);
  neckGroup.add(knot);

  const scarfTails = [];
  for (let i = 0; i < 2; i++) {
    const tail = new THREE.Mesh(featherGeometry(0.5 + i * 0.1, 0.105, 0.018), bandanaMat);
    tail.position.set(-0.04, 0.38, 0.255 + (i - 0.5) * 0.03);
    tail.rotation.z = 1.62 + i * 0.2;
    tail.rotation.x = 0.45 + i * 0.22;
    tail.rotation.y = 0.55 + i * 0.1;
    neckGroup.add(tail);
    scarfTails.push(tail);
  }

  // ------------------------------------------------------------ leash
  const leashCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-2.02, 0.08, 0.28),
    new THREE.Vector3(-1.36, 0.03, 0.72),
    new THREE.Vector3(-0.62, 0.04, 0.78),
    new THREE.Vector3(0.12, 0.1, 0.56),
    new THREE.Vector3(0.42, 0.34, 0.34),
  ]);
  const leash = new THREE.Mesh(
    new THREE.TubeGeometry(leashCurve, 60, 0.017, 6, false),
    matte(0xd96245, 0.55),
  );
  group.add(leash);

  const ankleStrap = new THREE.Mesh(
    new THREE.TorusGeometry(0.098, 0.025, 8, 22),
    matte(0xd96245, 0.6),
  );
  ankleStrap.rotation.x = Math.PI / 2;
  ankleStrap.rotation.z = 0.08;
  ankleStrap.position.set(0.39, 0.34, 0.3);
  pelicanRoot.add(ankleStrap);

  // --------------------------------------------------------- animation
  const state = {
    wingFlap: 0,
  };

  function update(t, dt, waveSlopeX, waveSlopeZ) {
    // body breathing and a little balance sway
    const breath = 1 + Math.sin(t * 1.65 + 0.4) * 0.014;
    body.scale.set(1.06 * breath, 0.72 / breath, 0.66 * breath);

    bodyGroup.position.y = 1.1 + Math.sin(t * 1.9 + 1.1) * 0.018;
    bodyGroup.rotation.z = -0.035 + Math.sin(t * 0.72) * 0.032 - waveSlopeX * 0.03;
    bodyGroup.rotation.x = Math.sin(t * 0.57 + 2.0) * 0.02 + waveSlopeZ * 0.025;
    bodyGroup.rotation.y = Math.sin(t * 0.31) * 0.012;

    // neck and head: curious, slow glances
    neckGroup.rotation.y = Math.sin(t * 0.47 + 0.9) * 0.085 + Math.sin(t * 0.19) * 0.05;
    neckGroup.rotation.x = Math.sin(t * 0.63) * 0.035;
    neckGroup.rotation.z = Math.sin(t * 0.53 + 1.8) * 0.02;

    headGroup.rotation.y = Math.sin(t * 0.38 + 2.4) * 0.12;
    headGroup.rotation.x = Math.sin(t * 0.81 + 0.6) * 0.03;
    headGroup.rotation.z = Math.sin(t * 0.64 + 1.2) * 0.035;

    // beak + pouch: the pouch lags and jiggles with the swell
    const wobble = Math.sin(t * 4.9 + 0.8) * 0.035 + Math.sin(t * 2.3) * 0.025;
    pouchGroup.rotation.z = 0.02 + wobble * 0.75 - waveSlopeX * 0.04;
    pouchGroup.rotation.x = Math.sin(t * 3.7 + 1.4) * 0.02;
    pouch.scale.set(0.61, 0.31 * (1 + wobble * 0.55), 0.265 * (1 + wobble * 0.25));
    pouch.position.y = -0.215 - wobble * 0.035;

    // occasional stretch / flap, plus a gentle continuous sway
    const pulse = Math.pow(Math.max(0, Math.sin(t * 0.52 + 1.4)), 14);
    state.wingFlap += (pulse - state.wingFlap) * Math.min(1, dt * 4.5);
    const sway = Math.sin(t * 1.25) * 0.035 + Math.sin(t * 0.57 + 1.2) * 0.02;
    wingR.rotation.x = -0.98 - state.wingFlap * 0.45 - sway;
    wingL.rotation.x = 0.98 + state.wingFlap * 0.45 + sway;
    wingR.rotation.y = -0.05 - state.wingFlap * 0.12;
    wingL.rotation.y = 0.05 + state.wingFlap * 0.12;
    wingR.rotation.z = 0.03 + state.wingFlap * 0.08;
    wingL.rotation.z = -0.03 - state.wingFlap * 0.08;
    wingRMesh.position.y = -state.wingFlap * 0.02;
    wingLMesh.position.y = -state.wingFlap * 0.02;

    // tail twitch
    tailGroup.rotation.y = Math.sin(t * 1.1 + 2.2) * 0.07;
    tailGroup.rotation.x = Math.sin(t * 0.9) * 0.03;
    tailGroup.rotation.z = Math.sin(t * 1.7 + 0.3) * 0.02;

    // scarf in the wind
    for (let i = 0; i < scarfTails.length; i++) {
      const tail = scarfTails[i];
      const ph = t * (4.2 + i * 0.7) + i * 1.7;
      tail.rotation.z = 1.62 + i * 0.2 + Math.sin(ph) * 0.18;
      tail.rotation.y = 0.55 + i * 0.1 + Math.sin(ph * 0.7 + 1.0) * 0.24;
      tail.rotation.x = 0.45 + i * 0.22 + Math.cos(ph * 0.9) * 0.12;
      tail.scale.y = 1 + Math.sin(ph * 1.3) * 0.08;
    }
  }

  return { group, update, pelicanRoot };
}
