(function () {
  "use strict";
  const STORAGE_KEY = "ldv_lang";
  const DEFAULT_LANG = "en";
  const SUPPORTED = ["en", "id"];

  // Every later task appends its page's keys here (both en and id).
  const DICT = {
    en: {
      "nav.new_analysis": "New Analysis",
      "nav.dashboard": "Dashboard",
      "nav.citation_library": "Citation Library",
      "nav.secure_logout": "Secure Logout",
      "nav.sign_in": "Sign In",
      "brand.name": "Sydeco CRA",
    },
    id: {
      "nav.new_analysis": "Analisis Baru",
      "nav.dashboard": "Dasbor",
      "nav.citation_library": "Pustaka Sitasi",
      "nav.secure_logout": "Keluar Aman",
      "nav.sign_in": "Masuk",
      "brand.name": "Sydeco CRA",
    },
  };

  function getLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return SUPPORTED.indexOf(stored) !== -1 ? stored : DEFAULT_LANG;
  }

  function t(key) {
    return (DICT[getLang()] && DICT[getLang()][key]) || DICT[DEFAULT_LANG][key] || key;
  }

  function applyLang() {
    const lang = getLang();
    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const value = DICT[lang][el.dataset.i18n];
      if (value) el.textContent = value;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      const value = DICT[lang][el.dataset.i18nPlaceholder];
      if (value) el.setAttribute("placeholder", value);
    });

    document.querySelectorAll("[data-lang-toggle]").forEach(function (el) {
      el.textContent = lang === "en" ? "ID" : "EN";
    });

    if (window.Alpine && typeof window.Alpine.store === "function") {
      window.Alpine.store("lang", lang);
    }
  }

  function setLang(lang) {
    localStorage.setItem(STORAGE_KEY, SUPPORTED.indexOf(lang) !== -1 ? lang : DEFAULT_LANG);
    applyLang();
  }

  function toggleLang() {
    setLang(getLang() === "en" ? "id" : "en");
  }

  // Browser-only wiring — skipped when this file is `require()`-d from Node
  // (e.g. by i18n.selfcheck.js), since `document`/`window` don't exist there.
  if (typeof document !== "undefined") {
    document.addEventListener("alpine:init", function () {
      window.Alpine.store("lang", getLang());
    });
    document.addEventListener("DOMContentLoaded", applyLang);
  }
  if (typeof window !== "undefined") {
    window.i18n = { getLang, setLang, toggleLang, t, applyLang, DICT };
  }
  // Node-side export so i18n.selfcheck.js can `require()` this file directly
  // instead of evaluating it as a string (avoids new Function()/eval entirely).
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { getLang, setLang, toggleLang, t, applyLang, DICT };
  }
})();
