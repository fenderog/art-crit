import * as THREE from "three";
import { swell } from "./ocean.js";

const NOSE_X = 1.3;
const TAIL_X = -1.3;
const WIDEST_X = -0.15;
const HALF_WIDTH = 0.27;
const TAIL_HALF_WIDTH = 0.1;
const FIN_X = -0.95;
const DECK_ABOVE_SWELL = 0.1; // deck height above the swell line when the board is at rest
const EPS = 0.02;

const UP = new THREE.Vector3(0, 1, 0);
const X_AXIS = new THREE.Vector3(1, 0, 0);
const normal = new THREE.Vector3();
const forward = new THREE.Vector3();
const side = new THREE.Vector3();
const basis = new THREE.Matrix4();
const yaw = new THREE.Quaternion();
const roll = new THREE.Quaternion();

// Half-width of the outline at x: a rounded nose and a squarish tail.
function halfWidth(x) {
  if (x >= WIDEST_X) {
    const t = (x - WIDEST_X) / (NOSE_X - WIDEST_X);
    return HALF_WIDTH * Math.pow(1 - Math.pow(t, 2.4), 0.55);
  }
  const t = (WIDEST_X - x) / (WIDEST_X - TAIL_X);
  return TAIL_HALF_WIDTH + (HALF_WIDTH - TAIL_HALF_WIDTH) * Math.pow(1 - Math.pow(t, 3), 0.4);
}

// Outline in the XY plane (x along the length, y across the width).
function outlineShape(steps = 80) {
  const xAt = (i) => TAIL_X + ((NOSE_X - TAIL_X) * i) / steps;
  const points = [];
  for (let i = 0; i <= steps; i++) points.push(new THREE.Vector2(xAt(i), -halfWidth(xAt(i))));
  for (let i = steps - 1; i >= 0; i--) points.push(new THREE.Vector2(xAt(i), halfWidth(xAt(i))));
  return new THREE.Shape(points);
}

export function createSurfboard() {
  const board = new THREE.Group();

  const deckGeometry = new THREE.ExtrudeGeometry(outlineShape(), {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 3,
    curveSegments: 8,
  });
  deckGeometry.rotateX(Math.PI / 2); // length along x, width along z, thickness down y
  deckGeometry.computeBoundingBox();
  deckGeometry.translate(0, -deckGeometry.boundingBox.max.y, 0); // deck top at y = 0

  const finGeometry = new THREE.ExtrudeGeometry(
    new THREE.Shape([new THREE.Vector2(-0.14, -0.06), new THREE.Vector2(0.12, -0.06), new THREE.Vector2(0, -0.27)]),
    { depth: 0.025, bevelEnabled: false }
  );
  finGeometry.translate(0, 0, -0.0125);

  const deck = new THREE.Mesh(deckGeometry, new THREE.MeshStandardMaterial({ color: 0xff6f4a, roughness: 0.4 }));
  const fin = new THREE.Mesh(finGeometry, new THREE.MeshStandardMaterial({ color: 0x2b3a48, roughness: 0.4 }));
  fin.position.x = FIN_X;

  board.add(deck, fin);
  return board;
}

// Lays the board on the swell at x = z = 0, with a little carving yaw and roll on top.
export function poseSurfboard(board, t) {
  const slopeX = (swell(EPS, 0) - swell(-EPS, 0)) / (2 * EPS);
  const slopeZ = (swell(0, EPS) - swell(0, -EPS)) / (2 * EPS);
  normal.set(-slopeX, 1, -slopeZ).normalize();
  forward.copy(X_AXIS).addScaledVector(normal, -normal.x).normalize();
  side.crossVectors(forward, normal);
  board.quaternion.setFromRotationMatrix(basis.makeBasis(forward, normal, side));
  board.quaternion.multiply(yaw.setFromAxisAngle(UP, 0.07 * Math.sin(0.6 * t)));
  board.quaternion.multiply(roll.setFromAxisAngle(X_AXIS, 0.05 * Math.sin(1.1 * t + 1)));
  board.position.set(0, swell(0, 0) + DECK_ABOVE_SWELL + 0.03 * Math.sin(1.3 * t), 0);
}
