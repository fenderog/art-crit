// Community votes: a heart per user per result, and one gold, silver and bronze medal per user per page, from
// visitors signed in with GitHub (adr/0022). The API (cloudflare/votes.mjs) exists only on the published site, so
// everywhere else `loadVotes()` answers null and no vote controls are drawn. These are separate from the page
// owner's own ranking (runs.js), which keeps its own chips.

import { el } from "./dom.js";

const MEDALS = [
  { key: "gold", icon: "🥇", name: "gold" },
  { key: "silver", icon: "🥈", name: "silver" },
  { key: "bronze", icon: "🥉", name: "bronze" },
];
const LOAD_TIMEOUT_MS = 4000; // a slow vote API must never hold the page back

// The votes of one page as a small store, or null when there is no vote API here or it doesn't answer.
export async function loadVotes(slug) {
  if (!slug) return null;
  const listeners = new Set();
  const store = {
    user: null, totals: {}, mine: null,
    // Sign-in leaves the site and comes back to this very page.
    loginUrl: `api/login?return=${encodeURIComponent(location.pathname + location.search + location.hash)}`,
    watch: (fn) => listeners.add(fn),
    apply(data) {
      store.user = data.user;
      store.totals = data.totals;
      store.mine = data.mine;
      for (const fn of [...listeners]) if (fn() === false) listeners.delete(fn);
    },
    async refresh() {
      const data = await request(`api/votes?p=${encodeURIComponent(slug)}`);
      if (data) store.apply(data);
      return data;
    },
    async heart(run, on) { return write("heart", { run, on }); },
    async medal(medal, run) { return write("medal", { medal, run }); },
    async logout() {
      await fetch("api/logout", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      await store.refresh();
    },
  };
  async function write(what, body) {
    const res = await fetch(`api/${what}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ p: slug, ...body }) });
    if (res.status === 401) await store.refresh(); // the session ended: show the signed-out state
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `HTTP ${res.status}`);
    store.apply(await res.json());
  }
  return (await store.refresh()) ? store : null;
}

// GET json from the vote API; null for anything that isn't its answer (a static host's 404 or index.html, a timeout).
async function request(url) {
  try {
    const res = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(LOAD_TIMEOUT_MS) });
    if (!res.ok) return null;
    const data = await res.json();
    return data && typeof data.totals === "object" && data.totals ? data : null;
  } catch {
    return null;
  }
}

// "@alice · sign out" or "Sign in with GitHub", at the right end of the site header.
export function renderAuth(store) {
  const header = document.querySelector(".site-header");
  if (!store || !header) return;
  const box = el("span", { class: "auth" });
  header.append(box);
  const draw = () => {
    box.replaceChildren(...(store.user
      ? [el("span", { text: `@${store.user.login}` }), el("button", { class: "link-button", text: "Sign out", attrs: { type: "button" }, on: { click: () => store.logout() } })]
      : [el("a", { text: "Sign in with GitHub", attrs: { href: store.loginUrl } })]));
  };
  store.watch(draw);
  draw();
}

// The "Community" row of one result: ♥ and 🥇🥈🥉 with their totals. Pressed = yours. Signed out, a click goes to
// GitHub to sign in. Every bar of the page redraws when any vote changes, since a medal moves between results.
export function voteBar(store, runId) {
  const note = el("span", { class: "vote-note", attrs: { role: "status" } });
  const heart = voteButton("vote vote-heart");
  const medals = MEDALS.map((m) => ({ ...m, button: voteButton("vote vote-medal") }));
  const bar = el("div", { class: "votes", attrs: { role: "group", "aria-label": "Community votes" } }, [
    el("span", { class: "votes-label", text: "Community" }),
    heart, ...medals.map((m) => m.button), note,
  ]);

  const act = (button, run) => async (e) => {
    e.stopPropagation();
    if (!store.user) {
      location.assign(store.loginUrl);
      return;
    }
    button.disabled = true;
    note.textContent = "";
    try {
      await run();
    } catch (err) {
      note.textContent = `not saved: ${err.message}`;
    }
    button.disabled = false;
  };

  const paint = () => {
    const total = store.totals[runId] ?? { hearts: 0, gold: 0, silver: 0, bronze: 0 };
    const mine = store.mine ?? { hearts: [], gold: null, silver: null, bronze: null };
    const hearted = mine.hearts.includes(runId);
    fill(heart, hearted ? "♥" : "♡", total.hearts, hearted);
    heart.title = !store.user ? "Sign in with GitHub to vote" : hearted ? "Take back your heart" : "Give this result a heart";
    heart.setAttribute("aria-label", `Hearts: ${total.hearts}${hearted ? ", including yours" : ""}`);
    heart.onclick = act(heart, () => store.heart(runId, !hearted));
    for (const m of medals) {
      const placed = mine[m.key] === runId;
      fill(m.button, m.icon, total[m.key], placed);
      m.button.classList.toggle("has", total[m.key] > 0);
      m.button.title = !store.user ? "Sign in with GitHub to vote"
        : placed ? `Take back your ${m.name} medal`
        : mine[m.key] ? `Move your ${m.name} medal here` : `Give this result your ${m.name} medal`;
      m.button.setAttribute("aria-label", `${m.name} medals: ${total[m.key]}${placed ? ", including yours" : ""}`);
      m.button.onclick = act(m.button, () => store.medal(m.key, placed ? null : runId));
    }
  };
  paint();
  store.watch(() => bar.isConnected ? paint() : false); // false = this bar was redrawn away: stop listening
  return bar;
}

function voteButton(className) {
  return el("button", { class: className, attrs: { type: "button" } }, [el("span", { class: "vote-icon" }), el("span", { class: "vote-n" })]);
}

function fill(button, icon, count, pressed) {
  button.setAttribute("aria-pressed", String(pressed));
  button.querySelector(".vote-icon").textContent = icon;
  button.querySelector(".vote-n").textContent = count ? String(count) : "";
}
