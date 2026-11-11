import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

// ----- config -----
const prefersReduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
const V = new THREE.Vector3();

// ----- renderer & scene -----
const container = document.getElementById("app");
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe8f2, 24, 68);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(11, 4.2, 6);

// environment for nice PBR reflections
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ----- sky dome -----
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  depthWrite: false,
  uniforms: {
    topColor: { value: new THREE.Color(0x2e6ea3) },
    bottomColor: { value: new THREE.Color(0xf6e3c0) },
    bottom2: { value: new THREE.Color(0x9fd4e8) }
  },
  vertexShader: `
    varying vec3 vWorld;
    void main(){
      vec4 w = modelMatrix * vec4(position,1.0);
      vWorld = w.xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
    }`,
  fragmentShader: `
    uniform vec3 topColor;
    uniform vec3 bottomColor;
    uniform vec3 bottom2;
    varying vec3 vWorld;
    void main(){
      float h = normalize(vWorld).y;
      vec3 col;
      if(h > 0.0){
        float t = smoothstep(0.02, 0.65, h);
        col = mix(bottom2, topColor, t);
        // warm glow near horizon
        float g = pow(1.0 - abs(h), 4.0) * 0.45;
        col += vec3(1.0, 0.82, 0.55) * g;
      } else {
        col = mix(bottomColor, vec3(0.05,0.32,0.45), clamp(-h*3.0,0.0,1.0));
      }
      gl_FragColor = vec4(col, 1.0);
    }`
});
const sky = new THREE.Mesh(new THREE.SphereGeometry(80, 32, 20), skyMat);
scene.add(sky);

// sun disc (emissive sprite)
const sunSpriteTex = (() => {
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(64,64,8,64,64,64);
  grad.addColorStop(0, "rgba(255,242,180,1)");
  grad.addColorStop(0.25, "rgba(255,210,110,0.9)");
  grad.addColorStop(1, "rgba(255,210,110,0)");
  g.fillStyle = grad; g.fillRect(0,0,128,128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const sun = new THREE.Sprite(new THREE.SpriteMaterial({ map: sunSpriteTex, transparent: true, opacity: 0.95, depthWrite: false }));
sun.position.set(28, 22, -18);
sun.scale.set(26, 26, 1);
scene.add(sun);

// ----- lights -----
const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x1a7a8c, 1.05);
scene.add(hemi);
const sunLight = new THREE.DirectionalLight(0xffe7b0, 2.2);
sunLight.position.set(18, 20, -10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -18; sunLight.shadow.camera.right = 18;
sunLight.shadow.camera.top = 18; sunLight.shadow.camera.bottom = -18;
sunLight.shadow.camera.near = 1; sunLight.shadow.camera.far = 50;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
const fill = new THREE.DirectionalLight(0x8ec9ff, 0.55);
fill.position.set(-12, 8, 10);
scene.add(fill);

// ----- materials -----
const matWhite = new THREE.MeshStandardMaterial({ color: 0xffffffff, roughness: 0.58, metalness: 0 });
const matWhiteSoft = new THREE.MeshStandardMaterial({ color: 0xf2ece0, roughness: 0.68, metalness: 0 });
const matBlackTip = new THREE.MeshStandardMaterial({ color: 0x21262c, roughness: 0.6, metalness: 0 });
const matBeak = new THREE.MeshStandardMaterial({ color: 0xffa726, roughness: 0.42, metalness: 0, emissive: 0x2a1400, emissiveIntensity: 0.08 });
const matBeakTip = new THREE.MeshStandardMaterial({ color: 0xe66a15, roughness: 0.5, metalness: 0 });
const matPouch = new THREE.MeshStandardMaterial({ color: 0xffc08a, roughness: 0.6, metalness: 0, side: THREE.DoubleSide, emissive: 0x331a00, emissiveIntensity: 0.06 });
const matLeg = new THREE.MeshStandardMaterial({ color: 0xe07a1a, roughness: 0.6, metalness: 0 });
const matEye = new THREE.MeshStandardMaterial({ color: 0x0d1417, roughness: 0.15, metalness: 0.2 });
const matBoardTop = new THREE.MeshPhysicalMaterial({ color: 0x08a3bb, roughness: 0.28, metalness: 0.08, clearcoat: 0.6, clearcoatRoughness: 0.3 });
const matBoardBottom = new THREE.MeshPhysicalMaterial({ color: 0xff6b4a, roughness: 0.32, metalness: 0.05, clearcoat: 0.4, clearcoatRoughness: 0.35 });
const matFin = new THREE.MeshStandardMaterial({ color: 0x222a30, roughness: 0.4 });

// helper: rounded extrude shape -> mesh
function extrudeShape(shape, depth, bevel = 0.02) {
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize: bevel * 0.9,
    bevelSegments: 3,
    steps: 1,
    curveSegments: 18
  });
  geo.center();
  return geo;
}

// ----- surfboard -----
const boardGroup = new THREE.Group();
{
  const s = new THREE.Shape();
  // board outline in XY (length along Y then rotated)
  // nose at +Y (~2.2), tail at -Y (~-1.9)
  s.moveTo(0, 2.3);
  s.bezierCurveTo(0.55, 2.15, 0.62, 0.9, 0.58, 0.2);
  s.bezierCurveTo(0.55, -0.7, 0.42, -1.55, 0.30, -1.9);
  s.lineTo(0.12, -1.95);
  s.lineTo(0, -1.80);
  s.lineTo(-0.12, -1.95);
  s.lineTo(-0.30, -1.9);
  s.bezierCurveTo(-0.42, -1.55, -0.55, -0.7, -0.58, 0.2);
  s.bezierCurveTo(-0.62, 0.9, -0.55, 2.15, 0, 2.3);

  const boardGeo = extrudeShape(s, 0.14, 0.035);
  // extrude is in XY, depth Z. Rotate to lie flat with length along Z
  boardGeo.rotateX(Math.PI / 2);
  // now Y is thickness, Z is length? Let's check: original Y length -> after rotateX 90, Y->Z
  // thin dimension ends up along Y
  const deck = new THREE.Mesh(boardGeo, matBoardTop);
  deck.castShadow = true; deck.receiveShadow = true;
  boardGroup.add(deck);

  // stripe
  const stripeShape = new THREE.Shape();
  stripeShape.moveTo(0, 1.9);
  stripeShape.bezierCurveTo(0.22, 1.8, 0.28, 0.6, 0.24, 0.0);
  stripeShape.bezierCurveTo(0.20, -0.8, 0.16, -1.5, 0.10, -1.75);
  stripeShape.lineTo(-0.10, -1.75);
  stripeShape.bezierCurveTo(-0.16, -1.5, -0.20, -0.8, -0.24, 0.0);
  stripeShape.bezierCurveTo(-0.28, 0.6, -0.22, 1.8, 0, 1.9);
  const stripeGeo = extrudeShape(stripeShape, 0.145, 0.0);
  stripeGeo.rotateX(Math.PI / 2);
  const stripe = new THREE.Mesh(stripeGeo, new THREE.MeshStandardMaterial({ color: 0xfff6e8, roughness: 0.35 }));
  stripe.position.y = 0.012;
  boardGroup.add(stripe);

  // fins
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0); finShape.lineTo(0.28, 0.35); finShape.lineTo(0.30, -0.35); finShape.lineTo(0, 0);
  const finGeo = extrudeShape(finShape, 0.04, 0.015);
  const fin1 = new THREE.Mesh(finGeo, matFin);
  fin1.position.set(0.18, -0.10, -1.55); fin1.rotation.x = Math.PI;
  boardGroup.add(fin1);
  const fin2 = fin1.clone(); fin2.position.x = -0.18; boardGroup.add(fin2);

  // tail pad & front
  const noseLight = new THREE.Mesh(new THREE.CircleGeometry(0.07, 12), new THREE.MeshBasicMaterial({ color: 0xfff3b0 }));
  noseLight.rotation.x = -Math.PI/2; noseLight.position.set(0, 0.085, 2.05); boardGroup.add(noseLight);
}
boardGroup.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });

// ----- pelican -----
const rider = new THREE.Group();
rider.add(boardGroup);
const pelican = new THREE.Group();
pelican.position.y = 0.14; // on deck
rider.add(pelican);
scene.add(rider);

let wingLgeo, wingRgeo;
let wingL, wingR, headGroup, neckMesh, bodyMesh, tailMesh, pouchMesh, eyeL, eyeR;

{
  // BODY: sphere scaled to teardrop
  bodyMesh = new THREE.Mesh(new THREE.SphereGeometry(0.62, 32, 22), matWhite);
  bodyMesh.scale.set(0.95, 0.85, 1.25);
  bodyMesh.position.set(0, 0.68, -0.18);
  bodyMesh.castShadow = true;
  pelican.add(bodyMesh);

  // belly (lighter, slightly forward)
  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.52, 24, 18), matWhiteSoft);
  belly.scale.set(0.88, 0.78, 1.05);
  belly.position.set(0, 0.58, 0.18);
  belly.castShadow = true;
  pelican.add(belly);

  // tail fan - extruded rounded tip
  const tailShape = new THREE.Shape();
  tailShape.moveTo(0, 0);
  tailShape.bezierCurveTo(0.28, -0.08, 0.42, -0.32, 0.30, -0.58);
  tailShape.bezierCurveTo(0.18, -0.40, 0.10, -0.28, 0, -0.22);
  tailShape.bezierCurveTo(-0.10, -0.28, -0.18, -0.40, -0.30, -0.58);
  tailShape.bezierCurveTo(-0.42, -0.32, -0.28, -0.08, 0, 0);
  tailMesh = new THREE.Mesh(extrudeShape(tailShape, 0.09, 0.02), matWhiteSoft);
  tailMesh.position.set(0, 0.78, -0.82);
  tailMesh.rotation.x = 0.55;
  tailMesh.castShadow = true;
  pelican.add(tailMesh);

  // NECK: tube S-curve
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.95, 0.32),
    new THREE.Vector3(0.02, 1.18, 0.48),
    new THREE.Vector3(-0.02, 1.32, 0.58),
    new THREE.Vector3(0, 1.48, 0.62)
  ]);
  neckMesh = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 16, 0.20, 12, false), matWhite);
  neckMesh.castShadow = true;
  pelican.add(neckMesh);

  // HEAD group at top of neck
  headGroup = new THREE.Group();
  headGroup.position.set(0, 1.58, 0.68);
  pelican.add(headGroup);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.30, 28, 20), matWhite);
  head.scale.set(0.92, 0.88, 1.18);
  head.castShadow = true;
  headGroup.add(head);

  // crest feathers (3 little spikes at back)
  for (let i = 0; i < 3; i++) {
    const crest = new THREE.Mesh(new THREE.ConeGeometry(0.07 - i*0.012, 0.28 + i*0.06, 8), matWhite);
    crest.position.set((i-1)*0.07, 0.22 + i*0.02, -0.18 - i*0.04);
    crest.rotation.x = -0.9 + (i-1)*0.18;
    crest.rotation.z = (i-1)*0.35;
    crest.castShadow = true;
    headGroup.add(crest);
  }

  // EYES
  const eyeGeo = new THREE.SphereGeometry(0.045, 12, 12);
  eyeL = new THREE.Mesh(eyeGeo, matEye); eyeL.position.set(0.24, 0.06, 0.10); headGroup.add(eyeL);
  eyeR = new THREE.Mesh(eyeGeo, matEye); eyeR.position.set(-0.24, 0.06, 0.10); headGroup.add(eyeR);
  const hlGeo = new THREE.SphereGeometry(0.016, 8, 8);
  const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const hlL = new THREE.Mesh(hlGeo, hlMat); hlL.position.set(0.255, 0.075, 0.135); headGroup.add(hlL);
  const hlR = new THREE.Mesh(hlGeo, hlMat); hlR.position.set(-0.255, 0.075, 0.135); headGroup.add(hlR);

  // BEAK: upper mandible
  // Use a tapered shape via Lathe? Simpler: cone stretched
  const beakGroup = new THREE.Group();
  beakGroup.position.set(0, 0.02, 0.28);
  headGroup.add(beakGroup);

  const upperGeo = new THREE.ConeGeometry(0.13, 1.15, 12);
  // Cone points +Y by default; rotate to point +Z (forward)
  const upper = new THREE.Mesh(upperGeo, matBeak);
  upper.rotation.x = Math.PI/2; // now points +Z? Cone tip +Y -> after rotX 90, tip points +Z? actually +Y -> +Z? Let's check: rotX 90 maps Y->Z, Z->-Y
  upper.scale.set(1.15, 1, 0.75); // flatten slightly? need after rotation so scale axes accordingly
  // Cone geometry tip is +Y, base -Y. After rotX, tip goes to +Z? good.
  upper.position.set(0, -0.02, 0.52);
  upper.castShadow = true;
  beakGroup.add(upper);

  // hook tip
  const hook = new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 10), matBeakTip);
  hook.scale.set(1.1, 0.6, 1.4);
  hook.position.set(0, -0.10, 1.05);
  hook.rotation.x = 0.35;
  hook.castShadow = true;
  beakGroup.add(hook);

  // pouch (hanging cloth under beak)
  pouchMesh = new THREE.Mesh(new THREE.SphereGeometry(0.28, 20, 16), matPouch);
  pouchMesh.scale.set(0.85, 0.65, 1.55);
  pouchMesh.position.set(0, -0.20, 0.55);
  pouchMesh.castShadow = true;
  beakGroup.add(pouchMesh);
  // pouch crease lines (canvas texture)
  pouchMesh.material = matPouch.clone();
  pouchMesh.material.roughness = 0.75;

  // nostril ridge
  const ridge = new THREE.Mesh(new THREE.CapsuleGeometry(0.02, 0.7, 6, 8), matBeakTip);
  ridge.rotation.x = Math.PI/2;
  ridge.position.set(0, 0.07, 0.45);
  beakGroup.add(ridge);

  // WINGS
  function makeWingGeo(side = 1) {
    const s = new THREE.Shape();
    // wing outline lying flat, root at 0,0 tip at +X (side * length)
    s.moveTo(0, 0);
    s.bezierCurveTo(0.5*side, 0.28, 1.05*side, 0.34, 1.55*side, 0.18);
    s.bezierCurveTo(1.75*side, 0.08, 1.78*side, -0.02, 1.92*side, -0.02);
    s.bezierCurveTo(1.95*side, -0.10, 1.85*side, -0.22, 1.60*side, -0.26);
    s.bezierCurveTo(1.15*side, -0.32, 0.55*side, -0.28, 0.18*side, -0.18);
    s.bezierCurveTo(0, -0.16, -0.05*side, -0.08, 0, 0);
    return extrudeShape(s, 0.07, 0.025);
  }

  // Right wing (pelican's left? but just two)
  wingLgeo = makeWingGeo(1);
  wingRgeo = makeWingGeo(-1);
  wingL = new THREE.Mesh(wingLgeo, matWhite);
  wingR = new THREE.Mesh(wingRgeo, matWhite);
  wingL.position.set(0.38, 0.88, -0.18);
  wingR.position.set(-0.38, 0.88, -0.18);
  wingL.rotation.y = -0.15; // slight sweep back
  wingR.rotation.y = 0.15;
  wingL.castShadow = wingR.castShadow = true;

  // black primary tips: add small black mesh at wingtip
  const tipShape = new THREE.Shape();
  tipShape.moveTo(0,0);
  tipShape.bezierCurveTo(0.22, -0.02, 0.32, -0.10, 0.38, -0.14);
  tipShape.bezierCurveTo(0.42, -0.06, 0.38, 0.04, 0.26, 0.06);
  tipShape.bezierCurveTo(0.10, 0.04, 0, 0.02, 0,0);
  const tipGeo = extrudeShape(tipShape, 0.075, 0.02);
  const tipL = new THREE.Mesh(tipGeo, matBlackTip);
  tipL.position.set(1.52, 0, -0.10);
  wingL.add(tipL);
  const tipR = new THREE.Mesh(tipGeo.clone(), matBlackTip);
  tipR.scale.x = -1;
  tipR.position.set(-1.52, 0, -0.10);
  wingR.add(tipR);

  pelican.add(wingL, wingR);

  // LEGS & FEET
  function makeLeg(x) {
    const leg = new THREE.Group();
    leg.position.set(x, 0.42, 0.05);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.045, 0.42, 10), matLeg);
    shin.position.y = -0.12; shin.castShadow = true; leg.add(shin);
    // foot: webbed shape
    const footShape = new THREE.Shape();
    footShape.moveTo(0, 0);
    footShape.bezierCurveTo(0.10, -0.02, 0.20, -0.28, 0.18, -0.38);
    footShape.bezierCurveTo(0.12, -0.46, 0.0, -0.46, -0.02, -0.38);
    footShape.bezierCurveTo(0.0, -0.42, -0.06, -0.48, -0.10, -0.38);
    footShape.bezierCurveTo(-0.16, -0.28, -0.14, -0.06, 0, 0);
    const footGeo = extrudeShape(footShape, 0.03, 0.012);
    const foot = new THREE.Mesh(footGeo, matLeg);
    foot.rotation.x = -Math.PI/2; // lay flat
    foot.position.y = -0.36; foot.castShadow = true;
    leg.add(foot);
    return leg;
  }
  pelican.add(makeLeg(0.22), makeLeg(-0.22));
}

// ----- ocean base -----
const oceanGeo = new THREE.PlaneGeometry(90, 46, 68, 36);
oceanGeo.rotateX(-Math.PI / 2);
const oceanPos = oceanGeo.attributes.position;
const oceanBase = new Float32Array(oceanPos.count * 3);
oceanPos.array.forEach((v, i) => oceanBase[i] = v);

const oceanMat = new THREE.MeshStandardMaterial({
  color: 0x1290c8,
  roughness: 0.28,
  metalness: 0.05,
  transparent: true,
  opacity: 0.98,
  emissive: 0x0a4a66,
  emissiveIntensity: 0.18
});
// canvas texture for foam speckles
{
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = "#0b7ea6"; g.fillRect(0,0,256,256);
  g.globalAlpha = 0.18; g.fillStyle = "#ffffff";
  for (let i = 0; i < 420; i++) {
    const r = 1 + Math.random()*1.8;
    g.beginPath(); g.arc(Math.random()*256, Math.random()*256, r, 0, Math.PI*2); g.fill();
  }
  g.globalAlpha = 0.10;
  for (let i = 0; i < 90; i++) {
    const w = 2 + Math.random()*3;
    g.fillRect(Math.random()*256, Math.random()*256, w*3, 1);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(6,3);
  t.colorSpace = THREE.SRGBColorSpace;
  oceanMat.map = t;
  oceanMat.needsUpdate = true;
}
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.position.set(0, -0.45, 0);
ocean.receiveShadow = true;
scene.add(ocean);

// ----- big surf wave (curling wall) -----
const waveGroup = new THREE.Group();
scene.add(waveGroup);

function buildWaveWall() {
  // Wall lying in ZY plane: length along Z (30), height along Y (6)
  // Start as plane (XY), then rotate Y 90deg so length axis is Z.
  const geo = new THREE.PlaneGeometry(30, 6, 64, 10);
  geo.rotateY(Math.PI / 2);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const y0 = pos.getY(i); // -3 .. 3
    const z = pos.getZ(i);  // -15 .. 15
    const v = (y0 + 3) / 6; // 0 bottom .. 1 top
    const t = (z + 15) / 30;
    const taper = Math.sin(t * Math.PI); // 0 at ends, 1 middle
    // curl forward (+X) increases with height — a bit more dramatic for the barrel
    const curl = v * v * 2.05 * (0.55 + taper * 0.55) + v * 0.28;
    // shape: lean forward at top, slight pocket
    const x = curl + Math.sin(z * 0.30) * 0.12 * v + Math.sin(z*0.12)*0.07;
    // height: middle higher
    const y = y0 * 0.90 + 0.32 + (taper - 0.2) * 0.60 + Math.sin(z*0.22)*0.08;
    pos.setXYZ(i, x, y, z);
  }
  geo.computeVertexNormals();
  return geo;
}

function waveHeightAt(z) {
  const t = THREE.MathUtils.clamp((z + 15) / 30, 0, 1);
  const taper = Math.sin(t * Math.PI);
  // top edge y (v=1)
  return 3*0.90 + 0.32 + (taper - 0.2) * 0.60;
}
function waveCrestXAt(z) {
  const t = THREE.MathUtils.clamp((z + 15) / 30, 0, 1);
  const taper = Math.sin(t * Math.PI);
  // top edge x (v=1)
  return 1 * 2.05 * (0.55 + taper*0.55) + 1*0.28 + Math.sin(z*0.30)*0.12 + Math.sin(z*0.12)*0.07;
}

const waveWallGeo = buildWaveWall();
const waveMat = new THREE.MeshPhysicalMaterial({
  color: 0x0f9cc4,
  roughness: 0.22,
  metalness: 0.02,
  transmission: 0.22,
  thickness: 1.6,
  transparent: true,
  opacity: 0.96,
  clearcoat: 0.55,
  clearcoatRoughness: 0.28,
  side: THREE.DoubleSide,
  emissive: 0x052e3d,
  emissiveIntensity: 0.18
});
const waveWall = new THREE.Mesh(waveWallGeo, waveMat);
waveWall.position.set(-2.8, 1.1, 0);
waveWall.castShadow = true; waveWall.receiveShadow = true;
waveGroup.add(waveWall);

// inner shadow face (darker, slightly inset)
const waveInnerGeo = buildWaveWall();
const waveInner = new THREE.Mesh(waveInnerGeo, new THREE.MeshStandardMaterial({
  color: 0x065a78, roughness: 0.5, metalness: 0, transparent: true, opacity: 0.45, side: THREE.BackSide
}));
waveInner.position.copy(waveWall.position);
waveInner.position.x += 0.06;
waveGroup.add(waveInner);

// foam crest: tube along top edge (matches wall top)
{
  const crestPts = [];
  for (let t = -13.5; t <= 13.5; t += 0.75) {
    const yTop = waveHeightAt(t) + 1.1; // wall top + offset
    const xTop = waveCrestXAt(t) - 2.8; // wall x offset
    const y = yTop + Math.sin(t*0.45)*0.16;
    const x = xTop + 0.35 + Math.sin(t*0.28)*0.12;
    crestPts.push(new THREE.Vector3(x, y, t));
  }
  const curve = new THREE.CatmullRomCurve3(crestPts);
  const tubeGeo = new THREE.TubeGeometry(curve, 56, 0.48, 10, false);
  const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.32, metalness: 0, transparent: true, opacity: 0.96 });
  const foam = new THREE.Mesh(tubeGeo, foamMat);
  foam.castShadow = true; foam.receiveShadow = true;
  waveGroup.add(foam);

  // secondary lip just under crest
  const lipPts = crestPts.map(p => new THREE.Vector3(p.x - 0.45, p.y - 0.55, p.z));
  const lipCurve = new THREE.CatmullRomCurve3(lipPts);
  const lipTube = new THREE.TubeGeometry(lipCurve, 56, 0.30, 8, false);
  const lip = new THREE.Mesh(lipTube, new THREE.MeshStandardMaterial({ color: 0xeaf7ff, roughness: 0.45, transparent: true, opacity: 0.9, side: THREE.DoubleSide }));
  waveGroup.add(lip);
}

// ----- spray particles -----
let clockTime = 0;
const SPRAY_MAX = 420;
const sprayGeo = new THREE.BufferGeometry();
const sprayPos = new Float32Array(SPRAY_MAX * 3);
const sprayVel = new Float32Array(SPRAY_MAX * 3);
const sprayLife = new Float32Array(SPRAY_MAX);
const sprayMaxLife = new Float32Array(SPRAY_MAX);
sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
{
  const c = document.createElement("canvas"); c.width = c.height = 32;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(16,16,0,16,16,16);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.5, "rgba(255,255,255,0.7)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad; g.fillRect(0,0,32,32);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  var sprayMat = new THREE.PointsMaterial({ size: 0.32, map: tex, transparent: true, opacity: 0.95, depthWrite: false, sizeAttenuation: true, blending: THREE.AdditiveBlending });
}
const spray = new THREE.Points(sprayGeo, sprayMat);
spray.frustumCulled = false;
scene.add(spray);

function respawnSpray(i, strength = 1) {
  // spawn at board rail + wave face
  const t = clockTime || 0;
  const rideZ = rider.position.z;
  const rideX = rider.position.x;
  const rideY = rider.position.y;
  const side = Math.random() < 0.5 ? 1 : -1;
  sprayPos[i*3 + 0] = rideX + (Math.random()-0.5)*0.6 + side*0.35;
  sprayPos[i*3 + 1] = rideY + Math.random()*0.25;
  sprayPos[i*3 + 2] = rideZ + (Math.random()-0.5)*2.4;
  // velocity: outward and up
  const back = -1.2 - Math.random()*1.6 * strength;
  const up = 1.2 + Math.random()*2.2 * strength;
  const out = side*(0.4 + Math.random()*0.7);
  sprayVel[i*3 + 0] = out * 0.8 + (Math.random()-0.5)*0.4;
  sprayVel[i*3 + 1] = up;
  sprayVel[i*3 + 2] = back + Math.sin(t*3)*0.3;
  sprayLife[i] = 0;
  sprayMaxLife[i] = 0.9 + Math.random()*0.85;
}
for (let i = 0; i < SPRAY_MAX; i++) { sprayLife[i] = Math.random()*0.8; sprayMaxLife[i] = 1; respawnSpray(i); }

// ground sand strip (far shore) for depth — pushed far so no hard edge in view
const sand = new THREE.Mesh(
  new THREE.PlaneGeometry(120, 14),
  new THREE.MeshStandardMaterial({ color: 0xe8d4a0, roughness: 0.95 })
);
sand.rotation.x = -Math.PI/2;
sand.position.set(0, -0.68, -28);
scene.add(sand);

// distant sand haze — soft gradient toward sky so horizon blends
const hazeMat = new THREE.ShaderMaterial({
  transparent: true,
  side: THREE.DoubleSide,
  uniforms: { top: { value: new THREE.Color(0x9fd4e8) }, bottom: { value: new THREE.Color(0xe8d4a0) } },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform vec3 top; uniform vec3 bottom; varying vec2 vUv; void main(){ vec3 c=mix(bottom, top, vUv.y); gl_FragColor=vec4(c, (1.0-vUv.y)*0.35); }`
});
const haze = new THREE.Mesh(new THREE.PlaneGeometry(120, 6), hazeMat);
haze.position.set(0, 0.4, -26);
scene.add(haze);

// ----- clouds -----
const clouds = [];
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, metalness: 0, emissive: 0x0a1a22, transparent: true, opacity: 0.98 });
  const n = 4 + Math.floor(Math.random()*3);
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.7 + Math.random()*0.5, 12, 10), mat);
    m.position.set((i - n/2)*0.85 + (Math.random()-0.5)*0.3, (Math.random()-0.5)*0.35, (Math.random()-0.5)*0.4);
    m.scale.y = 0.58; m.castShadow = false;
    g.add(m);
  }
  g.position.set(x, y, z); g.scale.setScalar(s);
  scene.add(g);
  clouds.push({ g, speed: 0.18 + Math.random()*0.22 });
}
makeCloud(-14, 13, -18, 2.0);
makeCloud(4, 14.5, -20, 2.4);
makeCloud(16, 12.5, -12, 1.5);
makeCloud(-6, 15, 12, 1.7);
makeCloud(18, 11, 8, 1.3);
makeCloud(-18, 11, 6, 1.4);

// ----- distant gulls -----
const gulls = [];
function makeGull() {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0xe8eef2, side: THREE.DoubleSide });
  const w1 = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.18), mat);
  const w2 = w1.clone();
  w1.position.x = -0.35; w2.position.x = 0.35;
  w1.rotation.z = 0.25; w2.rotation.z = -0.25;
  g.add(w1, w2);
  g.userData = { w1, w2 };
  return g;
}
for (let i = 0; i < 4; i++) {
  const g = makeGull();
  g.position.set(-20 + Math.random()*40, 9 + Math.random()*3, -14 + Math.random()*8);
  scene.add(g);
  gulls.push({ g, r: 12 + Math.random()*6, h: 9 + Math.random()*2.5, speed: 0.22 + Math.random()*0.14, phase: Math.random()*Math.PI*2 });
}

// ----- bottom foam line (subtle surf wash near camera) -----
const baseFoam = new THREE.Mesh(
  new THREE.TorusGeometry(18, 0.20, 6, 64, Math.PI*1.35),
  new THREE.MeshStandardMaterial({ color: 0xf4fcff, roughness: 0.55, transparent: true, opacity: 0.55 })
);
baseFoam.rotation.x = Math.PI/2;
baseFoam.rotation.z = 0.4;
baseFoam.position.set(0, -0.32, 3.5);
scene.add(baseFoam);

// ----- animation -----
const clock = new THREE.Clock();
let camAngle = 0.45;

function updateOcean(t) {
  const pos = oceanGeo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = oceanBase[i*3], z = oceanBase[i*3+2];
    // gentle swell + chop
    let y = Math.sin(x*0.28 + t*1.1) * 0.18 + Math.sin(z*0.42 - t*0.9) * 0.12 + Math.sin((x+z)*0.18 + t*0.6)*0.08;
    // larger swell near wave front (x ~0)
    const waveProx = Math.exp(-Math.pow((x+2.5)/7, 2));
    y += waveProx * (0.55 + 0.35*Math.sin(t*1.3 + z*0.24));
    // shore fade
    const shore = THREE.MathUtils.smoothstep(z, -18, -8);
    y *= (0.6 + shore*0.4);
    // chop detail
    y += Math.sin(x*1.4 + t*2.2)*0.03 + Math.sin(z*1.8 - t*1.8)*0.02;
    pos.setY(i, y);
  }
  pos.needsUpdate = true;
  oceanGeo.computeVertexNormals();
}

function updateSpray(dt) {
  for (let i = 0; i < SPRAY_MAX; i++) {
    sprayLife[i] += dt;
    if (sprayLife[i] >= sprayMaxLife[i]) respawnSpray(i);
    const idx = i*3;
    sprayPos[idx+1] -= 5.8 * dt; // gravity via vel
    sprayVel[idx+1] -= 7.5 * dt;
    sprayPos[idx+0] += sprayVel[idx+0]*dt;
    sprayPos[idx+1] += sprayVel[idx+1]*dt;
    sprayPos[idx+2] += sprayVel[idx+2]*dt;
    sprayVel[idx+2] *= 0.99;
    if (sprayPos[idx+1] < -0.6) respawnSpray(i);
  }
  sprayGeo.attributes.position.needsUpdate = true;
  // opacity pulse
  sprayMat.opacity = 0.82 + Math.sin(clockTime*2.1)*0.08;
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
  clockTime = t;

  updateOcean(t);
  updateSpray(dt);

  // --- rider animation on wave face ---
  // ride along Z back/forth, up/down the face
  const ridePeriod = prefersReduced ? 14 : 9.5;
  const phase = (t / ridePeriod) * Math.PI * 2;
  const rideZ = Math.sin(phase) * 7.6;
  // y: higher in middle of run, lower near ends (trim) — follows wave height taper
  const trim = Math.cos(phase) * 0.5 + 0.5; // 0..1
  const tNorm = (rideZ + 15) / 30;
  const taperZ = Math.sin(Math.max(0, Math.min(1, tNorm)) * Math.PI); // 0..1
  const rideY = 0.95 + trim * 1.25 + taperZ * 0.35 + Math.sin(t*1.6)*0.12;
  // x: stay just off the wall face (wall face at mid-height ~ -2.2 .. -1.6)
  // trim pushes rider a bit higher / closer to the pocket
  const rideX = -0.75 + Math.cos(phase)*0.28 + trim * 0.12 + Math.sin(rideZ*0.28)*0.10;

  rider.position.set(rideX, rideY, rideZ);
  rider.scale.setScalar(1.38);
  // board rock: tilt with trim, plus wobble
  rider.rotation.z = -0.22 - trim*0.28 + Math.sin(t*1.7)*0.045;
  rider.rotation.x = Math.cos(phase)*0.14 + Math.sin(t*2.2)*0.03;
  rider.rotation.y = -0.55 + Math.sin(phase)*0.18; // heading along wave

  // pelican body language
  pelican.rotation.y = Math.sin(t*0.9)*0.08;
  pelican.rotation.x = 0.06 + Math.sin(t*1.3)*0.04;
  // wing balance: flare when carving — surfing stance, wings up
  const flare = 0.42 + Math.abs(Math.sin(phase))*0.28 + Math.sin(t*2.0)*0.14;
  wingL.rotation.z = flare; wingR.rotation.z = -flare;
  wingL.rotation.x = Math.sin(t*1.9)*0.10 + Math.cos(phase)*0.08;
  wingR.rotation.x = Math.sin(t*1.9+0.6)*0.10 - Math.cos(phase)*0.08;
  // neck/head bob
  neckMesh.rotation.x = Math.sin(t*1.5)*0.05;
  headGroup.rotation.y = Math.sin(t*0.7)*0.18 + Math.cos(phase)*0.12;
  headGroup.rotation.x = -0.12 + Math.sin(t*1.2)*0.06;
  pouchMesh.scale.y = 0.65 + Math.sin(t*1.4)*0.05; // pouch bounce
  bodyMesh.position.y = 0.68 + Math.sin(t*1.8)*0.02;

  // wave wall breathing (subtle x pulse)
  waveGroup.position.x = Math.sin(t*0.5)*0.22;
  waveWall.material.roughness = 0.22 + Math.sin(t*1.2)*0.03;

  // clouds drift
  for (const c of clouds) {
    c.g.position.x += c.speed * dt * (prefersReduced ? 0.4 : 1);
    if (c.g.position.x > 28) c.g.position.x = -28;
  }
  // gulls circle
  for (const gu of gulls) {
    const a = t*gu.speed + gu.phase;
    gu.g.position.x = Math.cos(a)*gu.r;
    gu.g.position.z = Math.sin(a)*gu.r*0.55 - 2;
    gu.g.position.y = gu.h + Math.sin(t*0.8 + gu.phase)*0.5;
    gu.g.rotation.y = -a - Math.PI/2;
    const flap = Math.sin(t*5.5 + gu.phase*5)*0.5;
    gu.g.userData.w1.rotation.z = 0.25 + flap*0.35;
    gu.g.userData.w2.rotation.z = -0.25 - flap*0.35;
  }

  // foam base rotation
  baseFoam.rotation.z = 0.4 + Math.sin(t*0.3)*0.06;
  baseFoam.position.y = -0.30 + Math.sin(t*0.9)*0.08;

  // --- camera: gentle front-arc sway, non-interactive (stays on ocean side) ---
  // swing left-right in front of the wave, never go behind the wall
  const sway = prefersReduced ? Math.sin(t*0.06)*0.22 : Math.sin(t*0.11)*0.48;
  const sway2 = prefersReduced ? Math.sin(t*0.05+1.2)*0.10 : Math.sin(t*0.09+1.2)*0.22;
  const camR = prefersReduced ? 10.8 : 10.2 + Math.sin(t*0.15)*0.6;
  const camH = prefersReduced ? 3.7 : 3.5 + Math.sin(t*0.28)*0.38 + Math.sin(t*0.7)*0.10;
  // focus rider
  V.copy(rider.position).add(new THREE.Vector3(0, 0.95, 0));
  const lookTarget = V.clone();
  lookTarget.z += Math.cos(phase)*1.0;
  lookTarget.x += 0.25;
  lookTarget.y -= 0.15;

  // front hemisphere: +X is ocean side, so keep x positive large
  camera.position.x = camR * Math.cos(sway2*0.6) + 2.2 + sway*1.4;
  camera.position.y = camH;
  camera.position.z = Math.sin(sway*1.1) * camR * 0.62 + rideZ*0.28;
  // ensure we never go far behind rider along Z
  camera.position.x = Math.max(camera.position.x, 7.5);
  camera.lookAt(lookTarget);

  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// error overlay (instead of black page)
window.addEventListener("error", (e) => {
  let el = document.getElementById("err");
  if (!el) {
    el = document.createElement("div"); el.id = "err";
    el.style.cssText = "position:fixed;left:12px;bottom:12px;max-width:420px;padding:10px 12px;background:#7a1f1f;color:#fff;border-radius:10px;font:13px/1.4 system-ui;z-index:20";
    document.body.appendChild(el);
  }
  el.textContent = "Error: " + (e.message || "unknown");
});
// DEBUG: wrap computeBoundingSphere to log NaN stack
const origCompute = THREE.BufferGeometry.prototype.computeBoundingSphere;
THREE.BufferGeometry.prototype.computeBoundingSphere = function(){
  const r = origCompute.call(this);
  if (this.boundingSphere && isNaN(this.boundingSphere.radius)) {
    console.error('DEBUG NaN geometry', this.type, this.parameters || 'no-params', 'count', this.attributes?.position?.count);
    // check positions for NaN
    const pos = this.attributes?.position;
    if(pos) {
      for(let i=0;i<pos.count;i++){
        const x=pos.getX(i), y=pos.getY(i), z=pos.getZ(i);
        if(isNaN(x)||isNaN(y)||isNaN(z)){ console.error(' NaN at',i,x,y,z); break; }
      }
    }
    console.trace('NaN stack');
  }
  return r;
};
