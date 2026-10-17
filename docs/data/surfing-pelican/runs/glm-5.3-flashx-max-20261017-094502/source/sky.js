import * as THREE from "three";

const rnd = (a) => (Math.random() * 2 - 1) * a;

/** Gradient sky dome, sun with glow, drifting clouds, and a little palm island. */
export function createSky() {
  const group = new THREE.Group();

  // gradient dome
  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(430, 32, 20),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        cTop: { value: new THREE.Color(0x1f5fbf) },
        cHorizon: { value: new THREE.Color(0xcfeef7) },
      },
      vertexShader: /* glsl */ `
        varying vec3 vDir;
        void main() {
          vDir = normalize(position);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform vec3 cTop;
        uniform vec3 cHorizon;
        varying vec3 vDir;
        void main() {
          float h = clamp(vDir.y, 0.0, 1.0);
          gl_FragColor = vec4(mix(cHorizon, cTop, pow(h, 0.62)), 1.0);
        }
      `,
    })
  );
  group.add(dome);

  // sun + glow (glow texture generated on a canvas, no external assets)
  const sunPos = new THREE.Vector3(-90, 70, -180);
  const sun = new THREE.Mesh(
    new THREE.CircleGeometry(16, 40),
    new THREE.MeshBasicMaterial({ color: 0xffe9a8, fog: false })
  );
  sun.position.copy(sunPos);
  sun.lookAt(0, 0, 0);
  group.add(sun);

  const cnv = document.createElement("canvas");
  cnv.width = cnv.height = 128;
  const ctx = cnv.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, 8, 64, 64, 64);
  g.addColorStop(0, "rgba(255,240,190,0.9)");
  g.addColorStop(0.4, "rgba(255,220,140,0.35)");
  g.addColorStop(1, "rgba(255,220,140,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  const glow = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cnv), transparent: true, depthWrite: false, fog: false })
  );
  glow.scale.setScalar(150);
  glow.position.copy(sunPos);
  group.add(glow);

  // clouds
  const clouds = [];
  const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.92 });
  for (let i = 0; i < 6; i++) {
    const c = new THREE.Group();
    const n = 3 + Math.floor(Math.random() * 3);
    for (let j = 0; j < n; j++) {
      const puff = new THREE.Mesh(new THREE.SphereGeometry(3 + Math.random() * 2.6, 10, 8), cloudMat);
      puff.position.set((j - n / 2) * 3.4 + rnd(1.5), rnd(1.2), rnd(2));
      puff.scale.y = 0.55;
      c.add(puff);
    }
    c.position.set(rnd(150), 34 + Math.random() * 26, -40 - Math.random() * 130);
    c.userData.speed = 0.6 + Math.random() * 0.9;
    clouds.push(c);
    group.add(c);
  }

  // palm island on the horizon
  const island = new THREE.Group();
  island.position.set(-45, 0.9, -85);

  const sand = new THREE.Mesh(
    new THREE.CylinderGeometry(9, 12, 3, 24),
    new THREE.MeshLambertMaterial({ color: 0xe9d8a6 })
  );
  island.add(sand);

  const mound = new THREE.Mesh(
    new THREE.SphereGeometry(9.5, 20, 14),
    new THREE.MeshLambertMaterial({ color: 0x2d6a4f })
  );
  mound.scale.y = 0.42;
  mound.position.y = 1.4;
  island.add(mound);

  const palm = new THREE.Group();
  palm.position.set(2, 2.2, 1);
  palm.rotation.z = 0.12;
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.22, 0.34, 5, 8),
    new THREE.MeshLambertMaterial({ color: 0x8a6642 })
  );
  trunk.position.y = 2.5;
  palm.add(trunk);

  const frondMat = new THREE.MeshLambertMaterial({ color: 0x40916c });
  for (let k = 0; k < 7; k++) {
    const frond = new THREE.Group();
    frond.rotation.y = (k / 7) * Math.PI * 2;
    frond.rotation.x = -0.45;
    const blade = new THREE.Mesh(new THREE.SphereGeometry(1, 8, 6), frondMat);
    blade.scale.set(0.45, 0.1, 1.7);
    blade.position.z = 1.4;
    frond.add(blade);
    frond.position.y = 5;
    palm.add(frond);
  }
  for (let k = 0; k < 3; k++) {
    const nut = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 8, 6),
      new THREE.MeshLambertMaterial({ color: 0x6b4f2e })
    );
    nut.position.set(Math.cos(k * 2.1) * 0.35, 4.8, Math.sin(k * 2.1) * 0.35);
    palm.add(nut);
  }
  island.add(palm);
  group.add(island);

  function update(t, dt) {
    for (const c of clouds) {
      c.position.x += c.userData.speed * dt;
      if (c.position.x > 170) c.position.x = -170;
    }
  }

  return { group, update };
}
