// The scene `art-crit video` renders (video.py `render_layout`, ADR-0033; helpers in motion.js). Every frame is a pure function of its number:
// video.py calls `renderFrame(f)`, screenshots the page and moves on, so the motion is the same on every machine and
// never depends on how fast Chrome is. The plan (plan-<layout>.json, made by video.py) holds the size, the timeline,
// the timings and the runs. Text from runs and prompts only ever goes through textContent.

import {
  box, caption, clamp, describeRun, drawCaption, el, fit, fmtCost, fmtTime, frames, frameSrc, glow, hide, inCubic, lerp,
  loadPlan, logo, outBack, outCubic, pose, prog, px, ready, show, spring,
} from "./motion.js";

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
    head: [90, 250, 840, 150], bubble: [1000, 210, 830, 660], logo: [90, 120, 60],
    question: [60, 54, 1180, 100], cta: [60, 172, 46], url: [null, 74, 30],
  }
  : {
    card: [90, 222, 900], badge: 104, sticker: 36,
    progress: [48, 40, 984], toprow: [48, 66, 984, 24], mini: [48, 108, 984, 32, 2],
    info: [90, 1160, 900], vendor: 36, name: [124, 64], effort: 36, stats: 54,
    head: [60, 330, 960, 168], bubble: [60, 760, 960, 640], logo: [60, 180, 76],
    question: [48, 140, 984, 112], cta: [48, 278, 48], url: [null, 1598, 34],
    gridHead: [48, 120, 984, 72], gridPrompt: [48, 214, 984, 34, 3], gridLogo: [48, 44, 44],
  };

// ---- the layers ---------------------------------------------------------------------------------------------------

document.body.style.width = `${W}px`;
document.body.style.height = `${H}px`;
const bg = el("div", "layer", document.body);

// the opening
const hook = el("div", "layer", document.body);
const mosaic = el("div", "mosaic", hook);
const TILE = WIDE ? 280 : 300;
const GAP = 18;
const diag = Math.hypot(W, H);
const cols = Math.ceil(diag / (TILE + GAP)) + 1;
const rows = Math.ceil(diag / (TILE + GAP)) + 2;
box(mosaic, (W - cols * (TILE + GAP)) / 2, (H - rows * (TILE + GAP)) / 2, cols * (TILE + GAP), rows * (TILE + GAP));
mosaic.style.display = "flex";
mosaic.style.gap = `${GAP}px`;
const mosaicCols = [];
for (let c = 0; c < cols; c++) {
  const col = el("div", null, mosaic);
  col.style.display = "flex";
  col.style.flexDirection = "column";
  col.style.gap = `${GAP}px`;
  col.style.width = `${TILE}px`;
  const imgs = [];
  for (let r = 0; r < rows; r++) imgs.push({ img: el("img", null, col), run: runs[(r * 3 + c * 2) % N] });
  mosaicCols.push({ col, imgs });
}
el("div", "shade", hook);
const [lx, ly, lh] = G.logo;
const hookLogo = box(logo(hook, lh), lx, ly);
hookLogo.classList.add("abs");
const [hx, hy, hw, hsize] = G.head;
const head = box(el("div", "abs headline", hook), hx, hy, hw);
const [line1, line2] = hookLines();
const headA = el("div", null, head, line1);
const headB = el("div", "hl", head, line2);
const headSize = Math.min(fit(headA, hw, hsize, 64), fit(headB, hw, hsize, 64));
px(head, headSize);
px(headA, headSize);
px(headB, headSize);
const [bx, by, bw, bh] = G.bubble;
const bubble = box(el("div", "abs bubble", hook), bx, by, bw);
bubble.style.maxHeight = `${bh}px`;
bubble.style.padding = WIDE ? "34px 40px" : "40px 44px";
const bubbleLabel = px(el("div", "bubble-label", bubble), WIDE ? 24 : 26);
el("i", null, bubbleLabel);
bubbleLabel.append("THE PROMPT");
bubbleLabel.style.marginBottom = "22px";
const promptLen = plan.prompt.length;
const promptSize = (WIDE ? [54, 46, 38, 30] : [66, 54, 44, 36])[promptLen <= 70 ? 0 : promptLen <= 140 ? 1 : promptLen <= 260 ? 2 : 3];
const bubbleText = px(el("div", "bubble-text", bubble), promptSize);
bubbleText.style.webkitLineClamp = String(Math.floor((bh - 130) / (promptSize * 1.26)));
const typed = el("span", null, bubbleText);
const caret = el("span", "caret", bubbleText);

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
const tiles = runs.map((run, i) => {
  const [x, y, s] = TILES[i];
  const tile = box(el("div", "tile", document.body), x, y, s, s);
  tile.style.borderRadius = `${Math.round(s * 0.07)}px`;
  const img = el("img", null, tile);
  const scrim = el("div", "scrim", tile);
  scrim.style.padding = `${s * 0.2}px ${s * 0.05}px ${s * 0.045}px`;
  // one model at several levels: the level is what tells the tiles apart
  px(el("b", null, scrim, oneModel ? run.effort : run.pretty), Math.max(20, s * 0.085));
  const sub = [oneModel ? null : run.effort, run.cost ? fmtCost(run.cost) : null, run.duration_s ? fmtTime(run.duration_s) : null].filter(Boolean).join(" · ");
  px(el("span", null, scrim, sub), Math.max(16, s * 0.06));
  el("div", "ring", tile);
  const size = Math.max(54, s * 0.19);
  const badge = px(box(el("div", "num", document.body), x + s * 0.04, y + s * 0.04, size, size), size * 0.52);
  badge.textContent = String(run.num);
  return { tile, img, badge, x, y, s };
});
let crown = null;
if (pick) {
  const t = tiles[pick.index];
  crown = box(el("div", "crown", document.body), t.x + t.s / 2 - t.s * 0.17, t.y - t.s * 0.24, t.s * 0.34, t.s * 0.29);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 20");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", "M2 6l5 4 5-8 5 8 5-4-2 12H4z");
  path.setAttribute("fill", "#ffe14d");
  path.setAttribute("stroke", "#9a6b00");
  path.setAttribute("stroke-width", "1.2");
  path.setAttribute("stroke-linejoin", "round");
  svg.append(path);
  crown.append(svg);
}

const [qx, qy, qw, qsize] = G.question;
const question = box(el("div", "abs question", document.body), qx, qy, qw);
const qWords = ["Place", "your", "vote"].map((w, i) => {
  if (i) question.append(" ");
  return el("span", "word", question, w);
});
fit(question, qw, qsize, 48);
const [ctx, cty, ctsize] = G.cta;
const cta = px(box(el("div", "abs cta", document.body), ctx, cty), ctsize);
const ctaAsk = el("span", "cta-ask", cta, "on"); // "on <logo> ↓": the site's pill is below the tiles (beside them when wide)
logo(ctaAsk, Math.round(ctsize * 1.15));
ctaAsk.append(WIDE ? "→" : "↓");
const ctaPick = pick ? el("span", null, cta, `My pick: #${pick.num}. What's yours?`) : null;
if (ctaPick) {
  ctaPick.style.position = "absolute";
  ctaPick.style.left = "0";
  ctaPick.style.top = "0";
}
const [, uy, usize] = G.url;
const url = px(el("div", "abs url-pill", document.body), usize);
el("i", null, url);
url.append(plan.site);
box(url, WIDE ? W - 60 - url.offsetWidth : (W - url.offsetWidth) / 2, uy);

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

function drawHook(t, d, f) {
  const out = inCubic(prog(t, d - T.exit, T.exit));
  pose(hook, { o: 1 });
  // the wall drifts, columns in turns; it is on screen from the first frame (that frame is the cover)
  pose(mosaic, { s: 1.04 + 0.05 * t / d + out * 0.25, r: -11 });
  mosaicCols.forEach(({ col, imgs }, c) => {
    col.style.transform = `translateY(${(c % 2 ? 1 : -1) * (40 + t * 55)}px)`;
    imgs.forEach(({ img, run }) => show(img, frameSrc(run, f, true)));
  });
  const punch = outCubic(prog(t, 0, 0.35));
  pose(head, { s: lerp(1.08, 1, punch) + out * 0.2, o: 1 - out, blur: out * 14, y: -out * 80 });
  pose(hookLogo, { o: 1 - out, y: -out * 80, blur: out * 14 });
  const b = prog(t, T.bubble, 0.45);
  pose(bubble, { o: outCubic(prog(t, T.bubble, 0.2)) * (1 - out), s: lerp(0.86, 1, outBack(b)) + out * 0.1, y: lerp(60, 0, outCubic(b)) - out * 60, blur: out * 14 });
  const chars = Math.round(plan.prompt.length * prog(t, T.type_from, T.type_s));
  typed.textContent = plan.prompt.slice(0, chars);
  caret.style.opacity = chars < plan.prompt.length || Math.floor(t * 2.5) % 2 === 0 ? "1" : "0";
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

// tiles fly in one after another from `start`; with `still`, they are already in place
function drawTiles(t, f, start, still) {
  tiles.forEach((tile, i) => {
    const at = start + i * T.stagger;
    const u = still ? 1 : prog(t, at, 0.6);
    const e = spring(u);
    pose(tile.tile, { o: still ? 1 : outCubic(prog(t, at, 0.15)), y: lerp(H * 0.35, 0, e), s: lerp(0.55, 1, e), r: lerp(i % 2 ? 8 : -8, 0, e) });
    show(tile.img, frameSrc(runs[i], f, tile.s <= 560));
    const b = still ? 1 : prog(t, at + 0.25, 0.4);
    pose(tile.badge, { o: outCubic(clamp(b * 4)), s: outBack(b) });
  });
}

function drawGrid(t, d, f, spot) {
  pose(gridHead, { o: outCubic(prog(t, 0, 0.3)), y: lerp(-30, 0, outCubic(prog(t, 0, 0.4))) });
  pose(gridLogo, { o: outCubic(prog(t, 0, 0.3)) });
  pose(gridPrompt, { o: outCubic(prog(t, 0.15, 0.3)) });
  drawTiles(t, f, T.tiles, false);
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
  drawTiles(t, f, T.tiles, afterGrid);
  pose(question, { o: 1 });
  qWords.forEach((w, i) => {
    const u = prog(t, T.question + i * 0.09, 0.4);
    pose(w, { o: outCubic(clamp(u * 3)), s: lerp(0.3, 1, outBack(u)), y: lerp(40, 0, outCubic(u)) });
  });
  const c = prog(t, T.cta, 0.4);
  const swap = pick ? outCubic(prog(t, T.pick + 0.3, 0.3)) : 0;
  pose(cta, { o: outCubic(clamp(c * 2.5)), x: lerp(-40, 0, outCubic(c)) });
  pose(ctaAsk, { o: 1 - swap, y: Math.sin(t * 6) * 4 * (1 - swap) });
  if (ctaPick) pose(ctaPick, { o: swap, y: lerp(30, 0, swap) });
  pose(url, { o: outCubic(prog(t, T.cta + 0.3, 0.3)), y: lerp(30, 0, outCubic(prog(t, T.cta + 0.3, 0.4))) });
  if (crown) {
    const u = prog(t, T.pick, 0.6);
    pose(crown, { o: outCubic(clamp(u * 4)), y: lerp(-160, 0, spring(u)), r: lerp(-25, -8, spring(u)) + Math.sin(t * 3) * 3 });
    tiles[pick.index].tile.classList.toggle("pick", t >= T.pick + 0.15);
  }
}

const everything = [hook, chrome, flash, mosaic, hookLogo, gridLogo, head, bubble, question, cta, url, gridHead, gridPrompt, crown,
  ...runEls.flatMap((r) => [r.card, r.badge, r.sticker, ...r.info.nodes]),
  ...tiles.flatMap((t) => [t.tile, t.badge])].filter(Boolean);

frames((f) => {
  const seg = SEGMENTS.findLast((s) => s.start <= f) ?? SEGMENTS[0];
  const t = (f - seg.start) / FPS;
  const d = seg.frames / FPS;
  everything.forEach(hide);
  // the cut is hidden by motion, so the colour can change with it
  background(f / FPS, seg.type === "run" ? runs[seg.run].hue : ACCENT_HUE, seg.type === "run");
  if (seg.type === "hook") drawHook(t, d, f);
  else if (seg.type === "run") drawRun(t, d, f, runs[seg.run]);
  else if (seg.type === "grid") drawGrid(t, d, f, seg.spot);
  else drawFinale(t, d, f, SEGMENTS.some((s) => s.type === "grid"));
});
await ready();
