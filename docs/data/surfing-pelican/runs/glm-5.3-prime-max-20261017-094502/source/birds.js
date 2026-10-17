import * as THREE from 'three';

// Distant gulls circling on the breeze: tiny silhouettes with flapping wings.
export function createBirds() {
  const group = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: '#2c3a46', side: THREE.DoubleSide });

  const wingGeo = new THREE.BufferGeometry();
  wingGeo.setAttribute(
    'position',
    new THREE.Float32BufferAttribute([0, 0, -0.05, 1.15, 0.1, 0.32, 1.15, 0.1, -0.24], 3)
  );
  wingGeo.computeVertexNormals();

  const bodyGeo = new THREE.ConeGeometry(0.09, 0.6, 4);
  bodyGeo.rotateX(Math.PI / 2); // nose toward +Z

  const birds = [];
  for (let i = 0; i < 6; i++) {
    const b = new THREE.Group();
    b.add(new THREE.Mesh(bodyGeo, mat));
    const mkWing = (mirror) => {
      const pivot = new THREE.Group();
      const w = new THREE.Mesh(wingGeo, mat);
      if (mirror) w.rotation.y = Math.PI;
      pivot.add(w);
      b.add(pivot);
      return pivot;
    };
    const wr = mkWing(false);
    const wl = mkWing(true);
    b.scale.setScalar(0.7 + Math.random() * 0.8);
    group.add(b);
    birds.push({
      b,
      wr,
      wl,
      cx: (Math.random() - 0.5) * 60,
      cz: -25 - Math.random() * 70,
      r: 12 + Math.random() * 16,
      y: 6 + Math.random() * 8,
      w: (Math.random() < 0.5 ? -1 : 1) * (0.12 + Math.random() * 0.16),
      phase: Math.random() * Math.PI * 2,
      flap: 5.5 + Math.random() * 3,
    });
  }

  function update(t) {
    for (const d of birds) {
      const a = d.phase + t * d.w;
      d.b.position.set(
        d.cx + Math.cos(a) * d.r,
        d.y + Math.sin(t * 0.7 + d.phase) * 1.2,
        d.cz + Math.sin(a) * d.r
      );
      d.b.rotation.y = Math.atan2(-Math.sin(a) * d.w, Math.cos(a) * d.w);
      const f = Math.sin(t * d.flap + d.phase);
      d.b.rotation.z = f * 0.06;
      d.wr.rotation.z = f * 0.55;
      d.wl.rotation.z = -f * 0.55;
    }
  }

  return { group, update };
}
