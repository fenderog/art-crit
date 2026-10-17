import * as THREE from 'three';
import { PALETTE } from './theme.js';
import { glslWaveChunk } from './waves.js';

// The ocean: one big plane whose vertices are displaced by the shared wave
// field. Normals come from the analytic gradient, plus tiny fragment-level
// ripple normals for sparkle. Foam appears on crests and the steep swell face;
// distance fades into the same warm haze as the sky horizon.
export function createOcean(sunDir) {
  const geo = new THREE.PlaneGeometry(560, 560, 380, 380);
  geo.rotateX(-Math.PI / 2);

  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: sunDir.clone() },
    uCamPos: { value: new THREE.Vector3() },
    uDeep: { value: new THREE.Color(PALETTE.waterDeep) },
    uShallow: { value: new THREE.Color(PALETTE.waterShallow) },
    uSkyTint: { value: new THREE.Color(PALETTE.waterSky) },
    uSun: { value: new THREE.Color(PALETTE.sun) },
    // fade into the sky's horizon color so water and sky meet seamlessly
    uFog: { value: new THREE.Color(PALETTE.horizon) },
  };

  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying vec3 vWorld;
      varying vec3 vN;
      varying float vH;
      ${glslWaveChunk()}
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        float h = waveH(wp.xz, uTime);
        wp.y += h;
        vec2 g = waveGrad(wp.xz, uTime);
        vN = normalize(vec3(-g.x, 1.0, -g.y));
        vH = h;
        vWorld = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform vec3 uSunDir;
      uniform vec3 uCamPos;
      uniform vec3 uDeep;
      uniform vec3 uShallow;
      uniform vec3 uSkyTint;
      uniform vec3 uSun;
      uniform vec3 uFog;
      varying vec3 vWorld;
      varying vec3 vN;
      varying float vH;
      void main() {
        vec2 p = vWorld.xz;
        float t = uTime;
        vec3 N = normalize(vN);

        // fine ripples: normals only (too small to displace geometry)
        float th1 = dot(vec2(0.85, 0.53), p) * 2.4166 - 2.6583 * t;
        float th2 = dot(vec2(0.28, -0.96), p) * 3.6959 - 3.6959 * t + 1.7;
        float th3 = dot(vec2(-0.60, 0.80), p) * 6.9813 - 6.2831 * t + 3.9;
        vec2 g = vec2(0.0);
        g += vec2(0.85, 0.53) * (0.045 * 2.4166 * cos(th1));
        g += vec2(0.28, -0.96) * (0.030 * 3.6959 * cos(th2));
        g += vec2(-0.60, 0.80) * (0.018 * 6.9813 * cos(th3));
        N = normalize(N + vec3(-g.x, 0.0, -g.y) * 1.5);

        vec3 V = normalize(uCamPos - vWorld);
        float fres = pow(1.0 - max(dot(N, V), 0.0), 3.0);
        vec3 col = mix(uDeep, uShallow, clamp((vH + 1.3) * 0.32, 0.0, 1.0));
        col = mix(col, uSkyTint, clamp(fres * 0.65, 0.0, 1.0));

        // sun glitter
        vec3 R = reflect(-normalize(uSunDir), N);
        float sparkle = 0.55 + 0.45 * sin(th1 * 3.7 + th2 * 2.9);
        col += uSun * pow(max(dot(R, V), 0.0), 150.0) * (1.4 + 2.2 * sparkle);

        // foam: noisy mask on crests, extra streaks on the steep face
        float n = sin(p.x * 0.55 + p.y * 0.35 - t * 0.9) * sin(p.y * 0.62 - p.x * 0.28 + t * 0.7);
        n += 0.6 * sin(p.x * 1.31 - p.y * 0.77 + t * 1.3);
        float crest = smoothstep(1.28, 1.95, vH);
        float steep = clamp(length(vN.xz) * 1.8, 0.0, 1.0);
        float foam = crest * clamp(0.30 + 0.55 * n, 0.0, 1.0) + crest * steep * 0.55;
        col = mix(col, vec3(0.93, 0.97, 0.96), clamp(foam, 0.0, 1.0) * 0.85);

        // warm haze toward the horizon (matches the sky)
        float dist = distance(uCamPos, vWorld);
        col = mix(col, uFog, smoothstep(80.0, 235.0, dist));

        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  return { mesh, uniforms };
}
