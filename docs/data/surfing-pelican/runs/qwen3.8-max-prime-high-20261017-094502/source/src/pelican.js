import * as THREE from "three";
import { PALETTE } from "./palette.js";

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const sstep = (e0, e1, x) => {
  const t = clamp((x - e0) / (e1 - e0 || 1e-6), 0, 1);
  return t * t * (3 - 2 * t);
};
const lerp = (a, b, t) => a + (b - a) * t;

/**
 * Local frame of the bird: +Z forward (beak), +Y up, +X to its right.
 * It stands on a deck that sits at y ~= 0.20 in rig space.
 */
export const DECK_Y = 0.20;

/* ================================================================== *
 * geometry helpers
 * ================================================================== */

const _REF = new THREE.Vector3(0, 0, 1);

/**
 * Swept, tapered, elliptical tube along a curve — used for the neck, the beak,
 * the pouch and the legs. `profile(t)` returns [radiusAcross, radiusUp].
 * `origin` puts the geometry in the local space of a group placed there, so
 * segments can be stacked into a bendable chain.
 */
function sweptTube(curve, t0, t1, steps, radial, profile, origin = null) {
  const pos = [];
  const idx = [];
  const T = new THREE.Vector3();
  const R = new THREE.Vector3();
  const U = new THREE.Vector3();
  const P = new THREE.Vector3();
  const base = origin || new THREE.Vector3();

  for (let i = 0; i <= steps; i++) {
    const t = t0 + ((t1 - t0) * i) / steps;
    curve.getPoint(t, P);
    curve.getTangent(t, T).normalize();
    R.crossVectors(_REF, T);
    if (R.lengthSq() < 1e-6) R.set(1, 0, 0);
    R.normalize();
    U.crossVectors(T, R).normalize();

    const [rx, ry] = profile(t);
    for (let j = 0; j <= radial; j++) {
      const a = (j / radial) * Math.PI * 2;
      const ca = Math.cos(a);
      const sa = Math.sin(a);
      pos.push(
        P.x - base.x + R.x * ca * rx + U.x * sa * ry,
        P.y - base.y + R.y * ca * rx + U.y * sa * ry,
        P.z - base.z + R.z * ca * rx + U.z * sa * ry
      );
    }
  }

  const row = radial + 1;
  for (let i = 0; i < steps; i++) {
    for (let j = 0; j < radial; j++) {
      const a = i * row + j;
      const b = a + 1;
      const c = a + row;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/** Planar shape extruded thin (shape-y becomes world +Z), then deformed. */
function bentPanel(shape, thickness, bend) {
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: thickness,
    bevelEnabled: true,
    bevelThickness: thickness * 0.42,
    bevelSize: thickness * 0.5,
    bevelSegments: 2,
    curveSegments: 10,
  });
  geo.rotateX(Math.PI / 2);
  geo.computeBoundingBox();
  geo.translate(0, -(geo.boundingBox.min.y + geo.boundingBox.max.y) * 0.5, 0);

  const p = geo.attributes.position;
  const v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    bend(v);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  p.needsUpdate = true;
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

/** Vertex colours ramping `from` -> `to` along |axis|, cool underneath. */
function paintRamp(geo, axis, from, to, e0, e1, shade = 0.86) {
  const p = geo.attributes.position;
  const colors = new Float32Array(p.count * 3);
  const c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const d = axis === "x" ? Math.abs(x) : axis === "y" ? Math.abs(y) : Math.abs(z);
    c.copy(from).lerp(to, sstep(e0, e1, d));
    if (y < 0) c.multiplyScalar(lerp(1.0, shade, clamp(-y * 6, 0, 1)));
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
}

function makeMaterials() {
  const plumage = new THREE.MeshStandardMaterial({
    color: new THREE.Color(PALETTE.body),
    roughness: 0.84,
    metalness: 0.0,
  });
  const plumageVC = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.86,
    metalness: 0.0,
    side: THREE.DoubleSide,
  });
  return {
    plumage,
    plumageVC,
    beak: new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.beak), roughness: 0.40 }),
    beakTip: new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.beakTip), roughness: 0.45 }),
    pouch: new THREE.MeshStandardMaterial({
      color: new THREE.Color(PALETTE.pouch),
      roughness: 0.55,
      side: THREE.DoubleSide,
    }),
    leg: new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.leg), roughness: 0.6 }),
    eye: new THREE.MeshStandardMaterial({ color: new THREE.Color(PALETTE.eye), roughness: 0.10, metalness: 0.15 }),
    glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
    ring: new THREE.MeshStandardMaterial({ color: new THREE.Color("#d8c39b"), roughness: 0.7 }),
  };
}

/* ================================================================== *
 * parts
 * ================================================================== */

function buildBody(mats) {
  const g = new THREE.Group();
  const add = (geo, mat, pos, scale) => {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(...pos);
    if (scale) m.scale.set(...scale);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return m;
  };

  const s40 = new THREE.SphereGeometry(1, 40, 28);
  add(s40, mats.plumage, [0, 0.98, -0.02], [0.56, 0.60, 1.02]); // torso
  add(s40, mats.plumage, [0, 0.87, 0.60], [0.47, 0.48, 0.54]); // breast
  add(s40, mats.plumage, [0, 1.00, -0.84], [0.42, 0.40, 0.52]); // rump
  add(s40, mats.plumage, [0, 1.24, 0.30], [0.46, 0.34, 0.46]); // upper back

  for (const s of [-1, 1]) {
    const sh = add(new THREE.SphereGeometry(0.25, 22, 16), mats.plumage, [s * 0.40, 1.24, 0.08], [0.78, 0.95, 1.15]);
    sh.name = s > 0 ? "shoulderR" : "shoulderL";
  }
  return g;
}

function buildTail(mats) {
  const s = new THREE.Shape();
  s.moveTo(0, 0.0);
  s.bezierCurveTo(0.30, 0.02, 0.50, 0.16, 0.58, 0.42);
  s.bezierCurveTo(0.42, 0.37, 0.28, 0.37, 0.15, 0.44);
  s.lineTo(-0.15, 0.44);
  s.bezierCurveTo(-0.28, 0.37, -0.42, 0.37, -0.58, 0.42);
  s.bezierCurveTo(-0.50, 0.16, -0.30, 0.02, 0, 0.0);

  const geo = bentPanel(s, 0.05, (v) => {
    const along = clamp(v.z / 0.44, 0, 1);
    v.y += -0.13 * along * along;              // droop toward the tip
    v.y += 0.045 * (1.0 - clamp(Math.abs(v.x) / 0.58, 0, 1)); // slight crown
  });
  paintRamp(geo, "z", new THREE.Color(PALETTE.body), new THREE.Color(PALETTE.wingTip), 0.12, 0.44);
  geo.rotateY(Math.PI); // point it backwards (-Z)

  const mesh = new THREE.Mesh(geo, mats.plumageVC);
  mesh.castShadow = true;
  const g = new THREE.Group();
  g.add(mesh);
  return g;
}

function buildWing(side, mats) {
  const S = 1.70; // span, root to tip
  const s = new THREE.Shape();

  // leading edge out to the wrist
  s.moveTo(0.0, 0.48);
  s.bezierCurveTo(0.30 * S, 0.50, 0.62 * S, 0.42, 0.80 * S, 0.24);
  s.quadraticCurveTo(0.92 * S, 0.13, 1.00 * S, 0.02);

  // splayed primaries with notched tips
  s.lineTo(1.04 * S, -0.14);
  s.lineTo(0.94 * S, -0.24);
  s.lineTo(1.02 * S, -0.33);
  s.lineTo(0.91 * S, -0.43);
  s.lineTo(0.98 * S, -0.52);
  s.lineTo(0.86 * S, -0.60);
  s.lineTo(0.90 * S, -0.68);
  s.lineTo(0.74 * S, -0.72);

  // trailing edge home
  s.bezierCurveTo(0.56 * S, -0.70, 0.34 * S, -0.60, 0.16 * S, -0.52);
  s.quadraticCurveTo(0.06 * S, -0.48, 0.0, -0.46);
  s.lineTo(0.0, 0.48);

  const geo = bentPanel(s, 0.072, (v) => {
    const span = clamp(v.x / S, 0, 1);
    const tw = -0.30 * Math.pow(span, 1.4); // washout
    const ct = Math.cos(tw), st = Math.sin(tw);
    const y0 = v.y, z0 = v.z;
    let y = y0 * ct - z0 * st;
    let z = y0 * st + z0 * ct;
    const camberN = clamp((z0 + 0.8) / 1.45, 0, 1);
    y += -Math.sin(camberN * Math.PI) * 0.12 * (1.0 - 0.55 * span); // aerofoil
    y += Math.pow(span, 1.9) * 0.28;                                 // dihedral
    z -= Math.pow(span, 2.0) * 0.15;                                 // sweep
    v.y = y;
    v.z = z;
  });

  // plumage: white coverts -> black flight feathers
  const p = geo.attributes.position;
  const colors = new Float32Array(p.count * 3);
  const white = new THREE.Color(PALETTE.body);
  const cream = new THREE.Color(PALETTE.bodyShade);
  const dark = new THREE.Color(PALETTE.wingTip);
  const c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const span = clamp(x / S, 0, 1);
    c.copy(white).lerp(cream, sstep(-0.5, 0.5, z) * 0.4);
    c.lerp(dark, sstep(0.50, 0.94, span) * 0.93);
    const rows = 0.5 + 0.5 * Math.sin((z + 0.5) * 9.0 - span * 2.0);
    c.lerp(cream, rows * 0.11 * (1.0 - span));
    if (y < 0) c.multiplyScalar(lerp(1.0, 0.87, clamp(-y * 6, 0, 1)));
    colors[i * 3] = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

  const mesh = new THREE.Mesh(geo, mats.plumageVC);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  const shoulder = new THREE.Group();
  shoulder.position.set(side * 0.44, 1.26, 0.06);
  shoulder.scale.x = side; // three flips winding + normals for negative scale
  shoulder.add(mesh);

  const delt = new THREE.Mesh(new THREE.SphereGeometry(0.185, 20, 14), mats.plumage);
  delt.scale.set(1.3, 0.92, 1.15);
  delt.position.set(0.05, -0.01, 0.0);
  delt.castShadow = true;
  shoulder.add(delt);

  return shoulder;
}

function buildNeck(mats) {
  const curve = new THREE.CatmullRomCurve3(
    [
      new THREE.Vector3(0.0, 1.24, 0.40),
      new THREE.Vector3(0.0, 1.42, 0.68),
      new THREE.Vector3(0.0, 1.70, 0.80),
      new THREE.Vector3(0.0, 1.94, 0.82),
      new THREE.Vector3(0.0, 2.08, 0.86),
    ],
    false,
    "catmullrom",
    0.4
  );
  const profile = (t) => {
    const r = lerp(0.235, 0.152, sstep(0.0, 0.85, t)) * (1.0 + 0.10 * Math.sin(t * 5.0));
    return [r * 1.0, r * 1.06];
  };

  const splits = [0, 0.44, 0.76, 1.0];
  const root = new THREE.Group();
  const joints = [];
  let parent = root;
  let parentOrigin = new THREE.Vector3(0, 0, 0);
  let prev = curve.getPoint(splits[0]).clone();

  for (let i = 0; i < splits.length - 1; i++) {
    const t0 = splits[i];
    const t1 = splits[i + 1];
    const geo = sweptTube(curve, t0, t1, 16, 20, profile, prev);
    const mesh = new THREE.Mesh(geo, mats.plumage);
    mesh.castShadow = true;

    const joint = new THREE.Group();
    joint.position.copy(prev).sub(parentOrigin);
    joint.add(mesh);
    parent.add(joint);
    joints.push(joint);

    if (i > 0) {
      const kn = new THREE.Mesh(new THREE.SphereGeometry(profile(t0)[0] * 1.05, 18, 14), mats.plumage);
      kn.castShadow = true;
      joint.add(kn);
    }

    const next = curve.getPoint(t1).clone();
    const child = new THREE.Group();
    child.position.copy(next).sub(prev);
    joint.add(child);

    parent = child;
    parentOrigin = next.clone();
    prev = next;
  }

  return { root, joints, headSocket: parent, curve };
}

function buildHead(mats) {
  const g = new THREE.Group();

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.27, 34, 24), mats.plumage);
  skull.scale.set(0.94, 1.0, 1.12);
  skull.position.set(0, 0.0, 0.02);
  skull.castShadow = true;
  g.add(skull);

  const nape = new THREE.Mesh(new THREE.SphereGeometry(0.2, 22, 16), mats.plumage);
  nape.scale.set(0.92, 0.74, 1.0);
  nape.position.set(0, 0.12, -0.10);
  nape.castShadow = true;
  g.add(nape);

  // shaggy crest feathers
  for (let i = 0; i < 5; i++) {
    const f = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.22 + (i % 2) * 0.06, 6), mats.plumage);
    f.position.set((i - 2) * 0.052, 0.15 - Math.abs(i - 2) * 0.035, -0.18 - Math.abs(i - 2) * 0.025);
    f.rotation.set(-1.2 + i * 0.07, 0, (i - 2) * 0.26);
    f.castShadow = true;
    g.add(f);
  }

  /* upper mandible */
  const beakCurve = new THREE.CatmullRomCurve3(
    [
      new THREE.Vector3(0, 0.01, 0.14),
      new THREE.Vector3(0, -0.01, 0.58),
      new THREE.Vector3(0, -0.05, 0.96),
      new THREE.Vector3(0, -0.11, 1.20),
      new THREE.Vector3(0, -0.17, 1.32),
    ],
    false,
    "catmullrom",
    0.35
  );
  const upper = new THREE.Mesh(
    sweptTube(beakCurve, 0, 1, 36, 18, (t) => {
      const k = sstep(0, 1, t);
      const w = lerp(0.185, 0.036, Math.pow(k, 0.82));
      const h = lerp(0.112, 0.048, Math.pow(k, 0.65)) * (1.0 + 0.30 * (1 - k));
      return [w, h];
    }),
    mats.beak
  );
  upper.castShadow = true;
  g.add(upper);

  // dark hook at the tip
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.042, 0.15, 12), mats.beakTip);
  hook.position.set(0, -0.215, 1.33);
  hook.rotation.set(Math.PI + 0.22, 0, 0);
  hook.castShadow = true;
  g.add(hook);

  /* gular pouch */
  const pouchCurve = new THREE.CatmullRomCurve3(
    [
      new THREE.Vector3(0, -0.09, 0.12),
      new THREE.Vector3(0, -0.19, 0.48),
      new THREE.Vector3(0, -0.25, 0.86),
      new THREE.Vector3(0, -0.23, 1.10),
      new THREE.Vector3(0, -0.19, 1.24),
    ],
    false,
    "catmullrom",
    0.4
  );
  const pouchMesh = new THREE.Mesh(
    sweptTube(pouchCurve, 0, 1, 28, 22, (t) => {
      const bulge = Math.sin(clamp(t, 0, 1) * Math.PI);
      return [0.045 + 0.20 * Math.pow(bulge, 0.68), 0.035 + 0.17 * Math.pow(bulge, 0.85)];
    }),
    mats.pouch
  );
  pouchMesh.castShadow = true;
  g.add(pouchMesh);

  /* lower mandible rails */
  for (const sx of [-1, 1]) {
    const railCurve = new THREE.CatmullRomCurve3(
      [
        new THREE.Vector3(sx * 0.142, -0.05, 0.14),
        new THREE.Vector3(sx * 0.124, -0.085, 0.58),
        new THREE.Vector3(sx * 0.074, -0.135, 0.96),
        new THREE.Vector3(sx * 0.018, -0.185, 1.24),
      ],
      false,
      "catmullrom",
      0.4
    );
    const rail = new THREE.Mesh(
      sweptTube(railCurve, 0, 1, 22, 10, () => [0.027, 0.031]),
      mats.beak
    );
    rail.castShadow = true;
    g.add(rail);
  }

  /* eyes */
  const eyes = [];
  for (const sx of [-1, 1]) {
    const socket = new THREE.Group();
    socket.position.set(sx * 0.183, 0.055, 0.135);
    socket.rotation.y = sx * 0.55;

    const ringM = new THREE.Mesh(new THREE.SphereGeometry(0.076, 18, 14), mats.ring);
    ringM.scale.set(1, 1, 0.5);
    socket.add(ringM);

    const lid = new THREE.Group();
    const ball = new THREE.Mesh(new THREE.SphereGeometry(0.061, 20, 16), mats.eye);
    ball.position.z = 0.014;
    lid.add(ball);
    const glintM = new THREE.Mesh(new THREE.SphereGeometry(0.016, 10, 8), mats.glint);
    glintM.position.set(0.021, 0.025, 0.053);
    lid.add(glintM);
    socket.add(lid);
    g.add(socket);
    eyes.push({ socket, lid, side: sx });
  }

  return { group: g, eyes, pouchMesh, skull };
}

function buildLeg(mats) {
  const hip = new THREE.Group();
  const knee = new THREE.Group();
  const ankle = new THREE.Group();
  const toes = new THREE.Group();

  const L1 = 0.31;
  const L2 = 0.31;

  const seg = (len, r0, r1, mat, radial = 12) => {
    const curve = new THREE.LineCurve3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -len, 0));
    const m = new Mesh_(
      sweptTube(curve, 0, 1, 6, radial, (t) => [lerp(r0, r1, t) * 1.03, lerp(r0, r1, t)]),
      mat
    );
    m.castShadow = true;
    return m;
  };

  hip.add(seg(L1, 0.092, 0.064, mats.plumage, 14)); // feathered thigh
  knee.position.y = -L1;
  hip.add(knee);

  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.064, 14, 10), mats.leg);
  knob.castShadow = true;
  knee.add(knob);
  knee.add(seg(L2, 0.052, 0.038, mats.leg, 10)); // bare shin
  ankle.position.y = -L2;
  knee.add(ankle);

  /* webbed foot drawn flat in XZ, toes toward +Z */
  const footShape = new THREE.Shape();
  footShape.moveTo(0.0, 0.02);
  footShape.lineTo(-0.055, 0.0);
  footShape.bezierCurveTo(-0.14, 0.06, -0.20, 0.16, -0.195, 0.29);
  footShape.bezierCurveTo(-0.15, 0.305, -0.10, 0.29, -0.072, 0.25);
  footShape.bezierCurveTo(-0.062, 0.33, -0.03, 0.385, 0.0, 0.385);
  footShape.bezierCurveTo(0.03, 0.385, 0.062, 0.33, 0.072, 0.25);
  footShape.bezierCurveTo(0.10, 0.29, 0.15, 0.305, 0.195, 0.29);
  footShape.bezierCurveTo(0.20, 0.16, 0.14, 0.06, 0.055, 0.0);
  footShape.lineTo(0.0, 0.02);

  const footGeo = new THREE.ExtrudeGeometry(footShape, {
    depth: 0.032,
    bevelEnabled: true,
    bevelThickness: 0.010,
    bevelSize: 0.013,
    bevelSegments: 2,
    curveSegments: 8,
  });
  footGeo.rotateX(Math.PI / 2); // toes toward +Z
  footGeo.translate(0, -0.030, -0.02);
  const foot = new THREE.Mesh(footGeo, mats.leg);
  foot.castShadow = true;
  toes.add(foot);

  for (const sx of [-0.185, 0, 0.185]) {
    const nail = new THREE.Mesh(new THREE.ConeGeometry(0.016, 0.055, 6), mats.beak);
    nail.position.set(sx, 0.0, sx === 0 ? 0.40 : 0.30);
    nail.rotation.set(Math.PI / 2 - 0.2, 0, 0);
    toes.add(nail);
  }

  ankle.add(toes);
  return { hip, knee, ankle, toes, thighLen: L1, shinLen: L2 };
}

const Mesh_ = THREE.Mesh;

/* ================================================================== *
 * two-bone IK so the feet stay planted on the deck
 * ================================================================== */

const DOWN = new THREE.Vector3(0, -1, 0);
const POLE = new THREE.Vector3(0, -0.35, -1).normalize(); // hocks kick backwards

/**
 * Points the hip at `target` (both in the pelican's local space), bends the
 * knee around `POLE`, then counter-rotates the ankle so the foot stays flat
 * on the deck whatever the leg does.
 */
function solveLeg(leg, hipPos, target) {
  const L1 = leg.thighLen;
  const L2 = leg.shinLen;
  const maxReach = (L1 + L2) * 0.995;

  const to = target.clone().sub(hipPos);
  const d = clamp(to.length(), 1e-4, maxReach);
  const u = to.normalize();

  // component of the pole perpendicular to the hip->target line
  const w = POLE.clone().addScaledVector(u, -POLE.dot(u));
  if (w.lengthSq() < 1e-8) w.set(1, 0, 0).addScaledVector(u, -u.x);
  w.normalize();

  const cosA = clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1);
  const alpha = Math.acos(cosA);
  const thighDir = u.clone().multiplyScalar(Math.cos(alpha)).addScaledVector(w, Math.sin(alpha)).normalize();

  leg.hip.quaternion.setFromUnitVectors(DOWN, thighDir);

  const kneePos = hipPos.clone().addScaledVector(thighDir, L1);
  const shin = target.clone().sub(kneePos);
  if (shin.lengthSq() < 1e-10) shin.copy(thighDir);
  shin.normalize();

  const invHip = leg.hip.quaternion.clone().invert();
  leg.knee.quaternion.setFromUnitVectors(DOWN, shin.clone().applyQuaternion(invHip));

  // foot flat in pelican space: undo hip*knee, then let the toes flex
  leg.ankle.quaternion.copy(leg.knee.quaternion).premultiply(leg.hip.quaternion).invert();

  return d / (L1 + L2);
}

/* ================================================================== *
 * assembly
 * ================================================================== */

export function createPelican() {
  const mats = makeMaterials();
  const root = new THREE.Group();
  root.name = "pelican";

  const body = buildBody(mats);
  root.add(body);

  const neck = buildNeck(mats);
  root.add(neck.root);

  const head = buildHead(mats);
  head.group.position.set(0, 0.05, 0.05);
  neck.headSocket.add(head.group);

  const tail = buildTail(mats);
  tail.position.set(0, 1.10, -1.10);
  tail.rotation.x = -0.26;
  root.add(tail);

  const wingR = buildWing(1, mats);
  const wingL = buildWing(-1, mats);
  root.add(wingR, wingL);

  const legR = buildLeg(mats);
  const legL = buildLeg(mats);
  legR.hip.position.set(0.19, 0.70, -0.30);
  legL.hip.position.set(-0.19, 0.70, 0.02);
  root.add(legR.hip, legL.hip);

  // ankle targets (front foot toward the nose, back foot toward the tail)
  const ankleY = DECK_Y + 0.072;
  const feet = {
    front: new THREE.Vector3(-0.17, ankleY, 0.40),
    back: new THREE.Vector3(0.19, ankleY, -0.50),
  };

  const rig = {
    root,
    mats,
    body,
    tail,
    neck,
    head,
    wingL,
    wingR,
    legL,
    legR,
    feet,
    state: {
      blink: 0,
      nextBlink: 2.5,
      gesture: null,
      gestureAt: 2.0,
      gestureT: 0,
      flapExtra: 0,
      look: new THREE.Vector2(0, 0),
      lookGoal: new THREE.Vector2(0, 0),
      crouch: 0,
    },
  };

  rig.update = (t, dt, drive) => updatePelican(rig, t, dt, drive);
  rig.root.updateMatrixWorld(true);
  return rig;
}

/* ================================================================== *
 * animation
 * ================================================================== */

function updatePelican(rig, t, dt, d) {
  const st = rig.state;

  /* ---- idle gestures first, they feed the wing motion ---- */
  if (!st.gesture) {
    st.flapExtra *= Math.max(0, 1 - dt * 6);
    st.gestureAt -= dt;
    if (st.gestureAt <= 0) {
      st.gesture = Math.random() < 0.55 ? "look" : "pump";
      st.gestureT = 0;
      st.lookGoal.set(0, 0);
    }
  } else {
    st.gestureT += dt;
    const p = st.gestureT;
    if (st.gesture === "look") {
      if (p < 0.4) {
        const k = sstep(0, 0.4, p);
        st.lookGoal.set(-0.95 * k, 0.32 * k);
      } else if (p < 1.7) {
        st.lookGoal.set(-0.95 + Math.sin(p * 2.1) * 0.12, 0.32 + Math.sin(p * 1.4) * 0.10);
      } else if (p < 2.4) {
        const k = 1 - sstep(1.7, 2.4, p);
        st.lookGoal.set(-0.95 * k, 0.32 * k);
      } else {
        st.gesture = null;
        st.gestureAt = 2.0 + Math.random() * 5.0;
      }
    } else {
      st.flapExtra = Math.sin(p * 14.0) * Math.exp(-p * 1.7) * 0.9;
      if (p > 1.5) {
        st.gesture = null;
        st.gestureAt = 2.0 + Math.random() * 5.0;
      }
    }
  }
  st.look.x += (st.lookGoal.x - st.look.x) * Math.min(1, dt * 9);
  st.look.y += (st.lookGoal.y - st.look.y) * Math.min(1, dt * 9);

  /* ---- load / crouch ---- */
  const loadTarget = clamp(d.load, 0, 1);
  st.crouch += (loadTarget - st.crouch) * Math.min(1, dt * 5);
  const crouch = st.crouch;

  const breathe = Math.sin(t * 1.9) * 0.012 + Math.sin(t * 4.3) * 0.005;

  /* ---- torso ---- */
  rig.body.position.y = breathe * 1.3 - crouch * 0.07;
  rig.body.rotation.x = d.bodyPitch * 0.40 + breathe * 0.5 + crouch * 0.10;
  rig.body.rotation.z = -d.bodyRoll * 0.30;

  rig.root.position.y = -crouch * 0.10 + breathe * 0.35;
  rig.root.rotation.x = d.bodyPitch * 0.30 + crouch * 0.14;
  rig.root.rotation.z = -d.bodyRoll * 0.20;
  rig.root.rotation.y = Math.sin(t * 0.31) * 0.05 - d.bank * 0.20;

  /* ---- neck: distributes the head turn down the vertebrae ---- */
  const joints = rig.neck.joints;
  for (let i = 0; i < joints.length; i++) {
    const k = (i + 1) / (joints.length + 0.5);
    joints[i].rotation.y = st.look.x * 0.20 * k;
    joints[i].rotation.x = st.look.y * 0.14 * k + Math.sin(t * 1.3 + i) * 0.012 + crouch * 0.05 * k;
    joints[i].rotation.z = Math.sin(t * 0.8 + i * 1.4) * 0.014 + d.bodyRoll * 0.05 * k;
  }

  /* ---- head: stabilised against the body, plus the look ---- */
  const hg = rig.head.group;
  hg.rotation.y = st.look.x * 0.70 + Math.sin(t * 0.42) * 0.03;
  hg.rotation.x = st.look.y * 0.50 - d.bodyPitch * 0.45 - crouch * 0.10 + Math.sin(t * 1.1) * 0.02;
  hg.rotation.z = -st.look.x * 0.12 + d.bodyRoll * 0.18;
  hg.position.y = 0.05 + Math.sin(t * 2.3) * 0.008;

  /* ---- blink ---- */
  st.nextBlink -= dt;
  if (st.nextBlink <= 0) {
    st.blink = 1;
    st.nextBlink = 2.2 + Math.random() * 4.5;
  }
  if (st.blink > 0) {
    st.blink = Math.max(0, st.blink - dt * 9);
    const s = clamp(1 - Math.sin(st.blink * Math.PI) * 0.95, 0.05, 1);
    rig.head.eyes.forEach((e) => e.lid.scale.set(1, s, 1));
  }

  /* ---- wings out for balance ---- */
  const flap = clamp(d.flap + st.flapExtra, -1.0, 1.4);
  const gust = Math.sin(t * 2.1) * 0.045 + Math.sin(t * 5.7) * 0.02;
  for (const sgn of [1, -1]) {
    const w = sgn > 0 ? rig.wingR : rig.wingL;
    w.rotation.z = sgn * (0.16 + flap * 0.50 + gust * sgn + d.bank * 0.26 * sgn);
    w.rotation.y = sgn * (0.14 - flap * 0.16 + Math.sin(t * 1.7 + (sgn > 0 ? 0 : 0.6)) * 0.04);
    w.rotation.x = -0.08 + Math.sin(t * 2.4 + sgn) * 0.05 + d.bodyPitch * 0.22;
    w.position.y = 1.26 + flap * 0.035;
    w.position.z = 0.06 - flap * 0.05;
  }

  /* ---- pouch swings in the wind ---- */
  const swing = Math.sin(t * 2.6) * 0.03 + crouch * 0.05;
  rig.head.pouchMesh.scale.set(
    1 + swing * 0.5 + Math.sin(t * 7.3) * 0.012,
    1 - swing * 0.7 + Math.sin(t * 6.1) * 0.014,
    1 + swing * 0.3
  );
  rig.head.pouchMesh.rotation.x = swing * 0.5;

  /* ---- tail ---- */
  rig.tail.rotation.y = Math.sin(t * 1.4) * 0.13 + d.bank * 0.30;
  rig.tail.rotation.x = -0.26 + Math.sin(t * 2.0) * 0.06 - crouch * 0.22;
  rig.tail.rotation.z = -d.bodyRoll * 0.18;

  /* ---- legs: IK keeps both feet glued to the deck ---- */
  const chatter = Math.sin(t * 9.0) * 0.010 * (0.4 + crouch);
  const fT = rig.feet.front.clone();
  fT.y += chatter * 0.5;
  fT.z += Math.sin(t * 1.7) * 0.025 - crouch * 0.03;
  const bT = rig.feet.back.clone();
  bT.y -= chatter * 0.3;
  bT.z += Math.sin(t * 1.7 + 1.1) * 0.02 + crouch * 0.03;

  const hipL = rig.legL.hip.position;
  const hipR = rig.legR.hip.position;
  // hips ride with the torso, so shift the targets by the same amount
  fT.y += rig.body.position.y;
  bT.y += rig.body.position.y;
  solveLeg(rig.legL, hipL, fT);
  solveLeg(rig.legR, hipR, bT);

  // toes flex with the load
  rig.legL.toes.rotation.x = Math.sin(t * 3.1) * 0.05 - crouch * 0.12;
  rig.legR.toes.rotation.x = Math.sin(t * 3.1 + 1.2) * 0.05 - crouch * 0.12;

  return { front, back };
}
