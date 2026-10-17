import * as THREE from 'three';

// All pelican geometry is generated in code -- no external assets. The bird is
// modelled in a local space where +X is forward (the direction of travel),
// +Y is up and +Z is to the rider's left.

function makeFeatherTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#f8f9f7';
  ctx.fillRect(0, 0, 256, 256);

  const img = ctx.getImageData(0, 0, 256, 256);
  for (let i = 0; i < img.data.length; i += 4) {
    const n = (Math.random() * 16) | 0;
    img.data[i] = Math.max(0, img.data[i] - n);
    img.data[i + 1] = Math.max(0, img.data[i + 1] - n);
    img.data[i + 2] = Math.max(0, img.data[i + 2] - n);
  }
  ctx.putImageData(img, 0, 0);

  // Soft feather streaks.
  ctx.globalAlpha = 0.06;
  ctx.strokeStyle = '#9fb0bd';
  for (let i = 0; i < 90; i++) {
    const y = Math.random() * 256;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.bezierCurveTo(80, y + 12, 170, y - 12, 256, y);
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2, 2);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function makeWingGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 0.2);
  s.bezierCurveTo(0.38, 0.3, 0.86, 0.2, 1.18, -0.04);
  s.bezierCurveTo(0.82, -0.12, 0.34, -0.3, 0, -0.24);
  s.closePath();

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.05,
    bevelEnabled: true,
    bevelThickness: 0.015,
    bevelSize: 0.02,
    bevelSegments: 2,
    curveSegments: 12,
  });
  // Lay the wing flat (chord across Z, span along X).
  geo.rotateX(-Math.PI / 2);
  geo.translate(0, 0, 0);
  return geo;
}

function makeBoardGeometry() {
  const s = new THREE.Shape();
  s.moveTo(-1.7, 0);
  s.bezierCurveTo(-1.0, 0.42, 0.9, 0.46, 1.7, 0);
  s.bezierCurveTo(0.9, -0.46, -1.0, -0.42, -1.7, 0);

  const geo = new THREE.ExtrudeGeometry(s, {
    depth: 0.12,
    bevelEnabled: true,
    bevelThickness: 0.03,
    bevelSize: 0.03,
    bevelSegments: 3,
    curveSegments: 18,
  });
  geo.rotateX(-Math.PI / 2);
  return geo;
}

export function createPelican() {
  const root = new THREE.Group();

  const featherMap = makeFeatherTexture();
  const mats = {
    feather: new THREE.MeshStandardMaterial({
      color: 0xedf1ee,
      map: featherMap,
      roughness: 0.8,
      metalness: 0.0,
      envMapIntensity: 0.8,
    }),
    wingTip: new THREE.MeshStandardMaterial({
      color: 0x3a4048,
      roughness: 0.85,
    }),
    beak: new THREE.MeshStandardMaterial({
      color: 0xffb733,
      roughness: 0.45,
      emissive: 0x201200,
      emissiveIntensity: 0.7,
    }),
    pouch: new THREE.MeshStandardMaterial({ color: 0xf7c07a, roughness: 0.6 }),
    eye: new THREE.MeshStandardMaterial({ color: 0x0a0a10, roughness: 0.15 }),
    leg: new THREE.MeshStandardMaterial({ color: 0xef8a2b, roughness: 0.5 }),
    board: new THREE.MeshStandardMaterial({ color: 0xff6f52, roughness: 0.3 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xfff4d6, roughness: 0.3 }),
  };

  // ---- Surfboard -----------------------------------------------------------
  const board = new THREE.Mesh(makeBoardGeometry(), mats.board);
  board.position.y = 0.02;
  root.add(board);

  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.75, 0.02, 0.13),
    mats.stripe,
  );
  stripe.position.set(0, 0.17, 0);
  root.add(stripe);

  // ---- Legs & feet ---------------------------------------------------------
  for (const side of [-1, 1]) {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.045, 0.055, 0.46, 10),
      mats.leg,
    );
    leg.position.set(-0.02, 0.4, side * 0.15);
    root.add(leg);

    const foot = new THREE.Mesh(
      new THREE.BoxGeometry(0.3, 0.045, 0.16),
      mats.leg,
    );
    foot.position.set(0.04, 0.19, side * 0.15);
    root.add(foot);
  }

  // ---- Torso (everything above the legs) -----------------------------------
  const torso = new THREE.Group();
  root.add(torso);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.5, 32, 24), mats.feather);
  body.scale.set(1.2, 0.95, 0.92);
  body.position.set(-0.05, 0.95, 0);
  torso.add(body);

  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.62, 6), mats.feather);
  tail.rotation.z = 1.35; // point back and slightly up
  tail.scale.z = 0.6;
  tail.position.set(-0.72, 1.02, 0);
  torso.add(tail);

  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.28, 1.2, 0),
    new THREE.Vector3(0.42, 1.55, 0),
    new THREE.Vector3(0.55, 1.86, 0),
    new THREE.Vector3(0.62, 2.08, 0),
  ]);
  const neck = new THREE.Mesh(
    new THREE.TubeGeometry(neckCurve, 28, 0.16, 12, false),
    mats.feather,
  );
  torso.add(neck);

  // Head group pivots at the top of the neck so the bird can look around.
  const headPivot = new THREE.Group();
  headPivot.position.set(0.6, 2.05, 0);
  torso.add(headPivot);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 32, 24), mats.feather);
  head.scale.set(1.05, 0.95, 0.92);
  head.position.set(0.06, 0.07, 0);
  headPivot.add(head);

  // Upper mandible.
  const beak = new THREE.Mesh(new THREE.ConeGeometry(0.115, 0.95, 8), mats.beak);
  beak.rotation.z = -Math.PI / 2;
  beak.scale.set(0.68, 1.0, 0.9);
  beak.position.set(0.75, 0.03, 0);
  headPivot.add(beak);

  // Gular pouch hanging under the mandible.
  const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.25, 24, 16), mats.pouch);
  pouch.scale.set(1.95, 0.8, 0.95);
  pouch.position.set(0.45, -0.14, 0);
  headPivot.add(pouch);

  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12), mats.eye);
    eye.position.set(0.24, 0.16, side * 0.2);
    headPivot.add(eye);
  }

  // ---- Wings ---------------------------------------------------------------
  const wingGeo = makeWingGeometry();
  const wings = [];
  for (const side of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.set(0.02, 1.14, side * 0.3);
    torso.add(pivot);

    const wing = new THREE.Mesh(wingGeo, mats.feather);
    pivot.add(wing);

    // Dark wing tips.
    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 10), mats.wingTip);
    tip.scale.set(0.55, 0.22, 0.9);
    tip.position.set(1.1, 0, -0.02);
    pivot.add(tip);

    // Point the span outward, back and up.
    const dir = new THREE.Vector3(-0.62, 0.4, side * 0.72).normalize();
    const base = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(1, 0, 0),
      dir,
    );
    pivot.quaternion.copy(base);

    wings.push({ pivot, base, side });
  }

  headPivot.rotation.y = -0.5;
  headPivot.rotation.z = -0.06;

  return { root, torso, wings, headPivot };
}
