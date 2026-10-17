// Sky dome, sun and drifting clouds. The dome is parented to the camera so it
// is always infinitely far away.

import * as THREE from 'three';
import { PALETTE, SUN_DIR } from './palette.js';

const vertexShader = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = normalize( position );
  gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}
`;

const fragmentShader = /* glsl */ `
precision highp float;

uniform vec3 uSunDirView;
uniform vec3 uSunColor;
uniform vec3 uTop;
uniform vec3 uMid;
uniform vec3 uHorizon;
uniform vec3 uCloud;
uniform vec3 uCloudShade;
uniform float uTime;

varying vec3 vDir;

float hash31( vec3 p ) {
  p = fract( p * 0.3183099 + vec3( 0.71, 0.113, 0.419 ) );
  p *= 17.0;
  return fract( p.x * p.y * p.z * ( p.x + p.y + p.z ) );
}

float vnoise( vec3 x ) {
  vec3 i = floor( x );
  vec3 f = fract( x );
  f = f * f * ( 3.0 - 2.0 * f );
  return mix(
    mix( mix( hash31( i + vec3( 0.0, 0.0, 0.0 ) ), hash31( i + vec3( 1.0, 0.0, 0.0 ) ), f.x ),
         mix( hash31( i + vec3( 0.0, 1.0, 0.0 ) ), hash31( i + vec3( 1.0, 1.0, 0.0 ) ), f.x ), f.y ),
    mix( mix( hash31( i + vec3( 0.0, 0.0, 1.0 ) ), hash31( i + vec3( 1.0, 0.0, 1.0 ) ), f.x ),
         mix( hash31( i + vec3( 0.0, 1.0, 1.0 ) ), hash31( i + vec3( 1.0, 1.0, 1.0 ) ), f.x ), f.y ),
    f.z );
}

float fbm( vec3 p ) {
  float v = 0.0;
  float a = 0.5;
  for ( int i = 0; i < 5; i ++ ) {
    v += a * vnoise( p );
    p *= 2.07;
    a *= 0.5;
  }
  return v;
}

void main() {
  vec3 d = normalize( vDir );
  vec3 sun = normalize( uSunDirView );

  float y = clamp( d.y, -1.0, 1.0 );

  // vertical gradient
  vec3 col = mix( uHorizon, uMid, smoothstep( 0.0, 0.30, y ) );
  col = mix( col, uTop, smoothstep( 0.26, 0.85, y ) );
  // a little extra haze below the true horizon (hidden by the sea anyway)
  col = mix( col, uHorizon * 0.86, smoothstep( 0.0, -0.14, y ) );

  // --- sun: disc + wide glow
  float a = acos( clamp( dot( d, sun ), -1.0, 1.0 ) );
  float disc = smoothstep( 0.0165, 0.0115, a );
  float glow = exp( -a * 5.0 ) * 0.55 + exp( -a * 22.0 ) * 0.6;
  col += uSunColor * ( disc * 2.2 + glow );

  // --- clouds
  vec3 cp = d * 2.6 + vec3( uTime * 0.011, uTime * 0.004, uTime * 0.007 );
  float c = fbm( cp );
  float cover = smoothstep( 0.58, 0.86, c ) * 0.85;
  // keep the horizon band clear so the sun path stays visible
  float band = smoothstep( 0.015, 0.22, y ) * ( 1.0 - smoothstep( 0.45, 0.95, y ) * 0.45 );
  cover *= band;
  float shade = smoothstep( 0.55, 0.80, fbm( cp * 2.1 + 3.7 ) );
  vec3 cloudCol = mix( uCloud, uCloudShade, shade );
  // warm the clouds that sit near the sun
  cloudCol = mix( cloudCol, uSunColor * 1.15, exp( -a * 1.6 ) * 0.55 * band );
  col = mix( col, cloudCol, cover * 0.92 );

  gl_FragColor = vec4( col, 1.0 );
  gl_FragColor = linearToOutputTexel( gl_FragColor );
}
`;

const lin = (hex) => new THREE.Color(hex).convertSRGBToLinear();

export function createSky(camera) {
  const geometry = new THREE.SphereGeometry(15000, 48, 32);
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uSunDirView: { value: new THREE.Vector3(0, 1, 0) },
      uSunColor: { value: lin(PALETTE.sun) },
      uTop: { value: lin(PALETTE.skyTop) },
      uMid: { value: lin(PALETTE.skyMid) },
      uHorizon: { value: lin(PALETTE.skyHorizon) },
      uCloud: { value: lin(PALETTE.cloud) },
      uCloudShade: { value: lin(PALETTE.cloudShade) },
      uTime: { value: 0 },
    },
    vertexShader,
    fragmentShader,
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'dome';
  mesh.renderOrder = -1;
  mesh.frustumCulled = false;
  camera.add(mesh);

  const sunDir = new THREE.Vector3(SUN_DIR.x, SUN_DIR.y, SUN_DIR.z).normalize();

  return {
    mesh,
    update(t) {
      material.uniforms.uTime.value = t;
      // sun direction in view space (the dome is centred on the camera)
      material.uniforms.uSunDirView.value.copy(sunDir).transformDirection(camera.matrixWorldInverse);
    },
  };
}
