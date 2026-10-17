// Sky dome, clouds and a handful of distant birds — all procedural.

import * as THREE from 'three';

const SKY_VERTEX = /* glsl */ `
  varying vec3 vDir;
  void main() {
    vDir = normalize(position);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const SKY_FRAGMENT = /* glsl */ `
  precision highp float;

  uniform vec3 uZenith;
  uniform vec3 uHorizon;
  uniform vec3 uSunDir;
  uniform vec3 uSunColor;

  varying vec3 vDir;

  void main() {
    vec3 d = normalize(vDir);
    float h = clamp(d.y, 0.0, 1.0);

    vec3 col = mix(uHorizon, uZenith, pow(h, 0.35));

    float s = max(dot(d, normalize(uSunDir)), 0.0);
    col += uSunColor * (pow(s, 1500.0) * 3.4 + pow(s, 90.0) * 0.55 + pow(s, 8.0) * 0.22);

    // just under the horizon keep the haze colour so the ocean fog blends in
    col = mix(col, uHorizon, smoothstep(0.0, -0.09, d.y));

    gl_FragColor = vec4(col, 1.0);
  }
`;

/** Soft puffy cloud sprite drawn on a canvas. */
function makeCloudTexture() {
  const w = 512;
  const h = 256;
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, w, h);

  const blobs = [
    [128, 156, 84], [200, 124, 104], [276, 140, 100], [352, 160, 80],
    [236, 176, 72], [168, 180, 60], [312, 184, 64], [408, 176, 52],
    [120, 190, 44], [360, 200, 40], [250, 200, 46], [180, 210, 34],
  ];
  for (const [x, y, r] of blobs) {
    const g = ctx.createRadialGradient(x, y, r * 0.12, x, y, r);
    g.addColorStop(0, 'rgba(255,255,255,0.92)');
    g.addColorStop(0.5, 'rgba(255,252,246,0.5)');
    g.addColorStop(1, 'rgba(255,250,242,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.generateMipmaps = true;
  return tex;
}

function createClouds() {
  const group = new THREE.Group();
  const tex = makeCloudTexture();

  for (let i = 0; i < 12; i++) {
    const mat = new THREE.SpriteMaterial({
      map: tex,
      transparent: true,
      depthWrite: false,
      fog: false,
      opacity: 0.5 + Math.random() * 0.3,
      color: new THREE.Color().setHSL(0.09, 0.45, 0.9 - Math.random() * 0.06),
    });
    const sprite = new THREE.Sprite(mat);
    const a = Math.random() * Math.PI * 2;
    const r = 150 + Math.random() * 160;
    sprite.position.set(Math.cos(a) * r, 32 + Math.random() * 58, Math.sin(a) * r);
    const s = 24 + Math.random() * 34;
    sprite.scale.set(s, s * (0.32 + Math.random() * 0.12), 1);
    sprite.userData.speed = 0.5 + Math.random() * 1.4;
    group.add(sprite);
  }
  return group;
}

function createBirds() {
  const group = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x3d4d58, fog: false, side: THREE.DoubleSide });

  const wingGeo = new THREE.PlaneGeometry(1.5, 0.3, 2, 1);
  wingGeo.translate(0.75, 0, 0);

  for (let i = 0; i < 6; i++) {
    const bird = new THREE.Group();

    const left = new THREE.Mesh(wingGeo, mat);
    const right = new THREE.Mesh(wingGeo, mat);
    right.scale.x = -1;
    bird.add(left, right);

    const body = new THREE.Mesh(new THREE.SphereGeometry(0.16, 8, 6), mat);
    body.scale.set(0.8, 0.8, 2.0);
    bird.add(body);

    const a = Math.random() * Math.PI * 2;
    const radius = 26 + Math.random() * 70;
    bird.userData = {
      centerX: -20 + Math.random() * 60,
      centerZ: -40 + Math.random() * 60,
      radius,
      angle: a,
      speed: (0.02 + Math.random() * 0.035) * (Math.random() < 0.5 ? -1 : 1),
      height: 24 + Math.random() * 26,
      flapPhase: Math.random() * Math.PI * 2,
      flapSpeed: 6 + Math.random() * 3,
      wings: [left, right],
    };
    bird.scale.setScalar(1.1 + Math.random() * 0.7);
    group.add(bird);
  }
  return group;
}

export function createSky({ sunDir }) {
  const uniforms = {
    uZenith: { value: new THREE.Color(0x2f6cb2) },
    uHorizon: { value: new THREE.Color(0xe8dfd2) },
    uSunDir: { value: sunDir.clone() },
    uSunColor: { value: new THREE.Color(0xffcf94) },
  };

  const geometry = new THREE.SphereGeometry(900, 48, 32);
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: SKY_VERTEX,
    fragmentShader: SKY_FRAGMENT,
    side: THREE.BackSide,
    depthWrite: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;

  const clouds = createClouds();
  const birds = createBirds();

  return {
    mesh,
    group: (() => {
      const g = new THREE.Group();
      g.add(mesh, clouds, birds);
      return g;
    })(),
    update(t, dt) {
      // clouds drift slowly and wrap around
      for (const sprite of clouds.children) {
        sprite.position.x += sprite.userData.speed * dt;
        if (sprite.position.x > 340) sprite.position.x = -340;
      }

      // distant birds loop over the water
      for (const bird of birds.children) {
        const u = bird.userData;
        u.angle += u.speed * dt;
        const x = u.centerX + Math.cos(u.angle) * u.radius;
        const z = u.centerZ + Math.sin(u.angle) * u.radius;
        bird.position.set(x, u.height + Math.sin(t * 0.6 + u.flapPhase) * 1.6, z);

        const vx = -Math.sin(u.angle) * Math.sign(u.speed);
        const vz = Math.cos(u.angle) * Math.sign(u.speed);
        bird.rotation.y = Math.atan2(vx, vz);

        const flap = Math.sin(t * u.flapSpeed + u.flapPhase);
        const [left, right] = u.wings;
        left.rotation.z = 0.25 + flap * 0.65;
        right.rotation.z = -0.25 - flap * 0.65;
      }
    },
  };
}
