import * as THREE from "three";
import { waveHeight, waveSlope } from "./ocean.js";

// ---- materials -----------------------------------------------------------
const FEATHER = new THREE.MeshPhongMaterial({ color: 0xf7f2e7, shininess: 24, specular: 0x444444 });
const FEATHER_TIP = new THREE.MeshPhongMaterial({ color: 0xd8d0c0, shininess: 20 });
const ORANGE = new THREE.MeshPhongMaterial({ color: 0xf28c28, shininess: 30 });
const BEAK_MAT = new THREE.MeshPhongMaterial({ color: 0xf6a821, shininess: 40 });
const POUCH = new THREE.MeshPhongMaterial({ color: 0xe8931c, shininess: 35 });
const BLACK = new THREE.MeshBasicMaterial({ color: 0x1d1d1d });
const BOARD_MAT = new THREE.MeshPhongMaterial({ color: 0xe63946, shininess: 70, specular: 0x88ccdd });
const STRIPE_MAT = new THREE.MeshPhongMaterial({ color: 0xfff1dc, shininess: 50 });
const FIN_MAT = new THREE.MeshPhongMaterial({ color: 0x28324e, shininess: 60 });
const FOAM_MAT = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.45, depthWrite: false });

function sphere(r, mat, sx = 1, sy = 1, sz = 1) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 22, 16), mat);
  m.scale.set(sx, sy, sz);
  m.castShadow = true;
  return m;
}

// ---- surfboard -----------------------------------------------------------
function createBoard() {
  const group = new THREE.Group();

  const shape = new THREE.Shape();
  shape.moveTo(0, 2.3); // nose
  shape.bezierCurveTo(0.62, 1.6, 0.66, 0.4, 0.6, -0.6);
  shape.bezierCurveTo(0.56, -1.4, 0.3, -1.9, 0, -1.9); // rounded tail
  shape.bezierCurveTo(-0.3, -1.9, -0.56, -1.4, -0.6, -0.6);
  shape.bezierCurveTo(-0.66, 0.4, -0.62, 1.6, 0, 2.3);

  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: 0.14,
    bevelEnabled: true,
    bevelSize: 0.05,
    bevelThickness: 0.04,
    bevelSegments: 2,
    curveSegments: 24,
  });
  geo.rotateX(Math.PI / 2); // shape length -> +Z, thickness -> Y
  geo.computeBoundingBox();
  geo.translate(0, -geo.boundingBox.max.y, 0); // deck top sits at y = 0

  const deck = new THREE.Mesh(geo, BOARD_MAT);
  deck.castShadow = true;
  deck.rotation.x = -0.06; // a touch of nose rocker
  group.add(deck);

  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.02, 3.9), STRIPE_MAT);
  stripe.position.set(0, 0.012, 0);
  group.add(stripe);

  const fin = new THREE.Mesh(new THREE.ConeGeometry(0.17, 0.5, 4), FIN_MAT);
  fin.rotation.x = Math.PI; // point down
  fin.scale.x = 0.35;
  fin.position.set(0, -0.22, -1.35);
  group.add(fin);

  group.position.y = -0.04;
  return group;
}

// ---- pelican -------------------------------------------------------------
function createBird() {
  const bird = new THREE.Group();

  // body
  const body = sphere(1, FEATHER, 0.95, 0.85, 1.4);
  body.position.set(0, 1.55, -0.1);
  body.rotation.x = 0.06;
  bird.add(body);

  // neck
  const n1 = sphere(0.4, FEATHER);
  n1.position.set(0, 2.25, 0.75);
  const n2 = sphere(0.36, FEATHER);
  n2.position.set(0, 2.6, 1.05);
  bird.add(n1, n2);

  // head (own group so it can look around)
  const head = new THREE.Group();
  head.position.set(0, 2.95, 1.3);
  head.add(sphere(0.42, FEATHER));

  const beak = new THREE.Group();
  beak.position.set(0, -0.05, 0.35);

  const upper = new THREE.Mesh(new THREE.ConeGeometry(0.17, 1.55, 12), BEAK_MAT);
  upper.geometry.rotateX(Math.PI / 2); // point +Z
  upper.scale.y = 0.6;
  upper.position.z = 0.75;
  upper.castShadow = true;
  beak.add(upper);

  const pouch = sphere(0.26, POUCH, 0.75, 1.15, 2.6);
  pouch.position.set(0, -0.16, 0.5);
  beak.add(pouch);
  head.add(beak);

  for (const s of [-1, 1]) {
    const eye = sphere(0.055, BLACK);
    eye.position.set(0.21 * s, 0.12, 0.3);
    const glint = sphere(0.018, new THREE.MeshBasicMaterial({ color: 0xffffff }));
    glint.position.set(0.225 * s, 0.14, 0.34);
    head.add(eye, glint);
  }
  bird.add(head);

  // wings (pivot groups at the shoulders)
  const wings = {};
  for (const s of [-1, 1]) {
    const pivot = new THREE.Group();
    pivot.position.set(0.72 * s, 1.85, -0.05);

    const wing = sphere(1, FEATHER, 0.85, 0.09, 0.42);
    wing.position.set(0.78 * s, 0, 0.02);
    wing.rotation.y = 0.35 * s; // sweep back
    pivot.add(wing);

    const tip = sphere(0.3, FEATHER_TIP, 1, 0.28, 1.1);
    tip.position.set(1.52 * s, 0, -0.14);
    tip.rotation.y = 0.35 * s;
    pivot.add(tip);

    pivot.rotation.z = 0.25 * s;
    wings[s] = pivot;
    bird.add(pivot);
  }

  // tail
  const tail = new THREE.Group();
  tail.position.set(0, 1.5, -1.35);
  const tailMesh = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1.0, 10), FEATHER_TIP);
  tailMesh.rotation.x = -0.9; // point back and up
  tailMesh.scale.z = 0.45;
  tailMesh.position.set(0, 0.25, -0.35);
  tailMesh.castShadow = true;
  tail.add(tailMesh);
  bird.add(tail);

  // legs + feet
  for (const s of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.78, 10), ORANGE);
    leg.position.set(0.3 * s, 0.36, 0.15);
    leg.rotation.x = 0.08;
    leg.castShadow = true;
    const knee = sphere(0.1, ORANGE);
    knee.position.set(0.3 * s, 0.72, 0.1);
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.06, 0.55), ORANGE);
    foot.position.set(0.3 * s, 0.03, 0.32);
    foot.castShadow = true;
    bird.add(leg, knee, foot);
  }

  return { bird, head, wingL: wings[1], wingR: wings[-1], tail };
}

// ---- foam ----------------------------------------------------------------
function createFoam() {
  const foam = new THREE.Group();

  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.35, 0.18, 8, 48), FOAM_MAT);
  ring.geometry.rotateX(Math.PI / 2);
  ring.position.set(0, 0.05, 0.2);
  ring.scale.set(1, 1, 1.15);
  foam.add(ring);

  const wakeMat = (op) =>
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: op, depthWrite: false });
  const w1 = new THREE.Mesh(new THREE.SphereGeometry(0.5, 12, 8), wakeMat(0.3));
  w1.scale.set(1.7, 0.18, 0.55);
  w1.position.set(0, 0.06, -3.1);
  const w2 = new THREE.Mesh(new THREE.SphereGeometry(0.5, 12, 8), wakeMat(0.16));
  w2.scale.set(2.1, 0.15, 0.55);
  w2.position.set(0, 0.06, -4.5);
  foam.add(w1, w2);

  // spray droplets kicked up at the nose
  const sprayMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75 });
  const spray = [];
  for (let i = 0; i < 16; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.05 + Math.random() * 0.08, 6, 5), sprayMat);
    m.position.set((Math.random() - 0.5) * 1.2, 0.2, 1.7 + Math.random() * 0.9);
    m.userData.phase = Math.random() * Math.PI * 2;
    spray.push(m);
    foam.add(m);
  }

  return { foam, ring, spray };
}

// ---- rider (board + pelican + foam), self-animating -----------------------
export function createRider() {
  const group = new THREE.Group();
  group.add(createBoard());

  const { bird, head, wingL, wingR, tail } = createBird();
  group.add(bird);

  const { foam, ring, spray } = createFoam();
  group.add(foam);

  function update(t) {
    // ride the wave: height + tilt from the local wave gradient
    const h = waveHeight(0, 0, t);
    const { hx, hz } = waveSlope(0, 0, t);
    group.position.y = h + 0.12;
    group.rotation.x = -Math.atan(hz) * 0.85;
    group.rotation.z = Math.atan(hx) * 0.85;
    group.rotation.y = 0.12 * Math.sin(t * 0.45); // gentle carving

    // wings: idle flap + an occasional big balance flap
    const flap = Math.sin(t * 2.4) * 0.1;
    const big = Math.pow(Math.max(0, Math.sin(t * 0.55 - 0.8)), 6) * 0.55;
    wingL.rotation.z = 0.25 + flap + big;
    wingR.rotation.z = -0.25 - flap - big;

    // head look-around
    head.rotation.y = Math.sin(t * 0.5) * 0.4;
    head.rotation.x = 0.08 * Math.sin(t * 0.9 + 1.3) - 0.05;

    // tail wag + body bob
    tail.rotation.x = 0.1 * Math.sin(t * 2.1);
    bird.position.y = 0.05 * Math.sin(t * 2.4 + 0.6);

    // foam pulse + spray
    const s = Math.sin(t * 2.0);
    ring.material.opacity = 0.35 + 0.12 * s;
    ring.scale.set(1 + 0.06 * s, 1, 1.15 + 0.06 * s);
    for (const p of spray) {
      p.position.y = 0.15 + 0.45 * (0.5 + 0.5 * Math.sin(t * 3.1 + p.userData.phase));
    }
  }

  return { group, update };
}
