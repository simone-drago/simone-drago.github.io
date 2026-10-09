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

// Shows one news item at a time and moves on when the active step's bar fills
// (its duration is --tick in style.css). Hovering or focusing the ticker pauses it,
// and so does the Pause button. With reduced motion it never advances on its own.
function setUpTicker(ticker) {
  if (!ticker) return;
  const items = [...ticker.querySelectorAll(".ticker-item")];
  const steps = [...ticker.querySelectorAll(".ticker-step")];
  const pause = ticker.querySelector(".ticker-pause");
  if (items.length < 2 || !pause) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let current = 0;
  let userPaused = false;
  let hovered = false;
  let focused = false;

  const show = (n) => {
    current = (n + items.length) % items.length;
    items.forEach((el, k) => el.classList.toggle("is-active", k === current));
    steps.forEach((el, k) => {
      el.classList.toggle("is-active", k === current);
      el.classList.toggle("is-done", k < current);
      el.setAttribute("aria-current", String(k === current));
      // Restart the fill animation of the active step.
      const bar = el.firstElementChild;
      bar.style.animation = "none";
      void bar.offsetWidth;
      bar.style.animation = "";
    });
  };
  const sync = () => {
    ticker.classList.toggle("is-paused", userPaused || hovered || focused);
    pause.textContent = userPaused ? "Play" : "Pause";
    pause.setAttribute("aria-pressed", String(userPaused));
  };

  steps.forEach((el, k) => {
    el.addEventListener("click", () => show(k));
    el.firstElementChild.addEventListener("animationend", () => show(current + 1));
  });
  pause.addEventListener("click", () => { userPaused = !userPaused; sync(); });
  ticker.addEventListener("mouseenter", () => { hovered = true; sync(); });
  ticker.addEventListener("mouseleave", () => { hovered = false; sync(); });
  // Pause while a keyboard user is inside the ticker. A mouse click also moves focus
  // there, but must not pause it: rotation resumes as soon as the pointer leaves.
  ticker.addEventListener("focusin", (e) => { focused = e.target.matches(":focus-visible"); sync(); });
  ticker.addEventListener("focusout", (e) => {
    if (!ticker.contains(e.relatedTarget)) { focused = false; sync(); }
  });

  if (reduced) pause.hidden = true;
  ticker.classList.add("is-ready");
  show(0);
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
  });
  systemDark.addEventListener("change", label);
  label();
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
