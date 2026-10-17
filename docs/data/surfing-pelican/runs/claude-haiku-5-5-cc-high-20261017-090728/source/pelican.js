import * as THREE from "three";

const COLORS = {
  white: 0xf4f1ea,
  wing: 0xbdb9ad,
  wingTip: 0x3a4048,
  bill: 0xe8ad4a,
  pouch: 0xf0953a,
  foot: 0xe8862e,
  tail: 0x9fa39a,
  eye: 0x1c2026,
};

const UP = new THREE.Vector3(0, 1, 0);
const SPHERE = new THREE.SphereGeometry(1, 24, 16);
const materials = new Map();

function material(color) {
  if (!materials.has(color)) {
    materials.set(color, new THREE.MeshStandardMaterial({ color, roughness: 0.55, side: THREE.DoubleSide }));
  }
  return materials.get(color);
}

function ellipsoid(center, radii, color, rotationZ = 0) {
  const mesh = new THREE.Mesh(SPHERE, material(color));
  mesh.position.set(...center);
  mesh.scale.set(...radii);
  mesh.rotation.z = rotationZ;
  return mesh;
}

// Sweeps an elliptical cross-section along a smooth curve. radii(u) returns [rx, ry] for u in 0..1.
function tubeMesh(points, radii, color, samples = 24, sides = 14) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
  const position = [];
  const index = [];
  const side = new THREE.Vector3();
  const up = new THREE.Vector3();

  for (let i = 0; i <= samples; i++) {
    const u = i / samples;
    const center = curve.getPointAt(u);
    const tangent = curve.getTangentAt(u);
    side.crossVectors(tangent, UP);
    if (side.lengthSq() < 1e-6) side.set(0, 0, 1);
    side.normalize();
    up.crossVectors(side, tangent).normalize();

    const [rx, ry] = radii(u);
    for (let j = 0; j < sides; j++) {
      const a = (j / sides) * Math.PI * 2;
      const c = Math.cos(a) * rx;
      const s = Math.sin(a) * ry;
      position.push(
        center.x + side.x * c + up.x * s,
        center.y + side.y * c + up.y * s,
        center.z + side.z * c + up.z * s
      );
    }
  }

  for (let i = 0; i < samples; i++) {
    for (let j = 0; j < sides; j++) {
      const a = i * sides + j;
      const b = i * sides + ((j + 1) % sides);
      const c = (i + 1) * sides + j;
      const d = (i + 1) * sides + ((j + 1) % sides);
      index.push(a, c, b, b, c, d);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(position, 3));
  geometry.setIndex(index);
  geometry.computeVertexNormals();
  return new THREE.Mesh(geometry, material(color));
}

// Flat feather-like plate in the XY plane, thickness along z.
function feather(points, depth) {
  const geometry = new THREE.ExtrudeGeometry(
    new THREE.Shape(points.map(([x, y]) => new THREE.Vector2(x, y))),
    { depth, bevelEnabled: true, bevelThickness: 0.008, bevelSize: 0.008, bevelSegments: 2, curveSegments: 12 }
  );
  geometry.translate(0, 0, -depth / 2);
  return geometry;
}

const WING_OUTLINE = new THREE.SplineCurve(
  [[-0.1, 0], [0.08, 0.05], [0.14, 0.3], [0.13, 0.6], [0.07, 0.86], [0, 1], [-0.08, 0.9], [-0.13, 0.62], [-0.15, 0.3], [-0.1, 0]].map(
    ([x, y]) => new THREE.Vector2(x, y)
  )
).getPoints(48);

const wingGeometry = feather(WING_OUTLINE.map((p) => [p.x, p.y]), 0.03);
const wingTipGeometry = feather(
  [[-0.13, 0.62], [0.12, 0.6], [0.07, 0.86], [0, 1], [-0.08, 0.9]],
  0.045
);

function createWing(side) {
  const pivot = new THREE.Group();
  pivot.position.set(0.05, 1.0, side * 0.18);
  pivot.add(new THREE.Mesh(wingGeometry, material(COLORS.wing)), new THREE.Mesh(wingTipGeometry, material(COLORS.wingTip)));
  return pivot;
}

const aimDirection = new THREE.Vector3();

// Points a wing (which extends along its local +y) in the given direction.
function aimWing(pivot, x, y, z) {
  pivot.quaternion.setFromUnitVectors(UP, aimDirection.set(x, y, z).normalize());
}

// Procedural pelican standing on a board, facing +x. The feet stay on the deck;
// the upper body sways over them and the wings flail for balance.
export function createPelican() {
  const root = new THREE.Group();
  const upper = new THREE.Group();
  root.add(upper);

  for (const z of [-0.1, 0.1]) {
    root.add(tubeMesh([[0, 0.62, z], [0.1, 0.36, z], [0.03, 0.1, z]], () => [0.035, 0.035], COLORS.foot, 12, 8));
    root.add(ellipsoid([0.08, 0.03, z], [0.2, 0.03, 0.12], COLORS.foot));
  }

  upper.add(ellipsoid([0, 0.82, 0], [0.46, 0.27, 0.26], COLORS.white, 0.16)); // body
  upper.add(ellipsoid([-0.5, 0.76, 0], [0.16, 0.05, 0.13], COLORS.tail, -0.35)); // tail
  upper.add(
    tubeMesh(
      [[0.3, 0.95, 0], [0.45, 1.16, 0], [0.52, 1.4, 0], [0.64, 1.6, 0], [0.78, 1.7, 0]],
      (u) => {
        const r = 0.15 - 0.06 * u;
        return [r, r * 0.9];
      },
      COLORS.white
    )
  );
  upper.add(ellipsoid([0.82, 1.74, 0], [0.15, 0.13, 0.125], COLORS.white)); // head
  upper.add(ellipsoid([0.9, 1.79, 0.11], [0.03, 0.03, 0.03], COLORS.eye)); // eye
  upper.add(
    tubeMesh(
      [[0.9, 1.76, 0], [1.1, 1.74, 0], [1.3, 1.69, 0], [1.42, 1.62, 0]],
      (u) => [0.05 - 0.02 * u, 0.03 - 0.015 * u],
      COLORS.bill
    )
  ); // bill
  upper.add(ellipsoid([1.1, 1.56, 0], [0.22, 0.12, 0.1], COLORS.pouch, -0.15)); // pouch

  const nearWing = createWing(1);
  const farWing = createWing(-1);
  upper.add(nearWing, farWing);

  function update(t) {
    upper.rotation.z = 0.05 * Math.sin(1.3 * t);
    upper.rotation.x = 0.04 * Math.sin(1.7 * t + 0.5);

    const flap = Math.sin(2.4 * t);
    aimWing(nearWing, 0.75, 0.6 + 0.12 * flap, 0.35);
    aimWing(farWing, -0.55, 0.85 - 0.1 * flap, -0.3);
  }

  return { root, update };
}
