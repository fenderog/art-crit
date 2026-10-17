import * as THREE from 'three';
import { createWaveNormalTexture, createWaveFoamTexture } from './textures.js';

/**
 * Procedural 2D profile of the curling wave cross-section
 * u in [0, 1]: 0 = deep water behind wave, ~0.65 = crest, ~0.82 = lip curl, 1.0 = ocean flats
 */
export function getWaveProfile(u) {
  let x, y;
  if (u < 0.20) {
    const t = u / 0.20;
    x = -32 + t * 22;
    y = 0.25 * Math.sin(t * Math.PI * 0.5);
  } else if (u < 0.65) {
    const t = (u - 0.20) / (0.65 - 0.20);
    // Smooth concave rising wave face
    x = -10 + t * 14.5;
    y = 0.25 + 6.75 * Math.pow(t, 1.65);
  } else if (u < 0.82) {
    const t = (u - 0.65) / (0.82 - 0.65);
    // Curling barrel lip arching forward and down
    const angle = t * Math.PI * 0.95;
    const rx = 2.45;
    const ry = 2.25;
    x = 4.5 + rx * Math.sin(angle);
    y = 7.0 + ry * (Math.cos(angle) - 1.0);
  } else if (u < 0.90) {
    const t = (u - 0.82) / (0.90 - 0.82);
    // Waterfall impact curtain plunging into the trough
    const startX = 4.5 + 2.45 * Math.sin(Math.PI * 0.95);
    const startY = 7.0 + 2.25 * (Math.cos(Math.PI * 0.95) - 1.0);
    x = startX - t * 1.6;
    y = startY - t * (startY - 0.08);
  } else {
    const t = (u - 0.90) / (1.0 - 0.90);
    // Ocean flats extending toward horizon
    x = 3.8 + t * 34.0;
    y = 0.08 * Math.sin(t * Math.PI * 4.0);
  }
  return { x, y };
}

/**
 * Exact analytical 3D position on the wave surface
 * @param {number} z coordinate along wave length (-40 to +40)
 * @param {number} u cross section coordinate (0 to 1)
 * @param {number} time animation time
 */
export function getWavePoint(z, u, time = 0) {
  // Peeling wave effect: wave breaks slightly earlier at lower Z
  const peel = z * 0.055;
  const effU = Math.max(0.001, Math.min(0.999, u - peel * 0.035));
  const base = getWaveProfile(effU);

  // Dynamic rolling ocean swell modulation
  const swell1 = Math.sin(z * 0.22 - time * 1.5) * 0.22;
  const swell2 = Math.cos(base.x * 0.35 + z * 0.18 - time * 2.1) * 0.12;
  const xMod = Math.sin(z * 0.12) * 0.45;

  return new THREE.Vector3(
    base.x + xMod,
    base.y + swell1 + swell2,
    z
  );
}

/**
 * Evaluates the wave surface state (position, normal, tangent, barrel status) for a surfboard
 */
export function getWaveState(z, facePos, time = 0) {
  // Map facePos (0 = base trough, 0.5 = pocket, 1.0 = lip crest) to u parameter
  const u = 0.28 + facePos * 0.44; // u in [0.28, 0.72]

  const p = getWavePoint(z, u, time);

  // Central difference calculation for accurate surface normal
  const du = 0.005;
  const dz = 0.05;
  const pU1 = getWavePoint(z, u + du, time);
  const pU0 = getWavePoint(z, u - du, time);
  const pZ1 = getWavePoint(z + dz, u, time);
  const pZ0 = getWavePoint(z - dz, u, time);

  const dU = new THREE.Vector3().subVectors(pU1, pU0).normalize();
  const dZ = new THREE.Vector3().subVectors(pZ1, pZ0).normalize();

  // Outward facing surface normal: dZ x dU
  const normal = new THREE.Vector3().crossVectors(dZ, dU).normalize();

  // Tangent along the wave face (up/down)
  const tangent = dU.clone();

  // Check if tucked under the lip / in the barrel
  const inBarrel = facePos > 0.68 && facePos < 0.92 && p.x > 3.0;

  return {
    position: p,
    normal: normal,
    tangent: tangent,
    alongWave: dZ,
    inBarrel: inBarrel,
    steepness: Math.abs(dU.y)
  };
}

export class WaveSystem {
  constructor(scene) {
    this.scene = scene;
    this.time = 0;

    this.normalTexture = createWaveNormalTexture();
    this.foamTexture = createWaveFoamTexture();

    this.buildWaveMesh();
    this.buildWhitewater();
    this.buildLipFoam();
  }

  buildWaveMesh() {
    const uSegments = 100;
    const zSegments = 140;
    const geometry = new THREE.BufferGeometry();

    const positions = [];
    const uvs = [];
    const indices = [];

    const zMin = -45;
    const zMax = 45;

    for (let j = 0; j <= zSegments; j++) {
      const v = j / zSegments;
      const z = zMin + v * (zMax - zMin);

      for (let i = 0; i <= uSegments; i++) {
        const u = i / uSegments;
        const pt = getWavePoint(z, u, 0);

        positions.push(pt.x, pt.y, pt.z);
        uvs.push(u * 3.0, v * 8.0);
      }
    }

    for (let j = 0; j < zSegments; j++) {
      for (let i = 0; i < uSegments; i++) {
        const a = j * (uSegments + 1) + i;
        const b = (j + 1) * (uSegments + 1) + i;
        const c = (j + 1) * (uSegments + 1) + (i + 1);
        const d = j * (uSegments + 1) + (i + 1);

        indices.push(a, b, d);
        indices.push(b, c, d);
      }
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    // Material with subsurface scattering look and clearcoat gloss
    this.waveMaterial = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(0x007799),
      roughness: 0.1,
      metalness: 0.05,
      clearcoat: 1.0,
      clearcoatRoughness: 0.06,
      transmission: 0.35,
      ior: 1.333,
      normalMap: this.normalTexture,
      normalScale: new THREE.Vector2(0.85, 0.85),
      side: THREE.DoubleSide
    });

    // Custom shader tweak for backlit wave glow and crest foam
    this.waveMaterial.onBeforeCompile = (shader) => {
      shader.uniforms.uTime = { value: 0 };
      shader.uniforms.tFoam = { value: this.foamTexture };

      shader.vertexShader = `
        varying vec3 vWorldPos;
        varying vec3 vWorldNorm;
        ${shader.vertexShader}
      `;
      shader.vertexShader = shader.vertexShader.replace(
        '#include <worldpos_vertex>',
        `
        #include <worldpos_vertex>
        vWorldPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
        vWorldNorm = normalize((modelMatrix * vec4(normal, 0.0)).xyz);
        `
      );

      shader.fragmentShader = `
        uniform float uTime;
        uniform sampler2D tFoam;
        varying vec3 vWorldPos;
        varying vec3 vWorldNorm;
        ${shader.fragmentShader}
      `;

      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <dithering_fragment>',
        `
        #include <dithering_fragment>

        // Wave crest & lip foam highlight
        float crestFactor = smoothstep(5.5, 7.2, vWorldPos.y);
        vec2 foamUv = vWorldPos.xz * 0.15 + vec2(uTime * 0.05, uTime * 0.02);
        vec4 foamTex = texture2D(tFoam, foamUv);
        float foamIntensity = crestFactor * foamTex.a * 0.85;

        // Subsurface backlit glow: wave lip glows emerald turquoise when sun shines through
        vec3 sunDir = normalize(vec3(-0.4, 0.6, 0.7));
        float backlit = pow(max(0.0, dot(reflect(-sunDir, vWorldNorm), vec3(0.0, 0.0, 1.0))), 2.0);
        float thinLip = smoothstep(4.0, 7.0, vWorldPos.y) * 0.45;
        vec3 subsurfaceColor = vec3(0.05, 0.95, 0.85) * backlit * thinLip;

        gl_FragColor.rgb += subsurfaceColor;
        gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.96, 0.99, 1.0), foamIntensity);
        `
      );
      this.shader = shader;
    };

    this.mesh = new THREE.Mesh(geometry, this.waveMaterial);
    this.mesh.receiveShadow = true;
    this.scene.add(this.mesh);

    // Save initial vertex positions for dynamic ripple animation
    this.basePositions = Float32Array.from(positions);
    this.uSegments = uSegments;
    this.zSegments = zSegments;
    this.zMin = zMin;
    this.zMax = zMax;
  }

  buildWhitewater() {
    // Foamy impact strip along the trough where the lip crashes
    const planeGeo = new THREE.PlaneGeometry(12, 90, 24, 60);
    const foamMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.4,
      metalness: 0.1,
      map: this.foamTexture,
      transparent: true,
      opacity: 0.82,
      depthWrite: false,
      side: THREE.DoubleSide
    });

    this.whitewater = new THREE.Mesh(planeGeo, foamMat);
    this.whitewater.rotation.x = -Math.PI / 2;
    this.whitewater.position.set(4.2, 0.12, 0);
    this.scene.add(this.whitewater);
  }

  buildLipFoam() {
    // Glowing frothy ribbon along the curling lip crest
    const curvePoints = [];
    for (let z = -45; z <= 45; z += 3) {
      const p = getWavePoint(z, 0.76, 0);
      curvePoints.push(new THREE.Vector3(p.x, p.y + 0.05, p.z));
    }
    const curve = new THREE.CatmullRomCurve3(curvePoints);
    const tubeGeo = new THREE.TubeGeometry(curve, 64, 0.35, 8, false);

    const tubeMat = new THREE.MeshStandardMaterial({
      color: 0xf0f9ff,
      roughness: 0.3,
      metalness: 0.1,
      transparent: true,
      opacity: 0.75,
      map: this.foamTexture
    });

    this.lipFoam = new THREE.Mesh(tubeGeo, tubeMat);
    this.scene.add(this.lipFoam);
  }

  update(time, dt) {
    this.time = time;

    // Scroll normal map for animated caustic ripples
    if (this.normalTexture) {
      this.normalTexture.offset.x = (time * 0.08) % 1;
      this.normalTexture.offset.y = (time * 0.04) % 1;
    }

    if (this.foamTexture) {
      this.foamTexture.offset.y = (time * 0.05) % 1;
    }

    if (this.shader) {
      this.shader.uniforms.uTime.value = time;
    }

    // Dynamic wave swell vertex animation
    const posAttr = this.mesh.geometry.attributes.position;
    const array = posAttr.array;
    let idx = 0;

    for (let j = 0; j <= this.zSegments; j++) {
      const v = j / this.zSegments;
      const z = this.zMin + v * (this.zMax - this.zMin);

      for (let i = 0; i <= this.uSegments; i++) {
        const u = i / this.uSegments;
        const pt = getWavePoint(z, u, time);

        array[idx] = pt.x;
        array[idx + 1] = pt.y;
        array[idx + 2] = pt.z;
        idx += 3;
      }
    }

    posAttr.needsUpdate = true;
    this.mesh.geometry.computeVertexNormals();

    // Subtle whitewater undulating motion
    if (this.whitewater) {
      this.whitewater.position.y = 0.12 + Math.sin(time * 3.0) * 0.04;
      this.whitewater.material.map.offset.y = (time * 0.2) % 1;
    }
  }
}
