import * as THREE from "three";

export const SUN_DIR = new THREE.Vector3(0.15, 0.62, -0.55).normalize();

const HORIZON = new THREE.Color("#f3b48a");
const ZENITH = new THREE.Color("#6aa6dc");
const NADIR = new THREE.Color("#e7c4a4");

export function createSky() {
  const geo = new THREE.SphereGeometry(180, 28, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    fog: false,
    depthWrite: false,
    uniforms: {
      sunDir: { value: SUN_DIR },
      horizon: { value: HORIZON },
      zenith: { value: ZENITH },
      nadir: { value: NADIR },
    },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vec4 worldPos = modelMatrix * vec4(position, 1.0);
        vDir = worldPos.xyz - cameraPosition;
        gl_Position = projectionMatrix * viewMatrix * worldPos;
      }
    `,
    fragmentShader: `
      varying vec3 vDir;
      uniform vec3 sunDir;
      uniform vec3 horizon;
      uniform vec3 zenith;
      uniform vec3 nadir;
      void main() {
        vec3 d = normalize(vDir);
        float h = d.y;
        vec3 col = mix(nadir, horizon, smoothstep(-0.35, 0.02, h));
        col = mix(col, zenith, smoothstep(-0.02, 0.28, h));
        float sun = pow(max(dot(d, sunDir), 0.0), 180.0);
        float glow = pow(max(dot(d, sunDir), 0.0), 6.0);
        col += vec3(1.0, 0.92, 0.78) * sun * 1.5;
        col += vec3(1.0, 0.68, 0.42) * glow * 0.38;
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  const dome = new THREE.Mesh(geo, mat);
  dome.frustumCulled = false;
  dome.renderOrder = -1;

  const clouds = new THREE.Group();
  const puffGeo = new THREE.SphereGeometry(1, 12, 10);
  const puffMat = new THREE.MeshBasicMaterial({
    color: 0xfff4ea,
    transparent: true,
    opacity: 0.82,
    fog: false,
    depthWrite: false,
  });
  const banks = [
    { x: -30, y: 16, z: -18, s: 3.2 },
    { x: 8, y: 18, z: -28, s: 4.1 },
    { x: 36, y: 14, z: -8, s: 2.4 },
    { x: -12, y: 20, z: 24, s: 2.8 },
    { x: 22, y: 17, z: 18, s: 3.4 },
  ];
  const movers = [];
  for (const bank of banks) {
    const g = new THREE.Group();
    const blobs = [
      [0, 0, 0, 1],
      [0.9, 0.15, 0.2, 0.75],
      [-0.85, 0.05, -0.1, 0.7],
      [0.3, 0.35, -0.15, 0.62],
    ];
    for (const [x, y, z, s] of blobs) {
      const puff = new THREE.Mesh(puffGeo, puffMat);
      puff.position.set(x * bank.s, y * bank.s, z * bank.s);
      puff.scale.setScalar(s * bank.s);
      g.add(puff);
    }
    g.userData.x0 = bank.x;
    g.userData.phase = bank.x;
    g.position.set(bank.x, bank.y, bank.z);
    clouds.add(g);
    movers.push(g);
  }

  function update(t) {
    for (const g of movers) {
      const span = 150;
      g.position.x = ((g.userData.x0 - t * 1.4) % span + span) % span - span / 2;
    }
  }

  return { dome, clouds, update, horizon: HORIZON };
}
