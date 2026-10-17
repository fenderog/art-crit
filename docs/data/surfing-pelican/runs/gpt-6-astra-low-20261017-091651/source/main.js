import * as THREE from 'three';

const host = document.querySelector('#scene');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(33, 1, .1, 100);
camera.position.set(8, 6.5, 13); camera.lookAt(0, 1.05, 0);
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setClearColor(0xf3f0e5,0); renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;
host.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x618c87,2.5));
const sun=new THREE.DirectionalLight(0xfff2d6,4);sun.position.set(-4,10,6);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-9;sun.shadow.camera.right=9;sun.shadow.camera.top=9;sun.shadow.camera.bottom=-9;sun.shadow.normalBias=.03;scene.add(sun);
const mat=(color,roughness=.65)=>new THREE.MeshStandardMaterial({color,roughness});
const white=mat(0xfff9e9), feather=mat(0xe6e7d9), dark=mat(0x263f40), bill=mat(0xf4b94f), orange=mat(0xe9853d), coral=mat(0xed7950), foam=mat(0xe7ffef), teal=mat(0x209f9c,.32);
function mesh(geo,material,parent=scene){const m=new THREE.Mesh(geo,material);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
function ell(parent,material,p,s){const m=mesh(new THREE.SphereGeometry(1,40,24),material,parent);m.position.set(...p);m.scale.set(...s);return m;}
function tube(points,r,material,parent=scene){return mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),48,r,8,false),material,parent);}
// A small, sculptural slice of ocean, with a translucent-looking curled crest.
const sea=new THREE.Group();scene.add(sea);sea.position.set(.5,-.35,0);
const base=mesh(new THREE.CylinderGeometry(5,5,.22,100),teal,sea);base.scale.set(1,1,.65);base.position.y=-.15;
const surfaceGeo=new THREE.PlaneGeometry(10,6.5,100,60);surfaceGeo.rotateX(-Math.PI/2);
const a=surfaceGeo.attributes.position;
for(let i=0;i<a.count;i++){let x=a.getX(i),z=a.getZ(i);const q=Math.sqrt((x*x)/25+(z*z)/10.5625);if(q>1){x/=q;z/=q;}a.setXYZ(i,x,.06+Math.sin(x*1.5+z*2)*.055,z);}surfaceGeo.computeVertexNormals();mesh(surfaceGeo,teal,sea);
const waveGeo=new THREE.BufferGeometry(), positions=[],indices=[];
const NX=90, NT=42;
for(let i=0;i<=NX;i++){const x=-4.6+i/NX*9.2;const taper=Math.pow(Math.sin(i/NX*Math.PI),.65);for(let j=0;j<=NT;j++){const t=j/NT;const angle=t*3.85;const r=1.1*taper;positions.push(x,.04+r*(1-Math.cos(angle)), -1.75+r*Math.sin(angle));}}
for(let i=0;i<NX;i++)for(let j=0;j<NT;j++){const k=i*(NT+1)+j;indices.push(k,k+1,k+NT+1,k+1,k+NT+2,k+NT+1);}waveGeo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));waveGeo.setIndex(indices);waveGeo.computeVertexNormals();const waveMat=mat(0x36b4ac,.27);waveMat.side=THREE.DoubleSide;mesh(waveGeo,waveMat,sea);
const crest=[];for(let i=0;i<=90;i++){const x=-4.6+i/90*9.2,r=1.1*Math.pow(Math.sin(i/90*Math.PI),.65);crest.push([x,.08+r*(1-Math.cos(3.85)),-1.75+r*Math.sin(3.85)]);}tube(crest,.075,foam,sea);
// Foam scallops and floating flecks.
let seed=7;function rand(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
for(let i=0;i<100;i++){const p=crest[Math.floor(rand()*crest.length)],s=.035+rand()*.09;ell(sea,foam,[p[0],p[1]+rand()*.08,p[2]+(rand()-.5)*.25],[s*1.5,s*.55,s]);}
for(let i=0;i<32;i++){const x=(rand()-.5)*8,z=.5+rand()*1.8;if(x*x/25+z*z/10.5<.9){tube([[x,.14,z],[x+.16,.15,z+.04],[x+.4,.14,z]],.012,foam,sea);}}
const rider=new THREE.Group();scene.add(rider);rider.position.set(.1,.35,.65);rider.rotation.y=-.18;
// Longboard with a classic cream stringer.
const board=ell(rider,coral,[0,0,0],[2.35,.13,.64]);
ell(rider,white,[0,.116,0],[2.16,.022,.09]);
for(const x of [1.4,1.62]){const stripe=mesh(new THREE.BoxGeometry(.075,.018,.89),white,rider);stripe.position.set(x,.105,0);}
const bird=new THREE.Group();rider.add(bird);bird.position.set(0,.15,0);
for(const x of [-.44,.5]){tube([[x,.14,.1],[x+.06,.55,.09],[x-.08,.86,0]],.065,orange,bird);const foot=ell(bird,orange,[x-.15,.08,.19],[.3,.065,.23]);foot.rotation.y=.25;for(let k=0;k<3;k++)tube([[x-.1,.09,.14],[x-.35,.08,.04+k*.14]],.025,bill,bird);}
const body=ell(bird,white,[.22,1.12,0],[.84,.68,.54]);body.rotation.z=-.15;
// Tail feathers.
for(let i=0;i<5;i++){const f=ell(bird,i%2?white:feather,[1.05+i*.025,1.2,-.2+i*.1],[.55,.12,.1]);f.rotation.z=.3;}
// A tall curved pelican neck, and an unmistakable long bill.
tube([[-.16,1.2,0],[-.62,1.6,0],[-.7,2.12,0],[-.9,2.45,0]],.25,white,bird);
ell(bird,white,[-.89,2.44,0],[.43,.43,.35]);
const pouch=ell(bird,bill,[-1.49,2.15,0],[.79,.25,.24]);pouch.rotation.z=.16;
const beak=ell(bird,orange,[-1.64,2.36,0],[.98,.075,.23]);beak.rotation.z=.055;
tube([[-2.57,2.3,0],[-2.6,2.24,0],[-2.55,2.19,0]],.04,orange,bird);
for(const z of [-.315,.315]){ell(bird,bill,[-1.03,2.55,z],[.115,.12,.037]);ell(bird,dark,[-1.06,2.56,z*1.075],[.064,.073,.023]);ell(bird,white,[-1.08,2.59,z*1.13],[.018,.023,.011]);}
for(let i=0;i<3;i++){const tuft=ell(bird,white,[-.65+i*.06,2.76+i*.025,0],[.09,.2,.1]);tuft.rotation.z=-.5-i*.15;}
const wings=[];
for(const side of [-1,1]){const wing=new THREE.Group();wing.position.set(.25,1.45,side*.35);bird.add(wing);wing.rotation.x=side*-.25;wings.push(wing);const w=ell(wing,white,[.18,.08,side*.62],[.58,.16,.86]);w.rotation.y=side*-.28;for(let i=0;i<7;i++){const f=ell(wing,i>3?dark:feather,[.02+i*.13,.02,side*(1.04+(6-i)*.055)],[.15,.075,.43]);f.rotation.y=side*(-.35+i*.12);}}
// Tiny white spray follows the board, never obscuring the rider.
const droplets=[];for(let i=0;i<35;i++){const d=ell(scene,foam,[0,0,0],[.025,.055,.025]);droplets.push({m:d,phase:rand(),speed:.5+rand(),z:rand()*.9});}
// Distant little gull silhouettes.
for(let i=0;i<3;i++){const g=new THREE.Group();scene.add(g);g.position.set(-3.6+i*1.35,3.6+i*.35,-3.1);tube([[-.24,0,0],[-.12,.07,0],[0,0,0],[.12,.07,0],[.24,0,0]],.012,mat(0x718e85),g);g.scale.setScalar(.65+i*.12);}
function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}window.addEventListener('resize',resize);resize();
const clock=new THREE.Clock();function animate(){const t=clock.getElapsedTime();rider.position.y=.4+Math.sin(t*1.6)*.085;rider.rotation.z=Math.sin(t*1.6)*.035;rider.rotation.x=Math.sin(t*1.1)*.04;bird.rotation.z=Math.sin(t*1.6+.7)*.025;wings.forEach((w,i)=>w.rotation.x=(i===0?-1:1)*(-.25+Math.sin(t*1.8)*.09));sea.position.y=-.35+Math.sin(t*.8)*.025;for(const d of droplets){const p=(t*d.speed*.45+d.phase)%1;d.m.position.set(1.8+p*2.8,.25+Math.sin(p*Math.PI)*(.35+d.z),.4+d.z+p*.5);d.m.scale.setScalar((1-p)*.8);}
renderer.render(scene,camera);requestAnimationFrame(animate);}animate();
