import * as THREE from 'three';

// Sum-of-sines swell shared by the ocean mesh and everything that rides it.
export function waveHeight(x, z, t) {
  return (
    0.22 * Math.sin(0.35 * x + 1.2 * t) +
    0.16 * Math.sin(0.5 * z - 0.9 * t + 1.3) +
    0.09 * Math.sin(0.42 * (x + z) + 1.7 * t)
  );
}

export function createOcean() {
  const geo = new THREE.PlaneGeometry(90, 60, 110, 70);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const baseX = new Float32Array(pos.count);
  const baseZ = new Float32Array(pos.count);
  for (let i = 0; i < pos.count; i++) {
    baseX[i] = pos.getX(i);
    baseZ[i] = pos.getZ(i);
  }
  const mat = new THREE.MeshStandardMaterial({
    color: 0x2288cc,
    roughness: 0.32,
    metalness: 0.05,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.receiveShadow = true;

  function update(t) {
    for (let i = 0; i < pos.count; i++) {
      pos.setY(i, waveHeight(baseX[i], baseZ[i], t));
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
  }
  update(0);
  return { mesh, update };
}
