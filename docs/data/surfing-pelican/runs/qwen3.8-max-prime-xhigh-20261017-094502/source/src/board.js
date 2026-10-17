import * as THREE from "three";
import { smoothShape, taperedTube, smoothstep, lerp } from "./util.js";

/* Surfboard outline stations: [x along the board, half width] */
const STATIONS = [
  [1.72, 0.0],
  [1.6, 0.075],
  [1.42, 0.152],
  [1.15, 0.222],
  [0.8, 0.27],
  [0.42, 0.3],
  [0.1, 0.314],
  [-0.3, 0.31],
  [-0.7, 0.296],
  [-1.05, 0.276],
  [-1.32, 0.252],
  [-1.5, 0.222],
  [-1.6, 0.172],
  [-1.65, 0.088],
  [-1.66, 0.0],
];

export const DECK_Y = 0.051;

/** Half width of the outline at a given station (linear between control points). */
export function halfWidthAt(x) {
  const s = STATIONS;
  if (x >= s[0][0]) return s[0][1];
  if (x <= s[s.length - 1][0]) return s[s.length - 1][1];
  for (let i = 0; i < s.length - 1; i++) {
    const a = s[i];
    const b = s[i + 1];
    if (x <= a[0] && x >= b[0]) return lerp(a[1], b[1], (a[0] - x) / (a[0] - b[0]));
  }
  return 0.2;
}

/** Thickness taper + rocker as a function of x — shared by the blank and the deck pad. */
function foilY(x, y) {
  const noseT = smoothstep(0.55, 1.62, x);
  const tailT = smoothstep(-0.75, -1.58, x);
  let yy = y * (1 - 0.55 * Math.pow(noseT, 1.3) - 0.45 * Math.pow(tailT, 1.3));
  yy += 0.3 * Math.pow(Math.max(0, (x - 0.55) / 1.2), 2.4);
  yy += 0.16 * Math.pow(Math.max(0, (-0.72 - x) / 0.95), 2.2);
  return yy;
}

export const deckHeightAt = (x) => foilY(x, DECK_Y);
export const hullHeightAt = (x) => foilY(x, -DECK_Y);

function finGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0.0, 0.03);
  s.bezierCurveTo(0.05, -0.06, 0.09, -0.135, 0.16, -0.168);
  s.lineTo(0.29, -0.162);
  s.bezierCurveTo(0.3, -0.08, 0.325, -0.02, 0.34, 0.03);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, {
    depth: 0.014,
    bevelEnabled: true,
    bevelThickness: 0.005,
    bevelSize: 0.005,
    bevelSegments: 2,
    curveSegments: 8,
  });
  g.translate(0, 0, -0.007);
  return g;
}

export function createBoard({ speckleTex }) {
  const group = new THREE.Group();

  /* ---- blank ------------------------------------------------------- */
  const outline = [];
  for (const [x, w] of STATIONS) outline.push([x, w]);
  for (let i = STATIONS.length - 2; i >= 1; i--) outline.push([STATIONS[i][0], -STATIONS[i][1]]);
  outline.push([STATIONS[0][0], STATIONS[0][1]]); // close the loop smoothly at the nose

  const shape = smoothShape(outline, 8, true);
  const blank = new THREE.ExtrudeGeometry(shape, {
    depth: 0.05,
    bevelEnabled: true,
    bevelThickness: 0.026,
    bevelSize: 0.028,
    bevelSegments: 3,
    curveSegments: 6,
    steps: 1,
  });
  blank.rotateX(-Math.PI / 2);
  blank.translate(0, -(0.05 / 2), 0);

  const pos = blank.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    pos.setY(i, foilY(pos.getX(i), pos.getY(i)));
  }
  pos.needsUpdate = true;
  blank.computeVertexNormals();

  // livery baked into vertex colours
  {
    const deck = new THREE.Color("#f4eee1");
    const hull = new THREE.Color("#e8e2d6");
    const rail = new THREE.Color("#12798a");
    const pin = new THREE.Color("#e4633f");
    const wood = new THREE.Color("#a5713c");
    const tail = new THREE.Color("#f0b23c");
    const nrm = blank.attributes.normal;
    const colors = new Float32Array(pos.count * 3);
    const c = new THREE.Color();
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);
      const ny = nrm.getY(i);
      c.copy(y > 0 ? deck : hull);

      // rail band
      const railAmt = smoothstep(0.35, 0.85, 1 - Math.abs(ny));
      c.lerp(rail, railAmt * 0.92);
      // coral pinstripe just above the rail
      const stripe = smoothstep(0.02, 0.032, Math.abs(y)) * smoothstep(0.05, 0.036, Math.abs(y));
      c.lerp(pin, stripe * (1 - railAmt) * 0.95);
      // nose + tail blocks
      c.lerp(pin, smoothstep(1.34, 1.66, x) * 0.85);
      c.lerp(tail, smoothstep(-1.34, -1.62, x) * 0.7);
      // stringer
      const stringer = smoothstep(0.022, 0.012, Math.abs(z)) * smoothstep(0.25, 0.6, Math.abs(ny));
      c.lerp(wood, stringer * 0.9);
      // subtle ageing
      c.multiplyScalar(0.97 + 0.05 * Math.abs(Math.sin(x * 21.3 + z * 9.7)));
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
    blank.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  }

  const boardMat = new THREE.MeshPhysicalMaterial({
    vertexColors: true,
    roughness: 0.46,
    metalness: 0.0,
    clearcoat: 0.32,
    clearcoatRoughness: 0.35,
    roughnessMap: speckleTex,
  });
  const board = new THREE.Mesh(blank, boardMat);
  group.add(board);

  /* ---- traction pad ------------------------------------------------- */
  const padGeo = new THREE.PlaneGeometry(1.0, 0.5, 18, 8);
  padGeo.rotateX(-Math.PI / 2);
  {
    const p = padGeo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i) - 0.6;
      const hw = Math.max(0.02, halfWidthAt(x) + 0.028 - 0.05);
      p.setX(i, x);
      p.setZ(i, p.getZ(i) * (hw / 0.25));
      p.setY(i, deckHeightAt(x) + 0.008);
    }
    p.needsUpdate = true;
    padGeo.computeVertexNormals();
  }
  const pad = new THREE.Mesh(
    padGeo,
    new THREE.MeshStandardMaterial({
      color: new THREE.Color("#2b2f36"),
      roughness: 0.95,
      metalness: 0.0,
      bumpMap: speckleTex,
      bumpScale: 0.6,
      side: THREE.DoubleSide,
    })
  );
  group.add(pad);

  // pad kick at the tail
  const kickGeo = new THREE.BoxGeometry(0.16, 0.05, 0.4);
  const kick = new THREE.Mesh(kickGeo, pad.material);
  kick.position.set(-1.04, deckHeightAt(-1.04) + 0.026, 0);
  kick.rotation.z = -0.34;
  group.add(kick);

  /* ---- fins --------------------------------------------------------- */
  const finMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color("#12515e"),
    roughness: 0.22,
    metalness: 0.05,
    clearcoat: 0.8,
  });
  const finGeo = finGeometry();
  const finSpecs = [
    { x: -1.06, z: 0, yaw: 0, cant: 0 },
    { x: -0.96, z: 0.155, yaw: 0.16, cant: -0.26 },
    { x: -0.96, z: -0.155, yaw: -0.16, cant: 0.26 },
  ];
  for (const f of finSpecs) {
    const fin = new THREE.Mesh(finGeo, finMat);
    fin.position.set(f.x, hullHeightAt(f.x) + 0.012, f.z);
    fin.rotation.y = f.yaw;
    fin.rotation.x = f.cant;
    group.add(fin);
  }

  /* ---- leash -------------------------------------------------------- */
  const plugGeo = new THREE.CylinderGeometry(0.028, 0.032, 0.03, 12);
  const plug = new THREE.Mesh(plugGeo, finMat);
  plug.position.set(-1.44, deckHeightAt(-1.44) + 0.014, 0.09);
  group.add(plug);

  const leashCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-1.44, deckHeightAt(-1.44) + 0.03, 0.09),
    new THREE.Vector3(-1.22, deckHeightAt(-1.22) - 0.02, 0.02),
    new THREE.Vector3(-0.95, deckHeightAt(-0.95) - 0.03, -0.06),
    new THREE.Vector3(-0.66, deckHeightAt(-0.66) + 0.05, -0.1),
    new THREE.Vector3(-0.47, 0.19, -0.12),
  ]);
  const leash = new THREE.Mesh(
    taperedTube(leashCurve, 30, () => 0.012, 6),
    new THREE.MeshStandardMaterial({ color: new THREE.Color("#20242a"), roughness: 0.8 })
  );
  group.add(leash);

  const cuff = new THREE.Mesh(
    new THREE.CylinderGeometry(0.045, 0.05, 0.07, 14),
    new THREE.MeshStandardMaterial({ color: new THREE.Color("#2c3138"), roughness: 0.9 })
  );
  cuff.position.set(-0.465, 0.19, -0.12);
  cuff.rotation.z = 0.22;
  group.add(cuff);

  return { group, board, deckHeightAt };
}
