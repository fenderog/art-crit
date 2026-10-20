// The scene `art-crit video` renders (video.py `render_layout`, ADR-0033; helpers in motion.js). Every frame is a pure function of its number:
// video.py calls `renderFrame(f)`, screenshots the page and moves on, so the motion is the same on every machine and
// never depends on how fast Chrome is. The plan (plan-<layout>.json, made by video.py) holds the size, the timeline,
// the timings and the runs. Text from runs and prompts only ever goes through textContent.

import {
  box, caption, clamp, describeRun, el, drawCaption, fit, frames, frameSrc, glow, hide, inCubic, lerp, loadPlan, logo,
  outBack, outCubic, pose, prog, px, ready, show, spring,
} from "./motion.js";
import { finaleScene, hookScene } from "./parts.js";

const plan = await loadPlan();
const { fps: FPS, timing: T, tiles: TILES, segments: SEGMENTS } = plan;
const [W, H] = plan.size;
const WIDE = W > H;
const ACCENT_HUE = 262;

const runs = plan.runs.map(describeRun);
const N = runs.length;
const pick = runs.find((r) => r.pick) ?? null;
const oneModel = new Set(runs.map((r) => r.pretty)).size === 1;

function hookLines() {
  if (oneModel) return [runs[0].pretty, `${N} effort levels.`];
  return [`${new Set(runs.map((r) => r.pretty)).size} AI models.`, "Same prompt."];
}

// ---- geometry -----------------------------------------------------------------------------------------------------

const G = WIDE
  ? {
    card: [60, 60, 960], badge: 112, sticker: 40,
    progress: [1100, 64, 760], toprow: [1100, 92, 760, 24], mini: [1100, 138, 760, 30, 3],
    info: [1100, 330, 760], vendor: 34, name: [132, 64], effort: 38, stats: 58,
  }
  : {
    card: [90, 222, 900], badge: 104, sticker: 36,
    progress: [48, 40, 984], toprow: [48, 66, 984, 24], mini: [48, 108, 984, 32, 2],
    info: [90, 1160, 900], vendor: 36, name: [124, 64], effort: 36, stats: 54,
    gridHead: [48, 120, 984, 72], gridPrompt: [48, 214, 984, 34, 3], gridLogo: [48, 44, 44],
  };

// ---- the layers ---------------------------------------------------------------------------------------------------

document.body.style.width = `${W}px`;
document.body.style.height = `${H}px`;
const bg = el("div", "layer", document.body);

// the opening
const [line1, line2] = hookLines();
const hook = hookScene(document.body, runs, { size: plan.size, lines: [line1, line2], prompt: plan.prompt });

// one run at a time: the progress bar, the prompt reminder, then a card and a caption per run
const chrome = el("div", "layer", document.body);
const [prx, pry, prw] = G.progress;
const progress = box(el("div", "progress", chrome), prx, pry, prw);
const bars = runs.map(() => el("i", null, el("span", null, progress)));
const [tx, ty, tw, tsize] = G.toprow;
const toprow = px(box(el("div", "abs toprow", chrome), tx, ty, tw), tsize);
logo(toprow, Math.round(tsize * 1.3));
const counter = el("span", "dim", toprow);
const [mx, my, mw, msize, mlines] = G.mini;
const mini = px(box(el("div", "abs mini-prompt", chrome), mx, my, mw), msize);
mini.style.webkitLineClamp = String(mlines);
mini.textContent = plan.prompt;

const [cx, cy, side] = G.card;
const [ix, iy, iw] = G.info;
const runEls = runs.map((run) => {
  const card = box(el("div", "card", document.body), cx, cy, side, side);
  card.style.borderRadius = `${Math.round(side * 0.05)}px`;
  card.style.boxShadow = `0 40px 120px rgba(0,0,0,.6), 0 0 90px hsl(${run.hue} 80% 55% / .35)`;
  const img = el("img", null, card);
  el("div", "ring", card);
  const badge = px(box(el("div", "num", document.body), cx - G.badge * 0.28, cy - G.badge * 0.28, G.badge, G.badge), G.badge * 0.52);
  badge.textContent = String(run.num);
  let sticker = null;
  if (run.sticker) {
    sticker = px(el("div", "sticker", document.body, run.sticker), G.sticker);
    box(sticker, cx + side - sticker.offsetWidth + G.sticker * 0.5, cy - G.sticker * 0.9);
  }

  const info = caption(document.body, run, ix, iy, iw, G);
  return { card, img, badge, sticker, info };
});
const flash = el("div", "flash", document.body);

// everyone at once: one tile per run, then the question
const finale = finaleScene(document.body, runs, { size: plan.size, tiles: TILES, question: ["Place", "your", "vote"], cta: null, link: plan.site, pick, byEffort: oneModel });
const tiles = finale.tiles;

let gridHead = null;
let gridLogo = null;
let gridPrompt = null;
if (G.gridHead) {
  const [gx, gy, gw, gsize] = G.gridHead;
  const [glx, gly, glh] = G.gridLogo;
  gridLogo = box(logo(document.body, glh), glx, gly);
  gridLogo.classList.add("abs");
  gridHead = box(el("div", "abs headline", document.body), gx, gy, gw);
  el("span", null, gridHead, `${line1} `);
  el("span", "hl", gridHead, line2);
  fit(gridHead, gw, gsize, 40);
  const [gpx, gpy, gpw, gpsize, gplines] = G.gridPrompt;
  gridPrompt = px(box(el("div", "abs mini-prompt", document.body), gpx, gpy, gpw), gpsize);
  gridPrompt.style.webkitLineClamp = String(gplines);
  gridPrompt.textContent = plan.prompt;
}

// ---- drawing ------------------------------------------------------------------------------------------------------

// a glow in the run's own hue behind the card (or the middle)
function background(t, hue, behindCard) {
  glow(bg, t, hue, behindCard ? cx + side / 2 : W / 2, behindCard ? cy + side / 2 : H * 0.45, plan.size);
}

function drawRun(t, d, f, run) {
  const els = runEls[run.index];
  const enter = prog(t, 0, T.enter);
  const exit = inCubic(prog(t, d - T.exit, T.exit));
  const e = spring(enter);
  pose(els.card, {
    y: lerp(H * 0.5, 0, e) - exit * H * 0.55,
    s: lerp(0.72, 1, e) - exit * 0.12,
    r: lerp(9, 0, e),
    blur: (1 - outCubic(prog(t, 0, 0.22))) * 22 + exit * 24,
  });
  els.img.style.transform = `scale(${1.0 + 0.045 * t / d})`;
  show(els.img, frameSrc(run, Math.round(t * FPS), false));
  const textOut = outCubic(prog(t, d - T.exit - 0.05, T.exit));
  const textPose = (start, extra) => {
    const u = prog(t, start, 0.4);
    return { o: outCubic(prog(t, start, 0.2)) * (1 - textOut), y: -textOut * 40, ...extra(u) };
  };
  pose(els.badge, textPose(T.enter * 0.55, (u) => ({ s: outBack(u) * (1 - exit * 0.5), r: lerp(-30, 0, outCubic(u)), y: -exit * H * 0.55 })));
  if (els.sticker) pose(els.sticker, textPose(T.sticker, (u) => ({ s: lerp(1.9, 1, outBack(u)), r: lerp(-22, -6, outCubic(u)) + Math.sin(t * 5) * 1.5, y: -exit * H * 0.55 })));
  drawCaption(els.info, run, t, textOut, T);
  pose(flash, { o: 0.28 * (1 - prog(t, 0, 0.14)) });

  pose(chrome, { o: run.index === 0 ? outCubic(prog(t, 0, 0.3)) : 1 });
  bars.forEach((bar, i) => { bar.style.transform = `scaleX(${i < run.index ? 1 : i > run.index ? 0 : prog(t, 0, d)})`; });
  counter.textContent = `${run.num} / ${N}`;
}

function drawGrid(t, d, f, spot) {
  pose(gridHead, { o: outCubic(prog(t, 0, 0.3)), y: lerp(-30, 0, outCubic(prog(t, 0, 0.4))) });
  pose(gridLogo, { o: outCubic(prog(t, 0, 0.3)) });
  pose(gridPrompt, { o: outCubic(prog(t, 0.15, 0.3)) });
  finale.drawTiles(t, f, T.tiles, false, T);
  tiles.forEach((tile) => {
    tile.tile.classList.remove("spot");
    tile.tile.style.zIndex = tile.badge.style.zIndex = "";
  });
  if (!spot || t < spot.from) return;
  // once they have landed, a spotlight steps through the tiles: each one in turn grows while the rest dim
  const k = Math.min(N - 1, Math.floor((t - spot.from) / spot.each));
  const u = (t - spot.from - k * spot.each) / spot.each;
  const grow = outBack(clamp(u * 4)) * (1 - inCubic(prog(u, 0.8, 0.2)));
  tiles.forEach((tile, i) => {
    if (i === k) {
      pose(tile.tile, { s: 1 + 0.09 * grow });
      pose(tile.badge, { s: 1 + 0.25 * grow, x: -tile.s * 0.045 * grow, y: -tile.s * 0.045 * grow });
      tile.tile.classList.add("spot");
      tile.tile.style.zIndex = "2";
      tile.badge.style.zIndex = "3";
    } else {
      tile.tile.style.filter = `brightness(${1 - 0.45 * grow})`;
    }
  });
}

function drawFinale(t, d, f, afterGrid) {
  if (afterGrid) {
    const out = outCubic(prog(t, 0, 0.25));
    pose(gridHead, { o: 1 - out, y: -out * 40 });
    pose(gridLogo, { o: 1 - out });
    pose(gridPrompt, { o: 1 - out });
  }
  finale.draw(t, d, f, T, afterGrid);
}

const everything = [...hook.nodes, chrome, flash, gridLogo, gridHead, gridPrompt, ...finale.nodes,
  ...runEls.flatMap((r) => [r.card, r.badge, r.sticker, ...r.info.nodes])].filter(Boolean);

frames((f) => {
  const seg = SEGMENTS.findLast((s) => s.start <= f) ?? SEGMENTS[0];
  const t = (f - seg.start) / FPS;
  const d = seg.frames / FPS;
  everything.forEach(hide);
  // the cut is hidden by motion, so the colour can change with it
  background(f / FPS, seg.type === "run" ? runs[seg.run].hue : ACCENT_HUE, seg.type === "run");
  if (seg.type === "hook") hook.draw(t, d, f, T);
  else if (seg.type === "run") drawRun(t, d, f, runs[seg.run]);
  else if (seg.type === "grid") drawGrid(t, d, f, seg.spot);
  else drawFinale(t, d, f, SEGMENTS.some((s) => s.type === "grid"));
});
await ready();
