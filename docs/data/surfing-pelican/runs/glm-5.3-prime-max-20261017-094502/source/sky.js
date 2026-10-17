import * as THREE from 'three';

// Golden-hour gradient sky dome with a soft sun disc + glow (all in the shader).
export function createSky() {
  const geo = new THREE.SphereGeometry(500, 40, 24);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      top: { value: new THREE.Color('#2e5f9e') },
      mid: { value: new THREE.Color('#8fb8dd') },
      horizon: { value: new THREE.Color('#ffd9a0') },
      sunColor: { value: new THREE.Color('#fff3c4') },
      sunDir: { value: new THREE.Vector3(-0.45, 0.34, -0.85).normalize() },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 top;
      uniform vec3 mid;
      uniform vec3 horizon;
      uniform vec3 sunColor;
      uniform vec3 sunDir;
      varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir);
        float h = d.y;
        vec3 col = mix(horizon, mid, smoothstep(0.02, 0.30, h));
        col = mix(col, top, smoothstep(0.25, 0.75, h));
        vec3 below = mix(horizon, vec3(0.16, 0.32, 0.38), 0.6);
        col = mix(col, below, smoothstep(0.02, 0.20, -h));
        float s = clamp(dot(d, normalize(sunDir)), 0.0, 1.0);
        col += sunColor * pow(s, 600.0) * 1.3; // sun disc
        col += sunColor * pow(s, 24.0) * 0.30; // tight halo
        col += sunColor * pow(s, 3.0) * 0.10; // wide warm haze
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  return { mesh, sunDir: mat.uniforms.sunDir.value };
}
