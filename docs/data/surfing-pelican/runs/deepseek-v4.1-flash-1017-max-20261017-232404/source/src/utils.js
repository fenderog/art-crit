import * as THREE from 'three';

/* -------------------------------------------------------------------------- */
/*  Small deterministic helpers                                                */
/* -------------------------------------------------------------------------- */

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function random() {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function canvas2d(width, height) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return { canvas, ctx: canvas.getContext('2d') };
}

function textureFromCanvas(canvas, { srgb = true } = {}) {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  texture.anisotropy = 4;
  return texture;
}

/* -------------------------------------------------------------------------- */
/*  Generated image assets                                                     */
/* -------------------------------------------------------------------------- */

export function makeSoftCircleTexture(size = 128) {
  const { canvas, ctx } = canvas2d(size, size);
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.22, 'rgba(255,255,255,0.95)');
  g.addColorStop(0.55, 'rgba(255,255,255,0.36)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return textureFromCanvas(canvas, { srgb: false });
}

export function makeGlowTexture(size = 512, stops = null) {
  const { canvas, ctx } = canvas2d(size, size);
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  const s = stops ?? [
    [0, 'rgba(255,247,224,1)'],
    [0.08, 'rgba(255,224,166,0.98)'],
    [0.24, 'rgba(255,168,103,0.48)'],
    [0.55, 'rgba(255,124,91,0.13)'],
    [1, 'rgba(255,100,80,0)']
  ];
  for (const [p, c] of s) g.addColorStop(p, c);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return textureFromCanvas(canvas, { srgb: false });
}

export function makeShadowTexture(size = 256) {
  const { canvas, ctx } = canvas2d(size, size);
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(8,22,25,0.46)');
  g.addColorStop(0.42, 'rgba(8,22,25,0.27)');
  g.addColorStop(0.78, 'rgba(8,22,25,0.06)');
  g.addColorStop(1, 'rgba(8,22,25,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  return textureFromCanvas(canvas, { srgb: false });
}

export function makeCloudTexture(seed = 8, warm = '#fff1d9') {
  const { canvas, ctx } = canvas2d(768, 384);
  const rand = mulberry32(seed);
  const blobs = 34;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.globalCompositeOperation = 'source-over';

  for (let i = 0; i < blobs; i++) {
    const angle = rand() * Math.PI * 2;
    const radial = Math.pow(rand(), 0.7);
    const cx = canvas.width * 0.5 + Math.cos(angle) * radial * canvas.width * 0.36;
    const cy = canvas.height * 0.54 + Math.sin(angle) * radial * canvas.height * 0.24;
    const rx = 28 + rand() * 110;
    const ry = rx * (0.16 + rand() * 0.28);
    const alpha = 0.035 + rand() * 0.095;
    const rotation = (rand() - 0.5) * 0.2;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rotation);
    ctx.scale(1, ry / rx);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx);
    g.addColorStop(0, `rgba(255,255,255,${alpha})`);
    g.addColorStop(0.55, `rgba(255,255,255,${alpha * 0.65})`);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(0, 0, rx, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // A warm, brighter crown gives the cloud a sunlit edge.
  ctx.save();
  ctx.globalCompositeOperation = 'source-atop';
  const sheen = ctx.createLinearGradient(0, 0, 0, canvas.height);
  sheen.addColorStop(0, warm);
  sheen.addColorStop(0.46, 'rgba(255,255,255,0.88)');
  sheen.addColorStop(0.7, 'rgba(255,187,152,0.55)');
  sheen.addColorStop(1, 'rgba(166,96,126,0.24)');
  ctx.fillStyle = sheen;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.restore();

  return textureFromCanvas(canvas);
}

export function makeHibiscusTexture(size = 512) {
  const { canvas, ctx } = canvas2d(size, size);
  const c = size / 2;
  ctx.clearRect(0, 0, size, size);

  // Two little tropical leaves peeking out behind the bloom.
  ctx.save();
  ctx.translate(c, c);
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.rotate(side * 1.03);
    const leaf = ctx.createLinearGradient(0, 0, 0, size * 0.39);
    leaf.addColorStop(0, 'rgba(32,145,131,0.96)');
    leaf.addColorStop(1, 'rgba(12,87,82,0.9)');
    ctx.fillStyle = leaf;
    ctx.beginPath();
    ctx.ellipse(side * 34, -size * 0.13, size * 0.085, size * 0.26, side * 0.62, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(3,52,49,0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(side * 17, -size * 0.0);
    ctx.quadraticCurveTo(side * 42, -size * 0.14, side * 52, -size * 0.33);
    ctx.stroke();
    ctx.restore();
  }
  ctx.restore();

  // Five rounded, cream petals.
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
    ctx.save();
    ctx.translate(c, c);
    ctx.rotate(a);
    const petal = ctx.createRadialGradient(0, -size * 0.12, 8, 0, -size * 0.26, size * 0.27);
    petal.addColorStop(0, 'rgba(255,225,174,0.98)');
    petal.addColorStop(0.55, 'rgba(255,239,209,0.98)');
    petal.addColorStop(0.9, 'rgba(255,179,129,0.95)');
    petal.addColorStop(1, 'rgba(255,139,104,0.72)');
    ctx.fillStyle = petal;
    ctx.beginPath();
    ctx.ellipse(0, -size * 0.22, size * 0.135, size * 0.23, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(232,102,85,0.25)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, -size * 0.04);
    ctx.quadraticCurveTo(size * 0.025, -size * 0.22, 0, -size * 0.39);
    ctx.stroke();
    ctx.restore();
  }

  // Golden stamens.
  ctx.save();
  ctx.translate(c, c);
  ctx.strokeStyle = 'rgba(156,89,32,0.9)';
  ctx.lineWidth = 4;
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    const r = size * (0.11 + (i % 3) * 0.014);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,219,103,1)';
    ctx.beginPath();
    ctx.arc(Math.cos(a) * r, Math.sin(a) * r, 5, 0, Math.PI * 2);
    ctx.fill();
  }
  const core = ctx.createRadialGradient(0, 0, 0, 0, 0, size * 0.11);
  core.addColorStop(0, 'rgba(255,243,172,1)');
  core.addColorStop(0.6, 'rgba(251,199,75,1)');
  core.addColorStop(1, 'rgba(208,112,37,0.8)');
  ctx.fillStyle = core;
  ctx.beginPath();
  ctx.arc(0, 0, size * 0.105, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  return textureFromCanvas(canvas);
}

export function makeGrainDataURL(size = 180) {
  const { canvas, ctx } = canvas2d(size, size);
  const image = ctx.createImageData(size, size);
  for (let i = 0; i < image.data.length; i += 4) {
    const v = Math.floor(Math.random() * 255);
    image.data[i] = v;
    image.data[i + 1] = v;
    image.data[i + 2] = v;
    image.data[i + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
  return canvas.toDataURL('image/png');
}

/* -------------------------------------------------------------------------- */
/*  Geometry builders                                                          */
/* -------------------------------------------------------------------------- */

export function createTaperedTube(curve, radiusAt, tubularSegments = 28, radialSegments = 12) {
  const frames = curve.computeFrenetFrames(tubularSegments, false);
  const positions = [];
  const uvs = [];
  const indices = [];
  const point = new THREE.Vector3();
  const normal = new THREE.Vector3();

  for (let i = 0; i <= tubularSegments; i++) {
    const t = i / tubularSegments;
    curve.getPointAt(t, point);
    const radius = radiusAt(t);
    const N = frames.normals[i];
    const B = frames.binormals[i];

    for (let j = 0; j <= radialSegments; j++) {
      const v = (j / radialSegments) * Math.PI * 2;
      const sin = Math.sin(v);
      const cos = -Math.cos(v);
      normal.copy(N).multiplyScalar(cos).addScaledVector(B, sin).normalize();
      positions.push(
        point.x + radius * normal.x,
        point.y + radius * normal.y,
        point.z + radius * normal.z
      );
      uvs.push(t, j / radialSegments);
    }
  }

  for (let i = 1; i <= tubularSegments; i++) {
    for (let j = 1; j <= radialSegments; j++) {
      const a = (radialSegments + 1) * (i - 1) + (j - 1);
      const b = (radialSegments + 1) * i + (j - 1);
      const c = (radialSegments + 1) * i + j;
      const d = (radialSegments + 1) * (i - 1) + j;
      indices.push(a, d, b, b, d, c);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Builds a smooth loft with its long axis travelling along X.
 * Sections look like { x, y, z, w, h } where w is half-width (Z) and h is half-height (Y).
 */
export function createLoft(sections, segments = 30, radialSegments = 18) {
  const centerCurve = new THREE.CatmullRomCurve3(
    sections.map((s) => new THREE.Vector3(s.x, s.y, s.z ?? 0)),
    false,
    'catmullrom',
    0.35
  );
  const widthCurve = new THREE.CatmullRomCurve3(
    sections.map((s) => new THREE.Vector3(s.w, 0, 0)),
    false,
    'catmullrom',
    0.35
  );
  const heightCurve = new THREE.CatmullRomCurve3(
    sections.map((s) => new THREE.Vector3(s.h, 0, 0)),
    false,
    'catmullrom',
    0.35
  );

  const positions = [];
  const uvs = [];
  const indices = [];
  const p = new THREE.Vector3();
  const wp = new THREE.Vector3();
  const hp = new THREE.Vector3();

  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    centerCurve.getPoint(t, p);
    widthCurve.getPoint(t, wp);
    heightCurve.getPoint(t, hp);
    const w = Math.max(0.0015, wp.x);
    const h = Math.max(0.0015, hp.x);

    for (let j = 0; j <= radialSegments; j++) {
      const a = (j / radialSegments) * Math.PI * 2;
      positions.push(p.x, p.y + Math.cos(a) * h, p.z + Math.sin(a) * w);
      uvs.push(t, j / radialSegments);
    }
  }

  for (let i = 1; i <= segments; i++) {
    for (let j = 1; j <= radialSegments; j++) {
      const a = (radialSegments + 1) * (i - 1) + (j - 1);
      const b = (radialSegments + 1) * i + (j - 1);
      const c = (radialSegments + 1) * i + j;
      const d = (radialSegments + 1) * (i - 1) + j;
      indices.push(a, b, d, b, c, d);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * A single stylised feather, root at x=0 and tip at x=1.
 * Vertex colours let the outer third fade to a smoky, darker tip.
 */
export function createFeatherGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, 0.055);
  shape.bezierCurveTo(0.12, 0.115, 0.56, 0.125, 1.0, 0.0);
  shape.bezierCurveTo(0.56, -0.125, 0.12, -0.115, 0, -0.055);
  shape.closePath();

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.024,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.012,
    bevelSegments: 2,
    curveSegments: 20,
    steps: 1
  });
  geometry.translate(0, 0, -0.012);
  geometry.computeVertexNormals();

  const position = geometry.getAttribute('position');
  const colors = new Float32Array(position.count * 3);
  const base = new THREE.Color(0xfff2de);
  const middle = new THREE.Color(0xffe4c7);
  const tip = new THREE.Color(0x686171);
  const color = new THREE.Color();

  for (let i = 0; i < position.count; i++) {
    const x = position.getX(i);
    const t = THREE.MathUtils.clamp(x, 0, 1);
    if (t < 0.62) {
      color.copy(base).lerp(middle, THREE.MathUtils.smoothstep(t, 0.0, 0.62));
    } else {
      color.copy(middle).lerp(tip, THREE.MathUtils.smoothstep(t, 0.62, 1.0));
    }
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
  }
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  return geometry;
}

/**
 * Creates a basis whose local +X points along `direction` and whose
 * local +Y remains as close to world up as possible.
 */
export function orientXAlong(object, direction) {
  const xAxis = direction.clone().normalize();
  const worldUp = new THREE.Vector3(0, 1, 0);
  const zAxis = new THREE.Vector3().crossVectors(xAxis, worldUp);
  if (zAxis.lengthSq() < 1e-6) zAxis.set(0, 0, 1);
  zAxis.normalize();
  const yAxis = new THREE.Vector3().crossVectors(zAxis, xAxis).normalize();
  const basis = new THREE.Matrix4().makeBasis(xAxis, yAxis, zAxis);
  object.quaternion.setFromRotationMatrix(basis);
}
