import * as THREE from 'three';

// Plan outline of the surfboard (nose at +y before rotation).
function boardShape() {
  const s = new THREE.Shape();
  s.moveTo(0, -1.55); // tail
  s.quadraticCurveTo(0.42, -1.35, 0.46, -0.6);
  s.quadraticCurveTo(0.5, 0.2, 0.3, 0.9);
  s.quadraticCurveTo(0.18, 1.38, 0, 1.62); // nose tip
  s.quadraticCurveTo(-0.18, 1.38, -0.3, 0.9);
  s.quadraticCurveTo(-0.5, 0.2, -0.46, -0.6);
  s.quadraticCurveTo(-0.42, -1.35, 0, -1.55);
  return s;
}

export function createSurfboard() {
  const group = new THREE.Group();
  const deckY = 0.13; // height of the standing surface above the group origin

  const geo = new THREE.ExtrudeGeometry(boardShape(), {
    depth: 0.12,
    steps: 1,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.04,
    bevelSegments: 2,
  });
  geo.rotateX(Math.PI / 2); // plan shape -> XZ plane, nose toward +Z

  // bend in a little nose/tail rocker
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i);
    const lift =
      0.12 * Math.pow(Math.max(0, z) / 1.62, 2) +
      0.05 * Math.pow(Math.max(0, -z) / 1.55, 2);
    pos.setY(i, pos.getY(i) + lift);
  }

  const mat = new THREE.MeshStandardMaterial({
    color: '#e2574c',
    flatShading: true,
    roughness: 0.4,
  });
  const board = new THREE.Mesh(geo, mat);
  board.position.y = 0.09; // sit slightly into the waterline
  group.add(board);

  // deck stripes
  const stripeMat = new THREE.MeshStandardMaterial({
    color: '#f7ecd2',
    flatShading: true,
    roughness: 0.5,
  });
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 2.2), stripeMat);
  stripe.position.set(0, deckY + 0.005, 0.05);
  group.add(stripe);
  const stripe2 = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.02, 1.7), stripeMat);
  stripe2.position.set(0.14, deckY + 0.005, 0);
  group.add(stripe2);

  // tail fin
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.3, 0.22), mat);
  fin.position.set(0, -0.12, -1.28);
  fin.rotation.x = 0.3;
  group.add(fin);

  return { group, deckY };
}
