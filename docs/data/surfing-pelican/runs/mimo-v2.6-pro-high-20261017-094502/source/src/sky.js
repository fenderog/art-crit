/**
 * Sky dome with sun glow, drifting stylised clouds and distant seabirds.
 */
import * as THREE from "three";

const vertexShader = /* glsl */ `
varying vec3 vDirection;

void main() {
  vDirection = normalize( position );
  gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}
`;

const fragmentShader = /* glsl */ `
uniform vec3 uSunDirection;
varying vec3 vDirection;

void main() {
  vec3 dir = normalize( vDirection );
  float h = clamp( dir.y * 1.12 + 0.055, 0.0, 1.0 );

  // deep blue overhead fading to a pale, warm haze at the horizon
  vec3 color = mix( vec3( 0.843, 0.918, 0.965 ), vec3( 0.129, 0.396, 0.729 ), pow( h, 0.70 ) );

  float sunDot = max( dot( dir, normalize( uSunDirection ) ), 0.0 );
  color += vec3( 1.0, 0.851, 0.596 ) * pow( sunDot, 6.0 ) * 0.30;
  color += vec3( 1.0, 0.949, 0.812 ) * pow( sunDot, 160.0 ) * 0.85;
  color += vec3( 1.0, 0.988, 0.933 ) * smoothstep( 0.9992, 0.9998, sunDot ) * 2.2;

  // haze band exactly where the ocean meets the sky
  color = mix( color, vec3( 0.788, 0.886, 0.937 ), smoothstep( 0.155, 0.0, abs( dir.y ) ) );

  gl_FragColor = vec4( color, 1.0 );
}
`;

function createCloud(material) {
  const group = new THREE.Group();
  const puffs = 6 + Math.floor(Math.random() * 4);
  for (let i = 0; i < puffs; i++) {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), material);
    puff.position.set(
      (Math.random() - 0.5) * 13.5,
      (Math.random() - 0.5) * 2.6,
      (Math.random() - 0.5) * 5.5
    );
    const s = 3.0 + Math.random() * 3.6;
    puff.scale.set(s * (1.15 + Math.random() * 0.6), s * 0.52, s);
    group.add(puff);
  }
  return group;
}

function createBird(material) {
  const bird = new THREE.Group();
  const wingGeo = new THREE.PlaneGeometry(2.1, 0.62, 3, 1);
  const positions = wingGeo.attributes.position;
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    positions.setZ(i, Math.abs(x) * 0.34); // gentle dihedral curve
    positions.setY(i, positions.getY(i) * (1.0 - Math.abs(x) * 0.22));
  }
  wingGeo.computeVertexNormals();

  const left = new THREE.Mesh(wingGeo, material);
  left.position.x = -1.02;
  const right = new THREE.Mesh(wingGeo, material);
  right.position.x = 1.02;
  right.scale.x = -1;

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), material);
  body.scale.set(1, 0.8, 1.9);

  bird.add(left, right, body);
  bird.userData.wings = [left, right];
  return bird;
}

export function createSky(scene, sunDirection) {
  const domeMaterial = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: { uSunDirection: { value: sunDirection.clone() } },
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(430, 32, 20), domeMaterial);
  dome.frustumCulled = false;
  dome.renderOrder = -1;
  scene.add(dome);

  // ---- clouds -------------------------------------------------------------
  const cloudMaterial = new THREE.MeshLambertMaterial({
    color: 0xdfeaf6,
    emissive: 0xc9dff2,
    emissiveIntensity: 0.9,
    transparent: true,
    opacity: 0.88,
    depthWrite: true,
  });
  const clouds = [];
  for (let i = 0; i < 10; i++) {
    const cloud = createCloud(cloudMaterial);
    const angle = (i / 10) * Math.PI * 2 + Math.random() * 0.5;
    const radius = 235 + Math.random() * 115;
    cloud.position.set(
      Math.cos(angle) * radius,
      52 + Math.random() * 58,
      Math.sin(angle) * radius
    );
    cloud.rotation.y = Math.random() * Math.PI;
    cloud.userData.speed = 0.9 + Math.random() * 1.3;
    clouds.push(cloud);
    scene.add(cloud);
  }

  // ---- distant seabirds ---------------------------------------------------
  const birdMaterial = new THREE.MeshBasicMaterial({
    color: 0x4a6072,
    transparent: true,
    opacity: 0.55,
    side: THREE.DoubleSide,
  });
  const birds = [];
  for (let i = 0; i < 6; i++) {
    const bird = createBird(birdMaterial);
    const radius = 42 + Math.random() * 58;
    bird.userData.radius = radius;
    bird.userData.angle = Math.random() * Math.PI * 2;
    bird.userData.speed = (0.035 + Math.random() * 0.035) * (Math.random() < 0.5 ? -1 : 1);
    bird.userData.height = 10 + Math.random() * 15;
    bird.userData.phase = Math.random() * Math.PI * 2;
    bird.scale.setScalar(1.0 + Math.random() * 0.9);
    birds.push(bird);
    scene.add(bird);
  }

  return {
    dome,
    update(t, dt) {
      for (const cloud of clouds) {
        cloud.position.x += cloud.userData.speed * dt;
        if (cloud.position.x > 380) cloud.position.x = -380;
      }
      for (const bird of birds) {
        const u = bird.userData;
        u.angle += u.speed * dt;
        bird.position.set(
          Math.cos(u.angle) * u.radius,
          u.height + Math.sin(t * 0.5 + u.phase) * 1.6,
          Math.sin(u.angle) * u.radius
        );
        bird.rotation.y = -u.angle + (u.speed > 0 ? -Math.PI / 2 : Math.PI / 2);
        const flap = Math.sin(t * 4.2 + u.phase) * 0.62;
        u.wings[0].rotation.x = flap;
        u.wings[1].rotation.x = flap;
      }
    },
  };
}