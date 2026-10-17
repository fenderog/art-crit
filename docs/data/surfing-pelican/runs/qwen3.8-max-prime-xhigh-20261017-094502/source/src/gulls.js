import * as THREE from "three";

/** Flat wing in the XZ plane: chord along X, tip toward +Z, normal up. */
function gullWingGeometry() {
  const s = new THREE.Shape();
  s.moveTo(0.085, 0.0);
  s.bezierCurveTo(0.1, 0.2, 0.05, 0.44, -0.05, 0.63);
  s.lineTo(-0.135, 0.61);
  s.bezierCurveTo(-0.06, 0.4, -0.055, 0.18, -0.1, 0.0);
  s.closePath();
  const g = new THREE.ShapeGeometry(s, 10);
  g.rotateX(-Math.PI / 2); // shape-x -> +X (chord), shape-y -> -Z (span)
  g.scale(1, 1, -1); // span toward +Z
  return g;
}

/** A loose flock wheeling in the distance — pure set dressing. */
export function createGulls(count = 7) {
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#f6f3ec"),
    roughness: 0.85,
    side: THREE.DoubleSide,
  });
  const darkMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#4b4b53"),
    roughness: 0.8,
    side: THREE.DoubleSide,
  });

  const wingGeo = gullWingGeometry();
  const tipGeo = new THREE.PlaneGeometry(0.13, 0.09);
  tipGeo.rotateX(-Math.PI / 2);
  const bodyGeo = new THREE.SphereGeometry(0.085, 14, 10);
  const beakGeo = new THREE.ConeGeometry(0.026, 0.13, 8);
  beakGeo.rotateZ(-Math.PI / 2);

  const birds = [];
  for (let i = 0; i < count; i++) {
    const b = new THREE.Group();

    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.scale.set(1.9, 0.85, 0.75);
    b.add(body);
    const beak = new THREE.Mesh(beakGeo, darkMat);
    beak.position.set(0.19, 0.012, 0);
    b.add(beak);
    const tail = new THREE.Mesh(tipGeo, bodyMat);
    tail.position.set(-0.2, 0.005, 0);
    tail.scale.set(1.1, 1, 0.55);
    b.add(tail);

    const wings = [];
    for (const side of [1, -1]) {
      const w = new THREE.Group();
      w.position.set(-0.01, 0.012, side * 0.045);
      w.scale.z = side; // -1 mirrors the port wing
      const mesh = new THREE.Mesh(wingGeo, bodyMat);
      w.add(mesh);
      const tip = new THREE.Mesh(tipGeo, darkMat);
      tip.position.set(-0.035, 0.004, 0.58);
      tip.scale.set(0.9, 1, 0.5);
      w.add(tip);
      b.add(w);
      wings.push({ group: w, side });
    }

    b.scale.setScalar(0.9 + Math.random() * 1.1);
    group.add(b);
    birds.push({
      obj: b,
      wings,
      radius: 46 + Math.random() * 60,
      height: 8 + Math.random() * 16,
      speed: (0.05 + Math.random() * 0.05) * (Math.random() < 0.3 ? -1 : 1),
      phase: (i / count) * Math.PI * 2 + Math.random(),
      flapSpeed: 3.2 + Math.random() * 2.4,
      flapPhase: Math.random() * 10,
      glidePhase: Math.random() * 6,
      cx: (Math.random() - 0.5) * 16,
      cz: (Math.random() - 0.5) * 16,
      squash: 0.55 + Math.random() * 0.4,
      bob: 0.5 + Math.random() * 1.5,
    });
  }

  function update(t) {
    for (const bird of birds) {
      const a = bird.phase + t * bird.speed;
      const r = bird.radius + Math.sin(t * 0.11 + bird.phase) * 5;
      const x = bird.cx + Math.cos(a) * r;
      const z = bird.cz + Math.sin(a) * r * bird.squash;
      const y = bird.height + Math.sin(t * 0.23 + bird.phase * 2) * bird.bob;
      bird.obj.position.set(x, y, z);

      // heading = d/da of the orbit, flipped when flying clockwise
      const dir = Math.sign(bird.speed);
      const hx = -Math.sin(a) * r * dir;
      const hz = Math.cos(a) * r * bird.squash * dir;
      bird.obj.rotation.y = Math.atan2(-hz, hx);
      bird.obj.rotation.x = dir * 0.32; // bank into the turn
      bird.obj.rotation.z = Math.sin(t * 0.37 + bird.phase) * 0.07;

      // flap, then hold a glide when the "glide" oscillator is negative
      const glide = Math.sin(t * 0.13 + bird.glidePhase);
      const amp = 0.22 + 0.78 * Math.max(0, glide);
      const flap = Math.sin(t * bird.flapSpeed + bird.flapPhase) * amp + 0.08 * glide;
      for (const w of bird.wings) {
        w.group.rotation.x = -w.side * flap * 0.9;
      }
    }
  }

  return { group, update };
}
