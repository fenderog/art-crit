import { WAVE } from "./wavefield.js";

// Records where the board has been, in the frame of the sea, so the water shader can paint a wake.
// Samples are uploaded oldest first, which lets the shader look only at the few samples near a pixel.
export const TRAIL_N = 48;
export const TRAIL_LIFE = 3.5;

export function createTrail(uniforms) {
  const arr = uniforms.uTrail.value;
  const bounds = uniforms.uTrailBounds.value;
  const samples = [];
  let acc = 0;
  const step = 1 / 11.5;

  function update(t, dt, st) {
    acc += dt;
    while (acc >= step) {
      acc -= step;
      samples.push({
        x: st.tailX + t * WAVE.speed,
        y: st.tailArc + t * WAVE.climb,
        t,
        w: 0.55 + 0.45 * st.energy,
      });
    }
    while (samples.length > TRAIL_N || (samples.length && t - samples[0].t > TRAIL_LIFE)) samples.shift();

    // right-align into the uniform array; unused leading slots just extend the oldest x so it stays monotonic
    const n = samples.length;
    const pad = TRAIL_N - n;
    let x0 = 1e9;
    let x1 = -1e9;
    let y0 = 1e9;
    let y1 = -1e9;
    for (let i = 0; i < TRAIL_N; i++) {
      const s = i < pad ? null : samples[i - pad];
      const u = arr[i];
      if (s) {
        u.set(s.x, s.y, s.t, s.w);
        x0 = Math.min(x0, s.x);
        x1 = Math.max(x1, s.x);
        y0 = Math.min(y0, s.y);
        y1 = Math.max(y1, s.y);
      } else {
        const ref = n ? samples[0] : { x: 0, y: 0 };
        u.set(ref.x - 0.3 * (pad - i), ref.y, -1e5, 0);
      }
    }
    bounds.set(x0 - 3.5, x1 + 3.5, y0 - 3.5, y1 + 3.5);
  }
  return { update };
}
