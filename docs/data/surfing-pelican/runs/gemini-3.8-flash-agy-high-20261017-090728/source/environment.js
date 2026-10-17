import * as THREE from 'three';

/**
 * Creates atmospheric environment:
 * - Golden hour tropical sky dome
 * - Sun with radiant corona
 * - Directional sunlight and ambient ocean bounce lighting
 * - Distant volcanic island silhouettes
 * - Background flock of pelicans soaring in formation
 */
export class Environment {
  constructor(scene) {
    this.scene = scene;
    this.buildSky();
    this.buildLights();
    this.buildIslands();
    this.buildBackgroundFlock();
  }

  buildSky() {
    // Sky dome with procedural tropical sunset gradient
    const skyGeo = new THREE.SphereGeometry(300, 32, 24);
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');

    const grad = ctx.createLinearGradient(0, 0, 0, 512);
    grad.addColorStop(0.0, '#0c4a6e');  // Deep zenith blue
    grad.addColorStop(0.35, '#0284c7'); // Cyan sky
    grad.addColorStop(0.65, '#f97316'); // Golden-orange sunset band
    grad.addColorStop(0.85, '#fde047'); // Radiant horizon gold
    grad.addColorStop(1.0, '#082f49');  // Deep ocean floor

    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 512);

    const skyTex = new THREE.CanvasTexture(canvas);
    const skyMat = new THREE.MeshBasicMaterial({
      map: skyTex,
      side: THREE.BackSide,
      fog: false
    });

    this.skyMesh = new THREE.Mesh(skyGeo, skyMat);
    this.scene.add(this.skyMesh);

    // Radiant Sun sphere
    const sunGeo = new THREE.SphereGeometry(14, 16, 16);
    const sunMat = new THREE.MeshBasicMaterial({ color: 0xfffbeb });
    this.sunMesh = new THREE.Mesh(sunGeo, sunMat);
    this.sunMesh.position.set(-80, 55, 180);
    this.scene.add(this.sunMesh);

    // Sun Corona halo
    const coronaGeo = new THREE.PlaneGeometry(55, 55);
    const coronaCanvas = document.createElement('canvas');
    coronaCanvas.width = 128;
    coronaCanvas.height = 128;
    const cCtx = coronaCanvas.getContext('2d');
    const cGrad = cCtx.createRadialGradient(64, 64, 5, 64, 64, 64);
    cGrad.addColorStop(0.0, 'rgba(255, 255, 230, 0.9)');
    cGrad.addColorStop(0.4, 'rgba(255, 200, 100, 0.4)');
    cGrad.addColorStop(1.0, 'rgba(255, 150, 50, 0.0)');
    cCtx.fillStyle = cGrad;
    cCtx.fillRect(0, 0, 128, 128);

    const coronaTex = new THREE.CanvasTexture(coronaCanvas);
    const coronaMat = new THREE.MeshBasicMaterial({
      map: coronaTex,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    this.corona = new THREE.Mesh(coronaGeo, coronaMat);
    this.corona.position.copy(this.sunMesh.position);
    this.scene.add(this.corona);
  }

  buildLights() {
    // 1. Warm directional sun light (casts sharp shadows and highlights water)
    this.sunLight = new THREE.DirectionalLight(0xfffaed, 2.8);
    this.sunLight.position.set(-50, 45, 90);
    this.sunLight.castShadow = true;
    this.sunLight.shadow.mapSize.width = 2048;
    this.sunLight.shadow.mapSize.height = 2048;
    this.sunLight.shadow.camera.near = 5;
    this.sunLight.shadow.camera.far = 160;
    this.sunLight.shadow.camera.left = -25;
    this.sunLight.shadow.camera.right = 25;
    this.sunLight.shadow.camera.top = 25;
    this.sunLight.shadow.camera.bottom = -25;
    this.sunLight.shadow.bias = -0.0005;
    this.scene.add(this.sunLight);

    // 2. Turquoise ocean ambient fill light (simulates bounce off tropical water)
    this.hemiLight = new THREE.HemisphereLight(0xffeedd, 0x0284c7, 1.2);
    this.scene.add(this.hemiLight);

    // 3. Subtle tube backlight (illuminates the inside of the barrel tube)
    const tubeLight = new THREE.PointLight(0x00f0ff, 1.5, 45, 1.2);
    tubeLight.position.set(3.5, 4.0, 0);
    this.scene.add(tubeLight);
  }

  buildIslands() {
    this.islandGroup = new THREE.Group();
    this.scene.add(this.islandGroup);

    const islandMat = new THREE.MeshStandardMaterial({
      color: 0x164e63, // Deep tropical teal silhouette
      roughness: 0.9,
      metalness: 0.1
    });

    // Create 3 volcanic peaks on the horizon
    const peaks = [
      { x: -140, z: 220, r: 45, h: 32 },
      { x: -75, z: 240, r: 60, h: 48 },
      { x: 30, z: 230, r: 40, h: 26 }
    ];

    for (const p of peaks) {
      const geo = new THREE.ConeGeometry(p.r, p.h, 7);
      const mesh = new THREE.Mesh(geo, islandMat);
      mesh.position.set(p.x, p.h * 0.4 - 5, p.z);
      mesh.rotation.y = Math.random() * Math.PI;
      this.islandGroup.add(mesh);
    }
  }

  buildBackgroundFlock() {
    this.flockGroup = new THREE.Group();
    this.scene.add(this.flockGroup);

    // Flock of 5 pelicans gliding in V-formation in the distance
    this.flockBirds = [];
    const birdGeo = new THREE.BufferGeometry();
    // V-shaped wing mesh
    const vertices = new Float32Array([
      0, 0, 0.4,     // Beak tip
      -1.2, 0, -0.2, // Left wing tip
      0, 0, -0.4,    // Tail
      0, 0, 0.4,     // Beak
      0, 0, -0.4,    // Tail
      1.2, 0, -0.2   // Right wing tip
    ]);
    birdGeo.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    birdGeo.computeVertexNormals();

    const birdMat = new THREE.MeshBasicMaterial({
      color: 0x0c4a6e,
      side: THREE.DoubleSide
    });

    const offsets = [
      { x: 0, z: 0, y: 0 },
      { x: -4, z: -5, y: -0.5 },
      { x: 4, z: -5, y: 0.4 },
      { x: -8, z: -10, y: -0.8 },
      { x: 8, z: -10, y: 0.6 }
    ];

    for (let i = 0; i < offsets.length; i++) {
      const bird = new THREE.Mesh(birdGeo, birdMat);
      bird.position.set(offsets[i].x, offsets[i].y, offsets[i].z);
      bird.scale.setScalar(0.75);
      this.flockGroup.add(bird);
      this.flockBirds.push({
        mesh: bird,
        phase: i * 0.6
      });
    }

    this.flockGroup.position.set(-30, 24, 90);
  }

  update(time, camera) {
    if (this.corona && camera) {
      this.corona.lookAt(camera.position);
    }

    // Animate distant flock soaring and gliding
    if (this.flockGroup) {
      this.flockGroup.position.x = -80 + (time * 4.5) % 200;
      this.flockGroup.position.y = 22 + Math.sin(time * 0.4) * 2.0;

      for (const bird of this.flockBirds) {
        // Slow majestic wing flap
        const flap = Math.sin(time * 3.5 + bird.phase);
        bird.mesh.rotation.x = flap * 0.15;
      }
    }
  }
}
