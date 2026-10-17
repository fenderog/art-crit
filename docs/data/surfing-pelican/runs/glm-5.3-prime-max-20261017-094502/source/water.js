import * as THREE from 'three';

// Shared ocean wave function (also used to float the board, spray, camera...).
export function waveHeight(x, z, t) {
  return (
    1.35 * Math.sin(z * 0.10 - t * 0.75) + // main rolling swell
    0.45 * Math.sin(z * 0.23 - t * 1.35 + x * 0.06) + // secondary chop
    0.30 * Math.sin(x * 0.16 + t * 0.55) + // cross swell
    0.18 * Math.sin((x * 0.7 + z) * 0.14 + t * 1.05) // detail
  );
}

export function createWater() {
  const SIZE = 170;
  const SEGS = 110;
  const geometry = new THREE.PlaneGeometry(SIZE, SIZE, SEGS, SEGS);
  geometry.rotateX(-Math.PI / 2); // lie flat in XZ, displace Y

  const position = geometry.attributes.position;
  const count = position.count;
  const colors = new Float32Array(count * 3);
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  position.setUsage(THREE.DynamicDrawUsage);
  geometry.attributes.color.setUsage(THREE.DynamicDrawUsage);

  const material = new THREE.MeshStandardMaterial({
    vertexColors: true,
    flatShading: true, // derivative-based facet normals, no recompute needed
    roughness: 0.5,
    metalness: 0.05,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  const base = position.array.slice(); // static x/z of each vertex
  const deep = new THREE.Color('#0b5e78');
  const shallow = new THREE.Color('#31c3b0');
  const foam = new THREE.Color('#f4f9f7');
  const c = new THREE.Color();

  function update(t) {
    const p = position.array;
    for (let i = 0; i < count; i++) {
      const ix = i * 3;
      const x = base[ix];
      const z = base[ix + 2];
      const h = waveHeight(x, z, t);
      p[ix + 1] = h;
      // tint: deeper in troughs, lighter on rises, white foam on crests
      const hN = THREE.MathUtils.clamp(h * 0.42 + 0.5, 0, 1);
      c.copy(deep).lerp(shallow, hN);
      const f = THREE.MathUtils.smoothstep(h, 0.95, 1.45);
      if (f > 0) c.lerp(foam, f);
      colors[ix] = c.r;
      colors[ix + 1] = c.g;
      colors[ix + 2] = c.b;
    }
    position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
  }

  update(0);
  return { mesh, update };
}
