// Local run monitor (ADR-0027): what `art-crit run` is doing on this machine right now — every batch in
// [run].dir with live metrics, the prompt, the files the agent wrote, its transcript and a Stop button
// for a running agent. `art-crit serve` only: the published site has no api/runs and shows nothing here.

import { el, getJSON, showMessage } from "./dom.js";
import { fmtBytes, fmtCost, fmtDate, fmtDateShort, fmtDuration, fmtNum } from "./fmt.js";
import { effortPill, modelParts, runUrl } from "./runs.js";
import { renderTranscript } from "./transcript.js";

const POLL_MS = 2000;
const main = document.getElementById("main");
const LOCAL = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname);
let batches = [];
let selected = null; // {batch, run}: which batch is open and which of its runs is shown
let timer = null;

// Shown when this isn't `art-crit serve` on this machine (the published site, or a plain file server).
function localOnlyNote(text) {
  main.hidden = true;
  const note = document.getElementById("local-only");
  note.hidden = false;
  showMessage(note, text);
}

// A run's state as a chip: running/queued are neutral, done is good, failed/timeout are bad (CSS).
function stateChip(row) {
  const label = { complete: "done", running: "running", queued: "queued", failed: "failed", timeout: "timeout" }[row.state] || row.state || "?";
  return el("span", { class: "monitor-state", text: label, attrs: { "data-state": row.state || "" } });
}

function summary(row) {
  if (row.state === "queued") return "waiting";
  const m = row.metrics || {};
  return [fmtDuration(m.duration_ms), fmtCost(m.cost_usd, m.cost_estimated, m.cost_estimate_proxy), `${fmtNum(m.tool_calls)} tools`]
    .filter((part) => part && part !== "–").join(" · ");
}

async function refresh() {
  let data;
  try {
    data = await getJSON("api/runs");
  } catch (err) {
    return localOnlyNote(`The run monitor needs \`art-crit serve\` on this machine (${err.message}).`);
  }
  batches = data.batches || [];
  document.getElementById("where").textContent = data.dir
    ? `${batches.length} batch${batches.length === 1 ? "" : "es"} in ${data.dir}`
    : "no [run].dir in art-crit.toml";
  if (!batches.some((b) => selected && b.batch === selected.batch)) selected = batches.length ? { batch: batches[0].batch, run: null } : null;
  drawBatches();
  await drawDetail();
  schedule();
}

// Keep polling while something is queued or running (and the tab is visible); the runner is elsewhere.
function schedule() {
  clearTimeout(timer);
  const busy = batches.some((b) => b.runs.some((r) => r.state === "queued" || r.state === "running"));
  document.getElementById("status").textContent = busy ? "live · every 2s" : "idle";
  if (busy && document.visibilityState === "visible") timer = setTimeout(refresh, POLL_MS);
}

function drawBatches() {
  const root = document.getElementById("batches");
  if (!batches.length) return root.replaceChildren(el("p", { class: "muted", text: "No batches yet." }));
  root.replaceChildren(...batches.map((b) => el("section", { class: "monitor-batch" }, [
    el("button", { class: "monitor-batch-head", attrs: { type: "button" }, on: { click: () => pick(b.batch, null) } }, [
      el("span", { class: "monitor-batch-title", text: b.title || b.prompt || b.batch }),
      el("span", { class: "muted", text: [b.page, b.kind, fmtDate(b.created)].filter(Boolean).join(" · ") }),
    ]),
    el("ul", { class: "monitor-runs" }, b.runs.map((r) => el("li", {}, [runButton(b, r)]))),
  ])));
}

function pick(batch, run) {
  selected = { batch, run };
  drawBatches();
  drawDetail();
}

function runButton(b, row) {
  const { name } = modelParts(row.model || "");
  const active = selected && selected.batch === b.batch && selected.run === row.id;
  return el("button", { class: active ? "monitor-run is-active" : "monitor-run", attrs: { type: "button", "data-state": row.state }, on: { click: () => pick(b.batch, row.id) } }, [
    stateChip(row), el("span", { class: "monitor-run-model", text: name || row.id }), effortPill(row.level),
    el("span", { class: "monitor-run-metrics muted", text: summary(row) }),
  ]);
}

async function drawDetail() {
  const root = document.getElementById("detail");
  if (!selected) return root.replaceChildren(el("p", { class: "muted", text: "Pick a batch or a run." }));
  const batch = batches.find((b) => b.batch === selected.batch);
  if (!selected.run) {
    return root.replaceChildren(el("h2", { text: batch.title || batch.prompt || batch.batch }),
      el("p", { class: "monitor-prompt", text: batch.prompt }), el("p", { class: "muted", text: `${batch.runs.length} runs · created ${fmtDate(batch.created)}` }));
  }
  let d;
  try {
    d = await getJSON(`api/run?b=${encodeURIComponent(selected.batch)}&r=${encodeURIComponent(selected.run)}`);
  } catch (err) {
    return root.replaceChildren(el("p", { class: "form-error", text: err.message }));
  }
  root.replaceChildren(...detail(d).filter(Boolean)); // el() skips nulls, replaceChildren() prints them
}

function tile(label, value) {
  return el("div", { class: "stat" }, [el("span", { class: "stat-label", text: label }), el("span", { class: "stat-value", text: value })]);
}

function tiles(row) {
  const m = row.metrics || {};
  const running = row.state === "running";
  return el("div", { class: "stat-tiles" }, [
    tile("Duration", fmtDuration(m.duration_ms)), tile("Cost", fmtCost(m.cost_usd, m.cost_estimated, m.cost_estimate_proxy)),
    tile("Tokens", fmtNum(m.tokens_total)), tile("Output tokens", fmtNum(m.tokens_output)),
    tile("Reasoning", fmtNum(m.tokens_reasoning)), tile("Tool calls", fmtNum(m.tool_calls)), tile("Turns", fmtNum(m.turns)),
    running ? tile("Last write", row.activity_ms == null ? "–" : `${fmtDuration(row.activity_ms)} ago`) : tile("Started", fmtDateShort(row.started_at)),
  ]);
}

function stopButton(d) {
  const button = el("button", { class: "btn btn-sm monitor-stop", text: "Stop", attrs: { type: "button" } });
  button.addEventListener("click", async () => {
    if (!confirm(`Stop ${d.run.id}? The agent's process is killed and the run is marked failed.`)) return;
    button.disabled = true;
    try {
      const res = await fetch("api/stop", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ batch: d.batch, run: d.run.id }) });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
      button.textContent = "stopping…";
      refresh();
    } catch (err) {
      button.disabled = false;
      alert(err.message);
    }
  });
  return button;
}

function fileList(title, files) {
  return el("div", { class: "monitor-files" }, [
    el("h3", { text: files.length ? `${title} (${files.length})` : title }),
    files.length
      ? el("ul", {}, files.map((f) => el("li", {}, [el("span", { class: "monitor-file", text: f.name }), el("span", { class: "muted", text: fmtBytes(f.bytes) })])))
      : el("p", { class: "muted", text: "nothing yet" }),
  ]);
}

function transcriptSection(d) {
  const box = el("div", { class: "monitor-transcript" });
  if (d.transcript.length) renderTranscript(box, d.transcript);
  else box.append(el("p", { class: "muted", text: "No session file yet (muse writes one when the agent exits)." }));
  return el("section", { class: "monitor-block" }, [
    el("h3", {}, [el("span", { text: "Transcript" }), d.live ? el("span", { class: "monitor-live", text: "live" }) : null]),
    el("p", { class: "muted", text: d.live
      ? "Converted from the session file while the run is still going; images and long text are left out."
      : (d.truncated ? "Only the last part is shown here; images and long text are left out." : "Images and long text are left out; open the run page for the full transcript.") }),
    box,
  ]);
}

function detail(d) {
  const row = d.run;
  const { provider, name, via } = modelParts(row.model || "");
  const published = row.published && d.page
    ? el("a", { class: "link-button", attrs: { href: runUrl(d.page, row.id) }, text: "Open run page ↗" })
    : el("span", { class: "muted", text: "not published yet" });
  return [
    el("div", { class: "monitor-head" }, [
      el("h2", {}, [el("span", { text: name || row.id }), effortPill(row.level), stateChip(row)]),
      el("span", { class: "spacer" }),
      published,
      row.state === "running" ? stopButton(d) : null,
    ]),
    el("p", { class: "muted monitor-runline", text: [via ? `${provider} · via ${via}` : provider, row.harness, row.id].filter(Boolean).join(" · ") }),
    tiles(row),
    row.error ? el("p", { class: "run-error", text: row.error }) : null,
    el("section", { class: "monitor-block" }, [
      el("details", {}, [el("summary", { text: "Prompt" }), el("p", { class: "monitor-prompt", text: d.prompt })]),
      el("details", {}, [el("summary", { text: "Brief the agent got" }), el("pre", { class: "monitor-brief", text: d.brief })]),
    ]),
    el("div", { class: "monitor-cols" }, [fileList("work/", d.files.work), fileList("output/", d.files.output)]),
    transcriptSection(d),
  ];
}

if (!LOCAL) {
  localOnlyNote("The run monitor is local only: run `uv run art-crit serve` and open it from there.");
} else {
  main.hidden = false;
  document.getElementById("refresh").addEventListener("click", refresh);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") refresh(); });
  refresh();
}
