import * as THREE from 'three';
import { waveHeight } from './waves.js';
import {
  makeBoardFoam,
  makeFoamPuff,
  makeFoamTile,
  makeSprayTexture,
  rng,
} from './textures.js';

function particleMaterial(texture, { additive = false, softness = 1 } = {}) {
  return new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: texture },
      uPixelScale: { value: 800 },
      uOpacity: { value: 1 },
      uWarm: { value: new THREE.Color('#fff8ea') },
      uSoftness: { value: softness },
    },
    vertexShader: /* glsl */ `
      attribute float aSize;
      attribute float aAlpha;
      uniform float uPixelScale;
      varying float vAlpha;
      void main() {
        vAlpha = aAlpha;
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = aSize * uPixelScale / max(0.001, -mv.z);
        gl_Position = projectionMatrix * mv;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap;
      uniform vec3 uWarm;
      uniform float uOpacity;
      varying float vAlpha;
      void main() {
        vec4 t = texture2D(uMap, gl_PointCoord);
        float a = t.a * vAlpha * uOpacity;
        if (a < 0.003) discard;
        gl_FragColor = vec4(uWarm, a);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
  });
}

function createFoamParticles(count = 170) {
  const rand = rng(411);
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);
  const data = [];

  for (let i = 0; i < count; i++) {
    data.push({
      x: 0,
      z: 0,
      vx: 0,
      vz: 0,
      age: rand() * 2.5,
      life: 1.4 + rand() * 1.5,
      size: 0.3 + rand() * 0.35,
      spin: rand() * 6.28,
    });
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));

  const mat = particleMaterial(makeFoamPuff(), { additive: false });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  points.renderOrder = 3;

  let cursor = 0;
  let emitAcc = 0;
  const tmp = new THREE.Vector3();

  function spawn(d, state, initial = false) {
    const rand2 = rand;
    const along = (rand2() - 0.5) * 1.2;
    const lag = -1.5 - rand2() * 0.9;
    d.x =
      state.position.x +
      state.forward.x * lag +
      state.right.x * along;
    d.z =
      state.position.z +
      state.forward.z * lag +
      state.right.z * along;
    const outward = Math.sign(along) || 1;
    d.vx = state.right.x * outward * (0.15 + rand2() * 0.45) - state.forward.x * 0.2;
    d.vz = state.right.z * outward * (0.15 + rand2() * 0.45) - state.forward.z * 0.2;
    d.age = initial ? rand2() * d.life * 1.2 : 0;
    d.life = 1.5 + rand2() * 1.7;
    d.size = 0.28 + rand2() * 0.35;
    d.spin = rand2() * 6.28;
  }

  function update(t, dt, state, camera) {
    emitAcc += dt * 72;
    while (emitAcc > 1) {
      emitAcc -= 1;
      const d = data[cursor];
      spawn(d, state);
      cursor = (cursor + 1) % count;
    }

    for (let i = 0; i < count; i++) {
      const d = data[i];
      d.age += dt;
      if (d.age > d.life) {
        spawn(d, state, false);
      }
      d.x += d.vx * dt;
      d.z += d.vz * dt;
      d.vx *= 1 - dt * 0.9;
      d.vz *= 1 - dt * 0.9;

      const u = Math.min(1, d.age / d.life);
      const y = waveHeight(d.x, d.z, t) + 0.035 + Math.sin(t * 2 + d.spin) * 0.008;
      positions[i * 3] = d.x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = d.z;
      sizes[i] = d.size + u * 0.9;
      alphas[i] = Math.sin(Math.min(1, u) * Math.PI) ** 0.6 * 0.5;
    }

    geo.attributes.position.needsUpdate = true;
    geo.attributes.aSize.needsUpdate = true;
    geo.attributes.aAlpha.needsUpdate = true;

    // keep the point scale in sync with the camera
    const pxScale =
      (window.devicePixelRatio ? Math.min(window.devicePixelRatio, 2) : 1) * 0;
    // pixel scale is supplied by the parent
    void pxScale;
  }

  function setPixelScale(v) {
    mat.uniforms.uPixelScale.value = v;
  }

  return { points, update, setPixelScale, spawnAt: (state) => spawn(data[cursor], state) };
}

function createSpray(count = 150) {
  const rand = rng(931);
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);
  const data = [];
  for (let i = 0; i < count; i++) {
    data.push({
      x: 0,
      y: -100,
      z: 0,
      vx: 0,
      vy: 0,
      vz: 0,
      age: 99,
      life: 1,
      size: 0.05,
    });
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));

  const mat = particleMaterial(makeSprayTexture(), { additive: true });
  mat.uniforms.uOpacity.value = 0.85;
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  points.renderOrder = 4;

  let cursor = 0;
  let acc = 0;
  let burstTimer = 0.7;

  function emit(state, explosive = false) {
    const d = data[cursor];
    cursor = (cursor + 1) % count;
    const side = rand() > 0.5 ? 1 : -1;
    const forwardOffset = explosive ? 1.35 + rand() * 0.75 : 0.9 + rand() * 0.9;
    const sideOffset = (0.4 + rand() * 0.28) * side;
    d.x =
      state.position.x +
      state.forward.x * forwardOffset +
      state.right.x * sideOffset;
    d.z =
      state.position.z +
      state.forward.z * forwardOffset +
      state.right.z * sideOffset;
    d.y = waveHeight(d.x, d.z, state.time) + 0.09;
    const up = explosive ? 1.8 + rand() * 2.6 : 1.0 + rand() * 2.0;
    d.vx = state.right.x * side * (0.7 + rand() * 1.2) - state.forward.x * (0.3 + rand() * 0.7);
    d.vz = state.right.z * side * (0.7 + rand() * 1.2) - state.forward.z * (0.3 + rand() * 0.7);
    d.vy = up;
    d.age = 0;
    d.life = 0.55 + rand() * 0.65;
    d.size = 0.025 + rand() * 0.055;
  }

  function update(t, dt, state) {
    acc += dt * 24;
    while (acc > 1) {
      acc -= 1;
      emit(state, false);
    }

    burstTimer -= dt;
    if (burstTimer < 0) {
      burstTimer = 2.2 + rand() * 2.3;
      for (let i = 0; i < 18; i++) emit(state, true);
    }

    for (let i = 0; i < count; i++) {
      const d = data[i];
      d.age += dt;
      if (d.age > d.life) {
        alphas[i] = 0;
        sizes[i] = 0.001;
        positions[i * 3 + 1] = -100;
        continue;
      }
      d.vy -= 7.4 * dt;
      d.x += d.vx * dt;
      d.y += d.vy * dt;
      d.z += d.vz * dt;
      const u = d.age / d.life;
      const water = waveHeight(d.x, d.z, t);
      if (d.y < water && d.vy < 0) {
        alphas[i] = 0;
        d.age = d.life + 0.1;
        positions[i * 3 + 1] = -100;
        continue;
      }
      positions[i * 3] = d.x;
      positions[i * 3 + 1] = d.y;
      positions[i * 3 + 2] = d.z;
      sizes[i] = d.size * (0.7 + u * 1.6);
      alphas[i] = (1 - u) * (1 - u) * 0.85;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.aSize.needsUpdate = true;
    geo.attributes.aAlpha.needsUpdate = true;
  }

  function setPixelScale(v) {
    mat.uniforms.uPixelScale.value = v;
  }

  return { points, update, setPixelScale };
}

function createWake(scene, count = 54) {
  const positions = new Float32Array(count * 2 * 3);
  const uvs = new Float32Array(count * 2 * 2);
  const indices = [];
  for (let i = 0; i < count; i++) {
    uvs[i * 4 + 0] = 0;
    uvs[i * 4 + 1] = i / (count - 1);
    uvs[i * 4 + 2] = 1;
    uvs[i * 4 + 3] = i / (count - 1);
    if (i < count - 1) {
      const a = i * 2;
      const b = a + 1;
      const c = a + 2;
      const d = a + 3;
      indices.push(a, c, b, b, c, d);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  geo.setIndex(indices);

  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: makeFoamTile() },
      uTime: { value: 0 },
      uOpacity: { value: 0.7 },
    },
    vertexShader: /* glsl */ `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap;
      uniform float uTime;
      uniform float uOpacity;
      varying vec2 vUv;
      void main() {
        vec2 uv = vec2(vUv.x * 1.6 + 0.15, vUv.y * 7.0 + uTime * 0.09);
        float a = texture2D(uMap, uv).a;
        float fade = pow(max(0.0, 1.0 - vUv.y), 1.55);
        fade *= smoothstep(0.0, 0.06, vUv.y);
        float edge = smoothstep(0.0, 0.18, vUv.x) * (1.0 - smoothstep(0.82, 1.0, vUv.x));
        a *= fade * edge * uOpacity;
        if (a < 0.004) discard;
        gl_FragColor = vec4(vec3(1.0, 0.98, 0.94), a * 0.85);
      }
    `,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = 2;
  scene.add(mesh);

  const history = [];
  for (let i = 0; i < count; i++) {
    history.push({ x: 0, z: 0, rightX: 0, rightZ: 1 });
  }
  let acc = 0;

  function update(t, dt, state) {
    mat.uniforms.uTime.value = t;
    acc += dt;
    const interval = 1 / 24;
    while (acc >= interval) {
      acc -= interval;
      history.pop();
      history.unshift({
        x: state.position.x - state.forward.x * 1.55,
        z: state.position.z - state.forward.z * 1.55,
        rightX: state.right.x,
        rightZ: state.right.z,
      });
    }

    for (let i = 0; i < count; i++) {
      const h = history[i];
      const v = i / (count - 1);
      const w = 0.55 + v * 2.0;
      const y = waveHeight(h.x, h.z, t) + 0.06;
      const idx = i * 6;
      positions[idx + 0] = h.x - h.rightX * w;
      positions[idx + 1] = y;
      positions[idx + 2] = h.z - h.rightZ * w;
      positions[idx + 3] = h.x + h.rightX * w;
      positions[idx + 4] = y;
      positions[idx + 5] = h.z + h.rightZ * w;
    }
    geo.attributes.position.needsUpdate = true;
    mesh.position.set(0, 0, 0);
  }

  return { mesh, update };
}

export function createParticles(scene, boardGroup) {
  const rand = rng(74);
  const foam = createFoamParticles();
  const spray = createSpray();
  const wake = createWake(scene);
  scene.add(foam.points);
  scene.add(spray.points);

  const haloMat = new THREE.MeshBasicMaterial({
    map: makeBoardFoam(),
    transparent: true,
    opacity: 0.55,
    depthWrite: false,
    color: new THREE.Color('#ffffff'),
    blending: THREE.NormalBlending,
  });
  const haloGroup = new THREE.Group();
  const halo = new THREE.Mesh(new THREE.PlaneGeometry(5.6, 2.3), haloMat);
  halo.rotation.x = -Math.PI / 2;
  halo.position.set(-0.8, 0.045, 0);
  halo.renderOrder = 2;
  haloGroup.add(halo);
  haloGroup.rotation.y = 0;
  scene.add(haloGroup);

  const state = {
    position: new THREE.Vector3(),
    forward: new THREE.Vector3(1, 0, 0),
    right: new THREE.Vector3(0, 0, 1),
    time: 0,
  };

  function setPixelScale(camera, renderer) {
    const size = renderer.getDrawingBufferSize(new THREE.Vector2());
    const scale = size.y / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2));
    foam.setPixelScale(scale);
    spray.setPixelScale(scale);
  }

  function update(t, dt, board) {
    state.time = t;
    state.position.copy(board.position);
    state.forward.copy(board.forward);
    state.right.copy(board.right);

    foam.update(t, dt, state);
    spray.update(t, dt, state);
    wake.update(t, dt, state);

    haloGroup.position.set(
      board.position.x,
      waveHeight(board.position.x, board.position.z, t) + 0.06,
      board.position.z,
    );
    haloGroup.rotation.y = board.yaw;
    haloMat.opacity = 0.48 + Math.sin(t * 1.8) * 0.06;
    // break up the halo with a tiny drift
    halo.position.z = Math.sin(t * 0.7) * 0.06;

    void boardGroup;
    void rand;
  }

  return { update, setPixelScale };
}
