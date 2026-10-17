import * as THREE from "three";
const r = new THREE.WebGLRenderer({antialias:true});
r.setSize(innerWidth, innerHeight); r.setPixelRatio(Math.min(devicePixelRatio,2));
document.body.appendChild(r.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xa8dcf0);
scene.fog = new THREE.Fog(0xa8dcf0, 25, 80);
const cam = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 200);
scene.add(new THREE.HemisphereLight(0xffffff, 0x2a6a8a, 1.1));
const sun = new THREE.DirectionalLight(0xfff0d0, 2); sun.position.set(5,10,6); scene.add(sun);

// sun disc
const sd = new THREE.Mesh(new THREE.CircleGeometry(5,32), new THREE.MeshBasicMaterial({color:0xfff4c0,fog:false}));
sd.position.set(-20,14,-70); scene.add(sd);

// water
const wg = new THREE.PlaneGeometry(120,120,120,120); wg.rotateX(-Math.PI/2);
const wm = new THREE.MeshStandardMaterial({color:0x1b8fb0,flatShading:true,roughness:.35});
const water = new THREE.Mesh(wg, wm); scene.add(water);
const pos = wg.attributes.position, base = pos.array.slice();
function h(x,z,t){
  return Math.sin(x*.25+t*1.2)*.7 + Math.sin(z*.3+x*.1+t*.8)*.5 + Math.sin(x*.7-t*2)*.12
   + 1.8*Math.exp(-((z+1)**2)/6)*Math.sin(x*.12+t*.6)*.5;
}
const wave = (x,t)=>h(x,0,t);

// surfboard
const surf = new THREE.Group(); scene.add(surf);
const board = new THREE.Mesh(new THREE.SphereGeometry(1,24,12), new THREE.MeshStandardMaterial({color:0xff6a3d,roughness:.4}));
board.scale.set(2.4,.12,.6); surf.add(board);
const stripe = new THREE.Mesh(new THREE.BoxGeometry(3.6,.02,.12), new THREE.MeshStandardMaterial({color:0xffffff}));
stripe.position.y=.12; surf.add(stripe);

// pelican
const p = new THREE.Group(); p.position.y=.1; surf.add(p);
const white = new THREE.MeshStandardMaterial({color:0xf6f3ea,roughness:.8});
const wing = new THREE.MeshStandardMaterial({color:0x6d747c,roughness:.8,side:2});
const beakM = new THREE.MeshStandardMaterial({color:0xf2b233,roughness:.5});
const mk=(g,m,x,y,z,s)=>{const o=new THREE.Mesh(g,m);o.position.set(x,y,z);if(s)o.scale.set(...s);p.add(o);return o;};
const sph=new THREE.SphereGeometry(1,20,16);
const body=mk(sph,white,0,.75,0,[.7,.55,.45]); body.rotation.z=.2;
mk(sph,white,-.75,.65,0,[.5,.2,.2]); // tail
const neck = new THREE.Group(); neck.position.set(.5,.95,0); p.add(neck);
const n1=new THREE.Mesh(new THREE.CylinderGeometry(.09,.13,.7,10),white); n1.position.set(.12,.3,0); n1.rotation.z=-.4; neck.add(n1);
const head=new THREE.Mesh(sph,white); head.scale.setScalar(.2); head.position.set(.3,.6,0); neck.add(head);
const beak=new THREE.Mesh(new THREE.ConeGeometry(.09,.8,8),beakM); beak.rotation.z=-Math.PI/2-.12; beak.position.set(.75,.55,0); neck.add(beak);
const pouch=new THREE.Mesh(sph,beakM); pouch.scale.set(.35,.08,.07); pouch.position.set(.7,.5,0); neck.add(pouch);
for(const s of[1,-1]){const e=new THREE.Mesh(sph,new THREE.MeshBasicMaterial({color:0x111111}));e.scale.setScalar(.035);e.position.set(.4,.65,s*.17);neck.add(e);}
// wings
const wings=[1,-1].map(s=>{const g=new THREE.Group();g.position.set(0,.95,s*.3);
  const sh=new THREE.Shape();sh.moveTo(0,0);sh.quadraticCurveTo(-.2,1.2,-.5,2.2);sh.lineTo(-1,1.8);sh.quadraticCurveTo(-.9,.6,-.7,0);
  const m=new THREE.Mesh(new THREE.ShapeGeometry(sh),wing);m.rotation.x=-Math.PI/2;m.rotation.z=0;
  const inner=new THREE.Group();inner.add(m);m.scale.set(1,s,1);m.rotation.x=-Math.PI/2; 
  // shape lies along local +y -> map to z outward
  m.rotation.set(s>0?Math.PI/2:-Math.PI/2,0,0);m.scale.set(1,1,1);
  g.add(m);p.add(g);return g;});
// legs
for(const s of[1,-1]){const l=new THREE.Mesh(new THREE.CylinderGeometry(.04,.04,.4),beakM);l.position.set(.1-s*.2,.35,s*.2);p.add(l);}

// spray
const N=300, sp=new Float32Array(N*3), sv=[];
const sg=new THREE.BufferGeometry(); sg.setAttribute("position",new THREE.BufferAttribute(sp,3));
scene.add(new THREE.Points(sg,new THREE.PointsMaterial({color:0xffffff,size:.15,transparent:true,opacity:.8})));
for(let i=0;i<N;i++)sv.push({l:Math.random()*2,v:new THREE.Vector3()});

const clock=new THREE.Clock();
function frame(){
  const t=clock.getElapsedTime();
  for(let i=0;i<pos.count;i++){
    const x=base[i*3],z=base[i*3+2];
    pos.array[i*3+1]=h(x,z,t);
  }
  pos.needsUpdate=true; wg.computeVertexNormals();
  const bx=Math.sin(t*.5)*3, bz=Math.sin(t*.7)*1.2-1;
  const by=h(bx,bz,t);
  const e=.3, sx=(h(bx+e,bz,t)-h(bx-e,bz,t))/(2*e), sz=(h(bx,bz+e,t)-h(bx,bz-e,t))/(2*e);
  surf.position.set(bx,by+.05,bz);
  surf.rotation.set(-sz*.8+Math.sin(t*1.3)*.08,Math.cos(t*.5)*-.25,Math.atan(sx)+Math.sin(t*.9)*.05);
  p.rotation.z=Math.sin(t*1.1)*.08; p.rotation.x=Math.sin(t*.9)*.05;
  neck.rotation.z=Math.sin(t*1.5)*.08;
  const fl=Math.sin(t*2.2)*.25+.35;
  wings[0].rotation.x=fl; wings[1].rotation.x=-fl;
  wings[0].rotation.z=wings[1].rotation.z=Math.sin(t*2.2)*.1;
  for(let i=0;i<N;i++){const q=sv[i];q.l-=.016;
    if(q.l<=0){q.l=.8+Math.random()*.8;sp[i*3]=bx-1.8+Math.random()*.4;sp[i*3+1]=by+.1;sp[i*3+2]=bz+(Math.random()-.5)*.6;
      q.v.set(-1-Math.random()*1.5,1.5+Math.random()*2,(Math.random()-.5)*1.5);}
    q.v.y-=.07;sp[i*3]+=q.v.x*.016;sp[i*3+1]+=q.v.y*.016*2;sp[i*3+2]+=q.v.z*.016;}
  sg.attributes.position.needsUpdate=true;
  cam.position.set(bx*.4+Math.sin(t*.2)*3,3.2+Math.sin(t*.3)*.5,9);
  cam.lookAt(bx,by+1,bz);
  r.render(scene,cam); requestAnimationFrame(frame);
}
frame();
addEventListener("resize",()=>{r.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();});
