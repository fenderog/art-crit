import * as THREE from 'three';
import { makeCloudTexture, makeGlowTexture } from './textures.js';

const SKY_VERT = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const SKY_FRAG = /* glsl */ `
uniform vec3 uTop;
uniform vec3 uHorizon;
uniform vec3 uSunColor;
uniform vec3 uSunDir;
varying vec3 vDir;
void main() {
  vec3 d = normalize(vDir);
  float y = d.y;
  vec3 col = mix(uHorizon, uTop, pow(clamp(y, 0.0, 1.0), 0.58));
  float sd = max(dot(d, uSunDir), 0.0);
  col += uSunColor * pow(sd, 5.0) * 0.14;
  col += uSunColor * pow(sd, 40.0) * 0.55;
  col = mix(col, uHorizon * 1.06, smoothstep(0.16, -0.06, y));
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

const GULL_VERT = /* glsl */ `
varying vec3 vNormalW;
void main() {
  vNormalW = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const GULL_FRAG = /* glsl */ `
uniform vec3 uColor;
uniform vec3 uSunDir;
uniform vec3 uSkyTop;
uniform vec3 uHorizon;
varying vec3 vNormalW;
void main() {
  vec3 n = normalize(vNormalW);
  float lit = clamp(dot(n, uSunDir) * 0.5 + 0.5, 0.0, 1.0);
  vec3 col = uColor * mix(0.55, 1.15, lit);
  col = mix(col, uSkyTop, 0.16);
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSky({ palette, sunDir }) {
  const group = new THREE.Group();

  const uniforms = {
    uTop: { value: new THREE.Color(palette.skyTop) },
    uHorizon: { value: new THREE.Color(palette.skyHorizon) },
    uSunColor: { value: new THREE.Color(palette.sunColor) },
    uSunDir: { value: sunDir.clone() },
  };

  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(600, 48, 24),
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: SKY_VERT,
      fragmentShader: SKY_FRAG,
      side: THREE.BackSide,
      depthWrite: false,
    }),
  );
  dome.frustumCulled = false;
  dome.renderOrder = -10;
  group.add(dome);

  // sun disc + halo
  const sunPos = sunDir.clone().multiplyScalar(520);
  const disc = new THREE.Mesh(
    new THREE.CircleGeometry(20, 48),
    new THREE.MeshBasicMaterial({
      color: 0xfff6dd,
      depthWrite: false,
      transparent: true,
      opacity: 0.98,
    }),
  );
  disc.position.copy(sunPos);
  disc.renderOrder = -9;
  group.add(disc);

  const glow = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: makeGlowTexture(),
      color: 0xffe2b0,
      transparent: true,
      opacity: 0.75,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  glow.position.copy(sunPos);
  glow.scale.setScalar(320);
  glow.renderOrder = -9;
  group.add(glow);

  // drifting cumulus clouds
  const cloudTex = makeCloudTexture(11);
  const clouds = [];
  const cloudSpecs = [
    [-260, 58, -300, 230, 96],
    [220, 44, -340, 260, 104],
    [-120, 92, -380, 200, 78],
    [330, 86, -180, 190, 74],
    [-360, 40, -60, 210, 82],
    [90, 110, -420, 240, 88],
    [-40, 62, -330, 170, 66],
    [380, 52, 60, 180, 70],
  ];
  for (const [x, y, z, w, h] of cloudSpecs) {
    const sprite = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: cloudTex,
        transparent: true,
        opacity: 0.62 + Math.random() * 0.2,
        depthWrite: false,
      }),
    );
    sprite.position.set(x, y, z);
    sprite.scale.set(w, h, 1);
    group.add(sprite);
    clouds.push({ sprite, drift: 0.7 + Math.random() * 1.1, baseY: y });
  }

  // distant gulls, slowly circling
  const gulls = [];
  const gullGeo = new THREE.SphereGeometry(1, 10, 8);
  const wingGeo = new THREE.BoxGeometry(1, 0.06, 0.32);
  for (let i = 0; i < 5; i++) {
    const gull = new THREE.Group();
    const body = new THREE.Mesh(gullGeo);
    body.scale.setScalar(0.34 + i * 0.03);
    body.scale.z *= 2.2;
    gull.add(body);

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uColor: { value: new THREE.Color(i % 2 ? 0xf2f4f2 : 0xdfe3e0) },
        uSunDir: { value: sunDir.clone() },
        uSkyTop: { value: new THREE.Color(palette.skyTop) },
        uHorizon: { value: new THREE.Color(palette.skyHorizon) },
      },
      vertexShader: GULL_VERT,
      fragmentShader: GULL_FRAG,
      side: THREE.DoubleSide,
    });
    body.material = mat;

    const wings = [];
    for (const side of [-1, 1]) {
      const pivot = new THREE.Group();
      pivot.position.x = side * 0.22;
      const wing = new THREE.Mesh(wingGeo, mat);
      wing.position.x = side * 0.75;
      wing.scale.set(1.5, 1, 1);
      pivot.add(wing);
      gull.add(pivot);
      wings.push({ pivot, side });
    }

    const radius = 55 + i * 26;
    const height = 16 + (i % 3) * 9;
    const phase = i * 1.7;
    const speed = 0.045 + i * 0.008;
    group.add(gull);
    gulls.push({ gull, wings, radius, height, phase, speed });
  }

  return {
    group,
    update(t) {
      for (const c of clouds) {
        c.sprite.position.x += c.drift * 0.012;
        c.sprite.position.y = c.baseY + Math.sin(t * 0.12 + c.drift * 3) * 1.6;
        if (c.sprite.position.x > 480) c.sprite.position.x = -480;
      }
      for (const g of gulls) {
        const a = g.phase + t * g.speed;
        g.gull.position.set(
          Math.cos(a) * g.radius,
          g.height + Math.sin(a * 2.1) * 1.8,
          Math.sin(a) * g.radius - 60,
        );
        g.gull.rotation.y = -a + Math.PI / 2;
        const flap = Math.sin(t * 3.4 + g.phase * 2) * 0.62;
        for (const w of g.wings) w.pivot.rotation.z = w.side * flap;
      }
    },
  };
}