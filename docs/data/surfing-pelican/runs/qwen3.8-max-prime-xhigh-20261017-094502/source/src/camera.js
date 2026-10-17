import * as THREE from "three";
import { oceanHeight } from "./waves.js";
import { clamp, damp, fbm1 } from "./util.js";

/**
 * A slow, never-repeating cinematic orbit: layered incommensurate sines drive
 * azimuth / radius / height, plus a whisper of handheld drift. Nothing here is
 * user controlled — the film just runs.
 */
export function createCameraRig(camera) {
  const desired = new THREE.Vector3();
  const look = new THREE.Vector3();
  const smoothLook = new THREE.Vector3(0, 1.2, 0);
  const shake = new THREE.Vector3();
  let initialised = false;
  let fovBase = 42;

  function update(t, dt, subject, ctx) {
    const azimuth = 1.02 + 0.74 * Math.sin(t * 0.0523) + 0.17 * Math.sin(t * 0.1271 + 1.4);
    const radius = clamp(
      8.6 + 2.5 * Math.sin(t * 0.0411 + 0.7) + 0.85 * Math.sin(t * 0.1137 + 2.2),
      5.6,
      13.5
    );
    const height = clamp(
      2.15 + 1.25 * Math.sin(t * 0.0371 + 2.1) + 0.42 * Math.sin(t * 0.0973 + 0.3),
      1.25,
      4.6
    );

    // aim slightly ahead of the bird, and a touch off-centre for composition
    const lead = clamp(ctx.speed * 0.42, 0, 1.4);
    look.copy(subject);
    look.y += 1.02;
    look.addScaledVector(ctx.forward, lead);
    const sideX = -Math.sin(azimuth);
    const sideZ = Math.cos(azimuth);
    const off = 0.55 + 0.35 * Math.sin(t * 0.029 + 1.1);
    look.x += sideX * off;
    look.z += sideZ * off;

    smoothLook.x = damp(smoothLook.x, look.x, 3.4, dt);
    smoothLook.y = damp(smoothLook.y, look.y, 3.0, dt);
    smoothLook.z = damp(smoothLook.z, look.z, 3.4, dt);

    const cx = smoothLook.x + Math.cos(azimuth) * radius;
    const cz = smoothLook.z + Math.sin(azimuth) * radius;
    const seaHere = oceanHeight(cx, cz, t);
    const cy = seaHere + height;

    // handheld drift
    shake.set(
      (fbm1(t * 0.83 + 11.2) - 0.5) * 0.085,
      (fbm1(t * 0.71 + 47.9) - 0.5) * 0.075,
      (fbm1(t * 0.63 + 91.4) - 0.5) * 0.085
    );

    desired.set(cx, cy, cz).add(shake);
    if (!initialised) {
      camera.position.copy(desired);
      smoothLook.copy(look);
      initialised = true;
    } else {
      camera.position.x = damp(camera.position.x, desired.x, 6.5, dt);
      camera.position.y = damp(camera.position.y, desired.y, 6.5, dt);
      camera.position.z = damp(camera.position.z, desired.z, 6.5, dt);
    }

    // never dip under the sea, and never let a swell crest cut the subject off
    const minY = Math.max(
      oceanHeight(camera.position.x, camera.position.z, t) + 0.55,
      smoothLook.y - 0.55
    );
    if (camera.position.y < minY) camera.position.y = minY;

    camera.lookAt(smoothLook);
    // slow dutch roll + micro shake on the frame
    const roll =
      0.028 * Math.sin(t * 0.061 + 0.4) + 0.012 * Math.sin(t * 0.211) + (fbm1(t * 1.7 + 5) - 0.5) * 0.02;
    camera.rotateZ(roll);

    const fov = fovBase + 2.6 * Math.sin(t * 0.0313 + 1.7) + 1.1 * Math.sin(t * 0.0879);
    if (Math.abs(fov - camera.fov) > 1e-4) {
      camera.fov = fov;
      camera.updateProjectionMatrix();
    }
  }

  return {
    update,
    setFov(f) {
      fovBase = f;
    },
  };
}
