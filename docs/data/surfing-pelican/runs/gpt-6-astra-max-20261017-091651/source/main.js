import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// Everything in this little world is modelled here. No downloaded models or textures.
const container = document.querySelector('#scene');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const TAU = Math.PI * 2;
const palette = {
  cream: '#fff7df', white: '#fffbed', feather: '#e8e8d6', slate: '#344f4b',
  orange: '#efa234', bill: '#ffc05a', pouch: '#eda455', coral: '#cf6746',
  water: '#329d9a', deep: '#087f82', mint: '#89d9c4', foam: '#f5fae7',
};
let seed = 41;
function random() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
const lerp = THREE.MathUtils.lerp;
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
function material(color, roughness = .6, extra = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness, ...extra });
}
const mats = {
  cream: material(palette.cream), white: material(palette.white), feather: material(palette.feather),
  slate: material(palette.slate, .65), orange: material(palette.orange, .48),
  bill: material(palette.bill, .44), pouch: material(palette.pouch, .65),
  coral: material(palette.coral, .8), eye: material('#142f2c', .25),
  foam: material(palette.foam, .85), mint: material('#b1e8d4', .5),
};
const scene = new THREE.Scene();
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
} catch {
  container.classList.add('fallback');
  container.textContent = 'Somewhere, a pelican is having a very good day.';
}
function start() {
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.04;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');
  const studio = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(studio, .04).texture;
  scene.environmentIntensity = .19;
  studio.dispose();
  pmrem.dispose();

  const camera = new THREE.OrthographicCamera(-9, 9, 7, -7, .1, 100);
  camera.position.set(9, 7.2, 13);
  camera.lookAt(0, 1.35, 0);
  scene.add(new THREE.HemisphereLight('#fff7e4', '#7ca9a0', 2.05));
  scene.add(new THREE.AmbientLight('#d5f3df', .32));
  const sunlight = new THREE.DirectionalLight('#fff0cd', 3.0);
  sunlight.position.set(-3, 10, 7);
  sunlight.castShadow = true;
  sunlight.shadow.mapSize.set(2048, 2048);
  Object.assign(sunlight.shadow.camera, { left: -9, right: 9, top: 8, bottom: -7, near: 1, far: 30 });
  sunlight.shadow.bias = -.0004;
  sunlight.shadow.normalBias = .035;
  sunlight.shadow.radius = 4;
  scene.add(sunlight);
  const fill = new THREE.DirectionalLight('#c7f8ed', 1.1);
  fill.position.set(6, 5, -5);
  scene.add(fill);

  // A soft, painted contact shadow keeps the sculptural ocean grounded.
  const shadowCanvas = document.createElement('canvas');
  shadowCanvas.width = shadowCanvas.height = 128;
  const ctx = shadowCanvas.getContext('2d');
  const gradient = ctx.createRadialGradient(64, 64, 3, 64, 64, 64);
  gradient.addColorStop(0, 'rgba(42,76,61,.23)');
  gradient.addColorStop(.55, 'rgba(42,76,61,.12)');
  gradient.addColorStop(1, 'rgba(42,76,61,0)');
  ctx.fillStyle = gradient; ctx.fillRect(0, 0, 128, 128);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(16.5, 11.2), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(shadowCanvas), transparent: true, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.set(0, -.48, .2);
  scene.add(shadow);

  const world = new THREE.Group();
  scene.add(world);
  const ocean = makeOcean();
  world.add(ocean.group);
  const wave = makeWave();
  world.add(wave.group);
  const surfer = makeSurfer();
  surfer.group.position.set(.65, .28, 1.25);
  surfer.group.rotation.y = -.16;
  surfer.group.rotation.z = -.065;
  world.add(surfer.group);
  const wake = makeWake();
  world.add(wake.group);
  const spray = makeSpray();
  world.add(spray.group);

  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    const aspect = w / h;
    // Keep the full miniature in frame, even on a narrow phone.
    const width = aspect < 1.05 ? 15.9 : 17.7;
    const height = width / aspect;
    camera.left = -width / 2; camera.right = width / 2;
    camera.top = height / 2; camera.bottom = -height / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    if (reducedMotion) renderer.render(scene, camera);
  }
  new ResizeObserver(resize).observe(container);
  resize();

  let elapsed = 0, last = performance.now();
  function frame(now) {
    if (!reducedMotion) requestAnimationFrame(frame);
    const dt = Math.min((now - last) / 1000, .04);
    last = now;
    if (document.hidden) return;
    if (!reducedMotion) elapsed += dt;
    const t = elapsed;
    surfer.group.position.y = .28 + Math.sin(t * 1.45) * .045;
    surfer.group.position.x = .65 + Math.sin(t * .55) * .18;
    surfer.group.position.z = 1.25 + Math.sin(t * .8) * .08;
    surfer.group.rotation.z = -.055 + Math.sin(t * 1.45 + .7) * .034;
    surfer.group.rotation.x = .025 + Math.sin(t * 1.1) * .028;
    surfer.bird.rotation.z = Math.sin(t * 1.45 + 1.4) * .022;
    surfer.nearWing.rotation.x = -.06 + Math.sin(t * 1.45 + .3) * .065;
    surfer.farWing.rotation.x = .43 - Math.sin(t * 1.45 + .8) * .065;
    surfer.nearWing.rotation.z = Math.sin(t * 1.1) * .025;
    surfer.head.rotation.z = Math.sin(t * .85) * .024;
    const blink = t % 7.2;
    const eyeScale = blink > 6.95 ? .15 + .85 * Math.abs((blink - 7.075) / .125) : 1;
    surfer.eyes.forEach(eye => { eye.scale.y = eyeScale; });
    surfer.scarves.forEach((mesh, n) => {
      const a = mesh.geometry.attributes.position;
      const base = mesh.userData.base;
      for (let i = 0; i < a.count; i++) {
        const influence = Math.max(0, (-base[i * 3] - .1) / 1.2);
        a.setY(i, base[i * 3 + 1] + Math.sin(t * 4.5 + influence * 4 + n) * .07 * influence);
        a.setZ(i, base[i * 3 + 2] + Math.cos(t * 4 + influence * 3) * .045 * influence);
      }
      a.needsUpdate = true;
    });
    wave.group.position.y = Math.sin(t * .8) * .035;
    wave.group.scale.y = 1 + Math.sin(t * .65) * .012;
    ocean.animate(t);
    wake.animate(t);
    spray.animate(t);
    renderer.render(scene, camera);
  }
  requestAnimationFrame(frame);
}

function mesh(geometry, mat, parent, position, scale) {
  const object = new THREE.Mesh(geometry, mat);
  if (position) object.position.set(...position);
  if (scale) object.scale.set(...scale);
  object.castShadow = true;
  object.receiveShadow = true;
  parent.add(object);
  return object;
}
const sphereGeometry = new THREE.SphereGeometry(1, 32, 24);
const foamGeometry = new THREE.SphereGeometry(1, 12, 8);
function ellipsoid(parent, mat, position, scale) {
  return mesh(mat === mats.foam || mat === mats.mint ? foamGeometry : sphereGeometry, mat, parent, position, scale);
}
function batchStaticFoam(group) {
  for (const mat of [mats.foam, mats.mint]) {
    const objects = group.children.filter(object => object.geometry === foamGeometry && object.material === mat);
    if (!objects.length) continue;
    const batch = new THREE.InstancedMesh(foamGeometry, mat, objects.length);
    batch.receiveShadow = true;
    objects.forEach((object, i) => {
      object.updateMatrix();
      batch.setMatrixAt(i, object.matrix);
      group.remove(object);
    });
    group.add(batch);
  }
}
function tube(parent, points, radius, mat, segments = 48, radial = 8) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => Array.isArray(p) ? v3(...p) : p));
  return mesh(new THREE.TubeGeometry(curve, segments, radius, radial, false), mat, parent);
}
function taperedTube(parent, points, radii, mat) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => v3(...p)));
  const steps = 36, sides = 16, positions = [], indices = [];
  const frames = curve.computeFrenetFrames(steps, false);
  for (let i = 0; i <= steps; i++) {
    const u = i / steps, point = curve.getPointAt(u);
    const ri = u * (radii.length - 1), k = Math.min(Math.floor(ri), radii.length - 2);
    const radius = lerp(radii[k], radii[k + 1], ri - k);
    for (let j = 0; j <= sides; j++) {
      const a = j / sides * TAU;
      const p = point.clone().addScaledVector(frames.normals[i], Math.cos(a) * radius).addScaledVector(frames.binormals[i], Math.sin(a) * radius);
      positions.push(p.x, p.y, p.z);
      if (i < steps && j < sides) {
        const q = i * (sides + 1) + j;
        indices.push(q, q + 1, q + sides + 1, q + 1, q + sides + 2, q + sides + 1);
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices); geo.computeVertexNormals();
  return mesh(geo, mat, parent);
}

function feather(parent, start, end, width, thickness, mat) {
  const a = v3(...start), b = v3(...end), dir = b.clone().sub(a).normalize();
  const side = new THREE.Vector3(0, 1, 0).cross(dir).normalize();
  const normal = dir.clone().cross(side).normalize();
  const positions = [], indices = [], steps = 14, sides = 10;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps, bulge = Math.pow(Math.sin(Math.PI * t), .62) * (1.15 - t * .3);
    const p = a.clone().lerp(b, t);
    p.y += Math.sin(t * Math.PI) * .045;
    for (let j = 0; j <= sides; j++) {
      const angle = j / sides * TAU;
      const q = p.clone().addScaledVector(side, Math.cos(angle) * width * bulge).addScaledVector(normal, Math.sin(angle) * thickness * bulge);
      positions.push(q.x, q.y, q.z);
      if (i < steps && j < sides) {
        const k = i * (sides + 1) + j;
        indices.push(k, k + 1, k + sides + 1, k + 1, k + sides + 2, k + sides + 1);
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  return mesh(geometry, mat, parent);
}

function makeSurfer() {
  const group = new THREE.Group();
  makeBoard(group);
  const bird = new THREE.Group();
  bird.scale.set(1.08, 1.08, 1.08);
  group.add(bird);

  // Two bent legs and broad, three-toed webbed feet.
  for (const [x, z] of [[-.58, .3], [.56, -.2]]) {
    taperedTube(bird, [[x - .15, 1.31, z], [x - .27, .82, z], [x, .32, z]], [.09, .072, .07], mats.orange);
    const foot = new THREE.Shape();
    foot.moveTo(-.1, 0);
    foot.bezierCurveTo(-.03, .13, .20, .19, .44, .23);
    foot.quadraticCurveTo(.52, .23, .45, .12);
    foot.lineTo(.56, .015);
    foot.quadraticCurveTo(.58, -.04, .46, -.09);
    foot.lineTo(.43, -.23);
    foot.quadraticCurveTo(.16, -.17, -.1, 0);
    const g = new THREE.ExtrudeGeometry(foot, { depth: .06, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: .035, bevelThickness: .025, curveSegments: 12 });
    g.rotateX(-Math.PI / 2);
    mesh(g, mats.orange, bird, [x, .26, z]);
    for (const dz of [-.10, .09]) tube(bird, [[x + .06, .34, z], [x + .26, .34, z + dz * .6], [x + .43, .325, z + dz]], .009, mats.pouch, 12, 5);
  }

  // A plump, pear-shaped body, with little overlapping tail feathers.
  for (let i = 0; i < 5; i++) {
    feather(bird, [-.64, 1.65, (i - 2) * .1], [-1.7 + Math.abs(i - 2) * .09, 1.71, (i - 2) * .19], .16, .08, i % 2 ? mats.feather : mats.cream);
  }
  const body = ellipsoid(bird, mats.white, [-.06, 1.87, 0], [.96, .87, .68]);
  body.rotation.z = -.12;

  const nearWing = makeWing(1);
  nearWing.position.set(-.35, 2.15, .45);
  nearWing.rotation.y = .12;
  bird.add(nearWing);
  const farWing = makeWing(-1);
  farWing.position.set(-.30, 2.18, -.25);
  farWing.rotation.y = -1.1;
  bird.add(farWing);

  taperedTube(bird, [[.35, 2.23, 0], [.51, 2.65, 0], [.43, 3.22, 0], [.73, 3.79, 0]], [.42, .29, .225, .34], mats.white);
  const head = new THREE.Group();
  head.position.set(.72, 3.75, 0);
  bird.add(head);
  ellipsoid(head, mats.white, [.09, .12, 0], [.49, .47, .405]);
  // A few wind-combed feathers on the back of the head.
  feather(head, [-.05, .38, -.12], [-.55, .51, -.12], .13, .07, mats.cream);
  feather(head, [-.07, .43, .02], [-.46, .60, .035], .12, .065, mats.white);
  feather(head, [-.08, .36, .16], [-.45, .44, .20], .12, .065, mats.cream);
  makeBill(head);
  const eyes = [];
  for (const sign of [-1, 1]) {
    ellipsoid(head, mats.pouch, [.26, .21, sign * .343], [.145, .15, .065]);
    ellipsoid(head, mats.white, [.278, .221, sign * .382], [.106, .113, .032]);
    const eye = new THREE.Group();
    eye.position.set(.30, .225, sign * .411);
    head.add(eye);
    ellipsoid(eye, mats.eye, [0, 0, 0], [.064, .082, .025]);
    ellipsoid(eye, mats.white, [.016, .03, sign * .023], [.021, .024, .012]);
    eyes.push(eye);
    tube(head, [[.14, .35, sign * .327], [.255, .385, sign * .325], [.35, .355, sign * .30]], .022, mats.feather, 16, 6);
  }

  // The little neckerchief is the only thing he bothered to put on today.
  const cloth = material(palette.coral, .85, { side: THREE.DoubleSide });
  const collar = mesh(new THREE.CylinderGeometry(.328, .342, .17, 40, 1, true), cloth, bird, [.49, 2.75, 0]);
  collar.rotation.z = .07;
  const kerchief = new THREE.BufferGeometry();
  kerchief.setAttribute('position', new THREE.Float32BufferAttribute([.22, 2.71, .27, .75, 2.71, .27, .52, 2.41, .35], 3));
  kerchief.computeVertexNormals();
  mesh(kerchief, cloth, bird);
  ellipsoid(bird, mats.coral, [.20, 2.75, .08], [.13, .13, .15]);
  const scarves = [];
  for (let k = 0; k < 2; k++) {
    const vertices = [], indices = [];
    for (let i = 0; i <= 12; i++) {
      const t = i / 12;
      for (let side = 0; side < 2; side++) {
        vertices.push(.2 - t * (1.14 - k * .15), 2.76 + .15 * Math.sin(t * 2.5) - k * .18 + (side - .5) * (.2 * (1 - t * .3)), .09 + t * (.28 + k * .15));
      }
      if (i < 12) { const n = i * 2; indices.push(n, n + 1, n + 2, n + 1, n + 3, n + 2); }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3)); geo.setIndex(indices); geo.computeVertexNormals();
    const scarf = mesh(geo, material(k ? '#dc7954' : palette.coral, .9, { side: THREE.DoubleSide }), bird);
    scarf.userData.base = Float32Array.from(vertices);
    scarves.push(scarf);
  }
  return { group, bird, head, nearWing, farWing, eyes, scarves };
}

function makeBill(head) {
  // Elliptical sections give the upper bill a ridge and the lower bill its unmistakable pouch.
  for (const lower of [true, false]) {
    const vertices = [], indices = [], colors = [], steps = 36, sides = 24;
    const colorA = new THREE.Color(lower ? '#eaa153' : '#ffbd4d');
    const colorB = new THREE.Color(lower ? '#f6bd70' : '#ffd374');
    for (let i = 0; i <= steps; i++) {
      const u = i / steps;
      const width = .255 * Math.pow(1 - u, .67) + .008;
      const baseline = -.035 - u * .115;
      const bottom = baseline - .58 * Math.pow(Math.sin(Math.PI * u), .75);
      const y = lower ? (baseline + bottom) / 2 : baseline + .09 * (1 - u);
      const ry = lower ? Math.max(.008, (baseline - bottom) / 2) : .12 * Math.pow(1 - u, .5) + .01;
      for (let j = 0; j <= sides; j++) {
        const a = j / sides * TAU;
        vertices.push(.37 + 2.35 * u, y + Math.sin(a) * ry, Math.cos(a) * width);
        const c = colorA.clone().lerp(colorB, Math.max(0, Math.sin(a)) * .65);
        colors.push(c.r, c.g, c.b);
        if (i < steps && j < sides) {
          const k = i * (sides + 1) + j;
          indices.push(k, k + sides + 1, k + 1, k + 1, k + sides + 1, k + sides + 2);
        }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geo.setIndex(indices); geo.computeVertexNormals();
    mesh(geo, material('#ffffff', .5, { vertexColors: true, side: THREE.DoubleSide }), head);
  }
  const lineMat = material('#a66f35');
  for (const sign of [-1, 1]) {
    const points = [];
    for (let i = 0; i <= 20; i++) {
      const t = i / 20;
      points.push([.39 + 2.31 * t, -.039 - t * .115, sign * (.257 * Math.pow(1 - t, .67) + .009)]);
    }
    tube(head, points, .012, lineMat, 40, 6);
    ellipsoid(head, lineMat, [.76, .049, sign * .213], [.065, .014, .009]);
  }
}

function makeWing(sign) {
  const group = new THREE.Group();
  // The primary feathers fan out individually, rather than forming one flat paddle.
  for (let i = 0; i < 7; i++) {
    feather(group,
      [-.26 - i * .105, .40 - i * .027, sign * (1.34 - i * .026)],
      [-.34 - i * .29, .47 - i * .09, sign * (2.92 - i * .145)],
      .165, .068, i % 2 ? mats.slate : material('#3c5751', .7));
  }
  const vertices = [], indices = [], steps = 28, sides = 24;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const z = t * 1.87;
    const lead = .15 - .45 * t * t;
    const chord = .67 * Math.pow(Math.sin(Math.PI * (.1 + t * .87)), .55);
    for (let j = 0; j <= sides; j++) {
      const angle = j / sides * TAU;
      const x = lead - chord * (1 + Math.cos(angle)) / 2;
      const y = .46 * Math.sin(t * Math.PI * .73) + Math.sin(angle) * .16 * Math.pow(Math.sin(Math.PI * t), .4);
      vertices.push(x, y, sign * z);
      if (i < steps && j < sides) {
        const q = i * (sides + 1) + j;
        if (sign === 1) indices.push(q, q + sides + 1, q + 1, q + 1, q + sides + 1, q + sides + 2);
        else indices.push(q, q + 1, q + sides + 1, q + 1, q + sides + 2, q + sides + 1);
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3)); geo.setIndex(indices); geo.computeVertexNormals();
  mesh(geo, material(palette.cream, .7, { side: THREE.DoubleSide }), group);
  for (let i = 0; i < 9; i++) {
    const t = i / 9;
    const z = .25 + t * 1.44;
    const y = .46 * Math.sin(z / 1.87 * Math.PI * .73);
    feather(group, [-.13 - t * .24, y + .035, sign * z], [-.85 - t * .27, y - .065, sign * (z + .18)], .135, .075, i % 3 === 0 ? mats.feather : mats.white);
  }
  return group;
}

function makeBoard(parent) {
  const shape = new THREE.Shape();
  shape.moveTo(-2.56, 0);
  shape.bezierCurveTo(-2.56, .34, -1.9, .53, -.9, .565);
  shape.bezierCurveTo(.65, .64, 2.35, .44, 2.68, 0);
  shape.bezierCurveTo(2.35, -.44, .65, -.64, -.9, -.565);
  shape.bezierCurveTo(-1.9, -.53, -2.56, -.34, -2.56, 0);
  const geo = new THREE.ExtrudeGeometry(shape, { steps: 1, depth: .13, bevelEnabled: true, bevelSize: .07, bevelThickness: .065, bevelSegments: 4, curveSegments: 36 });
  geo.rotateX(-Math.PI / 2);
  mesh(geo, [material('#e7a142', .38), material('#fff1c9', .45)], parent, [0, .055, 0]);
  // An inlaid ivory stringer, with two thin, dark pinstripes.
  const stripe = new THREE.Shape();
  stripe.moveTo(-2.5, -.075); stripe.quadraticCurveTo(0, -.12, 2.56, -.048);
  stripe.lineTo(2.61, 0); stripe.lineTo(2.56, .048); stripe.quadraticCurveTo(0, .12, -2.5, .075); stripe.closePath();
  const stripeGeo = new THREE.ShapeGeometry(stripe, 30); stripeGeo.rotateX(-Math.PI / 2);
  mesh(stripeGeo, material('#fff6d9', .55, { side: THREE.DoubleSide }), parent, [0, .253, 0]);
  for (const z of [-.14, .14]) tube(parent, [[-2.35, .254, z * .55], [-1.1, .255, z], [.9, .255, z], [2.35, .254, z * .45]], .009, mats.slate, 48, 5);
  // A simple hand-painted wave on the nose.
  tube(parent, [[1.7, .257, .23], [1.85, .258, .23], [1.96, .258, .14], [1.93, .258, .08], [1.87, .258, .12], [1.98, .258, .22], [2.17, .258, .20]], .017, mats.slate, 28, 6);
  const finShape = new THREE.Shape();
  finShape.moveTo(-1.92, 0); finShape.quadraticCurveTo(-2.1, -.45, -1.65, -.57); finShape.quadraticCurveTo(-1.73, -.25, -1.32, 0); finShape.closePath();
  mesh(new THREE.ExtrudeGeometry(finShape, { depth: .06, bevelEnabled: true, bevelSize: .025, bevelThickness: .025, bevelSegments: 2 }), mats.slate, parent, [0, .015, -.03]);
  // A coiled leash floats behind the tail.
  tube(parent, [[-2.2, .26, .27], [-2.55, .30, .48], [-2.8, .16, .75], [-2.64, .02, 1.06], [-2.27, .04, .94], [-2.14, .18, .62]], .018, mats.slate, 45, 6);
}

function makeOcean() {
  const group = new THREE.Group();
  const positions = [], colors = [], indices = [], radial = 44, around = 160;
  const deep = new THREE.Color('#239997'), pale = new THREE.Color('#71c5b2');
  for (let r = 0; r <= radial; r++) {
    const u = r / radial;
    for (let j = 0; j <= around; j++) {
      const a = j / around * TAU;
      const irregular = 1 + .025 * Math.sin(a * 3 + 1) + .018 * Math.cos(a * 7);
      const x = Math.cos(a) * 6.65 * u * irregular;
      const z = Math.sin(a) * 4.12 * u * irregular - .25;
      const edge = Math.pow(Math.max(0, (u - .86) / .14), 2);
      const y = .08 + (Math.sin(x * 1.1 + z * 1.4) + Math.sin(z * 2.6 - x * .35)) * .026 * (1 - edge) - edge * .28;
      positions.push(x, y, z);
      const c = deep.clone().lerp(pale, .12 + Math.pow(u, 4) * .66 + .07 * Math.sin(x + z));
      colors.push(c.r, c.g, c.b);
      if (r < radial && j < around) {
        const k = r * (around + 1) + j;
        indices.push(k, k + 1, k + around + 1, k + 1, k + around + 2, k + around + 1);
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices); geo.computeVertexNormals();
  const mat = material('#ffffff', .36, { vertexColors: true, metalness: .04, side: THREE.DoubleSide });
  const surface = mesh(geo, mat, group); surface.castShadow = false;
  const base = Float32Array.from(positions);

  // Contour-like little currents around the edge of the miniature.
  const rippleMat = material('#b5e5cf', .6, { transparent: true, opacity: .66 });
  const rippleMat2 = material('#e2efcf', .7, { transparent: true, opacity: .75 });
  for (let i = 0; i < 25; i++) {
    const a = random() * TAU, r = .71 + random() * .23;
    const points = [];
    const len = .09 + random() * .18;
    for (let j = 0; j <= 24; j++) {
      const ang = a + j / 24 * len;
      points.push([Math.cos(ang) * 6.5 * r, .115 - Math.max(0, r - .87) * .9, Math.sin(ang) * 4.07 * r - .25]);
    }
    const ripple = tube(group, points, .012 + random() * .011, i % 4 === 0 ? rippleMat2 : rippleMat, 24, 5);
    ripple.castShadow = false;
  }
  for (let i = 0; i < 9; i++) {
    const a = .10 + i * .18;
    const points = [];
    for (let j = 0; j <= 30; j++) {
      const theta = a + j / 30 * .12;
      points.push([Math.cos(theta) * 6.96, -.3, Math.sin(theta) * 4.38 - .25]);
    }
    const ripple = tube(group, points, .015, rippleMat, 30, 6); ripple.castShadow = false;
  }
  return { group, animate(t) {
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = base[i * 3], z = base[i * 3 + 2];
      const r = Math.hypot(x / 6.7, (z + .25) / 4.2);
      pos.array[i * 3 + 1] = base[i * 3 + 1] + Math.sin(x * 1.4 + z * 2.4 - t * 1.3) * .024 * Math.max(0, 1 - r * r);
    }
    pos.needsUpdate = true;
  } };
}

// Wave cross-section: a sweeping face folds over into a rounded, translucent-looking lip.
const waveProfile = new THREE.CatmullRomCurve3([
  v3(0, .03, 1.55), v3(0, .50, .36), v3(0, 1.55, -1.04),
  v3(0, 2.7, -1.39), v3(0, 3.65, -.98), v3(0, 4.04, -.14),
  v3(0, 3.85, .57), v3(0, 3.31, .83),
  v3(0, 3.30, 1.07), v3(0, 4.02, .93), v3(0, 4.40, -.05),
  v3(0, 4.01, -1.25), v3(0, 2.83, -2.02), v3(0, .10, -3.04),
  v3(0, -.06, -.5),
], true, 'catmullrom', .38);
function waveFactor(u) {
  return Math.pow(Math.sin(Math.PI * THREE.MathUtils.clamp(u, .001, .999)), .66) * (1.18 - u * .44);
}
function wavePoint(u, s) {
  const p = waveProfile.getPoint(s);
  const f = waveFactor(u);
  p.x = -5.75 + 10.9 * u;
  p.y = p.y * f + .06;
  p.z = p.z * (.08 + .92 * f) - .62 + Math.sin(u * Math.PI) * .22 + .25 * (u - .5);
  return p;
}
function makeWave() {
  const group = new THREE.Group();
  const vertices = [], colors = [], indices = [], nx = 120, ns = 100;
  const dark = new THREE.Color('#108b8e'), middle = new THREE.Color('#26b2a7'), top = new THREE.Color('#6ed3b9');
  for (let i = 0; i <= nx; i++) {
    const u = i / nx;
    for (let j = 0; j <= ns; j++) {
      const s = j / ns;
      const p = wavePoint(u, s);
      vertices.push(p.x, p.y, p.z);
      const profile = waveProfile.getPoint(s);
      const amount = Math.max(0, Math.min(1, profile.y / 4.4));
      let c = dark.clone().lerp(middle, amount * .85);
      c.lerp(top, Math.pow(amount, 4) * .85);
      // Deep jade inside the hollow, warm, light mint along the upper surface.
      if (s > .13 && s < .31) c.multiplyScalar(.85 + .1 * Math.cos(s * 20));
      if (s > .49 && s < .78) c.lerp(top, .24);
      c.lerp(middle, Math.pow(Math.abs(u - .5) * 2, 4) * .6);
      colors.push(c.r, c.g, c.b);
      if (i < nx && j < ns) {
        const k = i * (ns + 1) + j;
        indices.push(k, k + ns + 1, k + 1, k + 1, k + ns + 1, k + ns + 2);
      }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices); geo.computeVertexNormals();
  mesh(geo, material('#ffffff', .31, { vertexColors: true, metalness: .04, side: THREE.DoubleSide }), group);

  // Long, hand-drawn-looking threads follow the curvature of the water.
  const lineMats = [material('#88d9c3', .5), material('#5ac5b6', .45), material('#bbe9d1', .6)];
  for (let k = 0; k < 14; k++) {
    const s = .045 + k * .0305;
    const start = .035 + random() * .16, end = .80 + random() * .15;
    const points = [];
    for (let j = 0; j <= 85; j++) {
      const u = lerp(start, end, j / 85);
      const p = wavePoint(u, s + Math.sin(u * 12 + k * .7) * .007 + Math.sin(u * 5 + k) * .005);
      p.z += .025;
      p.y += .012;
      points.push(p);
    }
    const line = tube(group, points, k % 4 === 0 ? .014 : .007, lineMats[k % 3], 85, 5);
    line.castShadow = false;
  }
  // The fold has two creamy foam ribbons, not a uniform white pipe.
  const lipS = 7.45 / 15;
  for (let k = 0; k < 3; k++) {
    const points = [];
    for (let j = 0; j <= 100; j++) {
      const u = .016 + j / 100 * .97;
      const p = wavePoint(u, lipS - k * .007);
      p.z += .035 + k * .045;
      p.y += Math.sin(u * 60 + k) * .025 + k * .055;
      points.push(p);
    }
    tube(group, points, k === 0 ? .092 : .055, k === 2 ? mats.mint : mats.foam, 130, 8);
  }
  // Small overlapping, stretched bubbles keep the foam organic at silhouette scale.
  for (let i = 0; i < 205; i++) {
    const u = .01 + i / 205 * .98;
    const p = wavePoint(u, lipS + (random() - .5) * .027);
    const r = .04 + random() * .12;
    p.z += .045 + random() * .05;
    p.y += random() * .10;
    const blob = ellipsoid(group, i % 8 === 0 ? mats.mint : mats.foam, [p.x, p.y, p.z], [r * (1 + random() * .8), r * .72, r]);
    blob.castShadow = false;
  }
  // A wash of foam gathers where the wave meets the still water.
  for (let i = 0; i < 70; i++) {
    const u = random(), p = wavePoint(u, .01 + random() * .03);
    p.z += random() * .37;
    const r = .035 + random() * .08;
    const blob = ellipsoid(group, i % 3 ? mats.foam : mats.mint, [p.x, .13 + random() * .07, p.z], [r * 2.3, .025, r * .8]);
    blob.castShadow = false;
  }
  batchStaticFoam(group);
  return { group };
}

function makeWake() {
  const group = new THREE.Group();
  const mat = material('#f5f7dc', .7, { transparent: true, opacity: .9 });
  for (let i = 0; i < 4; i++) {
    const points = [];
    for (let j = 0; j <= 35; j++) {
      const t = j / 35;
      points.push([-1.0 - t * (3.9 + i * .08), .18 + Math.sin(t * Math.PI) * .10, 1.4 + i * .12 + Math.sin(t * 2.7) * (.55 + i * .05)]);
    }
    const line = tube(group, points, i % 3 === 0 ? .036 : .015, mat, 40, 6); line.castShadow = false;
  }
  const bubbles = [];
  const foam = new THREE.InstancedMesh(foamGeometry, mats.foam, 80);
  foam.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  foam.frustumCulled = false;
  group.add(foam);
  const transform = new THREE.Object3D();
  for (let i = 0; i < 80; i++) {
    const t = random(), r = .022 + random() * .06;
    const p = [-1.1 - t * 4.1, .2 + random() * .08, 1.35 + Math.sin(t * 2.7) * .8 + random() * .8];
    bubbles.push({ base: p, phase: random() * TAU, radius: r });
  }
  function animate(t) {
    bubbles.forEach((b, i) => {
      const pulse = Math.sin(t * 2 + b.phase);
      transform.position.set(b.base[0], b.base[1] + pulse * .025, b.base[2]);
      transform.scale.set(b.radius * 1.8, .03 + pulse * .006, b.radius);
      transform.updateMatrix();
      foam.setMatrixAt(i, transform.matrix);
    });
    foam.instanceMatrix.needsUpdate = true;
  }
  animate(0);
  return { group, animate }; 
}

function makeSpray() {
  const group = new THREE.Group(), droplets = [];
  const geo = new THREE.SphereGeometry(1, 8, 6);
  const spray = new THREE.InstancedMesh(geo, material('#ffffff', .85), 88);
  spray.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  spray.frustumCulled = false;
  group.add(spray);
  const transform = new THREE.Object3D();
  for (let i = 0; i < 66; i++) {
    const u = .08 + random() * .82;
    const origin = wavePoint(u, 7.45 / 15);
    const r = .022 + random() * .035;
    spray.setColorAt(i, new THREE.Color(i % 4 ? palette.foam : '#b1e8d4'));
    droplets.push({ origin, phase: random(), speed: .3 + random() * .25, height: .4 + random() * .75, distance: .4 + random() * .7, radius: r });
  }
  for (let i = 0; i < 22; i++) {
    const r = .025 + random() * .04;
    const origin = v3(-1.5 + random() * .9, .22, 1.6 + random() * .5);
    spray.setColorAt(i + 66, new THREE.Color(palette.foam));
    droplets.push({ origin, phase: random(), speed: .65 + random() * .3, height: .25 + random() * .65, distance: .8, radius: r });
  }
  function animate(t) {
    droplets.forEach((d, i) => {
      const life = (t * d.speed + d.phase) % 1;
      transform.position.set(d.origin.x - life * .45, d.origin.y + Math.sin(life * Math.PI) * d.height - life * .3, d.origin.z + life * d.distance);
      const s = d.radius * Math.pow(Math.sin(life * Math.PI), .6);
      transform.scale.set(s, s * (1.3 - life * .5), s);
      transform.updateMatrix();
      spray.setMatrixAt(i, transform.matrix);
    });
    spray.instanceMatrix.needsUpdate = true;
  }
  animate(0);
  return { group, animate };
}

if (renderer) start();
