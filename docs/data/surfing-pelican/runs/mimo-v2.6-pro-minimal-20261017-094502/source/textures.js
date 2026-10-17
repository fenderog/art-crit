// Every texture used by the scene is generated in code (no external assets).
import * as THREE from 'three';

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function smoothstep(t) {
  return t * t * (3 - 2 * t);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function canvasTexture(canvas, { srgb = false } = {}) {
  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  tex.needsUpdate = true;
  return tex;
}

/** Seamless tiling value-noise texture (RGBA, all channels identical). */
export function makeNoiseTexture(size = 256, seed = 20240517) {
  const rnd = mulberry32(seed);
  const field = new Float32Array(size * size);
  let amp = 1;
  let total = 0;
  for (let octave = 0; octave < 5; octave++) {
    const cells = 4 << octave;
    const grid = new Float32Array(cells * cells);
    for (let i = 0; i < grid.length; i++) grid[i] = rnd();
    for (let y = 0; y < size; y++) {
      const fy = (y / size) * cells;
      const y0 = Math.floor(fy);
      const ty = smoothstep(fy - y0);
      const y1 = (y0 + 1) % cells;
      for (let x = 0; x < size; x++) {
        const fx = (x / size) * cells;
        const x0 = Math.floor(fx);
        const tx = smoothstep(fx - x0);
        const x1 = (x0 + 1) % cells;
        const v = lerp(
          lerp(grid[y0 * cells + x0], grid[y0 * cells + x1], tx),
          lerp(grid[y1 * cells + x0], grid[y1 * cells + x1], tx),
          ty,
        );
        field[y * size + x] += v * amp;
      }
    }
    total += amp;
    amp *= 0.52;
  }

  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  for (let i = 0; i < size * size; i++) {
    const v = Math.round(Math.min(1, Math.max(0, field[i] / total)) * 255);
    img.data[i * 4] = v;
    img.data[i * 4 + 1] = v;
    img.data[i * 4 + 2] = v;
    img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return canvasTexture(canvas);
}

/** Soft round puff used for spray droplets (alpha only). */
export function makeDropTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const g = ctx.createRadialGradient(
    size / 2,
    size / 2,
    0,
    size / 2,
    size / 2,
    size / 2,
  );
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.72)');
  g.addColorStop(0.72, 'rgba(255,255,255,0.18)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.NoColorSpace;
  return tex;
}

/** Big radial glow used for the sun halo. */
export function makeGlowTexture(size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const g = ctx.createRadialGradient(
    size / 2,
    size / 2,
    0,
    size / 2,
    size / 2,
    size / 2,
  );
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.12, 'rgba(255,246,214,0.85)');
  g.addColorStop(0.32, 'rgba(255,226,170,0.32)');
  g.addColorStop(0.62, 'rgba(255,214,150,0.09)');
  g.addColorStop(1, 'rgba(255,210,150,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/** Puffy cumulus cloud sprite with soft edges. */
export function makeCloudTexture(seed = 7) {
  const rnd = mulberry32(seed);
  const w = 512;
  const h = 256;
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');

  const blobs = 22;
  for (let i = 0; i < blobs; i++) {
    const cx = w * (0.16 + 0.68 * rnd());
    const cy = h * (0.52 + 0.26 * (rnd() - 0.5) * 2);
    const r = h * (0.12 + 0.3 * rnd()) * (1 - Math.abs(cx / w - 0.5) * 0.8);
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    const a = 0.32 + 0.3 * rnd();
    g.addColorStop(0, `rgba(255,255,255,${a})`);
    g.addColorStop(0.55, `rgba(255,255,255,${a * 0.55})`);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  }

  // flat-ish base, like a cumulus cloud
  ctx.globalCompositeOperation = 'destination-out';
  const base = ctx.createLinearGradient(0, h * 0.62, 0, h);
  base.addColorStop(0, 'rgba(0,0,0,0)');
  base.addColorStop(1, 'rgba(0,0,0,0.85)');
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, w, h);

  // fade the sprite edges so it blends into the sky
  const side = ctx.createLinearGradient(0, 0, w, 0);
  side.addColorStop(0, 'rgba(0,0,0,1)');
  side.addColorStop(0.16, 'rgba(0,0,0,0)');
  side.addColorStop(0.84, 'rgba(0,0,0,0)');
  side.addColorStop(1, 'rgba(0,0,0,1)');
  ctx.fillStyle = side;
  ctx.fillRect(0, 0, w, h);
  ctx.globalCompositeOperation = 'source-over';

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}