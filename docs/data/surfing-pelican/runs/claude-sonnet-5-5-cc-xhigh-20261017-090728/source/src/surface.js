import { keyframes } from "./water.js";
import { NS, REG, ND, profilePoint, profileArc } from "./profile.js";
import { WAVE, sliceState } from "./wavefield.js";

// JS twin of the vertex shader: where is profile index `idx` of slice x at time t?
const _p = [0, 0];
const _s = { c: 0, h: 1 };
export function slicePos(x, idx, t, out) {
  sliceState(x, t, _s);
  profilePoint(keyframes, _s.c, idx, _p);
  const k = _s.h * WAVE.scale;
  out[0] = x;
  out[1] = _p[1] * k;
  out[2] = -Math.max(-WAVE.qMax, Math.min(WAVE.qMax, _p[0] * k));
  return out;
}

export function sliceArc(x, idx, t) {
  sliceState(x, t, _s);
  return (profileArc(keyframes, _s.c, idx) - profileArc(keyframes, _s.c, REG.E)) * _s.h * WAVE.scale;
}

// Profile index on the inner wall where the surface is `height` metres above the floor.
export function wallIndexAt(x, height, t) {
  sliceState(x, t, _s);
  const k = _s.h * WAVE.scale;
  let lo = REG.D + ND - 1;
  let prevY = 0;
  profilePoint(keyframes, _s.c, lo, _p);
  prevY = _p[1] * k;
  for (let j = lo - 1; j >= REG.D; j -= 0.5) {
    profilePoint(keyframes, _s.c, j, _p);
    const y = _p[1] * k;
    if (y >= height) {
      const f = (height - prevY) / Math.max(y - prevY, 1e-5);
      return j + 0.5 * (1 - clamp01(f));
    }
    prevY = y;
  }
  return REG.D;
}
const clamp01 = (x) => Math.min(1, Math.max(0, x));

export { NS };
