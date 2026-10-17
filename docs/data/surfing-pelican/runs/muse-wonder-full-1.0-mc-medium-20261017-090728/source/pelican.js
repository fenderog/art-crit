import * as THREE from "three";

const white = new THREE.MeshStandardMaterial({ color: 0xf7f1e3, roughness: 0.85 });
const cream = new THREE.MeshStandardMaterial({ color: 0xefe3c8, roughness: 0.9 });
const darkTip = new THREE.MeshStandardMaterial({ color: 0x2b2f36, roughness: 0.85 });
const orange = new THREE.MeshStandardMaterial({ color: 0xf08a1d, roughness: 0.6 });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xf6a04d, roughness: 0.75 });
const black = new THREE.MeshStandardMaterial({ color: 0x14181d, roughness: 0.35 });

function ball(mat, sx, sy, sz, x, y, z) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), mat);
  m.scale.set(sx, sy, sz);
  m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}

function boardTexture() {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 512;
  const g = c.getContext("2d");
  g.fillStyle = "#ffd23e"; g.fillRect(0, 0, 256, 512);
  g.fillStyle = "#0ea5a4"; g.fillRect(0, 70, 256, 372);
  g.fillStyle = "#ff6b35"; g.fillRect(0, 150, 256, 34); g.fillRect(0, 330, 256, 34);
  g.fillStyle = "#fff7e6"; g.fillRect(108, 0, 40, 512);
  g.fillStyle = "#0b7285";
  g.beginPath(); g.arc(128, 256, 34, 0, Math.PI * 2); g.fill();
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

export function createSurfboard() {
  const group = new THREE.Group();
  // Pointed-oval outline in the XZ plane, nose toward +Z.
  const shape = new THREE.Shape();
  shape.moveTo(0, 2.15);
  shape.bezierCurveTo(0.62, 1.5, 0.72, 0.4, 0.72, -0.6);
  shape.bezierCurveTo(0.72, -1.4, 0.42, -1.95, 0, -2.05);
  shape.bezierCurveTo(-0.42, -1.95, -0.72, -1.4, -0.72, -0.6);
  shape.bezierCurveTo(-0.72, 0.4, -0.62, 1.5, 0, 2.15);

  const baseGeo = new THREE.ExtrudeGeometry(shape, { depth: 0.1, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.05, bevelSegments: 2 });
  baseGeo.rotateX(-Math.PI / 2);
  const base = new THREE.Mesh(baseGeo, new THREE.MeshStandardMaterial({ color: 0xfff7e6, roughness: 0.45 }));
  base.position.y = 0.08;
  base.castShadow = true;
  group.add(base);

  const topGeo = new THREE.ShapeGeometry(shape);
  topGeo.rotateX(-Math.PI / 2);
  // Remap UVs from board outline bounds so the stripe texture fits the deck.
  const p = topGeo.attributes.position;
  const uv = topGeo.attributes.uv;
  for (let i = 0; i < p.count; i++) uv.setXY(i, (p.getX(i) + 0.75) / 1.5, (p.getZ(i) + 2.1) / 4.3);
  const top = new THREE.Mesh(topGeo, new THREE.MeshStandardMaterial({ map: boardTexture(), roughness: 0.5, side: THREE.DoubleSide }));
  top.position.y = 0.245;
  group.add(top);

  // Fin underneath, toward the tail.
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.32, 0.42), new THREE.MeshStandardMaterial({ color: 0xff6b35, roughness: 0.5 }));
  fin.position.set(0, -0.1, -1.55);
  group.add(fin);
  return group;
}

function createWing(side) {
  // side: +1 extends toward board nose (+Z), -1 toward tail.
  const pivot = new THREE.Group();
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0.5, 0.32, 1.25, 0.34, 1.9, 0.05);
  shape.bezierCurveTo(1.3, -0.18, 0.55, -0.26, 0, -0.14);
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.07, bevelEnabled: false });
  geo.rotateX(-Math.PI / 2); // lay the wing flat in the horizontal plane
  const wing = new THREE.Mesh(geo, white);
  wing.castShadow = true;
  pivot.add(wing);
  // Dark flight-feather tips.
  for (let i = 0; i < 3; i++) {
    const f = ball(darkTip, 0.34, 0.045, 0.09, 1.72 + i * 0.08, 0.02 - i * 0.07, 0.035);
    f.rotation.y = 0.25 - i * 0.18;
    pivot.add(f);
  }
  // Orient: wing shape runs along +X locally; swing it out along ±Z, held up for balance.
  pivot.rotation.y = side > 0 ? -Math.PI / 2 : Math.PI / 2;
  return pivot;
}

function createFoot(x, z, yaw) {
  const g = new THREE.Group();
  const foot = ball(orange, 0.3, 0.055, 0.2, 0.1, 0, 0);
  g.add(foot);
  for (let i = -1; i <= 1; i++) {
    const toe = ball(orange, 0.14, 0.04, 0.07, 0.34, 0, i * 0.11);
    g.add(toe);
  }
  g.position.set(x, 0.27, z);
  g.rotation.y = yaw;
  return g;
}

/**
 * Returns { group, parts } — a pelican in a sideways surf stance.
 * Local axes: board nose +Z, beak faces +X, feet spread along Z, wings along ±Z.
 */
export function createPelican() {
  const group = new THREE.Group();

  // Legs and webbed feet planted front/back on the board.
  for (const z of [0.62, -0.62]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.09, 0.62, 10), orange);
    leg.position.set(0, 0.52, z * 0.82);
    leg.rotation.x = z > 0 ? -0.28 : 0.28;
    leg.castShadow = true;
    group.add(leg);
    group.add(createFoot(0, z, 0));
  }

  // Body, tilted slightly forward over the board.
  const body = new THREE.Group();
  body.position.set(-0.1, 1.28, 0);
  body.add(ball(white, 0.92, 0.72, 0.62, 0, 0, 0));
  body.add(ball(cream, 0.55, 0.5, 0.48, 0.52, -0.18, 0)); // chest
  group.add(body);

  // Tail feathers fanning behind (-X).
  const tail = new THREE.Group();
  tail.position.set(-0.88, 1.36, 0);
  for (let i = -1; i <= 1; i++) {
    const f = ball(i === 0 ? cream : white, 0.42, 0.07, 0.14, -0.3, 0, i * 0.15);
    f.rotation.y = i * 0.25;
    tail.add(f);
  }
  group.add(tail);

  // S-curved neck with head, built as one pivoting group for bobbing.
  const neck = new THREE.Group();
  neck.position.set(0.62, 1.55, 0);
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0.28, 0.3, 0),
    new THREE.Vector3(0.18, 0.68, 0),
    new THREE.Vector3(0.42, 0.98, 0),
  ]);
  const neckMesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 16, 0.17, 10), white);
  neckMesh.castShadow = true;
  neck.add(neckMesh);

  const head = new THREE.Group();
  head.position.set(0.5, 1.06, 0);
  head.add(ball(white, 0.34, 0.3, 0.27, 0, 0, 0));
  // Shaggy crest at the back of the head.
  for (let i = 0; i < 3; i++) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.3, 6), cream);
    crest.position.set(-0.24, 0.14 - i * 0.04, (i - 1) * 0.08);
    crest.rotation.z = 1.15;
    head.add(crest);
  }
  // Eyes.
  for (const s of [1, -1]) {
    head.add(ball(black, 0.045, 0.045, 0.045, 0.22, 0.1, s * 0.2));
    head.add(ball(new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.016, 0.016, 0.016, 0.25, 0.13, s * 0.225));
  }
  // Long upper beak with hooked tip, plus the hanging pouch beneath.
  const beak = new THREE.Group();
  beak.position.set(0.26, -0.02, 0);
  const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.11, 1.35, 10), orange);
  upper.rotation.z = Math.PI / 2 + 0.06;
  upper.position.x = 0.66;
  upper.scale.z = 0.55;
  upper.castShadow = true;
  beak.add(upper);
  const hook = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.18, 8), orange);
  hook.position.set(1.34, -0.1, 0);
  hook.rotation.x = Math.PI;
  beak.add(hook);
  const pouch = ball(pouchMat, 0.5, 0.17, 0.13, 0.55, -0.19, 0);
  beak.add(pouch);
  head.add(beak);
  neck.add(head);
  group.add(neck);

  // Wings held wide like a surfer's arms.
  const wingFront = createWing(1);
  wingFront.position.set(-0.12, 1.62, 0.5);
  group.add(wingFront);
  const wingBack = createWing(-1);
  wingBack.position.set(-0.12, 1.62, -0.5);
  group.add(wingBack);

  return { group, parts: { body, tail, neck, head, pouch, wingFront, wingBack } };
}
