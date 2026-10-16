// Shared run cards for page.html's model rows and compare.html's wrapping grid.

import { el } from "./dom.js";
import { fmtDuration, fmtCost, fmtNum, fmtDate } from "./fmt.js";
import { runDir, harnessLabel, stateBadge, effortPill, prettyModelLabel, runUrl, LOWER_IS_BETTER, isComplete, byRankThenModel, rankChip, vendorOptions, groupByVendor, bestSets, playUrl, byModelThenEffort } from "./runs.js";
import { outputBadge, outputOk, renderOutput } from "./output.js";
import { selectBox } from "./selection.js";
import { voteBar } from "./votes.js";

const FEW = 4; // with `fillFew`, up to this many runs are equal columns filling the page

// Draws `runs` into `container`: ranked runs first, then by model. From `groupFrom` runs up, and when they span
// several vendors, there is one labelled grid per vendor; fewer are one flat grid. The ★ best values compare all
// of `runs`. `selection` adds a checkbox to every card, `dense` makes narrower cards, `fillFew` stretches 2-4 runs
// across the page, `votes` (votes.js) adds the community hearts and medals.
export function renderRunGrid(container, slug, runs, { groupFrom, selection = null, dense = false, fillFew = false, votes = null }) {
  const sorted = [...runs].sort(byRankThenModel);
  const best = bestSets(sorted);
  const grid = (list, extra) => el("div", { class: `compare-columns${dense ? " is-dense" : ""}${extra ? " is-few" : ""}`, style: extra }, list.map((r) => runCard(slug, r, best, selection, votes)));
  const groups = groupByVendor(sorted);
  if (sorted.length < groupFrom || groups.length < 2) {
    const few = fillFew && sorted.length > 1 && sorted.length <= FEW;
    container.replaceChildren(grid(sorted, few ? { "--cols": String(sorted.length), "--cols-mid": String(Math.min(sorted.length, 2)) } : null));
    return;
  }
  container.replaceChildren(...groups.map((g) =>
    el("section", { class: "vendor-group", ...vendorOptions(g.runs[0].model), attrs: { ...vendorOptions(g.runs[0].model).attrs, "aria-label": g.name } }, [
      el("h2", { class: "vendor-head" }, [
        el("span", { class: "vendor-name", text: g.name }),
        el("span", { class: "vendor-count", text: `${g.runs.length} run${g.runs.length === 1 ? "" : "s"}` }),
      ]),
      grid(g.runs),
    ])
  ));
}

// One horizontally scrolling row per exact model id (routes stay distinct). Rows follow their best rank,
// then model id; within a row effort always increases, even when a higher effort has a better rank.
export function renderModelRows(container, slug, runs, { selection = null, votes = null } = {}) {
  const groups = new Map();
  for (const r of [...runs].sort(byRankThenModel)) {
    if (!groups.has(r.model)) groups.set(r.model, []);
    groups.get(r.model).push(r);
  }
  const best = bestSets(runs);
  container.replaceChildren(...[...groups].map(([model, list]) => {
    const opts = vendorOptions(model);
    return el("section", { class: "model-row", ...opts, attrs: { ...opts.attrs, "aria-label": model } }, [
      el("div", { class: "model-row-head" }, [
        el("h2", {}, [prettyModelLabel(model)]),
        el("span", { class: "model-row-count", text: `${list.length} run${list.length === 1 ? "" : "s"}` }),
      ]),
      el("div", { class: "model-results", attrs: { tabindex: "0", role: "region", "aria-label": `${model} results, scroll for more runs` } },
        list.sort(byModelThenEffort).map((r) => runCard(slug, r, best, selection, votes, { grouped: true }))),
    ]);
  }));
}

// Starts every game at once by pressing each card's play overlay. Each sandboxed game has its own opaque origin,
// so each downloads and runs its own copy of the engine. The button hides when there is nothing to play (media
// pages, or `container` hidden) and disables once everything runs. Returns the function to call after a redraw.
export function setupPlayAll(btn, container) {
  const update = () => {
    btn.hidden = container.hidden || !container.querySelector(".game-frame");
    btn.disabled = !container.querySelector("[data-play]");
  };
  btn.addEventListener("click", () => {
    for (const overlay of container.querySelectorAll("[data-play]")) overlay.click();
    update();
  });
  container.addEventListener("click", () => setTimeout(update)); // a game started from its own overlay
  update();
  return update;
}

// "pi 0.87.1 · 1m 5s · 29,343 tokens · $0.0037", with the best values among the shown runs starred.
function metricsLine(r, best) {
  const m = r.metrics || {};
  const line = el("div", { class: "compare-metrics" }, [el("span", { class: "harness-label", text: harnessLabel(r) })]);
  const part = (key, value, suffix) => {
    const isBest = best[key] && best[key].has(r.id);
    line.append(
      el("span", { class: "sep", text: "·" }),
      el("span", { class: isBest ? "is-best" : null, attrs: isBest ? { title: LOWER_IS_BETTER[key] } : {} }, [el("b", { text: `${isBest ? "★ " : ""}${value}` }), suffix]),
    );
  };
  part("duration_ms", fmtDuration(m.duration_ms), "");
  part("tokens_total", fmtNum(m.tokens_total), " tokens");
  part("cost_usd", fmtCost(m.cost_usd, m.cost_estimated, m.cost_estimate_proxy), "");
  return line;
}

export function runCard(slug, r, best, selection = null, votes = null, { grouped = false } = {}) {
  const base = runDir(slug, r.id);
  const sb = stateBadge(r) || outputBadge(r);
  // ↗ opens the run alone in a popup window, through the sandboxed play.html (never the raw entry URL)
  const url = playUrl(slug, r.id);
  const pop = outputOk(r) ? el("a", {
    class: "popout", text: "↗",
    attrs: { href: url, target: "_blank", rel: "noopener", title: "Open in its own window", "aria-label": `Open ${r.model} ${r.effort} in its own window` },
    on: { click: (e) => { e.preventDefault(); window.open(url, "_blank", "popup,noopener,width=1280,height=800"); } },
  }) : null;
  const heading = [
    el("span", { class: "card-title" }, [selection ? selectBox(r, selection) : null, el("a", { class: "card-model", attrs: { href: runUrl(slug, r.id), title: grouped ? `${r.model} · ${r.effort} · ${fmtDate(r.started_at)}` : r.model } }, [grouped ? "Details →" : prettyModelLabel(r.model)])]),
    el("span", { class: "card-tags" }, [rankChip(r.rank), r.rank != null ? " " : null, effortPill(r.effort), sb ? " " : null, sb, pop ? " " : null, pop]),
  ];
  // The vote row shares the metrics row: a card is exactly three grid rows (heading, output, metrics), see .compare-col.
  const meta = votes ? el("div", { class: "compare-meta" }, [metricsLine(r, best), voteBar(votes, r.id)]) : metricsLine(r, best);
  const body = el("div", { class: "compare-body" });
  const errors = grouped ? meta : body; // diagnostics never displace a fixed-size preview in model rows
  if (r.error) errors.append(el("p", { class: "run-error", text: r.error }));
  for (const node of renderOutput(r, base, { compact: true, href: runUrl(slug, r.id) })) {
    (grouped && node.classList.contains("run-error") ? errors : body).append(node);
  }
  return el("div", { class: isComplete(r) ? "compare-col" : "compare-col is-failed", ...vendorOptions(r.model) }, [el("h3", {}, heading), body, meta]);
}
