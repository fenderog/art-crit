// A squadron of pelicans gliding in a line past the break.

import * as THREE from 'three';

function wingGeometry() {
  // left wing in the xz plane, root at the origin, extending along +x
  const pts = [
    [0, 0.12], [0.35, 0.13], [0.7, 0.1], [0.95, 0.05], [1.12, -0.04],
    [1.05, -0.12], [0.85, -0.16], [0.5, -0.2], [0.2, -0.22], [0, -0.18],
  ];
  const shape = new THREE.Shape();
  shape.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) shape.lineTo(pts[i][0], pts[i][1]);
  const geo = new THREE.ShapeGeometry(shape);
  geo.rotateX(Math.PI / 2); // shape y -> +z: leading edge faces forward
  return geo;
}

function makeBird(mat) {
  const bird = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), mat);
  body.scale.set(0.16, 0.15, 0.48);
  bird.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), mat);
  head.scale.set(0.07, 0.07, 0.1);
  head.position.set(0, 0.06, 0.42);
  bird.add(head);
  const bill = new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.5, 8), mat);
  bill.rotation.x = Math.PI / 2 + 0.25;
  bill.position.set(0, -0.0, 0.7);
  bird.add(bill);
  const wings = [];
  const wg = wingGeometry();
  for (const s of [1, -1]) {
    const root = new THREE.Group();
    root.position.set(0.1 * s, 0.04, 0.05);
    root.scale.set(s * 1.25, 1, 1);
    const inner = new THREE.Group();
    const m = new THREE.Mesh(wg, mat);
    inner.add(m);
    root.add(inner);
    bird.add(root);
    wings.push(inner);
  }
  bird.userData.wings = wings;
  return bird;
}

export class Flock {
  constructor() {
    this.group = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: '#3b332e', roughness: 0.9, side: THREE.DoubleSide });
    this.birds = [];
    for (let i = 0; i < 6; i++) {
      const b = makeBird(mat);
      b.userData.i = i;
      this.group.add(b);
      this.birds.push(b);
    }
  }

  update(t) {
    const period = 70;
    const lead = 150 - ((t * 5.2 + 40) % (period * 5.2));
    for (const b of this.birds) {
      const i = b.userData.i;
      const x = lead + i * 3.4;
      const z = -48 - i * 2.2 + Math.sin(t * 0.13) * 6;
      const y = 10.5 + i * 0.25 + Math.sin(t * 0.6 + i * 0.5) * 0.5;
      b.position.set(x, y, z);
      // fly towards -x, gently banking
      b.rotation.set(0.05 * Math.sin(t * 0.6 + i), -Math.PI / 2, 0.08 * Math.sin(t * 0.4 + i * 0.3));
      // flap a few strokes, then glide (each bird a beat behind the one ahead)
      const c = (t * 1.0 - i * 0.18) % 6;
      const flapping = c < 2.2;
      const a = flapping ? Math.sin(c * Math.PI * 2 * 1.4) * 0.45 : 0.04 + 0.02 * Math.sin(t * 2 + i);
      for (const w of b.userData.wings) w.rotation.z = a;
    }
  }
}
