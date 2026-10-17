import * as THREE from 'three';

// Everything in this little escape is built from geometry. No downloaded assets.
const mount = document.querySelector('#scene');
const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;
mount.appendChild(renderer.domElement);

const camera = new THREE.OrthographicCamera(-12, 12, 6, -6, .1, 100);
const hemi = new THREE.HemisphereLight(0xfffcf0, 0x549a8e, 2.4);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffe3b1, 4.0);
sun.position.set(-6, 12, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -13;
sun.shadow.camera.right = 13;
sun.shadow.camera.top = 10;
sun.shadow.camera.bottom = -10;
sun.shadow.normalBias = .035;
sun.shadow.bias = -.00015;
sun.shadow.radius = 5;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xd5f3ee, 1.3);
fill.position.set(5, 5, -8);
scene.add(fill);

const mat = (color, roughness = .6) => new THREE.MeshStandardMaterial({ color, roughness });
const ivory = mat('#fff9e7');
const cream = mat('#e8e4cf');
const wingWhite = mat('#f4f1dd');
const dark = mat('#344c4b');
const darkFeather = mat('#476160');
const orange = mat('#e9a249');
const billTop = mat('#f3b65e');
const pouch = mat('#e5a079');
const billEdge = mat('#aa6948');
const eyeBlack = mat('#142e30', .23);
const foamMat = mat('#e4f5dd', .75);
const foamBright = mat('#f4f9e6');
const seaLine = mat('#a0dec5');
const coral = mat('#e97e60', .4);
const rail = mat('#f5cba6', .5);
const sphereGeo = new THREE.SphereGeometry(1, 40, 28);
const smallSphereGeo = new THREE.SphereGeometry(1, 14, 10);
function ellipsoid(parent, material, position, scale, rot = 0, small = false) {
  const mesh = new THREE.Mesh(small ? smallSphereGeo : sphereGeo, material);
  mesh.position.set(...position); mesh.scale.set(...scale); mesh.rotation.z = rot;
  mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function curveTube(parent, points, radius, material, segments = 40) {
  const path = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(path, segments, radius, 9, false), material);
  mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
let seed = 37;
function random() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

// An irregular, gently domed patch of ocean, like a hand-made miniature.
const ocean = new THREE.Group();
scene.add(ocean);
const waterMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .32, metalness: .04, side: THREE.DoubleSide });
const oceanGeo = new THREE.BufferGeometry();
const oceanPos = [], oceanColors = [], oceanIndices = [];
const rings = 30, sides = 160;
const seaDeep = new THREE.Color('#168c8e'), seaLight = new THREE.Color('#69bfb0');
for (let r = 0; r <= rings; r++) {
  for (let a = 0; a <= sides; a++) {
    const angle = a / sides * Math.PI * 2, radius = r / rings;
    const edge = 1 + .035 * Math.sin(angle * 3) + .025 * Math.sin(angle * 5 + 1);
    const x = Math.cos(angle) * radius * 10.2 * edge;
    const z = Math.sin(angle) * radius * 4.5 * edge;
    const y = -.28 + Math.sin(radius * Math.PI) * .12 + .035 * Math.sin(x * 1.7 + z * 2) * radius;
    oceanPos.push(x, y, z);
    const color = seaDeep.clone().lerp(seaLight, Math.pow(radius, 3) * .88 + .07 * Math.sin(angle));
    oceanColors.push(color.r, color.g, color.b);
    if (r < rings && a < sides) { const i = r * (sides + 1) + a; oceanIndices.push(i, i + sides + 1, i + 1, i + 1, i + sides + 1, i + sides + 2); }
  }
}
oceanGeo.setAttribute('position', new THREE.Float32BufferAttribute(oceanPos, 3));
oceanGeo.setAttribute('color', new THREE.Float32BufferAttribute(oceanColors, 3));
oceanGeo.setIndex(oceanIndices); oceanGeo.computeVertexNormals();
const oceanMesh = new THREE.Mesh(oceanGeo, waterMat); oceanMesh.receiveShadow = true; ocean.add(oceanMesh);

// The wave's cross-section folds back onto itself into a translucent-looking curl.
const wave = new THREE.Group(); ocean.add(wave);
const section = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, -.22, 3.65), new THREE.Vector3(0, .02, 2.3),
  new THREE.Vector3(0, .42, .6), new THREE.Vector3(0, 1.3, -1.0),
  new THREE.Vector3(0, 2.65, -1.8), new THREE.Vector3(0, 3.65, -1.65),
  new THREE.Vector3(0, 4.12, -.85), new THREE.Vector3(0, 3.94, -.02),
  new THREE.Vector3(0, 3.38, .25)
]);
function wavePoint(u, v, extra = 0) {
  const x = -8.6 + u * 16.2;
  const p = section.getPoint(v);
  const envelope = Math.pow(Math.sin(Math.PI * u), .8) * (.35 + .86 * u);
  return new THREE.Vector3(x, -.19 + (p.y + .22) * envelope + extra,
    p.z * (.65 + .35 * Math.sin(Math.PI * u)) - .32 + .20 * Math.sin(u * Math.PI * 2));
}
const wp = [], wc = [], wi = [];
const nx = 140, ny = 64;
const deep = new THREE.Color('#087e83'), mid = new THREE.Color('#25afa5'), lip = new THREE.Color('#91d8be');
for (let i = 0; i <= nx; i++) {
  for (let j = 0; j <= ny; j++) {
    const u = i / nx, v = j / ny;
    const p = wavePoint(u, v); wp.push(p.x, p.y, p.z);
    let c = deep.clone().lerp(mid, .2 + .38 * Math.sin(v * Math.PI));
    if (v > .52) c.lerp(lip, Math.pow((v - .52) / .48, 1.3) * .95);
    const radius = Math.min(1, Math.sqrt(p.x * p.x / 104 + p.z * p.z / 20.25));
    const baseColor = seaDeep.clone().lerp(seaLight, Math.pow(radius, 3) * .88);
    const edgeBlend = Math.max(1 - THREE.MathUtils.smoothstep(v, 0, .24), 1 - THREE.MathUtils.smoothstep(Math.min(u, 1 - u), 0, .09));
    c.lerp(baseColor, edgeBlend);
    c.multiplyScalar(1 + .022 * Math.sin(u * 100 + v * 5));
    wc.push(c.r, c.g, c.b);
    if (i < nx && j < ny) { const n = i * (ny + 1) + j; wi.push(n, n + 1, n + ny + 1, n + 1, n + ny + 2, n + ny + 1); }
  }
}
const waveGeo = new THREE.BufferGeometry();
waveGeo.setAttribute('position', new THREE.Float32BufferAttribute(wp, 3));
waveGeo.setAttribute('color', new THREE.Float32BufferAttribute(wc, 3));
waveGeo.setIndex(wi); waveGeo.computeVertexNormals();
const waveMesh = new THREE.Mesh(waveGeo, waterMat); waveMesh.castShadow = true; waveMesh.receiveShadow = true; wave.add(waveMesh);

// Long foam ribbons and little pillowy bubbles pick out the crest.
for (let k = 0; k < 3; k++) {
  const points = [];
  for (let i = 0; i <= 100; i++) {
    const u = .025 + i / 100 * .95;
    const p = wavePoint(u, .955 - k * .052, .04 + .014 * Math.sin(i * .6));
    points.push(p.toArray());
  }
  curveTube(wave, points, .065 - k * .014, k === 0 ? foamBright : foamMat, 150);
}
for (let i = 0; i < 205; i++) {
  const u = .03 + random() * .94;
  const v = .86 + random() * .14;
  const p = wavePoint(u, v, .04);
  const s = .045 + random() * .105;
  ellipsoid(wave, i % 3 === 0 ? foamBright : foamMat, p.toArray(), [s * 1.5, s * .8, s], 0, true);
}
// Fine, flowing lines follow the face rather than a generic flat sea.
for (let k = 0; k < 8; k++) {
  const points = [], start = .11 + random() * .12, end = .79 + random() * .13;
  for (let i = 0; i <= 65; i++) {
    const u = start + (end - start) * i / 65;
    const p = wavePoint(u, .28 + k * .062 + Math.sin(u * 11 + k) * .009, .014);
    p.z += .016;
    points.push(p.toArray());
  }
  const material = mat(k % 3 === 0 ? '#6ac9b6' : '#3cb6a9', .45);
  curveTube(wave, points, .012 + (k % 2) * .006, material, 90);
}
// Decorative broken streaks on the water surface.
for (let i = 0; i < 32; i++) {
  const x = -8 + random() * 16, z = 1.25 + random() * 2.7;
  if ((x * x / 95 + z * z / 20) > .88) continue;
  const length = .3 + random() * 1.2;
  curveTube(ocean, [[x, -.08, z], [x + length * .5, -.06, z + .055], [x + length, -.09, z + .03]], .014 + random() * .012, seaLine, 14);
}

// The board is a rounded, rockered surfboard with real rails and a deck inlay.
const surfer = new THREE.Group();
surfer.position.set(.75, .56, 1.30);
scene.add(surfer);
const board = new THREE.Group(); surfer.add(board);
function boardGeometry(length, width, height) {
  const shape = new THREE.Shape();
  shape.moveTo(-length / 2, 0);
  shape.bezierCurveTo(-length / 2 + .15, width * .46, -length * .17, width * .54, length * .23, width * .40);
  shape.bezierCurveTo(length * .43, width * .34, length * .49, width * .17, length / 2, 0);
  shape.bezierCurveTo(length * .49, -width * .17, length * .43, -width * .34, length * .23, -width * .40);
  shape.bezierCurveTo(-length * .17, -width * .54, -length / 2 + .15, -width * .46, -length / 2, 0);
  const geo = new THREE.ExtrudeGeometry(shape, { depth: height, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: .055, bevelThickness: .045, curveSegments: 48 });
  geo.rotateX(-Math.PI / 2);
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setY(i, p.getY(i) + .19 * Math.pow(Math.abs(x) / (length / 2), 3)); }
  geo.computeVertexNormals(); return geo;
}
const boardBase = new THREE.Mesh(boardGeometry(4.7, 1.30, .11), rail); board.add(boardBase); boardBase.castShadow = true;
const deck = new THREE.Mesh(boardGeometry(4.60, 1.19, .025), coral); deck.position.y = .13; board.add(deck); deck.receiveShadow = true; deck.castShadow = true;
curveTube(board, [[-2.16, .32, 0], [-1.6, .245, 0], [0, .208, 0], [1.6, .245, 0], [2.13, .32, 0]], .025, ivory, 50);
// Two cream pinstripes on the front of the deck.
for (const x of [-1.72, -1.57]) {
  curveTube(board, [[x, .28, -.31], [x, .28, 0], [x, .28, .31]], .019, ivory, 12);
}
const fin = new THREE.Mesh(new THREE.ConeGeometry(.27, .56, 3), dark); fin.position.set(1.5, -.18, 0); fin.rotation.z = Math.PI; board.add(fin);

const bird = new THREE.Group(); bird.position.set(.15, .22, 0); surfer.add(bird);
// Short legs, broad webbed feet, and a few sculpted toe creases.
for (const z of [-.39, .42]) {
  curveTube(bird, [[.23, .90, z], [.05, .54, z], [-.03, .14, z + .04]], .085, orange, 15);
  const footShape = new THREE.Shape();
  footShape.moveTo(.18, -.10); footShape.quadraticCurveTo(-.12, -.12, -.48, -.23);
  footShape.quadraticCurveTo(-.59, -.20, -.52, -.10); footShape.lineTo(-.63, .015);
  footShape.quadraticCurveTo(-.64, .10, -.51, .11); footShape.lineTo(-.49, .24);
  footShape.quadraticCurveTo(-.41, .29, -.33, .21); footShape.lineTo(.18, .12); footShape.closePath();
  const fg = new THREE.ExtrudeGeometry(footShape, {depth:.055, bevelEnabled:true, bevelThickness:.035, bevelSize:.035, bevelSegments:3, steps:1}); fg.rotateX(-Math.PI/2);
  const foot = new THREE.Mesh(fg, orange); foot.position.set(-.02, .04, z); bird.add(foot); foot.castShadow = true;
  for (const dz of [-.12, .09]) curveTube(bird, [[.02,.135,z],[-.18,.13,z+dz*.6],[-.43,.12,z+dz]], .009, billEdge, 8);
}
const body = ellipsoid(bird, ivory, [.24, 1.45, 0], [.88, 1.08, .73], -.24);
ellipsoid(bird, cream, [-.28, 1.29, .05], [.52, .74, .61], -.35);
// Tail feathers fan behind the body.
for (let i = 0; i < 5; i++) {
  const feather = ellipsoid(bird, i < 2 ? dark : wingWhite, [1.00 + i * .035, 1.22, (i - 2) * .13], [.64, .16, .19], .27 + i * .04);
  feather.rotation.y = (i - 2) * -.12;
}
// Pelican's long S-curved neck; overlapping forms keep a soft clay-like silhouette.
curveTube(bird, [[-.21,1.75,0],[-.58,2.12,0],[-.52,2.65,0],[-.70,3.07,0],[-.91,3.23,0]], .32, ivory, 60);
ellipsoid(bird, ivory, [-.42, 2.05, 0], [.40, .59, .42], -.20);
ellipsoid(bird, ivory, [-.91, 3.24, 0], [.58, .51, .45], -.12);
// Wind-combed crest, understated rather than a cartoon mohawk.
for (let i = 0; i < 3; i++) {
  ellipsoid(bird, ivory, [-.53 + i * .12, 3.55 - i * .065, -.06], [.29, .08, .12], .42 - i * .12);
}
// Bill and expandable throat pouch, shaped separately with a crisp mouth seam.
function makeBill() {
  const shape = new THREE.Shape();
  shape.moveTo(-1.13, 3.24); shape.bezierCurveTo(-1.63, 3.28, -2.55, 3.20, -3.00, 3.02);
  shape.quadraticCurveTo(-3.11, 2.94, -2.94, 2.90); shape.bezierCurveTo(-2.40, 2.94, -1.65, 2.99, -1.10, 3.00); shape.closePath();
  const g = new THREE.ExtrudeGeometry(shape, {depth:.33, bevelEnabled:true, bevelSize:.065, bevelThickness:.06, bevelSegments:4, steps:1, curveSegments:40});
  const m = new THREE.Mesh(g, billTop); m.position.z = -.165; bird.add(m); m.castShadow = true;
  const lower = new THREE.Shape(); lower.moveTo(-1.13,3.00); lower.lineTo(-2.96,2.91);
  lower.bezierCurveTo(-2.52,2.79,-1.77,2.27,-1.36,2.48); lower.quadraticCurveTo(-1.03,2.63,-1.13,3.00);
  const pg = new THREE.ExtrudeGeometry(lower, {depth:.28, bevelEnabled:true, bevelSize:.09, bevelThickness:.10, bevelSegments:5, steps:1, curveSegments:40});
  const pm = new THREE.Mesh(pg,pouch); pm.position.z=-.14; bird.add(pm); pm.castShadow=true;
  for(const z of [-.25,.25]) curveTube(bird,[[-2.98,2.97,z*.35],[-2.47,3.015,z],[-1.75,3.06,z],[-1.13,3.08,z]],.015,billEdge,32);
  ellipsoid(bird, billEdge, [-1.62, 3.21, .238], [.058,.018,.012], .1);
}
makeBill();
// Eyes on both sides, with a blue-grey ring and a tiny catchlight.
for (const side of [-1, 1]) {
  const z = side * .397;
  ellipsoid(bird, mat('#c8d8c6'), [-1.04, 3.40, z], [.165, .174, .065]);
  ellipsoid(bird, ivory, [-1.065, 3.42, z + side * .045], [.13,.14,.046]);
  ellipsoid(bird, eyeBlack, [-1.10,3.42,z + side * .080], [.073,.087,.033]);
  ellipsoid(bird, foamBright, [-1.12,3.46,z + side * .108], [.021,.026,.012], 0, true);
  curveTube(bird,[[-1.18,3.60,z],[-1.05,3.64,z + side * .017],[-.90,3.59,z]],.025,ivory,12);
}
// The two outstretched wings are articulated at the shoulder for the loop.
const wings = [];
for (const side of [-1,1]) {
  const wing = new THREE.Group(); wing.position.set(.35,1.94,side*.50); bird.add(wing); wings.push(wing);
  const upper = ellipsoid(wing,wingWhite,[.30,.02,side*.38],[.68,.24,.68],.13); upper.rotation.y = side*-.35;
  const outer = ellipsoid(wing,wingWhite,[.72,-.015,side*.95],[.62,.17,.70],.15); outer.rotation.y=side*-.55;
  for(let i=0;i<6;i++) {
    const feather = ellipsoid(wing, i < 2 ? darkFeather : dark, [.51+i*.165,-.06-i*.025,side*(1.37-i*.065)], [.17,.105,.59-i*.027], .03);
    feather.rotation.y = side*(-.28-i*.105);
  }
  for(let i=0;i<5;i++) {
    const feather=ellipsoid(wing, i%2 ? ivory:cream, [.17+i*.18,.14,side*(.48+i*.10)],[.15,.095,.44]);
    feather.rotation.y = side*-.38;
  }
  wing.rotation.x = side * .06;
}

// A flowing little wake around the board, dotted with airborne sea spray.
const wake = new THREE.Group(); scene.add(wake);
for (let k=0;k<5;k++) {
  const z = 1.30 + (k-2)*.23;
  curveTube(wake, [[1.55,.30,z],[2.45,.19,z+.06],[3.45,-.04,z+.22],[4.4+k*.20,-.10,z+.39]], .025+(k%2)*.014, foamMat, 36);
}
const sprays = [];
for (let i=0;i<44;i++) {
  const droplet = new THREE.Mesh(smallSphereGeo, i%3 ? foamMat:foamBright);
  const data = { phase:random(), x:1.8+random()*2.0, z:1.0+random()*1.7, height:.20+random()*.80, speed:.35+random()*.3, size:.025+random()*.045 };
  droplet.scale.setScalar(data.size); wake.add(droplet); sprays.push({mesh:droplet,...data});
}
for (let i=0;i<65;i++) {
  const x=1.6+random()*4.2,z=.7+random()*2.1;
  ellipsoid(wake,foamMat,[x,-.06+random()*.12,z],[.055+random()*.10,.018,.035+random()*.055],0,true);
}
// Two distant seabirds, drawn as quiet sculptural strokes.
const distantBirds = new THREE.Group(); scene.add(distantBirds);
for (const [x,y,z,s] of [[-4.8,4.3,-3.5,.36],[-3.7,4.75,-4.2,.24]]) {
  const g=new THREE.Group(); g.position.set(x,y,z); g.scale.setScalar(s);
  curveTube(g,[[-.9,.15,0],[-.52,.32,0],[-.16,.13,0],[0,0,0],[.23,.22,0],[.6,.29,0],[.94,.12,0]],.035,darkFeather,30);
  distantBirds.add(g);
}

let mobile = false;
function resize() {
  const w = mount.clientWidth, h = mount.clientHeight;
  mobile = window.innerWidth <= 700;
  renderer.setSize(w,h);
  const aspect=w/h;
  const span = mobile ? 16.8 : 11.3;
  camera.left=-span*aspect/2;camera.right=span*aspect/2;camera.top=span/2;camera.bottom=-span/2;
  if(mobile) {
    camera.position.set(8,8,17);
    camera.lookAt(-.4,2.85,0);
    ocean.scale.setScalar(.76); ocean.position.set(.1,-1.6,0);
    surfer.scale.setScalar(1.04); surfer.position.set(.35,-.90,1.3);
    wake.scale.setScalar(.8); wake.position.set(0,-1.6,0);
    distantBirds.visible=false;
  } else {
    camera.position.set(8,7.2,16);
    camera.lookAt(-2.0,1.8,0);
    ocean.scale.setScalar(1);ocean.position.set(0,0,0);
    surfer.scale.setScalar(1.20);surfer.position.set(.9,.48,1.30);
    wake.scale.setScalar(1);wake.position.set(0,0,0);
    distantBirds.visible=true;
  }
  camera.updateProjectionMatrix();
}
window.addEventListener('resize',resize);
resize();
const clock=new THREE.Clock();
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function animate() {
  requestAnimationFrame(animate);
  const t=clock.getElapsedTime()*(reducedMotion?.18:1);
  surfer.position.y=(mobile?-.90:.48)+Math.sin(t*1.45)*.10+Math.sin(t*2.3)*.025;
  surfer.rotation.z=.035+Math.sin(t*1.45+.6)*.025;
  surfer.rotation.y=-.10+Math.sin(t*.8)*.025;
  bird.rotation.z=Math.sin(t*1.45-.5)*.025;
  wings[0].rotation.x=-.08+Math.sin(t*1.45+.3)*.075;
  wings[1].rotation.x=.08-Math.sin(t*1.45+.3)*.075;
  wings[0].rotation.z=Math.sin(t*1.2)*.025;
  wings[1].rotation.z=-Math.sin(t*1.2)*.025;
  wave.scale.y=1+Math.sin(t*.85)*.018;
  for(const p of sprays) {
    const life=(p.phase+t*p.speed)%1;
    p.mesh.position.set(p.x+life*.95,.18+Math.sin(life*Math.PI)*p.height,p.z+life*.28);
    const scale=p.size*Math.sin(life*Math.PI);
    p.mesh.scale.set(scale*.8,scale*1.4,scale*.8);
  }
  distantBirds.position.x=Math.sin(t*.13)*.22;
  renderer.render(scene,camera);
}
animate();
