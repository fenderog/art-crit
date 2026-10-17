import * as THREE from "three";

// Hazy headlands on the horizon.
export function createIslands() {
  const group = new THREE.Group();
  const defs = [
    { x: -520, z: -1100, sx: 420, sy: 85, sz: 120, c: 0x8a6f86, seed: 1 },
    { x: 360, z: -1250, sx: 520, sy: 60, sz: 140, c: 0x9a7d8a, seed: 2 },
    { x: -80, z: -1500, sx: 700, sy: 40, sz: 100, c: 0xb08f90, seed: 3 },
    { x: 1000, z: -900, sx: 260, sy: 70, sz: 90, c: 0x7f6a85, seed: 4 },
  ];
  for (const d of defs) {
    const geo = new THREE.IcosahedronGeometry(1, 4);
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i);
      const y = p.getY(i);
      const z = p.getZ(i);
      const n =
        Math.sin(x * 3.1 + d.seed) * 0.12 + Math.sin(x * 7.3 + z * 2 + d.seed * 2) * 0.06 + Math.sin(x * 15 + d.seed) * 0.025;
      p.setY(i, y > 0 ? y * (1 + n) : y * 0.4);
    }
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: d.c, fog: false }));
    m.scale.set(d.sx, d.sy, d.sz);
    m.position.set(d.x, -d.sy * 0.15, d.z);
    group.add(m);
  }
  return group;
}

// A few gulls wheeling about.
export function createGulls(count = 6) {
  const gulls = [];
  const group = new THREE.Group();
  const wingGeo = new THREE.BufferGeometry();
  wingGeo.setAttribute(
    "position",
    new THREE.Float32BufferAttribute([0, 0, 0.12, 0, 0, -0.1, 1.0, 0.02, -0.12, 0.55, 0, 0.1, 0, 0, 0.12, 1.0, 0.02, -0.12], 3)
  );
  wingGeo.setIndex([0, 1, 2, 0, 2, 5, 0, 5, 3]);
  wingGeo.computeVertexNormals();
  const matW = new THREE.MeshBasicMaterial({ color: 0xfff1de, side: THREE.DoubleSide, fog: false });
  const matBody = new THREE.MeshBasicMaterial({ color: 0xfff1de, fog: false });
  for (let i = 0; i < count; i++) {
    const g = new THREE.Group();
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 6), matBody);
    body.scale.set(0.8, 0.7, 2.2);
    g.add(body);
    const wl = new THREE.Mesh(wingGeo, matW);
    const wr = new THREE.Mesh(wingGeo, matW);
    wr.scale.x = -1;
    g.add(wl, wr);
    g.scale.setScalar(1.6);
    group.add(g);
    gulls.push({
      g, wl, wr,
      cx: -30 + i * 12 + Math.sin(i * 3.1) * 10,
      cz: -60 - (i % 3) * 25,
      r: 8 + (i % 4) * 5,
      h: 14 + (i * 7) % 11,
      sp: 0.18 + (i % 3) * 0.05,
      ph: i * 1.7,
    });
  }
  function update(t) {
    for (const b of gulls) {
      const a = t * b.sp + b.ph;
      const x = b.cx + Math.cos(a) * b.r;
      const z = b.cz + Math.sin(a) * b.r * 0.6;
      b.g.position.set(x, b.h + Math.sin(a * 1.7) * 1.5, z);
      const dx = -Math.sin(a) * b.r;
      const dz = Math.cos(a) * b.r * 0.6;
      b.g.rotation.y = Math.atan2(dx, dz);
      b.g.rotation.z = -0.35;
      const f = Math.sin(t * (4 + b.sp * 5) + b.ph) * 0.45;
      const glide = Math.sin(t * 0.3 + b.ph) > 0.4 ? 0.1 : 1;
      b.wl.rotation.z = f * glide + 0.1;
      b.wr.rotation.z = -(f * glide + 0.1);
    }
  }
  return { group, update };
}
