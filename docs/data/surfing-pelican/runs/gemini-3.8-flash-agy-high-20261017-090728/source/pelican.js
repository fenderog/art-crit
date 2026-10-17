import * as THREE from 'three';
import { createSurfboardTexture } from './textures.js';
import { getWaveState } from './wave.js';

/**
 * Creates the complete animated 3D Surfing Pelican:
 * - Retro twin-fin surfboard with airbrush artwork & leash
 * - Anatomically rich pelican with iconic bill, elastic throat pouch,
 *   articulated multi-segment wings, crest feathers, and retro surf sunglasses
 * - Complete surfing maneuver choreography (bottom turns, lip snaps, barrel rides, cutbacks)
 * - Dynamic secondary physics (pouch inertia, wind flutter, wing drag, blinking)
 */
export class SurfingPelican {
  constructor(scene) {
    this.scene = scene;

    // Surfing position & trajectory state
    this.z = 2.0;          // Position along wave length
    this.facePos = 0.5;    // Position up/down wave face (0 = trough, 1 = lip)
    this.speed = 1.0;
    this.time = 0;
    this.currentManeuver = 'Dropping In';
    this.carveIntensity = 0.2;

    // Physics & inertia state
    this.pouchVelocity = 0;
    this.pouchOffset = 0;
    this.roll = 0;
    this.pitch = 0;
    this.yaw = 0;
    this.crouch = 0;
    this.blinkTimer = 2.5;

    // Master container
    this.root = new THREE.Group();
    this.scene.add(this.root);

    this.buildSurfboard();
    this.buildPelican();
  }

  buildSurfboard() {
    this.boardGroup = new THREE.Group();
    this.root.add(this.boardGroup);

    // 1. Board Deck & Hull Geometry (Retro swallowtail fish shape)
    const boardShape = new THREE.Shape();
    const length = 3.8;
    const halfWidth = 0.72;

    // Pointed nose with slight curve
    boardShape.moveTo(0, length * 0.52);
    // Right rail curving down to swallowtail tip
    boardShape.bezierCurveTo(halfWidth * 0.95, length * 0.35, halfWidth, length * 0.05, halfWidth * 0.88, -length * 0.42);
    // Right swallowtail wing
    boardShape.lineTo(halfWidth * 0.75, -length * 0.52);
    // Swallowtail center notch
    boardShape.lineTo(0, -length * 0.38);
    // Left swallowtail wing
    boardShape.lineTo(-halfWidth * 0.75, -length * 0.52);
    // Left rail curving up to nose
    boardShape.lineTo(-halfWidth * 0.88, -length * 0.42);
    boardShape.bezierCurveTo(-halfWidth, length * 0.05, -halfWidth * 0.95, length * 0.35, 0, length * 0.52);

    const extrudeSettings = {
      steps: 2,
      depth: 0.16,
      bevelEnabled: true,
      bevelThickness: 0.06,
      bevelSize: 0.06,
      bevelSegments: 4
    };

    const boardGeo = new THREE.ExtrudeGeometry(boardShape, extrudeSettings);
    boardGeo.center();

    // Give the board realistic nose and tail rocker (upward curve)
    const pos = boardGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      // Rocker curve along Y axis (which corresponds to board length)
      const rocker = Math.pow(Math.abs(y) / (length * 0.5), 2.2) * (y > 0 ? 0.32 : 0.14);
      pos.setZ(i, pos.getZ(i) + rocker);
    }
    boardGeo.computeVertexNormals();

    const boardTex = createSurfboardTexture();
    const boardMat = new THREE.MeshStandardMaterial({
      map: boardTex,
      roughness: 0.25,
      metalness: 0.15
    });

    this.boardMesh = new THREE.Mesh(boardGeo, boardMat);
    // Rotate so board lies flat on XZ plane, nose pointing along -Z
    this.boardMesh.rotation.x = Math.PI / 2;
    this.boardMesh.rotation.z = Math.PI;
    this.boardMesh.castShadow = true;
    this.boardMesh.receiveShadow = true;
    this.boardGroup.add(this.boardMesh);

    // 2. Twin Keel Fins on the bottom
    const finShape = new THREE.Shape();
    finShape.moveTo(0, 0);
    finShape.bezierCurveTo(0.08, -0.22, 0.22, -0.38, 0.35, -0.42);
    finShape.lineTo(0.38, -0.38);
    finShape.bezierCurveTo(0.28, -0.15, 0.24, 0.0, 0.24, 0.0);
    finShape.closePath();

    const finExtrude = { depth: 0.03, bevelEnabled: true, bevelThickness: 0.01, bevelSize: 0.01, bevelSegments: 2 };
    const finGeo = new THREE.ExtrudeGeometry(finShape, finExtrude);
    const finMat = new THREE.MeshStandardMaterial({
      color: 0xff0055, // Fluorescent magenta
      roughness: 0.2,
      metalness: 0.2
    });

    // Right fin
    const rightFin = new THREE.Mesh(finGeo, finMat);
    rightFin.rotation.x = -Math.PI / 2;
    rightFin.rotation.z = 0.1;
    rightFin.position.set(0.36, -0.12, 1.3);
    this.boardGroup.add(rightFin);

    // Left fin
    const leftFin = new THREE.Mesh(finGeo, finMat);
    leftFin.rotation.x = -Math.PI / 2;
    leftFin.rotation.z = -0.1;
    leftFin.position.set(-0.36, -0.12, 1.3);
    this.boardGroup.add(leftFin);

    // 3. Surf Leash attached to rear deck
    const leashCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0.08, 1.45),
      new THREE.Vector3(-0.15, 0.14, 1.2),
      new THREE.Vector3(-0.25, 0.25, 0.95),
      new THREE.Vector3(-0.28, 0.42, 0.8) // Ankle cuff
    ]);
    const leashGeo = new THREE.TubeGeometry(leashCurve, 20, 0.015, 6, false);
    const leashMat = new THREE.MeshStandardMaterial({ color: 0x00f0ff, roughness: 0.3 });
    this.leashMesh = new THREE.Mesh(leashGeo, leashMat);
    this.boardGroup.add(this.leashMesh);
  }

  buildPelican() {
    this.pelican = new THREE.Group();
    this.pelican.position.set(0, 0.15, 0.2); // Positioned centered above the wax
    this.boardGroup.add(this.pelican);

    // Common palette materials
    this.whitePlumageMat = new THREE.MeshStandardMaterial({
      color: 0xfbfbfd,
      roughness: 0.65,
      metalness: 0.05
    });

    this.greyPlumageMat = new THREE.MeshStandardMaterial({
      color: 0x475569, // Slate covert feathers
      roughness: 0.7,
      metalness: 0.05
    });

    this.darkFlightMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b, // Dark navy-charcoal primary feathers
      roughness: 0.6,
      metalness: 0.05
    });

    this.beakUpperMat = new THREE.MeshStandardMaterial({
      color: 0xffa01c, // Vibrant warm orange-gold
      roughness: 0.35,
      metalness: 0.1
    });

    this.pouchMat = new THREE.MeshStandardMaterial({
      color: 0xff8c72, // Elastic peach-salmon throat sac
      roughness: 0.45,
      metalness: 0.05,
      transparent: true,
      opacity: 0.92
    });

    this.legMat = new THREE.MeshStandardMaterial({
      color: 0xff6b4a, // Coral-orange webbed feet
      roughness: 0.5,
      metalness: 0.1
    });

    // 1. Surfer Feet & Legs (Surfing stance: front foot forward-angled, back foot sideways)
    this.buildLegs();

    // 2. Torso (Puffed chest, tilted forward into athletic stance)
    this.torsoGroup = new THREE.Group();
    this.torsoGroup.position.set(0, 0.55, 0.0);
    this.pelican.add(this.torsoGroup);

    // Torso body mesh
    const bodyGeo = new THREE.SphereGeometry(0.55, 24, 20);
    bodyGeo.scale(0.85, 1.15, 1.35);
    const bodyMesh = new THREE.Mesh(bodyGeo, this.whitePlumageMat);
    bodyMesh.rotation.x = 0.35; // Tilted athletic crouch
    bodyMesh.castShadow = true;
    bodyMesh.receiveShadow = true;
    this.torsoGroup.add(bodyMesh);

    // Back mantle / scapular plumage
    const mantleGeo = new THREE.SphereGeometry(0.53, 20, 16, 0, Math.PI * 2, 0, Math.PI * 0.45);
    mantleGeo.scale(0.88, 1.18, 1.38);
    const mantleMesh = new THREE.Mesh(mantleGeo, this.greyPlumageMat);
    mantleMesh.rotation.x = 0.35;
    this.torsoGroup.add(mantleMesh);

    // Tail Feathers (Layered fan)
    this.tailGroup = new THREE.Group();
    this.tailGroup.position.set(0, 0.22, 0.7);
    this.torsoGroup.add(this.tailGroup);

    for (let i = -3; i <= 3; i++) {
      const featherGeo = new THREE.ConeGeometry(0.12, 0.65, 4);
      featherGeo.scale(1.0, 1.0, 0.15);
      const feather = new THREE.Mesh(featherGeo, i % 2 === 0 ? this.whitePlumageMat : this.greyPlumageMat);
      feather.position.set(i * 0.08, 0, 0.25);
      feather.rotation.x = Math.PI / 2 + 0.15;
      feather.rotation.y = i * 0.12;
      this.tailGroup.add(feather);
    }

    // 3. Wings (Articulated left and right arms for balancing & skimming the wave)
    this.buildWings();

    // 4. Neck & Head (Graceful S-curve with head tracking)
    this.buildHeadAndBeak();
  }

  buildLegs() {
    this.legsGroup = new THREE.Group();
    this.pelican.add(this.legsGroup);

    // Helper for webbed foot
    const createWebbedFoot = () => {
      const foot = new THREE.Group();
      // Ankle joint
      const ankleGeo = new THREE.CylinderGeometry(0.06, 0.05, 0.38, 8);
      const ankle = new THREE.Mesh(ankleGeo, this.legMat);
      ankle.position.y = 0.19;
      foot.add(ankle);

      // Webbing membrane & 4 toes
      const webShape = new THREE.Shape();
      webShape.moveTo(0, 0);
      webShape.lineTo(0.28, 0.38);  // Outer toe
      webShape.lineTo(0.09, 0.46);  // Mid-outer
      webShape.lineTo(-0.11, 0.44); // Mid-inner
      webShape.lineTo(-0.25, 0.32); // Inner toe
      webShape.closePath();

      const webExtrude = { depth: 0.02, bevelEnabled: true, bevelThickness: 0.01, bevelSize: 0.01, bevelSegments: 2 };
      const webGeo = new THREE.ExtrudeGeometry(webShape, webExtrude);
      const webMesh = new THREE.Mesh(webGeo, this.legMat);
      webMesh.rotation.x = -Math.PI / 2;
      webMesh.position.y = 0.01;
      foot.add(webMesh);

      // Black toe claws
      const clawMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.3 });
      const toeTips = [[0.28, 0.38], [0.09, 0.46], [-0.11, 0.44], [-0.25, 0.32]];
      for (const [tx, tz] of toeTips) {
        const claw = new THREE.Mesh(new THREE.ConeGeometry(0.02, 0.08, 6), clawMat);
        claw.rotation.x = Math.PI / 2;
        claw.position.set(tx, 0.02, tz + 0.04);
        foot.add(claw);
      }
      return foot;
    };

    // Front foot (angled 35 degrees forward-left across stringer)
    this.frontFoot = createWebbedFoot();
    this.frontFoot.position.set(-0.18, 0, -0.42);
    this.frontFoot.rotation.y = -0.6;
    this.legsGroup.add(this.frontFoot);

    // Back foot (planted 75 degrees sideways on the traction pad)
    this.backFoot = createWebbedFoot();
    this.backFoot.position.set(0.22, 0, 0.58);
    this.backFoot.rotation.y = -1.35;
    this.legsGroup.add(this.backFoot);
  }

  buildWings() {
    this.leftWing = this.createWing(false);
    this.leftWing.position.set(-0.45, 0.15, -0.05);
    this.torsoGroup.add(this.leftWing);

    this.rightWing = this.createWing(true);
    this.rightWing.position.set(0.45, 0.15, -0.05);
    this.torsoGroup.add(this.rightWing);
  }

  createWing(isRight) {
    const side = isRight ? 1 : -1;
    const wingRoot = new THREE.Group();

    // 1. Upper arm (humerus)
    const upperGeo = new THREE.CylinderGeometry(0.12, 0.10, 0.65, 8);
    const upperMesh = new THREE.Mesh(upperGeo, this.whitePlumageMat);
    upperMesh.position.set(side * 0.3, 0.05, 0);
    upperMesh.rotation.z = side * 1.1;
    wingRoot.add(upperMesh);

    // 2. Elbow joint & Forearm
    const forearmGroup = new THREE.Group();
    forearmGroup.position.set(side * 0.58, 0.15, 0);
    wingRoot.add(forearmGroup);

    const forearmGeo = new THREE.CylinderGeometry(0.10, 0.08, 0.75, 8);
    const forearmMesh = new THREE.Mesh(forearmGeo, this.greyPlumageMat);
    forearmMesh.position.set(side * 0.35, -0.05, 0.1);
    forearmMesh.rotation.z = side * 0.7;
    forearmMesh.rotation.x = 0.25;
    forearmGroup.add(forearmMesh);

    // 3. Primary flight feathers (finger-like separated quills)
    const primariesGroup = new THREE.Group();
    primariesGroup.position.set(side * 0.72, -0.2, 0.2);
    forearmGroup.add(primariesGroup);

    for (let i = 0; i < 6; i++) {
      const fGeo = new THREE.ConeGeometry(0.09, 0.95 - i * 0.06, 4);
      fGeo.scale(1.0, 1.0, 0.12);
      const fMesh = new THREE.Mesh(fGeo, this.darkFlightMat);
      fMesh.position.set(side * (i * 0.08), -i * 0.08, i * 0.05);
      fMesh.rotation.z = side * (0.8 + i * 0.14);
      fMesh.rotation.x = 0.2 + i * 0.06;
      primariesGroup.add(fMesh);
    }

    // Save joint handles for animation
    wingRoot.userData = {
      forearm: forearmGroup,
      primaries: primariesGroup,
      isRight: isRight
    };

    return wingRoot;
  }

  buildHeadAndBeak() {
    // 1. Neck (Lower & Mid joints for flexible S-curve)
    this.neckLower = new THREE.Group();
    this.neckLower.position.set(0, 0.35, -0.45);
    this.torsoGroup.add(this.neckLower);

    const neckLowerGeo = new THREE.CylinderGeometry(0.19, 0.24, 0.45, 12);
    const neckLowerMesh = new THREE.Mesh(neckLowerGeo, this.whitePlumageMat);
    neckLowerMesh.position.set(0, 0.18, -0.08);
    neckLowerMesh.rotation.x = -0.4;
    this.neckLower.add(neckLowerMesh);

    this.neckMid = new THREE.Group();
    this.neckMid.position.set(0, 0.38, -0.16);
    this.neckLower.add(this.neckMid);

    const neckMidGeo = new THREE.CylinderGeometry(0.16, 0.19, 0.45, 12);
    const neckMidMesh = new THREE.Mesh(neckMidGeo, this.whitePlumageMat);
    neckMidMesh.position.set(0, 0.18, 0.08);
    neckMidMesh.rotation.x = 0.35;
    this.neckMid.add(neckMidMesh);

    // 2. Head
    this.head = new THREE.Group();
    this.head.position.set(0, 0.38, 0.15);
    this.neckMid.add(this.head);

    const skullGeo = new THREE.SphereGeometry(0.28, 16, 16);
    skullGeo.scale(0.85, 0.95, 1.15);
    const skullMesh = new THREE.Mesh(skullGeo, this.whitePlumageMat);
    skullMesh.castShadow = true;
    this.head.add(skullMesh);

    // Head Crest Feathers (wind-blown tufts at the crown)
    this.crestGroup = new THREE.Group();
    this.crestGroup.position.set(0, 0.22, 0.18);
    this.head.add(this.crestGroup);

    for (let i = 0; i < 4; i++) {
      const cGeo = new THREE.ConeGeometry(0.05, 0.42 - i * 0.05, 4);
      cGeo.scale(1.0, 1.0, 0.15);
      const cMesh = new THREE.Mesh(cGeo, i === 0 ? this.whitePlumageMat : this.greyPlumageMat);
      cMesh.position.set((i - 1.5) * 0.04, i * 0.04, 0.1 + i * 0.04);
      cMesh.rotation.x = Math.PI / 2 + 0.4 + i * 0.1;
      this.crestGroup.add(cMesh);
    }

    // 3. Eyes with animated blinking eyelids
    this.buildEyes();

    // 4. Retro 80s Mirrored Surf Sunglasses
    this.buildSunglasses();

    // 5. The Grand Pelican Beak & Gular Pouch
    this.buildBeak();
  }

  buildEyes() {
    this.eyesGroup = new THREE.Group();
    this.eyesGroup.position.set(0, 0.08, -0.15);
    this.head.add(this.eyesGroup);

    const eyeGeo = new THREE.SphereGeometry(0.08, 12, 12);
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 });
    const pupilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.1 });
    const irisMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.2 }); // Golden amber iris

    // Left Eye
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.21, 0, 0);
    const leftIris = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.02, 10), irisMat);
    leftIris.rotation.x = Math.PI / 2;
    leftIris.rotation.y = -0.3;
    leftIris.position.set(-0.06, 0, -0.06);
    leftEye.add(leftIris);
    const leftPupil = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.025, 8), pupilMat);
    leftPupil.rotation.x = Math.PI / 2;
    leftPupil.rotation.y = -0.3;
    leftPupil.position.set(-0.065, 0, -0.065);
    leftEye.add(leftPupil);
    this.eyesGroup.add(leftEye);

    // Right Eye
    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.21, 0, 0);
    const rightIris = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.02, 10), irisMat);
    rightIris.rotation.x = Math.PI / 2;
    rightIris.rotation.y = 0.3;
    rightIris.position.set(0.06, 0, -0.06);
    rightEye.add(rightIris);
    const rightPupil = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.025, 8), pupilMat);
    rightPupil.rotation.x = Math.PI / 2;
    rightPupil.rotation.y = 0.3;
    rightPupil.position.set(0.065, 0, -0.065);
    rightEye.add(rightPupil);
    this.eyesGroup.add(rightEye);

    // Eyelids for blinking
    const lidGeo = new THREE.SphereGeometry(0.085, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.5);
    this.leftLid = new THREE.Mesh(lidGeo, this.whitePlumageMat);
    this.leftLid.position.set(-0.21, 0.01, 0);
    this.leftLid.rotation.x = -Math.PI / 2 + 0.2;
    this.eyesGroup.add(this.leftLid);

    this.rightLid = new THREE.Mesh(lidGeo, this.whitePlumageMat);
    this.rightLid.position.set(0.21, 0.01, 0);
    this.rightLid.rotation.x = -Math.PI / 2 + 0.2;
    this.eyesGroup.add(this.rightLid);
  }

  buildSunglasses() {
    this.shades = new THREE.Group();
    this.shades.position.set(0, 0.08, -0.22);
    this.head.add(this.shades);

    // Mirrored rainbow lenses with high metallic reflection
    const lensMat = new THREE.MeshPhysicalMaterial({
      color: 0x00f5d4,
      metalness: 0.95,
      roughness: 0.05,
      clearcoat: 1.0,
      clearcoatRoughness: 0.02
    });

    // Frame material (fluorescent neon magenta)
    const frameMat = new THREE.MeshStandardMaterial({
      color: 0xff0077,
      roughness: 0.2,
      metalness: 0.1
    });

    const lensGeo = new THREE.BoxGeometry(0.19, 0.12, 0.02);

    // Left lens
    const leftLens = new THREE.Mesh(lensGeo, lensMat);
    leftLens.position.set(-0.15, 0, 0);
    leftLens.rotation.y = -0.22;
    this.shades.add(leftLens);

    // Right lens
    const rightLens = new THREE.Mesh(lensGeo, lensMat);
    rightLens.position.set(0.15, 0, 0);
    rightLens.rotation.y = 0.22;
    this.shades.add(rightLens);

    // Bridge over the top of the beak
    const bridgeGeo = new THREE.BoxGeometry(0.14, 0.03, 0.04);
    const bridge = new THREE.Mesh(bridgeGeo, frameMat);
    bridge.position.set(0, 0.04, 0.02);
    this.shades.add(bridge);

    // Frame brow line
    const browGeo = new THREE.BoxGeometry(0.48, 0.03, 0.03);
    const brow = new THREE.Mesh(browGeo, frameMat);
    brow.position.set(0, 0.06, 0.01);
    this.shades.add(brow);
  }

  buildBeak() {
    this.beakGroup = new THREE.Group();
    this.beakGroup.position.set(0, -0.05, -0.25);
    this.head.add(this.beakGroup);

    // 1. Upper Mandible (Long hooked bill)
    const billLength = 1.35;
    const upperShape = new THREE.Shape();
    upperShape.moveTo(0, 0);
    upperShape.lineTo(0.14, -billLength * 0.2);
    upperShape.lineTo(0.09, -billLength * 0.85);
    upperShape.lineTo(0.04, -billLength);
    upperShape.lineTo(-0.04, -billLength);
    upperShape.lineTo(-0.09, -billLength * 0.85);
    upperShape.lineTo(-0.14, -billLength * 0.2);
    upperShape.closePath();

    const upperExtrude = { depth: 0.14, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 3 };
    const upperGeo = new THREE.ExtrudeGeometry(upperShape, upperExtrude);
    upperGeo.center();

    this.upperBill = new THREE.Mesh(upperGeo, this.beakUpperMat);
    this.upperBill.rotation.x = Math.PI / 2;
    this.upperBill.position.set(0, 0.02, -billLength * 0.5);
    this.beakGroup.add(this.upperBill);

    // Hooked bill tip (The Maxillary Nail)
    const nailGeo = new THREE.ConeGeometry(0.06, 0.18, 8);
    const nailMat = new THREE.MeshStandardMaterial({ color: 0xff4500, roughness: 0.2 });
    const nail = new THREE.Mesh(nailGeo, nailMat);
    nail.rotation.x = -Math.PI / 2 - 0.5;
    nail.position.set(0, -0.02, -billLength - 0.05);
    this.beakGroup.add(nail);

    // 2. Lower Jaw & The Iconic Gular Pouch
    this.lowerJawGroup = new THREE.Group();
    this.lowerJawGroup.position.set(0, -0.04, 0);
    this.beakGroup.add(this.lowerJawGroup);

    // Lower jaw bones
    const jawGeo = new THREE.CylinderGeometry(0.04, 0.03, billLength, 8);
    const leftJaw = new THREE.Mesh(jawGeo, this.beakUpperMat);
    leftJaw.position.set(-0.09, -0.02, -billLength * 0.48);
    leftJaw.rotation.x = Math.PI / 2;
    this.lowerJawGroup.add(leftJaw);

    const rightJaw = new THREE.Mesh(jawGeo, this.beakUpperMat);
    rightJaw.position.set(0.09, -0.02, -billLength * 0.48);
    rightJaw.rotation.x = Math.PI / 2;
    this.lowerJawGroup.add(rightJaw);

    // Gular Pouch (Elastic throat sac that wobbles with inertia)
    const pouchGeo = new THREE.SphereGeometry(0.32, 16, 16);
    pouchGeo.scale(0.55, 1.25, 2.3);
    this.pouchMesh = new THREE.Mesh(pouchGeo, this.pouchMat);
    this.pouchMesh.position.set(0, -0.28, -billLength * 0.45);
    this.pouchMesh.rotation.x = 0.15;
    this.lowerJawGroup.add(this.pouchMesh);
  }

  /**
   * Main animation loop update
   * Runs the procedural surfing routine, computes trajectory on the wave,
   * aligns board orientation, and animates all limbs and secondary physics
   */
  update(dt, time, particleSystem, audioUpdater) {
    this.time = time;

    // 1. Procedural Surfing Routine State Machine
    // Loops continuously through a thrilling 24-second sequence of authentic maneuvers:
    const cycleTime = 24.0;
    const t = (time % cycleTime);

    let targetFacePos = 0.5;
    let targetSpeed = 1.0;
    let targetRoll = 0.0;
    let targetPitch = 0.0;
    let targetYaw = 0.0;
    let targetCrouch = 0.0;
    let targetPouchOpen = 0.0;
    let maneuverName = 'Trimming';
    let turnIntensity = 0.15;

    if (t < 3.5) {
      // Phase 1: Dropping in down the face (The Takeoff)
      const p = t / 3.5;
      maneuverName = 'Dropping In!';
      targetFacePos = 0.65 - p * 0.38; // 0.65 -> 0.27
      targetSpeed = 1.2 + p * 0.5;
      targetPitch = 0.22;
      targetCrouch = 0.3 + p * 0.35;
      targetRoll = -0.15;
      turnIntensity = 0.25;
    } else if (t < 7.5) {
      // Phase 2: Powerful Deep Bottom Turn
      const p = (t - 3.5) / 4.0;
      maneuverName = 'Deep Bottom Turn!';
      targetFacePos = 0.26 + Math.sin(p * Math.PI) * 0.12;
      targetSpeed = 1.4;
      targetRoll = 0.65 * Math.sin(p * Math.PI); // Hard bank into the face
      targetYaw = -0.45 * Math.sin(p * Math.PI);
      targetPitch = -0.15;
      targetCrouch = 0.75; // Low crouch, trailing wing skims the water!
      turnIntensity = 0.85 * Math.sin(p * Math.PI);
    } else if (t < 11.5) {
      // Phase 3: Accelerating Up to the Lip & Radical Lip Snap!
      const p = (t - 7.5) / 4.0;
      if (p < 0.6) {
        maneuverName = 'Climbing the Face';
        targetFacePos = 0.32 + p * 0.95; // Climbing to 0.89 (lip!)
        targetPitch = -0.25;
        targetRoll = 0.25;
        targetCrouch = 0.4;
        turnIntensity = 0.5;
      } else {
        const snapP = (p - 0.6) / 0.4;
        maneuverName = 'Radical Lip Snap!!';
        targetFacePos = 0.88 - snapP * 0.15;
        targetRoll = -0.75 * Math.sin(snapP * Math.PI); // Snap tail around!
        targetYaw = 0.7 * Math.sin(snapP * Math.PI);
        targetCrouch = 0.85;
        targetPouchOpen = 0.4;
        turnIntensity = 1.0; // Max rooster tail spray!
      }
    } else if (t < 17.5) {
      // Phase 4: Inside the Barrel! (The Green Room Tube Ride)
      const p = (t - 11.5) / 6.0;
      maneuverName = 'In the Tube! 🌊';
      targetFacePos = 0.72 + Math.sin(p * Math.PI * 2) * 0.04; // Locked in trim under lip
      targetSpeed = 1.15;
      targetRoll = 0.28;
      targetPitch = 0.02;
      targetYaw = -0.05;
      targetCrouch = 0.65; // Tucked stance inside the hollow barrel
      targetPouchOpen = 0.2;
      turnIntensity = 0.2;
    } else if (t < 21.0) {
      // Phase 5: Spitting Barrel Exit & Joyous Flap
      const p = (t - 17.5) / 3.5;
      maneuverName = 'Shooting out the Barrel!';
      targetFacePos = 0.68 - p * 0.25;
      targetSpeed = 1.5;
      targetRoll = -0.2;
      targetPitch = 0.08;
      targetCrouch = 0.2;
      targetPouchOpen = 0.5; // Stoked open beak!
      turnIntensity = 0.45;
    } else {
      // Phase 6: Smooth Roundhouse Cutback
      const p = (t - 21.0) / 3.0;
      maneuverName = 'Roundhouse Cutback';
      targetFacePos = 0.43 + Math.sin(p * Math.PI) * 0.22;
      targetRoll = -0.55 * Math.sin(p * Math.PI);
      targetYaw = 0.4 * Math.sin(p * Math.PI);
      targetCrouch = 0.55;
      turnIntensity = 0.7;
    }

    this.currentManeuver = maneuverName;
    this.carveIntensity = turnIntensity;

    // Smooth physics interpolation
    const lerpRate = dt * 5.0;
    this.facePos += (targetFacePos - this.facePos) * lerpRate;
    this.speed += (targetSpeed - this.speed) * lerpRate;
    this.roll += (targetRoll - this.roll) * lerpRate;
    this.pitch += (targetPitch - this.pitch) * lerpRate;
    this.yaw += (targetYaw - this.yaw) * lerpRate;
    this.crouch += (targetCrouch - this.crouch) * lerpRate;

    // Progress along wave length Z
    this.z += (Math.sin(time * 0.35) * 1.5 - 0.2) * dt;
    this.z = Math.max(-12, Math.min(18, this.z)); // Keep centered within cinematic stage

    // 2. Lock to the Dynamic Wave Surface
    const waveState = getWaveState(this.z, this.facePos, time);
    const pos = waveState.position;
    this.root.position.copy(pos);

    // Build local coordinate frame aligned with wave surface
    const up = waveState.normal.clone();
    const forward = waveState.alongWave.clone(); // Down the line
    const right = new THREE.Vector3().crossVectors(up, forward).normalize();

    // Recompute orthogonal forward
    forward.crossVectors(right, up).normalize();

    const basisMatrix = new THREE.Matrix4().makeBasis(right, up, forward);
    this.root.quaternion.setFromRotationMatrix(basisMatrix);

    // Apply board carving angles (bank, trim pitch, carve yaw)
    this.boardGroup.rotation.z = this.roll;
    this.boardGroup.rotation.x = this.pitch;
    this.boardGroup.rotation.y = this.yaw;

    // 3. Spray Particles Emission
    if (particleSystem) {
      const sprayDir = right.clone().multiplyScalar(this.roll > 0 ? 1 : -1);
      const boardVel = forward.clone().multiplyScalar(this.speed * 8.0);
      particleSystem.emitRailSpray(pos, boardVel, sprayDir, turnIntensity);
    }

    // 4. Audio Feedback Update
    if (audioUpdater) {
      audioUpdater(turnIntensity, waveState.inBarrel, time);
    }

    // 5. Secondary Pelican Body Animations:
    // A. Crouch and weight shift
    this.torsoGroup.position.y = 0.55 - this.crouch * 0.22;
    this.torsoGroup.rotation.z = -this.roll * 0.35; // Body compensates for board bank
    this.torsoGroup.rotation.x = 0.35 + this.crouch * 0.2;

    // B. Legs & feet flexion
    this.frontFoot.position.y = -this.crouch * 0.05;
    this.backFoot.position.y = -this.crouch * 0.05;

    // C. Wings balancing & wave skimming:
    // When banking hard into the face (roll > 0), inside wing dips down close to water, outside wing lifts
    const leftArmRoll = -0.3 + this.roll * 0.8 - this.crouch * 0.2;
    const rightArmRoll = 0.3 + this.roll * 0.8 + this.crouch * 0.2;

    // Wing flap cycle when speeding or exiting tube
    const flap = Math.sin(time * 6.5) * (this.speed > 1.3 ? 0.35 : 0.08);

    this.leftWing.rotation.z = leftArmRoll + flap;
    this.leftWing.rotation.x = 0.15 + this.crouch * 0.3;
    this.rightWing.rotation.z = rightArmRoll - flap;
    this.rightWing.rotation.x = 0.15 + this.crouch * 0.3;

    // Forearm & primaries flex
    this.leftWing.userData.forearm.rotation.z = -0.4 + flap * 0.5;
    this.rightWing.userData.forearm.rotation.z = 0.4 - flap * 0.5;

    // D. Gular Pouch Inertia Physics (harmonic oscillation + G-force)
    const gForce = turnIntensity * 1.5;
    const pouchSpring = 35.0;
    const pouchDamping = 6.0;
    const targetOffset = targetPouchOpen * 0.35 + Math.sin(time * 8.0) * 0.06 * gForce;
    const pouchAcc = (targetOffset - this.pouchOffset) * pouchSpring - this.pouchVelocity * pouchDamping;
    this.pouchVelocity += pouchAcc * dt;
    this.pouchOffset += this.pouchVelocity * dt;

    this.lowerJawGroup.rotation.x = this.pouchOffset;
    this.pouchMesh.scale.y = 1.25 + this.pouchOffset * 0.8;
    this.pouchMesh.scale.x = 0.55 + this.pouchOffset * 0.4;

    // E. Head stabilization & Vestibular-Ocular Reflex:
    // Keeps head level with horizon and focused forward into the wave
    this.head.rotation.z = -this.roll * 0.65;
    this.head.rotation.y = -this.yaw * 0.5 + Math.sin(time * 1.2) * 0.1;
    this.head.rotation.x = -this.pitch * 0.5;

    // F. Crest feather wind flutter
    for (let i = 0; i < this.crestGroup.children.length; i++) {
      const crestF = this.crestGroup.children[i];
      crestF.rotation.z = Math.sin(time * 14.0 + i) * 0.15;
    }

    // G. Tail rudder tilt
    this.tailGroup.rotation.y = -this.yaw * 0.8;
    this.tailGroup.rotation.z = this.roll * 0.5;

    // H. Eye blinking
    this.blinkTimer -= dt;
    if (this.blinkTimer < 0) {
      this.blinkTimer = 2.5 + Math.random() * 2.0;
    }
    const isBlinking = this.blinkTimer < 0.14;
    const lidAngle = isBlinking ? 0.0 : -Math.PI / 2 + 0.2;
    this.leftLid.rotation.x = lidAngle;
    this.rightLid.rotation.x = lidAngle;
  }
}
