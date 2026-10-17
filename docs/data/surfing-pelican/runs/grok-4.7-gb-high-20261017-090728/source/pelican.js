import * as THREE from "three";
import { WORLD_UP, composeRootQuaternion } from "./frame.js";

const DECK_Y = 0.09;

const _upright = new THREE.Quaternion();
const _blended = new THREE.Quaternion();
const _aim = new THREE.Vector3();
const _hipW = new THREE.Vector3();
const _delta = new THREE.Vector3();
const _dir = new THREE.Vector3();
const _tangent = new THREE.Vector3();
const _right = new THREE.Vector3();
const _up = new THREE.Vector3();
const _point = new THREE.Vector3();
const _neckColor = new THREE.Color();
const _brown = new THREE.Color(0x6a4532);
const _cream = new THREE.Color(0xf4f0e4);
const _m = new THREE.Matrix4();
const _invQ = new THREE.Quaternion();
const _axisX = new THREE.Vector3();
const _axisY = new THREE.Vector3();
const _axisZ = new THREE.Vector3();
const _side = new THREE.Vector3();
const Y_AXIS = new THREE.Vector3(0, 1, 0);

function std(color, roughness, extra = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness,
    metalness: 0,
    ...extra,
  });
}

function coat(color, roughness, clearcoat = 0.35) {
  return new THREE.MeshPhysicalMaterial({
    color,
    roughness,
    metalness: 0,
    clearcoat,
    clearcoatRoughness: 0.4,
  });
}

function shade(mesh, cast = true) {
  mesh.castShadow = cast;
  mesh.receiveShadow = true;
  return mesh;
}

function bodyGeometry() {
  const g = new THREE.SphereGeometry(1, 40, 28);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i);
    let y = p.getY(i);
    let z = p.getZ(i);
    const tail = Math.max(0, z);
    const breast = Math.max(0, -z);
    x *= 0.4 - tail * 0.05;
    y = y * (0.34 + breast * 0.04) - 0.015;
    if (y < 0) y *= 0.88;
    z = z * 0.58 + tail * tail * 0.22;
    p.setXYZ(i, x, y, z);
  }
  g.computeVertexNormals();
  return g;
}

// Broad side faces local ±X. After the bird turns to travel +X, that is the side camera.
function profileFeather(length, width) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(width * 0.9, length * 0.06, width * 0.45, length * 0.48, width * 0.08, length * 0.9);
  s.quadraticCurveTo(0, length * 1.02, -width * 0.05, length * 0.78);
  s.bezierCurveTo(-width * 0.28, length * 0.42, -width * 0.16, length * 0.08, 0, 0);
  const g = new THREE.ShapeGeometry(s, 6);
  g.rotateY(Math.PI / 2);
  return g;
}

function mandibleGeometry({ length, baseW, tipW, baseH, tipH, droop, hook, upper }) {
  const seg = 16;
  const sides = 9;
  const positions = [];
  const indices = [];
  let tipY = 0;
  for (let i = 0; i <= seg; i++) {
    const t = i / seg;
    const z = -t * length;
    const width = baseW + (tipW - baseW) * Math.pow(t, 0.8);
    const height = baseH + (tipH - baseH) * t;
    const hookT = upper ? Math.pow(Math.max(0, (t - 0.72) / 0.28), 2) : 0;
    const y0 = -droop * t * t - hook * hookT;
    if (i === seg) tipY = y0;
    for (let s = 0; s < sides; s++) {
      const a = (s / sides) * Math.PI * 2;
      const ex = Math.cos(a) * width;
      let ey = Math.sin(a) * height;
      if (upper && ey < 0) ey *= 0.32;
      if (!upper && ey > 0) ey *= 0.38;
      positions.push(ex, y0 + ey, z);
    }
  }
  for (let i = 0; i < seg; i++) {
    for (let s = 0; s < sides; s++) {
      const a = i * sides + s;
      const b = i * sides + ((s + 1) % sides);
      const c = (i + 1) * sides + s;
      const d = (i + 1) * sides + ((s + 1) % sides);
      indices.push(a, c, b, b, c, d);
    }
  }
  const tip = positions.length / 3;
  positions.push(0, tipY, -length);
  const last = seg * sides;
  for (let s = 0; s < sides; s++) {
    indices.push(tip, last + ((s + 1) % sides), last + s);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  g.setIndex(indices);
  g.computeVertexNormals();
  return g;
}

function pouchGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(0.14, -0.18, 0.38, -0.28, 0.58, -0.12);
  s.quadraticCurveTo(0.7, -0.03, 0.64, 0);
  s.lineTo(0, 0);
  const g = new THREE.ExtrudeGeometry(s, {
    depth: 0.2,
    bevelEnabled: true,
    bevelThickness: 0.025,
    bevelSize: 0.02,
    bevelSegments: 2,
    curveSegments: 8,
  });
  g.translate(0, 0, -0.1);
  g.rotateY(Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

function boardGeometry() {
  const L = 2.85;
  const mid = 0.3;
  const nose = L / 2;
  const tail = -L / 2;
  const shape = new THREE.Shape();
  shape.moveTo(0, nose);
  shape.bezierCurveTo(0.07, nose - 0.12, mid, nose * 0.32, mid, 0.02);
  shape.bezierCurveTo(mid, -0.42, mid * 0.7, tail + 0.32, 0.055, tail);
  shape.lineTo(-0.055, tail);
  shape.bezierCurveTo(-mid * 0.7, tail + 0.32, -mid, -0.42, -mid, 0.02);
  shape.bezierCurveTo(-mid, nose * 0.32, -0.07, nose - 0.12, 0, nose);

  const g = new THREE.ExtrudeGeometry(shape, {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.01,
    bevelSize: 0.012,
    bevelSegments: 2,
    curveSegments: 10,
    steps: 1,
  });
  g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const z = p.getZ(i);
    const nz = z / (L / 2);
    const rocker = 0.07 * nz * nz + Math.pow(Math.max(0, -nz), 2) * 0.05;
    p.setY(i, p.getY(i) + rocker);
  }
  g.computeBoundingBox();
  const lift = 0.012 - g.boundingBox.min.y;
  g.translate(0, lift, 0);
  g.computeBoundingBox();

  const deck = new THREE.Color(0xf4f1e8);
  const noseColor = new THREE.Color(0xe06a3a);
  const colors = new Float32Array(p.count * 3);
  const c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const z = p.getZ(i);
    const k = 1 - THREE.MathUtils.smoothstep(z, -1.2, -0.35);
    c.copy(deck).lerp(noseColor, k);
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  g.computeVertexNormals();
  return g;
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.02);
  s.lineTo(0.1, 0.2);
  s.lineTo(0.045, 0.18);
  s.lineTo(0.015, 0.3);
  s.lineTo(-0.015, 0.18);
  s.lineTo(-0.05, 0.2);
  s.lineTo(-0.11, 0.16);
  s.lineTo(-0.02, 0.02);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.022, bevelEnabled: false, curveSegments: 2 });
  g.rotateX(-Math.PI / 2);
  g.computeVertexNormals();
  return g;
}

function createNeckGeometry(rings, sides) {
  const count = (rings + 1) * sides;
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  const indices = [];
  for (let i = 0; i < rings; i++) {
    for (let s = 0; s < sides; s++) {
      const a = i * sides + s;
      const b = i * sides + ((s + 1) % sides);
      const c = (i + 1) * sides + s;
      const d = (i + 1) * sides + ((s + 1) % sides);
      indices.push(a, c, b, b, c, d);
    }
  }
  g.setIndex(indices);
  g.userData.rings = rings;
  g.userData.sides = sides;
  return g;
}

function neckRadius(t) {
  if (t < 0.55) return 0.15 + (0.12 - 0.15) * (t / 0.55);
  return 0.12 + (0.085 - 0.12) * ((t - 0.55) / 0.45);
}

function writeNeck(geo, curve) {
  const rings = geo.userData.rings;
  const sides = geo.userData.sides;
  const pos = geo.attributes.position;
  const color = geo.attributes.color;
  let vi = 0;
  for (let i = 0; i <= rings; i++) {
    const t = i / rings;
    curve.getPointAt(t, _point);
    curve.getTangentAt(t, _tangent).normalize();
    _right.crossVectors(_tangent, WORLD_UP);
    if (_right.lengthSq() < 1e-6) _right.set(1, 0, 0);
    _right.normalize();
    _up.crossVectors(_right, _tangent).normalize();
    const radius = neckRadius(t);
    const k = THREE.MathUtils.smoothstep(t, 0.22, 0.82);
    _neckColor.copy(_brown).lerp(_cream, k);
    for (let s = 0; s < sides; s++) {
      const a = (s / sides) * Math.PI * 2;
      const cx = Math.cos(a) * radius;
      const sy = Math.sin(a) * radius;
      pos.setXYZ(
        vi,
        _point.x + _right.x * cx + _up.x * sy,
        _point.y + _right.y * cx + _up.y * sy,
        _point.z + _right.z * cx + _up.z * sy,
      );
      color.setXYZ(vi, _neckColor.r, _neckColor.g, _neckColor.b);
      vi++;
    }
  }
  pos.needsUpdate = true;
  color.needsUpdate = true;
  geo.computeVertexNormals();
}

function orientHead(head, forward) {
  _aim.copy(forward).normalize();
  _right.crossVectors(_aim, WORLD_UP);
  if (_right.lengthSq() < 1e-6) _right.set(1, 0, 0);
  _right.normalize();
  // up = right × forward. Check: forward (0,0,−1) → right (1,0,0), up (0,1,0).
  _up.crossVectors(_right, _aim).normalize();
  _tangent.copy(_aim).negate();
  _m.makeBasis(_right, _up, _tangent);
  head.quaternion.setFromRotationMatrix(_m);
}

function stretchBone(mesh, from, to) {
  _delta.subVectors(to, from);
  const len = Math.max(0.04, _delta.length());
  mesh.position.copy(from).addScaledVector(_delta, 0.5);
  _dir.copy(_delta).multiplyScalar(1 / len);
  mesh.quaternion.setFromUnitVectors(Y_AXIS, _dir);
  mesh.scale.set(1, len, 1);
}

// Shape +X becomes local −Z after rotateY, which orientWing maps to the tail.
function wingSilhouette() {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.bezierCurveTo(0.22, 0.26, 0.7, 0.58, 1.28, 0.7);
  s.quadraticCurveTo(1.62, 0.76, 1.7, 0.52);
  s.quadraticCurveTo(1.58, 0.34, 1.26, 0.3);
  s.bezierCurveTo(0.86, 0.16, 0.62, 0.24, 0.48, 0.06);
  s.bezierCurveTo(0.3, 0.16, 0.16, 0.04, 0.0, -0.03);
  s.closePath();
  const g = new THREE.ShapeGeometry(s, 10);
  g.rotateY(Math.PI / 2);
  return g;
}

function createWing(side, materials) {
  const wing = new THREE.Group();
  const flap = new THREE.Group();
  wing.add(flap);
  wing.userData.flap = flap;
  wing.userData.side = side;
  const main = shade(new THREE.Mesh(wingSilhouette(), materials.feather), false);
  flap.add(main);
  const covert = shade(new THREE.Mesh(wingSilhouette(), materials.featherMid), false);
  covert.scale.set(1, 0.58, 0.55);
  covert.position.set(0.016, 0.03, 0);
  flap.add(covert);
  return wing;
}

export function createPelican() {
  const materials = {
    body: std(0x6b4634, 0.78),
    bodyDark: std(0x3c2b22, 0.84),
    belly: std(0x8d6249, 0.8),
    head: std(0xf3efe4, 0.62),
    crown: std(0xf0d48a, 0.58),
    nape: std(0xf7f3ea, 0.7, { side: THREE.DoubleSide }),
    feather: std(0x3a2a22, 0.76, { side: THREE.DoubleSide }),
    featherMid: std(0x8a5a3c, 0.7, { side: THREE.DoubleSide }),
    bill: coat(0xe0ae4e, 0.42, 0.45),
    billLow: coat(0xc9923e, 0.48, 0.3),
    pouch: coat(0xd2654e, 0.38, 0.55),
    mouth: std(0x4a1a22, 0.72),
    foot: std(0xf0c15a, 0.64),
    pupil: std(0x140e0a, 0.35),
    iris: std(0xd9a24a, 0.4),
    sclera: std(0xf7f4ee, 0.45),
    ring: std(0xf2d48a, 0.5),
    glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
    pad: std(0xd85a3c, 0.92),
    stringer: std(0xd7b48a, 0.55),
    fin: std(0x1b3038, 0.4),
    leash: std(0x1a1a1a, 0.55),
    board: std(0xffffff, 0.46, { vertexColors: true }),
  };
  materials.pouch.emissive = new THREE.Color(0x6a241c);
  materials.pouch.emissiveIntensity = 0.05;

  const root = new THREE.Group();
  root.name = "pelican";

  const board = new THREE.Group();
  const deck = shade(new THREE.Mesh(boardGeometry(), materials.board));
  board.add(deck);
  const pad = shade(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.01, 0.72), materials.pad), false);
  pad.position.set(0, DECK_Y + 0.004, 0.08);
  board.add(pad);
  const stringer = shade(new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.006, 2.15), materials.stringer), false);
  stringer.position.set(0, DECK_Y + 0.002, -0.05);
  board.add(stringer);
  const fin = shade(new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.16, 0.2), materials.fin));
  fin.position.set(0, -0.05, 1.0);
  fin.rotation.x = 0.25;
  board.add(fin);
  const leash = shade(
    new THREE.Mesh(
      new THREE.TubeGeometry(
        new THREE.CatmullRomCurve3([
          new THREE.Vector3(0.14, DECK_Y + 0.02, 0.18),
          new THREE.Vector3(0.22, 0.16, 0.5),
          new THREE.Vector3(0.06, 0.08, 0.86),
          new THREE.Vector3(0, 0.04, 1.12),
        ]),
        18,
        0.008,
        5,
        false,
      ),
      materials.leash,
    ),
    false,
  );
  board.add(leash);
  root.add(board);

  const tailAnchor = new THREE.Object3D();
  tailAnchor.position.set(0, 0.12, 1.18);
  board.add(tailAnchor);
  const railAnchor = new THREE.Object3D();
  railAnchor.position.set(-0.28, 0.1, 0.15);
  board.add(railAnchor);

  const footL = shade(new THREE.Mesh(footGeometry(), materials.foot));
  footL.position.set(-0.28, DECK_Y, -0.48);
  footL.rotation.y = 0.35;
  footL.scale.setScalar(1.9);
  const footR = shade(new THREE.Mesh(footGeometry(), materials.foot));
  footR.position.set(0.24, DECK_Y, 0.02);
  footR.rotation.y = -0.2;
  footR.scale.setScalar(1.75);
  root.add(footL, footR);

  const torso = new THREE.Group();
  root.add(torso);

  const body = shade(new THREE.Mesh(bodyGeometry(), materials.body));
  body.position.set(0, 0.5, 0.02);
  torso.add(body);
  const mantle = shade(new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 14), materials.body));
  mantle.scale.set(1.2, 0.5, 1.35);
  mantle.position.set(0, 0.66, 0.12);
  torso.add(mantle);
  const belly = shade(new THREE.Mesh(new THREE.SphereGeometry(0.22, 18, 14), materials.belly));
  belly.scale.set(1.05, 0.85, 1.15);
  belly.position.set(0, 0.4, -0.22);
  torso.add(belly);
  const rump = shade(new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 10), materials.body));
  rump.scale.set(1.05, 0.7, 1.45);
  rump.position.set(0, 0.46, 0.52);
  torso.add(rump);

  const neckGeo = createNeckGeometry(14, 10);
  const neck = shade(new THREE.Mesh(neckGeo, std(0xffffff, 0.7, { vertexColors: true })));
  torso.add(neck);
  const neckPoints = [
    new THREE.Vector3(),
    new THREE.Vector3(),
    new THREE.Vector3(),
    new THREE.Vector3(),
  ];
  const neckCurve = new THREE.CatmullRomCurve3(neckPoints, false, "catmullrom", 0.35);

  const head = new THREE.Group();
  torso.add(head);
  const cranium = shade(new THREE.Mesh(new THREE.SphereGeometry(0.155, 28, 20), materials.head));
  cranium.scale.set(1.02, 0.9, 1.16);
  head.add(cranium);
  const crown = shade(
    new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 22, 14, 0, Math.PI * 2, 0, Math.PI * 0.52),
      materials.crown,
    ),
  );
  crown.scale.set(0.98, 0.82, 1.08);
  crown.position.y = 0.02;
  head.add(crown);

  function createEye(side) {
    const eye = new THREE.Group();
    const ring = shade(new THREE.Mesh(new THREE.SphereGeometry(0.058, 14, 10), materials.ring), false);
    ring.scale.set(1.15, 1.08, 0.55);
    const sclera = shade(new THREE.Mesh(new THREE.SphereGeometry(0.062, 16, 12), materials.sclera), false);
    sclera.position.z = -0.02;
    const iris = shade(new THREE.Mesh(new THREE.SphereGeometry(0.032, 12, 8), materials.iris), false);
    iris.position.z = -0.05;
    const pupil = shade(new THREE.Mesh(new THREE.SphereGeometry(0.016, 10, 8), materials.pupil), false);
    pupil.position.z = -0.066;
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.008, 8, 6), materials.glint);
    glint.castShadow = false;
    glint.position.set(side * 0.01, 0.012, -0.07);
    const brow = shade(new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 8), materials.bodyDark), false);
    brow.scale.set(1.25, 0.32, 0.45);
    brow.position.set(0, 0.05, -0.01);
    eye.add(ring, sclera, iris, pupil, glint, brow);
    eye.position.set(side * 0.148, 0.02, -0.1);
    eye.rotation.y = -side * 0.42;
    return eye;
  }
  const eyeL = createEye(-1);
  const eyeR = createEye(1);
  head.add(eyeL, eyeR);

  const mouth = shade(new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 10), materials.mouth), false);
  mouth.scale.set(0.9, 0.7, 0.8);
  mouth.position.set(0, -0.02, -0.14);
  head.add(mouth);

  const upperPivot = new THREE.Group();
  upperPivot.position.set(0, 0.015, -0.1);
  const upper = shade(new THREE.Mesh(mandibleGeometry({
    length: 0.9,
    baseW: 0.072,
    tipW: 0.011,
    baseH: 0.05,
    tipH: 0.012,
    droop: 0.05,
    hook: 0.11,
    upper: true,
  }), materials.bill));
  upper.name = "upperBill";
  upperPivot.add(upper);
  const nostrilL = shade(new THREE.Mesh(new THREE.SphereGeometry(0.01, 8, 6), materials.pupil), false);
  nostrilL.scale.set(1.3, 0.65, 0.8);
  nostrilL.position.set(0.04, 0.028, -0.16);
  const nostrilR = nostrilL.clone();
  nostrilR.position.x = -0.04;
  upper.add(nostrilL, nostrilR);
  head.add(upperPivot);

  const lowerPivot = new THREE.Group();
  lowerPivot.position.set(0, -0.02, -0.1);
  const lower = shade(new THREE.Mesh(mandibleGeometry({
    length: 0.82,
    baseW: 0.058,
    tipW: 0.01,
    baseH: 0.03,
    tipH: 0.009,
    droop: 0.02,
    hook: 0,
    upper: false,
  }), materials.billLow));
  lowerPivot.add(lower);
  const pouch = shade(new THREE.Mesh(pouchGeometry(), materials.pouch));
  pouch.scale.set(1, 1, 1);
  pouch.position.set(0, -0.02, -0.06);
  lowerPivot.add(pouch);
  head.add(lowerPivot);

  for (let i = 0; i < 3; i++) {
    const nape = shade(new THREE.Mesh(profileFeather(0.12, 0.035), materials.nape), false);
    nape.rotation.x = 0.35;
    nape.rotation.z = (i - 1) * 0.22;
    nape.position.set((i - 1) * 0.03, 0.06, 0.1);
    head.add(nape);
  }

  const lookAnchor = new THREE.Object3D();
  lookAnchor.position.set(0, 0.42, -0.08);
  head.add(lookAnchor);

  const wingL = createWing(-1, materials);
  wingL.position.set(-0.32, 0.5, 0.0);
  const wingR = createWing(1, materials);
  wingR.position.set(0.28, 0.58, 0.02);
  wingR.scale.setScalar(0.72);
  torso.add(wingL, wingR);

  const tail = new THREE.Group();
  tail.position.set(0, 0.46, 0.58);
  for (let i = 0; i < 4; i++) {
    const feather = shade(new THREE.Mesh(profileFeather(0.34, 0.07), materials.featherMid), false);
    feather.rotation.x = (i - 1.5) * 0.2;
    feather.position.set((i - 1.5) * 0.045, 0.01, 0.04);
    tail.add(feather);
  }
  torso.add(tail);

  const hipL = new THREE.Object3D();
  hipL.position.set(-0.1, 0.34, -0.02);
  const hipR = new THREE.Object3D();
  hipR.position.set(0.12, 0.34, 0.12);
  torso.add(hipL, hipR);
  const hipBallL = shade(new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), materials.foot), false);
  const hipBallR = hipBallL.clone();
  hipL.add(hipBallL);
  hipR.add(hipBallR);

  const legGeo = new THREE.CylinderGeometry(0.032, 0.022, 1, 8);
  const legL = shade(new THREE.Mesh(legGeo, materials.foot));
  const legR = shade(new THREE.Mesh(legGeo, materials.foot));
  root.add(legL, legR);

  function layout(t) {
    const sway = Math.sin(t * 0.85) * 0.035;
    const bob = Math.sin(t * 1.45) * 0.018;
    neckPoints[0].set(0, 0.64, -0.16);
    neckPoints[1].set(sway * 0.35, 0.72, -0.4);
    neckPoints[2].set(sway, 0.9 + bob, -0.66);
    neckPoints[3].set(sway * 0.25, 1.0 + bob, -0.9);
    neckCurve.needsUpdate = true;
    writeNeck(neckGeo, neckCurve);

    _aim.copy(neckPoints[3]).sub(neckPoints[2]);
    _aim.y *= 0.28;
    _aim.x += Math.sin(t * 0.55) * 0.04 - 0.26;
    if (_aim.lengthSq() < 1e-6) _aim.set(0, 0, -1);
    _aim.normalize();
    orientHead(head, _aim);
    head.position.copy(neckPoints[3]).addScaledVector(_aim, 0.16);

    const chatter = Math.pow(Math.max(0, Math.sin(t * 0.62)), 16);
    lowerPivot.rotation.x = -0.2 - chatter * 0.28;
    upperPivot.rotation.x = 0.05 + chatter * 0.08;

    const blink = Math.pow(Math.max(0, Math.sin(t * 0.37)), 28);
    const eyeScale = 1 - blink * 0.92;
    eyeL.scale.y = eyeScale;
    eyeR.scale.y = eyeScale;

    const cycle = t % 5.4;
    const flap = cycle < 0.9 ? Math.sin((cycle / 0.9) * Math.PI) : 0;
    const micro = Math.sin(t * 2.15) * 0.04 + Math.sin(t * 3.4) * 0.018;
    wingL.userData.flap.rotation.x = -0.18 + flap * 0.65 + micro;
    wingR.userData.flap.rotation.x = 0.9 + flap * 0.3 - micro;

    tail.rotation.y = 0;
    tail.rotation.x = 0.62 + Math.sin(t * 1.3) * 0.08;
  }

  function orientWing(wing, forward) {
    composeRootQuaternion(forward, WORLD_UP, _upright);
    // Upright +X is character right. The camera sits on the left, so the
    // visible wing face points along -X of that upright frame.
    _side.set(-1, 0, 0).applyQuaternion(_upright);
    wing.parent.getWorldQuaternion(_invQ);
    _invQ.invert();
    _axisX.copy(_side).applyQuaternion(_invQ).normalize();
    _axisY.copy(WORLD_UP).applyQuaternion(_invQ);
    _axisZ.crossVectors(_axisX, _axisY);
    if (_axisZ.lengthSq() < 1e-6) _axisZ.set(0, 0, 1);
    _axisZ.normalize();
    _axisY.crossVectors(_axisZ, _axisX).normalize();
    _m.makeBasis(_axisX, _axisY, _axisZ);
    wing.quaternion.setFromRotationMatrix(_m);
  }

  function animate(t, forward) {
    torso.quaternion.identity();
    torso.position.y = Math.sin(t * 1.65) * 0.012;
    layout(t);
    root.updateMatrixWorld(true);
    orientWing(wingL, forward);
    orientWing(wingR, forward);
    hipL.getWorldPosition(_hipW);
    root.worldToLocal(_hipW);
    stretchBone(legL, _hipW, footL.position);
    hipR.getWorldPosition(_hipW);
    root.worldToLocal(_hipW);
    stretchBone(legR, _hipW, footR.position);
  }

  animate(0, new THREE.Vector3(1, 0, 0));

  return {
    root,
    head,
    upperBill: upper,
    lookAnchor,
    anchors: { tail: tailAnchor, rail: railAnchor },
    animate,
  };
}
