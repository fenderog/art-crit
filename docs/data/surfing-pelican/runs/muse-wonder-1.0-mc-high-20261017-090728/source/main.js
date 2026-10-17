import * as THREE from "three";

const canvas = document.getElementById("scene");
const clockEl = document.getElementById("clock");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x8ec9d8, 18, 42);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(0, 3.2, 9.5);

// Sky dome (gradient shader, generated in code)
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(60, 32, 15),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x2a7fb8) }, mid: { value: new THREE.Color(0x8ec9d8) }, bot: { value: new THREE.Color(0xffd9a0) } },
    vertexShader: `varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top,mid,bot; void main(){ float h=normalize(vP).y; vec3 c=h>0.12?mix(mid,top,smoothstep(.12,.65,h)):mix(bot,mid,smoothstep(-.08,.12,h)); gl_FragColor=vec4(c,1.); }`
  })
);
scene.add(sky);

scene.add(new THREE.HemisphereLight(0xbfe6ff, 0x2a6b7a, 1.1));
const sunLight = new THREE.DirectionalLight(0xffe3a3, 2.2);
sunLight.position.set(-6, 9, 4); sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -10; sunLight.shadow.camera.right = 10;
sunLight.shadow.camera.top = 10; sunLight.shadow.camera.bottom = -10;
scene.add(sunLight);
scene.add(new THREE.DirectionalLight(0x7fd4ff, 0.5).translateX(6).translateY(3).translateZ(-4));

// Materials
const M = {
  white: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .65 }),
  cream: new THREE.MeshStandardMaterial({ color: 0xfff6e6, roughness: .7 }),
  grey: new THREE.MeshStandardMaterial({ color: 0xd9e6ea, roughness: .8 }),
  orange: new THREE.MeshStandardMaterial({ color: 0xff8a1e, roughness: .5 }),
  orangeLight: new THREE.MeshStandardMaterial({ color: 0xffb03a, roughness: .55 }),
  black: new THREE.MeshStandardMaterial({ color: 0x16222a, roughness: .4 }),
  board: new THREE.MeshStandardMaterial({ color: 0xffcf4d, roughness: .35 }),
  boardStripe: new THREE.MeshStandardMaterial({ color: 0x0e7c86, roughness: .4 }),
  water: new THREE.MeshStandardMaterial({ color: 0x0e7c9e, roughness: .25, metalness: .05, transparent: true, opacity: .96 }),
  foam: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .9, transparent: true, opacity: .92 }),
  sand: new THREE.MeshStandardMaterial({ color: 0xe8cf9a, roughness: 1 }),
};

function mesh(geo, mat, x=0,y=0,z=0){ const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.castShadow=true; m.receiveShadow=true; return m; }

// Sun disc + clouds
const sun = mesh(new THREE.SphereGeometry(1.1, 24, 24), new THREE.MeshBasicMaterial({ color: 0xffdf7e, fog: false }), -11, 6.5, -22);
sun.castShadow = false; scene.add(sun);
const clouds = new THREE.Group();
function cloud(x,y,z,s){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, transparent:true, opacity:.92 });
  [[0,0,0,1],[1.1,.1,.1,.75],[-1,.05,0,.7],[.4,.35,-.2,.6]].forEach(([a,b,c,r])=>{
    const m = mesh(new THREE.SphereGeometry(r,18,18), mat, a,b,c); m.scale.y=.55; m.castShadow=false; g.add(m);
  });
  g.position.set(x,y,z); g.scale.setScalar(s); clouds.add(g);
}
cloud(-8,6.2,-14,1.2); cloud(6,7,-16,1.5); cloud(11,5,-10,.9); cloud(-13,5,-9,1); scene.add(clouds);

// Ocean — animated vertices
const oceanGeo = new THREE.PlaneGeometry(60, 34, 96, 48);
oceanGeo.rotateX(-Math.PI/2);
const oceanBase = oceanGeo.attributes.position.array.slice();
const ocean = new THREE.Mesh(oceanGeo, M.water);
ocean.position.y = -0.55; ocean.receiveShadow = true; scene.add(ocean);

// Curling wave behind rider (torus arc + lip)
const waveGroup = new THREE.Group();
const waveBody = mesh(new THREE.CylinderGeometry(2.6, 2.6, 11, 32, 1, true, Math.PI*0.15, Math.PI*0.95),
  new THREE.MeshStandardMaterial({ color: 0x1190b5, roughness:.2, transparent:true, opacity:.92, side:THREE.DoubleSide }), 0,0,0);
waveBody.rotation.z = Math.PI/2; waveBody.rotation.y = Math.PI/2;
const waveLip = mesh(new THREE.TorusGeometry(2.55, .28, 12, 40, Math.PI*.9), M.foam, 0,0,0);
waveLip.rotation.z = Math.PI*.05; waveLip.rotation.y = Math.PI/2;
waveGroup.add(waveBody, waveLip);
waveGroup.position.set(0, 0.2, -3.2); waveGroup.rotation.y = -0.12;
scene.add(waveGroup);

// Foam trail blobs
const foams = [];
for(let i=0;i<26;i++){
  const f = mesh(new THREE.SphereGeometry(0.12+Math.random()*0.22, 10, 10), M.foam, (Math.random()-.5)*3, -0.28, -1+Math.random()*3);
  f.scale.y = .35; f.castShadow=false; foams.push(f); scene.add(f);
}

// Distant islands + buoys
[[-13,-14,2.2],[13,-15,2.8]].forEach(([x,z,s])=>{
  const isl = mesh(new THREE.ConeGeometry(s, s*.7, 7), new THREE.MeshStandardMaterial({color:0x5a9a6a, roughness:1}), x, -0.1, z);
  isl.castShadow=false; scene.add(isl);
});
const buoy = mesh(new THREE.CylinderGeometry(.18,.22,.5,12), new THREE.MeshStandardMaterial({color:0xff4444}), 4.5,-0.2,-2);
scene.add(buoy);

// ---- Surfboard ----
function makeBoard(){
  const shape = new THREE.Shape();
  shape.moveTo(0, 1.55); shape.bezierCurveTo(.42,1.1,.48,.2,.42,-1.1); shape.bezierCurveTo(.38,-1.45,.18,-1.6,0,-1.6);
  shape.bezierCurveTo(-.18,-1.6,-.38,-1.45,-.42,-1.1); shape.bezierCurveTo(-.48,.2,-.42,1.1,0,1.55);
  const geo = new THREE.ExtrudeGeometry(shape, { depth:.09, bevelEnabled:true, bevelThickness:.04, bevelSize:.04, bevelSegments:2, steps:1 });
  geo.rotateX(-Math.PI/2);
  const g = new THREE.Group();
  const base = new THREE.Mesh(geo, M.board); base.castShadow=true; g.add(base);
  const stripe = mesh(new THREE.BoxGeometry(.14,.03,2.5), M.boardStripe, 0,.08,0); g.add(stripe);
  const fin = mesh(new THREE.BoxGeometry(.04,.28,.32), M.boardStripe, 0,-.16,-1.05); fin.rotation.x=.3; g.add(fin);
  g.scale.set(1,1,1.15); return g;
}

// ---- Pelican ----
function makePelican(){
  const g = new THREE.Group();
  // body
  const body = mesh(new THREE.SphereGeometry(.72, 28, 22), M.white, 0, .72, 0); body.scale.set(.92, .78, 1.25); g.add(body);
  const belly = mesh(new THREE.SphereGeometry(.6, 24, 18), M.cream, 0, .62, .18); belly.scale.set(.85,.65,1.05); g.add(belly);
  const tail = mesh(new THREE.ConeGeometry(.32, .9, 12), M.grey, 0, .78, -1.05); tail.rotation.x = Math.PI/2.3; tail.scale.set(1.4,.6,1); g.add(tail);

  // neck as S-curve tube
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0,.85,.75), new THREE.Vector3(0,1.05,1.05), new THREE.Vector3(0,1.55,1.02), new THREE.Vector3(0,1.78,1.22)
  ]);
  g.add(mesh(new THREE.TubeGeometry(curve, 20, .19, 12), M.white));
  // head
  const head = new THREE.Group(); head.position.set(0,1.86,1.28);
  head.add(mesh(new THREE.SphereGeometry(.34,24,20), M.white, 0,0,0));
  const crest = mesh(new THREE.ConeGeometry(.14,.38,10), M.grey, -.02,.28,-.12); crest.rotation.x=-.5; head.add(crest);
  // beak: long upper + pouch
  const beak = mesh(new THREE.ConeGeometry(.13, 1.15, 12), M.orange, 0,-.04,.72); beak.rotation.x = Math.PI/2; beak.scale.set(.75,1,1); head.add(beak);
  const pouch = mesh(new THREE.SphereGeometry(.28,18,14), M.orangeLight, 0,-.22,.48); pouch.scale.set(.7,.65,1.6); head.add(pouch);
  // eyes
  [-1,1].forEach(s=>{ head.add(mesh(new THREE.SphereGeometry(.055,10,10), M.black, s*.22,.09,.24)); });
  // tiny sunglasses for character (two discs + bar) — sits still, part of bird
  [-1,1].forEach(s=>{ const lens = mesh(new THREE.CylinderGeometry(.11,.11,.03,16), M.black, s*.16,.1,.3); lens.rotation.x=Math.PI/2; head.add(lens); });
  g.add(head); g.userData.head = head;

  // wings
  function wing(side){
    const pivot = new THREE.Group(); pivot.position.set(side*.55, 1.05, .05);
    const w = mesh(new THREE.SphereGeometry(.75,20,14), M.white, side*.62,0,-.1); w.scale.set(1.15,.18,1.55);
    const tip = mesh(new THREE.SphereGeometry(.45,16,12), M.grey, side*1.25,-.02,-.55); tip.scale.set(1,.14,1.3);
    pivot.add(w, tip); g.add(pivot); return pivot;
  }
  g.userData.wingL = wing(-1); g.userData.wingR = wing(1);

  // legs + webbed feet on board
  [-1,1].forEach(s=>{
    const leg = mesh(new THREE.CylinderGeometry(.05,.05,.42,8), M.orange, s*.24,.28,.08); g.add(leg);
    const foot = mesh(new THREE.SphereGeometry(.16,12,10), M.orange, s*.24,.06,.16); foot.scale.set(1,.35,1.5); g.add(foot);
  });
  return g;
}

const rider = new THREE.Group();
const board = makeBoard(); board.position.y = 0.02;
const pelican = makePelican();
rider.add(board, pelican); scene.add(rider);

// Spray particles
const SPRAY = 220;
const sprayPos = new Float32Array(SPRAY*3), sprayVel = [];
for(let i=0;i<SPRAY;i++){ sprayPos.set([(Math.random()-.5)*.6, .1, -1.2], i*3); sprayVel.push(new THREE.Vector3((Math.random()-.5)*1.2, 1+Math.random()*2, -1-Math.random()*2)); }
const sprayGeo = new THREE.BufferGeometry(); sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos,3));
const spray = new THREE.Points(sprayGeo, new THREE.PointsMaterial({ color:0xffffff, size:.09, transparent:true, opacity:.85 }));
scene.add(spray);

// resize
function resize(){ const w=innerWidth,h=innerHeight; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); }
addEventListener("resize", resize); resize();

const clock = new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // ocean waves
  const pos = oceanGeo.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x = oceanBase[i*3], z = oceanBase[i*3+2];
    pos.setY(i, Math.sin(x*.55 + t*1.6)*.14 + Math.cos(z*.7 + t*1.2)*.12 + Math.sin((x+z)*.3 + t)*.06);
  }
  pos.needsUpdate = true; oceanGeo.computeVertexNormals();

  // rider rides: bob, carve side-to-side, pitch/roll with swell
  const carve = Math.sin(t*.55);
  rider.position.set(carve*1.15, .32 + Math.sin(t*1.7)*.18 + Math.sin(t*2.9)*.05, Math.sin(t*.35)*.25);
  rider.rotation.set(Math.sin(t*1.7+.4)*.08 - .04, carve*-.28, Math.sin(t*1.35)*.13 + carve*.08);
  board.rotation.y = carve*.12;

  // pelican life: wings balance-flap, head scans, body lean, pouch sway
  pelican.position.y = Math.abs(Math.sin(t*2.2))*.04;
  pelican.rotation.z = Math.sin(t*1.35)*.05;
  pelican.userData.wingL.rotation.z =  .55 + Math.sin(t*2.4)*.45;
  pelican.userData.wingR.rotation.z = -.55 - Math.sin(t*2.4+ .3)*.45;
  pelican.userData.wingL.rotation.y = Math.sin(t*1.1)*.12;
  pelican.userData.wingR.rotation.y = -Math.sin(t*1.1)*.12;
  pelican.userData.head.rotation.y = Math.sin(t*.7)*.38;
  pelican.userData.head.rotation.z = Math.sin(t*1.9)*.06;
  pelican.userData.head.position.y = 1.86 + Math.sin(t*2.2)*.03;

  // wave breathes, foam pulses, clouds drift, buoy bobs
  waveGroup.scale.y = 1 + Math.sin(t*1.4)*.045;
  waveGroup.position.y = .2 + Math.sin(t*1.7)*.08;
  foams.forEach((f,i)=>{ f.position.x = rider.position.x + Math.sin(i*2.1+t*2)*.7; f.position.z = -0.6 - (i%7)*.28 + Math.sin(t+i)*.08; f.material.opacity=.7+Math.sin(t*3+i)*.2; });
  clouds.children.forEach((c,i)=>{ c.position.x += Math.sin(t*.05+i)*.0015 + .004; if(c.position.x>16) c.position.x=-16; });
  buoy.position.y = -.2 + Math.sin(t*1.8+1)*.12; buoy.rotation.z = Math.sin(t*1.5)*.15;
  sun.position.x = -11 + Math.sin(t*.05)*.3;

  // spray recycles at board tail
  const p = sprayGeo.attributes.position.array;
  for(let i=0;i<SPRAY;i++){
    p[i*3]+= sprayVel[i].x*.016; p[i*3+1]+= sprayVel[i].y*.016; p[i*3+2]+= sprayVel[i].z*.016;
    sprayVel[i].y -= .055;
    if(p[i*3+1] < -.35){ p[i*3]= rider.position.x+(Math.random()-.5)*.5; p[i*3+1]=.15; p[i*3+2]= rider.position.z-1.0; sprayVel[i].set((Math.random()-.5)*1.4, 1.2+Math.random()*2.2, -1-Math.random()*1.8); }
  }
  sprayGeo.attributes.position.needsUpdate = true;

  // gentle non-interactive camera sway
  camera.position.x = Math.sin(t*.22)*.7;
  camera.position.y = 3.2 + Math.sin(t*.4)*.18;
  camera.lookAt(rider.position.x*.55, 1.05, 0);

  if(clockEl) clockEl.textContent = `${String(Math.floor(t/60)).padStart(2,"0")}:${String(Math.floor(t%60)).padStart(2,"0")}`;
  renderer.render(scene, camera);
}
animate();
