import * as THREE from "three";

/* ------------------------------------------------------------------ */
/* Renderer / scene / camera                                           */
/* ------------------------------------------------------------------ */

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xffb37a, 40, 160);

const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 500);
camera.position.set(0, 6, 18);

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

/* ------------------------------------------------------------------ */
/* Sky dome (sunset gradient) + sun                                    */
/* ------------------------------------------------------------------ */

const sky = new THREE.Mesh(
  new THREE.SphereGeometry(200, 32, 24),
  new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {},
    vertexShader: /* glsl */ `
      varying vec3 vPos;
      void main() {
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      varying vec3 vPos;
      void main() {
        float h = normalize(vPos).y;              // -1..1
        vec3 horizon = vec3(1.00, 0.66, 0.42);    // warm orange
        vec3 mid     = vec3(0.98, 0.55, 0.45);
        vec3 zenith  = vec3(0.16, 0.24, 0.52);    // dusk blue
        vec3 c = mix(horizon, mid, smoothstep(-0.05, 0.25, h));
        c = mix(c, zenith, smoothstep(0.15, 0.75, h));
        // sun glow around -Z direction
        vec3 sunDir = normalize(vec3(0.0, 0.12, -1.0));
        float d = max(dot(normalize(vPos), sunDir), 0.0);
        c += vec3(1.0, 0.75, 0.45) * pow(d, 60.0) * 1.2;  // hot core
        c += vec3(1.0, 0.60, 0.30) * pow(d, 8.0) * 0.35;  // halo
        gl_FragColor = vec4(c, 1.0);
      }
    `,
  })
);
scene.add(sky);

/* Lights ------------------------------------------------------------- */

const sunLight = new THREE.DirectionalLight(0xffd9a0, 2.0);
sunLight.position.set(0, 14, -40);
scene.add(sunLight);

scene.add(new THREE.HemisphereLight(0xffc6a0, 0x1b3a5c, 1.1));
scene.add(new THREE.AmbientLight(0x5566aa, 0.4));

/* ------------------------------------------------------------------ */
/* Ocean: a big plane displaced by Gerstner-ish waves in the shader    */
/* ------------------------------------------------------------------ */

const OCEAN_SIZE = 300;
const oceanGeo = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, 180, 180);
oceanGeo.rotateX(-Math.PI / 2);

const oceanUniforms = {
  uTime: { value: 0 },
};

const ocean = new THREE.Mesh(
  oceanGeo,
  new THREE.ShaderMaterial({
    uniforms: oceanUniforms,
    fog: true,
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying float vHeight;
      varying vec3 vWorld;

      // layered travelling sine waves (looks like rolling swell)
      float waveHeight(vec2 p) {
        float h = 0.0;
        h += sin(p.x * 0.12 + uTime * 0.9) * 1.4;
        h += sin(p.x * 0.07 - uTime * 0.6 + p.y * 0.05) * 1.0;
        h += sin(p.x * 0.31 + uTime * 1.7) * 0.35;
        h += sin((p.x + p.y) * 0.22 - uTime * 1.1) * 0.45;
        return h;
      }

      void main() {
        vec3 pos = position;
        float h = waveHeight(pos.xz);
        pos.y += h;

        // crude normal from finite differences
        float eps = 1.0;
        float hx = waveHeight(pos.xz + vec2(eps, 0.0));
        float hz = waveHeight(pos.xz + vec2(0.0, eps));
        vec3 n = normalize(vec3(h - hx, eps, h - hz));

        vHeight = h;
        vWorld = (modelMatrix * vec4(pos, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      #include <fog_pars_fragment>
      varying float vHeight;
      varying vec3 vWorld;
      uniform float uTime;

      void main() {
        vec3 sunDir = normalize(vec3(0.0, 0.12, -1.0));

        vec3 deep    = vec3(0.05, 0.22, 0.42);
        vec3 shallow = vec3(0.15, 0.55, 0.70);
        vec3 foam    = vec3(1.0, 0.95, 0.9);

        float crest = smoothstep(0.9, 2.6, vHeight);
        vec3 col = mix(deep, shallow, smoothstep(-2.0, 1.5, vHeight));

        // sparkle stripes
        float sparkle = sin(vWorld.x * 2.3 + vWorld.z * 0.5 + uTime * 2.0);
        col += vec3(0.10, 0.08, 0.05) * smoothstep(0.6, 1.0, sparkle);

        // foam on crests, banded a bit
        float band = 0.75 + 0.25 * sin(vWorld.x * 1.7 + uTime * 2.2);
        col = mix(col, foam, crest * band * 0.85);

        // sun glitter path towards -Z
        vec3 view = normalize(vWorld - cameraPosition);
        float spec = pow(max(dot(reflect(view, normalize(vec3(0.0,1.0,0.0))), -sunDir), 0.0), 8.0);
        col += vec3(1.0, 0.7, 0.4) * spec * 0.5;

        gl_FragColor = vec4(col, 1.0);
        #include <fog_fragment>
      }
    `,
  })
);
scene.add(ocean);

/* A few drifting clouds (flattened fuzzy sprites made of spheres) --- */

const clouds = new THREE.Group();
const cloudMat = new THREE.MeshBasicMaterial({
  color: 0xffe0c4,
  transparent: true,
  opacity: 0.85,
  fog: false,
});
for (let i = 0; i < 7; i++) {
  const cloud = new THREE.Group();
  const puffs = 4 + Math.floor(Math.random() * 3);
  for (let j = 0; j < puffs; j++) {
    const r = 1.6 + Math.random() * 2.2;
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 10), cloudMat);
    puff.position.set((j - puffs / 2) * 2.4 + Math.random(), Math.random() * 1.2, (Math.random() - 0.5) * 2);
    puff.scale.y = 0.55;
    cloud.add(puff);
  }
  const ang = (i / 7) * Math.PI * 2 + Math.random() * 0.5;
  const dist = 90 + Math.random() * 60;
  cloud.position.set(Math.cos(ang) * dist, 22 + Math.random() * 18, Math.sin(ang) * dist - 20);
  cloud.userData.speed = 0.4 + Math.random() * 0.5;
  clouds.add(cloud);
}
scene.add(clouds);

/* ------------------------------------------------------------------ */
/* The pelican + surfboard                                             */
/* ------------------------------------------------------------------ */

const pelican = new THREE.Group();

const bodyMat = new THREE.MeshStandardMaterial({ color: 0xf5f0e6, roughness: 0.8 });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x2b2b33, roughness: 0.6 });
const beakMat = new THREE.MeshStandardMaterial({ color: 0xffb347, roughness: 0.45 });
const pouchMat = new THREE.MeshStandardMaterial({ color: 0xff8c5a, roughness: 0.6 });

// body
const body = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 18), bodyMat);
body.scale.set(1.0, 0.85, 1.5);
pelican.add(body);

// tail feathers
const tail = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.2, 8), darkMat);
tail.rotation.x = Math.PI / 2.3;
tail.position.set(0, 0.05, 1.6);
pelican.add(tail);

// neck
const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.3, 1.1, 12), bodyMat);
neck.position.set(0, 0.55, -1.0);
neck.rotation.x = -0.5;
pelican.add(neck);

// head
const head = new THREE.Group();
head.position.set(0, 1.05, -1.45);
const skull = new THREE.Mesh(new THREE.SphereGeometry(0.32, 20, 16), bodyMat);
head.add(skull);

// big beak: upper mandible
const upper = new THREE.Mesh(new THREE.ConeGeometry(0.16, 1.3, 10), beakMat);
upper.rotation.x = -Math.PI / 2;
upper.position.set(0, 0.02, -0.75);
head.add(upper);

// pouch hanging under the beak
const pouch = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), pouchMat);
pouch.scale.set(0.9, 0.7, 1.6);
pouch.position.set(0, -0.14, -0.65);
head.add(pouch);

// eye
const eyeGeo = new THREE.SphereGeometry(0.06, 10, 8);
const eyeMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 });
for (const s of [-1, 1]) {
  const eye = new THREE.Mesh(eyeGeo, eyeMat);
  eye.position.set(s * 0.2, 0.1, -0.18);
  head.add(eye);
}
pelican.add(head);

// wings — pivot at shoulder so they can flap
function makeWing(side) {
  const wing = new THREE.Group();
  wing.position.set(side * 0.8, 0.35, -0.1);

  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.quadraticCurveTo(2.2, 0.9, 3.4, 0.35); // leading edge out to tip
  shape.quadraticCurveTo(2.2, -0.35, 1.4, -0.55); // trailing edge back
  shape.quadraticCurveTo(0.6, -0.65, 0, -0.4);
  shape.closePath();

  const geo = new THREE.ShapeGeometry(shape, 16);
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    color: 0xe8e2d4, roughness: 0.85, side: THREE.DoubleSide,
  }));
  mesh.rotation.x = -Math.PI / 2;
  mesh.scale.x = side;
  wing.add(mesh);

  // primary feather tips (dark)
  for (let i = 0; i < 5; i++) {
    const f = new THREE.Mesh(
      new THREE.ConeGeometry(0.07, 0.9, 6),
      darkMat
    );
    f.rotation.x = -Math.PI / 2;
    f.rotation.z = Math.PI / 2;
    f.position.set(side * (2.2 + i * 0.25), 0, 0.15 + i * 0.1);
    wing.add(f);
  }
  return wing;
}
const wingL = makeWing(1);
const wingR = makeWing(-1);
pelican.add(wingL, wingR);

// webbed feet resting on the board
const footMat = new THREE.MeshStandardMaterial({ color: 0xffa060, roughness: 0.6 });
for (const s of [-1, 1]) {
  const foot = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.06, 0.6), footMat);
  foot.position.set(s * 0.35, -0.85, 0.3);
  pelican.add(foot);
}

// ---------------- surfboard ----------------
const surfboard = new THREE.Group();

const boardShape = new THREE.Shape();
const L = 3.6; // half-length
boardShape.moveTo(0, L);
boardShape.quadraticCurveTo(0.55, L * 0.4, 0.5, 0);
boardShape.quadraticCurveTo(0.45, -L * 0.6, 0, -L);
boardShape.quadraticCurveTo(-0.45, -L * 0.6, -0.5, 0);
boardShape.quadraticCurveTo(-0.55, L * 0.4, 0, L);
boardShape.closePath();

const boardGeo = new THREE.ExtrudeGeometry(boardShape, {
  depth: 0.18,
  bevelEnabled: true,
  bevelSize: 0.1,
  bevelThickness: 0.08,
  bevelSegments: 3,
  curveSegments: 24,
});
boardGeo.rotateX(Math.PI / 2);
const board = new THREE.Mesh(boardGeo, new THREE.MeshStandardMaterial({
  color: 0xffd23f, roughness: 0.35, metalness: 0.1,
}));
surfboard.add(board);

// racing stripe
const stripe = new THREE.Mesh(
  new THREE.BoxGeometry(0.12, 0.02, 6.2),
  new THREE.MeshStandardMaterial({ color: 0xe63946, roughness: 0.4 })
);
stripe.position.y = 0.14;
surfboard.add(stripe);

// fin under the tail
const fin = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.7, 8), darkMat);
fin.rotation.x = Math.PI;
fin.position.set(0, -0.35, 2.6);
surfboard.add(fin);

// stack: board, then pelican on top
const rider = new THREE.Group();
pelican.position.y = 1.05;
rider.add(surfboard, pelican);
scene.add(rider);

/* ------------------------------------------------------------------ */
/* Animation loop                                                      */
/* ------------------------------------------------------------------ */

const clock = new THREE.Clock();

function animate() {
  const t = clock.getElapsedTime();
  const dt = Math.min(clock.getDelta(), 0.05);

  oceanUniforms.uTime.value = t;

  // rider surfs along a rolling path: carve left/right, ride the swell
  const carveX = Math.sin(t * 0.5) * 6.0;
  const carveZ = -4 + Math.sin(t * 0.33) * 2.0;

  // same wave function as the shader, so the board sits on the water
  const waveHeight = (x, z, time) =>
    Math.sin(x * 0.12 + time * 0.9) * 1.4 +
    Math.sin(x * 0.07 - time * 0.6 + z * 0.05) * 1.0 +
    Math.sin(x * 0.31 + time * 1.7) * 0.35 +
    Math.sin((x + z) * 0.22 - time * 1.1) * 0.45;

  const x = carveX;
  const z = carveZ;
  const y = waveHeight(x, z, t);

  rider.position.set(x, y - 0.05, z);

  // slope-riding tilt: sample wave ahead to pitch with the wave face
  const ahead = waveHeight(x, z - 2.0, t);
  const behind = waveHeight(x, z + 2.0, t);
  rider.rotation.x = THREE.MathUtils.lerp(
    rider.rotation.x,
    Math.atan2(ahead - behind, 4.0) * 0.8,
    0.08
  );

  // banking into the carve
  const carveVel = Math.cos(t * 0.5) * 0.5 * 6.0;
  rider.rotation.z = THREE.MathUtils.lerp(
    rider.rotation.z,
    THREE.MathUtils.clamp(-carveVel * 0.09, -0.5, 0.5),
    0.08
  );

  // pelican counterbalances with its body, head bobs, tail kicks
  pelican.rotation.z = -rider.rotation.z * 0.7;
  pelican.rotation.x = Math.sin(t * 1.3) * 0.06;

  head.position.y = 1.05 + Math.sin(t * 2.1) * 0.05;
  head.rotation.x = Math.sin(t * 1.7) * 0.08 - 0.05;
  head.rotation.y = Math.sin(t * 0.8) * 0.15;

  tail.rotation.z = Math.sin(t * 3.0) * 0.15;

  // lazy flapping wings
  const flap = Math.sin(t * 2.4);
  wingL.rotation.z = 0.15 + flap * 0.55;
  wingR.rotation.z = -0.15 - flap * 0.55;
  wingL.rotation.y = Math.sin(t * 2.4 + 0.5) * 0.1;
  wingR.rotation.y = -Math.sin(t * 2.4 + 0.5) * 0.1;

  // drifting clouds
  for (const c of clouds.children) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 160) c.position.x = -160;
  }

  // camera gently tracks the rider
  const camTarget = new THREE.Vector3(x * 0.6, y + 2.5, z + 16);
  camera.position.lerp(camTarget, 0.02);
  camera.lookAt(x * 0.8, y + 1.2, z - 2);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();
