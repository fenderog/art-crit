/**
 * The surfing pelican: a stylised bird built from primitives riding a
 * surfboard. The whole rig is driven by the shared wave field so it floats
 * and tilts on the moving water surface.
 */
import * as THREE from "three";
import { waveHeight, waveNormal } from "./waves.js";
import { softCircleTexture, foamTexture } from "./textures.js";

const BOARD_HALF_LENGTH = 1.95;
const BOARD_HALF_WIDTH = 0.62;
const BOARD_TOP = 0.17;
const PELICAN_SCALE = 0.62;
const FOOT_Y = -1.15; // in pelican local space

// ---------------------------------------------------------------- materials
function materials() {
  return {
    body: new THREE.MeshStandardMaterial({ color: 0xf7f2e8, roughness: 0.78, metalness: 0.0 }),
    bodyShade: new THREE.MeshStandardMaterial({ color: 0xe6e2d6, roughness: 0.82, metalness: 0.0 }),
    wing: new THREE.MeshStandardMaterial({ color: 0xece7db, roughness: 0.82, metalness: 0.0 }),
    wingTip: new THREE.MeshStandardMaterial({ color: 0xb9c2ca, roughness: 0.85, metalness: 0.0 }),
    beak: new THREE.MeshStandardMaterial({ color: 0xf2a83f, roughness: 0.46, metalness: 0.03 }),
    pouch: new THREE.MeshStandardMaterial({ color: 0xe07f27, roughness: 0.52, metalness: 0.02 }),
    leg: new THREE.MeshStandardMaterial({ color: 0xe58a2c, roughness: 0.55, metalness: 0.02 }),
    eye: new THREE.MeshStandardMaterial({ color: 0x191c24, roughness: 0.18, metalness: 0.12 }),
    glint: new THREE.MeshBasicMaterial({ color: 0xffffff }),
    board: new THREE.MeshStandardMaterial({ color: 0xe2563f, roughness: 0.36, metalness: 0.05 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xfbeed6, roughness: 0.42, metalness: 0.04 }),
    fin: new THREE.MeshStandardMaterial({ color: 0x1f6f83, roughness: 0.45, metalness: 0.05 }),
  };
}

// ------------------------------------------------------------------- surfboard
function createBoard(mats) {
  const group = new THREE.Group();

  const shape = new THREE.Shape();
  const L = BOARD_HALF_LENGTH;
  const W = BOARD_HALF_WIDTH;
  shape.moveTo(0, L);
  shape.bezierCurveTo(W * 0.5, L * 0.74, W, L * 0.26, W, 0.05);
  shape.bezierCurveTo(W, -L * 0.5, W * 0.66, -L * 0.94, 0, -L);
  shape.bezierCurveTo(-W * 0.66, -L * 0.94, -W, -L * 0.5, -W, 0.05);
  shape.bezierCurveTo(-W, L * 0.26, -W * 0.5, L * 0.74, 0, L);

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.13,
    bevelSize: 0.12,
    bevelSegments: 5,
    curveSegments: 30,
  });
  geometry.rotateX(Math.PI / 2); // nose points toward +Z
  geometry.computeBoundingBox();
  geometry.translate(
    0,
    -(geometry.boundingBox.min.y + geometry.boundingBox.max.y) / 2,
    0
  );

  const board = new THREE.Mesh(geometry, mats.board);
  group.add(board);

  // deck stripe + tail pad
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.035, 2.5), mats.stripe);
  stripe.position.set(0, BOARD_TOP + 0.012, 0.18);
  group.add(stripe);

  const pad = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.035, 0.66), mats.stripe);
  pad.position.set(0, BOARD_TOP + 0.012, -1.12);
  group.add(pad);

  // fin under the tail
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.34, 0.52), mats.fin);
  fin.position.set(0, -0.2, -1.28);
  fin.rotation.x = -0.22;
  group.add(fin);

  return group;
}

// --------------------------------------------------------------------- pelican

/** Swept wing silhouette: +x points outward, +y points forward. */
function wingGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0.72);
  shape.bezierCurveTo(1.0, 0.62, 1.85, 0.15, 2.35, -1.35);
  shape.bezierCurveTo(2.2, -1.85, 1.3, -1.8, 0.5, -1.2);
  shape.bezierCurveTo(0.18, -0.9, -0.1, -0.1, 0, 0.72);
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.11,
    bevelEnabled: true,
    bevelThickness: 0.08,
    bevelSize: 0.11,
    bevelSegments: 3,
    curveSegments: 18,
  });
  geometry.rotateX(Math.PI / 2); // wing plane becomes horizontal
  return geometry;
}

function createPelican(mats) {
  const pelican = new THREE.Group();

  // ---- body ---------------------------------------------------------------
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), mats.body);
  body.position.set(0, 0.3, 0);
  body.scale.set(1.02, 0.96, 1.52);
  pelican.add(body);

  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.86, 28, 20), mats.body);
  chest.position.set(0, 0.16, 0.72);
  chest.scale.set(1, 0.94, 1);
  pelican.add(chest);

  const tail = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 16), mats.bodyShade);
  tail.position.set(0, 0.52, -1.62);
  tail.scale.set(0.5, 0.14, 0.95);
  tail.rotation.x = 0.42;
  pelican.add(tail);

  // ---- neck ---------------------------------------------------------------
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.78, 0.95),
    new THREE.Vector3(0, 1.55, 0.72),
    new THREE.Vector3(0, 2.28, 0.98),
    new THREE.Vector3(0, 2.66, 1.38),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 30, 0.32, 14, false), mats.body);
  pelican.add(neck);

  // ---- head (rotates as one unit) ----------------------------------------
  const head = new THREE.Group();
  head.position.set(0, 2.86, 1.5);
  pelican.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.5, 30, 22), mats.body);
  skull.scale.set(0.92, 1.0, 1.12);
  head.add(skull);

  // upper mandible: long, slim, very slightly drooping at the tip
  const mandible = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.125, 1.78, 14), mats.beak);
  mandible.geometry.rotateX(Math.PI / 2);
  mandible.position.set(0, 0.02, 1.3);
  mandible.rotation.x = -0.09;
  head.add(mandible);

  const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.055, 1.3), mats.beak);
  ridge.position.set(0, 0.12, 1.18);
  ridge.rotation.x = -0.16;
  head.add(ridge);

  // the pouch: a soft sac hanging under the base of the beak
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 26, 20), mats.pouch);
  pouch.position.set(0, -0.28, 0.68);
  pouch.scale.set(0.27, 0.37, 0.62);
  pouch.rotation.x = 0.2;
  head.add(pouch);

  // eyes
  const eyes = [];
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.098, 16, 12), mats.eye);
    eye.position.set(side * 0.3, 0.2, 0.4);
    head.add(eye);
    eyes.push(eye);

    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.033, 10, 8), mats.glint);
    glint.position.set(side * 0.335, 0.235, 0.475);
    head.add(glint);
  }

  // swept-back crest feathers
  for (let i = 0; i < 3; i++) {
    const feather = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.5, 8), mats.bodyShade);
    feather.position.set((i - 1) * 0.12, 0.28 - i * 0.03, -0.42);
    feather.rotation.x = -1.95;
    feather.rotation.z = (i - 1) * 0.25;
    feather.scale.set(1, 1, 0.32);
    head.add(feather);
  }

  // ---- wings --------------------------------------------------------------
  // ---- wings --------------------------------------------------------------
  const wingGeo = wingGeometry();
  const wings = [];
  for (const side of [-1, 1]) {
    const shoulder = new THREE.Group();
    shoulder.position.set(side * 0.68, 0.62, 0.16);
    pelican.add(shoulder);

    const wing = new THREE.Mesh(wingGeo, mats.wing);
    wing.scale.x = side; // mirror the silhouette for the other side
    shoulder.add(wing);

    // primaries fan out at the wing tip and lag slightly behind the flap
    const outer = new THREE.Group();
    outer.position.set(side * 1.62, -0.04, -1.02);
    shoulder.add(outer);

    for (let f = 0; f < 3; f++) {
      const feather = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), mats.wingTip);
      feather.position.set(side * (0.18 + f * 0.36), -0.05 - f * 0.03, -0.12 - f * 0.34);
      feather.scale.set(0.48, 0.065, 0.9 - f * 0.12);
      feather.rotation.y = side * -0.42;
      outer.add(feather);
    }

    wings.push({ shoulder, outer, side });
  }

  // ---- legs and webbed feet ------------------------------------------------
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.115, 0.1, 0.5, 12), mats.leg);
    leg.position.set(side * 0.36, -0.88, 0.1);
    leg.rotation.z = side * 0.16;
    pelican.add(leg);

    const foot = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), mats.leg);
    foot.position.set(side * 0.44, FOOT_Y + 0.04, 0.3);
    foot.scale.set(0.23, 0.055, 0.38);
    foot.rotation.y = side * 0.22;
    pelican.add(foot);
  }

  return { group: pelican, head, eyes, wings, pouch };
}

// ------------------------------------------------------------------ the rig
export function createSurfRig(scene) {
  const mats = materials();
  const group = new THREE.Group();
  scene.add(group);

  const board = createBoard(mats);
  group.add(board);

  const pelican = createPelican(mats);
  pelican.group.scale.setScalar(PELICAN_SCALE);
  pelican.group.position.y = BOARD_TOP - FOOT_Y * PELICAN_SCALE;
  pelican.group.rotation.x = -0.07;
  group.add(pelican.group);

  // soft contact shadow and foam collar on the water surface
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({
    map: softCircleTexture(128),
    color: 0x0d2c4c,
    transparent: true,
    opacity: 0.3,
    depthWrite: false,
  }));
  shadow.geometry.rotateX(-Math.PI / 2);
  shadow.position.y = -0.2;
  shadow.scale.set(2.3, 1, 4.9);
  shadow.renderOrder = 1;
  group.add(shadow);

  const foamMap = foamTexture(256, 110);
  const collar = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({
    map: foamMap,
    color: 0xf2fbff,
    transparent: true,
    opacity: 0.5,
    depthWrite: false,
  }));
  collar.geometry.rotateX(-Math.PI / 2);
  collar.position.y = -0.12;
  collar.scale.set(1.75, 1, 4.2);
  collar.renderOrder = 2;
  group.add(collar);

  const normal = new THREE.Vector3();
  const noseWorld = new THREE.Vector3();

  return {
    group,
    pelican,
    /** World position of the board nose, used to spawn spray. */
    nosePosition(target = noseWorld) {
      return target.set(0, 0, BOARD_HALF_LENGTH * 0.92).applyMatrix4(group.matrixWorld);
    },
    update(t, dt) {
      // ride the surface
      const h = waveHeight(0, 0, t);
      waveNormal(0, 0, t, normal);
      group.position.set(0, h + 0.28, 0);
      group.rotation.order = "YXZ";
      group.rotation.set(Math.asin(normal.z), Math.sin(t * 0.13) * 0.12, -Math.asin(normal.x));

      // ---- pelican life ---------------------------------------------------
      const flap = Math.sin(t * 1.55);
      for (const wing of pelican.wings) {
        const s = wing.side;
        wing.shoulder.rotation.x = flap * 0.32 - 0.08;
        wing.shoulder.rotation.z = -s * (0.15 + Math.sin(t * 1.55 + 0.6) * 0.15);
        wing.outer.rotation.x = Math.sin(t * 1.55 - 0.95) * 0.3;
        wing.outer.rotation.z = -s * (0.1 + Math.sin(t * 1.55 - 1.4) * 0.16);
      }

      pelican.group.position.y =
        BOARD_TOP - FOOT_Y * PELICAN_SCALE + Math.sin(t * 1.55) * 0.045;
      pelican.group.rotation.z = Math.sin(t * 0.72) * 0.05;
      pelican.group.rotation.x = -0.07 + Math.sin(t * 0.9) * 0.035;

      pelican.head.rotation.y = Math.sin(t * 0.33) * 0.3 + Math.sin(t * 0.17) * 0.14;
      pelican.head.rotation.x = Math.sin(t * 0.47) * 0.11 - 0.03;
      pelican.head.rotation.z = Math.sin(t * 0.29) * 0.07;

      pelican.pouch.scale.y = 0.33 + Math.sin(t * 2.2) * 0.018;

      // occasional blink
      const blink = Math.pow(Math.max(0, Math.sin(t * 0.78)), 60);
      for (const eye of pelican.eyes) eye.scale.y = 1 - blink * 0.92;

      // foam texture drift
      foamMap.offset.y = (-t * 0.22) % 1;
      collar.material.opacity = 0.36 + Math.sin(t * 1.9) * 0.08;
    },
  };
}