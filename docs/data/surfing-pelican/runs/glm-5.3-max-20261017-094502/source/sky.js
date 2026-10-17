import * as THREE from 'three';
import { PALETTE } from './theme.js';
import { makeGlowTexture } from './textures.js';

// Gradient sky dome with a hot sun disc + glow, all in one shader.
// The dome is parented to the "scenery rig" that follows the rider, so the
// horizon and sun stay put like a genuinely distant backdrop.
export function createSky(sunDir) {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      uZenith: { value: new THREE.Color(PALETTE.zenith) },
      uHorizon: { value: new THREE.Color(PALETTE.horizon) },
      uSun: { value: new THREE.Color(PALETTE.sun) },
      uSunDir: { value: sunDir.clone() },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uZenith;
      uniform vec3 uHorizon;
      uniform vec3 uSun;
      uniform vec3 uSunDir;
      varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir);
        float h = max(d.y, 0.0);
        vec3 col = mix(uHorizon, uZenith, pow(h, 0.55));
        float s = max(dot(d, normalize(uSunDir)), 0.0);
        col += uSun * (pow(s, 900.0) * 3.5 + pow(s, 80.0) * 0.5 + pow(s, 7.0) * 0.25 + pow(s, 2.0) * 0.06);
        float below = smoothstep(0.0, 0.10, -min(d.y, 0.0));
        col = mix(col, uHorizon, below);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(520, 40, 24), mat);
  mesh.frustumCulled = false;
  return mesh;
}

// Soft additive sprite layered over the shader sun for a cheap bloom feel.
export function createSunSprite(sunDir) {
  const tex = makeGlowTexture([
    [0.0, 'rgba(255,250,240,1)'],
    [0.16, 'rgba(255,236,200,0.95)'],
    [0.4, 'rgba(255,205,150,0.45)'],
    [0.7, 'rgba(255,185,130,0.12)'],
    [1.0, 'rgba(255,180,125,0)'],
  ]);
  const mat = new THREE.SpriteMaterial({
    map: tex,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    fog: false,
  });
  const sp = new THREE.Sprite(mat);
  sp.scale.set(150, 150, 1);
  sp.position.copy(sunDir).multiplyScalar(430);
  return sp;
}
