import * as THREE from "three";
import { waveHeight } from "./ocean.js";
import { createPelican } from "./pelican.js";

const BOARD_HALF_LENGTH = 1.55;
const BOARD_HALF_WIDTH = 0.24;
const BOARD_COLOR = 0xf7f3ea;
const STRIPE_COLOR = 0xe8553a;

// Surfboard outline: pointed nose, squashed tail, widest a little behind centre.
function halfWidthAt(u) {
  // u runs from -1 (tail) to +1 (nose)
  return BOARD_HALF_WIDTH * Math.pow(1 - u * u, 0.6) * (1 - 0.1 * u);
}

function createBoard() {
  const steps = 48;
  const points = [];
  for (let i = 0; i <= steps; i++) {
    const u = -1 + (2 * i) / steps;
    points.push(new THREE.Vector2(u * BOARD_HALF_LENGTH, halfWidthAt(u)));
  }
  for (let i = steps - 1; i >= 1; i--) {
    const u = -1 + (2 * i) / steps;
    points.push(new THREE.Vector2(u * BOARD_HALF_LENGTH, -halfWidthAt(u)));
  }

  const geometry = new THREE.ExtrudeGeometry(new THREE.Shape(points), {
    depth: 0.09,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 4,
    curveSegments: 1,
  });
  geometry.computeBoundingBox();
  const { min, max } = geometry.boundingBox;
  const deckY = (max.z - min.z) / 2;
  geometry.translate(0, 0, -(min.z + max.z) / 2);
  // Outline (x, y) stays flat; extrusion depth becomes height.
  geometry.rotateX(-Math.PI / 2);

  const group = new THREE.Group();
  group.add(
    new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ color: BOARD_COLOR, roughness: 0.35 }),
    ),
  );

  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.4, 0.004, 0.05),
    new THREE.MeshStandardMaterial({ color: STRIPE_COLOR, roughness: 0.4 }),
  );
  stripe.position.y = deckY + 0.001;
  group.add(stripe);

  // Swept-back fin under the tail.
  const finShape = new THREE.Shape([
    new THREE.Vector2(0.12, 0.02),
    new THREE.Vector2(-0.22, 0.02),
    new THREE.Vector2(-0.1, -0.24),
  ]);
  const finGeometry = new THREE.ExtrudeGeometry(finShape, { depth: 0.025, bevelEnabled: false });
  finGeometry.translate(0, 0, -0.0125);
  const fin = new THREE.Mesh(
    finGeometry,
    new THREE.MeshStandardMaterial({ color: STRIPE_COLOR, roughness: 0.4 }),
  );
  fin.position.set(-1.1, -deckY, 0);
  group.add(fin);

  return { group, deckY };
}

// Surfer rides the face of the wave: the board sits on the surface at the origin,
// pitching and rolling to match the slope under it while the swell rolls past.
export function createSurfer() {
  const root = new THREE.Group();
  const board = createBoard();
  const pelican = createPelican();
  pelican.group.position.y = board.deckY;
  root.add(board.group, pelican.group);

  const sampleX = BOARD_HALF_LENGTH * 0.8;
  const sampleZ = BOARD_HALF_WIDTH * 0.8;

  function update(t) {
    const nose = waveHeight(sampleX, 0, t);
    const tail = waveHeight(-sampleX, 0, t);
    const starboard = waveHeight(0, sampleZ, t);
    const port = waveHeight(0, -sampleZ, t);

    const pitch = Math.atan2(nose - tail, 2 * sampleX);
    const roll = Math.atan2(starboard - port, 2 * sampleZ);

    root.position.y = waveHeight(0, 0, t) - 0.02;
    root.rotation.set(-roll, 0, pitch);

    pelican.update(t);
  }

  return { root, update };
}
