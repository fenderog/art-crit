import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import {
  axisLoft,
  makeTube,
  featherGeometry,
  featherTexture,
  plumageTexture,
  clamp,
  lerp,
  smoothstep,
} from "./geo.js";

const DEG = Math.PI / 180;
const V3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

// ---------------------------------------------------------------- palette ---
const COL = {
  plumage: 0xfbf7ef,
  skin: 0xf2a73b,
  billTop: [0.96, 0.62, 0.15],
  billSide: [0.93, 0.4, 0.06],
  billHook: [0.72, 0.2, 0.1],
  pouch: [0.96, 0.56, 0.3],
  leg: 0xe08a3c,
  foot: 0xf0993f,
  flight: [0.045, 0.047, 0.055],
  flightGrey: [0.2, 0.21, 0.23],
};

function makeMaterials() {
  const plumageTex = plumageTexture();
  plumageTex.repeat.set(2.4, 2.0);
  const fTex = featherTexture();
  const plumage = new THREE.MeshPhysicalMaterial({
    color: COL.plumage,
    map: plumageTex,
    bumpMap: plumageTex,
    bumpScale: 0.12,
    roughness: 0.9,
    sheen: 0.7,
    sheenRoughness: 0.55,
    sheenColor: new THREE.Color(0xfff6e8),
  });
  const feather = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    vertexColors: true,
    map: fTex,
    bumpMap: fTex,
    bumpScale: 1.2,
    roughness: 0.85,
    side: THREE.DoubleSide,
    specularIntensity: 0.3,
    sheen: 0.12,
    sheenRoughness: 0.7,
    sheenColor: new THREE.Color(0xffffff),
  });
  const bill = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    vertexColors: true,
    roughness: 0.42,
    clearcoat: 0.5,
    clearcoatRoughness: 0.3,
    emissive: new THREE.Color(0x3a1400),
    emissiveIntensity: 0.35,
  });
  const pouch = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    vertexColors: true,
    roughness: 0.55,
    side: THREE.DoubleSide,
    clearcoat: 0.25,
    emissive: new THREE.Color(0x5a2208),
    emissiveIntensity: 0.4,
  });
  const skin = new THREE.MeshStandardMaterial({ color: COL.skin, roughness: 0.55 });
  const leg = new THREE.MeshStandardMaterial({ color: COL.leg, roughness: 0.6 });
  const foot = new THREE.MeshStandardMaterial({ color: COL.foot, roughness: 0.55, side: THREE.DoubleSide });
  const eye = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    vertexColors: true,
    roughness: 0.15,
    clearcoat: 1,
    clearcoatRoughness: 0.05,
  });
  const glint = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 2.4, 2.2), toneMapped: false });
  return { plumage, feather, bill, pouch, skin, leg, foot, eye, glint };
}

function shadowAll(obj) {
  obj.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  return obj;
}

// ------------------------------------------------------------------ body ----
function buildBody(mat) {
  const rows = [
    [-0.5, 0.025, 0, 0.0, 0.0],
    [-0.47, 0.025, 0, 0.032, 0.03],
    [-0.4, 0.018, 0, 0.08, 0.072],
    [-0.28, 0.0, 0, 0.155, 0.142],
    [-0.12, -0.006, 0, 0.238, 0.225],
    [0.04, 0.0, 0, 0.272, 0.25],
    [0.18, 0.02, 0, 0.262, 0.24],
    [0.3, 0.052, 0, 0.215, 0.195],
    [0.39, 0.088, 0, 0.132, 0.118],
    [0.44, 0.118, 0, 0.062, 0.056],
    [0.455, 0.13, 0, 0.0, 0.0],
  ];
  const g = axisLoft(rows, 44, 34);
  return new THREE.Mesh(g, mat.plumage);
}

// ------------------------------------------------------------------ bill ----
const BILL = { x0: 0.08, L: 0.6 };
function billCenter(u) {
  const hook = smoothstep(0.84, 1.0, u);
  return -0.018 - 0.05 * u * u - 0.06 * hook * hook;
}
function billHalf(u) {
  const w = [0.054, 0.066, 0.058, 0.045, 0.029, 0.016, 0.008];
  const h = [0.048, 0.042, 0.035, 0.028, 0.022, 0.017, 0.012];
  const f = clamp(u, 0, 1) * (w.length - 1);
  const i = Math.min(Math.floor(f), w.length - 2);
  const t = f - i;
  const s = t * t * (3 - 2 * t);
  return [lerp(w[i], w[i + 1], s), lerp(h[i], h[i + 1], s)];
}

function buildUpperBill(mat) {
  const nU = 34;
  const nV = 22;
  const pos = [];
  const col = [];
  const idx = [];
  for (let i = 0; i <= nU; i++) {
    const u = i / nU;
    const x = BILL.x0 + BILL.L * u;
    const yc = billCenter(u);
    const [w, h] = billHalf(u);
    const end = i === nU ? 0 : 1;
    for (let j = 0; j <= nV; j++) {
      const a = (j / nV) * Math.PI * 2;
      const c = Math.cos(a);
      const s = Math.sin(a);
      const top = s > 0;
      const y = yc + h * (top ? Math.pow(s, 0.8) : 0.55 * s) * end;
      const z = w * c * (1 - 0.12 * (top ? s * s : 0)) * end;
      pos.push(x, y, z);
      // colour: lighter ridge, orange sides, red hooked nail
      const ridge = smoothstep(0.1, 0.95, Math.max(s, 0));
      let r = lerp(COL.billSide[0], COL.billTop[0], ridge);
      let gch = lerp(COL.billSide[1], COL.billTop[1], ridge);
      let b = lerp(COL.billSide[2], COL.billTop[2], ridge);
      const hk = smoothstep(0.9, 0.985, u);
      r = lerp(r, COL.billHook[0], hk);
      gch = lerp(gch, COL.billHook[1], hk);
      b = lerp(b, COL.billHook[2], hk);
      col.push(r, gch, b);
    }
  }
  for (let i = 0; i < nU; i++) {
    for (let j = 0; j < nV; j++) {
      const a = i * (nV + 1) + j;
      const b = a + 1;
      const c = a + nV + 1;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return new THREE.Mesh(g, mat.bill);
}

// Lower mandible with the hanging gular pouch (re-built every frame).
function buildPouch(mat) {
  const nU = 26;
  const nV = 14;
  const geom = new THREE.BufferGeometry();
  const pos = new Float32Array((nU + 1) * (nV + 1) * 3);
  const col = new Float32Array((nU + 1) * (nV + 1) * 3);
  const idx = [];
  for (let i = 0; i < nU; i++) {
    for (let j = 0; j < nV; j++) {
      const a = i * (nV + 1) + j;
      const b = a + 1;
      const c = a + nV + 1;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  geom.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geom.setAttribute("color", new THREE.BufferAttribute(col, 3));
  geom.setIndex(idx);
  const mesh = new THREE.Mesh(geom, mat.pouch);
  mesh.frustumCulled = false;
  const hinge = { x: BILL.x0 + 0.02, y: -0.04 };

  mesh.userData.update = (gape, sag, wob) => {
    for (let i = 0; i <= nU; i++) {
      // u from -0.3 (throat) to 1 (tip)
      const u = -0.3 + (1.3 * i) / nU;
      const uu = clamp(u, 0, 1);
      const [w0, h0] = billHalf(uu);
      let cx;
      let cy;
      let w;
      let depth;
      if (u >= 0) {
        cx = BILL.x0 + BILL.L * u;
        cy = billCenter(u) - h0 * 0.85 - 0.006;
        w = w0 * 0.97;
        const k = clamp(u / 0.92, 0, 1);
        depth = (0.125 + 0.05 * sag) * Math.pow(Math.sin(Math.PI * Math.pow(k, 0.72)), 0.85) + 0.012 * (1 - k);
        depth += wob * 0.02 * Math.sin(u * 5.0) * (1 - u);
        if (u > 0.9) depth *= 1 - smoothstep(0.9, 1.0, u);
        depth = Math.max(depth, 0.001);
      } else {
        const k = -u / 0.3; // 0 at bill base, 1 at throat end
        cx = BILL.x0 - 0.1 * k;
        cy = billCenter(0) - 0.048 - 0.1 * k;
        w = lerp(0.052, 0.014, k);
        depth = lerp(0.085 + 0.025 * sag, 0.004, k * k);
      }
      // gape: rotate the front part about the jaw hinge
      const gk = gape * smoothstep(0.0, 0.25, u);
      const cs = Math.cos(gk);
      const sn = Math.sin(gk);
      const dx = cx - hinge.x;
      const dy = cy - hinge.y;
      const rx = hinge.x + dx * cs + dy * sn;
      const ry = hinge.y - dx * sn + dy * cs;
      // ring "down" axis after rotation
      const downX = sn;
      const downY = -cs;
      for (let j = 0; j <= nV; j++) {
        const a = (j / nV) * Math.PI;
        const lat = Math.cos(a);
        const dn = Math.sin(a);
        const o = (i * (nV + 1) + j) * 3;
        pos[o] = rx + downX * depth * dn;
        pos[o + 1] = ry + downY * depth * dn;
        pos[o + 2] = w * lat;
        const k2 = Math.max(0, dn);
        const fade = smoothstep(-0.3, 0.2, u);
        col[o] = lerp(1.0, COL.pouch[0], 0.4 + 0.6 * fade) * (0.88 + 0.12 * k2);
        col[o + 1] = lerp(0.82, COL.pouch[1], fade) * (0.85 + 0.15 * k2);
        col[o + 2] = lerp(0.7, COL.pouch[2], fade) * (0.8 + 0.2 * k2);
      }
    }
    geom.attributes.position.needsUpdate = true;
    geom.attributes.color.needsUpdate = true;
    geom.computeVertexNormals();
  };
  return mesh;
}

// ------------------------------------------------------------------ eyes ----
function buildEye(mat, side) {
  const g = new THREE.Group();
  const R = 0.021;
  const geo = new THREE.SphereGeometry(R, 44, 30);
  const gaze = new THREE.Vector3(0.38, 0.08, 0.92 * side).normalize();
  const pos = geo.attributes.position;
  const col = new Float32Array(pos.count * 3);
  const v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i).normalize();
    const a = Math.acos(clamp(v.dot(gaze), -1, 1));
    let c;
    if (a < 0.3) c = [0.015, 0.012, 0.012];
    else if (a < 0.34) {
      const t = (a - 0.3) / 0.04;
      c = [lerp(0.015, 0.9, t), lerp(0.012, 0.85, t), lerp(0.012, 0.55, t)];
    } else if (a < 0.66) {
      const t = (a - 0.34) / 0.32;
      c = [lerp(0.96, 0.82, t), lerp(0.9, 0.62, t), lerp(0.62, 0.22, t)];
    } else {
      const t = smoothstep(0.66, 0.78, a);
      c = [lerp(0.82, 0.16, t), lerp(0.6, 0.1, t), lerp(0.2, 0.06, t)];
    }
    col[i * 3] = c[0];
    col[i * 3 + 1] = c[1];
    col[i * 3 + 2] = c[2];
  }
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const ball = new THREE.Mesh(geo, mat.eye);
  g.add(ball);
  // bright specular glint
  const glint = new THREE.Mesh(new THREE.SphereGeometry(0.0034, 10, 8), mat.glint);
  const gd = gaze.clone().applyAxisAngle(new THREE.Vector3(1, 0, 0), -0.55 * side).applyAxisAngle(new THREE.Vector3(0, 1, 0), 0.25);
  glint.position.copy(gd).multiplyScalar(R * 0.985);
  g.add(glint);
  // upper lid: hemisphere rotating around the fore-aft axis
  const lidGeo = new THREE.SphereGeometry(R * 1.07, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2);
  const lid = new THREE.Mesh(lidGeo, mat.skin);
  const lidPivot = new THREE.Group();
  lidPivot.add(lid);
  g.add(lidPivot);
  const lowGeo = new THREE.SphereGeometry(R * 1.07, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2);
  const lowLid = new THREE.Mesh(lowGeo, mat.skin);
  lowLid.rotation.x = Math.PI;
  const lowPivot = new THREE.Group();
  lowPivot.add(lowLid);
  g.add(lowPivot);
  g.userData.setLid = (open, squint) => {
    // open: 0 closed .. 1 open; squint lowers the upper lid a little
    const a = lerp(-0.62, 0.78, open) - squint * 0.5;
    lidPivot.rotation.x = -side * a;
    lowPivot.rotation.x = side * lerp(-0.3, 0.95, open);
  };
  g.userData.setLid(1, 0);
  return g;
}

// ------------------------------------------------------------------ wings ---
const WING = { L1: 0.26, L2: 0.32, L3: 0.27 };

function flightFeatherGeo(kind) {
  if (kind === "primary") {
    return featherGeometry({
      segs: 10,
      across: 4,
      lead: 0.3,
      trail: 0.7,
      droop: 0.1,
      camber: 0.1,
      tip: 0.3,
      base: 0.5,
      colorFn: (t, v) => {
        const k = smoothstep(0.12, 0.34, t);
        const edge = 0.9 + 0.1 * Math.sin(v * 3.1);
        return [lerp(0.95, COL.flight[0] * edge, k), lerp(0.95, COL.flight[1] * edge, k), lerp(0.95, COL.flight[2] * edge, k)];
      },
    });
  }
  if (kind === "secondary") {
    return featherGeometry({
      segs: 10,
      across: 4,
      lead: 0.3,
      trail: 0.7,
      droop: 0.08,
      camber: 0.09,
      tip: 0.34,
      base: 0.5,
      colorFn: (t, v) => {
        const k = smoothstep(0.16, 0.42, t);
        const c = [lerp(COL.flightGrey[0], COL.flight[0], smoothstep(0.5, 1, t)), lerp(COL.flightGrey[1], COL.flight[1], smoothstep(0.5, 1, t)), lerp(COL.flightGrey[2], COL.flight[2], smoothstep(0.5, 1, t))];
        return [lerp(0.95, c[0], k), lerp(0.95, c[1], k), lerp(0.95, c[2], k)];
      },
    });
  }
  // coverts and body feathers: white
  return featherGeometry({
    segs: 6,
    across: 3,
    lead: 0.4,
    trail: 0.6,
    droop: 0.1,
    camber: 0.12,
    tip: 0.5,
    base: 0.85,
    colorFn: (t) => [0.98, 0.97, 0.94].map((x) => x * (0.92 + 0.08 * t)),
  });
}

function buildWing(side, mat, geos) {
  const wing = { side, primaries: [], secondaries: [], tertials: [] };
  const frame = new THREE.Group();
  frame.rotation.y = -side * (Math.PI / 2);
  frame.scale.z = side;
  const joint = new THREE.Group(); // shoulder joint
  frame.add(joint);
  const elbow = new THREE.Group();
  elbow.position.x = WING.L1;
  joint.add(elbow);
  const wrist = new THREE.Group();
  wrist.position.x = WING.L2;
  elbow.add(wrist);
  wing.frame = frame;
  wing.joint = joint;
  wing.elbow = elbow;
  wing.wrist = wrist;

  // arm filler (flattened tapered capsules covered by coverts)
  const arm = (parent, len, r0, r1) => {
    const g = new THREE.CylinderGeometry(r1, r0, len, 14, 1);
    g.rotateZ(-Math.PI / 2);
    g.translate(len / 2, 0, 0);
    const m = new THREE.Mesh(g, mat.plumage);
    m.scale.set(1, 0.5, 1);
    m.position.z = -0.01;
    parent.add(m);
    return m;
  };
  arm(joint, WING.L1, 0.085, 0.075);
  arm(elbow, WING.L2, 0.075, 0.06);
  arm(wrist, WING.L3, 0.06, 0.035);
  for (const [p, r] of [
    [joint, 0.085],
    [elbow, 0.075],
    [wrist, 0.06],
  ]) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), mat.plumage);
    s.scale.set(1, 0.5, 1);
    s.position.z = -0.01;
    p.add(s);
  }

  const placeFeather = (parent, geo, x, z, y, theta, len, wid, droopRoll = 0) => {
    const m = new THREE.Mesh(geo, mat.feather);
    m.position.set(x, y, z);
    m.rotation.order = "YXZ";
    m.rotation.y = theta - Math.PI / 2;
    m.rotation.x = droopRoll;
    m.scale.set(len, 1, wid);
    parent.add(m);
    return m;
  };

  // primaries on the hand
  const prLen = [0.47, 0.51, 0.55, 0.58, 0.6, 0.61, 0.6, 0.57, 0.52, 0.44];
  for (let i = 0; i < 10; i++) {
    const u = i / 9;
    const m = placeFeather(
      wrist,
      geos.primary,
      lerp(0.015, WING.L3 * 0.95, u),
      0.012,
      0.0015 * (10 - i),
      lerp(24, 80, Math.pow(u, 0.85)) * DEG,
      prLen[i],
      lerp(0.074, 0.058, u),
    );
    m.userData.base = { theta: m.rotation.y, roll: m.rotation.x, i };
    wing.primaries.push(m);
  }
  // secondaries on the forearm
  const nSec = 11;
  for (let i = 0; i < nSec; i++) {
    const u = i / (nSec - 1);
    const m = placeFeather(
      elbow,
      geos.secondary,
      lerp(WING.L2 * 0.98, 0.01, u),
      0.01,
      0.0012 * (nSec - i),
      lerp(6, -6, u) * DEG,
      lerp(0.38, 0.4, Math.sin(u * Math.PI)) * (0.96 + 0.04 * Math.sin(i * 2.1)),
      0.075,
    );
    m.userData.base = { theta: m.rotation.y, roll: m.rotation.x, i };
    wing.secondaries.push(m);
  }
  // tertials on the upper arm
  const nTer = 5;
  for (let i = 0; i < nTer; i++) {
    const u = i / (nTer - 1);
    const m = placeFeather(
      joint,
      geos.secondary,
      lerp(WING.L1 * 0.97, 0.02, u),
      0.01,
      0.0012 * (nTer - i),
      lerp(-4, -22, u) * DEG,
      lerp(0.31, 0.24, u),
      0.07,
    );
    m.userData.base = { theta: m.rotation.y, roll: m.rotation.x, i };
    wing.tertials.push(m);
  }

  // coverts: static white rows merged per bone
  const rows = (parent, specs) => {
    const list = [];
    const M = new THREE.Matrix4();
    const Q = new THREE.Quaternion();
    const E = new THREE.Euler();
    for (const sp of specs) {
      for (let i = 0; i < sp.n; i++) {
        const u = sp.n === 1 ? 0 : i / (sp.n - 1);
        const th = lerp(sp.th0, sp.th1, u) * DEG;
        E.set(sp.roll || 0, th - Math.PI / 2, 0, "YXZ");
        Q.setFromEuler(E);
        M.compose(
          V3(lerp(sp.x0, sp.x1, u), sp.y + 0.0006 * i, sp.z),
          Q,
          V3(lerp(sp.l0, sp.l1, u), 1, sp.w),
        );
        list.push(geos.covert.clone().applyMatrix4(M));
      }
    }
    const mesh = new THREE.Mesh(mergeGeometries(list), mat.feather);
    parent.add(mesh);
    return mesh;
  };
  rows(wrist, [
    { n: 10, x0: 0.02, x1: WING.L3 * 0.9, th0: 28, th1: 82, l0: 0.25, l1: 0.19, w: 0.066, y: 0.006, z: -0.02 },
    { n: 8, x0: 0.03, x1: WING.L3 * 0.85, th0: 40, th1: 86, l0: 0.16, l1: 0.12, w: 0.056, y: 0.014, z: -0.038 },
    { n: 6, x0: 0.04, x1: WING.L3 * 0.75, th0: 55, th1: 88, l0: 0.1, l1: 0.08, w: 0.05, y: 0.022, z: -0.055 },
  ]);
  rows(elbow, [
    { n: 11, x0: WING.L2 * 0.98, x1: 0.01, th0: 8, th1: -4, l0: 0.24, l1: 0.23, w: 0.074, y: 0.006, z: -0.02 },
    { n: 11, x0: WING.L2 * 0.96, x1: 0.02, th0: 14, th1: 0, l0: 0.17, l1: 0.16, w: 0.064, y: 0.014, z: -0.038 },
    { n: 9, x0: WING.L2 * 0.94, x1: 0.03, th0: 22, th1: 4, l0: 0.11, l1: 0.1, w: 0.054, y: 0.022, z: -0.055 },
  ]);
  rows(joint, [
    { n: 6, x0: WING.L1 * 0.96, x1: 0.02, th0: -4, th1: -24, l0: 0.22, l1: 0.18, w: 0.074, y: 0.006, z: -0.02 },
    { n: 6, x0: WING.L1 * 0.94, x1: 0.03, th0: 4, th1: -14, l0: 0.14, l1: 0.12, w: 0.064, y: 0.014, z: -0.038 },
    { n: 5, x0: WING.L1 * 0.9, x1: 0.05, th0: 14, th1: -4, l0: 0.09, l1: 0.09, w: 0.054, y: 0.022, z: -0.055 },
  ]);
  return wing;
}

// ------------------------------------------------------------------ legs ----
function buildLeg(mat) {
  const g = new THREE.Group();
  const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.05, 1, 14), mat.plumage);
  const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.022, 1, 10), mat.leg);
  const knee = new THREE.Mesh(new THREE.SphereGeometry(0.034, 14, 10), mat.plumage);
  const heel = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 10), mat.leg);
  g.add(thigh, shin, knee, heel);

  // foot: three webbed toes + short hind toe
  const foot = new THREE.Group();
  const toes = [
    { a: 0.5, l: 0.15 },
    { a: 0.0, l: 0.19 },
    { a: -0.5, l: 0.15 },
  ];
  const shape = new THREE.Shape();
  shape.moveTo(-0.02, 0);
  const tipsPts = toes.map((t) => [Math.cos(t.a) * t.l, Math.sin(t.a) * t.l]);
  shape.lineTo(tipsPts[2][0], tipsPts[2][1]);
  for (let i = 2; i > 0; i--) {
    const a = tipsPts[i];
    const b = tipsPts[i - 1];
    const mx = (a[0] + b[0]) / 2 - 0.035;
    const my = (a[1] + b[1]) / 2;
    shape.quadraticCurveTo(mx, my, b[0], b[1]);
  }
  shape.lineTo(-0.02, 0);
  const web = new THREE.Mesh(new THREE.ShapeGeometry(shape, 8), mat.foot);
  web.rotation.x = -Math.PI / 2; // shape x -> forward, shape y -> -z
  web.position.y = 0.004;
  foot.add(web);
  for (const t of toes) {
    const curve = new THREE.CatmullRomCurve3([V3(0, 0.012, 0), V3(Math.cos(t.a) * t.l * 0.5, 0.012, -Math.sin(t.a) * t.l * 0.5), V3(Math.cos(t.a) * t.l, 0.008, -Math.sin(t.a) * t.l)]);
    const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 8, 0.0105, 8), mat.leg);
    foot.add(m);
    const nail = new THREE.Mesh(new THREE.SphereGeometry(0.0105, 8, 6), mat.leg);
    nail.position.set(Math.cos(t.a) * t.l, 0.008, -Math.sin(t.a) * t.l);
    foot.add(nail);
  }
  const hind = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.011, 0.06, 8), mat.leg);
  hind.rotation.z = Math.PI / 2;
  hind.position.set(-0.04, 0.01, 0);
  foot.add(hind);
  g.add(foot);
  return { group: g, thigh, shin, knee, heel, foot };
}

const _up = V3(0, 1, 0);
function placeSegment(mesh, a, b) {
  const d = V3().subVectors(b, a);
  const len = d.length();
  mesh.position.copy(a).addScaledVector(d, 0.5);
  mesh.quaternion.setFromUnitVectors(_up, d.divideScalar(Math.max(len, 1e-5)));
  mesh.scale.set(1, len, 1);
}

// --------------------------------------------------------------- pelican ----
export function createPelican() {
  const mat = makeMaterials();
  const root = new THREE.Group();
  const body = new THREE.Group();
  root.add(body);
  body.add(buildBody(mat));

  // neck
  const neck = makeTube(28, 18, mat.plumage);
  body.add(neck);
  const neckCurve = new THREE.CatmullRomCurve3([V3(), V3(), V3(), V3(), V3()], false, "centripetal");
  const neckPts = Array.from({ length: 29 }, () => V3());
  const neckRad = new Array(29);

  // head
  const head = new THREE.Group();
  body.add(head);
  const skull = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), mat.plumage);
  skull.scale.set(0.135, 0.078, 0.073);
  skull.position.set(0.03, 0.0, 0);
  head.add(skull);
  // forehead / crown blends into the bill
  const brow = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), mat.plumage);
  brow.scale.set(0.085, 0.045, 0.06);
  brow.position.set(0.115, 0.026, 0);
  head.add(brow);
  const upper = buildUpperBill(mat);
  head.add(upper);
  const pouch = buildPouch(mat);
  head.add(pouch);

  // facial skin around the eyes
  const eyes = [];
  for (const side of [1, -1]) {
    const patch = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), mat.skin);
    patch.scale.set(0.058, 0.04, 0.018);
    patch.position.set(0.058, 0.014, 0.055 * side);
    patch.rotation.y = side * -0.35;
    head.add(patch);
    const lore = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), mat.skin);
    lore.scale.set(0.06, 0.024, 0.016);
    lore.position.set(0.12, -0.004, 0.047 * side);
    lore.rotation.y = side * -0.18;
    head.add(lore);
    const eye = buildEye(mat, side);
    eye.position.set(0.052, 0.024, 0.0595 * side);
    head.add(eye);
    eyes.push(eye);
  }

  // crest tuft
  const tuftGeo = featherGeometry({
    segs: 5,
    across: 2,
    lead: 0.5,
    trail: 0.5,
    droop: 0.2,
    camber: 0.05,
    tip: 0.6,
    base: 0.5,
    colorFn: () => [0.98, 0.96, 0.9],
  });
  const tuft = [];
  for (let i = 0; i < 5; i++) {
    const m = new THREE.Mesh(tuftGeo, mat.feather);
    m.position.set(-0.085 - 0.004 * i, 0.04 - 0.004 * Math.abs(i - 2), (i - 2) * 0.012);
    m.rotation.order = "YXZ";
    const yaw = Math.PI + (i - 2) * 0.14;
    m.rotation.y = yaw;
    m.rotation.z = 0.25 - 0.04 * Math.abs(i - 2);
    m.scale.set(0.085 - 0.01 * Math.abs(i - 2), 1, 0.016);
    m.userData.base = { yaw, tilt: m.rotation.z, i };
    head.add(m);
    tuft.push(m);
  }

  // wings
  const geos = {
    primary: flightFeatherGeo("primary"),
    secondary: flightFeatherGeo("secondary"),
    covert: flightFeatherGeo("covert"),
  };
  const wingR = buildWing(1, mat, geos);
  const wingL = buildWing(-1, mat, geos);
  wingR.frame.position.set(0.08, 0.15, 0.13);
  wingL.frame.position.set(0.08, 0.15, -0.13);
  body.add(wingR.frame, wingL.frame);
  const wings = [wingR, wingL];

  // tail feathers
  const tailGeo = featherGeometry({
    segs: 8,
    across: 3,
    lead: 0.5,
    trail: 0.5,
    droop: 0.12,
    camber: 0.06,
    tip: 0.35,
    base: 0.5,
    colorFn: (t) => {
      const k = smoothstep(0.3, 1, t);
      return [lerp(0.97, 0.45, k), lerp(0.97, 0.46, k), lerp(0.95, 0.5, k)];
    },
  });
  const tail = [];
  const tailPivot = new THREE.Group();
  tailPivot.position.set(-0.44, 0.03, 0);
  body.add(tailPivot);
  for (let i = 0; i < 11; i++) {
    const u = i / 10 - 0.5;
    const m = new THREE.Mesh(tailGeo, mat.feather);
    m.rotation.order = "YXZ";
    m.rotation.y = Math.PI + (-u) * 0.98;
    m.rotation.z = -0.1;
    m.position.set(0, 0.0015 * Math.abs(i - 5), u * 0.05);
    m.scale.set(0.3 - 0.018 * Math.abs(i - 5), 1, 0.07);
    m.userData.base = { yaw: m.rotation.y, tilt: m.rotation.z, i };
    tailPivot.add(m);
    tail.push(m);
  }

  // legs
  const legR = buildLeg(mat);
  const legL = buildLeg(mat);
  root.add(legR.group, legL.group);
  const footTarget = [V3(0.12, 0.034, 0.17), V3(-0.14, 0.034, -0.17)];
  const toeOut = [-0.18, 0.18];
  const hipLocal = [V3(0.0, -0.1, 0.085), V3(0.0, -0.1, -0.085)];

  shadowAll(root);

  // --------------------------------------------------------- animation state
  const st = {
    bounceY: 0,
    bounceV: 0,
    sag: 0,
    sagV: 0,
    wob: 0,
    stretch: 0.6,
    headYaw: 0,
    headPitch: 0,
    gape: 0,
    rollSmooth: 0,
    wing: [{}, {}],
  };

  const tmpA = V3();
  const tmpHip = V3();
  const headBase = V3();

  function solveLeg(leg, hipWorldLocal, foot, toe) {
    const a = 0.26;
    const b = 0.17;
    const H = hipWorldLocal;
    const F = tmpA.copy(foot).add(V3(0, 0.02, 0));
    const d = V3().subVectors(F, H);
    let dist = d.length();
    const maxD = (a + b) * 0.995;
    if (dist > maxD) {
      d.multiplyScalar(maxD / dist);
      dist = maxD;
      F.copy(H).add(d);
    }
    const dir = d.clone().divideScalar(dist);
    const cosA = clamp((a * a + dist * dist - b * b) / (2 * a * dist), -1, 1);
    const sinA = Math.sqrt(1 - cosA * cosA);
    const pole = V3(-1, 0.35, 0);
    pole.addScaledVector(dir, -pole.dot(dir)).normalize();
    const J = H.clone().addScaledVector(dir, a * cosA).addScaledVector(pole, a * sinA);
    const Hin = H.clone().addScaledVector(J.clone().sub(H).normalize(), -0.07); // start the thigh deeper inside the body
    placeSegment(leg.thigh, Hin, J);
    placeSegment(leg.shin, J, F);
    leg.knee.position.copy(J);
    leg.heel.position.copy(F);
    leg.foot.position.set(foot.x, foot.y - 0.026, foot.z);
    leg.foot.rotation.y = toe;
  }

  function update(t, dt, s) {
    // s: { roll, accelY, speed, crouch, camLocal } describe how the board is moving
    dt = Math.min(dt, 0.05);
    // vertical spring (body bounce driven by board vertical acceleration)
    const k = 90;
    const c = 11;
    const target = -0.025 * (s.accelY || 0);
    st.bounceV += (-k * (st.bounceY - target) - c * st.bounceV) * dt;
    st.bounceY += st.bounceV * dt;
    st.bounceY = clamp(st.bounceY, -0.08, 0.08);
    // pouch sloshes with vertical acceleration and turning
    const kp = 70;
    const cp = 4.5;
    const sagTarget = clamp(0.06 * (s.accelY || 0), -0.5, 0.8);
    st.sagV += (-kp * (st.sag - sagTarget) - cp * st.sagV) * dt;
    st.sag += st.sagV * dt;
    st.wob = lerp(st.wob, clamp(st.sagV * 0.3, -1, 1), 0.2);

    const roll = s.roll || 0;
    st.rollSmooth = lerp(st.rollSmooth, roll, 1 - Math.exp(-dt * 6));

    // crouch pose
    const crouch = clamp(s.crouch ?? 0.5, 0, 1);
    const bodyY = 0.5 - 0.075 * crouch + st.bounceY;
    body.position.set(-0.02, bodyY, 0);
    // pitch forward in the crouch, counter-roll slightly against the board
    body.rotation.set(0.7 * st.rollSmooth, 0.05 * Math.sin(t * 0.9), -0.1 - 0.12 * crouch + 0.04 * Math.sin(t * 1.3), "XYZ");

    // ---- neck & head
    const wave = Math.sin(t * 0.8);
    st.stretch = lerp(st.stretch, clamp(0.55 + 0.18 * wave + 0.25 * (s.speed || 0), 0, 1), 1 - Math.exp(-dt * 3));
    const sk = st.stretch;
    const swayZ = 0.03 * Math.sin(t * 1.1);
    // control points (body space): retracted S -> extended
    const P = [
      V3(lerp(0.24, 0.28, sk), 0.17, 0),
      V3(lerp(0.15, 0.32, sk), lerp(0.3, 0.31, sk), swayZ * 0.3),
      V3(lerp(0.13, 0.29, sk), lerp(0.43, 0.46, sk), swayZ * 0.7),
      V3(lerp(0.25, 0.38, sk), lerp(0.53, 0.58, sk), swayZ),
      V3(lerp(0.35, 0.47, sk), lerp(0.5, 0.62, sk) + 0.008 * Math.sin(t * 2.3), swayZ * 1.1),
    ];
    // head turns toward the camera now and then
    const glance = smoothstep(0.35, 0.75, 0.5 + 0.5 * Math.sin(t * 0.37 + 1.2));
    let yawTarget = 0;
    if (s.camLocal) {
      const ca = Math.atan2(s.camLocal.z, s.camLocal.x);
      yawTarget = -clamp(ca, -0.9, 0.9) * glance * 0.9;
    }
    st.headYaw = lerp(st.headYaw, yawTarget + 0.07 * Math.sin(t * 0.9), 1 - Math.exp(-dt * 2.5));
    const pitchTarget = -0.2 - 0.18 * (1 - sk) + 0.08 * Math.sin(t * 1.7) + 0.005 * (s.accelY || 0);
    st.headPitch = lerp(st.headPitch, pitchTarget, 1 - Math.exp(-dt * 4));

    head.position.copy(P[4]);
    head.rotation.order = "YZX";
    head.rotation.set(-0.08 * st.rollSmooth, st.headYaw, st.headPitch);
    // neck ends inside the skull
    headBase.set(-0.06, -0.014, 0).applyEuler(head.rotation).add(head.position);
    neckCurve.points[0].copy(P[0]);
    neckCurve.points[1].copy(P[1]);
    neckCurve.points[2].copy(P[2]);
    neckCurve.points[3].copy(P[3]);
    neckCurve.points[4].copy(headBase);
    for (let i = 0; i <= 28; i++) {
      neckCurve.getPoint(i / 28, neckPts[i]);
      const u = i / 28;
      neckRad[i] = lerp(0.108, 0.064, smoothstep(0.0, 0.95, u)) + 0.035 * Math.exp(-u * 8) + 0.008 * Math.sin(u * Math.PI * 2);
    }
    neck.userData.update(neckPts, neckRad);

    // ---- bill gape (every so often the pelican whoops) & blink
    const cyc = (t + 2.0) % 11.0;
    const whoop = smoothstep(4.2, 4.6, cyc) * (1 - smoothstep(5.2, 5.9, cyc));
    const g2 = (t + 7.1) % 17.0;
    const whoop2 = smoothstep(9.0, 9.35, g2) * (1 - smoothstep(9.8, 10.4, g2));
    st.gape = lerp(st.gape, Math.max(whoop, whoop2 * 0.7) * 0.5, 1 - Math.exp(-dt * 14));
    pouch.userData.update(st.gape, st.sag + st.gape * 0.8, st.wob);
    upper.rotation.z = st.gape * -0.04;

    const bt = (t + 0.7) % 3.9;
    const blink = bt < 0.16 ? Math.sin((bt / 0.16) * Math.PI) : 0;
    const squint = 0.22 + 0.1 * Math.sin(t * 0.5);
    for (const e of eyes) e.userData.setLid(1 - blink, squint * (1 - blink));

    // tuft + tail flutter
    for (const m of tuft) {
      const b = m.userData.base;
      m.rotation.z = b.tilt + 0.18 * Math.sin(t * 7.0 + b.i * 0.8) + 0.12 * (s.speed || 0);
      m.rotation.y = b.yaw + 0.08 * Math.sin(t * 5.0 + b.i * 1.3);
    }
    for (const m of tail) {
      const b = m.userData.base;
      m.rotation.z = b.tilt + 0.06 * Math.sin(t * 4.2 + b.i * 0.6) + 0.1 * st.rollSmooth;
      m.rotation.y = b.yaw + 0.04 * Math.sin(t * 3.1 + b.i);
    }

    // ---- wings. The wave is always on the pelican's right: that wing is held up and folded clear of the
    // face, the left wing is thrown out over the open water for balance.
    const gust = 0.55 + 0.45 * Math.sin(t * 0.63 + 0.4);
    const spd = s.speed || 0;
    const rl = st.rollSmooth;
    for (let w = 0; w < 2; w++) {
      const wing = wings[w];
      const uphill = wing.side > 0;
      const sw = st.wing[w];
      const ph = w * 1.7;
      const target = uphill
        ? {
            dih: 0.72 + 0.08 * Math.sin(t * 0.9 + ph) + 0.1 * rl,
            sweep: 0.85 + 0.08 * Math.sin(t * 0.7) + 0.1 * spd,
            pitch: 0.2 + 0.08 * Math.sin(t * 0.55),
            elbow: -1.05 - 0.08 * Math.sin(t * 0.8),
            wrist: 1.3 + 0.08 * Math.sin(t * 0.9 + 1.0),
            wristUp: 0.05,
          }
        : {
            dih: -0.02 + 0.1 * Math.sin(t * 0.9 + ph) + 0.06 * gust - 0.22 * rl,
            sweep: 0.26 + 0.12 * Math.sin(t * 0.7 + 2.0) + 0.1 * spd,
            pitch: 0.1 * Math.sin(t * 0.55 + 1.0) - 0.12 * rl,
            elbow: -0.34 - 0.1 * Math.sin(t * 0.8 + 1.0),
            wrist: 0.55 + 0.08 * Math.sin(t * 0.9 + 2.0),
            wristUp: 0.14 + 0.1 * Math.sin(t * 1.3) + 0.12 * gust,
          };
      const f = 1 - Math.exp(-dt * 5);
      for (const k in target) sw[k] = k in sw ? lerp(sw[k], target[k], f) : target[k];
      wing.joint.rotation.order = "XYZ";
      wing.joint.rotation.set(sw.pitch, -sw.sweep, sw.dih);
      wing.elbow.rotation.set(0, sw.elbow, 0.06 * Math.sin(t * 1.1 + w));
      wing.wrist.rotation.set(0, sw.wrist, sw.wristUp);
      for (const m of wing.primaries) {
        const b = m.userData.base;
        const fp = b.i * 0.55 + w * 1.9;
        m.rotation.y = b.theta + (0.03 + 0.012 * b.i) * Math.sin(t * 3.1 + fp) * gust;
        m.rotation.x = b.roll + (0.04 + 0.01 * b.i) * Math.sin(t * 2.3 + fp);
      }
      for (const m of wing.secondaries) {
        const b = m.userData.base;
        const fp = b.i * 0.7 + w * 1.3;
        m.rotation.y = b.theta + 0.035 * Math.sin(t * 2.7 + fp) * gust;
        m.rotation.x = b.roll + 0.03 * Math.sin(t * 2.1 + fp);
      }
      for (const m of wing.tertials) {
        const b = m.userData.base;
        m.rotation.y = b.theta + 0.03 * Math.sin(t * 2.2 + b.i + w);
      }
    }

    // ---- legs (IK to feet planted on the board)
    root.updateMatrixWorld(true);
    for (let i = 0; i < 2; i++) {
      tmpHip.copy(hipLocal[i]);
      body.localToWorld(tmpHip);
      root.worldToLocal(tmpHip);
      solveLeg(i === 0 ? legR : legL, tmpHip.clone(), footTarget[i], toeOut[i]);
    }
  }

  return { root, body, head, update, state: st };
}
