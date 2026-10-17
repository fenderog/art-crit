import * as THREE from "three";
import { PALETTE } from "./palette.js";

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const sstep = (e0, e1, x) => {
  const t = clamp((x - e0) / (e1 - e0 || 1e-6), 0, 1);
  return t * t * (3 - 2 * t);
};

/**
 * A surfboard built as a swept parametric surface.
 *   local frame: +Z = nose, +X = right rail, +Y = up, y = 0 is the waterline
 *   u = 0 at the tail, u = 1 at the nose tip
 */
export const BOARD = {
  length: 4.9,
  width: 1.02,
  thickness: 0.19,
  tailZ: 0, // computed below
  noseZ: 0,
};
BOARD.tailZ = -BOARD.length * 0.42;
BOARD.noseZ = BOARD.length * 0.58;

function widthAt(u) {
  const W = BOARD.width;
  const t = u - 0.42;
  const half = t < 0 ? 0.54 : 0.70; // tail is shorter than the nose
  const tn = clamp(Math.abs(t) / half, 0, 1);
  const e = t < 0 ? 2.1 : 2.6;
  return Math.max(0.004, W * Math.max(0, 1 - Math.pow(tn, e)));
}

function thicknessAt(u) {
  const w = widthAt(u) / BOARD.width;
  return BOARD.thickness * (0.28 + 0.72 * Math.pow(w, 0.55));
}

function rockerAt(u) {
  const nose = 0.62 * Math.pow(clamp((u - 0.52) / 0.48, 0, 1), 2.3);
  const tail = 0.24 * Math.pow(clamp((0.30 - u) / 0.30, 0, 1), 2.0);
  return nose + tail;
}

function zAt(u) {
  return BOARD.tailZ + u * BOARD.length;
}

const RADIAL = 30;
const LONG = 110;

function boardGeometry() {
  const pos = [];
  const col = [];
  const idx = [];

  const deck = new THREE.Color(PALETTE.boardDeck);
  const bottom = new THREE.Color(PALETTE.boardBottom);
  const stripe = new THREE.Color(PALETTE.boardStripe);
  const rail = new THREE.Color(PALETTE.boardRail);
  const pad = new THREE.Color("#2b3b45");
  const noseFade = new THREE.Color("#f6d9a8");
  const tmp = new THREE.Color();

  // pass 1: find the lowest point so the board rests exactly on y = 0
  let minY = Infinity;
  for (let i = 0; i <= LONG; i++) {
    const u = i / LONG;
    minY = Math.min(minY, rockerAt(u) - 0.58 * thicknessAt(u));
  }

  for (let i = 0; i <= LONG; i++) {
    const u = i / LONG;
    const hw = widthAt(u) * 0.5;
    const th = thicknessAt(u);
    const z = zAt(u);
    const rock = rockerAt(u) - minY;

    for (let j = 0; j <= RADIAL; j++) {
      const a = (j / RADIAL) * Math.PI * 2;
      const sx = Math.sin(a);
      const sy = Math.cos(a);

      const x = hw * Math.sign(sx) * Math.pow(Math.abs(sx), 0.70);
      const y =
        sy >= 0
          ? rock + th * 0.42 * Math.pow(sy, 0.72)
          : rock - th * 0.58 * Math.pow(-sy, 1.7);

      pos.push(x, y, z);

      // --- paint ---------------------------------------------------------
      const xn = clamp(x / Math.max(hw, 1e-4), -1, 1);
      tmp.copy(bottom).lerp(deck, sstep(-0.06, 0.26, sy));
      tmp.lerp(rail, (1 - sstep(0.0, 0.16, Math.abs(sy))) * 0.9);

      // deck stringer stripe
      const st = (1 - sstep(0.075, 0.15, Math.abs(xn))) * sstep(0.06, 0.3, sy);
      tmp.lerp(stripe, st * 0.95);

      // wax / traction pad where the feet land
      const pd =
        sstep(0.26, 0.33, u) *
        (1 - sstep(0.60, 0.66, u)) *
        (1 - sstep(0.40, 0.56, Math.abs(xn))) *
        sstep(0.12, 0.4, sy);
      tmp.lerp(pad, pd * 0.85);

      // warm fade toward the nose on the bottom
      tmp.lerp(noseFade, sstep(0.72, 1.0, u) * (1 - sstep(0.0, 0.4, sy)) * 0.55);

      col.push(tmp.r, tmp.g, tmp.b);
    }
  }

  const row = RADIAL + 1;
  for (let i = 0; i < LONG; i++) {
    for (let j = 0; j < RADIAL; j++) {
      const a = i * row + j;
      const b = a + 1;
      const c = a + row;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  geo.computeBoundingSphere();
  return geo;
}

function finGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0.06, -0.20, 0.30, -0.42, 0.62, -0.46);
  shape.bezierCurveTo(0.52, -0.30, 0.44, -0.14, 0.46, 0.0);
  shape.lineTo(0, 0);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.045,
    bevelEnabled: true,
    bevelSize: 0.018,
    bevelThickness: 0.018,
    bevelSegments: 3,
    curveSegments: 12,
  });
  geo.rotateY(Math.PI / 2); // thin along X
  geo.translate(-0.0225, 0, 0);
  geo.computeVertexNormals();
  return geo;
}

export function createSurfboard() {
  const group = new THREE.Group();

  const hull = new THREE.Mesh(
    boardGeometry(),
    new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.30,
      metalness: 0.0,
      envMapIntensity: 1.0,
    })
  );
  hull.name = "board-hull";
  group.add(hull);

  const finMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(PALETTE.fin),
    roughness: 0.35,
    metalness: 0.05,
  });

  const fin = new THREE.Mesh(finGeometry(), finMat);
  fin.scale.setScalar(0.95);
  fin.position.set(0, 0.02, zAt(0.14));
  fin.rotation.x = -0.12;
  group.add(fin);

  // two small side bites
  for (const s of [-1, 1]) {
    const bite = new THREE.Mesh(finGeometry(), finMat);
    bite.scale.set(0.42, 0.42, 0.42);
    bite.position.set(s * 0.16, 0.015, zAt(0.235));
    bite.rotation.set(-0.05, 0, s * 0.32);
    group.add(bite);
  }

  // leash plug at the tail
  const plug = new THREE.Mesh(
    new THREE.CylinderGeometry(0.045, 0.05, 0.05, 12),
    new THREE.MeshStandardMaterial({ color: 0x2a2a2e, roughness: 0.6 })
  );
  plug.position.set(0, 0.055, zAt(0.045));
  group.add(plug);

  group.userData.zAt = zAt;
  return group;
}
