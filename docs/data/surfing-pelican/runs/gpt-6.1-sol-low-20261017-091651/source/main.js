import * as THREE from 'three';

const host = document.querySelector('#scene');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(33, 1, .1, 100);
camera.position.set(9, 6.7, 13.5); camera.lookAt(0, .8, 0);
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.setClearColor(0xf3eddf,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;host.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xfff4db,0x5caaa2,2.7));
const sun=new THREE.DirectionalLight(0xffefcf,4);sun.position.set(-3,9,5);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-9;sun.shadow.camera.right=9;sun.shadow.camera.top=9;sun.shadow.camera.bottom=-9;sun.shadow.normalBias=.035;scene.add(sun);
const mat=(c,roughness=.65)=>new THREE.MeshStandardMaterial({color:c,roughness});
const white=mat('#fff8de'), cream=mat('#e8e5ce'), orange=mat('#f5a447'), coral=mat('#e8664d'), dark=mat('#263c37'), feet=mat('#e9a24c'), teal=mat('#37aaa6'), foam=mat('#dcf5e7');
function ell(parent,material,pos,scale){const m=new THREE.Mesh(new THREE.SphereGeometry(1,40,24),material);m.position.set(...pos);m.scale.set(...scale);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
function tube(parent,points,r,material){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,48,r,8,false),material);parent.add(mesh);mesh.castShadow=true;return mesh;}
const ocean=new THREE.Group();scene.add(ocean);
const water=ell(ocean,teal,[0,-.32,0],[6.6,.42,3.7]);
const rim=ell(ocean,mat('#82c7b8'),[0,-.46,0],[6.65,.35,3.75]);
// A sculpted travelling swell with a pale, curling lip.
const wave=new THREE.Group();ocean.add(wave);
const vertices=[],indices=[];const nx=100,nz=34;
for(let i=0;i<=nx;i++){const x=(i/nx-.5)*11;const taper=Math.pow(Math.sin(Math.PI*i/nx),.8);for(let j=0;j<=nz;j++){const v=j/nz;const z=-2.8+v*2.4;const y=.05+taper*(1.48*Math.exp(-Math.pow((v-.52)/.24,2)));vertices.push(x,y,z+.24*Math.sin(x*.5));if(i<nx&&j<nz){const a=i*(nz+1)+j,b=a+nz+1;indices.push(a,b,a+1,b,b+1,a+1);}}}
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setIndex(indices);geo.computeVertexNormals();const waveMesh=new THREE.Mesh(geo,mat('#47bdb3'));waveMesh.material.side=THREE.DoubleSide;waveMesh.receiveShadow=true;wave.add(waveMesh);
for(let k=0;k<3;k++){const pts=[];for(let i=0;i<=70;i++){const x=(i/70-.5)*10.8;const t=Math.pow(Math.sin(Math.PI*i/70),.8);pts.push([x,.08+1.48*t-k*.075,-1.56+.24*Math.sin(x*.5)+k*.075]);}tube(wave,pts,.037-k*.007,foam);}
// Fine, hand-drawn-looking traces on the water.
for(let k=0;k<22;k++){const z=.1+(k%6)*.47,x=-5.2+((k*1.73)%9.6);const pts=[];for(let j=0;j<15;j++)pts.push([x+j*.065,.065+.015*Math.sin(j*.3),z+.04*Math.sin(j*.4+k)]);tube(ocean,pts,.012,k%3?mat('#9bd9c8'):foam);}
const surfer=new THREE.Group();surfer.position.set(.2,.43,.6);scene.add(surfer);
const board=new THREE.Group();board.rotation.z=-.035;surfer.add(board);
ell(board,coral,[0,0,0],[2.25,.12,.59]);
ell(board,mat('#f6dca2'),[0,.109,0],[1.98,.021,.075]);
for(const z of [-.38,.38]){tube(board,[[-1.7,.06,z],[-.4,.12,z],[1,.11,z],[1.8,.05,z*.5]],.017,white);}
const bird=new THREE.Group();bird.position.set(-.15,.12,0);surfer.add(bird);
// Sturdy little legs and broad webbed feet.
for(const z of [-.27,.3]){tube(bird,[[-.1,.7,z],[-.24,.35,z],[-.1,.12,z]],.075,feet);const foot=ell(bird,feet,[.06,.1,z],[.32,.065,.2]);foot.rotation.y=-.15;}
ell(bird,white,[-.35,1.12,0],[.91,.69,.55]);
const tail=ell(bird,cream,[-1.12,1.27,0],[.53,.18,.3]);tail.rotation.z=-.3;
// The neck bends forward into the characteristic oversized bill.
tube(bird,[[.13,1.16,0],[.43,1.58,0],[.35,2.06,0],[.49,2.43,0]],.245,white);
ell(bird,white,[.54,2.46,0],[.43,.39,.35]);
const pouch=ell(bird,mat('#e9b859'),[1.24,2.24,0],[.77,.24,.24]);pouch.rotation.z=.1;
const bill=ell(bird,orange,[1.31,2.43,0],[.93,.095,.235]);bill.rotation.z=-.035;
tube(bird,[[.67,2.4,.222],[1.35,2.39,.19],[2.17,2.36,.015]],.013,mat('#bf7540'));
for(const z of [-.305,.305]){ell(bird,mat('#e7b85e'),[.62,2.55,z],[.116,.122,.035]);ell(bird,dark,[.65,2.56,z*1.09],[.065,.074,.025]);ell(bird,white,[.665,2.582,z*1.15],[.018,.022,.012]);}
// A windswept crest.
for(let i=0;i<3;i++){const tuft=ell(bird,white,[.22-i*.085,2.75+i*.025,0],[.24,.067,.09]);tuft.rotation.z=-.45-i*.1;}
const wings=[];
for(const side of [-1,1]){const pivot=new THREE.Group();pivot.position.set(-.43,1.45,side*.38);bird.add(pivot);pivot.rotation.x=side*-.15;const wing=ell(pivot,cream,[-.25,.02,side*.51],[.63,.16,.76]);wing.rotation.y=side*.35;for(let i=0;i<5;i++){const feather=ell(pivot,i<2?white:mat('#657973'),[-.65+i*.15,-.02,side*(.91+i*.035)],[.28,.075,.38]);feather.rotation.y=side*(-.5+i*.12);}wings.push(pivot);}
// Tiny foam pearls trail the board, never obscuring the silhouette.
const bubbles=[];for(let i=0;i<45;i++){const a=i*2.399;const r=.3+(i%8)*.13;const m=ell(scene,foam,[-1.9-Math.random()*1.8,.13, .5+Math.sin(a)*r],[.035+Math.random()*.07,.03,.035+Math.random()*.06]);bubbles.push(m);}
function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}window.addEventListener('resize',resize);resize();
const clock=new THREE.Clock();function animate(){requestAnimationFrame(animate);const t=clock.getElapsedTime();surfer.position.y=.45+Math.sin(t*1.7)*.095;surfer.rotation.z=Math.sin(t*1.7)*.035;surfer.rotation.y=Math.sin(t*.7)*.04;bird.rotation.z=Math.sin(t*1.7+.6)*-.025;wings.forEach((w,i)=>w.rotation.x=(i?1:-1)*(-.15+Math.sin(t*1.7+.7)*.09));wave.scale.y=1+Math.sin(t*1.2)*.035;bubbles.forEach((b,i)=>{b.position.y=.13+Math.max(0,Math.sin(t*2+i))*.09;b.scale.setScalar(.7+.3*Math.sin(t*2+i));});renderer.render(scene,camera);}animate();
