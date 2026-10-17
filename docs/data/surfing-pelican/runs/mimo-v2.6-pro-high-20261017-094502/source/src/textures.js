/**
 * Procedural textures generated on a canvas at runtime (no external assets).
 */
import * as THREE from "three";

/** Soft round sprite with a radial alpha falloff. */
export function softCircleTexture(size = 128, inner = 0.0) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  const g = ctx.createRadialGradient(
    size / 2,
    size / 2,
    size * 0.5 * inner,
    size / 2,
    size / 2,
    size * 0.5
  );
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(0.45, "rgba(255,255,255,0.55)");
  g.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
}

/** Irregular foam patch made of overlapping soft blobs. */
export function foamTexture(size = 256, blobs = 90) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  for (let i = 0; i < blobs; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const r = size * (0.02 + Math.random() * 0.11);
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    const a = 0.12 + Math.random() * 0.45;
    g.addColorStop(0, `rgba(255,255,255,${a})`);
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  return texture;
}