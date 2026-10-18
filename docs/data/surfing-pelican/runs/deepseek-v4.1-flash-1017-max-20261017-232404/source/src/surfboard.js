import * as THREE from 'three';
import { makeHibiscusTexture, makeShadowTexture } from './utils.js';

function roundedStrip(length, width, radius = 0.12) {
  const shape = new THREE.Shape();
  const hx = length * 0.5;
  const hy = width * 0.5;
  shape.moveTo(-hx + radius, -hy);
  shape.lineTo(hx - radius, -hy);
  shape.quadraticCurveTo(hx, -hy, hx, -hy + radius);
  shape.lineTo(hx, hy - radius);
  shape.quadraticCurveTo(hx, hy, hx - radius, hy);
  shape.lineTo(-hx + radius, hy);
  shape.quadraticCurveTo(-hx, hy, -hx, hy - radius);
  shape.lineTo(-hx, -hy + radius);
  shape.quadraticCurveTo(-hx, -hy, -hx + radius, -hy);
  shape.closePath();
  return shape;
}

function flatShape(shape, material, y, segments = 24) {
  const geometry = new THREE.ShapeGeometry(shape, segments);
  geometry.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.y = y;
  return mesh;
}

export function createSurfboard() {
  const group = new THREE.Group();
  group.name = 'surfboard';

  const boardMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xf66d50,
    roughness: 0.32,
    metalness: 0.0,
    clearcoat: 1.0,
    clearcoatRoughness: 0.16,
    envMapIntensity: 1.15
  });

  const creamMaterial = new THREE.MeshStandardMaterial({
    color: 0xffe8c9,
    roughness: 0.38,
    metalness: 0.0
  });

  const tealMaterial = new THREE.MeshStandardMaterial({
    color: 0x126f72,
    roughness: 0.36,
    metalness: 0.02
  });

  const shape = new THREE.Shape();
  shape.moveTo(-1.7, 0);
  shape.bezierCurveTo(-1.7, 0.2, -1.38, 0.39, -0.74, 0.47);
  shape.bezierCurveTo(0.0, 0.54, 1.15, 0.45, 1.55, 0.22);
  shape.bezierCurveTo(1.68, 0.13, 1.68, -0.13, 1.55, -0.22);
  shape.bezierCurveTo(1.15, -0.45, 0.0, -0.54, -0.74, -0.47);
  shape.bezierCurveTo(-1.38, -0.39, -1.7, -0.2, -1.7, 0);

  const boardGeometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.12,
    bevelEnabled: true,
    bevelSegments: 4,
    bevelSize: 0.04,
    bevelThickness: 0.04,
    curveSegments: 52,
    steps: 1
  });
  boardGeometry.center();
  boardGeometry.rotateX(-Math.PI / 2);
  boardGeometry.computeBoundingBox();

  const deckY = boardGeometry.boundingBox.max.y;

  const board = new THREE.Mesh(boardGeometry, boardMaterial);
  board.castShadow = true;
  board.receiveShadow = true;
  group.add(board);

  // Long cream racing stripe.
  const stripe = flatShape(roundedStrip(2.75, 0.31, 0.14), creamMaterial, deckY + 0.0025);
  stripe.position.x = -0.02;
  group.add(stripe);

  // Teal pinstripes bordering the stripe.
  for (const z of [-0.176, 0.176]) {
    const pin = flatShape(roundedStrip(2.72, 0.018, 0.008), tealMaterial, deckY + 0.0035);
    pin.position.x = -0.02;
    pin.position.z = z;
    group.add(pin);
  }

  // Tropical flower inlay near the nose.
  const flowerTexture = makeHibiscusTexture(512);
  const flowerMaterial = new THREE.MeshStandardMaterial({
    map: flowerTexture,
    transparent: true,
    roughness: 0.42,
    metalness: 0.0,
    depthWrite: false,
    polygonOffset: true,
    polygonOffsetFactor: -1,
    polygonOffsetUnits: -1
  });
  const flower = new THREE.Mesh(new THREE.PlaneGeometry(0.58, 0.58), flowerMaterial);
  flower.rotation.x = -Math.PI / 2;
  flower.position.set(-1.04, deckY + 0.006, 0.235);
  group.add(flower);

  // Dark traction pad at the tail.
  const padMaterial = new THREE.MeshStandardMaterial({
    color: 0x173f45,
    roughness: 0.82,
    metalness: 0.0
  });
  const pad = flatShape(roundedStrip(0.48, 0.34, 0.13), padMaterial, deckY + 0.0055);
  pad.position.x = 1.17;
  group.add(pad);

  // Three raised grip ridges on the pad.
  for (let i = 0; i < 3; i++) {
    const ridge = new THREE.Mesh(
      new THREE.BoxGeometry(0.34, 0.009, 0.014),
      new THREE.MeshStandardMaterial({ color: 0x2a5c60, roughness: 0.75 })
    );
    ridge.position.set(1.17, deckY + 0.012, -0.09 + i * 0.09);
    group.add(ridge);
  }

  // A softly swept centre fin under the tail.
  const finShape = new THREE.Shape();
  finShape.moveTo(-0.27, 0.01);
  finShape.quadraticCurveTo(-0.05, -0.22, 0.2, -0.6);
  finShape.quadraticCurveTo(0.22, -0.28, 0.31, -0.02);
  finShape.closePath();
  const finGeometry = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.045,
    bevelEnabled: true,
    bevelSize: 0.012,
    bevelThickness: 0.012,
    bevelSegments: 2,
    curveSegments: 16
  });
  finGeometry.translate(0, 0, -0.0225);
  const fin = new THREE.Mesh(finGeometry, tealMaterial);
  fin.position.set(1.14, boardGeometry.boundingBox.min.y + 0.02, 0);
  fin.castShadow = true;
  group.add(fin);

  // A soft contact shadow under the bird helps it sit on the deck.
  const shadowTexture = makeShadowTexture(256);
  const contactShadow = new THREE.Mesh(
    new THREE.PlaneGeometry(1.55, 0.92),
    new THREE.MeshBasicMaterial({
      map: shadowTexture,
      transparent: true,
      opacity: 0.58,
      depthWrite: false
    })
  );
  contactShadow.rotation.x = -Math.PI / 2;
  contactShadow.position.set(0.1, deckY + 0.008, 0);
  group.add(contactShadow);

  return {
    group,
    board,
    deckY,
    materials: { boardMaterial, creamMaterial, tealMaterial }
  };
}
