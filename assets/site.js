(function () {
  "use strict";

  const body = document.body;
  const menuButton = document.querySelector("[data-menu-button]");
  const nav = document.querySelector("[data-site-nav]");

  if (menuButton && nav) {
    menuButton.addEventListener("click", function () {
      const isOpen = nav.classList.toggle("open");
      body.classList.toggle("menu-open", isOpen);
      menuButton.setAttribute("aria-expanded", String(isOpen));
      menuButton.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.classList.remove("open");
        body.classList.remove("menu-open");
        menuButton.setAttribute("aria-expanded", "false");
      }
    });
  }

  const progress = document.querySelector("[data-scroll-progress]");
  if (progress) {
    const updateProgress = function () {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? (window.scrollY / max) * 100 : 0;
      progress.style.width = Math.min(100, Math.max(0, pct)) + "%";
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
  }

  const filterButtons = Array.from(document.querySelectorAll("[data-project-filter]"));
  const projectCards = Array.from(document.querySelectorAll("[data-project-track]"));
  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const filter = button.dataset.projectFilter;
      filterButtons.forEach(function (item) {
        item.classList.toggle("active", item === button);
        item.setAttribute("aria-pressed", String(item === button));
      });
      projectCards.forEach(function (card) {
        const tracks = (card.dataset.projectTrack || "").split(" ");
        card.hidden = filter !== "all" && !tracks.includes(filter);
      });
    });
  });

  const year = document.querySelector("[data-current-year]");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  const revealItems = Array.from(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    revealItems.forEach(function (item) { observer.observe(item); });
  } else {
    revealItems.forEach(function (item) { item.classList.add("visible"); });
  }

  const dialog = document.querySelector("[data-image-dialog]");
  const dialogImage = dialog ? dialog.querySelector("img") : null;
  const dialogClose = dialog ? dialog.querySelector("[data-dialog-close]") : null;
  document.addEventListener("click", function (event) {
    const button = event.target.closest("[data-expand-image]");
    if (button && dialog && dialogImage) {
      dialogImage.src = button.dataset.expandImage;
      dialogImage.alt = button.dataset.imageAlt || "Expanded analytical chart";
      dialog.showModal();
    }
  });
  if (dialogClose && dialog) {
    dialogClose.addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) { dialog.close(); }
    });
  }
})();
