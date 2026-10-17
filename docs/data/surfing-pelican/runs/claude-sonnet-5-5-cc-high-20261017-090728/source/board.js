import * as THREE from "three";

export const BOARD_LEN = 3.4;
const HALF = BOARD_LEN / 2;

// s: 0 at tail, 1 at nose
function halfWidth(s) {
  if (s >= 0.45) {
    const k = (s - 0.45) / 0.55;
    return 0.46 * Math.pow(Math.max(1 - k * k, 0), 0.55);
  }
  const k = (0.45 - s) / 0.58;
  return 0.46 * Math.pow(Math.max(1 - k * k, 0), 0.5);
}

const rocker = (z) => 0.16 * Math.pow(Math.abs(z) / HALF, 2.4);
const thickness = (s) => Math.min(1, Math.min(s, 1 - s) * 9 + 0.15);
// domed deck and rounded belly, as a function of lateral fraction f = x / halfwidth
const top = (f, s) => 0.05 * thickness(s) * (1 - f * f);
const bottom = (f, s) => -(0.1 * thickness(s)) * (1 - 0.8 * Math.pow(Math.abs(f), 2.5));

function buildHull() {
  const S = 80; // along the length
  const R = 16; // across half the section
  const pos = [];
  const idx = [];
  const ring = R * 2;
  for (let i = 0; i <= S; i++) {
    const s = i / S;
    const z = (s - 0.5) * BOARD_LEN;
    const hw = Math.max(halfWidth(s), 0.004);
    const rk = rocker(z);
    for (let j = 0; j < R; j++) {
      const f = -1 + (2 * j) / R; // -1 .. just under 1
      pos.push(f * hw, rk + top(f, s), z);
    }
    for (let j = 0; j < R; j++) {
      const f = 1 - (2 * j) / R; // 1 .. just above -1
      pos.push(f * hw, rk + bottom(f, s), z);
    }
  }
  for (let i = 0; i < S; i++) {
    for (let j = 0; j < ring; j++) {
      const a = i * ring + j;
      const b = i * ring + ((j + 1) % ring);
      idx.push(a, a + ring, b, b, a + ring, b + ring);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

export function createBoard() {
  const board = new THREE.Group();
  const hull = new THREE.Mesh(
    buildHull(),
    new THREE.MeshPhysicalMaterial({
      color: 0xff5a36,
      roughness: 0.32,
      clearcoat: 1,
      clearcoatRoughness: 0.15,
    })
  );
  hull.castShadow = true;
  hull.receiveShadow = true;
  board.add(hull);

  // stripes sit just above the domed deck
  const addStripe = (center, width, color) => {
    const S = 70;
    const W = 4;
    const pos = [];
    const idx = [];
    for (let i = 0; i <= S; i++) {
      const s = 0.04 + (i / S) * 0.92;
      const z = (s - 0.5) * BOARD_LEN;
      const hw = Math.max(halfWidth(s), 0.004);
      for (let j = 0; j <= W; j++) {
        const x = (center + (j / W - 0.5) * width) * hw * 2.1;
        const f = THREE.MathUtils.clamp(x / hw, -0.97, 0.97);
        pos.push(f * hw, rocker(z) + top(f, s) + 0.004, z);
      }
    }
    for (let i = 0; i < S; i++) {
      for (let j = 0; j < W; j++) {
        const a = i * (W + 1) + j;
        idx.push(a, a + W + 1, a + 1, a + 1, a + W + 1, a + W + 2);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color, roughness: 0.4, side: THREE.DoubleSide }));
    m.receiveShadow = true;
    board.add(m);
  };
  addStripe(0, 0.07, 0xfff4de);
  addStripe(0.2, 0.025, 0xffd23f);
  addStripe(-0.2, 0.025, 0xffd23f);

  // tail fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.quadraticCurveTo(0.02, -0.18, 0.2, -0.26);
  finShape.lineTo(0.2, 0);
  const fin = new THREE.Mesh(
    new THREE.ExtrudeGeometry(finShape, { depth: 0.02, bevelEnabled: false }),
    new THREE.MeshStandardMaterial({ color: 0x1b2a3a, roughness: 0.5 })
  );
  fin.rotation.y = -Math.PI / 2;
  fin.position.set(0.01, -0.1, -HALF + 0.45);
  board.add(fin);

  return board;
}
