import * as THREE from "three";

// Ocean setting: a big curling wave behind the surfer, animated open water
// in front, gradient sky, sun, drifting clouds, and distant gulls.

const waterMat = new THREE.MeshStandardMaterial({
  color: 0x12808f, roughness: 0.42, metalness: 0.05,
});
const waveMat = new THREE.MeshStandardMaterial({
  color: 0x0f7d90, roughness: 0.55, metalness: 0.02, side: THREE.DoubleSide,
});
const foamMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9 });

// Cross-section of the wave in the (z, y) plane: rises from the trough in
// front, steepens, and curls over toward the camera at the lip.
const PROFILE = [
  [2.6, -0.25], [1.4, 0.0], [0.55, 0.55], [0.0, 1.35], [-0.3, 2.4],
  [-0.38, 3.45], [-0.15, 4.35], [0.35, 5.0], [1.0, 5.32], [1.62, 5.22],
  [2.02, 4.82], [2.08, 4.32], [1.78, 3.95], [1.3, 3.82],
];

function createWave() {
  const group = new THREE.Group();
  const curve = new THREE.CatmullRomCurve3(
    PROFILE.map(([z, y]) => new THREE.Vector3(0, y, z)));
  const profilePts = curve.getPoints(56);
  const width = 30, cols = 42, rows = profilePts.length;
  const positions = [];
  const indices = [];
  for (let i = 0; i < cols; i++) {
    const x = -width / 2 + (width * i) / (cols - 1);
    const swell = Math.sin(x * 0.22) * 0.38 - Math.abs(x) * 0.012;
    for (let j = 0; j < rows; j++) {
      const p = profilePts[j];
      const lift = swell * (j / rows);
      positions.push(x, p.y + lift, p.z + Math.sin(x * 0.3 + j * 0.1) * 0.12);
    }
  }
  for (let i = 0; i < cols - 1; i++) {
    for (let j = 0; j < rows - 1; j++) {
      const a = i * rows + j, b = a + rows;
      indices.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  const wave = new THREE.Mesh(geo, waveMat);
  wave.receiveShadow = true;
  group.add(wave);

  // foam clustered along the throwing lip (last stretch of the profile)
  const lipPts = profilePts.slice(-16);
  const foam = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 10, 8), foamMat, 130);
  const dummy = new THREE.Object3D();
  const foamSeeds = [];
  for (let i = 0; i < 130; i++) {
    foamSeeds.push({
      x: -14 + Math.random() * 28,
      pt: lipPts[Math.floor(Math.random() * lipPts.length)],
      off: (Math.random() - 0.5) * 0.35,
      drop: Math.random() * 0.3,
      r: 0.07 + Math.random() * 0.14,
      ph: Math.random() * 6.28,
    });
  }
  group.add(foam);

  // thin foam streaks where the face meets the trough
  const baseFoam = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 10, 8), foamMat, 90);
  for (let i = 0; i < 90; i++) {
    dummy.position.set(-14 + Math.random() * 28, 0.0 + Math.random() * 0.05, 1.7 + Math.random() * 0.8);
    dummy.scale.set(0.6 + Math.random() * 0.9, 0.05 + Math.random() * 0.05, 0.22 + Math.random() * 0.3);
    dummy.rotation.set(0, Math.random() * 3, 0);
    dummy.updateMatrix();
    baseFoam.setMatrixAt(i, dummy.matrix);
  }
  group.add(baseFoam);

  function update(t) {
    group.position.y = Math.sin(t * 0.5) * 0.05;
    for (let i = 0; i < foamSeeds.length; i++) {
      const s = foamSeeds[i];
      const pulse = 1 + Math.sin(t * 2.2 + s.ph) * 0.18;
      dummy.position.set(s.x, s.pt.y - s.drop + Math.sin(t * 1.4 + s.ph) * 0.04, s.pt.z + s.off);
      dummy.scale.set(s.r * 1.9 * pulse, s.r * 0.75 * pulse, s.r * pulse);
      dummy.rotation.set(0, s.ph, 0);
      dummy.updateMatrix();
      foam.setMatrixAt(i, dummy.matrix);
    }
    foam.instanceMatrix.needsUpdate = true;
  }
  group.position.set(0, 0, -2.4);
  return { group, update };
}

function createWater() {
  const geo = new THREE.PlaneGeometry(90, 44, 84, 40);
  geo.rotateX(-Math.PI / 2);
  const base = geo.attributes.position.array.slice();
  const mesh = new THREE.Mesh(geo, waterMat);
  mesh.position.set(0, -0.12, 10);
  mesh.receiveShadow = true;
  function update(t) {
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = base[i * 3], z = base[i * 3 + 2];
      p.setY(i,
        Math.sin(x * 0.32 + t * 1.15) * 0.09 +
        Math.sin(z * 0.45 - t * 0.85) * 0.07 +
        Math.sin((x + z) * 0.18 + t * 0.6) * 0.06);
    }
    p.needsUpdate = true;
    geo.computeVertexNormals();
  }
  return { mesh, update };
}

function createSky() {
  const geo = new THREE.SphereGeometry(70, 24, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      top: { value: new THREE.Color(0x3fa9d6) },
      mid: { value: new THREE.Color(0x9adbe8) },
      low: { value: new THREE.Color(0xffe3b3) },
    },
    vertexShader: `
      varying vec3 vPos;
      void main() {
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform vec3 top; uniform vec3 mid; uniform vec3 low;
      varying vec3 vPos;
      void main() {
        float h = clamp(normalize(vPos).y, -0.05, 1.0);
        vec3 c = h < 0.18 ? mix(low, mid, smoothstep(0.0, 0.18, h))
                          : mix(mid, top, smoothstep(0.18, 0.75, h));
        gl_FragColor = vec4(c, 1.0);
      }`,
  });
  return new THREE.Mesh(geo, mat);
}

function createCloud(x, y, z, s) {
  const cloud = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  const puffs = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < puffs; i++) {
    const p = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), mat);
    p.scale.set(1.1 + Math.random() * 0.9, 0.42 + Math.random() * 0.2, 0.7);
    p.position.set((i - puffs / 2) * 0.95, Math.random() * 0.25, (Math.random() - 0.5) * 0.5);
    cloud.add(p);
  }
  cloud.position.set(x, y, z);
  cloud.scale.setScalar(s);
  return cloud;
}

function createGull() {
  const gull = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x33505c, side: THREE.DoubleSide });
  const geo = new THREE.PlaneGeometry(0.85, 0.2);
  geo.translate(0.42, 0, 0);
  const wl = new THREE.Mesh(geo, mat);
  const wr = new THREE.Mesh(geo, mat);
  wr.rotation.y = Math.PI;
  gull.add(wl, wr);
  return { gull, wl, wr };
}

export function createOcean() {
  const group = new THREE.Group();
  group.add(createSky());

  const sun = new THREE.Mesh(new THREE.CircleGeometry(2.6, 32),
    new THREE.MeshBasicMaterial({ color: 0xffd98a, fog: false }));
  sun.position.set(-13, 8.5, -34);
  group.add(sun);
  const sunHalo = new THREE.Mesh(new THREE.CircleGeometry(4.4, 32),
    new THREE.MeshBasicMaterial({ color: 0xffedb8, transparent: true, opacity: 0.35, fog: false }));
  sunHalo.position.copy(sun.position).z -= 0.1;
  group.add(sunHalo);

  const water = createWater();
  group.add(water.mesh);
  const wave = createWave();
  group.add(wave.group);

  const clouds = [
    createCloud(-14, 10.5, -26, 1.5), createCloud(6, 12, -30, 1.9),
    createCloud(16, 9, -24, 1.1), createCloud(-4, 13.5, -32, 1.3),
    createCloud(-22, 8, -22, 1.0),
  ];
  clouds.forEach((c) => group.add(c));

  const gulls = [];
  for (let i = 0; i < 3; i++) {
    const g = createGull();
    g.gull.position.set(-18 + i * 9, 6.5 + i * 0.9, -15 - i * 2);
    g.speed = 0.55 + i * 0.12;
    g.phase = i * 2.1;
    gulls.push(g);
    group.add(g.gull);
  }

  function update(t, dt) {
    water.update(t);
    wave.update(t);
    for (const c of clouds) {
      c.position.x += dt * 0.12;
      if (c.position.x > 30) c.position.x = -30;
    }
    for (const g of gulls) {
      g.gull.position.x += dt * g.speed;
      g.gull.position.y += Math.sin(t * 0.9 + g.phase) * dt * 0.25;
      if (g.gull.position.x > 26) g.gull.position.x = -26;
      const flap = Math.sin(t * 6 + g.phase) * 0.55;
      g.wl.rotation.z = flap;
      g.wr.rotation.z = -flap;
    }
  }
  return { group, update };
}
