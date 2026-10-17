import * as THREE from "three";

function dropletTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 64;
  const g = canvas.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 2, 32, 32, 30);
  grd.addColorStop(0, "rgba(255,255,255,0.95)");
  grd.addColorStop(0.35, "rgba(236,248,255,0.55)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createSpray() {
  const map = dropletTexture();
  const group = new THREE.Group();
  const count = 64;
  const drops = [];
  for (let i = 0; i < count; i++) {
    const material = new THREE.SpriteMaterial({
      map,
      transparent: true,
      depthWrite: false,
      opacity: 0,
      color: 0xf7fbff,
    });
    const sprite = new THREE.Sprite(material);
    sprite.visible = false;
    sprite.scale.setScalar(0.2);
    group.add(sprite);
    drops.push({
      sprite,
      life: 0,
      age: 1,
      vel: new THREE.Vector3(),
    });
  }

  const forward = new THREE.Vector3();
  const right = new THREE.Vector3();
  const up = new THREE.Vector3();
  const tail = new THREE.Vector3();
  let cursor = 0;

  function emit(rider, speed) {
    const drop = drops[cursor];
    cursor = (cursor + 1) % drops.length;
    forward.set(0, 0, -1).applyQuaternion(rider.quaternion);
    right.set(1, 0, 0).applyQuaternion(rider.quaternion);
    up.set(0, 1, 0).applyQuaternion(rider.quaternion);
    tail.set(0.2 + Math.random() * 0.08, 0.04, 0.85 + Math.random() * 0.2);
    tail.applyQuaternion(rider.quaternion).add(rider.position);
    drop.sprite.position.copy(tail);
    drop.sprite.visible = true;
    drop.life = 0.75 + Math.random() * 0.35;
    drop.age = drop.life;
    // Water is still in the world; the ride frame scrolls forward at `speed`,
    // so a fresh droplet trails toward -x and is kicked up off the rail.
    drop.vel.set(-speed * (0.85 + Math.random() * 0.2), 0, (Math.random() - 0.5) * 0.35);
    drop.vel.addScaledVector(up, 1.3 + Math.random() * 1.7);
    drop.vel.addScaledVector(right, 0.35 + Math.random() * 0.9);
    drop.vel.addScaledVector(forward, -Math.random() * 0.5);
  }

  function update(dt, rider, speed) {
    const births = dt > 0 ? 3 : 0;
    for (let i = 0; i < births; i++) emit(rider, speed);
    for (const drop of drops) {
      if (drop.life <= 0) continue;
      drop.life -= dt;
      drop.vel.y -= 3.2 * dt;
      drop.sprite.position.addScaledVector(drop.vel, dt);
      const u = Math.max(drop.life, 0) / drop.age;
      drop.sprite.material.opacity = u * 0.8;
      const s = 0.12 + (1 - u) * 0.55;
      drop.sprite.scale.setScalar(s);
      if (drop.life <= 0) {
        drop.sprite.visible = false;
        drop.sprite.material.opacity = 0;
      }
    }
  }

  return { group, update };
}
