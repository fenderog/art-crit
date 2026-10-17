import * as THREE from 'three';

const host = document.querySelector('#scene');
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera();
camera.position.set(10, 7.8, 14);
camera.lookAt(0, 1.35, 0);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.23;
host.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xfff9df, 0x558b82, 2.7));
const sun = new THREE.DirectionalLight(0xffe8bb, 4);
sun.position.set(-4, 10, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left:-9, right:9, top:9, bottom:-9, near:1, far:30 });
sun.shadow.normalBias = .04;
sun.shadow.bias = -.0002;
sun.shadow.radius = 4;
scene.add(sun);
const rim = new THREE.DirectionalLight(0xc2f5e9, 1.7);
rim.position.set(0, 5, -7); scene.add(rim);
const mat = (color, roughness=.55) => new THREE.MeshStandardMaterial({ color, roughness });
const ivory=mat('#fff8df'), white=mat('#fffdf0'), dark=mat('#293e42'), yellow=mat('#efb64b'), orange=mat('#dd843d'), coral=mat('#dc7255'), cream=mat('#ffe7ad');
function mesh(geo, material, parent=scene) { const m=new THREE.Mesh(geo,material);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m; }
function egg(parent, material, position, scale) {const m=mesh(new THREE.SphereGeometry(1,32,24),material,parent);m.position.set(...position);m.scale.set(...scale);return m;}
function line(points, radius, material, parent=scene) {return mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),Math.max(20,points.length*6),radius,7,false),material,parent);}

// A small, sculptural piece of ocean, with a softly bevelled edge.
const ocean = new THREE.Group(); scene.add(ocean);
const waterMat=mat('#319f9d',.3);
const base=mesh(new THREE.CylinderGeometry(5.55,5.15,.43,96),waterMat,ocean);
base.position.y=-.22;base.scale.z=.71;
const surface=mesh(new THREE.CircleGeometry(5.53,96),mat('#53b7ad',.32),ocean);
surface.rotation.x=-Math.PI/2;surface.scale.y=.71;surface.position.y=.005;
const floor=mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({opacity:.12}));
floor.rotation.x=-Math.PI/2;floor.position.y=-.47;floor.castShadow=false;

// The wave is a continuous curled ribbon, not a stack of primitives.
const section=new THREE.CatmullRomCurve3([
 new THREE.Vector3(0,.05,-3.1),new THREE.Vector3(0,.65,-2.92),new THREE.Vector3(0,1.8,-2.55),
 new THREE.Vector3(0,2.9,-1.92),new THREE.Vector3(0,3.46,-1.07),new THREE.Vector3(0,3.36,-.24),
 new THREE.Vector3(0,2.83,.18),new THREE.Vector3(0,2.4,-.02)
]);
function wavePoint(u,v,t=0){const p=section.getPoint(v);const x=(u-.5)*9.3;const taper=Math.pow(Math.max(0,Math.sin(Math.PI*u)),.48);const height=taper*(.93-.23*u);return new THREE.Vector3(x,p.y*height+.025+Math.sin(u*16+t)*.035*Math.sin(v*Math.PI),p.z+Math.sin(u*5)*.13);}
const nx=100,ny=48, positions=[],colors=[],indices=[];
const deep=new THREE.Color('#168e96'),light=new THREE.Color('#8bdbbf');
for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++){const p=wavePoint(i/nx,j/ny);positions.push(p.x,p.y,p.z);const c=deep.clone().lerp(light, Math.pow(j/ny,3)*.8+ .08*Math.sin(i*.12));colors.push(c.r,c.g,c.b);if(i<nx&&j<ny){const a=i*(ny+1)+j,b=a+ny+1;indices.push(a,b,a+1,b,b+1,a+1);}}
const waveGeo=new THREE.BufferGeometry();waveGeo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));waveGeo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));waveGeo.setIndex(indices);waveGeo.computeVertexNormals();
const wave=mesh(waveGeo,new THREE.MeshStandardMaterial({vertexColors:true,side:THREE.DoubleSide,roughness:.27,metalness:.08}));
const foam=mat('#edfae1',.7), paleWater=mat('#99dbca',.5);
for(let k=0;k<5;k++){const pts=[];for(let i=0;i<=85;i++){const u=.012+i/85*.976,p=wavePoint(u,.91+k*.018);p.y+=.018+Math.sin(i*.7+k)*.014;pts.push(p.toArray());}line(pts,.024+(k===2?.018:0),k===0?paleWater:foam);}
// Long water-colour lines running over the face of the swell.
for(let k=0;k<19;k++){const u=.07+k*.047;const pts=[];for(let j=0;j<15;j++){const p=wavePoint(u+Math.sin(j*.15)*.012,.09+j/14*.69);p.z+=.025;pts.push(p.toArray());}line(pts,k%3===0?.018:.009,paleWater);}
let seed=17;function random(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
for(let k=0;k<42;k++){
 const x=(random()-.5)*9,z=.4+random()*2.8; if((x*x/30+z*z/15)> .91)continue;
 const pts=[];const length=.2+random()*.75;for(let j=0;j<8;j++)pts.push([x+j/7*length,.035,z+Math.sin(j/7*Math.PI)*.045]);
 line(pts,k%4===0?.022:.012,k%3===0?foam:paleWater);
}

const surfer=new THREE.Group();scene.add(surfer);surfer.position.set(.65,.45,1.15);surfer.rotation.y=-.12;
// Hand-shaped longboard, with inset double pinstripes.
const boardShape=new THREE.Shape();boardShape.moveTo(-2.13,0);boardShape.bezierCurveTo(-2.13,-.46,-.85,-.59,.8,-.48);boardShape.bezierCurveTo(2.45,-.37,2.52,.12,1.79,.37);boardShape.bezierCurveTo(.5,.71,-2.13,.65,-2.13,0);
const board=mesh(new THREE.ExtrudeGeometry(boardShape,{depth:.12,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.065,bevelThickness:.045,curveSegments:40}),coral,surfer);board.rotation.x=-Math.PI/2;
for(const z of [-.14,.14]){line([[-1.98,.178,z],[-.9,.178,z],[.6,.178,z],[1.9,.178,z]],.035,cream,surfer);}
const fin=mesh(new THREE.ConeGeometry(.25,.55,3),dark,surfer);fin.position.set(-1.35,-.24,0);fin.rotation.z=Math.PI;
// A relaxed stance: two webbed feet and bent little legs.
const bird=new THREE.Group();surfer.add(bird);bird.position.set(-.22,0,0);
for(const z of [-.26,.26]){
 line([[-.28,.23,z],[-.38,.57,z],[-.12,.86,z]],.065,orange,bird);
 const foot=egg(bird,orange,[-.07,.25,z],[.35,.065,.17]);foot.rotation.y=z*.3;
 for(let j=0;j<3;j++)line([[-.11,.3,z],[.16,.27,z+(j-1)*.095]],.015,yellow,bird);
}
const body=egg(bird,ivory,[-.26,1.21,0],[.86,.68,.51]);body.rotation.z=.16;
const tail=egg(bird,dark,[-1.02,1.11,0],[.62,.16,.31]);tail.rotation.z=-.17;
for(let i=0;i<3;i++){const f=egg(bird,ivory,[-1.05,1.23,(i-1)*.15],[.55,.12,.105]);f.rotation.z=-.15;}
// Curving neck, with a fuller chest and a deliberately oversized bill.
line([[.05,1.32,0],[.28,1.73,0],[.23,2.12,0],[.38,2.45,0],[.6,2.55,0]],.235,ivory,bird);
egg(bird,ivory,[.12,1.65,.01],[.39,.48,.35]);
const head=new THREE.Group();head.position.set(.54,2.49,0);bird.add(head);
egg(head,white,[0,0,0],[.43,.42,.34]);
// Amber throat pouch: a tapered, curved volume under the upper mandible.
const pouchGeo=new THREE.BufferGeometry(),pp=[],ii=[];
for(let i=0;i<=30;i++){let t=i/30;const r=Math.sin(Math.PI*(t*.93+.055));for(let j=0;j<=24;j++){const a=j/24*Math.PI*2;pp.push(.23+t*1.45,-.09-Math.sin(Math.PI*t)*.19+Math.cos(a)*.19*r,Math.sin(a)*.225*r*(1-t*.6));if(i<30&&j<24){const q=i*25+j;ii.push(q,q+25,q+1,q+25,q+26,q+1);}}}
pouchGeo.setAttribute('position',new THREE.Float32BufferAttribute(pp,3));pouchGeo.setIndex(ii);pouchGeo.computeVertexNormals();mesh(pouchGeo,orange,head);
const billShape=new THREE.Shape();billShape.moveTo(.17,.025);billShape.quadraticCurveTo(.87,.1,1.72,-.075);billShape.quadraticCurveTo(1.75,-.17,1.61,-.15);billShape.lineTo(.2,-.11);billShape.closePath();
const bill=mesh(new THREE.ExtrudeGeometry(billShape,{depth:.23,bevelEnabled:true,bevelThickness:.04,bevelSize:.035,bevelSegments:3,steps:1}),yellow,head);bill.position.z=-.115;
for(const sign of [-1,1]){
 egg(head,cream,[.135,.1,sign*.297],[.14,.145,.045]);
 egg(head,dark,[.167,.11,sign*.333],[.065,.074,.027]);
 egg(head,white,[.184,.136,sign*.354],[.018,.022,.008]);
 line([[.02,.255,sign*.27],[.12,.27,sign*.28],[.23,.23,sign*.27]],.027,ivory,head);
}
for(let i=0;i<3;i++){const tuft=egg(head,white,[-.25-i*.055,.28-i*.07,0],[.24,.09,.14]);tuft.rotation.z=-.4+i*.15;}
const wings=[];
for(const sign of [-1,1]){
 const wing=new THREE.Group();wing.position.set(-.26,1.48,sign*.25);bird.add(wing);wings.push(wing);
 const arm=egg(wing,ivory,[-.14,.04,sign*.49],[.57,.21,.76]);arm.rotation.y=sign*.28;
 const tip=egg(wing,dark,[-.43,-.005,sign*1.05],[.49,.13,.65]);tip.rotation.y=sign*.37;
 for(let i=0;i<7;i++){
  const feather=egg(wing,i<2?ivory:dark,[-.74+i*.105,-.025-i*.014,sign*(.55+i*.145)],[.55-i*.022,.075,.12]);
  feather.rotation.y=sign*(-.3+i*.14);feather.rotation.z=.07;
 }
 for(let i=0;i<4;i++){const f=egg(wing,white,[-.28+i*.08,.16,sign*(.35+i*.16)],[.3,.07,.13]);f.rotation.y=sign*.35;}
}
// Airborne spray and a broken, streaming wake.
const wake=new THREE.Group();scene.add(wake);
for(let i=0;i<3;i++){const pts=[];for(let j=0;j<30;j++)pts.push([-3.7+j/29*3.2,.09+Math.sin(j*.13)*.04,1.1+(i-1)*.3+Math.sin(j*.13)*.16]);line(pts,.024+i*.009,foam,wake);}
const drops=[];
for(let i=0;i<38;i++){
 const d=egg(scene,foam,[0,0,0],[1,1,1]);const s=.018+random()*.033;d.scale.set(s,s*(1.2+random()),s);d.castShadow=false;
 drops.push({mesh:d,phase:random(),x:-2.8+random()*2.1,z:.6+random()*1.4,speed:.3+random()*.3});
}
// Tiny distant seabirds finish the open-air composition.
const gullMat=mat('#668b77');
for(let i=0;i<3;i++){const g=new THREE.Group();scene.add(g);g.position.set(-2.4+i*1.2,4.5+i*.22,-3.6-i*.2);g.scale.setScalar(.6+i*.1);line([[-.37,0,0],[-.19,.09,0],[0,-.03,0],[.18,.09,0],[.37,.02,0]],.018,gullMat,g);}

function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);const aspect=w/h;const vertical=10.5;camera.left=-vertical*aspect/2;camera.right=vertical*aspect/2;camera.top=vertical/2;camera.bottom=-vertical/2;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe(host);resize();
const clock=new THREE.Clock();
function animate(){const t=clock.getElapsedTime();surfer.position.y=.45+Math.sin(t*1.4)*.075;surfer.position.x=.65+Math.sin(t*.48)*.2;surfer.rotation.z=.035+Math.sin(t*1.4)*.035;surfer.rotation.x=Math.sin(t*.9)*.035;
 wings[0].rotation.x=.07+Math.sin(t*1.6)*.055;wings[1].rotation.x=-.1-Math.sin(t*1.6+.4)*.07;head.rotation.z=Math.sin(t*.8)*.025;
 const p=waveGeo.attributes.position;for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++){const v=wavePoint(i/nx,j/ny,t*.9);p.setY(i*(ny+1)+j,v.y);}p.needsUpdate=true;waveGeo.computeVertexNormals();
 for(const d of drops){const a=(t*d.speed+d.phase)%1;d.mesh.position.set(d.x-a*.8,.1+Math.sin(a*Math.PI)*(.35+d.phase*.65),d.z+a*.15);d.mesh.visible=a<.93;}
 wake.position.x=Math.sin(t)*.08;renderer.render(scene,camera);requestAnimationFrame(animate);}
animate();
