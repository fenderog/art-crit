import * as THREE from 'three';

// Procedural sky, clouds and distant birds. Everything is drawn on canvases at
// runtime so the page needs no external assets.

function makeSkyTexture() {
  const w = 2048;
  const h = 1024;
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  const ctx = c.getContext('2d');

  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0.0, '#0a2450');
  g.addColorStop(0.3, '#2b6cae');
  g.addColorStop(0.48, '#7fbde5');
  g.addColorStop(0.56, '#d7eefb');
  g.addColorStop(0.62, '#cfe8f2');
  g.addColorStop(1.0, '#8fc0d0');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);

  // Sun glow.
  const sunX = w * 0.68;
  const sunY = h * 0.5;
  const sg = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, 320);
  sg.addColorStop(0.0, 'rgba(255,255,245,0.95)');
  sg.addColorStop(0.12, 'rgba(255,244,214,0.75)');
  sg.addColorStop(0.45, 'rgba(255,232,190,0.18)');
  sg.addColorStop(1.0, 'rgba(255,232,190,0)');
  ctx.fillStyle = sg;
  ctx.fillRect(0, 0, w, h);

  // Clouds -- layered soft ellipses in a band above the horizon.
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 46; i++) {
    const cx = Math.random() * w;
    const cy = h * (0.22 + Math.random() * 0.26);
    const scale = 0.5 + Math.random();
    const puffs = 6 + ((Math.random() * 6) | 0);
    for (let p = 0; p < puffs; p++) {
      const rx = (60 + Math.random() * 120) * scale;
      const ry = rx * (0.35 + Math.random() * 0.25);
      const ox = (Math.random() - 0.5) * 320 * scale;
      const oy = (Math.random() - 0.5) * 60 * scale;
      const a = 0.02 + Math.random() * 0.05;
      const cg = ctx.createRadialGradient(cx + ox, cy + oy, 0, cx + ox, cy + oy, rx);
      cg.addColorStop(0, `rgba(255,255,255,${a})`);
      cg.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = cg;
      ctx.save();
      ctx.translate(cx + ox, cy + oy);
      ctx.scale(1, ry / rx);
      ctx.beginPath();
      ctx.arc(0, 0, rx, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }
  ctx.globalCompositeOperation = 'source-over';

  const tex = new THREE.CanvasTexture(c);
  tex.mapping = THREE.EquirectangularReflectionMapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function makeCloudTexture() {
  const s = 128;
  const c = document.createElement('canvas');
  c.width = c.height = s;
  const ctx = c.getContext('2d');
  for (let i = 0; i < 14; i++) {
    const x = s / 2 + (Math.random() - 0.5) * 60;
    const y = s / 2 + (Math.random() - 0.5) * 34;
    const r = 16 + Math.random() * 24;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, 'rgba(255,255,255,0.5)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createEnvironment(scene, renderer) {
  const skyTex = makeSkyTexture();
  scene.background = skyTex;

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromEquirectangular(skyTex).texture;
  pmrem.dispose();

  const sunDir = new THREE.Vector3(0.5, 0.45, -0.72).normalize();

  const sun = new THREE.DirectionalLight(0xfff3dd, 2.2);
  sun.position.copy(sunDir).multiplyScalar(60);
  scene.add(sun);

  // Cool rim light from the opposite side to give the bird some form.
  const rim = new THREE.DirectionalLight(0xa9d4ff, 0.6);
  rim.position.set(-0.6, 0.35, 0.55).multiplyScalar(40);
  scene.add(rim);

  const fill = new THREE.HemisphereLight(0xbfe3ff, 0x1a4a55, 0.85);
  scene.add(fill);

  // Billboard clouds for depth.
  const cloudTex = makeCloudTexture();
  const clouds = [];
  const cloudMat = new THREE.SpriteMaterial({
    map: cloudTex,
    transparent: true,
    depthWrite: false,
    opacity: 0.85,
  });
  for (let i = 0; i < 14; i++) {
    const sprite = new THREE.Sprite(cloudMat.clone());
    const s = 14 + Math.random() * 26;
    sprite.scale.set(s * 1.8, s, 1);
    sprite.position.set(
      (Math.random() - 0.5) * 320,
      32 + Math.random() * 46,
      (Math.random() - 0.5) * 320 - 60,
    );
    sprite.material.opacity = 0.4 + Math.random() * 0.4;
    clouds.push({ sprite, speed: 0.6 + Math.random() * 1.1 });
    scene.add(sprite);
  }

  return {
    sunDir,
    update(dt) {
      for (const c of clouds) {
        c.sprite.position.x -= c.speed * dt;
        if (c.sprite.position.x < -190) c.sprite.position.x = 190;
      }
    },
  };
}

// A few distant gulls for scale and life.
export function createBirds(scene, count = 7) {
  const birds = [];
  const mat = new THREE.MeshStandardMaterial({
    color: 0xf3f5f7,
    roughness: 0.9,
    side: THREE.DoubleSide,
  });

  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, 0);
  wingShape.lineTo(1.0, 0.16);
  wingShape.lineTo(1.0, -0.16);
  wingShape.closePath();
  const wingGeo = new THREE.ShapeGeometry(wingShape);

  for (let i = 0; i < count; i++) {
    const bird = new THREE.Group();
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8), mat);
    body.scale.set(1.9, 0.8, 0.8);
    bird.add(body);

    const wingL = new THREE.Mesh(wingGeo, mat);
    wingL.rotation.y = Math.PI / 2;
    bird.add(wingL);
    const wingR = new THREE.Mesh(wingGeo, mat);
    wingR.rotation.y = -Math.PI / 2;
    bird.add(wingR);

    const radius = 70 + Math.random() * 90;
    const phase = Math.random() * Math.PI * 2;
    bird.position.set(
      Math.cos(phase) * radius,
      24 + Math.random() * 24,
      Math.sin(phase) * radius,
    );
    const s = 0.8 + Math.random() * 0.7;
    bird.scale.setScalar(s);
    scene.add(bird);

    birds.push({
      bird,
      wingL,
      wingR,
      phase,
      radius,
      speed: (0.05 + Math.random() * 0.05) * (Math.random() < 0.5 ? -1 : 1),
      flap: 3 + Math.random() * 2,
      flapPhase: Math.random() * Math.PI * 2,
    });
  }

  return {
    update(t) {
      for (const b of birds) {
        b.phase += b.speed * 0.01;
        b.bird.position.x = Math.cos(b.phase) * b.radius;
        b.bird.position.z = Math.sin(b.phase) * b.radius;
        b.bird.rotation.y = -b.phase + Math.PI / 2;
        const f = Math.sin(t * b.flap + b.flapPhase) * 0.55;
        b.wingL.rotation.z = f;
        b.wingR.rotation.z = -f;
      }
    },
  };
}
