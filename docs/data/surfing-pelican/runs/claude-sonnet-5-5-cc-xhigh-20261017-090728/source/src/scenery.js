import * as THREE from "three";
import { SUN_DIR, PALETTE } from "./sky.js";
import { mulberry, clamp, lerp, smoothstep } from "./geo.js";

// ---------------------------------------------------------------------------
// A rocky headland far down the wave: the point the swell peels off, lost in haze.
export function createHeadland() {
  const rnd = mulberry(5);
  const noise2 = (() => {
    const g = new Float32Array(64 * 64).map(() => rnd());
    const at = (x, y) => g[((y & 63) << 6) | (x & 63)];
    return (x, y) => {
      const xi = Math.floor(x);
      const yi = Math.floor(y);
      const fx = x - xi;
      const fy = y - yi;
      const sx = fx * fx * (3 - 2 * fx);
      const sy = fy * fy * (3 - 2 * fy);
      return lerp(lerp(at(xi, yi), at(xi + 1, yi), sx), lerp(at(xi, yi + 1), at(xi + 1, yi + 1), sx), sy);
    };
  })();
  const fbm = (x, y) => {
    let s = 0;
    let a = 0.5;
    for (let i = 0; i < 5; i++) {
      s += a * noise2(x, y);
      x *= 2.07;
      y *= 2.07;
      a *= 0.5;
    }
    return s;
  };

  const NX = 120;
  const NZ = 56;
  const W = 2600; // along the coast
  const D = 900; // into the land
  const pos = [];
  const col = [];
  const idx = [];
  const hz = PALETTE.horizon.clone().lerp(PALETTE.horizonCool, 0.55);
  const rock = new THREE.Color("#4f6a58");
  const rock2 = new THREE.Color("#7b7466");
  const heightAt = (u, v) => {
    // u in [-1,1] along the coast, v in [0,1] inland: a broken ridge of low hills
    const bumps = 0.55 * Math.exp(-Math.pow((u + 0.1) * 2.6, 2)) + 0.4 * Math.exp(-Math.pow((u - 0.45) * 4.2, 2)) + 0.28 * Math.exp(-Math.pow((u + 0.62) * 5.0, 2));
    const land = smoothstep(0.0, 0.3, v) * (1 - 0.5 * smoothstep(0.5, 1.0, v));
    const edge = smoothstep(-1.0, -0.6, u) * smoothstep(1.0, 0.6, u);
    return (20 + 260 * bumps * land * (0.5 + 0.9 * fbm(u * 4 + 11, v * 3 + 5))) * edge + 5 * land;
  };
  for (let j = 0; j <= NZ; j++) {
    for (let i = 0; i <= NX; i++) {
      const u = (i / NX) * 2 - 1;
      const v = j / NZ;
      const h = heightAt(u, v) * (j === 0 ? 0 : 1);
      pos.push(u * W * 0.5, h - 4, -v * D);
      // faked lighting + atmosphere
      const e = 4 / NX;
      const hx = heightAt(u + e, v) - heightAt(u - e, v);
      const hz2 = heightAt(u, v + 0.02) - heightAt(u, v - 0.02);
      const n = new THREE.Vector3(-hx / (2 * e * W * 0.5), 1, hz2 / (0.04 * D)).normalize();
      const lit = clamp(n.dot(SUN_DIR) * 0.9 + 0.35, 0.1, 1.1);
      const c = rock.clone().lerp(rock2, clamp(fbm(u * 9, v * 9) * 1.6 - 0.2, 0, 1)).multiplyScalar(0.55 + lit * 0.7);
      c.lerp(hz, 0.5 + 0.2 * (1 - clamp(h / 260, 0, 1)));
      col.push(c.r, c.g, c.b);
    }
  }
  for (let j = 0; j < NZ; j++) {
    for (let i = 0; i < NX; i++) {
      const a = j * (NX + 1) + i;
      const b = a + 1;
      const c = a + NX + 1;
      const d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  geo.setIndex(idx);
  const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, fog: false }));
  mesh.frustumCulled = false;
  mesh.rotation.y = -Math.PI / 2; // coast runs along z, facing the wave
  mesh.position.set(-3300, 0, 40);
  return mesh;
}

// ---------------------------------------------------------------------------
// Gulls gliding in the distance.
function gullGeometry() {
  // body + head + wings are separate so the wings can flap
  const body = new THREE.SphereGeometry(1, 12, 8);
  body.scale(0.34, 0.1, 0.1);
  const head = new THREE.SphereGeometry(0.075, 8, 6);
  head.translate(0.34, 0.04, 0);
  const tail = new THREE.ConeGeometry(0.07, 0.24, 6);
  tail.rotateZ(Math.PI / 2);
  tail.translate(-0.42, 0, 0);
  const bill = new THREE.ConeGeometry(0.025, 0.1, 5);
  bill.rotateZ(-Math.PI / 2);
  bill.translate(0.46, 0.035, 0);
  return { body, head, tail, bill };
}

function wingGeometry(side) {
  const s = new THREE.Shape();
  s.moveTo(0, 0.0);
  s.lineTo(0.12, 0.2);
  s.quadraticCurveTo(0.2, 0.62, 0.0, 0.78);
  s.quadraticCurveTo(-0.16, 0.5, -0.2, 0.0);
  s.lineTo(0, 0);
  const g = new THREE.ShapeGeometry(s, 6);
  const p = g.attributes.position;
  const c = new Float32Array(p.count * 3);
  for (let i = 0; i < p.count; i++) {
    const t = p.getY(i) / 0.78;
    const k = smoothstep(0.55, 0.9, t);
    c[i * 3] = lerp(0.97, 0.12, k);
    c[i * 3 + 1] = lerp(0.97, 0.13, k);
    c[i * 3 + 2] = lerp(0.96, 0.15, k);
  }
  g.setAttribute("color", new THREE.BufferAttribute(c, 3));
  g.rotateX(Math.PI / 2); // lie flat: y (span) -> +z
  if (side < 0) g.scale(1, 1, -1);
  return g;
}

export function createGulls(count = 7) {
  const group = new THREE.Group();
  const white = new THREE.MeshStandardMaterial({ color: 0xf5f5f0, roughness: 0.8 });
  const dark = new THREE.MeshStandardMaterial({ color: 0xe6a63a, roughness: 0.6 });
  const wingMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide });
  const gg = gullGeometry();
  const wR = wingGeometry(1);
  const wL = wingGeometry(-1);
  const birds = [];
  const rnd = mulberry(21);
  for (let i = 0; i < count; i++) {
    const b = new THREE.Group();
    b.add(new THREE.Mesh(gg.body, white), new THREE.Mesh(gg.head, white), new THREE.Mesh(gg.tail, white), new THREE.Mesh(gg.bill, dark));
    const right = new THREE.Group();
    right.add(new THREE.Mesh(wR, wingMat));
    const left = new THREE.Group();
    left.add(new THREE.Mesh(wL, wingMat));
    right.position.set(0.04, 0.02, 0.06);
    left.position.set(0.04, 0.02, -0.06);
    b.add(right, left);
    const scale = 1.6 + rnd() * 1.4;
    b.scale.setScalar(scale);
    group.add(b);
    birds.push({
      b,
      right,
      left,
      cx: -40 + rnd() * 70,
      cz: 40 + rnd() * 90,
      r: 14 + rnd() * 30,
      y: 9 + rnd() * 24,
      w: (0.12 + rnd() * 0.1) * (rnd() < 0.5 ? 1 : -1),
      ph: rnd() * 6.28,
      flap: 1.6 + rnd() * 1.4,
    });
  }
  function update(t, ref) {
    for (const g of birds) {
      const a = g.ph + t * g.w;
      const x = ref.x + g.cx + Math.cos(a) * g.r;
      const z = g.cz + Math.sin(a) * g.r * 0.7;
      const y = g.y + 2 * Math.sin(t * 0.2 + g.ph);
      g.b.position.set(x, y, z);
      // face along the direction of travel
      const dx = -Math.sin(a) * g.w;
      const dz = Math.cos(a) * g.w * 0.7;
      g.b.rotation.set(0.15 * Math.sin(t * 0.4 + g.ph), Math.atan2(-dz, dx), -0.18 * Math.sign(g.w) * 1.0, "YXZ");
      // flap in bursts, then glide
      const burst = smoothstep(0.35, 0.6, 0.5 + 0.5 * Math.sin(t * 0.23 + g.ph * 2));
      const f = Math.sin(t * g.flap * 6.0 + g.ph) * (0.15 + 0.55 * burst) + 0.1 * (1 - burst);
      g.right.rotation.x = f;
      g.left.rotation.x = -f;
    }
  }
  return { group, update };
}
