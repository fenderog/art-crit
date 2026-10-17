import * as THREE from 'three';

// A handful of distant gulls that circle far behind the pelican. They are
// cheap silhouettes: two flapping extruded chevrons each.

function chevronGeometry() {
  const shape = new THREE.Shape();
  shape.moveTo(0, -0.12);
  shape.lineTo(0.75, 0.34);
  shape.lineTo(1.65, 0.2);
  shape.lineTo(1.55, -0.16);
  shape.lineTo(0.7, -0.02);
  shape.closePath();
  return new THREE.ExtrudeGeometry(shape, {
    depth: 0.03,
    bevelEnabled: false,
    curveSegments: 2,
  }).rotateX(-Math.PI / 2);
}

export function createBirds(count = 7) {
  const geometry = chevronGeometry();
  const material = new THREE.MeshBasicMaterial({
    color: 0x41596b,
    fog: true,
    side: THREE.DoubleSide,
  });

  const flock = new THREE.Group();
  const birds = [];

  for (let i = 0; i < count; i++) {
    const pivot = new THREE.Group();
    const bird = new THREE.Group();

    const wingR = new THREE.Mesh(geometry, material);
    const wingL = new THREE.Mesh(geometry, material);
    wingL.scale.x = -1;
    bird.add(wingR, wingL);

    const body = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 6), material);
    body.scale.set(1, 0.8, 2.4);
    bird.add(body);

    pivot.add(bird);
    flock.add(pivot);

    birds.push({
      pivot,
      bird,
      wingR,
      wingL,
      radius: 46 + Math.random() * 62,
      speed: (0.032 + Math.random() * 0.03) * (Math.random() < 0.5 ? -1 : 1),
      phase: Math.random() * Math.PI * 2,
      height: 11 + Math.random() * 17,
      scale: 1.1 + Math.random() * 1.5,
      flapSpeed: 2.1 + Math.random() * 1.5,
    });
    bird.scale.setScalar(birds[i].scale);
  }

  const out = new THREE.Vector3();

  return {
    group: flock,
    update(t) {
      for (const b of birds) {
        const a = b.phase + t * b.speed;
        b.pivot.position.set(
          Math.cos(a) * b.radius,
          b.height + Math.sin(t * 0.36 + b.phase) * 1.6,
          Math.sin(a) * b.radius
        );
        out.set(-Math.sin(a) * Math.sign(b.speed), 0, Math.cos(a) * Math.sign(b.speed));
        b.pivot.rotation.y = Math.atan2(out.x, out.z);
        b.bird.rotation.z = Math.sin(t * 0.5 + b.phase) * 0.16;

        const flap = Math.sin(t * b.flapSpeed + b.phase);
        b.wingR.rotation.z = 0.28 + flap * 0.62;
        b.wingL.rotation.z = -0.28 - flap * 0.62;
      }
    },
  };
}