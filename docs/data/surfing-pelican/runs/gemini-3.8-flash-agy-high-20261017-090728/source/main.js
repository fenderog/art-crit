import * as THREE from 'three';
import { WaveSystem } from './wave.js';
import { ParticleSystem } from './particles.js';
import { SurfingPelican } from './pelican.js';
import { Environment } from './environment.js';
import { CameraDirector } from './camera.js';
import { toggleAudio, updateAudio, getAudioState } from './audio.js';

class SurfingApp {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.isPaused = false;
    this.lastTime = performance.now();
    this.elapsedTime = 0;

    this.initThree();
    this.initSceneObjects();
    this.initUI();
    this.onWindowResize();

    window.addEventListener('resize', () => this.onWindowResize());
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initThree() {
    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x0c4a6e, 0.0035);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 800);
    this.camera.position.set(-6, 3, -6);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    this.container.appendChild(this.renderer.domElement);

    // 4. Camera Director
    this.cameraDirector = new CameraDirector(this.camera, this.renderer.domElement);
  }

  initSceneObjects() {
    // 1. Sky, Sun, Lighting, Distant Islands & Flying Flock
    this.environment = new Environment(this.scene);

    // 2. Dynamic 3D Curling Barrel Wave & Whitewater
    this.waveSystem = new WaveSystem(this.scene);

    // 3. High-performance GPU Water Spray & Mist Particles
    this.particleSystem = new ParticleSystem(this.scene);

    // 4. The Star: Surfing Pelican & Retro Surfboard
    this.pelican = new SurfingPelican(this.scene);
  }

  initUI() {
    // Sound Toggle Button
    const btnSound = document.getElementById('btn-sound');
    const soundIcon = document.getElementById('sound-icon');
    const soundLabel = document.getElementById('sound-label');

    btnSound.addEventListener('click', () => {
      const active = toggleAudio();
      if (active) {
        soundIcon.textContent = '🔊';
        soundLabel.textContent = 'Sound: On';
        btnSound.classList.add('active');
      } else {
        soundIcon.textContent = '🔈';
        soundLabel.textContent = 'Sound: Off';
        btnSound.classList.remove('active');
      }
    });

    // Pause / Play Button
    const btnPause = document.getElementById('btn-pause');
    const pauseIcon = document.getElementById('pause-icon');
    const pauseLabel = document.getElementById('pause-label');

    btnPause.addEventListener('click', () => {
      this.isPaused = !this.isPaused;
      if (this.isPaused) {
        pauseIcon.textContent = '▶';
        pauseLabel.textContent = 'Play';
        btnPause.classList.add('active');
      } else {
        pauseIcon.textContent = '⏸';
        pauseLabel.textContent = 'Pause';
        btnPause.classList.remove('active');
      }
    });

    // Camera Mode Buttons
    const camButtons = document.querySelectorAll('.camera-btn');
    camButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        camButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.getAttribute('data-cam');
        this.cameraDirector.setMode(mode);
      });
    });

    // Telemetry display elements
    this.telemetryText = document.getElementById('telemetry-maneuver');
    this.meterFill = document.getElementById('meter-fill');
  }

  onWindowResize() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate() {
    requestAnimationFrame(this.animate);

    const now = performance.now();
    const delta = Math.min((now - this.lastTime) / 1000, 0.05);
    this.lastTime = now;

    if (!this.isPaused) {
      this.elapsedTime += delta;

      // 1. Update Surfing Pelican & Surfboard
      this.pelican.update(delta, this.elapsedTime, this.particleSystem, updateAudio);

      // 2. Update Dynamic Wave Swell & Whitewater
      this.waveSystem.update(this.elapsedTime, delta);

      // 3. Update Spray & Mist Particles
      this.particleSystem.update(delta, this.elapsedTime);

      // 4. Update Atmospheric Environment & Distant Flock
      this.environment.update(this.elapsedTime, this.camera);

      // 5. Update UI Telemetry
      if (this.telemetryText) {
        this.telemetryText.textContent = this.pelican.currentManeuver;
      }
      if (this.meterFill) {
        const percent = Math.min(100, Math.max(10, this.pelican.carveIntensity * 100));
        this.meterFill.style.width = `${percent}%`;
      }
    }

    // 6. Update Camera Director
    this.cameraDirector.update(delta, this.elapsedTime, this.pelican.root.position);

    // 7. Render Frame
    this.renderer.render(this.scene, this.camera);
  }
}

// Start application when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  new SurfingApp();
});
