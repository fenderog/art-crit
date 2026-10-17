import * as THREE from "three";

// Late-afternoon light, sun low behind the wave so the lip glows.
export const SUN_DIR = new THREE.Vector3(-0.75, 0.36, -0.62).normalize();

export const palette = {
  zenith: new THREE.Color("#2a5fa8"),
  horizon: new THREE.Color("#f6d2a6"),
  sun: new THREE.Color("#fff1d8"),
};

export const skyUniforms = {
  uSunDir: { value: SUN_DIR },
  uZenith: { value: palette.zenith },
  uHorizon: { value: palette.horizon },
  uSunColor: { value: palette.sun },
};

// Shared between the sky dome and the water reflections / horizon haze.
export const skyGLSL = /* glsl */ `
uniform vec3 uSunDir;
uniform vec3 uZenith;
uniform vec3 uHorizon;
uniform vec3 uSunColor;

vec3 skyColor(vec3 d) {
  float y = clamp(d.y, 0.0, 1.0);
  vec3 col = mix(uHorizon, uZenith, pow(y, 0.42));
  // slight blue band just above the horizon away from the sun
  float sd = max(dot(d, uSunDir), 0.0);
  col = mix(col, uHorizon * vec3(1.05, 0.92, 0.85), (1.0 - smoothstep(0.0, 0.25, y)) * 0.35 * sd);
  col += uSunColor * (pow(sd, 5.0) * 0.28 + pow(sd, 48.0) * 0.55);
  return col;
}
`;

export function createSky() {
  const group = new THREE.Group();

  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(1500, 48, 24),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: { ...skyUniforms },
      vertexShader: /* glsl */ `
        varying vec3 vDir;
        void main() {
          vDir = normalize(position);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }`,
      fragmentShader: /* glsl */ `
        varying vec3 vDir;
        ${skyGLSL}
        void main() {
          vec3 d = normalize(vDir);
          vec3 col = skyColor(d);
          float sd = dot(d, uSunDir);
          col += uSunColor * smoothstep(0.99955, 0.99975, sd) * 30.0;
          gl_FragColor = vec4(col, 1.0);
        }`,
    })
  );
  dome.renderOrder = -10;
  dome.frustumCulled = false;
  group.add(dome);

  // Distant islands: hazy silhouettes on the horizon.
  const haze = palette.horizon.clone().lerp(new THREE.Color("#5a6f8a"), 0.42);
  const islandMat = new THREE.MeshBasicMaterial({ color: haze });
  const islands = [
    [-0.95, 1.0, 70, 26],
    [-0.82, 1.05, 110, 44],
    [-0.7, 1.0, 50, 18],
    [-0.35, 0.98, 40, 12],
    [0.55, 1.0, 90, 20],
  ];
  for (const [ang, dist, w, h] of islands) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), islandMat);
    const r = 1100 * dist;
    m.position.set(Math.sin(ang) * r, -2, -Math.cos(ang) * r);
    m.scale.set(w, h, w * 0.6);
    m.rotation.y = -ang;
    m.renderOrder = -9;
    group.add(m);
  }

  // Painted clouds, generated on a canvas.
  const cloudTex = makeCloudTexture();
  const rand = mulberry(7);
  for (let i = 0; i < 16; i++) {
    const ang = -1.9 + rand() * 3.4;
    const elev = 0.03 + rand() * 0.2;
    const r = 1150;
    const mat = new THREE.SpriteMaterial({
      map: cloudTex,
      transparent: true,
      depthWrite: false,
      fog: false,
      opacity: 0.55 + rand() * 0.35,
    });
    // clouds near the sun are warmer
    const toSun = Math.max(0, Math.cos(ang - Math.atan2(SUN_DIR.x, -SUN_DIR.z)));
    mat.color.set("#ffffff").lerp(new THREE.Color("#ffc9a0"), toSun * 0.6);
    const s = new THREE.Sprite(mat);
    s.position.set(Math.sin(ang) * r * Math.cos(elev), Math.sin(elev) * r + 20, -Math.cos(ang) * r * Math.cos(elev));
    const w = 160 + rand() * 260;
    s.scale.set(w, w * (0.28 + rand() * 0.12), 1);
    s.renderOrder = -8;
    group.add(s);
  }

  return {
    group,
    update(camera) {
      group.position.copy(camera.position);
    },
  };
}

function makeCloudTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 192;
  const g = c.getContext("2d");
  const rand = mulberry(3);
  for (let i = 0; i < 70; i++) {
    const x = 70 + rand() * 372;
    const bulge = Math.sin(((x - 70) / 372) * Math.PI);
    const y = 120 - rand() * 60 * bulge;
    const r = 18 + rand() * 40 * (0.4 + bulge);
    const grd = g.createRadialGradient(x, y, 0, x, y, r);
    const shade = Math.round(235 + (y < 100 ? 20 : 0));
    grd.addColorStop(0, `rgba(${shade},${shade},${shade},0.55)`);
    grd.addColorStop(1, `rgba(${shade},${shade},${shade},0)`);
    g.fillStyle = grd;
    g.beginPath();
    g.arc(x, y, r, 0, Math.PI * 2);
    g.fill();
  }
  // soft flat underside
  const fade = g.createLinearGradient(0, 120, 0, 192);
  fade.addColorStop(0, "rgba(0,0,0,0)");
  fade.addColorStop(1, "rgba(0,0,0,1)");
  g.globalCompositeOperation = "destination-out";
  g.fillStyle = fade;
  g.fillRect(0, 120, 512, 72);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
