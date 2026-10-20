// The two big set pieces of the videos, shared by scene.js (`art-crit video`) and studio.js (the studio's Hook and
// Finale cards; ADR-0033, ADR-0034): the hook (a drifting wall of every run, a two-line headline, the prompt typing
// into a bubble) and the finale (every run as a numbered tile, a question, a call to vote, a crown on the owner's pick).
// Positions come from `hookGeometry` / `finaleGeometry` for the frame's size; tile boxes come from the plan.

import { box, clamp, el, fit, fmtCost, fmtTime, frameSrc, inCubic, lerp, logo, outBack, outCubic, pose, prog, px, show, spring } from "./motion.js";

const shape = ([W, H]) => (W > H ? "wide" : W < H ? "tall" : "square");

export function hookGeometry(size) {
  return {
    wide: { head: [90, 250, 840, 150], bubble: [1000, 210, 830, 660], logo: [90, 120, 60], tile: 280, label: 24, pad: "34px 40px", text: [54, 46, 38, 30] },
    tall: { head: [60, 330, 960, 168], bubble: [60, 760, 960, 640], logo: [60, 180, 76], tile: 300, label: 26, pad: "40px 44px", text: [66, 54, 44, 36] },
    square: { head: [60, 150, 960, 120], bubble: [60, 470, 960, 520], logo: [60, 60, 56], tile: 260, label: 22, pad: "30px 36px", text: [50, 42, 36, 30] },
  }[shape(size)];
}

export function finaleGeometry(size) {
  return {
    wide: { question: [60, 54, 1180, 100], cta: [60, 172, 46], url: ["right", 74, 30] },
    tall: { question: [48, 140, 984, 112], cta: [48, 278, 48], url: ["center", 1598, 34] },
    square: { question: [40, 36, 1000, 84], cta: [40, 136, 38], url: ["center", 1014, 26] },
  }[shape(size)];
}

// The hook: `lines` = the headline's two lines (the second in yellow); `prompt` = typed into a bubble (none: no bubble).
export function hookScene(parent, runs, { size, lines, prompt }) {
  const [W, H] = size;
  const G = hookGeometry(size);
  const N = runs.length;
  const root = el("div", "layer", parent);
  const mosaic = el("div", "mosaic", root);
  const TILE = G.tile;
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
  el("div", "shade", root);
  const [lx, ly, lh] = G.logo;
  const mark = box(logo(root, lh), lx, ly);
  mark.classList.add("abs");
  let [hx, hy, hw, hsize] = G.head;
  if (!prompt) hy += (G.bubble[1] - hy) * 0.6; // no bubble under it: the headline sits lower
  const head = box(el("div", "abs headline", root), hx, hy, hw);
  const headA = el("div", null, head, lines[0]);
  const headB = el("div", "hl", head, lines[1] || "");
  const headSize = Math.min(fit(headA, hw, hsize, 64), fit(headB, hw, hsize, 64));
  for (const node of [head, headA, headB]) px(node, headSize);
  let bubble = null;
  let typed = null;
  let caret = null;
  if (prompt) {
    const [bx, by, bw, bh] = G.bubble;
    bubble = box(el("div", "abs bubble", root), bx, by, bw);
    bubble.style.maxHeight = `${bh}px`;
    bubble.style.padding = G.pad;
    const label = px(el("div", "bubble-label", bubble), G.label);
    el("i", null, label);
    label.append("THE PROMPT");
    label.style.marginBottom = "22px";
    const n = prompt.length;
    const size = G.text[n <= 70 ? 0 : n <= 140 ? 1 : n <= 260 ? 2 : 3];
    const text = px(el("div", "bubble-text", bubble), size);
    text.style.webkitLineClamp = String(Math.floor((bh - 130) / (size * 1.26)));
    typed = el("span", null, text);
    caret = el("span", "caret", text);
  }

  // T = the plan's timings (bubble, type_from, type_s, exit); the wall is on screen from the first frame (the cover)
  function draw(t, d, f, T) {
    const out = inCubic(prog(t, d - T.exit, T.exit));
    pose(root, { o: 1 });
    pose(mosaic, { s: 1.04 + 0.05 * t / d + out * 0.25, r: -11 });
    mosaicCols.forEach(({ col, imgs }, c) => {
      col.style.transform = `translateY(${(c % 2 ? 1 : -1) * (40 + t * 55)}px)`;
      imgs.forEach(({ img, run }) => show(img, frameSrc(run, f, true)));
    });
    const punch = outCubic(prog(t, 0, 0.35));
    pose(head, { s: lerp(1.08, 1, punch) + out * 0.2, o: 1 - out, blur: out * 14, y: -out * 80 });
    pose(mark, { o: 1 - out, y: -out * 80, blur: out * 14 });
    if (!bubble) return;
    const b = prog(t, T.bubble, 0.45);
    pose(bubble, { o: outCubic(prog(t, T.bubble, 0.2)) * (1 - out), s: lerp(0.86, 1, outBack(b)) + out * 0.1, y: lerp(60, 0, outCubic(b)) - out * 60, blur: out * 14 });
    const chars = Math.round(prompt.length * prog(t, T.type_from, T.type_s));
    typed.textContent = prompt.slice(0, chars);
    caret.style.opacity = chars < prompt.length || Math.floor(t * 2.5) % 2 === 0 ? "1" : "0";
  }
  return { draw, nodes: [root, mosaic, mark, head, bubble].filter(Boolean) };
}

// The finale. `tiles` = [x, y, side] per run; `question` = its words; `cta` = the line under it (null: "on <logo> ↓");
// `link` = the pill's text (empty: none); `pick` = the run the crown lands on (or null); `byEffort` = label tiles by
// effort (every run is one model).
export function finaleScene(parent, runs, { size, tiles: boxes, question: words, cta, link, pick, byEffort }) {
  const [W] = size;
  const G = finaleGeometry(size);
  const tiles = runs.map((run, i) => {
    const [x, y, s] = boxes[i];
    const tile = box(el("div", "tile", parent), x, y, s, s);
    tile.style.borderRadius = `${Math.round(s * 0.07)}px`;
    const img = el("img", null, tile);
    const scrim = el("div", "scrim", tile);
    scrim.style.padding = `${s * 0.2}px ${s * 0.05}px ${s * 0.045}px`;
    px(el("b", null, scrim, byEffort ? run.effort : run.pretty), Math.max(20, s * 0.085));
    const sub = [byEffort ? null : run.effort, run.cost ? fmtCost(run.cost) : null, run.duration_s ? fmtTime(run.duration_s) : null].filter(Boolean).join(" · ");
    px(el("span", null, scrim, sub), Math.max(16, s * 0.06));
    el("div", "ring", tile);
    const size = Math.max(54, s * 0.19);
    const badge = px(box(el("div", "num", parent), x + s * 0.04, y + s * 0.04, size, size), size * 0.52);
    badge.textContent = run.label ?? String(run.num);
    return { tile, img, badge, x, y, s, run };
  });
  let crown = null;
  if (pick) {
    const t = tiles[pick.index];
    crown = box(el("div", "crown", parent), t.x + t.s / 2 - t.s * 0.17, t.y - t.s * 0.24, t.s * 0.34, t.s * 0.29);
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
  const question = box(el("div", "abs question", parent), qx, qy, qw);
  const qWords = words.map((w, i) => {
    if (i) question.append(" ");
    return el("span", "word", question, w);
  });
  fit(question, qw, qsize, 48);
  const [ctx, cty, ctsize] = G.cta;
  const ctaNode = px(box(el("div", "abs cta", parent), ctx, cty), ctsize);
  let ctaAsk;
  if (cta) ctaAsk = el("span", null, ctaNode, cta);
  else {
    ctaAsk = el("span", "cta-ask", ctaNode, "on"); // "on <logo> ↓": the site's pill is below the tiles (beside them when wide)
    logo(ctaAsk, Math.round(ctsize * 1.15));
    ctaAsk.append(W > size[1] ? "→" : "↓");
  }
  const ctaPick = pick ? el("span", null, ctaNode, `My pick: #${pick.label ?? pick.num}. What's yours?`) : null;
  if (ctaPick) {
    ctaPick.style.position = "absolute";
    ctaPick.style.left = "0";
    ctaPick.style.top = "0";
  }
  let url = null;
  if (link) {
    const [where, uy, usize] = G.url;
    url = px(el("div", "abs url-pill", parent), usize);
    el("i", null, url);
    url.append(link);
    box(url, where === "right" ? W - 60 - url.offsetWidth : (W - url.offsetWidth) / 2, uy);
  }

  // tiles fly in one after another from `start`; with `still`, they are already in place
  function drawTiles(t, f, start, still, T) {
    tiles.forEach((tile, i) => {
      const at = start + i * T.stagger;
      const u = still ? 1 : prog(t, at, 0.6);
      const e = spring(u);
      pose(tile.tile, { o: still ? 1 : outCubic(prog(t, at, 0.15)), y: lerp(size[1] * 0.35, 0, e), s: lerp(0.55, 1, e), r: lerp(i % 2 ? 8 : -8, 0, e) });
      show(tile.img, frameSrc(tile.run, f, tile.s <= 560));
      const b = still ? 1 : prog(t, at + 0.25, 0.4);
      pose(tile.badge, { o: outCubic(clamp(b * 4)), s: outBack(b) });
    });
  }

  function draw(t, d, f, T, still = false) {
    drawTiles(t, f, T.tiles, still, T);
    pose(question, { o: 1 });
    qWords.forEach((w, i) => {
      const u = prog(t, T.question + i * 0.09, 0.4);
      pose(w, { o: outCubic(clamp(u * 3)), s: lerp(0.3, 1, outBack(u)), y: lerp(40, 0, outCubic(u)) });
    });
    const c = prog(t, T.cta, 0.4);
    const swap = pick ? outCubic(prog(t, T.pick + 0.3, 0.3)) : 0;
    pose(ctaNode, { o: outCubic(clamp(c * 2.5)), x: lerp(-40, 0, outCubic(c)) });
    pose(ctaAsk, { o: 1 - swap, y: Math.sin(t * 6) * 4 * (1 - swap) });
    if (ctaPick) pose(ctaPick, { o: swap, y: lerp(30, 0, swap) });
    if (url) pose(url, { o: outCubic(prog(t, T.cta + 0.3, 0.3)), y: lerp(30, 0, outCubic(prog(t, T.cta + 0.3, 0.4))) });
    if (crown) {
      const u = prog(t, T.pick, 0.6);
      pose(crown, { o: outCubic(clamp(u * 4)), y: lerp(-160, 0, spring(u)), r: lerp(-25, -8, spring(u)) + Math.sin(t * 3) * 3 });
      tiles[pick.index].tile.classList.toggle("pick", t >= T.pick + 0.15);
    }
  }
  return {
    tiles, draw, drawTiles,
    nodes: [crown, question, ctaNode, url, ...tiles.flatMap((t) => [t.tile, t.badge])].filter(Boolean),
  };
}
