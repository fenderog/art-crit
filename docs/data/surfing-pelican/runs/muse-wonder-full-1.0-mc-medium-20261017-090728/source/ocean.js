import * as THREE from "three";

/** Shared wave field: drives both the ocean mesh and the rider's motion. */
export function waveHeight(x, z, t) {
  return (
    0.42 * Math.sin(0.18 * x + t * 1.05) +
    0.34 * Math.sin(0.21 * z - t * 0.85 + 1.3) +
    0.2 * Math.sin(0.1 * (x + z) + t * 0.55) +
    0.12 * Math.sin(0.45 * x - 0.3 * z + t * 1.7)
  );
}

export function waveNormal(x, z, t) {
  const e = 0.35;
  const dx = waveHeight(x + e, z, t) - waveHeight(x - e, z, t);
  const dz = waveHeight(x, z + e, t) - waveHeight(x, z - e, t);
  return new THREE.Vector3(-dx / (2 * e), 1, -dz / (2 * e)).normalize();
}

export function createOcean() {
  const geo = new THREE.PlaneGeometry(140, 140, 88, 88);
  geo.rotateX(-Math.PI / 2);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x1593a8,
    roughness: 0.55,
    metalness: 0.05,
    flatShading: true,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.receiveShadow = true;
  const pos = geo.attributes.position;
  const base = pos.array.slice();

  function update(t) {
    for (let i = 0; i < pos.count; i++) {
      const x = base[i * 3];
      const z = base[i * 3 + 2];
      pos.setY(i, waveHeight(x, z, t));
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
  }
  update(0);
  return { mesh, update };
}

/** A curling barrel wave standing behind the rider, built from an open cylinder. */
export function createBarrel() {
  const group = new THREE.Group();
  const geo = new THREE.CylinderGeometry(6.2, 6.2, 48, 32, 1, true, 0.35, 3.67);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x1fb0b4,
    roughness: 0.35,
    metalness: 0.02,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.95,
    emissive: 0x0a4d5e,
  });
  const curl = new THREE.Mesh(geo, mat);
  // Lay the cylinder along X so its arc becomes a curl concave toward the rider.
  curl.rotation.z = Math.PI / 2;
  group.add(curl);

  // Foamy lip along the top edge of the curl: a crest tube dotted with foam.
  const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, flatShading: true, emissive: 0x667777 });
  for (let i = 0; i < 82; i++) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.13 + Math.random() * 0.17, 7, 6), foamMat);
    s.position.set(-23 + i * 0.57 + Math.random() * 0.25, 2.05 + Math.random() * 0.3, 5.85 + Math.random() * 0.25);
    s.scale.y = 0.65;
    group.add(s);
  }
  group.position.set(0, 3.0, -15);
  return group;
}
