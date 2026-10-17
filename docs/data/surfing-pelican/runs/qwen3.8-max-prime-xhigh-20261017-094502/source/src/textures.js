import * as THREE from "three";

/** All textures in this project are generated in code (no external assets). */

function canvas(size) {
  const c = document.createElement("canvas");
  c.width = size.w || size;
  c.height = size.h || size;
  return c;
}

function finish(c, { repeat = 1, srgb = false, aniso = 4 } = {}) {
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeat, repeat);
  tex.anisotropy = aniso;
  if (srgb) tex.colorSpace = THREE.SRGBColorSpace;
  tex.needsUpdate = true;
  return tex;
}

/** Soft round puff — spray droplets, mist, wake foam. */
export function softDotTexture() {
  const c = canvas(128);
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0.0, "rgba(255,255,255,1)");
  grd.addColorStop(0.25, "rgba(255,255,255,0.82)");
  grd.addColorStop(0.55, "rgba(255,255,255,0.28)");
  grd.addColorStop(1.0, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  return finish(c);
}

/** Contact shadow blob under the board. */
export function blobShadowTexture() {
  const c = canvas({ w: 256, h: 256 });
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grd.addColorStop(0.0, "rgba(0,0,0,0.85)");
  grd.addColorStop(0.45, "rgba(0,0,0,0.45)");
  grd.addColorStop(0.8, "rgba(0,0,0,0.10)");
  grd.addColorStop(1.0, "rgba(0,0,0,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 256, 256);
  return finish(c);
}

/** Overlapping feather scallops — used as a bump map so plumage catches light. */
export function featherBumpTexture() {
  const c = canvas({ w: 256, h: 256 });
  const g = c.getContext("2d");
  g.fillStyle = "#7d7d7d";
  g.fillRect(0, 0, 256, 256);

  const rows = 16;
  const cols = 8;
  for (let r = 0; r < rows; r++) {
    const y = (r / rows) * 256;
    const off = (r % 2) * (256 / cols) * 0.5;
    for (let i = -1; i <= cols; i++) {
      const x = off + (i / cols) * 256 + (256 / cols) * 0.5;
      const w = 256 / cols;
      const grd = g.createLinearGradient(x - w * 0.5, y, x + w * 0.5, y + 256 / rows);
      grd.addColorStop(0.0, "rgba(232,232,232,1)");
      grd.addColorStop(0.55, "rgba(150,150,150,1)");
      grd.addColorStop(1.0, "rgba(58,58,58,1)");
      g.fillStyle = grd;
      g.beginPath();
      g.ellipse(x, y + 256 / rows * 0.55, w * 0.52, (256 / rows) * 0.62, 0, Math.PI, 0);
      g.closePath();
      g.fill();
      g.strokeStyle = "rgba(30,30,30,0.55)";
      g.lineWidth = 1.4;
      g.stroke();
    }
  }
  // fine barb streaks
  g.globalAlpha = 0.14;
  g.strokeStyle = "#ffffff";
  g.lineWidth = 1;
  for (let i = 0; i < 420; i++) {
    const x = Math.random() * 256;
    const y = Math.random() * 256;
    g.beginPath();
    g.moveTo(x, y);
    g.lineTo(x + (Math.random() - 0.5) * 5, y + 3 + Math.random() * 5);
    g.stroke();
  }
  g.globalAlpha = 1;
  return finish(c, { repeat: 3 });
}

/** Fine speckle for resin / deck texture (roughness map). */
export function speckleTexture(base = "#8a8a8a", dots = "#3a3a3a") {
  const c = canvas({ w: 128, h: 128 });
  const g = c.getContext("2d");
  g.fillStyle = base;
  g.fillRect(0, 0, 128, 128);
  g.fillStyle = dots;
  for (let i = 0; i < 900; i++) {
    g.globalAlpha = 0.05 + Math.random() * 0.2;
    const s = Math.random() * 1.8 + 0.4;
    g.fillRect(Math.random() * 128, Math.random() * 128, s, s);
  }
  g.globalAlpha = 1;
  return finish(c, { repeat: 4 });
}
