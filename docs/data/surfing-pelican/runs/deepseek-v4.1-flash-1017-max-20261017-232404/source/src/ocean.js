import * as THREE from 'three';
import { waveGLSL } from './waves.js';

export function createOcean(scene) {
  const uniforms = {
    uTime: { value: 0 },
    uDeep: { value: new THREE.Color(0x041c2a) },
    uMid: { value: new THREE.Color(0x07505e) },
    uShallow: { value: new THREE.Color(0x0f8b8a) },
    uSky: { value: new THREE.Color(0x714a6c) },
    uHorizon: { value: new THREE.Color(0xd98b72) },
    uFoam: { value: new THREE.Color(0xfff2dc) },
    uSunDir: { value: new THREE.Vector3(0.27, 0.065, -0.96).normalize() },
    uBoardPos: { value: new THREE.Vector2(0, 0.8) }
  };

  const geometry = new THREE.PlaneGeometry(220, 220, 300, 300);
  geometry.rotateX(-Math.PI / 2);

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying vec3 vWorldPos;
      varying vec3 vNormalW;
      varying float vHeight;
      varying float vCrestH;

      ${waveGLSL}

      void main() {
        vec3 pos = position;
        float h = waveHeight(pos.xz, uTime);
        pos.y += h;

        float zc = -3.35 + 0.68 * sin(uTime * 0.13);
        vCrestH = waveHeight(vec2(pos.x, zc), uTime);

        vec3 n = waveNormal(pos.xz, uTime);
        vec4 world = modelMatrix * vec4(pos, 1.0);

        vWorldPos = world.xyz;
        vNormalW = normalize(mat3(modelMatrix) * n);
        vHeight = h;

        gl_Position = projectionMatrix * viewMatrix * world;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform vec3 uDeep;
      uniform vec3 uMid;
      uniform vec3 uShallow;
      uniform vec3 uSky;
      uniform vec3 uHorizon;
      uniform vec3 uFoam;
      uniform vec3 uSunDir;
      uniform vec2 uBoardPos;

      varying vec3 vWorldPos;
      varying vec3 vNormalW;
      varying float vHeight;
      varying float vCrestH;

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
        for (int i = 0; i < 4; i++) {
          value += amplitude * noise(p);
          p = p * 2.03 + vec2(13.1, 7.7);
          amplitude *= 0.5;
        }
        return value;
      }

      void main() {
        vec3 N = normalize(vNormalW);
        vec3 V = normalize(cameraPosition - vWorldPos);
        float ndv = clamp(dot(N, V), 0.0, 1.0);
        float fresnel = pow(1.0 - ndv, 4.0);

        vec2 microP = vWorldPos.xz;
        float microX = noise(microP * 2.8 + vec2(uTime * 0.45, -uTime * 0.22)) - 0.5;
        float microZ = noise(microP * 3.1 + vec2(-uTime * 0.28, uTime * 0.35)) - 0.5;
        float microFade = smoothstep(38.0, 4.0, length(cameraPosition.xz - microP));
        N = normalize(N + vec3(microX, 0.0, microZ) * 0.025 * microFade);
        ndv = clamp(dot(N, V), 0.0, 1.0);
        fresnel = pow(1.0 - ndv, 4.0);

        vec3 base = mix(uDeep, uMid, smoothstep(-0.2, 1.7, vHeight));
        base = mix(base, uShallow, smoothstep(1.2, 3.0, vHeight) * 0.62);

        vec3 keyDir = normalize(vec3(-0.38, 0.78, 0.52));
        float key = max(dot(N, keyDir), 0.0);
        float ridgeShade = 0.48 + 0.7 * pow(key, 1.35);
        base *= ridgeShade;

        vec3 warmBounce = vec3(0.16, 0.065, 0.02);
        base += warmBounce * pow(max(dot(N, normalize(vec3(-0.2, 0.1, 0.85))), 0.0), 2.2) * 0.55;

        vec3 reflected = reflect(-V, N);
        vec3 skyReflection = mix(uHorizon, uSky, smoothstep(-0.02, 0.5, reflected.y));
        vec3 col = mix(base, skyReflection, 0.055 + fresnel * 0.42);

        vec3 L = normalize(uSunDir);
        vec3 H = normalize(L + V);
        float ndh = max(dot(N, H), 0.0);
        float specular = pow(ndh, 300.0);
        float glitter = pow(ndh, 32.0);

        col += vec3(1.0, 0.46, 0.18) * specular * 2.4;
        col += vec3(1.0, 0.36, 0.12) * glitter * 0.12;

        float sunPath = pow(max(0.0, dot(normalize(vec3(V.x, 0.0, V.z)), normalize(vec3(uSunDir.x, 0.0, uSunDir.z)))), 13.0);
        col += vec3(1.0, 0.31, 0.10) * sunPath * 0.06 * (0.4 + fresnel);

        vec2 q = vWorldPos.xz;
        float n1 = fbm(q * 0.55 + vec2(uTime * 0.14, -uTime * 0.08));
        float n2 = fbm(q * 2.1 - vec2(uTime * 0.28, uTime * 0.05));
        float n3 = noise(q * 5.0 + vec2(uTime * 0.6, -uTime * 0.2));

        float zc = -3.35 + 0.68 * sin(uTime * 0.13);
        float relativeHeight = vHeight / max(vCrestH, 1.0);
        float crestBand = exp(-pow((vWorldPos.z - zc) / 0.6, 2.0));
        float crest = smoothstep(0.79, 0.965, relativeHeight + (n1 - 0.5) * 0.09);
        float caps = smoothstep(0.57, 0.8, n1 * 0.78 + n2 * 0.38) * smoothstep(0.58, 0.82, relativeHeight);
        float lace = smoothstep(0.58, 0.76, n1 * 0.62 + n2 * 0.5 + n3 * 0.12);
        float foam = clamp(crest * (0.22 + n2 * 0.8) + caps * 0.08 * crestBand + crestBand * crest * lace * 0.82, 0.0, 1.0);
        foam *= 0.72 + n3 * 0.28;

        float streaks = smoothstep(0.68, 0.8, noise(vec2(q.x * 1.55, q.y * 5.2 + uTime * 0.55))) * smoothstep(0.62, 0.8, relativeHeight) * 0.1;
        float faceLace = smoothstep(0.72, 0.84, noise(vec2(q.x * 3.6, q.y * 0.85 + uTime * 0.36))) * smoothstep(0.48, 0.66, relativeHeight) * smoothstep(0.82, 0.68, relativeHeight) * 0.04;

        float underCrest = exp(-pow((vWorldPos.z - zc - 1.0) / 2.5, 2.0));
        col *= 1.0 - underCrest * 0.1 * smoothstep(0.5, 2.0, vHeight);

        float dx = vWorldPos.x - uBoardPos.x;
        float dz = vWorldPos.z - uBoardPos.y;
        float contact = smoothstep(0.82, 0.16, length(vec2(dx * 1.2, dz * 2.1))) * smoothstep(0.0, 0.45, n2);
        float wake = exp(-pow(dz / 0.55, 2.0)) * exp(-max(dx, 0.0) * 0.34) * smoothstep(-0.45, 0.6, dx);
        float wakeFoam = contact * 0.4 + wake * 0.22 * smoothstep(0.25, 0.65, n1);
        wakeFoam *= 0.35 + n2 * 0.9;

        col = mix(col, uFoam, clamp(foam * 0.92 + streaks + faceLace + wakeFoam, 0.0, 0.92));
        col += uFoam * contact * 0.05;

        float distanceToCamera = length(cameraPosition.xz - vWorldPos.xz);
        float haze = smoothstep(52.0, 112.0, distanceToCamera);
        col = mix(col, uHorizon, haze);

        // A hint of sparkle in the foam so it feels like wet, moving light.
        col += vec3(1.0, 0.75, 0.48) * pow(n3, 7.0) * foam * 0.16;

        gl_FragColor = vec4(col, 1.0);
      }
    `
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  scene.add(mesh);

  function update(t, boardPosition) {
    uniforms.uTime.value = t;
    uniforms.uBoardPos.value.set(boardPosition.x, boardPosition.z);
  }

  return { mesh, material, uniforms, update };
}
