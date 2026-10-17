import * as THREE from "three";

// Wave numbers are duplicated in the vertex shader below. Keep them identical.
const CREST_AMP = 1.55;
const CREST_K = 0.072;
const CREST_W = 0.16;
const WALL_AMP = 3.35;
const FACE_WIDTH = 4.6;
const FACE_POWER = 1.7;
const SIGMA_BACK = 1.45;
const LIP_AMP = 0.36;
const LIP_CENTER = 0.28;
const LIP_SIGMA = 0.55;
const CURL_AMP = 1.15;
const CURL_CENTER = 0.05;
const CURL_SIGMA = 0.78;

const SIZE_X = 176;
const SIZE_Z = 148;
const SEG_X = 200;
const SEG_Z = 320;

export function crestZ(x, t) {
  return CREST_AMP * Math.sin(CREST_K * x - CREST_W * t);
}

function chop(x, z, t) {
  return (
    0.15 * Math.sin(0.17 * x + 0.52 * t) +
    0.1 * Math.sin(0.31 * z - 0.68 * t + 0.4) +
    0.055 * Math.sin(0.48 * x + 0.27 * z + 1.15 * t) +
    0.03 * Math.sin(1.02 * x - 0.66 * z - 1.7 * t)
  );
}

export function oceanHeight(x, z, t) {
  const dz = z - crestZ(x, t);
  let wall;
  if (dz >= 0) {
    wall = WALL_AMP * Math.exp(-(dz * dz) / (2 * SIGMA_BACK * SIGMA_BACK));
  } else {
    const u = Math.min(1, Math.max(0, (dz + FACE_WIDTH) / FACE_WIDTH));
    const e = Math.pow(u, FACE_POWER);
    const s = e * e * (3 - 2 * e);
    wall = WALL_AMP * s;
  }
  const lipDz = dz + LIP_CENTER;
  const lip = LIP_AMP * Math.exp(-(lipDz * lipDz) / (2 * LIP_SIGMA * LIP_SIGMA));
  return chop(x, z, t) + wall + lip;
}

export function curlOffset(x, z, t, h) {
  const dz = z - crestZ(x, t);
  const u = dz + CURL_CENTER;
  const band = Math.exp(-(u * u) / (2 * CURL_SIGMA * CURL_SIGMA));
  const grow = smoothstep(1.35, 2.7, h);
  return -CURL_AMP * band * grow;
}

function smoothstep(e0, e1, x) {
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
}

// Height of the visible surface at a world (x, z), inverting the lip's z-curl.
export function visualHeight(x, z, t) {
  let z0 = z;
  for (let i = 0; i < 3; i++) {
    const h = oceanHeight(x, z0, t);
    z0 = z - curlOffset(x, z0, t, h);
  }
  return oceanHeight(x, z0, t);
}

export function createRideState() {
  return {
    position: new THREE.Vector3(),
    normal: new THREE.Vector3(),
  };
}

const _sample = new THREE.Vector3();

export function sampleSurface(x, z, t, out) {
  const y = visualHeight(x, z, t);
  const e = 0.45;
  const ddx = (visualHeight(x + e, z, t) - visualHeight(x - e, z, t)) / (2 * e);
  const ddz = (visualHeight(x, z + e, t) - visualHeight(x, z - e, t)) / (2 * e);
  _sample.set(-ddx, 1, -ddz).normalize();
  out.position.set(x, y, z);
  out.normal.copy(_sample);
  return out;
}

export function rideState(t, out) {
  const x = t * 3.65;
  const crest = crestZ(x, t);
  const carve = Math.sin(t * 0.31) * 0.22 + Math.sin(t * 0.11) * 0.1;
  const down = Math.min(3.05, Math.max(2.2, 2.58 - carve));
  return sampleSurface(x, crest - down, t, out);
}

const TRAIL = 28;

const waterVertex = /* glsl */ `
uniform float uTime;
varying vec3 vWorld;
varying vec3 vNormal;
varying float vHeight;
varying float vFoam;

float crestZ(float x, float t) {
  return ${CREST_AMP.toFixed(4)} * sin(${CREST_K.toFixed(4)} * x - ${CREST_W.toFixed(4)} * t);
}

float chop(float x, float z, float t) {
  return
    0.15 * sin(0.17 * x + 0.52 * t) +
    0.10 * sin(0.31 * z - 0.68 * t + 0.40) +
    0.055 * sin(0.48 * x + 0.27 * z + 1.15 * t) +
    0.030 * sin(1.02 * x - 0.66 * z - 1.70 * t);
}

float oceanHeight(float x, float z, float t) {
  float dz = z - crestZ(x, t);
  float wall;
  if (dz >= 0.0) {
    wall = ${WALL_AMP.toFixed(4)} * exp(-(dz * dz) / (2.0 * ${SIGMA_BACK.toFixed(4)} * ${SIGMA_BACK.toFixed(4)}));
  } else {
    float u = clamp((dz + ${FACE_WIDTH.toFixed(4)}) / ${FACE_WIDTH.toFixed(4)}, 0.0, 1.0);
    float e = pow(u, ${FACE_POWER.toFixed(4)});
    float s = e * e * (3.0 - 2.0 * e);
    wall = ${WALL_AMP.toFixed(4)} * s;
  }
  float lipDz = dz + ${LIP_CENTER.toFixed(4)};
  float lip = ${LIP_AMP.toFixed(4)} * exp(-(lipDz * lipDz) / (2.0 * ${LIP_SIGMA.toFixed(4)} * ${LIP_SIGMA.toFixed(4)}));
  return chop(x, z, t) + wall + lip;
}

float curlOffset(float x, float z, float t, float h) {
  float dz = z - crestZ(x, t);
  float u = dz + ${CURL_CENTER.toFixed(4)};
  float band = exp(-(u * u) / (2.0 * ${CURL_SIGMA.toFixed(4)} * ${CURL_SIGMA.toFixed(4)}));
  float grow = smoothstep(1.35, 2.70, h);
  return -${CURL_AMP.toFixed(4)} * band * grow;
}

vec3 displaced(vec2 xz) {
  float h = oceanHeight(xz.x, xz.y, uTime);
  float c = curlOffset(xz.x, xz.y, uTime, h);
  return vec3(xz.x, h, xz.y + c);
}

float lipFoam(float x, float z, float h) {
  float dz = z - crestZ(x, uTime);
  float u = dz + 0.04;
  float band = exp(-(u * u) * 3.4);
  float cap = smoothstep(2.65, 3.4, h);
  return clamp(band * cap, 0.0, 1.0);
}

void main() {
  vec4 world = modelMatrix * vec4(position, 1.0);
  vec2 xz = world.xz;
  vec3 p = displaced(xz);
  float e = 0.4;
  vec3 dx = displaced(xz + vec2(e, 0.0)) - displaced(xz - vec2(e, 0.0));
  vec3 dz = displaced(xz + vec2(0.0, e)) - displaced(xz - vec2(0.0, e));
  vNormal = normalize(cross(dz, dx));
  vWorld = p;
  vHeight = p.y;
  vFoam = lipFoam(xz.x, xz.y, p.y);
  gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
}
`;

const waterFragment = /* glsl */ `
precision highp float;

uniform vec3 uSunDir;
uniform vec3 uCameraPos;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFace;
uniform vec3 uFoamColor;
uniform vec3 uHorizon;
uniform vec2 uFocus;
uniform vec2 uTrail[28];
uniform vec2 uBoardPos;
uniform vec2 uBoardFwd;
uniform vec2 uBoardRight;
uniform float uTime;

varying vec3 vWorld;
varying vec3 vNormal;
varying float vHeight;
varying float vFoam;

float trailFoam() {
  float f = 0.0;
  for (int i = 0; i < 28; i++) {
    float d = distance(vWorld.xz, uTrail[i]);
    float age = 1.0 - float(i) / 28.0;
    f += smoothstep(0.62, 0.0, d) * age;
  }
  return clamp(f, 0.0, 1.0);
}

void main() {
  vec3 N = normalize(vNormal);
  if (!gl_FrontFacing) N = -N;
  vec3 V = normalize(uCameraPos - vWorld);
  vec3 L = normalize(uSunDir);
  vec3 H = normalize(L + V);

  float ndl = max(dot(N, L), 0.0);
  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.4);
  float face = pow(max(dot(N, V), 0.0), 0.55) * smoothstep(0.15, 2.1, vHeight);
  float back = smoothstep(0.35, 2.4, vHeight) * (1.0 - face);

  vec3 col = mix(uDeep, uShallow, clamp(ndl * 0.45 + face * 0.35, 0.0, 1.0));
  col = mix(col, uFace, clamp(face * 0.85, 0.0, 1.0));
  col = mix(col, uDeep * 0.85, clamp(back * 0.25, 0.0, 1.0));

  float spec = pow(max(dot(N, H), 0.0), 90.0);
  float gloss = pow(max(dot(N, H), 0.0), 14.0);
  col += vec3(1.0, 0.86, 0.68) * spec * 0.85;
  col += vec3(1.0, 0.72, 0.5) * gloss * 0.18;
  col = mix(col, vec3(1.0, 0.78, 0.58), fres * 0.42);

  float peel = smoothstep(uFocus.x + 3.0, uFocus.x - 16.0, vWorld.x);
  float lip = vFoam * (0.72 + 0.7 * peel);
  float wake = trailFoam();
  float foam = clamp(max(lip, wake * 0.78), 0.0, 1.0);
  float fizz = 0.82 + 0.18 * sin(vWorld.x * 3.4 + vWorld.z * 2.2 - uTime * 3.5);
  foam *= fizz;
  col = mix(col, uFoamColor, foam);

  vec2 rel = vWorld.xz - uBoardPos;
  float along = dot(rel, uBoardFwd);
  float across = dot(rel, uBoardRight);
  float contact = exp(-along * along / 3.1 - across * across / 0.22);
  col *= 1.0 - contact * 0.42;

  float dist = length(uCameraPos - vWorld);
  float fog = smoothstep(48.0, 125.0, dist);
  col = mix(col, uHorizon, fog);

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createOcean() {
  const geo = new THREE.PlaneGeometry(SIZE_X, SIZE_Z, SEG_X, SEG_Z);
  geo.rotateX(-Math.PI / 2);

  const trail = [];
  for (let i = 0; i < TRAIL; i++) trail.push(new THREE.Vector2(0, -9999));

  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: new THREE.Vector3(0.2, 0.8, 0.1) },
    uCameraPos: { value: new THREE.Vector3() },
    uDeep: { value: new THREE.Color(0x071e30) },
    uShallow: { value: new THREE.Color(0x146e78) },
    uFace: { value: new THREE.Color(0x2a9a90) },
    uFoamColor: { value: new THREE.Color(0xf5fbff) },
    uHorizon: { value: new THREE.Color(0xf2a36a) },
    uFocus: { value: new THREE.Vector2() },
    uTrail: { value: trail },
    uBoardPos: { value: new THREE.Vector2() },
    uBoardFwd: { value: new THREE.Vector2(1, 0) },
    uBoardRight: { value: new THREE.Vector2(0, 1) },
  };

  const mesh = new THREE.Mesh(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: waterVertex,
      fragmentShader: waterFragment,
      side: THREE.DoubleSide,
    }),
  );
  mesh.name = "ocean";
  mesh.receiveShadow = false;
  mesh.castShadow = false;
  mesh.frustumCulled = false;

  const cellX = SIZE_X / SEG_X;
  const cellZ = SIZE_Z / SEG_Z;

  function pushTrail(point) {
    for (let i = TRAIL - 1; i > 0; i--) trail[i].copy(trail[i - 1]);
    trail[0].set(point.x, point.z);
  }

  return {
    mesh,
    uniforms,
    update(t, focus, tailWorld, boardFrame) {
      const ox = Math.round(focus.x / cellX) * cellX;
      const oz = Math.round(focus.z / cellZ) * cellZ;
      mesh.position.set(ox, 0, oz);
      uniforms.uTime.value = t;
      uniforms.uFocus.value.set(focus.x, focus.z);
      if (tailWorld) {
        const last = trail[0];
        if (last.y < -1000 || Math.hypot(tailWorld.x - last.x, tailWorld.z - last.y) > 0.22) {
          pushTrail(tailWorld);
        }
      }
      if (boardFrame) {
        uniforms.uBoardPos.value.set(boardFrame.position.x, boardFrame.position.z);
        uniforms.uBoardFwd.value.set(boardFrame.forward.x, boardFrame.forward.z).normalize();
        uniforms.uBoardRight.value.set(boardFrame.right.x, boardFrame.right.z).normalize();
      }
    },
  };
}
