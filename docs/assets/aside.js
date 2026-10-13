// The details sidebar of page.html and run.html (#page-layout, #page-aside, #aside-toggle, #aside-close,
// #aside-backdrop). Wide screens: beside the main column, open unless the viewer closed it (remembered in
// localStorage, shared by both pages). Narrow screens: a drawer over the page, closed until opened.

const ASIDE_KEY = "art-crit.aside"; // "closed" once the viewer hides the details sidebar on a wide screen

export function setupAside() {
  const layout = document.getElementById("page-layout");
  const btn = document.getElementById("aside-toggle");
  const narrow = matchMedia("(max-width: 1023px)");
  let closed = false;
  try { closed = localStorage.getItem(ASIDE_KEY) === "closed"; } catch {}
  let drawer = false;
  const update = () => {
    const open = narrow.matches ? drawer : !closed;
    layout.dataset.aside = open ? "open" : "closed";
    btn.setAttribute("aria-expanded", String(open));
    btn.title = open ? "Hide details" : "Show details";
  };
  const toggle = (open) => {
    if (narrow.matches) drawer = open;
    else {
      closed = !open;
      try { localStorage.setItem(ASIDE_KEY, closed ? "closed" : "open"); } catch {}
    }
    update();
  };
  btn.addEventListener("click", () => toggle(layout.dataset.aside !== "open"));
  document.getElementById("aside-close").addEventListener("click", () => { toggle(false); btn.focus(); });
  document.getElementById("aside-backdrop").addEventListener("click", () => toggle(false));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && narrow.matches && drawer) toggle(false); });
  narrow.addEventListener("change", () => { drawer = false; update(); });
  update();
}
