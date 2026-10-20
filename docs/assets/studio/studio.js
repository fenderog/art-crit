// The video studio (studio.html, local only: `art-crit serve`; SPEC.md "Video studio", ADR-0034). Pick a template, fill
// its slots with runs from any page, put text cards between them, preview the timing, and render. The choices come
// from the server (GET api/studio = studio.catalog()), and so does the timeline (POST api/studio/plan), so the preview
// and the render never disagree. Run data and card text only ever reach the page through textContent.

import { el, getJSON } from "../dom.js";
import { EFFORTS, effortIndex, isFailed, localFeature, modelParts, prettyModelName, runDir, vendorName, vendorOf, vendorOptions } from "../runs.js";

const main = document.getElementById("main");
const STORE = "art-crit:studio";
const PREVIEW_WIDTH = { duel: 780, lineup: 820, wipe: 780, ladder: 360, countdown: 360, montage: 580 };
const MINI_COLS = { duel: 2, wipe: 2, ladder: 2, countdown: 1, montage: 3 };

let C; // the catalog
const RUNS = new Map(); // "<slug>/<run id>" -> a run the picker offers
let PAGES = [];
let PLAN = null; // the server's timeline for the current spec
let S; // what is saved between visits: the spec, minus nothing
const ui = { editCard: null, picker: null, pos: 0, playing: false, speed: 1, filters: { page: "all", types: new Set(), vendors: new Set(), efforts: new Set() } };

// ---- state --------------------------------------------------------------------------------------------------------

function defaults() {
  const card = (id, type) => ({ id, type, heading: C.cards[type].heading, sub: C.cards[type].sub, link: C.cards[type].link || "", look: C.cards[type].look, secs: 3, at: atFor(type, 2) });
  return { tpl: "duel", counts: {}, slots: {}, cards: [card("c1", "title"), card("c2", "vote")], nextCard: 3, still: 3, sync: "together", music: "upbeat", labels: true, metrics: false, wipe: 50 };
}
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || "null");
    if (saved && C.templates[saved.tpl]) return { ...defaults(), ...saved };
  } catch { /* a private window, or nothing saved */ }
  return defaults();
}
function save() {
  try { localStorage.setItem(STORE, JSON.stringify(S)); } catch { /* not kept: fine */ }
}

const tpl = () => C.templates[S.tpl];
const slotCount = () => (tpl().counts ? (tpl().counts.includes(S.counts[S.tpl]) ? S.counts[S.tpl] : tpl().counts[0]) : tpl().labels.length);
const labels = () => (tpl().counts ? Array.from({ length: slotCount() }, (_, i) => String(i + 1)) : tpl().labels);
const units = () => (tpl().together ? 1 : slotCount());
const picks = () => Array.from({ length: slotCount() }, (_, i) => (S.slots[S.tpl] || [])[i] || null);
const runOf = (ref) => (ref ? RUNS.get(`${ref.page}/${ref.run}`) || null : null);
function atFor(type, n) {
  const at = C.cards[type].at;
  return at === "middle" ? Math.floor(n / 2) : at;
}
function spec() {
  return { template: S.tpl, count: slotCount(), slots: picks(), cards: S.cards, still: S.still, sync: S.sync, music: S.music,
    labels: S.labels, metrics: S.metrics, wipe: S.wipe };
}

// ---- runs ---------------------------------------------------------------------------------------------------------

// image | video | model | game | web, the way studio.slot_type decides it
function typeOf(run) {
  const items = run.output?.items || [];
  if (!items.length) return run.kind === "godot" ? "game" : "web";
  if (items.some((i) => i.type === "video")) return "video";
  return items.some((i) => i.type === "model") ? "model" : "image";
}

async function loadRuns() {
  PAGES = await getJSON("data/pages.json");
  const pages = await Promise.all(PAGES.map((p) => getJSON(`data/${encodeURIComponent(p.slug)}/page.json`).catch(() => null)));
  pages.forEach((page, i) => {
    if (!page) return;
    for (const run of page.runs) {
      if (isFailed(run)) continue;
      const v = vendorOf(run.model);
      RUNS.set(`${PAGES[i].slug}/${run.id}`, {
        ref: { page: PAGES[i].slug, run: run.id }, pageTitle: page.title, run, type: typeOf(run),
        model: prettyModelName(modelParts(run.model).name), vendor: vendorName(v), effort: run.effort,
        thumb: run.thumb ? `${runDir(PAGES[i].slug, run.id)}${run.thumb}` : null,
        clip: (run.output?.items || []).find((it) => it.type === "video")?.duration_s || null,
        time: run.metrics?.duration_ms ? clock(run.metrics.duration_ms / 1000) : "–",
        cost: run.metrics?.cost_usd ? `$${run.metrics.cost_usd.toFixed(3)}` : "–",
      });
    }
  });
}

const clock = (x) => `${Math.floor(x / 60)}:${String(Math.floor(x % 60)).padStart(2, "0")}`;

// ---- the server's timeline ----------------------------------------------------------------------------------------

let planTimer = null;
function replan() {
  clearTimeout(planTimer);
  planTimer = setTimeout(async () => {
    try {
      const res = await fetch("api/studio/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(spec()) });
      const body = await res.json();
      if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
      PLAN = body;
      ui.pos = Math.min(ui.pos, PLAN.total);
      planError.textContent = "";
    } catch (err) {
      planError.textContent = `Can't work out the timeline: ${err.message}`;
    }
    drawTimeline();
    drawPreview();
    drawSettings();
    if (ui.editCard) drawEditor(); // its "plays n of m" and arrows follow the new order
  }, 80);
}

function changed({ plan = true, all = false } = {}) {
  save();
  if (all) drawAll();
  if (plan) replan();
}

// ---- page structure -----------------------------------------------------------------------------------------------

const h = (tag, cls, text, children) => el(tag, { class: cls, text }, children);
const button = (cls, text, onClick, attrs = {}) => el("button", { class: cls, text, attrs: { type: "button", ...attrs }, on: { click: onClick } });
const step = (n, title, extra = []) => el("div", { class: "st-step" }, [h("span", "st-step-n", String(n)), h("h2", null, title), ...extra]);

const templatesBox = h("div", "st-templates");
const step2Info = h("span", "st-muted");
const countBox = h("div", "st-count");
const frame = h("div", "st-frame");
const wipeRow = h("label", "st-wipe");
const transport = h("div", "st-transport");
const timelineHead = h("span", "st-mono st-muted");
const segmentsBox = h("div", "st-segments");
const addCards = h("div", "st-add");
const editorBox = h("div");
const planError = h("p", "st-error", "", []);
const settings = h("aside", "st-panel st-settings");
const rendersBox = h("section", "st-renders");
const dialog = el("dialog", { class: "st-dialog", attrs: { "aria-label": "Choose a result" } });

function layout() {
  main.replaceChildren(
    el("section", { class: "st-intro" }, [
      h("h1", null, "Video studio"),
      h("p", "st-lede", "Turn results into a short video. Pick a template, fill each slot with a run from any prompt on the site: images, videos, 3D models, games and web pages all work. Then preview it and render."),
    ]),
    el("section", { class: "st-section" }, [step(1, "Choose a template"), templatesBox]),
    el("section", { class: "st-section" }, [
      step(2, "Fill the slots and preview", [step2Info, countBox]),
      el("div", { class: "st-columns" }, [
        el("div", { class: "st-left" }, [
          el("div", { class: "st-panel st-preview" }, [frame, wipeRow, transport]),
          el("div", { class: "st-panel st-timeline" }, [
            el("div", { class: "st-row" }, [h("h3", null, "Timeline"), timelineHead]),
            segmentsBox, addCards, editorBox, planError,
          ]),
        ]),
        settings,
      ]),
    ]),
    rendersBox,
  );
  document.body.append(dialog);
  buildTransport();
  buildSettings();
}

function drawAll() {
  drawTemplates();
  drawStep2();
  drawTimeline();
  drawEditor();
  drawPreview();
  drawSettings();
}

// ---- step 1: templates --------------------------------------------------------------------------------------------

function drawTemplates() {
  templatesBox.replaceChildren(...Object.entries(C.templates).map(([id, t]) => {
    const n = t.counts ? (S.counts[id] || t.counts[0]) : t.labels.length;
    const mini = el("div", { class: "st-mini" }, Array.from({ length: n }, () => h("span")));
    mini.style.aspectRatio = t.format.replace(":", " / ");
    mini.style.gridTemplateColumns = `repeat(${MINI_COLS[id] || n}, minmax(0, 1fr))`;
    return el("button", { class: "st-template", attrs: { type: "button", "aria-pressed": String(id === S.tpl) }, on: { click: () => pickTemplate(id) } }, [
      el("div", { class: "st-mini-box" }, [mini]),
      h("span", "st-template-name", t.name),
      h("span", "st-template-desc", t.desc),
      el("span", { class: "st-chips" }, [
        h("span", "st-chip", t.format),
        h("span", "st-chip", t.counts ? `${t.counts.join(" or ")} slots` : `${n} slots`),
        h("span", "st-chip", t.together ? "all at once" : "one after another"),
      ]),
    ]);
  }));
}

function pickTemplate(id) {
  stop();
  S.tpl = id;
  ui.pos = 0;
  ui.picker = null;
  changed({ all: true });
}

// ---- step 2: slots, preview, timeline, settings -------------------------------------------------------------------

function drawStep2() {
  const filled = picks().filter((p) => runOf(p)).length;
  step2Info.textContent = `${tpl().name} · ${filled} of ${slotCount()} filled`;
  countBox.replaceChildren(...(tpl().counts ? [h("span", "st-muted", "Results"), ...tpl().counts.map((n) => button("st-pill", String(n), () => {
    S.counts[S.tpl] = n;
    changed({ all: true });
  }, { "aria-pressed": String(n === slotCount()) }))] : []));
}

// The segment at time x (seconds) of the plan.
function segmentAt(x) {
  if (!PLAN?.segments.length) return null;
  return PLAN.segments.find((g) => x >= g.start && x < g.start + g.secs) || PLAN.segments[PLAN.segments.length - 1];
}
const cardById = (id) => S.cards.find((c) => c.id === id) || null;

function shownCard() {
  const edited = cardById(ui.editCard);
  if (edited && !ui.playing) return edited;
  const cur = segmentAt(ui.pos);
  return cur?.type === "card" && (ui.playing || ui.pos > 0) ? cardById(cur.card) : null;
}

// how far through its clip a moving slot is at the playhead (0..100), by the sync setting
function progressOf(i) {
  const info = PLAN?.slots[i];
  if (!info || info.type === "image") return null;
  const seg = tpl().together ? PLAN.segments.find((g) => g.type === "slots") : PLAN.segments.find((g) => g.slot === i);
  if (!seg) return 0;
  const local = Math.max(0, Math.min(ui.pos - seg.start, seg.secs));
  if (S.sync === "stretch") return (local / seg.secs) * 100;
  if (S.sync === "loop") return ((local % info.secs) / info.secs) * 100;
  return Math.min(1, local / info.secs) * 100;
}

let previewKey = "";
function drawPreview() {
  if (!C) return;
  frame.style.maxWidth = `${PREVIEW_WIDTH[S.tpl]}px`;
  frame.style.aspectRatio = tpl().format.replace(":", " / ");
  const card = shownCard();
  const cur = segmentAt(ui.pos);
  const active = !tpl().together && cur?.type === "slot" ? cur.slot : null;
  const key = JSON.stringify([S.tpl, picks(), card, S.labels, S.metrics, S.wipe, active, ui.editCard && !ui.playing]);
  if (key !== previewKey) {
    previewKey = key;
    frame.replaceChildren(card ? cardPreview(card) : slotsPreview(active));
    frame.style.background = card ? C.looks[card.look].bg : "";
  }
  frame.querySelectorAll("[data-progress]").forEach((bar) => {
    const p = progressOf(Number(bar.dataset.progress));
    bar.style.width = `${p ?? 0}%`;
  });
  drawTransport();
  segmentsBox.querySelectorAll("[data-seg]").forEach((b) => {
    const g = PLAN?.segments[Number(b.dataset.seg)];
    const on = g && (g.type === "card" ? g.card === ui.editCard : g === cur && ui.pos > 0 && !ui.editCard);
    b.classList.toggle("is-on", Boolean(on));
  });
}

function cardPreview(card) {
  const look = C.looks[card.look];
  const box = el("div", { class: "st-card-preview" }, [
    h("span", "st-card-heading", card.heading),
    card.sub ? h("span", "st-card-sub", card.sub) : null,
    card.type === "vote" && card.link ? h("span", "st-card-link", card.link) : null,
  ]);
  box.style.color = look.fg;
  box.querySelector(".st-card-heading").style.fontSize = tpl().format === "16:9" ? "30px" : "26px";
  const link = box.querySelector(".st-card-link");
  if (link) {
    link.style.background = look.chip_bg;
    link.style.color = look.chip_fg;
  }
  return box;
}

function slotButton(i, extra = {}) {
  const ref = picks()[i];
  const r = runOf(ref);
  const lab = labels()[i];
  const info = PLAN?.slots[i];
  const b = el("button", {
    class: `st-slot${r ? " is-filled" : ""}${extra.cls || ""}`,
    attrs: { type: "button", "aria-label": r ? `Slot ${lab}: ${r.model} ${r.effort}. Change` : `Slot ${lab}: choose a result` },
    on: { click: () => openPicker(i) },
  }, [
    r?.thumb ? el("img", { attrs: { src: r.thumb, alt: "", loading: "lazy" } }) : null,
    h("span", "st-slot-label", lab),
  ]);
  if (!r) {
    b.append(el("span", { class: "st-slot-empty" }, [h("span", "st-plus", "+"), extra.emptyText || "Choose a result"]));
    return b;
  }
  b.append(h("span", "st-slot-type", C.types[r.type].label), h("span", "st-slot-how", C.types[r.type].how));
  if (S.labels) {
    b.append(el("span", { class: `st-slot-caption${extra.right ? " is-right" : ""}` }, [
      el("span", { class: "st-tag" }, [`${r.model} `, h("span", "st-tag-effort", r.effort)]),
      S.metrics ? h("span", "st-tag st-mono", `${r.time} · ${r.cost}`) : null,
    ]));
  }
  if (info && info.type !== "image") {
    const bar = h("span");
    bar.dataset.progress = String(i);
    b.append(el("span", { class: "st-progress" }, [bar]));
  }
  return b;
}

function slotsPreview(active) {
  if (tpl().wipe) {
    const box = el("div", { class: "st-wipe-box" }, [0, 1].map((i) => {
      const b = slotButton(i, { cls: " st-layer", right: i === 1, emptyText: `Choose ${labels()[i]}` });
      if (i) b.style.clipPath = `inset(0 0 0 ${S.wipe}%)`;
      return b;
    }));
    const line = h("span", "st-wipe-line");
    line.style.left = `${S.wipe}%`;
    box.append(line);
    return box;
  }
  const grid = el("div", { class: "st-slots" }, picks().map((_, i) => {
    const b = slotButton(i);
    if (active !== null) b.classList.toggle(i === active ? "is-active" : "is-dim", true);
    return b;
  }));
  grid.style.gridTemplateColumns = `repeat(${tpl().together ? (MINI_COLS[S.tpl] || slotCount()) : (MINI_COLS[S.tpl] || 1)}, minmax(0, 1fr))`;
  return grid;
}

// ---- transport ----------------------------------------------------------------------------------------------------

const playBtn = button("st-play", "", () => (ui.playing ? stop() : play()), { "aria-label": "Play preview" });
const scrub = el("input", { attrs: { type: "range", min: "0", max: "1000", value: "0", "aria-label": "Preview position" } });
const clockText = h("span", "st-mono st-ink");
const speedSel = el("select", { attrs: { "aria-label": "Speed" } }, ["0.25", "0.5", "1", "2"].map((v) => el("option", { text: `${v}×`, attrs: { value: v } })));

function buildTransport() {
  speedSel.value = "1";
  speedSel.addEventListener("change", () => { ui.speed = Number(speedSel.value); });
  scrub.addEventListener("input", () => {
    stop();
    ui.editCard = null;
    ui.pos = (Number(scrub.value) / 1000) * (PLAN?.total || 0);
    drawEditor();
    drawPreview();
  });
  const stepBy = (dir) => () => {
    stop();
    ui.pos = Math.max(0, Math.min(PLAN?.total || 0, ui.pos + dir / 30));
    drawPreview();
  };
  transport.replaceChildren(
    button("st-icon", "‹", stepBy(-1), { "aria-label": "Back one frame" }),
    playBtn,
    button("st-icon", "›", stepBy(1), { "aria-label": "Forward one frame" }),
    el("label", { class: "st-scrub" }, [clockText, scrub]),
    el("label", { class: "st-inline" }, ["Speed", speedSel]),
  );
  const range = el("input", { attrs: { type: "range", min: "0", max: "100", value: String(S.wipe) } });
  range.addEventListener("input", () => {
    S.wipe = Number(range.value);
    save();
    drawPreview();
  });
  wipeRow.replaceChildren("Wipe", range);
}

function drawTransport() {
  const total = PLAN?.total || 0;
  playBtn.textContent = ui.playing ? "❚❚" : "▶";
  playBtn.setAttribute("aria-label", ui.playing ? "Pause preview" : "Play preview");
  scrub.value = String(total ? Math.round((ui.pos / total) * 1000) : 0);
  clockText.textContent = `${clock(ui.pos)} / ${clock(total)}`;
  wipeRow.hidden = !tpl().wipe;
  for (const box of [wipeRow, transport]) box.style.maxWidth = `${PREVIEW_WIDTH[S.tpl]}px`;
}

let last = 0;
function tick(now) {
  if (!ui.playing) return;
  const dt = last ? (now - last) / 1000 : 0;
  last = now;
  ui.pos += dt * ui.speed;
  if (ui.pos >= (PLAN?.total || 0)) ui.pos = 0;
  drawPreview();
  requestAnimationFrame(tick);
}
function play() {
  if (!PLAN?.total) return;
  ui.playing = true;
  ui.editCard = null;
  last = 0;
  drawEditor();
  requestAnimationFrame(tick);
  drawPreview();
}
function stop() {
  ui.playing = false;
  drawPreview();
}

// ---- timeline and cards -------------------------------------------------------------------------------------------

function segmentName(g) {
  if (g.type === "card") {
    const c = cardById(g.card);
    return `${C.cards[c?.type]?.label || "Card"}: ${c?.heading || "untitled"}`;
  }
  if (g.type === "slots") return `${slotCount()} results together`;
  const r = runOf(picks()[g.slot]);
  return `${labels()[g.slot]} · ${r ? r.model : "empty"}`;
}

function drawTimeline() {
  if (!C) return;
  timelineHead.textContent = `${clock(PLAN?.total || 0)} total`;
  segmentsBox.replaceChildren(...(PLAN?.segments || []).map((g, i) => {
    const card = g.type === "card" ? cardById(g.card) : null;
    const empty = g.type === "slot" && !runOf(picks()[g.slot]);
    const b = el("button", {
      class: `st-seg${card ? " is-card" : ""}${empty ? " is-empty" : ""}`,
      attrs: { type: "button", "aria-label": card ? `Edit the ${segmentName(g)} card` : `Jump to ${segmentName(g)}` },
      on: {
        click: () => {
          stop();
          ui.editCard = card ? card.id : null;
          ui.pos = Math.min(g.start + 0.01, PLAN.total);
          drawEditor();
          drawPreview();
        },
      },
    }, [h("span", "st-seg-name", segmentName(g)), h("span", "st-mono", `${Math.round(g.secs * 10) / 10}s`)]);
    b.dataset.seg = String(i);
    b.style.flexGrow = String(g.secs);
    if (card) {
      b.style.background = C.looks[card.look].bg;
      b.style.color = C.looks[card.look].fg;
      if (card.look === "light") b.classList.add("is-light");
    }
    return b;
  }));
  addCards.replaceChildren(h("span", "st-muted", "Add a card"), ...Object.entries(C.cards).map(([type, d]) => button("st-pill st-add-pill", `+ ${d.label}`, () => addCard(type))));
  drawStep2();
}

function addCard(type) {
  if (S.cards.length >= C.limits.cards) return;
  const d = C.cards[type];
  const card = { id: `c${S.nextCard++}`, type, heading: d.heading, sub: d.sub, link: d.link || "", look: d.look, secs: 3, at: atFor(type, units()) };
  S.cards = type === "title" ? [card, ...S.cards] : [...S.cards, card];
  stop();
  ui.editCard = card.id;
  changed();
}

// Move a card one place earlier/later in play order: past a neighbouring card (swap), or past a result block (`at`).
function moveCard(id, dir) {
  const seq = PLAN?.segments || [];
  const k = seq.findIndex((g) => g.type === "card" && g.card === id);
  const other = seq[k + dir];
  if (k < 0 || !other) return;
  const card = cardById(id);
  let cards = S.cards.filter((c) => c.id !== id);
  if (other.type === "card") {
    const j = cards.findIndex((c) => c.id === other.card);
    cards.splice(dir < 0 ? j : j + 1, 0, card);
  } else {
    const moved = { ...card, at: Math.min(card.at, units()) + dir };
    cards = dir < 0 ? [...cards, moved] : [moved, ...cards];
  }
  S.cards = cards;
  changed();
}

function updateCard(id, patch, { plan = false } = {}) {
  S.cards = S.cards.map((c) => (c.id === id ? { ...c, ...patch } : c));
  save();
  drawPreview();
  if (plan) replan();
  else drawTimeline();
}

function drawEditor() {
  const card = cardById(ui.editCard);
  if (!card) {
    editorBox.replaceChildren();
    return;
  }
  const d = C.cards[card.type];
  const seq = PLAN?.segments || [];
  const k = seq.findIndex((g) => g.type === "card" && g.card === card.id);
  const input = (tag, value, max, onInput, attrs = {}) => {
    const node = el(tag, { attrs: { maxlength: String(max), ...attrs } });
    node.value = value;
    node.addEventListener("input", () => onInput(node.value));
    return node;
  };
  const length = el("select", {}, C.seconds.map((s) => el("option", { text: `${s} seconds`, attrs: { value: String(s) } })));
  length.value = String(card.secs);
  length.addEventListener("change", () => updateCard(card.id, { secs: Number(length.value) }, { plan: true }));
  editorBox.replaceChildren(el("div", { class: "st-editor" }, [
    el("div", { class: "st-row" }, [
      h("span", "st-strong", `${d.label} card`),
      h("span", "st-muted", k >= 0 ? `plays ${k + 1} of ${seq.length}` : ""),
      h("span", "st-grow"),
      button("st-icon", "‹", () => moveCard(card.id, -1), { "aria-label": "Move the card earlier", disabled: k <= 0 ? "" : null }),
      button("st-icon", "›", () => moveCard(card.id, 1), { "aria-label": "Move the card later", disabled: k < 0 || k >= seq.length - 1 ? "" : null }),
      button("st-btn st-danger", "Delete", () => {
        S.cards = S.cards.filter((c) => c.id !== card.id);
        ui.editCard = null;
        changed();
        drawEditor();
      }),
      button("st-btn st-dark", "Done", () => {
        ui.editCard = null;
        drawEditor();
        drawPreview();
      }),
    ]),
    el("label", { class: "st-field" }, [d.heading_label, input("input", card.heading, C.limits.heading, (v) => updateCard(card.id, { heading: v }), { type: "text" })]),
    el("label", { class: "st-field" }, [el("span", {}, [`${d.sub_label} `, h("span", "st-muted", "optional")]), input("textarea", card.sub, C.limits.sub, (v) => updateCard(card.id, { sub: v }), { rows: "2" })]),
    card.type === "vote" ? el("label", { class: "st-field" }, ["Link shown on the card", input("input", card.link, C.limits.link, (v) => updateCard(card.id, { link: v }), { type: "text" })]) : null,
    el("div", { class: "st-row st-wrap-row" }, [
      el("div", { class: "st-row" }, [h("span", "st-muted", "Look"), ...Object.entries(C.looks).map(([id, look]) => {
        const swatch = h("span", "st-swatch");
        swatch.style.background = look.bg;
        return el("button", { class: "st-pill", attrs: { type: "button", "aria-pressed": String(card.look === id) }, on: { click: () => { updateCard(card.id, { look: id }); drawEditor(); } } }, [swatch, look.label]);
      })]),
      el("label", { class: "st-inline" }, ["Length", length]),
    ]),
  ]));
}

// ---- settings -----------------------------------------------------------------------------------------------------

const stillSel = el("select");
const syncSel = el("select");
const musicSel = el("select");
const labelsBox = el("input", { attrs: { type: "checkbox" } });
const metricsBox = el("input", { attrs: { type: "checkbox" } });
const motionBox = el("div", { class: "st-motion" });
const formatLine = h("div", "st-muted st-format");
const renderBtn = button("st-render", "Render video", () => render());
const renderHint = h("span", "st-muted");

function buildSettings() {
  const options = (sel, entries) => sel.replaceChildren(...entries.map(([v, text]) => el("option", { text, attrs: { value: String(v) } })));
  options(stillSel, C.seconds.map((s) => [s, `${s} seconds`]));
  options(syncSel, Object.entries(C.sync));
  options(musicSel, Object.entries(C.music));
  stillSel.addEventListener("change", () => { S.still = Number(stillSel.value); changed(); });
  syncSel.addEventListener("change", () => { S.sync = syncSel.value; save(); drawPreview(); });
  musicSel.addEventListener("change", () => { S.music = musicSel.value; save(); });
  labelsBox.addEventListener("change", () => { S.labels = labelsBox.checked; save(); drawPreview(); });
  metricsBox.addEventListener("change", () => { S.metrics = metricsBox.checked; save(); drawPreview(); });
  motionBox.replaceChildren(
    h("span", "st-strong", "Moving results"),
    h("span", "st-muted st-small", "Videos play their clip, 3D models turn on a turntable, games and web pages play as a screen recording."),
    el("label", { class: "st-field" }, ["When lengths differ", syncSel]),
  );
  settings.replaceChildren(
    h("h3", null, "Video settings"),
    el("label", { class: "st-field" }, ["Seconds for each still image", stillSel]),
    motionBox,
    el("label", { class: "st-field" }, ["Music", musicSel]),
    el("div", { class: "st-checks" }, [
      el("label", { class: "st-check" }, [labelsBox, "Label each result with model and effort"]),
      el("label", { class: "st-check" }, [metricsBox, "Add time and cost"]),
    ]),
    formatLine, renderBtn, renderHint,
  );
}

function drawSettings() {
  stillSel.value = String(S.still);
  syncSel.value = S.sync;
  musicSel.value = S.music;
  labelsBox.checked = S.labels;
  metricsBox.checked = S.metrics;
  motionBox.hidden = !(PLAN?.slots || []).some((s) => s && s.type !== "image");
  const total = clock(PLAN?.total || 0);
  formatLine.replaceChildren("Format ", h("b", null, tpl().format), " · Length ", h("b", null, total));
  const left = picks().filter((p) => !runOf(p)).length;
  renderBtn.disabled = left > 0 || rendering;
  renderHint.textContent = rendering ? "A video is being rendered; one at a time."
    : left ? `Fill every slot to render (${left} left).` : `Ready: ${total} at ${tpl().format}.`;
}

// ---- rendering ----------------------------------------------------------------------------------------------------

let rendering = false;
let jobs = []; // renders under way or failed (the server's memory)
let renders = []; // the finished videos in videos/studio/
let pollTimer = null;

async function render() {
  renderBtn.disabled = true;
  try {
    const res = await fetch("api/video", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ studio: spec() }) });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
    await pollJobs();
  } catch (err) {
    renderHint.textContent = `Could not start the render: ${err.message}`;
    renderBtn.disabled = false;
  }
}

async function pollJobs() {
  clearTimeout(pollTimer);
  try {
    ({ jobs, renders } = await getJSON("api/video/jobs"));
  } catch {
    return;
  }
  rendering = jobs.some((j) => j.state === "running");
  drawRenders();
  drawSettings();
  if (rendering) pollTimer = setTimeout(pollJobs, 1500);
}

// {name} deletes a video file, {job} dismisses a failed render
async function remove(body) {
  try {
    const res = await fetch("api/video/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `HTTP ${res.status}`);
  } catch (err) {
    renderHint.textContent = `Could not delete it: ${err.message}`;
  }
  await pollJobs();
}

function renderRow(item, state, out, actions) {
  const meta = [item.template, item.format, item.length != null ? clock(item.length) : null, item.slots ? `${item.slots} results` : null].filter(Boolean).join(" · ");
  return el("div", { class: "st-render-row" }, [
    el("div", { class: "st-row st-wrap-row" }, [
      h("span", "st-strong", item.title),
      h("span", "st-muted", meta),
      h("span", "st-grow"),
      state ? h("span", `st-state ${state[0]}`, state[1]) : null,
      ...actions,
    ]),
    item.error ? h("p", "st-error", item.error) : null,
    out,
  ]);
}

function drawRenders() {
  rendersBox.hidden = !jobs.length && !renders.length;
  const working = jobs.map((j) => renderRow(j, j.state === "running" ? ["is-running", `Rendering · ${j.step}`] : ["is-failed", "Failed"], null,
    j.state === "running" ? [] : [button("st-btn", "Dismiss", () => remove({ job: j.job }))]));
  const done = renders.map((r) => {
    const url = `api/video/file?name=${encodeURIComponent(r.name)}`;
    return renderRow(r, ["is-done", "Done"], el("div", { class: "st-render-out" }, [
      el("video", { attrs: { src: url, controls: "", playsinline: "", preload: "metadata" } }),
      el("a", { text: "Download", attrs: { href: url, download: r.name } }),
    ]), [button("st-btn st-danger", "Delete", () => {
      if (confirm(`Delete "${r.title}"? Its file (${r.name}) is removed from videos/studio/.`)) remove({ name: r.name });
    }, { "aria-label": `Delete ${r.name}` })]);
  });
  rendersBox.replaceChildren(h("h2", null, "Your renders"), el("div", { class: "st-render-list" }, [...working, ...done]));
}

// ---- the result picker --------------------------------------------------------------------------------------------

function openPicker(i) {
  stop();
  ui.picker = i;
  drawPicker();
  if (!dialog.open) dialog.showModal();
}

function setSlot(i, ref) {
  const next = picks();
  next[i] = ref;
  S.slots[S.tpl] = next;
  dialog.close();
  ui.picker = null;
  changed({ all: true });
}

function drawPicker() {
  const f = ui.filters;
  const all = [...RUNS.values()];
  const shown = all.filter((r) => (f.page === "all" || r.ref.page === f.page)
    && (!f.types.size || f.types.has(r.type)) && (!f.vendors.size || f.vendors.has(r.vendor)) && (!f.efforts.size || f.efforts.has(r.effort)));
  const current = picks()[ui.picker];
  const pills = (set, values, label) => values.map((v) => button("st-pill", label(v), () => {
    if (set.has(v)) set.delete(v);
    else set.add(v);
    drawPicker();
  }, { "aria-pressed": String(set.has(v)) }));
  const pageSel = el("select", {}, [el("option", { text: "All prompts", attrs: { value: "all" } }), ...PAGES.map((p) => el("option", { text: p.title, attrs: { value: p.slug } }))]);
  pageSel.value = f.page;
  pageSel.addEventListener("change", () => { f.page = pageSel.value; drawPicker(); });
  const vendors = [...new Set(all.map((r) => r.vendor))].sort();
  const efforts = EFFORTS.filter((e) => all.some((r) => r.effort === e));
  dialog.replaceChildren(
    el("div", { class: "st-dialog-head" }, [
      el("div", { class: "st-grow" }, [
        h("h2", null, `Choose a result for "${labels()[ui.picker]}"`),
        h("span", "st-muted", `${shown.length} results match`),
      ]),
      current ? button("st-btn", "Empty this slot", () => setSlot(ui.picker, null)) : null,
      button("st-icon", "×", () => dialog.close(), { "aria-label": "Close" }),
    ]),
    el("div", { class: "st-filters" }, [
      el("label", { class: "st-inline" }, ["Prompt", pageSel]),
      el("div", { class: "st-row" }, [h("span", "st-muted", "Type"), ...pills(f.types, Object.keys(C.types), (t) => C.types[t].label)]),
      el("div", { class: "st-row" }, [h("span", "st-muted", "Vendor"), ...pills(f.vendors, vendors, (v) => v)]),
      el("div", { class: "st-row" }, [h("span", "st-muted", "Effort"), ...pills(f.efforts, efforts, (e) => e)]),
    ]),
    el("div", { class: "st-results" }, byModel(shown).map((g) => {
      const vo = vendorOptions(g.model);
      return el("section", { class: "st-group", attrs: vo.attrs, style: vo.style }, [
        el("h3", { class: "st-group-head" }, [h("span", "st-dot"), h("span", "st-group-vendor", g.vendor), h("span", "st-group-sep", " – "), g.name,
          h("span", "st-muted st-group-count", `${g.items.length} ${g.items.length === 1 ? "run" : "runs"}`)]),
        el("div", { class: "st-group-row" }, g.items.map((r) => resultCard(r, current))),
      ]);
    })),
  );
}

// The picker's runs grouped like the page's lanes: one row per model, vendors and models by name, each row by prompt
// and then effort (low to high).
function byModel(entries) {
  const groups = new Map();
  for (const r of entries) {
    if (!groups.has(r.run.model)) {
      const { name, via } = modelParts(r.run.model);
      groups.set(r.run.model, { model: r.run.model, vendor: r.vendor, name: prettyModelName(name) + (via ? ` via ${via}` : ""), items: [] });
    }
    groups.get(r.run.model).items.push(r);
  }
  const list = [...groups.values()].sort((a, b) => a.vendor.localeCompare(b.vendor) || a.name.localeCompare(b.name));
  for (const g of list) g.items.sort((a, b) => a.pageTitle.localeCompare(b.pageTitle) || effortIndex(a.effort) - effortIndex(b.effort));
  return list;
}

function resultCard(r, current) {
  const on = current && current.page === r.ref.page && current.run === r.ref.run;
  return el("button", {
    class: `st-result${on ? " is-on" : ""}`,
    attrs: { type: "button", "aria-label": `Use ${r.model} ${r.effort} (${C.types[r.type].label}) from ${r.pageTitle}` },
    on: { click: () => setSlot(ui.picker, r.ref) },
  }, [
    el("span", { class: "st-result-pic" }, [
      r.thumb ? el("img", { attrs: { src: r.thumb, alt: "", loading: "lazy" } }) : null,
      h("span", "st-result-type", `${C.types[r.type].label}${r.clip ? ` · 0:${String(Math.round(r.clip)).padStart(2, "0")}` : ""}`),
    ]),
    el("span", { class: "st-result-text" }, [
      h("span", "st-strong st-accent-effort", r.effort),
      h("span", "st-muted st-small", r.pageTitle),
    ]),
  ]);
}
dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); }); // a click on the backdrop

// ---- start --------------------------------------------------------------------------------------------------------

// Opened from a compare page (studio.html?p=<slug>&r=a,b,c): a template that fits that many runs, filled in order.
function prefill() {
  const params = new URLSearchParams(location.search);
  const slug = params.get("p");
  const ids = (params.get("r") || "").split(",").filter(Boolean);
  if (!slug || !ids.length) return;
  const n = ids.length;
  const id = n <= 2 ? "duel" : n <= 4 ? "lineup" : n === 5 ? "countdown" : "montage";
  S.tpl = id;
  if (id === "lineup") S.counts.lineup = n;
  S.slots[id] = ids.slice(0, id === "montage" ? 6 : n).map((run) => (RUNS.has(`${slug}/${run}`) ? { page: slug, run } : null));
  history.replaceState(null, "", location.pathname);
}

async function start() {
  if (!(await localFeature("video"))) {
    main.replaceChildren(el("section", { class: "st-intro" }, [
      h("h1", null, "Video studio"),
      h("p", "st-lede", "The video studio runs on your own machine: start `uv run art-crit serve` and open studio.html there."),
    ]));
    return;
  }
  C = await getJSON("api/studio");
  await loadRuns();
  S = load();
  prefill();
  save();
  layout();
  drawAll();
  replan();
  pollJobs();
}

start().catch((err) => {
  main.replaceChildren(h("p", "st-error", `The video studio failed to load: ${err.message}`));
});
