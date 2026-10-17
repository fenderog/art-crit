// A small escort of gulls wheeling around the surfer.

import * as THREE from 'three';
import { PALETTE } from './palette.js';

function buildGull() {
  const g = new THREE.Group();

  const bodyGeo = new THREE.ConeGeometry(0.16, 0.95, 7);
  bodyGeo.rotateX(Math.PI / 2); // point towards +z
  g.add(new THREE.Mesh(bodyGeo, gullMat()));

  const headGeo = new THREE.SphereGeometry(0.13, 10, 8);
  const head = new THREE.Mesh(headGeo, gullMat());
  head.position.set(0, 0.06, 0.42);
  g.add(head);

  const beakGeo = new THREE.ConeGeometry(0.045, 0.28, 5);
  beakGeo.rotateX(Math.PI / 2);
  const beak = new THREE.Mesh(beakGeo, gullMat());
  beak.position.set(0, 0.04, 0.66);
  g.add(beak);

  const tail = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.42, 4), gullMat());
  tail.rotation.x = -Math.PI / 2;
  tail.scale.set(0.4, 1, 1.5);
  tail.position.set(0, 0.02, -0.55);
  g.add(tail);

  // wings: two thin blades on pivots
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, 0);
  wingShape.quadraticCurveTo(0.55, 0.16, 1.15, 0.02);
  wingShape.quadraticCurveTo(0.6, -0.06, 0, -0.05);
  wingShape.lineTo(0, 0);
  const wingGeo = new THREE.ExtrudeGeometry(wingShape, {
    depth: 0.03,
    bevelEnabled: false,
    curveSegments: 10,
    steps: 1,
  });
  wingGeo.rotateX(Math.PI / 2);

  const wings = [];
  for (const sign of [1, -1]) {
    const pivot = new THREE.Group();
    pivot.position.set(0, 0.08, 0.05);
    const geo = sign > 0 ? wingGeo : wingGeo.clone();
    if (sign < 0) mirrorX(geo);
    pivot.add(new THREE.Mesh(geo, gullMat()));
    g.add(pivot);
    wings.push(pivot);
  }

  return { group: g, wings };
}

function mirrorX(geo) {
  const pos = geo.attributes.position;
  const nor = geo.attributes.normal;
  for (let i = 0; i < pos.count; i++) {
    pos.setX(i, -pos.getX(i));
    if (nor) nor.setX(i, -nor.getX(i));
  }
  pos.needsUpdate = true;
  if (nor) nor.needsUpdate = true;
}

let material;
function gullMat() {
  if (!material) {
    material = new THREE.MeshStandardMaterial({
      color: new THREE.Color(PALETTE.gull),
      roughness: 0.9,
      metalness: 0,
      flatShading: true,
      side: THREE.DoubleSide,
    });
  }
  return material;
}

const BIRDS = 5;

export function createFlock(scene) {
  const group = new THREE.Group();
  group.name = 'flock';
  scene.add(group);

  const birds = [];
  for (let i = 0; i < BIRDS; i++) {
    const bird = buildGull();
    group.add(bird.group);
    const rank = Math.floor(i / 2) + 1;
    const side = i % 2 === 0 ? -1 : 1;
    birds.push({
      ...bird,
      radius: 26 + rank * 16,
      offset: side * (rank * 5.5) + (i === 4 ? 0 : side * 1.5),
      lead: i === 4 ? 0 : -rank * 0.55,
      height: i === 4 ? 8.5 : 7.5 + Math.sin(i) * 1.4,
      phase: i * 0.9,
      speed: i === 4 ? 0.052 : 0.05 + rank * 0.004,
    });
  }

  const up = new THREE.Vector3();
  const fwd = new THREE.Vector3();
  const right = new THREE.Vector3();
  const pos = new THREE.Vector3();
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();

  return {
    group,
    update(t, rider) {
      const st = rider.state;
      up.copy(st.up);
      fwd.copy(st.forward);
      right.copy(st.right);

      for (const b of birds) {
        const a = t * b.speed * 6.0 + b.phase;
        const x = Math.cos(a) * b.radius + b.lead * 14.0;
        const z = Math.sin(a) * b.radius * 0.55 + b.offset * 6.0;
        pos
          .copy(right)
          .multiplyScalar(x)
          .addScaledVector(fwd, z)
          .addScaledVector(up, b.height + Math.sin(t * 0.8 + b.phase) * 1.2)
          .add(st.position);

        // face along the circle tangent
        const tx = -Math.sin(a) * b.radius;
        const tz = Math.cos(a) * b.radius * 0.55;
        const tan = right.clone().multiplyScalar(tx).addScaledVector(fwd, tz).normalize();
        const bank = new THREE.Vector3().crossVectors(up, tan).normalize();
        const newUp = new THREE.Vector3().crossVectors(tan, bank).normalize();
        m.makeBasis(bank, newUp, tan);
        q.setFromRotationMatrix(m);
        b.group.position.copy(pos);
        b.group.quaternion.copy(q);

        const flap = Math.sin(t * 7.5 + b.phase * 3.0);
        const idle = -0.15;
        b.wings[0].rotation.z = idle + flap * 0.55;
        b.wings[1].rotation.z = -(idle + flap * 0.55);
      }
    },
  };
}
