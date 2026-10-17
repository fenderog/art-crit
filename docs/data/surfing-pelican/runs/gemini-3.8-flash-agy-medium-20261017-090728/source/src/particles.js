import * as THREE from 'three';
import { createSprayParticleTexture } from './textures.js';

/**
 * High-performance Water Spray and Atmospheric Mist Particle Systems.
 * Simulates explosive surfboard carve spray, wave lip offshore blowback, and golden sun droplets.
 */
export class ParticleSystem {
  constructor() {
    this.group = new THREE.Group();
    this.group.name = 'ParticleSystem';

    this.particleTexture = createSprayParticleTexture();

    this.initSurfSpray();
    this.initLipBlowback();
    this.initAtmosphericDroplets();
  }

  // --- 1. SURFBOARD SPRAY PARTICLES ---
  initSurfSpray() {
    this.sprayCount = 800;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.sprayCount * 3);
    const velocities = new Float32Array(this.sprayCount * 3);
    const lives = new Float32Array(this.sprayCount);
    const maxLives = new Float32Array(this.sprayCount);
    const sizes = new Float32Array(this.sprayCount);

    for (let i = 0; i < this.sprayCount; i++) {
      // Initialize dormant
      positions[i * 3] = 0;
      positions[i * 3 + 1] = -100;
      positions[i * 3 + 2] = 0;

      velocities[i * 3] = 0;
      velocities[i * 3 + 1] = 0;
      velocities[i * 3 + 2] = 0;

      lives[i] = 0;
      maxLives[i] = 1.0;
      sizes[i] = 0.4 + Math.random() * 0.6;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geo.setAttribute('life', new THREE.BufferAttribute(lives, 1));
    geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.sprayMaterial = new THREE.PointsMaterial({
      size: 0.65,
      map: this.particleTexture,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      color: 0xe0f7fa // sparkling cyan-white
    });

    this.sprayPoints = new THREE.Points(geo, this.sprayMaterial);
    this.group.add(this.sprayPoints);

    this.sprayData = {
      positions,
      velocities,
      lives,
      maxLives,
      sizes,
      nextIdx: 0
    };
  }

  // Emit a burst of spray droplets from a board rail or tail fin
  emitSpray(origin, direction, count, speedScale = 1.0) {
    const { positions, velocities, lives, maxLives, sizes } = this.sprayData;

    for (let c = 0; c < count; c++) {
      const i = this.sprayData.nextIdx;
      this.sprayData.nextIdx = (this.sprayData.nextIdx + 1) % this.sprayCount;

      positions[i * 3] = origin.x + (Math.random() - 0.5) * 0.2;
      positions[i * 3 + 1] = origin.y + (Math.random() - 0.5) * 0.1;
      positions[i * 3 + 2] = origin.z + (Math.random() - 0.5) * 0.2;

      // Cone spray velocity
      const spread = 0.55;
      const speed = (6.0 + Math.random() * 10.0) * speedScale;

      velocities[i * 3] = (direction.x + (Math.random() - 0.5) * spread) * speed;
      velocities[i * 3 + 1] = (direction.y + 0.3 + Math.random() * 0.8) * speed * 0.8;
      velocities[i * 3 + 2] = (direction.z + (Math.random() - 0.5) * spread) * speed;

      lives[i] = 1.0;
      maxLives[i] = 0.6 + Math.random() * 0.6; // lifetime in seconds
      sizes[i] = 0.35 + Math.random() * 0.5;
    }
  }

  // --- 2. WAVE LIP BLOWBACK (WIND-BLOWN MIST) ---
  initLipBlowback() {
    this.lipMistCount = 500;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.lipMistCount * 3);
    const vels = new Float32Array(this.lipMistCount * 3);

    for (let i = 0; i < this.lipMistCount; i++) {
      // Spawn along the curling wave crest
      positions[i * 3] = 0.2 + (Math.random() - 0.5) * 2.0;
      positions[i * 3 + 1] = 8.5 + Math.random() * 1.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 60.0;

      // Wind blowing offshore (up and backwards)
      vels[i * 3] = -2.5 - Math.random() * 3.5;
      vels[i * 3 + 1] = 1.2 + Math.random() * 2.0;
      vels[i * 3 + 2] = (Math.random() - 0.5) * 1.5;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const mistMat = new THREE.PointsMaterial({
      size: 1.4,
      map: this.particleTexture,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      color: 0xfff3e0 // golden sunlight tint
    });

    this.lipMist = new THREE.Points(geo, mistMat);
    this.group.add(this.lipMist);
    this.lipMistVels = vels;
  }

  // --- 3. ATMOSPHERIC SUN DROPLETS (BOKEH SPARKLES) ---
  initAtmosphericDroplets() {
    this.bokehCount = 300;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.bokehCount * 3);

    for (let i = 0; i < this.bokehCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 35.0 + 5.0;
      positions[i * 3 + 1] = Math.random() * 12.0;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 40.0;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const bokehMat = new THREE.PointsMaterial({
      size: 0.8,
      map: this.particleTexture,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      color: 0xffecc4 // warm amber sunset sparkles
    });

    this.bokeh = new THREE.Points(geo, bokehMat);
    this.group.add(this.bokeh);
  }

  update(delta, surfboard) {
    // 1. UPDATE SURFBOARD SPRAY EMISSION
    if (surfboard && surfboard.physics) {
      const { sprayOrigins, physics } = surfboard;
      const { sprayIntensity, roll, carveAngle } = physics;

      // Rate of emission scales with carve speed and turns
      const numToEmit = Math.floor(sprayIntensity * 8);

      // Tail spray
      const tailDir = new THREE.Vector3(
        -carveAngle * 0.8,
        0.5,
        -1.2
      ).normalize();
      this.emitSpray(sprayOrigins.tailFin, tailDir, numToEmit, sprayIntensity * 0.7);

      // Rail carve spray (whichever rail is dug into the water)
      if (roll < -0.1) {
        // Digging inside rail
        const railDir = new THREE.Vector3(-0.9, 0.6, -0.4).normalize();
        this.emitSpray(sprayOrigins.leftRail, railDir, Math.floor(numToEmit * 1.2), sprayIntensity * 0.9);
      } else if (roll > 0.1) {
        // Outside rail spray
        const railDir = new THREE.Vector3(0.9, 0.6, -0.4).normalize();
        this.emitSpray(sprayOrigins.rightRail, railDir, Math.floor(numToEmit * 1.2), sprayIntensity * 0.9);
      }
    }

    // 2. SIMULATE ACTIVE SPRAY PARTICLES
    const { positions, velocities, lives, maxLives } = this.sprayData;
    const gravity = -14.0;
    const windX = -2.5;

    for (let i = 0; i < this.sprayCount; i++) {
      if (lives[i] > 0) {
        lives[i] -= delta / maxLives[i];

        if (lives[i] <= 0) {
          positions[i * 3 + 1] = -100; // recycle out of view
        } else {
          // Physics integration: velocity + gravity + wind
          velocities[i * 3] += windX * delta;
          velocities[i * 3 + 1] += gravity * delta;

          positions[i * 3] += velocities[i * 3] * delta;
          positions[i * 3 + 1] += velocities[i * 3 + 1] * delta;
          positions[i * 3 + 2] += velocities[i * 3 + 2] * delta;

          // Dissolve when touching water plane
          if (positions[i * 3 + 1] < 0.2) {
            lives[i] = 0;
            positions[i * 3 + 1] = -100;
          }
        }
      }
    }

    this.sprayPoints.geometry.attributes.position.needsUpdate = true;

    // 3. SIMULATE LIP MIST BLOWBACK
    if (this.lipMist && this.lipMistVels) {
      const mistPos = this.lipMist.geometry.attributes.position;
      for (let i = 0; i < this.lipMistCount; i++) {
        let x = mistPos.getX(i) + this.lipMistVels[i * 3] * delta;
        let y = mistPos.getY(i) + this.lipMistVels[i * 3 + 1] * delta;
        let z = mistPos.getZ(i) + this.lipMistVels[i * 3 + 2] * delta;

        // Reset if blown too far back or dispersed
        if (x < -12.0 || y > 15.0) {
          x = 0.5 + (Math.random() - 0.5) * 1.5;
          y = 8.5 + Math.random() * 1.2;
          z = (Math.random() - 0.5) * 60.0;
        }

        mistPos.setXYZ(i, x, y, z);
      }
      mistPos.needsUpdate = true;
    }

    // 4. ATMOSPHERIC BOKEH DRIFT
    if (this.bokeh) {
      const bPos = this.bokeh.geometry.attributes.position;
      for (let i = 0; i < this.bokehCount; i++) {
        let y = bPos.getY(i) + Math.sin(i + performance.now() * 0.001) * 0.006;
        let x = bPos.getX(i) - delta * 0.8;
        if (x < -15) x = 30;
        bPos.setXY(i, x, y);
      }
      bPos.needsUpdate = true;
    }
  }
}
