import * as THREE from "three";

// Travelling swells. Each one moves toward +x, the way the surfer is facing.
const SWELLS = [
  { amp: 0.6, k: 0.5, speed: 1.4, dir: 0.0 },
  { amp: 0.18, k: 1.1, speed: 1.9, dir: 0.3 },
  { amp: 0.06, k: 2.2, speed: 2.4, dir: -0.5 },
];

export function waveHeight(x, z, t) {
  let h = 0;
  for (const s of SWELLS) {
    const phase = s.k * (x * Math.cos(s.dir) + z * Math.sin(s.dir)) - s.k * s.speed * t;
    h += s.amp * Math.sin(phase);
  }
  return h;
}

export function createOcean() {
  const geometry = new THREE.PlaneGeometry(70, 36, 140, 72);
  geometry.rotateX(-Math.PI / 2);

  const position = geometry.attributes.position;
  const rest = Float32Array.from(position.array);

  const material = new THREE.MeshStandardMaterial({
    color: 0x1b7fb0,
    roughness: 0.28,
    metalness: 0.02,
  });
  const mesh = new THREE.Mesh(geometry, material);

  function update(t) {
    for (let i = 0; i < position.count; i++) {
      position.setY(i, waveHeight(rest[i * 3], rest[i * 3 + 2], t));
    }
    position.needsUpdate = true;
    geometry.computeVertexNormals();
  }

  update(0);
  return { mesh, update };
}
