import * as THREE from 'three';
import { makeCloudTexture, makeGlowTexture, mulberry32 } from './utils.js';
import { waveHeight } from './waves.js';

export const SUN_DIR = new THREE.Vector3(0.27, 0.065, -0.96).normalize();

export function createSky(scene) {
  const group = new THREE.Group();
  scene.add(group);

  /* ------------------------------- sky dome ------------------------------- */
  const skyUniforms = {
    uZenith: { value: new THREE.Color(0x1d183d) },
    uUpper: { value: new THREE.Color(0x5b3057) },
    uMid: { value: new THREE.Color(0xb95362) },
    uHorizon: { value: new THREE.Color(0xe9a079) },
    uSunColor: { value: new THREE.Color(0xffd29a) },
    uCloudShadow: { value: new THREE.Color(0x664458) },
    uCloudLight: { value: new THREE.Color(0xffd0ac) },
    uSunDir: { value: SUN_DIR.clone() },
    uTime: { value: 0 }
  };

  const skyMaterial = new THREE.ShaderMaterial({
    uniforms: skyUniforms,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uZenith;
      uniform vec3 uUpper;
      uniform vec3 uMid;
      uniform vec3 uHorizon;
      uniform vec3 uSunColor;
      uniform vec3 uSunDir;
      uniform vec3 uCloudShadow;
      uniform vec3 uCloudLight;
      uniform float uTime;
      varying vec3 vDir;

      float hash21(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }

      float noise(vec2 p) {
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
        float value = 0.0;
        float amplitude = 0.5;
        for (int i = 0; i < 5; i++) {
          value += amplitude * noise(p);
          p = p * 2.04 + vec2(9.2, 3.4);
          amplitude *= 0.5;
        }
        return value;
      }

      void main() {
        vec3 dir = normalize(vDir);
        float h = dir.y;

        vec3 col = mix(uHorizon, uMid, smoothstep(0.0, 0.16, h));
        col = mix(col, uUpper, smoothstep(0.10, 0.48, h));
        col = mix(col, uZenith, smoothstep(0.42, 1.0, h));

        float below = smoothstep(0.0, -0.22, h);
        col = mix(col, vec3(0.035, 0.09, 0.11), below);

        float sd = max(dot(dir, uSunDir), 0.0);
        float disc = smoothstep(0.99955, 0.99982, sd);
        float innerGlow = pow(sd, 240.0);
        float wideGlow = pow(sd, 9.0);
        float haze = pow(sd, 2.0);

        col += uSunColor * disc * 3.1;
        col += uSunColor * innerGlow * 0.9;
        col += vec3(1.0, 0.38, 0.16) * wideGlow * 0.32;
        col += vec3(1.0, 0.30, 0.16) * haze * 0.10;

        float horizonHaze = pow(max(0.0, 1.0 - abs(h) * 5.5), 3.0);
        col += vec3(1.0, 0.44, 0.24) * horizonHaze * 0.075;

        // Painted cloud banks projected on the sky dome.
        float lon = atan(dir.z, dir.x);
        vec2 cuv = vec2(lon * 1.8 + uTime * 0.006, h * 5.4);
        float cloudBase = fbm(cuv * 1.15 + vec2(3.2, 1.7));
        float cloudDetail = fbm(cuv * 2.8 + vec2(-1.4, 6.1));
        float cloudMask = smoothstep(0.5, 0.72, cloudBase + cloudDetail * 0.26);
        cloudMask *= smoothstep(0.018, 0.12, h) * (1.0 - smoothstep(0.62, 0.88, h));
        float wisps = smoothstep(0.54, 0.68, fbm(cuv * vec2(1.1, 4.6) + vec2(8.4, -2.0)));
        wisps *= smoothstep(0.03, 0.16, h) * (1.0 - smoothstep(0.7, 0.95, h));

        float cloudSun = pow(sd, 5.0);
        float cloudShade = smoothstep(0.28, 0.9, cloudBase + cloudSun * 0.35);
        vec3 cloudColor = mix(uCloudShadow, uCloudLight, cloudShade);
        cloudColor += uSunColor * cloudSun * 0.45 * cloudMask;
        float cloudAlpha = cloudMask * 0.56 + wisps * 0.14;
        col = mix(col, cloudColor, clamp(cloudAlpha, 0.0, 0.78));

        // Very soft, warm banding gives the sky a painted, screen-print feel.
        float band = sin(h * 76.0 + 0.6) * 0.5 + 0.5;
        col += vec3(0.025, 0.012, 0.025) * band * smoothstep(0.02, 0.5, h) * 0.08;

        gl_FragColor = vec4(col, 1.0);
      }
    `,
    side: THREE.BackSide,
    depthWrite: false
  });

  const sky = new THREE.Mesh(new THREE.SphereGeometry(300, 48, 32), skyMaterial);
  sky.frustumCulled = false;
  group.add(sky);

  /* -------------------------------- sun glow ------------------------------ */
  const glowTexture = makeGlowTexture(512);
  const sunPos = SUN_DIR.clone().multiplyScalar(245);
  sunPos.y += 2.5;

  const halo = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture,
      color: new THREE.Color().setRGB(2.0, 0.7, 0.28),
      transparent: true,
      opacity: 0.4,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      toneMapped: false
    })
  );
  halo.position.copy(sunPos);
  halo.scale.set(44, 44, 1);
  group.add(halo);

  const core = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture,
      color: new THREE.Color().setRGB(3.8, 1.75, 0.68),
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      toneMapped: false
    })
  );
  core.position.copy(sunPos).add(new THREE.Vector3(0, 0, -0.2));
  core.scale.set(11, 11, 1);
  group.add(core);

  /* -------------------------------- islands ------------------------------- */
  function makeRidgeShape(width, height, seed) {
    const rand = mulberry32(seed);
    const shape = new THREE.Shape();
    const half = width * 0.5;
    shape.moveTo(-half, 0);
    const peaks = 4;
    let x = -half;
    for (let i = 0; i < peaks; i++) {
      const nextX = -half + ((i + 1) / peaks) * width;
      const midX = (x + nextX) * 0.5 + (rand() - 0.5) * width * 0.03;
      const peak = height * (0.22 + rand() * 0.9) * (1.0 - Math.abs((i + 0.5) / peaks - 0.5) * 0.72);
      shape.quadraticCurveTo(midX, peak, nextX, height * (0.04 + rand() * 0.12));
      x = nextX;
    }
    shape.lineTo(half, 0);
    shape.lineTo(-half, 0);
    return new THREE.ShapeGeometry(shape, 18);
  }

  function addIsland({ x, z, width, height, color, opacity = 1, seed }) {
    const mesh = new THREE.Mesh(
      makeRidgeShape(width, height, seed),
      new THREE.MeshBasicMaterial({
        color,
        transparent: opacity < 1,
        opacity,
        side: THREE.DoubleSide,
        depthWrite: false
      })
    );
    mesh.position.set(x, -0.15, z);
    mesh.renderOrder = -2;
    group.add(mesh);
    return mesh;
  }

  addIsland({ x: -43, z: -108, width: 86, height: 9.2, color: 0x402b4d, seed: 5, opacity: 0.78 });
  addIsland({ x: 46, z: -112, width: 32, height: 4.3, color: 0x4e3050, seed: 8, opacity: 0.72 });

  /* ------------------------------- sailboat ------------------------------- */
  const boat = new THREE.Group();
  boat.position.set(24, 0.7, -38);
  boat.scale.setScalar(1.15);

  const hullShape = new THREE.Shape();
  hullShape.moveTo(-0.72, 0.05);
  hullShape.quadraticCurveTo(-0.3, -0.25, 0.65, 0.0);
  hullShape.lineTo(0.46, 0.13);
  hullShape.lineTo(-0.55, 0.13);
  hullShape.closePath();
  const hull = new THREE.Mesh(
    new THREE.ShapeGeometry(hullShape),
    new THREE.MeshBasicMaterial({ color: 0x2b2033, side: THREE.DoubleSide })
  );
  boat.add(hull);

  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.018, 0.018, 1.7, 5),
    new THREE.MeshBasicMaterial({ color: 0x2b2033 })
  );
  mast.position.set(0.02, 0.92, 0);
  boat.add(mast);

  const sailShape = new THREE.Shape();
  sailShape.moveTo(0.03, 0.18);
  sailShape.lineTo(0.03, 1.7);
  sailShape.quadraticCurveTo(0.8, 0.62, 0.75, 0.22);
  sailShape.closePath();
  const sail = new THREE.Mesh(
    new THREE.ShapeGeometry(sailShape),
    new THREE.MeshBasicMaterial({
      color: 0xffd9b1,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9
    })
  );
  boat.add(sail);

  const jibShape = new THREE.Shape();
  jibShape.moveTo(-0.04, 1.58);
  jibShape.lineTo(-0.04, 0.3);
  jibShape.lineTo(-0.58, 0.24);
  jibShape.closePath();
  const jib = new THREE.Mesh(
    new THREE.ShapeGeometry(jibShape),
    new THREE.MeshBasicMaterial({
      color: 0xffe6c8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.82
    })
  );
  boat.add(jib);

  group.add(boat);

  /* ----------------------------- distant birds ---------------------------- */
  const birdMaterial = new THREE.MeshBasicMaterial({
    color: 0x3d2a40,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.82
  });

  function makeDistantBird() {
    const bird = new THREE.Group();
    const left = new THREE.Group();
    const right = new THREE.Group();

    const wingGeometry = new THREE.BufferGeometry();
    wingGeometry.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(
        [
          0, 0, 0,
          -0.55, 0, 0.13,
          -0.34, 0, -0.1
        ],
        3
      )
    );
    wingGeometry.computeVertexNormals();

    const leftWing = new THREE.Mesh(wingGeometry, birdMaterial);
    leftWing.scale.x = -1;
    left.add(leftWing);

    const rightWing = new THREE.Mesh(wingGeometry, birdMaterial);
    right.add(rightWing);

    bird.add(left, right);
    bird.userData.left = left;
    bird.userData.right = right;
    return bird;
  }

  const distantBirds = [];
  const birdSpecs = [
    { x: -20, y: 15, z: -51, s: 0.42, phase: 0.4 },
    { x: -16.5, y: 16.8, z: -55, s: 0.32, phase: 1.8 },
    { x: -23.5, y: 13.2, z: -47, s: 0.27, phase: 3.4 },
    { x: 17, y: 18, z: -59, s: 0.24, phase: 5.1 }
  ];
  for (const spec of birdSpecs) {
    const bird = makeDistantBird();
    bird.position.set(spec.x, spec.y, spec.z);
    bird.scale.setScalar(spec.s);
    bird.userData.phase = spec.phase;
    bird.userData.base = new THREE.Vector3(spec.x, spec.y, spec.z);
    group.add(bird);
    distantBirds.push(bird);
  }

  function update(t) {
    skyUniforms.uTime.value = t;
    boat.position.y = waveHeight(boat.position.x, boat.position.z, t) + 0.25;
    boat.rotation.z = Math.sin(t * 0.55) * 0.035;
    boat.rotation.x = Math.sin(t * 0.37 + 1.2) * 0.018;

    for (const bird of distantBirds) {
      const p = bird.userData.phase;
      const flap = Math.sin(t * 2.1 + p);
      bird.userData.left.rotation.z = 0.2 + flap * 0.35;
      bird.userData.right.rotation.z = -0.2 - flap * 0.35;
      bird.position.x = bird.userData.base.x + Math.sin(t * 0.08 + p) * 1.4;
      bird.position.y = bird.userData.base.y + Math.sin(t * 0.3 + p) * 0.22;
    }
  }

  return { group, update };
}
