import * as THREE from "three";
import { waveHeight } from "./waves.js";

// Low-poly faceted ocean. The surface is displaced on the CPU
// every frame; crest vertices get a foamy white vertex color.

export class Ocean {
  constructor(size = 140, segments = 96) {
    this.size = size;
    this.segments = segments;

    const geo = new THREE.PlaneGeometry(size, size, segments, segments);
    geo.rotateX(-Math.PI / 2); // work directly in XZ, Y = up
    this.base = geo.attributes.position.array.slice(); // rest positions

    // Vertex colors for foam on crests.
    const count = geo.attributes.position.count;
    this.colors = new Float32Array(count * 3);
    geo.setAttribute("color", new THREE.BufferAttribute(this.colors, 3));

    const mat = new THREE.MeshStandardMaterial({
      color: 0x1c7f9e,
      flatShading: true,
      vertexColors: true,
      roughness: 0.55,
      metalness: 0.05,
    });

    this.mesh = new THREE.Mesh(geo, mat);
    this.mesh.position.y = -0.6; // ride height offset for the board
  }

  update(t) {
    const pos = this.mesh.geometry.attributes.position;
    const arr = pos.array;
    const base = this.base;
    const colors = this.colors;

    const crest = 0.75; // height above which foam fades in
    const foamSpan = 0.9;

    for (let i = 0; i < pos.count; i++) {
      const ix = i * 3;
      const x = base[ix];
      const z = base[ix + 2];
      const h = waveHeight(x, z, t);
      arr[ix + 1] = h;

      // Foam intensity: whiter near wave crests.
      let f = (h - (crest - foamSpan)) / foamSpan;
      f = Math.max(0, Math.min(1, f));
      // A little noise so foam isn't a clean band.
      f *= 0.65 + 0.35 * Math.sin(x * 3.1 + z * 2.3 + t * 2.0);

      const cix = ix;
      colors[cix] = 0.11 + f * 0.85;
      colors[cix + 1] = 0.5 + f * 0.45;
      colors[cix + 2] = 0.62 + f * 0.36;
    }

    pos.needsUpdate = true;
    this.mesh.geometry.attributes.color.needsUpdate = true;
    this.mesh.geometry.computeVertexNormals();
  }
}
