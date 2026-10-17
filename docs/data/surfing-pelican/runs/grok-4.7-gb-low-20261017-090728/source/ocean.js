import * as THREE from "three";
import { waveHeight } from "./wave.js";
import { SUN_DIR } from "./sky.js";

function smoothstep(edge0, edge1, x) {
  const t = THREE.MathUtils.clamp((x - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

export function createOcean() {
  const geo = new THREE.PlaneGeometry(100, 80, 180, 120);
  geo.rotateX(-Math.PI / 2);
  const colors = new Float32Array(geo.attributes.position.count * 3);
  geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  const material = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.3,
    metalness: 0.05,
    envMapIntensity: 0.65,
  });
  const mesh = new THREE.Mesh(geo, material);
  mesh.receiveShadow = true;
  mesh.castShadow = false;

  const deep = new THREE.Color("#074555");
  const mid = new THREE.Color("#148f9c");
  const lit = new THREE.Color("#7ed9cf");
  const foam = new THREE.Color("#f6f3ee");
  const glint = new THREE.Color("#fff4d8");
  const col = new THREE.Color();

  function update(t, originX) {
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) + originX;
      const z = pos.getZ(i);
      pos.setY(i, waveHeight(x, z, t));
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
    const nrm = geo.attributes.normal;
    for (let i = 0; i < pos.count; i++) {
      const h = pos.getY(i);
      const nx = nrm.getX(i);
      const ny = nrm.getY(i);
      const nz = nrm.getZ(i);
      const nd = Math.max(0, nx * SUN_DIR.x + ny * SUN_DIR.y + nz * SUN_DIR.z);
      const crest = smoothstep(0.95, 1.35, h);
      const foamAmt = crest;
      const mix = THREE.MathUtils.clamp(0.2 + (h + 0.4) * 0.38 + nd * 0.25, 0, 1);
      col.copy(deep).lerp(mid, mix);
      col.lerp(lit, nd * 0.4);
      col.lerp(foam, foamAmt);
      col.lerp(glint, Math.pow(nd, 64) * 0.9);
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }
    geo.attributes.color.needsUpdate = true;
  }

  return { mesh, update };
}
