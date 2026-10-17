import * as THREE from "three";
import { taperedTube, clamp, lerp, smoothstep, TAU } from "./util.js";

/* ------------------------------------------------------------- palette */

const C = {
  plumage: "#f8f4ec",
  plumageShade: "#ded6c8",
  nape: "#b9a88f",
  covert: "#f0eade",
  wingMid: "#9a9184",
  primary: "#4a443c",
  beak: "#ffb648",
  beakTip: "#cf8a26",
  pouch: "#ff9a5e",
  pouchDeep: "#d9714a",
  leg: "#8b8078",
  eye: "#171010",
  eyeRing: "#e6c257",
  marking: "#2f2a26",
};

const mat = (color, opts = {}) =>
  new THREE.MeshStandardMaterial(
    Object.assign({ color: new THREE.Color(color), roughness: 0.78, metalness: 0.0 }, opts)
  );

/** Feathered look: soft sheen + a generated scallop bump map. */
class MeshPhysicalFeather extends THREE.MeshPhysicalMaterial {
  constructor(bumpTex, color, extra = {}) {
    super(
      Object.assign(
        {
          color: new THREE.Color(color),
          roughness: 0.82,
          metalness: 0.0,
          sheen: 0.55,
          sheenRoughness: 0.75,
          sheenColor: new THREE.Color("#fff6e6"),
          bumpMap: bumpTex,
          bumpScale: 0.7,
        },
        extra
      )
    );
  }
}

/* ------------------------------------------------------------- wing maths */

const W = {
  span: 1.42,
  rootChord: 0.62,
  tipChord: 0.085,
  sweep: 0.36,
  leRoot: -0.3,
  camber: 0.09,
  dihedral: 0.3,
  washout: 0.24,
  fold: 0.56,
};

const chordAt = (u) => lerp(W.rootChord, W.tipChord, Math.pow(u, 0.8));
const leAt = (u) => W.leRoot + W.sweep * Math.pow(u, 1.35);
const camberAt = (u) => W.camber * (1 - 0.5 * u);
const dihedralAt = (u) => W.dihedral * Math.pow(u, 2.0);
const washAt = (u) => W.washout * Math.pow(u, 1.6);

/** Point on the (right) wing surface: u = along span, v = along chord. */
function wingPoint(u, v, out = new THREE.Vector3()) {
  const c = chordAt(u);
  const xc = leAt(u) + c * 0.5;
  const dx = (v - 0.5) * c;
  const th = washAt(u);
  return out.set(
    xc + dx * Math.cos(th),
    -dx * Math.sin(th) - camberAt(u) * Math.sin(Math.PI * v) + dihedralAt(u),
    u * W.span
  );
}

const _cA = new THREE.Color();
const _cB = new THREE.Color();
const _cC = new THREE.Color();

function wingColor(u, v, target) {
  // white coverts at the shoulder -> warm grey -> near-black primaries
  _cA.set(C.covert);
  _cB.set(C.wingMid);
  _cC.set(C.primary);
  let c;
  if (u < 0.46) {
    c = _cA.clone().lerp(_cB, smoothstep(0.3, 0.58, u));
  } else {
    c = _cB.clone().lerp(_cC, smoothstep(0.58, 0.88, u));
  }
  // pale trailing-edge band on the outer wing
  c.lerp(_cA.clone(), smoothstep(0.92, 1.0, v) * 0.35 * smoothstep(0.4, 0.8, u));
  // darker leading edge strip
  c.multiplyScalar(1 - 0.18 * smoothstep(0.14, 0.0, v) * smoothstep(0.3, 0.9, u));
  // mottling
  const m = 0.94 + 0.12 * Math.abs(Math.sin(u * 41.7) * Math.sin(v * 27.3 + u * 9.1));
  c.multiplyScalar(m);
  target.copy(c);
  return target;
}

function wingGeometry(u0, u1, spanSegs, chordSegs) {
  const positions = [];
  const uvs = [];
  const indices = [];

  for (let i = 0; i <= spanSegs; i++) {
    const u = lerp(u0, u1, i / spanSegs);
    for (let j = 0; j <= chordSegs; j++) {
      const v = j / chordSegs;
      const p = wingPoint(u, v);
      positions.push(p.x, p.y, p.z);
      uvs.push(u * 3.2, v * 1.1);
    }
  }
  for (let i = 0; i < spanSegs; i++) {
    for (let j = 0; j < chordSegs; j++) {
      const a = i * (chordSegs + 1) + j;
      const b = a + chordSegs + 1;
      indices.push(a, b, a + 1, a + 1, b, b + 1);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geo.setIndex(indices);
  geo.computeVertexNormals();

  // per-vertex plumage gradient
  const pos = geo.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const p = new THREE.Vector3();
  const col = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    p.fromBufferAttribute(pos, i);
    // recover u/v from the (known) grid ordering
    const gi = Math.floor(i / (chordSegs + 1));
    const gj = i % (chordSegs + 1);
    const u = lerp(u0, u1, gi / spanSegs);
    const v = gj / chordSegs;
    wingColor(u, v, col);
    colors[i * 3] = col.r;
    colors[i * 3 + 1] = col.g;
    colors[i * 3 + 2] = col.b;
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  return geo;
}

/** A single flat flight feather pointing +X, width along Z. */
function featherGeometry(len, wRoot) {
  const s = new THREE.Shape();
  s.moveTo(0, -wRoot * 0.42);
  s.bezierCurveTo(len * 0.3, -wRoot * 0.55, len * 0.72, -wRoot * 0.3, len, 0);
  s.bezierCurveTo(len * 0.72, wRoot * 0.3, len * 0.3, wRoot * 0.55, 0, wRoot * 0.42);
  s.closePath();
  const g = new THREE.ShapeGeometry(s, 16);
  g.rotateX(-Math.PI / 2);
  return g;
}

/* ------------------------------------------------------------- assembly */

export function createPelican({ featherTex }) {
  const root = new THREE.Group(); // origin = deck level, forward = +X

  const feather = new MeshPhysicalFeather(featherTex, C.plumage);
  const featherShade = new MeshPhysicalFeather(featherTex, C.plumageShade, {
    sheen: 0.35,
    roughness: 0.88,
  });
  const wingMat = new THREE.MeshPhysicalMaterial({
    vertexColors: true,
    side: THREE.DoubleSide,
    roughness: 0.85,
    metalness: 0.0,
    sheen: 0.5,
    sheenRoughness: 0.8,
    sheenColor: new THREE.Color("#fff3e0"),
    bumpMap: featherTex,
    bumpScale: 0.45,
  });
  const darkFeather = mat(C.primary, { roughness: 0.72, side: THREE.DoubleSide });
  const beakMat = mat(C.beak, { roughness: 0.42 });
  const beakTipMat = mat(C.beakTip, { roughness: 0.5 });
  const pouchMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(C.pouch),
    roughness: 0.42,
    metalness: 0.0,
    clearcoat: 0.25,
    clearcoatRoughness: 0.7,
    side: THREE.DoubleSide,
  });
  const legMat = mat(C.leg, { roughness: 0.62 });
  const eyeMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(C.eye),
    roughness: 0.08,
    metalness: 0.0,
    clearcoat: 1.0,
    clearcoatRoughness: 0.05,
  });
  const ringMat = mat(C.eyeRing, { roughness: 0.55 });

  const add = (geo, material, x = 0, y = 0, z = 0, parent = root) => {
    const m = new THREE.Mesh(geo, material);
    m.position.set(x, y, z);
    parent.add(m);
    return m;
  };

  /* ---- torso: lathe profile, axis along X -------------------------- */
  const profile = [
    [-0.68, 0.03],
    [-0.56, 0.19],
    [-0.4, 0.31],
    [-0.2, 0.4],
    [0.02, 0.435],
    [0.24, 0.42],
    [0.42, 0.35],
    [0.56, 0.24],
    [0.66, 0.12],
    [0.7, 0.02],
  ].map((p) => new THREE.Vector2(Math.max(p[1], 0.001), p[0]));

  const torsoGeo = new THREE.LatheGeometry(profile, 40);
  torsoGeo.rotateZ(-Math.PI / 2); // lathe axis Y -> +X (forward)
  torsoGeo.scale(1, 1.04, 0.88);

  const bodyGroup = new THREE.Group();
  bodyGroup.position.set(0.0, 0.8, 0);
  root.add(bodyGroup);

  add(torsoGeo, feather, 0.02, 0, 0, bodyGroup);

  // breast / belly highlight + rump
  const breast = add(new THREE.SphereGeometry(0.34, 28, 20), feather, 0.3, -0.1, 0, bodyGroup);
  breast.scale.set(1.05, 0.88, 0.85);
  const rump = add(new THREE.SphereGeometry(0.3, 24, 18), featherShade, -0.42, 0.02, 0, bodyGroup);
  rump.scale.set(1.2, 0.9, 0.85);

  /* ---- tail fan ---------------------------------------------------- */
  const tailGroup = new THREE.Group();
  tailGroup.position.set(-0.62, 0.06, 0);
  tailGroup.rotation.z = 0.3;
  bodyGroup.add(tailGroup);
  const tailFeathers = [];
  for (let i = 0; i < 5; i++) {
    const f = i / 4 - 0.5; // -0.5 .. 0.5
    const pivot = new THREE.Group();
    pivot.rotation.y = f * 0.42;
    pivot.rotation.x = -f * 0.18;
    tailGroup.add(pivot);
    const geo = featherGeometry(0.5, 0.11);
    geo.rotateY(Math.PI); // point backward (-X)
    const m = new THREE.Mesh(geo, i % 2 ? darkFeather : featherShade);
    m.scale.set(1 - Math.abs(f) * 0.25, 1, 1);
    m.position.set(0.02, -Math.abs(f) * 0.02, f * 0.05);
    pivot.add(m);
    tailFeathers.push(pivot);
  }

  /* ---- neck -------------------------------------------------------- */
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.32, 0.14, 0),
    new THREE.Vector3(0.52, 0.38, 0),
    new THREE.Vector3(0.5, 0.66, 0),
    new THREE.Vector3(0.62, 0.9, 0),
    new THREE.Vector3(0.7, 1.02, 0),
  ]);
  const neckGeo = taperedTube(neckCurve, 30, (u) => lerp(0.24, 0.12, Math.pow(u, 0.8)), 16);
  // buff-yellow nape on the back of the neck, blended in through vertex colours
  {
    const nrm = neckGeo.attributes.normal;
    const pos = neckGeo.attributes.position;
    const base = new THREE.Color(C.plumage);
    const nape = new THREE.Color(C.nape);
    const colors = new Float32Array(pos.count * 3);
    const c = new THREE.Color();
    for (let i = 0; i < pos.count; i++) {
      const back = smoothstep(-0.05, -0.8, nrm.getX(i));
      const up = smoothstep(0.2, 0.9, nrm.getY(i)) * 0.35;
      c.copy(base).lerp(nape, clamp(back + up * back, 0, 1) * 0.85);
      // soft grey shading under the belly of the neck
      c.lerp(new THREE.Color(C.plumageShade), smoothstep(0.0, -0.9, nrm.getY(i)) * 0.5);
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
    neckGeo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  }
  const neckMat = new MeshPhysicalFeather(featherTex, "#ffffff", { vertexColors: true });
  add(neckGeo, neckMat, 0, 0, 0, bodyGroup);

  /* ---- head -------------------------------------------------------- */
  const headGroup = new THREE.Group();
  headGroup.position.set(0.72, 1.06, 0);
  bodyGroup.add(headGroup);

  const skull = add(new THREE.SphereGeometry(0.145, 30, 22), feather, 0.06, 0.02, 0, headGroup);
  skull.scale.set(1.32, 1.06, 1.0);
  const crown = add(new THREE.SphereGeometry(0.11, 22, 16), featherShade, 0.0, 0.07, 0, headGroup);
  crown.scale.set(1.2, 0.7, 1.0);

  // little nape crest
  for (let i = 0; i < 3; i++) {
    const g = featherGeometry(0.16, 0.05);
    g.rotateY(Math.PI);
    const m = new THREE.Mesh(g, featherShade);
    m.position.set(-0.05, 0.06 - i * 0.035, (i - 1) * 0.05);
    m.rotation.z = 0.5 + i * 0.12;
    m.rotation.y = (i - 1) * 0.2;
    headGroup.add(m);
  }

  /* ---- eyes -------------------------------------------------------- */
  for (const s of [-1, 1]) {
    const eye = add(new THREE.SphereGeometry(0.042, 20, 16), eyeMat, 0.115, 0.05, s * 0.115, headGroup);
    eye.scale.set(1, 1, 0.6);
    const ring = add(new THREE.TorusGeometry(0.052, 0.011, 8, 22), ringMat, 0.108, 0.05, s * 0.128, headGroup);
    ring.rotation.y = Math.PI / 2;
    ring.scale.set(1, 1, 0.7);
    // dark lore stripe running back from the eye
    const stripe = add(new THREE.SphereGeometry(0.05, 16, 12), mat(C.marking, { roughness: 0.9 }), -0.02, 0.045, s * 0.115, headGroup);
    stripe.scale.set(1.7, 0.42, 0.4);
    // catch light
    const glint = add(
      new THREE.SphereGeometry(0.012, 10, 8),
      new THREE.MeshBasicMaterial({ color: new THREE.Color("#fff6e2") }),
      0.145,
      0.072,
      s * 0.126,
      headGroup
    );
    glint.scale.set(1, 1, 0.5);
  }

  /* ---- bill + gular pouch ------------------------------------------ */
  const billGroup = new THREE.Group();
  billGroup.position.set(0.16, 0.0, 0);
  headGroup.add(billGroup);

  const upperCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.02, 0.03, 0),
    new THREE.Vector3(0.22, 0.015, 0),
    new THREE.Vector3(0.45, -0.015, 0),
    new THREE.Vector3(0.62, -0.06, 0),
  ]);
  const upperGeo = taperedTube(upperCurve, 26, (u) => lerp(0.082, 0.011, Math.pow(u, 0.8)), 14);
  upperGeo.scale(1, 0.62, 1);
  add(upperGeo, beakMat, 0, 0, 0, billGroup);
  // hooked tip
  const hookGeo = new THREE.ConeGeometry(0.022, 0.07, 10);
  hookGeo.rotateZ(Math.PI);
  hookGeo.scale(1, 1, 0.7);
  add(hookGeo, beakTipMat, 0.63, -0.085, 0, billGroup);

  // lower jaw pivots at the back of the bill so the pouch can gape
  const jawGroup = new THREE.Group();
  jawGroup.position.set(-0.02, -0.015, 0);
  billGroup.add(jawGroup);

  const pouchGeo = new THREE.SphereGeometry(1, 26, 18);
  const pPos = pouchGeo.attributes.position;
  for (let i = 0; i < pPos.count; i++) {
    const x = pPos.getX(i);
    const y = pPos.getY(i);
    const z = pPos.getZ(i);
    // teardrop: fuller at the back, tapering to the bill tip, sagging downward
    const t = clamp((x + 1) * 0.5, 0, 1);
    const taper = Math.pow(Math.sin(Math.PI * Math.pow(t, 0.62)), 0.65);
    pPos.setXYZ(i, x * 0.3, y * 0.115 * taper - (1 - taper) * 0.012, z * 0.095 * taper);
  }
  pouchGeo.computeVertexNormals();
  pouchGeo.translate(0.3, -0.075, 0);
  const pouch = add(pouchGeo, pouchMat, 0, 0, 0, jawGroup);
  pouch.scale.set(1, 1, 1);

  for (const s of [-1, 1]) {
    const lowerCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0.0, 0.0, s * 0.055),
      new THREE.Vector3(0.24, -0.035, s * 0.05),
      new THREE.Vector3(0.46, -0.075, s * 0.03),
      new THREE.Vector3(0.6, -0.1, s * 0.006),
    ]);
    const lg = taperedTube(lowerCurve, 20, (u) => lerp(0.021, 0.005, u), 8);
    add(lg, beakMat, 0, 0, 0, jawGroup);
  }

  /* ---- wings ------------------------------------------------------- */
  const wings = [];
  for (const side of [1, -1]) {
    const shoulder = new THREE.Group();
    shoulder.position.set(-0.02, 0.3, side * 0.24);
    bodyGroup.add(shoulder);

    const innerGeo = wingGeometry(0, W.fold, 20, 9);
    add(innerGeo, wingMat, 0, 0, 0, shoulder);

    // wrist / outer wing
    const anchor = wingPoint(W.fold, 0.5);
    const wrist = new THREE.Group();
    wrist.position.copy(anchor);
    shoulder.add(wrist);

    const outerGeo = wingGeometry(W.fold, 1.0, 16, 8);
    outerGeo.translate(-anchor.x, -anchor.y, -anchor.z);
    add(outerGeo, wingMat, 0, 0, 0, wrist);

    // primary feathers fanned off the wrist
    const primaries = [];
    for (let k = 0; k < 5; k++) {
      const u = 0.62 + k * 0.085;
      const at = wingPoint(u, 1.0);
      const pivot = new THREE.Group();
      pivot.position.set(at.x - anchor.x, at.y - anchor.y, at.z - anchor.z);
      pivot.rotation.y = 0.1 + k * 0.05;
      pivot.rotation.z = -0.06 - k * 0.03;
      wrist.add(pivot);
      const len = 0.16 + k * 0.035;
      const g = featherGeometry(len, 0.075);
      const m = new THREE.Mesh(g, darkFeather);
      pivot.add(m);
      primaries.push(pivot);
    }

    // mirrored side
    if (side === -1) {
      shoulder.scale.z = -1;
    }
    wings.push({ side, shoulder, wrist, primaries });
  }

  /* ---- legs + webbed feet ------------------------------------------ */
  const legsGroup = new THREE.Group();
  root.add(legsGroup);

  const footShape = new THREE.Shape();
  footShape.moveTo(-0.06, 0);
  footShape.lineTo(0.06, 0.075);
  footShape.lineTo(0.19, 0.1);
  footShape.lineTo(0.12, 0.035);
  footShape.lineTo(0.22, 0.0);
  footShape.lineTo(0.12, -0.035);
  footShape.lineTo(0.19, -0.1);
  footShape.lineTo(0.06, -0.075);
  footShape.lineTo(-0.05, -0.03);
  footShape.closePath();
  const footGeo = new THREE.ExtrudeGeometry(footShape, {
    depth: 0.018,
    bevelEnabled: true,
    bevelThickness: 0.006,
    bevelSize: 0.006,
    bevelSegments: 2,
    curveSegments: 4,
  });
  footGeo.rotateX(-Math.PI / 2);
  footGeo.translate(0, 0.008, 0);

  const legs = [];
  const stance = [
    { hip: [0.05, 0.6, 0.11], knee: [0.14, 0.34, 0.15], ankle: [0.28, 0.13, 0.13], foot: [0.31, 0.0, 0.13], yaw: -0.2 },
    { hip: [-0.22, 0.6, -0.1], knee: [-0.3, 0.34, -0.14], ankle: [-0.46, 0.14, -0.12], foot: [-0.5, 0.0, -0.12], yaw: 0.32 },
  ];
  for (const s of stance) {
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(...s.hip),
      new THREE.Vector3(...s.knee),
      new THREE.Vector3(...s.ankle),
    ]);
    const legGeo = taperedTube(curve, 18, (u) => lerp(0.075, 0.042, u), 10);
    add(legGeo, legMat, 0, 0, 0, legsGroup);
    add(new THREE.SphereGeometry(0.072, 14, 12), legMat, s.knee[0], s.knee[1], s.knee[2], legsGroup);
    // ankle -> foot
    const lowerCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(...s.ankle),
      new THREE.Vector3(s.foot[0] - 0.02, 0.06, s.foot[2]),
      new THREE.Vector3(s.foot[0], 0.02, s.foot[2]),
    ]);
    add(taperedTube(lowerCurve, 12, (u) => lerp(0.042, 0.03, u), 8), legMat, 0, 0, 0, legsGroup);
    const foot = add(footGeo, legMat, s.foot[0], 0, s.foot[2], legsGroup);
    foot.rotation.y = s.yaw;
    foot.scale.setScalar(1.45);
    // thigh feathers hiding the hip joint
    const thigh = add(new THREE.SphereGeometry(0.15, 18, 14), featherShade, s.hip[0], s.hip[1] - 0.03, s.hip[2], legsGroup);
    thigh.scale.set(1.15, 1.25, 0.95);
    legs.push({ foot, thigh });
  }

  /* ---- animation ---------------------------------------------------- */

  // flap bursts: a quasi-random schedule so it never looks like a metronome
  const flapTimes = [];
  let ft = 6;
  for (let i = 0; i < 40; i++) {
    ft += 5.5 + ((Math.sin(i * 12.9898) * 43758.5453) % 1 + 1) % 1 * 7;
    flapTimes.push(ft);
  }
  let flapIndex = 0;
  let flapPhase = -1;
  const FLAP_DUR = 1.5;

  const state = {
    lean: 0,
    bank: 0,
    bob: 0,
    headYaw: 0,
    headPitch: 0,
    headTilt: 0,
    jaw: 0,
    pouchBulge: 1,
  };

  function update(t, dt, ctx) {
    // ---- flap scheduler
    if (flapPhase < 0 && flapIndex < flapTimes.length && t >= flapTimes[flapIndex]) {
      flapPhase = 0;
      flapIndex++;
    }
    let flap = 0;
    let flapRate = 0;
    if (flapPhase >= 0) {
      flapPhase += dt;
      const k = flapPhase / FLAP_DUR;
      if (k >= 1) {
        flapPhase = -1;
      } else {
        const env = Math.sin(Math.PI * k); // 0..1..0
        flap = Math.sin(k * TAU * 1.6) * env;
        flapRate = Math.cos(k * TAU * 1.6) * env;
      }
    }

    // ---- body: leans against the board's motion, bobs with the swell
    const targetLean = clamp(-ctx.pitch * 0.75 + ctx.accelX * 0.09, -0.3, 0.34);
    const targetBank = clamp(ctx.roll * 0.4, -0.32, 0.32);
    state.lean = lerp(state.lean, targetLean, 1 - Math.exp(-4.5 * dt));
    state.bank = lerp(state.bank, targetBank, 1 - Math.exp(-3.5 * dt));
    state.bob = Math.sin(t * 1.7) * 0.012 + ctx.heave * 0.05;

    bodyGroup.rotation.z = state.lean + Math.sin(t * 0.9) * 0.012;
    bodyGroup.rotation.x = state.bank;
    bodyGroup.rotation.y = Math.sin(t * 0.43) * 0.035 + clamp(ctx.yawRate * 0.35, -0.14, 0.14);
    bodyGroup.position.y = 0.8 + state.bob - Math.abs(flap) * 0.02;
    bodyGroup.position.x = -ctx.accelX * 0.012;

    // ---- wings: mostly a stiff glide, correcting balance, with flap bursts
    const gust = Math.sin(t * 1.31) * 0.5 + Math.sin(t * 2.17 + 1.3) * 0.28;
    // dihedral > 0 = tips up. Each wing also cancels the body's lean on its own
    // side, so the wings stay level in world space while the hull heels over.
    const baseDihedral = 0.09 + gust * 0.05 + flap * 0.62 + clamp(ctx.roll * 0.12, -0.1, 0.1);
    for (const w of wings) {
      const s = w.side;
      const dihedral = baseDihedral + s * state.bank * 1.05;
      // NOTE the left shoulder is mirrored (scale.z = -1): a mirror applied *before*
      // the shoulder's own rotation flips the sign of rotation.x / rotation.y,
      // while the wrist (rotated *inside* the mirrored frame) keeps the same sign.
      w.shoulder.rotation.x = -s * dihedral;
      w.shoulder.rotation.y = s * (-0.06 - flap * 0.22) + Math.sin(t * 0.7 + s) * 0.03 * s;
      w.shoulder.rotation.z = 0.04 + Math.abs(flap) * 0.05;
      w.wrist.rotation.x = -(0.05 + flapRate * 0.3 - gust * 0.03);
      w.wrist.rotation.y = 0.05 + Math.abs(flap) * 0.12;
      for (let k = 0; k < w.primaries.length; k++) {
        const p = w.primaries[k];
        const f = Math.sin(t * 6.1 + k * 0.9 + (s > 0 ? 0 : 1.7)) * 0.06 * (1 + Math.abs(flapRate));
        p.rotation.z = -0.06 - k * 0.03 + f;
        p.rotation.x = Math.sin(t * 4.3 + k * 1.3) * 0.05;
      }
    }

    // ---- head: stabilised gaze with slow scans and the occasional tilt
    const scan = Math.sin(t * 0.31) * 0.5 + Math.sin(t * 0.13 + 2.0) * 0.5;
    state.headYaw = lerp(state.headYaw, scan * 0.42 - ctx.yawRate * 0.5, 1 - Math.exp(-2.2 * dt));
    state.headPitch = lerp(
      state.headPitch,
      Math.sin(t * 0.24 + 1.1) * 0.1 - ctx.pitch * 0.55 + 0.04,
      1 - Math.exp(-2.6 * dt)
    );
    state.headTilt = lerp(
      state.headTilt,
      Math.sin(t * 0.19 + 0.4) * 0.16 + Math.sin(t * 0.07) * 0.1,
      1 - Math.exp(-1.8 * dt)
    );
    headGroup.rotation.y = state.headYaw;
    headGroup.rotation.z = state.headPitch - bodyGroup.rotation.z * 0.55;
    headGroup.rotation.x = state.headTilt - bodyGroup.rotation.x * 0.4;

    // ---- bill: gapes to cool off, pouch jiggles with the ride
    const gape =
      0.04 +
      0.03 * Math.sin(t * 0.6) +
      Math.max(0, Math.sin(t * 0.21 - 1.2)) ** 6 * 0.5 +
      Math.abs(flap) * 0.12;
    state.jaw = lerp(state.jaw, gape, 1 - Math.exp(-6 * dt));
    jawGroup.rotation.z = -state.jaw;
    const jiggle = Math.sin(t * 9.3) * 0.03 + ctx.heave * 0.5 + Math.abs(flapRate) * 0.05;
    pouch.scale.set(1 + jiggle * 0.16, 1 - jiggle * 0.3 + state.jaw * 0.5, 1 + jiggle * 0.2 + state.jaw * 0.35);
    pouch.position.y = -state.jaw * 0.04;

    // ---- tail feathers stream and twitch
    for (let i = 0; i < tailFeathers.length; i++) {
      const f = (i / (tailFeathers.length - 1) - 0.5) * 2;
      tailFeathers[i].rotation.z =
        -0.1 + Math.sin(t * 2.3 + i * 0.8) * 0.05 - Math.abs(flap) * 0.12 - ctx.pitch * 0.2;
      tailFeathers[i].rotation.x = f * 0.1 + Math.sin(t * 1.7 + i) * 0.03;
    }

    return { flap: Math.abs(flap), flapRate };
  }

  return { root, bodyGroup, headGroup, wings, update };
}
