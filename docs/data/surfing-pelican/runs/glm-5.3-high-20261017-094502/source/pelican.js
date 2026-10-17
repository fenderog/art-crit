import * as THREE from "three";

// The star of the show: a pelican built entirely from primitives,
// crouched on a surfboard, wings out for balance, pouch wobbling.

const WHITE = 0xf7f3ea;
const BEAK = 0xf0a13a;
const POUCH = 0xe8734a;
const FEET = 0xd98a2b;
const BOARD = 0xff5a3c;

export class Pelican {
  constructor() {
    this.group = new THREE.Group(); // everything, incl. board
    this.rider = new THREE.Group(); // just the bird (bobs independently)
    this.group.add(this.rider);

    const body = new THREE.Group();
    this.rider.add(body);
    this.body = body;

    const matBody = new THREE.MeshStandardMaterial({
      color: WHITE,
      roughness: 0.8,
      flatShading: true,
    });
    const matDark = new THREE.MeshStandardMaterial({
      color: 0x2b2b33,
      roughness: 0.6,
    });
    const matBeak = new THREE.MeshStandardMaterial({
      color: BEAK,
      roughness: 0.55,
    });
    const matPouch = new THREE.MeshStandardMaterial({
      color: POUCH,
      roughness: 0.6,
    });
    const matFoot = new THREE.MeshStandardMaterial({ color: FEET, roughness: 0.7 });
    const matBoard = new THREE.MeshStandardMaterial({
      color: BOARD,
      roughness: 0.35,
      metalness: 0.1,
    });
    const matStripe = new THREE.MeshStandardMaterial({
      color: 0xfff4e0,
      roughness: 0.4,
    });

    // ---- Surfboard ----
    const board = new THREE.Group();
    board.position.y = 0.0;
    this.group.add(board);
    this.board = board;

    const deck = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), matBoard);
    deck.scale.set(2.3, 0.14, 0.62);
    board.add(deck);

    const stripe = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.05, 0.16), matStripe);
    stripe.position.y = 0.13;
    board.add(stripe);

    // Tail fin (skeg) of the surfboard.
    const skeg = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.5, 4), matBoard);
    skeg.position.set(-2.0, -0.2, 0);
    skeg.rotation.z = Math.PI / 2 + 0.35;
    board.add(skeg);

    // ---- Body ----
    const torso = new THREE.Mesh(new THREE.SphereGeometry(0.62, 18, 14), matBody);
    torso.scale.set(1.25, 0.85, 0.95);
    torso.rotation.z = 0.28; // leaning forward
    torso.position.set(0.1, 0.62, 0);
    body.add(torso);

    // Tail feathers.
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.85, 6), matBody);
    tail.position.set(-0.75, 0.58, 0);
    tail.rotation.z = -Math.PI / 2 - 0.35;
    body.add(tail);

    // ---- Neck ----
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.2, 0.85, 10), matBody);
    neck.position.set(0.62, 1.05, 0);
    neck.rotation.z = -0.45;
    body.add(neck);

    // ---- Head ----
    const head = new THREE.Group();
    head.position.set(0.98, 1.42, 0);
    body.add(head);
    this.head = head;

    const skull = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 12), matBody);
    skull.scale.set(1.15, 1, 0.95);
    head.add(skull);

    // Crest feathers.
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.3, 5), matBody);
    crest.position.set(-0.12, 0.24, 0);
    crest.rotation.z = 0.5;
    head.add(crest);

    // Eyes.
    const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8);
    const eyeL = new THREE.Mesh(eyeGeo, matDark);
    eyeL.position.set(0.15, 0.07, 0.16);
    head.add(eyeL);
    const eyeR = new THREE.Mesh(eyeGeo, matDark);
    eyeR.position.set(0.15, 0.07, -0.16);
    head.add(eyeR);

    // ---- Beak + pouch ----
    const beak = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.95, 8), matBeak);
    beak.rotation.z = -Math.PI / 2;
    beak.position.set(0.62, -0.02, 0);
    beak.scale.set(1, 1, 0.55);
    head.add(beak);

    this.pouch = new THREE.Mesh(new THREE.SphereGeometry(0.17, 12, 10), matPouch);
    this.pouch.position.set(0.5, -0.16, 0);
    this.pouch.scale.set(1.8, 0.7, 0.5);
    head.add(this.pouch);

    // ---- Wings ----
    const wingGeo = new THREE.BoxGeometry(0.95, 0.06, 0.55);
    const wingTipGeo = new THREE.BoxGeometry(0.5, 0.05, 0.4);

    this.wingL = new THREE.Group();
    this.wingL.position.set(0.05, 0.85, 0.35);
    const wl = new THREE.Mesh(wingGeo, matBody);
    wl.position.set(0.1, 0, 0.32);
    wl.rotation.y = 0.25;
    this.wingL.add(wl);
    const wlTip = new THREE.Mesh(wingTipGeo, matDark);
    wlTip.position.set(0.5, 0, 0.6);
    wlTip.rotation.y = 0.55;
    this.wingL.add(wlTip);
    body.add(this.wingL);

    this.wingR = new THREE.Group();
    this.wingR.position.set(0.05, 0.85, -0.35);
    const wr = new THREE.Mesh(wingGeo, matBody);
    wr.position.set(0.1, 0, -0.32);
    wr.rotation.y = -0.25;
    this.wingR.add(wr);
    const wrTip = new THREE.Mesh(wingTipGeo, matDark);
    wrTip.position.set(0.5, 0, -0.6);
    wrTip.rotation.y = -0.55;
    this.wingR.add(wrTip);
    body.add(this.wingR);

    // ---- Feet ----
    const footGeo = new THREE.BoxGeometry(0.42, 0.06, 0.2);
    const footL = new THREE.Mesh(footGeo, matFoot);
    footL.position.set(0.25, 0.12, 0.18);
    footL.rotation.z = 0.15;
    body.add(footL);
    const footR = new THREE.Mesh(footGeo, matFoot);
    footR.position.set(0.25, 0.12, -0.18);
    footR.rotation.z = 0.15;
    body.add(footR);
  }

  // h: wave height at the board, sx/sz: wave slopes, t: time.
  update(t, h, sx, sz) {
    // Board rides the wave surface.
    this.group.position.y = h - 0.5;
    this.group.rotation.z = -sx * 0.85 + Math.sin(t * 0.9) * 0.03;
    this.group.rotation.x = sz * 0.85;

    // Rider bobbing & carving.
    this.rider.position.y = Math.sin(t * 3.1) * 0.05;
    this.rider.rotation.y = Math.sin(t * 0.7) * 0.12;
    this.rider.rotation.z = Math.sin(t * 1.3) * 0.05;

    // Wing flap: mostly gliding, with a lazy oscillation.
    const flap = Math.sin(t * 2.2) * 0.35 + Math.sin(t * 4.7) * 0.1;
    this.wingL.rotation.x = -0.25 - flap;
    this.wingR.rotation.x = 0.25 + flap;

    // Head looks ahead, occasionally dips toward the water.
    const peek = Math.max(0, Math.sin(t * 0.5));
    this.head.rotation.z = -peek * 0.5;

    // Pouch jiggles in the wind.
    this.pouch.scale.set(1.8 + Math.sin(t * 6) * 0.08, 0.7, 0.5);
  }
}
