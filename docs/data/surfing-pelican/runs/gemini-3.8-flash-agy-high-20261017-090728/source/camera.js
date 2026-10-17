import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/**
 * Cinematic Camera Director:
 * Smoothly tracks the surfing pelican with multiple action shot perspectives,
 * automatic director switching, and optional manual orbit controls.
 */
export class CameraDirector {
  constructor(camera, domElement) {
    this.camera = camera;
    this.domElement = domElement;

    this.mode = 'auto'; // 'auto', 'front', 'barrel', 'rail', 'drone', 'orbit'
    this.autoIndex = 0;
    this.autoTimer = 0;
    this.autoInterval = 9.0; // Seconds per shot in auto mode

    // Shot definitions (target relative offsets or world positions)
    this.shots = [
      {
        id: 'front',
        name: 'Action Cam',
        getOffset: () => new THREE.Vector3(-4.2, 1.8, -4.8),
        lookOffset: new THREE.Vector3(0, 0.4, 0),
        fov: 52
      },
      {
        id: 'barrel',
        name: 'Inside the Tube 🌊',
        getOffset: () => new THREE.Vector3(2.5, 0.8, -5.2),
        lookOffset: new THREE.Vector3(0, 0.2, 0),
        fov: 58
      },
      {
        id: 'rail',
        name: 'Water Rail Cam',
        getOffset: () => new THREE.Vector3(-2.8, 0.35, 1.8),
        lookOffset: new THREE.Vector3(0, 0.3, -0.6),
        fov: 50
      },
      {
        id: 'drone',
        name: 'Aerial Drone',
        getOffset: () => new THREE.Vector3(-8.5, 7.5, 7.0),
        lookOffset: new THREE.Vector3(0, 0.2, 0),
        fov: 48
      },
      {
        id: 'hero',
        name: 'Hero Close-Up',
        getOffset: () => new THREE.Vector3(-1.8, 0.65, -2.4),
        lookOffset: new THREE.Vector3(0, 0.6, 0),
        fov: 42
      }
    ];

    this.currentShot = this.shots[0];
    this.targetPos = new THREE.Vector3();
    this.camTarget = new THREE.Vector3();
    this.lookTarget = new THREE.Vector3();

    // Orbit controls for interactive exploration
    this.orbit = new OrbitControls(this.camera, this.domElement);
    this.orbit.enableDamping = true;
    this.orbit.dampingFactor = 0.05;
    this.orbit.maxDistance = 60;
    this.orbit.minDistance = 2;
    this.orbit.enabled = false;

    // Detect user interaction with orbit controls
    this.domElement.addEventListener('pointerdown', () => {
      if (this.mode === 'orbit') return;
      // Allow user to temporarily orbit without breaking auto unless switched
    });
  }

  setMode(modeId) {
    this.mode = modeId;
    if (modeId === 'orbit') {
      this.orbit.enabled = true;
      this.orbit.target.copy(this.targetPos);
    } else {
      this.orbit.enabled = false;
      const found = this.shots.find(s => s.id === modeId);
      if (found) {
        this.currentShot = found;
      }
    }
  }

  getModeName() {
    if (this.mode === 'orbit') return 'Free Orbit';
    if (this.mode === 'auto') return `Auto: ${this.currentShot.name}`;
    return this.currentShot.name;
  }

  update(dt, time, pelicanPos) {
    this.targetPos.copy(pelicanPos);

    if (this.mode === 'orbit') {
      this.orbit.target.lerp(this.targetPos, dt * 3.0);
      this.orbit.update();
      return;
    }

    // Auto Director shot cycler
    if (this.mode === 'auto') {
      this.autoTimer += dt;
      if (this.autoTimer > this.autoInterval) {
        this.autoTimer = 0;
        this.autoIndex = (this.autoIndex + 1) % this.shots.length;
        this.currentShot = this.shots[this.autoIndex];
      }
    }

    // Dynamic camera placement relative to pelican
    const baseOffset = this.currentShot.getOffset();

    // Add subtle ocean swell breathing to camera position
    const swellBob = Math.sin(time * 1.4) * 0.22;
    const swellSway = Math.cos(time * 0.9) * 0.18;

    const desiredCamPos = this.targetPos.clone().add(baseOffset).add(new THREE.Vector3(swellSway, swellBob, 0));
    const desiredLookPos = this.targetPos.clone().add(this.currentShot.lookOffset);

    // Smooth cinematic damping
    const followSpeed = this.mode === 'auto' && this.autoTimer < 1.2 ? 2.5 : 4.5;
    this.camTarget.lerp(desiredCamPos, dt * followSpeed);
    this.lookTarget.lerp(desiredLookPos, dt * (followSpeed * 1.2));

    this.camera.position.copy(this.camTarget);
    this.camera.lookAt(this.lookTarget);

    // Smooth FOV transitions
    if (Math.abs(this.camera.fov - this.currentShot.fov) > 0.1) {
      this.camera.fov += (this.currentShot.fov - this.camera.fov) * dt * 2.0;
      this.camera.updateProjectionMatrix();
    }
  }
}
