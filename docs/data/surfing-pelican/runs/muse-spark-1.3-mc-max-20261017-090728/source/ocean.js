import * as THREE from 'three';

// Animated ocean: a rolling swell the surfer rides, a curling breaker
// behind them, foam on its lip, whitewater at its foot, and a wake
// trailing the board. Everything is procedural geometry.

// Shared wave surface. Swell travels toward -X so the rider, facing +X,
// appears to move forward through the water.
export function waveHeight(x, z, t) {
  return (
    0.34 * Math.sin(x * 0.32 + t * 1.05) * Math.cos(z * 0.28 + t * 0.65) +
    0.17 * Math.sin(x * 0.66 - t * 1.5 + z * 0.42) +
    0.09 * Math.sin(z * 1.05 + t * 2.1 + x * 0.23)
  );
}

function smoothstep(a, b, x) {
  const t = THREE.MathUtils.clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}

// Deterministic pseudo-random so the foam layout is stable.
function mulberry32(seed) {
  let s = seed >>> 0;
  return () => {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let v = Math.imul(s ^ (s >>> 15), 1 | s);
    v = (v + Math.imul(v ^ (v >>> 7), 61 | v)) ^ v;
    return ((v ^ (v >>> 14)) >>> 0) / 4294967296;
  };
}

const FOAM_MAT = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9 });
const STREAK_MAT = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 1,
  transparent: true,
  opacity: 0.85,
});

const WAVE_POS = new THREE.Vector3(0, 2.3, -7);
const WAVE_W = 36;
const WAVE_H = 7.5;
const CURL = 4.3;

// Static curl of the breaker face: yn runs 0 (foot) to 1 (lip).
function curlOffset(bx, yn) {
  const s = smoothstep(0.3, 1.0, yn);
  return CURL * Math.pow(s, 1.6) * (1 + 0.06 * Math.sin(bx * 0.5));
}

export function createOcean(scene) {
  // --- Rolling swell ---
  const oceanGeo = new THREE.PlaneGeometry(170, 170, 100, 100);
  oceanGeo.rotateX(-Math.PI / 2);
  const ocean = new THREE.Mesh(
    oceanGeo,
    new THREE.MeshStandardMaterial({
      color: 0x1b6da3,
      roughness: 0.6,
      metalness: 0.05,
      flatShading: true,
    }),
  );
  ocean.receiveShadow = true;
  scene.add(ocean);
  const oceanPos = oceanGeo.attributes.position;

  // --- Far sea disc stretching to the horizon ---
  const farGeo = new THREE.CircleGeometry(400, 48);
  farGeo.rotateX(-Math.PI / 2);
  const far = new THREE.Mesh(
    farGeo,
    new THREE.MeshStandardMaterial({ color: 0x2e82ac, roughness: 1 }),
  );
  far.position.y = -0.45;
  scene.add(far);

  // --- Curling breaker ---
  const wallGeo = new THREE.PlaneGeometry(WAVE_W, WAVE_H, 64, 14);
  const wall = new THREE.Mesh(
    wallGeo,
    new THREE.MeshStandardMaterial({
      color: 0x1f9db4,
      roughness: 0.4,
      metalness: 0.05,
      transparent: true,
      opacity: 0.93,
      side: THREE.DoubleSide,
      flatShading: true,
    }),
  );
  wall.position.copy(WAVE_POS);
  wall.receiveShadow = true;
  scene.add(wall);
  const wallPos = wallGeo.attributes.position;
  const wallBase = wallPos.array.slice();

  // --- Foam: lip puffs, spilling puffs, whitewater, wake churn ---
  const rng = mulberry32(7);
  const puffGeo = new THREE.SphereGeometry(1, 8, 6);
  const puffs = []; // { m, bx, by, bz, sx, sy, sz, phase, kind }

  function addPuff(x, y, z, sx, sy, sz, kind) {
    const m = new THREE.Mesh(puffGeo, FOAM_MAT);
    m.position.set(x, y, z);
    m.scale.set(sx, sy, sz);
    scene.add(m);
    puffs.push({ m, bx: x, by: y, bz: z, sx, sy, sz, phase: rng() * Math.PI * 2, kind });
  }

  for (let i = 0; i < 30; i++) {
    const bx = -16.5 + (i * 33) / 29 + (rng() - 0.5) * 0.8;
    addPuff(
      bx,
      WAVE_POS.y + WAVE_H / 2 + (rng() - 0.5) * 0.4,
      WAVE_POS.z + curlOffset(bx, 1) + (rng() - 0.5) * 0.5,
      0.5 + rng() * 0.5,
      0.35 + rng() * 0.3,
      0.45 + rng() * 0.4,
      'lip',
    );
  }
  for (let i = 0; i < 16; i++) {
    const bx = -15 + rng() * 30;
    addPuff(
      bx,
      WAVE_POS.y + 2.6 + (rng() - 0.5) * 0.5,
      WAVE_POS.z + curlOffset(bx, 0.85) + 0.3,
      0.4 + rng() * 0.4,
      0.3 + rng() * 0.25,
      0.4 + rng() * 0.3,
      'spill',
    );
  }
  for (let i = 0; i < 14; i++) {
    addPuff(
      -16 + rng() * 32,
      0.5,
      -5.2 + rng() * 1.5,
      1.6 + rng(),
      0.22,
      0.9 + rng() * 0.5,
      'wash',
    );
  }
  for (let i = 0; i < 6; i++) {
    const s = 0.3 + rng() * 0.25;
    addPuff(-1.4 - rng() * 2.2, 0.2, (rng() - 0.5) * 0.6, s, s * 0.55, s, 'churn');
  }

  // --- Wake streaks fanning out behind the board ---
  const streaks = [];
  for (const side of [1, -1]) {
    const s = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.05, 0.4), STREAK_MAT);
    s.position.set(-3.2, 0.2, side * 0.85);
    s.rotation.y = side * 0.12;
    scene.add(s);
    streaks.push({ m: s, z: side * 0.85 });
  }

  function update(t) {
    // Swell follows the shared wave function.
    for (let i = 0; i < oceanPos.count; i++) {
      oceanPos.setY(i, waveHeight(oceanPos.getX(i), oceanPos.getZ(i), t));
    }
    oceanPos.needsUpdate = true;
    oceanGeo.computeVertexNormals();

    // Breaker face: static curl plus a lively ripple.
    for (let i = 0; i < wallPos.count; i++) {
      const bx = wallBase[i * 3];
      const by = wallBase[i * 3 + 1];
      const yn = (by + WAVE_H / 2) / WAVE_H;
      const ripple =
        0.14 * Math.sin(bx * 1.15 + t * 2.1) * yn + 0.08 * Math.sin(bx * 2.3 - t * 3.0) * yn;
      wallPos.setZ(i, curlOffset(bx, yn) + ripple);
      wallPos.setY(i, by + 0.12 * Math.sin(bx * 0.8 + t * 1.6) * yn);
    }
    wallPos.needsUpdate = true;
    wallGeo.computeVertexNormals();

    for (const p of puffs) {
      const w = 1 + 0.12 * Math.sin(t * 3.2 + p.phase);
      p.m.scale.set(p.sx * w, p.sy * (2 - w), p.sz * w);
      if (p.kind === 'lip') {
        p.m.position.y = p.by + 0.12 * Math.sin(t * 2.4 + p.phase * 1.3);
      } else if (p.kind === 'spill') {
        // Foam spilling down the face of the wave.
        const c = (t * 0.35 + p.phase) % 1;
        p.m.position.z = p.bz + c * 1.6;
        p.m.position.y = p.by - c * 1.1 + 0.06 * Math.sin(t * 5 + p.phase * 7);
      } else if (p.kind === 'wash') {
        // Whitewater drifting past with the current.
        let x = p.bx - t * 0.7;
        x = ((((x + 17) % 34) + 34) % 34) - 17;
        p.m.position.x = x;
        p.m.position.y = waveHeight(x, p.bz, t) + 0.15;
      } else {
        // Churn hugging the surface behind the board.
        p.m.position.y = waveHeight(p.bx, p.bz, t) + 0.12;
      }
    }

    for (const s of streaks) {
      s.m.position.y = waveHeight(-3.2, s.z, t) + 0.12;
    }
  }

  return { update };
}
