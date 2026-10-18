import * as THREE from 'three';

function makeCanvas(width, height, draw) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  draw(ctx, width, height);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

/** Soft radial glow, used for the sun and its halo. */
export function makeGlowTexture() {
  return makeCanvas(256, 256, (ctx, w, h) => {
    const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
    g.addColorStop(0.0, 'rgba(255,255,255,1)');
    g.addColorStop(0.12, 'rgba(255,248,220,0.92)');
    g.addColorStop(0.3, 'rgba(255,214,150,0.34)');
    g.addColorStop(0.58, 'rgba(255,170,110,0.09)');
    g.addColorStop(1.0, 'rgba(255,150,90,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  });
}

/** A single soft, irregular cloud puff. */
export function makeCloudTexture(seed = 1) {
  return makeCanvas(512, 256, (ctx, w, h) => {
    let s = seed * 9301 + 49297;
    const rand = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };

    // Soft base mass.
    ctx.filter = 'blur(9px)';
    const base = ctx.createRadialGradient(w / 2, h * 0.66, 0, w / 2, h * 0.66, w * 0.4);
    base.addColorStop(0, 'rgba(255,250,248,0.42)');
    base.addColorStop(0.6, 'rgba(255,245,242,0.22)');
    base.addColorStop(1, 'rgba(255,240,238,0)');
    ctx.fillStyle = base;
    ctx.beginPath();
    ctx.ellipse(w / 2, h * 0.66, w * 0.4, h * 0.16, 0, 0, Math.PI * 2);
    ctx.fill();

    // Rounded cumulus lobes with a little more definition.
    ctx.filter = 'blur(3px)';
    for (let i = 0; i < 14; i++) {
      const px = w * (0.16 + rand() * 0.68);
      const py = h * (0.42 + rand() * 0.26);
      const r = h * (0.1 + rand() * 0.17);
      const g = ctx.createRadialGradient(px, py - r * 0.2, 0, px, py, r);
      const alpha = 0.4 + rand() * 0.25;
      g.addColorStop(0, `rgba(255,255,255,${alpha})`);
      g.addColorStop(0.6, `rgba(255,248,244,${alpha * 0.72})`);
      g.addColorStop(1, 'rgba(255,244,240,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.ellipse(px, py, r * (1.05 + rand() * 0.6), r * 0.78, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    // A few bright upper highlights.
    ctx.filter = 'blur(2px)';
    for (let i = 0; i < 8; i++) {
      const px = w * (0.2 + rand() * 0.6);
      const py = h * (0.36 + rand() * 0.16);
      const r = h * (0.05 + rand() * 0.09);
      const g = ctx.createRadialGradient(px, py, 0, px, py, r);
      g.addColorStop(0, 'rgba(255,255,255,0.5)');
      g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

/** Soft round droplet for the spray particle system. */
export function makeSprayTexture() {
  return makeCanvas(64, 64, (ctx, w, h) => {
    const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.35, 'rgba(246,253,255,0.9)');
    g.addColorStop(0.7, 'rgba(214,244,250,0.32)');
    g.addColorStop(1, 'rgba(200,240,250,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  });
}

/** Ragged ellipse of foam that sits around the board. */
export function makeFoamRingTexture() {
  return makeCanvas(256, 512, (ctx, w, h) => {
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(0.55, 1);
    ctx.filter = 'blur(7px)';

    for (let i = 0; i < 140; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = 108 + Math.random() * 26;
      const x = Math.cos(a) * r;
      const y = Math.sin(a) * r;
      const rad = 3 + Math.random() * 12;
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
      g.addColorStop(0, `rgba(255,255,255,${0.22 + Math.random() * 0.5})`);
      g.addColorStop(1, 'rgba(240,255,255,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fill();
    }

    // Broken, streaky ring highlights.
    for (let i = 0; i < 24; i++) {
      const a0 = Math.random() * Math.PI * 2;
      const a1 = a0 + 0.05 + Math.random() * 0.22;
      ctx.strokeStyle = `rgba(255,255,255,${0.1 + Math.random() * 0.28})`;
      ctx.lineWidth = 2 + Math.random() * 9;
      ctx.beginPath();
      ctx.arc(0, 0, 112 + Math.random() * 18, a0, a1);
      ctx.stroke();
    }
    ctx.restore();

    // A little foam dragged off the tail.
    ctx.filter = 'blur(5px)';
    for (let i = 0; i < 30; i++) {
      const x = w / 2 + (Math.random() - 0.5) * 70;
      const y = h - 50 - Math.random() * 90;
      const rad = 3 + Math.random() * 10;
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
      g.addColorStop(0, `rgba(255,255,255,${0.1 + Math.random() * 0.3})`);
      g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}
