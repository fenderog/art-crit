import * as THREE from 'three';

// The sun sits low and slightly to the left, giving the whole scene a long,
// honey-coloured backlight.
export const SUN_DIR = new THREE.Vector3(-0.43, 0.13, -0.89).normalize();

// This is deliberately duplicated in the ocean vertex shader. Keeping the
// height function in one readable place makes the board ride the same water.
export function waveHeight(x, z, t) {
  return (
    0.48 * Math.sin(x * 0.11 + z * 0.43 - t * 0.82 + 0.9) +
    0.24 * Math.sin(-x * 0.45 + z * 0.23 + t * 1.32 + 2.2) +
    0.11 * Math.sin(x * 0.76 - z * 0.58 - t * 1.84 + 4.0) +
    0.055 * Math.sin(-x * 1.3 - z * 1.0 + t * 2.5 + 1.1)
  );
}

function makeRadialTexture(stops, size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createRadialGradient(
    size / 2, size / 2, 0,
    size / 2, size / 2, size / 2
  );
  for (const [at, color] of stops) gradient.addColorStop(at, color);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const oceanVertexShader = /* glsl */ `
  uniform float uTime;

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vHeight;

  float waveHeight(vec2 p, float t) {
    return
      0.48 * sin(dot(p, vec2(0.11, 0.43)) - t * 0.82 + 0.9) +
      0.24 * sin(dot(p, vec2(-0.45, 0.23)) + t * 1.32 + 2.2) +
      0.11 * sin(dot(p, vec2(0.76, -0.58)) - t * 1.84 + 4.0) +
      0.055 * sin(dot(p, vec2(-1.3, -1.0)) + t * 2.5 + 1.1);
  }

  void main() {
    vec3 displaced = position;
    float height = waveHeight(position.xz, uTime);

    const float e = 0.32;
    float dx = waveHeight(position.xz + vec2(e, 0.0), uTime) - height;
    float dz = waveHeight(position.xz + vec2(0.0, e), uTime) - height;

    displaced.y += height;
    vHeight = height;
    vNormal = normalize(mat3(modelMatrix) * vec3(-dx / e, 1.0, -dz / e));
    vWorldPos = (modelMatrix * vec4(displaced, 1.0)).xyz;

    gl_Position = projectionMatrix * viewMatrix * vec4(vWorldPos, 1.0);
  }
`;

const oceanFragmentShader = /* glsl */ `
  uniform float uTime;
  uniform vec3 uDeep;
  uniform vec3 uMid;
  uniform vec3 uShallow;
  uniform vec3 uFoam;
  uniform vec3 uHorizon;
  uniform vec3 uSky;
  uniform vec3 uHaze;
  uniform vec3 uSunColor;
  uniform vec3 uSunDir;
  uniform vec2 uBoardPos;
  uniform vec2 uBoardDir;

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vHeight;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 4; i++) {
      value += amplitude * noise(p);
      p = p * 2.03 + 11.7;
      amplitude *= 0.5;
    }
    return value;
  }

  void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(cameraPosition - vWorldPos);
    vec3 L = normalize(uSunDir);
    float fresnel = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 3.0);

    float crest = smoothstep(-0.35, 0.75, vHeight);
    vec3 water = mix(uDeep, uMid, 0.28 + crest * 0.72);
    water = mix(water, uShallow, smoothstep(0.25, 0.95, vHeight) * 0.38);

    vec3 reflection = reflect(-V, N);
    vec3 skyReflection = mix(uHorizon, uSky, smoothstep(-0.08, 0.55, reflection.y));
    skyReflection = mix(
      skyReflection,
      uSunColor,
      pow(max(dot(reflection, L), 0.0), 7.0) * 0.55
    );
    water = mix(water, skyReflection, fresnel * 0.78);

    float micro = noise(vWorldPos.xz * 1.45 + vec2(uTime * 0.20, -uTime * 0.13));
    water += vec3(0.015, 0.045, 0.050) * (micro - 0.5);

    vec3 H = normalize(L + V);
    float sharpGlint = pow(max(dot(N, H), 0.0), 180.0);
    float softGlint = pow(max(dot(N, H), 0.0), 24.0);
    water += uSunColor * (sharpGlint * 1.8 + softGlint * 0.17);

    float foamNoise = fbm(vWorldPos.xz * 0.72 + vec2(uTime * 0.17, -uTime * 0.11));
    float crestFoam =
      smoothstep(0.25, 0.66, vHeight) *
      smoothstep(0.48, 0.78, foamNoise);
    float streakPhase = 0.5 + 0.5 * sin(
      vWorldPos.x * 1.7 + vWorldPos.z * 0.35 + uTime * 1.8 + foamNoise * 7.0
    );
    float streaks =
      smoothstep(0.78, 0.96, streakPhase) *
      smoothstep(0.08, 0.64, vHeight);
    float foam = clamp(crestFoam * 0.82 + streaks * 0.46, 0.0, 1.0);

    // Foam hugs the board and leaves a soft, broken wake behind it.
    vec2 forward = normalize(uBoardDir + vec2(0.0001));
    vec2 side = vec2(-forward.y, forward.x);
    vec2 fromBoard = vWorldPos.xz - uBoardPos;
    float along = dot(fromBoard, forward);
    float across = dot(fromBoard, side);
    float oval = length(vec2((along + 0.12) / 1.9, across / 0.76));
    float contact = smoothstep(1.13, 0.54, oval + (foamNoise - 0.5) * 0.18);
    float behind = 1.0 - smoothstep(-1.5, 0.2, along);
    float wakeDistance = clamp((-along - 1.3) / 6.2, 0.0, 1.0);
    float wakeWidth = abs(across + sin(along * 2.3 + uTime * 2.0 + foamNoise * 2.0) * 0.22);
    float wake =
      behind * (1.0 - wakeDistance) *
      smoothstep(0.95, 0.10, wakeWidth) *
      (0.24 + 0.76 * foamNoise);
    foam = clamp(foam + contact * 0.92 + wake * 0.78, 0.0, 1.0);

    water = mix(water, uFoam, foam * 0.84);

    float distanceToCamera = length(cameraPosition - vWorldPos);
    float haze = 1.0 - exp(-pow(distanceToCamera * 0.0082, 2.0));
    water = mix(water, uHaze, clamp(haze, 0.0, 1.0) * 0.9);

    gl_FragColor = vec4(water, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

const skyVertexShader = /* glsl */ `
  varying vec3 vWorldDirection;

  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldDirection = normalize(worldPosition.xyz - cameraPosition);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const skyFragmentShader = /* glsl */ `
  uniform vec3 uTop;
  uniform vec3 uUpper;
  uniform vec3 uMid;
  uniform vec3 uHorizon;
  uniform vec3 uSunColor;
  uniform vec3 uSunDir;
  uniform float uTime;

  varying vec3 vWorldDirection;

  float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 4; i++) {
      value += amplitude * noise(p);
      p = p * 2.02 + 5.1;
      amplitude *= 0.5;
    }
    return value;
  }

  void main() {
    vec3 dir = normalize(vWorldDirection);
    float elevation = max(dir.y, 0.0);

    vec3 colour = mix(uHorizon, uMid, smoothstep(0.0, 0.11, elevation));
    colour = mix(colour, uUpper, smoothstep(0.10, 0.34, elevation));
    colour = mix(colour, uTop, smoothstep(0.33, 0.85, elevation));

    vec3 sunDir = normalize(uSunDir);
    float sunAmount = max(dot(dir, sunDir), 0.0);

    // A broad, warm bloom and a compact, painterly sun disc.
    colour += uSunColor * pow(sunAmount, 28.0) * 0.32;
    colour += vec3(1.0, 0.45, 0.27) * pow(sunAmount, 5.0) * 0.10;

    float warmSide = pow(
      max(dot(normalize(dir.xz + vec2(0.0001)), normalize(sunDir.xz + vec2(0.0001))), 0.0),
      3.0
    );
    colour = mix(
      colour,
      vec3(1.0, 0.66, 0.49),
      warmSide * (1.0 - smoothstep(0.0, 0.38, elevation)) * 0.20
    );

    float disc = smoothstep(0.9970, 0.9980, sunAmount);
    colour = mix(colour, mix(uSunColor, vec3(1.0, 0.96, 0.82), 0.55), disc);

    // A barely-there band of high cloud keeps the gradient from feeling flat.
    vec2 cloudUV = dir.xz / (max(dir.y, 0.035) + 0.34);
    float cloudNoise = fbm(cloudUV * vec2(1.25, 2.1) + vec2(uTime * 0.003, 2.0));
    float cloudBand =
      smoothstep(0.50, 0.68, cloudNoise) *
      smoothstep(0.035, 0.075, dir.y) *
      (1.0 - smoothstep(0.11, 0.27, dir.y));
    colour = mix(colour, vec3(1.0, 0.79, 0.73), cloudBand * 0.22);

    colour = mix(colour, uHorizon * 0.72, smoothstep(0.0, -0.12, dir.y) * 0.82);
    colour += (hash(gl_FragCoord.xy) - 0.5) / 255.0;

    gl_FragColor = vec4(colour, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

function createCloud(materials, puffGeometry, puffData, scale) {
  const group = new THREE.Group();
  for (let i = 0; i < puffData.length; i++) {
    const [x, y, z, sx, sy, sz, materialIndex, rotation] = puffData[i];
    const puff = new THREE.Mesh(puffGeometry, materials[materialIndex]);
    puff.position.set(x, y, z);
    puff.scale.set(sx, sy, sz);
    puff.rotation.set(rotation * 0.17, rotation, rotation * 0.08);
    group.add(puff);
  }
  group.scale.setScalar(scale);
  return group;
}

function createIslands() {
  const islands = new THREE.Group();

  function island(x, z, scale, colour, opacity) {
    const group = new THREE.Group();
    const material = new THREE.MeshBasicMaterial({
      color: colour,
      transparent: opacity < 1,
      opacity,
      fog: true,
      depthWrite: true
    });

    const peaks = [
      [-1.0, 1.8, 0.9, 0.0, 5.8, 2.8],
      [0.5, 1.4, -0.2, 0.0, 8.4, 3.6],
      [1.8, 1.3, 0.5, 0.0, 4.9, 2.3],
      [0.0, 1.1, -1.1, 0.0, 3.8, 2.0]
    ];

    for (const [px, py, pz, rx, height, radius] of peaks) {
      const geometry = new THREE.ConeGeometry(radius, height, 7, 2);
      const peak = new THREE.Mesh(geometry, material);
      peak.position.set(px, py + height * 0.5 - 0.5, pz);
      peak.rotation.y = px * 0.6;
      peak.scale.z = 0.72;
      group.add(peak);
    }

    group.position.set(x, 0, z);
    group.scale.setScalar(scale);
    islands.add(group);
  }

  island(-61, -176, 2.15, 0x4b6d79, 0.78);
  island(49, -188, 1.25, 0x607c86, 0.55);

  return islands;
}

function createSailboat() {
  const boat = new THREE.Group();
  const cream = new THREE.MeshBasicMaterial({ color: 0xf8e7ce, fog: true });
  const dark = new THREE.MeshBasicMaterial({ color: 0x294a56, fog: true });

  const hull = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.10, 0.12), dark);
  hull.position.y = 0.03;
  boat.add(hull);

  const sailShape = new THREE.Shape();
  sailShape.moveTo(0, 0.06);
  sailShape.lineTo(0, 0.88);
  sailShape.lineTo(0.43, 0.10);
  sailShape.closePath();
  const sail = new THREE.Mesh(new THREE.ShapeGeometry(sailShape), cream);
  sail.position.z = 0.01;
  boat.add(sail);

  const mast = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.9, 0.018), dark);
  mast.position.set(0, 0.45, 0);
  boat.add(mast);

  boat.position.set(23, 0.18, -78);
  boat.rotation.y = -0.25;
  boat.scale.setScalar(0.82);
  return boat;
}

function createBirds() {
  const birds = new THREE.Group();
  const material = new THREE.LineBasicMaterial({
    color: 0x273f4d,
    transparent: true,
    opacity: 0.58,
    depthWrite: false
  });

  const specs = [
    [-14.0, 11.5, -42.0, 0.72, 0.0],
    [13.5, 14.0, -58.0, 0.58, 1.9],
    [18.0, 9.4, -46.0, 0.46, 3.8],
    [-22.0, 16.5, -65.0, 0.52, 5.1]
  ];

  for (const [x, y, z, scale, phase] of specs) {
    const points = [];
    for (let i = 0; i < 9; i++) points.push(new THREE.Vector3());
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    line.position.set(x, y, z);
    line.scale.setScalar(scale);
    line.userData.phase = phase;
    line.userData.base = new THREE.Vector3(x, y, z);
    birds.add(line);
  }

  birds.userData.update = (time, camera) => {
    for (const bird of birds.children) {
      bird.quaternion.copy(camera.quaternion);
      const phase = bird.userData.phase;
      const flap = Math.sin(time * 2.25 + phase);
      const wingLift = 0.13 + flap * 0.22;
      const positions = bird.geometry.attributes.position.array;

      const coords = [
        [-1.05, 0.05 + wingLift * 0.9],
        [-0.66, 0.13 + wingLift * 1.5],
        [-0.26, 0.06 + wingLift * 0.7],
        [0.0, 0.0],
        [0.26, 0.06 + wingLift * 0.7],
        [0.66, 0.13 + wingLift * 1.5],
        [1.05, 0.05 + wingLift * 0.9]
      ];

      for (let i = 0; i < coords.length; i++) {
        positions[i * 3] = coords[i][0];
        positions[i * 3 + 1] = coords[i][1];
        positions[i * 3 + 2] = 0;
      }
      // Keep unused points tucked behind the final wingtip.
      positions[21] = 1.05;
      positions[22] = 0.05 + wingLift * 0.9;
      positions[23] = 0;
      positions[24] = 1.05;
      positions[25] = 0.05 + wingLift * 0.9;
      positions[26] = 0;

      bird.geometry.attributes.position.needsUpdate = true;

      const drift = Math.sin(time * 0.035 + phase) * 4.0;
      bird.position.x = bird.userData.base.x + drift;
      bird.position.y = bird.userData.base.y + Math.sin(time * 0.6 + phase) * 0.35;
    }
  };

  return birds;
}

export function createWorld(scene, camera, renderer) {
  scene.fog = new THREE.FogExp2(0xe9b9a2, 0.0032);

  // ---- Lighting ---------------------------------------------------------
  const hemisphere = new THREE.HemisphereLight(0xffd7b6, 0x174f5d, 1.55);
  scene.add(hemisphere);

  const sunLight = new THREE.DirectionalLight(0xffd19a, 3.4);
  sunLight.position.copy(SUN_DIR).multiplyScalar(80);
  scene.add(sunLight);

  const coolFill = new THREE.DirectionalLight(0x9bd8e2, 1.15);
  coolFill.position.set(7, 8, 12);
  scene.add(coolFill);

  const warmBounce = new THREE.PointLight(0xffa86a, 14, 18, 2);
  warmBounce.position.set(-5, 2.4, 3);
  scene.add(warmBounce);

  // ---- Sky --------------------------------------------------------------
  const skyMaterial = new THREE.ShaderMaterial({
    uniforms: {
      uTop: { value: new THREE.Color(0x3d5f8e) },
      uUpper: { value: new THREE.Color(0x8399bd) },
      uMid: { value: new THREE.Color(0xdab8c0) },
      uHorizon: { value: new THREE.Color(0xffcda9) },
      uSunColor: { value: new THREE.Color(0xffe2a8) },
      uSunDir: { value: SUN_DIR.clone() },
      uTime: { value: 0 }
    },
    vertexShader: skyVertexShader,
    fragmentShader: skyFragmentShader,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    toneMapped: true
  });

  const sky = new THREE.Mesh(new THREE.SphereGeometry(700, 48, 32), skyMaterial);
  sky.renderOrder = -100;
  sky.frustumCulled = false;
  scene.add(sky);

  // Two soft additive veils make the painted sun feel like it is really glowing.
  const sunGlowTexture = makeRadialTexture([
    [0.0, 'rgba(255,245,210,0.92)'],
    [0.10, 'rgba(255,218,155,0.62)'],
    [0.32, 'rgba(255,159,105,0.24)'],
    [0.68, 'rgba(255,125,91,0.045)'],
    [1.0, 'rgba(255,110,80,0)']
  ], 512);

  const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: sunGlowTexture,
    color: 0xfff0ca,
    transparent: true,
    opacity: 0.82,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: true,
    fog: false,
    toneMapped: false
  }));
  sunGlow.position.copy(SUN_DIR).multiplyScalar(420);
  sunGlow.scale.set(180, 180, 1);
  sunGlow.renderOrder = -90;
  scene.add(sunGlow);

  const sunCore = new THREE.Sprite(new THREE.SpriteMaterial({
    map: sunGlowTexture,
    color: 0xfff8df,
    transparent: true,
    opacity: 0.45,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: true,
    fog: false,
    toneMapped: false
  }));
  sunCore.position.copy(SUN_DIR).multiplyScalar(419);
  sunCore.scale.set(54, 54, 1);
  sunCore.renderOrder = -89;
  scene.add(sunCore);

  // ---- Ocean ------------------------------------------------------------
  const oceanGeometry = new THREE.PlaneGeometry(460, 460, 300, 300);
  oceanGeometry.rotateX(-Math.PI / 2);

  const oceanUniforms = {
    uTime: { value: 0 },
    uDeep: { value: new THREE.Color(0x062f3e) },
    uMid: { value: new THREE.Color(0x0a7178) },
    uShallow: { value: new THREE.Color(0x3cae9d) },
    uFoam: { value: new THREE.Color(0xf5eedf) },
    uHorizon: { value: new THREE.Color(0xffcda9) },
    uSky: { value: new THREE.Color(0x7f9cbe) },
    uHaze: { value: new THREE.Color(0xe7b49f) },
    uSunColor: { value: new THREE.Color(0xffe3ab) },
    uSunDir: { value: SUN_DIR.clone() },
    uBoardPos: { value: new THREE.Vector2(0, 0) },
    uBoardDir: { value: new THREE.Vector2(0, 1) }
  };

  const oceanMaterial = new THREE.ShaderMaterial({
    uniforms: oceanUniforms,
    vertexShader: oceanVertexShader,
    fragmentShader: oceanFragmentShader,
    side: THREE.FrontSide,
    fog: false,
    toneMapped: true
  });

  const ocean = new THREE.Mesh(oceanGeometry, oceanMaterial);
  ocean.frustumCulled = false;
  scene.add(ocean);

  // ---- Clouds -----------------------------------------------------------
  const cloudPuffGeometry = new THREE.IcosahedronGeometry(1, 2);
  const cloudMaterials = [
    new THREE.MeshStandardMaterial({
      color: 0xffdfcf,
      emissive: 0x633f43,
      emissiveIntensity: 0.14,
      roughness: 1.0,
      metalness: 0.0,
      fog: true
    }),
    new THREE.MeshStandardMaterial({
      color: 0xe9bdc0,
      emissive: 0x5c3e49,
      emissiveIntensity: 0.13,
      roughness: 1.0,
      metalness: 0.0,
      fog: true
    }),
    new THREE.MeshStandardMaterial({
      color: 0xffead9,
      emissive: 0x674d47,
      emissiveIntensity: 0.10,
      roughness: 1.0,
      metalness: 0.0,
      fog: true
    })
  ];

  const cloudSpecs = [
    {
      position: [38, 14, -118],
      scale: 1.0,
      puffs: [
        [0, 0, 0, 5.4, 2.0, 2.8, 0, 0.1],
        [-4.2, 0.3, 0.2, 3.4, 1.7, 2.2, 1, 0.7],
        [4.0, -0.1, -0.2, 3.8, 1.5, 2.0, 2, 1.5],
        [1.5, 1.1, 0.1, 3.0, 1.9, 1.8, 0, 2.2],
        [-2.0, -0.8, 0.1, 3.2, 1.0, 1.7, 1, 0.4]
      ]
    },
    {
      position: [-42, 22, -150],
      scale: 1.15,
      puffs: [
        [0, 0, 0, 6.2, 1.6, 2.5, 1, 0.2],
        [-5.4, 0.1, 0.2, 3.7, 1.2, 2.0, 0, 1.1],
        [4.5, 0.4, 0.0, 4.2, 1.4, 2.2, 2, 2.8],
        [0.8, 1.0, 0.0, 3.0, 1.2, 1.7, 1, 1.8]
      ]
    },
    {
      position: [72, 7.5, -195],
      scale: 1.5,
      puffs: [
        [0, 0, 0, 6.5, 1.0, 2.2, 0, 0.1],
        [-5.8, 0.2, 0.1, 4.0, 0.8, 1.8, 1, 0.9],
        [5.2, 0.1, 0.0, 4.6, 0.8, 1.7, 2, 2.2]
      ]
    },
    {
      position: [-76, 9, -210],
      scale: 1.25,
      puffs: [
        [0, 0, 0, 7.0, 1.1, 2.4, 2, 0.5],
        [-4.4, 0.2, 0.0, 4.2, 0.9, 1.9, 0, 2.0],
        [4.7, 0.0, 0.1, 4.8, 0.7, 1.8, 1, 1.3]
      ]
    }
  ];

  for (const spec of cloudSpecs) {
    const cloud = createCloud(cloudMaterials, cloudPuffGeometry, spec.puffs, spec.scale);
    cloud.position.set(...spec.position);
    scene.add(cloud);
  }

  const islands = createIslands();
  scene.add(islands);

  const sailboat = createSailboat();
  scene.add(sailboat);

  const birds = createBirds();
  scene.add(birds);

  // ---- Little floating glints on the water ------------------------------
  const sparkleCount = 140;
  const sparklePositions = new Float32Array(sparkleCount * 3);
  const sparkleSeeds = [];
  for (let i = 0; i < sparkleCount; i++) {
    const x = (Math.random() - 0.5) * 65;
    const z = (Math.random() - 0.5) * 55;
    sparkleSeeds.push({ x, z, phase: Math.random() * Math.PI * 2 });
    sparklePositions[i * 3] = x;
    sparklePositions[i * 3 + 1] = 0.2;
    sparklePositions[i * 3 + 2] = z;
  }
  const sparkleGeometry = new THREE.BufferGeometry();
  sparkleGeometry.setAttribute('position', new THREE.BufferAttribute(sparklePositions, 3));
  const sparkleTexture = makeRadialTexture([
    [0.0, 'rgba(255,248,220,1)'],
    [0.18, 'rgba(255,220,160,0.72)'],
    [0.55, 'rgba(255,170,110,0.12)'],
    [1.0, 'rgba(255,150,100,0)']
  ], 128);
  const sparkles = new THREE.Points(
    sparkleGeometry,
    new THREE.PointsMaterial({
      map: sparkleTexture,
      color: 0xffe6b1,
      size: 0.16,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
      fog: false
    })
  );
  sparkles.frustumCulled = false;
  scene.add(sparkles);

  function update(time, dt, boardPosition, boardForward) {
    skyMaterial.uniforms.uTime.value = time;
    oceanUniforms.uTime.value = time;
    oceanUniforms.uBoardPos.value.set(boardPosition.x, boardPosition.z);
    oceanUniforms.uBoardDir.value.set(boardForward.x, boardForward.z).normalize();

    sky.position.copy(camera.position);
    sunGlow.position.copy(camera.position).addScaledVector(SUN_DIR, 420);
    sunCore.position.copy(camera.position).addScaledVector(SUN_DIR, 419);

    birds.userData.update(time, camera);

    // Refloat the tiny sunlit specks so they sit on the swell.
    const positions = sparkleGeometry.attributes.position.array;
    for (let i = 0; i < sparkleCount; i++) {
      const seed = sparkleSeeds[i];
      positions[i * 3 + 1] =
        waveHeight(seed.x, seed.z, time) +
        0.05 +
        Math.sin(time * 1.4 + seed.phase) * 0.025;
    }
    sparkleGeometry.attributes.position.needsUpdate = true;
    sparkles.material.opacity = 0.58 + Math.sin(time * 0.7) * 0.08;
  }

  return {
    update,
    ocean,
    sunLight,
    sky
  };
}
