import * as THREE from 'three';

export const BOARD_LENGTH = 1.9;
const HALF_W = 0.28;
const THICK = 0.075;
const LIFT = 0.03; // raises the board so its belly sits at y = 0

function halfWidth(t) {
  if (t >= 0.45) return HALF_W * Math.pow(Math.max(0, 1 - Math.pow((t - 0.45) / 0.55, 2)), 0.5);
  return 0.11 + (HALF_W - 0.11) * Math.pow(Math.sin((t / 0.45) * Math.PI * 0.5), 0.8);
}
function rocker(t) {
  return t > 0.45 ? 0.13 * Math.pow((t - 0.45) / 0.55, 2.2) : 0.05 * Math.pow((0.45 - t) / 0.45, 2);
}
function thickness(t) {
  return THICK * Math.pow(Math.sin(Math.PI * t), 0.45);
}

// deck height (board-local y) at the stance
export const DECK_Y = LIFT + rocker(0.47) + thickness(0.47) * 0.62;

function deckTexture() {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 1024;
  const g = c.getContext('2d');
  g.fillStyle = '#f4eee2';
  g.fillRect(0, 0, 256, 1024);
  // soft resin tint towards the rails
  const rail = g.createLinearGradient(0, 0, 256, 0);
  rail.addColorStop(0, 'rgba(214,190,150,0.55)');
  rail.addColorStop(0.18, 'rgba(214,190,150,0)');
  rail.addColorStop(0.82, 'rgba(214,190,150,0)');
  rail.addColorStop(1, 'rgba(214,190,150,0.55)');
  g.fillStyle = rail;
  g.fillRect(0, 0, 256, 1024);
  // nose stripes (canvas y = (1 - v) * 1024; v = 0 tail, 1 nose)
  const band = (v0, v1, col) => {
    g.fillStyle = col;
    g.fillRect(0, (1 - v1) * 1024, 256, (v1 - v0) * 1024);
  };
  band(0.7, 0.735, '#ff6a4d');
  band(0.745, 0.765, '#ffb347');
  band(0.775, 0.79, '#17a3a3');
  // retro sunset logo
  const cx = 128, cy = (1 - 0.36) * 1024, R = 74;
  g.save();
  g.beginPath();
  g.arc(cx, cy, R, 0, Math.PI * 2);
  g.clip();
  const grad = g.createLinearGradient(0, cy - R, 0, cy + R);
  grad.addColorStop(0, '#ffd166');
  grad.addColorStop(0.5, '#ff7a4d');
  grad.addColorStop(1, '#d6336c');
  g.fillStyle = grad;
  g.fillRect(cx - R, cy - R, 2 * R, 2 * R);
  g.fillStyle = '#f4eee2';
  for (let k = 0; k < 6; k++) {
    const y = cy + 6 + k * 12;
    g.fillRect(cx - R, y, 2 * R, 2 + k * 1.2);
  }
  g.restore();
  // stringer
  g.fillStyle = '#9a6a3a';
  g.fillRect(126.5, 0, 3, 1024);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function buildSurface(top) {
  const NL = 72;
  const NW = 22;
  const pos = [];
  const uv = [];
  const idx = [];
  for (let i = 0; i <= NL; i++) {
    const t = 0.5 - 0.5 * Math.cos((Math.PI * i) / NL);
    const z = (t - 0.5) * BOARD_LENGTH;
    const w = halfWidth(t);
    const r = rocker(t) + LIFT;
    const th = thickness(t);
    for (let j = 0; j <= NW; j++) {
      const s = -1 + (2 * j) / NW;
      const a = Math.abs(s);
      const y = top
        ? r + th * 0.62 * Math.pow(Math.max(0, 1 - a * a), 0.42)
        : r - th * 0.38 * Math.pow(Math.max(0, 1 - a * a * a), 0.3);
      pos.push(s * w, y, z);
      uv.push(j / NW, t);
    }
  }
  for (let i = 0; i < NL; i++) {
    for (let j = 0; j < NW; j++) {
      const a = i * (NW + 1) + j;
      const b = a + 1;
      const c = a + NW + 1;
      const d = c + 1;
      if (top) idx.push(a, c, b, b, c, d);
      else idx.push(a, b, c, b, d, c);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

function finGeometry(scale) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.quadraticCurveTo(0.02, 0.07, 0.085, 0.12);
  s.quadraticCurveTo(0.075, 0.05, 0.11, 0);
  s.lineTo(0, 0);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.008, bevelEnabled: true, bevelThickness: 0.002, bevelSize: 0.002, bevelSegments: 1, curveSegments: 8 });
  geo.translate(-0.055, 0, -0.004);
  geo.scale(scale, scale, 1);
  return geo;
}

const FIN_BASE = new THREE.Quaternion().setFromRotationMatrix(
  new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, -1, 0), new THREE.Vector3(-1, 0, 0)),
);

export function createSurfboard() {
  const group = new THREE.Group();
  const deckMat = new THREE.MeshPhysicalMaterial({ map: deckTexture(), roughness: 0.38, clearcoat: 0.8, clearcoatRoughness: 0.12 });
  const bottomMat = new THREE.MeshPhysicalMaterial({ color: '#1d8f8c', roughness: 0.35, clearcoat: 0.7, clearcoatRoughness: 0.15 });
  const finMat = new THREE.MeshStandardMaterial({ color: '#2b2b30', roughness: 0.4 });

  const deck = new THREE.Mesh(buildSurface(true), deckMat);
  const bottom = new THREE.Mesh(buildSurface(false), bottomMat);
  deck.castShadow = bottom.castShadow = true;
  deck.receiveShadow = true;
  group.add(deck, bottom);

  // thruster set; shape is drawn in the xy plane, rotated to hang under the tail
  const fins = [
    { t: 0.065, x: 0, toe: 0, cant: 0, s: 1.0 },
    { t: 0.15, x: 0.165, toe: -0.06, cant: -0.12, s: 0.9 },
    { t: 0.15, x: -0.165, toe: 0.06, cant: 0.12, s: 0.9 },
  ];
  for (const f of fins) {
    const fin = new THREE.Mesh(finGeometry(f.s), finMat);
    const z = (f.t - 0.5) * BOARD_LENGTH;
    const y = LIFT + rocker(f.t) - thickness(f.t) * 0.3;
    fin.position.set(f.x, y, z);
    // shape +x -> board -z (fin trails backwards), shape +y -> board -y (hangs down)
    fin.quaternion.setFromEuler(new THREE.Euler(0, f.toe, f.cant)).multiply(FIN_BASE);
    fin.castShadow = true;
    group.add(fin);
  }
  return group;
}
