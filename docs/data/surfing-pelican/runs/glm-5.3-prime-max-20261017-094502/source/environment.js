import * as THREE from 'three';

function wrap(v, range) {
  const r = range * 2;
  return ((v % r) + r) % r - range;
}

// Distant islands + drifting low-poly clouds.
export function createEnvironment() {
  const group = new THREE.Group();

  // ---- islands ----
  const islandA = new THREE.MeshStandardMaterial({ color: '#41626d', flatShading: true, roughness: 1 });
  const islandB = new THREE.MeshStandardMaterial({ color: '#4a6d78', flatShading: true, roughness: 1 });
  const mkIsland = (x, z, s, mat) => {
    const g = new THREE.Group();
    const cone = (r, h, px, pz, m) => {
      const c = new THREE.Mesh(new THREE.ConeGeometry(r, h, 7), m);
      c.position.set(px, h * 0.5 - 1.6, pz);
      g.add(c);
    };
    cone(11 * s, 10 * s, 0, 0, mat);
    cone(7 * s, 6 * s, 9 * s, 4 * s, mat);
    cone(6 * s, 5 * s, -8 * s, 6 * s, islandB);
    g.position.set(x, -1.8, z);
    group.add(g);
  };
  mkIsland(-64, -80, 1.15, islandA);
  mkIsland(58, -98, 1.5, islandA);
  mkIsland(82, -24, 0.75, islandB);

  // ---- clouds (instanced puffs) ----
  const puffGeo = new THREE.SphereGeometry(1, 9, 7);
  const puffMat = new THREE.MeshStandardMaterial({ color: '#fdf6ec', flatShading: true, roughness: 1 });
  const CLOUDS = 7;
  const PER = 7;
  const N = CLOUDS * PER;
  const mesh = new THREE.InstancedMesh(puffGeo, puffMat, N);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

  const data = [];
  let idx = 0;
  for (let cl = 0; cl < CLOUDS; cl++) {
    const cx = (Math.random() - 0.5) * 160;
    const cz = -35 - Math.random() * 95;
    const cy = 16 + Math.random() * 13;
    const spd = 0.6 + Math.random() * 0.8;
    const base = 1.5 + Math.random() * 2.2;
    for (let p = 0; p < PER; p++, idx++) {
      data.push({
        cx,
        cy,
        cz,
        spd,
        ox: (Math.random() - 0.5) * 6.5 * base,
        oy: (Math.random() - 0.5) * 1.2 * base,
        oz: (Math.random() - 0.5) * 2.6 * base,
        s: (0.45 + Math.random() * 0.8) * base,
      });
    }
  }
  group.add(mesh);

  const dummy = new THREE.Object3D();
  function update(t) {
    for (let i = 0; i < N; i++) {
      const d = data[i];
      const x = wrap(d.cx + t * d.spd, 90);
      dummy.position.set(x + d.ox, d.cy + d.oy, d.cz + d.oz);
      dummy.scale.set(d.s, d.s * 0.55, d.s * 0.85);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  }
  update(0);

  return { group, update };
}
