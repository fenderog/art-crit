import * as THREE from "three";

const COUNT = 520;

function softCircle() {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 64;
  const g = canvas.getContext("2d");
  const glow = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  glow.addColorStop(0, "rgba(255,255,255,1)");
  glow.addColorStop(0.35, "rgba(255,255,255,0.65)");
  glow.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = glow;
  g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createSpray() {
  const positions = new Float32Array(COUNT * 3);
  const lifeAttr = new Float32Array(COUNT);
  const sizeAttr = new Float32Array(COUNT);
  const alphaAttr = new Float32Array(COUNT);
  const vel = new Float32Array(COUNT * 3);
  const life = new Float32Array(COUNT);
  const maxLife = new Float32Array(COUNT);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setAttribute("aLife", new THREE.BufferAttribute(lifeAttr, 1));
  geo.setAttribute("aSize", new THREE.BufferAttribute(sizeAttr, 1));
  geo.setAttribute("aAlpha", new THREE.BufferAttribute(alphaAttr, 1));

  const material = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms: { uMap: { value: softCircle() } },
    vertexShader: /* glsl */ `
      attribute float aLife;
      attribute float aSize;
      attribute float aAlpha;
      varying float vLife;
      varying float vAlpha;
      void main() {
        vLife = aLife;
        vAlpha = aAlpha;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aSize * (190.0 / max(1.0, -mv.z));
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap;
      varying float vLife;
      varying float vAlpha;
      void main() {
        float tex = texture2D(uMap, gl_PointCoord).a;
        float fade = smoothstep(0.0, 0.18, vLife);
        float alpha = tex * fade * vAlpha;
        if (alpha < 0.02) discard;
        gl_FragColor = vec4(vec3(0.96, 0.98, 1.0), alpha);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });

  const points = new THREE.Points(geo, material);
  points.frustumCulled = false;
  points.renderOrder = 3;

  const _origin = new THREE.Vector3();
  const _velocity = new THREE.Vector3();

  function spawn(i, origin, velocity, size, span, alpha) {
    positions[i * 3] = origin.x;
    positions[i * 3 + 1] = origin.y;
    positions[i * 3 + 2] = origin.z;
    vel[i * 3] = velocity.x;
    vel[i * 3 + 1] = velocity.y;
    vel[i * 3 + 2] = velocity.z;
    life[i] = span;
    maxLife[i] = span;
    sizeAttr[i] = size;
    alphaAttr[i] = alpha;
  }

  for (let i = 0; i < COUNT; i++) life[i] = 0;

  return {
    points,
    update(dt, sources) {
      const { tail, rail, lip, back, left } = sources;
      let budget = 10;
      for (let i = 0; i < COUNT; i++) {
        if (life[i] <= 0) {
          if (budget <= 0) continue;
          budget -= 1;
          const roll = Math.random();
          if (roll < 0.55) {
            _origin.copy(tail);
            _origin.x += (Math.random() - 0.5) * 0.12;
            _origin.z += (Math.random() - 0.5) * 0.12;
            _velocity.copy(back).multiplyScalar(1.4 + Math.random() * 2.2);
            _velocity.y += 1.4 + Math.random() * 2.4;
            _velocity.addScaledVector(left, (Math.random() - 0.35) * 1.6);
            spawn(i, _origin, _velocity, 0.18 + Math.random() * 0.22, 0.45 + Math.random() * 0.45, 0.75);
          } else if (roll < 0.82) {
            _origin.copy(rail);
            _velocity.copy(left).multiplyScalar(0.8 + Math.random() * 1.4);
            _velocity.addScaledVector(back, 0.6 + Math.random());
            _velocity.y += 1.1 + Math.random() * 2.1;
            spawn(i, _origin, _velocity, 0.16 + Math.random() * 0.2, 0.4 + Math.random() * 0.4, 0.7);
          } else {
            _origin.copy(lip);
            _origin.x += (Math.random() - 0.5) * 1.4;
            _origin.y += Math.random() * 0.6;
            _velocity.copy(back).multiplyScalar(0.3 + Math.random());
            _velocity.y += 0.6 + Math.random() * 1.6;
            _velocity.addScaledVector(left, (Math.random() - 0.5) * 0.8);
            spawn(i, _origin, _velocity, 0.45 + Math.random() * 0.55, 0.8 + Math.random() * 0.7, 0.28);
          }
        } else {
          vel[i * 3 + 1] -= 8.5 * dt;
          positions[i * 3] += vel[i * 3] * dt;
          positions[i * 3 + 1] += vel[i * 3 + 1] * dt;
          positions[i * 3 + 2] += vel[i * 3 + 2] * dt;
          life[i] -= dt;
        }
        lifeAttr[i] = life[i] > 0 ? life[i] / maxLife[i] : 0;
      }
      geo.attributes.position.needsUpdate = true;
      geo.attributes.aLife.needsUpdate = true;
      geo.attributes.aSize.needsUpdate = true;
      geo.attributes.aAlpha.needsUpdate = true;
    },
  };
}
