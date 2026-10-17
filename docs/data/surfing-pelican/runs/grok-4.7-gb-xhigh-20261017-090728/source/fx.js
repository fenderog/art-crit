import * as THREE from "three";
import { sampleWater } from "./sim.js";

function discTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const g = canvas.getContext("2d");
  const grd = g.createRadialGradient(64, 64, 4, 64, 64, 64);
  grd.addColorStop(0, "rgba(255,255,255,1)");
  grd.addColorStop(0.35, "rgba(255,255,255,0.55)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function shadowTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const g = canvas.getContext("2d");
  const grd = g.createRadialGradient(64, 64, 8, 64, 64, 64);
  grd.addColorStop(0, "rgba(0,0,0,0.55)");
  grd.addColorStop(0.45, "rgba(0,0,0,0.22)");
  grd.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const SPRAY_N = 220;
const TRAIL_MAX = 72;

const sprayVertex = /* glsl */ `
attribute float aAlpha;
attribute float aSize;
varying float vAlpha;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vAlpha = aAlpha;
  gl_PointSize = aSize * aAlpha * (320.0 / max(1.0, -mv.z));
  gl_Position = projectionMatrix * mv;
}
`;

const sprayFragment = /* glsl */ `
uniform sampler2D uMap;
varying float vAlpha;
void main() {
  vec4 tex = texture2D(uMap, gl_PointCoord);
  if (tex.a * vAlpha < 0.02) discard;
  gl_FragColor = vec4(vec3(1.0, 0.98, 0.95), tex.a * vAlpha);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

const wakeVertex = /* glsl */ `
attribute vec4 aColor;
varying vec4 vColor;
void main() {
  vColor = aColor;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const wakeFragment = /* glsl */ `
varying vec4 vColor;
void main() {
  gl_FragColor = vColor;
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
`;

export function createFx(scene) {
  const sprayGeo = new THREE.BufferGeometry();
  const sprayPos = new Float32Array(SPRAY_N * 3);
  const sprayAlpha = new Float32Array(SPRAY_N);
  const spraySize = new Float32Array(SPRAY_N);
  sprayGeo.setAttribute("position", new THREE.BufferAttribute(sprayPos, 3));
  sprayGeo.setAttribute("aAlpha", new THREE.BufferAttribute(sprayAlpha, 1));
  sprayGeo.setAttribute("aSize", new THREE.BufferAttribute(spraySize, 1));
  const spray = new THREE.Points(
    sprayGeo,
    new THREE.ShaderMaterial({
      uniforms: { uMap: { value: discTexture() } },
      vertexShader: sprayVertex,
      fragmentShader: sprayFragment,
      transparent: true,
      depthWrite: false,
      blending: THREE.NormalBlending,
    }),
  );
  spray.frustumCulled = false;
  spray.renderOrder = 3;

  const wakeGeo = new THREE.BufferGeometry();
  const wakePos = new Float32Array(TRAIL_MAX * 2 * 3);
  const wakeCol = new Float32Array(TRAIL_MAX * 2 * 4);
  const wakeIndex = [];
  for (let i = 0; i < TRAIL_MAX - 1; i++) {
    const a = i * 2;
    const b = a + 1;
    const c = a + 2;
    const d = a + 3;
    wakeIndex.push(a, c, b, c, d, b);
  }
  wakeGeo.setAttribute("position", new THREE.BufferAttribute(wakePos, 3));
  wakeGeo.setAttribute("aColor", new THREE.BufferAttribute(wakeCol, 4));
  wakeGeo.setIndex(wakeIndex);
  wakeGeo.setDrawRange(0, 0);
  const wake = new THREE.Mesh(
    wakeGeo,
    new THREE.ShaderMaterial({
      vertexShader: wakeVertex,
      fragmentShader: wakeFragment,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    }),
  );
  wake.frustumCulled = false;
  wake.renderOrder = 2;

  const blobGeo = new THREE.CircleGeometry(1, 32);
  blobGeo.rotateX(-Math.PI / 2);
  const blob = new THREE.Mesh(
    blobGeo,
    new THREE.MeshBasicMaterial({
      map: shadowTexture(),
      transparent: true,
      depthWrite: false,
      color: 0x062830,
    }),
  );
  blob.scale.set(1.55, 1, 1.55);
  blob.renderOrder = 1;
  blob.frustumCulled = false;

  scene.add(spray, wake, blob);

  const drops = Array.from({ length: SPRAY_N }, (_, i) => ({
    x: 0,
    y: 0,
    z: 0,
    vx: 0,
    vy: 0,
    vz: 0,
    life: 0,
    max: 1,
    size: 8,
    mist: i % 5 === 0,
  }));
  const trail = [];
  let trailTimer = 0;
  const spawnLocal = new THREE.Vector3();
  const down = new THREE.Vector3();
  const side = new THREE.Vector3();
  const up = new THREE.Vector3(0, 1, 0);
  const align = new THREE.Quaternion();

  function spawn(drop, pose) {
    down.set(pose.normal.x, 0, pose.normal.z);
    if (down.lengthSq() > 1e-6) down.normalize();
    else down.set(0, 0, 1);
    const rail = pose.right.dot(down) >= 0 ? 1 : -1;
    const along = Math.random();
    spawnLocal.set(rail * (0.16 + Math.random() * 0.1), 0.08, 0.15 + along * 0.85);
    spawnLocal.applyQuaternion(pose.quaternion).add(pose.position);
    drop.x = spawnLocal.x;
    drop.y = spawnLocal.y;
    drop.z = spawnLocal.z;
    const kick = drop.mist ? 0.8 + Math.random() * 0.6 : 1.6 + Math.random() * 2.4;
    const lift = drop.mist ? 0.7 + Math.random() * 0.8 : 1.5 + Math.random() * 2.6;
    drop.vx = -pose.forward.x * kick + down.x * (0.6 + Math.random()) + (Math.random() - 0.5) * 0.8;
    drop.vy = lift;
    drop.vz = -pose.forward.z * kick + down.z * (0.6 + Math.random()) + (Math.random() - 0.5) * 0.8;
    drop.max = drop.mist ? 0.9 + Math.random() * 0.5 : 0.4 + Math.random() * 0.45;
    drop.life = drop.max;
    drop.size = drop.mist ? 14 + Math.random() * 10 : 5 + Math.random() * 8;
  }

  return {
    update(time, dt, pose, origin) {
      let born = 0;
      const quota = 5;
      for (let i = 0; i < drops.length; i++) {
        const d = drops[i];
        if (d.life <= 0) {
          if (born < quota) {
            spawn(d, pose);
            born++;
          }
          continue;
        }
        d.vy -= (d.mist ? 2.4 : 8.2) * dt;
        d.x += d.vx * dt;
        d.y += d.vy * dt;
        d.z += d.vz * dt;
        d.life -= dt;
        const water = sampleWater(d.x, d.z, time);
        if (d.y < water.h) d.life = 0;
      }

      for (let i = 0; i < drops.length; i++) {
        const d = drops[i];
        sprayPos[i * 3] = d.x - origin.x;
        sprayPos[i * 3 + 1] = d.y;
        sprayPos[i * 3 + 2] = d.z - origin.z;
        const fade = d.life > 0 ? Math.min(1, d.life / 0.22) * Math.min(1, d.life / d.max * 1.15) : 0;
        sprayAlpha[i] = fade * (d.mist ? 0.45 : 0.85);
        spraySize[i] = d.size;
      }
      sprayGeo.attributes.position.needsUpdate = true;
      sprayGeo.attributes.aAlpha.needsUpdate = true;
      sprayGeo.attributes.aSize.needsUpdate = true;

      trailTimer += dt;
      if (trailTimer > 0.045) {
        trailTimer = 0;
        side.copy(pose.right);
        side.y = 0;
        if (side.lengthSq() < 1e-6) side.set(1, 0, 0);
        side.normalize();
        spawnLocal.set(0, 0.05, 0.85);
        spawnLocal.applyQuaternion(pose.quaternion).add(pose.position);
        trail.push({ x: spawnLocal.x, z: spawnLocal.z, sx: side.x, sz: side.z, born: time });
        if (trail.length > TRAIL_MAX) trail.shift();
      }

      const n = trail.length;
      const life = 2.6;
      for (let i = 0; i < n; i++) {
        const p = trail[i];
        const age = THREE.MathUtils.clamp((time - p.born) / life, 0, 1);
        const fade = (1 - age) * (1 - age);
        const width = 0.12 + 0.62 * fade;
        const water = sampleWater(p.x, p.z, time);
        const y = water.h + 0.045;
        const liftX = water.normal.x * 0.04;
        const liftZ = water.normal.z * 0.04;
        const o = i * 2;
        wakePos[(o) * 3] = p.x + p.sx * width - origin.x + liftX;
        wakePos[(o) * 3 + 1] = y;
        wakePos[(o) * 3 + 2] = p.z + p.sz * width - origin.z + liftZ;
        wakePos[(o + 1) * 3] = p.x - p.sx * width - origin.x + liftX;
        wakePos[(o + 1) * 3 + 1] = y;
        wakePos[(o + 1) * 3 + 2] = p.z - p.sz * width - origin.z + liftZ;
        const alpha = 0.5 * fade;
        for (let k = 0; k < 2; k++) {
          const c = (o + k) * 4;
          wakeCol[c] = 0.95;
          wakeCol[c + 1] = 0.93;
          wakeCol[c + 2] = 0.88;
          wakeCol[c + 3] = alpha;
        }
      }
      wakeGeo.attributes.position.needsUpdate = true;
      wakeGeo.attributes.aColor.needsUpdate = true;
      wakeGeo.setDrawRange(0, Math.max(0, n - 1) * 6);

      align.setFromUnitVectors(up, pose.normal);
      blob.position.set(0, pose.position.y + 0.03, 0);
      blob.quaternion.copy(align);
    },
  };
}
