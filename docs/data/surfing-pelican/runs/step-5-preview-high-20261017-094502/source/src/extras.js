// extras.js — the rest of the world: a hazy island with a lighthouse, and
// three gulls drifting on the thermals.

import * as THREE from 'three';
import { plate, flattenXZ, mesh } from './geom.js';
import { PALETTE } from './uniforms.js';

const std = (color, roughness, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.0, ...extra });

function birdWingShape() {
  const s = new THREE.Shape();
  s.moveTo(0.04, 0.02);
  s.quadraticCurveTo(0.10, 0.42, -0.02, 0.82);
  s.quadraticCurveTo(-0.06, 0.84, -0.08, 0.78);
  s.quadraticCurveTo(0.02, 0.40, -0.02, 0.02);
  s.closePath();
  return s;
}

export function createIsland() {
  const group = new THREE.Group();
  group.position.set(-150, -9, 340);

  const rockMat = std(PALETTE.island, 1.0);
  const hill1 = mesh(new THREE.SphereGeometry(1, 24, 16), rockMat);
  hill1.scale.set(78, 34, 60);
  hill1.position.set(0, 20, 0);
  group.add(hill1);

  const hill2 = mesh(new THREE.SphereGeometry(1, 20, 14), rockMat);
  hill2.scale.set(46, 20, 40);
  hill2.position.set(62, 12, -22);
  group.add(hill2);

  const hill3 = mesh(new THREE.SphereGeometry(1, 18, 12), rockMat);
  hill3.scale.set(30, 26, 30);
  hill3.position.set(-46, 14, 18);
  group.add(hill3);

  // lighthouse on the near shoulder
  const towerMat = std(PALETTE.lighthouse, 0.9);
  const tower = mesh(new THREE.CylinderGeometry(2.6, 4.4, 16, 14), towerMat);
  tower.position.set(48, 24, 6);
  group.add(tower);

  const band = mesh(new THREE.CylinderGeometry(3.4, 3.4, 2.2, 14), std(0xc4483c, 0.9));
  band.position.set(48, 20, 6);
  group.add(band);

  const gallery = mesh(new THREE.CylinderGeometry(3.8, 3.8, 0.9, 14), towerMat);
  gallery.position.set(48, 32.6, 6);
  group.add(gallery);

  const lamp = mesh(
    new THREE.SphereGeometry(2.0, 14, 10),
    new THREE.MeshStandardMaterial({
      color: 0xfff0c0,
      emissive: new THREE.Color(PALETTE.lighthouseLight),
      emissiveIntensity: 0,
      roughness: 0.3,
      fog: false,
    }),
  );
  lamp.position.set(48, 33.8, 6);
  group.add(lamp);

  const roof = mesh(new THREE.ConeGeometry(3.4, 3.2, 14), std(0x3c4650, 0.9));
  roof.position.set(48, 36.6, 6);
  group.add(roof);

  group.update = (t) => {
    // a slow sweep of the light
    lamp.material.emissiveIntensity = Math.max(0, Math.sin(t * 1.9)) ** 8 * 4.0;
  };

  return group;
}

export function createBirds() {
  const group = new THREE.Group();
  const birds = [];
  const wingGeo = spanPlateTwisted(birdWingShape(), 0.03, 1, 14);
  const bodyGeo = new THREE.SphereGeometry(1, 12, 10);

  for (let i = 0; i < 3; i++) {
    const b = new THREE.Group();
    const body = mesh(bodyGeo, new THREE.MeshBasicMaterial({ color: PALETTE.bird, fog: true }));
    body.scale.set(0.16, 0.15, 0.5);
    b.add(body);
    const wings = [];
    for (const side of [1, -1]) {
      const pivot = new THREE.Group();
      const w = mesh(wingGeo, new THREE.MeshBasicMaterial({ color: PALETTE.bird, fog: true }));
      if (side < 0) w.scale.z = -1;
      pivot.add(w);
      b.add(pivot);
      wings.push({ pivot, side });
    }
    group.add(b);
    birds.push({
      group: b,
      wings,
      radius: 55 + i * 26,
      height: 20 + i * 7,
      speed: 0.055 + i * 0.016,
      phase: i * 2.1,
      flap: 1.2 + i * 0.4,
    });
  }

  return {
    group,
    /** keep the horizon-ish glow out of the way of the lighthouse */
    update(t) {
      const look = new THREE.Vector3();
      for (const b of birds) {
        const a = b.phase + t * b.speed;
        b.group.position.set(
          Math.cos(a) * b.radius,
          b.height + Math.sin(t * 0.21 + b.phase) * 3.2,
          Math.sin(a) * b.radius * 0.62 + 40,
        );
        // face along the tangent, bank into the turn
        look.set(
          b.group.position.x - Math.sin(a) * b.speed * 6,
          b.group.position.y,
          b.group.position.z + Math.cos(a) * b.speed * 3.6,
        );
        b.group.lookAt(look);
        b.group.rotateZ(0.5);
        const flap = Math.sin(t * b.flap * Math.PI * 2 + b.phase);
        for (const w of b.wings) {
          w.pivot.rotation.x = 0.5 * flap * w.side;
        }
      }
    },
  };
}

/** a bird wing: span along +Z, thin in Y */
function spanPlateTwisted(shape, thickness, side, segs) {
  return flattenXZ(plate(shape, thickness, segs));
}
