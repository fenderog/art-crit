import { el } from "../dom.js";

// Local only (`art-crit serve`): makes social-media videos of the runs being compared (video.py, SPEC.md "Social videos").
// The files are written to <repo>/videos/, never published; this panel previews them and links to download them.
const LAYOUTS = [["reveal", "Vertical · one at a time"], ["grid", "Vertical · all at once"], ["wide", "Landscape · one at a time"]];

export function videoPanel(slug, runIds) {
  const boxes = LAYOUTS.map(([id, label]) => {
    const input = el("input", { attrs: { type: "checkbox", value: id, checked: "" } });
    return { id, input, node: el("label", { class: "v2-video-opt" }, [input, label]) };
  });
  const sound = el("input", { attrs: { type: "checkbox", checked: "" } });
  const status = el("span", { class: "cover-status", attrs: { role: "status" } });
  const results = el("div", { class: "v2-video-results" });
  const button = el("button", { class: "v2-pill", text: "Make videos", attrs: { type: "button" } });

  const fail = (message) => {
    status.textContent = message;
    status.classList.add("is-error");
    button.disabled = false;
  };
  const finish = (job, state) => {
    status.textContent = "Done. Saved in the videos/ folder next to docs/ (not published).";
    results.replaceChildren(
      el("p", { class: "v2-cmp-note" }, ["Link for the post: ", el("a", { text: state.link, attrs: { href: state.link, target: "_blank", rel: "noopener noreferrer" } })]),
      ...state.files.map((name) => {
        const url = `api/video/file?job=${job}&name=${encodeURIComponent(name)}`;
        return el("figure", { class: "v2-video-item" }, [
          el("video", { attrs: { src: url, controls: "", playsinline: "", preload: "metadata" } }),
          el("figcaption", {}, [name, " · ", el("a", { text: "download", attrs: { href: url, download: name } })]),
        ]);
      }));
    button.disabled = false;
  };
  const poll = async (job) => {
    try {
      const res = await fetch(`api/video?job=${job}`, { cache: "no-store" });
      const state = await res.json();
      if (!res.ok) return fail(state.error || `HTTP ${res.status}`);
      if (state.state === "failed") return fail(`Could not make the videos: ${state.error}`);
      if (state.state === "done") return finish(job, state);
      status.textContent = `Working: ${state.step}…`;
      setTimeout(() => poll(job), 1500);
    } catch (err) {
      fail(`Lost the server: ${err.message}`);
    }
  };
  button.addEventListener("click", async () => {
    const layouts = boxes.filter((b) => b.input.checked).map((b) => b.id);
    if (!layouts.length) return fail("Pick at least one format.");
    button.disabled = true;
    status.classList.remove("is-error");
    status.textContent = "Starting…";
    results.replaceChildren();
    try {
      const res = await fetch(`api/video?p=${encodeURIComponent(slug)}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ runs: runIds, layouts, sound: sound.checked }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) return fail(body.error || `HTTP ${res.status}`);
      poll(body.job);
    } catch (err) {
      fail(err.message);
    }
  });
  return el("section", { class: "v2-video" }, [
    el("h2", { text: "Make social videos" }),
    el("p", { class: "v2-cmp-note", text: "Local only. One animated video per format: a hook with the prompt, each run with its model, effort, time and cost, then \"Which one wins?\". Games and 3D models are recorded and every frame is drawn in Chrome, so it takes a minute or two." }),
    el("div", { class: "v2-video-opts" }, [...boxes.map((b) => b.node), el("label", { class: "v2-video-opt" }, [sound, "Sound"]), button, status]),
    results,
  ]);
}
