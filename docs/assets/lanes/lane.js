// One horizontal lane of cards: ‹ › buttons at its edges plus mouse/touch dragging. The track slides by whole cards
// (translateX); dragging moves it freely and stops at either end (no snapping).

import { el } from "../dom.js";

const NO_DRAG = ".model-stage, input, select, iframe, textarea"; // things that handle their own pointer

export function createLane(cards) {
  const track = el("div", { class: "v2-track" }, cards);
  const viewport = el("div", { class: "v2-viewport" }, [track]);
  const arrow = (dir) => el("button", {
    class: `v2-arrow is-${dir}`, text: dir === "prev" ? "‹" : "›",
    attrs: { type: "button", "aria-label": dir === "prev" ? "Previous runs" : "Next runs" },
  });
  const prev = arrow("prev");
  const next = arrow("next");
  const lane = { node: el("div", { class: "v2-lane-body" }, [viewport, prev, next]), x: 0, onRange: null };

  const measure = () => {
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    const step = (cards[0] ? cards[0].offsetWidth : 320) + gap;
    const visible = Math.max(1, Math.floor((viewport.clientWidth + gap) / Math.max(step, 1)));
    const maxPx = Math.max(0, track.scrollWidth - viewport.clientWidth);
    return { step, visible, maxPx };
  };

  // The lane sits at a free pixel offset (lane.x <= 0): dragging leaves it exactly where it is let go, no snapping.
  function apply(animate = true) {
    const m = measure();
    lane.x = Math.min(0, Math.max(-m.maxPx, lane.x));
    track.classList.toggle("is-dragging", !animate);
    track.style.transform = `translateX(${lane.x}px)`;
    prev.disabled = lane.x >= -1;
    next.disabled = lane.x <= -m.maxPx + 1;
    prev.hidden = next.hidden = m.maxPx <= 1;
    const first = Math.round(-lane.x / m.step);
    lane.onRange?.(first + 1, Math.min(cards.length, first + m.visible), m.maxPx > 1);
  }
  // The arrows page by whole cards, from wherever the lane is.
  prev.addEventListener("click", () => { stopGlide(); const m = measure(); lane.x = -Math.max(0, Math.ceil(-lane.x / m.step - 1e-6) - m.visible) * m.step; apply(); });
  next.addEventListener("click", () => { stopGlide(); const m = measure(); lane.x = -(Math.floor(-lane.x / m.step + 1e-6) + m.visible) * m.step; apply(); });

  // Dragging. A drag starts only after 6px of movement, so clicks on buttons and links inside cards still work, and a
  // click that ends a drag is swallowed.
  // A video can be dragged by its picture; only its native controls bar (the bottom strip) keeps its own pointer handling.
  const onVideoControls = (e) => e.target instanceof HTMLVideoElement && e.target.getBoundingClientRect().bottom - e.clientY < 48;
  // Momentum: on release the lane keeps gliding with the speed of the flick and eases to a stop (no snapping).
  let glide = 0;
  const stopGlide = () => { cancelAnimationFrame(glide); glide = 0; };
  let samples = [];
  let drag = null;
  let justDragged = false;
  const clamp = (pos, m) => Math.max(-m.maxPx, Math.min(0, pos));
  track.addEventListener("pointerdown", (e) => {
    if ((e.pointerType === "mouse" && e.button !== 0) || e.target.closest(NO_DRAG) || onVideoControls(e)) return;
    stopGlide();
    samples = [];
    drag = { x: e.clientX, id: e.pointerId, start: lane.x, moved: false, pos: lane.x };
  });
  track.addEventListener("pointermove", (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved) {
      if (Math.abs(dx) < 6) return;
      drag.moved = true;
      try { track.setPointerCapture(e.pointerId); } catch {} // keeps the drag going outside the lane
      track.classList.add("is-dragging");
    }
    const m = measure();
    drag.pos = clamp(drag.start + dx, m);
    const now = performance.now();
    samples.push([now, drag.pos]);
    samples = samples.filter(([t]) => now - t < 100);
    track.style.transform = `translateX(${drag.pos}px)`;
  });
  const end = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag;
    drag = null;
    if (!d.moved) return;
    justDragged = true;
    setTimeout(() => { justDragged = false; }, 0);
    lane.x = d.pos;
    apply(false);
    const now = performance.now();
    const recent = samples.filter(([t]) => now - t < 100);
    let v = 0; // px per ms, from the last 100ms of the drag
    if (recent.length > 1) {
      const [t0, x0] = recent[0], [t1, x1] = recent[recent.length - 1];
      v = t1 > t0 ? (x1 - x0) / (t1 - t0) : 0;
    }
    if (Math.abs(v) < 0.05) return;
    let last = now;
    const tick = (t) => {
      const dt = Math.min(32, t - last);
      last = t;
      lane.x += v * dt;
      v *= Math.exp(-dt / 160); // friction
      const m = measure();
      const hit = lane.x > 0 || lane.x < -m.maxPx;
      apply(false);
      glide = Math.abs(v) > 0.02 && !hit ? requestAnimationFrame(tick) : 0;
    };
    glide = requestAnimationFrame(tick);
  };
  track.addEventListener("pointerup", end);
  track.addEventListener("pointercancel", end);
  track.addEventListener("click", (e) => { if (justDragged) { e.stopPropagation(); e.preventDefault(); } }, true);
  track.addEventListener("dragstart", (e) => e.preventDefault()); // no native image dragging

  new ResizeObserver(() => apply(false)).observe(viewport); // also runs once when attached
  return lane;
}
