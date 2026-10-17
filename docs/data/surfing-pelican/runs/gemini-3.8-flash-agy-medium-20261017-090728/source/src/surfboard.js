import * as THREE from 'three';
import { createSurfboardDeckTexture } from './textures.js';

/**
 * High-performance sculpted surfboard with realistic hydrodynamics,
 * thruster fin setup, flexible leash cord, and dynamic wave-carving trajectory solver.
 */
export class Surfboard {
  constructor() {
    this.group = new THREE.Group();
    this.group.name = 'SurfboardRig';

    // Board container that rotates and rolls
    this.boardMeshGroup = new THREE.Group();
    this.group.add(this.boardMeshGroup);

    this.initMaterials();
    this.buildBoard();
    this.buildFins();
    this.buildLeash();

    // Physics & trajectory parameters
    this.physics = {
      carveAngle: 0,
      speed: 1.0,
      pitch: 0,
      roll: 0,
      yaw: 0,
      inBarrel: false,
      gForce: 1.0,
      sprayIntensity: 1.0,
      railContact: { left: 0.5, right: 0.5 }
    };

    // Tracking world positions for spray emitters
    this.sprayOrigins = {
      leftRail: new THREE.Vector3(),
      rightRail: new THREE.Vector3(),
      tailFin: new THREE.Vector3()
    };
  }

  initMaterials() {
    const deckTexture = createSurfboardDeckTexture();

    // High-gloss fiberglass resin finish with clearcoat
    this.boardMat = new THREE.MeshPhysicalMaterial({
      map: deckTexture,
      color: 0xffffff,
      roughness: 0.12,
      metalness: 0.05,
      clearcoat: 1.0,
      clearcoatRoughness: 0.08,
      reflectivity: 0.8
    });

    // Dark fiberglass thruster fins
    this.finMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7, // vibrant electric blue
      roughness: 0.2,
      metalness: 0.1
    });

    // Flexible polyurethane leash cord (bright neon orange)
    this.leashMat = new THREE.MeshStandardMaterial({
      color: 0xff4500,
      roughness: 0.4
    });

    // Ankle cuff & rail saver strap
    this.cuffMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.7
    });
  }

  buildBoard() {
    // Sculpted longboard geometry with nose rocker and rail contours
    // Length: 4.4, Width: 1.25, Thickness: 0.14
    const length = 4.4;
    const width = 1.25;
    const thickness = 0.14;

    const segX = 24;
    const segZ = 48;
    const geo = new THREE.PlaneGeometry(width, length, segX, segZ);
    geo.rotateX(-Math.PI / 2); // Lay horizontal in X-Z

    const pos = geo.attributes.position;
    const halfL = length / 2;
    const halfW = width / 2;

    for (let i = 0; i < pos.count; i++) {
      let x = pos.getX(i);
      let z = pos.getZ(i);

      // Normalized length coordinate: -1 (tail) to +1 (nose)
      const uZ = z / halfL;
      // Normalized width coordinate: -1 (left rail) to +1 (right rail)
      const uX = x / halfW;

      // Planform outline shaping (nose taper and tail swallow/pin)
      // Nose tapers smoothly from 0.4 to 1.0; tail tapers from -0.5 to -1.0
      let outlineFactor = 1.0;
      if (uZ > 0.2) {
        // Taper to rounded nose
        const t = (uZ - 0.2) / 0.8;
        outlineFactor = Math.cos(t * Math.PI * 0.45);
      } else if (uZ < -0.3) {
        // Taper to tail
        const t = (-uZ - 0.3) / 0.7;
        outlineFactor = Math.cos(t * Math.PI * 0.38);
      }

      x *= outlineFactor;
      pos.setX(i, x);

      // 3D Rocker curve (upward curvature of nose and tail)
      let rocker = 0;
      if (uZ > 0.1) {
        // Progressive nose rocker to prevent pearling
        rocker = Math.pow((uZ - 0.1) / 0.9, 2.2) * 0.32;
      } else if (uZ < -0.2) {
        // Subtle tail kick
        rocker = Math.pow((-uZ - 0.2) / 0.8, 2.0) * 0.08;
      }

      // Deck crown / rail roll-off (thicker in center, beveled at rails)
      const railDist = Math.abs(uX);
      const railBevel = Math.cos(railDist * Math.PI * 0.5) * (thickness * 0.5);

      pos.setY(i, rocker + railBevel);
    }

    geo.computeVertexNormals();

    // Upper deck mesh
    const deckMesh = new THREE.Mesh(geo, this.boardMat);
    deckMesh.castShadow = true;
    deckMesh.receiveShadow = true;
    this.boardMeshGroup.add(deckMesh);

    // Bottom hull (subtle concave bottom)
    const hullGeo = geo.clone();
    const hullPos = hullGeo.attributes.position;
    for (let i = 0; i < hullPos.count; i++) {
      const curY = hullPos.getY(i);
      hullPos.setY(i, curY - thickness);
    }
    hullGeo.computeVertexNormals();

    // Reverse normal orientation for bottom
    const hullMat = new THREE.MeshPhysicalMaterial({
      color: 0xf1f5f9,
      roughness: 0.08,
      metalness: 0.02,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05
    });
    const hullMesh = new THREE.Mesh(hullGeo, hullMat);
    hullMesh.castShadow = true;
    hullMesh.receiveShadow = true;
    this.boardMeshGroup.add(hullMesh);

    // Beveled rails perimeter band
    const railMat = new THREE.MeshStandardMaterial({
      color: 0x0891b2, // matching teal rail tint
      roughness: 0.2
    });
    // Add nose tip bumper protector
    const noseTipGeo = new THREE.SphereGeometry(0.08, 12, 12);
    noseTipGeo.scale(1.2, 0.4, 0.8);
    const noseTip = new THREE.Mesh(noseTipGeo, railMat);
    noseTip.position.set(0, 0.32, halfL);
    this.boardMeshGroup.add(noseTip);
  }

  buildFins() {
    // Classic Thruster Fin Setup: Center fin + twin angled side-bites
    const finsGroup = new THREE.Group();
    finsGroup.position.set(0, -0.06, -1.65);
    this.boardMeshGroup.add(finsGroup);

    const finConfigs = [
      { x: 0, z: -0.25, rotY: 0, scale: 1.0 },       // Center main skeg
      { x: -0.32, z: 0.15, rotY: -0.08, scale: 0.85 }, // Left side-bite
      { x: 0.32, z: 0.15, rotY: 0.08, scale: 0.85 }   // Right side-bite
    ];

    finConfigs.forEach(cfg => {
      const shape = new THREE.Shape();
      const s = cfg.scale;
      // Swept-back hydrofoil fin profile
      shape.moveTo(0, 0);
      shape.quadraticCurveTo(-0.06 * s, -0.25 * s, -0.15 * s, -0.42 * s);
      shape.quadraticCurveTo(-0.05 * s, -0.38 * s, 0.08 * s, -0.3 * s);
      shape.quadraticCurveTo(0.18 * s, -0.15 * s, 0.28 * s, 0);
      shape.closePath();

      const extrudeSettings = {
        depth: 0.024 * s,
        bevelEnabled: true,
        bevelSegments: 3,
        steps: 1,
        bevelSize: 0.008 * s,
        bevelThickness: 0.008 * s
      };

      const finGeo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      finGeo.rotateY(Math.PI / 2);
      finGeo.translate(-0.012 * s, 0, 0);

      const fin = new THREE.Mesh(finGeo, this.finMat);
      fin.position.set(cfg.x, 0, cfg.z);
      fin.rotation.y = cfg.rotY;
      fin.castShadow = true;
      finsGroup.add(fin);
    });
  }

  buildLeash() {
    // Leash plug on the deck near the tail
    const plugGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.04, 12);
    const plug = new THREE.Mesh(plugGeo, this.cuffMat);
    plug.position.set(0, 0.1, -1.95);
    this.boardMeshGroup.add(plug);

    // Flexible leash cord: dynamic CatmullRom spline to rear ankle
    this.leashPoints = [
      new THREE.Vector3(0, 0.1, -1.95),
      new THREE.Vector3(0.05, 0.2, -1.5),
      new THREE.Vector3(-0.15, 0.4, -1.1),
      new THREE.Vector3(-0.2, 0.75, -0.9) // connects near rear ankle
    ];
    this.leashCurve = new THREE.CatmullRomCurve3(this.leashPoints);
    this.leashGeo = new THREE.TubeGeometry(this.leashCurve, 18, 0.016, 6, false);
    this.leashMesh = new THREE.Mesh(this.leashGeo, this.leashMat);
    this.boardMeshGroup.add(this.leashMesh);
  }

  /**
   * Trajectory and fluid dynamics solver for carving the wave.
   * Rhythmic surf maneuvers: bottom turn -> snap off lip -> tube ride / pocket trim.
   */
  update(time, delta, waveModel) {
    // Cycle through continuous carving rhythm (period ~ 9 seconds)
    const cycleTime = (time * 0.7) % (Math.PI * 2);

    // 1. CARVE MANEUVER SOLVER
    // Compound harmonic path across the wave face
    const carveCurve = Math.sin(cycleTime);
    const snapCurve = Math.sin(cycleTime * 2.0);

    // Height on the wave face (from trough ~1.5 up to lip ~6.5)
    // Dropping in, climbing to the lip, diving down into the bottom turn
    const waveHeightNorm = 0.5 + 0.42 * Math.sin(cycleTime - 0.4);

    // Lateral position across the wave face (X axis: into the barrel vs out on the shoulder)
    // X ~ 1.5 is inside the barrel pocket; X ~ 5.5 is out on the shoulder
    const lateralX = 3.2 + 2.2 * Math.cos(cycleTime * 0.8) + snapCurve * 0.5;

    // Longitudinal speed down the wave line (Z axis)
    // Board maintains position in the pocket with subtle forward/back surging
    const surgeZ = Math.sin(cycleTime * 1.5) * 1.4;

    // Get wave face surface elevation and normal at this (X, Z) coordinate
    const surfaceData = waveModel.getSurfaceData(lateralX, surgeZ);
    const targetY = surfaceData.height;

    // 2. BOARD ATTITUDE & ROTATION
    // Yaw: carving direction
    const yaw = -Math.cos(cycleTime) * 0.45 + snapCurve * 0.15;

    // Roll: banking into the wave face or turn
    // Hard bottom turn banks steeply into the wave face (up to 40 degrees)
    const bankTurn = -carveCurve * 0.48;
    const waveSlopeRoll = surfaceData.slopeX * 0.65;
    const roll = bankTurn + waveSlopeRoll;

    // Pitch: nose up when climbing, nose down when dropping
    const pitch = -Math.cos(cycleTime) * 0.22 - surfaceData.slopeZ * 0.5 + 0.08;

    // Calculate G-force during carving turns
    const turnAccel = Math.abs(Math.sin(cycleTime));
    const gForce = 1.0 + turnAccel * 0.65;

    // Surfing speed
    const speed = 1.0 + (1.0 - waveHeightNorm) * 0.5 + turnAccel * 0.3;

    // Is the board currently deep in the tube/barrel?
    const inBarrel = lateralX < 2.4 && targetY > 3.0;

    // 3. APPLY POSITION & ROTATION TO BOARD
    this.group.position.set(lateralX, targetY, surgeZ);

    // Apply rotation to boardMeshGroup with smooth damping
    this.boardMeshGroup.rotation.y = yaw;
    this.boardMeshGroup.rotation.z = roll;
    this.boardMeshGroup.rotation.x = pitch;

    // Subtle natural board chatter / vibration on chop
    const chopVibe = Math.sin(time * 30.0) * 0.012 * speed;
    this.boardMeshGroup.position.y = chopVibe;

    // 4. UPDATE SPRAY CONTACT & EMISSION ORIGINS
    // Calculate world positions of the left and right rails and the tail fin
    this.boardMeshGroup.updateMatrixWorld(true);

    const leftRailLocal = new THREE.Vector3(-0.55, -0.05, -0.5);
    const rightRailLocal = new THREE.Vector3(0.55, -0.05, -0.5);
    const tailFinLocal = new THREE.Vector3(0, -0.3, -1.8);

    this.sprayOrigins.leftRail.copy(leftRailLocal).applyMatrix4(this.boardMeshGroup.matrixWorld);
    this.sprayOrigins.rightRail.copy(rightRailLocal).applyMatrix4(this.boardMeshGroup.matrixWorld);
    this.sprayOrigins.tailFin.copy(tailFinLocal).applyMatrix4(this.boardMeshGroup.matrixWorld);

    // Spray intensity increases during hard turns and high speed
    const sprayIntensity = (turnAccel * 1.5 + speed * 0.8) * (1.0 + Math.abs(roll));

    // Store state in physics object
    this.physics.carveAngle = carveCurve;
    this.physics.speed = speed;
    this.physics.pitch = pitch;
    this.physics.roll = roll;
    this.physics.yaw = yaw;
    this.physics.inBarrel = inBarrel;
    this.physics.gForce = gForce;
    this.physics.sprayIntensity = sprayIntensity;
    this.physics.railContact.left = Math.max(0, -roll + 0.3);
    this.physics.railContact.right = Math.max(0, roll + 0.3);

    return this.physics;
  }
}
