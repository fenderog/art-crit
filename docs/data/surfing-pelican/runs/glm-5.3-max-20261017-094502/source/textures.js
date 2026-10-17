import * as THREE from 'three';

// All "assets" in this scene are generated in code (the packaged page must run
// offline with no network requests), so textures are drawn to canvases here.

export function makeGlowTexture(stops, size = 128) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  for (const [offset, color] of stops) grad.addColorStop(offset, color);
  g.fillStyle = grad;
  g.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function makeCloudTexture(size = 256) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const g = c.getContext('2d');
  for (let i = 0; i < 16; i++) {
    const x = size * (0.2 + 0.6 * Math.random());
    const y = size * (0.3 + 0.4 * Math.random());
    const r = size * (0.07 + 0.15 * Math.random());
    const grad = g.createRadialGradient(x, y, 0, x, y, r);
    grad.addColorStop(0, 'rgba(255,250,244,0.55)');
    grad.addColorStop(0.6, 'rgba(255,244,236,0.22)');
    grad.addColorStop(1, 'rgba(255,240,230,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, size, size);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
