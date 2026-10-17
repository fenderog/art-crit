import * as THREE from "three";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

// Final display-referred colour grade: contrast, saturation, split tone, vignette, dither.
export function createGradePass() {
  return new ShaderPass({
    uniforms: {
      tDiffuse: { value: null },
      uTime: { value: 0 },
      uRes: { value: new THREE.Vector2(1, 1) },
      uContrast: { value: 1.08 },
      uSat: { value: 1.12 },
      uVig: { value: 0.35 },
      uTone: { value: 1.0 },
    },
    vertexShader: /* glsl */ `
      varying vec2 vUv;
      void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D tDiffuse;
      uniform float uTime;
      uniform vec2 uRes;
      uniform float uContrast;
      uniform float uSat;
      uniform float uVig;
      uniform float uTone;
      varying vec2 vUv;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
      void main() {
        vec3 c = texture2D(tDiffuse, vUv).rgb;
        c = (c - 0.5) * uContrast + 0.5;
        float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
        c = mix(vec3(l), c, uSat);
        c += vec3(-0.005, 0.012, 0.028) * (1.0 - l) * uTone;
        c += vec3(0.03, 0.014, -0.012) * l * uTone;
        vec2 q = (vUv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
        float v = smoothstep(1.05, 0.25, length(q));
        c *= mix(vec3(1.0), mix(vec3(0.72, 0.8, 0.94), vec3(1.0), v), uVig);
        c += (hash(vUv * uRes + fract(uTime)) - 0.5) / 255.0;
        gl_FragColor = vec4(max(c, 0.0), 1.0);
      }
    `,
  });
}
