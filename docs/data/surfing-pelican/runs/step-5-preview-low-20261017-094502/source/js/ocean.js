// The ocean: an endless "projected" polar grid that follows the surfer, so the
// mesh stays dense where the camera is and stretches out to the horizon.
// Displacement happens in the vertex shader; normals, foam and sun glitter are
// evaluated per pixel from the same wave function the surfer rides on.

import * as THREE from 'three';
import { WAVE_GLSL } from './waves.js';
import { PALETTE, SUN_DIR, FOG_DENSITY } from './palette.js';

const NEAR_STEP = 0.5; // spacing of the innermost rings
const NEAR_RINGS = 80; // ... up to r = 40
const RINGS = 240; // total ring count
const SEGMENTS = 192; // quads around the circle
const OUTER_RADIUS = 6000;

function buildWaterGeometry() {
  const positions = [];
  const uvs = [];
  const normals = [];
  const indices = [];

  const radii = [];
  for (let i = 1; i <= NEAR_RINGS; i++) radii.push(i * NEAR_STEP);
  const growth = Math.pow(
    OUTER_RADIUS / (NEAR_RINGS * NEAR_STEP),
    1 / (RINGS - NEAR_RINGS),
  );
  let r = NEAR_RINGS * NEAR_STEP;
  for (let i = NEAR_RINGS; i < RINGS; i++) {
    r *= growth;
    radii.push(r);
  }

  // centre vertex
  positions.push(0, 0, 0);
  normals.push(0, 1, 0);
  uvs.push(0.5, 0.5);

  const ringBase = [];
  let next = 1;
  for (let i = 0; i < radii.length; i++) {
    ringBase.push(next);
    const rad = radii[i];
    for (let j = 0; j < SEGMENTS; j++) {
      const a = (j / SEGMENTS) * Math.PI * 2;
      positions.push(Math.cos(a) * rad, 0, Math.sin(a) * rad);
      normals.push(0, 1, 0);
      uvs.push(0.5 + Math.cos(a) * 0.5, 0.5 + Math.sin(a) * 0.5);
    }
    next += SEGMENTS;
  }

  const quads = SEGMENTS;
  // fan from the single centre vertex
  for (let j = 0; j < quads; j++) {
    indices.push(0, ringBase[0] + ((j + 1) % quads), ringBase[0] + j);
  }
  for (let i = 0; i < ringBase.length - 1; i++) {
    const a = ringBase[i];
    const b = ringBase[i + 1];
    for (let j = 0; j < quads; j++) {
      const j2 = (j + 1) % quads;
      indices.push(a + j, a + j2, b + j2);
      indices.push(a + j, b + j2, b + j);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setIndex(indices);
  geo.computeBoundingSphere();
  return geo;
}

const vertexShader = /* glsl */ `
uniform float uTime;
varying vec3 vWorld;

${WAVE_GLSL}

void main() {
  vec4 wp = modelMatrix * vec4( position, 1.0 );
  wp.y += waveAt( wp.xz, uTime );
  vWorld = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
precision highp float;

uniform float uTime;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uSkyTop;
uniform vec3 uHorizon;
uniform vec3 uDeep;
uniform vec3 uShallow;
uniform vec3 uFoam;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform vec2 uRider;
uniform vec2 uRiderFwd;
uniform float uSparkle;

varying vec3 vWorld;

${WAVE_GLSL}

float hash21( vec2 p ) {
  p = fract( p * vec2( 123.34, 456.21 ) );
  p += dot( p, p + 45.32 );
  return fract( p.x * p.y );
}

float vnoise( vec2 p ) {
  vec2 i = floor( p );
  vec2 f = fract( p );
  f = f * f * ( 3.0 - 2.0 * f );
  const float o = 110.0;
  float a = hash21( i );
  float b = hash21( i + vec2( o, 0.0 ) );
  float c = hash21( i + vec2( 0.0, o ) );
  float d = hash21( i + vec2( o, o ) );
  return mix( mix( a, b, f.x ), mix( c, d, f.x ), f.y );
}

float fbm( vec2 p ) {
  float v = 0.0;
  float a = 0.5;
  for ( int i = 0; i < 4; i ++ ) {
    v += a * vnoise( p );
    p *= 2.03;
    a *= 0.5;
  }
  return v;
}

void main() {
  vec2 p = vWorld.xz;
  float t = uTime;

  float h = waveAt( p, t );

  // per-pixel normal by finite differences (same eps as the CPU version)
  float e = 0.5;
  float hx = ( waveAt( p + vec2( e, 0.0 ), t ) - waveAt( p - vec2( e, 0.0 ), t ) ) / ( 2.0 * e );
  float hz = ( waveAt( p + vec2( 0.0, e ), t ) - waveAt( p - vec2( 0.0, e ), t ) ) / ( 2.0 * e );
  vec3 n = normalize( vec3( -hx, 1.0, -hz ) );

  vec3 view = normalize( cameraPosition - vWorld );
  float ndv = clamp( dot( n, view ), 0.0, 1.0 );

  // --- body colour: deep in the troughs, bright and translucent on the faces
  float hn = smoothstep( -0.95, 1.0, h );
  vec3 col = mix( uDeep, uShallow, hn );
  // a touch of sky ambient so the foreground never goes flat black
  // (linear space: 0.035 is already a soft lift, it is NOT an sRGB value)
  col += mix( uHorizon, uSkyTop, 0.35 ) * 0.05;

  // light bleeding through the wave faces
  float sss = pow( clamp( h, 0.0, 1.4 ) / 1.4, 2.0 ) * pow( ndv, 1.5 );
  col += uSunColor * sss * 0.30;

  // --- sky reflection (fresnel)
  float fres = 0.025 + 0.975 * pow( 1.0 - ndv, 5.0 );
  vec3 rdir = reflect( -view, n );
  rdir.y = abs( rdir.y );
  vec3 sky = mix( uHorizon, uSkyTop, smoothstep( 0.0, 0.45, rdir.y ) );
  col = mix( col, sky, clamp( fres, 0.0, 1.0 ) );

  // --- sun glitter
  vec3 hv = normalize( uSunDir + view );
  float nh = max( dot( n, hv ), 0.0 );
  float broad = pow( nh, 60.0 ) * 0.16;
  float sharp = pow( nh, 460.0 ) * 1.25 * uSparkle;
  col += uSunColor * ( broad + sharp );

  // --- whitecaps on the steep, high parts of the swell
  float slope = 1.0 - n.y;
  float crest = smoothstep( 0.72, 1.4, h );
  float steep = smoothstep( 0.075, 0.19, slope );
  float mottle = fbm( p * 0.42 + vec2( t * 0.25, t * 0.05 ) );
  float foam = crest * steep * smoothstep( 0.53, 0.8, mottle );

  // --- disturbed water in the board's wake (an ellipse along the travel dir)
  vec2 d = p - uRider;
  float along = dot( d, uRiderFwd );
  vec2 perp = vec2( -uRiderFwd.y, uRiderFwd.x );
  float across = dot( d, perp );
  float wr = length( vec2( across * 1.5, along * 0.6 ) );
  float wake = smoothstep( 3.4, 0.0, wr ) * ( 0.10 + 0.30 * smoothstep( 0.4, 0.9, h ) );

  col = mix( col, uFoam, clamp( foam * 0.95 + wake * 0.5, 0.0, 1.0 ) );

  // --- haze
  float dist = length( cameraPosition - vWorld );
  float fk = uFogDensity * dist;
  float f = 1.0 - exp( -fk * fk );
  col = mix( col, uFogColor, clamp( f, 0.0, 1.0 ) );

  gl_FragColor = vec4( col, 1.0 );
  gl_FragColor = linearToOutputTexel( gl_FragColor );
}
`;

const lin = (hex) => new THREE.Color(hex).convertSRGBToLinear();

export function createOcean(scene) {
  const geometry = buildWaterGeometry();

  const uniforms = {
    uTime: { value: 0 },
    uSunDir: { value: new THREE.Vector3(SUN_DIR.x, SUN_DIR.y, SUN_DIR.z).normalize() },
    uSunColor: { value: lin(PALETTE.sun) },
    uSkyTop: { value: lin(PALETTE.skyTop) },
    uHorizon: { value: lin(PALETTE.skyHorizon) },
    uDeep: { value: lin(PALETTE.deep) },
    uShallow: { value: lin(PALETTE.shallow) },
    uFoam: { value: lin(PALETTE.foam) },
    uFogColor: { value: lin(PALETTE.haze) },
    uFogDensity: { value: FOG_DENSITY },
    uRider: { value: new THREE.Vector2() },
    uRiderFwd: { value: new THREE.Vector2(0, 1) },
    uSparkle: { value: 1 },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    side: THREE.DoubleSide,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'ocean';
  mesh.frustumCulled = false;
  mesh.renderOrder = 1;
  scene.add(mesh);

  return { mesh, uniforms };
}
