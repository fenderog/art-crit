import * as THREE from "three";

function cloudTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const g = canvas.getContext("2d");
  const glow = g.createRadialGradient(128, 128, 10, 128, 128, 128);
  glow.addColorStop(0, "rgba(255,255,255,0.95)");
  glow.addColorStop(0.35, "rgba(255,248,240,0.55)");
  glow.addColorStop(0.7, "rgba(255,236,220,0.16)");
  glow.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = glow;
  g.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function createBird() {
  const mat = new THREE.MeshBasicMaterial({ color: 0x2c241e, side: THREE.DoubleSide });
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  shape.lineTo(0.72, 0.16);
  shape.lineTo(1.05, 0.02);
  shape.lineTo(0.62, -0.03);
  shape.lineTo(0, 0);
  const geo = new THREE.ShapeGeometry(shape);
  const group = new THREE.Group();
  const left = new THREE.Mesh(geo, mat);
  const right = new THREE.Mesh(geo, mat);
  right.scale.x = -1;
  group.add(left, right);
  group.userData.left = left;
  group.userData.right = right;
  return group;
}

export function createSky() {
  const uniforms = {
    uSunDir: { value: new THREE.Vector3(0.2, 0.7, 0.2) },
    uZenith: { value: new THREE.Color(0x35588a) },
    uMid: { value: new THREE.Color(0xf0b48a) },
    uHorizon: { value: new THREE.Color(0xffc48a) },
    uWarm: { value: new THREE.Color(0xffe2b8) },
  };
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(480, 32, 20),
    new THREE.ShaderMaterial({
      uniforms,
      side: THREE.BackSide,
      depthWrite: false,
      vertexShader: /* glsl */ `
        varying vec3 vDir;
        void main() {
          vDir = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        varying vec3 vDir;
        uniform vec3 uSunDir;
        uniform vec3 uZenith;
        uniform vec3 uMid;
        uniform vec3 uHorizon;
        uniform vec3 uWarm;
        void main() {
          vec3 dir = normalize(vDir);
          float h = dir.y;
          vec3 col = mix(uHorizon, uMid, smoothstep(0.0, 0.22, h));
          col = mix(col, uZenith, smoothstep(0.28, 0.72, h));
          col = mix(col, uHorizon * 0.72, smoothstep(0.02, -0.2, h));
          vec3 sun = normalize(uSunDir);
          float disc = pow(max(dot(dir, sun), 0.0), 1600.0);
          float glow = pow(max(dot(dir, sun), 0.0), 7.0);
          col += uWarm * glow * 0.9;
          col += vec3(1.0, 0.97, 0.92) * disc;
          gl_FragColor = vec4(col, 1.0);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }
      `,
    }),
  );
  mesh.renderOrder = -2;
  mesh.frustumCulled = false;

  const clouds = new THREE.Group();
  const tex = cloudTexture();
  const cloudMat = new THREE.MeshBasicMaterial({
    map: tex,
    transparent: true,
    depthWrite: false,
    color: 0xfff1e4,
    opacity: 0.85,
    side: THREE.DoubleSide,
  });
  const cloudLayout = [
    [-30, 28, 36, 34, 11],
    [18, 34, 48, 42, 13],
    [46, 22, 10, 26, 8],
    [-8, 40, -30, 30, 9],
    [60, 30, -18, 38, 12],
    [-50, 24, -8, 28, 8],
  ];
  for (const [x, y, z, sx, sy] of cloudLayout) {
    const puff = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), cloudMat);
    puff.position.set(x, y, z);
    puff.scale.set(sx, sy, 1);
    clouds.add(puff);
  }

  const birds = [];
  for (let i = 0; i < 4; i++) {
    const bird = createBird();
    bird.userData.radius = 22 + i * 6;
    bird.userData.speed = 0.12 + i * 0.03;
    bird.userData.phase = i * 1.4;
    bird.userData.height = 12 + i * 2.2;
    birds.push(bird);
    clouds.add(bird);
  }

  return {
    mesh,
    clouds,
    update(t, camera, sunDir) {
      mesh.position.copy(camera.position);
      clouds.position.set(camera.position.x, 0, camera.position.z);
      uniforms.uSunDir.value.copy(sunDir);
      for (const puff of clouds.children) {
        if (!puff.userData.radius) {
          puff.lookAt(camera.position.x, puff.position.y, camera.position.z);
        }
      }
      for (const bird of birds) {
        const a = t * bird.userData.speed + bird.userData.phase;
        bird.position.set(
          Math.cos(a) * bird.userData.radius,
          bird.userData.height + Math.sin(a * 2) * 0.4,
          Math.sin(a) * bird.userData.radius * 0.65 + 18,
        );
        bird.rotation.y = -a + Math.PI / 2;
        const flap = Math.sin(t * 6 + bird.userData.phase) * 0.45;
        bird.userData.left.rotation.z = flap;
        bird.userData.right.rotation.z = -flap;
      }
    },
  };
}
