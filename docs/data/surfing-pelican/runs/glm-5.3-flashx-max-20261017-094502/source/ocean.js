import * as THREE from "three";

/** Stylized wave field: sum of a few traveling sine waves. */
export function waveHeight(x, z, t) {
  return (
    0.55 * Math.sin(x * 0.28 + t * 1.05) +
    0.34 * Math.sin(z * 0.21 + t * 0.85 + 1.7) +
    0.22 * Math.sin((x + z) * 0.15 + t * 1.5) +
    0.12 * Math.sin(x * 0.52 - z * 0.3 + t * 1.9)
  );
}

/** Finite-difference gradient of the wave field at (x, z). */
export function waveSlope(x, z, t, e = 0.6) {
  const hx = (waveHeight(x + e, z, t) - waveHeight(x - e, z, t)) / (2 * e);
  const hz = (waveHeight(x, z + e, t) - waveHeight(x, z - e, t)) / (2 * e);
  return { hx, hz };
}

/** Animated low-poly ocean surface (CPU-displaced, flat shaded). */
export function createOcean() {
  const geo = new THREE.PlaneGeometry(170, 170, 150, 150);
  geo.rotateX(-Math.PI / 2);

  const mat = new THREE.MeshPhongMaterial({
    color: 0x0d7d99,
    specular: 0xbfeaf5,
    shininess: 70,
    flatShading: true,
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.receiveShadow = true;

  function update(t) {
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      pos.setY(i, waveHeight(pos.getX(i), pos.getZ(i), t));
    }
    pos.needsUpdate = true;
  }

  return { mesh, update };
}
