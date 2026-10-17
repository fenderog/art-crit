import * as THREE from 'three';

// Gradient sky dome with a soft sun glow, plus a few drifting clouds.
export function createSky(sunDirection) {
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x1c6fb0) },
      midColor: { value: new THREE.Color(0x77b6d8) },
      bottomColor: { value: new THREE.Color(0xffdcb0) },
      sunDir: { value: sunDirection.clone().normalize() },
      sunColor: { value: new THREE.Color(0xfff1c8) },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      varying vec3 vDir;
      uniform vec3 topColor;
      uniform vec3 midColor;
      uniform vec3 bottomColor;
      uniform vec3 sunDir;
      uniform vec3 sunColor;
      void main() {
        float h = clamp(vDir.y, -1.0, 1.0);
        vec3 col = mix(bottomColor, midColor, smoothstep(-0.05, 0.28, h));
        col = mix(col, topColor, smoothstep(0.22, 0.85, h));
        float s = max(dot(vDir, normalize(sunDir)), 0.0);
        col += sunColor * pow(s, 6.0) * 0.28;
        col += sunColor * pow(s, 220.0) * 2.0;
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });

  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMat);
  sky.frustumCulled = false;

  const root = new THREE.Group();
  root.add(sky);

  // Clouds: clusters of soft spheres drifting slowly across the sky.
  const cloudMat = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 1.0,
    metalness: 0.0,
    transparent: true,
    opacity: 0.92,
    fog: true,
  });

  const clouds = [];
  const cloudGroup = new THREE.Group();
  root.add(cloudGroup);

  const puff = new THREE.SphereGeometry(1, 16, 12);

  for (let i = 0; i < 8; i++) {
    const cloud = new THREE.Group();
    const puffs = 4 + Math.floor(Math.random() * 4);
    for (let p = 0; p < puffs; p++) {
      const m = new THREE.Mesh(puff, cloudMat);
      const s = 2.5 + Math.random() * 3.5;
      m.scale.set(s * (1 + Math.random() * 0.6), s * 0.7, s);
      m.position.set(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 1.5,
        (Math.random() - 0.5) * 5
      );
      cloud.add(m);
    }
    const angle = Math.random() * Math.PI * 2;
    const radius = 90 + Math.random() * 120;
    cloud.position.set(
      Math.cos(angle) * radius,
      34 + Math.random() * 34,
      Math.sin(angle) * radius
    );
    cloud.userData.speed = 0.6 + Math.random() * 1.0;
    clouds.push(cloud);
    cloudGroup.add(cloud);
  }

  function update(dt) {
    for (const cloud of clouds) {
      cloud.position.x += cloud.userData.speed * dt;
      if (cloud.position.x > 260) cloud.position.x = -260;
    }
  }

  return { root, update };
}
