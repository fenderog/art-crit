import * as THREE from 'three';
import { waveHeight } from './world.js';

const TAU = Math.PI * 2;
const BASE_YAW = -0.56;

function makeFeatherGeometry(length, width, thickness = 0.018) {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(length * 0.22, width * 0.72, length * 0.7, width * 0.54, length, 0);
  shape.bezierCurveTo(length * 0.7, -width * 0.54, length * 0.22, -width * 0.72, 0, 0);

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: thickness,
    bevelEnabled: true,
    bevelThickness: thickness * 0.35,
    bevelSize: thickness * 0.25,
    bevelSegments: 1,
    curveSegments: 16
  });
  geometry.rotateX(Math.PI / 2);
  return geometry;
}

function makeWingGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0.02, 0.46);
  shape.bezierCurveTo(0.62, 0.52, 1.5, 0.40, 2.08, 0.10);
  shape.bezierCurveTo(2.25, 0.015, 2.26, -0.10, 2.11, -0.20);
  shape.bezierCurveTo(1.73, -0.38, 1.04, -0.53, 0.44, -0.55);
  shape.bezierCurveTo(0.18, -0.56, 0.01, -0.34, 0.0, -0.03);
  shape.closePath();

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.055,
    bevelEnabled: true,
    bevelThickness: 0.018,
    bevelSize: 0.024,
    bevelSegments: 2,
    curveSegments: 22
  });
  geometry.rotateX(Math.PI / 2);
  geometry.computeVertexNormals();
  return geometry;
}

function taperedTube(points, radiusStart, radiusEnd, tubularSegments = 22, radialSegments = 12) {
  const curve = new THREE.CatmullRomCurve3(points);
  const frames = curve.computeFrenetFrames(tubularSegments, false);
  const positions = [];
  const indices = [];

  for (let i = 0; i <= tubularSegments; i++) {
    const t = i / tubularSegments;
    const point = curve.getPoint(t);
    const radius = THREE.MathUtils.lerp(radiusStart, radiusEnd, t);
    const normal = frames.normals[i];
    const binormal = frames.binormals[i];

    for (let j = 0; j < radialSegments; j++) {
      const angle = (j / radialSegments) * TAU;
      const sin = Math.sin(angle);
      const cos = Math.cos(angle);
      positions.push(
        point.x + normal.x * cos * radius + binormal.x * sin * radius,
        point.y + normal.y * cos * radius + binormal.y * sin * radius,
        point.z + normal.z * cos * radius + binormal.z * sin * radius
      );
    }
  }

  for (let i = 0; i < tubularSegments; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const nextJ = (j + 1) % radialSegments;
      const a = i * radialSegments + j;
      const b = i * radialSegments + nextJ;
      const c = (i + 1) * radialSegments + j;
      const d = (i + 1) * radialSegments + nextJ;
      indices.push(a, b, c, b, d, c);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

function createRingedGeometry(sections, radialSegments, ringAt, capEnds = true) {
  const positions = [];
  const indices = [];

  for (let i = 0; i <= sections; i++) {
    const t = i / sections;
    const ring = ringAt(t);
    for (let j = 0; j < radialSegments; j++) {
      const angle = (j / radialSegments) * TAU;
      positions.push(
        ring.cx + Math.cos(angle) * ring.rx,
        ring.cy + Math.sin(angle) * ring.ry,
        ring.z
      );
    }
  }

  for (let i = 0; i < sections; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const nextJ = (j + 1) % radialSegments;
      const a = i * radialSegments + j;
      const b = i * radialSegments + nextJ;
      const c = (i + 1) * radialSegments + j;
      const d = (i + 1) * radialSegments + nextJ;
      indices.push(a, b, c, b, d, c);
    }
  }

  if (capEnds) {
    for (const [ringIndex, reverse] of [[0, true], [sections, false]]) {
      const ring = ringAt(ringIndex / sections);
      const centre = positions.length / 3;
      positions.push(ring.cx, ring.cy, ring.z);
      for (let j = 0; j < radialSegments; j++) {
        const nextJ = (j + 1) % radialSegments;
        const a = ringIndex * radialSegments + j;
        const b = ringIndex * radialSegments + nextJ;
        if (reverse) indices.push(centre, b, a);
        else indices.push(centre, a, b);
      }
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

function addCylinder(parent, start, end, radiusStart, radiusEnd, material) {
  const direction = end.clone().sub(start);
  const length = direction.length();
  const geometry = new THREE.CylinderGeometry(radiusEnd, radiusStart, length, 9, 1);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.copy(start).addScaledVector(direction, 0.5);
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.normalize()
  );
  parent.add(mesh);
  return mesh;
}

function makeFootGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, -0.12);
  shape.lineTo(-0.17, 0.15);
  shape.quadraticCurveTo(-0.23, 0.30, -0.12, 0.33);
  shape.lineTo(-0.055, 0.39);
  shape.quadraticCurveTo(0.0, 0.46, 0.055, 0.39);
  shape.lineTo(0.12, 0.33);
  shape.quadraticCurveTo(0.23, 0.30, 0.17, 0.15);
  shape.closePath();

  const geometry = new THREE.ShapeGeometry(shape, 10);
  geometry.rotateX(Math.PI / 2);
  return geometry;
}

function makeCentralStripeShape(halfWidth, start, end) {
  const shape = new THREE.Shape();
  const radius = halfWidth;
  shape.moveTo(-halfWidth, start + radius);
  shape.quadraticCurveTo(-halfWidth, start, 0, start);
  shape.quadraticCurveTo(halfWidth, start, halfWidth, start + radius);
  shape.lineTo(halfWidth, end - radius * 2.2);
  shape.quadraticCurveTo(halfWidth, end, 0, end);
  shape.quadraticCurveTo(-halfWidth, end, -halfWidth, end - radius * 2.2);
  shape.closePath();
  return shape;
}

function makeRibbon(segments, material) {
  const positionArray = new Float32Array((segments + 1) * 2 * 3);
  const indices = [];
  for (let i = 0; i < segments; i++) {
    const a = i * 2;
    const b = i * 2 + 1;
    const c = (i + 1) * 2;
    const d = (i + 1) * 2 + 1;
    indices.push(a, b, c, b, d, c);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positionArray, 3));
  geometry.setIndex(indices);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return mesh;
}

export function createPelican(scene, camera) {
  const rider = new THREE.Group();
  rider.rotation.order = 'YXZ';
  scene.add(rider);

  // ---------------------------------------------------------------- board
  const boardLength = 4.15;
  const boardWidth = 1.16;
  const halfWidth = boardWidth / 2;
  const boardShape = new THREE.Shape();
  boardShape.moveTo(0, boardLength / 2);
  boardShape.bezierCurveTo(halfWidth * 0.54, boardLength / 2, halfWidth * 0.94, boardLength / 2 - 0.52, halfWidth, boardLength / 2 - 1.15);
  boardShape.lineTo(halfWidth, -boardLength / 2 + 0.52);
  boardShape.quadraticCurveTo(halfWidth, -boardLength / 2, halfWidth * 0.68, -boardLength / 2);
  boardShape.lineTo(-halfWidth * 0.68, -boardLength / 2);
  boardShape.quadraticCurveTo(-halfWidth, -boardLength / 2, -halfWidth, -boardLength / 2 + 0.52);
  boardShape.lineTo(-halfWidth, boardLength / 2 - 1.15);
  boardShape.bezierCurveTo(-halfWidth * 0.94, boardLength / 2 - 0.52, -halfWidth * 0.54, boardLength / 2, 0, boardLength / 2);
  boardShape.closePath();

  const boardGeometry = new THREE.ExtrudeGeometry(boardShape, {
    depth: 0.14,
    bevelEnabled: true,
    bevelThickness: 0.035,
    bevelSize: 0.038,
    bevelSegments: 3,
    curveSegments: 26
  });
  boardGeometry.rotateX(Math.PI / 2);
  boardGeometry.computeBoundingBox();
  const boardTop = 0.13;
  const boardBottom = boardTop - (boardGeometry.boundingBox.max.y - boardGeometry.boundingBox.min.y);

  const boardMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xf06b52,
    roughness: 0.34,
    metalness: 0.02,
    clearcoat: 0.62,
    clearcoatRoughness: 0.34
  });
  const board = new THREE.Mesh(boardGeometry, boardMaterial);
  board.position.y = boardTop - boardGeometry.boundingBox.max.y;
  rider.add(board);

  const creamDeck = new THREE.MeshStandardMaterial({
    color: 0xf7e8c8,
    roughness: 0.55
  });
  const tealDeck = new THREE.MeshStandardMaterial({
    color: 0x145f65,
    roughness: 0.6
  });

  const wideStripe = new THREE.Mesh(
    new THREE.ShapeGeometry(makeCentralStripeShape(0.105, -1.26, 1.74), 24),
    tealDeck
  );
  wideStripe.rotation.x = Math.PI / 2;
  wideStripe.position.y = boardTop + 0.004;
  rider.add(wideStripe);

  const thinStripe = new THREE.Mesh(
    new THREE.ShapeGeometry(makeCentralStripeShape(0.048, -1.22, 1.70), 20),
    creamDeck
  );
  thinStripe.rotation.x = Math.PI / 2;
  thinStripe.position.y = boardTop + 0.009;
  rider.add(thinStripe);

  // Tail stomp pad, made from a softly rounded little slab.
  const padShape = new THREE.Shape();
  padShape.moveTo(-0.31, -1.82);
  padShape.quadraticCurveTo(-0.36, -1.82, -0.36, -1.74);
  padShape.lineTo(-0.36, -0.95);
  padShape.quadraticCurveTo(-0.36, -0.86, -0.25, -0.86);
  padShape.lineTo(0.25, -0.86);
  padShape.quadraticCurveTo(0.36, -0.86, 0.36, -0.95);
  padShape.lineTo(0.36, -1.74);
  padShape.quadraticCurveTo(0.36, -1.82, 0.31, -1.82);
  padShape.closePath();
  const pad = new THREE.Mesh(new THREE.ShapeGeometry(padShape, 8), tealDeck);
  pad.rotation.x = Math.PI / 2;
  pad.position.y = boardTop + 0.012;
  rider.add(pad);

  // A fin sits below the tail, visible through the clearest parts of the swell.
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0.58, 0);
  finShape.quadraticCurveTo(0.50, -0.39, 0.22, -0.50);
  finShape.lineTo(0, 0);
  const finGeometry = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.04,
    bevelEnabled: false
  });
  finGeometry.rotateY(Math.PI / 2);
  const fin = new THREE.Mesh(finGeometry, tealDeck);
  fin.position.set(-0.02, boardBottom + 0.13, -1.18);
  rider.add(fin);

  // -------------------------------------------------------------- pelican
  const pelicanRoot = new THREE.Group();
  pelicanRoot.position.y = boardTop + 0.003;
  rider.add(pelicanRoot);

  const cream = new THREE.MeshStandardMaterial({
    color: 0xfff0dc,
    roughness: 0.72,
    metalness: 0.0
  });
  const creamShade = new THREE.MeshStandardMaterial({
    color: 0xf1d9bc,
    roughness: 0.8,
    metalness: 0.0
  });
  const warmCream = new THREE.MeshStandardMaterial({
    color: 0xffe4c5,
    roughness: 0.78,
    metalness: 0.0
  });
  const orange = new THREE.MeshStandardMaterial({
    color: 0xf7a13b,
    roughness: 0.48,
    metalness: 0.0
  });
  const deepOrange = new THREE.MeshStandardMaterial({
    color: 0xef8731,
    roughness: 0.55,
    metalness: 0.0
  });
  const slate = new THREE.MeshStandardMaterial({
    color: 0x536a79,
    roughness: 0.8,
    metalness: 0.0,
    side: THREE.DoubleSide
  });
  const mustard = new THREE.MeshStandardMaterial({
    color: 0xe9a63d,
    roughness: 0.7,
    metalness: 0.0,
    side: THREE.DoubleSide
  });
  const yellowCrest = new THREE.MeshStandardMaterial({
    color: 0xf5d587,
    roughness: 0.72,
    metalness: 0.0,
    side: THREE.DoubleSide
  });
  const darkEye = new THREE.MeshStandardMaterial({
    color: 0x1b252b,
    roughness: 0.18,
    metalness: 0.05
  });
  const eyeLight = new THREE.MeshBasicMaterial({ color: 0xfff9ec });

  const bird = new THREE.Group();
  bird.position.y = 0.025;
  pelicanRoot.add(bird);

  // The contact shadow keeps the bird visually planted on the board.
  const contactShadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.48, 28),
    new THREE.MeshBasicMaterial({
      color: 0x153b43,
      transparent: true,
      opacity: 0.22,
      depthWrite: false
    })
  );
  contactShadow.rotation.x = -Math.PI / 2;
  contactShadow.scale.set(1.05, 0.66, 1);
  contactShadow.position.set(0, 0.006, -0.02);
  pelicanRoot.add(contactShadow);

  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 36, 26), cream);
  body.scale.set(0.51, 0.70, 0.78);
  body.position.set(0, 1.11, -0.02);
  body.rotation.x = 0.03;
  bird.add(body);

  const chest = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 22), warmCream);
  chest.scale.set(0.38, 0.52, 0.30);
  chest.position.set(0, 1.06, 0.46);
  chest.rotation.x = -0.16;
  bird.add(chest);

  const tailGroup = new THREE.Group();
  tailGroup.position.set(0, 1.02, -0.61);
  tailGroup.rotation.x = -0.18;
  bird.add(tailGroup);

  const tailBase = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), creamShade);
  tailBase.scale.set(0.33, 0.27, 0.28);
  tailBase.position.set(0, 0.02, -0.08);
  tailGroup.add(tailBase);

  const tailFeatherGeometry = makeFeatherGeometry(0.92, 0.14, 0.014);
  for (let i = 0; i < 6; i++) {
    const angle = (i - 2.5) * 0.16;
    const feather = new THREE.Mesh(tailFeatherGeometry, i > 3 ? creamShade : cream);
    feather.scale.setScalar(0.82 + (2 - Math.abs(i - 2.5)) * 0.07);
    feather.rotation.y = Math.PI / 2 + angle;
    feather.position.set((i - 2.5) * 0.055, -0.01 + Math.abs(i - 2.5) * 0.004, 0.02);
    tailGroup.add(feather);
  }

  const headPivot = new THREE.Group();
  headPivot.position.set(0, 1.58, 0.38);
  bird.add(headPivot);

  const neckPoints = [
    new THREE.Vector3(0, -0.08, -0.03),
    new THREE.Vector3(0, 0.14, 0.02),
    new THREE.Vector3(0, 0.32, 0.11),
    new THREE.Vector3(0, 0.48, 0.24),
    new THREE.Vector3(0, 0.59, 0.36)
  ];
  const neck = new THREE.Mesh(
    taperedTube(neckPoints, 0.205, 0.155, 24, 12),
    cream
  );
  headPivot.add(neck);

  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), cream);
  head.scale.set(0.315, 0.288, 0.335);
  head.position.set(0, 0.65, 0.36);
  headPivot.add(head);

  const cheek = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 16), warmCream);
  cheek.scale.set(0.22, 0.20, 0.19);
  cheek.position.set(0, 0.57, 0.48);
  headPivot.add(cheek);

  const crest = new THREE.Group();
  crest.position.set(0, 0.87, 0.16);
  headPivot.add(crest);

  const crestGeometry = new THREE.Shape();
  const crestLength = 0.54;
  const crestWidth = 0.085;
  crestGeometry.moveTo(0, 0);
  crestGeometry.bezierCurveTo(-crestWidth, crestLength * 0.26, -crestWidth * 0.85, crestLength * 0.72, crestWidth * 0.18, crestLength);
  crestGeometry.bezierCurveTo(crestWidth * 0.52, crestLength * 0.66, crestWidth * 0.52, crestLength * 0.20, 0, 0);
  const crestFeatherGeometry = new THREE.ExtrudeGeometry(crestGeometry, {
    depth: 0.012,
    bevelEnabled: true,
    bevelThickness: 0.004,
    bevelSize: 0.004,
    bevelSegments: 1,
    curveSegments: 12
  });
  crestFeatherGeometry.translate(0, 0, -0.006);

  for (let i = 0; i < 4; i++) {
    const feather = new THREE.Mesh(crestFeatherGeometry, i === 3 ? creamShade : yellowCrest);
    const scale = 0.68 + i * 0.11;
    feather.scale.set(scale, scale, 1);
    feather.position.set((i - 1.5) * 0.035, 0, (i - 1.5) * 0.018);
    feather.rotation.set(-0.58 - i * 0.075, (i - 1.5) * 0.13, (i - 1.5) * 0.15);
    crest.add(feather);
  }

  // Eyes, each on a tiny group so a blink can squash the whole eye.
  const eyes = [];
  for (const side of [-1, 1]) {
    const eyeGroup = new THREE.Group();
    eyeGroup.position.set(side * 0.246, 0.73, 0.465);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.059, 18, 14), darkEye);
    eye.scale.set(0.95, 1.08, 0.95);
    eyeGroup.add(eye);
    const catchlight = new THREE.Mesh(new THREE.SphereGeometry(0.017, 10, 8), eyeLight);
    catchlight.position.set(side * 0.008, 0.019, 0.052);
    eyeGroup.add(catchlight);
    headPivot.add(eyeGroup);
    eyes.push(eyeGroup);
  }

  // Beak group: long upper mandible, pendulous orange pouch, and tip hook.
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, 0.58, 0.52);
  headPivot.add(beakGroup);

  const upperBillGeometry = createRingedGeometry(20, 14, (t) => {
    const centerY = 0.040 - t * 0.125;
    return {
      cx: 0,
      cy: centerY,
      z: 0.015 + t * 1.43,
      rx: 0.245 * (1.0 - t * 0.76) + 0.016,
      ry: 0.077 * (1.0 - t * 0.34)
    };
  });
  const upperBill = new THREE.Mesh(upperBillGeometry, orange);
  upperBill.rotation.x = 0.06;
  beakGroup.add(upperBill);

  // A pale ridge makes the upper bill catch the sunset.
  const billRidge = new THREE.Mesh(
    new THREE.SphereGeometry(1, 18, 10),
    new THREE.MeshStandardMaterial({ color: 0xffd05c, roughness: 0.5 })
  );
  billRidge.scale.set(0.085, 0.028, 0.52);
  billRidge.position.set(0, 0.065, 0.64);
  beakGroup.add(billRidge);

  const pouchGeometry = createRingedGeometry(22, 18, (t) => {
    const profile = Math.pow(Math.sin(Math.PI * (0.075 + t * 0.915)), 0.72);
    return {
      cx: 0,
      cy: -0.035 - t * 0.16 - profile * 0.17,
      z: 0.06 + t * 1.30,
      rx: 0.025 + profile * 0.225,
      ry: 0.025 + profile * 0.205
    };
  });
  const pouch = new THREE.Mesh(pouchGeometry, deepOrange);
  pouch.rotation.x = 0.05;
  beakGroup.add(pouch);

  const beakTip = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), deepOrange);
  beakTip.scale.set(0.060, 0.065, 0.085);
  beakTip.position.set(0, -0.115, 1.43);
  beakGroup.add(beakTip);

  for (const side of [-1, 1]) {
    const nostril = new THREE.Mesh(
      new THREE.SphereGeometry(0.016, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0xb76023 })
    );
    nostril.position.set(side * 0.105, 0.078, 0.33);
    beakGroup.add(nostril);
  }

  // Wings. A negative x-scale mirrors the left wing cleanly while preserving
  // the pleasingly lopsided feather arrangement.
  const wingGeometry = makeWingGeometry();
  const primaryGeometry = makeFeatherGeometry(1.03, 0.095, 0.012);
  const wings = [];

  function buildWing(sign) {
    const wing = new THREE.Group();
    wing.position.set(sign * 0.41, 1.42, 0.035);
    wing.scale.x = sign;
    wing.userData.sign = sign;
    wing.userData.primaries = [];

    const membrane = new THREE.Mesh(wingGeometry, cream);
    membrane.material.side = THREE.DoubleSide;
    wing.add(membrane);

    const shoulder = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 16), cream);
    shoulder.scale.set(0.26, 0.29, 0.34);
    shoulder.position.set(0.02, 0.02, 0.01);
    wing.add(shoulder);

    for (let i = 0; i < 5; i++) {
      const feather = new THREE.Mesh(primaryGeometry, slate);
      feather.rotation.y = 0.44 + i * 0.185;
      feather.position.set(
        1.12 + i * 0.145,
        -0.054 - i * 0.002,
        -0.27 - i * 0.022
      );
      feather.scale.set(0.90 + i * 0.025, 0.9, 1);
      feather.userData.phase = i * 0.7 + (sign > 0 ? 0.5 : 2.1);
      wing.userData.primaries.push(feather);
      wing.add(feather);
    }

    // A few short coverts soften the transition into the dark primaries.
    for (let i = 0; i < 3; i++) {
      const covert = new THREE.Mesh(
        makeFeatherGeometry(0.5, 0.10, 0.012),
        creamShade
      );
      covert.rotation.y = 0.40 + i * 0.22;
      covert.position.set(1.05 + i * 0.16, -0.025, -0.17 - i * 0.015);
      wing.add(covert);
    }

    bird.add(wing);
    wings.push(wing);
    return wing;
  }

  buildWing(-1);
  buildWing(1);

  // Scarf: a little knot and two twisting ribbons trailing in the wind.
  const scarf = new THREE.Group();
  scarf.position.set(0, 1.66, 0.37);
  bird.add(scarf);

  const scarfRing = new THREE.Mesh(new THREE.TorusGeometry(0.215, 0.040, 8, 28), mustard);
  scarfRing.rotation.x = Math.PI / 2;
  scarfRing.scale.z = 1.03;
  scarf.add(scarfRing);

  const knot = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 12), mustard);
  knot.scale.set(1.25, 0.8, 1.1);
  knot.position.set(0.17, -0.02, -0.11);
  scarf.add(knot);

  const ribbonSegments = 22;
  const ribbons = [];
  for (let r = 0; r < 2; r++) {
    const ribbon = makeRibbon(ribbonSegments, mustard);
    ribbon.userData.side = r === 0 ? 1 : -1;
    ribbon.userData.phase = r * 2.35 + 0.7;
    scarf.add(ribbon);
    ribbons.push(ribbon);
  }

  // Legs and webbed feet.
  const legs = new THREE.Group();
  pelicanRoot.add(legs);

  const footGeometry = makeFootGeometry();
  for (const side of [-1, 1]) {
    const hip = new THREE.Vector3(side * 0.20, 0.55, 0.14);
    const knee = new THREE.Vector3(side * 0.27, 0.27, 0.24);
    const ankle = new THREE.Vector3(side * 0.28, 0.075, 0.32);
    addCylinder(legs, hip, knee, 0.053, 0.046, deepOrange);
    addCylinder(legs, knee, ankle, 0.046, 0.036, orange);

    const foot = new THREE.Mesh(footGeometry, orange);
    foot.position.set(side * 0.28, 0.038, 0.25);
    foot.rotation.y = side * 0.06;
    foot.material.side = THREE.DoubleSide;
    legs.add(foot);
  }

  // ------------------------------------------------------------- animation
  let currentTime = 0;
  let flapStartedAt = -10;
  let flapPower = 0;
  const waveNormal = new THREE.Vector3();
  const forward = new THREE.Vector3();
  const headingDirection = new THREE.Vector3();
  const right = new THREE.Vector3();
  const basis = new THREE.Matrix4();
  const boardState = {
    position: new THREE.Vector3(),
    forward: new THREE.Vector3(0, 0, 1)
  };

  function updateRibbons(time) {
    for (const ribbon of ribbons) {
      const positions = ribbon.geometry.attributes.position.array;
      const side = ribbon.userData.side;
      const phase = ribbon.userData.phase;

      for (let i = 0; i <= ribbonSegments; i++) {
        const s = i / ribbonSegments;
        const x =
          side * (0.09 + s * 0.44) +
          Math.sin(time * 4.1 + s * 5.2 + phase) * 0.15 * s +
          Math.sin(time * 2.4 + phase) * 0.055 * s;
        const y =
          1.70 +
          Math.sin(time * 3.5 + s * 4.8 + phase) * 0.16 * s -
          s * 0.30 -
          s * s * 0.08;
        const z = 0.32 - s * 1.86;

        const twist =
          side * 0.16 +
          Math.sin(time * 3.0 + s * 4.0 + phase) * 0.78 +
          s * side * 0.35;
        const halfWidth = (0.115 * (1.0 - s * 0.38));
        const wx = Math.cos(twist) * halfWidth;
        const wy = Math.sin(twist) * halfWidth;

        const index = i * 6;
        positions[index] = x - wx;
        positions[index + 1] = y - wy - 1.66;
        positions[index + 2] = z;
        positions[index + 3] = x + wx;
        positions[index + 4] = y + wy - 1.66;
        positions[index + 5] = z;
      }

      ribbon.geometry.attributes.position.needsUpdate = true;
      ribbon.geometry.computeVertexNormals();
    }
  }

  function triggerFlap(time = currentTime) {
    flapStartedAt = time;
    flapPower = 1;
  }

  function update(time, dt) {
    currentTime = time;

    // Work out the wave normal and the board's diagonal heading, then place
    // the board tangent to the moving water.
    const eps = 0.95;
    const dx =
      (waveHeight(eps, 0, time) - waveHeight(-eps, 0, time)) / (eps * 2);
    const dz =
      (waveHeight(0, eps, time) - waveHeight(0, -eps, time)) / (eps * 2);
    waveNormal.set(-dx, 1, -dz).normalize();

    const heading = BASE_YAW + Math.sin(time * 0.36) * 0.052;
    headingDirection.set(Math.sin(heading), 0, Math.cos(heading));
    forward
      .copy(headingDirection)
      .addScaledVector(waveNormal, -headingDirection.dot(waveNormal))
      .normalize();
    right.crossVectors(waveNormal, forward).normalize();
    forward.crossVectors(right, waveNormal).normalize();
    basis.makeBasis(right, waveNormal, forward);
    rider.quaternion.setFromRotationMatrix(basis);
    rider.rotateZ(Math.sin(time * 0.58) * 0.014);

    rider.position.x = 0;
    rider.position.z = 0;
    rider.position.y =
      waveHeight(0, 0, time) +
      0.015 +
      Math.sin(time * 2.0) * 0.013;

    // Subtle, continuous life.
    bird.position.y = 0.025 + Math.sin(time * 1.65) * 0.015;
    bird.rotation.z = Math.sin(time * 0.43) * 0.027 + Math.sin(time * 0.17) * 0.012;
    bird.rotation.x = 0.022 + Math.sin(time * 0.72) * 0.009;

    headPivot.rotation.y =
      Math.sin(time * 0.31) * 0.11 +
      Math.sin(time * 0.13 + 1.2) * 0.045;
    headPivot.rotation.x = -0.02 + Math.sin(time * 0.83) * 0.022;
    headPivot.rotation.z = Math.sin(time * 0.47) * 0.017;

    crest.rotation.z = Math.sin(time * 1.7) * 0.022;
    crest.rotation.x = Math.sin(time * 1.13) * 0.016;

    beakGroup.rotation.y = Math.sin(time * 0.24 + 0.8) * 0.018;
    pouch.scale.y = 1.0 + Math.sin(time * 2.25 + 0.7) * 0.035;
    pouch.rotation.z = Math.sin(time * 1.4 + 0.2) * 0.009;

    const blinkCycle = (time + 1.1) % 5.7;
    const blinkScale =
      blinkCycle < 0.19
        ? 1.0 - Math.sin((blinkCycle / 0.19) * Math.PI) * 0.86
        : 1.0;
    for (const eye of eyes) eye.scale.y = blinkScale;

    if (flapPower > 0) {
      const since = time - flapStartedAt;
      if (since > 1.9) {
        flapPower = 0;
      }
    }
    const sinceFlap = time - flapStartedAt;
    const flapWave =
      flapPower > 0 && sinceFlap >= 0
        ? Math.sin(sinceFlap * 12.0) * Math.exp(-sinceFlap * 1.9) * 0.42 * flapPower
        : 0;

    const idleFlutter = Math.sin(time * 1.25) * 0.028 + Math.sin(time * 2.3 + 1.4) * 0.009;
    for (const wing of wings) {
      const sign = wing.userData.sign;
      const phase = sign > 0 ? 0.25 : 1.05;
      const lift =
        0.33 +
        idleFlutter +
        Math.sin(time * 0.61 + phase) * 0.014 +
        flapWave;
      wing.rotation.z = sign * lift;
      wing.rotation.y = sign * Math.sin(time * 0.4 + phase) * 0.018;
      for (const feather of wing.userData.primaries) {
        feather.rotation.z =
          Math.sin(time * 2.15 + feather.userData.phase) * 0.018 +
          flapWave * 0.16;
      }
    }

    tailGroup.rotation.x =
      -0.18 + Math.sin(time * 1.1 + 0.4) * 0.024;
    tailGroup.rotation.y = Math.sin(time * 0.52) * 0.035;

    updateRibbons(time);

    // Board state for the ocean foam and for camera framing.
    boardState.position.copy(rider.position);
    boardState.forward.copy(forward);

    return boardState;
  }

  function getBoardForward() {
    return forward;
  }

  return {
    rider,
    pelicanRoot,
    board,
    update,
    triggerFlap,
    getBoardForward,
    boardState,
    currentTime: () => currentTime
  };
}
