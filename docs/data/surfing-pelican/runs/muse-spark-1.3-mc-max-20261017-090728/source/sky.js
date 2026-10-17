import * as THREE from 'three';

// Sky dome with a gradient + sun glow shader, drifting low-poly clouds,
// and two distant gulls soaring in slow circles. All procedural.

const SUN_DIR = new THREE.Vector3(10, 14, 7).normalize();

function buildSkyDome() {
  const geo = new THREE.SphereGeometry(230, 24, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: {
      topColor: { value: new THREE.Color(0x2f7fc9) },
      midColor: { value: new THREE.Color(0x8fd4ec) },
      botColor: { value: new THREE.Color(0xfdf1dc) },
      sunDir: { value: SUN_DIR },
    },
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vDir;
      uniform vec3 topColor;
      uniform vec3 midColor;
      uniform vec3 botColor;
      uniform vec3 sunDir;
      void main() {
        float h = clamp(normalize(vDir).y, -1.0, 1.0);
        vec3 col = mix(botColor, midColor, smoothstep(0.0, 0.25, h));
        col = mix(col, topColor, smoothstep(0.2, 0.75, h));
        col = mix(vec3(0.85, 0.93, 0.94), col, smoothstep(-0.15, 0.02, h));
        float s = max(dot(normalize(vDir), normalize(sunDir)), 0.0);
        col += vec3(1.0, 0.9, 0.75) * (pow(s, 800.0) * 1.2 + pow(s, 10.0) * 0.18);
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });
  return new THREE.Mesh(geo, mat);
}

function buildCloud(seed) {
  let s = seed >>> 0;
  const rng = () => {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let v = Math.imul(s ^ (s >>> 15), 1 | s);
    v = (v + Math.imul(v ^ (v >>> 7), 61 | v)) ^ v;
    return ((v ^ (v >>> 14)) >>> 0) / 4294967296;
  };
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
  const cloud = new THREE.Group();
  const n = 4 + Math.floor(rng() * 3);
  for (let i = 0; i < n; i++) {
    const r = 1.2 + rng() * 1.6;
    const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 9, 7), mat);
    puff.position.set((i - n / 2) * 2.0 + (rng() - 0.5), (rng() - 0.5) * 0.8, (rng() - 0.5) * 1.6);
    puff.scale.y = 0.55;
    cloud.add(puff);
  }
  return cloud;
}

function buildGull() {
  const mat = new THREE.MeshStandardMaterial({ color: 0x3a4750, roughness: 0.9 });
  const gull = new THREE.Group();
  const bodyGeo = new THREE.SphereGeometry(0.18, 8, 6);
  const body = new THREE.Mesh(bodyGeo, mat);
  body.scale.set(1.8, 0.5, 0.5);
  gull.add(body);
  const wings = [];
  for (const side of [1, -1]) {
    const pivot = new THREE.Group();
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 0.55), mat);
    w.position.z = side * 0.32;
    pivot.add(w);
    gull.add(pivot);
    wings.push({ pivot, side });
  }
  return { gull, wings };
}

export function createSky(scene) {
  scene.add(buildSkyDome());

  const clouds = [];
  const cloudDefs = [
    { x: -30, y: 17, z: -28, s: 1.4, v: 0.45 },
    { x: 8, y: 21, z: -38, s: 1.9, v: 0.3 },
    { x: 38, y: 15, z: -20, s: 1.1, v: 0.55 },
    { x: -8, y: 19, z: 22, s: 1.3, v: 0.4 },
  ];
  cloudDefs.forEach((d, i) => {
    const c = buildCloud(100 + i * 17);
    c.position.set(d.x, d.y, d.z);
    c.scale.setScalar(d.s);
    scene.add(c);
    clouds.push({ c, v: d.v });
  });

  const gulls = [
    { ...buildGull(), cx: -6, cy: 9, cz: -10, r: 9, w: 0.14, p: 0 },
    { ...buildGull(), cx: 7, cy: 11, cz: -14, r: 12, w: -0.1, p: 2.4 },
  ];
  for (const g of gulls) scene.add(g.gull);

  function update(t, dt) {
    for (const { c, v } of clouds) {
      c.position.x -= dt * v;
      if (c.position.x < -70) c.position.x = 70;
    }
    for (const g of gulls) {
      const a = g.w * t + g.p;
      const x = g.cx + g.r * Math.cos(a);
      const z = g.cz + g.r * 0.6 * Math.sin(a);
      g.gull.position.set(x, g.cy + 0.5 * Math.sin(2 * a), z);
      // Face along the direction of travel.
      const vx = -Math.sin(a) * Math.sign(g.w);
      const vz = 0.6 * Math.cos(a) * Math.sign(g.w);
      g.gull.rotation.y = Math.atan2(-vz, vx);
      const flap = 0.15 + 0.55 * (0.5 + 0.5 * Math.sin(t * 6 + g.p * 3));
      for (const { pivot, side } of g.wings) pivot.rotation.x = -side * flap;
    }
  }

  return { update };
}
