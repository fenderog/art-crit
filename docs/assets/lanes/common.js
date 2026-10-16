// Shared bits of the lanes pages (ADR-0029): the sign-in pill, the final-prompt dialog and the offline vote row.

import { el } from "../dom.js";

const REF_IMAGE = /\.(png|jpe?g|gif|webp|avif|svg)$/i;

// "Sign in with GitHub to vote" (or "@alice · Sign out") at the right end of the header.
export function headerAuth(store) {
  const header = document.querySelector(".site-header");
  if (!store || !header) return;
  const box = el("span", { class: "auth" });
  header.append(box);
  const draw = () => {
    box.replaceChildren(...(store.user
      ? [el("span", { text: `@${store.user.login}` }), el("button", { class: "link-button", text: "Sign out", attrs: { type: "button" }, on: { click: () => store.logout() } })]
      : [el("a", { text: "Sign in with GitHub to vote", attrs: { href: store.loginUrl } })]));
  };
  store.watch(draw);
  draw();
}

// The full brief each run received, as a modal <dialog> (focus trap, Esc and backdrop click close it), with the
// page's reference images underneath. Returns { open }.
export function promptDialog(page, slug) {
  const text = page.final_prompt || page.prompt || "";
  const refs = (page.references || []).filter((name) => REF_IMAGE.test(name));
  const dlg = el("dialog", { class: "v2-dialog", attrs: { "aria-labelledby": "v2-dialog-title" } }, [
    el("div", { class: "v2-dialog-head" }, [
      el("div", {}, [
        el("h2", { text: "Final prompt", attrs: { id: "v2-dialog-title" } }),
        el("p", { text: "The full brief each run received" }),
      ]),
      el("button", { class: "v2-icon-btn", text: "×", attrs: { type: "button", "aria-label": "Close" }, on: { click: () => dlg.close() } }),
    ]),
    el("div", { class: "v2-dialog-body" }, [
      el("pre", { class: "v2-prompt-text", text }),
      refs.length ? el("div", { class: "v2-refs" }, [
        el("h3", { text: "Reference" }),
        ...refs.map((name) => el("img", { attrs: { src: `data/${encodeURIComponent(slug)}/references/${encodeURIComponent(name)}`, alt: `Reference: ${name}`, loading: "lazy" } })),
      ]) : null,
    ]),
  ]);
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); }); // a click on the backdrop
  document.body.append(dlg);
  return { open: () => dlg.showModal() };
}

export const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

// Where there is no vote API (art-crit serve, a plain static host) the row still shows, inactive, so the card keeps its layout.
export function offlineVotes() {
  const b = (icon, name) => el("button", { class: "vote", text: icon, attrs: { type: "button", disabled: "", "aria-label": name, title: "Voting works on the published site" } });
  return el("div", { class: "votes is-offline", attrs: { role: "group", "aria-label": "Votes (not available here)" } }, [
    el("span", { class: "votes-label", text: "Your vote:" }), b("♡", "Heart"), b("🥇", "Gold"), b("🥈", "Silver"), b("🥉", "Bronze"),
  ]);
}
