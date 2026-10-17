// geom.js — small geometry helpers used to sculpt the bird and the board.

import * as THREE from 'three';

/**
 * A tube that can taper along its length (THREE.TubeGeometry cannot).
 * radiusFn(t) gives the radius at t=0..1 measured along the curve.
 */
export function taperedTube(curve, tubularSegments, radialSegments, radiusFn) {
  const frames = curve.computeFrenetFrames(tubularSegments, false);
  const position = [];
  const normal = [];
  const uv = [];
  const index = [];

  for (let i = 0; i <= tubularSegments; i++) {
    const t = i / tubularSegments;
    const P = curve.getPointAt(t);
    const N = frames.normals[i];
    const B = frames.binormals[i];
    const r = radiusFn(t);
    for (let j = 0; j <= radialSegments; j++) {
      const a = (j / radialSegments) * Math.PI * 2;
      const cv = Math.cos(a);
      const sv = Math.sin(a);
      const nx = cv * N.x + sv * B.x;
      const ny = cv * N.y + sv * B.y;
      const nz = cv * N.z + sv * B.z;
      position.push(P.x + r * nx, P.y + r * ny, P.z + r * nz);
      normal.push(nx, ny, nz);
      uv.push(j / radialSegments, t);
    }
  }
  for (let i = 0; i < tubularSegments; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const a = i * (radialSegments + 1) + j;
      const b = (i + 1) * (radialSegments + 1) + j;
      const c = (i + 1) * (radialSegments + 1) + j + 1;
      const d = i * (radialSegments + 1) + j + 1;
      index.push(a, b, d, b, c, d);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(position, 3));
  geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normal, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  geometry.setIndex(index);
  geometry.computeBoundingSphere();
  return geometry;
}

/** A thin extruded plate from a 2D outline, so it stays visible edge-on. */
export function plate(shape, thickness, curveSegments = 12) {
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: thickness,
    bevelEnabled: false,
    curveSegments,
  });
  geometry.translate(0, 0, -thickness / 2); // centre the thickness on z = 0
  geometry.computeVertexNormals();
  return geometry;
}

/** Lay a shape's XY plane flat on the ground, thickness along +Y. */
export function flattenXZ(geometry) {
  geometry.rotateX(-Math.PI / 2);
  geometry.computeVertexNormals();
  return geometry;
}

/** Make a plate stand vertically in the XZ frame, thickness along +X. */
export function faceForward(geometry) {
  geometry.rotateY(Math.PI / 2);
  geometry.computeVertexNormals();
  return geometry;
}

export function mesh(geometry, material) {
  const m = new THREE.Mesh(geometry, material);
  m.castShadow = false;
  m.receiveShadow = false;
  return m;
}
