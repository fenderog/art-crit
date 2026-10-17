import * as THREE from "three";
import { PALETTE } from "./palette.js";

/**
 * Sky dome: vertical gradient + sun disc + wide golden bloom + a horizon haze
 * band that matches the ocean fog colour exactly, so sea and sky melt into
 * each other. No textures — everything is evaluated in the shader.
 */
export function createSky(sunDir) {
  const uniforms = {
    uSunDir: { value: sunDir.clone() },
    uZenith: { value: new THREE.Color(PALETTE.zenith) },
    uMid: { value: new THREE.Color(PALETTE.midSky) },
    uHorizon: { value: new THREE.Color(PALETTE.horizonSky) },
    uHaze: { value: new THREE.Color(PALETTE.haze) },
    uSunCore: { value: new THREE.Color(PALETTE.sunCore) },
    uSunGlow: { value: new THREE.Color(PALETTE.sunGlow) },
    uTime: { value: 0 },
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
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        gl_Position.z = gl_Position.w;   // pin to the far plane
      }
    `,
    fragmentShader: /* glsl */ `
      precision highp float;
      uniform vec3 uSunDir, uZenith, uMid, uHorizon, uHaze, uSunCore, uSunGlow;
      uniform float uTime;
      varying vec3 vDir;

      float hash(vec2 p) {
        return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
      }
      float vnoise(vec2 p) {
        vec2 i = floor(p), f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        float a = hash(i), b = hash(i + vec2(1.0, 0.0));
        float c = hash(i + vec2(0.0, 1.0)), d = hash(i + vec2(1.0, 1.0));
        return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
      }

      void main() {
        vec3 dir = normalize(vDir);
        float h = dir.y;

        // --- vertical gradient -------------------------------------------
        vec3 col = mix(uHorizon, uMid, smoothstep(0.0, 0.22, h));
        col = mix(col, uZenith, smoothstep(0.14, 0.85, h));

        // warm band hugging the horizon
        float band = exp(-abs(h) * 13.0);
        col = mix(col, uHaze, band * 0.55);

        // --- sun ----------------------------------------------------------
        float sd = max(dot(dir, uSunDir), 0.0);
        float disc = smoothstep(0.99885, 0.99945, sd);
        float core = pow(sd, 900.0);
        float glow = pow(sd, 42.0);
        float wide = pow(sd, 6.0);
        col += uSunCore * (disc * 3.2 + core * 1.6);
        col += uSunGlow * (glow * 0.55 + wide * 0.16);

        // --- soft cloud wisps (procedural, drift slowly) -------------------
        if (h > 0.005) {
          vec2 uv = dir.xz / (h + 0.14);
          float t = uTime * 0.006;
          float n = vnoise(uv * 0.55 + vec2(t, -t * 0.6));
          n += 0.5 * vnoise(uv * 1.7 + vec2(-t * 1.7, t * 0.9));
          n += 0.25 * vnoise(uv * 4.3 + vec2(t * 2.3, t * 1.1));
          n /= 1.75;
          float wisp = smoothstep(0.52, 0.92, n) * smoothstep(0.005, 0.16, h) * (1.0 - smoothstep(0.34, 0.9, h));
          vec3 cloudCol = mix(vec3(1.0, 0.87, 0.76), vec3(1.0, 0.98, 0.94), smoothstep(0.0, 0.3, h));
          cloudCol += uSunGlow * pow(sd, 8.0) * 0.5;
          col = mix(col, cloudCol, wisp * 0.5);
        }

        // --- below the horizon: pure haze so it meets the fogged sea -------
        col = mix(col, uHaze * 0.92, smoothstep(0.0, -0.10, h));

        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });

  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), material);
  mesh.scale.setScalar(9000);
  mesh.frustumCulled = false;
  mesh.renderOrder = -1000;
  mesh.name = "sky";

  return { mesh, uniforms, material };
}
