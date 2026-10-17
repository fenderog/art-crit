// A brown pelican built from lofts, spheres and individual feathers.
// Local frame: +z forward (bill), +y up, +x is the bird's left.

import * as THREE from 'three';
import { buildLoft, createLoftGeometry, updateLoft, featherGeometry, paintGeometry, mulberry32, smoothstep, clamp } from './geom.js';
import { DECK_Y } from './surfboard.js';

const V3 = THREE.Vector3;
const rnd = mulberry32(1234);

const C = (hex) => new THREE.Color(hex);
const COL = {
  back: C('#c9c2b6'),
  belly: C('#5a4f46'),
  chest: C('#6b5d50'),
  neckWhite: C('#f4f0e6'),
  chestnut: C('#5e3322'),
  crown: C('#f2d77e'),
  head: C('#f7f3ea'),
  billBase: C('#b8a397'),
  billMid: C('#c7a084'),
  billTip: C('#d75f2e'),
  pouch: C('#433832'),
  primary: C('#2a2420'),
  secondary: C('#4f463f'),
  tertial: C('#7a6f64'),
  covertG: C('#9a948b'),
  covertL: C('#b9b3a8'),
  leg: C('#2e2a28'),
  tail: C('#463e37'),
  eye: C('#f3edd2'),
  ring: C('#d4918a'),
};

const ARM = 0.27;
const FORE = 0.3;
const HAND = 0.17;
const TORSO_PITCH = -0.42;
const NECK_BASE = new V3(0, 0.1, 0.33);   // torso local
const HIP = new V3(0.085, -0.15, -0.02);   // torso local (left; mirrored for right)
const HEAD_REST = new V3(0, 0.6, 0.36);    // body local
const HEAD_ATTACH = new V3(0, -0.045, -0.035); // head local
const TIBIA = 0.2;
const TARSUS = 0.16;

function featherTexture() {
  const W = 256, H = 512;
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  const g = c.getContext('2d');
  g.fillStyle = '#9a9a9a';
  g.fillRect(0, 0, W, H);
  const cols = 12, rows = 28;
  const cw = W / cols, rh = H / rows;
  // draw from the tail end (bottom) upwards so head-side feathers overlap
  for (let r = rows + 1; r >= -1; r--) {
    for (let k = -1; k <= cols; k++) {
      const x = k * cw + (r % 2) * cw * 0.5 + (rnd() - 0.5) * 3;
      const y = r * rh + (rnd() - 0.5) * 2;
      const l = 190 + rnd() * 50;
      g.fillStyle = `rgb(${l},${l},${l})`;
      g.strokeStyle = 'rgba(60,60,60,0.3)';
      g.lineWidth = 1.2;
      for (const ox of [0, W, -W]) {
        g.beginPath();
        g.ellipse(x + ox, y, cw * 0.62, rh * 1.05, 0, 0, Math.PI * 2);
        g.fill();
        g.stroke();
        g.strokeStyle = 'rgba(255,255,255,0.25)';
        g.beginPath();
        g.moveTo(x + ox, y - rh * 0.8);
        g.lineTo(x + ox, y + rh * 0.7);
        g.stroke();
        g.strokeStyle = 'rgba(60,60,60,0.3)';
      }
    }
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.anisotropy = 4;
  return tex;
}

function footGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0.012, -0.02);
  s.lineTo(0.03, 0.02);
  s.quadraticCurveTo(0.075, 0.08, 0.088, 0.118);
  s.quadraticCurveTo(0.062, 0.102, 0.046, 0.112);
  s.quadraticCurveTo(0.038, 0.14, 0.03, 0.165);
  s.quadraticCurveTo(0.014, 0.128, -0.002, 0.138);
  s.quadraticCurveTo(-0.012, 0.152, -0.02, 0.162);
  s.quadraticCurveTo(-0.03, 0.122, -0.046, 0.116);
  s.quadraticCurveTo(-0.06, 0.104, -0.07, 0.1);
  s.quadraticCurveTo(-0.04, 0.04, -0.012, -0.02);
  s.lineTo(0.012, -0.02);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.01, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 2, curveSegments: 6 });
  geo.rotateX(Math.PI / 2);
  geo.translate(0, 0.014, 0);
  return geo;
}

function variants(base, n, spread) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const m = new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: 0.85 });
    m.color.copy(base).offsetHSL((rnd() - 0.5) * 0.01, (rnd() - 0.5) * 0.05, (rnd() - 0.5) * spread);
    out.push(m);
  }
  return out;
}

const _v = new V3();
const _v2 = new V3();
const _q = new THREE.Quaternion();
const _q2 = new THREE.Quaternion();
const _m = new THREE.Matrix4();
const _e = new THREE.Euler();
const ZERO = new V3();
const UP = new V3(0, 1, 0);

export class Pelican {
  constructor() {
    this.body = new THREE.Group();
    this.torso = new THREE.Group();
    this.torso.rotation.x = TORSO_PITCH;
    this.body.add(this.torso);
    this.legs = new THREE.Group();

    this.featherTex = featherTexture();
    this.mats = {
      primary: variants(COL.primary, 3, 0.03),
      secondary: variants(COL.secondary, 3, 0.04),
      tertial: variants(COL.tertial, 2, 0.04),
      covertG: variants(COL.covertG, 3, 0.05),
      covertL: variants(COL.covertL, 3, 0.05),
      tail: variants(COL.tail, 2, 0.03),
    };
    this.geos = {
      feather: featherGeometry({}),
      primary: featherGeometry({ emarg: 0.35, shaft: 1.5, fringe: 1.0 }),
      covert: featherGeometry({ segs: 5, shaft: 1.15, fringe: 1.2, base: 0.85 }),
    };

    this.buildTorso();
    this.buildTail();
    this.wings = [this.buildWing(1), this.buildWing(-1)];
    this.buildHead();
    this.buildNeck();
    this.buildLegs();

    this.body.traverse((o) => {
      if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; }
    });
    this.legs.traverse((o) => {
      if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; }
    });

    this.headQ = new THREE.Quaternion();
    this.nextBlink = 2;
    this.jig = 0;
    this.jigV = 0;
    this.prevWorld = new V3();
    this.prevVel = new V3();
    this.hasPrev = false;
  }

  buildTorso() {
    const N = 28;
    const path = [];
    for (let i = 0; i < N; i++) {
      const t = i / (N - 1);
      path.push(new V3(0, 0.025 * Math.sin(Math.PI * t), -0.48 + 0.9 * t));
    }
    const section = (t, o) => {
      const k = Math.sin(Math.PI * Math.pow(t, 1.3));
      o.rx = 0.2 * Math.pow(k, 0.62);
      o.ry = 0.19 * Math.pow(k, 0.6);
      o.oy = -0.025 * Math.sin(Math.PI * t);
    };
    const colorFn = (c, t, cs, sn) => {
      c.copy(COL.belly).lerp(COL.back, smoothstep(-0.3, 0.45, sn));
      if (t > 0.75) c.lerp(COL.chest, smoothstep(0.75, 0.95, t) * smoothstep(0.4, -0.2, sn));
    };
    const geo = buildLoft(path, section, { radial: 22, colorFn });
    this.featherTex.repeat.set(4, 3);
    const mat = new THREE.MeshStandardMaterial({ map: this.featherTex, vertexColors: true, roughness: 0.9 });
    this.bodyMat = mat;
    this.torso.add(new THREE.Mesh(geo, mat));
  }

  feather(parent, geo, mat, x, y, z, len, width, yaw, pitch = 0, roll = 0) {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.scale.set(width, len, len);
    m.rotation.order = 'YXZ';
    m.rotation.set(pitch, yaw, roll);
    parent.add(m);
    return m;
  }

  pick(list) {
    return list[Math.floor(rnd() * list.length)];
  }

  buildTail() {
    const tail = new THREE.Group();
    tail.position.set(0, 0.03, -0.45);
    tail.rotation.x = 0.28;
    this.torso.add(tail);
    this.tail = tail;
    this.tailFeathers = [];
    for (let i = 0; i < 7; i++) {
      const f = i / 6 - 0.5;
      const yaw = f * 1.1;
      const m = this.feather(tail, this.geos.feather, this.pick(this.mats.tail), f * 0.05, Math.abs(f) * -0.01 + i * 0.001, 0, 0.17 - Math.abs(f) * 0.03, 0.06, yaw);
      this.tailFeathers.push({ m, yaw });
    }
  }

  boneMesh(len, ry0, ry1, rz0, rz1) {
    const N = 9;
    const path = [];
    for (let i = 0; i < N; i++) path.push(new V3(-0.015 + (len + 0.015) * (i / (N - 1)), 0, 0));
    const section = (t, o) => {
      const end = Math.sqrt(1 - smoothstep(0.82, 1.0, t) * 0.95);
      o.rx = (rz0 + (rz1 - rz0) * t) * end;
      o.ry = (ry0 + (ry1 - ry0) * t) * end;
      o.ox = -o.rx * 0.45;
    };
    const colorFn = (c, t, cs, sn) => c.copy(COL.secondary).lerp(COL.covertL, smoothstep(-0.4, 0.5, sn));
    const geo = buildLoft(path, section, { radial: 14, colorFn });
    return new THREE.Mesh(geo, this.bodyMat);
  }

  buildWing(side) {
    const shoulder = new THREE.Group();
    shoulder.position.set(0.14 * side, 0.12, 0.17);
    shoulder.scale.x = side;
    this.torso.add(shoulder);
    const arm = new THREE.Group();
    const fore = new THREE.Group();
    const hand = new THREE.Group();
    arm.rotation.order = fore.rotation.order = hand.rotation.order = 'YZX';
    fore.position.x = ARM;
    hand.position.x = FORE;
    shoulder.add(arm);
    arm.add(fore);
    fore.add(hand);

    arm.add(this.boneMesh(ARM + 0.02, 0.05, 0.04, 0.1, 0.085));
    fore.add(this.boneMesh(FORE + 0.02, 0.04, 0.03, 0.085, 0.07));
    hand.add(this.boneMesh(HAND + 0.03, 0.03, 0.016, 0.065, 0.03));

    const G = this.geos, M = this.mats;
    // tertials (innermost, long and pale)
    for (let i = 0; i < 3; i++) {
      this.feather(arm, G.feather, this.pick(M.tertial), -0.03 + i * 0.045, -0.006 - i * 0.001, -0.02, 0.27 - i * 0.01, 0.08, 0.32 - i * 0.08, -0.04);
    }
    // secondaries
    for (let i = 0; i < 6; i++) {
      const f = i / 5;
      this.feather(arm, G.feather, this.pick(M.secondary), 0.04 + f * (ARM - 0.06), -0.012 - i * 0.0008, -0.022, 0.32 + f * 0.01, 0.085, 0.12 - 0.16 * f, -0.05);
    }
    for (let i = 0; i < 9; i++) {
      const f = i / 8;
      this.feather(fore, G.feather, this.pick(M.secondary), 0.01 + f * (FORE - 0.02), -0.012 - i * 0.0008, -0.022, 0.335 - f * 0.025, 0.085, -0.06 - 0.12 * f, -0.05);
    }
    // greater coverts
    for (let i = 0; i < 7; i++) {
      const f = i / 6;
      this.feather(arm, G.covert, this.pick(M.covertG), 0.0 + f * (ARM - 0.02), 0.006 + i * 0.0006, -0.01, 0.16, 0.075, 0.12 - 0.16 * f, -0.08);
    }
    for (let i = 0; i < 9; i++) {
      const f = i / 8;
      this.feather(fore, G.covert, this.pick(M.covertG), 0.01 + f * (FORE - 0.02), 0.006 + i * 0.0006, -0.01, 0.155 - f * 0.02, 0.075, -0.06 - 0.12 * f, -0.08);
    }
    // lesser coverts
    for (let i = 0; i < 8; i++) {
      const f = i / 7;
      this.feather(arm, G.covert, this.pick(M.covertL), 0.0 + f * (ARM - 0.01), 0.018 + i * 0.0005, 0.018, 0.095, 0.06, 0.1 - 0.12 * f, -0.12);
    }
    for (let i = 0; i < 9; i++) {
      const f = i / 8;
      this.feather(fore, G.covert, this.pick(M.covertL), 0.01 + f * (FORE - 0.02), 0.016 + i * 0.0005, 0.016, 0.09, 0.055, -0.04 - 0.1 * f, -0.12);
    }
    // primary coverts
    for (let i = 0; i < 5; i++) {
      this.feather(hand, G.covert, this.pick(M.covertG), 0.01 + i * 0.035, 0.008 + i * 0.0006, -0.005, 0.13, 0.065, -0.3 - 0.18 * i, -0.08);
    }
    // primaries: fanned "fingers"
    const LEN = [0.33, 0.35, 0.37, 0.39, 0.41, 0.43, 0.45, 0.46, 0.45, 0.41];
    const primaries = [];
    for (let i = 0; i < 10; i++) {
      const f = i / 9;
      const yaw = -0.2 - 1.2 * Math.pow(f, 1.1);
      const m = this.feather(hand, i >= 5 ? G.primary : G.feather, this.pick(M.primary),
        HAND * Math.min(1, i / 7), -0.008 + 0.0012 * i, -0.01, LEN[i], 0.075, yaw, -0.03);
      primaries.push({ m, yaw, i });
    }
    return { side, shoulder, arm, fore, hand, primaries };
  }

  buildHead() {
    const head = new THREE.Group();
    head.position.copy(HEAD_REST);
    this.body.add(head);
    this.head = head;

    const skin = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75 });
    const skullGeo = paintGeometry(new THREE.SphereGeometry(1, 28, 20), (c, n) => {
      c.copy(COL.head).lerp(COL.crown, smoothstep(0.25, 0.75, n.y) * smoothstep(0.6, -0.2, n.z));
    });
    const skull = new THREE.Mesh(skullGeo, skin);
    skull.scale.set(0.07, 0.078, 0.1);
    head.add(skull);
    const brow = new THREE.Mesh(paintGeometry(new THREE.SphereGeometry(1, 20, 14), (c) => c.copy(COL.head)), skin);
    brow.scale.set(0.05, 0.048, 0.09);
    brow.position.set(0, -0.008, 0.055);
    head.add(brow);
    const throat = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 12), new THREE.MeshStandardMaterial({ color: COL.pouch, roughness: 0.7 }));
    throat.scale.set(0.046, 0.056, 0.075);
    throat.position.set(0, -0.05, 0.005);
    head.add(throat);

    // upper mandible with hooked tip
    const NB = 28;
    const billPath = [];
    for (let i = 0; i < NB; i++) {
      const t = i / (NB - 1);
      if (t <= 0.92) {
        billPath.push(new V3(0, -0.004 - 0.03 * t, 0.045 + 0.54 * t));
      } else {
        const k = (t - 0.92) / 0.08;
        billPath.push(new V3(0, -0.004 - 0.03 * 0.92 - 0.034 * (1 - Math.cos(k * Math.PI * 0.5)), 0.045 + 0.54 * 0.92 + 0.026 * Math.sin(k * Math.PI * 0.5)));
      }
    }
    const billSec = (t, o) => {
      const end = Math.sqrt(Math.max(0, 1 - smoothstep(0.88, 1.0, t)));
      o.rx = (0.04 - 0.018 * smoothstep(0, 0.5, t) + 0.005 * smoothstep(0.5, 0.86, t)) * end;
      o.ry = (0.028 - 0.016 * smoothstep(0, 0.4, t)) * (0.35 + 0.65 * end);
      if (t === 1) o.ry = 0;
    };
    const billCol = (c, t, cs, sn) => {
      c.copy(COL.billBase).lerp(COL.billMid, smoothstep(0.1, 0.6, t)).lerp(COL.billTip, smoothstep(0.8, 0.97, t));
      if (sn > 0.75) c.multiplyScalar(1.1);
      if (sn < -0.3) c.multiplyScalar(0.7);
    };
    const billMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.45 });
    head.add(new THREE.Mesh(buildLoft(billPath, billSec, { radial: 16, colorFn: billCol }), billMat));

    // lower mandible + gular pouch
    const NP = 24;
    const pouchPath = [];
    for (let i = 0; i < NP; i++) {
      const t = i / (NP - 1);
      pouchPath.push(new V3(0, -0.032 - 0.018 * t, 0.035 + 0.52 * t));
    }
    const pouchSec = (t, o) => {
      const depth = 0.008 + 0.058 * Math.pow(Math.sin(Math.PI * Math.min(1, t * 1.25)), 0.9) * (1 - 0.45 * t);
      const end = Math.sqrt(Math.max(0, 1 - smoothstep(0.9, 1.0, t)));
      o.rx = (0.034 - 0.012 * t) * end;
      o.ry = depth * (0.3 + 0.7 * end);
      o.oy = -depth * 0.8 + 0.004;
    };
    const pouchCol = (c, t, cs, sn) => {
      c.copy(COL.pouch).lerp(COL.billMid, smoothstep(0.82, 0.98, t) * 0.8);
      if (sn > 0.4) c.lerp(COL.billBase, 0.5);
    };
    const pouchMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.55 });
    this.pouch = new THREE.Mesh(buildLoft(pouchPath, pouchSec, { radial: 18, colorFn: pouchCol }), pouchMat);
    head.add(this.pouch);

    // eyes
    const eyeMat = new THREE.MeshStandardMaterial({ color: COL.eye, roughness: 0.15 });
    const pupilMat = new THREE.MeshStandardMaterial({ color: '#0b0908', roughness: 0.1 });
    const ringMat = new THREE.MeshStandardMaterial({ color: COL.ring, roughness: 0.6 });
    this.eyes = [];
    for (const s of [1, -1]) {
      const eye = new THREE.Group();
      eye.position.set(0.053 * s, 0.024, 0.03);
      const ball = new THREE.Mesh(new THREE.SphereGeometry(0.016, 16, 12), eyeMat);
      const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.0075, 12, 8), pupilMat);
      pupil.position.set(0.0115 * s, 0.002, 0.005);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.0165, 0.0038, 8, 20), ringMat);
      ring.rotation.y = Math.PI / 2;
      ring.position.x = 0.004 * s;
      eye.add(ball, pupil, ring);
      head.add(eye);
      this.eyes.push(eye);
    }
  }

  buildNeck() {
    this.neckRings = 20;
    this.neckPath = Array.from({ length: this.neckRings }, () => new V3());
    const colorFn = (c, t, cs, sn) => {
      c.copy(COL.chestnut).lerp(COL.neckWhite, smoothstep(-0.5, 0.05, sn));
      c.lerp(COL.neckWhite, smoothstep(0.8, 0.97, t));
      c.lerp(COL.back, smoothstep(0.12, 0.0, t) * 0.7);
    };
    this.neckGeo = createLoftGeometry(this.neckRings, 16, colorFn);
    this.neckSec = (t, o) => {
      const r = 0.085 + (0.05 - 0.085) * smoothstep(0, 0.72, t) + 0.01 * smoothstep(0.78, 1, t);
      o.rx = r * 0.92;
      o.ry = r * 1.05;
    };
    const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95 });
    this.neck = new THREE.Mesh(this.neckGeo, mat);
    this.neck.frustumCulled = false;
    this.body.add(this.neck);
  }

  buildLegs() {
    const footGeo = footGeometry();
    const legMat = new THREE.MeshStandardMaterial({ color: COL.leg, roughness: 0.7 });
    const featherLeg = new THREE.MeshStandardMaterial({ color: COL.belly, roughness: 0.9 });
    const tibiaGeo = new THREE.CylinderGeometry(0.03, 0.022, 1, 10);
    tibiaGeo.translate(0, 0.5, 0);
    const tarsusGeo = new THREE.CylinderGeometry(0.016, 0.014, 1, 8);
    tarsusGeo.translate(0, 0.5, 0);
    this.legParts = [];
    for (const s of [1, -1]) {
      const foot = new THREE.Mesh(footGeo, legMat);
      foot.position.set(0.105 * s, DECK_Y, -0.07);
      foot.rotation.y = 0.18 * s;
      foot.scale.x = s;
      const tibia = new THREE.Mesh(tibiaGeo, featherLeg);
      const tarsus = new THREE.Mesh(tarsusGeo, legMat);
      const knee = new THREE.Mesh(new THREE.SphereGeometry(0.02, 10, 8), legMat);
      this.legs.add(foot, tibia, tarsus, knee);
      this.legParts.push({ s, foot, tibia, tarsus, knee, ankle: new V3(0.105 * s, DECK_Y + 0.02, -0.085) });
    }
  }

  // ctx: { bodyUp (board local), lean, crouch, flap, lookDir (world), dt, t }
  update(t, dt, ctx) {
    const body = this.body;

    // --- body placement in board space ---
    const up = _v.copy(ctx.bodyUp).normalize();
    const fwd = _v2.set(0, 0, 1).addScaledVector(up, -up.z).normalize();
    const side = new V3().crossVectors(up, fwd);
    _m.makeBasis(side, up, fwd);
    body.quaternion.setFromRotationMatrix(_m);
    _q.setFromAxisAngle(side.set(1, 0, 0), 0.08 + ctx.crouch * 0.1); // lean forward a touch when crouching
    body.quaternion.multiply(_q);
    const hipH = 0.4 - ctx.crouch * 0.075;
    body.position.set(0, DECK_Y, -0.05).addScaledVector(up, hipH);
    body.updateMatrixWorld(true);

    // pouch jiggle driven by vertical acceleration
    body.getWorldPosition(_v2);
    if (this.hasPrev && dt > 0) {
      const vel = _v.subVectors(_v2, this.prevWorld).divideScalar(dt);
      const acc = (vel.y - this.prevVel.y) / dt;
      this.prevVel.copy(vel);
      this.jigV += (-140 * this.jig - 7 * this.jigV - clamp(acc, -40, 40) * 0.05) * dt;
      this.jig += this.jigV * dt;
      this.jig = clamp(this.jig, -0.25, 0.25);
    }
    this.prevWorld.copy(_v2);
    this.hasPrev = true;
    const js = 1 + this.jig + 0.03 * Math.sin(t * 9.0);
    this.pouch.scale.set(1, js, 1);
    this.pouch.position.y = -0.035 * (1 - js);

    // --- wings: balancing ---
    const lean = ctx.lean;
    const flap = ctx.flap;
    for (const w of this.wings) {
      const s = w.side;
      const ph = s * 0.7;
      const raise = 0.42 - s * lean * 0.45 + 0.07 * Math.sin(t * 1.7 + ph) + flap * 0.85;
      const sweep = -0.18 + 0.08 * Math.sin(t * 0.9 + ph) - flap * 0.15;
      const twist = -0.14 + 0.06 * Math.sin(t * 2.1 + ph) + flap * 0.15;
      w.arm.rotation.set(twist, sweep, raise);
      w.fore.rotation.set(0.02, 0.55 - flap * 0.25 + 0.05 * Math.sin(t * 1.3 + ph), -0.16 - flap * 0.35 + 0.05 * Math.sin(t * 2.3 + ph));
      w.hand.rotation.set(0.0, 0.42 + 0.08 * Math.sin(t * 1.1 + ph), -0.2 - flap * 0.45 + 0.06 * Math.sin(t * 2.7 + ph));
      const spread = 0.9 + 0.12 * Math.sin(t * 0.8 + ph) + flap * 0.15;
      for (const p of w.primaries) {
        p.m.rotation.y = p.yaw * spread;
        p.m.rotation.z = 0.07 * Math.sin(t * 19 + p.i * 1.3 + ph) * (0.4 + p.i / 9);
        p.m.rotation.x = -0.03 + 0.05 * Math.sin(t * 13 + p.i);
      }
    }
    this.tail.rotation.x = 0.28 + 0.08 * Math.sin(t * 1.7) - lean * 0.05;
    this.tail.rotation.y = lean * 0.25;
    for (const f of this.tailFeathers) f.m.rotation.y = f.yaw * (1 + 0.12 * Math.sin(t * 1.3));

    // --- head: stabilised in world space, looking where it goes ---
    const look = ctx.lookDir;
    _m.lookAt(look, ZERO, UP);
    _q.setFromRotationMatrix(_m);
    _q2.setFromEuler(_e.set(0.24 + 0.05 * Math.sin(t * 0.7), 0, 0.06 * Math.sin(t * 0.53)));
    _q.multiply(_q2);
    body.getWorldQuaternion(_q2).invert();
    _q2.multiply(_q);
    // limit how far the head can twist relative to the body
    const ang = 2 * Math.acos(clamp(Math.abs(_q2.w), 0, 1));
    if (ang > 1.4) _q2.slerp(_q.identity(), 1 - 1.4 / ang);
    this.headQ.slerp(_q2, 1 - Math.exp(-dt * 9));
    this.head.quaternion.copy(this.headQ);
    _v.set(0, 0, 1).applyQuaternion(this.headQ);
    this.head.position.copy(HEAD_REST);
    this.head.position.x += _v.x * 0.05;
    this.head.position.y -= ctx.crouch * 0.03;
    this.head.position.z += _v.z * 0.02;

    // blink
    if (t > this.nextBlink + 0.14) this.nextBlink = t + 2.2 + rnd() * 4;
    const blink = t > this.nextBlink && t < this.nextBlink + 0.14 ? 0.12 : 1;
    for (const e of this.eyes) e.scale.y = blink;

    // --- neck: cubic Bezier from chest to the back of the skull ---
    const P0 = _v.copy(NECK_BASE).applyQuaternion(this.torso.quaternion);
    const P1 = new V3(0, 0.12, 0.13).applyQuaternion(this.torso.quaternion).add(P0);
    const P3 = new V3().copy(HEAD_ATTACH).applyQuaternion(this.head.quaternion).add(this.head.position);
    const P2 = new V3(0, -0.075, -0.15).applyQuaternion(this.head.quaternion).add(P3);
    const n = this.neckRings;
    for (let i = 0; i < n; i++) {
      const s = i / (n - 1);
      const a = (1 - s) * (1 - s) * (1 - s), b = 3 * (1 - s) * (1 - s) * s, c = 3 * (1 - s) * s * s, d = s * s * s;
      this.neckPath[i].set(
        a * P0.x + b * P1.x + c * P2.x + d * P3.x,
        a * P0.y + b * P1.y + c * P2.y + d * P3.y,
        a * P0.z + b * P1.z + c * P2.z + d * P3.z,
      );
    }
    // extend a little into the head so no gap opens
    this.neckPath[n - 1].addScaledVector(_v2.subVectors(P3, P2).normalize(), 0.03);
    updateLoft(this.neckGeo, this.neckPath, this.neckSec, _v2.set(0, 0, 1));

    // --- legs: two-bone IK from hips (body) to ankles (board) ---
    for (const L of this.legParts) {
      const hip = _v.copy(HIP);
      hip.x *= L.s;
      hip.applyQuaternion(this.torso.quaternion).applyQuaternion(body.quaternion).add(body.position);
      const ank = L.ankle;
      const dir = _v2.subVectors(ank, hip);
      let d = dir.length();
      dir.divideScalar(d);
      d = clamp(d, 0.05, TIBIA + TARSUS - 0.002);
      const a = (TIBIA * TIBIA - TARSUS * TARSUS + d * d) / (2 * d);
      const h = Math.sqrt(Math.max(0, TIBIA * TIBIA - a * a));
      // the visible joint of a bird's leg (the ankle) bends backwards
      const pole = new V3(0, 0, -1).addScaledVector(dir, -(-dir.z));
      pole.normalize();
      const knee = new V3().copy(hip).addScaledVector(dir, a).addScaledVector(pole, h);
      L.knee.position.copy(knee);
      orientSegment(L.tibia, hip, knee);
      orientSegment(L.tarsus, knee, ank);
    }
  }
}

const _dir = new V3();
function orientSegment(mesh, a, b) {
  _dir.subVectors(b, a);
  const len = _dir.length();
  mesh.position.copy(a);
  mesh.quaternion.setFromUnitVectors(UP, _dir.divideScalar(len));
  mesh.scale.set(1, len, 1);
}
