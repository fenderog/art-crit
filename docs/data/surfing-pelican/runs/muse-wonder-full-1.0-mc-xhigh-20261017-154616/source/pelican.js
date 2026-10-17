import * as THREE from "three";

// Procedural pelican on a longboard. Local axes for the surfing rig:
// +X is direction of travel (board nose), +Y is up, +Z faces the camera.
// The pelican stands surfer-style: feet spread along the board, chest to +Z,
// long beak turned toward +X.

const MAT = {
  feather: new THREE.MeshStandardMaterial({ color: 0xfff6ea, roughness: 0.85 }),
  featherShade: new THREE.MeshStandardMaterial({ color: 0xe9ddc9, roughness: 0.9 }),
  flight: new THREE.MeshStandardMaterial({ color: 0x2e3438, roughness: 0.8 }),
  beak: new THREE.MeshStandardMaterial({ color: 0xff9d2e, roughness: 0.55 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xffb37a, roughness: 0.7 }),
  leg: new THREE.MeshStandardMaterial({ color: 0xd97b36, roughness: 0.8 }),
  eye: new THREE.MeshStandardMaterial({ color: 0x14181a, roughness: 0.25 }),
  coral: new THREE.MeshStandardMaterial({ color: 0xe8503a, roughness: 0.75 }),
  boardSide: new THREE.MeshStandardMaterial({ color: 0xe8503a, roughness: 0.45 }),
  foam: new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 }),
};

function ellipsoid(rx, ry, rz, mat) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), mat);
  m.scale.set(rx, ry, rz);
  m.castShadow = true;
  return m;
}

function tube(points, radius, mat) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
  const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, radius, 12, false), mat);
  m.castShadow = true;
  return m;
}

// ---- surfboard ------------------------------------------------------------

function boardShape() {
  const s = new THREE.Shape();
  s.moveTo(1.75, 0);
  s.bezierCurveTo(1.25, 0.34, 0.2, 0.42, -1.05, 0.36);
  s.bezierCurveTo(-1.55, 0.33, -1.72, 0.18, -1.72, 0);
  s.bezierCurveTo(-1.72, -0.18, -1.55, -0.33, -1.05, -0.36);
  s.bezierCurveTo(0.2, -0.42, 1.25, -0.34, 1.75, 0);
  return s;
}

function deckTexture() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 128;
  const g = c.getContext("2d");
  g.fillStyle = "#fdf3d8"; g.fillRect(0, 0, 512, 128);
  g.fillStyle = "#e8503a"; g.fillRect(0, 44, 512, 40);
  g.fillStyle = "#12808f"; g.fillRect(0, 58, 512, 12);
  g.fillStyle = "#e8503a";
  g.fillRect(0, 6, 512, 8); g.fillRect(0, 114, 512, 8);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function createBoard() {
  const board = new THREE.Group();
  const shape = boardShape();
  const bodyGeo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 24,
  });
  const body = new THREE.Mesh(bodyGeo, MAT.boardSide);
  body.rotation.x = -Math.PI / 2;
  body.position.y = 0.02;
  body.castShadow = true; body.receiveShadow = true;
  board.add(body);

  const deckGeo = new THREE.ShapeGeometry(shape, 24);
  const pos = deckGeo.attributes.position;
  const uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) {
    uv[i * 2] = (pos.getX(i) + 1.75) / 3.5;
    uv[i * 2 + 1] = (pos.getY(i) + 0.42) / 0.84;
  }
  deckGeo.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
  const deck = new THREE.Mesh(deckGeo, new THREE.MeshStandardMaterial({
    map: deckTexture(), roughness: 0.4,
  }));
  deck.rotation.x = -Math.PI / 2;
  deck.position.y = 0.145;
  deck.receiveShadow = true;
  board.add(deck);

  const fin = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.42, 10), MAT.boardSide);
  fin.scale.set(1.4, 1, 0.18);
  fin.rotation.z = Math.PI;
  fin.position.set(-1.25, -0.18, 0);
  board.add(fin);
  return board;
}

// ---- wings ----------------------------------------------------------------
// One wing built extending along +X from its pivot; callers mirror it.

function createWing() {
  const wing = new THREE.Group();
  const arm = ellipsoid(0.62, 0.085, 0.3, MAT.feather);
  arm.position.set(0.55, 0, -0.02);
  arm.rotation.z = -0.08;
  wing.add(arm);
  const covert = ellipsoid(0.4, 0.07, 0.22, MAT.featherShade);
  covert.position.set(0.38, 0.05, -0.06);
  wing.add(covert);
  // black flight feathers fanned at the tip
  for (let i = 0; i < 5; i++) {
    const f = ellipsoid(0.42 - i * 0.02, 0.04, 0.09, MAT.flight);
    const spread = (i - 2) * 0.16;
    f.position.set(1.08 + Math.cos(spread) * 0.12, -0.02, -0.08 + Math.sin(spread) * 0.42);
    f.rotation.y = -spread;
    f.rotation.z = -0.1;
    wing.add(f);
  }
  return wing;
}

// ---- head -----------------------------------------------------------------

function createHead() {
  const head = new THREE.Group(); // origin at skull centre, beak along +X
  const skull = ellipsoid(0.3, 0.25, 0.22, MAT.feather);
  head.add(skull);
  const cheek = ellipsoid(0.2, 0.17, 0.18, MAT.feather);
  cheek.position.set(0.16, -0.06, 0);
  head.add(cheek);

  // swept-back crest
  for (let i = 0; i < 3; i++) {
    const crest = ellipsoid(0.2, 0.045, 0.05, MAT.featherShade);
    crest.position.set(-0.28 - i * 0.05, 0.16 - i * 0.05, (i - 1) * 0.07);
    crest.rotation.z = 0.45;
    head.add(crest);
  }

  // upper beak: long, flattened, gently tapered, with a hooked tip
  const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.105, 1.2, 14), MAT.beak);
  upper.rotation.z = -Math.PI / 2 - 0.06; // cylinder's thin end -> +X, dipping slightly
  upper.scale.set(1, 1, 0.55);
  upper.position.set(0.82, 0.02, 0);
  upper.castShadow = true;
  head.add(upper);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.14, 10), MAT.beak);
  hook.rotation.z = Math.PI;
  hook.position.set(1.42, -0.06, 0);
  head.add(hook);

  // throat pouch + lower beak, in a group so it can sway
  const pouchGroup = new THREE.Group();
  pouchGroup.position.set(0.2, -0.08, 0);
  const pouch = ellipsoid(0.5, 0.24, 0.16, MAT.pouch);
  pouch.position.set(0.42, -0.17, 0);
  pouchGroup.add(pouch);
  const lower = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.05, 1.05, 10), MAT.beak);
  lower.rotation.z = -Math.PI / 2 - 0.16;
  lower.scale.set(1, 1, 0.5);
  lower.position.set(0.52, -0.1, 0);
  pouchGroup.add(lower);
  head.add(pouchGroup);

  // eyes
  const eyes = [];
  for (const side of [1, -1]) {
    const eye = new THREE.Group();
    const ball = new THREE.Mesh(new THREE.SphereGeometry(0.048, 14, 10), MAT.eye);
    eye.add(ball);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.016, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0xffffff }));
    glint.position.set(0.025, 0.025, 0.032 * side);
    eye.add(glint);
    eye.position.set(0.17, 0.07, 0.19 * side);
    head.add(eye);
    eyes.push(ball);
  }
  return { head, pouchGroup, pouch, eyes };
}

// ---- feet -----------------------------------------------------------------

function createFoot() {
  const foot = new THREE.Group(); // toes point +Z
  const pad = ellipsoid(0.15, 0.035, 0.17, MAT.leg);
  pad.position.set(0, 0.03, 0.03);
  foot.add(pad);
  for (let i = -1; i <= 1; i++) {
    const toe = ellipsoid(0.05, 0.028, 0.13, MAT.leg);
    toe.position.set(i * 0.1, 0.025, 0.18);
    toe.rotation.y = -i * 0.35;
    foot.add(toe);
  }
  return foot;
}

// ---- spray ----------------------------------------------------------------

function dropTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.6, "rgba(255,255,255,0.7)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

function createSpray(count = 140) {
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const mat = new THREE.PointsMaterial({
    color: 0xffffff, size: 0.16, transparent: true, opacity: 0.9,
    map: dropTexture(), sizeAttenuation: true, depthWrite: false,
  });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  const drops = [];
  for (let i = 0; i < count; i++) drops.push({ life: Math.random(), vel: new THREE.Vector3() });
  function reset(d) {
    d.life = 0;
    d.vel.set(-1.6 - Math.random() * 1.6, 1 + Math.random() * 1.6, (Math.random() - 0.5) * 0.9);
  }
  drops.forEach((d) => { reset(d); d.life = Math.random(); });
  function update(dt, origin) {
    for (let i = 0; i < drops.length; i++) {
      const d = drops[i];
      d.life += dt / 0.75;
      if (d.life >= 1) reset(d);
      const t = d.life * 0.75;
      positions[i * 3] = origin.x + d.vel.x * t;
      positions[i * 3 + 1] = origin.y + d.vel.y * t - 3.2 * t * t;
      positions[i * 3 + 2] = origin.z + d.vel.z * t;
    }
    geo.attributes.position.needsUpdate = true;
  }
  return { points, update };
}

// ---- the surfer -----------------------------------------------------------

export function createSurfer() {
  const rig = new THREE.Group(); // moves along the wave face
  const board = createBoard();
  rig.add(board);

  // foam collar where board meets water
  const collar = new THREE.Mesh(new THREE.TorusGeometry(1, 0.16, 10, 40), MAT.foam.clone());
  collar.rotation.x = Math.PI / 2;
  collar.scale.set(1.55, 0.42, 0.35);
  collar.position.y = -0.02;
  rig.add(collar);
  const wake = new THREE.Mesh(new THREE.CircleGeometry(1, 24),
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.3, depthWrite: false }));
  wake.rotation.x = -Math.PI / 2;
  wake.scale.set(2.4, 0.55, 1);
  wake.position.set(-2.1, -0.04, 0);
  rig.add(wake);

  const spray = createSpray();
  rig.add(spray.points);

  // feet stay glued to the deck; legs stretch to meet the bobbing body
  const footF = createFoot(); footF.position.set(0.62, 0.14, 0.02); footF.rotation.y = -0.15;
  const footB = createFoot(); footB.position.set(-0.66, 0.14, -0.02); footB.rotation.y = 0.2;
  rig.add(footF, footB);
  const legGeo = new THREE.CylinderGeometry(0.055, 0.07, 1, 10);
  legGeo.translate(0, 0.5, 0); // pivot at ankle, grows along +Y
  const legF = new THREE.Mesh(legGeo, MAT.leg);
  const legB = new THREE.Mesh(legGeo, MAT.leg);
  legF.castShadow = legB.castShadow = true;
  rig.add(legF, legB);

  // body group: everything above the ankles, bobs and leans as one
  const body = new THREE.Group();
  rig.add(body);
  const torso = ellipsoid(0.58, 0.72, 0.48, MAT.feather);
  torso.position.set(0, 0.55, 0);
  body.add(torso);
  const belly = ellipsoid(0.46, 0.55, 0.36, MAT.feather);
  belly.position.set(0.02, 0.42, 0.18);
  body.add(belly);
  const hips = ellipsoid(0.48, 0.3, 0.38, MAT.featherShade);
  hips.position.set(0, 0.1, -0.04);
  body.add(hips);

  // tail fan, pointing back toward the wave
  const tail = new THREE.Group();
  tail.position.set(0, 0.18, -0.42);
  for (let i = 0; i < 5; i++) {
    const f = ellipsoid(0.09, 0.03, 0.34, i % 2 ? MAT.featherShade : MAT.feather);
    const a = (i - 2) * 0.22;
    f.position.set(Math.sin(a) * 0.3, -0.04, -0.28);
    f.rotation.y = a;
    f.rotation.x = 0.35;
    tail.add(f);
  }
  body.add(tail);

  // neck: an S-curve rising from the chest and turning toward travel
  const neck = tube(
    [[0, 0.95, 0.12], [0.02, 1.25, 0.1], [0.12, 1.52, 0.04], [0.3, 1.72, 0], [0.48, 1.82, 0]],
    0.155, MAT.feather);
  body.add(neck);
  const throat = ellipsoid(0.2, 0.34, 0.17, MAT.feather);
  throat.position.set(0.06, 1.25, 0.08);
  body.add(throat);

  const { head, pouchGroup, pouch, eyes } = createHead();
  head.position.set(0.62, 1.88, 0);
  body.add(head);

  // coral neckerchief, with a fluttering tail
  const scarfRing = new THREE.Mesh(new THREE.TorusGeometry(0.19, 0.07, 10, 24), MAT.coral);
  scarfRing.position.set(0.05, 1.42, 0.06);
  scarfRing.rotation.x = Math.PI / 2 - 0.25;
  scarfRing.castShadow = true;
  body.add(scarfRing);
  const scarfTail = new THREE.Group();
  scarfTail.position.set(-0.16, 1.42, 0.1);
  const flap = ellipsoid(0.3, 0.02, 0.13, MAT.coral);
  flap.position.set(-0.26, -0.05, 0);
  scarfTail.add(flap);
  body.add(scarfTail);

  // wings spread for balance: front wing leads low, back wing trails high
  const wingF = createWing();
  wingF.position.set(0.38, 1.02, -0.1);
  body.add(wingF);
  const wingBWrap = new THREE.Group();
  wingBWrap.position.set(-0.38, 1.05, -0.1);
  wingBWrap.rotation.y = Math.PI;
  const wingB = createWing();
  wingBWrap.add(wingB);
  body.add(wingBWrap);

  const UP = new THREE.Vector3(0, 1, 0);
  const ankleF = new THREE.Vector3(0.62, 0.17, 0.02);
  const ankleB = new THREE.Vector3(-0.66, 0.17, -0.02);
  const hipF = new THREE.Vector3(0.3, 0.02, 0.05);
  const hipB = new THREE.Vector3(-0.3, 0.02, -0.05);
  const tmpHip = new THREE.Vector3(), tmpDir = new THREE.Vector3();
  function aimLeg(leg, ankle, hipLocal) {
    leg.position.copy(ankle);
    tmpHip.copy(hipLocal).applyMatrix4(body.matrix); // body-local hip -> rig space
    tmpDir.copy(tmpHip).sub(ankle);
    const len = tmpDir.length();
    leg.quaternion.setFromUnitVectors(UP, tmpDir.normalize());
    leg.scale.set(1, len, 1);
  }

  return {
    group: rig,
    update(t, dt) { updateSurfer(t, dt); },
  };

  function updateSurfer(t, dt) {
    const carve = Math.sin(t * 0.55); // -1 low on the face, +1 high
    const carveVel = Math.cos(t * 0.55);
    // stays on the wave face: higher on the face sits further back (-Z),
    // matching the wave profile in ocean.js (wave group at z = -2.4)
    rig.position.set(
      Math.sin(t * 0.27) * 1.35,
      1.12 + carve * 0.5 + Math.sin(t * 2.1) * 0.03,
      -2.0 - carve * 0.32);
    rig.rotation.set(
      -0.5 - carve * 0.14, // rail dug into the steep face
      carveVel * 0.28,
      carveVel * 0.16 + Math.sin(t * 2.1) * 0.015);

    // body language, slightly lagging the board
    const lag = Math.sin(t * 0.55 - 0.45);
    body.position.set(0, 0.78 + Math.sin(t * 1.65) * 0.045 - lag * 0.03, 0);
    body.rotation.set(lag * 0.13, carveVel * 0.1, 0.14 + carveVel * 0.1);
    body.updateMatrix();

    aimLeg(legF, ankleF, hipF);
    aimLeg(legB, ankleB, hipB);

    // head stays level and looks down the line; pouch sways behind it
    head.rotation.set(Math.sin(t * 1.3) * 0.04, carveVel * 0.12, -body.rotation.z * 0.65 + Math.sin(t * 0.9) * 0.03);
    pouchGroup.rotation.z = Math.sin(t * 1.65 - 0.7) * 0.09 - 0.04;
    const pouchPulse = 1 + Math.sin(t * 1.65 - 0.9) * 0.07;
    pouch.scale.set(0.5, 0.24 * pouchPulse, 0.16);

    // blink every few seconds
    const blink = (t % 3.7) < 0.12 ? 0.12 : 1;
    for (const e of eyes) e.scale.set(1, blink, 1);

    // balancing wings: slow, out of phase with each other and the carve
    wingF.rotation.z = -0.18 + Math.sin(t * 1.4) * 0.13 + carve * 0.12;
    wingF.rotation.y = -0.12 + Math.sin(t * 0.8) * 0.06;
    wingB.rotation.z = 0.22 + Math.sin(t * 1.4 + 1.1) * 0.13 - carve * 0.1;
    wingB.rotation.y = -0.1 + Math.cos(t * 0.7) * 0.06;

    tail.rotation.x = Math.sin(t * 1.9) * 0.08;
    tail.rotation.y = Math.sin(t * 1.1) * 0.1;
    scarfTail.rotation.z = 0.25 + Math.sin(t * 5.2) * 0.14;
    scarfTail.rotation.y = Math.sin(t * 3.7) * 0.25;

    collar.scale.set(1.55 + Math.sin(t * 3.1) * 0.06, 0.42, 0.35 + Math.sin(t * 2.6) * 0.03);
    collar.material.opacity = 0.7 + Math.sin(t * 2.3) * 0.15;
    spray.update(dt, { x: -1.55, y: 0.12, z: -0.15 });
  }
}
