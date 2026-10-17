import * as THREE from "three";

// Non-interactive animated scene: a procedural pelican surfing a curling wave.
const canvas = document.getElementById("scene");
const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
const TIME_SCALE = reduced ? 0.12 : 1;

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xbfeaf2, 28, 72);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);
camera.position.set(0, 4.2, 15);

// Sky dome (gradient shader, generated in code — no assets)
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(90, 24, 16),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x3aa7d6) }, mid: { value: new THREE.Color(0x9fdcf0) }, bot: { value: new THREE.Color(0xfff2cf) } },
    vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top,mid,bot;
      void main(){ float h=normalize(vP).y; vec3 c=h>0.12?mix(mid,top,smoothstep(.12,.75,h)):mix(bot,mid,smoothstep(-.25,.12,h)); gl_FragColor=vec4(c,1.); }`,
  })
);
scene.add(sky);

// Lights
scene.add(new THREE.HemisphereLight(0xdff6ff, 0x1b6f7d, 1.15));
const sun = new THREE.DirectionalLight(0xfff1c4, 2.4);
sun.position.set(-9, 13, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -18; sun.shadow.camera.right = 18;
sun.shadow.camera.top = 14; sun.shadow.camera.bottom = -8;
sun.shadow.camera.far = 45; sun.shadow.bias = -0.0004;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x9fdcff, 0.55);
fill.position.set(8, 4, 10); scene.add(fill);

// Sun disc + clouds
const sunDisc = new THREE.Mesh(new THREE.CircleGeometry(3.2, 32),
  new THREE.MeshBasicMaterial({ color: 0xffdf8a, fog: false }));
sunDisc.position.set(-24, 16, -42); scene.add(sunDisc);
const halo = new THREE.Mesh(new THREE.CircleGeometry(5.2, 32),
  new THREE.MeshBasicMaterial({ color: 0xffeaa8, transparent: true, opacity: 0.35, fog: false }));
halo.position.copy(sunDisc.position).z -= 0.1; scene.add(halo);

const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
function makeCloud(x, y, z, s) {
  const g = new THREE.Group();
  [[0,0,0,1.5],[1.6,-0.2,0,1.1],[-1.5,-0.25,0,1.05],[0.5,0.45,-0.3,1.0]].forEach(([a,b,c,r]) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), cloudMat);
    m.position.set(a,b,c); m.scale.y = 0.55; g.add(m);
  });
  g.position.set(x,y,z); g.scale.setScalar(s); scene.add(g); return g;
}
const clouds = [makeCloud(-15,10,-26,1.4), makeCloud(13,12,-30,1.8), makeCloud(22,8,-22,1), makeCloud(-24,7,-20,0.9)];

// ----- The curling wave: custom strip, profile v goes trough -> face -> lip
function waveProfile(x, v, t, out) {
  const crest = Math.sin(x * 0.22 + 0.6) * 0.35;
  let y = -0.7 + Math.pow(v, 1.25) * (5.1 + crest);
  let z = 3.4 - Math.pow(v, 1.15) * 4.6;
  if (v > 0.68) { // curl the lip over the face
    const a = ((v - 0.68) / 0.32) * Math.PI * 0.95;
    const r = 1.45 + Math.sin(t * 0.9 + x * 0.3) * 0.08;
    y += Math.sin(a) * r * 0.55;
    z += (1 - Math.cos(a)) * r;
  }
  y += Math.sin(x * 0.85 - t * 2.2) * 0.09 * v + Math.sin(x * 0.3 + t * 1.1) * 0.07 * v;
  z += Math.sin(x * 0.6 - t * 1.6) * 0.06 * v;
  out.set(x, y, z); return out;
}
const WSEG_X = 72, WSEG_V = 28, WAVE_W = 34;
const waveGeo = new THREE.BufferGeometry();
{
  const pos = new Float32Array((WSEG_X+1)*(WSEG_V+1)*3);
  const idx = [];
  for (let i=0;i<WSEG_X;i++) for (let j=0;j<WSEG_V;j++) {
    const a=i*(WSEG_V+1)+j, b=a+WSEG_V+1; idx.push(a,b,a+1, b,b+1,a+1);
  }
  waveGeo.setAttribute("position", new THREE.BufferAttribute(pos,3));
  waveGeo.setIndex(idx);
}
const wave = new THREE.Mesh(waveGeo, new THREE.MeshStandardMaterial({
  color: 0x0e94b4, roughness: 0.32, metalness: 0.05, side: THREE.DoubleSide,
}));
wave.receiveShadow = true; scene.add(wave);

// White foam cap following the lip (v near 1)
const foamGeo = new THREE.BufferGeometry();
{
  const pos = new Float32Array((WSEG_X+1)*2*3); const idx=[];
  for (let i=0;i<WSEG_X;i++){ const a=i*2; idx.push(a,a+2,a+1, a+2,a+3,a+1); }
  foamGeo.setAttribute("position", new THREE.BufferAttribute(pos,3)); foamGeo.setIndex(idx);
}
const foamCap = new THREE.Mesh(foamGeo, new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, side: THREE.DoubleSide }));
scene.add(foamCap);

// Open ocean in front / below
const oceanGeo = new THREE.PlaneGeometry(90, 46, 56, 28);
oceanGeo.rotateX(-Math.PI/2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshStandardMaterial({ color: 0x0b7d9e, roughness: 0.38, metalness: 0.05 }));
ocean.position.set(0, -0.72, 10); ocean.receiveShadow = true; scene.add(ocean);

// ----- Surfboard (extruded outline)
function boardGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0, 1.65);
  s.bezierCurveTo(0.42, 1.1, 0.46, 0.2, 0.42, -0.9);
  s.bezierCurveTo(0.38, -1.45, 0.2, -1.65, 0, -1.65);
  s.bezierCurveTo(-0.2, -1.65, -0.38, -1.45, -0.42, -0.9);
  s.bezierCurveTo(-0.46, 0.2, -0.42, 1.1, 0, 1.65);
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 24 });
  g.rotateX(Math.PI/2); return g; // length lies along Z, thickness along Y
}
// ----- Pelican, built from primitives
const M = {
  white: new THREE.MeshStandardMaterial({ color: 0xfdfaf2, roughness: 0.75 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xf3e7c8, roughness: 0.85 }),
  dark:  new THREE.MeshStandardMaterial({ color: 0x2b2b30, roughness: 0.7 }),
  beak:  new THREE.MeshStandardMaterial({ color: 0xf59a23, roughness: 0.5 }),
  pouch: new THREE.MeshStandardMaterial({ color: 0xf7b733, roughness: 0.65 }),
  leg:   new THREE.MeshStandardMaterial({ color: 0xe8762a, roughness: 0.6 }),
  eye:   new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.25 }),
};
function ball(mat, sx, sy, sz, x=0,y=0,z=0) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), mat);
  m.scale.set(sx,sy,sz); m.position.set(x,y,z); m.castShadow = true; return m;
}
function makeWing(side) { // side: +1 left(+X), -1 right
  const shoulder = new THREE.Group();
  const inner = ball(M.white, 0.95, 0.13, 0.42, side*0.85, 0, -0.05);
  inner.rotation.z = side * 0.08; shoulder.add(inner);
  const elbow = new THREE.Group(); elbow.position.set(side*1.7, 0, -0.05); shoulder.add(elbow);
  const outer = ball(M.white, 0.8, 0.1, 0.34, side*0.7, 0, -0.12); elbow.add(outer);
  const tip = ball(M.dark, 0.55, 0.08, 0.26, side*1.45, 0, -0.22); elbow.add(tip); // black flight feathers
  return { shoulder, elbow };
}
function makeLeg(x) {
  const g = new THREE.Group(); g.position.set(x, 0, 0);
  const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.045, 0.62, 10), M.leg);
  leg.position.y = -0.31; leg.castShadow = true; g.add(leg);
  const foot = ball(M.leg, 0.16, 0.035, 0.3, 0, -0.63, 0.1); g.add(foot); // webbed foot, flat on board
  return g;
}
function buildPelican() {
  const root = new THREE.Group();           // origin at the feet / board top
  const body = new THREE.Group(); body.position.y = 1.05; root.add(body);
  body.add(ball(M.white, 0.62, 0.58, 0.95, 0, 0.1, -0.05));          // torso, long axis Z (facing +Z)
  body.add(ball(M.cream, 0.5, 0.42, 0.6, 0, -0.08, 0.28));           // chest
  const tail = ball(M.white, 0.42, 0.09, 0.55, 0, 0.18, -1.05); tail.rotation.x = -0.35; body.add(tail);
  const tailTip = ball(M.dark, 0.36, 0.07, 0.22, 0, 0.28, -1.38); tailTip.rotation.x = -0.35; body.add(tailTip);

  const L = makeWing(1), R = makeWing(-1);
  L.shoulder.position.set(0.4, 0.38, 0.05); R.shoulder.position.set(-0.4, 0.38, 0.05);
  body.add(L.shoulder, R.shoulder);

  // S-curved neck: tube along a curve, then head group at its end
  const neckCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0.25, 0.72), new THREE.Vector3(0, 0.62, 0.55),
    new THREE.Vector3(0, 0.88, 0.72), new THREE.Vector3(0, 1.05, 0.98),
  ]);
  const neck = new THREE.Mesh(new THREE.TubeGeometry(neckCurve, 20, 0.21, 12), M.white);
  neck.castShadow = true; body.add(neck);

  const head = new THREE.Group(); head.position.set(0, 1.08, 1.0); body.add(head);
  head.add(ball(M.white, 0.34, 0.32, 0.42, 0, 0.08, 0.1));
  for (let i=-1;i<=1;i++) { // shaggy crest
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.34, 8), M.cream);
    c.position.set(i*0.11, 0.38, -0.12); c.rotation.x = -0.7; c.rotation.z = i*0.25; c.castShadow = true; head.add(c);
  }
  // Long orange beak (tapered, flattened) + sagging pouch underneath
  const beak = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.13, 1.55, 10), M.beak);
  beak.scale.x = 0.55; beak.rotation.x = Math.PI/2 - 0.12; beak.position.set(0, 0.02, 1.05); beak.castShadow = true; head.add(beak);
  const pouch = ball(M.pouch, 0.17, 0.3, 0.62, 0, -0.28, 0.78); head.add(pouch);
  [-1,1].forEach(s => {
    head.add(ball(M.eye, 0.055, 0.055, 0.055, s*0.24, 0.18, 0.34));
    head.add(ball(M.white, 0.02, 0.02, 0.02, s*0.26, 0.21, 0.38));
  });
  const legL = makeLeg(0.45), legR = makeLeg(-0.45);
  legL.position.y = legR.position.y = 0.66; legL.position.z = legR.position.z = 0; // feet spread along board once yawed
  root.add(legL, legR);
  return { root, body, head, pouch, tail, wingL: L, wingR: R };
}

const rider = new THREE.Group(); scene.add(rider); // board + pelican, moved along wave face
const board = new THREE.Mesh(boardGeometry(), new THREE.MeshStandardMaterial({ color: 0xffd23f, roughness: 0.35 }));
board.castShadow = true; board.receiveShadow = true; rider.add(board);
const stripe = new THREE.Mesh(boardGeometry(), new THREE.MeshStandardMaterial({ color: 0xe94f37, roughness: 0.4 }));
stripe.scale.set(0.38, 0.4, 0.97); stripe.position.y = 0.045; rider.add(stripe);
const fin = ball(new THREE.MeshStandardMaterial({ color: 0xe94f37, roughness: 0.4 }), 0.03, 0.22, 0.28, 0, -0.18, -1.2);
rider.add(fin);
const pelican = buildPelican(); pelican.root.position.y = 0.08;
pelican.root.rotation.y = -Math.PI/2; // sideways surfing stance: chest out of the wave face, wings along the board
const stance = new THREE.Group(); stance.add(pelican.root); rider.add(stance); // tilted toward gravity-up each frame

// ----- Spray behind the board + foam falling off the lip
function makePoints(n, size, opacity) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n*3), 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xffffff, size, transparent: true, opacity, depthWrite: false }));
  pts.frustumCulled = false; scene.add(pts); return pts;
}
const SPRAY_N = 280, spray = makePoints(SPRAY_N, 0.14, 0.85);
const sprayVel = new Float32Array(SPRAY_N*3), sprayAge = new Float32Array(SPRAY_N).map(()=>Math.random());
const FOAM_N = 240, foamPts = makePoints(FOAM_N, 0.2, 0.9);
const foamAge = new Float32Array(FOAM_N).map(()=>Math.random());
const foamX = new Float32Array(FOAM_N).map(()=>(Math.random()*2-1)*15);

// Distant gulls: two flapping triangles each
const gulls = [];
for (let i=0;i<4;i++) {
  const g = new THREE.Group(), mat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
  [-1,1].forEach(s => {
    const w = new THREE.Mesh(new THREE.BufferGeometry(), mat);
    w.geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array([0,0,0, s*0.7,0.12,-0.15, s*0.7,0.12,0.18]),3));
    w.geometry.computeVertexNormals(); w.userData.side = s; g.add(w);
  });
  g.userData = { phase: i*1.7, r: 16+i*3, h: 8.5+i*0.9, speed: 0.05+i*0.012 };
  scene.add(g); gulls.push(g);
}

// ----- Surf path: carve back and forth across the wave face forever
const _p = new THREE.Vector3(), _p2 = new THREE.Vector3(), _tan = new THREE.Vector3();
function surfPoint(t, out, outNormal) {
  const x = Math.sin(t*0.30) * 6.8;
  const v = 0.50 + Math.sin(t*0.60 + 1.2) * 0.15; // climb and drop on the face
  waveProfile(x, v, t, out);
  waveProfile(x, v+0.03, t, _p2); _tan.subVectors(_p2, out).normalize();
  outNormal.set(0, -_tan.z, _tan.y).normalize();
  out.addScaledVector(outNormal, 0.14);
  return { x, v };
}
const _pos = new THREE.Vector3(), _next = new THREE.Vector3(), _n = new THREE.Vector3(), _n2 = new THREE.Vector3();
const _fwd = new THREE.Vector3(), _side = new THREE.Vector3(), _up = new THREE.Vector3(), _m = new THREE.Matrix4();
const camTarget = new THREE.Vector3(0, 2, 0);

function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false); camera.aspect = w/h; camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize); resize();

const clock = new THREE.Clock();
let t = 0;
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05) * TIME_SCALE;
  t += dt;

  // Wave + foam cap vertices
  const wp = waveGeo.attributes.position.array;
  for (let i=0;i<=WSEG_X;i++) for (let j=0;j<=WSEG_V;j++) {
    waveProfile(-WAVE_W/2 + (i/WSEG_X)*WAVE_W, j/WSEG_V, t, _p);
    const k=(i*(WSEG_V+1)+j)*3; wp[k]=_p.x; wp[k+1]=_p.y; wp[k+2]=_p.z;
  }
  waveGeo.attributes.position.needsUpdate = true; waveGeo.computeVertexNormals();
  const fp = foamGeo.attributes.position.array;
  for (let i=0;i<=WSEG_X;i++) {
    const x=-WAVE_W/2+(i/WSEG_X)*WAVE_W;
    waveProfile(x, 0.93, t, _p); fp[i*6]=_p.x; fp[i*6+1]=_p.y+0.04; fp[i*6+2]=_p.z+0.04;
    waveProfile(x, 1.0, t, _p);  fp[i*6+3]=_p.x; fp[i*6+4]=_p.y+0.04; fp[i*6+5]=_p.z+0.04;
  }
  foamGeo.attributes.position.needsUpdate = true; foamGeo.computeVertexNormals();

  // Ocean chop
  const op = oceanGeo.attributes.position.array;
  for (let i=0;i<op.length;i+=3) {
    const x=oceanBase[i], z=oceanBase[i+2];
    op[i+1] = Math.sin(x*0.35+t*1.4)*0.14 + Math.cos(z*0.45+t*1.1)*0.12 + Math.sin((x+z)*0.22-t*0.8)*0.08;
  }
  oceanGeo.attributes.position.needsUpdate = true; oceanGeo.computeVertexNormals();

  // Rider follows the face, board aligned to travel direction + face normal
  surfPoint(t, _pos, _n); surfPoint(t+0.08, _next, _n2);
  rider.position.copy(_pos);
  _fwd.subVectors(_next,_pos); if (_fwd.lengthSq()<1e-6) _fwd.set(1,0,0); _fwd.normalize();
  _side.crossVectors(_n,_fwd).normalize(); _up.crossVectors(_fwd,_side);
  _m.makeBasis(_side,_up,_fwd); rider.quaternion.setFromRotationMatrix(_m);
  stance.rotation.z = -Math.atan2(_side.y, _n.y) * 0.82; // body mostly upright vs gravity, board stays on the face

  // Pelican performance: lean into carves, balance with wings, bob head, sway pouch
  const turn = Math.cos(t*0.30); // + at one end of the carve, - at the other
  const climb = Math.cos(t*0.60+1.2);
  pelican.body.rotation.z = turn * 0.16;
  pelican.body.rotation.x = -0.08 + climb * 0.08 + Math.sin(t*2.1)*0.02;
  pelican.body.position.y = 1.05 + Math.sin(t*2.1)*0.045; // knees pumping
  pelican.wingL.shoulder.rotation.z =  0.22 + Math.sin(t*1.7)*0.16 + turn*0.14;
  pelican.wingR.shoulder.rotation.z = -0.22 - Math.sin(t*1.7+0.9)*0.16 + turn*0.14;
  pelican.wingL.elbow.rotation.z =  0.18 + Math.sin(t*1.7-0.5)*0.2;
  pelican.wingR.elbow.rotation.z = -0.18 - Math.sin(t*1.7+0.4)*0.2;
  pelican.wingL.shoulder.rotation.x = pelican.wingR.shoulder.rotation.x = Math.sin(t*0.9)*0.06;
  pelican.head.rotation.y = Math.sin(t*0.45)*0.3;
  pelican.head.rotation.x = Math.sin(t*2.1+0.6)*0.07;
  pelican.pouch.scale.set(0.17, 0.3+Math.sin(t*2.6)*0.035, 0.62);
  pelican.pouch.position.x = Math.sin(t*1.3)*0.04;
  pelican.tail.rotation.y = Math.sin(t*1.9)*0.18;

  // Spray: recycle particles kicked up at the board's tail
  const sp = spray.geometry.attributes.position.array;
  const tailPos = _p.copy(_pos).addScaledVector(_fwd,-1.5);
  for (let i=0;i<SPRAY_N;i++) {
    sprayAge[i]+=dt*1.4;
    if (sprayAge[i]>=1) {
      sprayAge[i]=0; sp[i*3]=tailPos.x; sp[i*3+1]=tailPos.y+0.1; sp[i*3+2]=tailPos.z;
      sprayVel[i*3]=-_fwd.x*1.6+(Math.random()-0.5)*1.4;
      sprayVel[i*3+1]=1.4+Math.random()*1.8;
      sprayVel[i*3+2]=-_fwd.z*1.6+(Math.random()-0.5)*1.4+0.7;
    }
    sprayVel[i*3+1]-=4.5*dt;
    sp[i*3]+=sprayVel[i*3]*dt; sp[i*3+1]+=sprayVel[i*3+1]*dt; sp[i*3+2]+=sprayVel[i*3+2]*dt;
  }
  spray.geometry.attributes.position.needsUpdate = true;

  // Foam shedding off the lip and sliding down the face
  const fpp = foamPts.geometry.attributes.position.array;
  for (let i=0;i<FOAM_N;i++) {
    foamAge[i]+=dt*0.55; if (foamAge[i]>=1){ foamAge[i]=0; foamX[i]=(Math.random()*2-1)*15; }
    waveProfile(foamX[i], 1.0-foamAge[i]*0.45, t, _p);
    fpp[i*3]=_p.x; fpp[i*3+1]=_p.y+0.12; fpp[i*3+2]=_p.z+0.12;
  }
  foamPts.geometry.attributes.position.needsUpdate = true;

  clouds.forEach((c,i)=>{ c.position.x += dt*(0.25+i*0.07); if (c.position.x>34) c.position.x=-34; });
  gulls.forEach(g=>{
    const u=g.userData, a=t*u.speed*Math.PI*2+u.phase;
    g.position.set(Math.cos(a)*u.r, u.h+Math.sin(t*0.7+u.phase)*0.5, -14+Math.sin(a)*5);
    g.rotation.y = -a; g.children.forEach(w=>{ w.rotation.x = Math.sin(t*6+u.phase)*0.45*w.userData.side; });
  });

  // Slow cinematic sway; gaze tracks the pelican (no controls anywhere)
  camTarget.lerp(_p.set(_pos.x*0.55, _pos.y+1.4, _pos.z), 0.04);
  camera.position.set(Math.sin(t*0.07)*2.2, 4.3+Math.sin(t*0.11)*0.5, 14.5+Math.sin(t*0.05)*0.8);
  camera.lookAt(camTarget);
  renderer.render(scene, camera);
}
animate();


