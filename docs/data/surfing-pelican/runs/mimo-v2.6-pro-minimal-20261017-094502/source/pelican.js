import * as THREE from 'three';
import { waveHeight, waveNormal } from './waves.js';

// Local frame convention: +Z = forward (direction of travel), +Y = up.

const C = {
  body: 0xf6f1e4,
  breast: 0xfbf7ec,
  shade: 0xdfe2dc,
  wing: 0xece7d8,
  wingTip: 0xb6c0c4,
  beakTop: 0xef9f36,
  beakLow: 0xe08a2c,
  pouch: 0xf6a23e,
  leg: 0xe8862c,
  eye: 0x221a15,
  eyeRing: 0xf1d69b,
  board: 0xf4f2ee,
  boardStripe: 0xe2583d,
  boardRail: 0x27536d,
  fin: 0x1d3d52,
};

function std(color, roughness = 0.7, extra = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness,
    metalness: 0,
    ...extra,
  });
}

/** Extrude a flat shape so it lies in the XZ plane: X = length, Z = chord, Y = thickness. */
function extrudeFlat(shape, { depth = 0.1, bevel = 0.05, segments = 24 } = {}) {
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: bevel > 0,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 4,
    curveSegments: segments,
  });
  geo.translate(0, 0, -depth / 2);
  geo.rotateX(Math.PI / 2);
  return geo;
}

/** Rounded leaf/feather shape, length along +X, width along Y. */
function featherShape(length, width) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(
    length * 0.28,
    width * 0.56,
    length * 0.72,
    width * 0.52,
    length,
    0,
  );
  s.bezierCurveTo(
    length * 0.72,
    -width * 0.52,
    length * 0.28,
    -width * 0.56,
    0,
    0,
  );
  return s;
}

function featherGeometry(length, width, depth = 0.055) {
  return extrudeFlat(featherShape(length, width), {
    depth,
    bevel: depth * 0.6,
    segments: 18,
  });
}

function buildBoard() {
  const group = new THREE.Group();
  const L = 2.15;
  const W = 0.62;

  const outline = new THREE.Shape();
  outline.moveTo(L, 0);
  outline.bezierCurveTo(L * 0.96, W * 0.52, L * 0.52, W * 0.96, 0, W);
  outline.bezierCurveTo(-L * 0.56, W * 0.96, -L * 0.97, W * 0.56, -L * 0.99, 0);
  outline.bezierCurveTo(-L * 0.97, -W * 0.56, -L * 0.56, -W * 0.96, 0, -W);
  outline.bezierCurveTo(L * 0.52, -W * 0.96, L * 0.96, -W * 0.52, L, 0);

  const boardGeo = extrudeFlat(outline, {
    depth: 0.13,
    bevel: 0.075,
    segments: 44,
  });
  boardGeo.rotateY(-Math.PI / 2); // nose toward +Z

  // rocker: nose and tail curve up
  const rockerY = (z) => {
    const t = z / L;
    return 0.2 * t * t + Math.max(0, t) * 0.1;
  };
  const applyRocker = (geo) => {
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      pos.setY(i, pos.getY(i) + rockerY(pos.getZ(i)));
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
    return geo;
  };
  applyRocker(boardGeo);

  const board = new THREE.Mesh(boardGeo, std(C.board, 0.42));
  group.add(board);

  // deck stripe
  const stripeShape = new THREE.Shape();
  stripeShape.moveTo(L * 0.86, 0);
  stripeShape.bezierCurveTo(L * 0.8, W * 0.3, L * 0.45, W * 0.42, 0, W * 0.42);
  stripeShape.bezierCurveTo(
    -L * 0.5,
    W * 0.42,
    -L * 0.82,
    W * 0.26,
    -L * 0.86,
    0,
  );
  stripeShape.bezierCurveTo(
    -L * 0.82,
    -W * 0.26,
    -L * 0.5,
    -W * 0.42,
    0,
    -W * 0.42,
  );
  stripeShape.bezierCurveTo(L * 0.45, -W * 0.42, L * 0.8, -W * 0.3, L * 0.86, 0);
  const stripeGeo = extrudeFlat(stripeShape, {
    depth: 0.012,
    bevel: 0.012,
    segments: 30,
  });
  stripeGeo.rotateY(-Math.PI / 2);
  stripeGeo.translate(0, 0.128, 0);
  applyRocker(stripeGeo);
  group.add(new THREE.Mesh(stripeGeo, std(C.boardStripe, 0.5)));

  // centre stringer for contrast
  const stringerShape = new THREE.Shape();
  stringerShape.moveTo(-L * 0.9, -0.022);
  stringerShape.lineTo(L * 0.9, -0.022);
  stringerShape.lineTo(L * 0.9, 0.022);
  stringerShape.lineTo(-L * 0.9, 0.022);
  stringerShape.closePath();
  const stringerGeo = extrudeFlat(stringerShape, {
    depth: 0.01,
    bevel: 0.01,
    segments: 4,
  });
  stringerGeo.rotateY(-Math.PI / 2);
  stringerGeo.translate(0, 0.132, 0);
  applyRocker(stringerGeo);
  group.add(new THREE.Mesh(stringerGeo, std(C.boardRail, 0.45)));

  // fins (chord along Z, height pointing down)
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(-0.6, 0);
  finShape.bezierCurveTo(-0.5, 0.24, -0.4, 0.42, -0.3, 0.5);
  finShape.lineTo(-0.18, 0.5);
  finShape.bezierCurveTo(-0.13, 0.34, -0.06, 0.16, 0, 0);
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.055,
    bevelEnabled: true,
    bevelThickness: 0.02,
    bevelSize: 0.02,
    bevelSegments: 3,
    curveSegments: 16,
  });
  finGeo.translate(0, 0, -0.0275);
  finGeo.rotateY(-Math.PI / 2);
  finGeo.rotateZ(Math.PI); // height points down
  const finMat = std(C.fin, 0.45);
  const finSpecs = [
    [0, -1.3, 0],
    [0.29, -1.14, -0.24],
    [-0.29, -1.14, 0.24],
  ];
  for (const [x, z, ry] of finSpecs) {
    const fin = new THREE.Mesh(finGeo, finMat);
    fin.position.set(x, -0.13 + rockerY(z) - 0.02, z);
    fin.rotation.y = ry;
    group.add(fin);
  }

  return group;
}

/** Mirror a geometry across X, repairing the triangle winding. */
function mirrorX(geo) {
  const g = geo.clone();
  g.scale(-1, 1, 1);
  for (const name of Object.keys(g.attributes)) {
    const attr = g.attributes[name];
    const arr = attr.array;
    const itemSize = attr.itemSize;
    const verts = arr.length / itemSize;
    for (let i = 0; i < verts; i += 3) {
      for (let k = 0; k < itemSize; k++) {
        const a = arr[(i + 1) * itemSize + k];
        arr[(i + 1) * itemSize + k] = arr[(i + 2) * itemSize + k];
        arr[(i + 2) * itemSize + k] = a;
      }
    }
    attr.needsUpdate = true;
  }
  return g;
}

function buildWing(side) {
  const group = new THREE.Group();
  const shape = new THREE.Shape();
  shape.moveTo(0, 0.3);
  shape.bezierCurveTo(0.85, 0.42, 1.75, 0.34, 2.42, 0.06);
  shape.bezierCurveTo(2.66, -0.03, 2.62, -0.2, 2.28, -0.28);
  shape.bezierCurveTo(1.5, -0.54, 0.62, -0.6, 0, -0.48);
  shape.closePath();

  const geo = extrudeFlat(shape, { depth: 0.11, bevel: 0.055, segments: 26 });
  const wingGeo = side < 0 ? mirrorX(geo) : geo;
  const matWing = std(C.wing, 0.82, { side: THREE.DoubleSide });
  const matTip = std(C.wingTip, 0.85, { side: THREE.DoubleSide });
  group.add(new THREE.Mesh(wingGeo, matWing));

  // primary feathers at the wing tip, fanned outward and back
  const featherGeo = featherGeometry(1.15, 0.34, 0.05);
  const baseAngle = side > 0 ? 1.1 : Math.PI - 1.1;
  const fans = [0.16, 0.03, -0.1, -0.23];
  for (let i = 0; i < fans.length; i++) {
    const feather = new THREE.Mesh(featherGeo, matTip);
    const x = side * (1.32 + i * 0.28);
    feather.position.set(x, -0.02 - i * 0.012, -0.2 - i * 0.11);
    feather.rotation.y = baseAngle + side * fans[i];
    feather.rotation.z = side * 0.05;
    group.add(feather);
  }
  return group;
}

function buildFoot() {
  const s = new THREE.Shape();
  s.moveTo(-0.15, -0.3);
  s.lineTo(-0.31, 0.28);
  s.quadraticCurveTo(-0.23, 0.43, -0.13, 0.31);
  s.lineTo(-0.07, 0.16);
  s.lineTo(-0.03, 0.45);
  s.quadraticCurveTo(0.03, 0.55, 0.1, 0.4);
  s.lineTo(0.13, 0.19);
  s.lineTo(0.29, 0.29);
  s.quadraticCurveTo(0.37, 0.2, 0.25, 0.1);
  s.lineTo(0.15, -0.3);
  s.closePath();
  return extrudeFlat(s, { depth: 0.055, bevel: 0.028, segments: 12 });
}

function buildPelican() {
  const bird = new THREE.Group();
  const matBody = std(C.body, 0.78);
  const matBreast = std(C.breast, 0.82);
  const matShade = std(C.shade, 0.8);
  const matBeakTop = std(C.beakTop, 0.42);
  const matBeakLow = std(C.beakLow, 0.5);
  const matPouch = std(C.pouch, 0.5, { emissive: 0x3a1b06, emissiveIntensity: 1 });
  const matLeg = std(C.leg, 0.6);
  const matEye = std(C.eye, 0.28);
  const matEyeRing = std(C.eyeRing, 0.72);

  // body
  const bodyGeo = new THREE.SphereGeometry(1, 40, 28);
  const body = new THREE.Mesh(bodyGeo, matBody);
  body.position.set(0, 2.02, -0.04);
  body.scale.set(0.84, 0.9, 1.48);
  body.rotation.x = 0.24;
  bird.add(body);

  const breast = new THREE.Mesh(bodyGeo, matBreast);
  breast.position.set(0, 1.72, 0.62);
  breast.scale.set(0.72, 0.78, 0.95);
  breast.rotation.x = 0.36;
  bird.add(breast);

  // tail feathers
  const tailGeo = featherGeometry(0.9, 0.4, 0.06);
  for (let i = -1; i <= 1; i++) {
    const tail = new THREE.Mesh(tailGeo, matShade);
    tail.position.set(i * 0.11, 2.12, -1.42);
    tail.rotation.y = Math.PI / 2 + i * 0.24;
    tail.rotation.x = 0.3;
    tail.rotation.z = i * 0.12;
    bird.add(tail);
  }

  // legs + webbed feet
  const legGeo = new THREE.CylinderGeometry(0.082, 0.098, 1.75, 12);
  const footGeo = buildFoot();
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(legGeo, matLeg);
    leg.position.set(side * 0.33, 1.05, 0.26);
    leg.rotation.x = 0.2;
    leg.rotation.z = side * -0.1;
    bird.add(leg);

    const foot = new THREE.Mesh(footGeo, matLeg);
    foot.position.set(side * 0.36, 0.135, 0.52);
    foot.rotation.y = side * 0.3;
    foot.rotation.x = -0.06;
    bird.add(foot);
  }

  // neck
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 2.3, 0.42),
    new THREE.Vector3(0, 2.92, 0.5),
    new THREE.Vector3(0, 3.36, 0.88),
    new THREE.Vector3(0, 3.52, 1.44),
  ]);
  const neck = new THREE.Mesh(
    new THREE.TubeGeometry(neckCurve, 40, 0.215, 16, false),
    matBody,
  );
  bird.add(neck);

  const nape = new THREE.Mesh(bodyGeo, matBody);
  nape.position.set(0, 2.3, 0.5);
  nape.scale.set(0.42, 0.5, 0.55);
  bird.add(nape);

  // head
  const head = new THREE.Group();
  head.position.set(0, 3.62, 1.64);
  bird.add(head);

  const skull = new THREE.Mesh(bodyGeo, matBody);
  skull.scale.set(0.45, 0.47, 0.53);
  head.add(skull);

  const crown = new THREE.Mesh(bodyGeo, matShade);
  crown.position.set(0, 0.13, -0.18);
  crown.scale.set(0.32, 0.24, 0.32);
  head.add(crown);

  // beak
  const beak = new THREE.Group();
  beak.position.set(0, -0.1, 0.3);
  beak.rotation.x = 0.1;
  head.add(beak);

  const upperGeo = new THREE.CylinderGeometry(0.045, 0.32, 1.58, 14);
  upperGeo.rotateX(Math.PI / 2);
  upperGeo.scale(1.0, 0.5, 1);
  const upper = new THREE.Mesh(upperGeo, matBeakTop);
  upper.position.set(0, 0.13, 0.78);
  beak.add(upper);

  const hookGeo = new THREE.ConeGeometry(0.085, 0.32, 12);
  hookGeo.rotateX(Math.PI / 2 + 0.55);
  const hook = new THREE.Mesh(hookGeo, matBeakTop);
  hook.position.set(0, 0.03, 1.6);
  beak.add(hook);

  const lowerGeo = new THREE.CylinderGeometry(0.045, 0.17, 1.36, 12);
  lowerGeo.rotateX(Math.PI / 2);
  lowerGeo.scale(0.82, 0.3, 1);
  const lower = new THREE.Mesh(lowerGeo, matBeakLow);
  lower.position.set(0, -0.06, 0.66);
  beak.add(lower);

  const pouch = new THREE.Mesh(bodyGeo, matPouch);
  pouch.position.set(0, -0.3, 0.64);
  pouch.scale.set(0.32, 0.4, 0.76);
  beak.add(pouch);

  // eyes
  for (const side of [-1, 1]) {
    const ring = new THREE.Mesh(bodyGeo, matEyeRing);
    ring.position.set(side * 0.385, 0.085, 0.13);
    ring.scale.set(0.055, 0.115, 0.14);
    head.add(ring);

    const eye = new THREE.Mesh(bodyGeo, matEye);
    eye.position.set(side * 0.418, 0.095, 0.175);
    eye.scale.setScalar(0.072);
    head.add(eye);

    const glint = new THREE.Mesh(
      bodyGeo,
      new THREE.MeshBasicMaterial({ color: 0xffffff }),
    );
    glint.position.set(side * 0.442, 0.125, 0.215);
    glint.scale.setScalar(0.023);
    head.add(glint);
  }

  return { bird, head, beak, pouch };
}

function buildWings() {
  const holder = new THREE.Group();
  const right = buildWing(1);
  const left = buildWing(-1);
  right.position.set(0.5, 2.22, 0.12);
  left.position.set(-0.5, 2.22, 0.12);
  holder.add(right, left);
  return { holder, right, left };
}

export function createSurfer() {
  const root = new THREE.Group();
  const ride = new THREE.Group();
  root.add(ride);

  const board = buildBoard();
  ride.add(board);

  const { bird, head, beak, pouch } = buildPelican();
  const { holder: wings, right: wingR, left: wingL } = buildWings();
  bird.add(wings);
  ride.add(bird);

  root.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  // scratch objects reused every frame
  const up = new THREE.Vector3();
  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const normal = { x: 0, y: 1, z: 0 };
  const basis = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const qRoll = new THREE.Quaternion();
  const qPitch = new THREE.Quaternion();
  const qYaw = new THREE.Quaternion();
  const Z_AXIS = new THREE.Vector3(0, 0, 1);
  const X_AXIS = new THREE.Vector3(1, 0, 0);
  const Y_AXIS = new THREE.Vector3(0, 1, 0);
  const UP = new THREE.Vector3(0, 1, 0);
  const wakeLocal = new THREE.Vector3(0, 0.16, -1.95);
  const wakeWorld = new THREE.Vector3();

  const state = {
    position: new THREE.Vector3(),
    forward: new THREE.Vector3(0, 0, 1),
  };

  function update(t) {
    // glide path: a lazy line across the wave face
    const x = Math.sin(t * 0.21) * 1.55 + Math.sin(t * 0.37) * 0.55;
    const z = Math.cos(t * 0.16) * 1.25 + Math.sin(t * 0.27) * 0.45;
    const yaw = -0.62 + Math.sin(t * 0.19) * 0.24 + Math.sin(t * 0.33) * 0.09;

    waveNormal(x, z, t, normal);
    const h = waveHeight(x, z, t);

    // sit on the surface, tilted with the wave face
    up.set(normal.x, normal.y, normal.z).lerp(UP, 0.45).normalize();
    fwd.set(Math.sin(yaw), 0, Math.cos(yaw));
    fwd.addScaledVector(up, -fwd.dot(up)).normalize();
    right.crossVectors(up, fwd).normalize();
    basis.makeBasis(right, up, fwd);
    q.setFromRotationMatrix(basis);

    const roll = -0.13 + Math.sin(t * 0.53) * 0.11 + Math.sin(t * 0.29) * 0.05;
    const pitch =
      -0.06 + (h - waveHeight(x + fwd.x * 2.2, z + fwd.z * 2.2, t)) * 0.12;
    qRoll.setFromAxisAngle(Z_AXIS, roll);
    qPitch.setFromAxisAngle(X_AXIS, pitch);
    q.multiply(qRoll).multiply(qPitch);

    root.quaternion.copy(q);
    root.position.set(x, h + 0.11, z);

    // ---- secondary motion ----
    const bob = Math.sin(t * 1.9) * 0.035 + Math.sin(t * 3.1) * 0.018;
    ride.position.y = bob;
    ride.rotation.z = Math.sin(t * 0.61) * 0.035;
    ride.rotation.x = Math.sin(t * 0.47 + 1.2) * 0.03;

    bird.position.y = 0.02 + Math.sin(t * 1.35) * 0.03;
    bird.rotation.y = Math.sin(t * 0.41) * 0.14 + Math.sin(t * 0.9) * 0.05;
    bird.rotation.x = 0.1 + Math.sin(t * 1.1) * 0.035;

    // head: looking down the line, occasional glances
    const glance = Math.sin(t * 0.33) * 0.32 + Math.sin(t * 0.83) * 0.12;
    head.rotation.y = glance;
    head.rotation.x = -0.06 + Math.sin(t * 0.72) * 0.07;

    // wings: held out and up for balance, with gentle flaps
    const flap = Math.sin(t * 2.35) * 0.16 + Math.sin(t * 0.71) * 0.12;
    const lift = 0.38 + flap;
    const sweep = 0.72 + Math.sin(t * 1.15) * 0.16;
    const twist = Math.sin(t * 1.7) * 0.06;
    wingR.rotation.set(-0.12 + twist, sweep, lift);
    wingL.rotation.set(-0.12 + twist, -sweep, -lift);

    // pouch jiggle
    const puff = 1 + Math.sin(t * 2.2) * 0.05 + Math.sin(t * 0.9) * 0.03;
    pouch.scale.set(0.32 * puff, 0.4 / puff, 0.76);
    beak.rotation.x = 0.1 + Math.sin(t * 0.65) * 0.045;

    state.position.copy(root.position);
    state.forward.copy(fwd);
  }

  function getWakePoint(target) {
    wakeWorld.copy(wakeLocal);
    root.localToWorld(wakeWorld);
    return (target || wakeWorld).copy(wakeWorld);
  }

  return { root, update, getWakePoint, state };
}