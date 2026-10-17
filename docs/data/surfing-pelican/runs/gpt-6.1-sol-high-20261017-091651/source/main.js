import * as THREE from 'three';

// All geometry, textures and animation are generated locally.
const host = document.querySelector('#scene');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
host.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color('#f4eddf');
scene.fog = new THREE.Fog('#dfebe0', 25, 69);
const camera = new THREE.PerspectiveCamera(37, innerWidth / innerHeight, .1, 150);
const target = new THREE.Vector3(-1.6, 1.6, 0);
const viewDirection = new THREE.Vector3(-.48, .30, .84).normalize();
const right = new THREE.Vector3(.868, 0, .496);
const back = new THREE.Vector3(-.496, 0, .868);

scene.add(new THREE.HemisphereLight('#fff5da', '#438e86', 2.1));
const sunLight = new THREE.DirectionalLight('#fff2cc', 3.2);
sunLight.position.set(-7, 12, 7);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
Object.assign(sunLight.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: .5, far: 40 });
sunLight.shadow.bias = -.0006;
sunLight.shadow.normalBias = .025;
sunLight.shadow.radius = 4;
scene.add(sunLight);
const fill = new THREE.DirectionalLight('#b9e6d5', 1.3);
fill.position.set(5, 5, -7);
scene.add(fill);

const material = (color, roughness = .65, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness, ...extra });
const ivory = material('#fff3d5');
const featherCream = material('#e7e2c7');
const featherWhite = material('#fff8e6');
const darkFeather = material('#324b49');
const darkTip = material('#263f3d');
const gold = material('#f6b34e', .42);
const pouchMat = material('#e5a04f', .6);
const orange = material('#e28b41', .5);
const eyeBlack = material('#152d2a', .2);
const foamMat = material('#f4f6dd', .8);
const foamShade = material('#c8eddf', .8);
const sphereGeometry = new THREE.SphereGeometry(1, 32, 24);
function ellipsoid(parent, mat, pos, scale, rotation) {
  const mesh = new THREE.Mesh(sphereGeometry, mat);
  mesh.position.set(...pos); mesh.scale.set(...scale);
  if (rotation) mesh.rotation.set(...rotation);
  mesh.castShadow = true; mesh.receiveShadow = true;
  parent.add(mesh); return mesh;
}
function curveTube(parent, points, radius, mat, segments = 40) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 8, false), mat);
  parent.add(mesh); return mesh;
}
function capsuleBetween(parent, a, b, width, thickness, mat) {
  const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b);
  const mesh = ellipsoid(parent, mat, va.clone().add(vb).multiplyScalar(.5).toArray(), [width, va.distanceTo(vb) * .58, thickness]);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), vb.sub(va).normalize());
  return mesh;
}
let seed = 721;
function random() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

// A quiet, perfectly straight horizon behind the sculptural swell.
const seaGeo = new THREE.PlaneGeometry(160, 125, 150, 150);
seaGeo.rotateX(-Math.PI / 2);
const seaPos = seaGeo.attributes.position;
for (let i = 0; i < seaPos.count; i++) {
  const x = seaPos.getX(i), z = seaPos.getZ(i) + 52.5;
  seaPos.setXYZ(i, right.x*x + back.x*z, -.10, right.z*x + back.z*z);
}
seaGeo.computeVertexNormals();
const seaMat = material('#41b6ac', .48, { metalness: .04 });
seaMat.onBeforeCompile = shader => {
  shader.uniforms.uTime = { value: 0 }; seaMat.userData.shader = shader;
  shader.vertexShader = 'uniform float uTime; varying vec3 vWater;\n' + shader.vertexShader;
  shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
    transformed.y += .045 * sin(position.x*.9+uTime*.9) * cos(position.z*1.3-uTime*.6);
    vWater = transformed;`);
  shader.fragmentShader = 'uniform float uTime; varying vec3 vWater;\n' + shader.fragmentShader;
  shader.fragmentShader = shader.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
    float flow = sin(vWater.z*3.2 + sin(vWater.x*.7+uTime*.3)*1.8-uTime*.6);
    float ripple = smoothstep(.90,1.,flow) * .035;
    float depth = smoothstep(-9., 19., vWater.z);
    diffuseColor.rgb = mix(vec3(.035,.35,.29), diffuseColor.rgb, .35+depth*.65);
    diffuseColor.rgb += ripple;
  `);
};
const sea = new THREE.Mesh(seaGeo, seaMat); sea.receiveShadow = true; scene.add(sea);

// The apricot sun is a flat, matte disc, not a light source.
const sun = new THREE.Mesh(new THREE.CircleGeometry(1.75, 96), new THREE.MeshBasicMaterial({ color: '#edbf9c', fog: false, toneMapped: false }));
sun.position.set(5.7, 5.0, -9.5); sun.quaternion.copy(camera.quaternion); scene.add(sun);
const sunRing = new THREE.Mesh(new THREE.RingGeometry(1.88, 1.89, 96), new THREE.MeshBasicMaterial({ color: '#dfb68d', transparent: true, opacity: .3, side: THREE.DoubleSide, fog: false }));
sunRing.position.copy(sun.position); scene.add(sunRing);

// The wave is one continuous, curling surface, with vertex-coloured water.
const waveRoot = new THREE.Group(); waveRoot.position.set(.5, 0, -1.8); scene.add(waveRoot);
const section = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, .0, -6.5), new THREE.Vector3(0, .28, -4.6),
  new THREE.Vector3(0, 1.1, -2.9), new THREE.Vector3(0, 2.75, -1.9),
  new THREE.Vector3(0, 4.05, -.9), new THREE.Vector3(0, 4.35, .25),
  new THREE.Vector3(0, 3.88, 1.08), new THREE.Vector3(0, 3.20, .96)
]);
const NX = 150, NY = 62;
const wp = [], wc = [], wi = [];
const waterLow = new THREE.Color('#227c7a'), waterMid = new THREE.Color('#3db8ac'), waterHigh = new THREE.Color('#a2e2c7');
function wavePoint(x, v, t = 0) {
  const s = section.getPoint(v);
  const envelope = Math.exp(-Math.pow((x - 1.6) / 6.6, 4));
  // A lower left shoulder opens the view onto our rider.
  const shoulder = .43 + .57 * THREE.MathUtils.smoothstep(x, -5, 1.5);
  const edges = THREE.MathUtils.smoothstep(x, -8.5, -6.8) * (1 - THREE.MathUtils.smoothstep(x, 6.4, 8.5));
  const amplitude = envelope * shoulder * edges;
  const ripple = Math.sin(x*2.8+v*8+t*.8)*.035 + Math.sin(x*5-v*15+t)*.015;
  return new THREE.Vector3(x, s.y*amplitude + ripple*v, s.z + Math.sin(x*.45)*.22 + Math.sin(t*.55+x*.6)*.06*v);
}
for (let i=0;i<=NX;i++) {
  const x=-8.5+i/NX*17;
  for(let j=0;j<=NY;j++) {
    const v=j/NY, p=wavePoint(x,v); wp.push(p.x,p.y,p.z);
    const c=waterLow.clone().lerp(waterMid, Math.min(1,v*1.7));
    c.lerp(waterHigh, Math.pow(Math.max(0,(v-.55)/.45),1.8)*.85);
    const band = (Math.sin(x*14+v*8)*.5+.5)*.05;
    c.offsetHSL(0,0,band); wc.push(c.r,c.g,c.b);
    if(i<NX && j<NY) {const a=i*(NY+1)+j,b=a+NY+1;wi.push(a,b,a+1,b,b+1,a+1);}
  }
}
const waveGeo=new THREE.BufferGeometry(); waveGeo.setAttribute('position',new THREE.Float32BufferAttribute(wp,3)); waveGeo.setAttribute('color',new THREE.Float32BufferAttribute(wc,3)); waveGeo.setIndex(wi); waveGeo.computeVertexNormals();
const waveMat = material('#ffffff', .32, { vertexColors:true, side:THREE.DoubleSide, metalness:.04, transparent:true });
waveMat.onBeforeCompile = shader => {
  shader.vertexShader = 'varying vec2 vWaveCoord;\n' + shader.vertexShader;
  shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n vWaveCoord = vec2(position.x, position.z);');
  shader.fragmentShader = 'varying vec2 vWaveCoord;\n' + shader.fragmentShader;
  shader.fragmentShader = shader.fragmentShader.replace('#include <color_fragment>', '#include <color_fragment>\n diffuseColor.a *= smoothstep(0., .8, 8.5-abs(vWaveCoord.x)) * smoothstep(-6.5, -4.5, vWaveCoord.y);');
};
const wave = new THREE.Mesh(waveGeo,waveMat); wave.receiveShadow=true; waveRoot.add(wave);

// Long pale veins follow the water up and around its lip.
for(let i=0;i<55;i++) {
  const x=-7.9+i*.29+random()*.15;
  const points=[];
  const start=.14+random()*.35, end=.85+random()*.14;
  for(let j=0;j<=32;j++) {
    const v=start+(end-start)*j/32;
    const p=wavePoint(x+Math.sin(v*9+i)*.035,v);p.y+=.022;
    points.push(p.toArray());
  }
  const mat=new THREE.MeshStandardMaterial({color:i%3===0?'#e0f6d9':'#a1e0c9',roughness:.5,transparent:true,opacity:.14+random()*.2});
  curveTube(waveRoot,points,.009+random()*.009,mat,40);
}
const crestFoam=new THREE.Group(); waveRoot.add(crestFoam);
for(let i=0;i<200;i++) {
  const x=-8.3+i/199*16.6;
  const v=.91+random()*.09;
  const p=wavePoint(x,v); const r=.055+random()*.09;
  ellipsoid(crestFoam,i%4===0?foamShade:foamMat,[p.x,p.y+.025+(random()-.5)*.075,p.z+(random()-.5)*.10],[r*1.35,r*.85,r], [0,0,random()]);
}
// A scattering of delicate droplets rises off the crest.
const sprayCount=110, sprayArray=new Float32Array(sprayCount*3), spraySeeds=[];
for(let i=0;i<sprayCount;i++) spraySeeds.push({x:-6.5+random()*13,phase:random(),speed:.16+random()*.15,drift:random()*.7});
const sprayGeo=new THREE.BufferGeometry();sprayGeo.setAttribute('position',new THREE.BufferAttribute(sprayArray,3));
const spray=new THREE.Points(sprayGeo,new THREE.PointsMaterial({color:'#fff8de',size:.045,transparent:true,opacity:.8,sizeAttenuation:true}));waveRoot.add(spray);

// Hand-shaped longboard with a warm rail, cream pinline and striped deck.
const surfer=new THREE.Group();surfer.position.set(-.15,.38,2.15);scene.add(surfer);
const boardPivot=new THREE.Group();surfer.add(boardPivot);
const boardShape=new THREE.Shape();
boardShape.moveTo(-2.5,0);boardShape.bezierCurveTo(-2.48,-.39,-1.6,-.57,.5,-.52);boardShape.bezierCurveTo(1.6,-.48,2.2,-.31,2.27,0);boardShape.bezierCurveTo(2.2,.31,1.6,.48,.5,.52);boardShape.bezierCurveTo(-1.6,.57,-2.48,.39,-2.5,0);
const boardGeo=new THREE.ExtrudeGeometry(boardShape,{depth:.13,bevelEnabled:true,bevelSegments:4,steps:1,bevelSize:.065,bevelThickness:.06,curveSegments:48});
boardGeo.rotateX(-Math.PI/2);
const board=new THREE.Mesh(boardGeo,material('#e77c59',.38));board.castShadow=true;board.receiveShadow=true;boardPivot.add(board);
const deck = new THREE.Mesh(new THREE.ShapeGeometry(boardShape,64),material('#ef946e',.5));deck.rotation.x=-Math.PI/2;deck.position.y=.195;deck.scale.set(.94,.9,1);boardPivot.add(deck);
// Stringer and twin vintage stripes, clipped naturally by the rounded nose.
for(const z of [-.19,0,.19]) {
  const stripe=new THREE.Mesh(new THREE.BoxGeometry(z===0?4.38:4.0,.008,z===0?.025:.064),material(z===0?'#9d674e':'#f9e9c2'));
  stripe.position.set(-.08,.205,z);boardPivot.add(stripe);
}
const finShape=new THREE.Shape();finShape.moveTo(0,0);finShape.quadraticCurveTo(.8,-.85,.95,-.2);finShape.lineTo(1.02,0);
const fin=new THREE.Mesh(new THREE.ExtrudeGeometry(finShape,{depth:.05,bevelEnabled:true,bevelSize:.02,bevelThickness:.02,bevelSegments:2}),material('#264d46'));fin.position.set(.8,-.08,0);boardPivot.add(fin);

// Pelican: a soft, pear-shaped body, bent neck and unmistakable long bill.
const bird=new THREE.Group();bird.position.y=.2;boardPivot.add(bird);
ellipsoid(bird,ivory,[.18,1.12,0],[.72,.81,.53],[0,0,-.19]);
ellipsoid(bird,featherWhite,[-.19,1.20,.12],[.48,.65,.45],[0,0,-.2]);
// Scalloped tail feathers.
for(let i=0;i<5;i++) capsuleBetween(bird,[.55,.90,(i-2)*.105],[1.15+Math.abs(i-2)*.025,.80,(i-2)*.14],.11,.075,i%2?featherCream:ivory);
curveTube(bird,[[-.31,1.25,0],[-.64,1.65,0],[-.67,2.13,0],[-.86,2.44,0]],.225,ivory);
ellipsoid(bird,ivory,[-.83,2.47,0],[.40,.40,.335],[0,0,-.12]);
ellipsoid(bird,featherWhite,[-.98,2.49,.08],[.27,.29,.29]);
// Swept-back crown wisps.
for(let i=0;i<4;i++) capsuleBetween(bird,[-.72,2.73,(i-1.5)*.10],[-.35+i*.045,2.83-i*.035,(i-1.5)*.12],.075,.065,featherWhite);
// Sculpt the bill as elliptical sections; a very long, tapered silhouette.
function billMesh(rings, mat) {
  const pos=[],idx=[]; const n=32;
  for(const r of rings) for(let j=0;j<=n;j++){const a=j/n*Math.PI*2;pos.push(r[0],r[1]+Math.sin(a)*r[3],Math.cos(a)*r[2]);}
  for(let i=0;i<rings.length-1;i++)for(let j=0;j<n;j++){const a=i*(n+1)+j,b=a+n+1;idx.push(a,a+1,b,b,a+1,b+1);}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));geo.setIndex(idx);geo.computeVertexNormals();const m=new THREE.Mesh(geo,mat);m.castShadow=true;bird.add(m);return m;
}
billMesh([[-1.07,2.44,.245,.10],[-1.36,2.43,.25,.095],[-1.95,2.40,.17,.065],[-2.55,2.35,.045,.035],[-2.65,2.32,.007,.025]],gold);
billMesh([[-1.06,2.32,.21,.05],[-1.25,2.19,.23,.17],[-1.57,2.16,.19,.21],[-2.07,2.24,.12,.115],[-2.61,2.32,.006,.012]],pouchMat);
for(const side of [-1,1]) {
  curveTube(bird,[[-1.09,2.365,side*.24],[-1.6,2.35,side*.205],[-2.17,2.33,side*.11],[-2.61,2.32,side*.01]],.012,orange);
  ellipsoid(bird,orange,[-1.42,2.485,side*.16],[.045,.014,.023]);
  ellipsoid(bird,material('#e9b75f'),[-.98,2.59,side*.283],[.145,.15,.045]);
  ellipsoid(bird,eyeBlack,[-1.0,2.60,side*.32],[.081,.09,.035]);
  ellipsoid(bird,featherWhite,[-1.024,2.635,side*.349],[.024,.027,.009]);
  curveTube(bird,[[-1.10,2.72,side*.28],[-1.01,2.75,side*.30],[-.88,2.71,side*.30]],.036,ivory,12);
}
// Small orange legs and broad, three-pointed webbed feet.
for(const x of [-.4,.48]) {
  capsuleBetween(bird,[x,.23,.12],[x+.07,.72,.08],.06,.058,orange);
  const footShape=new THREE.Shape();footShape.moveTo(.16,-.11);footShape.lineTo(-.29,-.22);footShape.quadraticCurveTo(-.39,-.2,-.34,-.12);footShape.lineTo(-.43,.01);footShape.quadraticCurveTo(-.45,.07,-.34,.10);footShape.lineTo(-.32,.23);footShape.lineTo(.15,.13);footShape.closePath();
  const foot=new THREE.Mesh(new THREE.ExtrudeGeometry(footShape,{depth:.035,bevelEnabled:true,bevelSize:.025,bevelThickness:.02,bevelSegments:3}),orange);foot.rotation.x=-Math.PI/2;foot.position.set(x,.065,.09);bird.add(foot);
}
// Layered wings: broad shoulders, overlapping ivory coverts, charcoal flight tips.
const wings=[];
for(const side of [-1,1]) {
  const wing=new THREE.Group();wing.position.set(.21,1.48,side*.32);bird.add(wing);wings.push(wing);
  capsuleBetween(wing,[0,0,0],[.14,.30,side*1.1],.30,.19,ivory);
  capsuleBetween(wing,[.14,.26,side*.7],[.41,.48,side*1.75],.24,.15,featherCream);
  for(let i=0;i<9;i++) {
    const f=i/8;
    const a=[.04+f*.30,.14+f*.23,side*(.50+f*1.14)];
    const b=[.64+f*.32,.15+f*.53,side*(.73+f*1.45)];
    capsuleBetween(wing,a,b,.14-f*.035,.065, i>3?darkFeather:featherCream);
    const end=new THREE.Vector3(...a).lerp(new THREE.Vector3(...b),.65).toArray();
    capsuleBetween(wing,a,end,.145-f*.035,.07, i%2?ivory:featherWhite);
    if(i>5) capsuleBetween(wing,new THREE.Vector3(...a).lerp(new THREE.Vector3(...b),.86).toArray(),b,.075,.046,darkTip);
  }
  for(let i=0;i<6;i++) capsuleBetween(wing,[-.08+i*.035,.21+i*.038,side*(.28+i*.22)],[.30+i*.045,.29+i*.047,side*(.48+i*.23)],.135,.075,featherWhite);
}

// Floating, broken strokes on the sea, rather than a grid of identical waves.
const seaStrokes=new THREE.Group();scene.add(seaStrokes);
const strokeMat=new THREE.MeshBasicMaterial({color:'#b4e8d5',transparent:true,opacity:.36});
for(let i=0;i<100;i++) {
  const x=(random()-.5)*39,z=-8+random()*30;
  if(Math.abs(x)<3 && z<5) continue;
  const len=.18+random()*1.1, pts=[];
  for(let j=0;j<=8;j++)pts.push([x+len*(j/8-.5),-.005+Math.sin(j/8*Math.PI)*.012,z+Math.sin(j/8*Math.PI)*.08]);
  curveTube(seaStrokes,pts,.009+random()*.009,strokeMat,10);
}
const wake=new THREE.Group();scene.add(wake);
const wakePieces=[];
for(let i=0;i<75;i++) {
  const k=i/74, side=i%2?1:-1;
  const x=-2.0+k*6.3,z=2.15+side*(.50+k*.7);
  const r=.03+random()*.07;
  const mesh=ellipsoid(wake,i%4?foamMat:foamShade,[x,.06+random()*.055,z],[r*(1.2+random()*2),r*.35,r*.8]);
  wakePieces.push({mesh,x,z,phase:random()*Math.PI*2});
}
for(const side of [-1,1])curveTube(wake,[[-2.25,.05,2.15+side*.18],[-1.4,.07,2.15+side*.6],[.5,.04,2.15+side*.70],[2.4,.015,2.15+side*1.05],[4.2,.01,2.15+side*1.2]],.018,foamShade,50);
// A few graphic distant birds give the horizon a sense of scale.
const distantMat=new THREE.MeshBasicMaterial({color:'#5b8274'});
for(let i=0;i<3;i++) {
  const x=-5+i*1.1,y=4.4+Math.sin(i*2)*.25,z=-12-i*.8;
  curveTube(scene,[[x-.18,y+.06,z],[x-.08,y+.07,z],[x,y,z],[x+.10,y+.08,z],[x+.20,y+.10,z]],.012,distantMat,16);
}

// Subtle film grain, generated once with no external image dependencies.
const grainCanvas=document.createElement('canvas');grainCanvas.width=grainCanvas.height=160;
const ctx=grainCanvas.getContext('2d');const grain=ctx.createImageData(160,160);
for(let i=0;i<grain.data.length;i+=4){const v=Math.floor(random()*255);grain.data[i]=grain.data[i+1]=grain.data[i+2]=v;grain.data[i+3]=65;}
ctx.putImageData(grain,0,0);document.querySelector('.grain').style.backgroundImage=`url(${grainCanvas.toDataURL()})`;

function resize(){
  const w=innerWidth,h=innerHeight,portrait=w/h<.85;
  renderer.setSize(w,h);camera.aspect=w/h;
  camera.fov=portrait?44:37;
  const dist=portrait?23:19.5;
  target.set(portrait?-.1:-1.7,portrait?2.2:1.65,0);
  camera.position.copy(target).addScaledVector(viewDirection,dist);
  camera.lookAt(target);camera.updateProjectionMatrix();
  sun.quaternion.copy(camera.quaternion);sunRing.quaternion.copy(camera.quaternion);
  if(portrait){sun.position.set(6.5,5.4,-9.5);}else{sun.position.set(5.7,5.0,-9.5);}sunRing.position.copy(sun.position);
}
addEventListener('resize',resize);resize();
const clock=new THREE.Clock();
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
function animate(){
  const t=clock.getElapsedTime()*(reduced?.2:1);
  surfer.position.y=.015+Math.sin(t*1.5)*.035;
  surfer.position.x=-.15+Math.sin(t*.65)*.18;
  surfer.rotation.y=Math.sin(t*.75)*.045;
  boardPivot.rotation.x=Math.sin(t*1.3)*.035;
  boardPivot.rotation.z=.035+Math.sin(t*1.5+.4)*.035;
  bird.rotation.x=Math.sin(t*1.3+.7)*-.022;
  bird.rotation.z=Math.sin(t*1.5-.4)*-.035;
  wings.forEach((wing,i)=>{wing.rotation.x=(i===0?.20:-.08)+Math.sin(t*1.2+i*.4)*.055;wing.rotation.y=i===0?.55:0;wing.rotation.z=Math.sin(t*.9)*.025;});
  waveRoot.position.y=Math.sin(t*.7)*.055;
  waveRoot.rotation.z=Math.sin(t*.5)*.003;
  if(seaMat.userData.shader)seaMat.userData.shader.uniforms.uTime.value=t;
  for(let i=0;i<sprayCount;i++){
    const s=spraySeeds[i],life=(s.phase+t*s.speed)%1,p=wavePoint(s.x,.94);
    sprayArray[i*3]=p.x+life*.4;
    sprayArray[i*3+1]=p.y+Math.sin(life*Math.PI)*(.3+s.drift);
    sprayArray[i*3+2]=p.z+life*.65;
  }
  sprayGeo.attributes.position.needsUpdate=true;
  wakePieces.forEach(({mesh,x,z,phase})=>{mesh.position.x=x+Math.sin(t+phase)*.055;mesh.position.y=.07+Math.sin(t*1.7+phase)*.018;mesh.scale.z= .045+Math.sin(t+phase)*.012;});
  renderer.render(scene,camera);
  requestAnimationFrame(animate);
}
animate();
