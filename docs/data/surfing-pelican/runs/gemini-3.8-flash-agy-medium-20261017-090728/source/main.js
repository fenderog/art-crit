import * as THREE from 'three';
import { Pelican } from './src/pelican.js';
import { Surfboard } from './src/surfboard.js';
import { WaveSystem } from './src/wave.js';
import { ParticleSystem } from './src/particles.js';
import { Environment } from './src/environment.js';
import { CameraDirector } from './src/cameraDirector.js';
import { SurfAudio } from './src/sound.js';

/**
 * Main Application Entry Point:
 * Orchestrates 3D rendering pipeline, procedural animation loop, and user interface.
 */
class SurfingPelicanApp {
  constructor() {
    this.container = document.getElementById('canvas-container');

    this.initRenderer();
    this.initScene();
    this.initObjects();
    this.initCameraDirector();
    this.initAudio();
    this.initUI();
    this.initEvents();

    this.clock = new THREE.Clock();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Cinematic tone mapping & color correction
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;

    // Realistic soft shadows
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.appendChild(this.renderer.domElement);
  }

  initScene() {
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x0e3650, 0.007);
  }

  initObjects() {
    // 1. Atmosphere & Environment
    this.environment = new Environment(this.scene);

    // 2. Wave & Ocean Pipeline
    this.wave = new WaveSystem();
    this.scene.add(this.wave.group);

    // 3. Surfboard Rig
    this.surfboard = new Surfboard();
    this.scene.add(this.surfboard.group);

    // 4. Pelican Character (Mounted onto Surfboard)
    this.pelican = new Pelican();
    this.surfboard.boardMeshGroup.add(this.pelican.group);

    // 5. Water Spray & Particle Effects
    this.particles = new ParticleSystem();
    this.scene.add(this.particles.group);
  }

  initCameraDirector() {
    this.camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      500
    );
    this.camera.position.set(10, 4, -8);

    // Track the surfboard
    this.cameraDirector = new CameraDirector(this.camera, this.surfboard.group);
  }

  initAudio() {
    this.audio = new SurfAudio();
  }

  initUI() {
    const camButtons = document.querySelectorAll('.cam-btn');
    camButtons.forEach((btn, idx) => {
      btn.addEventListener('click', () => {
        camButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        if (btn.dataset.mode === 'auto') {
          this.cameraDirector.autoDirector = true;
        } else {
          this.cameraDirector.autoDirector = false;
          const modeIndex = parseInt(btn.dataset.index, 10);
          this.cameraDirector.setMode(modeIndex);
        }
      });
    });

    const audioBtn = document.getElementById('audio-toggle');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        const playing = this.audio.toggle();
        if (playing) {
          audioBtn.classList.add('playing');
          audioBtn.innerHTML = '🔊 Surf Sound: On';
        } else {
          audioBtn.classList.remove('playing');
          audioBtn.innerHTML = '🔇 Surf Sound: Off';
        }
      });
    }

    // Update active camera button indicator during auto transitions
    this.camButtons = camButtons;
  }

  initEvents() {
    window.addEventListener('resize', () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    });
  }

  animate() {
    requestAnimationFrame(this.animate);

    const delta = Math.min(this.clock.getDelta(), 0.05); // clamp delta
    const time = this.clock.getElapsedTime();

    // 1. Update Surfboard Maneuvers & Physics
    const surfPhysics = this.surfboard.update(time, delta, this.wave);

    // 2. Update Pelican Biomechanical Animation
    this.pelican.update(time, delta, surfPhysics);

    // 3. Update Wave Surface Chop & UV Scrolling
    this.wave.update(time, delta);

    // 4. Update Particle Spray & Mist Systems
    this.particles.update(delta, this.surfboard);

    // 5. Update Distant Seabirds
    this.environment.update(time, delta);

    // 6. Update Autonomous Camera Director
    this.cameraDirector.update(time, delta, surfPhysics);

    // Sync UI badge if in auto mode
    if (this.cameraDirector.autoDirector && this.camButtons) {
      const currentIdx = this.cameraDirector.currentModeIndex;
      this.camButtons.forEach(btn => {
        if (btn.dataset.mode === 'auto') {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    // Render Scene
    this.renderer.render(this.scene, this.camera);
  }
}

// Initialize when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  new SurfingPelicanApp();
});
