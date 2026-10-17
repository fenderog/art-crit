import * as THREE from 'three';
import { createFoamNoiseTexture } from './textures.js';

/**
 * Parametric Peeling Barrel Wave and Dynamic Ocean System.
 * Constructs an authentic surfing pipeline with curling lip,
 * hollow barrel tube, steep wave face, churning white water, and ocean swells.
 */
export class WaveSystem {
  constructor() {
    this.group = new THREE.Group();
    this.group.name = 'WaveSystem';

    this.foamTexture = createFoamNoiseTexture();

    this.initMaterials();
    this.buildBarrelWave();
    this.buildOceanPlane();
    this.buildFoamLip();
    this.buildImpactZone();
  }

  initMaterials() {
    // Water shader / physical material with tropical translucent depth
    this.waterMat = new THREE.MeshPhysicalMaterial({
      color: 0x007799,         // tropical deep cyan/teal
      emissive: 0x002838,      // internal oceanic glow
      roughness: 0.15,
      metalness: 0.08,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      reflectivity: 0.9,
      transmission: 0.28,      // light penetrates thin barrel wall!
      thickness: 1.5,
      map: this.foamTexture
    });

    // Back of wave & deep swell material
    this.deepWaterMat = new THREE.MeshStandardMaterial({
      color: 0x034b6b,
      roughness: 0.25,
      metalness: 0.1
    });

    // Boiling white water / foam lip material
    this.foamMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.45,
      metalness: 0.02,
      map: this.foamTexture,
      transparent: true,
      opacity: 0.92
    });

    // Flat ocean floor / distant sea surface
    this.seaFloorMat = new THREE.MeshStandardMaterial({
      color: 0x013a52,
      roughness: 0.2,
      metalness: 0.15
    });
  }

  /**
   * Evaluates the wave 2D cross-section profile at normalized parameter u (0 to 1).
   * Returns {x, y, nx, ny} in wave local cross-section.
   */
  evalWaveProfile(u) {
    // u ranges from 0 (deep flat trough) to 1 (tip of curled pitching lip)
    let x, y;

    if (u < 0.3) {
      // Trough / base of wave (flat water transition)
      const t = u / 0.3;
      x = 12.0 - t * 4.5;
      y = 0.2 + Math.pow(t, 2.5) * 1.5;
    } else if (u < 0.65) {
      // Steepening wave face (the carve zone!)
      const t = (u - 0.3) / 0.35;
      x = 7.5 - t * 5.5; // X goes from 7.5 down to 2.0
      y = 1.7 + Math.sin(t * Math.PI * 0.5) * 5.2; // Y climbs from 1.7 to 6.9
    } else if (u < 0.85) {
      // Wave crest & start of lip throw
      const t = (u - 0.65) / 0.2;
      x = 2.0 - Math.sin(t * Math.PI * 0.5) * 1.8 + (t * 0.8); // Arching over
      y = 6.9 + Math.sin(t * Math.PI * 0.45) * 2.2; // Peak height ~9.1
    } else {
      // Curled falling lip pitching downward into the barrel
      const t = (u - 0.85) / 0.15;
      const angle = t * Math.PI * 0.75;
      x = 1.0 + Math.sin(angle) * 3.2; // throws forward into the trough
      y = 9.1 - (1.0 - Math.cos(angle)) * 3.8; // drops down to ~5.3
    }

    return { x, y };
  }

  buildBarrelWave() {
    // Construct high-density parametric mesh along profile (U) and wave length (V)
    const segU = 70; // along the wave curve
    const segV = 80; // down the wave line (Z)
    const lengthZ = 70; // length of wave wall

    const geo = new THREE.BufferGeometry();
    const positions = [];
    const normals = [];
    const uvs = [];
    const indices = [];

    for (let j = 0; j <= segV; j++) {
      const v = j / segV;
      const z = (v - 0.5) * lengthZ;

      // Peeling angle: wave breaks progressively down the line (Z axis)
      const peelOffset = (v - 0.5) * 4.0;

      for (let i = 0; i <= segU; i++) {
        const u = i / segU;
        const profile = this.evalWaveProfile(u);

        // Apply peeling wave shape and subtle longitudinal swell variation
        const x = profile.x + peelOffset * 0.15;
        const y = profile.y + Math.sin(v * Math.PI * 3.0) * 0.25;

        positions.push(x, y, z);
        normals.push(0, 1, 0); // computed below
        uvs.push(u * 3.5, v * 12.0);
      }
    }

    for (let j = 0; j < segV; j++) {
      for (let i = 0; i < segU; i++) {
        const a = j * (segU + 1) + i;
        const b = (j + 1) * (segU + 1) + i;
        const c = (j + 1) * (segU + 1) + (i + 1);
        const d = j * (segU + 1) + (i + 1);

        indices.push(a, b, d);
        indices.push(b, c, d);
      }
    }

    geo.setIndex(indices);
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));

    geo.computeVertexNormals();

    this.waveMesh = new THREE.Mesh(geo, this.waterMat);
    this.waveMesh.receiveShadow = true;
    this.waveMesh.castShadow = true;
    this.group.add(this.waveMesh);

    // Save base positions for animated ripple distortion
    this.waveBasePositions = geo.attributes.position.clone();

    // BACK OF SWELL (Outer ocean slope behind the wave)
    const backGeo = new THREE.PlaneGeometry(16, lengthZ, 20, segV);
    backGeo.rotateY(Math.PI / 2);
    backGeo.rotateX(-Math.PI / 2);

    const backPos = backGeo.attributes.position;
    for (let k = 0; k < backPos.count; k++) {
      const bx = backPos.getX(k);
      const bz = backPos.getZ(k);
      // Slope down from crest back into the open sea
      const slope = Math.max(0, -bx / 14);
      backPos.setY(k, Math.max(0.2, 8.8 * (1.0 - slope)));
      backPos.setX(k, -Math.abs(bx));
    }
    backGeo.computeVertexNormals();

    const backMesh = new THREE.Mesh(backGeo, this.deepWaterMat);
    backMesh.position.set(0.5, 0, 0);
    this.group.add(backMesh);
  }

  buildFoamLip() {
    // High-energy churning foam ribbon along the curled wave lip
    const lengthZ = 70;
    const curvePoints = [];
    const segs = 60;

    for (let i = 0; i <= segs; i++) {
      const t = i / segs;
      const z = (t - 0.5) * lengthZ;
      const peelOffset = (t - 0.5) * 4.0;
      const profile = this.evalWaveProfile(0.96);
      curvePoints.push(new THREE.Vector3(profile.x + peelOffset * 0.15 + 0.1, profile.y + 0.1, z));
    }

    const lipCurve = new THREE.CatmullRomCurve3(curvePoints);
    const lipGeo = new THREE.TubeGeometry(lipCurve, 60, 0.45, 10, false);
    const lipMesh = new THREE.Mesh(lipGeo, this.foamMat);
    this.group.add(lipMesh);
    this.lipMesh = lipMesh;
  }

  buildImpactZone() {
    // Churning white water carpet where the falling lip impacts the trough
    const impactGeo = new THREE.PlaneGeometry(5.5, 65, 18, 50);
    impactGeo.rotateX(-Math.PI / 2);

    const pos = impactGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      // Boiling chop bumps
      const bump = Math.sin(x * 3.0) * Math.cos(z * 2.0) * 0.18;
      pos.setY(i, 0.4 + bump);
    }
    impactGeo.computeVertexNormals();

    const impactMesh = new THREE.Mesh(impactGeo, this.foamMat);
    impactMesh.position.set(4.2, 0, 0);
    this.group.add(impactMesh);
    this.impactMesh = impactMesh;
  }

  buildOceanPlane() {
    // Open ocean surface stretching out in front of the wave to the horizon
    const seaGeo = new THREE.PlaneGeometry(120, 160, 60, 80);
    seaGeo.rotateX(-Math.PI / 2);

    const seaMesh = new THREE.Mesh(seaGeo, this.seaFloorMat);
    seaMesh.position.set(45, 0.1, 0);
    seaMesh.receiveShadow = true;
    this.group.add(seaMesh);
    this.seaMesh = seaMesh;
  }

  /**
   * Samples wave height and surface slopes at world coordinate (x, z).
   * Enables surfboard and pelican to adhere organically to the wave face.
   */
  getSurfaceData(x, z) {
    // Approximate parametric mapping from X coordinate on the face
    // X goes from ~1.0 (inside tube) to ~10.0 (trough)
    let height = 0.3;
    let slopeX = 0;
    let slopeZ = 0;

    if (x < 1.2) {
      // Inside barrel
      height = 5.2 - (x - 1.0) * 2.5;
      slopeX = 1.2;
    } else if (x < 3.0) {
      // Pocket / steep wall
      const t = (x - 1.2) / 1.8;
      height = 6.8 - t * 3.5;
      slopeX = -1.1;
    } else if (x < 7.5) {
      // Main carving face
      const t = (x - 3.0) / 4.5;
      height = 3.3 - t * 2.2;
      slopeX = -0.55;
    } else {
      // Trough / shoulder
      height = Math.max(0.25, 1.1 - (x - 7.5) * 0.12);
      slopeX = -0.08;
    }

    // Add subtle rolling swell along Z
    const swell = Math.sin(z * 0.15) * 0.22;
    height += swell;
    slopeZ = Math.cos(z * 0.15) * 0.04;

    return { height, slopeX, slopeZ };
  }

  /**
   * Dynamic animation update: scrolls water UV foam streaks, applies wave ripples
   */
  update(time, delta) {
    // Scroll foam texture to simulate roaring water rushing up the face and lip
    if (this.foamTexture) {
      this.foamTexture.offset.x = (time * 0.35) % 1;
      this.foamTexture.offset.y = (time * 0.18) % 1;
    }

    // Gentle pulsing ripple across wave vertices
    if (this.waveMesh && this.waveBasePositions) {
      const pos = this.waveMesh.geometry.attributes.position;
      const base = this.waveBasePositions;
      const count = pos.count;

      for (let i = 0; i < count; i += 2) {
        const bx = base.getX(i);
        const by = base.getY(i);
        const bz = base.getZ(i);

        // Water surface chop and swell flow
        const ripple = Math.sin(bx * 0.8 + time * 4.0) * Math.cos(bz * 0.5 + time * 3.0) * 0.06;
        pos.setY(i, by + ripple);
      }
      pos.needsUpdate = true;
    }

    // Foam impact zone boiling motion
    if (this.impactMesh) {
      this.impactMesh.position.y = 0.05 + Math.sin(time * 6.0) * 0.03;
    }
  }
}
