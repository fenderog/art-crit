import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// An entirely procedural little seaside escape. No models, textures, or network requests.
const container = document.querySelector('#scene');
const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;
container.appendChild(renderer.domElement);

const camera = new THREE.OrthographicCamera(-8, 8, 5, -5, 0.1, 100);
camera.position.set(8.5, 7.2, 16.5);
camera.lookAt(0, 1.9, 0);
const pmrem = new THREE.PMREMGenerator(renderer);
const studio = new RoomEnvironment();
scene.environment = pmrem.fromScene(studio, 0.04).texture;
scene.environmentIntensity = 0.32;
studio.dispose();
pmrem.dispose();

scene.add(new THREE.HemisphereLight(0xfff8de, 0x509589, 1.65));
const sunlight = new THREE.DirectionalLight(0xfff0cf, 3.0);
sunlight.position.set(-7, 12, 7);
sunlight.castShadow = true;
sunlight.shadow.mapSize.set(2048, 2048);
sunlight.shadow.camera.left = -11;
sunlight.shadow.camera.right = 11;
sunlight.shadow.camera.top = 10;
sunlight.shadow.camera.bottom = -8;
sunlight.shadow.normalBias = 0.035;
sunlight.shadow.bias = -0.0001;
sunlight.shadow.radius = 4;
scene.add(sunlight);
const rimLight = new THREE.DirectionalLight(0xd9fff0, 1.8);
rimLight.position.set(5, 7, -8);
scene.add(rimLight);

function mat(color, roughness = 0.65, extra = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness, ...extra });
}
const cream = mat('#fff8e4');
const featherLight = mat('#f6efda');
const featherShade = mat('#e2e3cd');
const graphite = mat('#304e4b');
const featherMid = mat('#65796d');
const gold = mat('#f9b641', 0.42);
const pouchMat = mat('#eaaa42', 0.65);
const orange = mat('#df8a35', 0.52);
const coral = mat('#dd6f4d', 0.4);
const foamMat = mat('#f3f7e3', 0.65);
const paleFoam = mat('#caedda', 0.55);
const sphereGeo = new THREE.SphereGeometry(1, 32, 24);
const dropGeo = new THREE.SphereGeometry(1, 12, 10);

function ellipsoid(parent, material, pos, scale, rotation = 0) {
  const mesh = new THREE.Mesh(sphereGeo, material);
  mesh.position.set(...pos);
  mesh.scale.set(...scale);
  mesh.rotation.z = rotation;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function curveMesh(parent, points, radius, material, segments = 40) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 8, false), material);
  parent.add(mesh);
  return mesh;
}
function feather(parent, a, b, width, material, thickness = 0.07) {
  const start = new THREE.Vector3(...a);
  const end = new THREE.Vector3(...b);
  const length = start.distanceTo(end);
  const m = new THREE.Mesh(sphereGeo, material);
  m.position.copy(start.add(end).multiplyScalar(0.5));
  m.scale.set(width, thickness, length * 0.65);
  const direction = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)).normalize();
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), direction);
  m.castShadow = true;
  m.receiveShadow = true;
  parent.add(m);
  return m;
}
function seededRandom(seed) {
  return () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}
const rand = seededRandom(181);

// Soft, transparent contact shadows keep the illustration floating on the paper.
const shadowCanvas = document.createElement('canvas');
shadowCanvas.width = shadowCanvas.height = 128;
const shadowCtx = shadowCanvas.getContext('2d');
const shadowGradient = shadowCtx.createRadialGradient(64, 64, 3, 64, 64, 64);
shadowGradient.addColorStop(0, 'rgba(35,76,65,.23)');
shadowGradient.addColorStop(0.45, 'rgba(35,76,65,.11)');
shadowGradient.addColorStop(1, 'rgba(35,76,65,0)');
shadowCtx.fillStyle = shadowGradient;
shadowCtx.fillRect(0, 0, 128, 128);
const shadowTexture = new THREE.CanvasTexture(shadowCanvas);
const groundShadow = new THREE.Mesh(new THREE.PlaneGeometry(21, 12), new THREE.MeshBasicMaterial({ map: shadowTexture, transparent: true, depthWrite: false }));
groundShadow.rotation.x = -Math.PI / 2;
groundShadow.position.set(0.4, -0.52, 0.4);
scene.add(groundShadow);

// A gently undulating, rounded patch of ocean, like a small sculpted world.
const seaGroup = new THREE.Group();
seaGroup.position.x = 0.1;
scene.add(seaGroup);
const rings = 34;
const sectors = 144;
const oceanPositions = [];
const oceanColors = [];
const oceanIndices = [];
const waterCenter = new THREE.Color('#29b1a9');
const waterEdge = new THREE.Color('#91d2b9');
const waterDeep = new THREE.Color('#159a99');
function seaHeight(x, z, t = 0) {
  return -0.12 + Math.sin(x * 1.1 + z * 0.8 + t * 0.9) * 0.045 + Math.cos(z * 1.7 - x * 0.4 + t * 0.7) * 0.035;
}
for (let r = 0; r <= rings; r++) {
  const u = r / rings;
  for (let j = 0; j <= sectors; j++) {
    const a = (j / sectors) * Math.PI * 2;
    const irregular = 1 + Math.sin(a * 3 + 0.5) * 0.035 + Math.sin(a * 7) * 0.018;
    const x = Math.cos(a) * 8.15 * u * irregular;
    const z = Math.sin(a) * 4.8 * u * irregular;
    const y = seaHeight(x, z) - Math.pow(u, 18) * 0.2;
    oceanPositions.push(x, y, z);
    const color = waterCenter.clone().lerp(waterEdge, Math.pow(u, 4) * 0.95);
    color.lerp(waterDeep, (Math.sin(x * 0.7 + z * 1.1) + 1) * 0.1 * (1 - u));
    oceanColors.push(color.r, color.g, color.b);
    if (r < rings && j < sectors) {
      const i = r * (sectors + 1) + j;
      oceanIndices.push(i, i + sectors + 1, i + 1, i + 1, i + sectors + 1, i + sectors + 2);
    }
  }
}
const oceanGeo = new THREE.BufferGeometry();
oceanGeo.setAttribute('position', new THREE.Float32BufferAttribute(oceanPositions, 3));
oceanGeo.setAttribute('color', new THREE.Float32BufferAttribute(oceanColors, 3));
oceanGeo.setIndex(oceanIndices);
oceanGeo.computeVertexNormals();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.29, metalness: 0.02, clearcoat: 0.55, clearcoatRoughness: 0.3, side: THREE.DoubleSide }));
ocean.receiveShadow = true;
seaGroup.add(ocean);

// The wave is a thick, curling sheet, not a stock model. Its cross-section rolls over itself.
const waveGroup = new THREE.Group();
waveGroup.position.set(0.6, -0.06, -1.3);
seaGroup.add(waveGroup);
function wavePoint(u, v, offset = 0) {
  const x = -6.1 + u * 11.6 - 0.75 * Math.pow(u, 6) * v;
  const envelope = Math.pow(Math.sin(Math.PI * u * 0.66), 0.65);
  const radius = 0.12 + 2.28 * envelope;
  const maxAngle = 2.71 + 0.3 * u;
  const angle = -Math.PI / 2 + (maxAngle + Math.PI / 2) * v;
  const r = radius + offset;
  const y = radius + Math.sin(angle) * r - 0.06;
  const z = -Math.cos(angle) * r + Math.sin(u * Math.PI) * 0.25;
  return new THREE.Vector3(x, y, z);
}
const wx = 128;
const wv = 64;
const wavePos = [];
const waveCol = [];
const waveInd = [];
const lowColor = new THREE.Color('#087f82');
const midColor = new THREE.Color('#23b5b1');
const topColor = new THREE.Color('#67cbb9');
for (let side = 0; side < 2; side++) {
  for (let i = 0; i <= wx; i++) {
    for (let j = 0; j <= wv; j++) {
      const u = i / wx;
      const v = j / wv;
      const p = wavePoint(u, v, side === 0 ? -0.015 : 0.14);
      wavePos.push(p.x, p.y, p.z);
      const c = lowColor.clone().lerp(midColor, Math.min(1, v * 1.6));
      c.lerp(topColor, Math.pow(v, 3) * 0.9);
      if (side === 0) c.multiplyScalar(0.93);
      const streak = Math.sin(u * 119 + v * 8) * Math.sin(u * 27 - v * 3) * 0.035;
      c.multiplyScalar(1 + streak);
      waveCol.push(c.r, c.g, c.b);
      if (i < wx && j < wv) {
        const k = side * (wx + 1) * (wv + 1) + i * (wv + 1) + j;
        if (side === 0) waveInd.push(k, k + 1, k + wv + 1, k + 1, k + wv + 2, k + wv + 1);
        else waveInd.push(k, k + wv + 1, k + 1, k + 1, k + wv + 1, k + wv + 2);
      }
    }
  }
}
const layerLength = (wx + 1) * (wv + 1);
for (let i = 0; i < wx; i++) {
  const a = i * (wv + 1) + wv;
  const b = (i + 1) * (wv + 1) + wv;
  waveInd.push(a, b, a + layerLength, b, b + layerLength, a + layerLength);
}
for(let j=0;j<wv;j++) {
  const k=wx*(wv+1)+j;
  waveInd.push(k,k+layerLength,k+1,k+1,k+layerLength,k+layerLength+1);
}
const waveGeo = new THREE.BufferGeometry();
waveGeo.setAttribute('position', new THREE.Float32BufferAttribute(wavePos, 3));
waveGeo.setAttribute('color', new THREE.Float32BufferAttribute(waveCol, 3));
waveGeo.setIndex(waveInd);
waveGeo.computeVertexNormals();
const wave = new THREE.Mesh(waveGeo, new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.3, metalness: 0.025, clearcoat: 0.75, clearcoatRoughness: 0.24, side: THREE.DoubleSide }));
wave.castShadow = true;
wave.receiveShadow = true;
waveGroup.add(wave);

// Long engraved threads of water follow the inside of the barrel.
const waterLineMat = mat('#99dfcb', 0.42, { transparent: true, opacity: 0.38 });
const darkLineMat = mat('#187f84', 0.45, { transparent: true, opacity: 0.3 });
for (let i = 0; i < 31; i++) {
  const u = 0.055 + i / 34;
  const start = 0.11 + rand() * 0.22;
  const end = 0.79 + rand() * 0.18;
  const points = [];
  for (let j = 0; j <= 35; j++) {
    const v = start + (end - start) * j / 35;
    const p = wavePoint(u + Math.sin(v * 5 + i) * 0.005, v, -0.033);
    points.push(p.toArray());
  }
  curveMesh(waveGroup, points, 0.009 + rand() * 0.011, i % 4 === 0 ? darkLineMat : waterLineMat, 35);
}
for (let j = 0; j < 5; j++) {
  const points = [];
  for (let i = 0; i <= 70; i++) {
    const u = 0.08 + 0.85 * i / 70;
    const p = wavePoint(u, 0.8 + j * 0.032 + Math.sin(u * 18 + j) * 0.009, 0.158);
    points.push(p.toArray());
  }
  curveMesh(waveGroup, points, j === 4 ? 0.022 : 0.014, j === 4 ? paleFoam : waterLineMat, 80);
}

const crestPoints = [];
for (let i = 0; i <= 110; i++) crestPoints.push(wavePoint(0.015 + i / 110 * 0.97, 1, 0.055).toArray());
curveMesh(waveGroup, crestPoints, 0.1, paleFoam, 140);
const foamBlobs = [];
for (let i = 0; i < 260; i++) {
  const u = 0.014 + i / 260 * 0.97;
  const p = wavePoint(u, 0.983 + rand() * 0.025, 0.04 + rand() * 0.13);
  p.y += rand() * 0.05;
  const size = 0.045 + rand() * 0.12;
  const blob = new THREE.Mesh(dropGeo, i % 4 === 0 ? paleFoam : foamMat);
  blob.position.copy(p);
  blob.scale.set(size * 1.5, size * 0.65, size);
  waveGroup.add(blob);
  foamBlobs.push({ mesh: blob, y: p.y, phase: rand() * Math.PI * 2 });
}

// The open end of the curl gets a delicate, irregular frothy rim.
const curlRim=[];
for(let j=0;j<=70;j++) curlRim.push(wavePoint(1,j/70,.065).toArray());
curveMesh(waveGroup,curlRim,.045,paleFoam,80);
for(let j=0;j<70;j++) {
  const p=wavePoint(.998,.58+j/70*.42,.08);
  const size=.04+rand()*.065;
  const blob=new THREE.Mesh(dropGeo,j%3?foamMat:paleFoam);
  blob.position.copy(p);blob.scale.set(size*.8,size,size*1.3);waveGroup.add(blob);
}

// Water trails and lacy foam at the edges of the little sea.
const rippleMat = mat('#d7ecce', 0.6, { transparent: true, opacity: 0.72 });
const subtleRipple = mat('#b0e1c9', 0.4, { transparent: true, opacity: 0.6 });
const rippleGroups = [];
for (let k = 0; k < 21; k++) {
  const group = new THREE.Group();
  const a = rand() * Math.PI * 2;
  const r = 0.52 + rand() * 0.39;
  const x = Math.cos(a) * 7.4 * r;
  const z = Math.sin(a) * 4.5 * r;
  const points = [];
  const length = 0.45 + rand() * 1.2;
  for (let j = 0; j <= 16; j++) {
    const f = j / 16;
    const xx = x + (f - 0.5) * length;
    const zz = z + Math.sin(f * Math.PI) * 0.14;
    points.push([xx, seaHeight(xx, zz) + 0.035, zz]);
  }
  curveMesh(group, points, 0.009 + rand() * 0.012, k % 3 === 0 ? rippleMat : subtleRipple, 20);
  seaGroup.add(group);
  rippleGroups.push({ group, phase: rand() * Math.PI * 2 });
}
for (let k = 0; k < 9; k++) {
  const points = [];
  for (let j = 0; j < 50; j++) {
    const a = 0.08 + j / 49 * 1.08;
    const r = 0.7 + k * 0.025;
    const x = Math.cos(a) * 7.7 * r;
    const z = Math.sin(a) * 4.8 * r;
    points.push([x, seaHeight(x, z) + 0.03, z]);
  }
  curveMesh(seaGroup, points, k % 3 === 0 ? 0.02 : 0.009, k % 3 === 0 ? rippleMat : subtleRipple, 50);
}

// A rounded coral longboard, complete with pinstripes, fin and a little deck emblem.
const rider = new THREE.Group();
rider.position.set(-1.25, 0.44, 2.0);
rider.rotation.y = -0.13;
scene.add(rider);
function boardShape(scale = 1) {
  const s = new THREE.Shape();
  s.moveTo(-3.2 * scale, 0);
  s.bezierCurveTo(-3.2 * scale, 0.46 * scale, -1.9 * scale, 0.64 * scale, 0.4 * scale, 0.6 * scale);
  s.bezierCurveTo(1.6 * scale, 0.58 * scale, 2.5 * scale, 0.39 * scale, 2.68 * scale, 0.22 * scale);
  s.quadraticCurveTo(2.84 * scale, 0, 2.68 * scale, -0.22 * scale);
  s.bezierCurveTo(2.5 * scale, -0.39 * scale, 1.6 * scale, -0.58 * scale, 0.4 * scale, -0.6 * scale);
  s.bezierCurveTo(-1.9 * scale, -0.64 * scale, -3.2 * scale, -0.46 * scale, -3.2 * scale, 0);
  return s;
}
function rocker(x) { return Math.pow(Math.max(0, -x - 1.35), 2) * 0.085 + Math.pow(Math.max(0, x - 1.65), 2) * 0.04; }
function boardMesh(shape, material, depth, y, bevel) {
  const geo = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelSegments: 4, steps: 1, bevelSize: bevel, bevelThickness: bevel, curveSegments: 48 });
  geo.rotateX(-Math.PI / 2);
  const positions = geo.attributes.position;
  for (let i = 0; i < positions.count; i++) positions.setY(i, positions.getY(i) + rocker(positions.getX(i)));
  geo.computeVertexNormals();
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.y = y;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  rider.add(mesh);
  return mesh;
}
boardMesh(boardShape(), coral, 0.12, 0, 0.085);
boardMesh(boardShape(0.965), mat('#ed8c62', 0.48), 0.008, 0.14, 0.018);
function boardStripe(z, width, color, start = -3.08, end = 2.66) {
  const vertices = [];
  const indices = [];
  const n = 80;
  for (let i = 0; i <= n; i++) {
    const x = start + (end - start) * i / n;
    vertices.push(x, 0.172 + rocker(x), z - width / 2, x, 0.172 + rocker(x), z + width / 2);
    if (i < n) { const k = i * 2; indices.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  rider.add(new THREE.Mesh(geo, mat(color, 0.5, { side: THREE.DoubleSide })));
}
boardStripe(0, 0.25, '#fff0cc');
boardStripe(-0.21, 0.025, '#f8e3b6', -2.94, 2.57);
boardStripe(0.21, 0.025, '#f8e3b6', -2.94, 2.57);
boardStripe(0, 0.025, '#54746a');
const finShape = new THREE.Shape();
finShape.moveTo(0, 0);
finShape.quadraticCurveTo(-0.2, -0.6, 0.6, -0.75);
finShape.quadraticCurveTo(0.35, -0.2, 0.9, 0);
finShape.closePath();
const fin = new THREE.Mesh(new THREE.ExtrudeGeometry(finShape, { depth: 0.06, bevelEnabled: true, bevelSize: 0.035, bevelThickness: 0.03, bevelSegments: 3, steps: 1 }), graphite);
fin.position.set(1.4, 0.02, -0.03);
rider.add(fin);
const logoCanvas = document.createElement('canvas');
logoCanvas.width = logoCanvas.height = 128;
const lc = logoCanvas.getContext('2d');
lc.fillStyle = '#f4e7c8';
lc.beginPath();lc.arc(64,64,58,0,Math.PI*2);lc.fill();
lc.strokeStyle='#486d61';lc.lineWidth=3;
lc.beginPath();lc.arc(64,56,23,Math.PI,0);lc.stroke();
for(let j=0;j<2;j++){lc.beginPath();for(let x=28;x<=100;x++) {const y=73+j*12+Math.sin((x-28)*Math.PI/24)*5;x===28?lc.moveTo(x,y):lc.lineTo(x,y);}lc.stroke();}
const logo = new THREE.Mesh(new THREE.PlaneGeometry(0.48, 0.48), new THREE.MeshStandardMaterial({ map: new THREE.CanvasTexture(logoCanvas), transparent: true, roughness: 0.65 }));
logo.rotation.x = -Math.PI / 2;
logo.position.set(-2.28, 0.179 + rocker(-2.28), 0.01);
rider.add(logo);

const boardShadow = new THREE.Mesh(new THREE.PlaneGeometry(7, 3), new THREE.MeshBasicMaterial({ map: shadowTexture, transparent: true, depthWrite: false, opacity: 0.7 }));
boardShadow.rotation.x = -Math.PI / 2;
boardShadow.position.set(-1.2, 0.01, 2.0);
scene.add(boardShadow);

// Two properly webbed feet, a slightly crouched stance, and an excessively large beak.
const bird = new THREE.Group();
bird.position.set(0.03, 0.18, 0);
bird.rotation.z = -0.035;
rider.add(bird);
const body = ellipsoid(bird, cream, [0.15, 1.86, 0], [0.92, 1.04, 0.69], -0.24);
ellipsoid(bird, featherLight, [0.64, 1.82, -0.03], [0.67, 0.74, 0.65], -0.45);
ellipsoid(bird, cream, [-0.31, 1.98, 0.1], [0.64, 0.83, 0.63], -0.2);
for(let i=0;i<5;i++) {
  feather(bird, [0.77,1.5,(i-2)*0.12], [1.7 + Math.sin(i)*0.12,1.45,(i-2)*0.23],0.12,i===0||i===4?featherMid:graphite,0.065);
}
ellipsoid(bird, featherLight, [0.85,1.67,0], [0.57,0.26,0.46],-.2);

function addFoot(z, xOffset) {
  ellipsoid(bird, featherLight, [0.16+xOffset,1.17,z], [0.24,0.43,0.23], -0.2);
  curveMesh(bird, [[0.15+xOffset,1.12,z],[0.31+xOffset,0.74,z],[-0.03+xOffset,0.29,z+0.03]], 0.075, orange, 22).castShadow = true;
  ellipsoid(bird, gold, [-0.035+xOffset,0.26,z+0.03], [.11,.13,.1]);
  const shape = new THREE.Shape();
  shape.moveTo(0.12,0.02);
  shape.quadraticCurveTo(-0.1,-0.13,-0.64,-0.29);
  shape.quadraticCurveTo(-0.73,-0.31,-0.65,-0.17);
  shape.lineTo(-0.52,-0.09);
  shape.quadraticCurveTo(-0.93,-0.1,-0.88,0.01);
  shape.quadraticCurveTo(-0.81,0.08,-0.52,0.1);
  shape.quadraticCurveTo(-0.79,0.3,-0.65,0.31);
  shape.quadraticCurveTo(-0.19,0.23,0.12,0.09);
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape,{depth:.045,bevelEnabled:true,bevelSegments:3,bevelSize:.035,bevelThickness:.03,curveSegments:16});
  geo.rotateX(-Math.PI/2);
  const foot = new THREE.Mesh(geo,gold);
  foot.position.set(xOffset,0.04,z);
  foot.castShadow=true;
  foot.receiveShadow=true;
  bird.add(foot);
  for(const zz of [-.19,0,.2]) {
    curveMesh(bird, [[xOffset-.06,.13,z],[xOffset-.3,.125,z+zz*.6],[xOffset-.62,.105,z+zz]], .011,orange,14);
  }
}
addFoot(-0.4,-0.35);
addFoot(0.45,0.27);

// A sculpted S-shaped neck, with a small head group for the sleepy nod.
const neckCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-.3,2.2,0),new THREE.Vector3(-.74,2.6,0),new THREE.Vector3(-.91,3.03,0),new THREE.Vector3(-.82,3.52,0),new THREE.Vector3(-1.01,3.96,0)
]);
const neckGeo = new THREE.TubeGeometry(neckCurve,50,.3,20,false);
const neckMesh = new THREE.Mesh(neckGeo,cream);
neckMesh.castShadow = true;
bird.add(neckMesh);
ellipsoid(bird,cream,[-.59,2.62,0],[.4,.57,.38],-.2);
const head = new THREE.Group();
head.position.set(-1.02,3.96,0);
bird.add(head);
ellipsoid(head,cream,[0,.08,0],[.53,.53,.43],-.08);
ellipsoid(head,featherLight,[.24,-.06,0],[.29,.4,.35],.3);
for(let i=0;i<3;i++) {
  ellipsoid(head,cream,[.22+i*.075,.49-i*.035,(i-1)*.08],[.115,.26-i*.02,.08],-.5-i*.12);
}

function loft(stations, material, parent) {
  const positions=[]; const indices=[]; const around=36; const length=72;
  const spine=new THREE.CatmullRomCurve3(stations.map(s=>new THREE.Vector3(s[0],s[1],0)));
  const profile=new THREE.CatmullRomCurve3(stations.map(s=>new THREE.Vector3(s[2],s[3],0)));
  for(let i=0;i<=length;i++) {
    const center=spine.getPoint(i/length);
    const size=profile.getPoint(i/length);
    for(let j=0;j<=around;j++) {
      const a=j/around*Math.PI*2;
      positions.push(center.x,center.y+Math.sin(a)*Math.max(.003,size.y),Math.cos(a)*Math.max(.003,size.x));
      if(i<length && j<around) {const k=i*(around+1)+j;indices.push(k,k+1,k+around+1,k+1,k+around+2,k+around+1);}
    }
  }
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geo.setIndex(indices);geo.computeVertexNormals();
  const mesh=new THREE.Mesh(geo,material);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh;
}
loft([
  [-.24,-.06,.22,.015],[-.4,-.13,.29,.12],[-.65,-.28,.3,.24],[-1.03,-.32,.255,.245],[-1.39,-.27,.18,.18],[-1.77,-.19,.1,.08],[-2.21,-.15,.008,.01]
],pouchMat,head);
loft([
  [-.25,.02,.17,.065],[-.44,.04,.32,.125],[-.78,.025,.31,.11],[-1.18,-.025,.245,.085],[-1.63,-.07,.15,.065],[-2.06,-.13,.045,.034],[-2.23,-.16,.005,.01]
],gold,head);
ellipsoid(head,orange,[-2.18,-.17,0],[.075,.072,.047],.3);
const eyes=[];
for(const side of [-1,1]) {
  curveMesh(head,[[-.38,-.06,.29*side],[-.82,-.08,.31*side],[-1.32,-.11,.215*side],[-1.85,-.15,.09*side],[-2.18,-.16,.008*side]],.014,orange,36);
  // Warm eye ring, black pupil and a tiny catchlight.
  eyes.push(ellipsoid(head,mat('#e6ba61'),[-.22,.22,.365*side],[.125,.135,.055],-.15));
  eyes.push(ellipsoid(head,graphite,[-.247,.228,.413*side],[.058,.072,.031]));
  eyes.push(ellipsoid(head,cream,[-.264,.255,.44*side],[.017,.019,.009]));
  curveMesh(head,[[-.35,.35,.35*side],[-.22,.387,.374*side],[-.105,.34,.36*side]],.027,cream,20);
  // The slight fold in the pelican's wonderfully impractical pouch.
  curveMesh(head,[[-.49,-.19,.26*side],[-.8,-.4,.255*side],[-1.2,-.44,.18*side]],.011,mat('#d99b39'),24);
}

function makeWing(side) {
  const wing = new THREE.Group();
  wing.position.set(-.05,2.3,.43*side);
  bird.add(wing);
  const tipHeight = side === -1 ? .52 : .03;
  // Individually modeled flight feathers make the wing silhouette scalloped.
  const tips = [
    [.08,.47+tipHeight,2.3],[.38,.42+tipHeight,2.55],[.72,.3+tipHeight,2.67],
    [1.04,.13+tipHeight,2.61],[1.32,-.02+tipHeight,2.43],[1.52,-.12+tipHeight,2.14],[1.59,-.16+tipHeight,1.81]
  ];
  for(let i=tips.length-1;i>=0;i--) {
    const tip=tips[i];
    feather(wing,[.12+i*.09,.3+tipHeight*.6,1.19*side],[tip[0],tip[1],tip[2]*side],.145,i%3===0?featherMid:graphite,.073);
  }
  const cover = new THREE.Shape();
  cover.moveTo(-.18,0);
  cover.bezierCurveTo(-.55,.4,-.56,1.06,-.29,1.58);
  cover.quadraticCurveTo(-.13,1.94,.14,2.08);
  cover.quadraticCurveTo(.47,1.93,.78,1.7);
  cover.quadraticCurveTo(1.28,1.32,.91,.69);
  cover.quadraticCurveTo(.5,.08,-.18,0);
  const coverGeo=new THREE.ExtrudeGeometry(cover,{depth:.12,bevelEnabled:true,bevelSize:.09,bevelThickness:.07,bevelSegments:4,curveSegments:24});
  const cv=coverGeo.attributes.position;
  for(let i=0;i<cv.count;i++) {
    const x=cv.getX(i), span=cv.getY(i), thickness=cv.getZ(i);
    cv.setXYZ(i,x,.08+span*(.16+tipHeight*.25)+thickness,span*side);
  }
  coverGeo.computeVertexNormals();
  const coverMesh=new THREE.Mesh(coverGeo,cream);
  coverMesh.castShadow=true;coverMesh.receiveShadow=true;wing.add(coverMesh);
  for(let i=0;i<6;i++) {
    const s=i/5;
    feather(wing,[.04+s*.6,.12+tipHeight*.25,(.25+s*.22)*side],[.54+s*.68,.23+tipHeight*.7,(1.36-s*.3)*side],.135,i%2===0?featherLight:cream,.08);
  }
  for(let i=0;i<5;i++) {
    const s=i/4;
    feather(wing,[-.14+s*.27,.37+tipHeight*.45,(.87+s*.15)*side],[.12+s*.75,.4+tipHeight*.7,(1.9+s*.12)*side],.12,featherLight,.07);
  }
  return wing;
}
const backWing=makeWing(-1);
const frontWing=makeWing(1);
backWing.rotation.y=-.28;
frontWing.rotation.y=-.37;

// A loose board leash is another small bit of surfboard character.
curveMesh(rider,[[2.4,.23,-.15],[2.8,.22,-.44],[2.65,.3,-.9],[1.65,.27,-1.02],[.8,.29,-.72],[.4,.48,.45]],.022,graphite,60);
const ankleBand = new THREE.Mesh(new THREE.TorusGeometry(.089,.027,8,24),graphite);
ankleBand.rotation.x=Math.PI/2;
ankleBand.position.set(.26,.56,.46);
rider.add(ankleBand);

// The wake continuously slips behind the board. Only the sea is in a hurry.
const wakeGroup=new THREE.Group();
wakeGroup.position.set(-1.25,.01,2);
scene.add(wakeGroup);
for(let k=0;k<7;k++) {
  const pts=[];
  const z=(k-3)*.16;
  for(let j=0;j<30;j++) {
    const x=.3+j/29*4.8;
    pts.push([x,.035+Math.sin(j*.5+k)*.012,z+Math.sin(j/29*Math.PI)*.18*(k>3?1:-1)]);
  }
  curveMesh(wakeGroup,pts,k===0||k===6?.028:.018,k%2?foamMat:paleFoam,35);
}
const spray=[];
for(let i=0;i<80;i++) {
  const mesh=new THREE.Mesh(dropGeo,i%3===0?paleFoam:foamMat);
  const size=.018+rand()*.042;
  mesh.scale.set(size,size*(1+rand()*1.4),size);
  scene.add(mesh);
  spray.push({mesh,phase:rand(),speed:.16+rand()*.2,side:rand()>.5?1:-1,spread:rand(),size});
}
const waterSpecks=[];
for(let i=0;i<105;i++) {
  const mesh=new THREE.Mesh(dropGeo,i%4===0?paleFoam:foamMat);
  const x=-5.6+rand()*12;
  const z=1+rand()*2.8;
  const size=.012+rand()*.038;
  mesh.scale.set(size*1.8,.012,size);
  mesh.position.set(x,seaHeight(x,z)+.045,z);
  seaGroup.add(mesh);
  waterSpecks.push({mesh,x,z,phase:rand()*Math.PI*2});
}

// Responsive framing, not an orbit controller: this is a moment to watch, not operate.
function resize() {
  const w=container.clientWidth;
  const h=container.clientHeight;
  renderer.setSize(w,h);
  const aspect=w/h;
  const mobile=window.innerWidth<=900;
  const viewHeight=mobile?12.2:10.9;
  const target=mobile?new THREE.Vector3(-2.3,1.9,1):new THREE.Vector3(-1.05,1.9,0);
  camera.position.copy(target).add(new THREE.Vector3(8.5,5.3,16.5));
  camera.lookAt(target);
  camera.left=-viewHeight*aspect/2;
  camera.right=viewHeight*aspect/2;
  camera.top=viewHeight/2;
  camera.bottom=-viewHeight/2;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(container);
resize();
const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
let runningTime=0;
let previous=performance.now();
function animate(now) {
  requestAnimationFrame(animate);
  const delta=Math.min((now-previous)/1000,.05);
  previous=now;
  if(!document.hidden && !reduceMotion.matches) runningTime+=delta;
  const t=runningTime;
  rider.position.y=.46+Math.sin(t*1.5)*.085;
  rider.position.x=-1.25+Math.sin(t*.7)*.1;
  rider.rotation.z=-.045+Math.sin(t*1.5+.3)*.025;
  rider.rotation.x=Math.sin(t*1.1)*.035;
  bird.rotation.z=-.025+Math.sin(t*1.5-.4)*.035;
  head.rotation.z=Math.sin(t*.95)*.035;
  const blinkPhase=t%6.4;
  const blink=blinkPhase>5.8&&blinkPhase<6.04?1-.96*Math.sin((blinkPhase-5.8)/.24*Math.PI):1;
  for(let i=0;i<eyes.length;i++) eyes[i].scale.y=[.135,.072,.019][i%3]*blink;
  frontWing.rotation.x=-.22+Math.sin(t*1.6)*.065;
  frontWing.rotation.z=Math.sin(t*1.6+.5)*.045;
  backWing.rotation.x=.52-Math.sin(t*1.6+.6)*.07;
  backWing.rotation.z=-Math.sin(t*1.6+.7)*.045;
  waveGroup.scale.y=1+Math.sin(t*.8)*.018;
  waveGroup.scale.z=1+Math.sin(t*.8+.7)*.015;
  for(const f of foamBlobs) f.mesh.position.y=f.y+Math.sin(t*2+f.phase)*.024;
  for(const r of rippleGroups) r.group.position.x=Math.sin(t*.7+r.phase)*.13;
  for(const p of spray) {
    const life=(p.phase+t*p.speed)%1;
    p.mesh.position.set(.8+life*3.5, .16+Math.sin(life*Math.PI)*(.28+p.spread*.8),2+p.side*(.5+life*(.5+p.spread)));
    const s=Math.sin(life*Math.PI)*p.size;
    p.mesh.scale.set(s,s*(1.1+life),s);
  }
  for(const p of waterSpecks) {
    p.mesh.position.x=p.x+Math.sin(t*.7+p.phase)*.1;
    p.mesh.position.y=seaHeight(p.x,p.z,t)+.04;
  }
  const oceanVertices=oceanGeo.attributes.position;
  for(let i=0;i<oceanVertices.count;i++) {
    const u=Math.floor(i/(sectors+1))/rings;
    const x=oceanVertices.getX(i),z=oceanVertices.getZ(i);
    oceanVertices.setY(i,seaHeight(x,z,t)-Math.pow(u,18)*.2);
  }
  oceanVertices.needsUpdate=true;
  renderer.render(scene,camera);
}
requestAnimationFrame(animate);
