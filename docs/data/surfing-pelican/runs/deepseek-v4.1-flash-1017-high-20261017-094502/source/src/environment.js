import * as THREE from 'three';
import { WAVE_GLSL, waveHeight } from './waves.js';
import {
  makeCloudTexture,
  makeGlowTexture,
  makeFoamTile,
  rng,
} from './textures.js';

export const SUN_DIR = new THREE.Vector3(-0.5, 0.19, -0.82).normalize();

const COLORS = {
  skyZenith: '#235878',
  skyUpper: '#5f96b0',
  skyHorizonWarm: '#ffc48b',
  skyHorizonCool: '#b8b5c4',
  fog: '#e8bc9d',
  waterDeep: '#063b49',
  waterShallow: '#177c7e',
  foam: '#fff7ea',
};

function wrap(value, min, max) {
  const range = max - min;
  return ((((value - min) % range) + range) % range) + min;
}

function createSky() {
  const uniforms = {
    uSunDir: { value: SUN_DIR.clone() },
    uZenith: { value: new THREE.Color(COLORS.skyZenith) },
    uUpper: { value: new THREE.Color(COLORS.skyUpper) },
    uHorizonWarm: { value: new THREE.Color(COLORS.skyHorizonWarm) },
    uHorizonCool: { value: new THREE.Color(COLORS.skyHorizonCool) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    side: THREE.BackSide,
    depthWrite: false,
    depthTest: false,
    fog: false,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uSunDir;
      uniform vec3 uZenith;
      uniform vec3 uUpper;
      uniform vec3 uHorizonWarm;
      uniform vec3 uHorizonCool;
      varying vec3 vDir;

      void main() {
        vec3 d = normalize(vDir);
        float h = max(d.y, 0.0);
        vec3 sunAzimuth = normalize(vec3(uSunDir.x, 0.0, uSunDir.z));
        vec3 dirAzimuth = normalize(vec3(d.x, 0.0, d.z));
        float sunAz = pow(max(dot(dirAzimuth, sunAzimuth), 0.0), 2.6);
        vec3 horizon = mix(uHorizonCool, uHorizonWarm, sunAz);

        vec3 col = mix(horizon, uUpper, smoothstep(0.0, 0.3, h));
        col = mix(col, uZenith, smoothstep(0.17, 0.9, h));

        float sd = max(dot(d, normalize(uSunDir)), 0.0);
        col += vec3(1.0, 0.84, 0.60) * pow(sd, 1600.0) * 5.0;
        col += vec3(1.0, 0.64, 0.37) * pow(sd, 64.0) * 0.22;
        col += vec3(1.0, 0.68, 0.41) * pow(sd, 8.0) * 0.055;
        col += vec3(1.0, 0.52, 0.28) * exp(-pow((h - 0.025) / 0.055, 2.0)) * 0.055 * (0.25 + sunAz);

        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });

  const mesh = new THREE.Mesh(new THREE.SphereGeometry(470, 48, 32), material);
  mesh.renderOrder = -10;
  mesh.frustumCulled = false;
  return mesh;
}

function createOcean() {
  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: SUN_DIR.clone() },
    uDeep: { value: new THREE.Color(COLORS.waterDeep) },
    uShallow: { value: new THREE.Color(COLORS.waterShallow) },
    uHorizonWarm: { value: new THREE.Color(COLORS.skyHorizonWarm) },
    uHorizonCool: { value: new THREE.Color(COLORS.skyHorizonCool) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    fog: false,
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying vec3 vWorld;
      varying vec3 vNormal;
      varying float vHeight;
      ${WAVE_GLSL}
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        float h = oceanHeight(wp.xz, uTime);
        wp.y += h;
        vec2 g = oceanGradient(wp.xz, uTime);
        vNormal = normalize(vec3(-g.x, 1.0, -g.y));
        vHeight = h;
        vWorld = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform vec3 uSunDir;
      uniform vec3 uDeep;
      uniform vec3 uShallow;
      uniform vec3 uHorizonWarm;
      uniform vec3 uHorizonCool;
      varying vec3 vWorld;
      varying vec3 vNormal;
      varying float vHeight;

      float hash21(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }
      float vnoise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        float a = hash21(i);
        float b = hash21(i + vec2(1.0, 0.0));
        float c = hash21(i + vec2(0.0, 1.0));
        float d = hash21(i + vec2(1.0, 1.0));
        return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
      }
      float fbm(vec2 p) {
        float v = 0.0;
        float a = 0.5;
        mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
        for (int i = 0; i < 4; i++) {
          v += a * vnoise(p);
          p = rot * p * 2.03 + 13.1;
          a *= 0.5;
        }
        return v;
      }

      void main() {
        vec3 V = normalize(cameraPosition - vWorld);
        vec3 N = normalize(vNormal);
        vec2 q = vWorld.xz;
        float t = uTime;

        // fine ripples
        float c1 = cos(q.x * 1.9 + q.y * 0.8 + t * 1.55);
        float c2 = cos(q.x * 3.7 - q.y * 2.4 - t * 2.15);
        float c3 = cos(q.x * 7.3 + q.y * 5.1 + t * 3.2);
        vec2 detail = vec2(1.9, 0.8) * c1 * 0.012
                    + vec2(3.7, -2.4) * c2 * 0.0048
                    + vec2(7.3, 5.1) * c3 * 0.0016;
        N = normalize(N + vec3(-detail.x, 0.0, -detail.y));

        float facing = clamp(dot(N, V), 0.0, 1.0);
        float fres = pow(1.0 - facing, 4.0);
        fres = mix(0.045, 1.0, fres);

        vec3 R = reflect(-V, N);
        float up = clamp(R.y, 0.0, 1.0);
        vec3 skyRef = mix(uHorizonWarm, vec3(0.18, 0.47, 0.58), smoothstep(0.0, 0.55, up));

        float crestMix = smoothstep(-0.32, 0.5, vHeight);
        vec3 water = mix(uDeep, uShallow, crestMix * 0.5);
        water = mix(water, skyRef * 0.72, fres * 0.72);

        vec3 L = normalize(uSunDir);
        vec3 H = normalize(L + V);
        float nh = max(dot(N, H), 0.0);
        float spec = pow(nh, 700.0) * 2.4 * (0.6 + 0.8 * fbm(q * 7.0 + t * 0.25));
        float sheen = pow(nh, 22.0) * 0.055;
        vec3 sunTint = vec3(1.0, 0.68, 0.38);
        water += sunTint * (spec + sheen * max(dot(N, L), 0.0));

        // whitecaps: broad crest bands broken up with noise
        float n1 = fbm(q * 0.5 + vec2(t * 0.045, -t * 0.025));
        float n2 = fbm(q * 2.2 + vec2(-t * 0.09, t * 0.06));
        float crest = smoothstep(0.24, 0.56, vHeight + (n1 - 0.5) * 0.2);
        float broken = smoothstep(0.46, 0.8, n2 + crest * 0.24);
        float foam = crest * broken;
        float streak = smoothstep(0.68, 0.92, fbm(vec2(q.x * 0.22 + q.y * 0.06, q.y * 1.3 - t * 0.12)));
        foam += streak * smoothstep(-0.05, 0.28, vHeight) * 0.1;
        float farFoam = 1.0 - smoothstep(110.0, 250.0, distance(cameraPosition, vWorld));
        foam = clamp(foam, 0.0, 0.62) * farFoam;
        water = mix(water, vec3(0.93, 0.95, 0.92), foam);

        // atmospheric haze, warmer toward the sun
        vec3 viewDir = normalize(vWorld - cameraPosition);
        vec3 viewAz = normalize(vec3(viewDir.x, 0.0, viewDir.z));
        vec3 sunAz = normalize(vec3(L.x, 0.0, L.z));
        float towardSun = pow(max(dot(viewAz, sunAz), 0.0), 2.0);
        vec3 hazeCol = mix(uHorizonCool, uHorizonWarm, towardSun);
        float dist = distance(cameraPosition, vWorld);
        float haze = 1.0 - exp(-pow(dist * 0.0051, 2.0));
        water = mix(water, hazeCol, haze);

        gl_FragColor = vec4(water, 1.0);
      }
    `,
  });

  const geometry = new THREE.PlaneGeometry(560, 560, 220, 220);
  geometry.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return { mesh, uniforms };
}

function makeCloud(rand, scale) {
  const group = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#f5d4c4'),
    roughness: 1.0,
    metalness: 0.0,
    emissive: new THREE.Color('#77372f'),
    emissiveIntensity: 0.32,
  });
  const puffGeo = new THREE.SphereGeometry(1, 16, 12);
  const count = 5 + Math.floor(rand() * 5);
  for (let i = 0; i < count; i++) {
    const puff = new THREE.Mesh(puffGeo, mat);
    const x = (rand() - 0.5) * 2.4;
    const y = (rand() - 0.3) * 0.55;
    const z = (rand() - 0.5) * 0.9;
    const s = 0.4 + rand() * 0.55;
    puff.position.set(x, y, z);
    puff.scale.set(s * (0.9 + rand() * 0.4), s * (0.55 + rand() * 0.3), s * (0.8 + rand() * 0.3));
    group.add(puff);
  }
  group.scale.setScalar(scale);
  return group;
}

function createPalm(height, lean, rand) {
  const group = new THREE.Group();
  const trunkMat = new THREE.MeshStandardMaterial({
    color: '#4d4a3f',
    roughness: 1,
  });
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.3, height, 6), trunkMat);
  trunk.position.y = height * 0.5;
  trunk.rotation.z = lean;
  group.add(trunk);

  const leafMat = new THREE.MeshStandardMaterial({
    color: '#284b48',
    roughness: 0.95,
    side: THREE.DoubleSide,
  });
  const leafGeo = new THREE.ConeGeometry(0.75, 3.6, 3, 1, true);
  for (let i = 0; i < 7; i++) {
    const leaf = new THREE.Mesh(leafGeo, leafMat);
    leaf.position.set(Math.sin(lean) * height, height, 0);
    leaf.rotation.z = Math.PI * 0.32 + lean;
    leaf.rotation.y = (i / 7) * Math.PI * 2 + rand() * 0.3;
    leaf.scale.set(1, 1, 0.18);
    group.add(leaf);
  }
  return group;
}

function createIsland(seed, opts = {}) {
  const rand = rng(seed);
  const group = new THREE.Group();
  const rockMat = new THREE.MeshStandardMaterial({
    color: '#4d6873',
    roughness: 1,
    metalness: 0,
    emissive: new THREE.Color('#1c2c34'),
    emissiveIntensity: 0.55,
  });
  const hillMat = new THREE.MeshStandardMaterial({
    color: '#516a6d',
    roughness: 1,
    metalness: 0,
    emissive: new THREE.Color('#25332f'),
    emissiveIntensity: 0.5,
  });

  const base = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), rockMat);
  base.scale.set(opts.width ?? 26, 6, opts.depth ?? 15);
  base.position.y = -1.5;
  group.add(base);

  const hillCount = 2 + Math.floor(rand() * 2);
  for (let i = 0; i < hillCount; i++) {
    const h = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), hillMat);
    h.scale.set(8 + rand() * 10, 7 + rand() * 8, 8 + rand() * 6);
    h.position.set((rand() - 0.5) * 22, 2 + rand() * 3, (rand() - 0.5) * 10);
    group.add(h);
  }

  // A couple of angular peaks keep the silhouettes from looking like domes.
  const peakMat = new THREE.MeshStandardMaterial({
    color: '#455f61',
    roughness: 1,
    metalness: 0,
    flatShading: true,
    emissive: new THREE.Color('#1d2b2c'),
    emissiveIntensity: 0.5,
  });
  for (let i = 0; i < 2; i++) {
    const h = 10 + rand() * 12;
    const peak = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 7, 1), peakMat);
    peak.scale.set(5 + rand() * 5, h, 5 + rand() * 4);
    peak.position.set((rand() - 0.5) * 20, 4 + h * 0.42, (rand() - 0.5) * 9);
    peak.rotation.y = rand() * Math.PI;
    group.add(peak);
  }

  if (opts.palms !== false) {
    for (let i = 0; i < 3; i++) {
      const palm = createPalm(7 + rand() * 5, (rand() - 0.5) * 0.22, rand);
      palm.position.set((rand() - 0.5) * 20, 5 + rand() * 3, (rand() - 0.5) * 8);
      group.add(palm);
    }
  }

  if (opts.lighthouse) {
    const towerMat = new THREE.MeshStandardMaterial({ color: '#efe4d2', roughness: 0.8 });
    const redMat = new THREE.MeshStandardMaterial({ color: '#c95b43', roughness: 0.8 });
    const tower = new THREE.Group();
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.4, 8, 12), towerMat);
    body.position.y = 4;
    tower.add(body);
    const stripe = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.15, 1.1, 12), redMat);
    stripe.position.y = 5.6;
    tower.add(stripe);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(1.15, 1.6, 12), redMat);
    roof.position.y = 8.8;
    tower.add(roof);
    const lamp = new THREE.Mesh(
      new THREE.SphereGeometry(0.42, 12, 10),
      new THREE.MeshBasicMaterial({ color: '#ffdba0' }),
    );
    lamp.position.y = 7.9;
    tower.add(lamp);
    tower.position.set(8, 7, -1);
    group.add(tower);

    const glow = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: makeGlowTexture(),
        color: '#ffce8a',
        transparent: true,
        opacity: 0.55,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        fog: false,
      }),
    );
    glow.position.set(8, 14.9, -1);
    glow.scale.setScalar(8);
    group.add(glow);
  }

  return group;
}

function createSailboat() {
  const group = new THREE.Group();
  const hullMat = new THREE.MeshStandardMaterial({ color: '#334f58', roughness: 0.7 });
  const sailMat = new THREE.MeshBasicMaterial({
    color: '#ffe7cb',
    side: THREE.DoubleSide,
    fog: true,
  });

  const hull = new THREE.Mesh(new THREE.CapsuleGeometry(0.7, 3.6, 5, 10), hullMat);
  hull.rotation.z = Math.PI / 2;
  hull.scale.set(1, 1, 0.55);
  hull.position.y = 0.4;
  group.add(hull);

  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 6, 6), hullMat);
  mast.position.set(0.15, 3.4, 0);
  group.add(mast);

  const sailShape = new THREE.Shape();
  sailShape.moveTo(0, 0);
  sailShape.lineTo(0, 5.2);
  sailShape.quadraticCurveTo(1.8, 3.4, 1.95, 0.1);
  sailShape.closePath();
  const sailGeo = new THREE.ShapeGeometry(sailShape);
  sailGeo.rotateY(Math.PI / 2);
  const sail = new THREE.Mesh(sailGeo, sailMat);
  sail.position.set(0.12, 1.2, 0);
  group.add(sail);

  const jibShape = new THREE.Shape();
  jibShape.moveTo(0, 0.9);
  jibShape.lineTo(-0.3, 4.9);
  jibShape.quadraticCurveTo(-1.7, 3.2, -1.9, 0.4);
  jibShape.closePath();
  const jibGeo = new THREE.ShapeGeometry(jibShape);
  jibGeo.rotateY(Math.PI / 2);
  const jib = new THREE.Mesh(jibGeo, sailMat);
  jib.position.set(0.18, 1.2, 0.02);
  group.add(jib);

  group.scale.setScalar(1.7);
  return group;
}

function createGull(rand) {
  const group = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({
    color: '#4c565b',
    side: THREE.DoubleSide,
    fog: true,
  });
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, 0);
  wingShape.quadraticCurveTo(0.9, 0.22, 1.55, -0.05);
  wingShape.quadraticCurveTo(0.9, -0.12, 0, -0.12);
  wingShape.closePath();
  const wingGeo = new THREE.ShapeGeometry(wingShape);

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.13, 8, 6), mat);
  body.scale.set(0.7, 0.5, 2.0);
  group.add(body);

  const wr = new THREE.Mesh(wingGeo, mat);
  wr.rotation.y = -Math.PI / 2;
  wr.position.set(0, 0, 0);
  const wl = new THREE.Mesh(wingGeo, mat);
  wl.rotation.y = Math.PI / 2;
  wl.scale.x = -1;
  wl.position.set(0, 0, 0);
  group.add(wr, wl);

  group.userData = {
    wr,
    wl,
    phase: rand() * Math.PI * 2,
    speed: 0.7 + rand() * 0.6,
  };
  return group;
}

export function createEnvironment(scene, camera) {
  scene.fog = new THREE.FogExp2(COLORS.fog, 0.0049);

  const sky = createSky();
  scene.add(sky);

  const { mesh: ocean, uniforms: oceanUniforms } = createOcean();
  scene.add(ocean);

  const glowTex = makeGlowTexture();
  const sunGlow = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTex,
      color: '#ffcf96',
      transparent: true,
      opacity: 0.42,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      depthTest: true,
      fog: false,
    }),
  );
  sunGlow.scale.setScalar(88);
  scene.add(sunGlow);

  const sunCoreMat = new THREE.SpriteMaterial({
    map: glowTex,
    transparent: true,
    opacity: 1.0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: true,
    fog: false,
  });
  sunCoreMat.color.setRGB(2.2, 1.9, 1.5);
  const sunCore = new THREE.Sprite(sunCoreMat);
  sunCore.scale.setScalar(26);
  scene.add(sunCore);

  // ------------------------------------------------------------------ lights
  const hemi = new THREE.HemisphereLight(0xb7dcea, 0x9c6048, 0.95);
  scene.add(hemi);

  const key = new THREE.DirectionalLight(0xffc38c, 3.35);
  key.position.copy(SUN_DIR).multiplyScalar(90);
  scene.add(key);
  scene.add(key.target);

  const fill = new THREE.DirectionalLight(0xffd8b8, 1.25);
  fill.position.set(20, 16, 30);
  scene.add(fill);
  scene.add(fill.target);

  const rim = new THREE.DirectionalLight(0x9fd4e2, 0.7);
  rim.position.set(-28, 12, -6);
  scene.add(rim);
  scene.add(rim.target);

  // ------------------------------------------------------------------ clouds
  const rand = rng(2024);
  const clouds = [];
  const cloudDefs = [
    [-260, 56, -200, 9],
    [40, 62, -240, 14],
    [150, 42, -160, 9],
    [255, 66, -270, 15],
    [-185, 30, -130, 8],
    [95, 34, -145, 6],
  ];
  for (const [x, y, z, s] of cloudDefs) {
    const cloud = makeCloud(rand, s);
    cloud.userData = { baseX: x, baseY: y, baseZ: z, drift: 0.4 + rand() * 0.7 };
    scene.add(cloud);
    clouds.push(cloud);
  }

  // ------------------------------------------------------------- islands
  const islands = [];
  const islandDefs = [
    { x: -95, z: -210, seed: 12, opts: { width: 26, depth: 14 } },
    { x: 125, z: -260, seed: 27, opts: { width: 19, depth: 12, lighthouse: true } },
    { x: 25, z: -180, seed: 41, opts: { width: 14, depth: 9, palms: false } },
  ];
  for (const def of islandDefs) {
    const island = createIsland(def.seed, def.opts);
    island.userData = { baseX: def.x, baseZ: def.z };
    island.position.set(def.x, -1.2, def.z);
    scene.add(island);
    islands.push(island);
  }

  const boat = createSailboat();
  boat.userData = { baseX: 82, baseZ: -168 };
  boat.position.set(82, 0, -168);
  scene.add(boat);

  // ---------------------------------------------------------------- gulls
  const gulls = [];
  for (let i = 0; i < 4; i++) {
    const gull = createGull(rand);
    gull.userData.baseX = -28 + rand() * 70;
    gull.userData.baseY = 7 + rand() * 10;
    gull.userData.baseZ = -20 - rand() * 30;
    gull.userData.drift = 1.5 + rand() * 2;
    gull.scale.setScalar(1.0 + rand() * 0.6);
    scene.add(gull);
    gulls.push(gull);
  }

  // high wispy clouds, as soft sprites
  const cloudTex = makeCloudTexture();
  const wisps = [];
  for (let i = 0; i < 7; i++) {
    const mat = new THREE.SpriteMaterial({
      map: cloudTex,
      color: '#ffd9c1',
      transparent: true,
      opacity: 0.45,
      depthWrite: false,
      fog: false,
    });
    const sprite = new THREE.Sprite(mat);
    sprite.userData = {
      baseX: -300 + rand() * 600,
      baseY: 70 + rand() * 55,
      baseZ: -260 - rand() * 120,
      scale: 90 + rand() * 80,
    };
    sprite.scale.set(sprite.userData.scale, sprite.userData.scale * 0.35, 1);
    scene.add(sprite);
    wisps.push(sprite);
  }

  // Small, thrown-away foam texture used to give the sea some sparkle
  const foamSparkle = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: makeFoamTile(),
      transparent: true,
      opacity: 0.0,
      depthWrite: false,
    }),
  );
  foamSparkle.visible = false;
  scene.add(foamSparkle);

  const clockStart = 0;

  function update(t, dt, boardPos) {
    oceanUniforms.uTime.value = t;
    sky.position.copy(camera.position);
    sunGlow.position.copy(camera.position).addScaledVector(SUN_DIR, 380);
    sunCore.position.copy(sunGlow.position);

    ocean.position.set(boardPos.x, 0, boardPos.z);

    key.position.copy(boardPos).addScaledVector(SUN_DIR, 90);
    key.target.position.copy(boardPos);
    fill.position.set(boardPos.x + 24, boardPos.y + 20, boardPos.z + 34);
    fill.target.position.copy(boardPos);
    rim.position.set(boardPos.x - 24, boardPos.y + 7, boardPos.z - 12);
    rim.target.position.copy(boardPos);

    for (const cloud of clouds) {
      const d = cloud.userData;
      cloud.position.x = camera.position.x + wrap(d.baseX - camera.position.x, -280, 280);
      cloud.position.y = d.baseY + Math.sin(t * 0.05 + d.baseX) * 1.5;
      cloud.position.z = d.baseZ;
      cloud.rotation.y = Math.sin(t * 0.02 + d.baseX) * 0.1;
    }

    for (const island of islands) {
      const d = island.userData;
      island.position.x = camera.position.x + wrap(d.baseX - camera.position.x, -300, 300);
      island.position.z = d.baseZ;
    }

    const bd = boat.userData;
    boat.position.x = camera.position.x + wrap(bd.baseX + t * 0.16 - camera.position.x, -270, 270);
    boat.position.z = bd.baseZ;
    boat.position.y = Math.sin(t * 0.9) * 0.22 - 0.1;
    boat.rotation.z = Math.sin(t * 0.8 + 0.4) * 0.03;

    for (const gull of gulls) {
      const d = gull.userData;
      gull.position.x = camera.position.x + wrap(d.baseX + t * d.drift * 0.6 - camera.position.x, -55, 55);
      gull.position.y = d.baseY + Math.sin(t * 0.5 + d.phase) * 1.2;
      gull.position.z = d.baseZ;
      const flap = Math.sin(t * 4.0 + d.phase);
      d.wr.rotation.z = flap * 0.45;
      d.wl.rotation.z = -flap * 0.45;
      gull.rotation.y = Math.cos(t * 0.16 + d.phase) * 0.35;
    }

    for (const wisp of wisps) {
      const d = wisp.userData;
      wisp.position.x = camera.position.x + wrap(d.baseX - camera.position.x, -380, 380);
      wisp.position.y = d.baseY + Math.sin(t * 0.03 + d.baseX) * 2.0;
      wisp.position.z = d.baseZ;
    }

    foamSparkle.visible = false;
  }

  return {
    update,
    sunDirection: SUN_DIR,
    oceanUniforms,
    sky,
    sunGlow,
    sunCore,
    lights: { hemi, key, fill, rim },
    waveHeight,
    clockStart,
  };
}
