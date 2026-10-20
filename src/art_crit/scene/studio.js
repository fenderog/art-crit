// The scene the video studio renders (studio.py `scene_plan`, ADR-0034): text cards in their looks, and the runs in the
// template's layout, either all at once (duel, line-up, wipe, montage) or one after another (ladder, countdown).
// Like scene.js, every frame is a pure function of its number; strings only ever go through textContent.

import {
  box, caption, clamp, describeRun, drawCaption, el, fmtCost, fmtTime, frames, frameSrc, glow, hide, inCubic, lerp,
  loadPlan, logo, outBack, outCubic, pose, prog, px, ready, show, spring,
} from "./motion.js";

const plan = await loadPlan();
const { fps: FPS, timing: T, segments: SEGMENTS, template: TPL, looks: LOOKS } = plan;
const [W, H] = plan.size;
const S = Math.min(W, H); // type is sized from the short side, so every format reads the same
const ACCENT_HUE = 262;
const slots = plan.slots.map(describeRun);
const N = slots.length;

document.body.style.width = `${W}px`;
document.body.style.height = `${H}px`;
const bg = el("div", "layer", document.body);
const everything = [];
const keep = (...nodes) => {
  everything.push(...nodes.filter(Boolean));
  return nodes[0];
};

// ---- text cards ---------------------------------------------------------------------------------------------------

const cardEls = new Map(); // segment index -> its card's nodes
SEGMENTS.forEach((seg, i) => {
  if (seg.type !== "card") return;
  const look = LOOKS[seg.card.look];
  const light = seg.card.look === "peach" || seg.card.look === "light";
  const root = keep(el("div", "layer st-card", document.body));
  root.style.background = look.bg;
  root.style.color = look.fg;
  const shine = el("div", "layer st-shine", root);
  const mark = keep(box(el("div", "abs", root), S * 0.06, S * 0.06)); // posed; the logo inside keeps its own filter
  logo(mark, Math.round(S * 0.055)).classList.toggle("on-light", light); // dark-mode ink, inverted on a light card
  const body = keep(el("div", "st-card-body", root));
  const base = S * 0.13 * (seg.card.heading.length > 55 ? 0.65 : seg.card.heading.length > 30 ? 0.8 : 1);
  const heading = px(el("div", "st-heading", body), base);
  const words = seg.card.heading.split(/\s+/).filter(Boolean).map((w, k) => {
    const mask = el("span", "mask", heading);
    if (k) heading.insertBefore(document.createTextNode(" "), mask);
    return keep(el("span", "word", mask, w));
  });
  const sub = seg.card.sub ? keep(px(el("div", "st-sub", body, seg.card.sub), base * 0.36)) : null;
  let chip = null;
  if (seg.card.link) {
    chip = keep(px(el("div", "st-chip", body, seg.card.link), base * 0.34));
    chip.style.background = look.chip_bg;
    chip.style.color = look.chip_fg;
  }
  cardEls.set(i, { root, shine, mark, body, words, sub, chip });
});

// `first` = the video opens with this card: its first frame is the cover, so it starts complete and only punches in
function drawCard(c, t, d, first) {
  // the colour opens as a circle from the middle
  const open = first ? 1 : outCubic(prog(t, 0, 0.45));
  pose(c.root, { o: 1 });
  c.root.style.clipPath = open >= 1 ? "none" : `circle(${(Math.hypot(W, H) / 2) * open}px at 50% 50%)`;
  c.shine.style.background = `radial-gradient(${S * 0.9}px ${S * 0.7}px at ${50 + 20 * Math.sin(t * 0.7)}% ${35 + 10 * Math.cos(t * 0.5)}%, rgba(255,255,255,.16), transparent 70%)`;
  const out = outCubic(prog(t, d - T.exit, T.exit));
  pose(c.mark, { o: (first ? 1 : outCubic(prog(t, 0.1, 0.3))) * (1 - out) });
  pose(c.body, { o: 1 - out, y: -out * 60, s: first ? lerp(1.08, 1, outCubic(prog(t, 0, 0.35))) : 1 });
  c.words.forEach((w, k) => {
    const u = first ? 1 : prog(t, 0.15 + k * 0.06, 0.45);
    pose(w, { y: lerp(120, 0, outBack(u)) / 100 * w.offsetHeight });
  });
  if (c.sub) pose(c.sub, { o: first ? 1 : outCubic(prog(t, 0.5, 0.35)), y: first ? 0 : lerp(30, 0, outCubic(prog(t, 0.5, 0.45))) });
  if (c.chip) {
    const u = prog(t, 0.75, 0.45);
    pose(c.chip, { o: outCubic(clamp(u * 3)), s: lerp(0.4, 1, outBack(u)) });
  }
}

// ---- the runs -----------------------------------------------------------------------------------------------------

// which frame of a run's clip shows at local time t of a segment d long (plan.sync)
function clipFrame(run, t, d) {
  const k = Math.round(t * FPS);
  if (plan.sync === "stretch") return Math.min(run.frames - 1, Math.floor((t / d) * run.frames));
  if (plan.sync === "loop") return k % run.frames;
  return Math.min(k, run.frames - 1);
}

function label(parent, run, size, align) {
  if (!plan.labels) return null;
  const scrim = el("div", `st-label ${align}`, parent);
  px(el("b", null, scrim, `${run.pretty} `), size).append(el("span", null, null, run.effort));
  if (plan.metrics) {
    const line = [run.duration_s ? fmtTime(run.duration_s) : null, run.cost ? fmtCost(run.cost) : null].filter(Boolean).join(" · ");
    if (line) px(el("span", "st-metrics", scrim, line), size * 0.72);
  }
  return scrim;
}

// all at once: one tile per run (both in the same square for the wipe)
const tiles = TPL.together ? slots.map((run, i) => {
  const [x, y, s] = plan.tiles[i];
  const tile = keep(box(el("div", "tile", document.body), x, y, s, s));
  tile.style.borderRadius = `${Math.round(s * (TPL.wipe ? 0.03 : 0.06))}px`;
  const img = el("img", null, tile);
  const size = Math.max(18, Math.min(40, s * 0.06));
  const scrim = label(tile, run, size, TPL.wipe && i ? "right" : "left");
  el("div", "ring", tile);
  let badge = null;
  if (TPL.badges) {
    const b = Math.max(52, s * 0.17);
    badge = keep(px(box(el("div", "num", document.body), x + s * 0.04, y + s * 0.04, b, b), b * 0.5));
    badge.textContent = run.label;
  }
  return { tile, img, scrim, badge, x, y, s };
}) : [];
let divider = null;
if (TPL.wipe) {
  const [x, y, s] = plan.tiles[0];
  divider = keep(box(el("div", "st-divider", document.body), x, y, 6, s));
  el("i", null, divider);
}
let title = null;
let titleWords = [];
if (plan.title) {
  title = keep(el("div", "st-title", document.body));
  const heading = px(el("div", "st-heading", title), S * 0.085 * (plan.title.length > 30 ? 0.75 : 1));
  titleWords = plan.title.split(/\s+/).filter(Boolean).map((w, k) => {
    const mask = el("span", "mask", heading);
    if (k) heading.insertBefore(document.createTextNode(" "), mask);
    return keep(el("span", "word", mask, w));
  });
}

function drawTogether(t, d) {
  const exit = inCubic(prog(t, d - T.exit, T.exit));
  tiles.forEach((tile, i) => {
    const at = T.tiles + (TPL.wipe ? 0 : i * T.stagger);
    const e = spring(prog(t, at, 0.6));
    pose(tile.tile, {
      o: outCubic(prog(t, at, 0.15)), y: lerp(H * 0.35, 0, e) - exit * H * 0.5, s: lerp(0.55, 1, e) - exit * 0.1,
      r: TPL.wipe ? 0 : lerp(i % 2 ? 8 : -8, 0, e), blur: exit * 20,
    });
    show(tile.img, frameSrc(slots[i], clipFrame(slots[i], t, d), tile.s <= 560));
    if (tile.badge) {
      const b = prog(t, at + 0.25, 0.4);
      pose(tile.badge, { o: outCubic(clamp(b * 4)) * (1 - exit), s: outBack(b), y: -exit * H * 0.5 });
    }
  });
  if (TPL.wipe) drawWipe(t, d, exit);
  if (title) {
    // the montage: once the tiles have landed they dim and the title comes up over them
    const u = outCubic(prog(t, 1.2, 0.5)) * (1 - exit);
    tiles.forEach((tile) => { tile.tile.style.filter = `brightness(${1 - 0.55 * u})`; });
    pose(title, { o: 1 - exit });
    titleWords.forEach((w, k) => {
      const v = prog(t, 1.3 + k * 0.07, 0.45);
      pose(w, { o: outCubic(clamp(v * 3)), s: lerp(0.4, 1, outBack(v)) });
    });
  }
}

// the wipe: B is uncovered from the right as the divider sweeps across to the left, then the divider settles at plan.wipe
function drawWipe(t, d, exit) {
  const sweep = 0.6 + 0.3 * (d - 0.6);
  const p = t < sweep ? lerp(100, 0, outCubic(prog(t, 0.6, sweep - 0.6))) : lerp(0, plan.wipe, outCubic(prog(t, sweep, 0.25 * d)));
  const [a, b] = tiles;
  b.tile.style.clipPath = `inset(0 0 0 ${p}%)`;
  if (a.scrim) a.scrim.style.opacity = String(clamp(p / 35));
  if (b.scrim) b.scrim.style.opacity = String(clamp((100 - p) / 35));
  divider.style.left = `${a.x + (a.s * p) / 100 - 3}px`;
  pose(divider, { o: outCubic(prog(t, 0.5, 0.2)) * (1 - exit), y: -exit * H * 0.5 });
}

// one after another: a story-style bar, then each run's card and caption in turn
const seqEls = [];
let chrome = null;
let bars = [];
let counter = null;
let pageLine = null;
const CARD = [90, 260, 900];
if (!TPL.together) {
  chrome = keep(el("div", "layer", document.body));
  const progress = box(el("div", "progress", chrome), 48, 40, 984);
  bars = slots.map(() => el("i", null, el("span", null, progress)));
  const toprow = px(box(el("div", "abs toprow", chrome), 48, 66, 984), 24);
  logo(toprow, 31);
  counter = el("span", "dim", toprow);
  pageLine = px(box(el("div", "abs mini-prompt", chrome), 48, 112, 984), 32);
  pageLine.style.webkitLineClamp = "2";
  const [cx, cy, side] = CARD;
  slots.forEach((run) => {
    const card = keep(box(el("div", "card", document.body), cx, cy, side, side));
    card.style.borderRadius = `${Math.round(side * 0.05)}px`;
    card.style.boxShadow = `0 40px 120px rgba(0,0,0,.6), 0 0 90px hsl(${run.hue} 80% 55% / .35)`;
    const img = el("img", null, card);
    el("div", "ring", card);
    let badge = null;
    if (TPL.badges) {
      badge = keep(px(box(el("div", "num", document.body), cx - 34, cy - 34, 130, 130), 58));
      badge.textContent = run.label;
    }
    const info = plan.labels ? caption(document.body, run, 90, 1200, 900, { vendor: 36, name: [124, 64], effort: 36, stats: 54 }, plan.metrics) : null;
    if (info) keep(...info.nodes);
    seqEls.push({ card, img, badge, info });
  });
}

function drawSlot(t, d, i) {
  const run = slots[i];
  const els = seqEls[i];
  const exit = inCubic(prog(t, d - T.exit, T.exit));
  const e = spring(prog(t, 0, T.enter));
  pose(els.card, {
    y: lerp(H * 0.5, 0, e) - exit * H * 0.55, s: lerp(0.72, 1, e) - exit * 0.12, r: lerp(9, 0, e),
    blur: (1 - outCubic(prog(t, 0, 0.22))) * 22 + exit * 24,
  });
  els.img.style.transform = `scale(${1.0 + 0.045 * t / d})`;
  show(els.img, frameSrc(run, clipFrame(run, t, d), false));
  if (els.badge) {
    const u = prog(t, T.enter * 0.55, 0.4);
    pose(els.badge, { o: outCubic(prog(t, T.enter * 0.55, 0.2)), s: outBack(u) * (1 - exit * 0.5), r: lerp(-30, 0, outCubic(u)), y: -exit * H * 0.55 });
  }
  if (els.info) drawCaption(els.info, run, t, outCubic(prog(t, d - T.exit - 0.05, T.exit)), T);
  pose(chrome, { o: 1 });
  bars.forEach((bar, k) => { bar.style.transform = `scaleX(${k < i ? 1 : k > i ? 0 : prog(t, 0, d)})`; });
  counter.textContent = `${i + 1} / ${N}`;
  pageLine.textContent = run.page_title;
}

// ---- drawing ------------------------------------------------------------------------------------------------------

frames((f) => {
  const k = SEGMENTS.findLastIndex((s) => s.start <= f);
  const seg = SEGMENTS[Math.max(0, k)];
  const t = (f - seg.start) / FPS;
  const d = seg.frames / FPS;
  everything.forEach(hide);
  tiles.forEach((tile) => { tile.tile.style.clipPath = ""; });
  const behind = seg.type === "slot" ? slots[seg.slot] : null;
  glow(bg, f / FPS, behind ? behind.hue : ACCENT_HUE, behind ? CARD[0] + CARD[2] / 2 : W / 2, behind ? CARD[1] + CARD[2] / 2 : H * 0.45, plan.size);
  if (seg.type === "card") drawCard(cardEls.get(Math.max(0, k)), t, d, k <= 0);
  else if (seg.type === "slots") drawTogether(t, d);
  else drawSlot(t, d, seg.slot);
});
await ready();
