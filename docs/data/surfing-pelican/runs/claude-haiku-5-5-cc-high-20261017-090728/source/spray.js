import * as THREE from "three";
import { surfaceHeight } from "./ocean.js";

const COUNT = 320;
const GRAVITY = 6;
const EMIT_RATE = 90; // droplets per second

function dropletTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 64;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  gradient.addColorStop(0, "rgba(255,255,255,1)");
  gradient.addColorStop(0.45, "rgba(255,255,255,0.9)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(canvas);
}

// Pool of droplets thrown off the tail and rails and flung back over the wake.
export function createSpray() {
  const positions = new Float32Array(COUNT * 3).fill(-1000);
  const velocities = new Float32Array(COUNT * 3);
  const life = new Float32Array(COUNT);

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    map: dropletTexture(),
    size: 0.12,
    sizeAttenuation: true,
    transparent: true,
    depthWrite: false,
  });
  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;

  const local = new THREE.Vector3();
  let cursor = 0;
  let pending = 0;

  function spawn(board) {
    const i = cursor;
    cursor = (cursor + 1) % COUNT;

    if (Math.random() < 0.5) {
      local.set(-1.25, -0.04, (Math.random() - 0.5) * 0.4);
    } else {
      local.set(-1.1 + Math.random() * 1.2, -0.04, Math.random() < 0.5 ? -0.27 : 0.27);
    }
    board.localToWorld(local);

    positions.set([local.x, local.y, local.z], i * 3);
    velocities.set([-(1 + Math.random() * 1.6), 1.2 + Math.random() * 1.8, (Math.random() - 0.5) * 1.2], i * 3);
    life[i] = 0.9 + Math.random() * 0.5;
  }

  // The board's world matrix must be current before calling this.
  function update(dt, t, board) {
    pending += EMIT_RATE * dt;
    while (pending >= 1) {
      pending -= 1;
      spawn(board);
    }

    for (let i = 0; i < COUNT; i++) {
      if (life[i] <= 0) continue;
      const k = i * 3;
      life[i] -= dt;
      velocities[k + 1] -= GRAVITY * dt;
      positions[k] += velocities[k] * dt;
      positions[k + 1] += velocities[k + 1] * dt;
      positions[k + 2] += velocities[k + 2] * dt;
      if (life[i] <= 0 || positions[k + 1] < surfaceHeight(positions[k], positions[k + 2], t)) {
        life[i] = 0;
        positions[k + 1] = -1000;
      }
    }
    geometry.attributes.position.needsUpdate = true;
  }

  return { points, update };
}
