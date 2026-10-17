import * as THREE from "three";

const V3 = THREE.Vector3;

const std = (color, o = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0, ...o });

const M = {
  body: std(0xfbf9f4, { roughness: 0.85 }),
  cream: std(0xf1e7d0, { roughness: 0.85 }),
  gray: std(0x8e939c, { roughness: 0.85, side: THREE.DoubleSide }),
  black: std(0x1d1e24, { roughness: 0.7, side: THREE.DoubleSide }),
  white: std(0xfbf8f0, { roughness: 0.85, side: THREE.DoubleSide }),
  offwhite: std(0xe9e4da, { roughness: 0.85, side: THREE.DoubleSide }),
  bill: std(0xf5a93a, { roughness: 0.45 }),
  billTip: std(0xd9472b, { roughness: 0.4 }),
  pouch: std(0xf7b568, { roughness: 0.5, side: THREE.DoubleSide }),
  leg: std(0xf08a24, { roughness: 0.55 }),
  eyeW: std(0xffffff, { roughness: 0.25 }),
  iris: std(0xf4d35e, { roughness: 0.3 }),
  pupil: std(0x0a0a0c, { roughness: 0.15 }),
  brow: std(0x6b6f78, { roughness: 0.8 }),
};

function shadowed(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function ellipsoid(rx, ry, rz, mat, seg = 28) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, seg, Math.round(seg * 0.7)), mat);
  m.scale.set(rx, ry, rz);
  return shadowed(m);
}

// ---- feathers ----------------------------------------------------------------
const featherCache = new Map();
function featherGeo(len, wid) {
  const key = `${len.toFixed(3)}_${wid.toFixed(3)}`;
  if (featherCache.has(key)) return featherCache.get(key);
  const s = new THREE.Shape();
  s.moveTo(-wid * 0.32, 0);
  s.lineTo(-wid * 0.5, len * 0.5);
  s.lineTo(-wid * 0.5, len * 0.86);
  s.quadraticCurveTo(-wid * 0.5, len, 0, len);
  s.quadraticCurveTo(wid * 0.5, len, wid * 0.5, len * 0.86);
  s.lineTo(wid * 0.5, len * 0.5);
  s.lineTo(wid * 0.32, 0);
  s.closePath();
  const g = new THREE.ShapeGeometry(s, 6);
  g.rotateX(-Math.PI / 2); // length now runs along -z, face normal +y
  featherCache.set(key, g);
  return g;
}

function feather(len, wid, mat) {
  return shadowed(new THREE.Mesh(featherGeo(len, wid), mat));
}

// ---- lofted tube (for the bill) --------------------------------------------
const RING = 18;
function makeLoft(sections, fn) {
  const pos = new Float32Array((sections + 1) * RING * 3);
  const idx = [];
  for (let i = 0; i < sections; i++) {
    for (let j = 0; j < RING; j++) {
      const a = i * RING + j;
      const b = i * RING + ((j + 1) % RING);
      const c = a + RING;
      const d = b + RING;
      idx.push(a, c, b, b, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setIndex(idx);
  updateLoft(g, sections, fn);
  return g;
}
function updateLoft(g, sections, fn) {
  const p = g.attributes.position;
  for (let i = 0; i <= sections; i++) {
    const t = i / sections;
    const { cy, cz, rx, ry } = fn(t);
    for (let j = 0; j < RING; j++) {
      const a = (j / RING) * Math.PI * 2;
      p.setXYZ(i * RING + j, Math.cos(a) * rx, cy + Math.sin(a) * ry, cz);
    }
  }
  p.needsUpdate = true;
  g.computeVertexNormals();
  g.computeBoundingSphere();
}

// tapered tube along a curve
function taperedTube(curve, radiusFn, segs, radial, mat) {
  const frames = curve.computeFrenetFrames(segs, false);
  const pos = [];
  const idx = [];
  for (let i = 0; i <= segs; i++) {
    const t = i / segs;
    const P = curve.getPointAt(t);
    const r = radiusFn(t);
    for (let j = 0; j < radial; j++) {
      const a = (j / radial) * Math.PI * 2;
      const n = frames.normals[i].clone().multiplyScalar(Math.cos(a)).addScaledVector(frames.binormals[i], Math.sin(a));
      pos.push(P.x + n.x * r, P.y + n.y * r, P.z + n.z * r);
    }
  }
  for (let i = 0; i < segs; i++) {
    for (let j = 0; j < radial; j++) {
      const a = i * radial + j;
      const b = i * radial + ((j + 1) % radial);
      idx.push(a, a + radial, b, b, a + radial, b + radial);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return shadowed(new THREE.Mesh(g, mat));
}

function limb(a, b, r, mat) {
  const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 10), mat));
  m.userData = { r };
  return m;
}
function placeLimb(m, a, b) {
  const d = new V3().subVectors(b, a);
  const len = d.length();
  m.position.copy(a).addScaledVector(d, 0.5);
  m.scale.set(1, len, 1);
  m.quaternion.setFromUnitVectors(new V3(0, 1, 0), d.normalize());
}

// ---- wing -------------------------------------------------------------------
function buildWing() {
  const wing = new THREE.Group(); // shoulder
  const s1 = new THREE.Group();
  const s2 = new THREE.Group();
  const s3 = new THREE.Group();
  s2.position.x = 0.48;
  s3.position.x = 0.5;
  wing.add(s1);
  s1.add(s2);
  s2.add(s3);
  const flutter = [];

  const bone = (g, len, r, mat) => {
    const m = ellipsoid(len / 2 + 0.03, r * 0.55, r * 1.2, mat, 16);
    m.position.x = len / 2;
    g.add(m);
  };
  bone(s1, 0.48, 0.075, M.body);
  bone(s2, 0.5, 0.06, M.body);
  bone(s3, 0.42, 0.04, M.gray);

  const row = (group, n, x0, x1, len, wid, mat, fan0, fan1, yOff, lenTaper = 0) => {
    for (let i = 0; i < n; i++) {
      const t = n === 1 ? 0 : i / (n - 1);
      const f = feather(len * (1 - lenTaper * t), wid, mat);
      f.position.set(x0 + (x1 - x0) * t, yOff + i * 0.0035, -0.04);
      f.rotation.y = -(fan0 + (fan1 - fan0) * t);
      group.add(f);
      flutter.push({ f, base: f.rotation.x, ph: i * 0.7 + group.id, amp: 0.05 + 0.04 * t });
    }
  };
  // flight feathers (underlayer, long) then coverts on top
  row(s1, 7, 0.02, 0.46, 0.62, 0.16, M.offwhite, -0.05, 0.1, -0.012);
  row(s2, 7, 0.02, 0.48, 0.66, 0.15, M.gray, 0.0, 0.05, -0.012);
  row(s3, 7, 0.0, 0.42, 0.78, 0.13, M.black, 0.0, 0.5, -0.012, -0.18);
  row(s1, 6, 0.04, 0.46, 0.36, 0.17, M.white, -0.05, 0.05, 0.012);
  row(s2, 6, 0.04, 0.48, 0.34, 0.16, M.white, 0.0, 0.05, 0.012);
  row(s3, 5, 0.02, 0.4, 0.3, 0.13, M.white, 0.0, 0.2, 0.012);
  return { wing, s1, s2, s3, flutter };
}

// ---- pelican -------------------------------------------------------------------
export function createPelican() {
  const root = new THREE.Group();

  // body
  const body = new THREE.Group();
  body.position.set(0, 0.98, -0.05);
  root.add(body);
  body.add(ellipsoid(0.36, 0.34, 0.62, M.body, 36));
  const chest = ellipsoid(0.3, 0.3, 0.3, M.body);
  chest.position.set(0, -0.02, 0.36);
  body.add(chest);
  const back = ellipsoid(0.32, 0.2, 0.5, M.white);
  back.position.set(0, 0.16, -0.08);
  body.add(back);

  // tail
  const tail = new THREE.Group();
  tail.position.set(0, 0.0, -0.52);
  body.add(tail);
  const tailF = [];
  for (let i = 0; i < 7; i++) {
    const t = i / 6 - 0.5;
    const f = feather(0.46, 0.13, i % 2 ? M.gray : M.offwhite);
    f.rotation.y = t * 0.8;
    f.rotation.x = 0.1;
    f.position.y = i * 0.003;
    tail.add(f);
    tailF.push({ f, ph: i });
  }

  // wings
  const wingL = buildWing();
  const wingR = buildWing();
  wingL.wing.position.set(0.3, 0.14, 0.14);
  wingR.wing.position.set(-0.3, 0.14, 0.14);
  wingR.wing.scale.x = -1;
  body.add(wingL.wing, wingR.wing);

  // neck + head
  const neck = new THREE.Group();
  neck.position.set(0, 0.12, 0.46);
  body.add(neck);
  const curve = new THREE.CatmullRomCurve3([
    new V3(0, -0.05, -0.05),
    new V3(0, 0.12, 0.14),
    new V3(0, 0.36, 0.14),
    new V3(0, 0.58, 0.04),
    new V3(0, 0.76, 0.12),
    new V3(0, 0.84, 0.28),
  ]);
  const neckMesh = taperedTube(
    curve,
    (t) => 0.17 - 0.1 * Math.sin(Math.min(t * 1.5, 1) * Math.PI * 0.5) + 0.02 * Math.sin(t * 3),
    28,
    16,
    M.body
  );
  neck.add(neckMesh);
  // feathered ruff at the base of the neck
  const ruff = ellipsoid(0.2, 0.17, 0.22, M.body);
  ruff.position.set(0, 0.04, 0.02);
  neck.add(ruff);

  const head = new THREE.Group();
  head.position.copy(curve.getPointAt(1));
  neck.add(head);
  const skull = ellipsoid(0.125, 0.125, 0.15, M.body, 30);
  head.add(skull);
  const crown = ellipsoid(0.11, 0.08, 0.1, M.cream, 20);
  crown.position.set(0, 0.05, -0.03);
  head.add(crown);

  // crest tufts
  const tufts = [];
  for (let i = 0; i < 4; i++) {
    const f = shadowed(new THREE.Mesh(new THREE.ConeGeometry(0.022, 0.2, 8), M.body));
    f.geometry.translate(0, -0.1, 0);
    f.position.set((i - 1.5) * 0.03, 0.1, -0.08);
    f.rotation.x = -1.9;
    head.add(f);
    tufts.push({ f, ph: i * 0.9 });
  }

  // eyes
  const eyes = new THREE.Group();
  eyes.scale.setScalar(1.3);
  for (const s of [-1, 1]) {
    const e = new THREE.Group();
    e.position.set(s * 0.085, 0.035, 0.07);
    const w = ellipsoid(0.048, 0.048, 0.048, M.eyeW, 20);
    e.add(w);
    const iris = ellipsoid(0.034, 0.034, 0.02, M.iris, 16);
    iris.position.set(s * 0.012, 0.0, 0.034);
    iris.lookAt(new V3(s * 0.3, 0, 1));
    e.add(iris);
    const pupil = ellipsoid(0.02, 0.02, 0.012, M.pupil, 12);
    pupil.position.set(s * 0.02, 0.0, 0.04);
    e.add(pupil);
    const glint = ellipsoid(0.007, 0.007, 0.004, M.eyeW, 8);
    glint.position.set(s * 0.012, 0.012, 0.05);
    e.add(glint);
    const brow = ellipsoid(0.056, 0.014, 0.05, M.brow, 12);
    brow.position.set(s * 0.004, 0.05, 0.012);
    brow.rotation.z = -s * 0.28;
    e.add(brow);
    eyes.add(e);
  }
  head.add(eyes);

  // bill
  const BL = 0.84;
  const upperFn = (t) => {
    const hook = t > 0.9 ? Math.pow((t - 0.9) / 0.1, 2) * 0.05 : 0;
    return {
      cy: -0.035 - 0.07 * t - hook,
      cz: 0.08 + BL * t,
      rx: 0.07 * (1 - 0.72 * Math.pow(t, 1.1)) + 0.012 * (1 - t) + 0.006,
      ry: 0.042 * (1 - 0.6 * t) + 0.012,
    };
  };
  const upper = shadowed(new THREE.Mesh(makeLoft(24, upperFn), M.bill));
  head.add(upper);
  const nail = shadowed(new THREE.Mesh(new THREE.SphereGeometry(1, 12, 10), M.billTip));
  nail.scale.set(0.017, 0.017, 0.03);
  const tipP = upperFn(1);
  nail.position.set(0, tipP.cy - 0.002, tipP.cz - 0.005);
  head.add(nail);
  const knob = ellipsoid(0.026, 0.018, 0.06, M.bill, 12);
  knob.position.set(0, upperFn(0.18).cy + 0.04, upperFn(0.18).cz);
  head.add(knob);

  let pouchBulge = 0.5;
  const pouchFn = (t) => {
    const u = upperFn(t);
    const depth = (0.012 + (0.17 * pouchBulge) * Math.pow(Math.sin(Math.PI * (0.06 + 0.82 * t)), 0.8)) * (1 - 0.35 * t);
    return {
      cy: u.cy - u.ry * 0.7 - depth * 0.55 + 0.015,
      cz: u.cz - 0.01,
      rx: u.rx * 0.98,
      ry: depth,
    };
  };
  const pouchGeo = makeLoft(24, pouchFn);
  const pouch = shadowed(new THREE.Mesh(pouchGeo, M.pouch));
  head.add(pouch);

  // legs (two-bone IK between hips on the body and feet fixed on the board)
  const legs = [];
  for (const s of [-1, 1]) {
    const thigh = limb(null, null, 0.05, M.body);
    const shin = limb(null, null, 0.032, M.leg);
    const knee = ellipsoid(0.048, 0.048, 0.048, M.leg, 12);
    const foot = new THREE.Group();
    const fs = new THREE.Shape();
    fs.moveTo(-0.025, 0);
    fs.lineTo(-0.16, 0.26);
    fs.quadraticCurveTo(-0.11, 0.3, -0.07, 0.24);
    fs.quadraticCurveTo(-0.045, 0.34, 0, 0.3);
    fs.quadraticCurveTo(0.045, 0.34, 0.07, 0.24);
    fs.quadraticCurveTo(0.11, 0.3, 0.16, 0.26);
    fs.lineTo(0.025, 0);
    fs.closePath();
    const fg = new THREE.ExtrudeGeometry(fs, { depth: 0.02, bevelEnabled: false });
    fg.rotateX(Math.PI / 2);
    const footMesh = shadowed(new THREE.Mesh(fg, M.leg));
    footMesh.position.y = 0.02;
    foot.add(footMesh);
    foot.rotation.y = s * 0.2;
    root.add(thigh, shin, knee, foot);
    const hipLocal = new V3(s * 0.17, -0.26, -0.02);
    const footPos = new V3(s * 0.2, 0.0, s > 0 ? 0.22 : -0.38);
    foot.position.copy(footPos);
    legs.push({ thigh, shin, knee, foot, hipLocal, footPos, s });
  }

  const hip = new V3();
  const knee = new V3();
  const tmp = new V3();
  function solveLegs() {
    body.updateMatrix();
    for (const L of legs) {
      hip.copy(L.hipLocal).applyMatrix4(body.matrix);
      const L1 = 0.46;
      const L2 = 0.44;
      const target = tmp.copy(L.footPos);
      target.y += 0.05;
      const d = new V3().subVectors(target, hip);
      let D = d.length();
      D = Math.min(D, L1 + L2 - 0.01);
      const dir = d.normalize();
      const a = (L1 * L1 - L2 * L2 + D * D) / (2 * D);
      const h = Math.sqrt(Math.max(L1 * L1 - a * a, 0));
      const bend = new V3(L.s * 0.25, 0, 1);
      bend.addScaledVector(dir, -bend.dot(dir)).normalize();
      knee.copy(hip).addScaledVector(dir, a).addScaledVector(bend, h);
      placeLimb(L.thigh, hip, knee);
      placeLimb(L.shin, knee, target);
      L.knee.position.copy(knee);
    }
  }

  // ---- animation -----------------------------------------------------------
  const lean = { v: 0 };
  function update(t, st) {
    // st: { turn (yaw rate), bank (-1..1 sideways lean), speed, pump }
    const sway = Math.sin(t * 1.7);
    const crouch = 0.06 + 0.04 * Math.sin(t * 2.3) + 0.05 * st.pump;
    body.position.y = 0.98 - crouch;
    body.rotation.x = 0.28 + 0.05 * Math.sin(t * 1.3);
    lean.v += (THREE.MathUtils.clamp(-st.turn * 0.22, -0.5, 0.5) - lean.v) * 0.08;
    body.rotation.z = lean.v + 0.03 * sway;
    body.rotation.y = -lean.v * 0.4 - 0.85 * st.sinYaw;

    // neck holds the head level, looks ahead, wobbles a bit
    neck.rotation.x = -body.rotation.x * 0.8 + 0.05 * Math.sin(t * 2.1);
    neck.rotation.z = -lean.v * 1.1;
    neck.rotation.y = 0.7 * st.sinYaw;
    head.rotation.x = 0.15 + 0.04 * Math.sin(t * 2.9 + 1);
    head.rotation.y = 0.12 * Math.sin(t * 0.8) + 0.12 * st.sinYaw;
    head.rotation.z = -lean.v * 0.4;

    // balance: arms out, tilting against the lean, flexing in the wind
    const wob = (ph) => Math.sin(t * 2.2 + ph);
    const wl = { raise: 0.6 - lean.v * 1.4 + 0.1 * wob(0), sweep: 0.55, fl: 0.1 };
    const wr = { raise: 0.6 + lean.v * 1.4 + 0.1 * wob(1.7), sweep: 0.55, fl: 0.1 };
    for (const [W, c, ph] of [[wingL, wl, 0], [wingR, wr, 2]]) {
      W.wing.rotation.z = c.raise;
      W.wing.rotation.y = c.sweep + 0.05 * wob(ph + 0.5);
      W.wing.rotation.x = -0.6 + 0.08 * wob(ph + 4);
      W.s1.rotation.z = 0.05 + 0.06 * wob(ph + 1);
      W.s2.rotation.z = 0.0 + 0.1 * wob(ph + 2) - 0.1;
      W.s3.rotation.z = -0.18 + 0.14 * wob(ph + 3);
      W.s3.rotation.y = 0.12 * wob(ph + 3.4);
      for (const fl of W.flutter) fl.f.rotation.x = fl.base + fl.amp * Math.sin(t * 6.5 + fl.ph);
    }
    for (const tf of tailF) tf.f.rotation.x = 0.1 + 0.04 * Math.sin(t * 5 + tf.ph) + st.speed * 0.01;
    tail.rotation.x = 0.1 + lean.v * 0.0;
    for (const tu of tufts) tu.f.rotation.x = -1.9 - 0.15 * Math.sin(t * 7 + tu.ph) - 0.2 * st.speed * 0.1;

    // pouch: wind-filled, flaps
    pouchBulge = 0.55 + 0.25 * Math.sin(t * 3.1) + 0.12 * Math.sin(t * 7.3) + 0.03 * st.speed;
    updateLoft(pouchGeo, 24, pouchFn);

    // blink
    const ph = (t % 4.3) / 4.3;
    const bl = ph > 0.965 ? 1 - Math.sin(((ph - 0.965) / 0.035) * Math.PI) * 0.9 : 1;
    eyes.scale.y = bl;

    solveLegs();
  }

  update(0, { turn: 0, bank: 0, speed: 0, pump: 0, sinYaw: 0 });
  return { root, update };
}
