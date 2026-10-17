import * as THREE from "three";

const AMP = 1.2; // swell height: crest to trough is twice this
const K = 0.55; // swell wavenumber along x (wavelength ≈ 11.4)

// Static swell. The board rides the front face at x = z = 0, which is an inflection point
// (zero curvature), so a rigid board sits on the surface along its whole length.
export function swell(x, z) {
  const phase = K * x + Math.PI + 0.22 * Math.sin(0.45 * z) + 0.12 * Math.sin(1.1 * z);
  return AMP * (Math.sin(phase) + 0.25 * Math.sin(2 * phase));
}

// Small chop that flows backwards past the board (towards -x). This is what sells the ride.
export function ripples(x, z, t) {
  return (
    0.035 * Math.sin(3.2 * x + 1.8 * z + 4.2 * t) +
    0.025 * Math.sin(5.1 * x - 0.9 * z + 5.6 * t + 1.0) +
    0.018 * Math.sin(2.3 * x + 2.4 * z + 3.3 * t + 2.0)
  );
}

export function surfaceHeight(x, z, t) {
  return swell(x, z) + ripples(x, z, t);
}

const DEEP = new THREE.Color(0x0b3c5d);
const MID = new THREE.Color(0x1f7ea1);
const LIGHT = new THREE.Color(0x63cbd9);
const FOAM = new THREE.Color(0xf5fbff);

export function createOcean() {
  const geometry = new THREE.PlaneGeometry(50, 70, 200, 140);
  geometry.rotateX(-Math.PI / 2);
  geometry.translate(0, 0, -20); // z from -55 (horizon) to 15 (behind the camera)

  const position = geometry.attributes.position;
  const count = position.count;
  const baseHeight = new Float32Array(count);
  const foamBase = new Float32Array(count);

  // The swell never changes, so its height and foam mask are computed once.
  for (let i = 0; i < count; i++) {
    const x = position.getX(i);
    const z = position.getZ(i);
    const h = swell(x, z);
    const slope = (swell(x + 0.05, z) - swell(x - 0.05, z)) / 0.1;
    baseHeight[i] = h;
    foamBase[i] =
      THREE.MathUtils.smoothstep(h, 0.45 * AMP, 0.85 * AMP) +
      0.5 * THREE.MathUtils.smoothstep(-slope, 0.2, 0.5);
  }

  const colors = new Float32Array(count * 3);
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  const material = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.3, metalness: 0 });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  const color = new THREE.Color();

  function update(t) {
    for (let i = 0; i < count; i++) {
      const x = position.getX(i);
      const z = position.getZ(i);
      const rip = ripples(x, z, t);
      const h = baseHeight[i] + rip;
      position.setY(i, h);

      // Deep water to teal to light crest, with moving foam streaks where the ripples catch the face.
      const depth = THREE.MathUtils.clamp((h + AMP) / (2 * AMP), 0, 1);
      color.lerpColors(DEEP, MID, depth).lerp(LIGHT, depth * depth * depth * 0.7);
      color.lerp(FOAM, THREE.MathUtils.clamp(foamBase[i] * (1 + 4 * rip), 0, 1));
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }
    position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
    geometry.computeVertexNormals();
  }

  update(0);
  return { mesh, update };
}
