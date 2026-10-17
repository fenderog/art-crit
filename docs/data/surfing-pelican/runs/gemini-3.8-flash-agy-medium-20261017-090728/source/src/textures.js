import * as THREE from 'three';

/**
 * Procedural texture generators for self-contained, offline-compatible graphics.
 */

// Generate a soft circular droplet texture for water spray particles
export function createSprayParticleTexture() {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
  gradient.addColorStop(0.2, 'rgba(230, 248, 255, 0.85)');
  gradient.addColorStop(0.5, 'rgba(180, 230, 255, 0.4)');
  gradient.addColorStop(0.8, 'rgba(120, 200, 255, 0.15)');
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  // Add bright tiny central specular glint
  const glint = ctx.createRadialGradient(size / 2 - 4, size / 2 - 4, 0, size / 2 - 4, size / 2 - 4, 8);
  glint.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
  glint.addColorStop(1, 'rgba(255, 255, 255, 0)');
  ctx.fillStyle = glint;
  ctx.fillRect(0, 0, size, size);

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Generate a high-resolution seamless water noise / foam texture
export function createFoamNoiseTexture() {
  const width = 512;
  const height = 512;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Deep oceanic blue base
  ctx.fillStyle = '#063a54';
  ctx.fillRect(0, 0, width, height);

  // Layered Voronoi-like cellular foam lines and streaks
  const imgData = ctx.getImageData(0, 0, width, height);
  const data = imgData.data;

  // Simple multi-frequency procedural cellular foam
  const points = [];
  const numPoints = 120;
  for (let i = 0; i < numPoints; i++) {
    points.push({
      x: Math.random() * width,
      y: Math.random() * height
    });
  }

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let minDist1 = 9999;
      let minDist2 = 9999;

      // Find two nearest points with torus wrap
      for (let i = 0; i < numPoints; i++) {
        let dx = Math.abs(x - points[i].x);
        let dy = Math.abs(y - points[i].y);
        if (dx > width / 2) dx = width - dx;
        if (dy > height / 2) dy = height - dy;
        const d = Math.sqrt(dx * dx + dy * dy);

        if (d < minDist1) {
          minDist2 = minDist1;
          minDist1 = d;
        } else if (d < minDist2) {
          minDist2 = d;
        }
      }

      // Edge detection for cell walls (foam lines)
      const edge = minDist2 - minDist1;
      let foam = 0;
      if (edge < 6.0) {
        foam = (1.0 - edge / 6.0);
        foam = Math.pow(foam, 1.5);
      }

      // Add directional foam streaks (surfing wave foam direction)
      const streak = Math.sin((x * 0.05) + Math.sin(y * 0.1) * 2.0) * 0.5 + 0.5;
      const streakNoise = Math.sin((x * 0.2) + (y * 0.05)) * 0.5 + 0.5;

      const idx = (y * width + x) * 4;
      const foamVal = Math.min(1.0, foam * 1.6 + (streak * streakNoise * 0.35));

      // Color: deep aquamarine to crisp white foam
      data[idx] = Math.floor(10 + foamVal * 245);
      data[idx + 1] = Math.floor(110 + foamVal * 145);
      data[idx + 2] = Math.floor(160 + foamVal * 95);
      data[idx + 3] = Math.floor(foamVal * 255);
    }
  }

  ctx.putImageData(imgData, 0, 0);

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(4, 4);
  texture.needsUpdate = true;
  return texture;
}

// Generate retro surfboard deck graphic with tropical racing stripes & wood stringer
export function createSurfboardDeckTexture() {
  const width = 512;
  const height = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Base off-white coconut cream
  ctx.fillStyle = '#f8f6f0';
  ctx.fillRect(0, 0, width, height);

  // Subtle fiberglass weave
  ctx.fillStyle = 'rgba(0,0,0,0.015)';
  for (let i = 0; i < height; i += 4) {
    ctx.fillRect(0, i, width, 1);
  }
  for (let j = 0; j < width; j += 4) {
    ctx.fillRect(j, 0, 1, height);
  }

  // Classic retro surf side stripes (Teal, Coral Orange, Warm Gold)
  const stripeWidth = 14;
  const midX = width / 2;

  // Outer teal stripes
  ctx.fillStyle = '#0891b2'; // cyan/teal
  ctx.fillRect(midX - 70 - stripeWidth, 0, stripeWidth, height);
  ctx.fillRect(midX + 70, 0, stripeWidth, height);

  // Coral orange stripes
  ctx.fillStyle = '#f97316'; // vibrant sunset orange
  ctx.fillRect(midX - 45 - stripeWidth, 0, stripeWidth, height);
  ctx.fillRect(midX + 45, 0, stripeWidth, height);

  // Golden yellow pin stripes
  ctx.fillStyle = '#fbbf24'; // sunny gold
  ctx.fillRect(midX - 22 - 6, 0, 6, height);
  ctx.fillRect(midX + 22, 0, 6, height);

  // Central dark koa/balsa wood stringer
  ctx.fillStyle = '#6b3a16'; // rich wood grain
  ctx.fillRect(midX - 4, 0, 8, height);
  ctx.fillStyle = '#4a2408'; // stringer center pinstripe
  ctx.fillRect(midX - 1, 0, 2, height);

  // Stylized Pelican Surf Club badge logo near the nose!
  const logoY = 240;
  ctx.save();
  ctx.beginPath();
  ctx.arc(midX, logoY, 42, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = '#f97316';
  ctx.stroke();

  // Draw tropical sun & waves emblem in the circle
  ctx.beginPath();
  ctx.arc(midX, logoY - 6, 16, 0, Math.PI * 2);
  ctx.fillStyle = '#f59e0b';
  ctx.fill();

  // Wave silhouette in badge
  ctx.beginPath();
  ctx.moveTo(midX - 28, logoY + 12);
  ctx.quadraticCurveTo(midX - 10, logoY - 2, midX, logoY + 8);
  ctx.quadraticCurveTo(midX + 15, logoY - 8, midX + 28, logoY + 12);
  ctx.lineTo(midX + 28, logoY + 28);
  ctx.lineTo(midX - 28, logoY + 28);
  ctx.closePath();
  ctx.fillStyle = '#0284c7';
  ctx.fill();

  ctx.restore();

  // Wax traction texture in rear stance area
  ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
  for (let y = 600; y < 900; y += 12) {
    for (let x = 160; x < 352; x += 12) {
      if (Math.random() > 0.3) {
        ctx.beginPath();
        ctx.arc(x + (Math.random() - 0.5) * 4, y + (Math.random() - 0.5) * 4, 3 + Math.random() * 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Pelican eye texture with warm amber iris and glossy pupil
export function createPelicanEyeTexture() {
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Eye sclera (soft pale cream)
  ctx.fillStyle = '#f5f0eb';
  ctx.fillRect(0, 0, size, size);

  const cx = size / 2;
  const cy = size / 2;
  const irisRadius = 75;

  // Iris gradient (amber/golden brown characteristic of pelicans)
  const irisGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, irisRadius);
  irisGrad.addColorStop(0, '#f59e0b'); // bright gold
  irisGrad.addColorStop(0.6, '#d97706'); // warm amber
  irisGrad.addColorStop(0.85, '#92400e'); // rich brown
  irisGrad.addColorStop(1, '#451a03'); // dark rim

  ctx.beginPath();
  ctx.arc(cx, cy, irisRadius, 0, Math.PI * 2);
  ctx.fillStyle = irisGrad;
  ctx.fill();

  // Iris radial striations
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.4)';
  ctx.lineWidth = 1.5;
  for (let a = 0; a < Math.PI * 2; a += 0.1) {
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * 25, cy + Math.sin(a) * 25);
    ctx.lineTo(cx + Math.cos(a) * (irisRadius - 4), cy + Math.sin(a) * (irisRadius - 4));
    ctx.stroke();
  }

  // Deep dark pupil
  const pupilRadius = 34;
  ctx.beginPath();
  ctx.arc(cx, cy, pupilRadius, 0, Math.PI * 2);
  ctx.fillStyle = '#0f172a';
  ctx.fill();

  // Glossy specular highlight
  const highlightGrad = ctx.createRadialGradient(cx - 14, cy - 16, 0, cx - 14, cy - 16, 18);
  highlightGrad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
  highlightGrad.addColorStop(0.5, 'rgba(255, 255, 255, 0.7)');
  highlightGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');

  ctx.beginPath();
  ctx.arc(cx - 14, cy - 16, 18, 0, Math.PI * 2);
  ctx.fillStyle = highlightGrad;
  ctx.fill();

  // Secondary small reflection
  ctx.beginPath();
  ctx.arc(cx + 12, cy + 14, 6, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
  ctx.fill();

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

// Procedural feather bump/normal map
export function createFeatherNormalTexture() {
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Neutral normal color: RGB(128, 128, 255)
  ctx.fillStyle = 'rgb(128, 128, 255)';
  ctx.fillRect(0, 0, size, size);

  // Soft overlapping feather vane grooves
  for (let y = 0; y < size; y += 8) {
    ctx.fillStyle = 'rgba(160, 128, 240, 0.2)';
    ctx.fillRect(0, y, size, 3);
    ctx.fillStyle = 'rgba(96, 128, 255, 0.2)';
    ctx.fillRect(0, y + 4, size, 3);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(3, 3);
  texture.needsUpdate = true;
  return texture;
}
