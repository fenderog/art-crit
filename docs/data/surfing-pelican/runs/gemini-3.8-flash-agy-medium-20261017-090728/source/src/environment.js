import * as THREE from 'three';

/**
 * Tropical Golden Hour Atmosphere, Lighting Rig, Sky Dome,
 * Distant Volcanic Island Silhouettes, and Soaring Seabirds.
 */
export class Environment {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'Environment';
    this.scene.add(this.group);

    this.initLighting();
    this.initSkyDome();
    this.initSun();
    this.initDistantIslands();
    this.initSeabirds();
  }

  initLighting() {
    // 1. Warm Golden Directional Sunlight
    this.sunLight = new THREE.DirectionalLight(0xfff1cc, 2.8);
    this.sunLight.position.set(-25, 22, -15);
    this.sunLight.castShadow = true;

    // High quality shadow configuration
    this.sunLight.shadow.mapSize.width = 2048;
    this.sunLight.shadow.mapSize.height = 2048;
    this.sunLight.shadow.camera.near = 5;
    this.sunLight.shadow.camera.far = 70;

    const d = 16;
    this.sunLight.shadow.camera.left = -d;
    this.sunLight.shadow.camera.right = d;
    this.sunLight.shadow.camera.top = d;
    this.sunLight.shadow.camera.bottom = -d;
    this.sunLight.shadow.bias = -0.0005;

    this.scene.add(this.sunLight);

    // 2. Tropical Hemisphere Ambient Light (Sky cyan vs Ocean aqua)
    this.hemiLight = new THREE.HemisphereLight(0x7dd3fc, 0x065f46, 1.3);
    this.scene.add(this.hemiLight);

    // 3. Golden Rim / Backlight for translucent wave wall and water spray
    this.rimLight = new THREE.DirectionalLight(0xf97316, 2.2);
    this.rimLight.position.set(20, 8, -25);
    this.scene.add(this.rimLight);

    // 4. Subtle fill light from the open shoulder
    this.fillLight = new THREE.DirectionalLight(0x38bdf8, 0.8);
    this.fillLight.position.set(15, 12, 20);
    this.scene.add(this.fillLight);
  }

  initSkyDome() {
    // Gradient Sky Dome with tropical golden-hour tones
    const skyGeo = new THREE.SphereGeometry(180, 32, 24);
    // Invert geometry to view from inside
    skyGeo.scale(-1, 1, 1);

    // Generate procedural sky texture with warm sunset gradient
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');

    const grad = ctx.createLinearGradient(0, 0, 0, 512);
    grad.addColorStop(0, '#0c2340');    // deep cobalt twilight zenith
    grad.addColorStop(0.35, '#0284c7'); // tropical cyan
    grad.addColorStop(0.65, '#f59e0b'); // amber sunset warmth
    grad.addColorStop(0.85, '#f97316'); // rich golden coral
    grad.addColorStop(0.96, '#ffedd5'); // brilliant horizon glare
    grad.addColorStop(1.0, '#38bdf8');  // water reflection blend

    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 512);

    const skyTexture = new THREE.CanvasTexture(canvas);
    skyTexture.wrapS = THREE.RepeatWrapping;
    skyTexture.wrapT = THREE.ClampToEdgeWrapping;

    const skyMat = new THREE.MeshBasicMaterial({
      map: skyTexture,
      depthWrite: false,
      fog: false
    });

    this.skyDome = new THREE.Mesh(skyGeo, skyMat);
    this.group.add(this.skyDome);
  }

  initSun() {
    const sunGroup = new THREE.Group();
    sunGroup.position.set(-75, 38, -60);
    this.group.add(sunGroup);

    // Sun core disc
    const sunGeo = new THREE.CircleGeometry(7.5, 32);
    const sunMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      depthWrite: false,
      transparent: true,
      opacity: 0.98
    });
    const sunMesh = new THREE.Mesh(sunGeo, sunMat);
    sunMesh.lookAt(0, 5, 0);
    sunGroup.add(sunMesh);

    // Golden corona glow halo
    const haloGeo = new THREE.CircleGeometry(22, 32);
    const haloCanvas = document.createElement('canvas');
    haloCanvas.width = 128;
    haloCanvas.height = 128;
    const hCtx = haloCanvas.getContext('2d');
    const hGrad = hCtx.createRadialGradient(64, 64, 10, 64, 64, 64);
    hGrad.addColorStop(0, 'rgba(255, 230, 150, 0.85)');
    hGrad.addColorStop(0.4, 'rgba(255, 160, 60, 0.45)');
    hGrad.addColorStop(1, 'rgba(255, 100, 20, 0)');
    hCtx.fillStyle = hGrad;
    hCtx.fillRect(0, 0, 128, 128);

    const haloTexture = new THREE.CanvasTexture(haloCanvas);
    const haloMat = new THREE.MeshBasicMaterial({
      map: haloTexture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const haloMesh = new THREE.Mesh(haloGeo, haloMat);
    haloMesh.lookAt(0, 5, 0);
    sunGroup.add(haloMesh);
  }

  initDistantIslands() {
    // Volcanic island silhouettes along the distant ocean horizon
    const islandMat = new THREE.MeshStandardMaterial({
      color: 0x0f2938, // misty dark cyan/slate silhouette
      roughness: 0.9,
      metalness: 0.1
    });

    const islandsGroup = new THREE.Group();
    islandsGroup.position.set(80, 0, -85);
    this.group.add(islandsGroup);

    // Jagged volcanic mountain peaks
    const peakConfigs = [
      { x: -35, z: 0, r: 16, h: 18 },
      { x: -12, z: -10, r: 24, h: 28 },
      { x: 15, z: 5, r: 20, h: 22 },
      { x: 42, z: -5, r: 15, h: 14 }
    ];

    peakConfigs.forEach(cfg => {
      const coneGeo = new THREE.ConeGeometry(cfg.r, cfg.h, 12);
      coneGeo.scale(1.4, 1.0, 0.8);
      const peak = new THREE.Mesh(coneGeo, islandMat);
      peak.position.set(cfg.x, cfg.h / 2 - 2, cfg.z);
      islandsGroup.add(peak);
    });

    // Silhouette palm trees on the lower island ridge
    const palmTrunkMat = new THREE.MeshBasicMaterial({ color: 0x091c28 });
    const palmFrondMat = new THREE.MeshBasicMaterial({ color: 0x091c28 });

    for (let p = 0; p < 14; p++) {
      const palm = new THREE.Group();
      const px = -25 + p * 4.5 + (Math.random() - 0.5) * 2;
      const pz = (Math.random() - 0.5) * 8;
      palm.position.set(px, 3.5 + Math.sin(p * 0.4) * 2.0, pz);

      // Curved trunk
      const trunkGeo = new THREE.CylinderGeometry(0.12, 0.22, 3.8, 6);
      trunkGeo.translate(0, 1.9, 0);
      const trunk = new THREE.Mesh(trunkGeo, palmTrunkMat);
      trunk.rotation.z = (Math.random() - 0.5) * 0.35;
      palm.add(trunk);

      // Palm fronds star
      for (let f = 0; f < 6; f++) {
        const frondGeo = new THREE.ConeGeometry(0.35, 1.8, 4);
        frondGeo.scale(1, 1, 0.2);
        frondGeo.translate(0, 0.9, 0);
        const frond = new THREE.Mesh(frondGeo, palmFrondMat);
        frond.position.set(0, 3.8, 0);
        frond.rotation.z = (f / 6) * Math.PI * 2;
        frond.rotation.x = 0.55;
        palm.add(frond);
      }

      islandsGroup.add(palm);
    }
  }

  initSeabirds() {
    // Soaring flock of distant seabirds gliding in the golden sky
    this.birds = [];
    const birdMat = new THREE.MeshBasicMaterial({ color: 0x1e293b, side: THREE.DoubleSide });

    const numBirds = 9;
    for (let i = 0; i < numBirds; i++) {
      const bird = new THREE.Group();

      // Swept wing geometry
      const wingShape = new THREE.Shape();
      wingShape.moveTo(0, 0);
      wingShape.lineTo(-0.8, -0.15);
      wingShape.lineTo(-1.6, 0.1);
      wingShape.lineTo(-0.4, 0.3);
      wingShape.closePath();

      const lWingGeo = new THREE.ShapeGeometry(wingShape);
      const lWing = new THREE.Mesh(lWingGeo, birdMat);
      lWing.rotation.x = Math.PI / 2;
      bird.add(lWing);

      // Mirror right wing
      const rWingGeo = lWingGeo.clone();
      rWingGeo.scale(-1, 1, 1);
      const rWing = new THREE.Mesh(rWingGeo, birdMat);
      rWing.rotation.x = Math.PI / 2;
      bird.add(rWing);

      // Bird body
      const bodyGeo = new THREE.ConeGeometry(0.12, 0.7, 6);
      bodyGeo.rotateX(Math.PI / 2);
      const bMesh = new THREE.Mesh(bodyGeo, birdMat);
      bird.add(bMesh);

      // Positioning in soaring echelon formation
      const offsetX = -10 + i * 4.0;
      const offsetY = 28 + (i % 3) * 3.5;
      const offsetZ = -35 + i * 2.5;
      bird.position.set(offsetX, offsetY, offsetZ);

      this.scene.add(bird);
      this.birds.push({
        group: bird,
        lWing,
        rWing,
        phase: i * 0.7,
        basePos: new THREE.Vector3(offsetX, offsetY, offsetZ),
        speed: 0.8 + Math.random() * 0.4
      });
    }
  }

  update(time, delta) {
    // Animate distant soaring seabirds
    for (const bird of this.birds) {
      // Gentle wing flap / glide cycle
      const flap = Math.sin(time * 3.5 * bird.speed + bird.phase);
      const wingAngle = flap > 0.3 ? (flap - 0.3) * 0.45 : -0.05;

      bird.lWing.rotation.y = wingAngle;
      bird.rWing.rotation.y = -wingAngle;

      // Flight trajectory circling in the distance
      const flightRadius = 38.0;
      const angle = time * 0.08 * bird.speed + bird.phase * 0.4;
      bird.group.position.x = bird.basePos.x + Math.sin(angle) * flightRadius;
      bird.group.position.z = bird.basePos.z + Math.cos(angle) * (flightRadius * 0.5);
      bird.group.position.y = bird.basePos.y + Math.sin(time * 0.5 + bird.phase) * 1.5;

      // Heading orientation
      bird.group.rotation.y = -angle - Math.PI / 2;
      bird.group.rotation.z = Math.sin(angle) * 0.2; // banking into turn
    }
  }
}
