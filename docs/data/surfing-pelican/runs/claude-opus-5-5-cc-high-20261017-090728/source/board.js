import * as THREE from "three";
import { loft, v3 } from "./loft.js";

export const BOARD_LENGTH = 2.3;

// Half-width of the outline at u in [0,1] (tail -> nose).
function halfWidth(u) {
  const e = Math.max(0, 1 - ((u - 0.45) / 0.55) ** 2);
  const tailRound = Math.min(1, u / 0.03) ** 0.5;
  return 0.29 * Math.pow(e, 0.36) * tailRound + 0.002;
}
function rocker(x) {
  const n = Math.max(0, (x - 0.35) / 0.8);
  const t = Math.max(0, (-x - 0.7) / 0.45);
  return 0.13 * n * n + 0.035 * t * t;
}

export function createBoard() {
  const group = new THREE.Group();
  const L = BOARD_LENGTH;
  const pts = [];
  for (let i = 0; i <= 24; i++) {
    const x = -L / 2 + (i / 24) * L;
    pts.push(v3(x, rocker(x), 0));
  }
  const deck = new THREE.Color("#fbf3e4");
  const bottom = new THREE.Color("#e9dccb");
  const stripe = new THREE.Color("#e2492f");
  const stripe2 = new THREE.Color("#2b8fb3");
  const rail = new THREE.Color("#f2b134");
  const geo = loft(
    pts,
    (t) => {
      const w = halfWidth(t);
      const thick = 0.045 * Math.pow(Math.sin(Math.PI * Math.min(1, t * 0.97 + 0.02)), 0.4) + 0.006;
      return [w, thick];
    },
    {
      segments: 90,
      radial: 28,
      power: 0.55,
      color: (t, off, c) => {
        const up = off.y;
        const side = Math.abs(off.z);
        const w = halfWidth(t);
        if (up < -0.004) return c.copy(bottom);
        if (side > w * 0.86) return c.copy(rail);
        // centre stripe plus a band near the nose
        if (side < 0.03 && t > 0.08 && t < 0.84) return c.copy(stripe);
        if (side < 0.052 && side > 0.04 && t > 0.08 && t < 0.84) return c.copy(stripe2);
        if (t > 0.86 && t < 0.885) return c.copy(stripe);
        return c.copy(deck);
      },
    }
  );
  // the loft path is centred in the board; lift so the deck sits at y≈0
  geo.translate(0, -0.045, 0);
  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.35, metalness: 0.0 });
  const board = new THREE.Mesh(geo, mat);
  board.castShadow = true;
  board.receiveShadow = true;
  group.add(board);

  // single fin
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.quadraticCurveTo(-0.02, -0.12, -0.13, -0.2);
  finShape.quadraticCurveTo(-0.08, -0.08, -0.16, 0);
  finShape.lineTo(0, 0);
  const finGeo = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.012,
    bevelEnabled: true,
    bevelThickness: 0.004,
    bevelSize: 0.004,
    bevelSegments: 2,
    curveSegments: 10,
  });
  finGeo.translate(0, 0, -0.006);
  const fin = new THREE.Mesh(finGeo, new THREE.MeshStandardMaterial({ color: "#2b8fb3", roughness: 0.3 }));
  fin.position.set(-L / 2 + 0.28, -0.075, 0);
  fin.castShadow = true;
  group.add(fin);

  return { group, deckHeight: (x) => rocker(x) - 0.004 };
}
