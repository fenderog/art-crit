import * as THREE from 'three';

const container = document.querySelector('#scene');
const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);
const camera = new THREE.OrthographicCamera(-9,9,5,-5,.1,100);
camera.position.set(0,6.8,14); camera.lookAt(0,1,0);
scene.add(new THREE.HemisphereLight(0xfff5da,0x3e9391,2.6));
const sunlight = new THREE.DirectionalLight(0xffe8c4,3.2);
sunlight.position.set(-5,10,6); sunlight.castShadow=true;
sunlight.shadow.mapSize.set(2048,2048);
Object.assign(sunlight.shadow.camera,{left:-10,right:10,top:10,bottom:-10,near:1,far:30});
sunlight.shadow.bias=-.0006;
scene.add(sunlight);
const mat = (color, roughness=.65) => new THREE.MeshStandardMaterial({color,roughness});
const ivory=mat('#fff1d8'), white=mat('#fff9e9'), wingMat=mat('#e6e5d3'), dark=mat('#304b4c'), yellow=mat('#f4b942'), orange=mat('#de8744'), coral=mat('#ed765e');
function mesh(geometry,material,parent=scene){const o=new THREE.Mesh(geometry,material);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
function ellipsoid(parent,material,pos,scale){const o=mesh(new THREE.SphereGeometry(1,40,28),material,parent);o.position.set(...pos);o.scale.set(...scale);return o;}
function tube(parent,points,r,material){return mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p))),32,r,10,false),material,parent);}
function shapeMesh(parent, points, depth, material, bevel=.06){const shape=new THREE.Shape();shape.moveTo(...points[0]);for(let i=1;i<points.length;i++)shape.lineTo(...points[i]);shape.closePath();const g=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:bevel,bevelThickness:bevel});g.translate(0,0,-depth/2);return mesh(g,material,parent);}

// The soft disc and distant wisps are geometry, not external images.
const sun=mesh(new THREE.CircleGeometry(1.18,80),new THREE.MeshBasicMaterial({color:'#ffcf88',transparent:true,opacity:.9}));
sun.position.set(4.3,1.2,-6.5);sun.quaternion.copy(camera.quaternion);sun.castShadow=false;
const halo=mesh(new THREE.CircleGeometry(1.4,80),new THREE.MeshBasicMaterial({color:'#ffdcaa',transparent:true,opacity:.25,depthWrite:false}));halo.position.copy(sun.position);halo.position.z-=.02;halo.quaternion.copy(camera.quaternion);
const cloudMat=new THREE.MeshBasicMaterial({color:'#fff1d6',transparent:true,opacity:.48,depthWrite:false});
for(const [x,y,z,s] of [[-5,1.75,-8,1],[.8,2.4,-9,.6],[7,1.5,-9,.8]]){ellipsoid(scene,cloudMat,[x,y,z],[1.35*s,.055*s,.1]);ellipsoid(scene,cloudMat,[x+.5,y+.09,z],[.7*s,.08*s,.1]);}

const waterUniforms={time:{value:0}};
const waterGeo=new THREE.PlaneGeometry(100,45,240,150);waterGeo.rotateX(-Math.PI/2);waterGeo.translate(0,-.2,15);
const water=mesh(waterGeo,new THREE.ShaderMaterial({uniforms:waterUniforms,vertexShader:`
  uniform float time; varying vec3 vP; varying float vWave;
  void main(){vec3 p=position; float w=sin(p.x*1.1+p.z*1.8-time*1.1)*.055+sin(p.z*3.7-p.x*.48-time*1.4)*.027; p.y+=w;vP=p;vWave=w;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}
`,fragmentShader:`
  varying vec3 vP;varying float vWave;uniform float time;
  void main(){float far= 1.-smoothstep(-7.5,-1.,vP.z);vec3 c=mix(vec3(.19,.61,.58),vec3(.61,.78,.70),far);c+=vWave*1.0;
  float line=sin(vP.z*8.+sin(vP.x*1.3-time*.4)*1.4-time*.85);float fleck=sin(vP.x*4.5+vP.z*.7+time*.6);float foam=smoothstep(.965,1.,line)*smoothstep(.1,.85,fleck);c=mix(c,vec3(.80,.91,.79),foam*.39);gl_FragColor=vec4(c,1.);}
` }));water.castShadow=false;

// A long sculpted glassy shoulder, capped by a feathered line of sea foam.
const nx=160, ny=44, wavePositions=[], waveColors=[], waveIndices=[];
function wavePoint(u,v,t=0){const x=-3.5+u*14;const h=.12+2.15*Math.pow(Math.sin(u*Math.PI*.85),1.8);const a=v*2.05;return new THREE.Vector3(x,h*Math.sin(a)-.1+Math.sin(x*1.5-t)*.055,-2.6+v*2.4+Math.sin(x*.5-t*.4)*.12);}
for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++){const u=i/nx,v=j/ny,p=wavePoint(u,v);wavePositions.push(...p);const c=new THREE.Color().setRGB(.10+.20*v,.51+.24*v,.49+.20*v);if(v>.94)c.lerp(new THREE.Color('#e4eed4'),(v-.94)/.06*.9);waveColors.push(c.r,c.g,c.b);}
for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){const a=i*(ny+1)+j,b=a+ny+1;waveIndices.push(a,b,a+1,b,b+1,a+1);}
const wg=new THREE.BufferGeometry();wg.setAttribute('position',new THREE.Float32BufferAttribute(wavePositions,3));wg.setAttribute('color',new THREE.Float32BufferAttribute(waveColors,3));wg.setIndex(waveIndices);wg.computeVertexNormals();
const wave=mesh(wg,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.3,metalness:.05,side:THREE.DoubleSide}));wave.castShadow=false;
const foamMat=mat('#f1f2d9');
const foam=[];
for(let i=0;i<125;i++){const u=i/124,p=wavePoint(u,1);const o=ellipsoid(scene,foamMat,[p.x,p.y+.02,p.z],[.075+Math.random()*.08,.045+Math.random()*.07,.06+Math.random()*.08]);o.castShadow=false;foam.push({o,u,seed:Math.random()*6});}

const surfer=new THREE.Group();scene.add(surfer);surfer.position.set(2.35,.12,1.5);surfer.rotation.y=-.14;
const board=new THREE.Group();surfer.add(board);board.rotation.z=-.045;
// An oval, gently rockered longboard with a cream stringer.
const boardGeo=new THREE.SphereGeometry(1,72,24);const bp=boardGeo.attributes.position;
for(let i=0;i<bp.count;i++){const x=bp.getX(i);bp.setXYZ(i,x*2.1,bp.getY(i)*.105+Math.pow(Math.abs(x),5)*.18,bp.getZ(i)*.55);}boardGeo.computeVertexNormals();
mesh(boardGeo,coral,board);
const stripe=mesh(new THREE.PlaneGeometry(3.52,.075),ivory,board);stripe.rotation.x=-Math.PI/2;stripe.position.y=.109;
for(const z of [-.39,.39]){tube(board,[[-1.55,.13,z*.65],[-.6,.107,z],[.6,.107,z],[1.55,.13,z*.65]],.012,ivory);}
const fin=shapeMesh(board,[[.8,0],[1.3,-.42],[1.48,0]],.06,dark,.025);fin.position.y=-.08;
const bird=new THREE.Group();surfer.add(bird);
// Low, bent knees and wide webbed feet: the stance does the storytelling.
for(const z of [-.27,.29]){const dx=z<0?.43:-.42;tube(bird,[[dx*.55,1.18,z],[dx+.14,.68,z],[dx-.12,.28,z+.04]],.065,orange);const foot=shapeMesh(bird,[[dx-.22,.22],[dx-.57,.12],[dx-.46,.25],[dx-.72,.28],[dx-.4,.38],[dx-.12,.34]],.18,orange,.035);foot.rotation.x=.07;foot.position.z=z;}
ellipsoid(bird,ivory,[.13,1.64,0],[.72,.81,.51]).rotation.z=-.2;
ellipsoid(bird,white,[-.24,1.93,.02],[.5,.63,.46]).rotation.z=-.28;
const tail=shapeMesh(bird,[[.55,1.53],[1.36,1.55],[1.05,1.19],[.51,1.27]],.35,dark,.08);
tube(bird,[[-.24,2.06,0],[-.49,2.42,0],[-.59,2.77,0],[-.76,2.94,0]],.24,ivory);
ellipsoid(bird,white,[-.76,2.98,0],[.38,.4,.32]);
// Pelican's unmistakable long bill and deep golden throat pouch.
const pouch=shapeMesh(bird,[[-.98,2.94],[-2.18,2.89],[-1.81,2.64],[-1.25,2.49],[-.94,2.61]],.19,yellow,.065);
const bill=shapeMesh(bird,[[-1.0,3.055],[-2.26,2.99],[-2.34,2.93],[-1.04,2.93]],.21,orange,.035);
tube(bird,[[-1.04,2.94,.147],[-1.65,2.935,.14],[-2.23,2.945,.075]],.012,mat('#b96b37'));
for(const s of [-1,1]){ellipsoid(bird,yellow,[-.88,3.09,s*.283],[.117,.126,.035]);ellipsoid(bird,dark,[-.91,3.105,s*.313],[.064,.074,.024]);ellipsoid(bird,white,[-.929,3.129,s*.332],[.018,.022,.009]);}
// Swept wings, with individually rounded charcoal flight feathers.
const nearWing=new THREE.Group();bird.add(nearWing);nearWing.position.set(.05,1.9,.37);
ellipsoid(nearWing,wingMat,[.35,.02,.03],[.69,.37,.19]).rotation.z=.35;
for(let i=0;i<6;i++){const feather=ellipsoid(nearWing,i<2?wingMat:dark,[.51+i*.13,.02+i*.10,.045],[.38,.105,.10]);feather.rotation.z=.34+i*.08;}
const farWing=new THREE.Group();bird.add(farWing);farWing.position.set(.22,2.0,-.31);
ellipsoid(farWing,ivory,[.43,.39,0],[.25,.65,.16]).rotation.z=-.65;
for(let i=0;i<5;i++){const f=ellipsoid(farWing,dark,[.66+i*.115,.81+i*.075,-.02],[.12,.34-i*.018,.075]);f.rotation.z=-.6-i*.12;}
// A few wind-ruffled head feathers.
for(let i=0;i<3;i++){const f=ellipsoid(bird,white,[-.51+i*.075,3.24+i*.022,-.04],[.06,.24-i*.035,.075]);f.rotation.z=-.65-i*.15;}

// Board wake: broken, foamy ribbons and tiny airborne droplets.
const wake=new THREE.Group();scene.add(wake);wake.position.copy(surfer.position);
const wakeLines=[];
for(let i=0;i<9;i++){const points=[];for(let j=0;j<20;j++){const t=j/19;points.push([.8+t*(2.2+i*.13),-.09+Math.sin(t*3)*.035,(i-4)*.10+Math.sin(t*2)*.32]);}const o=tube(wake,points,.014+(i%3)*.006,foamMat);o.castShadow=false;wakeLines.push(o);}
const droplets=[];
for(let i=0;i<45;i++){const o=ellipsoid(scene,foamMat,[0,0,0],[.018,.05,.018]);o.castShadow=false;droplets.push({o,phase:Math.random(),x:Math.random()*2,z:Math.random()*1.1});}
// Tiny seabirds out over the horizon.
const distantMat=mat('#60837a');
for(const [x,y,s] of [[-.2,1.35,.17],[.5,1.6,.12],[6.4,2.1,.14]]){const g=new THREE.Group();g.position.set(x,y,-6);scene.add(g);tube(g,[[-s,.01,0],[-s*.45,.07,0],[0,0,0],[s*.45,.07,0],[s,.01,0]],.012,distantMat);}

function resize(){const w=innerWidth,h=innerHeight;renderer.setSize(w,h);const aspect=w/h;const height=aspect<1?11.8:10.2;camera.left=-height*aspect/2;camera.right=height*aspect/2;camera.top=height/2;camera.bottom=-height/2;camera.updateProjectionMatrix();if(aspect<1){camera.position.x=1.6;camera.position.y=7.6;camera.lookAt(1.6,1.8,0);surfer.position.set(2.0,-.1,2.4);surfer.scale.setScalar(.86);}else{camera.position.set(0,6.8,14);camera.lookAt(0,1,0);surfer.position.set(2.35,.12,1.5);surfer.scale.setScalar(1.08);}sun.quaternion.copy(camera.quaternion);halo.quaternion.copy(camera.quaternion);}
window.addEventListener('resize',resize);resize();
const clock=new THREE.Clock();
function animate(){const t=clock.getElapsedTime();waterUniforms.time.value=t;
surfer.position.y=.14+Math.sin(t*1.5)*.085;surfer.rotation.z=Math.sin(t*1.5+.7)*.035;surfer.rotation.y=-.14+Math.sin(t*.7)*.035;
bird.rotation.z=Math.sin(t*1.5+.3)*-.025;nearWing.rotation.x=Math.sin(t*1.7)*.08;nearWing.rotation.z=Math.sin(t*1.4)*.055;farWing.rotation.z=Math.sin(t*1.4+.8)*.06;
const pos=wg.attributes.position;for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++){const p=wavePoint(i/nx,j/ny,t);pos.setXYZ(i*(ny+1)+j,p.x,p.y,p.z);}pos.needsUpdate=true;wg.computeVertexNormals();
for(const f of foam){const p=wavePoint(f.u,1,t);f.o.position.set(p.x,p.y+.035+Math.sin(t*2+f.seed)*.025,p.z);}
wake.position.set(surfer.position.x,.04,surfer.position.z);for(let i=0;i<wakeLines.length;i++)wakeLines[i].scale.x=1+Math.sin(t*1.6+i)*.08;
for(const d of droplets){const a=(t*.55+d.phase)%1;d.o.position.set(surfer.position.x+1.25+d.x+a*1.5,.15+Math.sin(a*Math.PI)*(.3+d.x*.22),surfer.position.z+d.z-.5);d.o.scale.setScalar(Math.sin(a*Math.PI)*.7);}
renderer.render(scene,camera);requestAnimationFrame(animate);}
animate();
