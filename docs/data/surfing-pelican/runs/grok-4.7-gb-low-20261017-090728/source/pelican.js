import * as THREE from "three";

const palette = {
  body: 0x6d5344,
  bodyDark: 0x3a2d28,
  chest: 0xf4ecdf,
  head: 0xf7f3ea,
  beak: 0xf0b24a,
  beakRidge: 0xc9843a,
  pouch: 0xd98468,
  foot: 0xd08a52,
  board: 0xf2c94b,
  boardDark: 0xd9a63a,
  pad: 0x2c2826,
  fin: 0xef5d3f,
  stringer: 0xfff8ea,
  iris: 0xf2d27a,
  pupil: 0x1a120e,
};

function mat(color, opts = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: opts.roughness ?? 0.72,
    metalness: opts.metalness ?? 0,
    envMapIntensity: opts.envMapIntensity ?? 0.35,
    vertexColors: opts.vertexColors ?? false,
    side: opts.side ?? THREE.FrontSide,
  });
}

function solid(geo, material) {
  const mesh = new THREE.Mesh(geo, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

// Shape is drawn in XY. +Y becomes local -Z (forward), extrude +Z becomes +Y (up).
function layFlat(geo) {
  geo.rotateX(-Math.PI / 2);
  geo.computeVertexNormals();
  return geo;
}

function boardGeometry() {
  const s = new THREE.Shape();
  const nose = 1.32;
  const tail = -1.02;
  s.moveTo(0, nose);
  s.bezierCurveTo(0.18, 0.95, 0.3, 0.45, 0.3, 0.05);
  s.bezierCurveTo(0.3, -0.4, 0.2, tail + 0.25, 0.1, tail);
  s.quadraticCurveTo(0, tail - 0.05, -0.1, tail);
  s.bezierCurveTo(-0.2, tail + 0.25, -0.3, -0.4, -0.3, 0.05);
  s.bezierCurveTo(-0.3, 0.45, -0.18, 0.95, 0, nose);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.065,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.014,
    bevelSegments: 2,
  });
  layFlat(geo);
  geo.computeBoundingBox();
  geo.translate(0, 0.02 - geo.boundingBox.min.y, 0);
  return geo;
}

function wingGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0.02, 0.04);
  s.bezierCurveTo(0.15, 0.22, 0.55, 0.26, 1.05, 0.14);
  s.bezierCurveTo(1.35, 0.08, 1.52, 0.03, 1.62, 0.0);
  s.bezierCurveTo(1.28, -0.03, 1.05, -0.14, 0.62, -0.16);
  s.quadraticCurveTo(0.22, -0.1, 0.02, 0.04);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.028,
    bevelEnabled: true,
    bevelThickness: 0.006,
    bevelSize: 0.006,
    bevelSegments: 1,
  });
  layFlat(geo);
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const near = new THREE.Color(0x7a5b4a);
  const far = new THREE.Color(0x2a221e);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const span = THREE.MathUtils.clamp(pos.getX(i) / 1.62, 0, 1);
    c.copy(near).lerp(far, Math.pow(span, 1.35));
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  return geo;
}

function mirrorSpan(geo) {
  const g = geo.clone();
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) p.setX(i, -p.getX(i));
  g.computeVertexNormals();
  const n = g.attributes.normal;
  let sum = 0;
  for (let i = 0; i < n.count; i++) sum += n.getY(i);
  if (sum < 0) {
    for (let i = 0; i < n.count; i++) {
      n.setXYZ(i, -n.getX(i), -n.getY(i), -n.getZ(i));
    }
  }
  return g;
}

function tailGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.02);
  s.lineTo(0.16, -0.34);
  s.lineTo(0.05, -0.28);
  s.lineTo(0, -0.46);
  s.lineTo(-0.05, -0.28);
  s.lineTo(-0.16, -0.34);
  s.lineTo(0, 0.02);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.02, bevelEnabled: false });
  return layFlat(geo);
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.02);
  s.lineTo(0.1, 0.2);
  s.lineTo(0.03, 0.16);
  s.lineTo(0, 0.28);
  s.lineTo(-0.03, 0.16);
  s.lineTo(-0.1, 0.2);
  s.lineTo(0, 0.02);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.018, bevelEnabled: false });
  return layFlat(geo);
}

export function createPelican() {
  const root = new THREE.Group();
  root.name = "pelican";

  const board = solid(boardGeometry(), mat(palette.board, { roughness: 0.48, envMapIntensity: 0.45 }));
  root.add(board);

  const pad = solid(
    new THREE.BoxGeometry(0.26, 0.012, 0.42),
    mat(palette.pad, { roughness: 0.9 }),
  );
  pad.position.set(0, 0.1, 0.28);
  root.add(pad);

  const stringer = solid(
    new THREE.BoxGeometry(0.02, 0.01, 1.7),
    mat(palette.stringer, { roughness: 0.4 }),
  );
  stringer.position.set(0, 0.1, -0.05);
  root.add(stringer);

  const fin = solid(
    new THREE.BoxGeometry(0.025, 0.16, 0.2),
    mat(palette.fin, { roughness: 0.4, envMapIntensity: 0.5 }),
  );
  fin.position.set(0, -0.02, 0.72);
  fin.rotation.x = -0.25;
  root.add(fin);

  const bodyMat = mat(palette.body, { roughness: 0.78 });
  const body = solid(new THREE.SphereGeometry(1, 28, 20), bodyMat);
  body.scale.set(0.34, 0.27, 0.5);
  body.position.set(0, 0.4, 0.02);
  body.rotation.x = 0.22;
  root.add(body);

  const chest = solid(new THREE.SphereGeometry(1, 20, 16), mat(palette.chest, { roughness: 0.7 }));
  chest.scale.set(0.24, 0.2, 0.26);
  chest.position.set(0, 0.36, -0.22);
  root.add(chest);

  const back = solid(new THREE.SphereGeometry(1, 18, 14), mat(palette.bodyDark, { roughness: 0.8 }));
  back.scale.set(0.22, 0.12, 0.28);
  back.position.set(0, 0.58, 0.08);
  root.add(back);

  const neck1 = new THREE.Group();
  neck1.position.set(0, 0.5, -0.28);
  root.add(neck1);
  const neck1Mesh = solid(
    new THREE.CylinderGeometry(0.08, 0.1, 0.26, 12),
    mat(palette.chest, { roughness: 0.68 }),
  );
  neck1Mesh.rotation.x = -Math.PI / 2;
  neck1Mesh.position.z = -0.13;
  neck1.add(neck1Mesh);

  const neck2 = new THREE.Group();
  neck2.position.set(0, 0, -0.26);
  neck1.add(neck2);
  const neck2Mesh = solid(
    new THREE.CylinderGeometry(0.062, 0.08, 0.22, 12),
    mat(palette.head, { roughness: 0.62 }),
  );
  neck2Mesh.rotation.x = -Math.PI / 2;
  neck2Mesh.position.z = -0.11;
  neck2.add(neck2Mesh);

  const head = new THREE.Group();
  head.position.set(0, 0.01, -0.2);
  neck2.add(head);
  const skull = solid(new THREE.SphereGeometry(0.16, 20, 16), mat(palette.head, { roughness: 0.55 }));
  skull.scale.set(1, 0.92, 1.08);
  head.add(skull);

  const crown = solid(new THREE.SphereGeometry(0.1, 14, 12), mat(palette.bodyDark, { roughness: 0.75 }));
  crown.scale.set(0.85, 0.55, 1.1);
  crown.position.set(0, 0.1, 0.04);
  head.add(crown);

  const beak = new THREE.Group();
  beak.position.set(0, -0.02, -0.1);
  head.add(beak);
  const billLen = 0.72;
  const bill = solid(
    new THREE.CylinderGeometry(0.02, 0.055, billLen, 10),
    mat(palette.beak, { roughness: 0.38, envMapIntensity: 0.55 }),
  );
  bill.rotation.x = -Math.PI / 2;
  bill.position.z = -billLen / 2;
  beak.add(bill);

  const ridge = solid(
    new THREE.CylinderGeometry(0.012, 0.03, billLen * 0.92, 8),
    mat(palette.beakRidge, { roughness: 0.42 }),
  );
  ridge.rotation.x = -Math.PI / 2;
  ridge.position.set(0, 0.028, -billLen * 0.46);
  beak.add(ridge);

  const hook = solid(
    new THREE.ConeGeometry(0.028, 0.09, 8),
    mat(palette.beakRidge, { roughness: 0.4 }),
  );
  hook.rotation.x = Math.PI * 0.92;
  hook.position.set(0, -0.02, -billLen + 0.02);
  beak.add(hook);

  const pouch = solid(new THREE.SphereGeometry(1, 16, 12), mat(palette.pouch, { roughness: 0.62 }));
  pouch.scale.set(0.09, 0.07, 0.3);
  pouch.position.set(0, -0.06, -0.34);
  beak.add(pouch);

  const beakTip = new THREE.Object3D();
  beakTip.name = "beakTip";
  beakTip.position.set(0, -0.03, -billLen);
  beak.add(beakTip);

  function eye(side) {
    const g = new THREE.Group();
    g.position.set(0.105 * side, 0.03, -0.06);
    const ring = solid(new THREE.SphereGeometry(0.048, 12, 10), mat(palette.bodyDark, { roughness: 0.5 }));
    const iris = solid(new THREE.SphereGeometry(0.034, 12, 10), mat(palette.iris, { roughness: 0.35 }));
    iris.position.x = 0.02 * side;
    const pupil = solid(new THREE.SphereGeometry(0.018, 10, 8), mat(palette.pupil, { roughness: 0.3 }));
    pupil.position.x = 0.038 * side;
    const shine = solid(new THREE.SphereGeometry(0.008, 8, 6), mat(0xffffff, { roughness: 0.2 }));
    shine.position.set(0.046 * side, 0.012, -0.01);
    g.add(ring, iris, pupil, shine);
    return g;
  }
  const eyeR = eye(1);
  const eyeL = eye(-1);
  head.add(eyeR, eyeL);

  const wingMat = mat(0xffffff, {
    roughness: 0.78,
    vertexColors: true,
    side: THREE.DoubleSide,
  });
  const wingGeoR = wingGeometry();
  const wingR = new THREE.Group();
  wingR.position.set(0.18, 0.52, -0.02);
  wingR.add(solid(wingGeoR, wingMat));
  root.add(wingR);

  const wingL = new THREE.Group();
  wingL.position.set(-0.18, 0.52, -0.02);
  wingL.add(solid(mirrorSpan(wingGeoR), wingMat));
  root.add(wingL);

  const tail = new THREE.Group();
  tail.position.set(0, 0.4, 0.42);
  tail.add(solid(tailGeometry(), mat(palette.bodyDark, { roughness: 0.8, side: THREE.DoubleSide })));
  root.add(tail);

  const footMat = mat(palette.foot, { roughness: 0.6, side: THREE.DoubleSide });
  const footGeo = footGeometry();
  function limb(side) {
    const leg = solid(new THREE.CylinderGeometry(0.03, 0.038, 0.18, 8), footMat);
    leg.position.set(0.14 * side, 0.2, 0.16);
    root.add(leg);
    const foot = solid(footGeo, footMat);
    foot.position.set(0.14 * side, 0.105, 0.1);
    root.add(foot);
  }
  limb(1);
  limb(-1);

  function update(t, turn) {
    const flap = Math.sin(t * 1.15) * 0.1 + Math.sin(t * 2.5) * 0.03;
    const roll = -turn * 0.2;
    wingR.rotation.z = 0.2 + flap + roll;
    wingL.rotation.z = -0.2 - flap + roll;
    wingR.rotation.y = -0.28;
    wingL.rotation.y = 0.22;
    neck1.rotation.x = 0.42 + Math.sin(t * 2.05) * 0.04;
    neck2.rotation.x = -0.22 + Math.sin(t * 2.05 + 0.7) * 0.035;
    head.rotation.x = -0.16 + Math.sin(t * 2.05 + 0.2) * 0.025;
    head.rotation.y = Math.sin(t * 0.55) * 0.07;
    tail.rotation.x = -0.55 + Math.sin(t * 2.8) * 0.06;
    tail.rotation.y = -turn * 0.45;
    const blink = Math.pow(Math.max(0, Math.sin(t * 0.62)), 48);
    const squish = 1 - blink * 0.9;
    eyeR.scale.y = squish;
    eyeL.scale.y = squish;
  }

  return { root, update, beakTip, head, wingGeoR };
}
