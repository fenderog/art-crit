import * as THREE from "three";

const plumage = new THREE.MeshPhysicalMaterial({
  color: 0x6d5648,
  roughness: 0.72,
  metalness: 0,
  sheen: 0.55,
  sheenColor: new THREE.Color(0xd8c2a4),
  sheenRoughness: 0.5,
});
const bellyMat = new THREE.MeshPhysicalMaterial({
  color: 0x8a6d58,
  roughness: 0.7,
  metalness: 0,
  sheen: 0.4,
  sheenColor: new THREE.Color(0xe6d2b8),
  sheenRoughness: 0.55,
});
const neckMat = new THREE.MeshPhysicalMaterial({
  color: 0xf4ecda,
  roughness: 0.62,
  metalness: 0,
  sheen: 0.7,
  sheenColor: new THREE.Color(0xfff6e8),
  sheenRoughness: 0.4,
});
const headMat = neckMat;
const napeMat = new THREE.MeshStandardMaterial({ color: 0x7a4630, roughness: 0.74 });
const covertMat = new THREE.MeshPhysicalMaterial({
  color: 0x8b8174,
  roughness: 0.68,
  metalness: 0,
  sheen: 0.45,
  sheenColor: new THREE.Color(0xe4d8c8),
  sheenRoughness: 0.5,
  side: THREE.DoubleSide,
});
const primaryMat = new THREE.MeshStandardMaterial({
  color: 0x23272b,
  roughness: 0.55,
  side: THREE.DoubleSide,
});
const beakMat = new THREE.MeshPhysicalMaterial({
  color: 0xe0a63a,
  roughness: 0.38,
  metalness: 0.02,
  clearcoat: 0.28,
  clearcoatRoughness: 0.4,
});
const beakLowMat = new THREE.MeshPhysicalMaterial({
  color: 0xc9843c,
  roughness: 0.45,
  metalness: 0,
  clearcoat: 0.15,
  clearcoatRoughness: 0.5,
});
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xd4893e, roughness: 0.52 });
const knobMat = new THREE.MeshStandardMaterial({ color: 0xf0c15a, roughness: 0.42 });
const feetMat = new THREE.MeshStandardMaterial({ color: 0x2c3134, roughness: 0.6 });
const deckMat = new THREE.MeshStandardMaterial({ color: 0xf3eee4, roughness: 0.45 });
const railMat = new THREE.MeshStandardMaterial({ color: 0xe15b3a, roughness: 0.4 });
const stringerMat = new THREE.MeshStandardMaterial({ color: 0x1b6e78, roughness: 0.35 });
const padMat = new THREE.MeshStandardMaterial({ color: 0x2a3338, roughness: 0.85 });
const finMat = new THREE.MeshStandardMaterial({ color: 0x143e44, roughness: 0.4 });
const eyeMat = new THREE.MeshStandardMaterial({
  color: 0xf0d35a,
  roughness: 0.25,
  metalness: 0.05,
});
const pupilMat = new THREE.MeshBasicMaterial({ color: 0x14120f });
const catchMat = new THREE.MeshBasicMaterial({ color: 0xfffaf2 });

function mesh(parent, geo, mat, x, y, z) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  parent.add(m);
  return m;
}

function boardGeometry() {
  const s = new THREE.Shape();
  // CCW in XY, nose at +y. After Rx(-π/2), +y maps to -z, the board's nose.
  s.moveTo(0, 1.62);
  s.bezierCurveTo(-0.15, 1.46, -0.34, 0.72, -0.33, 0.05);
  s.bezierCurveTo(-0.32, -0.72, -0.2, -1.22, -0.05, -1.4);
  s.quadraticCurveTo(0, -1.5, 0.05, -1.4);
  s.bezierCurveTo(0.2, -1.22, 0.32, -0.72, 0.33, 0.05);
  s.bezierCurveTo(0.34, 0.72, 0.15, 1.46, 0, 1.62);
  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.085,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.016,
    bevelSegments: 2,
    curveSegments: 12,
  });
  geo.translate(0, 0, -0.042);
  geo.rotateX(-Math.PI / 2);
  geo.computeBoundingBox();
  geo.translate(0, -geo.boundingBox.min.y + 0.02, 0);
  return geo;
}

function wingGeometry(side) {
  const s = side;
  const sh = new THREE.Shape();
  // +shape y becomes -z (forward) after Rx(-π/2). Tip extends along ±x.
  sh.moveTo(0, 0.06);
  sh.bezierCurveTo(s * 0.28, 0.2, s * 0.78, 0.14, s * 1.18, 0.0);
  sh.lineTo(s * 1.28, -0.05);
  sh.bezierCurveTo(s * 0.82, -0.22, s * 0.32, -0.28, 0, -0.12);
  sh.closePath();
  const geo = new THREE.ExtrudeGeometry(sh, {
    depth: 0.1,
    bevelEnabled: false,
    curveSegments: 8,
  });
  geo.translate(0, 0, -0.05);
  geo.rotateX(-Math.PI / 2);
  return geo;
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.1);
  s.bezierCurveTo(-0.16, 0.12, -0.2, 0.0, -0.12, -0.14);
  s.bezierCurveTo(-0.04, -0.18, 0.04, -0.18, 0.12, -0.14);
  s.bezierCurveTo(0.2, 0.0, 0.16, 0.12, 0, 0.1);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.018, bevelEnabled: false });
  geo.translate(0, 0, -0.009);
  geo.rotateX(-Math.PI / 2);
  return geo;
}

function limb(parent, a, b, radius, mat) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(radius, radius * 1.08, len, 8);
  const m = new THREE.Mesh(geo, mat);
  m.position.copy(a).add(b).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  parent.add(m);
  return m;
}

function makeEye(parent, x) {
  const g = new THREE.Group();
  g.position.set(x, 0.045, -0.15);
  const ball = mesh(g, new THREE.SphereGeometry(0.048, 14, 12), eyeMat, 0, 0, 0);
  const pupil = mesh(g, new THREE.SphereGeometry(0.022, 10, 8), pupilMat, 0, 0, -0.034);
  mesh(g, new THREE.SphereGeometry(0.01, 8, 6), catchMat, 0.014, 0.014, -0.04);
  parent.add(g);
  return { group: g, ball, pupil };
}

function makeWing() {
  const wing = new THREE.Group();
  wing.add(new THREE.Mesh(wingGeometry(1), covertMat));
  // Dark primaries fanned at the tip. The left wing is a mirrored clone.
  for (let i = 0; i < 4; i++) {
    const f = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.032, 0.09), primaryMat);
    f.position.set(0.9 + i * 0.04, 0.02, -0.04 + i * 0.06);
    f.rotation.y = 0.2 - i * 0.18;
    wing.add(f);
  }
  wing.position.set(0.28, 0.9, -0.02);
  return wing;
}

export function createPelican() {
  const root = new THREE.Group();
  const boardGeo = boardGeometry();
  const deck = new THREE.Mesh(boardGeo, deckMat);
  root.add(deck);
  const rail = new THREE.Mesh(boardGeo, railMat);
  rail.scale.set(1.045, 0.62, 1.03);
  rail.position.y = 0.012;
  root.add(rail);

  const top = boardGeo.boundingBox.max.y + 0.004;
  const stringer = mesh(root, new THREE.BoxGeometry(0.028, 0.01, 2.55), stringerMat, 0, top, 0.05);
  mesh(root, new THREE.BoxGeometry(0.4, 0.008, 0.72), padMat, 0, top, 0.58);
  const fin = mesh(root, new THREE.BoxGeometry(0.028, 0.14, 0.2), finMat, 0, 0.0, 0.98);
  fin.rotation.x = -0.35;

  const blobMap = softDisc();
  const blob = new THREE.Mesh(
    new THREE.CircleGeometry(0.7, 24),
    new THREE.MeshBasicMaterial({
      map: blobMap,
      transparent: true,
      depthWrite: false,
      color: 0x042430,
      opacity: 0.55,
    }),
  );
  blob.rotation.x = -Math.PI / 2;
  blob.position.y = 0.03;
  blob.scale.set(1.15, 1.6, 1);
  root.add(blob);

  const nose = new THREE.Object3D();
  nose.position.set(0, top, -1.55);
  const tailMark = new THREE.Object3D();
  tailMark.position.set(0, top, 1.35);
  root.add(nose, tailMark);

  const footGeo = footGeometry();
  const feet = [
    { x: -0.12, z: -0.02 },
    { x: 0.13, z: 0.22 },
  ];
  for (const f of feet) {
    const foot = new THREE.Mesh(footGeo, feetMat);
    foot.position.set(f.x, top + 0.01, f.z);
    root.add(foot);
  }

  const pivot = new THREE.Group();
  pivot.position.set(0, 0.42, 0.08);
  root.add(pivot);

  // Body parts are parented to root first (identity), then attached to pivot
  // so banking rotates them around the hips and the feet stay on the deck.
  const bodyParts = [];
  const body = mesh(root, new THREE.SphereGeometry(0.4, 28, 20), plumage, 0, 0.7, 0.1);
  body.scale.set(0.78, 0.66, 1.22);
  bodyParts.push(body);

  const belly = mesh(root, new THREE.SphereGeometry(0.28, 20, 16), bellyMat, 0, 0.58, -0.22);
  belly.scale.set(0.85, 0.72, 0.85);
  bodyParts.push(belly);

  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.82, -0.12),
    new THREE.Vector3(0, 1.02, -0.22),
    new THREE.Vector3(0, 1.2, -0.46),
    new THREE.Vector3(0, 1.24, -0.66),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(curve, 18, 0.1, 10, false), neckMat);
  root.add(neck);
  bodyParts.push(neck);

  for (const spread of [-0.22, 0, 0.22]) {
    const feather = mesh(root, new THREE.BoxGeometry(0.14, 0.018, 0.42), plumage, 0, 0.74, 0.62);
    feather.rotation.y = spread;
    feather.rotation.x = 0.35;
    bodyParts.push(feather);
  }

  const head = new THREE.Group();
  head.position.set(0, 1.26, -0.74);
  const skull = mesh(head, new THREE.SphereGeometry(0.2, 22, 16), headMat, 0, 0, 0);
  skull.scale.set(1, 0.92, 1.08);
  const cap = mesh(head, new THREE.SphereGeometry(0.19, 16, 12), napeMat, 0, 0.05, 0.06);
  cap.scale.set(0.92, 0.62, 0.78);

  const upper = mesh(head, new THREE.CylinderGeometry(0.026, 0.058, 0.92, 14), beakMat, 0, -0.02, -0.5);
  upper.rotation.x = -Math.PI / 2 - 0.2;
  const lower = mesh(
    head,
    new THREE.CylinderGeometry(0.016, 0.036, 0.55, 12),
    beakLowMat,
    0,
    -0.07,
    -0.36,
  );
  lower.rotation.x = -Math.PI / 2 - 0.28;

  const pouch = mesh(head, new THREE.SphereGeometry(0.18, 20, 14), pouchMat, 0, -0.14, -0.4);
  pouch.scale.set(0.7, 0.9, 1.2);

  const knob = mesh(head, new THREE.SphereGeometry(0.04, 10, 8), knobMat, 0, 0.06, -0.55);
  knob.scale.set(0.7, 0.9, 1.15);

  const eyeL = makeEye(head, -0.095);
  const eyeR = makeEye(head, 0.095);
  const beakTip = new THREE.Object3D();
  beakTip.position.set(0, -0.12, -1.02);
  head.add(beakTip);

  root.add(head);
  bodyParts.push(head);

  const wingR = makeWing();
  const wingL = wingR.clone();
  wingL.scale.x = -1;
  wingL.position.x = -0.28;
  // Wings stay on the board, not the banking torso, so a carve cannot
  // stand one wing edge-on to the chase camera.
  root.add(wingR, wingL);

  for (const part of bodyParts) pivot.attach(part);

  // Short dark legs from the deck up into the body, left on the root so they
  // stay planted when the torso banks.
  limb(root, new THREE.Vector3(-0.12, top + 0.02, -0.02), new THREE.Vector3(-0.1, 0.4, -0.02), 0.035, feetMat);
  limb(root, new THREE.Vector3(0.13, top + 0.02, 0.22), new THREE.Vector3(0.1, 0.4, 0.12), 0.035, feetMat);

  return {
    root,
    pivot,
    wingL,
    wingR,
    head,
    pouch,
    eyeL,
    eyeR,
    nose,
    tailMark,
    beakTip,
    stringer,
  };
}

export function posePelican(rig, t, ride) {
  rig.pivot.rotation.order = "YXZ";
  rig.pivot.rotation.x = ride.pitch;
  rig.pivot.rotation.z = ride.bank;
  rig.pivot.rotation.y = ride.bank * -0.12;

  const flap =
    Math.sin(t * 1.3) * 0.04 +
    Math.max(0, Math.sin(t * 0.55)) ** 8 * Math.sin(t * 9.0) * 0.28;
  const open = 0.08 * ride.lip;
  // Shallow dihedral, almost no sweep: the chase camera looks down the
  // chord, and a big yaw turns one wing into a line.
  const lift = 0.18 + flap * 0.55 + open * 0.2;
  rig.wingR.rotation.order = "YXZ";
  rig.wingL.rotation.order = "YXZ";
  rig.wingR.rotation.set(0.04, -0.12, lift);
  rig.wingL.rotation.set(0.04, -0.12, lift);

  rig.head.rotation.x = -0.06 + Math.sin(t * 1.6) * 0.035 - ride.pitch * 0.25;
  rig.head.rotation.z = -ride.bank * 0.3;
  rig.head.rotation.y = Math.sin(t * 0.8) * 0.04;

  const py = 0.9 + Math.sin(t * 2.1) * 0.035;
  rig.pouch.scale.set(0.7, py, 1.2);

  const blink = Math.max(0, Math.sin(t * 0.47)) ** 48;
  const sy = 1 - blink * 0.92;
  rig.eyeL.ball.scale.y = sy;
  rig.eyeR.ball.scale.y = sy;
}

function softDisc() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 4, 32, 32, 32);
  grd.addColorStop(0, "rgba(255,255,255,0.85)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function sprayTexture() {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 64;
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 1, 32, 32, 30);
  grd.addColorStop(0, "rgba(255,255,255,0.95)");
  grd.addColorStop(0.45, "rgba(255,255,255,0.35)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
