// Low-poly islands on the horizon, re-cycled as the surfer travels so the sea
// never runs out.

import * as THREE from 'three';
import { PALETTE } from './palette.js';

function hash(n) {
  const s = Math.sin(n * 127.1) * 43758.5453;
  return s - Math.floor(s);
}

function buildIsland(segments = 9) {
  const geo = new THREE.ConeGeometry(1, 1, segments, 4, false);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const y = pos.getY(i);
    const x = pos.getX(i);
    const z = pos.getZ(i);
    if (y < -0.49) continue; // leave the base cap alone
    const k = hash(i);
    const jitter = 1 + (k - 0.5) * 0.34;
    const lift = 1 + (hash(i + 91) - 0.5) * 0.28;
    pos.setX(i, x * jitter);
    pos.setZ(i, z * jitter);
    pos.setY(i, y * lift + (y > 0.4 ? 0.12 * hash(i + 7) : 0));
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  return geo;
}

const ISLANDS = [
  { ox: -1500, oz: -2400, s: 320, h: 130, ry: 0.4, tint: '#2c5a52' },
  { ox: 900, oz: -2000, s: 210, h: 90, ry: 1.9, tint: '#33635a' },
  { ox: 2100, oz: -2600, s: 420, h: 170, ry: 2.7, tint: '#28524b' },
  { ox: -2600, oz: -1500, s: 150, h: 62, ry: 0.9, tint: '#3a6b60' },
  { ox: 300, oz: -2900, s: 260, h: 105, ry: 3.4, tint: '#2a534c' },
  { ox: -600, oz: -3200, s: 520, h: 210, ry: 1.2, tint: '#234a45' },
];

const WRAP = 6000;

export function createIslands(scene) {
  const group = new THREE.Group();
  group.name = 'islands';
  scene.add(group);

  const items = ISLANDS.map((cfg) => {
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(cfg.tint),
      roughness: 1,
      metalness: 0,
      flatShading: true,
    });
    const m = new THREE.Mesh(buildIsland(9), mat);
    m.scale.set(cfg.s, cfg.h, cfg.s);
    m.position.set(cfg.ox, cfg.h * 0.5 - 8, cfg.oz);
    m.rotation.y = cfg.ry;
    group.add(m);
    return { mesh: m, cfg };
  });

  return {
    group,
    update(rider) {
      for (const it of items) {
        let x = it.cfg.ox;
        // wrap relative to the surfer so islands recycle smoothly
        while (x - rider.state.position.x > WRAP / 2) x -= WRAP;
        while (x - rider.state.position.x < -WRAP / 2) x += WRAP;
        it.mesh.position.x = x;
      }
    },
  };
}
