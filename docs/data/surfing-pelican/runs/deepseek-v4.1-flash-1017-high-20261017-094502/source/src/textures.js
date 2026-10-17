import * as THREE from 'three';

// Small deterministic RNG so the scene looks the same on every load.
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function canvas2d(w, h) {
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  return { canvas, ctx: canvas.getContext('2d') };
}

function finish(canvas, { srgb = false, repeat = false } = {}) {
  const tex = new THREE.CanvasTexture(canvas);
  if (srgb) tex.colorSpace = THREE.SRGBColorSpace;
  if (repeat) tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.anisotropy = 8;
  tex.needsUpdate = true;
  return tex;
}

export function makeBoardTexture() {
  const { canvas, ctx } = canvas2d(1024, 256);
  const rand = rng(7);

  // Warm resin base
  const base = ctx.createLinearGradient(0, 0, 0, 256);
  base.addColorStop(0, '#f9efdc');
  base.addColorStop(0.45, '#f4e5cd');
  base.addColorStop(1, '#eddbc0');
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, 1024, 256);

  // Faint lengthwise grain
  for (let i = 0; i < 90; i++) {
    const y = rand() * 256;
    ctx.strokeStyle = `rgba(160, 120, 80, ${0.015 + rand() * 0.025})`;
    ctx.lineWidth = 0.6 + rand() * 1.4;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.bezierCurveTo(300, y + rand() * 8 - 4, 700, y + rand() * 8 - 4, 1024, y);
    ctx.stroke();
  }

  // Central teal band + coral pinlines
  const band = ctx.createLinearGradient(0, 94, 0, 162);
  band.addColorStop(0, '#2c7d7a');
  band.addColorStop(0.5, '#236c6c');
  band.addColorStop(1, '#1b5b5d');
  ctx.fillStyle = band;
  ctx.fillRect(0, 100, 1024, 56);

  ctx.fillStyle = '#e46a4c';
  ctx.fillRect(0, 91, 1024, 6);
  ctx.fillRect(0, 159, 1024, 6);
  ctx.fillStyle = 'rgba(255, 248, 233, 0.9)';
  ctx.fillRect(0, 100, 1024, 2.5);
  ctx.fillRect(0, 153.5, 1024, 2.5);

  // Rail pinlines (visible toward the middle of the board)
  ctx.fillStyle = 'rgba(35, 108, 108, 0.85)';
  ctx.fillRect(0, 13, 1024, 3);
  ctx.fillRect(0, 240, 1024, 3);
  ctx.fillStyle = 'rgba(228, 106, 76, 0.65)';
  ctx.fillRect(0, 20, 1024, 1.6);
  ctx.fillRect(0, 234.4, 1024, 1.6);

  // Script wordmark
  ctx.save();
  ctx.fillStyle = '#f8eeda';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = 'italic 600 33px Georgia, "Times New Roman", serif';
  ctx.letterSpacing = '7px';
  ctx.fillText('pelican', 385, 130);
  ctx.font = '600 9px "Helvetica Neue", Arial, sans-serif';
  ctx.letterSpacing = '5px';
  ctx.fillStyle = 'rgba(248, 238, 218, 0.82)';
  ctx.fillText('SURF CO.', 385, 150);
  ctx.restore();

  // Tail badge: coral sun over a little cream wave
  ctx.save();
  ctx.translate(128, 128);
  ctx.fillStyle = '#e46a4c';
  ctx.beginPath();
  ctx.arc(0, 0, 35, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#f8eeda';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(0, 0, 26, 0, Math.PI * 2);
  ctx.stroke();
  ctx.strokeStyle = '#f8eeda';
  ctx.lineWidth = 5;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(-15, 6);
  ctx.quadraticCurveTo(-4, -4, 2, 5);
  ctx.quadraticCurveTo(9, 14, 16, 3);
  ctx.stroke();
  ctx.restore();

  // Nose: a retro setting sun
  ctx.save();
  ctx.translate(866, 128);
  ctx.fillStyle = '#e46a4c';
  ctx.beginPath();
  ctx.arc(0, 0, 31, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#f8eeda';
  ctx.beginPath();
  ctx.arc(0, 0, 23, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#e46a4c';
  ctx.beginPath();
  ctx.arc(0, 0, 15, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#f8eeda';
  ctx.fillRect(-46, 29, 92, 3);
  ctx.fillRect(-34, 38, 68, 2);
  ctx.restore();

  // Gentle speckle
  for (let i = 0; i < 900; i++) {
    const a = rand() * 0.05;
    ctx.fillStyle = rand() > 0.5 ? `rgba(255,255,255,${a})` : `rgba(90,60,40,${a})`;
    ctx.fillRect(rand() * 1024, rand() * 256, 1.2, 1.2);
  }

  const tex = finish(canvas, { srgb: true });
  // ExtrudeGeometry's cap UVs are raw shape coordinates. Map the board
  // (x in [-2.5, 2.5], y in [-0.7, 0.7]) onto the full texture.
  tex.repeat.set(1 / 5.0, 1 / 1.4);
  tex.offset.set(0.5, 0.5);
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  return tex;
}

function drawPuff(ctx, x, y, r, alpha, tint = '255,255,255') {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${tint},${alpha})`);
  g.addColorStop(0.45, `rgba(${tint},${alpha * 0.72})`);
  g.addColorStop(0.78, `rgba(${tint},${alpha * 0.22})`);
  g.addColorStop(1, `rgba(${tint},0)`);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
}

export function makeFoamPuff() {
  const { canvas, ctx } = canvas2d(128, 128);
  const rand = rng(31);
  drawPuff(ctx, 64, 64, 58, 0.85);
  for (let i = 0; i < 26; i++) {
    const a = rand() * Math.PI * 2;
    const d = rand() * 28;
    drawPuff(
      ctx,
      64 + Math.cos(a) * d,
      64 + Math.sin(a) * d,
      10 + rand() * 26,
      0.25 + rand() * 0.4,
    );
  }
  // A few soft holes make it feel like aerated water
  ctx.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < 9; i++) {
    const a = rand() * Math.PI * 2;
    const d = rand() * 30;
    drawPuff(ctx, 64 + Math.cos(a) * d, 64 + Math.sin(a) * d, 5 + rand() * 10, 0.35);
  }
  ctx.globalCompositeOperation = 'source-over';
  return finish(canvas);
}

export function makeFoamTile() {
  const size = 256;
  const { canvas, ctx } = canvas2d(size, size);
  const rand = rng(89);
  ctx.clearRect(0, 0, size, size);

  const blob = (x, y, r, alpha) => {
    for (let ox = -1; ox <= 1; ox++) {
      for (let oy = -1; oy <= 1; oy++) {
        drawPuff(ctx, x + ox * size, y + oy * size, r, alpha);
      }
    }
  };

  // Streaky, bubbly foam made from wrapped puffs
  for (let i = 0; i < 150; i++) {
    const x = rand() * size;
    const y = rand() * size;
    const r = 4 + rand() * 20;
    const a = 0.12 + rand() * 0.3;
    blob(x, y, r, a);
  }
  for (let i = 0; i < 45; i++) {
    const x = rand() * size;
    const y = rand() * size;
    ctx.strokeStyle = `rgba(255,255,255,${0.12 + rand() * 0.28})`;
    ctx.lineWidth = 1 + rand() * 2.2;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.bezierCurveTo(x + 14, y - 8, x + 26, y + 9, x + 40, y + 2);
    ctx.stroke();
  }

  // break it up a little
  ctx.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < 90; i++) {
    blob(rand() * size, rand() * size, 2 + rand() * 8, 0.25 + rand() * 0.35);
  }
  ctx.globalCompositeOperation = 'source-over';

  return finish(canvas, { repeat: true });
}

export function makeBoardFoam() {
  const w = 512;
  const h = 256;
  const { canvas, ctx } = canvas2d(w, h);
  const rand = rng(14);

  // Elongated, irregular whitewater halo around the hull
  const g = ctx.createRadialGradient(w / 2, h / 2, 8, w / 2, h / 2, 210);
  g.addColorStop(0, 'rgba(255,255,255,0.55)');
  g.addColorStop(0.5, 'rgba(255,255,255,0.22)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.ellipse(w / 2, h / 2, 246, 112, 0, 0, Math.PI * 2);
  ctx.fill();

  for (let i = 0; i < 130; i++) {
    const a = rand() * Math.PI * 2;
    const d = 0.72 + rand() * 0.28;
    drawPuff(
      ctx,
      w / 2 + Math.cos(a) * 236 * d,
      h / 2 + Math.sin(a) * 104 * d,
      8 + rand() * 34,
      0.06 + rand() * 0.2,
    );
  }
  ctx.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < 50; i++) {
    const a = rand() * Math.PI * 2;
    const d = rand() * 0.9;
    drawPuff(
      ctx,
      w / 2 + Math.cos(a) * 210 * d,
      h / 2 + Math.sin(a) * 86 * d,
      6 + rand() * 22,
      0.18 + rand() * 0.25,
    );
  }
  ctx.globalCompositeOperation = 'source-over';
  return finish(canvas);
}

export function makeSprayTexture() {
  const { canvas, ctx } = canvas2d(64, 64);
  drawPuff(ctx, 32, 32, 30, 0.95);
  const tex = finish(canvas);
  return tex;
}

export function makeGlowTexture() {
  const size = 256;
  const { canvas, ctx } = canvas2d(size, size);
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(255,250,232,1)');
  g.addColorStop(0.08, 'rgba(255,242,205,0.95)');
  g.addColorStop(0.22, 'rgba(255,206,150,0.42)');
  g.addColorStop(0.55, 'rgba(255,176,120,0.11)');
  g.addColorStop(1, 'rgba(255,160,110,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return finish(canvas);
}

export function makeContactShadow() {
  const size = 256;
  const { canvas, ctx } = canvas2d(size, size);
  const g = ctx.createRadialGradient(size / 2, size / 2, 6, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(20,40,45,0.55)');
  g.addColorStop(0.45, 'rgba(20,40,45,0.32)');
  g.addColorStop(1, 'rgba(20,40,45,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return finish(canvas);
}

export function makeCloudTexture() {
  const w = 256;
  const h = 128;
  const { canvas, ctx } = canvas2d(w, h);
  const rand = rng(55);
  for (let i = 0; i < 22; i++) {
    const x = 40 + rand() * (w - 80);
    const y = h * 0.52 + (rand() - 0.5) * 30;
    const r = 18 + rand() * 34;
    drawPuff(ctx, x, y, r, 0.09 + rand() * 0.1);
  }
  return finish(canvas);
}

export function makeGrainDataURL() {
  const size = 128;
  const { canvas, ctx } = canvas2d(size, size);
  const img = ctx.createImageData(size, size);
  const rand = rng(123);
  for (let i = 0; i < size * size; i++) {
    const v = Math.floor(rand() * 255);
    img.data[i * 4] = v;
    img.data[i * 4 + 1] = v;
    img.data[i * 4 + 2] = v;
    img.data[i * 4 + 3] = Math.floor(rand() * 55);
  }
  ctx.putImageData(img, 0, 0);
  return canvas.toDataURL('image/png');
}
