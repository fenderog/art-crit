import * as THREE from 'three';

/**
 * Creates a procedural seamless normal map for ocean ripples.
 */
export function createWaveNormalTexture() {
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  const imgData = ctx.createImageData(size, size);
  const data = imgData.data;

  // Generate height field with multi-octave sine/perlin waves
  const height = new Float32Array(size * size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const u = (x / size) * Math.PI * 2;
      const v = (y / size) * Math.PI * 2;
      const h =
        Math.sin(u * 3 + v * 2) * 0.4 +
        Math.cos(u * 5 - v * 4) * 0.3 +
        Math.sin(u * 9 + v * 8) * 0.15 +
        Math.cos(u * 14 - v * 12) * 0.08;
      height[y * size + x] = h;
    }
  }

  // Compute normals using central differences
  for (let y = 0; y < size; y++) {
    const ym = (y - 1 + size) % size;
    const yp = (y + 1) % size;
    for (let x = 0; x < size; x++) {
      const xm = (x - 1 + size) % size;
      const xp = (x + 1) % size;

      const dx = (height[y * size + xp] - height[y * size + xm]) * 4.0;
      const dy = (height[yp * size + x] - height[ym * size + x]) * 4.0;
      const dz = 1.0;

      const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
      const nx = -dx / len;
      const ny = -dy / len;
      const nz = dz / len;

      const idx = (y * size + x) * 4;
      data[idx] = Math.floor((nx * 0.5 + 0.5) * 255);
      data[idx + 1] = Math.floor((ny * 0.5 + 0.5) * 255);
      data[idx + 2] = Math.floor((nz * 0.5 + 0.5) * 255);
      data[idx + 3] = 255;
    }
  }

  ctx.putImageData(imgData, 0, 0);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(8, 8);
  return texture;
}

/**
 * Creates a procedural sea foam texture with organic cellular web patterns.
 */
export function createWaveFoamTexture() {
  const size = 512;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Dark / transparent background
  ctx.fillStyle = 'rgba(0, 0, 0, 0)';
  ctx.fillRect(0, 0, size, size);

  // Draw cellular foam bubbles and webbing
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
  ctx.fillStyle = 'rgba(240, 255, 255, 0.45)';

  const numCells = 160;
  const points = [];
  for (let i = 0; i < numCells; i++) {
    points.push({
      x: Math.random() * size,
      y: Math.random() * size,
      r: 6 + Math.random() * 22
    });
  }

  // Draw bubble clusters
  for (const p of points) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.lineWidth = 2.0;
    ctx.stroke();
    ctx.fill();

    // Secondary inner froth
    if (p.r > 12) {
      ctx.beginPath();
      ctx.arc(p.x + (Math.random() - 0.5) * 4, p.y + (Math.random() - 0.5) * 4, p.r * 0.45, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.fill();
    }
  }

  // Interconnecting filament trails
  ctx.lineWidth = 1.5;
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const dx = points[i].x - points[j].x;
      const dy = points[i].y - points[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 45) {
        ctx.beginPath();
        ctx.moveTo(points[i].x, points[i].y);
        ctx.lineTo(points[j].x, points[j].y);
        ctx.strokeStyle = `rgba(255, 255, 255, ${(1 - dist / 45) * 0.7})`;
        ctx.stroke();
      }
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);
  return texture;
}

/**
 * Creates high-detail retro airbrush artwork for the surfboard deck.
 */
export function createSurfboardTexture() {
  const width = 512;
  const height = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // 1. Base vibrant sunset gradient (nose = vibrant pink/magenta, center = golden yellow/orange, tail = cyan/teal)
  const grad = ctx.createLinearGradient(0, 0, 0, height);
  grad.addColorStop(0.0, '#ff2a70');  // Neon pink nose
  grad.addColorStop(0.25, '#ff6a00'); // Sunset orange
  grad.addColorStop(0.50, '#ffcb00'); // Radiant golden yellow
  grad.addColorStop(0.75, '#00d2be'); // Tropical turquoise
  grad.addColorStop(1.0, '#0077b6');  // Deep ocean cyan tail
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, width, height);

  // 2. Dual racing speed stripes along rails
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 14;
  ctx.strokeRect(30, 40, width - 60, height - 80);

  ctx.strokeStyle = '#111827';
  ctx.lineWidth = 6;
  ctx.strokeRect(48, 56, width - 96, height - 112);

  // 3. Natural wooden stringer down the center
  const stringerWidth = 12;
  const stringerX = (width - stringerWidth) / 2;
  const woodGrad = ctx.createLinearGradient(stringerX, 0, stringerX + stringerWidth, 0);
  woodGrad.addColorStop(0, '#5c3317');
  woodGrad.addColorStop(0.5, '#b8860b');
  woodGrad.addColorStop(1, '#5c3317');
  ctx.fillStyle = woodGrad;
  ctx.fillRect(stringerX, 0, stringerWidth, height);

  // 4. Subtle airbrush sunburst glow in mid-deck
  const sunGlow = ctx.createRadialGradient(width / 2, height * 0.42, 10, width / 2, height * 0.42, 180);
  sunGlow.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
  sunGlow.addColorStop(0.5, 'rgba(255, 220, 100, 0.25)');
  sunGlow.addColorStop(1, 'rgba(255, 100, 0, 0)');
  ctx.fillStyle = sunGlow;
  ctx.beginPath();
  ctx.arc(width / 2, height * 0.42, 180, 0, Math.PI * 2);
  ctx.fill();

  // 5. Retro Hawaiian Surf Decal / Logo
  ctx.save();
  ctx.translate(width / 2, height * 0.38);

  // Logo circle
  ctx.beginPath();
  ctx.arc(0, 0, 75, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = '#ffcb00';
  ctx.stroke();

  // Palm tree silhouette
  ctx.fillStyle = '#00f5d4';
  ctx.beginPath();
  // Trunk
  ctx.moveTo(-4, 45);
  ctx.quadraticCurveTo(-15, 5, 0, -15);
  ctx.quadraticCurveTo(-5, 5, 4, 45);
  ctx.fill();
  // Fronds
  ctx.beginPath();
  ctx.arc(0, -15, 30, Math.PI, 0);
  ctx.lineWidth = 6;
  ctx.strokeStyle = '#00f5d4';
  ctx.stroke();

  // Text: "PELICAN POINT"
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 22px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('PELICAN', 0, -32);
  ctx.fillStyle = '#ff9f1c';
  ctx.font = 'bold 15px sans-serif';
  ctx.fillText('SURF CO.', 0, 62);
  ctx.restore();

  // 6. Tail Traction Pad (black diamond grooved grip near the rear)
  const padY = height * 0.72;
  const padHeight = height * 0.22;
  const padWidth = width * 0.65;
  const padX = (width - padWidth) / 2;

  ctx.fillStyle = '#1e293b';
  ctx.beginPath();
  ctx.roundRect(padX, padY, padWidth, padHeight, 20);
  ctx.fill();
  ctx.strokeStyle = '#0f172a';
  ctx.lineWidth = 4;
  ctx.stroke();

  // Diamond traction pattern
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 2;
  for (let x = padX; x < padX + padWidth; x += 16) {
    ctx.beginPath();
    ctx.moveTo(x, padY);
    ctx.lineTo(x + 20, padY + padHeight);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x + 20, padY);
    ctx.lineTo(x, padY + padHeight);
    ctx.stroke();
  }

  // Traction kicker arch
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(padX + 20, padY + padHeight - 20, padWidth - 40, 16);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Creates soft water droplet sprite for spray particles.
 */
export function createSprayParticleTexture() {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  const grad = ctx.createRadialGradient(size / 2, size / 2, 2, size / 2, size / 2, size / 2);
  grad.addColorStop(0.0, 'rgba(255, 255, 255, 1.0)');
  grad.addColorStop(0.35, 'rgba(220, 248, 255, 0.8)');
  grad.addColorStop(0.7, 'rgba(180, 235, 250, 0.3)');
  grad.addColorStop(1.0, 'rgba(150, 220, 240, 0.0)');

  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
  ctx.fill();

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}
