import * as THREE from 'three';

const CAPACITY = 420;

const sprayVertexShader = /* glsl */ `
  uniform float uScale;
  attribute float aSize;
  attribute float aAlpha;

  varying float vAlpha;

  void main() {
    vec4 viewPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = clamp(aSize * uScale / max(1.0, -viewPosition.z), 1.0, 54.0);
    vAlpha = aAlpha;
    gl_Position = projectionMatrix * viewPosition;
  }
`;

const sprayFragmentShader = /* glsl */ `
  varying float vAlpha;

  void main() {
    float distanceToCentre = length(gl_PointCoord - vec2(0.5));
    float mask = smoothstep(0.51, 0.06, distanceToCentre);
    float core = smoothstep(0.34, 0.0, distanceToCentre);
    vec3 colour = mix(vec3(0.69, 0.87, 0.86), vec3(1.0, 0.98, 0.91), core);
    gl_FragColor = vec4(colour, mask * vAlpha);

    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

export class SpraySystem {
  constructor(scene, renderer, camera) {
    this.scene = scene;
    this.renderer = renderer;
    this.camera = camera;

    this.positions = new Float32Array(CAPACITY * 3);
    this.sizes = new Float32Array(CAPACITY);
    this.alphas = new Float32Array(CAPACITY);
    this.velocities = new Float32Array(CAPACITY * 3);
    this.life = new Float32Array(CAPACITY);
    this.maxLife = new Float32Array(CAPACITY);
    this.baseSize = new Float32Array(CAPACITY);
    this.cursor = 0;
    this.emitAccumulator = 0;
    this.tmpOrigin = new THREE.Vector3();
    this.forward = new THREE.Vector3();
    this.side = new THREE.Vector3();

    for (let i = 0; i < CAPACITY; i++) {
      this.positions[i * 3 + 1] = -100;
    }

    const geometry = new THREE.BufferGeometry();
    const positionAttribute = new THREE.BufferAttribute(this.positions, 3);
    positionAttribute.setUsage(THREE.DynamicDrawUsage);
    const sizeAttribute = new THREE.BufferAttribute(this.sizes, 1);
    sizeAttribute.setUsage(THREE.DynamicDrawUsage);
    const alphaAttribute = new THREE.BufferAttribute(this.alphas, 1);
    alphaAttribute.setUsage(THREE.DynamicDrawUsage);
    geometry.setAttribute('position', positionAttribute);
    geometry.setAttribute('aSize', sizeAttribute);
    geometry.setAttribute('aAlpha', alphaAttribute);
    this.geometry = geometry;

    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uScale: { value: 1000 }
      },
      vertexShader: sprayVertexShader,
      fragmentShader: sprayFragmentShader,
      transparent: true,
      depthWrite: false,
      depthTest: true,
      blending: THREE.NormalBlending,
      toneMapped: true
    });

    this.points = new THREE.Points(geometry, this.material);
    this.points.frustumCulled = false;
    scene.add(this.points);
  }

  spawn(rider, burst = false) {
    const i = this.cursor;
    this.cursor = (this.cursor + 1) % CAPACITY;

    const sideSign = Math.random() < 0.5 ? -1 : 1;
    const isBow = Math.random() < 0.3;

    const localX = isBow
      ? sideSign * (0.49 + Math.random() * 0.12)
      : sideSign * (0.40 + Math.random() * 0.18);
    const localZ = isBow
      ? 0.75 + Math.random() * 0.95
      : -1.55 + Math.random() * 2.15;

    this.tmpOrigin.set(localX, 0.075 + Math.random() * 0.07, localZ);
    rider.localToWorld(this.tmpOrigin);

    this.positions[i * 3] = this.tmpOrigin.x;
    this.positions[i * 3 + 1] = this.tmpOrigin.y;
    this.positions[i * 3 + 2] = this.tmpOrigin.z;

    this.forward.set(0, 0, 1).applyQuaternion(rider.quaternion);
    this.side.set(sideSign, 0, 0).applyQuaternion(rider.quaternion);

    const backwards = 1.2 + Math.random() * 2.0 + (burst ? 1.3 : 0);
    const sideways = sideSign * (0.55 + Math.random() * 1.45) + (isBow ? sideSign * 0.5 : 0);
    const upwards = 0.75 + Math.random() * (burst ? 3.4 : 2.2);

    this.velocities[i * 3] =
      -this.forward.x * backwards +
      this.side.x * sideways +
      (Math.random() - 0.5) * 0.55;
    this.velocities[i * 3 + 1] = upwards;
    this.velocities[i * 3 + 2] =
      -this.forward.z * backwards +
      this.side.z * sideways +
      (Math.random() - 0.5) * 0.55;

    const lifespan = 0.58 + Math.random() * 0.9 + (burst ? 0.12 : 0);
    this.life[i] = lifespan;
    this.maxLife[i] = lifespan;
    this.baseSize[i] = 0.026 + Math.random() * (burst ? 0.085 : 0.055);
    this.sizes[i] = this.baseSize[i];
    this.alphas[i] = 0.9;
  }

  burst(rider, count = 72) {
    for (let i = 0; i < count; i++) this.spawn(rider, true);
  }

  update(dt, rider) {
    this.material.uniforms.uScale.value =
      this.renderer.domElement.height /
      (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov * 0.5)));

    this.emitAccumulator += dt * 48;
    while (this.emitAccumulator >= 1) {
      this.spawn(rider);
      this.emitAccumulator -= 1;
    }

    for (let i = 0; i < CAPACITY; i++) {
      if (this.life[i] <= 0) {
        this.alphas[i] = 0;
        continue;
      }

      this.life[i] -= dt;
      if (this.life[i] <= 0) {
        this.alphas[i] = 0;
        this.positions[i * 3 + 1] = -100;
        continue;
      }

      this.velocities[i * 3 + 1] -= 4.6 * dt;
      this.velocities[i * 3] *= 0.988;
      this.velocities[i * 3 + 2] *= 0.988;

      this.positions[i * 3] += this.velocities[i * 3] * dt;
      this.positions[i * 3 + 1] += this.velocities[i * 3 + 1] * dt;
      this.positions[i * 3 + 2] += this.velocities[i * 3 + 2] * dt;

      const age = this.maxLife[i] - this.life[i];
      this.sizes[i] = this.baseSize[i] * (1.0 + age * 0.46);
      this.alphas[i] =
        Math.min(1.0, age * 12.0) *
        Math.pow(Math.max(0.0, this.life[i] / this.maxLife[i]), 0.7) *
        0.85;
    }

    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.attributes.aSize.needsUpdate = true;
    this.geometry.attributes.aAlpha.needsUpdate = true;
  }
}
