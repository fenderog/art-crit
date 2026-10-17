import * as THREE from 'three';
import { createSprayParticleTexture } from './textures.js';
import { getWavePoint } from './wave.js';

/**
 * High-performance GPU particle system for surfboard rail spray, rooster tails,
 * and offshore wind wave mist. Zero GC garbage collection overhead.
 */
export class ParticleSystem {
  constructor(scene) {
    this.scene = scene;
    this.sprayTex = createSprayParticleTexture();

    this.initRailSpray();
    this.initLipMist();
  }

  initRailSpray() {
    this.maxSpray = 450;
    this.sprayGeo = new THREE.BufferGeometry();
    this.sprayPositions = new Float32Array(this.maxSpray * 3);
    this.sprayVelocities = new Float32Array(this.maxSpray * 3);
    this.sprayLives = new Float32Array(this.maxSpray); // 0 = dead, >0 = alive
    this.sprayMaxLives = new Float32Array(this.maxSpray);

    for (let i = 0; i < this.maxSpray; i++) {
      this.sprayLives[i] = 0;
      this.sprayPositions[i * 3 + 1] = -100; // Hidden initially
    }

    this.sprayGeo.setAttribute('position', new THREE.BufferAttribute(this.sprayPositions, 3));

    this.sprayMat = new THREE.PointsMaterial({
      size: 0.5,
      map: this.sprayTex,
      transparent: true,
      opacity: 0.75,
      blending: THREE.NormalBlending,
      depthWrite: false,
      color: 0xe0f7ff
    });

    this.sprayPoints = new THREE.Points(this.sprayGeo, this.sprayMat);
    this.scene.add(this.sprayPoints);
    this.nextSprayIdx = 0;
  }

  initLipMist() {
    this.maxMist = 300;
    this.mistGeo = new THREE.BufferGeometry();
    this.mistPositions = new Float32Array(this.maxMist * 3);
    this.mistVelocities = new Float32Array(this.maxMist * 3);
    this.mistLives = new Float32Array(this.maxMist);
    this.mistMaxLives = new Float32Array(this.maxMist);

    for (let i = 0; i < this.maxMist; i++) {
      this.mistLives[i] = 0;
      this.mistPositions[i * 3 + 1] = -100;
    }

    this.mistGeo.setAttribute('position', new THREE.BufferAttribute(this.mistPositions, 3));

    this.mistMat = new THREE.PointsMaterial({
      size: 1.1,
      map: this.sprayTex,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      color: 0xffffff
    });

    this.mistPoints = new THREE.Points(this.mistGeo, this.mistMat);
    this.scene.add(this.mistPoints);
    this.nextMistIdx = 0;
  }

  /**
   * Spawns spray particles from surfboard rails and fins
   * @param {THREE.Vector3} boardPos current surfboard world position
   * @param {THREE.Vector3} boardVel current surfboard velocity
   * @param {THREE.Vector3} sprayDir direction spray should eject
   * @param {number} intensity turn intensity (0 to 1)
   */
  emitRailSpray(boardPos, boardVel, sprayDir, intensity) {
    const count = Math.floor(2 + intensity * 8);

    for (let i = 0; i < count; i++) {
      const idx = this.nextSprayIdx;
      this.nextSprayIdx = (this.nextSprayIdx + 1) % this.maxSpray;

      // Position slightly behind and to the carving side of the board
      const jitter = (Math.random() - 0.5) * 0.3;
      this.sprayPositions[idx * 3] = boardPos.x + sprayDir.x * 0.2 + jitter;
      this.sprayPositions[idx * 3 + 1] = boardPos.y + 0.1;
      this.sprayPositions[idx * 3 + 2] = boardPos.z - 0.4 + jitter;

      // Velocity: ejected violently outward and upward, plus backward drag
      const speed = 3.5 + intensity * 6.5 + Math.random() * 2.0;
      this.sprayVelocities[idx * 3] = sprayDir.x * speed * 0.7 + (Math.random() - 0.5) * 1.5;
      this.sprayVelocities[idx * 3 + 1] = 2.0 + intensity * 5.0 + Math.random() * 2.5;
      this.sprayVelocities[idx * 3 + 2] = boardVel.z * 0.3 - 2.5 + (Math.random() - 0.5) * 1.0;

      const life = 0.5 + intensity * 0.5 + Math.random() * 0.3;
      this.sprayLives[idx] = life;
      this.sprayMaxLives[idx] = life;
    }
  }

  /**
   * Spawns offshore wind mist blown back from the crest
   */
  emitLipMist(time) {
    if (Math.random() > 0.4) return;

    const idx = this.nextMistIdx;
    this.nextMistIdx = (this.nextMistIdx + 1) % this.maxMist;

    // Pick a random location along the breaking crest
    const z = -25 + Math.random() * 45;
    const pt = getWavePoint(z, 0.78, time);

    this.mistPositions[idx * 3] = pt.x + (Math.random() - 0.5) * 0.4;
    this.mistPositions[idx * 3 + 1] = pt.y + (Math.random() - 0.5) * 0.2;
    this.mistPositions[idx * 3 + 2] = pt.z;

    // Blown back by offshore breeze (negative X, upward Y, drift down the line)
    this.mistVelocities[idx * 3] = -2.5 - Math.random() * 2.0;
    this.mistVelocities[idx * 3 + 1] = 1.0 + Math.random() * 1.5;
    this.mistVelocities[idx * 3 + 2] = 0.5 + (Math.random() - 0.5) * 1.0;

    const life = 1.2 + Math.random() * 0.8;
    this.mistLives[idx] = life;
    this.mistMaxLives[idx] = life;
  }

  update(dt, time) {
    const gravity = -9.8;

    // Update rail spray
    const sprayPos = this.sprayPositions;
    const sprayVel = this.sprayVelocities;
    for (let i = 0; i < this.maxSpray; i++) {
      if (this.sprayLives[i] > 0) {
        this.sprayLives[i] -= dt;
        if (this.sprayLives[i] <= 0) {
          sprayPos[i * 3 + 1] = -100; // Hide
          continue;
        }

        // Apply physics
        sprayVel[i * 3 + 1] += gravity * dt;
        sprayPos[i * 3] += sprayVel[i * 3] * dt;
        sprayPos[i * 3 + 1] += sprayVel[i * 3 + 1] * dt;
        sprayPos[i * 3 + 2] += sprayVel[i * 3 + 2] * dt;
      }
    }
    this.sprayGeo.attributes.position.needsUpdate = true;

    // Update lip mist
    this.emitLipMist(time);
    const mistPos = this.mistPositions;
    const mistVel = this.mistVelocities;
    for (let i = 0; i < this.maxMist; i++) {
      if (this.mistLives[i] > 0) {
        this.mistLives[i] -= dt;
        if (this.mistLives[i] <= 0) {
          mistPos[i * 3 + 1] = -100;
          continue;
        }

        // Gentle drag and upward drift
        mistPos[i * 3] += mistVel[i * 3] * dt;
        mistPos[i * 3 + 1] += mistVel[i * 3 + 1] * dt;
        mistPos[i * 3 + 2] += mistVel[i * 3 + 2] * dt;
        mistVel[i * 3 + 1] *= 0.98;
      }
    }
    this.mistGeo.attributes.position.needsUpdate = true;
  }
}
