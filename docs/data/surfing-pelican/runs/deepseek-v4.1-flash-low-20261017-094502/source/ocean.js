import * as THREE from 'three';
import { waveGLSL, waveHeight, waveNormal } from './waves.js';

// A large plane whose vertices are displaced on the GPU by a sum of sine
// waves. Lighting/normals are recomputed from the analytic wave normal.
export function createOcean() {
  const uniforms = { uTime: { value: 0 } };

  const geometry = new THREE.PlaneGeometry(400, 400, 400, 400);
  geometry.rotateX(-Math.PI / 2);

  const material = new THREE.MeshStandardMaterial({
    color: 0x1d6fa5,
    roughness: 0.22,
    metalness: 0.05,
  });

  material.onBeforeCompile = (shader) => {
    shader.uniforms.uTime = uniforms.uTime;
    shader.vertexShader = shader.vertexShader
      .replace(
        '#include <common>',
        `#include <common>\nuniform float uTime;\n${waveGLSL()}`
      )
      .replace(
        '#include <beginnormal_vertex>',
        '#include <beginnormal_vertex>\n  objectNormal = waveNormal(position.xz, uTime);'
      )
      .replace(
        '#include <begin_vertex>',
        '#include <begin_vertex>\n  transformed.y += waveHeight(transformed.xz, uTime);'
      );
  };

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.name = 'ocean';

  return {
    mesh,
    waveHeight,
    waveNormal,
    update(t) {
      uniforms.uTime.value = t;
    },
  };
}
