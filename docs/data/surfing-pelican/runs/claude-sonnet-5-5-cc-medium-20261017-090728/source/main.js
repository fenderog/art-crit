import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 400);

// sky
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false,
  vertexShader: "varying vec3 p;void main(){p=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}",
  fragmentShader: `varying vec3 p;void main(){float h=normalize(p).y;
    vec3 hor=vec3(1.,.82,.62),top=vec3(.25,.55,.9);
    vec3 c=mix(hor,top,pow(clamp(h,0.,1.),.5));
    vec3 s=normalize(vec3(-.5,.25,-.8));float d=max(dot(normalize(p),s),0.);
    c+=vec3(1.,.8,.5)*pow(d,40.)*.6+vec3(1.,.95,.8)*pow(d,600.);
    gl_FragColor=vec4(c,1.);}`
});
scene.add(new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), skyMat));
scene.fog = new THREE.Fog(0xf0c9a0, 40, 220);
scene.add(new THREE.HemisphereLight(0xcfe6ff, 0x2a6a7a, 1.1));
const sun = new THREE.DirectionalLight(0xffe2b0, 2.6);
sun.position.set(-50, 25, -80); scene.add(sun);

// ocean: swell frame moves with the surfer
const SW = 1.9, SK = 0.22;
function swell(z) { // asymmetric face; steep side toward +z (travel direction)
  const a = z * SK; return SW * (Math.sin(a) + 0.35 * Math.sin(2 * a + 1.0)) ;
}
function swellD(z) { return SW * SK * (Math.cos(z * SK) + 0.7 * Math.cos(2 * z * SK + 1.0)); }
function height(x, z, t) {
  return swell(z) + 0.18 * Math.sin(x * 0.9 + z * 0.5 - t * 1.6) + 0.12 * Math.sin(x * 1.7 - z * 1.1 + t * 2.1)
    + 0.5 * Math.sin(x * 0.18 + t * 0.4) * Math.sin(z * 0.1);
}
const geo = new THREE.PlaneGeometry(240, 240, 240, 240);
geo.rotateX(-Math.PI / 2);
const pos = geo.attributes.position;
const ocean = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
  color: 0x167f93, roughness: 0.25, metalness: 0.1, flatShading: false }));
ocean.material.onBeforeCompile = s => { // foam on crests by height
  s.vertexShader = s.vertexShader.replace("#include <common>", "#include <common>\nvarying float vH;")
    .replace("#include <begin_vertex>", "#include <begin_vertex>\nvH=position.y;");
  s.fragmentShader = s.fragmentShader.replace("#include <common>", "#include <common>\nvarying float vH;")
    .replace("#include <color_fragment>", `#include <color_fragment>
      float f=smoothstep(1.6,2.6,vH);
      diffuseColor.rgb=mix(diffuseColor.rgb*mix(.55,1.3,smoothstep(-2.,1.5,vH)),vec3(.95,1.,1.),f);`);
};
scene.add(ocean);

// spray
const N = 260, sp = new Float32Array(N * 3), sv = [], sl = new Float32Array(N);
for (let i = 0; i < N; i++) { sv.push(new THREE.Vector3()); sl[i] = Math.random(); }
const sg = new THREE.BufferGeometry(); sg.setAttribute("position", new THREE.BufferAttribute(sp, 3));
const spray = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xffffff, size: 0.18, transparent: true, opacity: 0.8, depthWrite: false }));
spray.frustumCulled = false; scene.add(spray);

// surfer rig
const rig = new THREE.Group(); scene.add(rig);
const tilt = new THREE.Group(); rig.add(tilt);
const M = (c, r = 0.6) => new THREE.MeshStandardMaterial({ color: c, roughness: r });
const white = M(0xf6f1e6, 0.8), dark = M(0x2d3036, 0.7), bill = M(0xf0b43c, 0.5), pouch = M(0xe69a6a, 0.6), orange = M(0xf08a2a, 0.6);
function mesh(g, m, p, s, r) { const o = new THREE.Mesh(g, m); o.position.set(...p); if (s) o.scale.set(...s); if (r) o.rotation.set(...r); return o; }
const sph = new THREE.SphereGeometry(1, 32, 24);

// board
const bshape = new THREE.Shape();
bshape.moveTo(0, -1.7); bshape.bezierCurveTo(0.55, -1.2, 0.6, 1.0, 0, 2.3);
bshape.bezierCurveTo(-0.6, 1.0, -0.55, -1.2, 0, -1.7);
const bg = new THREE.ExtrudeGeometry(bshape, { depth: 0.12, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06, bevelSegments: 4, curveSegments: 24 });
bg.rotateX(-Math.PI / 2); bg.translate(0, 0, 0);
const board = new THREE.Mesh(bg, M(0xff5a4a, 0.35)); board.position.y = -0.05; tilt.add(board);
const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.02, 3.6), M(0xfff3d0, 0.4)); stripe.position.set(0, 0.2, 0.3); tilt.add(stripe);
tilt.add(mesh(new THREE.ConeGeometry(0.06, 0.5, 6), dark, [0, -0.3, -1.4], [1, 1, 1], [0, 0, 0]));

// pelican (faces +z)
const bird = new THREE.Group(); bird.position.set(0, 0.55, 0.1); tilt.add(bird);
const body = mesh(sph, white, [0, 0.75, 0], [0.55, 0.5, 0.85], [-0.25, 0, 0]); bird.add(body);
bird.add(mesh(sph, white, [0, 0.9, -0.75], [0.3, 0.2, 0.6], [0.35, 0, 0])); // tail
for (const s of [-1, 1]) {
  bird.add(mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.55, 8), orange, [s * 0.22, 0.28, 0.05], [1, 1, 1], [0, 0, s * 0.15]));
  bird.add(mesh(sph, orange, [s * 0.24, 0.02, 0.18], [0.14, 0.04, 0.3]));
}
const neckPts = [[0, 1.0, 0.5], [0, 1.35, 0.7], [0, 1.75, 0.55], [0, 2.1, 0.55], [0, 2.3, 0.75]].map(a => new THREE.Vector3(...a));
const neckCurve = new THREE.CatmullRomCurve3(neckPts);
bird.add(new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 24, 0.17, 12), white));
const head = new THREE.Group(); head.position.set(0, 2.32, 0.8); bird.add(head);
head.add(mesh(sph, white, [0, 0, 0], [0.24, 0.24, 0.3]));
head.add(mesh(sph, M(0xf5d870), [0, 0.12, -0.12], [0.2, 0.17, 0.22]));
for (const s of [-1, 1]) {
  head.add(mesh(sph, M(0x111111, 0.2), [s * 0.17, 0.06, 0.12], [0.045, 0.045, 0.045]));
  head.add(mesh(sph, M(0xffffff, 0.2), [s * 0.185, 0.075, 0.145], [0.012, 0.012, 0.012]));
}
const upper = mesh(new THREE.ConeGeometry(1, 1, 4), bill, [0, 0.0, 0.85], [0.13, 0.9, 0.06], [Math.PI / 2, Math.PI / 4, 0]);
upper.scale.set(0.2, 1.3, 0.07); head.add(upper);
head.add(mesh(sph, pouch, [0, -0.1, 0.65], [0.13, 0.12, 0.55], [0.05, 0, 0]));
head.add(mesh(sph, bill, [0, 0.0, 1.45], [0.04, 0.04, 0.05]));
// wings
function wing(side) {
  const g = new THREE.Group();
  for (let i = 0; i < 9; i++) {
    const t = i / 8, len = 1.0 + 1.1 * Math.sin(Math.min(t * 1.2 + 0.2, 1) * 1.6);
    const f = mesh(sph, i > 3 ? dark : white, [0, 0, 0], [len / 2, 0.015, 0.2]);
    f.position.set(len / 2 * 0.95, 0, -0.5 + t * 0.9 - 0.45 * 0);
    g.add(f);
  }
  g.add(mesh(sph, white, [0.35, 0.02, 0.0], [0.5, 0.07, 0.5]));
  g.scale.x = side; return g;
}
const wl = wing(-1), wr = wing(1);
for (const w of [wl, wr]) { w.position.set(0, 1.0, 0.1); bird.add(w); }

const spot = new THREE.Vector3();
const clock = new THREE.Clock();
const nrm = new THREE.Vector3();
function update(t) {
  // ocean vertices
  for (let i = 0; i < pos.count; i++) pos.setY(i, height(pos.getX(i), pos.getZ(i), t));
  pos.needsUpdate = true; geo.computeVertexNormals();

  // carving path
  const x = 5 * Math.sin(t * 0.5), z = 1.2 * Math.sin(t * 0.37) - 0.3;
  const dx = 2.5 * Math.cos(t * 0.5), dz = 0.44 * Math.cos(t * 0.37);
  rig.position.set(x, height(x, z, t) + 0.12, z);
  const heading = Math.atan2(dx, 1.4 + dz);
  rig.rotation.set(0, heading, 0);
  const e = 0.5;
  const hx = (height(x + e, z, t) - height(x - e, z, t)) / (2 * e);
  const hz = (height(x, z + e, t) - height(x, z - e, t)) / (2 * e);
  nrm.set(-hx, 1, -hz).normalize();
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), nrm);
  const inv = rig.quaternion.clone().invert();
  tilt.quaternion.copy(inv.multiply(q).multiply(rig.quaternion.clone().identity().copy(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, heading, 0)))));
  tilt.rotation.z += -dx * 0.05 * 0.4; // lean into the turn

  // pelican balance
  const sway = Math.sin(t * 2.3);
  wl.rotation.set(0.1 * sway, 0.1, 0.25 + 0.15 * Math.sin(t * 1.8) + 0.1 * sway);
  wr.rotation.set(-0.1 * sway, -0.1, -(0.25 + 0.15 * Math.sin(t * 1.8 + 1.5) - 0.1 * sway));
  wl.rotation.z *= -1; wr.rotation.z *= -1;
  wl.rotation.z = -(0.2 + 0.2 * Math.sin(t * 1.8)); wr.rotation.z = 0.2 + 0.2 * Math.sin(t * 1.8 + 1.5);
  bird.rotation.set(0.15 + 0.04 * Math.sin(t * 3), 0, 0.05 * sway);
  head.rotation.set(0.15 * Math.sin(t * 1.3) + 0.1, 0.2 * Math.sin(t * 0.9), 0.08 * Math.sin(t * 1.1));

  // spray from board tail
  const tail = new THREE.Vector3(0, 0, -1.4).applyMatrix4(board.matrixWorld);
  for (let i = 0; i < N; i++) {
    sl[i] -= 0.016 * 1.4;
    if (sl[i] <= 0) {
      sl[i] = 0.6 + Math.random() * 0.6;
      const side = Math.random() < 0.5 ? -1 : 1;
      const s = new THREE.Vector3(side * (0.3 + Math.random()), 0, -0.5).applyEuler(new THREE.Euler(0, heading, 0));
      sp[i * 3] = tail.x + s.x * 0.2; sp[i * 3 + 1] = tail.y; sp[i * 3 + 2] = tail.z + s.z * 0.2;
      sv[i].set(s.x * 2, 1.5 + Math.random() * 2, s.z * 2 + (Math.random() - .5));
    }
    sv[i].y -= 0.016 * 7;
    sp[i * 3] += sv[i].x * 0.016; sp[i * 3 + 1] += sv[i].y * 0.016; sp[i * 3 + 2] += sv[i].z * 0.016;
  }
  sg.attributes.position.needsUpdate = true;

  // camera orbit, front-quarter view
  const a = 0.5 + 0.6 * Math.sin(t * 0.15) ;
  const r = 9.5 + Math.sin(t * 0.21) * 1.5;
  const cx = x * 0.6 + Math.sin(a + 0.6) * r, cz = z + Math.cos(a + 0.6) * r;
  camera.position.set(cx, Math.max(height(cx, cz, t) + 1.2, 0) + 1.4 + Math.sin(t * 0.3) * 0.5, cz);
  camera.lookAt(x, rig.position.y + 1.4, z);
}
// avoid camera landing behind: keep in front (+z) of surfer so we see its face
function frame() {
  update(clock.getElapsedTime());
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
board.updateWorldMatrix(true, false);
frame();
addEventListener("resize", () => {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
});
