// What both video scenes share (scene.js = `art-crit video`'s layouts, studio.js = the video studio's templates;
// ADR-0033): easing, posing nodes, the logo, frame images, number formats, a run's caption and the background glow.
// Every frame must be a pure function of its number: nothing here reads a clock.

import { EFFORTS, modelParts, prettyModelName, vendorIcon, vendorName, vendorOf, vendorOptions } from "./assets/runs.js"; // docs/assets, linked in beside the scene

export const clamp = (x, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, x));
export const lerp = (a, b, u) => a + (b - a) * u;
export const prog = (t, start, dur) => clamp((t - start) / dur);
export const outCubic = (u) => 1 - (1 - u) ** 3;
export const inCubic = (u) => u ** 3;
export const outBack = (u) => 1 + 2.4 * (u - 1) ** 3 + 1.4 * (u - 1) ** 2;
export const spring = (u) => (u >= 1 ? 1 : 1 - Math.exp(-6 * u) * Math.cos(9.5 * u));

export async function loadPlan() {
  return (await fetch(new URLSearchParams(location.search).get("plan"), { cache: "no-store" })).json();
}

export function el(tag, cls, parent, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  if (parent) parent.append(node);
  return node;
}
export function box(node, x, y, w, h) {
  node.style.left = `${x}px`;
  node.style.top = `${y}px`;
  if (w != null) node.style.width = `${w}px`;
  if (h != null) node.style.height = `${h}px`;
  return node;
}
export function px(node, size) {
  node.style.fontSize = `${size}px`;
  return node;
}
// opacity + transform (+ motion blur) in one call; o <= 0 hides the node
export function pose(node, { o = 1, x = 0, y = 0, s = 1, r = 0, blur = 0 } = {}) {
  node.style.visibility = o > 0.001 ? "visible" : "hidden";
  node.style.opacity = String(clamp(o));
  node.style.transform = `translate(${x}px, ${y}px) scale(${s}) rotate(${r}deg)`;
  node.style.filter = blur > 0.4 ? `blur(${blur.toFixed(1)}px)` : "none";
}
export const hide = (node) => pose(node, { o: 0 });

// The site's wordmark (docs/assets/logo.svg, 4.1:1). Its dark-mode colours apply: video.py opens the scene in dark mode.
export function logo(parent, height) {
  const img = el("img", "logo", parent);
  img.src = "assets/logo.svg";
  img.alt = "art-crit";
  img.style.height = `${height}px`;
  img.style.width = `${Math.round(height * 2312 / 562)}px`;
  return img;
}

// The largest font size (from max down to min) at which the node's text fits `width`; wraps at min if it never does.
export function fit(node, width, max, min) {
  for (let size = max; size >= min; size -= 2) {
    px(node, size);
    if (node.scrollWidth <= width) return size;
  }
  node.classList.add("wraps");
  return min;
}

// Frame images: set a src only when it changes, and wait for every new one to decode before the screenshot.
let decoding = [];
export function show(img, src) {
  if (img.dataset.src === src) return;
  img.dataset.src = src;
  img.src = src;
  decoding.push(img.decode().catch(() => {}));
}
export function frameSrc(run, k, small) {
  const n = ((k % run.frames) + run.frames) % run.frames;
  return `clips/${run.index}/${small ? "s" : "f"}/${String(n + 1).padStart(4, "0")}.jpg`;
}
// renderFrame(f) for a scene: reset, draw, then wait for the new frame images and one paint
export function frames(draw) {
  window.renderFrame = async (f) => {
    decoding = [];
    draw(f);
    await Promise.all(decoding);
    await new Promise((resolve) => requestAnimationFrame(() => resolve()));
  };
}
export async function ready() {
  await document.fonts.ready;
  await Promise.all([...document.images].filter((i) => i.src).map((i) => i.decode().catch(() => {})));
  window.sceneReady = true;
}

export const fmtTime = (s) => (s < 60 ? `${Math.floor(s)}s` : `${Math.floor(s / 60)}m ${String(Math.floor(s % 60)).padStart(2, "0")}s`);
export const fmtTokens = (v) => (v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v >= 1000 ? `${Math.round(v / 1000)}k` : `${Math.round(v)}`);
export const fmtCost = (v) => `$${v < 0.1 ? v.toFixed(3) : v.toFixed(2)}`;

// A run as the scenes show it, named the way the site names it (`r` = video.run_info plus whatever the plan adds).
export function describeRun(r, index) {
  const v = vendorOf(r.model);
  return {
    ...r, index, num: index + 1,
    pretty: prettyModelName(modelParts(r.model).name),
    vendor: vendorName(v), icon: vendorIcon(v),
    hue: Number(vendorOptions(r.model).style["--vh"]),
    level: Math.max(0, EFFORTS.indexOf(r.effort)),
    stats: [
      r.duration_s ? ["TIME", r.duration_s, fmtTime] : null,
      r.tokens ? ["TOKENS", r.tokens, fmtTokens] : null,
      r.cost ? ["COST", r.cost, fmtCost] : null,
    ].filter(Boolean),
  };
}

// A run's caption at (x, y), `width` wide: vendor icon + name, the model's name, its effort meter and its numbers.
// sizes = {vendor, name: [max, min], effort, stats}; stats = false leaves the numbers out.
export function caption(parent, run, x, y, width, sizes, stats = true) {
  const info = box(el("div", "abs", parent), x, y, width);
  const vendor = px(el("div", "vendor-row", info), sizes.vendor);
  const icon = el("span", "vendor-icon", vendor);
  icon.style.width = icon.style.height = `${sizes.vendor * 1.75}px`;
  if (run.icon) el("img", null, icon).src = run.icon;
  else {
    icon.textContent = run.vendor[0];
    icon.style.background = `hsl(${run.hue} 70% 45%)`;
  }
  el("span", null, vendor, run.vendor);
  const name = el("div", "name", info);
  name.style.marginTop = `${sizes.vendor * 0.6}px`;
  const words = run.pretty.split(" ").map((w, i) => {
    const mask = el("span", "mask", name);
    if (i) name.insertBefore(document.createTextNode(" "), mask);
    return el("span", "word", mask, w);
  });
  fit(name, width, ...sizes.name);
  const effort = px(el("div", "effort", info), sizes.effort);
  effort.style.marginTop = `${sizes.effort * 0.7}px`;
  const meter = el("span", "meter", effort);
  const lights = [1, 2, 3, 4, 5, 6].map((lvl) => {
    const b = el("b", null, meter);
    b.style.height = `${0.3 + lvl * 0.1}em`;
    return b;
  });
  el("span", null, effort, run.effort);
  const numbers = px(el("div", "stats", info), sizes.stats);
  numbers.style.marginTop = `${sizes.stats * 0.55}px`;
  const values = (stats ? run.stats : []).map(([label, value, format]) => {
    const stat = el("div", "stat", numbers);
    el("small", null, stat, label);
    const strong = el("strong", null, stat, format(value));
    stat.style.minWidth = `${strong.offsetWidth + 2}px`; // counting up must not push the next stat around
    return { strong, value, format };
  });
  return { vendor, words, effort, lights, stats: numbers, values, nodes: [vendor, effort, numbers, ...words] };
}

// The caption at local time t of its run's turn (T = the plan's timings), fading out with textOut (0..1).
export function drawCaption(c, run, t, textOut, T) {
  const textPose = (start, extra) => {
    const u = prog(t, start, 0.4);
    return { o: outCubic(prog(t, start, 0.2)) * (1 - textOut), y: -textOut * 40, ...extra(u) };
  };
  pose(c.vendor, textPose(T.name - 0.12, (u) => ({ x: lerp(-50, 0, outCubic(u)) })));
  c.words.forEach((w, i) => {
    const u = prog(t, T.name + i * 0.07, 0.45);
    pose(w, { y: lerp(120, 0, outBack(u)) / 100 * w.offsetHeight - textOut * 40, o: 1 - textOut });
  });
  pose(c.effort, textPose(T.stats - 0.12, (u) => ({ x: lerp(-40, 0, outCubic(u)) })));
  c.lights.forEach((b, i) => b.classList.toggle("on", i < run.level && t >= T.stats + 0.07 * (i + 1)));
  pose(c.stats, textPose(T.stats, (u) => ({ y: lerp(30, 0, outCubic(u)) - textOut * 40 })));
  const u = outCubic(prog(t, T.stats, T.count));
  c.values.forEach((v) => { v.strong.textContent = v.format(v.value * u); });
}

// A glow in `hue` around (cx, cy), drifting a little, over a dark floor.
export function glow(node, t, hue, cx, cy, size) {
  const x = cx + Math.sin(t * 0.6) * size[0] * 0.06;
  const y = cy + Math.cos(t * 0.5) * size[1] * 0.03;
  const r = Math.max(...size) * 0.62;
  node.style.background = `radial-gradient(${r}px ${r}px at ${x}px ${y}px, hsl(${hue} 85% 52% / .42), hsl(${hue} 80% 40% / .12) 55%, transparent 75%),`
    + ` radial-gradient(130% 55% at 50% 115%, hsl(${hue + 18} 70% 34% / .55), transparent 70%), linear-gradient(180deg, #0c0b14, #07070b)`;
}
