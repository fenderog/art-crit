import * as THREE from 'three';
import { sampleOcean } from './ocean.js';
import { makeFoamRingTexture } from './textures.js';

const YAW = 0.55;
const SPEED = 2.05;

function makeFeatherGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.bezierCurveTo(0.075, 0.12, 0.085, 0.55, 0, 1.0);
  shape.bezierCurveTo(-0.085, 0.55, -0.075, 0.12, 0, 0);
  const geom = new THREE.ExtrudeGeometry(shape, {
    depth: 0.018,
    bevelEnabled: true,
    bevelThickness: 0.008,
    bevelSize: 0.008,
    bevelSegments: 1,
    curveSegments: 10,
  });
  geom.rotateX(Math.PI / 2);
  geom.computeVertexNormals();
  return geom;
}

function buildBoard() {
  const shape = new THREE.Shape();
  shape.moveTo(0, -1.7);
  shape.bezierCurveTo(0.28, -1.69, 0.45, -1.35, 0.48, -0.72);
  shape.bezierCurveTo(0.5, -0.12, 0.49, 0.44, 0.4, 1.02);
  shape.bezierCurveTo(0.32, 1.48, 0.14, 1.71, 0, 1.78);
  shape.bezierCurveTo(-0.14, 1.71, -0.32, 1.48, -0.4, 1.02);
  shape.bezierCurveTo(-0.49, 0.44, -0.5, -0.12, -0.48, -0.72);
  shape.bezierCurveTo(-0.45, -1.35, -0.28, -1.69, 0, -1.7);

  const geom = new THREE.ExtrudeGeometry(shape, {
    depth: 0.09,
    bevelEnabled: true,
    bevelThickness: 0.035,
    bevelSize: 0.035,
    bevelSegments: 3,
    curveSegments: 28,
  });
  geom.rotateX(Math.PI / 2);
  geom.computeBoundingBox();
  geom.translate(0, -geom.boundingBox.min.y, 0);
  geom.computeVertexNormals();

  const deckTop = geom.boundingBox.max.y - geom.boundingBox.min.y;

  const boardMat = new THREE.MeshPhysicalMaterial({
    color: 0xf7f0dd,
    roughness: 0.26,
    metalness: 0.04,
    clearcoat: 0.55,
    clearcoatRoughness: 0.28,
  });
  const board = new THREE.Mesh(geom, boardMat);
  board.castShadow = true;
  board.receiveShadow = true;

  // Coral racing stripe, tapered toward the nose.
  const stripeShape = new THREE.Shape();
  stripeShape.moveTo(-0.09, -1.28);
  stripeShape.bezierCurveTo(0.09, -1.28, 0.07, 0.25, 0.045, 1.05);
  stripeShape.bezierCurveTo(0.03, 1.4, 0.012, 1.6, 0, 1.64);
  stripeShape.bezierCurveTo(-0.012, 1.6, -0.03, 1.4, -0.045, 1.05);
  stripeShape.bezierCurveTo(-0.07, 0.25, -0.09, -1.28, -0.09, -1.28);
  const stripeGeom = new THREE.ShapeGeometry(stripeShape, 24);
  stripeGeom.rotateX(-Math.PI / 2);
  stripeGeom.rotateY(Math.PI);
  const stripe = new THREE.Mesh(
    stripeGeom,
    new THREE.MeshPhysicalMaterial({
      color: 0xff4a35,
      roughness: 0.35,
      clearcoat: 0.4,
    })
  );
  stripe.position.y = deckTop + 0.002;
  board.add(stripe);

  // Two thin teal pinstripes flanking the stripe.
  for (const side of [-1, 1]) {
    const pin = new THREE.Mesh(
      new THREE.PlaneGeometry(0.014, 2.55),
      new THREE.MeshBasicMaterial({ color: 0x19c4b2 })
    );
    pin.rotation.x = -Math.PI / 2;
    pin.position.set(side * 0.135, deckTop + 0.003, 0.05);
    board.add(pin);
  }

  // A traction pad and leash plug add a little surf-shop detail.
  const padW = 0.36;
  const padL = 0.54;
  const padR = 0.1;
  const padShape = new THREE.Shape();
  padShape.moveTo(-padW / 2 + padR, -padL / 2);
  padShape.lineTo(padW / 2 - padR, -padL / 2);
  padShape.quadraticCurveTo(padW / 2, -padL / 2, padW / 2, -padL / 2 + padR);
  padShape.lineTo(padW / 2, padL / 2 - padR);
  padShape.quadraticCurveTo(padW / 2, padL / 2, padW / 2 - padR, padL / 2);
  padShape.lineTo(-padW / 2 + padR, padL / 2);
  padShape.quadraticCurveTo(-padW / 2, padL / 2, -padW / 2, padL / 2 - padR);
  padShape.lineTo(-padW / 2, -padL / 2 + padR);
  padShape.quadraticCurveTo(-padW / 2, -padL / 2, -padW / 2 + padR, -padL / 2);
  const padGeom = new THREE.ShapeGeometry(padShape, 8);
  padGeom.rotateX(-Math.PI / 2);
  const pad = new THREE.Mesh(
    padGeom,
    new THREE.MeshStandardMaterial({ color: 0x176f6a, roughness: 0.86 })
  );
  pad.position.set(0, deckTop + 0.004, -0.62);
  board.add(pad);

  const plug = new THREE.Mesh(
    new THREE.CylinderGeometry(0.035, 0.035, 0.014, 12),
    new THREE.MeshStandardMaterial({ color: 0xff8a3d, roughness: 0.5 })
  );
  plug.position.set(0, deckTop + 0.006, -1.52);
  board.add(plug);

  // A small fin beneath the tail.
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0);
  finShape.lineTo(0, -0.36);
  finShape.quadraticCurveTo(0.24, -0.3, 0.44, -0.02);
  finShape.lineTo(0, 0);
  const finGeom = new THREE.ExtrudeGeometry(finShape, {
    depth: 0.026,
    bevelEnabled: false,
    curveSegments: 10,
  });
  finGeom.rotateY(Math.PI / 2);
  const fin = new THREE.Mesh(
    finGeom,
    new THREE.MeshPhysicalMaterial({ color: 0x1fa99d, roughness: 0.3, clearcoat: 0.5 })
  );
  fin.position.set(-0.013, 0.07, -0.98);
  board.add(fin);

  // Foam collar hugging the waterline.
  const foam = new THREE.Mesh(
    new THREE.PlaneGeometry(2.75, 4.5),
    new THREE.MeshBasicMaterial({
      map: makeFoamRingTexture(),
      transparent: true,
      opacity: 0.8,
      depthWrite: false,
      side: THREE.DoubleSide,
    })
  );
  foam.rotation.x = -Math.PI / 2;
  foam.position.y = 0.09;
  foam.renderOrder = 2;
  board.add(foam);

  return { board, deckTop };
}

function buildPelican() {
  const root = new THREE.Group();
  const featherGeom = makeFeatherGeometry();

  const matFeather = new THREE.MeshStandardMaterial({
    color: 0xfff6e6,
    roughness: 0.88,
    metalness: 0.0,
  });
  const matFeatherShade = new THREE.MeshStandardMaterial({
    color: 0xf0dfc7,
    roughness: 0.9,
  });
  const matBlack = new THREE.MeshStandardMaterial({
    color: 0x2e303a,
    roughness: 0.75,
  });
  const matBeak = new THREE.MeshStandardMaterial({
    color: 0xffa72d,
    roughness: 0.4,
    metalness: 0.03,
  });
  const matBeakDark = new THREE.MeshStandardMaterial({
    color: 0xd97c1a,
    roughness: 0.45,
  });
  const matPouch = new THREE.MeshStandardMaterial({
    color: 0xffc35e,
    roughness: 0.58,
  });
  const matEyeWhite = new THREE.MeshStandardMaterial({
    color: 0xfff9ee,
    roughness: 0.3,
  });
  const matPupil = new THREE.MeshStandardMaterial({
    color: 0x0c0d12,
    roughness: 0.12,
    metalness: 0.1,
  });
  const matHighlight = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const matFeet = new THREE.MeshStandardMaterial({
    color: 0xff9440,
    roughness: 0.6,
  });

  const cast = (obj) => {
    obj.traverse((o) => {
      if (o.isMesh) o.castShadow = true;
    });
    return obj;
  };

  // Body: a soft pear-shaped lathe, with a chest that leans into the wind.
  const bodyProfile = [
    new THREE.Vector2(0.1, 0.49),
    new THREE.Vector2(0.24, 0.54),
    new THREE.Vector2(0.34, 0.66),
    new THREE.Vector2(0.395, 0.82),
    new THREE.Vector2(0.405, 0.98),
    new THREE.Vector2(0.365, 1.13),
    new THREE.Vector2(0.285, 1.26),
    new THREE.Vector2(0.19, 1.35),
    new THREE.Vector2(0.12, 1.39),
  ];
  const bodyGeom = new THREE.LatheGeometry(bodyProfile, 36);
  bodyGeom.scale(1.0, 1.0, 1.18);
  bodyGeom.translate(0, 0, 0.015);
  const body = new THREE.Mesh(bodyGeom, matFeather);
  body.rotation.x = 0.06;
  root.add(body);

  // Neck.
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 1.2, 0.07),
    new THREE.Vector3(0, 1.36, 0.13),
    new THREE.Vector3(0, 1.52, 0.17),
    new THREE.Vector3(0, 1.68, 0.2),
    new THREE.Vector3(0, 1.8, 0.21),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 30, 0.105, 14, false), matFeather);
  root.add(neck);

  // Head group, pivoted where the neck meets the skull.
  const head = new THREE.Group();
  head.position.set(0, 1.82, 0.2);
  root.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), matFeather);
  skull.scale.set(0.225, 0.215, 0.245);
  skull.position.set(0, 0.04, 0.06);
  head.add(skull);

  // Crest feathers at the back of the head.
  for (let i = 0; i < 3; i++) {
    const crest = new THREE.Mesh(featherGeom, matFeatherShade);
    crest.scale.set(0.7 - i * 0.08, 1, 0.2 - i * 0.015);
    crest.position.set((i - 1) * 0.055, 0.17, -0.1 - i * 0.015);
    crest.rotation.set(-0.95 - i * 0.12, 0, (i - 1) * 0.18);
    head.add(crest);
  }

  // Beak and pouch.
  const beak = new THREE.Group();
  beak.position.set(0, 0.0, 0.22);
  beak.rotation.x = 0.15;
  head.add(beak);

  const mandibleGeom = new THREE.CylinderGeometry(0.034, 0.088, 0.95, 12, 1, false);
  mandibleGeom.rotateX(Math.PI / 2);
  const mandible = new THREE.Mesh(mandibleGeom, matBeak);
  mandible.scale.set(1.38, 0.56, 1);
  mandible.position.set(0, -0.012, 0.475);
  beak.add(mandible);

  const hook = new THREE.Mesh(new THREE.SphereGeometry(0.045, 14, 10), matBeakDark);
  hook.scale.set(0.9, 0.8, 1.1);
  hook.position.set(0, -0.065, 0.955);
  beak.add(hook);

  const pouch = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 20), matPouch);
  pouch.scale.set(0.145, 0.2, 0.44);
  pouch.position.set(0, -0.195, 0.47);
  pouch.rotation.x = 0.06;
  beak.add(pouch);

  const pouchBase = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), matPouch);
  pouchBase.scale.set(0.17, 0.16, 0.22);
  pouchBase.position.set(0, -0.13, 0.15);
  beak.add(pouchBase);

  const jawCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, -0.03, 0.02),
    new THREE.Vector3(0, -0.075, 0.42),
    new THREE.Vector3(0, -0.07, 0.78),
    new THREE.Vector3(0, -0.06, 0.93),
  ]);
  const jawLine = new THREE.Mesh(
    new THREE.TubeGeometry(jawCurve, 20, 0.012, 8, false),
    matBeakDark
  );
  beak.add(jawLine);

  // Eyes.
  const eyeGroups = [];
  for (const side of [-1, 1]) {
    const eye = new THREE.Group();
    eye.position.set(side * 0.195, 0.065, 0.145);
    head.add(eye);

    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.062, 0.012, 8, 22), matBeak);
    ring.rotation.y = Math.PI / 2;
    ring.position.x = side * 0.012;
    eye.add(ring);

    const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.058, 20, 14), matEyeWhite);
    sclera.scale.set(0.62, 1, 1);
    eye.add(sclera);

    const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.033, 16, 12), matPupil);
    pupil.position.x = side * 0.03;
    pupil.scale.set(0.72, 1, 1);
    eye.add(pupil);

    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.011, 8, 6), matHighlight);
    glint.position.set(side * 0.047, 0.017, 0.017);
    eye.add(glint);

    eyeGroups.push({ eye, side });
  }

  // Wings.
  const matWingPanel = new THREE.MeshStandardMaterial({
    color: 0xfff6e6,
    roughness: 0.88,
    side: THREE.DoubleSide,
  });

  const wingPanelShape = new THREE.Shape();
  wingPanelShape.moveTo(0, 0.19);
  wingPanelShape.bezierCurveTo(0.18, 0.27, 0.44, 0.2, 0.63, 0.02);
  wingPanelShape.lineTo(0.6, -0.2);
  wingPanelShape.bezierCurveTo(0.42, -0.31, 0.14, -0.31, 0, -0.17);
  wingPanelShape.closePath();
  const wingPanelGeom = new THREE.ExtrudeGeometry(wingPanelShape, {
    depth: 0.022,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.012,
    bevelSegments: 2,
    curveSegments: 18,
  });
  wingPanelGeom.rotateX(Math.PI / 2);

  const wings = [];
  for (const side of [-1, 1]) {
    const wing = new THREE.Group();
    wing.position.set(side * 0.29, 1.16, 0.0);
    wing.rotation.order = 'YZX';
    root.add(wing);

    const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.11, 18, 14), matFeather);
    wing.add(shoulder);

    // A broad wing panel gives the wing mass from every angle.
    const panel = new THREE.Mesh(wingPanelGeom, matWingPanel);
    panel.scale.x = side;
    panel.position.y = 0.025;
    wing.add(panel);

    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.066, 0.34, 6, 12), matFeatherShade);
    arm.rotation.z = -side * Math.PI / 2;
    arm.position.x = side * 0.2;
    wing.add(arm);

    // Short covert feathers break up the line of the upper arm.
    for (let i = 0; i < 4; i++) {
      const g = new THREE.Group();
      g.rotation.order = 'YZX';
      g.rotation.y = side * (Math.PI / 2 + (i - 1.5) * 0.14);
      g.rotation.z = -side * (0.24 + i * 0.035);
      g.position.set(side * (0.06 + i * 0.1), 0.045, 0.0);
      const covert = new THREE.Mesh(featherGeom, i < 2 ? matFeatherShade : matFeather);
      covert.scale.set(1.25, 1, 0.26 + i * 0.045);
      g.add(covert);
      wing.add(g);
    }

    const hand = new THREE.Group();
    hand.position.x = side * 0.42;
    wing.add(hand);

    const featherLengths = [0.62, 0.76, 0.88, 0.94, 0.9, 0.8, 0.68];
    const feathers = [];
    for (let i = 0; i < featherLengths.length; i++) {
      const g = new THREE.Group();
      const fan = -0.38 + (i / (featherLengths.length - 1)) * 1.3;
      const droop = 0.05 + i * 0.032;
      g.rotation.order = 'YZX';
      g.rotation.y = side * (Math.PI / 2 + fan);
      g.rotation.z = -side * droop;
      g.position.y = 0.02 * i;

      const primary = i >= 4;
      const feather = new THREE.Mesh(featherGeom, primary ? matBlack : matFeather);
      feather.scale.set(primary ? 1.35 : 1.55, 1, featherLengths[i] * 1.08);
      feather.castShadow = true;
      g.add(feather);
      hand.add(g);
      feathers.push({ g, baseFan: fan, baseDroop: droop, side, i });
    }

    // Shorter covert feathers layered over the base of the primaries.
    for (let i = 0; i < 4; i++) {
      const g = new THREE.Group();
      const fan = -0.05 + i * 0.2;
      g.rotation.order = 'YZX';
      g.rotation.y = side * (Math.PI / 2 + fan);
      g.rotation.z = -side * (0.16 + i * 0.03);
      g.position.set(0, 0.035, 0);
      const feather = new THREE.Mesh(featherGeom, matFeatherShade);
      feather.scale.set(1.05, 1, 0.4 + i * 0.03);
      g.add(feather);
      hand.add(g);
    }

    wing.userData = { side, feathers };
    wings.push(wing);
  }

  // Tail.
  const tail = new THREE.Group();
  tail.position.set(0, 0.82, -0.42);
  tail.rotation.x = -0.25;
  root.add(tail);
  for (let i = -2; i <= 2; i++) {
    const g = new THREE.Group();
    g.rotation.y = Math.PI + i * 0.14;
    g.rotation.x = -0.12 + Math.abs(i) * 0.05;
    const feather = new THREE.Mesh(featherGeom, i === 0 ? matFeather : matFeatherShade);
    feather.scale.set(0.95, 1, 0.46 - Math.abs(i) * 0.04);
    feather.castShadow = true;
    g.add(feather);
    tail.add(g);
  }

  // Legs and webbed feet.
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.042, 0.26, 5, 10), matFeet);
    leg.position.set(side * 0.16, 0.37, 0.02);
    leg.rotation.x = 0.06;
    root.add(leg);

    const foot = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 12), matFeet);
    foot.scale.set(0.105, 0.035, 0.17);
    foot.position.set(side * 0.18, 0.045, 0.09);
    root.add(foot);

    for (let t = -1; t <= 1; t++) {
      const toe = new THREE.Mesh(new THREE.CapsuleGeometry(0.017, 0.1, 4, 8), matFeet);
      toe.rotation.x = Math.PI / 2;
      toe.rotation.z = t * 0.18;
      toe.position.set(side * 0.18 + t * 0.045, 0.04, 0.2);
      root.add(toe);
    }
  }

  cast(root);

  return { root, body, head, beak, pouch, wings, tail, eyeGroups };
}

export function createRider() {
  const group = new THREE.Group();
  group.rotation.order = 'YXZ';

  const { board, deckTop } = buildBoard();
  group.add(board);

  const pelican = buildPelican();
  pelican.root.position.y = deckTop - 0.005;
  group.add(pelican.root);

  const forward = new THREE.Vector3(Math.sin(YAW), 0, Math.cos(YAW));
  const right = new THREE.Vector3(Math.cos(YAW), 0, -Math.sin(YAW));
  const position = new THREE.Vector3(0, 0, 0);

  const bodyBaseScale = pelican.body.scale.clone();

  return {
    group,
    board,
    pelican: pelican.root,
    deckTop,
    forward,
    right,
    position,
    speed: SPEED,
    yaw: YAW,

    update(time, dt) {
      position.x += forward.x * SPEED * dt;
      position.z += forward.z * SPEED * dt;

      const wave = sampleOcean(position.x, position.z, time);
      const slopeF = wave.dx * forward.x + wave.dz * forward.z;
      const slopeR = wave.dx * right.x + wave.dz * right.z;

      const pitch = -Math.atan(slopeF) * 0.92 + Math.sin(time * 1.25) * 0.012;
      const roll = Math.atan(slopeR) * 0.92 + Math.cos(time * 1.05) * 0.01;

      group.position.set(position.x, wave.height - 0.04, position.z);
      group.rotation.y = YAW;
      group.rotation.x = pitch;
      group.rotation.z = roll;

      // The bird balances against the board, pivoting from its feet.
      pelican.root.rotation.x = -pitch * 0.68 + Math.sin(time * 1.4) * 0.017;
      pelican.root.rotation.z = -roll * 0.58 + Math.cos(time * 1.12) * 0.021;
      pelican.root.position.y = deckTop - 0.005 + Math.sin(time * 2.1) * 0.007;

      const breathe = 1 + Math.sin(time * 1.6) * 0.012;
      pelican.body.scale.set(
        bodyBaseScale.x * breathe,
        bodyBaseScale.y * (1 + Math.sin(time * 1.6) * 0.014),
        bodyBaseScale.z * breathe
      );

      // Wings make small, continuous balancing corrections.
      for (const wing of pelican.wings) {
        const side = wing.userData.side;
        const flap = Math.sin(time * 1.75 + side * 0.55) * 0.07;
        wing.rotation.z = side * (0.34 + flap);
        wing.rotation.y = side * (0.55 + Math.sin(time * 1.05 + side * 0.9) * 0.035);
        wing.rotation.x = side * 0.5 + Math.sin(time * 1.9 + side * 1.2) * 0.04;

        for (const f of wing.userData.feathers) {
          const flutter = Math.sin(time * 2.6 + f.i * 0.7 + side) * 0.018;
          f.g.rotation.z = -f.side * (f.baseDroop + flutter);
          f.g.rotation.y = f.side * (Math.PI / 2 + f.baseFan + flutter * 0.5);
        }
      }

      // Head drifts, then settles back toward the horizon.
      pelican.head.rotation.y =
        Math.sin(time * 0.31) * 0.16 + Math.sin(time * 0.13 + 1.2) * 0.07;
      pelican.head.rotation.x = Math.sin(time * 0.7) * 0.03 - 0.02;
      pelican.head.rotation.z = Math.sin(time * 0.42 + 0.8) * 0.025;

      const pouchPulse = 1 + Math.sin(time * 2.15) * 0.035;
      pelican.pouch.scale.set(0.145, 0.2 * pouchPulse, 0.44);

      pelican.tail.rotation.z = Math.sin(time * 1.15 + 0.4) * 0.06;
      pelican.tail.rotation.x = -0.25 + Math.sin(time * 0.9) * 0.03;

      // Occasional blink.
      const blinkPhase = (time + 1.4) % 4.4;
      const blink = blinkPhase < 0.16 ? Math.sin((blinkPhase / 0.16) * Math.PI) : 0;
      for (const { eye } of pelican.eyeGroups) {
        eye.scale.y = 1 - blink * 0.92;
      }
    },
  };
}
