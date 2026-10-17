import * as THREE from 'three';

/**
 * Autonomous Cinematic Camera Director.
 * Provides multiple cinematography angles tailored to professional surf films:
 * 1. Dynamic Chase Cam (action rail follow)
 * 2. Tube Barrel Cam (inside the hollow cylinder looking out)
 * 3. Water-Level Profile (telephoto water-skimming tracker)
 * 4. Hero Low-Angle (looking up at the crest and pelican silhouette)
 * 5. Sweeping Drone Arc (wide scenic composition)
 */
export class CameraDirector {
  constructor(camera, targetSubject) {
    this.camera = camera;
    this.subject = targetSubject; // the surfboard or pelican group

    this.modes = [
      {
        id: 'chase',
        name: 'Action Chase',
        offset: new THREE.Vector3(5.5, 2.2, -6.5),
        lookOffset: new THREE.Vector3(0, 1.2, 1.5),
        fov: 52
      },
      {
        id: 'barrel',
        name: 'Inside the Tube',
        offset: new THREE.Vector3(-1.8, 1.8, 4.8),
        lookOffset: new THREE.Vector3(0.5, 0.8, -1.0),
        fov: 58
      },
      {
        id: 'waterLevel',
        name: 'Water-Level Profile',
        offset: new THREE.Vector3(12.5, 0.8, 0.5),
        lookOffset: new THREE.Vector3(0, 1.0, 0),
        fov: 42
      },
      {
        id: 'hero',
        name: 'Hero Low-Angle',
        offset: new THREE.Vector3(6.0, -0.6, 5.0),
        lookOffset: new THREE.Vector3(-0.5, 1.8, -1.0),
        fov: 54
      },
      {
        id: 'drone',
        name: 'Sweeping Drone Arc',
        offset: new THREE.Vector3(14.0, 7.5, -9.0),
        lookOffset: new THREE.Vector3(0, 1.0, 0),
        fov: 46
      }
    ];

    this.currentModeIndex = 0;
    this.autoDirector = true;
    this.modeTimer = 0;
    this.switchInterval = 11.0; // Seconds between cinematic cuts

    // Interpolation state vectors
    this.currentCamPos = new THREE.Vector3().copy(this.camera.position);
    this.currentTargetPos = new THREE.Vector3();
    this.targetLook = new THREE.Vector3();
    this.dampedLook = new THREE.Vector3();

    // Handheld camera noise
    this.noisePhase = 0;
  }

  setMode(index) {
    this.currentModeIndex = index % this.modes.length;
    this.modeTimer = 0;
  }

  getCurrentMode() {
    return this.modes[this.currentModeIndex];
  }

  update(time, delta, surfPhysics) {
    // 1. AUTONOMOUS DIRECTOR TRANSITIONS
    if (this.autoDirector) {
      this.modeTimer += delta;
      if (this.modeTimer >= this.switchInterval) {
        this.modeTimer = 0;
        this.currentModeIndex = (this.currentModeIndex + 1) % this.modes.length;
      }
    }

    const mode = this.modes[this.currentModeIndex];
    const subjectPos = this.subject.position;

    // 2. CALCULATE TARGET CAMERA POSITION
    let desiredPos = new THREE.Vector3();

    if (mode.id === 'drone') {
      // Orbiting sweeping crane shot
      const orbitAngle = time * 0.15;
      const radius = 17.0;
      desiredPos.set(
        subjectPos.x + Math.cos(orbitAngle) * radius,
        subjectPos.y + 7.5 + Math.sin(time * 0.3) * 1.5,
        subjectPos.z + Math.sin(orbitAngle) * radius * 0.7
      );
    } else {
      // Subject-relative position with subtle dynamic lag
      desiredPos.copy(subjectPos).add(mode.offset);
    }

    // 3. HANDHELD CAMERA BREATHING & ACTION SHAKE
    this.noisePhase += delta * 2.0;
    const breatheX = Math.sin(this.noisePhase * 1.2) * 0.08;
    const breatheY = Math.cos(this.noisePhase * 1.5) * 0.06;

    // Add subtle camera shake during hard carves or high G-force
    const shakeIntensity = (surfPhysics ? surfPhysics.gForce - 1.0 : 0) * 0.12;
    const shakeX = (Math.random() - 0.5) * shakeIntensity;
    const shakeY = (Math.random() - 0.5) * shakeIntensity;

    desiredPos.x += breatheX + shakeX;
    desiredPos.y += breatheY + shakeY;

    // 4. SMOOTH CAMERA INTERPOLATION (Critically damped spring)
    const posLerpFactor = 1.0 - Math.exp(-4.5 * delta);
    this.currentCamPos.lerp(desiredPos, posLerpFactor);
    this.camera.position.copy(this.currentCamPos);

    // 5. SMOOTH TARGET TRACKING (LookAt)
    this.targetLook.copy(subjectPos).add(mode.lookOffset);
    const lookLerpFactor = 1.0 - Math.exp(-6.0 * delta);
    this.dampedLook.lerp(this.targetLook, lookLerpFactor);
    this.camera.lookAt(this.dampedLook);

    // Smooth FOV interpolation
    const currentFov = this.camera.fov;
    if (Math.abs(currentFov - mode.fov) > 0.1) {
      this.camera.fov += (mode.fov - currentFov) * 2.0 * delta;
      this.camera.updateProjectionMatrix();
    }
  }
}
