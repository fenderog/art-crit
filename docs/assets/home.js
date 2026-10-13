import { el, getJSON, showMessage } from "./dom.js";
import { modelParts, vendorOf, vendorName, vendorMark } from "./runs.js";
import { kindUi } from "./output.js";

const cards = document.getElementById("cards");

try {
  const pages = await getJSON("data/pages.json");
  if (!pages.length) {
    showMessage(cards, "No pages imported yet.");
  } else {
    for (const p of pages) cards.append(renderCard(p));
  }
} catch (err) {
  showMessage(cards.parentElement, `Could not load pages: ${err.message}`, "error");
}

function renderCard(p) {
  const thumb = p.thumb
    ? el("img", { class: p.kind === "media" ? "thumb thumb-contain" : "thumb", attrs: { src: p.thumb, alt: "", loading: "lazy" } })
    : el("div", { class: "thumb-ph", text: "no preview" });
  const models = p.models || [];
  const updated = p.updated ? new Date(p.updated) : null;
  const date = updated && !Number.isNaN(updated.getTime())
    ? el("span", { text: updated.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }), attrs: { title: `updated ${updated.toLocaleString()}` } })
    : null;
  return el("a", { class: "card", attrs: { href: `page.html?p=${encodeURIComponent(p.slug)}` } }, [
    el("div", { class: "card-media" }, [thumb, el("span", { class: "kind-chip", text: kindUi(p.kind).label, attrs: { "data-kind": p.kind } })]),
    el("div", { class: "card-body" }, [
      el("div", { class: "card-title", text: p.title }),
      vendorIcons(models),
      el("div", { class: "card-foot card-meta" }, [
        el("span", { text: `${p.n_runs} run${p.n_runs === 1 ? "" : "s"}` }),
        date,
      ]),
    ]),
  ]);
}

// One small icon per vendor (OpenRouter's, or its initial in its hue); hovering names the vendor and its models here.
function vendorIcons(models) {
  const byVendor = new Map();
  for (const m of models) {
    const v = vendorOf(m);
    if (!byVendor.has(v)) byVendor.set(v, { model: m, names: [] });
    byVendor.get(v).names.push(modelParts(m).short);
  }
  return el("div", { class: "vendor-icons" }, [...byVendor].map(([v, { model, names }]) => vendorMark(model, `${vendorName(v)}: ${names.join(", ")}`)));
}
