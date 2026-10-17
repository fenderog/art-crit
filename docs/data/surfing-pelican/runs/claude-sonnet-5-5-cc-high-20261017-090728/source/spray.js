import * as THREE from "three";

const vertex = /* glsl */ `
attribute float aSize;
attribute float aAlpha;
uniform float uScale;
varying float vAlpha;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * mv;
  gl_PointSize = aSize * uScale / max(-mv.z, 0.1);
  vAlpha = aAlpha;
}
`;

const fragment = /* glsl */ `
varying float vAlpha;
void main() {
  vec2 c = gl_PointCoord - 0.5;
  float d = length(c) * 2.0;
  float a = smoothstep(1.0, 0.15, d) * vAlpha;
  if (a < 0.003) discard;
  gl_FragColor = vec4(vec3(1.0, 0.96, 0.9) * 1.1, a);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createSpray(max = 3200) {
  const pos = new Float32Array(max * 3);
  const vel = new Float32Array(max * 3);
  const life = new Float32Array(max); // remaining
  const total = new Float32Array(max);
  const size = new Float32Array(max);
  const alpha = new Float32Array(max);
  const drag = new Float32Array(max);
  const grav = new Float32Array(max);
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setAttribute("aSize", new THREE.BufferAttribute(size, 1));
  g.setAttribute("aAlpha", new THREE.BufferAttribute(alpha, 1));
  const uniforms = { uScale: { value: 600 } };
  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: vertex,
    fragmentShader: fragment,
    transparent: true,
    depthWrite: false,
  });
  const points = new THREE.Points(g, material);
  points.frustumCulled = false;
  let head = 0;

  function emit(x, y, z, vx, vy, vz, sz, lf, gv = 7, dg = 0.6) {
    const i = head;
    head = (head + 1) % max;
    pos[i * 3] = x;
    pos[i * 3 + 1] = y;
    pos[i * 3 + 2] = z;
    vel[i * 3] = vx;
    vel[i * 3 + 1] = vy;
    vel[i * 3 + 2] = vz;
    size[i] = sz;
    life[i] = total[i] = lf;
    grav[i] = gv;
    drag[i] = dg;
  }

  function update(dt, groundAt) {
    for (let i = 0; i < max; i++) {
      if (life[i] <= 0) {
        alpha[i] = 0;
        continue;
      }
      life[i] -= dt;
      const k = Math.max(life[i], 0) / total[i];
      const dr = Math.exp(-drag[i] * dt);
      vel[i * 3] *= dr;
      vel[i * 3 + 1] = vel[i * 3 + 1] * dr - grav[i] * dt;
      vel[i * 3 + 2] *= dr;
      pos[i * 3] += vel[i * 3] * dt;
      pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
      pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
      alpha[i] = Math.min(1, (1 - k) * 12) * k * 0.75;
      size[i] *= 1 + dt * 0.5;
    }
    g.attributes.position.needsUpdate = true;
    g.attributes.aSize.needsUpdate = true;
    g.attributes.aAlpha.needsUpdate = true;
  }

  return { points, emit, update, uniforms };
}
