import * as THREE from "three";
// Renderer / scene / camera
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight); renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x8fd8f2); scene.fog = new THREE.Fog(0x8fd8f2, 25, 70);
const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, .1, 200);
camera.position.set(7,4.2,9); camera.lookAt(0,1.2,0);
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
const sun = new THREE.DirectionalLight(0xfff2cc, 2.4); sun.position.set(8,12,6); sun.castShadow=true; sun.shadow.mapSize.set(2048,2048); scene.add(sun);
scene.add(new THREE.HemisphereLight(0xbfefff, 0x2a7f9e, 1.1));
const mat=(c,r=.6,m=0)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m});
// Ocean: animated plane
const oceanGeo = new THREE.PlaneGeometry(80,40,90,40); oceanGeo.rotateX(-Math.PI/2);
const ocean = new THREE.Mesh(oceanGeo, new THREE.MeshPhysicalMaterial({color:0x1288b8,roughness:.25,transmission:.15,transparent:true,opacity:.95}));
ocean.receiveShadow=true; scene.add(ocean);
const base = oceanGeo.attributes.position.array.slice();
// Wave wall (curling face behind pelican)
const waveGeo = new THREE.CylinderGeometry(4.5,4.5,16,32,1,true,Math.PI*.15,Math.PI*.5);
const wave = new THREE.Mesh(waveGeo, new THREE.MeshPhysicalMaterial({color:0x1fb6d4,roughness:.2,transparent:true,opacity:.85,side:THREE.DoubleSide}));
wave.rotation.set(0,0,Math.PI/2); wave.rotation.y=.25; wave.position.set(-1,1.1,-8); scene.add(wave);
// Foam crest tube
const crest = new THREE.Mesh(new THREE.TorusGeometry(6.5,.55,12,60,Math.PI*.7), mat(0xffffff,.4));
crest.position.set(-4,6.2,-12.5); crest.rotation.set(0,0,.7); scene.add(crest);
// ---- Pelican ----
const pelican = new THREE.Group(); scene.add(pelican);
function mesh(geo,material,x=0,y=0,z=0){const m=new THREE.Mesh(geo,material);m.position.set(x,y,z);m.castShadow=true;return m;}
const white=mat(0xf7f3e8,.7), grey=mat(0xd8d3c3,.7), orange=mat(0xff8c1a,.5), dark=mat(0x222222,.5);
// body: lathe profile
const pts=[]; [[0,0],[.55,.08],[.85,.35],[.95,.75],[.8,1.15],[.45,1.45],[0,1.55]].forEach(p=>pts.push(new THREE.Vector2(p[0],p[1])));
const body=mesh(new THREE.LatheGeometry(pts,32),white,0,0,0); body.rotation.z=-.5; pelican.add(body);
// head + neck
const head=mesh(new THREE.SphereGeometry(.42,24,18),white,.55,1.65,.1); pelican.add(head);
const neck=mesh(new THREE.CylinderGeometry(.18,.28,.7,12),white,.3,1.25,.05); neck.rotation.z=-.4; pelican.add(neck);
// beak + pouch: long upper beak and hanging pouch
const beak=mesh(new THREE.ConeGeometry(.14,1.5,12),orange,1.25,1.62,.1); beak.rotation.z=-Math.PI/2.15; pelican.add(beak);
const pouch=mesh(new THREE.SphereGeometry(.45,18,12),mat(0xffb26b,.6),1.05,1.32,.1); pouch.scale.set(1.4,.6,.7); pelican.add(pouch);
const eye=mesh(new THREE.SphereGeometry(.06,10,8),dark,.78,1.78,.32); pelican.add(eye);
// crest feathers
for(let i=0;i<3;i++){const f=mesh(new THREE.ConeGeometry(.07,.45,8),grey,.25+i*.14,2.02-i*.04,-.05); f.rotation.z=.5; pelican.add(f);}
// wings as flattened extruded shapes, spread for balance
function wing(side){const s=new THREE.Shape(); s.moveTo(0,0); s.quadraticCurveTo(.7,.45,1.6,.35); s.quadraticCurveTo(1.2,-.1,.4,-.15); s.closePath();
 const m=mesh(new THREE.ExtrudeGeometry(s,{depth:.06,bevelEnabled:true,bevelSize:.03,bevelThickness:.02}),grey,0,1.05,side*.28);
 m.rotation.y=side* -.35; return m;}
const wL=wing(-1), wR=wing(1); pelican.add(wL,wR);
// tail
const tail=mesh(new THREE.BoxGeometry(.7,.06,.4),grey,-.75,.95,0); tail.rotation.z=.4; pelican.add(tail);
// webbed feet on board
const feet=new THREE.Group(); [-.18,.18].forEach(z=>{const f=mesh(new THREE.BoxGeometry(.42,.05,.22),orange,.05,.08,z); feet.add(f);}); pelican.add(feet);
// Surfboard
const boardShape=new THREE.Shape(); boardShape.moveTo(-1.6,0); boardShape.quadraticCurveTo(0,.35,1.7,.08); boardShape.quadraticCurveTo(1.85,0,1.7,-.08); boardShape.quadraticCurveTo(0,-.3,-1.6,0);
const board=mesh(new THREE.ExtrudeGeometry(boardShape,{depth:.08,bevelEnabled:true,bevelSize:.03,bevelThickness:.02}),mat(0xff4757,.35),0,0,0);
board.rotation.x=-Math.PI/2; board.position.y=.05; scene.add(board); pelican.attach ? null:null;
pelican.position.y=.35; pelican.rotation.z=-.12;
// Spray particles (soft sprite via canvas texture)
const c=document.createElement('canvas'); c.width=c.height=64; const g=c.getContext('2d'); const grad=g.createRadialGradient(32,32,2,32,32,30); grad.addColorStop(0,'rgba(255,255,255,.95)'); grad.addColorStop(1,'rgba(255,255,255,0)'); g.fillStyle=grad; g.fillRect(0,0,64,64);
const sprayTex=new THREE.CanvasTexture(c);
const N=220, pos=new Float32Array(N*3), vel=[];
for(let i=0;i<N;i++){pos.set([(Math.random()-.5)*3,.1,(Math.random()-.5)*.5],i*3); vel.push(new THREE.Vector3((Math.random()-.5)*1.2,1+Math.random()*2,(Math.random()-.5)*.8));}
const sprayGeo=new THREE.BufferGeometry(); sprayGeo.setAttribute('position',new THREE.BufferAttribute(pos,3));
const spray=new THREE.Points(sprayGeo,new THREE.PointsMaterial({size:.35,map:sprayTex,transparent:true,opacity:.85,depthWrite:false})); scene.add(spray);
// Sun disc + clouds
const sunDisc=mesh(new THREE.SphereGeometry(2,24,18),new THREE.MeshBasicMaterial({color:0xffe98a}),14,11,-18); scene.add(sunDisc);
for(let i=0;i<5;i++){const cl=new THREE.Group(); for(let j=0;j<4;j++){const s=mesh(new THREE.SphereGeometry(.8+Math.random()*.6,12,10),mat(0xffffff,.9),j*1.1-1.6,Math.random()*.3,0); s.castShadow=false; cl.add(s);} cl.position.set(-16+i*8,8+Math.random()*2,-16-Math.random()*6); scene.add(cl);}
// Animation
const clock=new THREE.Clock(); const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
function tick(){requestAnimationFrame(tick); const t=clock.getElapsedTime(), dt=Math.min(clock.getDelta(),.05)||.016; const k=reduced?.15:1;
 // ocean swell
 const p=oceanGeo.attributes.position; for(let i=0;i<p.count;i++){const x=base[i*3],z=base[i*3+2]; p.setY(i, Math.sin(x*.35+t*1.2)*.35+Math.cos(z*.5+t*.9)*.25 + Math.exp(-z*z/8)*.8*Math.sin(t*1.4));} p.needsUpdate=true; oceanGeo.computeVertexNormals();
 // pelican rides the swell, carves and bobs
 pelican.position.y=.5+Math.sin(t*1.4)*.18*k; pelican.rotation.z=-.12+Math.sin(t*1.1)*.18*k; pelican.rotation.y=Math.sin(t*.6)*.25*k;
 board.position.y=pelican.position.y-.45; board.rotation.z=pelican.rotation.z; board.rotation.y=pelican.rotation.y;
 wL.rotation.z=Math.sin(t*3)*.35*k; wR.rotation.z=-Math.sin(t*3)*.35*k; head.rotation.z=Math.sin(t*2)*.1*k; pouch.scale.y=.6+Math.sin(t*3)*.08*k;
 // spray churn behind board
 const sp=sprayGeo.attributes.position; for(let i=0;i<N;i++){let y=sp.getY(i)+vel[i].y*dt*k; let x=sp.getX(i)+vel[i].x*dt*k; if(y>2.2){y=.05;x=(Math.random()-.5)*3;} sp.setY(i,y); sp.setX(i,x);} sp.needsUpdate=true;
 camera.position.x=Math.sin(t*.18)*9*k; camera.position.y=4.2+Math.sin(t*.4)*.5*k; camera.lookAt(0,1.4,0);
 renderer.render(scene,camera);}
tick();
