import * as THREE from "three";

const std = (color, roughness = 0.68, metalness = 0) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness });

function adopt(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function paint(geo, colorAt) {
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const col = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    colorAt(col, pos.getX(i), pos.getY(i), pos.getZ(i), i);
    colors[i * 3] = col.r;
    colors[i * 3 + 1] = col.g;
    colors[i * 3 + 2] = col.b;
  }
  geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
}

function halfWidth(t) {
  const tail = Math.sin(Math.min(1, t / 0.14) * Math.PI * 0.5);
  const nose = Math.pow(1 - t, 0.48);
  const plan = Math.sin(Math.PI * Math.pow(t, 0.72));
  return (0.075 + 0.235 * plan) * (0.32 + 0.68 * nose) * (0.42 + 0.58 * tail);
}

function createBoard() {
  const shape = new THREE.Shape();
  const length = 2.85;
  const samples = 32;
  const outline = [];
  for (let i = 0; i <= samples; i++) {
    const t = i / samples;
    const y = (t - 0.46) * length;
    outline.push(new THREE.Vector2(halfWidth(t), y));
  }
  shape.moveTo(outline[0].x, outline[0].y);
  for (let i = 1; i < outline.length; i++) shape.lineTo(outline[i].x, outline[i].y);
  for (let i = outline.length - 1; i >= 0; i--) shape.lineTo(-outline[i].x, outline[i].y);
  shape.closePath();

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.085,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.016,
    bevelSegments: 2,
    curveSegments: 2,
  });
  // Shape +Y is the nose. rotateX(-90°) maps +Y to -Z, the rig's forward.
  geo.rotateX(-Math.PI / 2);

  const pos = geo.attributes.position;
  let zMin = Infinity;
  let zMax = -Infinity;
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i);
    zMin = Math.min(zMin, z);
    zMax = Math.max(zMax, z);
  }
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i);
    const u = (z - zMin) / (zMax - zMin || 1);
    const noseRocker = (1 - u) * (1 - u) * 0.11;
    const tailRocker = u * u * 0.05;
    pos.setY(i, pos.getY(i) + noseRocker + tailRocker);
  }
  geo.computeVertexNormals();

  const deck = new THREE.Color(0xf7f2e8);
  const hull = new THREE.Color(0x0f6c76);
  const rail = new THREE.Color(0xe36a45);
  const normal = geo.attributes.normal;
  paint(geo, (col, x, y, z, i) => {
    const ny = normal.getY(i);
    if (ny > 0.55) col.copy(deck);
    else if (ny < -0.25) col.copy(hull);
    else col.copy(rail);
  });
  geo.computeBoundingBox();
  geo.computeBoundingSphere();

  const mesh = adopt(
    new THREE.Mesh(
      geo,
      new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.42,
        metalness: 0.02,
      }),
    ),
  );

  // Sit the center of the hull on y = 0.
  let seat = Infinity;
  for (let i = 0; i < pos.count; i++) {
    if (Math.abs(pos.getX(i)) < 0.12 && Math.abs(pos.getZ(i)) < 0.2) {
      seat = Math.min(seat, pos.getY(i));
    }
  }
  if (Number.isFinite(seat)) mesh.position.y = -seat;

  const bb = geo.boundingBox;
  const nose = new THREE.Object3D();
  nose.name = "boardNose";
  nose.position.set(0, 0.06, bb.min.z + 0.04);
  const tail = new THREE.Object3D();
  tail.name = "boardTail";
  tail.position.set(0, 0.05, bb.max.z - 0.05);
  mesh.add(nose, tail);

  const deckY = (() => {
    let y = 0;
    for (let i = 0; i < pos.count; i++) {
      if (Math.abs(pos.getX(i)) < 0.12 && Math.abs(pos.getZ(i)) < 0.25 && normal.getY(i) > 0.5) {
        y = Math.max(y, pos.getY(i) + mesh.position.y);
      }
    }
    return y || 0.1;
  })();

  const stripeMat = std(0xe4533a, 0.4);
  const stripe = adopt(new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.008, 2.05), stripeMat));
  stripe.position.set(0, deckY + 0.004, -0.05);

  const discMat = std(0xe25b3a, 0.42);
  const discInner = std(0xf7f2e8, 0.4);
  const disc = adopt(new THREE.Mesh(new THREE.CircleGeometry(0.1, 22), discMat));
  const inner = adopt(new THREE.Mesh(new THREE.CircleGeometry(0.048, 18), discInner));
  disc.rotation.x = -Math.PI / 2;
  inner.rotation.x = -Math.PI / 2;
  disc.position.set(0, deckY + 0.006, bb.min.z + 0.42);
  inner.position.set(0, deckY + 0.008, bb.min.z + 0.42);

  const pad = adopt(
    new THREE.Mesh(
      new THREE.CircleGeometry(0.2, 20),
      std(0x2c261f, 0.92),
    ),
  );
  pad.rotation.x = -Math.PI / 2;
  pad.scale.set(0.72, 1, 1.35);
  pad.position.set(0, deckY + 0.005, 0.22);

  const finMat = std(0x0c3e48, 0.45);
  const finGeo = finGeometry();
  const fins = new THREE.Group();
  const finSpecs = [
    [0, bb.max.z - 0.22, 0],
    [-0.13, bb.max.z - 0.4, 0.22],
    [0.13, bb.max.z - 0.4, -0.22],
  ];
  for (const [x, z, yaw] of finSpecs) {
    const fin = adopt(new THREE.Mesh(finGeo, finMat));
    fin.position.set(x, mesh.position.y + 0.01, z);
    fin.rotation.y = yaw;
    fins.add(fin);
  }

  const group = new THREE.Group();
  group.add(mesh, stripe, disc, inner, pad, fins);
  group.userData.deckY = deckY;
  return group;
}

function finGeometry() {
  const s = new THREE.Shape();
  s.moveTo(-0.02, 0);
  s.lineTo(0.16, 0);
  s.lineTo(0.1, -0.2);
  s.lineTo(0.0, -0.16);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.014, bevelEnabled: false });
  g.translate(0, 0, -0.007);
  // Thickness was +Z. Stand the blade in the YZ plane, length along Z, tip down.
  g.rotateY(Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

function wingShape() {
  const s = new THREE.Shape();
  // Span runs +X, the silhouette stands in Y so a front view sees the wing.
  s.moveTo(0.0, -0.02);
  s.bezierCurveTo(0.32, 0.26, 0.85, 0.36, 1.22, 0.1);
  s.lineTo(1.34, 0.0);
  s.lineTo(1.12, -0.05);
  s.lineTo(1.26, -0.12);
  s.lineTo(0.95, -0.1);
  s.bezierCurveTo(0.55, -0.22, 0.22, -0.12, 0.0, -0.04);
  s.closePath();
  return s;
}

function createWingGeometry() {
  const geo = new THREE.ExtrudeGeometry(wingShape(), {
    depth: 0.045,
    bevelEnabled: true,
    bevelThickness: 0.008,
    bevelSize: 0.008,
    bevelSegments: 1,
  });
  geo.translate(0, 0, -0.022);
  geo.computeBoundingBox();
  const bb = geo.boundingBox;
  const span = bb.max.x - bb.min.x || 1;
  const root = new THREE.Color(0xa88468);
  const mid = new THREE.Color(0x7a5642);
  const tip = new THREE.Color(0x3d2c26);
  paint(geo, (col, x) => {
    const u = (x - bb.min.x) / span;
    if (u < 0.6) col.copy(root).lerp(mid, u / 0.6);
    else col.copy(mid).lerp(tip, (u - 0.6) / 0.4);
  });
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

function createWing(geo, side) {
  const mat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.72,
    metalness: 0,
    side: THREE.DoubleSide,
  });
  const mesh = adopt(new THREE.Mesh(geo, mat));
  const pivot = new THREE.Group();
  pivot.add(mesh);

  geo.computeBoundingBox();
  const bb = geo.boundingBox;
  const tipX = Math.abs(bb.max.x) > Math.abs(bb.min.x) ? bb.max.x : bb.min.x;
  const sign = Math.sign(tipX) || 1;
  const featherMat = std(0x3a2a24, 0.7);
  const featherGeo = new THREE.BoxGeometry(0.18, 0.018, 0.035);
  for (let i = 0; i < 3; i++) {
    const f = adopt(new THREE.Mesh(featherGeo, featherMat));
    f.position.set(tipX + sign * 0.06, (i - 1) * 0.045, 0);
    f.rotation.z = -sign * (i - 1) * 0.18;
    mesh.add(f);
  }

  const marker = new THREE.Object3D();
  marker.name = side === "r" ? "wingTipR" : "wingTipL";
  marker.position.set(tipX + sign * 0.16, 0, 0);
  mesh.add(marker);
  return pivot;
}

function createEye(side) {
  const g = new THREE.Group();
  const sign = side;
  g.position.set(sign * 0.1, 0.02, -0.05);
  const ball = adopt(
    new THREE.Mesh(new THREE.SphereGeometry(0.048, 16, 12), std(0xf3e7a4, 0.28)),
  );
  const pupil = adopt(
    new THREE.Mesh(new THREE.SphereGeometry(0.025, 12, 10), std(0x140e0c, 0.2)),
  );
  pupil.position.set(sign * 0.03, 0, -0.012);
  const glint = new THREE.Mesh(
    new THREE.SphereGeometry(0.01, 8, 6),
    new THREE.MeshBasicMaterial({ color: 0xffffff }),
  );
  glint.position.set(sign * 0.038, 0.014, -0.016);
  const ring = adopt(
    new THREE.Mesh(new THREE.TorusGeometry(0.052, 0.011, 8, 16), std(0xe07a40, 0.55)),
  );
  ring.rotation.y = Math.PI / 2;
  const brow = adopt(new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.016, 0.028), std(0x3a2c24, 0.7)));
  brow.position.set(sign * 0.03, 0.048, -0.01);
  brow.rotation.z = -sign * 0.45;
  g.add(ball, pupil, glint, ring, brow);
  return g;
}

function createWeb() {
  const s = new THREE.Shape();
  s.moveTo(0, -0.02);
  s.lineTo(0.11, 0.15);
  s.lineTo(0.02, 0.1);
  s.lineTo(0, 0.16);
  s.lineTo(-0.02, 0.1);
  s.lineTo(-0.11, 0.15);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.012, bevelEnabled: false });
  g.translate(0, 0, -0.006);
  // Toes are +Y. rotateX(-90°) sends them to -Z, the forward axis.
  g.rotateX(-Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

function createLeg(x, z, yaw, deckY) {
  const g = new THREE.Group();
  g.position.set(x, deckY, z);
  g.rotation.y = yaw;
  const leg = adopt(
    new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.028, 0.13, 8), std(0xd9894e, 0.62)),
  );
  leg.position.y = 0.07;
  const foot = adopt(new THREE.Mesh(createWeb(), std(0xc98448, 0.6)));
  foot.position.y = 0.012;
  g.add(leg, foot);
  return g;
}

function createBeakGeometry() {
  const pts = [
    new THREE.Vector2(0.012, 0.8),
    new THREE.Vector2(0.03, 0.62),
    new THREE.Vector2(0.052, 0.34),
    new THREE.Vector2(0.078, 0.12),
    new THREE.Vector2(0.09, 0.0),
  ];
  const g = new THREE.LatheGeometry(pts, 18);
  g.rotateX(-Math.PI / 2);
  g.scale(1, 0.72, 1);
  g.translate(0, 0.035, 0);
  const base = new THREE.Color(0xf0d078);
  const tip = new THREE.Color(0xe07a32);
  paint(g, (col, x, y, z) => {
    const u = THREE.MathUtils.clamp(-z / 0.8, 0, 1);
    col.copy(base).lerp(tip, u * u);
  });
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

function createBird(deckY) {
  const bird = new THREE.Group();
  bird.name = "pelican";

  const profile = [
    new THREE.Vector2(0.001, -0.54),
    new THREE.Vector2(0.02, -0.5),
    new THREE.Vector2(0.09, -0.44),
    new THREE.Vector2(0.18, -0.26),
    new THREE.Vector2(0.28, -0.04),
    new THREE.Vector2(0.3, 0.12),
    new THREE.Vector2(0.22, 0.26),
    new THREE.Vector2(0.12, 0.36),
    new THREE.Vector2(0.06, 0.4),
    new THREE.Vector2(0.001, 0.44),
  ];
  const bodyGeo = new THREE.LatheGeometry(profile, 28);
  // +Y is the chest end of the lathe. rotateX(-90°) points it forward (-Z).
  bodyGeo.rotateX(-Math.PI / 2);
  bodyGeo.scale(0.92, 0.86, 1);
  bodyGeo.computeVertexNormals();
  bodyGeo.computeBoundingBox();
  bodyGeo.computeBoundingSphere();
  const body = adopt(new THREE.Mesh(bodyGeo, std(0x8d6a54, 0.86)));
  body.name = "body";
  const bb = bodyGeo.boundingBox;
  body.position.set(
    -(bb.min.x + bb.max.x) / 2,
    deckY + 0.1 - bb.min.y,
    -(bb.min.z + bb.max.z) / 2 + 0.06,
  );
  bird.add(body);

  const tail = new THREE.Group();
  tail.position.set(0, body.position.y + (bb.min.y + bb.max.y) * 0.15, body.position.z + bb.max.z - 0.04);
  const tailMat = std(0x6b4a3c, 0.72);
  const tailGeo = new THREE.BoxGeometry(0.055, 0.012, 0.34);
  for (let i = -2; i <= 2; i++) {
    const f = adopt(new THREE.Mesh(tailGeo, tailMat));
    f.position.set(i * 0.028, 0, 0.12);
    f.rotation.y = i * 0.16;
    tail.add(f);
  }
  bird.add(tail);

  const rightGeo = createWingGeometry();
  const leftGeo = rightGeo.clone();
  leftGeo.scale(-1, 1, 1);
  leftGeo.computeVertexNormals();
  const wingR = createWing(rightGeo, "r");
  const wingL = createWing(leftGeo, "l");
  const geoMidZ = (bb.min.z + bb.max.z) / 2;
  const shoulderZ = body.position.z + geoMidZ + (bb.min.z - geoMidZ) * 0.2;
  const shoulderY = body.position.y + bb.max.y * 0.62;
  wingR.position.set(0.16, shoulderY, shoulderZ);
  wingL.position.set(-0.16, shoulderY, shoulderZ);
  bird.add(wingR, wingL);

  const neck = new THREE.Group();
  neck.position.set(0, body.position.y + bb.max.y - 0.04, body.position.z + bb.min.z + 0.1);
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0.16, -0.02),
    new THREE.Vector3(0, 0.34, 0.07),
    new THREE.Vector3(0, 0.52, -0.02),
    new THREE.Vector3(0, 0.66, -0.16),
  ]);
  const neckGeo = new THREE.TubeGeometry(curve, 28, 0.075, 12, false);
  const neckMesh = adopt(new THREE.Mesh(neckGeo, std(0xcbb9a2, 0.7)));
  neck.add(neckMesh);

  const head = new THREE.Group();
  head.name = "head";
  head.position.copy(curve.getPoint(1));
  const headMesh = adopt(new THREE.Mesh(new THREE.SphereGeometry(0.155, 24, 18), std(0xf4f0e6, 0.66)));
  headMesh.scale.set(1, 0.9, 1.08);
  const crown = adopt(new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 12), std(0xf2d36b, 0.68)));
  crown.scale.set(0.95, 0.42, 0.95);
  crown.position.set(0, 0.09, 0.02);
  const throat = adopt(new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), std(0xf6f1e6, 0.7)));
  throat.scale.set(0.78, 0.65, 0.85);
  throat.position.set(0, -0.07, -0.05);
  head.add(headMesh, crown, throat);

  const beak = adopt(
    new THREE.Mesh(
      createBeakGeometry(),
      new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.4, metalness: 0.02 }),
    ),
  );
  const beakBase = new THREE.Object3D();
  beakBase.name = "beakBase";
  const beakTip = new THREE.Object3D();
  beakTip.name = "beakTip";
  beakTip.position.set(0, -0.02, -0.8);
  const nail = adopt(new THREE.Mesh(new THREE.ConeGeometry(0.028, 0.09, 8), std(0xd4532c, 0.42)));
  nail.position.set(0, -0.045, -0.74);
  nail.rotation.x = Math.PI * 0.15;
  head.add(beak, beakBase, beakTip, nail);

  const pouchGeo = new THREE.SphereGeometry(0.2, 28, 18);
  pouchGeo.scale(0.68, 0.5, 1.55);
  pouchGeo.translate(0, -0.07, -0.3);
  const pouchDeep = new THREE.Color(0xc94a28);
  const pouchLit = new THREE.Color(0xf08a52);
  paint(pouchGeo, (col, x, y) => {
    const u = THREE.MathUtils.clamp((y + 0.22) / 0.28, 0, 1);
    col.copy(pouchDeep).lerp(pouchLit, u);
  });
  pouchGeo.computeVertexNormals();
  const pouch = adopt(
    new THREE.Mesh(
      pouchGeo,
      new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.52, metalness: 0 }),
    ),
  );
  pouch.name = "pouch";
  pouch.position.set(0, -0.02, -0.06);
  head.add(pouch);

  const eyeR = createEye(1);
  const eyeL = createEye(-1);
  head.add(eyeR, eyeL);
  neck.add(head);
  bird.add(neck);

  const legL = createLeg(-0.1, body.position.z - 0.02, 0.2, deckY);
  const legR = createLeg(0.11, body.position.z + 0.2, -0.16, deckY);
  bird.add(legL, legR);

  return { bird, wingL, wingR, neck, head, pouch, eyeL, eyeR, tail };
}

function blinkAmount(t) {
  const x = (t % 3.8) / 3.8;
  const pulse = (center) => {
    const d = Math.abs(x - center);
    if (d > 0.018) return 0;
    const u = 1 - d / 0.018;
    return u * u;
  };
  return Math.max(pulse(0.22), pulse(0.27));
}

export function createSurfer() {
  const rig = new THREE.Group();
  rig.name = "rig";
  const board = createBoard();
  const parts = createBird(board.userData.deckY);
  rig.add(board, parts.bird);

  return {
    rig,
    update(t, pose) {
      const flap =
        Math.sin(t * 1.65) * 0.1 + Math.pow(Math.max(0, Math.sin(t * 0.55)), 10) * 0.16;
      const dihedral = 0.62;
      // The wing silhouette faces the nose. Z rotation lifts the tips into a V
      // without turning that silhouette edge-on to the camera.
      parts.wingR.rotation.z = dihedral + flap - pose.bank * 0.15;
      parts.wingL.rotation.z = -dihedral - flap - pose.bank * 0.15;
      parts.wingR.rotation.y = -0.08;
      parts.wingL.rotation.y = 0.08;

      parts.neck.rotation.y = Math.sin(t * 0.5) * 0.05;
      parts.neck.rotation.z = Math.sin(t * 0.37) * 0.03;
      parts.neck.rotation.x = Math.sin(t * 1.35) * 0.035;

      const pitch = Math.asin(THREE.MathUtils.clamp(pose.forward.y, -1, 1));
      // Positive local X lifts the beak. Subtract pitch so a downhill nose stays level.
      parts.head.rotation.x = -0.16 - pitch * 0.7 + Math.sin(t * 1.3) * 0.025;
      parts.head.rotation.y = Math.sin(t * 0.6) * 0.05;
      // Positive bank rolled the body left; negative Z rotation brings the crown back up.
      parts.head.rotation.z = -pose.bank * 0.72;

      const wobble = Math.sin(t * 4.1) * 0.055 + Math.sin(t * 2.05) * 0.03;
      parts.pouch.scale.set(1, 1 + wobble, 1 + wobble * 0.45);

      const shut = 1 - 0.9 * blinkAmount(t);
      parts.eyeL.scale.y = shut;
      parts.eyeR.scale.y = shut;

      parts.tail.rotation.y = -pose.bank * 0.35;
      parts.tail.rotation.x = Math.sin(t * 1.8) * 0.06;
    },
  };
}
