/**
 * The animated ocean: a large plane displaced by the shared wave field,
 * shaded with a stylised water model (fresnel sky reflection, sun glitter,
 * crest foam and a haze fade into the horizon).
 */
import * as THREE from "three";
import { waveGLSL, TOTAL_AMPLITUDE } from "./waves.js";

const OCEAN_SIZE = 280;
const OCEAN_SEGMENTS = 264;

const vertexShader = /* glsl */ `
uniform float uTime;

varying vec3 vWorldPos;
varying vec3 vNormal;

${waveGLSL()}

void main() {
  vec4 worldPos = modelMatrix * vec4( position, 1.0 );
  float h = waveHeight( worldPos.xz, uTime );
  worldPos.y += h;

  vWorldPos = worldPos.xyz;
  vNormal = waveNormal( worldPos.xz, uTime );

  gl_Position = projectionMatrix * viewMatrix * worldPos;
}
`;

const fragmentShader = /* glsl */ `
uniform float uTime;
uniform vec3 uSunDirection;
uniform float uTotalAmplitude;

varying vec3 vWorldPos;
varying vec3 vNormal;

float hash( vec2 p ) {
  return fract( sin( dot( p, vec2( 127.1, 311.7 ) ) ) * 43758.5453123 );
}

float noise( vec2 p ) {
  vec2 i = floor( p );
  vec2 f = fract( p );
  vec2 u = f * f * ( 3.0 - 2.0 * f );
  return mix(
    mix( hash( i ), hash( i + vec2( 1.0, 0.0 ) ), u.x ),
    mix( hash( i + vec2( 0.0, 1.0 ) ), hash( i + vec2( 1.0, 1.0 ) ), u.x ),
    u.y
  );
}

void main() {
  vec3 viewDir = normalize( cameraPosition - vWorldPos );
  vec3 sunDir = normalize( uSunDirection );

  // --- fine ripple detail on top of the big swells -------------------------
  vec2 rp = vWorldPos.xz * 1.35 + vec2( uTime * 0.32, -uTime * 0.19 );
  float n0 = noise( rp );
  float nx = noise( rp + vec2( 0.17, 0.0 ) );
  float nz = noise( rp + vec2( 0.0, 0.17 ) );
  vec3 normal = normalize( vNormal + vec3( ( n0 - nx ) * 1.35, 0.0, ( n0 - nz ) * 1.35 ) );

  // --- water body colour ---------------------------------------------------
  float depthMix = clamp( vWorldPos.y / uTotalAmplitude * 0.5 + 0.55, 0.0, 1.0 );
  vec3 water = mix( vec3( 0.027, 0.180, 0.322 ), vec3( 0.098, 0.451, 0.608 ), depthMix );

  // --- sky reflection through fresnel -------------------------------------
  float fresnel = pow( 1.0 - clamp( dot( normal, viewDir ), 0.0, 1.0 ), 4.0 );
  fresnel = mix( 0.055, 1.0, fresnel );
  vec3 skyRef = mix( vec3( 0.639, 0.788, 0.878 ), vec3( 0.235, 0.494, 0.780 ), clamp( normal.y * 1.25, 0.0, 1.0 ) );
  vec3 color = mix( water, skyRef, fresnel );

  // --- sun glitter ---------------------------------------------------------
  vec3 halfVec = normalize( sunDir + viewDir );
  float ndh = max( dot( normal, halfVec ), 0.0 );
  float sparkle = noise( vWorldPos.xz * 6.0 + vec2( uTime * 1.1, uTime * 0.7 ) );
  color += vec3( 1.0, 0.925, 0.780 ) * pow( ndh, 320.0 ) * 3.2;
  color += vec3( 1.0, 0.902, 0.706 ) * pow( ndh, 34.0 ) * ( 0.10 + sparkle * 0.22 );

  // --- foam on the crests --------------------------------------------------
  float crest = smoothstep( 0.30, 1.05, vWorldPos.y / uTotalAmplitude );
  float foamTex = noise( vWorldPos.xz * 2.35 + vec2( uTime * 0.45, uTime * 0.32 ) ) * 0.65
                + noise( vWorldPos.xz * 5.5 - vec2( uTime * 0.3, uTime * 0.42 ) ) * 0.35;
  float foam = smoothstep( 0.32, 0.86, crest * ( 0.45 + foamTex * 1.05 ) );
  float streak = smoothstep( 0.55, 1.0, noise( vWorldPos.xz * vec2( 1.4, 7.0 ) + vec2( uTime * 0.5, 0.0 ) ) ) * crest;
  foam = clamp( foam * 0.9 + streak * 0.28, 0.0, 1.0 );
  color = mix( color, vec3( 0.925, 0.965, 0.984 ), foam * 0.88 );

  // --- haze toward the horizon -------------------------------------------
  float dist = length( cameraPosition - vWorldPos );
  color = mix( color, vec3( 0.788, 0.886, 0.937 ), smoothstep( 48.0, 132.0, dist ) );

  gl_FragColor = vec4( color, 1.0 );
}
`;

export function createOcean(scene, sunDirection) {
  const geometry = new THREE.PlaneGeometry(OCEAN_SIZE, OCEAN_SIZE, OCEAN_SEGMENTS, OCEAN_SEGMENTS);
  geometry.rotateX(-Math.PI / 2);

  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uSunDirection: { value: sunDirection.clone() },
      uTotalAmplitude: { value: TOTAL_AMPLITUDE },
    },
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  scene.add(mesh);

  return {
    mesh,
    update(t) {
      material.uniforms.uTime.value = t;
    },
  };
}