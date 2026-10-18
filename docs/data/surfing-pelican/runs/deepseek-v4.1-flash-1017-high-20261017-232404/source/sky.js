import * as THREE from 'three';
import { makeCloudTexture, makeGlowTexture } from './textures.js';

export const SUN_DIR = new THREE.Vector3(-0.86, 0.115, -0.34).normalize();

const skyVertex = /* glsl */ `
varying vec3 vDir;

void main() {
  vDir = normalize(position);
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * mv;
}
`;

const skyFragment = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uZenith;
uniform vec3 uMid;
uniform vec3 uHorizon;
uniform vec3 uSunColor;

varying vec3 vDir;

void main() {
  vec3 dir = normalize(vDir);
  float h = dir.y;

  vec3 col = mix(uHorizon, uMid, smoothstep(-0.01, 0.23, h));
  col = mix(col, uZenith, smoothstep(0.16, 0.72, h));

  float d = max(dot(dir, normalize(uSunDir)), 0.0);

  // Broad sunset bloom around the sun.
  col += uSunColor * pow(d, 420.0) * 1.25;
  col += vec3(1.0, 0.53, 0.28) * pow(d, 36.0) * 0.24;
  col += vec3(1.0, 0.4, 0.22) * pow(d, 5.0) * 0.06;

  // Thin, luminous haze sitting on the horizon.
  float haze = exp(-max(h, 0.0) * 22.0);
  col = mix(col, vec3(1.0, 0.76, 0.55), haze * 0.35);

  // Sun disc.
  float disc = smoothstep(0.99955, 0.99982, d);
  col = mix(col, vec3(1.0, 0.95, 0.78), disc);

  // Darken the tiny sliver below the horizon.
  col = mix(vec3(0.12, 0.17, 0.2), col, smoothstep(-0.09, 0.015, h));

  // Dither to keep the long gradient clean.
  float dither = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
  col += (dither - 0.5) / 255.0;

  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

function makeBird(scale, flapSpeed, phase) {
  const bird = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({
    color: 0x22303c,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.82,
  });

  const wingGeom = new THREE.BufferGeometry();
  wingGeom.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(
      [0, 0, 0.06, 0.95, 0.12, 0, 0.3, 0.02, -0.2],
      3
    )
  );
  wingGeom.computeVertexNormals();

  const right = new THREE.Mesh(wingGeom, mat);
  const left = new THREE.Mesh(wingGeom, mat);
  left.scale.x = -1;

  const rightPivot = new THREE.Group();
  rightPivot.add(right);
  const leftPivot = new THREE.Group();
  leftPivot.add(left);
  bird.add(rightPivot, leftPivot);

  bird.scale.setScalar(scale);
  bird.userData = { rightPivot, leftPivot, flapSpeed, phase };
  return bird;
}

export function createSky() {
  const group = new THREE.Group();

  const skyUniforms = {
    uSunDir: { value: SUN_DIR.clone() },
    uZenith: { value: new THREE.Color(0x142c55) },
    uMid: { value: new THREE.Color(0x91506f) },
    uHorizon: { value: new THREE.Color(0xffa767) },
    uSunColor: { value: new THREE.Color(0xffdca0) },
  };

  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(1300, 48, 24),
    new THREE.ShaderMaterial({
      uniforms: skyUniforms,
      vertexShader: skyVertex,
      fragmentShader: skyFragment,
      side: THREE.BackSide,
      depthWrite: false,
    })
  );
  dome.renderOrder = -10;
  group.add(dome);

  const glowTexture = makeGlowTexture();

  const halo = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture,
      color: 0xffc47a,
      transparent: true,
      opacity: 0.26,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );
  halo.position.copy(SUN_DIR).multiplyScalar(980);
  halo.scale.setScalar(235);
  group.add(halo);

  const core = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture,
      color: 0xfff1c8,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );
  core.position.copy(SUN_DIR).multiplyScalar(960);
  core.scale.setScalar(32);
  group.add(core);

  // Deterministic cloud layout.
  let seed = 7;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };

  const cloudTextures = [makeCloudTexture(3), makeCloudTexture(11), makeCloudTexture(23)];
  const tints = [0xd9a3b8, 0xc29ab8, 0xf0b6a8, 0xb99ac0, 0xe7b3ac];
  const sunAz = Math.atan2(SUN_DIR.x, SUN_DIR.z);

  for (let i = 0; i < 8; i++) {
    const az = sunAz + (i / 7 - 0.5) * 1.55 + (rand() - 0.5) * 0.28;
    const dist = 650 + rand() * 220;
    const y = 34 + rand() * 130;
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: cloudTextures[i % cloudTextures.length],
        color: tints[i % tints.length],
        transparent: true,
        opacity: 0.62 + rand() * 0.2,
        depthWrite: false,
      })
    );
    sprite.position.set(Math.sin(az) * dist, y, Math.cos(az) * dist);
    const s = 120 + rand() * 150;
    sprite.scale.set(s * (1.45 + rand() * 0.55), s * (0.5 + rand() * 0.22), 1);
    sprite.material.rotation = (rand() - 0.5) * 0.35;
    sprite.userData.base = sprite.position.clone();
    sprite.userData.phase = rand() * Math.PI * 2;
    sprite.userData.drift = 5 + rand() * 9;
    group.add(sprite);
  }

  const clouds = group.children.filter((child) => child.isSprite && child.userData.base);

  // A few distant birds, small enough to read as silhouettes.
  const birds = [];
  const birdData = [
    [-120, 62, -240, 2.1, 1.25, 0.0],
    [-62, 88, -300, 1.7, 0.95, 1.7],
    [58, 52, -265, 1.5, 1.45, 3.1],
    [130, 96, -310, 1.9, 1.1, 4.4],
    [-185, 38, -205, 1.4, 1.6, 2.4],
  ];
  for (const [x, y, z, s, speed, phase] of birdData) {
    const bird = makeBird(s, speed, phase);
    bird.position.set(x, y, z);
    group.add(bird);
    birds.push(bird);
  }

  return {
    group,
    update(time, camera) {
      group.position.copy(camera.position);
      for (const cloud of clouds) {
        const { base, phase, drift } = cloud.userData;
        cloud.position.x = base.x + Math.sin(time * 0.008 + phase) * drift;
        cloud.position.z = base.z + Math.cos(time * 0.006 + phase) * drift * 0.4;
      }
      for (const bird of birds) {
        const { rightPivot, leftPivot, flapSpeed, phase } = bird.userData;
        const flap = Math.sin(time * flapSpeed + phase) * 0.55;
        rightPivot.rotation.z = flap;
        leftPivot.rotation.z = -flap;
        bird.position.x += Math.sin(time * 0.05 + phase) * 0.0015;
      }
    },
  };
}
