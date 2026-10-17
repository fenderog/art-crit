import * as THREE from "three";
import { waveHeight } from "./waves.js";

// Water-spray particle system trailing the surfboard.
// Simple particle pool with gravity, spawn at the board's tail.

export class Spray {
  constructor(count = 220) {
    this.count = count;
    this.positions = new Float32Array(count * 3);
    this.velocities = new Float32Array(count * 3);
    this.life = new Float32Array(count); // 0 = dead

    // Start everything dead, parked far below the sea.
    for (let i = 0; i < count; i++) {
      this.positions[i * 3 + 1] = -1000;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(this.positions, 3));

    // Round soft sprite generated in code.
    const sprite = makeDropTexture();
    const mat = new THREE.PointsMaterial({
      size: 0.28,
      map: sprite,
      transparent: true,
      depthWrite: false,
      color: 0xeafcff,
      opacity: 0.9,
    });

    this.points = new THREE.Points(geo, mat);
    this.next = 0;
    this.spawnAccumulator = 0;
  }

  spawn(x, y, z, dirX, speed) {
    const i = this.next;
    this.next = (this.next + 1) % this.count;
    const ix = i * 3;
    this.positions[ix] = x + (Math.random() - 0.5) * 0.5;
    this.positions[ix + 1] = y + Math.random() * 0.15;
    this.positions[ix + 2] = z + (Math.random() - 0.5) * 0.6;
    this.velocities[ix] = dirX * (1.2 + Math.random() * speed);
    this.velocities[ix + 1] = 1.4 + Math.random() * 2.2;
    this.velocities[ix + 2] = (Math.random() - 0.5) * 1.6;
    this.life[i] = 0.9 + Math.random() * 0.5;
  }

  update(dt, boardX, boardZ, boardDir, t) {
    // Emit from the board's tail at a steady rate.
    this.spawnAccumulator += dt * 60;
    while (this.spawnAccumulator > 0) {
      this.spawnAccumulator -= 1;
      const y = waveHeight(boardX, boardZ, t) - 0.55;
      this.spawn(boardX - boardDir * 1.3, y, boardZ, -boardDir, 1.5);
    }

    const g = 6.5;
    for (let i = 0; i < this.count; i++) {
      if (this.life[i] <= 0) continue;
      const ix = i * 3;
      this.life[i] -= dt;
      if (this.life[i] <= 0) {
        this.positions[ix + 1] = -1000;
        continue;
      }
      this.velocities[ix + 1] -= g * dt;
      this.positions[ix] += this.velocities[ix] * dt;
      this.positions[ix + 1] += this.velocities[ix + 1] * dt;
      this.positions[ix + 2] += this.velocities[ix + 2] * dt;
    }

    this.points.geometry.attributes.position.needsUpdate = true;
  }
}

function makeDropTexture() {
  const c = document.createElement("canvas");
  c.width = 32;
  c.height = 32;
  const ctx = c.getContext("2d");
  const grad = ctx.createRadialGradient(16, 16, 1, 16, 16, 15);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.5, "rgba(255,255,255,0.5)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 32, 32);
  const tex = new THREE.CanvasTexture(c);
  return tex;
}
