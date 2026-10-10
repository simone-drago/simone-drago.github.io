// Abstract toggles, the rotating "Latest news", the light/dark switch, and the top bar.
document.addEventListener("DOMContentLoaded", () => {
  for (const btn of document.querySelectorAll(".toggle")) {
    btn.addEventListener("click", () => {
      const panel = document.getElementById(btn.getAttribute("aria-controls"));
      const open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      panel.hidden = open;
    });
  }

  // The address is stored reversed and split, so it never appears whole in the page source.
  for (const a of document.querySelectorAll(".email-link")) {
    const reverse = (x) => [...x].reverse().join("");
    a.href = `mailto:${reverse(a.dataset.u)}@${reverse(a.dataset.d)}`;
  }

  setUpTicker(document.querySelector(".ticker"));
  setUpThemeToggle(document.querySelector(".theme-toggle"));
  setUpNav(document.querySelector(".topbar-nav"));
});

// Shows one news item at a time and moves on when the bar fills (its duration is --tick in
// style.css). The arrows step back and forth and restart the bar; they never pause it.
// It pauses with the Pause button, while a mouse is over the news text, or while a keyboard
// user is inside the ticker. Taps on a phone never pause it. With reduced motion it never
// advances on its own.
function setUpTicker(ticker) {
  if (!ticker) return;
  const items = [...ticker.querySelectorAll(".ticker-item")];
  const list = ticker.querySelector(".ticker-items");
  const bar = ticker.querySelector(".ticker-bar > span");
  const pause = ticker.querySelector(".ticker-pause");
  const prev = ticker.querySelector(".ticker-prev");
  const next = ticker.querySelector(".ticker-next");
  const index = ticker.querySelector(".ticker-index");
  if (items.length < 2 || !bar || !pause || !prev || !next) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let current = 0;
  let userPaused = false;
  let hovered = false;
  let focused = false;

  const restartBar = () => {
    bar.style.animation = "none";
    void bar.offsetWidth;
    bar.style.animation = "";
  };
  // step = +1 (next: the old item leaves upwards / to the left) or -1 (previous).
  const go = (step) => {
    const from = items[current];
    current = (current + step + items.length) % items.length;
    const to = items[current];
    // Park the incoming item on the side it enters from, without animating that jump.
    to.classList.add("is-instant");
    to.dataset.side = step > 0 ? "after" : "before";
    void to.offsetWidth;
    to.classList.remove("is-instant");
    from.dataset.side = step > 0 ? "before" : "after";
    from.classList.remove("is-active");
    to.classList.add("is-active");
    if (index) index.textContent = String(current + 1);
    restartBar();
  };
  const sync = () => {
    ticker.classList.toggle("is-paused", userPaused || hovered || focused);
    pause.classList.toggle("is-off", userPaused);
    pause.setAttribute("aria-label", userPaused ? "Resume news" : "Pause news");
    pause.title = userPaused ? "Resume" : "Pause";
  };

  bar.addEventListener("animationend", () => go(1));
  prev.addEventListener("click", () => go(-1));
  next.addEventListener("click", () => go(1));
  pause.addEventListener("click", () => { userPaused = !userPaused; sync(); });
  // Only a real mouse pauses on hover: a tap on a phone also "enters", but never leaves.
  list.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") { hovered = true; sync(); } });
  list.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hovered = false; sync(); } });
  // Keyboard focus pauses; a mouse click on a button does not (it is not :focus-visible).
  ticker.addEventListener("focusin", (e) => { focused = e.target.matches(":focus-visible"); sync(); });
  ticker.addEventListener("focusout", (e) => {
    if (!ticker.contains(e.relatedTarget)) { focused = false; sync(); }
  });

  if (reduced) pause.hidden = true;
  ticker.classList.add("is-ready");
  restartBar();
  sync();
}

// Light/dark switch. The choice is remembered in this browser; until the visitor
// picks one, the site follows the system setting.
function setUpThemeToggle(btn) {
  if (!btn) return;
  const root = document.documentElement;
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
  const current = () => root.dataset.theme || (systemDark.matches ? "dark" : "light");
  const label = () => {
    const next = current() === "dark" ? "light" : "dark";
    btn.setAttribute("aria-label", `Switch to ${next} theme`);
  };
  btn.addEventListener("click", () => {
    const next = current() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) { /* private mode: still switches */ }
    label();
    tintBrowser();
  });
  // Phone browsers colour their own bars from <meta name="theme-color">; keep it on the chosen theme.
  const tintBrowser = () => {
    if (!root.dataset.theme) return;   // no choice made: the two media-specific tags already apply
    const bg = getComputedStyle(root).getPropertyValue("--bg").trim();
    for (const m of document.querySelectorAll('meta[name="theme-color"]')) m.content = bg;
  };
  systemDark.addEventListener("change", label);
  label();
  tintBrowser();
}

// Underline the top-bar link of the section currently in view.
function setUpNav(nav) {
  if (!nav || !("IntersectionObserver" in window)) return;
  const links = new Map();
  for (const a of nav.querySelectorAll("a")) {
    const id = a.hash.slice(1);
    if (id && a.pathname === location.pathname && document.getElementById(id)) links.set(id, a);
  }
  const visible = new Set();
  const spy = new IntersectionObserver((entries) => {
    for (const e of entries) e.isIntersecting ? visible.add(e.target.id) : visible.delete(e.target.id);
    const current = [...links.keys()].find((id) => visible.has(id));
    for (const [id, a] of links) {
      if (id === current) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    }
  }, { rootMargin: "-20% 0px -70% 0px" });
  for (const id of links.keys()) spy.observe(document.getElementById(id));
}
