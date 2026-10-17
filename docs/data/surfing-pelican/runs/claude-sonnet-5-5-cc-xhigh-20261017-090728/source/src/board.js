import * as THREE from "three";
import { crow, clamp } from "./geo.js";

export const BOARD = { L: 1.95, W: 0.58, T: 0.064 };

function boardTexture() {
  const W = 1024;
  const H = 512;
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const g = c.getContext("2d");
  // v: 0..0.5 deck (rail -> centre -> rail), 0.5..1 bottom
  const deck = g.createLinearGradient(0, 0, W, 0);
  deck.addColorStop(0, "#f4532c");
  deck.addColorStop(0.55, "#e8321f");
  deck.addColorStop(1, "#f86a2a");
  g.fillStyle = deck;
  g.fillRect(0, 0, W, H / 2);
  // cream rails (edges of the deck half)
  g.fillStyle = "#fff1d6";
  g.fillRect(0, 0, W, H * 0.045);
  g.fillRect(0, H * 0.5 - H * 0.045, W, H * 0.045);
  // centre stripe
  g.fillStyle = "#fff1d6";
  g.fillRect(0, H * 0.25 - H * 0.032, W, H * 0.064);
  g.fillStyle = "#1c7f92";
  g.fillRect(0, H * 0.25 - H * 0.007, W, H * 0.014);
  // thin accent lines
  g.fillStyle = "#1c7f92";
  g.fillRect(0, H * 0.115, W, H * 0.008);
  g.fillRect(0, H * 0.385 - H * 0.008, W, H * 0.008);
  // sun + waves emblem near the nose (u close to 1)
  const ex = W * 0.8;
  const ey = H * 0.25;
  g.fillStyle = "#fff1d6";
  g.beginPath();
  g.arc(ex, ey - H * 0.02, H * 0.065, 0, Math.PI * 2);
  g.fill();
  g.strokeStyle = "#1c7f92";
  g.lineWidth = H * 0.012;
  g.lineCap = "round";
  for (let i = 0; i < 3; i++) {
    g.beginPath();
    const yy = ey + H * 0.045 + i * H * 0.022;
    g.moveTo(ex - H * 0.1, yy);
    for (let k = 0; k <= 8; k++) g.lineTo(ex - H * 0.1 + (k / 8) * H * 0.2, yy + Math.sin(k * 1.6 + i) * H * 0.008);
    g.stroke();
  }
  // traction pad near the tail
  g.fillStyle = "#2a2f36";
  const rr = (x, y, w, h, r) => {
    g.beginPath();
    g.moveTo(x + r, y);
    g.arcTo(x + w, y, x + w, y + h, r);
    g.arcTo(x + w, y + h, x, y + h, r);
    g.arcTo(x, y + h, x, y, r);
    g.arcTo(x, y, x + w, y, r);
    g.closePath();
    g.fill();
  };
  rr(W * 0.1, H * 0.25 - H * 0.12, W * 0.2, H * 0.24, 18);
  // pad grooves
  g.strokeStyle = "#3d444d";
  g.lineWidth = 2;
  for (let i = 0; i < 14; i++) {
    g.beginPath();
    g.moveTo(W * 0.1 + 6 + i * (W * 0.2 - 12) / 13, H * 0.25 - H * 0.11);
    g.lineTo(W * 0.1 + 6 + i * (W * 0.2 - 12) / 13, H * 0.25 + H * 0.11);
    g.stroke();
  }
  // bottom
  g.fillStyle = "#fff3dc";
  g.fillRect(0, H * 0.5, W, H * 0.5);
  g.fillStyle = "#2fb7b0";
  g.fillRect(0, H * 0.5, W * 0.18, H * 0.5);
  g.fillStyle = "#ff6a4d";
  g.fillRect(W * 0.18, H * 0.5, W * 0.02, H * 0.5);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  tex.wrapS = THREE.ClampToEdgeWrapping;
  tex.flipY = false;
  return tex;
}

function finGeometry(h, base, sweep) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.lineTo(base, 0);
  s.quadraticCurveTo(base * 0.55, h * 0.5, sweep, h);
  s.quadraticCurveTo(base * 0.1, h * 0.55, 0, 0);
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.008, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 2, curveSegments: 10 });
  g.translate(0, 0, -0.004);
  return g;
}

export function createBoard() {
  const { L, W, T } = BOARD;
  const group = new THREE.Group();
  const outline = [
    [0.0, 0.46],
    [0.04, 0.68],
    [0.14, 0.89],
    [0.3, 0.985],
    [0.45, 1.0],
    [0.62, 0.935],
    [0.78, 0.75],
    [0.9, 0.48],
    [0.965, 0.24],
    [0.99, 0.12],
    [1.0, 0.0],
  ];
  const rocker = [
    [0.0, 0.042],
    [0.12, 0.01],
    [0.4, 0.0],
    [0.62, 0.006],
    [0.82, 0.05],
    [0.93, 0.105],
    [1.0, 0.17],
  ];
  const nU = 72;
  const nV = 44;
  const pos = [];
  const uv = [];
  const idx = [];
  const rk0 = crow(rocker, 0.45)[1];
  for (let i = 0; i <= nU; i++) {
    const u = i / nU;
    const hw = Math.max(crow(outline, u)[1], 0) * (W / 2);
    const rk = crow(rocker, u)[1];
    const th = T * (0.22 + 0.78 * Math.pow(Math.sin(Math.PI * clamp(u * 0.94 + 0.03, 0, 1)), 0.65));
    for (let j = 0; j <= nV; j++) {
      const a = (j / nV) * Math.PI * 2;
      const c = Math.cos(a);
      const s = Math.sin(a);
      const z = hw * Math.sign(c) * Math.pow(Math.abs(c), 0.55);
      const top = s >= 0;
      const y = rk - rk0 + (top ? 0.58 * th * Math.pow(s, 0.75) : 0.42 * th * s * Math.pow(Math.abs(s), -0.2) * 1.0);
      pos.push((u - 0.5) * L, y - 0.58 * T * 0.0, z);
      uv.push(u, j / nV);
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
  // tail cap
  const capStart = pos.length / 3;
  pos.push(-0.5 * L, 0.0, 0);
  uv.push(0, 0.5);
  for (let j = 0; j <= nV; j++) idx.push(capStart, j + 1 > nV ? 0 : j + 1, j);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  geo.setIndex(idx);
  geo.computeVertexNormals();

  const mat = new THREE.MeshPhysicalMaterial({
    map: boardTexture(),
    roughness: 0.4,
    metalness: 0,
    clearcoat: 0.6,
    clearcoatRoughness: 0.12,
    envMapIntensity: 0.7,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);

  // fins
  const finMat = new THREE.MeshPhysicalMaterial({ color: 0xfff0d6, roughness: 0.35, clearcoat: 0.6 });
  const mkFin = (x, z, h, base, sweep, toe) => {
    const m = new THREE.Mesh(finGeometry(h, base, sweep), finMat);
    m.rotation.y = toe;
    m.position.set(x, -0.012, z);
    m.scale.set(-1, -1, 1);
    m.castShadow = true;
    group.add(m);
  };
  mkFin(-0.7, 0, 0.12, 0.13, 0.13, 0);
  mkFin(-0.6, 0.15, 0.115, 0.12, 0.12, -0.05);
  mkFin(-0.6, -0.15, 0.115, 0.12, 0.12, 0.05);
  return group;
}
