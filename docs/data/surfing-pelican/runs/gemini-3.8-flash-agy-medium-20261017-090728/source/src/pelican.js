import * as THREE from 'three';
import { createPelicanEyeTexture, createFeatherNormalTexture } from './textures.js';

/**
 * Procedural Pelican 3D Character Model with Articulated Rig and Animation Solver
 */
export class Pelican {
  constructor() {
    this.group = new THREE.Group();
    this.group.name = 'Pelican';

    // Materials
    this.initMaterials();

    // Rig joints reference object for kinematics
    this.joints = {};

    // Build the hierarchical character model
    this.buildModel();

    // Secondary motion state
    this.pouchPhase = 0;
    this.wingFlutter = 0;
    this.headLookTarget = new THREE.Vector3(0, 0, 5);
  }

  initMaterials() {
    const featherNormal = createFeatherNormalTexture();
    const eyeTexture = createPelicanEyeTexture();

    // Body & neck white/cream feathers
    this.featherWhiteMat = new THREE.MeshStandardMaterial({
      color: 0xf4f6f8,
      roughness: 0.65,
      metalness: 0.05,
      normalMap: featherNormal,
      normalScale: new THREE.Vector2(0.2, 0.2)
    });

    // Darker slate grey for wing flight feathers and back accents
    this.featherSlateMat = new THREE.MeshStandardMaterial({
      color: 0x3d4450,
      roughness: 0.7,
      metalness: 0.05,
      normalMap: featherNormal,
      normalScale: new THREE.Vector2(0.3, 0.3)
    });

    // Secondary wing covert silvery feathers
    this.featherCovertMat = new THREE.MeshStandardMaterial({
      color: 0x85929e,
      roughness: 0.6,
      metalness: 0.05
    });

    // Beak horn material (warm golden yellow/amber)
    this.beakMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      roughness: 0.35,
      metalness: 0.08
    });

    // Beak tip hook (deeper coral/reddish amber)
    this.beakTipMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      roughness: 0.25,
      metalness: 0.1
    });

    // Throat pouch: flexible salmon/amber gular skin
    this.pouchMat = new THREE.MeshStandardMaterial({
      color: 0xfb923c,
      roughness: 0.45,
      metalness: 0.05,
      side: THREE.DoubleSide
    });

    // Pelican eye material
    this.eyeMat = new THREE.MeshStandardMaterial({
      map: eyeTexture,
      roughness: 0.15,
      metalness: 0.1
    });

    // Bare facial skin around eyes (pale pinkish-cream)
    this.faceSkinMat = new THREE.MeshStandardMaterial({
      color: 0xfecdd3,
      roughness: 0.5
    });

    // Legs & webbed feet (warm flesh/pinkish-grey)
    this.legMat = new THREE.MeshStandardMaterial({
      color: 0xe08466,
      roughness: 0.5,
      metalness: 0.05
    });

    // Webbing membrane
    this.webbingMat = new THREE.MeshStandardMaterial({
      color: 0xed9f85,
      roughness: 0.6,
      side: THREE.DoubleSide
    });

    // Sunglasses frame (stylish tortoise shell / retro gold)
    this.shadesFrameMat = new THREE.MeshStandardMaterial({
      color: 0x27190f,
      roughness: 0.25,
      metalness: 0.4
    });

    // Sunglasses lenses (dark polarized reflective mirror)
    this.shadesLensMat = new THREE.MeshPhysicalMaterial({
      color: 0x05131a,
      roughness: 0.08,
      metalness: 0.9,
      reflectivity: 0.9,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05
    });

    // Lei flower materials (Hawaiian plumeria/hibiscus)
    this.flowerColors = [
      new THREE.MeshStandardMaterial({ color: 0xf43f5e, roughness: 0.4 }), // bright magenta
      new THREE.MeshStandardMaterial({ color: 0xfbbf24, roughness: 0.4 }), // warm yellow
      new THREE.MeshStandardMaterial({ color: 0xffedd5, roughness: 0.4 }), // white plumeria
      new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.5 })  // tropical green leaf
    ];
  }

  buildModel() {
    // ROOT / PELVIS
    const pelvis = new THREE.Group();
    pelvis.position.set(0, 1.25, 0); // elevated above board
    this.group.add(pelvis);
    this.joints.pelvis = pelvis;

    // --- BODY / TORSO ---
    const bodyGroup = new THREE.Group();
    pelvis.add(bodyGroup);
    this.joints.body = bodyGroup;

    // Main torso: aerodynamic tapered teardrop
    const bodyGeo = new THREE.SphereGeometry(0.85, 24, 20);
    bodyGeo.scale(0.85, 0.95, 1.35);
    const bodyMesh = new THREE.Mesh(bodyGeo, this.featherWhiteMat);
    bodyMesh.castShadow = true;
    bodyMesh.receiveShadow = true;
    bodyMesh.position.set(0, 0, -0.1);
    bodyMesh.rotation.x = -0.15; // slightly forward lean
    bodyGroup.add(bodyMesh);

    // Torso back mantle (darker feather overlay)
    const mantleGeo = new THREE.SphereGeometry(0.86, 20, 16, 0, Math.PI * 2, 0, Math.PI * 0.45);
    mantleGeo.scale(0.83, 0.92, 1.32);
    const mantleMesh = new THREE.Mesh(mantleGeo, this.featherCovertMat);
    mantleMesh.position.set(0, 0.08, -0.12);
    mantleMesh.rotation.x = -0.15;
    bodyGroup.add(mantleMesh);

    // --- TAIL ---
    const tailGroup = new THREE.Group();
    tailGroup.position.set(0, 0.15, -1.25);
    bodyGroup.add(tailGroup);
    this.joints.tail = tailGroup;

    // Layered tail fan feathers
    for (let i = -3; i <= 3; i++) {
      const angle = (i / 3) * 0.35;
      const featherGeo = new THREE.ConeGeometry(0.12, 0.8, 6);
      featherGeo.scale(1.0, 1.0, 0.25);
      const feather = new THREE.Mesh(featherGeo, this.featherSlateMat);
      feather.position.set(Math.sin(angle) * 0.25, 0, -0.35);
      feather.rotation.y = angle;
      feather.rotation.x = -Math.PI / 2 + 0.25;
      tailGroup.add(feather);
    }

    // --- ARTICULATED S-CURVE NECK ---
    // Neck Base
    const neckBase = new THREE.Group();
    neckBase.position.set(0, 0.45, 0.6);
    neckBase.rotation.x = 0.35;
    bodyGroup.add(neckBase);
    this.joints.neckBase = neckBase;

    const neck1Geo = new THREE.CylinderGeometry(0.3, 0.36, 0.5, 16);
    const neck1Mesh = new THREE.Mesh(neck1Geo, this.featherWhiteMat);
    neck1Mesh.position.set(0, 0.25, 0);
    neck1Mesh.castShadow = true;
    neckBase.add(neck1Mesh);

    // Neck Mid
    const neckMid = new THREE.Group();
    neckMid.position.set(0, 0.48, 0);
    neckMid.rotation.x = -0.4;
    neckBase.add(neckMid);
    this.joints.neckMid = neckMid;

    const neck2Geo = new THREE.CylinderGeometry(0.24, 0.3, 0.55, 16);
    const neck2Mesh = new THREE.Mesh(neck2Geo, this.featherWhiteMat);
    neck2Mesh.position.set(0, 0.26, 0);
    neck2Mesh.castShadow = true;
    neckMid.add(neck2Mesh);

    // Neck Upper
    const neckUpper = new THREE.Group();
    neckUpper.position.set(0, 0.52, 0);
    neckUpper.rotation.x = 0.2;
    neckMid.add(neckUpper);
    this.joints.neckUpper = neckUpper;

    const neck3Geo = new THREE.CylinderGeometry(0.21, 0.25, 0.45, 16);
    const neck3Mesh = new THREE.Mesh(neck3Geo, this.featherWhiteMat);
    neck3Mesh.position.set(0, 0.22, 0);
    neck3Mesh.castShadow = true;
    neckUpper.add(neck3Mesh);

    // --- HEAD ---
    const headGroup = new THREE.Group();
    headGroup.position.set(0, 0.44, 0.05);
    neckUpper.add(headGroup);
    this.joints.head = headGroup;

    // Cranium
    const craniumGeo = new THREE.SphereGeometry(0.32, 20, 18);
    craniumGeo.scale(0.85, 0.95, 1.2);
    const craniumMesh = new THREE.Mesh(craniumGeo, this.featherWhiteMat);
    craniumMesh.position.set(0, 0.1, 0);
    craniumMesh.castShadow = true;
    headGroup.add(craniumMesh);

    // Crest feathers on crown (pelican back plume)
    const crestGroup = new THREE.Group();
    crestGroup.position.set(0, 0.26, -0.22);
    headGroup.add(crestGroup);
    this.joints.crest = crestGroup;

    for (let c = 0; c < 5; c++) {
      const crestPlumeGeo = new THREE.ConeGeometry(0.06, 0.4 - c * 0.04, 6);
      crestPlumeGeo.scale(1.0, 1.0, 0.2);
      const crestPlume = new THREE.Mesh(crestPlumeGeo, this.featherWhiteMat);
      crestPlume.position.set((c - 2) * 0.04, c * 0.02, -c * 0.06);
      crestPlume.rotation.x = -Math.PI / 2 - 0.25 - c * 0.1;
      crestGroup.add(crestPlume);
    }

    // Bare facial eye patches
    for (const side of [-1, 1]) {
      const patchGeo = new THREE.CircleGeometry(0.12, 16);
      const patch = new THREE.Mesh(patchGeo, this.faceSkinMat);
      patch.position.set(side * 0.27, 0.12, 0.12);
      patch.rotation.y = side * (Math.PI / 2 + 0.1);
      headGroup.add(patch);

      // Eye
      const eyeGeo = new THREE.SphereGeometry(0.07, 16, 16);
      const eye = new THREE.Mesh(eyeGeo, this.eyeMat);
      eye.position.set(side * 0.265, 0.12, 0.14);
      eye.rotation.y = side * (Math.PI / 2);
      headGroup.add(eye);
    }

    // --- BEAK & GULAR POUCH ---
    const beakGroup = new THREE.Group();
    beakGroup.position.set(0, 0.08, 0.35);
    headGroup.add(beakGroup);
    this.joints.beak = beakGroup;

    // Upper bill (Maxilla): long, sturdy, flattened with longitudinal dorsal ridge
    const billLength = 1.45;
    const billGeo = new THREE.ConeGeometry(0.18, billLength, 16);
    billGeo.scale(0.85, 0.45, 1.0);
    billGeo.rotateX(Math.PI / 2);
    billGeo.translate(0, 0.02, billLength / 2);
    const upperBill = new THREE.Mesh(billGeo, this.beakMat);
    upperBill.castShadow = true;
    beakGroup.add(upperBill);

    // Beak hook / nail at the tip
    const hookGeo = new THREE.CylinderGeometry(0.02, 0.05, 0.14, 8);
    hookGeo.rotateX(0.4);
    const hookMesh = new THREE.Mesh(hookGeo, this.beakTipMat);
    hookMesh.position.set(0, -0.04, billLength);
    beakGroup.add(hookMesh);

    // Beak dorsal ridge line (distinctive horn keel)
    const ridgeGeo = new THREE.BoxGeometry(0.04, 0.06, billLength * 0.85);
    const ridgeMesh = new THREE.Mesh(ridgeGeo, this.beakTipMat);
    ridgeMesh.position.set(0, 0.06, billLength * 0.45);
    beakGroup.add(ridgeMesh);

    // GULAR POUCH (The iconic pelican throat sac)
    // Modeled as an expandable, organic pouch suspended beneath the bill and throat
    const pouchCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, -0.02, 0.1),
      new THREE.Vector3(0, -0.32, 0.5),
      new THREE.Vector3(0, -0.28, 0.95),
      new THREE.Vector3(0, -0.08, 1.3),
      new THREE.Vector3(0, -0.02, 1.4)
    ]);
    const pouchGeo = new THREE.TubeGeometry(pouchCurve, 24, 0.14, 14, false);
    pouchGeo.scale(0.8, 1.5, 1.0); // deep and expandable
    const pouchMesh = new THREE.Mesh(pouchGeo, this.pouchMat);
    pouchMesh.castShadow = true;
    beakGroup.add(pouchMesh);
    this.pouchMesh = pouchMesh;

    // Store pouch original vertex positions for dynamic ripple/wobble deformation
    this.pouchOrigPos = pouchGeo.attributes.position.clone();

    // --- COOL RETRO SURF SHADES (SUNGLASSES) ---
    const shadesGroup = new THREE.Group();
    shadesGroup.position.set(0, 0.14, 0.22);
    headGroup.add(shadesGroup);

    // Sunglasses bridge
    const bridgeGeo = new THREE.BoxGeometry(0.24, 0.03, 0.03);
    const bridgeMesh = new THREE.Mesh(bridgeGeo, this.shadesFrameMat);
    bridgeMesh.position.set(0, 0.04, 0.14);
    shadesGroup.add(bridgeMesh);

    // Dual teardrop aviator lenses & rims
    for (const side of [-1, 1]) {
      // Lens frame
      const rimGeo = new THREE.TorusGeometry(0.12, 0.022, 8, 20);
      rimGeo.scale(1.1, 0.85, 1.0);
      const rimMesh = new THREE.Mesh(rimGeo, this.shadesFrameMat);
      rimMesh.position.set(side * 0.18, 0.01, 0.13);
      rimMesh.rotation.y = side * 0.25;
      shadesGroup.add(rimMesh);

      // Dark tinted reflective lens
      const lensGeo = new THREE.CircleGeometry(0.115, 18);
      lensGeo.scale(1.1, 0.85);
      const lensMesh = new THREE.Mesh(lensGeo, this.shadesLensMat);
      lensMesh.position.set(side * 0.18, 0.01, 0.132);
      lensMesh.rotation.y = side * 0.25;
      shadesGroup.add(lensMesh);

      // Side temple arm going back along head
      const armGeo = new THREE.BoxGeometry(0.02, 0.02, 0.35);
      const armMesh = new THREE.Mesh(armGeo, this.shadesFrameMat);
      armMesh.position.set(side * 0.29, 0.03, -0.03);
      armMesh.rotation.y = side * 0.12;
      shadesGroup.add(armMesh);
    }

    // --- HAWAIIAN TROPICAL FLOWER LEI ---
    const leiGroup = new THREE.Group();
    leiGroup.position.set(0, 0.38, 0.45);
    bodyGroup.add(leiGroup);
    this.joints.lei = leiGroup;

    const numFlowers = 18;
    for (let f = 0; f < numFlowers; f++) {
      const angle = (f / numFlowers) * Math.PI * 2;
      const rx = 0.48 * Math.cos(angle);
      const rz = 0.45 * Math.sin(angle);
      const ry = -Math.sin(angle) * 0.18;

      const flower = new THREE.Group();
      flower.position.set(rx, ry, rz);
      flower.rotation.z = angle + Math.PI / 2;
      flower.rotation.x = Math.PI / 3;

      // 5 petals for tropical plumeria
      const petalMat = this.flowerColors[f % 3];
      for (let p = 0; p < 5; p++) {
        const petalGeo = new THREE.ConeGeometry(0.045, 0.12, 5);
        petalGeo.scale(1.0, 1.0, 0.3);
        const petal = new THREE.Mesh(petalGeo, petalMat);
        petal.rotation.z = (p / 5) * Math.PI * 2;
        petal.position.set(Math.cos((p / 5) * Math.PI * 2) * 0.03, Math.sin((p / 5) * Math.PI * 2) * 0.03, 0);
        flower.add(petal);
      }

      // Small green leaf interspersed
      if (f % 2 === 0) {
        const leafGeo = new THREE.ConeGeometry(0.035, 0.14, 5);
        leafGeo.scale(1.0, 1.0, 0.2);
        const leaf = new THREE.Mesh(leafGeo, this.flowerColors[3]);
        leaf.position.set(0, 0, -0.02);
        leaf.rotation.z = (f * 1.5);
        flower.add(leaf);
      }

      leiGroup.add(flower);
    }

    // --- WINGS (LEFT & RIGHT) ---
    this.joints.wings = {};
    for (const side of ['left', 'right']) {
      const s = side === 'left' ? -1 : 1;

      // Shoulder joint
      const shoulder = new THREE.Group();
      shoulder.position.set(s * 0.65, 0.4, 0.1);
      bodyGroup.add(shoulder);

      // Upper arm (Humerus)
      const upperArmGeo = new THREE.CylinderGeometry(0.12, 0.15, 0.7, 10);
      upperArmGeo.translate(0, 0.35, 0);
      const upperArm = new THREE.Mesh(upperArmGeo, this.featherWhiteMat);
      upperArm.rotation.z = s * 0.6;
      shoulder.add(upperArm);

      // Elbow joint
      const elbow = new THREE.Group();
      elbow.position.set(s * 0.55, 0.55, 0);
      shoulder.add(elbow);

      // Forearm (Radius/Ulna)
      const forearmGeo = new THREE.CylinderGeometry(0.09, 0.12, 0.9, 10);
      forearmGeo.translate(0, 0.45, 0);
      const forearm = new THREE.Mesh(forearmGeo, this.featherCovertMat);
      forearm.rotation.z = s * 0.4;
      elbow.add(forearm);

      // Wrist joint
      const wrist = new THREE.Group();
      wrist.position.set(s * 0.58, 0.75, 0);
      elbow.add(wrist);

      // Flight Feathers: layered spread wingspan
      const primaryFeathers = new THREE.Group();
      wrist.add(primaryFeathers);

      // 7 Primary long flight feathers with dark tips
      for (let p = 0; p < 7; p++) {
        const pLen = 1.2 - p * 0.08;
        const pGeo = new THREE.ConeGeometry(0.12, pLen, 6);
        pGeo.scale(1.0, 1.0, 0.15);
        pGeo.translate(0, pLen / 2, 0);
        const pMesh = new THREE.Mesh(pGeo, this.featherSlateMat);
        pMesh.position.set(s * (0.1 + p * 0.07), -0.05, -p * 0.12);
        pMesh.rotation.z = s * (0.8 + p * 0.14);
        pMesh.rotation.y = s * (0.15 - p * 0.04);
        pMesh.rotation.x = -0.2 - p * 0.05;
        pMesh.castShadow = true;
        primaryFeathers.add(pMesh);
      }

      // Secondary broad feathers along forearm
      for (let sec = 0; sec < 6; sec++) {
        const secLen = 0.85 - sec * 0.04;
        const secGeo = new THREE.ConeGeometry(0.13, secLen, 6);
        secGeo.scale(1.0, 1.0, 0.15);
        secGeo.translate(0, secLen / 2, 0);
        const secMesh = new THREE.Mesh(secGeo, this.featherCovertMat);
        secMesh.position.set(s * 0.15, sec * 0.14, -0.15 - sec * 0.06);
        secMesh.rotation.z = s * 1.1;
        secMesh.rotation.x = -0.3;
        elbow.add(secMesh);
      }

      this.joints.wings[side] = {
        shoulder,
        elbow,
        wrist,
        primaries: primaryFeathers
      };
    }

    // --- LEGS & WEBBED FEET (SURFER STANCE) ---
    // Stance: Left foot front/angled, Right foot rear/rail grip
    this.joints.legs = {};
    const footConfigs = [
      { side: 'front', x: 0.15, z: 0.8, footRotY: -0.4, crouch: 1.0 },
      { side: 'rear', x: -0.2, z: -0.9, footRotY: 0.35, crouch: 1.15 }
    ];

    footConfigs.forEach(cfg => {
      // Hip joint attached to pelvis
      const hip = new THREE.Group();
      hip.position.set(cfg.x * 1.5, -0.4, cfg.z * 0.6);
      pelvis.add(hip);

      // Thigh
      const thighGeo = new THREE.CylinderGeometry(0.12, 0.1, 0.55, 10);
      thighGeo.translate(0, -0.25, 0);
      const thigh = new THREE.Mesh(thighGeo, this.featherWhiteMat);
      thigh.rotation.x = 0.65 * cfg.crouch;
      thigh.rotation.z = (cfg.x > 0 ? 0.3 : -0.3);
      hip.add(thigh);

      // Knee joint
      const knee = new THREE.Group();
      knee.position.set(0, -0.48, 0.3);
      hip.add(knee);

      // Shin (Tarsometatarsus)
      const shinGeo = new THREE.CylinderGeometry(0.07, 0.065, 0.6, 10);
      shinGeo.translate(0, -0.28, 0);
      const shin = new THREE.Mesh(shinGeo, this.legMat);
      shin.rotation.x = -1.15 * cfg.crouch;
      knee.add(shin);

      // Ankle joint
      const ankle = new THREE.Group();
      ankle.position.set(0, -0.52, -0.35);
      knee.add(ankle);

      // Webbed Foot (Totipalmate: 4 toes joined by full webbing)
      const foot = new THREE.Group();
      foot.rotation.y = cfg.footRotY;
      ankle.add(foot);

      // 4 articulated toes
      const toeAngles = [-0.45, -0.15, 0.18, 0.48];
      const toeLengths = [0.42, 0.55, 0.58, 0.45];

      for (let t = 0; t < 4; t++) {
        const tLen = toeLengths[t];
        const toeGeo = new THREE.CylinderGeometry(0.025, 0.018, tLen, 8);
        toeGeo.translate(0, tLen / 2, 0);
        const toe = new THREE.Mesh(toeGeo, this.legMat);
        toe.rotation.x = Math.PI / 2;
        toe.rotation.y = toeAngles[t];
        foot.add(toe);

        // Toe claw
        const clawGeo = new THREE.ConeGeometry(0.02, 0.08, 6);
        clawGeo.translate(0, 0.04, 0);
        const claw = new THREE.Mesh(clawGeo, this.shadesFrameMat);
        claw.position.set(Math.sin(toeAngles[t]) * tLen, 0, Math.cos(toeAngles[t]) * tLen);
        claw.rotation.x = Math.PI / 2 + 0.3;
        foot.add(claw);
      }

      // Webbing membrane between toes
      const webShape = new THREE.Shape();
      webShape.moveTo(0, 0);
      for (let t = 0; t < 4; t++) {
        webShape.lineTo(Math.sin(toeAngles[t]) * toeLengths[t] * 0.9, Math.cos(toeAngles[t]) * toeLengths[t] * 0.9);
      }
      webShape.lineTo(0, 0);
      const webGeo = new THREE.ShapeGeometry(webShape);
      const webMesh = new THREE.Mesh(webGeo, this.webbingMat);
      webMesh.rotation.x = -Math.PI / 2;
      webMesh.position.y = 0.01;
      foot.add(webMesh);

      this.joints.legs[cfg.side] = { hip, knee, ankle, foot };
    });
  }

  /**
   * Dynamic animation solver reacting to surfing maneuvers, wave curvature, and ocean wind
   */
  update(time, delta, surfPhysics) {
    const {
      carveAngle = 0,      // -1 (turning up face) to +1 (bottom turn)
      speed = 1.0,         // surfing speed multiplier
      pitch = 0,           // board nose pitch
      roll = 0,            // board rail roll
      inBarrel = false,    // inside the barrel tube
      gForce = 1.0         // centrifugal G-forces in turns
    } = surfPhysics || {};

    // 1. PELVIS / CROUCH DYNAMICS
    // Deep athletic crouch in hard bottom turns, slight extension when trimming
    const crouchFactor = 1.0 + Math.abs(carveAngle) * 0.35 + (gForce - 1.0) * 0.25;
    const baseHeight = 1.15 - (crouchFactor - 1.0) * 0.28;
    this.joints.pelvis.position.y = baseHeight + Math.sin(time * 3.5) * 0.03;

    // Pelvis leans into the turn
    this.joints.pelvis.rotation.z = -roll * 0.65;
    this.joints.pelvis.rotation.x = -pitch * 0.4 + 0.1;
    this.joints.pelvis.rotation.y = carveAngle * 0.3;

    // 2. SPINE & NECK S-CURVE ABSORPTION
    // Keep head stable and eyes looking down the line (vestibulo-ocular reflex)
    const neckSway = Math.sin(time * 4.0) * 0.04;
    this.joints.neckBase.rotation.z = roll * 0.35 + neckSway;
    this.joints.neckBase.rotation.x = 0.35 - carveAngle * 0.15;

    this.joints.neckMid.rotation.z = -roll * 0.2;
    this.joints.neckMid.rotation.x = -0.42 + Math.cos(time * 3.0) * 0.05;

    this.joints.neckUpper.rotation.y = -carveAngle * 0.4 + 0.15;
    this.joints.neckUpper.rotation.z = roll * 0.1;

    // Head stays level with the horizon and anticipates the exit of the wave
    this.joints.head.rotation.z = roll * 0.45;
    this.joints.head.rotation.x = -0.1 + (inBarrel ? 0.25 : 0.05) + Math.sin(time * 2.5) * 0.03;
    this.joints.head.rotation.y = -carveAngle * 0.25 + 0.1;

    // Head crest feathers flutter in the offshore wind
    const crestFlutter = Math.sin(time * 12.0) * 0.08 + (speed * 0.05);
    this.joints.crest.rotation.x = crestFlutter;

    // 3. WINGS FOR BALANCE & AERODYNAMIC STABILITY
    // Left wing (inside wave face): dips low to graze or balance
    // Right wing (outside): lifts high for counterbalance and wind trim
    const wingFlap = Math.sin(time * 5.0) * 0.08;
    const { left, right } = this.joints.wings;

    if (left && right) {
      // Left Wing
      left.shoulder.rotation.z = -0.45 + carveAngle * 0.45 + wingFlap;
      left.shoulder.rotation.x = 0.15 - roll * 0.3;
      left.elbow.rotation.z = -0.3 + carveAngle * 0.2;
      left.wrist.rotation.y = Math.sin(time * 6.0) * 0.06;
      left.primaries.rotation.z = -carveAngle * 0.3 + Math.sin(time * 9.0) * 0.05;

      // Right Wing
      right.shoulder.rotation.z = 0.65 + carveAngle * 0.4 - wingFlap;
      right.shoulder.rotation.x = -0.15 + roll * 0.3;
      right.elbow.rotation.z = 0.4 + carveAngle * 0.25;
      right.wrist.rotation.y = -Math.sin(time * 6.0) * 0.06;
      right.primaries.rotation.z = carveAngle * 0.25 + Math.cos(time * 9.0) * 0.05;
    }

    // 4. TAIL TRIM
    this.joints.tail.rotation.y = -carveAngle * 0.4;
    this.joints.tail.rotation.x = Math.sin(time * 4.0) * 0.08 - 0.2;

    // 5. GULAR POUCH SECONDARY MOTION (JIGGLE & AIR BILLOW)
    // Deform pouch vertices dynamically
    this.pouchPhase += delta * (8.0 + speed * 4.0);
    if (this.pouchMesh && this.pouchOrigPos) {
      const pos = this.pouchMesh.geometry.attributes.position;
      const orig = this.pouchOrigPos;
      const count = pos.count;

      for (let i = 0; i < count; i++) {
        const ox = orig.getX(i);
        const oy = orig.getY(i);
        const oz = orig.getZ(i);

        // Ripple based on height and Z position
        const ripple = Math.sin(this.pouchPhase + oz * 4.0) * 0.018 * (1.0 - oy * 2.0);
        const windBulge = (speed * 0.035) * Math.sin(oz * Math.PI * 0.8);

        pos.setXYZ(i, ox + ripple, oy - Math.abs(ripple) * 0.6 - windBulge * 0.4, oz);
      }
      pos.needsUpdate = true;
      this.pouchMesh.geometry.computeVertexNormals();
    }

    // 6. HAWAIIAN LEI FLUTTER
    this.joints.lei.rotation.y = Math.sin(time * 3.5) * 0.08 + carveAngle * 0.1;
    this.joints.lei.rotation.z = Math.cos(time * 4.0) * 0.05;
  }
}
