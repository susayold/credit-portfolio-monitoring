(function () {
  "use strict";

  const STORAGE_KEY = "financial-risk-portfolio-language";
  const TRANSLATABLE_ATTRIBUTES = ["aria-label", "title", "placeholder", "alt"];
  const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "CODE", "PRE", "NOSCRIPT"]);
  const translations = window.PORTFOLIO_TRANSLATIONS_VI || {};
  const textSources = new WeakMap();
  const attributeSources = new WeakMap();
  let currentLanguage = readPreference();
  let observer = null;

  function readPreference() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "vi" ? "vi" : "en";
    } catch (error) {
      return "en";
    }
  }

  function normalise(value) {
    return String(value || "").trim().replace(/\s+/g, " ");
  }

  function preserveOuterWhitespace(original, replacement) {
    const leading = original.match(/^\s*/)[0];
    const trailing = original.match(/\s*$/)[0];
    return leading + replacement + trailing;
  }

  function translationFor(value) {
    return translations[normalise(value)] || null;
  }

  function shouldSkip(node) {
    const parent = node.parentElement;
    return !parent || SKIP_TAGS.has(parent.tagName) || Boolean(parent.closest("[data-i18n-ui], [data-i18n-ignore]"));
  }

  function applyTextNode(node, language) {
    if (shouldSkip(node) || !normalise(node.nodeValue)) {
      return;
    }

    if (!textSources.has(node)) {
      textSources.set(node, node.nodeValue);
    }

    const source = textSources.get(node);
    const translated = translationFor(source);
    node.nodeValue = language === "vi" && translated
      ? preserveOuterWhitespace(source, translated)
      : source;
  }

  function sourceAttributesFor(element) {
    if (!attributeSources.has(element)) {
      attributeSources.set(element, {});
    }
    return attributeSources.get(element);
  }

  function applyAttributes(element, language) {
    if (element.closest("[data-i18n-ui], [data-i18n-ignore]")) {
      return;
    }

    const sources = sourceAttributesFor(element);
    TRANSLATABLE_ATTRIBUTES.forEach(function (attribute) {
      if (!element.hasAttribute(attribute)) {
        return;
      }
      if (!(attribute in sources)) {
        sources[attribute] = element.getAttribute(attribute);
      }
      const source = sources[attribute];
      const translated = translationFor(source);
      element.setAttribute(attribute, language === "vi" && translated ? translated : source);
    });

    if (element.tagName === "META" && element.getAttribute("name") === "description") {
      if (!("content" in sources)) {
        sources.content = element.getAttribute("content");
      }
      const translated = translationFor(sources.content);
      element.setAttribute("content", language === "vi" && translated ? translated : sources.content);
    }
  }

  function applyTree(root, language) {
    if (root.nodeType === Node.TEXT_NODE) {
      applyTextNode(root, language);
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) {
      return;
    }

    if (root.nodeType === Node.ELEMENT_NODE) {
      applyAttributes(root, language);
    }

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    while (node) {
      if (node.nodeType === Node.TEXT_NODE) {
        applyTextNode(node, language);
      } else {
        applyAttributes(node, language);
      }
      node = walker.nextNode();
    }
  }

  function updateControls() {
    document.querySelectorAll("[data-language-option]").forEach(function (button) {
      const isActive = button.dataset.languageOption === currentLanguage;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  function observe() {
    if (!observer) {
      observer = new MutationObserver(function (records) {
        observer.disconnect();
        records.forEach(function (record) {
          if (record.type === "characterData") {
            textSources.delete(record.target);
            applyTextNode(record.target, currentLanguage);
            return;
          }
          if (record.type === "attributes") {
            const sources = sourceAttributesFor(record.target);
            sources[record.attributeName] = record.target.getAttribute(record.attributeName);
            applyAttributes(record.target, currentLanguage);
            return;
          }
          record.addedNodes.forEach(function (node) {
            applyTree(node, currentLanguage);
          });
        });
        observe();
      });
    }
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: TRANSLATABLE_ATTRIBUTES,
      childList: true,
      characterData: true,
      subtree: true
    });
  }

  function setLanguage(language, persist) {
    currentLanguage = language === "vi" ? "vi" : "en";
    if (observer) {
      observer.disconnect();
    }
    applyTree(document, currentLanguage);
    document.documentElement.lang = currentLanguage;
    updateControls();
    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, currentLanguage);
      } catch (error) {
        // The site remains fully functional when browser storage is unavailable.
      }
    }
    observe();
    window.dispatchEvent(new CustomEvent("portfolio:languagechange", { detail: { language: currentLanguage } }));
  }

  function injectStyles() {
    const style = document.createElement("style");
    style.setAttribute("data-i18n-ui", "");
    style.textContent = `
      .language-switch{display:inline-grid;grid-template-columns:repeat(2,34px);height:32px;padding:2px;border:1px solid #b8c3bf;background:#fff;border-radius:4px;box-shadow:0 2px 8px rgba(16,47,56,.06);flex:0 0 auto}
      .language-switch button{display:grid;place-items:center;border:0;border-radius:2px;background:transparent;color:#63747a;font:700 11px/1 Segoe UI,Arial,sans-serif;letter-spacing:0;cursor:pointer}
      .language-switch button:hover,.language-switch button:focus-visible{color:#172a31;outline:2px solid rgba(13,119,112,.24);outline-offset:-1px}
      .language-switch button.active{background:#172a31;color:#fff}
      .site-header>.site-nav{margin-left:auto;order:2}
      .site-header>.menu-button{order:3}
      .site-header>.language-switch{order:4;margin-left:10px}
      .toolbar>.language-switch{height:34px;margin-right:2px}
      @media(max-width:1000px){.site-header>.site-nav{margin-left:0}.site-header>.language-switch{margin-left:6px}}
      @media(max-width:760px){.topbar>div:first-child{min-width:0}.topbar h1{overflow-wrap:anywhere}.toolbar{flex-wrap:wrap;justify-content:flex-end}}
      @media(max-width:480px){.language-switch{grid-template-columns:repeat(2,30px)}.site-header>.language-switch{margin-left:auto}.site-header>.menu-button{margin-left:6px}.brand-copy strong{font-size:.82rem}.toolbar>.language-switch{grid-column:1/-1}}
      @media print{.language-switch{display:none!important}}
    `;
    document.head.appendChild(style);
  }

  function createControl() {
    const control = document.createElement("div");
    control.className = "language-switch";
    control.setAttribute("data-i18n-ui", "");
    control.setAttribute("role", "group");
    control.setAttribute("aria-label", "Language selection");
    control.innerHTML = `
      <button type="button" data-language-option="en" aria-label="Use English">EN</button>
      <button type="button" data-language-option="vi" aria-label="Dùng tiếng Việt">VI</button>
    `;
    control.addEventListener("click", function (event) {
      const button = event.target.closest("[data-language-option]");
      if (button) {
        setLanguage(button.dataset.languageOption, true);
      }
    });
    return control;
  }

  function mountControl() {
    const host = document.querySelector(".site-header") || document.querySelector(".toolbar");
    if (!host || host.querySelector(".language-switch")) {
      return;
    }
    const control = createControl();
    if (host.classList.contains("toolbar")) {
      host.insertBefore(control, host.firstChild);
    } else {
      host.appendChild(control);
    }
  }

  injectStyles();
  mountControl();
  setLanguage(currentLanguage, false);

  window.PORTFOLIO_I18N = Object.freeze({
    getLanguage: function () { return currentLanguage; },
    setLanguage: function (language) { setLanguage(language, true); },
    translationCount: Object.keys(translations).length
  });
})();
