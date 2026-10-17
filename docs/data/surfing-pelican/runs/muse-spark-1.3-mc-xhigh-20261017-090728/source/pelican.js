import * as THREE from 'three';

// Builds a cartoon pelican standing on a surfboard, facing +X.
// Returns { group, update(t, roll) }; roll is the board's current roll
// angle so the wings can counter-balance against it.
export function buildSurfer() {
  const group = new THREE.Group();

  const matBody = new THREE.MeshStandardMaterial({ color: 0xf7f2e7, roughness: 0.85 });
  const matWing = new THREE.MeshStandardMaterial({ color: 0x9fb0ba, roughness: 0.9 });
  const matTip = new THREE.MeshStandardMaterial({ color: 0x5b6670, roughness: 0.9 });
  const matBeak = new THREE.MeshStandardMaterial({ color: 0xf59a3e, roughness: 0.5 });
  const matBeakDark = new THREE.MeshStandardMaterial({ color: 0xc96f22, roughness: 0.6 });
  const matPouch = new THREE.MeshStandardMaterial({ color: 0xf0a988, roughness: 0.65 });
  const matLeg = new THREE.MeshStandardMaterial({ color: 0xe8852a, roughness: 0.7 });
  const matDark = new THREE.MeshStandardMaterial({ color: 0x23272c, roughness: 0.35 });
  const matWhite = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5 });
  const matBoard = new THREE.MeshStandardMaterial({ color: 0xff6b57, roughness: 0.4 });
  const matCream = new THREE.MeshStandardMaterial({ color: 0xfff3df, roughness: 0.6 });

  const solid = (geo, mat, x = 0, y = 0, z = 0) => {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.castShadow = true;
    return m;
  };

  // ---- surfboard (long axis = X, nose at +X) ----
  const L = 2.7;
  const W = 0.85;
  const s = new THREE.Shape();
  s.moveTo(-L / 2, 0);
  s.bezierCurveTo(-L / 2, W * 0.42, -L * 0.1, W * 0.5, L * 0.28, W * 0.32);
  s.quadraticCurveTo(L * 0.48, W * 0.1, L / 2, 0);
  s.quadraticCurveTo(L * 0.48, -W * 0.1, L * 0.28, -W * 0.32);
  s.bezierCurveTo(-L * 0.1, -W * 0.5, -L / 2, -W * 0.42, -L / 2, 0);
  const boardGeo = new THREE.ExtrudeGeometry(s, {
    depth: 0.07,
    bevelEnabled: true,
    bevelThickness: 0.025,
    bevelSize: 0.025,
    bevelSegments: 2,
    curveSegments: 24,
  });
  boardGeo.rotateX(-Math.PI / 2);
  boardGeo.translate(0, 0.025, 0);
  const board = new THREE.Mesh(boardGeo, matBoard);
  board.castShadow = true;
  board.receiveShadow = true;
  group.add(board);

  const stripe = solid(new THREE.BoxGeometry(L * 0.62, 0.014, 0.17), matCream, 0.05, 0.105, 0);
  stripe.castShadow = false;
  group.add(stripe);
  const noseDot = solid(new THREE.CylinderGeometry(0.09, 0.09, 0.014, 20), matCream, L * 0.38, 0.105, 0);
  noseDot.castShadow = false;
  group.add(noseDot);
  const fin = solid(new THREE.ConeGeometry(0.1, 0.3, 12), matCream, -L / 2 + 0.35, -0.1, 0);
  fin.scale.z = 0.35;
  fin.rotation.z = 0.25;
  group.add(fin);

  // ---- pelican ----
  const bird = new THREE.Group();
  group.add(bird);

  // legs + feet in a tandem surf stance along the board
  for (const fx of [0.38, -0.34]) {
    bird.add(solid(new THREE.BoxGeometry(0.26, 0.05, 0.12), matLeg, fx, 0.13, 0));
    for (let i = -1; i <= 1; i++) {
      const toe = solid(new THREE.ConeGeometry(0.028, 0.1, 8), matLeg, fx + 0.17, 0.12, i * 0.04);
      toe.rotation.z = -Math.PI / 2;
      bird.add(toe);
    }
    const leg = solid(new THREE.CylinderGeometry(0.045, 0.05, 0.34, 10), matLeg, fx - 0.02, 0.3, 0);
    leg.rotation.z = 0.08;
    bird.add(leg);
  }

  // body
  const body = solid(new THREE.SphereGeometry(0.34, 32, 24), matBody, 0, 0.62, 0);
  body.scale.set(1.28, 1.0, 0.92);
  bird.add(body);

  // tail feathers pointing up-back
  const tail = solid(new THREE.ConeGeometry(0.11, 0.42, 12), matWing, -0.44, 0.7, 0);
  tail.scale.set(1, 1, 0.55);
  tail.rotation.z = THREE.MathUtils.degToRad(72);
  bird.add(tail);

  // neck rising from the chest
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.28, 0.64, 0),
    new THREE.Vector3(0.4, 0.86, 0),
    new THREE.Vector3(0.42, 1.06, 0),
    new THREE.Vector3(0.36, 1.2, 0),
  ]);
  bird.add(solid(new THREE.TubeGeometry(neckCurve, 20, 0.105, 12), matBody));

  // head
  const head = new THREE.Group();
  head.position.set(0.38, 1.27, 0);
  bird.add(head);
  const skull = solid(new THREE.SphereGeometry(0.2, 28, 20), matBody);
  skull.scale.set(1.15, 1.0, 0.9);
  head.add(skull);

  // crest feathers swept back
  for (let i = 0; i < 3; i++) {
    const c = solid(new THREE.ConeGeometry(0.05 - i * 0.008, 0.16 - i * 0.02, 8), matWing, -0.16 - i * 0.05, 0.08 + i * 0.015, 0);
    c.rotation.z = 1.25;
    head.add(c);
  }

  // eyes on both sides so the 3/4 camera always catches one
  const eyeWhites = [];
  const pupils = [];
  for (const side of [1, -1]) {
    const e = solid(new THREE.SphereGeometry(0.05, 14, 12), matWhite, 0.1, 0.05, side * 0.135);
    e.castShadow = false;
    head.add(e);
    eyeWhites.push(e);
    const p = solid(new THREE.SphereGeometry(0.024, 12, 10), matDark, 0.132, 0.05, side * 0.168);
    p.castShadow = false;
    head.add(p);
    pupils.push(p);
  }

  // long beak with a wobbly pouch
  const beak = new THREE.Group();
  beak.position.set(0.14, -0.03, 0);
  beak.rotation.z = -0.05;
  head.add(beak);
  const upper = solid(new THREE.CylinderGeometry(0.02, 0.062, 0.8, 16), matBeak, 0.44, 0.01, 0);
  upper.rotation.z = -Math.PI / 2 - 0.03;
  beak.add(upper);
  const nail = solid(new THREE.ConeGeometry(0.021, 0.08, 10), matBeakDark, 0.85, -0.005, 0);
  nail.rotation.z = -Math.PI / 2 - 0.15;
  beak.add(nail);
  const pouch = solid(new THREE.SphereGeometry(0.24, 24, 18), matPouch, 0.4, -0.14, 0);
  pouch.scale.set(1.4, 0.62, 0.5);
  beak.add(pouch);
  const pouchBase = pouch.scale.clone();

  // outstretched balancing wings with fingered tips
  const wings = [];
  for (const side of [1, -1]) {
    const pivot = new THREE.Group();
    pivot.position.set(-0.02, 0.82, side * 0.24);
    const inner = solid(new THREE.SphereGeometry(0.3, 24, 18), matWing, -0.03, 0, side * 0.3);
    inner.scale.set(0.9, 0.24, 1.1);
    pivot.add(inner);
    const tip = solid(new THREE.SphereGeometry(0.2, 20, 14), matTip, -0.14, -0.01, side * 0.62);
    tip.scale.set(0.85, 0.2, 1.15);
    pivot.add(tip);
    for (let i = 0; i < 3; i++) {
      const f = solid(new THREE.ConeGeometry(0.045, 0.22, 8), matTip, -0.3 - i * 0.045, -0.02, side * (0.52 + i * 0.09));
      f.scale.z = 0.5;
      f.rotation.z = Math.PI / 2 + 0.25;
      f.rotation.y = side * -0.25;
      pivot.add(f);
    }
    pivot.rotation.y = -side * 0.15;
    bird.add(pivot);
    wings.push({ pivot, side });
  }

  function update(t, roll = 0) {
    // gentle flap plus a counter-tilt that fights the board's roll
    const flap = Math.sin(t * 2.4) * 0.15 + Math.sin(t * 5.1 + 1.0) * 0.035;
    const balance = THREE.MathUtils.clamp(-roll * 1.4, -0.45, 0.45);
    const f = -0.1 + flap;
    wings[0].pivot.rotation.x = f + balance;
    wings[1].pivot.rotation.x = -f + balance;
    wings[0].pivot.rotation.y = -0.15 + Math.sin(t * 2.4) * 0.03;
    wings[1].pivot.rotation.y = 0.15 - Math.sin(t * 2.4 + 0.6) * 0.03;

    // curious head: looks around, nods with the swell
    head.rotation.y = Math.sin(t * 0.55) * 0.5;
    head.rotation.z = Math.sin(t * 1.6) * 0.06 - 0.02;
    head.rotation.x = Math.sin(t * 0.8 + 0.7) * 0.08;

    // pouch wobble
    pouch.scale.set(
      pouchBase.x * (1 + 0.03 * Math.sin(t * 2.1)),
      pouchBase.y * (1 + 0.08 * Math.sin(t * 2.1 + 0.4)),
      pouchBase.z,
    );

    // tail wag and whole-body sway
    tail.rotation.x = Math.sin(t * 3.2) * 0.18;
    bird.position.y = Math.sin(t * 2.0) * 0.025;
    bird.rotation.z = Math.sin(t * 1.3) * 0.03;
    bird.rotation.x = balance * 0.25;

    // occasional blink
    const blink = (t % 4.3) < 0.12 ? 0.12 : 1;
    for (const e of eyeWhites) e.scale.y = blink;
    for (const p of pupils) p.scale.y = blink;
  }

  return { group, update };
}
