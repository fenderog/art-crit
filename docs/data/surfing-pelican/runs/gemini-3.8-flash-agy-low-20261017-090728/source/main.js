import * as THREE from 'three';

// -------------------------------------------------------------
// Scene, Camera & Renderer Setup
// -------------------------------------------------------------
const canvas = document.getElementById('webgl-canvas');
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x133854, 0.012);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 3, 11);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: 'high-performance'
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

// -------------------------------------------------------------
// Procedural Textures
// -------------------------------------------------------------
function createFoamTexture() {
  const size = 512;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Background ocean blue/green
  ctx.fillStyle = '#0f4d6d';
  ctx.fillRect(0, 0, size, size);

  // Sea foam lacing & bubbles
  for (let i = 0; i < 2200; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const r = Math.random() * 5 + 1;
    const alpha = Math.random() * 0.7 + 0.2;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(235, 252, 255, ${alpha})`;
    ctx.fill();
  }

  // Organic foam streaks
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.lineWidth = 2.5;
  for (let i = 0; i < 120; i++) {
    ctx.beginPath();
    let cx = Math.random() * size;
    let cy = Math.random() * size;
    ctx.moveTo(cx, cy);
    for (let j = 0; j < 4; j++) {
      cx += (Math.random() - 0.5) * 60;
      cy += Math.random() * 30;
      ctx.lineTo(cx, cy);
    }
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 2);
  return texture;
}

function createSurfboardTexture() {
  const size = 512;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Base vibrant turquoise
  const grad = ctx.createLinearGradient(0, 0, size, size);
  grad.addColorStop(0, '#02c4b8');
  grad.addColorStop(0.5, '#00a39a');
  grad.addColorStop(1, '#006e68');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // Racing sunset stripes
  ctx.fillStyle = '#ff7b25';
  ctx.fillRect(size * 0.35, 0, size * 0.08, size);
  ctx.fillStyle = '#ffc83b';
  ctx.fillRect(size * 0.43, 0, size * 0.05, size);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(size * 0.48, 0, size * 0.04, size);

  // Center balsa stringer line
  ctx.fillStyle = '#4a2500';
  ctx.fillRect(size * 0.495, 0, size * 0.01, size);

  // Deck traction pad at the tail
  ctx.fillStyle = 'rgba(20, 20, 20, 0.85)';
  ctx.fillRect(size * 0.25, size * 0.72, size * 0.5, size * 0.22);

  // Grip texture on pad
  ctx.fillStyle = '#444';
  for (let x = size * 0.26; x < size * 0.74; x += 12) {
    for (let y = size * 0.73; y < size * 0.93; y += 12) {
      ctx.fillRect(x, y, 6, 6);
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

function createSkyGradientTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  // Tropical golden hour sky
  const grad = ctx.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0.0, '#103957'); // deep azure zenith
  grad.addColorStop(0.45, '#357b99'); // warm sky
  grad.addColorStop(0.7, '#ff9e54'); // golden orange horizon
  grad.addColorStop(0.85, '#ffcf77'); // sun glow
  grad.addColorStop(1.0, '#ffd899'); // haze
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 512, 512);

  return new THREE.CanvasTexture(canvas);
}

// -------------------------------------------------------------
// Sky Dome, Sun & Environment
// -------------------------------------------------------------
const skyGeo = new THREE.SphereGeometry(300, 32, 24);
const skyMat = new THREE.MeshBasicMaterial({
  map: createSkyGradientTexture(),
  side: THREE.BackSide
});
const skyDome = new THREE.Mesh(skyGeo, skyMat);
scene.add(skyDome);

// Glowing Sun Disc
const sunGroup = new THREE.Group();
const sunGeo = new THREE.CircleGeometry(14, 32);
const sunMat = new THREE.MeshBasicMaterial({
  color: 0xfffae0,
  side: THREE.DoubleSide
});
const sunDisc = new THREE.Mesh(sunGeo, sunMat);
sunGroup.add(sunDisc);

// Sun Corona Halo
const coronaGeo = new THREE.RingGeometry(14, 36, 32);
const coronaMat = new THREE.MeshBasicMaterial({
  color: 0xffaa44,
  side: THREE.DoubleSide,
  transparent: true,
  opacity: 0.45
});
const corona = new THREE.Mesh(coronaGeo, coronaMat);
sunGroup.add(corona);

sunGroup.position.set(-60, 45, -180);
sunGroup.lookAt(0, 0, 0);
scene.add(sunGroup);

// Distant Low-Poly Tropical Islands
const islandMat = new THREE.MeshLambertMaterial({ color: 0x0c2538, flatShading: true });
for (let i = 0; i < 4; i++) {
  const island = new THREE.Mesh(
    new THREE.ConeGeometry(25 + Math.random() * 20, 20 + Math.random() * 25, 6),
    islandMat
  );
  island.position.set(-160 + i * 90 + (Math.random() - 0.5) * 30, -5, -220 + (Math.random() - 0.5) * 40);
  island.scale.set(1.4, 0.7, 1.2);
  scene.add(island);
}

// -------------------------------------------------------------
// Lighting
// -------------------------------------------------------------
const ambientLight = new THREE.AmbientLight(0x76b8d6, 1.2);
scene.add(ambientLight);

// Primary golden sun light
const sunLight = new THREE.DirectionalLight(0xfff0c4, 2.8);
sunLight.position.set(-40, 50, -20);
sunLight.castShadow = true;
sunLight.shadow.mapSize.width = 2048;
sunLight.shadow.mapSize.height = 2048;
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 120;
sunLight.shadow.camera.left = -18;
sunLight.shadow.camera.right = 18;
sunLight.shadow.camera.top = 18;
sunLight.shadow.camera.bottom = -18;
sunLight.shadow.bias = -0.0005;
scene.add(sunLight);

// Backlight / Rim light for translucent wave barrel
const rimLight = new THREE.DirectionalLight(0x4be6c5, 2.2);
rimLight.position.set(30, 25, -35);
scene.add(rimLight);

// -------------------------------------------------------------
// The Great Barrel Wave
// -------------------------------------------------------------
const foamTex = createFoamTexture();

// Ocean Wave Materials
const waveMaterial = new THREE.MeshPhysicalMaterial({
  color: 0x0d7c99,
  emissive: 0x032230,
  roughness: 0.12,
  metalness: 0.05,
  transmission: 0.45,
  ior: 1.333,
  reflectivity: 0.8,
  clearcoat: 1.0,
  clearcoatRoughness: 0.08,
  flatShading: false,
  map: foamTex,
  side: THREE.DoubleSide
});

const foamMaterial = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.88,
  map: foamTex,
  side: THREE.DoubleSide
});

// Construct parametric curling wave barrel
const waveWidth = 140; // along wave line (X axis)
const waveSegmentsX = 85;
const waveSegmentsY = 65;
const waveGeo = new THREE.PlaneGeometry(waveWidth, 38, waveSegmentsX, waveSegmentsY);

// Curving the plane into an iconic breaking tube
const posAttr = waveGeo.attributes.position;
const originalPositions = new Float32Array(posAttr.count * 3);

for (let i = 0; i < posAttr.count; i++) {
  const x = posAttr.getX(i);
  const v = (posAttr.getY(i) + 19) / 38; // 0 to 1 along wave profile

  // Parametric curling wave curve
  let y = 0;
  let z = 0;

  if (v < 0.35) {
    // Ocean base / flat water into the trough
    const t = v / 0.35;
    y = -1.2 + t * 1.5;
    z = (1.0 - t) * 22;
  } else if (v < 0.75) {
    // Face of the wave wall rising vertically
    const t = (v - 0.35) / 0.4;
    const angle = t * Math.PI * 0.58;
    y = 0.3 + Math.sin(angle) * 7.5;
    z = Math.cos(angle) * 6.5 - 2.5;
  } else {
    // Lip throwing forward and curling over
    const t = (v - 0.75) / 0.25;
    const angle = Math.PI * 0.58 + t * Math.PI * 0.75;
    y = 6.8 + Math.sin(angle) * 3.2;
    z = Math.cos(angle) * 4.8 - 2.0;
  }

  posAttr.setXYZ(i, x, y, z);
  originalPositions[i * 3 + 0] = x;
  originalPositions[i * 3 + 1] = y;
  originalPositions[i * 3 + 2] = z;
}

waveGeo.computeVertexNormals();
const waveMesh = new THREE.Mesh(waveGeo, waveMaterial);
waveMesh.receiveShadow = true;
scene.add(waveMesh);

// Foaming wave lip strip
const lipGeo = new THREE.CylinderGeometry(0.35, 0.6, waveWidth, 12, waveSegmentsX, true);
lipGeo.rotateZ(Math.PI / 2);
const lipMesh = new THREE.Mesh(lipGeo, foamMaterial);
lipMesh.position.set(0, 7.3, 1.1);
scene.add(lipMesh);

// Flat ocean floor / surrounding water
const oceanFloorGeo = new THREE.PlaneGeometry(280, 280, 48, 48);
oceanFloorGeo.rotateX(-Math.PI / 2);
const oceanFloorMat = new THREE.MeshPhysicalMaterial({
  color: 0x08425b,
  roughness: 0.2,
  metalness: 0.1,
  clearcoat: 0.8,
  map: foamTex
});
const oceanFloor = new THREE.Mesh(oceanFloorGeo, oceanFloorMat);
oceanFloor.position.set(0, -1.2, 70);
oceanFloor.receiveShadow = true;
scene.add(oceanFloor);

// -------------------------------------------------------------
// Water Spray & Mist Particles
// -------------------------------------------------------------
const sprayCount = 450;
const sprayGeo = new THREE.BufferGeometry();
const sprayPositions = new Float32Array(sprayCount * 3);
const sprayVelocities = new Float32Array(sprayCount * 3);
const sprayLives = new Float32Array(sprayCount);

for (let i = 0; i < sprayCount; i++) {
  // Spawn along the curling lip and board wake
  sprayPositions[i * 3 + 0] = (Math.random() - 0.5) * 50;
  sprayPositions[i * 3 + 1] = 6.5 + Math.random() * 1.5;
  sprayPositions[i * 3 + 2] = 0.5 + Math.random() * 2.0;

  sprayVelocities[i * 3 + 0] = (Math.random() - 0.5) * 2.0;
  sprayVelocities[i * 3 + 1] = -Math.random() * 4.0 - 1.0;
  sprayVelocities[i * 3 + 2] = Math.random() * 3.5 + 2.0;

  sprayLives[i] = Math.random();
}

sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPositions, 3));

// Procedural soft circle sprite for particles
const pCanvas = document.createElement('canvas');
pCanvas.width = 64;
pCanvas.height = 64;
const pCtx = pCanvas.getContext('2d');
const pGrad = pCtx.createRadialGradient(32, 32, 0, 32, 32, 30);
pGrad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
pGrad.addColorStop(0.5, 'rgba(220, 245, 255, 0.6)');
pGrad.addColorStop(1, 'rgba(220, 245, 255, 0)');
pCtx.fillStyle = pGrad;
pCtx.fillRect(0, 0, 64, 64);
const pTex = new THREE.CanvasTexture(pCanvas);

const sprayMat = new THREE.PointsMaterial({
  size: 0.6,
  map: pTex,
  transparent: true,
  opacity: 0.75,
  depthWrite: false,
  blending: THREE.AdditiveBlending
});

const sprayParticles = new THREE.Points(sprayGeo, sprayMat);
scene.add(sprayParticles);

// Board Wake Spray Particles
const wakeCount = 180;
const wakeGeo = new THREE.BufferGeometry();
const wakePositions = new Float32Array(wakeCount * 3);
const wakeVelocities = new Float32Array(wakeCount * 3);
const wakeLives = new Float32Array(wakeCount);

for (let i = 0; i < wakeCount; i++) {
  wakePositions[i * 3 + 0] = 0;
  wakePositions[i * 3 + 1] = 0;
  wakePositions[i * 3 + 2] = 0;

  wakeVelocities[i * 3 + 0] = -(Math.random() * 3.5 + 1.0);
  wakeVelocities[i * 3 + 1] = Math.random() * 3.5 + 1.0;
  wakeVelocities[i * 3 + 2] = (Math.random() - 0.5) * 2.0;

  wakeLives[i] = Math.random();
}

wakeGeo.setAttribute('position', new THREE.BufferAttribute(wakePositions, 3));
const wakeMat = new THREE.PointsMaterial({
  size: 0.45,
  map: pTex,
  transparent: true,
  opacity: 0.85,
  depthWrite: false,
  blending: THREE.AdditiveBlending
});
const wakeParticles = new THREE.Points(wakeGeo, wakeMat);
scene.add(wakeParticles);

// -------------------------------------------------------------
// Procedural Surfboard & Surfing Pelican
// -------------------------------------------------------------
const surferGroup = new THREE.Group();
scene.add(surferGroup);

// --- 1. SURFBOARD ---
const surfboardGroup = new THREE.Group();
surferGroup.add(surfboardGroup);

const boardShape = new THREE.Shape();
// Classic surfboard outline
boardShape.moveTo(0, 3.2); // Pointed nose
boardShape.bezierCurveTo(0.65, 2.2, 0.78, 0.5, 0.72, -1.2);
boardShape.bezierCurveTo(0.68, -2.2, 0.52, -2.8, 0.35, -3.1); // Pin tail
boardShape.lineTo(-0.35, -3.1);
boardShape.bezierCurveTo(-0.52, -2.8, -0.68, -2.2, -0.72, -1.2);
boardShape.bezierCurveTo(-0.78, 0.5, -0.65, 2.2, 0, 3.2);

const extrudeSettings = {
  depth: 0.14,
  bevelEnabled: true,
  bevelSegments: 4,
  steps: 1,
  bevelSize: 0.08,
  bevelThickness: 0.06
};

const boardGeo = new THREE.ExtrudeGeometry(boardShape, extrudeSettings);
boardGeo.rotateX(Math.PI / 2);
boardGeo.rotateY(Math.PI / 2);
boardGeo.scale(0.85, 0.8, 1.25);

// Add Rocker curve (banana curvature along board length)
const bPos = boardGeo.attributes.position;
for (let i = 0; i < bPos.count; i++) {
  const x = bPos.getX(i);
  // Nose kick & tail kick
  const rocker = 0.04 * (x * x);
  bPos.setY(i, bPos.getY(i) + rocker);
}
boardGeo.computeVertexNormals();

const boardTex = createSurfboardTexture();
boardTex.wrapS = THREE.RepeatWrapping;
boardTex.wrapT = THREE.RepeatWrapping;
boardTex.repeat.set(1, 1);

const boardMat = new THREE.MeshPhysicalMaterial({
  map: boardTex,
  color: 0xffffff,
  roughness: 0.15,
  metalness: 0.1,
  clearcoat: 1.0,
  clearcoatRoughness: 0.05
});

const surfboardMesh = new THREE.Mesh(boardGeo, boardMat);
surfboardMesh.castShadow = true;
surfboardMesh.receiveShadow = true;
surfboardGroup.add(surfboardMesh);

// Twin Thruster Fins underneath
const finShape = new THREE.Shape();
finShape.moveTo(0, 0);
finShape.bezierCurveTo(0.05, 0.1, 0.1, 0.3, 0.02, 0.55);
finShape.lineTo(-0.15, 0.45);
finShape.bezierCurveTo(-0.12, 0.25, -0.1, 0.1, -0.25, 0);
finShape.closePath();

const finGeo = new THREE.ExtrudeGeometry(finShape, { depth: 0.04, bevelEnabled: true, bevelThickness: 0.01, bevelSize: 0.01 });
finGeo.rotateZ(Math.PI);
const finMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.3 });

const finLeft = new THREE.Mesh(finGeo, finMat);
finLeft.position.set(-2.5, -0.1, 0.4);
finLeft.scale.set(0.8, 0.8, 0.8);
surfboardGroup.add(finLeft);

const finRight = new THREE.Mesh(finGeo, finMat);
finRight.position.set(-2.5, -0.1, -0.4);
finRight.scale.set(0.8, 0.8, 0.8);
surfboardGroup.add(finRight);

const finCenter = new THREE.Mesh(finGeo, finMat);
finCenter.position.set(-2.9, -0.1, 0.0);
finCenter.scale.set(0.85, 0.85, 0.85);
surfboardGroup.add(finCenter);

// --- 2. PELICAN CHARACTER ---
const pelican = new THREE.Group();
surfboardGroup.add(pelican);
pelican.position.set(-0.2, 0.2, 0);

// Materials
const featherWhite = new THREE.MeshStandardMaterial({
  color: 0xf4f7fa,
  roughness: 0.7,
  metalness: 0.05
});

const featherGrey = new THREE.MeshStandardMaterial({
  color: 0x9fa9b3,
  roughness: 0.75,
  metalness: 0.05
});

const featherDark = new THREE.MeshStandardMaterial({
  color: 0x3d4349,
  roughness: 0.8
});

const beakOrange = new THREE.MeshStandardMaterial({
  color: 0xff8c1a,
  roughness: 0.35,
  metalness: 0.1
});

const pouchPink = new THREE.MeshPhysicalMaterial({
  color: 0xff8566,
  roughness: 0.3,
  transmission: 0.4,
  thickness: 0.6,
  ior: 1.35
});

const legOrange = new THREE.MeshStandardMaterial({
  color: 0xf57c00,
  roughness: 0.5
});

// Legs & Webbed Feet (Athletic surfer stance)
function createWebbedFoot() {
  const foot = new THREE.Group();

  // Shin bone
  const shinGeo = new THREE.CylinderGeometry(0.08, 0.07, 0.85, 10);
  const shin = new THREE.Mesh(shinGeo, legOrange);
  shin.position.y = 0.42;
  shin.castShadow = true;
  foot.add(shin);

  // Knobby knee joint
  const kneeGeo = new THREE.SphereGeometry(0.11, 10, 10);
  const knee = new THREE.Mesh(kneeGeo, legOrange);
  knee.position.y = 0.85;
  foot.add(knee);

  // Webbed foot plate
  const webShape = new THREE.Shape();
  webShape.moveTo(-0.25, 0.4);
  webShape.lineTo(-0.18, 0.55);
  webShape.lineTo(0.0, 0.6);
  webShape.lineTo(0.18, 0.55);
  webShape.lineTo(0.25, 0.4);
  webShape.lineTo(0.08, 0.0);
  webShape.lineTo(-0.08, 0.0);
  webShape.closePath();

  const webGeo = new THREE.ExtrudeGeometry(webShape, { depth: 0.03, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02 });
  webGeo.rotateX(-Math.PI / 2);
  const webMesh = new THREE.Mesh(webGeo, legOrange);
  webMesh.position.set(0, 0.02, -0.2);
  webMesh.castShadow = true;
  webMesh.receiveShadow = true;
  foot.add(webMesh);

  // Claws
  for (let c = -1; c <= 1; c++) {
    const clawGeo = new THREE.ConeGeometry(0.03, 0.12, 6);
    clawGeo.rotateX(Math.PI / 2);
    const claw = new THREE.Mesh(clawGeo, featherDark);
    claw.position.set(c * 0.18, 0.02, 0.38);
    foot.add(claw);
  }

  return foot;
}

// Left Foot (Front foot, angled forward-left)
const footL = createWebbedFoot();
footL.position.set(0.9, 0, 0.28);
footL.rotation.set(-0.15, 0.35, -0.2);
pelican.add(footL);

// Right Foot (Back foot, perpendicular carving grip)
const footR = createWebbedFoot();
footR.position.set(-1.0, 0, -0.25);
footR.rotation.set(0.18, -0.4, 0.15);
pelican.add(footR);

// Pelican Pelvis & Torso (Crouched athletic surfing balance)
const bodyRoot = new THREE.Group();
bodyRoot.position.set(0, 0.85, 0);
pelican.add(bodyRoot);

// Plump Torso
const bodyGeo = new THREE.SphereGeometry(0.85, 24, 20);
bodyGeo.scale(1.35, 0.95, 0.85);
const bodyMesh = new THREE.Mesh(bodyGeo, featherWhite);
bodyMesh.castShadow = true;
bodyMesh.receiveShadow = true;
bodyRoot.add(bodyMesh);

// Grey feathered saddle / back
const saddleGeo = new THREE.SphereGeometry(0.86, 20, 16);
saddleGeo.scale(1.2, 0.85, 0.8);
const saddleMesh = new THREE.Mesh(saddleGeo, featherGrey);
saddleMesh.position.set(-0.15, 0.2, 0);
bodyRoot.add(saddleMesh);

// Tail Feathers Fan
const tailGroup = new THREE.Group();
tailGroup.position.set(-1.05, 0.2, 0);
bodyRoot.add(tailGroup);

for (let i = -2; i <= 2; i++) {
  const fGeo = new THREE.BoxGeometry(0.7, 0.04, 0.18);
  fGeo.translate(-0.35, 0, 0);
  const feather = new THREE.Mesh(fGeo, i % 2 === 0 ? featherDark : featherGrey);
  feather.rotation.y = i * 0.14;
  feather.rotation.z = -0.15 + Math.abs(i) * 0.05;
  feather.castShadow = true;
  tailGroup.add(feather);
}

// --- WINGS (Spanning wide for surfing balance!) ---
function createWing(isLeft) {
  const wingRoot = new THREE.Group();
  const sign = isLeft ? 1 : -1;

  // Inner wing (Shoulder to elbow)
  const innerGeo = new THREE.BoxGeometry(0.9, 0.16, 0.45);
  innerGeo.translate(0.45 * sign, 0, 0);
  const innerWing = new THREE.Mesh(innerGeo, featherWhite);
  innerWing.castShadow = true;
  wingRoot.add(innerWing);

  // Outer wing (Elbow to primary feathers)
  const outerJoint = new THREE.Group();
  outerJoint.position.set(0.9 * sign, 0, 0);
  wingRoot.add(outerJoint);

  const outerGeo = new THREE.BoxGeometry(1.2, 0.12, 0.38);
  outerGeo.translate(0.6 * sign, 0, 0);
  const outerWing = new THREE.Mesh(outerGeo, featherGrey);
  outerWing.castShadow = true;
  outerJoint.add(outerWing);

  // Long primary flight feathers
  const featherCount = 6;
  for (let f = 0; f < featherCount; f++) {
    const pGeo = new THREE.ConeGeometry(0.08, 1.1, 5);
    pGeo.rotateZ(sign * Math.PI / 2);
    pGeo.scale(1, 0.15, 1);
    const primFeather = new THREE.Mesh(pGeo, featherDark);
    primFeather.position.set((0.4 + f * 0.16) * sign, -0.02, -0.2 + f * 0.09);
    primFeather.rotation.y = sign * (0.15 + f * 0.08);
    primFeather.castShadow = true;
    outerJoint.add(primFeather);
  }

  return { wingRoot, outerJoint };
}

// Left Wing (Dipping low toward wave surface - classic surfer hand drag)
const wingLData = createWing(true);
wingLData.wingRoot.position.set(0.2, 0.3, 0.65);
wingLData.wingRoot.rotation.set(0.4, 0.25, -0.4);
wingLData.outerJoint.rotation.set(-0.2, 0.1, -0.25);
bodyRoot.add(wingLData.wingRoot);

// Right Wing (Raised high for aerodynamic balance)
const wingRData = createWing(false);
wingRData.wingRoot.position.set(0.2, 0.3, -0.65);
wingRData.wingRoot.rotation.set(-0.35, -0.2, 0.35);
wingRData.outerJoint.rotation.set(0.25, -0.15, 0.3);
bodyRoot.add(wingRData.wingRoot);

// --- TROPICAL HAWAIIAN LEI (Floral Garland) ---
const leiGroup = new THREE.Group();
leiGroup.position.set(0.85, 0.3, 0);
bodyRoot.add(leiGroup);

const flowerColors = [0xff2a55, 0xffbb00, 0xff66cc, 0xffffff, 0xff5500];
const flowerCount = 18;
for (let i = 0; i < flowerCount; i++) {
  const theta = (i / flowerCount) * Math.PI * 2;
  const radY = 0.52;
  const radZ = 0.58;
  const fX = Math.cos(theta) * 0.15;
  const fY = Math.sin(theta) * radY;
  const fZ = Math.cos(theta) * radZ;

  const blossom = new THREE.Mesh(
    new THREE.DodecahedronGeometry(0.12, 0),
    new THREE.MeshStandardMaterial({
      color: flowerColors[i % flowerColors.length],
      roughness: 0.4
    })
  );
  blossom.position.set(fX, fY, fZ);
  blossom.rotation.set(Math.random(), Math.random(), Math.random());
  leiGroup.add(blossom);
}

// --- NECK & HEAD (Iconic S-Curve) ---
const neckGroup = new THREE.Group();
neckGroup.position.set(0.9, 0.35, 0);
bodyRoot.add(neckGroup);

// Segmented graceful neck
const neckSegments = 5;
const neckBones = [];
let prevJoint = neckGroup;

for (let s = 0; s < neckSegments; s++) {
  const joint = new THREE.Group();
  joint.position.set(0.22, 0.18, 0);

  const radius = 0.28 - s * 0.025;
  const nMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radius * 0.9, radius, 0.28, 12),
    featherWhite
  );
  nMesh.rotation.z = -Math.PI / 4;
  nMesh.castShadow = true;
  joint.add(nMesh);

  prevJoint.add(joint);
  neckBones.push(joint);
  prevJoint = joint;
}

// Head & Bill
const headGroup = new THREE.Group();
prevJoint.add(headGroup);
headGroup.position.set(0.25, 0.2, 0);

// Skull
const headGeo = new THREE.SphereGeometry(0.36, 16, 14);
headGeo.scale(1.2, 1.0, 0.9);
const headMesh = new THREE.Mesh(headGeo, featherWhite);
headMesh.castShadow = true;
headGroup.add(headMesh);

// Cool Pelican Head Feather Crest
const crestGeo = new THREE.ConeGeometry(0.12, 0.4, 6);
crestGeo.rotateZ(-Math.PI / 2.6);
const crest = new THREE.Mesh(crestGeo, featherGrey);
crest.position.set(-0.35, 0.22, 0);
headGroup.add(crest);

// Eyes
const eyeWhiteMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
const eyePupilMat = new THREE.MeshBasicMaterial({ color: 0x111111 });

for (let side of [-1, 1]) {
  const eyeBall = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 10), eyeWhiteMat);
  eyeBall.position.set(0.18, 0.1, side * 0.26);
  headGroup.add(eyeBall);

  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), eyePupilMat);
  pupil.position.set(0.24, 0.1, side * 0.29);
  headGroup.add(pupil);
}

// Pelican Upper Bill (Long hooked beak)
const beakGroup = new THREE.Group();
headGroup.add(beakGroup);
beakGroup.position.set(0.35, -0.02, 0);

const beakShape = new THREE.Shape();
beakShape.moveTo(0, 0.12);
beakShape.lineTo(1.8, 0.05);
beakShape.lineTo(1.95, -0.05); // Hook tip
beakShape.lineTo(1.85, -0.07);
beakShape.lineTo(0, -0.05);
beakShape.closePath();

const beakExtrude = new THREE.ExtrudeGeometry(beakShape, {
  depth: 0.22,
  bevelEnabled: true,
  bevelThickness: 0.03,
  bevelSize: 0.03
});
beakExtrude.translate(0, 0, -0.11);
const beakMesh = new THREE.Mesh(beakExtrude, beakOrange);
beakMesh.castShadow = true;
beakGroup.add(beakMesh);

// Hook tip nail
const nailGeo = new THREE.SphereGeometry(0.08, 10, 10);
const nail = new THREE.Mesh(nailGeo, featherDark);
nail.position.set(1.92, -0.03, 0);
nail.scale.set(1.2, 1.8, 0.8);
beakGroup.add(nail);

// Iconic Flexible Throat Pouch (Gular pouch)
const pouchGeo = new THREE.SphereGeometry(0.65, 20, 16);
pouchGeo.scale(1.8, 0.75, 0.45);
pouchGeo.translate(0.7, -0.42, 0);
const pouchMesh = new THREE.Mesh(pouchGeo, pouchPink);
pouchMesh.castShadow = true;
beakGroup.add(pouchMesh);

// --- COOL SURFER SUNGLASSES ---
const glassesGroup = new THREE.Group();
glassesGroup.position.set(0.24, 0.12, 0);
headGroup.add(glassesGroup);

const frameMat = new THREE.MeshStandardMaterial({
  color: 0x111111,
  roughness: 0.2,
  metalness: 0.8
});

const lensMat = new THREE.MeshPhysicalMaterial({
  color: 0x00f0ff,
  roughness: 0.05,
  metalness: 0.95,
  reflectivity: 1.0,
  clearcoat: 1.0,
  clearcoatRoughness: 0.02
});

for (let s of [-1, 1]) {
  // Lens Frame
  const fGeo = new THREE.TorusGeometry(0.13, 0.03, 8, 16);
  fGeo.rotateY(Math.PI / 2);
  const frame = new THREE.Mesh(fGeo, frameMat);
  frame.position.set(0.05, 0, s * 0.26);
  glassesGroup.add(frame);

  // Mirrored Lens
  const lGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.02, 16);
  lGeo.rotateZ(Math.PI / 2);
  const lens = new THREE.Mesh(lGeo, lensMat);
  lens.position.set(0.05, 0, s * 0.26);
  glassesGroup.add(lens);
}

// Bridge across the bill
const bridgeGeo = new THREE.CylinderGeometry(0.025, 0.025, 0.48, 8);
const bridge = new THREE.Mesh(bridgeGeo, frameMat);
bridge.position.set(0.06, 0.05, 0);
glassesGroup.add(bridge);

// Neon pink sunglasses strap around the back of the head
const strapGeo = new THREE.TorusGeometry(0.34, 0.025, 8, 24, Math.PI);
strapGeo.rotateZ(Math.PI / 2);
const strapMat = new THREE.MeshBasicMaterial({ color: 0xff1493 });
const strap = new THREE.Mesh(strapGeo, strapMat);
strap.position.set(-0.1, 0.02, 0);
glassesGroup.add(strap);

// -------------------------------------------------------------
// Animation & Dynamic Simulation
// -------------------------------------------------------------
const clock = new THREE.Clock();
let wakeIndex = 0;

function updateWave(time) {
  const p = waveGeo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const origX = originalPositions[i * 3 + 0];
    const origY = originalPositions[i * 3 + 1];
    const origZ = originalPositions[i * 3 + 2];

    // Swell undulation traveling along the wave face
    const waveUndulation = Math.sin(origX * 0.12 + time * 3.5) * 0.35 +
                           Math.cos(origZ * 0.25 - time * 2.8) * 0.25;

    p.setY(i, origY + waveUndulation);
    p.setZ(i, origZ + Math.sin(origX * 0.08 + time * 2.0) * 0.15);
  }
  p.needsUpdate = true;
  waveGeo.computeVertexNormals();

  // Scroll foam texture to give rushing speed illusion
  foamTex.offset.x = (time * 0.45) % 1;
}

function updateParticles(dt, time) {
  // Wave lip spray
  const sPos = sprayGeo.attributes.position.array;
  for (let i = 0; i < sprayCount; i++) {
    sprayLives[i] -= dt * 0.8;
    if (sprayLives[i] <= 0) {
      sprayLives[i] = 1.0;
      sPos[i * 3 + 0] = surferGroup.position.x + (Math.random() - 0.5) * 35;
      sPos[i * 3 + 1] = 6.8 + Math.random() * 1.0;
      sPos[i * 3 + 2] = 0.5 + Math.random() * 1.5;
    } else {
      sPos[i * 3 + 0] += sprayVelocities[i * 3 + 0] * dt;
      sPos[i * 3 + 1] += sprayVelocities[i * 3 + 1] * dt;
      sPos[i * 3 + 2] += sprayVelocities[i * 3 + 2] * dt;
    }
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // Surfboard wake spray (rooster tail)
  const wPos = wakeGeo.attributes.position.array;
  const boardWorldPos = new THREE.Vector3();
  surfboardMesh.getWorldPosition(boardWorldPos);

  for (let k = 0; k < 3; k++) {
    const idx = (wakeIndex + k) % wakeCount;
    wPos[idx * 3 + 0] = boardWorldPos.x - 2.2 + (Math.random() - 0.5) * 0.3;
    wPos[idx * 3 + 1] = boardWorldPos.y + 0.1;
    wPos[idx * 3 + 2] = boardWorldPos.z + (Math.random() - 0.5) * 0.4;
    wakeVelocities[idx * 3 + 0] = -Math.random() * 5.0 - 2.0;
    wakeVelocities[idx * 3 + 1] = Math.random() * 4.0 + 1.5;
    wakeVelocities[idx * 3 + 2] = (Math.random() - 0.5) * 3.0;
    wakeLives[idx] = 1.0;
  }
  wakeIndex = (wakeIndex + 3) % wakeCount;

  for (let i = 0; i < wakeCount; i++) {
    if (wakeLives[i] > 0) {
      wakeLives[i] -= dt * 1.2;
      wPos[i * 3 + 0] += wakeVelocities[i * 3 + 0] * dt;
      wPos[i * 3 + 1] += wakeVelocities[i * 3 + 1] * dt;
      wPos[i * 3 + 2] += wakeVelocities[i * 3 + 2] * dt;
      wakeVelocities[i * 3 + 1] -= 9.8 * dt * 0.5; // gravity on water spray
    }
  }
  wakeGeo.attributes.position.needsUpdate = true;
}

function updatePelicanAndBoard(time) {
  // Surfer rhythmic carving trajectory inside the barrel
  const carveCycle = time * 1.35;
  const carveX = Math.sin(carveCycle * 0.7) * 2.2;
  const carveY = 2.2 + Math.sin(carveCycle) * 1.6; // climbing up & bottom turning
  const carveZ = 1.2 + Math.cos(carveCycle) * 1.4; // deeper into pocket and back to shoulder

  surferGroup.position.set(carveX, carveY, carveZ);

  // Dynamic banking angles derived from carving trajectory
  const roll = Math.cos(carveCycle) * 0.35 + 0.15; // banking into the wave face
  const pitch = -Math.sin(carveCycle) * 0.25; // board nose down on drop, nose up on climb
  const yaw = Math.sin(carveCycle * 0.7) * 0.25; // carving directional turns

  surfboardGroup.rotation.set(pitch, yaw, roll);

  // Athletic compression / extension of knees and body
  const compression = (Math.sin(carveCycle) + 1.0) * 0.5; // 0 (stretched) to 1 (compressed)
  bodyRoot.position.y = 0.72 + (1.0 - compression) * 0.25;
  bodyRoot.position.z = Math.sin(carveCycle) * 0.15; // leaning body weight forward/back
  bodyRoot.rotation.z = -roll * 0.65; // upper body counter-balances board lean

  // Dynamic Wing Balance Motion
  // Fluttering primary feathers in high wind
  const flutter = Math.sin(time * 18.0) * 0.08;
  const gust = Math.sin(time * 3.5) * 0.15;

  // Left wing (low wave feeler)
  wingLData.wingRoot.rotation.z = -0.35 - compression * 0.2 + flutter;
  wingLData.outerJoint.rotation.z = -0.25 + gust;

  // Right wing (high balance antenna)
  wingRData.wingRoot.rotation.z = 0.35 + compression * 0.25 - flutter;
  wingRData.outerJoint.rotation.z = 0.3 - gust;

  // Neck and Head horizon stabilization
  neckBones[0].rotation.z = -0.1 + Math.sin(time * 3.0) * 0.05;
  neckBones[1].rotation.z = -0.15 + compression * 0.1;
  neckBones[2].rotation.z = 0.1 - compression * 0.08;
  headGroup.rotation.z = -roll * 0.3; // head stays level looking out the barrel
  headGroup.rotation.y = 0.2 + Math.sin(time * 1.8) * 0.15; // looking toward wave exit

  // Pelican Throat Pouch Inertial wobble
  pouchMesh.scale.y = 0.75 + Math.sin(time * 7.0) * 0.08 + compression * 0.1;
  pouchMesh.scale.z = 0.45 + Math.cos(time * 6.0) * 0.06;

  // Hawaiian Lei sway
  leiGroup.rotation.z = Math.sin(time * 4.0) * 0.1;
  leiGroup.rotation.x = Math.cos(time * 3.5) * 0.08;
}

// -------------------------------------------------------------
// Cinematic Non-Interactive Camera Choreography
// -------------------------------------------------------------
function updateCinematicCamera(time) {
  // Smooth panoramic orbital & tracking paths showcasing different dramatic angles:
  // 1. Barrel View (looking out through the curling tube)
  // 2. Head-on Hero Tracking Shot
  // 3. Wide Coastal Vista
  const camTime = time * 0.22;

  // Base camera coordinates
  const camDist = 9.5 + Math.sin(camTime * 1.8) * 2.5;
  const camAngle = camTime;

  const targetX = surferGroup.position.x * 0.65;
  const targetY = surferGroup.position.y * 0.8 + 0.8;
  const targetZ = surferGroup.position.z * 0.65;

  const eyeX = targetX + Math.sin(camAngle) * camDist * 0.8 + Math.cos(camTime * 0.7) * 2.0;
  const eyeY = 3.2 + Math.sin(camTime * 1.2) * 2.0;
  const eyeZ = targetZ + Math.cos(camAngle) * camDist * 0.6 + 5.5;

  camera.position.set(eyeX, eyeY, eyeZ);
  camera.lookAt(targetX, targetY, targetZ);
}

// -------------------------------------------------------------
// Animation Loop & Window Resize Handling
// -------------------------------------------------------------
function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.1);
  const time = clock.getElapsedTime();

  updateWave(time);
  updatePelicanAndBoard(time);
  updateParticles(dt, time);
  updateCinematicCamera(time);

  renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
  const w = window.innerWidth;
  const h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});
