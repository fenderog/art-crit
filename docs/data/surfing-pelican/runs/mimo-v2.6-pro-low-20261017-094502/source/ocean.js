import * as THREE from 'three';
import { waveGLSL } from './waves.js';

// ---------------------------------------------------------------------------
// small canvas-texture helpers (generated in code, no external assets)
// ---------------------------------------------------------------------------

function radialTexture(size, stops, blur = false) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  for (const [offset, color] of stops) g.addColorStop(offset, color);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  if (!blur) {
    tex.generateMipmaps = true;
    tex.minFilter = THREE.LinearMipmapLinearFilter;
  }
  return tex;
}

export function makeSoftDiscTexture() {
  return radialTexture(128, [
    [0, 'rgba(255,255,255,1)'],
    [0.35, 'rgba(255,255,255,0.85)'],
    [0.7, 'rgba(255,255,255,0.22)'],
    [1, 'rgba(255,255,255,0)'],
  ]);
}

// ---------------------------------------------------------------------------
// Sky dome: vertical gradient with a soft sun bloom, drawn on the inside of a
// big sphere. Not fogged, so the horizon colour has to match the scene fog.
// ---------------------------------------------------------------------------

export function createSky(sunDir, palette) {
  const geometry = new THREE.SphereGeometry(600, 32, 20);
  const material = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      uZenith: { value: palette.zenith.clone() },
      uHorizon: { value: palette.horizon.clone() },
      uSunColor: { value: palette.sunGlow.clone() },
      uSunDir: { value: sunDir.clone().normalize() },
    },
    vertexShader: /* glsl */ `
      varying vec3 vWorldPos;
      void main() {
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uZenith;
      uniform vec3 uHorizon;
      uniform vec3 uSunColor;
      uniform vec3 uSunDir;
      varying vec3 vWorldPos;
      void main() {
        vec3 d = normalize(vWorldPos - cameraPosition);
        float up = clamp(d.y, 0.0, 1.0);
        vec3 col = mix(uHorizon, uZenith, pow(up, 0.55));
        float sd = max(dot(d, normalize(uSunDir)), 0.0);
        col += uSunColor * (pow(sd, 900.0) * 1.1 + pow(sd, 32.0) * 0.30 + pow(sd, 5.0) * 0.13);
        col = mix(col, uHorizon * 0.92, smoothstep(0.02, -0.16, d.y));
        gl_FragColor = vec4(col, 1.0);
        #include <colorspace_fragment>
      }
    `,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return mesh;
}

export function createSunGlow(sunDir) {
  const texture = radialTexture(256, [
    [0, 'rgba(255,246,224,1)'],
    [0.12, 'rgba(255,238,199,0.72)'],
    [0.32, 'rgba(255,222,168,0.28)'],
    [0.62, 'rgba(255,214,150,0.08)'],
    [1, 'rgba(255,210,150,0)'],
  ]);
  const material = new THREE.SpriteMaterial({
    map: texture,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: true,
    transparent: true,
    fog: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.position.copy(sunDir).normalize().multiplyScalar(520);
  sprite.scale.setScalar(300);
  return sprite;
}

// ---------------------------------------------------------------------------
// Ocean: Gerstner displaced grid with hand written shading (depth tint,
// fresnel sky reflection, sun glints, crest foam) + scene fog.
// ---------------------------------------------------------------------------

export function createOcean(sunDir, palette) {
  const geometry = new THREE.PlaneGeometry(640, 640, 380, 380);
  geometry.rotateX(-Math.PI / 2);

  const material = new THREE.ShaderMaterial({
    fog: true,
    uniforms: {
      ...THREE.UniformsUtils.clone(THREE.UniformsLib.fog),
      uTime: { value: 0 },
      uSunDir: { value: sunDir.clone().normalize() },
      uSunColor: { value: palette.sunLight.clone() },
      uSkyColor: { value: palette.horizon.clone() },
      uDeep: { value: palette.deep.clone() },
      uShallow: { value: palette.shallow.clone() },
    },
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying vec3 vWorldPos;
      varying vec3 vNormal;
      varying float vCrest;
      #include <fog_pars_vertex>
      ${waveGLSL()}
      void main() {
        vec3 nrm;
        float crest;
        vec3 disp = gerstner(position.xz, uTime, nrm, crest);
        vWorldPos = disp;
        vNormal = nrm;
        vCrest = crest;
        vec4 mvPosition = modelViewMatrix * vec4(disp, 1.0);
        gl_Position = projectionMatrix * mvPosition;
        #include <fog_vertex>
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform vec3 uSunDir;
      uniform vec3 uSunColor;
      uniform vec3 uSkyColor;
      uniform vec3 uDeep;
      uniform vec3 uShallow;
      varying vec3 vWorldPos;
      varying vec3 vNormal;
      varying float vCrest;
      #include <fog_pars_fragment>

      float hash(vec2 p) {
        return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
      }
      float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 fr = fract(p);
        fr = fr * fr * (3.0 - 2.0 * fr);
        return mix(
          mix(hash(i), hash(i + vec2(1.0, 0.0)), fr.x),
          mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), fr.x),
          fr.y
        );
      }

      void main() {
        vec3 N = normalize(vNormal);
        vec3 V = normalize(cameraPosition - vWorldPos);
        float fres = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 4.0);

        vec3 col = mix(uDeep, uShallow, smoothstep(-1.7, 1.9, vWorldPos.y));
        col = mix(col, uSkyColor, clamp(fres * 0.9, 0.0, 1.0));

        // sun glints
        vec3 H = normalize(normalize(uSunDir) + V);
        float ndh = max(dot(N, H), 0.0);
        float glint = pow(ndh, 260.0) * 2.6 + pow(ndh, 26.0) * 0.22;
        col += uSunColor * glint;

        // crest foam, broken up by two octaves of noise. The fine octave and
        // the foam itself fade with distance so the detail cannot alias into
        // salt and pepper speckles on the far water.
        float dist = length(cameraPosition - vWorldPos);
        float detail = 1.0 - smoothstep(18.0, 78.0, dist);
        float n = noise(vWorldPos.xz * 1.35 + uTime * 0.28) * 0.55
                + noise(vWorldPos.xz * 4.1 - uTime * 0.5) * 0.45 * detail;
        float foamAmount = smoothstep(0.34, 1.05, vCrest * (0.42 + n * 0.95));
        foamAmount += smoothstep(0.62, 1.0, n) * smoothstep(0.15, 0.75, vCrest) * 0.5;
        float foam = clamp(foamAmount, 0.0, 1.0) * (0.22 + 0.78 * detail);
        col = mix(col, vec3(0.94, 0.965, 0.975), foam * 0.92);

        gl_FragColor = vec4(col, 1.0);
        #include <fog_fragment>
        #include <colorspace_fragment>
      }
    `,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  return mesh;
}

// ---------------------------------------------------------------------------
// Spray: a cloud of soft particles kicked up around the surfboard.
// ---------------------------------------------------------------------------

export function createSpray(count = 260) {
  const positions = new Float32Array(count * 3);
  const seeds = new Float32Array(count * 4);
  for (let i = 0; i < count; i++) {
    seeds[i * 4 + 0] = Math.random() * Math.PI * 2; // angle around board
    seeds[i * 4 + 1] = 0.6 + Math.random() * 2.2; // radius
    seeds[i * 4 + 2] = Math.random(); // phase
    seeds[i * 4 + 3] = 0.4 + Math.random() * 1.1; // speed / height
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  const material = new THREE.PointsMaterial({
    size: 0.22,
    map: makeSoftDiscTexture(),
    color: 0xf2fbff,
    transparent: true,
    opacity: 0.5,
    depthWrite: false,
    sizeAttenuation: true,
    fog: true,
  });

  const points = new THREE.Points(geometry, material);
  points.frustumCulled = false;
  points.userData.seeds = seeds;
  points.userData.positions = positions;
  points.userData.count = count;
  return points;
}

// ---------------------------------------------------------------------------
// Fake contact shadow: a soft dark blob that follows the moving water surface.
// ---------------------------------------------------------------------------

export function createContactShadow() {
  const texture = radialTexture(256, [
    [0, 'rgba(6,26,40,0.72)'],
    [0.45, 'rgba(6,26,40,0.42)'],
    [0.78, 'rgba(6,26,40,0.12)'],
    [1, 'rgba(6,26,40,0)'],
  ]);
  const material = new THREE.MeshBasicMaterial({
    map: texture,
    transparent: true,
    opacity: 0.85,
    depthWrite: false,
    fog: true,
  });
  const mesh = new THREE.Mesh(new THREE.CircleGeometry(1, 40), material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.scale.set(2.05, 3.0, 1);
  mesh.renderOrder = 2;
  return mesh;
}